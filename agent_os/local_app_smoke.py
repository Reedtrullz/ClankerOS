from __future__ import annotations

import shlex
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import quote

from agent_os.delegation_runner import configure_profile_adapter
from agent_os.engine import AgentSystem
from agent_os.local_app import (
    NO_EXTERNAL_EFFECT_CLAIMS,
    _load_workspace_state,
    render_local_app_route,
    run_demo_app_scenario,
)
from agent_os.profile_routing import ensure_default_profiles
from agent_os.storage import Storage
from agent_os.subagent_delegation import load_delegation_result_metadata


def run_local_app_smoke_test(root: Path) -> dict[str, Any]:
    root = root.resolve()
    smoke_artifacts = root / ".clanker" / "app" / "smoke-artifacts"
    smoke_artifacts.mkdir(parents=True, exist_ok=True)
    sample_markdown = smoke_artifacts / "sample.md"
    sample_markdown.write_text("# App Smoke Artifact\n", encoding="utf-8")
    outside_artifact = Path(tempfile.gettempdir()) / f"{root.name}-app-smoke-outside.txt"
    outside_artifact.write_text("outside app smoke\n", encoding="utf-8")
    outside_link = smoke_artifacts / "outside.txt"
    if outside_link.exists() or outside_link.is_symlink():
        outside_link.unlink()
    outside_link.symlink_to(outside_artifact)
    routes = [
        ("/", "ClankerOS Local Operator"),
        ("/today", "Today Command Center"),
        ("/guide", "Suggested Use Guide"),
        ("/resume", "Resume Workspace"),
        ("/goals", "Goal Cockpit"),
        ("/search", "Global Search"),
        ("/workspace", "Workspace State"),
        ("/memory", "Memory Bank"),
        ("/skills", "Skills Inventory"),
        ("/profiles", "Profiles And Routing"),
        ("/workflow", "Modern Operator Workflow"),
        ("/actions", "Safe Action Catalog"),
        ("/verification", "Verification Handoff"),
        ("/ci-evidence", "CI Evidence Records"),
        ("/dogfooding", "Manual Dogfooding Checklist"),
        ("/projects", "Project Workflow Index"),
        ("/delegation-runs", "Delegation Run Index"),
        ("/inbox", "Operator Inbox"),
        ("/approvals", "Approvals"),
        ("/incidents", "Incidents"),
        ("/health", "System Health"),
        ("/demo", "Demo Scenario"),
        ("/artifacts?path=.clanker/app/smoke-artifacts/sample.md", "artifact_type"),
        (
            f"/artifacts?path={quote(str(sample_markdown), safe='')}",
            "absolute artifact paths are rejected",
            400,
        ),
        ("/artifacts?path=../README.md", "parent traversal is rejected", 400),
        (
            "/artifacts?path=.clanker/app/smoke-artifacts/outside.txt",
            "outside repo root",
            400,
        ),
    ]
    results = []
    for route_info in routes:
        route, marker, expected_status = (
            route_info if len(route_info) == 3 else (*route_info, 200)
        )
        response = render_local_app_route(root, route)
        marker_found = marker in response.body
        results.append(
            {
                "route": route,
                "status": response.status,
                "expected_status": expected_status,
                "required_marker": marker,
                "marker_found": marker_found,
            }
        )
    ok = all(
        item["status"] == item["expected_status"] and item["marker_found"]
        for item in results
    )
    return {
        "status": "passed" if ok else "failed",
        "routes": results,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": NO_EXTERNAL_EFFECT_CLAIMS,
    }


