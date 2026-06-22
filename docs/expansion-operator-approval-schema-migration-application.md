# Expansion Operator Approval Schema Migration Application

- id: operator_approval_schema_migration_application_58b1de2348a1
- status: operator_approval_schema_migration_applied
- source_template: expansion_operator_approval_schema_migration_selection_input_template_f996d5f4b462
- source_status: operator_approval_schema_migration_selection_input_required
- source_packet: expansion_operator_approval_schema_migration_selection_packet_5b00d71060c7
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_d2536bf7efc4
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_05d8ff4beb6a
- source_request: expansion_operator_approval_schema_migration_approval_request_cd8b40d8168e
- source_plan: expansion_operator_approval_schema_migration_plan_14f74e1e91ad
- source_decision: expansion_operator_approval_schema_decision_2c10728733d4
- source_review: expansion_operator_approval_request_review_718ad693cf0f
- target_table: operator_approval_requests
- operator_id: operator
- selected_action: approve
- selection_note: Approved local operator approval request schema after reviewing the generated migration plan.
- evidence_reference: docs/expansion-operator-approval-schema-migration-selection-input-template.md
- inputs_recorded: 1
- missing_required_inputs: 0
- actions_taken: 1
- migration_applied: 1
- table_created: 1
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- report_path: docs/expansion-operator-approval-schema-migration-application.md
- created_at: 2026-06-22T14:48:24.423366+00:00

## Applied Columns

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

## Applied Indexes

- index=idx_operator_approval_requests_status columns=status
- index=idx_operator_approval_requests_subject columns=subject_type,subject_key
- index=idx_operator_approval_requests_source_decision columns=source_decision_id
- index=idx_operator_approval_requests_requested_at columns=requested_at

## Claims

- Creates operator_approval_requests table locally.

## Non-Claims

- Does not create operator approval request rows.
- Does not create approval_requests rows.
- Does not approve decisions.
- Does not enable capability promotion.
- Does not mutate external systems.
