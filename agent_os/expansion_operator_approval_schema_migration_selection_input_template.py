from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.expansion_operator_approval_schema_migration_action_checklist import (
    SELECTED_ACTION,
)
from agent_os.expansion_operator_approval_schema_migration_approval_request import (
    ALLOWED_ACTIONS,
    APPROVAL_BOUNDARY,
    REQUESTED_ACTION,
)
from agent_os.expansion_operator_approval_schema_migration_plan import TARGET_TABLE
from agent_os.expansion_operator_approval_schema_migration_selection_packet import (
    OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_REQUIRED,
)
from agent_os.storage import (
    ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate,
    ExpansionOperatorApprovalSchemaMigrationSelectionPacket,
    Storage,
)


OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_INPUT_REQUIRED = (
    "operator_approval_schema_migration_selection_input_required"
)
MISSING_APPROVAL_SCHEMA_MIGRATION_SELECTION_PACKET = (
    "missing_approval_schema_migration_selection_packet"
)
APPROVAL_SCHEMA_MIGRATION_SELECTION_PACKET_NOT_READY = (
    "approval_schema_migration_selection_packet_not_ready"
)
RECOMMENDED_NEXT_STEP = "operator_approval_schema_migration_operator_input_required"
REQUIRED_FIELDS = [
    "operator_id",
    "selected_action",
    "selection_note",
    "evidence_reference",
]
REPORT_PATH = (
    "docs/expansion-operator-approval-schema-migration-selection-input-template.md"
)