def run_local_app_demo_smoke_test(root: Path) -> dict[str, Any]:
    root = root.resolve()
    demo = run_demo_app_scenario(root)
    routes = [
        (
            "/demo",
            "Demo Scenario",
            [
                "data-operator-ribbon='true'",
                "data-operator-ribbon-cards='true'",
                "data-focus-mode-supported=\"true\"",
                "id=\"focus-toggle\"",
                "data-focus-mode-toggle=\"true\"",
                "data-focus-mode-storage=\"localStorage:clankeros-focus-mode\"",
                "data-focus-mode-write-on-get=\"false\"",
                "if (event.key === \"m\") { event.preventDefault(); toggleFocusMode(); }",
                "data-command-palette-filter-supported='true'",
                "data-command-palette-filter='true'",
                "data-command-palette-result-list='true'",
                "data-command-palette-empty='true'",
                "data-browser-route-history='true'",
                "data-browser-route-history-storage-key='clankeros-route-history'",
                "data-open-panel-memory='true'",
                "data-open-panel-memory-storage-prefix='clankeros-open-panels:'",
                "function initializeOpenPanelMemoryState()",
                "data-scroll-position-memory='true'",
                "data-scroll-position-memory-storage-prefix='clankeros-scroll-position:'",
                "function initializeScrollPositionMemoryState()",
                "function initializeActionFormDraftState()",
                "function initializeGoalNoteDraftState()",
                "data-command-palette-route-history='true'",
                "data-command-palette-route-history-storage-key='clankeros-route-history'",
                "function syncPaletteFilter()",
                "function rememberCurrentRoute()",
                "Demo Operator Workbench",
                "data-demo-operator-workbench='true'",
                "data-demo-workbench-primary='true'",
                "data-demo-workbench-evidence='true'",
                "demo_workbench_fixture_status</dt><dd>available",
                "demo_workbench_next_action</dt><dd>request_commit_for_reviewed_run",
                "Demo Walkthrough Map",
                "data-demo-walkthrough-map='true'",
                "data-demo-walkthrough-actions='true'",
                "data-demo-walkthrough-evidence='true'",
                "demo_walkthrough_current_stage</dt><dd>run",
                "demo_walkthrough_current_position</dt><dd>4/7",
                "demo_walkthrough_next_action</dt><dd>request_commit_for_reviewed_run",
                "demo_walkthrough_total_stages</dt><dd>7",
                "Demo Command Bar",
                "data-demo-command-evidence='true'",
                "demo_command_fixture_status</dt><dd>available",
                "demo_command_primary_command</dt><dd>python3 -m agent_os.cli demo",
                "Demo Dogfooding Links",
                "Demo Browser Progress",
                "Demo Gate Actions",
                "active_action: coder-commit-request",
                "confirmation_required: true_for_local_writes",
                "form_action: /actions/coder-commit-request",
                "external_effects_created: false",
                "Manual Browser Checkpoints",
                demo.coder_worktree_run_id,
            ],
        ),
        (
            "/dogfooding",
            "Manual Dogfooding Checklist",
            [
                "Dogfooding Operator Workbench",
                "data-dogfooding-operator-workbench='true'",
                "data-dogfooding-workbench-primary='true'",
                "data-dogfooding-workbench-evidence='true'",
                "Dogfooding Return Brief",
                "data-dogfooding-return-brief='true'",
                "data-dogfooding-return-evidence='true'",
                "dogfooding_return_product_action</dt><dd>request_commit_for_reviewed_run",
                "Dogfooding Session Checklist",
                "data-dogfooding-session-checklist='true'",
                "dogfooding_session_checklist_next_action</dt><dd>request_commit_for_reviewed_run",
                "Dogfooding Command Bar",
                "data-dogfooding-command-bar='true'",
                "data-dogfooding-command-evidence='true'",
                "data-dogfooding-fixture-evidence='true'",
                "dogfooding_workbench_fixture_status</dt><dd>available",
                "dogfooding_command_fixture_status</dt><dd>available",
                "demo_fixture_status: available",
                "next_dogfooding_action: request_commit_for_reviewed_run",
                f"/runs/{demo.coder_worktree_run_id}",
            ],
        ),
        (
            "/delegation-runs",
            "Delegation Run Index",
            [
                "Delegation Run Operator Workbench",
                "data-delegation-run-operator-workbench='true'",
                "data-delegation-run-workbench-primary='true'",
                "data-delegation-run-workbench-evidence='true'",
                "data-delegation-run-command-evidence='true'",
                "delegation_run_workbench_status</dt><dd>handoff_ready",
                "delegation_run_workbench_next_action</dt><dd>prepare_coder_from_handoff",
                "delegation_run_workbench_action_label</dt><dd>Prepare coder packet",
                demo.delegation_id,
                demo.run_id,
            ],
        ),
        (
            f"/runs/{quote(demo.run_id)}",
            "Run",
            [
                "Delegation Run Continuation",
                "data-delegation-run-continuation='true'",
                "data-delegation-run-continuation-evidence='true'",
                "delegation_run_continuation_status</dt><dd>action_form_ready",
                "delegation_run_continuation_next_action</dt><dd>prepare_coder_from_handoff",
                "delegation_run_continuation_action_label</dt><dd>Prepare coder packet",
                "Delegation Run Evidence",
                "Delegation Execution Artifacts",
                "Delegation Run Workflow State",
            ],
        ),
        (
            "/goals",
            "Goal Cockpit",
            [
                "Active Goals",
                "goal_first_navigation",
                f"/goals/{demo.goal_id}",
            ],
        ),
        (
            "/today",
            "Today Command Center",
            [
                "data-today-command-center='true'",
                "data-today-command-actions='true'",
                "data-today-command-primary='true'",
                "data-today-state-details='true'",
                "data-today-command-evidence='true'",
                "data-today-session-rail='true'",
                "data-today-session-rail-primary='true'",
                "today_session_rail_status</dt><dd>goal_ready",
                "today_session_rail_primary_action</dt><dd>Create commit request",
                "today_session_rail_finish_surface</dt><dd><a href='#today-finish'>Finish Today</a>",
                "data-today-note-details='true'",
                "data-today-pause-details='true'",
                "data-today-finish-details='true'",
                "data-today-session-summary='true'",
                "data-today-operator-workbench='true'",
                "data-today-workbench-evidence='true'",
                "data-today-decision-queue='true'",
                "data-today-decision-list='true'",
                "data-today-decision-row='true'",
                "data-today-decision-filter='true'",
                "data-today-decision-filter-kind='worktree_approval'",
                "data-today-decision-filter-query='true'",
                "data-today-decision-evidence='true'",
                "data-today-workflow-map='true'",
                "data-today-ci-handoff='true'",
                "data-today-goal-queue='true'",
                "today_command_status</dt><dd>goal_ready",
                "today_session_status</dt><dd>available",
                "today_session_current_gate</dt><dd>commit_request",
                "today_session_next_action</dt><dd>Create commit request",
                "today_workbench_status</dt><dd>goal_ready",
                "today_decision_queue_status</dt><dd>waiting_on_operator",
                "today_decision_queue_next_action</dt><dd>Create commit request",
                "today_decision_queue_pending_approvals</dt><dd>1",
                "today_workflow_map_status</dt><dd>available",
                "today_workflow_map_current_gate</dt><dd>commit_request",
                "today_ci_handoff_app_github_polling</dt><dd>false",
                "today_goal_queue_status</dt><dd>goals_ready",
                "today_command_primary_action</dt><dd>Create commit request",
                "today_workbench_do_action</dt><dd>Create commit request",
                "today_command_attention_status</dt><dd>needs_approval_review",
                "today_command_finish_form_available</dt><dd>true",
                f"/runs/{demo.coder_worktree_run_id}",
            ],
        ),
        (
            f"/goals/{quote(demo.goal_id)}",
            "Current Phase",
            [
                "data-operator-ribbon='true'",
                "operator_ribbon_status</dt><dd>available",
                "Timeline",
                "Goal Operator Workbench",
                "Goal Progress Meter",
                "data-goal-progress-meter='true'",
                "data-goal-progress-meter-bars='true'",
                "data-goal-progress-meter-task-bar='true'",
                "data-goal-progress-meter-gate-bar='true'",
                "data-goal-progress-meter-waiting='true'",
                "data-goal-progress-meter-proof='true'",
                "data-goal-progress-meter-action='true'",
                "data-goal-progress-meter-evidence='true'",
                "goal_progress_meter_current_gate</dt><dd>commit_request",
                "Goal Attention Digest",
                "data-goal-attention-digest='true'",
                "data-goal-attention-actions='true'",
                "data-goal-attention-primary='true'",
                "data-goal-attention-approvals='true'",
                "data-goal-attention-incidents='true'",
                "data-goal-attention-recommendations='true'",
                "data-goal-attention-open-work='true'",
                "data-goal-attention-safety='true'",
                "data-goal-attention-evidence='true'",
                "goal_attention_digest_status</dt><dd>waiting_on_operator",
                "Goal Decision Queue",
                "data-goal-decision-queue='true'",
                "data-goal-decision-list='true'",
                "data-goal-decision-row='true'",
                "data-goal-decision-filter='true'",
                "data-goal-decision-filter-kind='worktree_approval'",
                "data-goal-decision-filter-query='true'",
                "data-goal-decision-evidence='true'",
                "goal_decision_queue_status</dt><dd>waiting_on_operator",
                "data-goal-command-strip='true'",
                "data-goal-command-evidence='true'",
                "data-goal-jump-evidence='true'",
                "data-goal-workbench-evidence='true'",
                "data-goal-overview-actions='true'",
                "data-goal-overview-now='true'",
                "data-goal-overview-primary='true'",
                "data-goal-overview-scope='true'",
                "data-goal-overview-progress='true'",
                "data-goal-overview-waiting='true'",
                "data-goal-overview-safety='true'",
                "data-goal-overview-evidence='true'",
                "data-goal-overview-details='true'",
                "data-goal-risk-actions='true'",
                "data-goal-risk-now='true'",
                "data-goal-risk-primary='true'",
                "data-goal-risk-counts='true'",
                "data-goal-risk-boundary='true'",
                "data-goal-risk-first='true'",
                "data-goal-risk-safety='true'",
                "data-goal-risk-evidence='true'",
                "data-goal-risk-list='true'",
                "data-goal-criteria-actions='true'",
                "data-goal-criteria-now='true'",
                "data-goal-criteria-primary='true'",
                "data-goal-criteria-source='true'",
                "data-goal-criteria-progress='true'",
                "data-goal-criteria-first='true'",
                "data-goal-criteria-safety='true'",
                "data-goal-criteria-evidence='true'",
                "data-goal-criteria-list='true'",
                "data-goal-progress-actions='true'",
                "data-goal-progress-now='true'",
                "data-goal-progress-primary='true'",
                "data-goal-progress-tasks='true'",
                "data-goal-progress-gates='true'",
                "data-goal-progress-waiting='true'",
                "data-goal-progress-safety='true'",
                "data-goal-progress-evidence='true'",
                "data-goal-progress-details='true'",
                "data-goal-completion-actions='true'",
                "data-goal-completion-now='true'",
                "data-goal-completion-primary='true'",
                "data-goal-completion-gates='true'",
                "data-goal-completion-waiting='true'",
                "data-goal-completion-publish='true'",
                "data-goal-completion-safety='true'",
                "data-goal-completion-evidence='true'",
                "data-goal-timeline-actions='true'",
                "data-goal-timeline-now='true'",
                "data-goal-timeline-primary='true'",
                "data-goal-timeline-latest='true'",
                "data-goal-timeline-families='true'",
                "data-goal-timeline-flow='true'",
                "data-goal-timeline-safety='true'",
                "data-goal-timeline-evidence='true'",
                "data-goal-timeline-metadata='true'",
                "data-goal-activity-actions='true'",
                "data-goal-activity-now='true'",
                "data-goal-activity-primary='true'",
                "data-goal-activity-latest='true'",
                "data-goal-activity-signals='true'",
                "data-goal-activity-window='true'",
                "data-goal-activity-safety='true'",
                "data-goal-activity-evidence='true'",
                "data-goal-activity-metadata='true'",
                "data-goal-daily-loop-actions='true'",
                "data-goal-daily-loop-primary='true'",
                "data-goal-daily-loop-evidence='true'",
                "data-goal-pause-details='true'",
                "data-goal-finish-details='true'",
                "data-goal-section-index-actions='true'",
                "data-goal-section-index-operate='true'",
                "data-goal-section-index-proof='true'",
                "data-goal-section-index-work='true'",
                "data-goal-section-index-knowledge='true'",
                "data-goal-section-index-finish='true'",
                "data-goal-section-index-primary='true'",
                "data-goal-section-index-evidence='true'",
                "Goal Return Brief",
                "data-goal-return-brief='true'",
                "data-goal-return-actions='true'",
                "data-goal-return-primary='true'",
                "data-goal-return-latest='true'",
                "data-goal-return-blocker='true'",
                "data-goal-return-finish='true'",
                "data-goal-return-resume='true'",
                "data-goal-return-evidence='true'",
                "goal_return_current_gate</dt><dd>commit_request",
                "Goal Session Digest",
                "data-goal-session-digest='true'",
                "data-goal-session-actions='true'",
                "data-goal-session-primary='true'",
                "data-goal-session-since-save='true'",
                "data-goal-session-artifact='true'",
                "data-goal-session-waiting='true'",
                "data-goal-session-finish='true'",
                "data-goal-session-evidence='true'",
                "goal_session_digest_current_gate</dt><dd>commit_request",
                "Goal Continuation Rail",
                "data-goal-continuation-rail='true'",
                "data-goal-continuation-actions='true'",
                "data-goal-continuation-primary='true'",
                "data-goal-continuation-next='true'",
                "data-goal-continuation-then='true'",
                "data-goal-continuation-publish='true'",
                "data-goal-continuation-finish='true'",
                "data-goal-continuation-evidence='true'",
                "goal_continuation_current_gate</dt><dd>commit_request",
                "Goal Workflow Map",
                "data-goal-workflow-map='true'",
                "data-goal-workflow-map-actions='true'",
                "data-goal-workflow-map-primary='true'",
                "data-goal-workflow-map-progress='true'",
                "data-goal-workflow-map-approval='true'",
                "data-goal-workflow-map-publish='true'",
                "data-goal-workflow-map-finish='true'",
                "data-goal-workflow-map-evidence='true'",
                "workflow_map_current_gate</dt><dd>commit_request",
                "Goal Coder Handoff Digest",
                "data-goal-coder-handoff-digest='true'",
                "data-goal-coder-handoff-actions='true'",
                "data-goal-coder-handoff-primary='true'",
                "data-goal-coder-handoff-handoff='true'",
                "data-goal-coder-handoff-prep='true'",
                "data-goal-coder-handoff-execute='true'",
                "data-goal-coder-handoff-ship='true'",
                "data-goal-coder-handoff-safety='true'",
                "data-goal-coder-handoff-evidence='true'",
                "goal_coder_handoff_digest_status</dt><dd>ready_for_commit_request",
                "Goal CI Handoff",
                "data-goal-ci-handoff-actions='true'",
                "data-goal-ci-handoff-check='true'",
                "data-goal-ci-handoff-record='true'",
                "data-goal-ci-handoff-proof='true'",
                "data-goal-ci-handoff-full='true'",
                "data-goal-ci-handoff-finish='true'",
                "data-goal-ci-handoff-evidence='true'",
                "Goal Live State",
                "data-goal-live-actions='true'",
                "data-goal-live-now='true'",
                "data-goal-live-phase='true'",
                "data-goal-live-refresh='true'",
                "data-goal-live-pause='true'",
                "data-goal-live-safety='true'",
                "data-goal-live-evidence='true'",
                "data-goal-delegation-actions='true'",
                "data-goal-delegation-now='true'",
                "data-goal-delegation-latest='true'",
                "data-goal-delegation-workflow='true'",
                "data-goal-delegation-handoff='true'",
                "data-goal-delegation-safety='true'",
                "data-goal-delegation-evidence='true'",
                "data-goal-delegation-list='true'",
                "data-goal-run-actions='true'",
                "data-goal-run-now='true'",
                "data-goal-run-latest='true'",
                "data-goal-run-review='true'",
                "data-goal-run-changes='true'",
                "data-goal-run-safety='true'",
                "data-goal-run-evidence='true'",
                "data-goal-run-list='true'",
                "data-goal-approval-actions='true'",
                "data-goal-approval-now='true'",
                "data-goal-approval-pending='true'",
                "data-goal-approval-approved='true'",
                "data-goal-approval-downstream='true'",
                "data-goal-approval-safety='true'",
                "data-goal-approval-evidence='true'",
                "data-goal-approval-list='true'",
                "data-goal-incident-actions='true'",
                "data-goal-incident-now='true'",
                "data-goal-incident-open='true'",
                "data-goal-incident-first='true'",
                "data-goal-incident-recovery='true'",
                "data-goal-incident-safety='true'",
                "data-goal-incident-evidence='true'",
                "data-goal-incident-list='true'",
                "data-goal-evidence-actions='true'",
                "data-goal-evidence-now='true'",
                "data-goal-evidence-latest='true'",
                "data-goal-evidence-inventory='true'",
                "data-goal-evidence-attention='true'",
                "data-goal-evidence-safety='true'",
                "data-goal-evidence-evidence='true'",
                "data-goal-evidence-list='true'",
                "data-goal-artifact-actions='true'",
                "data-goal-artifact-open='true'",
                "data-goal-artifact-latest='true'",
                "data-goal-artifact-types='true'",
                "data-goal-artifact-inventory='true'",
                "data-goal-artifact-safety='true'",
                "data-goal-artifact-evidence='true'",
                "data-goal-artifact-list='true'",
                "data-goal-artifact-explorer-evidence='true'",
                "data-goal-artifact-filter='true'",
                "data-goal-artifact-filter-evidence='true'",
                "data-goal-artifact-reader='true'",
                "data-goal-artifact-reader-evidence='true'",
                "data-goal-artifact-groups='true'",
                "data-goal-memory-actions='true'",
                "data-goal-memory-now='true'",
                "data-goal-memory-notes='true'",
                "data-goal-memory-bank='true'",
                "data-goal-memory-pin='true'",
                "data-goal-memory-safety='true'",
                "data-goal-memory-evidence='true'",
                "data-goal-memory-list='true'",
                "data-goal-skills-actions='true'",
                "data-goal-skills-now='true'",
                "data-goal-skills-record='true'",
                "data-goal-skills-usage='true'",
                "data-goal-skills-profile='true'",
                "data-goal-skills-safety='true'",
                "data-goal-skills-evidence='true'",
                "data-goal-skills-list='true'",
                "data-goal-git-actions='true'",
                "data-goal-git-now='true'",
                "data-goal-git-branch='true'",
                "data-goal-git-changes='true'",
                "data-goal-git-proof='true'",
                "data-goal-git-safety='true'",
                "data-goal-git-evidence='true'",
                "data-goal-git-snapshot='true'",
                "data-goal-verification-actions='true'",
                "data-goal-verification-now='true'",
                "data-goal-verification-primary='true'",
                "data-goal-verification-current='true'",
                "data-goal-verification-latest='true'",
                "data-goal-verification-record='true'",
                "data-goal-verification-safety='true'",
                "data-goal-verification-evidence='true'",
                "data-goal-verification-list='true'",
                "data-goal-resume-snapshot='true'",
                "data-goal-resume-actions='true'",
                "data-goal-resume-now='true'",
                "data-goal-resume-primary='true'",
                "data-goal-resume-current='true'",
                "data-goal-resume-saved='true'",
                "data-goal-resume-artifact='true'",
                "data-goal-resume-safety='true'",
                "data-goal-resume-evidence='true'",
                "data-goal-resume-restore='true'",
                "data-goal-resume-save='true'",
                "data-goal-operator-notes-actions='true'",
                "data-goal-operator-notes-now='true'",
                "data-goal-operator-notes-primary='true'",
                "data-goal-operator-notes-artifact='true'",
                "data-goal-operator-notes-resume='true'",
                "data-goal-operator-notes-form-card='true'",
                "data-goal-operator-notes-safety='true'",
                "data-goal-operator-notes-evidence='true'",
                "data-goal-operator-notes-browser='true'",
                "data-goal-operator-notes-filter='true'",
                "data-goal-operator-notes-filter-evidence='true'",
                "data-goal-operator-notes-list='true'",
                "data-goal-operator-notes-form='true'",
                "data-goal-note-draft-form='true'",
                "data-goal-note-draft-input='true'",
                "data-goal-note-draft-reset='true'",
                "data-goal-task-closeout='true'",
                "data-goal-task-closeout-actions='true'",
                "data-goal-task-closeout-evidence='true'",
                "data-goal-remaining-work-actions='true'",
                "data-goal-remaining-work-now='true'",
                "data-goal-remaining-work-progress='true'",
                "data-goal-remaining-work-waiting='true'",
                "data-goal-remaining-work-open='true'",
                "data-goal-remaining-work-finish='true'",
                "data-goal-remaining-work-evidence='true'",
                "data-goal-remaining-work-list='true'",
                "Next Action",
                "Activity Log",
                "Memory",
                "Skills Used",
                demo.delegation_id,
                demo.coder_worktree_run_id,
                "goal_live_refresh_interval_seconds",
            ],
        ),
        (
            "/search?q=fixture-backed",
            "Global Search",
            [
                "search_scope",
                "data-search-operator-workbench='true'",
                "data-search-workbench-primary='true'",
                "data-search-state-details='true'",
                "data-search-workbench-evidence='true'",
                "Search Result Map",
                "data-search-result-map='true'",
                "data-search-result-map-cards='true'",
                "data-search-result-map-evidence='true'",
                "Search Result Filter",
                "data-search-result-filter='true'",
                "data-search-result-filter-evidence='true'",
                "data-search-command-evidence='true'",
                demo.goal_id,
                "artifact",
            ],
        ),
        (
            "/resume",
            "Resume Workspace",
            [
                "Resume Command Bar",
                "Resume Operator Workbench",
                "data-resume-state-details='true'",
                "data-resume-operator-workbench='true'",
                "data-resume-workbench-primary='true'",
                "data-resume-workbench-evidence='true'",
                "data-resume-command-evidence='true'",
                "resume_command_status</dt><dd>available",
                "resume_command_source</dt><dd>lead_goal_state",
                "resume_command_next_action</dt><dd>Create commit request",
                "resume_workbench_status</dt><dd>action_form_ready",
                "resume_workbench_source</dt><dd>lead_goal_state",
                "resume_workbench_next_action</dt><dd>Create commit request",
                "id='resume-workbench-action-form'",
                "action='/actions/coder-commit-request'",
                "resume_workspace_available",
                "resume_workspace_write_on_get",
            ],
        ),
        (
            "/workspace",
            "Workspace State",
            [
                "Workspace Operator Workbench",
                "data-workspace-operator-workbench='true'",
                "data-workspace-workbench-primary='true'",
                "data-workspace-workbench-evidence='true'",
                "data-workspace-state-details='true'",
                "data-workspace-restore-details='true'",
                "Workspace View Memory",
                "data-workspace-view-memory='true'",
                "data-workspace-view-memory-evidence='true'",
                "data-workspace-view-memory-card='open-panels'",
                "data-workspace-view-memory-key='clankeros-open-panels:'",
                "data-workspace-view-memory-card='scroll-position'",
                "data-workspace-view-memory-key='clankeros-scroll-position:'",
                "data-workspace-view-memory-card='note-drafts'",
                "data-workspace-view-memory-key='clankeros-goal-note-draft:'",
                "workspace_view_memory_status</dt><dd>available",
                "data-workspace-save-details='true'",
                "save-workspace",
                "workspace_path",
            ],
        ),
        (
            "/memory",
            "Memory Bank",
            [
                "data-memory-operator-workbench='true'",
                "data-memory-workbench-primary='true'",
                "data-memory-state-details='true'",
                "data-memory-workbench-evidence='true'",
                "Memory Pinboard",
                "data-memory-pinboard='true'",
                "data-memory-pinboard-cards='true'",
                "data-memory-pinboard-evidence='true'",
                "Memory Inventory Filter",
                "data-memory-inventory-filter='true'",
                "data-memory-inventory-filter-evidence='true'",
                "data-memory-command-evidence='true'",
                "Project Memories",
                "Generated Memories",
                "Future Work",
            ],
        ),
        (
            "/skills",
            "Skills Inventory",
            [
                "data-skills-operator-workbench='true'",
                "data-skills-workbench-primary='true'",
                "data-skills-state-details='true'",
                "data-skills-workbench-evidence='true'",
                "Skills Inventory Filter",
                "data-skills-inventory-filter='true'",
                "data-skills-inventory-filter-evidence='true'",
                "data-skills-command-evidence='true'",
                "skills_workbench_status</dt><dd>generated_ready",
                "skills_workbench_next_action</dt><dd>Review generated skill",
                "Available Skills",
                "generated_skill_storage",
                "provider_actions_taken",
            ],
        ),
        (
            "/profiles",
            "Profiles And Routing",
            [
                "data-profiles-operator-workbench='true'",
                "data-profiles-workbench-primary='true'",
                "data-profiles-state-details='true'",
                "data-profiles-workbench-evidence='true'",
                "Profile Routing Filter",
                "data-profile-routing-filter='true'",
                "data-profile-routing-filter-evidence='true'",
                "data-profiles-command-evidence='true'",
                "provider_routing_active",
                "provider_calls_taken",
            ],
        ),
        (
            f"/projects/{quote(demo.project_id)}",
            "Project",
            [
                "Project Operator Guidance",
                "Project Workflow Launchpad",
                f"/workflow?run_id={demo.coder_worktree_run_id}",
            ],
        ),
        (
            f"/delegations/{quote(demo.delegation_id)}",
            "Delegation",
            [
                "Workflow Readiness",
                "Safe Local Actions",
                "implementation_handoff_status",
            ],
        ),
        (
            f"/workflow?delegation_id={quote(demo.delegation_id)}",
            "Modern Operator Workflow",
            [
                "Workflow Operator Workbench",
                "data-workflow-operator-workbench='true'",
                "data-workflow-workbench-primary='true'",
                "data-workflow-workbench-evidence='true'",
                "data-workflow-command-evidence='true'",
                "workflow_workbench_status</dt><dd>delegation_selected",
                "workflow_workbench_next_action</dt><dd>request_commit_for_reviewed_run",
                "Workflow Command Bar",
                "data-workflow-command-bar='true'",
                "workflow_command_status</dt><dd>delegation_selected",
                "workflow_command_next_action</dt><dd>request_commit_for_reviewed_run",
                "Selected Workflow State",
                "selected_status",
                "request_commit_for_reviewed_run",
            ],
        ),
        (
            f"/workflow?run_id={quote(demo.coder_worktree_run_id)}",
            "Modern Operator Workflow",
            [
                "Workflow Operator Workbench",
                "data-workflow-operator-workbench='true'",
                "data-workflow-workbench-primary='true'",
                "data-workflow-workbench-evidence='true'",
                "data-workflow-command-evidence='true'",
                "workflow_workbench_status</dt><dd>run_selected",
                "workflow_workbench_next_action</dt><dd>request_commit_for_reviewed_run",
                "Workflow Command Bar",
                "data-workflow-command-bar='true'",
                "workflow_command_status</dt><dd>run_selected",
                "workflow_command_next_action</dt><dd>request_commit_for_reviewed_run",
                "Selected Workflow Continuation",
                "run_action_surface",
                "external_effects_created: false",
            ],
        ),
        (
            f"/runs/{quote(demo.coder_worktree_run_id)}",
            "Run",
            [
                "Run Operator Workbench",
                "Run Workflow State",
                "Run Review Gate",
                "Run Evidence Map",
                "data-run-evidence-map='true'",
                "review_gate_status</dt><dd>reviewed",
                "Run Approval Actions",
                "Coder Worktree Evidence",
                "bounded_file_validation_status",
            ],
        ),
        (
            "/approvals",
            "Approvals",
            [
                "Approval Operator Workbench",
                "data-approval-operator-workbench='true'",
                "data-approval-workbench-primary='true'",
                "data-approval-workbench-evidence='true'",
                "data-approval-command-evidence='true'",
                "data-approval-finish-details='true'",
                "Approval Queue Filter",
                "data-approval-queue-filter='true'",
                "data-approval-filter-evidence='true'",
                "approval_workbench_status</dt><dd>decision_form_ready",
                "approval_queue_status</dt><dd>available",
                demo.approval_id,
                "approve-coder-worktree",
                "Pending Worktree Approvals",
            ],
        ),
        (
            "/inbox",
            "Operator Inbox",
            [
                "Inbox Operator Workbench",
                "data-inbox-operator-workbench='true'",
                "data-inbox-workbench-primary='true'",
                "data-inbox-workbench-evidence='true'",
                "Inbox Triage Board",
                "data-inbox-triage-board='true'",
                "data-inbox-triage-cards='true'",
                "data-inbox-triage-evidence='true'",
                "Inbox Next Item Brief",
                "data-inbox-next-item-brief='true'",
                "data-inbox-next-actions='true'",
                "data-inbox-next-evidence='true'",
                "data-inbox-command-evidence='true'",
                "Inbox Queue Filter",
                "data-inbox-queue-filter='true'",
                "data-inbox-filter-evidence='true'",
                "data-inbox-finish-details='true'",
                "Pending Worktree Approvals",
                "Coder Worktree Runs",
                demo.coder_worktree_run_id,
            ],
        ),
        (
            "/incidents",
            "Incidents",
            [
                "Incident Operator Workbench",
                "data-incident-operator-workbench='true'",
                "data-incident-workbench-primary='true'",
                "data-incident-workbench-evidence='true'",
                "data-incident-command-evidence='true'",
                "data-incident-finish-details='true'",
                "incident_workbench_status</dt><dd>empty",
                "incident_triage_status</dt><dd>available",
                "incident_workbench_write_on_get</dt><dd>false",
                "incident_workbench_external_effects_created</dt><dd>false",
            ],
        ),
        (
            "/actions",
            "Safe Action Catalog",
            [
                "Action Operator Workbench",
                "data-action-operator-workbench='true'",
                "action_workbench_action_name</dt><dd>coder-commit-request",
                "Action Workflow Map",
                "data-action-workflow-map='true'",
                "data-action-workflow-actions='true'",
                "data-action-workflow-evidence='true'",
                "Current Demo Action Surfaces",
                "next_demo_action: request_commit_for_reviewed_run",
                "external_effects=none",
            ],
        ),
        (
            "/health",
            "System Health",
            [
                "Health Operator Workbench",
                "data-health-operator-workbench='true'",
                "data-health-workbench-primary='true'",
                "data-health-workbench-evidence='true'",
                "health_workbench_status_artifact_write_on_get</dt><dd>true",
                "Health Command Bar",
                "data-health-command-bar='true'",
                "data-health-command-evidence='true'",
                "data-health-diagnostics-evidence='true'",
                "health_command_status_artifact_write_on_get</dt><dd>true",
                "storage_initializes",
                "no provider calls",
                "no external mutation",
            ],
        ),
    ]
    results = []
    for route, marker, snippets in routes:
        response = render_local_app_route(root, route)
        missing_snippets = [snippet for snippet in snippets if snippet not in response.body]
        marker_found = marker in response.body
        results.append(
            {
                "route": route,
                "status": response.status,
                "required_marker": marker,
                "marker_found": marker_found,
                "expected_snippets": snippets,
                "missing_snippets": missing_snippets,
            }
        )
    ok = all(
        item["status"] == 200
        and item["marker_found"]
        and not item["missing_snippets"]
        for item in results
    )
    return {
        "status": "passed" if ok else "failed",
        "demo": {
            "project_id": demo.project_id,
            "delegation_id": demo.delegation_id,
            "run_id": demo.run_id,
            "coder_worktree_run_id": demo.coder_worktree_run_id,
        },
        "routes": results,
        "fixture_backed": True,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": NO_EXTERNAL_EFFECT_CLAIMS,
    }


