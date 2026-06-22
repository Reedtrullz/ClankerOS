# Agent System Dashboard

## Queue Health

- pending: 0
- waiting_approval: 0
- claimed: 0
- running: 0
- verifying: 0
- completed: 326
- blocked: 0
- failed: 0
- active: 0
- needs_attention: 0

## Iteration Loop

- status: planned
- focus: Review current evidence and add the next actionable queue item.
- source: tasks.md#fallback
- packet: docs/next-iteration.md
- created_at: 2026-06-22T11:05:36.538974+00:00

## Simplicity Guardrail

- policy: highest-score-then-lowest-complexity
- reason: selected fallback because no actionable queue items were found
- selected_score: 0
- selected_complexity: 0
- selected_focus: Review current evidence and add the next actionable queue item.

## Expansion Operator Approval Schema Decision

- status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_e52f9cb04b84
- source_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_4e8e020bceda
- source_ledger: expansion_operator_decision_ledger_3f19bbf99553
- source_checklist: expansion_operator_review_checklist_ed281b99faf2
- source_index: expansion_decision_evidence_index_d3745cabb2c9
- source_brief: expansion_decision_brief_811755ec3d0e
- source_audit: goal_completion_audit_a710217dd757
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
- report: docs/expansion-operator-approval-schema-decision.md

- expansion_operator_approval_schema_decision_28975ae3657a: status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_e52f9cb04b84 source_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_4e8e020bceda source_ledger=expansion_operator_decision_ledger_3f19bbf99553 source_checklist=expansion_operator_review_checklist_ed281b99faf2 source_index=expansion_decision_evidence_index_d3745cabb2c9 source_brief=expansion_decision_brief_811755ec3d0e source_audit=goal_completion_audit_a710217dd757 affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 decision_options=3 recommended_option=operator_approval_requests_table rejected_options=2 schema_objects=1 migration_applied=0 created_approval_requests=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_plan_required report=docs/expansion-operator-approval-schema-decision.md

## Expansion Operator Approval Schema Migration Plan

- status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_28975ae3657a
- source_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_e52f9cb04b84
- source_review_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_4e8e020bceda
- source_ledger: expansion_operator_decision_ledger_3f19bbf99553
- source_checklist: expansion_operator_review_checklist_ed281b99faf2
- source_index: expansion_decision_evidence_index_d3745cabb2c9
- source_brief: expansion_decision_brief_811755ec3d0e
- source_audit: goal_completion_audit_a710217dd757
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
- report: docs/expansion-operator-approval-schema-migration-plan.md

- expansion_operator_approval_schema_migration_plan_43cd7e7b31b7: status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_28975ae3657a source_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_e52f9cb04b84 source_review_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_4e8e020bceda source_ledger=expansion_operator_decision_ledger_3f19bbf99553 source_checklist=expansion_operator_review_checklist_ed281b99faf2 source_index=expansion_decision_evidence_index_d3745cabb2c9 source_brief=expansion_decision_brief_811755ec3d0e source_audit=goal_completion_audit_a710217dd757 recommended_option=operator_approval_requests_table target_table=operator_approval_requests affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 planned_columns=26 planned_indexes=4 migration_steps=4 migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_approval_required report=docs/expansion-operator-approval-schema-migration-plan.md

## Expansion Operator Approval Schema Migration Approval Request

- status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43cd7e7b31b7
- source_status: operator_approval_schema_migration_plan_ready
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
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_decision_required
- report: docs/expansion-operator-approval-schema-migration-approval-request.md

- expansion_operator_approval_schema_migration_approval_request_88a59ed82a34: status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43cd7e7b31b7 source_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_28975ae3657a source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_e52f9cb04b84 source_review_status=approval_request_schema_review_required target_table=operator_approval_requests planned_columns=26 planned_indexes=4 migration_steps=4 affected_requests=11 schema_gaps=11 request_count=1 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_decision_required report=docs/expansion-operator-approval-schema-migration-approval-request.md

## Expansion Operator Approval Schema Migration Decision Ledger

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
- report: docs/expansion-operator-approval-schema-migration-decision-ledger.md

- expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081: status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_88a59ed82a34 source_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43cd7e7b31b7 source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_28975ae3657a source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_e52f9cb04b84 source_review_status=approval_request_schema_review_required target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 approved_decisions=0 deferred_decisions=0 more_evidence_decisions=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_action_required report=docs/expansion-operator-approval-schema-migration-decision-ledger.md

## Expansion Operator Approval Schema Migration Action Checklist

- status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081
- source_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_88a59ed82a34
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43cd7e7b31b7
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_28975ae3657a
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_e52f9cb04b84
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- action_count: 1
- pending_actions: 1
- actions_taken: 0
- selected_action: none
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_selection_required
- report: docs/expansion-operator-approval-schema-migration-action-checklist.md

- expansion_operator_approval_schema_migration_action_checklist_c8d344afd257: status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081 source_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_88a59ed82a34 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43cd7e7b31b7 source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_28975ae3657a source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_required report=docs/expansion-operator-approval-schema-migration-action-checklist.md

## Expansion Operator Approval Schema Migration Selection Packet

- status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_c8d344afd257
- source_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_88a59ed82a34
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43cd7e7b31b7
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_28975ae3657a
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_e52f9cb04b84
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- action_count: 1
- pending_actions: 1
- actions_taken: 0
- selected_action: none
- selection_count: 1
- pending_selections: 1
- selections_recorded: 0
- approve_selections: 0
- defer_selections: 0
- more_evidence_selections: 0
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_selection_input_required
- report: docs/expansion-operator-approval-schema-migration-selection-packet.md

- expansion_operator_approval_schema_migration_selection_packet_05fdef0caa17: status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_c8d344afd257 source_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081 source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_88a59ed82a34 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43cd7e7b31b7 source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_28975ae3657a source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 approve_selections=0 defer_selections=0 more_evidence_selections=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_input_required report=docs/expansion-operator-approval-schema-migration-selection-packet.md

## Queue Health Checks

- blocked_threshold: 2
- failed_threshold: 2
- hotspots: 0

- none

## Handoff Review

- status: clear
- current_focus: Review current evidence and add the next actionable queue item.
- blocked_tasks: 0
- stale_handoffs: 0
- report: docs/handoff-review.md

- none

## Eval After Change

- failed: 0

- eval_after_change_bd85fa596ed7: status=pass change=Add Expansion Operator Approval Schema Migration Selection Input Template from selection packets files=agent_os/expansion_operator_approval_schema_migration_selection_input_template.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_21b6a386585b results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_0d383518167b: status=pass change=Add Expansion Operator Approval Schema Migration Selection Packet from action checklists files=agent_os/expansion_operator_approval_schema_migration_selection_packet.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_53c46f6d9926 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_95daf953bd95: status=pass change=Add Expansion Operator Approval Schema Migration Action Checklist from decision ledgers files=agent_os/expansion_operator_approval_schema_migration_action_checklist.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_b4567c7f4709 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_c7b6839703d1: status=pass change=Add Expansion Operator Approval Schema Migration Decision Ledger from approval requests files=agent_os/expansion_operator_approval_schema_migration_decision_ledger.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_fa04499de687 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_71511c86450e: status=pass change=Add Expansion Operator Approval Schema Migration Approval Request from migration plans files=agent_os/expansion_operator_approval_schema_migration_approval_request.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_84fd053bbdf7 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md

## Learning Distillation

- status: stable
- stable_learnings: 1
- source_learnings: 24
- min_occurrences: 3
- report: docs/learning-distillation.md

- learning_distillation_255ae71ad9db: status=stable stable_learnings=1 source_learnings=24 min_occurrences=3 report=docs/learning-distillation.md
- Run run_<id> showed that the first closed loop can be verified through file evidence before expanding to broader domains. occurrences=24 runs=run_ef049fa8bc1b,run_442800b11c88,run_85aba7975e44,run_e00b0c8f8421,run_19c337ce39cd,run_e641748ed7b5,run_29f35bcd3c4a,run_5850098a3daf,run_bdee61e695bb,run_5c2e1d7e727b,run_395eef2e002e,run_9a7518e69a09,run_c43d94c11c75,run_24c24ce0765e,run_42129a67e1fe,run_5953ddebb94f,run_3f0260c058b7,run_4ca70d56e922,run_b3345106e3e7,run_e9eb60b88b08,run_aff094d41613,run_6bba00951a85,run_d1c5f8393518,run_ff65446deb79

