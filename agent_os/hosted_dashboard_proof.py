from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    AutomaticRetryProofChecklist,
    AutonomousSchedulingProofChecklist,
    BudgetEnforcementProofChecklist,
    BrowserDesktopAdapterProofChecklist,
    CapabilityRealCostTrackingAudit,
    CiDeployProofChecklist,
    HostedDashboardProofChecklist,
    RealCostTrackingProofChecklist,
    RemoteWorkerProofChecklist,
    Storage,
    TrustPromotionProofChecklist,
)


REAL_COST_TRACKING_PROOF_CHECKLIST_MISSING = (
    "real_cost_tracking_proof_checklist_missing"
)
REAL_COST_TRACKING_AUDIT_MISSING = "real_cost_tracking_audit_missing"
HOSTED_DASHBOARD_PROOF_BLOCKED = "hosted_dashboard_proof_blocked"
OPERATOR_HOSTED_DASHBOARD_REVIEW_REQUIRED = (
    "operator_hosted_dashboard_review_required"
)
NO_HOSTED_DASHBOARD_PROOF_CANDIDATE = "no_hosted_dashboard_proof_candidate"
KEEP_HOSTED_DASHBOARD_DISABLED = "keep_hosted_dashboard_disabled"
MANUAL_HOSTED_DASHBOARD_REVIEW_REQUIRED = "manual_hosted_dashboard_review_required"
KEEP_COST_TRACKING_DISABLED = "keep_cost_tracking_disabled"
REAL_COST_TRACKING_AUDIT_SOURCE = "real_cost_tracking_audit"
REAL_COST_TRACKING_PROOF_CHECKLIST_SOURCE = "real_cost_tracking_proof_checklist"
DASHBOARD_BLOCKED = "blocked_until_cost_tracking_and_operator_approval"
DASHBOARD_BLOCKED_BY_PROOF = (
    "blocked_until_real_cost_tracking_proof_and_operator_approval"
)
DASHBOARD_REVIEW_READY = "ready_for_operator_hosted_dashboard_review"
HOSTED_DASHBOARD = "hosted_dashboard"
HOSTED_DASHBOARD_PROOF_ITEM = "hosted_dashboard_design_review"
NO_EFFECT = "none"
REPORT_PATH = "docs/hosted-dashboard-proof-checklist.md"


def write_hosted_dashboard_proof_checklist(
    root: Path,
) -> tuple[Path, HostedDashboardProofChecklist]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    real_cost_tracking_proof_checklists = storage.list_recent_real_cost_tracking_proof_checklists(
        limit=None,
    )
    source_audit: CapabilityRealCostTrackingAudit | None = None
    source_checklist: RealCostTrackingProofChecklist | None = None
    source_automatic_retry_checklist: AutomaticRetryProofChecklist | None = None
    source_trust_checklist: TrustPromotionProofChecklist | None = None
    source_budget_checklist: BudgetEnforcementProofChecklist | None = None
    source_ci_deploy_checklist: CiDeployProofChecklist | None = None
    source_browser_desktop_adapter_checklist: BrowserDesktopAdapterProofChecklist | None = None
    source_autonomous_scheduling_checklist: AutonomousSchedulingProofChecklist | None = None
    source_remote_worker_checklist: RemoteWorkerProofChecklist | None = None
    source_hosted_dashboard_checklist: HostedDashboardProofChecklist | None = None
    source_real_cost_tracking_checklist: RealCostTrackingProofChecklist | None = None
    if real_cost_tracking_proof_checklists:
        (
            source_checklist,
            source_automatic_retry_checklist,
            source_trust_checklist,
            source_budget_checklist,
            source_ci_deploy_checklist,
            source_browser_desktop_adapter_checklist,
            source_autonomous_scheduling_checklist,
            source_remote_worker_checklist,
            source_hosted_dashboard_checklist,
            source_real_cost_tracking_checklist,
        ) = _latest_real_cost_sourced_real_cost_tracking_proof(
            storage=storage,
            real_cost_tracking_checklists=real_cost_tracking_proof_checklists,
        )
        if source_checklist is None:
            fallback_checklist = real_cost_tracking_proof_checklists[0]
            (
                source_automatic_retry_checklist,
                source_trust_checklist,
                source_budget_checklist,
                source_ci_deploy_checklist,
                source_browser_desktop_adapter_checklist,
                source_autonomous_scheduling_checklist,
                source_remote_worker_checklist,
                source_hosted_dashboard_checklist,
                source_real_cost_tracking_checklist,
            ) = _source_chain_from_real_cost_tracking_proof(
                storage=storage,
                source_checklist=fallback_checklist,
            )
            if source_automatic_retry_checklist is not None:
                source_checklist = fallback_checklist
        checklist = _checklist_from_latest_real_cost_tracking_proof(
            storage=storage,
            source_checklist=source_checklist,
            report_path=REPORT_PATH,
        )
    else:
        cost_audits = storage.list_recent_capability_real_cost_tracking_audits(
            limit=1
        )
        source_audit = cost_audits[0] if cost_audits else None
        if source_audit is not None:
            checklist = _checklist_from_latest_cost_audit(
                storage=storage,
                source_audit=source_audit,
                report_path=REPORT_PATH,
            )
        else:
            checklist = _checklist_from_latest_real_cost_tracking_proof(
                storage=storage,
                source_checklist=None,
                report_path=REPORT_PATH,
            )
    report_path = root / checklist.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_hosted_dashboard_proof_checklist_report(
            checklist,
            source_audit=source_audit,
            source_checklist=source_checklist,
            source_automatic_retry_checklist=source_automatic_retry_checklist,
            source_trust_checklist=source_trust_checklist,
            source_budget_checklist=source_budget_checklist,
            source_ci_deploy_checklist=source_ci_deploy_checklist,
            source_browser_desktop_adapter_checklist=source_browser_desktop_adapter_checklist,
            source_autonomous_scheduling_checklist=source_autonomous_scheduling_checklist,
            source_remote_worker_checklist=source_remote_worker_checklist,
            source_hosted_dashboard_checklist=source_hosted_dashboard_checklist,
            source_real_cost_tracking_checklist=source_real_cost_tracking_checklist,
        ),
        encoding="utf-8",
    )
    return report_path, checklist


