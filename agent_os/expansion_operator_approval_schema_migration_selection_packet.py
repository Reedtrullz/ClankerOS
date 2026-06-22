from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.expansion_operator_approval_schema_migration_action_checklist import (
    OPERATOR_APPROVAL_SCHEMA_MIGRATION_MANUAL_ACTION_REQUIRED,
    SELECTED_ACTION,
)
from agent_os.expansion_operator_approval_schema_migration_approval_request import (
    ALLOWED_ACTIONS,
    APPROVAL_BOUNDARY,
    REQUESTED_ACTION,
)
from agent_os.expansion_operator_approval_schema_migration_plan import TARGET_TABLE
from agent_os.storage import (
    ExpansionOperatorApprovalSchemaMigrationActionChecklist,
    ExpansionOperatorApprovalSchemaMigrationSelectionPacket,
    Storage,
)


OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_REQUIRED = (
    "operator_approval_schema_migration_selection_required"
)
MISSING_APPROVAL_SCHEMA_MIGRATION_ACTION_CHECKLIST = (
    "missing_approval_schema_migration_action_checklist"
)
APPROVAL_SCHEMA_MIGRATION_ACTION_CHECKLIST_NOT_READY = (
    "approval_schema_migration_action_checklist_not_ready"
)
RECOMMENDED_NEXT_STEP = (
    "operator_approval_schema_migration_operator_selection_input_required"
)
REPORT_PATH = "docs/expansion-operator-approval-schema-migration-selection-packet.md"


def write_expansion_operator_approval_schema_migration_selection_packet(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalSchemaMigrationSelectionPacket]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    checklists = (
        storage.list_recent_expansion_operator_approval_schema_migration_action_checklists(
            limit=1,
        )
    )
    source_checklist = checklists[0] if checklists else None

    if source_checklist is None:
        status = MISSING_APPROVAL_SCHEMA_MIGRATION_ACTION_CHECKLIST
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
        approval_boundary = "none"
        requested_action = "none"
        allowed_actions: list[str] = []
        selection_count = 0
        pending_selection_count = 0
        selection_items: list[dict[str, Any]] = []
        recommended_next_step = (
            "expansion-operator-approval-schema-migration-action-checklist"
        )
    elif not _is_ready_source_checklist(source_checklist):
        status = APPROVAL_SCHEMA_MIGRATION_ACTION_CHECKLIST_NOT_READY
        source_checklist_id = source_checklist.id
        source_checklist_status = source_checklist.status
        source_ledger_id = source_checklist.source_ledger_id
        source_ledger_status = source_checklist.source_ledger_status
        source_request_id = source_checklist.source_request_id
        source_request_status = source_checklist.source_request_status
        source_plan_id = source_checklist.source_plan_id
        source_plan_status = source_checklist.source_plan_status
        source_decision_id = source_checklist.source_decision_id
        source_decision_status = source_checklist.source_decision_status
        source_review_id = source_checklist.source_review_id
        source_review_status = source_checklist.source_review_status
        target_table = source_checklist.target_table
        request_count = source_checklist.request_count
        decision_count = source_checklist.decision_count
        pending_decision_count = source_checklist.pending_decision_count
        action_count = source_checklist.action_count
        pending_action_count = source_checklist.pending_action_count
        approval_boundary = source_checklist.approval_boundary
        requested_action = source_checklist.requested_action
        allowed_actions = source_checklist.allowed_actions
        selection_count = 0
        pending_selection_count = 0
        selection_items = []
        recommended_next_step = source_checklist.recommended_next_step
    else:
        status = OPERATOR_APPROVAL_SCHEMA_MIGRATION_SELECTION_REQUIRED
        source_checklist_id = source_checklist.id
        source_checklist_status = source_checklist.status
        source_ledger_id = source_checklist.source_ledger_id
        source_ledger_status = source_checklist.source_ledger_status
        source_request_id = source_checklist.source_request_id
        source_request_status = source_checklist.source_request_status
        source_plan_id = source_checklist.source_plan_id
        source_plan_status = source_checklist.source_plan_status
        source_decision_id = source_checklist.source_decision_id
        source_decision_status = source_checklist.source_decision_status
        source_review_id = source_checklist.source_review_id
        source_review_status = source_checklist.source_review_status
        target_table = source_checklist.target_table
        request_count = source_checklist.request_count
        decision_count = source_checklist.decision_count
        pending_decision_count = source_checklist.pending_decision_count
        action_count = source_checklist.action_count
        pending_action_count = source_checklist.pending_action_count
        approval_boundary = source_checklist.approval_boundary
        requested_action = source_checklist.requested_action
        allowed_actions = source_checklist.allowed_actions
        selection_count = 1
        pending_selection_count = 1
        selection_items = [_selection_item(source_checklist)]
        recommended_next_step = RECOMMENDED_NEXT_STEP

    packet = (
        storage.record_expansion_operator_approval_schema_migration_selection_packet(
            status=status,
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
            approve_selection_count=0,
            defer_selection_count=0,
            more_evidence_selection_count=0,
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=0,
            table_created_count=0,
            operator_approval_row_count=0,
            created_approval_request_count=0,
            existing_approval_request_count=storage.count_approval_requests(),
            recommended_next_step=recommended_next_step,
            selection_items=selection_items,
            report_path=REPORT_PATH,
        )
    )
    report_path = root / packet.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_schema_migration_selection_packet_report(
            packet
        ),
        encoding="utf-8",
    )
    return report_path, packet