## Budget And Trust Posture

- status: report_only
- tasks: 326
- budget_state: not_tracked
- trust_state: not_tracked
- risk_counts: low=326
- report: docs/budget-trust-posture.md

- budget_trust_posture_68d682f8a130: status=report_only tasks=326 budget_state=not_tracked trust_state=not_tracked risk_counts=low=326 report=docs/budget-trust-posture.md

## Dispatch Posture History

- status: report_only
- snapshots: 25
- latest_tasks: 326
- task_delta: 100
- latest_risk_counts: low=326
- report: docs/dispatch-posture-history.md

- dispatch_posture_history_11c91397ed73: status=report_only snapshots=25 latest_tasks=326 task_delta=100 latest_risk_counts=low=326 report=docs/dispatch-posture-history.md

## Dispatch Posture Snapshot Review

- status: fresh
- snapshots: 25
- stale_snapshots: 22
- latest_snapshot_age_seconds: 6
- stale_after_seconds: 3600
- report: docs/dispatch-posture-staleness.md

- dispatch_posture_staleness_72eb5fdaa611: status=fresh snapshots=25 stale_snapshots=22 latest_snapshot_age_seconds=6 stale_after_seconds=3600 latest_tasks=326 latest_risk_counts=low=326 report=docs/dispatch-posture-staleness.md

## Dispatch Posture Refresh Recommendation

- status: no_refresh_needed
- source_review: dispatch_posture_staleness_72eb5fdaa611
- source_status: fresh
- recommended_commands: none
- report: docs/dispatch-posture-refresh.md

- dispatch_posture_refresh_b3bc10fe4e1d: status=no_refresh_needed source_review=dispatch_posture_staleness_72eb5fdaa611 source_status=fresh recommended_commands=none report=docs/dispatch-posture-refresh.md

## Capability Expansion Ledger

- status: report_only
- capabilities: 9
- ready: 0
- deferred: 9
- approval_boundary: explicit_operator_approval_required
- report: docs/capability-expansion-ledger.md

- capability_expansion_ledger_dd8b1a681d81: status=report_only capabilities=9 ready=0 deferred=9 approval_boundary=explicit_operator_approval_required report=docs/capability-expansion-ledger.md

## Capability Readiness Review

- status: blocked_by_missing_evidence
- source_ledger: capability_expansion_ledger_dd8b1a681d81
- capabilities: 9
- ready: 0
- not_ready: 9
- missing_evidence: 9
- recommended_commands: none
- report: docs/capability-readiness-review.md

- capability_readiness_review_6d59ab5cf11d: status=blocked_by_missing_evidence source_ledger=capability_expansion_ledger_dd8b1a681d81 capabilities=9 ready=0 not_ready=9 missing_evidence=9 recommended_commands=none report=docs/capability-readiness-review.md

## Capability Proof Gap Index

- status: open_gaps
- source_review: capability_readiness_review_6d59ab5cf11d
- capabilities: 9
- gaps: 9
- missing_evidence: 9
- blocked_capabilities: 9
- next_proofs: 9
- recommended_commands: none
- report: docs/capability-proof-gap-index.md

- capability_proof_gap_index_b1fe73da8795: status=open_gaps source_review=capability_readiness_review_6d59ab5cf11d source_status=blocked_by_missing_evidence gaps=9 missing_evidence=9 blocked_capabilities=9 next_proofs=9 recommended_commands=none report=docs/capability-proof-gap-index.md

## Capability Approval Boundary Matrix

- status: approval_required
- source_index: capability_proof_gap_index_b1fe73da8795
- capabilities: 9
- boundaries: 1
- gaps: 9
- blocked_capabilities: 9
- approvals_required: 9
- recommended_commands: none
- report: docs/capability-approval-boundary-matrix.md

- capability_approval_boundary_matrix_a76bf3bf7bd8: status=approval_required source_index=capability_proof_gap_index_b1fe73da8795 source_status=open_gaps boundaries=1 gaps=9 blocked_capabilities=9 approvals_required=9 recommended_commands=none report=docs/capability-approval-boundary-matrix.md

