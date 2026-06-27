from __future__ import annotations

import hashlib
import html
import json
import sqlite3
import subprocess
import sys
import tempfile
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse

from agent_os.coder_prep import (
    CoderPrepError,
    list_coder_prep_packets,
    prepare_coder_from_handoff,
    prepare_coder_from_handoff_markdown,
)
from agent_os.coder_publication import (
    CoderPublicationError,
    approve_coder_publication,
    create_coder_publication_handoff,
    list_coder_publications,
    load_coder_publication_handoff_payload,
    request_coder_publication,
)
from agent_os.coder_worktree_execution import (
    CoderWorktreeApprovalError,
    CoderWorktreeCommitError,
    CoderWorktreeRunError,
    approve_coder_worktree,
    approve_coder_worktree_commit,
    coder_worktree_change_summary,
    commit_coder_worktree,
    get_coder_worktree_run,
    list_coder_worktree_approvals,
    list_coder_worktree_commit_approvals,
    list_coder_worktree_runs,
    request_coder_worktree_approval,
    request_coder_worktree_commit_approval,
    run_approved_coder_worktree,
)
from agent_os.coder_worktree_plan import (
    CoderWorktreePlanError,
    list_coder_worktree_plan_packets,
    prepare_worktree_plan_from_coder_prep,
)
from agent_os.ci_snapshot_evidence import (
    record_ci_snapshot_evidence_from_gh_status_json,
)
from agent_os.context_pack import ContextPackError, generate_context_pack
from agent_os.delegation_runner import (
    DelegationRunError,
    run_delegation,
)
from agent_os.engine import AgentSystem
from agent_os.ids import new_id
from agent_os.implementation_handoff import summarize_implementation_handoff
from agent_os.memory_entries import MemoryEntryError
from agent_os.planning import PlanningError, create_goal_lifecycle
from agent_os.project_registry import register_project
from agent_os.run_review import write_run_review
from agent_os.storage import Storage, utc_now
from agent_os.steering import collect_inbox_items
from agent_os.subagent_delegation import (
    DelegationError,
    create_subagent_delegation,
    load_delegation_result_metadata,
)


class SafeHtml(str):
    pass


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8787
MAX_ARTIFACT_BYTES = 64_000
NO_EXTERNAL_EFFECT_CLAIMS = [
    "no provider calls",
    "no network actions except local browser/server loopback",
    "no push",
    "no PR creation",
    "no deploy",
    "no external mutation",
]
NAV_ITEMS = [
    ("Dashboard", "/"),
    ("Resume", "/resume"),
    ("Goals", "/goals"),
    ("Search", "/search"),
    ("Workspace", "/workspace"),
    ("Memory", "/memory"),
    ("Skills", "/skills"),
    ("Profiles", "/profiles"),
    ("Workflow", "/workflow"),
    ("Actions", "/actions"),
    ("Verification", "/verification"),
    ("CI Evidence", "/ci-evidence"),
    ("Dogfooding", "/dogfooding"),
    ("Projects", "/projects"),
    ("Delegation Runs", "/delegation-runs"),
    ("Inbox", "/inbox"),
    ("Approvals", "/approvals"),
    ("Incidents", "/incidents"),
    ("Health", "/health"),
    ("Demo", "/demo"),
]
ROUTE_KEYBOARD_SHORTCUTS = {
    "/": "h",
    "/resume": "r",
    "/goals": "g",
    "/search": "s",
}
GLOBAL_KEYBOARD_SHORTCUTS = {
    "/": "Open command palette",
    "Escape": "Close command palette",
    "h": "Open home",
    "g": "Open goals",
    "r": "Open resume",
    "s": "Open search",
    "t": "Toggle theme",
}
WORKFLOW_STEPS = [
    ("Goal / task", "goal, tasks", "local_state", "none", "goal row, task rows"),
    ("Delegate scout", "delegate", "local_state", "task", "delegation row"),
    ("Context pack", "context-pack", "local_artifact", "delegation", "context_pack.json/.md"),
    ("Run delegation", "run-delegation", "local_execution", "delegation", "evidence packet"),
    ("Implementation handoff", "implementation-handoff", "readback", "completed delegation", "implementation_handoff.md"),
    ("Coder prep", "coder-prep / coder-prep-from-handoff", "local_artifact", "implementation_handoff.md", "coder_prep.md"),
    ("Coder worktree plan", "coder-worktree-plan", "local_artifact", "coder_prep.md", "coder_worktree_plan.md"),
    ("Worktree approval", "coder-worktree-approval", "local_approval", "coder_worktree_plan.md", "approval request"),
    ("Approved worktree execution", "run-coder-worktree", "local_execution", "approved worktree plan", "coder_worktree evidence"),
    ("Bounded-file validation", "run-coder-worktree", "local_evidence", "worktree run", "bounded_file_validation.json"),
    ("Review", "review-run", "local_artifact", "completed coder worktree run", "review.md"),
    ("Commit request", "coder-commit-request", "local_approval", "reviewed worktree run", "coder_commit_request.md"),
    ("Commit approval", "approve-coder-commit", "local_approval", "commit request", "coder_commit_decision.md"),
    ("Local commit", "commit-coder-worktree", "local_git_only", "approved commit request", "commit.json"),
    ("Publication request", "coder-publication-request", "local_approval", "local commit", "publication_request.md"),
    ("Publication approval", "approve-coder-publication", "local_approval", "publication request", "publication_decision.md"),
    ("Publication handoff", "coder-publication-handoff", "local_artifact", "approved publication", "publication_handoff.md + pr_body.md"),
    ("Manual operator push/PR outside ClankerOS", "manual git/gh", "external_manual_only", "publication handoff", "outside ClankerOS"),
    ("Goal completion", "complete-goal", "local_state", "manual publication finished", "goal status=completed"),
]
ACTION_CATALOG = [
    ("refresh-dashboard-state", "low-risk", "dashboard", "yes", "yes", "current repo/app route state", ".clanker/app/local_app_status.json"),
    ("context-pack", "local artifact", "delegation detail", "yes", "yes", "delegation_id", "context_pack.json/.md"),
    ("run-delegation", "local execution", "goal next action", "yes", "yes", "pending read-only delegation with a safe adapter", "delegation run evidence packet"),
    ("implementation-handoff", "readback", "delegation detail", "no", "no", "completed delegation", "implementation handoff status/readback"),
    ("coder-prep", "local artifact", "delegation detail", "yes", "yes", "readable implementation_handoff.md", "coder_prep.json/.md"),
    ("coder-prep-from-handoff", "local artifact", "delegation detail", "yes", "yes", "repo-relative implementation_handoff.md", "coder_prep.json/.md"),
    ("coder-worktree-plan", "local artifact", "delegation detail", "yes", "yes", "coder_prep.md", "coder_worktree_plan.json/.md"),
    ("coder-worktree-approval", "approval request", "delegation detail", "yes", "yes", "coder_worktree_plan.md", "coder_worktree_approval_request.json/.md"),
    ("approve-coder-worktree", "approval decision", "approvals", "yes", "yes", "pending worktree approval", "coder_worktree_approval_decision.json/.md"),
    ("run-coder-worktree", "bounded local execution", "goal next action", "yes", "yes", "approved worktree request plus safe local command", "coder_worktree evidence packet"),
    ("review-run", "local artifact", "goal next action", "yes", "yes", "completed coder worktree run", "runs/<source_run_id>/review.md"),
    ("coder-commit-request", "approval request", "run detail", "yes", "yes", "reviewed completed coder worktree run", "coder_commit_request.json/.md"),
    ("approve-coder-commit", "approval decision", "approvals", "yes", "yes", "pending commit approval", "coder_commit_decision.json/.md"),
    ("commit-coder-worktree", "local git only", "run detail", "yes", "yes", "approved commit request plus typed matching message", "commit.json and isolated worktree commit"),
    ("coder-publication-request", "approval request", "run detail", "yes", "yes", "isolated local commit", "publication_request.json/.md"),
    ("approve-coder-publication", "approval decision", "approvals", "yes", "yes", "pending publication approval", "publication_decision.json/.md"),
    ("coder-publication-handoff", "local artifact", "run detail", "yes", "yes", "approved publication request", "publication_handoff.json/.md plus pr_body.md"),
    ("complete-goal", "local state", "goal detail", "yes", "yes", "ready publication handoff plus operator confirmation that manual publish is done", "goal status=completed"),
    ("ci-snapshot-evidence-from-gh-json", "local evidence", "ci evidence", "yes", "yes", "operator-supplied gh run view JSON, optionally scoped to a completed job", "ci snapshot evidence JSON"),
    ("register-project", "local state", "first run / projects", "yes", "yes", "local git repo path plus default test command", "registered project row and projects/<project>/project.md"),
    ("create-goal", "local state", "first run / goals", "yes", "yes", "registered project and goal prompt", "goal row, plan, tasks, and goal artifacts"),
    ("delegate", "local state", "goal next action", "yes", "yes", "planned goal task and read-only scout profile", "subagent delegation contract JSON"),
    ("resume-goal", "local state", "goal detail", "yes", "yes", "goal status=paused", "goal status=active"),
    ("save-goal-note", "local artifact", "goal detail", "yes", "yes", "goal id plus operator note text", ".clanker/projects/<project>/goals/<goal>/operator-notes.md"),
    ("save-workspace", "local state", "workspace", "yes", "yes", "open project/goal, filters, panels, last artifact", ".clanker/app/workspace.json"),
    ("pin-memory", "local state", "memory", "yes", "yes", "proposed memory entry", "memory status=active when evidence exists"),
]


@dataclass(frozen=True)
class LocalAppResponse:
    status: int
    body: str
    content_type: str = "text/html; charset=utf-8"
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class DemoScenarioResult:
    project_id: str
    goal_id: str
    task_id: str
    delegation_id: str
    run_id: str
    coder_worktree_run_id: str
    project_root: Path
    handoff_md: Path
    coder_prep_md: Path
    coder_worktree_plan_md: Path
    approval_id: str
    execution_approval_id: str
    review_path: Path


@dataclass(frozen=True)
class DashboardNextAction:
    action: str
    href: str
    target: str
    reason: str


def validate_bind_host(host: str, *, allow_nonlocal_bind: bool = False) -> None:
    if host in LOCAL_HOSTS:
        return
    if allow_nonlocal_bind:
        return
    raise ValueError(
        f"refusing non-local bind host {host!r}; pass --allow-nonlocal-bind to opt in"
    )


def serve_local_app(
    root: Path,
    *,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    allow_nonlocal_bind: bool = False,
) -> None:
    root = root.resolve()
    validate_bind_host(host, allow_nonlocal_bind=allow_nonlocal_bind)
    AgentSystem(root).initialize()
    write_local_app_status(root, host=host, port=port)

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib hook
            response = render_local_app_route(
                root,
                self.path,
                host=host,
                port=port,
            )
            _send_response(self, response)

        def do_POST(self) -> None:  # noqa: N802 - stdlib hook
            length = int(self.headers.get("content-length", "0") or "0")
            body = self.rfile.read(length).decode("utf-8") if length else ""
            response = render_local_app_route(
                root,
                self.path,
                method="POST",
                form=parse_qs(body),
                host=host,
                port=port,
            )
            _send_response(self, response)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}"
    print(f"local_app_url: {url}", flush=True)
    print(f"bind_host: {host}", flush=True)
    print(f"port: {port}", flush=True)
    for claim in NO_EXTERNAL_EFFECT_CLAIMS:
        print(f"non_claim: {claim}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("local_app_stopped: keyboard_interrupt", flush=True)
    finally:
        server.server_close()


def render_local_app_route(
    root: Path,
    raw_path: str,
    *,
    method: str = "GET",
    form: dict[str, list[str]] | None = None,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> LocalAppResponse:
    root = root.resolve()
    AgentSystem(root).initialize()
    parsed = urlparse(raw_path)
    path = parsed.path
    query = parse_qs(parsed.query)
    notice = _one(query, "notice")

    def page(title: str, content: str, *, status: int = 200) -> LocalAppResponse:
        return _html_page(
            root,
            title,
            _notice_banner(notice) + content,
            status=status,
            current_path=raw_path,
        )

    try:
        if method == "POST":
            return _handle_post(root, path, form or {})
        if path == "/":
            return page("Dashboard", _dashboard(root, host=host, port=port))
        if path == "/goals":
            return page("Goals", _goals(root))
        if path == "/resume":
            return page("Resume", _resume_page(root))
        if path == "/search":
            return page("Search", _search_page(root, query=_one(query, "q") or ""))
        if path == "/workspace":
            return page("Workspace", _workspace_page(root))
        if path == "/memory":
            return page("Memory", _memory_page(root))
        if path == "/skills":
            return page("Skills", _skills_page(root))
        if path == "/profiles":
            return page("Profiles", _profiles_page(root))
        if path == "/workflow":
            return page(
                "Workflow",
                _workflow(
                    root,
                    delegation_id=_one(query, "delegation_id"),
                    run_id=_one(query, "run_id"),
                ),
            )
        if path == "/actions":
            return page("Actions", _actions_page(root))
        if path == "/verification":
            return page("Verification", _verification_page(root))
        if path == "/ci-evidence":
            return page("CI Evidence", _ci_evidence_page(root))
        if path == "/dogfooding":
            return page("Dogfooding", _dogfooding_page(root))
        if path == "/projects":
            return page("Projects", _projects(root))
        if path == "/delegation-runs":
            return page("Delegation Runs", _delegation_runs(root))
        if path == "/inbox":
            return page("Inbox", _inbox(root))
        if path == "/approvals":
            return page("Approvals", _approvals(root))
        if path == "/incidents":
            return page("Incidents", _incidents(root))
        if path.startswith("/goals/"):
            goal_id = unquote(path.removeprefix("/goals/"))
            return page(f"Goal {goal_id}", _goal_detail(root, goal_id))
        if path.startswith("/projects/"):
            project_id = unquote(path.removeprefix("/projects/"))
            return page(f"Project {project_id}", _project_detail(root, project_id))
        if path.startswith("/delegations/"):
            delegation_id = unquote(path.removeprefix("/delegations/"))
            return page(
                f"Delegation {delegation_id}",
                _delegation_detail(root, delegation_id),
            )
        if path.startswith("/runs/"):
            run_id = unquote(path.removeprefix("/runs/"))
            return page(f"Run {run_id}", _run_detail(root, run_id))
        if path == "/artifacts":
            return _artifact_viewer(root, _one(query, "path"), current_path=raw_path)
        if path == "/health":
            return page("Health", _health(root, host=host, port=port))
        if path == "/demo":
            return page("Demo", _demo_page(root))
        return page("Not Found", "<p>Route not found.</p>", status=404)
    except Exception as error:  # defensive app boundary
        return _html_page(
            root,
            "Local App Error",
            f"<p class='error'>{_e(type(error).__name__)}: {_e(str(error))}</p>",
            status=500,
            current_path=raw_path,
        )


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
                "demo_fixture_status: available",
                "next_dogfooding_action: request_commit_for_reviewed_run",
                f"/runs/{demo.coder_worktree_run_id}",
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
            f"/goals/{quote(demo.goal_id)}",
            "Current Phase",
            [
                "Timeline",
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
                demo.goal_id,
                "artifact",
            ],
        ),
        (
            "/resume",
            "Resume Workspace",
            [
                "resume_workspace_available",
                "resume_workspace_write_on_get",
            ],
        ),
        (
            "/workspace",
            "Workspace State",
            [
                "save-workspace",
                "workspace_path",
            ],
        ),
        (
            "/memory",
            "Memory Bank",
            [
                "Project Memories",
                "Generated Memories",
                "Future Work",
            ],
        ),
        (
            "/skills",
            "Skills Inventory",
            [
                "Available Skills",
                "generated_skill_storage",
                "provider_actions_taken",
            ],
        ),
        (
            "/profiles",
            "Profiles And Routing",
            [
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
                "Selected Workflow State",
                "selected_status",
                "request_commit_for_reviewed_run",
            ],
        ),
        (
            f"/workflow?run_id={quote(demo.coder_worktree_run_id)}",
            "Modern Operator Workflow",
            [
                "Selected Workflow Continuation",
                "run_action_surface",
                "external_effects_created: false",
            ],
        ),
        (
            f"/runs/{quote(demo.coder_worktree_run_id)}",
            "Run",
            [
                "Run Workflow State",
                "Run Review Gate",
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
                demo.approval_id,
                "approve-coder-worktree",
                "Pending Worktree Approvals",
            ],
        ),
        (
            "/inbox",
            "Operator Inbox",
            [
                "Pending Worktree Approvals",
                "Coder Worktree Runs",
                demo.coder_worktree_run_id,
            ],
        ),
        (
            "/actions",
            "Safe Action Catalog",
            [
                "Current Demo Action Surfaces",
                "next_demo_action: request_commit_for_reviewed_run",
                "external_effects=none",
            ],
        ),
        (
            "/health",
            "System Health",
            [
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


def run_demo_app_scenario(root: Path) -> DemoScenarioResult:
    root = root.resolve()
    system = AgentSystem(root)
    system.initialize()
    storage = system.storage
    project_root = root / ".clanker" / "demo" / "local-app-project"
    _ensure_demo_git_project(project_root)
    project = storage.upsert_registered_project(
        name="local-app-demo",
        root_path=str(project_root),
        default_test_command="python3 -m pytest -q",
        allowed_write_roots=[str(project_root)],
    )
    goal_id = storage.create_goal(
        project.name,
        "Demo the ClankerOS local operator app with fixture-backed state",
    )
    task_id = storage.create_task(
        goal_id=goal_id,
        project_id=project.name,
        task_type="record_learning",
        description="Inspect demo files and prepare a bounded app handoff.",
        verification_plan={"type": "manual_review"},
    )
    run_id = new_id("run")
    _write_demo_skill_record(root, storage, project.name, task_id=task_id, run_id=run_id)
    evidence_dir = root / ".clanker" / "delegations" / "pending" / "runs" / run_id / "evidence"
    delegation = storage.record_subagent_delegation(
        routing_decision_id=None,
        parent_goal_id=goal_id,
        parent_task_id=task_id,
        assigned_profile="scout",
        category="summarization",
        title="Fixture-backed local app demo scout",
        prompt="Fixture-backed local demo; no provider call.",
        input_context_json={"project_id": project.name},
        allowed_tools_json=[],
        forbidden_actions_json=["provider_call", "push", "deploy", "network"],
        expected_output_schema="file_relevance_report",
        budget_json={"mode": "fixture"},
        status="pending",
        result_summary=None,
        result_artifact_path="",
        started_at=utc_now(),
        completed_at=None,
    )
    evidence_dir = (
        root / ".clanker" / "delegations" / delegation.id / "runs" / run_id / "evidence"
    )
    evidence_dir.mkdir(parents=True, exist_ok=True)
    context_pack_json = evidence_dir / "context_pack.json"
    context_pack_md = evidence_dir / "context_pack.md"
    handoff_json = evidence_dir / "implementation_handoff.json"
    handoff_md = evidence_dir / "implementation_handoff.md"
    context_pack_json.write_text(
        json.dumps(
            {
                "context_pack_id": "context_pack_local_app_demo",
                "ranked_files": [{"path": "demo.txt", "score": 10, "reasons": ["demo fixture"]}],
                "test_hints": [{"path": "tests/test_demo.py"}],
                "grep_hits": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    context_pack_md.write_text("# Context Pack\n\n- demo.txt\n", encoding="utf-8")
    handoff_payload = {
        "schema_version": 1,
        "kind": "implementation_context_handoff",
        "delegation_id": delegation.id,
        "run_id": run_id,
        "parent_task_id": task_id,
        "expected_output_schema": "file_relevance_report",
        "result_summary": "Fixture-backed demo handoff for local app dogfooding.",
        "project": {"id": project.name, "root_path": str(project_root)},
        "context_pack": {
            "available": True,
            "id": "context_pack_local_app_demo",
            "json_path": str(context_pack_json.relative_to(root)),
            "markdown_path": str(context_pack_md.relative_to(root)),
            "ranked_file_count": 1,
            "grep_hit_count": 0,
            "top_ranked_files": ["demo.txt"],
            "test_hints": ["tests/test_demo.py"],
        },
        "validation": {
            "returned_files_in_inventory": True,
            "returned_files_missing": [],
            "top_ranked_files_referenced": ["demo.txt"],
        },
        "scout_output": {
            "files": ["demo.txt", "tests/test_demo.py"],
            "relevant_files": ["demo.txt", "tests/test_demo.py"],
            "findings": ["Fixture-backed demo files are bounded."],
        },
        "non_claims": [
            "Demo handoff is fixture-backed.",
            "No provider was called.",
            "No network action was taken.",
        ],
    }
    handoff_json.write_text(
        json.dumps(handoff_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    handoff_md.write_text(
        "# Implementation Handoff\n\n- fixture-backed: true\n- file: demo.txt\n",
        encoding="utf-8",
    )
    result_artifact = root / ".clanker" / "delegations" / f"{delegation.id}-result.json"
    result_artifact.write_text(
        json.dumps(
            {
                "delegation_id": delegation.id,
                "recorded_by": "local_app_demo",
                "result_summary": "Fixture-backed local app demo handoff prepared.",
                "structured_output": {
                    "files": ["demo.txt", "tests/test_demo.py"],
                    "findings": ["Fixture-backed demo files are bounded."],
                    "relevant_files": ["demo.txt", "tests/test_demo.py"],
                },
                "execution_run_id": run_id,
                "target_project_id": project.name,
                "implementation_handoff_json": str(handoff_json.relative_to(root)),
                "implementation_handoff_md": str(handoff_md.relative_to(root)),
                "context_pack_json": str(context_pack_json.relative_to(root)),
                "context_pack_md": str(context_pack_md.relative_to(root)),
                "context_pack_returned_files_in_inventory": True,
                "provider_calls_taken_by_clankeros": 0,
                "network_actions_taken": 0,
                "external_mutations_taken": 0,
                "execution_evidence_dir": str(evidence_dir.relative_to(root)),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    storage.complete_subagent_delegation(
        delegation.id,
        result_summary="Fixture-backed local app demo handoff prepared.",
        result_artifact_path=str(result_artifact),
        completed_at=utc_now(),
    )
    prep = prepare_coder_from_handoff(root, storage, delegation.id)
    plan = prepare_worktree_plan_from_coder_prep(root, storage, delegation.id)
    approval = request_coder_worktree_approval(
        root,
        storage,
        delegation.id,
        requested_by="operator",
        note="Demo pending approval for inbox and approvals dogfooding.",
    ).approval
    execution_approval = request_coder_worktree_approval(
        root,
        storage,
        delegation.id,
        requested_by="local_app_demo",
        note="Demo execution approval for fixture-backed worktree run.",
        force_new=True,
    ).approval
    approve_coder_worktree(
        root,
        storage,
        execution_approval.id,
        decided_by="local_app_demo",
        note="Approve fixture-backed demo worktree execution.",
    )
    coder_run = run_approved_coder_worktree(
        root,
        storage,
        delegation.id,
        command="python3 scripts/change_demo.py",
        verify=True,
    ).run
    review_path = root / "runs" / run_id / "review.md"
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(
        "\n".join(
            [
                "# Demo Run Review",
                "",
                f"- source_run_id: {run_id}",
                f"- coder_worktree_run_id: {coder_run.id}",
                "- review_status: fixture_reviewed",
                "- changed_files_within_allowed_files: true",
                "- non_claim: fixture review does not commit, push, deploy, call providers, or use the network.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_local_app_status(root, host=DEFAULT_HOST, port=DEFAULT_PORT)
    return DemoScenarioResult(
        project_id=project.name,
        goal_id=goal_id,
        task_id=task_id,
        delegation_id=delegation.id,
        run_id=run_id,
        coder_worktree_run_id=coder_run.id,
        project_root=project_root,
        handoff_md=handoff_md,
        coder_prep_md=prep.markdown_path,
        coder_worktree_plan_md=plan.markdown_path,
        approval_id=approval.id,
        execution_approval_id=execution_approval.id,
        review_path=review_path,
    )


def _write_demo_skill_record(
    root: Path,
    storage: Storage,
    project_id: str,
    *,
    task_id: str,
    run_id: str,
) -> None:
    skill_path = root / ".clanker" / "skills" / "local-files" / "SKILL.md"
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "---",
            "name: local-files",
            "description: Fixture-backed local file inspection skill for the ClankerOS demo.",
            "---",
            "",
            "# local-files",
            "",
            "## When To Use",
            "",
            "- Inspect local project files for a bounded ClankerOS goal.",
            "- Prepare a deterministic local-app demo handoff without provider calls.",
            "",
            "## Verification Steps",
            "",
            "- Confirm referenced files are inside the registered demo project.",
            "- Confirm provider_calls_taken_by_clankeros remains 0.",
            "- Confirm network_actions_taken remains 0.",
            "",
            "## Demo Metadata",
            "",
            f"- project_id: {project_id}",
            f"- source_task_id: {task_id}",
            f"- source_run_id: {run_id}",
            "- status: active",
            "- generated_for_demo: true",
            "",
        ]
    )
    skill_path.write_text(content, encoding="utf-8")
    skill = storage.record_skill(
        project_id=project_id,
        name="local-files",
        description="Fixture-backed local file inspection skill for the ClankerOS demo.",
        path=str(skill_path),
        status="active",
        created_by_profile="local_app_demo",
        source_run_id=run_id,
        source_task_id=task_id,
        verification_status="fixture_demo",
    )
    storage.record_skill_version(
        skill_id=skill.id,
        version=1,
        content_hash=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        path=str(skill_path),
        change_summary="Seed fixture-backed local-files skill for demo app surfaces.",
        verification_status="fixture_demo",
    )


def write_local_app_status(root: Path, *, host: str, port: int) -> Path:
    root = root.resolve()
    state = _repo_state(root)
    warnings = _warning_items(state, host)
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": host,
        "port": port,
        "repo_root": str(root),
        "branch": state["branch"],
        "commit": state["commit"],
        "dirty_tracked_files": state["dirty_tracked_files"],
        "untracked_files": state["untracked_files"],
        "warnings": warnings,
        "routes_available": ["/", "/goals", "/goals/<id>", "/search", "/workspace", "/memory", "/skills", "/profiles", "/workflow", "/actions", "/verification", "/ci-evidence", "/dogfooding", "/projects", "/delegation-runs", "/delegations/<id>", "/runs/<id>", "/inbox", "/approvals", "/incidents", "/artifacts", "/health", "/demo"],
        "supported_workflow_stages": [step[0] for step in WORKFLOW_STEPS],
        "non_claims": NO_EXTERNAL_EFFECT_CLAIMS,
        "known_gaps": [
            "No authentication for localhost MVP.",
            "Worktree execution remains CLI-first except for fixture-backed demo setup.",
            "Local commit action requires an approved commit request, typed matching message, and explicit confirmation.",
            "Publication push and PR creation are displayed as manual commands only.",
        ],
    }
    path = root / ".clanker" / "app" / "local_app_status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _dashboard(root: Path, *, host: str, port: int) -> str:
    state = _repo_state(root)
    storage = _storage(root)
    rows = _summary_rows(root, storage)
    warnings = _warning_items(state, host)
    next_action = _dashboard_next_action(root, storage)
    return "".join(
        [
            _home_dashboard(root, storage, next_action),
            _warnings(warnings),
            "<section><h2>Repository</h2>",
            _kv(
                [
                    ("root", str(root)),
                    ("branch", state["branch"]),
                    ("commit", state["commit"]),
                    ("ahead_of_origin_main", str(state["ahead_of_origin_main"]).lower()),
                    ("dirty_tracked_files", str(len(state["dirty_tracked_files"]))),
                    ("untracked_files", ", ".join(state["untracked_files"]) or "none"),
                    ("local_url", f"http://{host}:{port}"),
                ]
            ),
            "</section>",
            "<section><h2>Dashboard Refresh</h2>",
            "<p class='muted'>Refresh the local app status artifact from current repository and route state.</p>",
            "<form method='post' action='/actions/refresh-dashboard-state'>"
            "<input type='hidden' name='requested_by' value='operator'>"
            "<button type='submit'>refresh-dashboard-state</button>"
            "</form>",
            "</section>",
            _dashboard_verification_snapshot(root),
            _dashboard_dogfooding_snapshot(root),
            _dashboard_goal_snapshot(root),
            "<section><h2>Modern Workflow</h2>",
            "<p><a href='/workflow'>Open workflow stepper</a></p>",
            _workflow_list(compact=True),
            "</section>",
            _list_section("Projects", rows["projects"], "/projects"),
            _list_section("Recent Goals", rows["goals"], "/goals"),
            _list_section("Recent Tasks", rows["tasks"]),
            _list_section("Recent Delegations", rows["delegations"]),
            _list_section("Recent Delegation Runs", rows["delegation_runs"], "/delegation-runs"),
            _list_section("Recent Implementation Handoffs", rows["implementation_handoffs"]),
            _list_section("Recent Coder Worktree Runs", rows["coder_runs"]),
            _list_section("Recent Commit Requests / Local Commits", rows["commit_requests"]),
            _list_section("Recent Publication Requests", rows["publication_requests"]),
            _list_section("Recent Publication Handoffs", rows["publication_handoffs"]),
            _list_section("Operator Inbox", rows["inbox"], "/inbox"),
            _list_section("Pending Approvals", rows["approvals"], "/approvals"),
            _list_section("Incidents / Recommendations", rows["incidents"], "/incidents"),
            _dashboard_next_action_section(next_action),
        ]
    )


def _home_dashboard(
    root: Path,
    storage: Storage,
    next_action: DashboardNextAction,
) -> str:
    rows = _goal_rows(storage, limit=100)
    active = [row for row in rows if _goal_bucket(row) == "active"]
    paused = [row for row in rows if _goal_bucket(row) == "paused"]
    completed = [row for row in rows if _goal_bucket(row) == "completed"]
    lead_goal = active[0] if active else (paused[0] if paused else (completed[0] if completed else None))
    lead_lines: list[tuple[str, str | SafeHtml]] = [
        ("home_active_goals", str(len(active))),
        ("home_paused_goals", str(len(paused))),
        ("home_completed_goals", str(len(completed))),
        ("home_recent_activity_items", str(len(_home_recent_activity_items(root, storage)))),
        ("home_next_action", next_action.action),
        ("home_dashboard_goal_first", "true"),
    ]
    if lead_goal is not None:
        lead_state = _goal_state(root, storage, str(lead_goal["id"]))
        lead_next = _goal_next_action(root, lead_state)
        lead_lines.extend(
            [
                ("lead_goal", SafeHtml(f"<a href='/goals/{quote(str(lead_goal['id']))}'>{_e(lead_goal['title'] or lead_goal['description'])}</a>")),
                ("lead_goal_phase", _goal_current_phase(lead_state)),
                ("lead_goal_next_action", lead_next.action),
            ]
        )
    else:
        lead_lines.append(("lead_goal", "none"))

    sections = [
        "<section class='hero'><h1>Goal-First Home</h1>",
        "<p>Daily operating board for goals, activity, inbox, recommendations, and incidents.</p>",
        _kv(lead_lines),
        _non_claim_banner(),
        "</section>",
        _home_start_here(root, storage, lead_goal),
        _home_day_plan(root, storage, lead_goal),
        _home_attention_brief(root, storage, lead_goal),
        _home_focus_queue(root, storage, active=active, paused=paused),
        _home_verification_handoff(root),
        _home_goal_board(root, storage, active=active, paused=paused, completed=completed),
        _home_resume_workspace(root, lead_goal),
        _home_recent_activity(root, storage),
        _home_inbox(root),
        _home_recommendations(storage),
        _home_incidents(storage),
    ]
    if not _first_run_progress(root, storage)["complete"]:
        sections.append(_first_run_panel(root, storage))
    return "".join(sections)


def _home_start_here(root: Path, storage: Storage, lead_goal: sqlite3.Row | None) -> str:
    workspace = _load_workspace_state(root)
    open_project = str(workspace.get("open_project") or "").strip()
    open_goal = str(workspace.get("open_goal") or "").strip()
    filters = str(workspace.get("filters") or "").strip()
    expanded = str(workspace.get("expanded_panels") or "").strip()
    last_artifact = str(workspace.get("last_viewed_artifact") or "").strip()
    readiness = _workspace_resume_readiness(
        root,
        open_project=open_project,
        open_goal=open_goal,
        filters=filters,
        expanded=expanded,
        last_artifact=last_artifact,
    )
    ci_record = _latest_ci_evidence_record(root)
    if ci_record is None:
        ci_status = "missing"
        ci_source = "none"
    else:
        ci_source, record = ci_record
        ci_status = str(record.status)

    rows: list[tuple[str, str | SafeHtml]] = [
        ("start_here_resume_status", str(readiness["status"])),
        ("start_here_resume_ready", str(readiness["ready"]).lower()),
        ("start_here_resume_surface", SafeHtml("<a href='/resume'>/resume</a>")),
        ("start_here_ci_status", ci_status),
        ("start_here_ci_source", ci_source),
        ("start_here_ci_surface", SafeHtml("<a href='/verification'>/verification</a>")),
        ("start_here_write_on_get", "false"),
        ("start_here_external_effects_created", "false"),
        ("start_here_network_actions_taken", "0"),
    ]
    lines: list[str] = []
    if lead_goal is None:
        first_run = _first_run_progress(root, storage)
        primary_surface = first_run["next_surface"]
        rows.extend(
            [
                ("start_here_mode", "first_run"),
                ("start_here_primary_goal", "none"),
                ("start_here_current_phase", "First run"),
                ("start_here_primary_action", first_run["next_action"]),
                ("start_here_primary_surface", primary_surface),
                ("start_here_reason", first_run["next_reason"]),
                ("start_here_progress", f"first_run_step={first_run['current_step']}"),
                ("start_here_waiting_items", "0"),
            ]
        )
        lines.extend(
            [
                f"start_here_now: {_e(first_run['next_action'])}",
                f"start_here_click: {primary_surface}",
                "start_here_attention: create the first local project and goal from the browser",
                f"start_here_resume: readiness={_e(str(readiness['status']))} surface=<a href='/resume'>/resume</a>",
                f"start_here_ci: status={_e(ci_status)} source={_e(ci_source)} surface=<a href='/verification'>/verification</a>",
            ]
        )
    else:
        goal_id = str(lead_goal["id"])
        state = _goal_state(root, storage, goal_id)
        phase = _goal_current_phase(state)
        next_action = _goal_next_action(root, state)
        open_incidents = len([item for item in state["incidents"] if item["status"] == "open"])
        open_recommendations = len(
            [item for item in state["recommendations"] if item["status"] == "open"]
        )
        pending_approvals = (
            _count_status(state["worktree_approvals"], "pending_operator_approval")
            + _count_status(state["commit_approvals"], "pending_operator_approval")
            + _count_status(state["publications"], "pending_operator_approval")
        )
        waiting_items = open_incidents + open_recommendations + pending_approvals
        label = str(lead_goal["title"] or lead_goal["description"] or goal_id)
        rows.extend(
            [
                ("start_here_mode", "goal"),
                ("start_here_primary_goal", SafeHtml(f"<a href='/goals/{quote(goal_id)}'>{_e(label)}</a>")),
                ("start_here_current_phase", phase),
                ("start_here_primary_action", next_action.action),
                ("start_here_primary_surface", SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>")),
                ("start_here_reason", next_action.reason),
                ("start_here_progress", _goal_progress_label(state)),
                ("start_here_waiting_items", str(waiting_items)),
                ("start_here_pending_approvals", str(pending_approvals)),
                ("start_here_open_incidents", str(open_incidents)),
                ("start_here_open_recommendations", str(open_recommendations)),
            ]
        )
        lines.extend(
            [
                f"start_here_now: {_e(next_action.action)}",
                f"start_here_click: <a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>",
                f"start_here_attention: {_e(_goal_operator_attention(phase, next_action))}",
                f"start_here_resume: readiness={_e(str(readiness['status']))} surface=<a href='/resume'>/resume</a>",
                f"start_here_waiting: approvals={pending_approvals} incidents={open_incidents} recommendations={open_recommendations}",
                f"start_here_ci: status={_e(ci_status)} source={_e(ci_source)} surface=<a href='/verification'>/verification</a>",
            ]
        )
    return "".join(
        [
            "<section class='panel home-start-here' data-home-start-here='true'><h2>Start Here</h2>",
            "<p class='muted'>One scan-friendly readback for the next click, resume posture, blockers, and CI handoff.</p>",
            _kv(rows),
            _ul(lines),
            "</section>",
        ]
    )


def _home_day_plan(root: Path, storage: Storage, lead_goal: sqlite3.Row | None) -> str:
    workspace = _load_workspace_state(root)
    open_goal = str(workspace.get("open_goal") or "").strip()
    open_project = str(workspace.get("open_project") or "").strip()
    filters = str(workspace.get("filters") or "").strip()
    expanded = str(workspace.get("expanded_panels") or "").strip()
    last_artifact = str(workspace.get("last_viewed_artifact") or "").strip()
    readiness = _workspace_resume_readiness(
        root,
        open_project=open_project,
        open_goal=open_goal,
        filters=filters,
        expanded=expanded,
        last_artifact=last_artifact,
    )
    first_run = _first_run_progress(root, storage)
    rows: list[tuple[str, str | SafeHtml]] = [
        ("home_day_plan_source", "goal_state_and_workspace"),
        ("home_day_plan_resume_ready", str(readiness["ready"]).lower()),
        ("home_day_plan_resume_status", str(readiness["status"])),
        ("home_day_plan_resume_surface", SafeHtml("<a href='/resume'>/resume</a>")),
        ("home_day_plan_write_on_get", "false"),
        ("home_day_plan_external_effects_created", "false"),
    ]
    lines: list[str] = []
    if lead_goal is None:
        rows.extend(
            [
                ("home_day_plan_status", "first_run"),
                ("home_day_plan_primary_goal", "none"),
                ("home_day_plan_current_phase", "First run"),
                ("home_day_plan_next_action", first_run["next_action"]),
                ("home_day_plan_next_surface", SafeHtml(f"<a href='{_e(first_run['next_surface'])}'>{_e(first_run['next_surface'])}</a>")),
                ("home_day_plan_waiting_items", "0"),
                ("home_day_plan_finish_status", "not_ready_until_goal_exists"),
                ("home_day_plan_finish_action", "save-workspace"),
                ("home_day_plan_finish_form_available", "false"),
            ]
        )
        lines.extend(
            [
                f"day_plan_now: {_e(first_run['next_action'])}",
                f"day_plan_next_surface: <a href='{_e(first_run['next_surface'])}'>{_e(first_run['next_surface'])}</a>",
                "day_plan_end_of_day_resume: not_ready_until_workspace_saved",
            ]
        )
        finish_form = ""
    else:
        goal_id = str(lead_goal["id"])
        state = _goal_state(root, storage, goal_id)
        goal = state["goal"]
        phase = _goal_current_phase(state)
        next_action = _goal_next_action(root, state)
        latest_artifact = _goal_latest_artifact_path(root, state)
        saved_goal_matches_lead = open_goal == goal_id
        saved_project_matches_lead = open_project == str(goal.project_id)
        saved_artifact_matches_latest = bool(latest_artifact) and last_artifact == latest_artifact
        finish_ready = (
            saved_goal_matches_lead
            and saved_project_matches_lead
            and (saved_artifact_matches_latest or not latest_artifact)
        )
        finish_status = "ready" if finish_ready else "needs_workspace_save"
        open_tasks = len([task for task in state["tasks"] if task.status != "completed"])
        open_incidents = len([row for row in state["incidents"] if row["status"] == "open"])
        open_recommendations = len([row for row in state["recommendations"] if row["status"] == "open"])
        pending_approvals = (
            _count_status(state["worktree_approvals"], "pending_operator_approval")
            + _count_status(state["commit_approvals"], "pending_operator_approval")
            + _count_status(state["publications"], "pending_operator_approval")
        )
        waiting_items = open_incidents + open_recommendations + pending_approvals
        rows.extend(
            [
                ("home_day_plan_status", "goal_ready"),
                ("home_day_plan_primary_goal", SafeHtml(f"<a href='/goals/{quote(goal_id)}'>{_e(lead_goal['title'] or lead_goal['description'] or goal_id)}</a>")),
                ("home_day_plan_current_phase", phase),
                ("home_day_plan_next_action", next_action.action),
                ("home_day_plan_next_surface", SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>")),
                ("home_day_plan_operator_attention", _goal_operator_attention(phase, next_action)),
                ("home_day_plan_progress", _goal_progress_label(state)),
                ("home_day_plan_open_tasks", str(open_tasks)),
                ("home_day_plan_open_incidents", str(open_incidents)),
                ("home_day_plan_open_recommendations", str(open_recommendations)),
                ("home_day_plan_pending_approvals", str(pending_approvals)),
                ("home_day_plan_waiting_items", str(waiting_items)),
                ("home_day_plan_finish_status", finish_status),
                ("home_day_plan_finish_action", "save-workspace"),
                ("home_day_plan_finish_form_available", "true"),
                ("home_day_plan_finish_confirmation_required", "true"),
                ("home_day_plan_saved_goal_matches_lead", str(saved_goal_matches_lead).lower()),
                ("home_day_plan_saved_project_matches_lead", str(saved_project_matches_lead).lower()),
                ("home_day_plan_saved_artifact_matches_latest", str(saved_artifact_matches_latest).lower()),
                (
                    "home_day_plan_latest_artifact",
                    SafeHtml(_artifact_link(latest_artifact)) if latest_artifact else "none",
                ),
                (
                    "home_day_plan_finish_return_to",
                    SafeHtml("<a href='/'>/</a>"),
                ),
            ]
        )
        lines.extend(
            [
                f"day_plan_now: {_e(next_action.action)}",
                f"day_plan_current_phase: {_e(phase)}",
                f"day_plan_goal_surface: <a href='/goals/{quote(goal_id)}'>/goals/{_e(goal_id)}</a>",
                f"day_plan_next_surface: <a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>",
                f"day_plan_waiting: approvals={pending_approvals} incidents={open_incidents} recommendations={open_recommendations}",
                f"day_plan_end_of_day_resume: {'ready' if readiness['ready'] else 'needs_saved_workspace'}",
                f"day_plan_finish: status={_e(finish_status)} action=save-workspace return_to=/",
            ]
        )
        finish_form = "".join(
            [
                "<h3>Finish Today</h3>",
                "<p class='muted'>Save the lead goal, current day-plan filters, expanded panels, and latest artifact as tomorrow's resume point. This writes only `.clanker/app/workspace.json` after confirmation.</p>",
                _input_form(
                    "save-workspace",
                    {
                        "open_project": str(goal.project_id),
                        "open_goal": goal_id,
                        "return_to": "/",
                    },
                    {
                        "filters": f"goal:{goal_id}",
                        "expanded_panels": "day-plan,daily-loop,next-action,timeline,evidence,artifacts,notes",
                        "last_viewed_artifact": latest_artifact,
                        "updated_by": "home-day-plan",
                    },
                ),
            ]
        )
    return "".join(
        [
            "<section class='panel home-day-plan' data-home-day-plan='true'><h2>Home Day Plan</h2>",
            "<p class='muted'>Start, continue, unblock, and finish the lead goal from the daily Home board.</p>",
            _kv(rows),
            _ul(lines),
            finish_form,
            "</section>",
        ]
    )


def _home_attention_brief(root: Path, storage: Storage, lead_goal: sqlite3.Row | None) -> str:
    inbox = collect_inbox_items(root)
    pending_approvals = (
        len(inbox["pending_approvals"])
        + len(inbox["coder_worktree_approvals"])
        + len(inbox["coder_worktree_commit_approvals"])
        + len(inbox["coder_publication_requests"])
    )
    open_incidents = len(inbox["open_incidents"])
    open_recommendations = len(storage.list_recent_task_recommendations(limit=20))
    inbox_items = int(inbox["count"])
    review_items = pending_approvals + open_incidents + open_recommendations
    ci_record = _latest_ci_evidence_record(root)
    if ci_record is None:
        ci_source = "none"
        ci_status = "missing"
    else:
        ci_source, record = ci_record
        ci_status = str(record.status)
    lead_goal_value: str | SafeHtml = "none"
    if lead_goal is not None:
        lead_goal_id = str(lead_goal["id"])
        lead_label = str(lead_goal["title"] or lead_goal["description"] or lead_goal_id)
        lead_goal_value = SafeHtml(
            f"<a href='/goals/{quote(lead_goal_id)}'>{_e(_compact_label(lead_label, 72))}</a>"
        )

    if open_incidents:
        status = "needs_incident_review"
        primary_action = "Review incidents"
        primary_href = "/incidents"
        reason = "open_incidents"
    elif pending_approvals:
        status = "needs_approval_review"
        primary_action = "Review approvals"
        primary_href = "/approvals"
        reason = "pending_approvals"
    elif open_recommendations:
        status = "needs_recommendation_review"
        primary_action = "Review recommendations"
        primary_href = "/incidents"
        reason = "open_recommendations"
    elif inbox_items:
        status = "needs_inbox_review"
        primary_action = "Review inbox"
        primary_href = "/inbox"
        reason = "inbox_items"
    elif lead_goal is None:
        status = "first_run"
        primary_action = "Register ClankerOS project"
        primary_href = "/goals"
        reason = "no_goal_available"
    elif ci_status != "success":
        status = "needs_ci_proof"
        primary_action = "Review verification handoff"
        primary_href = "/verification"
        reason = "ci_proof_not_success"
    elif lead_goal is not None:
        state = _goal_state(root, storage, str(lead_goal["id"]))
        next_action = _goal_next_action(root, state)
        status = "clear_to_continue_goal"
        primary_action = next_action.action
        primary_href = next_action.href
        reason = "no_attention_blockers"

    return "".join(
        [
            "<section class='panel home-attention-brief' data-home-attention-brief='true'><h2>Home Attention Brief</h2>",
            "<p class='muted'>A read-only triage pass for approvals, incidents, recommendations, inbox, and proof before deeper goal work.</p>",
            _kv(
                [
                    ("home_attention_status", status),
                    ("home_attention_primary_action", primary_action),
                    (
                        "home_attention_primary_surface",
                        SafeHtml(f"<a href='{_e(primary_href)}'>{_e(primary_href)}</a>"),
                    ),
                    ("home_attention_reason", reason),
                    ("home_attention_lead_goal", lead_goal_value),
                    ("home_attention_review_items", str(review_items)),
                    ("home_attention_inbox_items", str(inbox_items)),
                    ("home_attention_pending_approvals", str(pending_approvals)),
                    ("home_attention_open_incidents", str(open_incidents)),
                    ("home_attention_open_recommendations", str(open_recommendations)),
                    ("home_attention_ci_status", ci_status),
                    ("home_attention_ci_source", ci_source),
                    ("home_attention_ci_surface", SafeHtml("<a href='/verification'>/verification</a>")),
                    ("home_attention_inbox_surface", SafeHtml("<a href='/inbox'>/inbox</a>")),
                    ("home_attention_approval_surface", SafeHtml("<a href='/approvals'>/approvals</a>")),
                    ("home_attention_incident_surface", SafeHtml("<a href='/incidents'>/incidents</a>")),
                    ("home_attention_write_on_get", "false"),
                    ("home_attention_github_status_fetch", "none"),
                    ("home_attention_provider_calls_taken_by_clankeros", "0"),
                    ("home_attention_network_actions_taken", "0"),
                    ("home_attention_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"home_attention_now: {_e(primary_action)}",
                    f"home_attention_click: <a href='{_e(primary_href)}'>{_e(primary_href)}</a>",
                    f"home_attention_review: approvals={pending_approvals} incidents={open_incidents} recommendations={open_recommendations} inbox={inbox_items}",
                    f"home_attention_ci: status={_e(ci_status)} source={_e(ci_source)} surface=<a href='/verification'>/verification</a>",
                    "home_attention_safety: read-only local triage; confirmed actions remain on target surfaces",
                ]
            ),
            "</section>",
        ]
    )


def _home_focus_queue(
    root: Path,
    storage: Storage,
    *,
    active: list[sqlite3.Row],
    paused: list[sqlite3.Row],
) -> str:
    rows = active + paused
    lines = [_home_focus_queue_line(root, storage, row) for row in rows[:8]]
    if not lines:
        lines = [
            "focus_queue_status: first_run_ready",
            "focus_queue_next_surface: <a href='/goals'>/goals</a>",
            "focus_queue_next_action: Register ClankerOS project",
        ]
    return "".join(
        [
            "<section><h2>Home Focus Queue</h2>",
            _kv(
                [
                    ("focus_queue_source", "goal_state_next_actions"),
                    ("focus_queue_items", str(len(active) + len(paused))),
                    ("focus_queue_active_goals", str(len(active))),
                    ("focus_queue_paused_goals", str(len(paused))),
                    ("focus_queue_write_on_get", "false"),
                    ("focus_queue_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _home_focus_queue_line(root: Path, storage: Storage, row: sqlite3.Row) -> str:
    goal_id = str(row["id"])
    state = _goal_state(root, storage, goal_id)
    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    open_incidents = len([item for item in state["incidents"] if item["status"] == "open"])
    open_recommendations = len(
        [item for item in state["recommendations"] if item["status"] == "open"]
    )
    pending_approvals = (
        _count_status(state["worktree_approvals"], "pending_operator_approval")
        + _count_status(state["commit_approvals"], "pending_operator_approval")
        + _count_status(state["publications"], "pending_operator_approval")
    )
    waiting_items = open_incidents + open_recommendations + pending_approvals
    label = str(row["title"] or row["description"] or goal_id)
    return (
        f"focus_queue_item: <a href='/goals/{quote(goal_id)}'>{_e(_compact_label(label, 56))}</a> "
        f"phase={_e(phase)} next_action={_e(next_action.action)} "
        f"surface=<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a> "
        f"progress={_e(_goal_progress_label(state))} waiting={waiting_items} "
        f"approvals={pending_approvals} incidents={open_incidents} recommendations={open_recommendations}"
    )


def _home_verification_handoff(root: Path) -> str:
    repo = _repo_state(root)
    full_commit = _git(root, ["rev-parse", "HEAD"]) or repo["commit"]
    latest_record = _latest_ci_evidence_record(root)
    lines: list[tuple[str, str | SafeHtml]] = [
        ("home_verification_source", "github_actions_operator_supplied_evidence"),
        ("home_verification_surface", SafeHtml("<a href='/verification'>/verification</a>")),
        ("home_ci_evidence_surface", SafeHtml("<a href='/ci-evidence'>/ci-evidence</a>")),
        ("home_ci_current_branch", repo["branch"]),
        ("home_ci_current_commit", full_commit),
        ("home_ci_github_status_fetch", "none"),
        ("home_ci_app_network_actions_taken", "0"),
        ("home_ci_external_mutations_taken", "0"),
        ("home_ci_write_on_get", "false"),
    ]
    if latest_record is None:
        lines.extend(
            [
                ("home_latest_ci_status", "missing"),
                ("home_latest_ci_record_source", "none"),
                (
                    "home_ci_next_action",
                    "wait_for_github_actions_success_then_record_ci_snapshot_or_deploy_evidence",
                ),
            ]
        )
    else:
        source_kind, record = latest_record
        result = record.result_json if isinstance(record.result_json, dict) else {}
        branch_matches = record.branch_name == repo["branch"]
        commit_matches = _commit_refs_match(record.commit_sha, full_commit, repo["commit"])
        lines.extend(
            [
                ("home_latest_ci_source", source_kind),
                ("home_latest_ci_status", record.status),
                ("home_latest_ci_provider", record.provider),
                ("home_latest_ci_branch", record.branch_name),
                ("home_latest_ci_commit", record.commit_sha),
                ("home_latest_ci_external_run_id", record.external_run_id),
                (
                    "home_latest_ci_url",
                    SafeHtml(f"<a href='{_e(record.external_url)}'>{_e(record.external_url)}</a>"),
                ),
                ("home_latest_ci_record_source", "operator_supplied"),
                ("home_latest_ci_branch_matches_current", str(branch_matches).lower()),
                ("home_latest_ci_commit_matches_current", str(commit_matches).lower()),
                (
                    "home_latest_ci_matches_current_checkout",
                    str(branch_matches and commit_matches).lower(),
                ),
                ("home_latest_ci_network_actions_taken", str(result.get("network_actions_taken", "unknown"))),
                (
                    "home_latest_ci_external_mutations_taken",
                    str(result.get("external_mutations_taken", "unknown")),
                ),
            ]
        )
    handoff_lines = [
        *_ci_snapshot_handoff_lines(root, key_prefix="home_ci_snapshot_"),
        "home_ci_proof_boundary: completed passing GitHub Actions run plus operator-supplied local record",
        "home_ci_fast_smoke_boundary: Fast smoke verification is early route/CLI proof only",
        "home_ci_full_suite_location: GitHub Actions",
    ]
    return "".join(
        [
            "<section><h2>Home Verification Handoff</h2>",
            _kv(lines),
            _ul(handoff_lines),
            "</section>",
        ]
    )


def _home_goal_board(
    root: Path,
    storage: Storage,
    *,
    active: list[sqlite3.Row],
    paused: list[sqlite3.Row],
    completed: list[sqlite3.Row],
) -> str:
    return "".join(
        [
            "<section><h2>Home Goal Board</h2>",
            _kv(
                [
                    ("active_goals", str(len(active))),
                    ("paused_goals", str(len(paused))),
                    ("completed_goals", str(len(completed))),
                    ("goal_board_surface", SafeHtml("<a href='/goals'>/goals</a>")),
                ]
            ),
            "<div class='grid'>",
            _home_goal_lane(root, storage, "Active Goals", active),
            _home_goal_lane(root, storage, "Paused Goals", paused),
            _home_goal_lane(root, storage, "Completed Goals", completed),
            "</div>",
            "</section>",
        ]
    )


def _home_goal_lane(
    root: Path,
    storage: Storage,
    title: str,
    rows: list[sqlite3.Row],
) -> str:
    return "".join(
        [
            "<div class='panel'>",
            f"<h3>{_e(title)}</h3>",
            _ul([_goal_index_line(root, storage, row) for row in rows[:6]]),
            "</div>",
        ]
    )


def _home_resume_workspace(root: Path, lead_goal: sqlite3.Row | None) -> str:
    state = _load_workspace_state(root)
    open_project = str(state.get("open_project") or "").strip()
    open_goal = str(state.get("open_goal") or "").strip()
    filters = str(state.get("filters") or "").strip()
    expanded = str(state.get("expanded_panels") or "").strip()
    last_artifact = str(state.get("last_viewed_artifact") or "").strip()
    workspace_path = ".clanker/app/workspace.json"
    workspace_path_readback = (
        _artifact_link(workspace_path) if _workspace_path(root).exists() else workspace_path
    )
    lines: list[str] = [
        f"workspace_path: {workspace_path_readback}",
        f"workspace_updated_at: {_e(state.get('updated_at') or 'never')}",
        f"workspace_filters: {_e(filters or 'none')}",
        f"workspace_expanded_panels: {_e(expanded or 'none')}",
    ]
    if open_goal:
        lines.append(f"resume_goal: <a href='/goals/{quote(open_goal)}'>{_e(open_goal)}</a>")
    if open_project:
        lines.append(f"resume_project: <a href='/projects/{quote(open_project)}'>{_e(open_project)}</a>")
    if last_artifact:
        lines.append(f"resume_artifact: {_artifact_link(last_artifact)}")
    lines.extend(_home_resume_next_action_lines(root, open_goal))
    if not any([open_goal, open_project, last_artifact]):
        lines.append("workspace_status: no_saved_workspace")
    lines.append("resume_surface: <a href='/resume'>/resume</a>")
    lines.append("workspace_surface: <a href='/workspace'>/workspace</a>")

    form = ""
    if lead_goal is not None:
        lead_goal_id = str(lead_goal["id"])
        lead_project = str(lead_goal["project_id"] or "")
        form = "".join(
            [
                "<h3>Remember Current Goal</h3>",
                _input_form(
                    "save-workspace",
                    {},
                    {
                        "open_project": lead_project,
                        "open_goal": lead_goal_id,
                        "filters": filters or "active",
                        "expanded_panels": expanded or "timeline,evidence,approvals",
                        "last_viewed_artifact": last_artifact,
                        "updated_by": "operator-home",
                    },
                ),
            ]
        )

    return "".join(
        [
            "<section><h2>Home Resume Workspace</h2>",
            "<p class='muted'>Resume saved local browser context or explicitly remember the current lead goal for tomorrow.</p>",
            _ul(lines),
            _home_resume_action_form_section(root, open_goal),
            form,
            "</section>",
        ]
    )


def _home_resume_next_action_lines(root: Path, open_goal: str) -> list[str]:
    if not open_goal:
        return [
            "home_resume_next_action_status: no_saved_goal",
            "home_resume_next_action_form_available: false",
            "home_resume_next_action_write_on_get: false",
            "home_resume_next_action_external_effects_created: false",
        ]
    storage = _storage(root)
    state = _goal_state(root, storage, open_goal)
    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    form = _goal_next_action_form(state, next_action)
    return [
        f"home_resume_current_phase: {_e(phase)}",
        f"home_resume_next_action: {_e(next_action.action)}",
        f"home_resume_next_reason: {_e(next_action.reason)}",
        f"home_resume_operator_attention: {_e(_goal_operator_attention(phase, next_action))}",
        f"home_resume_next_surface: <a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>",
        f"home_resume_next_action_form_available: {str(bool(form)).lower()}",
        "home_resume_next_action_source: saved_goal_state",
        "home_resume_next_action_write_on_get: false",
        "home_resume_next_action_external_effects_created: false",
    ]


def _home_resume_action_form_section(root: Path, open_goal: str) -> str:
    if not open_goal:
        return ""
    storage = _storage(root)
    state = _goal_state(root, storage, open_goal)
    next_action = _goal_next_action(root, state)
    form = _goal_next_action_form(state, next_action)
    if not form:
        return ""
    return "".join(
        [
            "<h3>Home Resume Action Form</h3>",
            "<p class='muted'>Run the saved goal's browser-available local next action from Home.</p>",
            _kv(
                [
                    ("home_resume_action_form_goal", open_goal),
                    ("home_resume_action_form_next_action", next_action.action),
                    ("home_resume_action_form_external_effects_created", "false"),
                ]
            ),
            form,
        ]
    )


def _home_recent_activity(root: Path, storage: Storage) -> str:
    items = _home_recent_activity_items(root, storage)
    return "".join(
        [
            "<section><h2>Home Recent Activity</h2>",
            _kv(
                [
                    ("activity_log_format", "human_readable"),
                    ("recent_activity_items", str(len(items))),
                ]
            ),
            _home_activity_command_bar(items),
            _ul([_timeline_line(item) for item in items[:12]]),
            "</section>",
        ]
    )


def _home_activity_command_bar(items: list[dict[str, str]]) -> str:
    latest = items[0] if items else {}
    latest_href = latest.get("href") or "/goals"
    latest_label = latest.get("message") or "No recent activity"
    latest_at = _format_time(latest.get("at") or "") if latest else "none"
    operator_notes = sum(1 for item in items if item.get("kind") == "operator_note")
    artifacts = sum(
        1
        for item in items
        if item.get("kind") == "artifact"
        or str(item.get("href") or "").startswith("/artifacts?path=")
    )
    return "".join(
        [
            "<section class='panel home-activity-command-bar' data-home-activity-command-bar='true'><h3>Home Activity Command Bar</h3>",
            "<p class='muted'>One read-only summary of the latest local activity across current goals.</p>",
            _kv(
                [
                    ("home_activity_command_status", "available"),
                    ("home_activity_command_items", str(len(items))),
                    ("home_activity_command_latest_at", latest_at),
                    ("home_activity_command_latest_message", latest_label),
                    (
                        "home_activity_command_latest_surface",
                        SafeHtml(f"<a href='{_e(latest_href)}'>{_e(latest_href)}</a>"),
                    ),
                    ("home_activity_command_operator_notes", str(operator_notes)),
                    ("home_activity_command_artifacts", str(artifacts)),
                    ("home_activity_command_source", "goal_timeline_items"),
                    ("home_activity_command_write_on_get", "false"),
                    ("home_activity_command_network_actions_taken", "0"),
                    ("home_activity_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"home_activity_now: {_e(latest_label)}",
                    f"home_activity_click: <a href='{_e(latest_href)}'>{_e(latest_href)}</a>",
                    "home_activity_safety: read-only local timeline",
                ]
            ),
            "</section>",
        ]
    )


def _home_recent_activity_items(root: Path, storage: Storage) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for row in _goal_rows(storage, limit=12):
        state = _goal_state(root, storage, str(row["id"]))
        label = str(row["title"] or row["description"] or row["id"])
        for item in _goal_timeline_items(root, state)[-5:]:
            copy = dict(item)
            copy["message"] = f"{_compact_label(label, 42)}: {copy.get('message', '')}"
            items.append(copy)
    return sorted(items, key=lambda item: item.get("at") or "", reverse=True)


def _home_inbox(root: Path) -> str:
    inbox = collect_inbox_items(root)
    lines = [
        f"home_inbox_items: {inbox['count']}",
        f"steering_reviews: {len(inbox['steering_reviews'])}",
        f"pending_approvals: {len(inbox['pending_approvals'])}",
        f"open_incidents: {len(inbox['open_incidents'])}",
        f"subagent_delegations: {len(inbox['subagent_delegations'])}",
        f"coder_worktree_runs: {len(inbox['coder_worktree_runs'])}",
        f"commit_approvals: {len(inbox['coder_worktree_commit_approvals'])}",
        f"publication_requests: {len(inbox['coder_publication_requests'])}",
        "inbox_surface: <a href='/inbox'>/inbox</a>",
    ]
    return _list_section("Home Inbox", lines, "/inbox")


def _home_recommendations(storage: Storage) -> str:
    recommendations = storage.list_recent_task_recommendations(limit=8)
    lines = [
        (
            f"{_e(item.id)}: status={_e(item.status)} goal={_e(item.goal_id)} "
            f"task={_e(item.task_id)} reason={_e(item.reason)} "
            f"evidence={_artifact_link(item.evidence_path)}"
        )
        for item in recommendations
    ]
    if not lines:
        lines = ["home_recommendations_status: none_open"]
    return _list_section("Home Recommendations", lines, "/incidents")


def _home_incidents(storage: Storage) -> str:
    incidents = [
        item for item in storage.list_recent_incidents(limit=8) if item.status == "open"
    ]
    lines = [_incident_line(item) for item in incidents]
    if not lines:
        lines = ["home_incidents_status: none_open"]
    return _list_section("Home Incidents", lines, "/incidents")


def _dashboard_verification_snapshot(root: Path) -> str:
    workflow_path = root / ".github" / "workflows" / "tests.yml"
    workflow_text = (
        workflow_path.read_text(encoding="utf-8") if workflow_path.exists() else ""
    )
    latest_ci_record = _latest_ci_evidence_record(root)
    lines = [
        f"dashboard_workflow_file_status: {'available' if workflow_path.exists() else 'missing'}",
        f"dashboard_job_timeout_minutes: {_e(_workflow_timeout_minutes(workflow_text))}",
        "dashboard_ci_proof_boundary: completed passing GitHub Actions run plus operator-supplied local record",
        "dashboard_github_status_fetch: none",
        "verification_surface: <a href='/verification'>/verification</a>",
        "ci_evidence_surface: <a href='/ci-evidence'>/ci-evidence</a>",
    ]
    lines.extend(_ci_snapshot_handoff_lines(root, key_prefix="dashboard_ci_snapshot_"))
    if latest_ci_record is not None:
        source_kind, record = latest_ci_record
        lines.extend(
            [
                f"dashboard_latest_ci_source: {_e(source_kind)}",
                f"dashboard_latest_ci_status: {_e(record.status)}",
                f"dashboard_latest_ci_provider: {_e(record.provider)}",
                f"dashboard_latest_ci_commit: {_e(record.commit_sha)}",
                f"dashboard_latest_ci_branch: {_e(record.branch_name)}",
                f"dashboard_ci_external_run_id: {_e(record.external_run_id)}",
                f"dashboard_ci_url: <a href='{_e(record.external_url)}'>{_e(record.external_url)}</a>",
                f"dashboard_ci_handoff: {_e(getattr(record, 'github_handoff_id', 'none'))}",
                "dashboard_ci_record_source: operator_supplied",
                f"dashboard_ci_network_actions_taken: {_e(record.result_json.get('network_actions_taken', 'unknown'))}",
                f"dashboard_ci_external_mutations_taken: {_e(record.result_json.get('external_mutations_taken', 'unknown'))}",
            ]
        )
    else:
        lines.extend(
            [
                "dashboard_latest_ci_status: missing",
                "dashboard_next_ci_action: wait_for_github_actions_success_then_record_ci_snapshot_or_deploy_evidence",
                "dashboard_ci_record_source: none",
            ]
        )
    return _list_section("Verification Snapshot", lines, "/verification")


def _dashboard_dogfooding_snapshot(root: Path) -> str:
    storage = _storage(root)
    project = storage.get_registered_project("local-app-demo")
    if project is None:
        return _list_section(
            "Dashboard Dogfooding Snapshot",
            [
                "dashboard_demo_fixture_status: missing",
                "dashboard_next_dogfooding_action: run_demo_app_scenario",
                "demo_command: python3 -m agent_os.cli demo-app-scenario",
                "dogfooding_surface: <a href='/dogfooding'>/dogfooding</a>",
                "manual_browser_script_surface: <a href='/demo'>/demo</a>",
                "app_network_actions_taken: 0",
                "github_status_fetch: none",
            ],
            "/dogfooding",
        )

    delegations = [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if _task_project(storage, delegation.parent_task_id) == project.name
    ]
    selected_delegation = delegations[0] if delegations else None
    selected_run = None
    if selected_delegation is not None:
        runs = list_coder_worktree_runs(
            root,
            delegation_id=selected_delegation.id,
            limit=20,
        )
        selected_run = next((run for run in runs if run.status == "completed"), None)
        if selected_run is None and runs:
            selected_run = runs[0]

    next_action = "select_demo_delegation"
    workflow_surface = "<a href='/workflow'>/workflow</a>"
    run_surface = "none"
    if selected_delegation is not None:
        workflow_surface = (
            f"<a href='/workflow?delegation_id={quote(selected_delegation.id)}'>"
            f"/workflow?delegation_id={_e(selected_delegation.id)}</a>"
        )
        next_action = "review_delegation_state"
    if selected_run is not None:
        progress = _demo_progress_state(root, selected_run.id)
        next_action = progress["next_step"]
        workflow_surface = (
            f"<a href='/workflow?run_id={quote(selected_run.id)}'>"
            f"/workflow?run_id={_e(selected_run.id)}</a>"
        )
        run_surface = (
            f"<a href='/runs/{quote(selected_run.id)}'>"
            f"/runs/{_e(selected_run.id)}</a>"
        )

    return _list_section(
        "Dashboard Dogfooding Snapshot",
        [
            "dashboard_demo_fixture_status: available",
            f"dashboard_next_dogfooding_action: {_e(next_action)}",
            f"project_surface: <a href='/projects/{quote(project.name)}'>/projects/{_e(project.name)}</a>",
            f"workflow_surface: {workflow_surface}",
            f"run_surface: {run_surface}",
            "dogfooding_surface: <a href='/dogfooding'>/dogfooding</a>",
            "manual_browser_script_surface: <a href='/demo'>/demo</a>",
            "verification_surface: <a href='/verification'>/verification</a>",
            "app_network_actions_taken: 0",
            "external_mutations_taken: 0",
            "github_status_fetch: none",
        ],
        "/dogfooding",
    )


def _dashboard_goal_snapshot(root: Path) -> str:
    storage = _storage(root)
    rows = _goal_rows(storage, limit=6)
    if not rows:
        return _list_section(
            "Goal Snapshot",
            [
                "goal_cockpit_status: empty",
                "first_run_experience: open /goals to create project and first goal from browser guidance",
                "first_run_browser_path: register-project -> create-goal -> delegate -> context-pack -> run-delegation",
                "first_run_cli_required: false",
                "goal_surface: <a href='/goals'>/goals</a>",
            ],
            "/goals",
        )
    active = [row for row in rows if _goal_bucket(row) == "active"]
    paused = [row for row in rows if _goal_bucket(row) == "paused"]
    completed = [row for row in rows if _goal_bucket(row) == "completed"]
    lead_goal = active[0] if active else rows[0]
    state = _goal_state(root, storage, str(lead_goal["id"]))
    next_action = _goal_next_action(root, state)
    return _list_section(
        "Goal Snapshot",
        [
            f"goal_cockpit_status: populated",
            f"active_goals: {len(active)}",
            f"paused_goals: {len(paused)}",
            f"completed_goals: {len(completed)}",
            f"lead_goal: <a href='/goals/{quote(str(lead_goal['id']))}'>{_e(lead_goal['title'] or lead_goal['description'])}</a>",
            f"lead_goal_phase: {_e(_goal_current_phase(state))}",
            f"lead_goal_next_action: {_e(next_action.action)}",
            f"goal_surface: <a href='/goals'>/goals</a>",
        ],
        "/goals",
    )


def _search_page(root: Path, *, query: str) -> str:
    storage = _storage(root)
    term = query.strip()
    results = _search_results(root, storage, term) if term else []
    return "".join(
        [
            "<section><h1>Global Search</h1>",
            "<p class='muted'>Search goals, projects, delegations, artifacts, incidents, recommendations, memory, runs, and approvals from indexed local state.</p>",
            _search_form(term),
            _kv(
                [
                    ("search_query", term or "none"),
                    ("search_scope", "goals projects delegations artifacts incidents recommendations memory runs approvals"),
                    ("raw_filesystem_browsing", "false"),
                    ("results", str(len(results))),
                ]
            ),
            "</section>",
            _search_command_bar(term, results),
            _list_section(
                "Search Results",
                [_search_result_line(item) for item in results],
                anchor_id="search-results",
            ),
            _non_claim_banner(),
        ]
    )


def _search_form(term: str) -> str:
    return (
        "<form id='search-form' method='get' action='/search'>"
        f"<label>q <input name='q' value='{_e(term)}'></label>"
        "<button type='submit'>search</button>"
        "</form>"
    )


def _search_command_bar(term: str, results: list[dict[str, str]]) -> str:
    counts: dict[str, int] = {}
    for item in results:
        category = item.get("category", "unknown")
        counts[category] = counts.get(category, 0) + 1
    first_kind = "none"
    first_title = "none"
    first_href = "none"
    first_summary = "none"
    first_action = "Type a search query" if not term else "No local results"
    first_surface = SafeHtml("<a href='#search-form'>Search form</a>")
    if results:
        first = results[0]
        first_kind = first["category"]
        first_title = first["title"]
        first_href = first["href"]
        first_summary = first["summary"]
        first_action = "Open first result"
        first_surface = SafeHtml(
            f"<a href='{_e(first_href)}'>{_e(first_title)}</a>"
        )
    lines = [
        f"search_command_now: {_e(first_action)}",
        f"search_command_click: {first_surface}",
        f"search_command_reason: {_e(first_summary if results else (term or 'no query entered'))}",
        "search_command_safety: read-only indexed local search",
    ]
    if not term:
        lines.append("search_command_empty: enter a query to search local indexed state")
    elif not results:
        lines.append("search_command_empty: no matching local indexed records")
    category_keys = [
        "goal",
        "project",
        "task",
        "delegation",
        "run",
        "approval",
        "incident",
        "recommendation",
        "memory",
        "skill",
        "artifact",
    ]
    return "".join(
        [
            "<section class='panel search-command-bar' data-search-command-bar='true'><h2>Search Command Bar</h2>",
            "<p class='muted'>One read-only summary of the current local search and the first result to open.</p>",
            _kv(
                [
                    ("search_command_status", "available"),
                    ("search_command_query", term or "none"),
                    ("search_command_total_results", str(len(results))),
                    *[
                        (f"search_command_{category}_results", str(counts.get(category, 0)))
                        for category in category_keys
                    ],
                    ("search_command_first_kind", first_kind),
                    ("search_command_first_title", first_title),
                    ("search_command_first_href", first_href),
                    ("search_command_first_action", first_action),
                    ("search_command_first_surface", first_surface),
                    ("search_command_first_summary", first_summary),
                    ("search_command_write_on_get", "false"),
                    ("search_command_network_actions_taken", "0"),
                    ("search_command_external_effects_created", "false"),
                    ("search_command_raw_filesystem_browsing", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _search_results(root: Path, storage: Storage, term: str) -> list[dict[str, str]]:
    needle = term.lower()
    results: list[dict[str, str]] = []

    def add(category: str, title: str, href: str, summary: str) -> None:
        text = " ".join([category, title, href, summary]).lower()
        if needle in text:
            results.append(
                {
                    "category": category,
                    "title": title,
                    "href": href,
                    "summary": summary,
                }
            )

    for row in _goal_rows(storage, limit=200):
        goal_id = str(row["id"])
        goal_state = _goal_state(root, storage, goal_id)
        next_action = _goal_next_action(root, goal_state)
        add(
            "goal",
            str(row["title"] or row["description"] or row["id"]),
            f"/goals/{quote(goal_id)}",
            (
                f"id={goal_id} project={row['project_id']} status={row['status']} "
                f"phase={_goal_current_phase(goal_state)} "
                f"next_action={next_action.action} "
                f"remaining_work={_goal_remaining_work_summary(goal_state)}"
            ),
        )
    for project in storage.list_registered_projects():
        add(
            "project",
            project.name,
            f"/projects/{quote(project.name)}",
            f"root={project.root_path} test={project.default_test_command}",
        )
    for task in _table_rows(
        storage.db_path,
        "select * from tasks order by updated_at desc, id desc limit 200",
    ):
        add(
            "task",
            str(task["description"]),
            f"/goals/{quote(str(task['goal_id']))}",
            f"id={task['id']} project={task['project_id']} status={task['status']} type={task['task_type']}",
        )
    for delegation in storage.list_recent_subagent_delegations(limit=None):
        add(
            "delegation",
            delegation.title,
            f"/delegations/{quote(delegation.id)}",
            f"id={delegation.id} goal={delegation.parent_goal_id} status={delegation.status} profile={delegation.assigned_profile}",
        )
    for row in _table_rows(
        storage.db_path,
        "select * from runs order by started_at desc, id desc limit 200",
    ):
        add(
            "run",
            str(row["id"]),
            f"/runs/{quote(str(row['id']))}",
            f"goal={row['goal_id']} project={row['project_id']} status={row['status']}",
        )
    for incident in storage.list_recent_incidents(limit=100):
        add(
            "incident",
            incident.summary,
            "/incidents",
            f"id={incident.id} project={incident.project_id} status={incident.status} severity={incident.severity}",
        )
    for recommendation in storage.list_task_recommendations(limit=100):
        add(
            "recommendation",
            recommendation.reason,
            "/incidents",
            f"id={recommendation.id} goal={recommendation.goal_id} status={recommendation.status} type={recommendation.recommendation_type}",
        )
    for approval in storage.list_recent_approval_requests(limit=100):
        add(
            "approval",
            approval.reason,
            "/approvals",
            f"id={approval.id} goal={approval.goal_id} project={approval.project_id} status={approval.status}",
        )
    for memory in storage.list_memory_entries(limit=100):
        add(
            "memory",
            memory.key,
            "/memory",
            f"project={memory.project_id} scope={memory.scope} status={memory.status} value={memory.value}",
        )
    for skill in storage.list_skills(limit=100):
        add(
            "skill",
            skill.name,
            "/skills",
            f"project={skill.project_id or 'global'} status={skill.status} description={skill.description}",
        )
    for artifact in _known_artifact_paths(root, storage):
        summary = artifact
        if _artifact_contains(root, artifact, needle):
            summary = f"content_match path={artifact}"
        add("artifact", Path(artifact).name, f"/artifacts?path={quote(artifact)}", summary)
    return results[:80]


def _search_result_line(item: dict[str, str]) -> str:
    return (
        f"<strong>{_e(item['category'])}</strong> "
        f"<a href='{_e(item['href'])}'>{_e(item['title'])}</a>: "
        f"{_e(item['summary'])}"
    )


def _known_artifact_paths(root: Path, storage: Storage) -> list[str]:
    paths: list[str] = []

    def remember(path: str | Path | None) -> None:
        if not path:
            return
        relative = _repo_relative_artifact_path(root, path)
        if relative != "none" and relative not in paths:
            paths.append(relative)

    for row in _goal_rows(storage, limit=200):
        goal_dir = Path(".clanker") / "projects" / str(row["project_id"]) / "goals" / str(row["id"])
        for name in ["GOAL.md", "PLAN.md", "TASKS.md", "CONTRACT.md"]:
            remember(goal_dir / name)
    for task in _table_rows(
        storage.db_path,
        "select artifacts from tasks order by updated_at desc, id desc limit 200",
    ):
        for artifact in _json_loads_safe(str(task["artifacts"] or "[]"), []):
            remember(artifact)
    for row in _table_rows(
        storage.db_path,
        "select activity_path, summary_path, events_path from runs order by started_at desc, id desc limit 200",
    ):
        remember(row["activity_path"])
        remember(row["summary_path"])
        remember(row["events_path"])
    for delegation in storage.list_recent_subagent_delegations(limit=None):
        remember(delegation.result_artifact_path)
        metadata = load_delegation_result_metadata(delegation)
        for key in [
            "context_pack_json",
            "context_pack_md",
            "implementation_handoff_json",
            "implementation_handoff_md",
        ]:
            remember(metadata.get(key))
    for memory in storage.list_memory_entries(limit=100):
        remember(memory.artifact_path)
    for skill in storage.list_skills(limit=100):
        remember(skill.path)
    return paths[:200]


def _artifact_contains(root: Path, relative_path: str, needle: str) -> bool:
    try:
        path = resolve_artifact_path(root, relative_path)
    except ValueError:
        return False
    if not path.exists() or not path.is_file():
        return False
    try:
        text = path.read_bytes()[:MAX_ARTIFACT_BYTES].decode("utf-8", errors="replace")
    except OSError:
        return False
    return needle in text.lower()


def _resume_page(root: Path) -> str:
    state = _load_workspace_state(root)
    open_project = str(state.get("open_project") or "").strip()
    open_goal = str(state.get("open_goal") or "").strip()
    filters = str(state.get("filters") or "").strip()
    expanded = str(state.get("expanded_panels") or "").strip()
    last_artifact = str(state.get("last_viewed_artifact") or "").strip()
    has_workspace = any([open_project, open_goal, filters, expanded, last_artifact])

    targets: list[str] = []
    if open_goal:
        targets.append(f"resume_goal: <a href='/goals/{quote(open_goal)}'>{_e(open_goal)}</a>")
    if open_project:
        targets.append(f"resume_project: <a href='/projects/{quote(open_project)}'>{_e(open_project)}</a>")
    if last_artifact:
        targets.append(f"resume_artifact: {_artifact_link(last_artifact)}")
    if not targets:
        targets.extend(
            [
                "resume_status: no_saved_workspace",
                "start_goal_cockpit: <a href='/goals'>/goals</a>",
                "start_first_run: <a href='/'>Goal-First Home</a>",
            ]
        )

    next_href = "/goals"
    next_label = "Open Goal Cockpit"
    if open_goal:
        next_href = f"/goals/{quote(open_goal)}"
        next_label = f"Open saved goal {open_goal}"
    elif open_project:
        next_href = f"/projects/{quote(open_project)}"
        next_label = f"Open saved project {open_project}"
    elif last_artifact:
        next_href = f"/artifacts?path={quote(last_artifact)}"
        next_label = "Open saved artifact"

    return "".join(
        [
            "<section><h1>Resume Workspace</h1>",
            "<p class='muted'>One local landing page for returning to the last saved ClankerOS operator context.</p>",
            _kv(
                [
                    ("resume_workspace_available", str(has_workspace).lower()),
                    ("resume_workspace_source", ".clanker/app/workspace.json"),
                    ("resume_updated_at", state.get("updated_at", "never")),
                    ("resume_filters", filters or "none"),
                    ("resume_expanded_panels", expanded or "none"),
                    ("resume_workspace_write_on_get", "false"),
                    ("resume_provider_calls_taken_by_clankeros", "0"),
                    ("resume_network_actions_taken", "0"),
                    ("resume_external_effects_created", "false"),
                ]
            ),
            f"<p><a href='{_e(next_href)}'>{_e(next_label)}</a></p>",
            "</section>",
            _resume_readiness_section(root, state, open_project, open_goal, filters, expanded, last_artifact),
            _resume_next_action_section(root, open_goal),
            _resume_workflow_map_section(root, open_goal),
            _list_section("Resume Targets", targets),
            _list_section(
                "Manage Resume State",
                [
                    "workspace_surface: <a href='/workspace'>/workspace</a>",
                    "save_workspace_action: confirmed_local_only",
                    "raw_filesystem_browsing: false",
                ],
            ),
            _non_claim_banner(),
        ]
    )


def _resume_readiness_section(
    root: Path,
    state: dict[str, str],
    open_project: str,
    open_goal: str,
    filters: str,
    expanded: str,
    last_artifact: str,
) -> str:
    readiness = _workspace_resume_readiness(
        root,
        open_project=open_project,
        open_goal=open_goal,
        filters=filters,
        expanded=expanded,
        last_artifact=last_artifact,
    )
    last_artifact_exists = bool(readiness["last_artifact_exists"])
    ready = bool(readiness["ready"])
    status = str(readiness["status"])
    next_surface = str(readiness["next_surface"])
    return "".join(
        [
            "<section><h2>Resume Readiness</h2>",
            "<p class='muted'>Checklist for returning tomorrow to the exact saved local operator context.</p>",
            _kv(
                [
                    ("resume_readiness_status", status),
                    ("resume_readiness_source", ".clanker/app/workspace.json"),
                    ("resume_readiness_updated_at", state.get("updated_at", "never")),
                    ("resume_readiness_open_project", "present" if open_project else "missing"),
                    ("resume_readiness_open_goal", "present" if open_goal else "missing"),
                    ("resume_readiness_filters", "present" if filters else "missing"),
                    ("resume_readiness_expanded_panels", "present" if expanded else "missing"),
                    ("resume_readiness_last_viewed_artifact", "present" if last_artifact else "missing"),
                    ("resume_readiness_last_artifact_exists", str(last_artifact_exists).lower()),
                    ("resume_readiness_next_surface", SafeHtml(f"<a href='{_e(next_surface)}'>{_e(next_surface)}</a>")),
                    ("resume_readiness_come_back_tomorrow_ready", str(ready).lower()),
                    ("resume_readiness_illustration", "[project] -> [goal] -> [filters/panels] -> [artifact] -> [next action]"),
                    ("resume_readiness_write_on_get", "false"),
                    ("resume_readiness_external_effects_created", "false"),
                ]
            ),
            "</section>",
        ]
    )


def _workspace_resume_readiness(
    root: Path,
    *,
    open_project: str,
    open_goal: str,
    filters: str,
    expanded: str,
    last_artifact: str,
) -> dict[str, object]:
    last_artifact_exists = False
    if last_artifact:
        try:
            last_artifact_exists = resolve_artifact_path(root, last_artifact).exists()
        except ValueError:
            last_artifact_exists = False
    required = {
        "open_project": bool(open_project),
        "open_goal": bool(open_goal),
        "filters": bool(filters),
        "expanded_panels": bool(expanded),
        "last_viewed_artifact": bool(last_artifact),
        "last_artifact_exists": last_artifact_exists,
    }
    ready = all(required.values())
    status = "ready" if ready else ("partial" if any(required.values()) else "not_started")
    next_surface = f"/goals/{quote(open_goal)}" if open_goal else (f"/projects/{quote(open_project)}" if open_project else "/goals")
    return {
        "required": required,
        "ready": ready,
        "status": status,
        "next_surface": next_surface,
        "last_artifact_exists": last_artifact_exists,
    }


def _resume_next_action_section(root: Path, open_goal: str) -> str:
    if not open_goal:
        return _list_section(
            "Resume Next Action",
            [
                "resume_next_action_status: no_saved_goal",
                "resume_next_surface: <a href='/goals'>/goals</a>",
                "resume_next_action_form_available: false",
                "resume_next_action_external_effects_created: false",
            ],
        )
    storage = _storage(root)
    state = _goal_state(root, storage, open_goal)
    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    form = _goal_next_action_form(state, next_action)
    return "".join(
        [
            "<section><h2>Resume Next Action</h2>",
            "<p class='muted'>Continue from the saved goal's current local workflow state without leaving the return-to-work page.</p>",
            _kv(
                [
                    ("resume_saved_goal", open_goal),
                    ("resume_current_phase", phase),
                    ("resume_next_action", next_action.action),
                    ("resume_next_reason", next_action.reason),
                    ("resume_operator_attention", _goal_operator_attention(phase, next_action)),
                    ("resume_next_surface", SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>")),
                    ("resume_next_action_form_available", "true" if form else "false"),
                    ("resume_next_action_source", "saved_goal_state"),
                    ("resume_next_action_write_on_get", "false"),
                    ("resume_next_action_external_effects_created", "false"),
                ]
            ),
            f"<div class='resume-action-form'><h3>Resume Action Form</h3>{form}</div>" if form else "",
            "</section>",
        ]
    )


def _resume_workflow_map_section(root: Path, open_goal: str) -> str:
    if not open_goal:
        return "".join(
            [
                "<section id='resume-workflow-map' class='panel resume-workflow-map' data-resume-workflow-map='true'><h2>Resume Workflow Map</h2>",
                "<p class='muted'>A read-only gate map appears here once a saved goal exists.</p>",
                _kv(
                    [
                        ("resume_workflow_map_status", "no_saved_goal"),
                        ("resume_workflow_map_saved_goal", "none"),
                        ("resume_workflow_map_next_surface", SafeHtml("<a href='/goals'>/goals</a>")),
                        ("resume_workflow_map_source", "saved_workspace_goal"),
                        ("resume_workflow_map_write_on_get", "false"),
                        ("resume_workflow_map_provider_calls_taken_by_clankeros", "0"),
                        ("resume_workflow_map_network_actions_taken", "0"),
                        ("resume_workflow_map_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )
    storage = _storage(root)
    state = _goal_state(root, storage, open_goal)
    goal = state.get("goal")
    if goal is None:
        return "".join(
            [
                "<section id='resume-workflow-map' class='panel resume-workflow-map' data-resume-workflow-map='true'><h2>Resume Workflow Map</h2>",
                "<p class='muted'>The saved workspace points at a goal that is no longer available locally.</p>",
                _kv(
                    [
                        ("resume_workflow_map_status", "missing_goal"),
                        ("resume_workflow_map_saved_goal", open_goal),
                        ("resume_workflow_map_next_surface", SafeHtml("<a href='/goals'>/goals</a>")),
                        ("resume_workflow_map_source", "saved_workspace_goal"),
                        ("resume_workflow_map_write_on_get", "false"),
                        ("resume_workflow_map_provider_calls_taken_by_clankeros", "0"),
                        ("resume_workflow_map_network_actions_taken", "0"),
                        ("resume_workflow_map_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )
    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    gates, counts, current_gate = _goal_workflow_gate_summary(root, state, next_action)
    done = counts.get("done", 0)
    pending = counts.get("pending", 0)
    waiting = counts.get("waiting", 0)
    total = len(gates)
    items: list[str] = []
    for index, (name, status) in enumerate(gates, start=1):
        label = name.replace("_", " ")
        marker = "current" if name == current_gate else status
        next_label = (
            f" next={_e(next_action.action)}"
            if name == current_gate and current_gate != "complete"
            else ""
        )
        items.append(
            "<li "
            f"data-resume-workflow-gate='{_e(name)}' "
            f"data-gate-status='{_e(status)}' "
            f"data-gate-marker='{_e(marker)}'>"
            f"<span class='workflow-map-index'>{index}</span> "
            f"<strong>{_e(label)}</strong> "
            f"resume_workflow_map_step: {_e(name)} status={_e(status)} marker={_e(marker)}{next_label}</li>"
        )
    return "".join(
        [
            "<section id='resume-workflow-map' class='panel resume-workflow-map' data-resume-workflow-map='true'><h2>Resume Workflow Map</h2>",
            "<p class='muted'>The saved goal's local workflow gates, shown here so returning to work does not require opening the full Goal page first.</p>",
            _kv(
                [
                    ("resume_workflow_map_status", "available"),
                    ("resume_workflow_map_saved_goal", open_goal),
                    ("resume_workflow_map_current_phase", phase),
                    ("resume_workflow_map_current_gate", current_gate),
                    ("resume_workflow_map_next_action", next_action.action),
                    (
                        "resume_workflow_map_next_surface",
                        SafeHtml(
                            f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"
                        ),
                    ),
                    ("resume_workflow_map_progress", f"{done}/{total} gates done"),
                    ("resume_workflow_map_done_count", str(done)),
                    ("resume_workflow_map_pending_count", str(pending)),
                    ("resume_workflow_map_waiting_count", str(waiting)),
                    ("resume_workflow_map_source", "goal_remaining_work_gates"),
                    (
                        "resume_workflow_map_goal_surface",
                        SafeHtml(f"<a href='/goals/{quote(open_goal)}'>/goals/{_e(open_goal)}</a>"),
                    ),
                    ("resume_workflow_map_write_on_get", "false"),
                    ("resume_workflow_map_provider_calls_taken_by_clankeros", "0"),
                    ("resume_workflow_map_network_actions_taken", "0"),
                    ("resume_workflow_map_external_effects_created", "false"),
                ]
            ),
            "<ol class='workflow-map-rail resume-workflow-map-rail'>",
            "".join(items),
            "</ol>",
            "</section>",
        ]
    )


def _workspace_page(root: Path) -> str:
    state = _load_workspace_state(root)
    open_project = state.get("open_project", "")
    open_goal = state.get("open_goal", "")
    last_artifact = state.get("last_viewed_artifact", "")
    restore_links = []
    if open_project:
        restore_links.append(f"open_project: <a href='/projects/{quote(open_project)}'>{_e(open_project)}</a>")
    if open_goal:
        restore_links.append(f"open_goal: <a href='/goals/{quote(open_goal)}'>{_e(open_goal)}</a>")
    if last_artifact:
        restore_links.append(f"last_viewed_artifact: {_artifact_link(last_artifact)}")
    return "".join(
        [
            "<section><h1>Workspace State</h1>",
            "<p class='muted'>Persistent local browser context for leaving and resuming ClankerOS work.</p>",
            _kv(
                [
                    ("workspace_path", ".clanker/app/workspace.json"),
                    ("open_project", open_project or "none"),
                    ("open_goal", open_goal or "none"),
                    ("filters", state.get("filters", "") or "none"),
                    ("expanded_panels", state.get("expanded_panels", "") or "none"),
                    ("last_viewed_artifact", last_artifact or "none"),
                    ("updated_at", state.get("updated_at", "never")),
                ]
            ),
            "</section>",
            _workspace_daily_brief(root, state, open_project, open_goal, last_artifact),
            _list_section("Restore Links", restore_links),
            _list_section("Workspace Continuation", _workspace_next_action_lines(root, open_goal)),
            _workspace_workflow_map_section(root, open_goal),
            _workspace_action_form_section(root, open_goal),
            "<section id='save-workspace'><h2>Save Workspace</h2>",
            _input_form(
                "save-workspace",
                {},
                {
                    "open_project": open_project,
                    "open_goal": open_goal,
                    "filters": state.get("filters", ""),
                    "expanded_panels": state.get("expanded_panels", ""),
                    "last_viewed_artifact": last_artifact,
                    "updated_by": state.get("updated_by", "operator"),
                },
            ),
            "</section>",
            _non_claim_banner(),
        ]
    )


def _workspace_daily_brief(
    root: Path,
    state: dict[str, str],
    open_project: str,
    open_goal: str,
    last_artifact: str,
) -> str:
    filters = state.get("filters", "")
    expanded = state.get("expanded_panels", "")
    readiness = _workspace_resume_readiness(
        root,
        open_project=open_project,
        open_goal=open_goal,
        filters=filters,
        expanded=expanded,
        last_artifact=last_artifact,
    )
    required = readiness["required"]
    if not open_goal:
        status = "no_saved_workspace" if not any(required.values()) else "no_saved_goal"
        phase = "none"
        current_gate = "none"
        next_action = "Open goals"
        reason = "no_saved_goal"
        target_href = "/goals"
        target_label = "/goals"
        progress = "0/0 gates done"
        waiting_items = "approvals=0 incidents=0 recommendations=0"
        finish_status = "needs_workspace_save"
        source = "saved_workspace_state"
    else:
        storage = _storage(root)
        goal_state = _goal_state(root, storage, open_goal)
        goal = goal_state.get("goal")
        if goal is None:
            status = "missing_goal"
            phase = "missing"
            current_gate = "missing_goal"
            next_action = "Open goals"
            reason = "saved_goal_missing"
            target_href = "/goals"
            target_label = "/goals"
            progress = "0/0 gates done"
            waiting_items = "approvals=0 incidents=0 recommendations=0"
            finish_status = "repair_saved_workspace"
            source = "saved_workspace_state"
        else:
            status = "available"
            phase = _goal_current_phase(goal_state)
            action = _goal_next_action(root, goal_state)
            gates, counts, current_gate = _goal_workflow_gate_summary(root, goal_state, action)
            next_action = action.action
            reason = action.reason
            target_href = action.href
            target_label = action.href
            progress = f"{counts.get('done', 0)}/{len(gates)} gates done"
            pending_approvals = (
                _count_status(goal_state["worktree_approvals"], "pending_operator_approval")
                + _count_status(goal_state["commit_approvals"], "pending_operator_approval")
                + _count_status(goal_state["publications"], "pending_operator_approval")
            )
            waiting_items = (
                f"approvals={pending_approvals} "
                f"incidents={sum(1 for row in goal_state['incidents'] if row['status'] == 'open')} "
                f"recommendations={sum(1 for row in goal_state['recommendations'] if row['status'] == 'open')}"
            )
            finish_status = "ready" if readiness["ready"] else "needs_workspace_save"
            source = "saved_workspace_goal"
    target = SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>")
    save_target = SafeHtml("<a href='#save-workspace'>#save-workspace</a>")
    project_target = (
        SafeHtml(f"<a href='/projects/{quote(open_project)}'>{_e(open_project)}</a>")
        if open_project
        else SafeHtml("<a href='/projects'>/projects</a>")
    )
    goal_target = (
        SafeHtml(f"<a href='/goals/{quote(open_goal)}'>{_e(open_goal)}</a>")
        if open_goal
        else SafeHtml("<a href='/goals'>/goals</a>")
    )
    return "".join(
        [
            "<section id='workspace-daily-brief' class='panel workspace-daily-brief' data-workspace-daily-brief='true'><h2>Workspace Daily Brief</h2>",
            "<p class='muted'>A read-only morning and end-of-day checklist for the saved local workspace.</p>",
            _kv(
                [
                    ("workspace_daily_status", status),
                    ("workspace_daily_project", project_target),
                    ("workspace_daily_goal", goal_target),
                    ("workspace_daily_phase", phase),
                    ("workspace_daily_current_gate", current_gate),
                    ("workspace_daily_next_action", next_action),
                    ("workspace_daily_reason", reason),
                    ("workspace_daily_target_surface", target),
                    ("workspace_daily_resume_ready", "true" if readiness["ready"] else "false"),
                    ("workspace_daily_resume_status", str(readiness["status"])),
                    (
                        "workspace_daily_open_project_saved",
                        "true" if required["open_project"] else "false",
                    ),
                    (
                        "workspace_daily_open_goal_saved",
                        "true" if required["open_goal"] else "false",
                    ),
                    (
                        "workspace_daily_filters_saved",
                        "true" if required["filters"] else "false",
                    ),
                    (
                        "workspace_daily_expanded_panels_saved",
                        "true" if required["expanded_panels"] else "false",
                    ),
                    (
                        "workspace_daily_last_artifact_saved",
                        "true" if required["last_viewed_artifact"] else "false",
                    ),
                    (
                        "workspace_daily_last_artifact_exists",
                        "true" if readiness["last_artifact_exists"] else "false",
                    ),
                    ("workspace_daily_progress", progress),
                    ("workspace_daily_waiting_items", waiting_items),
                    ("workspace_daily_finish_status", finish_status),
                    ("workspace_daily_save_surface", save_target),
                    ("workspace_daily_source", source),
                    ("workspace_daily_write_on_get", "false"),
                    ("workspace_daily_provider_calls_taken_by_clankeros", "0"),
                    ("workspace_daily_network_actions_taken", "0"),
                    ("workspace_daily_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"workspace_daily_start: {_e(next_action)}",
                    f"workspace_daily_continue: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"workspace_daily_finish: status={_e(finish_status)} save=<a href='#save-workspace'>#save-workspace</a>",
                    "workspace_daily_safety: read-only until confirmed save-workspace or local action form",
                ]
            ),
            "</section>",
        ]
    )


def _workspace_next_action_lines(root: Path, open_goal: str) -> list[str]:
    if not open_goal:
        return [
            "workspace_next_action_status: no_saved_goal",
            "workspace_next_surface: <a href='/goals'>/goals</a>",
            "workspace_next_action_form_available: false",
            "workspace_next_action_write_on_get: false",
            "workspace_next_action_external_effects_created: false",
        ]
    storage = _storage(root)
    state = _goal_state(root, storage, open_goal)
    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    form = _goal_next_action_form(state, next_action)
    return [
        f"workspace_current_phase: {_e(phase)}",
        f"workspace_next_action: {_e(next_action.action)}",
        f"workspace_next_reason: {_e(next_action.reason)}",
        f"workspace_operator_attention: {_e(_goal_operator_attention(phase, next_action))}",
        f"workspace_next_surface: <a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>",
        f"workspace_next_action_form_available: {str(bool(form)).lower()}",
        "workspace_next_action_source: saved_goal_state",
        "workspace_next_action_write_on_get: false",
        "workspace_next_action_external_effects_created: false",
    ]


def _workspace_workflow_map_section(root: Path, open_goal: str) -> str:
    if not open_goal:
        return "".join(
            [
                "<section id='workspace-workflow-map' class='panel workspace-workflow-map' data-workspace-workflow-map='true'><h2>Workspace Workflow Map</h2>",
                "<p class='muted'>A read-only workflow map appears here once workspace state has a saved goal.</p>",
                _kv(
                    [
                        ("workspace_workflow_map_status", "no_saved_goal"),
                        ("workspace_workflow_map_saved_goal", "none"),
                        ("workspace_workflow_map_next_surface", SafeHtml("<a href='/goals'>/goals</a>")),
                        ("workspace_workflow_map_save_surface", SafeHtml("<a href='#save-workspace'>#save-workspace</a>")),
                        ("workspace_workflow_map_source", "workspace_saved_goal"),
                        ("workspace_workflow_map_write_on_get", "false"),
                        ("workspace_workflow_map_provider_calls_taken_by_clankeros", "0"),
                        ("workspace_workflow_map_network_actions_taken", "0"),
                        ("workspace_workflow_map_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )
    storage = _storage(root)
    state = _goal_state(root, storage, open_goal)
    goal = state.get("goal")
    if goal is None:
        return "".join(
            [
                "<section id='workspace-workflow-map' class='panel workspace-workflow-map' data-workspace-workflow-map='true'><h2>Workspace Workflow Map</h2>",
                "<p class='muted'>The saved workspace points at a goal that is no longer available locally.</p>",
                _kv(
                    [
                        ("workspace_workflow_map_status", "missing_goal"),
                        ("workspace_workflow_map_saved_goal", open_goal),
                        ("workspace_workflow_map_next_surface", SafeHtml("<a href='/goals'>/goals</a>")),
                        ("workspace_workflow_map_save_surface", SafeHtml("<a href='#save-workspace'>#save-workspace</a>")),
                        ("workspace_workflow_map_source", "workspace_saved_goal"),
                        ("workspace_workflow_map_write_on_get", "false"),
                        ("workspace_workflow_map_provider_calls_taken_by_clankeros", "0"),
                        ("workspace_workflow_map_network_actions_taken", "0"),
                        ("workspace_workflow_map_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )
    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    gates, counts, current_gate = _goal_workflow_gate_summary(root, state, next_action)
    done = counts.get("done", 0)
    pending = counts.get("pending", 0)
    waiting = counts.get("waiting", 0)
    total = len(gates)
    items: list[str] = []
    for index, (name, status) in enumerate(gates, start=1):
        label = name.replace("_", " ")
        marker = "current" if name == current_gate else status
        next_label = (
            f" next={_e(next_action.action)}"
            if name == current_gate and current_gate != "complete"
            else ""
        )
        items.append(
            "<li "
            f"data-workspace-workflow-gate='{_e(name)}' "
            f"data-gate-status='{_e(status)}' "
            f"data-gate-marker='{_e(marker)}'>"
            f"<span class='workflow-map-index'>{index}</span> "
            f"<strong>{_e(label)}</strong> "
            f"workspace_workflow_map_step: {_e(name)} status={_e(status)} marker={_e(marker)}{next_label}</li>"
        )
    return "".join(
        [
            "<section id='workspace-workflow-map' class='panel workspace-workflow-map' data-workspace-workflow-map='true'><h2>Workspace Workflow Map</h2>",
            "<p class='muted'>The editable workspace state's saved goal workflow gates, shown beside the save form so the operator can adjust context without losing the current gate.</p>",
            _kv(
                [
                    ("workspace_workflow_map_status", "available"),
                    ("workspace_workflow_map_saved_goal", open_goal),
                    ("workspace_workflow_map_current_phase", phase),
                    ("workspace_workflow_map_current_gate", current_gate),
                    ("workspace_workflow_map_next_action", next_action.action),
                    (
                        "workspace_workflow_map_next_surface",
                        SafeHtml(
                            f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"
                        ),
                    ),
                    ("workspace_workflow_map_progress", f"{done}/{total} gates done"),
                    ("workspace_workflow_map_done_count", str(done)),
                    ("workspace_workflow_map_pending_count", str(pending)),
                    ("workspace_workflow_map_waiting_count", str(waiting)),
                    ("workspace_workflow_map_source", "goal_remaining_work_gates"),
                    (
                        "workspace_workflow_map_goal_surface",
                        SafeHtml(f"<a href='/goals/{quote(open_goal)}'>/goals/{_e(open_goal)}</a>"),
                    ),
                    ("workspace_workflow_map_save_surface", SafeHtml("<a href='#save-workspace'>#save-workspace</a>")),
                    ("workspace_workflow_map_write_on_get", "false"),
                    ("workspace_workflow_map_provider_calls_taken_by_clankeros", "0"),
                    ("workspace_workflow_map_network_actions_taken", "0"),
                    ("workspace_workflow_map_external_effects_created", "false"),
                ]
            ),
            "<ol class='workflow-map-rail workspace-workflow-map-rail'>",
            "".join(items),
            "</ol>",
            "</section>",
        ]
    )


def _workspace_action_form_section(root: Path, open_goal: str) -> str:
    if not open_goal:
        return ""
    storage = _storage(root)
    state = _goal_state(root, storage, open_goal)
    next_action = _goal_next_action(root, state)
    form = _goal_next_action_form(state, next_action)
    if not form:
        return ""
    return "".join(
        [
            "<section><h2>Workspace Action Form</h2>",
            "<p class='muted'>Run the saved goal's browser-available local next action from the workspace state page.</p>",
            _kv(
                [
                    ("workspace_action_form_goal", open_goal),
                    ("workspace_action_form_next_action", next_action.action),
                    ("workspace_action_form_external_effects_created", "false"),
                ]
            ),
            form,
            "</section>",
        ]
    )


def _memory_page(root: Path) -> str:
    storage = _storage(root)
    entries = storage.list_memory_entries(limit=100)
    project_memories = [entry for entry in entries if entry.scope != "global"]
    global_memories = [entry for entry in entries if entry.scope == "global"]
    generated = [entry for entry in entries if entry.source_type != "operator"]
    proposed = [entry for entry in entries if entry.status == "proposed"]
    operator_notes = _operator_note_paths(root)
    future_work = storage.list_recent_task_recommendations(limit=20)
    return "".join(
        [
            "<section><h1>Memory Bank</h1>",
            "<p class='muted'>Project memories, global memories, generated memories, operator notes, future work, and pin actions from local records.</p>",
            _kv(
                [
                    ("project_memory_count", str(len(project_memories))),
                    ("global_memory_count", str(len(global_memories))),
                    ("generated_memory_count", str(len(generated))),
                    ("operator_note_count", str(len(operator_notes))),
                    ("future_work_count", str(len(future_work))),
                    ("pin_memory_available", "true"),
                ]
            ),
            "</section>",
            _memory_command_bar(
                root,
                entries=entries,
                project_memories=project_memories,
                global_memories=global_memories,
                generated=generated,
                proposed=proposed,
                operator_notes=operator_notes,
                future_work=future_work,
            ),
            _list_section(
                "Proposed Memories",
                [_memory_line(entry) for entry in proposed],
                anchor_id="memory-proposed",
            ),
            _list_section(
                "Project Memories",
                [_memory_line(entry) for entry in project_memories],
                anchor_id="memory-project",
            ),
            _list_section(
                "Global Memories",
                [_memory_line(entry) for entry in global_memories],
                anchor_id="memory-global",
            ),
            _list_section(
                "Generated Memories",
                [_memory_line(entry) for entry in generated],
                anchor_id="memory-generated",
            ),
            _list_section(
                "Operator Notes",
                [f"operator_note: {_artifact_link(path)}" for path in operator_notes],
                anchor_id="memory-operator-notes",
            ),
            _list_section(
                "Future Work",
                [_task_recommendation_line(item) for item in future_work],
                anchor_id="memory-future-work",
            ),
            _non_claim_banner(),
        ]
    )


def _memory_command_bar(
    root: Path,
    *,
    entries: list[Any],
    project_memories: list[Any],
    global_memories: list[Any],
    generated: list[Any],
    proposed: list[Any],
    operator_notes: list[str],
    future_work: list[Any],
) -> str:
    workspace = _load_workspace_state(root)
    active_count = len([entry for entry in entries if entry.status == "active"])
    archived_count = len([entry for entry in entries if entry.status == "archived"])
    first_target = "none"
    next_action = "Review memory bank"
    target_href = "#memory-project"
    target_label = "Project Memories"
    reason = "local_memory_records_available" if entries else "no_memory_records_yet"
    if proposed:
        first = proposed[0]
        first_target = first.id
        next_action = "Pin first proposed memory"
        target_href = "#memory-proposed"
        target_label = "Proposed Memories"
        reason = "proposed_memory_waiting_for_operator"
    elif operator_notes:
        first_target = operator_notes[0]
        next_action = "Review operator notes"
        target_href = "#memory-operator-notes"
        target_label = "Operator Notes"
        reason = "operator_note_artifacts_available"
    elif future_work:
        first = future_work[0]
        first_target = getattr(first, "id", "future_work")
        next_action = "Review future work"
        target_href = "#memory-future-work"
        target_label = "Future Work"
        reason = "task_recommendations_available"
    elif global_memories:
        first_target = global_memories[0].id
        target_href = "#memory-global"
        target_label = "Global Memories"
        reason = "global_memory_records_available"
    elif generated:
        first_target = generated[0].id
        target_href = "#memory-generated"
        target_label = "Generated Memories"
        reason = "generated_memory_records_available"
    elif project_memories:
        first_target = project_memories[0].id
    elif workspace.get("open_goal"):
        first_target = workspace["open_goal"]
        next_action = "Resume saved goal"
        target_href = "/resume"
        target_label = "/resume"
        reason = "saved_workspace_available"
    else:
        next_action = "Create goal context"
        target_href = "/goals"
        target_label = "/goals"

    target_surface = SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>")
    return "".join(
        [
            "<section class='panel memory-command-bar' data-memory-command-bar='true'><h2>Memory Command Bar</h2>",
            "<p class='muted'>One read-only summary of durable memory state and the next local memory action.</p>",
            _kv(
                [
                    ("memory_command_status", "available"),
                    ("memory_command_total_entries", str(len(entries))),
                    ("memory_command_project_entries", str(len(project_memories))),
                    ("memory_command_global_entries", str(len(global_memories))),
                    ("memory_command_generated_entries", str(len(generated))),
                    ("memory_command_proposed_entries", str(len(proposed))),
                    ("memory_command_active_entries", str(active_count)),
                    ("memory_command_archived_entries", str(archived_count)),
                    ("memory_command_operator_notes", str(len(operator_notes))),
                    ("memory_command_future_work", str(len(future_work))),
                    ("memory_command_first_target", first_target),
                    ("memory_command_next_action", next_action),
                    ("memory_command_target_surface", target_surface),
                    ("memory_command_reason", reason),
                    ("memory_command_workspace_project", workspace.get("open_project", "")),
                    ("memory_command_workspace_goal", workspace.get("open_goal", "")),
                    ("memory_command_workspace_artifact", workspace.get("last_viewed_artifact", "")),
                    ("memory_command_pin_memory_available", str(bool(proposed)).lower()),
                    ("memory_command_write_on_get", "false"),
                    ("memory_command_raw_filesystem_browsing", "false"),
                    ("memory_command_provider_calls_taken", "0"),
                    ("memory_command_network_actions_taken", "0"),
                    ("memory_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"memory_command_now: {_e(next_action)}",
                    f"memory_command_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"memory_command_reason: {_e(reason)}",
                    "memory_command_safety: read-only memory guidance",
                ]
            ),
            "</section>",
        ]
    )


def _memory_line(entry: Any) -> str:
    pin = ""
    if entry.status != "active":
        pin = " " + _form("pin-memory", {"memory_id": entry.id, "note": "Pinned from memory page"})
    return (
        f"{_e(entry.id)}: project={_e(entry.project_id)} scope={_e(entry.scope)} "
        f"status={_e(entry.status)} key={_e(entry.key)} value={_e(entry.value)} "
        f"artifact={_artifact_link(entry.artifact_path)}{pin}"
    )


def _operator_note_paths(root: Path) -> list[str]:
    base = root / ".clanker" / "projects"
    if not base.exists():
        return []
    paths = []
    for path in sorted(base.glob("*/goals/*/operator-notes.md")):
        paths.append(_repo_relative_artifact_path(root, path))
    return paths[:100]


def _skills_page(root: Path) -> str:
    storage = _storage(root)
    skills = storage.list_skills(limit=100)
    usage = _skill_usage(storage)
    available_lines = [_skill_line(root, skill, usage) for skill in skills]
    generated_lines = [_skill_line(root, skill, usage) for skill in skills if skill.source_run_id]
    return "".join(
        [
            "<section><h1>Skills Inventory</h1>",
            "<p class='muted'>Available and generated skills from local ClankerOS records. This page reads usage signals only; it does not install or execute skills.</p>",
            _kv(
                [
                    ("available_skill_count", str(len(skills))),
                    ("generated_skill_storage", "ready"),
                    ("provider_actions_taken", "0"),
                ]
            ),
            "</section>",
            _skills_command_bar(root, skills=skills, usage=usage),
            _list_section(
                "Available Skills",
                available_lines or ["none_recorded_yet usage_count=0 last_used=none projects_using=none"],
                anchor_id="skills-available",
            ),
            _list_section(
                "Generated Skills",
                generated_lines or ["none_recorded_yet usage_count=0 last_used=none projects_using=none"],
                anchor_id="skills-generated",
            ),
            _non_claim_banner(),
        ]
    )


def _skills_command_bar(
    root: Path,
    *,
    skills: list[Any],
    usage: dict[str, dict[str, Any]],
) -> str:
    generated = [skill for skill in skills if skill.source_run_id]
    active = [skill for skill in skills if skill.status == "active"]
    proposed = [skill for skill in skills if skill.status == "proposed"]
    archived = [skill for skill in skills if skill.status == "archived"]
    used_names = {name for name, data in usage.items() if int(data.get("count", 0)) > 0}
    projects = {
        str(project)
        for data in usage.values()
        for project in data.get("projects", set())
        if project
    }
    projects.update(str(skill.project_id) for skill in skills if skill.project_id)
    first_skill = (
        generated[0]
        if generated
        else (active[0] if active else (proposed[0] if proposed else (skills[0] if skills else None)))
    )
    first_target = "none"
    next_action = "Create goal context"
    target_href = "/goals"
    target_label = "/goals"
    reason = "no_skill_records_yet"
    if first_skill is not None:
        first_target = first_skill.name
        if first_skill.source_run_id:
            next_action = "Review generated skill"
            target_href = "#skills-generated"
            target_label = "Generated Skills"
            reason = "generated_skill_record_available"
        elif first_skill.status == "proposed":
            next_action = "Review proposed skill"
            target_href = "#skills-available"
            target_label = "Available Skills"
            reason = "proposed_skill_waiting_for_operator"
        else:
            next_action = "Review available skill"
            target_href = "#skills-available"
            target_label = "Available Skills"
            reason = "available_skill_record_available"
    first_artifact: str | SafeHtml = "none"
    if first_skill is not None and first_skill.path:
        first_artifact = _artifact_link(_repo_relative_artifact_path(root, first_skill.path))
    return "".join(
        [
            "<section class='panel skills-command-bar' data-skills-command-bar='true'><h2>Skills Command Bar</h2>",
            "<p class='muted'>One read-only summary of skill availability, generated records, usage, and the next local review target.</p>",
            _kv(
                [
                    ("skills_command_status", "available"),
                    ("skills_command_total_records", str(len(skills))),
                    ("skills_command_active_records", str(len(active))),
                    ("skills_command_proposed_records", str(len(proposed))),
                    ("skills_command_archived_records", str(len(archived))),
                    ("skills_command_generated_records", str(len(generated))),
                    ("skills_command_used_skill_names", str(len(used_names))),
                    ("skills_command_projects_using_skills", str(len(projects))),
                    ("skills_command_first_target", first_target),
                    ("skills_command_first_artifact", first_artifact),
                    ("skills_command_next_action", next_action),
                    (
                        "skills_command_target_surface",
                        SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>"),
                    ),
                    ("skills_command_reason", reason),
                    ("skills_command_execution_available", "false"),
                    ("skills_command_install_available", "false"),
                    ("skills_command_write_on_get", "false"),
                    ("skills_command_raw_filesystem_browsing", "false"),
                    ("skills_command_provider_calls_taken", "0"),
                    ("skills_command_network_actions_taken", "0"),
                    ("skills_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"skills_command_now: {_e(next_action)}",
                    f"skills_command_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"skills_command_reason: {_e(reason)}",
                    "skills_command_safety: read-only skill guidance",
                ]
            ),
            "</section>",
        ]
    )


def _skill_usage(storage: Storage) -> dict[str, dict[str, Any]]:
    usage: dict[str, dict[str, Any]] = {}
    for row in _table_rows(
        storage.db_path,
        "select project_id, skill_tags from tasks order by updated_at desc limit 500",
    ):
        for tag in _json_loads_safe(str(row["skill_tags"] or "[]"), []):
            data = usage.setdefault(str(tag), {"count": 0, "projects": set()})
            data["count"] += 1
            data["projects"].add(str(row["project_id"]))
    return usage


def _skill_line(root: Path, skill: Any, usage: dict[str, dict[str, Any]]) -> str:
    data = usage.get(skill.name, {"count": 0, "projects": set()})
    projects = ", ".join(sorted(data["projects"])) if data["projects"] else (skill.project_id or "none")
    return (
        f"{_e(skill.id)}: name={_e(skill.name)} status={_e(skill.status)} "
        f"usage_count={data['count']} last_used={_e(skill.last_used_at or skill.updated_at)} "
        f"projects_using={_e(projects)} path={_artifact_link(_repo_relative_artifact_path(root, skill.path))}"
    )


def _profiles_page(root: Path) -> str:
    storage = _storage(root)
    profile_path = root / ".clanker" / "profiles.yml"
    profile_lines = profile_path.read_text(encoding="utf-8").splitlines() if profile_path.exists() else []
    configured_profiles = _profile_names(profile_lines)
    storage_profiles = storage.list_profiles(enabled_only=False)
    prepared = [
        "Planning: inactive provider-routing placeholder",
        "Coding: inactive provider-routing placeholder",
        "Review: inactive provider-routing placeholder",
        "Docs: inactive provider-routing placeholder",
        "Cheap model: inactive provider-routing placeholder",
        "Frontier model: inactive provider-routing placeholder",
    ]
    return "".join(
        [
            "<section><h1>Profiles And Routing</h1>",
            "<p class='muted'>Prepared UI and storage readback for future provider routing. Providers remain inactive.</p>",
            _kv(
                [
                    ("profiles_path", ".clanker/profiles.yml" if profile_path.exists() else "missing"),
                    ("configured_profile_count", str(len(configured_profiles))),
                    ("storage_profile_count", str(len(storage_profiles))),
                    ("profile_storage_ready", "true"),
                    ("provider_routing_active", "false"),
                    ("provider_calls_taken", "0"),
                ]
            ),
            "</section>",
            _profiles_command_bar(
                configured_profiles=configured_profiles,
                storage_profiles=storage_profiles,
                future_lanes=prepared,
                profile_path_exists=profile_path.exists(),
            ),
            _list_section(
                "Configured Profiles",
                [_profile_config_line(name) for name in configured_profiles],
                anchor_id="profiles-configured",
            ),
            _list_section(
                "Storage Profiles",
                [_storage_profile_line(profile) for profile in storage_profiles]
                or ["none_recorded_yet provider_routing_active=false provider_calls_taken=0"],
                anchor_id="profiles-storage",
            ),
            _list_section("Future Profile Lanes", prepared, anchor_id="profiles-future"),
            _non_claim_banner(),
        ]
    )


def _profiles_command_bar(
    *,
    configured_profiles: list[str],
    storage_profiles: list[Any],
    future_lanes: list[str],
    profile_path_exists: bool,
) -> str:
    enabled_profiles = [profile for profile in storage_profiles if profile.enabled]
    disabled_profiles = [profile for profile in storage_profiles if not profile.enabled]
    adapter_configured = [
        profile for profile in storage_profiles if profile.adapter_config_json
    ]
    write_allowed = [
        profile
        for profile in storage_profiles
        if str(profile.permissions_json.get("write", "deny")) not in {"deny", "false", "0"}
    ]
    use_for_values = {
        str(item)
        for profile in storage_profiles
        for item in profile.use_for_json
        if item
    }
    first_target = "Planning"
    next_action = "Review future profile lanes"
    target_href = "#profiles-future"
    target_label = "Future Profile Lanes"
    reason = "future_profile_lanes_prepared"
    if storage_profiles:
        first_target = storage_profiles[0].name
        next_action = "Review storage profile"
        target_href = "#profiles-storage"
        target_label = "Storage Profiles"
        reason = "storage_profile_records_available"
    elif configured_profiles:
        first_target = configured_profiles[0]
        next_action = "Review configured profile"
        target_href = "#profiles-configured"
        target_label = "Configured Profiles"
        reason = "configured_profiles_file_available"
    return "".join(
        [
            "<section class='panel profiles-command-bar' data-profiles-command-bar='true'><h2>Profiles Command Bar</h2>",
            "<p class='muted'>One read-only summary of inactive provider-routing preparation and the next local profile review target.</p>",
            _kv(
                [
                    ("profiles_command_status", "available"),
                    ("profiles_command_profiles_file", "present" if profile_path_exists else "missing"),
                    ("profiles_command_configured_profiles", str(len(configured_profiles))),
                    ("profiles_command_storage_profiles", str(len(storage_profiles))),
                    ("profiles_command_enabled_profiles", str(len(enabled_profiles))),
                    ("profiles_command_disabled_profiles", str(len(disabled_profiles))),
                    ("profiles_command_future_lanes", str(len(future_lanes))),
                    ("profiles_command_adapter_configured", str(len(adapter_configured))),
                    ("profiles_command_write_allowed_profiles", str(len(write_allowed))),
                    ("profiles_command_use_for_labels", str(len(use_for_values))),
                    ("profiles_command_first_target", first_target),
                    ("profiles_command_next_action", next_action),
                    (
                        "profiles_command_target_surface",
                        SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>"),
                    ),
                    ("profiles_command_reason", reason),
                    ("profiles_command_provider_routing_active", "false"),
                    ("profiles_command_provider_calls_taken", "0"),
                    ("profiles_command_model_routing_enabled", "false"),
                    ("profiles_command_write_on_get", "false"),
                    ("profiles_command_network_actions_taken", "0"),
                    ("profiles_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"profiles_command_now: {_e(next_action)}",
                    f"profiles_command_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"profiles_command_reason: {_e(reason)}",
                    "profiles_command_safety: read-only inactive provider-routing guidance",
                ]
            ),
            "</section>",
        ]
    )


def _profile_config_line(name: str) -> str:
    return f"profile={_e(name)} source=.clanker/profiles.yml provider=inactive"


def _storage_profile_line(profile: Any) -> str:
    use_for = ",".join(str(item) for item in profile.use_for_json) or "none"
    write_permission = profile.permissions_json.get("write", "unknown")
    adapter_state = "configured" if profile.adapter_config_json else "not_configured"
    return (
        f"profile={_e(profile.name)} label={_e(profile.label)} "
        f"mode={_e(profile.mode)} cost={_e(profile.cost_tier)} "
        f"model={_e(profile.model)} enabled={str(profile.enabled).lower()} "
        f"write={_e(write_permission)} adapter={_e(adapter_state)} "
        f"use_for={_e(use_for)} provider=inactive"
    )


def _profile_names(lines: list[str]) -> list[str]:
    names = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("- name:"):
            names.append(stripped.removeprefix("- name:").strip())
    return names


def _first_run_panel(root: Path, storage: Storage) -> str:
    progress = _first_run_progress(root, storage)
    default_project = progress["default_project"]
    return "".join(
        [
            "<section id='first-run-guide'><h2>First Run Guide</h2>",
            "<p class='muted'>A state-aware path for a new operator to create local ClankerOS state and reach the first delegation handoff without reading docs.</p>",
            _kv(
                [
                    (
                        "first_run_guided_path",
                        "Create project -> Create first goal -> Create first delegation -> Generate context pack -> Run first delegation",
                    ),
                    ("first_run_current_step", progress["current_step"]),
                    ("first_run_project_registered", str(progress["project_registered"]).lower()),
                    ("first_run_goal_created", str(progress["goal_created"]).lower()),
                    ("first_run_delegation_created", str(progress["delegation_created"]).lower()),
                    ("first_run_dogfood_project", progress["dogfood_project"]),
                    ("first_run_default_project", progress["default_project"]),
                    ("first_run_project_path", progress["project_path"]),
                    ("first_run_context_pack_ready", str(progress["context_pack_ready"]).lower()),
                    ("first_run_delegation_completed", str(progress["delegation_completed"]).lower()),
                    ("first_run_next_surface", progress["next_surface"]),
                    ("first_run_next_action", progress["next_action"]),
                    ("first_run_next_reason", progress["next_reason"]),
                    ("first_run_next_action_source", "state_aware_first_run"),
                    ("first_run_context_pack_action", progress["context_pack_action"]),
                    ("first_run_run_delegation_command", progress["run_delegation_command"]),
                    ("first_run_run_delegation_action", progress["run_delegation_action"]),
                    ("first_run_browser_execution_exposed", progress["browser_execution_exposed"]),
                    ("first_run_provider_calls_taken_by_clankeros", "0"),
                    ("first_run_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    "first_run_empty_state_illustration: [project] -> [goal] -> [delegation] -> [handoff]",
                    f"first_run_step: create_project status={_e(_first_run_step_status(progress, 'create_project'))}",
                    f"first_run_step: create_first_goal status={_e(_first_run_step_status(progress, 'create_first_goal'))}",
                    f"first_run_step: create_first_delegation status={_e(_first_run_step_status(progress, 'create_first_delegation'))}",
                    f"first_run_step: generate_context_pack status={_e(_first_run_step_status(progress, 'generate_context_pack'))}",
                    f"first_run_step: run_first_delegation status={_e(_first_run_step_status(progress, 'run_first_delegation'))}",
                    "Create project: register a local git repository.",
                    "Create first goal: materialize a goal, plan, and planned tasks.",
                    "Generate context pack: prepare the local context artifacts needed before the first delegation run.",
                    "Run first delegation: follow the Goal page next action and confirm the local run-delegation form.",
                    "<code>python3 -m agent_os.cli demo</code>: populate deterministic local demo data.",
                ]
            ),
            "<h3>Create Project</h3>",
            _input_form(
                "register-project",
                {},
                {
                    "name": default_project,
                    "path": str(root),
                    "test_command": "python3 -m pytest -q",
                    "allowed_write_roots": str(root),
                },
            ),
            "<h3>Create First Goal</h3>",
            _input_form(
                "create-goal",
                {},
                {
                    "project_id": default_project,
                    "prompt": "Make ClankerOS easier to operate from the browser.",
                    "created_by_profile": "planner",
                },
            ),
            "</section>",
        ]
    )


def _first_run_progress(root: Path, storage: Storage) -> dict[str, Any]:
    projects = storage.list_registered_projects()
    goals = _goal_rows(storage, limit=100)
    goal_row = goals[0] if goals else None
    goal_id = str(goal_row["id"]) if goal_row is not None else ""
    default_project = (
        str(goal_row["project_id"])
        if goal_row is not None
        else (projects[0].name if projects else "clankeros")
    )
    delegations = storage.list_subagent_delegations(goal_id) if goal_id else []
    delegation = delegations[0] if delegations else None
    context_pack_ready = False
    delegation_completed = False
    context_pack_action = "pending_until_delegation_exists"
    run_delegation_command = "pending_until_context_pack_ready"
    run_delegation_action = "pending_until_context_pack_ready"
    browser_execution_exposed = "false"
    if delegation is not None:
        metadata = load_delegation_result_metadata(delegation)
        context_pack_ready = _delegation_has_context_pack(root, delegation, metadata)
        delegation_completed = delegation.status == "completed"
        context_pack_action = f"/actions/context-pack delegation_id={delegation.id}"
        if context_pack_ready:
            run_delegation_command = f"python3 -m agent_os.cli run-delegation {delegation.id}"
            run_delegation_action = f"/actions/run-delegation delegation_id={delegation.id}"
            browser_execution_exposed = "confirmed_local_only"
    project_registered = bool(projects)
    goal_created = goal_row is not None
    delegation_created = delegation is not None
    if not project_registered:
        current_step = "create_project"
        next_surface: str | SafeHtml = SafeHtml("<a href='/goals'>/goals</a>")
        next_action = "Register ClankerOS project"
        next_reason = "no_project_registered"
    elif not goal_created:
        current_step = "create_first_goal"
        next_surface = SafeHtml("<a href='/goals'>/goals</a>")
        next_action = "Create first goal"
        next_reason = "no_goal_created"
    elif not delegation_created:
        current_step = "create_first_delegation"
        next_surface = SafeHtml(f"<a href='/goals/{quote(goal_id)}'>/goals/{_e(goal_id)}</a>")
        next_action = "Open goal to create scout delegation"
        next_reason = "goal_ready_for_delegation"
    elif not context_pack_ready:
        current_step = "generate_context_pack"
        next_surface = SafeHtml(f"<a href='/goals/{quote(goal_id)}'>/goals/{_e(goal_id)}</a>")
        next_action = "Generate context pack"
        next_reason = "delegation_waiting_for_context_pack"
    elif not delegation_completed:
        current_step = "run_first_delegation"
        next_surface = SafeHtml(f"<a href='/goals/{quote(goal_id)}'>/goals/{_e(goal_id)}</a>")
        next_action = "Run delegation"
        next_reason = "context_pack_ready"
    else:
        current_step = "first_delegation_complete"
        next_surface = SafeHtml(f"<a href='/goals/{quote(goal_id)}'>/goals/{_e(goal_id)}</a>")
        next_action = "Review first delegation evidence"
        next_reason = "first_delegation_completed"
    return {
        "project_registered": project_registered,
        "goal_created": goal_created,
        "delegation_created": delegation_created,
        "dogfood_project": "clankeros",
        "project_path": str(root),
        "context_pack_ready": context_pack_ready,
        "delegation_completed": delegation_completed,
        "current_step": current_step,
        "next_surface": next_surface,
        "next_action": next_action,
        "next_reason": next_reason,
        "context_pack_action": context_pack_action,
        "run_delegation_command": run_delegation_command,
        "run_delegation_action": run_delegation_action,
        "browser_execution_exposed": browser_execution_exposed,
        "default_project": default_project,
        "complete": delegation_completed,
    }


def _first_run_step_status(progress: dict[str, Any], step: str) -> str:
    if step == "create_project":
        return "done" if progress["project_registered"] else "current"
    if step == "create_first_goal":
        if progress["goal_created"]:
            return "done"
        return "current" if progress["project_registered"] else "waiting_for_project"
    if step == "create_first_delegation":
        if progress["delegation_created"]:
            return "done"
        return "current" if progress["goal_created"] else "waiting_for_goal"
    if step == "generate_context_pack":
        if progress["context_pack_ready"]:
            return "done"
        if progress["delegation_created"]:
            return "current"
        return "waiting_for_delegation" if progress["goal_created"] else "waiting_for_goal"
    if step == "run_first_delegation":
        if progress["delegation_completed"]:
            return "done"
        if progress["context_pack_ready"]:
            return "current"
        if progress["delegation_created"]:
            return "waiting_for_context_pack"
        return "waiting_for_delegation" if progress["goal_created"] else "waiting_for_goal"
    return "unknown"


def _load_workspace_state(root: Path) -> dict[str, str]:
    path = _workspace_path(root)
    if not path.exists():
        return {
            "open_project": "",
            "open_goal": "",
            "filters": "",
            "expanded_panels": "",
            "last_viewed_artifact": "",
            "updated_by": "operator",
            "updated_at": "never",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    return {key: str(data.get(key, "")) for key in [
        "open_project",
        "open_goal",
        "filters",
        "expanded_panels",
        "last_viewed_artifact",
        "updated_by",
        "updated_at",
    ]}


def _write_workspace_state(root: Path, state: dict[str, str]) -> dict[str, Any]:
    path = _workspace_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "open_project": state.get("open_project", "").strip(),
        "open_goal": state.get("open_goal", "").strip(),
        "filters": state.get("filters", "").strip(),
        "expanded_panels": state.get("expanded_panels", "").strip(),
        "last_viewed_artifact": state.get("last_viewed_artifact", "").strip(),
        "updated_by": state.get("updated_by", "operator").strip() or "operator",
        "updated_at": utc_now(),
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"workspace_path": path, "status": "saved", **payload}


def _remember_delegation_workspace(
    root: Path,
    storage: Storage,
    delegation_id: str,
    *,
    artifact_path: str | Path | None,
    updated_by: str,
) -> dict[str, Any] | None:
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        return None
    try:
        goal = storage.get_goal(delegation.parent_goal_id)
    except KeyError:
        return None
    return _write_workspace_state(
        root,
        {
            **_load_workspace_state(root),
            "open_project": goal.project_id,
            "open_goal": goal.id,
            "last_viewed_artifact": _repo_relative_artifact_path(root, artifact_path),
            "updated_by": updated_by,
        },
    )


def _workspace_path(root: Path) -> Path:
    return root / ".clanker" / "app" / "workspace.json"


def _safe_local_return_path(value: str | None) -> str:
    candidate = (value or "").strip()
    parsed = urlparse(candidate)
    if (
        not candidate.startswith("/")
        or candidate.startswith("//")
        or parsed.scheme
        or parsed.netloc
        or "\n" in candidate
        or "\r" in candidate
    ):
        return ""
    return candidate


def _json_loads_safe(value: str, fallback: Any) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


@dataclass(frozen=True)
class GoalNextAction:
    action: str
    href: str
    reason: str


def _goals(root: Path) -> str:
    storage = _storage(root)
    rows = _goal_rows(storage, limit=100)
    if not rows:
        return "".join(
            [
                "<section><h1>Goal Cockpit</h1>",
                "<p class='muted'>Everything in ClankerOS revolves around a Goal. No goals exist yet in this local state.</p>",
                "</section>",
                _goal_board_command_bar(
                    root,
                    storage,
                    rows=rows,
                    active=[],
                    paused=[],
                    completed=[],
                ),
                _first_run_panel(root, storage),
                _non_claim_banner(),
            ]
        )
    active = [row for row in rows if _goal_bucket(row) == "active"]
    paused = [row for row in rows if _goal_bucket(row) == "paused"]
    completed = [row for row in rows if _goal_bucket(row) == "completed"]
    return "".join(
        [
            "<section><h1>Goal Cockpit</h1>",
            "<p class='muted'>Daily operator home for active, paused, and completed goals. Each goal owns project intent, phase, evidence, approvals, incidents, memory, and remaining work.</p>",
            _kv(
                [
                    ("active_goals", str(len(active))),
                    ("paused_goals", str(len(paused))),
                    ("completed_goals", str(len(completed))),
                    ("goal_first_navigation", "true"),
                    ("external_effects_created", "false"),
                ]
            ),
            "</section>",
            _goal_board_command_bar(
                root,
                storage,
                rows=rows,
                active=active,
                paused=paused,
                completed=completed,
            ),
            _goal_creation_panel(storage, rows),
            _list_section("Active Goals", [_goal_index_line(root, storage, row) for row in active]),
            _list_section("Paused Goals", [_goal_index_line(root, storage, row) for row in paused]),
            _list_section("Completed Goals", [_goal_index_line(root, storage, row) for row in completed]),
            _first_run_panel(root, storage),
            _non_claim_banner(),
        ]
    )


def _goal_creation_panel(storage: Storage, rows: list[sqlite3.Row]) -> str:
    projects = storage.list_registered_projects()
    project_names = [str(project.name) for project in projects]
    if not project_names:
        return _list_section(
            "Start Another Goal",
            [
                "goal_creation_form_available: false",
                "goal_creation_reason: no_registered_projects",
                "project_surface: <a href='/projects'>/projects</a>",
            ],
        )
    lead_project = str(rows[0]["project_id"] or "")
    default_project = lead_project if lead_project in project_names else project_names[0]
    return "".join(
        [
            "<section id='goal-start-another'><h2>Start Another Goal</h2>",
            "<p class='muted'>Create the next local goal from the cockpit without switching to the CLI.</p>",
            _kv(
                [
                    ("goal_creation_form_available", "true"),
                    ("goal_creation_project_count", str(len(project_names))),
                    ("goal_creation_default_project", default_project),
                    ("goal_creation_project_options", ", ".join(project_names)),
                    ("goal_creation_confirmation_required", "true"),
                    ("goal_creation_provider_calls_taken_by_clankeros", "0"),
                    ("goal_creation_network_actions_taken", "0"),
                    ("goal_creation_external_effects_created", "false"),
                ]
            ),
            _input_form(
                "create-goal",
                {},
                {
                    "project_id": default_project,
                    "prompt": "Describe the next local coding goal.",
                    "created_by_profile": "planner",
                },
            ),
            "</section>",
        ]
    )


def _goal_board_command_bar(
    root: Path,
    storage: Storage,
    *,
    rows: list[sqlite3.Row],
    active: list[sqlite3.Row],
    paused: list[sqlite3.Row],
    completed: list[sqlite3.Row],
) -> str:
    selected_row, source = _goal_board_selected_row(root, rows, active, paused, completed)
    if selected_row is None:
        first_run = _first_run_progress(root, storage)
        lines = [
            f"goal_board_now: {_e(first_run['next_action'])}",
            f"goal_board_click: {first_run['next_surface']}",
            (
                "goal_board_first_run: "
                f"step={_e(first_run['current_step'])} "
                f"reason={_e(first_run['next_reason'])}"
            ),
            "goal_board_safety: read-only board guidance; confirmed forms remain below",
        ]
        return "".join(
            [
                "<section class='panel goal-board-command-bar' data-goal-board-command-bar='true'><h2>Goal Board Command Bar</h2>",
                "<p class='muted'>One board-level pointer for a fresh or empty Goal cockpit.</p>",
                _kv(
                    [
                        ("goal_board_status", "first_run"),
                        ("goal_board_total_goals", "0"),
                        ("goal_board_active_goals", "0"),
                        ("goal_board_paused_goals", "0"),
                        ("goal_board_completed_goals", "0"),
                        ("goal_board_priority_source", "first_run"),
                        ("goal_board_primary_goal", "none"),
                        ("goal_board_primary_project", first_run["default_project"]),
                        ("goal_board_primary_phase", "First run"),
                        ("goal_board_primary_action", first_run["next_action"]),
                        ("goal_board_primary_surface", first_run["next_surface"]),
                        ("goal_board_primary_reason", first_run["next_reason"]),
                        ("goal_board_first_run_step", first_run["current_step"]),
                        ("goal_board_action_form_available", "true"),
                        ("goal_board_action_form_surface", SafeHtml("<a href='#first-run-guide'>First Run Guide</a>")),
                        ("goal_board_resume_surface", SafeHtml("<a href='/resume'>/resume</a>")),
                        ("goal_board_write_on_get", "false"),
                        ("goal_board_provider_calls_taken_by_clankeros", "0"),
                        ("goal_board_network_actions_taken", "0"),
                        ("goal_board_external_effects_created", "false"),
                    ]
                ),
                _ul(lines),
                "</section>",
            ]
        )

    goal_id = str(selected_row["id"])
    state = _goal_state(root, storage, goal_id)
    goal = state["goal"]
    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    action_form = _goal_next_action_form(state, next_action)
    open_incidents = sum(1 for row in state["incidents"] if row["status"] == "open")
    open_recommendations = sum(
        1 for row in state["recommendations"] if row["status"] == "open"
    )
    open_tasks = sum(
        1
        for task in state["tasks"]
        if task.status not in {"completed", "cancelled"}
    )
    pending_approvals = (
        _count_status(state["worktree_approvals"], "pending_operator_approval")
        + _count_status(state["commit_approvals"], "pending_operator_approval")
        + _count_status(state["publications"], "pending_operator_approval")
    )
    waiting_items = open_incidents + open_recommendations + pending_approvals
    label = _compact_label(goal.title or goal.description or goal.id, 72)
    goal_surface = SafeHtml(f"<a href='/goals/{quote(goal.id)}'>{_e(label)}</a>")
    project_surface = SafeHtml(
        f"<a href='/projects/{quote(goal.project_id)}'>{_e(goal.project_id)}</a>"
    )
    next_surface = SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>")
    lines = [
        f"goal_board_now: {_e(next_action.action)}",
        f"goal_board_click: <a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>",
        f"goal_board_open: <a href='/goals/{quote(goal.id)}'>{_e(goal.id)}</a>",
        (
            "goal_board_waiting: "
            f"approvals={pending_approvals} incidents={open_incidents} "
            f"recommendations={open_recommendations}"
        ),
        f"goal_board_progress: {_e(_goal_progress_label(state))}",
        "goal_board_safety: read-only local board guidance",
    ]
    return "".join(
        [
            "<section class='panel goal-board-command-bar' data-goal-board-command-bar='true'><h2>Goal Board Command Bar</h2>",
            "<p class='muted'>One board-level recommendation before the active, paused, and completed lanes.</p>",
            _kv(
                [
                    ("goal_board_status", "available"),
                    ("goal_board_total_goals", str(len(rows))),
                    ("goal_board_active_goals", str(len(active))),
                    ("goal_board_paused_goals", str(len(paused))),
                    ("goal_board_completed_goals", str(len(completed))),
                    ("goal_board_priority_source", source),
                    ("goal_board_primary_goal", goal_surface),
                    ("goal_board_primary_project", project_surface),
                    ("goal_board_primary_phase", phase),
                    ("goal_board_primary_action", next_action.action),
                    ("goal_board_primary_surface", next_surface),
                    ("goal_board_primary_reason", next_action.reason),
                    ("goal_board_progress", _goal_progress_label(state)),
                    ("goal_board_open_tasks", str(open_tasks)),
                    ("goal_board_waiting_items", str(waiting_items)),
                    ("goal_board_pending_approvals", str(pending_approvals)),
                    ("goal_board_open_incidents", str(open_incidents)),
                    ("goal_board_open_recommendations", str(open_recommendations)),
                    ("goal_board_action_form_available", str(bool(action_form)).lower()),
                    ("goal_board_action_form_surface", next_surface),
                    ("goal_board_resume_surface", SafeHtml("<a href='/resume'>/resume</a>")),
                    (
                        "goal_board_create_goal_surface",
                        SafeHtml("<a href='#goal-start-another'>Start Another Goal</a>"),
                    ),
                    ("goal_board_write_on_get", "false"),
                    ("goal_board_provider_calls_taken_by_clankeros", "0"),
                    ("goal_board_network_actions_taken", "0"),
                    ("goal_board_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _goal_board_selected_row(
    root: Path,
    rows: list[sqlite3.Row],
    active: list[sqlite3.Row],
    paused: list[sqlite3.Row],
    completed: list[sqlite3.Row],
) -> tuple[sqlite3.Row | None, str]:
    saved_goal = str(_load_workspace_state(root).get("open_goal") or "").strip()
    if saved_goal:
        for row in rows:
            if str(row["id"]) == saved_goal:
                return row, "saved_goal"
    if active:
        return active[0], "active_goal"
    if paused:
        return paused[0], "paused_goal"
    if completed:
        return completed[0], "completed_goal"
    return None, "first_run"


def _goal_detail(root: Path, goal_id: str) -> str:
    storage = _storage(root)
    state = _goal_state(root, storage, goal_id)
    goal = state.get("goal")
    if goal is None:
        return "<p class='error'>Goal not found.</p>"
    next_action = _goal_next_action(root, state)
    phase = _goal_current_phase(state)
    return "".join(
        [
            _goal_live_state(),
            f"<section id='goal-summary' class='hero'><h1>Goal {_e(goal.id)}</h1>",
            f"<p>{_e(goal.title or goal.description)}</p>",
            _kv(
                [
                    ("project", SafeHtml(f"<a href='/projects/{quote(goal.project_id)}'>{_e(goal.project_id)}</a>")),
                    ("status", goal.status),
                    ("current_phase", phase),
                    ("goal_live_refresh_interval_seconds", "5"),
                ]
            ),
            "</section>",
            _goal_section_index(),
            _goal_command_bar(root, state, phase, next_action),
            _goal_daily_loop(root, state, phase, next_action),
            _goal_workflow_map(root, state, next_action),
            _goal_phase_banner(root, state, phase, next_action),
            _goal_next_action_card(state, next_action),
            _goal_next_recommendation_section(state, next_action),
            _goal_resume_snapshot(root, state),
            _goal_overview(state),
            _goal_risk_section(state),
            _goal_completion_criteria(state),
            _goal_completion_readiness(root, state, next_action),
            _goal_progress(state),
            _goal_timeline(root, state),
            _goal_activity_log(root, state),
            _goal_delegation_section(root, state),
            _goal_run_section(root, state),
            _goal_approval_section(root, state),
            _list_section(
                "Goal Incidents",
                _goal_incident_lines(root, state),
                "/incidents",
                anchor_id="goal-incidents",
            ),
            _goal_evidence_section(root, state),
            _list_section("Artifacts", _goal_artifact_lines(root, state), anchor_id="goal-artifacts"),
            _goal_artifact_explorer(root, state),
            _list_section("Memory", _goal_memory_lines(root, state), anchor_id="goal-memory"),
            _list_section("Skills Used", _goal_skill_lines(root, state), anchor_id="goal-skills-used"),
            _goal_git_status(root, state),
            _goal_verification_evidence(root, state),
            _goal_operator_notes_section(root, state),
            _list_section(
                "Remaining Work",
                _goal_remaining_work_lines(root, state, next_action),
                anchor_id="goal-remaining-work",
            ),
            _non_claim_banner(),
        ]
    )


def _goal_live_state() -> str:
    return "".join(
        [
            "<section id='goal-live-state' class='panel' data-live-refresh='goal'><h2>Goal Live State</h2>",
            "<p class='muted'>Keeps this goal page current while preserving local form edits.</p>",
            _kv(
                [
                    ("goal_live_refresh_enabled", "true"),
                    ("goal_live_refresh_interval_seconds", "5"),
                    ("goal_live_refresh_mode", "local_page_reload"),
                    ("goal_live_refresh_pause_when_editing", "true"),
                    ("goal_live_refresh_pause_when_hidden", "true"),
                    ("goal_live_refresh_network_scope", "local_browser_loopback_only"),
                    ("goal_live_refresh_external_effects_created", "false"),
                ]
            ),
            """
<script data-live-refresh-script='goal'>
(function() {
  var intervalMs = 5000;
  function refreshPaused() {
    var active = document.activeElement;
    var tag = active && active.tagName ? active.tagName.toLowerCase() : "";
    return document.hidden || tag === "input" || tag === "textarea" || tag === "select" || Boolean(active && active.isContentEditable);
  }
  function tick() {
    if (!refreshPaused()) {
      window.location.reload();
      return;
    }
    window.setTimeout(tick, intervalMs);
  }
  window.setTimeout(tick, intervalMs);
})();
</script>""",
            "</section>",
        ]
    )


def _goal_section_index() -> str:
    sections = [
        ("Summary", "goal-summary"),
        ("Live state", "goal-live-state"),
        ("Command bar", "goal-command-bar"),
        ("Daily loop", "goal-daily-loop"),
        ("Workflow map", "goal-workflow-map"),
        ("Current phase", "goal-current-phase"),
        ("Next action", "goal-next-action"),
        ("Next recommendation", "goal-next-recommendation"),
        ("Resume snapshot", "goal-resume-snapshot"),
        ("Overview", "goal-overview"),
        ("Progress", "goal-progress"),
        ("Timeline", "goal-timeline"),
        ("Activity log", "goal-activity-log"),
        ("Risk level", "goal-risk"),
        ("Completion criteria", "goal-completion-criteria"),
        ("Completion readiness", "goal-completion-readiness"),
        ("Delegation command", "goal-delegation-command-bar"),
        ("Delegations", "goal-delegations"),
        ("Run command", "goal-run-command-bar"),
        ("Runs", "goal-runs"),
        ("Approval command", "goal-approval-command-bar"),
        ("Approvals", "goal-approvals"),
        ("Incidents", "goal-incidents"),
        ("Evidence command", "goal-evidence-command-bar"),
        ("Evidence", "goal-evidence"),
        ("Artifacts", "goal-artifacts"),
        ("Artifact explorer", "goal-artifact-explorer"),
        ("Memory", "goal-memory"),
        ("Skills used", "goal-skills-used"),
        ("Git status", "goal-git-status"),
        ("Verification command", "goal-verification-command-bar"),
        ("Verification evidence", "goal-verification-evidence"),
        ("Operator notes", "goal-operator-notes"),
        ("Remaining work", "goal-remaining-work"),
    ]
    links = [
        f"<a href='#{_e(anchor)}'>{_e(label)}</a>"
        for label, anchor in sections
    ]
    return (
        "<section id='goal-section-index'><h2>Goal Section Index</h2>"
        + _kv(
            [
                ("goal_section_index_status", "available"),
                ("goal_section_count", str(len(sections))),
                ("goal_section_index_write_on_get", "false"),
                ("goal_section_index_external_effects_created", "false"),
            ]
        )
        + _ul(links)
        + "</section>"
    )


def _goal_workflow_map(
    root: Path,
    state: dict[str, Any],
    next_action: GoalNextAction,
) -> str:
    gates, counts, current_gate = _goal_workflow_gate_summary(root, state, next_action)
    done = counts.get("done", 0)
    pending = counts.get("pending", 0)
    waiting = counts.get("waiting", 0)
    total = len(gates)
    items: list[str] = []
    for index, (name, status) in enumerate(gates, start=1):
        label = name.replace("_", " ")
        marker = "current" if name == current_gate else status
        next_label = (
            f" next={_e(next_action.action)}"
            if name == current_gate and current_gate != "complete"
            else ""
        )
        items.append(
            "<li "
            f"data-workflow-gate='{_e(name)}' "
            f"data-gate-status='{_e(status)}' "
            f"data-gate-marker='{_e(marker)}'>"
            f"<span class='workflow-map-index'>{index}</span> "
            f"<strong>{_e(label)}</strong> "
            f"status={_e(status)} marker={_e(marker)}{next_label}</li>"
        )
    return "".join(
        [
            "<section id='goal-workflow-map' class='panel goal-workflow-map' data-goal-workflow-map='true'><h2>Goal Workflow Map</h2>",
            "<p class='muted'>A top-level lifecycle rail for the Goal, from scout delegation through manual publish.</p>",
            _kv(
                [
                    ("workflow_map_status", "available"),
                    ("workflow_map_current_gate", current_gate),
                    ("workflow_map_next_action", next_action.action),
                    (
                        "workflow_map_next_surface",
                        SafeHtml(
                            f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"
                        ),
                    ),
                    ("workflow_map_progress", f"{done}/{total} gates done"),
                    ("workflow_map_done_count", str(done)),
                    ("workflow_map_pending_count", str(pending)),
                    ("workflow_map_waiting_count", str(waiting)),
                    ("workflow_map_source", "goal_remaining_work_gates"),
                    ("workflow_map_write_on_get", "false"),
                    ("workflow_map_network_actions_taken", "0"),
                    ("workflow_map_external_effects_created", "false"),
                ]
            ),
            "<ol class='workflow-map-rail'>",
            "".join(items),
            "</ol>",
            "</section>",
        ]
    )


def _goal_workflow_gate_summary(
    root: Path,
    state: dict[str, Any],
    next_action: GoalNextAction,
) -> tuple[list[tuple[str, str]], dict[str, int], str]:
    gate_lines = _goal_remaining_work_gate_lines(root, state, next_action)
    gates: list[tuple[str, str]] = []
    for line in gate_lines:
        if not line.startswith("remaining_work_gate: "):
            continue
        parts = line.removeprefix("remaining_work_gate: ").split()
        if not parts:
            continue
        name = parts[0]
        status = "unknown"
        for part in parts[1:]:
            if part.startswith("status="):
                status = part.removeprefix("status=")
                break
        gates.append((name, status))
    counts: dict[str, int] = {}
    for _, status in gates:
        counts[status] = counts.get(status, 0) + 1
    current_gate = next(
        (name for name, status in gates if status == "pending"),
        next((name for name, status in gates if status == "waiting"), "complete"),
    )
    return gates, counts, current_gate


def _goal_command_bar(
    root: Path,
    state: dict[str, Any],
    phase: str,
    next_action: GoalNextAction,
) -> str:
    goal = state["goal"]
    open_incidents = sum(1 for row in state["incidents"] if row["status"] == "open")
    open_recommendations = sum(
        1 for row in state["recommendations"] if row["status"] == "open"
    )
    open_tasks = sum(
        1 for task in state["tasks"] if task.status not in {"completed", "cancelled"}
    )
    pending_approvals = (
        _count_status(state["worktree_approvals"], "pending_operator_approval")
        + _count_status(state["commit_approvals"], "pending_operator_approval")
        + _count_status(state["publications"], "pending_operator_approval")
    )
    waiting_items = open_incidents + open_recommendations + pending_approvals
    latest_ci = _latest_ci_evidence_record(root, project_id=goal.project_id)
    ci_status = "missing"
    ci_source = "none"
    if latest_ci is not None:
        ci_source, ci_record = latest_ci
        ci_status = str(ci_record.status)
    attention = _goal_operator_attention(phase, next_action)
    progress = _goal_progress_label(state)
    return "".join(
        [
            "<section id='goal-command-bar' class='panel goal-command-bar' data-goal-command-bar='true'><h2>Goal Command Bar</h2>",
            "<p class='muted'>The shortest useful readback for this goal: state, click, waiting work, proof, and safety boundary.</p>",
            _kv(
                [
                    ("goal_command_bar_mode", "goal"),
                    ("goal_command_bar_goal", goal.id),
                    ("goal_command_bar_phase", phase),
                    ("goal_command_bar_attention", attention),
                    ("goal_command_bar_primary_action", next_action.action),
                    (
                        "goal_command_bar_primary_surface",
                        SafeHtml(
                            f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"
                        ),
                    ),
                    ("goal_command_bar_reason", next_action.reason),
                    ("goal_command_bar_progress", progress),
                    ("goal_command_bar_open_tasks", str(open_tasks)),
                    ("goal_command_bar_waiting_items", str(waiting_items)),
                    ("goal_command_bar_pending_approvals", str(pending_approvals)),
                    ("goal_command_bar_open_incidents", str(open_incidents)),
                    ("goal_command_bar_open_recommendations", str(open_recommendations)),
                    ("goal_command_bar_resume_surface", SafeHtml("<a href='/resume'>/resume</a>")),
                    ("goal_command_bar_ci_status", ci_status),
                    ("goal_command_bar_ci_source", ci_source),
                    (
                        "goal_command_bar_ci_surface",
                        SafeHtml("<a href='/verification'>/verification</a>"),
                    ),
                    ("goal_command_bar_write_on_get", "false"),
                    ("goal_command_bar_network_actions_taken", "0"),
                    ("goal_command_bar_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_command_now: {_e(attention)}",
                    f"goal_command_click: <a href='{_e(next_action.href)}'>{_e(next_action.action)}</a>",
                    f"goal_command_progress: {_e(progress)}",
                    (
                        "goal_command_waiting: "
                        f"approvals={pending_approvals} "
                        f"incidents={open_incidents} "
                        f"recommendations={open_recommendations}"
                    ),
                    "goal_command_resume: <a href='/resume'>/resume</a>",
                    (
                        "goal_command_ci: "
                        f"status={_e(ci_status)} source={_e(ci_source)} "
                        "surface=<a href='/verification'>/verification</a>"
                    ),
                ]
            ),
            "</section>",
        ]
    )


def _goal_daily_loop(
    root: Path,
    state: dict[str, Any],
    phase: str,
    next_action: GoalNextAction,
) -> str:
    goal = state["goal"]
    workspace = _load_workspace_state(root)
    saved_goal = str(workspace.get("open_goal") or "").strip()
    saved_project = str(workspace.get("open_project") or "").strip()
    saved_artifact = str(workspace.get("last_viewed_artifact") or "").strip()
    latest_artifact = _goal_latest_artifact_path(root, state)
    workspace_matches_goal = saved_goal == goal.id
    workspace_matches_project = saved_project == goal.project_id
    artifact_matches_latest = (
        bool(latest_artifact)
        and saved_artifact == latest_artifact
    )
    resume_ready = (
        workspace_matches_goal
        and workspace_matches_project
        and (artifact_matches_latest or not latest_artifact)
    )
    open_incidents = sum(1 for row in state["incidents"] if row["status"] == "open")
    open_recommendations = sum(
        1 for row in state["recommendations"] if row["status"] == "open"
    )
    pending_approvals = (
        _count_status(state["worktree_approvals"], "pending_operator_approval")
        + _count_status(state["commit_approvals"], "pending_operator_approval")
        + _count_status(state["publications"], "pending_operator_approval")
    )
    waiting_items = open_incidents + open_recommendations + pending_approvals
    form_available = bool(_goal_next_action_form(state, next_action))
    if open_incidents:
        unblock_surface = SafeHtml("<a href='/incidents'>/incidents</a>")
        unblock_action = "Inspect incident"
        unblock_reason = "open_incidents"
    elif pending_approvals:
        unblock_surface = SafeHtml("<a href='/approvals'>/approvals</a>")
        unblock_action = "Review approval"
        unblock_reason = "pending_approvals"
    elif open_recommendations:
        unblock_surface = SafeHtml("<a href='/incidents'>/incidents</a>")
        unblock_action = "Review recommendation"
        unblock_reason = "open_recommendations"
    else:
        unblock_surface = SafeHtml("<a href='#goal-remaining-work'>Remaining Work</a>")
        unblock_action = "Inspect remaining work"
        unblock_reason = "no_blockers"
    finish_status = "ready" if resume_ready else "needs_workspace_save"
    latest_artifact_value: str | SafeHtml = (
        SafeHtml(_artifact_link(latest_artifact)) if latest_artifact else "none"
    )
    saved_artifact_value: str | SafeHtml = (
        SafeHtml(_artifact_link(saved_artifact)) if saved_artifact else "none"
    )
    finish_form = _input_form(
        "save-workspace",
        {
            "open_project": goal.project_id,
            "open_goal": goal.id,
            "return_to": f"/goals/{goal.id}",
        },
        {
            "filters": f"goal:{goal.id}",
            "expanded_panels": "daily-loop,next-action,timeline,evidence,artifacts,notes",
            "last_viewed_artifact": latest_artifact,
            "updated_by": "goal-daily-loop",
        },
    )
    return "".join(
        [
            "<section id='goal-daily-loop' class='panel goal-daily-loop' data-goal-daily-loop='true'><h2>Goal Daily Loop</h2>",
            "<p class='muted'>Start, continue, unblock, and finish this goal from local browser state with a confirmed local resume save.</p>",
            _kv(
                [
                    ("goal_daily_loop_status", "available"),
                    ("goal_daily_loop_goal", goal.id),
                    ("goal_daily_loop_project", goal.project_id),
                    ("goal_daily_loop_phase", phase),
                    ("goal_daily_loop_start_surface", SafeHtml("<a href='/resume'>/resume</a>")),
                    ("goal_daily_loop_next_action", next_action.action),
                    (
                        "goal_daily_loop_next_surface",
                        SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"),
                    ),
                    ("goal_daily_loop_next_form_available", str(form_available).lower()),
                    ("goal_daily_loop_waiting_items", str(waiting_items)),
                    ("goal_daily_loop_pending_approvals", str(pending_approvals)),
                    ("goal_daily_loop_open_incidents", str(open_incidents)),
                    ("goal_daily_loop_open_recommendations", str(open_recommendations)),
                    ("goal_daily_loop_unblock_action", unblock_action),
                    ("goal_daily_loop_unblock_surface", unblock_surface),
                    ("goal_daily_loop_unblock_reason", unblock_reason),
                    ("goal_daily_loop_finish_status", finish_status),
                    ("goal_daily_loop_finish_action", "save-workspace"),
                    ("goal_daily_loop_finish_form_available", "true"),
                    ("goal_daily_loop_finish_confirmation_required", "true"),
                    (
                        "goal_daily_loop_finish_surface",
                        SafeHtml("<a href='#goal-resume-snapshot'>Goal Resume Snapshot</a>"),
                    ),
                    (
                        "goal_daily_loop_finish_return_to",
                        SafeHtml(f"<a href='/goals/{quote(goal.id)}'>/goals/{_e(goal.id)}</a>"),
                    ),
                    ("goal_daily_loop_saved_goal_matches_current", str(workspace_matches_goal).lower()),
                    ("goal_daily_loop_saved_project_matches_current", str(workspace_matches_project).lower()),
                    ("goal_daily_loop_saved_artifact_matches_latest", str(artifact_matches_latest).lower()),
                    ("goal_daily_loop_latest_artifact", latest_artifact_value),
                    ("goal_daily_loop_saved_artifact", saved_artifact_value),
                    ("goal_daily_loop_source", "goal_state_and_workspace"),
                    ("goal_daily_loop_write_on_get", "false"),
                    ("goal_daily_loop_network_actions_taken", "0"),
                    ("goal_daily_loop_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_daily_loop_step: start status={'ready' if workspace_matches_goal else 'needs_saved_goal'} surface=<a href='/resume'>/resume</a>",
                    f"goal_daily_loop_step: continue action={_e(next_action.action)} surface=<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>",
                    f"goal_daily_loop_step: unblock action={_e(unblock_action)} surface={unblock_surface} waiting={waiting_items}",
                    f"goal_daily_loop_step: finish status={_e(finish_status)} surface=<a href='#goal-resume-snapshot'>Goal Resume Snapshot</a>",
                    "goal_daily_loop_safety: confirmed local workspace save only",
                ]
            ),
            "<h3>Finish Today</h3>",
            "<p class='muted'>Save this goal, current filters, expanded panels, and latest artifact as tomorrow's resume point. This writes only `.clanker/app/workspace.json` after confirmation.</p>",
            finish_form,
            "</section>",
        ]
    )


def _goal_rows(storage: Storage, *, limit: int) -> list[sqlite3.Row]:
    return _table_rows(
        storage.db_path,
        """
        select * from goals
        order by updated_at desc, created_at desc, id desc
        limit ?
        """,
        (limit,),
    )


def _goal_bucket(row: sqlite3.Row) -> str:
    status = str(row["status"]).lower()
    if status in {"completed", "done", "closed"}:
        return "completed"
    if status in {"paused", "blocked", "waiting", "waiting_approval"}:
        return "paused"
    return "active"


def _goal_index_line(root: Path, storage: Storage, row: sqlite3.Row) -> str:
    state = _goal_state(root, storage, str(row["id"]))
    next_action = _goal_next_action(root, state)
    return (
        f"<a href='/goals/{quote(str(row['id']))}'>{_e(row['title'] or row['description'])}</a>: "
        f"project={_e(row['project_id'])} status={_e(row['status'])} "
        f"phase={_e(_goal_current_phase(state))} "
        f"next_action={_e(next_action.action)} "
        f"progress={_e(_goal_progress_label(state))} "
        f"remaining_work={_e(_goal_remaining_work_summary(state))}"
    )


def _goal_remaining_work_summary(state: dict[str, Any]) -> str:
    open_tasks = len([task for task in state["tasks"] if task.status != "completed"])
    open_incidents = len([row for row in state["incidents"] if row["status"] == "open"])
    open_recommendations = len(
        [row for row in state["recommendations"] if row["status"] == "open"]
    )
    return (
        f"open_tasks:{open_tasks} "
        f"open_incidents:{open_incidents} "
        f"open_recommendations:{open_recommendations}"
    )


def _goal_state(root: Path, storage: Storage, goal_id: str) -> dict[str, Any]:
    try:
        goal = storage.get_goal(goal_id)
    except KeyError:
        return {"goal": None}
    tasks = storage.list_tasks(goal_id)
    task_ids = {task.id for task in tasks}
    delegations = storage.list_subagent_delegations(goal_id)
    delegation_ids = {delegation.id for delegation in delegations}
    worktree_approvals = [
        item
        for item in list_coder_worktree_approvals(root, limit=200)
        if item.delegation_id in delegation_ids
    ]
    worktree_runs = [
        item
        for item in list_coder_worktree_runs(root, limit=200)
        if item.delegation_id in delegation_ids
    ]
    commit_approvals = [
        item
        for item in list_coder_worktree_commit_approvals(root, limit=200)
        if item.delegation_id in delegation_ids
    ]
    publications = [
        item
        for item in list_coder_publications(root, limit=200)
        if item.delegation_id in delegation_ids
    ]
    incidents = _table_rows(
        storage.db_path,
        "select * from incidents where goal_id = ? order by created_at desc, id desc",
        (goal_id,),
    )
    recommendations = _table_rows(
        storage.db_path,
        "select * from task_recommendations where goal_id = ? order by created_at desc, id desc",
        (goal_id,),
    )
    run_rows = _table_rows(
        storage.db_path,
        "select * from runs where goal_id = ? order by started_at desc, id desc",
        (goal_id,),
    )
    event_rows = _table_rows(
        storage.db_path,
        "select * from events where goal_id = ? order by created_at asc, id asc",
        (goal_id,),
    )
    steering_reviews = storage.list_recent_steering_reviews(limit=20, goal_id=goal_id)
    prep_packets = [
        item
        for item in list_coder_prep_packets(root)
        if item.get("source", {}).get("delegation_id") in delegation_ids
    ]
    worktree_plans = [
        item
        for item in list_coder_worktree_plan_packets(root)
        if item.get("source", {}).get("delegation_id") in delegation_ids
    ]
    risks = [task.risk_level for task in tasks]
    skill_tags = sorted({tag for task in tasks for tag in task.skill_tags})
    plans = storage.list_plans(goal_id)
    latest_plan = plans[-1] if plans else None
    plan_steps = storage.list_plan_steps(latest_plan.id) if latest_plan else []
    sprint_contract = storage.get_latest_sprint_contract(goal_id)
    return {
        "root": root,
        "goal": goal,
        "plans": plans,
        "latest_plan": latest_plan,
        "plan_steps": plan_steps,
        "sprint_contract": sprint_contract,
        "tasks": tasks,
        "task_ids": task_ids,
        "delegations": delegations,
        "delegation_ids": delegation_ids,
        "runs": run_rows,
        "events": event_rows,
        "worktree_approvals": worktree_approvals,
        "worktree_runs": worktree_runs,
        "commit_approvals": commit_approvals,
        "publications": publications,
        "incidents": incidents,
        "recommendations": recommendations,
        "steering_reviews": steering_reviews,
        "prep_packets": prep_packets,
        "worktree_plans": worktree_plans,
        "risk_level": _highest_risk(risks),
        "skill_tags": skill_tags,
    }


def _goal_current_phase(state: dict[str, Any]) -> str:
    goal = state.get("goal")
    if goal is None:
        return "Missing"
    if goal.status == "completed":
        return "Completed"
    if goal.status == "paused":
        return "Paused"
    if any(str(row["status"]) == "open" for row in state["incidents"]):
        return "Blocked"
    if any(task.status in {"failed", "blocked"} for task in state["tasks"]):
        return "Blocked"
    if _count_status(state["publications"], "ready_for_operator"):
        return "Ready to publish"
    if _count_status(state["publications"], "approved"):
        return "Ready to publish"
    if _count_status(state["publications"], "pending_operator_approval"):
        return "Waiting for approval"
    if _count_status(state["commit_approvals"], "committed"):
        return "Ready to publish"
    if _count_status(state["commit_approvals"], "approved"):
        return "Ready to commit"
    if _count_status(state["commit_approvals"], "pending_operator_approval"):
        return "Waiting for approval"
    completed_runs = [run for run in state["worktree_runs"] if run.status == "completed"]
    if completed_runs:
        reviewed = [
            run
            for run in completed_runs
            if _run_review_gate_state(state["root"], run).get("commit_request_form_available")
        ]
        return "Ready to commit" if reviewed else "Needs review"
    if any(run.status == "running" for run in state["worktree_runs"]):
        return "Running"
    if _count_status(state["worktree_approvals"], "pending_operator_approval"):
        return "Waiting for approval"
    if _count_status(state["worktree_approvals"], "approved"):
        return "Ready to run"
    if state["worktree_plans"]:
        return "Waiting for approval"
    if state["prep_packets"]:
        return "Planning worktree"
    if any(_goal_delegation_has_handoff(state, delegation) for delegation in state["delegations"]):
        return "Coder prep"
    if any(delegation.status == "completed" for delegation in state["delegations"]):
        return "Implementation handoff"
    if any(delegation.status in {"pending", "running"} for delegation in state["delegations"]):
        return "Running"
    if state["tasks"]:
        return "Ready for delegation"
    return "Goal accepted"


def _goal_phase_banner(
    root: Path,
    state: dict[str, Any],
    phase: str,
    next_action: GoalNextAction,
) -> str:
    latest_item = _goal_latest_timeline_item(root, state)
    latest_activity = latest_item.get("message") if latest_item else "none"
    return "".join(
        [
            "<section id='goal-current-phase' class='banner goal-phase-banner' aria-live='polite'><h2>Current Phase</h2>",
            f"<p class='phase-callout'><strong>{_e(phase)}</strong></p>",
            _kv(
                [
                    ("current_phase_banner", phase),
                    ("current_phase_is_large_banner", "true"),
                    ("phase_reason", _goal_phase_reason(root, state, phase)),
                    ("operator_attention", _goal_operator_attention(phase, next_action)),
                    ("next_recommended_action", next_action.action),
                    ("next_action_surface", SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>")),
                    ("latest_activity", latest_activity or "none"),
                    ("operator_always_knows_what_is_happening", "true"),
                    ("phase_banner_external_effects_created", "false"),
                ]
            ),
            "</section>",
        ]
    )


def _goal_latest_timeline_item(root: Path, state: dict[str, Any]) -> dict[str, str] | None:
    items = _goal_timeline_items(root, state)
    return items[-1] if items else None


def _goal_phase_reason(root: Path, state: dict[str, Any], phase: str) -> str:
    if phase == "Completed":
        return "goal is marked completed"
    if phase == "Paused":
        return "goal status is paused and can be resumed locally"
    if phase == "Blocked":
        open_incident = next((row for row in state["incidents"] if row["status"] == "open"), None)
        if open_incident is not None:
            return f"open incident requires inspection: {open_incident['summary']}"
        blocked_tasks = [
            task
            for task in state["tasks"]
            if task.status in {"failed", "blocked"}
        ]
        if blocked_tasks:
            return f"{len(blocked_tasks)} task(s) are failed or blocked"
        return "blocked state detected"
    if phase == "Ready to publish":
        if _count_status(state["publications"], "ready_for_operator"):
            return "publication handoff is ready for manual push/PR outside ClankerOS"
        if _count_status(state["publications"], "approved"):
            return "publication is approved and needs a local handoff artifact"
        if _count_status(state["commit_approvals"], "committed"):
            return "local commit exists and publication request can be created"
        return "publication gate is available"
    if phase == "Ready to commit":
        if _count_status(state["commit_approvals"], "approved"):
            return "commit approval is granted; local worktree commit can be recorded"
        reviewed = [
            run
            for run in state["worktree_runs"]
            if run.status == "completed"
            and _run_review_gate_state(root, run).get("commit_request_form_available")
        ]
        if reviewed:
            return "reviewed worktree run is ready for commit request"
        return "commit gate is available"
    if phase == "Needs review":
        return "completed worktree run needs a review artifact before commit request"
    if phase == "Waiting for approval":
        if _count_status(state["publications"], "pending_operator_approval"):
            return "publication approval is pending operator decision"
        if _count_status(state["commit_approvals"], "pending_operator_approval"):
            return "commit approval is pending operator decision"
        if _count_status(state["worktree_approvals"], "pending_operator_approval"):
            return "worktree approval is pending operator decision"
        if state["worktree_plans"]:
            return "worktree plan exists and needs an approval request"
        return "operator approval is required before continuing"
    if phase == "Running":
        if any(run.status == "running" for run in state["worktree_runs"]):
            return "approved worktree execution is running"
        if any(delegation.status in {"pending", "running"} for delegation in state["delegations"]):
            return "delegation is pending or running; browser execution remains unexposed"
        return "local workflow step is running"
    if phase == "Ready to run":
        return "worktree execution approval is granted; run the bounded local action or use the CLI fallback"
    if phase == "Planning worktree":
        return "coder prep exists and a bounded worktree plan is the next artifact"
    if phase == "Coder prep":
        return "implementation handoff is available and coder prep is next"
    if phase == "Implementation handoff":
        return "delegation result is complete and implementation handoff/coder prep is next"
    if phase == "Ready for delegation":
        return "goal has planned tasks and needs a scout delegation"
    if phase == "Goal accepted":
        return "goal exists and needs planning or task setup"
    return "phase read from local goal state"


def _goal_operator_attention(phase: str, next_action: GoalNextAction) -> str:
    if phase == "Blocked":
        return f"Resolve: {next_action.action}"
    if phase == "Running":
        return f"Watch: {next_action.action}"
    if phase == "Completed":
        return "Done: inspect evidence before closing"
    if phase in {
        "Waiting for approval",
        "Needs review",
        "Ready to commit",
        "Ready to publish",
        "Ready to run",
        "Planning worktree",
        "Coder prep",
        "Implementation handoff",
        "Ready for delegation",
        "Paused",
        "Goal accepted",
    }:
        return f"Act: {next_action.action}"
    return f"Next: {next_action.action}"


def _goal_next_action(root: Path, state: dict[str, Any]) -> GoalNextAction:
    goal = state.get("goal")
    if goal is None:
        return GoalNextAction("select_existing_goal", "/goals", "goal_not_found")
    if goal.status == "completed":
        return GoalNextAction("Review completed goal evidence", f"/goals/{quote(goal.id)}", "goal_status_completed")
    if goal.status == "paused":
        return GoalNextAction("Resume paused goal", f"/goals/{quote(goal.id)}", "goal_status_paused")
    open_incident = next((row for row in state["incidents"] if row["status"] == "open"), None)
    if open_incident is not None:
        return GoalNextAction("Inspect incident", "/incidents", str(open_incident["summary"]))
    recommendation = next((row for row in state["recommendations"] if row["status"] == "open"), None)
    if recommendation is not None:
        return GoalNextAction("Review recommendation", "/incidents", str(recommendation["reason"]))
    for status, action, href in [
        ("ready_for_operator", "Manual publish outside ClankerOS", None),
        ("approved", "Create publication handoff", None),
        ("pending_operator_approval", "Approve publication", "/approvals"),
    ]:
        publication = next((item for item in state["publications"] if item.status == status), None)
        if publication is not None:
            return GoalNextAction(action, href or f"/runs/{quote(publication.run_id)}", f"publication={publication.id}")
    committed = next((item for item in state["commit_approvals"] if item.status == "committed"), None)
    if committed is not None:
        return GoalNextAction("Create publication request", f"/runs/{quote(committed.run_id)}", f"commit={committed.commit_sha or 'recorded'}")
    approved_commit = next((item for item in state["commit_approvals"] if item.status == "approved"), None)
    if approved_commit is not None:
        return GoalNextAction("Commit approved worktree", f"/runs/{quote(approved_commit.run_id)}", f"approval={approved_commit.id}")
    pending_commit = next((item for item in state["commit_approvals"] if item.status == "pending_operator_approval"), None)
    if pending_commit is not None:
        return GoalNextAction("Approve commit", "/approvals", f"approval={pending_commit.id}")
    completed_run = next((item for item in state["worktree_runs"] if item.status == "completed"), None)
    if completed_run is not None:
        gate = _run_review_gate_state(root, completed_run)
        if gate["commit_request_form_available"]:
            return GoalNextAction("Create commit request", f"/runs/{quote(completed_run.id)}", f"reviewed_run={completed_run.id}")
        return GoalNextAction("Open review", f"/runs/{quote(completed_run.id)}", str(gate["blocked_reason"]))
    pending_worktree = next((item for item in state["worktree_approvals"] if item.status == "pending_operator_approval"), None)
    if pending_worktree is not None:
        return GoalNextAction("Approve worktree", "/approvals", f"approval={pending_worktree.id}")
    approved_worktree = next((item for item in state["worktree_approvals"] if item.status == "approved"), None)
    if approved_worktree is not None:
        return GoalNextAction("Run approved worktree", f"/goals/{quote(goal.id)}", f"approval={approved_worktree.id}")
    if state["worktree_plans"]:
        delegation_id = str(state["worktree_plans"][0].get("source", {}).get("delegation_id") or "")
        return GoalNextAction("Request worktree approval", f"/delegations/{quote(delegation_id)}", "coder_worktree_plan_available")
    if state["prep_packets"]:
        delegation_id = str(state["prep_packets"][0].get("source", {}).get("delegation_id") or "")
        return GoalNextAction("Create worktree plan", f"/delegations/{quote(delegation_id)}", "coder_prep_available")
    completed_delegation = next((item for item in state["delegations"] if item.status == "completed"), None)
    if completed_delegation is not None:
        return GoalNextAction("Run coder prep", f"/delegations/{quote(completed_delegation.id)}", "implementation_handoff_or_result_available")
    if state["delegations"]:
        delegation = state["delegations"][0]
        metadata = load_delegation_result_metadata(delegation)
        if not _delegation_has_context_pack(root, delegation, metadata):
            return GoalNextAction("Generate context pack", f"/goals/{quote(goal.id)}", f"delegation={delegation.id} context_pack_missing")
        return GoalNextAction("Run delegation", f"/goals/{quote(goal.id)}", f"delegation={delegation.id} context_pack_ready_confirmed_browser_action")
    return GoalNextAction("Create scout delegation", f"/goals/{quote(goal.id)}", "goal_has_no_delegation_yet")


def _goal_next_action_form(state: dict[str, Any], next_action: GoalNextAction) -> str:
    if next_action.action == "Create scout delegation":
        return _goal_scout_delegation_form(state)
    if next_action.action == "Resume paused goal":
        return _goal_resume_form(state)
    if next_action.action == "Generate context pack":
        return _goal_context_pack_form(state)
    if next_action.action == "Run delegation":
        return _goal_run_delegation_handoff(state)
    if next_action.action == "Run coder prep":
        return _goal_coder_prep_form(state)
    if next_action.action == "Create worktree plan":
        return _goal_worktree_plan_form(state)
    if next_action.action == "Request worktree approval":
        return _goal_worktree_approval_form(state)
    if next_action.action == "Approve worktree":
        return _goal_approve_worktree_form(state)
    if next_action.action == "Run approved worktree":
        return _goal_run_worktree_handoff(state["root"], state)
    if next_action.action == "Create commit request":
        return _goal_commit_request_form(state["root"], state)
    if next_action.action == "Open review":
        return _goal_review_run_form(state["root"], state)
    if next_action.action == "Approve commit":
        return _goal_approve_commit_form(state)
    if next_action.action == "Commit approved worktree":
        return _goal_commit_worktree_form(state)
    if next_action.action == "Create publication request":
        return _goal_publication_request_form(state)
    if next_action.action == "Approve publication":
        return _goal_approve_publication_form(state)
    if next_action.action == "Create publication handoff":
        return _goal_publication_handoff_form(state)
    if next_action.action == "Manual publish outside ClankerOS":
        return _goal_manual_publish_panel(state["root"], state)
    return ""


def _goal_next_action_card(state: dict[str, Any], next_action: GoalNextAction) -> str:
    form = _goal_next_action_form(state, next_action)
    return (
        "<section id='goal-next-action'><h2>Next Action</h2>"
        + _kv(
            [
                ("recommended_action", next_action.action),
                ("reason", next_action.reason),
                ("open_surface", SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>")),
                ("next_action_form_available", "true" if form else "false"),
                ("external_effects_created", "false"),
            ]
        )
        + form
        + "</section>"
    )


def _goal_next_recommendation_section(
    state: dict[str, Any],
    next_action: GoalNextAction,
) -> str:
    recommendation = next(
        (row for row in state["recommendations"] if row["status"] == "open"),
        None,
    )
    if recommendation is not None:
        evidence_path = str(recommendation["evidence_path"] or "")
        rows: list[tuple[str, str | SafeHtml]] = [
            ("next_recommendation_status", "open_task_recommendation"),
            ("next_recommendation_source", "task_recommendations"),
            ("next_recommendation_id", str(recommendation["id"])),
            ("next_recommendation_type", str(recommendation["recommendation_type"])),
            ("next_recommendation_task_id", str(recommendation["task_id"])),
            ("next_recommendation_action", next_action.action),
            ("next_recommendation_reason", str(recommendation["reason"])),
            ("next_recommendation_surface", SafeHtml("<a href='/incidents'>/incidents</a>")),
            (
                "next_recommendation_evidence",
                SafeHtml(_artifact_link(evidence_path)) if evidence_path else "missing",
            ),
            ("next_recommendation_write_on_get", "false"),
            ("next_recommendation_external_effects_created", "false"),
        ]
    else:
        rows = [
            ("next_recommendation_status", "derived_from_goal_state"),
            ("next_recommendation_source", "current_phase_and_goal_records"),
            ("next_recommendation_action", next_action.action),
            ("next_recommendation_reason", next_action.reason),
            (
                "next_recommendation_surface",
                SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"),
            ),
            ("next_recommendation_form_surface", "Next Action card"),
            ("next_recommendation_write_on_get", "false"),
            ("next_recommendation_external_effects_created", "false"),
        ]
    return (
        "<section id='goal-next-recommendation'><h2>Next Recommendation</h2>"
        "<p class='muted'>Explains why this goal is pointing at the current action.</p>"
        + _kv(rows)
        + "</section>"
    )


def _goal_resume_form(state: dict[str, Any]) -> str:
    goal = state.get("goal")
    if goal is None or goal.status != "paused":
        return "<p class='muted'>resume_goal_form_status: unavailable_until_goal_status_is_paused</p>"
    return "".join(
        [
            "<h3>Resume Paused Goal</h3>",
            "<p class='muted'>Sets this local goal status from paused to active. It does not approve work, run delegations or worktrees, call providers, use the network, push, create a PR, deploy, or mutate external systems.</p>",
            _kv(
                [
                    ("resume_goal_form_available", "true"),
                    ("resume_goal_required_status", "paused"),
                    ("resume_goal_new_status", "active"),
                    ("resume_goal_external_effects_created", "false"),
                ]
            ),
            _input_form(
                "resume-goal",
                {"goal_id": goal.id},
                {
                    "resumed_by": "operator",
                    "note": "Resume paused goal from local app.",
                },
            ),
        ]
    )


def _goal_approve_worktree_form(state: dict[str, Any]) -> str:
    approval = _goal_pending_worktree_approval(state)
    if approval is None:
        return "<p class='muted'>approve_worktree_form_status: unavailable_until_pending_worktree_approval_exists</p>"
    return "".join(
        [
            "<h3>Approve Worktree</h3>",
            "<p class='muted'>Records a local approval decision for the bounded worktree request. It does not run the worktree, edit source files, call a provider, use the network, commit, push, create a PR, or deploy.</p>",
            _input_form(
                "approve-coder-worktree",
                {"approval_id": approval.id},
                {
                    "decided_by": "operator",
                    "note": "Approved bounded execution from goal page",
                },
            ),
        ]
    )


def _goal_run_worktree_handoff(root: Path, state: dict[str, Any]) -> str:
    approval = _goal_approved_worktree_approval(state)
    if approval is None:
        return "<p class='muted'>run_worktree_handoff_status: unavailable_until_worktree_approval_is_approved</p>"
    plan_payload = _goal_worktree_plan_payload(root, approval)
    bounded_task = plan_payload.get("bounded_coding_task") if isinstance(plan_payload.get("bounded_coding_task"), dict) else {}
    project = plan_payload.get("project") if isinstance(plan_payload.get("project"), dict) else {}
    future_run_plan = plan_payload.get("future_run_plan") if isinstance(plan_payload.get("future_run_plan"), dict) else {}
    raw_allowed_files = bounded_task.get("allowed_files", [])
    if not isinstance(raw_allowed_files, list):
        raw_allowed_files = []
    allowed_files = [str(item) for item in raw_allowed_files if isinstance(item, str)]
    raw_verification_commands = future_run_plan.get("suggested_verification_commands", [])
    if not isinstance(raw_verification_commands, list):
        raw_verification_commands = []
    verification_commands = [
        str(item)
        for item in raw_verification_commands
        if isinstance(item, str)
    ]
    default_test_command = str(project.get("default_test_command") or "project_default_test_command")
    verifier = verification_commands[0] if verification_commands else default_test_command
    command_template = (
        f"python3 -m agent_os.cli run-coder-worktree {approval.delegation_id} "
        '--command "<operator-approved bounded command>" --verify'
    )
    default_browser_command = ""
    run_surface = f"/workflow?delegation_id={quote(approval.delegation_id)}"
    expected_run_surface = f"/runs/<new_coder_worktree_run_id>"
    plan_path = approval.source_plan_path or str(plan_payload.get("_path") or "missing")
    return "".join(
        [
            "<h3>Run Approved Worktree</h3>",
            "<p class='muted'>Runs one operator-provided safe local command in the approved isolated worktree after confirmation. The existing backend approval, safe-command, verifier, and bounded-file checks still apply. It does not commit, call providers, use non-loopback network actions, or push, create a PR, or deploy.</p>",
            _kv(
                [
                    ("run_coder_worktree_command_template", command_template),
                    ("run_coder_worktree_form_available", "true"),
                    ("approval_id", approval.id),
                    ("delegation_id", approval.delegation_id),
                    ("approved_plan", _artifact_link(plan_path)),
                    ("source_plan_sha256", approval.source_plan_sha256),
                    ("allowed_files_count", str(len(allowed_files))),
                    ("allowed_files_preview", ", ".join(allowed_files[:5]) or "none"),
                    ("verification_command_with_verify_flag", verifier),
                    ("safe_command_validator", "enabled"),
                    ("allowed_command_prefixes", "python3 -m pytest, python3 -m py_compile, python3 scripts/, npm test"),
                    ("expected_evidence_dir", f".clanker/delegations/{approval.delegation_id}/runs/<new_run_id>/coder_worktree/"),
                    ("return_to_workflow", SafeHtml(f"<a href='{_e(run_surface)}'>{_e(run_surface)}</a>")),
                    ("return_to_run_after_command", expected_run_surface),
                    ("browser_execution_exposed", "confirmed_local_only"),
                    ("copy_only", "false"),
                    ("provider_calls_taken_by_clankeros", "0"),
                    ("network_actions_taken_by_app", "0"),
                    ("external_mutations_taken", "0"),
                ]
            ),
            _input_form(
                "run-coder-worktree",
                {"delegation_id": approval.delegation_id, "verify": "yes"},
                {
                    "command": default_browser_command,
                    "verify_command": verifier,
                },
            ),
        ]
    )


def _goal_commit_request_form(root: Path, state: dict[str, Any]) -> str:
    run = _goal_reviewed_completed_worktree_run(root, state)
    if run is None:
        return "<p class='muted'>commit_request_form_status: unavailable_until_reviewed_completed_run_exists</p>"
    return "".join(
        [
            "<h3>Create Commit Request</h3>",
            "<p class='muted'>Creates a pending local commit approval request from the reviewed worktree evidence. It does not stage, commit, push, create a PR, deploy, call a provider, or use the network.</p>",
            _input_form(
                "coder-commit-request",
                {"run_id": run.id, "requested_by": "operator"},
                {
                    "message": "Implement bounded change from approved worktree run",
                    "note": "Request local commit after review from goal page",
                },
            ),
        ]
    )


def _goal_review_run_form(root: Path, state: dict[str, Any]) -> str:
    run = _goal_unreviewed_completed_worktree_run(root, state)
    if run is None:
        return "<p class='muted'>review_run_form_status: unavailable_until_completed_unreviewed_run_exists</p>"
    review_path = Path("runs") / run.source_run_id / "review.md"
    return "".join(
        [
            "<h3>Create Review</h3>",
            "<p class='muted'>Writes the local human-readable review artifact required before a commit request. It does not approve commits, stage files, commit, push, create a PR, deploy, call a provider, or use the network.</p>",
            _kv(
                [
                    ("coder_worktree_run", run.id),
                    ("source_run_id", run.source_run_id),
                    ("review_artifact", review_path.as_posix()),
                ]
            ),
            _form("review-run", {"run_id": run.id}),
        ]
    )


def _goal_approve_commit_form(state: dict[str, Any]) -> str:
    approval = _goal_pending_commit_approval(state)
    if approval is None:
        return "<p class='muted'>approve_commit_form_status: unavailable_until_pending_commit_approval_exists</p>"
    return "".join(
        [
            "<h3>Approve Commit</h3>",
            "<p class='muted'>Records a local approval decision for the reviewed commit request. It does not stage, commit, push, create a PR, deploy, call a provider, or use the network.</p>",
            _input_form(
                "approve-coder-commit",
                {"approval_id": approval.id},
                {
                    "decided_by": "operator",
                    "note": "Approved local commit from goal page",
                },
            ),
        ]
    )


def _goal_commit_worktree_form(state: dict[str, Any]) -> str:
    approval = _goal_approved_commit_approval(state)
    if approval is None:
        return "<p class='muted'>commit_worktree_form_status: unavailable_until_commit_approval_exists</p>"
    return "".join(
        [
            "<h3>Commit Approved Worktree</h3>",
            "<p class='muted'>Creates one local commit only inside the isolated coder worktree after the existing backend gate re-checks review, source hashes, branch/HEAD, changed files, bounded-file validation, and verifier state. It does not push, create a PR, deploy, call a provider, or use the network.</p>",
            _input_form(
                "commit-coder-worktree",
                {"run_id": approval.run_id, "committed_by": "operator"},
                {"message": approval.commit_message},
            ),
        ]
    )


def _goal_publication_request_form(state: dict[str, Any]) -> str:
    approval = _goal_committed_worktree_approval(state)
    if approval is None:
        return "<p class='muted'>publication_request_form_status: unavailable_until_local_commit_exists</p>"
    return "".join(
        [
            "<h3>Create Publication Request</h3>",
            "<p class='muted'>Creates a pending local publication approval request from the isolated local commit. It does not push, create a PR, deploy, call a provider, or use the network.</p>",
            _input_form(
                "coder-publication-request",
                {
                    "run_id": approval.run_id,
                    "requested_by": "operator",
                    "remote": "origin",
                    "target_branch": "main",
                },
                {"note": "Request publication handoff from goal page"},
            ),
        ]
    )


def _goal_approve_publication_form(state: dict[str, Any]) -> str:
    publication = _goal_pending_publication(state)
    if publication is None:
        return "<p class='muted'>approve_publication_form_status: unavailable_until_pending_publication_approval_exists</p>"
    return "".join(
        [
            "<h3>Approve Publication</h3>",
            "<p class='muted'>Records a local approval decision to prepare publication handoff artifacts. It does not push, create a PR, deploy, call a provider, or use the network.</p>",
            _input_form(
                "approve-coder-publication",
                {"publication_id": publication.id},
                {
                    "decided_by": "operator",
                    "note": "Approved publication handoff from goal page",
                },
            ),
        ]
    )


def _goal_publication_handoff_form(state: dict[str, Any]) -> str:
    publication = _goal_approved_publication(state)
    if publication is None:
        return "<p class='muted'>publication_handoff_form_status: unavailable_until_publication_approval_exists</p>"
    return "".join(
        [
            "<h3>Create Publication Handoff</h3>",
            "<p class='muted'>Writes local publication handoff and PR-body artifacts with suggested manual commands only. It does not push, create a PR, deploy, call a provider, or use the network.</p>",
            _form("coder-publication-handoff", {"run_id": publication.run_id}),
        ]
    )


def _goal_manual_publish_panel(root: Path, state: dict[str, Any]) -> str:
    publication = _goal_ready_publication(state)
    if publication is None:
        return "<p class='muted'>manual_publish_status: unavailable_until_publication_handoff_ready</p>"
    return "".join(
        [
            "<h3>Manual Publish Boundary</h3>",
            "<p class='muted'>Publication handoff is ready. Push and draft PR creation remain outside ClankerOS and must be run manually by the operator.</p>",
            _publication_handoff_commands_panel(root, publication),
            "<h3>Complete Goal</h3>",
            "<p class='muted'>After the operator has finished the manual push/PR work outside ClankerOS, this confirmed local action marks the Goal completed. It does not push, create a PR, deploy, call a provider, or use the network.</p>",
            _input_form(
                "complete-goal",
                {"goal_id": state["goal"].id},
                {
                    "completed_by": "operator",
                    "note": "Manual publication finished outside ClankerOS.",
                },
            ),
        ]
    )


def _goal_pending_worktree_approval(state: dict[str, Any]) -> Any | None:
    return next(
        (
            item
            for item in state.get("worktree_approvals", [])
            if item.status == "pending_operator_approval"
        ),
        None,
    )


def _goal_approved_worktree_approval(state: dict[str, Any]) -> Any | None:
    return next(
        (item for item in state.get("worktree_approvals", []) if item.status == "approved"),
        None,
    )


def _goal_worktree_plan_payload(root: Path, approval: Any) -> dict[str, Any]:
    plan_path = getattr(approval, "source_plan_path", "") or ""
    if not plan_path:
        return {}
    candidate = root / plan_path
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if isinstance(payload, dict):
        payload["_path"] = _repo_relative_artifact_path(root, candidate)
        return payload
    return {}


def _goal_pending_commit_approval(state: dict[str, Any]) -> Any | None:
    return next(
        (
            item
            for item in state.get("commit_approvals", [])
            if item.status == "pending_operator_approval"
        ),
        None,
    )


def _goal_approved_commit_approval(state: dict[str, Any]) -> Any | None:
    return next(
        (item for item in state.get("commit_approvals", []) if item.status == "approved"),
        None,
    )


def _goal_committed_worktree_approval(state: dict[str, Any]) -> Any | None:
    return next(
        (item for item in state.get("commit_approvals", []) if item.status == "committed"),
        None,
    )


def _goal_pending_publication(state: dict[str, Any]) -> Any | None:
    return next(
        (
            item
            for item in state.get("publications", [])
            if item.status == "pending_operator_approval"
        ),
        None,
    )


def _goal_approved_publication(state: dict[str, Any]) -> Any | None:
    return next(
        (item for item in state.get("publications", []) if item.status == "approved"),
        None,
    )


def _goal_ready_publication(state: dict[str, Any]) -> Any | None:
    return next(
        (item for item in state.get("publications", []) if item.status == "ready_for_operator"),
        None,
    )


def _goal_reviewed_completed_worktree_run(root: Path, state: dict[str, Any]) -> Any | None:
    for run in state.get("worktree_runs", []):
        if run.status == "completed" and _run_review_gate_state(root, run)[
            "commit_request_form_available"
        ]:
            return run
    return None


def _goal_unreviewed_completed_worktree_run(root: Path, state: dict[str, Any]) -> Any | None:
    for run in state.get("worktree_runs", []):
        if run.status == "completed" and not _run_review_gate_state(root, run)[
            "commit_request_form_available"
        ]:
            return run
    return None


def _goal_coder_prep_form(state: dict[str, Any]) -> str:
    delegation = _goal_completed_delegation(state)
    if delegation is None:
        return "<p class='muted'>coder_prep_form_status: unavailable_until_delegation_completes</p>"
    return "".join(
        [
            "<h3>Run Coder Prep</h3>",
            "<p class='muted'>Creates the local coder prep packet from the implementation handoff. It does not edit source files, create a worktree, run commands, call a provider, or use the network.</p>",
            _form("coder-prep", {"delegation_id": delegation.id}),
        ]
    )


def _goal_worktree_plan_form(state: dict[str, Any]) -> str:
    delegation_id = _goal_packet_delegation_id(state.get("prep_packets", []))
    if not delegation_id:
        return "<p class='muted'>coder_worktree_plan_form_status: unavailable_until_coder_prep_exists</p>"
    return "".join(
        [
            "<h3>Create Worktree Plan</h3>",
            "<p class='muted'>Creates the approval-gated local worktree plan from coder prep. It does not create a worktree, edit files, run commands, approve work, call a provider, or use the network.</p>",
            _form("coder-worktree-plan", {"delegation_id": delegation_id}),
        ]
    )


def _goal_worktree_approval_form(state: dict[str, Any]) -> str:
    delegation_id = _goal_packet_delegation_id(state.get("worktree_plans", []))
    if not delegation_id:
        return "<p class='muted'>coder_worktree_approval_form_status: unavailable_until_worktree_plan_exists</p>"
    return "".join(
        [
            "<h3>Request Worktree Approval</h3>",
            "<p class='muted'>Creates a pending local approval request for bounded worktree execution. It does not approve execution, create a worktree, run commands, call a provider, or mutate external systems.</p>",
            _input_form(
                "coder-worktree-approval",
                {"delegation_id": delegation_id},
                {
                    "requested_by": "operator",
                    "note": "Approve bounded worktree execution from goal page",
                },
            ),
        ]
    )


def _goal_completed_delegation(state: dict[str, Any]) -> Any | None:
    return next(
        (item for item in state.get("delegations", []) if item.status == "completed"),
        None,
    )


def _goal_packet_delegation_id(packets: list[dict[str, Any]]) -> str:
    for packet in packets:
        source = packet.get("source") if isinstance(packet.get("source"), dict) else {}
        delegation_id = str(source.get("delegation_id") or "").strip()
        if delegation_id:
            return delegation_id
    return ""


def _goal_scout_delegation_form(state: dict[str, Any]) -> str:
    goal = state.get("goal")
    if goal is None:
        return ""
    task = _goal_delegation_target_task(state)
    if task is None:
        return "<p class='muted'>delegate_form_status: unavailable_until_planned_task_exists</p>"
    return "".join(
        [
            "<h3>Create Scout Delegation</h3>",
            "<p class='muted'>Creates a read-only delegation contract for the next planned task. It does not start a subagent or call a provider.</p>",
            _input_form(
                "delegate",
                {
                    "goal_id": goal.id,
                    "task_id": task.id,
                    "profile": "scout",
                },
                {
                    "title": f"Scout {goal.title or goal.description}",
                    "requested_by": "operator",
                },
            ),
        ]
    )


def _goal_delegation_target_task(state: dict[str, Any]) -> Any | None:
    delegated_task_ids = {delegation.parent_task_id for delegation in state.get("delegations", [])}
    for task in state.get("tasks", []):
        if task.id not in delegated_task_ids:
            return task
    return None


def _goal_context_pack_form(state: dict[str, Any]) -> str:
    delegation = _goal_context_pack_target_delegation(state)
    if delegation is None:
        return "<p class='muted'>context_pack_form_status: unavailable_until_delegation_exists</p>"
    return "".join(
        [
            "<h3>Generate Context Pack</h3>",
            "<p class='muted'>Creates or refreshes the local scout context pack for this delegation. It does not run the delegation, call a provider, or use the network.</p>",
            _form("context-pack", {"delegation_id": delegation.id}),
        ]
    )


def _goal_run_delegation_handoff(state: dict[str, Any]) -> str:
    delegation = _goal_context_pack_target_delegation(state, require_missing=False)
    if delegation is None:
        return ""
    command = f"python3 -m agent_os.cli run-delegation {delegation.id}"
    return "".join(
        [
            "<h3>Run Delegation</h3>",
            "<p class='muted'>Runs the existing read-only delegation adapter after confirmation. The backend keeps the same adapter safety checks and incident recording as the CLI path.</p>",
            _kv(
                [
                    ("run_delegation_command", command),
                    ("run_delegation_form_available", "true"),
                    ("browser_execution_exposed", "confirmed_local_only"),
                    ("adapter_safety_checks", "read_only_profile unsafe_command_filter incident_on_failure"),
                    ("provider_calls_taken_by_clankeros", "0"),
                    ("network_actions_taken_by_app", "0"),
                    ("external_mutations_taken", "0"),
                ]
            ),
            _form("run-delegation", {"delegation_id": delegation.id, "operator_id": "operator"}),
        ]
    )


def _goal_context_pack_target_delegation(
    state: dict[str, Any],
    *,
    require_missing: bool = True,
) -> Any | None:
    for delegation in state.get("delegations", []):
        metadata = load_delegation_result_metadata(delegation)
        has_pack = _delegation_has_context_pack(state["root"], delegation, metadata)
        if require_missing and not has_pack:
            return delegation
        if not require_missing and has_pack and delegation.status != "completed":
            return delegation
    return None


def _delegation_has_context_pack(
    root: Path,
    delegation: Any,
    metadata: dict[str, Any],
) -> bool:
    if metadata.get("context_pack_md") or metadata.get("context_pack_json"):
        return True
    context_dir = root / ".clanker" / "delegations" / delegation.id / "context"
    return (context_dir / "context_pack.md").exists() or (context_dir / "context_pack.json").exists()


def _goal_overview(state: dict[str, Any]) -> str:
    goal = state["goal"]
    return "<section id='goal-overview'><h2>Overview</h2>" + _kv(
        [
            ("intent", goal.description),
            ("original_prompt", goal.original_prompt),
            ("created_at", goal.created_at),
            ("updated_at", goal.updated_at),
            ("completed_at", goal.completed_at or "none"),
            ("risk_level", state["risk_level"]),
            ("operator_notes_status", "local_artifact_if_present"),
        ]
    ) + "</section>"


def _goal_risk_section(state: dict[str, Any]) -> str:
    tasks = state.get("tasks", [])
    counts = _risk_counts(tasks)
    contract = state.get("sprint_contract")
    lines = [
        f"goal_risk_level: {_e(state.get('risk_level') or 'unknown')}",
        f"risk_counts: {_e(_risk_counts_label(counts))}",
        f"tasks_with_risk: {len(tasks)}",
        "approval_boundary: high_or_unknown_risk_requires_operator_approval_before_dispatch",
        "external_effects_created: false",
    ]
    risk_notes = getattr(contract, "risk_notes", "") if contract is not None else ""
    if risk_notes:
        lines.append(f"risk_notes: {_e(risk_notes)}")
    for task in tasks:
        lines.append(
            f"{_e(task.id)}: risk={_e(task.risk_level)} status={_e(task.status)} "
            f"type={_e(task.task_type)}"
        )
    return _list_section("Goal Risk", lines, anchor_id="goal-risk")


def _goal_completion_criteria(state: dict[str, Any]) -> str:
    plan = state.get("latest_plan")
    contract = state.get("sprint_contract")
    steps = state.get("plan_steps", [])
    tasks = state.get("tasks", [])
    contract_items = _criteria_items(
        getattr(contract, "acceptance_criteria", "") if contract is not None else ""
    )
    task_items = _task_completion_items(tasks) if not contract_items and not steps else []
    source = (
        "sprint_contract"
        if contract_items
        else ("plan_steps" if steps else ("task_verification_plan" if task_items else "none"))
    )
    completed_steps = sum(1 for step in steps if step.status == "completed")
    completed_tasks = sum(1 for task in tasks if task.status == "completed")
    criteria_count = len(contract_items) if contract_items else (len(steps) if steps else len(task_items))
    progress = (
        f"{completed_steps}/{len(steps)} plan steps completed"
        if steps
        else f"{completed_tasks}/{len(tasks)} tasks completed"
    )
    lines = [
        f"completion_criteria_source: {source}",
        f"completion_criteria_count: {criteria_count}",
        f"completion_progress: {progress}",
    ]
    if plan is not None:
        lines.append(f"latest_plan: {_artifact_link(plan.artifact_path)}")
        lines.append(f"latest_plan_status: {_e(plan.status)}")
    if contract is not None:
        lines.append(f"sprint_contract: {_artifact_link(contract.artifact_path)}")
        lines.append(f"sprint_contract_status: {_e(contract.status)}")
    for item in contract_items:
        lines.append(f"criterion: {_e(item)}")
    for step in steps:
        lines.append(
            f"step {step.order_index}: status={_e(step.status)} "
            f"acceptance={_e(step.acceptance_criteria)} "
            f"verifier={_e(step.verification_command)}"
        )
    for item in task_items:
        lines.append(
            f"task {item['task_id']}: status={_e(item['status'])} "
            f"acceptance={_e(item['acceptance'])}"
        )
    if len(lines) == 3:
        lines.append("completion_criteria_status: none_available")
    return _list_section("Goal Completion Criteria", lines, anchor_id="goal-completion-criteria")


def _goal_completion_readiness(
    root: Path,
    state: dict[str, Any],
    next_action: GoalNextAction,
) -> str:
    goal = state["goal"]
    gates, counts, current_gate = _goal_workflow_gate_summary(root, state, next_action)
    open_tasks = sum(1 for task in state["tasks"] if task.status not in {"completed", "cancelled"})
    open_incidents = sum(1 for row in state["incidents"] if row["status"] == "open")
    open_recommendations = sum(
        1 for row in state["recommendations"] if row["status"] == "open"
    )
    pending_approvals = (
        _count_status(state["worktree_approvals"], "pending_operator_approval")
        + _count_status(state["commit_approvals"], "pending_operator_approval")
        + _count_status(state["publications"], "pending_operator_approval")
    )
    publication = _goal_ready_publication(state)
    total_gates = len(gates)
    done_gates = counts.get("done", 0)
    ready_for_completion = goal.status != "completed" and publication is not None

    if goal.status == "completed":
        readiness_status = "completed"
        readiness_action = "Review completed goal evidence"
        readiness_target = f"<a href='/goals/{quote(goal.id)}'>/goals/{_e(goal.id)}</a>"
        reason = "goal_status_completed"
    elif open_incidents:
        readiness_status = "blocked_by_incidents"
        readiness_action = "Inspect incident"
        readiness_target = "<a href='/incidents'>/incidents</a>"
        reason = "open_incidents"
    elif pending_approvals:
        readiness_status = "waiting_for_operator_approval"
        readiness_action = "Review approval"
        readiness_target = "<a href='/approvals'>/approvals</a>"
        reason = "pending_approvals"
    elif ready_for_completion:
        readiness_status = "ready_for_manual_completion"
        readiness_action = "Complete goal after manual publish"
        readiness_target = "<a href='#goal-completion-readiness'>Goal Completion Readiness</a>"
        reason = "publication_handoff_ready_manual_publish_boundary"
    elif open_tasks or counts.get("pending", 0) or counts.get("waiting", 0):
        readiness_status = "workflow_incomplete"
        readiness_action = next_action.action
        readiness_target = f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"
        reason = f"current_gate={current_gate}"
    else:
        readiness_status = "needs_evidence_review"
        readiness_action = "Review timeline and evidence"
        readiness_target = "<a href='#goal-timeline'>Timeline</a>"
        reason = "no_open_rows_but_completion_not_recorded"

    sections = [
        "<section id='goal-completion-readiness' class='panel goal-completion-readiness' data-goal-completion-readiness='true'><h2>Goal Completion Readiness</h2>",
        "<p class='muted'>Shows whether this Goal can be locally completed yet, based on the current workflow gates, approvals, incidents, and manual publication boundary.</p>",
        _kv(
            [
                ("completion_readiness_status", readiness_status),
                ("completion_readiness_reason", reason),
                ("completion_readiness_goal", goal.id),
                ("completion_readiness_current_gate", current_gate),
                ("completion_readiness_gate_progress", f"{done_gates}/{total_gates} gates done"),
                ("completion_readiness_done_gates", str(done_gates)),
                ("completion_readiness_pending_gates", str(counts.get("pending", 0))),
                ("completion_readiness_waiting_gates", str(counts.get("waiting", 0))),
                ("completion_readiness_open_tasks", str(open_tasks)),
                ("completion_readiness_open_incidents", str(open_incidents)),
                ("completion_readiness_open_recommendations", str(open_recommendations)),
                ("completion_readiness_pending_approvals", str(pending_approvals)),
                (
                    "completion_readiness_publication_handoff_ready",
                    "true" if publication is not None else "false",
                ),
                (
                    "completion_readiness_complete_goal_form_available",
                    "true" if ready_for_completion else "false",
                ),
                (
                    "completion_readiness_next_action",
                    readiness_action,
                ),
                ("completion_readiness_target_surface", SafeHtml(readiness_target)),
                ("completion_readiness_source", "goal_workflow_gates_and_local_status"),
                ("completion_readiness_write_on_get", "false"),
                ("completion_readiness_network_actions_taken", "0"),
                ("completion_readiness_external_effects_created", "false"),
            ]
        ),
        _ul(
            [
                f"completion_readiness_now: {_e(readiness_action)}",
                f"completion_readiness_click: {readiness_target}",
                "completion_readiness_safety: confirmed local completion only after manual publish",
            ]
        ),
    ]
    if ready_for_completion:
        sections.extend(
            [
                "<details class='completion-readiness-action' data-completion-readiness-action='true'>",
                "<summary>Complete Goal</summary>",
                "<p class='muted'>Use this only after manual push/PR work has already happened outside ClankerOS. Confirmation is required and the action records local goal status only.</p>",
                _input_form(
                    "complete-goal",
                    {"goal_id": goal.id},
                    {
                        "completed_by": "operator",
                        "note": "Manual publication finished outside ClankerOS.",
                    },
                ),
                "</details>",
            ]
        )
    sections.append("</section>")
    return "".join(sections)


def _goal_progress(state: dict[str, Any]) -> str:
    tasks = state["tasks"]
    completed_tasks = [task for task in tasks if task.status == "completed"]
    blocked_tasks = [task for task in tasks if task.status in {"blocked", "failed"}]
    total = len(tasks)
    completed = len(completed_tasks)
    progress = (
        "<progress value='{value}' max='{max}' aria-label='Goal task progress'></progress>".format(
            value=completed,
            max=max(total, 1),
        )
    )
    return (
        "<section id='goal-progress'><h2>Progress</h2>"
        + progress
        + _kv(
            [
                ("progress_label", _goal_progress_label(state)),
                ("progress_bar_enabled", "true"),
                ("tasks_completed", f"{completed}/{total}"),
                ("blocked_or_failed_tasks", str(len(blocked_tasks))),
                ("delegations", str(len(state["delegations"]))),
                ("runs", str(len(state["runs"]) + len(state["worktree_runs"]))),
                ("approvals", str(len(state["worktree_approvals"]) + len(state["commit_approvals"]) + len(state["publications"]))),
                ("incidents", str(len(state["incidents"]))),
            ]
        )
        + "</section>"
    )


def _goal_progress_label(state: dict[str, Any]) -> str:
    tasks = state.get("tasks", [])
    if not tasks:
        return "0/0 tasks completed"
    completed = sum(1 for task in tasks if task.status == "completed")
    return f"{completed}/{len(tasks)} tasks completed"


def _goal_resume_snapshot(root: Path, state: dict[str, Any]) -> str:
    goal = state["goal"]
    workspace = _load_workspace_state(root)
    saved_goal = workspace.get("open_goal", "")
    saved_project = workspace.get("open_project", "")
    saved_filters = workspace.get("filters", "").strip()
    saved_panels = workspace.get("expanded_panels", "").strip()
    saved_artifact = workspace.get("last_viewed_artifact", "").strip()
    latest_artifact = _goal_latest_artifact_path(root, state)
    workspace_available = any([saved_goal, saved_project, saved_filters, saved_panels, saved_artifact])
    goal_matches = saved_goal == goal.id
    project_matches = saved_project == goal.project_id
    saved_goal_link = (
        SafeHtml(f"<a href='/goals/{quote(saved_goal)}'>{_e(saved_goal)}</a>")
        if saved_goal
        else "none"
    )
    saved_project_link = (
        SafeHtml(f"<a href='/projects/{quote(saved_project)}'>{_e(saved_project)}</a>")
        if saved_project
        else "none"
    )
    return "".join(
        [
            "<section id='goal-resume-snapshot'><h2>Goal Resume Snapshot</h2>",
            "<p class='muted'>Save and restore the current goal context for the next operator session. This reads saved workspace state on page load and only writes after confirmation.</p>",
            _kv(
                [
                    ("goal_resume_current_goal", SafeHtml(f"<a href='/goals/{quote(goal.id)}'>{_e(goal.id)}</a>")),
                    ("goal_resume_current_project", SafeHtml(f"<a href='/projects/{quote(goal.project_id)}'>{_e(goal.project_id)}</a>")),
                    ("saved_workspace_goal", saved_goal_link),
                    ("saved_workspace_project", saved_project_link),
                    ("workspace_goal_matches_current", "true" if goal_matches else "false"),
                    ("workspace_updated_at", workspace.get("updated_at", "never") or "never"),
                    ("suggested_last_artifact", SafeHtml(_artifact_link(latest_artifact)) if latest_artifact else "none"),
                    ("workspace_surface", SafeHtml("<a href='/workspace'>/workspace</a>")),
                    ("save_workspace_form_available", "true"),
                    ("workspace_auto_write_on_get", "false"),
                    ("external_effects_created", "false"),
                ]
            ),
            "<h3>Goal Workspace Restore State</h3>",
            _kv(
                [
                    ("workspace_restore_available", "true" if workspace_available else "false"),
                    ("workspace_restore_goal_matches_current", "true" if goal_matches else "false"),
                    ("workspace_restore_project_matches_current", "true" if project_matches else "false"),
                    ("workspace_restore_filters", saved_filters or "none"),
                    ("workspace_restore_expanded_panels", saved_panels or "none"),
                    ("workspace_restore_last_artifact", SafeHtml(_artifact_link(saved_artifact)) if saved_artifact else "none"),
                    ("workspace_restore_source", ".clanker/app/workspace.json"),
                    ("workspace_restore_write_on_get", "false"),
                ]
            ),
            "<h3>Remember This Goal</h3>",
            _input_form(
                "save-workspace",
                {"return_to": f"/goals/{goal.id}"},
                {
                    "open_project": goal.project_id,
                    "open_goal": goal.id,
                    "filters": f"goal:{goal.id}",
                    "expanded_panels": "overview,next-action,timeline,evidence,artifacts,notes",
                    "last_viewed_artifact": latest_artifact,
                    "updated_by": "operator-goal",
                },
            ),
            "</section>",
        ]
    )


def _goal_timeline(root: Path, state: dict[str, Any]) -> str:
    items = _goal_timeline_items(root, state)
    operator_note_count = sum(1 for item in items if item.get("kind") == "operator_note")
    artifact_count = sum(1 for item in items if item.get("kind") == "artifact")
    return "".join(
        [
            "<section id='goal-timeline'><h2>Timeline</h2>",
            _goal_timeline_command_bar(state, items),
            _kv(
                [
                    ("timeline_links_enabled", "true"),
                    ("timeline_items", str(len(items))),
                    ("timeline_artifact_records", str(artifact_count)),
                    ("timeline_operator_note_artifacts", str(operator_note_count)),
                    ("operator_note_timeline_external_effects_created", "false"),
                ]
            ),
            _ul([_timeline_line(item) for item in items]),
            "</section>",
        ]
    )


def _goal_timeline_command_bar(
    state: dict[str, Any],
    items: list[dict[str, str]],
) -> str:
    goal = state["goal"]
    latest = items[-1] if items else {}
    latest_href = latest.get("href") or f"/goals/{quote(goal.id)}"
    latest_message = latest.get("message") or "No goal timeline events yet"
    latest_kind = _timeline_item_family(latest) if latest else "none"
    latest_at = _format_time(latest.get("at") or "") if latest else "none"
    family_counts = {
        "artifact": 0,
        "approval": 0,
        "delegation": 0,
        "operator_note": 0,
        "run": 0,
        "task": 0,
    }
    for item in items:
        family = _timeline_item_family(item)
        if family in family_counts:
            family_counts[family] += 1
    lines = [
        f"timeline_command_now: {_e(latest_message)}",
        f"timeline_command_click: <a href='{_e(latest_href)}'>{_e(latest_href)}</a>",
        "timeline_command_review: scan newest event first, then use linked artifacts or approvals",
        "timeline_command_safety: read-only local timeline",
    ]
    return "".join(
        [
            "<div class='panel goal-timeline-command-bar' data-goal-timeline-command-bar='true'><h3>Goal Timeline Command Bar</h3>",
            "<p class='muted'>One scan-friendly summary before the full chronological event list.</p>",
            _kv(
                [
                    ("timeline_command_status", "available" if items else "empty"),
                    ("timeline_command_goal", goal.id),
                    ("timeline_command_items", str(len(items))),
                    ("timeline_command_latest_kind", latest_kind),
                    ("timeline_command_latest_at", latest_at),
                    ("timeline_command_latest_message", latest_message),
                    (
                        "timeline_command_latest_surface",
                        SafeHtml(f"<a href='{_e(latest_href)}'>{_e(latest_href)}</a>"),
                    ),
                    ("timeline_command_artifact_events", str(family_counts["artifact"])),
                    ("timeline_command_approval_events", str(family_counts["approval"])),
                    ("timeline_command_delegation_events", str(family_counts["delegation"])),
                    ("timeline_command_run_events", str(family_counts["run"])),
                    ("timeline_command_task_events", str(family_counts["task"])),
                    ("timeline_command_operator_note_events", str(family_counts["operator_note"])),
                    ("timeline_command_source", "goal_timeline_items"),
                    ("timeline_command_write_on_get", "false"),
                    ("timeline_command_provider_calls_taken", "0"),
                    ("timeline_command_network_actions_taken", "0"),
                    ("timeline_command_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</div>",
        ]
    )


def _timeline_item_family(item: dict[str, str]) -> str:
    kind = str(item.get("kind") or "").strip()
    if kind:
        return kind
    href = str(item.get("href") or "")
    message = str(item.get("message") or "").lower()
    if href.startswith("/artifacts?path="):
        return "artifact"
    if href.startswith("/delegations/") or "delegation" in message or "scout delegated" in message:
        return "delegation"
    if href.startswith("/runs/") or "execution" in message or "review passed" in message:
        return "run"
    if href.startswith("/approvals") or "approval" in message or "approved" in message or "rejected" in message:
        return "approval"
    if "task" in message:
        return "task"
    return "event"


def _goal_activity_log(root: Path, state: dict[str, Any]) -> str:
    items = _goal_timeline_items(root, state)[-12:]
    return "".join(
        [
            "<section id='goal-activity-log'><h2>Activity Log</h2>",
            _kv(
                [
                    ("activity_log_format", "human_readable"),
                    (
                        "activity_log_operator_notes_included",
                        str(any(item.get("kind") == "operator_note" for item in items)).lower(),
                    ),
                    ("activity_log_items", str(len(items))),
                ]
            ),
            _goal_activity_command_bar(state, items),
            _ul([_timeline_line(item) for item in items]),
            "</section>",
        ]
    )


def _goal_activity_command_bar(
    state: dict[str, Any],
    items: list[dict[str, str]],
) -> str:
    goal = state["goal"]
    latest = items[-1] if items else {}
    latest_href = latest.get("href") or f"/goals/{quote(goal.id)}"
    latest_label = latest.get("message") or "No goal activity yet"
    latest_at = _format_time(latest.get("at") or "") if latest else "none"
    operator_notes = sum(1 for item in items if item.get("kind") == "operator_note")
    artifacts = sum(
        1
        for item in items
        if item.get("kind") == "artifact"
        or str(item.get("href") or "").startswith("/artifacts?path=")
    )
    latest_kind = latest.get("kind") or "event"
    return "".join(
        [
            "<section class='panel goal-activity-command-bar' data-goal-activity-command-bar='true'><h3>Goal Activity Command Bar</h3>",
            "<p class='muted'>One read-only summary of the latest human-readable event for this goal.</p>",
            _kv(
                [
                    ("goal_activity_command_status", "available"),
                    ("goal_activity_command_goal", goal.id),
                    ("goal_activity_command_items", str(len(items))),
                    ("goal_activity_command_latest_kind", latest_kind),
                    ("goal_activity_command_latest_at", latest_at),
                    ("goal_activity_command_latest_message", latest_label),
                    (
                        "goal_activity_command_latest_surface",
                        SafeHtml(f"<a href='{_e(latest_href)}'>{_e(latest_href)}</a>"),
                    ),
                    ("goal_activity_command_operator_notes", str(operator_notes)),
                    ("goal_activity_command_artifacts", str(artifacts)),
                    ("goal_activity_command_source", "goal_timeline_items"),
                    ("goal_activity_command_write_on_get", "false"),
                    ("goal_activity_command_network_actions_taken", "0"),
                    ("goal_activity_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_activity_now: {_e(latest_label)}",
                    f"goal_activity_click: <a href='{_e(latest_href)}'>{_e(latest_href)}</a>",
                    "goal_activity_safety: read-only local timeline",
                ]
            ),
            "</section>",
        ]
    )


def _goal_timeline_items(root: Path, state: dict[str, Any]) -> list[dict[str, str]]:
    goal = state["goal"]
    items: list[dict[str, str]] = [
        {
            "at": goal.created_at,
            "message": f"Goal created for project {goal.project_id}.",
            "href": f"/goals/{quote(goal.id)}",
        }
    ]
    for task in state["tasks"]:
        items.append(
            {
                "at": task.created_at,
                "message": f"Task created: {task.task_type}.",
                "href": f"/goals/{quote(goal.id)}",
                "kind": "task",
            }
        )
        if task.updated_at != task.created_at:
            items.append(
                {
                    "at": task.updated_at,
                    "message": f"Task {task.id} status is {task.status}.",
                    "href": f"/goals/{quote(goal.id)}",
                    "kind": "task",
                }
            )
    operator_notes = _goal_operator_notes_path(goal)
    if (root / operator_notes).exists():
        items.append(
            {
                "at": _artifact_time(root, operator_notes.as_posix()) or goal.updated_at,
                "message": "Operator note saved.",
                "href": _artifact_href(root, operator_notes),
                "kind": "operator_note",
            }
        )
    for delegation in state["delegations"]:
        delegation_href = f"/delegations/{quote(delegation.id)}"
        items.append({"at": delegation.created_at, "message": f"Scout delegated: {delegation.title}.", "href": delegation_href})
        if delegation.started_at:
            items.append({"at": delegation.started_at, "message": f"Delegation {delegation.id} started.", "href": delegation_href})
        if delegation.completed_at:
            items.append({"at": delegation.completed_at, "message": f"Execution completed: delegation {delegation.id}.", "href": delegation_href})
        metadata = load_delegation_result_metadata(delegation)
        for label, key in [
            ("Context pack built", "context_pack_md"),
            ("Implementation handoff created", "implementation_handoff_md"),
        ]:
            at = _artifact_time(root, str(metadata.get(key) or ""))
            if at:
                artifact = str(metadata.get(key) or "")
                items.append(
                    {
                        "at": at,
                        "message": f"{label} for {delegation.id}.",
                        "href": _artifact_href(root, artifact),
                    }
                )
    for packet in state["prep_packets"]:
        at = _artifact_time(root, str(packet.get("_path") or ""))
        href = _artifact_href(root, packet.get("_path")) if packet.get("_path") else f"/goals/{quote(goal.id)}"
        items.append({"at": at or goal.updated_at, "message": "Coder prep finished.", "href": href})
    for packet in state["worktree_plans"]:
        at = _artifact_time(root, str(packet.get("_path") or ""))
        href = _artifact_href(root, packet.get("_path")) if packet.get("_path") else f"/goals/{quote(goal.id)}"
        items.append({"at": at or goal.updated_at, "message": "Worktree planned.", "href": href})
    for approval in state["worktree_approvals"]:
        items.append({"at": approval.requested_at, "message": f"Approval requested: worktree execution {approval.id}.", "href": "/approvals"})
        if approval.decided_at:
            items.append(
                {
                    "at": approval.decided_at,
                    "message": _approval_decision_timeline_message(
                        "worktree execution",
                        approval.status,
                        approval.id,
                    ),
                    "href": "/approvals",
                }
            )
    for run in state["worktree_runs"]:
        run_href = f"/runs/{quote(run.id)}"
        items.append({"at": run.started_at, "message": f"Approved worktree execution started: {run.id}.", "href": run_href})
        items.append({"at": run.completed_at, "message": f"Execution {run.status}: {run.id}.", "href": run_href})
        review_state = _run_review_gate_state(root, run)
        if review_state["exists"]:
            review_path = str(review_state["review_path"])
            review_message = (
                f"Review passed for {run.id}."
                if review_state["status"] == "reviewed"
                else f"Review artifact recorded for {run.id}: status={review_state['status']}."
            )
            items.append(
                {
                    "at": _artifact_time(root, review_path) or run.completed_at,
                    "message": review_message,
                    "href": _artifact_href(root, review_path),
                }
            )
    for approval in state["commit_approvals"]:
        run_href = f"/runs/{quote(approval.run_id)}"
        items.append({"at": approval.requested_at, "message": f"Commit approval requested: {approval.id}.", "href": run_href})
        if approval.decided_at:
            items.append(
                {
                    "at": approval.decided_at,
                    "message": _gate_decision_timeline_message(
                        "Commit",
                        approval.status,
                        approval.id,
                    ),
                    "href": "/approvals",
                }
            )
        if approval.commit_artifact_path:
            at = _artifact_time(root, approval.commit_artifact_path)
            if at:
                items.append({"at": at, "message": f"Local commit artifact recorded for {approval.run_id}.", "href": _artifact_href(root, approval.commit_artifact_path)})
    for publication in state["publications"]:
        run_href = f"/runs/{quote(publication.run_id)}"
        items.append({"at": publication.requested_at, "message": f"Publication approval requested: {publication.id}.", "href": run_href})
        if publication.decided_at:
            items.append(
                {
                    "at": publication.decided_at,
                    "message": _gate_decision_timeline_message(
                        "Publication",
                        publication.status,
                        publication.id,
                    ),
                    "href": "/approvals",
                }
            )
        if publication.handoff_at:
            href = _artifact_href(root, publication.handoff_artifact_path) if publication.handoff_artifact_path else run_href
            items.append({"at": publication.handoff_at, "message": f"Publication handoff ready: {publication.id}.", "href": href})
    for row in state["events"]:
        items.append({"at": row["created_at"], "message": str(row["message"]), "href": f"/goals/{quote(goal.id)}"})
    artifact_hrefs = {
        item.get("href", "")
        for item in items
        if item.get("href", "").startswith("/artifacts?path=")
    }
    for record in _goal_artifact_records(root, state):
        href = _artifact_href(root, record["path"])
        if href in artifact_hrefs:
            continue
        artifact_hrefs.add(href)
        items.append(
            {
                "at": _artifact_time(root, record["path"]) or goal.updated_at,
                "message": f"Artifact recorded: {record['label']}.",
                "href": href,
                "kind": "artifact",
            }
        )
    return sorted(items, key=lambda item: item.get("at") or "")


def _approval_decision_timeline_message(kind: str, status: str, item_id: str) -> str:
    if status == "approved":
        return f"Approval granted: {kind} {item_id}."
    if status == "rejected":
        return f"Approval rejected: {kind} {item_id}."
    return f"Approval decision recorded: {kind} {item_id} status={status}."


def _gate_decision_timeline_message(gate: str, status: str, item_id: str) -> str:
    if status == "approved":
        return f"{gate} approved: {item_id}."
    if status == "rejected":
        return f"{gate} rejected: {item_id}."
    return f"{gate} decision recorded: {item_id} status={status}."


def _timeline_line(item: dict[str, str]) -> str:
    timestamp = f"<time>{_e(_format_time(item.get('at') or ''))}</time>"
    message = _e(item.get("message") or "")
    href = item.get("href") or ""
    if href:
        return f"{timestamp} <a class='timeline-link' href='{_e(href)}'>{message}</a>"
    return f"{timestamp} {message}"


def _format_time(value: str) -> str:
    if not value:
        return "unknown"
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
        return parsed.strftime("%H:%M")
    except ValueError:
        return value.split("T")[-1][:5] if "T" in value else value[:16]


def _artifact_time(root: Path, path: str) -> str | None:
    if not path or path == "none":
        return None
    candidate = root / path
    if not candidate.exists():
        return None
    return datetime.fromtimestamp(candidate.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")


def _goal_delegation_lines(state: dict[str, Any]) -> list[str]:
    return [
        f"<a href='/delegations/{quote(delegation.id)}'>{_e(delegation.id)}</a>: status={_e(delegation.status)} profile={_e(delegation.assigned_profile)} title={_e(delegation.title)}"
        for delegation in state["delegations"]
    ]


def _goal_delegation_section(root: Path, state: dict[str, Any]) -> str:
    lines = _goal_delegation_lines(state)
    return _goal_delegation_command_bar(root, state, lines) + _list_section(
        "Delegations",
        lines,
        anchor_id="goal-delegations",
    )


def _goal_delegation_command_bar(
    root: Path,
    state: dict[str, Any],
    delegation_lines: list[str],
) -> str:
    goal = state["goal"]
    delegations = list(state["delegations"])
    pending_delegations = [item for item in delegations if item.status == "pending"]
    running_delegations = [item for item in delegations if item.status == "running"]
    completed_delegations = [item for item in delegations if item.status == "completed"]
    failed_or_blocked_delegations = [
        item for item in delegations if item.status in {"failed", "blocked"}
    ]
    summary_by_delegation: dict[str, dict[str, Any]] = {}
    context_pack_ready = 0
    implementation_handoff_ready = 0
    for delegation in delegations:
        metadata = load_delegation_result_metadata(delegation)
        if _delegation_has_context_pack(root, delegation, metadata):
            context_pack_ready += 1
        summary = summarize_implementation_handoff(root, delegation)
        summary_by_delegation[delegation.id] = summary
        if str(summary["status"]) == "readable":
            implementation_handoff_ready += 1

    selected_delegation = delegations[0] if delegations else None
    latest_delegation_id = "none"
    latest_delegation_status = "none"
    latest_delegation_profile = "none"
    latest_delegation_surface: str | SafeHtml = "none"
    latest_workflow_surface: str | SafeHtml = "none"
    latest_context_pack_status = "none"
    latest_handoff_status = "none"
    next_action = "Create scout delegation"
    target_href = "#goal-next-action"
    target_label = "Next Action"
    reason = "goal has no delegation yet"

    if selected_delegation is not None:
        latest_delegation_id = selected_delegation.id
        latest_delegation_status = selected_delegation.status
        latest_delegation_profile = selected_delegation.assigned_profile
        latest_delegation_surface = SafeHtml(
            f"<a href='/delegations/{quote(selected_delegation.id)}'>"
            f"/delegations/{_e(selected_delegation.id)}</a>"
        )
        latest_workflow_surface = SafeHtml(
            f"<a href='/workflow?delegation_id={quote(selected_delegation.id)}'>"
            f"/workflow?delegation_id={_e(selected_delegation.id)}</a>"
        )
        metadata = load_delegation_result_metadata(selected_delegation)
        latest_context_pack_status = (
            "available"
            if _delegation_has_context_pack(root, selected_delegation, metadata)
            else "missing"
        )
        summary = summary_by_delegation[selected_delegation.id]
        latest_handoff_status = (
            "available" if str(summary["status"]) == "readable" else str(summary["status"])
        )
        delegation_prep = [
            item
            for item in state["prep_packets"]
            if item.get("source", {}).get("delegation_id") == selected_delegation.id
        ]
        delegation_plans = [
            item
            for item in state["worktree_plans"]
            if item.get("source", {}).get("delegation_id") == selected_delegation.id
        ]
        worktree_approvals = list_coder_worktree_approvals(
            root,
            delegation_id=selected_delegation.id,
            limit=50,
        )
        worktree_runs = list_coder_worktree_runs(
            root,
            delegation_id=selected_delegation.id,
            limit=50,
        )
        commit_approvals = list_coder_worktree_commit_approvals(
            root,
            delegation_id=selected_delegation.id,
            limit=50,
        )
        publications = list_coder_publications(
            root,
            delegation_id=selected_delegation.id,
            limit=50,
        )
        token = _delegation_next_action(
            root,
            summary=summary,
            prep_count=len(delegation_prep),
            plan_count=len(delegation_plans),
            worktree_approvals=worktree_approvals,
            worktree_runs=worktree_runs,
            commit_approvals=commit_approvals,
            publications=publications,
        )
        selected_run = worktree_runs[0] if worktree_runs else None
        selected_commit_run_id = next(
            (item.run_id for item in commit_approvals if getattr(item, "run_id", "")),
            "",
        )
        selected_publication_run_id = next(
            (item.run_id for item in publications if getattr(item, "run_id", "")),
            "",
        )
        run_id = (
            selected_run.id
            if selected_run is not None
            else selected_commit_run_id or selected_publication_run_id
        )
        if token == "generate_context_pack":
            next_action = "Generate context pack"
            target_href = "#goal-next-action"
            reason = "selected delegation is missing a context pack"
        elif token == "run_delegation_or_review_implementation_handoff":
            next_action = "Run delegation"
            target_href = "#goal-next-action"
            reason = "implementation handoff is missing or unreadable"
        elif token == "prepare_coder_from_handoff":
            next_action = "Run coder prep"
            target_href = f"/delegations/{quote(selected_delegation.id)}"
            target_label = f"/delegations/{selected_delegation.id}"
            reason = "implementation handoff is ready for bounded coder prep"
        elif token == "prepare_coder_worktree_plan":
            next_action = "Create worktree plan"
            target_href = f"/delegations/{quote(selected_delegation.id)}"
            target_label = f"/delegations/{selected_delegation.id}"
            reason = "coder prep packet is ready for worktree planning"
        elif token == "decide_pending_worktree_approval":
            next_action = "Approve worktree"
            target_href = "/approvals"
            target_label = "/approvals"
            reason = "worktree approval is waiting for an operator decision"
        elif token == "run_approved_worktree_from_cli":
            next_action = "Run approved worktree"
            target_href = "#goal-next-action"
            reason = "worktree execution is approved and needs confirmed local execution"
        elif token == "request_commit_for_reviewed_run":
            next_action = "Create commit request"
            target_href = f"/runs/{quote(run_id)}" if run_id else f"/delegations/{quote(selected_delegation.id)}"
            target_label = f"/runs/{run_id}" if run_id else f"/delegations/{selected_delegation.id}"
            reason = "reviewed coder run is ready for a local commit request"
        elif token == "approve_or_reject_commit_request":
            next_action = "Approve commit"
            target_href = "/approvals"
            target_label = "/approvals"
            reason = "commit approval is waiting for an operator decision"
        elif token == "commit_approved_worktree":
            next_action = "Commit approved worktree"
            target_href = f"/runs/{quote(run_id)}" if run_id else f"/delegations/{quote(selected_delegation.id)}"
            target_label = f"/runs/{run_id}" if run_id else f"/delegations/{selected_delegation.id}"
            reason = "commit approval is granted for the selected delegation"
        elif token == "request_publication_handoff":
            next_action = "Create publication request"
            target_href = f"/runs/{quote(run_id)}" if run_id else f"/delegations/{quote(selected_delegation.id)}"
            target_label = f"/runs/{run_id}" if run_id else f"/delegations/{selected_delegation.id}"
            reason = "local commit is recorded and publication can be requested"
        elif token == "approve_or_reject_publication_request":
            next_action = "Approve publication"
            target_href = "/approvals"
            target_label = "/approvals"
            reason = "publication approval is waiting for an operator decision"
        elif token == "prepare_publication_handoff":
            next_action = "Create publication handoff"
            target_href = f"/runs/{quote(run_id)}" if run_id else f"/delegations/{quote(selected_delegation.id)}"
            target_label = f"/runs/{run_id}" if run_id else f"/delegations/{selected_delegation.id}"
            reason = "publication approval is granted for the selected delegation"
        elif token == "manual_operator_push_pr_outside_clankeros":
            next_action = "Use publication handoff"
            target_href = f"/runs/{quote(run_id)}" if run_id else f"/delegations/{quote(selected_delegation.id)}"
            target_label = f"/runs/{run_id}" if run_id else f"/delegations/{selected_delegation.id}"
            reason = "publication handoff is ready for manual push or PR outside ClankerOS"
        else:
            next_action = "Review delegation workflow"
            target_href = f"/workflow?delegation_id={quote(selected_delegation.id)}"
            target_label = f"/workflow?delegation_id={selected_delegation.id}"
            reason = "selected delegation has workflow state to inspect"

    if next_action == "Create commit request":
        status = "ready_for_commit_request"
    elif not delegations:
        status = "empty"
    elif failed_or_blocked_delegations:
        status = "attention_required"
    elif running_delegations:
        status = "running"
    elif implementation_handoff_ready:
        status = "handoff_available"
    elif context_pack_ready:
        status = "context_pack_ready"
    else:
        status = "delegations_available"

    target = SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>")
    return "".join(
        [
            "<section id='goal-delegation-command-bar' class='panel goal-delegation-command-bar' data-goal-delegation-command-bar='true'><h3>Goal Delegation Command Bar</h3>",
            "<p class='muted'>Goal-scoped delegation posture before the detailed scout, context-pack, and handoff rows.</p>",
            _kv(
                [
                    ("goal_delegation_command_goal", goal.id),
                    ("goal_delegation_command_project", goal.project_id),
                    ("goal_delegation_command_status", status),
                    ("goal_delegation_command_items", str(len(delegation_lines))),
                    ("goal_delegation_command_total_delegations", str(len(delegations))),
                    ("goal_delegation_command_pending_delegations", str(len(pending_delegations))),
                    ("goal_delegation_command_running_delegations", str(len(running_delegations))),
                    ("goal_delegation_command_completed_delegations", str(len(completed_delegations))),
                    (
                        "goal_delegation_command_failed_or_blocked_delegations",
                        str(len(failed_or_blocked_delegations)),
                    ),
                    ("goal_delegation_command_context_packs_ready", str(context_pack_ready)),
                    (
                        "goal_delegation_command_implementation_handoffs_ready",
                        str(implementation_handoff_ready),
                    ),
                    ("goal_delegation_command_coder_prep_packets", str(len(state["prep_packets"]))),
                    ("goal_delegation_command_worktree_plans", str(len(state["worktree_plans"]))),
                    ("goal_delegation_command_latest_delegation", latest_delegation_id),
                    ("goal_delegation_command_latest_status", latest_delegation_status),
                    ("goal_delegation_command_latest_profile", latest_delegation_profile),
                    ("goal_delegation_command_latest_surface", latest_delegation_surface),
                    ("goal_delegation_command_workflow_surface", latest_workflow_surface),
                    ("goal_delegation_command_latest_context_pack_status", latest_context_pack_status),
                    ("goal_delegation_command_latest_handoff_status", latest_handoff_status),
                    ("goal_delegation_command_next_action", next_action),
                    ("goal_delegation_command_target_surface", target),
                    ("goal_delegation_command_reason", reason),
                    (
                        "goal_delegation_command_source",
                        "goal_delegations_context_and_handoff_state",
                    ),
                    ("goal_delegation_command_write_on_get", "false"),
                    ("goal_delegation_command_provider_calls_taken", "0"),
                    ("goal_delegation_command_network_actions_taken", "0"),
                    ("goal_delegation_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_delegation_now: {_e(next_action)}",
                    f"goal_delegation_click: {target}",
                    (
                        "goal_delegation_latest: "
                        f"{_e(latest_delegation_id)} status={_e(latest_delegation_status)} "
                        f"context={_e(latest_context_pack_status)} handoff={_e(latest_handoff_status)}"
                    ),
                    "goal_delegation_safety: read-only local delegation posture",
                ]
            ),
            "</section>",
        ]
    )


def _goal_run_lines(root: Path, state: dict[str, Any]) -> list[str]:
    lines = [
        f"<a href='/runs/{quote(str(row['id']))}'>{_e(row['id'])}</a>: status={_e(row['status'])} project={_e(row['project_id'])}"
        for row in state["runs"]
    ]
    lines.extend(_coder_run_line(root, run) for run in state["worktree_runs"])
    return lines


def _goal_run_section(root: Path, state: dict[str, Any]) -> str:
    lines = _goal_run_lines(root, state)
    return _goal_run_command_bar(root, state, lines) + _list_section(
        "Runs",
        lines,
        anchor_id="goal-runs",
    )


def _goal_run_command_bar(
    root: Path,
    state: dict[str, Any],
    run_lines: list[str],
) -> str:
    goal = state["goal"]
    task_runs = list(state["runs"])
    worktree_runs = list(state["worktree_runs"])
    completed_worktree_runs = [
        run for run in worktree_runs if run.status == "completed"
    ]
    running_worktree_runs = [
        run for run in worktree_runs if run.status == "running"
    ]
    failed_worktree_runs = [
        run for run in worktree_runs if run.status == "failed"
    ]
    review_states = [
        _run_review_gate_state(root, run)
        for run in worktree_runs
    ]
    reviewed_runs = [
        run
        for run, review in zip(worktree_runs, review_states, strict=False)
        if review["commit_request_form_available"]
    ]
    review_blocked_runs = [
        run
        for run, review in zip(worktree_runs, review_states, strict=False)
        if run.status == "completed" and not review["commit_request_form_available"]
    ]
    changed_files_count = sum(len(run.changed_files) for run in worktree_runs)
    outside_allowed_files = sum(len(run.outside_allowed_files) for run in worktree_runs)
    verification_failed_runs = [
        run
        for run in worktree_runs
        if run.verification_exit_code is not None and run.verification_exit_code != 0
    ]
    selected_run = worktree_runs[0] if worktree_runs else None
    selected_task_run = task_runs[0] if task_runs and selected_run is None else None

    latest_run_id = "none"
    latest_run_status = "none"
    latest_run_surface: str | SafeHtml = "none"
    latest_review_status = "none"
    latest_changed_files_count = "0"
    latest_diff_summary = "none"
    latest_diff_surface: str | SafeHtml = "none"
    next_action = "Create run through the next Goal action"
    target_href = "#goal-next-action"
    target_label = "Next Action"
    reason = "no local run records are attached to this goal"

    if selected_run is not None:
        latest_run_id = selected_run.id
        latest_run_status = selected_run.status
        latest_run_surface = SafeHtml(
            f"<a href='/runs/{quote(selected_run.id)}'>/runs/{_e(selected_run.id)}</a>"
        )
        review_gate = _run_review_gate_state(root, selected_run)
        latest_review_status = str(review_gate["status"])
        change_summary = coder_worktree_change_summary(root, selected_run)
        latest_changed_files_count = change_summary["changed_files_count"]
        latest_diff_summary = change_summary["diff_summary"]
        latest_diff_surface = _artifact_link(
            str(Path(selected_run.evidence_path) / "diff.patch")
        )
        commit_approvals = [
            item
            for item in state["commit_approvals"]
            if item.run_id == selected_run.id
        ]
        publications = [
            item
            for item in state["publications"]
            if item.run_id == selected_run.id
        ]
        next_action, raw_target_href, target_label, reason = _run_command_next_action(
            selected_run,
            review_gate=review_gate,
            commit_approvals=commit_approvals,
            publications=publications,
        )
        target_href = (
            f"/runs/{quote(selected_run.id)}{raw_target_href}"
            if raw_target_href.startswith("#")
            else raw_target_href
        )
    elif selected_task_run is not None:
        latest_run_id = str(selected_task_run["id"])
        latest_run_status = str(selected_task_run["status"])
        latest_run_surface = SafeHtml(
            f"<a href='/runs/{quote(latest_run_id)}'>/runs/{_e(latest_run_id)}</a>"
        )
        next_action = "Review task run evidence"
        target_href = f"/runs/{quote(latest_run_id)}"
        target_label = f"/runs/{latest_run_id}"
        reason = "task run evidence is available for this goal"

    if selected_run is not None and next_action == "Create commit request":
        status = "ready_for_commit_request"
    elif (
        selected_run is not None
        and selected_run.status == "completed"
        and latest_review_status != "reviewed"
    ):
        status = "needs_review"
    elif selected_run is not None:
        status = "worktree_runs_available"
    elif task_runs:
        status = "task_runs_available"
    elif run_lines:
        status = "history_available"
    else:
        status = "empty"

    target = SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>")
    return "".join(
        [
            "<section id='goal-run-command-bar' class='panel goal-run-command-bar' data-goal-run-command-bar='true'><h3>Goal Run Command Bar</h3>",
            "<p class='muted'>Goal-scoped run posture before the detailed task and worktree run list.</p>",
            _kv(
                [
                    ("goal_run_command_goal", goal.id),
                    ("goal_run_command_project", goal.project_id),
                    ("goal_run_command_status", status),
                    ("goal_run_command_items", str(len(run_lines))),
                    ("goal_run_command_task_runs", str(len(task_runs))),
                    ("goal_run_command_worktree_runs", str(len(worktree_runs))),
                    (
                        "goal_run_command_completed_worktree_runs",
                        str(len(completed_worktree_runs)),
                    ),
                    (
                        "goal_run_command_running_worktree_runs",
                        str(len(running_worktree_runs)),
                    ),
                    (
                        "goal_run_command_failed_worktree_runs",
                        str(len(failed_worktree_runs)),
                    ),
                    ("goal_run_command_reviewed_runs", str(len(reviewed_runs))),
                    (
                        "goal_run_command_review_blocked_runs",
                        str(len(review_blocked_runs)),
                    ),
                    (
                        "goal_run_command_verification_failed_runs",
                        str(len(verification_failed_runs)),
                    ),
                    ("goal_run_command_changed_files_count", str(changed_files_count)),
                    ("goal_run_command_outside_allowed_files", str(outside_allowed_files)),
                    ("goal_run_command_latest_run", latest_run_id),
                    ("goal_run_command_latest_status", latest_run_status),
                    ("goal_run_command_latest_surface", latest_run_surface),
                    ("goal_run_command_latest_review_status", latest_review_status),
                    (
                        "goal_run_command_latest_changed_files_count",
                        latest_changed_files_count,
                    ),
                    ("goal_run_command_latest_diff_summary", latest_diff_summary),
                    ("goal_run_command_latest_diff", SafeHtml(str(latest_diff_surface))),
                    ("goal_run_command_next_action", next_action),
                    ("goal_run_command_target_surface", target),
                    ("goal_run_command_reason", reason),
                    ("goal_run_command_source", "goal_runs_and_coder_worktree_runs"),
                    ("goal_run_command_write_on_get", "false"),
                    ("goal_run_command_provider_calls_taken", "0"),
                    ("goal_run_command_network_actions_taken", "0"),
                    ("goal_run_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_run_now: {_e(next_action)}",
                    f"goal_run_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"goal_run_latest: {_e(latest_run_id)} status={_e(latest_run_status)} review={_e(latest_review_status)}",
                    "goal_run_safety: read-only local run posture",
                ]
            ),
            "</section>",
        ]
    )


def _goal_approval_lines(root: Path, state: dict[str, Any]) -> list[str]:
    return (
        [_approval_line(item) for item in state["worktree_approvals"]]
        + [_commit_line(item) for item in state["commit_approvals"]]
        + [_publication_line(root, item) for item in state["publications"]]
    )


def _goal_approval_section(root: Path, state: dict[str, Any]) -> str:
    lines = _goal_approval_lines(root, state)
    return _goal_approval_command_bar(state, lines) + _list_section(
        "Approvals",
        lines,
        anchor_id="goal-approvals",
    )


def _goal_approval_command_bar(
    state: dict[str, Any],
    approval_lines: list[str],
) -> str:
    goal = state["goal"]
    pending_worktree = _count_status(
        state["worktree_approvals"],
        "pending_operator_approval",
    )
    pending_commit = _count_status(
        state["commit_approvals"],
        "pending_operator_approval",
    )
    pending_publication = _count_status(
        state["publications"],
        "pending_operator_approval",
    )
    approved_worktree = _count_status(state["worktree_approvals"], "approved")
    approved_commit = _count_status(state["commit_approvals"], "approved")
    approved_publication = _count_status(state["publications"], "approved")
    committed_commit = _count_status(state["commit_approvals"], "committed")
    publication_ready = _count_status(state["publications"], "ready_for_operator")
    pending_total = pending_worktree + pending_commit + pending_publication
    approved_total = approved_worktree + approved_commit + approved_publication
    downstream_total = committed_commit + publication_ready

    next_action = "Continue Goal workflow"
    target_href = "#goal-next-action"
    target_label = "Next Action"
    reason = "approval gates are not the active local blocker"
    if pending_publication:
        next_action = "Approve publication"
        target_href = "/approvals"
        target_label = "/approvals"
        reason = "publication gate is waiting for an operator decision"
    elif pending_commit:
        next_action = "Approve commit"
        target_href = "/approvals"
        target_label = "/approvals"
        reason = "commit gate is waiting for an operator decision"
    elif pending_worktree:
        next_action = "Approve worktree"
        target_href = "/approvals"
        target_label = "/approvals"
        reason = "worktree gate is waiting for an operator decision"
    elif publication_ready:
        next_action = "Use publication handoff"
        target_href = "#goal-completion-readiness"
        target_label = "Completion Readiness"
        reason = "publication handoff is ready for manual push/PR outside ClankerOS"
    elif approved_publication:
        publication = next(
            (item for item in state["publications"] if item.status == "approved"),
            None,
        )
        next_action = "Create publication handoff"
        target_href = (
            f"/runs/{quote(publication.run_id)}"
            if publication is not None
            else "#goal-next-action"
        )
        target_label = target_href if publication is not None else "Next Action"
        reason = "publication approval is granted and needs a local handoff artifact"
    elif committed_commit:
        commit = next(
            (item for item in state["commit_approvals"] if item.status == "committed"),
            None,
        )
        next_action = "Create publication request"
        target_href = (
            f"/runs/{quote(commit.run_id)}"
            if commit is not None
            else "#goal-next-action"
        )
        target_label = target_href if commit is not None else "Next Action"
        reason = "local worktree commit is recorded and publication can be requested"
    elif approved_commit:
        commit = next(
            (item for item in state["commit_approvals"] if item.status == "approved"),
            None,
        )
        next_action = "Commit approved worktree"
        target_href = (
            f"/runs/{quote(commit.run_id)}"
            if commit is not None
            else "#goal-next-action"
        )
        target_label = target_href if commit is not None else "Next Action"
        reason = "commit approval is granted and awaiting the local commit action"
    elif approved_worktree:
        next_action = "Run approved worktree"
        target_href = "#goal-next-action"
        target_label = "Next Action"
        reason = "worktree approval is granted and execution is the next bounded step"
    elif approval_lines:
        next_action = "Review approval history"
        target_href = "#goal-approvals"
        target_label = "Approvals"
        reason = "approval records exist but no active approval gate is waiting"

    if pending_total:
        status = "waiting_for_operator"
    elif approved_total or downstream_total:
        status = "approved_gate_available"
    elif approval_lines:
        status = "history_available"
    else:
        status = "empty"

    return "".join(
        [
            "<section id='goal-approval-command-bar' class='panel goal-approval-command-bar' data-goal-approval-command-bar='true'><h3>Goal Approval Command Bar</h3>",
            "<p class='muted'>Goal-scoped approval posture before the detailed worktree, commit, and publication approval records.</p>",
            _kv(
                [
                    ("goal_approval_command_goal", goal.id),
                    ("goal_approval_command_project", goal.project_id),
                    ("goal_approval_command_status", status),
                    ("goal_approval_command_items", str(len(approval_lines))),
                    ("goal_approval_command_pending_total", str(pending_total)),
                    ("goal_approval_command_approved_total", str(approved_total)),
                    ("goal_approval_command_pending_worktree", str(pending_worktree)),
                    ("goal_approval_command_pending_commit", str(pending_commit)),
                    ("goal_approval_command_pending_publication", str(pending_publication)),
                    ("goal_approval_command_approved_worktree", str(approved_worktree)),
                    ("goal_approval_command_approved_commit", str(approved_commit)),
                    ("goal_approval_command_approved_publication", str(approved_publication)),
                    ("goal_approval_command_committed_commits", str(committed_commit)),
                    ("goal_approval_command_ready_publications", str(publication_ready)),
                    ("goal_approval_command_next_action", next_action),
                    (
                        "goal_approval_command_target_surface",
                        SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>"),
                    ),
                    ("goal_approval_command_reason", reason),
                    ("goal_approval_command_source", "goal_local_approval_records"),
                    ("goal_approval_command_write_on_get", "false"),
                    ("goal_approval_command_provider_calls_taken", "0"),
                    ("goal_approval_command_network_actions_taken", "0"),
                    ("goal_approval_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_approval_now: {_e(next_action)}",
                    f"goal_approval_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"goal_approval_reason: {_e(reason)}",
                    "goal_approval_safety: read-only local approval posture",
                ]
            ),
            "</section>",
        ]
    )


def _goal_incident_lines(root: Path, state: dict[str, Any]) -> list[str]:
    incidents = state["incidents"]
    open_incidents = [row for row in incidents if row["status"] == "open"]
    resolved_incidents = [row for row in incidents if row["status"] == "resolved"]
    lines = [
        "goal_incident_surface: <a href='/incidents'>/incidents</a>",
        f"goal_incident_open_count: {len(open_incidents)}",
        f"goal_incident_resolved_count: {len(resolved_incidents)}",
        f"goal_incident_total_count: {len(incidents)}",
        "goal_incidents_write_on_get: false",
        "goal_incidents_external_effects_created: false",
    ]
    if not incidents:
        lines.append("goal_incident_status: none")
        return lines
    for incident in incidents[:10]:
        evidence_path = str(incident["evidence_path"] or "none")
        lines.append(
            f"goal_incident: {_e(incident['id'])} status={_e(incident['status'])} "
            f"severity={_e(incident['severity'])} run={_e(incident['run_id'] or 'none')} "
            f"task={_e(incident['task_id'] or 'none')} summary={_e(incident['summary'])}"
        )
        lines.append(
            f"goal_incident_evidence: {_artifact_link(_repo_relative_artifact_path(root, evidence_path))}"
        )
    if len(incidents) > 10:
        lines.append(f"goal_incident_more_count: {len(incidents) - 10}")
    return lines


def _goal_evidence_lines(root: Path, state: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for row in state["runs"]:
        for key in ["activity_path", "summary_path", "events_path"]:
            if row[key]:
                lines.append(f"{_e(row['id'])} {key}: {_artifact_link(_repo_relative_artifact_path(root, row[key]))}")
    for incident in state["incidents"]:
        lines.append(f"incident {incident['id']}: {_artifact_link(str(incident['evidence_path'] or 'none'))}")
    for recommendation in state["recommendations"]:
        lines.append(f"recommendation {recommendation['id']}: {_artifact_link(str(recommendation['evidence_path']))}")
    for run in state["worktree_runs"]:
        lines.append(f"{_e(run.id)} evidence: {_artifact_link(run.evidence_path)}")
    return lines


def _goal_evidence_section(root: Path, state: dict[str, Any]) -> str:
    lines = _goal_evidence_lines(root, state)
    return _goal_evidence_command_bar(root, state, lines) + _list_section(
        "Evidence",
        lines,
        anchor_id="goal-evidence",
    )


def _goal_evidence_command_bar(
    root: Path,
    state: dict[str, Any],
    evidence_lines: list[str],
) -> str:
    goal = state["goal"]
    artifact_records = _goal_artifact_records(root, state)
    artifact_counts = {kind: 0 for kind in ["markdown", "json", "patch", "text"]}
    for record in artifact_records:
        artifact_counts[record["kind"]] += 1

    run_evidence_items = sum(
        1
        for row in state["runs"]
        for key in ["activity_path", "summary_path", "events_path"]
        if row[key]
    )
    worktree_evidence_items = len(state["worktree_runs"])
    incident_evidence_items = len(state["incidents"])
    recommendation_evidence_items = len(state["recommendations"])
    latest_record = artifact_records[-1] if artifact_records else None
    if incident_evidence_items:
        next_action = "Review incident evidence"
        target_href = "#goal-incidents"
        target_label = "Goal Incidents"
        reason = "open or historical incident evidence is attached to this goal"
    elif recommendation_evidence_items:
        next_action = "Review recommendation evidence"
        target_href = "/incidents"
        target_label = "/incidents"
        reason = "task recommendations have local evidence attached"
    elif latest_record is not None:
        next_action = "Open latest Goal artifact"
        target_href = f"/artifacts?path={quote(latest_record['path'])}"
        target_label = latest_record["label"]
        reason = "goal artifacts are available in the bounded artifact viewer"
    elif evidence_lines:
        next_action = "Review evidence list"
        target_href = "#goal-evidence"
        target_label = "Evidence"
        reason = "run evidence records are available"
    else:
        next_action = "Create evidence through the next Goal action"
        target_href = "#goal-next-action"
        target_label = "Next Action"
        reason = "no local evidence records are attached yet"

    status = "available" if evidence_lines or artifact_records else "empty"
    latest_label = latest_record["label"] if latest_record is not None else "none"
    latest_surface = (
        _artifact_link(latest_record["path"])
        if latest_record is not None
        else "none"
    )
    return "".join(
        [
            "<section id='goal-evidence-command-bar' class='panel goal-evidence-command-bar' data-goal-evidence-command-bar='true'><h3>Goal Evidence Command Bar</h3>",
            "<p class='muted'>Goal-scoped evidence posture before the detailed evidence list and typed artifact explorer.</p>",
            _kv(
                [
                    ("goal_evidence_command_goal", goal.id),
                    ("goal_evidence_command_project", goal.project_id),
                    ("goal_evidence_command_status", status),
                    ("goal_evidence_command_items", str(len(evidence_lines))),
                    ("goal_evidence_command_artifact_records", str(len(artifact_records))),
                    ("goal_evidence_command_run_evidence_items", str(run_evidence_items)),
                    ("goal_evidence_command_worktree_evidence_items", str(worktree_evidence_items)),
                    ("goal_evidence_command_incident_evidence_items", str(incident_evidence_items)),
                    ("goal_evidence_command_recommendation_evidence_items", str(recommendation_evidence_items)),
                    ("goal_evidence_command_markdown_artifacts", str(artifact_counts["markdown"])),
                    ("goal_evidence_command_json_artifacts", str(artifact_counts["json"])),
                    ("goal_evidence_command_patch_artifacts", str(artifact_counts["patch"])),
                    ("goal_evidence_command_text_artifacts", str(artifact_counts["text"])),
                    ("goal_evidence_command_latest_artifact", latest_label),
                    ("goal_evidence_command_latest_surface", SafeHtml(str(latest_surface))),
                    ("goal_evidence_command_next_action", next_action),
                    (
                        "goal_evidence_command_target_surface",
                        SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>"),
                    ),
                    ("goal_evidence_command_reason", reason),
                    ("goal_evidence_command_source", "goal_evidence_lines_and_artifact_registry"),
                    ("goal_evidence_command_write_on_get", "false"),
                    ("goal_evidence_command_provider_calls_taken", "0"),
                    ("goal_evidence_command_network_actions_taken", "0"),
                    ("goal_evidence_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_evidence_now: {_e(next_action)}",
                    f"goal_evidence_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"goal_evidence_reason: {_e(reason)}",
                    "goal_evidence_safety: read-only local evidence inventory",
                ]
            ),
            "</section>",
        ]
    )


def _goal_artifact_lines(root: Path, state: dict[str, Any]) -> list[str]:
    return [
        f"{_e(record['label'])}: {_artifact_link(record['path'])}"
        for record in _goal_artifact_records(root, state)
    ]


def _goal_artifact_explorer(root: Path, state: dict[str, Any]) -> str:
    records = _goal_artifact_records(root, state)
    groups = {kind: [] for kind in ["markdown", "json", "patch", "text"]}
    for record in records:
        groups[record["kind"]].append(record)
    sections = [
        "<section id='goal-artifact-explorer'><h2>Goal Artifact Explorer</h2>",
        _kv(
            [
                ("artifact_explorer_raw_filesystem_browsing", "false"),
                ("artifact_viewer_route", "/artifacts?path=<repo-relative-artifact>"),
                ("artifact_render_types", "Markdown, JSON, Patch, Text"),
                ("markdown_artifacts", str(len(groups["markdown"]))),
                ("json_artifacts", str(len(groups["json"]))),
                ("patch_artifacts", str(len(groups["patch"]))),
                ("text_artifacts", str(len(groups["text"]))),
            ]
        ),
    ]
    if not records:
        sections.append(_ul(["artifact_explorer_status: no_supported_goal_artifacts"]))
    for kind, heading in [
        ("markdown", "Markdown"),
        ("json", "JSON"),
        ("patch", "Patch"),
        ("text", "Text"),
    ]:
        items = [
            (
                f"{_e(record['label'])}: {_artifact_link(record['path'])} "
                f"artifact_type={_e(record['kind'])} "
                f"status={_e(record['status'])} "
                f"source={_e(record['source'])}"
            )
            for record in groups[kind]
        ]
        sections.append(f"<h3>{heading}</h3>")
        sections.append(_ul(items or [f"{kind}_artifacts_status: none"]))
    sections.append("</section>")
    return "".join(sections)


def _goal_artifact_records(root: Path, state: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(label: str, path: str | Path | None, *, source: str) -> None:
        relative_path = _repo_relative_artifact_path(root, path)
        if not relative_path or relative_path == "none":
            return
        kind = _goal_artifact_render_kind(relative_path)
        if kind is None:
            return
        try:
            resolve_artifact_path(root, relative_path)
        except ValueError:
            return
        key = (label, relative_path)
        if key in seen:
            return
        seen.add(key)
        records.append(
            {
                "label": label,
                "path": relative_path,
                "kind": kind,
                "status": _artifact_status(root, relative_path),
                "source": source,
            }
        )

    for task in state["tasks"]:
        for artifact in task.artifacts:
            add(f"task {task.id}", artifact, source="task")
    for row in state["runs"]:
        for label, key in [
            ("run summary", "summary_path"),
            ("run activity", "activity_path"),
            ("run events", "events_path"),
        ]:
            add(f"{label} {row['id']}", row[key], source="run")
    for incident in state["incidents"]:
        add(f"incident {incident['id']}", incident["evidence_path"], source="incident")
    for recommendation in state["recommendations"]:
        add(f"recommendation {recommendation['id']}", recommendation["evidence_path"], source="recommendation")
    for delegation in state["delegations"]:
        metadata = load_delegation_result_metadata(delegation)
        add(f"delegation {delegation.id} result", delegation.result_artifact_path, source="delegation")
        for key in [
            "context_pack_json",
            "context_pack_md",
            "implementation_handoff_json",
            "implementation_handoff_md",
        ]:
            if metadata.get(key):
                add(key, str(metadata[key]), source="delegation_metadata")
    for packet in state["prep_packets"]:
        _add_packet_artifacts(add, packet, source="coder_prep")
    for packet in state["worktree_plans"]:
        _add_packet_artifacts(add, packet, source="worktree_plan")
    for run in state["worktree_runs"]:
        evidence_path = Path(run.evidence_path)
        add(f"coder run {run.id} review", Path("runs") / run.source_run_id / "review.md", source="coder_run")
        for label, path in [
            ("run json", evidence_path / "run.json"),
            ("diff", evidence_path / "diff.patch"),
            ("changed files", evidence_path / "changed_files.json"),
            ("bounded file validation", evidence_path / "bounded_file_validation.json"),
            ("git status", evidence_path / "git_status.txt"),
            ("stdout", evidence_path / "stdout.txt"),
            ("stderr", evidence_path / "stderr.txt"),
            ("verification stdout", evidence_path / "verification_stdout.txt"),
            ("verification stderr", evidence_path / "verification_stderr.txt"),
        ]:
            add(f"coder run {run.id} {label}", path, source="coder_run")
    for approval in state["commit_approvals"]:
        for label, path in [
            ("commit_request", approval.request_artifact_path),
            ("commit_decision", approval.decision_artifact_path),
            ("commit_artifact", approval.commit_artifact_path),
        ]:
            add(label, path, source="commit")
    for publication in state["publications"]:
        for label, path in [
            ("publication_request", publication.request_artifact_path),
            ("publication_decision", publication.decision_artifact_path),
            ("publication_handoff", publication.handoff_artifact_path),
        ]:
            add(label, path, source="publication")
    return records


def _goal_latest_artifact_path(root: Path, state: dict[str, Any]) -> str:
    records = _goal_artifact_records(root, state)
    existing = [
        record
        for record in records
        if (root / record["path"]).exists()
    ]
    if not existing:
        note_path = _goal_operator_notes_path(state["goal"])
        if (root / note_path).exists():
            return note_path.as_posix()
        return ""
    latest = max(
        existing,
        key=lambda record: (root / record["path"]).stat().st_mtime,
    )
    return latest["path"]


def _add_packet_artifacts(
    add: Any,
    packet: dict[str, Any],
    *,
    source: str,
) -> None:
    kind = str(packet.get("kind", source))
    add(kind, packet.get("_path") or packet.get("artifacts", {}).get("json"), source=source)
    artifacts = packet.get("artifacts") if isinstance(packet.get("artifacts"), dict) else {}
    for label, path in artifacts.items():
        add(f"{kind}_{label}", path, source=source)


def _goal_artifact_render_kind(path: str) -> str | None:
    suffix = Path(path).suffix.lower()
    if suffix == ".md":
        return "markdown"
    if suffix == ".json":
        return "json"
    if suffix in {".patch", ".diff"}:
        return "patch"
    if suffix in {".txt", ".log"}:
        return "text"
    return None


def _goal_memory_lines(root: Path, state: dict[str, Any]) -> list[str]:
    storage = _storage(root)
    goal = state["goal"]
    project_memory = Path("projects") / goal.project_id / "knowledge.md"
    global_memory = Path("knowledge.md")
    operator_notes = Path(".clanker") / "projects" / goal.project_id / "goals" / goal.id / "operator-notes.md"
    project_entries = storage.list_memory_entries(project_id=goal.project_id, limit=100)
    global_entries = [
        entry for entry in storage.list_memory_entries(limit=100) if entry.scope == "global"
    ]
    generated_entries = [
        entry for entry in project_entries if entry.source_type != "operator"
    ]
    active_entries = [entry for entry in project_entries if entry.status == "active"]
    proposed_entries = [entry for entry in project_entries if entry.status == "proposed"]
    future_work = [row for row in state["recommendations"] if row["status"] == "open"]
    latest_generated = generated_entries[0] if generated_entries else None
    latest_project_entry = project_entries[0] if project_entries else None
    operator_note_status = "available" if (root / operator_notes).exists() else "not_started"
    return [
        "memory_surface: <a href='/memory'>/memory</a>",
        f"goal_memory_project_id: {_e(goal.project_id)}",
        f"project_memory: {_artifact_link(project_memory.as_posix()) if (root / project_memory).exists() else 'missing'}",
        f"global_memory: {_artifact_link(global_memory.as_posix()) if (root / global_memory).exists() else 'missing'}",
        f"operator_notes: {_artifact_link(operator_notes.as_posix()) if operator_note_status == 'available' else 'not_started'}",
        f"operator_notes_status: {operator_note_status}",
        f"goal_memory_project_entries: {len(project_entries)}",
        f"goal_memory_active_entries: {len(active_entries)}",
        f"goal_memory_proposed_entries: {len(proposed_entries)}",
        f"goal_memory_global_entries: {len(global_entries)}",
        f"goal_generated_memory_count: {len(generated_entries)}",
        f"goal_future_work_count: {len(future_work)}",
        f"latest_project_memory: {_goal_memory_entry_summary(latest_project_entry)}",
        f"latest_generated_memory: {_goal_memory_entry_summary(latest_generated)}",
        "pin_memory_action: available_on_memory_page",
        "pin_memory_from_goal_page=false",
        "goal_memory_external_effects_created=false",
    ]


def _goal_memory_entry_summary(entry: Any | None) -> str:
    if entry is None:
        return "none"
    return (
        f"{_e(entry.id)} status={_e(entry.status)} "
        f"scope={_e(entry.scope)} key={_e(entry.key)} "
        f"artifact={_artifact_link(entry.artifact_path)}"
    )


def _goal_skill_lines(root: Path, state: dict[str, Any]) -> list[str]:
    storage = _storage(root)
    goal = state["goal"]
    usage = _skill_usage(storage)
    skills = storage.list_skills(limit=200)
    skills_by_name: dict[str, list[Any]] = {}
    for skill in skills:
        skills_by_name.setdefault(skill.name, []).append(skill)
    profile_counts: dict[str, int] = {}
    for delegation in state["delegations"]:
        profile_counts[delegation.assigned_profile] = profile_counts.get(delegation.assigned_profile, 0) + 1
    lines = [
        "skills_surface: <a href='/skills'>/skills</a>",
        "goal_skill_usage_source: tasks.skill_tags",
    ]
    for tag in state["skill_tags"]:
        data = usage.get(tag, {"count": 0, "projects": set()})
        projects = ", ".join(sorted(data["projects"])) if data["projects"] else goal.project_id
        matching = [
            skill
            for skill in skills_by_name.get(tag, [])
            if skill.project_id in {None, "", goal.project_id}
        ]
        if matching:
            skill_links = ", ".join(
                f"{_e(skill.id)} status={_e(skill.status)} path={_artifact_link(_repo_relative_artifact_path(root, skill.path))}"
                for skill in matching[:3]
            )
        else:
            skill_links = "none"
        lines.append(
            f"task_skill: {_e(tag)} usage_count={data['count']} projects_using={_e(projects)} "
            f"matching_skill_records={len(matching)} generated_or_available={skill_links}"
        )
    lines.extend(f"profile_used: {profile} count={count}" for profile, count in sorted(profile_counts.items()))
    if not state["skill_tags"] and not profile_counts:
        lines.append("none_recorded_yet")
    lines.append("skill_execution_from_goal_page=false")
    return lines


def _goal_git_status(root: Path, state: dict[str, Any]) -> str:
    goal = state["goal"]
    project = _storage(root).get_registered_project(goal.project_id)
    project_root = Path(project.root_path) if project else root
    repo = _repo_state(project_root)
    tracked_files = repo["dirty_tracked_files"]
    untracked_files = repo["untracked_files"]
    latest_git_status = _goal_latest_git_status_artifact(root, state)
    posture, next_action, next_target = _goal_git_command_posture(
        goal,
        repo,
        latest_git_status,
    )
    latest_git_status_link = (
        SafeHtml(_artifact_link(latest_git_status)) if latest_git_status else "none"
    )
    return "".join(
        [
            "<section id='goal-git-status'><h2>Git Status</h2>",
            "<section class='panel goal-git-command-bar' data-goal-git-command-bar='true'><h3>Goal Git Command Bar</h3>",
            _kv(
                [
                    ("goal_git_command_project", goal.project_id),
                    ("goal_git_command_root", str(project_root)),
                    ("goal_git_command_branch", repo["branch"]),
                    ("goal_git_command_commit", repo["commit"]),
                    ("goal_git_command_posture", posture),
                    ("goal_git_command_tracked_changes", str(len(tracked_files))),
                    ("goal_git_command_untracked_files", str(len(untracked_files))),
                    ("goal_git_command_latest_git_status_artifact", latest_git_status_link),
                    ("goal_git_command_next_action", next_action),
                    ("goal_git_command_target_surface", SafeHtml(next_target)),
                    ("goal_git_command_source", "local_git_status_no_fetch"),
                    ("goal_git_command_write_on_get", "false"),
                    ("goal_git_command_github_fetch", "none"),
                    ("goal_git_command_network_actions_taken", "0"),
                    ("goal_git_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_git_command_now: {_e(next_action)}",
                    f"goal_git_command_click: {next_target}",
                    "goal_git_command_safety: local git readback only",
                ]
            ),
            "</section>",
            "<h3>Repository Snapshot</h3>",
            _kv(
                [
                    ("project", goal.project_id),
                    ("branch", repo["branch"]),
                    ("commit", repo["commit"]),
                    ("dirty_tracked_files", str(len(tracked_files))),
                    ("dirty_tracked_file_sample", _goal_git_file_sample(tracked_files)),
                    ("untracked_file_count", str(len(untracked_files))),
                    ("untracked_files", _goal_git_file_sample(untracked_files)),
                    ("ahead_of_origin_main", str(repo["ahead_of_origin_main"]).lower()),
                ]
            ),
            "</section>",
        ]
    )


def _goal_latest_git_status_artifact(root: Path, state: dict[str, Any]) -> str:
    for record in reversed(_goal_artifact_records(root, state)):
        if record["label"].endswith(" git status") and record["status"] == "available":
            return record["path"]
    return ""


def _goal_git_command_posture(
    goal: Any,
    repo: dict[str, Any],
    latest_git_status: str,
) -> tuple[str, str, str]:
    if repo["branch"] == "unknown" and repo["commit"] == "unknown":
        return (
            "repo_unknown",
            "Inspect registered project",
            f"<a href='/projects/{quote(goal.project_id)}'>/projects/{_e(goal.project_id)}</a>",
        )
    if repo["dirty_tracked_files"]:
        target = (
            _artifact_link(latest_git_status)
            if latest_git_status
            else "<a href='#goal-artifact-explorer'>Goal Artifact Explorer</a>"
        )
        return ("tracked_changes_present", "Review tracked changes", target)
    if repo["untracked_files"]:
        target = (
            _artifact_link(latest_git_status)
            if latest_git_status
            else "<a href='#goal-artifact-explorer'>Goal Artifact Explorer</a>"
        )
        return ("untracked_files_present", "Review untracked files", target)
    return (
        "clean",
        "Check verification evidence",
        "<a href='#goal-verification-evidence'>Goal Verification Evidence</a>",
    )


def _goal_git_file_sample(files: list[str], limit: int = 8) -> str:
    if not files:
        return "none"
    sample = ", ".join(files[:limit])
    if len(files) > limit:
        sample += f" (+{len(files) - limit} more)"
    return sample


def _goal_verification_evidence(root: Path, state: dict[str, Any]) -> str:
    goal = state["goal"]
    project = _storage(root).get_registered_project(goal.project_id)
    project_root = Path(project.root_path) if project else root
    repo = _repo_state(project_root)
    full_commit = _git(project_root, ["rev-parse", "HEAD"]) or repo["commit"]
    latest_record = _latest_ci_evidence_record(root, project_id=goal.project_id)
    lines: list[str] = [
        f"goal_ci_project: {_e(goal.project_id)}",
        f"goal_ci_current_branch: {_e(repo['branch'])}",
        f"goal_ci_current_commit: {_e(full_commit)}",
        "verification_surface: <a href='/verification'>/verification</a>",
        "ci_evidence_surface: <a href='/ci-evidence'>/ci-evidence</a>",
        "goal_ci_github_status_fetch: none",
        "goal_ci_app_network_actions_taken: 0",
        "goal_ci_external_mutations_taken: 0",
    ]
    if latest_record is None:
        lines.extend(
            [
                "goal_ci_latest_status: missing",
                "goal_ci_latest_source: none",
                "goal_ci_matches_current_checkout: false",
                "goal_ci_next_action: wait_for_github_actions_success_then_record_project_ci_evidence",
                "goal_ci_proof_boundary: no project-scoped local CI proof record yet",
            ]
        )
        return (
            _goal_verification_command_bar(
                root=root,
                goal=goal,
                repo=repo,
                full_commit=full_commit,
                source_kind="none",
                record=None,
                branch_matches=False,
                commit_matches=False,
                matches_current=False,
            )
            + _list_section(
                "Goal Verification Evidence",
                lines,
                "/verification",
                anchor_id="goal-verification-evidence",
            )
            + _goal_ci_json_recording_form(goal.id, goal.project_id, repo, full_commit)
        )

    source_kind, record = latest_record
    branch_matches = record.branch_name == repo["branch"]
    commit_matches = _commit_refs_match(record.commit_sha, full_commit, repo["commit"])
    matches_current = branch_matches and commit_matches
    result = record.result_json if isinstance(record.result_json, dict) else {}
    lines.extend(
        [
            f"goal_ci_latest_status: {_e(record.status)}",
            f"goal_ci_latest_source: {_e(source_kind)}",
            f"goal_ci_latest_provider: {_e(record.provider)}",
            f"goal_ci_latest_branch: {_e(record.branch_name)}",
            f"goal_ci_latest_commit: {_e(record.commit_sha)}",
            f"goal_ci_latest_external_run_id: {_e(record.external_run_id)}",
            f"goal_ci_latest_url: <a href='{_e(record.external_url)}'>{_e(record.external_url)}</a>",
            f"goal_ci_latest_status_source: {_e(result.get('status_source', 'unknown'))}",
            f"goal_ci_latest_evidence_scope: {_e(result.get('evidence_scope', 'unknown'))}",
            f"goal_ci_latest_evidence_path: {_artifact_link(_repo_relative_artifact_path(root, record.evidence_path))}",
            f"goal_ci_branch_matches_current: {str(branch_matches).lower()}",
            f"goal_ci_commit_matches_current: {str(commit_matches).lower()}",
            f"goal_ci_matches_current_checkout: {str(matches_current).lower()}",
            "goal_ci_record_source: operator_supplied",
            f"goal_ci_network_actions_taken: {_e(result.get('network_actions_taken', 'unknown'))}",
            f"goal_ci_external_mutations_taken: {_e(result.get('external_mutations_taken', 'unknown'))}",
            "goal_ci_proof_boundary: operator_supplied_project_record_only",
        ]
    )
    return (
        _goal_verification_command_bar(
            root=root,
            goal=goal,
            repo=repo,
            full_commit=full_commit,
            source_kind=source_kind,
            record=record,
            branch_matches=branch_matches,
            commit_matches=commit_matches,
            matches_current=matches_current,
        )
        + _list_section(
            "Goal Verification Evidence",
            lines,
            "/verification",
            anchor_id="goal-verification-evidence",
        )
        + _goal_ci_json_recording_form(goal.id, goal.project_id, repo, full_commit)
    )


def _goal_verification_command_bar(
    *,
    root: Path,
    goal: Any,
    repo: dict[str, Any],
    full_commit: str,
    source_kind: str,
    record: Any | None,
    branch_matches: bool,
    commit_matches: bool,
    matches_current: bool,
) -> str:
    result_json = getattr(record, "result_json", {}) if record is not None else {}
    result = result_json if isinstance(result_json, dict) else {}
    evidence_scope = str(result.get("evidence_scope", "none"))
    status_source = str(result.get("status_source", "none"))
    latest_status = str(record.status) if record is not None else "missing"
    latest_run_id = str(record.external_run_id) if record is not None else "none"
    latest_url = str(record.external_url) if record is not None else ""
    latest_commit = str(record.commit_sha) if record is not None else "none"
    evidence_path = (
        _artifact_link(_repo_relative_artifact_path(root, record.evidence_path))
        if record is not None
        else "none"
    )
    if record is None:
        proof_status = "missing"
        next_action = "Record Goal CI proof"
        reason = "no project-scoped local CI proof record yet"
        target_href = "#record-goal-ci-proof"
        target_label = "Record Goal CI Proof From GitHub JSON"
    elif not matches_current:
        proof_status = "stale"
        next_action = "Record current Goal CI proof"
        reason = "latest local proof does not match the current branch and commit"
        target_href = "#record-goal-ci-proof"
        target_label = "Record Goal CI Proof From GitHub JSON"
    elif evidence_scope == "job":
        proof_status = "early_job_proof"
        next_action = "Wait for full-suite proof or record full workflow success"
        reason = "job-scoped evidence is useful but not full-suite proof"
        target_href = "/verification"
        target_label = "/verification"
    elif latest_status == "success":
        proof_status = "current_success"
        next_action = "Review recorded proof"
        reason = "latest operator-supplied proof matches the current checkout"
        target_href = "/ci-evidence"
        target_label = "/ci-evidence"
    else:
        proof_status = "needs_attention"
        next_action = "Inspect recorded CI evidence"
        reason = "latest operator-supplied proof is not a success record"
        target_href = "/ci-evidence"
        target_label = "/ci-evidence"

    return "".join(
        [
            "<section id='goal-verification-command-bar' class='panel goal-verification-command-bar' data-goal-verification-command-bar='true'><h3>Goal Verification Command Bar</h3>",
            "<p class='muted'>Goal-scoped proof posture before the detailed evidence and recording form.</p>",
            _kv(
                [
                    ("goal_verification_command_goal", goal.id),
                    ("goal_verification_command_project", goal.project_id),
                    ("goal_verification_command_status", proof_status),
                    ("goal_verification_command_latest_status", latest_status),
                    ("goal_verification_command_latest_source", source_kind),
                    ("goal_verification_command_latest_status_source", status_source),
                    ("goal_verification_command_latest_evidence_scope", evidence_scope),
                    ("goal_verification_command_branch", repo["branch"]),
                    ("goal_verification_command_current_commit", full_commit),
                    ("goal_verification_command_latest_commit", latest_commit),
                    ("goal_verification_command_branch_matches_current", str(branch_matches).lower()),
                    ("goal_verification_command_commit_matches_current", str(commit_matches).lower()),
                    ("goal_verification_command_matches_current_checkout", str(matches_current).lower()),
                    ("goal_verification_command_latest_run_id", latest_run_id),
                    (
                        "goal_verification_command_latest_url",
                        SafeHtml(
                            f"<a href='{_e(latest_url)}'>{_e(latest_url)}</a>"
                            if latest_url
                            else "none"
                        ),
                    ),
                    (
                        "goal_verification_command_latest_evidence",
                        SafeHtml(evidence_path),
                    ),
                    ("goal_verification_command_next_action", next_action),
                    (
                        "goal_verification_command_target_surface",
                        SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>"),
                    ),
                    ("goal_verification_command_reason", reason),
                    ("goal_verification_command_source", "project_scoped_ci_evidence_records"),
                    ("goal_verification_command_write_on_get", "false"),
                    ("goal_verification_command_github_status_fetch", "none"),
                    ("goal_verification_command_provider_calls_taken", "0"),
                    ("goal_verification_command_network_actions_taken", "0"),
                    ("goal_verification_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"goal_verification_now: {_e(next_action)}",
                    f"goal_verification_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"goal_verification_reason: {_e(reason)}",
                    "goal_verification_safety: local operator-supplied proof only",
                ]
            ),
            "</section>",
        ]
    )


def _goal_ci_json_recording_form(
    goal_id: str,
    project_id: str,
    repo: dict[str, Any],
    full_commit: str,
) -> str:
    branch = repo["branch"] if repo["branch"] != "unknown" else "main"
    commit = full_commit if full_commit != "unknown" else repo["commit"]
    return "".join(
        [
            "<section id='record-goal-ci-proof'><h2>Record Goal CI Proof From GitHub JSON</h2>",
            "<p class='muted'>Paste <code>gh run view</code> JSON after GitHub Actions completes. This validates the supplied JSON and writes a local project-scoped CI evidence record; it does not contact GitHub.</p>",
            "<form method='post' action='/actions/ci-snapshot-evidence-from-gh-json'>",
            f"<input type='hidden' name='project' value='{_e(project_id)}'>",
            f"<input type='hidden' name='branch' value='{_e(branch)}'>",
            f"<input type='hidden' name='commit' value='{_e(commit)}'>",
            "<input type='hidden' name='provider' value='github-actions'>",
            f"<input type='hidden' name='return_to' value='/goals/{_e(quote(goal_id))}'>",
            "<label>external_run_id <input name='external_run_id' value='' placeholder='optional if JSON has databaseId or URL'></label>",
            "<label>url <input name='url' value='' placeholder='optional if JSON has url'></label>",
            "<label>job_name <input name='job_name' value='' placeholder='Fast smoke verification'></label>",
            "<label>recorded_by <input name='recorded_by' value='operator'></label>",
            "<label>note <input name='note' value='Validated from Goal page pasted GitHub Actions JSON.'></label>",
            "<label>status_json <textarea name='status_json' rows='8' spellcheck='false'></textarea></label>",
            "<button type='submit'>ci-snapshot-evidence-from-gh-json</button>",
            "</form>",
            _kv(
                [
                    ("goal_ci_record_form_available", "true"),
                    ("goal_ci_record_action", "ci-snapshot-evidence-from-gh-json"),
                    ("goal_ci_record_project", project_id),
                    ("goal_ci_record_branch", branch),
                    ("goal_ci_record_commit", commit),
                    ("goal_ci_record_return_to_goal", "true"),
                    ("confirmation_required", "true"),
                    ("github_status_fetch", "none"),
                    ("network_actions_taken_by_app", "0"),
                    ("external_mutations_taken", "0"),
                    ("external_run_id_inference", "databaseId_or_actions_run_url"),
                    ("external_url_inference", "status_json_url"),
                ]
            ),
            "</section>",
        ]
    )


def _commit_refs_match(record_commit: str, full_commit: str, short_commit: str) -> bool:
    record = record_commit.strip()
    if not record or record == "unknown":
        return False
    for candidate in {full_commit.strip(), short_commit.strip()}:
        if not candidate or candidate == "unknown":
            continue
        if record == candidate or candidate.startswith(record) or record.startswith(candidate):
            return True
    return False


def _goal_operator_note_lines(root: Path, state: dict[str, Any]) -> list[str]:
    goal = state["goal"]
    note_path = _goal_operator_notes_path(goal)
    if (root / note_path).exists():
        return [
            f"operator_notes: {_artifact_link(note_path.as_posix())}",
            "operator_notes_status: available",
            "note_append_form_available: true",
        ]
    return [
        "operator_notes: none",
        f"planned_notes_path: {note_path.as_posix()}",
        "note_append_form_available: true",
    ]


def _goal_operator_notes_section(root: Path, state: dict[str, Any]) -> str:
    goal = state["goal"]
    return "".join(
        [
            "<section id='goal-operator-notes'><h2>Operator Notes</h2>",
            "<p class='muted'>Append a goal-scoped local note for tomorrow's resume context. This writes only the operator-notes artifact.</p>",
            _ul(_goal_operator_note_lines(root, state)),
            _input_form(
                "save-goal-note",
                {"goal_id": goal.id, "author": "operator"},
                {"note": "What should future me know about this goal?"},
            ),
            "</section>",
        ]
    )


def _goal_operator_notes_path(goal: Any) -> Path:
    return Path(".clanker") / "projects" / goal.project_id / "goals" / goal.id / "operator-notes.md"


def _goal_file_path(project_id: str, goal_id: str, filename: str) -> Path:
    return Path(".clanker") / "projects" / project_id / "goals" / goal_id / filename


def _goal_remaining_work_lines(
    root: Path,
    state: dict[str, Any],
    next_action: GoalNextAction,
) -> list[str]:
    tasks = [task for task in state["tasks"] if task.status != "completed"]
    open_incidents = [row for row in state["incidents"] if row["status"] == "open"]
    open_recommendations = [
        row for row in state["recommendations"] if row["status"] == "open"
    ]
    gate_lines = _goal_remaining_work_gate_lines(root, state, next_action)
    lines = [
        "remaining_work_source: goal_state_workflow_gates",
        f"remaining_work_next_action: {_e(next_action.action)}",
        f"remaining_work_next_surface: {_e(next_action.href)}",
        f"remaining_work_open_tasks: {len(tasks)}",
        f"remaining_work_open_incidents: {len(open_incidents)}",
        f"remaining_work_open_recommendations: {len(open_recommendations)}",
        "remaining_work_external_effects_created: false",
    ]
    lines.extend(
        f"remaining_work_open_task: {_e(task.id)} status={_e(task.status)} type={_e(task.task_type)}"
        for task in tasks[:10]
    )
    lines.extend(gate_lines)
    if not tasks and next_action.action == "Manual publish outside ClankerOS":
        lines.append("manual publication remains outside ClankerOS")
    if not tasks and not any("status=pending" in line for line in gate_lines):
        lines.append("no open task rows; inspect timeline and evidence before marking complete")
    return lines


def _goal_remaining_work_gate_lines(
    root: Path,
    state: dict[str, Any],
    next_action: GoalNextAction,
) -> list[str]:
    delegations = state["delegations"]
    has_delegation = bool(delegations)
    has_context_pack = any(
        _delegation_has_context_pack(
            root,
            delegation,
            load_delegation_result_metadata(delegation),
        )
        for delegation in delegations
    )
    completed_delegation = any(
        delegation.status == "completed" for delegation in delegations
    )
    has_handoff = any(
        _goal_delegation_has_handoff(state, delegation) for delegation in delegations
    )
    has_prep = bool(state["prep_packets"])
    has_worktree_plan = bool(state["worktree_plans"])
    worktree_pending = _count_status(
        state["worktree_approvals"],
        "pending_operator_approval",
    )
    worktree_approved = _count_status(state["worktree_approvals"], "approved")
    has_completed_run = any(run.status == "completed" for run in state["worktree_runs"])
    has_running_run = any(run.status == "running" for run in state["worktree_runs"])
    has_review = any(
        run.status == "completed"
        and _run_review_gate_state(root, run).get("commit_request_form_available")
        for run in state["worktree_runs"]
    )
    commit_pending = _count_status(state["commit_approvals"], "pending_operator_approval")
    commit_approved = _count_status(state["commit_approvals"], "approved")
    has_local_commit = _count_status(state["commit_approvals"], "committed") > 0
    publication_pending = _count_status(
        state["publications"],
        "pending_operator_approval",
    )
    publication_approved = _count_status(state["publications"], "approved")
    publication_ready = _count_status(state["publications"], "ready_for_operator")
    has_publication_request = bool(state["publications"])

    gates: list[tuple[str, str, str, str]] = []

    def add(name: str, status: str, *, next_step: str = "", detail: str = "") -> None:
        gates.append((name, status, next_step, detail))

    def pending_if_ready(done: bool, ready: bool, next_step: str) -> str:
        if done:
            return "done"
        if ready or next_action.action == next_step:
            return "pending"
        return "waiting"

    add(
        "scout_delegation",
        pending_if_ready(
            has_delegation,
            bool(state["tasks"]),
            "Create scout delegation",
        ),
        next_step="Create scout delegation",
        detail=f"delegations={len(delegations)}",
    )
    add(
        "context_pack",
        pending_if_ready(has_context_pack, has_delegation, "Generate context pack"),
        next_step="Generate context pack",
    )
    add(
        "implementation_handoff",
        pending_if_ready(
            has_handoff,
            has_context_pack or completed_delegation,
            "Run delegation",
        ),
        next_step="Run delegation",
        detail=(
            "completed_delegations="
            f"{sum(1 for delegation in delegations if delegation.status == 'completed')}"
        ),
    )
    add(
        "coder_prep",
        pending_if_ready(has_prep, has_handoff, "Run coder prep"),
        next_step="Run coder prep",
    )
    add(
        "worktree_plan",
        pending_if_ready(has_worktree_plan, has_prep, "Create worktree plan"),
        next_step="Create worktree plan",
    )
    add(
        "worktree_approval",
        pending_if_ready(
            worktree_approved > 0 or has_completed_run or has_running_run,
            has_worktree_plan,
            "Request worktree approval",
        ),
        next_step="Request worktree approval",
        detail=f"pending={worktree_pending} approved={worktree_approved}",
    )
    add(
        "worktree_run",
        pending_if_ready(
            has_completed_run,
            worktree_approved > 0 or has_running_run,
            "Run approved worktree",
        ),
        next_step="Run approved worktree",
        detail=(
            f"running={sum(1 for run in state['worktree_runs'] if run.status == 'running')} "
            f"completed={sum(1 for run in state['worktree_runs'] if run.status == 'completed')}"
        ),
    )
    add(
        "review",
        pending_if_ready(has_review, has_completed_run, "Open review"),
        next_step="Open review",
    )
    add(
        "commit_request",
        pending_if_ready(
            bool(state["commit_approvals"]),
            has_review,
            "Create commit request",
        ),
        next_step="Create commit request",
        detail=f"requests={len(state['commit_approvals'])}",
    )
    add(
        "commit_approval",
        pending_if_ready(
            commit_approved > 0 or has_local_commit,
            commit_pending > 0,
            "Approve commit",
        ),
        next_step="Approve commit",
        detail=f"pending={commit_pending} approved={commit_approved}",
    )
    add(
        "local_commit",
        pending_if_ready(has_local_commit, commit_approved > 0, "Commit approved worktree"),
        next_step="Commit approved worktree",
    )
    add(
        "publication_request",
        pending_if_ready(
            has_publication_request,
            has_local_commit,
            "Create publication request",
        ),
        next_step="Create publication request",
        detail=f"requests={len(state['publications'])}",
    )
    add(
        "publication_approval",
        pending_if_ready(
            publication_approved > 0 or publication_ready > 0,
            publication_pending > 0,
            "Approve publication",
        ),
        next_step="Approve publication",
        detail=f"pending={publication_pending} approved={publication_approved}",
    )
    add(
        "publication_handoff",
        pending_if_ready(publication_ready > 0, publication_approved > 0, "Create publication handoff"),
        next_step="Create publication handoff",
        detail=f"ready_for_operator={publication_ready}",
    )
    add(
        "manual_publish",
        (
            "done"
            if state["goal"].status == "completed"
            else ("pending" if publication_ready > 0 else "waiting")
        ),
        next_step="Manual publish outside ClankerOS",
        detail="outside_clankeros=true",
    )

    counts: dict[str, int] = {}
    for _, status, _, _ in gates:
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "remaining_work_gate_counts: "
        + " ".join(
            f"{status}={counts.get(status, 0)}"
            for status in ["done", "pending", "waiting"]
        )
    ]
    for name, status, next_step, detail in gates:
        parts = [f"remaining_work_gate: {name}", f"status={status}"]
        if status == "pending" and next_step:
            parts.append(f"next={_e(next_step)}")
        if detail:
            parts.append(f"detail={_e(detail)}")
        lines.append(" ".join(parts))
    return lines


def _highest_risk(risks: list[str]) -> str:
    order = {"low": 1, "medium": 2, "high": 3}
    if not risks:
        return "unknown"
    return max(risks, key=lambda value: order.get(value, 0))


def _risk_counts(tasks: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in tasks:
        risk = str(getattr(task, "risk_level", "") or "unknown")
        counts[risk] = counts.get(risk, 0) + 1
    return counts


def _risk_counts_label(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    order = ["unknown", "high", "medium", "low"]
    labels = [
        f"{risk}={counts[risk]}"
        for risk in order
        if risk in counts
    ]
    labels.extend(
        f"{risk}={count}"
        for risk, count in sorted(counts.items())
        if risk not in order
    )
    return ",".join(labels)


def _criteria_items(text: str) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        items.append(stripped)
    return items


def _task_completion_items(tasks: list[Any]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for task in tasks:
        verification_plan = getattr(task, "verification_plan", {}) or {}
        acceptance = str(
            verification_plan.get("acceptance_criteria")
            or verification_plan.get("expected")
            or task.description
        ).strip()
        if not acceptance:
            continue
        items.append(
            {
                "task_id": task.id,
                "status": task.status,
                "acceptance": acceptance,
            }
        )
    return items


def _goal_delegation_has_handoff(state: dict[str, Any], delegation: Any) -> bool:
    metadata = load_delegation_result_metadata(delegation)
    return bool(metadata.get("implementation_handoff_md") or metadata.get("implementation_handoff_json"))


def _workflow(
    root: Path,
    *,
    delegation_id: str | None = None,
    run_id: str | None = None,
) -> str:
    selected_statuses = _workflow_step_statuses(
        root,
        delegation_id=delegation_id,
        run_id=run_id,
    )
    return "".join(
        [
            "<section><h1>Modern Operator Workflow</h1>",
            _non_claim_banner(),
            _selected_workflow_state(root, delegation_id=delegation_id, run_id=run_id),
            _selected_workflow_continuation(
                root,
                delegation_id=delegation_id,
                run_id=run_id,
            ),
            _workflow_list(compact=False, selected_statuses=selected_statuses),
            "</section>",
        ]
    )


def _actions_page(root: Path) -> str:
    return "".join(
        [
            "<section><h1>Safe Action Catalog</h1>",
            "<p class='muted'>Read-only map of local app actions, where their forms appear, what they require, and what local artifact or decision they produce.</p>",
            _non_claim_banner(),
            "</section>",
            _list_section(
                "Navigation Actions",
                [
                    "<a href='/'>view dashboard</a>: read current local repository/app state",
                    "<a href='/goals'>view goals</a>: inspect goal-first daily operator cockpit",
                    "<a href='/projects'>view projects</a>: inspect registered project state",
                    "<a href='/delegation-runs'>view delegation runs</a>: inspect scout execution evidence",
                    "<a href='/inbox'>view inbox</a>: inspect operator queue",
                    "<a href='/approvals'>view approvals</a>: inspect pending local decisions",
                    "<a href='/incidents'>view incidents</a>: inspect local incident evidence",
                    "<a href='/health'>view health</a>: inspect local status and write status artifact",
                ],
            ),
            "<section><h2>Dashboard Action</h2>",
            "<p class='muted'>This confirmed action rewrites only the local app status artifact from current state.</p>",
            "<form method='post' action='/actions/refresh-dashboard-state'>"
            "<input type='hidden' name='requested_by' value='operator'>"
            "<button type='submit'>refresh-dashboard-state</button>"
            "</form>",
            "</section>",
            _current_demo_action_surfaces(root),
            _list_section(
                "Local Artifact And Approval Actions",
                [_action_catalog_line(item) for item in ACTION_CATALOG],
            ),
            _list_section(
                "Execution Boundary",
                [
                    "run-coder-worktree: confirmed goal action only after approved worktree request and safe local command validation; not a general arbitrary-command surface",
                    "manual_operator_push_pr_outside_clankeros: outside ClankerOS; app displays suggested commands only after publication handoff",
                ],
            ),
        ]
    )


def _current_demo_action_surfaces(root: Path) -> str:
    storage = _storage(root)
    project = storage.get_registered_project("local-app-demo")
    if project is None:
        return _list_section(
            "Current Demo Action Surfaces",
            [
                "demo_fixture_status: missing",
                "next_demo_action: run_demo_app_scenario",
                "demo_command: python3 -m agent_os.cli demo-app-scenario",
                "external_effects_created: false",
                "network_actions_taken_by_app: 0",
            ],
        )

    delegations = [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if _task_project(storage, delegation.parent_task_id) == project.name
    ]
    selected_delegation = delegations[0] if delegations else None
    selected_run = None
    if selected_delegation is not None:
        runs = list_coder_worktree_runs(
            root,
            delegation_id=selected_delegation.id,
            limit=20,
        )
        selected_run = next((run for run in runs if run.status == "completed"), None)
        if selected_run is None and runs:
            selected_run = runs[0]

    next_action = "select_demo_delegation"
    workflow_surface = "<a href='/workflow'>/workflow</a>"
    delegation_surface = "none"
    run_surface = "none"
    action_form_surface = "<a href='/demo'>/demo</a>"
    if selected_delegation is not None:
        delegation_surface = (
            f"<a href='/delegations/{quote(selected_delegation.id)}'>"
            f"/delegations/{_e(selected_delegation.id)}</a>"
        )
        workflow_surface = (
            f"<a href='/workflow?delegation_id={quote(selected_delegation.id)}'>"
            f"/workflow?delegation_id={_e(selected_delegation.id)}</a>"
        )
        action_form_surface = delegation_surface
        next_action = "review_delegation_state"
    if selected_run is not None:
        progress = _demo_progress_state(root, selected_run.id)
        next_action = progress["next_step"]
        workflow_surface = (
            f"<a href='/workflow?run_id={quote(selected_run.id)}'>"
            f"/workflow?run_id={_e(selected_run.id)}</a>"
        )
        run_surface = (
            f"<a href='/runs/{quote(selected_run.id)}'>"
            f"/runs/{_e(selected_run.id)}</a>"
        )
        action_form_surface = run_surface
        if next_action in {
            "approve_or_reject_commit_request",
            "approve_or_reject_publication_request",
        }:
            action_form_surface = "<a href='/approvals'>/approvals</a>"

    return _list_section(
        "Current Demo Action Surfaces",
        [
            "demo_fixture_status: available",
            f"project_surface: <a href='/projects/{quote(project.name)}'>/projects/{_e(project.name)}</a>",
            f"delegation_surface: {delegation_surface}",
            f"workflow_surface: {workflow_surface}",
            f"run_action_surface: {run_surface}",
            f"next_demo_action: {_e(next_action)}",
            f"action_form_surface: {action_form_surface}",
            "approval_queue_surface: <a href='/approvals'>/approvals</a>",
            "inbox_surface: <a href='/inbox'>/inbox</a>",
            "external_effects_created: false",
            "network_actions_taken_by_app: 0",
        ],
    )


def _verification_page(root: Path) -> str:
    workflow_path = root / ".github" / "workflows" / "tests.yml"
    workflow_text = (
        workflow_path.read_text(encoding="utf-8") if workflow_path.exists() else ""
    )
    workflow_lines = [
        ("workflow_path", ".github/workflows/tests.yml"),
        (
            "workflow_file_status",
            "available" if workflow_path.exists() else "missing",
        ),
        (
            "push_to_main",
            "configured" if _workflow_has_push_main(workflow_text) else "missing",
        ),
        (
            "pull_request_to_main",
            "configured" if _workflow_has_pull_request_main(workflow_text) else "missing",
        ),
        (
            "workflow_dispatch",
            "configured" if "workflow_dispatch:" in workflow_text else "missing",
        ),
        (
            "full_suite_command",
            "python -m pytest -q" if "python -m pytest -q" in workflow_text else "missing",
        ),
        (
            "fast_smoke_job",
            "configured" if "smoke:" in workflow_text else "missing",
        ),
        (
            "route_marker_app_smoke",
            "configured" if "app-smoke-test" in workflow_text else "missing",
        ),
        (
            "fixture_backed_app_demo_smoke",
            "configured" if "app-demo-smoke-test" in workflow_text else "missing",
        ),
        (
            "full_suite_job",
            "configured" if "full-suite:" in workflow_text else "missing",
        ),
        (
            "full_suite_depends_on_smoke",
            "configured" if "needs: smoke" in workflow_text else "missing",
        ),
        ("fast_smoke_timeout_minutes", _workflow_timeout_minutes(workflow_text, "smoke")),
        ("job_timeout_minutes", _workflow_timeout_minutes(workflow_text)),
        ("in_progress_run_status", "not_ci_proof"),
        ("CI_proof_boundary", "CI proof requires a completed passing GitHub Actions run"),
        ("app_network_actions_taken", "0"),
        ("app_external_mutations_taken", "0"),
    ]
    workflow_status = _verification_workflow_status(workflow_lines)
    workflow_step_lines = [
        "Fast smoke job: compile source/tests, route-marker app-smoke-test, fixture-backed app-demo-smoke-test, demo-app-scenario, app --help, dashboard, iterate, git diff --check",
        "Compile source and tests: python -m compileall -q agent_os tests",
        "Run local CLI smoke checks: app-smoke-test, app-demo-smoke-test, demo-app-scenario, app --help, dashboard, iterate",
        "Fixture-backed app demo smoke: creates local demo state and renders demo, dogfooding, selected project, delegation, workflow, run, approvals, inbox, actions, and health pages",
        "Check whitespace: git diff --check",
        "Full suite job: waits for fast smoke verification before spending time on pytest",
        "Run full test suite: python -m pytest -q",
    ]
    workflow_summary_lines = [
        f"{key}: {value}" for key, value in workflow_lines
    ]
    compact_checks = [
        "python3 -m py_compile agent_os/local_app.py tests/test_first_milestone.py",
        "python3 -m pytest tests/test_first_milestone.py -q -k local_app_routes_render_modern_workflow_and_health",
        "python3 -m pytest tests/test_first_milestone.py -q -k local_app_demo_scenario",
        "python3 -m pytest tests/test_first_milestone.py -q -k local_app_cli_commands_and_bind_safety",
        "python3 -m agent_os.cli app-smoke-test",
        "python3 -m agent_os.cli app-demo-smoke-test",
        "git diff --check",
    ]
    return "".join(
        [
            "<section><h1>Verification Handoff</h1>",
            "<p class='muted'>Read-only testing map for the local operator app. Use compact local checks while GitHub Actions runs the slow full suite after a pushed commit.</p>",
            _non_claim_banner(),
            "</section>",
            _verification_command_bar(root, workflow_status),
            "<section id='github-actions-workflow'><h2>GitHub Actions Workflow</h2>",
            _kv(workflow_lines),
            "</section>",
            _list_section("Workflow Configuration Summary", workflow_summary_lines),
            _list_section("GitHub Actions Steps", workflow_step_lines),
            _ci_snapshot_handoff_panel(root, anchor_id="verification-ci-handoff"),
            _latest_ci_evidence_panel(root),
            _list_section(
                "Remote Run State Guidance",
                [
                    "Fast smoke verification can pass before the full suite finishes; treat it as early route/CLI proof only.",
                    "If a GitHub run is still in progress, keep waiting on GitHub rather than rerunning the full suite locally.",
                    "If the GitHub run fails, inspect the failed job log and fix that specific failure before pushing another app slice.",
                    "If the GitHub run reaches the job timeout, treat it as missing full-suite proof and narrow the slow or blocked test in CI.",
                ],
            ),
            _list_section("Compact Local Checks", compact_checks),
            _list_section(
                "Recorded CI Evidence",
                [
                    "<a href='/ci-evidence'>/ci-evidence</a>: operator-supplied CI/deploy proof records already stored in local ClankerOS state.",
                    "The local app reads these records from SQLite and does not fetch GitHub status.",
                ],
            ),
            _list_section(
                "Non-Claims",
                [
                    "The app does not contact GitHub or fetch CI status.",
                    "A pushed commit is not CI proof until the GitHub Actions run completes successfully.",
                    "No push, PR, deploy, provider call, or external mutation is executed by this page.",
                ],
            ),
        ]
    )


def _verification_workflow_status(workflow_lines: list[tuple[str, str]]) -> str:
    expected = {
        "workflow_file_status": "available",
        "push_to_main": "configured",
        "pull_request_to_main": "configured",
        "workflow_dispatch": "configured",
        "full_suite_command": "python -m pytest -q",
        "fast_smoke_job": "configured",
        "route_marker_app_smoke": "configured",
        "fixture_backed_app_demo_smoke": "configured",
        "full_suite_job": "configured",
        "full_suite_depends_on_smoke": "configured",
    }
    values = {key: value for key, value in workflow_lines}
    missing = [
        key
        for key, expected_value in expected.items()
        if values.get(key) != expected_value
    ]
    return "configured" if not missing else "incomplete"


def _ci_evidence_command_state(root: Path) -> dict[str, str]:
    repo_state = _repo_state(root)
    branch = repo_state["branch"] if repo_state["branch"] != "unknown" else "unknown"
    full_commit = _git(root, ["rev-parse", "HEAD"])
    current_commit = full_commit or repo_state["commit"]
    current_commit_known = bool(current_commit and current_commit != "unknown")
    current_commit_label = current_commit if current_commit_known else "unknown"
    latest = _latest_ci_evidence_record(root)
    if latest is None:
        return {
            "branch": branch,
            "current_commit": current_commit_label,
            "latest_source": "none",
            "latest_status": "missing",
            "latest_scope": "none",
            "latest_commit": "none",
            "latest_external_run_id": "none",
            "latest_target": "#record-ci-snapshot-json",
            "current_proof": "missing_current_commit_proof",
            "command_status": "no_records",
            "next_action": "Paste GitHub Actions JSON",
            "target_surface": "#record-ci-snapshot-json",
            "reason": "no_local_ci_evidence_records",
        }

    source_kind, record = latest
    result = getattr(record, "result_json", {}) or {}
    latest_scope = str(result.get("evidence_scope", "unknown"))
    latest_status = str(getattr(record, "status", "unknown"))
    latest_commit = str(getattr(record, "commit_sha", "unknown"))
    if source_kind == "direct_public_snapshot":
        latest_target = "#recent-direct-snapshot-ci-evidence"
    else:
        latest_target = "#recent-ci-evidence"

    if not current_commit_known:
        current_proof = "current_commit_unknown"
        command_status = "records_available_current_commit_unknown"
        next_action = "Confirm checkout then record CI proof"
        target_surface = "#record-ci-snapshot-json"
        reason = "current_checkout_commit_unknown"
    elif latest_commit != current_commit:
        current_proof = "stale_or_different_commit"
        command_status = "latest_record_for_different_commit"
        next_action = "Record current commit CI proof"
        target_surface = "#record-ci-snapshot-json"
        reason = "latest_record_commit_does_not_match_current_checkout"
    elif latest_status == "success" and latest_scope == "workflow_run":
        current_proof = "current_workflow_run_success"
        command_status = "current_full_ci_recorded"
        next_action = "Review latest CI evidence"
        target_surface = latest_target
        reason = "current_commit_has_workflow_run_success"
    elif latest_status == "success" and latest_scope.startswith("workflow_job:"):
        current_proof = "current_job_scope_only"
        command_status = "current_fast_smoke_recorded"
        next_action = "Record full-suite CI proof"
        target_surface = "#record-ci-snapshot-json"
        reason = "latest_record_is_job_scoped_early_proof"
    else:
        current_proof = "current_ci_record_not_full_success"
        command_status = "current_ci_record_needs_review"
        next_action = "Review and refresh CI evidence"
        target_surface = "#record-ci-snapshot-json"
        reason = "latest_record_is_not_full_workflow_success"

    return {
        "branch": branch,
        "current_commit": current_commit_label,
        "latest_source": source_kind,
        "latest_status": latest_status,
        "latest_scope": latest_scope,
        "latest_commit": latest_commit,
        "latest_external_run_id": str(getattr(record, "external_run_id", "unknown")),
        "latest_target": latest_target,
        "current_proof": current_proof,
        "command_status": command_status,
        "next_action": next_action,
        "target_surface": target_surface,
        "reason": reason,
    }


def _verification_command_bar(root: Path, workflow_status: str) -> str:
    state = _ci_evidence_command_state(root)
    if workflow_status != "configured":
        command_status = "workflow_incomplete"
        next_action = "Fix GitHub Actions workflow"
        target_surface = "GitHub Actions Workflow"
        target_href = "#github-actions-workflow"
        reason = "workflow_file_missing_or_incomplete"
    elif state["current_proof"] == "current_workflow_run_success":
        command_status = "ci_proof_recorded"
        next_action = "Use recorded CI evidence"
        target_surface = "/ci-evidence"
        target_href = "/ci-evidence"
        reason = state["reason"]
    else:
        command_status = "waiting_for_github_actions_proof"
        next_action = state["next_action"]
        target_surface = "/ci-evidence#record-ci-snapshot-json"
        target_href = "/ci-evidence#record-ci-snapshot-json"
        reason = state["reason"]
    return "".join(
        [
            "<section id='verification-command-bar' class='panel verification-command-bar' data-verification-command-bar='true'><h2>Verification Command Bar</h2>",
            _kv(
                [
                    ("verification_command_status", command_status),
                    ("verification_command_workflow_status", workflow_status),
                    ("verification_command_branch", state["branch"]),
                    ("verification_command_current_commit", state["current_commit"]),
                    ("verification_command_current_proof", state["current_proof"]),
                    ("verification_command_latest_ci_source", state["latest_source"]),
                    ("verification_command_latest_ci_status", state["latest_status"]),
                    ("verification_command_latest_ci_scope", state["latest_scope"]),
                    ("verification_command_latest_ci_commit", state["latest_commit"]),
                    ("verification_command_latest_ci_run_id", state["latest_external_run_id"]),
                    ("verification_command_next_action", next_action),
                    (
                        "verification_command_target_surface",
                        SafeHtml(
                            f"<a href='{_e(target_href)}'>{_e(target_surface)}</a>"
                        ),
                    ),
                    ("verification_command_reason", reason),
                    ("verification_command_write_on_get", "false"),
                    ("verification_command_github_status_fetch", "none"),
                    ("verification_command_network_actions_taken", "0"),
                    ("verification_command_external_effects_created", "false"),
                    ("verification_command_push_created", "false"),
                    ("verification_command_pr_created", "false"),
                    ("verification_command_deploy_created", "false"),
                ]
            ),
            _ul(
                [
                    f"verification_command_now: {_e(next_action)}",
                    f"verification_command_click: <a href='{_e(target_href)}'>{_e(target_surface)}</a>",
                    f"verification_command_reason: {_e(reason)}",
                    "verification_command_safety: read-only verification guidance",
                ]
            ),
            "</section>",
        ]
    )


def _latest_ci_evidence_panel(root: Path) -> str:
    latest_record = _latest_ci_evidence_record(root)
    if latest_record is None:
        return _list_section(
            "Latest Recorded CI Evidence",
            [
                "latest_ci_status: missing",
                "next_ci_evidence_action: wait_for_github_actions_success_then_record_ci_snapshot_or_deploy_evidence",
                "record_command_template: python3 -m agent_os.cli ci-deploy-evidence <github_handoff_id> --provider github-actions --status success --external-run-id <run_id> --url <run_url>",
                "direct_snapshot_record_command_template: python3 -m agent_os.cli ci-snapshot-evidence --project clankeros --branch main --commit <commit_sha> --provider github-actions --status success --external-run-id <run_id> --url <run_url>",
                "proof_boundary: no local CI proof record yet",
                "github_status_fetch: none",
            ],
        )
    source_kind, record = latest_record
    if source_kind == "direct_public_snapshot":
        return _list_section(
            "Latest Recorded CI Evidence",
            [
                "latest_ci_source: direct_public_snapshot",
                f"latest_ci_status: {_e(record.status)}",
                f"latest_ci_provider: {_e(record.provider)}",
                f"latest_ci_commit: {_e(record.commit_sha)}",
                f"latest_ci_branch: {_e(record.branch_name)}",
                f"latest_ci_external_run_id: {_e(record.external_run_id)}",
                f"latest_ci_url: <a href='{_e(record.external_url)}'>{_e(record.external_url)}</a>",
                "latest_ci_handoff: none",
                f"latest_ci_recorded_by: {_e(record.recorded_by)}",
                f"latest_ci_evidence_path: {_artifact_link(_repo_relative_artifact_path(root, record.evidence_path))}",
                "proof_boundary: operator_supplied_record_only",
                "github_status_fetch: none",
            ],
        )
    return _list_section(
        "Latest Recorded CI Evidence",
        [
            "latest_ci_source: publication_handoff",
            f"latest_ci_status: {_e(record.status)}",
            f"latest_ci_provider: {_e(record.provider)}",
            f"latest_ci_commit: {_e(record.commit_sha)}",
            f"latest_ci_branch: {_e(record.branch_name)}",
            f"latest_ci_external_run_id: {_e(record.external_run_id)}",
            f"latest_ci_url: <a href='{_e(record.external_url)}'>{_e(record.external_url)}</a>",
            f"latest_ci_handoff: {_e(record.github_handoff_id)}",
            f"latest_ci_recorded_by: {_e(record.recorded_by)}",
            f"latest_ci_evidence_path: {_artifact_link(_repo_relative_artifact_path(root, record.evidence_path))}",
            "proof_boundary: operator_supplied_record_only",
            "github_status_fetch: none",
        ],
    )


def _ci_snapshot_handoff_panel(root: Path, *, anchor_id: str | None = None) -> str:
    return _list_section(
        "Direct Snapshot CI Handoff",
        [
            *_ci_snapshot_handoff_lines(root),
            "handoff_status: template_only",
            "record_when: GitHub Actions status=completed conclusion=success and headSha matches the expected commit",
            "proof_boundary: no CI proof is recorded until the operator runs the record-after-success command",
            "github_status_fetch: none",
            "app_network_actions_taken: 0",
            "external_mutations_taken: 0",
        ],
        anchor_id=anchor_id,
    )


def _ci_snapshot_handoff_lines(root: Path, *, key_prefix: str = "ci_snapshot_") -> list[str]:
    state = _repo_state(root)
    branch = state["branch"] if state["branch"] != "unknown" else "<branch>"
    full_commit = _git(root, ["rev-parse", "HEAD"])
    commit = full_commit or (
        state["commit"] if state["commit"] != "unknown" else "<commit_sha>"
    )
    repo = _github_repo_slug(root)
    run_url = f"https://github.com/{repo}/actions/runs/<run_id>"
    handoff_command = (
        "python3 -m agent_os.cli ci-snapshot-handoff "
        f"--project clankeros --branch {branch} --commit {commit} "
        f"--external-run-id <run_id> --repo {repo}"
    )
    status_command = (
        f"gh run view <run_id> --repo {repo} "
        "--json status,conclusion,headSha,headBranch,databaseId,url,jobs"
    )
    record_command = (
        "python3 -m agent_os.cli ci-snapshot-evidence "
        f"--project clankeros --branch {branch} --commit {commit} "
        f"--provider github-actions --status success --external-run-id <run_id> "
        f"--url {run_url}"
    )
    validated_record_command = (
        f"{status_command} | "
        "python3 -m agent_os.cli ci-snapshot-evidence-from-gh-json "
        f"--project clankeros --branch {branch} --commit {commit} "
        "--provider github-actions --status-json -"
    )
    fast_smoke_record_command = (
        f"{status_command} | "
        "python3 -m agent_os.cli ci-snapshot-evidence-from-gh-json "
        f"--project clankeros --branch {branch} --commit {commit} "
        "--provider github-actions --status-json - --job-name 'Fast smoke verification'"
    )
    return [
        f"{key_prefix}handoff_command_template: {_e(handoff_command)}",
        f"{key_prefix}status_check_command_template: {_e(status_command)}",
        f"{key_prefix}fast_smoke_validated_record_command_template: {_e(fast_smoke_record_command)}",
        f"{key_prefix}validated_record_command_template: {_e(validated_record_command)}",
        f"{key_prefix}record_after_success_command_template: {_e(record_command)}",
    ]


def _latest_ci_evidence_record(
    root: Path,
    *,
    project_id: str | None = None,
) -> tuple[str, Any] | None:
    storage = _storage(root)
    limit = None if project_id else 1
    records = storage.list_recent_ci_deploy_evidence_records(limit=limit)
    snapshot_records = storage.list_recent_ci_snapshot_evidence_records(limit=limit)
    if project_id:
        records = [record for record in records if record.project_id == project_id]
        snapshot_records = [
            record for record in snapshot_records if record.project_id == project_id
        ]
    latest_records: list[tuple[str, Any]] = []
    if records:
        latest_records.append(("publication_handoff", records[0]))
    if snapshot_records:
        latest_records.append(("direct_public_snapshot", snapshot_records[0]))
    latest_records.sort(
        key=lambda item: getattr(item[1], "created_at", ""),
        reverse=True,
    )
    if not latest_records:
        return None
    return latest_records[0]


def _ci_evidence_page(root: Path) -> str:
    storage = _storage(root)
    records = storage.list_recent_ci_deploy_evidence_records(limit=20)
    snapshot_records = storage.list_recent_ci_snapshot_evidence_records(limit=20)
    items = [_ci_evidence_line(root, record) for record in records]
    snapshot_items = [
        _ci_snapshot_evidence_line(root, record) for record in snapshot_records
    ]
    return "".join(
        [
            "<section><h1>CI Evidence Records</h1>",
            "<p class='muted'>Read-only view of operator-supplied CI/deploy evidence already recorded in local ClankerOS state.</p>",
            _non_claim_banner(),
            _kv(
                [
                    ("handoff_record_count", str(len(records))),
                    ("snapshot_record_count", str(len(snapshot_records))),
                    ("app_network_actions_taken", "0"),
                    ("external_mutations_taken", "0"),
                    ("github_status_fetch", "none"),
                ]
            ),
            "</section>",
            _ci_evidence_command_bar(root, records, snapshot_records),
            _ci_evidence_recording_guide(root),
            _ci_snapshot_json_recording_form(root),
            _list_section("Recent CI Evidence", items, anchor_id="recent-ci-evidence"),
            _list_section(
                "Recent Direct Snapshot CI Evidence",
                snapshot_items,
                anchor_id="recent-direct-snapshot-ci-evidence",
            ),
            _list_section(
                "Non-Claims",
                [
                    "app_network_actions_taken: 0",
                    "external_mutations_taken: 0",
                    "no GitHub status fetch is performed by the local app.",
                    "CI proof is only as current as the operator-supplied evidence record.",
                    "No push, PR, deploy, provider call, or external mutation is executed by this page.",
                ],
            ),
        ]
    )


def _ci_evidence_command_bar(
    root: Path,
    records: list[Any],
    snapshot_records: list[Any],
) -> str:
    state = _ci_evidence_command_state(root)
    target_href = state["target_surface"]
    target_label = target_href
    if not target_href.startswith("/"):
        target_label = target_href.removeprefix("#").replace("-", " ")
    return "".join(
        [
            "<section id='ci-evidence-command-bar' class='panel ci-evidence-command-bar' data-ci-evidence-command-bar='true'><h2>CI Evidence Command Bar</h2>",
            _kv(
                [
                    ("ci_evidence_command_status", state["command_status"]),
                    ("ci_evidence_command_handoff_record_count", str(len(records))),
                    ("ci_evidence_command_snapshot_record_count", str(len(snapshot_records))),
                    ("ci_evidence_command_branch", state["branch"]),
                    ("ci_evidence_command_current_commit", state["current_commit"]),
                    ("ci_evidence_command_current_proof", state["current_proof"]),
                    ("ci_evidence_command_latest_source", state["latest_source"]),
                    ("ci_evidence_command_latest_status", state["latest_status"]),
                    ("ci_evidence_command_latest_scope", state["latest_scope"]),
                    ("ci_evidence_command_latest_commit", state["latest_commit"]),
                    ("ci_evidence_command_latest_run_id", state["latest_external_run_id"]),
                    ("ci_evidence_command_next_action", state["next_action"]),
                    (
                        "ci_evidence_command_target_surface",
                        SafeHtml(
                            f"<a href='{_e(target_href)}'>{_e(target_label)}</a>"
                        ),
                    ),
                    ("ci_evidence_command_reason", state["reason"]),
                    ("ci_evidence_command_write_on_get", "false"),
                    ("ci_evidence_command_github_status_fetch", "none"),
                    ("ci_evidence_command_network_actions_taken", "0"),
                    ("ci_evidence_command_external_effects_created", "false"),
                    ("ci_evidence_command_push_created", "false"),
                    ("ci_evidence_command_pr_created", "false"),
                    ("ci_evidence_command_deploy_created", "false"),
                ]
            ),
            _ul(
                [
                    f"ci_evidence_command_now: {_e(state['next_action'])}",
                    f"ci_evidence_command_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"ci_evidence_command_reason: {_e(state['reason'])}",
                    "ci_evidence_command_safety: local proof records only",
                ]
            ),
            "</section>",
        ]
    )


def _ci_snapshot_json_recording_form(root: Path) -> str:
    state = _repo_state(root)
    full_commit = _git(root, ["rev-parse", "HEAD"])
    commit = full_commit or (
        state["commit"] if state["commit"] != "unknown" else "<commit_sha>"
    )
    branch = state["branch"] if state["branch"] != "unknown" else "main"
    return "".join(
        [
            "<section id='record-ci-snapshot-json'><h2>Record Direct Snapshot From GitHub JSON</h2>",
            "<p class='muted'>Paste JSON from the displayed <code>gh run view</code> command after GitHub Actions completes, or enter a completed job name to record scoped job proof while the full run is still in progress. The local app can infer the run id and URL from the JSON, validates the supplied JSON before writing CI evidence, and never contacts GitHub itself.</p>",
            "<form method='post' action='/actions/ci-snapshot-evidence-from-gh-json'>",
            f"<label>project <input name='project' value='clankeros'></label>",
            f"<label>branch <input name='branch' value='{_e(branch)}'></label>",
            f"<label>commit <input name='commit' value='{_e(commit)}'></label>",
            "<label>provider <input name='provider' value='github-actions'></label>",
            "<label>external_run_id <input name='external_run_id' value='' placeholder='optional if JSON has databaseId or URL'></label>",
            "<label>url <input name='url' value='' placeholder='optional if JSON has url'></label>",
            "<label>job_name <input name='job_name' value='' placeholder='Fast smoke verification'></label>",
            "<label>recorded_by <input name='recorded_by' value='operator'></label>",
            "<label>note <input name='note' value='Validated from pasted GitHub Actions JSON.'></label>",
            "<label>status_json <textarea name='status_json' rows='10' spellcheck='false'></textarea></label>",
            "<button type='submit'>ci-snapshot-evidence-from-gh-json</button>",
            "</form>",
            _kv(
                [
                    ("confirmation_required", "true"),
                    ("github_status_fetch", "none"),
                    ("network_actions_taken_by_app", "0"),
                    ("external_mutations_taken", "0"),
                    ("external_run_id_inference", "databaseId_or_actions_run_url"),
                    ("external_url_inference", "status_json_url"),
                    ("record_when", "run status=completed conclusion=success headSha matches commit"),
                    ("job_record_when", "named job status=completed conclusion=success headSha matches commit"),
                ]
            ),
            "</section>",
        ]
    )


def _ci_evidence_recording_guide(root: Path) -> str:
    handoffs = _storage(root).list_recent_github_handoff_records(limit=1)
    if not handoffs:
        return _list_section(
            "CI Evidence Recording Guide",
            [
                "latest_github_handoff: missing",
                "next_ci_evidence_action: create_publication_handoff_then_manual_push_pr_outside_clankeros",
                "record_command_template: unavailable_until_github_handoff_exists",
                *_ci_snapshot_handoff_lines(root, key_prefix="direct_snapshot_"),
                "direct_snapshot_record_command_template: python3 -m agent_os.cli ci-snapshot-evidence --project clankeros --branch main --commit <commit_sha> --provider github-actions --status success --external-run-id <run_id> --url <run_url>",
                "required_operator_inputs: GitHub Actions JSON with status, conclusion, headSha, url, databaseId, and optional completed job name",
                "proof_boundary: operator_supplied_record_only",
                "direct_snapshot_boundary: use only for direct operator-authorized pushed snapshots, not publication handoffs",
                "github_status_fetch: none",
            ],
            anchor_id="ci-evidence-recording-guide",
        )

    handoff = handoffs[0]
    return _list_section(
        "CI Evidence Recording Guide",
        [
            f"latest_recordable_handoff_id: {_e(handoff.id)}",
            f"handoff_project: {_e(handoff.project_id)}",
            f"handoff_branch: {_e(handoff.branch_name)}",
            f"handoff_commit: {_e(handoff.commit_sha)}",
            f"handoff_status: {_e(handoff.status)}",
            f"handoff_evidence: {_artifact_link(_repo_relative_artifact_path(root, handoff.evidence_path))}",
            "record_when: GitHub Actions run has completed and the operator has inspected the result",
            f"record_command_template: python3 -m agent_os.cli ci-deploy-evidence {_e(handoff.id)} --provider github-actions --status success --external-run-id <run_id> --url <run_url>",
            *_ci_snapshot_handoff_lines(root, key_prefix="direct_snapshot_"),
            "required_operator_inputs: GitHub Actions JSON with status, conclusion, headSha, url, databaseId, and optional completed job name",
            "proof_boundary: operator_supplied_record_only",
            "github_status_fetch: none",
        ],
        anchor_id="ci-evidence-recording-guide",
    )


def _ci_evidence_line(root: Path, record: Any) -> str:
    evidence_path = _repo_relative_artifact_path(root, record.evidence_path)
    return (
        f"{_e(record.id)}: "
        f"status={_e(record.status)} "
        f"status_source={_e(record.result_json.get('status_source', 'unknown'))} "
        f"evidence_scope={_e(record.result_json.get('evidence_scope', 'unknown'))} "
        f"provider={_e(record.provider)} "
        f"project={_e(record.project_id)} "
        f"branch={_e(record.branch_name)} "
        f"commit={_e(record.commit_sha)} "
        f"github_handoff={_e(record.github_handoff_id)} "
        f"external_run_id: {_e(record.external_run_id)} "
        f"url={_e(record.external_url)} "
        f"recorded_by={_e(record.recorded_by)} "
        f"network_actions_taken={_e(record.result_json.get('network_actions_taken', 'unknown'))} "
        f"external_mutations_taken={_e(record.result_json.get('external_mutations_taken', 'unknown'))} "
        f"evidence_path={_artifact_link(evidence_path)}"
    )


def _ci_snapshot_evidence_line(root: Path, record: Any) -> str:
    evidence_path = _repo_relative_artifact_path(root, record.evidence_path)
    return (
        f"{_e(record.id)}: "
        "source=direct_public_snapshot "
        f"status={_e(record.status)} "
        f"status_source={_e(record.result_json.get('status_source', 'unknown'))} "
        f"evidence_scope={_e(record.result_json.get('evidence_scope', 'unknown'))} "
        f"provider={_e(record.provider)} "
        f"project={_e(record.project_id)} "
        f"branch={_e(record.branch_name)} "
        f"commit={_e(record.commit_sha)} "
        f"external_run_id: {_e(record.external_run_id)} "
        f"url={_e(record.external_url)} "
        f"recorded_by={_e(record.recorded_by)} "
        f"network_actions_taken={_e(record.result_json.get('network_actions_taken', 'unknown'))} "
        f"external_mutations_taken={_e(record.result_json.get('external_mutations_taken', 'unknown'))} "
        f"evidence_path={_artifact_link(evidence_path)}"
    )


def _dogfooding_page(root: Path) -> str:
    storage = _storage(root)
    project = storage.get_registered_project("local-app-demo")
    fixture_status = "available" if project is not None else "missing"
    next_surface = "/demo" if project is not None else "demo-app-scenario"
    fixture_lines = [
        ("demo_fixture_status", fixture_status),
        ("next_operator_surface", next_surface),
        ("app_network_actions_taken", "0"),
        ("external_mutations_taken", "0"),
        ("provider_calls_taken_by_clankeros", "0"),
        ("github_status_fetch", "none"),
        ("push_pr_deploy_status", "outside_clankeros_manual_only"),
    ]
    return "".join(
        [
            "<section><h1>Manual Dogfooding Checklist</h1>",
            "<p class='muted'>A read-only route map for the first browser pass through the local operator app. Use it before pushing, then let GitHub Actions run the slow suite.</p>",
            _non_claim_banner(),
            _kv(fixture_lines),
            "</section>",
            _dogfooding_next_action_panel(root),
            _list_section(
                "Start Or Refresh Fixture",
                [
                    "Run `python3 -m agent_os.cli demo-app-scenario` to create or refresh fixture-backed local state.",
                    "Open <a href='/demo'>/demo</a> and confirm demo_fixture_status before following run-specific links.",
                    "Open <a href='/health'>/health</a> if you need a fresh `.clanker/app/local_app_status.json` readback.",
                ],
            ),
            _list_section(
                "Browser Route Walk",
                [
                    "<a href='/demo'>/demo</a>: fixture launchpad, selected run links, and browser progress.",
                    "<a href='/workflow'>/workflow</a>: full modern workflow; use scoped delegation or run links from `/demo` when available.",
                    "<a href='/projects'>/projects</a>: project goals, linked tasks, and project operator guidance.",
                    "<a href='/delegation-runs'>/delegation-runs</a>: scout evidence, context packs, handoffs, and retry posture.",
                    "<a href='/inbox'>/inbox</a> and <a href='/approvals'>/approvals</a>: local queue and approval gates.",
                    "<a href='/actions'>/actions</a>: safe action catalog and confirmation posture.",
                ],
            ),
            _list_section(
                "Commit And Publication Gate Walk",
                [
                    "From the selected `/runs/<run_id>` page, request a commit only after reviewing diff, changed files, bounded validation, stdout/stderr, and review artifacts.",
                    "Approve the commit request explicitly, type the matching commit message, and keep the commit inside the isolated coder worktree.",
                    "After the local commit exists, request and approve publication handoff preparation.",
                    "Stop at publication handoff: manual push and PR commands stay outside ClankerOS.",
                ],
            ),
            _dogfooding_ci_followup(root),
            _list_section(
                "Verification Handoff",
                [
                    "<a href='/verification'>/verification</a>: checked-in GitHub Actions workflow posture and compact local checks.",
                    "Run compact local checks before pushing; use GitHub Actions for the full suite.",
                    "no GitHub status fetch is performed by the local app.",
                    "CI proof requires a completed passing GitHub Actions run after push.",
                ],
            ),
            _list_section(
                "Safety Boundary",
                [
                    "app_network_actions_taken: 0",
                    "external_mutations_taken: 0",
                    "provider_calls_taken_by_clankeros: 0",
                    "No push, PR creation, deploy, provider call, or GitHub status fetch is executed by this page.",
                ],
            ),
            _demo_dogfooding_state(root),
        ]
    )


def _dogfooding_ci_followup(root: Path) -> str:
    return _list_section(
        "GitHub Actions Follow-up",
        [
            *_ci_snapshot_handoff_lines(root, key_prefix="dogfooding_ci_snapshot_"),
            "record_when: GitHub Actions status=completed conclusion=success and headSha matches the expected commit",
            "proof_boundary: fast smoke is early proof; full-suite CI proof starts only after a completed passing GitHub Actions run is recorded",
            "github_status_fetch: none",
            "app_network_actions_taken: 0",
            "external_mutations_taken: 0",
        ],
    )


def _dogfooding_next_action_panel(root: Path) -> str:
    storage = _storage(root)
    project = storage.get_registered_project("local-app-demo")
    if project is None:
        return _list_section(
            "Dogfooding Next Action",
            [
                "demo_fixture_status: missing",
                "next_dogfooding_action: run_demo_app_scenario",
                "demo_command: python3 -m agent_os.cli demo-app-scenario",
                "demo_surface: <a href='/demo'>/demo</a>",
                "verification_surface: <a href='/verification'>/verification</a>",
                "external_effects_created: false",
                "network_actions_taken_by_app: 0",
            ],
        )

    delegations = [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if _task_project(storage, delegation.parent_task_id) == project.name
    ]
    selected_delegation = delegations[0] if delegations else None
    selected_run = None
    if selected_delegation is not None:
        runs = list_coder_worktree_runs(
            root,
            delegation_id=selected_delegation.id,
            limit=20,
        )
        selected_run = next((run for run in runs if run.status == "completed"), None)
        if selected_run is None and runs:
            selected_run = runs[0]

    next_action = "select_demo_delegation"
    workflow_surface = "<a href='/workflow'>/workflow</a>"
    delegation_surface = "none"
    run_surface = "none"
    action_surface = "<a href='/demo'>/demo</a>"
    if selected_delegation is not None:
        delegation_surface = (
            f"<a href='/delegations/{quote(selected_delegation.id)}'>"
            f"/delegations/{_e(selected_delegation.id)}</a>"
        )
        workflow_surface = (
            f"<a href='/workflow?delegation_id={quote(selected_delegation.id)}'>"
            f"/workflow?delegation_id={_e(selected_delegation.id)}</a>"
        )
        action_surface = delegation_surface
        next_action = "review_delegation_state"
    if selected_run is not None:
        progress = _demo_progress_state(root, selected_run.id)
        next_action = progress["next_step"]
        workflow_surface = (
            f"<a href='/workflow?run_id={quote(selected_run.id)}'>"
            f"/workflow?run_id={_e(selected_run.id)}</a>"
        )
        run_surface = (
            f"<a href='/runs/{quote(selected_run.id)}'>"
            f"/runs/{_e(selected_run.id)}</a>"
        )
        action_surface = run_surface
        if next_action in {
            "approve_or_reject_commit_request",
            "approve_or_reject_publication_request",
        }:
            action_surface = "<a href='/approvals'>/approvals</a>"

    lines = [
        "demo_fixture_status: available",
        f"next_dogfooding_action: {_e(next_action)}",
        f"project_surface: <a href='/projects/{quote(project.name)}'>/projects/{_e(project.name)}</a>",
        f"delegation_surface: {delegation_surface}",
        f"workflow_surface: {workflow_surface}",
        f"run_action_surface: {run_surface}",
        f"action_surface: {action_surface}",
        "approval_queue_surface: <a href='/approvals'>/approvals</a>",
        "inbox_surface: <a href='/inbox'>/inbox</a>",
        "action_catalog_surface: <a href='/actions'>/actions</a>",
        "verification_surface: <a href='/verification'>/verification</a>",
        "external_effects_created: false",
        "network_actions_taken_by_app: 0",
    ]
    if next_action == "manual_operator_push_pr_outside_clankeros":
        lines.append("manual_boundary: outside_clankeros")
    return _list_section("Dogfooding Next Action", lines)


def _workflow_has_push_main(workflow_text: str) -> bool:
    return "push:" in workflow_text and "branches: [main]" in workflow_text


def _workflow_has_pull_request_main(workflow_text: str) -> bool:
    return "pull_request:" in workflow_text and "branches: [main]" in workflow_text


def _workflow_timeout_minutes(workflow_text: str, job_name: str = "full-suite") -> str:
    in_requested_job = False
    requested_prefix = f"{job_name}:"
    for line in workflow_text.splitlines():
        stripped = line.strip()
        if stripped == requested_prefix:
            in_requested_job = True
            continue
        if in_requested_job and line.startswith("  ") and stripped.endswith(":"):
            return "missing"
        if in_requested_job and stripped.startswith("timeout-minutes:"):
            return stripped.split(":", 1)[1].strip() or "missing"
    if job_name != "full-suite":
        return "missing"
    for line in workflow_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("timeout-minutes:"):
            return stripped.split(":", 1)[1].strip() or "missing"
    return "missing"


def _github_repo_slug(root: Path) -> str:
    remote_url = _git(root, ["remote", "get-url", "origin"])
    if not remote_url or "github.com" not in remote_url:
        return "<owner/repo>"
    slug = remote_url.split("github.com", 1)[1].lstrip("/:").strip()
    if slug.endswith(".git"):
        slug = slug[:-4]
    slug = slug.strip("/")
    if "/" not in slug or slug.startswith("."):
        return "<owner/repo>"
    return slug


def _action_catalog_line(item: tuple[str, str, str, str, str, str, str]) -> str:
    action, category, surface, mutates, confirmation, requires, output = item
    return (
        f"<strong>{_e(action)}</strong>: "
        f"category={_e(category)} "
        f"surface={_e(surface)} "
        f"mutates_local_state={_e(mutates)} "
        f"requires_confirmation={_e(confirmation)} "
        f"required_previous_artifact={_e(requires)} "
        f"output_artifact={_e(output)} "
        "external_effects=none"
    )


def _projects(root: Path) -> str:
    storage = _storage(root)
    projects = storage.list_registered_projects()
    return "".join(
        [
            "<section><h1>Project Workflow Index</h1>",
            "<p class='muted'>Project entry points with local repo posture, goal/task counts, delegation links, workflow shortcuts, safe registration, and the next local operator action.</p>",
            "</section>",
            _project_registration_panel(root, projects),
            "<section><h2>Registered Projects</h2>",
            _ul([_project_index_line(root, storage, project) for project in projects]),
            "</section>",
            _non_claim_banner(),
        ]
    )


def _project_registration_panel(root: Path, projects: list[Any]) -> str:
    next_index = len(projects) + 1
    return "".join(
        [
            "<section><h2>Register Local Project</h2>",
            "<p class='muted'>Add another local git repository to the operator cockpit without leaving the browser.</p>",
            _kv(
                [
                    ("project_registration_form_available", "true"),
                    ("project_registration_registered_project_count", str(len(projects))),
                    ("project_registration_confirmation_required", "true"),
                    ("project_registration_provider_calls_taken_by_clankeros", "0"),
                    ("project_registration_network_actions_taken", "0"),
                    ("project_registration_external_effects_created", "false"),
                ]
            ),
            _input_form(
                "register-project",
                {},
                {
                    "name": f"local-project-{next_index}",
                    "path": str(root),
                    "test_command": "python3 -m pytest -q",
                    "allowed_write_roots": str(root),
                },
            ),
            "</section>",
        ]
    )


def _project_index_line(root: Path, storage: Storage, project: Any) -> str:
    project_id = project.name
    repo = _repo_state(Path(project.root_path))
    goal_rows = _table_rows(
        storage.db_path,
        "select id from goals where project_id = ?",
        (project_id,),
    )
    task_rows = _table_rows(
        storage.db_path,
        "select id from tasks where project_id = ?",
        (project_id,),
    )
    delegations = [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if _task_project(storage, delegation.parent_task_id) == project_id
    ]
    state = _project_operator_state(
        root,
        storage,
        project_id=project_id,
        task_rows=task_rows,
    )
    next_action = _project_next_action(
        root,
        open_incidents=state["open_incidents"],
        recommendations=state["recommendations"],
        worktree_approvals=state["worktree_approvals"],
        worktree_runs=state["worktree_runs"],
        commit_approvals=state["commit_approvals"],
        publications=state["publications"],
    )
    workflow_links = [
        f"<a href='/projects/{quote(project_id)}'>open project</a>",
        "<a href='/workflow'>open workflow</a>",
    ]
    if delegations:
        delegation = delegations[0]
        workflow_links.append(
            f"<a href='/workflow?delegation_id={quote(delegation.id)}'>open selected delegation workflow</a>"
        )
    if state["worktree_runs"]:
        run = state["worktree_runs"][0]
        workflow_links.append(
            f"<a href='/workflow?run_id={quote(run.id)}'>open selected coder run workflow</a>"
        )
    return (
        f"<strong><a href='/projects/{quote(project_id)}'>{_e(project_id)}</a></strong>: "
        f"root_path={_e(project.root_path)} "
        f"default_test_command={_e(project.default_test_command)} "
        f"current_branch={_e(repo['branch'])} "
        f"current_commit={_e(repo['commit'])} "
        f"goals: {len(goal_rows)} "
        f"tasks: {len(task_rows)} "
        f"delegations: {len(delegations)} "
        f"project_next_recommended_action={_e(next_action)} "
        + " ".join(workflow_links)
    )


def _delegation_runs(root: Path) -> str:
    storage = _storage(root)
    records = _delegation_run_records(root, storage, limit=50)
    return "".join(
        [
            "<section><h1>Delegation Run Index</h1>",
            "<p class='muted'>Read-only index of scout/delegation execution runs, evidence paths, context packs, handoffs, zero-effect counters, retry signals, and next local operator actions.</p>",
            "</section>",
            _delegation_run_command_bar(root, records),
            _list_section(
                "Delegation Runs Needing Attention",
                [
                    _delegation_run_line(root, storage, delegation, project_id=project)
                    for delegation, project, metadata in records
                    if delegation.status != "completed" or metadata.get("incident_id")
                ],
                anchor_id="delegation-runs-attention",
            ),
            _list_section(
                "Ready For Coder Prep",
                [
                    _delegation_run_line(root, storage, delegation, project_id=project)
                    for delegation, project, metadata in records
                    if delegation.status == "completed"
                    and (
                        metadata.get("implementation_handoff_md")
                        or metadata.get("implementation_handoff_json")
                    )
                ],
                anchor_id="delegation-runs-ready-for-coder-prep",
            ),
            _list_section(
                "Recent Delegation Runs",
                [
                    _delegation_run_line(root, storage, delegation, project_id=project)
                    for delegation, project, _metadata in records
                ],
                anchor_id="delegation-runs-recent",
            ),
            _non_claim_banner(),
        ]
    )


def _delegation_run_command_bar(
    root: Path,
    records: list[tuple[Any, str, dict[str, Any]]],
) -> str:
    completed = [record for record in records if record[0].status == "completed"]
    pending = [record for record in records if record[0].status != "completed"]
    incidents = [record for record in records if record[2].get("incident_id")]
    retry_candidates = [
        record
        for record in records
        if record[0].status != "completed" or record[2].get("incident_id")
    ]
    context_pack_ready = [
        record
        for record in records
        if record[2].get("context_pack_md") or record[2].get("context_pack_json")
    ]
    handoff_ready = [
        record
        for record in records
        if record[2].get("implementation_handoff_md")
        or record[2].get("implementation_handoff_json")
    ]
    first_record = (
        incidents[0]
        if incidents
        else pending[0]
        if pending
        else handoff_ready[0]
        if handoff_ready
        else records[0]
        if records
        else None
    )
    first_id = "none"
    first_project = "none"
    first_run = "none"
    first_status = "none"
    first_profile = "none"
    first_category = "none"
    first_action = "No delegation runs"
    first_reason = "no delegation run records"
    first_target = SafeHtml("<a href='/goals'>/goals</a>")
    first_workflow = SafeHtml("<a href='/workflow'>/workflow</a>")
    first_result = SafeHtml("none")
    if first_record is not None:
        delegation, project, metadata = first_record
        run_id = metadata.get("execution_run_id") or metadata.get("run_id") or "none"
        first_id = delegation.id
        first_project = project
        first_run = str(run_id)
        first_status = delegation.status
        first_profile = delegation.assigned_profile
        first_category = delegation.category
        first_action = _delegation_run_next_action(delegation, metadata)
        first_workflow = SafeHtml(
            f"<a href='/workflow?delegation_id={quote(delegation.id)}'>/workflow?delegation_id={_e(delegation.id)}</a>"
        )
        if run_id != "none":
            first_target = SafeHtml(f"<a href='/runs/{quote(str(run_id))}'>/runs/{_e(str(run_id))}</a>")
        else:
            first_target = SafeHtml(f"<a href='/delegations/{quote(delegation.id)}'>/delegations/{_e(delegation.id)}</a>")
        first_result = SafeHtml(_artifact_link(_repo_relative_artifact_path(root, delegation.result_artifact_path)))
        if metadata.get("incident_id"):
            first_reason = f"incident={metadata.get('incident_id')}"
        elif delegation.status != "completed":
            first_reason = f"delegation_status={delegation.status}"
        elif metadata.get("implementation_handoff_md") or metadata.get("implementation_handoff_json"):
            first_reason = "implementation_handoff_available"
        elif run_id != "none":
            first_reason = "execution_run_available"
        else:
            first_reason = "delegation_result_available"
    lines = [
        f"delegation_run_command_now: {_e(first_action)}",
        f"delegation_run_command_click: {first_target}",
        f"delegation_run_command_workflow: {first_workflow}",
        f"delegation_run_command_reason: {_e(first_reason)}",
        "delegation_run_command_safety: read-only local delegation guidance",
    ]
    if not records:
        lines.append("delegation_run_command_empty: no local delegation runs")
    return "".join(
        [
            "<section class='panel delegation-run-command-bar' data-delegation-run-command-bar='true'><h2>Delegation Run Command Bar</h2>",
            "<p class='muted'>One read-only delegation/run summary for scout evidence, handoff readiness, and retry attention.</p>",
            _kv(
                [
                    ("delegation_run_command_status", "available"),
                    ("delegation_run_command_total", str(len(records))),
                    ("delegation_run_command_completed", str(len(completed))),
                    ("delegation_run_command_pending", str(len(pending))),
                    ("delegation_run_command_incidents", str(len(incidents))),
                    ("delegation_run_command_retry_candidates", str(len(retry_candidates))),
                    ("delegation_run_command_context_packs", str(len(context_pack_ready))),
                    ("delegation_run_command_implementation_handoffs", str(len(handoff_ready))),
                    ("delegation_run_command_first_delegation", first_id),
                    ("delegation_run_command_first_run", first_run),
                    ("delegation_run_command_first_project", first_project),
                    ("delegation_run_command_first_status", first_status),
                    ("delegation_run_command_first_profile", first_profile),
                    ("delegation_run_command_first_category", first_category),
                    ("delegation_run_command_next_action", first_action),
                    ("delegation_run_command_target_surface", first_target),
                    ("delegation_run_command_workflow_surface", first_workflow),
                    ("delegation_run_command_reason", first_reason),
                    ("delegation_run_command_result_artifact", first_result),
                    ("delegation_run_command_write_on_get", "false"),
                    ("delegation_run_command_provider_calls_taken", "0"),
                    ("delegation_run_command_network_actions_taken", "0"),
                    ("delegation_run_command_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _inbox(root: Path) -> str:
    inbox = collect_inbox_items(root)
    return "".join(
        [
            "<section><h1>Operator Inbox</h1>",
            "<p class='muted'>Read-only local operator queue assembled from steering reviews, approvals, incidents, delegations, coder runs, commits, and publication handoffs.</p>",
            "</section>",
            _inbox_command_bar(root, inbox),
            _list_section(
                "Inbox Summary",
                _inbox_summary_lines(root)
                + ["network_actions_taken: 0", "external_mutations_taken: 0"],
                anchor_id="inbox-summary",
            ),
            _list_section(
                "Steering Reviews",
                [_steering_review_line(item) for item in inbox["steering_reviews"]],
                anchor_id="inbox-steering-reviews",
            ),
            _list_section(
                "Pending Approval Requests",
                [_operator_approval_line(item) for item in inbox["pending_approvals"]],
                anchor_id="inbox-pending-approval-requests",
            ),
            _list_section(
                "Open Incidents",
                [_incident_line(item) for item in inbox["open_incidents"]],
                "/incidents",
                anchor_id="inbox-open-incidents",
            ),
            _list_section(
                "Subagent Delegations",
                [_delegation_line(item) for item in inbox["subagent_delegations"]],
                anchor_id="inbox-subagent-delegations",
            ),
            _list_section(
                "Delegation Runs",
                _delegation_run_lines(root, _storage(root), limit=20),
                "/delegation-runs",
                anchor_id="inbox-delegation-runs",
            ),
            _list_section(
                "Pending Worktree Approvals",
                [_approval_line(item) for item in inbox["coder_worktree_approvals"]],
                "/approvals",
                anchor_id="inbox-pending-worktree-approvals",
            ),
            _list_section(
                "Coder Worktree Runs",
                [_coder_run_line(root, item) for item in inbox["coder_worktree_runs"]],
                anchor_id="inbox-coder-worktree-runs",
            ),
            _list_section(
                "Pending Commit Approvals",
                [
                    _commit_inbox_follow_up_line(item)
                    for item in inbox["coder_worktree_commit_approvals"]
                ],
                "/approvals",
                anchor_id="inbox-pending-commit-approvals",
            ),
            _list_section(
                "Local Coder Commits",
                [_commit_line(item) for item in inbox["coder_worktree_commits"]],
                anchor_id="inbox-local-coder-commits",
            ),
            _list_section(
                "Pending Publication Requests",
                [
                    _publication_inbox_follow_up_line(root, item)
                    for item in inbox["coder_publication_requests"]
                ],
                "/approvals",
                anchor_id="inbox-pending-publication-requests",
            ),
            _list_section(
                "Publication Handoffs",
                [_publication_line(root, item) for item in inbox["coder_publication_handoffs"]],
                anchor_id="inbox-publication-handoffs",
            ),
            _non_claim_banner(),
        ]
    )


def _inbox_command_bar(root: Path, inbox: dict[str, object]) -> str:
    steering_reviews = list(inbox["steering_reviews"])
    pending_approvals = list(inbox["pending_approvals"])
    open_incidents = list(inbox["open_incidents"])
    subagent_delegations = list(inbox["subagent_delegations"])
    coder_worktree_approvals = list(inbox["coder_worktree_approvals"])
    coder_worktree_runs = list(inbox["coder_worktree_runs"])
    coder_worktree_commit_approvals = list(inbox["coder_worktree_commit_approvals"])
    coder_worktree_commits = list(inbox["coder_worktree_commits"])
    coder_publication_requests = list(inbox["coder_publication_requests"])
    coder_publication_handoffs = list(inbox["coder_publication_handoffs"])
    total = int(inbox["count"])
    first_kind = "none"
    first_id = "none"
    first_project = "none"
    first_action = "No inbox items"
    first_surface = SafeHtml("<a href='/goals'>/goals</a>")
    first_reason = "no local operator attention items"
    if open_incidents:
        item = open_incidents[0]
        first_kind = "incident"
        first_id = item.id
        first_project = item.project_id
        first_action = "Inspect incident"
        first_surface = SafeHtml("<a href='#inbox-open-incidents'>Open Incidents</a>")
        first_reason = item.summary
    elif steering_reviews:
        item = steering_reviews[0]
        first_kind = "steering_review"
        first_id = item.id
        first_project = item.project_id
        first_action = "Review steering decision"
        first_surface = SafeHtml("<a href='#inbox-steering-reviews'>Steering Reviews</a>")
        first_reason = item.recommended_next_action
    elif pending_approvals:
        item = pending_approvals[0]
        first_kind = "approval_request"
        first_id = item.id
        first_project = item.project_id
        first_action = "Review approval request"
        first_surface = SafeHtml("<a href='#inbox-pending-approval-requests'>Pending Approval Requests</a>")
        first_reason = item.reason
    elif coder_worktree_approvals:
        item = coder_worktree_approvals[0]
        first_kind = "worktree_approval"
        first_id = item.id
        first_project = item.project_id
        first_action = "Approve worktree"
        first_surface = SafeHtml("<a href='#inbox-pending-worktree-approvals'>Pending Worktree Approvals</a>")
        first_reason = "bounded worktree plan is waiting for operator decision"
    elif coder_worktree_commit_approvals:
        item = coder_worktree_commit_approvals[0]
        first_kind = "commit_approval"
        first_id = item.id
        first_project = item.project_id
        first_action = "Approve commit"
        first_surface = SafeHtml("<a href='#inbox-pending-commit-approvals'>Pending Commit Approvals</a>")
        first_reason = "reviewed coder run is waiting for commit decision"
    elif coder_publication_requests:
        item = coder_publication_requests[0]
        first_kind = "publication_request"
        first_id = item.id
        first_project = item.project_id
        first_action = "Approve publication"
        first_surface = SafeHtml("<a href='#inbox-pending-publication-requests'>Pending Publication Requests</a>")
        first_reason = "local publication handoff is waiting for operator decision"
    elif coder_worktree_runs:
        item = coder_worktree_runs[0]
        first_kind = "coder_worktree_run"
        first_id = item.id
        first_project = item.project_id
        first_action = "Open run"
        first_surface = SafeHtml("<a href='#inbox-coder-worktree-runs'>Coder Worktree Runs</a>")
        first_reason = item.status
    elif coder_publication_handoffs:
        item = coder_publication_handoffs[0]
        first_kind = "publication_handoff"
        first_id = item.id
        first_project = item.project_id
        first_action = "Use publication handoff outside ClankerOS"
        first_surface = SafeHtml("<a href='#inbox-publication-handoffs'>Publication Handoffs</a>")
        first_reason = "manual push/PR boundary is ready"
    elif subagent_delegations:
        item = subagent_delegations[0]
        first_kind = "subagent_delegation"
        first_id = item.id
        first_project = _task_project(_storage(root), item.parent_task_id) or "unknown"
        first_action = "Inspect delegation"
        first_surface = SafeHtml("<a href='#inbox-subagent-delegations'>Subagent Delegations</a>")
        first_reason = item.status
    elif coder_worktree_commits:
        item = coder_worktree_commits[0]
        first_kind = "local_coder_commit"
        first_id = item.id
        first_project = item.project_id
        first_action = "Review local commit evidence"
        first_surface = SafeHtml("<a href='#inbox-local-coder-commits'>Local Coder Commits</a>")
        first_reason = item.status
    lines = [
        f"inbox_command_now: {_e(first_action)}",
        f"inbox_command_click: {first_surface}",
        f"inbox_command_reason: {_e(first_reason)}",
        "inbox_command_safety: read-only queue guidance",
    ]
    if total == 0:
        lines.append("inbox_command_empty: no local operator queue items")
    return "".join(
        [
            "<section class='panel inbox-command-bar' data-inbox-command-bar='true'><h2>Inbox Command Bar</h2>",
            "<p class='muted'>One read-only summary of the next operator attention item across the local queue.</p>",
            _kv(
                [
                    ("inbox_command_status", "available"),
                    ("inbox_command_total_items", str(total)),
                    ("inbox_command_steering_reviews", str(len(steering_reviews))),
                    ("inbox_command_pending_approvals", str(len(pending_approvals))),
                    ("inbox_command_open_incidents", str(len(open_incidents))),
                    ("inbox_command_worktree_approvals", str(len(coder_worktree_approvals))),
                    ("inbox_command_commit_approvals", str(len(coder_worktree_commit_approvals))),
                    ("inbox_command_publication_requests", str(len(coder_publication_requests))),
                    ("inbox_command_coder_runs", str(len(coder_worktree_runs))),
                    ("inbox_command_publication_handoffs", str(len(coder_publication_handoffs))),
                    ("inbox_command_first_kind", first_kind),
                    ("inbox_command_first_id", first_id),
                    ("inbox_command_first_project", first_project),
                    ("inbox_command_first_action", first_action),
                    ("inbox_command_first_surface", first_surface),
                    ("inbox_command_first_reason", first_reason),
                    ("inbox_command_write_on_get", "false"),
                    ("inbox_command_network_actions_taken", "0"),
                    ("inbox_command_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _approvals(root: Path) -> str:
    worktree_approvals = list_coder_worktree_approvals(
        root,
        status="pending_operator_approval",
        limit=50,
    )
    commit_approvals = list_coder_worktree_commit_approvals(
        root,
        status="pending_operator_approval",
        limit=50,
    )
    publication_approvals = list_coder_publications(
        root,
        status="pending_operator_approval",
        limit=50,
    )
    return "".join(
        [
            "<section><h1>Approvals</h1>",
            "<p class='muted'>Approval forms write local decision artifacts only. They do not execute work, commit, push, create PRs, deploy, call providers, or use the network.</p>",
            "</section>",
            _approval_queue_command_bar(
                worktree_approvals,
                commit_approvals,
                publication_approvals,
            ),
            _approval_decision_brief(
                root,
                worktree_approvals,
                commit_approvals,
                publication_approvals,
            ),
            _list_section(
                "Pending Worktree Approvals",
                [_worktree_approval_action_line(item) for item in worktree_approvals],
                anchor_id="pending-worktree-approvals",
            ),
            _list_section(
                "Pending Commit Approvals",
                [_commit_approval_action_line(item) for item in commit_approvals],
                anchor_id="pending-commit-approvals",
            ),
            _list_section(
                "Pending Publication Approvals",
                [_publication_approval_action_line(root, item) for item in publication_approvals],
                anchor_id="pending-publication-approvals",
            ),
            _non_claim_banner(),
        ]
    )


def _approval_decision_brief(
    root: Path,
    worktree_approvals: list[Any],
    commit_approvals: list[Any],
    publication_approvals: list[Any],
) -> str:
    status = "empty"
    kind = "none"
    decision_id = "none"
    project = "none"
    action = "No pending approvals"
    action_name = "none"
    decision_surface = SafeHtml("<a href='/goals'>/goals</a>")
    run_surface: str | SafeHtml = "none"
    source_run = "none"
    delegation_surface: str | SafeHtml = "none"
    workflow_surface: str | SafeHtml = SafeHtml("<a href='/goals'>/goals</a>")
    request_artifact: str | SafeHtml = "none"
    evidence_artifact: str | SafeHtml = "none"
    after_decision = "none"
    after_surface: str | SafeHtml = SafeHtml("<a href='/goals'>/goals</a>")
    typed_commit_message_required = "false"
    changed_files = "0"
    remote_target = "none"
    reason = "no_pending_local_approval_decisions"
    context_run = "none"
    context_delegation = "none"

    if worktree_approvals:
        item = worktree_approvals[0]
        status = "needs_worktree_decision"
        kind = "worktree"
        decision_id = item.id
        project = item.project_id
        action = "Approve worktree"
        action_name = "approve-coder-worktree"
        decision_surface = SafeHtml(
            "<a href='#pending-worktree-approvals'>Pending Worktree Approvals</a>"
        )
        run_surface = "not_created_yet"
        source_run = item.source_run_id or "none"
        context_run = "not_created_yet"
        context_delegation = item.delegation_id
        delegation_surface = _path_link(
            f"/delegations/{quote(item.delegation_id)}"
        )
        workflow_surface = _path_link(
            f"/workflow?delegation_id={quote(item.delegation_id)}"
        )
        request_artifact = _artifact_link(
            _repo_relative_artifact_path(root, item.request_artifact_path)
        )
        evidence_artifact = _artifact_link(
            _repo_relative_artifact_path(root, item.source_plan_path)
        )
        after_decision = "run approved worktree from goal or run surface"
        after_surface = workflow_surface
        reason = "bounded_worktree_plan_waiting_for_operator"
    elif commit_approvals:
        item = commit_approvals[0]
        status = "needs_commit_decision"
        kind = "commit"
        decision_id = item.id
        project = item.project_id
        action = "Approve commit"
        action_name = "approve-coder-commit"
        decision_surface = SafeHtml(
            "<a href='#pending-commit-approvals'>Pending Commit Approvals</a>"
        )
        run_surface = _path_link(f"/runs/{quote(item.run_id)}")
        source_run = item.source_run_id or "none"
        context_run = item.run_id
        context_delegation = item.delegation_id
        delegation_surface = _path_link(
            f"/delegations/{quote(item.delegation_id)}"
        )
        workflow_surface = _path_link(f"/workflow?run_id={quote(item.run_id)}")
        request_artifact = _artifact_link(
            _repo_relative_artifact_path(root, item.request_artifact_path)
        )
        evidence_artifact = _artifact_link(
            _repo_relative_artifact_path(root, item.review_path)
        )
        after_decision = "commit approved worktree with typed message"
        after_surface = run_surface
        typed_commit_message_required = "true"
        changed_files = str(len(item.changed_files))
        reason = "reviewed_worktree_commit_waiting_for_operator"
    elif publication_approvals:
        item = publication_approvals[0]
        status = "needs_publication_decision"
        kind = "publication"
        decision_id = item.id
        project = item.project_id
        action = "Approve publication"
        action_name = "approve-coder-publication"
        decision_surface = SafeHtml(
            "<a href='#pending-publication-approvals'>Pending Publication Approvals</a>"
        )
        run_surface = _path_link(f"/runs/{quote(item.run_id)}")
        source_run = item.source_run_id or "none"
        context_run = item.run_id
        context_delegation = item.delegation_id
        delegation_surface = _path_link(
            f"/delegations/{quote(item.delegation_id)}"
        )
        workflow_surface = _path_link(f"/workflow?run_id={quote(item.run_id)}")
        request_artifact = _artifact_link(
            _repo_relative_artifact_path(root, item.request_artifact_path)
        )
        evidence_artifact = _artifact_link(
            _repo_relative_artifact_path(root, item.source_commit_artifact_path)
        )
        after_decision = "prepare publication handoff for manual push/PR"
        after_surface = run_surface
        remote_target = f"{item.remote}/{item.target_branch}"
        reason = "committed_worktree_publication_waiting_for_operator"

    lines = [
        f"approval_decision_now: {_e(action)}",
        f"approval_decision_click: {decision_surface}",
        (
            "approval_decision_context: "
            f"project={_e(project)} run={_e(context_run)} "
            f"delegation={_e(context_delegation)}"
        ),
        f"approval_decision_reason: {_e(reason)}",
        f"approval_decision_evidence: {evidence_artifact}",
        f"approval_decision_after: {_e(after_decision)} at {after_surface}",
        "approval_decision_safety: confirmed local decision artifact only",
    ]
    if status == "empty":
        lines.append("approval_decision_empty: no pending local approval decisions")

    return "".join(
        [
            (
                "<section class='panel approval-decision-brief' "
                "data-approval-decision-brief='true' "
                f"data-approval-decision-status='{_e(status)}'>"
                "<h2>Approval Decision Brief</h2>"
            ),
            "<p class='muted'>The next local approval decision with direct inspection links and post-decision routing.</p>",
            _kv(
                [
                    ("approval_decision_status", status),
                    ("approval_decision_kind", kind),
                    ("approval_decision_id", decision_id),
                    ("approval_decision_project", project),
                    ("approval_decision_action", action),
                    ("approval_decision_action_name", action_name),
                    ("approval_decision_surface", decision_surface),
                    ("approval_decision_run", run_surface),
                    ("approval_decision_source_run", source_run),
                    ("approval_decision_delegation", delegation_surface),
                    ("approval_decision_workflow", workflow_surface),
                    ("approval_decision_request_artifact", request_artifact),
                    ("approval_decision_evidence_artifact", evidence_artifact),
                    ("approval_decision_after_decision", after_decision),
                    ("approval_decision_after_surface", after_surface),
                    (
                        "approval_decision_typed_commit_message_required",
                        typed_commit_message_required,
                    ),
                    ("approval_decision_changed_files", changed_files),
                    ("approval_decision_remote_target", remote_target),
                    ("approval_decision_write_on_get", "false"),
                    ("approval_decision_executes_work", "false"),
                    ("approval_decision_provider_calls_taken_by_clankeros", "0"),
                    ("approval_decision_network_actions_taken", "0"),
                    ("approval_decision_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _approval_queue_command_bar(
    worktree_approvals: list[Any],
    commit_approvals: list[Any],
    publication_approvals: list[Any],
) -> str:
    total = len(worktree_approvals) + len(commit_approvals) + len(publication_approvals)
    first_kind = "none"
    first_id = "none"
    first_project = "none"
    first_action = "No pending approvals"
    first_surface = SafeHtml("<a href='/goals'>/goals</a>")
    after_decision = "none"
    if worktree_approvals:
        item = worktree_approvals[0]
        first_kind = "worktree"
        first_id = item.id
        first_project = item.project_id
        first_action = "Approve worktree"
        first_surface = SafeHtml("<a href='#pending-worktree-approvals'>Pending Worktree Approvals</a>")
        after_decision = "run approved worktree from goal or run surface"
    elif commit_approvals:
        item = commit_approvals[0]
        first_kind = "commit"
        first_id = item.id
        first_project = item.project_id
        first_action = "Approve commit"
        first_surface = SafeHtml("<a href='#pending-commit-approvals'>Pending Commit Approvals</a>")
        after_decision = "commit approved worktree with typed message"
    elif publication_approvals:
        item = publication_approvals[0]
        first_kind = "publication"
        first_id = item.id
        first_project = item.project_id
        first_action = "Approve publication"
        first_surface = SafeHtml("<a href='#pending-publication-approvals'>Pending Publication Approvals</a>")
        after_decision = "prepare publication handoff for manual push/PR"
    lines = [
        f"approval_queue_now: {_e(first_action)}",
        f"approval_queue_click: {first_surface}",
        f"approval_queue_after_decision: {_e(after_decision)}",
        "approval_queue_safety: local decision artifact only",
    ]
    if total == 0:
        lines.append("approval_queue_empty: no pending local approval decisions")
    return "".join(
        [
            "<section class='panel approval-queue-command-bar' data-approval-queue-command-bar='true'><h2>Approval Queue Command Bar</h2>",
            "<p class='muted'>One read-only summary of the local decisions waiting for the operator.</p>",
            _kv(
                [
                    ("approval_queue_status", "available"),
                    ("approval_queue_total_pending", str(total)),
                    ("approval_queue_worktree_pending", str(len(worktree_approvals))),
                    ("approval_queue_commit_pending", str(len(commit_approvals))),
                    ("approval_queue_publication_pending", str(len(publication_approvals))),
                    ("approval_queue_first_kind", first_kind),
                    ("approval_queue_first_id", first_id),
                    ("approval_queue_first_project", first_project),
                    ("approval_queue_first_action", first_action),
                    ("approval_queue_first_surface", first_surface),
                    ("approval_queue_after_decision", after_decision),
                    ("approval_queue_write_on_get", "false"),
                    ("approval_queue_network_actions_taken", "0"),
                    ("approval_queue_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _incidents(root: Path) -> str:
    storage = _storage(root)
    incidents = storage.list_recent_incidents(limit=50)
    recommendations = storage.list_task_recommendations(limit=50)
    open_incidents = [item for item in incidents if item.status == "open"]
    resolved_incidents = [item for item in incidents if item.status != "open"]
    open_recommendations = [item for item in recommendations if item.status == "open"]
    return "".join(
        [
            "<section><h1>Incidents</h1>",
            "<p class='muted'>Read-only triage board for local incidents and recovery recommendations. Resolution still happens through explicit operator commands, not page load.</p>",
            "</section>",
            _incident_triage_command_bar(
                incidents=incidents,
                open_incidents=open_incidents,
                resolved_incidents=resolved_incidents,
                recommendations=recommendations,
                open_recommendations=open_recommendations,
            ),
            _list_section(
                "Open Incidents",
                [_incident_line(item) for item in open_incidents],
                anchor_id="incident-open",
            ),
            _list_section(
                "Resolved Incidents",
                [_incident_line(item) for item in resolved_incidents],
                anchor_id="incident-resolved",
            ),
            _list_section(
                "Task Recommendations",
                [_task_recommendation_line(item) for item in recommendations],
                anchor_id="incident-recommendations",
            ),
            _non_claim_banner(),
        ]
    )


def _incident_triage_command_bar(
    *,
    incidents: list[Any],
    open_incidents: list[Any],
    resolved_incidents: list[Any],
    recommendations: list[Any],
    open_recommendations: list[Any],
) -> str:
    first_kind = "none"
    first_id = "none"
    first_project = "none"
    first_goal = "none"
    first_task = "none"
    first_run = "none"
    first_severity = "none"
    first_reason = "no local incidents or recommendations"
    first_evidence = SafeHtml("none")
    next_action = "No incident triage needed"
    target_href = "/goals"
    target_label = "/goals"
    if open_incidents:
        item = open_incidents[0]
        first_kind = "incident"
        first_id = item.id
        first_project = item.project_id
        first_goal = item.goal_id or "none"
        first_task = item.task_id or "none"
        first_run = item.run_id or "none"
        first_severity = item.severity
        first_reason = item.summary
        first_evidence = SafeHtml(_artifact_link(item.evidence_path or "none"))
        next_action = "Inspect open incident"
        target_href = "#incident-open"
        target_label = "Open Incidents"
    elif open_recommendations:
        item = open_recommendations[0]
        first_kind = "recommendation"
        first_id = item.id
        first_project = item.project_id
        first_goal = item.goal_id
        first_task = item.task_id
        first_run = item.run_id or "none"
        first_severity = item.source_status
        first_reason = item.reason
        first_evidence = SafeHtml(_artifact_link(item.evidence_path))
        next_action = "Review recovery recommendation"
        target_href = "#incident-recommendations"
        target_label = "Task Recommendations"
    elif resolved_incidents:
        item = resolved_incidents[0]
        first_kind = "resolved_incident"
        first_id = item.id
        first_project = item.project_id
        first_goal = item.goal_id or "none"
        first_task = item.task_id or "none"
        first_run = item.run_id or "none"
        first_severity = item.severity
        first_reason = item.summary
        first_evidence = SafeHtml(_artifact_link(item.evidence_path or "none"))
        next_action = "Review resolved incident history"
        target_href = "#incident-resolved"
        target_label = "Resolved Incidents"
    elif recommendations:
        item = recommendations[0]
        first_kind = "recommendation_history"
        first_id = item.id
        first_project = item.project_id
        first_goal = item.goal_id
        first_task = item.task_id
        first_run = item.run_id or "none"
        first_severity = item.source_status
        first_reason = item.reason
        first_evidence = SafeHtml(_artifact_link(item.evidence_path))
        next_action = "Review recommendation history"
        target_href = "#incident-recommendations"
        target_label = "Task Recommendations"
    target_surface = SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>")
    lines = [
        f"incident_triage_now: {_e(next_action)}",
        f"incident_triage_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
        f"incident_triage_reason: {_e(first_reason)}",
        "incident_triage_safety: read-only local triage guidance",
    ]
    if not incidents and not recommendations:
        lines.append("incident_triage_empty: no local incident or recommendation records")
    return "".join(
        [
            "<section class='panel incident-command-bar' data-incident-command-bar='true'><h2>Incident Triage Command Bar</h2>",
            "<p class='muted'>One read-only triage summary for local incidents and task recovery recommendations.</p>",
            _kv(
                [
                    ("incident_triage_status", "available"),
                    ("incident_triage_total_incidents", str(len(incidents))),
                    ("incident_triage_open_incidents", str(len(open_incidents))),
                    ("incident_triage_resolved_incidents", str(len(resolved_incidents))),
                    ("incident_triage_total_recommendations", str(len(recommendations))),
                    ("incident_triage_open_recommendations", str(len(open_recommendations))),
                    ("incident_triage_first_kind", first_kind),
                    ("incident_triage_first_id", first_id),
                    ("incident_triage_first_project", first_project),
                    ("incident_triage_first_goal", first_goal),
                    ("incident_triage_first_task", first_task),
                    ("incident_triage_first_run", first_run),
                    ("incident_triage_first_severity_or_source", first_severity),
                    ("incident_triage_next_action", next_action),
                    ("incident_triage_target_surface", target_surface),
                    ("incident_triage_reason", first_reason),
                    ("incident_triage_evidence", first_evidence),
                    ("incident_triage_write_on_get", "false"),
                    ("incident_triage_resolution_on_get", "false"),
                    ("incident_triage_provider_calls_taken", "0"),
                    ("incident_triage_network_actions_taken", "0"),
                    ("incident_triage_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _project_detail(root: Path, project_id: str) -> str:
    storage = _storage(root)
    project = storage.get_registered_project(project_id)
    if project is None:
        return "<p class='error'>Project not found.</p>"
    repo = _repo_state(Path(project.root_path))
    goal_rows = _table_rows(
        storage.db_path,
        "select * from goals where project_id = ? order by updated_at desc limit 20",
        (project_id,),
    )
    task_rows = _table_rows(
        storage.db_path,
        "select id, goal_id, status, task_type, description from tasks where project_id = ? order by updated_at desc limit 20",
        (project_id,),
    )
    delegations = [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if _task_project(storage, delegation.parent_task_id) == project_id
    ][:20]
    operator_state = _project_operator_state(
        root,
        storage,
        project_id=project_id,
        task_rows=task_rows,
    )
    return "".join(
        [
            f"<section><h1>Project {_e(project.name)}</h1>",
            _kv(
                [
                    ("root_path", project.root_path),
                    ("default_test_command", project.default_test_command),
                    ("current_branch", repo["branch"]),
                    ("current_commit", repo["commit"]),
                    ("allowed_write_roots", ", ".join(project.allowed_write_roots)),
                ]
            ),
            "</section>",
            _project_command_bar(
                root,
                project_id=project_id,
                repo=repo,
                goal_rows=goal_rows,
                task_rows=task_rows,
                delegations=delegations,
                operator_state=operator_state,
            ),
            _project_goal_creation_panel(project_id, goal_rows),
            _list_section(
                "Project Goals",
                [
                    _goal_index_line(root, storage, row)
                    for row in goal_rows
                ],
            ),
            _list_section(
                "Project Tasks",
                [
                    f"{_e(row['id'])}: status={_e(row['status'])} "
                    f"goal={_e(row['goal_id'])} type={_e(row['task_type'])} - {_e(row['description'])}"
                    for row in task_rows
                ],
            ),
            _list_section(
                "Delegations",
                [
                    f"<a href='/delegations/{quote(delegation.id)}'>{_e(delegation.id)}</a>: {delegation.status} {delegation.title}"
                    for delegation in delegations
                ],
            ),
            _list_section(
                "Delegation Runs",
                _delegation_run_lines(root, storage, project_id=project_id, limit=20),
                "/delegation-runs",
            ),
            _project_operator_guidance(
                root,
                storage,
                project_id=project_id,
                task_rows=task_rows,
                operator_state=operator_state,
            ),
            _project_workflow_launchpad(
                root,
                storage,
                project_id=project_id,
                delegations=delegations,
            ),
            _list_section(
                "Implementation Handoffs",
                _implementation_handoff_lines(root, storage, project_id=project_id, limit=20),
            ),
            _list_section(
                "Coder Prep / Worktree / Publication Artifacts",
                _artifact_links(
                    list_coder_prep_packets(root)
                    + list_coder_worktree_plan_packets(root)
                    + [
                        {"_path": publication.request_artifact_path, "kind": "coder_publication", "id": publication.id}
                        for publication in list_coder_publications(root, limit=20)
                        if publication.project_id == project_id
                    ]
                ),
            ),
        ]
    )


def _project_command_bar(
    root: Path,
    *,
    project_id: str,
    repo: dict[str, Any],
    goal_rows: list[sqlite3.Row],
    task_rows: list[sqlite3.Row],
    delegations: list[Any],
    operator_state: dict[str, Any],
) -> str:
    active_goals = [row for row in goal_rows if _goal_bucket(row) == "active"]
    paused_goals = [row for row in goal_rows if _goal_bucket(row) == "paused"]
    completed_goals = [row for row in goal_rows if _goal_bucket(row) == "completed"]
    next_action = _project_next_action(
        root,
        open_incidents=operator_state["open_incidents"],
        recommendations=operator_state["recommendations"],
        worktree_approvals=operator_state["worktree_approvals"],
        worktree_runs=operator_state["worktree_runs"],
        commit_approvals=operator_state["commit_approvals"],
        publications=operator_state["publications"],
    )
    target_href, target_label, reason = _project_next_action_target(
        root,
        project_id,
        next_action=next_action,
        goal_rows=goal_rows,
        delegations=delegations,
        operator_state=operator_state,
    )
    pending_approvals = (
        _count_status(operator_state["worktree_approvals"], "pending_operator_approval")
        + _count_status(operator_state["commit_approvals"], "pending_operator_approval")
        + _count_status(operator_state["publications"], "pending_operator_approval")
    )
    ready_publications = _count_status(operator_state["publications"], "ready_for_operator")
    open_incidents = len(operator_state["open_incidents"])
    open_recommendations = len(operator_state["recommendations"])
    lead_goal = active_goals[0] if active_goals else (paused_goals[0] if paused_goals else (goal_rows[0] if goal_rows else None))
    lead_goal_value: str | SafeHtml = "none"
    if lead_goal is not None:
        lead_goal_id = str(lead_goal["id"])
        lead_goal_label = str(lead_goal["title"] or lead_goal["description"] or lead_goal_id)
        lead_goal_value = SafeHtml(
            f"<a href='/goals/{quote(lead_goal_id)}'>{_e(_compact_label(lead_goal_label, 72))}</a>"
        )
    lines = [
        f"project_command_now: {_e(next_action)}",
        f"project_command_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
        f"project_command_reason: {_e(reason)}",
        "project_command_safety: read-only project guidance",
    ]
    if not goal_rows:
        lines.append("project_command_empty: create the first goal for this project")
    return "".join(
        [
            "<section class='panel project-command-bar' data-project-command-bar='true'><h2>Project Command Bar</h2>",
            "<p class='muted'>One read-only project summary for the next local operator action before the longer project inventory.</p>",
            _kv(
                [
                    ("project_command_status", "available"),
                    ("project_command_project", project_id),
                    ("project_command_branch", repo["branch"]),
                    ("project_command_commit", repo["commit"]),
                    ("project_command_active_goals", str(len(active_goals))),
                    ("project_command_paused_goals", str(len(paused_goals))),
                    ("project_command_completed_goals", str(len(completed_goals))),
                    ("project_command_tasks", str(len(task_rows))),
                    ("project_command_delegations", str(len(delegations))),
                    ("project_command_coder_runs", str(len(operator_state["worktree_runs"]))),
                    ("project_command_pending_approvals", str(pending_approvals)),
                    ("project_command_open_incidents", str(open_incidents)),
                    ("project_command_open_recommendations", str(open_recommendations)),
                    ("project_command_publication_handoffs", str(ready_publications)),
                    ("project_command_lead_goal", lead_goal_value),
                    ("project_command_next_action", next_action),
                    ("project_command_target_surface", SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>")),
                    ("project_command_reason", reason),
                    ("project_command_write_on_get", "false"),
                    ("project_command_network_actions_taken", "0"),
                    ("project_command_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _project_next_action_target(
    root: Path,
    project_id: str,
    *,
    next_action: str,
    goal_rows: list[sqlite3.Row],
    delegations: list[Any],
    operator_state: dict[str, Any],
) -> tuple[str, str, str]:
    if operator_state["open_incidents"]:
        incident = operator_state["open_incidents"][0]
        return "/incidents", "/incidents", str(incident["summary"])
    if operator_state["recommendations"]:
        recommendation = operator_state["recommendations"][0]
        return "/incidents", "/incidents", str(recommendation.reason)
    ready_publication = next(
        (item for item in operator_state["publications"] if item.status == "ready_for_operator"),
        None,
    )
    if ready_publication is not None:
        return (
            f"/runs/{quote(ready_publication.run_id)}",
            f"/runs/{ready_publication.run_id}",
            "manual publication handoff is ready outside ClankerOS",
        )
    approved_publication = next(
        (item for item in operator_state["publications"] if item.status == "approved"),
        None,
    )
    if approved_publication is not None:
        return (
            f"/runs/{quote(approved_publication.run_id)}",
            f"/runs/{approved_publication.run_id}",
            "approved publication needs a local handoff packet",
        )
    pending_publication = next(
        (item for item in operator_state["publications"] if item.status == "pending_operator_approval"),
        None,
    )
    if pending_publication is not None:
        return "/approvals", "/approvals", f"publication approval {pending_publication.id} is pending"
    committed = next(
        (item for item in operator_state["commit_approvals"] if item.status == "committed"),
        None,
    )
    if committed is not None and not operator_state["publications"]:
        return (
            f"/runs/{quote(committed.run_id)}",
            f"/runs/{committed.run_id}",
            "local commit exists and needs a publication request",
        )
    approved_commit = next(
        (item for item in operator_state["commit_approvals"] if item.status == "approved"),
        None,
    )
    if approved_commit is not None:
        return (
            f"/runs/{quote(approved_commit.run_id)}",
            f"/runs/{approved_commit.run_id}",
            "commit approval is ready for local worktree commit",
        )
    pending_commit = next(
        (item for item in operator_state["commit_approvals"] if item.status == "pending_operator_approval"),
        None,
    )
    if pending_commit is not None:
        return "/approvals", "/approvals", f"commit approval {pending_commit.id} is pending"
    reviewed_run = next(
        (
            item
            for item in operator_state["worktree_runs"]
            if item.status == "completed"
            and _run_review_gate_state(root, item)["commit_request_form_available"]
        ),
        None,
    )
    if reviewed_run is not None:
        return (
            f"/runs/{quote(reviewed_run.id)}",
            f"/runs/{reviewed_run.id}",
            "reviewed coder run can request commit approval",
        )
    pending_worktree = next(
        (item for item in operator_state["worktree_approvals"] if item.status == "pending_operator_approval"),
        None,
    )
    if pending_worktree is not None:
        return "/approvals", "/approvals", f"worktree approval {pending_worktree.id} is pending"
    approved_worktree = next(
        (item for item in operator_state["worktree_approvals"] if item.status == "approved"),
        None,
    )
    if approved_worktree is not None and not operator_state["worktree_runs"]:
        return (
            f"/workflow?delegation_id={quote(approved_worktree.delegation_id)}",
            f"/workflow?delegation_id={approved_worktree.delegation_id}",
            "approved worktree is waiting for confirmed execution",
        )
    if delegations:
        delegation = delegations[0]
        return (
            f"/delegations/{quote(delegation.id)}",
            f"/delegations/{delegation.id}",
            "project has delegation evidence to review",
        )
    if goal_rows:
        goal_id = str(goal_rows[0]["id"])
        return (
            f"/goals/{quote(goal_id)}",
            f"/goals/{goal_id}",
            f"{next_action} for latest project goal",
        )
    return (
        f"/projects/{quote(project_id)}#start-goal-for-this-project",
        "Start Goal For This Project",
        "no project goals exist yet",
    )


def _project_goal_creation_panel(project_id: str, goal_rows: list[sqlite3.Row]) -> str:
    return "".join(
        [
            "<section id='start-goal-for-this-project'><h2>Start Goal For This Project</h2>",
            "<p class='muted'>Create the next local goal for this registered project without leaving the project page.</p>",
            _kv(
                [
                    ("project_goal_creation_form_available", "true"),
                    ("project_goal_creation_project_id", project_id),
                    ("project_goal_creation_existing_goal_count", str(len(goal_rows))),
                    ("project_goal_creation_confirmation_required", "true"),
                    ("project_goal_creation_provider_calls_taken_by_clankeros", "0"),
                    ("project_goal_creation_network_actions_taken", "0"),
                    ("project_goal_creation_external_effects_created", "false"),
                ]
            ),
            _input_form(
                "create-goal",
                {"project_id": project_id},
                {
                    "prompt": "Describe the next local coding goal for this project.",
                    "created_by_profile": "planner",
                },
            ),
            "</section>",
        ]
    )


def _project_operator_guidance(
    root: Path,
    storage: Storage,
    *,
    project_id: str,
    task_rows: list[sqlite3.Row],
    operator_state: dict[str, Any] | None = None,
) -> str:
    state = operator_state or _project_operator_state(
        root,
        storage,
        project_id=project_id,
        task_rows=task_rows,
    )
    incidents = state["incidents"]
    open_incidents = state["open_incidents"]
    recommendations = state["recommendations"]
    worktree_approvals = state["worktree_approvals"]
    worktree_runs = state["worktree_runs"]
    commit_approvals = state["commit_approvals"]
    publications = state["publications"]
    completed_runs = [item for item in worktree_runs if item.status == "completed"]
    reviewed_runs = [
        item
        for item in completed_runs
        if _run_review_gate_state(root, item)["commit_request_form_available"]
    ]
    guidance = "<section><h2>Project Operator Guidance</h2>" + _kv(
        [
            (
                "project_next_recommended_action",
                _project_next_action(
                    root,
                    open_incidents=open_incidents,
                    recommendations=recommendations,
                    worktree_approvals=worktree_approvals,
                    worktree_runs=worktree_runs,
                    commit_approvals=commit_approvals,
                    publications=publications,
                ),
            ),
            ("tasks", str(len(task_rows))),
            ("open_project_incidents", str(len(open_incidents))),
            ("task_recommendations", str(len(recommendations))),
            (
                "pending_worktree_approvals",
                str(_count_status(worktree_approvals, "pending_operator_approval")),
            ),
            ("completed_worktree_runs", str(len(completed_runs))),
            ("reviewed_completed_worktree_runs", str(len(reviewed_runs))),
            (
                "pending_commit_approvals",
                str(_count_status(commit_approvals, "pending_operator_approval")),
            ),
            ("local_commits", str(_count_status(commit_approvals, "committed"))),
            (
                "pending_publication_approvals",
                str(_count_status(publications, "pending_operator_approval")),
            ),
            ("publication_handoffs", str(_count_status(publications, "ready_for_operator"))),
        ]
    ) + "</section>"
    incident_lines = [
        f"{_e(row['id'])}: status={_e(row['status'])} severity={_e(row['severity'])} "
        f"{_e(row['summary'])} evidence={_artifact_link(row['evidence_path'] or 'none')}"
        for row in incidents
    ]
    recommendation_lines = [
        _task_recommendation_line(item)
        for item in recommendations
    ]
    return guidance + _list_section(
        "Incidents / Recommendations",
        incident_lines + recommendation_lines,
        "/incidents" if incidents else None,
    )


def _project_workflow_launchpad(
    root: Path,
    storage: Storage,
    *,
    project_id: str,
    delegations: list[Any],
) -> str:
    coder_runs = [
        item
        for item in list_coder_worktree_runs(root, limit=100)
        if item.project_id == project_id
    ]
    project_lines = [
        "project_workflow_stage: project_ready",
        "<a href='/workflow'>open full workflow stepper</a>",
        "<a href='/actions'>open safe action catalog</a>",
        "<a href='/dogfooding'>open manual dogfooding checklist</a>",
        "<a href='/verification'>open verification handoff</a>",
    ]
    delegation_lines = [
        f"<a href='/delegations/{quote(delegation.id)}'>{_e(delegation.id)}</a>: "
        f"<a href='/workflow?delegation_id={quote(delegation.id)}'>selected workflow</a> "
        f"status={_e(delegation.status)} title={_e(delegation.title)}"
        for delegation in delegations[:10]
    ]
    run_lines = [
        f"<a href='/runs/{quote(run.id)}'>{_e(run.id)}</a>: "
        f"<a href='/workflow?run_id={quote(run.id)}'>selected workflow</a> "
        f"status={_e(run.status)} changed_files={_e(str(len(run.changed_files)))}"
        for run in coder_runs[:10]
    ]
    return "".join(
        [
            "<section><h2>Project Workflow Launchpad</h2>",
            _ul(project_lines),
            "</section>",
            _list_section("Launch Delegation Workflows", delegation_lines),
            _list_section("Launch Coder Run Workflows", run_lines),
        ]
    )


def _project_operator_state(
    root: Path,
    storage: Storage,
    *,
    project_id: str,
    task_rows: list[sqlite3.Row],
) -> dict[str, Any]:
    task_ids = [str(row["id"]) for row in task_rows]
    incidents = _table_rows(
        storage.db_path,
        "select id, status, severity, summary, evidence_path from incidents where project_id = ? order by created_at desc limit 20",
        (project_id,),
    )
    return {
        "incidents": incidents,
        "open_incidents": [row for row in incidents if row["status"] == "open"],
        "recommendations": _project_task_recommendations(storage, task_ids),
        "worktree_approvals": [
            item
            for item in list_coder_worktree_approvals(root, limit=100)
            if item.project_id == project_id
        ],
        "worktree_runs": [
            item
            for item in list_coder_worktree_runs(root, limit=100)
            if item.project_id == project_id
        ],
        "commit_approvals": [
            item
            for item in list_coder_worktree_commit_approvals(root, limit=100)
            if item.project_id == project_id
        ],
        "publications": [
            item
            for item in list_coder_publications(root, limit=100)
            if item.project_id == project_id
        ],
    }


def _project_task_recommendations(
    storage: Storage,
    task_ids: list[str],
) -> list[Any]:
    recommendations: list[Any] = []
    seen: set[str] = set()
    for task_id in task_ids:
        for item in storage.list_task_recommendations(
            task_id=task_id,
            status="open",
            limit=10,
        ):
            if item.id in seen:
                continue
            seen.add(item.id)
            recommendations.append(item)
    return recommendations[:20]


def _dashboard_next_action(root: Path, storage: Storage) -> DashboardNextAction:
    open_incidents = _table_rows(
        storage.db_path,
        "select id, project_id, summary from incidents "
        "where status = 'open' order by created_at desc limit 1",
    )
    if open_incidents:
        incident = open_incidents[0]
        return DashboardNextAction(
            "review_project_incidents",
            "/incidents",
            str(incident["id"]),
            str(incident["summary"]),
        )

    recommendations = _table_rows(
        storage.db_path,
        "select id, task_id, reason from task_recommendations "
        "where status = 'open' order by created_at desc limit 1",
    )
    if recommendations:
        recommendation = recommendations[0]
        return DashboardNextAction(
            "review_task_recommendations",
            "/incidents",
            str(recommendation["id"]),
            str(recommendation["reason"]),
        )

    publications = list_coder_publications(root, limit=200)
    for status, action, href in [
        ("ready_for_operator", "manual_operator_push_pr_outside_clankeros", None),
        ("approved", "prepare_publication_handoff", None),
        (
            "pending_operator_approval",
            "approve_or_reject_publication_request",
            "/approvals",
        ),
    ]:
        publication = next((item for item in publications if item.status == status), None)
        if publication is not None:
            return DashboardNextAction(
                action,
                href or f"/runs/{quote(publication.run_id)}",
                publication.run_id,
                f"publication_status={publication.status} project={publication.project_id}",
            )

    commit_approvals = list_coder_worktree_commit_approvals(root, limit=200)
    publication_run_ids = {item.run_id for item in publications}
    committed_without_publication = next(
        (
            item
            for item in commit_approvals
            if item.status == "committed" and item.run_id not in publication_run_ids
        ),
        None,
    )
    if committed_without_publication is not None:
        return DashboardNextAction(
            "request_publication_handoff",
            f"/runs/{quote(committed_without_publication.run_id)}",
            committed_without_publication.run_id,
            f"local_commit={committed_without_publication.commit_sha or 'recorded'}",
        )

    approved_commit = next(
        (item for item in commit_approvals if item.status == "approved"),
        None,
    )
    if approved_commit is not None:
        return DashboardNextAction(
            "commit_approved_worktree",
            f"/runs/{quote(approved_commit.run_id)}",
            approved_commit.run_id,
            f"commit_approval={approved_commit.id}",
        )

    pending_commit = next(
        (
            item
            for item in commit_approvals
            if item.status == "pending_operator_approval"
        ),
        None,
    )
    if pending_commit is not None:
        return DashboardNextAction(
            "approve_or_reject_commit_request",
            "/approvals",
            pending_commit.id,
            f"run={pending_commit.run_id}",
        )

    worktree_runs = list_coder_worktree_runs(root, limit=200)
    commit_run_ids = {item.run_id for item in commit_approvals}
    reviewed_run = next(
        (
            item
            for item in worktree_runs
            if item.status == "completed"
            and item.id not in commit_run_ids
            and _run_review_gate_state(root, item)["commit_request_form_available"]
        ),
        None,
    )
    if reviewed_run is not None:
        return DashboardNextAction(
            "request_commit_for_reviewed_run",
            f"/runs/{quote(reviewed_run.id)}",
            reviewed_run.id,
            f"review_exists_for_source_run={reviewed_run.source_run_id}",
        )

    worktree_approvals = list_coder_worktree_approvals(root, limit=200)
    pending_worktree = next(
        (
            item
            for item in worktree_approvals
            if item.status == "pending_operator_approval"
        ),
        None,
    )
    if pending_worktree is not None:
        return DashboardNextAction(
            "decide_pending_worktree_approval",
            "/approvals",
            pending_worktree.id,
            f"delegation={pending_worktree.delegation_id}",
        )

    run_delegation_ids = {item.delegation_id for item in worktree_runs}
    approved_worktree = next(
        (
            item
            for item in worktree_approvals
            if item.status == "approved" and item.delegation_id not in run_delegation_ids
        ),
        None,
    )
    if approved_worktree is not None:
        return DashboardNextAction(
            "run_approved_worktree_from_cli",
            f"/workflow?delegation_id={quote(approved_worktree.delegation_id)}",
            approved_worktree.delegation_id,
            f"worktree_approval={approved_worktree.id}",
        )

    project_count = len(storage.list_registered_projects())
    if project_count:
        return DashboardNextAction(
            "review_project_state",
            "/projects",
            f"projects={project_count}",
            "no higher-priority approval, reviewed run, publication, incident, or recommendation is pending",
        )
    return DashboardNextAction(
        "run_demo_scenario_or_register_project",
        "/demo",
        "no_registered_projects",
        "create fixture state or register a real local project",
    )


def _dashboard_next_action_section(next_action: DashboardNextAction) -> str:
    return "<section><h2>Next Recommended Action</h2>" + _kv(
        [
            ("dashboard_next_recommended_action", next_action.action),
            ("target", next_action.target),
            ("reason", next_action.reason),
            (
                "open_surface",
                SafeHtml(
                    f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"
                ),
            ),
        ]
    ) + (
        "<p class='muted'>This is read-only operator guidance; it does not "
        "execute approvals, commits, publication handoffs, pushes, PRs, "
        "deploys, provider calls, or external mutations.</p></section>"
    )


def _project_next_action(
    root: Path,
    *,
    open_incidents: list[Any],
    recommendations: list[Any],
    worktree_approvals: list[Any],
    worktree_runs: list[Any],
    commit_approvals: list[Any],
    publications: list[Any],
) -> str:
    if open_incidents:
        return "review_project_incidents"
    if recommendations:
        return "review_task_recommendations"
    if _count_status(publications, "ready_for_operator"):
        return "manual_operator_push_pr_outside_clankeros"
    if _count_status(publications, "approved"):
        return "prepare_publication_handoff"
    if _count_status(publications, "pending_operator_approval"):
        return "approve_or_reject_publication_request"
    if _count_status(commit_approvals, "committed") and not publications:
        return "request_publication_handoff"
    if _count_status(commit_approvals, "approved"):
        return "commit_approved_worktree"
    if _count_status(commit_approvals, "pending_operator_approval"):
        return "approve_or_reject_commit_request"
    reviewed_runs = [
        item
        for item in worktree_runs
        if item.status == "completed"
        and _run_review_gate_state(root, item)["commit_request_form_available"]
    ]
    if reviewed_runs and not commit_approvals:
        return "request_commit_for_reviewed_run"
    if _count_status(worktree_approvals, "pending_operator_approval"):
        return "decide_pending_worktree_approval"
    if _count_status(worktree_approvals, "approved") and not worktree_runs:
        return "run_approved_worktree_from_cli"
    return "review_project_state"


def _task_recommendation_line(item: Any) -> str:
    commands = ", ".join(item.recommended_commands) or "none"
    return (
        f"{_e(item.id)}: status={_e(item.status)} task={_e(item.task_id)} "
        f"type={_e(item.recommendation_type)} reason={_e(item.reason)} "
        f"commands={_e(commands)} evidence={_artifact_link(item.evidence_path)}"
    )


def _delegation_detail(root: Path, delegation_id: str) -> str:
    storage = _storage(root)
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        return "<p class='error'>Delegation not found.</p>"
    summary = summarize_implementation_handoff(root, delegation)
    metadata = load_delegation_result_metadata(delegation)
    run_id = summary.get("run_id") or metadata.get("execution_run_id") or "unknown"
    sections = [
        f"<section><h1>Delegation {_e(delegation.id)}</h1>",
        _kv(
            [
                ("status", delegation.status),
                ("profile", delegation.assigned_profile),
                ("category", delegation.category),
                ("parent_task_id", delegation.parent_task_id),
                ("run_id", str(run_id)),
                ("result_summary", delegation.result_summary or "none"),
            ]
        ),
        "</section>",
        _handoff_block(summary),
        _delegation_workflow_readiness(root, delegation, summary),
        _list_section("Coder Prep", _artifact_links(list_coder_prep_packets(root), delegation_id=delegation_id)),
        _list_section("Coder Worktree Plan", _artifact_links(list_coder_worktree_plan_packets(root), delegation_id=delegation_id)),
        _list_section("Worktree Approvals", [_approval_line(item) for item in list_coder_worktree_approvals(root, delegation_id=delegation_id, limit=20)]),
        _list_section(
            "Worktree Runs",
            [
                _coder_run_line(root, item)
                for item in list_coder_worktree_runs(
                    root,
                    delegation_id=delegation_id,
                    limit=20,
                )
            ],
        ),
        _list_section("Commit Requests / Local Commits", [_commit_line(item) for item in list_coder_worktree_commit_approvals(root, delegation_id=delegation_id, limit=20)]),
        _list_section("Publication Requests / Handoffs", [_publication_line(root, item) for item in list_coder_publications(root, delegation_id=delegation_id, limit=20)]),
        _safe_action_forms(
            delegation_id=delegation_id,
            handoff_md=str(summary["markdown_path"]),
        ),
    ]
    return "".join(sections)


def _run_detail(root: Path, run_id: str) -> str:
    storage = _storage(root)
    run = storage.get_run(run_id) if _row_exists(storage.db_path, "runs", run_id) else None
    coder_runs = [item for item in list_coder_worktree_runs(root, limit=50) if item.id == run_id]
    delegation_run = _delegation_for_execution_run(storage, run_id)
    if run is None and not coder_runs and delegation_run is None:
        return "<p class='error'>Run not found.</p>"
    parts = [f"<section><h1>Run {_e(run_id)}</h1>"]
    if run is not None:
        parts.append(
            _kv(
                [
                    ("goal_id", run.goal_id),
                    ("project_id", run.project_id),
                    ("status", run.status),
                    ("summary_path", run.summary_path or "none"),
                    ("events_path", run.events_path or "none"),
                ]
            )
        )
    for coder_run in coder_runs:
        evidence_path = Path(coder_run.evidence_path)
        review_path = Path("runs") / coder_run.source_run_id / "review.md"
        evidence_links = [
            ("review", str(review_path)),
            ("run_json", str(evidence_path / "run.json")),
            ("diff", str(evidence_path / "diff.patch")),
            ("changed_files", str(evidence_path / "changed_files.json")),
            ("bounded_file_validation", str(evidence_path / "bounded_file_validation.json")),
            ("git_status", str(evidence_path / "git_status.txt")),
            ("stdout", str(evidence_path / "stdout.txt")),
            ("stderr", str(evidence_path / "stderr.txt")),
            ("verification_stdout", str(evidence_path / "verification_stdout.txt")),
            ("verification_stderr", str(evidence_path / "verification_stderr.txt")),
        ]
        parts.append(
            _kv(
                [
                    ("coder_worktree_status", coder_run.status),
                    ("delegation_id", coder_run.delegation_id),
                    ("source_run_id", coder_run.source_run_id),
                    ("worktree_path", coder_run.worktree_path),
                    ("branch_name", coder_run.branch_name),
                    ("changed_files", ", ".join(coder_run.changed_files) or "none"),
                    ("outside_allowed_files", ", ".join(coder_run.outside_allowed_files) or "none"),
                    ("verification_exit_code", str(coder_run.verification_exit_code)),
                    ("evidence_path", coder_run.evidence_path),
                ]
            )
        )
        parts.append(_run_command_bar(root, coder_run))
        parts.append(_run_workflow_state(root, coder_run))
        parts.append(_run_review_gate(root, coder_run))
        parts.append(
            _list_section(
                "Coder Worktree Evidence",
                [
                    f"{_e(label)}: {_artifact_link(path)}"
                    for label, path in evidence_links
                    if (root / path).exists()
                ],
                anchor_id="coder-worktree-evidence",
            )
        )
        parts.append(_run_action_forms(root, coder_run.id))
    if delegation_run is not None:
        delegation, metadata = delegation_run
        parts.append(_delegation_execution_run_detail(root, storage, delegation, metadata, run_id))
    parts.append("</section>")
    return "".join(parts)


def _delegation_for_execution_run(
    storage: Storage,
    run_id: str,
) -> tuple[Any, dict[str, Any]] | None:
    for delegation in storage.list_recent_subagent_delegations(limit=None):
        metadata = load_delegation_result_metadata(delegation)
        metadata_run_id = metadata.get("execution_run_id") or metadata.get("run_id")
        if metadata_run_id == run_id:
            return delegation, metadata
    return None


def _delegation_execution_run_detail(
    root: Path,
    storage: Storage,
    delegation: Any,
    metadata: dict[str, Any],
    run_id: str,
) -> str:
    summary = summarize_implementation_handoff(root, delegation)
    project_id = str(metadata.get("target_project_id") or _task_project(storage, delegation.parent_task_id))
    evidence_dir = str(metadata.get("execution_evidence_dir") or metadata.get("evidence_dir") or "none")
    next_action = _delegation_run_next_action(delegation, metadata)
    context_pack_status = "available" if (
        metadata.get("context_pack_json") or metadata.get("context_pack_md")
    ) else "missing"
    implementation_handoff_status = "available" if (
        metadata.get("implementation_handoff_json") or metadata.get("implementation_handoff_md")
    ) else "missing"
    retry_candidate = str(
        delegation.status != "completed" or bool(metadata.get("incident_id"))
    ).lower()
    return "".join(
        [
            "<section><h2>Delegation Run Evidence</h2>",
            _kv(
                [
                    ("delegation_id", SafeHtml(f"<a href='/delegations/{quote(delegation.id)}'>{_e(delegation.id)}</a>")),
                    ("run_id", run_id),
                    ("status", delegation.status),
                    ("project_id", project_id),
                    ("profile", delegation.assigned_profile),
                    ("category", delegation.category),
                    ("parent_task_id", delegation.parent_task_id),
                    ("result_summary", delegation.result_summary or "none"),
                    ("evidence_dir", evidence_dir),
                    ("provider_calls_taken_by_clankeros", str(metadata.get("provider_calls_taken_by_clankeros", "unknown"))),
                    ("network_actions_taken", str(metadata.get("network_actions_taken", "unknown"))),
                    ("external_mutations_taken", str(metadata.get("external_mutations_taken", "unknown"))),
                    ("incident", str(metadata.get("incident_id") or "none")),
                    ("retry_candidate", retry_candidate),
                    ("next_recommended_action", next_action),
                ]
            ),
            "</section>",
            _list_section(
                "Delegation Execution Artifacts",
                _delegation_execution_artifact_lines(root, delegation, metadata),
            ),
            "<section><h2>Delegation Run Workflow State</h2>",
            _kv(
                [
                    ("context_pack_status", context_pack_status),
                    ("context_pack", _artifact_link(str(metadata.get("context_pack_md") or metadata.get("context_pack_json") or "none"))),
                    ("implementation_handoff_status", implementation_handoff_status),
                    ("implementation_handoff", _artifact_link(str(metadata.get("implementation_handoff_md") or metadata.get("implementation_handoff_json") or "none"))),
                    ("implementation_handoff_readback", str(summary["status"])),
                    ("coder_prep_status", _delegation_packet_status(list_coder_prep_packets(root), delegation.id)),
                    ("coder_worktree_plan_status", _delegation_packet_status(list_coder_worktree_plan_packets(root), delegation.id)),
                    ("next_recommended_action", next_action),
                ]
            ),
            "</section>",
        ]
    )


def _delegation_execution_artifact_lines(
    root: Path,
    delegation: Any,
    metadata: dict[str, Any],
) -> list[str]:
    artifacts: list[tuple[str, str]] = [
        ("result_artifact", _repo_relative_artifact_path(root, delegation.result_artifact_path)),
        ("context_pack_json", str(metadata.get("context_pack_json") or "none")),
        ("context_pack_md", str(metadata.get("context_pack_md") or "none")),
        ("implementation_handoff_json", str(metadata.get("implementation_handoff_json") or "none")),
        ("implementation_handoff_md", str(metadata.get("implementation_handoff_md") or "none")),
    ]
    evidence_dir = metadata.get("execution_evidence_dir") or metadata.get("evidence_dir")
    if evidence_dir:
        for filename in [
            "input.json",
            "prompt.md",
            "stdout.txt",
            "stderr.txt",
            "raw_output.txt",
            "parsed_output.json",
            "validation.json",
            "result.json",
            "project.json",
            "repo_files.json",
            "context_pack_metadata.json",
        ]:
            artifacts.append((filename, str(Path(str(evidence_dir)) / filename)))
    lines = []
    seen: set[str] = set()
    for label, path in artifacts:
        if not path or path == "none" or path in seen:
            continue
        seen.add(path)
        if (root / path).exists():
            lines.append(f"{_e(label)}: {_artifact_link(path)}")
    return lines


def _delegation_packet_status(packets: list[dict[str, Any]], delegation_id: str) -> str:
    return "available" if any(
        packet.get("source", {}).get("delegation_id") == delegation_id
        for packet in packets
    ) else "missing"


def _run_command_bar(root: Path, coder_run: Any) -> str:
    commit_approvals = [
        item
        for item in list_coder_worktree_commit_approvals(root, limit=50)
        if item.run_id == coder_run.id
    ]
    publications = [
        item
        for item in list_coder_publications(root, limit=50)
        if item.run_id == coder_run.id
    ]
    review_gate = _run_review_gate_state(root, coder_run)
    change_summary = coder_worktree_change_summary(root, coder_run)
    next_action, target_href, target_label, reason = _run_command_next_action(
        coder_run,
        review_gate=review_gate,
        commit_approvals=commit_approvals,
        publications=publications,
    )
    target = SafeHtml(f"<a href='{_e(target_href)}'>{_e(target_label)}</a>")
    lines = [
        f"run_command_now: {_e(next_action)}",
        f"run_command_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
        f"run_command_reason: {_e(reason)}",
        "run_command_safety: read-only run guidance",
    ]
    return "".join(
        [
            "<section class='panel run-command-bar' data-run-command-bar='true'><h2>Run Command Bar</h2>",
            "<p class='muted'>One read-only summary of the run gate, evidence posture, and next local operator action before the detailed evidence and forms.</p>",
            _kv(
                [
                    ("run_command_status", "available"),
                    ("run_command_run_id", coder_run.id),
                    ("run_command_project", coder_run.project_id),
                    ("run_command_delegation", SafeHtml(f"<a href='/delegations/{quote(coder_run.delegation_id)}'>{_e(coder_run.delegation_id)}</a>")),
                    ("run_command_worktree_status", coder_run.status),
                    ("run_command_review_status", str(review_gate["status"])),
                    ("run_command_review_path", SafeHtml(_artifact_link(str(review_gate["review_path"]))) if review_gate["exists"] else str(review_gate["review_path"])),
                    ("run_command_commit_request_status", _status_counts(commit_approvals)),
                    ("run_command_publication_status", _status_counts(publications)),
                    ("run_command_changed_files_count", change_summary["changed_files_count"]),
                    ("run_command_diff_summary", change_summary["diff_summary"]),
                    ("run_command_next_action", next_action),
                    ("run_command_target_surface", target),
                    ("run_command_reason", reason),
                    ("run_command_write_on_get", "false"),
                    ("run_command_network_actions_taken", "0"),
                    ("run_command_external_effects_created", "false"),
                    ("run_command_push_created", "false"),
                    ("run_command_pr_created", "false"),
                    ("run_command_deploy_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _run_command_next_action(
    coder_run: Any,
    *,
    review_gate: dict[str, Any],
    commit_approvals: list[Any],
    publications: list[Any],
) -> tuple[str, str, str, str]:
    pending_commit = next(
        (item for item in commit_approvals if item.status == "pending_operator_approval"),
        None,
    )
    approved_commit = next(
        (item for item in commit_approvals if item.status == "approved"),
        None,
    )
    committed = next(
        (item for item in commit_approvals if item.status == "committed"),
        None,
    )
    pending_publication = next(
        (item for item in publications if item.status == "pending_operator_approval"),
        None,
    )
    approved_publication = next(
        (item for item in publications if item.status == "approved"),
        None,
    )
    ready_publication = next(
        (item for item in publications if item.status == "ready_for_operator"),
        None,
    )
    if not commit_approvals:
        if review_gate["commit_request_form_available"]:
            return (
                "Create commit request",
                "#run-approval-actions",
                "Run approval actions",
                "reviewed coder run is ready for a local commit request",
            )
        return (
            "Review run",
            "#run-review-gate",
            "Run Review Gate",
            str(review_gate["blocked_reason"]),
        )
    if pending_commit is not None:
        return (
            "Review commit approval",
            "/approvals",
            "/approvals",
            f"commit approval {pending_commit.id} is pending",
        )
    if approved_commit is not None:
        return (
            "Commit approved worktree",
            "#confirmed-local-commit-action",
            "Confirmed Local Commit Action",
            f"commit approval {approved_commit.id} is approved",
        )
    if committed is not None and not publications:
        return (
            "Create publication request",
            "#run-approval-actions",
            "Run approval actions",
            "local commit exists and needs a publication request",
        )
    if pending_publication is not None:
        return (
            "Review publication approval",
            "/approvals",
            "/approvals",
            f"publication approval {pending_publication.id} is pending",
        )
    if approved_publication is not None:
        return (
            "Create publication handoff",
            "#publication-handoff-action",
            "Publication Handoff Action",
            f"publication approval {approved_publication.id} is approved",
        )
    if ready_publication is not None:
        return (
            "Use publication handoff manually",
            "#publication-handoff-commands",
            "Publication Handoff Commands",
            "manual push/PR boundary is ready outside ClankerOS",
        )
    return (
        "Review run evidence",
        "#coder-worktree-evidence",
        "Coder Worktree Evidence",
        f"run status={coder_run.status}",
    )


def _run_workflow_state(root: Path, coder_run: Any) -> str:
    storage = _storage(root)
    delegation = storage.get_subagent_delegation(coder_run.delegation_id)
    if delegation is None:
        return "<section id='run-workflow-state'><h2>Run Workflow State</h2>" + _kv(
            [
                ("selection_status", "delegation_not_found"),
                ("delegation_id", coder_run.delegation_id),
                ("run_id", coder_run.id),
            ]
        ) + "</section>"

    summary = summarize_implementation_handoff(root, delegation)
    prep_packets = [
        item
        for item in list_coder_prep_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    plan_packets = [
        item
        for item in list_coder_worktree_plan_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    worktree_approvals = list_coder_worktree_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    worktree_runs = list_coder_worktree_runs(root, delegation_id=delegation.id, limit=50)
    commit_approvals = list_coder_worktree_commit_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    publications = list_coder_publications(root, delegation_id=delegation.id, limit=50)
    bounded_status = _artifact_status(
        root,
        Path(coder_run.evidence_path) / "bounded_file_validation.json",
    )
    verification_status = (
        "passed"
        if coder_run.verification_exit_code == 0
        else "failed"
        if coder_run.verification_exit_code is not None
        else "not_run"
    )
    ready_publications = [
        item for item in publications if item.status == "ready_for_operator"
    ]
    return "<section id='run-workflow-state'><h2>Run Workflow State</h2>" + _non_claim_banner() + _kv(
        [
            ("delegation_id", coder_run.delegation_id),
            ("run_id", coder_run.id),
            ("context_pack_status", _artifact_status(root, summary["context_pack_json"])),
            ("context_pack_path", _artifact_link(summary["context_pack_json"])),
            ("implementation_handoff_status", str(summary["status"])),
            ("implementation_handoff_path", _artifact_link(summary["markdown_path"])),
            ("coder_prep_status", "available" if prep_packets else "missing"),
            ("coder_worktree_plan_status", "available" if plan_packets else "missing"),
            ("worktree_approval_status", _status_counts(worktree_approvals)),
            ("worktree_run_status", coder_run.status),
            ("bounded_file_validation_status", bounded_status),
            ("changed_files", ", ".join(coder_run.changed_files) or "none"),
            ("outside_allowed_files", ", ".join(coder_run.outside_allowed_files) or "none"),
            ("verification_status", verification_status),
            ("verification_exit_code", str(coder_run.verification_exit_code)),
            ("commit_request_status", _status_counts(commit_approvals)),
            ("commit_approval_status", _status_counts(commit_approvals)),
            (
                "commit_sha",
                next(
                    (item.commit_sha for item in commit_approvals if item.commit_sha),
                    "none",
                ),
            ),
            ("publication_request_status", _status_counts(publications)),
            ("publication_approval_status", _status_counts(publications)),
            (
                "publication_handoff_status",
                "available" if ready_publications else "missing",
            ),
            (
                "next_recommended_action",
                _delegation_next_action(
                    root,
                    summary=summary,
                    prep_count=len(prep_packets),
                    plan_count=len(plan_packets),
                    worktree_approvals=worktree_approvals,
                    worktree_runs=worktree_runs,
                    commit_approvals=commit_approvals,
                    publications=publications,
                ),
            ),
        ]
    ) + "</section>"


def _run_review_gate(root: Path, coder_run: Any) -> str:
    state = _run_review_gate_state(root, coder_run)
    rows: list[tuple[str, str | SafeHtml]] = [
        ("review_gate_status", state["status"]),
        ("review_path", _artifact_link(state["review_path"]) if state["exists"] else state["review_path"]),
        ("review_file_exists", str(state["exists"]).lower()),
        ("review_mentions_run", str(state["mentions_run"]).lower()),
        ("commit_request_form_available", str(state["commit_request_form_available"]).lower()),
        ("blocked_reason", state["blocked_reason"]),
        ("backend_rule", "review.md must mention the coder worktree run id before coder-commit-request"),
        ("network_actions_taken", "0"),
        ("external_mutations_taken", "0"),
    ]
    return "".join(
        [
            "<section id='run-review-gate'><h2>Run Review Gate</h2>",
            "<p class='muted'>This readback mirrors the existing commit-request backend gate before the app offers a local commit request form.</p>",
            _kv(rows),
            "</section>",
        ]
    )


def _run_review_gate_state(root: Path, coder_run: Any) -> dict[str, Any]:
    review_path = Path("runs") / coder_run.source_run_id / "review.md"
    absolute_review_path = root / review_path
    exists = absolute_review_path.is_file()
    mentions_run = False
    if exists:
        try:
            mentions_run = coder_run.id in absolute_review_path.read_text(encoding="utf-8")
        except OSError:
            mentions_run = False
    commit_request_form_available = (
        coder_run.status == "completed" and exists and mentions_run
    )
    if commit_request_form_available:
        status = "reviewed"
        blocked_reason = "none"
    elif not exists:
        status = "missing"
        blocked_reason = "review_artifact_missing"
    elif not mentions_run:
        status = "stale_or_unmatched"
        blocked_reason = "review_artifact_does_not_mention_run"
    else:
        status = "not_ready"
        blocked_reason = f"coder_worktree_status_{coder_run.status}"
    return {
        "review_path": review_path.as_posix(),
        "exists": exists,
        "mentions_run": mentions_run,
        "status": status,
        "blocked_reason": blocked_reason,
        "commit_request_form_available": commit_request_form_available,
    }


def _artifact_viewer(
    root: Path,
    relative_path: str | None,
    *,
    current_path: str = "/artifacts",
) -> LocalAppResponse:
    if not relative_path:
        return _html_page(root, "Artifact", "<p class='error'>Missing path.</p>", status=400, current_path=current_path)
    try:
        path = resolve_artifact_path(root, relative_path)
    except ValueError as error:
        return _html_page(root, "Artifact Rejected", f"<p class='error'>{_e(str(error))}</p>", status=400, current_path=current_path)
    if not path.exists() or not path.is_file():
        return _html_page(root, "Artifact Missing", "<p class='error'>Artifact file not found.</p>", status=404, current_path=current_path)
    size = path.stat().st_size
    data = path.read_bytes()[:MAX_ARTIFACT_BYTES]
    truncated = size > MAX_ARTIFACT_BYTES
    text = data.decode("utf-8", errors="replace")
    if path.suffix == ".json":
        try:
            text = json.dumps(json.loads(text), indent=2, sort_keys=True)
        except json.JSONDecodeError:
            pass
    artifact_type = _artifact_type(path)
    render_family = _artifact_render_family(path)
    renderer = _artifact_renderer_name(path)
    repo_relative = path.relative_to(root).as_posix()
    line_count = len(text.splitlines())
    workspace = _load_workspace_state(root)
    body = "".join(
        [
            _artifact_command_bar(
                root,
                relative_path=repo_relative,
                artifact_type=artifact_type,
                render_family=render_family,
                renderer=renderer,
                size=size,
                rendered_bytes=len(data),
                line_count=line_count,
                truncated=truncated,
                workspace=workspace,
            ),
            _artifact_review_brief(
                relative_path=repo_relative,
                artifact_type=artifact_type,
                render_family=render_family,
                renderer=renderer,
                line_count=line_count,
                truncated=truncated,
                workspace=workspace,
            ),
            f"<section id='artifact-content'><h1>Artifact {_e(repo_relative)}</h1>",
            _kv(
                [
                    ("artifact_type", artifact_type),
                    ("artifact_render_family", render_family),
                    ("artifact_renderer", renderer),
                    ("artifact_raw_filesystem_browsing", "false"),
                    ("artifact_content_executed", "false"),
                    ("size_bytes", str(size)),
                    ("rendered_bytes", str(len(data))),
                    ("line_count", str(line_count)),
                    ("truncated", str(truncated).lower()),
                ]
            ),
            _render_artifact_content(text, render_family, renderer),
            "<p class='muted'>Artifact content is rendered as inert text and is never executed.</p>",
            "</section>",
            _remember_artifact_section(root, relative_path, current_path),
        ]
    )
    return _html_page(root, "Artifact", body, current_path=current_path)


def _artifact_review_brief(
    *,
    relative_path: str,
    artifact_type: str,
    render_family: str,
    renderer: str,
    line_count: int,
    truncated: bool,
    workspace: dict[str, str],
) -> str:
    context = _artifact_context_from_path(relative_path)
    project_id = context["project_id"]
    goal_id = context["goal_id"]
    remembered = workspace.get("last_viewed_artifact") == relative_path
    if goal_id != "unknown":
        review_status = "goal_scoped"
        primary_action = "Return to goal"
        primary_href = f"/goals/{quote(goal_id)}"
        primary_label = f"/goals/{goal_id}"
        secondary_href = f"/projects/{quote(project_id)}"
        secondary_label = f"/projects/{project_id}"
        reason = "artifact_path_identifies_goal_context"
    elif remembered:
        review_status = "saved_resume_anchor"
        primary_action = "Resume from artifact"
        primary_href = "/resume"
        primary_label = "/resume"
        secondary_href = "/workspace"
        secondary_label = "/workspace"
        reason = "artifact_saved_as_workspace_anchor"
    elif context["source"] == "delegation_path":
        review_status = "delegation_scoped"
        primary_action = "Review delegation runs"
        primary_href = "/delegation-runs"
        primary_label = "/delegation-runs"
        secondary_href = "#remember-artifact"
        secondary_label = "Remember Artifact"
        reason = "artifact_path_identifies_delegation_context"
    else:
        review_status = "unclassified"
        primary_action = "Remember artifact"
        primary_href = "#remember-artifact"
        primary_label = "Remember Artifact"
        secondary_href = "/workspace"
        secondary_label = "/workspace"
        reason = "artifact_path_unclassified"
    project_value: str | SafeHtml = project_id
    if project_id != "unknown":
        project_value = SafeHtml(f"<a href='/projects/{quote(project_id)}'>{_e(project_id)}</a>")
    goal_value: str | SafeHtml = goal_id
    if goal_id != "unknown":
        goal_value = SafeHtml(f"<a href='/goals/{quote(goal_id)}'>{_e(goal_id)}</a>")
    return "".join(
        [
            "<section id='artifact-review-brief' class='panel artifact-review-brief' data-artifact-review-brief='true'><h2>Artifact Review Brief</h2>",
            "<p class='muted'>A read-only review card that connects this bounded artifact back to the local operator workflow before the inert content view.</p>",
            _kv(
                [
                    ("artifact_review_status", review_status),
                    ("artifact_review_path", relative_path),
                    ("artifact_review_project", project_value),
                    ("artifact_review_goal", goal_value),
                    ("artifact_review_context_source", context["source"]),
                    ("artifact_review_type", artifact_type),
                    ("artifact_review_render_family", render_family),
                    ("artifact_review_renderer", renderer),
                    ("artifact_review_line_count", str(line_count)),
                    ("artifact_review_truncated", str(truncated).lower()),
                    ("artifact_review_saved_workspace_project", workspace.get("open_project", "")),
                    ("artifact_review_saved_workspace_goal", workspace.get("open_goal", "")),
                    ("artifact_review_already_remembered", str(remembered).lower()),
                    ("artifact_review_primary_action", primary_action),
                    (
                        "artifact_review_primary_surface",
                        SafeHtml(f"<a href='{_e(primary_href)}'>{_e(primary_label)}</a>"),
                    ),
                    (
                        "artifact_review_secondary_surface",
                        SafeHtml(f"<a href='{_e(secondary_href)}'>{_e(secondary_label)}</a>"),
                    ),
                    ("artifact_review_reason", reason),
                    ("artifact_review_write_on_get", "false"),
                    ("artifact_review_raw_filesystem_browsing", "false"),
                    ("artifact_review_content_executed", "false"),
                    ("artifact_review_provider_calls_taken_by_clankeros", "0"),
                    ("artifact_review_network_actions_taken", "0"),
                    ("artifact_review_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"artifact_review_now: {_e(primary_action)}",
                    f"artifact_review_click: <a href='{_e(primary_href)}'>{_e(primary_label)}</a>",
                    f"artifact_review_reason: {_e(reason)}",
                    "artifact_review_safety: bounded inert read-only review",
                ]
            ),
            "</section>",
        ]
    )


def _artifact_command_bar(
    root: Path,
    *,
    relative_path: str,
    artifact_type: str,
    render_family: str,
    renderer: str,
    size: int,
    rendered_bytes: int,
    line_count: int,
    truncated: bool,
    workspace: dict[str, str],
) -> str:
    context = _artifact_context_from_path(relative_path)
    remembered = workspace.get("last_viewed_artifact") == relative_path
    if remembered:
        next_action = "Resume from artifact"
        target_href = "/resume"
        target_label = "/resume"
        reason = "artifact_is_saved_workspace_anchor"
    else:
        next_action = "Remember artifact"
        target_href = "#remember-artifact"
        target_label = "Remember Artifact"
        reason = "artifact_not_saved_as_resume_anchor"
    goal_value: str | SafeHtml = context["goal_id"]
    if context["goal_id"] != "unknown":
        goal_value = SafeHtml(
            f"<a href='/goals/{quote(context['goal_id'])}'>{_e(context['goal_id'])}</a>"
        )
    project_value: str | SafeHtml = context["project_id"]
    if context["project_id"] != "unknown":
        project_value = SafeHtml(
            f"<a href='/projects/{quote(context['project_id'])}'>{_e(context['project_id'])}</a>"
        )
    return "".join(
        [
            "<section id='artifact-command-bar' class='panel artifact-command-bar' data-artifact-command-bar='true'><h2>Artifact Command Bar</h2>",
            _kv(
                [
                    ("artifact_command_status", "ready"),
                    ("artifact_command_path", relative_path),
                    ("artifact_command_type", artifact_type),
                    ("artifact_command_render_family", render_family),
                    ("artifact_command_renderer", renderer),
                    ("artifact_command_size_bytes", str(size)),
                    ("artifact_command_rendered_bytes", str(rendered_bytes)),
                    ("artifact_command_line_count", str(line_count)),
                    ("artifact_command_truncated", str(truncated).lower()),
                    ("artifact_command_project", project_value),
                    ("artifact_command_goal", goal_value),
                    ("artifact_command_context_source", context["source"]),
                    ("artifact_command_workspace_project", workspace.get("open_project", "")),
                    ("artifact_command_workspace_goal", workspace.get("open_goal", "")),
                    ("artifact_command_already_remembered", str(remembered).lower()),
                    ("artifact_command_next_action", next_action),
                    (
                        "artifact_command_target_surface",
                        SafeHtml(
                            f"<a href='{_e(target_href)}'>{_e(target_label)}</a>"
                        ),
                    ),
                    ("artifact_command_reason", reason),
                    ("artifact_command_write_on_get", "false"),
                    ("artifact_command_raw_filesystem_browsing", "false"),
                    ("artifact_command_content_executed", "false"),
                    ("artifact_command_network_actions_taken", "0"),
                    ("artifact_command_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"artifact_command_now: {_e(next_action)}",
                    f"artifact_command_click: <a href='{_e(target_href)}'>{_e(target_label)}</a>",
                    f"artifact_command_reason: {_e(reason)}",
                    "artifact_command_safety: bounded inert artifact read",
                ]
            ),
            "</section>",
        ]
    )


def _artifact_context_from_path(relative_path: str) -> dict[str, str]:
    parts = Path(relative_path).parts
    for index, part in enumerate(parts):
        if (
            part == "projects"
            and index + 3 < len(parts)
            and parts[index + 2] == "goals"
        ):
            return {
                "project_id": parts[index + 1],
                "goal_id": parts[index + 3],
                "source": "project_goal_path",
            }
    if len(parts) >= 3 and parts[0] == ".clanker" and parts[1] == "delegations":
        return {
            "project_id": "unknown",
            "goal_id": "unknown",
            "source": "delegation_path",
        }
    return {
        "project_id": "unknown",
        "goal_id": "unknown",
        "source": "path_unclassified",
    }


def _remember_artifact_section(root: Path, relative_path: str, current_path: str) -> str:
    workspace = _load_workspace_state(root)
    return "".join(
        [
            "<section id='remember-artifact'><h2>Remember Artifact</h2>",
            "<p class='muted'>Store this artifact as the local resume anchor for the next ClankerOS session. The viewer does not write on page load.</p>",
            _kv(
                [
                    ("remember_artifact_form_available", "true"),
                    ("remember_artifact_path", relative_path),
                    ("remember_artifact_get_writes", "false"),
                    ("remember_artifact_external_effects_created", "false"),
                ]
            ),
            _input_form(
                "save-workspace",
                {"return_to": current_path},
                {
                    "open_project": workspace.get("open_project", ""),
                    "open_goal": workspace.get("open_goal", ""),
                    "filters": f"artifact:{relative_path}",
                    "expanded_panels": workspace.get("expanded_panels", "") or "artifacts",
                    "last_viewed_artifact": relative_path,
                    "updated_by": "operator-artifact",
                },
            ),
            "</section>",
        ]
    )


def resolve_artifact_path(root: Path, relative_path: str) -> Path:
    root = root.resolve()
    raw = unquote(relative_path).strip()
    path = Path(raw)
    if not raw:
        raise ValueError("artifact path is required")
    if path.is_absolute():
        raise ValueError("absolute artifact paths are rejected")
    if ".." in path.parts:
        raise ValueError("parent traversal is rejected")
    resolved = (root / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError("artifact path resolves outside repo root") from error
    if resolved.suffix not in {".md", ".json", ".txt", ".patch", ".diff", ".log"}:
        raise ValueError("artifact file type is not supported")
    return resolved


def _artifact_type(path: Path) -> str:
    return {
        ".md": "markdown",
        ".json": "json",
        ".txt": "text",
        ".patch": "patch",
        ".diff": "diff",
        ".log": "log",
    }.get(path.suffix, "unknown")


def _artifact_render_family(path: Path) -> str:
    if path.suffix == ".md":
        return "markdown"
    if path.suffix == ".json":
        return "json"
    if path.suffix in {".patch", ".diff"}:
        return "patch"
    return "text"


def _artifact_renderer_name(path: Path) -> str:
    family = _artifact_render_family(path)
    if family == "markdown":
        return "markdown_safe_html"
    if family == "json":
        return "json_pretty_pre"
    if family == "patch":
        return "patch_line_view"
    return "text_pre"


def _render_artifact_content(text: str, render_family: str, renderer: str) -> str:
    if render_family == "markdown":
        return _render_markdown_artifact(text, renderer)
    if render_family == "patch":
        return _render_patch_artifact(text, renderer)
    class_name = "artifact-json" if render_family == "json" else "artifact-text"
    return (
        f"<div class='artifact-render-shell' data-artifact-renderer='{_e(renderer)}'>"
        f"<pre class='{class_name}'>{_e(text)}</pre>"
        "</div>"
    )


def _render_markdown_artifact(text: str, renderer: str) -> str:
    parts = [
        f"<div class='artifact-render-shell artifact-markdown' data-artifact-renderer='{_e(renderer)}'>"
    ]
    in_list = False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if in_list:
                parts.append("</ul>")
                in_list = False
            continue
        if stripped.startswith("- "):
            if not in_list:
                parts.append("<ul class='artifact-markdown-list'>")
                in_list = True
            parts.append(f"<li>{_e(stripped[2:].strip())}</li>")
            continue
        if in_list:
            parts.append("</ul>")
            in_list = False
        heading_level = len(stripped) - len(stripped.lstrip("#"))
        if (
            1 <= heading_level <= 6
            and stripped[heading_level:heading_level + 1] == " "
        ):
            tag = "h2" if heading_level == 1 else "h3"
            parts.append(
                f"<{tag} class='artifact-markdown-heading'>{_e(stripped[heading_level:].strip())}</{tag}>"
            )
        else:
            parts.append(f"<p>{_e(stripped)}</p>")
    if in_list:
        parts.append("</ul>")
    parts.append("</div>")
    return "".join(parts)


def _render_patch_artifact(text: str, renderer: str) -> str:
    lines = [
        f"<div class='artifact-render-shell' data-artifact-renderer='{_e(renderer)}'>",
        "<pre class='artifact-patch'>",
    ]
    for line in text.splitlines():
        class_name = "artifact-patch-line"
        if line.startswith("+") and not line.startswith("+++"):
            class_name += " artifact-patch-add"
        elif line.startswith("-") and not line.startswith("---"):
            class_name += " artifact-patch-delete"
        elif line.startswith("@@"):
            class_name += " artifact-patch-hunk"
        elif (
            line.startswith("diff ")
            or line.startswith("index ")
            or line.startswith("---")
            or line.startswith("+++")
        ):
            class_name += " artifact-patch-meta"
        lines.append(f"<span class='{class_name}'>{_e(line)}</span>")
    lines.extend(["</pre>", "</div>"])
    return "".join(lines)


def _health(root: Path, *, host: str, port: int) -> str:
    status_path = write_local_app_status(root, host=host, port=port)
    storage = _storage(root)
    counts = _counts(storage.db_path)
    state = _repo_state(root)
    warnings = _warning_items(state, host)
    imports = _workflow_import_status()
    return "".join(
        [
            "<section><h1>System Health</h1>",
            _warnings(warnings),
            _kv(
                [
                    ("python", sys.version.split()[0]),
                    ("repo_root", str(root)),
                    ("branch", state["branch"]),
                    ("commit", state["commit"]),
                    ("worktree_dirty", str(bool(state["dirty_tracked_files"]))),
                    ("untracked_files", ", ".join(state["untracked_files"]) or "none"),
                    ("sqlite_database", str(storage.db_path)),
                    ("storage_initializes", "true"),
                    ("status_artifact", str(status_path.relative_to(root))),
                    ("bind", f"{host}:{port}"),
                ]
            ),
            _list_section("Counts", [f"{key}: {value}" for key, value in counts.items()]),
            _list_section("Key Commands Registered", _key_commands()),
            _list_section("Workflow Imports", [f"{key}: {value}" for key, value in imports.items()]),
            _non_claim_banner(),
            "</section>",
        ]
    )


def _demo_page(root: Path) -> str:
    return "".join(
        [
            "<section><h1>Demo Scenario</h1>",
            "<p>Use the fixture-backed demo to populate this local app without providers, pushes, PRs, deploys, or external projects.</p>",
            "<pre>python3 -m agent_os.cli demo-app-scenario</pre>",
            "<p>The command creates or reuses a demo project under <code>.clanker/demo/local-app-project</code>, writes context-pack and implementation-handoff fixture artifacts, prepares coder prep and worktree-plan packets, and leaves a pending worktree approval request.</p>",
            _non_claim_banner(),
            "</section>",
            _demo_dogfooding_state(root),
        ]
    )


def _demo_dogfooding_state(root: Path) -> str:
    storage = _storage(root)
    project = storage.get_registered_project("local-app-demo")
    if project is None:
        return "".join(
            [
                "<section><h2>Demo Dogfooding Links</h2>",
                "<p class='muted'>Run <code>python3 -m agent_os.cli demo-app-scenario</code> to create fixture state and unlock direct demo links.</p>",
                "</section>",
                _manual_browser_script(None),
            ]
        )

    delegations = [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if _task_project(storage, delegation.parent_task_id) == project.name
    ]
    selected_delegation = delegations[0] if delegations else None
    selected_run = None
    if selected_delegation is not None:
        runs = list_coder_worktree_runs(
            root,
            delegation_id=selected_delegation.id,
            limit=20,
        )
        selected_run = next((run for run in runs if run.status == "completed"), None)
        if selected_run is None and runs:
            selected_run = runs[0]

    links = [f"<a href='/projects/{quote(project.name)}'>Project: {_e(project.name)}</a>"]
    artifact_lines: list[str] = []
    approval_lines: list[str] = []
    review_path = "none"

    if selected_delegation is not None:
        summary = summarize_implementation_handoff(root, selected_delegation)
        links.extend(
            [
                f"<a href='/delegations/{quote(selected_delegation.id)}'>Delegation: {_e(selected_delegation.id)}</a>",
                f"<a href='/workflow?delegation_id={quote(selected_delegation.id)}'>Workflow scoped to delegation</a>",
            ]
        )
        artifact_lines.extend(
            [
                f"implementation_handoff: {_artifact_link(str(summary['markdown_path']))}",
                f"context_pack: {_artifact_link(str(summary['context_pack_json']))}",
            ]
        )
        prep_packets = [
            item
            for item in list_coder_prep_packets(root)
            if item.get("source", {}).get("delegation_id") == selected_delegation.id
        ]
        plan_packets = [
            item
            for item in list_coder_worktree_plan_packets(root)
            if item.get("source", {}).get("delegation_id") == selected_delegation.id
        ]
        artifact_lines.extend(_artifact_links(prep_packets, delegation_id=selected_delegation.id))
        artifact_lines.extend(_artifact_links(plan_packets, delegation_id=selected_delegation.id))
        approval_lines.extend(
            _approval_line(item)
            for item in list_coder_worktree_approvals(
                root,
                delegation_id=selected_delegation.id,
                status="pending_operator_approval",
                limit=20,
            )
        )

    if selected_run is not None:
        links.extend(
            [
                f"<a href='/runs/{quote(selected_run.id)}'>Coder worktree run: {_e(selected_run.id)}</a>",
                f"<a href='/workflow?run_id={quote(selected_run.id)}'>Workflow scoped to run</a>",
            ]
        )
        candidate_review = root / "runs" / selected_run.source_run_id / "review.md"
        if candidate_review.exists():
            review_path = candidate_review.relative_to(root).as_posix()
            artifact_lines.append(f"review: {_artifact_link(review_path)}")
        artifact_lines.extend(
            [
                f"diff: {_artifact_link(str(Path(selected_run.evidence_path) / 'diff.patch'))}",
                f"changed_files: {_artifact_link(str(Path(selected_run.evidence_path) / 'changed_files.json'))}",
                f"bounded_file_validation: {_artifact_link(str(Path(selected_run.evidence_path) / 'bounded_file_validation.json'))}",
            ]
        )

    links.extend(
        [
            "<a href='/approvals'>Approvals</a>",
            "<a href='/inbox'>Inbox</a>",
            "<a href='/health'>Health</a>",
        ]
    )

    state = [
        ("project_id", project.name),
        ("delegation_id", selected_delegation.id if selected_delegation else "none"),
        ("coder_worktree_run_id", selected_run.id if selected_run else "none"),
        ("review_path", _artifact_link(review_path)),
        ("fixture_backed", "true"),
        ("network_actions_taken", "0"),
        ("external_mutations_taken", "0"),
    ]
    return "".join(
        [
            "<section><h2>Demo Dogfooding Links</h2>",
            "<p class='muted'>These links are read from current local fixture state. They do not create state or execute actions.</p>",
            _kv(state),
            _ul(links),
            "</section>",
            _list_section("Demo Artifacts", artifact_lines),
            _list_section("Pending Demo Approvals", approval_lines, "/approvals"),
            _demo_next_action_panel(root, selected_run.id if selected_run else ""),
            _demo_browser_progress(root, selected_run.id if selected_run else ""),
            _demo_gate_artifacts(root, selected_run.id if selected_run else ""),
            _demo_gate_actions(root, selected_run.id if selected_run else ""),
            _manual_browser_script(
                {
                    "project_id": project.name,
                    "goal_id": selected_delegation.parent_goal_id if selected_delegation else "",
                    "delegation_id": selected_delegation.id if selected_delegation else "",
                    "run_id": selected_run.id if selected_run else "",
                    "review_path": review_path,
                }
            ),
        ]
    )


def _demo_browser_progress(root: Path, run_id: str) -> str:
    progress = _demo_progress_state(root, run_id)
    if not run_id:
        return _list_section(
            "Demo Browser Progress",
            [
                "selected_run_status: missing",
                f"next_operator_step: {_e(progress['next_step'])}",
                "network_actions_taken: 0",
                "external_mutations_taken: 0",
            ],
        )
    lines = [
        f"selected_run_id: {_e(run_id)}",
        f"goal_completion_status: {_e(progress['goal_status'])}",
        f"commit_request_status: {_e(progress['commit_status'])}",
        f"commit_approval_status: {_e(progress['commit_status'])}",
        f"local_commit_status: {_e(progress['local_commit_status'])}",
        f"publication_request_status: {_e(progress['publication_status'])}",
        f"publication_approval_status: {_e(progress['publication_status'])}",
        f"publication_handoff_status: {_e(progress['publication_handoff_status'])}",
        f"manual_push_pr_status: {_e(progress['manual_status'])}",
        f"next_operator_step: {_e(progress['next_step'])}",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]
    return _list_section("Demo Browser Progress", lines, f"/runs/{quote(run_id)}")


def _demo_gate_artifacts(root: Path, run_id: str) -> str:
    if not run_id:
        return _list_section(
            "Demo Gate Artifacts",
            [
                "selected_run_status: missing",
                "commit_request_artifact: none",
                "publication_request_artifact: none",
                "publication_handoff_artifact: none",
                "external_mutations_taken: 0",
            ],
        )

    commit_records = [
        item
        for item in list_coder_worktree_commit_approvals(root, limit=50)
        if item.run_id == run_id
    ]
    publications = [
        item
        for item in list_coder_publications(root, limit=50)
        if item.run_id == run_id
    ]
    commit_record = _preferred_record(
        commit_records,
        ["committed", "approved", "pending_operator_approval", "rejected"],
    )
    publication = _preferred_record(
        publications,
        ["ready_for_operator", "approved", "pending_operator_approval", "rejected"],
    )
    lines = [f"selected_run_id: {_e(run_id)}"]
    if commit_record is None:
        lines.extend(
            [
                "commit_request_artifact: none",
                "commit_decision_artifact: none",
                "local_commit_artifact: pending_until_local_commit",
                "commit_sha: none",
            ]
        )
    else:
        lines.extend(
            [
                f"commit_request_artifact: {_artifact_link(commit_record.request_artifact_path)}",
                f"commit_decision_artifact: {_artifact_link(commit_record.decision_artifact_path) if commit_record.decision_artifact_path else 'none'}",
                (
                    f"local_commit_artifact: {_artifact_link(commit_record.commit_artifact_path)}"
                    if commit_record.commit_sha
                    else "local_commit_artifact: pending_until_local_commit"
                ),
                f"commit_sha: {_e(commit_record.commit_sha or 'none')}",
            ]
        )
    if publication is None:
        lines.extend(
            [
                "publication_request_artifact: none",
                "publication_decision_artifact: none",
                "publication_handoff_artifact: pending_until_publication_handoff",
                "publication_pr_body_path: pending_until_publication_handoff",
            ]
        )
    else:
        pr_body_path = "pending_until_publication_handoff"
        if publication.status == "ready_for_operator":
            payload = load_coder_publication_handoff_payload(root, publication)
            pr_body_path = str(payload.get("pr_body_path", "unavailable"))
        lines.extend(
            [
                f"publication_request_artifact: {_artifact_link(publication.request_artifact_path)}",
                f"publication_decision_artifact: {_artifact_link(publication.decision_artifact_path) if publication.decision_artifact_path else 'none'}",
                (
                    f"publication_handoff_artifact: {_artifact_link(publication.handoff_artifact_path)}"
                    if publication.status == "ready_for_operator"
                    else "publication_handoff_artifact: pending_until_publication_handoff"
                ),
                (
                    f"publication_pr_body_path: {_artifact_link(pr_body_path)}"
                    if publication.status == "ready_for_operator" and pr_body_path != "unavailable"
                    else f"publication_pr_body_path: {_e(pr_body_path)}"
                ),
            ]
        )
    lines.extend(
        [
            "manual_boundary: outside_clankeros",
            "network_actions_taken: 0",
            "external_mutations_taken: 0",
        ]
    )
    return _list_section("Demo Gate Artifacts", lines, f"/runs/{quote(run_id)}")


def _demo_gate_actions(root: Path, run_id: str) -> str:
    progress = _demo_progress_state(root, run_id)
    next_step = progress["next_step"]
    lines = [
        f"current_gate: {_e(next_step)}",
        "confirmation_required: true_for_local_writes",
        "external_effects_created: false",
        "network_actions_taken_by_app: 0",
    ]
    form_html = "<p class='muted'>active_form: unavailable until a demo coder run exists.</p>"
    if not run_id:
        lines.extend(
            [
                "active_action: demo-app-scenario",
                "form_action: none",
                "operator_surface: /demo",
                "required_input: none",
                "output_artifact: fixture_demo_state",
            ]
        )
    elif next_step == "request_commit_for_reviewed_run":
        lines.extend(
            [
                "active_action: coder-commit-request",
                "form_action: /actions/coder-commit-request",
                f"operator_surface: /runs/{_e(run_id)}",
                "required_input: message",
                "output_artifact: coder_commit_request.md",
            ]
        )
        form_html = _input_form(
            "coder-commit-request",
            {"run_id": run_id, "requested_by": "operator"},
            {
                "message": "Implement bounded change from approved worktree run",
                "note": "Demo commit request",
            },
        )
    elif next_step == "approve_or_reject_commit_request":
        pending_commit = _preferred_record(
            [
                item
                for item in list_coder_worktree_commit_approvals(root, limit=50)
                if item.run_id == run_id and item.status == "pending_operator_approval"
            ],
            ["pending_operator_approval"],
        )
        lines.extend(
            [
                "active_action: approve-coder-commit",
                "form_action: /actions/approve-coder-commit",
                "operator_surface: /approvals",
                f"approval_id: {_e(pending_commit.id if pending_commit else 'missing')}",
                "required_input: approval decision note",
                "output_artifact: coder_commit_decision.md",
            ]
        )
        if pending_commit is not None:
            form_html = _form(
                "approve-coder-commit",
                {
                    "approval_id": pending_commit.id,
                    "decided_by": "operator",
                    "note": "Approve demo commit",
                },
            )
    elif next_step == "commit_approved_worktree":
        lines.extend(
            [
                "active_action: commit-coder-worktree",
                "form_action: /actions/commit-coder-worktree",
                f"operator_surface: /runs/{_e(run_id)}",
                "required_input: exact typed commit message",
                "output_artifact: commit.json",
            ]
        )
        form_html = _input_form(
            "commit-coder-worktree",
            {"run_id": run_id, "committed_by": "operator"},
            {"message": "Implement bounded change from approved worktree run"},
        )
    elif next_step == "request_publication_handoff":
        lines.extend(
            [
                "active_action: coder-publication-request",
                "form_action: /actions/coder-publication-request",
                f"operator_surface: /runs/{_e(run_id)}",
                "required_input: remote, target_branch, note",
                "output_artifact: publication_request.md",
            ]
        )
        form_html = _input_form(
            "coder-publication-request",
            {
                "run_id": run_id,
                "requested_by": "operator",
                "remote": "origin",
                "target_branch": "main",
            },
            {"note": "Demo publication request"},
        )
    elif next_step == "approve_or_reject_publication_request":
        pending_publication = _preferred_record(
            [
                item
                for item in list_coder_publications(root, limit=50)
                if item.run_id == run_id and item.status == "pending_operator_approval"
            ],
            ["pending_operator_approval"],
        )
        lines.extend(
            [
                "active_action: approve-coder-publication",
                "form_action: /actions/approve-coder-publication",
                "operator_surface: /approvals",
                f"publication_id: {_e(pending_publication.id if pending_publication else 'missing')}",
                "required_input: publication approval note",
                "output_artifact: publication_decision.md",
            ]
        )
        if pending_publication is not None:
            form_html = _form(
                "approve-coder-publication",
                {
                    "publication_id": pending_publication.id,
                    "decided_by": "operator",
                    "note": "Approve demo publication handoff",
                },
            )
    elif next_step == "prepare_publication_handoff":
        lines.extend(
            [
                "active_action: coder-publication-handoff",
                "form_action: /actions/coder-publication-handoff",
                f"operator_surface: /runs/{_e(run_id)}",
                "required_input: approved publication request",
                "output_artifact: publication_handoff.md + pr_body.md",
            ]
        )
        form_html = _form("coder-publication-handoff", {"run_id": run_id})
    elif next_step == "manual_operator_push_pr_outside_clankeros":
        goal_id = progress.get("goal_id", "")
        lines.extend(
            [
                "active_action: manual_operator_push_pr_outside_clankeros",
                "form_action: /actions/complete-goal",
                f"operator_surface: /goals/{_e(goal_id)}",
                f"goal_id: {_e(goal_id or 'missing')}",
                "required_input: operator confirms manual publication is complete",
                "output_artifact: goal status=completed",
                "manual_boundary: outside_clankeros",
                "copy_only: true",
            ]
        )
        if goal_id:
            form_html = _input_form(
                "complete-goal",
                {"goal_id": goal_id},
                {
                    "completed_by": "operator",
                    "note": "Demo manual publication finished outside ClankerOS.",
                },
            )
        else:
            form_html = "<p class='muted'>complete-goal form unavailable until the demo run is linked to a goal.</p>"
    elif next_step == "review_completed_goal_evidence":
        goal_id = progress.get("goal_id", "")
        lines.extend(
            [
                "active_action: review_completed_goal_evidence",
                "form_action: none",
                f"operator_surface: /goals/{_e(goal_id)}",
                f"goal_id: {_e(goal_id or 'missing')}",
                "required_input: inspect completed goal evidence",
                "output_artifact: none",
                "goal_completion_status: completed",
                "manual_boundary: outside_clankeros",
            ]
        )
        form_html = "<p class='muted'>Goal is locally completed. Review the completed Goal evidence and CI records before merging or continuing outside ClankerOS.</p>"
    else:
        lines.extend(
            [
                f"active_action: {_e(next_step)}",
                "form_action: none",
                f"operator_surface: /runs/{_e(run_id)}",
                "required_input: review current local state",
                "output_artifact: none",
            ]
        )
    return "".join(
        [
            "<section><h2>Demo Gate Actions</h2>",
            "<p class='muted'>State-aware local forms for the current demo gate. Each write still goes through the normal confirmation page and existing local safety checks.</p>",
            _ul(lines),
            form_html,
            "</section>",
        ]
    )


def _demo_next_action_panel(root: Path, run_id: str) -> str:
    progress = _demo_progress_state(root, run_id)
    if not run_id:
        return _list_section(
            "Demo Next Action",
            [
                f"demo_continue_from: {_e(progress['next_step'])}",
                "demo_command: python3 -m agent_os.cli demo-app-scenario",
                "external_effects_created: false",
                "network_actions_taken_by_app: 0",
            ],
        )

    next_step = progress["next_step"]
    action_hints = {
        "request_commit_for_reviewed_run": "request the local commit gate from the run detail page",
        "approve_or_reject_commit_request": "decide the pending commit request on approvals",
        "commit_approved_worktree": "type the commit message and create the local worktree commit from the run detail page",
        "request_publication_handoff": "request the publication handoff gate from the run detail page",
        "approve_or_reject_publication_request": "decide the pending publication request on approvals",
        "prepare_publication_handoff": "prepare the local publication handoff from the run detail page",
        "manual_operator_push_pr_outside_clankeros": "use the publication handoff outside ClankerOS, then mark the Goal completed locally",
        "review_completed_goal_evidence": "review the completed Goal evidence",
    }
    lines = [
        f"demo_continue_from: {_e(next_step)}",
        f"operator_surface_hint: {_e(action_hints.get(next_step, 'review demo state'))}",
        f"workflow_surface: <a href='/workflow?run_id={quote(run_id)}'>/workflow?run_id={_e(run_id)}</a>",
        f"run_action_surface: <a href='/runs/{quote(run_id)}'>/runs/{_e(run_id)}</a>",
        "approvals_surface: <a href='/approvals'>/approvals</a>",
        "inbox_surface: <a href='/inbox'>/inbox</a>",
        "external_effects_created: false",
        "network_actions_taken_by_app: 0",
    ]
    if next_step == "manual_operator_push_pr_outside_clankeros":
        lines.append("manual_boundary: outside_clankeros")
    if next_step == "review_completed_goal_evidence":
        lines.append("goal_completion_status: completed")
    return _list_section("Demo Next Action", lines)


def _demo_progress_state(root: Path, run_id: str) -> dict[str, str]:
    if not run_id:
        return {
            "goal_id": "",
            "goal_status": "missing",
            "commit_status": "not_requested",
            "local_commit_status": "missing",
            "publication_status": "not_requested",
            "publication_handoff_status": "missing",
            "manual_status": "not_ready",
            "next_step": "run demo scenario and select a coder worktree run",
        }
    storage = _storage(root)
    goal_id = _goal_id_for_coder_run(storage, run_id)
    goal_status = "missing"
    if goal_id:
        try:
            goal_status = storage.get_goal(goal_id).status
        except KeyError:
            goal_status = "missing"
    commit_records = [
        item
        for item in list_coder_worktree_commit_approvals(root, limit=50)
        if item.run_id == run_id
    ]
    publications = [
        item
        for item in list_coder_publications(root, limit=50)
        if item.run_id == run_id
    ]
    commit_status = _preferred_status(
        commit_records,
        ["committed", "approved", "pending_operator_approval", "rejected"],
        "not_requested",
    )
    publication_status = _preferred_status(
        publications,
        ["ready_for_operator", "approved", "pending_operator_approval", "rejected"],
        "not_requested",
    )
    local_commit_status = (
        "available" if any(item.commit_sha for item in commit_records) else "missing"
    )
    publication_handoff_status = (
        "available"
        if any(item.status == "ready_for_operator" for item in publications)
        else "missing"
    )
    manual_status = (
        "ready_outside_clankeros"
        if publication_handoff_status == "available"
        else "not_ready"
    )
    next_step = _demo_next_operator_step(
        goal_status=goal_status,
        commit_status=commit_status,
        local_commit_status=local_commit_status,
        publication_status=publication_status,
        publication_handoff_status=publication_handoff_status,
    )
    return {
        "goal_id": goal_id,
        "goal_status": goal_status,
        "commit_status": commit_status,
        "local_commit_status": local_commit_status,
        "publication_status": publication_status,
        "publication_handoff_status": publication_handoff_status,
        "manual_status": manual_status,
        "next_step": next_step,
    }


def _preferred_status(items: list[Any], statuses: list[str], default: str) -> str:
    for status in statuses:
        if any(item.status == status for item in items):
            return status
    return default


def _preferred_record(items: list[Any], statuses: list[str]) -> Any | None:
    for status in statuses:
        for item in items:
            if item.status == status:
                return item
    return items[0] if items else None


def _demo_next_operator_step(
    *,
    goal_status: str,
    commit_status: str,
    local_commit_status: str,
    publication_status: str,
    publication_handoff_status: str,
) -> str:
    if goal_status == "completed":
        return "review_completed_goal_evidence"
    if commit_status == "not_requested":
        return "request_commit_for_reviewed_run"
    if commit_status == "pending_operator_approval":
        return "approve_or_reject_commit_request"
    if commit_status == "approved":
        return "commit_approved_worktree"
    if local_commit_status == "available" and publication_status == "not_requested":
        return "request_publication_handoff"
    if publication_status == "pending_operator_approval":
        return "approve_or_reject_publication_request"
    if publication_status == "approved":
        return "prepare_publication_handoff"
    if publication_handoff_status == "available":
        return "manual_operator_push_pr_outside_clankeros"
    return "review_demo_state"


def _goal_id_for_coder_run(storage: Storage, run_id: str) -> str:
    coder_run = get_coder_worktree_run(storage, run_id)
    if coder_run is None:
        return ""
    delegation = storage.get_subagent_delegation(coder_run.delegation_id)
    if delegation is None:
        return ""
    return delegation.parent_goal_id


def _manual_browser_script(state: dict[str, str] | None) -> str:
    delegation_id = (state or {}).get("delegation_id", "")
    run_id = (state or {}).get("run_id", "")
    goal_id = (state or {}).get("goal_id", "")
    project_id = (state or {}).get("project_id", "local-app-demo")
    steps = [
        "Run `python3 -m agent_os.cli demo-app-scenario` to refresh fixture state.",
        "Start `python3 -m agent_os.cli app` and open `http://127.0.0.1:8787/demo`.",
        f"Open `/projects/{project_id}` and confirm Project Operator Guidance shows the demo next action.",
    ]
    if delegation_id:
        steps.extend(
            [
                f"Open `/workflow?delegation_id={delegation_id}` and scan selected_status tokens.",
                f"Open `/delegations/{delegation_id}` and inspect handoff, coder prep, worktree plan, and pending approval state.",
            ]
        )
    if run_id:
        steps.extend(
            [
                f"Open `/workflow?run_id={run_id}` and confirm the run-scoped workflow state.",
                f"Open `/runs/{run_id}` and review diff, changed files, bounded validation, stdout/stderr, and review artifacts.",
                "From the run page, walk commit request, commit approval, typed local commit, publication request, publication approval, and publication handoff.",
            ]
        )
        if goal_id:
            steps.append(
                f"After manual push/PR outside ClankerOS, return to `/goals/{goal_id}` and use `complete-goal` to record local Goal completion."
            )
    steps.extend(
        [
            "Open `/approvals` and `/inbox` to verify pending decisions stay visible.",
            "Stop before any manual push or PR command; ClankerOS only writes the publication handoff and suggested commands.",
        ]
    )
    rendered_steps = [f"{index}. {_e(step)}" for index, step in enumerate(steps, start=1)]
    return "".join(
        [
            "<section><h2>Manual Browser Script</h2>",
            "<p class='muted'>Use this as the first manual dogfooding pass after a pushed app change.</p>",
            _ul(rendered_steps),
            "</section>",
            _manual_browser_checkpoints(state),
        ]
    )


def _manual_browser_checkpoints(state: dict[str, str] | None) -> str:
    delegation_id = (state or {}).get("delegation_id", "")
    run_id = (state or {}).get("run_id", "")
    project_id = (state or {}).get("project_id", "local-app-demo")
    checkpoints = [
        "<a href='/demo'>/demo</a> marker=Demo Scenario expected=Demo Dogfooding Links,Demo Browser Progress,Demo Gate Artifacts",
        "<a href='/dogfooding'>/dogfooding</a> marker=Manual Dogfooding Checklist expected=Dogfooding Next Action,GitHub Actions Follow-up",
        f"<a href='/projects/{quote(project_id)}'>/projects/{_e(project_id)}</a> marker=Project expected=Project Operator Guidance,Project Workflow Launchpad",
        "<a href='/approvals'>/approvals</a> marker=Approvals expected=pending local decisions or empty queue",
        "<a href='/inbox'>/inbox</a> marker=Operator Inbox expected=queue counts and next-action cues",
        "<a href='/verification'>/verification</a> marker=Verification Handoff expected=fast/full-suite boundary and no GitHub status fetch",
        "<a href='/health'>/health</a> marker=System Health expected=local app status artifact and zero-effect non-claims",
    ]
    if delegation_id:
        checkpoints.extend(
            [
                f"<a href='/delegations/{quote(delegation_id)}'>/delegations/{_e(delegation_id)}</a> marker=Delegation expected=Workflow Readiness,Safe Local Actions",
                f"<a href='/workflow?delegation_id={quote(delegation_id)}'>/workflow?delegation_id={_e(delegation_id)}</a> marker=Modern Operator Workflow expected=Selected Workflow State",
            ]
        )
    else:
        checkpoints.append("delegation_checkpoint_status: pending_until_demo_fixture_exists")
    if run_id:
        checkpoints.extend(
            [
                f"<a href='/workflow?run_id={quote(run_id)}'>/workflow?run_id={_e(run_id)}</a> marker=Modern Operator Workflow expected=Selected Workflow Continuation",
                f"<a href='/runs/{quote(run_id)}'>/runs/{_e(run_id)}</a> marker=Run expected=Run Workflow State,Run Approval Actions,Coder Worktree Evidence",
            ]
        )
    else:
        checkpoints.append("run_checkpoint_status: pending_until_demo_fixture_exists")
    checkpoints.extend(
        [
            "manual_boundary: outside_clankeros",
            "provider_calls_taken_by_clankeros: 0",
            "network_actions_taken_by_app: 0",
            "external_mutations_taken: 0",
        ]
    )
    return _list_section("Manual Browser Checkpoints", checkpoints)


def _handle_post(root: Path, path: str, form: dict[str, list[str]]) -> LocalAppResponse:
    action = path.removeprefix("/actions/")
    mutating = action not in {"implementation-handoff"}
    if mutating and _one(form, "confirm") != "yes":
        return _html_page(
            root,
            "Confirm Action",
            _confirm_form(action, form),
            status=409,
        )
    storage = _storage(root)
    try:
        if action == "refresh-dashboard-state":
            status_path = write_local_app_status(
                root,
                host=DEFAULT_HOST,
                port=DEFAULT_PORT,
            )
            message = f"local_app_status: {status_path.relative_to(root)}"
            location = "/"
            result = {"status_path": status_path, "artifact_written": True}
        elif action == "register-project":
            project = register_project(
                root,
                name=_required(form, "name"),
                repo_path=Path(_required(form, "path")),
                default_test_command=_required(form, "test_command"),
                allowed_write_roots=[
                    Path(item.strip())
                    for item in (_one(form, "allowed_write_roots") or "").split(",")
                    if item.strip()
                ]
                or None,
            )
            message = f"project_registered: {project.name}"
            location = f"/projects/{quote(project.name)}"
            _write_workspace_state(
                root,
                {
                    **_load_workspace_state(root),
                    "open_project": project.name,
                    "open_goal": "",
                    "last_viewed_artifact": f"projects/{project.name}/project.md",
                    "updated_by": "register-project",
                },
            )
            result = project
        elif action == "create-goal":
            lifecycle = create_goal_lifecycle(
                root,
                storage,
                project_id=_required(form, "project_id"),
                prompt=_required(form, "prompt"),
                created_by_profile=_one(form, "created_by_profile") or "planner",
            )
            message = f"goal_created: {lifecycle.goal.id}"
            location = f"/goals/{quote(lifecycle.goal.id)}"
            _write_workspace_state(
                root,
                {
                    **_load_workspace_state(root),
                    "open_project": lifecycle.goal.project_id,
                    "open_goal": lifecycle.goal.id,
                    "last_viewed_artifact": str(lifecycle.goal_artifact_path.relative_to(root)),
                    "updated_by": "create-goal",
                },
            )
            result = lifecycle
        elif action == "delegate":
            result = _create_scout_delegation_from_form(root, storage, form)
            message = f"subagent_delegation: {result.id}"
            location = f"/delegations/{quote(result.id)}"
            _remember_delegation_workspace(
                root,
                storage,
                result.id,
                artifact_path=result.result_artifact_path,
                updated_by="delegate",
            )
        elif action == "resume-goal":
            result = _resume_goal_from_form(storage, form)
            message = f"goal_resumed: {result['goal_id']}"
            location = f"/goals/{quote(result['goal_id'])}"
            _write_workspace_state(
                root,
                {
                    **_load_workspace_state(root),
                    "open_project": result["project_id"],
                    "open_goal": result["goal_id"],
                    "last_viewed_artifact": _repo_relative_artifact_path(
                        root,
                        _goal_file_path(result["project_id"], result["goal_id"], "GOAL.md"),
                    ),
                    "updated_by": "resume-goal",
                },
            )
        elif action == "complete-goal":
            result = _complete_goal_from_form(root, storage, form)
            message = f"goal_completed: {result['goal_id']}"
            location = f"/goals/{quote(result['goal_id'])}"
            handoff_artifact_path = result.get("handoff_artifact_path")
            _write_workspace_state(
                root,
                {
                    **_load_workspace_state(root),
                    "open_project": result["project_id"],
                    "open_goal": result["goal_id"],
                    "last_viewed_artifact": _repo_relative_artifact_path(
                        root,
                        (
                            Path(str(handoff_artifact_path)).with_suffix(".md")
                            if handoff_artifact_path
                            else None
                        ),
                    ),
                    "updated_by": "complete-goal",
                },
            )
        elif action == "save-goal-note":
            result = _append_goal_operator_note(root, storage, form)
            message = f"goal_operator_note_saved: {result['goal_id']}"
            location = f"/goals/{quote(result['goal_id'])}"
            _write_workspace_state(
                root,
                {
                    **_load_workspace_state(root),
                    "open_project": result["project_id"],
                    "open_goal": result["goal_id"],
                    "last_viewed_artifact": result["note_path"],
                    "updated_by": "save-goal-note",
                },
            )
        elif action == "save-workspace":
            result = _write_workspace_state(
                root,
                {
                    "open_project": _one(form, "open_project") or "",
                    "open_goal": _one(form, "open_goal") or "",
                    "filters": _one(form, "filters") or "",
                    "expanded_panels": _one(form, "expanded_panels") or "",
                    "last_viewed_artifact": _one(form, "last_viewed_artifact") or "",
                    "updated_by": _one(form, "updated_by") or "operator",
                },
            )
            message = "workspace_saved: .clanker/app/workspace.json"
            location = _safe_local_return_path(_one(form, "return_to")) or "/workspace"
        elif action == "pin-memory":
            memory_id = _required(form, "memory_id")
            result = storage.update_memory_entry_status(
                memory_id,
                status="active",
                decided_by=_one(form, "decided_by") or "operator",
                reason=_one(form, "note") or "Pinned from local app.",
            )
            message = f"memory_pinned: {result.id}"
            location = "/memory"
            workspace = _load_workspace_state(root)
            open_project = result.project_id or workspace.get("open_project", "")
            open_goal = workspace.get("open_goal", "").strip()
            if open_goal and open_project:
                try:
                    goal = storage.get_goal(open_goal)
                except KeyError:
                    open_goal = ""
                else:
                    if goal.project_id != open_project:
                        open_goal = ""
            _write_workspace_state(
                root,
                {
                    **workspace,
                    "open_project": open_project,
                    "open_goal": open_goal,
                    "last_viewed_artifact": _repo_relative_artifact_path(
                        root,
                        result.artifact_path,
                    ),
                    "updated_by": "pin-memory",
                },
            )
        elif action == "context-pack":
            delegation_id = _required(form, "delegation_id")
            result = generate_context_pack(root, storage, delegation_id)
            message = f"context_pack: {result.context_pack_id}"
            location = f"/delegations/{quote(delegation_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                delegation_id,
                artifact_path=result.markdown_path or result.json_path,
                updated_by="context-pack",
            )
        elif action == "run-delegation":
            delegation_id = _required(form, "delegation_id")
            run_result = run_delegation(
                root,
                storage,
                delegation_id,
                record_memory=_one(form, "record_memory") == "yes",
                memory_key=_one(form, "memory_key"),
                operator_id=_one(form, "operator_id") or "operator",
            )
            message = (
                f"run_delegation: {run_result.delegation_id}"
                if run_result.status == "completed"
                else f"run_delegation_failed: {run_result.message}"
            )
            location = f"/delegations/{quote(delegation_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                delegation_id,
                artifact_path=(
                    run_result.result_artifact_path or (run_result.evidence_dir / "summary.md")
                ),
                updated_by="run-delegation",
            )
            result = {
                "delegation_id": run_result.delegation_id,
                "run_id": run_result.run_id,
                "status": run_result.status,
                "adapter_type": run_result.adapter_type,
                "exit_code": run_result.exit_code,
                "stdout_path": run_result.stdout_path,
                "stderr_path": run_result.stderr_path,
                "parsed_output_path": run_result.parsed_output_path,
                "evidence_dir": run_result.evidence_dir,
                "result_artifact_path": run_result.result_artifact_path,
                "incident_id": run_result.incident_id,
                "memory_proposal_id": run_result.memory_proposal_id,
                "next_recommended_action": run_result.next_recommended_action,
                "provider_calls_taken_by_clankeros": 0,
                "network_actions_taken": 0,
                "external_mutations_taken": 0,
            }
        elif action == "implementation-handoff":
            delegation_id = _required(form, "delegation_id")
            delegation = storage.get_subagent_delegation(delegation_id)
            if delegation is None:
                raise ValueError("delegation not found")
            summary = summarize_implementation_handoff(root, delegation)
            message = f"implementation_handoff_status: {summary['status']}"
            location = f"/delegations/{quote(delegation_id)}"
            result = summary
        elif action == "coder-prep":
            delegation_id = _required(form, "delegation_id")
            result = prepare_coder_from_handoff(root, storage, delegation_id)
            message = f"coder_prep: {result.prep_id}"
            location = f"/delegations/{quote(delegation_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                delegation_id,
                artifact_path=result.markdown_path or result.artifact_path,
                updated_by="coder-prep",
            )
        elif action == "coder-prep-from-handoff":
            handoff_md = _required(form, "handoff_md")
            result = prepare_coder_from_handoff_markdown(root, storage, handoff_md)
            message = f"coder_prep: {result.prep_id}"
            location = f"/delegations/{quote(result.delegation_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                result.delegation_id,
                artifact_path=result.markdown_path or result.artifact_path,
                updated_by="coder-prep-from-handoff",
            )
        elif action == "coder-worktree-plan":
            delegation_id = _required(form, "delegation_id")
            result = prepare_worktree_plan_from_coder_prep(root, storage, delegation_id)
            message = f"coder_worktree_plan: {result.plan_id}"
            location = f"/delegations/{quote(delegation_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                delegation_id,
                artifact_path=result.markdown_path or result.artifact_path,
                updated_by="coder-worktree-plan",
            )
        elif action == "coder-worktree-approval":
            delegation_id = _required(form, "delegation_id")
            result = request_coder_worktree_approval(
                root,
                storage,
                delegation_id,
                requested_by=_one(form, "requested_by") or "operator",
                note=_one(form, "note") or "Requested from local app.",
            )
            message = f"coder_worktree_approval: {result.approval.id}"
            location = f"/delegations/{quote(delegation_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                delegation_id,
                artifact_path=Path(result.approval.request_artifact_path).with_suffix(".md"),
                updated_by="coder-worktree-approval",
            )
        elif action == "approve-coder-worktree":
            approval_id = _required(form, "approval_id")
            result = approve_coder_worktree(
                root,
                storage,
                approval_id,
                decided_by=_one(form, "decided_by") or "operator",
                note=_one(form, "note") or "Approved from local app.",
            )
            message = f"approved_coder_worktree: {result.approval.id}"
            location = "/"
            _remember_delegation_workspace(
                root,
                storage,
                result.approval.delegation_id,
                artifact_path=(
                    Path(result.approval.decision_artifact_path).with_suffix(".md")
                    if result.approval.decision_artifact_path
                    else None
                ),
                updated_by="approve-coder-worktree",
            )
        elif action == "run-coder-worktree":
            delegation_id = _required(form, "delegation_id")
            run_result = run_approved_coder_worktree(
                root,
                storage,
                delegation_id,
                command=_required(form, "command"),
                verify=_one(form, "verify") == "yes",
                verify_command=_one(form, "verify_command") or None,
                rerun=_one(form, "rerun") == "yes",
            )
            coder_run = run_result.run
            change_summary = coder_worktree_change_summary(root, coder_run)
            message = (
                f"run_coder_worktree: already_recorded {coder_run.id}"
                if run_result.already_recorded
                else f"run_coder_worktree: {coder_run.status}"
            )
            location = f"/runs/{quote(coder_run.id)}"
            result = {
                "run_id": coder_run.id,
                "delegation_id": coder_run.delegation_id,
                "source_delegation_run_id": coder_run.source_run_id,
                "project_id": coder_run.project_id,
                "approval_id": coder_run.approval_id,
                "status": coder_run.status,
                "failure_class": coder_run.failure_class or "none",
                "worktree_path": coder_run.worktree_path,
                "branch_name": coder_run.branch_name,
                "command_exit_code": coder_run.command_exit_code,
                "verification_exit_code": coder_run.verification_exit_code,
                "changed_files": coder_run.changed_files,
                "changed_files_count": change_summary["changed_files_count"],
                "outside_allowed_files": coder_run.outside_allowed_files,
                "changed_files_within_allowed_files": not coder_run.outside_allowed_files,
                "diff_summary": change_summary["diff_summary"],
                "evidence_path": coder_run.evidence_path,
                "commit_created": False,
                "push_created": False,
                "deploy_created": False,
                "provider_calls_taken_by_clankeros": 0,
                "network_actions_taken": 0,
                "external_mutations_taken": 0,
            }
            run_summary_path = Path(coder_run.evidence_path) / "summary.md"
            _remember_delegation_workspace(
                root,
                storage,
                coder_run.delegation_id,
                artifact_path=(
                    run_summary_path
                    if (root / run_summary_path).exists()
                    else coder_run.evidence_path
                ),
                updated_by="run-coder-worktree",
            )
        elif action == "review-run":
            requested_run_id = _required(form, "run_id")
            coder_run = get_coder_worktree_run(storage, requested_run_id)
            if coder_run is not None and coder_run.status != "completed":
                raise ValueError(f"review-run requires a completed coder worktree run: {coder_run.status}")
            source_run_id = coder_run.source_run_id if coder_run is not None else requested_run_id
            report_path, packet = write_run_review(root, source_run_id)
            message = f"run_review: {packet.run.id}"
            location = f"/runs/{quote(requested_run_id)}"
            result = {
                "run_id": packet.run.id,
                "requested_run_id": requested_run_id,
                "coder_worktree_run_id": coder_run.id if coder_run is not None else "none",
                "review_path": report_path.relative_to(root).as_posix(),
                "tasks": len(packet.tasks),
                "events": len(packet.events),
                "recommended_next_action": packet.recommended_next_action,
                "network_actions_taken": 0,
                "external_mutations_taken": 0,
            }
            if coder_run is not None:
                _remember_delegation_workspace(
                    root,
                    storage,
                    coder_run.delegation_id,
                    artifact_path=report_path,
                    updated_by="review-run",
                )
        elif action == "coder-commit-request":
            run_id = _required(form, "run_id")
            result = request_coder_worktree_commit_approval(
                root,
                storage,
                run_id,
                requested_by=_one(form, "requested_by") or "operator",
                commit_message=_required(form, "message"),
                note=_one(form, "note") or "Requested from local app.",
            )
            message = f"coder_commit_request: {result.approval.id}"
            location = f"/runs/{quote(run_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                result.approval.delegation_id,
                artifact_path=Path(result.approval.request_artifact_path).with_suffix(".md"),
                updated_by="coder-commit-request",
            )
        elif action == "approve-coder-commit":
            approval_id = _required(form, "approval_id")
            result = approve_coder_worktree_commit(
                root,
                storage,
                approval_id,
                decided_by=_one(form, "decided_by") or "operator",
                note=_one(form, "note") or "Approved from local app.",
            )
            message = f"approved_coder_commit: {result.approval.id}"
            location = "/"
            _remember_delegation_workspace(
                root,
                storage,
                result.approval.delegation_id,
                artifact_path=(
                    Path(result.approval.source_run_evidence_path)
                    / "coder_commit"
                    / "coder_commit_decision.md"
                ),
                updated_by="approve-coder-commit",
            )
        elif action == "commit-coder-worktree":
            run_id = _required(form, "run_id")
            result = commit_coder_worktree(
                root,
                storage,
                run_id,
                message=_required(form, "message"),
                committed_by=_one(form, "committed_by") or "operator",
            )
            message = f"commit_coder_worktree: {result.status}"
            location = f"/runs/{quote(run_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                result.approval.delegation_id,
                artifact_path=(
                    Path(result.alias_evidence_path).with_suffix(".md")
                    if result.alias_evidence_path
                    else Path(result.evidence_path).with_suffix(".md")
                ),
                updated_by="commit-coder-worktree",
            )
        elif action == "coder-publication-request":
            run_id = _required(form, "run_id")
            result = request_coder_publication(
                root,
                storage,
                run_id,
                requested_by=_one(form, "requested_by") or "operator",
                remote=_one(form, "remote") or "origin",
                target_branch=_one(form, "target_branch") or "main",
                note=_required(form, "note"),
            )
            message = f"coder_publication_request: {result.publication.id}"
            location = f"/runs/{quote(run_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                result.publication.delegation_id,
                artifact_path=Path(result.publication.request_artifact_path).with_suffix(".md"),
                updated_by="coder-publication-request",
            )
        elif action == "approve-coder-publication":
            publication_id = _required(form, "publication_id")
            result = approve_coder_publication(
                root,
                storage,
                publication_id,
                decided_by=_one(form, "decided_by") or "operator",
                note=_one(form, "note") or "Approved from local app.",
            )
            message = f"approved_coder_publication: {result.publication.id}"
            location = "/approvals"
            _remember_delegation_workspace(
                root,
                storage,
                result.publication.delegation_id,
                artifact_path=(
                    Path(result.publication.decision_artifact_path).with_suffix(".md")
                    if result.publication.decision_artifact_path
                    else None
                ),
                updated_by="approve-coder-publication",
            )
        elif action == "coder-publication-handoff":
            run_id = _required(form, "run_id")
            result = create_coder_publication_handoff(root, storage, run_id)
            message = f"coder_publication_handoff: {result.status}"
            location = f"/runs/{quote(run_id)}"
            _remember_delegation_workspace(
                root,
                storage,
                result.publication.delegation_id,
                artifact_path=Path(result.artifact_path).with_suffix(".md"),
                updated_by="coder-publication-handoff",
            )
        elif action == "ci-snapshot-evidence-from-gh-json":
            result = record_ci_snapshot_evidence_from_gh_status_json(
                root,
                project_id=_one(form, "project") or "clankeros",
                branch_name=_one(form, "branch") or "main",
                commit_sha=_required(form, "commit"),
                provider=_one(form, "provider") or "github-actions",
                external_run_id=_one(form, "external_run_id"),
                status_json_text=_required(form, "status_json"),
                external_url=_one(form, "url"),
                recorded_by=_one(form, "recorded_by") or "operator",
                note=_one(form, "note") or "Validated from local app.",
                job_name=_one(form, "job_name"),
            )
            message = f"ci_snapshot_evidence_from_gh_json: {result.status}"
            location = _safe_local_return_path(_one(form, "return_to")) or "/ci-evidence"
        else:
            raise ValueError(f"unsupported action: {action}")
    except (
        ValueError,
        ContextPackError,
        DelegationRunError,
        MemoryEntryError,
        CoderPrepError,
        CoderWorktreePlanError,
        CoderWorktreeApprovalError,
        CoderWorktreeRunError,
        CoderWorktreeCommitError,
        CoderPublicationError,
        PlanningError,
        DelegationError,
        KeyError,
    ) as error:
        return _html_page(
            root,
            "Action Error",
            _action_error_page(action, form, error),
            status=400,
        )
    return _html_page(
        root,
        "Action Result",
        _action_result_page(
            root,
            action=action,
            form=form,
            message=message,
            location=location,
            result=result,
        ),
    )


def _create_scout_delegation_from_form(
    root: Path,
    storage: Storage,
    form: dict[str, list[str]],
) -> Any:
    goal_id = _required(form, "goal_id")
    task_id = _required(form, "task_id")
    profile = _one(form, "profile") or "scout"
    if profile != "scout":
        raise ValueError("browser delegate action only supports the read-only scout profile")
    task = storage.get_task(task_id)
    if task.goal_id != goal_id:
        raise ValueError("task does not belong to submitted goal")
    existing = next(
        (
            delegation
            for delegation in storage.list_subagent_delegations(goal_id)
            if delegation.parent_task_id == task_id
        ),
        None,
    )
    if existing is not None:
        return existing
    return create_subagent_delegation(
        root,
        storage,
        task_id=task_id,
        title=_required(form, "title"),
        profile_override="scout",
    )


def _resume_goal_from_form(
    storage: Storage,
    form: dict[str, list[str]],
) -> dict[str, Any]:
    goal_id = _required(form, "goal_id")
    goal = storage.get_goal(goal_id)
    if goal.status != "paused":
        raise ValueError("resume-goal only supports status=paused")
    resumed_by = (_one(form, "resumed_by") or "operator").strip() or "operator"
    note = (_one(form, "note") or "").strip()
    storage.set_goal_status(goal.id, "active")
    return {
        "status": "goal_resumed",
        "goal_id": goal.id,
        "project_id": goal.project_id,
        "previous_status": goal.status,
        "new_status": "active",
        "resumed_by": resumed_by,
        "note": note or "none",
        "approvals_created": 0,
        "work_started": "false",
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
    }


def _complete_goal_from_form(
    root: Path,
    storage: Storage,
    form: dict[str, list[str]],
) -> dict[str, Any]:
    goal_id = _required(form, "goal_id")
    state = _goal_state(root, storage, goal_id)
    goal = state.get("goal")
    if goal is None:
        raise ValueError("goal not found")
    if goal.status == "completed":
        raise ValueError("complete-goal only supports incomplete goals")
    ready_publication = _goal_ready_publication(state)
    if ready_publication is None:
        raise ValueError("complete-goal requires a ready publication handoff")
    completed_by = (_one(form, "completed_by") or "operator").strip() or "operator"
    note = (_one(form, "note") or "").strip()
    storage.set_goal_status(goal.id, "completed")
    return {
        "status": "goal_completed",
        "goal_id": goal.id,
        "project_id": goal.project_id,
        "previous_status": goal.status,
        "new_status": "completed",
        "completed_by": completed_by,
        "note": note or "none",
        "publication_id": ready_publication.id,
        "publication_status": ready_publication.status,
        "handoff_artifact_path": ready_publication.handoff_artifact_path,
        "manual_publish_boundary": "outside_clankeros",
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
    }


def _append_goal_operator_note(
    root: Path,
    storage: Storage,
    form: dict[str, list[str]],
) -> dict[str, Any]:
    goal_id = _required(form, "goal_id")
    note = _required(form, "note").strip()
    if not note:
        raise ValueError("note is required")
    goal = storage.get_goal(goal_id)
    author = (_one(form, "author") or "operator").strip() or "operator"
    relative_path = _goal_operator_notes_path(goal)
    note_path = root / relative_path
    note_path.parent.mkdir(parents=True, exist_ok=True)
    existing = note_path.read_text(encoding="utf-8") if note_path.exists() else ""
    if not existing.strip():
        existing = f"# Operator Notes For {goal.id}\n\n"
    timestamp = utc_now()
    entry = "\n".join(
        [
            f"## {timestamp}",
            "",
            f"- author: {author}",
            f"- goal: {goal.id}",
            f"- project: {goal.project_id}",
            "",
            note,
            "",
        ]
    )
    note_path.write_text(existing.rstrip() + "\n\n" + entry, encoding="utf-8")
    return {
        "status": "goal_operator_note_saved",
        "goal_id": goal.id,
        "project_id": goal.project_id,
        "note_path": relative_path.as_posix(),
        "appended_by": author,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
    }


def _safe_action_forms(*, delegation_id: str, handoff_md: str) -> str:
    return f"""
    <section><h2>Safe Local Actions</h2>
      <p class="muted">Delegation-scoped artifact, approval, read-only delegation run, and approved bounded worktree run actions require an explicit confirmation page. Local commit and publication handoff actions stay gate-specific; push, PR, deploy, provider, and arbitrary command actions are not exposed here.</p>
      {_form('implementation-handoff', {'delegation_id': delegation_id})}
      {_form('context-pack', {'delegation_id': delegation_id})}
      {_form('run-delegation', {'delegation_id': delegation_id, 'operator_id': 'operator'})}
      {_form('coder-prep', {'delegation_id': delegation_id})}
      {_form('coder-prep-from-handoff', {'handoff_md': handoff_md})}
      {_form('coder-worktree-plan', {'delegation_id': delegation_id})}
      {_form('coder-worktree-approval', {'delegation_id': delegation_id, 'note': 'Approve bounded worktree execution from local app'})}
    </section>
    """


def _action_error_page(
    action: str,
    form: dict[str, list[str]],
    error: Exception,
) -> str:
    return "".join(
        [
            "<section><h1>Action Error Details</h1>",
            "<p class='error'>No action was completed.</p>",
            _non_claim_banner(),
            _kv(
                [
                    ("action", action),
                    ("error_type", type(error).__name__),
                    ("error", str(error)),
                ]
            ),
            "<h2>Action Payload</h2>",
            _kv(_submitted_form_rows(form)),
            "<p class='muted'>Review the submitted fields, fix the missing or invalid value, then retry from the relevant local app page.</p>",
            "</section>",
        ]
    )


def _action_result_page(
    root: Path,
    *,
    action: str,
    form: dict[str, list[str]],
    message: str,
    location: str,
    result: Any,
) -> str:
    next_href = f"{location}?notice={quote(message)}"
    return "".join(
        [
            "<section><h1>Action Result Details</h1>",
            "<p>Action completed. Review the local result before continuing.</p>",
            _non_claim_banner(),
            _kv(
                [
                    ("action", action),
                    ("result", message),
                    ("next_page", SafeHtml(f"<a href='{_e(next_href)}'>{_e(location)}</a>")),
                ]
            ),
            "<h2>Action Payload</h2>",
            _kv(_submitted_form_rows(form)),
            "<h2>Result Fields</h2>",
            _kv(_action_result_rows(root, result)),
            _action_result_continuation_section(root, location, message),
            "<p class='muted'>This page is a local readback only. Follow the next-page link after checking the payload, artifacts, and safety boundary.</p>",
            "</section>",
        ]
    )


def _action_result_continuation_section(root: Path, location: str, message: str) -> str:
    next_href = f"{location}?notice={quote(message)}"
    try:
        storage = _storage(root)
        workspace = _load_workspace_state(root)
    except Exception:
        return "".join(
            [
                "<section class='action-continuation' data-action-continuation='true'><h2>Action Continuation</h2>",
                _kv(
                    [
                        ("action_continuation_status", "state_unavailable"),
                        ("action_continuation_next_page", SafeHtml(f"<a href='{_e(next_href)}'>{_e(location)}</a>")),
                        ("action_continuation_action_form_available", "false"),
                        ("action_continuation_write_on_get", "false"),
                        ("action_continuation_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )

    goal_id = str(workspace.get("open_goal") or "").strip()
    if not goal_id:
        return "".join(
            [
                "<section class='action-continuation' data-action-continuation='true'><h2>Action Continuation</h2>",
                _kv(
                    [
                        ("action_continuation_status", "no_saved_goal"),
                        ("action_continuation_next_page", SafeHtml(f"<a href='{_e(next_href)}'>{_e(location)}</a>")),
                        ("action_continuation_action_form_available", "false"),
                        ("action_continuation_write_on_get", "false"),
                        ("action_continuation_provider_calls_taken", "0"),
                        ("action_continuation_network_actions_taken", "0"),
                        ("action_continuation_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )

    state = _goal_state(root, storage, goal_id)
    goal = state.get("goal")
    if goal is None:
        return "".join(
            [
                "<section class='action-continuation' data-action-continuation='true'><h2>Action Continuation</h2>",
                _kv(
                    [
                        ("action_continuation_status", "missing_goal"),
                        ("action_continuation_saved_goal", goal_id),
                        ("action_continuation_next_page", SafeHtml(f"<a href='{_e(next_href)}'>{_e(location)}</a>")),
                        ("action_continuation_action_form_available", "false"),
                        ("action_continuation_write_on_get", "false"),
                        ("action_continuation_provider_calls_taken", "0"),
                        ("action_continuation_network_actions_taken", "0"),
                        ("action_continuation_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )

    phase = _goal_current_phase(state)
    next_action = _goal_next_action(root, state)
    action_form = _goal_next_action_form(state, next_action)
    return "".join(
        [
            "<section class='action-continuation' data-action-continuation='true'><h2>Action Continuation</h2>",
            "<p class='muted'>Continue from the refreshed saved goal state after this local action.</p>",
            _kv(
                [
                    ("action_continuation_status", "available"),
                    ("action_continuation_source", "saved_workspace_goal_after_action"),
                    (
                        "action_continuation_goal",
                        SafeHtml(f"<a href='/goals/{quote(goal.id)}'>{_e(goal.title or goal.description or goal.id)}</a>"),
                    ),
                    ("action_continuation_phase", phase),
                    ("action_continuation_next_action", next_action.action),
                    (
                        "action_continuation_target",
                        SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"),
                    ),
                    ("action_continuation_next_page", SafeHtml(f"<a href='{_e(next_href)}'>{_e(location)}</a>")),
                    (
                        "action_continuation_action_form_available",
                        "true" if action_form else "false",
                    ),
                    (
                        "action_continuation_confirmation_required",
                        "true" if action_form else "false",
                    ),
                    ("action_continuation_safety_boundary", "confirmed_local_action_only"),
                    ("action_continuation_write_on_get", "false"),
                    ("action_continuation_provider_calls_taken", "0"),
                    ("action_continuation_network_actions_taken", "0"),
                    ("action_continuation_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"action_continuation_now: {_e(_goal_operator_attention(phase, next_action))}",
                    f"action_continuation_click: <a href='{_e(next_action.href)}'>{_e(next_action.action)}</a>",
                    f"action_continuation_result_page: <a href='{_e(next_href)}'>{_e(location)}</a>",
                    "action_continuation_safety: confirmed local actions only",
                ]
            ),
            (
                "<details class='action-continuation-action' data-action-continuation-action='true'>"
                "<summary>Run Next Local Action</summary>"
                "<p class='muted'>This reuses the current Goal page action form. Confirmation is required before any local write.</p>"
                f"{action_form}"
                "</details>"
                if action_form
                else ""
            ),
            "</section>",
        ]
    )


def _action_result_rows(root: Path, result: Any) -> list[tuple[str, str | SafeHtml]]:
    rows = _flatten_action_result(root, "", result)
    if not rows:
        return [("result_fields", "none")]
    limit = 80
    if len(rows) > limit:
        return rows[:limit] + [("result_fields_truncated", str(len(rows) - limit))]
    return rows


def _flatten_action_result(
    root: Path,
    prefix: str,
    value: Any,
) -> list[tuple[str, str | SafeHtml]]:
    if is_dataclass(value) and not isinstance(value, type):
        rows: list[tuple[str, str | SafeHtml]] = []
        for field in fields(value):
            key = f"{prefix}.{field.name}" if prefix else field.name
            rows.extend(_flatten_action_result(root, key, getattr(value, field.name)))
        return rows
    if isinstance(value, dict):
        rows = []
        for key, nested in value.items():
            field_key = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten_action_result(root, field_key, nested))
        return rows
    key = prefix or "result"
    if isinstance(value, Path):
        return [(key, _artifact_link(_repo_relative_artifact_path(root, value)))]
    if isinstance(value, (list, tuple, set)):
        rendered = ", ".join(str(item) for item in value) if value else "none"
        return [(key, rendered)]
    if isinstance(value, bool):
        return [(key, str(value).lower())]
    if value is None:
        return [(key, "none")]
    if key.endswith("_path") or key.endswith("_artifact_path"):
        return [(key, _artifact_link(_repo_relative_artifact_path(root, str(value))))]
    return [(key, str(value))]


def _run_action_forms(root: Path, run_id: str) -> str:
    coder_run = next(
        (item for item in list_coder_worktree_runs(root, limit=50) if item.id == run_id),
        None,
    )
    review_gate = (
        _run_review_gate_state(root, coder_run)
        if coder_run is not None
        else {
            "status": "run_missing",
            "blocked_reason": "coder_worktree_run_not_found",
            "commit_request_form_available": False,
        }
    )
    commit_approvals = [
        item
        for item in list_coder_worktree_commit_approvals(root, limit=50)
        if item.run_id == run_id
    ]
    publications = [
        item
        for item in list_coder_publications(root, limit=50)
        if item.run_id == run_id
    ]
    pending_commit = [item for item in commit_approvals if item.status == "pending_operator_approval"]
    approved_commit = [item for item in commit_approvals if item.status == "approved"]
    committed = [item for item in commit_approvals if item.status == "committed"]
    pending_publication = [
        item for item in publications if item.status == "pending_operator_approval"
    ]
    approved_publication = [item for item in publications if item.status == "approved"]
    ready_publication = [
        item for item in publications if item.status == "ready_for_operator"
    ]
    sections: list[str] = [
        "<section id='run-approval-actions'><h2>Run Approval Actions</h2>",
        "<p class='muted'>These forms create local approval/request artifacts only. They do not stage, commit, push, create PRs, deploy, call providers, or use the network.</p>",
    ]
    if not commit_approvals:
        if review_gate["commit_request_form_available"]:
            sections.append(
                _input_form(
                    "coder-commit-request",
                    {"run_id": run_id, "requested_by": "operator"},
                    {
                        "message": "Implement bounded change from approved worktree run",
                        "note": "Request local commit after review",
                    },
                )
            )
        else:
            sections.append(
                "<p class='muted'>commit_request_form_available: false "
                f"review_gate_status: {_e(review_gate['status'])} "
                f"blocked_reason: {_e(review_gate['blocked_reason'])}</p>"
            )
    elif pending_commit:
        sections.append(
            f"<p class='muted'>commit_request_pending: {_e(pending_commit[0].id)}</p>"
        )
    elif approved_commit:
        sections.append(
            f"<p class='muted'>commit_request_approved: {_e(approved_commit[0].id)}</p>"
        )
    elif committed:
        sections.append(
            f"<p class='muted'>local_commit_recorded: {_e(committed[0].commit_sha or 'unknown')}</p>"
        )
    if committed and not publications:
        sections.extend(
            [
                "<h3>Publication Request Action</h3>",
                "<p class='muted'>This writes a local publication approval request. It does not push, create a PR, deploy, call providers, or use the network.</p>",
                _input_form(
                    "coder-publication-request",
                    {
                        "run_id": run_id,
                        "requested_by": "operator",
                        "remote": "origin",
                        "target_branch": "main",
                    },
                    {"note": "Request publication handoff"},
                ),
            ]
        )
    elif pending_publication:
        sections.append(
            f"<p class='muted'>publication_request_pending: {_e(pending_publication[0].id)}</p>"
        )
    elif approved_publication:
        sections.append(
            f"<p class='muted'>publication_request_approved: {_e(approved_publication[0].id)}</p>"
        )
    elif ready_publication:
        sections.append(
            "<p class='muted'>publication_handoff_ready: "
            f"{_artifact_link(ready_publication[0].handoff_artifact_path)}</p>"
        )
        sections.append(_publication_handoff_commands_panel(root, ready_publication[0]))
    sections.append("</section>")
    if approved_commit:
        sections.extend(
            [
                "<section id='confirmed-local-commit-action'><h2>Confirmed Local Commit Action</h2>",
                "<p class='muted'>This creates one local commit only inside the isolated coder worktree after the existing commit gate re-checks review, source hashes, branch/HEAD, changed files, bounded-file validation, and verifier state. It does not push, create PRs, deploy, call providers, or use the network.</p>",
                _input_form(
                    "commit-coder-worktree",
                    {"run_id": run_id, "committed_by": "operator"},
                    {"message": "Implement bounded change from approved worktree run"},
                ),
                "</section>",
            ]
        )
    if approved_publication:
        sections.extend(
            [
                "<section id='publication-handoff-action'><h2>Publication Handoff Action</h2>",
                "<p class='muted'>This writes local publication handoff and PR-body artifacts with suggested manual commands only. It does not push, create a PR, deploy, call providers, or use the network.</p>",
                _form("coder-publication-handoff", {"run_id": run_id}),
                "</section>",
            ]
        )
    return "".join(sections)


def _publication_handoff_commands_panel(root: Path, publication: Any) -> str:
    payload = load_coder_publication_handoff_payload(root, publication)
    suggested_push = payload.get("suggested_push_command", "unavailable")
    suggested_pr = payload.get("suggested_draft_pr_command", "unavailable")
    pr_body_path = payload.get("pr_body_path", "unavailable")
    handoff_body_path = payload.get("handoff_body_path", pr_body_path)
    return _list_section(
        "Publication Handoff Commands",
        [
            "handoff_status: ready_for_operator",
            f"handoff_artifact: {_artifact_link(publication.handoff_artifact_path)}",
            f"suggested_push_command: {_e(suggested_push)}",
            f"suggested_draft_pr_command: {_e(suggested_pr)}",
            f"pr_body_path: {_artifact_link(str(pr_body_path)) if pr_body_path != 'unavailable' else 'unavailable'}",
            f"handoff_body_path: {_artifact_link(str(handoff_body_path)) if handoff_body_path != 'unavailable' else 'unavailable'}",
            "manual_boundary: outside_clankeros",
            "copy_only: true",
            "push_created=false pr_created=false deploy_created=false",
            "provider_calls_taken_by_clankeros: 0",
            "network_actions_taken: 0",
            "external_mutations_taken: 0",
        ],
        anchor_id="publication-handoff-commands",
    )


def _pending_approval_lines(root: Path) -> list[str]:
    lines: list[str] = []
    lines.extend(
        _approval_line(item)
        for item in list_coder_worktree_approvals(
            root,
            status="pending_operator_approval",
            limit=10,
        )
    )
    lines.extend(
        _commit_line(item)
        for item in list_coder_worktree_commit_approvals(
            root,
            status="pending_operator_approval",
            limit=10,
        )
    )
    lines.extend(
        _publication_line(root, item)
        for item in list_coder_publications(
            root,
            status="pending_operator_approval",
            limit=10,
        )
    )
    return lines


def _inbox_summary_lines(root: Path) -> list[str]:
    inbox = collect_inbox_items(root)
    return [
        f"inbox_items: {inbox['count']}",
        f"steering_reviews: {len(inbox['steering_reviews'])}",
        f"pending_approvals: {len(inbox['pending_approvals'])}",
        f"open_incidents: {len(inbox['open_incidents'])}",
        f"subagent_delegations: {len(inbox['subagent_delegations'])}",
        f"coder_worktree_approvals: {len(inbox['coder_worktree_approvals'])}",
        f"coder_worktree_runs: {len(inbox['coder_worktree_runs'])}",
        f"coder_worktree_commit_approvals: {len(inbox['coder_worktree_commit_approvals'])}",
        f"coder_worktree_commits: {len(inbox['coder_worktree_commits'])}",
        f"coder_publication_requests: {len(inbox['coder_publication_requests'])}",
        f"coder_publication_handoffs: {len(inbox['coder_publication_handoffs'])}",
    ]


def _worktree_approval_action_line(item: Any) -> str:
    return (
        f"{_approval_line(item)} "
        + _input_form(
            "approve-coder-worktree",
            {"approval_id": item.id, "decided_by": "operator"},
            {"note": "Approved bounded execution"},
        )
    )


def _commit_approval_action_line(item: Any) -> str:
    return (
        f"{_commit_line(item)} request={_artifact_link(item.request_artifact_path)} "
        "<div><strong>Commit Approval Follow-Up</strong> "
        f"<a href='/runs/{quote(item.run_id)}'>run detail</a> "
        "follow_up_action_after_approval: commit-coder-worktree "
        "typed_commit_message_required: true "
        "push_created=false pr_created=false deploy_created=false</div>"
        + _input_form(
            "approve-coder-commit",
            {"approval_id": item.id, "decided_by": "operator"},
            {"note": "Approved local commit"},
        )
    )


def _publication_approval_action_line(root: Path, item: Any) -> str:
    return (
        f"{_publication_line(root, item)} request={_artifact_link(item.request_artifact_path)} "
        "<div><strong>Publication Approval Follow-Up</strong> "
        f"<a href='/runs/{quote(item.run_id)}'>run detail</a> "
        "follow_up_action_after_approval: coder-publication-handoff "
        "push_created=false pr_created=false deploy_created=false</div>"
        + _input_form(
            "approve-coder-publication",
            {"publication_id": item.id, "decided_by": "operator"},
            {"note": "Approved publication handoff preparation"},
        )
    )


def _commit_inbox_follow_up_line(item: Any) -> str:
    return (
        f"{_commit_line(item)} request={_artifact_link(item.request_artifact_path)} "
        "<div><strong>Commit Inbox Follow-Up</strong> "
        f"<a href='/runs/{quote(item.run_id)}'>run detail</a> "
        "<a href='/approvals'>approval queue</a> "
        "next_inbox_action_after_approval: commit-coder-worktree "
        "typed_commit_message_required: true "
        "push_created=false pr_created=false deploy_created=false</div>"
    )


def _publication_inbox_follow_up_line(root: Path, item: Any) -> str:
    return (
        f"{_publication_line(root, item)} request={_artifact_link(item.request_artifact_path)} "
        "<div><strong>Publication Inbox Follow-Up</strong> "
        f"<a href='/runs/{quote(item.run_id)}'>run detail</a> "
        "<a href='/approvals'>approval queue</a> "
        "next_inbox_action_after_approval: coder-publication-handoff "
        "push_created=false pr_created=false deploy_created=false</div>"
    )


def _steering_review_line(item: Any) -> str:
    return (
        f"{_e(item.id)}: status={_e(item.status)} goal={_e(item.goal_id)} "
        f"action={_e(item.recommended_next_action)} "
        f"requires_operator={str(item.requires_operator).lower()} "
        f"report={_artifact_link(item.report_path)}"
    )


def _operator_approval_line(item: Any) -> str:
    return (
        f"{_e(item.id)}: status={_e(item.status)} goal={_e(item.goal_id)} "
        f"run={_e(item.run_id or 'none')} task={_e(item.task_id)} "
        f"risk={_e(item.risk_level)} reason={_e(item.reason)}"
    )


def _incident_line(item: Any) -> str:
    return (
        f"{_e(item.id)}: status={_e(item.status)} project={_e(item.project_id)} "
        f"run={_e(item.run_id)} severity={_e(item.severity)} "
        f"summary={_e(item.summary)} evidence={_artifact_link(item.evidence_path or 'none')}"
    )


def _delegation_line(item: Any) -> str:
    return (
        f"<a href='/delegations/{quote(item.id)}'>{_e(item.id)}</a>: "
        f"status={_e(item.status)} profile={_e(item.assigned_profile)} "
        f"category={_e(item.category)} title={_e(item.title)}"
    )


def _form(action: str, fields: dict[str, str]) -> str:
    inputs = "".join(
        f"<input type='hidden' name='{_e(key)}' value='{_e(value)}'>"
        for key, value in fields.items()
    )
    return (
        f"<form method='post' action='/actions/{_e(action)}'>"
        f"{inputs}<button type='submit'>{_e(action)}</button></form>"
    )


def _input_form(
    action: str,
    hidden_fields: dict[str, str],
    text_fields: dict[str, str],
) -> str:
    inputs = "".join(
        f"<input type='hidden' name='{_e(key)}' value='{_e(value)}'>"
        for key, value in hidden_fields.items()
    )
    for key, value in text_fields.items():
        inputs += (
            f"<label>{_e(key)} "
            f"<input name='{_e(key)}' value='{_e(value)}'></label>"
        )
    return (
        f"<form method='post' action='/actions/{_e(action)}'>"
        f"{inputs}<button type='submit'>{_e(action)}</button></form>"
    )


def _confirm_form(action: str, form: dict[str, list[str]]) -> str:
    inputs = []
    for key, values in form.items():
        if key == "confirm":
            continue
        for value in values:
            inputs.append(f"<input type='hidden' name='{_e(key)}' value='{_e(value)}'>")
    inputs.append("<input type='hidden' name='confirm' value='yes'>")
    return "".join(
        [
            f"<section><h1>Confirm {_e(action)}</h1>",
            "<p>This action writes local ClankerOS artifacts only. It does not push, create PRs, deploy, call providers, or execute external mutations.</p>",
            _non_claim_banner(),
            "<h2>Action Payload</h2>",
            _kv(_submitted_form_rows(form)),
            f"<form method='post' action='/actions/{_e(action)}'>{''.join(inputs)}<button type='submit'>Confirm local action</button></form>",
            "</section>",
        ]
    )


def _submitted_form_rows(form: dict[str, list[str]]) -> list[tuple[str, str]]:
    rows = [
        (key, ", ".join(values) if values else "")
        for key, values in form.items()
        if key != "confirm"
    ]
    return rows or [("submitted_fields", "none")]


def _notice_banner(notice: str | None) -> str:
    if not notice:
        return ""
    trimmed = notice.strip()
    if not trimmed:
        return ""
    if len(trimmed) > 500:
        trimmed = trimmed[:500] + "... truncated"
    return (
        "<div class='banner'><strong>Action Notice</strong> "
        f"<span>{_e(trimmed)}</span></div>"
    )


def _nav_links(current_path: str) -> str:
    path = urlparse(current_path or "/").path or "/"
    links = []
    for label, href in NAV_ITEMS:
        current = _is_current_nav(path, href)
        aria = " aria-current='page'" if current else ""
        links.append(f"<a href='{_e(href)}'{aria}{_shortcut_attrs(label, href)}>{_e(label)}</a>")
    return "".join(links)


def _shortcut_attrs(label: str, href: str) -> str:
    shortcut = ROUTE_KEYBOARD_SHORTCUTS.get(href)
    if not shortcut:
        return ""
    return (
        f" data-shortcut='{_e(shortcut)}'"
        f" aria-keyshortcuts='{_e(shortcut)}'"
        f" title='{_e(label)} ({_e(shortcut)})'"
    )


def _is_current_nav(path: str, href: str) -> bool:
    if href == "/":
        return path == "/"
    return path == href or path.startswith(href + "/")


def _breadcrumbs(current_path: str, title: str) -> str:
    path = urlparse(current_path or "/").path or "/"
    crumbs: list[tuple[str, str | None]] = [("Dashboard", "/")]
    if path == "/":
        crumbs = [("Dashboard", None)]
    elif path.startswith("/goals/"):
        crumbs.extend([("Goals", "/goals"), (path.removeprefix("/goals/"), None)])
    elif path.startswith("/projects/"):
        crumbs.extend([("Projects", "/projects"), (path.removeprefix("/projects/"), None)])
    elif path.startswith("/delegations/"):
        crumbs.extend([("Delegations", "/delegation-runs"), (path.removeprefix("/delegations/"), None)])
    elif path.startswith("/runs/"):
        crumbs.extend([("Runs", "/delegation-runs"), (path.removeprefix("/runs/"), None)])
    elif path == "/artifacts":
        crumbs.append(("Artifact", None))
    else:
        label = next((label for label, href in NAV_ITEMS if href == path), title)
        crumbs.append((label, None))
    rendered = []
    for index, (label, href) in enumerate(crumbs):
        text = _compact_label(unquote(label), 48)
        if href and index < len(crumbs) - 1:
            rendered.append(f"<a href='{_e(href)}'>{_e(text)}</a>")
        else:
            rendered.append(f"<span>{_e(text)}</span>" if index else f"<strong>{_e(text)}</strong>")
    return "<nav class='breadcrumbs' aria-label='Breadcrumbs' data-breadcrumbs='true'>" + "".join(rendered) + "</nav>"


def _recent_items_panel(root: Path) -> str:
    items = _recent_operator_links(root, limit=8)
    used_defaults = not items
    if not items:
        items = [
            ("Goal cockpit", "/goals", "first-run"),
            ("Demo", "/demo", "fixture"),
            ("Verification", "/verification", "proof"),
        ]
    rows = [
        f"<li><a href='{_e(href)}'>{_e(label)}</a><br><span class='muted'>{_e(kind)}</span></li>"
        for label, href, kind in items
    ]
    body = "".join(
        [
            "<aside class='operator-side' data-recent-items='true'>",
            "<h2>Recent Items</h2>",
            _recent_items_command_bar(root, items, used_defaults=used_defaults),
            "<ul>",
            "".join(rows),
            "</ul>",
            "</aside>",
        ]
    )
    return body


def _recent_items_command_bar(
    root: Path,
    items: list[tuple[str, str, str]],
    *,
    used_defaults: bool,
) -> str:
    state = _load_workspace_state(root)
    open_project = str(state.get("open_project") or "").strip()
    open_goal = str(state.get("open_goal") or "").strip()
    last_artifact = str(state.get("last_viewed_artifact") or "").strip()
    primary_label, primary_href, primary_kind = items[0]
    workspace_count = sum(1 for _, _, kind in items if kind.startswith("workspace"))
    goal_count = sum(1 for _, _, kind in items if "goal" in kind)
    delegation_count = sum(1 for _, _, kind in items if kind == "delegation")
    run_count = sum(1 for _, _, kind in items if kind == "run")
    lines = [
        f"recent_items_now: Open {_e(primary_label)}",
        f"recent_items_click: <a href='{_e(primary_href)}'>{_e(primary_href)}</a>",
        "recent_items_resume: <a href='/resume'>/resume</a>",
        "recent_items_safety: read-only local navigation",
    ]
    return "".join(
        [
            "<section class='recent-items-command-bar' data-recent-items-command-bar='true'><h3>Recent Items Command Bar</h3>",
            _kv(
                [
                    ("recent_items_status", "first_run" if used_defaults else "available"),
                    ("recent_items_total", str(len(items))),
                    ("recent_items_workspace_items", str(workspace_count)),
                    ("recent_items_goal_items", str(goal_count)),
                    ("recent_items_delegation_items", str(delegation_count)),
                    ("recent_items_run_items", str(run_count)),
                    ("recent_items_primary_label", primary_label),
                    ("recent_items_primary_kind", primary_kind),
                    (
                        "recent_items_primary_surface",
                        SafeHtml(f"<a href='{_e(primary_href)}'>{_e(primary_href)}</a>"),
                    ),
                    ("recent_items_saved_project", open_project or "none"),
                    ("recent_items_saved_goal", open_goal or "none"),
                    ("recent_items_last_artifact", last_artifact or "none"),
                    ("recent_items_resume_surface", SafeHtml("<a href='/resume'>/resume</a>")),
                    ("recent_items_write_on_get", "false"),
                    ("recent_items_provider_calls_taken", "0"),
                    ("recent_items_network_actions_taken", "0"),
                    ("recent_items_external_effects_created", "false"),
                ]
            ),
            _ul(lines),
            "</section>",
        ]
    )


def _operator_focus_context(root: Path) -> dict[str, Any]:
    try:
        storage = _storage(root)
    except Exception:
        return {
            "status": "state_unavailable",
            "target_href": "/health",
            "target_label": "/health",
        }

    state = _load_workspace_state(root)
    saved_goal_id = str(state.get("open_goal") or "").strip()
    goal_state: dict[str, Any] | None = None
    source = ""
    if saved_goal_id:
        candidate = _goal_state(root, storage, saved_goal_id)
        if candidate.get("goal") is not None:
            goal_state = candidate
            source = "saved_goal"

    if goal_state is None:
        rows = _goal_rows(storage, limit=20)
        active = [row for row in rows if _goal_bucket(row) == "active"]
        lead = active[0] if active else (rows[0] if rows else None)
        if lead is not None:
            goal_state = _goal_state(root, storage, str(lead["id"]))
            source = "lead_goal"

    if goal_state is None or goal_state.get("goal") is None:
        return {
            "status": "no_goal",
            "target_href": "/goals",
            "target_label": "/goals",
        }

    goal = goal_state["goal"]
    phase = _goal_current_phase(goal_state)
    next_action = _goal_next_action(root, goal_state)
    action_form = _goal_next_action_form(goal_state, next_action)
    form_available = bool(action_form)
    open_incidents = sum(1 for row in goal_state["incidents"] if row["status"] == "open")
    open_recommendations = sum(
        1 for row in goal_state["recommendations"] if row["status"] == "open"
    )
    open_tasks = sum(
        1
        for task in goal_state["tasks"]
        if task.status not in {"completed", "cancelled"}
    )
    pending_approvals = (
        _count_status(goal_state["worktree_approvals"], "pending_operator_approval")
        + _count_status(goal_state["commit_approvals"], "pending_operator_approval")
        + _count_status(goal_state["publications"], "pending_operator_approval")
    )
    return {
        "status": "available",
        "source": source,
        "goal_state": goal_state,
        "goal": goal,
        "goal_label": _compact_label(goal.title or goal.description or goal.id, 72),
        "phase": phase,
        "next_action": next_action,
        "action_form": action_form,
        "form_available": form_available,
        "attention": _goal_operator_attention(phase, next_action),
        "progress": _goal_progress_label(goal_state),
        "open_tasks": open_tasks,
        "pending_approvals": pending_approvals,
        "open_incidents": open_incidents,
        "open_recommendations": open_recommendations,
        "waiting_items": open_incidents + open_recommendations + pending_approvals,
    }


def _operator_focus_strip(context: dict[str, Any]) -> str:
    status = str(context.get("status", "state_unavailable"))
    if status != "available":
        href = str(context.get("target_href") or "/health")
        label = str(context.get("target_label") or href)
        action = "Open goals" if status == "no_goal" else "Open health"
        return "".join(
            [
                "<section class='operator-focus-strip' data-operator-focus-strip='true'><h2>Operator Focus</h2>",
                _kv(
                    [
                        ("operator_focus_status", status),
                        ("operator_focus_primary_action", action),
                        (
                            "operator_focus_target",
                            SafeHtml(f"<a href='{_e(href)}'>{_e(label)}</a>"),
                        ),
                        ("operator_focus_action_form_available", "false"),
                        ("operator_focus_write_on_get", "false"),
                        ("operator_focus_provider_calls_taken", "0"),
                        ("operator_focus_network_actions_taken", "0"),
                        ("operator_focus_external_effects_created", "false"),
                    ]
                ),
                _ul(
                    [
                        f"operator_focus_now: {_e(action)}",
                        f"operator_focus_click: <a href='{_e(href)}'>{_e(label)}</a>",
                        "operator_focus_safety: read-only local navigation",
                    ]
                ),
                "</section>",
            ]
        )

    goal = context["goal"]
    next_action = context["next_action"]
    action_form = str(context.get("action_form") or "")
    return "".join(
        [
            "<section class='operator-focus-strip' data-operator-focus-strip='true'><h2>Operator Focus</h2>",
            _kv(
                [
                    ("operator_focus_status", "available"),
                    ("operator_focus_source", str(context["source"])),
                    (
                        "operator_focus_goal",
                        SafeHtml(
                            f"<a href='/goals/{quote(goal.id)}'>{_e(context['goal_label'])}</a>"
                        ),
                    ),
                    (
                        "operator_focus_project",
                        SafeHtml(
                            f"<a href='/projects/{quote(goal.project_id)}'>{_e(goal.project_id)}</a>"
                        ),
                    ),
                    ("operator_focus_phase", str(context["phase"])),
                    ("operator_focus_attention", str(context["attention"])),
                    ("operator_focus_primary_action", next_action.action),
                    (
                        "operator_focus_target",
                        SafeHtml(
                            f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>"
                        ),
                    ),
                    ("operator_focus_reason", next_action.reason),
                    ("operator_focus_progress", str(context["progress"])),
                    ("operator_focus_open_tasks", str(context["open_tasks"])),
                    ("operator_focus_waiting_items", str(context["waiting_items"])),
                    ("operator_focus_pending_approvals", str(context["pending_approvals"])),
                    ("operator_focus_open_incidents", str(context["open_incidents"])),
                    ("operator_focus_open_recommendations", str(context["open_recommendations"])),
                    (
                        "operator_focus_form_available",
                        "true" if context["form_available"] else "false",
                    ),
                    (
                        "operator_focus_action_form_available",
                        "true" if action_form else "false",
                    ),
                    (
                        "operator_focus_confirmation_required",
                        "true" if action_form else "false",
                    ),
                    ("operator_focus_safety_boundary", "confirmed_local_action_only"),
                    ("operator_focus_resume_surface", SafeHtml("<a href='/resume'>/resume</a>")),
                    ("operator_focus_write_on_get", "false"),
                    ("operator_focus_provider_calls_taken", "0"),
                    ("operator_focus_network_actions_taken", "0"),
                    ("operator_focus_external_effects_created", "false"),
                ]
            ),
            _ul(
                [
                    f"operator_focus_now: {_e(context['attention'])}",
                    f"operator_focus_click: <a href='{_e(next_action.href)}'>{_e(next_action.action)}</a>",
                    f"operator_focus_progress: {_e(context['progress'])}",
                    (
                        "operator_focus_waiting: "
                        f"approvals={_e(context['pending_approvals'])} "
                        f"incidents={_e(context['open_incidents'])} "
                        f"recommendations={_e(context['open_recommendations'])}"
                    ),
                    "operator_focus_resume: <a href='/resume'>/resume</a>",
                    "operator_focus_safety: read-only local navigation",
                ]
            ),
            (
                "<details class='operator-focus-action' data-operator-focus-action='true'>"
                "<summary>Run Current Action</summary>"
                "<p class='muted'>Use the current goal's browser-available local next action from this page. Confirmation is required before any local write.</p>"
                f"{action_form}"
                "</details>"
                if action_form
                else ""
            ),
            "</section>",
        ]
    )


def _command_palette(root: Path, focus_context: dict[str, Any]) -> str:
    commands = [(label, href, "route") for label, href in NAV_ITEMS]
    commands.extend(_recent_operator_links(root, limit=6))
    seen: set[str] = set()
    rows = []
    for label, href, kind in commands:
        key = f"{href}:{label}"
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            f"<li><a href='{_e(href)}'{_shortcut_attrs(label, href)}>{_e(label)}</a> "
            f"<span class='muted'>{_e(kind)}</span></li>"
        )
    return "".join(
        [
            "<dialog id='command-palette' class='command-palette' data-command-palette='true'>",
            "<form method='dialog'><button class='icon-button' type='submit'>Close</button></form>",
            "<h2>Command Palette</h2>",
            _command_palette_continue(focus_context),
            "<form action='/search' method='get' class='command-grid'>",
            "<input id='command-palette-search' name='q' autocomplete='off' placeholder='Search local state'>",
            "<button type='submit'>Search</button>",
            "</form>",
            "<h3>Keyboard Shortcuts</h3>",
            _shortcut_help_list(),
            "<h3>Open</h3>",
            "<ul>",
            "".join(rows),
            "</ul>",
            "</dialog>",
        ]
    )


def _shortcut_help_list() -> str:
    rows = [
        f"<li><kbd>{_e(key)}</kbd> <span>{_e(description)}</span></li>"
        for key, description in GLOBAL_KEYBOARD_SHORTCUTS.items()
    ]
    return "<ul class='shortcut-list' data-shortcut-help='true'>" + "".join(rows) + "</ul>"


def _command_palette_continue(focus_context: dict[str, Any]) -> str:
    status = str(focus_context.get("status", "state_unavailable"))
    if status == "state_unavailable":
        return "".join(
            [
                "<section class='palette-continue' data-command-palette-continue='true'>",
                "<h3>Continue Current Goal</h3>",
                _kv(
                    [
                        ("palette_continue_status", "state_unavailable"),
                        ("palette_continue_target", SafeHtml("<a href='/health'>/health</a>")),
                        ("palette_continue_action_form_available", "false"),
                        ("palette_continue_write_on_get", "false"),
                        ("palette_continue_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )

    if status == "no_goal":
        return "".join(
            [
                "<section class='palette-continue' data-command-palette-continue='true'>",
                "<h3>Continue Current Goal</h3>",
                _kv(
                    [
                        ("palette_continue_status", "no_goal"),
                        ("palette_continue_target", SafeHtml("<a href='/goals'>/goals</a>")),
                        ("palette_continue_action_form_available", "false"),
                        ("palette_continue_write_on_get", "false"),
                        ("palette_continue_external_effects_created", "false"),
                    ]
                ),
                "</section>",
            ]
        )

    goal = focus_context["goal"]
    next_action = focus_context["next_action"]
    action_form = str(focus_context.get("action_form") or "")
    return "".join(
        [
            "<section class='palette-continue' data-command-palette-continue='true'>",
            "<h3>Continue Current Goal</h3>",
            _kv(
                [
                    ("palette_continue_status", "available"),
                    ("palette_continue_source", str(focus_context["source"])),
                    (
                        "palette_continue_goal",
                        SafeHtml(
                            f"<a href='/goals/{quote(goal.id)}'>{_e(focus_context['goal_label'])}</a>"
                        ),
                    ),
                    ("palette_continue_phase", str(focus_context["phase"])),
                    ("palette_continue_next_action", next_action.action),
                    ("palette_continue_target", SafeHtml(f"<a href='{_e(next_action.href)}'>{_e(next_action.href)}</a>")),
                    (
                        "palette_continue_form_available",
                        "true" if focus_context["form_available"] else "false",
                    ),
                    (
                        "palette_continue_action_form_available",
                        "true" if action_form else "false",
                    ),
                    (
                        "palette_continue_confirmation_required",
                        "true" if action_form else "false",
                    ),
                    ("palette_continue_safety_boundary", "confirmed_local_action_only"),
                    ("palette_continue_write_on_get", "false"),
                    ("palette_continue_provider_calls_taken", "0"),
                    ("palette_continue_network_actions_taken", "0"),
                    ("palette_continue_external_effects_created", "false"),
                ]
            ),
            (
                "<h4>Continue Action Form</h4>"
                "<p class='muted'>Run the current goal's browser-available local next action without leaving the palette. Confirmation is still required before any local write.</p>"
                f"{action_form}"
                if action_form
                else ""
            ),
            "</section>",
        ]
    )


def _recent_operator_links(root: Path, *, limit: int) -> list[tuple[str, str, str]]:
    links: list[tuple[str, str, str]] = []
    state = _load_workspace_state(root)
    open_project = str(state.get("open_project") or "").strip()
    open_goal = str(state.get("open_goal") or "").strip()
    last_artifact = str(state.get("last_viewed_artifact") or "").strip()
    if any([open_goal, open_project, last_artifact]):
        links.append(("Resume workspace", "/resume", "workspace"))
    if open_goal:
        links.append((f"Goal {open_goal}", f"/goals/{quote(open_goal)}", "workspace goal"))
    if open_project:
        links.append((f"Project {open_project}", f"/projects/{quote(open_project)}", "workspace project"))
    if last_artifact:
        links.append(("Last artifact", f"/artifacts?path={quote(last_artifact)}", "workspace artifact"))

    try:
        storage = _storage(root)
        for row in _goal_rows(storage, limit=3):
            label = str(row["title"] or row["description"] or row["id"])
            links.append((label, f"/goals/{quote(str(row['id']))}", "goal"))
        for delegation in storage.list_recent_subagent_delegations(limit=3):
            links.append((delegation.title or delegation.id, f"/delegations/{quote(delegation.id)}", "delegation"))
        for run in list_coder_worktree_runs(root, limit=3):
            links.append((run.id, f"/runs/{quote(run.id)}", "run"))
    except Exception:
        links.append(("Health", "/health", "state unavailable"))

    deduped: list[tuple[str, str, str]] = []
    seen_hrefs: set[str] = set()
    for label, href, kind in links:
        if href in seen_hrefs:
            continue
        seen_hrefs.add(href)
        deduped.append((_compact_label(label, 72), href, kind))
        if len(deduped) >= limit:
            break
    return deduped


def _compact_label(value: str, limit: int) -> str:
    collapsed = " ".join(str(value).split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: max(0, limit - 3)] + "..."


def _html_page(
    root: Path,
    title: str,
    content: str,
    *,
    status: int = 200,
    current_path: str = "",
) -> LocalAppResponse:
    current_path = current_path or "/"
    nav = _nav_links(current_path)
    breadcrumbs = _breadcrumbs(current_path, title)
    recent_panel = _recent_items_panel(root)
    focus_context = _operator_focus_context(root)
    focus_strip = _operator_focus_strip(focus_context)
    palette = _command_palette(root, focus_context)
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_e(title)} - ClankerOS Local Operator</title>
  <style>
    :root {{ color-scheme: light; --ink:#15171a; --muted:#5d6672; --line:#d9dee5; --panel:#f7f8fa; --surface:#ffffff; --accent:#176b87; --ok:#2e7d32; --warn:#8a4b00; --error:#9c1d24; }}
    :root[data-theme="dark"] {{ color-scheme: dark; --ink:#eef4f8; --muted:#a6b0bd; --line:#303842; --panel:#161b22; --surface:#0f1419; --accent:#62b6cb; --ok:#7bd88f; --warn:#f0bd59; --error:#ff8a94; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:var(--surface); line-height:1.45; }}
    header {{ display:flex; justify-content:space-between; align-items:center; gap:16px; padding:14px 24px; border-bottom:1px solid var(--line); background:var(--surface); position:sticky; top:0; z-index:2; }}
    header a {{ color:var(--ink); text-decoration:none; font-size:14px; margin-right:14px; }}
    header a[aria-current="page"] {{ color:var(--accent); font-weight:700; }}
    .header-actions {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
    .icon-button {{ border:1px solid var(--line); background:var(--panel); color:var(--ink); padding:7px 9px; border-radius:6px; }}
    main {{ max-width:1280px; margin:0 auto; padding:24px; }}
    .operator-shell {{ display:grid; grid-template-columns:minmax(180px, 240px) minmax(0, 1fr); gap:24px; align-items:start; }}
    .operator-side {{ position:sticky; top:74px; border:1px solid var(--line); background:var(--panel); padding:12px; }}
    .operator-side h2 {{ font-size:14px; }}
    .operator-side ul, .command-palette ul {{ list-style:none; padding:0; margin:0; display:grid; gap:7px; }}
    .operator-side li, .command-palette li {{ min-width:0; }}
    .operator-side a, .command-palette a {{ overflow-wrap:anywhere; }}
    .recent-items-command-bar {{ border:1px solid var(--line); border-left:4px solid var(--accent); background:var(--surface); padding:9px; margin:10px 0; }}
    .recent-items-command-bar h3 {{ margin-top:0; }}
    .recent-items-command-bar dl {{ grid-template-columns:1fr; gap:4px; }}
    .recent-items-command-bar ul {{ margin-top:8px; }}
    .recent-items-command-bar li {{ border:1px solid var(--line); background:var(--panel); padding:6px 7px; overflow-wrap:anywhere; }}
    .palette-continue {{ border:1px solid var(--line); background:var(--panel); padding:10px; margin:10px 0; }}
    .breadcrumbs {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; color:var(--muted); margin:0 0 14px; font-size:13px; }}
    .breadcrumbs a {{ color:var(--muted); }}
    .breadcrumbs span::before {{ content:"/"; margin-right:6px; color:var(--line); }}
    .operator-focus-strip {{ border:1px solid var(--line); border-left:4px solid var(--accent); background:var(--panel); padding:12px; margin:0 0 16px; }}
    .operator-focus-strip dl {{ grid-template-columns:minmax(170px, 230px) 1fr; }}
    .operator-focus-strip ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:8px; }}
    .operator-focus-strip li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .operator-focus-action {{ margin-top:12px; border:1px solid var(--line); background:var(--surface); padding:10px; }}
    .operator-focus-action summary {{ cursor:pointer; font-weight:700; }}
    .operator-focus-action form {{ margin-top:10px; }}
    .action-continuation {{ border:1px solid var(--line); background:var(--panel); padding:14px; margin:16px 0; }}
    .action-continuation-action {{ margin-top:12px; border:1px solid var(--line); background:var(--surface); padding:10px; }}
    .action-continuation-action summary {{ cursor:pointer; font-weight:700; }}
    .action-continuation-action form {{ margin-top:10px; }}
    section {{ border-bottom:1px solid var(--line); padding:20px 0; }}
    h1 {{ font-size:30px; line-height:1.15; margin:0 0 10px; letter-spacing:0; }}
    h2 {{ font-size:18px; margin:0 0 12px; letter-spacing:0; }}
    h3 {{ font-size:15px; margin:16px 0 6px; }}
    p, li, dd, dt, td, th, button, input {{ font-size:14px; }}
    .hero p {{ color:var(--muted); max-width:760px; }}
    .banner, .warning {{ border:1px solid var(--line); background:var(--panel); padding:12px; margin:12px 0; }}
    .panel {{ border:1px solid var(--line); background:var(--panel); padding:12px; }}
    .goal-command-bar {{ border-left:4px solid var(--accent); }}
    .goal-command-bar dl {{ grid-template-columns:minmax(180px, 240px) 1fr; }}
    .goal-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:8px; }}
    .goal-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-board-command-bar {{ border-left:4px solid var(--accent); }}
    .goal-board-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-board-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-delegation-command-bar {{ border-left:4px solid var(--accent); }}
    .goal-delegation-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-delegation-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-run-command-bar {{ border-left:4px solid var(--accent); }}
    .goal-run-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-run-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-approval-command-bar {{ border-left:4px solid var(--warn); }}
    .goal-approval-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-approval-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-git-command-bar {{ border-left:4px solid var(--accent); }}
    .goal-git-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-git-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-evidence-command-bar {{ border-left:4px solid var(--ok); }}
    .goal-evidence-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-evidence-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-verification-command-bar {{ border-left:4px solid var(--ok); }}
    .goal-verification-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-verification-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-completion-readiness {{ border-left:4px solid var(--ok); }}
    .goal-completion-readiness ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-completion-readiness li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .completion-readiness-action {{ margin-top:12px; border:1px solid var(--line); background:var(--surface); padding:10px; }}
    .completion-readiness-action summary {{ cursor:pointer; font-weight:700; }}
    .completion-readiness-action form {{ margin-top:10px; }}
    .goal-daily-loop {{ border-left:4px solid var(--ok); }}
    .goal-daily-loop dl {{ grid-template-columns:minmax(180px, 240px) 1fr; }}
    .goal-daily-loop ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-daily-loop li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .workspace-daily-brief {{ border-left:4px solid var(--accent); }}
    .workspace-daily-brief ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .workspace-daily-brief li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .home-attention-brief {{ border-left:4px solid var(--warn); }}
    .home-attention-brief ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .home-attention-brief li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .project-command-bar {{ border-left:4px solid var(--accent); }}
    .project-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .project-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .run-command-bar {{ border-left:4px solid var(--warn); }}
    .run-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .run-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .delegation-run-command-bar {{ border-left:4px solid var(--accent); }}
    .delegation-run-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .delegation-run-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .verification-command-bar {{ border-left:4px solid var(--accent); }}
    .verification-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .verification-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .ci-evidence-command-bar {{ border-left:4px solid var(--ok); }}
    .ci-evidence-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .ci-evidence-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .artifact-command-bar {{ border-left:4px solid var(--accent); }}
    .artifact-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .artifact-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .artifact-review-brief {{ border-left:4px solid var(--ok); }}
    .artifact-review-brief ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .artifact-review-brief li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .goal-timeline-command-bar {{ border-left:4px solid var(--accent); margin:0 0 12px; }}
    .goal-timeline-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .goal-timeline-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .workflow-map-rail {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(180px, 1fr)); gap:8px; }}
    .workflow-map-rail li {{ min-width:0; border:1px solid var(--line); background:var(--surface); padding:8px 9px; overflow-wrap:anywhere; }}
    .workflow-map-rail li[data-gate-marker="current"] {{ border-color:var(--accent); box-shadow:inset 3px 0 0 var(--accent); }}
    .workflow-map-index {{ display:inline-grid; place-items:center; width:22px; height:22px; border:1px solid var(--line); border-radius:999px; margin-right:5px; font-size:12px; color:var(--muted); }}
    .search-command-bar {{ border-left:4px solid var(--ok); }}
    .search-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .search-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .memory-command-bar {{ border-left:4px solid var(--ok); }}
    .memory-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .memory-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .skills-command-bar {{ border-left:4px solid var(--accent); }}
    .skills-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .skills-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .profiles-command-bar {{ border-left:4px solid var(--warn); }}
    .profiles-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .profiles-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .inbox-command-bar {{ border-left:4px solid var(--accent); }}
    .inbox-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .inbox-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .approval-queue-command-bar {{ border-left:4px solid var(--warn); }}
    .approval-queue-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .approval-queue-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .approval-decision-brief {{ border-left:4px solid var(--warn); }}
    .approval-decision-brief[data-approval-decision-status="empty"] {{ border-left-color:var(--ok); }}
    .approval-decision-brief ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .approval-decision-brief li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .incident-command-bar {{ border-left:4px solid var(--error); }}
    .incident-command-bar ul {{ list-style:none; padding:0; margin:12px 0 0; display:grid; grid-template-columns:repeat(auto-fit, minmax(240px, 1fr)); gap:8px; }}
    .incident-command-bar li {{ min-width:0; padding:8px 10px; border:1px solid var(--line); background:var(--surface); overflow-wrap:anywhere; }}
    .warning {{ border-color:#efc36a; color:var(--warn); }}
    .error {{ color:var(--error); font-weight:600; }}
    .muted {{ color:var(--muted); }}
    dl {{ display:grid; grid-template-columns:minmax(170px, 260px) 1fr; gap:8px 16px; }}
    dt {{ color:var(--muted); }}
    dd {{ margin:0; word-break:break-word; }}
    ol.workflow {{ list-style:none; padding:0; display:grid; gap:10px; }}
    ol.workflow li {{ border:1px solid var(--line); padding:12px; background:var(--surface); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:12px; }}
    a {{ color:var(--accent); }}
    progress {{ width:100%; max-width:420px; height:14px; accent-color:var(--accent); }}
    .timeline-link {{ display:inline-block; }}
    .command-palette {{ border:1px solid var(--line); background:var(--surface); color:var(--ink); max-width:720px; width:min(720px, calc(100vw - 32px)); }}
    .command-palette::backdrop {{ background:rgba(15,20,25,.45); }}
    .command-grid {{ display:grid; grid-template-columns:1fr auto; gap:8px; }}
    .shortcut-list kbd {{ display:inline-block; min-width:52px; border:1px solid var(--line); border-bottom-width:2px; border-radius:5px; padding:2px 6px; background:var(--panel); color:var(--ink); font-family:ui-monospace, SFMono-Regular, Menlo, monospace; font-size:12px; }}
    .sr-only {{ position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }}
    input {{ border:1px solid var(--line); background:var(--surface); color:var(--ink); padding:7px 9px; border-radius:6px; width:100%; }}
    pre {{ overflow:auto; padding:14px; background:#0f1419; color:#eef4f8; border-radius:6px; font-size:13px; line-height:1.4; }}
    button {{ border:1px solid var(--accent); background:var(--accent); color:white; padding:7px 10px; border-radius:6px; margin:3px 0; cursor:pointer; }}
    @media (max-width: 860px) {{ header {{ align-items:flex-start; flex-direction:column; }} .operator-shell {{ grid-template-columns:1fr; }} .operator-side {{ position:static; }} dl {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <header>
    <strong>ClankerOS Local Operator</strong>
    <nav>{nav}</nav>
    <div class="header-actions" data-keyboard-shortcuts="true">
      <span class="sr-only" id="keyboard-shortcuts-help">Keyboard shortcuts: slash opens command palette; Escape closes it; h opens home; g opens goals; r opens resume; s opens search; t toggles theme.</span>
      <button class="icon-button" id="palette-open" type="button" data-shortcut="/" aria-keyshortcuts="/" aria-describedby="keyboard-shortcuts-help" title="Open command palette (/)">Palette</button>
      <button class="icon-button" id="theme-toggle" type="button" data-shortcut="t" aria-keyshortcuts="t" aria-describedby="keyboard-shortcuts-help" title="Toggle theme (t)">Theme</button>
    </div>
  </header>
  {palette}
  <main>
    <div class="operator-shell" data-operator-shell="true">
      {recent_panel}
      <article>
        {breadcrumbs}
        {focus_strip}
        {content}
      </article>
    </div>
  </main>
  <script>
  (function() {{
    var root = document.documentElement;
    var storedTheme = window.localStorage ? localStorage.getItem("clankeros-theme") : "";
    if (storedTheme === "dark") {{ root.dataset.theme = "dark"; }}
    var palette = document.getElementById("command-palette");
    var paletteOpen = document.getElementById("palette-open");
    var paletteSearch = document.getElementById("command-palette-search");
    var themeToggle = document.getElementById("theme-toggle");
    function openPalette() {{
      if (!palette) {{ return; }}
      if (palette.showModal) {{ palette.showModal(); }} else {{ palette.removeAttribute("hidden"); }}
      if (paletteSearch) {{ paletteSearch.focus(); }}
    }}
    function closePalette() {{
      if (!palette) {{ return; }}
      if (palette.close) {{ palette.close(); }} else {{ palette.setAttribute("hidden", "hidden"); }}
    }}
    function toggleTheme() {{
      var next = root.dataset.theme === "dark" ? "" : "dark";
      root.dataset.theme = next;
      if (window.localStorage) {{ localStorage.setItem("clankeros-theme", next); }}
    }}
    if (paletteOpen) {{ paletteOpen.addEventListener("click", openPalette); }}
    if (themeToggle) {{ themeToggle.addEventListener("click", toggleTheme); }}
    document.addEventListener("keydown", function(event) {{
      var target = event.target || {{}};
      var tag = String(target.tagName || "").toLowerCase();
      if (event.defaultPrevented || event.metaKey || event.ctrlKey || event.altKey) {{ return; }}
      if (event.key === "Escape") {{ closePalette(); return; }}
      if (tag === "input" || tag === "textarea" || tag === "select") {{ return; }}
      if (event.key === "/") {{ event.preventDefault(); openPalette(); }}
      if (event.key === "g") {{ event.preventDefault(); window.location.href = "/goals"; }}
      if (event.key === "h") {{ event.preventDefault(); window.location.href = "/"; }}
      if (event.key === "r") {{ event.preventDefault(); window.location.href = "/resume"; }}
      if (event.key === "s") {{ event.preventDefault(); window.location.href = "/search"; }}
      if (event.key === "t") {{ event.preventDefault(); toggleTheme(); }}
    }});
  }})();
  </script>
</body>
</html>"""
    return LocalAppResponse(status, body)


def _send_response(handler: BaseHTTPRequestHandler, response: LocalAppResponse) -> None:
    handler.send_response(response.status)
    handler.send_header("content-type", response.content_type)
    for key, value in (response.headers or {}).items():
        handler.send_header(key, value)
    handler.end_headers()
    if response.body:
        handler.wfile.write(response.body.encode("utf-8"))


def _repo_state(root: Path) -> dict[str, Any]:
    root = root.resolve()
    branch = _git(root, ["branch", "--show-current"]) or "unknown"
    commit = _git(root, ["rev-parse", "--short=12", "HEAD"]) or "unknown"
    status_lines = (_git(root, ["status", "--short"]) or "").splitlines()
    dirty_tracked = [line for line in status_lines if not line.startswith("?? ")]
    untracked = [line[3:] for line in status_lines if line.startswith("?? ")]
    ahead = False
    if _git(root, ["rev-parse", "--verify", "origin/main"]):
        count = _git(root, ["rev-list", "--count", "origin/main..HEAD"])
        ahead = bool(count and count.strip() != "0")
    return {
        "branch": branch,
        "commit": commit,
        "dirty_tracked_files": dirty_tracked,
        "untracked_files": untracked,
        "ahead_of_origin_main": ahead,
    }


def _git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _storage(root: Path) -> Storage:
    storage = Storage(root.resolve() / ".agent" / "state.db")
    storage.initialize()
    return storage


def _summary_rows(root: Path, storage: Storage) -> dict[str, list[str]]:
    projects = [
        f"<a href='/projects/{quote(project.name)}'>{_e(project.name)}</a> - {_e(project.root_path)}"
        for project in storage.list_registered_projects()[:10]
    ]
    goals = [
        f"<a href='/goals/{quote(str(row['id']))}'>{_e(row['id'])}</a>: {row['status']} {_e(row['description'])}"
        for row in _table_rows(storage.db_path, "select id, status, description from goals order by updated_at desc limit 10")
    ]
    tasks = [
        f"{row['id']}: {row['status']} {row['task_type']} - {_e(row['description'])}"
        for row in _table_rows(storage.db_path, "select id, status, task_type, description from tasks order by updated_at desc limit 10")
    ]
    delegations = [
        f"<a href='/delegations/{quote(item.id)}'>{_e(item.id)}</a>: {item.status} {item.title}"
        for item in storage.list_recent_subagent_delegations(limit=10)
    ]
    return {
        "projects": projects,
        "goals": goals,
        "tasks": tasks,
        "delegations": delegations,
        "delegation_runs": _delegation_run_lines(root, storage, limit=10),
        "implementation_handoffs": _implementation_handoff_lines(root, storage, limit=10),
        "coder_runs": [
            _coder_run_line(root, item)
            for item in list_coder_worktree_runs(root, limit=10)
        ],
        "commit_requests": [_commit_line(item) for item in list_coder_worktree_commit_approvals(root, limit=10)],
        "publication_requests": [_publication_line(root, item) for item in list_coder_publications(root, limit=10)],
        "publication_handoffs": [
            _publication_line(root, item)
            for item in list_coder_publications(root, status="ready_for_operator", limit=10)
        ],
        "inbox": _inbox_summary_lines(root),
        "approvals": _pending_approval_lines(root),
        "incidents": [
            f"{row['id']}: {row['status']} {row['summary']}"
            for row in _table_rows(storage.db_path, "select id, status, summary from incidents order by created_at desc limit 10")
        ],
    }


def _table_rows(db_path: Path, query: str, params: tuple[object, ...] = ()) -> list[sqlite3.Row]:
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        try:
            return list(connection.execute(query, params).fetchall())
        except sqlite3.OperationalError:
            return []


def _implementation_handoff_lines(
    root: Path,
    storage: Storage,
    *,
    project_id: str | None = None,
    limit: int = 10,
) -> list[str]:
    lines: list[str] = []
    for delegation in storage.list_recent_subagent_delegations(limit=None):
        if project_id and _task_project(storage, delegation.parent_task_id) != project_id:
            continue
        summary = summarize_implementation_handoff(root, delegation)
        if summary["handoff_path"] == "none":
            continue
        lines.append(
            f"<a href='/delegations/{quote(delegation.id)}'>{_e(delegation.id)}</a>: "
            f"status={_e(str(summary['status']))} "
            f"project={_e(str(summary['project_id']))} "
            f"kind_valid={_e(str(summary['kind_valid']).lower())} "
            f"handoff={_artifact_link(summary['handoff_path'])} "
            f"markdown={_artifact_link(summary['markdown_path'])} "
            "<code>python3 -m agent_os.cli coder-prep-from-handoff "
            f"{_e(str(summary['markdown_path']))}</code>"
        )
        if len(lines) >= limit:
            break
    return lines


def _delegation_run_lines(
    root: Path,
    storage: Storage,
    *,
    project_id: str | None = None,
    limit: int = 10,
) -> list[str]:
    return [
        _delegation_run_line(root, storage, delegation, project_id=project)
        for delegation, project, _metadata in _delegation_run_records(
            root,
            storage,
            project_id=project_id,
            limit=limit,
        )
    ]


def _delegation_run_records(
    root: Path,
    storage: Storage,
    *,
    project_id: str | None = None,
    limit: int = 10,
) -> list[tuple[Any, str, dict[str, Any]]]:
    records: list[tuple[Any, str, dict[str, Any]]] = []
    for delegation in storage.list_recent_subagent_delegations(limit=None):
        metadata = load_delegation_result_metadata(delegation)
        project = str(
            metadata.get("target_project_id")
            or _task_project(storage, delegation.parent_task_id)
        )
        if project_id and project != project_id:
            continue
        records.append((delegation, project, metadata))
        if len(records) >= limit:
            break
    return records


def _delegation_run_line(
    root: Path,
    storage: Storage,
    delegation: Any,
    *,
    project_id: str,
) -> str:
    metadata = load_delegation_result_metadata(delegation)
    run_id = metadata.get("execution_run_id") or metadata.get("run_id") or "none"
    evidence_dir = metadata.get("execution_evidence_dir") or metadata.get("evidence_dir") or "none"
    context_pack = metadata.get("context_pack_md") or metadata.get("context_pack_json") or "none"
    implementation_handoff = (
        metadata.get("implementation_handoff_md")
        or metadata.get("implementation_handoff_json")
        or "none"
    )
    result_artifact = _repo_relative_artifact_path(root, delegation.result_artifact_path)
    provider_calls = metadata.get("provider_calls_taken_by_clankeros", "unknown")
    network_actions = metadata.get("network_actions_taken", "unknown")
    external_mutations = metadata.get("external_mutations_taken", "unknown")
    incident_id = metadata.get("incident_id") or "none"
    retry_candidate = str(delegation.status != "completed" or incident_id != "none").lower()
    next_action = _delegation_run_next_action(delegation, metadata)
    run_link: SafeHtml | str = (
        SafeHtml(f"<a href='/runs/{quote(str(run_id))}'>{_e(run_id)}</a>")
        if run_id != "none"
        else "none"
    )
    source_review_path = root / "runs" / str(run_id) / "review.md"
    review_link: SafeHtml | str = (
        _artifact_link(str(source_review_path.relative_to(root)))
        if run_id != "none" and source_review_path.exists()
        else "none"
    )
    return (
        f"<a href='/delegations/{quote(delegation.id)}'>{_e(delegation.id)}</a>: "
        f"status={_e(delegation.status)} run_id={run_link} "
        f"project={_e(project_id)} profile={_e(delegation.assigned_profile)} "
        f"category={_e(delegation.category)} "
        f"evidence_dir={_e(evidence_dir)} "
        f"result_artifact={_artifact_link(result_artifact)} "
        f"context_pack={_artifact_link(str(context_pack))} "
        f"implementation_handoff={_artifact_link(str(implementation_handoff))} "
        f"source_review={review_link} "
        f"provider_calls_taken_by_clankeros={_e(provider_calls)} "
        f"network_actions_taken={_e(network_actions)} "
        f"external_mutations_taken={_e(external_mutations)} "
        f"incident={_e(incident_id)} retry_candidate={retry_candidate} "
        f"next_recommended_action={_e(next_action)}"
    )


def _delegation_run_next_action(delegation: Any, metadata: dict[str, Any]) -> str:
    if metadata.get("incident_id"):
        return "inspect_delegation_run_incident"
    if delegation.status != "completed":
        return "run_delegation"
    if metadata.get("implementation_handoff_md") or metadata.get("implementation_handoff_json"):
        return "prepare_coder_from_handoff"
    if metadata.get("execution_run_id") or metadata.get("run_id"):
        return "create_implementation_handoff"
    return "review_delegation_result"


def _repo_relative_artifact_path(root: Path, path: str | Path | None) -> str:
    if not path:
        return "none"
    candidate = Path(path)
    if candidate.is_absolute():
        try:
            return candidate.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return str(path)
    return str(path)


def _artifact_href(root: Path, path: str | Path | None) -> str:
    return f"/artifacts?path={quote(_repo_relative_artifact_path(root, path))}"


def _row_exists(db_path: Path, table: str, row_id: str) -> bool:
    rows = _table_rows(db_path, f"select id from {table} where id = ? limit 1", (row_id,))
    return bool(rows)


def _counts(db_path: Path) -> dict[str, int]:
    names = {
        "projects": "registered_projects",
        "tasks": "tasks",
        "runs": "runs",
        "approvals": "approval_requests",
        "incidents": "incidents",
        "delegations": "subagent_delegations",
    }
    counts: dict[str, int] = {}
    for label, table in names.items():
        rows = _table_rows(db_path, f"select count(*) as count from {table}")
        counts[label] = int(rows[0]["count"]) if rows else 0
    return counts


def _workflow_import_status() -> dict[str, str]:
    return {
        "context_pack": "ok",
        "implementation_handoff": "ok",
        "coder_prep": "ok",
        "coder_worktree_plan": "ok",
        "coder_worktree_execution": "ok",
        "coder_publication": "ok",
        "inbox": "ok",
    }


def _key_commands() -> list[str]:
    return [
        "app",
        "local-app",
        "serve",
        "demo-app-scenario",
        "app-demo",
        "implementation-handoff",
        "coder-prep",
        "coder-prep-from-handoff",
        "coder-worktree-plan",
        "coder-worktree-approval",
        "approve-coder-worktree",
        "coder-commit-request",
        "approve-coder-commit",
        "coder-publication-request",
        "approve-coder-publication",
        "coder-publication-handoff",
        "inbox",
    ]


def _warning_items(state: dict[str, Any], host: str) -> list[str]:
    warnings = []
    if host not in LOCAL_HOSTS:
        warnings.append("App is bound to a non-localhost interface.")
    if state["dirty_tracked_files"]:
        warnings.append("Repository has uncommitted tracked changes.")
    if state["ahead_of_origin_main"]:
        warnings.append("Local branch is ahead of origin/main; public README may not reflect local app state.")
    duplicates = {"README (1).md", "docs/docs-index (1).md"}.intersection(state["untracked_files"])
    if duplicates:
        warnings.append(f"Known duplicate untracked files are present: {', '.join(sorted(duplicates))}.")
    return warnings


def _ensure_demo_git_project(project_root: Path) -> None:
    project_root.mkdir(parents=True, exist_ok=True)
    (project_root / "demo.txt").write_text("local app demo fixture\n", encoding="utf-8")
    (project_root / "tests").mkdir(exist_ok=True)
    (project_root / "tests" / "test_demo.py").write_text(
        "def test_demo_fixture():\n    assert True\n",
        encoding="utf-8",
    )
    (project_root / "scripts").mkdir(exist_ok=True)
    (project_root / "scripts" / "change_demo.py").write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "",
                "path = Path('demo.txt')",
                "text = path.read_text(encoding='utf-8')",
                "marker = 'allowed local app demo change'",
                "if marker not in text:",
                "    path.write_text(text.rstrip() + '\\n' + marker + '\\n', encoding='utf-8')",
                "print('allowed-demo-change')",
                "",
            ]
        ),
        encoding="utf-8",
    )
    if not (project_root / ".git").exists():
        subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "demo@example.invalid"], cwd=project_root, check=True)
        subprocess.run(["git", "config", "user.name", "ClankerOS Demo"], cwd=project_root, check=True)
        subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=project_root, check=True)
        subprocess.run(["git", "config", "tag.gpgsign", "false"], cwd=project_root, check=True)
    subprocess.run(
        ["git", "add", "demo.txt", "tests/test_demo.py", "scripts/change_demo.py"],
        cwd=project_root,
        check=True,
    )
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=project_root).returncode != 0:
        subprocess.run(
            ["git", "-c", "commit.gpgsign=false", "commit", "--no-gpg-sign", "-m", "Add local app demo fixture"],
            cwd=project_root,
            check=True,
            capture_output=True,
        )


def _task_project(storage: Storage, task_id: str) -> str:
    task = storage.get_task(task_id)
    return task.project_id if task is not None else "unknown"


def _handoff_block(summary: dict[str, Any]) -> str:
    return "<section><h2>Implementation Handoff</h2>" + _kv(
        [
            ("status", str(summary["status"])),
            ("path", _artifact_link(summary["handoff_path"])),
            ("markdown_path", _artifact_link(summary["markdown_path"])),
            ("kind", str(summary["kind"])),
            ("kind_valid", str(summary["kind_valid"]).lower()),
            ("context_pack", _artifact_link(summary["context_pack_json"])),
            ("snippets_embedded", str(summary["snippets_embedded"]).lower()),
        ]
    ) + "</section>"


def _delegation_workflow_readiness(
    root: Path,
    delegation: Any,
    summary: dict[str, Any],
) -> str:
    delegation_id = delegation.id
    prep_packets = list_coder_prep_packets(root)
    delegation_prep = [
        item
        for item in prep_packets
        if item.get("source", {}).get("delegation_id") == delegation_id
    ]
    plan_packets = list_coder_worktree_plan_packets(root)
    delegation_plans = [
        item
        for item in plan_packets
        if item.get("source", {}).get("delegation_id") == delegation_id
    ]
    worktree_approvals = list_coder_worktree_approvals(
        root,
        delegation_id=delegation_id,
        limit=50,
    )
    worktree_runs = list_coder_worktree_runs(
        root,
        delegation_id=delegation_id,
        limit=50,
    )
    commit_approvals = list_coder_worktree_commit_approvals(
        root,
        delegation_id=delegation_id,
        limit=50,
    )
    publications = list_coder_publications(
        root,
        delegation_id=delegation_id,
        limit=50,
    )
    completed_runs = [item for item in worktree_runs if item.status == "completed"]
    reviewed_runs = [
        item
        for item in completed_runs
        if (root / "runs" / item.source_run_id / "review.md").exists()
    ]
    committed = [item for item in commit_approvals if item.status == "committed"]
    ready_publications = [
        item for item in publications if item.status == "ready_for_operator"
    ]
    return "<section><h2>Workflow Readiness</h2>" + _kv(
        [
            ("context_pack_status", _artifact_status(root, summary["context_pack_json"])),
            ("context_pack_path", _artifact_link(summary["context_pack_json"])),
            ("context_pack_markdown", _artifact_link(summary["context_pack_md"])),
            (
                "context_pack_returned_files_in_inventory",
                str(summary.get("context_pack_returned_files_in_inventory")).lower(),
            ),
            (
                "context_pack_returned_files_missing",
                _joined(summary.get("context_pack_returned_files_missing")),
            ),
            ("implementation_handoff_status", str(summary["status"])),
            ("implementation_handoff_path", _artifact_link(summary["markdown_path"])),
            ("coder_prep_packets", str(len(delegation_prep))),
            ("coder_worktree_plans", str(len(delegation_plans))),
            (
                "pending_worktree_approvals",
                str(_count_status(worktree_approvals, "pending_operator_approval")),
            ),
            (
                "approved_worktree_approvals",
                str(_count_status(worktree_approvals, "approved")),
            ),
            ("completed_worktree_runs", str(len(completed_runs))),
            ("reviewed_completed_worktree_runs", str(len(reviewed_runs))),
            (
                "pending_commit_approvals",
                str(_count_status(commit_approvals, "pending_operator_approval")),
            ),
            (
                "approved_commit_approvals",
                str(_count_status(commit_approvals, "approved")),
            ),
            ("local_commits", str(len(committed))),
            (
                "pending_publication_approvals",
                str(_count_status(publications, "pending_operator_approval")),
            ),
            (
                "approved_publication_approvals",
                str(_count_status(publications, "approved")),
            ),
            ("publication_handoffs", str(len(ready_publications))),
            (
                "next_recommended_action",
                _delegation_next_action(
                    root,
                    summary=summary,
                    prep_count=len(delegation_prep),
                    plan_count=len(delegation_plans),
                    worktree_approvals=worktree_approvals,
                    worktree_runs=worktree_runs,
                    commit_approvals=commit_approvals,
                    publications=publications,
                ),
            ),
        ]
    ) + "</section>"


def _selected_workflow_state(
    root: Path,
    *,
    delegation_id: str | None = None,
    run_id: str | None = None,
) -> str:
    if not delegation_id and not run_id:
        return ""

    storage = _storage(root)
    selected_run = None
    if run_id:
        selected_run = next(
            (item for item in list_coder_worktree_runs(root, limit=200) if item.id == run_id),
            None,
        )
        if selected_run is None:
            return "<section><h2>Selected Workflow State</h2>" + _kv(
                [
                    ("selection_status", "run_not_found"),
                    ("selected_run_id", run_id),
                    ("selected_delegation_id", delegation_id or "unknown"),
                ]
            ) + "</section>"
        if delegation_id and selected_run.delegation_id != delegation_id:
            return "<section><h2>Selected Workflow State</h2>" + _kv(
                [
                    ("selection_status", "run_delegation_mismatch"),
                    ("selected_run_id", run_id),
                    ("selected_run_delegation_id", selected_run.delegation_id),
                    ("selected_delegation_id", delegation_id),
                ]
            ) + "</section>"
        delegation_id = selected_run.delegation_id

    delegation = storage.get_subagent_delegation(delegation_id or "")
    if delegation is None:
        return "<section><h2>Selected Workflow State</h2>" + _kv(
            [
                ("selection_status", "delegation_not_found"),
                ("selected_delegation_id", delegation_id or "unknown"),
                ("selected_run_id", run_id or "none"),
            ]
        ) + "</section>"

    summary = summarize_implementation_handoff(root, delegation)
    prep_packets = [
        item
        for item in list_coder_prep_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    plan_packets = [
        item
        for item in list_coder_worktree_plan_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    worktree_approvals = list_coder_worktree_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    worktree_runs = list_coder_worktree_runs(root, delegation_id=delegation.id, limit=50)
    if selected_run is None and len(worktree_runs) == 1:
        selected_run = worktree_runs[0]
    commit_approvals = list_coder_worktree_commit_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    publications = list_coder_publications(root, delegation_id=delegation.id, limit=50)
    bounded_status = "none"
    if selected_run is not None:
        bounded_status = _artifact_status(
            root,
            Path(selected_run.evidence_path) / "bounded_file_validation.json",
        )
    elif worktree_runs:
        bounded_status = "select_run"

    return "<section><h2>Selected Workflow State</h2>" + _kv(
        [
            ("selection_status", "found"),
            ("selected_delegation_id", delegation.id),
            ("selected_run_id", selected_run.id if selected_run is not None else run_id or "none"),
            ("delegation_status", delegation.status),
            ("context_pack_status", _artifact_status(root, summary["context_pack_json"])),
            ("context_pack_path", _artifact_link(summary["context_pack_json"])),
            ("implementation_handoff_status", str(summary["status"])),
            ("implementation_handoff_path", _artifact_link(summary["markdown_path"])),
            ("coder_prep_status", "available" if prep_packets else "missing"),
            ("coder_worktree_plan_status", "available" if plan_packets else "missing"),
            ("worktree_approval_status", _status_counts(worktree_approvals)),
            (
                "worktree_run_status",
                selected_run.status if selected_run is not None else _status_counts(worktree_runs),
            ),
            ("bounded_file_validation_status", bounded_status),
            ("commit_request_status", _status_counts(commit_approvals)),
            (
                "commit_sha",
                next(
                    (item.commit_sha for item in commit_approvals if item.commit_sha),
                    "none",
                ),
            ),
            ("publication_request_status", _status_counts(publications)),
            (
                "publication_handoff_status",
                "available"
                if any(item.status == "ready_for_operator" for item in publications)
                else "missing",
            ),
            (
                "next_recommended_action",
                _delegation_next_action(
                    root,
                    summary=summary,
                    prep_count=len(prep_packets),
                    plan_count=len(plan_packets),
                    worktree_approvals=worktree_approvals,
                    worktree_runs=worktree_runs,
                    commit_approvals=commit_approvals,
                    publications=publications,
                ),
            ),
        ]
    ) + "</section>"


def _selected_workflow_continuation(
    root: Path,
    *,
    delegation_id: str | None = None,
    run_id: str | None = None,
) -> str:
    if not delegation_id and not run_id:
        return ""

    storage = _storage(root)
    selected_run = None
    if run_id:
        selected_run = next(
            (item for item in list_coder_worktree_runs(root, limit=200) if item.id == run_id),
            None,
        )
        if selected_run is None:
            return _list_section(
                "Selected Workflow Continuation",
                [
                    "selection_status: run_not_found",
                    f"selected_run_id: {_e(run_id)}",
                    "external_effects_created: false",
                ],
            )
        if delegation_id and selected_run.delegation_id != delegation_id:
            return _list_section(
                "Selected Workflow Continuation",
                [
                    "selection_status: run_delegation_mismatch",
                    f"selected_run_id: {_e(run_id)}",
                    f"selected_delegation_id: {_e(delegation_id)}",
                    "external_effects_created: false",
                ],
            )
        delegation_id = selected_run.delegation_id

    delegation = storage.get_subagent_delegation(delegation_id or "")
    if delegation is None:
        return _list_section(
            "Selected Workflow Continuation",
            [
                "selection_status: delegation_not_found",
                f"selected_delegation_id: {_e(delegation_id or 'unknown')}",
                f"selected_run_id: {_e(run_id or 'none')}",
                "external_effects_created: false",
            ],
        )

    summary = summarize_implementation_handoff(root, delegation)
    prep_packets = [
        item
        for item in list_coder_prep_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    plan_packets = [
        item
        for item in list_coder_worktree_plan_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    worktree_approvals = list_coder_worktree_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    worktree_runs = list_coder_worktree_runs(root, delegation_id=delegation.id, limit=50)
    if selected_run is None and len(worktree_runs) == 1:
        selected_run = worktree_runs[0]
    commit_approvals = list_coder_worktree_commit_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    publications = list_coder_publications(root, delegation_id=delegation.id, limit=50)
    next_action = _delegation_next_action(
        root,
        summary=summary,
        prep_count=len(prep_packets),
        plan_count=len(plan_packets),
        worktree_approvals=worktree_approvals,
        worktree_runs=worktree_runs,
        commit_approvals=commit_approvals,
        publications=publications,
    )
    selected_run_id = selected_run.id if selected_run is not None else run_id or "none"
    run_surface = "select a coder worktree run"
    if selected_run is not None:
        run_surface = (
            f"<a href='/runs/{quote(selected_run.id)}'>"
            f"/runs/{_e(selected_run.id)}</a>"
        )
    action_hints = {
        "request_commit_for_reviewed_run": "request coder commit on the run detail page",
        "approve_or_reject_commit_request": "decide the pending commit request on approvals",
        "commit_approved_worktree": "commit approved worktree from the run detail page",
        "request_publication_handoff": "request publication handoff on the run detail page",
        "approve_or_reject_publication_request": "decide the pending publication request on approvals",
        "prepare_publication_handoff": "prepare the publication handoff on the run detail page",
        "manual_operator_push_pr_outside_clankeros": "use the publication handoff outside ClankerOS",
    }
    lines = [
        f"continue_from: {_e(next_action)}",
        f"operator_surface_hint: {_e(action_hints.get(next_action, 'review selected workflow state'))}",
        f"selected_delegation_id: {_e(delegation.id)}",
        f"selected_run_id: {_e(selected_run_id)}",
        f"run_action_surface: {run_surface}",
        "approvals_surface: <a href='/approvals'>/approvals</a>",
        "inbox_surface: <a href='/inbox'>/inbox</a>",
        "dogfooding_surface: <a href='/dogfooding'>/dogfooding</a>",
        "external_effects_created: false",
        "network_actions_taken_by_app: 0",
    ]
    return _list_section("Selected Workflow Continuation", lines)


def _workflow_step_statuses(
    root: Path,
    *,
    delegation_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, str]:
    if not delegation_id and not run_id:
        return {}

    storage = _storage(root)
    selected_run = None
    if run_id:
        selected_run = next(
            (item for item in list_coder_worktree_runs(root, limit=200) if item.id == run_id),
            None,
        )
        if selected_run is None:
            return {"Approved worktree execution": "run_not_found"}
        if delegation_id and selected_run.delegation_id != delegation_id:
            return {
                "Delegate scout": "run_delegation_mismatch",
                "Approved worktree execution": "run_delegation_mismatch",
            }
        delegation_id = selected_run.delegation_id

    delegation = storage.get_subagent_delegation(delegation_id or "")
    if delegation is None:
        return {"Delegate scout": "delegation_not_found"}

    summary = summarize_implementation_handoff(root, delegation)
    prep_packets = [
        item
        for item in list_coder_prep_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    plan_packets = [
        item
        for item in list_coder_worktree_plan_packets(root)
        if item.get("source", {}).get("delegation_id") == delegation.id
    ]
    worktree_approvals = list_coder_worktree_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    worktree_runs = list_coder_worktree_runs(root, delegation_id=delegation.id, limit=50)
    if selected_run is None and len(worktree_runs) == 1:
        selected_run = worktree_runs[0]
    commit_approvals = list_coder_worktree_commit_approvals(
        root,
        delegation_id=delegation.id,
        limit=50,
    )
    publications = list_coder_publications(root, delegation_id=delegation.id, limit=50)
    bounded_status = "none"
    if selected_run is not None:
        bounded_status = _artifact_status(
            root,
            Path(selected_run.evidence_path) / "bounded_file_validation.json",
        )
    elif worktree_runs:
        bounded_status = "select_run"
    local_commit_status = (
        "available" if any(item.commit_sha for item in commit_approvals) else "missing"
    )
    publication_handoff_status = (
        "available"
        if any(item.status == "ready_for_operator" for item in publications)
        else "missing"
    )
    manual_publication_status = (
        "ready" if publication_handoff_status == "available" else "not_ready"
    )
    return {
        "Goal / task": _workflow_status_token(
            "task",
            "available" if storage.get_task(delegation.parent_task_id) else "missing",
        ),
        "Delegate scout": _workflow_status_token("delegation", delegation.status),
        "Context pack": _workflow_status_token(
            "context_pack",
            _artifact_status(root, summary["context_pack_json"]),
        ),
        "Run delegation": _workflow_status_token("delegation_run", delegation.status),
        "Implementation handoff": _workflow_status_token(
            "handoff",
            str(summary["status"]),
        ),
        "Coder prep": _workflow_status_token(
            "coder_prep",
            "available" if prep_packets else "missing",
        ),
        "Coder worktree plan": _workflow_status_token(
            "worktree_plan",
            "available" if plan_packets else "missing",
        ),
        "Worktree approval": _workflow_status_token(
            "worktree_approval",
            _status_counts(worktree_approvals),
        ),
        "Approved worktree execution": _workflow_status_token(
            "worktree_run",
            selected_run.status if selected_run is not None else _status_counts(worktree_runs),
        ),
        "Bounded-file validation": _workflow_status_token(
            "bounded_file_validation",
            bounded_status,
        ),
        "Commit request": _workflow_status_token(
            "commit_request",
            _status_counts(commit_approvals),
        ),
        "Commit approval": _workflow_status_token(
            "commit_approval",
            _status_counts(commit_approvals),
        ),
        "Local commit": _workflow_status_token("local_commit", local_commit_status),
        "Publication request": _workflow_status_token(
            "publication_request",
            _status_counts(publications),
        ),
        "Publication approval": _workflow_status_token(
            "publication_approval",
            _status_counts(publications),
        ),
        "Publication handoff": _workflow_status_token(
            "publication_handoff",
            publication_handoff_status,
        ),
        "Manual operator push/PR outside ClankerOS": _workflow_status_token(
            "external_manual",
            manual_publication_status,
        ),
    }


def _delegation_next_action(
    root: Path,
    *,
    summary: dict[str, Any],
    prep_count: int,
    plan_count: int,
    worktree_approvals: list[Any],
    worktree_runs: list[Any],
    commit_approvals: list[Any],
    publications: list[Any],
) -> str:
    if _artifact_status(root, summary["context_pack_json"]) == "missing":
        return "generate_context_pack"
    if summary["status"] != "readable":
        return "run_delegation_or_review_implementation_handoff"
    if prep_count == 0:
        return "prepare_coder_from_handoff"
    if plan_count == 0:
        return "prepare_coder_worktree_plan"
    completed_runs = [item for item in worktree_runs if item.status == "completed"]
    reviewed_runs = [
        item
        for item in completed_runs
        if (root / "runs" / item.source_run_id / "review.md").exists()
    ]
    if reviewed_runs and not commit_approvals:
        return "request_commit_for_reviewed_run"
    if _count_status(commit_approvals, "pending_operator_approval"):
        return "approve_or_reject_commit_request"
    if _count_status(commit_approvals, "approved"):
        return "commit_approved_worktree"
    if _count_status(commit_approvals, "committed") and not publications:
        return "request_publication_handoff"
    if _count_status(publications, "pending_operator_approval"):
        return "approve_or_reject_publication_request"
    if _count_status(publications, "approved"):
        return "prepare_publication_handoff"
    if _count_status(publications, "ready_for_operator"):
        return "manual_operator_push_pr_outside_clankeros"
    if _count_status(worktree_approvals, "pending_operator_approval"):
        return "decide_pending_worktree_approval"
    if _count_status(worktree_approvals, "approved") and not worktree_runs:
        return "run_approved_worktree_from_cli"
    return "review_delegation_state"


def _artifact_status(root: Path, relative_path: object) -> str:
    path = str(relative_path)
    if not path or path == "none":
        return "none"
    return "available" if (root / path).exists() else "missing"


def _count_status(items: list[Any], status: str) -> int:
    return sum(1 for item in items if item.status == status)


def _status_counts(items: list[Any]) -> str:
    if not items:
        return "none"
    counts: dict[str, int] = {}
    for item in items:
        status = str(getattr(item, "status", "unknown"))
        counts[status] = counts.get(status, 0) + 1
    return ", ".join(f"{status}:{count}" for status, count in sorted(counts.items()))


def _workflow_status_token(prefix: str, value: object) -> str:
    return f"{prefix}_{_status_slug(value)}"


def _status_slug(value: object) -> str:
    slug = "".join(
        character.lower() if character.isalnum() else "_"
        for character in str(value)
    ).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug or "unknown"


def _joined(value: object) -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value) or "none"
    if value in (None, "", "none"):
        return "none"
    return str(value)


def _workflow_list(
    *,
    compact: bool,
    selected_statuses: dict[str, str] | None = None,
) -> str:
    items = []
    selected_statuses = selected_statuses or {}
    for index, (label, command, mutation, required, output) in enumerate(WORKFLOW_STEPS, start=1):
        if compact:
            items.append(f"<li>{index}. {_e(label)} <code>{_e(command)}</code></li>")
        else:
            rows = [
                ("command", command),
                ("available", "true"),
                ("mutates_local_state", str(mutation in {"local_state", "local_artifact", "local_approval", "local_execution", "local_git_only"}).lower()),
                ("creates_external_effects", "false" if "Manual operator" not in label else "outside_clankeros"),
                ("required_previous_artifact", required),
                ("output_artifact", output),
            ]
            if label in selected_statuses:
                rows.append(("selected_status", selected_statuses[label]))
            items.append(
                "<li>"
                f"<strong>{index}. {_e(label)}</strong>"
                + _kv(rows)
                + "</li>"
            )
    return "<ol class='workflow'>" + "".join(items) + "</ol>"


def _list_section(
    title: str,
    items: list[str],
    link: str | None = None,
    *,
    anchor_id: str | None = None,
) -> str:
    heading = f"<h2>{_e(title)}</h2>"
    if link:
        heading += f"<p><a href='{_e(link)}'>Open</a></p>"
    id_attr = f" id='{_e(anchor_id)}'" if anchor_id else ""
    return f"<section{id_attr}>{heading}{_ul(items)}</section>"


def _artifact_links(packets: list[dict[str, Any]], *, delegation_id: str | None = None) -> list[str]:
    links = []
    for packet in packets:
        source = packet.get("source", {})
        if delegation_id and source.get("delegation_id") != delegation_id:
            continue
        path = packet.get("_path") or packet.get("artifacts", {}).get("json")
        if path:
            links.append(f"{_e(packet.get('kind', 'artifact'))}: {_artifact_link(str(path))}")
    return links


def _approval_line(item: Any) -> str:
    return f"{item.id}: status={item.status} project={item.project_id} plan={item.source_plan_sha256}"


def _coder_run_line(root: Path, item: Any) -> str:
    change_summary = coder_worktree_change_summary(root, item)
    return (
        f"<a href='/runs/{quote(item.id)}'>{_e(item.id)}</a>: {item.status} "
        f"project={item.project_id} changed={','.join(item.changed_files) or 'none'} "
        f"changed_files_count={_e(change_summary['changed_files_count'])} "
        f"outside={','.join(item.outside_allowed_files) or 'none'} "
        f"diff_summary={_e(change_summary['diff_summary'])} "
        f"diff={_artifact_link(str(Path(item.evidence_path) / 'diff.patch'))}"
    )


def _commit_line(item: Any) -> str:
    return (
        f"{item.id}: status={item.status} run={item.run_id} project={item.project_id} "
        f"commit={item.commit_sha or 'none'}"
    )


def _publication_line(root: Path, item: Any) -> str:
    handoff = item.handoff_artifact_path if item.status == "ready_for_operator" else "none"
    return (
        f"{item.id}: status={item.status} run={item.run_id} project={item.project_id} "
        f"commit={item.commit_sha} handoff={_artifact_link(handoff)} "
        "push_created=false pr_created=false deploy_created=false"
    )


def _kv(items: list[tuple[str, str]]) -> str:
    rows = []
    for key, value in items:
        rendered = str(value) if isinstance(value, SafeHtml) else _e(value)
        rows.append(f"<dt>{_e(key)}</dt><dd>{rendered}</dd>")
    return "<dl>" + "".join(rows) + "</dl>"


def _ul(items: list[str]) -> str:
    if not items:
        return "<p class='muted'>none</p>"
    return "<ul>" + "".join(f"<li>{item}</li>" for item in items) + "</ul>"


def _non_claim_banner() -> str:
    return "<div class='banner'><strong>Safety boundary:</strong> " + "; ".join(
        _e(claim) for claim in NO_EXTERNAL_EFFECT_CLAIMS
    ) + ".</div>"


def _warnings(warnings: list[str]) -> str:
    if not warnings:
        return ""
    return "<section class='warning'><h2>Warnings</h2>" + _ul([_e(item) for item in warnings]) + "</section>"


def _artifact_link(path: str) -> SafeHtml | str:
    if not path or path == "none":
        return "none"
    return SafeHtml(f"<a href='/artifacts?path={quote(path)}'>{_e(path)}</a>")


def _path_link(path: str) -> SafeHtml:
    return SafeHtml(f"<a href='{_e(path)}'>{_e(path)}</a>")


def _one(values: dict[str, list[str]], key: str) -> str | None:
    items = values.get(key) or []
    return items[0] if items else None


def _required(values: dict[str, list[str]], key: str) -> str:
    value = _one(values, key)
    if not value:
        raise ValueError(f"{key} is required")
    return value


def _e(value: object) -> str:
    return html.escape(str(value), quote=True)
