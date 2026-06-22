from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_os.expansion_operator_approval_request_review import (
    APPROVAL_REQUEST_SCHEMA_REVIEW_REQUIRED,
    MISSING_APPROVAL_REQUEST_FIELDS,
)
from agent_os.storage import (
    ExpansionOperatorApprovalRequestReview,
    ExpansionOperatorApprovalSchemaDecision,
    Storage,
)


APPROVAL_SCHEMA_DECISION_READY = "approval_schema_decision_ready"
MISSING_APPROVAL_REQUEST_REVIEW = "missing_approval_request_review"
APPROVAL_REQUEST_REVIEW_NOT_READY = "approval_request_review_not_ready"
RECOMMENDED_OPTION = "operator_approval_requests_table"
RECOMMENDED_NEXT_STEP = "operator_approval_schema_migration_plan_required"
REPORT_PATH = "docs/expansion-operator-approval-schema-decision.md"


def write_expansion_operator_approval_schema_decision(
    root: Path,
) -> tuple[Path, ExpansionOperatorApprovalSchemaDecision]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    reviews = storage.list_recent_expansion_operator_approval_request_reviews(limit=1)
    source_review = reviews[0] if reviews else None

    if source_review is None:
        status = MISSING_APPROVAL_REQUEST_REVIEW
        source_review_id = "none"
        source_review_status = "none"
        source_draft_id = "none"
        source_ledger_id = "none"
        source_checklist_id = "none"
        source_index_id = "none"
        source_brief_id = "none"
        source_audit_id = "none"
        affected_request_count = 0
        schema_gap_count = 0
        missing_fields: list[str] = []
        external_request_count = 0
        capability_request_count = 0
        decision_options: list[dict[str, Any]] = []
        recommended_option = "none"
        recommended_next_step = "expansion-operator-approval-request-review"
    elif not _is_ready_source_review(source_review):
        status = APPROVAL_REQUEST_REVIEW_NOT_READY
        source_review_id = source_review.id
        source_review_status = source_review.status
        source_draft_id = source_review.source_draft_id
        source_ledger_id = source_review.source_ledger_id
        source_checklist_id = source_review.source_checklist_id
        source_index_id = source_review.source_index_id
        source_brief_id = source_review.source_brief_id
        source_audit_id = source_review.source_audit_id
        affected_request_count = source_review.review_item_count
        schema_gap_count = source_review.schema_gap_count
        missing_fields = _missing_fields(source_review)
        external_request_count = source_review.external_request_count
        capability_request_count = source_review.capability_request_count
        decision_options = []
        recommended_option = "none"
        recommended_next_step = source_review.recommended_next_step
    else:
        status = APPROVAL_SCHEMA_DECISION_READY
        source_review_id = source_review.id
        source_review_status = source_review.status
        source_draft_id = source_review.source_draft_id
        source_ledger_id = source_review.source_ledger_id
        source_checklist_id = source_review.source_checklist_id
        source_index_id = source_review.source_index_id
        source_brief_id = source_review.source_brief_id
        source_audit_id = source_review.source_audit_id
        affected_request_count = source_review.review_item_count
        schema_gap_count = source_review.schema_gap_count
        missing_fields = _missing_fields(source_review)
        external_request_count = source_review.external_request_count
        capability_request_count = source_review.capability_request_count
        decision_options = _decision_options(missing_fields)
        recommended_option = RECOMMENDED_OPTION
        recommended_next_step = RECOMMENDED_NEXT_STEP

    rejected_option_count = sum(
        1 for option in decision_options if option["disposition"] == "rejected"
    )
    schema_object_count = len(
        {
            option["schema_object"]
            for option in decision_options
            if option["disposition"] == "recommended"
            and option["schema_object"] != "none"
        }
    )

    decision = storage.record_expansion_operator_approval_schema_decision(
        status=status,
        source_review_id=source_review_id,
        source_review_status=source_review_status,
        source_draft_id=source_draft_id,
        source_ledger_id=source_ledger_id,
        source_checklist_id=source_checklist_id,
        source_index_id=source_index_id,
        source_brief_id=source_brief_id,
        source_audit_id=source_audit_id,
        affected_request_count=affected_request_count,
        schema_gap_count=schema_gap_count,
        missing_field_count=len(missing_fields),
        missing_fields=missing_fields,
        external_request_count=external_request_count,
        capability_request_count=capability_request_count,
        decision_option_count=len(decision_options),
        recommended_option=recommended_option,
        rejected_option_count=rejected_option_count,
        schema_object_count=schema_object_count,
        migration_applied_count=0,
        created_approval_request_count=0,
        existing_approval_request_count=storage.count_approval_requests(),
        recommended_next_step=recommended_next_step,
        decision_options=decision_options,
        report_path=REPORT_PATH,
    )
    report_path = root / decision.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_expansion_operator_approval_schema_decision_report(decision),
        encoding="utf-8",
    )
    return report_path, decision


