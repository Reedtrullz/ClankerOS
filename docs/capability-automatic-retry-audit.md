# Capability Automatic Retry Audit

- id: capability_automatic_retry_audit_cf1259c79b5c
- status: automatic_retry_blocked
- source_audit_id: capability_trust_promotion_audit_e402af3a4b71
- source_audit_status: trust_promotion_blocked
- capability_count: 9
- audits: 9
- blocked_retries: 9
- operator_reviews_required: 0
- blocked_trust_promotions: 9
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report_path: docs/capability-automatic-retry-audit.md
- created_at: 2026-06-22T13:57:43.744877+00:00

## Recommendation

- reason: Automatic retry remains blocked until trust promotion, required evidence, and operator approvals are present.

## Automatic Retry Audit

- hosted_dashboard: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- remote_workers: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- autonomous_scheduling: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- browser_desktop_adapters: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- ci_deploy_proof: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- budget_enforcement: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- trust_promotion: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- automatic_retries: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none
- real_cost_tracking: recommended_retry_action=keep_retry_disabled retry_state=blocked_until_trust_promotion_and_operator_approval source_trust_action=keep_trust_unpromoted source_trust_state=blocked_until_promotion_decision_and_operator_approval evidence_state=missing approval_state=approval_required approval_boundary=explicit_operator_approval_required retry_effect=none routing_effect=none

## Source Trust Promotion Audit

- id: capability_trust_promotion_audit_e402af3a4b71
- status: trust_promotion_blocked
- audits: 9
- blocked_trust_promotions: 9
- operator_reviews_required: 0
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- report: docs/capability-trust-promotion-audit.md

## Non-Claims

- Report-only local automatic retry audit.
- Does not create trust promotion audits as a side effect.
- Does not create promotion decision ledgers as a side effect.
- Does not create promotion gate checklists as a side effect.
- Does not create evidence collection plans as a side effect.
- Does not create approval boundary matrices as a side effect.
- Does not create proof gap indexes as a side effect.
- Does not create readiness reviews as a side effect.
- Does not create capability ledgers as a side effect.
- Does not collect evidence automatically.
- Does not approve capabilities automatically.
- Does not promote capabilities automatically.
- Does not promote trust automatically.
- Does not retry or replay work automatically.
- Does not generate proof artifacts automatically.
- Does not enable hosted dashboard.
- Does not start remote workers.
- Does not schedule autonomous work.
- Does not operate browser or desktop adapters.
- Does not run CI or deploys.
- Does not enforce budgets.
- Does not change routing or claims.
- Does not track real spend or mutate external systems.
