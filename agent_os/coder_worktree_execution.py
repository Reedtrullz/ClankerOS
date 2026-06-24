from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.coder_worktree_plan import CODER_WORKTREE_PLAN_KIND
from agent_os.ids import new_id
from agent_os.storage import Effect, Storage, utc_now


APPROVAL_REQUEST_KIND = "coder_worktree_execution_approval_request"
APPROVAL_DECISION_KIND = "coder_worktree_execution_approval_decision"
RUN_KIND = "approved_coder_worktree_run"
COMMIT_APPROVAL_REQUEST_KIND = "coder_worktree_commit_approval_request"
COMMIT_APPROVAL_DECISION_KIND = "coder_worktree_commit_approval_decision"
COMMIT_KIND = "coder_worktree_commit"
CODER_COMMIT_REQUEST_KIND = "coder_worktree_commit_request"
CODER_LOCAL_COMMIT_KIND = "coder_worktree_local_commit"


class CoderWorktreeApprovalError(ValueError):
    pass


class CoderWorktreeRunError(ValueError):
    pass


class CoderWorktreeCommitError(ValueError):
    pass


@dataclass(frozen=True)
class CoderWorktreeApprovalRecord:
    id: str
    delegation_id: str
    source_run_id: str
    project_id: str
    status: str
    source_plan_path: str
    source_plan_sha256: str
    source_coder_prep_md_sha256: str
    request_artifact_path: str
    decision_artifact_path: str | None
    requested_by: str
    request_note: str
    decided_by: str | None
    decision_note: str | None
    requested_at: str
    decided_at: str | None


@dataclass(frozen=True)
class CoderWorktreeRunRecord:
    id: str
    delegation_id: str
    source_run_id: str
    project_id: str
    approval_id: str
    source_plan_path: str
    source_plan_sha256: str
    status: str
    failure_class: str | None
    worktree_path: str
    branch_name: str
    command: str
    command_exit_code: int | None
    verification_command: str | None
    verification_exit_code: int | None
    changed_files: list[str]
    outside_allowed_files: list[str]
    evidence_path: str
    started_at: str
    completed_at: str


@dataclass(frozen=True)
class CoderWorktreeCommitApprovalRecord:
    id: str
    run_id: str
    delegation_id: str
    source_run_id: str
    project_id: str
    status: str
    failure_class: str | None
    source_run_evidence_path: str
    source_coder_worktree_run_sha256: str
    source_diff_sha256: str
    review_path: str
    worktree_path: str
    branch_name: str
    pre_commit_head: str
    changed_files: list[str]
    request_artifact_path: str
    decision_artifact_path: str | None
    commit_artifact_path: str
    commit_message: str
    allow_unverified: bool
    effect_id: str | None
    requested_by: str
    request_note: str
    decided_by: str | None
    decision_note: str | None
    committed_by: str | None
    commit_sha: str | None
    requested_at: str
    decided_at: str | None
    committed_at: str | None


@dataclass(frozen=True)
class CoderWorktreeApprovalResult:
    approval: CoderWorktreeApprovalRecord
    already_recorded: bool = False


@dataclass(frozen=True)
class CoderWorktreeDecisionResult:
    approval: CoderWorktreeApprovalRecord
    already_approved: bool = False


@dataclass(frozen=True)
class CoderWorktreeRunResult:
    run: CoderWorktreeRunRecord
    already_recorded: bool = False


@dataclass(frozen=True)
class CoderWorktreeCommitApprovalResult:
    approval: CoderWorktreeCommitApprovalRecord
    already_recorded: bool = False


@dataclass(frozen=True)
class CoderWorktreeCommitDecisionResult:
    approval: CoderWorktreeCommitApprovalRecord
    already_approved: bool = False


@dataclass(frozen=True)
class CoderWorktreeCommitResult:
    approval: CoderWorktreeCommitApprovalRecord
    status: str
    commit_sha: str | None
    evidence_path: str
    parent_commit_sha: str | None = None
    effect_id: str | None = None
    alias_evidence_path: str | None = None


def request_coder_worktree_approval(
    root: Path,
    storage: Storage,
    delegation_id: str,
    *,
    requested_by: str,
    note: str,
    force_new: bool = False,
) -> CoderWorktreeApprovalResult:
    root = root.resolve()
    _ensure_tables(storage)
    plan_path, plan_payload, plan_sha = _load_latest_plan(root, storage, delegation_id)
    project_id, source_run_id, allowed_files, prep_sha = _validate_plan(
        root,
        storage,
        plan_path,
        plan_payload,
    )

    existing = None if force_new else _latest_approval_for_plan(storage, delegation_id, plan_sha)
    if existing is not None:
        return CoderWorktreeApprovalResult(approval=existing, already_recorded=True)

    approval_id = new_id("coder_worktree_approval")
    now = utc_now()
    request_artifact = plan_path.parent / "coder_worktree_approval_request.json"
    decision_artifact = plan_path.parent / "coder_worktree_approval_decision.json"
    proposed_worktree = _dict_value(plan_payload.get("proposed_worktree"))
    payload = {
        "kind": APPROVAL_REQUEST_KIND,
        "schema_version": 1,
        "approval_id": approval_id,
        "delegation_id": delegation_id,
        "project_id": project_id,
        "source_run_id": source_run_id,
        "source_coder_worktree_plan": str(plan_path.relative_to(root)),
        "source_plan_sha256": plan_sha,
        "source_coder_prep_md_sha256": prep_sha,
        "allowed_files": allowed_files,
        "proposed_worktree": {
            "path_suggestion": proposed_worktree.get("path_suggestion", "none"),
            "branch_name_suggestion": proposed_worktree.get("branch_name_suggestion", "none"),
            "base_ref": proposed_worktree.get("base_ref", "operator_selected_current_head"),
        },
        "approval_required_before": [
            "create_worktree",
            "run_command",
            "edit_source",
            "commit",
            "push",
            "deploy",
        ],
        "requested_by": requested_by,
        "note": note,
        "status": "pending_operator_approval",
        "requested_at": now,
        "non_claims": [
            "Coder worktree approval does not create a worktree.",
            "Coder worktree approval does not run commands or edit source files.",
            "Coder worktree approval does not commit, push, deploy, call providers, or use the network.",
        ],
    }
    _write_json(request_artifact, payload)
    _write_text(request_artifact.with_suffix(".md"), _render_approval_request_markdown(payload))

    approval = _insert_approval(
        storage,
        approval_id=approval_id,
        delegation_id=delegation_id,
        source_run_id=source_run_id,
        project_id=project_id,
        source_plan_path=str(plan_path.relative_to(root)),
        source_plan_sha256=plan_sha,
        source_coder_prep_md_sha256=prep_sha,
        request_artifact_path=str(request_artifact.relative_to(root)),
        decision_artifact_path=str(decision_artifact.relative_to(root)),
        requested_by=requested_by,
        request_note=note,
        requested_at=now,
    )
    return CoderWorktreeApprovalResult(approval=approval)


def approve_coder_worktree(
    root: Path,
    storage: Storage,
    approval_id: str,
    *,
    decided_by: str,
    note: str,
) -> CoderWorktreeDecisionResult:
    root = root.resolve()
    _ensure_tables(storage)
    approval = get_coder_worktree_approval(storage, approval_id)
    if approval is None:
        raise CoderWorktreeApprovalError(f"approval not found: {approval_id}")
    already_approved = approval.status == "approved"
    if already_approved:
        return CoderWorktreeDecisionResult(approval=approval, already_approved=True)
    if approval.status != "pending_operator_approval":
        raise CoderWorktreeApprovalError(f"approval is not pending: {approval.status}")

    decided_at = utc_now()
    decision_path = root / (approval.decision_artifact_path or "")
    payload = {
        "kind": APPROVAL_DECISION_KIND,
        "schema_version": 1,
        "approval_id": approval.id,
        "delegation_id": approval.delegation_id,
        "project_id": approval.project_id,
        "source_coder_worktree_plan": approval.source_plan_path,
        "source_plan_sha256": approval.source_plan_sha256,
        "status": "approved",
        "decided_by": decided_by,
        "note": note,
        "decided_at": decided_at,
        "worktrees_created": 0,
        "commands_run": 0,
        "commit_created": False,
        "push_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Approving a coder worktree request does not create a worktree.",
            "Approving a coder worktree request does not run commands or edit source files.",
            "Approving a coder worktree request does not commit, push, deploy, call providers, or use the network.",
        ],
    }
    _write_json(decision_path, payload)
    _write_text(decision_path.with_suffix(".md"), _render_approval_decision_markdown(payload))
    updated = _mark_approval_approved(
        storage,
        approval.id,
        decided_by=decided_by,
        decision_note=note,
        decided_at=decided_at,
    )
    return CoderWorktreeDecisionResult(approval=updated)


