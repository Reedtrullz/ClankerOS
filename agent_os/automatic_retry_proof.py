from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    AutomaticRetryProofChecklist,
    AutonomousSchedulingProofChecklist,
    BudgetEnforcementProofChecklist,
    BrowserDesktopAdapterProofChecklist,
    CiDeployProofChecklist,
    HostedDashboardProofChecklist,
    RealCostTrackingProofChecklist,
    RemoteWorkerProofChecklist,
    Storage,
    TrustPromotionProofChecklist,
)


TRUST_PROMOTION_PROOF_CHECKLIST_MISSING = (
    "trust_promotion_proof_checklist_missing"
)
AUTOMATIC_RETRY_PROOF_BLOCKED = "automatic_retry_proof_blocked"
OPERATOR_AUTOMATIC_RETRY_REVIEW_REQUIRED = (
    "operator_automatic_retry_review_required"
)
NO_AUTOMATIC_RETRY_PROOF_CANDIDATE = "no_automatic_retry_proof_candidate"
KEEP_RETRY_DISABLED = "keep_retry_disabled"
MANUAL_RETRY_REVIEW_REQUIRED = "manual_retry_review_required"
KEEP_TRUST_UNPROMOTED = "keep_trust_unpromoted"
AUTOMATIC_RETRY_BLOCKED = (
    "blocked_until_trust_promotion_proof_and_operator_approval"
)
AUTOMATIC_RETRY_REVIEW_READY = "ready_for_operator_automatic_retry_review"
AUTOMATIC_RETRY = "automatic_retry"
AUTOMATIC_RETRY_PROOF_ITEM = "automatic_retry_policy_contract"
NO_EFFECT = "none"
REPORT_PATH = "docs/automatic-retry-proof-checklist.md"


def write_automatic_retry_proof_checklist(
    root: Path,
) -> tuple[Path, AutomaticRetryProofChecklist]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    trust_checklists = storage.list_recent_trust_promotion_proof_checklists(
        limit=None,
    )
    (
        source_checklist,
        source_budget_checklist,
        source_ci_deploy_checklist,
        source_browser_desktop_adapter_checklist,
        source_autonomous_scheduling_checklist,
        source_remote_worker_checklist,
        source_hosted_dashboard_checklist,
        source_real_cost_tracking_checklist,
    ) = _latest_real_cost_sourced_trust_promotion_proof(
        storage=storage,
        trust_checklists=trust_checklists,
    )
    if source_checklist is None:
        fallback_checklist = trust_checklists[0] if trust_checklists else None
        (
            source_budget_checklist,
            source_ci_deploy_checklist,
            source_browser_desktop_adapter_checklist,
            source_autonomous_scheduling_checklist,
            source_remote_worker_checklist,
            source_hosted_dashboard_checklist,
            source_real_cost_tracking_checklist,
        ) = _source_chain_from_trust_promotion_proof(
            storage=storage,
            source_checklist=fallback_checklist,
        )
        source_automatic_retry_checklist = (
            storage.get_automatic_retry_proof_checklist(
                source_real_cost_tracking_checklist.source_checklist_id
            )
            if source_real_cost_tracking_checklist is not None
            else None
        )
        has_dangling_real_cost_source = (
            source_hosted_dashboard_checklist is not None
            and source_hosted_dashboard_checklist.source_kind
            == "real_cost_tracking_proof_checklist"
            and (
                source_real_cost_tracking_checklist is None
                or source_automatic_retry_checklist is None
            )
        )
        if has_dangling_real_cost_source:
            source_checklist = None
            source_budget_checklist = None
            source_ci_deploy_checklist = None
            source_browser_desktop_adapter_checklist = None
            source_autonomous_scheduling_checklist = None
            source_remote_worker_checklist = None
            source_hosted_dashboard_checklist = None
            source_real_cost_tracking_checklist = None
        else:
            source_checklist = fallback_checklist
    checklist = _checklist_from_latest_trust_promotion_proof(
        storage=storage,
        source_checklist=source_checklist,
        report_path=REPORT_PATH,
    )
    report_path = root / checklist.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_automatic_retry_proof_checklist_report(
            checklist,
            source_checklist,
            source_budget_checklist,
            source_ci_deploy_checklist,
            source_browser_desktop_adapter_checklist,
            source_autonomous_scheduling_checklist,
            source_remote_worker_checklist,
            source_hosted_dashboard_checklist,
            source_real_cost_tracking_checklist,
        ),
        encoding="utf-8",
    )
    return report_path, checklist


def render_automatic_retry_proof_checklist_report(
    checklist: AutomaticRetryProofChecklist,
    source_checklist: TrustPromotionProofChecklist | None,
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
        "# Automatic Retry Proof Checklist",
        "",
        f"- id: {checklist.id}",
        f"- status: {checklist.status}",
        f"- source_checklist_id: {checklist.source_checklist_id or 'none'}",
        f"- source_checklist_status: {checklist.source_checklist_status}",
        f"- capability_count: {checklist.capability_count}",
        f"- checklist_items: {checklist.checklist_count}",
        f"- blocked_automatic_retry_proofs: {checklist.blocked_automatic_retry_proof_count}",
        f"- operator_reviews_required: {checklist.operator_review_required_count}",
        f"- blocked_trust_promotion_proofs: {checklist.blocked_trust_promotion_proof_count}",
        f"- blocked_budget_enforcement_proofs: {checklist.blocked_budget_enforcement_proof_count}",
        f"- blocked_ci_deploy_proofs: {checklist.blocked_ci_deploy_proof_count}",
        f"- blocked_adapter_proofs: {checklist.blocked_adapter_proof_count}",
        f"- blocked_scheduling_proofs: {checklist.blocked_scheduling_proof_count}",
        f"- blocked_worker_proofs: {checklist.blocked_worker_proof_count}",
        f"- blocked_dashboard_proofs: {checklist.blocked_dashboard_proof_count}",
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
        "## Automatic Retry Proof Items",
        "",
    ]
    if checklist.checklist_items:
        lines.extend(render_checklist_item_line(item) for item in checklist.checklist_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Trust Promotion Proof Checklist", ""])
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
                f"- blocked_trust_promotion_proofs: {source_checklist.blocked_trust_promotion_proof_count}",
                f"- operator_reviews_required: {source_checklist.operator_review_required_count}",
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
        if source_budget_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_id: "
                    f"{source_budget_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_status: "
                    f"{source_budget_checklist.source_checklist_status}",
                ]
            )
        if source_ci_deploy_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_ci_deploy_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_ci_deploy_checklist.source_checklist_status}",
                ]
            )
        if source_browser_desktop_adapter_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_browser_desktop_adapter_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_browser_desktop_adapter_checklist.source_checklist_status}",
                ]
            )
        if source_autonomous_scheduling_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_autonomous_scheduling_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_autonomous_scheduling_checklist.source_checklist_status}",
                ]
            )
        if source_remote_worker_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_remote_worker_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_remote_worker_checklist.source_checklist_status}",
                ]
            )
        if source_hosted_dashboard_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_hosted_dashboard_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_hosted_dashboard_checklist.source_checklist_status}",
                ]
            )
        if source_real_cost_tracking_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_real_cost_tracking_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_real_cost_tracking_checklist.source_checklist_status}",
                ]
            )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local Automatic Retry proof checklist.",
            "- Does not create Trust Promotion proof checklists as a side effect.",
            "- Does not create Budget Enforcement proof checklists as a side effect.",
            "- Does not create CI Deploy proof checklists as a side effect.",
            "- Does not create browser/desktop adapter proof checklists as a side effect.",
            "- Does not create autonomous scheduling proof checklists as a side effect.",
            "- Does not create remote worker proof checklists as a side effect.",
            "- Does not create hosted dashboard proof checklists as a side effect.",
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
            "- Does not claim remote work.",
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


