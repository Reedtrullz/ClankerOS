from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from agent_os.ids import new_id


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def _json_loads(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    return json.loads(value)


@dataclass(frozen=True)
class Task:
    id: str
    run_id: str | None
    goal_id: str
    project_id: str
    task_type: str
    description: str
    status: str
    priority: int
    risk_level: str
    depends_on: list[str]
    skill_tags: list[str]
    verification_plan: dict[str, Any]
    evidence: dict[str, Any]
    artifacts: list[str]
    owner: str | None
    attempts: int
    created_at: str
    updated_at: str
    claimed_at: str | None


@dataclass(frozen=True)
class GoalRecord:
    id: str
    project_id: str
    description: str
    status: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class RunRecord:
    id: str
    goal_id: str
    project_id: str
    status: str
    started_at: str
    completed_at: str | None
    activity_path: str | None
    summary_path: str | None
    events_path: str | None


@dataclass(frozen=True)
class EventRecord:
    id: int
    run_id: str
    goal_id: str | None
    task_id: str | None
    event_type: str
    message: str
    payload: dict[str, Any]
    created_at: str


@dataclass(frozen=True)
class Incident:
    id: str
    project_id: str
    run_id: str
    goal_id: str | None
    task_id: str | None
    task_type: str
    incident_type: str
    severity: str
    status: str
    summary: str
    failure_class: str
    verification_method: str | None
    verification_path: str | None
    failed_checks: list[str]
    evidence: dict[str, Any]
    artifacts: list[str]
    evidence_path: str | None
    created_at: str
    resolved_at: str | None
    resolved_by: str | None
    resolution_note: str | None
    resolution_evidence_path: str | None


@dataclass(frozen=True)
class ApprovalRequest:
    id: str
    task_id: str
    run_id: str | None
    goal_id: str
    project_id: str
    task_type: str
    risk_level: str
    status: str
    reason: str
    policy_name: str
    policy_version: str
    requested_by: str
    decided_by: str | None
    decision_note: str | None
    requested_at: str
    decided_at: str | None


@dataclass(frozen=True)
class SteeringReview:
    id: str
    goal_id: str
    project_id: str
    run_id: str | None
    reviewed_plan_version: str
    current_task_id: str | None
    status: str
    drift_score: str
    findings: list[dict[str, Any]]
    recommended_next_action: str
    requires_operator: bool
    report_path: str
    created_at: str


@dataclass(frozen=True)
class RegisteredProject:
    name: str
    root_path: str
    default_test_command: str
    allowed_write_roots: list[str]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class WorktreeRecord:
    id: str
    project_id: str
    task_id: str
    run_id: str
    base_commit: str
    branch_name: str
    worktree_path: str
    created_at: str


@dataclass(frozen=True)
class WorktreeCleanupRecord:
    id: str
    worktree_id: str
    effect_id: str
    project_id: str
    run_id: str
    task_id: str
    worktree_path: str
    branch_name: str
    cleanup_reason: str
    status: str
    decided_by: str
    decision_note: str
    evidence_path: str
    result_json: dict[str, Any]
    created_at: str


@dataclass(frozen=True)
class GitHubHandoffRecord:
    id: str
    effect_id: str
    project_id: str
    run_id: str
    task_id: str
    branch_name: str
    commit_sha: str
    remote_name: str
    remote_url: str
    base_branch: str
    status: str
    push_command: str
    draft_pr_command: str
    evidence_path: str
    result_json: dict[str, Any]
    created_at: str


@dataclass(frozen=True)
class CiDeployEvidenceRecord:
    id: str
    github_handoff_id: str
    effect_id: str
    project_id: str
    run_id: str
    task_id: str
    branch_name: str
    commit_sha: str
    provider: str
    external_run_id: str
    external_url: str
    status: str
    recorded_by: str
    evidence_path: str
    result_json: dict[str, Any]
    idempotency_key: str
    created_at: str


@dataclass(frozen=True)
class AgentProfile:
    id: str
    name: str
    label: str
    model: str
    cost_tier: str
    mode: str
    tools_json: list[str]
    permissions_json: dict[str, Any]
    use_for_json: list[str]
    max_budget_json: dict[str, Any]
    enabled: bool
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class RoutingRule:
    id: str
    category: str
    preferred_profile: str
    fallback_profile: str
    confidence_threshold: float | None
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class RoutingDecision:
    id: str
    task_id: str | None
    goal_id: str | None
    project_id: str | None
    selected_profile: str
    selected_model: str
    category: str
    reason: str
    estimated_cost_tier: str
    actual_cost: float | None
    status: str
    created_at: str


@dataclass(frozen=True)
class SubagentDelegation:
    id: str
    routing_decision_id: str | None
    parent_goal_id: str
    parent_task_id: str
    assigned_profile: str
    category: str
    title: str
    prompt: str
    input_context_json: dict[str, Any]
    allowed_tools_json: list[str]
    forbidden_actions_json: list[str]
    expected_output_schema: str
    budget_json: dict[str, Any]
    status: str
    result_summary: str | None
    result_artifact_path: str
    created_at: str
    started_at: str | None
    completed_at: str | None


@dataclass(frozen=True)
class Effect:
    id: str
    run_id: str
    task_id: str
    project_id: str
    capability: str
    effect_type: str
    idempotency_key: str
    target: str
    proposed_payload: dict[str, Any]
    status: str
    required_approval_id: str | None
    attempted_at: str | None
    committed_at: str | None
    evidence_path: str
    compensation_plan: dict[str, Any]
    result_json: dict[str, Any]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class IterationPacket:
    id: str
    focus: str
    source_path: str
    source_section: str
    status: str
    packet_path: str
    verification_commands: list[str]
    selection_policy: str
    selection_reason: str
    selected_score: int
    selected_complexity: int
    created_at: str


@dataclass(frozen=True)
class EvalRun:
    id: str
    name: str
    status: str
    details: dict[str, Any]
    created_at: str


@dataclass(frozen=True)
class Learning:
    id: str
    run_id: str
    project_id: str
    summary: str
    source: str
    created_at: str


@dataclass(frozen=True)
class MemoryEntry:
    id: str
    project_id: str
    scope: str
    key: str
    value: str
    source_type: str
    source_id: str
    confidence: float
    status: str
    created_by_profile: str
    artifact_path: str
    approved_by: str | None
    approved_at: str | None
    archived_by: str | None
    archived_at: str | None
    archive_reason: str | None
    created_at: str
    updated_at: str
    last_used_at: str | None


@dataclass(frozen=True)
class SkillRecord:
    id: str
    project_id: str | None
    name: str
    description: str
    path: str
    status: str
    created_by_profile: str
    source_run_id: str | None
    source_task_id: str | None
    verification_status: str
    approved_by: str | None
    approved_at: str | None
    archived_by: str | None
    archived_at: str | None
    archive_reason: str | None
    created_at: str
    updated_at: str
    last_used_at: str | None


@dataclass(frozen=True)
class SkillVersion:
    id: str
    skill_id: str
    version: int
    content_hash: str
    path: str
    change_summary: str
    verification_status: str
    created_at: str


@dataclass(frozen=True)
class EvalCandidate:
    id: str
    source_type: str
    source_id: str
    suggested_eval: str
    reason: str
    candidate_path: str
    status: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class Playbook:
    id: str
    slug: str
    title: str
    source_eval_name: str
    successful_run_count: int
    playbook_path: str
    status: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class QueueHealthFinding:
    status: str
    project_id: str
    task_type: str
    count: int
    threshold: int
    task_ids: list[str]
    latest_updated_at: str


@dataclass(frozen=True)
class HandoffReview:
    id: str
    status: str
    current_focus: str
    blocked_task_count: int
    stale_handoff_count: int
    blocked_tasks: list[dict[str, Any]]
    stale_handoffs: list[dict[str, Any]]
    reviewed_paths: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class EvalAfterChangeCheck:
    id: str
    change_summary: str
    changed_paths: list[str]
    eval_names: list[str]
    status: str
    result_paths: list[str]
    run_ids: list[str]
    report_path: str
    command: str
    created_at: str
    completed_at: str


@dataclass(frozen=True)
class LearningDistillation:
    id: str
    status: str
    min_occurrences: int
    stable_learning_count: int
    stable_learnings: list[dict[str, Any]]
    source_learning_count: int
    report_path: str
    created_at: str


@dataclass(frozen=True)
class BudgetTrustPostureReport:
    id: str
    status: str
    task_count: int
    risk_counts: dict[str, int]
    budget_state: str
    budget_summary: dict[str, Any]
    trust_state: str
    trust_summary: dict[str, Any]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class DispatchPostureHistorySummary:
    id: str
    status: str
    snapshot_count: int
    latest_task_count: int
    task_count_delta: int
    latest_risk_counts: dict[str, int]
    budget_states: list[str]
    trust_states: list[str]
    first_snapshot_at: str | None
    latest_snapshot_at: str | None
    report_path: str
    created_at: str


@dataclass(frozen=True)
class DispatchPostureStalenessReview:
    id: str
    status: str
    snapshot_count: int
    stale_snapshot_count: int
    latest_snapshot_age_seconds: int | None
    stale_after_seconds: int
    latest_task_count: int
    latest_risk_counts: dict[str, int]
    latest_snapshot_at: str | None
    oldest_snapshot_at: str | None
    report_path: str
    created_at: str


@dataclass(frozen=True)
class DispatchPostureRefreshRecommendation:
    id: str
    status: str
    source_review_id: str | None
    source_review_status: str
    snapshot_count: int
    stale_snapshot_count: int
    latest_snapshot_age_seconds: int | None
    stale_after_seconds: int
    latest_snapshot_at: str | None
    recommended_commands: list[str]
    reason: str
    approval_boundary: str
    deferred_capabilities: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityExpansionLedger:
    id: str
    status: str
    capability_count: int
    ready_count: int
    deferred_count: int
    approval_boundary: str
    capabilities: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityReadinessReview:
    id: str
    status: str
    source_ledger_id: str | None
    source_ledger_status: str
    capability_count: int
    ready_count: int
    not_ready_count: int
    missing_evidence_count: int
    approval_boundary: str
    recommended_commands: list[str]
    reason: str
    review_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityProofGapIndex:
    id: str
    status: str
    source_review_id: str | None
    source_review_status: str
    capability_count: int
    gap_count: int
    missing_evidence_count: int
    blocked_capability_count: int
    next_proof_count: int
    approval_boundary: str
    recommended_commands: list[str]
    reason: str
    proof_gaps: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityApprovalBoundaryMatrix:
    id: str
    status: str
    source_index_id: str | None
    source_index_status: str
    capability_count: int
    boundary_count: int
    gap_count: int
    blocked_capability_count: int
    approval_required_count: int
    recommended_commands: list[str]
    reason: str
    boundary_rows: list[dict[str, Any]]
    matrix_entries: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityEvidenceCollectionPlan:
    id: str
    status: str
    source_matrix_id: str | None
    source_matrix_status: str
    capability_count: int
    evidence_item_count: int
    manual_collection_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    evidence_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityPromotionGateChecklist:
    id: str
    status: str
    source_plan_id: str | None
    source_plan_status: str
    capability_count: int
    gate_count: int
    blocked_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityPromotionDecisionLedger:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    decision_count: int
    deferred_promotion_count: int
    operator_decision_required_count: int
    blocked_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    decision_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityTrustPromotionAudit:
    id: str
    status: str
    source_ledger_id: str | None
    source_ledger_status: str
    capability_count: int
    audit_count: int
    blocked_trust_promotion_count: int
    operator_review_required_count: int
    deferred_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    audit_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityAutomaticRetryAudit:
    id: str
    status: str
    source_audit_id: str | None
    source_audit_status: str
    capability_count: int
    audit_count: int
    blocked_retry_count: int
    operator_review_required_count: int
    blocked_trust_promotion_count: int
    deferred_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    audit_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityRealCostTrackingAudit:
    id: str
    status: str
    source_audit_id: str | None
    source_audit_status: str
    capability_count: int
    audit_count: int
    blocked_cost_tracking_count: int
    operator_review_required_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    deferred_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    audit_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class HostedDashboardProofChecklist:
    id: str
    status: str
    source_audit_id: str | None
    source_audit_status: str
    capability_count: int
    checklist_count: int
    blocked_dashboard_proof_count: int
    operator_review_required_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str
    source_kind: str = "real_cost_tracking_audit"
    source_checklist_id: str | None = None
    source_checklist_status: str = "none"


@dataclass(frozen=True)
class RemoteWorkerProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_worker_proof_count: int
    operator_review_required_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class AutonomousSchedulingProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_scheduling_proof_count: int
    operator_review_required_count: int
    blocked_worker_proof_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class BrowserDesktopAdapterProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_adapter_proof_count: int
    operator_review_required_count: int
    blocked_scheduling_proof_count: int
    blocked_worker_proof_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CiDeployProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_ci_deploy_proof_count: int
    operator_review_required_count: int
    blocked_adapter_proof_count: int
    blocked_scheduling_proof_count: int
    blocked_worker_proof_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class BudgetEnforcementProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_budget_enforcement_proof_count: int
    operator_review_required_count: int
    blocked_ci_deploy_proof_count: int
    blocked_adapter_proof_count: int
    blocked_scheduling_proof_count: int
    blocked_worker_proof_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class TrustPromotionProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_trust_promotion_proof_count: int
    operator_review_required_count: int
    blocked_budget_enforcement_proof_count: int
    blocked_ci_deploy_proof_count: int
    blocked_adapter_proof_count: int
    blocked_scheduling_proof_count: int
    blocked_worker_proof_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class AutomaticRetryProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_automatic_retry_proof_count: int
    operator_review_required_count: int
    blocked_trust_promotion_proof_count: int
    blocked_budget_enforcement_proof_count: int
    blocked_ci_deploy_proof_count: int
    blocked_adapter_proof_count: int
    blocked_scheduling_proof_count: int
    blocked_worker_proof_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class RealCostTrackingProofChecklist:
    id: str
    status: str
    source_checklist_id: str | None
    source_checklist_status: str
    capability_count: int
    checklist_count: int
    blocked_real_cost_tracking_proof_count: int
    operator_review_required_count: int
    blocked_automatic_retry_proof_count: int
    blocked_trust_promotion_proof_count: int
    blocked_budget_enforcement_proof_count: int
    blocked_ci_deploy_proof_count: int
    blocked_adapter_proof_count: int
    blocked_scheduling_proof_count: int
    blocked_worker_proof_count: int
    blocked_dashboard_proof_count: int
    blocked_cost_tracking_count: int
    blocked_retry_count: int
    blocked_trust_promotion_count: int
    missing_evidence_count: int
    approval_required_count: int
    boundary_count: int
    recommended_commands: list[str]
    reason: str
    checklist_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class GoalCompletionAudit:
    id: str
    status: str
    requirement_count: int
    satisfied_requirement_count: int
    blocked_requirement_count: int
    missing_evidence_count: int
    approval_required_count: int
    external_decision_count: int
    recommended_commands: list[str]
    reason: str
    audit_items: list[dict[str, Any]]
    external_decisions: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionDecisionBrief:
    id: str
    status: str
    source_audit_id: str
    source_audit_status: str
    requirement_count: int
    blocked_requirement_count: int
    external_decision_count: int
    approval_required_count: int
    decision_item_count: int
    recommended_next_step: str
    decision_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionDecisionEvidenceIndex:
    id: str
    status: str
    source_brief_id: str
    source_brief_status: str
    source_audit_id: str
    decision_item_count: int
    evidence_item_count: int
    external_decision_count: int
    capability_decision_count: int
    missing_evidence_link_count: int
    recommended_next_step: str
    evidence_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorReviewChecklist:
    id: str
    status: str
    source_index_id: str
    source_index_status: str
    source_brief_id: str
    source_audit_id: str
    review_item_count: int
    decision_required_count: int
    external_review_count: int
    capability_review_count: int
    missing_evidence_link_count: int
    allowed_actions: list[str]
    recommended_next_step: str
    review_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorDecisionLedger:
    id: str
    status: str
    source_checklist_id: str
    source_checklist_status: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    decision_item_count: int
    pending_decision_count: int
    approved_decision_count: int
    deferred_decision_count: int
    more_evidence_requested_count: int
    external_decision_count: int
    capability_decision_count: int
    allowed_actions: list[str]
    recommended_next_step: str
    decision_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalDraft:
    id: str
    status: str
    source_ledger_id: str
    source_ledger_status: str
    source_checklist_id: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    draft_item_count: int
    draft_request_count: int
    created_approval_request_count: int
    external_draft_count: int
    capability_draft_count: int
    approval_boundary_count: int
    pending_decision_count: int
    allowed_actions: list[str]
    recommended_next_step: str
    draft_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalRequestReview:
    id: str
    status: str
    source_draft_id: str
    source_draft_status: str
    source_ledger_id: str
    source_checklist_id: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    draft_request_count: int
    review_item_count: int
    ready_request_count: int
    blocked_request_count: int
    schema_gap_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    external_request_count: int
    capability_request_count: int
    approval_boundary_count: int
    recommended_next_step: str
    review_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalSchemaDecision:
    id: str
    status: str
    source_review_id: str
    source_review_status: str
    source_draft_id: str
    source_ledger_id: str
    source_checklist_id: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    affected_request_count: int
    schema_gap_count: int
    missing_field_count: int
    missing_fields: list[str]
    external_request_count: int
    capability_request_count: int
    decision_option_count: int
    recommended_option: str
    rejected_option_count: int
    schema_object_count: int
    migration_applied_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    recommended_next_step: str
    decision_options: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalSchemaMigrationPlan:
    id: str
    status: str
    source_decision_id: str
    source_decision_status: str
    source_review_id: str
    source_review_status: str
    source_draft_id: str
    source_ledger_id: str
    source_checklist_id: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    recommended_option: str
    target_table: str
    affected_request_count: int
    schema_gap_count: int
    missing_field_count: int
    external_request_count: int
    capability_request_count: int
    planned_column_count: int
    planned_index_count: int
    migration_step_count: int
    migration_applied_count: int
    table_created_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    recommended_next_step: str
    planned_columns: list[dict[str, Any]]
    planned_indexes: list[dict[str, Any]]
    migration_steps: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalSchemaMigrationApprovalRequest:
    id: str
    status: str
    source_plan_id: str
    source_plan_status: str
    source_decision_id: str
    source_decision_status: str
    source_review_id: str
    source_review_status: str
    target_table: str
    planned_column_count: int
    planned_index_count: int
    migration_step_count: int
    affected_request_count: int
    schema_gap_count: int
    request_count: int
    approval_boundary: str
    requested_action: str
    allowed_actions: list[str]
    migration_applied_count: int
    table_created_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    recommended_next_step: str
    approval_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalSchemaMigrationDecisionLedger:
    id: str
    status: str
    source_request_id: str
    source_request_status: str
    source_plan_id: str
    source_plan_status: str
    source_decision_id: str
    source_decision_status: str
    source_review_id: str
    source_review_status: str
    target_table: str
    planned_column_count: int
    planned_index_count: int
    migration_step_count: int
    affected_request_count: int
    schema_gap_count: int
    request_count: int
    decision_count: int
    pending_decision_count: int
    approved_decision_count: int
    deferred_decision_count: int
    more_evidence_decision_count: int
    approval_boundary: str
    requested_action: str
    allowed_actions: list[str]
    migration_applied_count: int
    table_created_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    recommended_next_step: str
    decision_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalSchemaMigrationActionChecklist:
    id: str
    status: str
    source_ledger_id: str
    source_ledger_status: str
    source_request_id: str
    source_request_status: str
    source_plan_id: str
    source_plan_status: str
    source_decision_id: str
    source_decision_status: str
    source_review_id: str
    source_review_status: str
    target_table: str
    request_count: int
    decision_count: int
    pending_decision_count: int
    action_count: int
    pending_action_count: int
    actions_taken_count: int
    selected_action: str
    approval_boundary: str
    requested_action: str
    allowed_actions: list[str]
    migration_applied_count: int
    table_created_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    recommended_next_step: str
    action_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalSchemaMigrationSelectionPacket:
    id: str
    status: str
    source_checklist_id: str
    source_checklist_status: str
    source_ledger_id: str
    source_ledger_status: str
    source_request_id: str
    source_request_status: str
    source_plan_id: str
    source_plan_status: str
    source_decision_id: str
    source_decision_status: str
    source_review_id: str
    source_review_status: str
    target_table: str
    request_count: int
    decision_count: int
    pending_decision_count: int
    action_count: int
    pending_action_count: int
    actions_taken_count: int
    selected_action: str
    selection_count: int
    pending_selection_count: int
    selections_recorded_count: int
    approve_selection_count: int
    defer_selection_count: int
    more_evidence_selection_count: int
    approval_boundary: str
    requested_action: str
    allowed_actions: list[str]
    migration_applied_count: int
    table_created_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    recommended_next_step: str
    selection_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate:
    id: str
    status: str
    source_packet_id: str
    source_packet_status: str
    source_checklist_id: str
    source_checklist_status: str
    source_ledger_id: str
    source_ledger_status: str
    source_request_id: str
    source_request_status: str
    source_plan_id: str
    source_plan_status: str
    source_decision_id: str
    source_decision_status: str
    source_review_id: str
    source_review_status: str
    target_table: str
    request_count: int
    decision_count: int
    pending_decision_count: int
    action_count: int
    pending_action_count: int
    actions_taken_count: int
    selected_action: str
    selection_count: int
    pending_selection_count: int
    selections_recorded_count: int
    approve_selection_count: int
    defer_selection_count: int
    more_evidence_selection_count: int
    template_count: int
    pending_input_count: int
    inputs_recorded_count: int
    required_fields_count: int
    missing_required_input_count: int
    approval_boundary: str
    requested_action: str
    allowed_actions: list[str]
    migration_applied_count: int
    table_created_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    recommended_next_step: str
    input_template_items: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class OperatorApprovalSchemaMigrationApplication:
    id: str
    status: str
    source_template_id: str
    source_template_status: str
    source_packet_id: str
    source_checklist_id: str
    source_ledger_id: str
    source_request_id: str
    source_plan_id: str
    source_decision_id: str
    source_review_id: str
    target_table: str
    operator_id: str
    selected_action: str
    selection_note: str
    evidence_reference: str
    inputs_recorded_count: int
    missing_required_input_count: int
    actions_taken_count: int
    migration_applied_count: int
    table_created_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_approval_request_count: int
    applied_table_columns: list[dict[str, Any]]
    applied_indexes: list[dict[str, Any]]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class OperatorApprovalRequest:
    id: str
    source_decision_id: str
    source_review_id: str
    source_draft_id: str
    source_ledger_id: str
    source_checklist_id: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    subject_type: str
    subject_key: str
    request_kind: str
    capability_key: str | None
    approval_boundary: str
    allowed_actions: list[str]
    status: str
    reason: str
    policy_name: str
    policy_version: str
    requested_by: str
    decided_by: str | None
    decision_note: str | None
    requested_at: str
    decided_at: str | None
    evidence_path: str | None
    created_at: str


@dataclass(frozen=True)
class OperatorApprovalRequestRowApplication:
    id: str
    status: str
    source_draft_id: str
    source_draft_status: str
    source_schema_application_id: str
    source_schema_application_status: str
    source_ledger_id: str
    source_checklist_id: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    operator_id: str
    selected_action: str
    selection_note: str
    evidence_reference: str
    draft_request_count: int
    operator_approval_row_count: int
    created_approval_request_count: int
    existing_operator_approval_request_count: int
    external_request_count: int
    capability_request_count: int
    created_request_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class OperatorApprovalRequestDecision:
    id: str
    status: str
    source_row_application_id: str
    source_row_application_status: str
    source_draft_id: str
    source_schema_application_id: str
    source_ledger_id: str
    source_checklist_id: str
    source_index_id: str
    source_brief_id: str
    source_audit_id: str
    operator_id: str
    selected_action: str
    selection_note: str
    evidence_reference: str
    pending_request_count_before: int
    decision_count: int
    approved_decision_count: int
    deferred_decision_count: int
    more_evidence_decision_count: int
    pending_request_count_after: int
    existing_decision_count: int
    created_approval_request_count: int
    external_request_count: int
    capability_request_count: int
    decided_request_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class OperatorApprovalEffectApplication:
    id: str
    status: str
    operator_id: str
    selection_note: str
    evidence_reference: str
    proposed_effect_count: int
    applied_effect_count: int
    existing_applied_effect_count: int
    external_effect_count: int
    capability_effect_count: int
    legacy_approval_request_count: int
    activation_action_count: int
    applied_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultEffectApplication:
    id: str
    status: str
    operator_id: str
    selection_note: str
    evidence_reference: str
    proposed_effect_count: int
    applied_effect_count: int
    existing_applied_effect_count: int
    capability_effect_count: int
    approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    applied_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectApplication:
    id: str
    status: str
    operator_id: str
    selection_note: str
    evidence_reference: str
    proposed_effect_count: int
    applied_effect_count: int
    existing_applied_effect_count: int
    capability_effect_count: int
    approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    applied_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectApplication:
    id: str
    status: str
    operator_id: str
    selection_note: str
    evidence_reference: str
    proposed_effect_count: int
    applied_effect_count: int
    existing_applied_effect_count: int
    capability_effect_count: int
    approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    applied_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskBatch:
    id: str
    status: str
    source_application_id: str
    applied_downstream_effect_count: int
    task_count: int
    existing_task_count: int
    capability_task_count: int
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    created_task_ids: list[str]
    source_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskBatch:
    id: str
    status: str
    source_application_id: str
    applied_downstream_effect_count: int
    task_count: int
    existing_task_count: int
    capability_task_count: int
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    created_task_ids: list[str]
    source_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskBatch:
    id: str
    status: str
    source_application_id: str
    applied_followup_effect_count: int
    task_count: int
    existing_task_count: int
    capability_task_count: int
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    created_task_ids: list[str]
    source_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskDelegationBatch:
    id: str
    status: str
    downstream_task_count: int
    routing_decision_count: int
    delegation_count: int
    existing_delegation_count: int
    execution_started_count: int
    network_action_count: int
    external_mutation_count: int
    activation_action_count: int
    created_routing_decision_ids: list[str]
    created_delegation_ids: list[str]
    downstream_task_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskDelegationBatch:
    id: str
    status: str
    downstream_task_count: int
    routing_decision_count: int
    delegation_count: int
    existing_delegation_count: int
    execution_started_count: int
    network_action_count: int
    external_mutation_count: int
    activation_action_count: int
    created_routing_decision_ids: list[str]
    created_delegation_ids: list[str]
    downstream_task_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord:
    id: str
    delegation_id: str
    downstream_task_id: str
    source_application_id: str
    source_decision_id: str
    source_downstream_result_id: str
    source_effect_id: str
    source_delegation_id: str
    source_downstream_task_id: str
    source_followup_result_id: str
    upstream_followup_effect_id: str
    source_contract_id: str
    goal_id: str
    project_id: str
    capability: str
    assigned_profile: str
    evidence_status: str
    result_summary: str
    evidence_path: str
    result_json: dict[str, object]
    idempotency_key: str
    activation_allowed: bool
    capability_enabled: bool
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskResultBatch:
    id: str
    status: str
    completed_delegation_count: int
    result_record_count: int
    existing_result_record_count: int
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    created_result_ids: list[str]
    completed_delegation_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultEffectTaskResultDecision:
    id: str
    status: str
    operator_id: str
    selected_action: str
    selection_note: str
    evidence_reference: str
    result_record_count: int
    decision_count: int
    accepted_keep_blocked_decision_count: int
    more_evidence_decision_count: int
    deferred_decision_count: int
    existing_decision_count: int
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    decided_result_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultRecord:
    id: str
    delegation_id: str
    downstream_task_id: str
    source_result_id: str
    source_effect_id: str
    source_contract_id: str
    goal_id: str
    project_id: str
    capability: str
    assigned_profile: str
    evidence_status: str
    result_summary: str
    evidence_path: str
    result_json: dict[str, object]
    idempotency_key: str
    activation_allowed: bool
    capability_enabled: bool
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultBatch:
    id: str
    status: str
    completed_delegation_count: int
    result_record_count: int
    existing_result_record_count: int
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    created_result_ids: list[str]
    completed_delegation_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultTaskResultDecision:
    id: str
    status: str
    operator_id: str
    selected_action: str
    selection_note: str
    evidence_reference: str
    result_record_count: int
    decision_count: int
    accepted_keep_blocked_decision_count: int
    more_evidence_decision_count: int
    deferred_decision_count: int
    existing_decision_count: int
    created_approval_request_count: int
    activation_action_count: int
    external_mutation_count: int
    decided_result_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationTaskBatch:
    id: str
    status: str
    source_application_id: str
    goal_id: str
    applied_capability_effect_count: int
    task_count: int
    existing_task_count: int
    activation_action_count: int
    created_task_ids: list[str]
    source_effect_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationContract:
    id: str
    task_id: str
    goal_id: str
    project_id: str
    capability: str
    source_effect_id: str
    source_application_id: str
    evidence_requirements: dict[str, object]
    approval_boundary: str
    approval_status: str
    required_approval_id: str
    status: str
    activation_allowed: bool
    created_approval_request_count: int
    activation_action_count: int
    report_path: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class CapabilityActivationContractBatch:
    id: str
    status: str
    source_task_batch_id: str
    activation_task_count: int
    contract_count: int
    existing_contract_count: int
    created_approval_request_count: int
    activation_action_count: int
    created_contract_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationEvidenceRecord:
    id: str
    contract_id: str
    task_id: str
    goal_id: str
    project_id: str
    capability: str
    source_effect_id: str
    evidence_kind: str
    evidence_reference: str
    verification_command: str
    verification_status: str
    recorded_by: str
    summary: str
    status: str
    evidence_path: str
    result_json: dict[str, object]
    idempotency_key: str
    created_approval_request_count: int
    activation_action_count: int
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationEvidenceBatch:
    id: str
    status: str
    contract_count: int
    evidence_record_count: int
    existing_evidence_count: int
    created_approval_request_count: int
    activation_action_count: int
    created_evidence_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationDecision:
    id: str
    status: str
    operator_id: str
    selected_action: str
    selection_note: str
    evidence_reference: str
    contract_count: int
    decision_count: int
    approved_decision_count: int
    deferred_decision_count: int
    more_evidence_decision_count: int
    existing_decision_count: int
    created_approval_request_count: int
    activation_action_count: int
    decided_contract_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupTaskBatch:
    id: str
    status: str
    source_decision_id: str
    contract_count: int
    followup_task_count: int
    existing_followup_task_count: int
    created_approval_request_count: int
    activation_action_count: int
    created_task_ids: list[str]
    contract_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupDelegationBatch:
    id: str
    status: str
    followup_task_count: int
    routing_decision_count: int
    delegation_count: int
    existing_delegation_count: int
    execution_started_count: int
    network_action_count: int
    external_mutation_count: int
    activation_action_count: int
    created_routing_decision_ids: list[str]
    created_delegation_ids: list[str]
    followup_task_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultRecord:
    id: str
    delegation_id: str
    followup_task_id: str
    contract_id: str
    decision_id: str
    goal_id: str
    project_id: str
    capability: str
    assigned_profile: str
    evidence_status: str
    result_summary: str
    evidence_path: str
    result_json: dict[str, object]
    idempotency_key: str
    activation_allowed: bool
    capability_enabled: bool
    created_approval_request_count: int
    activation_action_count: int
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultBatch:
    id: str
    status: str
    completed_delegation_count: int
    result_record_count: int
    existing_result_record_count: int
    created_approval_request_count: int
    activation_action_count: int
    created_result_ids: list[str]
    completed_delegation_ids: list[str]
    report_path: str
    created_at: str


@dataclass(frozen=True)
class CapabilityActivationFollowupResultDecision:
    id: str
    status: str
    operator_id: str
    selected_action: str
    selection_note: str
    evidence_reference: str
    result_record_count: int
    decision_count: int
    accepted_keep_blocked_decision_count: int
    more_evidence_decision_count: int
    deferred_decision_count: int
    existing_decision_count: int
    created_approval_request_count: int
    activation_action_count: int
    decided_result_ids: list[str]
    report_path: str
    created_at: str


SAFE_AUTO_TASK_TYPES = {"write_goal_artifact", "record_learning"}
SAFE_AUTO_RISK_LEVELS = {"low"}
APPROVAL_WAITING_STATUS = "waiting_approval"
APPROVAL_POLICY_NAME = "static_dispatch_policy"
APPROVAL_POLICY_VERSION = "v1"


class Storage:
    def __init__(self, db_path: Path):
        self.db_path = db_path

    def initialize(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("pragma journal_mode=wal")
            connection.executescript(
                """
                create table if not exists goals (
                    id text primary key,
                    project_id text not null,
                    description text not null,
                    status text not null,
                    created_at text not null,
                    updated_at text not null
                );

                create table if not exists runs (
                    id text primary key,
                    goal_id text not null,
                    project_id text not null,
                    status text not null,
                    started_at text not null,
                    completed_at text,
                    activity_path text,
                    summary_path text,
                    events_path text
                );

                create table if not exists tasks (
                    id text primary key,
                    run_id text,
                    goal_id text not null,
                    project_id text not null,
                    task_type text not null,
                    description text not null,
                    status text not null,
                    priority integer not null,
                    risk_level text not null,
                    skill_tags text not null,
                    depends_on text not null,
                    owner text,
                    attempts integer not null,
                    verification_plan text not null,
                    evidence text not null,
                    artifacts text not null,
                    created_at text not null,
                    updated_at text not null,
                    claimed_at text
                );

                create table if not exists events (
                    id integer primary key autoincrement,
                    run_id text not null,
                    goal_id text,
                    task_id text,
                    event_type text not null,
                    message text not null,
                    payload text not null,
                    created_at text not null
                );

                create table if not exists learnings (
                    id text primary key,
                    run_id text not null,
                    project_id text not null,
                    summary text not null,
                    source text not null,
                    created_at text not null
                );

                create table if not exists memory_entries (
                    id text primary key,
                    project_id text not null,
                    scope text not null,
                    key text not null,
                    value text not null,
                    source_type text not null,
                    source_id text not null,
                    confidence real not null,
                    status text not null,
                    created_by_profile text not null,
                    artifact_path text not null,
                    approved_by text,
                    approved_at text,
                    archived_by text,
                    archived_at text,
                    archive_reason text,
                    created_at text not null,
                    updated_at text not null,
                    last_used_at text
                );

                create table if not exists skills (
                    id text primary key,
                    project_id text,
                    name text not null,
                    description text not null,
                    path text not null,
                    status text not null,
                    created_by_profile text not null,
                    source_run_id text,
                    source_task_id text,
                    verification_status text not null,
                    approved_by text,
                    approved_at text,
                    archived_by text,
                    archived_at text,
                    archive_reason text,
                    created_at text not null,
                    updated_at text not null,
                    last_used_at text
                );

                create table if not exists skill_versions (
                    id text primary key,
                    skill_id text not null,
                    version integer not null,
                    content_hash text not null,
                    path text not null,
                    change_summary text not null,
                    verification_status text not null,
                    created_at text not null
                );

                create table if not exists eval_results (
                    id text primary key,
                    name text not null,
                    status text not null,
                    details text not null,
                    created_at text not null
                );

                create table if not exists eval_candidates (
                    id text primary key,
                    source_type text not null,
                    source_id text not null,
                    suggested_eval text not null,
                    reason text not null,
                    candidate_path text not null,
                    status text not null,
                    created_at text not null,
                    updated_at text not null,
                    unique(source_type, source_id)
                );

                create table if not exists incidents (
                    id text primary key,
                    project_id text not null,
                    run_id text not null,
                    goal_id text,
                    task_id text,
                    task_type text not null,
                    incident_type text not null,
                    severity text not null,
                    status text not null,
                    summary text not null,
                    failure_class text not null,
                    verification_method text,
                    verification_path text,
                    failed_checks text not null,
                    evidence text not null,
                    artifacts text not null,
                    evidence_path text,
                    created_at text not null,
                    resolved_at text,
                    resolved_by text,
                    resolution_note text,
                    resolution_evidence_path text
                );

                create table if not exists approval_requests (
                    id text primary key,
                    task_id text not null,
                    run_id text,
                    goal_id text not null,
                    project_id text not null,
                    task_type text not null,
                    risk_level text not null,
                    status text not null,
                    reason text not null,
                    policy_name text not null,
                    policy_version text not null,
                    requested_by text not null,
                    decided_by text,
                    decision_note text,
                    requested_at text not null,
                    decided_at text
                );

                create table if not exists registered_projects (
                    name text primary key,
                    root_path text not null,
                    default_test_command text not null,
                    allowed_write_roots text not null,
                    created_at text not null,
                    updated_at text not null
                );

                create table if not exists worktree_records (
                    id text primary key,
                    project_id text not null,
                    task_id text not null,
                    run_id text not null,
                    base_commit text not null,
                    branch_name text not null,
                    worktree_path text not null,
                    created_at text not null
                );

                create table if not exists worktree_cleanup_records (
                    id text primary key,
                    worktree_id text not null,
                    effect_id text not null,
                    project_id text not null,
                    run_id text not null,
                    task_id text not null,
                    worktree_path text not null,
                    branch_name text not null,
                    cleanup_reason text not null,
                    status text not null,
                    decided_by text not null,
                    decision_note text not null,
                    evidence_path text not null,
                    result_json text not null,
                    created_at text not null
                );

                create table if not exists github_handoff_records (
                    id text primary key,
                    effect_id text not null unique,
                    project_id text not null,
                    run_id text not null,
                    task_id text not null,
                    branch_name text not null,
                    commit_sha text not null,
                    remote_name text not null,
                    remote_url text not null,
                    base_branch text not null,
                    status text not null,
                    push_command text not null,
                    draft_pr_command text not null,
                    evidence_path text not null,
                    result_json text not null,
                    created_at text not null
                );

                create table if not exists ci_deploy_evidence_records (
                    id text primary key,
                    github_handoff_id text not null,
                    effect_id text not null,
                    project_id text not null,
                    run_id text not null,
                    task_id text not null,
                    branch_name text not null,
                    commit_sha text not null,
                    provider text not null,
                    external_run_id text not null,
                    external_url text not null,
                    status text not null,
                    recorded_by text not null,
                    evidence_path text not null,
                    result_json text not null,
                    idempotency_key text not null unique,
                    created_at text not null
                );

                create table if not exists profiles (
                    id text primary key,
                    name text not null unique,
                    label text not null,
                    model text not null,
                    cost_tier text not null,
                    mode text not null,
                    tools_json text not null,
                    permissions_json text not null,
                    use_for_json text not null,
                    max_budget_json text not null,
                    enabled integer not null,
                    created_at text not null,
                    updated_at text not null
                );

                create table if not exists routing_rules (
                    id text primary key,
                    category text not null unique,
                    preferred_profile text not null,
                    fallback_profile text not null,
                    confidence_threshold real,
                    created_at text not null,
                    updated_at text not null
                );

                create table if not exists routing_decisions (
                    id text primary key,
                    task_id text,
                    goal_id text,
                    project_id text,
                    selected_profile text not null,
                    selected_model text not null,
                    category text not null,
                    reason text not null,
                    estimated_cost_tier text not null,
                    actual_cost real,
                    status text not null,
                    created_at text not null
                );

                create table if not exists subagent_delegations (
                    id text primary key,
                    routing_decision_id text,
                    parent_goal_id text not null,
                    parent_task_id text not null,
                    assigned_profile text not null,
                    category text not null,
                    title text not null,
                    prompt text not null,
                    input_context_json text not null,
                    allowed_tools_json text not null,
                    forbidden_actions_json text not null,
                    expected_output_schema text not null,
                    budget_json text not null,
                    status text not null,
                    result_summary text,
                    result_artifact_path text not null,
                    created_at text not null,
                    started_at text,
                    completed_at text
                );

                create table if not exists effects (
                    id text primary key,
                    run_id text not null,
                    task_id text not null,
                    project_id text not null,
                    capability text not null,
                    effect_type text not null,
                    idempotency_key text not null,
                    target text not null,
                    proposed_payload_json text not null,
                    status text not null,
                    required_approval_id text,
                    attempted_at text,
                    committed_at text,
                    evidence_path text not null,
                    compensation_plan_json text not null,
                    result_json text not null default '{}',
                    created_at text not null,
                    updated_at text not null,
                    unique(idempotency_key)
                );

                create table if not exists iteration_packets (
                    id text primary key,
                    focus text not null,
                    source_path text not null,
                    source_section text not null,
                    status text not null,
                    packet_path text not null,
                    verification_commands text not null,
                    selection_policy text not null,
                    selection_reason text not null,
                    selected_score integer not null,
                    selected_complexity integer not null,
                    created_at text not null
                );

                create table if not exists playbooks (
                    id text primary key,
                    slug text not null unique,
                    title text not null,
                    source_eval_name text not null,
                    successful_run_count integer not null,
                    playbook_path text not null,
                    status text not null,
                    created_at text not null,
                    updated_at text not null
                );

                create table if not exists handoff_reviews (
                    id text primary key,
                    status text not null,
                    current_focus text not null,
                    blocked_task_count integer not null,
                    stale_handoff_count integer not null,
                    blocked_tasks text not null,
                    stale_handoffs text not null,
                    reviewed_paths text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists eval_after_change_checks (
                    id text primary key,
                    change_summary text not null,
                    changed_paths text not null,
                    eval_names text not null,
                    status text not null,
                    result_paths text not null,
                    run_ids text not null,
                    report_path text not null,
                    command text not null,
                    created_at text not null,
                    completed_at text not null
                );

                create table if not exists learning_distillations (
                    id text primary key,
                    status text not null,
                    min_occurrences integer not null,
                    stable_learning_count integer not null,
                    stable_learnings text not null,
                    source_learning_count integer not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists budget_trust_posture_reports (
                    id text primary key,
                    status text not null,
                    task_count integer not null,
                    risk_counts text not null,
                    budget_state text not null,
                    budget_summary text not null,
                    trust_state text not null,
                    trust_summary text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists dispatch_posture_history_summaries (
                    id text primary key,
                    status text not null,
                    snapshot_count integer not null,
                    latest_task_count integer not null,
                    task_count_delta integer not null,
                    latest_risk_counts text not null,
                    budget_states text not null,
                    trust_states text not null,
                    first_snapshot_at text,
                    latest_snapshot_at text,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists dispatch_posture_staleness_reviews (
                    id text primary key,
                    status text not null,
                    snapshot_count integer not null,
                    stale_snapshot_count integer not null,
                    latest_snapshot_age_seconds integer,
                    stale_after_seconds integer not null,
                    latest_task_count integer not null,
                    latest_risk_counts text not null,
                    latest_snapshot_at text,
                    oldest_snapshot_at text,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists dispatch_posture_refresh_recommendations (
                    id text primary key,
                    status text not null,
                    source_review_id text,
                    source_review_status text not null,
                    snapshot_count integer not null,
                    stale_snapshot_count integer not null,
                    latest_snapshot_age_seconds integer,
                    stale_after_seconds integer not null,
                    latest_snapshot_at text,
                    recommended_commands text not null,
                    reason text not null,
                    approval_boundary text not null,
                    deferred_capabilities text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_expansion_ledgers (
                    id text primary key,
                    status text not null,
                    capability_count integer not null,
                    ready_count integer not null,
                    deferred_count integer not null,
                    approval_boundary text not null,
                    capabilities text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_readiness_reviews (
                    id text primary key,
                    status text not null,
                    source_ledger_id text,
                    source_ledger_status text not null,
                    capability_count integer not null,
                    ready_count integer not null,
                    not_ready_count integer not null,
                    missing_evidence_count integer not null,
                    approval_boundary text not null,
                    recommended_commands text not null,
                    reason text not null,
                    review_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_proof_gap_indexes (
                    id text primary key,
                    status text not null,
                    source_review_id text,
                    source_review_status text not null,
                    capability_count integer not null,
                    gap_count integer not null,
                    missing_evidence_count integer not null,
                    blocked_capability_count integer not null,
                    next_proof_count integer not null,
                    approval_boundary text not null,
                    recommended_commands text not null,
                    reason text not null,
                    proof_gaps text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_approval_boundary_matrices (
                    id text primary key,
                    status text not null,
                    source_index_id text,
                    source_index_status text not null,
                    capability_count integer not null,
                    boundary_count integer not null,
                    gap_count integer not null,
                    blocked_capability_count integer not null,
                    approval_required_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    boundary_rows text not null,
                    matrix_entries text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_evidence_collection_plans (
                    id text primary key,
                    status text not null,
                    source_matrix_id text,
                    source_matrix_status text not null,
                    capability_count integer not null,
                    evidence_item_count integer not null,
                    manual_collection_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    evidence_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_promotion_gate_checklists (
                    id text primary key,
                    status text not null,
                    source_plan_id text,
                    source_plan_status text not null,
                    capability_count integer not null,
                    gate_count integer not null,
                    blocked_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_promotion_decision_ledgers (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    decision_count integer not null,
                    deferred_promotion_count integer not null,
                    operator_decision_required_count integer not null,
                    blocked_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    decision_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_trust_promotion_audits (
                    id text primary key,
                    status text not null,
                    source_ledger_id text,
                    source_ledger_status text not null,
                    capability_count integer not null,
                    audit_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    operator_review_required_count integer not null,
                    deferred_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    audit_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_automatic_retry_audits (
                    id text primary key,
                    status text not null,
                    source_audit_id text,
                    source_audit_status text not null,
                    capability_count integer not null,
                    audit_count integer not null,
                    blocked_retry_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    deferred_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    audit_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_real_cost_tracking_audits (
                    id text primary key,
                    status text not null,
                    source_audit_id text,
                    source_audit_status text not null,
                    capability_count integer not null,
                    audit_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    deferred_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    audit_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists hosted_dashboard_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_audit_id text,
                    source_audit_status text not null,
                    source_kind text,
                    source_checklist_id text,
                    source_checklist_status text,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists remote_worker_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_worker_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists autonomous_scheduling_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_scheduling_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_worker_proof_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists browser_desktop_adapter_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_adapter_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_scheduling_proof_count integer not null,
                    blocked_worker_proof_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists ci_deploy_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_ci_deploy_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_adapter_proof_count integer not null,
                    blocked_scheduling_proof_count integer not null,
                    blocked_worker_proof_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists budget_enforcement_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_budget_enforcement_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_ci_deploy_proof_count integer not null,
                    blocked_adapter_proof_count integer not null,
                    blocked_scheduling_proof_count integer not null,
                    blocked_worker_proof_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists trust_promotion_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_trust_promotion_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_budget_enforcement_proof_count integer not null,
                    blocked_ci_deploy_proof_count integer not null,
                    blocked_adapter_proof_count integer not null,
                    blocked_scheduling_proof_count integer not null,
                    blocked_worker_proof_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists automatic_retry_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_automatic_retry_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_trust_promotion_proof_count integer not null,
                    blocked_budget_enforcement_proof_count integer not null,
                    blocked_ci_deploy_proof_count integer not null,
                    blocked_adapter_proof_count integer not null,
                    blocked_scheduling_proof_count integer not null,
                    blocked_worker_proof_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists real_cost_tracking_proof_checklists (
                    id text primary key,
                    status text not null,
                    source_checklist_id text,
                    source_checklist_status text not null,
                    capability_count integer not null,
                    checklist_count integer not null,
                    blocked_real_cost_tracking_proof_count integer not null,
                    operator_review_required_count integer not null,
                    blocked_automatic_retry_proof_count integer not null,
                    blocked_trust_promotion_proof_count integer not null,
                    blocked_budget_enforcement_proof_count integer not null,
                    blocked_ci_deploy_proof_count integer not null,
                    blocked_adapter_proof_count integer not null,
                    blocked_scheduling_proof_count integer not null,
                    blocked_worker_proof_count integer not null,
                    blocked_dashboard_proof_count integer not null,
                    blocked_cost_tracking_count integer not null,
                    blocked_retry_count integer not null,
                    blocked_trust_promotion_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    boundary_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    checklist_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists goal_completion_audits (
                    id text primary key,
                    status text not null,
                    requirement_count integer not null,
                    satisfied_requirement_count integer not null,
                    blocked_requirement_count integer not null,
                    missing_evidence_count integer not null,
                    approval_required_count integer not null,
                    external_decision_count integer not null,
                    recommended_commands text not null,
                    reason text not null,
                    audit_items text not null,
                    external_decisions text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_decision_briefs (
                    id text primary key,
                    status text not null,
                    source_audit_id text not null,
                    source_audit_status text not null,
                    requirement_count integer not null,
                    blocked_requirement_count integer not null,
                    external_decision_count integer not null,
                    approval_required_count integer not null,
                    decision_item_count integer not null,
                    recommended_next_step text not null,
                    decision_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_decision_evidence_indexes (
                    id text primary key,
                    status text not null,
                    source_brief_id text not null,
                    source_brief_status text not null,
                    source_audit_id text not null,
                    decision_item_count integer not null,
                    evidence_item_count integer not null,
                    external_decision_count integer not null,
                    capability_decision_count integer not null,
                    missing_evidence_link_count integer not null,
                    recommended_next_step text not null,
                    evidence_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_review_checklists (
                    id text primary key,
                    status text not null,
                    source_index_id text not null,
                    source_index_status text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    review_item_count integer not null,
                    decision_required_count integer not null,
                    external_review_count integer not null,
                    capability_review_count integer not null,
                    missing_evidence_link_count integer not null,
                    allowed_actions text not null,
                    recommended_next_step text not null,
                    review_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_decision_ledgers (
                    id text primary key,
                    status text not null,
                    source_checklist_id text not null,
                    source_checklist_status text not null,
                    source_index_id text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    decision_item_count integer not null,
                    pending_decision_count integer not null,
                    approved_decision_count integer not null,
                    deferred_decision_count integer not null,
                    more_evidence_requested_count integer not null,
                    external_decision_count integer not null,
                    capability_decision_count integer not null,
                    allowed_actions text not null,
                    recommended_next_step text not null,
                    decision_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_drafts (
                    id text primary key,
                    status text not null,
                    source_ledger_id text not null,
                    source_ledger_status text not null,
                    source_checklist_id text not null,
                    source_index_id text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    draft_item_count integer not null,
                    draft_request_count integer not null,
                    created_approval_request_count integer not null,
                    external_draft_count integer not null,
                    capability_draft_count integer not null,
                    approval_boundary_count integer not null,
                    pending_decision_count integer not null,
                    allowed_actions text not null,
                    recommended_next_step text not null,
                    draft_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_request_reviews (
                    id text primary key,
                    status text not null,
                    source_draft_id text not null,
                    source_draft_status text not null,
                    source_ledger_id text not null,
                    source_checklist_id text not null,
                    source_index_id text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    draft_request_count integer not null,
                    review_item_count integer not null,
                    ready_request_count integer not null,
                    blocked_request_count integer not null,
                    schema_gap_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    external_request_count integer not null,
                    capability_request_count integer not null,
                    approval_boundary_count integer not null,
                    recommended_next_step text not null,
                    review_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_schema_decisions (
                    id text primary key,
                    status text not null,
                    source_review_id text not null,
                    source_review_status text not null,
                    source_draft_id text not null,
                    source_ledger_id text not null,
                    source_checklist_id text not null,
                    source_index_id text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    affected_request_count integer not null,
                    schema_gap_count integer not null,
                    missing_field_count integer not null,
                    missing_fields text not null,
                    external_request_count integer not null,
                    capability_request_count integer not null,
                    decision_option_count integer not null,
                    recommended_option text not null,
                    rejected_option_count integer not null,
                    schema_object_count integer not null,
                    migration_applied_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    recommended_next_step text not null,
                    decision_options text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_schema_migration_plans (
                    id text primary key,
                    status text not null,
                    source_decision_id text not null,
                    source_decision_status text not null,
                    source_review_id text not null,
                    source_review_status text not null,
                    source_draft_id text not null,
                    source_ledger_id text not null,
                    source_checklist_id text not null,
                    source_index_id text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    recommended_option text not null,
                    target_table text not null,
                    affected_request_count integer not null,
                    schema_gap_count integer not null,
                    missing_field_count integer not null,
                    external_request_count integer not null,
                    capability_request_count integer not null,
                    planned_column_count integer not null,
                    planned_index_count integer not null,
                    migration_step_count integer not null,
                    migration_applied_count integer not null,
                    table_created_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    recommended_next_step text not null,
                    planned_columns text not null,
                    planned_indexes text not null,
                    migration_steps text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_schema_migration_approval_requests (
                    id text primary key,
                    status text not null,
                    source_plan_id text not null,
                    source_plan_status text not null,
                    source_decision_id text not null,
                    source_decision_status text not null,
                    source_review_id text not null,
                    source_review_status text not null,
                    target_table text not null,
                    planned_column_count integer not null,
                    planned_index_count integer not null,
                    migration_step_count integer not null,
                    affected_request_count integer not null,
                    schema_gap_count integer not null,
                    request_count integer not null,
                    approval_boundary text not null,
                    requested_action text not null,
                    allowed_actions text not null,
                    migration_applied_count integer not null,
                    table_created_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    recommended_next_step text not null,
                    approval_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_schema_migration_decision_ledgers (
                    id text primary key,
                    status text not null,
                    source_request_id text not null,
                    source_request_status text not null,
                    source_plan_id text not null,
                    source_plan_status text not null,
                    source_decision_id text not null,
                    source_decision_status text not null,
                    source_review_id text not null,
                    source_review_status text not null,
                    target_table text not null,
                    planned_column_count integer not null,
                    planned_index_count integer not null,
                    migration_step_count integer not null,
                    affected_request_count integer not null,
                    schema_gap_count integer not null,
                    request_count integer not null,
                    decision_count integer not null,
                    pending_decision_count integer not null,
                    approved_decision_count integer not null,
                    deferred_decision_count integer not null,
                    more_evidence_decision_count integer not null,
                    approval_boundary text not null,
                    requested_action text not null,
                    allowed_actions text not null,
                    migration_applied_count integer not null,
                    table_created_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    recommended_next_step text not null,
                    decision_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_schema_migration_action_checklists (
                    id text primary key,
                    status text not null,
                    source_ledger_id text not null,
                    source_ledger_status text not null,
                    source_request_id text not null,
                    source_request_status text not null,
                    source_plan_id text not null,
                    source_plan_status text not null,
                    source_decision_id text not null,
                    source_decision_status text not null,
                    source_review_id text not null,
                    source_review_status text not null,
                    target_table text not null,
                    request_count integer not null,
                    decision_count integer not null,
                    pending_decision_count integer not null,
                    action_count integer not null,
                    pending_action_count integer not null,
                    actions_taken_count integer not null,
                    selected_action text not null,
                    approval_boundary text not null,
                    requested_action text not null,
                    allowed_actions text not null,
                    migration_applied_count integer not null,
                    table_created_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    recommended_next_step text not null,
                    action_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_schema_migration_selection_packets (
                    id text primary key,
                    status text not null,
                    source_checklist_id text not null,
                    source_checklist_status text not null,
                    source_ledger_id text not null,
                    source_ledger_status text not null,
                    source_request_id text not null,
                    source_request_status text not null,
                    source_plan_id text not null,
                    source_plan_status text not null,
                    source_decision_id text not null,
                    source_decision_status text not null,
                    source_review_id text not null,
                    source_review_status text not null,
                    target_table text not null,
                    request_count integer not null,
                    decision_count integer not null,
                    pending_decision_count integer not null,
                    action_count integer not null,
                    pending_action_count integer not null,
                    actions_taken_count integer not null,
                    selected_action text not null,
                    selection_count integer not null,
                    pending_selection_count integer not null,
                    selections_recorded_count integer not null,
                    approve_selection_count integer not null,
                    defer_selection_count integer not null,
                    more_evidence_selection_count integer not null,
                    approval_boundary text not null,
                    requested_action text not null,
                    allowed_actions text not null,
                    migration_applied_count integer not null,
                    table_created_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    recommended_next_step text not null,
                    selection_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists expansion_operator_approval_schema_migration_selection_input_templates (
                    id text primary key,
                    status text not null,
                    source_packet_id text not null,
                    source_packet_status text not null,
                    source_checklist_id text not null,
                    source_checklist_status text not null,
                    source_ledger_id text not null,
                    source_ledger_status text not null,
                    source_request_id text not null,
                    source_request_status text not null,
                    source_plan_id text not null,
                    source_plan_status text not null,
                    source_decision_id text not null,
                    source_decision_status text not null,
                    source_review_id text not null,
                    source_review_status text not null,
                    target_table text not null,
                    request_count integer not null,
                    decision_count integer not null,
                    pending_decision_count integer not null,
                    action_count integer not null,
                    pending_action_count integer not null,
                    actions_taken_count integer not null,
                    selected_action text not null,
                    selection_count integer not null,
                    pending_selection_count integer not null,
                    selections_recorded_count integer not null,
                    approve_selection_count integer not null,
                    defer_selection_count integer not null,
                    more_evidence_selection_count integer not null,
                    template_count integer not null,
                    pending_input_count integer not null,
                    inputs_recorded_count integer not null,
                    required_fields_count integer not null,
                    missing_required_input_count integer not null,
                    approval_boundary text not null,
                    requested_action text not null,
                    allowed_actions text not null,
                    migration_applied_count integer not null,
                    table_created_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    recommended_next_step text not null,
                    input_template_items text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists operator_approval_schema_migration_applications (
                    id text primary key,
                    status text not null,
                    source_template_id text not null,
                    source_template_status text not null,
                    source_packet_id text not null,
                    source_checklist_id text not null,
                    source_ledger_id text not null,
                    source_request_id text not null,
                    source_plan_id text not null,
                    source_decision_id text not null,
                    source_review_id text not null,
                    target_table text not null,
                    operator_id text not null,
                    selected_action text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    inputs_recorded_count integer not null,
                    missing_required_input_count integer not null,
                    actions_taken_count integer not null,
                    migration_applied_count integer not null,
                    table_created_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_approval_request_count integer not null,
                    applied_table_columns text not null,
                    applied_indexes text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists operator_approval_request_row_applications (
                    id text primary key,
                    status text not null,
                    source_draft_id text not null,
                    source_draft_status text not null,
                    source_schema_application_id text not null,
                    source_schema_application_status text not null,
                    source_ledger_id text not null,
                    source_checklist_id text not null,
                    source_index_id text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    operator_id text not null,
                    selected_action text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    draft_request_count integer not null,
                    operator_approval_row_count integer not null,
                    created_approval_request_count integer not null,
                    existing_operator_approval_request_count integer not null,
                    external_request_count integer not null,
                    capability_request_count integer not null,
                    created_request_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists operator_approval_request_decisions (
                    id text primary key,
                    status text not null,
                    source_row_application_id text not null,
                    source_row_application_status text not null,
                    source_draft_id text not null,
                    source_schema_application_id text not null,
                    source_ledger_id text not null,
                    source_checklist_id text not null,
                    source_index_id text not null,
                    source_brief_id text not null,
                    source_audit_id text not null,
                    operator_id text not null,
                    selected_action text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    pending_request_count_before integer not null,
                    decision_count integer not null,
                    approved_decision_count integer not null,
                    deferred_decision_count integer not null,
                    more_evidence_decision_count integer not null,
                    pending_request_count_after integer not null,
                    existing_decision_count integer not null,
                    created_approval_request_count integer not null,
                    external_request_count integer not null,
                    capability_request_count integer not null,
                    decided_request_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists operator_approval_effect_applications (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    proposed_effect_count integer not null,
                    applied_effect_count integer not null,
                    existing_applied_effect_count integer not null,
                    external_effect_count integer not null,
                    capability_effect_count integer not null,
                    legacy_approval_request_count integer not null,
                    activation_action_count integer not null,
                    applied_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_effect_applications (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    proposed_effect_count integer not null,
                    applied_effect_count integer not null,
                    existing_applied_effect_count integer not null,
                    capability_effect_count integer not null,
                    approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    applied_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_applications (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    proposed_effect_count integer not null,
                    applied_effect_count integer not null,
                    existing_applied_effect_count integer not null,
                    capability_effect_count integer not null,
                    approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    applied_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_task_result_effect_applications (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    proposed_effect_count integer not null,
                    applied_effect_count integer not null,
                    existing_applied_effect_count integer not null,
                    capability_effect_count integer not null,
                    approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    applied_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_task_result_effect_task_batches (
                    id text primary key,
                    status text not null,
                    source_application_id text not null,
                    applied_downstream_effect_count integer not null,
                    task_count integer not null,
                    existing_task_count integer not null,
                    capability_task_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    created_task_ids text not null,
                    source_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_task_batches (
                    id text primary key,
                    status text not null,
                    source_application_id text not null,
                    applied_downstream_effect_count integer not null,
                    task_count integer not null,
                    existing_task_count integer not null,
                    capability_task_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    created_task_ids text not null,
                    source_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_batches (
                    id text primary key,
                    status text not null,
                    source_application_id text not null,
                    applied_followup_effect_count integer not null,
                    task_count integer not null,
                    existing_task_count integer not null,
                    capability_task_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    created_task_ids text not null,
                    source_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_delegation_batches (
                    id text primary key,
                    status text not null,
                    downstream_task_count integer not null,
                    routing_decision_count integer not null,
                    delegation_count integer not null,
                    existing_delegation_count integer not null,
                    execution_started_count integer not null,
                    network_action_count integer not null,
                    external_mutation_count integer not null,
                    activation_action_count integer not null,
                    created_routing_decision_ids text not null,
                    created_delegation_ids text not null,
                    downstream_task_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_task_delegation_batches (
                    id text primary key,
                    status text not null,
                    downstream_task_count integer not null,
                    routing_decision_count integer not null,
                    delegation_count integer not null,
                    existing_delegation_count integer not null,
                    execution_started_count integer not null,
                    network_action_count integer not null,
                    external_mutation_count integer not null,
                    activation_action_count integer not null,
                    created_routing_decision_ids text not null,
                    created_delegation_ids text not null,
                    downstream_task_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_task_result_records (
                    id text primary key,
                    delegation_id text not null,
                    downstream_task_id text not null,
                    source_application_id text not null,
                    source_decision_id text not null,
                    source_downstream_result_id text not null,
                    source_effect_id text not null,
                    source_delegation_id text not null,
                    source_downstream_task_id text not null,
                    source_followup_result_id text not null,
                    upstream_followup_effect_id text not null,
                    source_contract_id text not null,
                    goal_id text not null,
                    project_id text not null,
                    capability text not null,
                    assigned_profile text not null,
                    evidence_status text not null,
                    result_summary text not null,
                    evidence_path text not null,
                    result_json text not null,
                    idempotency_key text not null unique,
                    activation_allowed integer not null,
                    capability_enabled integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_task_result_batches (
                    id text primary key,
                    status text not null,
                    completed_delegation_count integer not null,
                    result_record_count integer not null,
                    existing_result_record_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    created_result_ids text not null,
                    completed_delegation_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_effect_task_result_decisions (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selected_action text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    result_record_count integer not null,
                    decision_count integer not null,
                    accepted_keep_blocked_decision_count integer not null,
                    more_evidence_decision_count integer not null,
                    deferred_decision_count integer not null,
                    existing_decision_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    decided_result_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_records (
                    id text primary key,
                    delegation_id text not null,
                    downstream_task_id text not null,
                    source_result_id text not null,
                    source_effect_id text not null,
                    source_contract_id text not null,
                    goal_id text not null,
                    project_id text not null,
                    capability text not null,
                    assigned_profile text not null,
                    evidence_status text not null,
                    result_summary text not null,
                    evidence_path text not null,
                    result_json text not null,
                    idempotency_key text not null unique,
                    activation_allowed integer not null,
                    capability_enabled integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_batches (
                    id text primary key,
                    status text not null,
                    completed_delegation_count integer not null,
                    result_record_count integer not null,
                    existing_result_record_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    created_result_ids text not null,
                    completed_delegation_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_task_result_decisions (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selected_action text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    result_record_count integer not null,
                    decision_count integer not null,
                    accepted_keep_blocked_decision_count integer not null,
                    more_evidence_decision_count integer not null,
                    deferred_decision_count integer not null,
                    existing_decision_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    external_mutation_count integer not null,
                    decided_result_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_task_batches (
                    id text primary key,
                    status text not null,
                    source_application_id text not null,
                    goal_id text not null,
                    applied_capability_effect_count integer not null,
                    task_count integer not null,
                    existing_task_count integer not null,
                    activation_action_count integer not null,
                    created_task_ids text not null,
                    source_effect_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_contracts (
                    id text primary key,
                    task_id text not null unique,
                    goal_id text not null,
                    project_id text not null,
                    capability text not null,
                    source_effect_id text not null,
                    source_application_id text not null,
                    evidence_requirements_json text not null,
                    approval_boundary text not null,
                    approval_status text not null,
                    required_approval_id text not null,
                    status text not null,
                    activation_allowed integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    report_path text not null,
                    created_at text not null,
                    updated_at text not null
                );

                create table if not exists capability_activation_contract_batches (
                    id text primary key,
                    status text not null,
                    source_task_batch_id text not null,
                    activation_task_count integer not null,
                    contract_count integer not null,
                    existing_contract_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    created_contract_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_evidence_records (
                    id text primary key,
                    contract_id text not null,
                    task_id text not null,
                    goal_id text not null,
                    project_id text not null,
                    capability text not null,
                    source_effect_id text not null,
                    evidence_kind text not null,
                    evidence_reference text not null,
                    verification_command text not null,
                    verification_status text not null,
                    recorded_by text not null,
                    summary text not null,
                    status text not null,
                    evidence_path text not null,
                    result_json text not null,
                    idempotency_key text not null unique,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    created_at text not null
                );

                create table if not exists capability_activation_evidence_batches (
                    id text primary key,
                    status text not null,
                    contract_count integer not null,
                    evidence_record_count integer not null,
                    existing_evidence_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    created_evidence_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_decisions (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selected_action text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    contract_count integer not null,
                    decision_count integer not null,
                    approved_decision_count integer not null,
                    deferred_decision_count integer not null,
                    more_evidence_decision_count integer not null,
                    existing_decision_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    decided_contract_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_task_batches (
                    id text primary key,
                    status text not null,
                    source_decision_id text not null,
                    contract_count integer not null,
                    followup_task_count integer not null,
                    existing_followup_task_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    created_task_ids text not null,
                    contract_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_delegation_batches (
                    id text primary key,
                    status text not null,
                    followup_task_count integer not null,
                    routing_decision_count integer not null,
                    delegation_count integer not null,
                    existing_delegation_count integer not null,
                    execution_started_count integer not null,
                    network_action_count integer not null,
                    external_mutation_count integer not null,
                    activation_action_count integer not null,
                    created_routing_decision_ids text not null,
                    created_delegation_ids text not null,
                    followup_task_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_records (
                    id text primary key,
                    delegation_id text not null,
                    followup_task_id text not null,
                    contract_id text not null,
                    decision_id text not null,
                    goal_id text not null,
                    project_id text not null,
                    capability text not null,
                    assigned_profile text not null,
                    evidence_status text not null,
                    result_summary text not null,
                    evidence_path text not null,
                    result_json text not null,
                    idempotency_key text not null unique,
                    activation_allowed integer not null,
                    capability_enabled integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_batches (
                    id text primary key,
                    status text not null,
                    completed_delegation_count integer not null,
                    result_record_count integer not null,
                    existing_result_record_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    created_result_ids text not null,
                    completed_delegation_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists capability_activation_followup_result_decisions (
                    id text primary key,
                    status text not null,
                    operator_id text not null,
                    selected_action text not null,
                    selection_note text not null,
                    evidence_reference text not null,
                    result_record_count integer not null,
                    decision_count integer not null,
                    accepted_keep_blocked_decision_count integer not null,
                    more_evidence_decision_count integer not null,
                    deferred_decision_count integer not null,
                    existing_decision_count integer not null,
                    created_approval_request_count integer not null,
                    activation_action_count integer not null,
                    decided_result_ids text not null,
                    report_path text not null,
                    created_at text not null
                );

                create table if not exists steering_reviews (
                    id text primary key,
                    goal_id text not null,
                    project_id text not null,
                    run_id text,
                    reviewed_plan_version text not null,
                    current_task_id text,
                    status text not null,
                    drift_score text not null,
                    findings_json text not null,
                    recommended_next_action text not null,
                    requires_operator integer not null,
                    report_path text not null,
                    created_at text not null
                );
                """
            )
            self._ensure_column(connection, "tasks", "run_id", "text")
            self._ensure_column(connection, "incidents", "resolved_by", "text")
            self._ensure_column(connection, "incidents", "resolution_note", "text")
            self._ensure_column(connection, "incidents", "resolution_evidence_path", "text")
            self._ensure_column(connection, "approval_requests", "policy_name", "text")
            self._ensure_column(connection, "approval_requests", "policy_version", "text")
            self._ensure_column(connection, "iteration_packets", "selection_policy", "text")
            self._ensure_column(connection, "iteration_packets", "selection_reason", "text")
            self._ensure_column(connection, "hosted_dashboard_proof_checklists", "source_kind", "text")
            self._ensure_column(connection, "hosted_dashboard_proof_checklists", "source_checklist_id", "text")
            self._ensure_column(connection, "hosted_dashboard_proof_checklists", "source_checklist_status", "text")
            self._ensure_column(connection, "iteration_packets", "selected_score", "integer")
            self._ensure_column(connection, "iteration_packets", "selected_complexity", "integer")
            self._ensure_column(connection, "effects", "result_json", "text not null default '{}'")
            self._ensure_column(connection, "memory_entries", "artifact_path", "text not null default ''")
            self._ensure_column(connection, "memory_entries", "approved_by", "text")
            self._ensure_column(connection, "memory_entries", "approved_at", "text")
            self._ensure_column(connection, "memory_entries", "archived_by", "text")
            self._ensure_column(connection, "memory_entries", "archived_at", "text")
            self._ensure_column(connection, "memory_entries", "archive_reason", "text")
            self._allow_nullable_dispatch_posture_staleness_age(connection)
            connection.execute(
                """
                update approval_requests
                set policy_name = ?
                where policy_name is null or policy_name = ''
                """,
                (APPROVAL_POLICY_NAME,),
            )
            connection.execute(
                """
                update approval_requests
                set policy_version = ?
                where policy_version is null or policy_version = ''
                """,
                (APPROVAL_POLICY_VERSION,),
            )
            connection.execute(
                """
                update iteration_packets
                set selection_policy = ?
                where selection_policy is null or selection_policy = ''
                """,
                ("highest-score-then-lowest-complexity",),
            )
            connection.execute(
                """
                update iteration_packets
                set selection_reason = ?
                where selection_reason is null or selection_reason = ''
                """,
                ("legacy packet created before selection metadata was recorded",),
            )
            connection.execute(
                """
                update iteration_packets
                set selected_score = 0
                where selected_score is null
                """
            )
            connection.execute(
                """
                update iteration_packets
                set selected_complexity = 0
                where selected_complexity is null
                """
            )

    def create_goal(self, project_id: str, description: str) -> str:
        goal_id = new_id("goal")
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into goals (id, project_id, description, status, created_at, updated_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (goal_id, project_id, description, "accepted", now, now),
            )
        return goal_id

    def get_or_create_goal(self, project_id: str, description: str) -> str:
        with self._connect() as connection:
            row = connection.execute(
                """
                select id from goals
                where project_id = ? and description = ?
                order by created_at asc, id asc
                limit 1
                """,
                (project_id, description),
            ).fetchone()
            if row is not None:
                return row["id"]
            goal_id = new_id("goal")
            now = utc_now()
            connection.execute(
                """
                insert into goals (id, project_id, description, status, created_at, updated_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (goal_id, project_id, description, "accepted", now, now),
            )
        return goal_id

    def get_goal(self, goal_id: str) -> GoalRecord:
        with self._connect() as connection:
            row = connection.execute(
                "select * from goals where id = ?",
                (goal_id,),
            ).fetchone()
        if row is None:
            raise KeyError(goal_id)
        return self._row_to_goal(row)

    def set_goal_status(self, goal_id: str, status: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "update goals set status = ?, updated_at = ? where id = ?",
                (status, utc_now(), goal_id),
            )

    def create_run(self, goal_id: str, project_id: str, runs_root: Path) -> str:
        run_id = new_id("run")
        run_dir = runs_root / run_id
        with self._connect() as connection:
            connection.execute(
                """
                insert into runs (
                    id, goal_id, project_id, status, started_at,
                    activity_path, summary_path, events_path
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    goal_id,
                    project_id,
                    "running",
                    utc_now(),
                    str(run_dir / "activity.md"),
                    str(run_dir / "summary.md"),
                    str(run_dir / "events.jsonl"),
                ),
            )
        return run_id

    def get_run(self, run_id: str) -> RunRecord:
        with self._connect() as connection:
            row = connection.execute(
                "select * from runs where id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            raise KeyError(run_id)
        return self._row_to_run(row)

    def list_recent_runs(self, limit: int = 5) -> list[RunRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from runs
                order by started_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_run(row) for row in rows]

    def latest_goal_for_project(self, project_id: str) -> GoalRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from goals
                where project_id = ?
                order by updated_at desc, created_at desc, id desc
                limit 1
                """,
                (project_id,),
            ).fetchone()
        return self._row_to_goal(row) if row else None

    def complete_run(self, run_id: str, status: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "update runs set status = ?, completed_at = ? where id = ?",
                (status, utc_now(), run_id),
            )

    def create_task(
        self,
        *,
        goal_id: str,
        project_id: str,
        task_type: str,
        description: str,
        verification_plan: dict[str, Any],
        run_id: str | None = None,
        depends_on: list[str] | None = None,
        skill_tags: list[str] | None = None,
        priority: int = 100,
        risk_level: str = "low",
        evidence: dict[str, Any] | None = None,
        artifacts: list[str] | None = None,
    ) -> str:
        task_id = new_id("task")
        now = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into tasks (
                    id, run_id, goal_id, project_id, task_type, description, status,
                    priority, risk_level, skill_tags, depends_on, attempts,
                    verification_plan, evidence, artifacts, created_at, updated_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task_id,
                    run_id,
                    goal_id,
                    project_id,
                    task_type,
                    description,
                    "pending",
                    priority,
                    risk_level,
                    _json_dumps(skill_tags or ["local-files"]),
                    _json_dumps(depends_on or []),
                    0,
                    _json_dumps(verification_plan),
                    _json_dumps(evidence or {}),
                    _json_dumps(artifacts or []),
                    now,
                    now,
                ),
            )
        return task_id

    def claim_next_task(self, worker_id: str, skill_tags: list[str]) -> Task | None:
        worker_skills = set(skill_tags)
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from tasks
                where status = 'pending'
                order by priority asc, created_at asc, id asc
                """
            ).fetchall()

            for row in rows:
                task = self._row_to_task(row)
                if not set(task.skill_tags).issubset(worker_skills):
                    continue
                if not self._dependencies_completed(connection, task.depends_on):
                    continue
                if self._approval_required(connection, task):
                    self._ensure_pending_approval_request(connection, task)
                    now = utc_now()
                    connection.execute(
                        """
                        update tasks
                        set status = ?, updated_at = ?
                        where id = ? and status = 'pending'
                        """,
                        (APPROVAL_WAITING_STATUS, now, task.id),
                    )
                    continue

                now = utc_now()
                result = connection.execute(
                    """
                    update tasks
                    set status = 'claimed', owner = ?, attempts = attempts + 1,
                        claimed_at = ?, updated_at = ?
                    where id = ? and status = 'pending'
                    """,
                    (worker_id, now, now, task.id),
                )
                if result.rowcount == 1:
                    return self.get_task(task.id, connection=connection)
        return None

    def get_task(
        self,
        task_id: str,
        *,
        connection: sqlite3.Connection | None = None,
    ) -> Task:
        if connection is not None:
            row = connection.execute("select * from tasks where id = ?", (task_id,)).fetchone()
            if row is None:
                raise KeyError(task_id)
            return self._row_to_task(row)

        with self._connect() as owned_connection:
            row = owned_connection.execute(
                "select * from tasks where id = ?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(task_id)
            return self._row_to_task(row)

    def list_tasks(self, goal_id: str) -> list[Task]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from tasks
                where goal_id = ?
                order by created_at asc, id asc
                """,
                (goal_id,),
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def list_tasks_for_run(self, run_id: str) -> list[Task]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from tasks
                where run_id = ?
                order by created_at asc, id asc
                """,
                (run_id,),
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def list_all_tasks(self) -> list[Task]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from tasks
                order by created_at asc, id asc
                """
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def list_blocked_tasks(self) -> list[Task]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from tasks
                where status = 'blocked'
                order by updated_at asc, id asc
                """
            ).fetchall()
        return [self._row_to_task(row) for row in rows]

    def set_task_status(self, task_id: str, status: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "update tasks set status = ?, updated_at = ? where id = ?",
                (status, utc_now(), task_id),
            )

    def mark_task_completed(
        self,
        task_id: str,
        *,
        evidence: dict[str, Any],
        artifacts: list[str],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                update tasks
                set status = 'completed', evidence = ?, artifacts = ?, updated_at = ?
                where id = ?
                """,
                (_json_dumps(evidence), _json_dumps(artifacts), utc_now(), task_id),
            )

    def mark_task_failed(
        self,
        task_id: str,
        *,
        evidence: dict[str, Any],
        artifacts: list[str],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                update tasks
                set status = 'failed', evidence = ?, artifacts = ?, updated_at = ?
                where id = ?
                """,
                (_json_dumps(evidence), _json_dumps(artifacts), utc_now(), task_id),
            )

    def mark_task_blocked(
        self,
        task_id: str,
        *,
        evidence: dict[str, Any],
        artifacts: list[str],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                update tasks
                set status = 'blocked', evidence = ?, artifacts = ?, updated_at = ?
                where id = ?
                """,
                (_json_dumps(evidence), _json_dumps(artifacts), utc_now(), task_id),
            )

    def record_event(
        self,
        *,
        run_id: str,
        goal_id: str | None,
        task_id: str | None,
        event_type: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                insert into events (run_id, goal_id, task_id, event_type, message, payload, created_at)
                values (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    goal_id,
                    task_id,
                    event_type,
                    message,
                    _json_dumps(payload or {}),
                    utc_now(),
                ),
            )

    def list_events_for_run(self, run_id: str) -> list[EventRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from events
                where run_id = ?
                order by id asc
                """,
                (run_id,),
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def record_learning(self, run_id: str, project_id: str, summary: str, source: str) -> str:
        learning_id = new_id("learning")
        with self._connect() as connection:
            connection.execute(
                """
                insert into learnings (id, run_id, project_id, summary, source, created_at)
                values (?, ?, ?, ?, ?, ?)
                """,
                (learning_id, run_id, project_id, summary, source, utc_now()),
            )
        return learning_id

    def list_recent_learnings(self, limit: int = 500) -> list[Learning]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from learnings
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_learning(row) for row in rows]

    def list_learnings_for_run(self, run_id: str) -> list[Learning]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from learnings
                where run_id = ?
                order by created_at desc, id desc
                """,
                (run_id,),
            ).fetchall()
        return [self._row_to_learning(row) for row in rows]

    def record_memory_entry(
        self,
        *,
        memory_id: str | None = None,
        project_id: str,
        scope: str,
        key: str,
        value: str,
        source_type: str,
        source_id: str,
        confidence: float,
        status: str,
        created_by_profile: str,
        artifact_path: str,
    ) -> MemoryEntry:
        entry_id = memory_id or new_id("memory")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into memory_entries (
                    id, project_id, scope, key, value, source_type, source_id,
                    confidence, status, created_by_profile, created_at,
                    updated_at, last_used_at, artifact_path, approved_by,
                    approved_at, archived_by, archived_at, archive_reason
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    project_id,
                    scope,
                    key,
                    value,
                    source_type,
                    source_id,
                    confidence,
                    status,
                    created_by_profile,
                    created_at,
                    created_at,
                    None,
                    artifact_path,
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            )
        return MemoryEntry(
            id=entry_id,
            project_id=project_id,
            scope=scope,
            key=key,
            value=value,
            source_type=source_type,
            source_id=source_id,
            confidence=confidence,
            status=status,
            created_by_profile=created_by_profile,
            artifact_path=artifact_path,
            approved_by=None,
            approved_at=None,
            archived_by=None,
            archived_at=None,
            archive_reason=None,
            created_at=created_at,
            updated_at=created_at,
            last_used_at=None,
        )

    def get_memory_entry(self, memory_id: str) -> MemoryEntry | None:
        with self._connect() as connection:
            row = connection.execute(
                "select * from memory_entries where id = ?",
                (memory_id,),
            ).fetchone()
        return self._row_to_memory_entry(row) if row else None

    def find_memory_entry(
        self,
        *,
        project_id: str,
        scope: str,
        key: str,
        source_type: str,
        source_id: str,
        include_archived: bool = False,
    ) -> MemoryEntry | None:
        archived_clause = "" if include_archived else "and status != 'archived'"
        with self._connect() as connection:
            row = connection.execute(
                f"""
                select * from memory_entries
                where project_id = ?
                  and scope = ?
                  and key = ?
                  and source_type = ?
                  and source_id = ?
                  {archived_clause}
                order by updated_at desc, id desc
                limit 1
                """,
                (project_id, scope, key, source_type, source_id),
            ).fetchone()
        return self._row_to_memory_entry(row) if row else None

    def list_memory_entries(
        self,
        *,
        project_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[MemoryEntry]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if project_id is not None:
            conditions.append("project_id = ?")
            parameters.append(project_id)
        if status is not None:
            conditions.append("status = ?")
            parameters.append(status)
        where_clause = f"where {' and '.join(conditions)}" if conditions else ""
        query = f"""
            select * from memory_entries
            {where_clause}
            order by updated_at desc, id desc
        """
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(query, parameters).fetchall()
            else:
                rows = connection.execute(
                    query + " limit ?",
                    parameters + [limit],
            ).fetchall()
        return [self._row_to_memory_entry(row) for row in rows]

    def list_memory_entries_for_source(
        self,
        *,
        source_type: str | None = None,
        source_id: str,
    ) -> list[MemoryEntry]:
        conditions = ["source_id = ?"]
        parameters: list[Any] = [source_id]
        if source_type is not None:
            conditions.append("source_type = ?")
            parameters.append(source_type)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                select * from memory_entries
                where {' and '.join(conditions)}
                order by updated_at desc, id desc
                """,
                parameters,
            ).fetchall()
        return [self._row_to_memory_entry(row) for row in rows]

    def update_memory_entry_status(
        self,
        memory_id: str,
        *,
        status: str,
        decided_by: str | None = None,
        reason: str | None = None,
    ) -> MemoryEntry:
        updated_at = utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "select * from memory_entries where id = ?",
                (memory_id,),
            ).fetchone()
            if row is None:
                raise KeyError(memory_id)
            if status == "active":
                if not row["artifact_path"] or not Path(row["artifact_path"]).exists():
                    raise ValueError(
                        f"memory entry {memory_id} evidence artifact is missing"
                    )
                approved_by = decided_by
                approved_at = updated_at
                archived_by = row["archived_by"]
                archived_at = row["archived_at"]
                archive_reason = row["archive_reason"]
            elif status == "archived":
                approved_by = row["approved_by"]
                approved_at = row["approved_at"]
                archived_by = decided_by
                archived_at = updated_at
                archive_reason = reason
            else:
                approved_by = row["approved_by"]
                approved_at = row["approved_at"]
                archived_by = row["archived_by"]
                archived_at = row["archived_at"]
                archive_reason = row["archive_reason"]
            connection.execute(
                """
                update memory_entries
                set status = ?,
                    updated_at = ?,
                    approved_by = ?,
                    approved_at = ?,
                    archived_by = ?,
                    archived_at = ?,
                    archive_reason = ?
                where id = ?
                """,
                (
                    status,
                    updated_at,
                    approved_by,
                    approved_at,
                    archived_by,
                    archived_at,
                    archive_reason,
                    memory_id,
                ),
            )
            updated = connection.execute(
                "select * from memory_entries where id = ?",
                (memory_id,),
            ).fetchone()
        return self._row_to_memory_entry(updated)

    def run_exists(self, run_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "select id from runs where id = ?",
                (run_id,),
            ).fetchone()
        return row is not None

    def record_skill(
        self,
        *,
        skill_id: str | None = None,
        project_id: str | None,
        name: str,
        description: str,
        path: str,
        status: str,
        created_by_profile: str,
        source_run_id: str | None,
        source_task_id: str | None,
        verification_status: str,
    ) -> SkillRecord:
        entry_id = skill_id or new_id("skill")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into skills (
                    id, project_id, name, description, path, status,
                    created_by_profile, source_run_id, source_task_id,
                    verification_status, approved_by, approved_at, archived_by,
                    archived_at, archive_reason, created_at, updated_at,
                    last_used_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry_id,
                    project_id,
                    name,
                    description,
                    path,
                    status,
                    created_by_profile,
                    source_run_id,
                    source_task_id,
                    verification_status,
                    None,
                    None,
                    None,
                    None,
                    None,
                    created_at,
                    created_at,
                    None,
                ),
            )
        return SkillRecord(
            id=entry_id,
            project_id=project_id,
            name=name,
            description=description,
            path=path,
            status=status,
            created_by_profile=created_by_profile,
            source_run_id=source_run_id,
            source_task_id=source_task_id,
            verification_status=verification_status,
            approved_by=None,
            approved_at=None,
            archived_by=None,
            archived_at=None,
            archive_reason=None,
            created_at=created_at,
            updated_at=created_at,
            last_used_at=None,
        )

    def record_skill_version(
        self,
        *,
        skill_id: str,
        version: int,
        content_hash: str,
        path: str,
        change_summary: str,
        verification_status: str,
    ) -> SkillVersion:
        version_id = new_id("skill_version")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into skill_versions (
                    id, skill_id, version, content_hash, path, change_summary,
                    verification_status, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    version_id,
                    skill_id,
                    version,
                    content_hash,
                    path,
                    change_summary,
                    verification_status,
                    created_at,
                ),
            )
        return SkillVersion(
            id=version_id,
            skill_id=skill_id,
            version=version,
            content_hash=content_hash,
            path=path,
            change_summary=change_summary,
            verification_status=verification_status,
            created_at=created_at,
        )

    def get_skill(self, skill_id: str) -> SkillRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "select * from skills where id = ?",
                (skill_id,),
            ).fetchone()
        return self._row_to_skill(row) if row else None

    def find_skill(
        self,
        *,
        project_id: str | None,
        name: str,
        source_run_id: str | None,
        source_task_id: str | None,
        include_archived: bool = False,
    ) -> SkillRecord | None:
        archived_clause = "" if include_archived else "and status != 'archived'"
        with self._connect() as connection:
            row = connection.execute(
                f"""
                select * from skills
                where project_id is ?
                  and name = ?
                  and source_run_id is ?
                  and source_task_id is ?
                  {archived_clause}
                order by updated_at desc, id desc
                limit 1
                """,
                (project_id, name, source_run_id, source_task_id),
            ).fetchone()
        return self._row_to_skill(row) if row else None

    def list_skills(
        self,
        *,
        project_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[SkillRecord]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if project_id is not None:
            conditions.append("project_id = ?")
            parameters.append(project_id)
        if status is not None:
            conditions.append("status = ?")
            parameters.append(status)
        where_clause = f"where {' and '.join(conditions)}" if conditions else ""
        query = f"""
            select * from skills
            {where_clause}
            order by updated_at desc, id desc
        """
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(query, parameters).fetchall()
            else:
                rows = connection.execute(
                    query + " limit ?",
                    parameters + [limit],
            ).fetchall()
        return [self._row_to_skill(row) for row in rows]

    def list_skills_for_source_run(self, run_id: str) -> list[SkillRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from skills
                where source_run_id = ?
                order by updated_at desc, id desc
                """,
                (run_id,),
            ).fetchall()
        return [self._row_to_skill(row) for row in rows]

    def list_skill_versions(self, skill_id: str) -> list[SkillVersion]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from skill_versions
                where skill_id = ?
                order by version desc, created_at desc
                """,
                (skill_id,),
            ).fetchall()
        return [self._row_to_skill_version(row) for row in rows]

    def update_skill_status(
        self,
        skill_id: str,
        *,
        status: str,
        decided_by: str | None = None,
        reason: str | None = None,
    ) -> SkillRecord:
        updated_at = utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "select * from skills where id = ?",
                (skill_id,),
            ).fetchone()
            if row is None:
                raise KeyError(skill_id)
            if status == "active":
                if not row["path"] or not Path(row["path"]).exists():
                    raise ValueError(f"skill {skill_id} SKILL.md is missing")
                approved_by = decided_by
                approved_at = updated_at
                archived_by = row["archived_by"]
                archived_at = row["archived_at"]
                archive_reason = row["archive_reason"]
                verification_status = "approved"
            elif status == "archived":
                approved_by = row["approved_by"]
                approved_at = row["approved_at"]
                archived_by = decided_by
                archived_at = updated_at
                archive_reason = reason
                verification_status = row["verification_status"]
            else:
                approved_by = row["approved_by"]
                approved_at = row["approved_at"]
                archived_by = row["archived_by"]
                archived_at = row["archived_at"]
                archive_reason = row["archive_reason"]
                verification_status = row["verification_status"]
            connection.execute(
                """
                update skills
                set status = ?,
                    updated_at = ?,
                    verification_status = ?,
                    approved_by = ?,
                    approved_at = ?,
                    archived_by = ?,
                    archived_at = ?,
                    archive_reason = ?
                where id = ?
                """,
                (
                    status,
                    updated_at,
                    verification_status,
                    approved_by,
                    approved_at,
                    archived_by,
                    archived_at,
                    archive_reason,
                    skill_id,
                ),
            )
            updated = connection.execute(
                "select * from skills where id = ?",
                (skill_id,),
            ).fetchone()
        return self._row_to_skill(updated)

    def record_eval_result(self, name: str, status: str, details: dict[str, Any]) -> str:
        eval_id = new_id("eval")
        with self._connect() as connection:
            connection.execute(
                """
                insert into eval_results (id, name, status, details, created_at)
                values (?, ?, ?, ?, ?)
                """,
                (eval_id, name, status, _json_dumps(details), utc_now()),
            )
        return eval_id

    def record_eval_candidate(
        self,
        *,
        source_type: str,
        source_id: str,
        suggested_eval: str,
        reason: str,
        candidate_path: str,
        status: str = "proposed",
    ) -> EvalCandidate:
        now = utc_now()
        with self._connect() as connection:
            existing = connection.execute(
                """
                select * from eval_candidates
                where source_type = ? and source_id = ?
                """,
                (source_type, source_id),
            ).fetchone()
            if existing is not None:
                connection.execute(
                    """
                    update eval_candidates
                    set suggested_eval = ?,
                        reason = ?,
                        candidate_path = ?,
                        status = ?,
                        updated_at = ?
                    where source_type = ? and source_id = ?
                    """,
                    (
                        suggested_eval,
                        reason,
                        candidate_path,
                        status,
                        now,
                        source_type,
                        source_id,
                    ),
                )
            else:
                connection.execute(
                    """
                    insert into eval_candidates (
                        id, source_type, source_id, suggested_eval, reason,
                        candidate_path, status, created_at, updated_at
                    )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        new_id("eval_candidate"),
                        source_type,
                        source_id,
                        suggested_eval,
                        reason,
                        candidate_path,
                        status,
                        now,
                        now,
                    ),
                )
            row = connection.execute(
                """
                select * from eval_candidates
                where source_type = ? and source_id = ?
                """,
                (source_type, source_id),
            ).fetchone()
            if row is None:
                raise KeyError(f"{source_type}:{source_id}")
        return self._row_to_eval_candidate(row)

    def list_recent_eval_candidates(self, limit: int = 5) -> list[EvalCandidate]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from eval_candidates
                order by updated_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_eval_candidate(row) for row in rows]

    def list_eval_candidates_for_source(
        self,
        *,
        source_type: str,
        source_id: str,
    ) -> list[EvalCandidate]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from eval_candidates
                where source_type = ? and source_id = ?
                order by updated_at desc, id desc
                """,
                (source_type, source_id),
            ).fetchall()
        return [self._row_to_eval_candidate(row) for row in rows]

    def list_successful_eval_runs(self, name: str) -> list[EvalRun]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from eval_results
                where name = ? and status = 'pass'
                order by created_at asc, id asc
                """,
                (name,),
            ).fetchall()
        return [self._row_to_eval_run(row) for row in rows]

    def record_playbook(
        self,
        *,
        slug: str,
        title: str,
        source_eval_name: str,
        successful_run_count: int,
        playbook_path: str,
        status: str = "active",
    ) -> Playbook:
        now = utc_now()
        with self._connect() as connection:
            existing = connection.execute(
                "select * from playbooks where slug = ?",
                (slug,),
            ).fetchone()
            if existing is not None:
                connection.execute(
                    """
                    update playbooks
                    set title = ?,
                        source_eval_name = ?,
                        successful_run_count = ?,
                        playbook_path = ?,
                        status = ?,
                        updated_at = ?
                    where slug = ?
                    """,
                    (
                        title,
                        source_eval_name,
                        successful_run_count,
                        playbook_path,
                        status,
                        now,
                        slug,
                    ),
                )
            else:
                connection.execute(
                    """
                    insert into playbooks (
                        id, slug, title, source_eval_name, successful_run_count,
                        playbook_path, status, created_at, updated_at
                    )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        new_id("playbook"),
                        slug,
                        title,
                        source_eval_name,
                        successful_run_count,
                        playbook_path,
                        status,
                        now,
                        now,
                    ),
                )
            row = connection.execute(
                "select * from playbooks where slug = ?",
                (slug,),
            ).fetchone()
            if row is None:
                raise KeyError(slug)
        return self._row_to_playbook(row)

    def list_recent_playbooks(self, limit: int = 5) -> list[Playbook]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from playbooks
                order by updated_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_playbook(row) for row in rows]

    def record_iteration_packet(
        self,
        *,
        focus: str,
        source_path: str,
        source_section: str,
        status: str,
        packet_path: str,
        verification_commands: list[str],
        selection_policy: str,
        selection_reason: str,
        selected_score: int,
        selected_complexity: int,
    ) -> IterationPacket:
        packet_id = new_id("iteration")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into iteration_packets (
                    id, focus, source_path, source_section, status,
                    packet_path, verification_commands, selection_policy,
                    selection_reason, selected_score, selected_complexity, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    packet_id,
                    focus,
                    source_path,
                    source_section,
                    status,
                    packet_path,
                    _json_dumps(verification_commands),
                    selection_policy,
                    selection_reason,
                    selected_score,
                    selected_complexity,
                    created_at,
                ),
            )
        return IterationPacket(
            id=packet_id,
            focus=focus,
            source_path=source_path,
            source_section=source_section,
            status=status,
            packet_path=packet_path,
            verification_commands=verification_commands,
            selection_policy=selection_policy,
            selection_reason=selection_reason,
            selected_score=selected_score,
            selected_complexity=selected_complexity,
            created_at=created_at,
        )

    def list_recent_iteration_packets(self, limit: int = 5) -> list[IterationPacket]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from iteration_packets
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_iteration_packet(row) for row in rows]

    def record_handoff_review(
        self,
        *,
        status: str,
        current_focus: str,
        blocked_tasks: list[dict[str, Any]],
        stale_handoffs: list[dict[str, Any]],
        reviewed_paths: list[str],
        report_path: str,
    ) -> HandoffReview:
        review_id = new_id("handoff_review")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into handoff_reviews (
                    id, status, current_focus, blocked_task_count,
                    stale_handoff_count, blocked_tasks, stale_handoffs,
                    reviewed_paths, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    status,
                    current_focus,
                    len(blocked_tasks),
                    len(stale_handoffs),
                    _json_dumps(blocked_tasks),
                    _json_dumps(stale_handoffs),
                    _json_dumps(reviewed_paths),
                    report_path,
                    created_at,
                ),
            )
        return HandoffReview(
            id=review_id,
            status=status,
            current_focus=current_focus,
            blocked_task_count=len(blocked_tasks),
            stale_handoff_count=len(stale_handoffs),
            blocked_tasks=blocked_tasks,
            stale_handoffs=stale_handoffs,
            reviewed_paths=reviewed_paths,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_handoff_reviews(self, limit: int = 5) -> list[HandoffReview]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from handoff_reviews
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_handoff_review(row) for row in rows]

    def record_eval_after_change_check(
        self,
        *,
        change_summary: str,
        changed_paths: list[str],
        eval_names: list[str],
        status: str,
        result_paths: list[str],
        run_ids: list[str],
        report_path: str,
        command: str,
    ) -> EvalAfterChangeCheck:
        check_id = new_id("eval_after_change")
        created_at = utc_now()
        completed_at = created_at
        with self._connect() as connection:
            connection.execute(
                """
                insert into eval_after_change_checks (
                    id, change_summary, changed_paths, eval_names, status,
                    result_paths, run_ids, report_path, command, created_at,
                    completed_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    check_id,
                    change_summary,
                    _json_dumps(changed_paths),
                    _json_dumps(eval_names),
                    status,
                    _json_dumps(result_paths),
                    _json_dumps(run_ids),
                    report_path,
                    command,
                    created_at,
                    completed_at,
                ),
            )
        return EvalAfterChangeCheck(
            id=check_id,
            change_summary=change_summary,
            changed_paths=changed_paths,
            eval_names=eval_names,
            status=status,
            result_paths=result_paths,
            run_ids=run_ids,
            report_path=report_path,
            command=command,
            created_at=created_at,
            completed_at=completed_at,
        )

    def list_recent_eval_after_change_checks(
        self,
        limit: int = 5,
    ) -> list[EvalAfterChangeCheck]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from eval_after_change_checks
                order by completed_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_eval_after_change_check(row) for row in rows]

    def record_learning_distillation(
        self,
        *,
        status: str,
        min_occurrences: int,
        stable_learnings: list[dict[str, Any]],
        source_learning_count: int,
        report_path: str,
    ) -> LearningDistillation:
        distillation_id = new_id("learning_distillation")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into learning_distillations (
                    id, status, min_occurrences, stable_learning_count,
                    stable_learnings, source_learning_count, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    distillation_id,
                    status,
                    min_occurrences,
                    len(stable_learnings),
                    _json_dumps(stable_learnings),
                    source_learning_count,
                    report_path,
                    created_at,
                ),
            )
        return LearningDistillation(
            id=distillation_id,
            status=status,
            min_occurrences=min_occurrences,
            stable_learning_count=len(stable_learnings),
            stable_learnings=stable_learnings,
            source_learning_count=source_learning_count,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_learning_distillations(
        self,
        limit: int = 5,
    ) -> list[LearningDistillation]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from learning_distillations
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_learning_distillation(row) for row in rows]

    def record_budget_trust_posture_report(
        self,
        *,
        status: str,
        task_count: int,
        risk_counts: dict[str, int],
        budget_state: str,
        budget_summary: dict[str, Any],
        trust_state: str,
        trust_summary: dict[str, Any],
        report_path: str,
    ) -> BudgetTrustPostureReport:
        report_id = new_id("budget_trust_posture")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into budget_trust_posture_reports (
                    id, status, task_count, risk_counts, budget_state,
                    budget_summary, trust_state, trust_summary, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    report_id,
                    status,
                    task_count,
                    _json_dumps(risk_counts),
                    budget_state,
                    _json_dumps(budget_summary),
                    trust_state,
                    _json_dumps(trust_summary),
                    report_path,
                    created_at,
                ),
            )
        return BudgetTrustPostureReport(
            id=report_id,
            status=status,
            task_count=task_count,
            risk_counts=risk_counts,
            budget_state=budget_state,
            budget_summary=budget_summary,
            trust_state=trust_state,
            trust_summary=trust_summary,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_budget_trust_posture_reports(
        self,
        limit: int = 5,
    ) -> list[BudgetTrustPostureReport]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from budget_trust_posture_reports
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_budget_trust_posture_report(row) for row in rows]

    def record_dispatch_posture_history_summary(
        self,
        *,
        status: str,
        snapshot_count: int,
        latest_task_count: int,
        task_count_delta: int,
        latest_risk_counts: dict[str, int],
        budget_states: list[str],
        trust_states: list[str],
        first_snapshot_at: str | None,
        latest_snapshot_at: str | None,
        report_path: str,
    ) -> DispatchPostureHistorySummary:
        summary_id = new_id("dispatch_posture_history")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into dispatch_posture_history_summaries (
                    id, status, snapshot_count, latest_task_count,
                    task_count_delta, latest_risk_counts, budget_states,
                    trust_states, first_snapshot_at, latest_snapshot_at,
                    report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary_id,
                    status,
                    snapshot_count,
                    latest_task_count,
                    task_count_delta,
                    _json_dumps(latest_risk_counts),
                    _json_dumps(budget_states),
                    _json_dumps(trust_states),
                    first_snapshot_at,
                    latest_snapshot_at,
                    report_path,
                    created_at,
                ),
            )
        return DispatchPostureHistorySummary(
            id=summary_id,
            status=status,
            snapshot_count=snapshot_count,
            latest_task_count=latest_task_count,
            task_count_delta=task_count_delta,
            latest_risk_counts=latest_risk_counts,
            budget_states=budget_states,
            trust_states=trust_states,
            first_snapshot_at=first_snapshot_at,
            latest_snapshot_at=latest_snapshot_at,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_dispatch_posture_history_summaries(
        self,
        limit: int = 5,
    ) -> list[DispatchPostureHistorySummary]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from dispatch_posture_history_summaries
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dispatch_posture_history_summary(row) for row in rows]

    def record_dispatch_posture_staleness_review(
        self,
        *,
        status: str,
        snapshot_count: int,
        stale_snapshot_count: int,
        latest_snapshot_age_seconds: int | None,
        stale_after_seconds: int,
        latest_task_count: int,
        latest_risk_counts: dict[str, int],
        latest_snapshot_at: str | None,
        oldest_snapshot_at: str | None,
        report_path: str,
    ) -> DispatchPostureStalenessReview:
        review_id = new_id("dispatch_posture_staleness")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into dispatch_posture_staleness_reviews (
                    id, status, snapshot_count, stale_snapshot_count,
                    latest_snapshot_age_seconds, stale_after_seconds,
                    latest_task_count, latest_risk_counts, latest_snapshot_at,
                    oldest_snapshot_at, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    status,
                    snapshot_count,
                    stale_snapshot_count,
                    latest_snapshot_age_seconds,
                    stale_after_seconds,
                    latest_task_count,
                    _json_dumps(latest_risk_counts),
                    latest_snapshot_at,
                    oldest_snapshot_at,
                    report_path,
                    created_at,
                ),
            )
        return DispatchPostureStalenessReview(
            id=review_id,
            status=status,
            snapshot_count=snapshot_count,
            stale_snapshot_count=stale_snapshot_count,
            latest_snapshot_age_seconds=latest_snapshot_age_seconds,
            stale_after_seconds=stale_after_seconds,
            latest_task_count=latest_task_count,
            latest_risk_counts=latest_risk_counts,
            latest_snapshot_at=latest_snapshot_at,
            oldest_snapshot_at=oldest_snapshot_at,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_dispatch_posture_staleness_reviews(
        self,
        limit: int = 5,
    ) -> list[DispatchPostureStalenessReview]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from dispatch_posture_staleness_reviews
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dispatch_posture_staleness_review(row) for row in rows]

    def record_dispatch_posture_refresh_recommendation(
        self,
        *,
        status: str,
        source_review_id: str | None,
        source_review_status: str,
        snapshot_count: int,
        stale_snapshot_count: int,
        latest_snapshot_age_seconds: int | None,
        stale_after_seconds: int,
        latest_snapshot_at: str | None,
        recommended_commands: list[str],
        reason: str,
        approval_boundary: str,
        deferred_capabilities: list[str],
        report_path: str,
    ) -> DispatchPostureRefreshRecommendation:
        recommendation_id = new_id("dispatch_posture_refresh")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into dispatch_posture_refresh_recommendations (
                    id, status, source_review_id, source_review_status,
                    snapshot_count, stale_snapshot_count,
                    latest_snapshot_age_seconds, stale_after_seconds,
                    latest_snapshot_at, recommended_commands, reason,
                    approval_boundary, deferred_capabilities, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    recommendation_id,
                    status,
                    source_review_id,
                    source_review_status,
                    snapshot_count,
                    stale_snapshot_count,
                    latest_snapshot_age_seconds,
                    stale_after_seconds,
                    latest_snapshot_at,
                    _json_dumps(recommended_commands),
                    reason,
                    approval_boundary,
                    _json_dumps(deferred_capabilities),
                    report_path,
                    created_at,
                ),
            )
        return DispatchPostureRefreshRecommendation(
            id=recommendation_id,
            status=status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            snapshot_count=snapshot_count,
            stale_snapshot_count=stale_snapshot_count,
            latest_snapshot_age_seconds=latest_snapshot_age_seconds,
            stale_after_seconds=stale_after_seconds,
            latest_snapshot_at=latest_snapshot_at,
            recommended_commands=recommended_commands,
            reason=reason,
            approval_boundary=approval_boundary,
            deferred_capabilities=deferred_capabilities,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_dispatch_posture_refresh_recommendations(
        self,
        limit: int = 5,
    ) -> list[DispatchPostureRefreshRecommendation]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from dispatch_posture_refresh_recommendations
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_dispatch_posture_refresh_recommendation(row) for row in rows]

    def record_capability_expansion_ledger(
        self,
        *,
        status: str,
        capability_count: int,
        ready_count: int,
        deferred_count: int,
        approval_boundary: str,
        capabilities: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityExpansionLedger:
        ledger_id = new_id("capability_expansion_ledger")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_expansion_ledgers (
                    id, status, capability_count, ready_count, deferred_count,
                    approval_boundary, capabilities, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger_id,
                    status,
                    capability_count,
                    ready_count,
                    deferred_count,
                    approval_boundary,
                    _json_dumps(capabilities),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityExpansionLedger(
            id=ledger_id,
            status=status,
            capability_count=capability_count,
            ready_count=ready_count,
            deferred_count=deferred_count,
            approval_boundary=approval_boundary,
            capabilities=capabilities,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_expansion_ledgers(
        self,
        limit: int = 5,
    ) -> list[CapabilityExpansionLedger]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_expansion_ledgers
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_expansion_ledger(row) for row in rows]

    def record_capability_readiness_review(
        self,
        *,
        status: str,
        source_ledger_id: str | None,
        source_ledger_status: str,
        capability_count: int,
        ready_count: int,
        not_ready_count: int,
        missing_evidence_count: int,
        approval_boundary: str,
        recommended_commands: list[str],
        reason: str,
        review_items: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityReadinessReview:
        review_id = new_id("capability_readiness_review")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_readiness_reviews (
                    id, status, source_ledger_id, source_ledger_status,
                    capability_count, ready_count, not_ready_count,
                    missing_evidence_count, approval_boundary,
                    recommended_commands, reason, review_items, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    status,
                    source_ledger_id,
                    source_ledger_status,
                    capability_count,
                    ready_count,
                    not_ready_count,
                    missing_evidence_count,
                    approval_boundary,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(review_items),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityReadinessReview(
            id=review_id,
            status=status,
            source_ledger_id=source_ledger_id,
            source_ledger_status=source_ledger_status,
            capability_count=capability_count,
            ready_count=ready_count,
            not_ready_count=not_ready_count,
            missing_evidence_count=missing_evidence_count,
            approval_boundary=approval_boundary,
            recommended_commands=recommended_commands,
            reason=reason,
            review_items=review_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_readiness_reviews(
        self,
        limit: int = 5,
    ) -> list[CapabilityReadinessReview]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_readiness_reviews
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_readiness_review(row) for row in rows]

    def record_capability_proof_gap_index(
        self,
        *,
        status: str,
        source_review_id: str | None,
        source_review_status: str,
        capability_count: int,
        gap_count: int,
        missing_evidence_count: int,
        blocked_capability_count: int,
        next_proof_count: int,
        approval_boundary: str,
        recommended_commands: list[str],
        reason: str,
        proof_gaps: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityProofGapIndex:
        index_id = new_id("capability_proof_gap_index")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_proof_gap_indexes (
                    id, status, source_review_id, source_review_status,
                    capability_count, gap_count, missing_evidence_count,
                    blocked_capability_count, next_proof_count,
                    approval_boundary, recommended_commands, reason,
                    proof_gaps, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    index_id,
                    status,
                    source_review_id,
                    source_review_status,
                    capability_count,
                    gap_count,
                    missing_evidence_count,
                    blocked_capability_count,
                    next_proof_count,
                    approval_boundary,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(proof_gaps),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityProofGapIndex(
            id=index_id,
            status=status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            capability_count=capability_count,
            gap_count=gap_count,
            missing_evidence_count=missing_evidence_count,
            blocked_capability_count=blocked_capability_count,
            next_proof_count=next_proof_count,
            approval_boundary=approval_boundary,
            recommended_commands=recommended_commands,
            reason=reason,
            proof_gaps=proof_gaps,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_proof_gap_indexes(
        self,
        limit: int = 5,
    ) -> list[CapabilityProofGapIndex]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_proof_gap_indexes
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_proof_gap_index(row) for row in rows]

    def record_capability_approval_boundary_matrix(
        self,
        *,
        status: str,
        source_index_id: str | None,
        source_index_status: str,
        capability_count: int,
        boundary_count: int,
        gap_count: int,
        blocked_capability_count: int,
        approval_required_count: int,
        recommended_commands: list[str],
        reason: str,
        boundary_rows: list[dict[str, Any]],
        matrix_entries: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityApprovalBoundaryMatrix:
        matrix_id = new_id("capability_approval_boundary_matrix")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_approval_boundary_matrices (
                    id, status, source_index_id, source_index_status,
                    capability_count, boundary_count, gap_count,
                    blocked_capability_count, approval_required_count,
                    recommended_commands, reason, boundary_rows,
                    matrix_entries, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    matrix_id,
                    status,
                    source_index_id,
                    source_index_status,
                    capability_count,
                    boundary_count,
                    gap_count,
                    blocked_capability_count,
                    approval_required_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(boundary_rows),
                    _json_dumps(matrix_entries),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityApprovalBoundaryMatrix(
            id=matrix_id,
            status=status,
            source_index_id=source_index_id,
            source_index_status=source_index_status,
            capability_count=capability_count,
            boundary_count=boundary_count,
            gap_count=gap_count,
            blocked_capability_count=blocked_capability_count,
            approval_required_count=approval_required_count,
            recommended_commands=recommended_commands,
            reason=reason,
            boundary_rows=boundary_rows,
            matrix_entries=matrix_entries,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_approval_boundary_matrices(
        self,
        limit: int = 5,
    ) -> list[CapabilityApprovalBoundaryMatrix]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_approval_boundary_matrices
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_approval_boundary_matrix(row) for row in rows
        ]

    def record_capability_evidence_collection_plan(
        self,
        *,
        status: str,
        source_matrix_id: str | None,
        source_matrix_status: str,
        capability_count: int,
        evidence_item_count: int,
        manual_collection_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        evidence_items: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityEvidenceCollectionPlan:
        plan_id = new_id("capability_evidence_collection_plan")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_evidence_collection_plans (
                    id, status, source_matrix_id, source_matrix_status,
                    capability_count, evidence_item_count, manual_collection_count,
                    approval_required_count, boundary_count, recommended_commands,
                    reason, evidence_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    status,
                    source_matrix_id,
                    source_matrix_status,
                    capability_count,
                    evidence_item_count,
                    manual_collection_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(evidence_items),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityEvidenceCollectionPlan(
            id=plan_id,
            status=status,
            source_matrix_id=source_matrix_id,
            source_matrix_status=source_matrix_status,
            capability_count=capability_count,
            evidence_item_count=evidence_item_count,
            manual_collection_count=manual_collection_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            evidence_items=evidence_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_evidence_collection_plans(
        self,
        limit: int = 5,
    ) -> list[CapabilityEvidenceCollectionPlan]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_evidence_collection_plans
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_evidence_collection_plan(row) for row in rows]

    def record_capability_promotion_gate_checklist(
        self,
        *,
        status: str,
        source_plan_id: str | None,
        source_plan_status: str,
        capability_count: int,
        gate_count: int,
        blocked_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityPromotionGateChecklist:
        checklist_id = new_id("capability_promotion_gate_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_promotion_gate_checklists (
                    id, status, source_plan_id, source_plan_status,
                    capability_count, gate_count, blocked_promotion_count,
                    missing_evidence_count, approval_required_count, boundary_count,
                    recommended_commands, reason, checklist_items, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_plan_id,
                    source_plan_status,
                    capability_count,
                    gate_count,
                    blocked_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityPromotionGateChecklist(
            id=checklist_id,
            status=status,
            source_plan_id=source_plan_id,
            source_plan_status=source_plan_status,
            capability_count=capability_count,
            gate_count=gate_count,
            blocked_promotion_count=blocked_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_promotion_gate_checklists(
        self,
        limit: int = 5,
    ) -> list[CapabilityPromotionGateChecklist]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_promotion_gate_checklists
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_promotion_gate_checklist(row) for row in rows]

    def record_capability_promotion_decision_ledger(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        decision_count: int,
        deferred_promotion_count: int,
        operator_decision_required_count: int,
        blocked_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        decision_items: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityPromotionDecisionLedger:
        ledger_id = new_id("capability_promotion_decision_ledger")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_promotion_decision_ledgers (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, decision_count, deferred_promotion_count,
                    operator_decision_required_count, blocked_promotion_count,
                    missing_evidence_count, approval_required_count, boundary_count,
                    recommended_commands, reason, decision_items, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    decision_count,
                    deferred_promotion_count,
                    operator_decision_required_count,
                    blocked_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(decision_items),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityPromotionDecisionLedger(
            id=ledger_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            decision_count=decision_count,
            deferred_promotion_count=deferred_promotion_count,
            operator_decision_required_count=operator_decision_required_count,
            blocked_promotion_count=blocked_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            decision_items=decision_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_promotion_decision_ledgers(
        self,
        limit: int = 5,
    ) -> list[CapabilityPromotionDecisionLedger]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_promotion_decision_ledgers
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_promotion_decision_ledger(row) for row in rows
        ]

    def record_capability_trust_promotion_audit(
        self,
        *,
        status: str,
        source_ledger_id: str | None,
        source_ledger_status: str,
        capability_count: int,
        audit_count: int,
        blocked_trust_promotion_count: int,
        operator_review_required_count: int,
        deferred_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        audit_items: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityTrustPromotionAudit:
        audit_id = new_id("capability_trust_promotion_audit")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_trust_promotion_audits (
                    id, status, source_ledger_id, source_ledger_status,
                    capability_count, audit_count, blocked_trust_promotion_count,
                    operator_review_required_count, deferred_promotion_count,
                    missing_evidence_count, approval_required_count, boundary_count,
                    recommended_commands, reason, audit_items, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    status,
                    source_ledger_id,
                    source_ledger_status,
                    capability_count,
                    audit_count,
                    blocked_trust_promotion_count,
                    operator_review_required_count,
                    deferred_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(audit_items),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityTrustPromotionAudit(
            id=audit_id,
            status=status,
            source_ledger_id=source_ledger_id,
            source_ledger_status=source_ledger_status,
            capability_count=capability_count,
            audit_count=audit_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            operator_review_required_count=operator_review_required_count,
            deferred_promotion_count=deferred_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            audit_items=audit_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_trust_promotion_audits(
        self,
        limit: int = 5,
    ) -> list[CapabilityTrustPromotionAudit]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_trust_promotion_audits
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_trust_promotion_audit(row) for row in rows]

    def record_capability_automatic_retry_audit(
        self,
        *,
        status: str,
        source_audit_id: str | None,
        source_audit_status: str,
        capability_count: int,
        audit_count: int,
        blocked_retry_count: int,
        operator_review_required_count: int,
        blocked_trust_promotion_count: int,
        deferred_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        audit_items: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityAutomaticRetryAudit:
        audit_id = new_id("capability_automatic_retry_audit")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_automatic_retry_audits (
                    id, status, source_audit_id, source_audit_status,
                    capability_count, audit_count, blocked_retry_count,
                    operator_review_required_count, blocked_trust_promotion_count,
                    deferred_promotion_count, missing_evidence_count,
                    approval_required_count, boundary_count, recommended_commands,
                    reason, audit_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    status,
                    source_audit_id,
                    source_audit_status,
                    capability_count,
                    audit_count,
                    blocked_retry_count,
                    operator_review_required_count,
                    blocked_trust_promotion_count,
                    deferred_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(audit_items),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityAutomaticRetryAudit(
            id=audit_id,
            status=status,
            source_audit_id=source_audit_id,
            source_audit_status=source_audit_status,
            capability_count=capability_count,
            audit_count=audit_count,
            blocked_retry_count=blocked_retry_count,
            operator_review_required_count=operator_review_required_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            deferred_promotion_count=deferred_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            audit_items=audit_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_automatic_retry_audits(
        self,
        limit: int = 5,
    ) -> list[CapabilityAutomaticRetryAudit]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_automatic_retry_audits
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_automatic_retry_audit(row) for row in rows]

    def record_capability_real_cost_tracking_audit(
        self,
        *,
        status: str,
        source_audit_id: str | None,
        source_audit_status: str,
        capability_count: int,
        audit_count: int,
        blocked_cost_tracking_count: int,
        operator_review_required_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        deferred_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        audit_items: list[dict[str, Any]],
        report_path: str,
    ) -> CapabilityRealCostTrackingAudit:
        audit_id = new_id("capability_real_cost_tracking_audit")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_real_cost_tracking_audits (
                    id, status, source_audit_id, source_audit_status,
                    capability_count, audit_count, blocked_cost_tracking_count,
                    operator_review_required_count, blocked_retry_count,
                    blocked_trust_promotion_count, deferred_promotion_count,
                    missing_evidence_count, approval_required_count, boundary_count,
                    recommended_commands, reason, audit_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    status,
                    source_audit_id,
                    source_audit_status,
                    capability_count,
                    audit_count,
                    blocked_cost_tracking_count,
                    operator_review_required_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    deferred_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(audit_items),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityRealCostTrackingAudit(
            id=audit_id,
            status=status,
            source_audit_id=source_audit_id,
            source_audit_status=source_audit_status,
            capability_count=capability_count,
            audit_count=audit_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            operator_review_required_count=operator_review_required_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            deferred_promotion_count=deferred_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            audit_items=audit_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_real_cost_tracking_audits(
        self,
        limit: int = 5,
    ) -> list[CapabilityRealCostTrackingAudit]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_real_cost_tracking_audits
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_real_cost_tracking_audit(row) for row in rows]

    def record_hosted_dashboard_proof_checklist(
        self,
        *,
        status: str,
        source_audit_id: str | None,
        source_audit_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_dashboard_proof_count: int,
        operator_review_required_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
        source_kind: str = "real_cost_tracking_audit",
        source_checklist_id: str | None = None,
        source_checklist_status: str = "none",
    ) -> HostedDashboardProofChecklist:
        checklist_id = new_id("hosted_dashboard_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into hosted_dashboard_proof_checklists (
                    id, status, source_audit_id, source_audit_status,
                    source_kind, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_dashboard_proof_count, operator_review_required_count,
                    blocked_cost_tracking_count, blocked_retry_count,
                    blocked_trust_promotion_count, missing_evidence_count,
                    approval_required_count, boundary_count, recommended_commands,
                    reason, checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_audit_id,
                    source_audit_status,
                    source_kind,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_dashboard_proof_count,
                    operator_review_required_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return HostedDashboardProofChecklist(
            id=checklist_id,
            status=status,
            source_audit_id=source_audit_id,
            source_audit_status=source_audit_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
            source_kind=source_kind,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
        )

    def list_recent_hosted_dashboard_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[HostedDashboardProofChecklist]:
        with self._connect() as connection:
            query = """
                select * from hosted_dashboard_proof_checklists
                order by created_at desc, id desc
                """
            params: tuple[int, ...] = ()
            if limit is not None:
                query += " limit ?"
                params = (limit,)
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_hosted_dashboard_proof_checklist(row) for row in rows]

    def get_hosted_dashboard_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> HostedDashboardProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from hosted_dashboard_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_hosted_dashboard_proof_checklist(row)

    def record_remote_worker_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_worker_proof_count: int,
        operator_review_required_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> RemoteWorkerProofChecklist:
        checklist_id = new_id("remote_worker_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into remote_worker_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_worker_proof_count, operator_review_required_count,
                    blocked_dashboard_proof_count, blocked_cost_tracking_count,
                    blocked_retry_count, blocked_trust_promotion_count,
                    missing_evidence_count, approval_required_count,
                    boundary_count, recommended_commands, reason,
                    checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_worker_proof_count,
                    operator_review_required_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return RemoteWorkerProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_remote_worker_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[RemoteWorkerProofChecklist]:
        with self._connect() as connection:
            query = """
                select * from remote_worker_proof_checklists
                order by created_at desc, id desc
                """
            params: tuple[int, ...] = ()
            if limit is not None:
                query += " limit ?"
                params = (limit,)
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_remote_worker_proof_checklist(row) for row in rows]

    def get_remote_worker_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> RemoteWorkerProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from remote_worker_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_remote_worker_proof_checklist(row)

    def record_autonomous_scheduling_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_scheduling_proof_count: int,
        operator_review_required_count: int,
        blocked_worker_proof_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> AutonomousSchedulingProofChecklist:
        checklist_id = new_id("autonomous_scheduling_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into autonomous_scheduling_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_scheduling_proof_count, operator_review_required_count,
                    blocked_worker_proof_count, blocked_dashboard_proof_count,
                    blocked_cost_tracking_count, blocked_retry_count,
                    blocked_trust_promotion_count, missing_evidence_count,
                    approval_required_count, boundary_count, recommended_commands,
                    reason, checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_scheduling_proof_count,
                    operator_review_required_count,
                    blocked_worker_proof_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return AutonomousSchedulingProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_scheduling_proof_count=blocked_scheduling_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_autonomous_scheduling_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[AutonomousSchedulingProofChecklist]:
        with self._connect() as connection:
            query = """
                select * from autonomous_scheduling_proof_checklists
                order by created_at desc, id desc
                """
            params: tuple[int, ...] = ()
            if limit is not None:
                query += " limit ?"
                params = (limit,)
            rows = connection.execute(query, params).fetchall()
        return [
            self._row_to_autonomous_scheduling_proof_checklist(row) for row in rows
        ]

    def get_autonomous_scheduling_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> AutonomousSchedulingProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from autonomous_scheduling_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_autonomous_scheduling_proof_checklist(row)

    def record_browser_desktop_adapter_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_adapter_proof_count: int,
        operator_review_required_count: int,
        blocked_scheduling_proof_count: int,
        blocked_worker_proof_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> BrowserDesktopAdapterProofChecklist:
        checklist_id = new_id("browser_desktop_adapter_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into browser_desktop_adapter_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_adapter_proof_count, operator_review_required_count,
                    blocked_scheduling_proof_count, blocked_worker_proof_count,
                    blocked_dashboard_proof_count, blocked_cost_tracking_count,
                    blocked_retry_count, blocked_trust_promotion_count,
                    missing_evidence_count, approval_required_count,
                    boundary_count, recommended_commands, reason,
                    checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_adapter_proof_count,
                    operator_review_required_count,
                    blocked_scheduling_proof_count,
                    blocked_worker_proof_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return BrowserDesktopAdapterProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_adapter_proof_count=blocked_adapter_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_scheduling_proof_count=blocked_scheduling_proof_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_browser_desktop_adapter_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[BrowserDesktopAdapterProofChecklist]:
        with self._connect() as connection:
            query = """
                select * from browser_desktop_adapter_proof_checklists
                order by created_at desc, id desc
                """
            params: tuple[int, ...] = ()
            if limit is not None:
                query += " limit ?"
                params = (limit,)
            rows = connection.execute(query, params).fetchall()
        return [
            self._row_to_browser_desktop_adapter_proof_checklist(row)
            for row in rows
        ]

    def get_browser_desktop_adapter_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> BrowserDesktopAdapterProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from browser_desktop_adapter_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_browser_desktop_adapter_proof_checklist(row)

    def record_ci_deploy_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_ci_deploy_proof_count: int,
        operator_review_required_count: int,
        blocked_adapter_proof_count: int,
        blocked_scheduling_proof_count: int,
        blocked_worker_proof_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> CiDeployProofChecklist:
        checklist_id = new_id("ci_deploy_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into ci_deploy_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_ci_deploy_proof_count, operator_review_required_count,
                    blocked_adapter_proof_count, blocked_scheduling_proof_count,
                    blocked_worker_proof_count, blocked_dashboard_proof_count,
                    blocked_cost_tracking_count, blocked_retry_count,
                    blocked_trust_promotion_count, missing_evidence_count,
                    approval_required_count, boundary_count, recommended_commands,
                    reason, checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_ci_deploy_proof_count,
                    operator_review_required_count,
                    blocked_adapter_proof_count,
                    blocked_scheduling_proof_count,
                    blocked_worker_proof_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return CiDeployProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_ci_deploy_proof_count=blocked_ci_deploy_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_adapter_proof_count=blocked_adapter_proof_count,
            blocked_scheduling_proof_count=blocked_scheduling_proof_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_ci_deploy_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[CiDeployProofChecklist]:
        with self._connect() as connection:
            query = """
                select * from ci_deploy_proof_checklists
                order by created_at desc, id desc
                """
            params: tuple[int, ...] = ()
            if limit is not None:
                query += " limit ?"
                params = (limit,)
            rows = connection.execute(query, params).fetchall()
        return [
            self._row_to_ci_deploy_proof_checklist(row)
            for row in rows
        ]

    def get_ci_deploy_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> CiDeployProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from ci_deploy_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_ci_deploy_proof_checklist(row)

    def record_budget_enforcement_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_budget_enforcement_proof_count: int,
        operator_review_required_count: int,
        blocked_ci_deploy_proof_count: int,
        blocked_adapter_proof_count: int,
        blocked_scheduling_proof_count: int,
        blocked_worker_proof_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> BudgetEnforcementProofChecklist:
        checklist_id = new_id("budget_enforcement_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into budget_enforcement_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_budget_enforcement_proof_count,
                    operator_review_required_count, blocked_ci_deploy_proof_count,
                    blocked_adapter_proof_count, blocked_scheduling_proof_count,
                    blocked_worker_proof_count, blocked_dashboard_proof_count,
                    blocked_cost_tracking_count, blocked_retry_count,
                    blocked_trust_promotion_count, missing_evidence_count,
                    approval_required_count, boundary_count, recommended_commands,
                    reason, checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_budget_enforcement_proof_count,
                    operator_review_required_count,
                    blocked_ci_deploy_proof_count,
                    blocked_adapter_proof_count,
                    blocked_scheduling_proof_count,
                    blocked_worker_proof_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return BudgetEnforcementProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_budget_enforcement_proof_count=blocked_budget_enforcement_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_ci_deploy_proof_count=blocked_ci_deploy_proof_count,
            blocked_adapter_proof_count=blocked_adapter_proof_count,
            blocked_scheduling_proof_count=blocked_scheduling_proof_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_budget_enforcement_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[BudgetEnforcementProofChecklist]:
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    select * from budget_enforcement_proof_checklists
                    order by created_at desc, id desc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from budget_enforcement_proof_checklists
                    order by created_at desc, id desc
                    limit ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            self._row_to_budget_enforcement_proof_checklist(row)
            for row in rows
        ]

    def get_budget_enforcement_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> BudgetEnforcementProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from budget_enforcement_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_budget_enforcement_proof_checklist(row)

    def record_trust_promotion_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_trust_promotion_proof_count: int,
        operator_review_required_count: int,
        blocked_budget_enforcement_proof_count: int,
        blocked_ci_deploy_proof_count: int,
        blocked_adapter_proof_count: int,
        blocked_scheduling_proof_count: int,
        blocked_worker_proof_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> TrustPromotionProofChecklist:
        checklist_id = new_id("trust_promotion_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into trust_promotion_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_trust_promotion_proof_count,
                    operator_review_required_count,
                    blocked_budget_enforcement_proof_count,
                    blocked_ci_deploy_proof_count, blocked_adapter_proof_count,
                    blocked_scheduling_proof_count, blocked_worker_proof_count,
                    blocked_dashboard_proof_count, blocked_cost_tracking_count,
                    blocked_retry_count, blocked_trust_promotion_count,
                    missing_evidence_count, approval_required_count,
                    boundary_count, recommended_commands, reason,
                    checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_trust_promotion_proof_count,
                    operator_review_required_count,
                    blocked_budget_enforcement_proof_count,
                    blocked_ci_deploy_proof_count,
                    blocked_adapter_proof_count,
                    blocked_scheduling_proof_count,
                    blocked_worker_proof_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return TrustPromotionProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_trust_promotion_proof_count=blocked_trust_promotion_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_budget_enforcement_proof_count=blocked_budget_enforcement_proof_count,
            blocked_ci_deploy_proof_count=blocked_ci_deploy_proof_count,
            blocked_adapter_proof_count=blocked_adapter_proof_count,
            blocked_scheduling_proof_count=blocked_scheduling_proof_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_trust_promotion_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[TrustPromotionProofChecklist]:
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    select * from trust_promotion_proof_checklists
                    order by created_at desc, id desc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from trust_promotion_proof_checklists
                    order by created_at desc, id desc
                    limit ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            self._row_to_trust_promotion_proof_checklist(row)
            for row in rows
        ]

    def record_automatic_retry_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_automatic_retry_proof_count: int,
        operator_review_required_count: int,
        blocked_trust_promotion_proof_count: int,
        blocked_budget_enforcement_proof_count: int,
        blocked_ci_deploy_proof_count: int,
        blocked_adapter_proof_count: int,
        blocked_scheduling_proof_count: int,
        blocked_worker_proof_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> AutomaticRetryProofChecklist:
        checklist_id = new_id("automatic_retry_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into automatic_retry_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_automatic_retry_proof_count,
                    operator_review_required_count,
                    blocked_trust_promotion_proof_count,
                    blocked_budget_enforcement_proof_count,
                    blocked_ci_deploy_proof_count, blocked_adapter_proof_count,
                    blocked_scheduling_proof_count, blocked_worker_proof_count,
                    blocked_dashboard_proof_count, blocked_cost_tracking_count,
                    blocked_retry_count, blocked_trust_promotion_count,
                    missing_evidence_count, approval_required_count,
                    boundary_count, recommended_commands, reason,
                    checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_automatic_retry_proof_count,
                    operator_review_required_count,
                    blocked_trust_promotion_proof_count,
                    blocked_budget_enforcement_proof_count,
                    blocked_ci_deploy_proof_count,
                    blocked_adapter_proof_count,
                    blocked_scheduling_proof_count,
                    blocked_worker_proof_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return AutomaticRetryProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_automatic_retry_proof_count=blocked_automatic_retry_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_trust_promotion_proof_count=blocked_trust_promotion_proof_count,
            blocked_budget_enforcement_proof_count=blocked_budget_enforcement_proof_count,
            blocked_ci_deploy_proof_count=blocked_ci_deploy_proof_count,
            blocked_adapter_proof_count=blocked_adapter_proof_count,
            blocked_scheduling_proof_count=blocked_scheduling_proof_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_automatic_retry_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[AutomaticRetryProofChecklist]:
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    select * from automatic_retry_proof_checklists
                    order by created_at desc, id desc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from automatic_retry_proof_checklists
                    order by created_at desc, id desc
                    limit ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            self._row_to_automatic_retry_proof_checklist(row)
            for row in rows
        ]

    def get_trust_promotion_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> TrustPromotionProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from trust_promotion_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_trust_promotion_proof_checklist(row)

    def get_automatic_retry_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> AutomaticRetryProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from automatic_retry_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_automatic_retry_proof_checklist(row)

    def record_real_cost_tracking_proof_checklist(
        self,
        *,
        status: str,
        source_checklist_id: str | None,
        source_checklist_status: str,
        capability_count: int,
        checklist_count: int,
        blocked_real_cost_tracking_proof_count: int,
        operator_review_required_count: int,
        blocked_automatic_retry_proof_count: int,
        blocked_trust_promotion_proof_count: int,
        blocked_budget_enforcement_proof_count: int,
        blocked_ci_deploy_proof_count: int,
        blocked_adapter_proof_count: int,
        blocked_scheduling_proof_count: int,
        blocked_worker_proof_count: int,
        blocked_dashboard_proof_count: int,
        blocked_cost_tracking_count: int,
        blocked_retry_count: int,
        blocked_trust_promotion_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        boundary_count: int,
        recommended_commands: list[str],
        reason: str,
        checklist_items: list[dict[str, Any]],
        report_path: str,
    ) -> RealCostTrackingProofChecklist:
        checklist_id = new_id("real_cost_tracking_proof_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into real_cost_tracking_proof_checklists (
                    id, status, source_checklist_id, source_checklist_status,
                    capability_count, checklist_count,
                    blocked_real_cost_tracking_proof_count,
                    operator_review_required_count,
                    blocked_automatic_retry_proof_count,
                    blocked_trust_promotion_proof_count,
                    blocked_budget_enforcement_proof_count,
                    blocked_ci_deploy_proof_count, blocked_adapter_proof_count,
                    blocked_scheduling_proof_count, blocked_worker_proof_count,
                    blocked_dashboard_proof_count, blocked_cost_tracking_count,
                    blocked_retry_count, blocked_trust_promotion_count,
                    missing_evidence_count, approval_required_count,
                    boundary_count, recommended_commands, reason,
                    checklist_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    capability_count,
                    checklist_count,
                    blocked_real_cost_tracking_proof_count,
                    operator_review_required_count,
                    blocked_automatic_retry_proof_count,
                    blocked_trust_promotion_proof_count,
                    blocked_budget_enforcement_proof_count,
                    blocked_ci_deploy_proof_count,
                    blocked_adapter_proof_count,
                    blocked_scheduling_proof_count,
                    blocked_worker_proof_count,
                    blocked_dashboard_proof_count,
                    blocked_cost_tracking_count,
                    blocked_retry_count,
                    blocked_trust_promotion_count,
                    missing_evidence_count,
                    approval_required_count,
                    boundary_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(checklist_items),
                    report_path,
                    created_at,
                ),
            )
        return RealCostTrackingProofChecklist(
            id=checklist_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            capability_count=capability_count,
            checklist_count=checklist_count,
            blocked_real_cost_tracking_proof_count=blocked_real_cost_tracking_proof_count,
            operator_review_required_count=operator_review_required_count,
            blocked_automatic_retry_proof_count=blocked_automatic_retry_proof_count,
            blocked_trust_promotion_proof_count=blocked_trust_promotion_proof_count,
            blocked_budget_enforcement_proof_count=blocked_budget_enforcement_proof_count,
            blocked_ci_deploy_proof_count=blocked_ci_deploy_proof_count,
            blocked_adapter_proof_count=blocked_adapter_proof_count,
            blocked_scheduling_proof_count=blocked_scheduling_proof_count,
            blocked_worker_proof_count=blocked_worker_proof_count,
            blocked_dashboard_proof_count=blocked_dashboard_proof_count,
            blocked_cost_tracking_count=blocked_cost_tracking_count,
            blocked_retry_count=blocked_retry_count,
            blocked_trust_promotion_count=blocked_trust_promotion_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            boundary_count=boundary_count,
            recommended_commands=recommended_commands,
            reason=reason,
            checklist_items=checklist_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_real_cost_tracking_proof_checklists(
        self,
        limit: int | None = 5,
    ) -> list[RealCostTrackingProofChecklist]:
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    select * from real_cost_tracking_proof_checklists
                    order by created_at desc, id desc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from real_cost_tracking_proof_checklists
                    order by created_at desc, id desc
                    limit ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            self._row_to_real_cost_tracking_proof_checklist(row)
            for row in rows
        ]

    def record_goal_completion_audit(
        self,
        *,
        status: str,
        requirement_count: int,
        satisfied_requirement_count: int,
        blocked_requirement_count: int,
        missing_evidence_count: int,
        approval_required_count: int,
        external_decision_count: int,
        recommended_commands: list[str],
        reason: str,
        audit_items: list[dict[str, Any]],
        external_decisions: list[str],
        report_path: str,
    ) -> GoalCompletionAudit:
        audit_id = new_id("goal_completion_audit")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into goal_completion_audits (
                    id, status, requirement_count, satisfied_requirement_count,
                    blocked_requirement_count, missing_evidence_count,
                    approval_required_count, external_decision_count,
                    recommended_commands, reason, audit_items,
                    external_decisions, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    status,
                    requirement_count,
                    satisfied_requirement_count,
                    blocked_requirement_count,
                    missing_evidence_count,
                    approval_required_count,
                    external_decision_count,
                    _json_dumps(recommended_commands),
                    reason,
                    _json_dumps(audit_items),
                    _json_dumps(external_decisions),
                    report_path,
                    created_at,
                ),
            )
        return GoalCompletionAudit(
            id=audit_id,
            status=status,
            requirement_count=requirement_count,
            satisfied_requirement_count=satisfied_requirement_count,
            blocked_requirement_count=blocked_requirement_count,
            missing_evidence_count=missing_evidence_count,
            approval_required_count=approval_required_count,
            external_decision_count=external_decision_count,
            recommended_commands=recommended_commands,
            reason=reason,
            audit_items=audit_items,
            external_decisions=external_decisions,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_goal_completion_audits(
        self,
        limit: int = 5,
    ) -> list[GoalCompletionAudit]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from goal_completion_audits
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_goal_completion_audit(row) for row in rows]

    def record_expansion_decision_brief(
        self,
        *,
        status: str,
        source_audit_id: str,
        source_audit_status: str,
        requirement_count: int,
        blocked_requirement_count: int,
        external_decision_count: int,
        approval_required_count: int,
        decision_item_count: int,
        recommended_next_step: str,
        decision_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionDecisionBrief:
        brief_id = new_id("expansion_decision_brief")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_decision_briefs (
                    id, status, source_audit_id, source_audit_status,
                    requirement_count, blocked_requirement_count,
                    external_decision_count, approval_required_count,
                    decision_item_count, recommended_next_step,
                    decision_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    brief_id,
                    status,
                    source_audit_id,
                    source_audit_status,
                    requirement_count,
                    blocked_requirement_count,
                    external_decision_count,
                    approval_required_count,
                    decision_item_count,
                    recommended_next_step,
                    _json_dumps(decision_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionDecisionBrief(
            id=brief_id,
            status=status,
            source_audit_id=source_audit_id,
            source_audit_status=source_audit_status,
            requirement_count=requirement_count,
            blocked_requirement_count=blocked_requirement_count,
            external_decision_count=external_decision_count,
            approval_required_count=approval_required_count,
            decision_item_count=decision_item_count,
            recommended_next_step=recommended_next_step,
            decision_items=decision_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_decision_briefs(
        self,
        limit: int = 5,
    ) -> list[ExpansionDecisionBrief]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_decision_briefs
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_expansion_decision_brief(row) for row in rows]

    def record_expansion_decision_evidence_index(
        self,
        *,
        status: str,
        source_brief_id: str,
        source_brief_status: str,
        source_audit_id: str,
        decision_item_count: int,
        evidence_item_count: int,
        external_decision_count: int,
        capability_decision_count: int,
        missing_evidence_link_count: int,
        recommended_next_step: str,
        evidence_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionDecisionEvidenceIndex:
        index_id = new_id("expansion_decision_evidence_index")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_decision_evidence_indexes (
                    id, status, source_brief_id, source_brief_status,
                    source_audit_id, decision_item_count, evidence_item_count,
                    external_decision_count, capability_decision_count,
                    missing_evidence_link_count, recommended_next_step,
                    evidence_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    index_id,
                    status,
                    source_brief_id,
                    source_brief_status,
                    source_audit_id,
                    decision_item_count,
                    evidence_item_count,
                    external_decision_count,
                    capability_decision_count,
                    missing_evidence_link_count,
                    recommended_next_step,
                    _json_dumps(evidence_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionDecisionEvidenceIndex(
            id=index_id,
            status=status,
            source_brief_id=source_brief_id,
            source_brief_status=source_brief_status,
            source_audit_id=source_audit_id,
            decision_item_count=decision_item_count,
            evidence_item_count=evidence_item_count,
            external_decision_count=external_decision_count,
            capability_decision_count=capability_decision_count,
            missing_evidence_link_count=missing_evidence_link_count,
            recommended_next_step=recommended_next_step,
            evidence_items=evidence_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_decision_evidence_indexes(
        self,
        limit: int = 5,
    ) -> list[ExpansionDecisionEvidenceIndex]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_decision_evidence_indexes
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_expansion_decision_evidence_index(row) for row in rows]

    def record_expansion_operator_review_checklist(
        self,
        *,
        status: str,
        source_index_id: str,
        source_index_status: str,
        source_brief_id: str,
        source_audit_id: str,
        review_item_count: int,
        decision_required_count: int,
        external_review_count: int,
        capability_review_count: int,
        missing_evidence_link_count: int,
        allowed_actions: list[str],
        recommended_next_step: str,
        review_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorReviewChecklist:
        checklist_id = new_id("expansion_operator_review_checklist")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_review_checklists (
                    id, status, source_index_id, source_index_status,
                    source_brief_id, source_audit_id, review_item_count,
                    decision_required_count, external_review_count,
                    capability_review_count, missing_evidence_link_count,
                    allowed_actions, recommended_next_step, review_items,
                    report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_index_id,
                    source_index_status,
                    source_brief_id,
                    source_audit_id,
                    review_item_count,
                    decision_required_count,
                    external_review_count,
                    capability_review_count,
                    missing_evidence_link_count,
                    _json_dumps(allowed_actions),
                    recommended_next_step,
                    _json_dumps(review_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorReviewChecklist(
            id=checklist_id,
            status=status,
            source_index_id=source_index_id,
            source_index_status=source_index_status,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            review_item_count=review_item_count,
            decision_required_count=decision_required_count,
            external_review_count=external_review_count,
            capability_review_count=capability_review_count,
            missing_evidence_link_count=missing_evidence_link_count,
            allowed_actions=allowed_actions,
            recommended_next_step=recommended_next_step,
            review_items=review_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_review_checklists(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorReviewChecklist]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_review_checklists
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_expansion_operator_review_checklist(row) for row in rows]

    def record_expansion_operator_decision_ledger(
        self,
        *,
        status: str,
        source_checklist_id: str,
        source_checklist_status: str,
        source_index_id: str,
        source_brief_id: str,
        source_audit_id: str,
        decision_item_count: int,
        pending_decision_count: int,
        approved_decision_count: int,
        deferred_decision_count: int,
        more_evidence_requested_count: int,
        external_decision_count: int,
        capability_decision_count: int,
        allowed_actions: list[str],
        recommended_next_step: str,
        decision_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorDecisionLedger:
        ledger_id = new_id("expansion_operator_decision_ledger")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_decision_ledgers (
                    id, status, source_checklist_id, source_checklist_status,
                    source_index_id, source_brief_id, source_audit_id,
                    decision_item_count, pending_decision_count,
                    approved_decision_count, deferred_decision_count,
                    more_evidence_requested_count, external_decision_count,
                    capability_decision_count, allowed_actions,
                    recommended_next_step, decision_items, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    source_index_id,
                    source_brief_id,
                    source_audit_id,
                    decision_item_count,
                    pending_decision_count,
                    approved_decision_count,
                    deferred_decision_count,
                    more_evidence_requested_count,
                    external_decision_count,
                    capability_decision_count,
                    _json_dumps(allowed_actions),
                    recommended_next_step,
                    _json_dumps(decision_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorDecisionLedger(
            id=ledger_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            source_index_id=source_index_id,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            decision_item_count=decision_item_count,
            pending_decision_count=pending_decision_count,
            approved_decision_count=approved_decision_count,
            deferred_decision_count=deferred_decision_count,
            more_evidence_requested_count=more_evidence_requested_count,
            external_decision_count=external_decision_count,
            capability_decision_count=capability_decision_count,
            allowed_actions=allowed_actions,
            recommended_next_step=recommended_next_step,
            decision_items=decision_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_decision_ledgers(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorDecisionLedger]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_decision_ledgers
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_expansion_operator_decision_ledger(row) for row in rows]

    def record_expansion_operator_approval_draft(
        self,
        *,
        status: str,
        source_ledger_id: str,
        source_ledger_status: str,
        source_checklist_id: str,
        source_index_id: str,
        source_brief_id: str,
        source_audit_id: str,
        draft_item_count: int,
        draft_request_count: int,
        created_approval_request_count: int,
        external_draft_count: int,
        capability_draft_count: int,
        approval_boundary_count: int,
        pending_decision_count: int,
        allowed_actions: list[str],
        recommended_next_step: str,
        draft_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalDraft:
        draft_id = new_id("expansion_operator_approval_draft")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_drafts (
                    id, status, source_ledger_id, source_ledger_status,
                    source_checklist_id, source_index_id, source_brief_id,
                    source_audit_id, draft_item_count, draft_request_count,
                    created_approval_request_count, external_draft_count,
                    capability_draft_count, approval_boundary_count,
                    pending_decision_count, allowed_actions,
                    recommended_next_step, draft_items, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    draft_id,
                    status,
                    source_ledger_id,
                    source_ledger_status,
                    source_checklist_id,
                    source_index_id,
                    source_brief_id,
                    source_audit_id,
                    draft_item_count,
                    draft_request_count,
                    created_approval_request_count,
                    external_draft_count,
                    capability_draft_count,
                    approval_boundary_count,
                    pending_decision_count,
                    _json_dumps(allowed_actions),
                    recommended_next_step,
                    _json_dumps(draft_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalDraft(
            id=draft_id,
            status=status,
            source_ledger_id=source_ledger_id,
            source_ledger_status=source_ledger_status,
            source_checklist_id=source_checklist_id,
            source_index_id=source_index_id,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            draft_item_count=draft_item_count,
            draft_request_count=draft_request_count,
            created_approval_request_count=created_approval_request_count,
            external_draft_count=external_draft_count,
            capability_draft_count=capability_draft_count,
            approval_boundary_count=approval_boundary_count,
            pending_decision_count=pending_decision_count,
            allowed_actions=allowed_actions,
            recommended_next_step=recommended_next_step,
            draft_items=draft_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_drafts(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalDraft]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_drafts
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_expansion_operator_approval_draft(row) for row in rows]

    def record_expansion_operator_approval_request_review(
        self,
        *,
        status: str,
        source_draft_id: str,
        source_draft_status: str,
        source_ledger_id: str,
        source_checklist_id: str,
        source_index_id: str,
        source_brief_id: str,
        source_audit_id: str,
        draft_request_count: int,
        review_item_count: int,
        ready_request_count: int,
        blocked_request_count: int,
        schema_gap_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        external_request_count: int,
        capability_request_count: int,
        approval_boundary_count: int,
        recommended_next_step: str,
        review_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalRequestReview:
        review_id = new_id("expansion_operator_approval_request_review")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_request_reviews (
                    id, status, source_draft_id, source_draft_status,
                    source_ledger_id, source_checklist_id, source_index_id,
                    source_brief_id, source_audit_id, draft_request_count,
                    review_item_count, ready_request_count, blocked_request_count,
                    schema_gap_count, created_approval_request_count,
                    existing_approval_request_count, external_request_count,
                    capability_request_count, approval_boundary_count,
                    recommended_next_step, review_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    status,
                    source_draft_id,
                    source_draft_status,
                    source_ledger_id,
                    source_checklist_id,
                    source_index_id,
                    source_brief_id,
                    source_audit_id,
                    draft_request_count,
                    review_item_count,
                    ready_request_count,
                    blocked_request_count,
                    schema_gap_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    external_request_count,
                    capability_request_count,
                    approval_boundary_count,
                    recommended_next_step,
                    _json_dumps(review_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalRequestReview(
            id=review_id,
            status=status,
            source_draft_id=source_draft_id,
            source_draft_status=source_draft_status,
            source_ledger_id=source_ledger_id,
            source_checklist_id=source_checklist_id,
            source_index_id=source_index_id,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            draft_request_count=draft_request_count,
            review_item_count=review_item_count,
            ready_request_count=ready_request_count,
            blocked_request_count=blocked_request_count,
            schema_gap_count=schema_gap_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            external_request_count=external_request_count,
            capability_request_count=capability_request_count,
            approval_boundary_count=approval_boundary_count,
            recommended_next_step=recommended_next_step,
            review_items=review_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_request_reviews(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalRequestReview]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_request_reviews
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_request_review(row)
            for row in rows
        ]

    def record_expansion_operator_approval_schema_decision(
        self,
        *,
        status: str,
        source_review_id: str,
        source_review_status: str,
        source_draft_id: str,
        source_ledger_id: str,
        source_checklist_id: str,
        source_index_id: str,
        source_brief_id: str,
        source_audit_id: str,
        affected_request_count: int,
        schema_gap_count: int,
        missing_field_count: int,
        missing_fields: list[str],
        external_request_count: int,
        capability_request_count: int,
        decision_option_count: int,
        recommended_option: str,
        rejected_option_count: int,
        schema_object_count: int,
        migration_applied_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        recommended_next_step: str,
        decision_options: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalSchemaDecision:
        decision_id = new_id("expansion_operator_approval_schema_decision")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_schema_decisions (
                    id, status, source_review_id, source_review_status,
                    source_draft_id, source_ledger_id, source_checklist_id,
                    source_index_id, source_brief_id, source_audit_id,
                    affected_request_count, schema_gap_count, missing_field_count,
                    missing_fields, external_request_count, capability_request_count,
                    decision_option_count, recommended_option, rejected_option_count,
                    schema_object_count, migration_applied_count,
                    created_approval_request_count, existing_approval_request_count,
                    recommended_next_step, decision_options, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    status,
                    source_review_id,
                    source_review_status,
                    source_draft_id,
                    source_ledger_id,
                    source_checklist_id,
                    source_index_id,
                    source_brief_id,
                    source_audit_id,
                    affected_request_count,
                    schema_gap_count,
                    missing_field_count,
                    _json_dumps(missing_fields),
                    external_request_count,
                    capability_request_count,
                    decision_option_count,
                    recommended_option,
                    rejected_option_count,
                    schema_object_count,
                    migration_applied_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    recommended_next_step,
                    _json_dumps(decision_options),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalSchemaDecision(
            id=decision_id,
            status=status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            source_draft_id=source_draft_id,
            source_ledger_id=source_ledger_id,
            source_checklist_id=source_checklist_id,
            source_index_id=source_index_id,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            affected_request_count=affected_request_count,
            schema_gap_count=schema_gap_count,
            missing_field_count=missing_field_count,
            missing_fields=missing_fields,
            external_request_count=external_request_count,
            capability_request_count=capability_request_count,
            decision_option_count=decision_option_count,
            recommended_option=recommended_option,
            rejected_option_count=rejected_option_count,
            schema_object_count=schema_object_count,
            migration_applied_count=migration_applied_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            recommended_next_step=recommended_next_step,
            decision_options=decision_options,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_schema_decisions(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalSchemaDecision]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_schema_decisions
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_schema_decision(row)
            for row in rows
        ]

    def record_expansion_operator_approval_schema_migration_plan(
        self,
        *,
        status: str,
        source_decision_id: str,
        source_decision_status: str,
        source_review_id: str,
        source_review_status: str,
        source_draft_id: str,
        source_ledger_id: str,
        source_checklist_id: str,
        source_index_id: str,
        source_brief_id: str,
        source_audit_id: str,
        recommended_option: str,
        target_table: str,
        affected_request_count: int,
        schema_gap_count: int,
        missing_field_count: int,
        external_request_count: int,
        capability_request_count: int,
        planned_column_count: int,
        planned_index_count: int,
        migration_step_count: int,
        migration_applied_count: int,
        table_created_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        recommended_next_step: str,
        planned_columns: list[dict[str, Any]],
        planned_indexes: list[dict[str, Any]],
        migration_steps: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalSchemaMigrationPlan:
        plan_id = new_id("expansion_operator_approval_schema_migration_plan")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_schema_migration_plans (
                    id, status, source_decision_id, source_decision_status,
                    source_review_id, source_review_status, source_draft_id,
                    source_ledger_id, source_checklist_id, source_index_id,
                    source_brief_id, source_audit_id, recommended_option,
                    target_table, affected_request_count, schema_gap_count,
                    missing_field_count, external_request_count,
                    capability_request_count, planned_column_count,
                    planned_index_count, migration_step_count,
                    migration_applied_count, table_created_count,
                    operator_approval_row_count, created_approval_request_count,
                    existing_approval_request_count, recommended_next_step,
                    planned_columns, planned_indexes, migration_steps,
                    report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan_id,
                    status,
                    source_decision_id,
                    source_decision_status,
                    source_review_id,
                    source_review_status,
                    source_draft_id,
                    source_ledger_id,
                    source_checklist_id,
                    source_index_id,
                    source_brief_id,
                    source_audit_id,
                    recommended_option,
                    target_table,
                    affected_request_count,
                    schema_gap_count,
                    missing_field_count,
                    external_request_count,
                    capability_request_count,
                    planned_column_count,
                    planned_index_count,
                    migration_step_count,
                    migration_applied_count,
                    table_created_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    recommended_next_step,
                    _json_dumps(planned_columns),
                    _json_dumps(planned_indexes),
                    _json_dumps(migration_steps),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalSchemaMigrationPlan(
            id=plan_id,
            status=status,
            source_decision_id=source_decision_id,
            source_decision_status=source_decision_status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            source_draft_id=source_draft_id,
            source_ledger_id=source_ledger_id,
            source_checklist_id=source_checklist_id,
            source_index_id=source_index_id,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            recommended_option=recommended_option,
            target_table=target_table,
            affected_request_count=affected_request_count,
            schema_gap_count=schema_gap_count,
            missing_field_count=missing_field_count,
            external_request_count=external_request_count,
            capability_request_count=capability_request_count,
            planned_column_count=planned_column_count,
            planned_index_count=planned_index_count,
            migration_step_count=migration_step_count,
            migration_applied_count=migration_applied_count,
            table_created_count=table_created_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            recommended_next_step=recommended_next_step,
            planned_columns=planned_columns,
            planned_indexes=planned_indexes,
            migration_steps=migration_steps,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_schema_migration_plans(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalSchemaMigrationPlan]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_schema_migration_plans
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_schema_migration_plan(row)
            for row in rows
        ]

    def record_expansion_operator_approval_schema_migration_approval_request(
        self,
        *,
        status: str,
        source_plan_id: str,
        source_plan_status: str,
        source_decision_id: str,
        source_decision_status: str,
        source_review_id: str,
        source_review_status: str,
        target_table: str,
        planned_column_count: int,
        planned_index_count: int,
        migration_step_count: int,
        affected_request_count: int,
        schema_gap_count: int,
        request_count: int,
        approval_boundary: str,
        requested_action: str,
        allowed_actions: list[str],
        migration_applied_count: int,
        table_created_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        recommended_next_step: str,
        approval_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalSchemaMigrationApprovalRequest:
        request_id = new_id(
            "expansion_operator_approval_schema_migration_approval_request"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_schema_migration_approval_requests (
                    id, status, source_plan_id, source_plan_status,
                    source_decision_id, source_decision_status,
                    source_review_id, source_review_status, target_table,
                    planned_column_count, planned_index_count,
                    migration_step_count, affected_request_count,
                    schema_gap_count, request_count, approval_boundary,
                    requested_action, allowed_actions, migration_applied_count,
                    table_created_count, operator_approval_row_count,
                    created_approval_request_count, existing_approval_request_count,
                    recommended_next_step, approval_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request_id,
                    status,
                    source_plan_id,
                    source_plan_status,
                    source_decision_id,
                    source_decision_status,
                    source_review_id,
                    source_review_status,
                    target_table,
                    planned_column_count,
                    planned_index_count,
                    migration_step_count,
                    affected_request_count,
                    schema_gap_count,
                    request_count,
                    approval_boundary,
                    requested_action,
                    _json_dumps(allowed_actions),
                    migration_applied_count,
                    table_created_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    recommended_next_step,
                    _json_dumps(approval_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalSchemaMigrationApprovalRequest(
            id=request_id,
            status=status,
            source_plan_id=source_plan_id,
            source_plan_status=source_plan_status,
            source_decision_id=source_decision_id,
            source_decision_status=source_decision_status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            target_table=target_table,
            planned_column_count=planned_column_count,
            planned_index_count=planned_index_count,
            migration_step_count=migration_step_count,
            affected_request_count=affected_request_count,
            schema_gap_count=schema_gap_count,
            request_count=request_count,
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=migration_applied_count,
            table_created_count=table_created_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            recommended_next_step=recommended_next_step,
            approval_items=approval_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_schema_migration_approval_requests(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalSchemaMigrationApprovalRequest]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_schema_migration_approval_requests
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_schema_migration_approval_request(
                row
            )
            for row in rows
        ]

    def record_expansion_operator_approval_schema_migration_decision_ledger(
        self,
        *,
        status: str,
        source_request_id: str,
        source_request_status: str,
        source_plan_id: str,
        source_plan_status: str,
        source_decision_id: str,
        source_decision_status: str,
        source_review_id: str,
        source_review_status: str,
        target_table: str,
        planned_column_count: int,
        planned_index_count: int,
        migration_step_count: int,
        affected_request_count: int,
        schema_gap_count: int,
        request_count: int,
        decision_count: int,
        pending_decision_count: int,
        approved_decision_count: int,
        deferred_decision_count: int,
        more_evidence_decision_count: int,
        approval_boundary: str,
        requested_action: str,
        allowed_actions: list[str],
        migration_applied_count: int,
        table_created_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        recommended_next_step: str,
        decision_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalSchemaMigrationDecisionLedger:
        ledger_id = new_id(
            "expansion_operator_approval_schema_migration_decision_ledger"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_schema_migration_decision_ledgers (
                    id, status, source_request_id, source_request_status,
                    source_plan_id, source_plan_status, source_decision_id,
                    source_decision_status, source_review_id,
                    source_review_status, target_table, planned_column_count,
                    planned_index_count, migration_step_count,
                    affected_request_count, schema_gap_count, request_count,
                    decision_count, pending_decision_count,
                    approved_decision_count, deferred_decision_count,
                    more_evidence_decision_count, approval_boundary,
                    requested_action, allowed_actions, migration_applied_count,
                    table_created_count, operator_approval_row_count,
                    created_approval_request_count, existing_approval_request_count,
                    recommended_next_step, decision_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ledger_id,
                    status,
                    source_request_id,
                    source_request_status,
                    source_plan_id,
                    source_plan_status,
                    source_decision_id,
                    source_decision_status,
                    source_review_id,
                    source_review_status,
                    target_table,
                    planned_column_count,
                    planned_index_count,
                    migration_step_count,
                    affected_request_count,
                    schema_gap_count,
                    request_count,
                    decision_count,
                    pending_decision_count,
                    approved_decision_count,
                    deferred_decision_count,
                    more_evidence_decision_count,
                    approval_boundary,
                    requested_action,
                    _json_dumps(allowed_actions),
                    migration_applied_count,
                    table_created_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    recommended_next_step,
                    _json_dumps(decision_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalSchemaMigrationDecisionLedger(
            id=ledger_id,
            status=status,
            source_request_id=source_request_id,
            source_request_status=source_request_status,
            source_plan_id=source_plan_id,
            source_plan_status=source_plan_status,
            source_decision_id=source_decision_id,
            source_decision_status=source_decision_status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            target_table=target_table,
            planned_column_count=planned_column_count,
            planned_index_count=planned_index_count,
            migration_step_count=migration_step_count,
            affected_request_count=affected_request_count,
            schema_gap_count=schema_gap_count,
            request_count=request_count,
            decision_count=decision_count,
            pending_decision_count=pending_decision_count,
            approved_decision_count=approved_decision_count,
            deferred_decision_count=deferred_decision_count,
            more_evidence_decision_count=more_evidence_decision_count,
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=migration_applied_count,
            table_created_count=table_created_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            recommended_next_step=recommended_next_step,
            decision_items=decision_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_schema_migration_decision_ledgers(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalSchemaMigrationDecisionLedger]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_schema_migration_decision_ledgers
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_schema_migration_decision_ledger(
                row
            )
            for row in rows
        ]

    def record_expansion_operator_approval_schema_migration_action_checklist(
        self,
        *,
        status: str,
        source_ledger_id: str,
        source_ledger_status: str,
        source_request_id: str,
        source_request_status: str,
        source_plan_id: str,
        source_plan_status: str,
        source_decision_id: str,
        source_decision_status: str,
        source_review_id: str,
        source_review_status: str,
        target_table: str,
        request_count: int,
        decision_count: int,
        pending_decision_count: int,
        action_count: int,
        pending_action_count: int,
        actions_taken_count: int,
        selected_action: str,
        approval_boundary: str,
        requested_action: str,
        allowed_actions: list[str],
        migration_applied_count: int,
        table_created_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        recommended_next_step: str,
        action_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalSchemaMigrationActionChecklist:
        checklist_id = new_id(
            "expansion_operator_approval_schema_migration_action_checklist"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_schema_migration_action_checklists (
                    id, status, source_ledger_id, source_ledger_status,
                    source_request_id, source_request_status, source_plan_id,
                    source_plan_status, source_decision_id,
                    source_decision_status, source_review_id,
                    source_review_status, target_table, request_count,
                    decision_count, pending_decision_count, action_count,
                    pending_action_count, actions_taken_count, selected_action,
                    approval_boundary, requested_action, allowed_actions,
                    migration_applied_count, table_created_count,
                    operator_approval_row_count, created_approval_request_count,
                    existing_approval_request_count, recommended_next_step,
                    action_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checklist_id,
                    status,
                    source_ledger_id,
                    source_ledger_status,
                    source_request_id,
                    source_request_status,
                    source_plan_id,
                    source_plan_status,
                    source_decision_id,
                    source_decision_status,
                    source_review_id,
                    source_review_status,
                    target_table,
                    request_count,
                    decision_count,
                    pending_decision_count,
                    action_count,
                    pending_action_count,
                    actions_taken_count,
                    selected_action,
                    approval_boundary,
                    requested_action,
                    _json_dumps(allowed_actions),
                    migration_applied_count,
                    table_created_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    recommended_next_step,
                    _json_dumps(action_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalSchemaMigrationActionChecklist(
            id=checklist_id,
            status=status,
            source_ledger_id=source_ledger_id,
            source_ledger_status=source_ledger_status,
            source_request_id=source_request_id,
            source_request_status=source_request_status,
            source_plan_id=source_plan_id,
            source_plan_status=source_plan_status,
            source_decision_id=source_decision_id,
            source_decision_status=source_decision_status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            target_table=target_table,
            request_count=request_count,
            decision_count=decision_count,
            pending_decision_count=pending_decision_count,
            action_count=action_count,
            pending_action_count=pending_action_count,
            actions_taken_count=actions_taken_count,
            selected_action=selected_action,
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=migration_applied_count,
            table_created_count=table_created_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            recommended_next_step=recommended_next_step,
            action_items=action_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_schema_migration_action_checklists(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalSchemaMigrationActionChecklist]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_schema_migration_action_checklists
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_schema_migration_action_checklist(
                row
            )
            for row in rows
        ]

    def record_expansion_operator_approval_schema_migration_selection_packet(
        self,
        *,
        status: str,
        source_checklist_id: str,
        source_checklist_status: str,
        source_ledger_id: str,
        source_ledger_status: str,
        source_request_id: str,
        source_request_status: str,
        source_plan_id: str,
        source_plan_status: str,
        source_decision_id: str,
        source_decision_status: str,
        source_review_id: str,
        source_review_status: str,
        target_table: str,
        request_count: int,
        decision_count: int,
        pending_decision_count: int,
        action_count: int,
        pending_action_count: int,
        actions_taken_count: int,
        selected_action: str,
        selection_count: int,
        pending_selection_count: int,
        selections_recorded_count: int,
        approve_selection_count: int,
        defer_selection_count: int,
        more_evidence_selection_count: int,
        approval_boundary: str,
        requested_action: str,
        allowed_actions: list[str],
        migration_applied_count: int,
        table_created_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        recommended_next_step: str,
        selection_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalSchemaMigrationSelectionPacket:
        packet_id = new_id(
            "expansion_operator_approval_schema_migration_selection_packet"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_schema_migration_selection_packets (
                    id, status, source_checklist_id, source_checklist_status,
                    source_ledger_id, source_ledger_status, source_request_id,
                    source_request_status, source_plan_id, source_plan_status,
                    source_decision_id, source_decision_status,
                    source_review_id, source_review_status, target_table,
                    request_count, decision_count, pending_decision_count,
                    action_count, pending_action_count, actions_taken_count,
                    selected_action, selection_count, pending_selection_count,
                    selections_recorded_count, approve_selection_count,
                    defer_selection_count, more_evidence_selection_count,
                    approval_boundary, requested_action, allowed_actions,
                    migration_applied_count, table_created_count,
                    operator_approval_row_count, created_approval_request_count,
                    existing_approval_request_count, recommended_next_step,
                    selection_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    packet_id,
                    status,
                    source_checklist_id,
                    source_checklist_status,
                    source_ledger_id,
                    source_ledger_status,
                    source_request_id,
                    source_request_status,
                    source_plan_id,
                    source_plan_status,
                    source_decision_id,
                    source_decision_status,
                    source_review_id,
                    source_review_status,
                    target_table,
                    request_count,
                    decision_count,
                    pending_decision_count,
                    action_count,
                    pending_action_count,
                    actions_taken_count,
                    selected_action,
                    selection_count,
                    pending_selection_count,
                    selections_recorded_count,
                    approve_selection_count,
                    defer_selection_count,
                    more_evidence_selection_count,
                    approval_boundary,
                    requested_action,
                    _json_dumps(allowed_actions),
                    migration_applied_count,
                    table_created_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    recommended_next_step,
                    _json_dumps(selection_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalSchemaMigrationSelectionPacket(
            id=packet_id,
            status=status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            source_ledger_id=source_ledger_id,
            source_ledger_status=source_ledger_status,
            source_request_id=source_request_id,
            source_request_status=source_request_status,
            source_plan_id=source_plan_id,
            source_plan_status=source_plan_status,
            source_decision_id=source_decision_id,
            source_decision_status=source_decision_status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            target_table=target_table,
            request_count=request_count,
            decision_count=decision_count,
            pending_decision_count=pending_decision_count,
            action_count=action_count,
            pending_action_count=pending_action_count,
            actions_taken_count=actions_taken_count,
            selected_action=selected_action,
            selection_count=selection_count,
            pending_selection_count=pending_selection_count,
            selections_recorded_count=selections_recorded_count,
            approve_selection_count=approve_selection_count,
            defer_selection_count=defer_selection_count,
            more_evidence_selection_count=more_evidence_selection_count,
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=migration_applied_count,
            table_created_count=table_created_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            recommended_next_step=recommended_next_step,
            selection_items=selection_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_schema_migration_selection_packets(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalSchemaMigrationSelectionPacket]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_schema_migration_selection_packets
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_schema_migration_selection_packet(
                row
            )
            for row in rows
        ]

    def record_expansion_operator_approval_schema_migration_selection_input_template(
        self,
        *,
        status: str,
        source_packet_id: str,
        source_packet_status: str,
        source_checklist_id: str,
        source_checklist_status: str,
        source_ledger_id: str,
        source_ledger_status: str,
        source_request_id: str,
        source_request_status: str,
        source_plan_id: str,
        source_plan_status: str,
        source_decision_id: str,
        source_decision_status: str,
        source_review_id: str,
        source_review_status: str,
        target_table: str,
        request_count: int,
        decision_count: int,
        pending_decision_count: int,
        action_count: int,
        pending_action_count: int,
        actions_taken_count: int,
        selected_action: str,
        selection_count: int,
        pending_selection_count: int,
        selections_recorded_count: int,
        approve_selection_count: int,
        defer_selection_count: int,
        more_evidence_selection_count: int,
        template_count: int,
        pending_input_count: int,
        inputs_recorded_count: int,
        required_fields_count: int,
        missing_required_input_count: int,
        approval_boundary: str,
        requested_action: str,
        allowed_actions: list[str],
        migration_applied_count: int,
        table_created_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        recommended_next_step: str,
        input_template_items: list[dict[str, Any]],
        report_path: str,
    ) -> ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate:
        template_id = new_id(
            "expansion_operator_approval_schema_migration_selection_input_template"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into expansion_operator_approval_schema_migration_selection_input_templates (
                    id, status, source_packet_id, source_packet_status,
                    source_checklist_id, source_checklist_status,
                    source_ledger_id, source_ledger_status, source_request_id,
                    source_request_status, source_plan_id, source_plan_status,
                    source_decision_id, source_decision_status,
                    source_review_id, source_review_status, target_table,
                    request_count, decision_count, pending_decision_count,
                    action_count, pending_action_count, actions_taken_count,
                    selected_action, selection_count, pending_selection_count,
                    selections_recorded_count, approve_selection_count,
                    defer_selection_count, more_evidence_selection_count,
                    template_count, pending_input_count, inputs_recorded_count,
                    required_fields_count, missing_required_input_count,
                    approval_boundary, requested_action, allowed_actions,
                    migration_applied_count, table_created_count,
                    operator_approval_row_count, created_approval_request_count,
                    existing_approval_request_count, recommended_next_step,
                    input_template_items, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    template_id,
                    status,
                    source_packet_id,
                    source_packet_status,
                    source_checklist_id,
                    source_checklist_status,
                    source_ledger_id,
                    source_ledger_status,
                    source_request_id,
                    source_request_status,
                    source_plan_id,
                    source_plan_status,
                    source_decision_id,
                    source_decision_status,
                    source_review_id,
                    source_review_status,
                    target_table,
                    request_count,
                    decision_count,
                    pending_decision_count,
                    action_count,
                    pending_action_count,
                    actions_taken_count,
                    selected_action,
                    selection_count,
                    pending_selection_count,
                    selections_recorded_count,
                    approve_selection_count,
                    defer_selection_count,
                    more_evidence_selection_count,
                    template_count,
                    pending_input_count,
                    inputs_recorded_count,
                    required_fields_count,
                    missing_required_input_count,
                    approval_boundary,
                    requested_action,
                    _json_dumps(allowed_actions),
                    migration_applied_count,
                    table_created_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    recommended_next_step,
                    _json_dumps(input_template_items),
                    report_path,
                    created_at,
                ),
            )
        return ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate(
            id=template_id,
            status=status,
            source_packet_id=source_packet_id,
            source_packet_status=source_packet_status,
            source_checklist_id=source_checklist_id,
            source_checklist_status=source_checklist_status,
            source_ledger_id=source_ledger_id,
            source_ledger_status=source_ledger_status,
            source_request_id=source_request_id,
            source_request_status=source_request_status,
            source_plan_id=source_plan_id,
            source_plan_status=source_plan_status,
            source_decision_id=source_decision_id,
            source_decision_status=source_decision_status,
            source_review_id=source_review_id,
            source_review_status=source_review_status,
            target_table=target_table,
            request_count=request_count,
            decision_count=decision_count,
            pending_decision_count=pending_decision_count,
            action_count=action_count,
            pending_action_count=pending_action_count,
            actions_taken_count=actions_taken_count,
            selected_action=selected_action,
            selection_count=selection_count,
            pending_selection_count=pending_selection_count,
            selections_recorded_count=selections_recorded_count,
            approve_selection_count=approve_selection_count,
            defer_selection_count=defer_selection_count,
            more_evidence_selection_count=more_evidence_selection_count,
            template_count=template_count,
            pending_input_count=pending_input_count,
            inputs_recorded_count=inputs_recorded_count,
            required_fields_count=required_fields_count,
            missing_required_input_count=missing_required_input_count,
            approval_boundary=approval_boundary,
            requested_action=requested_action,
            allowed_actions=allowed_actions,
            migration_applied_count=migration_applied_count,
            table_created_count=table_created_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            recommended_next_step=recommended_next_step,
            input_template_items=input_template_items,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_expansion_operator_approval_schema_migration_selection_input_templates(
        self,
        limit: int = 5,
    ) -> list[ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from expansion_operator_approval_schema_migration_selection_input_templates
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_expansion_operator_approval_schema_migration_selection_input_template(
                row
            )
            for row in rows
        ]

    def operator_approval_requests_table_exists(self) -> bool:
        with self._connect() as connection:
            return self._table_exists(connection, "operator_approval_requests")

    def create_operator_approval_requests_schema(
        self,
        *,
        columns: list[dict[str, Any]],
        indexes: list[dict[str, Any]],
    ) -> tuple[bool, list[dict[str, Any]], list[dict[str, Any]]]:
        with self._connect() as connection:
            table_already_exists = self._table_exists(
                connection,
                "operator_approval_requests",
            )
            column_sql = ",\n                    ".join(
                f"{column['name']} {column['definition']}" for column in columns
            )
            connection.execute(
                f"""
                create table if not exists operator_approval_requests (
                    {column_sql}
                )
                """
            )
            for index in indexes:
                index_columns = ", ".join(index["columns"])
                connection.execute(
                    f"""
                    create index if not exists {index['name']}
                    on operator_approval_requests ({index_columns})
                    """
                )
        return (not table_already_exists), columns, indexes

    def record_operator_approval_schema_migration_application(
        self,
        *,
        status: str,
        source_template_id: str,
        source_template_status: str,
        source_packet_id: str,
        source_checklist_id: str,
        source_ledger_id: str,
        source_request_id: str,
        source_plan_id: str,
        source_decision_id: str,
        source_review_id: str,
        target_table: str,
        operator_id: str,
        selected_action: str,
        selection_note: str,
        evidence_reference: str,
        inputs_recorded_count: int,
        missing_required_input_count: int,
        actions_taken_count: int,
        migration_applied_count: int,
        table_created_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_approval_request_count: int,
        applied_table_columns: list[dict[str, Any]],
        applied_indexes: list[dict[str, Any]],
        report_path: str,
    ) -> OperatorApprovalSchemaMigrationApplication:
        application_id = new_id("operator_approval_schema_migration_application")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into operator_approval_schema_migration_applications (
                    id, status, source_template_id, source_template_status,
                    source_packet_id, source_checklist_id, source_ledger_id,
                    source_request_id, source_plan_id, source_decision_id,
                    source_review_id, target_table, operator_id,
                    selected_action, selection_note, evidence_reference,
                    inputs_recorded_count, missing_required_input_count,
                    actions_taken_count, migration_applied_count,
                    table_created_count, operator_approval_row_count,
                    created_approval_request_count, existing_approval_request_count,
                    applied_table_columns, applied_indexes, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id,
                    status,
                    source_template_id,
                    source_template_status,
                    source_packet_id,
                    source_checklist_id,
                    source_ledger_id,
                    source_request_id,
                    source_plan_id,
                    source_decision_id,
                    source_review_id,
                    target_table,
                    operator_id,
                    selected_action,
                    selection_note,
                    evidence_reference,
                    inputs_recorded_count,
                    missing_required_input_count,
                    actions_taken_count,
                    migration_applied_count,
                    table_created_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_approval_request_count,
                    _json_dumps(applied_table_columns),
                    _json_dumps(applied_indexes),
                    report_path,
                    created_at,
                ),
            )
        return OperatorApprovalSchemaMigrationApplication(
            id=application_id,
            status=status,
            source_template_id=source_template_id,
            source_template_status=source_template_status,
            source_packet_id=source_packet_id,
            source_checklist_id=source_checklist_id,
            source_ledger_id=source_ledger_id,
            source_request_id=source_request_id,
            source_plan_id=source_plan_id,
            source_decision_id=source_decision_id,
            source_review_id=source_review_id,
            target_table=target_table,
            operator_id=operator_id,
            selected_action=selected_action,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            inputs_recorded_count=inputs_recorded_count,
            missing_required_input_count=missing_required_input_count,
            actions_taken_count=actions_taken_count,
            migration_applied_count=migration_applied_count,
            table_created_count=table_created_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_approval_request_count=existing_approval_request_count,
            applied_table_columns=applied_table_columns,
            applied_indexes=applied_indexes,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_operator_approval_schema_migration_applications(
        self,
        limit: int = 5,
    ) -> list[OperatorApprovalSchemaMigrationApplication]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from operator_approval_schema_migration_applications
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_operator_approval_schema_migration_application(row)
            for row in rows
        ]

    def list_operator_approval_requests(
        self,
        *,
        source_draft_id: str | None = None,
    ) -> list[OperatorApprovalRequest]:
        with self._connect() as connection:
            if not self._table_exists(connection, "operator_approval_requests"):
                return []
            if source_draft_id is None:
                rows = connection.execute(
                    """
                    select * from operator_approval_requests
                    order by requested_at asc, id asc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from operator_approval_requests
                    where source_draft_id = ?
                    order by requested_at asc, id asc
                    """,
                    (source_draft_id,),
                ).fetchall()
        return [self._row_to_operator_approval_request(row) for row in rows]

    def count_operator_approval_requests(
        self,
        *,
        source_draft_id: str | None = None,
    ) -> int:
        with self._connect() as connection:
            if not self._table_exists(connection, "operator_approval_requests"):
                return 0
            if source_draft_id is None:
                row = connection.execute(
                    "select count(*) as count from operator_approval_requests"
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    select count(*) as count from operator_approval_requests
                    where source_draft_id = ?
                    """,
                    (source_draft_id,),
                ).fetchone()
        return int(row["count"])

    def create_operator_approval_requests_from_draft(
        self,
        *,
        draft: ExpansionOperatorApprovalDraft,
        operator_id: str,
        policy_name: str,
        policy_version: str,
    ) -> list[OperatorApprovalRequest]:
        created_requests: list[OperatorApprovalRequest] = []
        with self._connect() as connection:
            if not self._table_exists(connection, "operator_approval_requests"):
                return []
            existing_count = int(
                connection.execute(
                    """
                    select count(*) as count from operator_approval_requests
                    where source_draft_id = ?
                    """,
                    (draft.id,),
                ).fetchone()["count"]
            )
            if existing_count > 0:
                return []
            for index, item in enumerate(draft.draft_items):
                created_at = utc_now()
                request_id = new_id("operator_approval_request")
                source_decision_id = f"{draft.source_ledger_id}:item:{index}"
                subject_type = item["review_type"]
                subject_key = item.get("requirement") or item["decision"]
                capability_key = item.get("requirement")
                allowed_actions = item["allowed_actions"]
                values = {
                    "id": request_id,
                    "source_decision_id": source_decision_id,
                    "source_review_id": draft.source_checklist_id,
                    "source_draft_id": draft.id,
                    "source_ledger_id": draft.source_ledger_id,
                    "source_checklist_id": draft.source_checklist_id,
                    "source_index_id": draft.source_index_id,
                    "source_brief_id": draft.source_brief_id,
                    "source_audit_id": draft.source_audit_id,
                    "subject_type": subject_type,
                    "subject_key": subject_key,
                    "request_kind": item["approval_request_kind"],
                    "capability_key": capability_key,
                    "approval_boundary": item["approval_boundary"],
                    "allowed_actions": allowed_actions,
                    "status": "pending",
                    "reason": item["decision"],
                    "policy_name": policy_name,
                    "policy_version": policy_version,
                    "requested_by": operator_id,
                    "decided_by": None,
                    "decision_note": None,
                    "requested_at": created_at,
                    "decided_at": None,
                    "evidence_path": item.get("evidence_path"),
                    "created_at": created_at,
                }
                connection.execute(
                    """
                    insert into operator_approval_requests (
                        id, source_decision_id, source_review_id, source_draft_id,
                        source_ledger_id, source_checklist_id, source_index_id,
                        source_brief_id, source_audit_id, subject_type,
                        subject_key, request_kind, capability_key,
                        approval_boundary, allowed_actions, status, reason,
                        policy_name, policy_version, requested_by, decided_by,
                        decision_note, requested_at, decided_at, evidence_path,
                        created_at
                    )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        values["id"],
                        values["source_decision_id"],
                        values["source_review_id"],
                        values["source_draft_id"],
                        values["source_ledger_id"],
                        values["source_checklist_id"],
                        values["source_index_id"],
                        values["source_brief_id"],
                        values["source_audit_id"],
                        values["subject_type"],
                        values["subject_key"],
                        values["request_kind"],
                        values["capability_key"],
                        values["approval_boundary"],
                        _json_dumps(values["allowed_actions"]),
                        values["status"],
                        values["reason"],
                        values["policy_name"],
                        values["policy_version"],
                        values["requested_by"],
                        values["decided_by"],
                        values["decision_note"],
                        values["requested_at"],
                        values["decided_at"],
                        values["evidence_path"],
                        values["created_at"],
                    ),
                )
                created_requests.append(
                    OperatorApprovalRequest(
                        id=values["id"],
                        source_decision_id=values["source_decision_id"],
                        source_review_id=values["source_review_id"],
                        source_draft_id=values["source_draft_id"],
                        source_ledger_id=values["source_ledger_id"],
                        source_checklist_id=values["source_checklist_id"],
                        source_index_id=values["source_index_id"],
                        source_brief_id=values["source_brief_id"],
                        source_audit_id=values["source_audit_id"],
                        subject_type=values["subject_type"],
                        subject_key=values["subject_key"],
                        request_kind=values["request_kind"],
                        capability_key=values["capability_key"],
                        approval_boundary=values["approval_boundary"],
                        allowed_actions=values["allowed_actions"],
                        status=values["status"],
                        reason=values["reason"],
                        policy_name=values["policy_name"],
                        policy_version=values["policy_version"],
                        requested_by=values["requested_by"],
                        decided_by=values["decided_by"],
                        decision_note=values["decision_note"],
                        requested_at=values["requested_at"],
                        decided_at=values["decided_at"],
                        evidence_path=values["evidence_path"],
                        created_at=values["created_at"],
                    )
                )
        return created_requests

    def record_operator_approval_request_row_application(
        self,
        *,
        status: str,
        source_draft_id: str,
        source_draft_status: str,
        source_schema_application_id: str,
        source_schema_application_status: str,
        source_ledger_id: str,
        source_checklist_id: str,
        source_index_id: str,
        source_brief_id: str,
        source_audit_id: str,
        operator_id: str,
        selected_action: str,
        selection_note: str,
        evidence_reference: str,
        draft_request_count: int,
        operator_approval_row_count: int,
        created_approval_request_count: int,
        existing_operator_approval_request_count: int,
        external_request_count: int,
        capability_request_count: int,
        created_request_ids: list[str],
        report_path: str,
    ) -> OperatorApprovalRequestRowApplication:
        application_id = new_id("operator_approval_request_row_application")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into operator_approval_request_row_applications (
                    id, status, source_draft_id, source_draft_status,
                    source_schema_application_id, source_schema_application_status,
                    source_ledger_id, source_checklist_id, source_index_id,
                    source_brief_id, source_audit_id, operator_id,
                    selected_action, selection_note, evidence_reference,
                    draft_request_count, operator_approval_row_count,
                    created_approval_request_count,
                    existing_operator_approval_request_count,
                    external_request_count, capability_request_count,
                    created_request_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id,
                    status,
                    source_draft_id,
                    source_draft_status,
                    source_schema_application_id,
                    source_schema_application_status,
                    source_ledger_id,
                    source_checklist_id,
                    source_index_id,
                    source_brief_id,
                    source_audit_id,
                    operator_id,
                    selected_action,
                    selection_note,
                    evidence_reference,
                    draft_request_count,
                    operator_approval_row_count,
                    created_approval_request_count,
                    existing_operator_approval_request_count,
                    external_request_count,
                    capability_request_count,
                    _json_dumps(created_request_ids),
                    report_path,
                    created_at,
                ),
            )
        return OperatorApprovalRequestRowApplication(
            id=application_id,
            status=status,
            source_draft_id=source_draft_id,
            source_draft_status=source_draft_status,
            source_schema_application_id=source_schema_application_id,
            source_schema_application_status=source_schema_application_status,
            source_ledger_id=source_ledger_id,
            source_checklist_id=source_checklist_id,
            source_index_id=source_index_id,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            operator_id=operator_id,
            selected_action=selected_action,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            draft_request_count=draft_request_count,
            operator_approval_row_count=operator_approval_row_count,
            created_approval_request_count=created_approval_request_count,
            existing_operator_approval_request_count=existing_operator_approval_request_count,
            external_request_count=external_request_count,
            capability_request_count=capability_request_count,
            created_request_ids=created_request_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_operator_approval_request_row_applications(
        self,
        limit: int = 5,
    ) -> list[OperatorApprovalRequestRowApplication]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from operator_approval_request_row_applications
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_operator_approval_request_row_application(row)
            for row in rows
        ]

    def count_operator_approval_requests_with_status(
        self,
        *,
        source_draft_id: str,
        statuses: list[str],
    ) -> int:
        if not statuses:
            return 0
        placeholders = ",".join("?" for _ in statuses)
        with self._connect() as connection:
            if not self._table_exists(connection, "operator_approval_requests"):
                return 0
            row = connection.execute(
                f"""
                select count(*) as count from operator_approval_requests
                where source_draft_id = ? and status in ({placeholders})
                """,
                (source_draft_id, *statuses),
            ).fetchone()
        return int(row["count"])

    def decide_pending_operator_approval_requests(
        self,
        *,
        source_draft_id: str,
        selected_action: str,
        decided_by: str,
        decision_note: str,
    ) -> list[OperatorApprovalRequest]:
        status_by_action = {
            "approve": "approved",
            "defer": "deferred",
            "request_more_evidence": "more_evidence_requested",
        }
        decided_status = status_by_action[selected_action]
        decided_at = utc_now()
        with self._connect() as connection:
            if not self._table_exists(connection, "operator_approval_requests"):
                return []
            pending_rows = connection.execute(
                """
                select * from operator_approval_requests
                where source_draft_id = ? and status = 'pending'
                order by requested_at asc, id asc
                """,
                (source_draft_id,),
            ).fetchall()
            if not pending_rows:
                return []
            pending_ids = [row["id"] for row in pending_rows]
            connection.executemany(
                """
                update operator_approval_requests
                set status = ?,
                    decided_by = ?,
                    decision_note = ?,
                    decided_at = ?
                where id = ?
                """,
                [
                    (
                        decided_status,
                        decided_by,
                        decision_note,
                        decided_at,
                        request_id,
                    )
                    for request_id in pending_ids
                ],
            )
            placeholders = ",".join("?" for _ in pending_ids)
            rows = connection.execute(
                f"""
                select * from operator_approval_requests
                where id in ({placeholders})
                order by requested_at asc, id asc
                """,
                tuple(pending_ids),
            ).fetchall()
        return [self._row_to_operator_approval_request(row) for row in rows]

    def record_operator_approval_request_decision(
        self,
        *,
        status: str,
        source_row_application_id: str,
        source_row_application_status: str,
        source_draft_id: str,
        source_schema_application_id: str,
        source_ledger_id: str,
        source_checklist_id: str,
        source_index_id: str,
        source_brief_id: str,
        source_audit_id: str,
        operator_id: str,
        selected_action: str,
        selection_note: str,
        evidence_reference: str,
        pending_request_count_before: int,
        decision_count: int,
        approved_decision_count: int,
        deferred_decision_count: int,
        more_evidence_decision_count: int,
        pending_request_count_after: int,
        existing_decision_count: int,
        created_approval_request_count: int,
        external_request_count: int,
        capability_request_count: int,
        decided_request_ids: list[str],
        report_path: str,
    ) -> OperatorApprovalRequestDecision:
        decision_id = new_id("operator_approval_request_decision")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into operator_approval_request_decisions (
                    id, status, source_row_application_id,
                    source_row_application_status, source_draft_id,
                    source_schema_application_id, source_ledger_id,
                    source_checklist_id, source_index_id, source_brief_id,
                    source_audit_id, operator_id, selected_action,
                    selection_note, evidence_reference,
                    pending_request_count_before, decision_count,
                    approved_decision_count, deferred_decision_count,
                    more_evidence_decision_count, pending_request_count_after,
                    existing_decision_count, created_approval_request_count,
                    external_request_count, capability_request_count,
                    decided_request_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    status,
                    source_row_application_id,
                    source_row_application_status,
                    source_draft_id,
                    source_schema_application_id,
                    source_ledger_id,
                    source_checklist_id,
                    source_index_id,
                    source_brief_id,
                    source_audit_id,
                    operator_id,
                    selected_action,
                    selection_note,
                    evidence_reference,
                    pending_request_count_before,
                    decision_count,
                    approved_decision_count,
                    deferred_decision_count,
                    more_evidence_decision_count,
                    pending_request_count_after,
                    existing_decision_count,
                    created_approval_request_count,
                    external_request_count,
                    capability_request_count,
                    _json_dumps(decided_request_ids),
                    report_path,
                    created_at,
                ),
            )
        return OperatorApprovalRequestDecision(
            id=decision_id,
            status=status,
            source_row_application_id=source_row_application_id,
            source_row_application_status=source_row_application_status,
            source_draft_id=source_draft_id,
            source_schema_application_id=source_schema_application_id,
            source_ledger_id=source_ledger_id,
            source_checklist_id=source_checklist_id,
            source_index_id=source_index_id,
            source_brief_id=source_brief_id,
            source_audit_id=source_audit_id,
            operator_id=operator_id,
            selected_action=selected_action,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            pending_request_count_before=pending_request_count_before,
            decision_count=decision_count,
            approved_decision_count=approved_decision_count,
            deferred_decision_count=deferred_decision_count,
            more_evidence_decision_count=more_evidence_decision_count,
            pending_request_count_after=pending_request_count_after,
            existing_decision_count=existing_decision_count,
            created_approval_request_count=created_approval_request_count,
            external_request_count=external_request_count,
            capability_request_count=capability_request_count,
            decided_request_ids=decided_request_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_operator_approval_request_decisions(
        self,
        limit: int = 5,
    ) -> list[OperatorApprovalRequestDecision]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from operator_approval_request_decisions
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_operator_approval_request_decision(row) for row in rows]

    def record_operator_approval_effect_application(
        self,
        *,
        status: str,
        operator_id: str,
        selection_note: str,
        evidence_reference: str,
        proposed_effect_count: int,
        applied_effect_count: int,
        existing_applied_effect_count: int,
        external_effect_count: int,
        capability_effect_count: int,
        legacy_approval_request_count: int,
        activation_action_count: int,
        applied_effect_ids: list[str],
        report_path: str,
    ) -> OperatorApprovalEffectApplication:
        application_id = new_id("operator_approval_effect_application")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into operator_approval_effect_applications (
                    id, status, operator_id, selection_note, evidence_reference,
                    proposed_effect_count, applied_effect_count,
                    existing_applied_effect_count, external_effect_count,
                    capability_effect_count, legacy_approval_request_count,
                    activation_action_count, applied_effect_ids, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id,
                    status,
                    operator_id,
                    selection_note,
                    evidence_reference,
                    proposed_effect_count,
                    applied_effect_count,
                    existing_applied_effect_count,
                    external_effect_count,
                    capability_effect_count,
                    legacy_approval_request_count,
                    activation_action_count,
                    _json_dumps(applied_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return OperatorApprovalEffectApplication(
            id=application_id,
            status=status,
            operator_id=operator_id,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            proposed_effect_count=proposed_effect_count,
            applied_effect_count=applied_effect_count,
            existing_applied_effect_count=existing_applied_effect_count,
            external_effect_count=external_effect_count,
            capability_effect_count=capability_effect_count,
            legacy_approval_request_count=legacy_approval_request_count,
            activation_action_count=activation_action_count,
            applied_effect_ids=applied_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_operator_approval_effect_applications(
        self,
        limit: int = 5,
    ) -> list[OperatorApprovalEffectApplication]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from operator_approval_effect_applications
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_operator_approval_effect_application(row)
            for row in rows
        ]

    def record_capability_activation_followup_result_effect_application(
        self,
        *,
        status: str,
        operator_id: str,
        selection_note: str,
        evidence_reference: str,
        proposed_effect_count: int,
        applied_effect_count: int,
        existing_applied_effect_count: int,
        capability_effect_count: int,
        approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        applied_effect_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultEffectApplication:
        application_id = new_id(
            "capability_activation_followup_result_effect_application"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_effect_applications (
                    id, status, operator_id, selection_note, evidence_reference,
                    proposed_effect_count, applied_effect_count,
                    existing_applied_effect_count, capability_effect_count,
                    approval_request_count, activation_action_count,
                    external_mutation_count, applied_effect_ids, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id,
                    status,
                    operator_id,
                    selection_note,
                    evidence_reference,
                    proposed_effect_count,
                    applied_effect_count,
                    existing_applied_effect_count,
                    capability_effect_count,
                    approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(applied_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultEffectApplication(
            id=application_id,
            status=status,
            operator_id=operator_id,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            proposed_effect_count=proposed_effect_count,
            applied_effect_count=applied_effect_count,
            existing_applied_effect_count=existing_applied_effect_count,
            capability_effect_count=capability_effect_count,
            approval_request_count=approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            applied_effect_ids=applied_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_effect_applications(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultEffectApplication]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_effect_applications
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_effect_application(row)
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_application(
        self,
        *,
        status: str,
        operator_id: str,
        selection_note: str,
        evidence_reference: str,
        proposed_effect_count: int,
        applied_effect_count: int,
        existing_applied_effect_count: int,
        capability_effect_count: int,
        approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        applied_effect_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectApplication:
        application_id = new_id(
            "capability_activation_followup_result_task_result_effect_application"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_applications (
                    id, status, operator_id, selection_note, evidence_reference,
                    proposed_effect_count, applied_effect_count,
                    existing_applied_effect_count, capability_effect_count,
                    approval_request_count, activation_action_count,
                    external_mutation_count, applied_effect_ids, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id,
                    status,
                    operator_id,
                    selection_note,
                    evidence_reference,
                    proposed_effect_count,
                    applied_effect_count,
                    existing_applied_effect_count,
                    capability_effect_count,
                    approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(applied_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectApplication(
            id=application_id,
            status=status,
            operator_id=operator_id,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            proposed_effect_count=proposed_effect_count,
            applied_effect_count=applied_effect_count,
            existing_applied_effect_count=existing_applied_effect_count,
            capability_effect_count=capability_effect_count,
            approval_request_count=approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            applied_effect_ids=applied_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_effect_applications(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultTaskResultEffectApplication]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_applications
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_application(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_task_result_effect_application(
        self,
        *,
        status: str,
        operator_id: str,
        selection_note: str,
        evidence_reference: str,
        proposed_effect_count: int,
        applied_effect_count: int,
        existing_applied_effect_count: int,
        capability_effect_count: int,
        approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        applied_effect_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectApplication:
        application_id = new_id(
            "capability_activation_followup_result_task_result_effect_task_result_effect_application"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_task_result_effect_applications (
                    id, status, operator_id, selection_note, evidence_reference,
                    proposed_effect_count, applied_effect_count,
                    existing_applied_effect_count, capability_effect_count,
                    approval_request_count, activation_action_count,
                    external_mutation_count, applied_effect_ids, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    application_id,
                    status,
                    operator_id,
                    selection_note,
                    evidence_reference,
                    proposed_effect_count,
                    applied_effect_count,
                    existing_applied_effect_count,
                    capability_effect_count,
                    approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(applied_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectApplication(
            id=application_id,
            status=status,
            operator_id=operator_id,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            proposed_effect_count=proposed_effect_count,
            applied_effect_count=applied_effect_count,
            existing_applied_effect_count=existing_applied_effect_count,
            capability_effect_count=capability_effect_count,
            approval_request_count=approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            applied_effect_ids=applied_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_effect_task_result_effect_applications(
        self,
        limit: int = 5,
    ) -> list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectApplication
    ]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_result_effect_applications
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_result_effect_application(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_task_result_effect_task_batch(
        self,
        *,
        status: str,
        source_application_id: str,
        applied_downstream_effect_count: int,
        task_count: int,
        existing_task_count: int,
        capability_task_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        created_task_ids: list[str],
        source_effect_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskBatch:
        batch_id = new_id(
            "capability_activation_followup_result_task_result_effect_task_result_effect_task_batch"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_task_result_effect_task_batches (
                    id, status, source_application_id,
                    applied_downstream_effect_count, task_count,
                    existing_task_count, capability_task_count,
                    created_approval_request_count, activation_action_count,
                    external_mutation_count, created_task_ids, source_effect_ids,
                    report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    source_application_id,
                    applied_downstream_effect_count,
                    task_count,
                    existing_task_count,
                    capability_task_count,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(created_task_ids),
                    _json_dumps(source_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskBatch(
            id=batch_id,
            status=status,
            source_application_id=source_application_id,
            applied_downstream_effect_count=applied_downstream_effect_count,
            task_count=task_count,
            existing_task_count=existing_task_count,
            capability_task_count=capability_task_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            created_task_ids=created_task_ids,
            source_effect_ids=source_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_effect_task_result_effect_task_batches(
        self,
        limit: int = 5,
    ) -> list[
        CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskBatch
    ]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_result_effect_task_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_result_effect_task_batch(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_task_batch(
        self,
        *,
        status: str,
        source_application_id: str,
        applied_downstream_effect_count: int,
        task_count: int,
        existing_task_count: int,
        capability_task_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        created_task_ids: list[str],
        source_effect_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskBatch:
        batch_id = new_id(
            "capability_activation_followup_result_task_result_effect_task_batch"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_task_batches (
                    id, status, source_application_id,
                    applied_downstream_effect_count, task_count,
                    existing_task_count, capability_task_count,
                    created_approval_request_count, activation_action_count,
                    external_mutation_count, created_task_ids, source_effect_ids,
                    report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    source_application_id,
                    applied_downstream_effect_count,
                    task_count,
                    existing_task_count,
                    capability_task_count,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(created_task_ids),
                    _json_dumps(source_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectTaskBatch(
            id=batch_id,
            status=status,
            source_application_id=source_application_id,
            applied_downstream_effect_count=applied_downstream_effect_count,
            task_count=task_count,
            existing_task_count=existing_task_count,
            capability_task_count=capability_task_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            created_task_ids=created_task_ids,
            source_effect_ids=source_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_effect_task_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultTaskResultEffectTaskBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_batch(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_batch(
        self,
        *,
        status: str,
        source_application_id: str,
        applied_followup_effect_count: int,
        task_count: int,
        existing_task_count: int,
        capability_task_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        created_task_ids: list[str],
        source_effect_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskBatch:
        batch_id = new_id("capability_activation_followup_result_task_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_batches (
                    id, status, source_application_id,
                    applied_followup_effect_count, task_count,
                    existing_task_count, capability_task_count,
                    created_approval_request_count, activation_action_count,
                    external_mutation_count, created_task_ids, source_effect_ids,
                    report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    source_application_id,
                    applied_followup_effect_count,
                    task_count,
                    existing_task_count,
                    capability_task_count,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(created_task_ids),
                    _json_dumps(source_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskBatch(
            id=batch_id,
            status=status,
            source_application_id=source_application_id,
            applied_followup_effect_count=applied_followup_effect_count,
            task_count=task_count,
            existing_task_count=existing_task_count,
            capability_task_count=capability_task_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            created_task_ids=created_task_ids,
            source_effect_ids=source_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultTaskBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_batch(row)
            for row in rows
        ]

    def record_capability_activation_followup_result_task_delegation_batch(
        self,
        *,
        status: str,
        downstream_task_count: int,
        routing_decision_count: int,
        delegation_count: int,
        existing_delegation_count: int,
        execution_started_count: int,
        network_action_count: int,
        external_mutation_count: int,
        activation_action_count: int,
        created_routing_decision_ids: list[str],
        created_delegation_ids: list[str],
        downstream_task_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskDelegationBatch:
        batch_id = new_id(
            "capability_activation_followup_result_task_delegation_batch"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_delegation_batches (
                    id, status, downstream_task_count, routing_decision_count,
                    delegation_count, existing_delegation_count,
                    execution_started_count, network_action_count,
                    external_mutation_count, activation_action_count,
                    created_routing_decision_ids, created_delegation_ids,
                    downstream_task_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    downstream_task_count,
                    routing_decision_count,
                    delegation_count,
                    existing_delegation_count,
                    execution_started_count,
                    network_action_count,
                    external_mutation_count,
                    activation_action_count,
                    _json_dumps(created_routing_decision_ids),
                    _json_dumps(created_delegation_ids),
                    _json_dumps(downstream_task_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskDelegationBatch(
            id=batch_id,
            status=status,
            downstream_task_count=downstream_task_count,
            routing_decision_count=routing_decision_count,
            delegation_count=delegation_count,
            existing_delegation_count=existing_delegation_count,
            execution_started_count=execution_started_count,
            network_action_count=network_action_count,
            external_mutation_count=external_mutation_count,
            activation_action_count=activation_action_count,
            created_routing_decision_ids=created_routing_decision_ids,
            created_delegation_ids=created_delegation_ids,
            downstream_task_ids=downstream_task_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_delegation_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultTaskDelegationBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_delegation_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_delegation_batch(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_task_delegation_batch(
        self,
        *,
        status: str,
        downstream_task_count: int,
        routing_decision_count: int,
        delegation_count: int,
        existing_delegation_count: int,
        execution_started_count: int,
        network_action_count: int,
        external_mutation_count: int,
        activation_action_count: int,
        created_routing_decision_ids: list[str],
        created_delegation_ids: list[str],
        downstream_task_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskDelegationBatch:
        batch_id = new_id(
            "capability_activation_followup_result_task_result_effect_task_delegation_batch"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_task_delegation_batches (
                    id, status, downstream_task_count, routing_decision_count,
                    delegation_count, existing_delegation_count,
                    execution_started_count, network_action_count,
                    external_mutation_count, activation_action_count,
                    created_routing_decision_ids, created_delegation_ids,
                    downstream_task_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    downstream_task_count,
                    routing_decision_count,
                    delegation_count,
                    existing_delegation_count,
                    execution_started_count,
                    network_action_count,
                    external_mutation_count,
                    activation_action_count,
                    _json_dumps(created_routing_decision_ids),
                    _json_dumps(created_delegation_ids),
                    _json_dumps(downstream_task_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectTaskDelegationBatch(
            id=batch_id,
            status=status,
            downstream_task_count=downstream_task_count,
            routing_decision_count=routing_decision_count,
            delegation_count=delegation_count,
            existing_delegation_count=existing_delegation_count,
            execution_started_count=execution_started_count,
            network_action_count=network_action_count,
            external_mutation_count=external_mutation_count,
            activation_action_count=activation_action_count,
            created_routing_decision_ids=created_routing_decision_ids,
            created_delegation_ids=created_delegation_ids,
            downstream_task_ids=downstream_task_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_effect_task_delegation_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultTaskResultEffectTaskDelegationBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_delegation_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_delegation_batch(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_task_result(
        self,
        *,
        delegation_id: str,
        downstream_task_id: str,
        source_application_id: str,
        source_decision_id: str,
        source_downstream_result_id: str,
        source_effect_id: str,
        source_delegation_id: str,
        source_downstream_task_id: str,
        source_followup_result_id: str,
        upstream_followup_effect_id: str,
        source_contract_id: str,
        goal_id: str,
        project_id: str,
        capability: str,
        assigned_profile: str,
        evidence_status: str,
        result_summary: str,
        evidence_path: str,
        result_json: dict[str, object],
        idempotency_key: str,
        activation_allowed: bool,
        capability_enabled: bool,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord:
        result_id = new_id(
            "capability_activation_followup_result_task_result_effect_task_result"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_task_result_records (
                    id, delegation_id, downstream_task_id,
                    source_application_id, source_decision_id,
                    source_downstream_result_id, source_effect_id,
                    source_delegation_id, source_downstream_task_id,
                    source_followup_result_id, upstream_followup_effect_id,
                    source_contract_id, goal_id, project_id, capability,
                    assigned_profile, evidence_status, result_summary,
                    evidence_path, result_json, idempotency_key,
                    activation_allowed, capability_enabled,
                    created_approval_request_count, activation_action_count,
                    external_mutation_count, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_id,
                    delegation_id,
                    downstream_task_id,
                    source_application_id,
                    source_decision_id,
                    source_downstream_result_id,
                    source_effect_id,
                    source_delegation_id,
                    source_downstream_task_id,
                    source_followup_result_id,
                    upstream_followup_effect_id,
                    source_contract_id,
                    goal_id,
                    project_id,
                    capability,
                    assigned_profile,
                    evidence_status,
                    result_summary,
                    evidence_path,
                    _json_dumps(result_json),
                    idempotency_key,
                    1 if activation_allowed else 0,
                    1 if capability_enabled else 0,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord(
            id=result_id,
            delegation_id=delegation_id,
            downstream_task_id=downstream_task_id,
            source_application_id=source_application_id,
            source_decision_id=source_decision_id,
            source_downstream_result_id=source_downstream_result_id,
            source_effect_id=source_effect_id,
            source_delegation_id=source_delegation_id,
            source_downstream_task_id=source_downstream_task_id,
            source_followup_result_id=source_followup_result_id,
            upstream_followup_effect_id=upstream_followup_effect_id,
            source_contract_id=source_contract_id,
            goal_id=goal_id,
            project_id=project_id,
            capability=capability,
            assigned_profile=assigned_profile,
            evidence_status=evidence_status,
            result_summary=result_summary,
            evidence_path=evidence_path,
            result_json=result_json,
            idempotency_key=idempotency_key,
            activation_allowed=activation_allowed,
            capability_enabled=capability_enabled,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            created_at=created_at,
        )

    def get_capability_activation_followup_result_task_result_effect_task_result_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_result_records
                where idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_capability_activation_followup_result_task_result_effect_task_result_record(
            row
        )

    def list_capability_activation_followup_result_task_result_effect_task_result_records(
        self,
    ) -> list[CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_result_records
                order by created_at asc, id asc
                """
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_result_record(
                row
            )
            for row in rows
        ]

    def list_recent_capability_activation_followup_result_task_result_effect_task_result_records(
        self,
        limit: int = 20,
    ) -> list[CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_result_records
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_result_record(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_task_result_batch(
        self,
        *,
        status: str,
        completed_delegation_count: int,
        result_record_count: int,
        existing_result_record_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        created_result_ids: list[str],
        completed_delegation_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultBatch:
        batch_id = new_id(
            "capability_activation_followup_result_task_result_effect_task_result_batch"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_task_result_batches (
                    id, status, completed_delegation_count,
                    result_record_count, existing_result_record_count,
                    created_approval_request_count, activation_action_count,
                    external_mutation_count, created_result_ids,
                    completed_delegation_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    completed_delegation_count,
                    result_record_count,
                    existing_result_record_count,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(created_result_ids),
                    _json_dumps(completed_delegation_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultBatch(
            id=batch_id,
            status=status,
            completed_delegation_count=completed_delegation_count,
            result_record_count=result_record_count,
            existing_result_record_count=existing_result_record_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            created_result_ids=created_result_ids,
            completed_delegation_ids=completed_delegation_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_effect_task_result_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultTaskResultEffectTaskResultBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_effect_task_result_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_result_batch(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_effect_task_result_decision(
        self,
        *,
        status: str,
        operator_id: str,
        selected_action: str,
        selection_note: str,
        evidence_reference: str,
        result_record_count: int,
        decision_count: int,
        accepted_keep_blocked_decision_count: int,
        more_evidence_decision_count: int,
        deferred_decision_count: int,
        existing_decision_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        decided_result_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultDecision:
        decision_id = new_id(
            "capability_activation_followup_result_task_result_effect_task_result_decision"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_effect_task_result_decisions (
                    id, status, operator_id, selected_action, selection_note,
                    evidence_reference, result_record_count, decision_count,
                    accepted_keep_blocked_decision_count,
                    more_evidence_decision_count, deferred_decision_count,
                    existing_decision_count, created_approval_request_count,
                    activation_action_count, external_mutation_count,
                    decided_result_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    status,
                    operator_id,
                    selected_action,
                    selection_note,
                    evidence_reference,
                    result_record_count,
                    decision_count,
                    accepted_keep_blocked_decision_count,
                    more_evidence_decision_count,
                    deferred_decision_count,
                    existing_decision_count,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(decided_result_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultDecision(
            id=decision_id,
            status=status,
            operator_id=operator_id,
            selected_action=selected_action,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            result_record_count=result_record_count,
            decision_count=decision_count,
            accepted_keep_blocked_decision_count=accepted_keep_blocked_decision_count,
            more_evidence_decision_count=more_evidence_decision_count,
            deferred_decision_count=deferred_decision_count,
            existing_decision_count=existing_decision_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            decided_result_ids=decided_result_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_effect_task_result_decisions(
        self,
        limit: int | None = 5,
    ) -> list[CapabilityActivationFollowupResultTaskResultEffectTaskResultDecision]:
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    select * from capability_activation_followup_result_task_result_effect_task_result_decisions
                    order by created_at desc, id desc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from capability_activation_followup_result_task_result_effect_task_result_decisions
                    order by created_at desc, id desc
                    limit ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_effect_task_result_decision(
                row
            )
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result(
        self,
        *,
        delegation_id: str,
        downstream_task_id: str,
        source_result_id: str,
        source_effect_id: str,
        source_contract_id: str,
        goal_id: str,
        project_id: str,
        capability: str,
        assigned_profile: str,
        evidence_status: str,
        result_summary: str,
        evidence_path: str,
        result_json: dict[str, object],
        idempotency_key: str,
        activation_allowed: bool,
        capability_enabled: bool,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
    ) -> CapabilityActivationFollowupResultTaskResultRecord:
        result_id = new_id("capability_activation_followup_result_task_result")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_records (
                    id, delegation_id, downstream_task_id, source_result_id,
                    source_effect_id, source_contract_id, goal_id, project_id,
                    capability, assigned_profile, evidence_status,
                    result_summary, evidence_path, result_json, idempotency_key,
                    activation_allowed, capability_enabled,
                    created_approval_request_count, activation_action_count,
                    external_mutation_count, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_id,
                    delegation_id,
                    downstream_task_id,
                    source_result_id,
                    source_effect_id,
                    source_contract_id,
                    goal_id,
                    project_id,
                    capability,
                    assigned_profile,
                    evidence_status,
                    result_summary,
                    evidence_path,
                    _json_dumps(result_json),
                    idempotency_key,
                    1 if activation_allowed else 0,
                    1 if capability_enabled else 0,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultRecord(
            id=result_id,
            delegation_id=delegation_id,
            downstream_task_id=downstream_task_id,
            source_result_id=source_result_id,
            source_effect_id=source_effect_id,
            source_contract_id=source_contract_id,
            goal_id=goal_id,
            project_id=project_id,
            capability=capability,
            assigned_profile=assigned_profile,
            evidence_status=evidence_status,
            result_summary=result_summary,
            evidence_path=evidence_path,
            result_json=result_json,
            idempotency_key=idempotency_key,
            activation_allowed=activation_allowed,
            capability_enabled=capability_enabled,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            created_at=created_at,
        )

    def get_capability_activation_followup_result_task_result_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> CapabilityActivationFollowupResultTaskResultRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_records
                where idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_capability_activation_followup_result_task_result_record(
            row
        )

    def list_capability_activation_followup_result_task_result_records(
        self,
    ) -> list[CapabilityActivationFollowupResultTaskResultRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_records
                order by created_at asc, id asc
                """
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_record(row)
            for row in rows
        ]

    def list_recent_capability_activation_followup_result_task_result_records(
        self,
        limit: int = 20,
    ) -> list[CapabilityActivationFollowupResultTaskResultRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_records
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_record(row)
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_batch(
        self,
        *,
        status: str,
        completed_delegation_count: int,
        result_record_count: int,
        existing_result_record_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        created_result_ids: list[str],
        completed_delegation_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultBatch:
        batch_id = new_id("capability_activation_followup_result_task_result_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_batches (
                    id, status, completed_delegation_count,
                    result_record_count, existing_result_record_count,
                    created_approval_request_count, activation_action_count,
                    external_mutation_count, created_result_ids,
                    completed_delegation_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    completed_delegation_count,
                    result_record_count,
                    existing_result_record_count,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(created_result_ids),
                    _json_dumps(completed_delegation_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultBatch(
            id=batch_id,
            status=status,
            completed_delegation_count=completed_delegation_count,
            result_record_count=result_record_count,
            existing_result_record_count=existing_result_record_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            created_result_ids=created_result_ids,
            completed_delegation_ids=completed_delegation_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultTaskResultBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_task_result_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_batch(row)
            for row in rows
        ]

    def record_capability_activation_followup_result_task_result_decision(
        self,
        *,
        status: str,
        operator_id: str,
        selected_action: str,
        selection_note: str,
        evidence_reference: str,
        result_record_count: int,
        decision_count: int,
        accepted_keep_blocked_decision_count: int,
        more_evidence_decision_count: int,
        deferred_decision_count: int,
        existing_decision_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        external_mutation_count: int,
        decided_result_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultTaskResultDecision:
        decision_id = new_id(
            "capability_activation_followup_result_task_result_decision"
        )
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_task_result_decisions (
                    id, status, operator_id, selected_action, selection_note,
                    evidence_reference, result_record_count, decision_count,
                    accepted_keep_blocked_decision_count,
                    more_evidence_decision_count, deferred_decision_count,
                    existing_decision_count, created_approval_request_count,
                    activation_action_count, external_mutation_count,
                    decided_result_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    status,
                    operator_id,
                    selected_action,
                    selection_note,
                    evidence_reference,
                    result_record_count,
                    decision_count,
                    accepted_keep_blocked_decision_count,
                    more_evidence_decision_count,
                    deferred_decision_count,
                    existing_decision_count,
                    created_approval_request_count,
                    activation_action_count,
                    external_mutation_count,
                    _json_dumps(decided_result_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultTaskResultDecision(
            id=decision_id,
            status=status,
            operator_id=operator_id,
            selected_action=selected_action,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            result_record_count=result_record_count,
            decision_count=decision_count,
            accepted_keep_blocked_decision_count=accepted_keep_blocked_decision_count,
            more_evidence_decision_count=more_evidence_decision_count,
            deferred_decision_count=deferred_decision_count,
            existing_decision_count=existing_decision_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            external_mutation_count=external_mutation_count,
            decided_result_ids=decided_result_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_task_result_decisions(
        self,
        limit: int | None = 5,
    ) -> list[CapabilityActivationFollowupResultTaskResultDecision]:
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    select * from capability_activation_followup_result_task_result_decisions
                    order by created_at desc, id desc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from capability_activation_followup_result_task_result_decisions
                    order by created_at desc, id desc
                    limit ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_task_result_decision(
                row
            )
            for row in rows
        ]

    def record_capability_activation_task_batch(
        self,
        *,
        status: str,
        source_application_id: str,
        goal_id: str,
        applied_capability_effect_count: int,
        task_count: int,
        existing_task_count: int,
        activation_action_count: int,
        created_task_ids: list[str],
        source_effect_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationTaskBatch:
        batch_id = new_id("capability_activation_task_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_task_batches (
                    id, status, source_application_id, goal_id,
                    applied_capability_effect_count, task_count,
                    existing_task_count, activation_action_count,
                    created_task_ids, source_effect_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    source_application_id,
                    goal_id,
                    applied_capability_effect_count,
                    task_count,
                    existing_task_count,
                    activation_action_count,
                    _json_dumps(created_task_ids),
                    _json_dumps(source_effect_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationTaskBatch(
            id=batch_id,
            status=status,
            source_application_id=source_application_id,
            goal_id=goal_id,
            applied_capability_effect_count=applied_capability_effect_count,
            task_count=task_count,
            existing_task_count=existing_task_count,
            activation_action_count=activation_action_count,
            created_task_ids=created_task_ids,
            source_effect_ids=source_effect_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_task_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationTaskBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_task_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_activation_task_batch(row) for row in rows]

    def record_capability_activation_contract(
        self,
        *,
        task_id: str,
        goal_id: str,
        project_id: str,
        capability: str,
        source_effect_id: str,
        source_application_id: str,
        evidence_requirements: dict[str, object],
        approval_boundary: str,
        approval_status: str,
        required_approval_id: str,
        status: str,
        activation_allowed: bool,
        created_approval_request_count: int,
        activation_action_count: int,
        report_path: str,
    ) -> CapabilityActivationContract:
        contract_id = new_id("capability_activation_contract")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_contracts (
                    id, task_id, goal_id, project_id, capability,
                    source_effect_id, source_application_id,
                    evidence_requirements_json, approval_boundary,
                    approval_status, required_approval_id, status,
                    activation_allowed, created_approval_request_count,
                    activation_action_count, report_path, created_at, updated_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contract_id,
                    task_id,
                    goal_id,
                    project_id,
                    capability,
                    source_effect_id,
                    source_application_id,
                    _json_dumps(evidence_requirements),
                    approval_boundary,
                    approval_status,
                    required_approval_id,
                    status,
                    1 if activation_allowed else 0,
                    created_approval_request_count,
                    activation_action_count,
                    report_path,
                    created_at,
                    created_at,
                ),
            )
        return CapabilityActivationContract(
            id=contract_id,
            task_id=task_id,
            goal_id=goal_id,
            project_id=project_id,
            capability=capability,
            source_effect_id=source_effect_id,
            source_application_id=source_application_id,
            evidence_requirements=evidence_requirements,
            approval_boundary=approval_boundary,
            approval_status=approval_status,
            required_approval_id=required_approval_id,
            status=status,
            activation_allowed=activation_allowed,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            report_path=report_path,
            created_at=created_at,
            updated_at=created_at,
        )

    def list_capability_activation_contracts(
        self,
    ) -> list[CapabilityActivationContract]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_contracts
                order by created_at asc, id asc
                """
            ).fetchall()
        return [self._row_to_capability_activation_contract(row) for row in rows]

    def list_recent_capability_activation_contracts(
        self,
        limit: int = 20,
    ) -> list[CapabilityActivationContract]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_contracts
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_capability_activation_contract(row) for row in rows]

    def record_capability_activation_contract_batch(
        self,
        *,
        status: str,
        source_task_batch_id: str,
        activation_task_count: int,
        contract_count: int,
        existing_contract_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        created_contract_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationContractBatch:
        batch_id = new_id("capability_activation_contract_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_contract_batches (
                    id, status, source_task_batch_id, activation_task_count,
                    contract_count, existing_contract_count,
                    created_approval_request_count, activation_action_count,
                    created_contract_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    source_task_batch_id,
                    activation_task_count,
                    contract_count,
                    existing_contract_count,
                    created_approval_request_count,
                    activation_action_count,
                    _json_dumps(created_contract_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationContractBatch(
            id=batch_id,
            status=status,
            source_task_batch_id=source_task_batch_id,
            activation_task_count=activation_task_count,
            contract_count=contract_count,
            existing_contract_count=existing_contract_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            created_contract_ids=created_contract_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_contract_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationContractBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_contract_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_contract_batch(row)
            for row in rows
        ]

    def get_capability_activation_contract(
        self,
        contract_id: str,
    ) -> CapabilityActivationContract | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from capability_activation_contracts
                where id = ?
                """,
                (contract_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_capability_activation_contract(row)

    def record_capability_activation_evidence(
        self,
        *,
        contract_id: str,
        task_id: str,
        goal_id: str,
        project_id: str,
        capability: str,
        source_effect_id: str,
        evidence_kind: str,
        evidence_reference: str,
        verification_command: str,
        verification_status: str,
        recorded_by: str,
        summary: str,
        status: str,
        evidence_path: str,
        result_json: dict[str, object],
        idempotency_key: str,
        created_approval_request_count: int,
        activation_action_count: int,
    ) -> CapabilityActivationEvidenceRecord:
        evidence_id = new_id("capability_activation_evidence")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_evidence_records (
                    id, contract_id, task_id, goal_id, project_id, capability,
                    source_effect_id, evidence_kind, evidence_reference,
                    verification_command, verification_status, recorded_by,
                    summary, status, evidence_path, result_json,
                    idempotency_key, created_approval_request_count,
                    activation_action_count, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    evidence_id,
                    contract_id,
                    task_id,
                    goal_id,
                    project_id,
                    capability,
                    source_effect_id,
                    evidence_kind,
                    evidence_reference,
                    verification_command,
                    verification_status,
                    recorded_by,
                    summary,
                    status,
                    evidence_path,
                    _json_dumps(result_json),
                    idempotency_key,
                    created_approval_request_count,
                    activation_action_count,
                    created_at,
                ),
            )
            connection.execute(
                """
                update capability_activation_contracts
                set status = ?, approval_status = ?, updated_at = ?
                where id = ?
                """,
                (
                    "evidence_submitted",
                    "operator_decision_pending",
                    created_at,
                    contract_id,
                ),
            )
        return CapabilityActivationEvidenceRecord(
            id=evidence_id,
            contract_id=contract_id,
            task_id=task_id,
            goal_id=goal_id,
            project_id=project_id,
            capability=capability,
            source_effect_id=source_effect_id,
            evidence_kind=evidence_kind,
            evidence_reference=evidence_reference,
            verification_command=verification_command,
            verification_status=verification_status,
            recorded_by=recorded_by,
            summary=summary,
            status=status,
            evidence_path=evidence_path,
            result_json=result_json,
            idempotency_key=idempotency_key,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            created_at=created_at,
        )

    def get_capability_activation_evidence_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> CapabilityActivationEvidenceRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from capability_activation_evidence_records
                where idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_capability_activation_evidence_record(row)

    def list_capability_activation_evidence_records(
        self,
    ) -> list[CapabilityActivationEvidenceRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_evidence_records
                order by created_at asc, id asc
                """
            ).fetchall()
        return [
            self._row_to_capability_activation_evidence_record(row)
            for row in rows
        ]

    def list_recent_capability_activation_evidence_records(
        self,
        limit: int = 20,
    ) -> list[CapabilityActivationEvidenceRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_evidence_records
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_evidence_record(row)
            for row in rows
        ]

    def record_capability_activation_evidence_batch(
        self,
        *,
        status: str,
        contract_count: int,
        evidence_record_count: int,
        existing_evidence_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        created_evidence_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationEvidenceBatch:
        batch_id = new_id("capability_activation_evidence_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_evidence_batches (
                    id, status, contract_count, evidence_record_count,
                    existing_evidence_count, created_approval_request_count,
                    activation_action_count, created_evidence_ids, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    contract_count,
                    evidence_record_count,
                    existing_evidence_count,
                    created_approval_request_count,
                    activation_action_count,
                    _json_dumps(created_evidence_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationEvidenceBatch(
            id=batch_id,
            status=status,
            contract_count=contract_count,
            evidence_record_count=evidence_record_count,
            existing_evidence_count=existing_evidence_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            created_evidence_ids=created_evidence_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_evidence_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationEvidenceBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_evidence_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_evidence_batch(row)
            for row in rows
        ]

    def record_capability_activation_decision(
        self,
        *,
        status: str,
        operator_id: str,
        selected_action: str,
        selection_note: str,
        evidence_reference: str,
        contract_count: int,
        decision_count: int,
        approved_decision_count: int,
        deferred_decision_count: int,
        more_evidence_decision_count: int,
        existing_decision_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        decided_contract_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationDecision:
        decision_id = new_id("capability_activation_decision")
        created_at = utc_now()
        status_by_action = {
            "approve": ("approved_pending_activation", "approved_local_only"),
            "defer": ("deferred_by_operator", "deferred"),
            "request_more_evidence": (
                "more_evidence_requested",
                "more_evidence_requested",
            ),
        }
        contract_status, approval_status = status_by_action[selected_action]
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_decisions (
                    id, status, operator_id, selected_action, selection_note,
                    evidence_reference, contract_count, decision_count,
                    approved_decision_count, deferred_decision_count,
                    more_evidence_decision_count, existing_decision_count,
                    created_approval_request_count, activation_action_count,
                    decided_contract_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    status,
                    operator_id,
                    selected_action,
                    selection_note,
                    evidence_reference,
                    contract_count,
                    decision_count,
                    approved_decision_count,
                    deferred_decision_count,
                    more_evidence_decision_count,
                    existing_decision_count,
                    created_approval_request_count,
                    activation_action_count,
                    _json_dumps(decided_contract_ids),
                    report_path,
                    created_at,
                ),
            )
            for contract_id in decided_contract_ids:
                connection.execute(
                    """
                    update capability_activation_contracts
                    set status = ?, approval_status = ?, updated_at = ?
                    where id = ?
                    """,
                    (contract_status, approval_status, created_at, contract_id),
                )
        return CapabilityActivationDecision(
            id=decision_id,
            status=status,
            operator_id=operator_id,
            selected_action=selected_action,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            contract_count=contract_count,
            decision_count=decision_count,
            approved_decision_count=approved_decision_count,
            deferred_decision_count=deferred_decision_count,
            more_evidence_decision_count=more_evidence_decision_count,
            existing_decision_count=existing_decision_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            decided_contract_ids=decided_contract_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_decisions(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationDecision]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_decisions
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_decision(row)
            for row in rows
        ]

    def record_capability_activation_followup_task_batch(
        self,
        *,
        status: str,
        source_decision_id: str,
        contract_count: int,
        followup_task_count: int,
        existing_followup_task_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        created_task_ids: list[str],
        contract_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupTaskBatch:
        batch_id = new_id("capability_activation_followup_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_task_batches (
                    id, status, source_decision_id, contract_count,
                    followup_task_count, existing_followup_task_count,
                    created_approval_request_count, activation_action_count,
                    created_task_ids, contract_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    source_decision_id,
                    contract_count,
                    followup_task_count,
                    existing_followup_task_count,
                    created_approval_request_count,
                    activation_action_count,
                    _json_dumps(created_task_ids),
                    _json_dumps(contract_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupTaskBatch(
            id=batch_id,
            status=status,
            source_decision_id=source_decision_id,
            contract_count=contract_count,
            followup_task_count=followup_task_count,
            existing_followup_task_count=existing_followup_task_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            created_task_ids=created_task_ids,
            contract_ids=contract_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_task_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupTaskBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_task_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_task_batch(row)
            for row in rows
        ]

    def record_capability_activation_followup_delegation_batch(
        self,
        *,
        status: str,
        followup_task_count: int,
        routing_decision_count: int,
        delegation_count: int,
        existing_delegation_count: int,
        execution_started_count: int,
        network_action_count: int,
        external_mutation_count: int,
        activation_action_count: int,
        created_routing_decision_ids: list[str],
        created_delegation_ids: list[str],
        followup_task_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupDelegationBatch:
        batch_id = new_id("capability_activation_followup_delegation_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_delegation_batches (
                    id, status, followup_task_count, routing_decision_count,
                    delegation_count, existing_delegation_count,
                    execution_started_count, network_action_count,
                    external_mutation_count, activation_action_count,
                    created_routing_decision_ids, created_delegation_ids,
                    followup_task_ids, report_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    followup_task_count,
                    routing_decision_count,
                    delegation_count,
                    existing_delegation_count,
                    execution_started_count,
                    network_action_count,
                    external_mutation_count,
                    activation_action_count,
                    _json_dumps(created_routing_decision_ids),
                    _json_dumps(created_delegation_ids),
                    _json_dumps(followup_task_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupDelegationBatch(
            id=batch_id,
            status=status,
            followup_task_count=followup_task_count,
            routing_decision_count=routing_decision_count,
            delegation_count=delegation_count,
            existing_delegation_count=existing_delegation_count,
            execution_started_count=execution_started_count,
            network_action_count=network_action_count,
            external_mutation_count=external_mutation_count,
            activation_action_count=activation_action_count,
            created_routing_decision_ids=created_routing_decision_ids,
            created_delegation_ids=created_delegation_ids,
            followup_task_ids=followup_task_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_delegation_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupDelegationBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_delegation_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_delegation_batch(row)
            for row in rows
        ]

    def record_capability_activation_followup_result(
        self,
        *,
        delegation_id: str,
        followup_task_id: str,
        contract_id: str,
        decision_id: str,
        goal_id: str,
        project_id: str,
        capability: str,
        assigned_profile: str,
        evidence_status: str,
        result_summary: str,
        evidence_path: str,
        result_json: dict[str, object],
        idempotency_key: str,
        activation_allowed: bool,
        capability_enabled: bool,
        created_approval_request_count: int,
        activation_action_count: int,
    ) -> CapabilityActivationFollowupResultRecord:
        result_id = new_id("capability_activation_followup_result")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_records (
                    id, delegation_id, followup_task_id, contract_id,
                    decision_id, goal_id, project_id, capability,
                    assigned_profile, evidence_status, result_summary,
                    evidence_path, result_json, idempotency_key,
                    activation_allowed, capability_enabled,
                    created_approval_request_count, activation_action_count,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result_id,
                    delegation_id,
                    followup_task_id,
                    contract_id,
                    decision_id,
                    goal_id,
                    project_id,
                    capability,
                    assigned_profile,
                    evidence_status,
                    result_summary,
                    evidence_path,
                    _json_dumps(result_json),
                    idempotency_key,
                    1 if activation_allowed else 0,
                    1 if capability_enabled else 0,
                    created_approval_request_count,
                    activation_action_count,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultRecord(
            id=result_id,
            delegation_id=delegation_id,
            followup_task_id=followup_task_id,
            contract_id=contract_id,
            decision_id=decision_id,
            goal_id=goal_id,
            project_id=project_id,
            capability=capability,
            assigned_profile=assigned_profile,
            evidence_status=evidence_status,
            result_summary=result_summary,
            evidence_path=evidence_path,
            result_json=result_json,
            idempotency_key=idempotency_key,
            activation_allowed=activation_allowed,
            capability_enabled=capability_enabled,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            created_at=created_at,
        )

    def get_capability_activation_followup_result_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> CapabilityActivationFollowupResultRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from capability_activation_followup_result_records
                where idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_capability_activation_followup_result_record(row)

    def list_capability_activation_followup_result_records(
        self,
    ) -> list[CapabilityActivationFollowupResultRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_records
                order by created_at asc, id asc
                """
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_record(row)
            for row in rows
        ]

    def list_recent_capability_activation_followup_result_records(
        self,
        limit: int = 20,
    ) -> list[CapabilityActivationFollowupResultRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_records
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_record(row)
            for row in rows
        ]

    def record_capability_activation_followup_result_batch(
        self,
        *,
        status: str,
        completed_delegation_count: int,
        result_record_count: int,
        existing_result_record_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        created_result_ids: list[str],
        completed_delegation_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultBatch:
        batch_id = new_id("capability_activation_followup_result_batch")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_batches (
                    id, status, completed_delegation_count,
                    result_record_count, existing_result_record_count,
                    created_approval_request_count, activation_action_count,
                    created_result_ids, completed_delegation_ids, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    batch_id,
                    status,
                    completed_delegation_count,
                    result_record_count,
                    existing_result_record_count,
                    created_approval_request_count,
                    activation_action_count,
                    _json_dumps(created_result_ids),
                    _json_dumps(completed_delegation_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultBatch(
            id=batch_id,
            status=status,
            completed_delegation_count=completed_delegation_count,
            result_record_count=result_record_count,
            existing_result_record_count=existing_result_record_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            created_result_ids=created_result_ids,
            completed_delegation_ids=completed_delegation_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_batches(
        self,
        limit: int = 5,
    ) -> list[CapabilityActivationFollowupResultBatch]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from capability_activation_followup_result_batches
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_batch(row)
            for row in rows
        ]

    def record_capability_activation_followup_result_decision(
        self,
        *,
        status: str,
        operator_id: str,
        selected_action: str,
        selection_note: str,
        evidence_reference: str,
        result_record_count: int,
        decision_count: int,
        accepted_keep_blocked_decision_count: int,
        more_evidence_decision_count: int,
        deferred_decision_count: int,
        existing_decision_count: int,
        created_approval_request_count: int,
        activation_action_count: int,
        decided_result_ids: list[str],
        report_path: str,
    ) -> CapabilityActivationFollowupResultDecision:
        decision_id = new_id("capability_activation_followup_result_decision")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into capability_activation_followup_result_decisions (
                    id, status, operator_id, selected_action, selection_note,
                    evidence_reference, result_record_count, decision_count,
                    accepted_keep_blocked_decision_count,
                    more_evidence_decision_count, deferred_decision_count,
                    existing_decision_count, created_approval_request_count,
                    activation_action_count, decided_result_ids, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    status,
                    operator_id,
                    selected_action,
                    selection_note,
                    evidence_reference,
                    result_record_count,
                    decision_count,
                    accepted_keep_blocked_decision_count,
                    more_evidence_decision_count,
                    deferred_decision_count,
                    existing_decision_count,
                    created_approval_request_count,
                    activation_action_count,
                    _json_dumps(decided_result_ids),
                    report_path,
                    created_at,
                ),
            )
        return CapabilityActivationFollowupResultDecision(
            id=decision_id,
            status=status,
            operator_id=operator_id,
            selected_action=selected_action,
            selection_note=selection_note,
            evidence_reference=evidence_reference,
            result_record_count=result_record_count,
            decision_count=decision_count,
            accepted_keep_blocked_decision_count=accepted_keep_blocked_decision_count,
            more_evidence_decision_count=more_evidence_decision_count,
            deferred_decision_count=deferred_decision_count,
            existing_decision_count=existing_decision_count,
            created_approval_request_count=created_approval_request_count,
            activation_action_count=activation_action_count,
            decided_result_ids=decided_result_ids,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_capability_activation_followup_result_decisions(
        self,
        limit: int | None = 5,
    ) -> list[CapabilityActivationFollowupResultDecision]:
        with self._connect() as connection:
            if limit is None:
                rows = connection.execute(
                    """
                    select * from capability_activation_followup_result_decisions
                    order by created_at desc, id desc
                    """
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    select * from capability_activation_followup_result_decisions
                    order by created_at desc, id desc
                    limit ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            self._row_to_capability_activation_followup_result_decision(row)
            for row in rows
        ]

    def get_real_cost_tracking_proof_checklist(
        self,
        checklist_id: str | None,
    ) -> RealCostTrackingProofChecklist | None:
        if checklist_id is None:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from real_cost_tracking_proof_checklists
                where id = ?
                """,
                (checklist_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_real_cost_tracking_proof_checklist(row)

    def record_incident(
        self,
        *,
        incident_id: str | None = None,
        project_id: str,
        run_id: str,
        goal_id: str | None,
        task_id: str | None,
        task_type: str,
        incident_type: str,
        severity: str,
        status: str,
        summary: str,
        failure_class: str,
        verification_method: str | None,
        verification_path: str | None,
        failed_checks: list[str],
        evidence: dict[str, Any],
        artifacts: list[str],
        evidence_path: str | None,
    ) -> str:
        incident_id = incident_id or new_id("incident")
        with self._connect() as connection:
            connection.execute(
                """
                insert into incidents (
                    id, project_id, run_id, goal_id, task_id, task_type,
                    incident_type, severity, status, summary, failure_class,
                    verification_method, verification_path, failed_checks,
                    evidence, artifacts, evidence_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    project_id,
                    run_id,
                    goal_id,
                    task_id,
                    task_type,
                    incident_type,
                    severity,
                    status,
                    summary,
                    failure_class,
                    verification_method,
                    verification_path,
                    _json_dumps(failed_checks),
                    _json_dumps(evidence),
                    _json_dumps(artifacts),
                    evidence_path,
                    utc_now(),
                ),
            )
        return incident_id

    def list_recent_incidents(self, limit: int = 5) -> list[Incident]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from incidents
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_incident(row) for row in rows]

    def list_incidents_for_run(self, run_id: str) -> list[Incident]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from incidents
                where run_id = ?
                order by created_at desc, id desc
                """,
                (run_id,),
            ).fetchall()
        return [self._row_to_incident(row) for row in rows]

    def get_incident(self, incident_id: str) -> Incident:
        with self._connect() as connection:
            row = connection.execute(
                "select * from incidents where id = ?",
                (incident_id,),
            ).fetchone()
            if row is None:
                raise KeyError(incident_id)
            return self._row_to_incident(row)

    def resolve_incident(
        self,
        incident_id: str,
        *,
        resolved_by: str,
        resolution_note: str,
        resolution_evidence_path: str,
        resolved_at: str | None = None,
    ) -> Incident:
        resolved_at = resolved_at or utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "select * from incidents where id = ?",
                (incident_id,),
            ).fetchone()
            if row is None:
                raise KeyError(incident_id)
            if row["status"] == "resolved":
                return self._row_to_incident(row)

            connection.execute(
                """
                update incidents
                set status = 'resolved',
                    resolved_at = ?,
                    resolved_by = ?,
                    resolution_note = ?,
                    resolution_evidence_path = ?
                where id = ?
                """,
                (
                    resolved_at,
                    resolved_by,
                    resolution_note,
                    resolution_evidence_path,
                    incident_id,
                ),
            )
            updated = connection.execute(
                "select * from incidents where id = ?",
                (incident_id,),
            ).fetchone()
            if updated is None:
                raise KeyError(incident_id)
            return self._row_to_incident(updated)

    def list_pending_approvals(self) -> list[ApprovalRequest]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from approval_requests
                where status = 'pending'
                order by requested_at asc, id asc
                """
            ).fetchall()
        return [self._row_to_approval_request(row) for row in rows]

    def list_recent_approval_requests(self, limit: int = 5) -> list[ApprovalRequest]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from approval_requests
                order by requested_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_approval_request(row) for row in rows]

    def list_approval_requests_for_run(self, run_id: str) -> list[ApprovalRequest]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from approval_requests
                where run_id = ?
                order by requested_at desc, id desc
                """,
                (run_id,),
            ).fetchall()
        return [self._row_to_approval_request(row) for row in rows]

    def list_approval_requests_for_goal(self, goal_id: str) -> list[ApprovalRequest]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from approval_requests
                where goal_id = ?
                order by requested_at desc, id desc
                """,
                (goal_id,),
            ).fetchall()
        return [self._row_to_approval_request(row) for row in rows]

    def count_approval_requests(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "select count(*) as count from approval_requests"
            ).fetchone()
        if row is None:
            return 0
        return int(row["count"])

    def get_approval_request(self, approval_id: str) -> ApprovalRequest:
        with self._connect() as connection:
            row = connection.execute(
                "select * from approval_requests where id = ?",
                (approval_id,),
            ).fetchone()
            if row is None:
                raise KeyError(approval_id)
            return self._row_to_approval_request(row)

    def approve_approval_request(
        self,
        approval_id: str,
        *,
        decided_by: str,
        decision_note: str,
    ) -> ApprovalRequest:
        decided_at = utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "select * from approval_requests where id = ?",
                (approval_id,),
            ).fetchone()
            if row is None:
                raise KeyError(approval_id)
            if row["status"] != "pending":
                return self._row_to_approval_request(row)

            connection.execute(
                """
                update approval_requests
                set status = 'approved', decided_by = ?, decision_note = ?, decided_at = ?
                where id = ? and status = 'pending'
                """,
                (decided_by, decision_note, decided_at, approval_id),
            )
            connection.execute(
                """
                update tasks
                set status = 'pending', updated_at = ?
                where id = ? and status = ?
                """,
                (decided_at, row["task_id"], APPROVAL_WAITING_STATUS),
            )
            updated = connection.execute(
                "select * from approval_requests where id = ?",
                (approval_id,),
            ).fetchone()
            if updated is None:
                raise KeyError(approval_id)
            return self._row_to_approval_request(updated)

    def upsert_registered_project(
        self,
        *,
        name: str,
        root_path: str,
        default_test_command: str,
        allowed_write_roots: list[str],
    ) -> RegisteredProject:
        now = utc_now()
        existing = self.get_registered_project(name)
        created_at = existing.created_at if existing else now
        with self._connect() as connection:
            connection.execute(
                """
                insert into registered_projects (
                    name, root_path, default_test_command, allowed_write_roots,
                    created_at, updated_at
                )
                values (?, ?, ?, ?, ?, ?)
                on conflict(name) do update set
                    root_path = excluded.root_path,
                    default_test_command = excluded.default_test_command,
                    allowed_write_roots = excluded.allowed_write_roots,
                    updated_at = excluded.updated_at
                """,
                (
                    name,
                    root_path,
                    default_test_command,
                    _json_dumps(allowed_write_roots),
                    created_at,
                    now,
                ),
            )
        return RegisteredProject(
            name=name,
            root_path=root_path,
            default_test_command=default_test_command,
            allowed_write_roots=allowed_write_roots,
            created_at=created_at,
            updated_at=now,
        )

    def get_registered_project(self, name: str) -> RegisteredProject | None:
        with self._connect() as connection:
            row = connection.execute(
                "select * from registered_projects where name = ?",
                (name,),
            ).fetchone()
        return self._row_to_registered_project(row) if row is not None else None

    def list_registered_projects(self) -> list[RegisteredProject]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from registered_projects
                order by name asc
                """
            ).fetchall()
        return [self._row_to_registered_project(row) for row in rows]

    def record_worktree(
        self,
        *,
        project_id: str,
        task_id: str,
        run_id: str,
        base_commit: str,
        branch_name: str,
        worktree_path: str,
    ) -> WorktreeRecord:
        worktree_id = new_id("worktree")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into worktree_records (
                    id, project_id, task_id, run_id, base_commit,
                    branch_name, worktree_path, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    worktree_id,
                    project_id,
                    task_id,
                    run_id,
                    base_commit,
                    branch_name,
                    worktree_path,
                    created_at,
                ),
            )
        return WorktreeRecord(
            id=worktree_id,
            project_id=project_id,
            task_id=task_id,
            run_id=run_id,
            base_commit=base_commit,
            branch_name=branch_name,
            worktree_path=worktree_path,
            created_at=created_at,
        )

    def list_recent_worktree_records(self, limit: int = 5) -> list[WorktreeRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from worktree_records
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_worktree_record(row) for row in rows]

    def record_worktree_cleanup(
        self,
        *,
        worktree_id: str,
        effect_id: str,
        project_id: str,
        run_id: str,
        task_id: str,
        worktree_path: str,
        branch_name: str,
        cleanup_reason: str,
        status: str,
        decided_by: str,
        decision_note: str,
        evidence_path: str,
        result_json: dict[str, Any],
    ) -> WorktreeCleanupRecord:
        cleanup_id = new_id("worktree_cleanup")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into worktree_cleanup_records (
                    id, worktree_id, effect_id, project_id, run_id, task_id,
                    worktree_path, branch_name, cleanup_reason, status,
                    decided_by, decision_note, evidence_path, result_json,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cleanup_id,
                    worktree_id,
                    effect_id,
                    project_id,
                    run_id,
                    task_id,
                    worktree_path,
                    branch_name,
                    cleanup_reason,
                    status,
                    decided_by,
                    decision_note,
                    evidence_path,
                    _json_dumps(result_json),
                    created_at,
                ),
            )
        return WorktreeCleanupRecord(
            id=cleanup_id,
            worktree_id=worktree_id,
            effect_id=effect_id,
            project_id=project_id,
            run_id=run_id,
            task_id=task_id,
            worktree_path=worktree_path,
            branch_name=branch_name,
            cleanup_reason=cleanup_reason,
            status=status,
            decided_by=decided_by,
            decision_note=decision_note,
            evidence_path=evidence_path,
            result_json=result_json,
            created_at=created_at,
        )

    def get_removed_worktree_cleanup_for_effect(
        self,
        effect_id: str,
    ) -> WorktreeCleanupRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from worktree_cleanup_records
                where effect_id = ? and status = 'removed'
                order by created_at desc, id desc
                limit 1
                """,
                (effect_id,),
            ).fetchone()
        return self._row_to_worktree_cleanup_record(row) if row else None

    def list_recent_worktree_cleanup_records(
        self,
        limit: int = 5,
    ) -> list[WorktreeCleanupRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from worktree_cleanup_records
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_worktree_cleanup_record(row) for row in rows]

    def record_github_handoff(
        self,
        *,
        effect_id: str,
        project_id: str,
        run_id: str,
        task_id: str,
        branch_name: str,
        commit_sha: str,
        remote_name: str,
        remote_url: str,
        base_branch: str,
        status: str,
        push_command: str,
        draft_pr_command: str,
        evidence_path: str,
        result_json: dict[str, Any],
    ) -> GitHubHandoffRecord:
        handoff_id = new_id("github_handoff")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into github_handoff_records (
                    id, effect_id, project_id, run_id, task_id, branch_name,
                    commit_sha, remote_name, remote_url, base_branch, status,
                    push_command, draft_pr_command, evidence_path, result_json,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    handoff_id,
                    effect_id,
                    project_id,
                    run_id,
                    task_id,
                    branch_name,
                    commit_sha,
                    remote_name,
                    remote_url,
                    base_branch,
                    status,
                    push_command,
                    draft_pr_command,
                    evidence_path,
                    _json_dumps(result_json),
                    created_at,
                ),
            )
        return GitHubHandoffRecord(
            id=handoff_id,
            effect_id=effect_id,
            project_id=project_id,
            run_id=run_id,
            task_id=task_id,
            branch_name=branch_name,
            commit_sha=commit_sha,
            remote_name=remote_name,
            remote_url=remote_url,
            base_branch=base_branch,
            status=status,
            push_command=push_command,
            draft_pr_command=draft_pr_command,
            evidence_path=evidence_path,
            result_json=result_json,
            created_at=created_at,
        )

    def get_github_handoff_for_effect(
        self,
        effect_id: str,
    ) -> GitHubHandoffRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from github_handoff_records
                where effect_id = ?
                order by created_at desc, id desc
                limit 1
                """,
                (effect_id,),
            ).fetchone()
        return self._row_to_github_handoff_record(row) if row else None

    def list_recent_github_handoff_records(
        self,
        limit: int = 5,
    ) -> list[GitHubHandoffRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from github_handoff_records
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_github_handoff_record(row) for row in rows]

    def get_github_handoff(
        self,
        handoff_id: str,
    ) -> GitHubHandoffRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "select * from github_handoff_records where id = ?",
                (handoff_id,),
            ).fetchone()
        return self._row_to_github_handoff_record(row) if row else None

    def record_ci_deploy_evidence(
        self,
        *,
        github_handoff_id: str,
        effect_id: str,
        project_id: str,
        run_id: str,
        task_id: str,
        branch_name: str,
        commit_sha: str,
        provider: str,
        external_run_id: str,
        external_url: str,
        status: str,
        recorded_by: str,
        evidence_path: str,
        result_json: dict[str, Any],
        idempotency_key: str,
    ) -> CiDeployEvidenceRecord:
        record_id = new_id("ci_deploy_evidence")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into ci_deploy_evidence_records (
                    id, github_handoff_id, effect_id, project_id, run_id,
                    task_id, branch_name, commit_sha, provider, external_run_id,
                    external_url, status, recorded_by, evidence_path,
                    result_json, idempotency_key, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    github_handoff_id,
                    effect_id,
                    project_id,
                    run_id,
                    task_id,
                    branch_name,
                    commit_sha,
                    provider,
                    external_run_id,
                    external_url,
                    status,
                    recorded_by,
                    evidence_path,
                    _json_dumps(result_json),
                    idempotency_key,
                    created_at,
                ),
            )
        return CiDeployEvidenceRecord(
            id=record_id,
            github_handoff_id=github_handoff_id,
            effect_id=effect_id,
            project_id=project_id,
            run_id=run_id,
            task_id=task_id,
            branch_name=branch_name,
            commit_sha=commit_sha,
            provider=provider,
            external_run_id=external_run_id,
            external_url=external_url,
            status=status,
            recorded_by=recorded_by,
            evidence_path=evidence_path,
            result_json=result_json,
            idempotency_key=idempotency_key,
            created_at=created_at,
        )

    def get_ci_deploy_evidence_by_idempotency_key(
        self,
        idempotency_key: str,
    ) -> CiDeployEvidenceRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select * from ci_deploy_evidence_records
                where idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
        return self._row_to_ci_deploy_evidence_record(row) if row else None

    def list_recent_ci_deploy_evidence_records(
        self,
        limit: int | None = 5,
    ) -> list[CiDeployEvidenceRecord]:
        with self._connect() as connection:
            query = """
                select * from ci_deploy_evidence_records
                order by created_at desc, id desc
            """
            if limit is None:
                rows = connection.execute(query).fetchall()
            else:
                rows = connection.execute(query + " limit ?", (limit,)).fetchall()
        return [self._row_to_ci_deploy_evidence_record(row) for row in rows]

    def upsert_profile(
        self,
        *,
        name: str,
        label: str,
        model: str,
        cost_tier: str,
        mode: str,
        tools_json: list[str],
        permissions_json: dict[str, Any],
        use_for_json: list[str],
        max_budget_json: dict[str, Any],
        enabled: bool = True,
    ) -> AgentProfile:
        now = utc_now()
        profile_id = new_id("profile")
        with self._connect() as connection:
            row = connection.execute(
                "select id, created_at from profiles where name = ?",
                (name,),
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    insert into profiles (
                        id, name, label, model, cost_tier, mode, tools_json,
                        permissions_json, use_for_json, max_budget_json,
                        enabled, created_at, updated_at
                    )
                    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        profile_id,
                        name,
                        label,
                        model,
                        cost_tier,
                        mode,
                        _json_dumps(tools_json),
                        _json_dumps(permissions_json),
                        _json_dumps(use_for_json),
                        _json_dumps(max_budget_json),
                        1 if enabled else 0,
                        now,
                        now,
                    ),
                )
            else:
                profile_id = row["id"]
                connection.execute(
                    """
                    update profiles
                    set label = ?, model = ?, cost_tier = ?, mode = ?,
                        tools_json = ?, permissions_json = ?, use_for_json = ?,
                        max_budget_json = ?, enabled = ?, updated_at = ?
                    where name = ?
                    """,
                    (
                        label,
                        model,
                        cost_tier,
                        mode,
                        _json_dumps(tools_json),
                        _json_dumps(permissions_json),
                        _json_dumps(use_for_json),
                        _json_dumps(max_budget_json),
                        1 if enabled else 0,
                        now,
                        name,
                    ),
                )
        profile = self.get_profile(name)
        if profile is None:
            raise KeyError(name)
        return profile

    def list_profiles(self, *, enabled_only: bool = True) -> list[AgentProfile]:
        with self._connect() as connection:
            query = "select * from profiles"
            values: tuple[Any, ...] = ()
            if enabled_only:
                query += " where enabled = ?"
                values = (1,)
            query += " order by name asc"
            rows = connection.execute(query, values).fetchall()
        return [self._row_to_profile(row) for row in rows]

    def get_profile(self, name: str) -> AgentProfile | None:
        with self._connect() as connection:
            row = connection.execute(
                "select * from profiles where name = ?",
                (name,),
            ).fetchone()
        return self._row_to_profile(row) if row else None

    def upsert_routing_rule(
        self,
        *,
        category: str,
        preferred_profile: str,
        fallback_profile: str,
        confidence_threshold: float | None = None,
    ) -> RoutingRule:
        now = utc_now()
        rule_id = new_id("routing_rule")
        with self._connect() as connection:
            row = connection.execute(
                "select id from routing_rules where category = ?",
                (category,),
            ).fetchone()
            if row is None:
                connection.execute(
                    """
                    insert into routing_rules (
                        id, category, preferred_profile, fallback_profile,
                        confidence_threshold, created_at, updated_at
                    )
                    values (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        rule_id,
                        category,
                        preferred_profile,
                        fallback_profile,
                        confidence_threshold,
                        now,
                        now,
                    ),
                )
            else:
                rule_id = row["id"]
                connection.execute(
                    """
                    update routing_rules
                    set preferred_profile = ?, fallback_profile = ?,
                        confidence_threshold = ?, updated_at = ?
                    where category = ?
                    """,
                    (
                        preferred_profile,
                        fallback_profile,
                        confidence_threshold,
                        now,
                        category,
                    ),
                )
        rule = self.get_routing_rule(category)
        if rule is None:
            raise KeyError(category)
        return rule

    def get_routing_rule(self, category: str) -> RoutingRule | None:
        with self._connect() as connection:
            row = connection.execute(
                "select * from routing_rules where category = ?",
                (category,),
            ).fetchone()
        return self._row_to_routing_rule(row) if row else None

    def list_routing_rules(self) -> list[RoutingRule]:
        with self._connect() as connection:
            rows = connection.execute(
                "select * from routing_rules order by category asc",
            ).fetchall()
        return [self._row_to_routing_rule(row) for row in rows]

    def record_routing_decision(
        self,
        *,
        task_id: str | None,
        goal_id: str | None,
        project_id: str | None,
        selected_profile: str,
        selected_model: str,
        category: str,
        reason: str,
        estimated_cost_tier: str,
        actual_cost: float | None = None,
        status: str = "selected",
    ) -> RoutingDecision:
        decision_id = new_id("routing_decision")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into routing_decisions (
                    id, task_id, goal_id, project_id, selected_profile,
                    selected_model, category, reason, estimated_cost_tier,
                    actual_cost, status, created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    task_id,
                    goal_id,
                    project_id,
                    selected_profile,
                    selected_model,
                    category,
                    reason,
                    estimated_cost_tier,
                    actual_cost,
                    status,
                    created_at,
                ),
            )
        return RoutingDecision(
            id=decision_id,
            task_id=task_id,
            goal_id=goal_id,
            project_id=project_id,
            selected_profile=selected_profile,
            selected_model=selected_model,
            category=category,
            reason=reason,
            estimated_cost_tier=estimated_cost_tier,
            actual_cost=actual_cost,
            status=status,
            created_at=created_at,
        )

    def list_recent_routing_decisions(
        self,
        limit: int | None = 5,
    ) -> list[RoutingDecision]:
        with self._connect() as connection:
            query = """
                select * from routing_decisions
                order by created_at desc, id desc
            """
            if limit is None:
                rows = connection.execute(query).fetchall()
            else:
                rows = connection.execute(query + " limit ?", (limit,)).fetchall()
        return [self._row_to_routing_decision(row) for row in rows]

    def record_subagent_delegation(
        self,
        *,
        routing_decision_id: str | None,
        parent_goal_id: str,
        parent_task_id: str,
        assigned_profile: str,
        category: str,
        title: str,
        prompt: str,
        input_context_json: dict[str, Any],
        allowed_tools_json: list[str],
        forbidden_actions_json: list[str],
        expected_output_schema: str,
        budget_json: dict[str, Any],
        status: str,
        result_summary: str | None,
        result_artifact_path: str,
        started_at: str | None = None,
        completed_at: str | None = None,
    ) -> SubagentDelegation:
        delegation_id = new_id("subagent_delegation")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into subagent_delegations (
                    id, routing_decision_id, parent_goal_id, parent_task_id,
                    assigned_profile, category, title, prompt,
                    input_context_json, allowed_tools_json,
                    forbidden_actions_json, expected_output_schema,
                    budget_json, status, result_summary, result_artifact_path,
                    created_at, started_at, completed_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    delegation_id,
                    routing_decision_id,
                    parent_goal_id,
                    parent_task_id,
                    assigned_profile,
                    category,
                    title,
                    prompt,
                    _json_dumps(input_context_json),
                    _json_dumps(allowed_tools_json),
                    _json_dumps(forbidden_actions_json),
                    expected_output_schema,
                    _json_dumps(budget_json),
                    status,
                    result_summary,
                    result_artifact_path,
                    created_at,
                    started_at,
                    completed_at,
                ),
            )
        return SubagentDelegation(
            id=delegation_id,
            routing_decision_id=routing_decision_id,
            parent_goal_id=parent_goal_id,
            parent_task_id=parent_task_id,
            assigned_profile=assigned_profile,
            category=category,
            title=title,
            prompt=prompt,
            input_context_json=input_context_json,
            allowed_tools_json=allowed_tools_json,
            forbidden_actions_json=forbidden_actions_json,
            expected_output_schema=expected_output_schema,
            budget_json=budget_json,
            status=status,
            result_summary=result_summary,
            result_artifact_path=result_artifact_path,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
        )

    def list_subagent_delegations(
        self,
        goal_id: str,
    ) -> list[SubagentDelegation]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from subagent_delegations
                where parent_goal_id = ?
                order by created_at desc, id desc
                """,
                (goal_id,),
            ).fetchall()
        return [self._row_to_subagent_delegation(row) for row in rows]

    def list_recent_subagent_delegations(
        self,
        limit: int | None = 5,
    ) -> list[SubagentDelegation]:
        with self._connect() as connection:
            query = """
                select * from subagent_delegations
                order by created_at desc, id desc
            """
            if limit is None:
                rows = connection.execute(query).fetchall()
            else:
                rows = connection.execute(query + " limit ?", (limit,)).fetchall()
        return [self._row_to_subagent_delegation(row) for row in rows]

    def get_subagent_delegation(
        self,
        delegation_id: str,
    ) -> SubagentDelegation | None:
        with self._connect() as connection:
            row = connection.execute(
                "select * from subagent_delegations where id = ?",
                (delegation_id,),
            ).fetchone()
        return self._row_to_subagent_delegation(row) if row else None

    def complete_subagent_delegation(
        self,
        delegation_id: str,
        *,
        result_summary: str,
        result_artifact_path: str,
        completed_at: str | None = None,
    ) -> SubagentDelegation:
        completed_at = completed_at or utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "select * from subagent_delegations where id = ?",
                (delegation_id,),
            ).fetchone()
            if row is None:
                raise KeyError(delegation_id)
            if row["status"] == "completed":
                raise ValueError(f"delegation {delegation_id} is already completed")
            if row["status"] != "pending":
                raise ValueError(
                    f"delegation {delegation_id} is not pending: {row['status']}"
                )
            started_at = row["started_at"]
            connection.execute(
                """
                update subagent_delegations
                set status = ?,
                    result_summary = ?,
                    result_artifact_path = ?,
                    started_at = ?,
                    completed_at = ?
                where id = ?
                """,
                (
                    "completed",
                    result_summary,
                    result_artifact_path,
                    started_at,
                    completed_at,
                    delegation_id,
                ),
            )
            updated = connection.execute(
                "select * from subagent_delegations where id = ?",
                (delegation_id,),
            ).fetchone()
        return self._row_to_subagent_delegation(updated)

    def create_pending_approval_request_for_task(
        self,
        task_id: str,
        *,
        reason: str,
    ) -> ApprovalRequest:
        now = utc_now()
        with self._connect() as connection:
            row = connection.execute(
                "select * from tasks where id = ?",
                (task_id,),
            ).fetchone()
            if row is None:
                raise KeyError(task_id)
            task = self._row_to_task(row)
            approval_id = self._ensure_pending_approval_request(connection, task)
            connection.execute(
                """
                update approval_requests
                set reason = ?
                where id = ? and status = 'pending'
                """,
                (reason, approval_id),
            )
            connection.execute(
                """
                update tasks
                set status = ?, updated_at = ?
                where id = ?
                """,
                (APPROVAL_WAITING_STATUS, now, task_id),
            )
            approval_row = connection.execute(
                "select * from approval_requests where id = ?",
                (approval_id,),
            ).fetchone()
            if approval_row is None:
                raise KeyError(approval_id)
            return self._row_to_approval_request(approval_row)

    def record_effect(
        self,
        *,
        run_id: str,
        task_id: str,
        project_id: str,
        capability: str,
        effect_type: str,
        idempotency_key: str,
        target: str,
        proposed_payload: dict[str, Any],
        status: str,
        required_approval_id: str | None,
        attempted_at: str | None,
        committed_at: str | None,
        evidence_path: str,
        compensation_plan: dict[str, Any],
        result_json: dict[str, Any] | None = None,
    ) -> Effect:
        effect_id = new_id("effect")
        now = utc_now()
        result_payload = result_json or {}
        with self._connect() as connection:
            connection.execute(
                """
                insert into effects (
                    id, run_id, task_id, project_id, capability, effect_type,
                    idempotency_key, target, proposed_payload_json, status,
                    required_approval_id, attempted_at, committed_at,
                    evidence_path, compensation_plan_json, result_json,
                    created_at, updated_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    effect_id,
                    run_id,
                    task_id,
                    project_id,
                    capability,
                    effect_type,
                    idempotency_key,
                    target,
                    _json_dumps(proposed_payload),
                    status,
                    required_approval_id,
                    attempted_at,
                    committed_at,
                    evidence_path,
                    _json_dumps(compensation_plan),
                    _json_dumps(result_payload),
                    now,
                    now,
                ),
            )
        return Effect(
            id=effect_id,
            run_id=run_id,
            task_id=task_id,
            project_id=project_id,
            capability=capability,
            effect_type=effect_type,
            idempotency_key=idempotency_key,
            target=target,
            proposed_payload=proposed_payload,
            status=status,
            required_approval_id=required_approval_id,
            attempted_at=attempted_at,
            committed_at=committed_at,
            evidence_path=evidence_path,
            compensation_plan=compensation_plan,
            result_json=result_payload,
            created_at=now,
            updated_at=now,
        )

    def get_effect_for_approval(self, approval_id: str) -> Effect:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from effects
                where required_approval_id = ?
                order by created_at desc, id desc
                """,
                (approval_id,),
            ).fetchall()
        if not rows:
            raise KeyError(approval_id)
        if len(rows) > 1:
            raise ValueError(f"multiple effects found for approval: {approval_id}")
        return self._row_to_effect(rows[0])

    def get_effect(self, effect_id: str) -> Effect:
        with self._connect() as connection:
            row = connection.execute(
                "select * from effects where id = ?",
                (effect_id,),
            ).fetchone()
        if row is None:
            raise KeyError(effect_id)
        return self._row_to_effect(row)

    def mark_effect_committed(
        self,
        effect_id: str,
        *,
        result_json: dict[str, Any],
        evidence_path: str,
        compensation_plan: dict[str, Any],
        attempted_at: str,
        committed_at: str,
    ) -> Effect:
        with self._connect() as connection:
            connection.execute(
                """
                update effects
                set status = 'committed',
                    attempted_at = ?,
                    committed_at = ?,
                    evidence_path = ?,
                    compensation_plan_json = ?,
                    result_json = ?,
                    updated_at = ?
                where id = ?
                """,
                (
                    attempted_at,
                    committed_at,
                    evidence_path,
                    _json_dumps(compensation_plan),
                    _json_dumps(result_json),
                    utc_now(),
                    effect_id,
                ),
            )
            row = connection.execute(
                "select * from effects where id = ?",
                (effect_id,),
            ).fetchone()
            if row is None:
                raise KeyError(effect_id)
            return self._row_to_effect(row)

    def mark_effect_blocked(
        self,
        effect_id: str,
        *,
        result_json: dict[str, Any],
        evidence_path: str,
        attempted_at: str,
    ) -> Effect:
        with self._connect() as connection:
            connection.execute(
                """
                update effects
                set status = 'blocked',
                    attempted_at = ?,
                    evidence_path = ?,
                    result_json = ?,
                    updated_at = ?
                where id = ?
                """,
                (attempted_at, evidence_path, _json_dumps(result_json), utc_now(), effect_id),
            )
            row = connection.execute(
                "select * from effects where id = ?",
                (effect_id,),
            ).fetchone()
            if row is None:
                raise KeyError(effect_id)
            return self._row_to_effect(row)

    def mark_effect_applied(
        self,
        effect_id: str,
        *,
        result_json: dict[str, Any],
        evidence_path: str,
        compensation_plan: dict[str, Any],
        attempted_at: str,
    ) -> Effect:
        with self._connect() as connection:
            connection.execute(
                """
                update effects
                set status = 'applied',
                    attempted_at = ?,
                    committed_at = null,
                    evidence_path = ?,
                    compensation_plan_json = ?,
                    result_json = ?,
                    updated_at = ?
                where id = ?
                """,
                (
                    attempted_at,
                    evidence_path,
                    _json_dumps(compensation_plan),
                    _json_dumps(result_json),
                    utc_now(),
                    effect_id,
                ),
            )
            row = connection.execute(
                "select * from effects where id = ?",
                (effect_id,),
            ).fetchone()
            if row is None:
                raise KeyError(effect_id)
            return self._row_to_effect(row)

    def list_recent_effects(self, limit: int = 5) -> list[Effect]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from effects
                order by created_at desc, id desc
                limit ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_to_effect(row) for row in rows]

    def list_effects_for_run(self, run_id: str) -> list[Effect]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from effects
                where run_id = ?
                order by created_at desc, id desc
                """,
                (run_id,),
            ).fetchall()
        return [self._row_to_effect(row) for row in rows]

    def list_effects_with_idempotency_prefix(self, prefix: str) -> list[Effect]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from effects
                where idempotency_key like ?
                order by created_at desc, id desc
                """,
                (f"{prefix}%",),
            ).fetchall()
        return [self._row_to_effect(row) for row in rows]

    def list_stale_active_tasks(
        self,
        *,
        timeout_seconds: int,
        now: str | None = None,
    ) -> list[Task]:
        now_dt = _parse_utc(now or utc_now())
        cutoff = now_dt - timedelta(seconds=timeout_seconds)
        with self._connect() as connection:
            rows = connection.execute(
                """
                select * from tasks
                where status in ('claimed', 'running', 'verifying')
                order by updated_at asc, id asc
                """
            ).fetchall()

        stale_tasks = []
        for row in rows:
            last_activity = row["claimed_at"] or row["updated_at"] or row["created_at"]
            if _parse_utc(last_activity) <= cutoff:
                stale_tasks.append(self._row_to_task(row))
        return stale_tasks

    def list_queue_health_findings(
        self,
        *,
        blocked_threshold: int = 2,
        failed_threshold: int = 2,
    ) -> list[QueueHealthFinding]:
        thresholds = {
            "blocked": blocked_threshold,
            "failed": failed_threshold,
        }
        with self._connect() as connection:
            rows = connection.execute(
                """
                select id, project_id, task_type, status, updated_at, created_at
                from tasks
                where status in ('blocked', 'failed')
                order by created_at asc, id asc
                """
            ).fetchall()

        groups: dict[tuple[str, str, str], list[sqlite3.Row]] = {}
        for row in rows:
            key = (row["status"], row["project_id"], row["task_type"])
            groups.setdefault(key, []).append(row)

        status_order = {"blocked": 0, "failed": 1}
        findings: list[QueueHealthFinding] = []
        for (status, project_id, task_type), grouped_rows in groups.items():
            threshold = thresholds[status]
            count = len(grouped_rows)
            if count < threshold:
                continue
            latest_updated_at = max(row["updated_at"] for row in grouped_rows)
            findings.append(
                QueueHealthFinding(
                    status=status,
                    project_id=project_id,
                    task_type=task_type,
                    count=count,
                    threshold=threshold,
                    task_ids=[row["id"] for row in grouped_rows],
                    latest_updated_at=latest_updated_at,
                )
            )

        return sorted(
            findings,
            key=lambda finding: (
                status_order[finding.status],
                finding.project_id,
                finding.task_type,
            ),
        )

    def latest_run_id_for_goal(self, goal_id: str) -> str | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                select id from runs
                where goal_id = ?
                order by started_at desc, id desc
                limit 1
                """,
                (goal_id,),
            ).fetchone()
        return row["id"] if row else None

    def record_steering_review(
        self,
        *,
        review_id: str | None = None,
        goal_id: str,
        project_id: str,
        run_id: str | None,
        reviewed_plan_version: str,
        current_task_id: str | None,
        status: str,
        drift_score: str,
        findings: list[dict[str, Any]],
        recommended_next_action: str,
        requires_operator: bool,
        report_path: str,
    ) -> SteeringReview:
        review_id = review_id or new_id("steer")
        created_at = utc_now()
        with self._connect() as connection:
            connection.execute(
                """
                insert into steering_reviews (
                    id, goal_id, project_id, run_id, reviewed_plan_version,
                    current_task_id, status, drift_score, findings_json,
                    recommended_next_action, requires_operator, report_path,
                    created_at
                )
                values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    review_id,
                    goal_id,
                    project_id,
                    run_id,
                    reviewed_plan_version,
                    current_task_id,
                    status,
                    drift_score,
                    _json_dumps(findings),
                    recommended_next_action,
                    1 if requires_operator else 0,
                    report_path,
                    created_at,
                ),
            )
        return SteeringReview(
            id=review_id,
            goal_id=goal_id,
            project_id=project_id,
            run_id=run_id,
            reviewed_plan_version=reviewed_plan_version,
            current_task_id=current_task_id,
            status=status,
            drift_score=drift_score,
            findings=findings,
            recommended_next_action=recommended_next_action,
            requires_operator=requires_operator,
            report_path=report_path,
            created_at=created_at,
        )

    def list_recent_steering_reviews(
        self,
        *,
        limit: int = 5,
        goal_id: str | None = None,
        project_id: str | None = None,
        requires_operator: bool | None = None,
    ) -> list[SteeringReview]:
        clauses: list[str] = []
        values: list[Any] = []
        if goal_id is not None:
            clauses.append("goal_id = ?")
            values.append(goal_id)
        if project_id is not None:
            clauses.append("project_id = ?")
            values.append(project_id)
        if requires_operator is not None:
            clauses.append("requires_operator = ?")
            values.append(1 if requires_operator else 0)
        where = f"where {' and '.join(clauses)}" if clauses else ""
        values.append(limit)
        with self._connect() as connection:
            rows = connection.execute(
                f"""
                select * from steering_reviews
                {where}
                order by created_at desc, id desc
                limit ?
                """,
                values,
            ).fetchall()
        return [self._row_to_steering_review(row) for row in rows]

    def _ensure_column(
        self,
        connection: sqlite3.Connection,
        table_name: str,
        column_name: str,
        column_type: str,
    ) -> None:
        columns = {
            row["name"]
            for row in connection.execute(f"pragma table_info({table_name})").fetchall()
        }
        if column_name not in columns:
            try:
                connection.execute(
                    f"alter table {table_name} add column {column_name} {column_type}"
                )
            except sqlite3.OperationalError as error:
                if "duplicate column name" not in str(error).lower():
                    raise

    def _table_exists(self, connection: sqlite3.Connection, table_name: str) -> bool:
        row = connection.execute(
            "select name from sqlite_master where type = 'table' and name = ?",
            (table_name,),
        ).fetchone()
        return row is not None

    def _allow_nullable_dispatch_posture_staleness_age(
        self,
        connection: sqlite3.Connection,
    ) -> None:
        table_name = "dispatch_posture_staleness_reviews"
        columns = connection.execute(f"pragma table_info({table_name})").fetchall()
        target = next(
            (row for row in columns if row["name"] == "latest_snapshot_age_seconds"),
            None,
        )
        if target is None or target["notnull"] == 0:
            return

        legacy_table = f"{table_name}_legacy"
        connection.execute(f"alter table {table_name} rename to {legacy_table}")
        connection.execute(
            """
            create table dispatch_posture_staleness_reviews (
                id text primary key,
                status text not null,
                snapshot_count integer not null,
                stale_snapshot_count integer not null,
                latest_snapshot_age_seconds integer,
                stale_after_seconds integer not null,
                latest_task_count integer not null,
                latest_risk_counts text not null,
                latest_snapshot_at text,
                oldest_snapshot_at text,
                report_path text not null,
                created_at text not null
            )
            """
        )
        connection.execute(
            f"""
            insert into {table_name} (
                id, status, snapshot_count, stale_snapshot_count,
                latest_snapshot_age_seconds, stale_after_seconds,
                latest_task_count, latest_risk_counts, latest_snapshot_at,
                oldest_snapshot_at, report_path, created_at
            )
            select
                id, status, snapshot_count, stale_snapshot_count,
                latest_snapshot_age_seconds, stale_after_seconds,
                latest_task_count, latest_risk_counts, latest_snapshot_at,
                oldest_snapshot_at, report_path, created_at
            from {legacy_table}
            """
        )
        connection.execute(f"drop table {legacy_table}")

    def _dependencies_completed(
        self,
        connection: sqlite3.Connection,
        depends_on: list[str],
    ) -> bool:
        for dependency_id in depends_on:
            row = connection.execute(
                "select status from tasks where id = ?",
                (dependency_id,),
            ).fetchone()
            if row is None or row["status"] != "completed":
                return False
        return True

    def _approval_required(
        self,
        connection: sqlite3.Connection,
        task: Task,
    ) -> bool:
        approved = connection.execute(
            """
            select 1 from approval_requests
            where task_id = ? and status = 'approved'
            limit 1
            """,
            (task.id,),
        ).fetchone()
        if approved is not None:
            return False
        if task.risk_level not in SAFE_AUTO_RISK_LEVELS:
            return True
        return task.task_type not in SAFE_AUTO_TASK_TYPES

    def _ensure_pending_approval_request(
        self,
        connection: sqlite3.Connection,
        task: Task,
    ) -> str:
        existing = connection.execute(
            """
            select id from approval_requests
            where task_id = ? and status in ('pending', 'approved')
            order by requested_at desc, id desc
            limit 1
            """,
            (task.id,),
        ).fetchone()
        if existing is not None:
            return existing["id"]

        approval_id = new_id("approval")
        reason = (
            f"approval required before dispatch: risk_level={task.risk_level}; "
            f"task_type={task.task_type}"
        )
        connection.execute(
            """
            insert into approval_requests (
                id, task_id, run_id, goal_id, project_id, task_type, risk_level,
                status, reason, policy_name, policy_version, requested_by, requested_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                approval_id,
                task.id,
                task.run_id,
                task.goal_id,
                task.project_id,
                task.task_type,
                task.risk_level,
                "pending",
                reason,
                APPROVAL_POLICY_NAME,
                APPROVAL_POLICY_VERSION,
                "policy",
                utc_now(),
            ),
        )
        return approval_id

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _row_to_goal(self, row: sqlite3.Row) -> GoalRecord:
        return GoalRecord(
            id=row["id"],
            project_id=row["project_id"],
            description=row["description"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_run(self, row: sqlite3.Row) -> RunRecord:
        return RunRecord(
            id=row["id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            status=row["status"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            activity_path=row["activity_path"],
            summary_path=row["summary_path"],
            events_path=row["events_path"],
        )

    def _row_to_event(self, row: sqlite3.Row) -> EventRecord:
        return EventRecord(
            id=row["id"],
            run_id=row["run_id"],
            goal_id=row["goal_id"],
            task_id=row["task_id"],
            event_type=row["event_type"],
            message=row["message"],
            payload=_json_loads(row["payload"], {}),
            created_at=row["created_at"],
        )

    def _row_to_task(self, row: sqlite3.Row) -> Task:
        return Task(
            id=row["id"],
            run_id=row["run_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            task_type=row["task_type"],
            description=row["description"],
            status=row["status"],
            priority=row["priority"],
            risk_level=row["risk_level"],
            depends_on=_json_loads(row["depends_on"], []),
            skill_tags=_json_loads(row["skill_tags"], []),
            verification_plan=_json_loads(row["verification_plan"], {}),
            evidence=_json_loads(row["evidence"], {}),
            artifacts=_json_loads(row["artifacts"], []),
            owner=row["owner"],
            attempts=row["attempts"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            claimed_at=row["claimed_at"],
        )

    def _row_to_incident(self, row: sqlite3.Row) -> Incident:
        return Incident(
            id=row["id"],
            project_id=row["project_id"],
            run_id=row["run_id"],
            goal_id=row["goal_id"],
            task_id=row["task_id"],
            task_type=row["task_type"],
            incident_type=row["incident_type"],
            severity=row["severity"],
            status=row["status"],
            summary=row["summary"],
            failure_class=row["failure_class"],
            verification_method=row["verification_method"],
            verification_path=row["verification_path"],
            failed_checks=_json_loads(row["failed_checks"], []),
            evidence=_json_loads(row["evidence"], {}),
            artifacts=_json_loads(row["artifacts"], []),
            evidence_path=row["evidence_path"],
            created_at=row["created_at"],
            resolved_at=row["resolved_at"],
            resolved_by=row["resolved_by"],
            resolution_note=row["resolution_note"],
            resolution_evidence_path=row["resolution_evidence_path"],
        )

    def _row_to_steering_review(self, row: sqlite3.Row) -> SteeringReview:
        return SteeringReview(
            id=row["id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            run_id=row["run_id"],
            reviewed_plan_version=row["reviewed_plan_version"],
            current_task_id=row["current_task_id"],
            status=row["status"],
            drift_score=row["drift_score"],
            findings=_json_loads(row["findings_json"], []),
            recommended_next_action=row["recommended_next_action"],
            requires_operator=bool(row["requires_operator"]),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_approval_request(self, row: sqlite3.Row) -> ApprovalRequest:
        return ApprovalRequest(
            id=row["id"],
            task_id=row["task_id"],
            run_id=row["run_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            task_type=row["task_type"],
            risk_level=row["risk_level"],
            status=row["status"],
            reason=row["reason"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            requested_by=row["requested_by"],
            decided_by=row["decided_by"],
            decision_note=row["decision_note"],
            requested_at=row["requested_at"],
            decided_at=row["decided_at"],
        )

    def _row_to_registered_project(self, row: sqlite3.Row) -> RegisteredProject:
        return RegisteredProject(
            name=row["name"],
            root_path=row["root_path"],
            default_test_command=row["default_test_command"],
            allowed_write_roots=_json_loads(row["allowed_write_roots"], []),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_worktree_record(self, row: sqlite3.Row) -> WorktreeRecord:
        return WorktreeRecord(
            id=row["id"],
            project_id=row["project_id"],
            task_id=row["task_id"],
            run_id=row["run_id"],
            base_commit=row["base_commit"],
            branch_name=row["branch_name"],
            worktree_path=row["worktree_path"],
            created_at=row["created_at"],
        )

    def _row_to_worktree_cleanup_record(
        self,
        row: sqlite3.Row,
    ) -> WorktreeCleanupRecord:
        return WorktreeCleanupRecord(
            id=row["id"],
            worktree_id=row["worktree_id"],
            effect_id=row["effect_id"],
            project_id=row["project_id"],
            run_id=row["run_id"],
            task_id=row["task_id"],
            worktree_path=row["worktree_path"],
            branch_name=row["branch_name"],
            cleanup_reason=row["cleanup_reason"],
            status=row["status"],
            decided_by=row["decided_by"],
            decision_note=row["decision_note"],
            evidence_path=row["evidence_path"],
            result_json=_json_loads(row["result_json"], {}),
            created_at=row["created_at"],
        )

    def _row_to_github_handoff_record(
        self,
        row: sqlite3.Row,
    ) -> GitHubHandoffRecord:
        return GitHubHandoffRecord(
            id=row["id"],
            effect_id=row["effect_id"],
            project_id=row["project_id"],
            run_id=row["run_id"],
            task_id=row["task_id"],
            branch_name=row["branch_name"],
            commit_sha=row["commit_sha"],
            remote_name=row["remote_name"],
            remote_url=row["remote_url"],
            base_branch=row["base_branch"],
            status=row["status"],
            push_command=row["push_command"],
            draft_pr_command=row["draft_pr_command"],
            evidence_path=row["evidence_path"],
            result_json=_json_loads(row["result_json"], {}),
            created_at=row["created_at"],
        )

    def _row_to_ci_deploy_evidence_record(
        self,
        row: sqlite3.Row,
    ) -> CiDeployEvidenceRecord:
        return CiDeployEvidenceRecord(
            id=row["id"],
            github_handoff_id=row["github_handoff_id"],
            effect_id=row["effect_id"],
            project_id=row["project_id"],
            run_id=row["run_id"],
            task_id=row["task_id"],
            branch_name=row["branch_name"],
            commit_sha=row["commit_sha"],
            provider=row["provider"],
            external_run_id=row["external_run_id"],
            external_url=row["external_url"],
            status=row["status"],
            recorded_by=row["recorded_by"],
            evidence_path=row["evidence_path"],
            result_json=_json_loads(row["result_json"], {}),
            idempotency_key=row["idempotency_key"],
            created_at=row["created_at"],
        )

    def _row_to_profile(self, row: sqlite3.Row) -> AgentProfile:
        return AgentProfile(
            id=row["id"],
            name=row["name"],
            label=row["label"],
            model=row["model"],
            cost_tier=row["cost_tier"],
            mode=row["mode"],
            tools_json=_json_loads(row["tools_json"], []),
            permissions_json=_json_loads(row["permissions_json"], {}),
            use_for_json=_json_loads(row["use_for_json"], []),
            max_budget_json=_json_loads(row["max_budget_json"], {}),
            enabled=bool(row["enabled"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_routing_rule(self, row: sqlite3.Row) -> RoutingRule:
        return RoutingRule(
            id=row["id"],
            category=row["category"],
            preferred_profile=row["preferred_profile"],
            fallback_profile=row["fallback_profile"],
            confidence_threshold=row["confidence_threshold"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_routing_decision(self, row: sqlite3.Row) -> RoutingDecision:
        return RoutingDecision(
            id=row["id"],
            task_id=row["task_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            selected_profile=row["selected_profile"],
            selected_model=row["selected_model"],
            category=row["category"],
            reason=row["reason"],
            estimated_cost_tier=row["estimated_cost_tier"],
            actual_cost=row["actual_cost"],
            status=row["status"],
            created_at=row["created_at"],
        )

    def _row_to_subagent_delegation(self, row: sqlite3.Row) -> SubagentDelegation:
        return SubagentDelegation(
            id=row["id"],
            routing_decision_id=row["routing_decision_id"],
            parent_goal_id=row["parent_goal_id"],
            parent_task_id=row["parent_task_id"],
            assigned_profile=row["assigned_profile"],
            category=row["category"],
            title=row["title"],
            prompt=row["prompt"],
            input_context_json=_json_loads(row["input_context_json"], {}),
            allowed_tools_json=_json_loads(row["allowed_tools_json"], []),
            forbidden_actions_json=_json_loads(row["forbidden_actions_json"], []),
            expected_output_schema=row["expected_output_schema"],
            budget_json=_json_loads(row["budget_json"], {}),
            status=row["status"],
            result_summary=row["result_summary"],
            result_artifact_path=row["result_artifact_path"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
        )

    def _row_to_effect(self, row: sqlite3.Row) -> Effect:
        return Effect(
            id=row["id"],
            run_id=row["run_id"],
            task_id=row["task_id"],
            project_id=row["project_id"],
            capability=row["capability"],
            effect_type=row["effect_type"],
            idempotency_key=row["idempotency_key"],
            target=row["target"],
            proposed_payload=_json_loads(row["proposed_payload_json"], {}),
            status=row["status"],
            required_approval_id=row["required_approval_id"],
            attempted_at=row["attempted_at"],
            committed_at=row["committed_at"],
            evidence_path=row["evidence_path"],
            compensation_plan=_json_loads(row["compensation_plan_json"], {}),
            result_json=_json_loads(row["result_json"], {}),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_iteration_packet(self, row: sqlite3.Row) -> IterationPacket:
        return IterationPacket(
            id=row["id"],
            focus=row["focus"],
            source_path=row["source_path"],
            source_section=row["source_section"],
            status=row["status"],
            packet_path=row["packet_path"],
            verification_commands=_json_loads(row["verification_commands"], []),
            selection_policy=row["selection_policy"],
            selection_reason=row["selection_reason"],
            selected_score=row["selected_score"],
            selected_complexity=row["selected_complexity"],
            created_at=row["created_at"],
        )

    def _row_to_eval_run(self, row: sqlite3.Row) -> EvalRun:
        return EvalRun(
            id=row["id"],
            name=row["name"],
            status=row["status"],
            details=_json_loads(row["details"], {}),
            created_at=row["created_at"],
        )

    def _row_to_learning(self, row: sqlite3.Row) -> Learning:
        return Learning(
            id=row["id"],
            run_id=row["run_id"],
            project_id=row["project_id"],
            summary=row["summary"],
            source=row["source"],
            created_at=row["created_at"],
        )

    def _row_to_memory_entry(self, row: sqlite3.Row) -> MemoryEntry:
        return MemoryEntry(
            id=row["id"],
            project_id=row["project_id"],
            scope=row["scope"],
            key=row["key"],
            value=row["value"],
            source_type=row["source_type"],
            source_id=row["source_id"],
            confidence=row["confidence"],
            status=row["status"],
            created_by_profile=row["created_by_profile"],
            artifact_path=row["artifact_path"],
            approved_by=row["approved_by"],
            approved_at=row["approved_at"],
            archived_by=row["archived_by"],
            archived_at=row["archived_at"],
            archive_reason=row["archive_reason"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_used_at=row["last_used_at"],
        )

    def _row_to_skill(self, row: sqlite3.Row) -> SkillRecord:
        return SkillRecord(
            id=row["id"],
            project_id=row["project_id"],
            name=row["name"],
            description=row["description"],
            path=row["path"],
            status=row["status"],
            created_by_profile=row["created_by_profile"],
            source_run_id=row["source_run_id"],
            source_task_id=row["source_task_id"],
            verification_status=row["verification_status"],
            approved_by=row["approved_by"],
            approved_at=row["approved_at"],
            archived_by=row["archived_by"],
            archived_at=row["archived_at"],
            archive_reason=row["archive_reason"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            last_used_at=row["last_used_at"],
        )

    def _row_to_skill_version(self, row: sqlite3.Row) -> SkillVersion:
        return SkillVersion(
            id=row["id"],
            skill_id=row["skill_id"],
            version=row["version"],
            content_hash=row["content_hash"],
            path=row["path"],
            change_summary=row["change_summary"],
            verification_status=row["verification_status"],
            created_at=row["created_at"],
        )

    def _row_to_eval_candidate(self, row: sqlite3.Row) -> EvalCandidate:
        return EvalCandidate(
            id=row["id"],
            source_type=row["source_type"],
            source_id=row["source_id"],
            suggested_eval=row["suggested_eval"],
            reason=row["reason"],
            candidate_path=row["candidate_path"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_playbook(self, row: sqlite3.Row) -> Playbook:
        return Playbook(
            id=row["id"],
            slug=row["slug"],
            title=row["title"],
            source_eval_name=row["source_eval_name"],
            successful_run_count=row["successful_run_count"],
            playbook_path=row["playbook_path"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_handoff_review(self, row: sqlite3.Row) -> HandoffReview:
        return HandoffReview(
            id=row["id"],
            status=row["status"],
            current_focus=row["current_focus"],
            blocked_task_count=row["blocked_task_count"],
            stale_handoff_count=row["stale_handoff_count"],
            blocked_tasks=_json_loads(row["blocked_tasks"], []),
            stale_handoffs=_json_loads(row["stale_handoffs"], []),
            reviewed_paths=_json_loads(row["reviewed_paths"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_eval_after_change_check(
        self,
        row: sqlite3.Row,
    ) -> EvalAfterChangeCheck:
        return EvalAfterChangeCheck(
            id=row["id"],
            change_summary=row["change_summary"],
            changed_paths=_json_loads(row["changed_paths"], []),
            eval_names=_json_loads(row["eval_names"], []),
            status=row["status"],
            result_paths=_json_loads(row["result_paths"], []),
            run_ids=_json_loads(row["run_ids"], []),
            report_path=row["report_path"],
            command=row["command"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
        )

    def _row_to_learning_distillation(self, row: sqlite3.Row) -> LearningDistillation:
        return LearningDistillation(
            id=row["id"],
            status=row["status"],
            min_occurrences=row["min_occurrences"],
            stable_learning_count=row["stable_learning_count"],
            stable_learnings=_json_loads(row["stable_learnings"], []),
            source_learning_count=row["source_learning_count"],
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_budget_trust_posture_report(
        self,
        row: sqlite3.Row,
    ) -> BudgetTrustPostureReport:
        return BudgetTrustPostureReport(
            id=row["id"],
            status=row["status"],
            task_count=row["task_count"],
            risk_counts=_json_loads(row["risk_counts"], {}),
            budget_state=row["budget_state"],
            budget_summary=_json_loads(row["budget_summary"], {}),
            trust_state=row["trust_state"],
            trust_summary=_json_loads(row["trust_summary"], {}),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_dispatch_posture_history_summary(
        self,
        row: sqlite3.Row,
    ) -> DispatchPostureHistorySummary:
        return DispatchPostureHistorySummary(
            id=row["id"],
            status=row["status"],
            snapshot_count=row["snapshot_count"],
            latest_task_count=row["latest_task_count"],
            task_count_delta=row["task_count_delta"],
            latest_risk_counts=_json_loads(row["latest_risk_counts"], {}),
            budget_states=_json_loads(row["budget_states"], []),
            trust_states=_json_loads(row["trust_states"], []),
            first_snapshot_at=row["first_snapshot_at"],
            latest_snapshot_at=row["latest_snapshot_at"],
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_dispatch_posture_staleness_review(
        self,
        row: sqlite3.Row,
    ) -> DispatchPostureStalenessReview:
        return DispatchPostureStalenessReview(
            id=row["id"],
            status=row["status"],
            snapshot_count=row["snapshot_count"],
            stale_snapshot_count=row["stale_snapshot_count"],
            latest_snapshot_age_seconds=row["latest_snapshot_age_seconds"],
            stale_after_seconds=row["stale_after_seconds"],
            latest_task_count=row["latest_task_count"],
            latest_risk_counts=_json_loads(row["latest_risk_counts"], {}),
            latest_snapshot_at=row["latest_snapshot_at"],
            oldest_snapshot_at=row["oldest_snapshot_at"],
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_dispatch_posture_refresh_recommendation(
        self,
        row: sqlite3.Row,
    ) -> DispatchPostureRefreshRecommendation:
        return DispatchPostureRefreshRecommendation(
            id=row["id"],
            status=row["status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            snapshot_count=row["snapshot_count"],
            stale_snapshot_count=row["stale_snapshot_count"],
            latest_snapshot_age_seconds=row["latest_snapshot_age_seconds"],
            stale_after_seconds=row["stale_after_seconds"],
            latest_snapshot_at=row["latest_snapshot_at"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            approval_boundary=row["approval_boundary"],
            deferred_capabilities=_json_loads(row["deferred_capabilities"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_expansion_ledger(
        self,
        row: sqlite3.Row,
    ) -> CapabilityExpansionLedger:
        return CapabilityExpansionLedger(
            id=row["id"],
            status=row["status"],
            capability_count=row["capability_count"],
            ready_count=row["ready_count"],
            deferred_count=row["deferred_count"],
            approval_boundary=row["approval_boundary"],
            capabilities=_json_loads(row["capabilities"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_readiness_review(
        self,
        row: sqlite3.Row,
    ) -> CapabilityReadinessReview:
        return CapabilityReadinessReview(
            id=row["id"],
            status=row["status"],
            source_ledger_id=row["source_ledger_id"],
            source_ledger_status=row["source_ledger_status"],
            capability_count=row["capability_count"],
            ready_count=row["ready_count"],
            not_ready_count=row["not_ready_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_boundary=row["approval_boundary"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            review_items=_json_loads(row["review_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_proof_gap_index(
        self,
        row: sqlite3.Row,
    ) -> CapabilityProofGapIndex:
        return CapabilityProofGapIndex(
            id=row["id"],
            status=row["status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            capability_count=row["capability_count"],
            gap_count=row["gap_count"],
            missing_evidence_count=row["missing_evidence_count"],
            blocked_capability_count=row["blocked_capability_count"],
            next_proof_count=row["next_proof_count"],
            approval_boundary=row["approval_boundary"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            proof_gaps=_json_loads(row["proof_gaps"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_approval_boundary_matrix(
        self,
        row: sqlite3.Row,
    ) -> CapabilityApprovalBoundaryMatrix:
        return CapabilityApprovalBoundaryMatrix(
            id=row["id"],
            status=row["status"],
            source_index_id=row["source_index_id"],
            source_index_status=row["source_index_status"],
            capability_count=row["capability_count"],
            boundary_count=row["boundary_count"],
            gap_count=row["gap_count"],
            blocked_capability_count=row["blocked_capability_count"],
            approval_required_count=row["approval_required_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            boundary_rows=_json_loads(row["boundary_rows"], []),
            matrix_entries=_json_loads(row["matrix_entries"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_evidence_collection_plan(
        self,
        row: sqlite3.Row,
    ) -> CapabilityEvidenceCollectionPlan:
        return CapabilityEvidenceCollectionPlan(
            id=row["id"],
            status=row["status"],
            source_matrix_id=row["source_matrix_id"],
            source_matrix_status=row["source_matrix_status"],
            capability_count=row["capability_count"],
            evidence_item_count=row["evidence_item_count"],
            manual_collection_count=row["manual_collection_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            evidence_items=_json_loads(row["evidence_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_promotion_gate_checklist(
        self,
        row: sqlite3.Row,
    ) -> CapabilityPromotionGateChecklist:
        return CapabilityPromotionGateChecklist(
            id=row["id"],
            status=row["status"],
            source_plan_id=row["source_plan_id"],
            source_plan_status=row["source_plan_status"],
            capability_count=row["capability_count"],
            gate_count=row["gate_count"],
            blocked_promotion_count=row["blocked_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_promotion_decision_ledger(
        self,
        row: sqlite3.Row,
    ) -> CapabilityPromotionDecisionLedger:
        return CapabilityPromotionDecisionLedger(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            decision_count=row["decision_count"],
            deferred_promotion_count=row["deferred_promotion_count"],
            operator_decision_required_count=row["operator_decision_required_count"],
            blocked_promotion_count=row["blocked_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            decision_items=_json_loads(row["decision_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_trust_promotion_audit(
        self,
        row: sqlite3.Row,
    ) -> CapabilityTrustPromotionAudit:
        return CapabilityTrustPromotionAudit(
            id=row["id"],
            status=row["status"],
            source_ledger_id=row["source_ledger_id"],
            source_ledger_status=row["source_ledger_status"],
            capability_count=row["capability_count"],
            audit_count=row["audit_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            operator_review_required_count=row["operator_review_required_count"],
            deferred_promotion_count=row["deferred_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            audit_items=_json_loads(row["audit_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_automatic_retry_audit(
        self,
        row: sqlite3.Row,
    ) -> CapabilityAutomaticRetryAudit:
        return CapabilityAutomaticRetryAudit(
            id=row["id"],
            status=row["status"],
            source_audit_id=row["source_audit_id"],
            source_audit_status=row["source_audit_status"],
            capability_count=row["capability_count"],
            audit_count=row["audit_count"],
            blocked_retry_count=row["blocked_retry_count"],
            operator_review_required_count=row["operator_review_required_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            deferred_promotion_count=row["deferred_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            audit_items=_json_loads(row["audit_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_real_cost_tracking_audit(
        self,
        row: sqlite3.Row,
    ) -> CapabilityRealCostTrackingAudit:
        return CapabilityRealCostTrackingAudit(
            id=row["id"],
            status=row["status"],
            source_audit_id=row["source_audit_id"],
            source_audit_status=row["source_audit_status"],
            capability_count=row["capability_count"],
            audit_count=row["audit_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            operator_review_required_count=row["operator_review_required_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            deferred_promotion_count=row["deferred_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            audit_items=_json_loads(row["audit_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_hosted_dashboard_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> HostedDashboardProofChecklist:
        return HostedDashboardProofChecklist(
            id=row["id"],
            status=row["status"],
            source_audit_id=row["source_audit_id"],
            source_audit_status=row["source_audit_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            operator_review_required_count=row["operator_review_required_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
            source_kind=row["source_kind"] or "real_cost_tracking_audit",
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"] or "none",
        )

    def _row_to_remote_worker_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> RemoteWorkerProofChecklist:
        return RemoteWorkerProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            operator_review_required_count=row["operator_review_required_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_autonomous_scheduling_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> AutonomousSchedulingProofChecklist:
        return AutonomousSchedulingProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_scheduling_proof_count=row["blocked_scheduling_proof_count"],
            operator_review_required_count=row["operator_review_required_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_browser_desktop_adapter_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> BrowserDesktopAdapterProofChecklist:
        return BrowserDesktopAdapterProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_adapter_proof_count=row["blocked_adapter_proof_count"],
            operator_review_required_count=row["operator_review_required_count"],
            blocked_scheduling_proof_count=row["blocked_scheduling_proof_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_ci_deploy_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> CiDeployProofChecklist:
        return CiDeployProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_ci_deploy_proof_count=row["blocked_ci_deploy_proof_count"],
            operator_review_required_count=row["operator_review_required_count"],
            blocked_adapter_proof_count=row["blocked_adapter_proof_count"],
            blocked_scheduling_proof_count=row["blocked_scheduling_proof_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_budget_enforcement_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> BudgetEnforcementProofChecklist:
        return BudgetEnforcementProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_budget_enforcement_proof_count=(
                row["blocked_budget_enforcement_proof_count"]
            ),
            operator_review_required_count=row["operator_review_required_count"],
            blocked_ci_deploy_proof_count=row["blocked_ci_deploy_proof_count"],
            blocked_adapter_proof_count=row["blocked_adapter_proof_count"],
            blocked_scheduling_proof_count=row["blocked_scheduling_proof_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_trust_promotion_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> TrustPromotionProofChecklist:
        return TrustPromotionProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_trust_promotion_proof_count=(
                row["blocked_trust_promotion_proof_count"]
            ),
            operator_review_required_count=row["operator_review_required_count"],
            blocked_budget_enforcement_proof_count=(
                row["blocked_budget_enforcement_proof_count"]
            ),
            blocked_ci_deploy_proof_count=row["blocked_ci_deploy_proof_count"],
            blocked_adapter_proof_count=row["blocked_adapter_proof_count"],
            blocked_scheduling_proof_count=row["blocked_scheduling_proof_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_automatic_retry_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> AutomaticRetryProofChecklist:
        return AutomaticRetryProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_automatic_retry_proof_count=(
                row["blocked_automatic_retry_proof_count"]
            ),
            operator_review_required_count=row["operator_review_required_count"],
            blocked_trust_promotion_proof_count=(
                row["blocked_trust_promotion_proof_count"]
            ),
            blocked_budget_enforcement_proof_count=(
                row["blocked_budget_enforcement_proof_count"]
            ),
            blocked_ci_deploy_proof_count=row["blocked_ci_deploy_proof_count"],
            blocked_adapter_proof_count=row["blocked_adapter_proof_count"],
            blocked_scheduling_proof_count=row["blocked_scheduling_proof_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_real_cost_tracking_proof_checklist(
        self,
        row: sqlite3.Row,
    ) -> RealCostTrackingProofChecklist:
        return RealCostTrackingProofChecklist(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            capability_count=row["capability_count"],
            checklist_count=row["checklist_count"],
            blocked_real_cost_tracking_proof_count=(
                row["blocked_real_cost_tracking_proof_count"]
            ),
            operator_review_required_count=row["operator_review_required_count"],
            blocked_automatic_retry_proof_count=(
                row["blocked_automatic_retry_proof_count"]
            ),
            blocked_trust_promotion_proof_count=(
                row["blocked_trust_promotion_proof_count"]
            ),
            blocked_budget_enforcement_proof_count=(
                row["blocked_budget_enforcement_proof_count"]
            ),
            blocked_ci_deploy_proof_count=row["blocked_ci_deploy_proof_count"],
            blocked_adapter_proof_count=row["blocked_adapter_proof_count"],
            blocked_scheduling_proof_count=row["blocked_scheduling_proof_count"],
            blocked_worker_proof_count=row["blocked_worker_proof_count"],
            blocked_dashboard_proof_count=row["blocked_dashboard_proof_count"],
            blocked_cost_tracking_count=row["blocked_cost_tracking_count"],
            blocked_retry_count=row["blocked_retry_count"],
            blocked_trust_promotion_count=row["blocked_trust_promotion_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            boundary_count=row["boundary_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            checklist_items=_json_loads(row["checklist_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_goal_completion_audit(
        self,
        row: sqlite3.Row,
    ) -> GoalCompletionAudit:
        return GoalCompletionAudit(
            id=row["id"],
            status=row["status"],
            requirement_count=row["requirement_count"],
            satisfied_requirement_count=row["satisfied_requirement_count"],
            blocked_requirement_count=row["blocked_requirement_count"],
            missing_evidence_count=row["missing_evidence_count"],
            approval_required_count=row["approval_required_count"],
            external_decision_count=row["external_decision_count"],
            recommended_commands=_json_loads(row["recommended_commands"], []),
            reason=row["reason"],
            audit_items=_json_loads(row["audit_items"], []),
            external_decisions=_json_loads(row["external_decisions"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_decision_brief(
        self,
        row: sqlite3.Row,
    ) -> ExpansionDecisionBrief:
        return ExpansionDecisionBrief(
            id=row["id"],
            status=row["status"],
            source_audit_id=row["source_audit_id"],
            source_audit_status=row["source_audit_status"],
            requirement_count=row["requirement_count"],
            blocked_requirement_count=row["blocked_requirement_count"],
            external_decision_count=row["external_decision_count"],
            approval_required_count=row["approval_required_count"],
            decision_item_count=row["decision_item_count"],
            recommended_next_step=row["recommended_next_step"],
            decision_items=_json_loads(row["decision_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_decision_evidence_index(
        self,
        row: sqlite3.Row,
    ) -> ExpansionDecisionEvidenceIndex:
        return ExpansionDecisionEvidenceIndex(
            id=row["id"],
            status=row["status"],
            source_brief_id=row["source_brief_id"],
            source_brief_status=row["source_brief_status"],
            source_audit_id=row["source_audit_id"],
            decision_item_count=row["decision_item_count"],
            evidence_item_count=row["evidence_item_count"],
            external_decision_count=row["external_decision_count"],
            capability_decision_count=row["capability_decision_count"],
            missing_evidence_link_count=row["missing_evidence_link_count"],
            recommended_next_step=row["recommended_next_step"],
            evidence_items=_json_loads(row["evidence_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_review_checklist(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorReviewChecklist:
        return ExpansionOperatorReviewChecklist(
            id=row["id"],
            status=row["status"],
            source_index_id=row["source_index_id"],
            source_index_status=row["source_index_status"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            review_item_count=row["review_item_count"],
            decision_required_count=row["decision_required_count"],
            external_review_count=row["external_review_count"],
            capability_review_count=row["capability_review_count"],
            missing_evidence_link_count=row["missing_evidence_link_count"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            recommended_next_step=row["recommended_next_step"],
            review_items=_json_loads(row["review_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_decision_ledger(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorDecisionLedger:
        return ExpansionOperatorDecisionLedger(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            decision_item_count=row["decision_item_count"],
            pending_decision_count=row["pending_decision_count"],
            approved_decision_count=row["approved_decision_count"],
            deferred_decision_count=row["deferred_decision_count"],
            more_evidence_requested_count=row["more_evidence_requested_count"],
            external_decision_count=row["external_decision_count"],
            capability_decision_count=row["capability_decision_count"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            recommended_next_step=row["recommended_next_step"],
            decision_items=_json_loads(row["decision_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_draft(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalDraft:
        return ExpansionOperatorApprovalDraft(
            id=row["id"],
            status=row["status"],
            source_ledger_id=row["source_ledger_id"],
            source_ledger_status=row["source_ledger_status"],
            source_checklist_id=row["source_checklist_id"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            draft_item_count=row["draft_item_count"],
            draft_request_count=row["draft_request_count"],
            created_approval_request_count=row["created_approval_request_count"],
            external_draft_count=row["external_draft_count"],
            capability_draft_count=row["capability_draft_count"],
            approval_boundary_count=row["approval_boundary_count"],
            pending_decision_count=row["pending_decision_count"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            recommended_next_step=row["recommended_next_step"],
            draft_items=_json_loads(row["draft_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_request_review(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalRequestReview:
        return ExpansionOperatorApprovalRequestReview(
            id=row["id"],
            status=row["status"],
            source_draft_id=row["source_draft_id"],
            source_draft_status=row["source_draft_status"],
            source_ledger_id=row["source_ledger_id"],
            source_checklist_id=row["source_checklist_id"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            draft_request_count=row["draft_request_count"],
            review_item_count=row["review_item_count"],
            ready_request_count=row["ready_request_count"],
            blocked_request_count=row["blocked_request_count"],
            schema_gap_count=row["schema_gap_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            external_request_count=row["external_request_count"],
            capability_request_count=row["capability_request_count"],
            approval_boundary_count=row["approval_boundary_count"],
            recommended_next_step=row["recommended_next_step"],
            review_items=_json_loads(row["review_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_schema_decision(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalSchemaDecision:
        return ExpansionOperatorApprovalSchemaDecision(
            id=row["id"],
            status=row["status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            source_draft_id=row["source_draft_id"],
            source_ledger_id=row["source_ledger_id"],
            source_checklist_id=row["source_checklist_id"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            affected_request_count=row["affected_request_count"],
            schema_gap_count=row["schema_gap_count"],
            missing_field_count=row["missing_field_count"],
            missing_fields=_json_loads(row["missing_fields"], []),
            external_request_count=row["external_request_count"],
            capability_request_count=row["capability_request_count"],
            decision_option_count=row["decision_option_count"],
            recommended_option=row["recommended_option"],
            rejected_option_count=row["rejected_option_count"],
            schema_object_count=row["schema_object_count"],
            migration_applied_count=row["migration_applied_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            recommended_next_step=row["recommended_next_step"],
            decision_options=_json_loads(row["decision_options"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_schema_migration_plan(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalSchemaMigrationPlan:
        return ExpansionOperatorApprovalSchemaMigrationPlan(
            id=row["id"],
            status=row["status"],
            source_decision_id=row["source_decision_id"],
            source_decision_status=row["source_decision_status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            source_draft_id=row["source_draft_id"],
            source_ledger_id=row["source_ledger_id"],
            source_checklist_id=row["source_checklist_id"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            recommended_option=row["recommended_option"],
            target_table=row["target_table"],
            affected_request_count=row["affected_request_count"],
            schema_gap_count=row["schema_gap_count"],
            missing_field_count=row["missing_field_count"],
            external_request_count=row["external_request_count"],
            capability_request_count=row["capability_request_count"],
            planned_column_count=row["planned_column_count"],
            planned_index_count=row["planned_index_count"],
            migration_step_count=row["migration_step_count"],
            migration_applied_count=row["migration_applied_count"],
            table_created_count=row["table_created_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            recommended_next_step=row["recommended_next_step"],
            planned_columns=_json_loads(row["planned_columns"], []),
            planned_indexes=_json_loads(row["planned_indexes"], []),
            migration_steps=_json_loads(row["migration_steps"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_schema_migration_approval_request(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalSchemaMigrationApprovalRequest:
        return ExpansionOperatorApprovalSchemaMigrationApprovalRequest(
            id=row["id"],
            status=row["status"],
            source_plan_id=row["source_plan_id"],
            source_plan_status=row["source_plan_status"],
            source_decision_id=row["source_decision_id"],
            source_decision_status=row["source_decision_status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            target_table=row["target_table"],
            planned_column_count=row["planned_column_count"],
            planned_index_count=row["planned_index_count"],
            migration_step_count=row["migration_step_count"],
            affected_request_count=row["affected_request_count"],
            schema_gap_count=row["schema_gap_count"],
            request_count=row["request_count"],
            approval_boundary=row["approval_boundary"],
            requested_action=row["requested_action"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            migration_applied_count=row["migration_applied_count"],
            table_created_count=row["table_created_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            recommended_next_step=row["recommended_next_step"],
            approval_items=_json_loads(row["approval_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_schema_migration_decision_ledger(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalSchemaMigrationDecisionLedger:
        return ExpansionOperatorApprovalSchemaMigrationDecisionLedger(
            id=row["id"],
            status=row["status"],
            source_request_id=row["source_request_id"],
            source_request_status=row["source_request_status"],
            source_plan_id=row["source_plan_id"],
            source_plan_status=row["source_plan_status"],
            source_decision_id=row["source_decision_id"],
            source_decision_status=row["source_decision_status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            target_table=row["target_table"],
            planned_column_count=row["planned_column_count"],
            planned_index_count=row["planned_index_count"],
            migration_step_count=row["migration_step_count"],
            affected_request_count=row["affected_request_count"],
            schema_gap_count=row["schema_gap_count"],
            request_count=row["request_count"],
            decision_count=row["decision_count"],
            pending_decision_count=row["pending_decision_count"],
            approved_decision_count=row["approved_decision_count"],
            deferred_decision_count=row["deferred_decision_count"],
            more_evidence_decision_count=row["more_evidence_decision_count"],
            approval_boundary=row["approval_boundary"],
            requested_action=row["requested_action"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            migration_applied_count=row["migration_applied_count"],
            table_created_count=row["table_created_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            recommended_next_step=row["recommended_next_step"],
            decision_items=_json_loads(row["decision_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_schema_migration_action_checklist(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalSchemaMigrationActionChecklist:
        return ExpansionOperatorApprovalSchemaMigrationActionChecklist(
            id=row["id"],
            status=row["status"],
            source_ledger_id=row["source_ledger_id"],
            source_ledger_status=row["source_ledger_status"],
            source_request_id=row["source_request_id"],
            source_request_status=row["source_request_status"],
            source_plan_id=row["source_plan_id"],
            source_plan_status=row["source_plan_status"],
            source_decision_id=row["source_decision_id"],
            source_decision_status=row["source_decision_status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            target_table=row["target_table"],
            request_count=row["request_count"],
            decision_count=row["decision_count"],
            pending_decision_count=row["pending_decision_count"],
            action_count=row["action_count"],
            pending_action_count=row["pending_action_count"],
            actions_taken_count=row["actions_taken_count"],
            selected_action=row["selected_action"],
            approval_boundary=row["approval_boundary"],
            requested_action=row["requested_action"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            migration_applied_count=row["migration_applied_count"],
            table_created_count=row["table_created_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            recommended_next_step=row["recommended_next_step"],
            action_items=_json_loads(row["action_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_schema_migration_selection_packet(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalSchemaMigrationSelectionPacket:
        return ExpansionOperatorApprovalSchemaMigrationSelectionPacket(
            id=row["id"],
            status=row["status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            source_ledger_id=row["source_ledger_id"],
            source_ledger_status=row["source_ledger_status"],
            source_request_id=row["source_request_id"],
            source_request_status=row["source_request_status"],
            source_plan_id=row["source_plan_id"],
            source_plan_status=row["source_plan_status"],
            source_decision_id=row["source_decision_id"],
            source_decision_status=row["source_decision_status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            target_table=row["target_table"],
            request_count=row["request_count"],
            decision_count=row["decision_count"],
            pending_decision_count=row["pending_decision_count"],
            action_count=row["action_count"],
            pending_action_count=row["pending_action_count"],
            actions_taken_count=row["actions_taken_count"],
            selected_action=row["selected_action"],
            selection_count=row["selection_count"],
            pending_selection_count=row["pending_selection_count"],
            selections_recorded_count=row["selections_recorded_count"],
            approve_selection_count=row["approve_selection_count"],
            defer_selection_count=row["defer_selection_count"],
            more_evidence_selection_count=row["more_evidence_selection_count"],
            approval_boundary=row["approval_boundary"],
            requested_action=row["requested_action"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            migration_applied_count=row["migration_applied_count"],
            table_created_count=row["table_created_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            recommended_next_step=row["recommended_next_step"],
            selection_items=_json_loads(row["selection_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_expansion_operator_approval_schema_migration_selection_input_template(
        self,
        row: sqlite3.Row,
    ) -> ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate:
        return ExpansionOperatorApprovalSchemaMigrationSelectionInputTemplate(
            id=row["id"],
            status=row["status"],
            source_packet_id=row["source_packet_id"],
            source_packet_status=row["source_packet_status"],
            source_checklist_id=row["source_checklist_id"],
            source_checklist_status=row["source_checklist_status"],
            source_ledger_id=row["source_ledger_id"],
            source_ledger_status=row["source_ledger_status"],
            source_request_id=row["source_request_id"],
            source_request_status=row["source_request_status"],
            source_plan_id=row["source_plan_id"],
            source_plan_status=row["source_plan_status"],
            source_decision_id=row["source_decision_id"],
            source_decision_status=row["source_decision_status"],
            source_review_id=row["source_review_id"],
            source_review_status=row["source_review_status"],
            target_table=row["target_table"],
            request_count=row["request_count"],
            decision_count=row["decision_count"],
            pending_decision_count=row["pending_decision_count"],
            action_count=row["action_count"],
            pending_action_count=row["pending_action_count"],
            actions_taken_count=row["actions_taken_count"],
            selected_action=row["selected_action"],
            selection_count=row["selection_count"],
            pending_selection_count=row["pending_selection_count"],
            selections_recorded_count=row["selections_recorded_count"],
            approve_selection_count=row["approve_selection_count"],
            defer_selection_count=row["defer_selection_count"],
            more_evidence_selection_count=row["more_evidence_selection_count"],
            template_count=row["template_count"],
            pending_input_count=row["pending_input_count"],
            inputs_recorded_count=row["inputs_recorded_count"],
            required_fields_count=row["required_fields_count"],
            missing_required_input_count=row["missing_required_input_count"],
            approval_boundary=row["approval_boundary"],
            requested_action=row["requested_action"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            migration_applied_count=row["migration_applied_count"],
            table_created_count=row["table_created_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            recommended_next_step=row["recommended_next_step"],
            input_template_items=_json_loads(row["input_template_items"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_operator_approval_schema_migration_application(
        self,
        row: sqlite3.Row,
    ) -> OperatorApprovalSchemaMigrationApplication:
        return OperatorApprovalSchemaMigrationApplication(
            id=row["id"],
            status=row["status"],
            source_template_id=row["source_template_id"],
            source_template_status=row["source_template_status"],
            source_packet_id=row["source_packet_id"],
            source_checklist_id=row["source_checklist_id"],
            source_ledger_id=row["source_ledger_id"],
            source_request_id=row["source_request_id"],
            source_plan_id=row["source_plan_id"],
            source_decision_id=row["source_decision_id"],
            source_review_id=row["source_review_id"],
            target_table=row["target_table"],
            operator_id=row["operator_id"],
            selected_action=row["selected_action"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            inputs_recorded_count=row["inputs_recorded_count"],
            missing_required_input_count=row["missing_required_input_count"],
            actions_taken_count=row["actions_taken_count"],
            migration_applied_count=row["migration_applied_count"],
            table_created_count=row["table_created_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_approval_request_count=row["existing_approval_request_count"],
            applied_table_columns=_json_loads(row["applied_table_columns"], []),
            applied_indexes=_json_loads(row["applied_indexes"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_operator_approval_request(
        self,
        row: sqlite3.Row,
    ) -> OperatorApprovalRequest:
        return OperatorApprovalRequest(
            id=row["id"],
            source_decision_id=row["source_decision_id"],
            source_review_id=row["source_review_id"],
            source_draft_id=row["source_draft_id"],
            source_ledger_id=row["source_ledger_id"],
            source_checklist_id=row["source_checklist_id"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            subject_type=row["subject_type"],
            subject_key=row["subject_key"],
            request_kind=row["request_kind"],
            capability_key=row["capability_key"],
            approval_boundary=row["approval_boundary"],
            allowed_actions=_json_loads(row["allowed_actions"], []),
            status=row["status"],
            reason=row["reason"],
            policy_name=row["policy_name"],
            policy_version=row["policy_version"],
            requested_by=row["requested_by"],
            decided_by=row["decided_by"],
            decision_note=row["decision_note"],
            requested_at=row["requested_at"],
            decided_at=row["decided_at"],
            evidence_path=row["evidence_path"],
            created_at=row["created_at"],
        )

    def _row_to_operator_approval_request_row_application(
        self,
        row: sqlite3.Row,
    ) -> OperatorApprovalRequestRowApplication:
        return OperatorApprovalRequestRowApplication(
            id=row["id"],
            status=row["status"],
            source_draft_id=row["source_draft_id"],
            source_draft_status=row["source_draft_status"],
            source_schema_application_id=row["source_schema_application_id"],
            source_schema_application_status=row["source_schema_application_status"],
            source_ledger_id=row["source_ledger_id"],
            source_checklist_id=row["source_checklist_id"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            operator_id=row["operator_id"],
            selected_action=row["selected_action"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            draft_request_count=row["draft_request_count"],
            operator_approval_row_count=row["operator_approval_row_count"],
            created_approval_request_count=row["created_approval_request_count"],
            existing_operator_approval_request_count=row[
                "existing_operator_approval_request_count"
            ],
            external_request_count=row["external_request_count"],
            capability_request_count=row["capability_request_count"],
            created_request_ids=_json_loads(row["created_request_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_operator_approval_request_decision(
        self,
        row: sqlite3.Row,
    ) -> OperatorApprovalRequestDecision:
        return OperatorApprovalRequestDecision(
            id=row["id"],
            status=row["status"],
            source_row_application_id=row["source_row_application_id"],
            source_row_application_status=row["source_row_application_status"],
            source_draft_id=row["source_draft_id"],
            source_schema_application_id=row["source_schema_application_id"],
            source_ledger_id=row["source_ledger_id"],
            source_checklist_id=row["source_checklist_id"],
            source_index_id=row["source_index_id"],
            source_brief_id=row["source_brief_id"],
            source_audit_id=row["source_audit_id"],
            operator_id=row["operator_id"],
            selected_action=row["selected_action"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            pending_request_count_before=row["pending_request_count_before"],
            decision_count=row["decision_count"],
            approved_decision_count=row["approved_decision_count"],
            deferred_decision_count=row["deferred_decision_count"],
            more_evidence_decision_count=row["more_evidence_decision_count"],
            pending_request_count_after=row["pending_request_count_after"],
            existing_decision_count=row["existing_decision_count"],
            created_approval_request_count=row["created_approval_request_count"],
            external_request_count=row["external_request_count"],
            capability_request_count=row["capability_request_count"],
            decided_request_ids=_json_loads(row["decided_request_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_operator_approval_effect_application(
        self,
        row: sqlite3.Row,
    ) -> OperatorApprovalEffectApplication:
        return OperatorApprovalEffectApplication(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            proposed_effect_count=row["proposed_effect_count"],
            applied_effect_count=row["applied_effect_count"],
            existing_applied_effect_count=row["existing_applied_effect_count"],
            external_effect_count=row["external_effect_count"],
            capability_effect_count=row["capability_effect_count"],
            legacy_approval_request_count=row["legacy_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            applied_effect_ids=_json_loads(row["applied_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_effect_application(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultEffectApplication:
        return CapabilityActivationFollowupResultEffectApplication(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            proposed_effect_count=row["proposed_effect_count"],
            applied_effect_count=row["applied_effect_count"],
            existing_applied_effect_count=row["existing_applied_effect_count"],
            capability_effect_count=row["capability_effect_count"],
            approval_request_count=row["approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            applied_effect_ids=_json_loads(row["applied_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_application(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectApplication:
        return CapabilityActivationFollowupResultTaskResultEffectApplication(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            proposed_effect_count=row["proposed_effect_count"],
            applied_effect_count=row["applied_effect_count"],
            existing_applied_effect_count=row["existing_applied_effect_count"],
            capability_effect_count=row["capability_effect_count"],
            approval_request_count=row["approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            applied_effect_ids=_json_loads(row["applied_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_task_result_effect_application(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectApplication:
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectApplication(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            proposed_effect_count=row["proposed_effect_count"],
            applied_effect_count=row["applied_effect_count"],
            existing_applied_effect_count=row["existing_applied_effect_count"],
            capability_effect_count=row["capability_effect_count"],
            approval_request_count=row["approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            applied_effect_ids=_json_loads(row["applied_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_task_result_effect_task_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskBatch:
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultEffectTaskBatch(
            id=row["id"],
            status=row["status"],
            source_application_id=row["source_application_id"],
            applied_downstream_effect_count=row[
                "applied_downstream_effect_count"
            ],
            task_count=row["task_count"],
            existing_task_count=row["existing_task_count"],
            capability_task_count=row["capability_task_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            created_task_ids=_json_loads(row["created_task_ids"], []),
            source_effect_ids=_json_loads(row["source_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_task_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskBatch:
        return CapabilityActivationFollowupResultTaskResultEffectTaskBatch(
            id=row["id"],
            status=row["status"],
            source_application_id=row["source_application_id"],
            applied_downstream_effect_count=row[
                "applied_downstream_effect_count"
            ],
            task_count=row["task_count"],
            existing_task_count=row["existing_task_count"],
            capability_task_count=row["capability_task_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            created_task_ids=_json_loads(row["created_task_ids"], []),
            source_effect_ids=_json_loads(row["source_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskBatch:
        return CapabilityActivationFollowupResultTaskBatch(
            id=row["id"],
            status=row["status"],
            source_application_id=row["source_application_id"],
            applied_followup_effect_count=row["applied_followup_effect_count"],
            task_count=row["task_count"],
            existing_task_count=row["existing_task_count"],
            capability_task_count=row["capability_task_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            created_task_ids=_json_loads(row["created_task_ids"], []),
            source_effect_ids=_json_loads(row["source_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_delegation_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskDelegationBatch:
        return CapabilityActivationFollowupResultTaskDelegationBatch(
            id=row["id"],
            status=row["status"],
            downstream_task_count=row["downstream_task_count"],
            routing_decision_count=row["routing_decision_count"],
            delegation_count=row["delegation_count"],
            existing_delegation_count=row["existing_delegation_count"],
            execution_started_count=row["execution_started_count"],
            network_action_count=row["network_action_count"],
            external_mutation_count=row["external_mutation_count"],
            activation_action_count=row["activation_action_count"],
            created_routing_decision_ids=_json_loads(
                row["created_routing_decision_ids"],
                [],
            ),
            created_delegation_ids=_json_loads(row["created_delegation_ids"], []),
            downstream_task_ids=_json_loads(row["downstream_task_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_task_delegation_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskDelegationBatch:
        return CapabilityActivationFollowupResultTaskResultEffectTaskDelegationBatch(
            id=row["id"],
            status=row["status"],
            downstream_task_count=row["downstream_task_count"],
            routing_decision_count=row["routing_decision_count"],
            delegation_count=row["delegation_count"],
            existing_delegation_count=row["existing_delegation_count"],
            execution_started_count=row["execution_started_count"],
            network_action_count=row["network_action_count"],
            external_mutation_count=row["external_mutation_count"],
            activation_action_count=row["activation_action_count"],
            created_routing_decision_ids=_json_loads(
                row["created_routing_decision_ids"],
                [],
            ),
            created_delegation_ids=_json_loads(row["created_delegation_ids"], []),
            downstream_task_ids=_json_loads(row["downstream_task_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_task_result_record(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord:
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultRecord(
            id=row["id"],
            delegation_id=row["delegation_id"],
            downstream_task_id=row["downstream_task_id"],
            source_application_id=row["source_application_id"],
            source_decision_id=row["source_decision_id"],
            source_downstream_result_id=row["source_downstream_result_id"],
            source_effect_id=row["source_effect_id"],
            source_delegation_id=row["source_delegation_id"],
            source_downstream_task_id=row["source_downstream_task_id"],
            source_followup_result_id=row["source_followup_result_id"],
            upstream_followup_effect_id=row["upstream_followup_effect_id"],
            source_contract_id=row["source_contract_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            capability=row["capability"],
            assigned_profile=row["assigned_profile"],
            evidence_status=row["evidence_status"],
            result_summary=row["result_summary"],
            evidence_path=row["evidence_path"],
            result_json=_json_loads(row["result_json"], {}),
            idempotency_key=row["idempotency_key"],
            activation_allowed=bool(row["activation_allowed"]),
            capability_enabled=bool(row["capability_enabled"]),
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_task_result_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultBatch:
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultBatch(
            id=row["id"],
            status=row["status"],
            completed_delegation_count=row["completed_delegation_count"],
            result_record_count=row["result_record_count"],
            existing_result_record_count=row["existing_result_record_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            created_result_ids=_json_loads(row["created_result_ids"], []),
            completed_delegation_ids=_json_loads(
                row["completed_delegation_ids"],
                [],
            ),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_effect_task_result_decision(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultEffectTaskResultDecision:
        return CapabilityActivationFollowupResultTaskResultEffectTaskResultDecision(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selected_action=row["selected_action"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            result_record_count=row["result_record_count"],
            decision_count=row["decision_count"],
            accepted_keep_blocked_decision_count=(
                row["accepted_keep_blocked_decision_count"]
            ),
            more_evidence_decision_count=row["more_evidence_decision_count"],
            deferred_decision_count=row["deferred_decision_count"],
            existing_decision_count=row["existing_decision_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            decided_result_ids=_json_loads(row["decided_result_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_record(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultRecord:
        return CapabilityActivationFollowupResultTaskResultRecord(
            id=row["id"],
            delegation_id=row["delegation_id"],
            downstream_task_id=row["downstream_task_id"],
            source_result_id=row["source_result_id"],
            source_effect_id=row["source_effect_id"],
            source_contract_id=row["source_contract_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            capability=row["capability"],
            assigned_profile=row["assigned_profile"],
            evidence_status=row["evidence_status"],
            result_summary=row["result_summary"],
            evidence_path=row["evidence_path"],
            result_json=_json_loads(row["result_json"], {}),
            idempotency_key=row["idempotency_key"],
            activation_allowed=bool(row["activation_allowed"]),
            capability_enabled=bool(row["capability_enabled"]),
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultBatch:
        return CapabilityActivationFollowupResultTaskResultBatch(
            id=row["id"],
            status=row["status"],
            completed_delegation_count=row["completed_delegation_count"],
            result_record_count=row["result_record_count"],
            existing_result_record_count=row["existing_result_record_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            created_result_ids=_json_loads(row["created_result_ids"], []),
            completed_delegation_ids=_json_loads(
                row["completed_delegation_ids"],
                [],
            ),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_task_result_decision(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultTaskResultDecision:
        return CapabilityActivationFollowupResultTaskResultDecision(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selected_action=row["selected_action"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            result_record_count=row["result_record_count"],
            decision_count=row["decision_count"],
            accepted_keep_blocked_decision_count=(
                row["accepted_keep_blocked_decision_count"]
            ),
            more_evidence_decision_count=row["more_evidence_decision_count"],
            deferred_decision_count=row["deferred_decision_count"],
            existing_decision_count=row["existing_decision_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            external_mutation_count=row["external_mutation_count"],
            decided_result_ids=_json_loads(row["decided_result_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_task_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationTaskBatch:
        return CapabilityActivationTaskBatch(
            id=row["id"],
            status=row["status"],
            source_application_id=row["source_application_id"],
            goal_id=row["goal_id"],
            applied_capability_effect_count=row["applied_capability_effect_count"],
            task_count=row["task_count"],
            existing_task_count=row["existing_task_count"],
            activation_action_count=row["activation_action_count"],
            created_task_ids=_json_loads(row["created_task_ids"], []),
            source_effect_ids=_json_loads(row["source_effect_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_contract(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationContract:
        return CapabilityActivationContract(
            id=row["id"],
            task_id=row["task_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            capability=row["capability"],
            source_effect_id=row["source_effect_id"],
            source_application_id=row["source_application_id"],
            evidence_requirements=_json_loads(
                row["evidence_requirements_json"],
                {},
            ),
            approval_boundary=row["approval_boundary"],
            approval_status=row["approval_status"],
            required_approval_id=row["required_approval_id"],
            status=row["status"],
            activation_allowed=bool(row["activation_allowed"]),
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            report_path=row["report_path"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def _row_to_capability_activation_contract_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationContractBatch:
        return CapabilityActivationContractBatch(
            id=row["id"],
            status=row["status"],
            source_task_batch_id=row["source_task_batch_id"],
            activation_task_count=row["activation_task_count"],
            contract_count=row["contract_count"],
            existing_contract_count=row["existing_contract_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            created_contract_ids=_json_loads(row["created_contract_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_evidence_record(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationEvidenceRecord:
        return CapabilityActivationEvidenceRecord(
            id=row["id"],
            contract_id=row["contract_id"],
            task_id=row["task_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            capability=row["capability"],
            source_effect_id=row["source_effect_id"],
            evidence_kind=row["evidence_kind"],
            evidence_reference=row["evidence_reference"],
            verification_command=row["verification_command"],
            verification_status=row["verification_status"],
            recorded_by=row["recorded_by"],
            summary=row["summary"],
            status=row["status"],
            evidence_path=row["evidence_path"],
            result_json=_json_loads(row["result_json"], {}),
            idempotency_key=row["idempotency_key"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_evidence_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationEvidenceBatch:
        return CapabilityActivationEvidenceBatch(
            id=row["id"],
            status=row["status"],
            contract_count=row["contract_count"],
            evidence_record_count=row["evidence_record_count"],
            existing_evidence_count=row["existing_evidence_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            created_evidence_ids=_json_loads(row["created_evidence_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_decision(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationDecision:
        return CapabilityActivationDecision(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selected_action=row["selected_action"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            contract_count=row["contract_count"],
            decision_count=row["decision_count"],
            approved_decision_count=row["approved_decision_count"],
            deferred_decision_count=row["deferred_decision_count"],
            more_evidence_decision_count=row["more_evidence_decision_count"],
            existing_decision_count=row["existing_decision_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            decided_contract_ids=_json_loads(row["decided_contract_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_task_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupTaskBatch:
        return CapabilityActivationFollowupTaskBatch(
            id=row["id"],
            status=row["status"],
            source_decision_id=row["source_decision_id"],
            contract_count=row["contract_count"],
            followup_task_count=row["followup_task_count"],
            existing_followup_task_count=row["existing_followup_task_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            created_task_ids=_json_loads(row["created_task_ids"], []),
            contract_ids=_json_loads(row["contract_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_delegation_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupDelegationBatch:
        return CapabilityActivationFollowupDelegationBatch(
            id=row["id"],
            status=row["status"],
            followup_task_count=row["followup_task_count"],
            routing_decision_count=row["routing_decision_count"],
            delegation_count=row["delegation_count"],
            existing_delegation_count=row["existing_delegation_count"],
            execution_started_count=row["execution_started_count"],
            network_action_count=row["network_action_count"],
            external_mutation_count=row["external_mutation_count"],
            activation_action_count=row["activation_action_count"],
            created_routing_decision_ids=_json_loads(
                row["created_routing_decision_ids"],
                [],
            ),
            created_delegation_ids=_json_loads(row["created_delegation_ids"], []),
            followup_task_ids=_json_loads(row["followup_task_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_record(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultRecord:
        return CapabilityActivationFollowupResultRecord(
            id=row["id"],
            delegation_id=row["delegation_id"],
            followup_task_id=row["followup_task_id"],
            contract_id=row["contract_id"],
            decision_id=row["decision_id"],
            goal_id=row["goal_id"],
            project_id=row["project_id"],
            capability=row["capability"],
            assigned_profile=row["assigned_profile"],
            evidence_status=row["evidence_status"],
            result_summary=row["result_summary"],
            evidence_path=row["evidence_path"],
            result_json=_json_loads(row["result_json"], {}),
            idempotency_key=row["idempotency_key"],
            activation_allowed=bool(row["activation_allowed"]),
            capability_enabled=bool(row["capability_enabled"]),
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_batch(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultBatch:
        return CapabilityActivationFollowupResultBatch(
            id=row["id"],
            status=row["status"],
            completed_delegation_count=row["completed_delegation_count"],
            result_record_count=row["result_record_count"],
            existing_result_record_count=row["existing_result_record_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            created_result_ids=_json_loads(row["created_result_ids"], []),
            completed_delegation_ids=_json_loads(
                row["completed_delegation_ids"],
                [],
            ),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )

    def _row_to_capability_activation_followup_result_decision(
        self,
        row: sqlite3.Row,
    ) -> CapabilityActivationFollowupResultDecision:
        return CapabilityActivationFollowupResultDecision(
            id=row["id"],
            status=row["status"],
            operator_id=row["operator_id"],
            selected_action=row["selected_action"],
            selection_note=row["selection_note"],
            evidence_reference=row["evidence_reference"],
            result_record_count=row["result_record_count"],
            decision_count=row["decision_count"],
            accepted_keep_blocked_decision_count=(
                row["accepted_keep_blocked_decision_count"]
            ),
            more_evidence_decision_count=row["more_evidence_decision_count"],
            deferred_decision_count=row["deferred_decision_count"],
            existing_decision_count=row["existing_decision_count"],
            created_approval_request_count=row["created_approval_request_count"],
            activation_action_count=row["activation_action_count"],
            decided_result_ids=_json_loads(row["decided_result_ids"], []),
            report_path=row["report_path"],
            created_at=row["created_at"],
        )


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
