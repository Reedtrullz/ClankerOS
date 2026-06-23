# Tutorial: Create Downstream Tasks From Applied Result Effect Task Result Effects

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-apply`
has applied accepted downstream result effect task result decision effects as
local records. The task command turns those applied effects into pending task
graph work so the next proof-planning step can be routed and delegated.

## Prerequisites

Apply the downstream result effect task result decision effects first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-proposals.md
```

Confirm the application report exists:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-application.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Application`

## Create Pending Tasks

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-tasks
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_tasks: capability_activation_followup_result_task_result_effect_task_result_effect_tasks_recorded
applied_downstream_effects: 1
tasks_created: 1
existing_downstream_tasks: 0
capability_tasks_created: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-tasks.md
```

Rerunning the command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_tasks_already_recorded`
and create zero duplicate tasks.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-tasks.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Tasks`
- `docs/next-iteration.md` for the next queued routing/delegation slice

Each pending task records:

- current applied effect id
- current application id
- source decision id
- source downstream result id
- prior application, effect, delegation, task, contract, goal, and project ids
- capability and selected action
- blocked activation/capability flags
- zero approval, activation, and external mutation counts

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not allow activation.
- This does not mutate capability activation contracts.
- This does not mutate downstream result effect task result records.
- This does not mutate external systems.
- This does not route, schedule, retry, dispatch, run CI, or deploy.
