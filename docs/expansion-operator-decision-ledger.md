# Expansion Operator Decision Ledger

- id: expansion_operator_decision_ledger_3f19bbf99553
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
- report_path: docs/expansion-operator-decision-ledger.md
- created_at: 2026-06-22T09:04:48.824810+00:00

## Decision Items

- decision_state=pending_operator_decision selected_action=pending review_type=external_decision allowed_actions=approve,defer,request_more_evidence evidence_path=tasks.md evidence_status=blocked_task approval_boundary=explicit_operator_decision_required routing_effect=none decision=Choose external model providers and API policies before adding remote model routing.
- decision_state=pending_operator_decision selected_action=pending review_type=external_decision allowed_actions=approve,defer,request_more_evidence evidence_path=tasks.md evidence_status=blocked_task approval_boundary=explicit_operator_decision_required routing_effect=none decision=Choose deployment target before hosted dashboard work.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=hosted_dashboard allowed_actions=approve,defer,request_more_evidence evidence_path=docs/hosted-dashboard-proof-checklist.md evidence_id=hosted_dashboard_proof_checklist_620a518a9498 evidence_status=hosted_dashboard_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer hosted_dashboard after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=remote_workers allowed_actions=approve,defer,request_more_evidence evidence_path=docs/remote-worker-proof-checklist.md evidence_id=remote_worker_proof_checklist_2efdc0b8a79f evidence_status=remote_worker_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer remote_workers after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=autonomous_scheduling allowed_actions=approve,defer,request_more_evidence evidence_path=docs/autonomous-scheduling-proof-checklist.md evidence_id=autonomous_scheduling_proof_checklist_be630dc43dbc evidence_status=autonomous_scheduling_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer autonomous_scheduling after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=browser_desktop_adapters allowed_actions=approve,defer,request_more_evidence evidence_path=docs/browser-desktop-adapter-proof-checklist.md evidence_id=browser_desktop_adapter_proof_checklist_98d8fa8d01be evidence_status=browser_desktop_adapter_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer browser_desktop_adapters after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=ci_deploy_proof allowed_actions=approve,defer,request_more_evidence evidence_path=docs/ci-deploy-proof-checklist.md evidence_id=ci_deploy_proof_checklist_705296b46ea4 evidence_status=ci_deploy_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer ci_deploy_proof after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=budget_enforcement allowed_actions=approve,defer,request_more_evidence evidence_path=docs/budget-enforcement-proof-checklist.md evidence_id=budget_enforcement_proof_checklist_7e6d02f1c9a7 evidence_status=budget_enforcement_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer budget_enforcement after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=trust_promotion allowed_actions=approve,defer,request_more_evidence evidence_path=docs/trust-promotion-proof-checklist.md evidence_id=trust_promotion_proof_checklist_4fc7e03bcfd6 evidence_status=trust_promotion_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer trust_promotion after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=automatic_retries allowed_actions=approve,defer,request_more_evidence evidence_path=docs/automatic-retry-proof-checklist.md evidence_id=automatic_retry_proof_checklist_d21653c04756 evidence_status=automatic_retry_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer automatic_retries after evidence and policy review.
- decision_state=pending_operator_decision selected_action=pending review_type=capability_approval requirement=real_cost_tracking allowed_actions=approve,defer,request_more_evidence evidence_path=docs/real-cost-tracking-proof-checklist.md evidence_id=real_cost_tracking_proof_checklist_7a7d3f1ce217 evidence_status=real_cost_tracking_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer real_cost_tracking after evidence and policy review.

## Non-Claims

- Report-only local expansion operator decision ledger.
- Does not approve decisions.
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
