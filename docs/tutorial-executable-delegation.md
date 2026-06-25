# Tutorial: Executable Delegation

This tutorial runs the smallest executable subagent loop in ClankerOS:

1. register a local project;
2. create a goal, plan, sprint contract, and planned tasks;
3. create a read-only scout delegation;
4. configure a fake local shell adapter;
5. generate and inspect a deterministic context pack;
6. understand project-aware repo scouting context;
7. run the delegation;
8. inspect result, evidence, review, inbox, and dashboard;
9. prepare a bounded future coding plan from the implementation handoff;
10. request and approve bounded worktree execution;
11. run the approved local command in an isolated worktree;
12. optionally propose memory from the completed result.

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
context_pack = payload.get("context_pack", {})
pack = {}
if context_pack.get("available"):
    pack = json.loads(Path(context_pack["json_path"]).read_text(encoding="utf-8"))
top_files = [item["path"] for item in pack.get("ranked_files", [])[:3]]
if not top_files:
    top_files = ["agent_os/cli.py", "agent_os/delegation_runner.py"]
(evidence_dir / "fake-scout-seen.txt").write_text(
    payload["delegation"]["id"],
    encoding="utf-8",
)
expected_schema = payload["delegation"]["expected_output_schema"]
structured_output = {
    "options": [
        {
            "title": "Inspect executable delegation surfaces",
            "files": top_files,
            "reason": "These files were selected from the context pack."
        }
    ]
}
if expected_schema == "file_relevance_report":
    structured_output = {
        "files": top_files,
        "findings": ["Context pack ranked these files as likely relevant."],
        "relevant_files": top_files
    }
