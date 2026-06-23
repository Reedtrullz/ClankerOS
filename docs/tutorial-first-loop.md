# Tutorial: Run The First Local Loop

This tutorial walks through the smallest useful ClankerOS loop:

1. initialize local state;
2. create a goal;
3. let the local worker execute verifiable tasks;
4. inspect the evidence;
5. record a safe profile routing decision;
6. optionally record a read-only delegation contract;
7. optionally ingest a structured delegation result;
8. regenerate the dashboard.

ClankerOS is local-first. These commands write SQLite rows and markdown
reports in this checkout. They do not start remote workers, deploy services,
operate browser or desktop adapters, or mutate external systems.

## Prerequisites

- Python 3.10 or newer.
- A shell in the repository root.
- No network access is required for the local loop.

Optional but recommended:

- `git` for reviewing local changes.
- `gh` only when publishing to GitHub.

## 1. Initialize The Harness

```bash
python3 -m agent_os.cli init
```

This creates the local `.agent/` SQLite state and writes the runtime capability
matrix. The `.agent/` directory is intentionally ignored by Git.

## 2. Run A Goal

```bash
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
```

Expected behavior:

- a goal row is written;
- deterministic tasks are created;
- the local worker claims executable local work;
- verification evidence is written to `runs/`;
- learnings and summaries are reflected in project files.

## 3. Check The Queue And Handoff State

```bash
python3 -m agent_os.cli projects
python3 -m agent_os.cli approvals
python3 -m agent_os.cli queue-health
python3 -m agent_os.cli handoff-review
```

Useful readings:

- `projects: N` shows how many local git repositories are registered for
  ClankerOS-targeted work.
- `pending_approvals: 0` means no current local approval rows are waiting.
- `hotspots: 0` means no repeated blocked or failed task pattern was found.
- `status: clear` means the current handoff review found no stale handoff issue.

## 4. Record A Profile Routing Decision

```bash
python3 -m agent_os.cli profiles
python3 -m agent_os.cli route --category repo_search --project bootstrap
```

The `profiles` command creates safe local defaults for planner, coder, scout,
tester, and evaluator profiles. The `route` command records a selection
decision in SQLite. Category-only routing is useful before a concrete task
exists. It does not dispatch a subagent, call a model provider, or change the
worker claim rules.

## 5. Record A Read-Only Delegation Contract

If you have a concrete task id, create a scoped delegation contract:

```bash
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli delegations <goal_id>
python3 -m agent_os.cli delegation-result <delegation_id>
```

This stores a pending `subagent_delegations` row and a JSON artifact under
`.clanker/delegations/`. It does not start a subagent, call a model provider,
write files, approve work, commit, or mutate external systems.

## 6. Record A Delegation Result

If read-only specialist output exists, attach it to the delegation:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Relevant files identified." \
  --output-json '{"files":["agent_os/cli.py"]}'
```

This validates the payload against the expected schema family, marks the
delegation completed, and writes a result artifact under `.clanker/delegations/`.
It does not start a subagent, call a model provider, take a network action, or
mutate external systems.

## 7. Regenerate The Operator Dashboard

```bash
python3 -m agent_os.cli dashboard
```

Open `docs/dashboard.md` to inspect queue health, proof checklists, approval
boundaries, profile routing decisions, subagent delegation contracts,
playbooks, eval results, and the latest generated reports.

## 8. Run Verification

```bash
python3 -m pytest -q
python3 -m agent_os.cli eval
python3 -m agent_os.cli playbooks
```

The pytest suite is the broad local regression gate. The eval command proves
the first milestone scenario. Playbooks are promoted from repeated successful
eval runs and remain guidance only; they are not automatic executors.

## What This Tutorial Does Not Do

- It does not deploy a hosted dashboard.
- It does not start remote workers.
- It does not schedule autonomous external work.
- It does not operate browser or desktop adapters.
- It does not run GitHub Actions or deploy infrastructure.
- It does not dispatch subagents or call a model provider when recording a
  profile routing decision.
- It does not start subagents or call model providers when recording a
  delegation contract.
- It does not start subagents or call model providers when recording a
  delegation result.
- It does not enforce budgets, promote trust, retry work, or track real spend.
- It does not apply the future `operator_approval_requests` schema migration.

Those capabilities stay behind explicit report-only proof and approval
boundaries until they are separately designed, approved, implemented, and
verified.
