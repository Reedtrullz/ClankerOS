# Ingest Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Results

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations`
has created read-only evaluator delegation packets and an operator has recorded
completed evaluator output with `record-delegation-result`.

## Command

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli dashboard
```

The command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`,
creates local result records, and writes per-result JSON artifacts under
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results/`.

Repeated runs are idempotent. Completed delegations without structured result
artifacts are reported as missing artifacts without creating result rows.

## What It Records

Each result record preserves the completed delegation id, downstream task id,
source application, decision, downstream result, effect, prior delegation,
source task, contract, project, capability, evaluator profile, result summary,
and JSON evidence path.

The result artifact keeps the operator-supplied structured output next to the
source task evidence and verification plan so later review commands can make a
local decision without pretending proof is satisfied.

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
