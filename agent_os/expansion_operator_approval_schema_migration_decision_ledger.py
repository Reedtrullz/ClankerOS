from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.expansion_operator_approval_schema_migration_approval_request import (
    ALLOWED_ACTIONS,
    APPROVAL_BOUNDARY,
    OPERATOR_APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUIRED,
    REQUESTED_ACTION,
)
from agent_os.expansion_operator_approval_schema_migration_plan import TARGET_TABLE
from agent_os.storage import (
    ExpansionOperatorApprovalSchemaMigrationApprovalRequest,
    ExpansionOperatorApprovalSchemaMigrationDecisionLedger,
    Storage,
)


OPERATOR_APPROVAL_SCHEMA_MIGRATION_DECISION_PENDING = (
    "operator_approval_schema_migration_decision_pending"
)
MISSING_APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUEST = (
    "missing_approval_schema_migration_approval_request"
)
APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUEST_NOT_READY = (
    "approval_schema_migration_approval_request_not_ready"
)
RECOMMENDED_NEXT_STEP = "operator_approval_schema_migration_operator_action_required"
REPORT_PATH = "docs/expansion-operator-approval-schema-migration-decision-ledger.md"


def write_expansion_operator_approval_schema_migration_decision_ledger(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalSchemaMigrationDecisionLedger]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    requests = (
        storage.list_recent_expansion_operator_approval_schema_migration_approval_requests(
            limit=1,
        )
    )
    source_request = requests[0] if requests else None

    if source_request is None:
        status = MISSING_APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUEST
        source_request_id = "none"
        source_request_status = "none"
        source_plan_id = "none"
        source_plan_status = "none"
        source_decision_id = "none"
        source_decision_status = "none"
        source_review_id = "none"
        source_review_status = "none"
        target_table = "none"
        planned_column_count = 0
        planned_index_count = 0
        migration_step_count = 0
        affected_request_count = 0
        schema_gap_count = 0
        request_count = 0
        decision_count = 0
        pending_decision_count = 0
        approval_boundary = "none"
        requested_action = "none"
        allowed_actions: list[str] = []
        decision_items: list[dict[str, Any]] = []
        recommended_next_step = (
            "expansion-operator-approval-schema-migration-approval-request"
        )
    elif not _is_ready_source_request(source_request):
        status = APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUEST_NOT_READY
        source_request_id = source_request.id
        source_request_status = source_request.status
        source_plan_id = source_request.source_plan_id
        source_plan_status = source_request.source_plan_status
        source_decision_id = source_request.source_decision_id
        source_decision_status = source_request.source_decision_status
        source_review_id = source_request.source_review_id
        source_review_status = source_request.source_review_status
        target_table = source_request.target_table
        planned_column_count = source_request.planned_column_count
        planned_index_count = source_request.planned_index_count
        migration_step_count = source_request.migration_step_count
        affected_request_count = source_request.affected_request_count
        schema_gap_count = source_request.schema_gap_count
        request_count = source_request.request_count
        decision_count = 0
        pending_decision_count = 0
        approval_boundary = source_request.approval_boundary
        requested_action = source_request.requested_action
        allowed_actions = source_request.allowed_actions
        decision_items = []
        recommended_next_step = source_request.recommended_next_step
    else:
        status = OPERATOR_APPROVAL_SCHEMA_MIGRATION_DECISION_PENDING
        source_request_id = source_request.id
        source_request_status = source_request.status
        source_plan_id = source_request.source_plan_id
        source_plan_status = source_request.source_plan_status
        source_decision_id = source_request.source_decision_id
        source_decision_status = source_request.source_decision_status
        source_review_id = source_request.source_review_id
        source_review_status = source_request.source_review_status
        target_table = source_request.target_table
        planned_column_count = source_request.planned_column_count
        planned_index_count = source_request.planned_index_count
        migration_step_count = source_request.migration_step_count
        affected_request_count = source_request.affected_request_count
        schema_gap_count = source_request.schema_gap_count
        request_count = source_request.request_count
        decision_count = 1
        pending_decision_count = 1
        approval_boundary = source_request.approval_boundary
        requested_action = source_request.requested_action
        allowed_actions = source_request.allowed_actions
        decision_items = [_decision_item(source_request)]
        recommended_next_step = RECOMMENDED_NEXT_STEP

    ledger = (
        storage.record_expansion_operator_approval_schema_migration_decision_ledger(
            status=status,
            source_request_id=source_request_id,
            source_request_status=source_request_status,
            source_plan_id=source_plan_id,
            source_plan_status=source_plan_status,
            source_decision_id=source_decision_id,
            source_decision_status=source_decision_status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            target_table=target_table,
            planned_column_count=planned_column_count,
            planned_index_count=planned_index_count,
            migration_step_count=migration_step_count,
            affected_request_count=affected_request_count,
            schema_gap_count=schema_gap_count,
            request_count=request_count,
            decision_count=decision_count,
            pending_decision_count=pending_decision_count,
            approved_decision_count=0,
            deferred_decision_count=0,
            more_evidence_decision_count=0,
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=0,
            table_created_count=0,
            operator_approval_row_count=0,
            created_approval_request_count=0,
            existing_approval_request_count=storage.count_approval_requests(),
            recommended_next_step=recommended_next_step,
            decision_items=decision_items,
            report_path=REPORT_PATH,
        )
    )
    report_path = root / ledger.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_schema_migration_decision_ledger_report(
            ledger
        ),
        encoding="utf-8",
    )
    return report_path, ledger


