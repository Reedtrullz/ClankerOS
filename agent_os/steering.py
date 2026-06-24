from __future__ import annotations

from pathlib import Path

from agent_os.coder_worktree_execution import (
    list_coder_worktree_approvals,
    list_coder_worktree_commit_approvals,
    list_coder_worktree_runs,
)
from agent_os.storage import ApprovalRequest, Incident, SteeringReview, Storage, Task


def render_steering_review_line(review: SteeringReview) -> str:
    operator = "true" if review.requires_operator else "false"
    return (
        f"- {review.id}: status={review.status} goal={review.goal_id} "
        f"run={review.run_id or 'none'} drift={review.drift_score} "
        f"action={review.recommended_next_action} requires_operator={operator} "
        f"report={review.report_path}"
    )


def write_steering_review(root: Path, goal_id: str) -> tuple[Path, SteeringReview]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    goal = storage.get_goal(goal_id)
    run_id = storage.latest_run_id_for_goal(goal_id)
    tasks = storage.list_tasks(goal_id)
    approvals = storage.list_approval_requests_for_goal(goal_id)
    incidents = _incidents_for_goal(storage, goal_id)

    pending_approvals = [
        approval for approval in approvals if approval.status == "pending"
    ]
    open_incidents = [
        incident for incident in incidents if incident.status == "open"
    ]
    blocked_tasks = [task for task in tasks if task.status == "blocked"]
    failed_tasks = [task for task in tasks if task.status == "failed"]
    repeated_attempt_tasks = [
        task for task in tasks if task.status in {"failed", "blocked"} and task.attempts >= 2
    ]
    completed_tasks_without_evidence = [
        task for task in tasks if task.status == "completed" and not task.evidence
    ]
    active_tasks = [
        task
        for task in tasks
        if task.status in {"claimed", "running", "verifying", "waiting_approval"}
    ]

    findings: list[dict[str, object]] = []
    status = "clear"
    drift_score = "none"
    recommended_next_action = "continue"
    requires_operator = False
    current_task_id = _current_task_id(tasks)

    if pending_approvals:
        approval = pending_approvals[0]
        current_task_id = approval.task_id
        status = "operator_required"
        drift_score = "low"
        recommended_next_action = "operator_approval"
        requires_operator = True
        findings.append(_approval_finding(approval))
    elif blocked_tasks:
        task = blocked_tasks[0]
        current_task_id = task.id
        status = "review_required"
        drift_score = "high"
        recommended_next_action = "review_or_replan"
        requires_operator = True
        findings.append(_task_finding("blocked_task", "high", task))
    elif repeated_attempt_tasks:
        task = repeated_attempt_tasks[0]
        current_task_id = task.id
        status = "review_required"
        drift_score = "high"
        recommended_next_action = "review_or_replan"
        requires_operator = True
        findings.append(_task_finding("repeated_failed_task", "high", task))
    elif failed_tasks:
        task = failed_tasks[0]
        current_task_id = task.id
        status = "review_required"
        drift_score = "high"
        recommended_next_action = "review_or_replan"
        requires_operator = True
        findings.append(_task_finding("failed_task", "high", task))
    elif open_incidents:
        incident = open_incidents[0]
        status = "review_required"
        drift_score = "medium"
        recommended_next_action = "review_open_incident"
        requires_operator = True
        findings.append(_incident_finding(incident))
    elif completed_tasks_without_evidence:
        task = completed_tasks_without_evidence[0]
        current_task_id = task.id
        status = "review_required"
        drift_score = "high"
        recommended_next_action = "add_evidence_or_replan"
        requires_operator = True
        findings.append(_task_finding("completed_without_evidence", "high", task))
    elif tasks and all(task.status == "completed" for task in tasks) and goal.status != "completed":
        status = "final_review_required"
        drift_score = "none"
        recommended_next_action = "final_review"
        findings.append(
            {
                "kind": "goal_open_after_tasks_complete",
                "severity": "info",
                "goal_id": goal.id,
                "message": "all tasks are complete but the goal is not closed",
            }
        )
    elif not tasks:
        status = "plan_required"
        drift_score = "medium"
        recommended_next_action = "create_task_plan"
        requires_operator = True
        findings.append(
            {
                "kind": "no_tasks",
                "severity": "medium",
                "goal_id": goal.id,
                "message": "goal has no task graph yet",
            }
        )
    elif active_tasks:
        task = active_tasks[0]
        current_task_id = task.id
        status = "in_progress"
        drift_score = "low"
        recommended_next_action = "continue_current_task"
        findings.append(_task_finding("active_task", "low", task))
    else:
        findings.append(
            {
                "kind": "no_blockers_detected",
                "severity": "info",
                "goal_id": goal.id,
                "message": "no deterministic steering blockers were detected",
            }
        )

    report_path = Path("docs") / "steering-review.md"
    review = storage.record_steering_review(
        goal_id=goal.id,
        project_id=goal.project_id,
        run_id=run_id,
        reviewed_plan_version="tasks:v1",
        current_task_id=current_task_id,
        status=status,
        drift_score=drift_score,
        findings=findings,
        recommended_next_action=recommended_next_action,
        requires_operator=requires_operator,
        report_path=str(report_path),
    )
    absolute_report_path = root / report_path
    absolute_report_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_report_path.write_text(
        _render_report(
            review=review,
            task_count=len(tasks),
            approval_count=len(approvals),
            pending_approval_count=len(pending_approvals),
            open_incident_count=len(open_incidents),
        ),
        encoding="utf-8",
    )
    return absolute_report_path, review


