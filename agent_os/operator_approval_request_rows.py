from __future__ import annotations

from pathlib import Path

from agent_os.expansion_operator_approval_draft import APPROVAL_DRAFT_READY
from agent_os.operator_approval_schema_migration import (
    APPLICATION_ALREADY_APPLIED,
    APPLICATION_APPLIED,
)
from agent_os.storage import (
    ExpansionOperatorApprovalDraft,
    OperatorApprovalRequest,
    OperatorApprovalRequestRowApplication,
    OperatorApprovalSchemaMigrationApplication,
    Storage,
)


APPLICATION_ROWS_APPLIED = "operator_approval_request_rows_applied"
APPLICATION_ROWS_ALREADY_APPLIED = "operator_approval_request_rows_already_applied"
APPLICATION_ROWS_NOT_APPROVED = "operator_approval_request_rows_not_approved"
APPLICATION_ROWS_DRAFT_MISSING = "operator_approval_request_rows_draft_missing"
APPLICATION_ROWS_DRAFT_NOT_READY = "operator_approval_request_rows_draft_not_ready"
APPLICATION_ROWS_SCHEMA_MISSING = "operator_approval_request_rows_schema_missing"
APPLICATION_ROWS_SCHEMA_NOT_READY = "operator_approval_request_rows_schema_not_ready"
POLICY_NAME = "operator_approval_request_row_policy"
POLICY_VERSION = "v1"
REPORT_PATH = "docs/expansion-operator-approval-request-rows-application.md"


def apply_operator_approval_request_rows(
    root: Path,
    *,
    operator_id: str,
    selected_action: str,
    selection_note: str,
    evidence_reference: str,
) -> tuple[Path, OperatorApprovalRequestRowApplication]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    drafts = storage.list_recent_expansion_operator_approval_drafts(limit=1)
    draft = drafts[0] if drafts else None
    schema_applications = (
        storage.list_recent_operator_approval_schema_migration_applications(limit=1)
    )
    schema_application = schema_applications[0] if schema_applications else None

    created_requests: list[OperatorApprovalRequest] = []
    existing_operator_approval_request_count = 0

    if draft is None:
        status = APPLICATION_ROWS_DRAFT_MISSING
        draft = _empty_draft()
    elif draft.status != APPROVAL_DRAFT_READY:
        status = APPLICATION_ROWS_DRAFT_NOT_READY
    elif not storage.operator_approval_requests_table_exists():
        status = APPLICATION_ROWS_SCHEMA_MISSING
    elif schema_application is None:
        status = APPLICATION_ROWS_SCHEMA_MISSING
        schema_application = _empty_schema_application()
    elif schema_application.status not in {
        APPLICATION_APPLIED,
        APPLICATION_ALREADY_APPLIED,
    }:
        status = APPLICATION_ROWS_SCHEMA_NOT_READY
    elif selected_action != "approve":
        status = APPLICATION_ROWS_NOT_APPROVED
        existing_operator_approval_request_count = storage.count_operator_approval_requests(
            source_draft_id=draft.id,
        )
    else:
        existing_operator_approval_request_count = storage.count_operator_approval_requests(
            source_draft_id=draft.id,
        )
        if existing_operator_approval_request_count:
            status = APPLICATION_ROWS_ALREADY_APPLIED
        else:
            created_requests = storage.create_operator_approval_requests_from_draft(
                draft=draft,
                operator_id=operator_id,
                policy_name=POLICY_NAME,
                policy_version=POLICY_VERSION,
            )
            status = APPLICATION_ROWS_APPLIED if created_requests else APPLICATION_ROWS_SCHEMA_MISSING

    if schema_application is None:
        schema_application = _empty_schema_application()

    application = storage.record_operator_approval_request_row_application(
        status=status,
        source_draft_id=draft.id,
        source_draft_status=draft.status,
        source_schema_application_id=schema_application.id,
        source_schema_application_status=schema_application.status,
        source_ledger_id=draft.source_ledger_id,
        source_checklist_id=draft.source_checklist_id,
        source_index_id=draft.source_index_id,
        source_brief_id=draft.source_brief_id,
        source_audit_id=draft.source_audit_id,
        operator_id=operator_id,
        selected_action=selected_action,
        selection_note=selection_note,
        evidence_reference=evidence_reference,
        draft_request_count=draft.draft_request_count,
        operator_approval_row_count=len(created_requests),
        created_approval_request_count=0,
        existing_operator_approval_request_count=existing_operator_approval_request_count,
        external_request_count=sum(
            1 for item in draft.draft_items if item.get("review_type") == "external_decision"
        ),
        capability_request_count=sum(
            1 for item in draft.draft_items if item.get("review_type") == "capability_approval"
        ),
        created_request_ids=[request.id for request in created_requests],
        report_path=REPORT_PATH,
    )
    report_path = root / application.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_operator_approval_request_rows_application_report(
            application,
            created_requests,
        ),
        encoding="utf-8",
    )
    return report_path, application


