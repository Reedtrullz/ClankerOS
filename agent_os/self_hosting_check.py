from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.storage import utc_now


SELF_HOSTING_CHECK_COMMAND = "python3 -m agent_os.cli self-hosting-check"


@dataclass(frozen=True)
class SelfHostingCheckResult:
    status: str
    report_path: Path
    json_path: Path
    latest_path: Path
    payload: dict[str, Any]


def run_next_day_self_hosting_check(
    root: Path,
    *,
    remote: str = "origin",
    branch: str = "main",
    fetch_mode: str = "update",
) -> SelfHostingCheckResult:
    root = root.resolve()
    now = utc_now()
    fetch_check = _run_fetch_check(root, remote=remote, branch=branch, mode=fetch_mode)
    goal_context = _goal_context(root)
    resume_check = _saved_resume_check(root, goal_context)
    next_action_check = _browser_next_action_check(root, goal_context)
    main_proof_check = _current_main_proof_check(root, goal_context, remote=remote, branch=branch)

    checks = {
        "local_fetch": fetch_check,
        "saved_resume": resume_check,
        "current_main_proof": main_proof_check,
        "browser_next_action": next_action_check,
    }
    attention = [name for name, check in checks.items() if check["status"] != "ready"]
    status = "ready" if not attention else "attention_needed"

    artifact_dir = root / ".clanker" / "self-hosting-checks"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^0-9A-Za-z]+", "", now)[:24] or "now"
    json_path = artifact_dir / f"self-hosting-check-{slug}.json"
    latest_path = artifact_dir / "latest.json"
    report_path = root / "docs" / "self-hosting-check.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    payload: dict[str, Any] = {
        "kind": "next_day_self_hosting_check",
        "schema_version": 1,
        "status": status,
        "created_at": now,
        "command": SELF_HOSTING_CHECK_COMMAND,
        "remote": remote,
        "branch": branch,
        "fetch_mode": fetch_mode,
        "checks": checks,
        "attention_checks": attention,
        "artifacts": {
            "json": _relative(root, json_path),
            "latest_json": _relative(root, latest_path),
            "report": _relative(root, report_path),
        },
        "safety": {
            "provider_calls_taken": 0,
            "network_actions_taken": fetch_check["network_actions_taken"],
            "external_mutations_taken": 0,
            "browser_write_on_get": False,
            "browser_network_actions_taken": 0,
            "push_created": False,
            "pr_created": False,
            "deploy_created": False,
        },
        "non_claims": [
            "The browser app reads this report only; it does not run git fetch on page load.",
            "The command does not push, create pull requests, deploy, or call model providers.",
            "CI proof is based on locally recorded operator-supplied evidence.",
        ],
    }

    json_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    json_path.write_text(json_text, encoding="utf-8")
    latest_path.write_text(json_text, encoding="utf-8")
    report_path.write_text(_render_markdown(payload), encoding="utf-8")
    return SelfHostingCheckResult(
        status=status,
        report_path=report_path,
        json_path=json_path,
        latest_path=latest_path,
        payload=payload,
    )


def load_latest_self_hosting_check(root: Path) -> dict[str, Any] | None:
    path = root.resolve() / ".clanker" / "self-hosting-checks" / "latest.json"
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def render_self_hosting_check_cli_lines(result: SelfHostingCheckResult) -> list[str]:
    payload = result.payload
    safety = payload["safety"]
    lines = [
        f"self_hosting_check: {result.status}",
        f"report: {payload['artifacts']['report']}",
        f"evidence: {payload['artifacts']['latest_json']}",
    ]
    for name, check in payload["checks"].items():
        lines.append(f"{name}: {check['status']}")
        lines.append(f"{name}_reason: {check['reason']}")
    lines.extend(
        [
            f"attention_checks: {','.join(payload['attention_checks']) or 'none'}",
            f"network_actions_taken: {safety['network_actions_taken']}",
            f"external_mutations_taken: {safety['external_mutations_taken']}",
            f"provider_calls_taken: {safety['provider_calls_taken']}",
            f"browser_write_on_get: {str(safety['browser_write_on_get']).lower()}",
        ]
    )
    return lines


def self_hosting_check_command_template(root: Path) -> str:
    return SELF_HOSTING_CHECK_COMMAND


