from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from agent_os.coder_prep import render_coder_prep_review_lines
from agent_os.coder_worktree_execution import (
    render_coder_worktree_approval_review_lines,
    render_coder_worktree_commit_review_lines,
    render_coder_worktree_run_review_lines,
)
from agent_os.coder_worktree_plan import render_coder_worktree_plan_review_lines
from agent_os.implementation_handoff import render_implementation_handoff_review_lines
from agent_os.subagent_delegation import load_delegation_result_metadata
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


@dataclass(frozen=True)
class GitEvidenceSnapshot:
    status_text: str
    diff_text: str
    changed_files: dict[str, object]


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
    git_snapshot = _collect_git_evidence_snapshot(root, packet)
    _write_text_preserving(packet_dir / "git_status.txt", git_snapshot.status_text)
    _write_text_preserving(packet_dir / "diff.patch", git_snapshot.diff_text)
    _write_json_preserving(packet_dir / "changed_files.json", git_snapshot.changed_files)
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

    scout_context_lines = _scout_context_pack_lines(root, packet.delegations)
    if scout_context_lines:
        lines.extend(["", "## Scout Context Pack", ""])
        lines.extend(scout_context_lines)

    implementation_handoff_lines = render_implementation_handoff_review_lines(
        root,
        packet.delegations,
    )
    if implementation_handoff_lines:
        lines.extend(["", "## Implementation Handoff", ""])
        lines.extend(implementation_handoff_lines)

    coder_prep_lines: list[str] = []
    for delegation in packet.delegations:
        metadata = load_delegation_result_metadata(delegation)
        run_id = metadata.get("execution_run_id") or metadata.get("run_id")
        if run_id:
            coder_prep_lines.extend(
                render_coder_prep_review_lines(root, delegation.id, str(run_id))
            )
    if coder_prep_lines:
        lines.extend(["", "## Coder Prep", ""])
        lines.extend(coder_prep_lines)

    coder_worktree_plan_lines: list[str] = []
    for delegation in packet.delegations:
        metadata = load_delegation_result_metadata(delegation)
        run_id = metadata.get("execution_run_id") or metadata.get("run_id")
        if run_id:
            coder_worktree_plan_lines.extend(
                render_coder_worktree_plan_review_lines(
                    root,
                    delegation.id,
                    str(run_id),
                )
            )
    if coder_worktree_plan_lines:
        lines.extend(["", "## Coder Worktree Plan", ""])
        lines.extend(coder_worktree_plan_lines)

    coder_worktree_approval_lines: list[str] = []
    coder_worktree_run_lines: list[str] = []
    coder_worktree_commit_lines: list[str] = []
    for delegation in packet.delegations:
        coder_worktree_approval_lines.extend(
            render_coder_worktree_approval_review_lines(root, delegation.id)
        )
        coder_worktree_run_lines.extend(
            render_coder_worktree_run_review_lines(root, delegation.id)
        )
        coder_worktree_commit_lines.extend(
            render_coder_worktree_commit_review_lines(root, delegation.id)
        )
    if coder_worktree_approval_lines:
        lines.extend(["", "## Coder Worktree Approval", ""])
        lines.extend(coder_worktree_approval_lines)
    if coder_worktree_run_lines:
        lines.extend(["", "## Coder Worktree Run", ""])
        lines.extend(coder_worktree_run_lines)
    if coder_worktree_commit_lines:
        lines.extend(["", "## Coder Worktree Commit", ""])
        lines.extend(coder_worktree_commit_lines)

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