def render_hosted_dashboard_proof_checklist_report(
    checklist: HostedDashboardProofChecklist,
    source_audit: CapabilityRealCostTrackingAudit | None = None,
    source_checklist: RealCostTrackingProofChecklist | None = None,
    source_automatic_retry_checklist: AutomaticRetryProofChecklist | None = None,
    source_trust_checklist: TrustPromotionProofChecklist | None = None,
    source_budget_checklist: BudgetEnforcementProofChecklist | None = None,
    source_ci_deploy_checklist: CiDeployProofChecklist | None = None,
    source_browser_desktop_adapter_checklist: BrowserDesktopAdapterProofChecklist
    | None = None,
    source_autonomous_scheduling_checklist: AutonomousSchedulingProofChecklist
    | None = None,
    source_remote_worker_checklist: RemoteWorkerProofChecklist | None = None,
    source_hosted_dashboard_checklist: HostedDashboardProofChecklist | None = None,
    source_real_cost_tracking_checklist: RealCostTrackingProofChecklist | None = None,
) -> str:
    lines = [
        "# Hosted Dashboard Proof Checklist",
        "",
        f"- id: {checklist.id}",
        f"- status: {checklist.status}",
        f"- source_kind: {checklist.source_kind}",
        f"- source_checklist_id: {checklist.source_checklist_id or 'none'}",
        f"- source_checklist_status: {checklist.source_checklist_status}",
        f"- source_audit_id: {checklist.source_audit_id or 'none'}",
        f"- source_audit_status: {checklist.source_audit_status}",
        f"- capability_count: {checklist.capability_count}",
        f"- checklist_items: {checklist.checklist_count}",
        f"- blocked_dashboard_proofs: {checklist.blocked_dashboard_proof_count}",
        f"- operator_reviews_required: {checklist.operator_review_required_count}",
        f"- blocked_cost_tracking: {checklist.blocked_cost_tracking_count}",
        f"- blocked_retries: {checklist.blocked_retry_count}",
        f"- blocked_trust_promotions: {checklist.blocked_trust_promotion_count}",
        f"- missing_evidence: {checklist.missing_evidence_count}",
        f"- approvals_required: {checklist.approval_required_count}",
        f"- boundaries: {checklist.boundary_count}",
        f"- recommended_commands: {format_recommended_commands(checklist.recommended_commands)}",
        f"- report_path: {checklist.report_path}",
        f"- created_at: {checklist.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {checklist.reason}",
        "",
        "## Hosted Dashboard Proof Items",
        "",
    ]
    if checklist.checklist_items:
        lines.extend(render_checklist_item_line(item) for item in checklist.checklist_items)
    else:
        lines.append("- none")

    if checklist.source_kind == REAL_COST_TRACKING_PROOF_CHECKLIST_SOURCE:
        lines.extend(["", "## Source Real Cost Tracking Proof Checklist", ""])
        if source_checklist is None:
            lines.append("- none")
        else:
            lines.extend(
                [
                    f"- id: {source_checklist.id}",
                    f"- status: {source_checklist.status}",
                    f"- source_checklist_source_checklist_id: {source_checklist.source_checklist_id or 'none'}",
                    f"- source_checklist_source_checklist_status: {source_checklist.source_checklist_status}",
                    f"- checklist_items: {source_checklist.checklist_count}",
                    f"- blocked_real_cost_tracking_proofs: {source_checklist.blocked_real_cost_tracking_proof_count}",
                    f"- operator_reviews_required: {source_checklist.operator_review_required_count}",
                    f"- blocked_automatic_retry_proofs: {source_checklist.blocked_automatic_retry_proof_count}",
                    f"- blocked_trust_promotion_proofs: {source_checklist.blocked_trust_promotion_proof_count}",
                    f"- blocked_budget_enforcement_proofs: {source_checklist.blocked_budget_enforcement_proof_count}",
                    f"- blocked_ci_deploy_proofs: {source_checklist.blocked_ci_deploy_proof_count}",
                    f"- blocked_adapter_proofs: {source_checklist.blocked_adapter_proof_count}",
                    f"- blocked_scheduling_proofs: {source_checklist.blocked_scheduling_proof_count}",
                    f"- blocked_worker_proofs: {source_checklist.blocked_worker_proof_count}",
                    f"- blocked_dashboard_proofs: {source_checklist.blocked_dashboard_proof_count}",
                    f"- blocked_cost_tracking: {source_checklist.blocked_cost_tracking_count}",
                    f"- blocked_retries: {source_checklist.blocked_retry_count}",
                    f"- blocked_trust_promotions: {source_checklist.blocked_trust_promotion_count}",
                    f"- missing_evidence: {source_checklist.missing_evidence_count}",
                    f"- approvals_required: {source_checklist.approval_required_count}",
                    f"- report: {source_checklist.report_path}",
                ]
            )
            if source_automatic_retry_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_id: "
                        f"{source_automatic_retry_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_status: "
                        f"{source_automatic_retry_checklist.source_checklist_status}",
                    ]
                )
            if source_trust_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_trust_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_trust_checklist.source_checklist_status}",
                    ]
                )
            if source_budget_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_budget_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_budget_checklist.source_checklist_status}",
                    ]
                )
            if source_ci_deploy_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_ci_deploy_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_ci_deploy_checklist.source_checklist_status}",
                    ]
                )
            if source_browser_desktop_adapter_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_browser_desktop_adapter_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_browser_desktop_adapter_checklist.source_checklist_status}",
                    ]
                )
            if source_autonomous_scheduling_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_autonomous_scheduling_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_autonomous_scheduling_checklist.source_checklist_status}",
                    ]
                )
            if source_remote_worker_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_remote_worker_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_remote_worker_checklist.source_checklist_status}",
                    ]
                )
            if source_hosted_dashboard_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_hosted_dashboard_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_hosted_dashboard_checklist.source_checklist_status}",
                    ]
                )
            if source_real_cost_tracking_checklist is not None:
                lines.extend(
                    [
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                        f"{source_real_cost_tracking_checklist.source_checklist_id or 'none'}",
                        "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                        f"{source_real_cost_tracking_checklist.source_checklist_status}",
                    ]
                )
    else:
        lines.extend(["", "## Source Real Cost Tracking Audit", ""])
        if source_audit is None:
            lines.append("- none")
        else:
            lines.extend(
                [
                    f"- id: {source_audit.id}",
                    f"- status: {source_audit.status}",
                    f"- audits: {source_audit.audit_count}",
                    f"- blocked_cost_tracking: {source_audit.blocked_cost_tracking_count}",
                    f"- operator_reviews_required: {source_audit.operator_review_required_count}",
                    f"- blocked_retries: {source_audit.blocked_retry_count}",
                    f"- blocked_trust_promotions: {source_audit.blocked_trust_promotion_count}",
                    f"- missing_evidence: {source_audit.missing_evidence_count}",
                    f"- approvals_required: {source_audit.approval_required_count}",
                    f"- report: {source_audit.report_path}",
                ]
            )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local hosted dashboard proof checklist.",
            "- Does not create Real Cost Tracking proof checklists as a side effect.",
            "- Does not create real cost tracking audits as a side effect.",
            "- Does not create automatic retry audits as a side effect.",
            "- Does not create trust promotion audits as a side effect.",
            "- Does not create promotion decision ledgers as a side effect.",
            "- Does not create promotion gate checklists as a side effect.",
            "- Does not create evidence collection plans as a side effect.",
            "- Does not create approval boundary matrices as a side effect.",
            "- Does not create proof gap indexes as a side effect.",
            "- Does not create readiness reviews as a side effect.",
            "- Does not create capability ledgers as a side effect.",
            "- Does not collect evidence automatically.",
            "- Does not approve capabilities automatically.",
            "- Does not promote capabilities automatically.",
            "- Does not promote trust automatically.",
            "- Does not retry or replay work automatically.",
            "- Does not track real spend automatically.",
            "- Does not generate proof artifacts automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not deploy hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not change routing or claims.",
            "- Does not mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_hosted_dashboard_proof_checklist_line(
    checklist: HostedDashboardProofChecklist,
) -> str:
    source_status = (
        checklist.source_checklist_status
        if checklist.source_kind == REAL_COST_TRACKING_PROOF_CHECKLIST_SOURCE
        else checklist.source_audit_status
    )
    return (
        f"- {checklist.id}: status={checklist.status} "
        f"source_kind={checklist.source_kind} "
        f"source_checklist={checklist.source_checklist_id or 'none'} "
        f"source_audit={checklist.source_audit_id or 'none'} "
        f"source_status={source_status} "
        f"checklist_items={checklist.checklist_count} "
        f"blocked_dashboard_proofs={checklist.blocked_dashboard_proof_count} "
        f"operator_reviews_required={checklist.operator_review_required_count} "
        f"blocked_cost_tracking={checklist.blocked_cost_tracking_count} "
        f"blocked_retries={checklist.blocked_retry_count} "
        f"blocked_trust_promotions={checklist.blocked_trust_promotion_count} "
        f"missing_evidence={checklist.missing_evidence_count} "
        f"approvals_required={checklist.approval_required_count} "
        f"boundaries={checklist.boundary_count} "
        f"recommended_commands={format_recommended_commands(checklist.recommended_commands)} "
        f"report={checklist.report_path}"
    )


