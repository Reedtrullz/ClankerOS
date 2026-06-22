from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import EvalRun, Playbook, Storage


DEFAULT_MIN_SUCCESSES = 2


@dataclass(frozen=True)
class PlaybookDefinition:
    slug: str
    title: str
    source_eval_name: str
    trigger: str
    steps: list[str]


PLAYBOOK_DEFINITIONS = [
    PlaybookDefinition(
        slug="first-milestone-closed-loop",
        title="First Milestone Closed Loop Playbook",
        source_eval_name="first_milestone_closed_loop",
        trigger=(
            "Use when validating the local goal -> task graph -> execution -> "
            "verification -> memory -> dashboard loop."
        ),
        steps=[
            "Run `python3 -m agent_os.cli init` to make sure local state exists.",
            "Run `python3 -m agent_os.cli eval` to exercise the closed-loop path.",
            "Run `python3 -m agent_os.cli dashboard` to refresh operator visibility.",
            "Inspect `docs/dashboard.md` and `evals/results/first_milestone_closed_loop.json`.",
            "Record any gap as an eval, guardrail, queue item, or learning update.",
        ],
    )
]


def promote_successful_run_playbooks(
    root: Path,
    *,
    min_successes: int = DEFAULT_MIN_SUCCESSES,
) -> list[Playbook]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    promoted: list[Playbook] = []
    for definition in PLAYBOOK_DEFINITIONS:
        runs = storage.list_successful_eval_runs(definition.source_eval_name)
        if len(runs) < min_successes:
            continue

        playbook_path = root / "playbooks" / f"{definition.slug}.md"
        relative_path = _relative_to_root(root, playbook_path)
        playbook_path.parent.mkdir(parents=True, exist_ok=True)
        playbook_path.write_text(
            render_playbook(definition, runs),
            encoding="utf-8",
        )
        promoted.append(
            storage.record_playbook(
                slug=definition.slug,
                title=definition.title,
                source_eval_name=definition.source_eval_name,
                successful_run_count=len(runs),
                playbook_path=relative_path,
                status="active",
            )
        )

    write_playbook_index(root, storage.list_recent_playbooks(limit=20))
    return promoted


def write_playbook_index(root: Path, playbooks: list[Playbook]) -> Path:
    root = root.resolve()
    index_path = root / "docs" / "playbooks.md"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Playbooks",
        "",
        "- source: repeated successful local eval runs",
        f"- active: {sum(playbook.status == 'active' for playbook in playbooks)}",
        "",
        "## Active Playbooks",
        "",
    ]
    active_playbooks = [playbook for playbook in playbooks if playbook.status == "active"]
    if active_playbooks:
        lines.extend(render_playbook_line(playbook) for playbook in active_playbooks)
    else:
        lines.append("- none")
    lines.append("")
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def render_playbook(definition: PlaybookDefinition, runs: list[EvalRun]) -> str:
    lines = [
        f"# {definition.title}",
        "",
        f"- Source eval: {definition.source_eval_name}",
        f"- Successful runs: {len(runs)}",
        "- Status: active",
        "",
        "## Trigger",
        "",
        definition.trigger,
        "",
        "## Steps",
        "",
    ]
    lines.extend(f"{index}. {step}" for index, step in enumerate(definition.steps, start=1))
    lines.extend(
        [
            "",
            "## Evidence Pattern",
            "",
            "- `evals/results/first_milestone_closed_loop.json` records the latest run result.",
            "- `runs/<run_id>/activity.md` records execution events for each run.",
            "- `runs/<run_id>/summary.md` records the run summary.",
            "- `docs/dashboard.md` exposes current operator visibility.",
            "",
            "## Successful Runs",
            "",
        ]
    )
    for run in runs:
        run_id = run.details.get("run_id", "unknown")
        checks = run.details.get("checks", {})
        completed = checks.get("tasks_completed", "unknown")
        lines.append(
            f"- {run_id}: eval={run.name} status={run.status} "
            f"tasks_completed={completed} created_at={run.created_at}"
        )
    lines.append("")
    return "\n".join(lines)


def render_playbook_line(playbook: Playbook) -> str:
    return (
        f"- {playbook.slug}: {playbook.status} source={playbook.source_eval_name} "
        f"successful_runs={playbook.successful_run_count} path={playbook.playbook_path}"
    )


def _relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
