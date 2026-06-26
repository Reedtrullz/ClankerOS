from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from agent_os.ci_deploy_evidence import ALLOWED_CI_DEPLOY_STATUSES
from agent_os.storage import CiSnapshotEvidenceRecord, Storage, utc_now


@dataclass(frozen=True)
class CiSnapshotEvidenceResult:
    status: str
    record: CiSnapshotEvidenceRecord
    message: str


def record_ci_snapshot_evidence(
    root: Path,
    *,
    project_id: str,
    branch_name: str,
    commit_sha: str,
    provider: str,
    status: str,
    external_run_id: str,
    external_url: str,
    recorded_by: str = "operator",
    note: str = "",
) -> CiSnapshotEvidenceResult:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    normalized_status = status.strip().lower()
    if normalized_status not in ALLOWED_CI_DEPLOY_STATUSES:
        raise ValueError(
            "unsupported CI snapshot status: "
            f"{status}; expected one of {','.join(sorted(ALLOWED_CI_DEPLOY_STATUSES))}"
        )
    project = project_id.strip()
    branch = branch_name.strip()
    commit = commit_sha.strip()
    source_provider = provider.strip()
    run_id = external_run_id.strip()
    url = external_url.strip()
    if not project:
        raise ValueError("project is required")
    if not branch:
        raise ValueError("branch is required")
    if not _safe_branch(branch):
        raise ValueError("unsafe branch")
    if not commit:
        raise ValueError("commit is required")
    if not _safe_commit(commit):
        raise ValueError("unsafe commit")
    if not source_provider:
        raise ValueError("provider is required")
    if not run_id:
        raise ValueError("external run id is required")
    if not url:
        raise ValueError("external URL is required")

    idempotency_key = ":".join(
        [project, branch, commit, source_provider, run_id, url, normalized_status]
    )
    existing = storage.get_ci_snapshot_evidence_by_idempotency_key(idempotency_key)
    if existing is not None:
        return CiSnapshotEvidenceResult(
            status="already_recorded",
            record=existing,
            message="CI snapshot evidence already recorded",
        )

    evidence_dir = root / ".clanker" / "ci-snapshots" / _slug(project) / _slug(commit)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = (
        evidence_dir
        / f"ci-snapshot-evidence-{_slug(source_provider)}-{_slug(run_id)}.json"
    )
    result_json = {
        "kind": "ci_snapshot_evidence",
        "schema_version": 1,
        "status": normalized_status,
        "provider": source_provider,
        "external_run_id": run_id,
        "external_url": url,
        "recorded_by": recorded_by,
        "note": note,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "source": {
            "source_kind": "direct_public_snapshot",
            "project_id": project,
            "branch_name": branch,
            "commit_sha": commit,
        },
        "created_at": utc_now(),
        "non_claims": [
            "Does not call the CI provider.",
            "Does not run CI.",
            "Does not deploy.",
            "Does not mutate GitHub or external systems.",
            "Records operator-supplied proof for a direct pushed snapshot, not a publication handoff.",
        ],
    }
    evidence_path.write_text(
        json.dumps(result_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    record = storage.record_ci_snapshot_evidence(
        project_id=project,
        branch_name=branch,
        commit_sha=commit,
        provider=source_provider,
        external_run_id=run_id,
        external_url=url,
        status=normalized_status,
        recorded_by=recorded_by,
        evidence_path=str(evidence_path),
        result_json=result_json,
        idempotency_key=idempotency_key,
    )
    return CiSnapshotEvidenceResult(
        status="recorded",
        record=record,
        message="CI snapshot evidence recorded from operator input",
    )


def _safe_branch(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._/-]+", value)) and ".." not in value


def _safe_commit(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Fa-f0-9]{7,64}", value))


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return slug or "unknown"
