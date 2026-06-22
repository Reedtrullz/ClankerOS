from __future__ import annotations

import re
from pathlib import Path

from agent_os.storage import Learning, LearningDistillation, Storage


DEFAULT_MIN_OCCURRENCES = 3
RUN_ID_PATTERN = re.compile(r"\brun_[A-Za-z0-9]+\b")
GENERATED_START = "<!-- learning-distillation:start -->"
GENERATED_END = "<!-- learning-distillation:end -->"


def distill_learnings(
    root: Path,
    *,
    min_occurrences: int = DEFAULT_MIN_OCCURRENCES,
) -> tuple[Path, LearningDistillation]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    learnings = storage.list_recent_learnings(limit=1000)
    stable_learnings = _stable_learning_payloads(
        learnings,
        min_occurrences=min_occurrences,
    )
    status = "stable" if stable_learnings else "no_stable_learnings"
    report_path = root / "docs" / "learning-distillation.md"
    relative_report_path = _relative_to_root(root, report_path)
    distillation = storage.record_learning_distillation(
        status=status,
        min_occurrences=min_occurrences,
        stable_learnings=stable_learnings,
        source_learning_count=len(learnings),
        report_path=relative_report_path,
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_learning_distillation_report(distillation),
        encoding="utf-8",
    )
    _update_root_knowledge(root, distillation)
    return report_path, distillation


def render_learning_distillation_report(distillation: LearningDistillation) -> str:
    lines = [
        "# Learning Distillation",
        "",
        f"- id: {distillation.id}",
        f"- status: {distillation.status}",
        f"- min_occurrences: {distillation.min_occurrences}",
        f"- source_learnings: {distillation.source_learning_count}",
        f"- stable_learnings: {distillation.stable_learning_count}",
        f"- report_path: {distillation.report_path}",
        "- knowledge_path: knowledge.md",
        "- normalization: `run_[A-Za-z0-9]+` -> `run_<id>`",
        f"- created_at: {distillation.created_at}",
        "",
        "## Stable Learnings",
        "",
    ]
    if distillation.stable_learnings:
        lines.extend(
            render_stable_learning_line(learning)
            for learning in distillation.stable_learnings
        )
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local evidence.",
            "- Does not edit prompts, skills, playbooks, handoffs, tasks, or approvals.",
            "- Does not imply a scheduler, watcher, CI gate, deploy gate, retry, replay, or external side effect.",
        ]
    )
    lines.append("")
    return "\n".join(lines)


def render_learning_distillation_line(distillation: LearningDistillation) -> str:
    return (
        f"- {distillation.id}: status={distillation.status} "
        f"stable_learnings={distillation.stable_learning_count} "
        f"source_learnings={distillation.source_learning_count} "
        f"min_occurrences={distillation.min_occurrences} "
        f"report={distillation.report_path}"
    )


def render_stable_learning_line(learning: dict[str, object]) -> str:
    run_ids = ",".join(str(run_id) for run_id in learning.get("run_ids", []))
    return (
        f"- {learning['summary']} occurrences={learning['occurrences']} "
        f"runs={run_ids}"
    )


def _stable_learning_payloads(
    learnings: list[Learning],
    *,
    min_occurrences: int,
) -> list[dict[str, object]]:
    groups: dict[str, list[Learning]] = {}
    for learning in learnings:
        groups.setdefault(_normalize_summary(learning.summary), []).append(learning)

    stable: list[dict[str, object]] = []
    for summary, grouped in groups.items():
        if len(grouped) < min_occurrences:
            continue
        ordered = sorted(grouped, key=lambda item: (item.created_at, item.id))
        stable.append(
            {
                "summary": summary,
                "occurrences": len(grouped),
                "run_ids": [learning.run_id for learning in ordered],
                "project_ids": sorted({learning.project_id for learning in grouped}),
                "sources": [learning.source for learning in ordered],
                "first_seen_at": ordered[0].created_at,
                "latest_seen_at": ordered[-1].created_at,
            }
        )

    return sorted(
        stable,
        key=lambda learning: (
            -int(learning["occurrences"]),
            str(learning["summary"]),
        ),
    )


def _normalize_summary(summary: str) -> str:
    return RUN_ID_PATTERN.sub("run_<id>", " ".join(summary.split()))


def _update_root_knowledge(root: Path, distillation: LearningDistillation) -> None:
    knowledge_path = root / "knowledge.md"
    if knowledge_path.exists():
        existing = knowledge_path.read_text(encoding="utf-8")
    else:
        existing = "# Knowledge\n"

    section = _render_generated_knowledge_section(distillation)
    if GENERATED_START in existing and GENERATED_END in existing:
        before, remainder = existing.split(GENERATED_START, maxsplit=1)
        _, after = remainder.split(GENERATED_END, maxsplit=1)
        updated = f"{before}{GENERATED_START}\n{section}\n{GENERATED_END}{after}"
    elif "## Stable Distilled Learnings" in existing:
        updated = existing.rstrip() + "\n\n" + _wrapped_generated_section(section)
    else:
        updated = (
            existing.rstrip()
            + "\n\n## Stable Distilled Learnings\n\n"
            + _wrapped_generated_section(section)
        )

    knowledge_path.write_text(updated.rstrip() + "\n", encoding="utf-8")


def _wrapped_generated_section(section: str) -> str:
    return f"{GENERATED_START}\n{section}\n{GENERATED_END}"


def _render_generated_knowledge_section(distillation: LearningDistillation) -> str:
    lines = [
        f"- source: {distillation.report_path}",
        f"- status: {distillation.status}",
        f"- min_occurrences: {distillation.min_occurrences}",
        f"- source_learnings: {distillation.source_learning_count}",
        f"- stable_learnings: {distillation.stable_learning_count}",
        "",
    ]
    if distillation.stable_learnings:
        lines.extend(
            f"- {learning['summary']} "
            f"(occurrences={learning['occurrences']}, evidence={distillation.report_path})"
            for learning in distillation.stable_learnings
        )
    else:
        lines.append("- none")
    return "\n".join(lines)


def _relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
