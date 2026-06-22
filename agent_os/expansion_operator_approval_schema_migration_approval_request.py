from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.expansion_operator_approval_schema_migration_plan import (
    OPERATOR_APPROVAL_SCHEMA_MIGRATION_PLAN_READY,
    TARGET_TABLE,
)
from agent_os.storage import (
    ExpansionOperatorApprovalSchemaMigrationApprovalRequest,
    ExpansionOperatorApprovalSchemaMigrationPlan,
    Storage,
)


OPERATOR_APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUIRED = (
    "operator_approval_schema_migration_approval_required"
)
MISSING_APPROVAL_SCHEMA_MIGRATION_PLAN = "missing_approval_schema_migration_plan"
APPROVAL_SCHEMA_MIGRATION_PLAN_NOT_READY = (
    "approval_schema_migration_plan_not_ready"
)
REQUESTED_ACTION = "apply_operator_approval_requests_schema"
APPROVAL_BOUNDARY = "schema_migration"
REQUEST_TYPE = "schema_migration"
ALLOWED_ACTIONS = ["approve", "defer", "request_more_evidence"]
RECOMMENDED_NEXT_STEP = "operator_approval_schema_migration_operator_decision_required"
REPORT_PATH = (
    "docs/expansion-operator-approval-schema-migration-approval-request.md"
)


def write_expansion_operator_approval_schema_migration_approval_request(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalSchemaMigrationApprovalRequest]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    plans = storage.list_recent_expansion_operator_approval_schema_migration_plans(
        limit=1,
    )
    source_plan = plans[0] if plans else None

    if source_plan is None:
        status = MISSING_APPROVAL_SCHEMA_MIGRATION_PLAN
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
        approval_items: list[dict[str, Any]] = []
        recommended_next_step = "expansion-operator-approval-schema-migration-plan"
    elif not _is_ready_source_plan(source_plan):
        status = APPROVAL_SCHEMA_MIGRATION_PLAN_NOT_READY
        source_plan_id = source_plan.id
        source_plan_status = source_plan.status
        source_decision_id = source_plan.source_decision_id
        source_decision_status = source_plan.source_decision_status
        source_review_id = source_plan.source_review_id
        source_review_status = source_plan.source_review_status
        target_table = source_plan.target_table
        planned_column_count = source_plan.planned_column_count
        planned_index_count = source_plan.planned_index_count
        migration_step_count = source_plan.migration_step_count
        affected_request_count = source_plan.affected_request_count
        schema_gap_count = source_plan.schema_gap_count
        request_count = 0
        approval_items = []
        recommended_next_step = source_plan.recommended_next_step
    else:
        status = OPERATOR_APPROVAL_SCHEMA_MIGRATION_APPROVAL_REQUIRED
        source_plan_id = source_plan.id
        source_plan_status = source_plan.status
        source_decision_id = source_plan.source_decision_id
        source_decision_status = source_plan.source_decision_status
        source_review_id = source_plan.source_review_id
        source_review_status = source_plan.source_review_status
        target_table = source_plan.target_table
        planned_column_count = source_plan.planned_column_count
        planned_index_count = source_plan.planned_index_count
        migration_step_count = source_plan.migration_step_count
        affected_request_count = source_plan.affected_request_count
        schema_gap_count = source_plan.schema_gap_count
        request_count = 1
        approval_items = [_approval_item(source_plan)]
        recommended_next_step = RECOMMENDED_NEXT_STEP

    request = (
        storage.record_expansion_operator_approval_schema_migration_approval_request(
            status=status,
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
            approval_boundary=APPROVAL_BOUNDARY if request_count else "none",
            requested_action=REQUESTED_ACTION if request_count else "none",
            allowed_actions=ALLOWED_ACTIONS if request_count else [],
            migration_applied_count=0,
            table_created_count=0,
            operator_approval_row_count=0,
            created_approval_request_count=0,
            existing_approval_request_count=storage.count_approval_requests(),
            recommended_next_step=recommended_next_step,
            approval_items=approval_items,
            report_path=REPORT_PATH,
        )
    )
    report_path = root / request.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_schema_migration_approval_request_report(
            request
        ),
        encoding="utf-8",
    )
    return report_path, request


