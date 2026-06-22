from __future__ import annotations

from pathlib import Path
from typing import Callable, Protocol

from agent_os.storage import GoalCompletionAudit, Storage


BLOCKED_BY_REPORT_ONLY_PROOFS = "blocked_by_report_only_proofs"
MISSING_REQUIRED_PROOFS = "missing_required_proofs"
READY_FOR_OPERATOR_COMPLETION_REVIEW = "ready_for_operator_completion_review"
BLOCKED_REPORT_ONLY = "blocked_report_only"
MISSING_PROOF = "missing_proof"
PROVEN = "proven"
REPORT_PATH = "docs/goal-completion-audit.md"


class ProofChecklist(Protocol):
    id: str
    status: str
    report_path: str
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int


RequirementGetter = Callable[[Storage], list[ProofChecklist]]


REQUIREMENTS: tuple[tuple[str, str, RequirementGetter], ...] = (
    (
        "hosted_dashboard",
        "hosted-dashboard-proof-checklist",
        lambda storage: storage.list_recent_hosted_dashboard_proof_checklists(limit=1),
    ),
    (
        "remote_workers",
        "remote-worker-proof-checklist",
        lambda storage: storage.list_recent_remote_worker_proof_checklists(limit=1),
    ),
    (
        "autonomous_scheduling",
        "autonomous-scheduling-proof-checklist",
        lambda storage: storage.list_recent_autonomous_scheduling_proof_checklists(limit=1),
    ),
    (
        "browser_desktop_adapters",
        "browser-desktop-adapter-proof-checklist",
        lambda storage: storage.list_recent_browser_desktop_adapter_proof_checklists(limit=1),
    ),
    (
        "ci_deploy_proof",
        "ci-deploy-proof-checklist",
        lambda storage: storage.list_recent_ci_deploy_proof_checklists(limit=1),
    ),
    (
        "budget_enforcement",
        "budget-enforcement-proof-checklist",
        lambda storage: storage.list_recent_budget_enforcement_proof_checklists(limit=1),
    ),
    (
        "trust_promotion",
        "trust-promotion-proof-checklist",
        lambda storage: storage.list_recent_trust_promotion_proof_checklists(limit=1),
    ),
    (
        "automatic_retries",
        "automatic-retry-proof-checklist",
        lambda storage: storage.list_recent_automatic_retry_proof_checklists(limit=1),
    ),
    (
        "real_cost_tracking",
        "real-cost-tracking-proof-checklist",
        lambda storage: storage.list_recent_real_cost_tracking_proof_checklists(limit=1),
    ),
)


def write_goal_completion_audit(root: Path) -> tuple[Path, GoalCompletionAudit]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    audit_items = [_audit_requirement(storage, requirement) for requirement in REQUIREMENTS]
    external_decisions = _blocked_task_lines(root / "tasks.md")
    missing_commands = [
        item["recommended_command"]
        for item in audit_items
        if item["completion_state"] == MISSING_PROOF
    ]
    missing_evidence_count = sum(int(item["missing_evidence_count"]) for item in audit_items)
    approval_required_count = sum(int(item["approval_required_count"]) for item in audit_items)
    blocked_requirement_count = sum(
        1 for item in audit_items if item["completion_state"] == BLOCKED_REPORT_ONLY
    )
    satisfied_requirement_count = sum(
        1 for item in audit_items if item["completion_state"] == PROVEN
    )
    if missing_commands:
        status = MISSING_REQUIRED_PROOFS
        reason = (
            "The expansion goal cannot be completed because required local proof "
            "checklists are missing."
        )
    elif blocked_requirement_count or external_decisions:
        status = BLOCKED_BY_REPORT_ONLY_PROOFS
        reason = (
            "The expansion goal remains blocked because proof rows are report-only "
            "and external decisions or approvals are still required."
        )
    else:
        status = READY_FOR_OPERATOR_COMPLETION_REVIEW
        reason = (
            "All audited expansion requirements have local proof rows; operator "
            "completion review is still required before any goal-complete claim."
        )

    audit = storage.record_goal_completion_audit(
        status=status,
        requirement_count=len(audit_items),
        satisfied_requirement_count=satisfied_requirement_count,
        blocked_requirement_count=blocked_requirement_count,
        missing_evidence_count=missing_evidence_count,
        approval_required_count=approval_required_count,
        external_decision_count=len(external_decisions),
        recommended_commands=missing_commands,
        reason=reason,
        audit_items=audit_items,
        external_decisions=external_decisions,
        report_path=REPORT_PATH,
    )
    report_path = root / audit.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_goal_completion_audit_report(audit), encoding="utf-8")
    return report_path, audit


