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
    create_coder_publication_handoff,
    list_coder_publications,
)
from agent_os.coder_worktree_execution import (
    CoderWorktreeApprovalError,
    approve_coder_worktree,
    approve_coder_worktree_commit,
    list_coder_worktree_approvals,
    list_coder_worktree_commit_approvals,
    list_coder_worktree_runs,
    request_coder_worktree_approval,
    request_coder_worktree_commit_approval,
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
    project_root: Path
    handoff_md: Path
    coder_prep_md: Path
    coder_worktree_plan_md: Path
    approval_id: str


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
            return _html_page(root, "Workflow", _workflow(root))
        if path == "/projects":
            return _html_page(root, "Projects", _projects(root))
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
    routes = ["/", "/workflow", "/projects", "/health", "/demo"]
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
        note="Demo approval request only; no execution.",
    ).approval
    write_local_app_status(root, host=DEFAULT_HOST, port=DEFAULT_PORT)
    return DemoScenarioResult(
        project_id=project.name,
        goal_id=goal_id,
        task_id=task_id,
        delegation_id=delegation.id,
        run_id=run_id,
        project_root=project_root,
        handoff_md=handoff_md,
        coder_prep_md=prep.markdown_path,
        coder_worktree_plan_md=plan.markdown_path,
        approval_id=approval.id,
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
        "routes_available": ["/", "/workflow", "/projects", "/delegations/<id>", "/runs/<id>", "/artifacts", "/health", "/demo"],
        "supported_workflow_stages": [step[0] for step in WORKFLOW_STEPS],
        "non_claims": NO_EXTERNAL_EFFECT_CLAIMS,
        "known_gaps": [
            "No authentication for localhost MVP.",
            "Execution and commit actions remain CLI-first in this initial app version.",
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
            _list_section("Incidents / Recommendations", rows["incidents"]),
            "<section><h2>Next Recommended Action</h2><p>Review the workflow page, run the demo scenario, then inspect a delegation or artifact.</p></section>",
        ]
    )


def _workflow(root: Path) -> str:
    return "".join(
        [
            "<section><h1>Modern Operator Workflow</h1>",
            _non_claim_banner(),
            _workflow_list(compact=False),
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
        _list_section("Coder Prep", _artifact_links(list_coder_prep_packets(root), delegation_id=delegation_id)),
        _list_section("Coder Worktree Plan", _artifact_links(list_coder_worktree_plan_packets(root), delegation_id=delegation_id)),
        _list_section("Worktree Approvals", [_approval_line(item) for item in list_coder_worktree_approvals(root, delegation_id=delegation_id, limit=20)]),
        _list_section("Worktree Runs", [_coder_run_line(item) for item in list_coder_worktree_runs(root, delegation_id=delegation_id, limit=20)]),
        _list_section("Commit Requests / Local Commits", [_commit_line(item) for item in list_coder_worktree_commit_approvals(root, delegation_id=delegation_id, limit=20)]),
        _list_section("Publication Requests / Handoffs", [_publication_line(root, item) for item in list_coder_publications(root, delegation_id=delegation_id, limit=20)]),
        _safe_action_forms(
            delegation_id=delegation_id,
            run_id=str(run_id),
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
        parts.append(
            _kv(
                [
                    ("coder_worktree_status", coder_run.status),
                    ("delegation_id", coder_run.delegation_id),
                    ("worktree_path", coder_run.worktree_path),
                    ("branch_name", coder_run.branch_name),
                    ("changed_files", ", ".join(coder_run.changed_files) or "none"),
                    ("outside_allowed_files", ", ".join(coder_run.outside_allowed_files) or "none"),
                    ("verification_exit_code", str(coder_run.verification_exit_code)),
                    ("evidence_path", coder_run.evidence_path),
                ]
            )
        )
    parts.append("</section>")
    return "".join(parts)


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
        if action == "context-pack":
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
                message=_required(form, "message"),
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
        CoderPublicationError,
    ) as error:
        return _html_page(root, "Action Error", f"<p class='error'>{_e(str(error))}</p>", status=400)
    return LocalAppResponse(
        303,
        "",
        headers={"Location": f"{location}?notice={quote(message)}"},
    )


def _safe_action_forms(*, delegation_id: str, run_id: str, handoff_md: str) -> str:
    return f"""
    <section><h2>Safe Local Actions</h2>
      <p class="muted">Artifact-producing actions require an explicit confirmation page. Execution, local commit, push, PR, deploy, provider, and arbitrary command actions are not exposed here.</p>
      {_form('implementation-handoff', {'delegation_id': delegation_id})}
      {_form('context-pack', {'delegation_id': delegation_id})}
      {_form('coder-prep', {'delegation_id': delegation_id})}
      {_form('coder-prep-from-handoff', {'handoff_md': handoff_md})}
      {_form('coder-worktree-plan', {'delegation_id': delegation_id})}
      {_form('coder-worktree-approval', {'delegation_id': delegation_id, 'note': 'Approve bounded worktree execution from local app'})}
      {_form('coder-publication-handoff', {'run_id': run_id})}
    </section>
    """


def _form(action: str, fields: dict[str, str]) -> str:
    inputs = "".join(
        f"<input type='hidden' name='{_e(key)}' value='{_e(value)}'>"
        for key, value in fields.items()
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
    <nav><a href="/">Dashboard</a><a href="/workflow">Workflow</a><a href="/projects">Projects</a><a href="/health">Health</a><a href="/demo">Demo</a></nav>
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
        "coder-publication-handoff",
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
    if not (project_root / ".git").exists():
        subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "demo@example.invalid"], cwd=project_root, check=True)
        subprocess.run(["git", "config", "user.name", "ClankerOS Demo"], cwd=project_root, check=True)
    subprocess.run(["git", "add", "demo.txt", "tests/test_demo.py"], cwd=project_root, check=True)
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


def _workflow_list(*, compact: bool) -> str:
    items = []
    for index, (label, command, mutation, required, output) in enumerate(WORKFLOW_STEPS, start=1):
        if compact:
            items.append(f"<li>{index}. {_e(label)} <code>{_e(command)}</code></li>")
        else:
            items.append(
                "<li>"
                f"<strong>{index}. {_e(label)}</strong>"
                + _kv(
                    [
                        ("command", command),
                        ("available", "true"),
                        ("mutates_local_state", str(mutation in {"local_state", "local_artifact", "local_approval", "local_execution", "local_git_only"}).lower()),
                        ("creates_external_effects", "false" if "Manual operator" not in label else "outside_clankeros"),
                        ("required_previous_artifact", required),
                        ("output_artifact", output),
                    ]
                )
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
