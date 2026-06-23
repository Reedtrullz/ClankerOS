# Tutorial: Ingest Downstream Result Effect Task Result Effect Task Results

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations`
has created a read-only evaluator delegation packet and the operator has a
structured result to record. The ingestion command preserves the next evidence
plan as local state without enabling the capability.

## Prerequisites

Create a downstream result effect task result effect proof task and delegation
packet first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations
```

Find the downstream result effect task result effect delegation id in:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Delegations`
- `.clanker/delegations/`

The delegation should still be a read-only evidence review:

```text
category=evidence_review
expected_output_schema=evidence_review
execution_started=false
activation_allowed=false
capability_enabled=false
```

## Record The Delegation Result

Record the operator-supplied review output:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Evaluator drafted downstream result-effect task result-effect proof evidence while keeping activation blocked." \
  --output-json '{"evidence":[{"status":"planned","summary":"Collect downstream result-effect task result-effect proof evidence."}],"findings":[{"summary":"Keep activation blocked."}]}' \
  --recorded-by operator
```

The output JSON must satisfy the delegation's `evidence_review` schema by
including at least `evidence` or `findings`.

## Ingest The Result

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-results
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_results: capability_activation_followup_result_task_result_effect_task_result_effect_task_results_recorded
completed_delegations: 1
result_records_created: 1
existing_result_records: 0
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md
```

Rerunning the command should report
`capability_activation_followup_result_task_result_effect_task_result_effect_task_results_already_recorded`
and create zero new result records for already-ingested completed delegations.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md`
- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results/<delegation>-<capability>.json`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Results`

The JSON artifact preserves:

- source decision, downstream result, application, effect, delegation, task,
  contract, project, and capability ids
- the structured delegation output
- the downstream result effect task result effect task evidence and
  verification plan
- explicit zero approval, activation, and external mutation counts

## Non-Claims

- This does not start subagents.
- This does not call model providers.
- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not allow activation.
- This does not satisfy capability proof.
- This does not mutate capability activation contracts.
- This does not mutate downstream result effect task result records.
- This does not run CI, deploy, schedule, retry, promote trust, or mutate
  external systems.