print(json.dumps({
    "result_summary": "Identified a safe implementation starting point.",
    "structured_output": structured_output
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

## 5. Generate A Context Pack

Generate deterministic repo context before running the adapter:

```bash
python3 -m agent_os.cli context-pack <delegation_id> \
  --max-files 12 \
  --max-snippets 8 \
  --max-total-chars 12000
```

Expected output includes:

```text
context_pack: <delegation_id>
context_pack_id: context_pack_...
context_pack_json: .clanker/delegations/<delegation_id>/context/context_pack.json
context_pack_md: .clanker/delegations/<delegation_id>/context/context_pack.md
next_recommended_action: run_delegation
```

Open the Markdown file when you want the human-readable version. The JSON file
is what fake or real local scouts should read through
`payload["context_pack"]["json_path"]`.

`run-delegation` also auto-generates the context pack if it is missing and the
parent task has a registered project. Manual generation is useful when you want
to inspect or tune the scout context before any adapter runs.

The context pack is distinct from `project-context`: `project-context` writes a
durable operator summary for a registered repo; `context-pack` writes a
delegation-specific, capped, ranked file/search/snippet packet for one scout
run.

## 6. Project-Aware Repo Scouting

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
  },
  "context_pack": {
    "available": true,
    "json_path": "/absolute/path/to/evidence/context_pack.json",
    "markdown_path": "/absolute/path/to/evidence/context_pack.md",
    "top_ranked_files": ["agent_os/cli.py", "agent_os/delegation_runner.py"]
  }
}
```

The evidence packet includes `project.json`, `repo_files.json`,
`context_pack.json`, `context_pack.md`, and `context_pack_metadata.json` when
this context is available. With `--working-directory project_root`, the adapter
can read repository files by relative path while still receiving absolute
paths for `input.json`, `prompt.md`, the context pack, and the evidence
directory.

## 7. Run The Delegation

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
context_pack.json
context_pack.md
context_pack_metadata.json
implementation_handoff.json
implementation_handoff.md
memory_proposal.json
```

`memory_proposal.json` exists only when `--record-memory` is used.
`project.json` and `repo_files.json` exist only when the delegation belongs to
a registered project. `validation.json` records `context_pack_used`,
`returned_files_in_inventory`, `returned_files_missing`, and
`top_ranked_files_referenced` when a context pack was attached. Missing
returned files are warnings in validation metadata, not hard failures.
`implementation_handoff.json` and `.md` are compact downstream implementation
inputs. They include the context-pack path, ranked/test hint summaries,
returned-file validation, scout returned files, and non-claims without copying
large snippets into the handoff.

## 8. Inspect The Result And Evidence

```bash
python3 -m agent_os.cli delegation-result <delegation_id>
python3 -m agent_os.cli implementation-handoff <delegation_id>
python3 -m agent_os.cli coder-prep <delegation_id>
python3 -m agent_os.cli coder-worktree-plan <delegation_id>
python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "Approve bounded worktree execution"
python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "Approved bounded execution"
python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli inbox
python3 -m agent_os.cli dashboard
```

`delegation-result` prints runtime metadata when the result came from
`run-delegation`, including the run id, adapter type, evidence packet, and
context-pack and implementation-handoff paths. `implementation-handoff` parses
the handoff JSON and prints readability, schema/kind, returned-file
validation, top ranked files, test hints, scout relevant files, and whether
large snippets were embedded. `coder-prep` consumes the handoff Markdown and
writes a bounded future coding packet without editing source files or
dispatching work. `coder-worktree-plan` consumes `coder_prep.md` and writes an
approval-gated future worktree/run packet without creating a worktree or
requesting approval. `coder-worktree-approval` requests the explicit operator
gate for the current plan hash without creating a worktree. `approve-coder-worktree`
records the local decision without running commands. `run-coder-worktree` is
the first command in this flow that can create a worktree and run the
operator-provided safe local command. `review <run_id>` includes
`## Scout Context Pack`, `## Implementation Handoff`, `## Coder Prep`,
`## Coder Worktree Plan`, `## Coder Worktree Approval`, and
`## Coder Worktree Run` sections when those packets exist, then adds
`## Coder Worktree Commit` and `## Coder Publication` after those gates run.
The dashboard includes
`### Subagent / Scout Work`, `### Implementation Handoffs`,
`### Coder Prep Packets`, `### Coder Worktree Plans`,
`### Coder Worktree Approvals`, `### Approved Coder Worktree Runs`,
`### Coder Commit Requests`, `### Coder Local Commits`,
`### Coder Publication Requests`, and `### Coder Publication Handoffs`
sections with compact scout, handoff, prep, approval, worktree-run, commit,
and publication health.

## 9. Prepare A Bounded Coder Plan

Use this command after the handoff looks readable and relevant:

```bash
python3 -m agent_os.cli coder-prep <delegation_id>
```

Expected output includes:

```text
coder_prep: coder_prep
delegation_id: <delegation_id>
source_handoff_md: .clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.md
source_handoff_markdown_consumed: true
artifact: .clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_prep.json
markdown: .clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_prep.md
run_plan: operator_review_required
task_rows_created: 0
runs_created: 0
routing_decisions_created: 0
worktrees_created: 0
effects_created: 0
approval_requests_created: 0
source_edits: 0
commands_rerun: 0
network_actions_taken: 0
external_mutations_taken: 0
```

The JSON packet records allowed files, candidate test files, acceptance
criteria, risks, forbidden actions, and suggested verification commands for a
future explicit coding run. It is idempotent for the same handoff hash; a
second run prints `coder_prep: already_recorded coder_prep`.

Proof boundary: this is a prep artifact only. It does not create task rows,
runs, routing decisions, worktrees, effects, approvals, source edits, command
reruns, commits, pushes, deploys, provider calls, network actions, or external
mutations.

## 10. Prepare An Approval-Gated Worktree Plan

Use this command only after the coder-prep packet looks bounded enough for a
future implementation run:

```bash
python3 -m agent_os.cli coder-worktree-plan <delegation_id>
```

Expected output includes:

```text
coder_worktree_plan: coder_worktree_plan
delegation_id: <delegation_id>
source_coder_prep_md: .clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_prep.md
source_coder_prep_markdown_consumed: true
artifact: .clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_plan.json
markdown: .clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_plan.md
approval_gate: operator_approval_required
dispatch_ready: false
worktree_created: 0
task_rows_created: 0
runs_created: 0
routing_decisions_created: 0
worktrees_created: 0
effects_created: 0
approval_requests_created: 0
source_edits: 0
commands_rerun: 0
provider_calls_taken_by_clankeros: 0
network_actions_taken: 0
external_mutations_taken: 0
```

The JSON packet records the source prep hash, allowed files, candidate tests,
approval gate, proposed branch/path, and a future explicit
`run-goal --isolation worktree` command shape. It is idempotent for the same
`coder_prep.md` hash; a second run prints
`coder_worktree_plan: already_recorded coder_worktree_plan`.

Proof boundary: this is a plan artifact only. It does not create task rows,
runs, routing decisions, worktrees, effects, approvals, source edits, command
reruns, commits, pushes, deploys, provider calls, network actions, or external
mutations.

## 11. Approve And Run A Bounded Coder Worktree

Request approval for the exact current `coder_worktree_plan.json` hash:

```bash
python3 -m agent_os.cli coder-worktree-approval <delegation_id> \
  --requested-by operator \
  --note "Approve bounded worktree execution"
```

Expected output includes:

```text
coder_worktree_approval: coder_worktree_approval_...
approval_id: coder_worktree_approval_...
status: pending_operator_approval
artifact: .clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_approval_request.json
worktrees_created: 0
commands_run: 0
source_edits: 0
commit_created: false
push_created: false
deploy_created: false
provider_calls_taken_by_clankeros: 0
network_actions_taken: 0
external_mutations_taken: 0
```

Approve that local request:

```bash
python3 -m agent_os.cli approve-coder-worktree <approval_id> \
  --decided-by operator \
  --note "Approved bounded execution"
```

Expected output includes:

```text
approved_coder_worktree: <approval_id>
status: approved
artifact: .clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_approval_decision.json
worktrees_created: 0
commands_run: 0
source_edits: 0
commit_created: false
push_created: false
deploy_created: false
```

Run the approved bounded command:

```bash
python3 -m agent_os.cli run-coder-worktree <delegation_id> \
  --command "python3 scripts/local_change.py" \
  --verify
```

The command must be explicitly provided and pass conservative local-command
validation. Obvious network, deploy, push, publish, shell-destructive, and
desktop-control tokens are rejected before a worktree is created.

Run evidence is written under:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/
```

Required files include:

```text
run.json
command.txt
stdout.txt
stderr.txt
verification_command.txt
verification_stdout.txt
verification_stderr.txt
git_status.txt
diff.patch
changed_files.json
bounded_file_validation.json
approval.json
source_plan.json
summary.md
```

If changed files are outside the plan's `allowed_files`, the run is marked
`blocked` with `failure_class: bounded_file_violation`; ClankerOS does not
auto-revert. If verification fails, the run is marked `failed`. A successful
run still does not commit, push, deploy, call providers, or intentionally use
the network. The next action is to review the worktree evidence and use a
separate commit-approval path only if the existing diff is acceptable.

## 12. Request, Approve, And Create A Local Coder Worktree Commit

First write or refresh the review packet for the coder worktree run:

```bash
python3 -m agent_os.cli review <coder_worktree_run_id>
```

Then request a local commit for the completed coder worktree run:

```bash
python3 -m agent_os.cli coder-commit-request <coder_worktree_run_id> \
  --requested-by operator \
  --message "Implement bounded change from approved worktree run" \
  --note "Request local commit after review"
```

Expected output includes:

```text
coder_commit_request: coder_worktree_commit_approval_...
commit_request_id: coder_worktree_commit_approval_...
coder_worktree_run_id: run_...
status: pending_operator_approval
commit_created: false
push_created: false
pr_created: false
deploy_created: false
```

Approve the local commit request:

```bash
python3 -m agent_os.cli approve-coder-commit <commit_request_id> \
  --decided-by operator \
  --note "Approved local commit"
```

Create the local worktree commit only after approval:

```bash
python3 -m agent_os.cli commit-coder-worktree <coder_worktree_run_id> \
  --message "Implement bounded change from approved worktree run"
```

The commit command re-checks the approved request hash, reviewed run hash,
branch/HEAD, changed files, outside files, commit message, and verifier state
before staging only allowed files and creating one local git commit inside the
isolated coder worktree branch. It is idempotent after the commit. Stale
evidence, changed files outside the approved set, failed verification, or a
mismatched message blocks without committing.

The commit evidence lives in:

```text
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/commit.json
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/committed_diff.patch
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/committed_files.json
```

Request the next publication handoff boundary after the isolated local commit:

```bash
python3 -m agent_os.cli coder-publication-request <coder_worktree_run_id> \
  --requested-by operator \
  --remote origin \
  --target-branch main \
  --note "Request publication handoff"

python3 -m agent_os.cli approve-coder-publication <publication_request_id> \
  --decided-by operator \
  --note "Approved publication handoff preparation"

python3 -m agent_os.cli coder-publication-handoff <coder_worktree_run_id>
```

The publication request and approval do not push or create PRs. The handoff
writes local JSON/Markdown plus a PR body draft with suggested `git push` and
draft `gh pr create` commands, but does not execute those commands, run
`git fetch`, contact GitHub, deploy, call providers, or mutate external
systems. Manual operator execution is required for any future push or PR.

## 13. Propose Memory From The Result

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

`run-coder-worktree` also fails or blocks safely for missing plans, unreadable
prep/handoff artifacts, changed plan hashes after approval, missing or pending
approvals, unsafe command strings, worktree creation failures, command
failures, verification failures, bounded-file violations, and evidence write
failures. These records are local incidents/recommendations; ClankerOS does
not auto-retry, auto-commit, auto-push, deploy, or clean the worktree.

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
