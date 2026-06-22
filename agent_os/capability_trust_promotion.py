from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityPromotionDecisionLedger,
    CapabilityTrustPromotionAudit,
    Storage,
)


PROMOTION_DECISION_LEDGER_MISSING = "promotion_decision_ledger_missing"
TRUST_PROMOTION_BLOCKED = "trust_promotion_blocked"
OPERATOR_TRUST_REVIEW_REQUIRED = "operator_trust_review_required"
NO_TRUST_PROMOTION_CANDIDATES = "no_trust_promotion_candidates"
KEEP_TRUST_UNPROMOTED = "keep_trust_unpromoted"
MANUAL_TRUST_REVIEW_REQUIRED = "manual_trust_review_required"
TRUST_BLOCKED = "blocked_until_promotion_decision_and_operator_approval"
TRUST_REVIEW_READY = "ready_for_operator_trust_review"
DEFER_PROMOTION = "defer_promotion"
MANUAL_OPERATOR_REVIEW_REQUIRED = "manual_operator_review_required"
NO_EFFECT = "none"
REPORT_PATH = "docs/capability-trust-promotion-audit.md"


def write_capability_trust_promotion_audit(
    root: Path,
) -> tuple[Path, CapabilityTrustPromotionAudit]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    ledgers = storage.list_recent_capability_promotion_decision_ledgers(limit=1)
    source_ledger = ledgers[0] if ledgers else None
    audit = _audit_from_latest_ledger(
        storage=storage,
        source_ledger=source_ledger,
        report_path=REPORT_PATH,
    )
    report_path = root / audit.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_trust_promotion_audit_report(
            audit,
            source_ledger,
        ),
        encoding="utf-8",
    )
    return report_path, audit


def render_capability_trust_promotion_audit_report(
    audit: CapabilityTrustPromotionAudit,
    source_ledger: CapabilityPromotionDecisionLedger | None,
) -> str:
    lines = [
        "# Capability Trust Promotion Audit",
        "",
        f"- id: {audit.id}",
        f"- status: {audit.status}",
        f"- source_ledger_id: {audit.source_ledger_id or 'none'}",
        f"- source_ledger_status: {audit.source_ledger_status}",
        f"- capability_count: {audit.capability_count}",
        f"- audits: {audit.audit_count}",
        f"- blocked_trust_promotions: {audit.blocked_trust_promotion_count}",
        f"- operator_reviews_required: {audit.operator_review_required_count}",
        f"- deferred_promotions: {audit.deferred_promotion_count}",
        f"- missing_evidence: {audit.missing_evidence_count}",
        f"- approvals_required: {audit.approval_required_count}",
        f"- boundaries: {audit.boundary_count}",
        f"- recommended_commands: {format_recommended_commands(audit.recommended_commands)}",
        f"- report_path: {audit.report_path}",
        f"- created_at: {audit.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {audit.reason}",
        "",
        "## Trust Promotion Audit",
        "",
    ]
    if audit.audit_items:
        lines.extend(render_audit_item_line(item) for item in audit.audit_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Promotion Decision Ledger", ""])
    if source_ledger is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_ledger.id}",
                f"- status: {source_ledger.status}",
                f"- decisions: {source_ledger.decision_count}",
                f"- deferred_promotions: {source_ledger.deferred_promotion_count}",
                f"- operator_decisions_required: {source_ledger.operator_decision_required_count}",
                f"- missing_evidence: {source_ledger.missing_evidence_count}",
                f"- approvals_required: {source_ledger.approval_required_count}",
                f"- report: {source_ledger.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local trust promotion audit.",
            "- Does not create promotion decision ledgers as a side effect.",
            "- Does not create promotion gate checklists as a side effect.",
            "- Does not create evidence collection plans as a side effect.",
            "- Does not create approval boundary matrices as a side effect.",
            "- Does not create proof gap indexes as a side effect.",
            "- Does not create readiness reviews as a side effect.",
            "- Does not create capability ledgers as a side effect.",
            "- Does not collect evidence automatically.",
            "- Does not approve capabilities automatically.",
            "- Does not promote capabilities automatically.",
            "- Does not promote trust automatically.",
            "- Does not generate proof artifacts automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not retry or replay work.",
            "- Does not change routing or claims.",
            "- Does not track real spend or mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_capability_trust_promotion_audit_line(
    audit: CapabilityTrustPromotionAudit,
) -> str:
    return (
        f"- {audit.id}: status={audit.status} "
        f"source_ledger={audit.source_ledger_id or 'none'} "
        f"source_status={audit.source_ledger_status} "
        f"audits={audit.audit_count} "
        f"blocked_trust_promotions={audit.blocked_trust_promotion_count} "
        f"operator_reviews_required={audit.operator_review_required_count} "
        f"deferred_promotions={audit.deferred_promotion_count} "
        f"missing_evidence={audit.missing_evidence_count} "
        f"approvals_required={audit.approval_required_count} "
        f"boundaries={audit.boundary_count} "
        f"recommended_commands={format_recommended_commands(audit.recommended_commands)} "
        f"report={audit.report_path}"
    )


