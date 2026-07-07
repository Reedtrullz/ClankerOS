from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent_os.storage import CiSnapshotEvidenceRecord, Storage


GENERATED_READBACK_PATHS = (
    "docs/dashboard.md",
    "docs/self-hosting-check.md",
    "docs/next-iteration.md",
    ".clanker/ci-snapshots",
)


@dataclass(frozen=True)
class ProofSurfaceState:
    live_proof_state: str
    committed_dashboard_state: str
    generated_readback_state: str
    merge_claim: str
    head_commit: str
    remote_main_commit: str
    dashboard_snapshot_commit: str
    latest_ci_run_id: str
    latest_ci_scope: str
    non_claim: str
    project_id: str
    branch: str
    local_main_commit: str
    latest_ci_commit: str
    latest_ci_branch: str
    latest_ci_status: str
    latest_ci_evidence_path: str
    dashboard_status: str
    generated_readback_paths: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_proof_surface_state(
    root: Path,
    *,
    project_id: str = "clankeros",
    remote: str = "origin",
    branch: str = "main",
) -> ProofSurfaceState:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    head_commit = _git(root, ["rev-parse", "HEAD"]) or "unknown"
    current_branch = _git(root, ["branch", "--show-current"]) or "unknown"
    local_main_commit = _git(root, ["rev-parse", "--verify", f"refs/heads/{branch}"]) or "none"
    remote_main_commit = (
        _git(root, ["rev-parse", "--verify", f"refs/remotes/{remote}/{branch}"]) or "none"
    )
    dashboard_snapshot_commit = (
        _git(root, ["log", "-n", "1", "--format=%H", "--", "docs/dashboard.md"]) or "none"
    )
    dashboard_status = _git_status(root, "docs/dashboard.md")
    generated_status = _git_status(root, *GENERATED_READBACK_PATHS)

    latest_record = _latest_ci_record(storage, project_id=project_id)
    latest_full_success = _latest_full_success_ci_record(storage, project_id=project_id)

    latest_scope = _record_scope(latest_record)
    latest_run_id = latest_record.external_run_id if latest_record is not None else "none"
    latest_commit = latest_record.commit_sha if latest_record is not None else "none"
    latest_branch = latest_record.branch_name if latest_record is not None else "none"
    latest_status = latest_record.status if latest_record is not None else "missing"
    latest_path = latest_record.evidence_path if latest_record is not None else "none"

    full_record_matches_head = (
        latest_full_success is not None
        and _commit_refs_match(latest_full_success.commit_sha, head_commit)
    )
    head_matches_main = _commit_refs_match(head_commit, local_main_commit) or _commit_refs_match(
        head_commit,
        remote_main_commit,
    )
    if full_record_matches_head and head_matches_main:
        live_proof_state = "current_main_same_sha"
        merge_claim = "current_main_proof_valid"
    elif full_record_matches_head:
        live_proof_state = "branch_same_sha"
        merge_claim = "branch_proof_only"
    else:
        live_proof_state = "missing_or_stale"
        merge_claim = "no_merge_claim"

    if dashboard_status:
        committed_dashboard_state = "modified_local_readback"
    elif dashboard_snapshot_commit != "none":
        committed_dashboard_state = "committed_snapshot"
    else:
        committed_dashboard_state = "missing_snapshot"

    generated_paths = _status_paths(generated_status)
    generated_readback_state = (
        "local_uncommitted_readback" if generated_paths else "no_local_readback"
    )

    return ProofSurfaceState(
        live_proof_state=live_proof_state,
        committed_dashboard_state=committed_dashboard_state,
        generated_readback_state=generated_readback_state,
        merge_claim=merge_claim,
        head_commit=head_commit,
        remote_main_commit=remote_main_commit,
        dashboard_snapshot_commit=dashboard_snapshot_commit,
        latest_ci_run_id=latest_run_id,
        latest_ci_scope=latest_scope,
        non_claim="proof_surface_does_not_record_ci_or_mutate_external_systems",
        project_id=project_id,
        branch=current_branch,
        local_main_commit=local_main_commit,
        latest_ci_commit=latest_commit,
        latest_ci_branch=latest_branch,
        latest_ci_status=latest_status,
        latest_ci_evidence_path=latest_path,
        dashboard_status=dashboard_status or "clean",
        generated_readback_paths=generated_paths,
    )


