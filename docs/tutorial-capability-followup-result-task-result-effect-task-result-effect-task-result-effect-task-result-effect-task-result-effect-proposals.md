# Tutorial: Create Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide`
has recorded an accepted `accept_keep_blocked` operator decision for
downstream result effect task result effect task result effect task result
effect result records. The proposal command creates generic local `effects`
rows so the next local application step can be reviewed and tracked without
enabling a capability or satisfying proof.

## Prerequisites

Create, ingest, and review downstream result effect task result effect task
result effect task result effect task results first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
```

Confirm the latest decision report exists:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Decisions`

## Create Proposed Effects

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_recorded
accepted_decisions: 1
accepted_results: 1
effect_proposals_created: 1
existing_effect_proposals: 0
capability_effect_proposals: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md
```

Rerunning the same command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_already_recorded`
and create zero duplicate effects for already-proposed decisions.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals`

The report preserves:

- source decision and downstream result effect task result effect task result
  effect task result effect task result ids
- the proposed generic `effects` rows and idempotency keys
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