def render_audit_item_line(item: dict[str, str]) -> str:
    return (
        f"- {item['capability']}: "
        f"recommended_trust_action={item['recommended_trust_action']} "
        f"trust_promotion_state={item['trust_promotion_state']} "
        f"source_decision={item['source_decision']} "
        f"source_decision_state={item['source_decision_state']} "
        f"evidence_state={item['evidence_state']} "
        f"approval_state={item['approval_state']} "
        f"approval_boundary={item['approval_boundary']} "
        f"trust_effect={item['trust_effect']} "
        f"routing_effect={item['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _audit_from_latest_ledger(
    *,
    storage: Storage,
    source_ledger: CapabilityPromotionDecisionLedger | None,
    report_path: str,
) -> CapabilityTrustPromotionAudit:
    if source_ledger is None:
        return storage.record_capability_trust_promotion_audit(
            status=PROMOTION_DECISION_LEDGER_MISSING,
            source_ledger_id=None,
            source_ledger_status="none",
            capability_count=0,
            audit_count=0,
            blocked_trust_promotion_count=0,
            operator_review_required_count=0,
            deferred_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["capability-promotion-decision-ledger"],
            reason="No capability promotion decision ledger exists yet.",
            audit_items=[],
            report_path=report_path,
        )

    if (
        source_ledger.status != "operator_decision_required"
        and not source_ledger.decision_items
        and source_ledger.recommended_commands
    ):
        return storage.record_capability_trust_promotion_audit(
            status=PROMOTION_DECISION_LEDGER_MISSING,
            source_ledger_id=source_ledger.id,
            source_ledger_status=source_ledger.status,
            capability_count=source_ledger.capability_count,
            audit_count=0,
            blocked_trust_promotion_count=0,
            operator_review_required_count=0,
            deferred_promotion_count=source_ledger.deferred_promotion_count,
            missing_evidence_count=source_ledger.missing_evidence_count,
            approval_required_count=source_ledger.approval_required_count,
            boundary_count=source_ledger.boundary_count,
            recommended_commands=source_ledger.recommended_commands,
            reason=(
                "Latest capability promotion decision ledger is incomplete; "
                "run the recommended upstream command before auditing trust promotion."
            ),
            audit_items=[],
            report_path=report_path,
        )

    audit_items = [
        _audit_item_from_decision_item(item)
        for item in source_ledger.decision_items
    ]
    blocked_trust_promotion_count = sum(
        1
        for item in audit_items
        if item["recommended_trust_action"] == KEEP_TRUST_UNPROMOTED
    )
    operator_review_required_count = sum(
        1
        for item in audit_items
        if item["recommended_trust_action"] == MANUAL_TRUST_REVIEW_REQUIRED
    )
    if blocked_trust_promotion_count:
        status = TRUST_PROMOTION_BLOCKED
        reason = (
            "Trust promotion remains blocked until promotion decisions, required "
            "evidence, and operator approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_TRUST_REVIEW_REQUIRED
        reason = (
            "Promotion decisions are ready for manual trust review; no trust or "
            "routing state changes were applied."
        )
    else:
        status = NO_TRUST_PROMOTION_CANDIDATES
        reason = "No trust promotion audit rows were needed from the latest ledger."

    return storage.record_capability_trust_promotion_audit(
        status=status,
        source_ledger_id=source_ledger.id,
        source_ledger_status=source_ledger.status,
        capability_count=source_ledger.capability_count,
        audit_count=len(audit_items),
        blocked_trust_promotion_count=blocked_trust_promotion_count,
        operator_review_required_count=operator_review_required_count,
        deferred_promotion_count=source_ledger.deferred_promotion_count,
        missing_evidence_count=source_ledger.missing_evidence_count,
        approval_required_count=source_ledger.approval_required_count,
        boundary_count=source_ledger.boundary_count,
        recommended_commands=[],
        reason=reason,
        audit_items=audit_items,
        report_path=report_path,
    )


def _audit_item_from_decision_item(item: dict[str, str]) -> dict[str, str]:
    trust_blocked = item["recommended_decision"] == DEFER_PROMOTION
    return {
        "capability": item["capability"],
        "recommended_trust_action": (
            KEEP_TRUST_UNPROMOTED if trust_blocked else MANUAL_TRUST_REVIEW_REQUIRED
        ),
        "trust_promotion_state": (
            TRUST_BLOCKED if trust_blocked else TRUST_REVIEW_READY
        ),
        "source_decision": item["recommended_decision"],
        "source_decision_state": item["decision_state"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "trust_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }
