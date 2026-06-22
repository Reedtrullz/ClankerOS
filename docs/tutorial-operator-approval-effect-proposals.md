# Tutorial: Operator Approval Effect Proposals

Use this after the local operator approval request schema exists, request rows
have been created, and an operator has approved the pending rows.

## 1. Confirm Approved Request Decisions

```bash
python3 -m agent_os.cli expansion-operator-approval-request-decide \
  --operator-id operator \
  --selected-action approve \
  --selection-note "Approved pending operator approval requests after reviewing evidence." \
  --evidence-reference docs/expansion-operator-approval-request-rows-application.md
```

The command should report approved decisions and
`approval_requests_created: 0`.

## 2. Create Proposed Effects

```bash
python3 -m agent_os.cli expansion-operator-approval-effect-proposals
```

Expected output includes:

```text
effect_proposals_created: 11
legacy_approval_requests_created: 0
activation_actions_taken: 0
```

The generated report is:

```text
docs/expansion-operator-approval-effect-proposals.md
```

## 3. Inspect The Dashboard

```bash
python3 -m agent_os.cli dashboard
```

Read `docs/dashboard.md` and check
`## Expansion Operator Approval Effect Proposals`.

## Non-Claims

- Proposed effects are not applied effects.
- The command does not enable capabilities.
- The command does not promote trust, route work, schedule work, retry work, or
  track spend.
- The command does not run CI, deploy, push, open pull requests, or mutate
  external systems.
