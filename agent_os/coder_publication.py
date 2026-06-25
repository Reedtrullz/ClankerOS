from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.coder_worktree_execution import (
    CODER_LOCAL_COMMIT_KIND,
    CoderWorktreeCommitError,
    _ensure_tables as _ensure_coder_worktree_tables,
    _validate_git_worktree_safe,
    _validate_worktree_path_boundary,
    get_coder_worktree_run,
)
from agent_os.ids import new_id
from agent_os.storage import Storage, utc_now


PUBLICATION_REQUEST_KIND = "coder_worktree_publication_request"
PUBLICATION_DECISION_KIND = "coder_worktree_publication_approval_decision"
PUBLICATION_HANDOFF_KIND = "coder_worktree_publication_handoff"


class CoderPublicationError(ValueError):
    pass


@dataclass(frozen=True)
class CoderPublicationRecord:
    id: str
    run_id: str
    delegation_id: str
    source_run_id: str
    project_id: str
    status: str
    failure_class: str | None
    source_commit_artifact_path: str
    source_commit_artifact_sha256: str
    worktree_path: str
    branch_name: str
    commit_sha: str
    parent_commit_sha: str
    remote: str
    target_branch: str
    request_artifact_path: str
    decision_artifact_path: str | None
    handoff_artifact_path: str
    requested_by: str
    request_note: str
    decided_by: str | None
    decision_note: str | None
    requested_at: str
    decided_at: str | None
    handoff_at: str | None


@dataclass(frozen=True)
class CoderPublicationRequestResult:
    publication: CoderPublicationRecord
    already_recorded: bool = False


@dataclass(frozen=True)
class CoderPublicationDecisionResult:
    publication: CoderPublicationRecord
    already_approved: bool = False


@dataclass(frozen=True)
class CoderPublicationHandoffResult:
    publication: CoderPublicationRecord
    status: str
    artifact_path: str
    already_ready: bool = False


def request_coder_publication(
    root: Path,
    storage: Storage,
    run_id: str,
    *,
    requested_by: str,
    remote: str = "origin",
    target_branch: str = "main",
    note: str,
    force_new: bool = False,
) -> CoderPublicationRequestResult:
    root = root.resolve()
    _ensure_tables(storage)
    _validate_remote_name(remote)
    _validate_branch_name(target_branch, failure_class="unsafe_target_branch")
    context = _load_commit_context(root, storage, run_id)
    _validate_commit_context(root, context)
    commit_artifact_sha = _sha256_path(context["commit_artifact_path"])
    existing = (
        None
        if force_new
        else _latest_publication_for_source(
            storage,
            run_id=run_id,
            source_commit_artifact_sha256=commit_artifact_sha,
            remote=remote,
            target_branch=target_branch,
        )
    )
    if existing is not None:
        return CoderPublicationRequestResult(publication=existing, already_recorded=True)

    publication_id = new_id("coder_publication_request")
    now = utc_now()
    publication_dir = context["publication_dir"]
    request_artifact = publication_dir / "publication_request.json"
    decision_artifact = publication_dir / "publication_decision.json"
    handoff_artifact = publication_dir / "publication_handoff.json"
    payload = _publication_request_payload(
        root=root,
        publication_id=publication_id,
        context=context,
        source_commit_artifact_sha256=commit_artifact_sha,
        remote=remote,
        target_branch=target_branch,
        requested_by=requested_by,
        note=note,
        requested_at=now,
    )
    _write_json(request_artifact, payload)
    _write_text(request_artifact.with_suffix(".md"), _render_publication_request_markdown(payload))
    publication = _insert_publication(
        storage,
        publication_id=publication_id,
        run_id=run_id,
        delegation_id=context["run"].delegation_id,
        source_run_id=context["run"].source_run_id,
        project_id=context["run"].project_id,
        source_commit_artifact_path=str(context["commit_artifact_path"].relative_to(root)),
        source_commit_artifact_sha256=commit_artifact_sha,
        worktree_path=context["commit_payload"]["worktree_path"],
        branch_name=context["commit_payload"]["branch_name"],
        commit_sha=context["commit_payload"]["commit_sha"],
        parent_commit_sha=context["commit_payload"]["parent_commit_sha"],
        remote=remote,
        target_branch=target_branch,
        request_artifact_path=str(request_artifact.relative_to(root)),
        decision_artifact_path=str(decision_artifact.relative_to(root)),
        handoff_artifact_path=str(handoff_artifact.relative_to(root)),
        requested_by=requested_by,
        request_note=note,
        requested_at=now,
    )
    return CoderPublicationRequestResult(publication=publication)


