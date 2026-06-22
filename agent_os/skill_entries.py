from __future__ import annotations

import hashlib
import re
from pathlib import Path

from agent_os.ids import new_id
from agent_os.storage import SkillRecord, SkillVersion, Storage


class SkillEntryError(ValueError):
    pass


VALID_SKILL_STATUSES = {"proposed", "active", "archived"}
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*[a-z0-9]$")


def propose_skill(
    root: Path,
    storage: Storage,
    *,
    project_id: str,
    name: str,
    description: str,
    source_run_id: str,
    source_task_id: str | None = None,
    created_by_profile: str = "operator",
) -> tuple[SkillRecord, SkillVersion, Path, bool]:
    _validate_skill_input(name=name, description=description)
    if not storage.run_exists(source_run_id):
        raise SkillEntryError(f"run {source_run_id} not found")
    existing = storage.find_skill(
        project_id=project_id,
        name=name,
        source_run_id=source_run_id,
        source_task_id=source_task_id,
    )
    if existing is not None:
        versions = storage.list_skill_versions(existing.id)
        if not versions:
            raise SkillEntryError(f"skill {existing.id} has no versions")
        return existing, versions[0], Path(existing.path), True

    skill_id = new_id("skill")
    skill_path = _skill_path(root, name)
    content = _render_skill_markdown(
        name=name,
        description=description,
        source_run_id=source_run_id,
        source_task_id=source_task_id,
        created_by_profile=created_by_profile,
    )
    _write_skill_file(skill_path, content)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    skill = storage.record_skill(
        skill_id=skill_id,
        project_id=project_id,
        name=name,
        description=description,
        path=str(skill_path),
        status="proposed",
        created_by_profile=created_by_profile,
        source_run_id=source_run_id,
        source_task_id=source_task_id,
        verification_status="pending_operator_approval",
    )
    version = storage.record_skill_version(
        skill_id=skill.id,
        version=1,
        content_hash=content_hash,
        path=str(skill_path),
        change_summary=f"Initial proposal from run {source_run_id}.",
        verification_status="pending_operator_approval",
    )
    return skill, version, skill_path, False


def approve_skill(
    storage: Storage,
    skill_id: str,
    *,
    approved_by: str = "operator",
) -> SkillRecord:
    skill = storage.get_skill(skill_id)
    if skill is None:
        raise SkillEntryError(f"skill {skill_id} not found")
    if skill.status == "active":
        return skill
    if skill.status == "archived":
        raise SkillEntryError(f"skill {skill_id} is archived")
    try:
        return storage.update_skill_status(
            skill_id,
            status="active",
            decided_by=approved_by,
        )
    except ValueError as error:
        raise SkillEntryError(str(error)) from error


def archive_skill(
    storage: Storage,
    skill_id: str,
    *,
    archived_by: str = "operator",
    reason: str = "",
) -> SkillRecord:
    skill = storage.get_skill(skill_id)
    if skill is None:
        raise SkillEntryError(f"skill {skill_id} not found")
    if skill.status == "archived":
        return skill
    return storage.update_skill_status(
        skill_id,
        status="archived",
        decided_by=archived_by,
        reason=reason,
    )


def render_skill_line(skill: SkillRecord) -> str:
    return (
        f"{skill.id}: status={skill.status} project={skill.project_id or 'none'} "
        f"name={skill.name} source_run={skill.source_run_id or 'none'} "
        f"verification={skill.verification_status} path={skill.path} "
        f"description={skill.description}"
    )


def _validate_skill_input(*, name: str, description: str) -> None:
    if not SKILL_NAME_RE.match(name):
        raise SkillEntryError(
            "skill name must use lowercase letters, numbers, hyphens, or underscores"
        )
    if not description.strip():
        raise SkillEntryError("skill description is required")


def _skill_path(root: Path, name: str) -> Path:
    return root / ".clanker" / "skills" / name / "SKILL.md"


def _write_skill_file(skill_path: Path, content: str) -> None:
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = skill_path.with_name(".SKILL.md.tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(skill_path)


def _render_skill_markdown(
    *,
    name: str,
    description: str,
    source_run_id: str,
    source_task_id: str | None,
    created_by_profile: str,
) -> str:
    source_task = source_task_id or "none"
    return f"""---
name: {name}
description: "{description}"
status: proposed
---

# {name}

## Purpose

{description}

## When To Use

Use this skill when repeating the procedure captured from source run
`{source_run_id}` would help future ClankerOS work.

## When Not To Use

Do not use this skill for unrelated projects, destructive actions, external
side effects, or work that lacks fresh verification evidence.

## Procedure

1. Read the current project state and the relevant source files.
2. State the intended local change and its approval boundary.
3. Make the smallest scoped change that satisfies the task.
4. Run the verification commands named by the project.
5. Record evidence, non-claims, and any follow-up action.

## Required Inputs

- project id
- current objective or task
- source files or run evidence
- verification command

## Expected Outputs

- scoped local change or proposal
- verification evidence
- explicit non-claims
- next recommended action

## Verification Steps

- Run the focused regression for the changed behavior.
- Run the project default verification command.
- Confirm generated evidence files exist before approving the skill.

## Common Failure Modes

- Treating a proposed skill as active before operator approval.
- Reusing stale run evidence without a fresh check.
- Expanding scope beyond the current project task.

## Proposal Metadata

- source_run_id: {source_run_id}
- source_task_id: {source_task}
- created_by_profile: {created_by_profile}
- network_actions_taken: 0
- external_mutations_taken: 0
- activation_status: proposed_until_approved
"""
