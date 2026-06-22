from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path

from agent_os.budget_trust import (
    format_risk_counts,
    render_budget_trust_posture_line,
)
from agent_os.capability_expansion import render_capability_expansion_ledger_line
from agent_os.capability_approval_boundary import (
    format_recommended_commands as format_approval_boundary_commands,
    render_capability_approval_boundary_matrix_line,
)
from agent_os.capability_evidence_collection import (
    format_recommended_commands as format_evidence_collection_commands,
    render_capability_evidence_collection_plan_line,
)
from agent_os.capability_promotion_gate import (
    format_recommended_commands as format_promotion_gate_commands,
    render_capability_promotion_gate_checklist_line,
)
from agent_os.capability_promotion_decision import (
    format_recommended_commands as format_promotion_decision_commands,
    render_capability_promotion_decision_ledger_line,
)
from agent_os.capability_trust_promotion import (
    format_recommended_commands as format_trust_promotion_commands,
    render_capability_trust_promotion_audit_line,
)
from agent_os.capability_automatic_retry import (
    format_recommended_commands as format_automatic_retry_commands,
    render_capability_automatic_retry_audit_line,
)
from agent_os.capability_real_cost_tracking import (
    format_recommended_commands as format_real_cost_tracking_commands,
    render_capability_real_cost_tracking_audit_line,
)
from agent_os.hosted_dashboard_proof import (
    format_recommended_commands as format_hosted_dashboard_commands,
    render_hosted_dashboard_proof_checklist_line,
)
from agent_os.remote_worker_proof import (
    format_recommended_commands as format_remote_worker_commands,
    render_remote_worker_proof_checklist_line,
)
from agent_os.autonomous_scheduling_proof import (
    format_recommended_commands as format_autonomous_scheduling_commands,
    render_autonomous_scheduling_proof_checklist_line,
)
from agent_os.browser_desktop_adapter_proof import (
    format_recommended_commands as format_browser_desktop_adapter_commands,
    render_browser_desktop_adapter_proof_checklist_line,
)
from agent_os.ci_deploy_proof import (
    format_recommended_commands as format_ci_deploy_commands,
    render_ci_deploy_proof_checklist_line,
)
from agent_os.budget_enforcement_proof import (
    format_recommended_commands as format_budget_enforcement_commands,
    render_budget_enforcement_proof_checklist_line,
)
from agent_os.trust_promotion_proof import (
    format_recommended_commands as format_trust_promotion_proof_commands,
    render_trust_promotion_proof_checklist_line,
)
from agent_os.automatic_retry_proof import (
    format_recommended_commands as format_automatic_retry_proof_commands,
    render_automatic_retry_proof_checklist_line,
)
from agent_os.real_cost_tracking_proof import (
    format_recommended_commands as format_real_cost_tracking_proof_commands,
    render_real_cost_tracking_proof_checklist_line,
)
from agent_os.goal_completion_audit import (
    format_recommended_commands as format_goal_completion_audit_commands,
    render_goal_completion_audit_line,
)
from agent_os.expansion_decision_brief import render_expansion_decision_brief_line
from agent_os.expansion_decision_evidence_index import (
    render_expansion_decision_evidence_index_line,
)
from agent_os.expansion_operator_review_checklist import (
    format_allowed_actions as format_operator_review_allowed_actions,
    render_expansion_operator_review_checklist_line,
)
from agent_os.expansion_operator_decision_ledger import (
    format_allowed_actions as format_operator_decision_allowed_actions,
    render_expansion_operator_decision_ledger_line,
)
from agent_os.expansion_operator_approval_draft import (
    format_allowed_actions as format_operator_approval_allowed_actions,
    render_expansion_operator_approval_draft_line,
)
from agent_os.expansion_operator_approval_request_review import (
    render_expansion_operator_approval_request_review_line,
)
from agent_os.expansion_operator_approval_schema_decision import (
    render_expansion_operator_approval_schema_decision_line,
)
from agent_os.expansion_operator_approval_schema_migration_plan import (
    render_expansion_operator_approval_schema_migration_plan_line,
)
from agent_os.expansion_operator_approval_schema_migration_approval_request import (
    format_allowed_actions as format_schema_migration_approval_actions,
    render_expansion_operator_approval_schema_migration_approval_request_line,
)
from agent_os.expansion_operator_approval_schema_migration_decision_ledger import (
    format_allowed_actions as format_schema_migration_decision_actions,
    render_expansion_operator_approval_schema_migration_decision_ledger_line,
)
from agent_os.expansion_operator_approval_schema_migration_action_checklist import (
    format_allowed_actions as format_schema_migration_action_actions,
    render_expansion_operator_approval_schema_migration_action_checklist_line,
)
from agent_os.expansion_operator_approval_schema_migration_selection_packet import (
    format_allowed_actions as format_schema_migration_selection_actions,
    render_expansion_operator_approval_schema_migration_selection_packet_line,
)
from agent_os.expansion_operator_approval_schema_migration_selection_input_template import (
    format_allowed_actions as format_schema_migration_input_template_actions,
    render_expansion_operator_approval_schema_migration_selection_input_template_line,
)
from agent_os.operator_approval_schema_migration import (
    render_operator_approval_schema_migration_application_line,
)
from agent_os.operator_approval_request_rows import (
    render_operator_approval_request_rows_application_line,
)
from agent_os.operator_approval_request_decisions import (
    render_operator_approval_request_decision_line,
)
from agent_os.operator_approval_effect_proposals import (
    IDEMPOTENCY_PREFIX as OPERATOR_APPROVAL_EFFECT_IDEMPOTENCY_PREFIX,
    render_operator_approval_effect_proposal_line,
)
from agent_os.operator_approval_effect_application import (
    render_operator_approval_effect_application_line,
)
from agent_os.capability_activation_tasks import (
    render_capability_activation_task_batch_line,
)
from agent_os.capability_activation_contracts import (
    render_capability_activation_contract_batch_line,
)
from agent_os.capability_proof_gap import (
    format_recommended_commands as format_proof_gap_commands,
    render_capability_proof_gap_index_line,
)
from agent_os.capability_readiness import (
    format_recommended_commands as format_readiness_commands,
    render_capability_readiness_review_line,
)
from agent_os.dispatch_posture_history import render_dispatch_posture_history_line
from agent_os.dispatch_posture_refresh import (
    format_recommended_commands,
    render_dispatch_posture_refresh_line,
)
from agent_os.dispatch_posture_staleness import (
    format_optional_age_seconds,
    render_dispatch_posture_staleness_line,
)
from agent_os.eval_after_change import render_eval_after_change_line
from agent_os.handoff_review import (
    render_blocked_task_line,
    render_stale_handoff_line,
)
from agent_os.learning_distillation import (
    render_learning_distillation_line,
    render_stable_learning_line,
)
from agent_os.memory_entries import render_memory_entry_line
from agent_os.skill_entries import render_skill_line
from agent_os.playbooks import render_playbook_line
from agent_os.profile_routing import format_profile_line, format_routing_decision_line
from agent_os.queue_health import (
    DEFAULT_BLOCKED_THRESHOLD,
    DEFAULT_FAILED_THRESHOLD,
    render_queue_health_finding,
)
from agent_os.steering import render_steering_review_line
from agent_os.storage import Storage
from agent_os.subagent_delegation import render_subagent_delegation_line


