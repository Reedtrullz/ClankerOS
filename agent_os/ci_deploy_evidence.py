from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import CiDeployEvidenceRecord, Storage, utc_now


ALLOWED_CI_DEPLOY_STATUSES = {
    "success",
    "failure",
    "pending",
    "cancelled",
    "skipped",
}


@dataclass(frozen=True)
class CiDeployEvidenceResult:
    status: str
    record: CiDeployEvidenceRecord
    message: str


def record_ci_deploy_evidence(
    root: Path,
    *,
    github_handoff_id: str,
    provider: str,
    status: str,
    external_run_id: str,
    external_url: str,
    recorded_by: str = "operator",
    note: str = "",
) -> CiDeployEvidenceResult:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    normalized_status = status.strip().lower()
    if normalized_status not in ALLOWED_CI_DEPLOY_STATUSES:
        raise ValueError(
            "unsupported CI/deploy status: "
            f"{status}; expected one of {','.join(sorted(ALLOWED_CI_DEPLOY_STATUSES))}"
        )
    if not provider.strip():
        raise ValueError("provider is required")
    if not external_run_id.strip():
        raise ValueError("external run id is required")
    if not external_url.strip():
        raise ValueError("external URL is required")

    handoff = storage.get_github_handoff(github_handoff_id)
    if handoff is None:
        raise KeyError(github_handoff_id)

    idempotency_key = ":".join(
        [
            github_handoff_id,
            provider.strip(),
            external_run_id.strip(),
            external_url.strip(),
            normalized_status,
        ]
    )
    existing = storage.get_ci_deploy_evidence_by_idempotency_key(idempotency_key)
    if existing is not None:
        return CiDeployEvidenceResult(
            status="already_recorded",
            record=existing,
            message="CI/deploy evidence already recorded",
        )

    evidence_dir = Path(handoff.evidence_path).parent
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = (
        evidence_dir
        / f"ci-deploy-evidence-{handoff.id}-{_slug(provider)}-{_slug(external_run_id)}.json"
    )
    result_json = {
        "status": normalized_status,
        "provider": provider.strip(),
        "external_run_id": external_run_id.strip(),
        "external_url": external_url.strip(),
        "recorded_by": recorded_by,
        "note": note,
        "network_actions_taken": 0,
        "source": {
            "github_handoff_id": handoff.id,
            "effect_id": handoff.effect_id,
            "project_id": handoff.project_id,
            "run_id": handoff.run_id,
            "task_id": handoff.task_id,
            "branch_name": handoff.branch_name,
            "commit_sha": handoff.commit_sha,
            "handoff_evidence_path": handoff.evidence_path,
        },
        "created_at": utc_now(),
        "non_claims": [
            "Does not call the CI provider.",
            "Does not run CI.",
            "Does not deploy.",
            "Does not mutate GitHub or external systems.",
        ],
    }
    evidence_path.write_text(
        json.dumps(result_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    record = storage.record_ci_deploy_evidence(
        github_handoff_id=handoff.id,
        effect_id=handoff.effect_id,
        project_id=handoff.project_id,
        run_id=handoff.run_id,
        task_id=handoff.task_id,
        branch_name=handoff.branch_name,
        commit_sha=handoff.commit_sha,
        provider=provider.strip(),
        external_run_id=external_run_id.strip(),
        external_url=external_url.strip(),
        status=normalized_status,
        recorded_by=recorded_by,
        evidence_path=str(evidence_path),
        result_json=result_json,
        idempotency_key=idempotency_key,
    )
    return CiDeployEvidenceResult(
        status="recorded",
        record=record,
        message="CI/deploy evidence recorded from operator input",
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-")
    return slug or "unknown"
