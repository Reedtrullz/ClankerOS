from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityAutomaticRetryAudit,
    CapabilityTrustPromotionAudit,
    Storage,
)


TRUST_PROMOTION_AUDIT_MISSING = "trust_promotion_audit_missing"
AUTOMATIC_RETRY_BLOCKED = "automatic_retry_blocked"
OPERATOR_RETRY_REVIEW_REQUIRED = "operator_retry_review_required"
NO_AUTOMATIC_RETRY_CANDIDATES = "no_automatic_retry_candidates"
KEEP_RETRY_DISABLED = "keep_retry_disabled"
MANUAL_RETRY_REVIEW_REQUIRED = "manual_retry_review_required"
KEEP_TRUST_UNPROMOTED = "keep_trust_unpromoted"
RETRY_BLOCKED = "blocked_until_trust_promotion_and_operator_approval"
RETRY_REVIEW_READY = "ready_for_operator_retry_review"
NO_EFFECT = "none"
REPORT_PATH = "docs/capability-automatic-retry-audit.md"


def write_capability_automatic_retry_audit(
    root: Path,
) -> tuple[Path, CapabilityAutomaticRetryAudit]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    trust_audits = storage.list_recent_capability_trust_promotion_audits(limit=1)
    source_audit = trust_audits[0] if trust_audits else None
    audit = _audit_from_latest_trust_audit(
        storage=storage,
        source_audit=source_audit,
        report_path=REPORT_PATH,
    )
    report_path = root / audit.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_automatic_retry_audit_report(
            audit,
            source_audit,
        ),
        encoding="utf-8",
    )
    return report_path, audit


