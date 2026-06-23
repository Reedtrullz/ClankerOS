from __future__ import annotations

from pathlib import Path

from agent_os.capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals import (
    EFFECT_TYPE,
    IDEMPOTENCY_PREFIX,
    render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line,
)
from agent_os.storage import (
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectApplication,
    Effect,
    Storage,
    utc_now,
)


APPLICATION_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_recorded"
)
APPLICATION_ALREADY_RECORDED = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_already_recorded"
)
APPLICATION_NO_PROPOSALS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_no_proposals"
)
APPLICATION_NO_APPLICABLE_PROPOSALS = (
    "capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_no_applicable_proposals"
)
REPORT_PATH = (
    "docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md"
)


def apply_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effects(
    root: Path,
    *,
    operator_id: str,
    selection_note: str,
    evidence_reference: str,
) -> tuple[
    Path,
    CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectApplication,
    list[Effect],
]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    effects = storage.list_effects_with_idempotency_prefix(IDEMPOTENCY_PREFIX)
    proposed_effects = [effect for effect in effects if effect.status == "proposed"]
    existing_applied_effects = [
        effect for effect in effects if effect.status == "applied"
    ]
    applicable_effects = [
        effect for effect in proposed_effects if _is_applicable_effect(effect)
    ]

    if applicable_effects:
        status = APPLICATION_RECORDED
    elif existing_applied_effects and not proposed_effects:
        status = APPLICATION_ALREADY_RECORDED
    elif proposed_effects:
        status = APPLICATION_NO_APPLICABLE_PROPOSALS
    else:
        status = APPLICATION_NO_PROPOSALS

    application = (
        storage.record_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application(
            status=status,
            operator_id=operator_id,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            proposed_effect_count=len(proposed_effects),
            applied_effect_count=len(applicable_effects),
            existing_applied_effect_count=len(existing_applied_effects),
            capability_effect_count=len(applicable_effects),
            approval_request_count=0,
            activation_action_count=0,
            external_mutation_count=0,
            applied_effect_ids=[effect.id for effect in applicable_effects],
            report_path=REPORT_PATH,
        )
    )

    applied_effects: list[Effect] = []
    attempted_at = utc_now()
    for effect in applicable_effects:
        applied_effects.append(
            storage.mark_effect_applied(
                effect.id,
                result_json=_result_payload(application, effect, attempted_at),
                evidence_path=REPORT_PATH,
                compensation_plan={
                    "required": False,
                    "reason": (
                        "local_application_record_only_downstream_result_effect_task_result_effect_task_result_effect_task_result_effect_blocked_activation_preserved"
                    ),
                },
                attempted_at=attempted_at,
            )
        )

    report_path = root / application.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_report(
            application,
            proposed_effects,
            applied_effects,
            existing_applied_effects,
        ),
        encoding="utf-8",
    )
    return report_path, application, applied_effects


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_line(
    application: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectApplication,
) -> str:
    return (
        f"- {application.id}: status={application.status} "
        f"operator_id={application.operator_id} "
        f"proposed_effects={application.proposed_effect_count} "
        f"effects_applied={application.applied_effect_count} "
        f"existing_applied_effects={application.existing_applied_effect_count} "
        f"capability_effects={application.capability_effect_count} "
        f"approval_requests={application.approval_request_count} "
        f"activation_actions={application.activation_action_count} "
        f"external_mutations={application.external_mutation_count} "
        f"report={application.report_path}"
    )


def render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_application_report(
    application: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectApplication,
    proposed_effects: list[Effect],
    applied_effects: list[Effect],
    existing_applied_effects: list[Effect],
) -> str:
    lines = [
        "# Capability Activation Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Application",
        "",
        f"- id: {application.id}",
        f"- status: {application.status}",
        f"- operator_id: {application.operator_id}",
        f"- selection_note: {application.selection_note}",
        f"- evidence_reference: {application.evidence_reference}",
        f"- proposed_effects: {application.proposed_effect_count}",
        f"- effects_applied: {application.applied_effect_count}",
        f"- existing_applied_effects: {application.existing_applied_effect_count}",
        f"- capability_effects_applied: {application.capability_effect_count}",
        f"- approval_requests_created: {application.approval_request_count}",
        f"- activation_actions_taken: {application.activation_action_count}",
        f"- external_mutations_taken: {application.external_mutation_count}",
        f"- report_path: {application.report_path}",
        f"- created_at: {application.created_at}",
        "",
        "## Applied Effects",
        "",
    ]
    if applied_effects:
        lines.extend(
            render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line(
                effect
            )
            for effect in applied_effects
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Proposed Effects Considered", ""])
    if proposed_effects:
        lines.extend(
            render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line(
                effect
            )
            for effect in proposed_effects
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Applied Effects", ""])
    if existing_applied_effects:
        lines.extend(
            render_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposal_line(
                effect
            )
            for effect in existing_applied_effects
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


def _is_applicable_effect(effect: Effect) -> bool:
    payload = effect.proposed_payload
    return (
        effect.effect_type == EFFECT_TYPE
        and payload.get("selected_action") == "accept_keep_blocked"
        and payload.get("activation_allowed") is False
        and payload.get("capability_enabled") is False
        and payload.get("external_mutations_taken") == 0
    )


def _result_payload(
    application: CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectTaskResultEffectApplication,
    effect: Effect,
    attempted_at: str,
) -> dict[str, object]:
    payload = effect.proposed_payload
    return {
        "status": "applied",
        "application_id": application.id,
        "application_status": "recorded_local_only",
        "effect_id": effect.id,
        "effect_type": effect.effect_type,
        "capability": effect.capability,
        "target": effect.target,
        "required_approval_id": effect.required_approval_id,
        "operator_id": application.operator_id,
        "selection_note": application.selection_note,
        "evidence_reference": application.evidence_reference,
        "source_decision_id": payload.get("source_decision_id"),
        "source_downstream_result_id": payload.get(
            "source_downstream_result_id"
        ),
        "upstream_source_decision_id": payload.get("upstream_source_decision_id"),
        "upstream_source_downstream_result_id": payload.get(
            "upstream_source_downstream_result_id"
        ),
        "source_application_id": payload.get("source_application_id"),
        "source_application_decision_id": payload.get(
            "source_application_decision_id"
        ),
        "source_application_downstream_result_id": payload.get(
            "source_application_downstream_result_id"
        ),
        "source_application_delegation_id": payload.get(
            "source_application_delegation_id"
        ),
        "source_application_effect_id": payload.get(
            "source_application_effect_id"
        ),
        "source_application_record_id": payload.get(
            "source_application_record_id"
        ),
        "source_effect_id": payload.get("source_effect_id"),
        "source_delegation_id": payload.get("source_delegation_id"),
        "source_downstream_task_id": payload.get("source_downstream_task_id"),
        "upstream_downstream_task_id": payload.get("upstream_downstream_task_id"),
        "source_followup_result_id": payload.get("source_followup_result_id"),
        "upstream_followup_effect_id": payload.get("upstream_followup_effect_id"),
        "source_contract_id": payload.get("source_contract_id"),
        "source_goal_id": payload.get("source_goal_id"),
        "source_project_id": payload.get("source_project_id"),
        "assigned_profile": payload.get("assigned_profile"),
        "selected_action": payload.get("selected_action"),
        "evidence_status": payload.get("evidence_status"),
        "result_evidence_path": payload.get("result_evidence_path"),
        "activation_allowed": False,
        "capability_enabled": False,
        "approval_requests_created": 0,
        "activation_actions_taken": 0,
        "external_mutations_taken": 0,
        "attempted_at": attempted_at,
    }