def run_approved_coder_worktree(
    root: Path,
    storage: Storage,
    delegation_id: str,
    *,
    command: str,
    verify: bool,
    verify_command: str | None = None,
    rerun: bool = False,
) -> CoderWorktreeRunResult:
    root = root.resolve()
    _ensure_tables(storage)
    try:
        plan_path, plan_payload, plan_sha = _load_latest_plan(root, storage, delegation_id)
        project_id, source_run_id, allowed_files, _prep_sha = _validate_plan(
            root,
            storage,
            plan_path,
            plan_payload,
        )
    except CoderWorktreeApprovalError as error:
        _record_coder_worktree_incident(
            storage,
            project_id=_project_id_for_delegation(storage, delegation_id),
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="missing_or_invalid_plan",
            summary=str(error),
            evidence={"delegation_id": delegation_id},
            evidence_path=None,
        )
        raise CoderWorktreeRunError(str(error)) from error
    project = storage.get_registered_project(project_id)
    if project is None:
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="unregistered_project",
            summary=f"Project is not registered: {project_id}",
            evidence={"delegation_id": delegation_id, "source_plan": str(plan_path.relative_to(root))},
            evidence_path=None,
        )
        raise CoderWorktreeRunError(f"project is not registered: {project_id}")
    project_root = Path(project.root_path).resolve()
    if not project_root.exists():
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="project_root_missing",
            summary=f"Project root is missing: {project_root}",
            evidence={"project_root": str(project_root)},
            evidence_path=None,
        )
        raise CoderWorktreeRunError(f"project root is missing: {project_root}")

    try:
        _validate_source_chain(root, plan_path, plan_payload)
    except CoderWorktreeRunError as error:
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="unreadable_source_chain",
            summary=str(error),
            evidence={"source_plan": str(plan_path.relative_to(root))},
            evidence_path=None,
        )
        raise
    try:
        _validate_safe_command(command)
        if verify and verify_command:
            _validate_safe_command(verify_command)
    except CoderWorktreeRunError as error:
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="unsafe_command",
            summary=str(error),
            evidence={"command": command, "verify_command": verify_command},
            evidence_path=None,
        )
        raise

    approval = _latest_approval_for_plan(storage, delegation_id, plan_sha)
    if approval is None:
        approval = _latest_approval_for_delegation(storage, delegation_id)
    if approval is None:
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="missing_approval",
            summary="No coder worktree approval exists for the current plan hash.",
            evidence={"source_plan_sha256": plan_sha},
            evidence_path=None,
        )
        raise CoderWorktreeRunError("approval is missing")
    if approval.status != "approved":
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="approval_not_approved",
            summary=f"Coder worktree approval is not approved: {approval.id}",
            evidence={"approval_id": approval.id, "approval_status": approval.status},
            evidence_path=None,
        )
        raise CoderWorktreeRunError("approval is not approved")
    if approval.source_plan_sha256 != plan_sha:
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id="run_not_started",
            delegation_id=delegation_id,
            failure_class="source_hash_mismatch",
            summary="Approval source hash does not match current plan.",
            evidence={
                "approval_id": approval.id,
                "approval_source_plan_sha256": approval.source_plan_sha256,
                "current_source_plan_sha256": plan_sha,
            },
            evidence_path=None,
        )
        raise CoderWorktreeRunError(
            f"approval source hash does not match current plan: {approval.id}"
        )

    existing = (
        None
        if rerun
        else _latest_completed_run_for_approval(storage, approval.id, plan_sha)
    )
    if existing is not None:
        return CoderWorktreeRunResult(run=existing, already_recorded=True)

    run_id = new_id("run")
    started_at = utc_now()
    suggested = _dict_value(plan_payload.get("proposed_worktree"))
    branch_name = _branch_name(str(suggested.get("branch_name_suggestion") or ""), run_id)
    worktree_path = (root / ".agent" / "worktrees" / project_id / run_id).resolve()
    evidence_dir = (
        root
        / ".clanker"
        / "delegations"
        / delegation_id
        / "runs"
        / run_id
        / "coder_worktree"
    )
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    base_commit = _git_output(["git", "rev-parse", "HEAD"], cwd=project_root).strip()
    create_result = subprocess.run(
        ["git", "worktree", "add", "-b", branch_name, str(worktree_path), base_commit],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if create_result.returncode != 0:
        _write_text(evidence_dir / "stderr.txt", create_result.stderr)
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id=run_id,
            delegation_id=delegation_id,
            failure_class="worktree_creation_failed",
            summary="Coder worktree creation failed.",
            evidence={"stderr": create_result.stderr, "branch_name": branch_name},
            evidence_path=str(evidence_dir.relative_to(root)),
        )
        raise CoderWorktreeRunError("worktree creation failed")

    _write_text(evidence_dir / "command.txt", command + "\n")
    command_env = {"PYTHONDONTWRITEBYTECODE": "1"}
    command_result = subprocess.run(
        command,
        cwd=worktree_path,
        capture_output=True,
        text=True,
        shell=True,
        env={**os.environ, **command_env},
    )
    _write_text(evidence_dir / "stdout.txt", command_result.stdout)
    _write_text(evidence_dir / "stderr.txt", command_result.stderr)

    resolved_verify_command = None
    verification_result = None
    if verify:
        resolved_verify_command = verify_command or project.default_test_command
        _validate_safe_command(resolved_verify_command)
        verification_result = subprocess.run(
            resolved_verify_command,
            cwd=worktree_path,
            capture_output=True,
            text=True,
            shell=True,
            env={**os.environ, **command_env},
        )
    _write_text(evidence_dir / "verification_command.txt", (resolved_verify_command or "") + "\n")
    _write_text(
        evidence_dir / "verification_stdout.txt",
        verification_result.stdout if verification_result else "",
    )
    _write_text(
        evidence_dir / "verification_stderr.txt",
        verification_result.stderr if verification_result else "",
    )

    subprocess.run(
        ["git", "add", "-N", "."],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )
    git_status = _git_output(["git", "status", "--short"], cwd=worktree_path)
    diff_patch = _git_output(["git", "diff", "--no-ext-diff", "--binary"], cwd=worktree_path)
    tracked_changed = _git_lines(["git", "diff", "--name-only"], cwd=worktree_path)
    untracked_files = _git_lines(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=worktree_path,
    )
    changed_files = sorted(set(tracked_changed + untracked_files))
    outside_files = [path for path in changed_files if path not in set(allowed_files)]
    bounded_payload = {
        "valid": not outside_files,
        "allowed_files": allowed_files,
        "changed_files": changed_files,
        "outside_allowed_files": outside_files,
        "untracked_files": untracked_files,
        "policy": "changed files must be subset of allowed_files",
        "status": "passed" if not outside_files else "blocked",
    }
    if outside_files:
        bounded_payload["failure_class"] = "bounded_file_violation"
        bounded_payload["next_recommended_action"] = "operator_review"

    command_exit = command_result.returncode
    verification_exit = verification_result.returncode if verification_result else None
    status = "completed"
    failure_class = None
    if command_exit != 0:
        status = "failed"
        failure_class = "command_failed"
    elif verification_exit not in (None, 0):
        status = "failed"
        failure_class = "verification_failed"
    elif outside_files:
        status = "blocked"
        failure_class = "bounded_file_violation"

    _write_text(evidence_dir / "git_status.txt", git_status)
    _write_text(evidence_dir / "diff.patch", diff_patch)
    _write_json(
        evidence_dir / "changed_files.json",
        {
            "changed_files": changed_files,
            "untracked_files": untracked_files,
        },
    )
    _write_json(evidence_dir / "bounded_file_validation.json", bounded_payload)
    _write_json(evidence_dir / "approval.json", _approval_to_payload(approval))
    _write_json(evidence_dir / "source_plan.json", plan_payload)

    completed_at = utc_now()
    run_payload = {
        "kind": RUN_KIND,
        "schema_version": 1,
        "delegation_id": delegation_id,
        "run_id": run_id,
        "source_delegation_run_id": source_run_id,
        "project_id": project_id,
        "worktree_path": str(worktree_path),
        "branch_name": branch_name,
        "approval_id": approval.id,
        "approval_status": approval.status,
        "source_plan_sha256": plan_sha,
        "allowed_files": allowed_files,
        "changed_files": changed_files,
        "outside_allowed_files": outside_files,
        "changed_files_within_allowed_files": not outside_files,
        "command": command,
        "command_exit_code": command_exit,
        "verification_command": resolved_verify_command,
        "verification_exit_code": verification_exit,
        "status": status,
        "failure_class": failure_class,
        "commit_created": False,
        "push_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "next_recommended_action": (
            "review_coder_worktree_run"
            if status == "completed"
            else "operator_review"
        ),
        "started_at": started_at,
        "completed_at": completed_at,
        "non_claims": [
            "Coder worktree run does not commit changes.",
            "Coder worktree run does not push, deploy, call providers, or intentionally use the network.",
            "Changed files are left in the isolated worktree for operator review.",
        ],
    }
    _write_json(evidence_dir / "run.json", run_payload)
    _write_text(evidence_dir / "summary.md", _render_run_summary(run_payload, evidence_dir, root))

    record = _insert_run(
        storage,
        run_id=run_id,
        delegation_id=delegation_id,
        source_run_id=source_run_id,
        project_id=project_id,
        approval_id=approval.id,
        source_plan_path=str(plan_path.relative_to(root)),
        source_plan_sha256=plan_sha,
        status=status,
        failure_class=failure_class,
        worktree_path=str(worktree_path),
        branch_name=branch_name,
        command=command,
        command_exit_code=command_exit,
        verification_command=resolved_verify_command,
        verification_exit_code=verification_exit,
        changed_files=changed_files,
        outside_allowed_files=outside_files,
        evidence_path=str(evidence_dir.relative_to(root)),
        started_at=started_at,
        completed_at=completed_at,
    )
    if status in {"failed", "blocked"}:
        _record_coder_worktree_incident(
            storage,
            project_id=project_id,
            run_id=run_id,
            delegation_id=delegation_id,
            failure_class=failure_class or "coder_worktree_run_failed",
            summary=f"Coder worktree run {status}: {failure_class or 'unknown'}",
            evidence={"run_id": run_id, "status": status, "failure_class": failure_class},
            evidence_path=str(evidence_dir.relative_to(root)),
        )
    return CoderWorktreeRunResult(run=record)


def request_coder_worktree_commit_approval(
    root: Path,
    storage: Storage,
    run_id: str,
    *,
    requested_by: str,
    commit_message: str | None = None,
    note: str,
    allow_unverified: bool = False,
    force_new: bool = False,
) -> CoderWorktreeCommitApprovalResult:
    root = root.resolve()
    _ensure_tables(storage)
    run = get_coder_worktree_run(storage, run_id)
    if run is None:
        raise CoderWorktreeCommitError(f"coder worktree run not found: {run_id}")
    evidence = _load_run_evidence(root, run)
    _validate_run_commit_eligible(
        run,
        run_payload=evidence["run_payload"],
        allow_unverified=allow_unverified,
    )
    resolved_commit_message = (commit_message or f"Promote coder worktree run {run.id}").strip()
    if not resolved_commit_message:
        raise CoderWorktreeCommitError("commit message is required")
    review_path = _review_path_for_run(root, run)
    if not _review_mentions_run(review_path, run.id):
        raise CoderWorktreeCommitError(
            f"coder worktree run has not been reviewed: {review_path.relative_to(root)}"
        )
    worktree_path = Path(run.worktree_path)
    if not worktree_path.exists():
        raise CoderWorktreeCommitError(f"worktree does not exist: {worktree_path}")
    snapshot = _current_worktree_snapshot(worktree_path)
    _raise_if_snapshot_stale(
        snapshot=snapshot,
        expected_diff=evidence["diff_text"],
        expected_changed_files=run.changed_files,
        expected_head=None,
        detail_path=evidence["diff_path"],
    )

    source_run_sha = evidence["run_sha256"]
    source_diff_sha = evidence["diff_sha256"]
    existing = (
        None
        if force_new
        else _latest_commit_approval_for_run(
            storage,
            run.id,
            source_run_sha,
            source_diff_sha,
        )
    )
    if existing is not None:
        return CoderWorktreeCommitApprovalResult(
            approval=existing,
            already_recorded=True,
        )

    approval_id = new_id("coder_worktree_commit_approval")
    now = utc_now()
    request_artifact = evidence["evidence_dir"] / "coder_worktree_commit_approval_request.json"
    decision_artifact = evidence["evidence_dir"] / "coder_worktree_commit_approval_decision.json"
    commit_artifact = evidence["evidence_dir"] / "coder_worktree_commit.json"
    coder_commit_dir = evidence["evidence_dir"] / "coder_commit"
    payload = {
        "kind": COMMIT_APPROVAL_REQUEST_KIND,
        "schema_version": 1,
        "commit_approval_id": approval_id,
        "run_id": run.id,
        "delegation_id": run.delegation_id,
        "source_delegation_run_id": run.source_run_id,
        "project_id": run.project_id,
        "source_coder_worktree_run": run.evidence_path,
        "source_coder_worktree_run_sha256": source_run_sha,
        "source_diff_sha256": source_diff_sha,
        "review_path": str(review_path.relative_to(root)),
        "worktree_path": run.worktree_path,
        "branch_name": run.branch_name,
        "pre_commit_head": snapshot["head"],
        "changed_files": run.changed_files,
        "verification_command": run.verification_command,
        "commit_message": resolved_commit_message,
        "allow_unverified": allow_unverified,
        "status": "pending_operator_approval",
        "approval_required_before": [
            "create_local_commit",
            "push",
            "deploy",
        ],
        "requested_by": requested_by,
        "note": note,
        "requested_at": now,
        "commit_created": False,
        "push_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Coder worktree commit approval does not create a git commit.",
            "Coder worktree commit approval does not push, deploy, call providers, or use the network.",
            "Commit promotion must re-check evidence and rerun verification after operator approval.",
        ],
    }
    _write_json(request_artifact, payload)
    _write_text(
        request_artifact.with_suffix(".md"),
        _render_commit_approval_request_markdown(payload),
    )
    alias_payload = _coder_commit_request_payload(
        payload,
        evidence=evidence,
        run_payload=evidence["run_payload"],
    )
    _write_json(coder_commit_dir / "coder_commit_request.json", alias_payload)
    _write_text(
        coder_commit_dir / "coder_commit_request.md",
        _render_coder_commit_request_markdown(alias_payload),
    )

    approval = _insert_commit_approval(
        storage,
        approval_id=approval_id,
        run_id=run.id,
        delegation_id=run.delegation_id,
        source_run_id=run.source_run_id,
        project_id=run.project_id,
        source_run_evidence_path=run.evidence_path,
        source_coder_worktree_run_sha256=source_run_sha,
        source_diff_sha256=source_diff_sha,
        review_path=str(review_path.relative_to(root)),
        worktree_path=run.worktree_path,
        branch_name=run.branch_name,
        pre_commit_head=snapshot["head"],
        changed_files=run.changed_files,
        request_artifact_path=str(request_artifact.relative_to(root)),
        decision_artifact_path=str(decision_artifact.relative_to(root)),
        commit_artifact_path=str(commit_artifact.relative_to(root)),
        commit_message=resolved_commit_message,
        allow_unverified=allow_unverified,
        requested_by=requested_by,
        request_note=note,
        requested_at=now,
    )
    return CoderWorktreeCommitApprovalResult(approval=approval)