def render_capability_automatic_retry_audit_report(
    audit: CapabilityAutomaticRetryAudit,
    source_audit: CapabilityTrustPromotionAudit | None,
) -> str:
    lines = [
        "# Capability Automatic Retry Audit",
        "",
        f"- id: {audit.id}",
        f"- status: {audit.status}",
        f"- source_audit_id: {audit.source_audit_id or 'none'}",
        f"- source_audit_status: {audit.source_audit_status}",
        f"- capability_count: {audit.capability_count}",
        f"- audits: {audit.audit_count}",
        f"- blocked_retries: {audit.blocked_retry_count}",
        f"- operator_reviews_required: {audit.operator_review_required_count}",
        f"- blocked_trust_promotions: {audit.blocked_trust_promotion_count}",
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
        "## Automatic Retry Audit",
        "",
    ]
    if audit.audit_items:
        lines.extend(render_audit_item_line(item) for item in audit.audit_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Trust Promotion Audit", ""])
    if source_audit is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_audit.id}",
                f"- status: {source_audit.status}",
                f"- audits: {source_audit.audit_count}",
                f"- blocked_trust_promotions: {source_audit.blocked_trust_promotion_count}",
                f"- operator_reviews_required: {source_audit.operator_review_required_count}",
                f"- deferred_promotions: {source_audit.deferred_promotion_count}",
                f"- missing_evidence: {source_audit.missing_evidence_count}",
                f"- approvals_required: {source_audit.approval_required_count}",
                f"- report: {source_audit.report_path}",
            ]
        )

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local automatic retry audit.",
            "- Does not create trust promotion audits as a side effect.",
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
            "- Does not retry or replay work automatically.",
            "- Does not generate proof artifacts automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not change routing or claims.",
            "- Does not track real spend or mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_capability_automatic_retry_audit_line(
    audit: CapabilityAutomaticRetryAudit,
) -> str:
    return (
        f"- {audit.id}: status={audit.status} "
        f"source_audit={audit.source_audit_id or 'none'} "
        f"source_status={audit.source_audit_status} "
        f"audits={audit.audit_count} "
        f"blocked_retries={audit.blocked_retry_count} "
        f"operator_reviews_required={audit.operator_review_required_count} "
        f"blocked_trust_promotions={audit.blocked_trust_promotion_count} "
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
        f"recommended_retry_action={item['recommended_retry_action']} "
        f"retry_state={item['retry_state']} "
        f"source_trust_action={item['source_trust_action']} "
        f"source_trust_state={item['source_trust_state']} "
        f"evidence_state={item['evidence_state']} "
        f"approval_state={item['approval_state']} "
        f"approval_boundary={item['approval_boundary']} "
        f"retry_effect={item['retry_effect']} "
        f"routing_effect={item['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _audit_from_latest_trust_audit(
    *,
    storage: Storage,
    source_audit: CapabilityTrustPromotionAudit | None,
    report_path: str,
) -> CapabilityAutomaticRetryAudit:
    if source_audit is None:
        return storage.record_capability_automatic_retry_audit(
            status=TRUST_PROMOTION_AUDIT_MISSING,
            source_audit_id=None,
            source_audit_status="none",
            capability_count=0,
            audit_count=0,
            blocked_retry_count=0,
            operator_review_required_count=0,
            blocked_trust_promotion_count=0,
            deferred_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["capability-trust-promotion-audit"],
            reason="No capability trust promotion audit exists yet.",
            audit_items=[],
            report_path=report_path,
        )

    if (
        source_audit.status != "operator_trust_review_required"
        and not source_audit.audit_items
        and source_audit.recommended_commands
    ):
        return storage.record_capability_automatic_retry_audit(
            status=TRUST_PROMOTION_AUDIT_MISSING,
            source_audit_id=source_audit.id,
            source_audit_status=source_audit.status,
            capability_count=source_audit.capability_count,
            audit_count=0,
            blocked_retry_count=0,
            operator_review_required_count=0,
            blocked_trust_promotion_count=source_audit.blocked_trust_promotion_count,
            deferred_promotion_count=source_audit.deferred_promotion_count,
            missing_evidence_count=source_audit.missing_evidence_count,
            approval_required_count=source_audit.approval_required_count,
            boundary_count=source_audit.boundary_count,
            recommended_commands=source_audit.recommended_commands,
            reason=(
                "Latest capability trust promotion audit is incomplete; "
                "run the recommended upstream command before auditing automatic retries."
            ),
            audit_items=[],
            report_path=report_path,
        )

    audit_items = [
        _audit_item_from_trust_audit_item(item)
        for item in source_audit.audit_items
    ]
    blocked_retry_count = sum(
        1
        for item in audit_items
        if item["recommended_retry_action"] == KEEP_RETRY_DISABLED
    )
    operator_review_required_count = sum(
        1
        for item in audit_items
        if item["recommended_retry_action"] == MANUAL_RETRY_REVIEW_REQUIRED
    )
    if blocked_retry_count:
        status = AUTOMATIC_RETRY_BLOCKED
        reason = (
            "Automatic retry remains blocked until trust promotion, required "
            "evidence, and operator approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_RETRY_REVIEW_REQUIRED
        reason = (
            "Trust promotion audit rows are ready for manual retry review; "
            "no retry or routing state changes were applied."
        )
    else:
        status = NO_AUTOMATIC_RETRY_CANDIDATES
        reason = "No automatic retry audit rows were needed from the latest trust audit."

    return storage.record_capability_automatic_retry_audit(
        status=status,
        source_audit_id=source_audit.id,
        source_audit_status=source_audit.status,
        capability_count=source_audit.capability_count,
        audit_count=len(audit_items),
        blocked_retry_count=blocked_retry_count,
        operator_review_required_count=operator_review_required_count,
        blocked_trust_promotion_count=source_audit.blocked_trust_promotion_count,
        deferred_promotion_count=source_audit.deferred_promotion_count,
        missing_evidence_count=source_audit.missing_evidence_count,
        approval_required_count=source_audit.approval_required_count,
        boundary_count=source_audit.boundary_count,
        recommended_commands=[],
        reason=reason,
        audit_items=audit_items,
        report_path=report_path,
    )


def _audit_item_from_trust_audit_item(item: dict[str, str]) -> dict[str, str]:
    retry_blocked = item["recommended_trust_action"] == KEEP_TRUST_UNPROMOTED
    return {
        "capability": item["capability"],
        "recommended_retry_action": (
            KEEP_RETRY_DISABLED if retry_blocked else MANUAL_RETRY_REVIEW_REQUIRED
        ),
        "retry_state": RETRY_BLOCKED if retry_blocked else RETRY_REVIEW_READY,
        "source_trust_action": item["recommended_trust_action"],
        "source_trust_state": item["trust_promotion_state"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "retry_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }
