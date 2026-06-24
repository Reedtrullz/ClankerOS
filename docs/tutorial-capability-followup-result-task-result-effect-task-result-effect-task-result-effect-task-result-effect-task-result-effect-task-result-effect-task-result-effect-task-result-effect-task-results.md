# Ingest Latest Downstream Result Effect Task Results

Use this after the latest downstream delegation command has created read-only
evaluator packets and an operator has recorded structured evaluator output with
`record-delegation-result`.

The ingestion command is local-only. It turns completed evaluator delegation
artifacts into durable result rows and per-result JSON evidence. It does not
start a subagent, call a model provider, approve activation, satisfy proof, or
mutate external systems.

## Prerequisites

Create the pending evaluator packet first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
```

Then record structured output for the pending delegation:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Evaluator found the next evidence plan remains blocked pending capability-specific proof." \
  --output-json '{"status":"blocked_pending_proof","findings":["No activation-ready proof was produced."],"recommended_next_action":"record_operator_review_decision"}'
```

`record-delegation-result` writes the delegation result artifact and marks the
delegation completed. The result-ingestion command will skip completed
delegations that do not have non-empty structured output.

## Ingest Results

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
```

Expected first-run output shape:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results_recorded
completed_delegations: 1
result_records_created: 1
existing_result_records: 0
missing_result_artifacts: 0
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
```

The report is written to:

```text
docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
```

Per-result JSON artifacts are written under:

```text
docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results/
```

## Idempotency Check

Run the same command again:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
```

Expected rerun posture:

```text
result_records_created: 0
existing_result_records: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
```

The rerun records a new batch row but does not create a duplicate result row
for the same completed delegation.

## Inspect Visibility

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Use `docs/dashboard.md` for the latest result counters and
`docs/next-iteration.md` for the next recommended local slice.

## Non-Claims

- Does not start subagents.
- Does not call model providers.
- Does not create `approval_requests` rows.
- Does not enable capabilities.
- Does not satisfy capability proof.
- Does not allow activation.
- Does not mutate capability activation contracts.
- Does not mutate external systems.
- Does not run CI, deploy, retry, schedule work, or promote trust.
- Does not mark the active goal complete.