def render_expansion_operator_approval_schema_decision_report(
    decision: ExpansionOperatorApprovalSchemaDecision,
) -> str:
    lines = [
        "# Expansion Operator Approval Schema Decision",
        "",
        f"- id: {decision.id}",
        f"- status: {decision.status}",
        f"- source_review: {decision.source_review_id}",
        f"- source_status: {decision.source_review_status}",
        f"- source_draft: {decision.source_draft_id}",
        f"- source_ledger: {decision.source_ledger_id}",
        f"- source_checklist: {decision.source_checklist_id}",
        f"- source_index: {decision.source_index_id}",
        f"- source_brief: {decision.source_brief_id}",
        f"- source_audit: {decision.source_audit_id}",
        f"- affected_requests: {decision.affected_request_count}",
        f"- schema_gaps: {decision.schema_gap_count}",
        f"- missing_fields: {decision.missing_field_count}",
        f"- external_requests: {decision.external_request_count}",
        f"- capability_requests: {decision.capability_request_count}",
        f"- decision_options: {decision.decision_option_count}",
        f"- recommended_option: {decision.recommended_option}",
        f"- rejected_options: {decision.rejected_option_count}",
        f"- schema_objects: {decision.schema_object_count}",
        f"- migration_applied: {decision.migration_applied_count}",
        f"- created_approval_requests: {decision.created_approval_request_count}",
        f"- existing_approval_requests: {decision.existing_approval_request_count}",
        f"- recommended_next_step: {decision.recommended_next_step}",
        f"- report_path: {decision.report_path}",
        f"- created_at: {decision.created_at}",
        "",
        "## Decision Options",
        "",
    ]
    if decision.decision_options:
        lines.extend(
            _render_decision_option_line(option)
            for option in decision.decision_options
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local expansion operator approval schema decision.",
            "- Does not apply schema migrations.",
            "- Does not create approval_requests rows.",
            "- Does not create operator approval rows.",
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


def render_expansion_operator_approval_schema_decision_line(
    decision: ExpansionOperatorApprovalSchemaDecision,
) -> str:
    return (
        f"- {decision.id}: status={decision.status} "
        f"source_review={decision.source_review_id} "
        f"source_status={decision.source_review_status} "
        f"source_draft={decision.source_draft_id} "
        f"source_ledger={decision.source_ledger_id} "
        f"source_checklist={decision.source_checklist_id} "
        f"source_index={decision.source_index_id} "
        f"source_brief={decision.source_brief_id} "
        f"source_audit={decision.source_audit_id} "
        f"affected_requests={decision.affected_request_count} "
        f"schema_gaps={decision.schema_gap_count} "
        f"missing_fields={decision.missing_field_count} "
        f"external_requests={decision.external_request_count} "
        f"capability_requests={decision.capability_request_count} "
        f"decision_options={decision.decision_option_count} "
        f"recommended_option={decision.recommended_option} "
        f"rejected_options={decision.rejected_option_count} "
        f"schema_objects={decision.schema_object_count} "
        f"migration_applied={decision.migration_applied_count} "
        f"created_approval_requests={decision.created_approval_request_count} "
        f"existing_approval_requests={decision.existing_approval_request_count} "
        f"recommended_next_step={decision.recommended_next_step} "
        f"report={decision.report_path}"
    )


def _is_ready_source_review(
    source_review: ExpansionOperatorApprovalRequestReview,
) -> bool:
    return (
        source_review.status == APPROVAL_REQUEST_SCHEMA_REVIEW_REQUIRED
        and source_review.schema_gap_count > 0
        and source_review.review_item_count > 0
    )


def _missing_fields(
    source_review: ExpansionOperatorApprovalRequestReview,
) -> list[str]:
    fields: list[str] = []
    for item in source_review.review_items:
        for field in item.get("missing_approval_request_fields", []):
            if field not in fields:
                fields.append(field)
    return fields or list(MISSING_APPROVAL_REQUEST_FIELDS)


def _decision_options(missing_fields: list[str]) -> list[dict[str, Any]]:
    return [
        {
            "option": RECOMMENDED_OPTION,
            "disposition": "recommended",
            "schema_object": "operator_approval_requests",
            "schema_status": "not_applied",
            "reason": "preserves the existing task approval gate while modeling external and capability approval subjects explicitly",
            "missing_fields": missing_fields,
        },
        {
            "option": "make_approval_requests_task_fields_nullable",
            "disposition": "rejected",
            "schema_object": "approval_requests",
            "schema_status": "not_applied",
            "reason": "weakens the current task-approval contract and risks ambiguous task dispatch semantics",
            "missing_fields": missing_fields,
        },
        {
            "option": "synthesize_placeholder_tasks_for_operator_decisions",
            "disposition": "rejected",
            "schema_object": "tasks",
            "schema_status": "not_applied",
            "reason": "mixes non-executable operator decisions into the executable task queue",
            "missing_fields": missing_fields,
        },
    ]


def _render_decision_option_line(option: dict[str, Any]) -> str:
    return (
        f"- option={option['option']} "
        f"disposition={option['disposition']} "
        f"schema_object={option['schema_object']} "
        f"schema_status={option['schema_status']} "
        f"missing_fields={','.join(option['missing_fields'])} "
        f"reason={option['reason']}"
    )
