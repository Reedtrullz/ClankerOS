from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_os.capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decisions import (
    DECISIONS_RECORDED,
)
from agent_os.storage import (
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
    Effect,
    Storage,
)


PROPOSALS_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_recorded"
)
PROPOSALS_ALREADY_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_already_recorded"
)
PROPOSALS_NO_ACCEPTED_DECISIONS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_no_accepted_decisions"
)
REPORT_PATH = (
    "docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md"
)
IDEMPOTENCY_PREFIX = (
    "capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decision-effect:"
)
EFFECT_TYPE = (
    "capability_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_blocked_result_proposal"
)


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectProposalSummary:
    status: str
    accepted_decision_count: int
    accepted_result_count: int
    effect_proposal_count: int
    existing_effect_proposal_count: int
    capability_effect_proposal_count: int
    approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    report_path: str


def write_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals(
    root: Path,
) -> tuple[
    Path,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectProposalSummary,
    list[Effect],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    accepted_pairs = _accepted_decision_result_pairs(storage)
    existing_effects = _capability_followup_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decision_effects(
        storage
    )
    existing_keys = {effect.idempotency_key for effect in existing_effects}
    created_effects: list[Effect] = []

    for decision, result_record in accepted_pairs:
        idempotency_key = _idempotency_key(decision, result_record)
        if idempotency_key in existing_keys:
            continue
        created_effects.append(
            storage.record_effect(
                run_id=decision.id,
                task_id=result_record.downstream_task_id,
                project_id=result_record.project_id,
                capability=result_record.capability,
                effect_type=EFFECT_TYPE,
                idempotency_key=idempotency_key,
                target=result_record.capability,
                proposed_payload=_payload_for_result(decision, result_record),
                status="proposed",
                required_approval_id=decision.id,
                attempted_at=None,
                committed_at=None,
                evidence_path=REPORT_PATH,
                compensation_plan={
                    "required": False,
                    "reason": (
                        "proposal_only_downstream_result_effect_task_result_"
                        "effect_task_result_effect_task_result_blocked_"
                        "activation_preserved"
                    ),
                },
                result_json={
                    "activation_actions_taken": 0,
                    "approval_requests_created": 0,
                    "external_mutations_taken": 0,
                    "capability_enabled": False,
                    "activation_allowed": False,
                },
            )
        )

    accepted_decision_ids = {decision.id for decision, _record in accepted_pairs}
    summary = CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectProposalSummary(
        status=_status_for_counts(
            accepted_result_count=len(accepted_pairs),
            created_count=len(created_effects),
            existing_count=len(existing_effects),
        ),
        accepted_decision_count=len(accepted_decision_ids),
        accepted_result_count=len(accepted_pairs),
        effect_proposal_count=len(created_effects),
        existing_effect_proposal_count=len(existing_effects),
        capability_effect_proposal_count=len(created_effects),
        approval_request_count=0,
        activation_action_count=0,
        external_mutation_count=0,
        report_path=REPORT_PATH,
    )

    report_path = root / summary.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_report(
            summary,
            accepted_pairs,
            created_effects,
            existing_effects,
        ),
        encoding="utf-8",
    )
    return report_path, summary, created_effects


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line(
    effect: Effect,
) -> str:
    source_result_id = effect.proposed_payload.get(
        "source_downstream_result_id",
        "unknown",
    )
    return (
        f"- effect={effect.id} decision={effect.run_id} "
        f"result={source_result_id} status={effect.status} "
        f"effect_type={effect.effect_type} capability={effect.capability} "
        f"target={effect.target} required_approval={effect.required_approval_id} "
        f"idempotency_key={effect.idempotency_key} report={effect.evidence_path}"
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_report(
    summary: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectProposalSummary,
    accepted_pairs: list[
        tuple[
            CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
            CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
        ]
    ],
    created_effects: list[Effect],
    existing_effects: list[Effect],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals",
        "",
        f"- status: {summary.status}",
        f"- accepted_decisions: {summary.accepted_decision_count}",
        f"- accepted_results: {summary.accepted_result_count}",
        f"- effect_proposals_created: {summary.effect_proposal_count}",
        f"- existing_effect_proposals: {summary.existing_effect_proposal_count}",
        f"- capability_effect_proposals: {summary.capability_effect_proposal_count}",
        f"- approval_requests_created: {summary.approval_request_count}",
        f"- activation_actions_taken: {summary.activation_action_count}",
        f"- external_mutations_taken: {summary.external_mutation_count}",
        f"- report_path: {summary.report_path}",
        "",
        "## Created Proposed Effects",
        "",
    ]
    if created_effects:
        lines.extend(
            render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line(
                effect
            )
            for effect in created_effects
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Accepted Downstream Results", ""])
    if accepted_pairs:
        lines.extend(
            _render_accepted_result_line(decision, record)
            for decision, record in accepted_pairs
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Proposed Effects", ""])
    if existing_effects:
        lines.extend(
            render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line(
                effect
            )
            for effect in existing_effects
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
            "- Does not mutate downstream result effect task result effect task result effect task result effect task result records.",
            "- Does not mutate external systems.",
            "- Does not route, schedule, retry, dispatch, run CI, or deploy.",
            "- Does not promote trust or mark the active goal complete.",
            "",
        ]
    )
    return "\n".join(lines)


def _accepted_decision_result_pairs(
    storage: Storage,
) -> list[
    tuple[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
    ]
]:
    result_records_by_id = {
        record.id: record
        for record in storage.list_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_records()
    }
    pairs = []
    for decision in (
        storage.list_recent_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decisions(
            limit=None,
        )
    ):
        if decision.status != DECISIONS_RECORDED:
            continue
        if decision.selected_action != "accept_keep_blocked":
            continue
        for result_id in decision.decided_result_ids:
            result_record = result_records_by_id.get(result_id)
            if result_record is None:
                continue
            if result_record.activation_allowed or result_record.capability_enabled:
                continue
            if result_record.external_mutation_count != 0:
                continue
            pairs.append((decision, result_record))
    return pairs


def _capability_followup_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_decision_effects(
    storage: Storage,
) -> list[Effect]:
    return storage.list_effects_with_idempotency_prefix(IDEMPOTENCY_PREFIX)


def _status_for_counts(
    *,
    accepted_result_count: int,
    created_count: int,
    existing_count: int,
) -> str:
    if accepted_result_count == 0:
        return PROPOSALS_NO_ACCEPTED_DECISIONS
    if created_count == 0 and existing_count >= accepted_result_count:
        return PROPOSALS_ALREADY_RECORDED
    return PROPOSALS_RECORDED


def _idempotency_key(
    decision: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
    result_record: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
) -> str:
    return f"{IDEMPOTENCY_PREFIX}{decision.id}:{result_record.id}"


def _payload_for_result(
    decision: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
    result_record: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
) -> dict[str, object]:
    return {
        "source_decision_id": decision.id,
        "source_downstream_result_id": result_record.id,
        "upstream_source_decision_id": result_record.source_decision_id,
        "upstream_source_downstream_result_id": result_record.source_downstream_result_id,
        "source_application_id": result_record.source_application_id,
        "source_application_decision_id": result_record.source_application_decision_id,
        "source_application_downstream_result_id": (
            result_record.source_application_downstream_result_id
        ),
        "source_application_delegation_id": (
            result_record.source_application_delegation_id
        ),
        "source_application_effect_id": result_record.source_application_effect_id,
        "source_application_record_id": result_record.source_application_record_id,
        "source_effect_id": result_record.source_effect_id,
        "source_delegation_id": result_record.delegation_id,
        "source_downstream_task_id": result_record.downstream_task_id,
        "upstream_downstream_task_id": result_record.source_downstream_task_id,
        "source_followup_result_id": result_record.source_followup_result_id,
        "upstream_followup_effect_id": result_record.upstream_followup_effect_id,
        "source_contract_id": result_record.source_contract_id,
        "source_goal_id": result_record.goal_id,
        "source_project_id": result_record.project_id,
        "capability": result_record.capability,
        "assigned_profile": result_record.assigned_profile,
        "selected_action": decision.selected_action,
        "evidence_status": result_record.evidence_status,
        "result_summary": result_record.result_summary,
        "result_evidence_path": result_record.evidence_path,
        "activation_allowed": False,
        "capability_enabled": False,
        "approval_requests_created": 0,
        "activation_actions_taken": 0,
        "external_mutations_taken": 0,
    }


def _render_accepted_result_line(
    decision: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultDecision,
    record: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultRecord,
) -> str:
    return (
        f"- decision={decision.id} result={record.id} "
        f"delegation={record.delegation_id} task={record.downstream_task_id} "
        f"source_application={record.source_application_id} "
        f"source_application_decision={record.source_application_decision_id} "
        f"source_application_downstream_result="
        f"{record.source_application_downstream_result_id} "
        f"source_effect={record.source_effect_id} "
        f"source_application_effect={record.source_application_effect_id} "
        f"upstream_decision={record.source_decision_id} "
        f"upstream_result={record.source_downstream_result_id} "
        f"capability={record.capability} status={record.evidence_status} "
        f"activation_allowed={record.activation_allowed} "
        f"capability_enabled={record.capability_enabled} "
        f"external_mutations={record.external_mutation_count}"
    )