def next_action_for_target(root: Path, target: str) -> tuple[Path, SteeringReview]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    if target.startswith("goal_"):
        goal_id = target
    else:
        goal = storage.latest_goal_for_project(target)
        if goal is None:
            raise KeyError(target)
        goal_id = goal.id
    return write_steering_review(root, goal_id)


def collect_inbox_items(root: Path) -> dict[str, object]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    steering_reviews = storage.list_recent_steering_reviews(
        limit=5,
        requires_operator=True,
    )
    pending_approvals = storage.list_pending_approvals()
    open_incidents = [
        incident
        for incident in storage.list_recent_incidents(limit=10)
        if incident.status == "open"
    ]
    subagent_delegations = storage.list_recent_subagent_delegations(limit=10)
    coder_worktree_approvals = list_coder_worktree_approvals(
        root,
        status="pending_operator_approval",
        limit=10,
    )
    coder_worktree_runs = list_coder_worktree_runs(root, limit=10)
    coder_worktree_commit_approvals = list_coder_worktree_commit_approvals(
        root,
        status="pending_operator_approval",
        limit=10,
    )
    coder_worktree_commits = list_coder_worktree_commit_approvals(
        root,
        status="committed",
        limit=10,
    )
    return {
        "steering_reviews": steering_reviews,
        "pending_approvals": pending_approvals,
        "open_incidents": open_incidents,
        "subagent_delegations": subagent_delegations,
        "coder_worktree_approvals": coder_worktree_approvals,
        "coder_worktree_runs": coder_worktree_runs,
        "coder_worktree_commit_approvals": coder_worktree_commit_approvals,
        "coder_worktree_commits": coder_worktree_commits,
        "count": (
            len(steering_reviews)
            + len(pending_approvals)
            + len(open_incidents)
            + len(subagent_delegations)
            + len(coder_worktree_approvals)
            + len(coder_worktree_runs)
            + len(coder_worktree_commit_approvals)
            + len(coder_worktree_commits)
        ),
    }


def _current_task_id(tasks: list[Task]) -> str | None:
    for status in ("running", "claimed", "verifying", "waiting_approval", "blocked", "failed"):
        for task in tasks:
            if task.status == status:
                return task.id
    return tasks[-1].id if tasks else None


def _incidents_for_goal(storage: Storage, goal_id: str) -> list[Incident]:
    return [
        incident
        for incident in storage.list_recent_incidents(limit=100)
        if incident.goal_id == goal_id
    ]


def _approval_finding(approval: ApprovalRequest) -> dict[str, object]:
    return {
        "kind": "pending_approval",
        "severity": "operator",
        "approval_id": approval.id,
        "task_id": approval.task_id,
        "run_id": approval.run_id,
        "message": "a pending approval blocks task execution",
    }


def _incident_finding(incident: Incident) -> dict[str, object]:
    return {
        "kind": "open_incident",
        "severity": incident.severity,
        "incident_id": incident.id,
        "task_id": incident.task_id,
        "message": incident.summary,
    }


def _task_finding(kind: str, severity: str, task: Task) -> dict[str, object]:
    return {
        "kind": kind,
        "severity": severity,
        "task_id": task.id,
        "task_type": task.task_type,
        "status": task.status,
        "attempts": task.attempts,
        "message": task.description,
    }


def _render_report(
    *,
    review: SteeringReview,
    task_count: int,
    approval_count: int,
    pending_approval_count: int,
    open_incident_count: int,
) -> str:
    lines = [
        "# Steering Review",
        "",
        f"- id: {review.id}",
        f"- goal_id: {review.goal_id}",
        f"- project_id: {review.project_id}",
        f"- run_id: {review.run_id or 'none'}",
        f"- reviewed_plan_version: {review.reviewed_plan_version}",
        f"- current_task_id: {review.current_task_id or 'none'}",
        f"- status: {review.status}",
        f"- drift_score: {review.drift_score}",
        f"- recommended_next_action: {review.recommended_next_action}",
        f"- requires_operator: {'true' if review.requires_operator else 'false'}",
        f"- task_count: {task_count}",
        f"- approval_count: {approval_count}",
        f"- pending_approval_count: {pending_approval_count}",
        f"- open_incident_count: {open_incident_count}",
        f"- created_at: {review.created_at}",
        "",
        "## Findings",
        "",
    ]
    for finding in review.findings:
        lines.append(
            f"- {finding.get('kind')}: severity={finding.get('severity')} "
            f"message={finding.get('message')}"
        )
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- network_actions_taken: 0",
            "- external_mutations_taken: 0",
            "- automatic_retries_taken: 0",
            "- task_execution_started: 0",
        ]
    )
    return "\n".join(lines) + "\n"
