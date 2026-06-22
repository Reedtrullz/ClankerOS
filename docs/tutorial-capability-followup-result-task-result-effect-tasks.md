# Tutorial: Create Tasks From Downstream Result Decision Effects

Use this after
`capability-activation-followup-result-task-result-effect-apply` has applied
accepted keep-blocked downstream proof-plan result decision effects as local
ledger records. The task command materializes the next proof work into the
task graph while still keeping activation blocked.

## Prerequisites

Apply downstream result decision effects first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream proof-plan result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-proposals.md
```

Confirm the application report exists:

- `docs/capability-activation-followup-result-task-result-effect-application.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Effect Application`

## Create Downstream Proof Tasks

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-tasks
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_tasks: capability_activation_followup_result_task_result_effect_tasks_recorded
applied_downstream_effects: 1
tasks_created: 1
existing_downstream_tasks: 0
capability_tasks_created: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-tasks.md
```

Rerunning the command should report
`capability_activation_followup_result_task_result_effect_tasks_already_recorded`
and create zero new tasks.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-tasks.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Effect Tasks`
- `docs/next-iteration.md` for the next selected work packet

Each task preserves:

- source application id
- source downstream decision id
- source downstream result record id
- source upstream follow-up result id
- source applied effect id
- upstream follow-up effect id
- downstream task id
- contract id
- capability

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not allow activation.
- This does not mutate capability activation contracts.
- This does not mutate downstream result task records.
- This does not route, delegate, schedule, retry, run CI, or deploy.
- This does not mutate external systems.
