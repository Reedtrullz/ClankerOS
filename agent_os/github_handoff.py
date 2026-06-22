from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import GitHubHandoffRecord, Storage, utc_now


@dataclass(frozen=True)
class GitHubHandoffResult:
    status: str
    handoff: GitHubHandoffRecord
    message: str


def create_github_handoff(
    root: Path,
    *,
    effect_id: str,
    remote: str = "origin",
    base: str = "main",
    title: str | None = None,
) -> GitHubHandoffResult:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    existing = storage.get_github_handoff_for_effect(effect_id)
    if existing is not None:
        return GitHubHandoffResult(
            status="already_ready",
            handoff=existing,
            message="handoff already recorded",
        )

    effect = storage.get_effect(effect_id)
    if effect.effect_type != "local_git_commit":
        raise ValueError(f"unsupported effect type: {effect.effect_type}")
    if effect.status != "committed":
        raise ValueError("local commit evidence required")

    commit_sha = effect.result_json.get("commit_sha")
    branch_name = effect.result_json.get("branch_name") or effect.proposed_payload.get(
        "branch_name"
    )
    if not commit_sha or not branch_name:
        raise ValueError("local commit evidence required")

    project = storage.get_registered_project(effect.project_id)
    if project is None:
        raise ValueError(f"registered project not found: {effect.project_id}")
    project_root = Path(project.root_path)
    _run_git(project_root, ["cat-file", "-e", f"{commit_sha}^{{commit}}"])
    remote_url = _git_stdout(project_root, ["remote", "get-url", remote])

    evidence_dir = Path(effect.evidence_path).parent
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"github-handoff-{effect.id}.json"
    body_path = evidence_dir / f"github-handoff-{effect.id}.md"
    pr_title = title or f"Apply approved ClankerOS effect {effect.id}"
    push_command = f"git push {remote} {branch_name}"
    draft_pr_command = " ".join(
        [
            "gh",
            "pr",
            "create",
            "--draft",
            "--head",
            shlex.quote(branch_name),
            "--base",
            shlex.quote(base),
            "--title",
            shlex.quote(pr_title),
            "--body-file",
            shlex.quote(str(body_path)),
        ]
    )

    result_json = {
        "status": "ready_for_operator",
        "effect_id": effect.id,
        "project_id": effect.project_id,
        "run_id": effect.run_id,
        "task_id": effect.task_id,
        "branch_name": branch_name,
        "commit_sha": commit_sha,
        "remote_name": remote,
        "remote_url": remote_url,
        "base_branch": base,
        "title": pr_title,
        "network_actions_taken": 0,
        "operator_commands": {
            "push": push_command,
            "draft_pr": draft_pr_command,
        },
        "created_at": utc_now(),
        "non_claims": [
            "Does not push to GitHub.",
            "Does not open a pull request.",
            "Does not run CI or deploy.",
        ],
    }
    evidence_path.write_text(
        json.dumps(result_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    body_path.write_text(
        "\n".join(
            [
                f"# {pr_title}",
                "",
                "## Local Evidence",
                "",
                f"- effect_id: {effect.id}",
                f"- run_id: {effect.run_id}",
                f"- task_id: {effect.task_id}",
                f"- branch: {branch_name}",
                f"- commit: {commit_sha}",
                f"- evidence: {effect.evidence_path}",
                "",
                "## Operator Checklist",
                "",
                "- Review local run evidence before pushing.",
                "- Push the branch only when the local commit is intended for GitHub.",
                "- Open the PR as a draft until remote CI evidence exists.",
                "",
                "## Non-Claims",
                "",
                "- This handoff did not push to GitHub.",
                "- This handoff did not open a pull request.",
                "- This handoff did not run CI or deploy.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    handoff = storage.record_github_handoff(
        effect_id=effect.id,
        project_id=effect.project_id,
        run_id=effect.run_id,
        task_id=effect.task_id,
        branch_name=branch_name,
        commit_sha=commit_sha,
        remote_name=remote,
        remote_url=remote_url,
        base_branch=base,
        status="ready_for_operator",
        push_command=push_command,
        draft_pr_command=draft_pr_command,
        evidence_path=str(evidence_path),
        result_json=result_json,
    )
    return GitHubHandoffResult(
        status="ready_for_operator",
        handoff=handoff,
        message="handoff ready for operator",
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
