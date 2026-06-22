from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.storage import (
    ExpansionOperatorApprovalDraft,
    ExpansionOperatorDecisionLedger,
    Storage,
)


APPROVAL_DRAFT_READY = "approval_draft_ready"
MISSING_OPERATOR_DECISION_LEDGER = "missing_operator_decision_ledger"
OPERATOR_DECISION_LEDGER_NOT_READY = "operator_decision_ledger_not_ready"
PENDING_OPERATOR_DECISIONS = "pending_operator_decisions"
REPORT_PATH = "docs/expansion-operator-approval-draft.md"


def write_expansion_operator_approval_draft(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalDraft]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    ledgers = storage.list_recent_expansion_operator_decision_ledgers(limit=1)
    source_ledger = ledgers[0] if ledgers else None

    if source_ledger is None:
        status = MISSING_OPERATOR_DECISION_LEDGER
        source_ledger_id = "none"
        source_ledger_status = "none"
        source_checklist_id = "none"
        source_index_id = "none"
        source_brief_id = "none"
        source_audit_id = "none"
        pending_decision_count = 0
        allowed_actions: list[str] = []
        recommended_next_step = "expansion-operator-decision-ledger"
        draft_items: list[dict[str, Any]] = []
    elif not _is_ready_source_ledger(source_ledger):
        status = OPERATOR_DECISION_LEDGER_NOT_READY
        source_ledger_id = source_ledger.id
        source_ledger_status = source_ledger.status
        source_checklist_id = source_ledger.source_checklist_id
        source_index_id = source_ledger.source_index_id
        source_brief_id = source_ledger.source_brief_id
        source_audit_id = source_ledger.source_audit_id
        pending_decision_count = source_ledger.pending_decision_count
        allowed_actions = source_ledger.allowed_actions
        recommended_next_step = source_ledger.recommended_next_step
        draft_items = []
    else:
        status = APPROVAL_DRAFT_READY
        source_ledger_id = source_ledger.id
        source_ledger_status = source_ledger.status
        source_checklist_id = source_ledger.source_checklist_id
        source_index_id = source_ledger.source_index_id
        source_brief_id = source_ledger.source_brief_id
        source_audit_id = source_ledger.source_audit_id
        pending_decision_count = source_ledger.pending_decision_count
        allowed_actions = source_ledger.allowed_actions
        recommended_next_step = "operator_approval_flow_required"
        draft_items = _draft_items(source_ledger)

    draft = storage.record_expansion_operator_approval_draft(
        status=status,
        source_ledger_id=source_ledger_id,
        source_ledger_status=source_ledger_status,
        source_checklist_id=source_checklist_id,
        source_index_id=source_index_id,
        source_brief_id=source_brief_id,
        source_audit_id=source_audit_id,
        draft_item_count=len(draft_items),
        draft_request_count=len(draft_items),
        created_approval_request_count=0,
        external_draft_count=sum(
            1 for item in draft_items if item["review_type"] == "external_decision"
        ),
        capability_draft_count=sum(
            1 for item in draft_items if item["review_type"] == "capability_approval"
        ),
        approval_boundary_count=len(
            {item["approval_boundary"] for item in draft_items}
        ),
        pending_decision_count=pending_decision_count,
        allowed_actions=allowed_actions,
        recommended_next_step=recommended_next_step,
        draft_items=draft_items,
        report_path=REPORT_PATH,
    )
    report_path = root / draft.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_draft_report(draft),
        encoding="utf-8",
    )
    return report_path, draft


