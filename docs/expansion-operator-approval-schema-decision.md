# Expansion Operator Approval Schema Decision

- id: expansion_operator_approval_schema_decision_1cc901add127
- status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_38b521d46367
- source_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_9973bcb20264
- source_ledger: expansion_operator_decision_ledger_450c01b7b76a
- source_checklist: expansion_operator_review_checklist_674a7cd36f9b
- source_index: expansion_decision_evidence_index_a734ba93a874
- source_brief: expansion_decision_brief_25100b2ce4eb
- source_audit: goal_completion_audit_ba7c7b9b8b14
- affected_requests: 11
- schema_gaps: 11
- missing_fields: 7
- external_requests: 2
- capability_requests: 9
- decision_options: 3
- recommended_option: operator_approval_requests_table
- rejected_options: 2
- schema_objects: 1
- migration_applied: 0
- created_approval_requests: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_plan_required
- report_path: docs/expansion-operator-approval-schema-decision.md
- created_at: 2026-06-22T16:24:21.173240+00:00

## Decision Options

- option=operator_approval_requests_table disposition=recommended schema_object=operator_approval_requests schema_status=not_applied missing_fields=task_id,goal_id,project_id,task_type,risk_level,policy_name,policy_version reason=preserves the existing task approval gate while modeling external and capability approval subjects explicitly
- option=make_approval_requests_task_fields_nullable disposition=rejected schema_object=approval_requests schema_status=not_applied missing_fields=task_id,goal_id,project_id,task_type,risk_level,policy_name,policy_version reason=weakens the current task-approval contract and risks ambiguous task dispatch semantics
- option=synthesize_placeholder_tasks_for_operator_decisions disposition=rejected schema_object=tasks schema_status=not_applied missing_fields=task_id,goal_id,project_id,task_type,risk_level,policy_name,policy_version reason=mixes non-executable operator decisions into the executable task queue

## Non-Claims

- Report-only local expansion operator approval schema decision.
- Does not apply schema migrations.
- Does not create approval_requests rows.
- Does not create operator approval rows.
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
