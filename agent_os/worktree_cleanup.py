from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import Effect, Storage, WorktreeCleanupRecord, WorktreeRecord, utc_now


TERMINAL_CLEANUP_STATUSES = {"committed", "blocked", "superseded"}


@dataclass(frozen=True)
class WorktreeCleanupResult:
    status: str
    dry_run: bool
    eligible_count: int
    removed_count: int
    blocked_count: int
    already_removed_count: int
    skipped_count: int
    records: list[WorktreeCleanupRecord]


def cleanup_worktrees(
    root: Path,
    *,
    confirm: bool,
    decided_by: str,
    reason: str,
) -> WorktreeCleanupResult:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    candidates = _cleanup_candidates(storage)

    if not confirm:
        return WorktreeCleanupResult(
            status="dry_run",
            dry_run=True,
            eligible_count=len(candidates),
            removed_count=0,
            blocked_count=0,
            already_removed_count=0,
            skipped_count=0,
            records=[],
        )

    removed_count = 0
    blocked_count = 0
    already_removed_count = 0
    skipped_count = 0
    records: list[WorktreeCleanupRecord] = []

    for worktree, effect in candidates:
        existing_removed = storage.get_removed_worktree_cleanup_for_effect(effect.id)
        worktree_path = Path(worktree.worktree_path)
        if existing_removed is not None or not worktree_path.exists():
            already_removed_count += 1
            if existing_removed is not None:
                records.append(existing_removed)
            continue

        project = storage.get_registered_project(effect.project_id)
        if project is None:
            records.append(
                _record_blocked_cleanup(
                    storage,
                    worktree,
                    effect,
                    decided_by=decided_by,
                    decision_note=reason,
                    cleanup_reason=effect.status,
                    reason="missing_project",
                    detail=f"registered project not found: {effect.project_id}",
                )
            )
            blocked_count += 1
            continue

        status_text = _git_stdout(
            worktree_path,
            ["status", "--porcelain", "--untracked-files=all"],
        )
        if status_text:
            records.append(
                _record_blocked_cleanup(
                    storage,
                    worktree,
                    effect,
                    decided_by=decided_by,
                    decision_note=reason,
                    cleanup_reason=effect.status,
                    reason="dirty_worktree",
                    detail=status_text,
                )
            )
            blocked_count += 1
            continue

        evidence_path = _cleanup_evidence_path(effect)
        result_json = {
            "status": "removed",
            "cleanup_reason": effect.status,
            "decision_note": reason,
            "decided_by": decided_by,
            "effect_id": effect.id,
            "worktree_id": worktree.id,
            "worktree_path": str(worktree_path),
            "branch_name": worktree.branch_name,
            "worktree_removed": True,
            "removed_at": utc_now(),
        }
        _write_json(evidence_path, result_json)
        _run_git(Path(project.root_path), ["worktree", "remove", str(worktree_path)])
        records.append(
            storage.record_worktree_cleanup(
                worktree_id=worktree.id,
                effect_id=effect.id,
                project_id=effect.project_id,
                run_id=effect.run_id,
                task_id=effect.task_id,
                worktree_path=str(worktree_path),
                branch_name=worktree.branch_name,
                cleanup_reason=effect.status,
                status="removed",
                decided_by=decided_by,
                decision_note=reason,
                evidence_path=str(evidence_path),
                result_json=result_json,
            )
        )
        removed_count += 1

    if blocked_count:
        status = "blocked"
    elif removed_count or already_removed_count:
        status = "applied"
    else:
        status = "noop"

    return WorktreeCleanupResult(
        status=status,
        dry_run=False,
        eligible_count=len(candidates),
        removed_count=removed_count,
        blocked_count=blocked_count,
        already_removed_count=already_removed_count,
        skipped_count=skipped_count,
        records=records,
    )


def _cleanup_candidates(storage: Storage) -> list[tuple[WorktreeRecord, Effect]]:
    worktrees = storage.list_recent_worktree_records(limit=10000)
    effects = storage.list_recent_effects(limit=10000)
    effects_by_task = {
        (effect.run_id, effect.task_id): effect
        for effect in effects
        if effect.effect_type == "local_git_commit"
        and effect.status in TERMINAL_CLEANUP_STATUSES
    }
    candidates = []
    for worktree in worktrees:
        effect = effects_by_task.get((worktree.run_id, worktree.task_id))
        if effect is not None:
            candidates.append((worktree, effect))
    return candidates


def _record_blocked_cleanup(
    storage: Storage,
    worktree: WorktreeRecord,
    effect: Effect,
    *,
    decided_by: str,
    decision_note: str,
    cleanup_reason: str,
    reason: str,
    detail: str,
) -> WorktreeCleanupRecord:
    evidence_path = _cleanup_evidence_path(effect)
    result_json = {
        "status": "blocked",
        "cleanup_reason": cleanup_reason,
        "reason": reason,
        "detail": detail,
        "decision_note": decision_note,
        "decided_by": decided_by,
        "effect_id": effect.id,
        "worktree_id": worktree.id,
        "worktree_path": worktree.worktree_path,
        "branch_name": worktree.branch_name,
        "worktree_removed": False,
        "checked_at": utc_now(),
    }
    _write_json(evidence_path, result_json)
    return storage.record_worktree_cleanup(
        worktree_id=worktree.id,
        effect_id=effect.id,
        project_id=effect.project_id,
        run_id=effect.run_id,
        task_id=effect.task_id,
        worktree_path=worktree.worktree_path,
        branch_name=worktree.branch_name,
        cleanup_reason=cleanup_reason,
        status="blocked",
        decided_by=decided_by,
        decision_note=decision_note,
        evidence_path=str(evidence_path),
        result_json=result_json,
    )


def _cleanup_evidence_path(effect: Effect) -> Path:
    evidence_dir = Path(effect.evidence_path).parent
    evidence_dir.mkdir(parents=True, exist_ok=True)
    return evidence_dir / f"worktree-cleanup-{effect.id}.json"


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
