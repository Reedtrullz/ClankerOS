# Tutorial: Record Delegation Results

This tutorial walks through the local profile-routing and delegation loop:

1. create or choose a concrete task;
2. record a safe profile routing decision;
3. create a read-only delegation contract;
4. ingest structured operator-supplied output;
5. inspect the completed evidence;
6. propose useful memory from the completed result.

The loop is local-first. It writes SQLite rows and JSON artifacts. It does not
start a subagent, call a model provider, approve work, commit, push, deploy, or
mutate external systems.

## Prerequisites

- Python 3.10 or newer.
- A shell in the ClankerOS repository root.
- An existing task id for the work you want to delegate.

If you need a task id, run a normal local goal first:

```bash
python3 -m agent_os.cli run-goal "Create a small local work packet" --project bootstrap
python3 -m agent_os.cli dashboard
```

Then inspect `docs/dashboard.md`, `runs/`, or the SQLite-backed CLI outputs to
choose the task id.

## 1. Initialize Profiles

```bash
python3 -m agent_os.cli profiles
python3 -m agent_os.cli profile-show scout
```

`profiles` materializes safe local defaults in SQLite and writes
`.clanker/profiles.yml` when no local profile config exists. The default
read-only specialist profiles include `scout`, `tester`, and `evaluator`.

## 2. Record A Routing Decision

For a concrete task:

```bash
python3 -m agent_os.cli route <task_id>
```

Or record a category/project decision before a task exists:

```bash
python3 -m agent_os.cli route --category repo_search --project bootstrap
```

Routing stores the selected profile, model label, category, reason, and cost
tier. It does not claim a task or call a model provider.

## 3. Create A Delegation Contract

```bash
python3 -m agent_os.cli delegate <task_id> \
  --profile scout \
  --title "Find relevant files"
```

The command writes:

- a `subagent_delegations` SQLite row;
- a JSON contract under `.clanker/delegations/`;
- a scoped prompt and input context;
- allowed tools, forbidden actions, budget hints, and an expected output schema.

Inspect it:

```bash
python3 -m agent_os.cli delegations <goal_id>
python3 -m agent_os.cli delegation-result <delegation_id>
```

The delegation starts as `pending`. That is intentional: this command records a
contract only.

## 4. Ingest A Structured Result

After a human operator or separately supervised read-only helper has produced a
result, attach it to the delegation:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Relevant files identified." \
  --output-json '{"files":["agent_os/cli.py","tests/test_first_milestone.py"]}' \
  --recorded-by operator
```

The command validates the JSON against the delegation's expected schema family.
Accepted keys must contain a non-empty list or object. Examples:

- `file_relevance_report` accepts non-empty `files`, `findings`, or `relevant_files`.
- `failing_test_summary` accepts non-empty `failures`, `failing_tests`, or `findings`.
- `dependency_map` accepts non-empty `dependencies` or `edges`.
- `risk_review` accepts non-empty `risks` or `findings`.
- `evidence_review` accepts non-empty `evidence` or `findings`.

If the payload does not match, ClankerOS rejects the result and leaves the
delegation pending.

## 5. Inspect Completed Evidence

```bash
python3 -m agent_os.cli delegation-result <delegation_id>
python3 -m agent_os.cli dashboard
```

Completed delegations point at:

```text
.clanker/delegations/<delegation_id>-result.json
```

That artifact includes the structured output, summary, recorder, completion
timestamp, and explicit non-claims:

- no subagent was started by ingestion;
- no model provider was called by ingestion;
- no network action was taken;
- no external mutation was performed.

Repeating the same result is idempotent and reports `already_recorded`. A
different result for a completed delegation is rejected so historical evidence
does not silently drift.

## Recommended Use

Use this loop when specialist work should inform the parent task but should not
yet be trusted as autonomous execution. Good examples:

- a file relevance report before coding;
- a failing test summary before debugging;
- a dependency map before refactoring;
- a risk review before approval;
- an evidence review before closing a work packet.

The parent task can then cite the completed delegation artifact as local
evidence while still preserving the difference between local recordkeeping and
actual external execution.

Capability activation follow-up work has one extra local ingestion step:
after completing a read-only evaluator delegation, run
`python3 -m agent_os.cli capability-activation-followup-results` to create the
capability follow-up result record. Completing the generic delegation does not
itself satisfy capability proof or enable activation.

## 6. Propose Memory From The Result

If the completed delegation result contains a small durable fact worth carrying
across sessions, propose it as memory:

```bash
python3 -m agent_os.cli memory propose-from-delegation <delegation_id> \
  --key relevant_cli_files \
  --created-by-profile scout
```

This writes a `memory_entries` row with `status=proposed` and a JSON artifact
under:

```text
.clanker/memory/<memory_id>.json
```

The proposal keeps the source delegation id, the source result artifact path,
the proposed key/value, confidence, and non-claims. It does not activate memory
silently.

Review proposals:

```bash
python3 -m agent_os.cli memory list --project bootstrap
```

Approve or archive explicitly:

```bash
python3 -m agent_os.cli memory approve <memory_id> --approved-by operator
python3 -m agent_os.cli memory archive <memory_id> --archived-by operator --reason "superseded"
```

Use manual proposals for known operator-supplied facts:

```bash
python3 -m agent_os.cli memory propose \
  --project bootstrap \
  --key test_command \
  --value "python3 -m pytest -q"
```

Memory approval changes local ClankerOS state only. It does not write to an
external memory service, call a model provider, or mutate other systems.
