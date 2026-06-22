# Tutorial: Apply The Operator Approval Request Schema

This tutorial shows how to cross the first local approval-schema boundaries.
The schema command creates the `operator_approval_requests` table only after an
explicit operator selection. The row command can then create pending local
operator approval request rows from expansion approval drafts. Neither command
approves decisions, promotes trust, dispatches work, or mutates external
systems.

## 1. Build The Report-Only Packet Chain

Run the current expansion reports until the input template exists:

```bash
python3 -m agent_os.cli goal-completion-audit
python3 -m agent_os.cli expansion-decision-brief
python3 -m agent_os.cli expansion-decision-evidence-index
python3 -m agent_os.cli expansion-operator-review-checklist
python3 -m agent_os.cli expansion-operator-decision-ledger
python3 -m agent_os.cli expansion-operator-approval-draft
python3 -m agent_os.cli expansion-operator-approval-request-review
python3 -m agent_os.cli expansion-operator-approval-schema-decision
python3 -m agent_os.cli expansion-operator-approval-schema-migration-plan
python3 -m agent_os.cli expansion-operator-approval-schema-migration-approval-request
python3 -m agent_os.cli expansion-operator-approval-schema-migration-decision-ledger
python3 -m agent_os.cli expansion-operator-approval-schema-migration-action-checklist
python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-packet
python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-input-template
```

At this point the reports should still show:

- `selected_action=none`;
- `inputs_recorded=0`;
- `migration_applied=0`;
- `table_created=0`;
- `operator_approval_rows_created=0`;
- `approval_requests_created=0`.

Those zeros are the approval boundary.

## 2. Defer Without Applying

To record an explicit non-approval decision, use `defer`:

```bash
python3 -m agent_os.cli expansion-operator-approval-schema-migration-apply \
  --operator-id operator \
  --selected-action defer \
  --selection-note "Need another review before applying the local schema." \
  --evidence-reference docs/expansion-operator-approval-schema-migration-selection-input-template.md
```

This writes `docs/expansion-operator-approval-schema-migration-application.md`
and a SQLite application row with
`status=operator_approval_schema_migration_not_approved`.

No table is created.

## 3. Approve The Local Schema

After reviewing the migration plan and input template, approve the local table
creation:

```bash
python3 -m agent_os.cli expansion-operator-approval-schema-migration-apply \
  --operator-id operator \
  --selected-action approve \
  --selection-note "Approved local operator approval request schema after reviewing the generated migration plan." \
  --evidence-reference docs/expansion-operator-approval-schema-migration-selection-input-template.md
```

Expected output includes:

```text
expansion_operator_approval_schema_migration_apply: operator_approval_schema_migration_applied
migration_applied: 1
table_created: 1
operator_approval_rows_created: 0
approval_requests_created: 0
```

The command creates `operator_approval_requests` locally and records the
columns/indexes applied in SQLite plus
`docs/expansion-operator-approval-schema-migration-application.md`.

## 4. Repeat Safely

Repeating the same approve command is idempotent. It should report:

```text
expansion_operator_approval_schema_migration_apply: operator_approval_schema_migration_already_applied
migration_applied: 0
table_created: 0
```

The repeat run records evidence that the table already exists instead of
applying the migration again.

## 5. Create Pending Operator Approval Rows

After the table exists, create local pending operator approval rows from the
latest expansion approval draft:

```bash
python3 -m agent_os.cli expansion-operator-approval-request-rows-apply \
  --operator-id operator \
  --selected-action approve \
  --selection-note "Approved local operator approval request row creation after reviewing the draft packet." \
  --evidence-reference docs/expansion-operator-approval-draft.md
```

Expected output includes:

```text
expansion_operator_approval_request_rows_apply: operator_approval_request_rows_applied
draft_requests: 11
operator_approval_rows_created: 11
approval_requests_created: 0
```

The rows are written to `operator_approval_requests` with `status=pending`.
The legacy task-scoped `approval_requests` table remains untouched.

Repeating the command is idempotent and reports
`operator_approval_request_rows_already_applied`.

## 6. Refresh Visibility

Regenerate the dashboard:

```bash
python3 -m agent_os.cli dashboard
```

Read `docs/dashboard.md` under:

```text
## Expansion Operator Approval Schema Migration Application
## Expansion Operator Approval Request Rows Application
```

The dashboard should show the latest schema selection, whether the local table
was created, how many pending operator approval rows were created, and the
explicit zero count for legacy approval rows.

## Non-Claims

This flow does not:

- decide pending operator approval request rows;
- create legacy `approval_requests` rows;
- approve pending decisions;
- promote a capability or trust level;
- run CI, deploy, push, or open a pull request;
- start workers, subagents, browser adapters, desktop adapters, retries, or
  scheduled work;
- mutate external systems.
