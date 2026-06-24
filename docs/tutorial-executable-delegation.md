# Tutorial: Executable Delegation

This tutorial runs the smallest executable subagent loop in ClankerOS:

1. register a local project;
2. create a goal, plan, sprint contract, and planned tasks;
3. create a read-only scout delegation;
4. configure a fake local shell adapter;
5. understand project-aware repo scouting context;
6. run the delegation;
7. inspect result, evidence, review, inbox, and dashboard;
8. optionally propose memory from the completed result.

The executor is a local shell adapter. ClankerOS owns the durable state,
prompt/context bundle, schema validation, evidence packet, incident handling,
and dashboard visibility. The adapter is replaceable.

## Prerequisites

- Python 3.10 or newer.
- A shell in the ClankerOS repository root.
- No model provider credentials are required.

## 1. Initialize And Register A Project

Use `bootstrap` for a local self-test walkthrough:

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli register-project bootstrap --path "$PWD" --test-command "python3 -m pytest -q"
python3 -m agent_os.cli project-context bootstrap
```

Registration records local repository metadata and a default verifier command.
It does not run tests, edit files, commit, push, deploy, or call providers.

## 2. Create Planning State

```bash
python3 -m agent_os.cli goal "Map the CLI files before changing delegation docs" --project bootstrap
python3 -m agent_os.cli plan <goal_id>
python3 -m agent_os.cli contract <goal_id>
python3 -m agent_os.cli tasks <goal_id>
```

Pick one planned task id from the `tasks` output. The commands above write
SQLite rows and artifacts under:

```text
.clanker/projects/bootstrap/goals/<goal_id>/
```

They do not execute task work.

## 3. Create A Delegation Contract

```bash
python3 -m agent_os.cli profiles
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Suggest relevant implementation files"
python3 -m agent_os.cli delegations <goal_id>
python3 -m agent_os.cli delegation-result <delegation_id>
```

The `delegate` command creates a pending `subagent_delegations` row and a JSON
contract under `.clanker/delegations/`. It records the scoped prompt, input
context, allowed tools, forbidden actions, budget hints, and expected output
schema. It does not start an executor by itself.

## 4. Configure A Fake Scout Adapter

Create a local fake adapter:

```bash
mkdir -p .clanker/adapters
python3 - <<'PY'
from pathlib import Path

Path(".clanker/adapters/fake_scout.py").write_text(
    """
import json
import sys
from pathlib import Path

input_path = Path(sys.argv[1])
payload = json.loads(input_path.read_text(encoding="utf-8"))
evidence_dir = Path(payload["evidence_dir"])
(evidence_dir / "fake-scout-seen.txt").write_text(
    payload["delegation"]["id"],
    encoding="utf-8",
)
print(json.dumps({
    "result_summary": "Identified a safe implementation starting point.",
    "structured_output": {
        "options": [
            {
                "title": "Inspect executable delegation surfaces",
                "files": [
                    "agent_os/cli.py",
                    "agent_os/delegation_runner.py",
                    "tests/test_first_milestone.py"
                ],
                "reason": "These files contain the command, runner, and regression tests."
            }
        ]
    }
}))
""".lstrip(),
    encoding="utf-8",
)
PY
```

Then attach it to the scout profile:

```bash
python3 -m agent_os.cli profile-adapter scout \
  --command "python3 .clanker/adapters/fake_scout.py" \
  --input-mode json_file \
  --output-mode json \
  --timeout-seconds 120
```

Adapters run from the ClankerOS system root by default. Keep that default when
the adapter script lives under `.clanker/adapters/` and only needs the input
bundle. For repo scouting against a registered project, use an absolute adapter
path and opt into the project root as the working directory:

```bash
python3 -m agent_os.cli profile-adapter scout \
  --command "python3 /absolute/path/to/project_scout.py" \
  --input-mode json_file \
  --output-mode json \
  --working-directory project_root \
  --timeout-seconds 120
