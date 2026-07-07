import subprocess
from pathlib import Path

from agent_os.ci_snapshot_evidence import record_ci_snapshot_evidence
from agent_os.local_app import render_local_app_route
from agent_os.local_app_smoke import run_local_app_golden_path_smoke_test


def _target_repo_commit(root: Path) -> str:
    repo = root / ".clanker" / "app" / "golden-path-target"
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _assert_secondary_details_after_first_viewport(body: str, prefix: str) -> None:
    first_marker = f"data-{prefix}-first-viewport='true'"
    details_marker = f"data-{prefix}-secondary-operator-details='true'"
    assert first_marker in body
    assert details_marker in body
    details_marker_start = body.index(details_marker)
    details_start = body.rfind("<details", 0, details_marker_start)
    details_open = body.index(">", details_start)
    details_tag = body[details_start:details_open]
    assert details_start > body.index(first_marker)
    assert " open" not in details_tag


def _assert_preserved_secondary_evidence(body: str) -> None:
    assert "900001" in body
    assert "success" in body
    assert "network_actions_taken" in body
    assert "external_effects_created" in body
    assert "implementation_handoff.md" in body


def test_operator_secondary_evidence_is_collapsed_after_first_viewport(
    tmp_path: Path,
) -> None:
    smoke = run_local_app_golden_path_smoke_test(tmp_path)
    assert smoke["status"] == "passed"
    commit = _target_repo_commit(tmp_path)
    record_ci_snapshot_evidence(
        tmp_path,
        project_id="golden-path",
        branch_name="main",
        commit_sha=commit,
        provider="github-actions",
        status="success",
        external_run_id="900001",
        external_url="https://github.com/Reedtrullz/ClankerOS/actions/runs/900001",
    )

    today = render_local_app_route(tmp_path, "/today")
    assert today.status == 200
    _assert_secondary_details_after_first_viewport(today.body, "today")
    _assert_preserved_secondary_evidence(today.body)
    assert "data-today-command-actions='true'" in today.body

    resume = render_local_app_route(tmp_path, "/resume")
    assert resume.status == 200
    _assert_secondary_details_after_first_viewport(resume.body, "resume")
    _assert_preserved_secondary_evidence(resume.body)
    assert "data-resume-workbench-action-form='true'" in resume.body

    goal = render_local_app_route(tmp_path, f"/goals/{smoke['goal_id']}")
    assert goal.status == 200
    _assert_secondary_details_after_first_viewport(goal.body, "goal")
    _assert_preserved_secondary_evidence(goal.body)
    assert "data-goal-action-dock='true'" in goal.body
