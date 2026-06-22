from __future__ import annotations

from pathlib import Path

from agent_os.operator_approval_effect_proposals import IDEMPOTENCY_PREFIX
from agent_os.storage import CapabilityActivationTaskBatch, Effect, Storage, Task


TASKS_RECORDED = "capability_activation_tasks_recorded"
TASKS_ALREADY_RECORDED = "capability_activation_tasks_already_recorded"
TASKS_NO_APPLIED_EFFECTS = "capability_activation_tasks_no_applied_effects"
REPORT_PATH = "docs/capability-activation-tasks.md"
TASK_TYPE = "capability_activation_task"
GOAL_DESCRIPTION = (
    "Prepare capability-specific activation gates from applied operator approval effects."
)


def write_capability_activation_tasks(
    root: Path,
) -> tuple[Path, CapabilityActivationTaskBatch, list[Task], list[Task], list[Effect]]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    applied_capability_effects = _applied_capability_effects(storage)
    existing_tasks = _existing_activation_tasks(storage)
    existing_task_source_effect_ids = {
        task.evidence.get("source_effect_id")
        for task in existing_tasks
        if task.evidence.get("source_effect_id")
    }
    effects_needing_tasks = [
        effect
        for effect in applied_capability_effects
        if effect.id not in existing_task_source_effect_ids
    ]

    goal_id = "none"
    created_tasks: list[Task] = []
    if effects_needing_tasks:
        goal_id = storage.get_or_create_goal("bootstrap", GOAL_DESCRIPTION)
        for effect in effects_needing_tasks:
            task_id = storage.create_task(
                goal_id=goal_id,
                project_id=effect.project_id,
                task_type=TASK_TYPE,
                description=_task_description(effect),
                priority=40,
                risk_level="high",
                skill_tags=["capability-activation", "operator-review", "local-files"],
                verification_plan=_verification_plan(effect),
                evidence=_task_evidence(effect),
                artifacts=[REPORT_PATH],
            )
            created_tasks.append(storage.get_task(task_id))
    elif existing_tasks:
        goal_id = existing_tasks[0].goal_id

    if effects_needing_tasks:
        status = TASKS_RECORDED
    elif applied_capability_effects:
        status = TASKS_ALREADY_RECORDED
    else:
        status = TASKS_NO_APPLIED_EFFECTS

    batch = storage.record_capability_activation_task_batch(
        status=status,
        source_application_id=_latest_application_id(storage, applied_capability_effects),
        goal_id=goal_id,
        applied_capability_effect_count=len(applied_capability_effects),
        task_count=len(created_tasks),
        existing_task_count=len(existing_tasks),
        activation_action_count=0,
        created_task_ids=[task.id for task in created_tasks],
        source_effect_ids=[effect.id for effect in applied_capability_effects],
        report_path=REPORT_PATH,
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_tasks_report(
            batch,
            created_tasks,
            existing_tasks,
            applied_capability_effects,
        ),
        encoding="utf-8",
    )
    return report_path, batch, created_tasks, existing_tasks, applied_capability_effects


def render_capability_activation_task_batch_line(
    batch: CapabilityActivationTaskBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"source_application={batch.source_application_id} "
        f"goal={batch.goal_id} "
        f"applied_capability_effects={batch.applied_capability_effect_count} "
        f"tasks_created={batch.task_count} "
        f"existing_activation_tasks={batch.existing_task_count} "
        f"activation_actions={batch.activation_action_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_tasks_report(
    batch: CapabilityActivationTaskBatch,
    created_tasks: list[Task],
    existing_tasks: list[Task],
    applied_capability_effects: list[Effect],
) -> str:
    lines = [
        "# Capability Activation Tasks",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- source_application: {batch.source_application_id}",
        f"- goal: {batch.goal_id}",
        f"- applied_capability_effects: {batch.applied_capability_effect_count}",
        f"- tasks_created: {batch.task_count}",
        f"- existing_activation_tasks: {batch.existing_task_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- report_path: {batch.report_path}",
        f"- created_at: {batch.created_at}",
        "",
        "## Created Activation Tasks",
        "",
    ]
    if created_tasks:
        lines.extend(_render_task_line(task) for task in created_tasks)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Activation Tasks", ""])
    if existing_tasks:
        lines.extend(_render_task_line(task) for task in existing_tasks)
    else:
        lines.append("- none")

    lines.extend(["", "## Applied Capability Effects", ""])
    if applied_capability_effects:
        lines.extend(_render_effect_line(effect) for effect in applied_capability_effects)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not enable capabilities.",
            "- Does not create legacy approval_requests rows.",
            "- Does not mutate external systems.",
            "- Does not route, schedule, retry, dispatch, run CI, or deploy.",
            "- Does not promote trust or mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _applied_capability_effects(storage: Storage) -> list[Effect]:
    return [
        effect
        for effect in storage.list_effects_with_idempotency_prefix(IDEMPOTENCY_PREFIX)
        if effect.status == "applied"
        and effect.effect_type == "operator_capability_proposal"
    ]


def _existing_activation_tasks(storage: Storage) -> list[Task]:
    return [
        task
        for task in storage.list_all_tasks()
        if task.task_type == TASK_TYPE and task.evidence.get("source_effect_id")
    ]


def _latest_application_id(
    storage: Storage,
    applied_capability_effects: list[Effect],
) -> str:
    applications = storage.list_recent_operator_approval_effect_applications(limit=1)
    if applications:
        return applications[0].id
    for effect in applied_capability_effects:
        application_id = effect.result_json.get("application_id")
        if isinstance(application_id, str) and application_id:
            return application_id
    return "none"


def _task_description(effect: Effect) -> str:
    return (
        f"Prepare activation gate for capability {effect.capability} from "
        f"applied operator approval effect {effect.id}; keep the capability "
        "disabled until evidence and explicit approval pass."
    )


def _verification_plan(effect: Effect) -> dict[str, object]:
    return {
        "type": "capability_activation_gate",
        "capability": effect.capability,
        "source_effect_id": effect.id,
        "source_application_id": effect.result_json.get("application_id", "none"),
        "activation_allowed": False,
        "required_gates": [
            "capability_specific_evidence",
            "explicit_operator_approval",
            "fresh_verification",
            "non_claim_review",
        ],
        "non_claims": [
            "does_not_enable_capability",
            "does_not_mutate_external_systems",
            "does_not_run_ci_or_deploy",
        ],
    }


def _task_evidence(effect: Effect) -> dict[str, object]:
    return {
        "source_effect_id": effect.id,
        "source_application_id": effect.result_json.get("application_id", "none"),
        "source_approval_id": effect.required_approval_id,
        "capability": effect.capability,
        "capability_enabled": False,
        "activation_actions_taken": 0,
        "external_mutations_taken": 0,
        "legacy_approval_requests_created": 0,
        "task_origin": "applied_operator_approval_effect",
    }


def _render_task_line(task: Task) -> str:
    return (
        f"- task={task.id} status={task.status} capability={task.evidence.get('capability')} "
        f"source_effect={task.evidence.get('source_effect_id')} "
        f"risk={task.risk_level} activation_allowed=false"
    )


def _render_effect_line(effect: Effect) -> str:
    return (
        f"- effect={effect.id} status={effect.status} "
        f"capability={effect.capability} target={effect.target} "
        f"source_application={effect.result_json.get('application_id', 'none')}"
    )
