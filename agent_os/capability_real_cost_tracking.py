from __future__ import annotations

from pathlib import Path

from agent_os.storage import (
    CapabilityAutomaticRetryAudit,
    CapabilityRealCostTrackingAudit,
    Storage,
)


AUTOMATIC_RETRY_AUDIT_MISSING = "automatic_retry_audit_missing"
REAL_COST_TRACKING_BLOCKED = "real_cost_tracking_blocked"
OPERATOR_COST_REVIEW_REQUIRED = "operator_cost_review_required"
NO_REAL_COST_TRACKING_CANDIDATES = "no_real_cost_tracking_candidates"
KEEP_COST_TRACKING_DISABLED = "keep_cost_tracking_disabled"
MANUAL_COST_REVIEW_REQUIRED = "manual_cost_review_required"
KEEP_RETRY_DISABLED = "keep_retry_disabled"
COST_TRACKING_BLOCKED = "blocked_until_retry_review_and_operator_approval"
COST_REVIEW_READY = "ready_for_operator_cost_review"
NO_EFFECT = "none"
REPORT_PATH = "docs/capability-real-cost-tracking-audit.md"


def write_capability_real_cost_tracking_audit(
    root: Path,
) -> tuple[Path, CapabilityRealCostTrackingAudit]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    retry_audits = storage.list_recent_capability_automatic_retry_audits(limit=1)
    source_audit = retry_audits[0] if retry_audits else None
    audit = _audit_from_latest_retry_audit(
        storage=storage,
        source_audit=source_audit,
        report_path=REPORT_PATH,
    )
    report_path = root / audit.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_real_cost_tracking_audit_report(
            audit,
            source_audit,
        ),
        encoding="utf-8",
    )
    return report_path, audit