def approve_coder_publication(
    root: Path,
    storage: Storage,
    publication_id: str,
    *,
    decided_by: str,
    note: str,
) -> CoderPublicationDecisionResult:
    root = root.resolve()
    _ensure_tables(storage)
    publication = get_coder_publication(storage, publication_id)
    if publication is None:
        raise CoderPublicationError(f"publication request not found: {publication_id}")
    if publication.status in {"approved", "ready_for_operator"}:
        return CoderPublicationDecisionResult(
            publication=publication,
            already_approved=True,
        )
    if publication.status != "pending_operator_approval":
        raise CoderPublicationError(f"publication approval is not pending: {publication.status}")

    request_artifact = root / publication.request_artifact_path
    if not request_artifact.exists():
        raise CoderPublicationError("publication request artifact missing")
    decided_at = utc_now()
    payload = {
        "kind": PUBLICATION_DECISION_KIND,
        "schema_version": 1,
        "publication_request_id": publication.id,
        "coder_worktree_run_id": publication.run_id,
        "delegation_id": publication.delegation_id,
        "project_id": publication.project_id,
        "source_request_sha256": _sha256_path(request_artifact),
        "status": "approved",
        "decided_by": decided_by,
        "note": note,
        "decided_at": decided_at,
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Approving publication does not push.",
            "Approving publication does not create a PR.",
            "Approving publication does not deploy.",
            "Approving publication does not call providers or use the network.",
        ],
    }
    decision_path = root / (publication.decision_artifact_path or "")
    _write_json(decision_path, payload)
    _write_text(decision_path.with_suffix(".md"), _render_publication_decision_markdown(payload))
    updated = _mark_publication_approved(
        storage,
        publication.id,
        decided_by=decided_by,
        decision_note=note,
        decided_at=decided_at,
    )
    return CoderPublicationDecisionResult(publication=updated)


def create_coder_publication_handoff(
    root: Path,
    storage: Storage,
    run_id: str,
) -> CoderPublicationHandoffResult:
    root = root.resolve()
    _ensure_tables(storage)
    publication = _latest_publication_for_run(storage, run_id)
    if publication is None or publication.status == "pending_operator_approval":
        raise CoderPublicationError("approved publication request is missing")
    if publication.status == "blocked":
        raise CoderPublicationError(f"publication request is blocked: {publication.failure_class or 'unknown'}")
    if publication.status not in {"approved", "ready_for_operator"}:
        raise CoderPublicationError(f"publication request is not approved: {publication.status}")

    context = _load_commit_context(root, storage, run_id)
    _validate_commit_context(root, context)
    current_hash = _sha256_path(context["commit_artifact_path"])
    if current_hash != publication.source_commit_artifact_sha256:
        _block_publication(storage, publication.id, failure_class="source_hash_mismatch")
        raise CoderPublicationError(f"source_hash_mismatch: {publication.id}")
    if publication.status == "ready_for_operator" and (root / publication.handoff_artifact_path).exists():
        return CoderPublicationHandoffResult(
            publication=publication,
            status="already_ready",
            artifact_path=publication.handoff_artifact_path,
            already_ready=True,
        )

    payload = _publication_handoff_payload(root, publication, context)
    handoff_path = root / publication.handoff_artifact_path
    _write_json(handoff_path, payload)
    _write_text(handoff_path.with_suffix(".md"), _render_publication_handoff_markdown(payload))
    body_path = Path(payload["handoff_body_path"])
    _write_text(body_path, _render_publication_pr_body(payload))
    updated = _mark_publication_ready(storage, publication.id, handoff_at=payload["created_at"])
    return CoderPublicationHandoffResult(
        publication=updated,
        status="ready_for_operator",
        artifact_path=publication.handoff_artifact_path,
    )


def record_coder_publication_failure_incident(
    root: Path,
    storage: Storage,
    *,
    command: str,
    target_id: str,
    error: CoderPublicationError,
) -> str:
    _ensure_tables(storage)
    error_text = str(error)
    failure_class = _publication_failure_class_from_error(error_text)
    publication = get_coder_publication(storage, target_id)
    run = get_coder_worktree_run(storage, target_id)
    if publication is None and run is None:
        publication = _latest_publication_for_run(storage, target_id)
    run_id = target_id
    delegation_id = "unknown"
    project_id = "unknown"
    evidence_path: str | None = None
    if publication is not None:
        run_id = publication.run_id
        delegation_id = publication.delegation_id
        project_id = publication.project_id
        evidence_path = publication.handoff_artifact_path or publication.request_artifact_path
    elif run is not None:
        run_id = run.id
        delegation_id = run.delegation_id
        project_id = run.project_id
        evidence_path = run.evidence_path
    evidence = {
        "failure_class": failure_class,
        "summary": error_text,
        "command": command,
        "target_id": target_id,
        "coder_worktree_run_id": run_id,
        "delegation_id": delegation_id,
        "project_id": project_id,
        "evidence_path": evidence_path,
        "next_recommended_operator_action": _publication_failure_next_action(failure_class),
    }
    return storage.record_incident(
        project_id=project_id,
        run_id=run_id,
        goal_id=None,
        task_id=delegation_id,
        task_type="coder_publication",
        incident_type="coder_publication_failure",
        severity="medium",
        status="open",
        summary=f"Coder publication gate failed: {failure_class}",
        failure_class=failure_class,
        verification_method="coder_publication_gate",
        verification_path=evidence_path,
        failed_checks=[failure_class],
        evidence=evidence,
        artifacts=[evidence_path] if evidence_path else [],
        evidence_path=evidence_path,
    )


