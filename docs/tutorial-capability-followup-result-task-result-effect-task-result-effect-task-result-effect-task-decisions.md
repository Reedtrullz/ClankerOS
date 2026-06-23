# Tutorial: Review Downstream Result Effect Task Result Effect Task Result Effect Task Results

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results`
has ingested completed read-only evaluator delegation output as local result
records. The decision command records the operator's review while keeping
capability activation blocked.

## Prerequisites

Create or refresh the result records first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results
```

Inspect:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Results`

The result record should still show:

```text
activation_allowed=false
capability_enabled=false
approval_requests_created=0
activation_actions_taken=0
external_mutations_taken=0
```

## Record The Operator Decision

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect task result-effect proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results.md
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_decide: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_decisions_recorded
selected_action: accept_keep_blocked
results_ready: 1
decisions_recorded: 1
accepted_keep_blocked_decisions: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-decisions.md
```

Rerunning the same command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_decisions_already_recorded`
with `decisions_recorded: 0` and `existing_decisions: 1`.

## Other Review Actions

Use `--selected-action request_more_evidence` when the result is useful but
not enough to accept even the blocked plan. A later `accept_keep_blocked`
decision can still be recorded for the same result.

Use `--selected-action defer_review` when the operator has not reviewed the
result yet.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Decisions`

The decision report preserves:

- the operator id, selected action, note, and evidence reference
- the decided result ids
- accepted, more-evidence, deferred, and existing decision counters
- explicit zero approval, activation, and external mutation counts

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not allow activation.
- This does not satisfy capability proof.
- This does not mutate capability activation contracts.
- This does not mutate result records.
- This does not mutate external systems.
- This does not start subagents or call model providers.
- This does not run CI, deploy, schedule, retry, track spend, or promote trust.
