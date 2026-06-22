# Expansion Operator Approval Schema Migration Plan

- id: expansion_operator_approval_schema_migration_plan_64f904d9406e
- status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_1cc901add127
- source_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_38b521d46367
- source_review_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_9973bcb20264
- source_ledger: expansion_operator_decision_ledger_450c01b7b76a
- source_checklist: expansion_operator_review_checklist_674a7cd36f9b
- source_index: expansion_decision_evidence_index_a734ba93a874
- source_brief: expansion_decision_brief_25100b2ce4eb
- source_audit: goal_completion_audit_ba7c7b9b8b14
- recommended_option: operator_approval_requests_table
- target_table: operator_approval_requests
- affected_requests: 11
- schema_gaps: 11
- missing_fields: 7
- external_requests: 2
- capability_requests: 9
- planned_columns: 26
- planned_indexes: 4
- migration_steps: 4
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_approval_required
- report_path: docs/expansion-operator-approval-schema-migration-plan.md
- created_at: 2026-06-22T16:24:21.304914+00:00

## Planned Columns

- column=id definition=text primary key
- column=source_decision_id definition=text not null
- column=source_review_id definition=text not null
- column=source_draft_id definition=text not null
- column=source_ledger_id definition=text not null
- column=source_checklist_id definition=text not null
- column=source_index_id definition=text not null
- column=source_brief_id definition=text not null
- column=source_audit_id definition=text not null
- column=subject_type definition=text not null
- column=subject_key definition=text not null
- column=request_kind definition=text not null
- column=capability_key definition=text
- column=approval_boundary definition=text not null
- column=allowed_actions definition=text not null
- column=status definition=text not null
- column=reason definition=text not null
- column=policy_name definition=text not null
- column=policy_version definition=text not null
- column=requested_by definition=text not null
- column=decided_by definition=text
- column=decision_note definition=text
- column=requested_at definition=text not null
- column=decided_at definition=text
- column=evidence_path definition=text
- column=created_at definition=text not null

## Planned Indexes

- index=idx_operator_approval_requests_status columns=status status=planned
- index=idx_operator_approval_requests_subject columns=subject_type,subject_key status=planned
- index=idx_operator_approval_requests_source_decision columns=source_decision_id status=planned
- index=idx_operator_approval_requests_requested_at columns=requested_at status=planned

## Migration Steps

- step=create_table target=operator_approval_requests status=planned
- step=create_indexes target=operator_approval_requests status=planned
- step=preserve_existing_approval_requests_contract target=approval_requests status=planned
- step=require_operator_approval_before_apply target=operator_approval_requests status=planned

## Non-Claims

- Report-only local expansion operator approval schema migration plan.
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
