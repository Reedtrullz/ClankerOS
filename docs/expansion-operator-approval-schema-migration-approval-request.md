# Expansion Operator Approval Schema Migration Approval Request

- id: expansion_operator_approval_schema_migration_approval_request_9823d6efd3eb
- status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_ff20ec525835
- source_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_b4d9e8170a5d
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_4f96fb8c6a87
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- planned_columns: 26
- planned_indexes: 4
- migration_steps: 4
- affected_requests: 11
- schema_gaps: 11
- request_count: 1
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_decision_required
- report_path: docs/expansion-operator-approval-schema-migration-approval-request.md
- created_at: 2026-06-22T17:03:52.690056+00:00

## Approval Items

- request_type=schema_migration requested_action=apply_operator_approval_requests_schema approval_status=not_created approval_boundary=schema_migration target_table=operator_approval_requests allowed_actions=approve,defer,request_more_evidence reason=operator approval required before applying planned schema migration

## Non-Claims

- Report-only local expansion operator approval schema migration approval request.
- Does not apply schema migrations.
- Does not create operator_approval_requests table.
- Does not create operator_approval_requests rows.
- Does not create approval_requests rows.
- Does not approve decisions.
- Does not take allowed actions.
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
