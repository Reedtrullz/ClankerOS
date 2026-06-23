from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import RegisteredProject, Storage


@dataclass(frozen=True)
class ProjectContext:
    project: RegisteredProject
    status: str
    repo_url: str
    default_branch: str
    current_branch: str
    project_note: str
    memory_path: str
    skills_path: str
    evidence_root: str
    last_activity_at: str


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


def list_project_registry(root: Path) -> list[RegisteredProject]:
    storage = Storage(root.resolve() / ".agent" / "state.db")
    storage.initialize()
    return storage.list_registered_projects()


def load_project_context(root: Path, name: str) -> ProjectContext:
    root = root.resolve()
    project_name = _validate_project_name(name)
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()
    project = storage.get_registered_project(project_name)
    if project is None:
        raise KeyError(project_name)

    repo_path = Path(project.root_path)
    current_branch = _git_value(repo_path, ["branch", "--show-current"])
    default_branch = _default_branch(repo_path, current_branch)
    repo_url = _git_value(repo_path, ["config", "--get", "remote.origin.url"])
    project_note = f"projects/{project.name}/project.md"
    memory_path = f"projects/{project.name}/knowledge.md"
    evidence_root = f"projects/{project.name}/artifacts"
    return ProjectContext(
        project=project,
        status="registered",
        repo_url=repo_url,
        default_branch=default_branch,
        current_branch=current_branch,
        project_note=project_note,
        memory_path=memory_path,
        skills_path=".clanker/skills",
        evidence_root=evidence_root,
        last_activity_at=project.updated_at,
    )


def render_project_line(project: RegisteredProject) -> str:
    allowed_roots = ",".join(project.allowed_write_roots)
    return (
        f"{project.name} status=registered root_path={project.root_path} "
        f'test="{project.default_test_command}" '
        f"allowed_write_roots={allowed_roots} updated_at={project.updated_at}"
    )


def render_project_status_lines(context: ProjectContext) -> list[str]:
    project = context.project
    return [
        f"project_status: {project.name}",
        f"project_id: {project.name}",
        f"status: {context.status}",
        f"root_path: {project.root_path}",
        f"repo_url: {context.repo_url}",
        f"default_branch: {context.default_branch}",
        f"current_branch: {context.current_branch}",
        f"default_test_command: {project.default_test_command}",
        f"allowed_write_roots: {','.join(project.allowed_write_roots)}",
        f"project_note: {context.project_note}",
        f"memory_path: {context.memory_path}",
        f"skills_path: {context.skills_path}",
        f"evidence_root: {context.evidence_root}",
        f"created_at: {project.created_at}",
        f"updated_at: {project.updated_at}",
        f"last_activity_at: {context.last_activity_at}",
        "commands_rerun: 0",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
    ]


def write_project_context(root: Path, name: str) -> tuple[ProjectContext, Path]:
    root = root.resolve()
    context = load_project_context(root, name)
    project = context.project
    project_dir = root / "projects" / project.name
    project_dir.mkdir(parents=True, exist_ok=True)
    context_path = project_dir / "context.md"
    context_path.write_text(
        "\n".join(
            [
                f"# Project Context: {project.name}",
                "",
                "## Registry",
                "",
                f"- project_id: {project.name}",
                f"- status: {context.status}",
                f"- root_path: {project.root_path}",
                f"- repo_url: {context.repo_url}",
                f"- default_branch: {context.default_branch}",
                f"- current_branch: {context.current_branch}",
                f"- default_test_command: {project.default_test_command}",
                f"- allowed_write_roots: {','.join(project.allowed_write_roots)}",
                f"- project_note: {context.project_note}",
                f"- memory_path: {context.memory_path}",
                f"- skills_path: {context.skills_path}",
                f"- evidence_root: {context.evidence_root}",
                f"- last_activity_at: {context.last_activity_at}",
                "",
                "## Operator Commands",
                "",
                "```bash",
                f"python3 -m agent_os.cli project-status {project.name}",
                f'python3 -m agent_os.cli run-goal "..." --project {project.name}',
                "python3 -m agent_os.cli dashboard",
                "python3 -m agent_os.cli iterate",
                "```",
                "",
                "## Non-Claims",
                "",
                "- Project context generation does not run tests, commit, push, deploy, or mutate external systems.",
                "- Project context generation does not create worktrees, approve effects, or call model providers.",
                "- Branch and remote fields are local git readbacks when available, not live GitHub or CI proof.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return context, context_path


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


def _git_value(repo_path: Path, args: list[str]) -> str:
    if not repo_path.exists():
        return "unknown"
    result = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _default_branch(repo_path: Path, current_branch: str) -> str:
    remote_head = _git_value(
        repo_path,
        ["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
    )
    if remote_head != "unknown" and "/" in remote_head:
        return remote_head.split("/", 1)[1]
    return current_branch