def render_coder_publication_request_cli_lines(
    root: Path,
    result: CoderPublicationRequestResult,
) -> list[str]:
    publication = result.publication
    prefix = "already_recorded " if result.already_recorded else ""
    return [
        f"coder_publication_request: {prefix}{publication.id}",
        f"publication_request_id: {publication.id}",
        f"coder_worktree_run_id: {publication.run_id}",
        f"delegation_id: {publication.delegation_id}",
        f"project_id: {publication.project_id}",
        f"status: {publication.status}",
        f"failure_class: {publication.failure_class or 'none'}",
        f"commit: {publication.commit_sha}",
        f"parent_commit: {publication.parent_commit_sha}",
        f"worktree_path: {publication.worktree_path}",
        f"branch: {publication.branch_name}",
        f"remote: {publication.remote}",
        f"target_branch: {publication.target_branch}",
        f"artifact: {publication.request_artifact_path}",
        "push_created: false",
        "pr_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_publication_decision_cli_lines(
    root: Path,
    result: CoderPublicationDecisionResult,
) -> list[str]:
    publication = result.publication
    prefix = "already_approved " if result.already_approved else ""
    return [
        f"approved_coder_publication: {prefix}{publication.id}",
        f"publication_request_id: {publication.id}",
        f"coder_worktree_run_id: {publication.run_id}",
        f"delegation_id: {publication.delegation_id}",
        f"project_id: {publication.project_id}",
        f"status: {publication.status}",
        f"artifact: {publication.decision_artifact_path or 'none'}",
        "push_created: false",
        "pr_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_publication_handoff_cli_lines(
    root: Path,
    result: CoderPublicationHandoffResult,
) -> list[str]:
    publication = result.publication
    payload = json.loads((root.resolve() / result.artifact_path).read_text(encoding="utf-8"))
    return [
        f"coder_publication_handoff: {result.status}",
        f"publication_request_id: {publication.id}",
        f"coder_worktree_run_id: {publication.run_id}",
        f"delegation_id: {publication.delegation_id}",
        f"project_id: {publication.project_id}",
        f"status: {publication.status}",
        f"commit: {publication.commit_sha}",
        f"parent_commit: {publication.parent_commit_sha}",
        f"worktree_path: {publication.worktree_path}",
        f"branch: {publication.branch_name}",
        f"remote: {publication.remote}",
        f"target_branch: {publication.target_branch}",
        f"suggested_push_command: {payload['suggested_push_command']}",
        f"suggested_draft_pr_command: {payload['suggested_draft_pr_command']}",
        f"handoff_body_path: {payload['handoff_body_path']}",
        f"artifact: {result.artifact_path}",
        "push_created: false",
        "pr_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
        "next_recommended_action: operator_may_manually_push_or_create_draft_pr",
    ]


def render_coder_publication_request_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for publication in list_coder_publications(root, limit=10):
        lines.append(
            f"- {publication.id}: delegation={publication.delegation_id} "
            f"project={publication.project_id} run={publication.run_id} "
            f"status={publication.status} commit={publication.commit_sha} "
            f"branch={publication.branch_name} remote={publication.remote} "
            f"target_branch={publication.target_branch} "
            f"request={publication.request_artifact_path} "
            "push_created=false pr_created=false deploy_created=false "
            "network_actions_taken=0 external_mutations_taken=0"
        )
    return lines


def render_coder_publication_handoff_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for publication in list_coder_publications(root, status="ready_for_operator", limit=10):
        payload = load_coder_publication_handoff_payload(root, publication)
        lines.append(
            f"- {publication.id}: delegation={publication.delegation_id} "
            f"project={publication.project_id} run={publication.run_id} "
            f"commit={publication.commit_sha} branch={publication.branch_name} "
            f"remote={publication.remote} target_branch={publication.target_branch} "
            f"handoff={publication.handoff_artifact_path} "
            f"suggested_push_command={payload.get('suggested_push_command', 'unavailable')} "
            f"suggested_draft_pr_command={payload.get('suggested_draft_pr_command', 'unavailable')} "
            f"handoff_body_path={payload.get('handoff_body_path', 'unavailable')} "
            "next_action=operator_may_manually_push_or_create_draft_pr "
            "push_created=false pr_created=false deploy_created=false"
        )
    return lines


