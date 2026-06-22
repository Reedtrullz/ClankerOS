# Capability Promotion Gate Checklist

- id: capability_promotion_gate_checklist_3280f4160e77
- status: promotion_blocked
- source_plan_id: capability_evidence_collection_plan_397193cdab97
- source_plan_status: evidence_required
- capability_count: 9
- gates: 9
- blocked_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report_path: docs/capability-promotion-gate-checklist.md
- created_at: 2026-06-22T15:51:20.663553+00:00

## Recommendation

- reason: Capability promotion remains blocked until manual evidence and operator approval are present.

## Promotion Gates

- hosted_dashboard: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=hosted_dashboard_design_review required_evidence=authenticated read-only deployment plan and local dashboard parity proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- remote_workers: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=remote_worker_contract_review required_evidence=claim isolation, idempotent work handoff, and worker lease recovery proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- autonomous_scheduling: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=scheduler_policy_dry_run required_evidence=operator-approved schedule policy, dry-run queue impact, and pause control proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- browser_desktop_adapters: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=adapter_permission_boundary_review required_evidence=adapter permission model, transcript capture, and no-secret logging proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- ci_deploy_proof: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=ci_deploy_evidence_contract required_evidence=CI run identifiers, deploy target contract, rollback evidence, and non-live proof labels evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- budget_enforcement: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=budget_policy_simulation required_evidence=budget source of truth, hard-stop behavior, and operator override audit proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- trust_promotion: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=trust_policy_simulation required_evidence=promotion criteria, demotion path, reviewer evidence, and routing simulation proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- automatic_retries: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=retry_policy_dry_run required_evidence=retry classification, attempt budget, replay safety, and incident linkage proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none
- real_cost_tracking: promotion_gate=blocked_until_evidence_and_operator_approval evidence_item=cost_accounting_source_review required_evidence=meter source, per-run attribution, budget reconciliation, and redaction proof evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required routing_effect=none

## Source Evidence Collection Plan

- id: capability_evidence_collection_plan_397193cdab97
- status: evidence_required
- evidence_items: 9
- manual_collection: 9
- approvals_required: 9
- report: docs/capability-evidence-collection-plan.md

## Non-Claims

- Report-only local promotion gate checklist.
- Does not create evidence collection plans as a side effect.
- Does not create approval boundary matrices as a side effect.
- Does not create proof gap indexes as a side effect.
- Does not create readiness reviews as a side effect.
- Does not create capability ledgers as a side effect.
- Does not collect evidence automatically.
- Does not approve capabilities automatically.
- Does not promote capabilities automatically.
- Does not generate proof artifacts automatically.
- Does not enable hosted dashboard.
- Does not start remote workers.
- Does not schedule autonomous work.
- Does not operate browser or desktop adapters.
- Does not run CI or deploys.
- Does not enforce budgets.
- Does not promote trust.
- Does not retry or replay work.
- Does not change routing or claims.
- Does not track real spend or mutate external systems.
