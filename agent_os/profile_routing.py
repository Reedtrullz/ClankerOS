from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import AgentProfile, RoutingDecision, Storage, Task


DEFAULT_PROFILES = [
    {
        "name": "planner",
        "label": "Strategic Planner",
        "model": "configurable/planner-model",
        "cost_tier": "high",
        "mode": "primary",
        "tools_json": ["read", "grep", "plan_write"],
        "permissions_json": {
            "read": "allow",
            "write": "deny",
            "shell": "deny",
            "commit": "deny",
        },
        "use_for_json": ["ambiguous_goal", "architecture", "plan_creation", "replan"],
        "max_budget_json": {"tokens": 20000, "seconds": 300},
    },
    {
        "name": "coder",
        "label": "Implementation Coder",
        "model": "configurable/coder-model",
        "cost_tier": "high",
        "mode": "primary",
        "tools_json": ["read", "write", "shell", "diff"],
        "permissions_json": {
            "read": "allow",
            "write": "allow_in_worktree",
            "shell": "allow_safe",
            "commit": "approval_required",
        },
        "use_for_json": ["implementation", "refactor", "bugfix"],
        "max_budget_json": {"tokens": 30000, "seconds": 600},
    },
    {
        "name": "scout",
        "label": "Repo Scout",
        "model": "configurable/cheap-fast-model",
        "cost_tier": "low",
        "mode": "subagent",
        "tools_json": ["read", "grep", "summarize"],
        "permissions_json": {
            "read": "allow",
            "write": "deny",
            "shell": "deny",
            "commit": "deny",
        },
        "use_for_json": ["repo_search", "file_mapping", "dependency_mapping", "summarization"],
        "max_budget_json": {"tokens": 8000, "seconds": 180},
    },
    {
        "name": "tester",
        "label": "Verification Tester",
        "model": "configurable/cheap-coding-model",
        "cost_tier": "low",
        "mode": "subagent",
        "tools_json": ["read", "shell"],
        "permissions_json": {
            "read": "allow",
            "write": "deny",
            "shell": "allow_tests_only",
            "commit": "deny",
        },
        "use_for_json": ["test_triage", "failure_summary", "verification_review"],
        "max_budget_json": {"tokens": 12000, "seconds": 300},
    },
    {
        "name": "evaluator",
        "label": "Alignment Evaluator",
        "model": "configurable/strong-reasoning-model",
        "cost_tier": "medium",
        "mode": "subagent",
        "tools_json": ["read", "grep", "evidence_read"],
        "permissions_json": {
            "read": "allow",
            "write": "deny",
            "shell": "deny",
            "commit": "deny",
        },
        "use_for_json": ["sprint_contract_review", "alignment_review", "evidence_review", "final_review"],
        "max_budget_json": {"tokens": 20000, "seconds": 420},
    },
]


DEFAULT_ROUTING_RULES = [
    ("repo_search", "scout", "planner"),
    ("file_mapping", "scout", "planner"),
    ("dependency_mapping", "scout", "planner"),
    ("summarization", "scout", "planner"),
    ("test_triage", "tester", "evaluator"),
    ("failure_summary", "tester", "evaluator"),
    ("verification_review", "tester", "evaluator"),
    ("implementation", "coder", "planner"),
    ("refactor", "coder", "planner"),
    ("bugfix", "coder", "planner"),
    ("ambiguous_goal", "planner", "evaluator"),
    ("architecture", "planner", "evaluator"),
    ("plan_creation", "planner", "evaluator"),
    ("replan", "planner", "evaluator"),
    ("sprint_contract_review", "evaluator", "planner"),
    ("alignment_review", "evaluator", "planner"),
    ("evidence_review", "evaluator", "planner"),
    ("final_review", "evaluator", "planner"),
]


TASK_TYPE_CATEGORY_MAP = {
    "test_triage": "test_triage",
    "failure_summary": "failure_summary",
    "verification_review": "verification_review",
    "write_goal_artifact": "implementation",
    "record_learning": "summarization",
    "coding_change": "implementation",
    "bugfix": "bugfix",
    "refactor": "refactor",
    "capability_activation_followup_task": "evidence_review",
    "capability_activation_followup_result_task": "evidence_review",
    "capability_activation_followup_result_task_result_effect_task": "evidence_review",
    "capability_activation_followup_result_task_result_effect_task_result_effect_task": "evidence_review",
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task": "evidence_review",
}


