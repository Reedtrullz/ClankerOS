# Expansion Operator Approval Schema Migration Decision Ledger

- id: expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081
- status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_88a59ed82a34
- source_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43cd7e7b31b7
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_28975ae3657a
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_e52f9cb04b84
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- planned_columns: 26
- planned_indexes: 4
- migration_steps: 4
- affected_requests: 11
- schema_gaps: 11
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- approved_decisions: 0
- deferred_decisions: 0
- more_evidence_decisions: 0
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_action_required
- report_path: docs/expansion-operator-approval-schema-migration-decision-ledger.md
- created_at: 2026-06-22T10:03:27.608632+00:00

## Decision Items

- decision_status=pending_operator_action requested_action=apply_operator_approval_requests_schema approval_boundary=schema_migration target_table=operator_approval_requests allowed_actions=approve,defer,request_more_evidence reason=operator must approve, defer, or request more evidence before schema migration

## Non-Claims

- Report-only local expansion operator approval schema migration decision ledger.
- Does not apply schema migrations.
- Does not create operator_approval_requests table.
- Does not create operator_approval_requests rows.
- Does not create approval_requests rows.
- Does not approve decisions.
- Does not defer decisions.
- Does not request more evidence.
- Does not take allowed actions.
- Does not record an operator decision as taken.
- Does not collect evidence automatically.
- Does not mark the active goal complete.
- Does not enable or deploy hosted dashboard.
- Does not start or claim remote work.
- Does not schedule autonomous work.
- Does not operate browser or desktop adapters.
- Does not run CI or deploys.
- Does not enforce budgets.
- Does not promote trust.
- Does not retry or replay work.
- Does not track real spend.
- Does not change routing or claims.
- Does not mutate external systems.
