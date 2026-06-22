from __future__ import annotations

from pathlib import Path

from agent_os.expansion_operator_approval_schema_migration_plan import (
    TARGET_TABLE,
    _planned_columns,
    _planned_indexes,
)
from agent_os.expansion_operator_approval_schema_migration_selection_input_template import (
    OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_INPUT_REQUIRED,
)
from agent_os.storage import (
    ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate,
    OperatorApprovalSchemaMigrationApplication,
    Storage,
)


APPLICATION_APPLIED = "operator_approval_schema_migration_applied"
APPLICATION_ALREADY_APPLIED = "operator_approval_schema_migration_already_applied"
APPLICATION_NOT_APPROVED = "operator_approval_schema_migration_not_approved"
APPLICATION_TEMPLATE_MISSING = "operator_approval_schema_migration_template_missing"
APPLICATION_TEMPLATE_NOT_READY = "operator_approval_schema_migration_template_not_ready"
REPORT_PATH = "docs/expansion-operator-approval-schema-migration-application.md"


def render_operator_approval_schema_migration_application_line(
    application: OperatorApprovalSchemaMigrationApplication,
) -> str:
    return (
        f"- {application.id}: status={application.status} "
        f"source_template={application.source_template_id} "
        f"target_table={application.target_table} "
        f"operator_id={application.operator_id} "
        f"selected_action={application.selected_action} "
        f"inputs_recorded={application.inputs_recorded_count} "
        f"actions_taken={application.actions_taken_count} "
        f"migration_applied={application.migration_applied_count} "
        f"table_created={application.table_created_count} "
        f"operator_approval_rows_created={application.operator_approval_row_count} "
        f"approval_requests_created={application.created_approval_request_count} "
        f"existing_approval_requests={application.existing_approval_request_count} "
        f"report={application.report_path}"
    )


def apply_operator_approval_schema_migration(
    root: Path,
    *,
    operator_id: str,
    selected_action: str,
    selection_note: str,
    evidence_reference: str,
) -> tuple[Path, OperatorApprovalSchemaMigrationApplication]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    templates = (
        storage.list_recent_expansion_operator_approval_schema_migration_selection_input_templates(
            limit=1,
        )
    )
    source_template = templates[0] if templates else None

    columns: list[dict[str, str]] = []
    indexes: list[dict[str, object]] = []
    migration_applied_count = 0
    table_created_count = 0
    actions_taken_count = 0

    if source_template is None:
        status = APPLICATION_TEMPLATE_MISSING
        source_template = _empty_template()
    elif not _is_ready_source_template(source_template):
        status = APPLICATION_TEMPLATE_NOT_READY
    elif selected_action != "approve":
        status = APPLICATION_NOT_APPROVED
    elif storage.operator_approval_requests_table_exists():
        status = APPLICATION_ALREADY_APPLIED
        columns = _planned_columns()
        indexes = _planned_indexes()
    else:
        status = APPLICATION_APPLIED
        columns = _planned_columns()
        indexes = _planned_indexes()
        table_created, columns, indexes = storage.create_operator_approval_requests_schema(
            columns=columns,
            indexes=indexes,
        )
        migration_applied_count = 1 if table_created else 0
        table_created_count = 1 if table_created else 0
        actions_taken_count = 1 if table_created else 0
        if not table_created:
            status = APPLICATION_ALREADY_APPLIED

    application = storage.record_operator_approval_schema_migration_application(
        status=status,
        source_template_id=source_template.id,
        source_template_status=source_template.status,
        source_packet_id=source_template.source_packet_id,
        source_checklist_id=source_template.source_checklist_id,
        source_ledger_id=source_template.source_ledger_id,
        source_request_id=source_template.source_request_id,
        source_plan_id=source_template.source_plan_id,
        source_decision_id=source_template.source_decision_id,
        source_review_id=source_template.source_review_id,
        target_table=source_template.target_table,
        operator_id=operator_id,
        selected_action=selected_action,
        selection_note=selection_note,
        evidence_reference=evidence_reference,
        inputs_recorded_count=1,
        missing_required_input_count=0,
        actions_taken_count=actions_taken_count,
        migration_applied_count=migration_applied_count,
        table_created_count=table_created_count,
        operator_approval_row_count=0,
        created_approval_request_count=0,
        existing_approval_request_count=storage.count_approval_requests(),
        applied_table_columns=columns,
        applied_indexes=indexes,
        report_path=REPORT_PATH,
    )
    report_path = root / application.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_operator_approval_schema_migration_application_report(application),
        encoding="utf-8",
    )
    return report_path, application


