from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityPromotionDecisionLedger,
    CapabilityPromotionGateChecklist,
    Storage,
)


PROMOTION_GATE_CHECKLIST_MISSING = "promotion_gate_checklist_missing"
PROMOTION_DECISION_BLOCKED = "promotion_decision_blocked"
OPERATOR_DECISION_REQUIRED = "operator_decision_required"
NO_PROMOTION_DECISIONS_NEEDED = "no_promotion_decisions_needed"
DEFER_PROMOTION = "defer_promotion"
MANUAL_OPERATOR_REVIEW_REQUIRED = "manual_operator_review_required"
DECISION_BLOCKED = "blocked_until_evidence_and_operator_approval"
READY_FOR_OPERATOR_DECISION = "ready_for_operator_promotion_decision"
PROMOTION_GATE_BLOCKED = "blocked_until_evidence_and_operator_approval"
APPROVAL_REQUIRED = "approval_required"
EVIDENCE_MISSING = "missing"
NO_EFFECT = "none"
REPORT_PATH = "docs/capability-promotion-decision-ledger.md"


def write_capability_promotion_decision_ledger(
    root: Path,
) -> tuple[Path, CapabilityPromotionDecisionLedger]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    checklists = storage.list_recent_capability_promotion_gate_checklists(limit=1)
    source_checklist = checklists[0] if checklists else None
    ledger = _ledger_from_latest_checklist(
        storage=storage,
        source_checklist=source_checklist,
        report_path=REPORT_PATH,
    )
    report_path = root / ledger.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_promotion_decision_ledger_report(
            ledger,
            source_checklist,
        ),
        encoding="utf-8",
    )
    return report_path, ledger


def render_capability_promotion_decision_ledger_report(
    ledger: CapabilityPromotionDecisionLedger,
    source_checklist: CapabilityPromotionGateChecklist | None,
) -> str:
    lines = [
        "# Capability Promotion Decision Ledger",
        "",
        f"- id: {ledger.id}",
        f"- status: {ledger.status}",
        f"- source_checklist_id: {ledger.source_checklist_id or 'none'}",
        f"- source_checklist_status: {ledger.source_checklist_status}",
        f"- capability_count: {ledger.capability_count}",
        f"- decisions: {ledger.decision_count}",
        f"- deferred_promotions: {ledger.deferred_promotion_count}",
        f"- operator_decisions_required: {ledger.operator_decision_required_count}",
        f"- blocked_promotions: {ledger.blocked_promotion_count}",
        f"- missing_evidence: {ledger.missing_evidence_count}",
        f"- approvals_required: {ledger.approval_required_count}",
        f"- boundaries: {ledger.boundary_count}",
        f"- recommended_commands: {format_recommended_commands(ledger.recommended_commands)}",
        f"- report_path: {ledger.report_path}",
        f"- created_at: {ledger.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {ledger.reason}",
        "",
        "## Promotion Decisions",
        "",
    ]
    if ledger.decision_items:
        lines.extend(render_decision_item_line(item) for item in ledger.decision_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Promotion Gate Checklist", ""])
    if source_checklist is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_checklist.id}",
                f"- status: {source_checklist.status}",
                f"- gates: {source_checklist.gate_count}",
                f"- blocked_promotions: {source_checklist.blocked_promotion_count}",
                f"- missing_evidence: {source_checklist.missing_evidence_count}",
                f"- approvals_required: {source_checklist.approval_required_count}",
                f"- report: {source_checklist.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local promotion decision ledger.",
            "- Does not create promotion gate checklists as a side effect.",
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


def render_capability_promotion_decision_ledger_line(
    ledger: CapabilityPromotionDecisionLedger,
) -> str:
    return (
        f"- {ledger.id}: status={ledger.status} "
        f"source_checklist={ledger.source_checklist_id or 'none'} "
        f"source_status={ledger.source_checklist_status} "
        f"decisions={ledger.decision_count} "
        f"deferred_promotions={ledger.deferred_promotion_count} "
        f"operator_decisions_required={ledger.operator_decision_required_count} "
        f"blocked_promotions={ledger.blocked_promotion_count} "
        f"missing_evidence={ledger.missing_evidence_count} "
        f"approvals_required={ledger.approval_required_count} "
        f"boundaries={ledger.boundary_count} "
        f"recommended_commands={format_recommended_commands(ledger.recommended_commands)} "
        f"report={ledger.report_path}"
    )


