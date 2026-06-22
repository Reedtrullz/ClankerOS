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

## Attach Evidence

```bash
python3 -m agent_os.cli capability-activation-evidence \
  --all \
  --evidence-kind proof_checklist \
  --evidence-reference docs/capability-activation-contracts.md \
  --verification-command "python3 -m agent_os.cli capability-activation-contracts" \
  --verification-status blocked \
  --recorded-by operator \
  --summary "Current activation contracts are present but still missing capability-specific proof."
```

Expected output includes:

```text
capability_activation_evidence: capability_activation_evidence_recorded
contracts_selected: 9
evidence_records_created: 9
approval_requests_created: 0
activation_actions_taken: 0
report: docs/capability-activation-evidence.md
```

Rerunning the command should report
`capability_activation_evidence_already_recorded`.

## Record The Operator Decision

```bash
python3 -m agent_os.cli capability-activation-decide \
  --operator-id operator \
  --selected-action request_more_evidence \
  --selection-note "Requested capability-specific proof before any activation decision." \
  --evidence-reference docs/capability-activation-evidence.md
```

Expected output includes:

```text
capability_activation_decide: capability_activation_decisions_recorded
contracts_ready: 9
decisions_recorded: 9
more_evidence_decisions: 9
approval_requests_created: 0
activation_actions_taken: 0
report: docs/capability-activation-decisions.md
```

Rerunning the command should report
`capability_activation_decisions_already_recorded`.

## Create Follow-Up Tasks

```bash
python3 -m agent_os.cli capability-activation-followups
```

Expected output includes:

```text
capability_activation_followups: capability_activation_followups_recorded
contracts_selected: 9
followup_tasks_created: 9
approval_requests_created: 0
activation_actions_taken: 0
report: docs/capability-activation-followups.md
```

Rerunning the command should report
`capability_activation_followups_already_recorded`.

The generated tasks are pending high-risk
`capability_activation_followup_task` rows that point back to the source
activation contract and decision. They make the next evidence-collection work
visible to the task graph without enabling the capability.

## Create Follow-Up Delegation Packets

```bash
python3 -m agent_os.cli capability-activation-followup-delegations
```

Expected output includes:

```text
capability_activation_followup_delegations: capability_activation_followup_delegations_recorded
followup_tasks: 9
routing_decisions_created: 9
delegations_created: 9
execution_started: 0
network_actions_taken: 0
activation_actions_taken: 0
report: docs/capability-activation-followup-delegations.md
```

Rerunning the command should report
`capability_activation_followup_delegations_already_recorded`.

The generated delegation packets are pending read-only evaluator contracts.
They include the source follow-up task evidence, required artifacts, required
commands, and non-claims, but they do not start a subagent or call a model
provider.

## Non-Claims

- This does not create `approval_requests` rows.
- This does not satisfy capability evidence.
- This does not enable capabilities.
- This does not start subagents, schedule, retry, run CI, deploy, push, or
  mutate external systems.
