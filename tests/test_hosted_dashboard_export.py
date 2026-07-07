import json
from pathlib import Path

from agent_os.cli import main


def test_hosted_dashboard_export_writes_static_local_bundle(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["--root", str(tmp_path), "init"]) == 0
    capsys.readouterr()

    assert main(["--root", str(tmp_path), "hosted-dashboard-export"]) == 0
    output = capsys.readouterr().out
    assert "hosted_dashboard_export: written" in output
    assert "output: .clanker/hosted-dashboard-export/index.html" in output
    assert "network_actions_taken: 0" in output
    assert "external_mutations_taken: 0" in output
    assert "deploy_created: false" in output

    index = tmp_path / ".clanker" / "hosted-dashboard-export" / "index.html"
    manifest_path = tmp_path / ".clanker" / "hosted-dashboard-export" / "manifest.json"
    assert index.exists()
    assert manifest_path.exists()
    html = index.read_text(encoding="utf-8")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "ClankerOS Read-Only Dashboard Export" in html
    assert "Proof Surface State" in html
    assert "Artifact Hygiene Summary" in html
    assert "<dt>network_actions_taken</dt><dd>0</dd>" in html
    assert "<dt>external_mutations_taken</dt><dd>0</dd>" in html
    assert "<dt>deploy_created</dt><dd>false</dd>" in html
    assert manifest["kind"] == "hosted_dashboard_export"
    assert manifest["network_actions_taken"] == 0
    assert manifest["external_mutations_taken"] == 0
    assert manifest["deploy_created"] is False
    assert manifest["dashboard_snapshot"]["state"] == "missing"
    assert "Does not deploy." in manifest["non_claims"]


def test_hosted_dashboard_export_includes_dashboard_proof_and_hygiene(
    tmp_path: Path,
    capsys,
) -> None:
    assert main(["--root", str(tmp_path), "init"]) == 0
    capsys.readouterr()
    (tmp_path / "status.md").write_text("# Root Status\n\nready\n", encoding="utf-8")
    (tmp_path / "docs").mkdir(exist_ok=True)
    (tmp_path / "docs" / "status.md").write_text(
        "# Docs Status\n\nsnapshot\n",
        encoding="utf-8",
    )
    assert main(["--root", str(tmp_path), "dashboard"]) == 0
    assert main(["--root", str(tmp_path), "proof-surface"]) == 0
    assert main(["--root", str(tmp_path), "artifact-hygiene"]) == 0
    capsys.readouterr()

    assert main(["--root", str(tmp_path), "hosted-dashboard-export"]) == 0
    html = (
        tmp_path / ".clanker" / "hosted-dashboard-export" / "index.html"
    ).read_text(encoding="utf-8")
    manifest = json.loads(
        (
            tmp_path / ".clanker" / "hosted-dashboard-export" / "manifest.json"
        ).read_text(encoding="utf-8")
    )
    assert "Agent System Dashboard" in html
    assert "Root Status" in html
    assert "Docs Status" in html
    assert "live_proof_state" in html
    assert "artifact_hygiene" not in html
    assert "Artifact Hygiene Summary" in html
    assert manifest["dashboard_snapshot"]["state"] == "available"
    assert manifest["status_summary"]["status_md"]["state"] == "available"
    assert manifest["status_summary"]["docs_status_md"]["state"] == "available"
    assert manifest["proof_surface"]["non_claim"] == (
        "proof_surface_does_not_record_ci_or_mutate_external_systems"
    )
    assert manifest["artifact_hygiene"]["status"] == "available"
    assert manifest["artifact_hygiene"]["deleted"] == 0
    assert manifest["artifact_hygiene"]["gitignore_changes"] == 0
