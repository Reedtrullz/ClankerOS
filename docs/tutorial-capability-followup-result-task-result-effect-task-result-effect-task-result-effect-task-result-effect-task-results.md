# Ingest Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Results

Use this when a read-only evaluator delegation packet for the latest downstream
proof task has been completed with `record-delegation-result`.

## Command

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli dashboard
```

## What It Records

The command reads completed `evidence_review` delegation packets for
`capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task`
tasks and creates local result records plus JSON artifacts under:

```text
docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results/
```

Repeated runs are idempotent. If a completed delegation is missing its result
artifact, the command records `..._results_missing_result_artifacts` and
creates no result record for that packet.

## Non-Claims

- Does not start subagents.
- Does not call model providers.
- Does not create `approval_requests` rows.
- Does not satisfy capability proof.
- Does not allow activation.
- Does not enable capabilities.
- Does not mutate external systems.
