from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agent_os.profile_routing import RouteRequest, route_work
from agent_os.storage import (
    AgentProfile,
    RoutingDecision,
    Storage,
    SubagentDelegation,
    Task,
    utc_now,
)


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


REQUIRED_KEYS_BY_SCHEMA = {
    "file_relevance_report": {"files", "findings", "relevant_files"},
    "dependency_map": {"dependencies", "edges"},
    "failing_test_summary": {"failures", "failing_tests", "findings"},
    "implementation_options": {"options"},
    "risk_review": {"risks", "findings"},
    "evidence_review": {"evidence", "findings"},
}


STRICT_REQUIRED_KEYS_BY_SCHEMA = {
    "file_relevance_report": {"files", "findings", "relevant_files"},
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


def record_delegation_result(
    root: Path,
    storage: Storage,
    *,
    delegation_id: str,
    result_summary: str,
    structured_output: dict[str, Any],
    recorded_by: str = "operator",
    execution_metadata: dict[str, Any] | None = None,
) -> tuple[SubagentDelegation, bool]:
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        raise DelegationError(f"delegation {delegation_id} not found")
    _validate_structured_output(delegation.expected_output_schema, structured_output)

    artifact_path = root / ".clanker" / "delegations" / f"{delegation.id}-result.json"
    if delegation.status == "completed":
        artifact_path = Path(delegation.result_artifact_path)
        _validate_idempotent_result(
            artifact_path,
            result_summary=result_summary,
            structured_output=structured_output,
        )
        return delegation, True

    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    completed_at = utc_now()
    _write_result_artifact(
        artifact_path,
        delegation=delegation,
        result_summary=result_summary,
        structured_output=structured_output,
        recorded_by=recorded_by,
        completed_at=completed_at,
        execution_metadata=execution_metadata,
    )
    completed = storage.complete_subagent_delegation(
        delegation.id,
        result_summary=result_summary,
        result_artifact_path=str(artifact_path),
        completed_at=completed_at,
    )
    return completed, False


def render_subagent_delegation_line(delegation: SubagentDelegation) -> str:
    metadata = load_delegation_result_metadata(delegation)
    line = (
        f"{delegation.id}: status={delegation.status} "
        f"profile={delegation.assigned_profile} category={delegation.category} "
        f"task={delegation.parent_task_id} schema={delegation.expected_output_schema} "
        f"artifact={delegation.result_artifact_path}"
    )
    run_id = metadata.get("execution_run_id") or metadata.get("run_id")
    if run_id:
        line += f" run={run_id}"
    adapter_type = metadata.get("adapter_type") or metadata.get("execution_adapter_type")
    if adapter_type:
        line += f" adapter={adapter_type}"
    exit_code = metadata.get("exit_code")
    if exit_code is not None:
        line += f" exit_code={exit_code}"
    evidence_dir = metadata.get("execution_evidence_dir") or metadata.get("evidence_dir")
    if evidence_dir:
        line += f" evidence={evidence_dir}"
    incident_id = metadata.get("incident_id")
    if incident_id:
        line += f" incident={incident_id}"
    if delegation.result_summary:
        line += f" summary={delegation.result_summary}"
    return line


def load_delegation_result_metadata(delegation: SubagentDelegation) -> dict[str, Any]:
    if not delegation.result_artifact_path:
        return {}
    artifact_path = Path(delegation.result_artifact_path)
    if not artifact_path.exists():
        return {}
    try:
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    keys = {
        "adapter_type",
        "evidence_dir",
        "execution_adapter_type",
        "execution_evidence_dir",
        "execution_run_id",
        "exit_code",
        "incident_id",
        "network_actions_taken",
        "provider_calls_taken_by_clankeros",
        "run_id",
    }
    return {key: payload[key] for key in keys if key in payload}


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
        "task_evidence": task.evidence,
        "task_artifacts": task.artifacts,
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


def _validate_structured_output(
    expected_schema: str,
    structured_output: dict[str, Any],
) -> None:
    if not isinstance(structured_output, dict):
        raise DelegationError(
            f"output does not match expected schema {expected_schema}"
        )
    required_keys = REQUIRED_KEYS_BY_SCHEMA.get(expected_schema)
    if required_keys is None:
        return
    strict_required_keys = STRICT_REQUIRED_KEYS_BY_SCHEMA.get(expected_schema, set())
    missing_or_empty = sorted(
        key
        for key in strict_required_keys
        if not _is_non_empty_structured_value(structured_output.get(key))
    )
    if missing_or_empty:
        raise DelegationError(
            f"output does not match expected schema {expected_schema}"
        )
    if not any(
        _is_non_empty_structured_value(structured_output.get(key))
        for key in required_keys
    ):
        raise DelegationError(
            f"output does not match expected schema {expected_schema}"
        )


def _validate_idempotent_result(
    artifact_path: Path,
    *,
    result_summary: str,
    structured_output: dict[str, Any],
) -> None:
    if not artifact_path.exists():
        raise DelegationError("delegation already completed with missing result artifact")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if (
        artifact.get("result_summary") != result_summary
        or artifact.get("structured_output") != structured_output
    ):
        raise DelegationError("delegation already completed with different result")


def _write_result_artifact(
    artifact_path: Path,
    *,
    delegation: SubagentDelegation,
    result_summary: str,
    structured_output: dict[str, Any],
    recorded_by: str,
    completed_at: str,
    execution_metadata: dict[str, Any] | None,
) -> None:
    metadata = execution_metadata or {}
    network_actions_taken = metadata.get("network_actions_taken", 0)
    provider_calls_taken_by_clankeros = metadata.get("provider_calls_taken_by_clankeros", 0)
    external_mutations_taken = metadata.get("external_mutations_taken", 0)
    non_claims = metadata.get(
        "non_claims",
        [
            "No subagent was started by this ingestion command.",
            "No model provider was called by this ingestion command.",
            "No file, git, approval, or external state was mutated beyond this local result record.",
        ],
    )
    payload = {
        "id": delegation.id,
        "routing_decision_id": delegation.routing_decision_id,
        "parent_goal_id": delegation.parent_goal_id,
        "parent_task_id": delegation.parent_task_id,
        "assigned_profile": delegation.assigned_profile,
        "category": delegation.category,
        "title": delegation.title,
        "expected_output_schema": delegation.expected_output_schema,
        "status": "completed",
        "recorded_by": recorded_by,
        "result_summary": result_summary,
        "structured_output": structured_output,
        "created_at": delegation.created_at,
        "completed_at": completed_at,
        "execution_started": delegation.started_at is not None,
        "network_actions_taken": network_actions_taken,
        "provider_calls_taken_by_clankeros": provider_calls_taken_by_clankeros,
        "external_mutations_taken": external_mutations_taken,
        "non_claims": non_claims,
    }
    payload.update(
        {
            key: value
            for key, value in metadata.items()
            if key
            not in {
                "network_actions_taken",
                "provider_calls_taken_by_clankeros",
                "external_mutations_taken",
                "non_claims",
            }
        }
    )
    temp_path = artifact_path.with_name(f".{artifact_path.name}.tmp")
    temp_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    temp_path.replace(artifact_path)


def _is_non_empty_structured_value(value: Any) -> bool:
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return len(value) > 0
    return False


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "delegation"
