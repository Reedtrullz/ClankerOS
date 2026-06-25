from __future__ import annotations

import html
import json
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
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
    request_coder_publication,
)
from agent_os.coder_worktree_execution import (
    CoderWorktreeApprovalError,
    CoderWorktreeCommitError,
    approve_coder_worktree,
    approve_coder_worktree_commit,
    commit_coder_worktree,
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
from agent_os.context_pack import ContextPackError, generate_context_pack
from agent_os.engine import AgentSystem
from agent_os.ids import new_id
from agent_os.implementation_handoff import summarize_implementation_handoff
from agent_os.storage import Storage, utc_now
from agent_os.steering import collect_inbox_items
from agent_os.subagent_delegation import load_delegation_result_metadata


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
    ("Commit request", "coder-commit-request", "local_approval", "reviewed worktree run", "coder_commit_request.md"),
    ("Commit approval", "approve-coder-commit", "local_approval", "commit request", "coder_commit_decision.md"),
    ("Local commit", "commit-coder-worktree", "local_git_only", "approved commit request", "commit.json"),
    ("Publication request", "coder-publication-request", "local_approval", "local commit", "publication_request.md"),
    ("Publication approval", "approve-coder-publication", "local_approval", "publication request", "publication_decision.md"),
    ("Publication handoff", "coder-publication-handoff", "local_artifact", "approved publication", "publication_handoff.md + pr_body.md"),
    ("Manual operator push/PR outside ClankerOS", "manual git/gh", "external_manual_only", "publication handoff", "outside ClankerOS"),
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
    try:
        if method == "POST":
            return _handle_post(root, path, form or {})
        if path == "/":
            return _html_page(root, "Dashboard", _dashboard(root, host=host, port=port))
        if path == "/workflow":
            return _html_page(
                root,
                "Workflow",
                _workflow(
                    root,
                    delegation_id=_one(query, "delegation_id"),
                    run_id=_one(query, "run_id"),
                ),
            )
        if path == "/projects":
            return _html_page(root, "Projects", _projects(root))
        if path == "/inbox":
            return _html_page(root, "Inbox", _inbox(root))
        if path == "/approvals":
            return _html_page(root, "Approvals", _approvals(root))
        if path == "/incidents":
            return _html_page(root, "Incidents", _incidents(root))
        if path.startswith("/projects/"):
            project_id = unquote(path.removeprefix("/projects/"))
            return _html_page(root, f"Project {project_id}", _project_detail(root, project_id))
        if path.startswith("/delegations/"):
            delegation_id = unquote(path.removeprefix("/delegations/"))
            return _html_page(
                root,
                f"Delegation {delegation_id}",
                _delegation_detail(root, delegation_id),
            )
        if path.startswith("/runs/"):
            run_id = unquote(path.removeprefix("/runs/"))
            return _html_page(root, f"Run {run_id}", _run_detail(root, run_id))
        if path == "/artifacts":
            return _artifact_viewer(root, _one(query, "path"))
        if path == "/health":
            return _html_page(root, "Health", _health(root, host=host, port=port))
        if path == "/demo":
            return _html_page(root, "Demo", _demo_page(root))
        return _html_page(root, "Not Found", "<p>Route not found.</p>", status=404)
    except Exception as error:  # defensive app boundary
        return _html_page(
            root,
            "Local App Error",
            f"<p class='error'>{_e(type(error).__name__)}: {_e(str(error))}</p>",
            status=500,
        )


def run_local_app_smoke_test(root: Path) -> dict[str, Any]:
    root = root.resolve()
    routes = ["/", "/workflow", "/projects", "/inbox", "/approvals", "/incidents", "/health", "/demo"]
    results = []
    for route in routes:
        response = render_local_app_route(root, route)
        results.append({"route": route, "status": response.status})
    ok = all(item["status"] == 200 for item in results)
    return {
        "status": "passed" if ok else "failed",
        "routes": results,
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


def write_local_app_status(root: Path, *, host: str, port: int) -> Path:
    root = root.resolve()
    state = _repo_state(root)
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": host,
        "port": port,
        "repo_root": str(root),
        "branch": state["branch"],
        "commit": state["commit"],
        "dirty_tracked_files": state["dirty_tracked_files"],
        "untracked_files": state["untracked_files"],
        "routes_available": ["/", "/workflow", "/projects", "/delegations/<id>", "/runs/<id>", "/inbox", "/approvals", "/incidents", "/artifacts", "/health", "/demo"],
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
    return "".join(
        [
            "<section class='hero'>",
            "<h1>ClankerOS Local Operator</h1>",
            "<p>Local-first operator UI for the handoff, worktree, commit, and publication workflow.</p>",
            _non_claim_banner(),
            "</section>",
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
            "<section><h2>Modern Workflow</h2>",
            "<p><a href='/workflow'>Open workflow stepper</a></p>",
            _workflow_list(compact=True),
            "</section>",
            _list_section("Projects", rows["projects"], "/projects"),
            _list_section("Recent Goals", rows["goals"]),
            _list_section("Recent Tasks", rows["tasks"]),
            _list_section("Recent Delegations", rows["delegations"]),
            _list_section("Recent Implementation Handoffs", rows["implementation_handoffs"]),
            _list_section("Recent Coder Worktree Runs", rows["coder_runs"]),
            _list_section("Recent Commit Requests / Local Commits", rows["commit_requests"]),
            _list_section("Recent Publication Requests", rows["publication_requests"]),
            _list_section("Recent Publication Handoffs", rows["publication_handoffs"]),
            _list_section("Operator Inbox", rows["inbox"], "/inbox"),
            _list_section("Pending Approvals", rows["approvals"], "/approvals"),
            _list_section("Incidents / Recommendations", rows["incidents"], "/incidents"),
            "<section><h2>Next Recommended Action</h2><p>Review the workflow page, run the demo scenario, then inspect a delegation or artifact.</p></section>",
        ]
    )


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
            _workflow_list(compact=False, selected_statuses=selected_statuses),
            "</section>",
        ]
    )


