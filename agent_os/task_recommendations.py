from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import Storage, Task, TaskRecommendation


REPORT_PATH = "docs/task-recommendations.md"
FAILED_RUN_TASK_RECOVERY = "failed_run_task_recovery"
BLOCKED_PLANNED_TASK_REPLAN = "blocked_planned_task_replan"


@dataclass(frozen=True)
class TaskRecommendationBatch:
    recommendations: list[TaskRecommendation]
    created_count: int
    existing_count: int
    report_path: str


def ensure_failed_run_task_recommendation(
    *,
    root: Path,
    storage: Storage,
    task: Task,
    run_id: str,
    profile_name: str,
    evidence_dir: Path,
) -> tuple[TaskRecommendation, bool]:
    step = storage.get_plan_step_by_task(task.id)
    reason = (
        "verification command failed"
        if task.evidence.get("returncode") is None
        else f"verification command failed with exit {task.evidence['returncode']}"
    )
    idempotency_key = f"task-recommendation:{FAILED_RUN_TASK_RECOVERY}:{task.id}:{run_id}"
    evidence_path = (
        evidence_dir
        / "recommendations"
        / f"{FAILED_RUN_TASK_RECOVERY}-{task.id}-{run_id}.json"
    )
    commands = [
        f"review {run_id}",
        f"replan {task.goal_id} --reason \"Review failed task {task.id} from run {run_id}\"",
        f"run-task {task.id} --profile {profile_name}",
    ]
    recommendation, created = storage.ensure_task_recommendation(
        idempotency_key=idempotency_key,
        task_id=task.id,
        run_id=run_id,
        goal_id=task.goal_id,
        project_id=task.project_id,
        plan_id=step.plan_id if step else None,
        recommendation_type=FAILED_RUN_TASK_RECOVERY,
        source_status="failed",
        status="open",
        reason=reason,
        recommended_commands=commands,
        evidence_path=_relative(root, evidence_path),
    )
    write_task_recommendation_evidence(root, recommendation)
    return recommendation, created


def write_task_recommendations(
    root: Path,
    *,
    goal_id: str | None = None,
) -> tuple[Path, TaskRecommendationBatch]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    tasks = storage.list_tasks(goal_id) if goal_id else storage.list_all_tasks()
    recommendations: list[TaskRecommendation] = []
    created_count = 0
    existing_count = 0
    for task in tasks:
        result = _recommend_for_task(root=root, storage=storage, task=task)
        if result is None:
            continue
        recommendation, created = result
        recommendations.append(recommendation)
        if created:
            created_count += 1
        else:
            existing_count += 1

    report_path = root / REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_task_recommendations_report(
            recommendations=recommendations,
            created_count=created_count,
            existing_count=existing_count,
            goal_id=goal_id,
            report_path=REPORT_PATH,
        ),
        encoding="utf-8",
    )
    return report_path, TaskRecommendationBatch(
        recommendations=recommendations,
        created_count=created_count,
        existing_count=existing_count,
        report_path=REPORT_PATH,
    )


def write_task_recommendation_evidence(
    root: Path,
    recommendation: TaskRecommendation,
) -> Path:
    evidence_path = root / recommendation.evidence_path
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(
        json.dumps(_recommendation_payload(recommendation), indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return evidence_path


def write_run_recommendations_packet(
    root: Path,
    evidence_dir: Path,
    recommendations: list[TaskRecommendation],
) -> list[str]:
    if not recommendations:
        return []
    packet_path = evidence_dir / "recommendations.jsonl"
    packet_path.write_text(
        "".join(
            json.dumps(_recommendation_payload(recommendation), sort_keys=True) + "\n"
            for recommendation in recommendations
        ),
        encoding="utf-8",
    )
    return [_relative(root, packet_path)]


def render_task_recommendations_report(
    *,
    recommendations: list[TaskRecommendation],
    created_count: int,
    existing_count: int,
    goal_id: str | None,
    report_path: str,
) -> str:
    lines = [
        "# Task Recommendations",
        "",
        f"- task_recommendations: {len(recommendations)}",
        f"- created: {created_count}",
        f"- existing: {existing_count}",
        f"- goal_id: {goal_id or 'all'}",
        f"- report_path: {report_path}",
        "",
        "## Recommendations",
        "",
    ]
    if recommendations:
        for recommendation in recommendations:
            lines.append(render_task_recommendation_line(recommendation))
            for command in recommendation.recommended_commands:
                lines.append(f"  - command: {command}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Local recommendation records only.",
            "- Does not retry, reset, replan, or dispatch tasks automatically.",
            "- Does not approve work, commit, push, deploy, call model providers, schedule work, or mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_task_recommendation_line(recommendation: TaskRecommendation) -> str:
    return (
        f"- {recommendation.id}: type={recommendation.recommendation_type} "
        f"status={recommendation.status} source_status={recommendation.source_status} "
        f"task={recommendation.task_id} run={recommendation.run_id or 'none'} "
        f"goal={recommendation.goal_id} commands={format_recommended_commands(recommendation.recommended_commands)} "
        f"evidence={recommendation.evidence_path}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return " | ".join(commands)


def _recommend_for_task(
    *,
    root: Path,
    storage: Storage,
    task: Task,
) -> tuple[TaskRecommendation, bool] | None:
    if task.status == "failed" and task.run_id:
        profile_name = str(task.evidence.get("profile") or task.owner or "coder")
        evidence_packet = task.evidence.get("evidence_packet")
        if isinstance(evidence_packet, str) and evidence_packet:
            evidence_dir = root / evidence_packet
        else:
            evidence_dir = (
                root
                / ".clanker"
                / "projects"
                / task.project_id
                / "goals"
                / task.goal_id
                / "runs"
                / task.run_id
                / "evidence"
            )
        recommendation, created = ensure_failed_run_task_recommendation(
            root=root,
            storage=storage,
            task=task,
            run_id=task.run_id,
            profile_name=profile_name,
            evidence_dir=evidence_dir,
        )
        write_run_recommendations_packet(root, evidence_dir, [recommendation])
        return recommendation, created

    if task.status != "blocked" or task.task_type != "planned_step":
        return None
    step = storage.get_plan_step_by_task(task.id)
    reason = step.blocked_reason if step and step.blocked_reason else "blocked task requires operator review"
    idempotency_key = f"task-recommendation:{BLOCKED_PLANNED_TASK_REPLAN}:{task.id}"
    evidence_path = (
        root
        / ".clanker"
        / "projects"
        / task.project_id
        / "goals"
        / task.goal_id
        / "recommendations"
        / f"{BLOCKED_PLANNED_TASK_REPLAN}-{task.id}.json"
    )
    commands = [
        f"tasks {task.goal_id}",
        f"replan {task.goal_id} --reason \"Unblock blocked task {task.id}: {reason}\"",
        f"update-task {task.id} --status planned",
    ]
    recommendation, created = storage.ensure_task_recommendation(
        idempotency_key=idempotency_key,
        task_id=task.id,
        run_id=None,
        goal_id=task.goal_id,
        project_id=task.project_id,
        plan_id=step.plan_id if step else None,
        recommendation_type=BLOCKED_PLANNED_TASK_REPLAN,
        source_status="blocked",
        status="open",
        reason=reason,
        recommended_commands=commands,
        evidence_path=_relative(root, evidence_path),
    )
    write_task_recommendation_evidence(root, recommendation)
    return recommendation, created


def _recommendation_payload(recommendation: TaskRecommendation) -> dict[str, object]:
    return {
        "id": recommendation.id,
        "idempotency_key": recommendation.idempotency_key,
        "task_id": recommendation.task_id,
        "run_id": recommendation.run_id,
        "goal_id": recommendation.goal_id,
        "project_id": recommendation.project_id,
        "plan_id": recommendation.plan_id,
        "recommendation_type": recommendation.recommendation_type,
        "source_status": recommendation.source_status,
        "status": recommendation.status,
        "reason": recommendation.reason,
        "recommended_commands": recommendation.recommended_commands,
        "evidence_path": recommendation.evidence_path,
        "created_at": recommendation.created_at,
        "updated_at": recommendation.updated_at,
    }


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())
