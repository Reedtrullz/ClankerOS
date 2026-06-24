# ClankerOS

ClankerOS is a local-first agent OS harness for durable AI coding work. It
turns goals into task graphs, records evidence, keeps approval boundaries
explicit, and shows operators what is actually proven before any autonomous
capability is allowed to act.

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
```

The project is intentionally conservative. It prefers local state, reportable
evidence, idempotent effects, and human approval over chat-only claims or
hidden autonomy.

## What It Does

- Tracks goals, tasks, evidence, approvals, effects, incidents, playbooks, and
  iteration packets in SQLite plus human-readable Markdown.
- Registers local git repositories and exposes `projects`, `project-status`,
  and `project-context` commands so an operator can inspect target repos before
  starting work.
- Creates durable project-scoped `goal`, `plan`, `contract`, and `tasks`
  records before execution, with versioned plan artifacts and explicit
  non-claims.
- Dispatches planned goal tasks through local profiles with `run-task`,
  records routing decisions, runs safe verifier commands, and writes evidence
  packets under `.clanker/projects/<project>/goals/<goal_id>/runs/`.
- Records retry/replan recommendations for failed planned-task runs and
  blocked planned tasks without automatically retrying, resetting, or
  dispatching work.
- Generates an operator dashboard and next-iteration packet from current local
  state.
- Runs worktree-isolated coding goals, captures diffs and verification output,
  and gates local commits behind explicit approval.
- Produces GitHub handoff packets after committed local effects, including
  exact push and draft-PR commands without taking network action itself.
- Supports safe profile routing, read-only delegation contracts, deterministic
  context packs, executable local delegation through configured shell adapters,
  project-aware repo scouting, structured delegation-result ingestion, proposed
  memory, and proposed skills.
- Models capability activation as blocked proof work until evidence, approval,
  idempotency, and rollback boundaries exist, including local downstream proof
  tasks and read-only evaluator delegation packets.

## Start Here

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli projects
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
python3 -m pytest -q
```

Then read:

- [Getting Started](docs/getting-started.md)
- [Suggested Use](docs/suggested-use.md)
- [Operator Recipes](docs/operator-recipes.md)
- [Concepts](docs/concepts.md)
- [Architecture](docs/architecture.md)
- [Command Reference](docs/reference-commands.md)
- [Documentation Index](docs/docs-index.md)
- [First Loop Tutorial](docs/tutorial-first-loop.md)
- [First Target Repository Tutorial](docs/tutorial-first-target-repo.md)
- [Project Registry Tutorial](docs/tutorial-project-registry.md)
- [Goal Planning Lifecycle Tutorial](docs/tutorial-goal-lifecycle.md)
- [Run A Planned Task Tutorial](docs/tutorial-run-task.md)
- [Operator Daily Loop Tutorial](docs/tutorial-operator-daily-loop.md)
- [Approval-Gated Coding Tutorial](docs/tutorial-approval-gated-coding.md)
- [Executable Delegation Tutorial](docs/tutorial-executable-delegation.md)
- [Public Snapshot Tutorial](docs/tutorial-public-snapshot.md)

