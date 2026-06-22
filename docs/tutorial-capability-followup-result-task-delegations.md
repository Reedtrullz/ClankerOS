# Tutorial: Route Downstream Follow-Up Result Tasks To Delegation Packets

Use this after `capability-activation-followup-result-tasks` has created
pending `capability_activation_followup_result_task` rows. The command routes
those downstream proof tasks to read-only evaluator delegation packets so the
next evidence plan can be reviewed without enabling the capability.

## Prerequisites

You need at least one pending downstream proof task:

```bash
python3 -m agent_os.cli capability-activation-followup-result-tasks
```

The task should still represent blocked activation:

```text
task_type=capability_activation_followup_result_task
status=pending
activation_allowed=false
capability_enabled=false
```

## Create The Delegation Packets

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-delegations
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_delegations: capability_activation_followup_result_task_delegations_recorded
downstream_tasks: 1
routing_decisions_created: 1
delegations_created: 1
existing_delegations: 0
execution_started: 0
network_actions_taken: 0
external_mutations_taken: 0
activation_actions_taken: 0
report: docs/capability-activation-followup-result-task-delegations.md
```

Rerunning the command should report
`capability_activation_followup_result_task_delegations_already_recorded` and
create zero new routing decisions or delegations when every pending downstream
task already has a packet.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-delegations.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Delegations`
- `.clanker/delegations/<task-id>-plan-next-proof-evidence-for-<capability>.json`

The delegation artifact should show:

- `assigned_profile=evaluator`
- `category=evidence_review`
- `expected_output_schema=evidence_review`
- `execution_started=false`
- `network_actions_taken=0`
- `external_mutations_taken=0`
- forbidden write, commit, shell, approval, and external-state mutation actions

## What This Step Means

This is a local routing and packet-materialization step. It makes the next
proof-plan review explicit and durable, but it does not run the review.

It still keeps the capability blocked:

- `activation_allowed=false`
- `capability_enabled=false`
- `approval_requests_created=0`
- `activation_actions_taken=0`
- `external_mutations_taken=0`

## Non-Claims

- This does not start subagents.
- This does not call model providers.
- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not allow activation.
- This does not satisfy capability proof.
- This does not run CI, deploy, schedule, retry, promote trust, or mutate
  external systems.