def render_goal_completion_audit_report(audit: GoalCompletionAudit) -> str:
    lines = [
        "# Goal Completion Audit",
        "",
        f"- id: {audit.id}",
        f"- status: {audit.status}",
        f"- requirements: {audit.requirement_count}",
        f"- satisfied_requirements: {audit.satisfied_requirement_count}",
        f"- blocked_requirements: {audit.blocked_requirement_count}",
        f"- missing_evidence: {audit.missing_evidence_count}",
        f"- approvals_required: {audit.approval_required_count}",
        f"- external_decisions_required: {audit.external_decision_count}",
        f"- recommended_commands: {format_recommended_commands(audit.recommended_commands)}",
        f"- report_path: {audit.report_path}",
        f"- created_at: {audit.created_at}",
        "",
        "## Recommendation",
        "",
        f"- reason: {audit.reason}",
        "",
        "## Audited Requirements",
        "",
    ]
    if audit.audit_items:
        lines.extend(render_goal_completion_audit_item_line(item) for item in audit.audit_items)
    else:
        lines.append("- none")

    lines.extend(["", "## External Decisions", ""])
    if audit.external_decisions:
        lines.extend(f"- {decision}" for decision in audit.external_decisions)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local goal completion audit.",
            "- Does not mark the active goal complete.",
            "- Does not approve capabilities automatically.",
            "- Does not collect evidence automatically.",
            "- Does not enable hosted dashboard.",
            "- Does not deploy hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not claim remote work.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not retry or replay work.",
            "- Does not track real spend.",
            "- Does not change routing or claims.",
            "- Does not mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_goal_completion_audit_line(audit: GoalCompletionAudit) -> str:
    return (
        f"- {audit.id}: status={audit.status} "
        f"requirements={audit.requirement_count} "
        f"satisfied_requirements={audit.satisfied_requirement_count} "
        f"blocked_requirements={audit.blocked_requirement_count} "
        f"missing_evidence={audit.missing_evidence_count} "
        f"approvals_required={audit.approval_required_count} "
        f"external_decisions_required={audit.external_decision_count} "
        f"recommended_commands={format_recommended_commands(audit.recommended_commands)} "
        f"report={audit.report_path}"
    )


def render_goal_completion_audit_item_line(item: dict[str, str]) -> str:
    return (
        f"- {item['requirement']}: completion_state={item['completion_state']} "
        f"evidence_id={item['evidence_id']} evidence_status={item['evidence_status']} "
        f"missing_evidence={item['missing_evidence_count']} "
        f"approvals_required={item['approval_required_count']} "
        f"approval_boundary={item['approval_boundary']} "
        f"routing_effect={item['routing_effect']} "
        f"report={item['report_path']} "
        f"recommended_command={item['recommended_command']}"
    )


def format_recommended_commands(commands: list[str]) -> str:
    if not commands:
        return "none"
    return ",".join(commands)


def _audit_requirement(
    storage: Storage,
    requirement: tuple[str, str, RequirementGetter],
) -> dict[str, str]:
    name, command, getter = requirement
    checklists = getter(storage)
    checklist = checklists[0] if checklists else None
    if checklist is None:
        return {
            "requirement": name,
            "completion_state": MISSING_PROOF,
            "evidence_id": "none",
            "evidence_status": "none",
            "missing_evidence_count": "1",
            "approval_required_count": "0",
            "approval_boundary": "explicit_operator_approval_required",
            "routing_effect": "none",
            "report_path": "none",
            "recommended_command": command,
        }
    completion_state = (
        BLOCKED_REPORT_ONLY if checklist.status.endswith("_blocked") else PROVEN
    )
    return {
        "requirement": name,
        "completion_state": completion_state,
        "evidence_id": checklist.id,
        "evidence_status": checklist.status,
        "missing_evidence_count": str(checklist.missing_evidence_count),
        "approval_required_count": str(checklist.approval_required_count),
        "approval_boundary": (
            "explicit_operator_approval_required"
            if checklist.boundary_count
            else "none"
        ),
        "routing_effect": "none",
        "report_path": checklist.report_path,
        "recommended_command": "none",
    }


def _blocked_task_lines(tasks_path: Path) -> list[str]:
    if not tasks_path.exists():
        return []
    decisions: list[str] = []
    current_section = ""
    for raw_line in tasks_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_section = line.removeprefix("## ").strip().lower()
            continue
        if current_section == "blocked" and line.startswith("- [ ] "):
            decisions.append(line.removeprefix("- [ ] ").strip())
            continue
        if current_section == "blocked" and decisions and raw_line.startswith(" "):
            continuation = line
            if continuation:
                decisions[-1] = f"{decisions[-1]} {continuation}"
    return decisions
