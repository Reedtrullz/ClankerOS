from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityProofGapIndex,
    CapabilityReadinessReview,
    Storage,
)


OPEN_GAPS = "open_gaps"
NO_OPEN_GAPS = "no_open_gaps"
READINESS_REVIEW_MISSING = "readiness_review_missing"
MISSING_EVIDENCE = "missing_evidence"
READINESS_BLOCKED = "readiness_blocked"
REPORT_PATH = "docs/capability-proof-gap-index.md"
APPROVAL_BOUNDARY = "explicit_operator_approval_required"


def write_capability_proof_gap_index(
    root: Path,
) -> tuple[Path, CapabilityProofGapIndex]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    reviews = storage.list_recent_capability_readiness_reviews(limit=1)
    source_review = reviews[0] if reviews else None
    index = _index_latest_review(
        storage=storage,
        source_review=source_review,
        report_path=REPORT_PATH,
    )
    report_path = root / index.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_proof_gap_index_report(index, source_review),
        encoding="utf-8",
    )
    return report_path, index


def render_capability_proof_gap_index_report(
    index: CapabilityProofGapIndex,
    source_review: CapabilityReadinessReview | None,
) -> str:
    lines = [
        "# Capability Proof Gap Index",
        "",
        f"- id: {index.id}",
        f"- status: {index.status}",
        f"- source_review_id: {index.source_review_id or 'none'}",
        f"- source_review_status: {index.source_review_status}",
        f"- capability_count: {index.capability_count}",
        f"- gaps: {index.gap_count}",
        f"- missing_evidence: {index.missing_evidence_count}",
        f"- blocked_capabilities: {index.blocked_capability_count}",
        f"- next_proofs: {index.next_proof_count}",
        f"- approval_boundary: {index.approval_boundary}",
        f"- recommended_commands: {format_recommended_commands(index.recommended_commands)}",
        f"- report_path: {index.report_path}",
        f"- created_at: {index.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {index.reason}",
        "",
        "## Proof Gaps",
        "",
    ]
    if index.proof_gaps:
        lines.extend(render_capability_proof_gap_line(gap) for gap in index.proof_gaps)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Readiness Review", ""])
    if source_review is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_review.id}",
                f"- status: {source_review.status}",
                f"- capabilities: {source_review.capability_count}",
                f"- ready: {source_review.ready_count}",
                f"- not_ready: {source_review.not_ready_count}",
                f"- missing_evidence: {source_review.missing_evidence_count}",
                f"- report: {source_review.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local proof-gap index.",
            "- Does not create readiness reviews as a side effect.",
            "- Does not create capability ledgers as a side effect.",
            "- Does not generate proof artifacts automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not retry or replay work.",
            "- Does not track real spend or mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_capability_proof_gap_index_line(
    index: CapabilityProofGapIndex,
) -> str:
    return (
        f"- {index.id}: status={index.status} "
        f"source_review={index.source_review_id or 'none'} "
        f"source_status={index.source_review_status} "
        f"gaps={index.gap_count} "
        f"missing_evidence={index.missing_evidence_count} "
        f"blocked_capabilities={index.blocked_capability_count} "
        f"next_proofs={index.next_proof_count} "
        f"recommended_commands={format_recommended_commands(index.recommended_commands)} "
        f"report={index.report_path}"
    )


def render_capability_proof_gap_line(gap: dict[str, str]) -> str:
    return (
        f"- {gap['capability']}: gap={gap['gap']} "
        f"readiness={gap['readiness']} "
        f"evidence_state={gap['evidence_state']} "
        f"next_proof={gap['next_proof']} "
        f"routing_effect={gap['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _index_latest_review(
    *,
    storage: Storage,
    source_review: CapabilityReadinessReview | None,
    report_path: str,
) -> CapabilityProofGapIndex:
    if source_review is None:
        return storage.record_capability_proof_gap_index(
            status=READINESS_REVIEW_MISSING,
            source_review_id=None,
            source_review_status="none",
            capability_count=0,
            gap_count=0,
            missing_evidence_count=0,
            blocked_capability_count=0,
            next_proof_count=0,
            approval_boundary=APPROVAL_BOUNDARY,
            recommended_commands=["capability-readiness-review"],
            reason="No capability readiness review exists yet.",
            proof_gaps=[],
            report_path=report_path,
        )

    proof_gaps = [
        _proof_gap_from_review_item(item)
        for item in source_review.review_items
        if _has_proof_gap(item)
    ]
    missing_evidence_count = sum(
        1 for gap in proof_gaps if gap["gap"] == MISSING_EVIDENCE
    )
    blocked_capability_count = len({gap["capability"] for gap in proof_gaps})
    next_proof_count = len({gap["next_proof"] for gap in proof_gaps})
    status = OPEN_GAPS if proof_gaps else NO_OPEN_GAPS
    reason = (
        "Capability proof gaps remain open until evidence paths are attached and approved."
        if proof_gaps
        else "No capability proof gaps were found in the latest readiness review."
    )
    return storage.record_capability_proof_gap_index(
        status=status,
        source_review_id=source_review.id,
        source_review_status=source_review.status,
        capability_count=source_review.capability_count,
        gap_count=len(proof_gaps),
        missing_evidence_count=missing_evidence_count,
        blocked_capability_count=blocked_capability_count,
        next_proof_count=next_proof_count,
        approval_boundary=source_review.approval_boundary,
        recommended_commands=[],
        reason=reason,
        proof_gaps=proof_gaps,
        report_path=report_path,
    )


def _has_proof_gap(item: dict[str, str]) -> bool:
    return item.get("readiness") != "ready" or item.get("evidence_state") != "present"


def _proof_gap_from_review_item(item: dict[str, str]) -> dict[str, str]:
    gap_type = (
        MISSING_EVIDENCE
        if item.get("evidence_state") == "missing"
        else READINESS_BLOCKED
    )
    return {
        "capability": item["capability"],
        "gap": gap_type,
        "readiness": item["readiness"],
        "evidence_state": item["evidence_state"],
        "required_evidence": item["required_evidence"],
        "next_proof": item["next_proof"],
        "approval_boundary": item["approval_boundary"],
        "routing_effect": item["routing_effect"],
    }