def approve_coder_worktree_commit(
    root: Path,
    storage: Storage,
    approval_id: str,
    *,
    decided_by: str,
    note: str,
) -> CoderWorktreeCommitDecisionResult:
    root = root.resolve()
    _ensure_tables(storage)
    approval = get_coder_worktree_commit_approval(storage, approval_id)
    if approval is None:
        raise CoderWorktreeCommitError(f"commit approval not found: {approval_id}")
    if approval.status in {"approved", "committed"}:
        return CoderWorktreeCommitDecisionResult(
            approval=approval,
            already_approved=True,
        )
    if approval.status != "pending_operator_approval":
        raise CoderWorktreeCommitError(f"approval is not pending: {approval.status}")

    decided_at = utc_now()
    decision_path = root / (approval.decision_artifact_path or "")
    coder_commit_dir = _coder_commit_dir(root, approval)
    payload = {
        "kind": COMMIT_APPROVAL_DECISION_KIND,
        "schema_version": 1,
        "commit_approval_id": approval.id,
        "run_id": approval.run_id,
        "delegation_id": approval.delegation_id,
        "project_id": approval.project_id,
        "source_coder_worktree_run": approval.source_run_evidence_path,
        "source_coder_worktree_run_sha256": approval.source_coder_worktree_run_sha256,
        "source_diff_sha256": approval.source_diff_sha256,
        "status": "approved",
        "decided_by": decided_by,
        "note": note,
        "decided_at": decided_at,
        "commit_created": False,
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Approving a coder worktree commit request does not create a git commit.",
            "Approving a coder worktree commit request does not push, deploy, call providers, or use the network.",
            "Commit promotion still must re-check evidence and rerun verification.",
        ],
    }
    _write_json(decision_path, payload)
    _write_text(
        decision_path.with_suffix(".md"),
        _render_commit_approval_decision_markdown(payload),
    )
    alias_payload = {
        "kind": COMMIT_APPROVAL_DECISION_KIND,
        "schema_version": 1,
        "commit_request_id": approval.id,
        "coder_worktree_run_id": approval.run_id,
        "delegation_id": approval.delegation_id,
        "project_id": approval.project_id,
        "source_request_sha256": _sha256_path(
            coder_commit_dir / "coder_commit_request.json"
        ),
        "status": "approved",
        "decided_by": decided_by,
        "note": note,
        "decided_at": decided_at,
        "staged_files": [],
        "commit_created": False,
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Approving a commit request does not stage files.",
            "Approving a commit request does not create a commit.",
            "Approving a commit request does not push, deploy, create a PR, call providers, or use the network.",
        ],
    }
    _write_json(coder_commit_dir / "coder_commit_decision.json", alias_payload)
    _write_text(
        coder_commit_dir / "coder_commit_decision.md",
        _render_coder_commit_decision_markdown(alias_payload),
    )
    updated = _mark_commit_approval_approved(
        storage,
        approval.id,
        decided_by=decided_by,
        decision_note=note,
        decided_at=decided_at,
    )
    return CoderWorktreeCommitDecisionResult(approval=updated)


def promote_coder_worktree_commit(
    root: Path,
    storage: Storage,
    approval_id: str,
    *,
    committed_by: str,
    message: str | None = None,
) -> CoderWorktreeCommitResult:
    root = root.resolve()
    _ensure_tables(storage)
    approval = get_coder_worktree_commit_approval(storage, approval_id)
    if approval is None:
        raise CoderWorktreeCommitError(f"commit approval not found: {approval_id}")
    if approval.status == "committed":
        _ensure_recorded_commit_exists(approval)
        return CoderWorktreeCommitResult(
            approval=approval,
            status="already_committed",
            commit_sha=approval.commit_sha,
            evidence_path=approval.commit_artifact_path,
            parent_commit_sha=approval.pre_commit_head,
            effect_id=approval.effect_id,
            alias_evidence_path=str(
                (_coder_commit_dir(root, approval) / "commit.json").relative_to(root)
            ),
        )
    if approval.status != "approved":
        raise CoderWorktreeCommitError("approval is not approved")

    run = get_coder_worktree_run(storage, approval.run_id)
    if run is None:
        raise CoderWorktreeCommitError(f"coder worktree run not found: {approval.run_id}")
    evidence = _load_run_evidence(root, run)
    _validate_run_commit_eligible(
        run,
        run_payload=evidence["run_payload"],
        allow_unverified=approval.allow_unverified,
    )
    try:
        _raise_if_source_hash_changed(approval, evidence)
    except CoderWorktreeCommitError as error:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="source_hash_mismatch",
            detail=str(error),
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError(f"source_hash_mismatch: {error}") from error
    worktree_path = Path(approval.worktree_path)
    if not worktree_path.exists():
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="worktree_missing",
            detail=f"worktree does not exist: {worktree_path}",
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError(f"worktree does not exist: {worktree_path}")

    try:
        _validate_git_worktree_safe(worktree_path, approval.branch_name)
    except CoderWorktreeCommitError as error:
        failure_class = (
            "source_state_changed"
            if str(error).startswith("source_state_changed")
            else "git_state_unsafe"
        )
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class=failure_class,
            detail=str(error),
            verification_exit_code=None,
        )
        raise
    snapshot = _current_worktree_snapshot(worktree_path)
    allowed_files = set(str(path) for path in evidence["allowed_files"])
    outside_files = [path for path in snapshot["changed_files"] if path not in allowed_files]
    staged_outside = [path for path in snapshot["staged_files"] if path not in allowed_files]
    if outside_files or staged_outside:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="outside_files_present",
            detail=(
                "outside files present: "
                f"{','.join(sorted(set(outside_files + staged_outside)))}"
            ),
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError("outside_files_present")
    if snapshot["head"] != approval.pre_commit_head:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="source_state_changed",
            detail=f"worktree HEAD changed from {approval.pre_commit_head} to {snapshot['head']}",
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError("source_state_changed")
    if snapshot["branch"] != approval.branch_name:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="source_state_changed",
            detail=f"worktree branch changed from {approval.branch_name} to {snapshot['branch']}",
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError("source_state_changed")
    if snapshot["changed_files"] != sorted(approval.changed_files):
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="changed_files_mismatch",
            detail="current changed files differ from approved commit request",
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError("changed_files_mismatch")
    if snapshot["diff"] != evidence["diff_text"]:
        detail = f"stale evidence: current diff no longer matches {evidence['diff_path']}"
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="stale_evidence",
            detail=detail,
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError(detail)
    if not snapshot["changed_files"]:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="no_changes",
            detail="no changes exist in the coder worktree",
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError("no_changes")

    verification_command = run.verification_command
    if not verification_command:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="missing_verification",
            detail="coder worktree run has no verification command",
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError("coder worktree run has no verification command")
    try:
        _validate_safe_command(verification_command)
    except CoderWorktreeRunError as error:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="unsafe_verification_command",
            detail=str(error),
            verification_exit_code=None,
        )
        raise CoderWorktreeCommitError(str(error)) from error

    evidence_dir = root / approval.source_run_evidence_path
    coder_commit_dir = _coder_commit_dir(root, approval)
    pre_status = _git_output(["git", "status", "--short"], cwd=worktree_path)
    _write_text(coder_commit_dir / "pre_commit_status.txt", pre_status)
    command_env = {"PYTHONDONTWRITEBYTECODE": "1"}
    verification_result = subprocess.run(
        verification_command,
        cwd=worktree_path,
        capture_output=True,
        text=True,
        shell=True,
        env={**os.environ, **command_env},
    )
    _write_text(evidence_dir / "commit_verification_command.txt", verification_command + "\n")
    _write_text(evidence_dir / "commit_verification_stdout.txt", verification_result.stdout)
    _write_text(evidence_dir / "commit_verification_stderr.txt", verification_result.stderr)
    if verification_result.returncode != 0:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="verification_failed",
            detail=f"verification command exited {verification_result.returncode}",
            verification_exit_code=verification_result.returncode,
        )
        raise CoderWorktreeCommitError(
            f"verification failed before commit: {verification_result.returncode}"
        )

    commit_message = (message or approval.commit_message).strip()
    if not commit_message:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="empty_commit_message",
            detail="commit message is required",
            verification_exit_code=verification_result.returncode,
        )
        raise CoderWorktreeCommitError("commit message is required")

    commit_result = subprocess.run(
        ["git", "add", "--", *approval.changed_files],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )
    if commit_result.returncode != 0:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="git_stage_failed",
            detail=commit_result.stderr.strip() or commit_result.stdout.strip(),
            verification_exit_code=verification_result.returncode,
        )
        raise CoderWorktreeCommitError("git stage failed")
    parent_commit_sha = _git_output(["git", "rev-parse", "HEAD"], cwd=worktree_path).strip()
    commit_result = subprocess.run(
        [
            "git",
            "-c",
            "user.name=ClankerOS",
            "-c",
            "user.email=clankeros@example.invalid",
            "commit",
            "-m",
            commit_message,
            "-m",
            f"Coder-worktree-run: {approval.run_id}",
            "-m",
            f"Commit-approval: {approval.id}",
            "-m",
            f"Committed-by: {committed_by}",
        ],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )
    _write_text(evidence_dir / "commit_stdout.txt", commit_result.stdout)
    _write_text(evidence_dir / "commit_stderr.txt", commit_result.stderr)
    if commit_result.returncode != 0:
        _block_commit_approval(
            root,
            storage,
            approval,
            failure_class="git_commit_failed",
            detail=commit_result.stderr.strip() or commit_result.stdout.strip(),
            verification_exit_code=verification_result.returncode,
        )
        raise CoderWorktreeCommitError("git commit failed")

    commit_sha = _git_output(["git", "rev-parse", "HEAD"], cwd=worktree_path).strip()
    committed_at = utc_now()
    post_status = _git_output(["git", "status", "--short"], cwd=worktree_path)
    _write_text(evidence_dir / "post_commit_status.txt", post_status)
    _write_text(coder_commit_dir / "post_commit_status.txt", post_status)
    committed_diff = _git_output(
        ["git", "show", "--stat", "--patch", "--binary", "--format=fuller", "HEAD"],
        cwd=worktree_path,
    )
    _write_text(coder_commit_dir / "committed_diff.patch", committed_diff)
    committed_files = _git_lines(
        ["git", "show", "--name-only", "--pretty=", "HEAD"],
        cwd=worktree_path,
    )
    committed_files_payload = {
        "committed_files": committed_files,
        "outside_allowed_files": [path for path in committed_files if path not in allowed_files],
    }
    _write_json(coder_commit_dir / "committed_files.json", committed_files_payload)
    payload = {
        "kind": COMMIT_KIND,
        "schema_version": 1,
        "status": "committed",
        "commit_approval_id": approval.id,
        "run_id": approval.run_id,
        "delegation_id": approval.delegation_id,
        "source_delegation_run_id": approval.source_run_id,
        "project_id": approval.project_id,
        "commit_sha": commit_sha,
        "parent_commit_sha": parent_commit_sha,
        "base_commit": approval.pre_commit_head,
        "branch_name": approval.branch_name,
        "worktree_path": approval.worktree_path,
        "changed_files": approval.changed_files,
        "committed_files": committed_files,
        "commit_message": commit_message,
        "source_coder_worktree_run_sha256": approval.source_coder_worktree_run_sha256,
        "source_diff_sha256": approval.source_diff_sha256,
        "verification_command": verification_command,
        "verification_exit_code": verification_result.returncode,
        "committed_by": committed_by,
        "committed_at": committed_at,
        "commit_created": True,
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Commit promotion creates one local git commit in the isolated coder worktree branch.",
            "Commit promotion does not push, deploy, call providers, or use the network.",
            "Promotion does not merge the worktree branch into the original project checkout.",
        ],
    }
    _write_json(root / approval.commit_artifact_path, payload)
    alias_payload = {
        "kind": CODER_LOCAL_COMMIT_KIND,
        "schema_version": 1,
        "coder_worktree_run_id": approval.run_id,
        "delegation_id": approval.delegation_id,
        "project_id": approval.project_id,
        "worktree_path": approval.worktree_path,
        "branch_name": approval.branch_name,
        "commit_request_id": approval.id,
        "commit_approval_id": approval.id,
        "commit_sha": commit_sha,
        "parent_commit_sha": parent_commit_sha,
        "commit_message": commit_message,
        "allowed_files": sorted(allowed_files),
        "committed_files": committed_files,
        "outside_allowed_files": committed_files_payload["outside_allowed_files"],
        "bounded_file_validation": {
            "valid": not committed_files_payload["outside_allowed_files"],
            "status": "passed" if not committed_files_payload["outside_allowed_files"] else "blocked",
        },
        "verification_exit_code": verification_result.returncode,
        "committed_at": committed_at,
        "commit_created": True,
        "push_created": False,
        "pr_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "next_recommended_action": "github_handoff",
        "non_claims": [
            "Commit was created only in the isolated worktree.",
            "Commit was not pushed.",
            "No PR was created.",
            "No deploy occurred.",
            "No provider call or network action was taken by ClankerOS.",
        ],
    }
    _write_json(coder_commit_dir / "commit.json", alias_payload)
    _write_text(coder_commit_dir / "commit.md", _render_coder_local_commit_markdown(alias_payload))
    updated = _mark_commit_approval_committed(
        storage,
        approval.id,
        committed_by=committed_by,
        commit_sha=commit_sha,
        committed_at=committed_at,
    )
    effect = _record_coder_commit_effect(
        root,
        storage,
        approval=updated,
        commit_payload=alias_payload,
        commit_artifact_path=coder_commit_dir / "commit.json",
        committed_diff_path=coder_commit_dir / "committed_diff.patch",
        verification_command=verification_command,
        verification_exit_code=verification_result.returncode,
    )
    updated = _mark_commit_approval_effect(storage, updated.id, effect_id=effect.id)
    return CoderWorktreeCommitResult(
        approval=updated,
        status="committed",
        commit_sha=commit_sha,
        evidence_path=approval.commit_artifact_path,
        parent_commit_sha=parent_commit_sha,
        effect_id=effect.id,
        alias_evidence_path=str((coder_commit_dir / "commit.json").relative_to(root)),
    )


