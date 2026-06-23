from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
    Storage,
)


DECISIONS_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decisions_recorded"
)
DECISIONS_ALREADY_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decisions_already_recorded"
)
DECISIONS_NO_RESULTS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decisions_no_results"
)
REPORT_PATH = (
    "docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md"
)


def decide_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_results(
    root: Path,
    *,
    operator_id: str,
    selected_action: str,
    selection_note: str,
    evidence_reference: str,
) -> tuple[
    Path,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
    list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    result_records = (
        storage.list_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_records()
    )
    already_decided_result_ids = _already_decided_result_ids(
        storage,
        result_records,
        selected_action=selected_action,
    )
    ready_records = [
        record for record in result_records if record.id not in already_decided_result_ids
    ]

    if ready_records:
        status = DECISIONS_RECORDED
    elif already_decided_result_ids:
        status = DECISIONS_ALREADY_RECORDED
    else:
        status = DECISIONS_NO_RESULTS

    decision_count = len(ready_records)
    decision = storage.record_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decision(
        status=status,
        operator_id=operator_id,
        selected_action=selected_action,
        selection_note=selection_note,
        evidence_reference=evidence_reference,
        result_record_count=len(ready_records),
        decision_count=decision_count,
        accepted_keep_blocked_decision_count=_decision_count_for_action(
            selected_action,
            "accept_keep_blocked",
            decision_count,
        ),
        more_evidence_decision_count=_decision_count_for_action(
            selected_action,
            "request_more_evidence",
            decision_count,
        ),
        deferred_decision_count=_decision_count_for_action(
            selected_action,
            "defer_review",
            decision_count,
        ),
        existing_decision_count=len(already_decided_result_ids),
        created_approval_request_count=0,
        activation_action_count=0,
        external_mutation_count=0,
        decided_result_ids=[record.id for record in ready_records],
        report_path=REPORT_PATH,
    )

    report_records = ready_records or [
        record
        for record in result_records
        if record.id in already_decided_result_ids
    ]
    report_path = root / decision.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decision_report(
            decision,
            report_records,
        ),
        encoding="utf-8",
    )
    return report_path, decision, ready_records


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decision_line(
    decision: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
) -> str:
    return (
        f"- {decision.id}: status={decision.status} "
        f"operator_id={decision.operator_id} "
        f"selected_action={decision.selected_action} "
        f"results_ready={decision.result_record_count} "
        f"decisions_recorded={decision.decision_count} "
        f"accepted_keep_blocked_decisions="
        f"{decision.accepted_keep_blocked_decision_count} "
        f"more_evidence_decisions={decision.more_evidence_decision_count} "
        f"deferred_decisions={decision.deferred_decision_count} "
        f"existing_decisions={decision.existing_decision_count} "
        f"approval_requests_created={decision.created_approval_request_count} "
        f"activation_actions={decision.activation_action_count} "
        f"external_mutations={decision.external_mutation_count} "
        f"report={decision.report_path}"
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decision_report(
    decision: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
    decided_records: list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Decisions",
        "",
        f"- id: {decision.id}",
        f"- status: {decision.status}",
        f"- operator_id: {decision.operator_id}",
        f"- selected_action: {decision.selected_action}",
        f"- selection_note: {decision.selection_note}",
        f"- evidence_reference: {decision.evidence_reference}",
        f"- results_ready: {decision.result_record_count}",
        f"- decisions_recorded: {decision.decision_count}",
        (
            "- accepted_keep_blocked_decisions: "
            f"{decision.accepted_keep_blocked_decision_count}"
        ),
        f"- more_evidence_decisions: {decision.more_evidence_decision_count}",
        f"- deferred_decisions: {decision.deferred_decision_count}",
        f"- existing_decisions: {decision.existing_decision_count}",
        f"- approval_requests_created: {decision.created_approval_request_count}",
        f"- activation_actions_taken: {decision.activation_action_count}",
        f"- external_mutations_taken: {decision.external_mutation_count}",
        f"- report_path: {decision.report_path}",
        f"- created_at: {decision.created_at}",
        "",
        "## Decided Results",
        "",
    ]
    if decided_records:
        lines.extend(_render_result_line(record) for record in decided_records)
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
            "- Does not allow activation.",
            "- Does not mutate capability activation contracts.",
            "- Does not mutate downstream result effect task result effect task result effect task result effect task result effect task result records.",
            "- Does not mutate external systems.",
            "- Does not route, schedule, retry, dispatch, run CI, or deploy.",
            "- Does not promote trust or mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _already_decided_result_ids(
    storage: Storage,
    result_records: list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord
    ],
    *,
    selected_action: str,
) -> set[str]:
    result_ids = {record.id for record in result_records}
    decided_ids: set[str] = set()
    for decision in (
        storage.list_recent_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decisions(
            limit=None,
        )
    ):
        if decision.status != DECISIONS_RECORDED:
            continue
        if (
            decision.selected_action != "accept_keep_blocked"
            and decision.selected_action != selected_action
        ):
            continue
        decided_ids.update(
            result_id
            for result_id in decision.decided_result_ids
            if result_id in result_ids
        )
    return decided_ids


def _decision_count_for_action(
    selected_action: str,
    target_action: str,
    decision_count: int,
) -> int:
    if selected_action == target_action:
        return decision_count
    return 0


def _render_result_line(
    record: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
) -> str:
    return (
        f"- result={record.id} delegation={record.delegation_id} "
        f"task={record.downstream_task_id} "
        f"source_decision={record.source_decision_id} "
        f"source_downstream_result={record.source_downstream_result_id} "
        f"source_effect={record.source_effect_id} "
        f"source_application_effect={record.source_application_effect_id} "
        f"capability={record.capability} status={record.evidence_status} "
        f"activation_allowed={record.activation_allowed} "
        f"capability_enabled={record.capability_enabled} "
        f"external_mutations={record.external_mutation_count}"
    )