def write_expansion_operator_approval_schema_migration_selection_input_template(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    packets = (
        storage.list_recent_expansion_operator_approval_schema_migration_selection_packets(
            limit=1,
        )
    )
    source_packet = packets[0] if packets else None

    if source_packet is None:
        status = MISSING_APPROVAL_SCHEMA_MIGRATION_SELECTION_PACKET
        source_packet_id = "none"
        source_packet_status = "none"
        source_checklist_id = "none"
        source_checklist_status = "none"
        source_ledger_id = "none"
        source_ledger_status = "none"
        source_request_id = "none"
        source_request_status = "none"
        source_plan_id = "none"
        source_plan_status = "none"
        source_decision_id = "none"
        source_decision_status = "none"
        source_review_id = "none"
        source_review_status = "none"
        target_table = "none"
        request_count = 0
        decision_count = 0
        pending_decision_count = 0
        action_count = 0
        pending_action_count = 0
        selection_count = 0
        pending_selection_count = 0
        approve_selection_count = 0
        defer_selection_count = 0
        more_evidence_selection_count = 0
        template_count = 0
        pending_input_count = 0
        required_fields_count = 0
        missing_required_input_count = 0
        approval_boundary = "none"
        requested_action = "none"
        allowed_actions: list[str] = []
        input_template_items: list[dict[str, Any]] = []
        recommended_next_step = (
            "expansion-operator-approval-schema-migration-selection-packet"
        )
    elif not _is_ready_source_packet(source_packet):
        status = APPROVAL_SCHEMA_MIGRATION_SELECTION_PACKET_NOT_READY
        source_packet_id = source_packet.id
        source_packet_status = source_packet.status
        source_checklist_id = source_packet.source_checklist_id
        source_checklist_status = source_packet.source_checklist_status
        source_ledger_id = source_packet.source_ledger_id
        source_ledger_status = source_packet.source_ledger_status
        source_request_id = source_packet.source_request_id
        source_request_status = source_packet.source_request_status
        source_plan_id = source_packet.source_plan_id
        source_plan_status = source_packet.source_plan_status
        source_decision_id = source_packet.source_decision_id
        source_decision_status = source_packet.source_decision_status
        source_review_id = source_packet.source_review_id
        source_review_status = source_packet.source_review_status
        target_table = source_packet.target_table
        request_count = source_packet.request_count
        decision_count = source_packet.decision_count
        pending_decision_count = source_packet.pending_decision_count
        action_count = source_packet.action_count
        pending_action_count = source_packet.pending_action_count
        selection_count = source_packet.selection_count
        pending_selection_count = source_packet.pending_selection_count
        approve_selection_count = source_packet.approve_selection_count
        defer_selection_count = source_packet.defer_selection_count
        more_evidence_selection_count = source_packet.more_evidence_selection_count
        template_count = 0
        pending_input_count = 0
        required_fields_count = 0
        missing_required_input_count = 0
        approval_boundary = source_packet.approval_boundary
        requested_action = source_packet.requested_action
        allowed_actions = source_packet.allowed_actions
        input_template_items = []
        recommended_next_step = source_packet.recommended_next_step
    else:
        status = OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_INPUT_REQUIRED
        source_packet_id = source_packet.id
        source_packet_status = source_packet.status
        source_checklist_id = source_packet.source_checklist_id
        source_checklist_status = source_packet.source_checklist_status
        source_ledger_id = source_packet.source_ledger_id
        source_ledger_status = source_packet.source_ledger_status
        source_request_id = source_packet.source_request_id
        source_request_status = source_packet.source_request_status
        source_plan_id = source_packet.source_plan_id
        source_plan_status = source_packet.source_plan_status
        source_decision_id = source_packet.source_decision_id
        source_decision_status = source_packet.source_decision_status
        source_review_id = source_packet.source_review_id
        source_review_status = source_packet.source_review_status
        target_table = source_packet.target_table
        request_count = source_packet.request_count
        decision_count = source_packet.decision_count
        pending_decision_count = source_packet.pending_decision_count
        action_count = source_packet.action_count
        pending_action_count = source_packet.pending_action_count
        selection_count = source_packet.selection_count
        pending_selection_count = source_packet.pending_selection_count
        approve_selection_count = source_packet.approve_selection_count
        defer_selection_count = source_packet.defer_selection_count
        more_evidence_selection_count = source_packet.more_evidence_selection_count
        template_count = 1
        pending_input_count = 1
        required_fields_count = len(REQUIRED_FIELDS)
        missing_required_input_count = len(REQUIRED_FIELDS)
        approval_boundary = source_packet.approval_boundary
        requested_action = source_packet.requested_action
        allowed_actions = source_packet.allowed_actions
        input_template_items = [_input_template_item(source_packet)]
        recommended_next_step = RECOMMENDED_NEXT_STEP

    template = storage.record_expansion_operator_approval_schema_migration_selection_input_template(
        status=status,
        source_packet_id=source_packet_id,
        source_packet_status=source_packet_status,
        source_checklist_id=source_checklist_id,
        source_checklist_status=source_checklist_status,
        source_ledger_id=source_ledger_id,
        source_ledger_status=source_ledger_status,
        source_request_id=source_request_id,
        source_request_status=source_request_status,
        source_plan_id=source_plan_id,
        source_plan_status=source_plan_status,
        source_decision_id=source_decision_id,
        source_decision_status=source_decision_status,
        source_review_id=source_review_id,
        source_review_status=source_review_status,
        target_table=target_table,
        request_count=request_count,
        decision_count=decision_count,
        pending_decision_count=pending_decision_count,
        action_count=action_count,
        pending_action_count=pending_action_count,
        actions_taken_count=0,
        selected_action=SELECTED_ACTION,
        selection_count=selection_count,
        pending_selection_count=pending_selection_count,
        selections_recorded_count=0,
        approve_selection_count=approve_selection_count,
        defer_selection_count=defer_selection_count,
        more_evidence_selection_count=more_evidence_selection_count,
        template_count=template_count,
        pending_input_count=pending_input_count,
        inputs_recorded_count=0,
        required_fields_count=required_fields_count,
        missing_required_input_count=missing_required_input_count,
        approval_boundary=approval_boundary,
        requested_action=requested_action,
        allowed_actions=allowed_actions,
        migration_applied_count=0,
        table_created_count=0,
        operator_approval_row_count=0,
        created_approval_request_count=0,
        existing_approval_request_count=storage.count_approval_requests(),
        recommended_next_step=recommended_next_step,
        input_template_items=input_template_items,
        report_path=REPORT_PATH,
    )
    report_path = root / template.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_schema_migration_selection_input_template_report(
            template
        ),
        encoding="utf-8",
    )
    return report_path, template


