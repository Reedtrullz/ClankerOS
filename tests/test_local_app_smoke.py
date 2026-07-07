from pathlib import Path

from agent_os.cli import main
from agent_os.local_app import render_local_app_route, validate_bind_host
from agent_os.local_app_smoke import (
    run_local_app_demo_smoke_test,
    run_local_app_golden_path_smoke_test,
)


def test_github_actions_workflow_runs_automatic_verification() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    workflow_path = repo_root / ".github" / "workflows" / "tests.yml"
    workflow = workflow_path.read_text(encoding="utf-8")

    for expected in [
        "push:",
        '      - "codex/**"',
        "pull_request:",
        "workflow_dispatch:",
        "permissions:",
        "contents: read",
        "smoke:",
        "name: Fast smoke verification",
        "timeout-minutes: 10",
        "full-suite:",
        "name: Full pytest suite",
        "needs: smoke",
        "timeout-minutes: 45",
        'python-version: "3.10"',
        "python -m compileall -q agent_os tests",
        "CLANKEROS_CI_ROOT: ${{ runner.temp }}/clankeros-ci-root",
        "CLANKEROS_GOLDEN_ROOT: ${{ runner.temp }}/clankeros-golden-root",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" init",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" app-smoke-test",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" demo-app-scenario",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" app-demo-smoke-test",
        "python -m agent_os.cli --root \"$CLANKEROS_GOLDEN_ROOT\" app-golden-path-smoke-test",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" app --help",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" dashboard",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" iterate",
        "Run focused local app pytest smoke",
        "ci_snapshot_evidence_from_gh_json_validates_successful_matching_run",
        "ci_snapshot_evidence_from_gh_json_records_completed_job_while_run_in_progress",
        "ci_snapshot_evidence_from_gh_json_rejects_pending_or_wrong_commit",
        "local_app_records_ci_snapshot_evidence_from_pasted_gh_json",
        "local_app_records_fast_smoke_ci_snapshot_evidence_from_pasted_gh_json",
        "local_app_rejects_pending_ci_snapshot_status_json_without_record",
        "github_actions_smoke_uses_temp_root_and_expected_order",
        "local_app_artifact_viewer_is_read_only_and_bounded",
        "local_app_demo_scenario_populates_fixture_state",
        "local_app_fresh_user_no_docs_golden_path_smoke",
        "operator_first_viewports_show_goal_phase_action_proof_finish_resume",
        "git diff --check",
        "python -m pytest -q",
        "--durations=25",
        "--durations-min=1.0",
    ]:
        assert expected in workflow


def test_github_actions_smoke_uses_temp_root_and_expected_order() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    workflow = (repo_root / ".github" / "workflows" / "tests.yml").read_text(
        encoding="utf-8"
    )

    ordered_markers = [
        "python -m compileall -q agent_os tests",
        "CLANKEROS_CI_ROOT: ${{ runner.temp }}/clankeros-ci-root",
        "CLANKEROS_GOLDEN_ROOT: ${{ runner.temp }}/clankeros-golden-root",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" init",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" app-smoke-test",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" demo-app-scenario",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" app-demo-smoke-test",
        "python -m agent_os.cli --root \"$CLANKEROS_GOLDEN_ROOT\" app-golden-path-smoke-test",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" app --help",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" dashboard",
        "python -m agent_os.cli --root \"$CLANKEROS_CI_ROOT\" iterate",
        "python -m pytest tests/test_first_milestone.py tests/test_local_app_smoke.py -q -k",
        "git diff --check",
        "full-suite:",
        "python -m pytest -q",
        "--durations=25",
    ]
    positions = [workflow.index(marker) for marker in ordered_markers]
    assert positions == sorted(positions)

    focused_pytest_line = next(
        line
        for line in workflow.splitlines()
        if "python -m pytest tests/test_first_milestone.py tests/test_local_app_smoke.py -q -k"
        in line
    )
    for expected_test in [
        "github_actions_workflow_runs_automatic_verification",
        "github_actions_smoke_uses_temp_root_and_expected_order",
        "ci_snapshot_evidence_from_gh_json_validates_successful_matching_run",
        "ci_snapshot_evidence_from_gh_json_records_completed_job_while_run_in_progress",
        "ci_snapshot_evidence_from_gh_json_rejects_pending_or_wrong_commit",
        "local_app_records_ci_snapshot_evidence_from_pasted_gh_json",
        "local_app_records_fast_smoke_ci_snapshot_evidence_from_pasted_gh_json",
        "local_app_rejects_pending_ci_snapshot_status_json_without_record",
        "ci_snapshot_handoff_prints_watch_and_record_commands_without_writes",
        "local_app_routes_render_modern_workflow_and_health",
        "local_app_runs_delegation_from_browser_action",
        "goal_runs_approved_worktree_from_browser_action",
        "local_app_artifact_viewer_is_read_only_and_bounded",
        "local_app_demo_scenario_populates_fixture_state",
        "local_app_cli_commands_and_bind_safety",
        "local_app_fresh_user_no_docs_golden_path_smoke",
        "operator_first_viewports_show_goal_phase_action_proof_finish_resume",
    ]:
        assert expected_test in focused_pytest_line