## Capability Evidence Collection Plan

- status: evidence_required
- source_matrix: capability_approval_boundary_matrix_a76bf3bf7bd8
- capabilities: 9
- evidence_items: 9
- manual_collection: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-evidence-collection-plan.md

- capability_evidence_collection_plan_471f1d177581: status=evidence_required source_matrix=capability_approval_boundary_matrix_a76bf3bf7bd8 source_status=approval_required evidence_items=9 manual_collection=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-evidence-collection-plan.md

## Capability Promotion Gate Checklist

- status: promotion_blocked
- source_plan: capability_evidence_collection_plan_471f1d177581
- capabilities: 9
- gates: 9
- blocked_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-promotion-gate-checklist.md

- capability_promotion_gate_checklist_d2607c4ce10b: status=promotion_blocked source_plan=capability_evidence_collection_plan_471f1d177581 source_status=evidence_required gates=9 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-gate-checklist.md

## Capability Promotion Decision Ledger

- status: promotion_decision_blocked
- source_checklist: capability_promotion_gate_checklist_d2607c4ce10b
- capabilities: 9
- decisions: 9
- deferred_promotions: 9
- operator_decisions_required: 0
- blocked_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-promotion-decision-ledger.md

- capability_promotion_decision_ledger_83caee14a891: status=promotion_decision_blocked source_checklist=capability_promotion_gate_checklist_d2607c4ce10b source_status=promotion_blocked decisions=9 deferred_promotions=9 operator_decisions_required=0 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-decision-ledger.md

## Capability Trust Promotion Audit

- status: trust_promotion_blocked
- source_ledger: capability_promotion_decision_ledger_83caee14a891
- capabilities: 9
- audits: 9
- blocked_trust_promotions: 9
- operator_reviews_required: 0
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-trust-promotion-audit.md

- capability_trust_promotion_audit_c35eaff06b80: status=trust_promotion_blocked source_ledger=capability_promotion_decision_ledger_83caee14a891 source_status=promotion_decision_blocked audits=9 blocked_trust_promotions=9 operator_reviews_required=0 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-trust-promotion-audit.md

## Capability Automatic Retry Audit

- status: automatic_retry_blocked
- source_audit: capability_trust_promotion_audit_c35eaff06b80
- capabilities: 9
- audits: 9
- blocked_retries: 9
- operator_reviews_required: 0
- blocked_trust_promotions: 9
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-automatic-retry-audit.md

- capability_automatic_retry_audit_32138c4e2f96: status=automatic_retry_blocked source_audit=capability_trust_promotion_audit_c35eaff06b80 source_status=trust_promotion_blocked audits=9 blocked_retries=9 operator_reviews_required=0 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-automatic-retry-audit.md

## Capability Real Cost Tracking Audit

- status: real_cost_tracking_blocked
- source_audit: capability_automatic_retry_audit_32138c4e2f96
- capabilities: 9
- audits: 9
- blocked_cost_tracking: 9
- operator_reviews_required: 0
- blocked_retries: 9
- blocked_trust_promotions: 9
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-real-cost-tracking-audit.md

- capability_real_cost_tracking_audit_78660d24d257: status=real_cost_tracking_blocked source_audit=capability_automatic_retry_audit_32138c4e2f96 source_status=automatic_retry_blocked audits=9 blocked_cost_tracking=9 operator_reviews_required=0 blocked_retries=9 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-real-cost-tracking-audit.md

## Hosted Dashboard Proof Checklist

- status: hosted_dashboard_proof_blocked
- source_kind: real_cost_tracking_proof_checklist
- source_checklist: real_cost_tracking_proof_checklist_81ae753ceb8c
- source_audit: none
- source_status: real_cost_tracking_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_dashboard_proofs: 1
- operator_reviews_required: 0
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/hosted-dashboard-proof-checklist.md

- hosted_dashboard_proof_checklist_620a518a9498: status=hosted_dashboard_proof_blocked source_kind=real_cost_tracking_proof_checklist source_checklist=real_cost_tracking_proof_checklist_81ae753ceb8c source_audit=none source_status=real_cost_tracking_proof_blocked checklist_items=1 blocked_dashboard_proofs=1 operator_reviews_required=0 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/hosted-dashboard-proof-checklist.md

