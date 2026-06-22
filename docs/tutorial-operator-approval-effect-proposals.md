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

## 4. Apply Proposed Effects Locally

```bash
python3 -m agent_os.cli expansion-operator-approval-effect-apply \
  --operator-id operator \
  --selection-note "Apply approved local operator approval effect proposals as local records only." \
  --evidence-reference docs/expansion-operator-approval-effect-proposals.md
```

Expected output includes:

```text
effects_applied: 11
legacy_approval_requests_created: 0
activation_actions_taken: 0
```

The generated report is:

```text
docs/expansion-operator-approval-effect-application.md
```

Read `docs/dashboard.md` and check
`## Expansion Operator Approval Effect Application` after regenerating the
dashboard.

## Non-Claims

- Proposed effects are not applied effects.
- Applied operator approval effects are local application records, not active
  capabilities.
- These commands do not enable capabilities.
- These commands do not promote trust, route work, schedule work, retry work,
  or track spend.
- These commands do not run CI, deploy, push, open pull requests, or mutate
  external systems.
