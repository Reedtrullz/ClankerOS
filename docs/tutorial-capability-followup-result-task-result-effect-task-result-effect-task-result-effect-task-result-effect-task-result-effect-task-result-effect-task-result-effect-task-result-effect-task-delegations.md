# Tutorial: Latest Capability Downstream Task Delegations

Use this after the latest downstream task materialization command has created
pending proof tasks and you want to route them into read-only evaluator packets.

The command records local `evidence_review` routing decisions and pending
`evaluator` delegation packets. It does not start a subagent, call a model
provider, approve activation, mutate contracts, or satisfy proof.

## Prerequisites

Create the pending proof tasks first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
```

## Create Delegation Packets

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
```

Expected first-run output shape:

```text
capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations: capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations_recorded
downstream_tasks: 1
routing_decisions_created: 1
delegations_created: 1
existing_delegations: 0
execution_started: 0
network_actions_taken: 0
external_mutations_taken: 0
activation_actions_taken: 0
```

The report is written to:

```text
docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md
```

Each packet JSON is stored under `.clanker/delegations/` and carries the source
task evidence plus verification plan for later result ingestion.

## Idempotency Check

Run the same command again:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
```

Expected rerun posture:

```text
routing_decisions_created: 0
delegations_created: 0
existing_delegations: 1
external_mutations_taken: 0
```

The rerun records a new batch row but does not create a duplicate delegation
for the same pending proof task.

## Inspect Visibility

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Use `docs/dashboard.md` for the latest delegation counters and
`docs/next-iteration.md` for the next recommended local slice.

## Non-Claims

- Does not start subagents.
- Does not call model providers.
- Keeps `execution_started=0`.
- Keeps `network_actions_taken=0`.
- Does not create `approval_requests` rows.
- Does not satisfy proof.
- Does not allow activation.
- Does not enable capabilities.
- Does not mutate capability activation contracts.
- Does not mutate external systems.
- Does not run CI, deploy, retry, schedule work, or promote trust.
- Does not mark the active goal complete.
