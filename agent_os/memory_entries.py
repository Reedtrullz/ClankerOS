from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agent_os.ids import new_id
from agent_os.storage import MemoryEntry, Storage


class MemoryEntryError(ValueError):
    pass


VALID_SCOPES = {"project", "user", "global"}
VALID_STATUSES = {"proposed", "active", "archived"}


def propose_memory_entry(
    root: Path,
    storage: Storage,
    *,
    project_id: str,
    key: str,
    value: str,
    scope: str = "project",
    source_type: str = "manual",
    source_id: str = "manual",
    confidence: float = 0.5,
    created_by_profile: str = "operator",
    extra_artifact_fields: dict[str, Any] | None = None,
) -> tuple[MemoryEntry, Path, bool]:
    _validate_memory_input(scope=scope, key=key, value=value, confidence=confidence)
    existing = storage.find_memory_entry(
        project_id=project_id,
        scope=scope,
        key=key,
        source_type=source_type,
        source_id=source_id,
    )
    if existing is not None:
        return existing, Path(existing.artifact_path or _artifact_path(root, existing.id)), True

    entry_id = new_id("memory")
    artifact_path = _artifact_path(root, entry_id)
    created_at = _write_proposal_artifact(
        artifact_path,
        entry_id=entry_id,
        project_id=project_id,
        scope=scope,
        key=key,
        value=value,
        source_type=source_type,
        source_id=source_id,
        confidence=confidence,
        created_by_profile=created_by_profile,
        extra_artifact_fields=extra_artifact_fields,
    )
    entry = storage.record_memory_entry(
        memory_id=entry_id,
        project_id=project_id,
        scope=scope,
        key=key,
        value=value,
        source_type=source_type,
        source_id=source_id,
        confidence=confidence,
        status="proposed",
        created_by_profile=created_by_profile,
        artifact_path=str(artifact_path),
    )
    if entry.created_at != created_at:
        _refresh_proposal_artifact_timestamps(artifact_path, entry)
    return entry, artifact_path, False


def propose_memory_from_delegation(
    root: Path,
    storage: Storage,
    *,
    delegation_id: str,
    key: str,
    scope: str = "project",
    confidence: float = 0.7,
    created_by_profile: str | None = None,
) -> tuple[MemoryEntry, Path, bool]:
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        raise MemoryEntryError(f"delegation {delegation_id} not found")
    if delegation.status != "completed" or not delegation.result_summary:
        raise MemoryEntryError(
            f"delegation {delegation_id} does not have a completed result"
        )
    task = storage.get_task(delegation.parent_task_id)
    result_artifact_path = Path(delegation.result_artifact_path)
    if not result_artifact_path.exists():
        raise MemoryEntryError(
            f"delegation {delegation_id} result artifact is missing"
        )
    result_artifact = json.loads(result_artifact_path.read_text(encoding="utf-8"))
    return propose_memory_entry(
        root,
        storage,
        project_id=task.project_id,
        key=key,
        value=delegation.result_summary,
        scope=scope,
        source_type="subagent_delegation",
        source_id=delegation.id,
        confidence=confidence,
        created_by_profile=created_by_profile or delegation.assigned_profile,
        extra_artifact_fields={
            "source_result_artifact_path": str(result_artifact_path),
            "source_result_summary": delegation.result_summary,
            "source_expected_output_schema": delegation.expected_output_schema,
            "source_structured_output": result_artifact.get("structured_output", {}),
        },
    )


def approve_memory_entry(
    storage: Storage,
    memory_id: str,
    *,
    approved_by: str = "operator",
) -> MemoryEntry:
    entry = storage.get_memory_entry(memory_id)
    if entry is None:
        raise MemoryEntryError(f"memory entry {memory_id} not found")
    if entry.status == "active":
        return entry
    if entry.status == "archived":
        raise MemoryEntryError(f"memory entry {memory_id} is archived")
    try:
        return storage.update_memory_entry_status(
            memory_id,
            status="active",
            decided_by=approved_by,
        )
    except ValueError as error:
        raise MemoryEntryError(str(error)) from error


def archive_memory_entry(
    storage: Storage,
    memory_id: str,
    *,
    archived_by: str = "operator",
    reason: str = "",
) -> MemoryEntry:
    entry = storage.get_memory_entry(memory_id)
    if entry is None:
        raise MemoryEntryError(f"memory entry {memory_id} not found")
    if entry.status == "archived":
        return entry
    return storage.update_memory_entry_status(
        memory_id,
        status="archived",
        decided_by=archived_by,
        reason=reason,
    )


def render_memory_entry_line(entry: MemoryEntry) -> str:
    return (
        f"{entry.id}: status={entry.status} project={entry.project_id} "
        f"scope={entry.scope} key={entry.key} source={entry.source_type}:{entry.source_id} "
        f"confidence={entry.confidence:g} artifact={entry.artifact_path or 'none'} "
        f"value={entry.value}"
    )


def _validate_memory_input(
    *,
    scope: str,
    key: str,
    value: str,
    confidence: float,
) -> None:
    if scope not in VALID_SCOPES:
        raise MemoryEntryError(f"invalid memory scope {scope}")
    if not key.strip():
        raise MemoryEntryError("memory key is required")
    if not value.strip():
        raise MemoryEntryError("memory value is required")
    if confidence < 0 or confidence > 1:
        raise MemoryEntryError("memory confidence must be between 0 and 1")


def _artifact_path(root: Path, entry_id: str) -> Path:
    return root / ".clanker" / "memory" / f"{entry_id}.json"


def _write_proposal_artifact(
    artifact_path: Path,
    *,
    entry_id: str,
    project_id: str,
    scope: str,
    key: str,
    value: str,
    source_type: str,
    source_id: str,
    confidence: float,
    created_by_profile: str,
    extra_artifact_fields: dict[str, Any] | None,
) -> str:
    from agent_os.storage import utc_now

    created_at = utc_now()
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = artifact_path.with_name(f".{artifact_path.name}.tmp")
    artifact = {
        "id": entry_id,
        "project_id": project_id,
        "scope": scope,
        "key": key,
        "value": value,
        "source_type": source_type,
        "source_id": source_id,
        "confidence": confidence,
        "status": "proposed",
        "created_by_profile": created_by_profile,
        "created_at": created_at,
        "updated_at": created_at,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Memory was proposed, not activated silently.",
            "No external system was mutated.",
            "No model provider was called by this command.",
        ],
    }
    if extra_artifact_fields:
        artifact.update(extra_artifact_fields)
    temp_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temp_path.replace(artifact_path)
    return created_at


def _refresh_proposal_artifact_timestamps(
    artifact_path: Path,
    entry: MemoryEntry,
) -> None:
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact["created_at"] = entry.created_at
    artifact["updated_at"] = entry.updated_at
    artifact_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
