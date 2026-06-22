from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.storage import (
    ExpansionOperatorDecisionLedger,
    ExpansionOperatorReviewChecklist,
    Storage,
)


PENDING_OPERATOR_DECISIONS = "pending_operator_decisions"
MISSING_OPERATOR_REVIEW_CHECKLIST = "missing_operator_review_checklist"
REPORT_PATH = "docs/expansion-operator-decision-ledger.md"


def write_expansion_operator_decision_ledger(
    root: Path,
) -> tuple[Path, ExpansionOperatorDecisionLedger]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    checklists = storage.list_recent_expansion_operator_review_checklists(limit=1)
    source_checklist = checklists[0] if checklists else None
    decision_items = _decision_items(source_checklist)

    if source_checklist is None:
        status = MISSING_OPERATOR_REVIEW_CHECKLIST
        source_checklist_id = "none"
        source_checklist_status = "none"
        source_index_id = "none"
        source_brief_id = "none"
        source_audit_id = "none"
        allowed_actions: list[str] = []
        recommended_next_step = "expansion-operator-review-checklist"
    else:
        status = PENDING_OPERATOR_DECISIONS
        source_checklist_id = source_checklist.id
        source_checklist_status = source_checklist.status
        source_index_id = source_checklist.source_index_id
        source_brief_id = source_checklist.source_brief_id
        source_audit_id = source_checklist.source_audit_id
        allowed_actions = source_checklist.allowed_actions
        recommended_next_step = "operator_decision_required"

    pending_decision_count = sum(
        1
        for item in decision_items
        if item["decision_state"] == "pending_operator_decision"
    )
    ledger = storage.record_expansion_operator_decision_ledger(
        status=status,
        source_checklist_id=source_checklist_id,
        source_checklist_status=source_checklist_status,
        source_index_id=source_index_id,
        source_brief_id=source_brief_id,
        source_audit_id=source_audit_id,
        decision_item_count=len(decision_items),
        pending_decision_count=pending_decision_count,
        approved_decision_count=0,
        deferred_decision_count=0,
        more_evidence_requested_count=0,
        external_decision_count=sum(
            1 for item in decision_items if item["review_type"] == "external_decision"
        ),
        capability_decision_count=sum(
            1
            for item in decision_items
            if item["review_type"] == "capability_approval"
        ),
        allowed_actions=allowed_actions,
        recommended_next_step=recommended_next_step,
        decision_items=decision_items,
        report_path=REPORT_PATH,
    )
    report_path = root / ledger.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_decision_ledger_report(ledger),
        encoding="utf-8",
    )
    return report_path, ledger


def render_expansion_operator_decision_ledger_report(
    ledger: ExpansionOperatorDecisionLedger,
) -> str:
    lines = [
        "# Expansion Operator Decision Ledger",
        "",
        f"- id: {ledger.id}",
        f"- status: {ledger.status}",
        f"- source_checklist: {ledger.source_checklist_id}",
        f"- source_status: {ledger.source_checklist_status}",
        f"- source_index: {ledger.source_index_id}",
        f"- source_brief: {ledger.source_brief_id}",
        f"- source_audit: {ledger.source_audit_id}",
        f"- decision_items: {ledger.decision_item_count}",
        f"- pending_decisions: {ledger.pending_decision_count}",
        f"- approved_decisions: {ledger.approved_decision_count}",
        f"- deferred_decisions: {ledger.deferred_decision_count}",
        f"- more_evidence_requested: {ledger.more_evidence_requested_count}",
        f"- external_decisions: {ledger.external_decision_count}",
        f"- capability_decisions: {ledger.capability_decision_count}",
        f"- allowed_actions: {format_allowed_actions(ledger.allowed_actions)}",
        f"- recommended_next_step: {ledger.recommended_next_step}",
        f"- report_path: {ledger.report_path}",
        f"- created_at: {ledger.created_at}",
        "",
        "## Decision Items",
        "",
    ]
    if ledger.decision_items:
        lines.extend(_render_decision_item_line(item) for item in ledger.decision_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator decision ledger.",
            "- Does not approve decisions.",
            "- Does not collect evidence automatically.",
            "- Does not mark the active goal complete.",
            "- Does not enable or deploy hosted dashboard.",
            "- Does not start or claim remote work.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not retry or replay work.",
            "- Does not track real spend.",
            "- Does not change routing or claims.",
            "- Does not mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_expansion_operator_decision_ledger_line(
    ledger: ExpansionOperatorDecisionLedger,
) -> str:
    return (
        f"- {ledger.id}: status={ledger.status} "
        f"source_checklist={ledger.source_checklist_id} "
        f"source_status={ledger.source_checklist_status} "
        f"source_index={ledger.source_index_id} "
        f"source_brief={ledger.source_brief_id} "
        f"source_audit={ledger.source_audit_id} "
        f"decision_items={ledger.decision_item_count} "
        f"pending_decisions={ledger.pending_decision_count} "
        f"approved_decisions={ledger.approved_decision_count} "
        f"deferred_decisions={ledger.deferred_decision_count} "
        f"more_evidence_requested={ledger.more_evidence_requested_count} "
        f"external_decisions={ledger.external_decision_count} "
        f"capability_decisions={ledger.capability_decision_count} "
        f"allowed_actions={format_allowed_actions(ledger.allowed_actions)} "
        f"recommended_next_step={ledger.recommended_next_step} "
        f"report={ledger.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    if not actions:
        return "none"
    return ",".join(actions)


def _decision_items(
    source_checklist: ExpansionOperatorReviewChecklist | None,
) -> list[dict[str, Any]]:
    if source_checklist is None:
        return []
    return [_decision_item(item) for item in source_checklist.review_items]


def _decision_item(item: dict[str, Any]) -> dict[str, Any]:
    decision_item = {
        "decision_state": "pending_operator_decision",
        "selected_action": "pending",
        "review_type": item["review_type"],
        "allowed_actions": item["allowed_actions"],
        "decision": item["decision"],
        "evidence_path": item["evidence_path"],
        "evidence_status": item["evidence_status"],
        "approval_boundary": item["approval_boundary"],
        "routing_effect": item["routing_effect"],
    }
    if "requirement" in item:
        decision_item["requirement"] = item["requirement"]
    if "evidence_id" in item:
        decision_item["evidence_id"] = item["evidence_id"]
    return decision_item


def _render_decision_item_line(item: dict[str, Any]) -> str:
    allowed_actions = format_allowed_actions(item["allowed_actions"])
    parts = [
        f"- decision_state={item['decision_state']}",
        f"selected_action={item['selected_action']}",
        f"review_type={item['review_type']}",
    ]
    if "requirement" in item:
        parts.append(f"requirement={item['requirement']}")
    parts.extend(
        [
            f"allowed_actions={allowed_actions}",
            f"evidence_path={item['evidence_path']}",
            f"evidence_status={item['evidence_status']}",
            f"approval_boundary={item['approval_boundary']}",
            f"routing_effect={item['routing_effect']}",
            f"decision={item['decision']}",
        ]
    )
    if "evidence_id" in item:
        parts.insert(-4, f"evidence_id={item['evidence_id']}")
    return " ".join(parts)
