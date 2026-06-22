from __future__ import annotations

from pathlib import Path

from agent_os.dispatch_posture_staleness import format_optional_age_seconds
from agent_os.storage import (
    DispatchPostureRefreshRecommendation,
    DispatchPostureStalenessReview,
    Storage,
)


NO_REFRESH_NEEDED = "no_refresh_needed"
MANUAL_REFRESH_RECOMMENDED = "manual_refresh_recommended"
SNAPSHOT_SEED_RECOMMENDED = "snapshot_seed_recommended"
STALENESS_REVIEW_MISSING = "staleness_review_missing"
REPORT_PATH = "docs/dispatch-posture-refresh.md"
FULL_REFRESH_COMMANDS = [
    "budget-trust-posture",
    "dispatch-posture-history",
    "dispatch-posture-staleness",
    "dispatch-posture-refresh",
]
DEFERRED_CAPABILITIES = [
    "autonomous_scheduling",
    "hosted_dashboard",
    "remote_workers",
    "browser_desktop_adapters",
    "ci_deploy_proof",
    "budget_enforcement",
    "trust_promotion",
    "automatic_retries",
    "real_cost_tracking",
]
APPROVAL_BOUNDARY = "operator_runs_recommended_commands_manually"


def write_dispatch_posture_refresh_report(
    root: Path,
) -> tuple[Path, DispatchPostureRefreshRecommendation]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    reviews = storage.list_recent_dispatch_posture_staleness_reviews(limit=1)
    source_review = reviews[0] if reviews else None
    recommendation = _recommend_from_staleness_review(
        storage=storage,
        source_review=source_review,
        report_path=REPORT_PATH,
    )
    report_path = root / recommendation.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_dispatch_posture_refresh_report(recommendation, source_review),
        encoding="utf-8",
    )
    return report_path, recommendation


def render_dispatch_posture_refresh_report(
    recommendation: DispatchPostureRefreshRecommendation,
    source_review: DispatchPostureStalenessReview | None,
) -> str:
    lines = [
        "# Dispatch Posture Refresh Recommendation",
        "",
        f"- id: {recommendation.id}",
        f"- status: {recommendation.status}",
        f"- source_review_id: {recommendation.source_review_id or 'none'}",
        f"- source_review_status: {recommendation.source_review_status}",
        f"- snapshots: {recommendation.snapshot_count}",
        f"- stale_snapshots: {recommendation.stale_snapshot_count}",
        f"- latest_snapshot_age_seconds: {format_optional_age_seconds(recommendation.latest_snapshot_age_seconds)}",
        f"- stale_after_seconds: {recommendation.stale_after_seconds}",
        f"- latest_snapshot_at: {recommendation.latest_snapshot_at or 'none'}",
        f"- approval_boundary: {recommendation.approval_boundary}",
        f"- report_path: {recommendation.report_path}",
        f"- created_at: {recommendation.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {recommendation.reason}",
        f"- recommended_commands: {format_recommended_commands(recommendation.recommended_commands)}",
        "",
        "## Recommended Commands",
        "",
    ]
    if recommendation.recommended_commands:
        lines.extend(f"- {command}" for command in recommendation.recommended_commands)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Review", ""])
    if source_review is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_review.id}",
                f"- status: {source_review.status}",
                f"- snapshots: {source_review.snapshot_count}",
                f"- stale_snapshots: {source_review.stale_snapshot_count}",
                f"- latest_snapshot_age_seconds: {format_optional_age_seconds(source_review.latest_snapshot_age_seconds)}",
                f"- stale_after_seconds: {source_review.stale_after_seconds}",
                f"- report: {source_review.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Deferred Capability Context",
            "",
        ]
    )
    lines.extend(f"- {capability}" for capability in recommendation.deferred_capabilities)
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local recommendation.",
            "- Does not run refresh commands automatically.",
            "- Does not create staleness reviews as a side effect.",
            "- Does not schedule refreshes.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not change task routing, approval decisions, worker claiming, retries, replay, CI, deploy, hosted dashboard, remote workers, browser or desktop adapters, cost tracking, or external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_dispatch_posture_refresh_line(
    recommendation: DispatchPostureRefreshRecommendation,
) -> str:
    return (
        f"- {recommendation.id}: status={recommendation.status} "
        f"source_review={recommendation.source_review_id or 'none'} "
        f"source_status={recommendation.source_review_status} "
        f"recommended_commands={format_recommended_commands(recommendation.recommended_commands)} "
        f"report={recommendation.report_path}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _recommend_from_staleness_review(
    *,
    storage: Storage,
    source_review: DispatchPostureStalenessReview | None,
    report_path: str,
) -> DispatchPostureRefreshRecommendation:
    if source_review is None:
        return storage.record_dispatch_posture_refresh_recommendation(
            status=STALENESS_REVIEW_MISSING,
            source_review_id=None,
            source_review_status="none",
            snapshot_count=0,
            stale_snapshot_count=0,
            latest_snapshot_age_seconds=None,
            stale_after_seconds=0,
            latest_snapshot_at=None,
            recommended_commands=["dispatch-posture-staleness"],
            reason="No dispatch posture staleness review exists yet.",
            approval_boundary=APPROVAL_BOUNDARY,
            deferred_capabilities=DEFERRED_CAPABILITIES,
            report_path=report_path,
        )

    status = NO_REFRESH_NEEDED
    commands: list[str] = []
    reason = "No refresh is currently recommended because the latest staleness review is fresh."
    if source_review.status == "stale":
        status = MANUAL_REFRESH_RECOMMENDED
        commands = FULL_REFRESH_COMMANDS
        reason = "Manual refresh is recommended because latest dispatch posture snapshot is stale."
    elif source_review.status == "missing_history":
        status = SNAPSHOT_SEED_RECOMMENDED
        commands = FULL_REFRESH_COMMANDS
        reason = "Manual snapshot seed is recommended because dispatch posture history is missing."

    return storage.record_dispatch_posture_refresh_recommendation(
        status=status,
        source_review_id=source_review.id,
        source_review_status=source_review.status,
        snapshot_count=source_review.snapshot_count,
        stale_snapshot_count=source_review.stale_snapshot_count,
        latest_snapshot_age_seconds=source_review.latest_snapshot_age_seconds,
        stale_after_seconds=source_review.stale_after_seconds,
        latest_snapshot_at=source_review.latest_snapshot_at,
        recommended_commands=commands,
        reason=reason,
        approval_boundary=APPROVAL_BOUNDARY,
        deferred_capabilities=DEFERRED_CAPABILITIES,
        report_path=report_path,
    )
