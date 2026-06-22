from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityExpansionLedger,
    CapabilityReadinessReview,
    Storage,
)


BLOCKED_BY_MISSING_EVIDENCE = "blocked_by_missing_evidence"
LEDGER_MISSING = "ledger_missing"
READY = "ready"
NOT_READY = "not_ready"
EVIDENCE_PRESENT = "present"
EVIDENCE_MISSING = "missing"
REPORT_PATH = "docs/capability-readiness-review.md"
APPROVAL_BOUNDARY = "explicit_operator_approval_required"


def write_capability_readiness_review(
    root: Path,
) -> tuple[Path, CapabilityReadinessReview]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    ledgers = storage.list_recent_capability_expansion_ledgers(limit=1)
    source_ledger = ledgers[0] if ledgers else None
    review = _review_latest_ledger(
        storage=storage,
        source_ledger=source_ledger,
        report_path=REPORT_PATH,
    )
    report_path = root / review.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_readiness_review_report(review, source_ledger),
        encoding="utf-8",
    )
    return report_path, review


def render_capability_readiness_review_report(
    review: CapabilityReadinessReview,
    source_ledger: CapabilityExpansionLedger | None,
) -> str:
    lines = [
        "# Capability Readiness Review",
        "",
        f"- id: {review.id}",
        f"- status: {review.status}",
        f"- source_ledger_id: {review.source_ledger_id or 'none'}",
        f"- source_ledger_status: {review.source_ledger_status}",
        f"- capability_count: {review.capability_count}",
        f"- ready: {review.ready_count}",
        f"- not_ready: {review.not_ready_count}",
        f"- missing_evidence: {review.missing_evidence_count}",
        f"- approval_boundary: {review.approval_boundary}",
        f"- recommended_commands: {format_recommended_commands(review.recommended_commands)}",
        f"- report_path: {review.report_path}",
        f"- created_at: {review.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {review.reason}",
        "",
        "## Reviewed Capabilities",
        "",
    ]
    if review.review_items:
        lines.extend(render_capability_readiness_item_line(item) for item in review.review_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Ledger", ""])
    if source_ledger is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_ledger.id}",
                f"- status: {source_ledger.status}",
                f"- capabilities: {source_ledger.capability_count}",
                f"- ready: {source_ledger.ready_count}",
                f"- deferred: {source_ledger.deferred_count}",
                f"- report: {source_ledger.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local readiness review.",
            "- Does not create capability ledgers as a side effect.",
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


def render_capability_readiness_review_line(
    review: CapabilityReadinessReview,
) -> str:
    return (
        f"- {review.id}: status={review.status} "
        f"source_ledger={review.source_ledger_id or 'none'} "
        f"capabilities={review.capability_count} ready={review.ready_count} "
        f"not_ready={review.not_ready_count} "
        f"missing_evidence={review.missing_evidence_count} "
        f"recommended_commands={format_recommended_commands(review.recommended_commands)} "
        f"report={review.report_path}"
    )


def render_capability_readiness_item_line(item: dict[str, str]) -> str:
    return (
        f"- {item['capability']}: readiness={item['readiness']} "
        f"evidence_state={item['evidence_state']} "
        f"next_proof={item['next_proof']} "
        f"routing_effect={item['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _review_latest_ledger(
    *,
    storage: Storage,
    source_ledger: CapabilityExpansionLedger | None,
    report_path: str,
) -> CapabilityReadinessReview:
    if source_ledger is None:
        return storage.record_capability_readiness_review(
            status=LEDGER_MISSING,
            source_ledger_id=None,
            source_ledger_status="none",
            capability_count=0,
            ready_count=0,
            not_ready_count=0,
            missing_evidence_count=0,
            approval_boundary=APPROVAL_BOUNDARY,
            recommended_commands=["capability-expansion-ledger"],
            reason="No capability expansion ledger exists yet.",
            review_items=[],
            report_path=report_path,
        )

    review_items = [_review_capability_entry(entry) for entry in source_ledger.capabilities]
    ready_count = sum(1 for item in review_items if item["readiness"] == READY)
    missing_evidence_count = sum(
        1 for item in review_items if item["evidence_state"] == EVIDENCE_MISSING
    )
    not_ready_count = len(review_items) - ready_count
    status = (
        READY
        if review_items and ready_count == len(review_items)
        else BLOCKED_BY_MISSING_EVIDENCE
    )
    reason = (
        "All ledger capabilities have readiness evidence."
        if status == READY
        else "Capability surfaces remain blocked until required evidence is attached and approved."
    )
    return storage.record_capability_readiness_review(
        status=status,
        source_ledger_id=source_ledger.id,
        source_ledger_status=source_ledger.status,
        capability_count=len(review_items),
        ready_count=ready_count,
        not_ready_count=not_ready_count,
        missing_evidence_count=missing_evidence_count,
        approval_boundary=source_ledger.approval_boundary,
        recommended_commands=[],
        reason=reason,
        review_items=review_items,
        report_path=report_path,
    )


def _review_capability_entry(entry: dict[str, str]) -> dict[str, str]:
    evidence_path = entry.get("evidence_path", "")
    evidence_state = EVIDENCE_PRESENT if evidence_path else EVIDENCE_MISSING
    readiness = READY if entry.get("state") == READY and evidence_path else NOT_READY
    return {
        "capability": entry["capability"],
        "readiness": readiness,
        "evidence_state": evidence_state,
        "required_evidence": entry["required_evidence"],
        "next_proof": entry["next_proof"],
        "approval_boundary": entry["approval_boundary"],
        "routing_effect": entry["routing_effect"],
    }