def render_operator_approval_request_rows_application_line(
    application: OperatorApprovalRequestRowApplication,
) -> str:
    return (
        f"- {application.id}: status={application.status} "
        f"source_draft={application.source_draft_id} "
        f"source_schema_application={application.source_schema_application_id} "
        f"operator_id={application.operator_id} "
        f"selected_action={application.selected_action} "
        f"draft_requests={application.draft_request_count} "
        f"operator_approval_rows_created={application.operator_approval_row_count} "
        f"approval_requests_created={application.created_approval_request_count} "
        f"existing_operator_approval_requests={application.existing_operator_approval_request_count} "
        f"external_requests={application.external_request_count} "
        f"capability_requests={application.capability_request_count} "
        f"report={application.report_path}"
    )


def render_operator_approval_request_rows_application_report(
    application: OperatorApprovalRequestRowApplication,
    created_requests: list[OperatorApprovalRequest],
) -> str:
    lines = [
        "# Expansion Operator Approval Request Rows Application",
        "",
        f"- id: {application.id}",
        f"- status: {application.status}",
        f"- source_draft: {application.source_draft_id}",
        f"- source_status: {application.source_draft_status}",
        f"- source_schema_application: {application.source_schema_application_id}",
        f"- source_schema_status: {application.source_schema_application_status}",
        f"- source_ledger: {application.source_ledger_id}",
        f"- source_checklist: {application.source_checklist_id}",
        f"- source_index: {application.source_index_id}",
        f"- source_brief: {application.source_brief_id}",
        f"- source_audit: {application.source_audit_id}",
        f"- operator_id: {application.operator_id}",
        f"- selected_action: {application.selected_action}",
        f"- selection_note: {application.selection_note}",
        f"- evidence_reference: {application.evidence_reference}",
        f"- draft_requests: {application.draft_request_count}",
        f"- operator_approval_rows_created: {application.operator_approval_row_count}",
        f"- approval_requests_created: {application.created_approval_request_count}",
        f"- existing_operator_approval_requests: {application.existing_operator_approval_request_count}",
        f"- external_requests: {application.external_request_count}",
        f"- capability_requests: {application.capability_request_count}",
        f"- report_path: {application.report_path}",
        f"- created_at: {application.created_at}",
        "",
        "## Created Operator Approval Requests",
        "",
    ]
    if created_requests:
        lines.extend(_render_request_line(request) for request in created_requests)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not create legacy approval_requests rows.",
            "- Does not approve decisions.",
            "- Does not enable capability promotion.",
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
        f"allowed_actions={','.join(request.allowed_actions)} "
        f"evidence_path={request.evidence_path}"
    )


def _empty_draft() -> ExpansionOperatorApprovalDraft:
    return ExpansionOperatorApprovalDraft(
        id="none",
        status="none",
        source_ledger_id="none",
        source_ledger_status="none",
        source_checklist_id="none",
        source_index_id="none",
        source_brief_id="none",
        source_audit_id="none",
        draft_item_count=0,
        draft_request_count=0,
        created_approval_request_count=0,
        external_draft_count=0,
        capability_draft_count=0,
        approval_boundary_count=0,
        pending_decision_count=0,
        allowed_actions=[],
        recommended_next_step="expansion-operator-approval-draft",
        draft_items=[],
        report_path="none",
        created_at="none",
    )


def _empty_schema_application() -> OperatorApprovalSchemaMigrationApplication:
    return OperatorApprovalSchemaMigrationApplication(
        id="none",
        status="none",
        source_template_id="none",
        source_template_status="none",
        source_packet_id="none",
        source_checklist_id="none",
        source_ledger_id="none",
        source_request_id="none",
        source_plan_id="none",
        source_decision_id="none",
        source_review_id="none",
        target_table="none",
        operator_id="none",
        selected_action="none",
        selection_note="none",
        evidence_reference="none",
        inputs_recorded_count=0,
        missing_required_input_count=0,
        actions_taken_count=0,
        migration_applied_count=0,
        table_created_count=0,
        operator_approval_row_count=0,
        created_approval_request_count=0,
        existing_approval_request_count=0,
        applied_table_columns=[],
        applied_indexes=[],
        report_path="none",
        created_at="none",
    )

