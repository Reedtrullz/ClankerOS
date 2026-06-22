from __future__ import annotations

import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from agent_os.operator_approval_effect_proposals import (
    IDEMPOTENCY_PREFIX as OPERATOR_APPROVAL_EFFECT_IDEMPOTENCY_PREFIX,
    PROPOSALS_RECORDED as OPERATOR_APPROVAL_EFFECT_PROPOSALS_RECORDED,
)
from agent_os.storage import IterationPacket, Storage


QUEUE_PRIORITY = ["now", "next", "improve", "recurring"]
SKIPPED_SECTIONS = {"blocked"}
SELECTION_POLICY = "highest-score-then-lowest-complexity"
METADATA_PATTERN = re.compile(r"<!--\s*(.*?)\s*-->")
VERIFICATION_COMMANDS = [
    "python3 -m pytest -q",
    "python3 -m agent_os.cli sweep-stuck --timeout-seconds 1800",
    "python3 -m agent_os.cli queue-health",
    "python3 -m agent_os.cli handoff-review",
    "python3 -m agent_os.cli eval-candidates",
    "python3 -m agent_os.cli approvals",
    "python3 -m agent_os.cli budget-trust-posture",
    "python3 -m agent_os.cli dispatch-posture-history",
    "python3 -m agent_os.cli dispatch-posture-staleness",
    "python3 -m agent_os.cli dispatch-posture-refresh",
    "python3 -m agent_os.cli capability-expansion-ledger",
    "python3 -m agent_os.cli capability-readiness-review",
    "python3 -m agent_os.cli capability-proof-gap-index",
    "python3 -m agent_os.cli capability-approval-boundary-matrix",
    "python3 -m agent_os.cli capability-evidence-collection-plan",
    "python3 -m agent_os.cli capability-promotion-gate-checklist",
    "python3 -m agent_os.cli capability-promotion-decision-ledger",
    "python3 -m agent_os.cli capability-trust-promotion-audit",
    "python3 -m agent_os.cli capability-automatic-retry-audit",
    "python3 -m agent_os.cli capability-real-cost-tracking-audit",
    "python3 -m agent_os.cli hosted-dashboard-proof-checklist",
    "python3 -m agent_os.cli remote-worker-proof-checklist",
    "python3 -m agent_os.cli autonomous-scheduling-proof-checklist",
    "python3 -m agent_os.cli browser-desktop-adapter-proof-checklist",
    "python3 -m agent_os.cli ci-deploy-proof-checklist",
    "python3 -m agent_os.cli budget-enforcement-proof-checklist",
    "python3 -m agent_os.cli trust-promotion-proof-checklist",
    "python3 -m agent_os.cli automatic-retry-proof-checklist",
    "python3 -m agent_os.cli real-cost-tracking-proof-checklist",
    "python3 -m agent_os.cli goal-completion-audit",
    "python3 -m agent_os.cli expansion-decision-brief",
    "python3 -m agent_os.cli expansion-decision-evidence-index",
    "python3 -m agent_os.cli expansion-operator-review-checklist",
    "python3 -m agent_os.cli expansion-operator-decision-ledger",
    "python3 -m agent_os.cli expansion-operator-approval-draft",
    "python3 -m agent_os.cli expansion-operator-approval-request-review",
    "python3 -m agent_os.cli expansion-operator-approval-schema-decision",
    "python3 -m agent_os.cli expansion-operator-approval-schema-migration-plan",
    "python3 -m agent_os.cli expansion-operator-approval-schema-migration-approval-request",
    "python3 -m agent_os.cli expansion-operator-approval-schema-migration-decision-ledger",
    "python3 -m agent_os.cli expansion-operator-approval-schema-migration-action-checklist",
    "python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-packet",
    "python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-input-template",
    "python3 -m agent_os.cli expansion-operator-approval-effect-proposals",
    "python3 -m agent_os.cli expansion-operator-approval-effect-apply --operator-id operator --selection-note \"Apply approved local operator approval effect proposals.\" --evidence-reference docs/expansion-operator-approval-effect-proposals.md",
    "python3 -m agent_os.cli capability-activation-tasks",
    "python3 -m agent_os.cli capability-activation-contracts",
    "python3 -m agent_os.cli capability-activation-evidence --all --evidence-kind proof_checklist --evidence-reference docs/capability-activation-contracts.md --verification-command \"python3 -m agent_os.cli capability-activation-contracts\" --verification-status blocked --recorded-by operator --summary \"Current activation contracts are present but still missing capability-specific proof.\"",
    "python3 -m agent_os.cli capability-activation-decide --operator-id operator --selected-action request_more_evidence --selection-note \"Requested capability-specific proof before any activation decision.\" --evidence-reference docs/capability-activation-evidence.md",
    "python3 -m agent_os.cli capability-activation-followups",
    "python3 -m agent_os.cli capability-activation-followup-delegations",
    "python3 -m agent_os.cli eval",
    "python3 -m agent_os.cli playbooks",
    "python3 -m agent_os.cli dashboard",
]