def render_checklist_item_line(item: dict[str, str]) -> str:
    parts = [
        f"- {item['capability']}: proof_item={item['proof_item']}",
        f"recommended_dashboard_action={item['recommended_dashboard_action']} "
        f"dashboard_state={item['dashboard_state']}",
    ]
    optional_proof_keys = (
        "source_real_cost_tracking_proof_action",
        "source_real_cost_tracking_proof_state",
        "source_automatic_retry_proof_action",
        "source_automatic_retry_proof_state",
        "source_trust_proof_action",
        "source_trust_proof_state",
        "source_budget_action",
        "source_budget_state",
        "source_ci_deploy_action",
        "source_ci_deploy_state",
        "source_adapter_action",
        "source_adapter_state",
        "source_scheduling_action",
        "source_scheduling_state",
        "source_worker_action",
        "source_worker_state",
        "source_dashboard_action",
        "source_dashboard_state",
    )
    if all(key in item for key in optional_proof_keys):
        parts.extend(
            [
                "source_real_cost_tracking_proof_action="
                f"{item['source_real_cost_tracking_proof_action']}",
                "source_real_cost_tracking_proof_state="
                f"{item['source_real_cost_tracking_proof_state']}",
                "source_automatic_retry_proof_action="
                f"{item['source_automatic_retry_proof_action']}",
                "source_automatic_retry_proof_state="
                f"{item['source_automatic_retry_proof_state']}",
                f"source_trust_proof_action={item['source_trust_proof_action']}",
                f"source_trust_proof_state={item['source_trust_proof_state']}",
                f"source_budget_action={item['source_budget_action']}",
                f"source_budget_state={item['source_budget_state']}",
                f"source_ci_deploy_action={item['source_ci_deploy_action']}",
                f"source_ci_deploy_state={item['source_ci_deploy_state']}",
                f"source_adapter_action={item['source_adapter_action']}",
                f"source_adapter_state={item['source_adapter_state']}",
                f"source_scheduling_action={item['source_scheduling_action']}",
                f"source_scheduling_state={item['source_scheduling_state']}",
                f"source_worker_action={item['source_worker_action']}",
                f"source_worker_state={item['source_worker_state']}",
                f"source_dashboard_action={item['source_dashboard_action']}",
                f"source_dashboard_state={item['source_dashboard_state']}",
            ]
        )
    parts.extend(
        [
            f"source_cost_action={item['source_cost_action']}",
            f"cost_tracking_state={item['cost_tracking_state']}",
            f"source_retry_action={item['source_retry_action']}",
            f"source_retry_state={item['source_retry_state']}",
            f"source_trust_action={item['source_trust_action']}",
            f"source_trust_state={item['source_trust_state']}",
            f"evidence_state={item['evidence_state']}",
            f"approval_state={item['approval_state']}",
            f"approval_boundary={item['approval_boundary']}",
            f"dashboard_effect={item['dashboard_effect']}",
            f"routing_effect={item['routing_effect']}",
        ]
    )
    return " ".join(parts)


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _latest_real_cost_sourced_real_cost_tracking_proof(
    *,
    storage: Storage,
    real_cost_tracking_checklists: list[RealCostTrackingProofChecklist],
) -> tuple[
    RealCostTrackingProofChecklist | None,
    AutomaticRetryProofChecklist | None,
    TrustPromotionProofChecklist | None,
    BudgetEnforcementProofChecklist | None,
    CiDeployProofChecklist | None,
    BrowserDesktopAdapterProofChecklist | None,
    AutonomousSchedulingProofChecklist | None,
    RemoteWorkerProofChecklist | None,
    HostedDashboardProofChecklist | None,
    RealCostTrackingProofChecklist | None,
]:
    for real_cost_tracking_checklist in real_cost_tracking_checklists:
        (
            automatic_retry_checklist,
            trust_checklist,
            budget_checklist,
            ci_deploy_checklist,
            browser_desktop_adapter_checklist,
            autonomous_scheduling_checklist,
            remote_worker_checklist,
            hosted_dashboard_checklist,
            source_real_cost_tracking_checklist,
        ) = _source_chain_from_real_cost_tracking_proof(
            storage=storage,
            source_checklist=real_cost_tracking_checklist,
        )
        if (
            automatic_retry_checklist is None
            or trust_checklist is None
            or budget_checklist is None
            or ci_deploy_checklist is None
            or browser_desktop_adapter_checklist is None
            or autonomous_scheduling_checklist is None
            or remote_worker_checklist is None
            or hosted_dashboard_checklist is None
            or source_real_cost_tracking_checklist is None
        ):
            continue
        return (
            real_cost_tracking_checklist,
            automatic_retry_checklist,
            trust_checklist,
            budget_checklist,
            ci_deploy_checklist,
            browser_desktop_adapter_checklist,
            autonomous_scheduling_checklist,
            remote_worker_checklist,
            hosted_dashboard_checklist,
            source_real_cost_tracking_checklist,
        )
    return None, None, None, None, None, None, None, None, None, None


