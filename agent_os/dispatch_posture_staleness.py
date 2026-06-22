from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from agent_os.budget_trust import format_risk_counts
from agent_os.storage import (
    BudgetTrustPostureReport,
    DispatchPostureStalenessReview,
    Storage,
    utc_now,
)


FRESH_STATUS = "fresh"
STALE_STATUS = "stale"
MISSING_STATUS = "missing_history"
DEFAULT_STALE_AFTER_MINUTES = 60
DEFAULT_REVIEW_LIMIT = 25


def write_dispatch_posture_staleness_report(
    root: Path,
    *,
    now: str | None = None,
    stale_after_minutes: int = DEFAULT_STALE_AFTER_MINUTES,
    limit: int = DEFAULT_REVIEW_LIMIT,
) -> tuple[Path, DispatchPostureStalenessReview]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    now_value = _parse_utc(now or utc_now())
    stale_after_seconds = stale_after_minutes * 60
    snapshots = storage.list_recent_budget_trust_posture_reports(limit=limit)
    review = _review_snapshots(
        storage=storage,
        snapshots=snapshots,
        now_value=now_value,
        stale_after_seconds=stale_after_seconds,
        report_path="docs/dispatch-posture-staleness.md",
    )
    report_path = root / review.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_dispatch_posture_staleness_report(
            review,
            snapshots,
            now_value=now_value,
        ),
        encoding="utf-8",
    )
    return report_path, review


def render_dispatch_posture_staleness_report(
    review: DispatchPostureStalenessReview,
    snapshots: list[BudgetTrustPostureReport],
    *,
    now_value: datetime | None = None,
) -> str:
    reviewed_at = now_value or _parse_utc(review.created_at)
    lines = [
        "# Dispatch Posture Snapshot Review",
        "",
        f"- id: {review.id}",
        f"- status: {review.status}",
        f"- snapshots: {review.snapshot_count}",
        f"- stale_snapshots: {review.stale_snapshot_count}",
        f"- latest_snapshot_age_seconds: {format_optional_age_seconds(review.latest_snapshot_age_seconds)}",
        f"- stale_after_seconds: {review.stale_after_seconds}",
        f"- latest_task_count: {review.latest_task_count}",
        f"- latest_snapshot_at: {review.latest_snapshot_at or 'none'}",
        f"- oldest_snapshot_at: {review.oldest_snapshot_at or 'none'}",
        f"- report_path: {review.report_path}",
        f"- created_at: {review.created_at}",
        "",
        "## Latest Risk Levels",
        "",
    ]
    if review.latest_risk_counts:
        lines.extend(
            f"- {risk}: {count}"
            for risk, count in review.latest_risk_counts.items()
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Reviewed Snapshots", ""])
    if snapshots:
        lines.extend(
            _render_reviewed_snapshot_line(
                snapshot=snapshot,
                stale_after_seconds=review.stale_after_seconds,
                now_value=reviewed_at,
            )
            for snapshot in snapshots
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local timestamp review.",
            "- Does not schedule snapshot refreshes.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not change task routing, approval decisions, worker claiming, retries, replay, CI, deploy, scheduler, or external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_dispatch_posture_staleness_line(
    review: DispatchPostureStalenessReview,
) -> str:
    return (
        f"- {review.id}: status={review.status} snapshots={review.snapshot_count} "
        f"stale_snapshots={review.stale_snapshot_count} "
        f"latest_snapshot_age_seconds={format_optional_age_seconds(review.latest_snapshot_age_seconds)} "
        f"stale_after_seconds={review.stale_after_seconds} "
        f"latest_tasks={review.latest_task_count} "
        f"latest_risk_counts={format_risk_counts(review.latest_risk_counts)} "
        f"report={review.report_path}"
    )


def _review_snapshots(
    *,
    storage: Storage,
    snapshots: list[BudgetTrustPostureReport],
    now_value: datetime,
    stale_after_seconds: int,
    report_path: str,
) -> DispatchPostureStalenessReview:
    latest = snapshots[0] if snapshots else None
    oldest = snapshots[-1] if snapshots else None
    latest_age = (
        _age_seconds(now_value, latest.created_at)
        if latest is not None
        else None
    )
    stale_count = sum(
        1
        for snapshot in snapshots
        if _age_seconds(now_value, snapshot.created_at) > stale_after_seconds
    )
    status = _review_status(
        latest=latest,
        latest_age_seconds=latest_age,
        stale_after_seconds=stale_after_seconds,
    )
    return storage.record_dispatch_posture_staleness_review(
        status=status,
        snapshot_count=len(snapshots),
        stale_snapshot_count=stale_count,
        latest_snapshot_age_seconds=latest_age,
        stale_after_seconds=stale_after_seconds,
        latest_task_count=latest.task_count if latest else 0,
        latest_risk_counts=latest.risk_counts if latest else {},
        latest_snapshot_at=latest.created_at if latest else None,
        oldest_snapshot_at=oldest.created_at if oldest else None,
        report_path=report_path,
    )


def _review_status(
    *,
    latest: BudgetTrustPostureReport | None,
    latest_age_seconds: int | None,
    stale_after_seconds: int,
) -> str:
    if latest is None:
        return MISSING_STATUS
    if latest_age_seconds is None:
        return MISSING_STATUS
    if latest_age_seconds > stale_after_seconds:
        return STALE_STATUS
    return FRESH_STATUS


def _render_reviewed_snapshot_line(
    *,
    snapshot: BudgetTrustPostureReport,
    stale_after_seconds: int,
    now_value: datetime,
) -> str:
    age_seconds = _age_seconds(now_value, snapshot.created_at)
    status = "stale" if age_seconds > stale_after_seconds else "fresh"
    return (
        f"- {snapshot.id}: status={status} age_seconds={age_seconds} "
        f"tasks={snapshot.task_count} "
        f"risk_counts={format_risk_counts(snapshot.risk_counts)} "
        f"created_at={snapshot.created_at}"
    )


def _age_seconds(now_value: datetime, created_at: str) -> int:
    age = now_value - _parse_utc(created_at)
    return max(0, int(age.total_seconds()))


def format_optional_age_seconds(value: int | None) -> str:
    if value is None:
        return "none"
    return str(value)


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
