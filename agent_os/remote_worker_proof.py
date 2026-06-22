from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    HostedDashboardProofChecklist,
    RealCostTrackingProofChecklist,
    RemoteWorkerProofChecklist,
    Storage,
)


HOSTED_DASHBOARD_PROOF_CHECKLIST_MISSING = (
    "hosted_dashboard_proof_checklist_missing"
)
REMOTE_WORKER_PROOF_BLOCKED = "remote_worker_proof_blocked"
OPERATOR_REMOTE_WORKER_REVIEW_REQUIRED = "operator_remote_worker_review_required"
NO_REMOTE_WORKER_PROOF_CANDIDATE = "no_remote_worker_proof_candidate"
KEEP_REMOTE_WORKERS_DISABLED = "keep_remote_workers_disabled"
MANUAL_REMOTE_WORKER_REVIEW_REQUIRED = "manual_remote_worker_review_required"
KEEP_HOSTED_DASHBOARD_DISABLED = "keep_hosted_dashboard_disabled"
WORKER_BLOCKED = "blocked_until_hosted_dashboard_proof_and_operator_approval"
WORKER_REVIEW_READY = "ready_for_operator_remote_worker_review"
REMOTE_WORKERS = "remote_workers"
REMOTE_WORKER_PROOF_ITEM = "remote_worker_dispatch_review"
NO_EFFECT = "none"
REPORT_PATH = "docs/remote-worker-proof-checklist.md"


def write_remote_worker_proof_checklist(
    root: Path,
) -> tuple[Path, RemoteWorkerProofChecklist]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    dashboard_checklists = storage.list_recent_hosted_dashboard_proof_checklists(
        limit=None,
    )
    (
        source_checklist,
        source_real_cost_tracking_checklist,
    ) = _latest_real_cost_sourced_hosted_dashboard_proof(
        storage=storage,
        dashboard_checklists=dashboard_checklists,
    )
    if source_checklist is None:
        fallback_checklist = dashboard_checklists[0] if dashboard_checklists else None
        if (
            fallback_checklist is not None
            and fallback_checklist.source_kind != "real_cost_tracking_proof_checklist"
        ):
            source_checklist = fallback_checklist
    checklist = _checklist_from_latest_dashboard_proof(
        storage=storage,
        source_checklist=source_checklist,
        report_path=REPORT_PATH,
    )
    report_path = root / checklist.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_remote_worker_proof_checklist_report(
            checklist,
            source_checklist,
            source_real_cost_tracking_checklist,
        ),
        encoding="utf-8",
    )
    return report_path, checklist


def render_remote_worker_proof_checklist_report(
    checklist: RemoteWorkerProofChecklist,
    source_checklist: HostedDashboardProofChecklist | None,
    source_real_cost_tracking_checklist: RealCostTrackingProofChecklist | None = None,
) -> str:
    lines = [
        "# Remote Worker Proof Checklist",
        "",
        f"- id: {checklist.id}",
        f"- status: {checklist.status}",
        f"- source_checklist_id: {checklist.source_checklist_id or 'none'}",
        f"- source_checklist_status: {checklist.source_checklist_status}",
        f"- capability_count: {checklist.capability_count}",
        f"- checklist_items: {checklist.checklist_count}",
        f"- blocked_worker_proofs: {checklist.blocked_worker_proof_count}",
        f"- operator_reviews_required: {checklist.operator_review_required_count}",
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
        "## Remote Worker Proof Items",
        "",
    ]
    if checklist.checklist_items:
        lines.extend(render_checklist_item_line(item) for item in checklist.checklist_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Hosted Dashboard Proof Checklist", ""])
    if source_checklist is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_checklist.id}",
                f"- status: {source_checklist.status}",
                f"- source_checklist_source_kind: {source_checklist.source_kind}",
                f"- source_checklist_source_checklist_id: {source_checklist.source_checklist_id or 'none'}",
                f"- source_checklist_source_checklist_status: {source_checklist.source_checklist_status}",
                f"- source_checklist_source_audit_id: {source_checklist.source_audit_id or 'none'}",
                f"- source_checklist_source_audit_status: {source_checklist.source_audit_status}",
                f"- checklist_items: {source_checklist.checklist_count}",
                f"- blocked_dashboard_proofs: {source_checklist.blocked_dashboard_proof_count}",
                f"- operator_reviews_required: {source_checklist.operator_review_required_count}",
                f"- blocked_cost_tracking: {source_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {source_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {source_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {source_checklist.missing_evidence_count}",
                f"- approvals_required: {source_checklist.approval_required_count}",
                f"- report: {source_checklist.report_path}",
            ]
        )
        if source_real_cost_tracking_checklist is not None:
            lines.extend(
                [
                    "- source_checklist_source_checklist_source_checklist_id: "
                    f"{source_real_cost_tracking_checklist.source_checklist_id or 'none'}",
                    "- source_checklist_source_checklist_source_checklist_status: "
                    f"{source_real_cost_tracking_checklist.source_checklist_status}",
                ]
            )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local remote worker proof checklist.",
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