def run_local_app_golden_path_smoke_test(root: Path) -> dict[str, Any]:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    AgentSystem(root).initialize()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    ensure_default_profiles(storage)

    project_name = "golden-path"
    target_repo = root / ".clanker" / "app" / "golden-path-target"
    _initialize_local_app_golden_path_repo(target_repo)
    adapter_path = _write_local_app_golden_path_scout_adapter(root)
    configure_profile_adapter(
        storage,
        "scout",
        adapter_type="shell",
        command=f"{shlex.quote(sys.executable)} {shlex.quote(str(adapter_path))}",
        input_mode="json_file",
        output_mode="json",
        timeout_seconds=30,
        working_directory="system_root",
    )

    checks: list[dict[str, Any]] = []

    def record(
        name: str,
        response: LocalAppResponse,
        *,
        expected_status: int = 200,
        snippets: list[str] | None = None,
    ) -> None:
        expected_snippets = snippets or []
        missing = [snippet for snippet in expected_snippets if snippet not in response.body]
        checks.append(
            {
                "name": name,
                "status": response.status,
                "expected_status": expected_status,
                "expected_snippets": expected_snippets,
                "missing_snippets": missing,
                "passed": response.status == expected_status and not missing,
            }
        )

    record(
        "open-home",
        render_local_app_route(root, "/"),
        snippets=["ClankerOS Local Operator"],
    )
    record(
        "open-today-first-run",
        render_local_app_route(root, "/today"),
        snippets=["Today Command Center", "First Run Guide"],
    )

    register_form = {
        "name": [project_name],
        "path": [str(target_repo)],
        "test_command": ["python3 -m pytest -q"],
        "allowed_write_roots": [str(target_repo)],
    }
    record(
        "confirm-create-project",
        render_local_app_route(
            root,
            "/actions/register-project",
            method="POST",
            form=register_form,
        ),
        expected_status=409,
        snippets=["action_confirmation_label</dt><dd>First project setup"],
    )
    record(
        "create-project",
        render_local_app_route(
            root,
            "/actions/register-project",
            method="POST",
            form={**register_form, "confirm": ["yes"]},
        ),
        snippets=["Project setup complete", "Create first goal"],
    )

    goal_prompt = "Create a fresh-user golden path proof."
    create_goal_form = {
        "project_id": [project_name],
        "prompt": [goal_prompt],
        "created_by_profile": ["planner"],
    }
    record(
        "confirm-create-goal",
        render_local_app_route(
            root,
            "/actions/create-goal",
            method="POST",
            form=create_goal_form,
        ),
        expected_status=409,
        snippets=["action_confirmation_label</dt><dd>First Goal setup"],
    )
    record(
        "create-goal",
        render_local_app_route(
            root,
            "/actions/create-goal",
            method="POST",
            form={**create_goal_form, "confirm": ["yes"]},
        ),
        snippets=["goal_created:", "Create scout delegation"],
    )

    goal = storage.latest_goal_for_project(project_name)
    goal_id = goal.id if goal is not None else ""
    tasks = storage.list_tasks(goal_id) if goal_id else []
    first_task = tasks[0] if tasks else None
    record(
        "open-today-create-action",
        render_local_app_route(root, "/today"),
        snippets=[
            "today_command_primary_action</dt><dd>Create scout delegation",
            "action='/actions/delegate'",
        ],
    )

    delegation_id = ""
    if first_task is not None:
        delegate_form = {
            "goal_id": [goal_id],
            "task_id": [first_task.id],
            "profile": ["scout"],
            "title": ["Golden path scout"],
            "requested_by": ["operator"],
            "return_to": ["/today#today-current-action"],
        }
        record(
            "confirm-next-action",
            render_local_app_route(
                root,
                "/actions/delegate",
                method="POST",
                form=delegate_form,
            ),
            expected_status=409,
            snippets=["Confirm scout delegation"],
        )
        record(
            "do-next-action",
            render_local_app_route(
                root,
                "/actions/delegate",
                method="POST",
                form={**delegate_form, "confirm": ["yes"]},
            ),
            snippets=["Scout delegation created", "Generate context pack"],
        )
        delegations = storage.list_subagent_delegations(goal_id)
        delegation_id = delegations[0].id if delegations else ""

    if delegation_id:
        context_form = {
            "delegation_id": [delegation_id],
            "return_to": ["/today#today-current-action"],
        }
        record(
            "confirm-context-pack",
            render_local_app_route(
                root,
                "/actions/context-pack",
                method="POST",
                form=context_form,
            ),
            expected_status=409,
            snippets=["Confirm context pack"],
        )
        record(
            "create-context-pack",
            render_local_app_route(
                root,
                "/actions/context-pack",
                method="POST",
                form={**context_form, "confirm": ["yes"]},
            ),
            snippets=["Context pack ready", "Run delegation"],
        )
        run_form = {
            "delegation_id": [delegation_id],
            "operator_id": ["operator"],
            "return_to": ["/today#today-current-action"],
        }
        record(
            "confirm-proof-run",
            render_local_app_route(
                root,
                "/actions/run-delegation",
                method="POST",
                form=run_form,
            ),
            expected_status=409,
            snippets=["Confirm scout run"],
        )
        record(
            "run-proof",
            render_local_app_route(
                root,
                "/actions/run-delegation",
                method="POST",
                form={**run_form, "confirm": ["yes"]},
            ),
            snippets=["Scout run finished", "implementation_handoff.md"],
        )

    completed_delegation = (
        storage.get_subagent_delegation(delegation_id) if delegation_id else None
    )
    run_metadata = (
        load_delegation_result_metadata(completed_delegation)
        if completed_delegation is not None
        else {}
    )
    proof_path_value = str(run_metadata.get("implementation_handoff_md") or "")
    proof_path = root / proof_path_value if proof_path_value else None
    proof_exists = bool(proof_path and proof_path.exists())
    if proof_path_value:
        record(
            "check-proof-artifact",
            render_local_app_route(
                root,
                f"/artifacts?path={quote(proof_path_value, safe='/.')}",
            ),
            snippets=["artifact_type", "implementation_handoff.md"],
        )
    else:
        checks.append(
            {
                "name": "check-proof-artifact",
                "status": "missing",
                "expected_status": 200,
                "expected_snippets": ["implementation_handoff.md"],
                "missing_snippets": ["implementation_handoff.md"],
                "passed": False,
            }
        )

    finish_form = {
        "open_project": [project_name],
        "open_goal": [goal_id],
        "filters": [f"goal:{goal_id}"],
        "expanded_panels": ["today,current-action,proof,resume"],
        "last_viewed_artifact": [proof_path_value],
        "resume_surface": ["/today#today-current-action"],
        "updated_by": ["golden-path-smoke"],
        "return_to": ["/resume"],
    }
    record(
        "confirm-finish-today",
        render_local_app_route(
            root,
            "/actions/save-workspace",
            method="POST",
            form=finish_form,
        ),
        expected_status=409,
        snippets=["action_confirmation_label</dt><dd>Save return point"],
    )
    record(
        "finish-today",
        render_local_app_route(
            root,
            "/actions/save-workspace",
            method="POST",
            form={**finish_form, "confirm": ["yes"]},
        ),
        snippets=["workspace_saved: .clanker/app/workspace.json", "Resume Tomorrow"],
    )
    record(
        "resume-tomorrow",
        render_local_app_route(root, "/resume"),
        snippets=["Resume Workspace", "Run coder prep", "implementation_handoff.md"],
    )

    workspace = _load_workspace_state(root)
    workspace_ok = (
        workspace.get("open_project") == project_name
        and workspace.get("open_goal") == goal_id
        and workspace.get("resume_surface") == "/today#today-current-action"
        and workspace.get("last_viewed_artifact") == proof_path_value
    )
    ok = all(item["passed"] for item in checks) and proof_exists and workspace_ok
    return {
        "status": "passed" if ok else "failed",
        "project_id": project_name,
        "goal_id": goal_id,
        "delegation_id": delegation_id,
        "proof_artifact": proof_path_value,
        "proof_exists": proof_exists,
        "workspace_resume_surface": workspace.get("resume_surface", ""),
        "workspace_last_viewed_artifact": workspace.get("last_viewed_artifact", ""),
        "workspace_ok": workspace_ok,
        "checks": checks,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": NO_EXTERNAL_EFFECT_CLAIMS,
    }


