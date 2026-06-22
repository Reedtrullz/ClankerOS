from __future__ import annotations

import json
import re
from pathlib import Path

from agent_os.storage import (
    CapabilityActivationContract,
    CapabilityActivationDecision,
    CapabilityActivationEvidenceBatch,
    CapabilityActivationEvidenceRecord,
    Storage,
    utc_now,
)


EVIDENCE_RECORDED = "capability_activation_evidence_recorded"
EVIDENCE_ALREADY_RECORDED = "capability_activation_evidence_already_recorded"
EVIDENCE_NO_CONTRACTS = "capability_activation_evidence_no_contracts"
EVIDENCE_REPORT_PATH = "docs/capability-activation-evidence.md"
DECISIONS_RECORDED = "capability_activation_decisions_recorded"
DECISIONS_ALREADY_RECORDED = "capability_activation_decisions_already_recorded"
DECISIONS_NO_EVIDENCE = "capability_activation_decisions_no_evidence"
DECISION_REPORT_PATH = "docs/capability-activation-decisions.md"
DECIDED_CONTRACT_STATUSES = {
    "approved_pending_activation",
    "deferred_by_operator",
    "more_evidence_requested",
}


def record_capability_activation_evidence(
    root: Path,
    *,
    contract_id: str | None,
    all_contracts: bool,
    evidence_kind: str,
    evidence_reference: str,
    verification_command: str,
    verification_status: str,
    recorded_by: str,
    summary: str,
) -> tuple[
    Path,
    CapabilityActivationEvidenceBatch,
    list[CapabilityActivationEvidenceRecord],
    list[CapabilityActivationEvidenceRecord],
    list[CapabilityActivationContract],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    selected_contracts = _selected_contracts(storage, contract_id, all_contracts)
    created_records: list[CapabilityActivationEvidenceRecord] = []
    existing_records: list[CapabilityActivationEvidenceRecord] = []

    for contract in selected_contracts:
        idempotency_key = _evidence_idempotency_key(
            contract,
            evidence_kind,
            evidence_reference,
            verification_command,
            verification_status,
        )
        existing = storage.get_capability_activation_evidence_by_idempotency_key(
            idempotency_key,
        )
        if existing is not None:
            existing_records.append(existing)
            continue

        evidence_path = (
            root
            / "docs"
            / "capability-activation-evidence"
            / f"{contract.id}-{_slug(evidence_kind)}-{_slug(verification_status)}.json"
        )
        result_json = _evidence_payload(
            contract,
            evidence_kind=evidence_kind,
            evidence_reference=evidence_reference,
            verification_command=verification_command,
            verification_status=verification_status,
            recorded_by=recorded_by,
            summary=summary,
        )
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(
            json.dumps(result_json, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        created_records.append(
            storage.record_capability_activation_evidence(
                contract_id=contract.id,
                task_id=contract.task_id,
                goal_id=contract.goal_id,
                project_id=contract.project_id,
                capability=contract.capability,
                source_effect_id=contract.source_effect_id,
                evidence_kind=evidence_kind,
                evidence_reference=evidence_reference,
                verification_command=verification_command,
                verification_status=verification_status,
                recorded_by=recorded_by,
                summary=summary,
                status="evidence_recorded",
                evidence_path=str(evidence_path),
                result_json=result_json,
                idempotency_key=idempotency_key,
                created_approval_request_count=0,
                activation_action_count=0,
            )
        )

    if created_records:
        status = EVIDENCE_RECORDED
    elif selected_contracts:
        status = EVIDENCE_ALREADY_RECORDED
    else:
        status = EVIDENCE_NO_CONTRACTS

    batch = storage.record_capability_activation_evidence_batch(
        status=status,
        contract_count=len(selected_contracts),
        evidence_record_count=len(created_records),
        existing_evidence_count=len(existing_records),
        created_approval_request_count=0,
        activation_action_count=0,
        created_evidence_ids=[record.id for record in created_records],
        report_path=EVIDENCE_REPORT_PATH,
    )
    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_evidence_report(
            batch,
            created_records,
            existing_records,
            selected_contracts,
        ),
        encoding="utf-8",
    )
    return report_path, batch, created_records, existing_records, selected_contracts


def decide_capability_activation_contracts(
    root: Path,
    *,
    operator_id: str,
    selected_action: str,
    selection_note: str,
    evidence_reference: str,
) -> tuple[Path, CapabilityActivationDecision, list[CapabilityActivationContract]]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    evidence_contract_ids = {
        record.contract_id
        for record in storage.list_capability_activation_evidence_records()
    }
    contracts = storage.list_capability_activation_contracts()
    ready_contracts = [
        contract
        for contract in contracts
        if contract.id in evidence_contract_ids
        and contract.status not in DECIDED_CONTRACT_STATUSES
    ]
    existing_decision_count = sum(
        1 for contract in contracts if contract.status in DECIDED_CONTRACT_STATUSES
    )

    if ready_contracts:
        status = DECISIONS_RECORDED
    elif existing_decision_count:
        status = DECISIONS_ALREADY_RECORDED
    else:
        status = DECISIONS_NO_EVIDENCE

    decision_count = len(ready_contracts)
    decision = storage.record_capability_activation_decision(
        status=status,
        operator_id=operator_id,
        selected_action=selected_action,
        selection_note=selection_note,
        evidence_reference=evidence_reference,
        contract_count=len(ready_contracts),
        decision_count=decision_count,
        approved_decision_count=_decision_count_for_action(
            selected_action,
            "approve",
            decision_count,
        ),
        deferred_decision_count=_decision_count_for_action(
            selected_action,
            "defer",
            decision_count,
        ),
        more_evidence_decision_count=_decision_count_for_action(
            selected_action,
            "request_more_evidence",
            decision_count,
        ),
        existing_decision_count=existing_decision_count,
        created_approval_request_count=0,
        activation_action_count=0,
        decided_contract_ids=[contract.id for contract in ready_contracts],
        report_path=DECISION_REPORT_PATH,
    )
    decided_contracts = [
        storage.get_capability_activation_contract(contract.id) or contract
        for contract in ready_contracts
    ]
    report_path = root / decision.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_decision_report(decision, decided_contracts),
        encoding="utf-8",
    )
    return report_path, decision, decided_contracts


def render_capability_activation_evidence_batch_line(
    batch: CapabilityActivationEvidenceBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"contracts_selected={batch.contract_count} "
        f"evidence_records_created={batch.evidence_record_count} "
        f"existing_evidence_records={batch.existing_evidence_count} "
        f"approval_requests_created={batch.created_approval_request_count} "
        f"activation_actions={batch.activation_action_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_decision_line(
    decision: CapabilityActivationDecision,
) -> str:
    return (
        f"- {decision.id}: status={decision.status} "
        f"operator_id={decision.operator_id} "
        f"selected_action={decision.selected_action} "
        f"contracts_ready={decision.contract_count} "
        f"decisions_recorded={decision.decision_count} "
        f"approved_decisions={decision.approved_decision_count} "
        f"deferred_decisions={decision.deferred_decision_count} "
        f"more_evidence_decisions={decision.more_evidence_decision_count} "
        f"existing_decisions={decision.existing_decision_count} "
        f"approval_requests_created={decision.created_approval_request_count} "
        f"activation_actions={decision.activation_action_count} "
        f"report={decision.report_path}"
    )


def render_capability_activation_evidence_report(
    batch: CapabilityActivationEvidenceBatch,
    created_records: list[CapabilityActivationEvidenceRecord],
    existing_records: list[CapabilityActivationEvidenceRecord],
    contracts: list[CapabilityActivationContract],
) -> str:
    lines = [
        "# Capability Activation Evidence",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- contracts_selected: {batch.contract_count}",
        f"- evidence_records_created: {batch.evidence_record_count}",
        f"- existing_evidence_records: {batch.existing_evidence_count}",
        f"- approval_requests_created: {batch.created_approval_request_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- report_path: {batch.report_path}",
        f"- created_at: {batch.created_at}",
        "",
        "## Created Evidence Records",
        "",
    ]
    if created_records:
        lines.extend(_render_evidence_record_line(record) for record in created_records)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Evidence Records", ""])
    if existing_records:
        lines.extend(_render_evidence_record_line(record) for record in existing_records)
    else:
        lines.append("- none")

    lines.extend(["", "## Selected Contracts", ""])
    if contracts:
        lines.extend(_render_contract_line(contract) for contract in contracts)
    else:
        lines.append("- none")

    lines.extend(_non_claim_lines())
    return "\n".join(lines)


def render_capability_activation_decision_report(
    decision: CapabilityActivationDecision,
    decided_contracts: list[CapabilityActivationContract],
) -> str:
    lines = [
        "# Capability Activation Decisions",
        "",
        f"- id: {decision.id}",
        f"- status: {decision.status}",
        f"- operator_id: {decision.operator_id}",
        f"- selected_action: {decision.selected_action}",
        f"- selection_note: {decision.selection_note}",
        f"- evidence_reference: {decision.evidence_reference}",
        f"- contracts_ready: {decision.contract_count}",
        f"- decisions_recorded: {decision.decision_count}",
        f"- approved_decisions: {decision.approved_decision_count}",
        f"- deferred_decisions: {decision.deferred_decision_count}",
        f"- more_evidence_decisions: {decision.more_evidence_decision_count}",
        f"- existing_decisions: {decision.existing_decision_count}",
        f"- approval_requests_created: {decision.created_approval_request_count}",
        f"- activation_actions_taken: {decision.activation_action_count}",
        f"- report_path: {decision.report_path}",
        f"- created_at: {decision.created_at}",
        "",
        "## Decided Contracts",
        "",
    ]
    if decided_contracts:
        lines.extend(_render_contract_line(contract) for contract in decided_contracts)
    else:
        lines.append("- none")

    lines.extend(_non_claim_lines())
    return "\n".join(lines)


def _selected_contracts(
    storage: Storage,
    contract_id: str | None,
    all_contracts: bool,
) -> list[CapabilityActivationContract]:
    if all_contracts:
        return storage.list_capability_activation_contracts()
    if contract_id is None:
        return []
    contract = storage.get_capability_activation_contract(contract_id)
    if contract is None:
        return []
    return [contract]


def _evidence_idempotency_key(
    contract: CapabilityActivationContract,
    evidence_kind: str,
    evidence_reference: str,
    verification_command: str,
    verification_status: str,
) -> str:
    return ":".join(
        [
            contract.id,
            evidence_kind.strip(),
            evidence_reference.strip(),
            verification_command.strip(),
            verification_status.strip().lower(),
        ]
    )


def _evidence_payload(
    contract: CapabilityActivationContract,
    *,
    evidence_kind: str,
    evidence_reference: str,
    verification_command: str,
    verification_status: str,
    recorded_by: str,
    summary: str,
) -> dict[str, object]:
    return {
        "status": "evidence_recorded",
        "contract_id": contract.id,
        "task_id": contract.task_id,
        "goal_id": contract.goal_id,
        "project_id": contract.project_id,
        "capability": contract.capability,
        "source_effect_id": contract.source_effect_id,
        "evidence_kind": evidence_kind,
        "evidence_reference": evidence_reference,
        "verification_command": verification_command,
        "verification_status": verification_status,
        "recorded_by": recorded_by,
        "summary": summary,
        "network_actions_taken": 0,
        "created_approval_request_count": 0,
        "activation_actions_taken": 0,
        "activation_allowed": False,
        "created_at": utc_now(),
        "non_claims": [
            "Does not create approval_requests rows.",
            "Does not enable capabilities.",
            "Does not satisfy capability evidence by itself.",
            "Does not mutate external systems.",
        ],
    }


def _render_evidence_record_line(record: CapabilityActivationEvidenceRecord) -> str:
    return (
        f"- evidence={record.id} status={record.status} "
        f"contract={record.contract_id} capability={record.capability} "
        f"evidence_kind={record.evidence_kind} "
        f"verification_status={record.verification_status} "
        f"approval_requests_created={record.created_approval_request_count} "
        f"activation_actions={record.activation_action_count} "
        f"path={record.evidence_path}"
    )


def _render_contract_line(contract: CapabilityActivationContract) -> str:
    return (
        f"- contract={contract.id} status={contract.status} "
        f"capability={contract.capability} task={contract.task_id} "
        f"approval_status={contract.approval_status} "
        f"activation_allowed={str(contract.activation_allowed).lower()}"
    )


def _decision_count_for_action(
    selected_action: str,
    expected_action: str,
    decision_count: int,
) -> int:
    return decision_count if selected_action == expected_action else 0


def _non_claim_lines() -> list[str]:
    return [
        "",
        "## Non-Claims",
        "",
        "- Does not create approval_requests rows.",
        "- Does not enable capabilities.",
        "- Does not run CI or deploy.",
        "- Does not mutate external systems.",
        "- Does not promote trust or mark the active goal complete.",
        "",
    ]


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return slug or "unknown"