def render_remote_worker_proof_checklist_line(
    checklist: RemoteWorkerProofChecklist,
) -> str:
    return (
        f"- {checklist.id}: status={checklist.status} "
        f"source_checklist={checklist.source_checklist_id or 'none'} "
        f"source_status={checklist.source_checklist_status} "
        f"checklist_items={checklist.checklist_count} "
        f"blocked_worker_proofs={checklist.blocked_worker_proof_count} "
        f"operator_reviews_required={checklist.operator_review_required_count} "
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
        f"recommended_worker_action={item['recommended_worker_action']}",
        f"worker_state={item['worker_state']}",
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
        "source_scheduling_action",
        "source_scheduling_state",
        "source_worker_action",
        "source_worker_state",
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
            f"worker_effect={item['worker_effect']}",
            f"routing_effect={item['routing_effect']}",
        ]
    )
    return " ".join(parts)


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _checklist_from_latest_dashboard_proof(
    *,
    storage: Storage,
    source_checklist: HostedDashboardProofChecklist | None,
    report_path: str,
) -> RemoteWorkerProofChecklist:
    if source_checklist is None:
        return storage.record_remote_worker_proof_checklist(
            status=HOSTED_DASHBOARD_PROOF_CHECKLIST_MISSING,
            source_checklist_id=None,
            source_checklist_status="none",
            capability_count=0,
            checklist_count=0,
            blocked_worker_proof_count=0,
            operator_review_required_count=0,
            blocked_dashboard_proof_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["hosted-dashboard-proof-checklist"],
            reason="No hosted dashboard proof checklist exists yet.",
            checklist_items=[],
            report_path=report_path,
        )

    if (
        source_checklist.status != "operator_hosted_dashboard_review_required"
        and not source_checklist.checklist_items
        and source_checklist.recommended_commands
    ):
        return storage.record_remote_worker_proof_checklist(
            status=HOSTED_DASHBOARD_PROOF_CHECKLIST_MISSING,
            source_checklist_id=source_checklist.id,
            source_checklist_status=source_checklist.status,
            capability_count=0,
            checklist_count=0,
            blocked_worker_proof_count=0,
            operator_review_required_count=0,
            blocked_dashboard_proof_count=0,
            blocked_cost_tracking_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=source_checklist.recommended_commands,
            reason=(
                "Latest hosted dashboard proof checklist is incomplete; run the "
                "recommended upstream command before checking remote worker proof."
            ),
            checklist_items=[],
            report_path=report_path,
        )

    source_item = _hosted_dashboard_source_item(source_checklist)
    checklist_items = (
        [_checklist_item_from_dashboard_proof_item(source_item)]
        if source_item is not None
        else []
    )
    blocked_worker_proof_count = sum(
        1
        for item in checklist_items
        if item["recommended_worker_action"] == KEEP_REMOTE_WORKERS_DISABLED
    )
    operator_review_required_count = sum(
        1
        for item in checklist_items
        if item["recommended_worker_action"] == MANUAL_REMOTE_WORKER_REVIEW_REQUIRED
    )
    if blocked_worker_proof_count:
        status = REMOTE_WORKER_PROOF_BLOCKED
        reason = (
            "Remote worker proof remains blocked until hosted dashboard proof, "
            "cost tracking, retry review, required evidence, and operator "
            "approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_REMOTE_WORKER_REVIEW_REQUIRED
        reason = (
            "Remote worker proof is ready for manual operator review; no "
            "remote worker, routing, or claim state changes were applied."
        )
    else:
        status = NO_REMOTE_WORKER_PROOF_CANDIDATE
        reason = (
            "No remote worker proof checklist row was needed from the latest "
            "hosted dashboard proof checklist."
        )

    return storage.record_remote_worker_proof_checklist(
        status=status,
        source_checklist_id=source_checklist.id,
        source_checklist_status=source_checklist.status,
        capability_count=len(checklist_items),
        checklist_count=len(checklist_items),
        blocked_worker_proof_count=blocked_worker_proof_count,
        operator_review_required_count=operator_review_required_count,
        blocked_dashboard_proof_count=sum(
            1
            for item in checklist_items
            if item["source_dashboard_action"] == KEEP_HOSTED_DASHBOARD_DISABLED
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


def _hosted_dashboard_source_item(
    source_checklist: HostedDashboardProofChecklist,
) -> dict[str, str] | None:
    for item in source_checklist.checklist_items:
        if item["capability"] == "hosted_dashboard":
            return item
    return None


def _latest_real_cost_sourced_hosted_dashboard_proof(
    *,
    storage: Storage,
    dashboard_checklists: list[HostedDashboardProofChecklist],
) -> tuple[
    HostedDashboardProofChecklist | None,
    RealCostTrackingProofChecklist | None,
]:
    for dashboard_checklist in dashboard_checklists:
        if dashboard_checklist.source_kind != "real_cost_tracking_proof_checklist":
            continue
        real_cost_tracking_checklist = (
            storage.get_real_cost_tracking_proof_checklist(
                dashboard_checklist.source_checklist_id
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
        return dashboard_checklist, real_cost_tracking_checklist
    return None, None


def _checklist_item_from_dashboard_proof_item(item: dict[str, str]) -> dict[str, str]:
    worker_blocked = (
        item["recommended_dashboard_action"] == KEEP_HOSTED_DASHBOARD_DISABLED
    )
    checklist_item = {
        "capability": REMOTE_WORKERS,
        "proof_item": REMOTE_WORKER_PROOF_ITEM,
        "recommended_worker_action": (
            KEEP_REMOTE_WORKERS_DISABLED
            if worker_blocked
            else MANUAL_REMOTE_WORKER_REVIEW_REQUIRED
        ),
        "worker_state": WORKER_BLOCKED if worker_blocked else WORKER_REVIEW_READY,
        "source_dashboard_action": item["recommended_dashboard_action"],
        "source_dashboard_state": item["dashboard_state"],
        "source_cost_action": item["source_cost_action"],
        "cost_tracking_state": item["cost_tracking_state"],
        "source_retry_action": item["source_retry_action"],
        "source_retry_state": item["source_retry_state"],
        "source_trust_action": item["source_trust_action"],
        "source_trust_state": item["source_trust_state"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "worker_effect": NO_EFFECT,
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
        "source_scheduling_action",
        "source_scheduling_state",
        "source_worker_action",
        "source_worker_state",
    ):
        if key in item:
            checklist_item[key] = item[key]
    return checklist_item