def request_coder_commit(
    root: Path,
    storage: Storage,
    run_id: str,
    *,
    requested_by: str,
    commit_message: str,
    note: str,
    allow_unverified: bool = False,
    force_new: bool = False,
) -> CoderWorktreeCommitApprovalResult:
    return request_coder_worktree_commit_approval(
        root,
        storage,
        run_id,
        requested_by=requested_by,
        commit_message=commit_message,
        note=note,
        allow_unverified=allow_unverified,
        force_new=force_new,
    )


def approve_coder_commit(
    root: Path,
    storage: Storage,
    approval_id: str,
    *,
    decided_by: str,
    note: str,
) -> CoderWorktreeCommitDecisionResult:
    return approve_coder_worktree_commit(
        root,
        storage,
        approval_id,
        decided_by=decided_by,
        note=note,
    )


def commit_coder_worktree(
    root: Path,
    storage: Storage,
    run_id: str,
    *,
    message: str,
    committed_by: str,
    use_approved_message: bool = False,
) -> CoderWorktreeCommitResult:
    _ensure_tables(storage)
    approval = _latest_commit_request_for_run(storage, run_id)
    if approval is None:
        raise CoderWorktreeCommitError("approved commit request is missing")
    if approval.status == "pending_operator_approval":
        raise CoderWorktreeCommitError("approved commit request is missing")
    if approval.status == "blocked":
        raise CoderWorktreeCommitError(f"commit request is blocked: {approval.failure_class or 'unknown'}")
    requested_message = message.strip()
    if not requested_message:
        raise CoderWorktreeCommitError("commit message is required")
    if not use_approved_message and requested_message != approval.commit_message:
        raise CoderWorktreeCommitError("commit message does not match approved request")
    selected_message = approval.commit_message if use_approved_message else requested_message
    return promote_coder_worktree_commit(
        root,
        storage,
        approval.id,
        committed_by=committed_by,
        message=selected_message,
    )


def render_coder_worktree_approval_cli_lines(
    root: Path,
    result: CoderWorktreeApprovalResult,
) -> list[str]:
    root = root.resolve()
    approval = result.approval
    prefix = "already_recorded " if result.already_recorded else ""
    return [
        f"coder_worktree_approval: {prefix}{approval.id}",
        f"approval_id: {approval.id}",
        f"delegation_id: {approval.delegation_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"source_plan_sha256: {approval.source_plan_sha256}",
        f"artifact: {(root / approval.request_artifact_path).relative_to(root)}",
        "worktrees_created: 0",
        "commands_run: 0",
        "source_edits: 0",
        "commit_created: false",
        "push_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_worktree_decision_cli_lines(
    root: Path,
    result: CoderWorktreeDecisionResult,
) -> list[str]:
    root = root.resolve()
    approval = result.approval
    prefix = "already_approved " if result.already_approved else ""
    return [
        f"approved_coder_worktree: {prefix}{approval.id}",
        f"approval_id: {approval.id}",
        f"delegation_id: {approval.delegation_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"artifact: {(root / (approval.decision_artifact_path or '')).relative_to(root)}",
        "worktrees_created: 0",
        "commands_run: 0",
        "source_edits: 0",
        "commit_created: false",
        "push_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_worktree_run_cli_lines(
    root: Path,
    result: CoderWorktreeRunResult,
) -> list[str]:
    run = result.run
    status_line = (
        f"coder_worktree_run: already_recorded {run.id}"
        if result.already_recorded
        else f"coder_worktree_run: {run.status}"
    )
    lines = [
        status_line,
        f"run_id: {run.id}",
        f"delegation_id: {run.delegation_id}",
        f"source_delegation_run_id: {run.source_run_id}",
        f"project_id: {run.project_id}",
        f"approval_id: {run.approval_id}",
        f"status: {run.status}",
        f"failure_class: {run.failure_class or 'none'}",
        f"worktree_path: {run.worktree_path}",
        f"branch_name: {run.branch_name}",
        f"command_exit_code: {run.command_exit_code if run.command_exit_code is not None else 'none'}",
        "verification_exit_code: "
        f"{run.verification_exit_code if run.verification_exit_code is not None else 'none'}",
        f"changed_files: {','.join(run.changed_files) or 'none'}",
        f"outside_allowed_files: {','.join(run.outside_allowed_files) or 'none'}",
        f"changed_files_within_allowed_files: {_bool(not run.outside_allowed_files)}",
        f"evidence: {run.evidence_path}",
        "commit_created: false",
        "push_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]
    return lines


def render_coder_worktree_commit_approval_cli_lines(
    root: Path,
    result: CoderWorktreeCommitApprovalResult,
) -> list[str]:
    root = root.resolve()
    approval = result.approval
    prefix = "already_recorded " if result.already_recorded else ""
    return [
        f"coder_worktree_commit_approval: {prefix}{approval.id}",
        f"commit_approval_id: {approval.id}",
        f"run_id: {approval.run_id}",
        f"delegation_id: {approval.delegation_id}",
        f"source_delegation_run_id: {approval.source_run_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"failure_class: {approval.failure_class or 'none'}",
        f"source_coder_worktree_run_sha256: {approval.source_coder_worktree_run_sha256}",
        f"source_diff_sha256: {approval.source_diff_sha256}",
        f"worktree_path: {approval.worktree_path}",
        f"branch_name: {approval.branch_name}",
        f"changed_files: {','.join(approval.changed_files) or 'none'}",
        f"artifact: {(root / approval.request_artifact_path).relative_to(root)}",
        "commit_created: false",
        "push_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_worktree_commit_decision_cli_lines(
    root: Path,
    result: CoderWorktreeCommitDecisionResult,
) -> list[str]:
    root = root.resolve()
    approval = result.approval
    prefix = "already_approved " if result.already_approved else ""
    return [
        f"approved_coder_worktree_commit: {prefix}{approval.id}",
        f"commit_approval_id: {approval.id}",
        f"run_id: {approval.run_id}",
        f"delegation_id: {approval.delegation_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"artifact: {(root / (approval.decision_artifact_path or '')).relative_to(root)}",
        "commit_created: false",
        "push_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_worktree_commit_cli_lines(
    root: Path,
    result: CoderWorktreeCommitResult,
) -> list[str]:
    approval = result.approval
    return [
        f"coder_worktree_commit: {result.status}",
        f"commit_approval_id: {approval.id}",
        f"run_id: {approval.run_id}",
        f"delegation_id: {approval.delegation_id}",
        f"source_delegation_run_id: {approval.source_run_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"commit: {result.commit_sha or 'none'}",
        f"worktree_path: {approval.worktree_path}",
        f"branch_name: {approval.branch_name}",
        f"changed_files: {','.join(approval.changed_files) or 'none'}",
        f"evidence: {result.evidence_path}",
        "commit_created: true",
        "push_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_commit_request_cli_lines(
    root: Path,
    result: CoderWorktreeCommitApprovalResult,
) -> list[str]:
    approval = result.approval
    prefix = "already_recorded " if result.already_recorded else ""
    artifact = _coder_commit_dir(root.resolve(), approval) / "coder_commit_request.json"
    return [
        f"coder_commit_request: {prefix}{approval.id}",
        f"commit_request_id: {approval.id}",
        f"commit_approval_id: {approval.id}",
        f"coder_worktree_run_id: {approval.run_id}",
        f"delegation_id: {approval.delegation_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"failure_class: {approval.failure_class or 'none'}",
        f"commit_message: {approval.commit_message}",
        f"worktree_path: {approval.worktree_path}",
        f"branch_name: {approval.branch_name}",
        f"changed_files: {','.join(approval.changed_files) or 'none'}",
        f"artifact: {artifact.relative_to(root.resolve())}",
        "staged_files: none",
        "commit_created: false",
        "push_created: false",
        "pr_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_commit_decision_cli_lines(
    root: Path,
    result: CoderWorktreeCommitDecisionResult,
) -> list[str]:
    approval = result.approval
    prefix = "already_approved " if result.already_approved else ""
    artifact = _coder_commit_dir(root.resolve(), approval) / "coder_commit_decision.json"
    return [
        f"approved_coder_commit: {prefix}{approval.id}",
        f"commit_request_id: {approval.id}",
        f"commit_approval_id: {approval.id}",
        f"coder_worktree_run_id: {approval.run_id}",
        f"delegation_id: {approval.delegation_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"artifact: {artifact.relative_to(root.resolve())}",
        "staged_files: none",
        "commit_created: false",
        "push_created: false",
        "pr_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_commit_coder_worktree_cli_lines(
    root: Path,
    result: CoderWorktreeCommitResult,
) -> list[str]:
    approval = result.approval
    evidence_path = result.alias_evidence_path or str(
        (_coder_commit_dir(root.resolve(), approval) / "commit.json").relative_to(root.resolve())
    )
    return [
        f"commit_coder_worktree: {result.status}",
        f"commit_request_id: {approval.id}",
        f"commit_approval_id: {approval.id}",
        f"coder_worktree_run_id: {approval.run_id}",
        f"delegation_id: {approval.delegation_id}",
        f"project_id: {approval.project_id}",
        f"status: {approval.status}",
        f"commit: {result.commit_sha or 'none'}",
        f"parent_commit: {result.parent_commit_sha or approval.pre_commit_head}",
        f"effect_id: {result.effect_id or approval.effect_id or 'none'}",
        f"worktree_path: {approval.worktree_path}",
        f"branch_name: {approval.branch_name}",
        f"committed_files: {','.join(approval.changed_files) or 'none'}",
        f"evidence: {evidence_path}",
        "commit_created: true",
        "push_created: false",
        "pr_created: false",
        "deploy_created: false",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
        "next_recommended_action: github_handoff",
    ]


def render_coder_worktree_approval_dashboard_lines(root: Path) -> list[str]:
    return [
        (
            f"- {approval.id}: delegation={approval.delegation_id} "
            f"project={approval.project_id} status={approval.status} "
            f"request={approval.request_artifact_path} "
            f"source_plan={approval.source_plan_path}"
        )
        for approval in list_coder_worktree_approvals(root, limit=10)
    ]


def render_coder_worktree_run_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for run in list_coder_worktree_runs(root, limit=10):
        lines.append(
            f"- {run.id}: delegation={run.delegation_id} project={run.project_id} "
            f"status={run.status} approval={run.approval_id} "
            f"worktree={run.worktree_path} branch={run.branch_name} "
            f"changed_files={','.join(run.changed_files) or 'none'} "
            f"outside_allowed_files={','.join(run.outside_allowed_files) or 'none'} "
            f"command_exit={run.command_exit_code if run.command_exit_code is not None else 'none'} "
            "verification_exit="
            f"{run.verification_exit_code if run.verification_exit_code is not None else 'none'} "
            f"diff={run.evidence_path}/diff.patch "
            "next_action=review_coder_worktree_run"
        )
    return lines


def render_coder_worktree_commit_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for approval in list_coder_worktree_commit_approvals(root, limit=10):
        request = _coder_commit_dir(root.resolve(), approval) / "coder_commit_request.json"
        local_commit = _coder_commit_dir(root.resolve(), approval) / "commit.json"
        lines.append(
            f"- {approval.id}: delegation={approval.delegation_id} project={approval.project_id} "
            f"run={approval.run_id} status={approval.status} "
            f"failure_class={approval.failure_class or 'none'} "
            f"commit={approval.commit_sha or 'none'} "
            f"effect={approval.effect_id or 'none'} "
            f"github_handoff_available={_bool(bool(approval.effect_id and approval.status == 'committed'))} "
            f"worktree={approval.worktree_path} branch={approval.branch_name} "
            f"message={approval.commit_message or 'none'} "
            f"changed_files={','.join(approval.changed_files) or 'none'} "
            f"request={approval.request_artifact_path} "
            f"coder_commit_request={request.relative_to(root.resolve())} "
            f"local_commit={local_commit.relative_to(root.resolve())} "
            f"evidence={approval.commit_artifact_path}"
        )
    return lines


def render_coder_commit_request_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for approval in list_coder_worktree_commit_approvals(root, limit=10):
        artifact = _coder_commit_dir(root.resolve(), approval) / "coder_commit_request.json"
        lines.append(
            f"- {approval.id}: delegation={approval.delegation_id} project={approval.project_id} "
            f"coder_worktree_run={approval.run_id} status={approval.status} "
            f"message={approval.commit_message or 'none'} "
            f"changed_files={','.join(approval.changed_files) or 'none'} "
            f"artifact={artifact.relative_to(root.resolve())} "
            "approval_required_before=stage_allowed_files,create_local_commit "
            "commit_created=false push_created=false pr_created=false"
        )
    return lines


def render_coder_local_commit_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for approval in list_coder_worktree_commit_approvals(root, status="committed", limit=10):
        artifact = _coder_commit_dir(root.resolve(), approval) / "commit.json"
        lines.append(
            f"- {approval.id}: delegation={approval.delegation_id} project={approval.project_id} "
            f"coder_worktree_run={approval.run_id} commit={approval.commit_sha or 'none'} "
            f"parent={approval.pre_commit_head} effect={approval.effect_id or 'none'} "
            f"github_handoff_available={_bool(bool(approval.effect_id))} "
            f"committed_files={','.join(approval.changed_files) or 'none'} "
            f"artifact={artifact.relative_to(root.resolve())} "
            "push_created=false pr_created=false deploy_created=false"
        )
    return lines


def render_coder_worktree_approval_review_lines(
    root: Path,
    delegation_id: str,
) -> list[str]:
    approvals = list_coder_worktree_approvals(root, delegation_id=delegation_id, limit=10)
    lines: list[str] = []
    for approval in approvals:
        lines.extend(
            [
                f"- delegation={delegation_id} approval={approval.id}",
                f"  - request: {approval.request_artifact_path}",
                f"  - status: {approval.status}",
                f"  - source_plan_sha256: {approval.source_plan_sha256}",
                "  - worktrees_created: 0",
                "  - non_claims: approval request/decision did not run commands or edit source",
            ]
        )
    return lines


def render_coder_worktree_run_review_lines(root: Path, delegation_id: str) -> list[str]:
    runs = list_coder_worktree_runs(root, delegation_id=delegation_id, limit=10)
    lines: list[str] = []
    for run in runs:
        lines.extend(
            [
                f"- delegation={delegation_id} coder_worktree_run={run.evidence_path}",
                f"  - run_id: {run.id}",
                f"  - status: {run.status}",
                f"  - approval_id: {run.approval_id}",
                f"  - worktree_path: {run.worktree_path}",
                f"  - branch_name: {run.branch_name}",
                f"  - changed_files: {','.join(run.changed_files) or 'none'}",
                f"  - outside_allowed_files: {','.join(run.outside_allowed_files) or 'none'}",
                f"  - changed_files_within_allowed_files: {_bool(not run.outside_allowed_files)}",
                f"  - command_exit_code: {run.command_exit_code if run.command_exit_code is not None else 'none'}",
                "  - verification_exit_code: "
                f"{run.verification_exit_code if run.verification_exit_code is not None else 'none'}",
                f"  - diff: {run.evidence_path}/diff.patch",
                "  - next_recommended_action: review_coder_worktree_run",
                "  - non_claims: no commit, push, deploy, provider call, or external mutation",
            ]
        )
    return lines


def render_coder_worktree_commit_review_lines(root: Path, delegation_id: str) -> list[str]:
    approvals = list_coder_worktree_commit_approvals(
        root,
        delegation_id=delegation_id,
        limit=10,
    )
    lines: list[str] = []
    for approval in approvals:
        lines.extend(
            [
                f"- delegation={delegation_id} coder_worktree_commit={approval.commit_artifact_path}",
                f"  - commit_approval_id: {approval.id}",
                f"  - run_id: {approval.run_id}",
                f"  - status: {approval.status}",
                f"  - failure_class: {approval.failure_class or 'none'}",
                f"  - commit_sha: {approval.commit_sha or 'none'}",
                f"  - parent_commit_sha: {approval.pre_commit_head}",
                f"  - effect_id: {approval.effect_id or 'none'}",
                f"  - github_handoff_available: {_bool(bool(approval.effect_id and approval.status == 'committed'))}",
                f"  - worktree_path: {approval.worktree_path}",
                f"  - branch_name: {approval.branch_name}",
                f"  - commit_message: {approval.commit_message or 'none'}",
                f"  - changed_files: {','.join(approval.changed_files) or 'none'}",
                f"  - request: {approval.request_artifact_path}",
                f"  - coder_commit_request: {(_coder_commit_dir(root.resolve(), approval) / 'coder_commit_request.json').relative_to(root.resolve())}",
                f"  - decision: {approval.decision_artifact_path or 'none'}",
                f"  - coder_commit_decision: {(_coder_commit_dir(root.resolve(), approval) / 'coder_commit_decision.json').relative_to(root.resolve())}",
                f"  - evidence: {approval.commit_artifact_path}",
                f"  - coder_worktree_local_commit: {(_coder_commit_dir(root.resolve(), approval) / 'commit.json').relative_to(root.resolve())}",
                "  - next_recommended_action: github_handoff" if approval.status == "committed" and approval.effect_id else "  - next_recommended_action: decide_or_commit_coder_worktree",
                "  - non_claims: local worktree commit only; no push, deploy, provider call, or external mutation",
            ]
        )
    return lines


def list_coder_worktree_approvals(
    root: Path,
    *,
    delegation_id: str | None = None,
    status: str | None = None,
    limit: int | None = 10,
) -> list[CoderWorktreeApprovalRecord]:
    storage = Storage(root.resolve() / ".agent" / "state.db")
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
    query = f"select * from coder_worktree_approvals {where} order by requested_at desc, id desc"
    if limit is not None:
        query += " limit ?"
        params.append(limit)
    with _connect(storage) as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [_row_to_approval(row) for row in rows]


def list_coder_worktree_runs(
    root: Path,
    *,
    delegation_id: str | None = None,
    limit: int | None = 10,
) -> list[CoderWorktreeRunRecord]:
    storage = Storage(root.resolve() / ".agent" / "state.db")
    if not storage.db_path.exists():
        return []
    _ensure_tables(storage)
    clauses: list[str] = []
    params: list[object] = []
    if delegation_id is not None:
        clauses.append("delegation_id = ?")
        params.append(delegation_id)
    where = f"where {' and '.join(clauses)}" if clauses else ""
    query = f"select * from coder_worktree_runs {where} order by completed_at desc, id desc"
    if limit is not None:
        query += " limit ?"
        params.append(limit)
    with _connect(storage) as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [_row_to_run(row) for row in rows]


def list_coder_worktree_commit_approvals(
    root: Path,
    *,
    delegation_id: str | None = None,
    status: str | None = None,
    limit: int | None = 10,
) -> list[CoderWorktreeCommitApprovalRecord]:
    storage = Storage(root.resolve() / ".agent" / "state.db")
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
        f"select * from coder_worktree_commit_approvals {where} "
        "order by requested_at desc, id desc"
    )
    if limit is not None:
        query += " limit ?"
        params.append(limit)
    with _connect(storage) as connection:
        rows = connection.execute(query, tuple(params)).fetchall()
    return [_row_to_commit_approval(row) for row in rows]