def _scout_context_pack_lines(
    root: Path,
    delegations: list[SubagentDelegation],
) -> list[str]:
    lines: list[str] = []
    for delegation in delegations:
        metadata = load_delegation_result_metadata(delegation)
        context_pack_path = metadata.get("context_pack_json")
        if not context_pack_path:
            continue
        full_path = root / context_pack_path
        lines.append(
            f"- delegation={delegation.id} profile={delegation.assigned_profile} "
            f"context_pack={context_pack_path}"
        )
        if metadata.get("context_pack_id"):
            lines.append(f"  - context_pack_id: {metadata['context_pack_id']}")
        if metadata.get("implementation_handoff_json"):
            lines.append(
                f"  - implementation_handoff: {metadata['implementation_handoff_json']}"
            )
        if "context_pack_returned_files_in_inventory" in metadata:
            lines.append(
                "  - returned_files_in_inventory: "
                f"{_review_bool(metadata['context_pack_returned_files_in_inventory'])}"
            )
        missing = metadata.get("context_pack_returned_files_missing") or []
        if missing:
            lines.append(f"  - returned_files_missing: {', '.join(missing)}")
        try:
            payload = json.loads(full_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            lines.append("  - context_pack_readable: false")
            continue
        top_files = [item["path"] for item in payload.get("ranked_files", [])[:5]]
        test_hints = [hint["path"] for hint in payload.get("test_hints", [])[:5]]
        referenced = metadata.get("context_pack_top_ranked_files_referenced") or []
        lines.append(f"  - top_ranked_files: {', '.join(top_files) if top_files else 'none'}")
        lines.append(f"  - test_hints: {', '.join(test_hints) if test_hints else 'none'}")
        lines.append(
            "  - scout_output_referenced_top_files: "
            f"{', '.join(referenced) if referenced else 'unknown'}"
        )
    return lines


def _review_bool(value: object) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    return "unknown"


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
        "git_status.txt",
        "diff.patch",
        "changed_files.json",
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


def _collect_git_evidence_snapshot(root: Path, packet: RunEvidencePacket) -> GitEvidenceSnapshot:
    target_root, target_source = _git_evidence_target(root, packet)
    resolved_target = target_root.resolve()
    rev_parse = _run_git(resolved_target, ["rev-parse", "--show-toplevel"])
    if rev_parse.returncode != 0:
        return GitEvidenceSnapshot(
            status_text=(
                f"not_git_repo: {resolved_target}\n"
                f"command: git rev-parse --show-toplevel\n"
                f"returncode: {rev_parse.returncode}\n"
                f"stdout:\n{rev_parse.stdout}\n"
                f"stderr:\n{rev_parse.stderr}"
            ),
            diff_text="",
            changed_files={
                "is_git_repo": False,
                "target_root": str(resolved_target),
                "target_source": target_source,
                "commands": {
                    "git_root": "git rev-parse --show-toplevel",
                },
                "returncodes": {
                    "git_root": rev_parse.returncode,
                },
                "changed_files": [],
                "tracked_changed_files": [],
                "untracked_files": [],
                "network_actions_taken": 0,
                "external_mutations_taken": 0,
                "non_claims": [
                    "Git snapshot export does not commit, push, fetch, pull, or mutate files.",
                    "No git diff is available because the selected target is not a git repository.",
                ],
            },
        )

    status = _run_git(resolved_target, ["status", "--short", "--branch"])
    diff, diff_command = _git_output_with_head_fallback(
        resolved_target,
        ["diff", "--no-ext-diff", "--binary", "HEAD", "--"],
        ["diff", "--no-ext-diff", "--binary"],
    )
    tracked, tracked_command = _git_output_with_head_fallback(
        resolved_target,
        ["diff", "--name-only", "HEAD", "--"],
        ["diff", "--name-only"],
    )
    untracked = _run_git(resolved_target, ["ls-files", "--others", "--exclude-standard"])
    tracked_files = _split_git_path_lines(tracked.stdout if tracked.returncode == 0 else "")
    untracked_files = _split_git_path_lines(
        untracked.stdout if untracked.returncode == 0 else ""
    )
    changed_files = sorted(set(tracked_files + untracked_files))
    return GitEvidenceSnapshot(
        status_text=status.stdout if status.returncode == 0 else status.stderr,
        diff_text=diff.stdout if diff.returncode == 0 else diff.stderr,
        changed_files={
            "is_git_repo": True,
            "target_root": str(resolved_target),
            "target_source": target_source,
            "git_root": rev_parse.stdout.strip(),
            "commands": {
                "git_root": "git rev-parse --show-toplevel",
                "status": "git status --short --branch",
                "diff": _format_git_command(diff_command),
                "tracked_changed_files": _format_git_command(tracked_command),
                "untracked_files": "git ls-files --others --exclude-standard",
            },
            "returncodes": {
                "git_root": rev_parse.returncode,
                "status": status.returncode,
                "diff": diff.returncode,
                "tracked_changed_files": tracked.returncode,
                "untracked_files": untracked.returncode,
            },
            "changed_files": changed_files,
            "tracked_changed_files": tracked_files,
            "untracked_files": untracked_files,
            "network_actions_taken": 0,
            "external_mutations_taken": 0,
            "non_claims": [
                "Git snapshot export does not commit, push, fetch, pull, or mutate files.",
                "Untracked file contents are listed by path only and are not embedded in diff.patch.",
            ],
        },
    )


def _git_evidence_target(root: Path, packet: RunEvidencePacket) -> tuple[Path, str]:
    project = Storage(root / ".agent" / "state.db").get_registered_project(
        packet.run.project_id
    )
    if project is not None:
        return Path(project.root_path), "registered_project"
    return root, "system_root"


def _git_output_with_head_fallback(
    cwd: Path,
    primary_args: list[str],
    fallback_args: list[str],
) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    primary = _run_git(cwd, primary_args)
    if primary.returncode == 0:
        return primary, primary_args
    fallback = _run_git(cwd, fallback_args)
    if fallback.returncode == 0:
        return fallback, fallback_args
    return primary, primary_args


def _run_git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(
            args=["git", *args],
            returncode=127,
            stdout="",
            stderr=str(exc),
        )


def _format_git_command(args: list[str]) -> str:
    return "git " + " ".join(args)


def _split_git_path_lines(output: str) -> list[str]:
    return [line.strip() for line in output.splitlines() if line.strip()]


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
