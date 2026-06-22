from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_os.operator_approval_request_decisions import DECISIONS_RECORDED
from agent_os.storage import Effect, OperatorApprovalRequest, OperatorApprovalRequestDecision, Storage


PROPOSALS_RECORDED = "operator_approval_effect_proposals_recorded"
PROPOSALS_ALREADY_RECORDED = "operator_approval_effect_proposals_already_recorded"
PROPOSALS_NO_APPROVED_DECISIONS = (
    "operator_approval_effect_proposals_no_approved_decisions"
)
PROPOSALS_DECISION_MISSING = "operator_approval_effect_proposals_decision_missing"
REPORT_PATH = "docs/expansion-operator-approval-effect-proposals.md"
IDEMPOTENCY_PREFIX = "operator-approval-effect:"


@dataclass(frozen=True)
class OperatorApprovalEffectProposalSummary:
    status: str
    source_decision_id: str
    source_draft_id: str
    approved_operator_request_count: int
    effect_proposal_count: int
    existing_effect_proposal_count: int
    external_effect_proposal_count: int
    capability_effect_proposal_count: int
    legacy_approval_request_count: int
    activation_action_count: int
    report_path: str


def write_operator_approval_effect_proposals(
    root: Path,
) -> tuple[Path, OperatorApprovalEffectProposalSummary, list[Effect]]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    decision = _latest_recorded_approval_decision(storage)
    approved_requests: list[OperatorApprovalRequest] = []
    created_effects: list[Effect] = []
    existing_effects: list[Effect] = []

    if decision is None:
        summary = OperatorApprovalEffectProposalSummary(
            status=PROPOSALS_DECISION_MISSING,
            source_decision_id="none",
            source_draft_id="none",
            approved_operator_request_count=0,
            effect_proposal_count=0,
            existing_effect_proposal_count=0,
            external_effect_proposal_count=0,
            capability_effect_proposal_count=0,
            legacy_approval_request_count=0,
            activation_action_count=0,
            report_path=REPORT_PATH,
        )
    else:
        approved_requests = _approved_requests_for_decision(storage, decision)
        existing_effects = _operator_approval_effects(storage)
        existing_keys = {effect.idempotency_key for effect in existing_effects}
        for request in approved_requests:
            idempotency_key = f"{IDEMPOTENCY_PREFIX}{request.id}"
            if idempotency_key in existing_keys:
                continue
            created_effects.append(
                storage.record_effect(
                    run_id=decision.id,
                    task_id="none",
                    project_id="bootstrap",
                    capability=_capability_for_request(request),
                    effect_type=_effect_type_for_request(request),
                    idempotency_key=idempotency_key,
                    target=request.capability_key or request.subject_key,
                    proposed_payload=_payload_for_request(decision, request),
                    status="proposed",
                    required_approval_id=request.id,
                    attempted_at=None,
                    committed_at=None,
                    evidence_path=REPORT_PATH,
                    compensation_plan={
                        "required": False,
                        "reason": "proposal_only_no_activation_action_taken",
                    },
                    result_json={
                        "activation_actions_taken": 0,
                        "legacy_approval_requests_created": 0,
                    },
                )
            )
        status = _status_for_counts(
            approved_count=len(approved_requests),
            created_count=len(created_effects),
            existing_count=len(existing_effects),
        )
        summary = OperatorApprovalEffectProposalSummary(
            status=status,
            source_decision_id=decision.id,
            source_draft_id=decision.source_draft_id,
            approved_operator_request_count=len(approved_requests),
            effect_proposal_count=len(created_effects),
            existing_effect_proposal_count=len(existing_effects),
            external_effect_proposal_count=sum(
                1 for effect in created_effects if effect.effect_type == "operator_external_decision"
            ),
            capability_effect_proposal_count=sum(
                1
                for effect in created_effects
                if effect.effect_type == "operator_capability_proposal"
            ),
            legacy_approval_request_count=0,
            activation_action_count=0,
            report_path=REPORT_PATH,
        )

    report_path = root / summary.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_operator_approval_effect_proposals_report(
            summary,
            approved_requests,
            created_effects,
            existing_effects,
        ),
        encoding="utf-8",
    )
    return report_path, summary, created_effects


