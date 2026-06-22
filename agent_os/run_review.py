from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_os.storage import (
    ApprovalRequest,
    Effect,
    EvalCandidate,
    EventRecord,
    GoalRecord,
    Incident,
    Learning,
    MemoryEntry,
    RunRecord,
    SkillRecord,
    Storage,
    SubagentDelegation,
    Task,
)


@dataclass(frozen=True)
class RunEvidencePacket:
    run: RunRecord
    goal: GoalRecord
    tasks: list[Task]
    events: list[EventRecord]
    learnings: list[Learning]
    incidents: list[Incident]
    approvals: list[ApprovalRequest]
    effects: list[Effect]
    delegations: list[SubagentDelegation]
    memory_entries: list[MemoryEntry]
    skills: list[SkillRecord]
    eval_candidates: list[EvalCandidate]

    @property
    def pending_approval_count(self) -> int:
        return sum(1 for approval in self.approvals if approval.status == "pending")

    @property
    def open_incident_count(self) -> int:
        return sum(1 for incident in self.incidents if incident.status == "open")

    @property
    def completed_task_count(self) -> int:
        return sum(1 for task in self.tasks if task.status == "completed")

    @property
    def passed_verification_count(self) -> int:
        return sum(1 for task in self.tasks if task.evidence.get("passed") is True)

    @property
    def recommended_next_action(self) -> str:
        if self.pending_approval_count:
            return "operator_approval"
        if self.open_incident_count:
            return "incident_review"
        if any(task.status == "blocked" for task in self.tasks):
            return "review_or_replan"
        if self.run.status == "completed":
            return "final_review"
        return "continue_run_review"


def collect_run_evidence(root: Path, run_id: str) -> RunEvidencePacket:
    storage = Storage(root / ".agent" / "state.db")
    run = storage.get_run(run_id)
    goal = storage.get_goal(run.goal_id)
    tasks = storage.list_tasks_for_run(run_id)
    if not tasks:
        tasks = storage.list_tasks(run.goal_id)
    return RunEvidencePacket(
        run=run,
        goal=goal,
        tasks=tasks,
        events=storage.list_events_for_run(run_id),
        learnings=storage.list_learnings_for_run(run_id),
        incidents=storage.list_incidents_for_run(run_id),
        approvals=storage.list_approval_requests_for_run(run_id),
        effects=storage.list_effects_for_run(run_id),
        delegations=storage.list_subagent_delegations(run.goal_id),
        memory_entries=storage.list_memory_entries_for_source(source_id=run_id),
        skills=storage.list_skills_for_source_run(run_id),
        eval_candidates=storage.list_eval_candidates_for_source(
            source_type="run",
            source_id=run_id,
        ),
    )


def write_run_review(root: Path, run_id: str) -> tuple[Path, RunEvidencePacket]:
    packet = collect_run_evidence(root, run_id)
    report_path = root / "runs" / run_id / "review.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_run_review(root, packet), encoding="utf-8")
    return report_path, packet


def write_evidence_index(root: Path, run_id: str) -> tuple[Path, RunEvidencePacket]:
    packet = collect_run_evidence(root, run_id)
    report_path = root / "runs" / run_id / "evidence-index.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_evidence_index(root, packet), encoding="utf-8")
    return report_path, packet


def write_replay_summary(root: Path, run_id: str) -> tuple[Path, RunEvidencePacket]:
    packet = collect_run_evidence(root, run_id)
    report_path = root / "runs" / run_id / "replay-summary.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_replay_summary(root, packet), encoding="utf-8")
    return report_path, packet


def render_run_review(root: Path, packet: RunEvidencePacket) -> str:
    lines = [
        "# Run Review",
        "",
        f"- run_id: {packet.run.id}",
        f"- project_id: {packet.run.project_id}",
        f"- status: {packet.run.status}",
        f"- started_at: {packet.run.started_at}",
        f"- completed_at: {packet.run.completed_at or 'in_progress'}",
        "",
        "## Original Goal",
        "",
        packet.goal.description,
        "",
        "## Current Plan",
        "",
    ]
    if packet.tasks:
        for task in packet.tasks:
            lines.append(
                f"- {task.id}: {task.status} type={task.task_type} "
                f"risk={task.risk_level} attempts={task.attempts}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Verification",
            "",
            f"- passed={packet.passed_verification_count}",
            f"- tasks={len(packet.tasks)}",
            f"- open_incidents={packet.open_incident_count}",
            f"- pending_approvals={packet.pending_approval_count}",
            "",
            "## Evidence Files",
            "",
        ]
    )
    evidence_paths = _evidence_paths(root, packet)
    if evidence_paths:
        lines.extend(f"- {path}" for path in evidence_paths)
    else:
        lines.append("- none")

    lines.extend(["", "## Operator Signals", ""])
    lines.append(f"- approvals: {len(packet.approvals)}")
    lines.append(f"- incidents: {len(packet.incidents)}")
    lines.append(f"- effects: {len(packet.effects)}")
    lines.append(f"- delegations: {len(packet.delegations)}")
    lines.append(f"- memory_proposals: {len(packet.memory_entries)}")
    lines.append(f"- skill_proposals: {len(packet.skills)}")

    lines.extend(
        [
            "",
            "## Recommended Next Action",
            "",
            f"- {packet.recommended_next_action}",
            "",
            "## Non-Claims",
            "",
            "- network_actions_taken: 0",
            "- external_mutations_taken: 0",
            "- This report does not approve effects, commit changes, push code, or rerun work.",
            "",
        ]
    )
    return "\n".join(lines)