@dataclass(frozen=True)
class RouteRequest:
    task_id: str | None = None
    category: str | None = None
    project_id: str | None = None
    profile_override: str | None = None


def ensure_default_profiles(storage: Storage) -> list[AgentProfile]:
    for profile in DEFAULT_PROFILES:
        storage.upsert_profile(**profile)
    for category, preferred, fallback in DEFAULT_ROUTING_RULES:
        storage.upsert_routing_rule(
            category=category,
            preferred_profile=preferred,
            fallback_profile=fallback,
        )
    return storage.list_profiles()


def write_default_profile_config(root: Path) -> Path:
    config_path = root / ".clanker" / "profiles.yml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        return config_path
    lines = [
        "# Safe local defaults for ClankerOS profile routing.",
        "# These are labels and policy hints, not provider credentials.",
        "profiles:",
    ]
    for profile in DEFAULT_PROFILES:
        lines.extend(
            [
                f"  - name: {profile['name']}",
                f"    label: {profile['label']}",
                f"    model: {profile['model']}",
                f"    cost_tier: {profile['cost_tier']}",
                f"    mode: {profile['mode']}",
                "    use_for:",
                *[f"      - {item}" for item in profile["use_for_json"]],
            ]
        )
    lines.append("routing_rules:")
    for category, preferred, fallback in DEFAULT_ROUTING_RULES:
        lines.extend(
            [
                f"  - category: {category}",
                f"    preferred_profile: {preferred}",
                f"    fallback_profile: {fallback}",
            ]
        )
    config_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return config_path


def route_work(storage: Storage, request: RouteRequest) -> RoutingDecision:
    ensure_default_profiles(storage)
    task = _get_task_or_none(storage, request.task_id)
    category = request.category or _category_for_task(task)
    project_id = request.project_id or (task.project_id if task is not None else None)
    goal_id = task.goal_id if task is not None else None

    if request.profile_override:
        profile = storage.get_profile(request.profile_override)
        if profile is None:
            raise KeyError(request.profile_override)
        reason = (
            f"operator_override: selected {profile.name} for category {category}"
        )
    else:
        rule = storage.get_routing_rule(category)
        profile_name = rule.preferred_profile if rule is not None else "planner"
        profile = storage.get_profile(profile_name)
        if profile is None and rule is not None:
            profile = storage.get_profile(rule.fallback_profile)
        if profile is None:
            profile = storage.get_profile("planner")
        if profile is None:
            raise KeyError("planner")
        reason = _routing_reason(category, profile.name, task)

    return storage.record_routing_decision(
        task_id=task.id if task is not None else None,
        goal_id=goal_id,
        project_id=project_id,
        selected_profile=profile.name,
        selected_model=profile.model,
        category=category,
        reason=reason,
        estimated_cost_tier=profile.cost_tier,
        status="selected",
    )


def format_profile_line(profile: AgentProfile) -> str:
    use_for = ",".join(profile.use_for_json)
    return (
        f"{profile.name}: {profile.label} mode={profile.mode} "
        f"cost={profile.cost_tier} model={profile.model} use_for={use_for}"
    )


def format_routing_decision_line(decision: RoutingDecision) -> str:
    return (
        f"{decision.id}: category={decision.category} "
        f"selected={decision.selected_profile} model={decision.selected_model} "
        f"cost={decision.estimated_cost_tier} task={decision.task_id or 'none'} "
        f"project={decision.project_id or 'none'} status={decision.status}"
    )


def _get_task_or_none(storage: Storage, task_id: str | None) -> Task | None:
    if task_id is None:
        return None
    return storage.get_task(task_id)


def _category_for_task(task: Task | None) -> str:
    if task is None:
        return "ambiguous_goal"
    return TASK_TYPE_CATEGORY_MAP.get(task.task_type, "implementation")


def _routing_reason(category: str, profile_name: str, task: Task | None) -> str:
    if task is None:
        return f"default_rule: category {category} selected {profile_name}"
    return (
        f"task_rule: task_type {task.task_type} mapped to category "
        f"{category} selected {profile_name}"
    )
