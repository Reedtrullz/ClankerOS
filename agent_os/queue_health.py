from __future__ import annotations

from pathlib import Path

from agent_os.storage import QueueHealthFinding, Storage


DEFAULT_BLOCKED_THRESHOLD = 2
DEFAULT_FAILED_THRESHOLD = 2


def write_queue_health_report(
    root: Path,
    *,
    blocked_threshold: int = DEFAULT_BLOCKED_THRESHOLD,
    failed_threshold: int = DEFAULT_FAILED_THRESHOLD,
) -> tuple[Path, list[QueueHealthFinding]]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    findings = storage.list_queue_health_findings(
        blocked_threshold=blocked_threshold,
        failed_threshold=failed_threshold,
    )
    report_path = root / "docs" / "queue-health.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_queue_health_report(
            findings,
            blocked_threshold=blocked_threshold,
            failed_threshold=failed_threshold,
        ),
        encoding="utf-8",
    )
    return report_path, findings


def render_queue_health_report(
    findings: list[QueueHealthFinding],
    *,
    blocked_threshold: int = DEFAULT_BLOCKED_THRESHOLD,
    failed_threshold: int = DEFAULT_FAILED_THRESHOLD,
) -> str:
    lines = [
        "# Queue Health Report",
        "",
        f"- blocked_threshold: {blocked_threshold}",
        f"- failed_threshold: {failed_threshold}",
        f"- hotspots: {len(findings)}",
        "",
        "## Hotspots",
        "",
    ]
    if findings:
        lines.extend(render_queue_health_finding(finding) for finding in findings)
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def render_queue_health_finding(finding: QueueHealthFinding) -> str:
    task_ids = ",".join(finding.task_ids)
    return (
        f"- {finding.status} project={finding.project_id} "
        f"type={finding.task_type} count={finding.count} "
        f"threshold={finding.threshold} tasks={task_ids}"
    )
