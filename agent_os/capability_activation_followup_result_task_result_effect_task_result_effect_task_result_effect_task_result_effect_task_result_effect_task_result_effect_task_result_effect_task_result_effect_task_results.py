from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agent_os.capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_tasks import (
    TASK_TYPE,
)
from agent_os.storage import (
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultBatch,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
    Storage,
    SubagentDelegation,
    Task,
)


RESULTS_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results_recorded"
)
RESULTS_ALREADY_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results_already_recorded"
)
RESULTS_NO_COMPLETED_DELEGATIONS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results_no_completed_delegations"
)
RESULTS_MISSING_RESULT_ARTIFACTS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results_missing_result_artifacts"
)
REPORT_PATH = (
    "docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md"
)


def write_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultBatch,
    list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ],
    list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ],
    list[SubagentDelegation],
    list[SubagentDelegation],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    downstream_tasks_by_id = {
        task.id: task for task in storage.list_all_tasks() if task.task_type == TASK_TYPE
    }
    completed_delegations = _completed_downstream_delegations(
        storage,
        downstream_tasks_by_id,
    )

    created_records: list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ] = []
    existing_records: list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ] = []
    missing_result_artifact_delegations: list[SubagentDelegation] = []
    for delegation in completed_delegations:
        existing = _existing_record_for_delegation(storage, delegation)
        if existing is not None:
            existing_records.append(existing)
            continue

        task = downstream_tasks_by_id[delegation.parent_task_id]
        result_artifact = _read_result_artifact(delegation)
        if not _has_structured_result_output(result_artifact):
            missing_result_artifact_delegations.append(delegation)
            continue

        result_payload = _result_payload(delegation, task, result_artifact)
        evidence_path = (
            root
            / "docs"
            / "capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results"
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
            storage.record_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result(
                delegation_id=delegation.id,
                downstream_task_id=delegation.parent_task_id,
                source_application_id=str(
                    task.evidence.get("source_application_id", "")
                ),
                source_decision_id=str(task.evidence.get("source_decision_id", "")),
                source_downstream_result_id=str(
                    task.evidence.get("source_downstream_result_id", "")
                ),
                source_effect_id=str(task.evidence.get("source_effect_id", "")),
                source_application_effect_id=str(
                    task.evidence.get("source_application_effect_id", "")
                ),
                source_application_record_id=str(
                    task.evidence.get("source_application_record_id", "")
                ),
                source_application_decision_id=str(
                    task.evidence.get("source_application_decision_id", "")
                ),
                source_application_downstream_result_id=str(
                    task.evidence.get("source_application_downstream_result_id", "")
                ),
                source_application_delegation_id=str(
                    task.evidence.get("source_application_delegation_id", "")
                ),
                source_downstream_task_id=str(
                    task.evidence.get("source_downstream_task_id", "")
                ),
                source_followup_result_id=str(
                    task.evidence.get("source_followup_result_id", "")
                ),
                upstream_followup_effect_id=str(
                    task.evidence.get("upstream_followup_effect_id", "")
                ),
                source_contract_id=str(task.evidence.get("source_contract_id", "")),
                goal_id=delegation.parent_goal_id,
                project_id=task.project_id,
                capability=str(task.evidence.get("capability", "")),
                assigned_profile=delegation.assigned_profile,
                evidence_status="next_evidence_plan_recorded",
                result_summary=delegation.result_summary or "",
                evidence_path=str(evidence_path),
                result_json=result_payload,
                idempotency_key=_idempotency_key(delegation),
                activation_allowed=False,
                capability_enabled=False,
                created_approval_request_count=0,
                activation_action_count=0,
                external_mutation_count=0,
            )
        )

    if created_records:
        status = RESULTS_RECORDED
    elif missing_result_artifact_delegations:
        status = RESULTS_MISSING_RESULT_ARTIFACTS
    elif completed_delegations:
        status = RESULTS_ALREADY_RECORDED
    else:
        status = RESULTS_NO_COMPLETED_DELEGATIONS

    batch = (
        storage.record_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_batch(
            status=status,
            completed_delegation_count=len(completed_delegations),
            result_record_count=len(created_records),
            existing_result_record_count=len(existing_records),
            created_approval_request_count=0,
            activation_action_count=0,
            external_mutation_count=0,
            created_result_ids=[record.id for record in created_records],
            completed_delegation_ids=[
                delegation.id for delegation in completed_delegations
            ],
            report_path=REPORT_PATH,
        )
    )

    report_path = root / batch.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results_report(
            batch,
            created_records,
            existing_records,
            missing_result_artifact_delegations,
            completed_delegations,
        ),
        encoding="utf-8",
    )
    return (
        report_path,
        batch,
        created_records,
        existing_records,
        missing_result_artifact_delegations,
        completed_delegations,
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_batch_line(
    batch: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultBatch,
) -> str:
    return (
        f"- {batch.id}: status={batch.status} "
        f"completed_delegations={batch.completed_delegation_count} "
        f"result_records_created={batch.result_record_count} "
        f"existing_result_records={batch.existing_result_record_count} "
        f"approval_requests_created={batch.created_approval_request_count} "
        f"activation_actions={batch.activation_action_count} "
        f"external_mutations={batch.external_mutation_count} "
        f"report={batch.report_path}"
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results_report(
    batch: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultBatch,
    created_records: list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ],
    existing_records: list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ],
    missing_result_artifact_delegations: list[SubagentDelegation],
    completed_delegations: list[SubagentDelegation],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Results",
        "",
        f"- id: {batch.id}",
        f"- status: {batch.status}",
        f"- completed_delegations: {batch.completed_delegation_count}",
        f"- result_records_created: {batch.result_record_count}",
        f"- existing_result_records: {batch.existing_result_record_count}",
        f"- approval_requests_created: {batch.created_approval_request_count}",
        f"- activation_actions_taken: {batch.activation_action_count}",
        f"- external_mutations_taken: {batch.external_mutation_count}",
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

    lines.extend(["", "## Missing Result Artifacts", ""])
    if missing_result_artifact_delegations:
        lines.extend(
            _render_delegation_line(delegation)
            for delegation in missing_result_artifact_delegations
        )
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
            "- Does not mutate capability activation contracts.",
            "- Does not mutate downstream result effect task result effect task result effect task result effect task result effect task result effect task result effect task result effect task result records.",
            "- Does not mutate external systems.",
            "- Does not dispatch, run CI, deploy, retry, or promote trust.",
            "- Does not mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _completed_downstream_delegations(
    storage: Storage,
    downstream_tasks_by_id: dict[str, Task],
) -> list[SubagentDelegation]:
    downstream_task_ids = set(downstream_tasks_by_id)
    return [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if delegation.parent_task_id in downstream_task_ids
        and delegation.status == "completed"
        and delegation.category == "evidence_review"
        and delegation.expected_output_schema == "evidence_review"
    ]


