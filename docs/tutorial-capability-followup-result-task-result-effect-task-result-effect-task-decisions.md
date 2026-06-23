# Tutorial: Review Downstream Result Effect Task Result Effect Task Decisions

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-results`
has ingested completed downstream result effect task result effect delegation
outputs. The decision command records the operator's posture on those result
records without enabling a capability or treating the evidence plan as
satisfied proof.

## Prerequisites

Create and ingest downstream result effect task result effect results first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Evaluator drafted downstream result-effect task result-effect proof evidence while keeping activation blocked." \
  --output-json '{"evidence":[{"status":"planned","summary":"Collect downstream result-effect task result-effect proof evidence."}],"findings":[{"summary":"Keep activation blocked."}]}' \
  --recorded-by operator
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-results
```

Confirm the latest result report exists:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Results`

## Record The Decision

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md
```

Allowed actions are:

- `accept_keep_blocked`
- `request_more_evidence`
- `defer_review`

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_decide: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_decisions_recorded
selected_action: accept_keep_blocked
results_ready: 1
decisions_recorded: 1
accepted_keep_blocked_decisions: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-decisions.md
```

Rerunning the same command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_task_result_decisions_already_recorded`
and create zero new decisions for already-decided result records.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-decisions.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Decisions`

The report preserves:

- operator id, selected action, note, and evidence reference
- decided downstream result effect task result effect result ids
- action counters for accepted, more-evidence, and deferred decisions
- explicit zero approval, activation, and external mutation counts

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not allow activation.
- This does not mutate capability activation contracts.
- This does not mutate downstream result effect task result effect result records.
- This does not mutate external systems.