def _projects(root: Path) -> str:
    storage = _storage(root)
    projects = storage.list_registered_projects()
    items = [
        f"<li><a href='/projects/{quote(project.name)}'>{_e(project.name)}</a> <span>{_e(project.root_path)}</span></li>"
        for project in projects
    ]
    return "<section><h1>Projects</h1>" + _ul(items) + "</section>"


def _inbox(root: Path) -> str:
    inbox = collect_inbox_items(root)
    return "".join(
        [
            "<section><h1>Operator Inbox</h1>",
            "<p class='muted'>Read-only local operator queue assembled from steering reviews, approvals, incidents, delegations, coder runs, commits, and publication handoffs.</p>",
            "</section>",
            _list_section(
                "Inbox Summary",
                _inbox_summary_lines(root)
                + ["network_actions_taken: 0", "external_mutations_taken: 0"],
            ),
            _list_section(
                "Steering Reviews",
                [_steering_review_line(item) for item in inbox["steering_reviews"]],
            ),
            _list_section(
                "Pending Approval Requests",
                [_operator_approval_line(item) for item in inbox["pending_approvals"]],
            ),
            _list_section(
                "Open Incidents",
                [_incident_line(item) for item in inbox["open_incidents"]],
                "/incidents",
            ),
            _list_section(
                "Subagent Delegations",
                [_delegation_line(item) for item in inbox["subagent_delegations"]],
            ),
            _list_section(
                "Pending Worktree Approvals",
                [_approval_line(item) for item in inbox["coder_worktree_approvals"]],
                "/approvals",
            ),
            _list_section(
                "Coder Worktree Runs",
                [_coder_run_line(item) for item in inbox["coder_worktree_runs"]],
            ),
            _list_section(
                "Pending Commit Approvals",
                [_commit_line(item) for item in inbox["coder_worktree_commit_approvals"]],
                "/approvals",
            ),
            _list_section(
                "Local Coder Commits",
                [_commit_line(item) for item in inbox["coder_worktree_commits"]],
            ),
            _list_section(
                "Pending Publication Requests",
                [_publication_line(root, item) for item in inbox["coder_publication_requests"]],
                "/approvals",
            ),
            _list_section(
                "Publication Handoffs",
                [_publication_line(root, item) for item in inbox["coder_publication_handoffs"]],
            ),
            _non_claim_banner(),
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
            _list_section(
                "Pending Worktree Approvals",
                [_worktree_approval_action_line(item) for item in worktree_approvals],
            ),
            _list_section(
                "Pending Commit Approvals",
                [_commit_approval_action_line(item) for item in commit_approvals],
            ),
            _list_section(
                "Pending Publication Approvals",
                [_publication_approval_action_line(root, item) for item in publication_approvals],
            ),
            _non_claim_banner(),
        ]
    )


