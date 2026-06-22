from __future__ import annotations

import subprocess
from pathlib import Path

from agent_os.storage import RegisteredProject, Storage


def register_project(
    root: Path,
    *,
    name: str,
    repo_path: Path,
    default_test_command: str,
    allowed_write_roots: list[Path] | None = None,
) -> RegisteredProject:
    root = root.resolve()
    project_name = _validate_project_name(name)
    if not default_test_command.strip():
        raise ValueError("default test command is required")

    git_root = _resolve_git_root(repo_path)
    allowed_roots = _resolve_allowed_write_roots(
        git_root,
        allowed_write_roots or [git_root],
    )

    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    project = storage.upsert_registered_project(
        name=project_name,
        root_path=str(git_root),
        default_test_command=default_test_command,
        allowed_write_roots=[str(path) for path in allowed_roots],
    )
    _write_project_note(root, project)
    return project


def _validate_project_name(name: str) -> str:
    normalized = name.strip()
    if not normalized:
        raise ValueError("project name is required")
    if any(part in normalized for part in ("/", "\\", "..")):
        raise ValueError("project name must not contain path separators")
    return normalized


def _resolve_git_root(repo_path: Path) -> Path:
    resolved = repo_path.expanduser().resolve()
    if not resolved.exists():
        raise ValueError("path does not exist")
    if not resolved.is_dir():
        raise ValueError("path is not a directory")

    result = subprocess.run(
        ["git", "-C", str(resolved), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ValueError("path is not a git repository")
    git_root_text = result.stdout.strip()
    if not git_root_text:
        raise ValueError("git repository root could not be resolved")
    return Path(git_root_text).resolve()


def _resolve_allowed_write_roots(
    git_root: Path,
    allowed_write_roots: list[Path],
) -> list[Path]:
    resolved_roots: list[Path] = []
    for root in allowed_write_roots:
        resolved = root.expanduser().resolve()
        if not resolved.exists():
            raise ValueError(f"allowed write root does not exist: {resolved}")
        if not _is_relative_to(resolved, git_root):
            raise ValueError(
                f"allowed write root must be inside registered repo: {resolved}"
            )
        resolved_roots.append(resolved)
    return sorted(set(resolved_roots), key=str)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _write_project_note(root: Path, project: RegisteredProject) -> Path:
    project_dir = root / "projects" / project.name
    project_dir.mkdir(parents=True, exist_ok=True)
    project_note = project_dir / "project.md"
    project_note.write_text(
        "\n".join(
            [
                f"# Project {project.name}",
                "",
                "- status: registered",
                f"- root_path: {project.root_path}",
                f"- default_test_command: {project.default_test_command}",
                f"- allowed_write_roots: {','.join(project.allowed_write_roots)}",
                f"- created_at: {project.created_at}",
                f"- updated_at: {project.updated_at}",
                "",
                "## Non-Claims",
                "",
                "- Registration does not create a worktree.",
                "- Registration does not run commands or tests.",
                "- Registration does not commit, push, deploy, or mutate external systems.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return project_note
