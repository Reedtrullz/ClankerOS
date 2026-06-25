from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.implementation_handoff import (
    IMPLEMENTATION_HANDOFF_KIND,
    summarize_implementation_handoff,
)
from agent_os.storage import RegisteredProject, Storage


class CoderPrepError(ValueError):
    pass


@dataclass(frozen=True)
class CoderPrepResult:
    prep_id: str
    delegation_id: str
    project_id: str
    artifact_path: Path
    markdown_path: Path
    source_handoff_md: str
    allowed_files: list[str]
    already_recorded: bool = False


def prepare_coder_from_handoff(
    root: Path,
    storage: Storage,
    delegation_id: str,
) -> CoderPrepResult:
    root = root.resolve()
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        raise CoderPrepError(f"delegation not found: {delegation_id}")
    summary = summarize_implementation_handoff(root, delegation)
    if not summary["readable"]:
        raise CoderPrepError("implementation handoff is not readable")
    if summary["kind"] != IMPLEMENTATION_HANDOFF_KIND:
        raise CoderPrepError(f"unsupported implementation handoff kind: {summary['kind']}")

    source_handoff_md = str(summary["markdown_path"])
    if source_handoff_md == "none":
        raise CoderPrepError("implementation handoff markdown is missing")
    source_handoff_md_path = _resolve(root, source_handoff_md)
    if not source_handoff_md_path.exists():
        raise CoderPrepError("implementation handoff markdown file is missing")

    project = storage.get_registered_project(str(summary["project_id"]))
    if project is None:
        raise CoderPrepError(f"project is not registered: {summary['project_id']}")

    handoff_markdown = source_handoff_md_path.read_text(encoding="utf-8")
    handoff_sha = hashlib.sha256(handoff_markdown.encode("utf-8")).hexdigest()
    allowed_files = _bounded_files(summary)
    if not allowed_files:
        raise CoderPrepError("implementation handoff has no bounded file list")

    prep_dir = _prep_dir(root, delegation_id, str(summary["run_id"]))
    artifact_path = prep_dir / "coder_prep.json"
    markdown_path = prep_dir / "coder_prep.md"
    if artifact_path.exists():
        existing = _read_existing(artifact_path)
        if existing.get("source", {}).get("handoff_sha256") == handoff_sha:
            return CoderPrepResult(
                prep_id=str(existing.get("prep_id", "coder_prep")),
                delegation_id=delegation_id,
                project_id=project.name,
                artifact_path=artifact_path,
                markdown_path=markdown_path,
                source_handoff_md=source_handoff_md,
                allowed_files=allowed_files,
                already_recorded=True,
            )

    payload = _payload(
        delegation_id=delegation_id,
        project=project,
        summary=summary,
        source_handoff_md=source_handoff_md,
        source_handoff_markdown=handoff_markdown,
        handoff_sha=handoff_sha,
        allowed_files=allowed_files,
        artifact_path=str(artifact_path.relative_to(root)),
        markdown_path=str(markdown_path.relative_to(root)),
    )
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return CoderPrepResult(
        prep_id=payload["prep_id"],
        delegation_id=delegation_id,
        project_id=project.name,
        artifact_path=artifact_path,
        markdown_path=markdown_path,
        source_handoff_md=source_handoff_md,
        allowed_files=allowed_files,
    )


def prepare_coder_from_handoff_markdown(
    root: Path,
    storage: Storage,
    handoff_md: str,
) -> CoderPrepResult:
    root = root.resolve()
    source_handoff_md_path = _resolve_handoff_markdown(root, handoff_md)
    handoff_json_path = source_handoff_md_path.with_name("implementation_handoff.json")
    handoff_payload = _read_existing(handoff_json_path)
    if not handoff_payload:
        raise CoderPrepError("implementation handoff json is not readable")
    if handoff_payload.get("kind") != IMPLEMENTATION_HANDOFF_KIND:
        raise CoderPrepError(
            f"unsupported implementation handoff kind: {handoff_payload.get('kind', 'unknown')}"
        )
    delegation_id = str(handoff_payload.get("delegation_id") or "").strip()
    if not delegation_id:
        raise CoderPrepError("implementation handoff is missing delegation_id")

    result = prepare_coder_from_handoff(root, storage, delegation_id)
    requested = str(source_handoff_md_path.relative_to(root))
    if result.source_handoff_md != requested:
        raise CoderPrepError(
            "requested implementation handoff markdown is not the current delegation handoff"
        )
    return result


