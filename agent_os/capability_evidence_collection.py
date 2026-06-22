from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityApprovalBoundaryMatrix,
    CapabilityEvidenceCollectionPlan,
    Storage,
)


EVIDENCE_REQUIRED = "evidence_required"
NO_EVIDENCE_REQUIRED = "no_evidence_required"
APPROVAL_BOUNDARY_MATRIX_MISSING = "approval_boundary_matrix_missing"
COLLECTION_MODE = "manual_operator_supplied"
EVIDENCE_MISSING = "missing"
REPORT_PATH = "docs/capability-evidence-collection-plan.md"


def write_capability_evidence_collection_plan(
    root: Path,
) -> tuple[Path, CapabilityEvidenceCollectionPlan]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    matrices = storage.list_recent_capability_approval_boundary_matrices(limit=1)
    source_matrix = matrices[0] if matrices else None
    plan = _plan_from_latest_matrix(
        storage=storage,
        source_matrix=source_matrix,
        report_path=REPORT_PATH,
    )
    report_path = root / plan.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_evidence_collection_plan_report(plan, source_matrix),
        encoding="utf-8",
    )
    return report_path, plan


def render_capability_evidence_collection_plan_report(
    plan: CapabilityEvidenceCollectionPlan,
    source_matrix: CapabilityApprovalBoundaryMatrix | None,
) -> str:
    lines = [
        "# Capability Evidence Collection Plan",
        "",
        f"- id: {plan.id}",
        f"- status: {plan.status}",
        f"- source_matrix_id: {plan.source_matrix_id or 'none'}",
        f"- source_matrix_status: {plan.source_matrix_status}",
        f"- capability_count: {plan.capability_count}",
        f"- evidence_items: {plan.evidence_item_count}",
        f"- manual_collection: {plan.manual_collection_count}",
        f"- approvals_required: {plan.approval_required_count}",
        f"- boundaries: {plan.boundary_count}",
        f"- recommended_commands: {format_recommended_commands(plan.recommended_commands)}",
        f"- report_path: {plan.report_path}",
        f"- created_at: {plan.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {plan.reason}",
        "",
        "## Evidence Items",
        "",
    ]
    if plan.evidence_items:
        lines.extend(render_evidence_item_line(item) for item in plan.evidence_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Approval Boundary Matrix", ""])
    if source_matrix is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_matrix.id}",
                f"- status: {source_matrix.status}",
                f"- boundaries: {source_matrix.boundary_count}",
                f"- gaps: {source_matrix.gap_count}",
                f"- approvals_required: {source_matrix.approval_required_count}",
                f"- report: {source_matrix.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local evidence collection plan.",
            "- Does not create approval boundary matrices as a side effect.",
            "- Does not create proof gap indexes as a side effect.",
            "- Does not create readiness reviews as a side effect.",
            "- Does not create capability ledgers as a side effect.",
            "- Does not collect evidence automatically.",
            "- Does not approve capabilities automatically.",
            "- Does not generate proof artifacts automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not retry or replay work.",
            "- Does not change routing or claims.",
            "- Does not track real spend or mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_capability_evidence_collection_plan_line(
    plan: CapabilityEvidenceCollectionPlan,
) -> str:
    return (
        f"- {plan.id}: status={plan.status} "
        f"source_matrix={plan.source_matrix_id or 'none'} "
        f"source_status={plan.source_matrix_status} "
        f"evidence_items={plan.evidence_item_count} "
        f"manual_collection={plan.manual_collection_count} "
        f"approvals_required={plan.approval_required_count} "
        f"boundaries={plan.boundary_count} "
        f"recommended_commands={format_recommended_commands(plan.recommended_commands)} "
        f"report={plan.report_path}"
    )


def render_evidence_item_line(item: dict[str, str]) -> str:
    return (
        f"- {item['capability']}: evidence_item={item['evidence_item']} "
        f"collection_mode={item['collection_mode']} "
        f"evidence_state={item['evidence_state']} "
        f"approval_boundary={item['approval_boundary']} "
        f"routing_effect={item['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _plan_from_latest_matrix(
    *,
    storage: Storage,
    source_matrix: CapabilityApprovalBoundaryMatrix | None,
    report_path: str,
) -> CapabilityEvidenceCollectionPlan:
    if source_matrix is None:
        return storage.record_capability_evidence_collection_plan(
            status=APPROVAL_BOUNDARY_MATRIX_MISSING,
            source_matrix_id=None,
            source_matrix_status="none",
            capability_count=0,
            evidence_item_count=0,
            manual_collection_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["capability-approval-boundary-matrix"],
            reason="No capability approval boundary matrix exists yet.",
            evidence_items=[],
            report_path=report_path,
        )

    if (
        source_matrix.status != "no_approval_required"
        and not source_matrix.matrix_entries
        and source_matrix.recommended_commands
    ):
        return storage.record_capability_evidence_collection_plan(
            status=APPROVAL_BOUNDARY_MATRIX_MISSING,
            source_matrix_id=source_matrix.id,
            source_matrix_status=source_matrix.status,
            capability_count=source_matrix.capability_count,
            evidence_item_count=0,
            manual_collection_count=0,
            approval_required_count=source_matrix.approval_required_count,
            boundary_count=source_matrix.boundary_count,
            recommended_commands=source_matrix.recommended_commands,
            reason=(
                "Latest capability approval boundary matrix is incomplete; "
                "run the recommended upstream command before planning evidence collection."
            ),
            evidence_items=[],
            report_path=report_path,
        )

    evidence_items = [
        _evidence_item_from_matrix_entry(entry)
        for entry in source_matrix.matrix_entries
    ]
    status = EVIDENCE_REQUIRED if evidence_items else NO_EVIDENCE_REQUIRED
    reason = (
        "Capability evidence remains manual until an operator supplies evidence paths and approvals."
        if evidence_items
        else "No capability evidence collection items are required by the latest approval boundary matrix."
    )
    return storage.record_capability_evidence_collection_plan(
        status=status,
        source_matrix_id=source_matrix.id,
        source_matrix_status=source_matrix.status,
        capability_count=source_matrix.capability_count,
        evidence_item_count=len(evidence_items),
        manual_collection_count=sum(
            1 for item in evidence_items if item["collection_mode"] == COLLECTION_MODE
        ),
        approval_required_count=source_matrix.approval_required_count,
        boundary_count=source_matrix.boundary_count,
        recommended_commands=[],
        reason=reason,
        evidence_items=evidence_items,
        report_path=report_path,
    )


def _evidence_item_from_matrix_entry(entry: dict[str, str]) -> dict[str, str]:
    return {
        "capability": entry["capability"],
        "evidence_item": entry["next_proof"],
        "required_evidence": entry["required_evidence"],
        "collection_mode": COLLECTION_MODE,
        "evidence_state": EVIDENCE_MISSING,
        "approval_boundary": entry["approval_boundary"],
        "decision_state": entry["decision_state"],
        "routing_effect": entry["routing_effect"],
    }
