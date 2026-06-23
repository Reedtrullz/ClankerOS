# Tutorial: Apply Downstream Result Effect Task Result Effect Task Result Decision Effects Locally

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals`
has created `proposed` effect rows for accepted keep-blocked downstream result
effect task result effect result decisions. The application command records
the accepted proposal as a local ledger application and marks the effect
`applied`, but it still does not enable a capability, satisfy proof, create
approval rows, or mutate external systems.

## Prerequisites

Create proposed downstream result effect task result effect result decision
effects first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals
```

Confirm the proposal report exists:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Proposals`

## Apply Local Records

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_apply: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_application_recorded
proposed_effects: 1
effects_applied: 1
existing_applied_effects: 0
capability_effects_applied: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-application.md
```

Rerunning the command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_application_already_recorded`
and apply zero duplicate effects.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-application.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Application`

Each application row records:

- operator id and selection note
- source downstream result effect task result effect decision id
- source downstream result effect task result effect record id
- source application id
- source effect ids
- source delegation id
- downstream task id
- contract id
- capability

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not allow activation.
- This does not mutate capability activation contracts.
- This does not mutate downstream result effect task result effect result records.
- This does not mutate external systems.
- This does not route, schedule, retry, dispatch, run CI, or deploy.
