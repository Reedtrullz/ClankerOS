from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.expansion_operator_approval_schema_migration_approval_request import (
    ALLOWED_ACTIONS,
    APPROVAL_BOUNDARY,
    REQUESTED_ACTION,
)
from agent_os.expansion_operator_approval_schema_migration_decision_ledger import (
    OPERATOR_APPROVAL_SCHEMA_MIGRATION_DECISION_PENDING,
)
from agent_os.expansion_operator_approval_schema_migration_plan import TARGET_TABLE
from agent_os.storage import (
    ExpansionOperatorApprovalSchemaMigrationActionChecklist,
    ExpansionOperatorApprovalSchemaMigrationDecisionLedger,
    Storage,
)


OPERATOR_APPROVAL_SCHEMA_MIGRATION_MANUAL_ACTION_REQUIRED = (
    "operator_approval_schema_migration_manual_action_required"
)
MISSING_APPROVAL_SCHEMA_MIGRATION_DECISION_LEDGER = (
    "missing_approval_schema_migration_decision_ledger"
)
APPROVAL_SCHEMA_MIGRATION_DECISION_LEDGER_NOT_READY = (
    "approval_schema_migration_decision_ledger_not_ready"
)
SELECTED_ACTION = "none"
RECOMMENDED_NEXT_STEP = (
    "operator_approval_schema_migration_operator_selection_required"
)
REPORT_PATH = "docs/expansion-operator-approval-schema-migration-action-checklist.md"


def write_expansion_operator_approval_schema_migration_action_checklist(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalSchemaMigrationActionChecklist]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    ledgers = (
        storage.list_recent_expansion_operator_approval_schema_migration_decision_ledgers(
            limit=1,
        )
    )
    source_ledger = ledgers[0] if ledgers else None

    if source_ledger is None:
        status = MISSING_APPROVAL_SCHEMA_MIGRATION_DECISION_LEDGER
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
        action_items: list[dict[str, Any]] = []
        recommended_next_step = (
            "expansion-operator-approval-schema-migration-decision-ledger"
        )
    elif not _is_ready_source_ledger(source_ledger):
        status = APPROVAL_SCHEMA_MIGRATION_DECISION_LEDGER_NOT_READY
        source_ledger_id = source_ledger.id
        source_ledger_status = source_ledger.status
        source_request_id = source_ledger.source_request_id
        source_request_status = source_ledger.source_request_status
        source_plan_id = source_ledger.source_plan_id
        source_plan_status = source_ledger.source_plan_status
        source_decision_id = source_ledger.source_decision_id
        source_decision_status = source_ledger.source_decision_status
        source_review_id = source_ledger.source_review_id
        source_review_status = source_ledger.source_review_status
        target_table = source_ledger.target_table
        request_count = source_ledger.request_count
        decision_count = source_ledger.decision_count
        pending_decision_count = source_ledger.pending_decision_count
        action_count = 0
        pending_action_count = 0
        approval_boundary = source_ledger.approval_boundary
        requested_action = source_ledger.requested_action
        allowed_actions = source_ledger.allowed_actions
        action_items = []
        recommended_next_step = source_ledger.recommended_next_step
    else:
        status = OPERATOR_APPROVAL_SCHEMA_MIGRATION_MANUAL_ACTION_REQUIRED
        source_ledger_id = source_ledger.id
        source_ledger_status = source_ledger.status
        source_request_id = source_ledger.source_request_id
        source_request_status = source_ledger.source_request_status
        source_plan_id = source_ledger.source_plan_id
        source_plan_status = source_ledger.source_plan_status
        source_decision_id = source_ledger.source_decision_id
        source_decision_status = source_ledger.source_decision_status
        source_review_id = source_ledger.source_review_id
        source_review_status = source_ledger.source_review_status
        target_table = source_ledger.target_table
        request_count = source_ledger.request_count
        decision_count = source_ledger.decision_count
        pending_decision_count = source_ledger.pending_decision_count
        action_count = 1
        pending_action_count = 1
        approval_boundary = source_ledger.approval_boundary
        requested_action = source_ledger.requested_action
        allowed_actions = source_ledger.allowed_actions
        action_items = [_action_item(source_ledger)]
        recommended_next_step = RECOMMENDED_NEXT_STEP

    checklist = (
        storage.record_expansion_operator_approval_schema_migration_action_checklist(
            status=status,
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
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=0,
            table_created_count=0,
            operator_approval_row_count=0,
            created_approval_request_count=0,
            existing_approval_request_count=storage.count_approval_requests(),
            recommended_next_step=recommended_next_step,
            action_items=action_items,
            report_path=REPORT_PATH,
        )
    )
    report_path = root / checklist.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_schema_migration_action_checklist_report(
            checklist
        ),
        encoding="utf-8",
    )
    return report_path, checklist


