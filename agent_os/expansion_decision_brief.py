from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.storage import ExpansionDecisionBrief, GoalCompletionAudit, Storage


OPERATOR_DECISIONS_REQUIRED = "operator_decisions_required"
MISSING_GOAL_COMPLETION_AUDIT = "missing_goal_completion_audit"
READY_FOR_OPERATOR_REVIEW = "ready_for_operator_review"
REPORT_PATH = "docs/expansion-decision-brief.md"
APPROVAL_BOUNDARY = "explicit_operator_approval_required"
EXTERNAL_DECISION_BOUNDARY = "explicit_operator_decision_required"


def write_expansion_decision_brief(
    root: Path,
) -> tuple[Path, ExpansionDecisionBrief]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    audits = storage.list_recent_goal_completion_audits(limit=1)
    source_audit = audits[0] if audits else None
    decision_items = _decision_items(source_audit)
    if source_audit is None:
        source_audit_id = "none"
        source_audit_status = "none"
        requirement_count = 0
        blocked_requirement_count = 0
        external_decision_count = 0
        approval_required_count = 0
        status = MISSING_GOAL_COMPLETION_AUDIT
        recommended_next_step = "run_goal_completion_audit"
    else:
        source_audit_id = source_audit.id
        source_audit_status = source_audit.status
        requirement_count = source_audit.requirement_count
        blocked_requirement_count = source_audit.blocked_requirement_count
        external_decision_count = source_audit.external_decision_count
        approval_required_count = source_audit.approval_required_count
        status = (
            OPERATOR_DECISIONS_REQUIRED
            if decision_items
            else READY_FOR_OPERATOR_REVIEW
        )
        recommended_next_step = (
            "operator_review_required"
            if decision_items
            else "operator_completion_review"
        )

    brief = storage.record_expansion_decision_brief(
        status=status,
        source_audit_id=source_audit_id,
        source_audit_status=source_audit_status,
        requirement_count=requirement_count,
        blocked_requirement_count=blocked_requirement_count,
        external_decision_count=external_decision_count,
        approval_required_count=approval_required_count,
        decision_item_count=len(decision_items),
        recommended_next_step=recommended_next_step,
        decision_items=decision_items,
        report_path=REPORT_PATH,
    )
    report_path = root / brief.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_expansion_decision_brief_report(brief), encoding="utf-8")
    return report_path, brief


def render_expansion_decision_brief_report(
    brief: ExpansionDecisionBrief,
) -> str:
    lines = [
        "# Expansion Decision Brief",
        "",
        f"- id: {brief.id}",
        f"- status: {brief.status}",
        f"- source_audit: {brief.source_audit_id}",
        f"- source_status: {brief.source_audit_status}",
        f"- requirements: {brief.requirement_count}",
        f"- blocked_requirements: {brief.blocked_requirement_count}",
        f"- external_decisions_required: {brief.external_decision_count}",
        f"- approvals_required: {brief.approval_required_count}",
        f"- decision_items: {brief.decision_item_count}",
        f"- recommended_next_step: {brief.recommended_next_step}",
        f"- report_path: {brief.report_path}",
        f"- created_at: {brief.created_at}",
        "",
        "## Decision Items",
        "",
    ]
    if brief.decision_items:
        lines.extend(_render_decision_item_line(item) for item in brief.decision_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion decision brief.",
            "- Does not approve capabilities.",
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


def render_expansion_decision_brief_line(
    brief: ExpansionDecisionBrief,
) -> str:
    return (
        f"- {brief.id}: status={brief.status} "
        f"source_audit={brief.source_audit_id} "
        f"source_status={brief.source_audit_status} "
        f"requirements={brief.requirement_count} "
        f"blocked_requirements={brief.blocked_requirement_count} "
        f"external_decisions_required={brief.external_decision_count} "
        f"approvals_required={brief.approval_required_count} "
        f"decision_items={brief.decision_item_count} "
        f"recommended_next_step={brief.recommended_next_step} "
        f"report={brief.report_path}"
    )


def _decision_items(
    source_audit: GoalCompletionAudit | None,
) -> list[dict[str, Any]]:
    if source_audit is None:
        return []

    items: list[dict[str, Any]] = [
        {
            "decision_type": "external_decision",
            "decision": decision,
            "approval_boundary": EXTERNAL_DECISION_BOUNDARY,
            "routing_effect": "none",
        }
        for decision in source_audit.external_decisions
    ]
    items.extend(
        _capability_approval_item(item)
        for item in source_audit.audit_items
        if item.get("completion_state") != "proven"
        or int(item.get("approval_required_count", "0")) > 0
    )
    return items


def _capability_approval_item(item: dict[str, Any]) -> dict[str, Any]:
    requirement = str(item["requirement"])
    approval_boundary = item.get("approval_boundary") or APPROVAL_BOUNDARY
    return {
        "decision_type": "capability_approval",
        "requirement": requirement,
        "completion_state": item.get("completion_state", "unknown"),
        "evidence_id": item.get("evidence_id", "none"),
        "evidence_status": item.get("evidence_status", "none"),
        "missing_evidence_count": item.get("missing_evidence_count", "0"),
        "approval_required_count": item.get("approval_required_count", "0"),
        "approval_boundary": approval_boundary,
        "routing_effect": "none",
        "decision": (
            f"Approve or defer {requirement} after evidence and policy review."
        ),
    }


def _render_decision_item_line(item: dict[str, Any]) -> str:
    if item["decision_type"] == "external_decision":
        return (
            f"- decision_type=external_decision "
            f"decision={item['decision']} "
            f"approval_boundary={item['approval_boundary']} "
            f"routing_effect={item['routing_effect']}"
        )
    return (
        f"- decision_type=capability_approval "
        f"requirement={item['requirement']} "
        f"completion_state={item['completion_state']} "
        f"evidence_id={item['evidence_id']} "
        f"evidence_status={item['evidence_status']} "
        f"missing_evidence={item['missing_evidence_count']} "
        f"approvals_required={item['approval_required_count']} "
        f"approval_boundary={item['approval_boundary']} "
        f"routing_effect={item['routing_effect']} "
        f"decision={item['decision']}"
    )