def render_operator_approval_schema_migration_application_report(
    application: OperatorApprovalSchemaMigrationApplication,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Migration Application",
        "",
        f"- id: {application.id}",
        f"- status: {application.status}",
        f"- source_template: {application.source_template_id}",
        f"- source_status: {application.source_template_status}",
        f"- source_packet: {application.source_packet_id}",
        f"- source_checklist: {application.source_checklist_id}",
        f"- source_ledger: {application.source_ledger_id}",
        f"- source_request: {application.source_request_id}",
        f"- source_plan: {application.source_plan_id}",
        f"- source_decision: {application.source_decision_id}",
        f"- source_review: {application.source_review_id}",
        f"- target_table: {application.target_table}",
        f"- operator_id: {application.operator_id}",
        f"- selected_action: {application.selected_action}",
        f"- selection_note: {application.selection_note}",
        f"- evidence_reference: {application.evidence_reference}",
        f"- inputs_recorded: {application.inputs_recorded_count}",
        f"- missing_required_inputs: {application.missing_required_input_count}",
        f"- actions_taken: {application.actions_taken_count}",
        f"- migration_applied: {application.migration_applied_count}",
        f"- table_created: {application.table_created_count}",
        f"- operator_approval_rows_created: {application.operator_approval_row_count}",
        f"- approval_requests_created: {application.created_approval_request_count}",
        f"- existing_approval_requests: {application.existing_approval_request_count}",
        f"- report_path: {application.report_path}",
        f"- created_at: {application.created_at}",
        "",
        "## Applied Columns",
        "",
    ]
    if application.applied_table_columns:
        lines.extend(
            f"- column={column['name']} definition={column['definition']}"
            for column in application.applied_table_columns
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Applied Indexes", ""])
    if application.applied_indexes:
        lines.extend(
            f"- index={index['name']} columns={','.join(index['columns'])}"
            for index in application.applied_indexes
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Claims",
            "",
            "- Creates operator_approval_requests table locally."
            if application.table_created_count
            else "- Did not create operator_approval_requests table in this run.",
            "",
            "## Non-Claims",
            "",
            "- Does not create operator approval request rows.",
            "- Does not create approval_requests rows.",
            "- Does not approve decisions.",
            "- Does not enable capability promotion.",
            "- Does not mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def _is_ready_source_template(
    template: ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate,
) -> bool:
    return (
        template.status == OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_INPUT_REQUIRED
        and template.target_table == TARGET_TABLE
        and template.pending_input_count == 1
        and template.inputs_recorded_count == 0
        and template.required_fields_count == 4
        and template.missing_required_input_count == 4
        and template.actions_taken_count == 0
        and template.migration_applied_count == 0
        and template.table_created_count == 0
        and template.created_approval_request_count == 0
    )


def _empty_template() -> ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate:
    return ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate(
        id="none",
        status="none",
        source_packet_id="none",
        source_packet_status="none",
        source_checklist_id="none",
        source_checklist_status="none",
        source_ledger_id="none",
        source_ledger_status="none",
        source_request_id="none",
        source_request_status="none",
        source_plan_id="none",
        source_plan_status="none",
        source_decision_id="none",
        source_decision_status="none",
        source_review_id="none",
        source_review_status="none",
        target_table="none",
        request_count=0,
        decision_count=0,
        pending_decision_count=0,
        action_count=0,
        pending_action_count=0,
        actions_taken_count=0,
        selected_action="none",
        selection_count=0,
        pending_selection_count=0,
        selections_recorded_count=0,
        approve_selection_count=0,
        defer_selection_count=0,
        more_evidence_selection_count=0,
        template_count=0,
        pending_input_count=0,
        inputs_recorded_count=0,
        required_fields_count=0,
        missing_required_input_count=0,
        approval_boundary="none",
        requested_action="none",
        allowed_actions=[],
        migration_applied_count=0,
        table_created_count=0,
        operator_approval_row_count=0,
        created_approval_request_count=0,
        existing_approval_request_count=0,
        recommended_next_step="expansion-operator-approval-schema-migration-selection-input-template",
        input_template_items=[],
        report_path="none",
        created_at="none",
    )
