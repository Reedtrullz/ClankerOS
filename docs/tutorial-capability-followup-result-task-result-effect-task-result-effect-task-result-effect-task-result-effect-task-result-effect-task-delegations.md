# Route Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Tasks

Use this after
`capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks`
has created pending downstream proof tasks.

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli dashboard
```

The command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`,
records one local `evidence_review` routing decision and one pending
`evaluator` delegation packet per pending downstream task that does not already
have a packet, and stores packet JSON under `.clanker/delegations/`.

The delegation artifact includes the source task evidence, required verification
gates, routing decision, allowed read-only tools, forbidden actions, and
`expected_output_schema=evidence_review`. It is a durable packet for a later
result-ingestion command, not proof that a subagent actually ran.

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
- Does not mutate downstream result effect task result effect task result effect task result effect task result records.
- Does not mutate external systems.
- Does not run CI, deploy, retry, schedule work, or promote trust.
- Does not mark the active goal complete.
