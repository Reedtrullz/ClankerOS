from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import (
    GoalRecord,
    PlanRecord,
    PlanStepRecord,
    RegisteredProject,
    SprintContractRecord,
    Storage,
    Task,
)


class PlanningError(ValueError):
    pass


@dataclass(frozen=True)
class GoalLifecycle:
    goal: GoalRecord
    plan: PlanRecord
    steps: list[PlanStepRecord]
    tasks: list[Task]
    goal_artifact_path: Path
    plan_artifact_path: Path
    tasks_artifact_path: Path


def create_goal_lifecycle(
    root: Path,
    storage: Storage,
    *,
    project_id: str,
    prompt: str,
    created_by_profile: str = "planner",
) -> GoalLifecycle:
    root = root.resolve()
    project = _require_project(storage, project_id)
    if not prompt.strip():
        raise PlanningError("goal prompt is required")
    goal_id = storage.create_goal(
        project.name,
        prompt.strip(),
        title=prompt.strip(),
        original_prompt=prompt.strip(),
    )
    goal = storage.get_goal(goal_id)
    goal_artifact_path = _write_goal_artifact(root, project, goal)
    plan, steps = create_plan_version(
        root,
        storage,
        goal,
        project,
        created_by_profile=created_by_profile,
    )
    tasks = storage.list_tasks(goal.id)
    tasks_artifact_path = write_tasks_artifact(root, goal, tasks)
    return GoalLifecycle(
        goal=goal,
        plan=plan,
        steps=steps,
        tasks=tasks,
        goal_artifact_path=goal_artifact_path,
        plan_artifact_path=root / plan.artifact_path,
        tasks_artifact_path=tasks_artifact_path,
    )


def ensure_latest_plan(
    root: Path,
    storage: Storage,
    goal_id: str,
) -> tuple[GoalRecord, PlanRecord, list[PlanStepRecord]]:
    goal = storage.get_goal(goal_id)
    project = _require_project(storage, goal.project_id)
    try:
        plan = storage.get_latest_plan(goal_id)
    except KeyError:
        plan, steps = create_plan_version(root, storage, goal, project)
        return goal, plan, steps
    steps = storage.list_plan_steps(plan.id)
    _write_plan_artifacts(root.resolve(), project, goal, plan, steps)
    return goal, plan, steps


def create_plan_version(
    root: Path,
    storage: Storage,
    goal: GoalRecord,
    project: RegisteredProject,
    *,
    reason: str | None = None,
    created_by_profile: str = "planner",
) -> tuple[PlanRecord, list[PlanStepRecord]]:
    root = root.resolve()
    existing_plans = storage.list_plans(goal.id)
    version = len(existing_plans) + 1
    if existing_plans:
        storage.set_plan_status(existing_plans[-1].id, "superseded")

    artifact_path = _relative_goal_path(project.name, goal.id) / f"PLAN-v{version}.md"
    summary = _plan_summary(goal, reason)
    plan = storage.create_plan(
        goal_id=goal.id,
        version=version,
        summary=summary,
        status="active",
        created_by_profile=created_by_profile,
        artifact_path=str(artifact_path),
    )
    steps = _create_default_plan_steps(
        storage,
        goal=goal,
        project=project,
        plan=plan,
        reason=reason,
    )
    _write_plan_artifacts(root, project, goal, plan, steps)
    write_tasks_artifact(root, goal, storage.list_tasks(goal.id))
    return plan, steps


def create_contract_for_goal(
    root: Path,
    storage: Storage,
    goal_id: str,
) -> tuple[GoalRecord, PlanRecord, SprintContractRecord]:
    goal, plan, steps = ensure_latest_plan(root, storage, goal_id)
    project = _require_project(storage, goal.project_id)
    existing = storage.get_latest_sprint_contract(goal.id)
    if existing is not None and existing.plan_id == plan.id:
        _write_contract_artifact(root.resolve(), project, goal, plan, steps, existing)
        return goal, plan, existing

    artifact_path = _relative_goal_path(project.name, goal.id) / "CONTRACT.md"
    contract = storage.create_sprint_contract(
        goal_id=goal.id,
        plan_id=plan.id,
        scope=f"Execute plan v{plan.version} for goal: {goal.title}",
        non_goals=(
            "No external side effects, no CI/deploy claim, no autonomous "
            "scheduling, and no model-provider dispatch from this contract."
        ),
        acceptance_criteria="\n".join(
            f"- {step.acceptance_criteria}" for step in steps
        ),
        verification_plan="\n".join(
            f"- {step.verification_command}" for step in steps
        ),
        risk_notes=(
            "Planned tasks remain status=planned until an operator or later "
            "runner explicitly moves them into an executable state."
        ),
        evaluator_notes="Review plan alignment, task evidence, and non-claims before execution.",
        status="draft",
        artifact_path=str(artifact_path),
    )
    _write_contract_artifact(root.resolve(), project, goal, plan, steps, contract)
    return goal, plan, contract


