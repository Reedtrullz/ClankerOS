# Tutorial: Create Downstream Tasks From Applied Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Effects

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply`
has applied proposed local effects. This command materializes those applied
effects as pending high-risk proof tasks in the local task graph.

It does not approve, activate, dispatch, schedule, retry, deploy, or mutate
external systems.

## Prerequisites

Apply the proposed effects first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md
```

Confirm this report exists:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`

## Create Pending Downstream Tasks

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_recorded
applied_downstream_effects: 1
tasks_created: 1
existing_downstream_tasks: 0
capability_tasks_created: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md
```

Rerunning the same command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_already_recorded`
with `tasks_created: 0` and `existing_downstream_tasks: 1`.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Tasks`

The report preserves:

- the task batch id and source application id
- applied effect ids
- newly created downstream task ids
- existing downstream task ids for idempotent reruns
- explicit zero approval, activation, and external mutation counts

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not allow activation.
- This does not mutate capability activation contracts.
- This does not mutate downstream result effect task result effect task result
  effect task result effect task result effect task result records.
- This does not mutate external systems.
- This does not route, schedule, retry, dispatch, run CI, deploy, promote
  trust, or mark the active goal complete.
