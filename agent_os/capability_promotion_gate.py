from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityEvidenceCollectionPlan,
    CapabilityPromotionGateChecklist,
    Storage,
)


PROMOTION_BLOCKED = "promotion_blocked"
PROMOTION_READY = "promotion_ready"
EVIDENCE_COLLECTION_PLAN_MISSING = "evidence_collection_plan_missing"
PROMOTION_GATE_BLOCKED = "blocked_until_evidence_and_operator_approval"
PROMOTION_GATE_READY = "ready_for_operator_promotion_review"
APPROVAL_REQUIRED = "approval_required"
APPROVAL_NOT_REQUIRED = "approval_not_required"
EXPLICIT_APPROVAL_BOUNDARY = "explicit_operator_approval_required"
DECISION_BLOCKED = "blocked_until_proof_and_operator_approval"
REPORT_PATH = "docs/capability-promotion-gate-checklist.md"


def write_capability_promotion_gate_checklist(
    root: Path,
) -> tuple[Path, CapabilityPromotionGateChecklist]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    plans = storage.list_recent_capability_evidence_collection_plans(limit=1)
    source_plan = plans[0] if plans else None
    checklist = _checklist_from_latest_plan(
        storage=storage,
        source_plan=source_plan,
        report_path=REPORT_PATH,
    )
    report_path = root / checklist.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_promotion_gate_checklist_report(checklist, source_plan),
        encoding="utf-8",
    )
    return report_path, checklist


def render_capability_promotion_gate_checklist_report(
    checklist: CapabilityPromotionGateChecklist,
    source_plan: CapabilityEvidenceCollectionPlan | None,
) -> str:
    lines = [
        "# Capability Promotion Gate Checklist",
        "",
        f"- id: {checklist.id}",
        f"- status: {checklist.status}",
        f"- source_plan_id: {checklist.source_plan_id or 'none'}",
        f"- source_plan_status: {checklist.source_plan_status}",
        f"- capability_count: {checklist.capability_count}",
        f"- gates: {checklist.gate_count}",
        f"- blocked_promotions: {checklist.blocked_promotion_count}",
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
        "## Promotion Gates",
        "",
    ]
    if checklist.checklist_items:
        lines.extend(render_checklist_item_line(item) for item in checklist.checklist_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Evidence Collection Plan", ""])
    if source_plan is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_plan.id}",
                f"- status: {source_plan.status}",
                f"- evidence_items: {source_plan.evidence_item_count}",
                f"- manual_collection: {source_plan.manual_collection_count}",
                f"- approvals_required: {source_plan.approval_required_count}",
                f"- report: {source_plan.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local promotion gate checklist.",
            "- Does not create evidence collection plans as a side effect.",
            "- Does not create approval boundary matrices as a side effect.",
            "- Does not create proof gap indexes as a side effect.",
            "- Does not create readiness reviews as a side effect.",
            "- Does not create capability ledgers as a side effect.",
            "- Does not collect evidence automatically.",
            "- Does not approve capabilities automatically.",
            "- Does not promote capabilities automatically.",
            "- Does not generate proof artifacts automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not retry or replay work.",
            "- Does not change routing or claims.",
            "- Does not track real spend or mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_capability_promotion_gate_checklist_line(
    checklist: CapabilityPromotionGateChecklist,
) -> str:
    return (
        f"- {checklist.id}: status={checklist.status} "
        f"source_plan={checklist.source_plan_id or 'none'} "
        f"source_status={checklist.source_plan_status} "
        f"gates={checklist.gate_count} "
        f"blocked_promotions={checklist.blocked_promotion_count} "
        f"missing_evidence={checklist.missing_evidence_count} "
        f"approvals_required={checklist.approval_required_count} "
        f"boundaries={checklist.boundary_count} "
        f"recommended_commands={format_recommended_commands(checklist.recommended_commands)} "
        f"report={checklist.report_path}"
    )