## Remote Worker Proof Checklist

- status: remote_worker_proof_blocked
- source_checklist: hosted_dashboard_proof_checklist_620a518a9498
- source_status: hosted_dashboard_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_worker_proofs: 1
- operator_reviews_required: 0
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/remote-worker-proof-checklist.md

- remote_worker_proof_checklist_2efdc0b8a79f: status=remote_worker_proof_blocked source_checklist=hosted_dashboard_proof_checklist_620a518a9498 source_status=hosted_dashboard_proof_blocked checklist_items=1 blocked_worker_proofs=1 operator_reviews_required=0 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/remote-worker-proof-checklist.md

## Autonomous Scheduling Proof Checklist

- status: autonomous_scheduling_proof_blocked
- source_checklist: remote_worker_proof_checklist_2efdc0b8a79f
- source_status: remote_worker_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_scheduling_proofs: 1
- operator_reviews_required: 0
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/autonomous-scheduling-proof-checklist.md

- autonomous_scheduling_proof_checklist_be630dc43dbc: status=autonomous_scheduling_proof_blocked source_checklist=remote_worker_proof_checklist_2efdc0b8a79f source_status=remote_worker_proof_blocked checklist_items=1 blocked_scheduling_proofs=1 operator_reviews_required=0 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/autonomous-scheduling-proof-checklist.md

## Browser Desktop Adapter Proof Checklist

- status: browser_desktop_adapter_proof_blocked
- source_checklist: autonomous_scheduling_proof_checklist_be630dc43dbc
- source_status: autonomous_scheduling_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_adapter_proofs: 1
- operator_reviews_required: 0
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/browser-desktop-adapter-proof-checklist.md

- browser_desktop_adapter_proof_checklist_98d8fa8d01be: status=browser_desktop_adapter_proof_blocked source_checklist=autonomous_scheduling_proof_checklist_be630dc43dbc source_status=autonomous_scheduling_proof_blocked checklist_items=1 blocked_adapter_proofs=1 operator_reviews_required=0 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/browser-desktop-adapter-proof-checklist.md

## CI Deploy Proof Checklist

- status: ci_deploy_proof_blocked
- source_checklist: browser_desktop_adapter_proof_checklist_98d8fa8d01be
- source_status: browser_desktop_adapter_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_ci_deploy_proofs: 1
- operator_reviews_required: 0
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/ci-deploy-proof-checklist.md

- ci_deploy_proof_checklist_705296b46ea4: status=ci_deploy_proof_blocked source_checklist=browser_desktop_adapter_proof_checklist_98d8fa8d01be source_status=browser_desktop_adapter_proof_blocked checklist_items=1 blocked_ci_deploy_proofs=1 operator_reviews_required=0 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/ci-deploy-proof-checklist.md

## Budget Enforcement Proof Checklist

- status: budget_enforcement_proof_blocked
- source_checklist: ci_deploy_proof_checklist_705296b46ea4
- source_status: ci_deploy_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_budget_enforcement_proofs: 1
- operator_reviews_required: 0
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/budget-enforcement-proof-checklist.md

- budget_enforcement_proof_checklist_7e6d02f1c9a7: status=budget_enforcement_proof_blocked source_checklist=ci_deploy_proof_checklist_705296b46ea4 source_status=ci_deploy_proof_blocked checklist_items=1 blocked_budget_enforcement_proofs=1 operator_reviews_required=0 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/budget-enforcement-proof-checklist.md

## Trust Promotion Proof Checklist

- status: trust_promotion_proof_blocked
- source_checklist: budget_enforcement_proof_checklist_7e6d02f1c9a7
- source_status: budget_enforcement_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_trust_promotion_proofs: 1
- operator_reviews_required: 0
- blocked_budget_enforcement_proofs: 1
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/trust-promotion-proof-checklist.md

