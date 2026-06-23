# Getting Started With ClankerOS

ClankerOS is a local-first control plane for agentic coding work. Use it when
you want goals, tasks, evidence, approvals, and operator decisions to survive
outside a chat transcript.

The safest first use is not full autonomy. It is a visible loop:

```text
goal -> task graph -> local work -> verification -> evidence -> dashboard -> next action
```

## Install And Initialize

```bash
git clone https://github.com/Reedtrullz/ClankerOS.git
cd ClankerOS
python3 -m agent_os.cli init
python3 -m pytest -q
```

Expected local effects:

- `.agent/state.db` is created for runtime state.
- `docs/runtime-capability-matrix.md` is written.
- No hosted service, remote worker, model provider, CI job, or deploy is
  started by initialization.

## Run The First Loop

```bash
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Read these files after the commands finish:

- `docs/dashboard.md` for current visible state.
- `docs/next-iteration.md` for the next local work packet.
- `status.md` and `projects/bootstrap/status.md` for chronological evidence.

## Use It For A Coding Change

Register a local repository and run the work in an isolated worktree:

```bash
python3 -m agent_os.cli register-project my-repo \
  --path /path/to/repo \
  --test-command "python3 -m pytest -q"
python3 -m agent_os.cli projects
python3 -m agent_os.cli project-status my-repo
python3 -m agent_os.cli project-context my-repo

python3 -m agent_os.cli run-goal \
  "Make the smallest verified change" \
  --project my-repo \
  --isolation worktree \
  --command "<safe local command>"
```

Then inspect the generated run evidence before approving anything:

```bash
python3 -m agent_os.cli approvals
python3 -m agent_os.cli dashboard
```

Only after reviewing the diff and tests:

```bash
python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "reviewed diff and tests"
python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator
```

`commit-approved` creates a local worktree commit only after a fresh evidence
recheck. It does not push or open a pull request.

`project-context` writes `projects/<name>/context.md` as a durable handoff
packet for the registered repository. It reads local registry and git metadata
only; it does not run tests, create a worktree, approve effects, commit, push,
deploy, or call a model provider.

## Plan Before Execution

For operator-led work, start with a durable goal plan before asking ClankerOS
to run or delegate anything:

```bash
python3 -m agent_os.cli goal "Make the smallest verified improvement" --project my-repo
python3 -m agent_os.cli plan <goal_id>
python3 -m agent_os.cli contract <goal_id>
python3 -m agent_os.cli tasks <goal_id>
```

Expected local effects:

- the goal is stored in SQLite with project, title, prompt, status, and
  priority fields;
- the first plan version is written to
  `.clanker/projects/my-repo/goals/<goal_id>/PLAN-v1.md`;
- `PLAN.md`, `GOAL.md`, and `TASKS.md` mirror the latest operator-readable
  state;
- three `planned_step` task rows are created with `status=planned`.

The planning lifecycle does not execute tasks. Use `update-task` to record an
operator decision on a planned task and `replan` when scope changes:

```bash
python3 -m agent_os.cli update-task <task_id> --status blocked --blocked-reason "waiting on scope"
python3 -m agent_os.cli replan <goal_id> --reason "operator narrowed the target"
```

## Best Operating Pattern

1. Keep each request narrow and evidence-shaped.
2. Register the project and inspect `project-context` before planning work.
3. Create a `goal`, inspect the `plan`, and read the `contract` before
   execution.
4. Ask for one local capability boundary at a time.
5. Prefer report-only proof before action-taking features.
6. Treat dashboard and generated reports as evidence, not as guarantees.
7. Commit only coherent, verified increments.
8. Push only after local tests and metadata readback are clean.

## Good First Prompts

```text
Run the first local loop, regenerate the dashboard, and summarize what is proven and not proven.
```

```text
Register this repo, run a worktree-isolated coding task, capture the diff and tests, then ask before committing.
```

```text
Create a durable goal, plan, sprint contract, and planned task list for this registered project without executing anything.
```

```text
Review the current dashboard and next-iteration packet, then implement the next local proof step with tests.
```

## What To Read Next

- `docs/concepts.md` for vocabulary.
- `docs/architecture.md` for the local control-plane shape.
- `docs/suggested-use.md` for prompt patterns and operating rules.
- `docs/tutorial-goal-lifecycle.md` for planning a registered project goal
  before execution.
- `docs/tutorial-approval-gated-coding.md` for the worktree approval loop.
