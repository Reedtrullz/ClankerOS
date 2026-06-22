from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    AutonomousSchedulingProofChecklist,
    BrowserDesktopAdapterProofChecklist,
    HostedDashboardProofChecklist,
    RealCostTrackingProofChecklist,
    RemoteWorkerProofChecklist,
    Storage,
)


AUTONOMOUS_SCHEDULING_PROOF_CHECKLIST_MISSING = (
    "autonomous_scheduling_proof_checklist_missing"
)
BROWSER_DESKTOP_ADAPTER_PROOF_BLOCKED = "browser_desktop_adapter_proof_blocked"
OPERATOR_BROWSER_DESKTOP_ADAPTER_REVIEW_REQUIRED = (
    "operator_browser_desktop_adapter_review_required"
)
NO_BROWSER_DESKTOP_ADAPTER_PROOF_CANDIDATE = (
    "no_browser_desktop_adapter_proof_candidate"
)
KEEP_BROWSER_DESKTOP_ADAPTERS_DISABLED = "keep_browser_desktop_adapters_disabled"
MANUAL_BROWSER_DESKTOP_ADAPTER_REVIEW_REQUIRED = (
    "manual_browser_desktop_adapter_review_required"
)
KEEP_AUTONOMOUS_SCHEDULING_DISABLED = "keep_autonomous_scheduling_disabled"
ADAPTER_BLOCKED = "blocked_until_autonomous_scheduling_proof_and_operator_approval"
ADAPTER_REVIEW_READY = "ready_for_operator_browser_desktop_adapter_review"
BROWSER_DESKTOP_ADAPTERS = "browser_desktop_adapters"
BROWSER_DESKTOP_ADAPTER_PROOF_ITEM = "adapter_permission_boundary_review"
NO_EFFECT = "none"
REPORT_PATH = "docs/browser-desktop-adapter-proof-checklist.md"


def write_browser_desktop_adapter_proof_checklist(
    root: Path,
) -> tuple[Path, BrowserDesktopAdapterProofChecklist]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    scheduling_checklists = storage.list_recent_autonomous_scheduling_proof_checklists(
        limit=None,
    )
    (
        source_checklist,
        source_remote_worker_checklist,
        source_hosted_dashboard_checklist,
        source_real_cost_tracking_checklist,
    ) = _latest_real_cost_sourced_autonomous_scheduling_proof(
        storage=storage,
        scheduling_checklists=scheduling_checklists,
    )
    if source_checklist is None:
        fallback_checklist = (
            scheduling_checklists[0] if scheduling_checklists else None
        )
        source_remote_worker_checklist = (
            storage.get_remote_worker_proof_checklist(
                fallback_checklist.source_checklist_id
            )
            if fallback_checklist is not None
            else None
        )
        source_hosted_dashboard_checklist = (
            storage.get_hosted_dashboard_proof_checklist(
                source_remote_worker_checklist.source_checklist_id
            )
            if source_remote_worker_checklist is not None
            else None
        )
        source_real_cost_tracking_checklist = (
            storage.get_real_cost_tracking_proof_checklist(
                source_hosted_dashboard_checklist.source_checklist_id
            )
            if source_hosted_dashboard_checklist is not None
            and source_hosted_dashboard_checklist.source_kind
            == "real_cost_tracking_proof_checklist"
            else None
        )
        if (
            fallback_checklist is not None
            and (
                source_remote_worker_checklist is None
                or source_hosted_dashboard_checklist is None
                or source_hosted_dashboard_checklist.source_kind
                != "real_cost_tracking_proof_checklist"
            )
        ):
            source_checklist = fallback_checklist
    checklist = _checklist_from_latest_autonomous_scheduling_proof(
        storage=storage,
        source_checklist=source_checklist,
        report_path=REPORT_PATH,
    )
    report_path = root / checklist.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_browser_desktop_adapter_proof_checklist_report(
            checklist,
            source_checklist,
            source_remote_worker_checklist,
            source_hosted_dashboard_checklist,
            source_real_cost_tracking_checklist,
        ),
        encoding="utf-8",
    )
    return report_path, checklist


