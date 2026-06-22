# Tutorial: Create Follow-Up Result Effect Proposals

Use this after an operator has reviewed ingested capability follow-up results
and chosen `accept_keep_blocked`. The command records a proposed local effect
that preserves the review decision while keeping capability activation blocked.

## Prerequisites

You need at least one accepted blocked follow-up result decision:

```bash
python3 -m agent_os.cli capability-activation-followup-results
python3 -m agent_os.cli capability-activation-followup-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted evaluator result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-results.md
```

The accepted result record must still have:

```text
activation_allowed=false
capability_enabled=false
```

## Create Proposed Effects

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-effect-proposals
```

Expected first-run output includes:

```text
capability_activation_followup_result_effect_proposals: capability_activation_followup_result_effect_proposals_recorded
accepted_decisions: 1
accepted_results: 1
effect_proposals_created: 1
existing_effect_proposals: 0
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-effect-proposals.md
```

Rerunning the command should report
`capability_activation_followup_result_effect_proposals_already_recorded` when
all accepted blocked results already have proposed effect rows.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-effect-proposals.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Effect Proposals`

Each proposed effect links back to:

- the accepted follow-up result decision;
- the ingested follow-up result record;
- the source delegation, follow-up task, activation contract, and capability;
- the idempotency key used to avoid duplicate proposals.

## What This Step Means

This step is useful because it moves an accepted blocked review into the
generic effects ledger. Later local workflows can inspect proposed effects
without pretending that the capability is enabled.

It is still only a local proposal:

- `status=proposed`
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
