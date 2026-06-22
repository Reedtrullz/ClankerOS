# Tutorial: Capability Activation Contracts

Use this when applied capability effects have already been materialized into
pending activation-gate tasks and you want the next blocked packet of evidence
requirements.

## Prerequisites

Run the operator approval effect chain through activation tasks:

```bash
python3 -m agent_os.cli expansion-operator-approval-effect-proposals
python3 -m agent_os.cli expansion-operator-approval-effect-apply \
  --operator-id operator \
  --selection-note "Apply approved local operator approval effect proposals as local records only." \
  --evidence-reference docs/expansion-operator-approval-effect-proposals.md
python3 -m agent_os.cli capability-activation-tasks
```

## Create Contracts

```bash
python3 -m agent_os.cli capability-activation-contracts
```

Expected output includes:

```text
capability_activation_contracts: capability_activation_contracts_recorded
activation_tasks: 9
contracts_created: 9
approval_requests_created: 0
activation_actions_taken: 0
report: docs/capability-activation-contracts.md
```

Rerunning the command should report
`capability_activation_contracts_already_recorded` and create no duplicate
contracts.

## Inspect The Evidence

Read:

- `docs/capability-activation-contracts.md`
- `docs/dashboard.md`, section `## Capability Activation Contracts`

Each contract should be `blocked_pending_evidence` with
`explicit_operator_approval_required`, `blocked_until_evidence_verified`, and
`activation_allowed=false`.

## Non-Claims

- This does not create `approval_requests` rows.
- This does not satisfy capability evidence.
- This does not enable capabilities.
- This does not route, schedule, retry, dispatch, run CI, deploy, push, or
  mutate external systems.
