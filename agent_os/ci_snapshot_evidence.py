from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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
    status_source: str = "operator_supplied",
    status_json: dict[str, Any] | None = None,
    evidence_scope: str = "workflow_run",
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

    scope = evidence_scope.strip() or "workflow_run"
    idempotency_parts = [
        project,
        branch,
        commit,
        source_provider,
        run_id,
        url,
        normalized_status,
    ]
    if scope != "workflow_run":
        idempotency_parts.append(scope)
    idempotency_key = ":".join(idempotency_parts)
    existing = storage.get_ci_snapshot_evidence_by_idempotency_key(idempotency_key)
    if existing is not None:
        return CiSnapshotEvidenceResult(
            status="already_recorded",
            record=existing,
            message="CI snapshot evidence already recorded",
        )

    evidence_dir = root / ".clanker" / "ci-snapshots" / _slug(project) / _slug(commit)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    scope_suffix = "" if scope == "workflow_run" else f"-{_slug(scope)}"
    evidence_path = evidence_dir / (
        f"ci-snapshot-evidence-{_slug(source_provider)}-{_slug(run_id)}"
        f"{scope_suffix}.json"
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
        "status_source": status_source,
        "evidence_scope": scope,
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
    if status_json is not None:
        result_json["validated_status_json"] = status_json
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


def record_ci_snapshot_evidence_from_gh_status_json(
    root: Path,
    *,
    project_id: str,
    branch_name: str,
    commit_sha: str,
    provider: str,
    external_run_id: str,
    status_json_text: str,
    external_url: str | None = None,
    recorded_by: str = "operator",
    note: str = "",
    job_name: str | None = None,
) -> CiSnapshotEvidenceResult:
    try:
        payload = json.loads(status_json_text)
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid GitHub status JSON: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("GitHub status JSON must be an object")

    status = str(payload.get("status", "")).strip().lower()
    conclusion = str(payload.get("conclusion", "")).strip().lower()
    head_sha = str(payload.get("headSha", "")).strip()
    head_branch = str(payload.get("headBranch", "")).strip()
    if head_sha != commit_sha:
        raise ValueError(
            "GitHub run headSha does not match commit: "
            f"expected {commit_sha}, got {head_sha or 'missing'}"
        )
    if head_branch and head_branch != branch_name:
        raise ValueError(
            "GitHub run headBranch does not match branch: "
            f"expected {branch_name}, got {head_branch}"
        )

    run_url = (external_url or str(payload.get("url", ""))).strip()
    if not run_url:
        raise ValueError("GitHub status JSON did not include url; pass --url")

    job = None
    requested_job_name = (job_name or "").strip()
    if requested_job_name:
        jobs = payload.get("jobs", [])
        if not isinstance(jobs, list):
            raise ValueError("GitHub status JSON jobs field must be a list")
        matches = [
            item
            for item in jobs
            if isinstance(item, dict)
            and str(item.get("name", "")).strip() == requested_job_name
        ]
        if len(matches) != 1:
            raise ValueError(
                "GitHub status JSON did not contain exactly one matching job: "
                f"job_name={requested_job_name} matches={len(matches)}"
            )
        job = matches[0]
        job_status = str(job.get("status", "")).strip().lower()
        job_conclusion = str(job.get("conclusion", "")).strip().lower()
        if job_status != "completed" or job_conclusion != "success":
            raise ValueError(
                "GitHub job is not successful: "
                f"job={requested_job_name} status={job_status or 'missing'} "
                f"conclusion={job_conclusion or 'missing'}"
            )
    elif status != "completed" or conclusion != "success":
        raise ValueError(
            "GitHub run is not successful: "
            f"status={status or 'missing'} conclusion={conclusion or 'missing'}"
        )

    validated_payload = {
        "status": status,
        "conclusion": conclusion,
        "headSha": head_sha,
        "headBranch": head_branch or None,
        "url": run_url,
        "jobs": payload.get("jobs", []),
    }
    status_source = "github_status_json"
    evidence_scope = "workflow_run"
    if job is not None:
        validated_payload["validatedJob"] = {
            "name": requested_job_name,
            "status": str(job.get("status", "")).strip().lower(),
            "conclusion": str(job.get("conclusion", "")).strip().lower(),
        }
        status_source = "github_status_json_job"
        evidence_scope = f"workflow_job:{requested_job_name}"
    return record_ci_snapshot_evidence(
        root,
        project_id=project_id,
        branch_name=branch_name,
        commit_sha=commit_sha,
        provider=provider,
        status="success",
        external_run_id=external_run_id,
        external_url=run_url,
        recorded_by=recorded_by,
        note=note,
        status_source=status_source,
        status_json=validated_payload,
        evidence_scope=evidence_scope,
    )


def _safe_branch(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9._/-]+", value)) and ".." not in value


def _safe_commit(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Fa-f0-9]{7,64}", value))


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return slug or "unknown"