def test_local_app_favicon_route_is_quiet_for_browser_qa(tmp_path: Path) -> None:
    response = render_local_app_route(tmp_path, "/favicon.ico")

    assert response.status == 204
    assert response.body == ""
    assert response.content_type == "image/x-icon"
    assert response.headers == {"cache-control": "max-age=86400"}
    assert not (tmp_path / ".clanker").exists()


def test_local_app_cli_commands_and_bind_safety(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["--root", str(tmp_path), "app-smoke-test"]) == 0
    smoke_output = capsys.readouterr().out
    assert "app_smoke_test: passed" in smoke_output
    assert "route /goals: 200 marker=matched required_marker=Goal Cockpit" in smoke_output
    assert "route /search: 200 marker=matched required_marker=Global Search" in smoke_output
    assert "route /workspace: 200 marker=matched required_marker=Workspace State" in smoke_output
    assert "route /memory: 200 marker=matched required_marker=Memory Bank" in smoke_output
    assert "route /skills: 200 marker=matched required_marker=Skills Inventory" in smoke_output
    assert "route /profiles: 200 marker=matched required_marker=Profiles And Routing" in smoke_output
    assert "route /workflow: 200 marker=matched required_marker=Modern Operator Workflow" in smoke_output
    assert "route /actions: 200 marker=matched required_marker=Safe Action Catalog" in smoke_output
    assert "route /verification: 200 marker=matched required_marker=Verification Handoff" in smoke_output
    assert "route /ci-evidence: 200 marker=matched required_marker=CI Evidence Records" in smoke_output
    assert "route /dogfooding: 200 marker=matched required_marker=Manual Dogfooding Checklist" in smoke_output
    assert "route /inbox: 200 marker=matched required_marker=Operator Inbox" in smoke_output
    assert "route /artifacts?path=.clanker/app/smoke-artifacts/sample.md: 200 marker=matched required_marker=artifact_type" in smoke_output
    assert "absolute artifact paths are rejected" in smoke_output
    assert "parent traversal is rejected" in smoke_output
    assert "outside repo root" in smoke_output
    assert "marker=missing" not in smoke_output
    assert "network_actions_taken: 0" in smoke_output

    assert main(["--root", str(tmp_path), "app-demo"]) == 0
    demo_output = capsys.readouterr().out
    assert "demo_app_scenario: ready" in demo_output
    assert "fixture_backed: true" in demo_output
    assert "network_actions_taken: 0" in demo_output

    assert main(["--root", str(tmp_path), "demo"]) == 0
    short_demo_output = capsys.readouterr().out
    assert "demo_app_scenario: ready" in short_demo_output
    assert "fixture_backed: true" in short_demo_output
    assert "network_actions_taken: 0" in short_demo_output

    demo_smoke = run_local_app_demo_smoke_test(tmp_path)
    assert demo_smoke["status"] == "passed"
    assert demo_smoke["fixture_backed"] is True
    assert demo_smoke["network_actions_taken"] == 0
    assert demo_smoke["external_mutations_taken"] == 0
    assert all(not route["missing_snippets"] for route in demo_smoke["routes"])

    assert main(["--root", str(tmp_path), "app-demo-smoke-test"]) == 0
    demo_smoke_output = capsys.readouterr().out
    assert "app_demo_smoke_test: passed" in demo_smoke_output
    assert "route /demo: 200 marker=matched required_marker=Demo Scenario expected_snippets=matched" in demo_smoke_output
    assert "route /dogfooding: 200 marker=matched required_marker=Manual Dogfooding Checklist expected_snippets=matched" in demo_smoke_output
    assert "route /workflow?run_id=" in demo_smoke_output
    assert "expected_snippets=missing" not in demo_smoke_output
    demo_route = next(route for route in demo_smoke["routes"] if route["route"] == "/demo")
    for expected_snippet in [
        "confirmation_required: true_for_local_writes",
        "form_action: /actions/coder-commit-request",
        "external_effects_created: false",
    ]:
        assert expected_snippet in demo_route["expected_snippets"]
    assert "fixture_backed: true" in demo_smoke_output
    assert "network_actions_taken: 0" in demo_smoke_output

    try:
        validate_bind_host("0.0.0.0")
    except ValueError as error:
        assert "refusing non-local bind host" in str(error)
    else:
        raise AssertionError("expected non-local bind to be rejected")
    validate_bind_host("0.0.0.0", allow_nonlocal_bind=True)