@dataclass(frozen=True)
class QueueItem:
    section: str
    text: str
    score: int
    complexity: int
    order: int
    selection_reason: str


def generate_next_iteration_packet(root: Path) -> IterationPacket:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    source_path = root / "tasks.md"
    item = _select_next_queue_item(source_path)
    packet_path = root / "docs" / "next-iteration.md"
    packet_path.parent.mkdir(parents=True, exist_ok=True)

    relative_packet_path = _relative_to_root(root, packet_path)
    packet = storage.record_iteration_packet(
        focus=item.text,
        source_path=_relative_to_root(root, source_path),
        source_section=item.section,
        status="planned",
        packet_path=relative_packet_path,
        verification_commands=VERIFICATION_COMMANDS,
        selection_policy=SELECTION_POLICY,
        selection_reason=item.selection_reason,
        selected_score=item.score,
        selected_complexity=item.complexity,
    )
    packet_path.write_text(_render_packet(root, packet), encoding="utf-8")
    return packet


def _select_next_queue_item(source_path: Path) -> QueueItem:
    if not source_path.exists():
        return QueueItem(
            section="fallback",
            text="Create or refresh the live momentum queue in tasks.md.",
            score=0,
            complexity=0,
            order=0,
            selection_reason="selected fallback because tasks.md is missing",
        )

    current_section = ""
    candidates: dict[str, list[str]] = {}
    order = 0
    for raw_line in source_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("## "):
            current_section = line.removeprefix("## ").strip().lower()
            candidates.setdefault(current_section, [])
            continue
        if not line.startswith("- [ ] "):
            continue
        if current_section in SKIPPED_SECTIONS:
            continue
        candidates.setdefault(current_section, []).append(line.removeprefix("- [ ] ").strip())
        order += 1

    for section in QUEUE_PRIORITY:
        if candidates.get(section):
            return _choose_queue_item(section, candidates[section])

    for section, items in candidates.items():
        if items:
            return _choose_queue_item(section, items)

    return QueueItem(
        section="fallback",
        text="Review current evidence and add the next actionable queue item.",
        score=0,
        complexity=0,
        order=0,
        selection_reason="selected fallback because no actionable queue items were found",
    )


def _render_packet(root: Path, packet: IterationPacket) -> str:
    command_lines = "\n".join(f"- `{command}`" for command in packet.verification_commands)
    posture_lines = "\n".join(f"- {line}" for line in _current_posture(root))
    return "\n".join(
        [
            "# Next Iteration Packet",
            "",
            f"- Packet ID: {packet.id}",
            f"- Status: {packet.status}",
            f"- Source: {packet.source_path}#{packet.source_section}",
            "",
            "## Objective",
            "",
            f"Advance the Agent System north-star goal by completing: {packet.focus}",
            "",
            "## Definition Of Done",
            "",
            "- Red-first regression coverage exists for the selected behavior.",
            "- The implementation leaves a durable file or SQLite evidence trail.",
            "- The dashboard or project state exposes the new loop state.",
            "- Repo operating files name the changed behavior and next action.",
            "- Verification commands pass locally before reporting completion.",
            "",
            "## Verification Commands",
            "",
            command_lines,
            "",
            "## Simplicity Guardrail",
            "",
            f"- selection_policy: {packet.selection_policy}",
            f"- selection_reason: {packet.selection_reason}",
            f"- selected_score: {packet.selected_score}",
            f"- selected_complexity: {packet.selected_complexity}",
            "",
            "## Guardrails And Non-Claims",
            "",
            "- No external side effects without an explicit approval checkpoint.",
            "- No hosted dashboard, background scheduler, or remote worker claim.",
            "- No destructive action without an explicit checkpoint.",
            "- Local proof is not CI, deploy, or live production proof.",
            "",
            "## Current Posture",
            "",
            posture_lines,
            "",
            "## Resume Prompt",
            "",
            (
                "Continue with the selected iteration, preserve the red-green "
                "verification trail, update repo state, regenerate the dashboard, "
                "and log evidence to Obsidian."
            ),
            "",
        ]
    )


