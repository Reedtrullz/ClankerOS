# Tutorial: Apply Follow-Up Result Effect Records

Use this after `capability-activation-followup-result-effect-proposals` has
created local proposed effects from accepted `accept_keep_blocked` follow-up
result decisions. The command records that those effects were applied locally
while preserving the blocked activation state.

## Prerequisites

You need at least one proposed follow-up decision effect:

```bash
python3 -m agent_os.cli capability-activation-followup-result-effect-proposals
```

The proposed effect must still represent a blocked activation:

```text
status=proposed
selected_action=accept_keep_blocked
activation_allowed=false
capability_enabled=false
```

## Apply The Local Records

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted blocked follow-up result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-effect-proposals.md
```

Expected first-run output includes:

```text
capability_activation_followup_result_effect_apply: capability_activation_followup_result_effect_application_recorded
proposed_effects: 1
effects_applied: 1
existing_applied_effects: 0
capability_effects_applied: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-effect-application.md
```

Rerunning the command should report
`capability_activation_followup_result_effect_application_already_recorded`
when the eligible local effects are already applied.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-effect-application.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Effect Application`

Each applied effect keeps links to the source decision, result, delegation,
follow-up task, activation contract, and capability. The effect status changes
from `proposed` to `applied`, but `committed_at` remains empty because no
external or activation side effect happened.

## What This Step Means

This is a local ledger application. It lets later workflow steps distinguish
between effect proposals that still need operator application and effects the
operator has intentionally recorded as applied locally.

The next local step is to turn those applied follow-up result effects into
downstream proof tasks:

```bash
python3 -m agent_os.cli capability-activation-followup-result-tasks
```

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