def latest_coder_worktree_approval_for_delegation(
    root: Path,
    delegation_id: str,
) -> CoderWorktreeApprovalRecord | None:
    approvals = list_coder_worktree_approvals(
        root,
        delegation_id=delegation_id,
        limit=1,
    )
    return approvals[0] if approvals else None


def latest_coder_worktree_run_for_delegation(
    root: Path,
    delegation_id: str,
) -> CoderWorktreeRunRecord | None:
    runs = list_coder_worktree_runs(root, delegation_id=delegation_id, limit=1)
    return runs[0] if runs else None


def latest_coder_worktree_commit_for_delegation(
    root: Path,
    delegation_id: str,
) -> CoderWorktreeCommitApprovalRecord | None:
    approvals = list_coder_worktree_commit_approvals(
        root,
        delegation_id=delegation_id,
        limit=1,
    )
    return approvals[0] if approvals else None


def get_coder_worktree_approval(
    storage: Storage,
    approval_id: str,
) -> CoderWorktreeApprovalRecord | None:
    _ensure_tables(storage)
    with _connect(storage) as connection:
        row = connection.execute(
            "select * from coder_worktree_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_approval(row) if row is not None else None


def get_coder_worktree_run(
    storage: Storage,
    run_id: str,
) -> CoderWorktreeRunRecord | None:
    _ensure_tables(storage)
    with _connect(storage) as connection:
        row = connection.execute(
            "select * from coder_worktree_runs where id = ?",
            (run_id,),
        ).fetchone()
    return _row_to_run(row) if row is not None else None


def get_coder_worktree_commit_approval(
    storage: Storage,
    approval_id: str,
) -> CoderWorktreeCommitApprovalRecord | None:
    _ensure_tables(storage)
    with _connect(storage) as connection:
        row = connection.execute(
            "select * from coder_worktree_commit_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_commit_approval(row) if row is not None else None


def _load_latest_plan(
    root: Path,
    storage: Storage,
    delegation_id: str,
) -> tuple[Path, dict[str, Any], str]:
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        raise CoderWorktreeApprovalError(f"delegation not found: {delegation_id}")
    pattern = root / ".clanker" / "delegations" / delegation_id / "runs" / "*" / "coder_prep" / "coder_worktree_plan.json"
    candidates = [path for path in root.glob(str(pattern.relative_to(root))) if path.exists()]
    if not candidates:
        raise CoderWorktreeApprovalError("coder worktree plan is not readable")
    plan_path = max(candidates, key=lambda path: path.stat().st_mtime_ns)
    try:
        payload = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoderWorktreeApprovalError("coder worktree plan is not readable") from error
    return plan_path, payload, hashlib.sha256(plan_path.read_bytes()).hexdigest()


def _validate_plan(
    root: Path,
    storage: Storage,
    plan_path: Path,
    payload: dict[str, Any],
) -> tuple[str, str, list[str], str]:
    if payload.get("kind") != CODER_WORKTREE_PLAN_KIND:
        raise CoderWorktreeApprovalError(
            f"unsupported coder worktree plan kind: {payload.get('kind')}"
        )
    if payload.get("dispatch_ready") is not False:
        raise CoderWorktreeApprovalError("coder worktree plan is dispatch-ready unexpectedly")
    gate = _dict_value(payload.get("approval_gate"))
    if gate.get("status") != "operator_approval_required":
        raise CoderWorktreeApprovalError("coder worktree plan does not require operator approval")
    source = _dict_value(payload.get("source"))
    prep_sha = str(source.get("coder_prep_md_sha256") or "")
    if not prep_sha:
        raise CoderWorktreeApprovalError("coder worktree plan source hash is missing")
    project = _dict_value(payload.get("project"))
    project_id = str(project.get("id") or "")
    if not project_id or storage.get_registered_project(project_id) is None:
        raise CoderWorktreeApprovalError(f"project is not registered: {project_id or 'unknown'}")
    allowed_files = [
        str(path).strip()
        for path in _dict_value(payload.get("bounded_coding_task")).get("allowed_files", [])
        if str(path).strip()
    ]
    if not allowed_files:
        raise CoderWorktreeApprovalError("coder worktree plan has no allowed files")
    source_run_id = str(source.get("run_id") or "unknown")
    return project_id, source_run_id, allowed_files, prep_sha


def _validate_source_chain(root: Path, plan_path: Path, payload: dict[str, Any]) -> None:
    source = _dict_value(payload.get("source"))
    prep_json = str(source.get("coder_prep_json") or "")
    prep_path = root / prep_json
    if not prep_json or not prep_path.exists():
        raise CoderWorktreeRunError("coder prep is not readable")
    try:
        prep_payload = json.loads(prep_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoderWorktreeRunError("coder prep is not readable") from error
    handoff_json = str(_dict_value(prep_payload.get("source")).get("handoff_json") or "")
    handoff_path = root / handoff_json
    if not handoff_json or not handoff_path.exists():
        raise CoderWorktreeRunError("implementation handoff is not readable")
    try:
        json.loads(handoff_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoderWorktreeRunError("implementation handoff is not readable") from error


def _validate_safe_command(command: str) -> None:
    stripped = command.strip()
    if not stripped:
        raise CoderWorktreeRunError("command is required")
    lowered = stripped.lower()
    unsafe_fragments = [
        "git push",
        "gh pr create",
        "curl",
        "wget",
        "ssh",
        "scp",
        "rsync",
        "sudo",
        "rm -rf",
        "docker push",
        "npm publish",
        "twine upload",
        "deploy",
        "kubectl",
        "terraform apply",
        "osascript",
    ]
    for fragment in unsafe_fragments:
        if fragment in lowered:
            raise CoderWorktreeRunError(f"unsafe command token: {fragment}")
    if re.search(r"(^|[\s;&|])open($|[\s;&|])", lowered):
        raise CoderWorktreeRunError("unsafe command token: open")
    allowed_prefixes = (
        "python3 -m pytest",
        "python -m pytest",
        "python3 -m py_compile",
        "python -m py_compile",
        "python3 scripts/",
        "python scripts/",
        "npm test",
    )
    if not lowered.startswith(allowed_prefixes):
        raise CoderWorktreeRunError("unsafe command: unsupported local command shape")


def _ensure_tables(storage: Storage) -> None:
    storage.db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(storage) as connection:
        connection.executescript(
            """
            create table if not exists coder_worktree_approvals (
                id text primary key,
                delegation_id text not null,
                source_run_id text not null,
                project_id text not null,
                status text not null,
                source_plan_path text not null,
                source_plan_sha256 text not null,
                source_coder_prep_md_sha256 text not null,
                request_artifact_path text not null,
                decision_artifact_path text,
                requested_by text not null,
                request_note text not null,
                decided_by text,
                decision_note text,
                requested_at text not null,
                decided_at text
            );

            create table if not exists coder_worktree_runs (
                id text primary key,
                delegation_id text not null,
                source_run_id text not null,
                project_id text not null,
                approval_id text not null,
                source_plan_path text not null,
                source_plan_sha256 text not null,
                status text not null,
                failure_class text,
                worktree_path text not null,
                branch_name text not null,
                command text not null,
                command_exit_code integer,
                verification_command text,
                verification_exit_code integer,
                changed_files text not null,
                outside_allowed_files text not null,
                evidence_path text not null,
                started_at text not null,
                completed_at text not null
            );

            create table if not exists coder_worktree_commit_approvals (
                id text primary key,
                run_id text not null,
                delegation_id text not null,
                source_run_id text not null,
                project_id text not null,
                status text not null,
                failure_class text,
                source_run_evidence_path text not null,
                source_coder_worktree_run_sha256 text not null,
                source_diff_sha256 text not null,
                review_path text not null,
                worktree_path text not null,
                branch_name text not null,
                pre_commit_head text not null,
                changed_files text not null,
                request_artifact_path text not null,
                decision_artifact_path text,
                commit_artifact_path text not null,
                commit_message text not null default '',
                allow_unverified integer not null default 0,
                effect_id text,
                requested_by text not null,
                request_note text not null,
                decided_by text,
                decision_note text,
                committed_by text,
                commit_sha text,
                requested_at text not null,
                decided_at text,
                committed_at text
            );

            create index if not exists idx_coder_worktree_approvals_delegation
                on coder_worktree_approvals (delegation_id, requested_at);
            create index if not exists idx_coder_worktree_approvals_plan
                on coder_worktree_approvals (delegation_id, source_plan_sha256);
            create index if not exists idx_coder_worktree_runs_delegation
                on coder_worktree_runs (delegation_id, completed_at);
            create index if not exists idx_coder_worktree_runs_approval_plan
                on coder_worktree_runs (approval_id, source_plan_sha256, status);
            create index if not exists idx_coder_worktree_commit_approvals_delegation
                on coder_worktree_commit_approvals (delegation_id, requested_at);
            create index if not exists idx_coder_worktree_commit_approvals_run
                on coder_worktree_commit_approvals (
                    run_id,
                    source_coder_worktree_run_sha256,
                    source_diff_sha256,
                    status
                );
            """
        )
        _ensure_column(
            connection,
            "coder_worktree_commit_approvals",
            "commit_message",
            "text not null default ''",
        )
        _ensure_column(
            connection,
            "coder_worktree_commit_approvals",
            "allow_unverified",
            "integer not null default 0",
        )
        _ensure_column(
            connection,
            "coder_worktree_commit_approvals",
            "effect_id",
            "text",
        )


def _insert_approval(
    storage: Storage,
    *,
    approval_id: str,
    delegation_id: str,
    source_run_id: str,
    project_id: str,
    source_plan_path: str,
    source_plan_sha256: str,
    source_coder_prep_md_sha256: str,
    request_artifact_path: str,
    decision_artifact_path: str,
    requested_by: str,
    request_note: str,
    requested_at: str,
) -> CoderWorktreeApprovalRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            insert into coder_worktree_approvals (
                id, delegation_id, source_run_id, project_id, status,
                source_plan_path, source_plan_sha256, source_coder_prep_md_sha256,
                request_artifact_path, decision_artifact_path, requested_by,
                request_note, requested_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                approval_id,
                delegation_id,
                source_run_id,
                project_id,
                "pending_operator_approval",
                source_plan_path,
                source_plan_sha256,
                source_coder_prep_md_sha256,
                request_artifact_path,
                decision_artifact_path,
                requested_by,
                request_note,
                requested_at,
            ),
        )
        row = connection.execute(
            "select * from coder_worktree_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_approval(row)


def _mark_approval_approved(
    storage: Storage,
    approval_id: str,
    *,
    decided_by: str,
    decision_note: str,
    decided_at: str,
) -> CoderWorktreeApprovalRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_approvals
            set status = 'approved',
                decided_by = ?,
                decision_note = ?,
                decided_at = ?
            where id = ?
            """,
            (decided_by, decision_note, decided_at, approval_id),
        )
        row = connection.execute(
            "select * from coder_worktree_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_approval(row)


def _insert_run(
    storage: Storage,
    *,
    run_id: str,
    delegation_id: str,
    source_run_id: str,
    project_id: str,
    approval_id: str,
    source_plan_path: str,
    source_plan_sha256: str,
    status: str,
    failure_class: str | None,
    worktree_path: str,
    branch_name: str,
    command: str,
    command_exit_code: int,
    verification_command: str | None,
    verification_exit_code: int | None,
    changed_files: list[str],
    outside_allowed_files: list[str],
    evidence_path: str,
    started_at: str,
    completed_at: str,
) -> CoderWorktreeRunRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            insert into coder_worktree_runs (
                id, delegation_id, source_run_id, project_id, approval_id,
                source_plan_path, source_plan_sha256, status, failure_class,
                worktree_path, branch_name, command, command_exit_code,
                verification_command, verification_exit_code, changed_files,
                outside_allowed_files, evidence_path, started_at, completed_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                delegation_id,
                source_run_id,
                project_id,
                approval_id,
                source_plan_path,
                source_plan_sha256,
                status,
                failure_class,
                worktree_path,
                branch_name,
                command,
                command_exit_code,
                verification_command,
                verification_exit_code,
                json.dumps(changed_files, sort_keys=True),
                json.dumps(outside_allowed_files, sort_keys=True),
                evidence_path,
                started_at,
                completed_at,
            ),
        )
        row = connection.execute(
            "select * from coder_worktree_runs where id = ?",
            (run_id,),
        ).fetchone()
    return _row_to_run(row)


def _insert_commit_approval(
    storage: Storage,
    *,
    approval_id: str,
    run_id: str,
    delegation_id: str,
    source_run_id: str,
    project_id: str,
    source_run_evidence_path: str,
    source_coder_worktree_run_sha256: str,
    source_diff_sha256: str,
    review_path: str,
    worktree_path: str,
    branch_name: str,
    pre_commit_head: str,
    changed_files: list[str],
    request_artifact_path: str,
    decision_artifact_path: str,
    commit_artifact_path: str,
    commit_message: str,
    allow_unverified: bool,
    requested_by: str,
    request_note: str,
    requested_at: str,
) -> CoderWorktreeCommitApprovalRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            insert into coder_worktree_commit_approvals (
                id, run_id, delegation_id, source_run_id, project_id, status,
                source_run_evidence_path, source_coder_worktree_run_sha256,
                source_diff_sha256, review_path, worktree_path, branch_name,
                pre_commit_head, changed_files, request_artifact_path,
                decision_artifact_path, commit_artifact_path, commit_message,
                allow_unverified, requested_by, request_note, requested_at
            )
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                approval_id,
                run_id,
                delegation_id,
                source_run_id,
                project_id,
                "pending_operator_approval",
                source_run_evidence_path,
                source_coder_worktree_run_sha256,
                source_diff_sha256,
                review_path,
                worktree_path,
                branch_name,
                pre_commit_head,
                json.dumps(changed_files, sort_keys=True),
                request_artifact_path,
                decision_artifact_path,
                commit_artifact_path,
                commit_message,
                1 if allow_unverified else 0,
                requested_by,
                request_note,
                requested_at,
            ),
        )
        row = connection.execute(
            "select * from coder_worktree_commit_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_commit_approval(row)


def _mark_commit_approval_approved(
    storage: Storage,
    approval_id: str,
    *,
    decided_by: str,
    decision_note: str,
    decided_at: str,
) -> CoderWorktreeCommitApprovalRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_commit_approvals
            set status = 'approved',
                decided_by = ?,
                decision_note = ?,
                decided_at = ?,
                failure_class = null
            where id = ?
            """,
            (decided_by, decision_note, decided_at, approval_id),
        )
        row = connection.execute(
            "select * from coder_worktree_commit_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_commit_approval(row)


def _mark_commit_approval_committed(
    storage: Storage,
    approval_id: str,
    *,
    committed_by: str,
    commit_sha: str,
    committed_at: str,
) -> CoderWorktreeCommitApprovalRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_commit_approvals
            set status = 'committed',
                committed_by = ?,
                commit_sha = ?,
                committed_at = ?,
                failure_class = null
            where id = ?
            """,
            (committed_by, commit_sha, committed_at, approval_id),
        )
        row = connection.execute(
            "select * from coder_worktree_commit_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_commit_approval(row)


def _mark_commit_approval_effect(
    storage: Storage,
    approval_id: str,
    *,
    effect_id: str,
) -> CoderWorktreeCommitApprovalRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_commit_approvals
            set effect_id = ?
            where id = ?
            """,
            (effect_id, approval_id),
        )
        row = connection.execute(
            "select * from coder_worktree_commit_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_commit_approval(row)


def _mark_commit_approval_blocked(
    storage: Storage,
    approval_id: str,
    *,
    failure_class: str,
) -> CoderWorktreeCommitApprovalRecord:
    with _connect(storage) as connection:
        connection.execute(
            """
            update coder_worktree_commit_approvals
            set status = 'blocked',
                failure_class = ?
            where id = ?
            """,
            (failure_class, approval_id),
        )
        row = connection.execute(
            "select * from coder_worktree_commit_approvals where id = ?",
            (approval_id,),
        ).fetchone()
    return _row_to_commit_approval(row)


def _latest_approval_for_plan(
    storage: Storage,
    delegation_id: str,
    source_plan_sha256: str,
) -> CoderWorktreeApprovalRecord | None:
    _ensure_tables(storage)
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_approvals
            where delegation_id = ?
              and source_plan_sha256 = ?
              and status in ('pending_operator_approval', 'approved')
            order by requested_at desc, id desc
            limit 1
            """,
            (delegation_id, source_plan_sha256),
        ).fetchone()
    return _row_to_approval(row) if row is not None else None


def _latest_approval_for_delegation(
    storage: Storage,
    delegation_id: str,
) -> CoderWorktreeApprovalRecord | None:
    _ensure_tables(storage)
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_approvals
            where delegation_id = ?
              and status in ('pending_operator_approval', 'approved')
            order by requested_at desc, id desc
            limit 1
            """,
            (delegation_id,),
        ).fetchone()
    return _row_to_approval(row) if row is not None else None


def _latest_completed_run_for_approval(
    storage: Storage,
    approval_id: str,
    source_plan_sha256: str,
) -> CoderWorktreeRunRecord | None:
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_runs
            where approval_id = ?
              and source_plan_sha256 = ?
              and status = 'completed'
            order by completed_at desc, id desc
            limit 1
            """,
            (approval_id, source_plan_sha256),
        ).fetchone()
    return _row_to_run(row) if row is not None else None


def _latest_commit_approval_for_run(
    storage: Storage,
    run_id: str,
    source_run_sha256: str,
    source_diff_sha256: str,
) -> CoderWorktreeCommitApprovalRecord | None:
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_commit_approvals
            where run_id = ?
              and source_coder_worktree_run_sha256 = ?
              and source_diff_sha256 = ?
              and status in ('pending_operator_approval', 'approved', 'committed')
            order by requested_at desc, id desc
            limit 1
            """,
            (run_id, source_run_sha256, source_diff_sha256),
        ).fetchone()
    return _row_to_commit_approval(row) if row is not None else None


def _latest_commit_request_for_run(
    storage: Storage,
    run_id: str,
) -> CoderWorktreeCommitApprovalRecord | None:
    with _connect(storage) as connection:
        row = connection.execute(
            """
            select * from coder_worktree_commit_approvals
            where run_id = ?
              and status in ('approved', 'committed', 'pending_operator_approval', 'blocked')
            order by requested_at desc, id desc
            limit 1
            """,
            (run_id,),
        ).fetchone()
    return _row_to_commit_approval(row) if row is not None else None


def _record_coder_worktree_incident(
    storage: Storage,
    *,
    project_id: str,
    run_id: str,
    delegation_id: str,
    failure_class: str,
    summary: str,
    evidence: dict[str, Any],
    evidence_path: str | None,
) -> str:
    return storage.record_incident(
        project_id=project_id,
        run_id=run_id,
        goal_id=None,
        task_id=delegation_id,
        task_type="coder_worktree_execution",
        incident_type="coder_worktree_execution_failure",
        severity="high" if failure_class == "bounded_file_violation" else "medium",
        status="open",
        summary=summary,
        failure_class=failure_class,
        verification_method="coder_worktree_execution",
        verification_path=evidence_path,
        failed_checks=[failure_class],
        evidence=evidence,
        artifacts=[evidence_path] if evidence_path else [],
        evidence_path=evidence_path,
    )


def _project_id_for_delegation(storage: Storage, delegation_id: str) -> str:
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        return "unknown"
    try:
        task = storage.get_task(delegation.parent_task_id)
    except KeyError:
        return "unknown"
    return task.project_id


def _row_to_approval(row: sqlite3.Row) -> CoderWorktreeApprovalRecord:
    return CoderWorktreeApprovalRecord(
        id=row["id"],
        delegation_id=row["delegation_id"],
        source_run_id=row["source_run_id"],
        project_id=row["project_id"],
        status=row["status"],
        source_plan_path=row["source_plan_path"],
        source_plan_sha256=row["source_plan_sha256"],
        source_coder_prep_md_sha256=row["source_coder_prep_md_sha256"],
        request_artifact_path=row["request_artifact_path"],
        decision_artifact_path=row["decision_artifact_path"],
        requested_by=row["requested_by"],
        request_note=row["request_note"],
        decided_by=row["decided_by"],
        decision_note=row["decision_note"],
        requested_at=row["requested_at"],
        decided_at=row["decided_at"],
    )


def _row_to_run(row: sqlite3.Row) -> CoderWorktreeRunRecord:
    return CoderWorktreeRunRecord(
        id=row["id"],
        delegation_id=row["delegation_id"],
        source_run_id=row["source_run_id"],
        project_id=row["project_id"],
        approval_id=row["approval_id"],
        source_plan_path=row["source_plan_path"],
        source_plan_sha256=row["source_plan_sha256"],
        status=row["status"],
        failure_class=row["failure_class"],
        worktree_path=row["worktree_path"],
        branch_name=row["branch_name"],
        command=row["command"],
        command_exit_code=row["command_exit_code"],
        verification_command=row["verification_command"],
        verification_exit_code=row["verification_exit_code"],
        changed_files=json.loads(row["changed_files"] or "[]"),
        outside_allowed_files=json.loads(row["outside_allowed_files"] or "[]"),
        evidence_path=row["evidence_path"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
    )


def _row_to_commit_approval(row: sqlite3.Row) -> CoderWorktreeCommitApprovalRecord:
    return CoderWorktreeCommitApprovalRecord(
        id=row["id"],
        run_id=row["run_id"],
        delegation_id=row["delegation_id"],
        source_run_id=row["source_run_id"],
        project_id=row["project_id"],
        status=row["status"],
        failure_class=row["failure_class"],
        source_run_evidence_path=row["source_run_evidence_path"],
        source_coder_worktree_run_sha256=row["source_coder_worktree_run_sha256"],
        source_diff_sha256=row["source_diff_sha256"],
        review_path=row["review_path"],
        worktree_path=row["worktree_path"],
        branch_name=row["branch_name"],
        pre_commit_head=row["pre_commit_head"],
        changed_files=json.loads(row["changed_files"] or "[]"),
        request_artifact_path=row["request_artifact_path"],
        decision_artifact_path=row["decision_artifact_path"],
        commit_artifact_path=row["commit_artifact_path"],
        commit_message=row["commit_message"] or "",
        allow_unverified=bool(row["allow_unverified"]),
        effect_id=row["effect_id"],
        requested_by=row["requested_by"],
        request_note=row["request_note"],
        decided_by=row["decided_by"],
        decision_note=row["decision_note"],
        committed_by=row["committed_by"],
        commit_sha=row["commit_sha"],
        requested_at=row["requested_at"],
        decided_at=row["decided_at"],
        committed_at=row["committed_at"],
    )


def _approval_to_payload(approval: CoderWorktreeApprovalRecord) -> dict[str, Any]:
    return {
        "id": approval.id,
        "delegation_id": approval.delegation_id,
        "source_run_id": approval.source_run_id,
        "project_id": approval.project_id,
        "status": approval.status,
        "source_plan_path": approval.source_plan_path,
        "source_plan_sha256": approval.source_plan_sha256,
        "request_artifact_path": approval.request_artifact_path,
        "decision_artifact_path": approval.decision_artifact_path,
        "requested_by": approval.requested_by,
        "decided_by": approval.decided_by,
        "requested_at": approval.requested_at,
        "decided_at": approval.decided_at,
    }


def _coder_commit_dir(root: Path, approval: CoderWorktreeCommitApprovalRecord) -> Path:
    return root / approval.source_run_evidence_path / "coder_commit"


def _coder_commit_request_payload(
    legacy_payload: dict[str, Any],
    *,
    evidence: dict[str, Any],
    run_payload: dict[str, Any],
) -> dict[str, Any]:
    return {
        "kind": CODER_COMMIT_REQUEST_KIND,
        "schema_version": 1,
        "commit_request_id": legacy_payload["commit_approval_id"],
        "coder_worktree_run_id": legacy_payload["run_id"],
        "delegation_id": legacy_payload["delegation_id"],
        "project_id": legacy_payload["project_id"],
        "worktree_path": legacy_payload["worktree_path"],
        "branch_name": legacy_payload["branch_name"],
        "source_run_json": str(evidence["run_json_path"]),
        "source_run_sha256": legacy_payload["source_coder_worktree_run_sha256"],
        "approval_required_before": [
            "stage_allowed_files",
            "create_local_commit",
        ],
        "commit_message": legacy_payload["commit_message"],
        "requested_by": legacy_payload["requested_by"],
        "note": legacy_payload["note"],
        "status": legacy_payload["status"],
        "allowed_files": list(run_payload.get("allowed_files", [])),
        "changed_files": legacy_payload["changed_files"],
        "outside_allowed_files": list(run_payload.get("outside_allowed_files", [])),
        "command_exit_code": legacy_payload.get("command_exit_code", run_payload.get("command_exit_code")),
        "verification_exit_code": run_payload.get("verification_exit_code"),
        "allow_unverified": legacy_payload["allow_unverified"],
        "bounded_file_validation": {
            "valid": bool(run_payload.get("changed_files_within_allowed_files")),
            "status": "passed" if run_payload.get("changed_files_within_allowed_files") else "blocked",
        },
        "non_claims": [
            "Commit request does not stage files.",
            "Commit request does not create a commit.",
            "Commit request does not push, deploy, create a PR, call providers, or use the network.",
        ],
    }


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_run_commit_eligible(
    run: CoderWorktreeRunRecord,
    *,
    run_payload: dict[str, Any],
    allow_unverified: bool,
) -> None:
    if run.failure_class == "bounded_file_violation" or run.outside_allowed_files:
        raise CoderWorktreeCommitError("bounded validation failed")
    if run.failure_class == "verification_failed":
        raise CoderWorktreeCommitError("verification failed")
    if run.status != "completed":
        raise CoderWorktreeCommitError(f"coder worktree run is not completed: {run.status}")
    if run_payload.get("changed_files_within_allowed_files") is not True:
        raise CoderWorktreeCommitError("bounded validation failed")
    if run.command_exit_code != 0:
        raise CoderWorktreeCommitError("command failed")
    if run.verification_exit_code != 0 and not allow_unverified:
        raise CoderWorktreeCommitError("verification failed")
    if not run.changed_files:
        raise CoderWorktreeCommitError("coder worktree run has no changed files to commit")


def _load_run_evidence(root: Path, run: CoderWorktreeRunRecord) -> dict[str, Any]:
    evidence_dir = root / run.evidence_path
    run_json_path = evidence_dir / "run.json"
    diff_path = evidence_dir / "diff.patch"
    changed_files_path = evidence_dir / "changed_files.json"
    bounded_path = evidence_dir / "bounded_file_validation.json"
    required_paths = (
        run_json_path,
        diff_path,
        changed_files_path,
        bounded_path,
        evidence_dir / "stdout.txt",
        evidence_dir / "stderr.txt",
        evidence_dir / "verification_command.txt",
        evidence_dir / "verification_stdout.txt",
        evidence_dir / "verification_stderr.txt",
    )
    for path in required_paths:
        if not path.exists():
            raise CoderWorktreeCommitError(
                f"coder worktree run evidence is not readable: {path.relative_to(root)}"
            )
    try:
        run_payload = json.loads(run_json_path.read_text(encoding="utf-8"))
        changed_payload = json.loads(changed_files_path.read_text(encoding="utf-8"))
        bounded_payload = json.loads(bounded_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CoderWorktreeCommitError("coder worktree run evidence is not readable") from error
    if run_payload.get("kind") != RUN_KIND:
        raise CoderWorktreeCommitError("coder worktree run evidence has unexpected kind")
    if sorted(changed_payload.get("changed_files", [])) != sorted(run.changed_files):
        raise CoderWorktreeCommitError("coder worktree run changed-file evidence is stale")
    diff_text = diff_path.read_text(encoding="utf-8")
    return {
        "evidence_dir": evidence_dir,
        "run_json_path": run_json_path,
        "diff_path": diff_path,
        "diff_text": diff_text,
        "run_sha256": hashlib.sha256(run_json_path.read_bytes()).hexdigest(),
        "diff_sha256": hashlib.sha256(diff_path.read_bytes()).hexdigest(),
        "run_payload": run_payload,
        "bounded_payload": bounded_payload,
        "allowed_files": list(run_payload.get("allowed_files", [])),
    }


def _review_path_for_run(root: Path, run: CoderWorktreeRunRecord) -> Path:
    return root / "runs" / run.source_run_id / "review.md"


def _review_mentions_run(review_path: Path, run_id: str) -> bool:
    try:
        return run_id in review_path.read_text(encoding="utf-8")
    except OSError:
        return False


def _current_worktree_snapshot(worktree_path: Path) -> dict[str, Any]:
    unstaged = _git_lines(["git", "diff", "--name-only"], cwd=worktree_path)
    staged = _git_lines(["git", "diff", "--cached", "--name-only"], cwd=worktree_path)
    untracked = _git_lines(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=worktree_path,
    )
    return {
        "head": _git_output(["git", "rev-parse", "HEAD"], cwd=worktree_path).strip(),
        "branch": _git_output(["git", "branch", "--show-current"], cwd=worktree_path).strip(),
        "diff": _git_output(
            ["git", "diff", "--no-ext-diff", "--binary"],
            cwd=worktree_path,
        ),
        "changed_files": sorted(set(unstaged + staged + untracked)),
        "staged_files": sorted(set(staged)),
        "untracked_files": sorted(set(untracked)),
    }


def _raise_if_snapshot_stale(
    *,
    snapshot: dict[str, Any],
    expected_diff: str,
    expected_changed_files: list[str],
    expected_head: str | None,
    detail_path: Path,
) -> None:
    if expected_head is not None and snapshot["head"] != expected_head:
        raise CoderWorktreeCommitError(
            f"stale evidence: worktree HEAD changed from {expected_head} to {snapshot['head']}"
        )
    if snapshot["diff"] != expected_diff:
        raise CoderWorktreeCommitError(
            f"stale evidence: current diff no longer matches {detail_path}"
        )
    if snapshot["changed_files"] != sorted(expected_changed_files):
        raise CoderWorktreeCommitError(
            "stale evidence: current changed files no longer match reviewed run evidence"
        )


def _raise_if_source_hash_changed(
    approval: CoderWorktreeCommitApprovalRecord,
    evidence: dict[str, Any],
) -> None:
    if evidence["run_sha256"] != approval.source_coder_worktree_run_sha256:
        raise CoderWorktreeCommitError("stale evidence: coder worktree run evidence changed")
    if evidence["diff_sha256"] != approval.source_diff_sha256:
        raise CoderWorktreeCommitError("stale evidence: coder worktree diff evidence changed")


def _block_commit_approval(
    root: Path,
    storage: Storage,
    approval: CoderWorktreeCommitApprovalRecord,
    *,
    failure_class: str,
    detail: str,
    verification_exit_code: int | None,
) -> CoderWorktreeCommitApprovalRecord:
    blocked_at = utc_now()
    payload = {
        "kind": COMMIT_KIND,
        "schema_version": 1,
        "status": "blocked",
        "failure_class": failure_class,
        "detail": detail,
        "commit_approval_id": approval.id,
        "run_id": approval.run_id,
        "delegation_id": approval.delegation_id,
        "project_id": approval.project_id,
        "commit_sha": None,
        "verification_exit_code": verification_exit_code,
        "blocked_at": blocked_at,
        "commit_created": False,
        "push_created": False,
        "deploy_created": False,
        "provider_calls_taken_by_clankeros": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
    }
    _write_json(root / approval.commit_artifact_path, payload)
    blocked = _mark_commit_approval_blocked(
        storage,
        approval.id,
        failure_class=failure_class,
    )
    _record_coder_worktree_incident(
        storage,
        project_id=approval.project_id,
        run_id=approval.run_id,
        delegation_id=approval.delegation_id,
        failure_class=failure_class,
        summary=f"Coder worktree commit promotion blocked: {failure_class}",
        evidence=payload,
        evidence_path=approval.commit_artifact_path,
    )
    return blocked


def _ensure_recorded_commit_exists(approval: CoderWorktreeCommitApprovalRecord) -> None:
    if not approval.commit_sha:
        raise CoderWorktreeCommitError("recorded commit SHA is missing")
    worktree_path = Path(approval.worktree_path)
    if not worktree_path.exists():
        raise CoderWorktreeCommitError(f"worktree does not exist: {worktree_path}")
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{approval.commit_sha}^{{commit}}"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CoderWorktreeCommitError(f"recorded commit is missing: {approval.commit_sha}")


def _validate_git_worktree_safe(worktree_path: Path, expected_branch: str) -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise CoderWorktreeCommitError("worktree is not a git worktree")
    git_dir = Path(_git_output(["git", "rev-parse", "--git-dir"], cwd=worktree_path).strip())
    if not git_dir.is_absolute():
        git_dir = worktree_path / git_dir
    unsafe_markers = [
        git_dir / "MERGE_HEAD",
        git_dir / "CHERRY_PICK_HEAD",
        git_dir / "REVERT_HEAD",
        git_dir / "rebase-merge",
        git_dir / "rebase-apply",
    ]
    if any(path.exists() for path in unsafe_markers):
        raise CoderWorktreeCommitError("git state unsafe")
    branch = _git_output(["git", "branch", "--show-current"], cwd=worktree_path).strip()
    if branch != expected_branch:
        raise CoderWorktreeCommitError(
            f"source_state_changed: branch changed from {expected_branch} to {branch}"
        )


def _record_coder_commit_effect(
    root: Path,
    storage: Storage,
    *,
    approval: CoderWorktreeCommitApprovalRecord,
    commit_payload: dict[str, Any],
    commit_artifact_path: Path,
    committed_diff_path: Path,
    verification_command: str,
    verification_exit_code: int,
) -> Effect:
    if approval.effect_id:
        try:
            return storage.get_effect(approval.effect_id)
        except KeyError:
            pass
    idempotency_key = f"coder_worktree_commit:{approval.id}:{commit_payload['commit_sha']}"
    existing = storage.list_effects_with_idempotency_prefix(idempotency_key)
    if existing:
        return existing[0]
    task_id = _task_id_for_delegation(storage, approval.delegation_id)
    proposed_payload = {
        "base_commit": commit_payload["parent_commit_sha"],
        "branch_name": approval.branch_name,
        "worktree_path": approval.worktree_path,
        "changed_files": commit_payload["committed_files"],
        "diff_path": str(committed_diff_path),
        "committed_diff_path": str(committed_diff_path),
        "test_command": verification_command,
        "test_exit_code": verification_exit_code,
        "coder_worktree_run_id": approval.run_id,
        "commit_request_id": approval.id,
    }
    result_json = {
        **commit_payload,
        "approval_id": approval.id,
        "commit_approval_id": approval.id,
        "effect_kind": "coder_worktree_local_commit",
    }
    return storage.record_effect(
        run_id=approval.run_id,
        task_id=task_id,
        project_id=approval.project_id,
        capability="coder_worktree_commit",
        effect_type="local_git_commit",
        idempotency_key=idempotency_key,
        target=approval.worktree_path,
        proposed_payload=proposed_payload,
        status="committed",
        required_approval_id=approval.id,
        attempted_at=commit_payload.get("committed_at") or utc_now(),
        committed_at=commit_payload.get("committed_at") or utc_now(),
        evidence_path=str(commit_artifact_path),
        compensation_plan={
            "status": "manual_revert_available",
            "command": f"git revert {commit_payload['commit_sha']}",
            "scope": "local coder worktree branch only",
        },
        result_json=result_json,
    )


def _task_id_for_delegation(storage: Storage, delegation_id: str) -> str:
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        return delegation_id
    return delegation.parent_task_id


def _render_approval_request_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Worktree Approval Request",
            "",
            f"- approval_id: {payload['approval_id']}",
            f"- delegation_id: {payload['delegation_id']}",
            f"- project_id: {payload['project_id']}",
            f"- status: {payload['status']}",
            f"- source_plan_sha256: {payload['source_plan_sha256']}",
            "",
            "## Allowed Files",
            "",
            *[f"- {path}" for path in payload["allowed_files"]],
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _render_approval_decision_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Worktree Approval Decision",
            "",
            f"- approval_id: {payload['approval_id']}",
            f"- status: {payload['status']}",
            f"- decided_by: {payload['decided_by']}",
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _render_commit_approval_request_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Worktree Commit Approval Request",
            "",
            f"- commit_approval_id: {payload['commit_approval_id']}",
            f"- run_id: {payload['run_id']}",
            f"- delegation_id: {payload['delegation_id']}",
            f"- project_id: {payload['project_id']}",
            f"- status: {payload['status']}",
            f"- source_coder_worktree_run_sha256: {payload['source_coder_worktree_run_sha256']}",
            f"- source_diff_sha256: {payload['source_diff_sha256']}",
            f"- review_path: {payload['review_path']}",
            f"- worktree_path: {payload['worktree_path']}",
            f"- branch_name: {payload['branch_name']}",
            f"- pre_commit_head: {payload['pre_commit_head']}",
            "",
            "## Changed Files",
            "",
            *[f"- {path}" for path in payload["changed_files"]],
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _render_commit_approval_decision_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Worktree Commit Approval Decision",
            "",
            f"- commit_approval_id: {payload['commit_approval_id']}",
            f"- run_id: {payload['run_id']}",
            f"- status: {payload['status']}",
            f"- decided_by: {payload['decided_by']}",
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _render_coder_commit_request_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Commit Request",
            "",
            f"- commit_request_id: {payload['commit_request_id']}",
            f"- coder_worktree_run_id: {payload['coder_worktree_run_id']}",
            f"- delegation_id: {payload['delegation_id']}",
            f"- project_id: {payload['project_id']}",
            f"- status: {payload['status']}",
            f"- commit_message: {payload['commit_message']}",
            f"- source_run_sha256: {payload['source_run_sha256']}",
            f"- worktree_path: {payload['worktree_path']}",
            f"- branch_name: {payload['branch_name']}",
            "",
            "## Changed Files",
            "",
            *[f"- {path}" for path in payload["changed_files"]],
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _render_coder_commit_decision_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Commit Approval Decision",
            "",
            f"- commit_request_id: {payload['commit_request_id']}",
            f"- coder_worktree_run_id: {payload['coder_worktree_run_id']}",
            f"- status: {payload['status']}",
            f"- decided_by: {payload['decided_by']}",
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _render_coder_local_commit_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Coder Worktree Local Commit",
            "",
            f"- coder_worktree_run_id: {payload['coder_worktree_run_id']}",
            f"- commit_request_id: {payload['commit_request_id']}",
            f"- commit_sha: {payload['commit_sha']}",
            f"- parent_commit_sha: {payload['parent_commit_sha']}",
            f"- branch_name: {payload['branch_name']}",
            f"- worktree_path: {payload['worktree_path']}",
            f"- next_recommended_action: {payload['next_recommended_action']}",
            "",
            "## Committed Files",
            "",
            *[f"- {path}" for path in payload["committed_files"]],
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _render_run_summary(payload: dict[str, Any], evidence_dir: Path, root: Path) -> str:
    return "\n".join(
        [
            "# Approved Coder Worktree Run",
            "",
            f"- run_id: {payload['run_id']}",
            f"- delegation_id: {payload['delegation_id']}",
            f"- status: {payload['status']}",
            f"- failure_class: {payload['failure_class'] or 'none'}",
            f"- worktree_path: {payload['worktree_path']}",
            f"- branch_name: {payload['branch_name']}",
            f"- changed_files_within_allowed_files: {_bool(payload['changed_files_within_allowed_files'])}",
            f"- diff: {evidence_dir.relative_to(root) / 'diff.patch'}",
            f"- next_recommended_action: {payload['next_recommended_action']}",
            "",
            "## Non-Claims",
            "",
            *[f"- {claim}" for claim in payload["non_claims"]],
            "",
        ]
    )


def _branch_name(suggestion: str, run_id: str) -> str:
    base = suggestion.strip() or "codex/coder-worktree"
    base = re.sub(r"[^A-Za-z0-9._/-]+", "-", base).strip("-/")
    if not base.startswith("codex/"):
        base = f"codex/{base}"
    return f"{base}-{run_id[-12:]}"


def _git_output(args: list[str], *, cwd: Path) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout


def _git_lines(args: list[str], *, cwd: Path) -> list[str]:
    return [line.strip() for line in _git_output(args, cwd=cwd).splitlines() if line.strip()]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _connect(storage: Storage) -> sqlite3.Connection:
    connection = sqlite3.connect(storage.db_path)
    connection.row_factory = sqlite3.Row
    return connection


def _ensure_column(
    connection: sqlite3.Connection,
    table: str,
    column: str,
    definition: str,
) -> None:
    columns = {
        str(row["name"])
        for row in connection.execute(f"pragma table_info({table})").fetchall()
    }
    if column not in columns:
        connection.execute(f"alter table {table} add column {column} {definition}")


def _dict_value(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _bool(value: bool) -> str:
    return "true" if value else "false"
