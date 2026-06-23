# Tutorial: Apply Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals`
has created proposed generic `effects` rows from accepted blocked downstream
result effect task result effect task result effect task result effect task
result decisions. The application command records the operator's local
acceptance of those proposed effects, marks them `applied`, and still keeps
capability activation blocked.

## Prerequisites

Create the proposed effects first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals
```

Confirm this report exists:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`

## Apply Proposed Effects Locally

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result-effect task result-effect task result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_apply: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_recorded
proposed_effects: 1
effects_applied: 1
existing_applied_effects: 0
capability_effects_applied: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md
```

Rerunning the same command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_already_recorded`
with `effects_applied: 0` and `existing_applied_effects: 1`.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Application`

The report preserves:

- the application id and operator selection note
- source decision and downstream result ids
- applied effect ids and idempotency keys
- capability, task, result, delegation, application, effect, contract, project,
  and evidence references
- explicit zero approval, activation, and external mutation counts

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not allow activation.
- This does not mutate capability activation contracts.
- This does not mutate downstream result effect task result effect task result
  effect task result effect task result records.
- This does not mutate external systems.
- This does not run CI, deploy, schedule, retry, track spend, or promote trust.