def _incidents(root: Path) -> str:
    storage = _storage(root)
    rows = _table_rows(
        storage.db_path,
        "select id, status, severity, summary, evidence_path from incidents order by created_at desc limit 50",
    )
    return "".join(
        [
            "<section><h1>Incidents</h1>",
            _ul(
                [
                    f"{_e(row['id'])}: status={_e(row['status'])} severity={_e(row['severity'])} "
                    f"{_e(row['summary'])} evidence={_artifact_link(row['evidence_path'] or 'none')}"
                    for row in rows
                ]
            ),
            "</section>",
        ]
    )


def _project_detail(root: Path, project_id: str) -> str:
    storage = _storage(root)
    project = storage.get_registered_project(project_id)
    if project is None:
        return "<p class='error'>Project not found.</p>"
    repo = _repo_state(Path(project.root_path))
    task_rows = _table_rows(
        storage.db_path,
        "select id, status, task_type, description from tasks where project_id = ? order by updated_at desc limit 20",
        (project_id,),
    )
    delegations = [
        delegation
        for delegation in storage.list_recent_subagent_delegations(limit=None)
        if _task_project(storage, delegation.parent_task_id) == project_id
    ][:20]
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
            _list_section(
                "Tasks / Goals",
                [
                    f"{row['id']}: {row['status']} {row['task_type']} - {row['description']}"
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
            _project_operator_guidance(
                root,
                storage,
                project_id=project_id,
                task_rows=task_rows,
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


def _project_operator_guidance(
    root: Path,
    storage: Storage,
    *,
    project_id: str,
    task_rows: list[sqlite3.Row],
) -> str:
    task_ids = [str(row["id"]) for row in task_rows]
    incidents = _table_rows(
        storage.db_path,
        "select id, status, severity, summary, evidence_path from incidents where project_id = ? order by created_at desc limit 20",
        (project_id,),
    )
    open_incidents = [row for row in incidents if row["status"] == "open"]
    recommendations = _project_task_recommendations(storage, task_ids)
    worktree_approvals = [
        item
        for item in list_coder_worktree_approvals(root, limit=100)
        if item.project_id == project_id
    ]
    worktree_runs = [
        item
        for item in list_coder_worktree_runs(root, limit=100)
        if item.project_id == project_id
    ]
    commit_approvals = [
        item
        for item in list_coder_worktree_commit_approvals(root, limit=100)
        if item.project_id == project_id
    ]
    publications = [
        item
        for item in list_coder_publications(root, limit=100)
        if item.project_id == project_id
    ]
    completed_runs = [item for item in worktree_runs if item.status == "completed"]
    reviewed_runs = [
        item
        for item in completed_runs
        if (root / "runs" / item.source_run_id / "review.md").exists()
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
        and (root / "runs" / item.source_run_id / "review.md").exists()
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
        _list_section("Worktree Runs", [_coder_run_line(item) for item in list_coder_worktree_runs(root, delegation_id=delegation_id, limit=20)]),
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
    if run is None and not coder_runs:
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
        parts.append(_run_workflow_state(root, coder_run))
        parts.append(
            _list_section(
                "Coder Worktree Evidence",
                [
                    f"{_e(label)}: {_artifact_link(path)}"
                    for label, path in evidence_links
                    if (root / path).exists()
                ],
            )
        )
        parts.append(_run_action_forms(root, coder_run.id))
    parts.append("</section>")
    return "".join(parts)


def _run_workflow_state(root: Path, coder_run: Any) -> str:
    storage = _storage(root)
    delegation = storage.get_subagent_delegation(coder_run.delegation_id)
    if delegation is None:
        return "<section><h2>Run Workflow State</h2>" + _kv(
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
    return "<section><h2>Run Workflow State</h2>" + _non_claim_banner() + _kv(
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


def _artifact_viewer(root: Path, relative_path: str | None) -> LocalAppResponse:
    if not relative_path:
        return _html_page(root, "Artifact", "<p class='error'>Missing path.</p>", status=400)
    try:
        path = resolve_artifact_path(root, relative_path)
    except ValueError as error:
        return _html_page(root, "Artifact Rejected", f"<p class='error'>{_e(str(error))}</p>", status=400)
    if not path.exists() or not path.is_file():
        return _html_page(root, "Artifact Missing", "<p class='error'>Artifact file not found.</p>", status=404)
    size = path.stat().st_size
    data = path.read_bytes()[:MAX_ARTIFACT_BYTES]
    truncated = size > MAX_ARTIFACT_BYTES
    text = data.decode("utf-8", errors="replace")
    if path.suffix == ".json":
        try:
            text = json.dumps(json.loads(text), indent=2, sort_keys=True)
        except json.JSONDecodeError:
            pass
    body = "".join(
        [
            f"<section><h1>Artifact {_e(str(path.relative_to(root)))}</h1>",
            _kv([("size_bytes", str(size)), ("truncated", str(truncated).lower())]),
            "<pre>",
            _e(text),
            "</pre>",
            "<p class='muted'>Artifact content is rendered as inert text and is never executed.</p>",
            "</section>",
        ]
    )
    return _html_page(root, "Artifact", body)


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


def _health(root: Path, *, host: str, port: int) -> str:
    status_path = write_local_app_status(root, host=host, port=port)
    storage = _storage(root)
    counts = _counts(storage.db_path)
    state = _repo_state(root)
    imports = _workflow_import_status()
    return "".join(
        [
            "<section><h1>System Health</h1>",
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
            _manual_browser_script(
                {
                    "project_id": project.name,
                    "delegation_id": selected_delegation.id if selected_delegation else "",
                    "run_id": selected_run.id if selected_run else "",
                    "review_path": review_path,
                }
            ),
        ]
    )


def _manual_browser_script(state: dict[str, str] | None) -> str:
    delegation_id = (state or {}).get("delegation_id", "")
    run_id = (state or {}).get("run_id", "")
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
        ]
    )


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
        elif action == "context-pack":
            delegation_id = _required(form, "delegation_id")
            result = generate_context_pack(root, storage, delegation_id)
            message = f"context_pack: {result.context_pack_id}"
            location = f"/delegations/{quote(delegation_id)}"
        elif action == "implementation-handoff":
            delegation_id = _required(form, "delegation_id")
            delegation = storage.get_subagent_delegation(delegation_id)
            if delegation is None:
                raise ValueError("delegation not found")
            summary = summarize_implementation_handoff(root, delegation)
            message = f"implementation_handoff_status: {summary['status']}"
            location = f"/delegations/{quote(delegation_id)}"
        elif action == "coder-prep":
            delegation_id = _required(form, "delegation_id")
            result = prepare_coder_from_handoff(root, storage, delegation_id)
            message = f"coder_prep: {result.prep_id}"
            location = f"/delegations/{quote(delegation_id)}"
        elif action == "coder-prep-from-handoff":
            handoff_md = _required(form, "handoff_md")
            result = prepare_coder_from_handoff_markdown(root, storage, handoff_md)
            message = f"coder_prep: {result.prep_id}"
            location = f"/delegations/{quote(result.delegation_id)}"
        elif action == "coder-worktree-plan":
            delegation_id = _required(form, "delegation_id")
            result = prepare_worktree_plan_from_coder_prep(root, storage, delegation_id)
            message = f"coder_worktree_plan: {result.plan_id}"
            location = f"/delegations/{quote(delegation_id)}"
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
        elif action == "coder-publication-handoff":
            run_id = _required(form, "run_id")
            result = create_coder_publication_handoff(root, storage, run_id)
            message = f"coder_publication_handoff: {result.status}"
            location = f"/runs/{quote(run_id)}"
        else:
            raise ValueError(f"unsupported action: {action}")
    except (
        ValueError,
        ContextPackError,
        CoderPrepError,
        CoderWorktreePlanError,
        CoderWorktreeApprovalError,
        CoderWorktreeCommitError,
        CoderPublicationError,
    ) as error:
        return _html_page(root, "Action Error", f"<p class='error'>{_e(str(error))}</p>", status=400)
    return LocalAppResponse(
        303,
        "",
        headers={"Location": f"{location}?notice={quote(message)}"},
    )


def _safe_action_forms(*, delegation_id: str, handoff_md: str) -> str:
    return f"""
    <section><h2>Safe Local Actions</h2>
      <p class="muted">Delegation-scoped artifact and approval actions require an explicit confirmation page. Worktree execution, local commit, publication handoff, push, PR, deploy, provider, and arbitrary command actions are not exposed here.</p>
      {_form('implementation-handoff', {'delegation_id': delegation_id})}
      {_form('context-pack', {'delegation_id': delegation_id})}
      {_form('coder-prep', {'delegation_id': delegation_id})}
      {_form('coder-prep-from-handoff', {'handoff_md': handoff_md})}
      {_form('coder-worktree-plan', {'delegation_id': delegation_id})}
      {_form('coder-worktree-approval', {'delegation_id': delegation_id, 'note': 'Approve bounded worktree execution from local app'})}
    </section>
    """


def _run_action_forms(root: Path, run_id: str) -> str:
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
        "<section><h2>Run Approval Actions</h2>",
        "<p class='muted'>These forms create local approval/request artifacts only. They do not stage, commit, push, create PRs, deploy, call providers, or use the network.</p>",
    ]
    if not commit_approvals:
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
    sections.append("</section>")
    if approved_commit:
        sections.extend(
            [
                "<section><h2>Confirmed Local Commit Action</h2>",
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
                "<section><h2>Publication Handoff Action</h2>",
                "<p class='muted'>This writes local publication handoff and PR-body artifacts with suggested manual commands only. It does not push, create a PR, deploy, call providers, or use the network.</p>",
                _form("coder-publication-handoff", {"run_id": run_id}),
                "</section>",
            ]
        )
    return "".join(sections)


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
        + _input_form(
            "approve-coder-commit",
            {"approval_id": item.id, "decided_by": "operator"},
            {"note": "Approved local commit"},
        )
    )


def _publication_approval_action_line(root: Path, item: Any) -> str:
    return (
        f"{_publication_line(root, item)} request={_artifact_link(item.request_artifact_path)} "
        + _input_form(
            "approve-coder-publication",
            {"publication_id": item.id, "decided_by": "operator"},
            {"note": "Approved publication handoff preparation"},
        )
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
    return (
        f"<section><h1>Confirm {_e(action)}</h1>"
        "<p>This action writes local ClankerOS artifacts only. It does not push, create PRs, deploy, call providers, or execute external mutations.</p>"
        f"<form method='post' action='/actions/{_e(action)}'>{''.join(inputs)}<button type='submit'>Confirm local action</button></form>"
        "</section>"
    )


def _html_page(root: Path, title: str, content: str, *, status: int = 200) -> LocalAppResponse:
    body = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_e(title)} - ClankerOS Local Operator</title>
  <style>
    :root {{ color-scheme: light; --ink:#15171a; --muted:#5d6672; --line:#d9dee5; --panel:#f7f8fa; --accent:#176b87; --warn:#8a4b00; --error:#9c1d24; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color:var(--ink); background:#ffffff; line-height:1.45; }}
    header {{ display:flex; justify-content:space-between; align-items:center; gap:16px; padding:14px 24px; border-bottom:1px solid var(--line); background:#fff; position:sticky; top:0; z-index:1; }}
    header a {{ color:var(--ink); text-decoration:none; font-size:14px; margin-right:14px; }}
    main {{ max-width:1180px; margin:0 auto; padding:24px; }}
    section {{ border-bottom:1px solid var(--line); padding:20px 0; }}
    h1 {{ font-size:30px; line-height:1.15; margin:0 0 10px; letter-spacing:0; }}
    h2 {{ font-size:18px; margin:0 0 12px; letter-spacing:0; }}
    h3 {{ font-size:15px; margin:16px 0 6px; }}
    p, li, dd, dt, td, th, button, input {{ font-size:14px; }}
    .hero p {{ color:var(--muted); max-width:760px; }}
    .banner, .warning {{ border:1px solid var(--line); background:var(--panel); padding:12px; margin:12px 0; }}
    .warning {{ border-color:#efc36a; color:var(--warn); }}
    .error {{ color:var(--error); font-weight:600; }}
    .muted {{ color:var(--muted); }}
    dl {{ display:grid; grid-template-columns:minmax(170px, 260px) 1fr; gap:8px 16px; }}
    dt {{ color:var(--muted); }}
    dd {{ margin:0; word-break:break-word; }}
    ol.workflow {{ list-style:none; padding:0; display:grid; gap:10px; }}
    ol.workflow li {{ border:1px solid var(--line); padding:12px; background:#fff; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(260px, 1fr)); gap:12px; }}
    a {{ color:var(--accent); }}
    pre {{ overflow:auto; padding:14px; background:#0f1419; color:#eef4f8; border-radius:6px; font-size:13px; line-height:1.4; }}
    button {{ border:1px solid var(--accent); background:var(--accent); color:white; padding:7px 10px; border-radius:6px; margin:3px 0; cursor:pointer; }}
  </style>
</head>
<body>
  <header>
    <strong>ClankerOS Local Operator</strong>
    <nav><a href="/">Dashboard</a><a href="/workflow">Workflow</a><a href="/projects">Projects</a><a href="/inbox">Inbox</a><a href="/approvals">Approvals</a><a href="/incidents">Incidents</a><a href="/health">Health</a><a href="/demo">Demo</a></nav>
  </header>
  <main>{content}</main>
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
        f"{row['id']}: {row['status']} {_e(row['description'])}"
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
        "implementation_handoffs": _implementation_handoff_lines(root, storage, limit=10),
        "coder_runs": [_coder_run_line(item) for item in list_coder_worktree_runs(root, limit=10)],
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
    subprocess.run(
        ["git", "add", "demo.txt", "tests/test_demo.py", "scripts/change_demo.py"],
        cwd=project_root,
        check=True,
    )
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=project_root).returncode != 0:
        subprocess.run(
            ["git", "commit", "-m", "Add local app demo fixture"],
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


def _list_section(title: str, items: list[str], link: str | None = None) -> str:
    heading = f"<h2>{_e(title)}</h2>"
    if link:
        heading += f"<p><a href='{_e(link)}'>Open</a></p>"
    return f"<section>{heading}{_ul(items)}</section>"


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


def _coder_run_line(item: Any) -> str:
    return (
        f"<a href='/runs/{quote(item.id)}'>{_e(item.id)}</a>: {item.status} "
        f"project={item.project_id} changed={','.join(item.changed_files) or 'none'} "
        f"outside={','.join(item.outside_allowed_files) or 'none'}"
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