def _choose_queue_item(section: str, raw_items: list[str]) -> QueueItem:
    candidates = [
        _parse_queue_item(section=section, raw_text=raw_text, order=order)
        for order, raw_text in enumerate(raw_items)
    ]
    max_score = max(candidate.score for candidate in candidates)
    score_matched = [
        candidate for candidate in candidates if candidate.score == max_score
    ]
    min_complexity = min(candidate.complexity for candidate in score_matched)
    complexity_matched = [
        candidate
        for candidate in score_matched
        if candidate.complexity == min_complexity
    ]
    selected = sorted(complexity_matched, key=lambda candidate: candidate.order)[0]

    if len(score_matched) > 1 and len(
        {candidate.complexity for candidate in score_matched}
    ) > 1:
        reason = (
            f"selected lower complexity {selected.complexity} among "
            f"{len(score_matched)} candidates with equal score {selected.score}"
        )
    elif len(score_matched) > 1:
        reason = (
            f"selected queue order among {len(score_matched)} candidates with "
            f"equal score {selected.score} and equal complexity {selected.complexity}"
        )
    elif len(candidates) > 1:
        reason = (
            f"selected highest score {selected.score}; complexity "
            f"{selected.complexity} recorded for audit"
        )
    else:
        reason = (
            f"selected only actionable item with score {selected.score} "
            f"and complexity {selected.complexity}"
        )

    return QueueItem(
        section=selected.section,
        text=selected.text,
        score=selected.score,
        complexity=selected.complexity,
        order=selected.order,
        selection_reason=reason,
    )


def _parse_queue_item(section: str, raw_text: str, order: int) -> QueueItem:
    score = 0
    complexity = 0
    metadata_match = METADATA_PATTERN.search(raw_text)
    if metadata_match:
        metadata = {
            key: value
            for key, value in (
                token.split("=", maxsplit=1)
                for token in metadata_match.group(1).split()
                if "=" in token
            )
        }
        score = _parse_int(metadata.get("score"), fallback=0)
        complexity = _parse_int(metadata.get("complexity"), fallback=0)

    clean_text = METADATA_PATTERN.sub("", raw_text).strip()
    return QueueItem(
        section=section,
        text=clean_text,
        score=score,
        complexity=complexity,
        order=order,
        selection_reason="",
    )


def _parse_int(value: str | None, *, fallback: int) -> int:
    if value is None:
        return fallback
    try:
        return int(value)
    except ValueError:
        return fallback


