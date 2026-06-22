from __future__ import annotations

from pathlib import Path

from agent_os.operator_approval_effect_proposals import IDEMPOTENCY_PREFIX
from agent_os.storage import Effect, OperatorApprovalEffectApplication, Storage, utc_now


APPLICATION_RECORDED = "operator_approval_effect_application_recorded"
APPLICATION_ALREADY_RECORDED = "operator_approval_effect_application_already_recorded"
APPLICATION_NO_PROPOSALS = "operator_approval_effect_application_no_proposals"
APPLICATION_NO_APPROVED_PROPOSALS = (
    "operator_approval_effect_application_no_approved_proposals"
)
REPORT_PATH = "docs/expansion-operator-approval-effect-application.md"


def apply_operator_approval_effects(
    root: Path,
    *,
    operator_id: str,
    selection_note: str,
    evidence_reference: str,
) -> tuple[Path, OperatorApprovalEffectApplication, list[Effect]]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    operator_effects = storage.list_effects_with_idempotency_prefix(IDEMPOTENCY_PREFIX)
    proposed_effects = [effect for effect in operator_effects if effect.status == "proposed"]
    existing_applied_effects = [
        effect for effect in operator_effects if effect.status == "applied"
    ]
    approved_request_ids = {
        request.id
        for request in storage.list_operator_approval_requests()
        if request.status == "approved"
    }
    applicable_effects = [
        effect
        for effect in proposed_effects
        if effect.required_approval_id in approved_request_ids
    ]

    if applicable_effects:
        status = APPLICATION_RECORDED
    elif existing_applied_effects and not proposed_effects:
        status = APPLICATION_ALREADY_RECORDED
    elif proposed_effects:
        status = APPLICATION_NO_APPROVED_PROPOSALS
    else:
        status = APPLICATION_NO_PROPOSALS

    applied_effect_ids = [effect.id for effect in applicable_effects]
    application = storage.record_operator_approval_effect_application(
        status=status,
        operator_id=operator_id,
        selection_note=selection_note,
        evidence_reference=evidence_reference,
        proposed_effect_count=len(proposed_effects),
        applied_effect_count=len(applicable_effects),
        existing_applied_effect_count=len(existing_applied_effects),
        external_effect_count=sum(
            1
            for effect in applicable_effects
            if effect.effect_type == "operator_external_decision"
        ),
        capability_effect_count=sum(
            1
            for effect in applicable_effects
            if effect.effect_type == "operator_capability_proposal"
        ),
        legacy_approval_request_count=0,
        activation_action_count=0,
        applied_effect_ids=applied_effect_ids,
        report_path=REPORT_PATH,
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
                    "reason": "local_application_record_only_no_external_action",
                },
                attempted_at=attempted_at,
            )
        )

    report_path = root / application.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_operator_approval_effect_application_report(
            application,
            proposed_effects,
            applied_effects,
            existing_applied_effects,
        ),
        encoding="utf-8",
    )
    return report_path, application, applied_effects


def render_operator_approval_effect_application_line(
    application: OperatorApprovalEffectApplication,
) -> str:
    return (
        f"- {application.id}: status={application.status} "
        f"operator_id={application.operator_id} "
        f"proposed_effects={application.proposed_effect_count} "
        f"effects_applied={application.applied_effect_count} "
        f"existing_applied_effects={application.existing_applied_effect_count} "
        f"external_effects={application.external_effect_count} "
        f"capability_effects={application.capability_effect_count} "
        f"activation_actions={application.activation_action_count} "
        f"legacy_approval_requests={application.legacy_approval_request_count} "
        f"report={application.report_path}"
    )


def render_operator_approval_effect_application_report(
    application: OperatorApprovalEffectApplication,
    proposed_effects: list[Effect],
    applied_effects: list[Effect],
    existing_applied_effects: list[Effect],
) -> str:
    lines = [
        "# Expansion Operator Approval Effect Application",
        "",
        f"- id: {application.id}",
        f"- status: {application.status}",
        f"- operator_id: {application.operator_id}",
        f"- selection_note: {application.selection_note}",
        f"- evidence_reference: {application.evidence_reference}",
        f"- proposed_effects: {application.proposed_effect_count}",
        f"- effects_applied: {application.applied_effect_count}",
        f"- existing_applied_effects: {application.existing_applied_effect_count}",
        f"- external_effects_applied: {application.external_effect_count}",
        f"- capability_effects_applied: {application.capability_effect_count}",
        f"- legacy_approval_requests_created: {application.legacy_approval_request_count}",
        f"- activation_actions_taken: {application.activation_action_count}",
        f"- report_path: {application.report_path}",
        f"- created_at: {application.created_at}",
        "",
        "## Applied Effects",
        "",
    ]
    if applied_effects:
        lines.extend(_render_effect_line(effect) for effect in applied_effects)
    else:
        lines.append("- none")

    lines.extend(["", "## Proposed Effects Considered", ""])
    if proposed_effects:
        lines.extend(_render_effect_line(effect) for effect in proposed_effects)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Applied Effects", ""])
    if existing_applied_effects:
        lines.extend(_render_effect_line(effect) for effect in existing_applied_effects)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not create legacy approval_requests rows.",
            "- Does not enable capabilities.",
            "- Does not promote trust, retry, schedule, route, or dispatch work.",
            "- Does not run CI or deploy.",
            "- Does not mark the active goal complete.",
            "- Does not mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def _result_payload(
    application: OperatorApprovalEffectApplication,
    effect: Effect,
    attempted_at: str,
) -> dict[str, object]:
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
        "activation_actions_taken": 0,
        "external_mutations_taken": 0,
        "legacy_approval_requests_created": 0,
        "capability_enabled": False,
        "attempted_at": attempted_at,
    }


def _render_effect_line(effect: Effect) -> str:
    return (
        f"- effect={effect.id} status={effect.status} "
        f"effect_type={effect.effect_type} capability={effect.capability} "
        f"target={effect.target} required_approval={effect.required_approval_id}"
    )