def render_automatic_retry_proof_checklist_line(
    checklist: AutomaticRetryProofChecklist,
) -> str:
    return (
        f"- {checklist.id}: status={checklist.status} "
        f"source_checklist={checklist.source_checklist_id or 'none'} "
        f"source_status={checklist.source_checklist_status} "
        f"checklist_items={checklist.checklist_count} "
        f"blocked_automatic_retry_proofs={checklist.blocked_automatic_retry_proof_count} "
        f"operator_reviews_required={checklist.operator_review_required_count} "
        f"blocked_trust_promotion_proofs={checklist.blocked_trust_promotion_proof_count} "
        f"blocked_budget_enforcement_proofs={checklist.blocked_budget_enforcement_proof_count} "
        f"blocked_ci_deploy_proofs={checklist.blocked_ci_deploy_proof_count} "
        f"blocked_adapter_proofs={checklist.blocked_adapter_proof_count} "
        f"blocked_scheduling_proofs={checklist.blocked_scheduling_proof_count} "
        f"blocked_worker_proofs={checklist.blocked_worker_proof_count} "
        f"blocked_dashboard_proofs={checklist.blocked_dashboard_proof_count} "
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
        f"- {item['capability']}: proof_item={item['proof_item']} "
        f"recommended_retry_action={item['recommended_retry_action']}",
        f"automatic_retry_state={item['automatic_retry_state']}",
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
    optional_proof_keys = (
        "source_real_cost_tracking_proof_action",
        "source_real_cost_tracking_proof_state",
        "source_automatic_retry_proof_action",
        "source_automatic_retry_proof_state",
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
            f"automatic_retry_effect={item['automatic_retry_effect']}",
            f"routing_effect={item['routing_effect']}",
        ]
    )
    return " ".join(parts)


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _latest_real_cost_sourced_trust_promotion_proof(
    *,
    storage: Storage,
    trust_checklists: list[TrustPromotionProofChecklist],
) -> tuple[
    TrustPromotionProofChecklist | None,
    BudgetEnforcementProofChecklist | None,
    CiDeployProofChecklist | None,
    BrowserDesktopAdapterProofChecklist | None,
    AutonomousSchedulingProofChecklist | None,
    RemoteWorkerProofChecklist | None,
    HostedDashboardProofChecklist | None,
    RealCostTrackingProofChecklist | None,
]:
    for trust_checklist in trust_checklists:
        (
            budget_checklist,
            ci_deploy_checklist,
            browser_desktop_adapter_checklist,
            autonomous_scheduling_checklist,
            remote_worker_checklist,
            hosted_dashboard_checklist,
            real_cost_tracking_checklist,
        ) = _source_chain_from_trust_promotion_proof(
            storage=storage,
            source_checklist=trust_checklist,
        )
        if (
            budget_checklist is None
            or ci_deploy_checklist is None
            or browser_desktop_adapter_checklist is None
            or autonomous_scheduling_checklist is None
            or remote_worker_checklist is None
            or hosted_dashboard_checklist is None
            or real_cost_tracking_checklist is None
        ):
            continue
        automatic_retry_checklist = storage.get_automatic_retry_proof_checklist(
            real_cost_tracking_checklist.source_checklist_id
        )
        if automatic_retry_checklist is None:
            continue
        return (
            trust_checklist,
            budget_checklist,
            ci_deploy_checklist,
            browser_desktop_adapter_checklist,
            autonomous_scheduling_checklist,
            remote_worker_checklist,
            hosted_dashboard_checklist,
            real_cost_tracking_checklist,
        )
    return None, None, None, None, None, None, None, None


