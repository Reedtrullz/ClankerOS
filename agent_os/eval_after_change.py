from __future__ import annotations

import json
from pathlib import Path

from agent_os.eval import run_first_milestone_eval
from agent_os.storage import EvalAfterChangeCheck, Storage


def run_eval_after_change(
    root: Path,
    *,
    change_summary: str,
    changed_paths: list[str],
) -> tuple[Path, EvalAfterChangeCheck]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    eval_result = run_first_milestone_eval(root)
    result_path = _relative_to_root(root, eval_result.result_path)
    payload = json.loads(eval_result.result_path.read_text(encoding="utf-8"))
    run_id = payload.get("run_id", "unknown")
    status = "pass" if eval_result.status == "pass" else "fail"
    report_path = root / "docs" / "eval-after-change.md"
    relative_report_path = _relative_to_root(root, report_path)
    command = _render_command(change_summary, changed_paths)

    check = storage.record_eval_after_change_check(
        change_summary=change_summary,
        changed_paths=changed_paths,
        eval_names=[eval_result.name],
        status=status,
        result_paths=[result_path],
        run_ids=[run_id],
        report_path=relative_report_path,
        command=command,
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_eval_after_change_report(check), encoding="utf-8")
    return report_path, check


def render_eval_after_change_report(check: EvalAfterChangeCheck) -> str:
    lines = [
        "# Eval After Change",
        "",
        f"- id: {check.id}",
        f"- status: {check.status}",
        f"- change: {check.change_summary}",
        f"- changed_paths: {','.join(check.changed_paths) or 'none'}",
        f"- evals: {','.join(check.eval_names)}",
        f"- result_paths: {','.join(check.result_paths)}",
        f"- run_ids: {','.join(check.run_ids)}",
        f"- command: {check.command}",
        f"- completed_at: {check.completed_at}",
        "",
    ]
    return "\n".join(lines)


def render_eval_after_change_line(check: EvalAfterChangeCheck) -> str:
    return (
        f"- {check.id}: status={check.status} change={check.change_summary} "
        f"files={','.join(check.changed_paths) or 'none'} "
        f"evals={','.join(check.eval_names)} runs={','.join(check.run_ids)} "
        f"results={','.join(check.result_paths)} report={check.report_path}"
    )


def _render_command(change_summary: str, changed_paths: list[str]) -> str:
    parts = [
        "python3 -m agent_os.cli eval-after-change",
        f"--change {json.dumps(change_summary)}",
    ]
    parts.extend(f"--file {json.dumps(path)}" for path in changed_paths)
    return " ".join(parts)


def _relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