The capability activation ladder has many intentionally verbose proof
tutorials. Use the [Documentation Index](docs/docs-index.md#capability-follow-up-tutorials)
when you need a specific blocked-activation rung.

Register and inspect a target repository before asking ClankerOS to touch it:

```bash
python3 -m agent_os.cli register-project my-repo --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli projects
python3 -m agent_os.cli project-status my-repo
python3 -m agent_os.cli project-context my-repo
```

Plan a registered project goal before executing work:

```bash
python3 -m agent_os.cli goal "Make the smallest verified improvement" --project my-repo
python3 -m agent_os.cli plan <goal_id>
python3 -m agent_os.cli contract <goal_id>
python3 -m agent_os.cli tasks <goal_id>
```

This writes versioned local artifacts under
`.clanker/projects/<project>/goals/<goal_id>/`. It does not execute tasks,
commit, push, deploy, or call model providers.

Execute one planned task only after the plan and sprint contract are clear:

```bash
python3 -m agent_os.cli run-task <task_id> --profile tester
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli evidence <run_id>
python3 -m agent_os.cli task-recommendations --goal <goal_id>
python3 -m agent_os.cli dashboard
```

`run-task` is profile-gated. `tester` can only run the registered project
default test command; `coder` can run safe local verifier commands. The command
creates a local run and evidence packet, but it does not commit, push, deploy,
start a model provider, or start a subagent.

`evidence <run_id>` adds the replayable operator packet under
`.clanker/projects/<project>/goals/<goal_id>/runs/<run_id>/evidence/` and
prints the `packet_dir`. If the run already has command-proof files from
`run-task`, ClankerOS preserves them and writes aggregate review sidecars.
The packet also includes `git_status.txt`, `diff.patch`, and
`changed_files.json` for the selected evidence target: the registered project
repo when the run belongs to one, otherwise the ClankerOS system root. These
files are local snapshots only; export does not fetch, pull, commit, push, or
mutate the repo.

If a planned task verifier fails, ClankerOS opens a local incident and records
an open `failed_run_task_recovery` recommendation with review, replan, and
manual rerun guidance. If a planned task is blocked, `task-recommendations`
records `blocked_planned_task_replan` guidance. These records are local
operator guidance only; they do not retry or change task status by themselves.

Run a read-only delegation through a configured local shell adapter when you
want a replaceable specialist executor:

```bash
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli context-pack <delegation_id> --max-files 12 --max-snippets 8
python3 -m agent_os.cli profile-adapter scout --command "python3 .clanker/adapters/fake_scout.py" --input-mode json_file --output-mode json --timeout-seconds 120
python3 -m agent_os.cli run-delegation <delegation_id>
python3 -m agent_os.cli delegation-result <delegation_id>
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli dashboard
```

`run-delegation` is provider-agnostic. ClankerOS owns the durable state,
prompt/context bundle, evidence packet, schema validation, and incident
handling; the configured adapter is only a local executor. There are no
built-in OpenAI, Anthropic, Codex, OpenCode, Hermes, Aider, or MCP provider
integrations yet. Subagent profiles remain read-only by default and cannot be
used by ClankerOS to commit, push, approve, deploy, or mutate external systems.
When the parent task belongs to a registered project, `context-pack` writes
ranked files, grep hits, snippets, test hints, entrypoint hints, config hints,
and non-claims under `.clanker/delegations/<delegation_id>/context/`.
`run-delegation` auto-generates that pack if it is missing, copies it into the
run evidence packet, and passes compact `context_pack` metadata to the adapter.
Add `--working-directory project_root` when configuring the adapter if the
local executor should run from the target repository instead of the ClankerOS
system root.
For the full walkthrough, see
[Executable Delegation](docs/tutorial-executable-delegation.md).

## Command Surface

| Need | Command |
| --- | --- |
| Initialize local state | `python3 -m agent_os.cli init` |
| See current operator state | `python3 -m agent_os.cli dashboard` |
| Select the next narrow slice | `python3 -m agent_os.cli iterate` |
| Register a local git repo | `python3 -m agent_os.cli register-project <name> --path <path>` |
| Create planning state | `goal`, `plan`, `contract`, `tasks` |
| Run one planned task | `python3 -m agent_os.cli run-task <task_id> --profile tester` |
| Configure delegation adapter | `python3 -m agent_os.cli profile-adapter scout --command "python3 .clanker/adapters/fake_scout.py"` |
| Configure project-root scout adapter | `python3 -m agent_os.cli profile-adapter scout --command "python3 /path/to/scout.py" --working-directory project_root` |
| Generate scout context | `python3 -m agent_os.cli context-pack <delegation_id>` |
| Run read-only delegation | `python3 -m agent_os.cli run-delegation <delegation_id>` |
| Review evidence | `review`, `evidence`, `replay-summary` |
| Inspect approvals | `python3 -m agent_os.cli approvals` |
| Prepare GitHub handoff | `python3 -m agent_os.cli github-handoff <effect_id>` |

For common workflows, use [Operator Recipes](docs/operator-recipes.md). For a
complete command map, use [Command Reference](docs/reference-commands.md).

## Executable Delegation

The current delegation loop can execute a pending read-only delegation through
a locally configured shell adapter. The adapter receives a scoped
prompt/context bundle, returns a JSON result envelope, and ClankerOS validates
the output against the delegation schema before marking the delegation
completed.

For registered-project tasks, `input.json` includes a `project` object with
the registered root path, default test command, and allowed write roots; a
`repo_scouting` object with a capped git file inventory; and a `context_pack`
object pointing at the evidence-local `context_pack.json` and
`context_pack.md`.

`context-pack` is the deterministic scout preflight. It extracts technical
terms from the goal, task, delegation prompt, and schema; ranks repository
files with explainable scores; records capped grep hits and snippets; skips
ignored and secret-like paths; and writes:

```text
.clanker/delegations/<delegation_id>/context/context_pack.json
.clanker/delegations/<delegation_id>/context/context_pack.md
```

During `run-delegation`, those files are copied into:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/context_pack.json
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/context_pack.md
```

Adapters run from the ClankerOS root by default; configure
`--working-directory project_root` to let a scout read repo files with relative
paths.

Malformed JSON, schema-invalid output, non-zero exits, timeouts, and unsafe
adapter commands fail safely with local incidents and evidence packets under:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/
```

This is the first executable delegation primitive, not a general provider
integration layer. Adapter commands are configured locally per profile, and
ClankerOS records that network/provider actions taken by the adapter are
unknown unless the adapter itself proves otherwise.

## Current Shape

ClankerOS is a Python CLI with a local SQLite control plane, generated Markdown
reports, JSON artifacts, pytest coverage, eval/playbook checks, and bootstrap
project memory. The first milestone is the closed loop:

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
```

The current control plane includes executable local slices where the verifier
is explicit (`run-goal`, `run-task`, `run-delegation`) and report-only ladders
where a capability is still blocked. Accepted blocked decisions can create
local proposed effects, applied effects can create more proof tasks, and every
activation step preserves `activation_allowed=false`,
`capability_enabled=false`, `approval_requests_created=0`,
`activation_actions_taken=0`, and `external_mutations_taken=0` unless a future
approved capability boundary changes that contract.

For the detailed state, use:

- [Operator Dashboard](docs/dashboard.md)
- [Next Iteration Packet](docs/next-iteration.md)
- [Operating Summary](docs/OPERATING_SUMMARY.md)
- [Generated Evidence Reports](docs/docs-index.md#generated-evidence-reports)
- [Status Log](status.md)
- [Bootstrap Handoff](projects/bootstrap/handoff.md)

## Key Files

- `agent_os/cli.py` - command entrypoint.
- `agent_os/storage.py` - SQLite schema and persistence layer.
- `agent_os/dashboard.py` - generated operator dashboard.
- `agent_os/iteration.py` - next-iteration packet generator.
- `docs/OPERATING_SUMMARY.md` - current architecture and proof state.
- `docs/dashboard.md` - generated operator cockpit.
- `docs/next-iteration.md` - generated next work packet.
- `tasks.md` - human-readable momentum queue.
- `status.md` - chronological implementation evidence.
- `projects/bootstrap/` - bootstrap project continuity notes.

## Public Snapshot Checklist

Before pushing a public snapshot:

```bash
git status --short --branch
git diff --check
python3 -m pytest -q
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Pushing is not deployment. Local tests are not CI proof. GitHub metadata
readback is not runtime proof. See
[Tutorial: Public Snapshot](docs/tutorial-public-snapshot.md) for the full
recommended flow.

## Non-Claims

This repository does not yet claim hosted dashboard availability, remote worker
execution, autonomous scheduling, browser/desktop adapter readiness, live
CI/deploy proof, built-in model provider integrations, budget enforcement,
trust promotion, automatic retries, automatic memory activation, automatic
skill activation, or real cost tracking. Shell adapters are local configured
executors; ClankerOS records `provider_calls_taken_by_clankeros=0` and
`external_mutations_taken=0`, but adapter network/provider behavior is unknown
unless the adapter writes evidence proving otherwise. Those surfaces remain
blocked until their evidence and approval contracts are satisfied.

## GitHub About

Suggested repository description:

```text
Local-first agent OS harness for durable AI coding: task graphs, executable delegation, verification evidence, and approval gates.
```

Suggested topics:

```text
agent-operating-system, agent-os, ai-agents, agentic-ai, coding-agents, agent-orchestration, subagent-delegation, executable-delegation, local-first, human-in-the-loop, approval-workflow, verification, evidence, task-graph, operator-dashboard, worktrees, sqlite, python, cli-tool, developer-tools
```