def render_expansion_operator_approval_schema_migration_decision_ledger_report(
    ledger: ExpansionOperatorApprovalSchemaMigrationDecisionLedger,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Migration Decision Ledger",
        "",
        f"- id: {ledger.id}",
        f"- status: {ledger.status}",
        f"- source_request: {ledger.source_request_id}",
        f"- source_status: {ledger.source_request_status}",
        f"- source_plan: {ledger.source_plan_id}",
        f"- source_plan_status: {ledger.source_plan_status}",
        f"- source_decision: {ledger.source_decision_id}",
        f"- source_decision_status: {ledger.source_decision_status}",
        f"- source_review: {ledger.source_review_id}",
        f"- source_review_status: {ledger.source_review_status}",
        f"- target_table: {ledger.target_table}",
        f"- planned_columns: {ledger.planned_column_count}",
        f"- planned_indexes: {ledger.planned_index_count}",
        f"- migration_steps: {ledger.migration_step_count}",
        f"- affected_requests: {ledger.affected_request_count}",
        f"- schema_gaps: {ledger.schema_gap_count}",
        f"- request_count: {ledger.request_count}",
        f"- decision_count: {ledger.decision_count}",
        f"- pending_decisions: {ledger.pending_decision_count}",
        f"- approved_decisions: {ledger.approved_decision_count}",
        f"- deferred_decisions: {ledger.deferred_decision_count}",
        f"- more_evidence_decisions: {ledger.more_evidence_decision_count}",
        f"- approval_boundary: {ledger.approval_boundary}",
        f"- requested_action: {ledger.requested_action}",
        f"- allowed_actions: {format_allowed_actions(ledger.allowed_actions)}",
        f"- migration_applied: {ledger.migration_applied_count}",
        f"- table_created: {ledger.table_created_count}",
        f"- operator_approval_rows_created: {ledger.operator_approval_row_count}",
        f"- approval_requests_created: {ledger.created_approval_request_count}",
        f"- existing_approval_requests: {ledger.existing_approval_request_count}",
        f"- recommended_next_step: {ledger.recommended_next_step}",
        f"- report_path: {ledger.report_path}",
        f"- created_at: {ledger.created_at}",
        "",
        "## Decision Items",
        "",
    ]
    if ledger.decision_items:
        lines.extend(_render_decision_item_line(item) for item in ledger.decision_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval schema migration decision ledger.",
            "- Does not apply schema migrations.",
            "- Does not create operator_approval_requests table.",
            "- Does not create operator_approval_requests rows.",
            "- Does not create approval_requests rows.",
            "- Does not approve decisions.",
            "- Does not defer decisions.",
            "- Does not request more evidence.",
            "- Does not take allowed actions.",
            "- Does not record an operator decision as taken.",
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


def render_expansion_operator_approval_schema_migration_decision_ledger_line(
    ledger: ExpansionOperatorApprovalSchemaMigrationDecisionLedger,
) -> str:
    return (
        f"- {ledger.id}: status={ledger.status} "
        f"source_request={ledger.source_request_id} "
        f"source_status={ledger.source_request_status} "
        f"source_plan={ledger.source_plan_id} "
        f"source_plan_status={ledger.source_plan_status} "
        f"source_decision={ledger.source_decision_id} "
        f"source_decision_status={ledger.source_decision_status} "
        f"source_review={ledger.source_review_id} "
        f"source_review_status={ledger.source_review_status} "
        f"target_table={ledger.target_table} "
        f"request_count={ledger.request_count} "
        f"decision_count={ledger.decision_count} "
        f"pending_decisions={ledger.pending_decision_count} "
        f"approved_decisions={ledger.approved_decision_count} "
        f"deferred_decisions={ledger.deferred_decision_count} "
        f"more_evidence_decisions={ledger.more_evidence_decision_count} "
        f"approval_boundary={ledger.approval_boundary} "
        f"requested_action={ledger.requested_action} "
        f"allowed_actions={format_allowed_actions(ledger.allowed_actions)} "
        f"migration_applied={ledger.migration_applied_count} "
        f"table_created={ledger.table_created_count} "
        f"operator_approval_rows_created={ledger.operator_approval_row_count} "
        f"approval_requests_created={ledger.created_approval_request_count} "
        f"existing_approval_requests={ledger.existing_approval_request_count} "
        f"recommended_next_step={ledger.recommended_next_step} "
        f"report={ledger.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    return ",".join(actions) if actions else "none"


def _is_ready_source_request(
    source_request: ExpansionOperatorApprovalSchemaMigrationApprovalRequest,
) -> bool:
    return (
        source_request.status == OPERATOR_APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUIRED
        and source_request.target_table == TARGET_TABLE
        and source_request.request_count == 1
        and source_request.approval_boundary == APPROVAL_BOUNDARY
        and source_request.requested_action == REQUESTED_ACTION
        and source_request.allowed_actions == ALLOWED_ACTIONS
        and source_request.migration_applied_count == 0
        and source_request.table_created_count == 0
        and source_request.operator_approval_row_count == 0
        and source_request.created_approval_request_count == 0
    )


def _decision_item(
    source_request: ExpansionOperatorApprovalSchemaMigrationApprovalRequest,
) -> dict[str, Any]:
    return {
        "decision_status": "pending_operator_action",
        "requested_action": source_request.requested_action,
        "approval_boundary": source_request.approval_boundary,
        "target_table": source_request.target_table,
        "source_request_id": source_request.id,
        "source_plan_id": source_request.source_plan_id,
        "source_decision_id": source_request.source_decision_id,
        "allowed_actions": source_request.allowed_actions,
        "reason": "operator must approve, defer, or request more evidence before schema migration",
    }


def _render_decision_item_line(item: dict[str, Any]) -> str:
    return (
        f"- decision_status={item['decision_status']} "
        f"requested_action={item['requested_action']} "
        f"approval_boundary={item['approval_boundary']} "
        f"target_table={item['target_table']} "
        f"allowed_actions={format_allowed_actions(item['allowed_actions'])} "
        f"reason={item['reason']}"
    )