def _read_result_artifact(delegation: SubagentDelegation) -> dict[str, Any] | None:
    artifact_path = Path(delegation.result_artifact_path)
    if not artifact_path.exists():
        return None
    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(artifact, dict):
        return None
    return artifact


def _has_structured_result_output(result_artifact: dict[str, Any] | None) -> bool:
    if result_artifact is None:
        return False
    structured_output = result_artifact.get("structured_output")
    return isinstance(structured_output, dict) and bool(structured_output)


def _existing_record_for_delegation(
    storage: Storage,
    delegation: SubagentDelegation,
) -> (
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    | None
):
    return (
        storage.get_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_by_idempotency_key(
            _idempotency_key(delegation),
        )
        or storage.get_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_by_idempotency_key(
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
        "downstream_task_id": delegation.parent_task_id,
        "source_application_id": task.evidence.get("source_application_id"),
        "source_decision_id": task.evidence.get("source_decision_id"),
        "source_downstream_result_id": task.evidence.get(
            "source_downstream_result_id"
        ),
        "source_effect_id": task.evidence.get("source_effect_id"),
        "source_application_effect_id": task.evidence.get(
            "source_application_effect_id"
        ),
        "source_application_record_id": task.evidence.get(
            "source_application_record_id"
        ),
        "source_application_decision_id": task.evidence.get(
            "source_application_decision_id"
        ),
        "source_application_downstream_result_id": task.evidence.get(
            "source_application_downstream_result_id"
        ),
        "source_application_delegation_id": task.evidence.get(
            "source_application_delegation_id"
        ),
        "source_delegation_id": task.evidence.get("source_delegation_id"),
        "source_downstream_task_id": task.evidence.get("source_downstream_task_id"),
        "upstream_downstream_task_id": task.evidence.get(
            "upstream_downstream_task_id"
        ),
        "source_followup_result_id": task.evidence.get("source_followup_result_id"),
        "upstream_followup_effect_id": task.evidence.get(
            "upstream_followup_effect_id"
        ),
        "upstream_source_decision_id": task.evidence.get(
            "upstream_source_decision_id"
        ),
        "upstream_source_downstream_result_id": task.evidence.get(
            "upstream_source_downstream_result_id"
        ),
        "source_contract_id": task.evidence.get("source_contract_id"),
        "source_goal_id": task.evidence.get("source_goal_id"),
        "source_project_id": task.evidence.get("source_project_id"),
        "goal_id": delegation.parent_goal_id,
        "project_id": task.project_id,
        "capability": task.evidence.get("capability"),
        "assigned_profile": delegation.assigned_profile,
        "result_summary": delegation.result_summary,
        "evidence_status": "next_evidence_plan_recorded",
        "result_evidence_path": task.evidence.get("result_evidence_path"),
        "activation_allowed": False,
        "capability_enabled": False,
        "approval_requests_created": 0,
        "activation_actions_taken": 0,
        "external_mutations_taken": 0,
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
        "source_verification_plan": task.verification_plan,
        "non_claims": [
            "No subagent was started by this ingestion command.",
            "No model provider was called by this ingestion command.",
            "No approval request was created.",
            "Capability activation remains blocked.",
            "Capability proof is not satisfied by this result record.",
            "No external system was mutated by this ingestion command.",
        ],
    }


def _idempotency_key(delegation: SubagentDelegation) -> str:
    return (
        "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result:"
        f"{delegation.id}"
    )


def _legacy_idempotency_key(delegation: SubagentDelegation) -> str:
    return f"{delegation.id}:{delegation.result_artifact_path}"


def _render_result_record_line(
    record: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
) -> str:
    return (
        f"- result={record.id} delegation={record.delegation_id} "
        f"task={record.downstream_task_id} "
        f"source_downstream_result={record.source_downstream_result_id} "
        f"source_application_effect={record.source_application_effect_id} "
        f"source_effect={record.source_effect_id} capability={record.capability} "
        f"status={record.evidence_status} "
        f"activation_allowed={str(record.activation_allowed).lower()} "
        f"capability_enabled={str(record.capability_enabled).lower()} "
        f"external_mutations={record.external_mutation_count} "
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