def render_operator_approval_effect_proposal_line(effect: Effect) -> str:
    return (
        f"- {effect.id}: status={effect.status} "
        f"effect_type={effect.effect_type} capability={effect.capability} "
        f"target={effect.target} required_approval={effect.required_approval_id} "
        f"idempotency_key={effect.idempotency_key} report={effect.evidence_path}"
    )


def render_operator_approval_effect_proposals_report(
    summary: OperatorApprovalEffectProposalSummary,
    approved_requests: list[OperatorApprovalRequest],
    created_effects: list[Effect],
    existing_effects: list[Effect],
) -> str:
    lines = [
        "# Expansion Operator Approval Effect Proposals",
        "",
        f"- status: {summary.status}",
        f"- source_decision: {summary.source_decision_id}",
        f"- source_draft: {summary.source_draft_id}",
        f"- approved_operator_requests: {summary.approved_operator_request_count}",
        f"- effect_proposals_created: {summary.effect_proposal_count}",
        f"- existing_effect_proposals: {summary.existing_effect_proposal_count}",
        f"- external_effect_proposals: {summary.external_effect_proposal_count}",
        f"- capability_effect_proposals: {summary.capability_effect_proposal_count}",
        f"- legacy_approval_requests_created: {summary.legacy_approval_request_count}",
        f"- activation_actions_taken: {summary.activation_action_count}",
        f"- report_path: {summary.report_path}",
        "",
        "## Created Proposed Effects",
        "",
    ]
    if created_effects:
        lines.extend(render_operator_approval_effect_proposal_line(effect) for effect in created_effects)
    else:
        lines.append("- none")

    lines.extend(["", "## Approved Operator Requests", ""])
    if approved_requests:
        lines.extend(_render_approved_request_line(request) for request in approved_requests)
    else:
        lines.append("- none")

    lines.extend(["", "## Existing Proposed Effects", ""])
    if existing_effects:
        lines.extend(render_operator_approval_effect_proposal_line(effect) for effect in existing_effects)
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


def _latest_recorded_approval_decision(
    storage: Storage,
) -> OperatorApprovalRequestDecision | None:
    for decision in storage.list_recent_operator_approval_request_decisions(limit=20):
        if decision.status == DECISIONS_RECORDED:
            return decision
    return None


def _approved_requests_for_decision(
    storage: Storage,
    decision: OperatorApprovalRequestDecision,
) -> list[OperatorApprovalRequest]:
    requests = storage.list_operator_approval_requests(
        source_draft_id=decision.source_draft_id,
    )
    decision_request_ids = set(decision.decided_request_ids)
    return [
        request
        for request in requests
        if request.status == "approved"
        and (not decision_request_ids or request.id in decision_request_ids)
    ]


def _operator_approval_effects(storage: Storage) -> list[Effect]:
    return storage.list_effects_with_idempotency_prefix(IDEMPOTENCY_PREFIX)


def _status_for_counts(
    *,
    approved_count: int,
    created_count: int,
    existing_count: int,
) -> str:
    if approved_count == 0:
        return PROPOSALS_NO_APPROVED_DECISIONS
    if created_count == 0 and existing_count >= approved_count:
        return PROPOSALS_ALREADY_RECORDED
    return PROPOSALS_RECORDED


def _capability_for_request(request: OperatorApprovalRequest) -> str:
    return request.capability_key or request.subject_type


def _effect_type_for_request(request: OperatorApprovalRequest) -> str:
    if request.subject_type == "capability_approval":
        return "operator_capability_proposal"
    return "operator_external_decision"


def _payload_for_request(
    decision: OperatorApprovalRequestDecision,
    request: OperatorApprovalRequest,
) -> dict[str, object]:
    return {
        "operator_request_id": request.id,
        "source_decision_id": decision.id,
        "source_draft_id": request.source_draft_id,
        "subject_type": request.subject_type,
        "subject_key": request.subject_key,
        "request_kind": request.request_kind,
        "capability_key": request.capability_key,
        "approval_boundary": request.approval_boundary,
        "decision_note": request.decision_note,
        "activation_actions_taken": 0,
    }


def _render_approved_request_line(request: OperatorApprovalRequest) -> str:
    return (
        f"- request={request.id} subject_type={request.subject_type} "
        f"subject_key={request.subject_key} request_kind={request.request_kind} "
        f"capability={request.capability_key or request.subject_type} "
        f"status={request.status} evidence_path={request.evidence_path}"
    )
