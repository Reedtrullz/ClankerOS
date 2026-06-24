from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_os.storage import SubagentDelegation
from agent_os.subagent_delegation import load_delegation_result_metadata


IMPLEMENTATION_HANDOFF_KIND = "implementation_context_handoff"


def summarize_implementation_handoff(
    root: Path,
    delegation: SubagentDelegation,
) -> dict[str, Any]:
    metadata = load_delegation_result_metadata(delegation)
    handoff_path = metadata.get("implementation_handoff_json")
    markdown_path = metadata.get("implementation_handoff_md")
    summary: dict[str, Any] = {
        "delegation_id": delegation.id,
        "run_id": metadata.get("execution_run_id") or metadata.get("run_id") or "unknown",
        "project_id": metadata.get("target_project_id") or "unknown",
        "status": "missing",
        "readable": False,
        "handoff_path": handoff_path or "none",
        "markdown_path": markdown_path or "none",
        "schema_version": "unknown",
        "kind": "unknown",
        "kind_valid": False,
        "context_pack_json": metadata.get("context_pack_json") or "none",
        "context_pack_md": metadata.get("context_pack_md") or "none",
        "context_pack_ranked_file_count": metadata.get(
            "context_pack_ranked_file_count",
            "unknown",
        ),
        "context_pack_grep_hit_count": metadata.get(
            "context_pack_grep_hit_count",
            "unknown",
        ),
        "context_pack_returned_files_in_inventory": metadata.get(
            "context_pack_returned_files_in_inventory"
        ),
        "context_pack_returned_files_missing": _string_list(
            metadata.get("context_pack_returned_files_missing")
        ),
        "context_pack_top_ranked_files_referenced": _string_list(
            metadata.get("context_pack_top_ranked_files_referenced")
        ),
        "top_ranked_files": _string_list(metadata.get("context_pack_top_ranked_files")),
        "test_hints": [],
        "scout_files": [],
        "scout_relevant_files": [],
        "finding_count": 0,
        "result_summary": delegation.result_summary or "none",
        "snippets_embedded": False,
        "error": None,
    }
    if not handoff_path:
        return summary

    full_path = _resolve_path(root, handoff_path)
    if not full_path.exists():
        summary["error"] = "handoff_file_missing"
        return summary

    try:
        payload = json.loads(full_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        summary["status"] = "unreadable"
        summary["error"] = str(error)
        return summary
    if not isinstance(payload, dict):
        summary["status"] = "invalid"
        summary["error"] = "handoff_json_not_object"
        return summary

    context_pack = _dict_value(payload.get("context_pack"))
    validation = _dict_value(payload.get("validation"))
    scout_output = _dict_value(payload.get("scout_output"))
    project = _dict_value(payload.get("project"))
    summary.update(
        {
            "status": "readable",
            "readable": True,
            "schema_version": payload.get("schema_version", "unknown"),
            "kind": payload.get("kind", "unknown"),
            "kind_valid": payload.get("kind") == IMPLEMENTATION_HANDOFF_KIND,
            "run_id": payload.get("run_id") or summary["run_id"],
            "project_id": project.get("id") or summary["project_id"],
            "parent_task_id": payload.get("parent_task_id") or "unknown",
            "expected_output_schema": payload.get("expected_output_schema") or "unknown",
            "result_summary": payload.get("result_summary") or summary["result_summary"],
            "context_pack_json": context_pack.get("json_path")
            or summary["context_pack_json"],
            "context_pack_md": context_pack.get("markdown_path")
            or summary["context_pack_md"],
            "context_pack_ranked_file_count": context_pack.get(
                "ranked_file_count",
                summary["context_pack_ranked_file_count"],
            ),
            "context_pack_grep_hit_count": context_pack.get(
                "grep_hit_count",
                summary["context_pack_grep_hit_count"],
            ),
            "context_pack_returned_files_in_inventory": validation.get(
                "returned_files_in_inventory",
                summary["context_pack_returned_files_in_inventory"],
            ),
            "context_pack_returned_files_missing": _string_list(
                validation.get(
                    "returned_files_missing",
                    summary["context_pack_returned_files_missing"],
                )
            ),
            "context_pack_top_ranked_files_referenced": _string_list(
                validation.get(
                    "top_ranked_files_referenced",
                    summary["context_pack_top_ranked_files_referenced"],
                )
            ),
            "top_ranked_files": _string_list(
                context_pack.get("top_ranked_files", summary["top_ranked_files"])
            ),
            "test_hints": _string_list(context_pack.get("test_hints")),
            "scout_files": _string_list(scout_output.get("files")),
            "scout_relevant_files": _string_list(scout_output.get("relevant_files")),
            "finding_count": len(_string_list(scout_output.get("findings"))),
            "snippets_embedded": _has_key(payload, "snippets"),
        }
    )
    return summary


def render_implementation_handoff_cli_lines(summary: dict[str, Any]) -> list[str]:
    lines = [
        f"implementation_handoff: {summary['delegation_id']}",
        f"status: {summary['status']}",
        f"path: {summary['handoff_path']}",
        f"markdown_path: {summary['markdown_path']}",
        f"schema_version: {summary['schema_version']}",
        f"kind: {summary['kind']}",
        f"kind_valid: {_bool(summary.get('kind_valid'))}",
        f"run_id: {summary['run_id']}",
        f"project_id: {summary['project_id']}",
        f"parent_task_id: {summary.get('parent_task_id', 'unknown')}",
        f"context_pack: {summary['context_pack_json']}",
        f"context_pack_md: {summary['context_pack_md']}",
        "context_pack_ranked_file_count: "
        f"{summary['context_pack_ranked_file_count']}",
        f"context_pack_grep_hit_count: {summary['context_pack_grep_hit_count']}",
        "context_pack_returned_files_in_inventory: "
        f"{_bool(summary.get('context_pack_returned_files_in_inventory'))}",
        "context_pack_returned_files_missing: "
        f"{_joined(summary['context_pack_returned_files_missing'])}",
        "context_pack_top_ranked_files_referenced: "
        f"{_joined(summary['context_pack_top_ranked_files_referenced'])}",
        f"top_ranked_files: {_joined(summary['top_ranked_files'])}",
        f"test_hints: {_joined(summary['test_hints'])}",
        f"scout_files: {_joined(summary['scout_files'])}",
        f"scout_relevant_files: {_joined(summary['scout_relevant_files'])}",
        f"finding_count: {summary['finding_count']}",
        f"snippets_embedded: {_bool(summary.get('snippets_embedded'))}",
        f"result_summary: {summary['result_summary']}",
        "coder_prep_command: "
        f"python3 -m agent_os.cli coder-prep {summary['delegation_id']}",
        "next_recommended_action: implementation_review",
    ]
    if summary.get("error"):
        lines.append(f"error: {summary['error']}")
    return lines


def render_implementation_handoff_review_lines(
    root: Path,
    delegations: list[SubagentDelegation],
) -> list[str]:
    lines: list[str] = []
    for delegation in delegations:
        summary = summarize_implementation_handoff(root, delegation)
        if summary["handoff_path"] == "none":
            continue
        lines.append(
            f"- delegation={delegation.id} handoff={summary['handoff_path']}"
        )
        lines.append(f"  - handoff_readable: {_bool(summary['readable'])}")
        lines.append(f"  - schema_version: {summary['schema_version']}")
        lines.append(f"  - kind: {summary['kind']}")
        lines.append(f"  - kind_valid: {_bool(summary['kind_valid'])}")
        lines.append(f"  - run_id: {summary['run_id']}")
        lines.append(f"  - project_id: {summary['project_id']}")
        lines.append(f"  - context_pack: {summary['context_pack_json']}")
        lines.append(
            "  - returned_files_in_inventory: "
            f"{_bool(summary['context_pack_returned_files_in_inventory'])}"
        )
        lines.append(
            "  - returned_files_missing: "
            f"{_joined(summary['context_pack_returned_files_missing'])}"
        )
        lines.append(
            "  - top_ranked_files_referenced: "
            f"{_joined(summary['context_pack_top_ranked_files_referenced'])}"
        )
        lines.append(f"  - top_ranked_files: {_joined(summary['top_ranked_files'])}")
        lines.append(f"  - test_hints: {_joined(summary['test_hints'])}")
        lines.append(
            f"  - scout_relevant_files: {_joined(summary['scout_relevant_files'])}"
        )
        lines.append(f"  - snippets_embedded: {_bool(summary['snippets_embedded'])}")
        if summary.get("error"):
            lines.append(f"  - error: {summary['error']}")
    return lines


def render_implementation_handoff_dashboard_lines(
    root: Path,
    delegations: list[SubagentDelegation],
) -> list[str]:
    lines: list[str] = []
    for delegation in delegations:
        summary = summarize_implementation_handoff(root, delegation)
        if summary["handoff_path"] == "none":
            continue
        lines.append(
            f"- {delegation.id}: status={delegation.status} "
            f"handoff={summary['handoff_path']} "
            f"handoff_readable={_bool(summary['readable'])} "
            f"schema_version={summary['schema_version']} "
            f"kind={summary['kind']} kind_valid={_bool(summary['kind_valid'])} "
            f"run={summary['run_id']} project={summary['project_id']} "
            "coder_prep_command=python3 -m agent_os.cli coder-prep "
            f"{delegation.id} "
            f"context_pack={summary['context_pack_json']} "
            "returned_files_in_inventory="
            f"{_bool(summary['context_pack_returned_files_in_inventory'])} "
            "missing_files="
            f"{_joined(summary['context_pack_returned_files_missing'])} "
            "top_ranked_files="
            f"{_joined(summary['top_ranked_files'])} "
            "scout_relevant_files="
            f"{_joined(summary['scout_relevant_files'])} "
            f"snippets_embedded={_bool(summary['snippets_embedded'])}"
        )
    return lines


def _resolve_path(root: Path, path: str) -> Path:
    parsed = Path(path)
    if parsed.is_absolute():
        return parsed
    return root / parsed


def _dict_value(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_list(value: object, *, limit: int = 5) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value][:limit]
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item)][:limit]


def _joined(values: list[str]) -> str:
    return ",".join(values) if values else "none"


def _bool(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "unknown"


def _has_key(value: object, key: str) -> bool:
    if isinstance(value, dict):
        if key in value:
            return True
        return any(_has_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(_has_key(child, key) for child in value)
    return False
