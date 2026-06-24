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
  project-aware repo scouting, first-class implementation handoffs, safe
  coder-prep packets, approval-gated coder worktree plans, explicit coder
  worktree approvals, bounded worktree execution with evidence, structured
  delegation-result ingestion, proposed memory, and proposed skills.
- Keeps the old capability proof ladder as advanced blocked-proof/reference
  machinery instead of the default operator path.

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

The primary operator surface is the implementation-handoff workflow: scout a
repo, inspect the generated handoff, prepare a bounded coder plan, propose an
approval-gated worktree plan, request explicit approval, run a bounded local
command in an isolated worktree, then review evidence before any separate
commit approval.

```bash
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli context-pack <delegation_id>
python3 -m agent_os.cli run-delegation <delegation_id>
python3 -m agent_os.cli implementation-handoff <delegation_id>
python3 -m agent_os.cli coder-prep <delegation_id>
python3 -m agent_os.cli coder-worktree-plan <delegation_id>
python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "Approve bounded worktree execution"
python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "Approved bounded execution"
python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli dashboard
```

The historical capability proof ladder remains callable and documented for
advanced blocked-proof work, but it is not the default README or CLI-help path.
Use the [Command Reference](docs/reference-commands.md#capability-activation-proof-tasks)
or [Documentation Index](docs/docs-index.md#capability-follow-up-tutorials)
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
python3 -m agent_os.cli implementation-handoff <delegation_id>
python3 -m agent_os.cli coder-prep <delegation_id>
python3 -m agent_os.cli coder-worktree-plan <delegation_id>
python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "Approve bounded worktree execution"
python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "Approved bounded execution"
python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify
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
Successful executable delegations also write compact implementation handoff
artifacts in the run evidence packet. These handoffs point at the context pack,
returned files, validation status, and relevant test hints without embedding
the large snippets:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.json
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.md
```

Use `implementation-handoff <delegation_id>` to parse that handoff directly.
It prints readability, schema/kind, context-pack validation, scout returned
files, top ranked files, test hints, and whether snippets were embedded.
Use `coder-prep <delegation_id>` when an operator wants to turn the handoff
into a bounded future coding plan before editing anything. It consumes
`implementation_handoff.md`, writes `coder_prep.json` and `coder_prep.md`
under the delegation run, and prints zero-effect counters for task rows, runs,
routing decisions, worktrees, approvals, source edits, command reruns, network
actions, and external mutations.
Use `coder-worktree-plan <delegation_id>` after reviewing the prep packet. It
consumes `coder_prep.md`, writes `coder_worktree_plan.json` and
`coder_worktree_plan.md` beside it, proposes a bounded future worktree/run
shape, and keeps `dispatch_ready=false` with no worktree, approval request, run,
task, effect, command rerun, source edit, network action, provider call, commit,
push, deploy, or external mutation.
Use `coder-worktree-approval <delegation_id>` to request the explicit operator
gate for that exact plan hash. It writes `coder_worktree_approval_request.json`
and `.md` beside the plan and still creates no worktree, runs no command, and
edits no source.
Use `approve-coder-worktree <approval_id>` to mark that local approval request
approved. It writes `coder_worktree_approval_decision.json` and `.md`, but it
still does not create a worktree or run commands.
Only `run-coder-worktree <delegation_id> --command "<safe local cmd>" --verify`
can create the isolated worktree. It requires an approved matching plan hash,
runs the operator-provided safe local command in that worktree, captures stdout,
stderr, verification output, git status, diff, changed files, and bounded-file
validation under `.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/`.
It blocks if changed files are outside `allowed_files`. It does not commit,
push, deploy, call providers, or intentionally use the network.
After a successful run, use `review <coder_worktree_run_id>` before requesting
local commit promotion. `coder-commit-request <coder_worktree_run_id>` requires
completed bounded worktree evidence, a clean verification result, current
changes still inside `allowed_files`, a readable worktree, and an explicit
commit message. It writes `coder_commit/coder_commit_request.json` and `.md`
without staging or committing. `approve-coder-commit <commit_request_id>`
records the operator decision in `coder_commit/coder_commit_decision.json` and
`.md` without staging or committing. Only
`commit-coder-worktree <coder_worktree_run_id>` may stage the reviewed allowed
files and create one local commit in the isolated worktree branch. It re-checks
the source run hash, branch/HEAD, current changed files, outside files,
message, and verifier state, then writes `coder_commit/commit.json`,
`pre_commit_status.txt`, `post_commit_status.txt`, `committed_diff.patch`, and
`committed_files.json`. The resulting `effect_id` can be passed to
`github-handoff <effect_id>` to create local push and draft-PR instructions.
None of these steps push, deploy, call providers, or mutate external systems.
Add `--working-directory project_root` when configuring the adapter if the
local executor should run from the target repository instead of the ClankerOS
system root.
For the full walkthrough, see
[Executable Delegation](docs/tutorial-executable-delegation.md).

## Primary Operator Surface

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
| Inspect implementation handoff | `python3 -m agent_os.cli implementation-handoff <delegation_id>` |
| Prepare bounded coder plan | `python3 -m agent_os.cli coder-prep <delegation_id>` |
| Prepare approval-gated worktree plan | `python3 -m agent_os.cli coder-worktree-plan <delegation_id>` |
| Request coder worktree approval | `python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "..."` |
| Approve coder worktree execution | `python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "..."` |
| Run approved bounded worktree command | `python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify` |
| Request local commit from reviewed worktree | `python3 -m agent_os.cli coder-commit-request <coder_worktree_run_id> --requested-by operator --message "..." --note "..."` |
| Approve local commit request | `python3 -m agent_os.cli approve-coder-commit <commit_request_id> --decided-by operator --note "..."` |
| Create local worktree commit | `python3 -m agent_os.cli commit-coder-worktree <coder_worktree_run_id> --message "..."` |
| Review evidence | `review`, `evidence`, `replay-summary` |
| Inspect approvals | `python3 -m agent_os.cli approvals` |
| Prepare GitHub handoff | `python3 -m agent_os.cli github-handoff <effect_id>` |

For common workflows, use [Operator Recipes](docs/operator-recipes.md). For
legacy proof-ladder and advanced report-only commands, use
[Command Reference](docs/reference-commands.md).

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
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.json
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.md
```

`delegation-result`, `implementation-handoff <delegation_id>`,
`coder-prep <delegation_id>`, `coder-worktree-plan <delegation_id>`,
`coder-worktree-approval <delegation_id>`, `approve-coder-worktree <approval_id>`,
`run-coder-worktree <delegation_id>`, `review <run_id>`, `inbox`, and `dashboard`
surface the context-pack path, returned-file inventory validation, missing
returned files, and implementation handoff health so a later implementation
pass can start from paths and metadata instead of pasted snippets. `review`
writes `## Implementation Handoff`, `## Coder Prep`, and
`## Coder Worktree Plan`, `## Coder Worktree Approval`, and
`## Coder Worktree Run` sections, and the dashboard writes
`### Implementation Handoffs`, `### Coder Prep Packets`, and
`### Coder Worktree Plans`, `### Coder Worktree Approvals`, and
`### Approved Coder Worktree Runs`.

`coder-prep` is artifact-only and idempotent for the same handoff hash. It
does not create task rows, dispatch runs, rerun commands, edit source files,
create worktrees, request approvals, commit, push, deploy, call providers, or
mutate external systems.
`coder-worktree-plan` is also artifact-only and idempotent for the same
`coder_prep.md` hash. It proposes a branch/path and future explicit
`run-goal --isolation worktree` command, but it does not create the worktree,
run the command, request approval, edit files, commit, push, deploy, call
providers, or mutate external systems.
`coder-worktree-approval` is idempotent for the same plan hash unless
`--force-new` is used. `approve-coder-worktree` tolerates already-approved
requests and prints `already_approved`. `run-coder-worktree` refuses to run
without an approved matching plan hash and does not rerun a completed
approval/plan pair unless `--rerun` is provided.

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

The current control plane's primary operator path is implementation handoff:
`run-delegation` writes context and handoff evidence, `implementation-handoff`
reads it back, `coder-prep` writes a bounded future coding plan, and
`coder-worktree-plan` writes an approval-gated future worktree plan.
`coder-worktree-approval`, `approve-coder-worktree`, and `run-coder-worktree`
then provide the first explicit bounded worktree execution gate with local
evidence but no automatic commit, push, deploy, provider call, or network
action. A reviewed successful coder worktree run can then move through the
separate local-only gate `coder-commit-request -> approve-coder-commit ->
commit-coder-worktree -> github-handoff`; commit approval remains separate
from execution approval, and GitHub handoff remains separate from push/PR.
Executable local slices still exist where the verifier is explicit (`run-goal`,
`run-task`, `run-delegation`, `run-coder-worktree`). The older report-only
proof ladders remain available as
advanced blocked-proof machinery, and every activation step still preserves
`activation_allowed=false`, `capability_enabled=false`,
`approval_requests_created=0`, `activation_actions_taken=0`, and
`external_mutations_taken=0` unless a future approved capability boundary
changes that contract.

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
