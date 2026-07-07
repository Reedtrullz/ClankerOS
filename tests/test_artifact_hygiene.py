import json
import subprocess
from pathlib import Path

from agent_os.artifact_hygiene import write_artifact_hygiene_report
from agent_os.cli import main


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "clankeros@example.invalid")
    _git(repo, "config", "user.name", "ClankerOS Test")
    _git(repo, "config", "commit.gpgsign", "false")
    (repo / ".gitignore").write_text(".agent/\n.clanker/app/\n", encoding="utf-8")
    tracked = repo / ".clanker" / "delegations" / "tracked" / "evidence.json"
    tracked.parent.mkdir(parents=True, exist_ok=True)
    tracked.write_text("{}\n", encoding="utf-8")
    _git(repo, "add", ".gitignore", ".clanker/delegations/tracked/evidence.json")
    _git(repo, "commit", "-m", "initial evidence")


def test_artifact_hygiene_reports_categories_without_cleanup(
    tmp_path: Path,
    capsys,
) -> None:
    _init_repo(tmp_path)
    original_gitignore = (tmp_path / ".gitignore").read_text(encoding="utf-8")
    ignored = tmp_path / ".agent" / "state.db"
    ignored.parent.mkdir()
    ignored.write_text("ignored runtime\n", encoding="utf-8")
    unpromoted = (
        tmp_path
        / ".clanker"
        / "ci-snapshots"
        / "clankeros"
        / "abc123"
        / "snapshot.json"
    )
    unpromoted.parent.mkdir(parents=True)
    unpromoted.write_text("{}\n", encoding="utf-8")
    visible = tmp_path / ".clanker" / "delegations" / "new" / "result.json"
    visible.parent.mkdir(parents=True)
    visible.write_text("{}\n", encoding="utf-8")
    generated = tmp_path / "runs" / "run_001" / "output.txt"
    generated.parent.mkdir(parents=True)
    generated.write_text("local run\n", encoding="utf-8")
    unknown = tmp_path / "scratch.txt"
    unknown.write_text("review me\n", encoding="utf-8")

    assert main(["--root", str(tmp_path), "artifact-hygiene"]) == 0
    output = capsys.readouterr().out
    assert "artifact_hygiene: written" in output
    assert "tracked_intentional: 1" in output
    assert "ignored_runtime_state: 1" in output
    assert "unpromoted_proof: 1" in output
    assert "generated_local_artifact: 1" in output
    assert "visible_evidence_candidate: 1" in output
    assert "unknown_needs_operator_review: 1" in output
    assert "deleted: 0" in output
    assert "gitignore_changes: 0" in output

    latest_json = tmp_path / ".clanker" / "artifact-hygiene" / "latest.json"
    latest_md = tmp_path / ".clanker" / "artifact-hygiene" / "latest.md"
    assert latest_json.exists()
    assert latest_md.exists()
    payload = json.loads(latest_json.read_text(encoding="utf-8"))
    assert payload["deleted"] == 0
    assert payload["gitignore_changes"] == 0
    assert payload["counts"]["tracked_intentional"] == 1
    assert payload["counts"]["ignored_runtime_state"] == 1
    assert payload["counts"]["unpromoted_proof"] == 1
    assert payload["counts"]["generated_local_artifact"] == 1
    assert payload["counts"]["visible_evidence_candidate"] == 1
    assert payload["counts"]["unknown_needs_operator_review"] == 1
    assert (tmp_path / ".gitignore").read_text(encoding="utf-8") == original_gitignore
    for path in [ignored, unpromoted, visible, generated, unknown]:
        assert path.exists()


def test_artifact_hygiene_classifies_its_own_report_as_generated_local_artifact(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    first = write_artifact_hygiene_report(tmp_path)
    assert first.counts["generated_local_artifact"] == 0

    second = write_artifact_hygiene_report(tmp_path)
    assert second.counts["generated_local_artifact"] == 2
    assert second.counts["unknown_needs_operator_review"] == 0