- trust_promotion_proof_checklist_4fc7e03bcfd6: status=trust_promotion_proof_blocked source_checklist=budget_enforcement_proof_checklist_7e6d02f1c9a7 source_status=budget_enforcement_proof_blocked checklist_items=1 blocked_trust_promotion_proofs=1 operator_reviews_required=0 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/trust-promotion-proof-checklist.md

## Automatic Retry Proof Checklist

- status: automatic_retry_proof_blocked
- source_checklist: trust_promotion_proof_checklist_4fc7e03bcfd6
- source_status: trust_promotion_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_automatic_retry_proofs: 1
- operator_reviews_required: 0
- blocked_trust_promotion_proofs: 1
- blocked_budget_enforcement_proofs: 1
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/automatic-retry-proof-checklist.md

- automatic_retry_proof_checklist_d21653c04756: status=automatic_retry_proof_blocked source_checklist=trust_promotion_proof_checklist_4fc7e03bcfd6 source_status=trust_promotion_proof_blocked checklist_items=1 blocked_automatic_retry_proofs=1 operator_reviews_required=0 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/automatic-retry-proof-checklist.md

## Real Cost Tracking Proof Checklist

- status: real_cost_tracking_proof_blocked
- source_checklist: automatic_retry_proof_checklist_d21653c04756
- source_status: automatic_retry_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_real_cost_tracking_proofs: 1
- operator_reviews_required: 0
- blocked_automatic_retry_proofs: 1
- blocked_trust_promotion_proofs: 1
- blocked_budget_enforcement_proofs: 1
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/real-cost-tracking-proof-checklist.md

- real_cost_tracking_proof_checklist_7a7d3f1ce217: status=real_cost_tracking_proof_blocked source_checklist=automatic_retry_proof_checklist_d21653c04756 source_status=automatic_retry_proof_blocked checklist_items=1 blocked_real_cost_tracking_proofs=1 operator_reviews_required=0 blocked_automatic_retry_proofs=1 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/real-cost-tracking-proof-checklist.md

## Goal Completion Audit

- status: blocked_by_report_only_proofs
- requirements: 9
- satisfied_requirements: 0
- blocked_requirements: 9
- missing_evidence: 9
- approvals_required: 9
- external_decisions_required: 2
- recommended_commands: none
- report: docs/goal-completion-audit.md

- goal_completion_audit_a710217dd757: status=blocked_by_report_only_proofs requirements=9 satisfied_requirements=0 blocked_requirements=9 missing_evidence=9 approvals_required=9 external_decisions_required=2 recommended_commands=none report=docs/goal-completion-audit.md

## Expansion Decision Brief

- status: operator_decisions_required
- source_audit: goal_completion_audit_a710217dd757
- source_status: blocked_by_report_only_proofs
- requirements: 9
- blocked_requirements: 9
- external_decisions_required: 2
- approvals_required: 9
- decision_items: 11
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-brief.md

- expansion_decision_brief_811755ec3d0e: status=operator_decisions_required source_audit=goal_completion_audit_a710217dd757 source_status=blocked_by_report_only_proofs requirements=9 blocked_requirements=9 external_decisions_required=2 approvals_required=9 decision_items=11 recommended_next_step=operator_review_required report=docs/expansion-decision-brief.md

## Expansion Decision Evidence Index

- status: evidence_indexed
- source_brief: expansion_decision_brief_811755ec3d0e
- source_status: operator_decisions_required
- source_audit: goal_completion_audit_a710217dd757
- decision_items: 11
- evidence_items: 11
- external_decisions: 2
- capability_decisions: 9
- missing_evidence_links: 0
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-evidence-index.md

- expansion_decision_evidence_index_d3745cabb2c9: status=evidence_indexed source_brief=expansion_decision_brief_811755ec3d0e source_status=operator_decisions_required source_audit=goal_completion_audit_a710217dd757 decision_items=11 evidence_items=11 external_decisions=2 capability_decisions=9 missing_evidence_links=0 recommended_next_step=operator_review_required report=docs/expansion-decision-evidence-index.md

## Expansion Operator Review Checklist

- status: operator_review_required
- source_index: expansion_decision_evidence_index_d3745cabb2c9
- source_status: evidence_indexed
- source_brief: expansion_decision_brief_811755ec3d0e
- source_audit: goal_completion_audit_a710217dd757
- review_items: 11
- decision_required: 11
- external_reviews: 2
- capability_reviews: 9
- missing_evidence_links: 0
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_decision_required
- report: docs/expansion-operator-review-checklist.md