def _run_fetch_check(
    root: Path,
    *,
    remote: str,
    branch: str,
    mode: str,
) -> dict[str, Any]:
    if mode not in {"update", "dry-run", "none"}:
        return {
            "status": "attention_needed",
            "reason": "unsupported_fetch_mode",
            "command": "",
            "returncode": 2,
            "stdout": "",
            "stderr": f"unsupported fetch mode: {mode}",
            "network_actions_taken": 0,
            "external_mutations_taken": 0,
            "local_git_refs_may_update": False,
        }
    if mode == "none":
        return {
            "status": "attention_needed",
            "reason": "fetch_not_run",
            "command": "skipped",
            "returncode": 0,
            "stdout": "",
            "stderr": "",
            "network_actions_taken": 0,
            "external_mutations_taken": 0,
            "local_git_refs_may_update": False,
        }

    args = ["git", "-C", str(root), "fetch", "--prune"]
    if mode == "dry-run":
        args.append("--dry-run")
    args.extend([remote, branch])
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "status": "attention_needed",
            "reason": "fetch_timed_out",
            "command": " ".join(args),
            "returncode": "timeout",
            "stdout": _trim(error.stdout if isinstance(error.stdout, str) else ""),
            "stderr": _trim(error.stderr if isinstance(error.stderr, str) else ""),
            "network_actions_taken": 1,
            "external_mutations_taken": 0,
            "local_git_refs_may_update": mode == "update",
        }
    return {
        "status": "ready" if result.returncode == 0 else "attention_needed",
        "reason": "fetch_completed" if result.returncode == 0 else "fetch_failed",
        "command": " ".join(args),
        "returncode": result.returncode,
        "stdout": _trim(result.stdout),
        "stderr": _trim(result.stderr),
        "network_actions_taken": 1,
        "external_mutations_taken": 0,
        "local_git_refs_may_update": mode == "update",
    }


def _goal_context(root: Path) -> dict[str, Any]:
    app = _local_app()
    storage = app._storage(root)
    workspace = app._load_workspace_state(root)
    saved_goal_id = str(workspace.get("open_goal") or "").strip()
    if saved_goal_id:
        state = app._goal_state(root, storage, saved_goal_id)
        if state.get("goal") is not None:
            goal = state["goal"]
            return {
                "source": "saved_workspace_goal",
                "goal_id": goal.id,
                "project_id": goal.project_id,
                "state": state,
                "workspace": workspace,
            }

    rows = app._goal_rows(storage, limit=100)
    active = [row for row in rows if app._goal_bucket(row) == "active"]
    paused = [row for row in rows if app._goal_bucket(row) == "paused"]
    completed = [row for row in rows if app._goal_bucket(row) == "completed"]
    lead, source = app._operator_lead_goal(root, storage, active, paused, completed)
    if lead is None:
        return {
            "source": source,
            "goal_id": "",
            "project_id": "",
            "state": None,
            "workspace": workspace,
        }
    goal_id = str(lead["id"])
    state = app._goal_state(root, storage, goal_id)
    goal = state.get("goal")
    return {
        "source": source,
        "goal_id": goal_id,
        "project_id": str(goal.project_id) if goal is not None else str(lead["project_id"]),
        "state": state,
        "workspace": workspace,
    }


def _saved_resume_check(root: Path, goal_context: dict[str, Any]) -> dict[str, Any]:
    app = _local_app()
    workspace = goal_context["workspace"]
    resume_surface = app._safe_local_return_path(workspace.get("resume_surface")) or ""
    open_goal = str(workspace.get("open_goal") or "").strip()
    open_project = str(workspace.get("open_project") or "").strip()
    goal_id = str(goal_context.get("goal_id") or "")
    goal_matches = bool(goal_id and open_goal == goal_id)
    ready = bool(resume_surface and open_goal and open_project and goal_matches)
    return {
        "status": "ready" if ready else "attention_needed",
        "reason": "saved_resume_matches_goal" if ready else "saved_resume_missing_or_stale",
        "open_project": open_project or "none",
        "open_goal": open_goal or "none",
        "goal_id": goal_id or "none",
        "goal_source": goal_context["source"],
        "resume_surface": resume_surface or "none",
        "safe_local_surface": bool(resume_surface),
    }


def _browser_next_action_check(root: Path, goal_context: dict[str, Any]) -> dict[str, Any]:
    app = _local_app()
    state = goal_context.get("state")
    if state is None or state.get("goal") is None:
        return {
            "status": "attention_needed",
            "reason": "no_goal_for_browser_next_action",
            "goal_id": "none",
            "action": "none",
            "surface": "none",
            "form_available": False,
        }
    action = app._goal_next_action(root, state)
    form_available = bool(app._goal_next_action_form(state, action))
    surface = app._goal_primary_action_href(
        state,
        action,
        form_available=form_available,
        absolute=True,
    )
    safe_surface = app._safe_local_return_path(surface)
    return {
        "status": "ready" if safe_surface else "attention_needed",
        "reason": "browser_next_action_ready" if safe_surface else "unsafe_or_missing_next_action_surface",
        "goal_id": str(state["goal"].id),
        "action": action.action,
        "why": action.reason,
        "surface": safe_surface or "none",
        "form_available": form_available,
        "source": goal_context["source"],
    }


