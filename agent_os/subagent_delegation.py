from __future__ import annotations

import json
import re
from pathlib import Path

from agent_os.profile_routing import RouteRequest, route_work
from agent_os.storage import AgentProfile, RoutingDecision, Storage, SubagentDelegation, Task


class DelegationError(ValueError):
    pass


EXPECTED_OUTPUT_BY_CATEGORY = {
    "repo_search": "file_relevance_report",
    "file_mapping": "file_relevance_report",
    "dependency_mapping": "dependency_map",
    "summarization": "file_relevance_report",
    "test_triage": "failing_test_summary",
    "failure_summary": "failing_test_summary",
    "verification_review": "evidence_review",
    "sprint_contract_review": "risk_review",
    "alignment_review": "risk_review",
    "evidence_review": "evidence_review",
    "final_review": "evidence_review",
}


def create_subagent_delegation(
    root: Path,
    storage: Storage,
    *,
    task_id: str,
    title: str,
    profile_override: str | None = None,
) -> SubagentDelegation:
    task = storage.get_task(task_id)
    decision = route_work(
        storage,
        RouteRequest(
            task_id=task_id,
            profile_override=profile_override,
        ),
    )
    profile = storage.get_profile(decision.selected_profile)
    if profile is None:
        raise DelegationError(f"profile {decision.selected_profile} not found")
    _validate_read_only_subagent(profile)

    artifact_path = (
        root
        / ".clanker"
        / "delegations"
        / f"{task_id}-{_slug(title)}.json"
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    prompt = _build_prompt(task, title, decision, profile)
    input_context = _build_input_context(task, decision, profile)
    forbidden_actions = _forbidden_actions(profile)
    expected_output_schema = EXPECTED_OUTPUT_BY_CATEGORY.get(
        decision.category,
        "implementation_options",
    )
    delegation = storage.record_subagent_delegation(
        routing_decision_id=decision.id,
        parent_goal_id=task.goal_id,
        parent_task_id=task.id,
        assigned_profile=profile.name,
        category=decision.category,
        title=title,
        prompt=prompt,
        input_context_json=input_context,
        allowed_tools_json=profile.tools_json,
        forbidden_actions_json=forbidden_actions,
        expected_output_schema=expected_output_schema,
        budget_json=profile.max_budget_json,
        status="pending",
        result_summary=None,
        result_artifact_path=str(artifact_path),
    )
    artifact_path.write_text(
        json.dumps(
            {
                "id": delegation.id,
                "routing_decision_id": delegation.routing_decision_id,
                "parent_goal_id": delegation.parent_goal_id,
                "parent_task_id": delegation.parent_task_id,
                "assigned_profile": delegation.assigned_profile,
                "category": delegation.category,
                "title": delegation.title,
                "prompt": delegation.prompt,
                "input_context": delegation.input_context_json,
                "allowed_tools": delegation.allowed_tools_json,
                "forbidden_actions": delegation.forbidden_actions_json,
                "expected_output_schema": delegation.expected_output_schema,
                "budget": delegation.budget_json,
                "status": delegation.status,
                "execution_started": False,
                "network_actions_taken": 0,
                "external_mutations_taken": 0,
                "non_claims": [
                    "No subagent was started.",
                    "No model provider was called.",
                    "No file, git, approval, or external state was mutated.",
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return delegation


def render_subagent_delegation_line(delegation: SubagentDelegation) -> str:
    return (
        f"{delegation.id}: status={delegation.status} "
        f"profile={delegation.assigned_profile} category={delegation.category} "
        f"task={delegation.parent_task_id} schema={delegation.expected_output_schema} "
        f"artifact={delegation.result_artifact_path}"
    )


def _validate_read_only_subagent(profile: AgentProfile) -> None:
    permissions = profile.permissions_json
    if (
        profile.mode != "subagent"
        or permissions.get("write") != "deny"
        or permissions.get("commit") != "deny"
    ):
        raise DelegationError(
            f"profile {profile.name} is not a read-only subagent"
        )


def _build_prompt(
    task: Task,
    title: str,
    decision: RoutingDecision,
    profile: AgentProfile,
) -> str:
    return "\n".join(
        [
            f"/goal {title}",
            "",
            "Context:",
            f"- parent_goal_id: {task.goal_id}",
            f"- parent_task_id: {task.id}",
            f"- project_id: {task.project_id}",
            f"- task_type: {task.task_type}",
            f"- task_description: {task.description}",
            f"- routing_category: {decision.category}",
            f"- assigned_profile: {profile.name}",
            "",
            "Boundaries:",
            "- Read-only context gathering only.",
            "- Do not write files, commit, approve, call external services, or mutate state.",
            "",
            "Deliverable:",
            f"- Return structured output matching `{EXPECTED_OUTPUT_BY_CATEGORY.get(decision.category, 'implementation_options')}`.",
        ]
    )


def _build_input_context(
    task: Task,
    decision: RoutingDecision,
    profile: AgentProfile,
) -> dict[str, object]:
    return {
        "parent_goal_id": task.goal_id,
        "parent_task_id": task.id,
        "project_id": task.project_id,
        "task_type": task.task_type,
        "task_description": task.description,
        "verification_plan": task.verification_plan,
        "routing_decision_id": decision.id,
        "routing_reason": decision.reason,
        "profile": profile.name,
        "model": profile.model,
    }


def _forbidden_actions(profile: AgentProfile) -> list[str]:
    forbidden = {"approve", "external_state_mutation"}
    permissions = profile.permissions_json
    for action in ["commit", "shell", "write"]:
        if permissions.get(action) == "deny":
            forbidden.add(action)
    return sorted(forbidden)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "delegation"