def render_evidence_index(root: Path, packet: RunEvidencePacket) -> str:
    run_files = _existing_paths(
        root,
        [
            packet.run.activity_path,
            packet.run.events_path,
            packet.run.summary_path,
        ],
    )
    project_artifacts = _project_artifact_paths(root, packet)
    lines = [
        "# Evidence Index",
        "",
        f"- run_id: {packet.run.id}",
        f"- project_id: {packet.run.project_id}",
        f"- status: {packet.run.status}",
        "",
        "## Run Files",
        "",
    ]
    lines.extend(f"- {path}" for path in run_files) if run_files else lines.append("- none")
    lines.extend(["", "## Project Artifacts", ""])
    lines.extend(f"- {path}" for path in project_artifacts) if project_artifacts else lines.append("- none")
    lines.extend(
        [
            "",
            "## Database Rows",
            "",
            f"- tasks: {len(packet.tasks)}",
            f"- events: {len(packet.events)}",
            f"- learnings: {len(packet.learnings)}",
            f"- incidents: {len(packet.incidents)}",
            f"- approvals: {len(packet.approvals)}",
            f"- effects: {len(packet.effects)}",
            f"- delegations: {len(packet.delegations)}",
            f"- memory_entries: {len(packet.memory_entries)}",
            f"- skills: {len(packet.skills)}",
            f"- eval_candidates: {len(packet.eval_candidates)}",
            "",
            "## Proposal And Effect References",
            "",
        ]
    )
    references = _proposal_and_effect_lines(root, packet)
    lines.extend(references if references else ["- none"])
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Does not replay or rerun the work.",
            "- Does not approve, reject, commit, push, deploy, or mutate external systems.",
            "- network_actions_taken: 0",
            "- external_mutations_taken: 0",
            "",
        ]
    )
    return "\n".join(lines)


def render_replay_summary(root: Path, packet: RunEvidencePacket) -> str:
    lines = [
        "# Replay Summary",
        "",
        f"- run_id: {packet.run.id}",
        f"- project_id: {packet.run.project_id}",
        f"- status: {packet.run.status}",
        "- conceptual_replay_only: true",
        "- commands_rerun: 0",
        "",
        "## Replay Steps",
        "",
    ]
    if packet.events:
        for event in packet.events:
            task = f" task={event.task_id}" if event.task_id else ""
            lines.append(
                f"- {event.created_at}: {event.event_type}{task} - {event.message}"
            )
    else:
        lines.append("- no events recorded")

    lines.extend(
        [
            "",
            "## Inputs Needed For Manual Replay",
            "",
            f"- original_goal: {packet.goal.description}",
            f"- summary: {_relative_to_root(root, packet.run.summary_path)}",
            f"- events: {_relative_to_root(root, packet.run.events_path)}",
            f"- artifacts: {len(_project_artifact_paths(root, packet))}",
            "",
            "## Replay Boundary",
            "",
            "- This report does not rerun commands, mutate files, or approve effects.",
            "- It is a conceptual replay map for operator review and future automation.",
            "",
        ]
    )
    return "\n".join(lines)


def _evidence_paths(root: Path, packet: RunEvidencePacket) -> list[str]:
    paths = _existing_paths(
        root,
        [
            packet.run.activity_path,
            packet.run.events_path,
            packet.run.summary_path,
        ],
    )
    paths.extend(_project_artifact_paths(root, packet))
    paths.extend(
        _existing_paths(
            root,
            [incident.evidence_path for incident in packet.incidents]
            + [incident.resolution_evidence_path for incident in packet.incidents]
            + [effect.evidence_path for effect in packet.effects]
            + [delegation.result_artifact_path for delegation in packet.delegations]
            + [entry.artifact_path for entry in packet.memory_entries]
            + [skill.path for skill in packet.skills]
            + [candidate.candidate_path for candidate in packet.eval_candidates],
        )
    )
    return _unique(paths)


def _project_artifact_paths(root: Path, packet: RunEvidencePacket) -> list[str]:
    paths = []
    for task in packet.tasks:
        paths.extend(task.artifacts)
    paths.extend(learning.source for learning in packet.learnings)
    return _unique(_existing_paths(root, paths))


def _proposal_and_effect_lines(root: Path, packet: RunEvidencePacket) -> list[str]:
    lines: list[str] = []
    for approval in packet.approvals:
        lines.append(f"- approval {approval.id}: status={approval.status} task={approval.task_id}")
    for incident in packet.incidents:
        lines.append(
            f"- incident {incident.id}: status={incident.status} "
            f"evidence={_relative_to_root(root, incident.evidence_path)}"
        )
    for effect in packet.effects:
        lines.append(
            f"- effect {effect.id}: status={effect.status} "
            f"type={effect.effect_type} evidence={_relative_to_root(root, effect.evidence_path)}"
        )
    for entry in packet.memory_entries:
        lines.append(
            f"- memory {entry.id}: status={entry.status} "
            f"artifact={_relative_to_root(root, entry.artifact_path)}"
        )
    for skill in packet.skills:
        lines.append(
            f"- skill {skill.id}: status={skill.status} path={_relative_to_root(root, skill.path)}"
        )
    return lines


def _existing_paths(root: Path, paths: list[str | None]) -> list[str]:
    existing = []
    for path in paths:
        if not path:
            continue
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = root / candidate
        if candidate.exists():
            existing.append(_relative_to_root(root, str(candidate)))
    return _unique(existing)


def _relative_to_root(root: Path, path: str | None) -> str:
    if not path:
        return "none"
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        return str(candidate.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(candidate)


def _unique(paths: list[str]) -> list[str]:
    seen = set()
    unique_paths = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique_paths.append(path)
    return unique_paths