def render_expansion_operator_approval_draft_report(
    draft: ExpansionOperatorApprovalDraft,
) -> str:
    lines = [
        "# Expansion Operator Approval Draft",
        "",
        f"- id: {draft.id}",
        f"- status: {draft.status}",
        f"- source_ledger: {draft.source_ledger_id}",
        f"- source_status: {draft.source_ledger_status}",
        f"- source_checklist: {draft.source_checklist_id}",
        f"- source_index: {draft.source_index_id}",
        f"- source_brief: {draft.source_brief_id}",
        f"- source_audit: {draft.source_audit_id}",
        f"- draft_items: {draft.draft_item_count}",
        f"- draft_requests: {draft.draft_request_count}",
        f"- created_approval_requests: {draft.created_approval_request_count}",
        f"- external_drafts: {draft.external_draft_count}",
        f"- capability_drafts: {draft.capability_draft_count}",
        f"- approval_boundaries: {draft.approval_boundary_count}",
        f"- pending_decisions: {draft.pending_decision_count}",
        f"- allowed_actions: {format_allowed_actions(draft.allowed_actions)}",
        f"- recommended_next_step: {draft.recommended_next_step}",
        f"- report_path: {draft.report_path}",
        f"- created_at: {draft.created_at}",
        "",
        "## Draft Items",
        "",
    ]
    if draft.draft_items:
        lines.extend(_render_draft_item_line(item) for item in draft.draft_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval draft.",
            "- Does not create approval_requests rows.",
            "- Does not take allowed actions.",
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


def render_expansion_operator_approval_draft_line(
    draft: ExpansionOperatorApprovalDraft,
) -> str:
    return (
        f"- {draft.id}: status={draft.status} "
        f"source_ledger={draft.source_ledger_id} "
        f"source_status={draft.source_ledger_status} "
        f"source_checklist={draft.source_checklist_id} "
        f"source_index={draft.source_index_id} "
        f"source_brief={draft.source_brief_id} "
        f"source_audit={draft.source_audit_id} "
        f"draft_items={draft.draft_item_count} "
        f"draft_requests={draft.draft_request_count} "
        f"created_approval_requests={draft.created_approval_request_count} "
        f"external_drafts={draft.external_draft_count} "
        f"capability_drafts={draft.capability_draft_count} "
        f"approval_boundaries={draft.approval_boundary_count} "
        f"pending_decisions={draft.pending_decision_count} "
        f"allowed_actions={format_allowed_actions(draft.allowed_actions)} "
        f"recommended_next_step={draft.recommended_next_step} "
        f"report={draft.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    if not actions:
        return "none"
    return ",".join(actions)


def _draft_items(
    source_ledger: ExpansionOperatorDecisionLedger | None,
) -> list[dict[str, Any]]:
    if source_ledger is None:
        return []
    return [_draft_item(item) for item in source_ledger.decision_items]


def _is_ready_source_ledger(source_ledger: ExpansionOperatorDecisionLedger) -> bool:
    return (
        source_ledger.status == PENDING_OPERATOR_DECISIONS
        and source_ledger.pending_decision_count > 0
    )


def _draft_item(item: dict[str, Any]) -> dict[str, Any]:
    draft_item = {
        "draft_state": "draft_only",
        "approval_request_status": "not_created",
        "selected_action": item["selected_action"],
        "review_type": item["review_type"],
        "approval_request_kind": _approval_request_kind(item),
        "allowed_actions": item["allowed_actions"],
        "decision": item["decision"],
        "evidence_path": item["evidence_path"],
        "evidence_status": item["evidence_status"],
        "approval_boundary": item["approval_boundary"],
        "routing_effect": "none",
    }
    if "requirement" in item:
        draft_item["requirement"] = item["requirement"]
    if "evidence_id" in item:
        draft_item["evidence_id"] = item["evidence_id"]
    return draft_item


def _approval_request_kind(item: dict[str, Any]) -> str:
    if item["review_type"] == "external_decision":
        return "external_operator_decision"
    return "capability_operator_approval"


def _render_draft_item_line(item: dict[str, Any]) -> str:
    allowed_actions = format_allowed_actions(item["allowed_actions"])
    parts = [
        f"- draft_state={item['draft_state']}",
        f"approval_request_status={item['approval_request_status']}",
        f"selected_action={item['selected_action']}",
        f"review_type={item['review_type']}",
    ]
    if "requirement" in item:
        parts.append(f"requirement={item['requirement']}")
    parts.extend(
        [
            f"approval_request_kind={item['approval_request_kind']}",
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
