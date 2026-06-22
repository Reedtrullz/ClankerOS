from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.ids import new_id
from agent_os.storage import Effect, Storage, WorktreeRecord, utc_now


@dataclass(frozen=True)
class CodingRunResult:
    goal_id: str
    run_id: str
    task_id: str
    status: str
    worktree: WorktreeRecord
    effect: Effect
    approval_id: str
    evidence_dir: Path


BLOCKED_COMMAND_FRAGMENTS = [
    "rm -rf",
    "rm -fr",
    "sudo ",
    "curl ",
    "wget ",
    "ssh ",
    "scp ",
    "rsync ",
    "git push",
    "git clean",
    ">/",
    "> /",
    "../",
]


def run_worktree_coding_goal(
    root: Path,
    *,
    project_name: str,
    description: str,
    command: str,
) -> CodingRunResult:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    project = storage.get_registered_project(project_name)
    if project is None:
        raise ValueError(f"project is not registered: {project_name}")
    _ensure_safe_command(command)
    _ensure_safe_command(project.default_test_command)

    goal_id = storage.create_goal(project.name, description)
    run_id = storage.create_run(goal_id, project.name, root / "runs")
    task_id = storage.create_task(
        goal_id=goal_id,
        run_id=run_id,
        project_id=project.name,
        task_type="coding_change",
        description=description,
        verification_plan={
            "type": "worktree_command",
            "command": command,
            "test_command": project.default_test_command,
        },
        risk_level="high",
        skill_tags=["local-shell", "git-worktree"],
    )

    run_dir = root / "runs" / run_id
    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "activity.md").write_text(
        f"# Activity For {run_id}\n\n- accepted coding goal for {project.name}\n",
        encoding="utf-8",
    )
    (run_dir / "events.jsonl").write_text("", encoding="utf-8")

    project_root = Path(project.root_path)
    base_commit = _git_stdout(project_root, ["rev-parse", "HEAD"])
    branch_name = f"clankeros/{run_id}"
    worktree_path = root / ".agent" / "worktrees" / project.name / run_id
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    _run_git(
        project_root,
        ["worktree", "add", "-b", branch_name, str(worktree_path), base_commit],
    )
    worktree = storage.record_worktree(
        project_id=project.name,
        task_id=task_id,
        run_id=run_id,
        base_commit=base_commit,
        branch_name=branch_name,
        worktree_path=str(worktree_path),
    )
    (evidence_dir / "worktree.json").write_text(
        json.dumps(
            {
                "id": worktree.id,
                "project_id": worktree.project_id,
                "task_id": worktree.task_id,
                "run_id": worktree.run_id,
                "base_commit": worktree.base_commit,
                "branch_name": worktree.branch_name,
                "worktree_path": worktree.worktree_path,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "project.json").write_text(
        json.dumps(
            {
                "name": project.name,
                "root_path": project.root_path,
                "default_test_command": project.default_test_command,
                "allowed_write_roots": project.allowed_write_roots,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "task.json").write_text(
        json.dumps(
            {
                "id": task_id,
                "goal_id": goal_id,
                "run_id": run_id,
                "description": description,
                "command": command,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    command_result = _run_shell_command(command, worktree_path)
    _write_command_evidence(evidence_dir, "command", command, worktree_path, command_result)

    _run_git(worktree_path, ["add", "-N", "."])
    status_text = _git_stdout(worktree_path, ["status", "--short", "--untracked-files=all"])
    changed_files = _git_stdout(worktree_path, ["diff", "--name-only"]).splitlines()
    diff_text = _git_stdout(worktree_path, ["diff", "--no-ext-diff"])
    allowed_write_roots = _changed_files_within_allowed_roots(
        changed_files,
        project_root,
        [Path(path) for path in project.allowed_write_roots],
    )

    (evidence_dir / "git_status.txt").write_text(status_text + "\n", encoding="utf-8")
    (evidence_dir / "diff.patch").write_text(diff_text, encoding="utf-8")
    (evidence_dir / "diff_summary.md").write_text(
        "\n".join(
            [
                "# Diff Summary",
                "",
                f"- changed_files: {len(changed_files)}",
                *(f"- {path}" for path in changed_files),
                "",
            ]
        ),
        encoding="utf-8",
    )

    test_result = _run_shell_command(project.default_test_command, worktree_path)
    _write_command_evidence(
        evidence_dir,
        "tests",
        project.default_test_command,
        worktree_path,
        test_result,
    )
    verification_passed = (
        command_result.returncode == 0
        and test_result.returncode == 0
        and bool(changed_files)
        and allowed_write_roots
    )
    verification = {
        "status": "passed" if verification_passed else "failed",
        "command": {"exit_code": command_result.returncode},
        "tests": {"exit_code": test_result.returncode},
        "diff": {"changed_files": changed_files, "has_diff": bool(changed_files)},
        "policy": {"allowed_write_roots": allowed_write_roots},
        "verified_at": utc_now(),
    }
    (evidence_dir / "verification.json").write_text(
        json.dumps(verification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    approval = storage.create_pending_approval_request_for_task(
        task_id,
        reason="approval required before local git commit side effect",
    )
    effect = storage.record_effect(
        run_id=run_id,
        task_id=task_id,
        project_id=project.name,
        capability="local_coding_agent",
        effect_type="local_git_commit",
        idempotency_key=f"{run_id}:{task_id}:local_git_commit",
        target=str(worktree_path),
        proposed_payload={
            "base_commit": base_commit,
            "branch_name": branch_name,
            "worktree_path": str(worktree_path),
            "changed_files": changed_files,
            "diff_path": str(evidence_dir / "diff.patch"),
            "test_command": project.default_test_command,
            "test_exit_code": test_result.returncode,
        },
        status="awaiting_approval" if verification_passed else "blocked",
        required_approval_id=approval.id,
        attempted_at=None,
        committed_at=None,
        evidence_path=str(evidence_dir / "summary.md"),
        compensation_plan={
            "status": "not_needed_before_commit",
            "reason": "local git commit has not been created",
        },
    )
    (evidence_dir / "effect.json").write_text(
        json.dumps(
            {
                "id": effect.id,
                "run_id": effect.run_id,
                "task_id": effect.task_id,
                "effect_type": effect.effect_type,
                "status": effect.status,
                "required_approval_id": effect.required_approval_id,
                "proposed_payload": effect.proposed_payload,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "approval.md").write_text(
        "\n".join(
            [
                "# Approval Required",
                "",
                f"- approval_id: {approval.id}",
                "- action_enabled: local_git_commit",
                f"- worktree: {worktree_path}",
                f"- branch: {branch_name}",
                f"- base_commit: {base_commit}",
                f"- changed_files: {','.join(changed_files) or 'none'}",
                f"- test_exit_code: {test_result.returncode}",
                f"- policy_allowed_write_roots: {allowed_write_roots}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (evidence_dir / "summary.md").write_text(
        "\n".join(
            [
                "# Coding Run Evidence",
                "",
                f"- run_id: {run_id}",
                f"- task_id: {task_id}",
                f"- project: {project.name}",
                f"- status: {effect.status}",
                f"- worktree: {worktree_path}",
                f"- branch: {branch_name}",
                f"- base_commit: {base_commit}",
                f"- changed_files: {','.join(changed_files) or 'none'}",
                f"- test_exit_code: {test_result.returncode}",
                f"- approval_id: {approval.id}",
                f"- effect_id: {effect.id}",
                "",
                "## Non-Claims",
                "",
                "- Does not create a local git commit.",
                "- Does not push, open a PR, merge, deploy, or mutate external systems.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    storage.complete_run(run_id, "waiting_approval" if verification_passed else "failed")
    storage.set_goal_status(goal_id, "waiting_approval" if verification_passed else "failed")

    return CodingRunResult(
        goal_id=goal_id,
        run_id=run_id,
        task_id=task_id,
        status=effect.status,
        worktree=worktree,
        effect=effect,
        approval_id=approval.id,
        evidence_dir=evidence_dir,
    )


def _ensure_safe_command(command: str) -> None:
    lowered = command.lower()
    for fragment in BLOCKED_COMMAND_FRAGMENTS:
        if fragment in lowered:
            raise ValueError(f"unsafe command blocked by policy: {fragment.strip()}")


def _run_shell_command(command: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        check=False,
        capture_output=True,
        text=True,
    )


def _write_command_evidence(
    evidence_dir: Path,
    label: str,
    command: str,
    cwd: Path,
    result: subprocess.CompletedProcess[str],
) -> None:
    started_at = utc_now()
    ended_at = utc_now()
    stdout_path = evidence_dir / f"{label}-stdout.txt"
    stderr_path = evidence_dir / f"{label}-stderr.txt"
    stdout_path.write_text(result.stdout, encoding="utf-8")
    stderr_path.write_text(result.stderr, encoding="utf-8")
    with (evidence_dir / "commands.jsonl").open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                {
                    "label": label,
                    "command": command,
                    "cwd": str(cwd),
                    "exit_code": result.returncode,
                    "stdout_path": str(stdout_path),
                    "stderr_path": str(stderr_path),
                    "started_at": started_at,
                    "ended_at": ended_at,
                },
                sort_keys=True,
            )
            + "\n"
        )
    if label == "tests":
        (evidence_dir / "tests.txt").write_text(
            "\n".join(
                [
                    f"command: {command}",
                    f"exit_code: {result.returncode}",
                    "stdout:",
                    result.stdout,
                    "stderr:",
                    result.stderr,
                ]
            ),
            encoding="utf-8",
        )


def _run_git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result


def _git_stdout(cwd: Path, args: list[str]) -> str:
    return _run_git(cwd, args).stdout.strip()


def _changed_files_within_allowed_roots(
    changed_files: list[str],
    project_root: Path,
    allowed_write_roots: list[Path],
) -> bool:
    if not changed_files:
        return False
    allowed_prefixes = []
    for root in allowed_write_roots:
        try:
            allowed_prefixes.append(root.resolve().relative_to(project_root.resolve()))
        except ValueError:
            return False
    for changed_file in changed_files:
        changed_path = Path(changed_file)
        if changed_path.is_absolute() or ".." in changed_path.parts:
            return False
        if Path(".") in allowed_prefixes:
            continue
        if not any(
            changed_path == prefix or prefix in changed_path.parents
            for prefix in allowed_prefixes
        ):
            return False
    return True