def render_coder_publication_review_lines(root: Path, delegation_id: str) -> list[str]:
    lines: list[str] = []
    for publication in list_coder_publications(root, delegation_id=delegation_id, limit=10):
        handoff_available = publication.status == "ready_for_operator"
        payload = load_coder_publication_handoff_payload(root, publication)
        lines.extend(
            [
                f"- delegation={delegation_id} coder_publication_request={publication.request_artifact_path}",
                f"  - publication_request_id: {publication.id}",
                f"  - run_id: {publication.run_id}",
                f"  - status: {publication.status}",
                f"  - failure_class: {publication.failure_class or 'none'}",
                f"  - commit_sha: {publication.commit_sha}",
                f"  - parent_commit_sha: {publication.parent_commit_sha}",
                f"  - worktree_path: {publication.worktree_path}",
                f"  - branch_name: {publication.branch_name}",
                f"  - remote: {publication.remote}",
                f"  - target_branch: {publication.target_branch}",
                f"  - handoff_available: {_bool(handoff_available)}",
                f"  - coder_publication_handoff: {publication.handoff_artifact_path if handoff_available else 'none'}",
                f"  - suggested_push_command: {payload.get('suggested_push_command', 'none') if handoff_available else 'none'}",
                f"  - suggested_draft_pr_command: {payload.get('suggested_draft_pr_command', 'none') if handoff_available else 'none'}",
                f"  - handoff_body_path: {payload.get('handoff_body_path', 'none') if handoff_available else 'none'}",
                "  - push_created: false",
                "  - pr_created: false",
                "  - deploy_created: false",
                "  - network_actions_taken: 0",
                "  - next_recommended_action: operator_may_manually_push_or_create_draft_pr" if handoff_available else "  - next_recommended_action: approve_or_prepare_coder_publication",
                "  - non_claims: publication handoff only; no push, PR, deploy, provider call, or network action",
            ]
        )
    return lines


def list_coder_publications(
    root: Path,
    *,
    delegation_id: str | None = None,
    status: str | None = None,
    limit: int | None = 10,
) -> list[CoderPublicationRecord]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    if not storage.db_path.exists():
        return []
    _ensure_tables(storage)
    clauses: list[str] = []
    params: list[object] = []
    if delegation_id is not None:
        clauses.append("delegation_id = ?")
        params.append(delegation_id)
    if status is not None:
        clauses.append("status = ?")
        params.append(status)
    where = f"where {' and '.join(clauses)}" if clauses else ""
    query = (
        f"select * from coder_worktree_publication_approvals {where} "
        "order by requested_at desc, id desc"
    )
    if limit is not None:
        query += " limit ?"
        params.append(limit)
    with _connect(storage) as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [_row_to_publication(row) for row in rows]


def latest_coder_publication_for_delegation(
    root: Path,
    delegation_id: str,
) -> CoderPublicationRecord | None:
    publications = list_coder_publications(root, delegation_id=delegation_id, limit=1)
    return publications[0] if publications else None


def get_coder_publication(
    storage: Storage,
    publication_id: str,
) -> CoderPublicationRecord | None:
    _ensure_tables(storage)
    with _connect(storage) as connection:
        row = connection.execute(
            "select * from coder_worktree_publication_approvals where id = ?",
            (publication_id,),
        ).fetchone()
    return _row_to_publication(row) if row is not None else None