def render_coder_prep_cli_lines(root: Path, result: CoderPrepResult) -> list[str]:
    prefix = "already_recorded " if result.already_recorded else ""
    return [
        f"coder_prep: {prefix}{result.prep_id}",
        f"delegation_id: {result.delegation_id}",
        f"project_id: {result.project_id}",
        f"source_handoff_md: {result.source_handoff_md}",
        "source_handoff_markdown_consumed: true",
        f"artifact: {result.artifact_path.relative_to(root.resolve())}",
        f"markdown: {result.markdown_path.relative_to(root.resolve())}",
        f"allowed_files: {','.join(result.allowed_files)}",
        "run_plan: operator_review_required",
        f"coder_worktree_plan_command: python3 -m agent_os.cli coder-worktree-plan {result.delegation_id}",
        "task_rows_created: 0",
        "runs_created: 0",
        "routing_decisions_created: 0",
        "worktrees_created: 0",
        "effects_created: 0",
        "approval_requests_created: 0",
        "source_edits: 0",
        "commands_rerun: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def render_coder_prep_dashboard_lines(root: Path) -> list[str]:
    lines: list[str] = []
    for packet in list_coder_prep_packets(root)[-10:]:
        bounded_task = packet.get("bounded_task", {})
        safety = packet.get("safety", {})
        source = packet.get("source", {})
        lines.append(
            f"- {packet.get('prep_id', 'unknown')}: "
            f"project={packet.get('project', {}).get('id', 'unknown')} "
            f"delegation={source.get('delegation_id', 'unknown')} "
            f"source_handoff_md={source.get('handoff_md', 'none')} "
            f"allowed_files={','.join(bounded_task.get('allowed_files', [])[:5]) or 'none'} "
            f"run_plan={packet.get('run_plan', {}).get('next_recommended_action', 'unknown')} "
            "coder_worktree_plan_command=python3 -m agent_os.cli coder-worktree-plan "
            f"{source.get('delegation_id', 'unknown')} "
            f"task_rows_created={safety.get('task_rows_created', 'unknown')} "
            f"source_edits={safety.get('source_edits_taken', 'unknown')} "
            f"commands_rerun={safety.get('commands_rerun', 'unknown')} "
            f"artifact={packet.get('_path', 'unknown')}"
        )
    return lines


def render_coder_prep_review_lines(root: Path, delegation_id: str, run_id: str) -> list[str]:
    prep_path = (
        root.resolve()
        / ".clanker"
        / "delegations"
        / delegation_id
        / "runs"
        / run_id
        / "coder_prep"
        / "coder_prep.json"
    )
    if not prep_path.exists():
        return []
    packet = _read_existing(prep_path)
    if not packet:
        return [f"- delegation={delegation_id} coder_prep_readable: false"]
    bounded_task = packet.get("bounded_task", {})
    safety = packet.get("safety", {})
    return [
        f"- delegation={delegation_id} coder_prep={prep_path.relative_to(root.resolve())}",
        f"  - kind: {packet.get('kind', 'unknown')}",
        f"  - source_handoff_md: {packet.get('source', {}).get('handoff_md', 'none')}",
        "  - allowed_files: "
        f"{','.join(bounded_task.get('allowed_files', [])[:5]) or 'none'}",
        f"  - run_plan: {packet.get('run_plan', {}).get('next_recommended_action', 'unknown')}",
        "  - coder_worktree_plan_command: "
        f"python3 -m agent_os.cli coder-worktree-plan {delegation_id}",
        f"  - task_rows_created: {safety.get('task_rows_created', 'unknown')}",
        f"  - source_edits: {safety.get('source_edits_taken', 'unknown')}",
        f"  - commands_rerun: {safety.get('commands_rerun', 'unknown')}",
    ]


def list_coder_prep_packets(root: Path) -> list[dict[str, Any]]:
    root = root.resolve()
    packets: list[dict[str, Any]] = []
    pattern = ".clanker/delegations/*/runs/*/coder_prep/coder_prep.json"
    for path in sorted(root.glob(pattern)):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict):
            payload["_path"] = str(path.relative_to(root))
            packets.append(payload)
    return packets