def update_lifecycle_task(
    root: Path,
    storage: Storage,
    task_id: str,
    *,
    status: str,
    blocked_reason: str | None = None,
) -> tuple[Task, PlanStepRecord | None]:
    if not status.strip():
        raise PlanningError("task status is required")
    storage.set_task_status(task_id, status.strip())
    step = storage.update_plan_step_for_task(
        task_id,
        status=status.strip(),
        blocked_reason=blocked_reason,
    )
    task = storage.get_task(task_id)
    write_tasks_artifact(
        root.resolve(),
        storage.get_goal(task.goal_id),
        storage.list_tasks(task.goal_id),
    )
    return task, step


def replan_goal(
    root: Path,
    storage: Storage,
    goal_id: str,
    *,
    reason: str,
) -> tuple[GoalRecord, PlanRecord, list[PlanStepRecord], int]:
    if not reason.strip():
        raise PlanningError("replan reason is required")
    goal = storage.get_goal(goal_id)
    project = _require_project(storage, goal.project_id)
    previous_count = len(storage.list_plans(goal.id))
    plan, steps = create_plan_version(
        root,
        storage,
        goal,
        project,
        reason=reason.strip(),
        created_by_profile="planner",
    )
    return goal, plan, steps, previous_count


def render_plan_step_line(step: PlanStepRecord) -> str:
    return (
        f"step {step.order_index}: {step.title} status={step.status} "
        f"profile={step.assigned_profile} task={step.task_id or 'none'} "
        f"verify=\"{step.verification_command}\""
    )


def render_task_line(task: Task) -> str:
    return (
        f"{task.id}: status={task.status} type={task.task_type} "
        f"priority={task.priority} description={task.description}"
    )


def write_tasks_artifact(root: Path, goal: GoalRecord, tasks: list[Task]) -> Path:
    artifact_path = root / _relative_goal_path(goal.project_id, goal.id) / "TASKS.md"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Tasks For {goal.id}",
        "",
        f"- project_id: {goal.project_id}",
        f"- goal: {goal.title}",
        "",
        "## Tasks",
        "",
    ]
    if not tasks:
        lines.append("- none")
    for task in tasks:
        lines.extend(
            [
                f"### {task.id}",
                "",
                f"- status: {task.status}",
                f"- type: {task.task_type}",
                f"- priority: {task.priority}",
                f"- description: {task.description}",
                f"- verification: {task.verification_plan.get('command', 'none')}",
                "",
            ]
        )
    if lines and lines[-1] == "":
        lines.pop()
    artifact_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return artifact_path


def _require_project(storage: Storage, project_id: str) -> RegisteredProject:
    project = storage.get_registered_project(project_id)
    if project is None:
        raise PlanningError(f"project {project_id} is not registered")
    return project


def _relative_goal_path(project_id: str, goal_id: str) -> Path:
    return Path(".clanker") / "projects" / project_id / "goals" / goal_id