def load_coder_publication_handoff_payload(
    root: Path,
    publication: CoderPublicationRecord,
) -> dict[str, Any]:
    handoff_path = root.resolve() / publication.handoff_artifact_path
    if publication.status != "ready_for_operator" or not handoff_path.exists():
        return {}
    try:
        return json.loads(handoff_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _ensure_tables(storage: Storage) -> None:
    _ensure_coder_worktree_tables(storage)
    with _connect(storage) as connection:
        connection.executescript(
            """
            create table if not exists coder_worktree_publication_approvals (
                id text primary key,
                run_id text not null,
                delegation_id text not null,
                source_run_id text not null,
                project_id text not null,
                status text not null,
                failure_class text,
                source_commit_artifact_path text not null,
                source_commit_artifact_sha256 text not null,
                worktree_path text not null,
                branch_name text not null,
                commit_sha text not null,
                parent_commit_sha text not null,
                remote text not null,
                target_branch text not null,
                request_artifact_path text not null,
                decision_artifact_path text,
                handoff_artifact_path text not null,
                requested_by text not null,
                request_note text not null,
                decided_by text,
                decision_note text,
                requested_at text not null,
                decided_at text,
                handoff_at text
            );

            create index if not exists idx_coder_worktree_publications_run
                on coder_worktree_publication_approvals (
                    run_id,
                    source_commit_artifact_sha256,
                    remote,
                    target_branch,
                    status
                );
            create index if not exists idx_coder_worktree_publications_delegation
                on coder_worktree_publication_approvals (delegation_id, requested_at);
            """
        )


def _connect(storage: Storage) -> sqlite3.Connection:
    connection = sqlite3.connect(storage.db_path)
    connection.row_factory = sqlite3.Row
    return connection


def _insert_publication(
    storage: Storage,
    *,
    publication_id: str,
    run_id: str,
    delegation_id: str,
    source_run_id: str,
    project_id: str,
    source_commit_artifact_path: str,
    source_commit_artifact_sha256: str,
    worktree_path: str,
    branch_name: str,
    commit_sha: str,
    parent_commit_sha: str,
    remote: str,
    target_branch: str,
    request_artifact_path: str,
    decision_artifact_path: str,
    handoff_artifact_path: str,
    requested_by: str,
    request_note: str,
    requested_at: str,
) -> CoderPublicationRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            insert into coder_worktree_publication_approvals (
                id, run_id, delegation_id, source_run_id, project_id, status,
                source_commit_artifact_path, source_commit_artifact_sha256,
                worktree_path, branch_name, commit_sha, parent_commit_sha,
                remote, target_branch, request_artifact_path,
                decision_artifact_path, handoff_artifact_path, requested_by,
                request_note, requested_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                publication_id,
                run_id,
                delegation_id,
                source_run_id,
                project_id,
                "pending_operator_approval",
                source_commit_artifact_path,
                source_commit_artifact_sha256,
                worktree_path,
                branch_name,
                commit_sha,
                parent_commit_sha,
                remote,
                target_branch,
                request_artifact_path,
                decision_artifact_path,
                handoff_artifact_path,
                requested_by,
                request_note,
                requested_at,
            ),
        )
        row = connection.execute(
            "select * from coder_worktree_publication_approvals where id = ?",
            (publication_id,),
        ).fetchone()
    return _row_to_publication(row)


def _mark_publication_approved(
    storage: Storage,
    publication_id: str,
    *,
    decided_by: str,
    decision_note: str,
    decided_at: str,
) -> CoderPublicationRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_publication_approvals
            set status = 'approved',
                decided_by = ?,
                decision_note = ?,
                decided_at = ?,
                failure_class = null
            where id = ?
            """,
            (decided_by, decision_note, decided_at, publication_id),
        )
        row = connection.execute(
            "select * from coder_worktree_publication_approvals where id = ?",
            (publication_id,),
        ).fetchone()
    return _row_to_publication(row)


def _mark_publication_ready(
    storage: Storage,
    publication_id: str,
    *,
    handoff_at: str,
) -> CoderPublicationRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_publication_approvals
            set status = 'ready_for_operator',
                handoff_at = ?,
                failure_class = null
            where id = ?
            """,
            (handoff_at, publication_id),
        )
        row = connection.execute(
            "select * from coder_worktree_publication_approvals where id = ?",
            (publication_id,),
        ).fetchone()
    return _row_to_publication(row)


def _block_publication(
    storage: Storage,
    publication_id: str,
    *,
    failure_class: str,
) -> CoderPublicationRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_publication_approvals
            set status = 'blocked',
                failure_class = ?
            where id = ?
            """,
            (failure_class, publication_id),
        )
        row = connection.execute(
            "select * from coder_worktree_publication_approvals where id = ?",
            (publication_id,),
        ).fetchone()
    return _row_to_publication(row)


def _latest_publication_for_source(
    storage: Storage,
    *,
    run_id: str,
    source_commit_artifact_sha256: str,
    remote: str,
    target_branch: str,
) -> CoderPublicationRecord | None:
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_publication_approvals
            where run_id = ?
              and source_commit_artifact_sha256 = ?
              and remote = ?
              and target_branch = ?
              and status in ('pending_operator_approval', 'approved', 'ready_for_operator')
            order by requested_at desc, id desc
            limit 1
            """,
            (run_id, source_commit_artifact_sha256, remote, target_branch),
        ).fetchone()
    return _row_to_publication(row) if row is not None else None


def _latest_publication_for_run(
    storage: Storage,
    run_id: str,
) -> CoderPublicationRecord | None:
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_publication_approvals
            where run_id = ?
              and status in ('approved', 'ready_for_operator', 'pending_operator_approval', 'blocked')
            order by requested_at desc, id desc
            limit 1
            """,
            (run_id,),
        ).fetchone()
    return _row_to_publication(row) if row is not None else None


def _latest_committed_approval_for_run(storage: Storage, run_id: str) -> sqlite3.Row | None:
    _ensure_coder_worktree_tables(storage)
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_commit_approvals
            where run_id = ?
              and status = 'committed'
              and commit_sha is not null
            order by committed_at desc, id desc
            limit 1
            """,
            (run_id,),
        ).fetchone()
    return row


