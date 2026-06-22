from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.storage import (
    ExpansionDecisionBrief,
    ExpansionDecisionEvidenceIndex,
    GoalCompletionAudit,
    Storage,
)


EVIDENCE_INDEXED = "evidence_indexed"
EVIDENCE_LINKS_MISSING = "evidence_links_missing"
MISSING_EXPANSION_DECISION_BRIEF = "missing_expansion_decision_brief"
REPORT_PATH = "docs/expansion-decision-evidence-index.md"


def write_expansion_decision_evidence_index(
    root: Path,
) -> tuple[Path, ExpansionDecisionEvidenceIndex]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    briefs = storage.list_recent_expansion_decision_briefs(limit=1)
    source_brief = briefs[0] if briefs else None
    source_audit = _source_audit(storage, source_brief)
    evidence_items = _evidence_items(root, source_brief, source_audit)
    missing_evidence_link_count = sum(
        1 for item in evidence_items if item["evidence_path"] == "none"
    )

    if source_brief is None:
        status = MISSING_EXPANSION_DECISION_BRIEF
        source_brief_id = "none"
        source_brief_status = "none"
        source_audit_id = "none"
        decision_item_count = 0
        recommended_next_step = "expansion-decision-brief"
    else:
        status = (
            EVIDENCE_LINKS_MISSING
            if missing_evidence_link_count
            else EVIDENCE_INDEXED
        )
        source_brief_id = source_brief.id
        source_brief_status = source_brief.status
        source_audit_id = source_brief.source_audit_id
        decision_item_count = source_brief.decision_item_count
        recommended_next_step = source_brief.recommended_next_step

    external_decision_count = sum(
        1 for item in evidence_items if item["decision_type"] == "external_decision"
    )
    capability_decision_count = sum(
        1
        for item in evidence_items
        if item["decision_type"] == "capability_approval"
    )
    index = storage.record_expansion_decision_evidence_index(
        status=status,
        source_brief_id=source_brief_id,
        source_brief_status=source_brief_status,
        source_audit_id=source_audit_id,
        decision_item_count=decision_item_count,
        evidence_item_count=len(evidence_items),
        external_decision_count=external_decision_count,
        capability_decision_count=capability_decision_count,
        missing_evidence_link_count=missing_evidence_link_count,
        recommended_next_step=recommended_next_step,
        evidence_items=evidence_items,
        report_path=REPORT_PATH,
    )
    report_path = root / index.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_decision_evidence_index_report(index),
        encoding="utf-8",
    )
    return report_path, index


def render_expansion_decision_evidence_index_report(
    index: ExpansionDecisionEvidenceIndex,
) -> str:
    lines = [
        "# Expansion Decision Evidence Index",
        "",
        f"- id: {index.id}",
        f"- status: {index.status}",
        f"- source_brief: {index.source_brief_id}",
        f"- source_status: {index.source_brief_status}",
        f"- source_audit: {index.source_audit_id}",
        f"- decision_items: {index.decision_item_count}",
        f"- evidence_items: {index.evidence_item_count}",
        f"- external_decisions: {index.external_decision_count}",
        f"- capability_decisions: {index.capability_decision_count}",
        f"- missing_evidence_links: {index.missing_evidence_link_count}",
        f"- recommended_next_step: {index.recommended_next_step}",
        f"- report_path: {index.report_path}",
        f"- created_at: {index.created_at}",
        "",
        "## Evidence Items",
        "",
    ]
    if index.evidence_items:
        lines.extend(
            _render_evidence_item_line(item) for item in index.evidence_items
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion decision evidence index.",
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


def render_expansion_decision_evidence_index_line(
    index: ExpansionDecisionEvidenceIndex,
) -> str:
    return (
        f"- {index.id}: status={index.status} "
        f"source_brief={index.source_brief_id} "
        f"source_status={index.source_brief_status} "
        f"source_audit={index.source_audit_id} "
        f"decision_items={index.decision_item_count} "
        f"evidence_items={index.evidence_item_count} "
        f"external_decisions={index.external_decision_count} "
        f"capability_decisions={index.capability_decision_count} "
        f"missing_evidence_links={index.missing_evidence_link_count} "
        f"recommended_next_step={index.recommended_next_step} "
        f"report={index.report_path}"
    )


def _source_audit(
    storage: Storage,
    source_brief: ExpansionDecisionBrief | None,
) -> GoalCompletionAudit | None:
    if source_brief is None:
        return None
    audits = storage.list_recent_goal_completion_audits(limit=20)
    return next(
        (audit for audit in audits if audit.id == source_brief.source_audit_id),
        None,
    )


def _evidence_items(
    root: Path,
    source_brief: ExpansionDecisionBrief | None,
    source_audit: GoalCompletionAudit | None,
) -> list[dict[str, Any]]:
    if source_brief is None:
        return []

    audit_items_by_requirement = {
        item["requirement"]: item for item in source_audit.audit_items
    } if source_audit else {}
    evidence_items: list[dict[str, Any]] = []
    for item in source_brief.decision_items:
        if item["decision_type"] == "external_decision":
            evidence_items.append(_external_decision_item(root, source_brief, item))
        else:
            evidence_items.append(
                _capability_decision_item(
                    source_brief,
                    item,
                    audit_items_by_requirement.get(item["requirement"], {}),
                )
            )
    return evidence_items


def _external_decision_item(
    root: Path,
    source_brief: ExpansionDecisionBrief,
    item: dict[str, Any],
) -> dict[str, Any]:
    evidence_path = "tasks.md" if (root / "tasks.md").exists() else "none"
    return {
        "decision_type": "external_decision",
        "decision": item["decision"],
        "source_brief": source_brief.id,
        "source_audit": source_brief.source_audit_id,
        "evidence_path": evidence_path,
        "evidence_status": "blocked_task" if evidence_path != "none" else "missing",
        "approval_boundary": item["approval_boundary"],
        "routing_effect": "none",
    }


def _capability_decision_item(
    source_brief: ExpansionDecisionBrief,
    item: dict[str, Any],
    audit_item: dict[str, Any],
) -> dict[str, Any]:
    evidence_path = audit_item.get("report_path", "none") or "none"
    return {
        "decision_type": "capability_approval",
        "requirement": item["requirement"],
        "decision": item["decision"],
        "source_brief": source_brief.id,
        "source_audit": source_brief.source_audit_id,
        "evidence_id": item.get("evidence_id", audit_item.get("evidence_id", "none")),
        "evidence_status": item.get(
            "evidence_status",
            audit_item.get("evidence_status", "none"),
        ),
        "evidence_path": evidence_path,
        "completion_state": item.get(
            "completion_state",
            audit_item.get("completion_state", "unknown"),
        ),
        "missing_evidence_count": item.get(
            "missing_evidence_count",
            audit_item.get("missing_evidence_count", "0"),
        ),
        "approval_required_count": item.get(
            "approval_required_count",
            audit_item.get("approval_required_count", "0"),
        ),
        "approval_boundary": item["approval_boundary"],
        "routing_effect": "none",
    }


def _render_evidence_item_line(item: dict[str, Any]) -> str:
    if item["decision_type"] == "external_decision":
        return (
            f"- decision_type=external_decision "
            f"evidence_path={item['evidence_path']} "
            f"evidence_status={item['evidence_status']} "
            f"approval_boundary={item['approval_boundary']} "
            f"routing_effect={item['routing_effect']} "
            f"decision={item['decision']}"
        )
    return (
        f"- decision_type=capability_approval "
        f"requirement={item['requirement']} "
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
