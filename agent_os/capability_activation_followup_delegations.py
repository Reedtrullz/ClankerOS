from __future__ import annotations

from pathlib import Path

from agent_os.capability_activation_followups import FOLLOWUP_TASK_TYPE
from agent_os.subagent_delegation import (
    create_subagent_delegation,
    render_subagent_delegation_line,
)
from agent_os.storage import (
    CapabilityActivationFollowupDelegationBatch,
    Storage,
    SubagentDelegation,
    Task,
)


DELEGATIONS_RECORDED = "capability_activation_followup_delegations_recorded"
DELEGATIONS_ALREADY_RECORDED = (
    "capability_activation_followup_delegations_already_recorded"
)
DELEGATIONS_NO_FOLLOWUP_TASKS = (
    "capability_activation_followup_delegations_no_followup_tasks"
)
REPORT_PATH = "docs/capability-activation-followup-delegations.md"


def write_capability_activation_followup_delegations(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationFollowupDelegationBatch,
    list[SubagentDelegation],
    list[SubagentDelegation],
    list[Task],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    followup_tasks = _pending_followup_tasks(storage)
    existing_delegations = _existing_delegations_for_tasks(storage, followup_tasks)
    delegated_task_ids = {delegation.parent_task_id for delegation in existing_delegations}
    tasks_needing_delegations = [
        task for task in followup_tasks if task.id not in delegated_task_ids
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
    elif followup_tasks:
        status = DELEGATIONS_ALREADY_RECORDED
    else:
        status = DELEGATIONS_NO_FOLLOWUP_TASKS

    batch = storage.record_capability_activation_followup_delegation_batch(
        status=status,
        followup_task_count=len(followup_tasks),
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
        followup_task_ids=[task.id for task in followup_tasks],
        report_path=REPORT_PATH,
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_delegations_report(
            batch,
            created_delegations,
            existing_delegations,
            followup_tasks,
        ),
        encoding="utf-8",
    )
    return report_path, batch, created_delegations, existing_delegations, followup_tasks


def render_capability_activation_followup_delegation_batch_line(
    batch: CapabilityActivationFollowupDelegationBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"followup_tasks={batch.followup_task_count} "
        f"routing_decisions_created={batch.routing_decision_count} "
        f"delegations_created={batch.delegation_count} "
        f"existing_delegations={batch.existing_delegation_count} "
        f"execution_started={batch.execution_started_count} "
        f"network_actions={batch.network_action_count} "
        f"activation_actions={batch.activation_action_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_followup_delegations_report(
    batch: CapabilityActivationFollowupDelegationBatch,
    created_delegations: list[SubagentDelegation],
    existing_delegations: list[SubagentDelegation],
    followup_tasks: list[Task],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Delegations",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- followup_tasks: {batch.followup_task_count}",
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

    lines.extend(["", "## Source Follow-Up Tasks", ""])
    if followup_tasks:
        lines.extend(_render_task_line(task) for task in followup_tasks)
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
            "- Does not satisfy capability proof.",
            "- Does not mutate external systems.",
            "- Does not route, schedule, retry, dispatch, run CI, or deploy.",
            "- Does not promote trust or mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _pending_followup_tasks(storage: Storage) -> list[Task]:
    return [
        task
        for task in storage.list_all_tasks()
        if task.task_type == FOLLOWUP_TASK_TYPE and task.status == "pending"
    ]


def _existing_delegations_for_tasks(
    storage: Storage,
    followup_tasks: list[Task],
) -> list[SubagentDelegation]:
    followup_task_ids = {task.id for task in followup_tasks}
    return [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if delegation.parent_task_id in followup_task_ids
    ]


def _delegation_title(task: Task) -> str:
    capability = str(task.evidence.get("capability") or "capability")
    return f"Review {capability} follow-up evidence requirements"


def _render_task_line(task: Task) -> str:
    return (
        f"- task={task.id} status={task.status} "
        f"capability={task.evidence.get('capability')} "
        f"source_contract={task.evidence.get('source_contract_id')} "
        f"source_decision={task.evidence.get('source_decision_id')} "
        f"risk={task.risk_level} activation_allowed=false"
    )