def _write_goal_artifact(
    root: Path,
    project: RegisteredProject,
    goal: GoalRecord,
) -> Path:
    artifact_path = root / _relative_goal_path(project.name, goal.id) / "GOAL.md"
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        "\n".join(
            [
                f"# Goal {goal.id}",
                "",
                f"- project_id: {goal.project_id}",
                f"- title: {goal.title}",
                f"- original_prompt: {goal.original_prompt}",
                f"- status: {goal.status}",
                f"- priority: {goal.priority}",
                f"- default_test_command: {project.default_test_command}",
                f"- created_at: {goal.created_at}",
                f"- updated_at: {goal.updated_at}",
                "",
                "## Non-Claims",
                "",
                "- Goal creation does not execute tasks.",
                "- Goal creation does not commit, push, deploy, or call model providers.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return artifact_path


def _create_default_plan_steps(
    storage: Storage,
    *,
    goal: GoalRecord,
    project: RegisteredProject,
    plan: PlanRecord,
    reason: str | None,
) -> list[PlanStepRecord]:
    reason_suffix = f" Replan reason: {reason}" if reason else ""
    specs = [
        {
            "title": "Clarify scope and acceptance criteria",
            "description": f"Confirm target behavior and proof boundary for: {goal.title}.{reason_suffix}",
            "acceptance": "Scope, non-goals, and verifier are explicit.",
            "command": f"python3 -m agent_os.cli project-context {project.name}",
            "profile": "planner",
        },
        {
            "title": "Implement the smallest safe change",
            "description": f"Make the minimal local change that satisfies the goal: {goal.title}.",
            "acceptance": "Changed files are limited to the agreed scope and have local evidence.",
            "command": project.default_test_command,
            "profile": "coder",
        },
        {
            "title": "Verify evidence and decide next action",
            "description": "Run verification, refresh operator views, and preserve explicit non-claims.",
            "acceptance": "Tests, dashboard, handoff, and next-action evidence are current.",
            "command": project.default_test_command,
            "profile": "tester",
        },
    ]
    steps: list[PlanStepRecord] = []
    for index, spec in enumerate(specs, start=1):
        task_id = storage.create_task(
            goal_id=goal.id,
            project_id=project.name,
            task_type="planned_step",
            description=spec["description"],
            verification_plan={
                "source": "plan_step",
                "command": spec["command"],
                "acceptance_criteria": spec["acceptance"],
            },
            priority=10 + index,
            risk_level="low",
            skill_tags=["plan-lifecycle"],
            evidence={"source": "plan_step", "plan_id": plan.id},
        )
        storage.set_task_status(task_id, "planned")
        steps.append(
            storage.create_plan_step(
                plan_id=plan.id,
                goal_id=goal.id,
                order_index=index,
                title=spec["title"],
                description=spec["description"],
                acceptance_criteria=spec["acceptance"],
                verification_command=spec["command"],
                status="planned",
                assigned_profile=spec["profile"],
                task_id=task_id,
            )
        )
    return steps


def _plan_summary(goal: GoalRecord, reason: str | None) -> str:
    if reason:
        return f"Replan for {goal.title}: {reason}"
    return f"Initial plan for {goal.title}"


def _write_plan_artifacts(
    root: Path,
    project: RegisteredProject,
    goal: GoalRecord,
    plan: PlanRecord,
    steps: list[PlanStepRecord],
) -> None:
    version_path = root / plan.artifact_path
    latest_path = root / _relative_goal_path(project.name, goal.id) / "PLAN.md"
    version_path.parent.mkdir(parents=True, exist_ok=True)
    text = _render_plan_markdown(goal, plan, steps)
    version_path.write_text(text, encoding="utf-8")
    latest_path.write_text(text, encoding="utf-8")


def _render_plan_markdown(
    goal: GoalRecord,
    plan: PlanRecord,
    steps: list[PlanStepRecord],
) -> str:
    lines = [
        f"# Plan v{plan.version} For {goal.id}",
        "",
        f"- goal: {goal.title}",
        f"- status: {plan.status}",
        f"- created_by_profile: {plan.created_by_profile}",
        f"- summary: {plan.summary}",
        "",
        "## Steps",
        "",
    ]
    for step in steps:
        lines.extend(
            [
                f"### {step.order_index}. {step.title}",
                "",
                f"- status: {step.status}",
                f"- assigned_profile: {step.assigned_profile}",
                f"- task_id: {step.task_id or 'none'}",
                f"- acceptance_criteria: {step.acceptance_criteria}",
                f"- verification_command: {step.verification_command}",
                f"- blocked_reason: {step.blocked_reason or 'none'}",
                "",
                step.description,
                "",
            ]
        )
    lines.extend(
        [
            "## Non-Claims",
            "",
            "- Plan creation does not execute tasks.",
            "- Plan creation does not commit, push, deploy, or call model providers.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_contract_artifact(
    root: Path,
    project: RegisteredProject,
    goal: GoalRecord,
    plan: PlanRecord,
    steps: list[PlanStepRecord],
    contract: SprintContractRecord,
) -> Path:
    artifact_path = root / contract.artifact_path
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        "\n".join(
            [
                f"# Sprint Contract {contract.id}",
                "",
                f"- project_id: {project.name}",
                f"- goal_id: {goal.id}",
                f"- plan_id: {plan.id}",
                f"- plan_version: {plan.version}",
                f"- status: {contract.status}",
                "",
                "## Scope",
                "",
                contract.scope,
                "",
                "## Non-Goals",
                "",
                contract.non_goals,
                "",
                "## Acceptance Criteria",
                "",
                contract.acceptance_criteria,
                "",
                "## Verification Plan",
                "",
                contract.verification_plan,
                "",
                "## Risk Notes",
                "",
                contract.risk_notes,
                "",
                "## Evaluator Notes",
                "",
                contract.evaluator_notes,
                "",
                "## Plan Steps",
                "",
                *[f"- {step.order_index}. {step.title}: {step.status}" for step in steps],
                "",
                "## Non-Claims",
                "",
                "- Contract creation does not approve work.",
                "- Contract creation does not run tests, commit, push, deploy, or call model providers.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return artifact_path