def render_checklist_item_line(item: dict[str, str]) -> str:
    return (
        f"- {item['capability']}: promotion_gate={item['promotion_gate']} "
        f"evidence_item={item['evidence_item']} "
        f"required_evidence={item['required_evidence']} "
        f"evidence_state={item['evidence_state']} "
        f"approval_state={item['approval_state']} "
        f"approval_boundary={item['approval_boundary']} "
        f"routing_effect={item['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _checklist_from_latest_plan(
    *,
    storage: Storage,
    source_plan: CapabilityEvidenceCollectionPlan | None,
    report_path: str,
) -> CapabilityPromotionGateChecklist:
    if source_plan is None:
        return storage.record_capability_promotion_gate_checklist(
            status=EVIDENCE_COLLECTION_PLAN_MISSING,
            source_plan_id=None,
            source_plan_status="none",
            capability_count=0,
            gate_count=0,
            blocked_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["capability-evidence-collection-plan"],
            reason="No capability evidence collection plan exists yet.",
            checklist_items=[],
            report_path=report_path,
        )

    if (
        source_plan.status != "no_evidence_required"
        and not source_plan.evidence_items
        and source_plan.recommended_commands
    ):
        return storage.record_capability_promotion_gate_checklist(
            status=EVIDENCE_COLLECTION_PLAN_MISSING,
            source_plan_id=source_plan.id,
            source_plan_status=source_plan.status,
            capability_count=source_plan.capability_count,
            gate_count=0,
            blocked_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=source_plan.approval_required_count,
            boundary_count=source_plan.boundary_count,
            recommended_commands=source_plan.recommended_commands,
            reason=(
                "Latest capability evidence collection plan is incomplete; "
                "run the recommended upstream command before reviewing promotion gates."
            ),
            checklist_items=[],
            report_path=report_path,
        )

    checklist_items = [
        _checklist_item_from_evidence_item(item)
        for item in source_plan.evidence_items
    ]
    missing_evidence_count = sum(
        1 for item in checklist_items if item["evidence_state"] == "missing"
    )
    blocked_promotion_count = sum(
        1
        for item in checklist_items
        if item["promotion_gate"] == PROMOTION_GATE_BLOCKED
    )
    status = PROMOTION_BLOCKED if blocked_promotion_count else PROMOTION_READY
    reason = (
        "Capability promotion remains blocked until manual evidence and operator approval are present."
        if blocked_promotion_count
        else "No blocked promotion gates remain in the latest evidence collection plan."
    )
    return storage.record_capability_promotion_gate_checklist(
        status=status,
        source_plan_id=source_plan.id,
        source_plan_status=source_plan.status,
        capability_count=source_plan.capability_count,
        gate_count=len(checklist_items),
        blocked_promotion_count=blocked_promotion_count,
        missing_evidence_count=missing_evidence_count,
        approval_required_count=sum(
            1 for item in checklist_items if item["approval_state"] == APPROVAL_REQUIRED
        ),
        boundary_count=source_plan.boundary_count,
        recommended_commands=[],
        reason=reason,
        checklist_items=checklist_items,
        report_path=report_path,
    )


def _checklist_item_from_evidence_item(item: dict[str, str]) -> dict[str, str]:
    evidence_state = item["evidence_state"]
    approval_state = (
        APPROVAL_REQUIRED
        if _requires_operator_approval(item)
        else APPROVAL_NOT_REQUIRED
    )
    promotion_gate = (
        PROMOTION_GATE_BLOCKED
        if evidence_state == "missing" or approval_state == APPROVAL_REQUIRED
        else PROMOTION_GATE_READY
    )
    return {
        "capability": item["capability"],
        "promotion_gate": promotion_gate,
        "evidence_item": item["evidence_item"],
        "required_evidence": item["required_evidence"],
        "evidence_state": evidence_state,
        "approval_state": approval_state,
        "approval_boundary": item["approval_boundary"],
        "routing_effect": item["routing_effect"],
    }


def _requires_operator_approval(item: dict[str, str]) -> bool:
    return (
        item.get("approval_boundary") == EXPLICIT_APPROVAL_BOUNDARY
        or item.get("decision_state") == DECISION_BLOCKED
    )
