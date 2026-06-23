from __future__ import annotations

from pathlib import Path

from agent_os.capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals import (
    EFFECT_TYPE,
    IDEMPOTENCY_PREFIX,
    render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line,
)
from agent_os.storage import (
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskBatch,
    Effect,
    Storage,
    Task,
)


TASKS_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_recorded"
)
TASKS_ALREADY_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_already_recorded"
)
TASKS_NO_APPLIED_EFFECTS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_no_applied_effects"
)
REPORT_PATH = (
    "docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md"
)
TASK_TYPE = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task"
)
GOAL_DESCRIPTION = (
    "Prepare downstream proof work from applied downstream result effect task result effect task result effect task result decision effects."
)


def write_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskBatch,
    list[Task],
    list[Task],
    list[Effect],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    applied_effects = _applied_downstream_result_effect_task_result_effect_task_result_effect_task_result_effects(
        storage
    )
    existing_tasks = _existing_downstream_tasks(storage)
    existing_task_source_effect_ids = {
        task.evidence.get("source_effect_id")
        for task in existing_tasks
        if task.evidence.get("source_effect_id")
    }
    effects_needing_tasks = [
        effect
        for effect in applied_effects
        if effect.id not in existing_task_source_effect_ids
    ]

    created_tasks: list[Task] = []
    if effects_needing_tasks:
        goal_id = storage.get_or_create_goal("bootstrap", GOAL_DESCRIPTION)
        for effect in effects_needing_tasks:
            task_id = storage.create_task(
                goal_id=goal_id,
                project_id=effect.project_id,
                task_type=TASK_TYPE,
                description=_task_description(effect),
                priority=37,
                risk_level="high",
                skill_tags=[
                    "capability-activation",
                    "followup-result",
                    "downstream-result-effect",
                    "task-result-effect",
                    "task-result-effect-application",
                    "evidence-planning",
                    "local-files",
                ],
                verification_plan=_verification_plan(effect),
                evidence=_task_evidence(effect),
                artifacts=[REPORT_PATH],
            )
            created_tasks.append(storage.get_task(task_id))

    if effects_needing_tasks:
        status = TASKS_RECORDED
    elif applied_effects:
        status = TASKS_ALREADY_RECORDED
    else:
        status = TASKS_NO_APPLIED_EFFECTS

    batch = (
        storage.record_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_batch(
            status=status,
            source_application_id=_latest_application_id(storage, applied_effects),
            applied_downstream_effect_count=len(applied_effects),
            task_count=len(created_tasks),
            existing_task_count=len(existing_tasks),
            capability_task_count=len(created_tasks),
            created_approval_request_count=0,
            activation_action_count=0,
            external_mutation_count=0,
            created_task_ids=[task.id for task in created_tasks],
            source_effect_ids=[effect.id for effect in applied_effects],
            report_path=REPORT_PATH,
        )
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_report(
            batch,
            created_tasks,
            existing_tasks,
            applied_effects,
        ),
        encoding="utf-8",
    )
    return report_path, batch, created_tasks, existing_tasks, applied_effects


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_batch_line(
    batch: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"source_application={batch.source_application_id} "
        f"applied_downstream_effects={batch.applied_downstream_effect_count} "
        f"tasks_created={batch.task_count} "
        f"existing_downstream_tasks={batch.existing_task_count} "
        f"capability_tasks_created={batch.capability_task_count} "
        f"approval_requests={batch.created_approval_request_count} "
        f"activation_actions={batch.activation_action_count} "
        f"external_mutations={batch.external_mutation_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks_report(
    batch: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskBatch,
    created_tasks: list[Task],
    existing_tasks: list[Task],
    applied_effects: list[Effect],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Tasks",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- source_application: {batch.source_application_id}",
        f"- applied_downstream_effects: {batch.applied_downstream_effect_count}",
        f"- tasks_created: {batch.task_count}",
        f"- existing_downstream_tasks: {batch.existing_task_count}",
        f"- capability_tasks_created: {batch.capability_task_count}",
        f"- approval_requests_created: {batch.created_approval_request_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- external_mutations_taken: {batch.external_mutation_count}",
        f"- report_path: {batch.report_path}",
        f"- created_at: {batch.created_at}",
        "",
        "## Created Downstream Tasks",
        "",
    ]
    if created_tasks:
        lines.extend(_render_task_line(task) for task in created_tasks)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Downstream Tasks", ""])
    if existing_tasks:
        lines.extend(_render_task_line(task) for task in existing_tasks)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Applied Downstream Result Effect Task Result Effect Task Result Effect Task Result Effects",
            "",
        ]
    )
    if applied_effects:
        lines.extend(
            render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line(
                effect
            )
            for effect in applied_effects
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not create approval_requests rows.",
            "- Does not enable capabilities.",
            "- Does not allow activation.",
            "- Does not satisfy capability proof.",
            "- Does not mutate capability activation contracts.",
            "- Does not mutate downstream result effect task result effect task result effect result records.",
            "- Does not mutate external systems.",
            "- Does not route, schedule, retry, dispatch, run CI, or deploy.",
            "- Does not promote trust or mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _applied_downstream_result_effect_task_result_effect_task_result_effect_task_result_effects(
    storage: Storage,
) -> list[Effect]:
    return [
        effect
        for effect in storage.list_effects_with_idempotency_prefix(IDEMPOTENCY_PREFIX)
        if effect.status == "applied"
        and effect.effect_type == EFFECT_TYPE
        and effect.result_json.get("selected_action") == "accept_keep_blocked"
        and effect.result_json.get("activation_allowed") is False
        and effect.result_json.get("capability_enabled") is False
        and effect.result_json.get("external_mutations_taken") == 0
    ]