def render_capability_real_cost_tracking_audit_report(
    audit: CapabilityRealCostTrackingAudit,
    source_audit: CapabilityAutomaticRetryAudit | None,
) -> str:
    lines = [
        "# Capability Real Cost Tracking Audit",
        "",
        f"- id: {audit.id}",
        f"- status: {audit.status}",
        f"- source_audit_id: {audit.source_audit_id or 'none'}",
        f"- source_audit_status: {audit.source_audit_status}",
        f"- capability_count: {audit.capability_count}",
        f"- audits: {audit.audit_count}",
        f"- blocked_cost_tracking: {audit.blocked_cost_tracking_count}",
        f"- operator_reviews_required: {audit.operator_review_required_count}",
        f"- blocked_retries: {audit.blocked_retry_count}",
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
        "## Real Cost Tracking Audit",
        "",
    ]
    if audit.audit_items:
        lines.extend(render_audit_item_line(item) for item in audit.audit_items)
    else:
        lines.append("- none")

    lines.extend(["", "## Source Automatic Retry Audit", ""])
    if source_audit is None:
        lines.append("- none")
    else:
        lines.extend(
            [
                f"- id: {source_audit.id}",
                f"- status: {source_audit.status}",
                f"- audits: {source_audit.audit_count}",
                f"- blocked_retries: {source_audit.blocked_retry_count}",
                f"- operator_reviews_required: {source_audit.operator_review_required_count}",
                f"- blocked_trust_promotions: {source_audit.blocked_trust_promotion_count}",
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
            "- Report-only local real cost tracking audit.",
            "- Does not create automatic retry audits as a side effect.",
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
            "- Does not track real spend automatically.",
            "- Does not generate proof artifacts automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not change routing or claims.",
            "- Does not mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_capability_real_cost_tracking_audit_line(
    audit: CapabilityRealCostTrackingAudit,
) -> str:
    return (
        f"- {audit.id}: status={audit.status} "
        f"source_audit={audit.source_audit_id or 'none'} "
        f"source_status={audit.source_audit_status} "
        f"audits={audit.audit_count} "
        f"blocked_cost_tracking={audit.blocked_cost_tracking_count} "
        f"operator_reviews_required={audit.operator_review_required_count} "
        f"blocked_retries={audit.blocked_retry_count} "
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
        f"recommended_cost_action={item['recommended_cost_action']} "
        f"cost_tracking_state={item['cost_tracking_state']} "
        f"source_retry_action={item['source_retry_action']} "
        f"source_retry_state={item['source_retry_state']} "
        f"source_trust_action={item['source_trust_action']} "
        f"source_trust_state={item['source_trust_state']} "
        f"evidence_state={item['evidence_state']} "
        f"approval_state={item['approval_state']} "
        f"approval_boundary={item['approval_boundary']} "
        f"cost_effect={item['cost_effect']} "
        f"routing_effect={item['routing_effect']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _audit_from_latest_retry_audit(
    *,
    storage: Storage,
    source_audit: CapabilityAutomaticRetryAudit | None,
    report_path: str,
) -> CapabilityRealCostTrackingAudit:
    if source_audit is None:
        return storage.record_capability_real_cost_tracking_audit(
            status=AUTOMATIC_RETRY_AUDIT_MISSING,
            source_audit_id=None,
            source_audit_status="none",
            capability_count=0,
            audit_count=0,
            blocked_cost_tracking_count=0,
            operator_review_required_count=0,
            blocked_retry_count=0,
            blocked_trust_promotion_count=0,
            deferred_promotion_count=0,
            missing_evidence_count=0,
            approval_required_count=0,
            boundary_count=0,
            recommended_commands=["capability-automatic-retry-audit"],
            reason="No capability automatic retry audit exists yet.",
            audit_items=[],
            report_path=report_path,
        )

    if (
        source_audit.status != "operator_retry_review_required"
        and not source_audit.audit_items
        and source_audit.recommended_commands
    ):
        return storage.record_capability_real_cost_tracking_audit(
            status=AUTOMATIC_RETRY_AUDIT_MISSING,
            source_audit_id=source_audit.id,
            source_audit_status=source_audit.status,
            capability_count=source_audit.capability_count,
            audit_count=0,
            blocked_cost_tracking_count=0,
            operator_review_required_count=0,
            blocked_retry_count=source_audit.blocked_retry_count,
            blocked_trust_promotion_count=source_audit.blocked_trust_promotion_count,
            deferred_promotion_count=source_audit.deferred_promotion_count,
            missing_evidence_count=source_audit.missing_evidence_count,
            approval_required_count=source_audit.approval_required_count,
            boundary_count=source_audit.boundary_count,
            recommended_commands=source_audit.recommended_commands,
            reason=(
                "Latest capability automatic retry audit is incomplete; "
                "run the recommended upstream command before auditing real cost tracking."
            ),
            audit_items=[],
            report_path=report_path,
        )

    audit_items = [
        _audit_item_from_retry_audit_item(item)
        for item in source_audit.audit_items
    ]
    blocked_cost_tracking_count = sum(
        1
        for item in audit_items
        if item["recommended_cost_action"] == KEEP_COST_TRACKING_DISABLED
    )
    operator_review_required_count = sum(
        1
        for item in audit_items
        if item["recommended_cost_action"] == MANUAL_COST_REVIEW_REQUIRED
    )
    if blocked_cost_tracking_count:
        status = REAL_COST_TRACKING_BLOCKED
        reason = (
            "Real cost tracking remains blocked until retry review, required "
            "evidence, and operator approvals are present."
        )
    elif operator_review_required_count:
        status = OPERATOR_COST_REVIEW_REQUIRED
        reason = (
            "Automatic retry audit rows are ready for manual cost review; "
            "no cost, budget, or routing state changes were applied."
        )
    else:
        status = NO_REAL_COST_TRACKING_CANDIDATES
        reason = "No real cost tracking audit rows were needed from the latest retry audit."

    return storage.record_capability_real_cost_tracking_audit(
        status=status,
        source_audit_id=source_audit.id,
        source_audit_status=source_audit.status,
        capability_count=source_audit.capability_count,
        audit_count=len(audit_items),
        blocked_cost_tracking_count=blocked_cost_tracking_count,
        operator_review_required_count=operator_review_required_count,
        blocked_retry_count=source_audit.blocked_retry_count,
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


def _audit_item_from_retry_audit_item(item: dict[str, str]) -> dict[str, str]:
    cost_blocked = item["recommended_retry_action"] == KEEP_RETRY_DISABLED
    return {
        "capability": item["capability"],
        "recommended_cost_action": (
            KEEP_COST_TRACKING_DISABLED
            if cost_blocked
            else MANUAL_COST_REVIEW_REQUIRED
        ),
        "cost_tracking_state": (
            COST_TRACKING_BLOCKED if cost_blocked else COST_REVIEW_READY
        ),
        "source_retry_action": item["recommended_retry_action"],
        "source_retry_state": item["retry_state"],
        "source_trust_action": item["source_trust_action"],
        "source_trust_state": item["source_trust_state"],
        "evidence_state": item["evidence_state"],
        "approval_state": item["approval_state"],
        "approval_boundary": item["approval_boundary"],
        "cost_effect": NO_EFFECT,
        "routing_effect": item["routing_effect"],
    }
