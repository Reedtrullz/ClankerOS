from __future__ import annotations

from pathlib import Path

from agent_os.capability_activation_tasks import TASK_TYPE
from agent_os.storage import (
    CapabilityActivationContract,
    CapabilityActivationContractBatch,
    Storage,
    Task,
)


CONTRACTS_RECORDED = "capability_activation_contracts_recorded"
CONTRACTS_ALREADY_RECORDED = "capability_activation_contracts_already_recorded"
CONTRACTS_NO_ACTIVATION_TASKS = "capability_activation_contracts_no_activation_tasks"
REPORT_PATH = "docs/capability-activation-contracts.md"
CONTRACT_STATUS = "blocked_pending_evidence"
APPROVAL_BOUNDARY = "explicit_operator_approval_required"
APPROVAL_STATUS = "blocked_until_evidence_verified"
CAPABILITY_PROOF_COMMANDS = {
    "hosted_dashboard": "hosted-dashboard-proof-checklist",
    "remote_workers": "remote-worker-proof-checklist",
    "autonomous_scheduling": "autonomous-scheduling-proof-checklist",
    "browser_desktop_adapters": "browser-desktop-adapter-proof-checklist",
    "ci_deploy_proof": "ci-deploy-proof-checklist",
    "budget_enforcement": "budget-enforcement-proof-checklist",
    "trust_promotion": "trust-promotion-proof-checklist",
    "automatic_retries": "automatic-retry-proof-checklist",
    "real_cost_tracking": "real-cost-tracking-proof-checklist",
}


def write_capability_activation_contracts(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationContractBatch,
    list[CapabilityActivationContract],
    list[CapabilityActivationContract],
    list[Task],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    activation_tasks = _activation_tasks(storage)
    existing_contracts = storage.list_capability_activation_contracts()
    existing_contract_task_ids = {contract.task_id for contract in existing_contracts}
    tasks_needing_contracts = [
        task for task in activation_tasks if task.id not in existing_contract_task_ids
    ]

    created_contracts: list[CapabilityActivationContract] = []
    for task in tasks_needing_contracts:
        created_contracts.append(
            storage.record_capability_activation_contract(
                task_id=task.id,
                goal_id=task.goal_id,
                project_id=task.project_id,
                capability=_task_capability(task),
                source_effect_id=str(task.evidence.get("source_effect_id", "none")),
                source_application_id=str(
                    task.evidence.get("source_application_id", "none")
                ),
                evidence_requirements=_evidence_requirements(task),
                approval_boundary=APPROVAL_BOUNDARY,
                approval_status=APPROVAL_STATUS,
                required_approval_id="none",
                status=CONTRACT_STATUS,
                activation_allowed=False,
                created_approval_request_count=0,
                activation_action_count=0,
                report_path=REPORT_PATH,
            )
        )

    if tasks_needing_contracts:
        status = CONTRACTS_RECORDED
    elif activation_tasks:
        status = CONTRACTS_ALREADY_RECORDED
    else:
        status = CONTRACTS_NO_ACTIVATION_TASKS

    batch = storage.record_capability_activation_contract_batch(
        status=status,
        source_task_batch_id=_latest_task_batch_id(storage),
        activation_task_count=len(activation_tasks),
        contract_count=len(created_contracts),
        existing_contract_count=len(existing_contracts),
        created_approval_request_count=0,
        activation_action_count=0,
        created_contract_ids=[contract.id for contract in created_contracts],
        report_path=REPORT_PATH,
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_contracts_report(
            batch,
            created_contracts,
            existing_contracts,
            activation_tasks,
        ),
        encoding="utf-8",
    )
    return report_path, batch, created_contracts, existing_contracts, activation_tasks


def render_capability_activation_contract_batch_line(
    batch: CapabilityActivationContractBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"source_task_batch={batch.source_task_batch_id} "
        f"activation_tasks={batch.activation_task_count} "
        f"contracts_created={batch.contract_count} "
        f"existing_contracts={batch.existing_contract_count} "
        f"approval_requests_created={batch.created_approval_request_count} "
        f"activation_actions={batch.activation_action_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_contracts_report(
    batch: CapabilityActivationContractBatch,
    created_contracts: list[CapabilityActivationContract],
    existing_contracts: list[CapabilityActivationContract],
    activation_tasks: list[Task],
) -> str:
    lines = [
        "# Capability Activation Contracts",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- source_task_batch: {batch.source_task_batch_id}",
        f"- activation_tasks: {batch.activation_task_count}",
        f"- contracts_created: {batch.contract_count}",
        f"- existing_contracts: {batch.existing_contract_count}",
        f"- approval_requests_created: {batch.created_approval_request_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- report_path: {batch.report_path}",
        f"- created_at: {batch.created_at}",
        "",
        "## Created Contracts",
        "",
    ]
    if created_contracts:
        lines.extend(_render_contract_line(contract) for contract in created_contracts)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Contracts", ""])
    if existing_contracts:
        lines.extend(_render_contract_line(contract) for contract in existing_contracts)
    else:
        lines.append("- none")

    lines.extend(["", "## Activation Tasks", ""])
    if activation_tasks:
        lines.extend(_render_activation_task_line(task) for task in activation_tasks)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not create approval_requests rows.",
            "- Does not enable capabilities.",
            "- Does not satisfy capability evidence.",
            "- Does not mutate external systems.",
            "- Does not route, schedule, retry, dispatch, run CI, or deploy.",
            "- Does not promote trust or mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _activation_tasks(storage: Storage) -> list[Task]:
    return [
        task
        for task in storage.list_all_tasks()
        if task.task_type == TASK_TYPE and task.evidence.get("source_effect_id")
    ]


def _latest_task_batch_id(storage: Storage) -> str:
    batches = storage.list_recent_capability_activation_task_batches(limit=1)
    if batches:
        return batches[0].id
    return "none"


def _task_capability(task: Task) -> str:
    return str(task.evidence.get("capability", "unknown"))


def _evidence_requirements(task: Task) -> dict[str, object]:
    capability = _task_capability(task)
    proof_command = CAPABILITY_PROOF_COMMANDS.get(
        capability,
        f"{capability.replace('_', '-')}-proof-checklist",
    )
    proof_path = f"docs/{proof_command}.md"
    return {
        "type": "capability_activation_contract",
        "capability": capability,
        "source_task_id": task.id,
        "source_effect_id": task.evidence.get("source_effect_id", "none"),
        "source_application_id": task.evidence.get("source_application_id", "none"),
        "required_artifacts": [
            "docs/capability-activation-tasks.md",
            proof_path,
            REPORT_PATH,
        ],
        "required_commands": [
            f"python3 -m agent_os.cli {proof_command}",
            "python3 -m agent_os.cli dashboard",
            "python3 -m agent_os.cli eval-after-change --change "
            f"\"Assess {capability} activation evidence\"",
        ],
        "required_gates": [
            "capability_specific_evidence",
            "fresh_verification",
            "explicit_operator_approval",
            "non_claim_review",
            "rollback_or_disable_plan",
        ],
        "approval_boundary": APPROVAL_BOUNDARY,
        "approval_status": APPROVAL_STATUS,
        "activation_allowed": False,
        "created_approval_request_count": 0,
        "activation_action_count": 0,
        "non_claims": [
            "does_not_enable_capability",
            "does_not_create_approval_requests_yet",
            "does_not_satisfy_evidence",
            "does_not_mutate_external_systems",
            "does_not_run_ci_or_deploy",
            "does_not_promote_trust",
        ],
    }


def _render_contract_line(contract: CapabilityActivationContract) -> str:
    return (
        f"- contract={contract.id} status={contract.status} "
        f"capability={contract.capability} task={contract.task_id} "
        f"source_effect={contract.source_effect_id} "
        f"approval_boundary={contract.approval_boundary} "
        f"approval_status={contract.approval_status} "
        f"activation_allowed={str(contract.activation_allowed).lower()} "
        f"approval_requests_created={contract.created_approval_request_count}"
    )


def _render_activation_task_line(task: Task) -> str:
    return (
        f"- task={task.id} status={task.status} "
        f"capability={task.evidence.get('capability')} "
        f"source_effect={task.evidence.get('source_effect_id')} "
        f"risk={task.risk_level}"
    )