- expansion_operator_review_checklist_ed281b99faf2: status=operator_review_required source_index=expansion_decision_evidence_index_d3745cabb2c9 source_status=evidence_indexed source_brief=expansion_decision_brief_811755ec3d0e source_audit=goal_completion_audit_a710217dd757 review_items=11 decision_required=11 external_reviews=2 capability_reviews=9 missing_evidence_links=0 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-review-checklist.md

## Expansion Operator Decision Ledger

- status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_ed281b99faf2
- source_status: operator_review_required
- source_index: expansion_decision_evidence_index_d3745cabb2c9
- source_brief: expansion_decision_brief_811755ec3d0e
- source_audit: goal_completion_audit_a710217dd757
- decision_items: 11
- pending_decisions: 11
- approved_decisions: 0
- deferred_decisions: 0
- more_evidence_requested: 0
- external_decisions: 2
- capability_decisions: 9
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_decision_required
- report: docs/expansion-operator-decision-ledger.md

- expansion_operator_decision_ledger_3f19bbf99553: status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_ed281b99faf2 source_status=operator_review_required source_index=expansion_decision_evidence_index_d3745cabb2c9 source_brief=expansion_decision_brief_811755ec3d0e source_audit=goal_completion_audit_a710217dd757 decision_items=11 pending_decisions=11 approved_decisions=0 deferred_decisions=0 more_evidence_requested=0 external_decisions=2 capability_decisions=9 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-decision-ledger.md

## Expansion Operator Approval Draft

- status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_3f19bbf99553
- source_status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_ed281b99faf2
- source_index: expansion_decision_evidence_index_d3745cabb2c9
- source_brief: expansion_decision_brief_811755ec3d0e
- source_audit: goal_completion_audit_a710217dd757
- draft_items: 11
- draft_requests: 11
- created_approval_requests: 0
- external_drafts: 2
- capability_drafts: 9
- approval_boundaries: 2
- pending_decisions: 11
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_approval_flow_required
- report: docs/expansion-operator-approval-draft.md

- expansion_operator_approval_draft_4e8e020bceda: status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_3f19bbf99553 source_status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_ed281b99faf2 source_index=expansion_decision_evidence_index_d3745cabb2c9 source_brief=expansion_decision_brief_811755ec3d0e source_audit=goal_completion_audit_a710217dd757 draft_items=11 draft_requests=11 created_approval_requests=0 external_drafts=2 capability_drafts=9 approval_boundaries=2 pending_decisions=11 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_approval_flow_required report=docs/expansion-operator-approval-draft.md

## Expansion Operator Approval Request Review

- status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_4e8e020bceda
- source_status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_3f19bbf99553
- source_checklist: expansion_operator_review_checklist_ed281b99faf2
- source_index: expansion_decision_evidence_index_d3745cabb2c9
- source_brief: expansion_decision_brief_811755ec3d0e
- source_audit: goal_completion_audit_a710217dd757
- draft_requests: 11
- review_items: 11
- ready_requests: 0
- blocked_requests: 11
- schema_gaps: 11
- created_approval_requests: 0
- existing_approval_requests: 0
- external_requests: 2
- capability_requests: 9
- approval_boundaries: 2
- recommended_next_step: approval_request_schema_decision_required
- report: docs/expansion-operator-approval-request-review.md

- expansion_operator_approval_request_review_e52f9cb04b84: status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_4e8e020bceda source_status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_3f19bbf99553 source_checklist=expansion_operator_review_checklist_ed281b99faf2 source_index=expansion_decision_evidence_index_d3745cabb2c9 source_brief=expansion_decision_brief_811755ec3d0e source_audit=goal_completion_audit_a710217dd757 draft_requests=11 review_items=11 ready_requests=0 blocked_requests=11 schema_gaps=11 created_approval_requests=0 existing_approval_requests=0 external_requests=2 capability_requests=9 approval_boundaries=2 recommended_next_step=approval_request_schema_decision_required report=docs/expansion-operator-approval-request-review.md

## Expansion Operator Approval Schema Migration Selection Input Template

- status: operator_approval_schema_migration_selection_input_required
- source_packet: expansion_operator_approval_schema_migration_selection_packet_05fdef0caa17
- source_status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_c8d344afd257
- source_checklist_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_88a59ed82a34
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43cd7e7b31b7
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_28975ae3657a
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_e52f9cb04b84
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- action_count: 1
- pending_actions: 1
- actions_taken: 0
- selected_action: none
- selection_count: 1
- pending_selections: 1
- selections_recorded: 0
- approve_selections: 0
- defer_selections: 0
- more_evidence_selections: 0
- template_count: 1
- pending_inputs: 1
- inputs_recorded: 0
- required_fields_count: 4
- missing_required_inputs: 4
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_input_required
- report: docs/expansion-operator-approval-schema-migration-selection-input-template.md

- expansion_operator_approval_schema_migration_selection_input_template_2b843f505bec: status=operator_approval_schema_migration_selection_input_required source_packet=expansion_operator_approval_schema_migration_selection_packet_05fdef0caa17 source_status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_c8d344afd257 source_checklist_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081 source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_88a59ed82a34 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43cd7e7b31b7 source_plan_status=operator_approval_schema_migration_plan_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 template_count=1 pending_inputs=1 inputs_recorded=0 required_fields_count=4 missing_required_inputs=4 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_input_required report=docs/expansion-operator-approval-schema-migration-selection-input-template.md

## Playbooks

- active: 1

- first-milestone-closed-loop: active source=first_milestone_closed_loop successful_runs=162 path=playbooks/first-milestone-closed-loop.md

## Eval Candidates

- proposed: 0

- none

## Approvals

- pending: 0
- approved: 0
- rejected: 0

- none

## Stuck Tasks

- open: 0

- none

## Incidents

- open: 0
- resolved: 0

- none

## Recent Runs

- run_60c83a6cdc32: completed project=bootstrap goal=goal_f2e7179ceed3 completed=2026-06-22T11:04:57.024140+00:00 summary=runs/run_60c83a6cdc32/summary.md
- run_21b6a386585b: completed project=bootstrap goal=goal_1d62a76a0ba2 completed=2026-06-22T11:04:35.231191+00:00 summary=runs/run_21b6a386585b/summary.md
- run_64d3fd52b283: completed project=bootstrap goal=goal_a86f3b22c342 completed=2026-06-22T10:46:30.390050+00:00 summary=runs/run_64d3fd52b283/summary.md
- run_a08cb9a26ca1: completed project=bootstrap goal=goal_d3392ccb7caa completed=2026-06-22T10:36:18.946389+00:00 summary=runs/run_a08cb9a26ca1/summary.md
- run_53c46f6d9926: completed project=bootstrap goal=goal_87400e6f5df3 completed=2026-06-22T10:36:07.957997+00:00 summary=runs/run_53c46f6d9926/summary.md

## Recent Learnings

- run_60c83a6cdc32: Run run_60c83a6cdc32 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_60c83a6cdc32/learning.md)
- run_21b6a386585b: Run run_21b6a386585b showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_21b6a386585b/learning.md)
- run_64d3fd52b283: Run run_64d3fd52b283 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_64d3fd52b283/learning.md)
- run_a08cb9a26ca1: Run run_a08cb9a26ca1 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_a08cb9a26ca1/learning.md)
- run_53c46f6d9926: Run run_53c46f6d9926 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_53c46f6d9926/learning.md)

## Recent Eval Results

- first_milestone_closed_loop: pass run=run_60c83a6cdc32 created_at=2026-06-22T11:04:57.029806+00:00
- first_milestone_closed_loop: pass run=run_21b6a386585b created_at=2026-06-22T11:04:35.238227+00:00
- first_milestone_closed_loop: pass run=run_64d3fd52b283 created_at=2026-06-22T10:46:30.399370+00:00
- first_milestone_closed_loop: pass run=run_a08cb9a26ca1 created_at=2026-06-22T10:36:18.957399+00:00
- first_milestone_closed_loop: pass run=run_53c46f6d9926 created_at=2026-06-22T10:36:07.964211+00:00