def render_browser_desktop_adapter_proof_checklist_report(
    checklist: BrowserDesktopAdapterProofChecklist,
    source_checklist: AutonomousSchedulingProofChecklist | None,
    source_remote_worker_checklist: RemoteWorkerProofChecklist | None = None,
    source_hosted_dashboard_checklist: HostedDashboardProofChecklist | None = None,
    source_real_cost_tracking_checklist: RealCostTrackingProofChecklist | None = None,
) -> str:
    lines = [
        "# Browser Desktop Adapter Proof Checklist",
        "",
        f"- id: {checklist.id}",
        f"- status: {checklist.status}",
        f"- source_checklist_id: {checklist.source_checklist_id or 'none'}",
        f"- source_checklist_status: {checklist.source_checklist_status}",
        f"- capability_count: {checklist.capability_count}",
        f"- checklist_items: {checklist.checklist_count}",
        f"- blocked_adapter_proofs: {checklist.blocked_adapter_proof_count}",
        f"- operator_reviews_required: {checklist.operator_review_required_count}",
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
        "## Browser Desktop Adapter Proof Items",
        "",
    ]
    if checklist.checklist_items:
        lines.extend(render_checklist_item_line(item) for item in checklist.checklist_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Autonomous Scheduling Proof Checklist", ""])
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
                f"- blocked_scheduling_proofs: {source_checklist.blocked_scheduling_proof_count}",
                f"- operator_reviews_required: {source_checklist.operator_review_required_count}",
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
        if source_remote_worker_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_id: "
                    f"{source_remote_worker_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_status: "
                    f"{source_remote_worker_checklist.source_checklist_status}",
                ]
            )
        if source_hosted_dashboard_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_hosted_dashboard_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_hosted_dashboard_checklist.source_checklist_status}",
                ]
            )
        if source_real_cost_tracking_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_id: "
                    f"{source_real_cost_tracking_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_source_checklist_source_checklist_status: "
                    f"{source_real_cost_tracking_checklist.source_checklist_status}",
                ]
            )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local browser/desktop adapter proof checklist.",
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


def render_browser_desktop_adapter_proof_checklist_line(
    checklist: BrowserDesktopAdapterProofChecklist,
) -> str:
    return (
        f"- {checklist.id}: status={checklist.status} "
        f"source_checklist={checklist.source_checklist_id or 'none'} "
        f"source_status={checklist.source_checklist_status} "
        f"checklist_items={checklist.checklist_count} "
        f"blocked_adapter_proofs={checklist.blocked_adapter_proof_count} "
        f"operator_reviews_required={checklist.operator_review_required_count} "
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
        f"- {item['capability']}: proof_item={item['proof_item']}",
        f"recommended_adapter_action={item['recommended_adapter_action']}",
        f"adapter_state={item['adapter_state']}",
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
        "source_trust_proof_action",
        "source_trust_proof_state",
        "source_budget_action",
        "source_budget_state",
        "source_ci_deploy_action",
        "source_ci_deploy_state",
        "source_adapter_action",
        "source_adapter_state",
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
            f"adapter_effect={item['adapter_effect']}",
            f"routing_effect={item['routing_effect']}",
        ]
    )
    return " ".join(parts)


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _latest_real_cost_sourced_autonomous_scheduling_proof(
    *,
    storage: Storage,
    scheduling_checklists: list[AutonomousSchedulingProofChecklist],
) -> tuple[
    AutonomousSchedulingProofChecklist | None,
    RemoteWorkerProofChecklist | None,
    HostedDashboardProofChecklist | None,
    RealCostTrackingProofChecklist | None,
]:
    for scheduling_checklist in scheduling_checklists:
        remote_worker_checklist = storage.get_remote_worker_proof_checklist(
            scheduling_checklist.source_checklist_id
        )
        if remote_worker_checklist is None:
            continue
        hosted_dashboard_checklist = storage.get_hosted_dashboard_proof_checklist(
            remote_worker_checklist.source_checklist_id
        )
        if (
            hosted_dashboard_checklist is None
            or hosted_dashboard_checklist.source_kind
            != "real_cost_tracking_proof_checklist"
        ):
            continue
        real_cost_tracking_checklist = (
            storage.get_real_cost_tracking_proof_checklist(
                hosted_dashboard_checklist.source_checklist_id
            )
        )
        if real_cost_tracking_checklist is None:
            continue
        if (
            storage.get_automatic_retry_proof_checklist(
                real_cost_tracking_checklist.source_checklist_id
            )
            is None
        ):
            continue
        return (
            scheduling_checklist,
            remote_worker_checklist,
            hosted_dashboard_checklist,
            real_cost_tracking_checklist,
        )
    return None, None, None, None


