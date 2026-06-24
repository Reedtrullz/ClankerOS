from __future__ import annotations

import json
from dataclasses import asdict, dataclass
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
    PlanRecord,
    PlanStepRecord,
    RoutingDecision,
    RunRecord,
    SkillRecord,
    SprintContractRecord,
    SteeringReview,
    Storage,
    SubagentDelegation,
    Task,
)


@dataclass(frozen=True)
class RunEvidencePacket:
    run: RunRecord
    goal: GoalRecord
    plans: list[PlanRecord]
    plan_steps: list[PlanStepRecord]
    sprint_contract: SprintContractRecord | None
    tasks: list[Task]
    events: list[EventRecord]
    routing_decisions: list[RoutingDecision]
    steering_reviews: list[SteeringReview]
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
    plans = storage.list_plans(run.goal_id)
    plan_steps = [
        step
        for plan in plans
        for step in storage.list_plan_steps(plan.id)
    ]
    latest_plan = plans[-1] if plans else None
    sprint_contract = (
        storage.get_sprint_contract_for_plan(latest_plan.id)
        if latest_plan is not None
        else storage.get_latest_sprint_contract(run.goal_id)
    )
    return RunEvidencePacket(
        run=run,
        goal=goal,
        plans=plans,
        plan_steps=plan_steps,
        sprint_contract=sprint_contract,
        tasks=tasks,
        events=storage.list_events_for_run(run_id),
        routing_decisions=_routing_decisions_for_packet(storage, run, tasks),
        steering_reviews=storage.list_recent_steering_reviews(
            limit=100,
            goal_id=run.goal_id,
        ),
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
    write_evidence_packet(root, packet)
    report_path = root / "runs" / run_id / "evidence-index.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_evidence_index(root, packet), encoding="utf-8")
    return report_path, packet


def evidence_packet_dir(root: Path, packet: RunEvidencePacket) -> Path:
    return (
        root
        / ".clanker"
        / "projects"
        / packet.run.project_id
        / "goals"
        / packet.run.goal_id
        / "runs"
        / packet.run.id
        / "evidence"
    )


def write_evidence_packet(root: Path, packet: RunEvidencePacket) -> Path:
    packet_dir = evidence_packet_dir(root, packet)
    packet_dir.mkdir(parents=True, exist_ok=True)
    _write_json_preserving(packet_dir / "run.json", packet.run)
    _write_json_preserving(packet_dir / "goal.json", packet.goal)
    _write_json_preserving(
        packet_dir / "plan.json",
        {
            "plan": packet.plans[-1] if packet.plans else None,
            "plans": packet.plans,
            "steps": packet.plan_steps,
        },
    )
    _write_json_preserving(
        packet_dir / "contract.json",
        packet.sprint_contract if packet.sprint_contract is not None else {"contract": None},
    )
    _write_json_preserving(packet_dir / "tasks.json", packet.tasks)
    _write_json_preserving(
        packet_dir / "verification.json",
        {
            "run_id": packet.run.id,
            "goal_id": packet.run.goal_id,
            "tasks_total": len(packet.tasks),
            "tasks_completed": packet.completed_task_count,
            "tasks_with_passed_verification": packet.passed_verification_count,
            "open_incidents": packet.open_incident_count,
            "pending_approvals": packet.pending_approval_count,
            "recommended_next_action": packet.recommended_next_action,
            "network_actions_taken": 0,
            "external_mutations_taken": 0,
            "non_claims": [
                "Evidence packet export does not rerun commands.",
                "Evidence packet export does not approve effects or commit code.",
                "Evidence packet export does not call model providers.",
            ],
        },
    )
    _write_jsonl_preserving(packet_dir / "events.jsonl", packet.events)
    _write_jsonl_preserving(packet_dir / "routing_decisions.jsonl", packet.routing_decisions)
    _write_jsonl_preserving(packet_dir / "delegations.jsonl", packet.delegations)
    _write_jsonl_preserving(packet_dir / "steering_reviews.jsonl", packet.steering_reviews)
    _write_jsonl_preserving(packet_dir / "commands.jsonl", _command_snapshots(packet))
    _write_jsonl_preserving(packet_dir / "approvals.jsonl", packet.approvals)
    _write_jsonl_preserving(packet_dir / "effects.jsonl", packet.effects)
    _write_jsonl_preserving(packet_dir / "memory_proposals.jsonl", packet.memory_entries)
    _write_jsonl_preserving(packet_dir / "skill_proposals.jsonl", packet.skills)
    _write_jsonl_preserving(packet_dir / "incidents.jsonl", packet.incidents)
    _write_jsonl_preserving(packet_dir / "eval_candidates.jsonl", packet.eval_candidates)
    _write_text_preserving(
        packet_dir / "summary.md",
        render_evidence_packet_summary(root, packet),
    )
    _write_text_preserving(
        packet_dir / "final_review.md",
        render_run_review(root, packet),
    )
    return packet_dir


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
    if packet.plans:
        latest_plan = packet.plans[-1]
        lines.append(
            f"- plan {latest_plan.id}: v{latest_plan.version} "
            f"status={latest_plan.status} profile={latest_plan.created_by_profile}"
        )
        for step in packet.plan_steps:
            lines.append(
                f"- step {step.order_index}: {step.status} "
                f"profile={step.assigned_profile} task={step.task_id or 'none'} "
                f"title={step.title}"
            )
    else:
        lines.append("- no persistent plan recorded")
    if packet.sprint_contract is not None:
        lines.append(
            f"- contract {packet.sprint_contract.id}: "
            f"status={packet.sprint_contract.status}"
        )
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
    lines.append(f"- routing_decisions: {len(packet.routing_decisions)}")
    lines.append(f"- steering_reviews: {len(packet.steering_reviews)}")
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
        f"- packet_dir: {_relative_to_root(root, str(evidence_packet_dir(root, packet)))}",
        "",
        "## Run Files",
        "",
    ]
    lines.extend(f"- {path}" for path in run_files) if run_files else lines.append("- none")
    lines.extend(["", "## Evidence Packet Files", ""])
    lines.extend(f"- {path}" for path in _evidence_packet_file_paths(root, packet))
    lines.extend(["", "## Project Artifacts", ""])
    lines.extend(f"- {path}" for path in project_artifacts) if project_artifacts else lines.append("- none")
    lines.extend(
        [
            "",
            "## Database Rows",
            "",
            f"- tasks: {len(packet.tasks)}",
            f"- plans: {len(packet.plans)}",
            f"- plan_steps: {len(packet.plan_steps)}",
            f"- sprint_contracts: {1 if packet.sprint_contract else 0}",
            f"- events: {len(packet.events)}",
            f"- routing_decisions: {len(packet.routing_decisions)}",
            f"- steering_reviews: {len(packet.steering_reviews)}",
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
    paths.extend(_existing_paths(root, [plan.artifact_path for plan in packet.plans]))
    paths.extend(
        _existing_paths(
            root,
            [packet.sprint_contract.artifact_path if packet.sprint_contract else None]
            + [review.report_path for review in packet.steering_reviews],
        )
    )
    paths.extend(_existing_paths(root, _evidence_packet_file_paths(root, packet)))
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
    for decision in packet.routing_decisions:
        lines.append(
            f"- routing {decision.id}: status={decision.status} "
            f"profile={decision.selected_profile} category={decision.category}"
        )
    for review in packet.steering_reviews:
        lines.append(
            f"- steering {review.id}: drift={review.drift_score} "
            f"next={review.recommended_next_action} "
            f"report={_relative_to_root(root, review.report_path)}"
        )
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


def render_evidence_packet_summary(root: Path, packet: RunEvidencePacket) -> str:
    return "\n".join(
        [
            "# Evidence Packet Summary",
            "",
            f"- run_id: {packet.run.id}",
            f"- goal_id: {packet.run.goal_id}",
            f"- project_id: {packet.run.project_id}",
            f"- status: {packet.run.status}",
            f"- recommended_next_action: {packet.recommended_next_action}",
            f"- plans: {len(packet.plans)}",
            f"- plan_steps: {len(packet.plan_steps)}",
            f"- sprint_contracts: {1 if packet.sprint_contract else 0}",
            f"- tasks: {len(packet.tasks)}",
            f"- routing_decisions: {len(packet.routing_decisions)}",
            f"- delegations: {len(packet.delegations)}",
            f"- steering_reviews: {len(packet.steering_reviews)}",
            f"- packet_dir: {_relative_to_root(root, str(evidence_packet_dir(root, packet)))}",
            "",
            "## Boundary",
            "",
            "- This packet is a local snapshot for operator review.",
            "- It does not rerun commands, approve effects, commit code, push, deploy, or call model providers.",
            "- network_actions_taken: 0",
            "- external_mutations_taken: 0",
            "",
        ]
    )


def _evidence_packet_file_paths(root: Path, packet: RunEvidencePacket) -> list[str]:
    packet_dir = evidence_packet_dir(root, packet)
    names = [
        "summary.md",
        "operator-summary.md",
        "run.json",
        "goal.json",
        "plan.json",
        "contract.json",
        "tasks.json",
        "tasks-snapshot.json",
        "events.jsonl",
        "routing_decisions.jsonl",
        "routing_decisions-snapshot.jsonl",
        "delegations.jsonl",
        "steering_reviews.jsonl",
        "commands.jsonl",
        "commands-snapshot.jsonl",
        "verification.json",
        "verification-summary.json",
        "approvals.jsonl",
        "effects.jsonl",
        "memory_proposals.jsonl",
        "skill_proposals.jsonl",
        "incidents.jsonl",
        "eval_candidates.jsonl",
        "final_review.md",
    ]
    return [
        _relative_to_root(root, str(packet_dir / name))
        for name in names
        if (packet_dir / name).exists()
    ]


def _routing_decisions_for_packet(
    storage: Storage,
    run: RunRecord,
    tasks: list[Task],
) -> list[RoutingDecision]:
    task_ids = {task.id for task in tasks}
    decisions = storage.list_recent_routing_decisions(limit=None)
    filtered = [
        decision
        for decision in decisions
        if decision.goal_id == run.goal_id or decision.task_id in task_ids
    ]
    return list(reversed(filtered))


def _command_snapshots(packet: RunEvidencePacket) -> list[dict[str, object]]:
    commands: list[dict[str, object]] = []
    for step in packet.plan_steps:
        if step.verification_command:
            commands.append(
                {
                    "source": "plan_step",
                    "plan_step_id": step.id,
                    "task_id": step.task_id,
                    "command": step.verification_command,
                    "status": step.status,
                }
            )
    for task in packet.tasks:
        command = task.verification_plan.get("command")
        if command:
            commands.append(
                {
                    "source": "task_verification_plan",
                    "task_id": task.id,
                    "command": command,
                    "status": task.status,
                }
            )
        else:
            commands.append(
                {
                    "source": "task_verification_plan",
                    "task_id": task.id,
                    "verification_plan": task.verification_plan,
                    "status": task.status,
                }
            )
    return commands


def _write_text_preserving(path: Path, content: str) -> Path:
    target = _preserving_target(path)
    target.write_text(content, encoding="utf-8")
    return target


def _write_json_preserving(path: Path, value: object) -> Path:
    target = _preserving_target(path)
    _write_json(target, value)
    return target


def _write_jsonl_preserving(path: Path, values: list[object]) -> Path:
    target = _preserving_target(path)
    _write_jsonl(target, values)
    return target


def _preserving_target(path: Path) -> Path:
    if not path.exists():
        return path
    sidecars = {
        "summary.md": "operator-summary.md",
        "verification.json": "verification-summary.json",
        "tasks.json": "tasks-snapshot.json",
        "routing_decisions.jsonl": "routing_decisions-snapshot.jsonl",
        "commands.jsonl": "commands-snapshot.jsonl",
    }
    return path.with_name(sidecars.get(path.name, path.name))


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(_jsonable(value), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, values: list[object]) -> None:
    path.write_text(
        "".join(json.dumps(_jsonable(value), sort_keys=True) + "\n" for value in values),
        encoding="utf-8",
    )


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


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