def _current_main_proof_check(
    root: Path,
    goal_context: dict[str, Any],
    *,
    remote: str,
    branch: str,
) -> dict[str, Any]:
    app = _local_app()
    storage = app._storage(root)
    project_id = str(goal_context.get("project_id") or "clankeros")
    project = storage.get_registered_project(project_id)
    project_root = Path(project.root_path).resolve() if project else root
    repo = app._repo_state(project_root)
    full_head = app._git(project_root, ["rev-parse", "HEAD"]) or "unknown"
    short_head = repo["commit"]
    local_main = app._git(project_root, ["rev-parse", "--verify", f"refs/heads/{branch}"])
    remote_main = app._git(
        project_root,
        ["rev-parse", "--verify", f"refs/remotes/{remote}/{branch}"],
    )
    head_matches_local_main = _commits_match(full_head, local_main, short_head)
    head_matches_remote_main = _commits_match(full_head, remote_main, short_head)
    ci_state = (
        app._project_ci_evidence_command_state(root, project_id)
        if project_id
        else app._ci_evidence_command_state(root)
    )
    proof_ready = (
        ci_state["current_proof"] == "current_workflow_run_success"
        and (head_matches_remote_main or head_matches_local_main)
    )
    if proof_ready and head_matches_remote_main:
        reason = "current_checkout_matches_remote_main_with_full_ci_proof"
    elif proof_ready:
        reason = "current_checkout_matches_local_main_with_full_ci_proof"
    elif ci_state["current_proof"] != "current_workflow_run_success":
        reason = "current_full_ci_proof_missing_or_stale"
    else:
        reason = "current_checkout_does_not_match_main_ref"
    return {
        "status": "ready" if proof_ready else "attention_needed",
        "reason": reason,
        "project_id": project_id,
        "project_root": str(project_root),
        "branch": repo["branch"],
        "head_commit": full_head,
        "head_short_commit": short_head,
        "local_main_commit": local_main or "none",
        "remote_main_commit": remote_main or "none",
        "head_matches_local_main": head_matches_local_main,
        "head_matches_remote_main": head_matches_remote_main,
        "ci_current_proof": ci_state["current_proof"],
        "ci_command_status": ci_state["command_status"],
        "ci_current_match_source": ci_state.get("current_match_source", "unknown"),
        "ci_latest_source": ci_state["latest_source"],
        "ci_latest_status": ci_state["latest_status"],
        "ci_latest_scope": ci_state["latest_scope"],
        "ci_latest_run_id": ci_state["latest_external_run_id"],
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    checks = payload["checks"]
    rows = "\n".join(
        f"| {name} | {check['status']} | {check['reason']} |"
        for name, check in checks.items()
    )
    next_action = checks["browser_next_action"]
    resume = checks["saved_resume"]
    proof = checks["current_main_proof"]
    return (
        "# Next-Day Self-Hosting Check\n\n"
        f"- Status: `{payload['status']}`\n"
        f"- Recorded: `{payload['created_at']}`\n"
        f"- Command: `{payload['command']}`\n"
        f"- Latest JSON: `{payload['artifacts']['latest_json']}`\n\n"
        "| Check | Status | Reason |\n"
        "| --- | --- | --- |\n"
        f"{rows}\n\n"
        "## Resume\n\n"
        f"- Project: `{resume['open_project']}`\n"
        f"- Goal: `{resume['open_goal']}`\n"
        f"- Surface: `{resume['resume_surface']}`\n\n"
        "## Browser Next Action\n\n"
        f"- Action: `{next_action['action']}`\n"
        f"- Surface: `{next_action['surface']}`\n"
        f"- Form available: `{str(next_action['form_available']).lower()}`\n\n"
        "## Current Main Proof\n\n"
        f"- Checkout branch: `{proof['branch']}`\n"
        f"- Head commit: `{proof['head_commit']}`\n"
        f"- Remote main commit: `{proof['remote_main_commit']}`\n"
        f"- CI proof: `{proof['ci_current_proof']}`\n"
        f"- CI match source: `{proof['ci_current_match_source']}`\n\n"
        "## Safety\n\n"
        f"- Network actions taken: `{payload['safety']['network_actions_taken']}`\n"
        f"- External mutations taken: `{payload['safety']['external_mutations_taken']}`\n"
        f"- Browser write on GET: `{str(payload['safety']['browser_write_on_get']).lower()}`\n"
        f"- Browser network actions taken: `{payload['safety']['browser_network_actions_taken']}`\n"
    )


def _local_app():
    from agent_os import local_app

    return local_app


def _commits_match(head: str, other: str, short_head: str) -> bool:
    candidates = [value.strip() for value in (head, other, short_head) if value.strip()]
    if len(candidates) < 2 or not other:
        return False
    head_value = head.strip()
    other_value = other.strip()
    if head_value == "unknown" or other_value == "unknown":
        return False
    return (
        head_value == other_value
        or head_value.startswith(other_value)
        or other_value.startswith(head_value)
        or short_head.strip() == other_value
        or other_value.startswith(short_head.strip())
    )


def _trim(value: str, *, limit: int = 4000) -> str:
    text = value.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)
