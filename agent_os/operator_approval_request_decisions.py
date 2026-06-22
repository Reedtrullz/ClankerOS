from __future__ import annotations

from pathlib import Path

from agent_os.operator_approval_request_rows import (
    APPLICATION_ROWS_ALREADY_APPLIED,
    APPLICATION_ROWS_APPLIED,
)
from agent_os.storage import (
    OperatorApprovalRequest,
    OperatorApprovalRequestDecision,
    OperatorApprovalRequestRowApplication,
    Storage,
)


DECISIONS_RECORDED = "operator_approval_request_decisions_recorded"
DECISIONS_ALREADY_RECORDED = "operator_approval_request_decisions_already_recorded"
DECISIONS_ROWS_MISSING = "operator_approval_request_decisions_rows_missing"
DECISIONS_ROWS_NOT_READY = "operator_approval_request_decisions_rows_not_ready"
REPORT_PATH = "docs/expansion-operator-approval-request-decisions.md"
DECIDED_STATUSES = ["approved", "deferred", "more_evidence_requested"]


def decide_operator_approval_requests(
    root: Path,
    *,
    operator_id: str,
    selected_action: str,
    selection_note: str,
    evidence_reference: str,
) -> tuple[Path, OperatorApprovalRequestDecision]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    row_applications = storage.list_recent_operator_approval_request_row_applications(
        limit=1,
    )
    row_application = row_applications[0] if row_applications else None
    decided_requests: list[OperatorApprovalRequest] = []

    if row_application is None:
        row_application = _empty_row_application()
        pending_before = 0
        pending_after = 0
        existing_decisions = 0
        status = DECISIONS_ROWS_MISSING
    elif row_application.status not in {
        APPLICATION_ROWS_APPLIED,
        APPLICATION_ROWS_ALREADY_APPLIED,
    }:
        pending_before = 0
        pending_after = 0
        existing_decisions = 0
        status = DECISIONS_ROWS_NOT_READY
    else:
        pending_before = storage.count_operator_approval_requests_with_status(
            source_draft_id=row_application.source_draft_id,
            statuses=["pending"],
        )
        existing_decisions = storage.count_operator_approval_requests_with_status(
            source_draft_id=row_application.source_draft_id,
            statuses=DECIDED_STATUSES,
        )
        if pending_before:
            decided_requests = storage.decide_pending_operator_approval_requests(
                source_draft_id=row_application.source_draft_id,
                selected_action=selected_action,
                decided_by=operator_id,
                decision_note=selection_note,
            )
            status = DECISIONS_RECORDED
        else:
            status = DECISIONS_ALREADY_RECORDED
        pending_after = storage.count_operator_approval_requests_with_status(
            source_draft_id=row_application.source_draft_id,
            statuses=["pending"],
        )

    decision_count = len(decided_requests)
    approved_count = _decision_count_for_action(selected_action, "approve", decision_count)
    deferred_count = _decision_count_for_action(selected_action, "defer", decision_count)
    more_evidence_count = _decision_count_for_action(
        selected_action,
        "request_more_evidence",
        decision_count,
    )
    external_count = sum(
        1 for request in decided_requests if request.subject_type == "external_decision"
    )
    capability_count = sum(
        1 for request in decided_requests if request.subject_type == "capability_approval"
    )
    if not decided_requests and row_application.id != "none":
        existing_requests = storage.list_operator_approval_requests(
            source_draft_id=row_application.source_draft_id,
        )
        external_count = sum(
            1 for request in existing_requests if request.subject_type == "external_decision"
        )
        capability_count = sum(
            1 for request in existing_requests if request.subject_type == "capability_approval"
        )

    decision = storage.record_operator_approval_request_decision(
        status=status,
        source_row_application_id=row_application.id,
        source_row_application_status=row_application.status,
        source_draft_id=row_application.source_draft_id,
        source_schema_application_id=row_application.source_schema_application_id,
        source_ledger_id=row_application.source_ledger_id,
        source_checklist_id=row_application.source_checklist_id,
        source_index_id=row_application.source_index_id,
        source_brief_id=row_application.source_brief_id,
        source_audit_id=row_application.source_audit_id,
        operator_id=operator_id,
        selected_action=selected_action,
        selection_note=selection_note,
        evidence_reference=evidence_reference,
        pending_request_count_before=pending_before,
        decision_count=decision_count,
        approved_decision_count=approved_count,
        deferred_decision_count=deferred_count,
        more_evidence_decision_count=more_evidence_count,
        pending_request_count_after=pending_after,
        existing_decision_count=existing_decisions,
        created_approval_request_count=0,
        external_request_count=external_count,
        capability_request_count=capability_count,
        decided_request_ids=[request.id for request in decided_requests],
        report_path=REPORT_PATH,
    )
    report_path = root / decision.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_operator_approval_request_decision_report(decision, decided_requests),
        encoding="utf-8",
    )
    return report_path, decision


