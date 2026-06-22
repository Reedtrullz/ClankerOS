from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.ids import new_id
from agent_os.runtime import write_runtime_capability_matrix
from agent_os.storage import Incident, Storage, Task, utc_now


@dataclass(frozen=True)
class RunResult:
    goal_id: str
    run_id: str
    status: str
    activity_path: Path
    events_path: Path
    summary_path: Path
    learning_path: Path
    eval_candidate_path: Path


class AgentSystem:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.storage = Storage(self.root / ".agent" / "state.db")
        self.worker_id = "local-worker-1"

    def initialize(self) -> None:
        self.storage.initialize()
        for directory in [
            self.root / "docs",
            self.root / "runs",
            self.root / "evals" / "candidates",
            self.root / "evals" / "results",
            self.root / "projects" / "bootstrap" / "artifacts",
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        self._ensure_text(
            self.root / "memory.md",
            "# Memory\n\n## Hot Memory\n\n- Active milestone: Milestone 1 local closed loop.\n",
        )
        self._ensure_text(
            self.root / "knowledge.md",
            "# Knowledge\n\n## Architecture Decisions\n\n- Start local-first.\n",
        )
        self._ensure_text(
            self.root / "projects" / "bootstrap" / "knowledge.md",
            "# Bootstrap Knowledge\n\nThe first milestone proves the closed loop.\n",
        )
        self._ensure_text(
            self.root / "projects" / "bootstrap" / "status.md",
            "# Bootstrap Status\n\nMilestone 1 is in progress.\n",
        )
        write_runtime_capability_matrix(self.root)

    def run_goal(self, project_id: str, description: str) -> RunResult:
        self.initialize()
        goal_id = self.storage.create_goal(project_id, description)
        run_id = self.storage.create_run(goal_id, project_id, self.root / "runs")
        run_dir = self.root / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        activity_path = run_dir / "activity.md"
        events_path = run_dir / "events.jsonl"
        summary_path = run_dir / "summary.md"
        activity_path.write_text(f"# Activity For {run_id}\n\n", encoding="utf-8")
        events_path.write_text("", encoding="utf-8")

        self._emit(
            run_id,
            goal_id,
            None,
            "goal.accepted",
            f"accepted goal for project {project_id}",
            {"description": description},
            activity_path,
            events_path,
        )

        first_task_id, learning_task_id = self._decompose_goal(
            goal_id,
            project_id,
            description,
            run_id,
            activity_path,
            events_path,
        )

        learning_path = self.root / "projects" / project_id / "artifacts" / run_id / "learning.md"
        eval_candidate_path = self.root / "evals" / "candidates" / f"{run_id}-closed-loop.json"

        while True:
            task = self.storage.claim_next_task(
                worker_id=self.worker_id,
                skill_tags=["local-files"],
            )
            if task is None:
                break
            self._emit(
                run_id,
                goal_id,
                task.id,
                "task.claimed",
                f"claimed task {task.id} ({task.task_type})",
                {"worker_id": self.worker_id},
                activity_path,
                events_path,
            )
            self.storage.set_task_status(task.id, "running")
            artifacts = self._execute_task(task, run_id, description, learning_task_id)
            self.storage.set_task_status(task.id, "verifying")
            evidence = self._verify_task(task, artifacts, description, run_id)

            if evidence["passed"]:
                self.storage.mark_task_completed(
                    task.id,
                    evidence=evidence,
                    artifacts=[str(path) for path in artifacts],
                )
                self._emit(
                    run_id,
                    goal_id,
                    task.id,
                    "task.verified",
                    f"verified task {task.id}",
                    evidence,
                    activity_path,
                    events_path,
                )
            else:
                artifact_paths = [str(path) for path in artifacts]
                self.storage.mark_task_failed(
                    task.id,
                    evidence=evidence,
                    artifacts=artifact_paths,
                )
                incident_id = self._record_verification_incident(
                    run_id=run_id,
                    goal_id=goal_id,
                    task=task,
                    evidence=evidence,
                    artifacts=artifact_paths,
                )
                self._emit(
                    run_id,
                    goal_id,
                    task.id,
                    "incident.opened",
                    f"opened incident {incident_id} for failed verification",
                    {"incident_id": incident_id, "incident_type": "verification_failed"},
                    activity_path,
                    events_path,
                )
                self._emit(
                    run_id,
                    goal_id,
                    task.id,
                    "task.failed",
                    f"failed verification for task {task.id}",
                    {"incident_id": incident_id, "evidence": evidence},
                    activity_path,
                    events_path,
                )
                break

        tasks = self.storage.list_tasks(goal_id)
        if tasks and all(task.status == "completed" for task in tasks):
            status = "completed"
        elif any(task.status == "waiting_approval" for task in tasks):
            status = "waiting_approval"
        else:
            status = "failed"
        self.storage.complete_run(run_id, status)
        self.storage.set_goal_status(goal_id, status)
        self._write_summary(summary_path, project_id, description, run_id, goal_id, tasks, status)
        self._mirror_project_status(project_id, run_id, goal_id, status, summary_path)
        self._emit(
            run_id,
            goal_id,
            None,
            "run.completed",
            f"run {run_id} completed with status {status}",
            {"summary_path": str(summary_path)},
            activity_path,
            events_path,
        )

        return RunResult(
            goal_id=goal_id,
            run_id=run_id,
            status=status,
            activity_path=activity_path,
            events_path=events_path,
            summary_path=summary_path,
            learning_path=learning_path,
            eval_candidate_path=eval_candidate_path,
        )

    def detect_stuck_tasks(
        self,
        *,
        timeout_seconds: int,
        now: str | None = None,
    ) -> list[str]:
        self.initialize()
        incident_ids = []
        for task in self.storage.list_stale_active_tasks(
            timeout_seconds=timeout_seconds,
            now=now,
        ):
            detected_at = now or utc_now()
            last_activity_at = task.claimed_at or task.updated_at or task.created_at
            evidence = {
                "passed": False,
                "method": "stuck_task_timeout",
                "timeout_seconds": timeout_seconds,
                "detected_at": detected_at,
                "last_activity_at": last_activity_at,
                "task_status": task.status,
                "owner": task.owner,
            }
            run_id = task.run_id or self.storage.latest_run_id_for_goal(task.goal_id) or "run_unknown"
            incident_id = self._record_stuck_task_incident(
                run_id=run_id,
                task=task,
                evidence=evidence,
            )
            incident = self.storage.list_recent_incidents(limit=1)[0]
            self.storage.mark_task_blocked(
                task.id,
                evidence=evidence,
                artifacts=[incident.evidence_path] if incident.evidence_path else [],
            )
            self.storage.record_event(
                run_id=run_id,
                goal_id=task.goal_id,
                task_id=task.id,
                event_type="incident.opened",
                message=f"opened incident {incident_id} for stuck task",
                payload={"incident_id": incident_id, "incident_type": "task_stuck"},
            )
            incident_ids.append(incident_id)
        return incident_ids

    def resolve_incident(
        self,
        incident_id: str,
        *,
        resolved_by: str,
        resolution_note: str,
    ) -> Incident:
        self.initialize()
        incident = self.storage.get_incident(incident_id)
        if incident.status == "resolved":
            return incident

        resolved_at = utc_now()
        if incident.evidence_path:
            resolution_path = Path(incident.evidence_path).with_name(
                f"{incident.id}-resolution.json"
            )
        else:
            resolution_path = (
                self.root / "runs" / incident.run_id / "incidents" / f"{incident.id}-resolution.json"
            )
        resolution_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "id": incident.id,
            "project_id": incident.project_id,
            "run_id": incident.run_id,
            "goal_id": incident.goal_id,
            "task_id": incident.task_id,
            "task_type": incident.task_type,
            "incident_type": incident.incident_type,
            "status": "resolved",
            "resolved_at": resolved_at,
            "resolved_by": resolved_by,
            "resolution_note": resolution_note,
            "original_evidence_path": incident.evidence_path,
        }
        resolution_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        resolved = self.storage.resolve_incident(
            incident.id,
            resolved_by=resolved_by,
            resolution_note=resolution_note,
            resolution_evidence_path=str(resolution_path),
            resolved_at=resolved_at,
        )
        run_dir = self.root / "runs" / incident.run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        self._emit_for_current_paths(
            incident.run_id,
            incident.goal_id,
            incident.task_id,
            "incident.resolved",
            f"resolved incident {incident.id}",
            {
                "incident_id": incident.id,
                "resolved_by": resolved_by,
                "resolution_evidence_path": str(resolution_path),
            },
        )
        return resolved

    def _decompose_goal(
        self,
        goal_id: str,
        project_id: str,
        description: str,
        run_id: str,
        activity_path: Path,
        events_path: Path,
    ) -> tuple[str, str]:
        artifact_path = (
            self.root
            / "projects"
            / project_id
            / "artifacts"
            / run_id
            / "goal-artifact.md"
        )
        first_task_id = self.storage.create_task(
            goal_id=goal_id,
            run_id=run_id,
            project_id=project_id,
            task_type="write_goal_artifact",
            description="Write a durable artifact proving goal intake and execution.",
            verification_plan={
                "type": "file_contains",
                "path": str(artifact_path),
                "contains": [description],
            },
        )
        self._emit(
            run_id,
            goal_id,
            first_task_id,
            "task.created",
            f"created task {first_task_id} (write_goal_artifact)",
            {"depends_on": []},
            activity_path,
            events_path,
        )

        learning_path = self.root / "projects" / project_id / "artifacts" / run_id / "learning.md"
        second_task_id = self.storage.create_task(
            goal_id=goal_id,
            run_id=run_id,
            project_id=project_id,
            task_type="record_learning",
            description="Record one learning and one eval candidate from the run.",
            verification_plan={
                "type": "learning_recorded",
                "path": str(learning_path),
                "contains": [run_id],
            },
            depends_on=[first_task_id],
        )
        self._emit(
            run_id,
            goal_id,
            second_task_id,
            "task.created",
            f"created task {second_task_id} (record_learning)",
            {"depends_on": [first_task_id]},
            activity_path,
            events_path,
        )
        return first_task_id, second_task_id

    def _execute_task(
        self,
        task: Task,
        run_id: str,
        goal_description: str,
        learning_task_id: str,
    ) -> list[Path]:
        if task.task_type == "write_goal_artifact":
            return [self._write_goal_artifact(task, run_id, goal_description)]
        if task.task_type == "record_learning":
            return self._record_learning(task, run_id, goal_description, learning_task_id)
        raise ValueError(f"Unsupported task type: {task.task_type}")

    def _write_goal_artifact(self, task: Task, run_id: str, goal_description: str) -> Path:
        artifact_path = Path(task.verification_plan["path"])
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text(
            "\n".join(
                [
                    f"# Goal Artifact For {run_id}",
                    "",
                    f"- Task: {task.id}",
                    f"- Goal: {goal_description}",
                    "- Definition of Done: artifact exists, names the task, and contains the goal.",
                    "- Evidence Method: deterministic file content verification.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return artifact_path

    def _record_learning(
        self,
        task: Task,
        run_id: str,
        goal_description: str,
        learning_task_id: str,
    ) -> list[Path]:
        learning_summary = (
            f"Run {run_id} showed that the first closed loop can be verified through "
            "file evidence before expanding to broader domains."
        )
        project_dir = self.root / "projects" / task.project_id
        artifact_dir = project_dir / "artifacts" / run_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        learning_path = artifact_dir / "learning.md"
        learning_path.write_text(
            "\n".join(
                [
                    f"# Learning For {run_id}",
                    "",
                    f"- Source task: {learning_task_id}",
                    f"- Goal: {goal_description}",
                    f"- Learning: {learning_summary}",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        self._append(
            self.root / "memory.md",
            "\n".join(
                [
                    "",
                    f"## Run {run_id}",
                    "",
                    f"- Goal: {goal_description}",
                    f"- Learning: {learning_summary}",
                    "",
                ]
            ),
        )
        self._append(
            project_dir / "knowledge.md",
            "\n".join(
                [
                    "",
                    f"## Learning {run_id}",
                    "",
                    f"- Learning: {learning_summary}",
                    "",
                ]
            ),
        )

        eval_candidate_path = self.root / "evals" / "candidates" / f"{run_id}-closed-loop.json"
        eval_reason = "The local closed loop is the core regression boundary for future changes."
        eval_candidate_path.parent.mkdir(parents=True, exist_ok=True)
        eval_candidate_path.write_text(
            json.dumps(
                {
                    "source_run_id": run_id,
                    "suggested_eval": "closed_loop_regression",
                    "reason": eval_reason,
                    "created_at": utc_now(),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        self.storage.record_learning(run_id, task.project_id, learning_summary, str(learning_path))
        self._emit_for_current_paths(
            run_id,
            task.goal_id,
            task.id,
            "learning.recorded",
            f"recorded learning for {run_id}",
            {"learning_path": str(learning_path), "eval_candidate_path": str(eval_candidate_path)},
        )
        return [learning_path, eval_candidate_path]

    def _verify_task(
        self,
        task: Task,
        artifacts: list[Path],
        goal_description: str,
        run_id: str,
    ) -> dict[str, Any]:
        if task.task_type == "write_goal_artifact":
            path = artifacts[0]
            text = path.read_text(encoding="utf-8") if path.exists() else ""
            checks = {
                "exists": path.exists(),
                "contains_goal": goal_description in text,
                "contains_task_id": task.id in text,
            }
            return {
                "passed": all(checks.values()),
                "method": "file_contains",
                "path": str(path),
                "checks": checks,
                "verified_at": utc_now(),
            }

        if task.task_type == "record_learning":
            learning_path, eval_candidate_path = artifacts
            memory_text = (self.root / "memory.md").read_text(encoding="utf-8")
            knowledge_text = (
                self.root / "projects" / task.project_id / "knowledge.md"
            ).read_text(encoding="utf-8")
            checks = {
                "learning_file_exists": learning_path.exists(),
                "eval_candidate_exists": eval_candidate_path.exists(),
                "memory_mentions_run": run_id in memory_text,
                "knowledge_mentions_run": run_id in knowledge_text,
            }
            return {
                "passed": all(checks.values()),
                "method": "learning_recorded",
                "path": str(learning_path),
                "checks": checks,
                "verified_at": utc_now(),
            }

        return {
            "passed": False,
            "method": "unsupported_task_type",
            "task_type": task.task_type,
            "verified_at": utc_now(),
        }

    def _record_verification_incident(
        self,
        *,
        run_id: str,
        goal_id: str,
        task: Task,
        evidence: dict[str, Any],
        artifacts: list[str],
    ) -> str:
        incident_id = new_id("incident")
        failed_checks = [
            name
            for name, passed in evidence.get("checks", {}).items()
            if passed is False
        ]
        evidence_path = self.root / "runs" / run_id / "incidents" / f"{incident_id}.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "id": incident_id,
            "project_id": task.project_id,
            "run_id": run_id,
            "goal_id": goal_id,
            "task_id": task.id,
            "task_type": task.task_type,
            "incident_type": "verification_failed",
            "severity": "high",
            "status": "open",
            "summary": f"Task {task.id} failed verification during run {run_id}.",
            "failure_class": "bad verification",
            "verification_method": evidence.get("method"),
            "verification_path": evidence.get("path"),
            "failed_checks": failed_checks,
            "evidence": evidence,
            "artifacts": artifacts,
            "created_at": utc_now(),
        }
        evidence_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.storage.record_incident(
            incident_id=incident_id,
            project_id=task.project_id,
            run_id=run_id,
            goal_id=goal_id,
            task_id=task.id,
            task_type=task.task_type,
            incident_type="verification_failed",
            severity="high",
            status="open",
            summary=payload["summary"],
            failure_class="bad verification",
            verification_method=evidence.get("method"),
            verification_path=evidence.get("path"),
            failed_checks=failed_checks,
            evidence=evidence,
            artifacts=artifacts,
            evidence_path=str(evidence_path),
        )
        self._write_eval_candidate(
            source_type="incident",
            source_id=incident_id,
            suggested_eval=f"verification_failed_{task.task_type}_regression",
            reason=(
                "A deterministic verifier failed; add an eval that reproduces "
                "the failed checks before changing the verifier or executor."
            ),
            payload={
                "source_incident_id": incident_id,
                "source_run_id": run_id,
                "source_goal_id": goal_id,
                "source_task_id": task.id,
                "gap_type": "verification_failed",
                "task_type": task.task_type,
                "failed_checks": failed_checks,
                "verification_method": evidence.get("method"),
                "verification_path": evidence.get("path"),
            },
        )
        return incident_id

    def _record_stuck_task_incident(
        self,
        *,
        run_id: str,
        task: Task,
        evidence: dict[str, Any],
    ) -> str:
        incident_id = new_id("incident")
        evidence_path = self.root / "runs" / run_id / "incidents" / f"{incident_id}.json"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        summary = f"Task {task.id} exceeded its active timeout during run {run_id}."
        payload = {
            "id": incident_id,
            "project_id": task.project_id,
            "run_id": run_id,
            "goal_id": task.goal_id,
            "task_id": task.id,
            "task_type": task.task_type,
            "incident_type": "task_stuck",
            "severity": "high",
            "status": "open",
            "summary": summary,
            "failure_class": "stuck task",
            "failed_checks": ["active_timeout"],
            "evidence": evidence,
            "artifacts": [],
            "created_at": utc_now(),
        }
        evidence_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.storage.record_incident(
            incident_id=incident_id,
            project_id=task.project_id,
            run_id=run_id,
            goal_id=task.goal_id,
            task_id=task.id,
            task_type=task.task_type,
            incident_type="task_stuck",
            severity="high",
            status="open",
            summary=summary,
            failure_class="stuck task",
            verification_method=evidence["method"],
            verification_path=None,
            failed_checks=["active_timeout"],
            evidence=evidence,
            artifacts=[],
            evidence_path=str(evidence_path),
        )
        self._write_eval_candidate(
            source_type="incident",
            source_id=incident_id,
            suggested_eval=f"task_stuck_{task.task_type}_regression",
            reason=(
                "A workflow gap was discovered by stuck-task detection; add an "
                "eval that proves timeout detection and reporting stay intact."
            ),
            payload={
                "source_incident_id": incident_id,
                "source_run_id": run_id,
                "source_goal_id": task.goal_id,
                "source_task_id": task.id,
                "gap_type": "task_stuck",
                "task_type": task.task_type,
                "failed_checks": ["active_timeout"],
                "timeout_seconds": evidence.get("timeout_seconds"),
                "last_activity_at": evidence.get("last_activity_at"),
            },
        )
        return incident_id

    def _write_eval_candidate(
        self,
        *,
        source_type: str,
        source_id: str,
        suggested_eval: str,
        reason: str,
        payload: dict[str, Any],
    ) -> Path:
        candidate_path = self.root / "evals" / "candidates" / f"{source_id}-eval-candidate.json"
        candidate_path.parent.mkdir(parents=True, exist_ok=True)
        candidate_payload = {
            "source_type": source_type,
            "source_id": source_id,
            "suggested_eval": suggested_eval,
            "reason": reason,
            "created_at": utc_now(),
            **payload,
        }
        candidate_path.write_text(
            json.dumps(candidate_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.storage.record_eval_candidate(
            source_type=source_type,
            source_id=source_id,
            suggested_eval=suggested_eval,
            reason=reason,
            candidate_path=self._relative_to_root(candidate_path),
        )
        return candidate_path

    def _write_summary(
        self,
        summary_path: Path,
        project_id: str,
        goal_description: str,
        run_id: str,
        goal_id: str,
        tasks: list[Task],
        status: str,
    ) -> None:
        lines = [
            f"# Run Summary {run_id}",
            "",
            f"- Project: {project_id}",
            f"- Goal ID: {goal_id}",
            f"- Goal: {goal_description}",
            f"- Status: {status}",
            "",
            "## Tasks",
            "",
        ]
        for task in tasks:
            lines.append(f"- {task.id}: {task.task_type} -> {task.status}")
        lines.append("")
        summary_path.write_text("\n".join(lines), encoding="utf-8")

    def _mirror_project_status(
        self,
        project_id: str,
        run_id: str,
        goal_id: str,
        status: str,
        summary_path: Path,
    ) -> None:
        project_status = self.root / "projects" / project_id / "status.md"
        self._append(
            project_status,
            "\n".join(
                [
                    "",
                    f"## Run {run_id}",
                    "",
                    f"- Goal ID: {goal_id}",
                    f"- Status: {status}",
                    f"- Summary: {summary_path}",
                    "",
                ]
            ),
        )

    def _emit(
        self,
        run_id: str,
        goal_id: str | None,
        task_id: str | None,
        event_type: str,
        message: str,
        payload: dict[str, Any],
        activity_path: Path,
        events_path: Path,
    ) -> None:
        self.storage.record_event(
            run_id=run_id,
            goal_id=goal_id,
            task_id=task_id,
            event_type=event_type,
            message=message,
            payload=payload,
        )
        event = {
            "created_at": utc_now(),
            "run_id": run_id,
            "goal_id": goal_id,
            "task_id": task_id,
            "event_type": event_type,
            "message": message,
            "payload": payload,
        }
        with events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        with activity_path.open("a", encoding="utf-8") as handle:
            handle.write(f"- {event['created_at']} - {message}\n")

    def _emit_for_current_paths(
        self,
        run_id: str,
        goal_id: str | None,
        task_id: str | None,
        event_type: str,
        message: str,
        payload: dict[str, Any],
    ) -> None:
        run_dir = self.root / "runs" / run_id
        self._emit(
            run_id,
            goal_id,
            task_id,
            event_type,
            message,
            payload,
            run_dir / "activity.md",
            run_dir / "events.jsonl",
        )

    def _ensure_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(text, encoding="utf-8")

    def _append(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(text)

    def _relative_to_root(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.root))
        except ValueError:
            return str(path)