def render_expansion_operator_approval_schema_migration_selection_input_template_report(
    template: ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Migration Selection Input Template",
        "",
        f"- id: {template.id}",
        f"- status: {template.status}",
        f"- source_packet: {template.source_packet_id}",
        f"- source_status: {template.source_packet_status}",
        f"- source_checklist: {template.source_checklist_id}",
        f"- source_checklist_status: {template.source_checklist_status}",
        f"- source_ledger: {template.source_ledger_id}",
        f"- source_ledger_status: {template.source_ledger_status}",
        f"- source_request: {template.source_request_id}",
        f"- source_request_status: {template.source_request_status}",
        f"- source_plan: {template.source_plan_id}",
        f"- source_plan_status: {template.source_plan_status}",
        f"- source_decision: {template.source_decision_id}",
        f"- source_decision_status: {template.source_decision_status}",
        f"- source_review: {template.source_review_id}",
        f"- source_review_status: {template.source_review_status}",
        f"- target_table: {template.target_table}",
        f"- request_count: {template.request_count}",
        f"- decision_count: {template.decision_count}",
        f"- pending_decisions: {template.pending_decision_count}",
        f"- action_count: {template.action_count}",
        f"- pending_actions: {template.pending_action_count}",
        f"- actions_taken: {template.actions_taken_count}",
        f"- selected_action: {template.selected_action}",
        f"- selection_count: {template.selection_count}",
        f"- pending_selections: {template.pending_selection_count}",
        f"- selections_recorded: {template.selections_recorded_count}",
        f"- approve_selections: {template.approve_selection_count}",
        f"- defer_selections: {template.defer_selection_count}",
        f"- more_evidence_selections: {template.more_evidence_selection_count}",
        f"- template_count: {template.template_count}",
        f"- pending_inputs: {template.pending_input_count}",
        f"- inputs_recorded: {template.inputs_recorded_count}",
        f"- required_fields_count: {template.required_fields_count}",
        f"- missing_required_inputs: {template.missing_required_input_count}",
        f"- approval_boundary: {template.approval_boundary}",
        f"- requested_action: {template.requested_action}",
        f"- allowed_actions: {format_allowed_actions(template.allowed_actions)}",
        f"- migration_applied: {template.migration_applied_count}",
        f"- table_created: {template.table_created_count}",
        f"- operator_approval_rows_created: {template.operator_approval_row_count}",
        f"- approval_requests_created: {template.created_approval_request_count}",
        f"- existing_approval_requests: {template.existing_approval_request_count}",
        f"- recommended_next_step: {template.recommended_next_step}",
        f"- report_path: {template.report_path}",
        f"- created_at: {template.created_at}",
        "",
        "## Required Operator Inputs",
        "",
    ]
    if template.input_template_items:
        lines.extend(
            _render_input_template_item_line(item)
            for item in template.input_template_items
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval schema migration selection input template.",
            "- Does not record operator input.",
            "- Does not record an operator selection.",
            "- Does not select an operator action.",
            "- Does not record an operator action as taken.",
            "- Does not apply schema migrations.",
            "- Does not create operator_approval_requests table.",
            "- Does not create operator_approval_requests rows.",
            "- Does not create approval_requests rows.",
            "- Does not approve decisions.",
            "- Does not defer decisions.",
            "- Does not request more evidence.",
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


def render_expansion_operator_approval_schema_migration_selection_input_template_line(
    template: ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate,
) -> str:
    return (
        f"- {template.id}: status={template.status} "
        f"source_packet={template.source_packet_id} "
        f"source_status={template.source_packet_status} "
        f"source_checklist={template.source_checklist_id} "
        f"source_checklist_status={template.source_checklist_status} "
        f"source_ledger={template.source_ledger_id} "
        f"source_ledger_status={template.source_ledger_status} "
        f"source_request={template.source_request_id} "
        f"source_request_status={template.source_request_status} "
        f"source_plan={template.source_plan_id} "
        f"source_plan_status={template.source_plan_status} "
        f"target_table={template.target_table} "
        f"request_count={template.request_count} "
        f"decision_count={template.decision_count} "
        f"pending_decisions={template.pending_decision_count} "
        f"action_count={template.action_count} "
        f"pending_actions={template.pending_action_count} "
        f"actions_taken={template.actions_taken_count} "
        f"selected_action={template.selected_action} "
        f"selection_count={template.selection_count} "
        f"pending_selections={template.pending_selection_count} "
        f"selections_recorded={template.selections_recorded_count} "
        f"template_count={template.template_count} "
        f"pending_inputs={template.pending_input_count} "
        f"inputs_recorded={template.inputs_recorded_count} "
        f"required_fields_count={template.required_fields_count} "
        f"missing_required_inputs={template.missing_required_input_count} "
        f"approval_boundary={template.approval_boundary} "
        f"requested_action={template.requested_action} "
        f"allowed_actions={format_allowed_actions(template.allowed_actions)} "
        f"migration_applied={template.migration_applied_count} "
        f"table_created={template.table_created_count} "
        f"operator_approval_rows_created={template.operator_approval_row_count} "
        f"approval_requests_created={template.created_approval_request_count} "
        f"existing_approval_requests={template.existing_approval_request_count} "
        f"recommended_next_step={template.recommended_next_step} "
        f"report={template.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    return ",".join(actions) if actions else "none"


def format_required_fields(fields: list[str]) -> str:
    return ",".join(fields) if fields else "none"


def _is_ready_source_packet(
    source_packet: ExpansionOperatorApprovalSchemaMigrationSelectionPacket,
) -> bool:
    return (
        source_packet.status == OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_REQUIRED
        and source_packet.target_table == TARGET_TABLE
        and source_packet.request_count == 1
        and source_packet.decision_count == 1
        and source_packet.pending_decision_count == 1
        and source_packet.action_count == 1
        and source_packet.pending_action_count == 1
        and source_packet.actions_taken_count == 0
        and source_packet.selected_action == SELECTED_ACTION
        and source_packet.selection_count == 1
        and source_packet.pending_selection_count == 1
        and source_packet.selections_recorded_count == 0
        and source_packet.approve_selection_count == 0
        and source_packet.defer_selection_count == 0
        and source_packet.more_evidence_selection_count == 0
        and source_packet.approval_boundary == APPROVAL_BOUNDARY
        and source_packet.requested_action == REQUESTED_ACTION
        and source_packet.allowed_actions == ALLOWED_ACTIONS
        and source_packet.migration_applied_count == 0
        and source_packet.table_created_count == 0
        and source_packet.operator_approval_row_count == 0
        and source_packet.created_approval_request_count == 0
        and source_packet.existing_approval_request_count == 0
    )


def _input_template_item(
    source_packet: ExpansionOperatorApprovalSchemaMigrationSelectionPacket,
) -> dict[str, Any]:
    return {
        "input_status": "operator_input_required",
        "selected_action": SELECTED_ACTION,
        "requested_action": source_packet.requested_action,
        "approval_boundary": source_packet.approval_boundary,
        "target_table": source_packet.target_table,
        "source_packet_id": source_packet.id,
        "source_checklist_id": source_packet.source_checklist_id,
        "source_ledger_id": source_packet.source_ledger_id,
        "source_request_id": source_packet.source_request_id,
        "allowed_actions": source_packet.allowed_actions,
        "required_fields": REQUIRED_FIELDS,
        "evidence_required": "operator input required before recording selection",
    }


def _render_input_template_item_line(item: dict[str, Any]) -> str:
    return (
        f"- input_status={item['input_status']} "
        f"selected_action={item['selected_action']} "
        f"requested_action={item['requested_action']} "
        f"approval_boundary={item['approval_boundary']} "
        f"target_table={item['target_table']} "
        f"allowed_actions={format_allowed_actions(item['allowed_actions'])} "
        f"required_fields={format_required_fields(item['required_fields'])} "
        f"evidence_required={item['evidence_required']}"
    )
