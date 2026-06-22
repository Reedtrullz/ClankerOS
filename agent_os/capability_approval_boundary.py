from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from agent_os.storage import (
    CapabilityApprovalBoundaryMatrix,
    CapabilityProofGapIndex,
    Storage,
)


APPROVAL_REQUIRED = "approval_required"
NO_APPROVAL_REQUIRED = "no_approval_required"
PROOF_GAP_INDEX_MISSING = "proof_gap_index_missing"
DECISION_BLOCKED = "blocked_until_proof_and_operator_approval"
REPORT_PATH = "docs/capability-approval-boundary-matrix.md"
APPROVAL_BOUNDARY = "explicit_operator_approval_required"


def write_capability_approval_boundary_matrix(
    root: Path,
) -> tuple[Path, CapabilityApprovalBoundaryMatrix]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    indexes = storage.list_recent_capability_proof_gap_indexes(limit=1)
    source_index = indexes[0] if indexes else None
    matrix = _matrix_from_latest_index(
        storage=storage,
        source_index=source_index,
        report_path=REPORT_PATH,
    )
    report_path = root / matrix.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_approval_boundary_matrix_report(matrix, source_index),
        encoding="utf-8",
    )
    return report_path, matrix


def render_capability_approval_boundary_matrix_report(
    matrix: CapabilityApprovalBoundaryMatrix,
    source_index: CapabilityProofGapIndex | None,
) -> str:
    lines = [
        "# Capability Approval Boundary Matrix",
        "",
        f"- id: {matrix.id}",
        f"- status: {matrix.status}",
        f"- source_index_id: {matrix.source_index_id or 'none'}",
        f"- source_index_status: {matrix.source_index_status}",
        f"- capability_count: {matrix.capability_count}",
        f"- boundaries: {matrix.boundary_count}",
        f"- gaps: {matrix.gap_count}",
        f"- blocked_capabilities: {matrix.blocked_capability_count}",
        f"- approvals_required: {matrix.approval_required_count}",
        f"- recommended_commands: {format_recommended_commands(matrix.recommended_commands)}",
        f"- report_path: {matrix.report_path}",
        f"- created_at: {matrix.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {matrix.reason}",
        "",
        "## Boundary Summary",
        "",
    ]
    if matrix.boundary_rows:
        lines.extend(render_boundary_row(row) for row in matrix.boundary_rows)
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Matrix", ""])
    if matrix.matrix_entries:
        lines.extend(render_matrix_entry_line(entry) for entry in matrix.matrix_entries)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Proof Gap Index", ""])
    if source_index is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_index.id}",
                f"- status: {source_index.status}",
                f"- gaps: {source_index.gap_count}",
                f"- missing_evidence: {source_index.missing_evidence_count}",
                f"- blocked_capabilities: {source_index.blocked_capability_count}",
                f"- report: {source_index.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local approval-boundary matrix.",
            "- Does not create proof gap indexes as a side effect.",
            "- Does not create readiness reviews as a side effect.",
            "- Does not create capability ledgers as a side effect.",
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


def render_capability_approval_boundary_matrix_line(
    matrix: CapabilityApprovalBoundaryMatrix,
) -> str:
    return (
        f"- {matrix.id}: status={matrix.status} "
        f"source_index={matrix.source_index_id or 'none'} "
        f"source_status={matrix.source_index_status} "
        f"boundaries={matrix.boundary_count} "
        f"gaps={matrix.gap_count} "
        f"blocked_capabilities={matrix.blocked_capability_count} "
        f"approvals_required={matrix.approval_required_count} "
        f"recommended_commands={format_recommended_commands(matrix.recommended_commands)} "
        f"report={matrix.report_path}"
    )


def render_boundary_row(row: dict[str, object]) -> str:
    return (
        f"- {row['approval_boundary']}: capabilities={row['capability_count']} "
        f"gaps={row['gap_count']} "
        f"approvals_required={row['approval_required_count']}"
    )


def render_matrix_entry_line(entry: dict[str, str]) -> str:
    return (
        f"- {entry['capability']}: approval_boundary={entry['approval_boundary']} "
        f"decision_state={entry['decision_state']} "
        f"gap={entry['gap']} "
        f"next_proof={entry['next_proof']} "
        f"routing_effect={entry['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _matrix_from_latest_index(
    *,
    storage: Storage,
    source_index: CapabilityProofGapIndex | None,
    report_path: str,
) -> CapabilityApprovalBoundaryMatrix:
    if source_index is None:
        return storage.record_capability_approval_boundary_matrix(
            status=PROOF_GAP_INDEX_MISSING,
            source_index_id=None,
            source_index_status="none",
            capability_count=0,
            boundary_count=0,
            gap_count=0,
            blocked_capability_count=0,
            approval_required_count=0,
            recommended_commands=["capability-proof-gap-index"],
            reason="No capability proof gap index exists yet.",
            boundary_rows=[],
            matrix_entries=[],
            report_path=report_path,
        )

    matrix_entries = [_matrix_entry_from_gap(gap) for gap in source_index.proof_gaps]
    boundary_rows = _boundary_rows(matrix_entries)
    status = APPROVAL_REQUIRED if matrix_entries else NO_APPROVAL_REQUIRED
    reason = (
        "Capability proof gaps remain blocked until proof evidence and explicit operator approval are present."
        if matrix_entries
        else "No capability approval boundaries are required by the latest proof gap index."
    )
    return storage.record_capability_approval_boundary_matrix(
        status=status,
        source_index_id=source_index.id,
        source_index_status=source_index.status,
        capability_count=source_index.capability_count,
        boundary_count=len(boundary_rows),
        gap_count=source_index.gap_count,
        blocked_capability_count=source_index.blocked_capability_count,
        approval_required_count=len(matrix_entries),
        recommended_commands=[],
        reason=reason,
        boundary_rows=boundary_rows,
        matrix_entries=matrix_entries,
        report_path=report_path,
    )


def _matrix_entry_from_gap(gap: dict[str, str]) -> dict[str, str]:
    return {
        "capability": gap["capability"],
        "approval_boundary": gap.get("approval_boundary") or APPROVAL_BOUNDARY,
        "decision_state": DECISION_BLOCKED,
        "gap": gap["gap"],
        "required_evidence": gap["required_evidence"],
        "next_proof": gap["next_proof"],
        "routing_effect": gap["routing_effect"],
    }


def _boundary_rows(entries: list[dict[str, str]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for entry in entries:
        grouped[entry["approval_boundary"]].append(entry)

    rows: list[dict[str, object]] = []
    for boundary, boundary_entries in sorted(grouped.items()):
        rows.append(
            {
                "approval_boundary": boundary,
                "capability_count": len(
                    {entry["capability"] for entry in boundary_entries}
                ),
                "gap_count": len(boundary_entries),
                "approval_required_count": len(boundary_entries),
                "capabilities": [entry["capability"] for entry in boundary_entries],
            }
        )
    return rows