def render_decision_item_line(item: dict[str, str]) -> str:
    return (
        f"- {item['capability']}: recommended_decision={item['recommended_decision']} "
        f"decision_state={item['decision_state']} "
        f"promotion_gate={item['promotion_gate']} "
        f"evidence_state={item['evidence_state']} "
        f"approval_state={item['approval_state']} "
        f"approval_boundary={item['approval_boundary']} "
        f"decision_effect={item['decision_effect']} "
        f"routing_effect={item['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _ledger_from_latest_checklist(
    *,
    storage: Storage,
    source_checklist: CapabilityPromotionGateChecklist | None,
    report_path: str,
) -> CapabilityPromotionDecisionLedger:
    if source_checklist is None:
        return storage.record_capability_promotion_decision_ledger(
            status=PROMOTION_GATE_CHECKLIST_MISSING,
            source_checklist_id=None,
            source_checklist_status="none",
            capability_count=0,
            decision_count=0,
            deferred_promotion_count=0,
            operator_decision_required_count=0,
            blocked_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["capability-promotion-gate-checklist"],
            reason="No capability promotion gate checklist exists yet.",
            decision_items=[],
            report_path=report_path,
        )

    if (
        source_checklist.status != "promotion_ready"
        and not source_checklist.checklist_items
        and source_checklist.recommended_commands
    ):
        return storage.record_capability_promotion_decision_ledger(
            status=PROMOTION_GATE_CHECKLIST_MISSING,
            source_checklist_id=source_checklist.id,
            source_checklist_status=source_checklist.status,
            capability_count=source_checklist.capability_count,
            decision_count=0,
            deferred_promotion_count=0,
            operator_decision_required_count=0,
            blocked_promotion_count=source_checklist.blocked_promotion_count,
            missing_evidence_count=source_checklist.missing_evidence_count,
            approval_required_count=source_checklist.approval_required_count,
            boundary_count=source_checklist.boundary_count,
            recommended_commands=source_checklist.recommended_commands,
            reason=(
                "Latest capability promotion gate checklist is incomplete; "
                "run the recommended upstream command before recording promotion decisions."
            ),
            decision_items=[],
            report_path=report_path,
        )

    decision_items = [
        _decision_item_from_checklist_item(item)
        for item in source_checklist.checklist_items
    ]
    deferred_promotion_count = sum(
        1 for item in decision_items if item["recommended_decision"] == DEFER_PROMOTION
    )
    operator_decision_required_count = sum(
        1
        for item in decision_items
        if item["recommended_decision"] == MANUAL_OPERATOR_REVIEW_REQUIRED
    )
    if deferred_promotion_count:
        status = PROMOTION_DECISION_BLOCKED
        reason = (
            "Capability promotions remain deferred until required evidence and "
            "operator approvals are present."
        )
    elif operator_decision_required_count:
        status = OPERATOR_DECISION_REQUIRED
        reason = (
            "Promotion gates are ready for manual operator decision review; "
            "no routing or trust state changes were applied."
        )
    else:
        status = NO_PROMOTION_DECISIONS_NEEDED
        reason = "No promotion decision rows were needed from the latest checklist."

    return storage.record_capability_promotion_decision_ledger(
        status=status,
        source_checklist_id=source_checklist.id,
        source_checklist_status=source_checklist.status,
        capability_count=source_checklist.capability_count,
        decision_count=len(decision_items),
        deferred_promotion_count=deferred_promotion_count,
        operator_decision_required_count=operator_decision_required_count,
        blocked_promotion_count=source_checklist.blocked_promotion_count,
        missing_evidence_count=source_checklist.missing_evidence_count,
        approval_required_count=source_checklist.approval_required_count,
        boundary_count=source_checklist.boundary_count,
        recommended_commands=[],
        reason=reason,
        decision_items=decision_items,
        report_path=report_path,
    )


def _decision_item_from_checklist_item(item: dict[str, str]) -> dict[str, str]:
    defer_promotion = (
        item["promotion_gate"] == PROMOTION_GATE_BLOCKED
        or item["evidence_state"] == EVIDENCE_MISSING
        or item["approval_state"] == APPROVAL_REQUIRED
    )
    return {
        "capability": item["capability"],
        "recommended_decision": (
            DEFER_PROMOTION if defer_promotion else MANUAL_OPERATOR_REVIEW_REQUIRED
        ),
        "decision_state": (
            DECISION_BLOCKED if defer_promotion else READY_FOR_OPERATOR_DECISION
        ),
        "promotion_gate": item["promotion_gate"],
        "evidence_item": item["evidence_item"],
        "required_evidence": item["required_evidence"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "decision_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }
