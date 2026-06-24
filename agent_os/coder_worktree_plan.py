from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.storage import Storage


CODER_WORKTREE_PLAN_KIND = "coder_worktree_run_plan"


class CoderWorktreePlanError(ValueError):
    pass


@dataclass(frozen=True)
class CoderWorktreePlanResult:
    plan_id: str
    delegation_id: str
    project_id: str
    artifact_path: Path
    markdown_path: Path
    source_coder_prep_md: str
    allowed_files: list[str]
    already_recorded: bool = False


def prepare_worktree_plan_from_coder_prep(
    root: Path,
    storage: Storage,
    delegation_id: str,
) -> CoderWorktreePlanResult:
    root = root.resolve()
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        raise CoderWorktreePlanError(f"delegation not found: {delegation_id}")

    prep_path = _latest_coder_prep_path(root, delegation_id)
    if prep_path is None:
        raise CoderWorktreePlanError("coder prep is not readable")
    prep_payload = _read_existing(prep_path)
    if not prep_payload:
        raise CoderWorktreePlanError("coder prep is not readable")
    if prep_payload.get("kind") != "coder_prep_plan":
        raise CoderWorktreePlanError(f"unsupported coder prep kind: {prep_payload.get('kind')}")

    source_coder_prep_md = _source_markdown_path(prep_payload, prep_path, root)
    source_coder_prep_md_path = _resolve(root, source_coder_prep_md)
    if not source_coder_prep_md_path.exists():
        raise CoderWorktreePlanError("coder prep markdown file is missing")
    coder_prep_markdown = source_coder_prep_md_path.read_text(encoding="utf-8")
    coder_prep_sha = hashlib.sha256(coder_prep_markdown.encode("utf-8")).hexdigest()

    project = _dict_value(prep_payload.get("project"))
    project_id = str(project.get("id") or "unknown")
    if storage.get_registered_project(project_id) is None:
        raise CoderWorktreePlanError(f"project is not registered: {project_id}")

    bounded_task = _dict_value(prep_payload.get("bounded_task"))
    allowed_files = _string_list(bounded_task.get("allowed_files"), limit=25)
    if not allowed_files:
        raise CoderWorktreePlanError("coder prep has no bounded file list")

    artifact_path = prep_path.parent / "coder_worktree_plan.json"
    markdown_path = prep_path.parent / "coder_worktree_plan.md"
    if artifact_path.exists():
        existing = _read_existing(artifact_path)
        if existing.get("source", {}).get("coder_prep_md_sha256") == coder_prep_sha:
            return CoderWorktreePlanResult(
                plan_id=str(existing.get("plan_id", "coder_worktree_plan")),
                delegation_id=delegation_id,
                project_id=project_id,
                artifact_path=artifact_path,
                markdown_path=markdown_path,
                source_coder_prep_md=source_coder_prep_md,
                allowed_files=allowed_files,
                already_recorded=True,
            )

    payload = _payload(
        delegation_id=delegation_id,
        prep_payload=prep_payload,
        source_coder_prep_json=str(prep_path.relative_to(root)),
        source_coder_prep_md=source_coder_prep_md,
        source_coder_prep_markdown=coder_prep_markdown,
        coder_prep_sha=coder_prep_sha,
        allowed_files=allowed_files,
        artifact_path=str(artifact_path.relative_to(root)),
        markdown_path=str(markdown_path.relative_to(root)),
    )
    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return CoderWorktreePlanResult(
        plan_id=payload["plan_id"],
        delegation_id=delegation_id,
        project_id=project_id,
        artifact_path=artifact_path,
        markdown_path=markdown_path,
        source_coder_prep_md=source_coder_prep_md,
        allowed_files=allowed_files,
    )


def render_coder_worktree_plan_cli_lines(
    root: Path,
    result: CoderWorktreePlanResult,
) -> list[str]:
    prefix = "already_recorded " if result.already_recorded else ""
    return [
        f"coder_worktree_plan: {prefix}{result.plan_id}",
        f"delegation_id: {result.delegation_id}",
        f"project_id: {result.project_id}",
        f"source_coder_prep_md: {result.source_coder_prep_md}",
        "source_coder_prep_markdown_consumed: true",
        f"artifact: {result.artifact_path.relative_to(root.resolve())}",
        f"markdown: {result.markdown_path.relative_to(root.resolve())}",
        f"allowed_files: {','.join(result.allowed_files)}",
        "approval_gate: operator_approval_required",
        "dispatch_ready: false",
        "worktree_created: 0",
        "task_rows_created: 0",
        "runs_created: 0",
        "routing_decisions_created: 0",
        "worktrees_created: 0",
        "effects_created: 0",
        "approval_requests_created: 0",
        "source_edits: 0",
        "commands_rerun: 0",
        "provider_calls_taken_by_clankeros: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_worktree_plan_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for packet in list_coder_worktree_plan_packets(root)[-10:]:
        bounded_task = _dict_value(packet.get("bounded_coding_task"))
        safety = _dict_value(packet.get("safety"))
        source = _dict_value(packet.get("source"))
        gate = _dict_value(packet.get("approval_gate"))
        lines.append(
            f"- {packet.get('plan_id', 'unknown')}: "
            f"project={packet.get('project', {}).get('id', 'unknown')} "
            f"delegation={source.get('delegation_id', 'unknown')} "
            f"source_coder_prep_md={source.get('coder_prep_md', 'none')} "
            f"allowed_files={','.join(bounded_task.get('allowed_files', [])[:5]) or 'none'} "
            f"approval_gate={gate.get('status', 'unknown')} "
            f"dispatch_ready={_bool(packet.get('dispatch_ready'))} "
            f"worktrees_created={safety.get('worktrees_created', 'unknown')} "
            f"source_edits={safety.get('source_edits_taken', 'unknown')} "
            f"commands_rerun={safety.get('commands_rerun', 'unknown')} "
            f"artifact={packet.get('_path', 'unknown')}"
        )
    return lines


def render_coder_worktree_plan_review_lines(
    root: Path,
    delegation_id: str,
    run_id: str,
) -> list[str]:
    plan_path = (
        root.resolve()
        / ".clanker"
        / "delegations"
        / delegation_id
        / "runs"
        / run_id
        / "coder_prep"
        / "coder_worktree_plan.json"
    )
    if not plan_path.exists():
        return []
    packet = _read_existing(plan_path)
    if not packet:
        return [f"- delegation={delegation_id} coder_worktree_plan_readable: false"]
    bounded_task = _dict_value(packet.get("bounded_coding_task"))
    safety = _dict_value(packet.get("safety"))
    gate = _dict_value(packet.get("approval_gate"))
    return [
        f"- delegation={delegation_id} coder_worktree_plan={plan_path.relative_to(root.resolve())}",
        f"  - kind: {packet.get('kind', 'unknown')}",
        f"  - source_coder_prep_md: {packet.get('source', {}).get('coder_prep_md', 'none')}",
        "  - allowed_files: "
        f"{','.join(bounded_task.get('allowed_files', [])[:5]) or 'none'}",
        f"  - approval_gate: {gate.get('status', 'unknown')}",
        f"  - dispatch_ready: {_bool(packet.get('dispatch_ready'))}",
        f"  - worktrees_created: {safety.get('worktrees_created', 'unknown')}",
        f"  - source_edits: {safety.get('source_edits_taken', 'unknown')}",
        f"  - commands_rerun: {safety.get('commands_rerun', 'unknown')}",
    ]


def list_coder_worktree_plan_packets(root: Path) -> list[dict[str, Any]]:
    root = root.resolve()
    packets: list[dict[str, Any]] = []
    pattern = ".clanker/delegations/*/runs/*/coder_prep/coder_worktree_plan.json"
    for path in sorted(root.glob(pattern)):
        payload = _read_existing(path)
        if payload:
            payload["_path"] = str(path.relative_to(root))
            packets.append(payload)
    return packets


def _payload(
    *,
    delegation_id: str,
    prep_payload: dict[str, Any],
    source_coder_prep_json: str,
    source_coder_prep_md: str,
    source_coder_prep_markdown: str,
    coder_prep_sha: str,
    allowed_files: list[str],
    artifact_path: str,
    markdown_path: str,
) -> dict[str, Any]:
    source = _dict_value(prep_payload.get("source"))
    project = _dict_value(prep_payload.get("project"))
    bounded_task = _dict_value(prep_payload.get("bounded_task"))
    candidate_test_files = _string_list(bounded_task.get("candidate_test_files"), limit=10)
    default_test_command = str(project.get("default_test_command") or "none")
    suggested_commands = [default_test_command] if default_test_command != "none" else []
    project_id = str(project.get("id") or "unknown")
    branch_name = f"codex/coder-prep-{_slug(delegation_id)}"
    worktree_path = f".agent/worktrees/{project_id}/coder-prep-{_slug(delegation_id)}"
    objective = str(bounded_task.get("objective") or "Implement bounded coder-prep follow-up.")
    return {
        "schema_version": 1,
        "kind": CODER_WORKTREE_PLAN_KIND,
        "plan_id": "coder_worktree_plan",
        "source": {
            "delegation_id": delegation_id,
            "run_id": source.get("run_id", "unknown"),
            "coder_prep_json": source_coder_prep_json,
            "coder_prep_md": source_coder_prep_md,
            "coder_prep_schema_version": prep_payload.get("schema_version", "unknown"),
            "coder_prep_kind": prep_payload.get("kind", "unknown"),
            "coder_prep_md_sha256": coder_prep_sha,
            "handoff_md": source.get("handoff_md", "none"),
            "handoff_sha256": source.get("handoff_sha256", "unknown"),
            "parent_task_id": source.get("parent_task_id", "unknown"),
        },
        "project": {
            "id": project_id,
            "root_path": project.get("root_path", "unknown"),
            "default_test_command": default_test_command,
            "allowed_write_roots": _string_list(project.get("allowed_write_roots"), limit=10),
        },
        "bounded_coding_task": {
            "title": f"Approval-gated worktree plan from coder prep {delegation_id}",
            "objective": objective,
            "allowed_files": allowed_files,
            "candidate_test_files": candidate_test_files,
            "acceptance_criteria": [
                *(_string_list(bounded_task.get("acceptance_criteria"), limit=10)),
                "Operator approves this plan before any worktree is created.",
                "Future implementation writes remain within allowed_files.",
            ],
            "risks": [
                *(_string_list(bounded_task.get("risks"), limit=10)),
                "This plan is not proof that the future coding run will pass.",
            ],
            "forbidden_actions": [
                "create_worktree_now",
                "edit_source_now",
                "dispatch_now",
                "commit",
                "push",
                "deploy",
                "provider_call",
                "network",
            ],
        },
        "proposed_worktree": {
            "status": "not_created",
            "worktree_created": False,
            "branch_name_suggestion": branch_name,
            "path_suggestion": worktree_path,
            "base_ref": "operator_selected_current_head",
        },
        "future_run_plan": {
            "status": "operator_approval_required",
            "execution_mode": "future_explicit_worktree_run",
            "commands_to_run_now": [],
            "suggested_future_command": (
                "python3 -m agent_os.cli run-goal "
                f"{json.dumps(objective)} --project {project_id} "
                "--isolation worktree --command "
                f"{json.dumps('<operator-approved bounded command>')}"
            ),
            "suggested_verification_commands": suggested_commands,
            "next_recommended_action": "operator_review",
            "dispatch_ready": False,
        },
        "approval_gate": {
            "status": "operator_approval_required",
            "approval_required_before": [
                "create_worktree",
                "run_command",
                "edit_source",
                "commit",
                "push",
                "deploy",
            ],
            "approval_request_created": False,
        },
        "artifacts": {
            "json": artifact_path,
            "markdown": markdown_path,
        },
        "source_coder_prep_markdown_consumed": True,
        "source_coder_prep_markdown_excerpt": source_coder_prep_markdown[:2000],
        "dispatch_ready": False,
        "safety": {
            "source_edits_taken": 0,
            "task_rows_created": 0,
            "runs_created": 0,
            "routing_decisions_created": 0,
            "worktrees_created": 0,
            "effects_created": 0,
            "approval_requests_created": 0,
            "commands_rerun": 0,
            "provider_calls_taken_by_clankeros": 0,
            "network_actions_taken": 0,
            "external_mutations_taken": 0,
        },
        "non_claims": [
            "Coder worktree planning does not create a git worktree.",
            "Coder worktree planning does not create task, run, routing, approval, or effect rows.",
            "Coder worktree planning does not edit source files, run commands, commit, push, deploy, or call providers.",
        ],
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    source = payload["source"]
    bounded_task = payload["bounded_coding_task"]
    future_run_plan = payload["future_run_plan"]
    proposed_worktree = payload["proposed_worktree"]
    approval_gate = payload["approval_gate"]
    safety = payload["safety"]
    lines = [
        "# Coder Worktree Plan",
        "",
        f"- plan_id: {payload['plan_id']}",
        f"- delegation_id: {source['delegation_id']}",
        f"- source_coder_prep_md: {source['coder_prep_md']}",
        f"- source_coder_prep_sha256: {source['coder_prep_md_sha256']}",
        f"- project_id: {payload['project']['id']}",
        "",
        "## Bounded Coding Task",
        "",
        f"- title: {bounded_task['title']}",
        f"- objective: {bounded_task['objective']}",
        "",
        "## Allowed Files",
        "",
        *[f"- {path}" for path in bounded_task["allowed_files"]],
        "",
        "## Proposed Worktree",
        "",
        f"- status: {proposed_worktree['status']}",
        f"- branch_name_suggestion: {proposed_worktree['branch_name_suggestion']}",
        f"- path_suggestion: {proposed_worktree['path_suggestion']}",
        f"- base_ref: {proposed_worktree['base_ref']}",
        "",
        "## Approval Gate",
        "",
        f"- status: {approval_gate['status']}",
        "- approval_request_created: false",
        *[f"- required_before: {item}" for item in approval_gate["approval_required_before"]],
        "",
        "## Future Run Plan",
        "",
        f"- execution_mode: {future_run_plan['execution_mode']}",
        "- commands_to_run_now: none",
        f"- suggested_future_command: {future_run_plan['suggested_future_command']}",
        f"- next_recommended_action: {future_run_plan['next_recommended_action']}",
        "- dispatch_ready: false",
        "",
        "## Safety Counters",
        "",
        *[f"- {key}: {value}" for key, value in safety.items()],
        "",
        "## Non-Claims",
        "",
        *[f"- {claim}" for claim in payload["non_claims"]],
        "",
    ]
    return "\n".join(lines)


def _latest_coder_prep_path(root: Path, delegation_id: str) -> Path | None:
    pattern = root / ".clanker" / "delegations" / delegation_id / "runs" / "*" / "coder_prep" / "coder_prep.json"
    matches = sorted(root.glob(str(pattern.relative_to(root))))
    return matches[-1] if matches else None


def _source_markdown_path(payload: dict[str, Any], prep_path: Path, root: Path) -> str:
    artifacts = _dict_value(payload.get("artifacts"))
    markdown = artifacts.get("markdown")
    if isinstance(markdown, str) and markdown:
        return markdown
    return str((prep_path.parent / "coder_prep.md").relative_to(root))


def _read_existing(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve(root: Path, path: str) -> Path:
    parsed = Path(path)
    if parsed.is_absolute():
        return parsed
    return root / parsed


def _dict_value(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_list(value: object, *, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    values: list[str] = []
    for item in value:
        text = str(item).strip()
        if text and text not in values:
            values.append(text)
    return values[:limit]


def _slug(value: str) -> str:
    normalized = value.replace("subagent_delegation_", "")
    slug = "".join(char.lower() if char.isalnum() else "-" for char in normalized)
    slug = "-".join(part for part in slug.split("-") if part)
    return slug[:24] or "plan"


def _bool(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "unknown"
