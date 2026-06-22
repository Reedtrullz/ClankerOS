from __future__ import annotations

from pathlib import Path

from agent_os.storage import HandoffReview, Storage, Task


def write_handoff_review_report(root: Path) -> tuple[Path, HandoffReview]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    current_focus = _current_focus(storage)
    blocked_tasks = [
        _blocked_task_payload(task)
        for task in storage.list_blocked_tasks()
    ]
    handoff_paths = _discover_handoff_paths(root)
    stale_handoffs = _stale_handoff_payloads(root, handoff_paths, current_focus)
    reviewed_paths = [_relative_to_root(root, path) for path in handoff_paths]
    status = "needs_attention" if blocked_tasks or stale_handoffs else "clear"

    report_path = root / "docs" / "handoff-review.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review = storage.record_handoff_review(
        status=status,
        current_focus=current_focus,
        blocked_tasks=blocked_tasks,
        stale_handoffs=stale_handoffs,
        reviewed_paths=reviewed_paths,
        report_path=_relative_to_root(root, report_path),
    )
    report_path.write_text(render_handoff_review_report(review), encoding="utf-8")
    return report_path, review


def render_handoff_review_report(review: HandoffReview) -> str:
    lines = [
        "# Handoff Review",
        "",
        f"- id: {review.id}",
        f"- status: {review.status}",
        f"- current_focus: {review.current_focus}",
        f"- blocked_tasks: {review.blocked_task_count}",
        f"- stale_handoffs: {review.stale_handoff_count}",
        f"- reviewed_paths: {len(review.reviewed_paths)}",
        "",
        "## Blocked Tasks",
        "",
    ]
    if review.blocked_tasks:
        lines.extend(render_blocked_task_line(task) for task in review.blocked_tasks)
    else:
        lines.append("- none")

    lines.extend(["", "## Stale Handoffs", ""])
    if review.stale_handoffs:
        lines.extend(render_stale_handoff_line(handoff) for handoff in review.stale_handoffs)
    else:
        lines.append("- none")

    lines.append("")
    return "\n".join(lines)


def render_blocked_task_line(task: dict[str, object]) -> str:
    return (
        f"- blocked task={task['id']} project={task['project_id']} "
        f"type={task['task_type']} run={task['run_id']} "
        f"updated_at={task['updated_at']} description={task['description']}"
    )


def render_stale_handoff_line(handoff: dict[str, object]) -> str:
    return (
        f"- stale path={handoff['path']} reason={handoff['reason']} "
        f"current_focus={handoff['current_focus']}"
    )


def _current_focus(storage: Storage) -> str:
    packets = storage.list_recent_iteration_packets(limit=1)
    if not packets:
        return "unknown"
    return packets[0].focus


def _blocked_task_payload(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "project_id": task.project_id,
        "run_id": task.run_id or "none",
        "goal_id": task.goal_id,
        "task_type": task.task_type,
        "updated_at": task.updated_at,
        "description": task.description,
    }


def _discover_handoff_paths(root: Path) -> list[Path]:
    paths: list[Path] = []
    root_handoff = root / "handoff.md"
    if root_handoff.exists():
        paths.append(root_handoff)
    projects_root = root / "projects"
    if projects_root.exists():
        paths.extend(sorted(projects_root.glob("*/handoff.md")))
    return sorted(paths)


def _stale_handoff_payloads(
    root: Path,
    handoff_paths: list[Path],
    current_focus: str,
) -> list[dict[str, object]]:
    if current_focus == "unknown":
        return []

    stale: list[dict[str, object]] = []
    for path in handoff_paths:
        text = path.read_text(encoding="utf-8")
        if current_focus in text:
            continue
        stale.append(
            {
                "path": _relative_to_root(root, path),
                "reason": "does_not_reference_current_focus",
                "current_focus": current_focus,
            }
        )
    return stale


def _relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
