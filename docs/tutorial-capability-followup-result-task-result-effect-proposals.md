# Tutorial: Propose Effects From Downstream Result Task Decisions

Use this after `capability-activation-followup-result-task-result-decide` has
recorded an `accept_keep_blocked` operator decision for downstream proof-plan
result records. The proposal command turns that accepted blocked posture into
generic local `effects` rows without applying the effects or enabling a
capability.

## Prerequisites

Create, ingest, and review downstream proof-plan results first:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-results
python3 -m agent_os.cli capability-activation-followup-result-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-results.md
```

Confirm the latest decision report exists:

- `docs/capability-activation-followup-result-task-decisions.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Decisions`

## Create Proposed Effects

Run:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-proposals
```

Expected first-run output includes:

```text
capability_activation_followup_result_task_result_effect_proposals: capability_activation_followup_result_task_result_effect_proposals_recorded
accepted_decisions: 1
accepted_results: 1
effect_proposals_created: 1
existing_effect_proposals: 0
capability_effect_proposals: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
report: docs/capability-activation-followup-result-task-result-effect-proposals.md
```

Rerunning the command should report
`capability_activation_followup_result_task_result_effect_proposals_already_recorded`
and create zero new effects for already-proposed downstream result decisions.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-result-task-result-effect-proposals.md`
- `docs/dashboard.md`, section
  `## Capability Activation Follow-Up Result Task Effect Proposals`

Each proposed effect links:

- source downstream result decision id
- source downstream result record id
- source upstream follow-up result id
- source effect id
- downstream task id
- activation contract id
- capability

## Non-Claims

- This does not apply proposed effects.
- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not allow activation.
- This does not mutate capability activation contracts.
- This does not mutate downstream result task records.
- This does not mutate external systems.