def _existing_downstream_tasks(storage: Storage) -> list[Task]:
    return [
        task
        for task in storage.list_all_tasks()
        if task.task_type == TASK_TYPE and task.evidence.get("source_effect_id")
    ]


def _latest_application_id(storage: Storage, applied_effects: list[Effect]) -> str:
    applications = (
        storage.list_recent_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_applications(
            limit=1
        )
    )
    if applications:
        return applications[0].id
    for effect in applied_effects:
        application_id = effect.result_json.get("application_id")
        if isinstance(application_id, str) and application_id:
            return application_id
    return "none"


def _task_description(effect: Effect) -> str:
    return (
        f"Prepare the next downstream evidence plan for capability {effect.capability} "
        f"from applied downstream result effect task result effect task result "
        f"effect task result decision effect {effect.id}; keep activation "
        "blocked until fresh proof and explicit operator approval exist."
    )


def _verification_plan(effect: Effect) -> dict[str, object]:
    result = effect.result_json
    return {
        "type": (
            "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_downstream_task"
        ),
        "capability": effect.capability,
        "source_effect_id": effect.id,
        "source_application_id": result.get("application_id", "none"),
        "source_decision_id": result.get("source_decision_id", "none"),
        "source_downstream_result_id": result.get(
            "source_downstream_result_id",
            "none",
        ),
        "source_application_record_id": result.get("source_application_id", "none"),
        "source_application_effect_id": result.get(
            "source_application_effect_id",
            "none",
        ),
        "source_application_decision_id": result.get(
            "source_application_decision_id",
            "none",
        ),
        "source_delegation_id": result.get("source_delegation_id", "none"),
        "source_downstream_task_id": result.get("source_downstream_task_id", "none"),
        "selected_action": result.get("selected_action", "none"),
        "activation_allowed": False,
        "capability_enabled": False,
        "required_gates": [
            "next_evidence_plan",
            "fresh_verification",
            "explicit_operator_approval",
            "non_claim_review",
        ],
        "non_claims": [
            "does_not_enable_capability",
            "does_not_allow_activation",
            "does_not_satisfy_capability_proof",
            "does_not_mutate_external_systems",
            "does_not_create_approval_requests",
            "does_not_mutate_downstream_result_effect_task_result_effect_task_result_effect_result_records",
        ],
    }


def _task_evidence(effect: Effect) -> dict[str, object]:
    result = effect.result_json
    return {
        "source_effect_id": effect.id,
        "source_application_id": result.get("application_id", "none"),
        "source_decision_id": result.get("source_decision_id", "none"),
        "source_downstream_result_id": result.get(
            "source_downstream_result_id",
            "none",
        ),
        "upstream_source_decision_id": result.get("upstream_source_decision_id", "none"),
        "upstream_source_downstream_result_id": result.get(
            "upstream_source_downstream_result_id",
            "none",
        ),
        "source_application_record_id": result.get("source_application_id", "none"),
        "source_application_effect_id": result.get(
            "source_application_effect_id",
            "none",
        ),
        "source_application_decision_id": result.get(
            "source_application_decision_id",
            "none",
        ),
        "source_application_downstream_result_id": result.get(
            "source_application_downstream_result_id",
            "none",
        ),
        "source_application_delegation_id": result.get(
            "source_application_delegation_id",
            "none",
        ),
        "source_delegation_id": result.get("source_delegation_id", "none"),
        "source_downstream_task_id": result.get("source_downstream_task_id", "none"),
        "upstream_downstream_task_id": result.get("upstream_downstream_task_id", "none"),
        "source_followup_result_id": result.get("source_followup_result_id", "none"),
        "upstream_followup_effect_id": result.get(
            "upstream_followup_effect_id",
            "none",
        ),
        "source_contract_id": result.get("source_contract_id", "none"),
        "source_goal_id": result.get("source_goal_id", "none"),
        "source_project_id": result.get("source_project_id", "none"),
        "assigned_profile": result.get("assigned_profile", "none"),
        "evidence_status": result.get("evidence_status", "none"),
        "result_evidence_path": result.get("result_evidence_path", "none"),
        "capability": effect.capability,
        "selected_action": result.get("selected_action", "none"),
        "activation_allowed": False,
        "capability_enabled": False,
        "activation_actions_taken": 0,
        "approval_requests_created": 0,
        "external_mutations_taken": 0,
        "task_origin": (
            "applied_downstream_result_effect_task_result_effect_task_result_effect_task_result_decision_effect"
        ),
    }


def _render_task_line(task: Task) -> str:
    return (
        f"- task={task.id} status={task.status} "
        f"capability={task.evidence.get('capability')} "
        f"effect={task.evidence.get('source_effect_id')} "
        f"source_downstream_result={task.evidence.get('source_downstream_result_id')} "
        f"risk={task.risk_level} activation_allowed=false"
    )
