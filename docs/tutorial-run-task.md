# Tutorial: Run A Planned Task

Use this tutorial when a registered-project goal already has a plan, a sprint
contract, and planned task rows, and you want ClankerOS to execute one planned
task through a local profile-backed verifier.

This is the bridge from planning state to executable evidence. It records a
routing decision, creates a run, executes the task verification command with a
safe local shell adapter, writes an evidence packet, updates the linked plan
step, and refreshes operator visibility.

It does not edit files by itself, commit, push, deploy, start subagents, call
model providers, promote trust, schedule retries, or mutate external systems.

## 1. Start From A Registered Project

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli register-project my-repo \
  --path /absolute/path/to/repo \
  --test-command "python3 -m pytest -q"
```

Registration gives ClankerOS the local git root, default test command, and
write boundary for the target project.

## 2. Create Planning State

```bash
python3 -m agent_os.cli goal \
  "Make one small verified improvement" \
  --project my-repo
python3 -m agent_os.cli contract goal_...
python3 -m agent_os.cli tasks goal_...
```

The `goal` command creates `planned_step` tasks. The `contract` command creates
the sprint agreement for the current plan. `run-task` refuses to dispatch a
planned task if the linked plan has no sprint contract.

## 3. Pick A Planned Task

Choose a `status=planned` task from:

```bash
python3 -m agent_os.cli tasks goal_...
```

Typical generated plans contain one planning task, one implementation task, and
one verification task. Pick the task whose verification command is appropriate
for the profile you will use.

## 4. Choose A Profile

Use `tester` when the task verification command exactly matches the registered
project default test command:

```bash
python3 -m agent_os.cli run-task task_... --profile tester
```

Use `coder` for a safe local shell verification command that is not the default
test command:

```bash
python3 -m agent_os.cli run-task task_... --profile coder
```

Profiles come from the local profile config and SQLite rows created by:

```bash
python3 -m agent_os.cli profiles
python3 -m agent_os.cli profile-show tester
```

The default `planner`, `scout`, and `evaluator` profiles do not have shell
execution permission and are rejected for `run-task`.

## 5. Read The Run Output

Successful output has this shape:

```text
task_run: run_...
run_id: run_...
task_id: task_...
goal_id: goal_...
project_id: my-repo
profile: tester
status: completed
verification_passed: true
routing_decision: routing_decision_...
evidence_packet: .clanker/projects/my-repo/goals/goal_.../runs/run_.../evidence
summary: .clanker/projects/my-repo/goals/goal_.../runs/run_.../evidence/summary.md
commands_rerun: 1
network_actions_taken: 0
external_mutations_taken: 0
```

If the verifier fails, the task and linked plan step are marked failed, a local
incident is opened, and the run still keeps stdout, stderr, command metadata,
verification JSON, and `recommendations.jsonl` for review.

## 6. Inspect Evidence

Read the evidence packet:

```text
.clanker/projects/my-repo/goals/<goal_id>/runs/<run_id>/evidence/
```

Important files:

- `summary.md` - human-readable task run summary.
- `verification.json` - command, profile, adapter, return code, stdout, stderr,
  and pass/fail state.
- `routing_decisions.jsonl` - the profile/model selection row.
- `commands.jsonl` - local command adapter metadata.
- `tasks.json` - task, plan-step, and contract snapshot.
- `git_status.txt`, `diff.patch`, and `changed_files.json` - added by
  `evidence <run_id>` as local git snapshots for the registered project repo.
  They do not fetch, pull, commit, push, or rerun the verifier.
- `recommendations.jsonl` - present when failed verification created recovery
  guidance.
- `stdout.txt` and `stderr.txt` - raw verifier output.

## 7. Review Recovery Recommendations

For failed task runs or blocked planned tasks:

```bash
python3 -m agent_os.cli task-recommendations --goal goal_...
```

This writes `docs/task-recommendations.md` and records idempotent
`task_recommendations` rows. Failed runs get `failed_run_task_recovery`
guidance such as `review <run_id>`, `replan <goal_id> --reason "..."`, and a
manual `run-task <task_id> --profile <profile>` command for after the operator
has explicitly reset or replanned the task. Blocked planned tasks get
`blocked_planned_task_replan` guidance.

The command is guidance only. It does not retry, reset, replan, dispatch,
approve, commit, push, deploy, call providers, schedule work, or mutate
external systems.

## 8. Review And Refresh The Cockpit

```bash
python3 -m agent_os.cli review run_...
python3 -m agent_os.cli dashboard
```

`review` writes `runs/<run_id>/review.md` from local run state. The dashboard
now includes `### Task Runs` and `### Task Recommendations` sections so the
operator can see recent planned task executions and recovery guidance alongside
active runs, plans, approvals, incidents, routing, delegations, memory, and
skill state.

## 9. Rerun Policy

`run-task` dispatches only tasks that are still `status=planned`. A completed
or failed task is not silently rerun:

```text
run_task_failed: task task_... status completed cannot be dispatched
```

Use `replan`, an explicit task status change, or a new goal when the operator
wants a new execution record.

## Proof Boundaries

- `run-task` executes the task verification command locally with `shell=True`
  inside the registered project root.
- Unsafe command substrings such as `rm -rf`, `git push`, `gh pr create`,
  `curl`, `wget`, `ssh`, and `scp` are blocked.
- `tester` can only run the project default test command.
- `coder` can run safe local shell verification commands.
- The evidence packet proves local shell execution only.
- No model provider, subagent runtime, browser automation, desktop automation,
  remote worker, hosted dashboard, CI job, deploy, commit, push, PR, automatic
  retry, budget enforcement, trust promotion, or real spend tracking is
  claimed by this command.
