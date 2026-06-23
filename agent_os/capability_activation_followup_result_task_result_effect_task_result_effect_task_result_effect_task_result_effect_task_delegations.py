from __future__ import annotations

from pathlib import Path

from agent_os.capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks import (
    TASK_TYPE,
)
from agent_os.storage import (
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskDelegationBatch,
    Storage,
    SubagentDelegation,
    Task,
)
from agent_os.subagent_delegation import (
    create_subagent_delegation,
    render_subagent_delegation_line,
)


DELEGATIONS_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations_recorded"
)
DELEGATIONS_ALREADY_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations_already_recorded"
)
DELEGATIONS_NO_DOWNSTREAM_TASKS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations_no_downstream_tasks"
)
REPORT_PATH = (
    "docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md"
)


def write_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskDelegationBatch,
    list[SubagentDelegation],
    list[SubagentDelegation],
    list[Task],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    downstream_tasks = _pending_downstream_tasks(storage)
    existing_delegations = _existing_delegations_for_tasks(storage, downstream_tasks)
    delegated_task_ids = {delegation.parent_task_id for delegation in existing_delegations}
    tasks_needing_delegations = [
        task for task in downstream_tasks if task.id not in delegated_task_ids
    ]

    created_delegations: list[SubagentDelegation] = []
    for task in tasks_needing_delegations:
        created_delegations.append(
            create_subagent_delegation(
                root,
                storage,
                task_id=task.id,
                title=_delegation_title(task),
            )
        )

    if created_delegations:
        status = DELEGATIONS_RECORDED
    elif downstream_tasks:
        status = DELEGATIONS_ALREADY_RECORDED
    else:
        status = DELEGATIONS_NO_DOWNSTREAM_TASKS

    batch = storage.record_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegation_batch(
        status=status,
        downstream_task_count=len(downstream_tasks),
        routing_decision_count=len(created_delegations),
        delegation_count=len(created_delegations),
        existing_delegation_count=len(existing_delegations),
        execution_started_count=sum(
            1
            for delegation in [*created_delegations, *existing_delegations]
            if delegation.started_at is not None
        ),
        network_action_count=0,
        external_mutation_count=0,
        activation_action_count=0,
        created_routing_decision_ids=[
            delegation.routing_decision_id
            for delegation in created_delegations
            if delegation.routing_decision_id
        ],
        created_delegation_ids=[delegation.id for delegation in created_delegations],
        downstream_task_ids=[task.id for task in downstream_tasks],
        report_path=REPORT_PATH,
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations_report(
            batch,
            created_delegations,
            existing_delegations,
            downstream_tasks,
        ),
        encoding="utf-8",
    )
    return (
        report_path,
        batch,
        created_delegations,
        existing_delegations,
        downstream_tasks,
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegation_batch_line(
    batch: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskDelegationBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"downstream_tasks={batch.downstream_task_count} "
        f"routing_decisions_created={batch.routing_decision_count} "
        f"delegations_created={batch.delegation_count} "
        f"existing_delegations={batch.existing_delegation_count} "
        f"execution_started={batch.execution_started_count} "
        f"network_actions={batch.network_action_count} "
        f"activation_actions={batch.activation_action_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations_report(
    batch: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskDelegationBatch,
    created_delegations: list[SubagentDelegation],
    existing_delegations: list[SubagentDelegation],
    downstream_tasks: list[Task],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Delegations",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- downstream_tasks: {batch.downstream_task_count}",
        f"- routing_decisions_created: {batch.routing_decision_count}",
        f"- delegations_created: {batch.delegation_count}",
        f"- existing_delegations: {batch.existing_delegation_count}",
        f"- execution_started: {batch.execution_started_count}",
        f"- network_actions_taken: {batch.network_action_count}",
        f"- external_mutations_taken: {batch.external_mutation_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- report_path: {batch.report_path}",
        f"- created_at: {batch.created_at}",
        "",
        "## Created Delegations",
        "",
    ]
    if created_delegations:
        lines.extend(
            f"- {render_subagent_delegation_line(delegation)}"
            for delegation in created_delegations
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Delegations", ""])
    if existing_delegations:
        lines.extend(
            f"- {render_subagent_delegation_line(delegation)}"
            for delegation in existing_delegations
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Source Downstream Tasks", ""])
    if downstream_tasks:
        lines.extend(_render_task_line(task) for task in downstream_tasks)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not start subagents.",
            "- Does not call model providers.",
            "- Does not create approval_requests rows.",
            "- Does not enable capabilities.",
            "- Does not allow activation.",
            "- Does not satisfy capability proof.",
            "- Does not mutate capability activation contracts.",
            "- Does not mutate downstream result effect task result effect task result effect task result records.",
            "- Does not mutate external systems.",
            "- Does not dispatch, run CI, deploy, retry, or promote trust.",
            "- Does not mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _pending_downstream_tasks(storage: Storage) -> list[Task]:
    return [
        task
        for task in storage.list_all_tasks()
        if task.task_type == TASK_TYPE and task.status == "pending"
    ]


def _existing_delegations_for_tasks(
    storage: Storage,
    downstream_tasks: list[Task],
) -> list[SubagentDelegation]:
    downstream_task_ids = {task.id for task in downstream_tasks}
    return [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if delegation.parent_task_id in downstream_task_ids
    ]


def _delegation_title(task: Task) -> str:
    capability = str(task.evidence.get("capability") or "capability")
    return (
        "Plan next downstream result effect task result effect task result "
        f"effect task result effect proof evidence for {capability}"
    )


def _render_task_line(task: Task) -> str:
    return (
        f"- task={task.id} status={task.status} "
        f"capability={task.evidence.get('capability')} "
        f"source_effect={task.evidence.get('source_effect_id')} "
        f"source_downstream_result={task.evidence.get('source_downstream_result_id')} "
        f"source_application_effect={task.evidence.get('source_application_effect_id')} "
        f"source_application_delegation={task.evidence.get('source_application_delegation_id')} "
        f"source_contract={task.evidence.get('source_contract_id')} "
        f"risk={task.risk_level} activation_allowed=false"
    )
