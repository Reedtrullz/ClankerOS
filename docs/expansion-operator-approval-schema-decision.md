# Expansion Operator Approval Schema Decision

- id: expansion_operator_approval_schema_decision_124bbc4cea5a
- status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_6a969c5a2c5d
- source_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_0918d86e7319
- source_ledger: expansion_operator_decision_ledger_f763b65ef44b
- source_checklist: expansion_operator_review_checklist_a309ac520d61
- source_index: expansion_decision_evidence_index_be27494fed2f
- source_brief: expansion_decision_brief_74ba41f05da5
- source_audit: goal_completion_audit_dba1759f9ab5
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
- created_at: 2026-06-22T14:31:55.657721+00:00

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
