# Expansion Operator Approval Schema Migration Plan

- id: expansion_operator_approval_schema_migration_plan_230532bbadd3
- status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_20d31b1c6e4f
- source_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
- source_review_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_912a128e4891
- source_ledger: expansion_operator_decision_ledger_69572a6acdfa
- source_checklist: expansion_operator_review_checklist_4c25f852c022
- source_index: expansion_decision_evidence_index_0dc19502eb59
- source_brief: expansion_decision_brief_9e899bc00c50
- source_audit: goal_completion_audit_52df6b8c2e20
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
- created_at: 2026-06-22T15:51:23.598531+00:00

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