def test_local_app_fresh_user_no_docs_golden_path_smoke(
    tmp_path: Path,
    capsys,
) -> None:
    direct_root = tmp_path / "direct"
    smoke = run_local_app_golden_path_smoke_test(direct_root)
    assert smoke["status"] == "passed"
    assert smoke["project_id"] == "golden-path"
    assert smoke["goal_id"].startswith("goal_")
    assert smoke["delegation_id"].startswith("subagent_delegation_")
    assert smoke["proof_artifact"].endswith("/implementation_handoff.md")
    assert (direct_root / smoke["proof_artifact"]).exists()
    assert smoke["proof_exists"] is True
    assert smoke["workspace_resume_surface"] == "/today#today-current-action"
    assert smoke["workspace_ok"] is True
    assert smoke["network_actions_taken"] == 0
    assert smoke["external_mutations_taken"] == 0
    assert [check["name"] for check in smoke["checks"]] == [
        "open-home",
        "open-today-first-run",
        "confirm-create-project",
        "create-project",
        "confirm-create-goal",
        "create-goal",
        "open-today-create-action",
        "confirm-next-action",
        "do-next-action",
        "confirm-context-pack",
        "create-context-pack",
        "confirm-proof-run",
        "run-proof",
        "check-proof-artifact",
        "confirm-finish-today",
        "finish-today",
        "resume-tomorrow",
    ]
    assert all(check["passed"] for check in smoke["checks"])

    cli_root = tmp_path / "cli"
    assert main(["--root", str(cli_root), "app-golden-path-smoke-test"]) == 0
    output = capsys.readouterr().out
    assert "app_golden_path_smoke_test: passed" in output
    assert "project_id: golden-path" in output
    assert "goal_id: goal_" in output
    assert "delegation_id: subagent_delegation_" in output
    assert "proof_artifact: .clanker/delegations/" in output
    assert "implementation_handoff.md" in output
    assert "proof_exists: true" in output
    assert "workspace_resume_surface: /today#today-current-action" in output
    assert "workspace_ok: true" in output
    assert "check resume-tomorrow: 200 expected_status=200 snippets=matched" in output
    assert "snippets=missing" not in output
    assert "network_actions_taken: 0" in output
    assert "external_mutations_taken: 0" in output


def test_operator_first_viewports_show_goal_phase_action_proof_finish_resume(
    tmp_path: Path,
) -> None:
    smoke = run_local_app_golden_path_smoke_test(tmp_path)
    assert smoke["status"] == "passed"

    def assert_first_viewport(body: str, prefix: str, later_marker: str) -> None:
        strip_marker = f"data-{prefix}-first-viewport='true'"
        assert strip_marker in body
        strip_start = body.index(strip_marker)
        assert strip_start < body.index(later_marker)
        for key, label in [
            ("goal", "Goal"),
            ("phase", "Phase"),
            ("next-action", "Next Action"),
            ("proof", "Proof"),
            ("finish", "Finish"),
            ("resume", "Resume"),
        ]:
            card_marker = f"data-{prefix}-first-viewport-card='{key}'"
            assert card_marker in body[strip_start:]
            card_start = body.index(card_marker, strip_start)
            assert f"<h3>{label}</h3>" in body[card_start : card_start + 500]
        assert (
            f"{prefix}_first_viewport_order: "
            "Goal -> Phase -> Next Action -> Proof -> Finish -> Resume"
        ) in body
        assert f"{prefix}_first_viewport_write_on_get</dt><dd>false" in body
        assert f"{prefix}_first_viewport_network_actions_taken</dt><dd>0" in body
        assert f"{prefix}_first_viewport_external_effects_created</dt><dd>false" in body

    today = render_local_app_route(tmp_path, "/today")
    assert today.status == 200
    assert_first_viewport(today.body, "today", "data-today-command-actions='true'")
    assert "today_first_viewport_goal</dt><dd><a href='/goals/" in today.body
    assert "today_first_viewport_phase</dt><dd>Coder prep" in today.body
    assert "today_first_viewport_next_action</dt><dd>Run coder prep" in today.body
    assert "today_first_viewport_proof_status</dt><dd>latest_artifact_available" in today.body
    assert "today_first_viewport_finish_status</dt><dd>ready" in today.body
    assert "today_first_viewport_resume_status</dt><dd>ready" in today.body

    resume = render_local_app_route(tmp_path, "/resume")
    assert resume.status == 200
    assert_first_viewport(resume.body, "resume", "data-resume-command-evidence='true'")
    assert "resume_first_viewport_goal</dt><dd><a href='/goals/" in resume.body
    assert "resume_first_viewport_phase</dt><dd>Coder prep" in resume.body
    assert "resume_first_viewport_next_action</dt><dd>Run coder prep" in resume.body
    assert "resume_first_viewport_proof_status</dt><dd>saved_artifact_available" in resume.body
    assert "resume_first_viewport_finish_status</dt><dd>ready_to_update" in resume.body

    goal = render_local_app_route(tmp_path, f"/goals/{smoke['goal_id']}")
    assert goal.status == 200
    assert_first_viewport(goal.body, "goal", "data-goal-control-strip='true'")
    assert "goal_first_viewport_goal</dt><dd><a href='/goals/" in goal.body
    assert "goal_first_viewport_phase</dt><dd>Coder prep" in goal.body
    assert "goal_first_viewport_next_action</dt><dd>Run coder prep" in goal.body
    assert "goal_first_viewport_finish_status</dt><dd>saved" in goal.body
    assert "goal_first_viewport_resume_status</dt><dd>ready" in goal.body
