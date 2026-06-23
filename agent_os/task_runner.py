from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from agent_os.ids import new_id
from agent_os.planning import refresh_goal_planning_artifacts
from agent_os.profile_routing import RouteRequest, ensure_default_profiles, route_work
from agent_os.storage import (
    AgentProfile,
    GoalRecord,
    PlanStepRecord,
    RegisteredProject,
    RoutingDecision,
    SprintContractRecord,
    Storage,
    Task,
    utc_now,
)


class TaskRunError(ValueError):
    pass


@dataclass(frozen=True)
class TaskRunResult:
    task: Task
    goal: GoalRecord
    project: RegisteredProject
    step: PlanStepRecord
    contract: SprintContractRecord
    profile: AgentProfile
    routing_decision: RoutingDecision
    run_id: str
    status: str
    verification_passed: bool
    evidence_dir: Path
    summary_path: Path


def run_planned_task(
    root: Path,
    storage: Storage,
    task_id: str,
    *,
    profile_name: str | None = None,
) -> TaskRunResult:
    root = root.resolve()
    ensure_default_profiles(storage)
    task = storage.get_task(task_id)
    if task.status != "planned":
        raise TaskRunError(f"task {task.id} status {task.status} cannot be dispatched")
    goal = storage.get_goal(task.goal_id)
    project = storage.get_registered_project(task.project_id)
    if project is None:
        raise TaskRunError(f"project {task.project_id} is not registered")
    step = storage.get_plan_step_by_task(task.id)
    if step is None:
        raise TaskRunError(f"task {task.id} is not linked to a plan step")
    contract = storage.get_sprint_contract_for_plan(step.plan_id)
    if contract is None:
        raise TaskRunError(f"plan {step.plan_id} has no sprint contract")

    selected_profile = profile_name or step.assigned_profile
    if not selected_profile:
        raise TaskRunError(f"task {task.id} has no selected profile")
    profile = storage.get_profile(selected_profile)
    if profile is None:
        raise TaskRunError(f"profile {selected_profile} is not configured")
    command = _verification_command(task)
    _validate_profile_can_run_command(profile, command, project.default_test_command)
    _validate_safe_command(command)

    routing_decision = route_work(
        storage,
        RouteRequest(
            task_id=task.id,
            profile_override=profile.name,
            status="dispatched",
        ),
    )
    run_id = storage.create_run(goal.id, project.name, root / "runs")
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    activity_path = run_dir / "activity.md"
    events_path = run_dir / "events.jsonl"
    summary_path = run_dir / "summary.md"
    activity_path.write_text(f"# Activity For {run_id}\n\n", encoding="utf-8")
    events_path.write_text("", encoding="utf-8")

    _emit(
        storage,
        activity_path,
        events_path,
        run_id=run_id,
        goal_id=goal.id,
        task_id=task.id,
        event_type="task.dispatch_started",
        message=f"dispatched task {task.id} with profile {profile.name}",
        payload={
            "profile": profile.name,
            "model": profile.model,
            "routing_decision_id": routing_decision.id,
            "command": command,
        },
    )
    storage.start_task_run(task.id, run_id=run_id, owner=profile.name)
    completed = _run_command(command, Path(project.root_path), profile)
    _emit(
        storage,
        activity_path,
        events_path,
        run_id=run_id,
        goal_id=goal.id,
        task_id=task.id,
        event_type="task.command_completed",
        message=f"command completed for task {task.id} with exit {completed.returncode}",
        payload={
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        },
    )

    evidence_dir = (
        root
        / ".clanker"
        / "projects"
        / project.name
        / "goals"
        / goal.id
        / "runs"
        / run_id
        / "evidence"
    )
    evidence_dir.mkdir(parents=True, exist_ok=True)
    verification_passed = completed.returncode == 0
    evidence = {
        "passed": verification_passed,
        "adapter": "local_shell",
        "profile": profile.name,
        "model": profile.model,
        "routing_decision_id": routing_decision.id,
        "run_id": run_id,
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "evidence_packet": _relative(root, evidence_dir),
        "contract_id": contract.id,
        "plan_id": step.plan_id,
    }
    artifact_paths = _write_evidence_packet(
        root=root,
        evidence_dir=evidence_dir,
        task=storage.get_task(task.id),
        goal=goal,
        project=project,
        step=step,
        contract=contract,
        profile=profile,
        routing_decision=routing_decision,
        evidence=evidence,
    )

    if verification_passed:
        storage.mark_task_completed(
            task.id,
            evidence=evidence,
            artifacts=artifact_paths,
        )
        storage.update_plan_step_for_task(task.id, status="completed")
        status = "completed"
        event_type = "task.completed"
        message = f"completed task {task.id}"
    else:
        storage.mark_task_failed(task.id, evidence=evidence, artifacts=artifact_paths)
        storage.update_plan_step_for_task(
            task.id,
            status="failed",
            blocked_reason="verification command failed",
        )
        _record_verification_incident(
            root=root,
            storage=storage,
            run_id=run_id,
            goal=goal,
            task=task,
            evidence=evidence,
            artifacts=artifact_paths,
        )
        status = "failed"
        event_type = "task.failed"
        message = f"failed task {task.id}"

    artifact_paths = _write_evidence_packet(
        root=root,
        evidence_dir=evidence_dir,
        task=storage.get_task(task.id),
        goal=goal,
        project=project,
        step=storage.get_plan_step_by_task(task.id) or step,
        contract=contract,
        profile=profile,
        routing_decision=routing_decision,
        evidence=evidence,
    )
    storage.complete_run(run_id, status)
    _write_run_summary(summary_path, project.name, goal, task, profile, evidence, status)
    _emit(
        storage,
        activity_path,
        events_path,
        run_id=run_id,
        goal_id=goal.id,
        task_id=task.id,
        event_type=event_type,
        message=message,
        payload=evidence,
    )
    refresh_goal_planning_artifacts(root, storage, goal.id)
    return TaskRunResult(
        task=storage.get_task(task.id),
        goal=goal,
        project=project,
        step=storage.get_plan_step_by_task(task.id) or step,
        contract=contract,
        profile=profile,
        routing_decision=routing_decision,
        run_id=run_id,
        status=status,
        verification_passed=verification_passed,
        evidence_dir=evidence_dir,
        summary_path=evidence_dir / "summary.md",
    )


