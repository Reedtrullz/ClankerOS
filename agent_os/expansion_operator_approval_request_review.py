from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.storage import (
    ExpansionOperatorApprovalDraft,
    ExpansionOperatorApprovalRequestReview,
    Storage,
)


APPROVAL_REQUEST_SCHEMA_REVIEW_REQUIRED = "approval_request_schema_review_required"
MISSING_OPERATOR_APPROVAL_DRAFT = "missing_operator_approval_draft"
OPERATOR_APPROVAL_DRAFT_NOT_READY = "operator_approval_draft_not_ready"
APPROVAL_DRAFT_READY = "approval_draft_ready"
SCHEMA_GAP = "approval_request_subject_not_modeled"
MISSING_APPROVAL_REQUEST_FIELDS = [
    "task_id",
    "goal_id",
    "project_id",
    "task_type",
    "risk_level",
    "policy_name",
    "policy_version",
]
REPORT_PATH = "docs/expansion-operator-approval-request-review.md"


def write_expansion_operator_approval_request_review(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalRequestReview]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    drafts = storage.list_recent_expansion_operator_approval_drafts(limit=1)
    source_draft = drafts[0] if drafts else None
    existing_approval_count = storage.count_approval_requests()

    if source_draft is None:
        status = MISSING_OPERATOR_APPROVAL_DRAFT
        source_draft_id = "none"
        source_draft_status = "none"
        source_ledger_id = "none"
        source_checklist_id = "none"
        source_index_id = "none"
        source_brief_id = "none"
        source_audit_id = "none"
        draft_request_count = 0
        recommended_next_step = "expansion-operator-approval-draft"
        review_items: list[dict[str, Any]] = []
    elif not _is_ready_source_draft(source_draft):
        status = OPERATOR_APPROVAL_DRAFT_NOT_READY
        source_draft_id = source_draft.id
        source_draft_status = source_draft.status
        source_ledger_id = source_draft.source_ledger_id
        source_checklist_id = source_draft.source_checklist_id
        source_index_id = source_draft.source_index_id
        source_brief_id = source_draft.source_brief_id
        source_audit_id = source_draft.source_audit_id
        draft_request_count = source_draft.draft_request_count
        recommended_next_step = source_draft.recommended_next_step
        review_items = []
    else:
        status = APPROVAL_REQUEST_SCHEMA_REVIEW_REQUIRED
        source_draft_id = source_draft.id
        source_draft_status = source_draft.status
        source_ledger_id = source_draft.source_ledger_id
        source_checklist_id = source_draft.source_checklist_id
        source_index_id = source_draft.source_index_id
        source_brief_id = source_draft.source_brief_id
        source_audit_id = source_draft.source_audit_id
        draft_request_count = source_draft.draft_request_count
        recommended_next_step = "approval_request_schema_decision_required"
        review_items = [_review_item(item) for item in source_draft.draft_items]

    review = storage.record_expansion_operator_approval_request_review(
        status=status,
        source_draft_id=source_draft_id,
        source_draft_status=source_draft_status,
        source_ledger_id=source_ledger_id,
        source_checklist_id=source_checklist_id,
        source_index_id=source_index_id,
        source_brief_id=source_brief_id,
        source_audit_id=source_audit_id,
        draft_request_count=draft_request_count,
        review_item_count=len(review_items),
        ready_request_count=0,
        blocked_request_count=len(review_items),
        schema_gap_count=len(review_items),
        created_approval_request_count=0,
        existing_approval_request_count=existing_approval_count,
        external_request_count=sum(
            1 for item in review_items if item["review_type"] == "external_decision"
        ),
        capability_request_count=sum(
            1 for item in review_items if item["review_type"] == "capability_approval"
        ),
        approval_boundary_count=len(
            {item["approval_boundary"] for item in review_items}
        ),
        recommended_next_step=recommended_next_step,
        review_items=review_items,
        report_path=REPORT_PATH,
    )
    report_path = root / review.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_request_review_report(review),
        encoding="utf-8",
    )
    return report_path, review