```

Command placeholders are available when you need explicit paths:

- `{input_path}` - the JSON input bundle path;
- `{prompt_path}` - the delegation prompt path;
- `{evidence_dir}` - the evidence directory;
- `{system_root}` - the ClankerOS repository root;
- `{project_root}` - the registered target repository root, when available.

Supported input modes:

- `json_file`: appends the input bundle path to the adapter command.
- `prompt_file`: appends the prompt path to the adapter command.
- `stdin`: sends the delegation prompt on standard input.

Supported output modes:

- `json`: stdout must be a JSON object.
- `text`: stdout is treated as `result_summary` with an empty structured output.

For useful completed delegations, prefer `json` output. The expected JSON
envelope is:

```json
{
  "result_summary": "Identified a safe implementation starting point.",
  "structured_output": {
    "options": [
      {
        "title": "Inspect CLI and runner",
        "files": ["agent_os/cli.py", "agent_os/delegation_runner.py"],
        "reason": "These files own the executable delegation path."
      }
    ]
  }
}
```

The planned-task flow above usually produces `expected_output_schema` set to
`implementation_options`, so `structured_output.options` must be non-empty. For
delegations whose category maps to `file_relevance_report`, provide non-empty
`files`, `findings`, and `relevant_files` instead.

## 5. Project-Aware Repo Scouting

When the parent task belongs to a registered project, `run-delegation` writes
project context into the adapter input bundle:

```json
{
  "project": {
    "id": "bootstrap",
    "root_path": "/absolute/path/to/repo",
    "default_test_command": "python3 -m pytest -q",
    "allowed_write_roots": ["/absolute/path/to/repo"]
  },
  "repo_scouting": {
    "available": true,
    "root_path": "/absolute/path/to/repo",
    "files": ["README.md", "agent_os/cli.py"],
    "inventory_method": "git ls-files --cached --others --exclude-standard"
  }
}
```

The evidence packet includes `project.json` and `repo_files.json` when this
context is available. With `--working-directory project_root`, the adapter can
read repository files by relative path while still receiving absolute paths for
`input.json`, `prompt.md`, and the evidence directory.

## 6. Run The Delegation

```bash
python3 -m agent_os.cli run-delegation <delegation_id>
```

Expected operator output includes:

```text
run_delegation: <delegation_id>
run_id: <run_id>
adapter_type: shell
status: completed
result_artifact: ...
evidence_packet: .clanker/delegations/<delegation_id>/runs/<run_id>/evidence
next_recommended_action: review_delegation_result
```

The evidence packet includes:

```text
summary.md
delegation.json
profile.json
adapter.json
input.json
prompt.md
stdout.txt
stderr.txt
raw_output.txt
parsed_output.json
validation.json
result.json
memory_proposal.json
```

`memory_proposal.json` exists only when `--record-memory` is used.
`project.json` and `repo_files.json` exist only when the delegation belongs to
a registered project.

## 7. Inspect The Result And Evidence

```bash
python3 -m agent_os.cli delegation-result <delegation_id>
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli inbox
python3 -m agent_os.cli dashboard
```

`delegation-result` prints runtime metadata when the result came from
`run-delegation`, including the run id, adapter type, evidence packet, and
network/provider non-claims. The dashboard and inbox show recent delegation
state compactly.

## 8. Propose Memory From The Result

Run the delegation with memory proposal enabled:

```bash
python3 -m agent_os.cli run-delegation <delegation_id> \
  --record-memory \
  --memory-key delegation.file_mapping.cli_entrypoints
```

Or propose memory after a completed delegation:

```bash
python3 -m agent_os.cli memory propose-from-delegation <delegation_id> \
  --key delegation.file_mapping.cli_entrypoints \
  --created-by-profile scout
python3 -m agent_os.cli memory list --project bootstrap
```

Memory stays `status=proposed` until the operator explicitly approves it.

## Failure Behavior

`run-delegation` fails safely and opens a local incident for:

- missing adapter config;
- unsafe adapter commands such as `rm -rf`, `git push`, `gh pr create`, `curl`,
  `wget`, `ssh`, `scp`, `rsync`, or `sudo`;
- adapter timeout;
- non-zero adapter exit;
- malformed JSON;
- schema-invalid JSON;
- detectable forbidden action claims;
- result artifact write failure.

Failed evidence packets include `incident.json`, `validation.json`,
`stdout.txt`, `stderr.txt`, and `result.json`. ClankerOS does not retry
automatically.

## Non-Claims

This loop does not provide built-in OpenAI, Anthropic, Codex, OpenCode,
Hermes, Aider, local-model, MCP, browser, desktop, remote-worker, hosted UI,
scheduling, deploy, or GitHub push/PR integrations.

For a shell adapter run, ClankerOS records:

- `provider_calls_taken_by_clankeros: 0`;
- `external_mutations_taken: 0`;
- `network_actions_taken: unknown unless adapter evidence proves otherwise`.

The adapter command may call arbitrary local tools if the operator configures
it to do so. ClankerOS blocks obvious unsafe command strings and keeps
subagent profiles read-only by default, but it cannot prove an adapter's
network/provider behavior unless the adapter writes evidence.
