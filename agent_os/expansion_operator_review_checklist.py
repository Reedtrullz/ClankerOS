from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.storage import (
    ExpansionDecisionEvidenceIndex,
    ExpansionOperatorReviewChecklist,
    Storage,
)


OPERATOR_REVIEW_REQUIRED = "operator_review_required"
MISSING_EVIDENCE_INDEX = "missing_evidence_index"
ALLOWED_ACTIONS = ["approve", "defer", "request_more_evidence"]
REPORT_PATH = "docs/expansion-operator-review-checklist.md"


def write_expansion_operator_review_checklist(
    root: Path,
) -> tuple[Path, ExpansionOperatorReviewChecklist]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    indexes = storage.list_recent_expansion_decision_evidence_indexes(limit=1)
    source_index = indexes[0] if indexes else None
    review_items = _review_items(source_index)

    if source_index is None:
        status = MISSING_EVIDENCE_INDEX
        source_index_id = "none"
        source_index_status = "none"
        source_brief_id = "none"
        source_audit_id = "none"
        recommended_next_step = "expansion-decision-evidence-index"
    else:
        status = OPERATOR_REVIEW_REQUIRED
        source_index_id = source_index.id
        source_index_status = source_index.status
        source_brief_id = source_index.source_brief_id
        source_audit_id = source_index.source_audit_id
        recommended_next_step = "operator_decision_required"

    external_review_count = sum(
        1 for item in review_items if item["review_type"] == "external_decision"
    )
    capability_review_count = sum(
        1 for item in review_items if item["review_type"] == "capability_approval"
    )
    missing_evidence_link_count = sum(
        1 for item in review_items if item["evidence_path"] == "none"
    )
    checklist = storage.record_expansion_operator_review_checklist(
        status=status,
        source_index_id=source_index_id,
        source_index_status=source_index_status,
        source_brief_id=source_brief_id,
        source_audit_id=source_audit_id,
        review_item_count=len(review_items),
        decision_required_count=len(review_items),
        external_review_count=external_review_count,
        capability_review_count=capability_review_count,
        missing_evidence_link_count=missing_evidence_link_count,
        allowed_actions=ALLOWED_ACTIONS,
        recommended_next_step=recommended_next_step,
        review_items=review_items,
        report_path=REPORT_PATH,
    )
    report_path = root / checklist.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_review_checklist_report(checklist),
        encoding="utf-8",
    )
    return report_path, checklist


def render_expansion_operator_review_checklist_report(
    checklist: ExpansionOperatorReviewChecklist,
) -> str:
    lines = [
        "# Expansion Operator Review Checklist",
        "",
        f"- id: {checklist.id}",
        f"- status: {checklist.status}",
        f"- source_index: {checklist.source_index_id}",
        f"- source_status: {checklist.source_index_status}",
        f"- source_brief: {checklist.source_brief_id}",
        f"- source_audit: {checklist.source_audit_id}",
        f"- review_items: {checklist.review_item_count}",
        f"- decision_required: {checklist.decision_required_count}",
        f"- external_reviews: {checklist.external_review_count}",
        f"- capability_reviews: {checklist.capability_review_count}",
        f"- missing_evidence_links: {checklist.missing_evidence_link_count}",
        f"- allowed_actions: {format_allowed_actions(checklist.allowed_actions)}",
        f"- recommended_next_step: {checklist.recommended_next_step}",
        f"- report_path: {checklist.report_path}",
        f"- created_at: {checklist.created_at}",
        "",
        "## Review Items",
        "",
    ]
    if checklist.review_items:
        lines.extend(_render_review_item_line(item) for item in checklist.review_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator review checklist.",
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


def render_expansion_operator_review_checklist_line(
    checklist: ExpansionOperatorReviewChecklist,
) -> str:
    return (
        f"- {checklist.id}: status={checklist.status} "
        f"source_index={checklist.source_index_id} "
        f"source_status={checklist.source_index_status} "
        f"source_brief={checklist.source_brief_id} "
        f"source_audit={checklist.source_audit_id} "
        f"review_items={checklist.review_item_count} "
        f"decision_required={checklist.decision_required_count} "
        f"external_reviews={checklist.external_review_count} "
        f"capability_reviews={checklist.capability_review_count} "
        f"missing_evidence_links={checklist.missing_evidence_link_count} "
        f"allowed_actions={format_allowed_actions(checklist.allowed_actions)} "
        f"recommended_next_step={checklist.recommended_next_step} "
        f"report={checklist.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    if not actions:
        return "none"
    return ",".join(actions)


def _review_items(
    source_index: ExpansionDecisionEvidenceIndex | None,
) -> list[dict[str, Any]]:
    if source_index is None:
        return []
    return [_review_item(item) for item in source_index.evidence_items]


def _review_item(item: dict[str, Any]) -> dict[str, Any]:
    if item["decision_type"] == "external_decision":
        return {
            "review_type": "external_decision",
            "operator_action_required": "choose_policy_or_defer",
            "allowed_actions": ALLOWED_ACTIONS,
            "decision": item["decision"],
            "evidence_path": item["evidence_path"],
            "evidence_status": item["evidence_status"],
            "approval_boundary": item["approval_boundary"],
            "routing_effect": "none",
        }
    return {
        "review_type": "capability_approval",
        "requirement": item["requirement"],
        "operator_action_required": "approve_defer_or_request_more_evidence",
        "allowed_actions": ALLOWED_ACTIONS,
        "decision": item["decision"],
        "evidence_path": item["evidence_path"],
        "evidence_id": item["evidence_id"],
        "evidence_status": item["evidence_status"],
        "completion_state": item["completion_state"],
        "missing_evidence_count": item["missing_evidence_count"],
        "approval_required_count": item["approval_required_count"],
        "approval_boundary": item["approval_boundary"],
        "routing_effect": "none",
    }


def _render_review_item_line(item: dict[str, Any]) -> str:
    allowed_actions = format_allowed_actions(item["allowed_actions"])
    if item["review_type"] == "external_decision":
        return (
            f"- review_type=external_decision "
            f"operator_action_required={item['operator_action_required']} "
            f"allowed_actions={allowed_actions} "
            f"evidence_path={item['evidence_path']} "
            f"evidence_status={item['evidence_status']} "
            f"approval_boundary={item['approval_boundary']} "
            f"routing_effect={item['routing_effect']} "
            f"decision={item['decision']}"
        )
    return (
        f"- review_type=capability_approval "
        f"requirement={item['requirement']} "
        f"operator_action_required={item['operator_action_required']} "
        f"allowed_actions={allowed_actions} "
        f"evidence_path={item['evidence_path']} "
        f"evidence_id={item['evidence_id']} "
        f"evidence_status={item['evidence_status']} "
        f"completion_state={item['completion_state']} "
        f"missing_evidence={item['missing_evidence_count']} "
        f"approvals_required={item['approval_required_count']} "
        f"approval_boundary={item['approval_boundary']} "
        f"routing_effect={item['routing_effect']} "
        f"decision={item['decision']}"
    )