def _verification_command(task: Task) -> str:
    command = task.verification_plan.get("command")
    if not isinstance(command, str) or not command.strip():
        raise TaskRunError(f"task {task.id} has no verification command")
    return command.strip()


def _validate_profile_can_run_command(
    profile: AgentProfile,
    command: str,
    default_test_command: str,
) -> None:
    shell_permission = profile.permissions_json.get("shell", "deny")
    if shell_permission == "deny":
        raise TaskRunError(f"profile {profile.name} cannot run shell commands")
    if shell_permission == "allow_tests_only" and command != default_test_command:
        raise TaskRunError(
            f"profile {profile.name} can only run the project default test command"
        )
    if shell_permission not in {"allow_safe", "allow_tests_only"}:
        raise TaskRunError(f"profile {profile.name} shell permission is not executable")


def _validate_safe_command(command: str) -> None:
    lowered = command.lower()
    blocked_tokens = [
        "rm -rf",
        "git push",
        "gh pr create",
        "curl ",
        "wget ",
        "ssh ",
        "scp ",
    ]
    for token in blocked_tokens:
        if token in lowered:
            raise TaskRunError(f"unsafe shell command blocked: {token.strip()}")


def _run_command(
    command: str,
    cwd: Path,
    profile: AgentProfile,
) -> subprocess.CompletedProcess[str]:
    timeout = int(profile.max_budget_json.get("seconds", 300))
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        stderr = _timeout_output(error.stderr)
        if stderr:
            stderr += "\n"
        stderr += f"Command timed out after {timeout} seconds."
        return subprocess.CompletedProcess(
            args=command,
            returncode=124,
            stdout=_timeout_output(error.stdout),
            stderr=stderr,
        )