def _checklist_from_latest_autonomous_scheduling_proof(
    *,
    storage: Storage,
    source_checklist: AutonomousSchedulingProofChecklist | None,
    report_path: str,
) -> BrowserDesktopAdapterProofChecklist:
    if source_checklist is None:
        return storage.record_browser_desktop_adapter_proof_checklist(
            status=AUTONOMOUS_SCHEDULING_PROOF_CHECKLIST_MISSING,
            source_checklist_id=None,
            source_checklist_status="none",
            capability_count=0,
            checklist_count=0,
            blocked_adapter_proof_count=0,
            operator_review_required_count=0,
            blocked_scheduling_proof_count=0,
            blocked_worker_proof_count=0,
            blocked_dashboard_proof_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["autonomous-scheduling-proof-checklist"],
            reason="No autonomous scheduling proof checklist exists yet.",
            checklist_items=[],
            report_path=report_path,
        )

    if (
        source_checklist.status != "operator_autonomous_scheduling_review_required"
        and not source_checklist.checklist_items
        and source_checklist.recommended_commands
    ):
        return storage.record_browser_desktop_adapter_proof_checklist(
            status=AUTONOMOUS_SCHEDULING_PROOF_CHECKLIST_MISSING,
            source_checklist_id=source_checklist.id,
            source_checklist_status=source_checklist.status,
            capability_count=0,
            checklist_count=0,
            blocked_adapter_proof_count=0,
            operator_review_required_count=0,
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
                "Latest autonomous scheduling proof checklist is incomplete; "
                "run the recommended upstream command before checking "
                "browser/desktop adapter proof."
            ),
            checklist_items=[],
            report_path=report_path,
        )

    source_item = _autonomous_scheduling_source_item(source_checklist)
    checklist_items = (
        [_checklist_item_from_autonomous_scheduling_proof_item(source_item)]
        if source_item is not None
        else []
    )
    blocked_adapter_proof_count = sum(
        1
        for item in checklist_items
        if item["recommended_adapter_action"]
        == KEEP_BROWSER_DESKTOP_ADAPTERS_DISABLED
    )
    operator_review_required_count = sum(
        1
        for item in checklist_items
        if item["recommended_adapter_action"]
        == MANUAL_BROWSER_DESKTOP_ADAPTER_REVIEW_REQUIRED
    )
    if blocked_adapter_proof_count:
        status = BROWSER_DESKTOP_ADAPTER_PROOF_BLOCKED
        reason = (
            "Browser/desktop adapter proof remains blocked until autonomous "
            "scheduling proof, remote worker proof, hosted dashboard proof, "
            "cost tracking, retry review, required evidence, and operator "
            "approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_BROWSER_DESKTOP_ADAPTER_REVIEW_REQUIRED
        reason = (
            "Browser/desktop adapter proof is ready for manual operator review; "
            "no adapter, scheduler, routing, or claim state changes were applied."
        )
    else:
        status = NO_BROWSER_DESKTOP_ADAPTER_PROOF_CANDIDATE
        reason = (
            "No browser/desktop adapter proof checklist row was needed from the "
            "latest autonomous scheduling proof checklist."
        )

    return storage.record_browser_desktop_adapter_proof_checklist(
        status=status,
        source_checklist_id=source_checklist.id,
        source_checklist_status=source_checklist.status,
        capability_count=len(checklist_items),
        checklist_count=len(checklist_items),
        blocked_adapter_proof_count=blocked_adapter_proof_count,
        operator_review_required_count=operator_review_required_count,
        blocked_scheduling_proof_count=sum(
            1
            for item in checklist_items
            if item["source_scheduling_action"]
            == KEEP_AUTONOMOUS_SCHEDULING_DISABLED
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


def _autonomous_scheduling_source_item(
    source_checklist: AutonomousSchedulingProofChecklist,
) -> dict[str, str] | None:
    for item in source_checklist.checklist_items:
        if item["capability"] == "autonomous_scheduling":
            return item
    return None


def _checklist_item_from_autonomous_scheduling_proof_item(
    item: dict[str, str],
) -> dict[str, str]:
    adapter_blocked = (
        item["recommended_scheduling_action"]
        == KEEP_AUTONOMOUS_SCHEDULING_DISABLED
    )
    checklist_item = {
        "capability": BROWSER_DESKTOP_ADAPTERS,
        "proof_item": BROWSER_DESKTOP_ADAPTER_PROOF_ITEM,
        "recommended_adapter_action": (
            KEEP_BROWSER_DESKTOP_ADAPTERS_DISABLED
            if adapter_blocked
            else MANUAL_BROWSER_DESKTOP_ADAPTER_REVIEW_REQUIRED
        ),
        "adapter_state": (
            ADAPTER_BLOCKED if adapter_blocked else ADAPTER_REVIEW_READY
        ),
        "source_scheduling_action": item["recommended_scheduling_action"],
        "source_scheduling_state": item["scheduling_state"],
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
        "adapter_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }
    for key in (
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
    ):
        if key in item:
            checklist_item[key] = item[key]
    return checklist_item