def render_proof_surface_cli_lines(state: ProofSurfaceState) -> list[str]:
    data = state.to_dict()
    ordered_keys = [
        "live_proof_state",
        "committed_dashboard_state",
        "generated_readback_state",
        "merge_claim",
        "head_commit",
        "remote_main_commit",
        "dashboard_snapshot_commit",
        "latest_ci_run_id",
        "latest_ci_scope",
        "non_claim",
        "project_id",
        "branch",
        "local_main_commit",
        "latest_ci_commit",
        "latest_ci_branch",
        "latest_ci_status",
        "latest_ci_evidence_path",
        "dashboard_status",
    ]
    lines = [f"{key}: {data[key]}" for key in ordered_keys]
    paths = ",".join(state.generated_readback_paths) if state.generated_readback_paths else "none"
    lines.append(f"generated_readback_paths: {paths}")
    lines.extend(
        [
            "network_actions_taken: 0",
            "external_mutations_taken: 0",
            "provider_calls_taken: 0",
            "deploy_created: false",
        ]
    )
    return lines


def render_proof_surface_dashboard_lines(state: ProofSurfaceState) -> list[str]:
    return [
        f"- live_proof_state: {state.live_proof_state}",
        f"- committed_dashboard_state: {state.committed_dashboard_state}",
        f"- generated_readback_state: {state.generated_readback_state}",
        f"- merge_claim: {state.merge_claim}",
        f"- head_commit: {state.head_commit}",
        f"- remote_main_commit: {state.remote_main_commit}",
        f"- dashboard_snapshot_commit: {state.dashboard_snapshot_commit}",
        f"- latest_ci_run_id: {state.latest_ci_run_id}",
        f"- latest_ci_scope: {state.latest_ci_scope}",
        f"- non_claim: {state.non_claim}",
        "- network_actions_taken: 0",
        "- external_mutations_taken: 0",
        "- provider_calls_taken: 0",
        "- deploy_created: false",
    ]


def _latest_ci_record(
    storage: Storage,
    *,
    project_id: str,
) -> CiSnapshotEvidenceRecord | None:
    for record in storage.list_recent_ci_snapshot_evidence_records(limit=None):
        if record.project_id == project_id:
            return record
    return None


def _latest_full_success_ci_record(
    storage: Storage,
    *,
    project_id: str,
) -> CiSnapshotEvidenceRecord | None:
    for record in storage.list_recent_ci_snapshot_evidence_records(limit=None):
        if (
            record.project_id == project_id
            and record.status == "success"
            and _record_scope(record) == "workflow_run"
        ):
            return record
    return None


def _record_scope(record: CiSnapshotEvidenceRecord | None) -> str:
    if record is None:
        return "none"
    return str((record.result_json or {}).get("evidence_scope", "unknown"))


def _git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _git_status(root: Path, *paths: str) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain", "-uall", "--", *paths],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.rstrip()


def _status_paths(status_text: str) -> list[str]:
    paths: list[str] = []
    for line in status_text.splitlines():
        if not line.strip():
            continue
        paths.append(line[3:].strip() if len(line) > 3 else line.strip())
    return paths


def _commit_refs_match(left: str, right: str) -> bool:
    left = (left or "").strip()
    right = (right or "").strip()
    if not left or not right or left == "none" or right == "none" or left == "unknown" or right == "unknown":
        return False
    return left == right or left.startswith(right) or right.startswith(left)