def _source_chain_from_trust_promotion_proof(
    *,
    storage: Storage,
    source_checklist: TrustPromotionProofChecklist | None,
) -> tuple[
    BudgetEnforcementProofChecklist | None,
    CiDeployProofChecklist | None,
    BrowserDesktopAdapterProofChecklist | None,
    AutonomousSchedulingProofChecklist | None,
    RemoteWorkerProofChecklist | None,
    HostedDashboardProofChecklist | None,
    RealCostTrackingProofChecklist | None,
]:
    if source_checklist is None:
        return None, None, None, None, None, None, None
    budget_checklist = storage.get_budget_enforcement_proof_checklist(
        source_checklist.source_checklist_id
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
    real_cost_tracking_checklist = (
        storage.get_real_cost_tracking_proof_checklist(
            hosted_dashboard_checklist.source_checklist_id
        )
        if hosted_dashboard_checklist is not None
        and hosted_dashboard_checklist.source_kind
        == "real_cost_tracking_proof_checklist"
        else None
    )
    return (
        budget_checklist,
        ci_deploy_checklist,
        browser_desktop_adapter_checklist,
        autonomous_scheduling_checklist,
        remote_worker_checklist,
        hosted_dashboard_checklist,
        real_cost_tracking_checklist,
    )


def _checklist_from_latest_trust_promotion_proof(
    *,
    storage: Storage,
    source_checklist: TrustPromotionProofChecklist | None,
    report_path: str,
) -> AutomaticRetryProofChecklist:
    if source_checklist is None:
        return storage.record_automatic_retry_proof_checklist(
            status=TRUST_PROMOTION_PROOF_CHECKLIST_MISSING,
            source_checklist_id=None,
            source_checklist_status="none",
            capability_count=0,
            checklist_count=0,
            blocked_automatic_retry_proof_count=0,
            operator_review_required_count=0,
            blocked_trust_promotion_proof_count=0,
            blocked_budget_enforcement_proof_count=0,
            blocked_ci_deploy_proof_count=0,
            blocked_adapter_proof_count=0,
            blocked_scheduling_proof_count=0,
            blocked_worker_proof_count=0,
            blocked_dashboard_proof_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["trust-promotion-proof-checklist"],
            reason="No Trust Promotion proof checklist exists yet.",
            checklist_items=[],
            report_path=report_path,
        )

    if (
        source_checklist.status != "operator_trust_promotion_review_required"
        and not source_checklist.checklist_items
        and source_checklist.recommended_commands
    ):
        return storage.record_automatic_retry_proof_checklist(
            status=TRUST_PROMOTION_PROOF_CHECKLIST_MISSING,
            source_checklist_id=source_checklist.id,
            source_checklist_status=source_checklist.status,
            capability_count=0,
            checklist_count=0,
            blocked_automatic_retry_proof_count=0,
            operator_review_required_count=0,
            blocked_trust_promotion_proof_count=0,
            blocked_budget_enforcement_proof_count=0,
            blocked_ci_deploy_proof_count=0,
            blocked_adapter_proof_count=0,
            blocked_scheduling_proof_count=0,
            blocked_worker_proof_count=0,
            blocked_dashboard_proof_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=source_checklist.recommended_commands,
            reason=(
                "Latest Trust Promotion proof checklist is incomplete; run the "
                "recommended upstream command before checking Automatic Retry proof."
            ),
            checklist_items=[],
            report_path=report_path,
        )

    source_item = _trust_promotion_source_item(source_checklist)
    checklist_items = (
        [_checklist_item_from_trust_promotion_proof_item(source_item)]
        if source_item is not None
        else []
    )
    blocked_automatic_retry_proof_count = sum(
        1
        for item in checklist_items
        if item["recommended_retry_action"] == KEEP_RETRY_DISABLED
    )
    operator_review_required_count = sum(
        1
        for item in checklist_items
        if item["recommended_retry_action"] == MANUAL_RETRY_REVIEW_REQUIRED
    )
    if blocked_automatic_retry_proof_count:
        status = AUTOMATIC_RETRY_PROOF_BLOCKED
        reason = (
            "Automatic Retry proof remains blocked until Trust Promotion proof, "
            "Budget Enforcement proof, CI Deploy proof, browser/desktop adapter "
            "proof, autonomous scheduling proof, remote worker proof, hosted "
            "dashboard proof, cost tracking, retry review, required evidence, "
            "and operator approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_AUTOMATIC_RETRY_REVIEW_REQUIRED
        reason = (
            "Automatic Retry proof is ready for manual operator review; no "
            "retry, trust, budget, CI, deploy, adapter, scheduler, routing, "
            "or claim state changes were applied."
        )
    else:
        status = NO_AUTOMATIC_RETRY_PROOF_CANDIDATE
        reason = (
            "No Automatic Retry proof checklist row was needed from the latest "
            "Trust Promotion proof checklist."
        )

    return storage.record_automatic_retry_proof_checklist(
        status=status,
        source_checklist_id=source_checklist.id,
        source_checklist_status=source_checklist.status,
        capability_count=len(checklist_items),
        checklist_count=len(checklist_items),
        blocked_automatic_retry_proof_count=blocked_automatic_retry_proof_count,
        operator_review_required_count=operator_review_required_count,
        blocked_trust_promotion_proof_count=sum(
            1
            for item in checklist_items
            if item["source_trust_proof_action"] == KEEP_TRUST_UNPROMOTED
        ),
        blocked_budget_enforcement_proof_count=sum(
            1
            for item in checklist_items
            if item["source_budget_action"] == "keep_budget_enforcement_disabled"
        ),
        blocked_ci_deploy_proof_count=sum(
            1
            for item in checklist_items
            if item["source_ci_deploy_action"] == "keep_ci_deploy_disabled"
        ),
        blocked_adapter_proof_count=sum(
            1
            for item in checklist_items
            if item["source_adapter_action"]
            == "keep_browser_desktop_adapters_disabled"
        ),
        blocked_scheduling_proof_count=sum(
            1
            for item in checklist_items
            if item["source_scheduling_action"]
            == "keep_autonomous_scheduling_disabled"
        ),
        blocked_worker_proof_count=sum(
            1
            for item in checklist_items
            if item["source_worker_action"] == "keep_remote_workers_disabled"
        ),
        blocked_dashboard_proof_count=sum(
            1
            for item in checklist_items
            if item["source_dashboard_action"] == "keep_hosted_dashboard_disabled"
        ),
        blocked_cost_tracking_count=sum(
            1
            for item in checklist_items
            if item["source_cost_action"] == "keep_cost_tracking_disabled"
        ),
        blocked_retry_count=sum(
            1
            for item in checklist_items
            if item["source_retry_action"] == KEEP_RETRY_DISABLED
        ),
        blocked_trust_promotion_count=sum(
            1
            for item in checklist_items
            if item["source_trust_action"] == KEEP_TRUST_UNPROMOTED
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


def _trust_promotion_source_item(
    source_checklist: TrustPromotionProofChecklist,
) -> dict[str, str] | None:
    for item in source_checklist.checklist_items:
        if item["capability"] == "trust_promotion":
            return item
    return None


def _checklist_item_from_trust_promotion_proof_item(
    item: dict[str, str],
) -> dict[str, str]:
    automatic_retry_blocked = (
        item["recommended_trust_action"] == KEEP_TRUST_UNPROMOTED
    )
    checklist_item = {
        "capability": AUTOMATIC_RETRY,
        "proof_item": AUTOMATIC_RETRY_PROOF_ITEM,
        "recommended_retry_action": (
            KEEP_RETRY_DISABLED
            if automatic_retry_blocked
            else MANUAL_RETRY_REVIEW_REQUIRED
        ),
        "automatic_retry_state": (
            AUTOMATIC_RETRY_BLOCKED
            if automatic_retry_blocked
            else AUTOMATIC_RETRY_REVIEW_READY
        ),
        "source_trust_proof_action": item["recommended_trust_action"],
        "source_trust_proof_state": item["trust_promotion_state"],
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
        "source_cost_action": item["source_cost_action"],
        "cost_tracking_state": item["cost_tracking_state"],
        "source_retry_action": item["source_retry_action"],
        "source_retry_state": item["source_retry_state"],
        "source_trust_action": item["source_trust_action"],
        "source_trust_state": item["source_trust_state"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "automatic_retry_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }
    for key in (
        "source_real_cost_tracking_proof_action",
        "source_real_cost_tracking_proof_state",
        "source_automatic_retry_proof_action",
        "source_automatic_retry_proof_state",
    ):
        if key in item:
            checklist_item[key] = item[key]
    return checklist_item