def _timeout_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _write_evidence_packet(
    *,
    root: Path,
    evidence_dir: Path,
    task: Task,
    goal: GoalRecord,
    project: RegisteredProject,
    step: PlanStepRecord,
    contract: SprintContractRecord,
    profile: AgentProfile,
    routing_decision: RoutingDecision,
    evidence: dict[str, object],
) -> list[str]:
    verification_path = evidence_dir / "verification.json"
    verification_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    tasks_path = evidence_dir / "tasks.json"
    tasks_path.write_text(
        json.dumps(
            {
                "task": _task_payload(task),
                "plan_step": {
                    "id": step.id,
                    "plan_id": step.plan_id,
                    "status": step.status,
                    "assigned_profile": step.assigned_profile,
                    "acceptance_criteria": step.acceptance_criteria,
                    "verification_command": step.verification_command,
                },
                "contract": {
                    "id": contract.id,
                    "status": contract.status,
                    "scope": contract.scope,
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    routing_path = evidence_dir / "routing_decisions.jsonl"
    routing_path.write_text(
        json.dumps(
            {
                "id": routing_decision.id,
                "task_id": routing_decision.task_id,
                "goal_id": routing_decision.goal_id,
                "project_id": routing_decision.project_id,
                "selected_profile": routing_decision.selected_profile,
                "selected_model": routing_decision.selected_model,
                "category": routing_decision.category,
                "status": routing_decision.status,
                "reason": routing_decision.reason,
                "created_at": routing_decision.created_at,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    commands_path = evidence_dir / "commands.jsonl"
    commands_path.write_text(
        json.dumps(
            {
                "command": evidence["command"],
                "cwd": project.root_path,
                "profile": profile.name,
                "adapter": evidence["adapter"],
                "returncode": evidence["returncode"],
                "created_at": utc_now(),
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    tests_path = evidence_dir / "tests.txt"
    tests_path.write_text(str(evidence["stdout"]), encoding="utf-8")
    stdout_path = evidence_dir / "stdout.txt"
    stdout_path.write_text(str(evidence["stdout"]), encoding="utf-8")
    stderr_path = evidence_dir / "stderr.txt"
    stderr_path.write_text(str(evidence["stderr"]), encoding="utf-8")
    summary_path = evidence_dir / "summary.md"
    summary_path.write_text(
        "\n".join(
            [
                f"# Task Run Evidence {evidence['run_id']}",
                "",
                f"- project_id: {project.name}",
                f"- goal_id: {goal.id}",
                f"- task_id: {task.id}",
                f"- profile: {profile.name}",
                f"- routing_decision: {routing_decision.id}",
                f"- contract: {contract.id}",
                f"- command: {evidence['command']}",
                f"- returncode: {evidence['returncode']}",
                f"- passed: {str(evidence['passed']).lower()}",
                "",
                "## Stdout",
                "",
                str(evidence["stdout"]).strip() or "none",
                "",
                "## Stderr",
                "",
                str(evidence["stderr"]).strip() or "none",
                "",
                "## Non-Claims",
                "",
                "- No commit, push, deploy, provider call, or external mutation was performed.",
                "- This evidence packet records local shell verification only.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return [
        _relative(root, summary_path),
        _relative(root, verification_path),
        _relative(root, routing_path),
        _relative(root, commands_path),
        _relative(root, tasks_path),
        _relative(root, tests_path),
        _relative(root, stdout_path),
        _relative(root, stderr_path),
    ]


def _task_payload(task: Task) -> dict[str, object]:
    return {
        "id": task.id,
        "run_id": task.run_id,
        "goal_id": task.goal_id,
        "project_id": task.project_id,
        "task_type": task.task_type,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "risk_level": task.risk_level,
        "verification_plan": task.verification_plan,
    }


def _record_verification_incident(
    *,
    root: Path,
    storage: Storage,
    run_id: str,
    goal: GoalRecord,
    task: Task,
    evidence: dict[str, object],
    artifacts: list[str],
) -> str:
    incident_id = new_id("incident")
    evidence_path = root / "runs" / run_id / "incidents" / f"{incident_id}.json"
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": incident_id,
        "run_id": run_id,
        "goal_id": goal.id,
        "task_id": task.id,
        "incident_type": "verification_failed",
        "evidence": evidence,
        "artifacts": artifacts,
    }
    evidence_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    storage.record_incident(
        incident_id=incident_id,
        project_id=task.project_id,
        run_id=run_id,
        goal_id=goal.id,
        task_id=task.id,
        task_type=task.task_type,
        incident_type="verification_failed",
        severity="medium",
        status="open",
        summary=f"Verification command failed for task {task.id}.",
        failure_class="verification_failed",
        verification_method="local_shell",
        verification_path=_relative(root, evidence_path),
        failed_checks=[str(evidence["command"])],
        evidence=evidence,
        artifacts=artifacts,
        evidence_path=_relative(root, evidence_path),
    )
    return incident_id


def _write_run_summary(
    summary_path: Path,
    project_id: str,
    goal: GoalRecord,
    task: Task,
    profile: AgentProfile,
    evidence: dict[str, object],
    status: str,
) -> None:
    summary_path.write_text(
        "\n".join(
            [
                f"# Run Summary {evidence['run_id']}",
                "",
                f"- Project: {project_id}",
                f"- Goal ID: {goal.id}",
                f"- Goal: {goal.title}",
                f"- Task ID: {task.id}",
                f"- Profile: {profile.name}",
                f"- Status: {status}",
                f"- Verification Passed: {str(evidence['passed']).lower()}",
                f"- Evidence Packet: {evidence['evidence_packet']}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _emit(
    storage: Storage,
    activity_path: Path,
    events_path: Path,
    *,
    run_id: str,
    goal_id: str | None,
    task_id: str | None,
    event_type: str,
    message: str,
    payload: dict[str, object],
) -> None:
    storage.record_event(
        run_id=run_id,
        goal_id=goal_id,
        task_id=task_id,
        event_type=event_type,
        message=message,
        payload=payload,
    )
    event = {
        "created_at": utc_now(),
        "run_id": run_id,
        "goal_id": goal_id,
        "task_id": task_id,
        "event_type": event_type,
        "message": message,
        "payload": payload,
    }
    with events_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    with activity_path.open("a", encoding="utf-8") as handle:
        handle.write(f"- {event['created_at']} - {message}\n")


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