def _initialize_local_app_golden_path_repo(repo_path: Path) -> None:
    repo_path.mkdir(parents=True, exist_ok=True)
    if not (repo_path / ".git").exists():
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "clankeros@example.invalid"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "ClankerOS Smoke"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "commit.gpgsign", "false"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
    readme = repo_path / "README.md"
    if not readme.exists():
        readme.write_text("# Golden Path Target\n", encoding="utf-8")
    head = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        cwd=repo_path,
        check=False,
        capture_output=True,
    )
    if head.returncode != 0:
        subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "initial golden path target"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )


def _write_local_app_golden_path_scout_adapter(root: Path) -> Path:
    adapter_path = root / ".clanker" / "app" / "golden-path-fake-scout.py"
    adapter_path.parent.mkdir(parents=True, exist_ok=True)
    adapter_path.write_text(
        "\n".join(
            [
                "import json",
                "import sys",
                "from pathlib import Path",
                "",
                "input_path = Path(sys.argv[1])",
                "payload = json.loads(input_path.read_text(encoding='utf-8'))",
                "evidence_dir = Path(payload['evidence_dir'])",
                "(evidence_dir / 'golden-path-scout-seen.txt').write_text(",
                "    payload['delegation']['id'],",
                "    encoding='utf-8',",
                ")",
                "print(json.dumps({",
                "  'result_summary': 'Fresh-user golden path proof found the next implementation seam.',",
                "  'structured_output': {",
                "    'files': ['agent_os/local_app.py', 'agent_os/cli.py'],",
                "    'findings': ['Today exposes the next action and proof handoff.'],",
                "    'relevant_files': ['agent_os/local_app.py', 'agent_os/cli.py'],",
                "    'options': [",
                "      {'label': 'Continue with coder prep', 'files': ['agent_os/local_app.py']}",
                "    ]",
                "  }",
                "}))",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return adapter_path


