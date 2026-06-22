# Capability Expansion Ledger

- id: capability_expansion_ledger_dd8b1a681d81
- status: report_only
- capability_count: 9
- ready: 0
- deferred: 9
- approval_boundary: explicit_operator_approval_required
- report_path: docs/capability-expansion-ledger.md
- created_at: 2026-06-22T09:04:46.532274+00:00

## Capabilities

- hosted_dashboard: state=deferred next_proof=hosted_dashboard_design_review routing_effect=none approval_boundary=explicit_operator_approval_required
- remote_workers: state=deferred next_proof=remote_worker_contract_review routing_effect=none approval_boundary=explicit_operator_approval_required
- autonomous_scheduling: state=deferred next_proof=scheduler_policy_dry_run routing_effect=none approval_boundary=explicit_operator_approval_required
- browser_desktop_adapters: state=deferred next_proof=adapter_permission_boundary_review routing_effect=none approval_boundary=explicit_operator_approval_required
- ci_deploy_proof: state=deferred next_proof=ci_deploy_evidence_contract routing_effect=none approval_boundary=explicit_operator_approval_required
- budget_enforcement: state=deferred next_proof=budget_policy_simulation routing_effect=none approval_boundary=explicit_operator_approval_required
- trust_promotion: state=deferred next_proof=trust_policy_simulation routing_effect=none approval_boundary=explicit_operator_approval_required
- automatic_retries: state=deferred next_proof=retry_policy_dry_run routing_effect=none approval_boundary=explicit_operator_approval_required
- real_cost_tracking: state=deferred next_proof=cost_accounting_source_review routing_effect=none approval_boundary=explicit_operator_approval_required

## Non-Claims

- Report-only local ledger.
- Does not enable hosted dashboard.
- Does not start remote workers.
- Does not schedule autonomous work.
- Does not operate browser or desktop adapters.
- Does not run CI or deploys.
- Does not enforce budgets.
- Does not promote trust.
- Does not retry or replay work.
- Does not track real spend or mutate external systems.
