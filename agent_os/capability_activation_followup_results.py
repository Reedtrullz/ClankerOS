from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agent_os.capability_activation_followups import FOLLOWUP_TASK_TYPE
from agent_os.storage import (
    CapabilityActivationFollowupResultBatch,
    CapabilityActivationFollowupResultRecord,
    Storage,
    SubagentDelegation,
    Task,
)


RESULTS_RECORDED = "capability_activation_followup_results_recorded"
RESULTS_ALREADY_RECORDED = "capability_activation_followup_results_already_recorded"
RESULTS_NO_COMPLETED_DELEGATIONS = (
    "capability_activation_followup_results_no_completed_delegations"
)
REPORT_PATH = "docs/capability-activation-followup-results.md"


def write_capability_activation_followup_results(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationFollowupResultBatch,
    list[CapabilityActivationFollowupResultRecord],
    list[CapabilityActivationFollowupResultRecord],
    list[SubagentDelegation],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    followup_tasks_by_id = {
        task.id: task
        for task in storage.list_all_tasks()
        if task.task_type == FOLLOWUP_TASK_TYPE
    }
    completed_delegations = _completed_followup_delegations(
        storage,
        followup_tasks_by_id,
    )

    created_records: list[CapabilityActivationFollowupResultRecord] = []
    existing_records: list[CapabilityActivationFollowupResultRecord] = []
    for delegation in completed_delegations:
        idempotency_key = _idempotency_key(delegation)
        existing = _existing_record_for_delegation(
            storage,
            delegation,
        )
        if existing is not None:
            existing_records.append(existing)
            continue

        task = followup_tasks_by_id[delegation.parent_task_id]
        result_artifact = _read_result_artifact(delegation)
        result_payload = _result_payload(
            delegation,
            task,
            result_artifact,
        )
        evidence_path = (
            root
            / "docs"
            / "capability-activation-followup-results"
            / (
                f"{delegation.id}-"
                f"{_slug(task.evidence.get('capability', 'capability'))}.json"
            )
        )
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(
            json.dumps(result_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        created_records.append(
            storage.record_capability_activation_followup_result(
                delegation_id=delegation.id,
                followup_task_id=delegation.parent_task_id,
                contract_id=str(task.evidence.get("source_contract_id", "")),
                decision_id=str(task.evidence.get("source_decision_id", "")),
                goal_id=delegation.parent_goal_id,
                project_id=str(task.project_id),
                capability=str(task.evidence.get("capability", "")),
                assigned_profile=delegation.assigned_profile,
                evidence_status="reviewed_missing_proof",
                result_summary=delegation.result_summary or "",
                evidence_path=str(evidence_path),
                result_json=result_payload,
                idempotency_key=idempotency_key,
                activation_allowed=False,
                capability_enabled=False,
                created_approval_request_count=0,
                activation_action_count=0,
            )
        )

    if created_records:
        status = RESULTS_RECORDED
    elif completed_delegations:
        status = RESULTS_ALREADY_RECORDED
    else:
        status = RESULTS_NO_COMPLETED_DELEGATIONS

    batch = storage.record_capability_activation_followup_result_batch(
        status=status,
        completed_delegation_count=len(completed_delegations),
        result_record_count=len(created_records),
        existing_result_record_count=len(existing_records),
        created_approval_request_count=0,
        activation_action_count=0,
        created_result_ids=[record.id for record in created_records],
        completed_delegation_ids=[delegation.id for delegation in completed_delegations],
        report_path=REPORT_PATH,
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_results_report(
            batch,
            created_records,
            existing_records,
            completed_delegations,
        ),
        encoding="utf-8",
    )
    return report_path, batch, created_records, existing_records, completed_delegations


def render_capability_activation_followup_result_batch_line(
    batch: CapabilityActivationFollowupResultBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"completed_delegations={batch.completed_delegation_count} "
        f"result_records_created={batch.result_record_count} "
        f"existing_result_records={batch.existing_result_record_count} "
        f"approval_requests_created={batch.created_approval_request_count} "
        f"activation_actions={batch.activation_action_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_followup_results_report(
    batch: CapabilityActivationFollowupResultBatch,
    created_records: list[CapabilityActivationFollowupResultRecord],
    existing_records: list[CapabilityActivationFollowupResultRecord],
    completed_delegations: list[SubagentDelegation],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Results",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- completed_delegations: {batch.completed_delegation_count}",
        f"- result_records_created: {batch.result_record_count}",
        f"- existing_result_records: {batch.existing_result_record_count}",
        f"- approval_requests_created: {batch.created_approval_request_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- report_path: {batch.report_path}",
        f"- created_at: {batch.created_at}",
        "",
        "## Created Result Records",
        "",
    ]
    if created_records:
        lines.extend(_render_result_record_line(record) for record in created_records)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Result Records", ""])
    if existing_records:
        lines.extend(_render_result_record_line(record) for record in existing_records)
    else:
        lines.append("- none")

    lines.extend(["", "## Completed Delegations", ""])
    if completed_delegations:
        lines.extend(
            _render_delegation_line(delegation)
            for delegation in completed_delegations
        )
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
            "- Does not allow activation.",
            "- Does not mutate external systems.",
            "- Does not route, schedule, retry, dispatch, run CI, or deploy.",
            "- Does not promote trust or mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _completed_followup_delegations(
    storage: Storage,
    followup_tasks_by_id: dict[str, Task],
) -> list[SubagentDelegation]:
    followup_task_ids = set(followup_tasks_by_id)
    return [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if delegation.parent_task_id in followup_task_ids
        and delegation.status == "completed"
        and delegation.category == "evidence_review"
        and delegation.expected_output_schema == "evidence_review"
    ]


def _read_result_artifact(delegation: SubagentDelegation) -> dict[str, Any]:
    artifact_path = Path(delegation.result_artifact_path)
    if not artifact_path.exists():
        return {}
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def _existing_record_for_delegation(
    storage: Storage,
    delegation: SubagentDelegation,
) -> CapabilityActivationFollowupResultRecord | None:
    return (
        storage.get_capability_activation_followup_result_by_idempotency_key(
            _idempotency_key(delegation),
        )
        or storage.get_capability_activation_followup_result_by_idempotency_key(
            _legacy_idempotency_key(delegation),
        )
    )


def _result_payload(
    delegation: SubagentDelegation,
    task: Task,
    result_artifact: dict[str, Any],
) -> dict[str, object]:
    return {
        "delegation_id": delegation.id,
        "followup_task_id": delegation.parent_task_id,
        "contract_id": task.evidence.get("source_contract_id"),
        "decision_id": task.evidence.get("source_decision_id"),
        "goal_id": delegation.parent_goal_id,
        "project_id": task.project_id,
        "capability": task.evidence.get("capability"),
        "assigned_profile": delegation.assigned_profile,
        "result_summary": delegation.result_summary,
        "evidence_status": "reviewed_missing_proof",
        "activation_allowed": False,
        "capability_enabled": False,
        "approval_requests_created": 0,
        "activation_actions_taken": 0,
        "delegation_result": {
            "result_summary": result_artifact.get("result_summary")
            or delegation.result_summary,
            "structured_output": result_artifact.get("structured_output", {}),
            "recorded_by": result_artifact.get("recorded_by"),
            "completed_at": result_artifact.get("completed_at")
            or delegation.completed_at,
            "artifact_path": delegation.result_artifact_path,
        },
        "source_task_evidence": task.evidence,
        "non_claims": [
            "No subagent was started by this ingestion command.",
            "No model provider was called by this ingestion command.",
            "No approval request was created.",
            "Capability activation remains blocked.",
            "Capability proof is not satisfied by this result record.",
        ],
    }


def _idempotency_key(delegation: SubagentDelegation) -> str:
    return f"capability_activation_followup_result:{delegation.id}"


def _legacy_idempotency_key(delegation: SubagentDelegation) -> str:
    return f"{delegation.id}:{delegation.result_artifact_path}"


def _render_result_record_line(
    record: CapabilityActivationFollowupResultRecord,
) -> str:
    return (
        f"- result={record.id} delegation={record.delegation_id} "
        f"task={record.followup_task_id} contract={record.contract_id} "
        f"capability={record.capability} status={record.evidence_status} "
        f"activation_allowed={str(record.activation_allowed).lower()} "
        f"capability_enabled={str(record.capability_enabled).lower()} "
        f"artifact={record.evidence_path}"
    )


def _render_delegation_line(delegation: SubagentDelegation) -> str:
    return (
        f"- delegation={delegation.id} task={delegation.parent_task_id} "
        f"profile={delegation.assigned_profile} category={delegation.category} "
        f"schema={delegation.expected_output_schema} status={delegation.status} "
        f"artifact={delegation.result_artifact_path}"
    )


def _slug(value: object) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", str(value).strip().lower()).strip("-")
    return slug or "capability"