def _current_posture(root: Path) -> list[str]:
    db_path = root / ".agent" / "state.db"
    if not db_path.exists():
        return ["state database missing"]

    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        task_statuses = Counter(
            {
                row["status"]: row["count"]
                for row in connection.execute(
                    "select status, count(*) as count from tasks group by status"
                )
            }
        )
        approval_count = _count_rows(connection, "approval_requests", "status = 'pending'")
        stuck_count = _count_rows(
            connection,
            "incidents",
            "incident_type = 'task_stuck' and status = 'open'",
        )
        incident_count = _count_rows(connection, "incidents", "status = 'open'")
        queue_health_hotspots = len(Storage(db_path).list_queue_health_findings())
        active_playbooks = _count_rows(connection, "playbooks", "status = 'active'")
        proposed_eval_candidates = _count_rows(
            connection,
            "eval_candidates",
            "status = 'proposed'",
        )
        eval_after_change_failures = _count_rows(
            connection,
            "eval_after_change_checks",
            "status = 'fail'",
        )
        stable_distilled_learnings = 0
        distillation_rows = Storage(db_path).list_recent_learning_distillations(limit=1)
        if distillation_rows:
            stable_distilled_learnings = distillation_rows[0].stable_learning_count
        budget_trust_posture = "none"
        posture_rows = Storage(db_path).list_recent_budget_trust_posture_reports(limit=1)
        if posture_rows:
            budget_trust_posture = posture_rows[0].status
        dispatch_posture_history = "none"
        history_rows = Storage(db_path).list_recent_dispatch_posture_history_summaries(
            limit=1,
        )
        if history_rows:
            dispatch_posture_history = history_rows[0].status
        dispatch_posture_staleness = "none"
        staleness_rows = Storage(db_path).list_recent_dispatch_posture_staleness_reviews(
            limit=1,
        )
        if staleness_rows:
            dispatch_posture_staleness = staleness_rows[0].status
        dispatch_posture_refresh = "none"
        refresh_rows = Storage(db_path).list_recent_dispatch_posture_refresh_recommendations(
            limit=1,
        )
        if refresh_rows:
            dispatch_posture_refresh = refresh_rows[0].status
        capability_expansion_ledger = "none"
        ledger_rows = Storage(db_path).list_recent_capability_expansion_ledgers(
            limit=1,
        )
        if ledger_rows:
            capability_expansion_ledger = ledger_rows[0].status
        capability_readiness_review = "none"
        readiness_rows = Storage(db_path).list_recent_capability_readiness_reviews(
            limit=1,
        )
        if readiness_rows:
            capability_readiness_review = readiness_rows[0].status
        capability_proof_gap_index = "none"
        proof_gap_rows = Storage(db_path).list_recent_capability_proof_gap_indexes(
            limit=1,
        )
        if proof_gap_rows:
            capability_proof_gap_index = proof_gap_rows[0].status
        capability_approval_boundary_matrix = "none"
        approval_boundary_rows = (
            Storage(db_path).list_recent_capability_approval_boundary_matrices(
                limit=1,
            )
        )
        if approval_boundary_rows:
            capability_approval_boundary_matrix = approval_boundary_rows[0].status
        capability_evidence_collection_plan = "none"
        evidence_collection_rows = (
            Storage(db_path).list_recent_capability_evidence_collection_plans(
                limit=1,
            )
        )
        if evidence_collection_rows:
            capability_evidence_collection_plan = evidence_collection_rows[0].status
        capability_promotion_gate_checklist = "none"
        promotion_gate_rows = (
            Storage(db_path).list_recent_capability_promotion_gate_checklists(
                limit=1,
            )
        )
        if promotion_gate_rows:
            capability_promotion_gate_checklist = promotion_gate_rows[0].status
        capability_promotion_decision_ledger = "none"
        promotion_decision_rows = (
            Storage(db_path).list_recent_capability_promotion_decision_ledgers(
                limit=1,
            )
        )
        if promotion_decision_rows:
            capability_promotion_decision_ledger = promotion_decision_rows[0].status
        capability_trust_promotion_audit = "none"
        trust_promotion_rows = (
            Storage(db_path).list_recent_capability_trust_promotion_audits(
                limit=1,
            )
        )
        if trust_promotion_rows:
            capability_trust_promotion_audit = trust_promotion_rows[0].status
        capability_automatic_retry_audit = "none"
        automatic_retry_rows = (
            Storage(db_path).list_recent_capability_automatic_retry_audits(
                limit=1,
            )
        )
        if automatic_retry_rows:
            capability_automatic_retry_audit = automatic_retry_rows[0].status
        capability_real_cost_tracking_audit = "none"
        real_cost_tracking_rows = (
            Storage(db_path).list_recent_capability_real_cost_tracking_audits(
                limit=1,
            )
        )
        if real_cost_tracking_rows:
            capability_real_cost_tracking_audit = real_cost_tracking_rows[0].status
        hosted_dashboard_proof_checklist = "none"
        hosted_dashboard_rows = (
            Storage(db_path).list_recent_hosted_dashboard_proof_checklists(
                limit=1,
            )
        )
        if hosted_dashboard_rows:
            hosted_dashboard_proof_checklist = hosted_dashboard_rows[0].status
        remote_worker_proof_checklist = "none"
        remote_worker_rows = (
            Storage(db_path).list_recent_remote_worker_proof_checklists(
                limit=1,
            )
        )
        if remote_worker_rows:
            remote_worker_proof_checklist = remote_worker_rows[0].status
        autonomous_scheduling_proof_checklist = "none"
        autonomous_scheduling_rows = (
            Storage(db_path).list_recent_autonomous_scheduling_proof_checklists(
                limit=1,
            )
        )
        if autonomous_scheduling_rows:
            autonomous_scheduling_proof_checklist = (
                autonomous_scheduling_rows[0].status
            )
        browser_desktop_adapter_proof_checklist = "none"
        browser_desktop_adapter_rows = (
            Storage(db_path).list_recent_browser_desktop_adapter_proof_checklists(
                limit=1,
            )
        )
        if browser_desktop_adapter_rows:
            browser_desktop_adapter_proof_checklist = (
                browser_desktop_adapter_rows[0].status
            )
        ci_deploy_proof_checklist = "none"
        ci_deploy_rows = (
            Storage(db_path).list_recent_ci_deploy_proof_checklists(
                limit=1,
            )
        )
        if ci_deploy_rows:
            ci_deploy_proof_checklist = ci_deploy_rows[0].status
        budget_enforcement_proof_checklist = "none"
        budget_enforcement_rows = (
            Storage(db_path).list_recent_budget_enforcement_proof_checklists(
                limit=1,
            )
        )
        if budget_enforcement_rows:
            budget_enforcement_proof_checklist = budget_enforcement_rows[0].status
        trust_promotion_proof_checklist = "none"
        trust_promotion_rows = (
            Storage(db_path).list_recent_trust_promotion_proof_checklists(
                limit=1,
            )
        )
        if trust_promotion_rows:
            trust_promotion_proof_checklist = trust_promotion_rows[0].status
        automatic_retry_proof_checklist = "none"
        automatic_retry_rows = (
            Storage(db_path).list_recent_automatic_retry_proof_checklists(
                limit=1,
            )
        )
        if automatic_retry_rows:
            automatic_retry_proof_checklist = automatic_retry_rows[0].status
        real_cost_tracking_proof_checklist = "none"
        real_cost_tracking_proof_rows = (
            Storage(db_path).list_recent_real_cost_tracking_proof_checklists(
                limit=1,
            )
        )
        if real_cost_tracking_proof_rows:
            real_cost_tracking_proof_checklist = (
                real_cost_tracking_proof_rows[0].status
            )
        goal_completion_audit = "none"
        goal_completion_rows = Storage(db_path).list_recent_goal_completion_audits(
            limit=1,
        )
        if goal_completion_rows:
            goal_completion_audit = goal_completion_rows[0].status
        expansion_decision_brief = "none"
        expansion_decision_rows = Storage(
            db_path
        ).list_recent_expansion_decision_briefs(
            limit=1,
        )
        if expansion_decision_rows:
            expansion_decision_brief = expansion_decision_rows[0].status
        expansion_decision_evidence_index = "none"
        expansion_evidence_rows = Storage(
            db_path
        ).list_recent_expansion_decision_evidence_indexes(
            limit=1,
        )
        if expansion_evidence_rows:
            expansion_decision_evidence_index = expansion_evidence_rows[0].status
        expansion_operator_review_checklist = "none"
        expansion_operator_review_rows = Storage(
            db_path
        ).list_recent_expansion_operator_review_checklists(
            limit=1,
        )
        if expansion_operator_review_rows:
            expansion_operator_review_checklist = (
                expansion_operator_review_rows[0].status
            )
        expansion_operator_decision_ledger = "none"
        expansion_operator_decision_rows = Storage(
            db_path
        ).list_recent_expansion_operator_decision_ledgers(
            limit=1,
        )
        if expansion_operator_decision_rows:
            expansion_operator_decision_ledger = (
                expansion_operator_decision_rows[0].status
            )
        expansion_operator_approval_draft = "none"
        expansion_operator_approval_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_drafts(
            limit=1,
        )
        if expansion_operator_approval_rows:
            expansion_operator_approval_draft = (
                expansion_operator_approval_rows[0].status
            )
        expansion_operator_approval_request_review = "none"
        expansion_operator_approval_request_review_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_request_reviews(
            limit=1,
        )
        if expansion_operator_approval_request_review_rows:
            expansion_operator_approval_request_review = (
                expansion_operator_approval_request_review_rows[0].status
            )
        expansion_operator_approval_schema_decision = "none"
        expansion_operator_approval_schema_decision_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_schema_decisions(
            limit=1,
        )
        if expansion_operator_approval_schema_decision_rows:
            expansion_operator_approval_schema_decision = (
                expansion_operator_approval_schema_decision_rows[0].status
            )
        expansion_operator_approval_schema_migration_plan = "none"
        expansion_operator_approval_schema_migration_plan_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_schema_migration_plans(
            limit=1,
        )
        if expansion_operator_approval_schema_migration_plan_rows:
            expansion_operator_approval_schema_migration_plan = (
                expansion_operator_approval_schema_migration_plan_rows[0].status
            )
        expansion_operator_approval_schema_migration_approval_request = "none"
        approval_schema_migration_approval_request_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_schema_migration_approval_requests(
            limit=1,
        )
        if approval_schema_migration_approval_request_rows:
            expansion_operator_approval_schema_migration_approval_request = (
                approval_schema_migration_approval_request_rows[0].status
            )
        expansion_operator_approval_schema_migration_decision_ledger = "none"
        approval_schema_migration_decision_ledger_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_schema_migration_decision_ledgers(
            limit=1,
        )
        if approval_schema_migration_decision_ledger_rows:
            expansion_operator_approval_schema_migration_decision_ledger = (
                approval_schema_migration_decision_ledger_rows[0].status
            )
        expansion_operator_approval_schema_migration_action_checklist = "none"
        approval_schema_migration_action_checklist_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_schema_migration_action_checklists(
            limit=1,
        )
        if approval_schema_migration_action_checklist_rows:
            expansion_operator_approval_schema_migration_action_checklist = (
                approval_schema_migration_action_checklist_rows[0].status
            )
        expansion_operator_approval_schema_migration_selection_packet = "none"
        approval_schema_migration_selection_packet_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_schema_migration_selection_packets(
            limit=1,
        )
        if approval_schema_migration_selection_packet_rows:
            expansion_operator_approval_schema_migration_selection_packet = (
                approval_schema_migration_selection_packet_rows[0].status
            )
        expansion_operator_approval_schema_migration_selection_input_template = "none"
        approval_schema_migration_selection_input_template_rows = Storage(
            db_path
        ).list_recent_expansion_operator_approval_schema_migration_selection_input_templates(
            limit=1,
        )
        if approval_schema_migration_selection_input_template_rows:
            expansion_operator_approval_schema_migration_selection_input_template = (
                approval_schema_migration_selection_input_template_rows[0].status
            )
        operator_approval_schema_migration_application = "none"
        if _table_exists(
            connection,
            "operator_approval_schema_migration_applications",
        ):
            operator_approval_schema_migration_application_rows = Storage(
                db_path
            ).list_recent_operator_approval_schema_migration_applications(
                limit=1,
            )
            if operator_approval_schema_migration_application_rows:
                operator_approval_schema_migration_application = (
                    operator_approval_schema_migration_application_rows[0].status
                )
        operator_approval_request_rows_application = "none"
        if _table_exists(
            connection,
            "operator_approval_request_row_applications",
        ):
            operator_approval_request_rows_application_rows = Storage(
                db_path
            ).list_recent_operator_approval_request_row_applications(
                limit=1,
            )
            if operator_approval_request_rows_application_rows:
                operator_approval_request_rows_application = (
                    operator_approval_request_rows_application_rows[0].status
                )
        operator_approval_request_decisions = "none"
        if _table_exists(
            connection,
            "operator_approval_request_decisions",
        ):
            operator_approval_request_decision_rows = Storage(
                db_path
            ).list_recent_operator_approval_request_decisions(
                limit=1,
            )
            if operator_approval_request_decision_rows:
                operator_approval_request_decisions = (
                    operator_approval_request_decision_rows[0].status
                )
        operator_approval_effect_proposals = "none"
        if _table_exists(connection, "effects"):
            operator_approval_effect_rows = Storage(
                db_path
            ).list_effects_with_idempotency_prefix(
                OPERATOR_APPROVAL_EFFECT_IDEMPOTENCY_PREFIX
            )
            if operator_approval_effect_rows:
                operator_approval_effect_proposals = (
                    OPERATOR_APPROVAL_EFFECT_PROPOSALS_RECORDED
                )
        operator_approval_effect_application = "none"
        if _table_exists(
            connection,
            "operator_approval_effect_applications",
        ):
            operator_approval_effect_application_rows = Storage(
                db_path
            ).list_recent_operator_approval_effect_applications(limit=1)
            if operator_approval_effect_application_rows:
                operator_approval_effect_application = (
                    operator_approval_effect_application_rows[0].status
                )
        capability_activation_tasks = "none"
        if _table_exists(
            connection,
            "capability_activation_task_batches",
        ):
            capability_activation_task_batch_rows = Storage(
                db_path
            ).list_recent_capability_activation_task_batches(limit=1)
            if capability_activation_task_batch_rows:
                capability_activation_tasks = (
                    capability_activation_task_batch_rows[0].status
                )
        capability_activation_contracts = "none"
        if _table_exists(
            connection,
            "capability_activation_contract_batches",
        ):
            capability_activation_contract_batch_rows = Storage(
                db_path
            ).list_recent_capability_activation_contract_batches(limit=1)
            if capability_activation_contract_batch_rows:
                capability_activation_contracts = (
                    capability_activation_contract_batch_rows[0].status
                )
        capability_activation_evidence = "none"
        if _table_exists(
            connection,
            "capability_activation_evidence_batches",
        ):
            capability_activation_evidence_rows = Storage(
                db_path
            ).list_recent_capability_activation_evidence_batches(limit=1)
            if capability_activation_evidence_rows:
                capability_activation_evidence = (
                    capability_activation_evidence_rows[0].status
                )
        capability_activation_decisions = "none"
        if _table_exists(
            connection,
            "capability_activation_decisions",
        ):
            capability_activation_decision_rows = Storage(
                db_path
            ).list_recent_capability_activation_decisions(limit=1)
            if capability_activation_decision_rows:
                capability_activation_decisions = (
                    capability_activation_decision_rows[0].status
                )
        capability_activation_followups = "none"
        if _table_exists(
            connection,
            "capability_activation_followup_task_batches",
        ):
            capability_activation_followup_rows = Storage(
                db_path
            ).list_recent_capability_activation_followup_task_batches(limit=1)
            if capability_activation_followup_rows:
                capability_activation_followups = (
                    capability_activation_followup_rows[0].status
                )
        capability_activation_followup_delegations = "none"
        if _table_exists(
            connection,
            "capability_activation_followup_delegation_batches",
        ):
            capability_activation_followup_delegation_rows = Storage(
                db_path
            ).list_recent_capability_activation_followup_delegation_batches(limit=1)
            if capability_activation_followup_delegation_rows:
                capability_activation_followup_delegations = (
                    capability_activation_followup_delegation_rows[0].status
                )
        handoff_reviews = Storage(db_path).list_recent_handoff_reviews(limit=1)

    handoff_blocked_tasks = 0
    stale_handoffs = 0
    if handoff_reviews:
        handoff_blocked_tasks = handoff_reviews[0].blocked_task_count
        stale_handoffs = handoff_reviews[0].stale_handoff_count

    return [
        f"pending tasks: {task_statuses['pending']}",
        f"waiting approval: {task_statuses['waiting_approval']}",
        f"blocked tasks: {task_statuses['blocked']}",
        f"failed tasks: {task_statuses['failed']}",
        f"pending approvals: {approval_count}",
        f"queue-health hotspots: {queue_health_hotspots}",
        f"handoff blocked tasks: {handoff_blocked_tasks}",
        f"stale handoffs: {stale_handoffs}",
        f"eval-after-change failures: {eval_after_change_failures}",
        f"stable distilled learnings: {stable_distilled_learnings}",
        f"budget/trust posture: {budget_trust_posture}",
        f"dispatch posture history: {dispatch_posture_history}",
        f"dispatch posture staleness: {dispatch_posture_staleness}",
        f"dispatch posture refresh: {dispatch_posture_refresh}",
        f"capability expansion ledger: {capability_expansion_ledger}",
        f"capability readiness review: {capability_readiness_review}",
        f"capability proof gap index: {capability_proof_gap_index}",
        f"capability approval boundary matrix: {capability_approval_boundary_matrix}",
        f"capability evidence collection plan: {capability_evidence_collection_plan}",
        f"capability promotion gate checklist: {capability_promotion_gate_checklist}",
        f"capability promotion decision ledger: {capability_promotion_decision_ledger}",
        f"capability trust promotion audit: {capability_trust_promotion_audit}",
        f"capability automatic retry audit: {capability_automatic_retry_audit}",
        f"capability real cost tracking audit: {capability_real_cost_tracking_audit}",
        f"hosted dashboard proof checklist: {hosted_dashboard_proof_checklist}",
        f"remote worker proof checklist: {remote_worker_proof_checklist}",
        f"autonomous scheduling proof checklist: {autonomous_scheduling_proof_checklist}",
        f"browser desktop adapter proof checklist: {browser_desktop_adapter_proof_checklist}",
        f"ci deploy proof checklist: {ci_deploy_proof_checklist}",
        f"budget enforcement proof checklist: {budget_enforcement_proof_checklist}",
        f"trust promotion proof checklist: {trust_promotion_proof_checklist}",
        f"automatic retry proof checklist: {automatic_retry_proof_checklist}",
        f"real cost tracking proof checklist: {real_cost_tracking_proof_checklist}",
        f"goal completion audit: {goal_completion_audit}",
        f"expansion decision brief: {expansion_decision_brief}",
        f"expansion decision evidence index: {expansion_decision_evidence_index}",
        f"expansion operator review checklist: {expansion_operator_review_checklist}",
        f"expansion operator decision ledger: {expansion_operator_decision_ledger}",
        f"expansion operator approval draft: {expansion_operator_approval_draft}",
        f"expansion operator approval request review: {expansion_operator_approval_request_review}",
        f"expansion operator approval schema decision: {expansion_operator_approval_schema_decision}",
        f"expansion operator approval schema migration plan: {expansion_operator_approval_schema_migration_plan}",
        f"expansion operator approval schema migration approval request: {expansion_operator_approval_schema_migration_approval_request}",
        f"expansion operator approval schema migration decision ledger: {expansion_operator_approval_schema_migration_decision_ledger}",
        f"expansion operator approval schema migration action checklist: {expansion_operator_approval_schema_migration_action_checklist}",
        f"expansion operator approval schema migration selection packet: {expansion_operator_approval_schema_migration_selection_packet}",
        f"expansion operator approval schema migration selection input template: {expansion_operator_approval_schema_migration_selection_input_template}",
        f"operator approval schema migration application: {operator_approval_schema_migration_application}",
        f"operator approval request rows application: {operator_approval_request_rows_application}",
        f"operator approval request decisions: {operator_approval_request_decisions}",
        f"operator approval effect proposals: {operator_approval_effect_proposals}",
        f"operator approval effect application: {operator_approval_effect_application}",
        f"capability activation tasks: {capability_activation_tasks}",
        f"capability activation contracts: {capability_activation_contracts}",
        f"capability activation evidence: {capability_activation_evidence}",
        f"capability activation decisions: {capability_activation_decisions}",
        f"capability activation followups: {capability_activation_followups}",
        f"capability activation followup delegations: {capability_activation_followup_delegations}",
        f"proposed eval candidates: {proposed_eval_candidates}",
        f"active playbooks: {active_playbooks}",
        f"open stuck-task incidents: {stuck_count}",
        f"open incidents: {incident_count}",
    ]


def _count_rows(connection: sqlite3.Connection, table_name: str, where_clause: str) -> int:
    if not _table_exists(connection, table_name):
        return 0
    row = connection.execute(f"select count(*) as count from {table_name} where {where_clause}").fetchone()
    return int(row["count"])


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "select 1 from sqlite_master where type = 'table' and name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
