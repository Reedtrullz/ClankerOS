# Expansion Operator Approval Draft

- id: expansion_operator_approval_draft_fe0f383a53d9
- status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_7e0ffe39db96
- source_status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_7d8776aa8770
- source_index: expansion_decision_evidence_index_97c56847e44a
- source_brief: expansion_decision_brief_eee8466ecf41
- source_audit: goal_completion_audit_3c5bac20d556
- draft_items: 11
- draft_requests: 11
- created_approval_requests: 0
- external_drafts: 2
- capability_drafts: 9
- approval_boundaries: 2
- pending_decisions: 11
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_approval_flow_required
- report_path: docs/expansion-operator-approval-draft.md
- created_at: 2026-06-22T15:36:48.401788+00:00

## Draft Items

- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=external_decision approval_request_kind=external_operator_decision allowed_actions=approve,defer,request_more_evidence evidence_path=tasks.md evidence_status=blocked_task approval_boundary=explicit_operator_decision_required routing_effect=none decision=Choose external model providers and API policies before adding remote model routing.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=external_decision approval_request_kind=external_operator_decision allowed_actions=approve,defer,request_more_evidence evidence_path=tasks.md evidence_status=blocked_task approval_boundary=explicit_operator_decision_required routing_effect=none decision=Choose deployment target before hosted dashboard work.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=hosted_dashboard approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/hosted-dashboard-proof-checklist.md evidence_id=hosted_dashboard_proof_checklist_3df5a6ec11d0 evidence_status=hosted_dashboard_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer hosted_dashboard after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=remote_workers approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/remote-worker-proof-checklist.md evidence_id=remote_worker_proof_checklist_9ff474ff4e27 evidence_status=remote_worker_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer remote_workers after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=autonomous_scheduling approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/autonomous-scheduling-proof-checklist.md evidence_id=autonomous_scheduling_proof_checklist_50ba273fcf80 evidence_status=autonomous_scheduling_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer autonomous_scheduling after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=browser_desktop_adapters approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/browser-desktop-adapter-proof-checklist.md evidence_id=browser_desktop_adapter_proof_checklist_63296afcf8e3 evidence_status=browser_desktop_adapter_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer browser_desktop_adapters after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=ci_deploy_proof approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/ci-deploy-proof-checklist.md evidence_id=ci_deploy_proof_checklist_92ca1f42986c evidence_status=ci_deploy_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer ci_deploy_proof after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=budget_enforcement approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/budget-enforcement-proof-checklist.md evidence_id=budget_enforcement_proof_checklist_dc10963e5136 evidence_status=budget_enforcement_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer budget_enforcement after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=trust_promotion approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/trust-promotion-proof-checklist.md evidence_id=trust_promotion_proof_checklist_dc82e6bb7043 evidence_status=trust_promotion_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer trust_promotion after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=automatic_retries approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/automatic-retry-proof-checklist.md evidence_id=automatic_retry_proof_checklist_f7a09afd3176 evidence_status=automatic_retry_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer automatic_retries after evidence and policy review.
- draft_state=draft_only approval_request_status=not_created selected_action=pending review_type=capability_approval requirement=real_cost_tracking approval_request_kind=capability_operator_approval allowed_actions=approve,defer,request_more_evidence evidence_path=docs/real-cost-tracking-proof-checklist.md evidence_id=real_cost_tracking_proof_checklist_adbaffc3a981 evidence_status=real_cost_tracking_proof_blocked approval_boundary=explicit_operator_approval_required routing_effect=none decision=Approve or defer real_cost_tracking after evidence and policy review.

## Non-Claims

- Report-only local expansion operator approval draft.
- Does not create approval_requests rows.
- Does not take allowed actions.
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