def _payload(
    *,
    delegation_id: str,
    project: RegisteredProject,
    summary: dict[str, Any],
    source_handoff_md: str,
    source_handoff_markdown: str,
    handoff_sha: str,
    allowed_files: list[str],
    artifact_path: str,
    markdown_path: str,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "coder_prep_plan",
        "prep_id": "coder_prep",
        "source": {
            "delegation_id": delegation_id,
            "handoff_json": summary["handoff_path"],
            "handoff_md": source_handoff_md,
            "handoff_schema_version": summary["schema_version"],
            "handoff_kind": summary["kind"],
            "handoff_sha256": handoff_sha,
            "parent_task_id": summary.get("parent_task_id", "unknown"),
            "run_id": summary["run_id"],
        },
        "project": {
            "id": project.name,
            "root_path": project.root_path,
            "default_test_command": project.default_test_command,
            "allowed_write_roots": project.allowed_write_roots,
        },
        "bounded_task": {
            "title": f"Bounded implementation from handoff {delegation_id}",
            "objective": summary.get("result_summary", "Implement handoff follow-up."),
            "allowed_files": allowed_files,
            "candidate_test_files": [
                path for path in allowed_files if path.startswith("test") or "/test" in path
            ],
            "acceptance_criteria": [
                "Implementation remains inside the bounded file set.",
                "Verification command is selected before execution.",
                "Non-claims are refreshed before commit, push, or deploy.",
            ],
            "risks": [
                "Handoff output is advisory and requires operator review.",
                "Coder prep does not prove implementation correctness.",
            ],
            "forbidden_actions": [
                "edit_source_now",
                "dispatch",
                "commit",
                "push",
                "deploy",
                "provider_call",
                "network",
            ],
        },
        "run_plan": {
            "status": "operator_review_required",
            "execution_mode": "future_explicit_worktree_or_task_run",
            "commands_to_run_now": [],
            "suggested_verification_commands": [project.default_test_command],
            "next_recommended_action": "operator_review",
            "dispatch_ready": False,
        },
        "artifacts": {
            "json": artifact_path,
            "markdown": markdown_path,
        },
        "source_handoff_markdown_consumed": True,
        "source_handoff_markdown_excerpt": source_handoff_markdown[:2000],
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
            "Coder prep does not edit source files.",
            "Coder prep does not create task, run, routing, approval, effect, or worktree rows.",
            "Coder prep does not commit, push, deploy, or call model providers.",
        ],
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    source = payload["source"]
    bounded_task = payload["bounded_task"]
    safety = payload["safety"]
    lines = [
        "# Coder Prep Plan",
        "",
        f"- prep_id: {payload['prep_id']}",
        f"- delegation_id: {source['delegation_id']}",
        f"- source_handoff_md: {source['handoff_md']}",
        f"- source_handoff_sha256: {source['handoff_sha256']}",
        f"- project_id: {payload['project']['id']}",
        "",
        "## Bounded Task",
        "",
        f"- title: {bounded_task['title']}",
        f"- objective: {bounded_task['objective']}",
        "",
        "## Allowed Files",
        "",
        *[f"- {path}" for path in bounded_task["allowed_files"]],
        "",
        "## Run Plan",
        "",
        f"- execution_mode: {payload['run_plan']['execution_mode']}",
        "- commands_to_run_now: none",
        f"- next_recommended_action: {payload['run_plan']['next_recommended_action']}",
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


def _bounded_files(summary: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for key in ("scout_relevant_files", "scout_files", "top_ranked_files", "test_hints"):
        for value in summary.get(key, []):
            text = str(value).strip()
            if text and text != "none" and text not in files:
                files.append(text)
    return files[:10]


def _prep_dir(root: Path, delegation_id: str, run_id: str) -> Path:
    return root / ".clanker" / "delegations" / delegation_id / "runs" / run_id / "coder_prep"


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


def _resolve_handoff_markdown(root: Path, path: str) -> Path:
    raw = str(path).strip()
    if not raw:
        raise CoderPrepError("implementation handoff markdown path is required")
    parsed = Path(raw)
    if parsed.is_absolute():
        raise CoderPrepError("implementation handoff markdown path must be relative to repo root")
    if ".." in parsed.parts:
        raise CoderPrepError("implementation handoff markdown path must not contain parent traversal")
    resolved = (root / parsed).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise CoderPrepError(
            "implementation handoff markdown path resolves outside repo root"
        ) from error
    if resolved.name != "implementation_handoff.md":
        raise CoderPrepError("expected an implementation_handoff.md artifact")
    if not resolved.exists():
        raise CoderPrepError("implementation handoff markdown file is missing")
    return resolved
