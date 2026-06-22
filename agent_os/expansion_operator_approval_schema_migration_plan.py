from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.expansion_operator_approval_schema_decision import (
    APPROVAL_SCHEMA_DECISION_READY,
    RECOMMENDED_OPTION,
)
from agent_os.storage import (
    ExpansionOperatorApprovalSchemaDecision,
    ExpansionOperatorApprovalSchemaMigrationPlan,
    Storage,
)


OPERATOR_APPROVAL_SCHEMA_MIGRATION_PLAN_READY = (
    "operator_approval_schema_migration_plan_ready"
)
MISSING_APPROVAL_SCHEMA_DECISION = "missing_approval_schema_decision"
APPROVAL_SCHEMA_DECISION_NOT_READY = "approval_schema_decision_not_ready"
TARGET_TABLE = "operator_approval_requests"
RECOMMENDED_NEXT_STEP = "operator_approval_schema_migration_approval_required"
REPORT_PATH = "docs/expansion-operator-approval-schema-migration-plan.md"


def write_expansion_operator_approval_schema_migration_plan(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalSchemaMigrationPlan]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    decisions = storage.list_recent_expansion_operator_approval_schema_decisions(limit=1)
    source_decision = decisions[0] if decisions else None

    if source_decision is None:
        status = MISSING_APPROVAL_SCHEMA_DECISION
        source_decision_id = "none"
        source_decision_status = "none"
        source_review_id = "none"
        source_review_status = "none"
        source_draft_id = "none"
        source_ledger_id = "none"
        source_checklist_id = "none"
        source_index_id = "none"
        source_brief_id = "none"
        source_audit_id = "none"
        recommended_option = "none"
        affected_request_count = 0
        schema_gap_count = 0
        missing_field_count = 0
        external_request_count = 0
        capability_request_count = 0
        planned_columns: list[dict[str, Any]] = []
        planned_indexes: list[dict[str, Any]] = []
        migration_steps: list[dict[str, Any]] = []
        target_table = "none"
        recommended_next_step = "expansion-operator-approval-schema-decision"
    elif not _is_ready_source_decision(source_decision):
        status = APPROVAL_SCHEMA_DECISION_NOT_READY
        source_decision_id = source_decision.id
        source_decision_status = source_decision.status
        source_review_id = source_decision.source_review_id
        source_review_status = source_decision.source_review_status
        source_draft_id = source_decision.source_draft_id
        source_ledger_id = source_decision.source_ledger_id
        source_checklist_id = source_decision.source_checklist_id
        source_index_id = source_decision.source_index_id
        source_brief_id = source_decision.source_brief_id
        source_audit_id = source_decision.source_audit_id
        recommended_option = source_decision.recommended_option
        affected_request_count = source_decision.affected_request_count
        schema_gap_count = source_decision.schema_gap_count
        missing_field_count = source_decision.missing_field_count
        external_request_count = source_decision.external_request_count
        capability_request_count = source_decision.capability_request_count
        planned_columns = []
        planned_indexes = []
        migration_steps = []
        target_table = "none"
        recommended_next_step = source_decision.recommended_next_step
    else:
        status = OPERATOR_APPROVAL_SCHEMA_MIGRATION_PLAN_READY
        source_decision_id = source_decision.id
        source_decision_status = source_decision.status
        source_review_id = source_decision.source_review_id
        source_review_status = source_decision.source_review_status
        source_draft_id = source_decision.source_draft_id
        source_ledger_id = source_decision.source_ledger_id
        source_checklist_id = source_decision.source_checklist_id
        source_index_id = source_decision.source_index_id
        source_brief_id = source_decision.source_brief_id
        source_audit_id = source_decision.source_audit_id
        recommended_option = source_decision.recommended_option
        affected_request_count = source_decision.affected_request_count
        schema_gap_count = source_decision.schema_gap_count
        missing_field_count = source_decision.missing_field_count
        external_request_count = source_decision.external_request_count
        capability_request_count = source_decision.capability_request_count
        planned_columns = _planned_columns()
        planned_indexes = _planned_indexes()
        migration_steps = _migration_steps()
        target_table = TARGET_TABLE
        recommended_next_step = RECOMMENDED_NEXT_STEP

    plan = storage.record_expansion_operator_approval_schema_migration_plan(
        status=status,
        source_decision_id=source_decision_id,
        source_decision_status=source_decision_status,
        source_review_id=source_review_id,
        source_review_status=source_review_status,
        source_draft_id=source_draft_id,
        source_ledger_id=source_ledger_id,
        source_checklist_id=source_checklist_id,
        source_index_id=source_index_id,
        source_brief_id=source_brief_id,
        source_audit_id=source_audit_id,
        recommended_option=recommended_option,
        target_table=target_table,
        affected_request_count=affected_request_count,
        schema_gap_count=schema_gap_count,
        missing_field_count=missing_field_count,
        external_request_count=external_request_count,
        capability_request_count=capability_request_count,
        planned_column_count=len(planned_columns),
        planned_index_count=len(planned_indexes),
        migration_step_count=len(migration_steps),
        migration_applied_count=0,
        table_created_count=0,
        operator_approval_row_count=0,
        created_approval_request_count=0,
        existing_approval_request_count=storage.count_approval_requests(),
        recommended_next_step=recommended_next_step,
        planned_columns=planned_columns,
        planned_indexes=planned_indexes,
        migration_steps=migration_steps,
        report_path=REPORT_PATH,
    )
    report_path = root / plan.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_schema_migration_plan_report(plan),
        encoding="utf-8",
    )
    return report_path, plan


