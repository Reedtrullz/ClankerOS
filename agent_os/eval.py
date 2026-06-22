from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from agent_os.engine import AgentSystem
from agent_os.storage import Storage, utc_now


@dataclass(frozen=True)
class EvalResult:
    name: str
    status: str
    result_path: Path
    checks: dict[str, int | bool | str]


def run_first_milestone_eval(root: Path) -> EvalResult:
    system = AgentSystem(root)
    run_result = system.run_goal(
        project_id="bootstrap",
        description="Eval: prove first milestone closed loop",
    )
    storage = Storage(root.resolve() / ".agent" / "state.db")
    tasks = storage.list_tasks(run_result.goal_id)
    checks: dict[str, int | bool | str] = {
        "run_status": run_result.status,
        "tasks_completed": sum(task.status == "completed" for task in tasks),
        "activity_exists": run_result.activity_path.exists(),
        "events_exists": run_result.events_path.exists(),
        "learning_exists": run_result.learning_path.exists(),
        "eval_candidate_exists": run_result.eval_candidate_path.exists(),
    }
    status = "pass" if (
        checks["run_status"] == "completed"
        and checks["tasks_completed"] == 2
        and checks["activity_exists"]
        and checks["events_exists"]
        and checks["learning_exists"]
        and checks["eval_candidate_exists"]
    ) else "fail"

    result_path = root.resolve() / "evals" / "results" / "first_milestone_closed_loop.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": "first_milestone_closed_loop",
        "status": status,
        "checks": checks,
        "run_id": run_result.run_id,
        "created_at": utc_now(),
    }
    result_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    storage.record_eval_result("first_milestone_closed_loop", status, payload)
    return EvalResult(
        name="first_milestone_closed_loop",
        status=status,
        result_path=result_path,
        checks=checks,
    )