def render_expansion_operator_approval_schema_migration_action_checklist_report(
    checklist: ExpansionOperatorApprovalSchemaMigrationActionChecklist,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Migration Action Checklist",
        "",
        f"- id: {checklist.id}",
        f"- status: {checklist.status}",
        f"- source_ledger: {checklist.source_ledger_id}",
        f"- source_status: {checklist.source_ledger_status}",
        f"- source_request: {checklist.source_request_id}",
        f"- source_request_status: {checklist.source_request_status}",
        f"- source_plan: {checklist.source_plan_id}",
        f"- source_plan_status: {checklist.source_plan_status}",
        f"- source_decision: {checklist.source_decision_id}",
        f"- source_decision_status: {checklist.source_decision_status}",
        f"- source_review: {checklist.source_review_id}",
        f"- source_review_status: {checklist.source_review_status}",
        f"- target_table: {checklist.target_table}",
        f"- request_count: {checklist.request_count}",
        f"- decision_count: {checklist.decision_count}",
        f"- pending_decisions: {checklist.pending_decision_count}",
        f"- action_count: {checklist.action_count}",
        f"- pending_actions: {checklist.pending_action_count}",
        f"- actions_taken: {checklist.actions_taken_count}",
        f"- selected_action: {checklist.selected_action}",
        f"- approval_boundary: {checklist.approval_boundary}",
        f"- requested_action: {checklist.requested_action}",
        f"- allowed_actions: {format_allowed_actions(checklist.allowed_actions)}",
        f"- migration_applied: {checklist.migration_applied_count}",
        f"- table_created: {checklist.table_created_count}",
        f"- operator_approval_rows_created: {checklist.operator_approval_row_count}",
        f"- approval_requests_created: {checklist.created_approval_request_count}",
        f"- existing_approval_requests: {checklist.existing_approval_request_count}",
        f"- recommended_next_step: {checklist.recommended_next_step}",
        f"- report_path: {checklist.report_path}",
        f"- created_at: {checklist.created_at}",
        "",
        "## Action Items",
        "",
    ]
    if checklist.action_items:
        lines.extend(_render_action_item_line(item) for item in checklist.action_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval schema migration action checklist.",
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


def render_expansion_operator_approval_schema_migration_action_checklist_line(
    checklist: ExpansionOperatorApprovalSchemaMigrationActionChecklist,
) -> str:
    return (
        f"- {checklist.id}: status={checklist.status} "
        f"source_ledger={checklist.source_ledger_id} "
        f"source_status={checklist.source_ledger_status} "
        f"source_request={checklist.source_request_id} "
        f"source_request_status={checklist.source_request_status} "
        f"source_plan={checklist.source_plan_id} "
        f"source_plan_status={checklist.source_plan_status} "
        f"source_decision={checklist.source_decision_id} "
        f"source_decision_status={checklist.source_decision_status} "
        f"target_table={checklist.target_table} "
        f"request_count={checklist.request_count} "
        f"decision_count={checklist.decision_count} "
        f"pending_decisions={checklist.pending_decision_count} "
        f"action_count={checklist.action_count} "
        f"pending_actions={checklist.pending_action_count} "
        f"actions_taken={checklist.actions_taken_count} "
        f"selected_action={checklist.selected_action} "
        f"approval_boundary={checklist.approval_boundary} "
        f"requested_action={checklist.requested_action} "
        f"allowed_actions={format_allowed_actions(checklist.allowed_actions)} "
        f"migration_applied={checklist.migration_applied_count} "
        f"table_created={checklist.table_created_count} "
        f"operator_approval_rows_created={checklist.operator_approval_row_count} "
        f"approval_requests_created={checklist.created_approval_request_count} "
        f"existing_approval_requests={checklist.existing_approval_request_count} "
        f"recommended_next_step={checklist.recommended_next_step} "
        f"report={checklist.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    return ",".join(actions) if actions else "none"


def _is_ready_source_ledger(
    source_ledger: ExpansionOperatorApprovalSchemaMigrationDecisionLedger,
) -> bool:
    return (
        source_ledger.status == OPERATOR_APPROVAL_SCHEMA_MIGRATION_DECISION_PENDING
        and source_ledger.target_table == TARGET_TABLE
        and source_ledger.pending_decision_count == 1
        and source_ledger.approved_decision_count == 0
        and source_ledger.deferred_decision_count == 0
        and source_ledger.more_evidence_decision_count == 0
        and source_ledger.approval_boundary == APPROVAL_BOUNDARY
        and source_ledger.requested_action == REQUESTED_ACTION
        and source_ledger.allowed_actions == ALLOWED_ACTIONS
        and source_ledger.migration_applied_count == 0
        and source_ledger.table_created_count == 0
        and source_ledger.operator_approval_row_count == 0
        and source_ledger.created_approval_request_count == 0
    )


def _action_item(
    source_ledger: ExpansionOperatorApprovalSchemaMigrationDecisionLedger,
) -> dict[str, Any]:
    return {
        "action_status": "manual_action_required",
        "selected_action": SELECTED_ACTION,
        "requested_action": source_ledger.requested_action,
        "approval_boundary": source_ledger.approval_boundary,
        "target_table": source_ledger.target_table,
        "source_ledger_id": source_ledger.id,
        "source_request_id": source_ledger.source_request_id,
        "allowed_actions": source_ledger.allowed_actions,
        "evidence_required": "operator selection and note required before action",
    }


def _render_action_item_line(item: dict[str, Any]) -> str:
    return (
        f"- action_status={item['action_status']} "
        f"selected_action={item['selected_action']} "
        f"requested_action={item['requested_action']} "
        f"approval_boundary={item['approval_boundary']} "
        f"target_table={item['target_table']} "
        f"allowed_actions={format_allowed_actions(item['allowed_actions'])} "
        f"evidence_required={item['evidence_required']}"
    )