def render_expansion_operator_approval_schema_migration_plan_report(
    plan: ExpansionOperatorApprovalSchemaMigrationPlan,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Migration Plan",
        "",
        f"- id: {plan.id}",
        f"- status: {plan.status}",
        f"- source_decision: {plan.source_decision_id}",
        f"- source_status: {plan.source_decision_status}",
        f"- source_review: {plan.source_review_id}",
        f"- source_review_status: {plan.source_review_status}",
        f"- source_draft: {plan.source_draft_id}",
        f"- source_ledger: {plan.source_ledger_id}",
        f"- source_checklist: {plan.source_checklist_id}",
        f"- source_index: {plan.source_index_id}",
        f"- source_brief: {plan.source_brief_id}",
        f"- source_audit: {plan.source_audit_id}",
        f"- recommended_option: {plan.recommended_option}",
        f"- target_table: {plan.target_table}",
        f"- affected_requests: {plan.affected_request_count}",
        f"- schema_gaps: {plan.schema_gap_count}",
        f"- missing_fields: {plan.missing_field_count}",
        f"- external_requests: {plan.external_request_count}",
        f"- capability_requests: {plan.capability_request_count}",
        f"- planned_columns: {plan.planned_column_count}",
        f"- planned_indexes: {plan.planned_index_count}",
        f"- migration_steps: {plan.migration_step_count}",
        f"- migration_applied: {plan.migration_applied_count}",
        f"- table_created: {plan.table_created_count}",
        f"- operator_approval_rows_created: {plan.operator_approval_row_count}",
        f"- approval_requests_created: {plan.created_approval_request_count}",
        f"- existing_approval_requests: {plan.existing_approval_request_count}",
        f"- recommended_next_step: {plan.recommended_next_step}",
        f"- report_path: {plan.report_path}",
        f"- created_at: {plan.created_at}",
        "",
        "## Planned Columns",
        "",
    ]
    if plan.planned_columns:
        lines.extend(
            _render_column_line(column) for column in plan.planned_columns
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Planned Indexes", ""])
    if plan.planned_indexes:
        lines.extend(_render_index_line(index) for index in plan.planned_indexes)
    else:
        lines.append("- none")

    lines.extend(["", "## Migration Steps", ""])
    if plan.migration_steps:
        lines.extend(_render_step_line(step) for step in plan.migration_steps)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval schema migration plan.",
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


def render_expansion_operator_approval_schema_migration_plan_line(
    plan: ExpansionOperatorApprovalSchemaMigrationPlan,
) -> str:
    return (
        f"- {plan.id}: status={plan.status} "
        f"source_decision={plan.source_decision_id} "
        f"source_status={plan.source_decision_status} "
        f"source_review={plan.source_review_id} "
        f"source_review_status={plan.source_review_status} "
        f"source_draft={plan.source_draft_id} "
        f"source_ledger={plan.source_ledger_id} "
        f"source_checklist={plan.source_checklist_id} "
        f"source_index={plan.source_index_id} "
        f"source_brief={plan.source_brief_id} "
        f"source_audit={plan.source_audit_id} "
        f"recommended_option={plan.recommended_option} "
        f"target_table={plan.target_table} "
        f"affected_requests={plan.affected_request_count} "
        f"schema_gaps={plan.schema_gap_count} "
        f"missing_fields={plan.missing_field_count} "
        f"external_requests={plan.external_request_count} "
        f"capability_requests={plan.capability_request_count} "
        f"planned_columns={plan.planned_column_count} "
        f"planned_indexes={plan.planned_index_count} "
        f"migration_steps={plan.migration_step_count} "
        f"migration_applied={plan.migration_applied_count} "
        f"table_created={plan.table_created_count} "
        f"operator_approval_rows_created={plan.operator_approval_row_count} "
        f"approval_requests_created={plan.created_approval_request_count} "
        f"existing_approval_requests={plan.existing_approval_request_count} "
        f"recommended_next_step={plan.recommended_next_step} "
        f"report={plan.report_path}"
    )


def _is_ready_source_decision(
    source_decision: ExpansionOperatorApprovalSchemaDecision,
) -> bool:
    return (
        source_decision.status == APPROVAL_SCHEMA_DECISION_READY
        and source_decision.recommended_option == RECOMMENDED_OPTION
        and source_decision.schema_object_count > 0
    )


def _planned_columns() -> list[dict[str, str]]:
    return [
        {"name": "id", "definition": "text primary key"},
        {"name": "source_decision_id", "definition": "text not null"},
        {"name": "source_review_id", "definition": "text not null"},
        {"name": "source_draft_id", "definition": "text not null"},
        {"name": "source_ledger_id", "definition": "text not null"},
        {"name": "source_checklist_id", "definition": "text not null"},
        {"name": "source_index_id", "definition": "text not null"},
        {"name": "source_brief_id", "definition": "text not null"},
        {"name": "source_audit_id", "definition": "text not null"},
        {"name": "subject_type", "definition": "text not null"},
        {"name": "subject_key", "definition": "text not null"},
        {"name": "request_kind", "definition": "text not null"},
        {"name": "capability_key", "definition": "text"},
        {"name": "approval_boundary", "definition": "text not null"},
        {"name": "allowed_actions", "definition": "text not null"},
        {"name": "status", "definition": "text not null"},
        {"name": "reason", "definition": "text not null"},
        {"name": "policy_name", "definition": "text not null"},
        {"name": "policy_version", "definition": "text not null"},
        {"name": "requested_by", "definition": "text not null"},
        {"name": "decided_by", "definition": "text"},
        {"name": "decision_note", "definition": "text"},
        {"name": "requested_at", "definition": "text not null"},
        {"name": "decided_at", "definition": "text"},
        {"name": "evidence_path", "definition": "text"},
        {"name": "created_at", "definition": "text not null"},
    ]


def _planned_indexes() -> list[dict[str, Any]]:
    return [
        {
            "name": "idx_operator_approval_requests_status",
            "columns": ["status"],
            "status": "planned",
        },
        {
            "name": "idx_operator_approval_requests_subject",
            "columns": ["subject_type", "subject_key"],
            "status": "planned",
        },
        {
            "name": "idx_operator_approval_requests_source_decision",
            "columns": ["source_decision_id"],
            "status": "planned",
        },
        {
            "name": "idx_operator_approval_requests_requested_at",
            "columns": ["requested_at"],
            "status": "planned",
        },
    ]


def _migration_steps() -> list[dict[str, str]]:
    return [
        {
            "action": "create_table",
            "target": TARGET_TABLE,
            "status": "planned",
        },
        {
            "action": "create_indexes",
            "target": TARGET_TABLE,
            "status": "planned",
        },
        {
            "action": "preserve_existing_approval_requests_contract",
            "target": "approval_requests",
            "status": "planned",
        },
        {
            "action": "require_operator_approval_before_apply",
            "target": TARGET_TABLE,
            "status": "planned",
        },
    ]


def _render_column_line(column: dict[str, str]) -> str:
    return f"- column={column['name']} definition={column['definition']}"


def _render_index_line(index: dict[str, Any]) -> str:
    return (
        f"- index={index['name']} "
        f"columns={','.join(index['columns'])} "
        f"status={index['status']}"
    )


def _render_step_line(step: dict[str, str]) -> str:
    return (
        f"- step={step['action']} "
        f"target={step['target']} "
        f"status={step['status']}"
    )