def _source_chain_from_real_cost_tracking_proof(
    *,
    storage: Storage,
    source_checklist: RealCostTrackingProofChecklist | None,
) -> tuple[
    AutomaticRetryProofChecklist | None,
    TrustPromotionProofChecklist | None,
    BudgetEnforcementProofChecklist | None,
    CiDeployProofChecklist | None,
    BrowserDesktopAdapterProofChecklist | None,
    AutonomousSchedulingProofChecklist | None,
    RemoteWorkerProofChecklist | None,
    HostedDashboardProofChecklist | None,
    RealCostTrackingProofChecklist | None,
]:
    if source_checklist is None:
        return None, None, None, None, None, None, None, None, None
    automatic_retry_checklist = storage.get_automatic_retry_proof_checklist(
        source_checklist.source_checklist_id
    )
    trust_checklist = (
        storage.get_trust_promotion_proof_checklist(
            automatic_retry_checklist.source_checklist_id
        )
        if automatic_retry_checklist is not None
        else None
    )
    budget_checklist = (
        storage.get_budget_enforcement_proof_checklist(
            trust_checklist.source_checklist_id
        )
        if trust_checklist is not None
        else None
    )
    ci_deploy_checklist = (
        storage.get_ci_deploy_proof_checklist(
            budget_checklist.source_checklist_id
        )
        if budget_checklist is not None
        else None
    )
    browser_desktop_adapter_checklist = (
        storage.get_browser_desktop_adapter_proof_checklist(
            ci_deploy_checklist.source_checklist_id
        )
        if ci_deploy_checklist is not None
        else None
    )
    autonomous_scheduling_checklist = (
        storage.get_autonomous_scheduling_proof_checklist(
            browser_desktop_adapter_checklist.source_checklist_id
        )
        if browser_desktop_adapter_checklist is not None
        else None
    )
    remote_worker_checklist = (
        storage.get_remote_worker_proof_checklist(
            autonomous_scheduling_checklist.source_checklist_id
        )
        if autonomous_scheduling_checklist is not None
        else None
    )
    hosted_dashboard_checklist = (
        storage.get_hosted_dashboard_proof_checklist(
            remote_worker_checklist.source_checklist_id
        )
        if remote_worker_checklist is not None
        else None
    )
    source_real_cost_tracking_checklist = (
        storage.get_real_cost_tracking_proof_checklist(
            hosted_dashboard_checklist.source_checklist_id
        )
        if hosted_dashboard_checklist is not None
        and hosted_dashboard_checklist.source_kind
        == REAL_COST_TRACKING_PROOF_CHECKLIST_SOURCE
        else None
    )
    return (
        automatic_retry_checklist,
        trust_checklist,
        budget_checklist,
        ci_deploy_checklist,
        browser_desktop_adapter_checklist,
        autonomous_scheduling_checklist,
        remote_worker_checklist,
        hosted_dashboard_checklist,
        source_real_cost_tracking_checklist,
    )


