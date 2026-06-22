from __future__ import annotations

from pathlib import Path

from agent_os.budget_trust import format_risk_counts
from agent_os.storage import (
    BudgetTrustPostureReport,
    DispatchPostureHistorySummary,
    Storage,
)


REPORT_STATUS = "report_only"
DEFAULT_HISTORY_LIMIT = 25


def write_dispatch_posture_history_report(
    root: Path,
    *,
    limit: int = DEFAULT_HISTORY_LIMIT,
) -> tuple[Path, DispatchPostureHistorySummary]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    snapshots = storage.list_recent_budget_trust_posture_reports(limit=limit)
    summary = _summarize_snapshots(
        storage=storage,
        snapshots=snapshots,
        report_path="docs/dispatch-posture-history.md",
    )
    report_path = root / summary.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_dispatch_posture_history_report(summary, snapshots),
        encoding="utf-8",
    )
    return report_path, summary


def render_dispatch_posture_history_report(
    summary: DispatchPostureHistorySummary,
    snapshots: list[BudgetTrustPostureReport],
) -> str:
    lines = [
        "# Dispatch Posture History",
        "",
        f"- id: {summary.id}",
        f"- status: {summary.status}",
        f"- snapshots: {summary.snapshot_count}",
        f"- latest_task_count: {summary.latest_task_count}",
        f"- task_count_delta: {summary.task_count_delta}",
        f"- budget_states: {','.join(summary.budget_states) or 'none'}",
        f"- trust_states: {','.join(summary.trust_states) or 'none'}",
        f"- first_snapshot_at: {summary.first_snapshot_at or 'none'}",
        f"- latest_snapshot_at: {summary.latest_snapshot_at or 'none'}",
        f"- report_path: {summary.report_path}",
        f"- created_at: {summary.created_at}",
        "",
        "## Latest Risk Levels",
        "",
    ]
    if summary.latest_risk_counts:
        lines.extend(
            f"- {risk}: {count}"
            for risk, count in summary.latest_risk_counts.items()
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Recent Snapshots", ""])
    if snapshots:
        lines.extend(render_dispatch_posture_snapshot_line(snapshot) for snapshot in snapshots)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local metadata history.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not change task routing, approval decisions, worker claiming, retries, replay, CI, deploy, scheduler, or external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_dispatch_posture_history_line(
    summary: DispatchPostureHistorySummary,
) -> str:
    return (
        f"- {summary.id}: status={summary.status} "
        f"snapshots={summary.snapshot_count} latest_tasks={summary.latest_task_count} "
        f"task_delta={summary.task_count_delta} "
        f"latest_risk_counts={format_risk_counts(summary.latest_risk_counts)} "
        f"report={summary.report_path}"
    )


def render_dispatch_posture_snapshot_line(
    snapshot: BudgetTrustPostureReport,
) -> str:
    return (
        f"- {snapshot.id}: tasks={snapshot.task_count} "
        f"risk_counts={format_risk_counts(snapshot.risk_counts)} "
        f"budget_state={snapshot.budget_state} trust_state={snapshot.trust_state} "
        f"created_at={snapshot.created_at}"
    )


def _summarize_snapshots(
    *,
    storage: Storage,
    snapshots: list[BudgetTrustPostureReport],
    report_path: str,
) -> DispatchPostureHistorySummary:
    latest = snapshots[0] if snapshots else None
    oldest = snapshots[-1] if snapshots else None
    latest_task_count = latest.task_count if latest else 0
    oldest_task_count = oldest.task_count if oldest else latest_task_count
    return storage.record_dispatch_posture_history_summary(
        status=REPORT_STATUS,
        snapshot_count=len(snapshots),
        latest_task_count=latest_task_count,
        task_count_delta=latest_task_count - oldest_task_count,
        latest_risk_counts=latest.risk_counts if latest else {},
        budget_states=_unique_states(snapshot.budget_state for snapshot in snapshots),
        trust_states=_unique_states(snapshot.trust_state for snapshot in snapshots),
        first_snapshot_at=oldest.created_at if oldest else None,
        latest_snapshot_at=latest.created_at if latest else None,
        report_path=report_path,
    )


def _unique_states(values) -> list[str]:
    return sorted({value for value in values if value})