def render_operator_approval_request_decision_line(
    decision: OperatorApprovalRequestDecision,
) -> str:
    return (
        f"- {decision.id}: status={decision.status} "
        f"source_row_application={decision.source_row_application_id} "
        f"operator_id={decision.operator_id} "
        f"selected_action={decision.selected_action} "
        f"pending_requests_before={decision.pending_request_count_before} "
        f"decisions_recorded={decision.decision_count} "
        f"approved_decisions={decision.approved_decision_count} "
        f"deferred_decisions={decision.deferred_decision_count} "
        f"more_evidence_decisions={decision.more_evidence_decision_count} "
        f"pending_requests_after={decision.pending_request_count_after} "
        f"existing_decisions={decision.existing_decision_count} "
        f"approval_requests_created={decision.created_approval_request_count} "
        f"external_requests={decision.external_request_count} "
        f"capability_requests={decision.capability_request_count} "
        f"report={decision.report_path}"
    )


def render_operator_approval_request_decision_report(
    decision: OperatorApprovalRequestDecision,
    decided_requests: list[OperatorApprovalRequest],
) -> str:
    lines = [
        "# Expansion Operator Approval Request Decisions",
        "",
        f"- id: {decision.id}",
        f"- status: {decision.status}",
        f"- source_row_application: {decision.source_row_application_id}",
        f"- source_row_application_status: {decision.source_row_application_status}",
        f"- source_draft: {decision.source_draft_id}",
        f"- source_schema_application: {decision.source_schema_application_id}",
        f"- source_ledger: {decision.source_ledger_id}",
        f"- source_checklist: {decision.source_checklist_id}",
        f"- source_index: {decision.source_index_id}",
        f"- source_brief: {decision.source_brief_id}",
        f"- source_audit: {decision.source_audit_id}",
        f"- operator_id: {decision.operator_id}",
        f"- selected_action: {decision.selected_action}",
        f"- selection_note: {decision.selection_note}",
        f"- evidence_reference: {decision.evidence_reference}",
        f"- pending_requests_before: {decision.pending_request_count_before}",
        f"- decisions_recorded: {decision.decision_count}",
        f"- approved_decisions: {decision.approved_decision_count}",
        f"- deferred_decisions: {decision.deferred_decision_count}",
        f"- more_evidence_decisions: {decision.more_evidence_decision_count}",
        f"- pending_requests_after: {decision.pending_request_count_after}",
        f"- existing_decisions: {decision.existing_decision_count}",
        f"- approval_requests_created: {decision.created_approval_request_count}",
        f"- external_requests: {decision.external_request_count}",
        f"- capability_requests: {decision.capability_request_count}",
        f"- report_path: {decision.report_path}",
        f"- created_at: {decision.created_at}",
        "",
        "## Decided Operator Approval Requests",
        "",
    ]
    if decided_requests:
        lines.extend(_render_request_line(request) for request in decided_requests)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not create legacy approval_requests rows.",
            "- Does not enable capabilities.",
            "- Does not promote trust, retry, schedule, route, or dispatch work.",
            "- Does not run CI or deploy.",
            "- Does not mark the active goal complete.",
            "- Does not mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def _render_request_line(request: OperatorApprovalRequest) -> str:
    return (
        f"- request={request.id} "
        f"subject_type={request.subject_type} "
        f"subject_key={request.subject_key} "
        f"request_kind={request.request_kind} "
        f"status={request.status} "
        f"selected_action={_action_for_status(request.status)} "
        f"decided_by={request.decided_by} "
        f"evidence_path={request.evidence_path}"
    )


def _decision_count_for_action(
    selected_action: str,
    expected_action: str,
    decision_count: int,
) -> int:
    return decision_count if selected_action == expected_action else 0


def _action_for_status(status: str) -> str:
    return {
        "approved": "approve",
        "deferred": "defer",
        "more_evidence_requested": "request_more_evidence",
    }.get(status, "none")


def _empty_row_application() -> OperatorApprovalRequestRowApplication:
    return OperatorApprovalRequestRowApplication(
        id="none",
        status="none",
        source_draft_id="none",
        source_draft_status="none",
        source_schema_application_id="none",
        source_schema_application_status="none",
        source_ledger_id="none",
        source_checklist_id="none",
        source_index_id="none",
        source_brief_id="none",
        source_audit_id="none",
        operator_id="none",
        selected_action="none",
        selection_note="none",
        evidence_reference="none",
        draft_request_count=0,
        operator_approval_row_count=0,
        created_approval_request_count=0,
        existing_operator_approval_request_count=0,
        external_request_count=0,
        capability_request_count=0,
        created_request_ids=[],
        report_path="none",
        created_at="none",
    )