def _load_commit_context(root: Path, storage: Storage, run_id: str) -> dict[str, Any]:
    run = get_coder_worktree_run(storage, run_id)
    if run is None:
        raise CoderPublicationError(f"coder worktree run not found: {run_id}")
    approval_row = _latest_committed_approval_for_run(storage, run_id)
    if approval_row is None:
        raise CoderPublicationError("local commit artifact missing")
    evidence_dir = root / run.evidence_path
    commit_artifact_path = evidence_dir / "coder_commit" / "commit.json"
    if not commit_artifact_path.exists():
        raise CoderPublicationError("local commit artifact missing")
    try:
        commit_payload = json.loads(commit_artifact_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CoderPublicationError("local commit artifact unreadable") from error
    return {
        "run": run,
        "commit_approval": approval_row,
        "evidence_dir": evidence_dir,
        "commit_artifact_path": commit_artifact_path,
        "commit_payload": commit_payload,
        "publication_dir": evidence_dir / "coder_publication",
    }


def _validate_commit_context(root: Path, context: dict[str, Any]) -> None:
    payload = context["commit_payload"]
    if payload.get("kind") != CODER_LOCAL_COMMIT_KIND:
        raise CoderPublicationError("local commit artifact has unexpected kind")
    commit_sha = str(payload.get("commit_sha") or "")
    if not commit_sha:
        raise CoderPublicationError("commit_sha_missing")
    worktree_path = Path(str(payload.get("worktree_path") or ""))
    if not worktree_path.exists():
        raise CoderPublicationError("missing_worktree")
    branch_name = str(payload.get("branch_name") or "")
    _validate_branch_name(branch_name, failure_class="unsafe_branch")
    try:
        _validate_worktree_path_boundary(root, worktree_path)
        _validate_git_worktree_safe(worktree_path, branch_name)
    except CoderWorktreeCommitError as error:
        raise CoderPublicationError(f"unsafe_git_state: {error}") from error
    _git_output(["cat-file", "-e", f"{commit_sha}^{{commit}}"], cwd=worktree_path)
    allowed_files = set(payload.get("allowed_files") or [])
    committed_files = list(payload.get("committed_files") or [])
    outside_files = [
        path for path in committed_files if path not in allowed_files
    ] + list(payload.get("outside_allowed_files") or [])
    if outside_files:
        raise CoderPublicationError("outside_allowed_files_present")
    if payload.get("push_created") is not False:
        raise CoderPublicationError("publication_state_already_mutated")
    if payload.get("pr_created") is not False:
        raise CoderPublicationError("publication_state_already_mutated")
    if payload.get("deploy_created") is not False:
        raise CoderPublicationError("publication_state_already_mutated")
    if int(payload.get("provider_calls_taken_by_clankeros") or 0) != 0:
        raise CoderPublicationError("publication_state_already_mutated")
    if int(payload.get("network_actions_taken") or 0) != 0:
        raise CoderPublicationError("publication_state_already_mutated")
    if int(payload.get("external_mutations_taken") or 0) != 0:
        raise CoderPublicationError("publication_state_already_mutated")


def _publication_request_payload(
    *,
    root: Path,
    publication_id: str,
    context: dict[str, Any],
    source_commit_artifact_sha256: str,
    remote: str,
    target_branch: str,
    requested_by: str,
    note: str,
    requested_at: str,
) -> dict[str, Any]:
    run = context["run"]
    payload = context["commit_payload"]
    return {
        "kind": PUBLICATION_REQUEST_KIND,
        "schema_version": 1,
        "publication_request_id": publication_id,
        "coder_worktree_run_id": run.id,
        "delegation_id": run.delegation_id,
        "project_id": run.project_id,
        "worktree_path": payload["worktree_path"],
        "branch_name": payload["branch_name"],
        "commit_sha": payload["commit_sha"],
        "parent_commit_sha": payload["parent_commit_sha"],
        "commit_artifact": str(context["commit_artifact_path"].relative_to(root)),
        "commit_artifact_sha256": source_commit_artifact_sha256,
        "remote": remote,
        "target_branch": target_branch,
        "requested_by": requested_by,
        "note": note,
        "status": "pending_operator_approval",
        "approval_required_before": [
            "prepare_push_command",
            "prepare_draft_pr_command",
        ],
        "committed_files": payload.get("committed_files", []),
        "outside_allowed_files": payload.get("outside_allowed_files", []),
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "requested_at": requested_at,
        "non_claims": [
            "Publication request does not push.",
            "Publication request does not create a PR.",
            "Publication request does not deploy.",
            "Publication request does not call providers or use the network.",
        ],
    }


def _publication_handoff_payload(
    root: Path,
    publication: CoderPublicationRecord,
    context: dict[str, Any],
) -> dict[str, Any]:
    payload = context["commit_payload"]
    handoff_path = root / publication.handoff_artifact_path
    body_path = handoff_path.with_name("publication_handoff_body.md")
    title = str(payload.get("commit_message") or f"Publish coder worktree commit {publication.commit_sha}")
    push_command = f"git push {publication.remote} {publication.branch_name}"
    draft_pr_command = (
        f"gh pr create --draft --base {publication.target_branch} "
        f"--head {publication.branch_name} --title \"{title}\" --body-file {body_path}"
    )
    return {
        "kind": PUBLICATION_HANDOFF_KIND,
        "schema_version": 1,
        "coder_worktree_run_id": publication.run_id,
        "delegation_id": publication.delegation_id,
        "project_id": publication.project_id,
        "worktree_path": publication.worktree_path,
        "branch_name": publication.branch_name,
        "commit_sha": publication.commit_sha,
        "parent_commit_sha": publication.parent_commit_sha,
        "remote": publication.remote,
        "target_branch": publication.target_branch,
        "committed_files": payload.get("committed_files", []),
        "verification_exit_code": payload.get("verification_exit_code"),
        "verification_status": "passed"
        if payload.get("verification_exit_code") == 0
        else "unknown",
        "bounded_file_validation": payload.get(
            "bounded_file_validation",
            {"valid": not payload.get("outside_allowed_files", []), "status": "unknown"},
        ),
        "diff_path": str(context["commit_artifact_path"].with_name("committed_diff.patch")),
        "suggested_push_command": push_command,
        "suggested_draft_pr_command": draft_pr_command,
        "handoff_body_path": str(body_path),
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "next_recommended_action": "operator_may_manually_push_or_create_draft_pr",
        "created_at": utc_now(),
        "non_claims": [
            "Publication handoff did not push.",
            "Publication handoff did not create a PR.",
            "Publication handoff did not deploy.",
            "Publication handoff did not call providers or use the network.",
            "Suggested commands require separate manual operator execution.",
        ],
    }


def _row_to_publication(row: sqlite3.Row) -> CoderPublicationRecord:
    return CoderPublicationRecord(
        id=row["id"],
        run_id=row["run_id"],
        delegation_id=row["delegation_id"],
        source_run_id=row["source_run_id"],
        project_id=row["project_id"],
        status=row["status"],
        failure_class=row["failure_class"],
        source_commit_artifact_path=row["source_commit_artifact_path"],
        source_commit_artifact_sha256=row["source_commit_artifact_sha256"],
        worktree_path=row["worktree_path"],
        branch_name=row["branch_name"],
        commit_sha=row["commit_sha"],
        parent_commit_sha=row["parent_commit_sha"],
        remote=row["remote"],
        target_branch=row["target_branch"],
        request_artifact_path=row["request_artifact_path"],
        decision_artifact_path=row["decision_artifact_path"],
        handoff_artifact_path=row["handoff_artifact_path"],
        requested_by=row["requested_by"],
        request_note=row["request_note"],
        decided_by=row["decided_by"],
        decision_note=row["decision_note"],
        requested_at=row["requested_at"],
        decided_at=row["decided_at"],
        handoff_at=row["handoff_at"],
    )


def _validate_remote_name(remote: str) -> None:
    if not _safe_git_name(remote):
        raise CoderPublicationError("unsafe_remote")


def _validate_branch_name(branch_name: str, *, failure_class: str) -> None:
    if not _safe_git_name(branch_name):
        raise CoderPublicationError(failure_class)


def _safe_git_name(value: str) -> bool:
    if not value or value.startswith("-") or value.endswith("/") or ".." in value or "@{" in value:
        return False
    if any(char.isspace() for char in value):
        return False
    return bool(re.fullmatch(r"[A-Za-z0-9._/\-]+", value))


def _publication_failure_class_from_error(error_text: str) -> str:
    mapping = [
        ("coder worktree run not found", "missing_coder_worktree_run"),
        ("local commit artifact missing", "missing_local_commit"),
        ("commit_sha_missing", "missing_commit_sha"),
        ("commit_sha_not_found", "commit_sha_not_found"),
        ("missing_worktree", "missing_worktree"),
        ("unsafe_remote", "unsafe_remote"),
        ("unsafe_target_branch", "unsafe_target_branch"),
        ("unsafe_branch", "unsafe_branch"),
        ("unsafe_git_state", "unsafe_git_state"),
        ("source_hash_mismatch", "source_hash_mismatch"),
        ("approved publication request is missing", "missing_publication_approval"),
        ("publication request is not approved", "publication_not_approved"),
        ("publication approval is not pending", "publication_not_pending"),
        ("outside_allowed_files_present", "outside_allowed_files_present"),
        ("publication_state_already_mutated", "publication_state_already_mutated"),
        ("publication request artifact missing", "evidence_write_failed"),
    ]
    for needle, failure_class in mapping:
        if needle in error_text:
            return failure_class
    return "publication_failed"


def _publication_failure_next_action(failure_class: str) -> str:
    if failure_class in {
        "missing_local_commit",
        "missing_commit_sha",
        "commit_sha_not_found",
        "outside_allowed_files_present",
        "publication_state_already_mutated",
    }:
        return "review_coder_worktree_commit"
    if failure_class in {
        "missing_publication_approval",
        "publication_not_approved",
        "publication_not_pending",
        "source_hash_mismatch",
    }:
        return "review_and_request_publication"
    return "inspect_publication_gate_failure"


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _git_output(args: list[str], *, cwd: Path) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise CoderPublicationError("commit_sha_not_found")
    return result.stdout.strip()


def _bool(value: bool) -> str:
    return "true" if value else "false"


def _render_publication_request_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Publication Request",
            "",
            f"- publication_request_id: {payload['publication_request_id']}",
            f"- coder_worktree_run_id: {payload['coder_worktree_run_id']}",
            f"- status: {payload['status']}",
            f"- commit: {payload['commit_sha']}",
            f"- branch: {payload['branch_name']}",
            f"- remote: {payload['remote']}",
            f"- target_branch: {payload['target_branch']}",
            f"- committed_files: {','.join(payload['committed_files']) or 'none'}",
            "",
            "## Non-Claims",
            "",
            "- Publication request did not push.",
            "- Publication request did not create a PR.",
            "- Publication request did not deploy, call providers, or use the network.",
            "",
        ]
    )