def render_expansion_operator_approval_request_review_report(
    review: ExpansionOperatorApprovalRequestReview,
) -> str:
    lines = [
        "# Expansion Operator Approval Request Review",
        "",
        f"- id: {review.id}",
        f"- status: {review.status}",
        f"- source_draft: {review.source_draft_id}",
        f"- source_status: {review.source_draft_status}",
        f"- source_ledger: {review.source_ledger_id}",
        f"- source_checklist: {review.source_checklist_id}",
        f"- source_index: {review.source_index_id}",
        f"- source_brief: {review.source_brief_id}",
        f"- source_audit: {review.source_audit_id}",
        f"- draft_requests: {review.draft_request_count}",
        f"- review_items: {review.review_item_count}",
        f"- ready_requests: {review.ready_request_count}",
        f"- blocked_requests: {review.blocked_request_count}",
        f"- schema_gaps: {review.schema_gap_count}",
        f"- created_approval_requests: {review.created_approval_request_count}",
        f"- existing_approval_requests: {review.existing_approval_request_count}",
        f"- external_requests: {review.external_request_count}",
        f"- capability_requests: {review.capability_request_count}",
        f"- approval_boundaries: {review.approval_boundary_count}",
        f"- recommended_next_step: {review.recommended_next_step}",
        f"- report_path: {review.report_path}",
        f"- created_at: {review.created_at}",
        "",
        "## Review Items",
        "",
    ]
    if review.review_items:
        lines.extend(_render_review_item_line(item) for item in review.review_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval request review.",
            "- Does not create approval_requests rows.",
            "- Does not approve decisions.",
            "- Does not take allowed actions.",
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


def render_expansion_operator_approval_request_review_line(
    review: ExpansionOperatorApprovalRequestReview,
) -> str:
    return (
        f"- {review.id}: status={review.status} "
        f"source_draft={review.source_draft_id} "
        f"source_status={review.source_draft_status} "
        f"source_ledger={review.source_ledger_id} "
        f"source_checklist={review.source_checklist_id} "
        f"source_index={review.source_index_id} "
        f"source_brief={review.source_brief_id} "
        f"source_audit={review.source_audit_id} "
        f"draft_requests={review.draft_request_count} "
        f"review_items={review.review_item_count} "
        f"ready_requests={review.ready_request_count} "
        f"blocked_requests={review.blocked_request_count} "
        f"schema_gaps={review.schema_gap_count} "
        f"created_approval_requests={review.created_approval_request_count} "
        f"existing_approval_requests={review.existing_approval_request_count} "
        f"external_requests={review.external_request_count} "
        f"capability_requests={review.capability_request_count} "
        f"approval_boundaries={review.approval_boundary_count} "
        f"recommended_next_step={review.recommended_next_step} "
        f"report={review.report_path}"
    )


def _is_ready_source_draft(source_draft: ExpansionOperatorApprovalDraft) -> bool:
    return (
        source_draft.status == APPROVAL_DRAFT_READY
        and source_draft.draft_request_count > 0
    )


def _review_item(item: dict[str, Any]) -> dict[str, Any]:
    review_item = {
        "request_state": "schema_gap",
        "creation_status": "not_created",
        "schema_gap": SCHEMA_GAP,
        "missing_approval_request_fields": MISSING_APPROVAL_REQUEST_FIELDS,
        "approval_table": "approval_requests",
        "review_type": item["review_type"],
        "approval_request_kind": item["approval_request_kind"],
        "selected_action": item["selected_action"],
        "allowed_actions": item["allowed_actions"],
        "decision": item["decision"],
        "evidence_path": item["evidence_path"],
        "evidence_status": item["evidence_status"],
        "approval_boundary": item["approval_boundary"],
        "routing_effect": "none",
    }
    if "requirement" in item:
        review_item["requirement"] = item["requirement"]
    if "evidence_id" in item:
        review_item["evidence_id"] = item["evidence_id"]
    return review_item


def _render_review_item_line(item: dict[str, Any]) -> str:
    parts = [
        f"- request_state={item['request_state']}",
        f"creation_status={item['creation_status']}",
        f"schema_gap={item['schema_gap']}",
        "missing_approval_request_fields="
        f"{','.join(item['missing_approval_request_fields'])}",
        f"review_type={item['review_type']}",
    ]
    if "requirement" in item:
        parts.append(f"requirement={item['requirement']}")
    parts.extend(
        [
            f"approval_table={item['approval_table']}",
            f"approval_request_kind={item['approval_request_kind']}",
            f"selected_action={item['selected_action']}",
            f"allowed_actions={','.join(item['allowed_actions'])}",
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