def _checklist_from_latest_real_cost_tracking_proof(
    *,
    storage: Storage,
    source_checklist: RealCostTrackingProofChecklist | None,
    report_path: str,
) -> HostedDashboardProofChecklist:
    if source_checklist is None:
        return storage.record_hosted_dashboard_proof_checklist(
            status=REAL_COST_TRACKING_PROOF_CHECKLIST_MISSING,
            source_audit_id=None,
            source_audit_status="none",
            source_kind=REAL_COST_TRACKING_PROOF_CHECKLIST_SOURCE,
            source_checklist_id=None,
            source_checklist_status="none",
            capability_count=0,
            checklist_count=0,
            blocked_dashboard_proof_count=0,
            operator_review_required_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["real-cost-tracking-proof-checklist"],
            reason="No Real Cost Tracking proof checklist exists yet.",
            checklist_items=[],
            report_path=report_path,
        )

    if (
        source_checklist.status != "operator_real_cost_tracking_review_required"
        and not source_checklist.checklist_items
        and source_checklist.recommended_commands
    ):
        return storage.record_hosted_dashboard_proof_checklist(
            status=REAL_COST_TRACKING_PROOF_CHECKLIST_MISSING,
            source_audit_id=None,
            source_audit_status="none",
            source_kind=REAL_COST_TRACKING_PROOF_CHECKLIST_SOURCE,
            source_checklist_id=source_checklist.id,
            source_checklist_status=source_checklist.status,
            capability_count=0,
            checklist_count=0,
            blocked_dashboard_proof_count=0,
            operator_review_required_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=source_checklist.recommended_commands,
            reason=(
                "Latest Real Cost Tracking proof checklist is incomplete; run "
                "the recommended upstream command before checking hosted dashboard proof."
            ),
            checklist_items=[],
            report_path=report_path,
        )

    source_item = _real_cost_tracking_proof_source_item(source_checklist)
    checklist_items = (
        [_checklist_item_from_real_cost_tracking_proof_item(source_item)]
        if source_item is not None
        else []
    )
    blocked_dashboard_proof_count = sum(
        1
        for item in checklist_items
        if item["recommended_dashboard_action"] == KEEP_HOSTED_DASHBOARD_DISABLED
    )
    operator_review_required_count = sum(
        1
        for item in checklist_items
        if item["recommended_dashboard_action"]
        == MANUAL_HOSTED_DASHBOARD_REVIEW_REQUIRED
    )
    if blocked_dashboard_proof_count:
        status = HOSTED_DASHBOARD_PROOF_BLOCKED
        reason = (
            "Hosted dashboard proof remains blocked until Real Cost Tracking "
            "proof, Automatic Retry proof, Trust Promotion proof, Budget "
            "Enforcement proof, CI Deploy proof, browser/desktop adapter "
            "proof, autonomous scheduling proof, remote worker proof, "
            "cost tracking, retry review, required evidence, and operator "
            "approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_HOSTED_DASHBOARD_REVIEW_REQUIRED
        reason = (
            "Hosted dashboard proof is ready for manual operator review; no "
            "dashboard, deployment, routing, scheduler, adapter, CI, budget, "
            "retry, trust, or cost state changes were applied."
        )
    else:
        status = NO_HOSTED_DASHBOARD_PROOF_CANDIDATE
        reason = (
            "No hosted dashboard proof checklist row was needed from the "
            "latest Real Cost Tracking proof checklist."
        )

    return storage.record_hosted_dashboard_proof_checklist(
        status=status,
        source_audit_id=None,
        source_audit_status="none",
        source_kind=REAL_COST_TRACKING_PROOF_CHECKLIST_SOURCE,
        source_checklist_id=source_checklist.id,
        source_checklist_status=source_checklist.status,
        capability_count=len(checklist_items),
        checklist_count=len(checklist_items),
        blocked_dashboard_proof_count=blocked_dashboard_proof_count,
        operator_review_required_count=operator_review_required_count,
        blocked_cost_tracking_count=sum(
            1
            for item in checklist_items
            if item["source_cost_action"] == KEEP_COST_TRACKING_DISABLED
        ),
        blocked_retry_count=sum(
            1
            for item in checklist_items
            if item["source_retry_action"] == "keep_retry_disabled"
        ),
        blocked_trust_promotion_count=sum(
            1
            for item in checklist_items
            if item["source_trust_action"] == "keep_trust_unpromoted"
        ),
        missing_evidence_count=sum(
            1 for item in checklist_items if item["evidence_state"] == "missing"
        ),
        approval_required_count=sum(
            1
            for item in checklist_items
            if item["approval_state"] == "approval_required"
        ),
        boundary_count=len(
            {
                item["approval_boundary"]
                for item in checklist_items
                if item["approval_boundary"] != "none"
            }
        ),
        recommended_commands=[],
        reason=reason,
        checklist_items=checklist_items,
        report_path=report_path,
    )


def _checklist_from_latest_cost_audit(
    *,
    storage: Storage,
    source_audit: CapabilityRealCostTrackingAudit | None,
    report_path: str,
) -> HostedDashboardProofChecklist:
    if source_audit is None:
        return storage.record_hosted_dashboard_proof_checklist(
            status=REAL_COST_TRACKING_AUDIT_MISSING,
            source_audit_id=None,
            source_audit_status="none",
            source_kind=REAL_COST_TRACKING_AUDIT_SOURCE,
            capability_count=0,
            checklist_count=0,
            blocked_dashboard_proof_count=0,
            operator_review_required_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["capability-real-cost-tracking-audit"],
            reason="No capability real cost tracking audit exists yet.",
            checklist_items=[],
            report_path=report_path,
        )

    if (
        source_audit.status != "operator_cost_review_required"
        and not source_audit.audit_items
        and source_audit.recommended_commands
    ):
        return storage.record_hosted_dashboard_proof_checklist(
            status=REAL_COST_TRACKING_AUDIT_MISSING,
            source_audit_id=source_audit.id,
            source_audit_status=source_audit.status,
            source_kind=REAL_COST_TRACKING_AUDIT_SOURCE,
            capability_count=0,
            checklist_count=0,
            blocked_dashboard_proof_count=0,
            operator_review_required_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=source_audit.recommended_commands,
            reason=(
                "Latest capability real cost tracking audit is incomplete; "
                "run the recommended upstream command before checking hosted dashboard proof."
            ),
            checklist_items=[],
            report_path=report_path,
        )

    source_item = _hosted_dashboard_item(source_audit)
    checklist_items = (
        [_checklist_item_from_cost_audit_item(source_item)]
        if source_item is not None
        else []
    )
    blocked_dashboard_proof_count = sum(
        1
        for item in checklist_items
        if item["recommended_dashboard_action"] == KEEP_HOSTED_DASHBOARD_DISABLED
    )
    operator_review_required_count = sum(
        1
        for item in checklist_items
        if item["recommended_dashboard_action"]
        == MANUAL_HOSTED_DASHBOARD_REVIEW_REQUIRED
    )
    if blocked_dashboard_proof_count:
        status = HOSTED_DASHBOARD_PROOF_BLOCKED
        reason = (
            "Hosted dashboard proof remains blocked until cost tracking, retry "
            "review, required evidence, and operator approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_HOSTED_DASHBOARD_REVIEW_REQUIRED
        reason = (
            "Hosted dashboard proof is ready for manual operator review; no "
            "dashboard, deployment, or routing state changes were applied."
        )
    else:
        status = NO_HOSTED_DASHBOARD_PROOF_CANDIDATE
        reason = "No hosted dashboard proof checklist row was needed from the latest cost audit."

    return storage.record_hosted_dashboard_proof_checklist(
        status=status,
        source_audit_id=source_audit.id,
        source_audit_status=source_audit.status,
        source_kind=REAL_COST_TRACKING_AUDIT_SOURCE,
        capability_count=len(checklist_items),
        checklist_count=len(checklist_items),
        blocked_dashboard_proof_count=blocked_dashboard_proof_count,
        operator_review_required_count=operator_review_required_count,
        blocked_cost_tracking_count=sum(
            1
            for item in checklist_items
            if item["source_cost_action"] == KEEP_COST_TRACKING_DISABLED
        ),
        blocked_retry_count=sum(
            1
            for item in checklist_items
            if item["source_retry_action"] == "keep_retry_disabled"
        ),
        blocked_trust_promotion_count=sum(
            1
            for item in checklist_items
            if item["source_trust_action"] == "keep_trust_unpromoted"
        ),
        missing_evidence_count=sum(
            1 for item in checklist_items if item["evidence_state"] == "missing"
        ),
        approval_required_count=sum(
            1
            for item in checklist_items
            if item["approval_state"] == "approval_required"
        ),
        boundary_count=len(
            {
                item["approval_boundary"]
                for item in checklist_items
                if item["approval_boundary"] != "none"
            }
        ),
        recommended_commands=[],
        reason=reason,
        checklist_items=checklist_items,
        report_path=report_path,
    )


def _hosted_dashboard_item(
    source_audit: CapabilityRealCostTrackingAudit,
) -> dict[str, str] | None:
    for item in source_audit.audit_items:
        if item["capability"] == HOSTED_DASHBOARD:
            return item
    return None


def _real_cost_tracking_proof_source_item(
    source_checklist: RealCostTrackingProofChecklist,
) -> dict[str, str] | None:
    for item in source_checklist.checklist_items:
        if item["capability"] == "real_cost_tracking":
            return item
    return None


def _checklist_item_from_real_cost_tracking_proof_item(
    item: dict[str, str],
) -> dict[str, str]:
    dashboard_blocked = item["recommended_cost_action"] == KEEP_COST_TRACKING_DISABLED
    return {
        "capability": HOSTED_DASHBOARD,
        "proof_item": HOSTED_DASHBOARD_PROOF_ITEM,
        "recommended_dashboard_action": (
            KEEP_HOSTED_DASHBOARD_DISABLED
            if dashboard_blocked
            else MANUAL_HOSTED_DASHBOARD_REVIEW_REQUIRED
        ),
        "dashboard_state": (
            DASHBOARD_BLOCKED_BY_PROOF
            if dashboard_blocked
            else DASHBOARD_REVIEW_READY
        ),
        "source_real_cost_tracking_proof_action": item["recommended_cost_action"],
        "source_real_cost_tracking_proof_state": item["real_cost_tracking_state"],
        "source_automatic_retry_proof_action": (
            item["source_automatic_retry_proof_action"]
        ),
        "source_automatic_retry_proof_state": (
            item["source_automatic_retry_proof_state"]
        ),
        "source_trust_proof_action": item["source_trust_proof_action"],
        "source_trust_proof_state": item["source_trust_proof_state"],
        "source_budget_action": item["source_budget_action"],
        "source_budget_state": item["source_budget_state"],
        "source_ci_deploy_action": item["source_ci_deploy_action"],
        "source_ci_deploy_state": item["source_ci_deploy_state"],
        "source_adapter_action": item["source_adapter_action"],
        "source_adapter_state": item["source_adapter_state"],
        "source_scheduling_action": item["source_scheduling_action"],
        "source_scheduling_state": item["source_scheduling_state"],
        "source_worker_action": item["source_worker_action"],
        "source_worker_state": item["source_worker_state"],
        "source_dashboard_action": item["source_dashboard_action"],
        "source_dashboard_state": item["source_dashboard_state"],
        "source_cost_action": item["recommended_cost_action"],
        "cost_tracking_state": item["real_cost_tracking_state"],
        "source_retry_action": item["source_retry_action"],
        "source_retry_state": item["source_retry_state"],
        "source_trust_action": item["source_trust_action"],
        "source_trust_state": item["source_trust_state"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "dashboard_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }


def _checklist_item_from_cost_audit_item(item: dict[str, str]) -> dict[str, str]:
    dashboard_blocked = item["recommended_cost_action"] == KEEP_COST_TRACKING_DISABLED
    return {
        "capability": item["capability"],
        "proof_item": HOSTED_DASHBOARD_PROOF_ITEM,
        "recommended_dashboard_action": (
            KEEP_HOSTED_DASHBOARD_DISABLED
            if dashboard_blocked
            else MANUAL_HOSTED_DASHBOARD_REVIEW_REQUIRED
        ),
        "dashboard_state": (
            DASHBOARD_BLOCKED if dashboard_blocked else DASHBOARD_REVIEW_READY
        ),
        "source_cost_action": item["recommended_cost_action"],
        "cost_tracking_state": item["cost_tracking_state"],
        "source_retry_action": item["source_retry_action"],
        "source_retry_state": item["source_retry_state"],
        "source_trust_action": item["source_trust_action"],
        "source_trust_state": item["source_trust_state"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "dashboard_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }
