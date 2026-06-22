from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityActivationContract,
    CapabilityActivationDecision,
    CapabilityActivationFollowupTaskBatch,
    Storage,
    Task,
)


FOLLOWUPS_RECORDED = "capability_activation_followups_recorded"
FOLLOWUPS_ALREADY_RECORDED = "capability_activation_followups_already_recorded"
FOLLOWUPS_NO_MORE_EVIDENCE_DECISIONS = (
    "capability_activation_followups_no_more_evidence_decisions"
)
REPORT_PATH = "docs/capability-activation-followups.md"
FOLLOWUP_TASK_TYPE = "capability_activation_followup_task"


def write_capability_activation_followups(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationFollowupTaskBatch,
    list[Task],
    list[Task],
    list[CapabilityActivationContract],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    source_decision = _latest_more_evidence_decision(storage)
    eligible_contracts = _eligible_contracts(storage, source_decision)
    existing_tasks = _existing_followup_tasks(storage)
    existing_contract_ids = {
        str(task.evidence.get("source_contract_id"))
        for task in existing_tasks
        if task.evidence.get("source_contract_id")
    }
    contracts_needing_tasks = [
        contract
        for contract in eligible_contracts
        if contract.id not in existing_contract_ids
    ]

    created_tasks: list[Task] = []
    for contract in contracts_needing_tasks:
        task_id = storage.create_task(
            goal_id=contract.goal_id,
            project_id=contract.project_id,
            task_type=FOLLOWUP_TASK_TYPE,
            description=_task_description(contract),
            priority=35,
            risk_level="high",
            skill_tags=[
                "capability-activation",
                "evidence-collection",
                "operator-review",
                "local-files",
            ],
            verification_plan=_verification_plan(contract, source_decision),
            evidence=_task_evidence(contract, source_decision),
            artifacts=[REPORT_PATH],
        )
        task = storage.get_task(task_id)
        if task is not None:
            created_tasks.append(task)

    if created_tasks:
        status = FOLLOWUPS_RECORDED
    elif eligible_contracts:
        status = FOLLOWUPS_ALREADY_RECORDED
    else:
        status = FOLLOWUPS_NO_MORE_EVIDENCE_DECISIONS

    batch = storage.record_capability_activation_followup_task_batch(
        status=status,
        source_decision_id=source_decision.id if source_decision is not None else "none",
        contract_count=len(eligible_contracts),
        followup_task_count=len(created_tasks),
        existing_followup_task_count=len(existing_tasks),
        created_approval_request_count=0,
        activation_action_count=0,
        created_task_ids=[task.id for task in created_tasks],
        contract_ids=[contract.id for contract in eligible_contracts],
        report_path=REPORT_PATH,
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followups_report(
            batch,
            created_tasks,
            existing_tasks,
            eligible_contracts,
        ),
        encoding="utf-8",
    )
    return report_path, batch, created_tasks, existing_tasks, eligible_contracts


def render_capability_activation_followup_batch_line(
    batch: CapabilityActivationFollowupTaskBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"source_decision={batch.source_decision_id} "
        f"contracts_selected={batch.contract_count} "
        f"followup_tasks_created={batch.followup_task_count} "
        f"existing_followup_tasks={batch.existing_followup_task_count} "
        f"approval_requests_created={batch.created_approval_request_count} "
        f"activation_actions={batch.activation_action_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_followups_report(
    batch: CapabilityActivationFollowupTaskBatch,
    created_tasks: list[Task],
    existing_tasks: list[Task],
    contracts: list[CapabilityActivationContract],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Tasks",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- source_decision: {batch.source_decision_id}",
        f"- contracts_selected: {batch.contract_count}",
        f"- followup_tasks_created: {batch.followup_task_count}",
        f"- existing_followup_tasks: {batch.existing_followup_task_count}",
        f"- approval_requests_created: {batch.created_approval_request_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- report_path: {batch.report_path}",
        f"- created_at: {batch.created_at}",
        "",
        "## Created Follow-Up Tasks",
        "",
    ]
    if created_tasks:
        lines.extend(_render_task_line(task) for task in created_tasks)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Follow-Up Tasks", ""])
    if existing_tasks:
        lines.extend(_render_task_line(task) for task in existing_tasks)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Contracts", ""])
    if contracts:
        lines.extend(_render_contract_line(contract) for contract in contracts)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
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


def _latest_more_evidence_decision(
    storage: Storage,
) -> CapabilityActivationDecision | None:
    decisions = storage.list_recent_capability_activation_decisions(limit=50)
    for decision in decisions:
        if (
            decision.selected_action == "request_more_evidence"
            and decision.more_evidence_decision_count > 0
        ):
            return decision
    return None


def _eligible_contracts(
    storage: Storage,
    source_decision: CapabilityActivationDecision | None,
) -> list[CapabilityActivationContract]:
    if source_decision is None:
        return []
    return [
        contract
        for contract in storage.list_capability_activation_contracts()
        if contract.status == "more_evidence_requested"
        and contract.approval_status == "more_evidence_requested"
    ]


def _existing_followup_tasks(storage: Storage) -> list[Task]:
    return [
        task
        for task in storage.list_all_tasks()
        if task.task_type == FOLLOWUP_TASK_TYPE
        and task.evidence.get("source_contract_id")
    ]


def _task_description(contract: CapabilityActivationContract) -> str:
    return (
        f"Collect capability-specific evidence requested for "
        f"{contract.capability} activation contract {contract.id}; keep "
        "activation blocked until proof and explicit approval exist."
    )


def _verification_plan(
    contract: CapabilityActivationContract,
    source_decision: CapabilityActivationDecision | None,
) -> dict[str, object]:
    required_commands = contract.evidence_requirements.get("required_commands", [])
    required_artifacts = contract.evidence_requirements.get("required_artifacts", [])
    return {
        "type": "capability_activation_more_evidence_followup",
        "capability": contract.capability,
        "source_contract_id": contract.id,
        "source_decision_id": source_decision.id if source_decision else "none",
        "required_commands": required_commands,
        "required_artifacts": required_artifacts,
        "required_gates": [
            "capability_specific_evidence",
            "fresh_verification",
            "explicit_operator_approval",
            "non_claim_review",
        ],
        "activation_allowed": False,
        "non_claims": [
            "does_not_enable_capability",
            "does_not_create_approval_requests",
            "does_not_mutate_external_systems",
        ],
    }


def _task_evidence(
    contract: CapabilityActivationContract,
    source_decision: CapabilityActivationDecision | None,
) -> dict[str, object]:
    return {
        "source_contract_id": contract.id,
        "source_decision_id": source_decision.id if source_decision else "none",
        "source_effect_id": contract.source_effect_id,
        "source_application_id": contract.source_application_id,
        "source_activation_task_id": contract.task_id,
        "capability": contract.capability,
        "evidence_requirements": contract.evidence_requirements,
        "activation_allowed": False,
        "capability_enabled": False,
        "approval_requests_created": 0,
        "activation_actions_taken": 0,
        "external_mutations_taken": 0,
        "task_origin": "capability_activation_more_evidence_decision",
    }


def _render_task_line(task: Task) -> str:
    return (
        f"- task={task.id} status={task.status} "
        f"task_type={task.task_type} capability={task.evidence.get('capability')} "
        f"source_contract={task.evidence.get('source_contract_id')} "
        f"source_decision={task.evidence.get('source_decision_id')} "
        f"risk={task.risk_level} activation_allowed=false"
    )


def _render_contract_line(contract: CapabilityActivationContract) -> str:
    return (
        f"- contract={contract.id} status={contract.status} "
        f"capability={contract.capability} task={contract.task_id} "
        f"approval_status={contract.approval_status} "
        f"activation_allowed={str(contract.activation_allowed).lower()}"
    )
