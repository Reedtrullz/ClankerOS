# Tutorial: Create Downstream Tasks From Follow-Up Result Effects

Use this after `capability-activation-followup-result-effect-apply` has
recorded accepted blocked follow-up result effects as local `applied` ledger
rows. The command turns those applied effects into pending downstream proof
tasks so the next evidence plan lives in the task graph.

## Prerequisites

You need at least one applied follow-up result effect:

```bash
python3 -m agent_os.cli capability-activation-followup-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted blocked follow-up result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-effect-proposals.md
```

The applied effect must still represent blocked activation:

```text
status=applied
selected_action=accept_keep_blocked
activation_allowed=false
capability_enabled=false
```

## Create The Downstream Tasks

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-tasks
```

Expected first-run output includes:

```text
capability_activation_followup_result_tasks: capability_activation_followup_result_tasks_recorded
applied_followup_effects: 1
tasks_created: 1
existing_downstream_tasks: 0
capability_tasks_created: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-tasks.md
```

Rerunning the command should report
`capability_activation_followup_result_tasks_already_recorded` and create zero
new tasks when every applied follow-up result effect already has a downstream
task.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-tasks.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Tasks`

The created task has type `capability_activation_followup_result_task`, risk
`high`, and evidence fields linking back to the source effect, source
application, follow-up result, delegation, follow-up task, activation contract,
and capability.

## What This Step Means

This is an executable queue-state step. It does not say the capability is
ready; it records the next proof-planning work item so later routing,
delegation, and verification can operate on durable task state.

It still keeps the capability blocked:

- `activation_allowed=false`
- `capability_enabled=false`
- `approval_requests_created=0`
- `activation_actions_taken=0`
- `external_mutations_taken=0`

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not allow activation.
- This does not satisfy capability proof.
- This does not mutate capability activation contracts.
- This does not start subagents, schedule, retry, run CI, deploy, push, or
  mutate external systems.
