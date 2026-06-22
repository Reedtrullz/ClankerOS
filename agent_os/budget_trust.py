from __future__ import annotations

from collections import Counter
from pathlib import Path

from agent_os.storage import BudgetTrustPostureReport, Storage, Task


REPORT_STATUS = "report_only"
BUDGET_STATE = "not_tracked"
TRUST_STATE = "not_tracked"
RISK_ORDER = ["critical", "high", "medium", "low", "unknown"]


def write_budget_trust_posture_report(
    root: Path,
) -> tuple[Path, BudgetTrustPostureReport]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    tasks = storage.list_all_tasks()
    risk_counts = _risk_counts(tasks)
    report_path = root / "docs" / "budget-trust-posture.md"
    relative_report_path = _relative_to_root(root, report_path)
    posture = storage.record_budget_trust_posture_report(
        status=REPORT_STATUS,
        task_count=len(tasks),
        risk_counts=risk_counts,
        budget_state=BUDGET_STATE,
        budget_summary=_budget_summary(),
        trust_state=TRUST_STATE,
        trust_summary=_trust_summary(tasks),
        report_path=relative_report_path,
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(render_budget_trust_posture_report(posture), encoding="utf-8")
    return report_path, posture


def render_budget_trust_posture_report(posture: BudgetTrustPostureReport) -> str:
    lines = [
        "# Budget And Trust Posture",
        "",
        f"- id: {posture.id}",
        f"- status: {posture.status}",
        f"- task_count: {posture.task_count}",
        f"- budget_state: {posture.budget_state}",
        f"- trust_state: {posture.trust_state}",
        f"- report_path: {posture.report_path}",
        f"- created_at: {posture.created_at}",
        "",
        "## Risk Levels",
        "",
    ]
    if posture.risk_counts:
        lines.extend(f"- {risk}: {count}" for risk, count in _ordered_counts(posture.risk_counts))
    else:
        lines.append("- none")

    lines.extend(["", "## Budget Posture", ""])
    lines.extend(
        f"- {key}: {value}"
        for key, value in posture.budget_summary.items()
    )
    lines.extend(["", "## Trust Posture", ""])
    lines.extend(
        f"- {key}: {value}"
        for key, value in posture.trust_summary.items()
    )
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local metadata.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not change task routing, approval decisions, worker claiming, retries, replay, CI, deploy, scheduler, or external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_budget_trust_posture_line(posture: BudgetTrustPostureReport) -> str:
    return (
        f"- {posture.id}: status={posture.status} tasks={posture.task_count} "
        f"budget_state={posture.budget_state} trust_state={posture.trust_state} "
        f"risk_counts={format_risk_counts(posture.risk_counts)} "
        f"report={posture.report_path}"
    )


def format_risk_counts(risk_counts: dict[str, int]) -> str:
    if not risk_counts:
        return "none"
    return ",".join(
        f"{risk}={count}"
        for risk, count in _ordered_counts(risk_counts)
    )


def _risk_counts(tasks: list[Task]) -> dict[str, int]:
    counts = Counter(task.risk_level or "unknown" for task in tasks)
    return dict(_ordered_counts(dict(counts)))


def _ordered_counts(counts: dict[str, int]) -> list[tuple[str, int]]:
    return sorted(
        counts.items(),
        key=lambda item: (
            RISK_ORDER.index(item[0]) if item[0] in RISK_ORDER else len(RISK_ORDER),
            item[0],
        ),
    )


def _budget_summary() -> dict[str, str]:
    return {
        "tracking": "not_tracked",
        "enforcement": "not_enabled",
        "cost_accounting": "not_enabled",
        "pause_on_exceed": "not_enabled",
    }


def _trust_summary(tasks: list[Task]) -> dict[str, str]:
    task_types = sorted({task.task_type for task in tasks})
    return {
        "tracking": "not_tracked",
        "promotion": "not_enabled",
        "routing_effect": "none",
        "task_types_seen": ",".join(task_types) or "none",
    }


def _relative_to_root(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root))
    except ValueError:
        return str(path)