def generate_static_dashboard(root: Path) -> Path:
    root = root.resolve()
    dashboard_path = root / "docs" / "dashboard.md"
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    db_path = root / ".agent" / "state.db"

    if not db_path.exists():
        dashboard_path.write_text(
            "\n".join(
                [
                    "# Agent System Dashboard",
                    "",
                    "## Queue Health",
                    "",
                    "- state database missing",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return dashboard_path

    storage = Storage(db_path)
    storage.initialize()
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
        runs = connection.execute(
            """
            select id, goal_id, project_id, status, started_at, completed_at, summary_path
            from runs
            order by started_at desc, id desc
            limit 5
            """
        ).fetchall()
        learnings = connection.execute(
            """
            select run_id, project_id, summary, source, created_at
            from learnings
            order by created_at desc, id desc
            limit 5
            """
        ).fetchall()
        evals = connection.execute(
            """
            select name, status, details, created_at
            from eval_results
            order by created_at desc, id desc
            limit 5
            """
        ).fetchall()
        incidents = []
        if _table_exists(connection, "incidents"):
            incidents = connection.execute(
                """
                select *
                from incidents
                order by created_at desc, id desc
                limit 5
                """
            ).fetchall()
        approvals = []
        if _table_exists(connection, "approval_requests"):
            approvals = connection.execute(
                """
                select id, task_id, run_id, goal_id, project_id, task_type,
                       risk_level, status, reason, requested_by, decided_by,
                       decision_note, requested_at, decided_at
                from approval_requests
                order by requested_at desc, id desc
                limit 5
                """
            ).fetchall()
        registered_projects = []
        if _table_exists(connection, "registered_projects"):
            registered_projects = storage.list_registered_projects()
        worktrees = []
        if _table_exists(connection, "worktree_records"):
            worktrees = storage.list_recent_worktree_records(limit=5)
        worktree_cleanups = []
        if _table_exists(connection, "worktree_cleanup_records"):
            worktree_cleanups = storage.list_recent_worktree_cleanup_records(limit=5)
        github_handoffs = []
        if _table_exists(connection, "github_handoff_records"):
            github_handoffs = storage.list_recent_github_handoff_records(limit=5)
        ci_deploy_evidence_records = []
        if _table_exists(connection, "ci_deploy_evidence_records"):
            ci_deploy_evidence_records = (
                storage.list_recent_ci_deploy_evidence_records(limit=5)
            )
        profiles = []
        if _table_exists(connection, "profiles"):
            profiles = storage.list_profiles()
        routing_decisions = []
        if _table_exists(connection, "routing_decisions"):
            routing_decisions = storage.list_recent_routing_decisions(limit=5)
        subagent_delegations = []
        if _table_exists(connection, "subagent_delegations"):
            subagent_delegations = storage.list_recent_subagent_delegations(limit=5)
        steering_reviews = []
        if _table_exists(connection, "steering_reviews"):
            steering_reviews = storage.list_recent_steering_reviews(limit=5)
        effects = []
        operator_approval_effect_proposals = []
        if _table_exists(connection, "effects"):
            effects = storage.list_recent_effects(limit=5)
            operator_approval_effect_proposals = (
                storage.list_effects_with_idempotency_prefix(
                    OPERATOR_APPROVAL_EFFECT_IDEMPOTENCY_PREFIX
                )
            )
        iterations = []
        if _table_exists(connection, "iteration_packets"):
            iterations = connection.execute(
                """
                select id, focus, source_path, source_section, status,
                       packet_path, verification_commands, selection_policy,
                       selection_reason, selected_score, selected_complexity,
                       created_at
                from iteration_packets
                order by created_at desc, id desc
                limit 1
                """
            ).fetchall()
        queue_health_findings = storage.list_queue_health_findings(
            blocked_threshold=DEFAULT_BLOCKED_THRESHOLD,
            failed_threshold=DEFAULT_FAILED_THRESHOLD,
        )
        playbooks = []
        if _table_exists(connection, "playbooks"):
            playbooks = storage.list_recent_playbooks(limit=5)
        eval_candidates = []
        if _table_exists(connection, "eval_candidates"):
            eval_candidates = storage.list_recent_eval_candidates(limit=5)
        handoff_reviews = []
        if _table_exists(connection, "handoff_reviews"):
            handoff_reviews = storage.list_recent_handoff_reviews(limit=1)
        eval_after_change_checks = []
        if _table_exists(connection, "eval_after_change_checks"):
            eval_after_change_checks = storage.list_recent_eval_after_change_checks(
                limit=5,
            )
        learning_distillations = []
        if _table_exists(connection, "learning_distillations"):
            learning_distillations = storage.list_recent_learning_distillations(
                limit=1,
            )
        memory_entries = []
        if _table_exists(connection, "memory_entries"):
            memory_entries = storage.list_memory_entries(status="proposed", limit=5)
        skill_entries = []
        if _table_exists(connection, "skills"):
            skill_entries = storage.list_skills(status="proposed", limit=5)
        budget_trust_reports = []
        if _table_exists(connection, "budget_trust_posture_reports"):
            budget_trust_reports = storage.list_recent_budget_trust_posture_reports(
                limit=1,
            )
        dispatch_posture_history_summaries = []
        if _table_exists(connection, "dispatch_posture_history_summaries"):
            dispatch_posture_history_summaries = (
                storage.list_recent_dispatch_posture_history_summaries(
                    limit=1,
                )
            )
        dispatch_posture_staleness_reviews = []
        if _table_exists(connection, "dispatch_posture_staleness_reviews"):
            dispatch_posture_staleness_reviews = (
                storage.list_recent_dispatch_posture_staleness_reviews(
                    limit=1,
                )
            )
        dispatch_posture_refresh_recommendations = []
        if _table_exists(connection, "dispatch_posture_refresh_recommendations"):
            dispatch_posture_refresh_recommendations = (
                storage.list_recent_dispatch_posture_refresh_recommendations(
                    limit=1,
                )
            )
        capability_expansion_ledgers = []
        if _table_exists(connection, "capability_expansion_ledgers"):
            capability_expansion_ledgers = (
                storage.list_recent_capability_expansion_ledgers(
                    limit=1,
                )
            )
        capability_readiness_reviews = []
        if _table_exists(connection, "capability_readiness_reviews"):
            capability_readiness_reviews = (
                storage.list_recent_capability_readiness_reviews(
                    limit=1,
                )
            )
        capability_proof_gap_indexes = []
        if _table_exists(connection, "capability_proof_gap_indexes"):
            capability_proof_gap_indexes = (
                storage.list_recent_capability_proof_gap_indexes(
                    limit=1,
                )
            )
        capability_approval_boundary_matrices = []
        if _table_exists(connection, "capability_approval_boundary_matrices"):
            capability_approval_boundary_matrices = (
                storage.list_recent_capability_approval_boundary_matrices(
                    limit=1,
                )
            )
        capability_evidence_collection_plans = []
        if _table_exists(connection, "capability_evidence_collection_plans"):
            capability_evidence_collection_plans = (
                storage.list_recent_capability_evidence_collection_plans(
                    limit=1,
                )
            )
        capability_promotion_gate_checklists = []
        if _table_exists(connection, "capability_promotion_gate_checklists"):
            capability_promotion_gate_checklists = (
                storage.list_recent_capability_promotion_gate_checklists(
                    limit=1,
                )
            )
        capability_promotion_decision_ledgers = []
        if _table_exists(connection, "capability_promotion_decision_ledgers"):
            capability_promotion_decision_ledgers = (
                storage.list_recent_capability_promotion_decision_ledgers(
                    limit=1,
                )
            )
        capability_trust_promotion_audits = []
        if _table_exists(connection, "capability_trust_promotion_audits"):
            capability_trust_promotion_audits = (
                storage.list_recent_capability_trust_promotion_audits(
                    limit=1,
                )
            )
        capability_automatic_retry_audits = []
        if _table_exists(connection, "capability_automatic_retry_audits"):
            capability_automatic_retry_audits = (
                storage.list_recent_capability_automatic_retry_audits(
                    limit=1,
                )
            )
        capability_real_cost_tracking_audits = []
        if _table_exists(connection, "capability_real_cost_tracking_audits"):
            capability_real_cost_tracking_audits = (
                storage.list_recent_capability_real_cost_tracking_audits(
                    limit=1,
                )
            )
        hosted_dashboard_proof_checklists = []
        if _table_exists(connection, "hosted_dashboard_proof_checklists"):
            hosted_dashboard_proof_checklists = (
                storage.list_recent_hosted_dashboard_proof_checklists(
                    limit=1,
                )
            )
        remote_worker_proof_checklists = []
        if _table_exists(connection, "remote_worker_proof_checklists"):
            remote_worker_proof_checklists = (
                storage.list_recent_remote_worker_proof_checklists(
                    limit=1,
                )
            )
        autonomous_scheduling_proof_checklists = []
        if _table_exists(connection, "autonomous_scheduling_proof_checklists"):
            autonomous_scheduling_proof_checklists = (
                storage.list_recent_autonomous_scheduling_proof_checklists(
                    limit=1,
                )
            )
        browser_desktop_adapter_proof_checklists = []
        if _table_exists(connection, "browser_desktop_adapter_proof_checklists"):
            browser_desktop_adapter_proof_checklists = (
                storage.list_recent_browser_desktop_adapter_proof_checklists(
                    limit=1,
                )
            )
        ci_deploy_proof_checklists = []
        if _table_exists(connection, "ci_deploy_proof_checklists"):
            ci_deploy_proof_checklists = (
                storage.list_recent_ci_deploy_proof_checklists(
                    limit=1,
                )
            )
        budget_enforcement_proof_checklists = []
        if _table_exists(connection, "budget_enforcement_proof_checklists"):
            budget_enforcement_proof_checklists = (
                storage.list_recent_budget_enforcement_proof_checklists(
                    limit=1,
                )
            )
        trust_promotion_proof_checklists = []
        if _table_exists(connection, "trust_promotion_proof_checklists"):
            trust_promotion_proof_checklists = (
                storage.list_recent_trust_promotion_proof_checklists(
                    limit=1,
                )
            )
        automatic_retry_proof_checklists = []
        if _table_exists(connection, "automatic_retry_proof_checklists"):
            automatic_retry_proof_checklists = (
                storage.list_recent_automatic_retry_proof_checklists(
                    limit=1,
                )
            )
        real_cost_tracking_proof_checklists = []
        if _table_exists(connection, "real_cost_tracking_proof_checklists"):
            real_cost_tracking_proof_checklists = (
                storage.list_recent_real_cost_tracking_proof_checklists(
                    limit=1,
                )
            )
        goal_completion_audits = []
        if _table_exists(connection, "goal_completion_audits"):
            goal_completion_audits = storage.list_recent_goal_completion_audits(
                limit=1
            )
        expansion_decision_briefs = []
        if _table_exists(connection, "expansion_decision_briefs"):
            expansion_decision_briefs = storage.list_recent_expansion_decision_briefs(
                limit=1
            )
        expansion_decision_evidence_indexes = []
        if _table_exists(connection, "expansion_decision_evidence_indexes"):
            expansion_decision_evidence_indexes = (
                storage.list_recent_expansion_decision_evidence_indexes(limit=1)
            )
        expansion_operator_review_checklists = []
        if _table_exists(connection, "expansion_operator_review_checklists"):
            expansion_operator_review_checklists = (
                storage.list_recent_expansion_operator_review_checklists(limit=1)
            )
        expansion_operator_decision_ledgers = []
        if _table_exists(connection, "expansion_operator_decision_ledgers"):
            expansion_operator_decision_ledgers = (
                storage.list_recent_expansion_operator_decision_ledgers(limit=1)
            )
        expansion_operator_approval_drafts = []
        if _table_exists(connection, "expansion_operator_approval_drafts"):
            expansion_operator_approval_drafts = (
                storage.list_recent_expansion_operator_approval_drafts(limit=1)
            )
        expansion_operator_approval_request_reviews = []
        if _table_exists(connection, "expansion_operator_approval_request_reviews"):
            expansion_operator_approval_request_reviews = (
                storage.list_recent_expansion_operator_approval_request_reviews(
                    limit=1
                )
            )
        expansion_operator_approval_schema_decisions = []
        if _table_exists(connection, "expansion_operator_approval_schema_decisions"):
            expansion_operator_approval_schema_decisions = (
                storage.list_recent_expansion_operator_approval_schema_decisions(
                    limit=1
                )
            )
        expansion_operator_approval_schema_migration_plans = []
        if _table_exists(
            connection,
            "expansion_operator_approval_schema_migration_plans",
        ):
            expansion_operator_approval_schema_migration_plans = (
                storage.list_recent_expansion_operator_approval_schema_migration_plans(
                limit=1,
            )
            )
        expansion_operator_approval_schema_migration_approval_requests = []
        if _table_exists(
            connection,
            "expansion_operator_approval_schema_migration_approval_requests",
        ):
            expansion_operator_approval_schema_migration_approval_requests = (
                storage.list_recent_expansion_operator_approval_schema_migration_approval_requests(
                limit=1,
            )
            )
        expansion_operator_approval_schema_migration_decision_ledgers = []
        if _table_exists(
            connection,
            "expansion_operator_approval_schema_migration_decision_ledgers",
        ):
            expansion_operator_approval_schema_migration_decision_ledgers = (
                storage.list_recent_expansion_operator_approval_schema_migration_decision_ledgers(
                limit=1,
            )
            )
        expansion_operator_approval_schema_migration_action_checklists = []
        if _table_exists(
            connection,
            "expansion_operator_approval_schema_migration_action_checklists",
        ):
            expansion_operator_approval_schema_migration_action_checklists = (
                storage.list_recent_expansion_operator_approval_schema_migration_action_checklists(
                limit=1,
            )
            )
        expansion_operator_approval_schema_migration_selection_packets = []
        if _table_exists(
            connection,
            "expansion_operator_approval_schema_migration_selection_packets",
        ):
            expansion_operator_approval_schema_migration_selection_packets = (
                storage.list_recent_expansion_operator_approval_schema_migration_selection_packets(
                limit=1,
            )
            )
        expansion_operator_approval_schema_migration_selection_input_templates = []
        if _table_exists(
            connection,
            "expansion_operator_approval_schema_migration_selection_input_templates",
        ):
            expansion_operator_approval_schema_migration_selection_input_templates = (
                storage.list_recent_expansion_operator_approval_schema_migration_selection_input_templates(
                limit=1,
            )
            )
        operator_approval_schema_migration_applications = []
        if _table_exists(
            connection,
            "operator_approval_schema_migration_applications",
        ):
            operator_approval_schema_migration_applications = (
                storage.list_recent_operator_approval_schema_migration_applications(
                    limit=1,
                )
            )
        operator_approval_request_row_applications = []
        if _table_exists(
            connection,
            "operator_approval_request_row_applications",
        ):
            operator_approval_request_row_applications = (
                storage.list_recent_operator_approval_request_row_applications(
                    limit=1,
                )
            )
        operator_approval_request_decisions = []
        if _table_exists(
            connection,
            "operator_approval_request_decisions",
        ):
            operator_approval_request_decisions = (
                storage.list_recent_operator_approval_request_decisions(limit=1)
            )
        operator_approval_effect_applications = []
        if _table_exists(
            connection,
            "operator_approval_effect_applications",
        ):
            operator_approval_effect_applications = (
                storage.list_recent_operator_approval_effect_applications(limit=1)
            )
        capability_activation_task_batches = []
        if _table_exists(
            connection,
            "capability_activation_task_batches",
        ):
            capability_activation_task_batches = (
                storage.list_recent_capability_activation_task_batches(limit=1)
            )
        capability_activation_contract_batches = []
        if _table_exists(
            connection,
            "capability_activation_contract_batches",
        ):
            capability_activation_contract_batches = (
                storage.list_recent_capability_activation_contract_batches(limit=1)
            )

    statuses = [
        "pending",
        "waiting_approval",
        "claimed",
        "running",
        "verifying",
        "completed",
        "blocked",
        "failed",
    ]
    active_count = sum(task_statuses[status] for status in ["claimed", "running", "verifying"])
    attention_count = (
        task_statuses["waiting_approval"] + task_statuses["blocked"] + task_statuses["failed"]
    )
    incident_statuses = Counter(incident["status"] for incident in incidents)
    approval_statuses = Counter(approval["status"] for approval in approvals)
    playbook_statuses = Counter(playbook.status for playbook in playbooks)
    eval_candidate_statuses = Counter(candidate.status for candidate in eval_candidates)
    latest_handoff_review = handoff_reviews[0] if handoff_reviews else None
    latest_learning_distillation = (
        learning_distillations[0] if learning_distillations else None
    )
    latest_budget_trust_report = (
        budget_trust_reports[0] if budget_trust_reports else None
    )
    latest_dispatch_posture_history = (
        dispatch_posture_history_summaries[0]
        if dispatch_posture_history_summaries
        else None
    )
    latest_dispatch_posture_staleness = (
        dispatch_posture_staleness_reviews[0]
        if dispatch_posture_staleness_reviews
        else None
    )
    latest_dispatch_posture_refresh = (
        dispatch_posture_refresh_recommendations[0]
        if dispatch_posture_refresh_recommendations
        else None
    )
    latest_capability_expansion_ledger = (
        capability_expansion_ledgers[0]
        if capability_expansion_ledgers
        else None
    )
    latest_capability_readiness_review = (
        capability_readiness_reviews[0]
        if capability_readiness_reviews
        else None
    )
    latest_capability_proof_gap_index = (
        capability_proof_gap_indexes[0]
        if capability_proof_gap_indexes
        else None
    )
    latest_capability_approval_boundary_matrix = (
        capability_approval_boundary_matrices[0]
        if capability_approval_boundary_matrices
        else None
    )
    latest_capability_evidence_collection_plan = (
        capability_evidence_collection_plans[0]
        if capability_evidence_collection_plans
        else None
    )
    latest_capability_promotion_gate_checklist = (
        capability_promotion_gate_checklists[0]
        if capability_promotion_gate_checklists
        else None
    )
    latest_capability_promotion_decision_ledger = (
        capability_promotion_decision_ledgers[0]
        if capability_promotion_decision_ledgers
        else None
    )
    latest_capability_trust_promotion_audit = (
        capability_trust_promotion_audits[0]
        if capability_trust_promotion_audits
        else None
    )
    latest_capability_automatic_retry_audit = (
        capability_automatic_retry_audits[0]
        if capability_automatic_retry_audits
        else None
    )
    latest_capability_real_cost_tracking_audit = (
        capability_real_cost_tracking_audits[0]
        if capability_real_cost_tracking_audits
        else None
    )
    latest_hosted_dashboard_proof_checklist = (
        hosted_dashboard_proof_checklists[0]
        if hosted_dashboard_proof_checklists
        else None
    )
    latest_remote_worker_proof_checklist = (
        remote_worker_proof_checklists[0]
        if remote_worker_proof_checklists
        else None
    )
    latest_autonomous_scheduling_proof_checklist = (
        autonomous_scheduling_proof_checklists[0]
        if autonomous_scheduling_proof_checklists
        else None
    )
    latest_browser_desktop_adapter_proof_checklist = (
        browser_desktop_adapter_proof_checklists[0]
        if browser_desktop_adapter_proof_checklists
        else None
    )
    latest_ci_deploy_proof_checklist = (
        ci_deploy_proof_checklists[0]
        if ci_deploy_proof_checklists
        else None
    )
    latest_budget_enforcement_proof_checklist = (
        budget_enforcement_proof_checklists[0]
        if budget_enforcement_proof_checklists
        else None
    )
    latest_trust_promotion_proof_checklist = (
        trust_promotion_proof_checklists[0]
        if trust_promotion_proof_checklists
        else None
    )
    latest_automatic_retry_proof_checklist = (
        automatic_retry_proof_checklists[0]
        if automatic_retry_proof_checklists
        else None
    )
    latest_real_cost_tracking_proof_checklist = (
        real_cost_tracking_proof_checklists[0]
        if real_cost_tracking_proof_checklists
        else None
    )
    latest_goal_completion_audit = (
        goal_completion_audits[0] if goal_completion_audits else None
    )
    latest_expansion_decision_brief = (
        expansion_decision_briefs[0] if expansion_decision_briefs else None
    )
    latest_expansion_decision_evidence_index = (
        expansion_decision_evidence_indexes[0]
        if expansion_decision_evidence_indexes
        else None
    )
    latest_expansion_operator_review_checklist = (
        expansion_operator_review_checklists[0]
        if expansion_operator_review_checklists
        else None
    )
    latest_expansion_operator_decision_ledger = (
        expansion_operator_decision_ledgers[0]
        if expansion_operator_decision_ledgers
        else None
    )
    latest_expansion_operator_approval_draft = (
        expansion_operator_approval_drafts[0]
        if expansion_operator_approval_drafts
        else None
    )
    latest_expansion_operator_approval_request_review = (
        expansion_operator_approval_request_reviews[0]
        if expansion_operator_approval_request_reviews
        else None
    )
    latest_expansion_operator_approval_schema_decision = (
        expansion_operator_approval_schema_decisions[0]
        if expansion_operator_approval_schema_decisions
        else None
    )
    latest_expansion_operator_approval_schema_migration_plan = (
        expansion_operator_approval_schema_migration_plans[0]
        if expansion_operator_approval_schema_migration_plans
        else None
    )
    latest_expansion_operator_approval_schema_migration_approval_request = (
        expansion_operator_approval_schema_migration_approval_requests[0]
        if expansion_operator_approval_schema_migration_approval_requests
        else None
    )
    latest_expansion_operator_approval_schema_migration_decision_ledger = (
        expansion_operator_approval_schema_migration_decision_ledgers[0]
        if expansion_operator_approval_schema_migration_decision_ledgers
        else None
    )
    latest_expansion_operator_approval_schema_migration_action_checklist = (
        expansion_operator_approval_schema_migration_action_checklists[0]
        if expansion_operator_approval_schema_migration_action_checklists
        else None
    )
    latest_expansion_operator_approval_schema_migration_selection_packet = (
        expansion_operator_approval_schema_migration_selection_packets[0]
        if expansion_operator_approval_schema_migration_selection_packets
        else None
    )
    latest_expansion_operator_approval_schema_migration_selection_input_template = (
        expansion_operator_approval_schema_migration_selection_input_templates[0]
        if expansion_operator_approval_schema_migration_selection_input_templates
        else None
    )
    latest_operator_approval_schema_migration_application = (
        operator_approval_schema_migration_applications[0]
        if operator_approval_schema_migration_applications
        else None
    )
    latest_operator_approval_request_row_application = (
        operator_approval_request_row_applications[0]
        if operator_approval_request_row_applications
        else None
    )
    latest_operator_approval_request_decision = (
        operator_approval_request_decisions[0]
        if operator_approval_request_decisions
        else None
    )
    latest_operator_approval_effect_application = (
        operator_approval_effect_applications[0]
        if operator_approval_effect_applications
        else None
    )
    latest_capability_activation_task_batch = (
        capability_activation_task_batches[0]
        if capability_activation_task_batches
        else None
    )
    latest_capability_activation_contract_batch = (
        capability_activation_contract_batches[0]
        if capability_activation_contract_batches
        else None
    )
    eval_after_change_statuses = Counter(
        check.status for check in eval_after_change_checks
    )
    stuck_incidents = [
        incident for incident in incidents if incident["incident_type"] == "task_stuck"
    ]
    stuck_statuses = Counter(incident["status"] for incident in stuck_incidents)
    active_runs = [
        run
        for run in runs
        if run["status"] in {"accepted", "running", "waiting_approval"}
    ]
    pending_approvals = [
        approval for approval in approvals if approval["status"] == "pending"
    ]
    approved_approval_ids = {
        approval["id"] for approval in approvals if approval["status"] == "approved"
    }
    approved_commit_effects = [
        effect
        for effect in effects
        if effect.effect_type == "local_git_commit"
        and effect.status == "awaiting_approval"
        and effect.required_approval_id in approved_approval_ids
    ]
    handed_off_effect_ids = {handoff.effect_id for handoff in github_handoffs}
    committed_effects_without_handoff = [
        effect
        for effect in effects
        if effect.effect_type == "local_git_commit"
        and effect.status == "committed"
        and effect.id not in handed_off_effect_ids
    ]
    open_incidents = [incident for incident in incidents if incident["status"] == "open"]

    lines = [
        "# Agent System Dashboard",
        "",
        "## Operator Cockpit",
        "",
        "### Active Goals/Runs",
        "",
    ]
    if active_runs:
        for run in active_runs:
            lines.append(
                f"- {run['id']}: {run['status']} project={run['project_id']} "
                f"goal={run['goal_id']} summary={_relative_to_root(root, run['summary_path'])}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Registered Projects", ""])
    if registered_projects:
        for project in registered_projects:
            allowed_roots = ",".join(project.allowed_write_roots)
            lines.append(
                f"- {project.name}: root={project.root_path} "
                f"test={project.default_test_command} allowed_write_roots={allowed_roots}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Approval Inbox", ""])
    if pending_approvals:
        for approval in pending_approvals:
            lines.append(
                f"- {approval['id']}: task={approval['task_id']} "
                f"run={approval['run_id']} project={approval['project_id']} "
                f"type={approval['task_type']} risk={approval['risk_level']} "
                f"reason={approval['reason']}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Proposed Effects", ""])
    if effects:
        for effect in effects:
            lines.append(
                f"- {effect.id}: {effect.effect_type} status={effect.status} "
                f"approval={effect.required_approval_id or 'none'} "
                f"project={effect.project_id} target={_relative_to_root(root, effect.target)} "
                f"evidence={_relative_to_root(root, effect.evidence_path)}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Recent Commits/Effects", ""])
    if effects:
        for effect in effects:
            committed_at = effect.committed_at or "not_committed"
            commit_sha = effect.result_json.get("commit_sha", "none")
            lines.append(
                f"- {effect.id}: {effect.effect_type} status={effect.status} "
                f"committed_at={committed_at} commit={commit_sha}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Incidents", ""])
    if open_incidents:
        for incident in open_incidents:
            lines.append(
                f"- {incident['id']}: {incident['severity']} "
                f"type={incident['incident_type']} task={incident['task_id']} "
                f"evidence={_relative_to_root(root, incident['evidence_path'])}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Verification Status", ""])
    if effects:
        for effect in effects:
            verification = _effect_verification_status(root, storage, effect)
            lines.append(
                f"- {effect.id}: {verification['status']} "
                f"method={verification['method']} "
                f"command_exit={verification['command_exit_code']} "
                f"tests_exit={verification['tests_exit_code']} "
                f"evidence={verification['path']}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Recent Worktrees", ""])
    if worktrees:
        for worktree in worktrees:
            lines.append(
                f"- {worktree.id}: project={worktree.project_id} "
                f"run={worktree.run_id} branch={worktree.branch_name} "
                f"base={worktree.base_commit} path={_relative_to_root(root, worktree.worktree_path)}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Worktree Cleanup", ""])
    if worktree_cleanups:
        for cleanup in worktree_cleanups:
            lines.append(
                f"- {cleanup.id}: status={cleanup.status} "
                f"reason={cleanup.cleanup_reason} effect={cleanup.effect_id} "
                f"path={_relative_to_root(root, cleanup.worktree_path)} "
                f"evidence={_relative_to_root(root, cleanup.evidence_path)}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### GitHub Handoffs", ""])
    if github_handoffs:
        for handoff in github_handoffs:
            lines.append(
                f"- {handoff.id}: status={handoff.status} effect={handoff.effect_id} "
                f"branch={handoff.branch_name} commit={handoff.commit_sha} "
                f"push=`{handoff.push_command}` "
                f"draft_pr=`{handoff.draft_pr_command}` "
                f"evidence={_relative_to_root(root, handoff.evidence_path)}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### CI/Deploy Evidence", ""])
    if ci_deploy_evidence_records:
        for record in ci_deploy_evidence_records:
            lines.append(
                f"- {record.id}: status={record.status} provider={record.provider} "
                f"handoff={record.github_handoff_id} commit={record.commit_sha} "
                f"external_run={record.external_run_id} url={record.external_url} "
                f"network_actions_taken={record.result_json.get('network_actions_taken', 'unknown')} "
                f"evidence={_relative_to_root(root, record.evidence_path)}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "### Profile Routing", ""])
    if profiles:
        lines.append(f"- enabled_profiles: {len(profiles)}")
        for profile in profiles:
            lines.append(f"- profile {format_profile_line(profile)}")
    else:
        lines.append("- enabled_profiles: 0")
    if routing_decisions:
        lines.append("- recent_decisions:")
        for decision in routing_decisions:
            lines.append(f"- {format_routing_decision_line(decision)}")
    else:
        lines.append("- recent_decisions: none")

    lines.extend(["", "### Subagent Delegations", ""])
    if subagent_delegations:
        for delegation in subagent_delegations:
            lines.append(f"- {render_subagent_delegation_line(delegation)}")
    else:
        lines.append("- none")

    lines.extend(["", "## Steering Reviews", ""])
    if steering_reviews:
        for review in steering_reviews:
            lines.append(render_steering_review_line(review))
    else:
        lines.append("- none")

    lines.extend(["", "### Next Recommended Action", ""])
    if pending_approvals:
        approval = pending_approvals[0]
        lines.append(
            f"- Review approval `{approval['id']}` and its run evidence before "
            "deciding with `python3 -m agent_os.cli approve <approval_id> "
            "--decided-by operator --note \"...\"`."
        )
    elif approved_commit_effects:
        effect = approved_commit_effects[0]
        lines.append(
            f"- Run `python3 -m agent_os.cli commit-approved {effect.required_approval_id}` "
            f"to create the verified local commit for effect `{effect.id}`."
        )
    elif committed_effects_without_handoff:
        effect = committed_effects_without_handoff[0]
        lines.append(
            f"- Run `python3 -m agent_os.cli github-handoff {effect.id}` to prepare "
            "operator push and draft PR commands without mutating GitHub."
        )
    elif effects:
        lines.append("- Review recent proposed effects and regenerate the dashboard after decisions.")
    else:
        lines.append("- Run `python3 -m agent_os.cli iterate` for the next local work packet.")

    lines.extend(
        [
            "",
            "## Queue Health",
            "",
        ]
    )
    for status in statuses:
        lines.append(f"- {status}: {task_statuses[status]}")
    lines.extend(
        [
            f"- active: {active_count}",
            f"- needs_attention: {attention_count}",
            "",
            "## Iteration Loop",
            "",
        ]
    )

    if iterations:
        iteration = iterations[0]
        lines.extend(
            [
                f"- status: {iteration['status']}",
                f"- focus: {iteration['focus']}",
                f"- source: {iteration['source_path']}#{iteration['source_section']}",
                f"- packet: {iteration['packet_path']}",
                f"- created_at: {iteration['created_at']}",
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Simplicity Guardrail", ""])
    if iterations:
        iteration = iterations[0]
        lines.extend(
            [
                f"- policy: {iteration['selection_policy']}",
                f"- reason: {iteration['selection_reason']}",
                f"- selected_score: {iteration['selected_score']}",
                f"- selected_complexity: {iteration['selected_complexity']}",
                f"- selected_focus: {iteration['focus']}",
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Operator Approval Schema Decision", ""])
    if latest_expansion_operator_approval_schema_decision is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_operator_approval_schema_decision.status}",
                f"- source_review: {latest_expansion_operator_approval_schema_decision.source_review_id}",
                f"- source_status: {latest_expansion_operator_approval_schema_decision.source_review_status}",
                f"- source_draft: {latest_expansion_operator_approval_schema_decision.source_draft_id}",
                f"- source_ledger: {latest_expansion_operator_approval_schema_decision.source_ledger_id}",
                f"- source_checklist: {latest_expansion_operator_approval_schema_decision.source_checklist_id}",
                f"- source_index: {latest_expansion_operator_approval_schema_decision.source_index_id}",
                f"- source_brief: {latest_expansion_operator_approval_schema_decision.source_brief_id}",
                f"- source_audit: {latest_expansion_operator_approval_schema_decision.source_audit_id}",
                f"- affected_requests: {latest_expansion_operator_approval_schema_decision.affected_request_count}",
                f"- schema_gaps: {latest_expansion_operator_approval_schema_decision.schema_gap_count}",
                f"- missing_fields: {latest_expansion_operator_approval_schema_decision.missing_field_count}",
                f"- external_requests: {latest_expansion_operator_approval_schema_decision.external_request_count}",
                f"- capability_requests: {latest_expansion_operator_approval_schema_decision.capability_request_count}",
                f"- decision_options: {latest_expansion_operator_approval_schema_decision.decision_option_count}",
                f"- recommended_option: {latest_expansion_operator_approval_schema_decision.recommended_option}",
                f"- rejected_options: {latest_expansion_operator_approval_schema_decision.rejected_option_count}",
                f"- schema_objects: {latest_expansion_operator_approval_schema_decision.schema_object_count}",
                f"- migration_applied: {latest_expansion_operator_approval_schema_decision.migration_applied_count}",
                f"- created_approval_requests: {latest_expansion_operator_approval_schema_decision.created_approval_request_count}",
                f"- existing_approval_requests: {latest_expansion_operator_approval_schema_decision.existing_approval_request_count}",
                f"- recommended_next_step: {latest_expansion_operator_approval_schema_decision.recommended_next_step}",
                f"- report: {latest_expansion_operator_approval_schema_decision.report_path}",
                "",
                render_expansion_operator_approval_schema_decision_line(
                    latest_expansion_operator_approval_schema_decision
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Operator Approval Schema Migration Plan", ""])
    if latest_expansion_operator_approval_schema_migration_plan is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_operator_approval_schema_migration_plan.status}",
                f"- source_decision: {latest_expansion_operator_approval_schema_migration_plan.source_decision_id}",
                f"- source_status: {latest_expansion_operator_approval_schema_migration_plan.source_decision_status}",
                f"- source_review: {latest_expansion_operator_approval_schema_migration_plan.source_review_id}",
                f"- source_review_status: {latest_expansion_operator_approval_schema_migration_plan.source_review_status}",
                f"- source_draft: {latest_expansion_operator_approval_schema_migration_plan.source_draft_id}",
                f"- source_ledger: {latest_expansion_operator_approval_schema_migration_plan.source_ledger_id}",
                f"- source_checklist: {latest_expansion_operator_approval_schema_migration_plan.source_checklist_id}",
                f"- source_index: {latest_expansion_operator_approval_schema_migration_plan.source_index_id}",
                f"- source_brief: {latest_expansion_operator_approval_schema_migration_plan.source_brief_id}",
                f"- source_audit: {latest_expansion_operator_approval_schema_migration_plan.source_audit_id}",
                f"- recommended_option: {latest_expansion_operator_approval_schema_migration_plan.recommended_option}",
                f"- target_table: {latest_expansion_operator_approval_schema_migration_plan.target_table}",
                f"- affected_requests: {latest_expansion_operator_approval_schema_migration_plan.affected_request_count}",
                f"- schema_gaps: {latest_expansion_operator_approval_schema_migration_plan.schema_gap_count}",
                f"- missing_fields: {latest_expansion_operator_approval_schema_migration_plan.missing_field_count}",
                f"- external_requests: {latest_expansion_operator_approval_schema_migration_plan.external_request_count}",
                f"- capability_requests: {latest_expansion_operator_approval_schema_migration_plan.capability_request_count}",
                f"- planned_columns: {latest_expansion_operator_approval_schema_migration_plan.planned_column_count}",
                f"- planned_indexes: {latest_expansion_operator_approval_schema_migration_plan.planned_index_count}",
                f"- migration_steps: {latest_expansion_operator_approval_schema_migration_plan.migration_step_count}",
                f"- migration_applied: {latest_expansion_operator_approval_schema_migration_plan.migration_applied_count}",
                f"- table_created: {latest_expansion_operator_approval_schema_migration_plan.table_created_count}",
                f"- operator_approval_rows_created: {latest_expansion_operator_approval_schema_migration_plan.operator_approval_row_count}",
                f"- approval_requests_created: {latest_expansion_operator_approval_schema_migration_plan.created_approval_request_count}",
                f"- existing_approval_requests: {latest_expansion_operator_approval_schema_migration_plan.existing_approval_request_count}",
                f"- recommended_next_step: {latest_expansion_operator_approval_schema_migration_plan.recommended_next_step}",
                f"- report: {latest_expansion_operator_approval_schema_migration_plan.report_path}",
                "",
                render_expansion_operator_approval_schema_migration_plan_line(
                    latest_expansion_operator_approval_schema_migration_plan
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Request Decisions",
            "",
        ]
    )
    if latest_operator_approval_request_decision is not None:
        decision = latest_operator_approval_request_decision
        lines.extend(
            [
                f"- status: {decision.status}",
                f"- source_row_application: {decision.source_row_application_id}",
                f"- source_status: {decision.source_row_application_status}",
                f"- source_draft: {decision.source_draft_id}",
                f"- source_schema_application: {decision.source_schema_application_id}",
                f"- source_ledger: {decision.source_ledger_id}",
                f"- source_checklist: {decision.source_checklist_id}",
                f"- source_index: {decision.source_index_id}",
                f"- source_brief: {decision.source_brief_id}",
                f"- source_audit: {decision.source_audit_id}",
                f"- operator_id: {decision.operator_id}",
                f"- selected_action: {decision.selected_action}",
                f"- pending_requests_before: {decision.pending_request_count_before}",
                f"- decisions_recorded: {decision.decision_count}",
                f"- approved_decisions: {decision.approved_decision_count}",
                f"- deferred_decisions: {decision.deferred_decision_count}",
                f"- more_evidence_decisions: {decision.more_evidence_decision_count}",
                f"- pending_requests_after: {decision.pending_request_count_after}",
                f"- existing_decisions: {decision.existing_decision_count}",
                f"- approval_requests_created: {decision.created_approval_request_count}",
                f"- external_requests: {decision.external_request_count}",
                f"- capability_requests: {decision.capability_request_count}",
                f"- report: {decision.report_path}",
                "",
                render_operator_approval_request_decision_line(decision),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Effect Proposals",
            "",
        ]
    )
    if operator_approval_effect_proposals:
        external_effect_count = sum(
            1
            for effect in operator_approval_effect_proposals
            if effect.effect_type == "operator_external_decision"
        )
        capability_effect_count = sum(
            1
            for effect in operator_approval_effect_proposals
            if effect.effect_type == "operator_capability_proposal"
        )
        latest_effect = operator_approval_effect_proposals[0]
        lines.extend(
            [
                "- status: operator_approval_effect_proposals_recorded",
                f"- source_decision: {latest_effect.run_id}",
                f"- approved_operator_requests: {len(operator_approval_effect_proposals)}",
                f"- effect_proposals_created: {len(operator_approval_effect_proposals)}",
                f"- existing_effect_proposals: {len(operator_approval_effect_proposals)}",
                f"- external_effect_proposals: {external_effect_count}",
                f"- capability_effect_proposals: {capability_effect_count}",
                "- legacy_approval_requests_created: 0",
                "- activation_actions_taken: 0",
                f"- report: {latest_effect.evidence_path}",
                "",
            ]
        )
        lines.extend(
            render_operator_approval_effect_proposal_line(effect)
            for effect in operator_approval_effect_proposals
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Effect Application",
            "",
        ]
    )
    if latest_operator_approval_effect_application is not None:
        application = latest_operator_approval_effect_application
        lines.extend(
            [
                f"- status: {application.status}",
                f"- operator_id: {application.operator_id}",
                f"- proposed_effects: {application.proposed_effect_count}",
                f"- effects_applied: {application.applied_effect_count}",
                f"- existing_applied_effects: {application.existing_applied_effect_count}",
                f"- external_effects_applied: {application.external_effect_count}",
                f"- capability_effects_applied: {application.capability_effect_count}",
                f"- legacy_approval_requests_created: {application.legacy_approval_request_count}",
                f"- activation_actions_taken: {application.activation_action_count}",
                f"- report: {application.report_path}",
                "",
                render_operator_approval_effect_application_line(application),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Capability Activation Tasks",
            "",
        ]
    )
    if latest_capability_activation_task_batch is not None:
        batch = latest_capability_activation_task_batch
        lines.extend(
            [
                f"- status: {batch.status}",
                f"- source_application: {batch.source_application_id}",
                f"- goal: {batch.goal_id}",
                f"- applied_capability_effects: {batch.applied_capability_effect_count}",
                f"- tasks_created: {batch.task_count}",
                f"- existing_activation_tasks: {batch.existing_task_count}",
                f"- activation_actions_taken: {batch.activation_action_count}",
                f"- report: {batch.report_path}",
                "",
                render_capability_activation_task_batch_line(batch),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Capability Activation Contracts",
            "",
        ]
    )
    if latest_capability_activation_contract_batch is not None:
        batch = latest_capability_activation_contract_batch
        lines.extend(
            [
                f"- status: {batch.status}",
                f"- source_task_batch: {batch.source_task_batch_id}",
                f"- activation_tasks: {batch.activation_task_count}",
                f"- contracts_created: {batch.contract_count}",
                f"- existing_contracts: {batch.existing_contract_count}",
                f"- approval_requests_created: {batch.created_approval_request_count}",
                f"- activation_actions_taken: {batch.activation_action_count}",
                f"- report: {batch.report_path}",
                "",
                render_capability_activation_contract_batch_line(batch),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Schema Migration Approval Request",
            "",
        ]
    )
    if latest_expansion_operator_approval_schema_migration_approval_request is not None:
        request = latest_expansion_operator_approval_schema_migration_approval_request
        lines.extend(
            [
                f"- status: {request.status}",
                f"- source_plan: {request.source_plan_id}",
                f"- source_status: {request.source_plan_status}",
                f"- source_decision: {request.source_decision_id}",
                f"- source_decision_status: {request.source_decision_status}",
                f"- source_review: {request.source_review_id}",
                f"- source_review_status: {request.source_review_status}",
                f"- target_table: {request.target_table}",
                f"- planned_columns: {request.planned_column_count}",
                f"- planned_indexes: {request.planned_index_count}",
                f"- migration_steps: {request.migration_step_count}",
                f"- affected_requests: {request.affected_request_count}",
                f"- schema_gaps: {request.schema_gap_count}",
                f"- request_count: {request.request_count}",
                f"- approval_boundary: {request.approval_boundary}",
                f"- requested_action: {request.requested_action}",
                f"- allowed_actions: {format_schema_migration_approval_actions(request.allowed_actions)}",
                f"- migration_applied: {request.migration_applied_count}",
                f"- table_created: {request.table_created_count}",
                f"- operator_approval_rows_created: {request.operator_approval_row_count}",
                f"- approval_requests_created: {request.created_approval_request_count}",
                f"- existing_approval_requests: {request.existing_approval_request_count}",
                f"- recommended_next_step: {request.recommended_next_step}",
                f"- report: {request.report_path}",
                "",
                render_expansion_operator_approval_schema_migration_approval_request_line(
                    request
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Schema Migration Decision Ledger",
            "",
        ]
    )
    if latest_expansion_operator_approval_schema_migration_decision_ledger is not None:
        ledger = latest_expansion_operator_approval_schema_migration_decision_ledger
        lines.extend(
            [
                f"- status: {ledger.status}",
                f"- source_request: {ledger.source_request_id}",
                f"- source_status: {ledger.source_request_status}",
                f"- source_plan: {ledger.source_plan_id}",
                f"- source_plan_status: {ledger.source_plan_status}",
                f"- source_decision: {ledger.source_decision_id}",
                f"- source_decision_status: {ledger.source_decision_status}",
                f"- source_review: {ledger.source_review_id}",
                f"- source_review_status: {ledger.source_review_status}",
                f"- target_table: {ledger.target_table}",
                f"- planned_columns: {ledger.planned_column_count}",
                f"- planned_indexes: {ledger.planned_index_count}",
                f"- migration_steps: {ledger.migration_step_count}",
                f"- affected_requests: {ledger.affected_request_count}",
                f"- schema_gaps: {ledger.schema_gap_count}",
                f"- request_count: {ledger.request_count}",
                f"- decision_count: {ledger.decision_count}",
                f"- pending_decisions: {ledger.pending_decision_count}",
                f"- approved_decisions: {ledger.approved_decision_count}",
                f"- deferred_decisions: {ledger.deferred_decision_count}",
                f"- more_evidence_decisions: {ledger.more_evidence_decision_count}",
                f"- approval_boundary: {ledger.approval_boundary}",
                f"- requested_action: {ledger.requested_action}",
                f"- allowed_actions: {format_schema_migration_decision_actions(ledger.allowed_actions)}",
                f"- migration_applied: {ledger.migration_applied_count}",
                f"- table_created: {ledger.table_created_count}",
                f"- operator_approval_rows_created: {ledger.operator_approval_row_count}",
                f"- approval_requests_created: {ledger.created_approval_request_count}",
                f"- existing_approval_requests: {ledger.existing_approval_request_count}",
                f"- recommended_next_step: {ledger.recommended_next_step}",
                f"- report: {ledger.report_path}",
                "",
                render_expansion_operator_approval_schema_migration_decision_ledger_line(
                    ledger
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Schema Migration Action Checklist",
            "",
        ]
    )
    if latest_expansion_operator_approval_schema_migration_action_checklist is not None:
        checklist = latest_expansion_operator_approval_schema_migration_action_checklist
        lines.extend(
            [
                f"- status: {checklist.status}",
                f"- source_ledger: {checklist.source_ledger_id}",
                f"- source_status: {checklist.source_ledger_status}",
                f"- source_request: {checklist.source_request_id}",
                f"- source_request_status: {checklist.source_request_status}",
                f"- source_plan: {checklist.source_plan_id}",
                f"- source_plan_status: {checklist.source_plan_status}",
                f"- source_decision: {checklist.source_decision_id}",
                f"- source_decision_status: {checklist.source_decision_status}",
                f"- source_review: {checklist.source_review_id}",
                f"- source_review_status: {checklist.source_review_status}",
                f"- target_table: {checklist.target_table}",
                f"- request_count: {checklist.request_count}",
                f"- decision_count: {checklist.decision_count}",
                f"- pending_decisions: {checklist.pending_decision_count}",
                f"- action_count: {checklist.action_count}",
                f"- pending_actions: {checklist.pending_action_count}",
                f"- actions_taken: {checklist.actions_taken_count}",
                f"- selected_action: {checklist.selected_action}",
                f"- approval_boundary: {checklist.approval_boundary}",
                f"- requested_action: {checklist.requested_action}",
                f"- allowed_actions: {format_schema_migration_action_actions(checklist.allowed_actions)}",
                f"- migration_applied: {checklist.migration_applied_count}",
                f"- table_created: {checklist.table_created_count}",
                f"- operator_approval_rows_created: {checklist.operator_approval_row_count}",
                f"- approval_requests_created: {checklist.created_approval_request_count}",
                f"- existing_approval_requests: {checklist.existing_approval_request_count}",
                f"- recommended_next_step: {checklist.recommended_next_step}",
                f"- report: {checklist.report_path}",
                "",
                render_expansion_operator_approval_schema_migration_action_checklist_line(
                    checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Schema Migration Selection Packet",
            "",
        ]
    )
    if latest_expansion_operator_approval_schema_migration_selection_packet is not None:
        packet = latest_expansion_operator_approval_schema_migration_selection_packet
        lines.extend(
            [
                f"- status: {packet.status}",
                f"- source_checklist: {packet.source_checklist_id}",
                f"- source_status: {packet.source_checklist_status}",
                f"- source_ledger: {packet.source_ledger_id}",
                f"- source_ledger_status: {packet.source_ledger_status}",
                f"- source_request: {packet.source_request_id}",
                f"- source_request_status: {packet.source_request_status}",
                f"- source_plan: {packet.source_plan_id}",
                f"- source_plan_status: {packet.source_plan_status}",
                f"- source_decision: {packet.source_decision_id}",
                f"- source_decision_status: {packet.source_decision_status}",
                f"- source_review: {packet.source_review_id}",
                f"- source_review_status: {packet.source_review_status}",
                f"- target_table: {packet.target_table}",
                f"- request_count: {packet.request_count}",
                f"- decision_count: {packet.decision_count}",
                f"- pending_decisions: {packet.pending_decision_count}",
                f"- action_count: {packet.action_count}",
                f"- pending_actions: {packet.pending_action_count}",
                f"- actions_taken: {packet.actions_taken_count}",
                f"- selected_action: {packet.selected_action}",
                f"- selection_count: {packet.selection_count}",
                f"- pending_selections: {packet.pending_selection_count}",
                f"- selections_recorded: {packet.selections_recorded_count}",
                f"- approve_selections: {packet.approve_selection_count}",
                f"- defer_selections: {packet.defer_selection_count}",
                f"- more_evidence_selections: {packet.more_evidence_selection_count}",
                f"- approval_boundary: {packet.approval_boundary}",
                f"- requested_action: {packet.requested_action}",
                f"- allowed_actions: {format_schema_migration_selection_actions(packet.allowed_actions)}",
                f"- migration_applied: {packet.migration_applied_count}",
                f"- table_created: {packet.table_created_count}",
                f"- operator_approval_rows_created: {packet.operator_approval_row_count}",
                f"- approval_requests_created: {packet.created_approval_request_count}",
                f"- existing_approval_requests: {packet.existing_approval_request_count}",
                f"- recommended_next_step: {packet.recommended_next_step}",
                f"- report: {packet.report_path}",
                "",
                render_expansion_operator_approval_schema_migration_selection_packet_line(
                    packet
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Queue Health Checks",
            "",
            f"- blocked_threshold: {DEFAULT_BLOCKED_THRESHOLD}",
            f"- failed_threshold: {DEFAULT_FAILED_THRESHOLD}",
            f"- hotspots: {len(queue_health_findings)}",
            "",
        ]
    )

    if queue_health_findings:
        lines.extend(render_queue_health_finding(finding) for finding in queue_health_findings)
    else:
        lines.append("- none")

    lines.extend(["", "## Handoff Review", ""])
    if latest_handoff_review is not None:
        lines.extend(
            [
                f"- status: {latest_handoff_review.status}",
                f"- current_focus: {latest_handoff_review.current_focus}",
                f"- blocked_tasks: {latest_handoff_review.blocked_task_count}",
                f"- stale_handoffs: {latest_handoff_review.stale_handoff_count}",
                f"- report: {latest_handoff_review.report_path}",
                "",
            ]
        )
        if latest_handoff_review.blocked_tasks:
            lines.extend(
                render_blocked_task_line(task)
                for task in latest_handoff_review.blocked_tasks
            )
        if latest_handoff_review.stale_handoffs:
            lines.extend(
                render_stale_handoff_line(handoff)
                for handoff in latest_handoff_review.stale_handoffs
            )
        if not latest_handoff_review.blocked_tasks and not latest_handoff_review.stale_handoffs:
            lines.append("- none")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Eval After Change",
            "",
            f"- failed: {eval_after_change_statuses['fail']}",
            "",
        ]
    )

    if eval_after_change_checks:
        lines.extend(
            render_eval_after_change_line(check)
            for check in eval_after_change_checks
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Learning Distillation", ""])
    if latest_learning_distillation is not None:
        lines.extend(
            [
                f"- status: {latest_learning_distillation.status}",
                f"- stable_learnings: {latest_learning_distillation.stable_learning_count}",
                f"- source_learnings: {latest_learning_distillation.source_learning_count}",
                f"- min_occurrences: {latest_learning_distillation.min_occurrences}",
                f"- report: {latest_learning_distillation.report_path}",
                "",
                render_learning_distillation_line(latest_learning_distillation),
            ]
        )
        if latest_learning_distillation.stable_learnings:
            lines.extend(
                render_stable_learning_line(learning)
                for learning in latest_learning_distillation.stable_learnings
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Memory Proposals", ""])
    if memory_entries:
        for entry in memory_entries:
            lines.append(f"- {render_memory_entry_line(entry)}")
    else:
        lines.append("- none")

    lines.extend(["", "## Skill Proposals", ""])
    if skill_entries:
        for skill in skill_entries:
            lines.append(f"- {render_skill_line(skill)}")
    else:
        lines.append("- none")

    lines.extend(["", "## Budget And Trust Posture", ""])
    if latest_budget_trust_report is not None:
        lines.extend(
            [
                f"- status: {latest_budget_trust_report.status}",
                f"- tasks: {latest_budget_trust_report.task_count}",
                f"- budget_state: {latest_budget_trust_report.budget_state}",
                f"- trust_state: {latest_budget_trust_report.trust_state}",
                f"- risk_counts: {format_risk_counts(latest_budget_trust_report.risk_counts)}",
                f"- report: {latest_budget_trust_report.report_path}",
                "",
                render_budget_trust_posture_line(latest_budget_trust_report),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Dispatch Posture History", ""])
    if latest_dispatch_posture_history is not None:
        lines.extend(
            [
                f"- status: {latest_dispatch_posture_history.status}",
                f"- snapshots: {latest_dispatch_posture_history.snapshot_count}",
                f"- latest_tasks: {latest_dispatch_posture_history.latest_task_count}",
                f"- task_delta: {latest_dispatch_posture_history.task_count_delta}",
                f"- latest_risk_counts: {format_risk_counts(latest_dispatch_posture_history.latest_risk_counts)}",
                f"- report: {latest_dispatch_posture_history.report_path}",
                "",
                render_dispatch_posture_history_line(latest_dispatch_posture_history),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Dispatch Posture Snapshot Review", ""])
    if latest_dispatch_posture_staleness is not None:
        lines.extend(
            [
                f"- status: {latest_dispatch_posture_staleness.status}",
                f"- snapshots: {latest_dispatch_posture_staleness.snapshot_count}",
                f"- stale_snapshots: {latest_dispatch_posture_staleness.stale_snapshot_count}",
                "- latest_snapshot_age_seconds: "
                f"{format_optional_age_seconds(latest_dispatch_posture_staleness.latest_snapshot_age_seconds)}",
                f"- stale_after_seconds: {latest_dispatch_posture_staleness.stale_after_seconds}",
                f"- report: {latest_dispatch_posture_staleness.report_path}",
                "",
                render_dispatch_posture_staleness_line(latest_dispatch_posture_staleness),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Dispatch Posture Refresh Recommendation", ""])
    if latest_dispatch_posture_refresh is not None:
        lines.extend(
            [
                f"- status: {latest_dispatch_posture_refresh.status}",
                f"- source_review: {latest_dispatch_posture_refresh.source_review_id or 'none'}",
                f"- source_status: {latest_dispatch_posture_refresh.source_review_status}",
                f"- recommended_commands: {format_recommended_commands(latest_dispatch_posture_refresh.recommended_commands)}",
                f"- report: {latest_dispatch_posture_refresh.report_path}",
                "",
                render_dispatch_posture_refresh_line(latest_dispatch_posture_refresh),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Expansion Ledger", ""])
    if latest_capability_expansion_ledger is not None:
        lines.extend(
            [
                f"- status: {latest_capability_expansion_ledger.status}",
                f"- capabilities: {latest_capability_expansion_ledger.capability_count}",
                f"- ready: {latest_capability_expansion_ledger.ready_count}",
                f"- deferred: {latest_capability_expansion_ledger.deferred_count}",
                f"- approval_boundary: {latest_capability_expansion_ledger.approval_boundary}",
                f"- report: {latest_capability_expansion_ledger.report_path}",
                "",
                render_capability_expansion_ledger_line(latest_capability_expansion_ledger),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Readiness Review", ""])
    if latest_capability_readiness_review is not None:
        lines.extend(
            [
                f"- status: {latest_capability_readiness_review.status}",
                f"- source_ledger: {latest_capability_readiness_review.source_ledger_id or 'none'}",
                f"- capabilities: {latest_capability_readiness_review.capability_count}",
                f"- ready: {latest_capability_readiness_review.ready_count}",
                f"- not_ready: {latest_capability_readiness_review.not_ready_count}",
                f"- missing_evidence: {latest_capability_readiness_review.missing_evidence_count}",
                f"- recommended_commands: {format_readiness_commands(latest_capability_readiness_review.recommended_commands)}",
                f"- report: {latest_capability_readiness_review.report_path}",
                "",
                render_capability_readiness_review_line(latest_capability_readiness_review),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Proof Gap Index", ""])
    if latest_capability_proof_gap_index is not None:
        lines.extend(
            [
                f"- status: {latest_capability_proof_gap_index.status}",
                f"- source_review: {latest_capability_proof_gap_index.source_review_id or 'none'}",
                f"- capabilities: {latest_capability_proof_gap_index.capability_count}",
                f"- gaps: {latest_capability_proof_gap_index.gap_count}",
                f"- missing_evidence: {latest_capability_proof_gap_index.missing_evidence_count}",
                f"- blocked_capabilities: {latest_capability_proof_gap_index.blocked_capability_count}",
                f"- next_proofs: {latest_capability_proof_gap_index.next_proof_count}",
                f"- recommended_commands: {format_proof_gap_commands(latest_capability_proof_gap_index.recommended_commands)}",
                f"- report: {latest_capability_proof_gap_index.report_path}",
                "",
                render_capability_proof_gap_index_line(latest_capability_proof_gap_index),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Approval Boundary Matrix", ""])
    if latest_capability_approval_boundary_matrix is not None:
        lines.extend(
            [
                f"- status: {latest_capability_approval_boundary_matrix.status}",
                f"- source_index: {latest_capability_approval_boundary_matrix.source_index_id or 'none'}",
                f"- capabilities: {latest_capability_approval_boundary_matrix.capability_count}",
                f"- boundaries: {latest_capability_approval_boundary_matrix.boundary_count}",
                f"- gaps: {latest_capability_approval_boundary_matrix.gap_count}",
                f"- blocked_capabilities: {latest_capability_approval_boundary_matrix.blocked_capability_count}",
                f"- approvals_required: {latest_capability_approval_boundary_matrix.approval_required_count}",
                f"- recommended_commands: {format_approval_boundary_commands(latest_capability_approval_boundary_matrix.recommended_commands)}",
                f"- report: {latest_capability_approval_boundary_matrix.report_path}",
                "",
                render_capability_approval_boundary_matrix_line(
                    latest_capability_approval_boundary_matrix
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Evidence Collection Plan", ""])
    if latest_capability_evidence_collection_plan is not None:
        lines.extend(
            [
                f"- status: {latest_capability_evidence_collection_plan.status}",
                f"- source_matrix: {latest_capability_evidence_collection_plan.source_matrix_id or 'none'}",
                f"- capabilities: {latest_capability_evidence_collection_plan.capability_count}",
                f"- evidence_items: {latest_capability_evidence_collection_plan.evidence_item_count}",
                f"- manual_collection: {latest_capability_evidence_collection_plan.manual_collection_count}",
                f"- approvals_required: {latest_capability_evidence_collection_plan.approval_required_count}",
                f"- boundaries: {latest_capability_evidence_collection_plan.boundary_count}",
                f"- recommended_commands: {format_evidence_collection_commands(latest_capability_evidence_collection_plan.recommended_commands)}",
                f"- report: {latest_capability_evidence_collection_plan.report_path}",
                "",
                render_capability_evidence_collection_plan_line(
                    latest_capability_evidence_collection_plan
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Promotion Gate Checklist", ""])
    if latest_capability_promotion_gate_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_capability_promotion_gate_checklist.status}",
                f"- source_plan: {latest_capability_promotion_gate_checklist.source_plan_id or 'none'}",
                f"- capabilities: {latest_capability_promotion_gate_checklist.capability_count}",
                f"- gates: {latest_capability_promotion_gate_checklist.gate_count}",
                f"- blocked_promotions: {latest_capability_promotion_gate_checklist.blocked_promotion_count}",
                f"- missing_evidence: {latest_capability_promotion_gate_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_capability_promotion_gate_checklist.approval_required_count}",
                f"- boundaries: {latest_capability_promotion_gate_checklist.boundary_count}",
                f"- recommended_commands: {format_promotion_gate_commands(latest_capability_promotion_gate_checklist.recommended_commands)}",
                f"- report: {latest_capability_promotion_gate_checklist.report_path}",
                "",
                render_capability_promotion_gate_checklist_line(
                    latest_capability_promotion_gate_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Promotion Decision Ledger", ""])
    if latest_capability_promotion_decision_ledger is not None:
        lines.extend(
            [
                f"- status: {latest_capability_promotion_decision_ledger.status}",
                f"- source_checklist: {latest_capability_promotion_decision_ledger.source_checklist_id or 'none'}",
                f"- capabilities: {latest_capability_promotion_decision_ledger.capability_count}",
                f"- decisions: {latest_capability_promotion_decision_ledger.decision_count}",
                f"- deferred_promotions: {latest_capability_promotion_decision_ledger.deferred_promotion_count}",
                f"- operator_decisions_required: {latest_capability_promotion_decision_ledger.operator_decision_required_count}",
                f"- blocked_promotions: {latest_capability_promotion_decision_ledger.blocked_promotion_count}",
                f"- missing_evidence: {latest_capability_promotion_decision_ledger.missing_evidence_count}",
                f"- approvals_required: {latest_capability_promotion_decision_ledger.approval_required_count}",
                f"- boundaries: {latest_capability_promotion_decision_ledger.boundary_count}",
                f"- recommended_commands: {format_promotion_decision_commands(latest_capability_promotion_decision_ledger.recommended_commands)}",
                f"- report: {latest_capability_promotion_decision_ledger.report_path}",
                "",
                render_capability_promotion_decision_ledger_line(
                    latest_capability_promotion_decision_ledger
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Trust Promotion Audit", ""])
    if latest_capability_trust_promotion_audit is not None:
        lines.extend(
            [
                f"- status: {latest_capability_trust_promotion_audit.status}",
                f"- source_ledger: {latest_capability_trust_promotion_audit.source_ledger_id or 'none'}",
                f"- capabilities: {latest_capability_trust_promotion_audit.capability_count}",
                f"- audits: {latest_capability_trust_promotion_audit.audit_count}",
                f"- blocked_trust_promotions: {latest_capability_trust_promotion_audit.blocked_trust_promotion_count}",
                f"- operator_reviews_required: {latest_capability_trust_promotion_audit.operator_review_required_count}",
                f"- deferred_promotions: {latest_capability_trust_promotion_audit.deferred_promotion_count}",
                f"- missing_evidence: {latest_capability_trust_promotion_audit.missing_evidence_count}",
                f"- approvals_required: {latest_capability_trust_promotion_audit.approval_required_count}",
                f"- boundaries: {latest_capability_trust_promotion_audit.boundary_count}",
                f"- recommended_commands: {format_trust_promotion_commands(latest_capability_trust_promotion_audit.recommended_commands)}",
                f"- report: {latest_capability_trust_promotion_audit.report_path}",
                "",
                render_capability_trust_promotion_audit_line(
                    latest_capability_trust_promotion_audit
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Automatic Retry Audit", ""])
    if latest_capability_automatic_retry_audit is not None:
        lines.extend(
            [
                f"- status: {latest_capability_automatic_retry_audit.status}",
                f"- source_audit: {latest_capability_automatic_retry_audit.source_audit_id or 'none'}",
                f"- capabilities: {latest_capability_automatic_retry_audit.capability_count}",
                f"- audits: {latest_capability_automatic_retry_audit.audit_count}",
                f"- blocked_retries: {latest_capability_automatic_retry_audit.blocked_retry_count}",
                f"- operator_reviews_required: {latest_capability_automatic_retry_audit.operator_review_required_count}",
                f"- blocked_trust_promotions: {latest_capability_automatic_retry_audit.blocked_trust_promotion_count}",
                f"- deferred_promotions: {latest_capability_automatic_retry_audit.deferred_promotion_count}",
                f"- missing_evidence: {latest_capability_automatic_retry_audit.missing_evidence_count}",
                f"- approvals_required: {latest_capability_automatic_retry_audit.approval_required_count}",
                f"- boundaries: {latest_capability_automatic_retry_audit.boundary_count}",
                f"- recommended_commands: {format_automatic_retry_commands(latest_capability_automatic_retry_audit.recommended_commands)}",
                f"- report: {latest_capability_automatic_retry_audit.report_path}",
                "",
                render_capability_automatic_retry_audit_line(
                    latest_capability_automatic_retry_audit
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Capability Real Cost Tracking Audit", ""])
    if latest_capability_real_cost_tracking_audit is not None:
        lines.extend(
            [
                f"- status: {latest_capability_real_cost_tracking_audit.status}",
                f"- source_audit: {latest_capability_real_cost_tracking_audit.source_audit_id or 'none'}",
                f"- capabilities: {latest_capability_real_cost_tracking_audit.capability_count}",
                f"- audits: {latest_capability_real_cost_tracking_audit.audit_count}",
                f"- blocked_cost_tracking: {latest_capability_real_cost_tracking_audit.blocked_cost_tracking_count}",
                f"- operator_reviews_required: {latest_capability_real_cost_tracking_audit.operator_review_required_count}",
                f"- blocked_retries: {latest_capability_real_cost_tracking_audit.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_capability_real_cost_tracking_audit.blocked_trust_promotion_count}",
                f"- deferred_promotions: {latest_capability_real_cost_tracking_audit.deferred_promotion_count}",
                f"- missing_evidence: {latest_capability_real_cost_tracking_audit.missing_evidence_count}",
                f"- approvals_required: {latest_capability_real_cost_tracking_audit.approval_required_count}",
                f"- boundaries: {latest_capability_real_cost_tracking_audit.boundary_count}",
                f"- recommended_commands: {format_real_cost_tracking_commands(latest_capability_real_cost_tracking_audit.recommended_commands)}",
                f"- report: {latest_capability_real_cost_tracking_audit.report_path}",
                "",
                render_capability_real_cost_tracking_audit_line(
                    latest_capability_real_cost_tracking_audit
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Hosted Dashboard Proof Checklist", ""])
    if latest_hosted_dashboard_proof_checklist is not None:
        hosted_dashboard_source_status = (
            latest_hosted_dashboard_proof_checklist.source_checklist_status
            if latest_hosted_dashboard_proof_checklist.source_kind
            == "real_cost_tracking_proof_checklist"
            else latest_hosted_dashboard_proof_checklist.source_audit_status
        )
        lines.extend(
            [
                f"- status: {latest_hosted_dashboard_proof_checklist.status}",
                f"- source_kind: {latest_hosted_dashboard_proof_checklist.source_kind}",
                f"- source_checklist: {latest_hosted_dashboard_proof_checklist.source_checklist_id or 'none'}",
                f"- source_audit: {latest_hosted_dashboard_proof_checklist.source_audit_id or 'none'}",
                f"- source_status: {hosted_dashboard_source_status}",
                f"- capabilities: {latest_hosted_dashboard_proof_checklist.capability_count}",
                f"- checklist_items: {latest_hosted_dashboard_proof_checklist.checklist_count}",
                f"- blocked_dashboard_proofs: {latest_hosted_dashboard_proof_checklist.blocked_dashboard_proof_count}",
                f"- operator_reviews_required: {latest_hosted_dashboard_proof_checklist.operator_review_required_count}",
                f"- blocked_cost_tracking: {latest_hosted_dashboard_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_hosted_dashboard_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_hosted_dashboard_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_hosted_dashboard_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_hosted_dashboard_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_hosted_dashboard_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_hosted_dashboard_commands(latest_hosted_dashboard_proof_checklist.recommended_commands)}",
                f"- report: {latest_hosted_dashboard_proof_checklist.report_path}",
                "",
                render_hosted_dashboard_proof_checklist_line(
                    latest_hosted_dashboard_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Remote Worker Proof Checklist", ""])
    if latest_remote_worker_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_remote_worker_proof_checklist.status}",
                f"- source_checklist: {latest_remote_worker_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_remote_worker_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_remote_worker_proof_checklist.capability_count}",
                f"- checklist_items: {latest_remote_worker_proof_checklist.checklist_count}",
                f"- blocked_worker_proofs: {latest_remote_worker_proof_checklist.blocked_worker_proof_count}",
                f"- operator_reviews_required: {latest_remote_worker_proof_checklist.operator_review_required_count}",
                f"- blocked_dashboard_proofs: {latest_remote_worker_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_remote_worker_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_remote_worker_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_remote_worker_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_remote_worker_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_remote_worker_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_remote_worker_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_remote_worker_commands(latest_remote_worker_proof_checklist.recommended_commands)}",
                f"- report: {latest_remote_worker_proof_checklist.report_path}",
                "",
                render_remote_worker_proof_checklist_line(
                    latest_remote_worker_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Autonomous Scheduling Proof Checklist", ""])
    if latest_autonomous_scheduling_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_autonomous_scheduling_proof_checklist.status}",
                f"- source_checklist: {latest_autonomous_scheduling_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_autonomous_scheduling_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_autonomous_scheduling_proof_checklist.capability_count}",
                f"- checklist_items: {latest_autonomous_scheduling_proof_checklist.checklist_count}",
                f"- blocked_scheduling_proofs: {latest_autonomous_scheduling_proof_checklist.blocked_scheduling_proof_count}",
                f"- operator_reviews_required: {latest_autonomous_scheduling_proof_checklist.operator_review_required_count}",
                f"- blocked_worker_proofs: {latest_autonomous_scheduling_proof_checklist.blocked_worker_proof_count}",
                f"- blocked_dashboard_proofs: {latest_autonomous_scheduling_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_autonomous_scheduling_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_autonomous_scheduling_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_autonomous_scheduling_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_autonomous_scheduling_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_autonomous_scheduling_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_autonomous_scheduling_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_autonomous_scheduling_commands(latest_autonomous_scheduling_proof_checklist.recommended_commands)}",
                f"- report: {latest_autonomous_scheduling_proof_checklist.report_path}",
                "",
                render_autonomous_scheduling_proof_checklist_line(
                    latest_autonomous_scheduling_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Browser Desktop Adapter Proof Checklist", ""])
    if latest_browser_desktop_adapter_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_browser_desktop_adapter_proof_checklist.status}",
                f"- source_checklist: {latest_browser_desktop_adapter_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_browser_desktop_adapter_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_browser_desktop_adapter_proof_checklist.capability_count}",
                f"- checklist_items: {latest_browser_desktop_adapter_proof_checklist.checklist_count}",
                f"- blocked_adapter_proofs: {latest_browser_desktop_adapter_proof_checklist.blocked_adapter_proof_count}",
                f"- operator_reviews_required: {latest_browser_desktop_adapter_proof_checklist.operator_review_required_count}",
                f"- blocked_scheduling_proofs: {latest_browser_desktop_adapter_proof_checklist.blocked_scheduling_proof_count}",
                f"- blocked_worker_proofs: {latest_browser_desktop_adapter_proof_checklist.blocked_worker_proof_count}",
                f"- blocked_dashboard_proofs: {latest_browser_desktop_adapter_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_browser_desktop_adapter_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_browser_desktop_adapter_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_browser_desktop_adapter_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_browser_desktop_adapter_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_browser_desktop_adapter_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_browser_desktop_adapter_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_browser_desktop_adapter_commands(latest_browser_desktop_adapter_proof_checklist.recommended_commands)}",
                f"- report: {latest_browser_desktop_adapter_proof_checklist.report_path}",
                "",
                render_browser_desktop_adapter_proof_checklist_line(
                    latest_browser_desktop_adapter_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## CI Deploy Proof Checklist", ""])
    if latest_ci_deploy_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_ci_deploy_proof_checklist.status}",
                f"- source_checklist: {latest_ci_deploy_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_ci_deploy_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_ci_deploy_proof_checklist.capability_count}",
                f"- checklist_items: {latest_ci_deploy_proof_checklist.checklist_count}",
                f"- blocked_ci_deploy_proofs: {latest_ci_deploy_proof_checklist.blocked_ci_deploy_proof_count}",
                f"- operator_reviews_required: {latest_ci_deploy_proof_checklist.operator_review_required_count}",
                f"- blocked_adapter_proofs: {latest_ci_deploy_proof_checklist.blocked_adapter_proof_count}",
                f"- blocked_scheduling_proofs: {latest_ci_deploy_proof_checklist.blocked_scheduling_proof_count}",
                f"- blocked_worker_proofs: {latest_ci_deploy_proof_checklist.blocked_worker_proof_count}",
                f"- blocked_dashboard_proofs: {latest_ci_deploy_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_ci_deploy_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_ci_deploy_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_ci_deploy_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_ci_deploy_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_ci_deploy_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_ci_deploy_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_ci_deploy_commands(latest_ci_deploy_proof_checklist.recommended_commands)}",
                f"- report: {latest_ci_deploy_proof_checklist.report_path}",
                "",
                render_ci_deploy_proof_checklist_line(
                    latest_ci_deploy_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Budget Enforcement Proof Checklist", ""])
    if latest_budget_enforcement_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_budget_enforcement_proof_checklist.status}",
                f"- source_checklist: {latest_budget_enforcement_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_budget_enforcement_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_budget_enforcement_proof_checklist.capability_count}",
                f"- checklist_items: {latest_budget_enforcement_proof_checklist.checklist_count}",
                f"- blocked_budget_enforcement_proofs: {latest_budget_enforcement_proof_checklist.blocked_budget_enforcement_proof_count}",
                f"- operator_reviews_required: {latest_budget_enforcement_proof_checklist.operator_review_required_count}",
                f"- blocked_ci_deploy_proofs: {latest_budget_enforcement_proof_checklist.blocked_ci_deploy_proof_count}",
                f"- blocked_adapter_proofs: {latest_budget_enforcement_proof_checklist.blocked_adapter_proof_count}",
                f"- blocked_scheduling_proofs: {latest_budget_enforcement_proof_checklist.blocked_scheduling_proof_count}",
                f"- blocked_worker_proofs: {latest_budget_enforcement_proof_checklist.blocked_worker_proof_count}",
                f"- blocked_dashboard_proofs: {latest_budget_enforcement_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_budget_enforcement_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_budget_enforcement_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_budget_enforcement_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_budget_enforcement_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_budget_enforcement_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_budget_enforcement_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_budget_enforcement_commands(latest_budget_enforcement_proof_checklist.recommended_commands)}",
                f"- report: {latest_budget_enforcement_proof_checklist.report_path}",
                "",
                render_budget_enforcement_proof_checklist_line(
                    latest_budget_enforcement_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Trust Promotion Proof Checklist", ""])
    if latest_trust_promotion_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_trust_promotion_proof_checklist.status}",
                f"- source_checklist: {latest_trust_promotion_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_trust_promotion_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_trust_promotion_proof_checklist.capability_count}",
                f"- checklist_items: {latest_trust_promotion_proof_checklist.checklist_count}",
                f"- blocked_trust_promotion_proofs: {latest_trust_promotion_proof_checklist.blocked_trust_promotion_proof_count}",
                f"- operator_reviews_required: {latest_trust_promotion_proof_checklist.operator_review_required_count}",
                f"- blocked_budget_enforcement_proofs: {latest_trust_promotion_proof_checklist.blocked_budget_enforcement_proof_count}",
                f"- blocked_ci_deploy_proofs: {latest_trust_promotion_proof_checklist.blocked_ci_deploy_proof_count}",
                f"- blocked_adapter_proofs: {latest_trust_promotion_proof_checklist.blocked_adapter_proof_count}",
                f"- blocked_scheduling_proofs: {latest_trust_promotion_proof_checklist.blocked_scheduling_proof_count}",
                f"- blocked_worker_proofs: {latest_trust_promotion_proof_checklist.blocked_worker_proof_count}",
                f"- blocked_dashboard_proofs: {latest_trust_promotion_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_trust_promotion_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_trust_promotion_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_trust_promotion_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_trust_promotion_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_trust_promotion_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_trust_promotion_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_trust_promotion_proof_commands(latest_trust_promotion_proof_checklist.recommended_commands)}",
                f"- report: {latest_trust_promotion_proof_checklist.report_path}",
                "",
                render_trust_promotion_proof_checklist_line(
                    latest_trust_promotion_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Automatic Retry Proof Checklist", ""])
    if latest_automatic_retry_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_automatic_retry_proof_checklist.status}",
                f"- source_checklist: {latest_automatic_retry_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_automatic_retry_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_automatic_retry_proof_checklist.capability_count}",
                f"- checklist_items: {latest_automatic_retry_proof_checklist.checklist_count}",
                f"- blocked_automatic_retry_proofs: {latest_automatic_retry_proof_checklist.blocked_automatic_retry_proof_count}",
                f"- operator_reviews_required: {latest_automatic_retry_proof_checklist.operator_review_required_count}",
                f"- blocked_trust_promotion_proofs: {latest_automatic_retry_proof_checklist.blocked_trust_promotion_proof_count}",
                f"- blocked_budget_enforcement_proofs: {latest_automatic_retry_proof_checklist.blocked_budget_enforcement_proof_count}",
                f"- blocked_ci_deploy_proofs: {latest_automatic_retry_proof_checklist.blocked_ci_deploy_proof_count}",
                f"- blocked_adapter_proofs: {latest_automatic_retry_proof_checklist.blocked_adapter_proof_count}",
                f"- blocked_scheduling_proofs: {latest_automatic_retry_proof_checklist.blocked_scheduling_proof_count}",
                f"- blocked_worker_proofs: {latest_automatic_retry_proof_checklist.blocked_worker_proof_count}",
                f"- blocked_dashboard_proofs: {latest_automatic_retry_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_automatic_retry_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_automatic_retry_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_automatic_retry_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_automatic_retry_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_automatic_retry_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_automatic_retry_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_automatic_retry_proof_commands(latest_automatic_retry_proof_checklist.recommended_commands)}",
                f"- report: {latest_automatic_retry_proof_checklist.report_path}",
                "",
                render_automatic_retry_proof_checklist_line(
                    latest_automatic_retry_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Real Cost Tracking Proof Checklist", ""])
    if latest_real_cost_tracking_proof_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_real_cost_tracking_proof_checklist.status}",
                f"- source_checklist: {latest_real_cost_tracking_proof_checklist.source_checklist_id or 'none'}",
                f"- source_status: {latest_real_cost_tracking_proof_checklist.source_checklist_status}",
                f"- capabilities: {latest_real_cost_tracking_proof_checklist.capability_count}",
                f"- checklist_items: {latest_real_cost_tracking_proof_checklist.checklist_count}",
                f"- blocked_real_cost_tracking_proofs: {latest_real_cost_tracking_proof_checklist.blocked_real_cost_tracking_proof_count}",
                f"- operator_reviews_required: {latest_real_cost_tracking_proof_checklist.operator_review_required_count}",
                f"- blocked_automatic_retry_proofs: {latest_real_cost_tracking_proof_checklist.blocked_automatic_retry_proof_count}",
                f"- blocked_trust_promotion_proofs: {latest_real_cost_tracking_proof_checklist.blocked_trust_promotion_proof_count}",
                f"- blocked_budget_enforcement_proofs: {latest_real_cost_tracking_proof_checklist.blocked_budget_enforcement_proof_count}",
                f"- blocked_ci_deploy_proofs: {latest_real_cost_tracking_proof_checklist.blocked_ci_deploy_proof_count}",
                f"- blocked_adapter_proofs: {latest_real_cost_tracking_proof_checklist.blocked_adapter_proof_count}",
                f"- blocked_scheduling_proofs: {latest_real_cost_tracking_proof_checklist.blocked_scheduling_proof_count}",
                f"- blocked_worker_proofs: {latest_real_cost_tracking_proof_checklist.blocked_worker_proof_count}",
                f"- blocked_dashboard_proofs: {latest_real_cost_tracking_proof_checklist.blocked_dashboard_proof_count}",
                f"- blocked_cost_tracking: {latest_real_cost_tracking_proof_checklist.blocked_cost_tracking_count}",
                f"- blocked_retries: {latest_real_cost_tracking_proof_checklist.blocked_retry_count}",
                f"- blocked_trust_promotions: {latest_real_cost_tracking_proof_checklist.blocked_trust_promotion_count}",
                f"- missing_evidence: {latest_real_cost_tracking_proof_checklist.missing_evidence_count}",
                f"- approvals_required: {latest_real_cost_tracking_proof_checklist.approval_required_count}",
                f"- boundaries: {latest_real_cost_tracking_proof_checklist.boundary_count}",
                f"- recommended_commands: {format_real_cost_tracking_proof_commands(latest_real_cost_tracking_proof_checklist.recommended_commands)}",
                f"- report: {latest_real_cost_tracking_proof_checklist.report_path}",
                "",
                render_real_cost_tracking_proof_checklist_line(
                    latest_real_cost_tracking_proof_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Goal Completion Audit", ""])
    if latest_goal_completion_audit is not None:
        lines.extend(
            [
                f"- status: {latest_goal_completion_audit.status}",
                f"- requirements: {latest_goal_completion_audit.requirement_count}",
                f"- satisfied_requirements: {latest_goal_completion_audit.satisfied_requirement_count}",
                f"- blocked_requirements: {latest_goal_completion_audit.blocked_requirement_count}",
                f"- missing_evidence: {latest_goal_completion_audit.missing_evidence_count}",
                f"- approvals_required: {latest_goal_completion_audit.approval_required_count}",
                f"- external_decisions_required: {latest_goal_completion_audit.external_decision_count}",
                f"- recommended_commands: {format_goal_completion_audit_commands(latest_goal_completion_audit.recommended_commands)}",
                f"- report: {latest_goal_completion_audit.report_path}",
                "",
                render_goal_completion_audit_line(latest_goal_completion_audit),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Decision Brief", ""])
    if latest_expansion_decision_brief is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_decision_brief.status}",
                f"- source_audit: {latest_expansion_decision_brief.source_audit_id}",
                f"- source_status: {latest_expansion_decision_brief.source_audit_status}",
                f"- requirements: {latest_expansion_decision_brief.requirement_count}",
                f"- blocked_requirements: {latest_expansion_decision_brief.blocked_requirement_count}",
                f"- external_decisions_required: {latest_expansion_decision_brief.external_decision_count}",
                f"- approvals_required: {latest_expansion_decision_brief.approval_required_count}",
                f"- decision_items: {latest_expansion_decision_brief.decision_item_count}",
                f"- recommended_next_step: {latest_expansion_decision_brief.recommended_next_step}",
                f"- report: {latest_expansion_decision_brief.report_path}",
                "",
                render_expansion_decision_brief_line(
                    latest_expansion_decision_brief
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Decision Evidence Index", ""])
    if latest_expansion_decision_evidence_index is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_decision_evidence_index.status}",
                f"- source_brief: {latest_expansion_decision_evidence_index.source_brief_id}",
                f"- source_status: {latest_expansion_decision_evidence_index.source_brief_status}",
                f"- source_audit: {latest_expansion_decision_evidence_index.source_audit_id}",
                f"- decision_items: {latest_expansion_decision_evidence_index.decision_item_count}",
                f"- evidence_items: {latest_expansion_decision_evidence_index.evidence_item_count}",
                f"- external_decisions: {latest_expansion_decision_evidence_index.external_decision_count}",
                f"- capability_decisions: {latest_expansion_decision_evidence_index.capability_decision_count}",
                f"- missing_evidence_links: {latest_expansion_decision_evidence_index.missing_evidence_link_count}",
                f"- recommended_next_step: {latest_expansion_decision_evidence_index.recommended_next_step}",
                f"- report: {latest_expansion_decision_evidence_index.report_path}",
                "",
                render_expansion_decision_evidence_index_line(
                    latest_expansion_decision_evidence_index
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Operator Review Checklist", ""])
    if latest_expansion_operator_review_checklist is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_operator_review_checklist.status}",
                f"- source_index: {latest_expansion_operator_review_checklist.source_index_id}",
                f"- source_status: {latest_expansion_operator_review_checklist.source_index_status}",
                f"- source_brief: {latest_expansion_operator_review_checklist.source_brief_id}",
                f"- source_audit: {latest_expansion_operator_review_checklist.source_audit_id}",
                f"- review_items: {latest_expansion_operator_review_checklist.review_item_count}",
                f"- decision_required: {latest_expansion_operator_review_checklist.decision_required_count}",
                f"- external_reviews: {latest_expansion_operator_review_checklist.external_review_count}",
                f"- capability_reviews: {latest_expansion_operator_review_checklist.capability_review_count}",
                f"- missing_evidence_links: {latest_expansion_operator_review_checklist.missing_evidence_link_count}",
                f"- allowed_actions: {format_operator_review_allowed_actions(latest_expansion_operator_review_checklist.allowed_actions)}",
                f"- recommended_next_step: {latest_expansion_operator_review_checklist.recommended_next_step}",
                f"- report: {latest_expansion_operator_review_checklist.report_path}",
                "",
                render_expansion_operator_review_checklist_line(
                    latest_expansion_operator_review_checklist
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Operator Decision Ledger", ""])
    if latest_expansion_operator_decision_ledger is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_operator_decision_ledger.status}",
                f"- source_checklist: {latest_expansion_operator_decision_ledger.source_checklist_id}",
                f"- source_status: {latest_expansion_operator_decision_ledger.source_checklist_status}",
                f"- source_index: {latest_expansion_operator_decision_ledger.source_index_id}",
                f"- source_brief: {latest_expansion_operator_decision_ledger.source_brief_id}",
                f"- source_audit: {latest_expansion_operator_decision_ledger.source_audit_id}",
                f"- decision_items: {latest_expansion_operator_decision_ledger.decision_item_count}",
                f"- pending_decisions: {latest_expansion_operator_decision_ledger.pending_decision_count}",
                f"- approved_decisions: {latest_expansion_operator_decision_ledger.approved_decision_count}",
                f"- deferred_decisions: {latest_expansion_operator_decision_ledger.deferred_decision_count}",
                f"- more_evidence_requested: {latest_expansion_operator_decision_ledger.more_evidence_requested_count}",
                f"- external_decisions: {latest_expansion_operator_decision_ledger.external_decision_count}",
                f"- capability_decisions: {latest_expansion_operator_decision_ledger.capability_decision_count}",
                f"- allowed_actions: {format_operator_decision_allowed_actions(latest_expansion_operator_decision_ledger.allowed_actions)}",
                f"- recommended_next_step: {latest_expansion_operator_decision_ledger.recommended_next_step}",
                f"- report: {latest_expansion_operator_decision_ledger.report_path}",
                "",
                render_expansion_operator_decision_ledger_line(
                    latest_expansion_operator_decision_ledger
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Operator Approval Draft", ""])
    if latest_expansion_operator_approval_draft is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_operator_approval_draft.status}",
                f"- source_ledger: {latest_expansion_operator_approval_draft.source_ledger_id}",
                f"- source_status: {latest_expansion_operator_approval_draft.source_ledger_status}",
                f"- source_checklist: {latest_expansion_operator_approval_draft.source_checklist_id}",
                f"- source_index: {latest_expansion_operator_approval_draft.source_index_id}",
                f"- source_brief: {latest_expansion_operator_approval_draft.source_brief_id}",
                f"- source_audit: {latest_expansion_operator_approval_draft.source_audit_id}",
                f"- draft_items: {latest_expansion_operator_approval_draft.draft_item_count}",
                f"- draft_requests: {latest_expansion_operator_approval_draft.draft_request_count}",
                f"- created_approval_requests: {latest_expansion_operator_approval_draft.created_approval_request_count}",
                f"- external_drafts: {latest_expansion_operator_approval_draft.external_draft_count}",
                f"- capability_drafts: {latest_expansion_operator_approval_draft.capability_draft_count}",
                f"- approval_boundaries: {latest_expansion_operator_approval_draft.approval_boundary_count}",
                f"- pending_decisions: {latest_expansion_operator_approval_draft.pending_decision_count}",
                f"- allowed_actions: {format_operator_approval_allowed_actions(latest_expansion_operator_approval_draft.allowed_actions)}",
                f"- recommended_next_step: {latest_expansion_operator_approval_draft.recommended_next_step}",
                f"- report: {latest_expansion_operator_approval_draft.report_path}",
                "",
                render_expansion_operator_approval_draft_line(
                    latest_expansion_operator_approval_draft
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(["", "## Expansion Operator Approval Request Review", ""])
    if latest_expansion_operator_approval_request_review is not None:
        lines.extend(
            [
                f"- status: {latest_expansion_operator_approval_request_review.status}",
                f"- source_draft: {latest_expansion_operator_approval_request_review.source_draft_id}",
                f"- source_status: {latest_expansion_operator_approval_request_review.source_draft_status}",
                f"- source_ledger: {latest_expansion_operator_approval_request_review.source_ledger_id}",
                f"- source_checklist: {latest_expansion_operator_approval_request_review.source_checklist_id}",
                f"- source_index: {latest_expansion_operator_approval_request_review.source_index_id}",
                f"- source_brief: {latest_expansion_operator_approval_request_review.source_brief_id}",
                f"- source_audit: {latest_expansion_operator_approval_request_review.source_audit_id}",
                f"- draft_requests: {latest_expansion_operator_approval_request_review.draft_request_count}",
                f"- review_items: {latest_expansion_operator_approval_request_review.review_item_count}",
                f"- ready_requests: {latest_expansion_operator_approval_request_review.ready_request_count}",
                f"- blocked_requests: {latest_expansion_operator_approval_request_review.blocked_request_count}",
                f"- schema_gaps: {latest_expansion_operator_approval_request_review.schema_gap_count}",
                f"- created_approval_requests: {latest_expansion_operator_approval_request_review.created_approval_request_count}",
                f"- existing_approval_requests: {latest_expansion_operator_approval_request_review.existing_approval_request_count}",
                f"- external_requests: {latest_expansion_operator_approval_request_review.external_request_count}",
                f"- capability_requests: {latest_expansion_operator_approval_request_review.capability_request_count}",
                f"- approval_boundaries: {latest_expansion_operator_approval_request_review.approval_boundary_count}",
                f"- recommended_next_step: {latest_expansion_operator_approval_request_review.recommended_next_step}",
                f"- report: {latest_expansion_operator_approval_request_review.report_path}",
                "",
                render_expansion_operator_approval_request_review_line(
                    latest_expansion_operator_approval_request_review
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Schema Migration Selection Input Template",
            "",
        ]
    )
    if (
        latest_expansion_operator_approval_schema_migration_selection_input_template
        is not None
    ):
        template = (
            latest_expansion_operator_approval_schema_migration_selection_input_template
        )
        lines.extend(
            [
                f"- status: {template.status}",
                f"- source_packet: {template.source_packet_id}",
                f"- source_status: {template.source_packet_status}",
                f"- source_checklist: {template.source_checklist_id}",
                f"- source_checklist_status: {template.source_checklist_status}",
                f"- source_ledger: {template.source_ledger_id}",
                f"- source_ledger_status: {template.source_ledger_status}",
                f"- source_request: {template.source_request_id}",
                f"- source_request_status: {template.source_request_status}",
                f"- source_plan: {template.source_plan_id}",
                f"- source_plan_status: {template.source_plan_status}",
                f"- source_decision: {template.source_decision_id}",
                f"- source_decision_status: {template.source_decision_status}",
                f"- source_review: {template.source_review_id}",
                f"- source_review_status: {template.source_review_status}",
                f"- target_table: {template.target_table}",
                f"- request_count: {template.request_count}",
                f"- decision_count: {template.decision_count}",
                f"- pending_decisions: {template.pending_decision_count}",
                f"- action_count: {template.action_count}",
                f"- pending_actions: {template.pending_action_count}",
                f"- actions_taken: {template.actions_taken_count}",
                f"- selected_action: {template.selected_action}",
                f"- selection_count: {template.selection_count}",
                f"- pending_selections: {template.pending_selection_count}",
                f"- selections_recorded: {template.selections_recorded_count}",
                f"- approve_selections: {template.approve_selection_count}",
                f"- defer_selections: {template.defer_selection_count}",
                f"- more_evidence_selections: {template.more_evidence_selection_count}",
                f"- template_count: {template.template_count}",
                f"- pending_inputs: {template.pending_input_count}",
                f"- inputs_recorded: {template.inputs_recorded_count}",
                f"- required_fields_count: {template.required_fields_count}",
                f"- missing_required_inputs: {template.missing_required_input_count}",
                f"- approval_boundary: {template.approval_boundary}",
                f"- requested_action: {template.requested_action}",
                f"- allowed_actions: {format_schema_migration_input_template_actions(template.allowed_actions)}",
                f"- migration_applied: {template.migration_applied_count}",
                f"- table_created: {template.table_created_count}",
                f"- operator_approval_rows_created: {template.operator_approval_row_count}",
                f"- approval_requests_created: {template.created_approval_request_count}",
                f"- existing_approval_requests: {template.existing_approval_request_count}",
                f"- recommended_next_step: {template.recommended_next_step}",
                f"- report: {template.report_path}",
                "",
                render_expansion_operator_approval_schema_migration_selection_input_template_line(
                    template
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Schema Migration Application",
            "",
        ]
    )
    if latest_operator_approval_schema_migration_application is not None:
        application = latest_operator_approval_schema_migration_application
        lines.extend(
            [
                f"- status: {application.status}",
                f"- source_template: {application.source_template_id}",
                f"- source_status: {application.source_template_status}",
                f"- source_packet: {application.source_packet_id}",
                f"- source_checklist: {application.source_checklist_id}",
                f"- source_ledger: {application.source_ledger_id}",
                f"- source_request: {application.source_request_id}",
                f"- source_plan: {application.source_plan_id}",
                f"- source_decision: {application.source_decision_id}",
                f"- source_review: {application.source_review_id}",
                f"- target_table: {application.target_table}",
                f"- operator_id: {application.operator_id}",
                f"- selected_action: {application.selected_action}",
                f"- inputs_recorded: {application.inputs_recorded_count}",
                f"- missing_required_inputs: {application.missing_required_input_count}",
                f"- actions_taken: {application.actions_taken_count}",
                f"- migration_applied: {application.migration_applied_count}",
                f"- table_created: {application.table_created_count}",
                f"- operator_approval_rows_created: {application.operator_approval_row_count}",
                f"- approval_requests_created: {application.created_approval_request_count}",
                f"- existing_approval_requests: {application.existing_approval_request_count}",
                f"- report: {application.report_path}",
                "",
                render_operator_approval_schema_migration_application_line(
                    application
                ),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Expansion Operator Approval Request Rows Application",
            "",
        ]
    )
    if latest_operator_approval_request_row_application is not None:
        application = latest_operator_approval_request_row_application
        lines.extend(
            [
                f"- status: {application.status}",
                f"- source_draft: {application.source_draft_id}",
                f"- source_status: {application.source_draft_status}",
                f"- source_schema_application: {application.source_schema_application_id}",
                f"- source_schema_status: {application.source_schema_application_status}",
                f"- source_ledger: {application.source_ledger_id}",
                f"- source_checklist: {application.source_checklist_id}",
                f"- source_index: {application.source_index_id}",
                f"- source_brief: {application.source_brief_id}",
                f"- source_audit: {application.source_audit_id}",
                f"- operator_id: {application.operator_id}",
                f"- selected_action: {application.selected_action}",
                f"- draft_requests: {application.draft_request_count}",
                f"- operator_approval_rows_created: {application.operator_approval_row_count}",
                f"- approval_requests_created: {application.created_approval_request_count}",
                f"- existing_operator_approval_requests: {application.existing_operator_approval_request_count}",
                f"- external_requests: {application.external_request_count}",
                f"- capability_requests: {application.capability_request_count}",
                f"- report: {application.report_path}",
                "",
                render_operator_approval_request_rows_application_line(application),
            ]
        )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Playbooks",
            "",
            f"- active: {playbook_statuses['active']}",
            "",
        ]
    )

    if playbooks:
        lines.extend(render_playbook_line(playbook) for playbook in playbooks)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Eval Candidates",
            "",
            f"- proposed: {eval_candidate_statuses['proposed']}",
            "",
        ]
    )

    if eval_candidates:
        for candidate in eval_candidates:
            lines.append(
                f"- {candidate.id}: {candidate.status} "
                f"source={candidate.source_type}:{candidate.source_id} "
                f"suggested={candidate.suggested_eval} path={candidate.candidate_path}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Approvals",
            "",
            f"- pending: {approval_statuses['pending']}",
            f"- approved: {approval_statuses['approved']}",
            f"- rejected: {approval_statuses['rejected']}",
            "",
        ]
    )

    if approvals:
        for approval in approvals:
            lines.append(
                f"- {approval['id']}: {approval['status']} task={approval['task_id']} "
                f"run={approval['run_id']} type={approval['task_type']} "
                f"risk={approval['risk_level']} requested_by={approval['requested_by']} "
                f"reason={approval['reason']}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Stuck Tasks",
            "",
            f"- open: {stuck_statuses['open']}",
            "",
        ]
    )

    if stuck_incidents:
        for incident in stuck_incidents:
            evidence_path = _relative_to_root(root, incident["evidence_path"])
            evidence = json.loads(incident["evidence"])
            owner = evidence.get("owner") or "none"
            last_activity = evidence.get("last_activity_at", "unknown")
            timeout_seconds = evidence.get("timeout_seconds", "unknown")
            lines.append(
                f"- {incident['id']}: {incident['status']}/{incident['severity']} "
                f"type={incident['incident_type']} run={incident['run_id']} "
                f"task={incident['task_id']} owner={owner} "
                f"last_activity_at={last_activity} timeout_seconds={timeout_seconds} "
                f"evidence={evidence_path}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Incidents",
            "",
            f"- open: {incident_statuses['open']}",
            f"- resolved: {incident_statuses['resolved']}",
            "",
        ]
    )

    if incidents:
        for incident in incidents:
            failed_checks = ", ".join(json.loads(incident["failed_checks"])) or "none"
            evidence_path = _relative_to_root(root, incident["evidence_path"])
            resolution_evidence_path = _relative_to_root(
                root,
                _row_value(incident, "resolution_evidence_path"),
            )
            resolution_details = ""
            if incident["status"] == "resolved":
                resolution_details = (
                    f" resolved_at={_row_value(incident, 'resolved_at', 'unknown')}"
                    f" resolved_by={_row_value(incident, 'resolved_by', 'unknown')}"
                    f" resolution_evidence={resolution_evidence_path}"
                    f" note={_row_value(incident, 'resolution_note', '')}"
                )
            lines.append(
                f"- {incident['id']}: {incident['status']}/{incident['severity']} "
                f"type={incident['incident_type']} run={incident['run_id']} "
                f"task={incident['task_id']} method={incident['verification_method']} "
                f"failed_checks={failed_checks} evidence={evidence_path}"
                f"{resolution_details}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Recent Runs",
            "",
        ]
    )

    if runs:
        for run in runs:
            summary = _relative_to_root(root, run["summary_path"])
            completed = run["completed_at"] or "in progress"
            lines.append(
                f"- {run['id']}: {run['status']} project={run['project_id']} "
                f"goal={run['goal_id']} completed={completed} summary={summary}"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Recent Evidence Packets", ""])
    evidence_packet_lines = []
    for run in runs:
        run_dir = root / "runs" / run["id"]
        review_path = run_dir / "review.md"
        evidence_path = run_dir / "evidence-index.md"
        replay_path = run_dir / "replay-summary.md"
        if not (review_path.exists() or evidence_path.exists() or replay_path.exists()):
            continue
        evidence_packet_lines.append(
            f"- {run['id']}: "
            f"review={_relative_to_root(root, str(review_path)) if review_path.exists() else 'missing'} "
            f"evidence={_relative_to_root(root, str(evidence_path)) if evidence_path.exists() else 'missing'} "
            f"replay={_relative_to_root(root, str(replay_path)) if replay_path.exists() else 'missing'}"
        )
    if evidence_packet_lines:
        lines.extend(evidence_packet_lines)
    else:
        lines.append("- none")

    lines.extend(["", "## Recent Learnings", ""])
    if learnings:
        for learning in learnings:
            source = _relative_to_root(root, learning["source"])
            lines.append(
                f"- {learning['run_id']}: {learning['summary']} "
                f"(project={learning['project_id']}, source={source})"
            )
    else:
        lines.append("- none")

    lines.extend(["", "## Recent Eval Results", ""])
    if evals:
        for eval_row in evals:
            details = json.loads(eval_row["details"])
            run_id = details.get("run_id", "unknown")
            lines.append(
                f"- {eval_row['name']}: {eval_row['status']} "
                f"run={run_id} created_at={eval_row['created_at']}"
            )
    else:
        lines.append("- none")

    lines.append("")
    dashboard_path.write_text("\n".join(lines), encoding="utf-8")
    return dashboard_path


def _effect_verification_status(
    root: Path,
    storage: Storage,
    effect,
) -> dict[str, str]:
    method = "unknown"
    try:
        task = storage.get_task(effect.task_id)
    except KeyError:
        task = None
    if task is not None:
        method = str(task.verification_plan.get("type", "unknown"))

    verification_path = Path(effect.evidence_path).with_name("verification.json")
    status = "missing"
    command_exit_code = "unknown"
    tests_exit_code = "unknown"
    if verification_path.exists():
        verification = json.loads(verification_path.read_text(encoding="utf-8"))
        status = str(verification.get("status", "unknown"))
        command_exit_code = str(
            verification.get("command", {}).get("exit_code", "unknown")
        )
        tests_exit_code = str(
            verification.get("tests", {}).get("exit_code", "unknown")
        )

    return {
        "status": status,
        "method": method,
        "command_exit_code": command_exit_code,
        "tests_exit_code": tests_exit_code,
        "path": _relative_to_root(root, str(verification_path)),
    }


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "select 1 from sqlite_master where type = 'table' and name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _relative_to_root(root: Path, path: str | None) -> str:
    if not path:
        return "none"
    parsed = Path(path)
    try:
        return str(parsed.resolve().relative_to(root))
    except ValueError:
        return str(parsed)


def _row_value(row: sqlite3.Row, key: str, default: str | None = None) -> str | None:
    if key not in row.keys():
        return default
    value = row[key]
    if value is None:
        return default
    return value
