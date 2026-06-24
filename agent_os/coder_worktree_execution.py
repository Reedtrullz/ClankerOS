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
from agent_os.storage import Storage, utc_now


APPROVAL_REQUEST_KIND = "coder_worktree_execution_approval_request"
APPROVAL_DECISION_KIND = "coder_worktree_execution_approval_decision"
RUN_KIND = "approved_coder_worktree_run"


class CoderWorktreeApprovalError(ValueError):
    pass


class CoderWorktreeRunError(ValueError):
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

            create index if not exists idx_coder_worktree_approvals_delegation
                on coder_worktree_approvals (delegation_id, requested_at);
            create index if not exists idx_coder_worktree_approvals_plan
                on coder_worktree_approvals (delegation_id, source_plan_sha256);
            create index if not exists idx_coder_worktree_runs_delegation
                on coder_worktree_runs (delegation_id, completed_at);
            create index if not exists idx_coder_worktree_runs_approval_plan
                on coder_worktree_runs (approval_id, source_plan_sha256, status);
            """
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


def _dict_value(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _bool(value: bool) -> str:
    return "true" if value else "false"