def _render_publication_decision_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Publication Decision",
            "",
            f"- publication_request_id: {payload['publication_request_id']}",
            f"- status: {payload['status']}",
            f"- decided_by: {payload['decided_by']}",
            f"- decided_at: {payload['decided_at']}",
            "",
            "## Non-Claims",
            "",
            "- Publication approval did not push.",
            "- Publication approval did not create a PR.",
            "- Publication approval did not deploy, call providers, or use the network.",
            "",
        ]
    )


def _render_publication_handoff_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Publication Handoff",
            "",
            f"- project_id: {payload['project_id']}",
            f"- coder_worktree_run_id: {payload['coder_worktree_run_id']}",
            f"- worktree_path: {payload['worktree_path']}",
            f"- branch_name: {payload['branch_name']}",
            f"- commit_sha: {payload['commit_sha']}",
            f"- parent_commit_sha: {payload['parent_commit_sha']}",
            f"- remote: {payload['remote']}",
            f"- target_branch: {payload['target_branch']}",
            f"- committed_files: {','.join(payload['committed_files']) or 'none'}",
            f"- verification_status: {payload['verification_status']}",
            f"- verification_exit_code: {payload['verification_exit_code']}",
            f"- bounded_file_validation_status: {payload['bounded_file_validation']['status']}",
            f"- diff_path: {payload['diff_path']}",
            f"- suggested_push_command: {payload['suggested_push_command']}",
            f"- suggested_draft_pr_command: {payload['suggested_draft_pr_command']}",
            f"- handoff_body_path: {payload['handoff_body_path']}",
            "",
            "## Non-Claims",
            "",
            "- Publication handoff did not push.",
            "- Publication handoff did not create a PR.",
            "- Publication handoff did not deploy, call providers, or use the network.",
            "- Suggested commands require separate manual operator execution.",
            "",
        ]
    )


def _render_publication_pr_body(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {payload['commit_sha']}",
            "",
            "## Local Evidence",
            "",
            f"- project_id: {payload['project_id']}",
            f"- coder_worktree_run_id: {payload['coder_worktree_run_id']}",
            f"- worktree: {payload['worktree_path']}",
            f"- branch: {payload['branch_name']}",
            f"- commit: {payload['commit_sha']}",
            f"- parent_commit: {payload['parent_commit_sha']}",
            f"- diff: {payload['diff_path']}",
            f"- committed_files: {','.join(payload['committed_files']) or 'none'}",
            "",
            "## Operator Checklist",
            "",
            "- Review local evidence before pushing.",
            "- Run the suggested push command only after explicit operator intent.",
            "- Create a draft PR only after the push is complete.",
            "",
            "## Non-Claims",
            "",
            "- This handoff did not push.",
            "- This handoff did not create a PR.",
            "- This handoff did not deploy, call providers, or use the network.",
            "",
        ]
    )