def render_expansion_operator_approval_schema_migration_selection_packet_report(
    packet: ExpansionOperatorApprovalSchemaMigrationSelectionPacket,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Migration Selection Packet",
        "",
        f"- id: {packet.id}",
        f"- status: {packet.status}",
        f"- source_checklist: {packet.source_checklist_id}",
        f"- source_status: {packet.source_checklist_status}",
        f"- source_ledger: {packet.source_ledger_id}",
        f"- source_ledger_status: {packet.source_ledger_status}",
        f"- source_request: {packet.source_request_id}",
        f"- source_request_status: {packet.source_request_status}",
        f"- source_plan: {packet.source_plan_id}",
        f"- source_plan_status: {packet.source_plan_status}",
        f"- source_decision: {packet.source_decision_id}",
        f"- source_decision_status: {packet.source_decision_status}",
        f"- source_review: {packet.source_review_id}",
        f"- source_review_status: {packet.source_review_status}",
        f"- target_table: {packet.target_table}",
        f"- request_count: {packet.request_count}",
        f"- decision_count: {packet.decision_count}",
        f"- pending_decisions: {packet.pending_decision_count}",
        f"- action_count: {packet.action_count}",
        f"- pending_actions: {packet.pending_action_count}",
        f"- actions_taken: {packet.actions_taken_count}",
        f"- selected_action: {packet.selected_action}",
        f"- selection_count: {packet.selection_count}",
        f"- pending_selections: {packet.pending_selection_count}",
        f"- selections_recorded: {packet.selections_recorded_count}",
        f"- approve_selections: {packet.approve_selection_count}",
        f"- defer_selections: {packet.defer_selection_count}",
        f"- more_evidence_selections: {packet.more_evidence_selection_count}",
        f"- approval_boundary: {packet.approval_boundary}",
        f"- requested_action: {packet.requested_action}",
        f"- allowed_actions: {format_allowed_actions(packet.allowed_actions)}",
        f"- migration_applied: {packet.migration_applied_count}",
        f"- table_created: {packet.table_created_count}",
        f"- operator_approval_rows_created: {packet.operator_approval_row_count}",
        f"- approval_requests_created: {packet.created_approval_request_count}",
        f"- existing_approval_requests: {packet.existing_approval_request_count}",
        f"- recommended_next_step: {packet.recommended_next_step}",
        f"- report_path: {packet.report_path}",
        f"- created_at: {packet.created_at}",
        "",
        "## Selection Items",
        "",
    ]
    if packet.selection_items:
        lines.extend(
            _render_selection_item_line(item) for item in packet.selection_items
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval schema migration selection packet.",
            "- Does not select an operator action.",
            "- Does not record an operator selection.",
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


def render_expansion_operator_approval_schema_migration_selection_packet_line(
    packet: ExpansionOperatorApprovalSchemaMigrationSelectionPacket,
) -> str:
    return (
        f"- {packet.id}: status={packet.status} "
        f"source_checklist={packet.source_checklist_id} "
        f"source_status={packet.source_checklist_status} "
        f"source_ledger={packet.source_ledger_id} "
        f"source_ledger_status={packet.source_ledger_status} "
        f"source_request={packet.source_request_id} "
        f"source_request_status={packet.source_request_status} "
        f"source_plan={packet.source_plan_id} "
        f"source_plan_status={packet.source_plan_status} "
        f"source_decision={packet.source_decision_id} "
        f"source_decision_status={packet.source_decision_status} "
        f"target_table={packet.target_table} "
        f"request_count={packet.request_count} "
        f"decision_count={packet.decision_count} "
        f"pending_decisions={packet.pending_decision_count} "
        f"action_count={packet.action_count} "
        f"pending_actions={packet.pending_action_count} "
        f"actions_taken={packet.actions_taken_count} "
        f"selected_action={packet.selected_action} "
        f"selection_count={packet.selection_count} "
        f"pending_selections={packet.pending_selection_count} "
        f"selections_recorded={packet.selections_recorded_count} "
        f"approve_selections={packet.approve_selection_count} "
        f"defer_selections={packet.defer_selection_count} "
        f"more_evidence_selections={packet.more_evidence_selection_count} "
        f"approval_boundary={packet.approval_boundary} "
        f"requested_action={packet.requested_action} "
        f"allowed_actions={format_allowed_actions(packet.allowed_actions)} "
        f"migration_applied={packet.migration_applied_count} "
        f"table_created={packet.table_created_count} "
        f"operator_approval_rows_created={packet.operator_approval_row_count} "
        f"approval_requests_created={packet.created_approval_request_count} "
        f"existing_approval_requests={packet.existing_approval_request_count} "
        f"recommended_next_step={packet.recommended_next_step} "
        f"report={packet.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    return ",".join(actions) if actions else "none"


def _is_ready_source_checklist(
    source_checklist: ExpansionOperatorApprovalSchemaMigrationActionChecklist,
) -> bool:
    return (
        source_checklist.status
        == OPERATOR_APPROVAL_SCHEMA_MIGRATION_MANUAL_ACTION_REQUIRED
        and source_checklist.target_table == TARGET_TABLE
        and source_checklist.request_count == 1
        and source_checklist.decision_count == 1
        and source_checklist.pending_decision_count == 1
        and source_checklist.action_count == 1
        and source_checklist.pending_action_count == 1
        and source_checklist.actions_taken_count == 0
        and source_checklist.selected_action == SELECTED_ACTION
        and source_checklist.approval_boundary == APPROVAL_BOUNDARY
        and source_checklist.requested_action == REQUESTED_ACTION
        and source_checklist.allowed_actions == ALLOWED_ACTIONS
        and source_checklist.migration_applied_count == 0
        and source_checklist.table_created_count == 0
        and source_checklist.operator_approval_row_count == 0
        and source_checklist.created_approval_request_count == 0
        and source_checklist.existing_approval_request_count == 0
    )


def _selection_item(
    source_checklist: ExpansionOperatorApprovalSchemaMigrationActionChecklist,
) -> dict[str, Any]:
    return {
        "selection_status": "operator_input_required",
        "selected_action": SELECTED_ACTION,
        "requested_action": source_checklist.requested_action,
        "approval_boundary": source_checklist.approval_boundary,
        "target_table": source_checklist.target_table,
        "source_checklist_id": source_checklist.id,
        "source_ledger_id": source_checklist.source_ledger_id,
        "source_request_id": source_checklist.source_request_id,
        "allowed_actions": source_checklist.allowed_actions,
        "evidence_required": "operator selection input required before action",
    }


def _render_selection_item_line(item: dict[str, Any]) -> str:
    return (
        f"- selection_status={item['selection_status']} "
        f"selected_action={item['selected_action']} "
        f"requested_action={item['requested_action']} "
        f"approval_boundary={item['approval_boundary']} "
        f"target_table={item['target_table']} "
        f"allowed_actions={format_allowed_actions(item['allowed_actions'])} "
        f"evidence_required={item['evidence_required']}"
    )
