import json
import subprocess
from pathlib import Path

from agent_os.ci_snapshot_evidence import record_ci_snapshot_evidence
from agent_os.cli import main
from agent_os.proof_surface import build_proof_surface_state
from agent_os.self_hosting_check import run_next_day_self_hosting_check
from agent_os.dashboard import generate_static_dashboard


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(repo: Path) -> str:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "clankeros@example.invalid")
    _git(repo, "config", "user.name", "ClankerOS Test")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / "docs").mkdir()
    (repo / "docs" / "dashboard.md").write_text("# Dashboard\n\nsnapshot\n", encoding="utf-8")
    (repo / "README.md").write_text("# Repo\n", encoding="utf-8")
    _git(repo, "add", "README.md", "docs/dashboard.md")
    _git(repo, "commit", "-m", "initial")
    return _git(repo, "rev-parse", "HEAD")


def _record_full_success(repo: Path, commit: str, *, branch: str = "main") -> None:
    record_ci_snapshot_evidence(
        repo,
        project_id="clankeros",
        branch_name=branch,
        commit_sha=commit,
        provider="github-actions",
        status="success",
        external_run_id="12345",
        external_url="https://github.com/Reedtrullz/ClankerOS/actions/runs/12345",
    )


def test_proof_surface_distinguishes_current_main_snapshot_and_local_readback(
    tmp_path: Path,
) -> None:
    commit = _init_repo(tmp_path)
    _record_full_success(tmp_path, commit)

    clean = build_proof_surface_state(tmp_path)
    assert clean.live_proof_state == "current_main_same_sha"
    assert clean.committed_dashboard_state == "committed_snapshot"
    assert clean.generated_readback_state == "local_uncommitted_readback"
    assert clean.merge_claim == "current_main_proof_valid"
    assert clean.head_commit == commit
    assert clean.remote_main_commit == "none"
    assert clean.dashboard_snapshot_commit == commit
    assert clean.latest_ci_run_id == "12345"
    assert clean.latest_ci_scope == "workflow_run"
    assert clean.non_claim == "proof_surface_does_not_record_ci_or_mutate_external_systems"

    (tmp_path / "docs" / "dashboard.md").write_text(
        "# Dashboard\n\nlocal generated readback\n",
        encoding="utf-8",
    )
    snapshot_dir = tmp_path / ".clanker" / "ci-snapshots" / "clankeros" / commit
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    (snapshot_dir / "local.json").write_text("{}\n", encoding="utf-8")

    dirty = build_proof_surface_state(tmp_path)
    assert dirty.live_proof_state == "current_main_same_sha"
    assert dirty.committed_dashboard_state == "modified_local_readback"
    assert dirty.generated_readback_state == "local_uncommitted_readback"
    assert dirty.merge_claim == "current_main_proof_valid"
    assert "docs/dashboard.md" in dirty.generated_readback_paths
    assert "ocs/dashboard.md" not in dirty.generated_readback_paths


def test_proof_surface_avoids_merge_claim_for_branch_or_stale_proof(tmp_path: Path) -> None:
    _init_repo(tmp_path)
    _git(tmp_path, "checkout", "-b", "feature/proof")
    (tmp_path / "README.md").write_text("# Repo\n\nbranch proof\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "branch proof")
    branch_commit = _git(tmp_path, "rev-parse", "HEAD")
    _record_full_success(tmp_path, branch_commit, branch="feature/proof")

    branch_state = build_proof_surface_state(tmp_path)
    assert branch_state.live_proof_state == "branch_same_sha"
    assert branch_state.merge_claim == "branch_proof_only"

    (tmp_path / "README.md").write_text("# Repo\n\nnew head\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "new head")

    stale = build_proof_surface_state(tmp_path)
    assert stale.live_proof_state == "missing_or_stale"
    assert stale.merge_claim == "no_merge_claim"


def test_proof_surface_cli_self_hosting_and_dashboard_surface_state(
    tmp_path: Path,
    capsys,
) -> None:
    commit = _init_repo(tmp_path)
    _record_full_success(tmp_path, commit)

    assert main(["--root", str(tmp_path), "proof-surface"]) == 0
    output = capsys.readouterr().out
    assert "live_proof_state: current_main_same_sha" in output
    assert "committed_dashboard_state: committed_snapshot" in output
    assert "merge_claim: current_main_proof_valid" in output

    result = run_next_day_self_hosting_check(tmp_path, fetch_mode="none")
    assert result.payload["proof_surface"]["live_proof_state"] == "current_main_same_sha"
    report = result.report_path.read_text(encoding="utf-8")
    assert "## Proof Surface" in report
    assert "- Merge claim: `current_main_proof_valid`" in report

    dashboard_path = generate_static_dashboard(tmp_path)
    dashboard = dashboard_path.read_text(encoding="utf-8")
    assert "### Proof Surface" in dashboard
    assert "- live_proof_state: current_main_same_sha" in dashboard