def render_expansion_operator_approval_schema_migration_approval_request_report(
    request: ExpansionOperatorApprovalSchemaMigrationApprovalRequest,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Migration Approval Request",
        "",
        f"- id: {request.id}",
        f"- status: {request.status}",
        f"- source_plan: {request.source_plan_id}",
        f"- source_status: {request.source_plan_status}",
        f"- source_decision: {request.source_decision_id}",
        f"- source_decision_status: {request.source_decision_status}",
        f"- source_review: {request.source_review_id}",
        f"- source_review_status: {request.source_review_status}",
        f"- target_table: {request.target_table}",
        f"- planned_columns: {request.planned_column_count}",
        f"- planned_indexes: {request.planned_index_count}",
        f"- migration_steps: {request.migration_step_count}",
        f"- affected_requests: {request.affected_request_count}",
        f"- schema_gaps: {request.schema_gap_count}",
        f"- request_count: {request.request_count}",
        f"- approval_boundary: {request.approval_boundary}",
        f"- requested_action: {request.requested_action}",
        f"- allowed_actions: {format_allowed_actions(request.allowed_actions)}",
        f"- migration_applied: {request.migration_applied_count}",
        f"- table_created: {request.table_created_count}",
        f"- operator_approval_rows_created: {request.operator_approval_row_count}",
        f"- approval_requests_created: {request.created_approval_request_count}",
        f"- existing_approval_requests: {request.existing_approval_request_count}",
        f"- recommended_next_step: {request.recommended_next_step}",
        f"- report_path: {request.report_path}",
        f"- created_at: {request.created_at}",
        "",
        "## Approval Items",
        "",
    ]
    if request.approval_items:
        lines.extend(_render_approval_item_line(item) for item in request.approval_items)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval schema migration approval request.",
            "- Does not apply schema migrations.",
            "- Does not create operator_approval_requests table.",
            "- Does not create operator_approval_requests rows.",
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


def render_expansion_operator_approval_schema_migration_approval_request_line(
    request: ExpansionOperatorApprovalSchemaMigrationApprovalRequest,
) -> str:
    return (
        f"- {request.id}: status={request.status} "
        f"source_plan={request.source_plan_id} "
        f"source_status={request.source_plan_status} "
        f"source_decision={request.source_decision_id} "
        f"source_decision_status={request.source_decision_status} "
        f"source_review={request.source_review_id} "
        f"source_review_status={request.source_review_status} "
        f"target_table={request.target_table} "
        f"planned_columns={request.planned_column_count} "
        f"planned_indexes={request.planned_index_count} "
        f"migration_steps={request.migration_step_count} "
        f"affected_requests={request.affected_request_count} "
        f"schema_gaps={request.schema_gap_count} "
        f"request_count={request.request_count} "
        f"approval_boundary={request.approval_boundary} "
        f"requested_action={request.requested_action} "
        f"allowed_actions={format_allowed_actions(request.allowed_actions)} "
        f"migration_applied={request.migration_applied_count} "
        f"table_created={request.table_created_count} "
        f"operator_approval_rows_created={request.operator_approval_row_count} "
        f"approval_requests_created={request.created_approval_request_count} "
        f"existing_approval_requests={request.existing_approval_request_count} "
        f"recommended_next_step={request.recommended_next_step} "
        f"report={request.report_path}"
    )


def format_allowed_actions(actions: list[str]) -> str:
    return ",".join(actions) if actions else "none"


def _is_ready_source_plan(
    source_plan: ExpansionOperatorApprovalSchemaMigrationPlan,
) -> bool:
    return (
        source_plan.status == OPERATOR_APPROVAL_SCHEMA_MIGRATION_PLAN_READY
        and source_plan.target_table == TARGET_TABLE
        and source_plan.migration_applied_count == 0
        and source_plan.table_created_count == 0
    )


def _approval_item(
    source_plan: ExpansionOperatorApprovalSchemaMigrationPlan,
) -> dict[str, Any]:
    return {
        "request_type": REQUEST_TYPE,
        "requested_action": REQUESTED_ACTION,
        "approval_status": "not_created",
        "approval_boundary": APPROVAL_BOUNDARY,
        "target_table": source_plan.target_table,
        "source_plan_id": source_plan.id,
        "source_decision_id": source_plan.source_decision_id,
        "allowed_actions": ALLOWED_ACTIONS,
        "reason": "operator approval required before applying planned schema migration",
    }


def _render_approval_item_line(item: dict[str, Any]) -> str:
    return (
        f"- request_type={item['request_type']} "
        f"requested_action={item['requested_action']} "
        f"approval_status={item['approval_status']} "
        f"approval_boundary={item['approval_boundary']} "
        f"target_table={item['target_table']} "
        f"allowed_actions={format_allowed_actions(item['allowed_actions'])} "
        f"reason={item['reason']}"
    )
