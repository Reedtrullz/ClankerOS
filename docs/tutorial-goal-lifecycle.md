# Tutorial: Goal, Plan, Contract, And Tasks

Use this tutorial when you want to turn an idea into durable ClankerOS planning
state for a registered local git project. This workflow is for operator
visibility before execution: it creates a goal, a versioned plan, a draft
contract, and planned task records.

It does not execute the tasks. It does not commit, push, deploy, approve
effects, start subagents, call model providers, or run a background scheduler.

## 1. Initialize Local State

```bash
python3 -m agent_os.cli init
```

This creates or migrates `.agent/state.db`. It is safe to run before the rest
of the commands.

## 2. Register The Target Project

Register the repository before creating lifecycle state:

```bash
python3 -m agent_os.cli register-project my-repo \
  --path /absolute/path/to/repo \
  --test-command "python3 -m pytest -q"
```

Registration validates that the path resolves to a git repository and writes a
human-readable project note under `projects/my-repo/project.md`.

## 3. Write A Project Context Packet

```bash
python3 -m agent_os.cli project-context my-repo
```

Read `projects/my-repo/context.md` before starting a goal. It records the local
git root, branch and remote readbacks, default verifier, allowed write roots,
and explicit non-claims.

## 4. Create A Goal Lifecycle

```bash
python3 -m agent_os.cli goal \
  "Add a small tested improvement to the CLI help output" \
  --project my-repo
```

Expected output shape:

```text
goal_created: goal_...
project: my-repo
plan_id: plan_...
plan_version: 1
tasks: 3
goal_artifact: .clanker/projects/my-repo/goals/goal_.../GOAL.md
plan_artifact: .clanker/projects/my-repo/goals/goal_.../PLAN.md
tasks_artifact: .clanker/projects/my-repo/goals/goal_.../TASKS.md
```

The command creates:

- a goal row in SQLite;
- a versioned plan row and plan-step rows;
- planned task rows linked to the plan steps;
- markdown mirrors under `.clanker/projects/my-repo/goals/<goal_id>/`.

The created tasks are `status=planned`. They are not claimable execution work
until a later runner or operator deliberately advances them.

## 5. Inspect The Current Plan

```bash
python3 -m agent_os.cli plan goal_...
```

Use this to read back the latest active plan version and its steps. The plan
command may materialize planning state for a registered-project goal that does
not already have a plan, but it does not run the verifier or execute any task.

## 6. Create Or Read The Draft Contract

```bash
python3 -m agent_os.cli contract goal_...
```

The contract captures scope, non-goals, acceptance criteria, verification
intent, and risk notes for the latest plan. Treat it as the operator agreement
for what the next execution loop may do.

The contract remains local planning evidence. It does not approve work,
activate capabilities, create commits, push to GitHub, deploy, or contact CI.

## 7. List Planned Tasks

```bash
python3 -m agent_os.cli tasks goal_...
```

Use the task list to choose the next operator action. A typical planned set is:

- clarify scope and acceptance criteria;
- implement the smallest safe change;
- verify evidence and decide the next action.

Those records are intentionally visible before they are executable. If the
scope is wrong, fix the plan or replan before advancing any task.

## 8. Update A Task State

```bash
python3 -m agent_os.cli update-task task_... \
  --status blocked \
  --blocked-reason "Contract needs operator review before implementation."
```

`update-task` records the task status and mirrors the update to the linked plan
step when one exists. It is useful for operator steering, blockers, and manual
review notes.

For a planning-only loop, prefer `planned`, `blocked`, or another explicit
review state that matches reality. Do not treat a status update as proof that
work happened.

## 9. Replan When Scope Changes

```bash
python3 -m agent_os.cli replan goal_... \
  --reason "Scope changed after contract review."
```

Replanning creates a new plan version and leaves older versions available for
audit. It also writes refreshed `PLAN.md`, `PLAN-v<N>.md`, and `TASKS.md`
artifacts.

Replanning is still planning. It does not supersede evidence, execute tasks,
or mutate the target project by itself.

## 10. Refresh Visibility

```bash
python3 -m agent_os.cli dashboard
```

The dashboard is the operator cockpit for the current local state. After this
workflow, use it to confirm the goal plan version, planned tasks, approval
posture, and non-claim counters.

## Proof Boundaries

- `register-project` proves only that the local path can be resolved as a git
  repository and recorded.
- `project-context` is a local readback packet, not live GitHub, CI, or deploy
  proof.
- `goal`, `plan`, and `contract` create local planning records and markdown
  artifacts.
- `tasks` lists local task records; it does not claim or execute them.
- `update-task` changes local state; it does not prove implementation.
- `replan` creates a new local plan version; it does not run work.
- `dashboard` summarizes local state; it is not a hosted dashboard.

## Suggested Operator Loop

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli register-project my-repo --path /absolute/path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli project-context my-repo
python3 -m agent_os.cli goal "Make one small verified improvement" --project my-repo
python3 -m agent_os.cli plan goal_...
python3 -m agent_os.cli contract goal_...
python3 -m agent_os.cli tasks goal_...
python3 -m agent_os.cli dashboard
```

Stop there unless the plan, contract, and task list are clear enough for a
separate execution path.
