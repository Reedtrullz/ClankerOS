# Tutorial: Latest Capability Downstream Task Records

Use this when accepted blocked downstream decision-effect applications already
exist and you want to materialize the next local proof tasks.

The command creates pending high-risk task records from applied local generic
effects. It is still a local evidence bridge. It does not approve, activate,
route, execute, retry, schedule, run CI, deploy, or mutate external systems.

## Prerequisites

Run the preceding application rung first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md
```

## Materialize Tasks

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
```

Expected first-run output shape:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_recorded
applied_downstream_effects: 1
tasks_created: 1
existing_downstream_tasks: 0
capability_tasks_created: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
```

The report is written to:

```text
docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md
```

## Idempotency Check

Run the same command again:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
```

Expected rerun posture:

```text
tasks_created: 0
existing_downstream_tasks: 1
external_mutations_taken: 0
```

The rerun records a new batch row but does not create a duplicate downstream
task for the same source effect.

## Inspect Visibility

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Use `docs/dashboard.md` for the latest batch counters and
`docs/next-iteration.md` for the next recommended local slice.

## Non-Claims

- Does not create `approval_requests` rows.
- Does not enable capabilities.
- Does not allow activation.
- Does not satisfy capability proof.
- Does not route, delegate, execute, schedule, retry, run CI, or deploy.
- Does not mutate external systems.
- Does not promote trust or mark the active expansion goal complete.
