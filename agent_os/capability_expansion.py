from __future__ import annotations

from pathlib import Path

from agent_os.storage import CapabilityExpansionLedger, Storage


REPORT_STATUS = "report_only"
REPORT_PATH = "docs/capability-expansion-ledger.md"
APPROVAL_BOUNDARY = "explicit_operator_approval_required"
DEFERRED_STATE = "deferred"
NO_ROUTING_EFFECT = "none"

CAPABILITY_SPECS = [
    {
        "capability": "hosted_dashboard",
        "state": DEFERRED_STATE,
        "required_evidence": "authenticated read-only deployment plan and local dashboard parity proof",
        "next_proof": "hosted_dashboard_design_review",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "remote_workers",
        "state": DEFERRED_STATE,
        "required_evidence": "claim isolation, idempotent work handoff, and worker lease recovery proof",
        "next_proof": "remote_worker_contract_review",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "autonomous_scheduling",
        "state": DEFERRED_STATE,
        "required_evidence": "operator-approved schedule policy, dry-run queue impact, and pause control proof",
        "next_proof": "scheduler_policy_dry_run",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "browser_desktop_adapters",
        "state": DEFERRED_STATE,
        "required_evidence": "adapter permission model, transcript capture, and no-secret logging proof",
        "next_proof": "adapter_permission_boundary_review",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "ci_deploy_proof",
        "state": DEFERRED_STATE,
        "required_evidence": "CI run identifiers, deploy target contract, rollback evidence, and non-live proof labels",
        "next_proof": "ci_deploy_evidence_contract",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "budget_enforcement",
        "state": DEFERRED_STATE,
        "required_evidence": "budget source of truth, hard-stop behavior, and operator override audit proof",
        "next_proof": "budget_policy_simulation",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "trust_promotion",
        "state": DEFERRED_STATE,
        "required_evidence": "promotion criteria, demotion path, reviewer evidence, and routing simulation proof",
        "next_proof": "trust_policy_simulation",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "automatic_retries",
        "state": DEFERRED_STATE,
        "required_evidence": "retry classification, attempt budget, replay safety, and incident linkage proof",
        "next_proof": "retry_policy_dry_run",
        "routing_effect": NO_ROUTING_EFFECT,
    },
    {
        "capability": "real_cost_tracking",
        "state": DEFERRED_STATE,
        "required_evidence": "meter source, per-run attribution, budget reconciliation, and redaction proof",
        "next_proof": "cost_accounting_source_review",
        "routing_effect": NO_ROUTING_EFFECT,
    },
]


def write_capability_expansion_ledger(
    root: Path,
) -> tuple[Path, CapabilityExpansionLedger]:
    root = root.resolve()
    storage = Storage(root / ".agent" / "state.db")
    storage.initialize()

    capabilities = _capability_entries()
    ledger = storage.record_capability_expansion_ledger(
        status=REPORT_STATUS,
        capability_count=len(capabilities),
        ready_count=_count_state(capabilities, "ready"),
        deferred_count=_count_state(capabilities, DEFERRED_STATE),
        approval_boundary=APPROVAL_BOUNDARY,
        capabilities=capabilities,
        report_path=REPORT_PATH,
    )
    report_path = root / ledger.report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        render_capability_expansion_ledger_report(ledger),
        encoding="utf-8",
    )
    return report_path, ledger


def render_capability_expansion_ledger_report(
    ledger: CapabilityExpansionLedger,
) -> str:
    lines = [
        "# Capability Expansion Ledger",
        "",
        f"- id: {ledger.id}",
        f"- status: {ledger.status}",
        f"- capability_count: {ledger.capability_count}",
        f"- ready: {ledger.ready_count}",
        f"- deferred: {ledger.deferred_count}",
        f"- approval_boundary: {ledger.approval_boundary}",
        f"- report_path: {ledger.report_path}",
        f"- created_at: {ledger.created_at}",
        "",
        "## Capabilities",
        "",
    ]
    lines.extend(render_capability_entry_line(entry) for entry in ledger.capabilities)
    lines.extend(
        [
            "",
            "## Non-Claims",
            "",
            "- Report-only local ledger.",
            "- Does not enable hosted dashboard.",
            "- Does not start remote workers.",
            "- Does not schedule autonomous work.",
            "- Does not operate browser or desktop adapters.",
            "- Does not run CI or deploys.",
            "- Does not enforce budgets.",
            "- Does not promote trust.",
            "- Does not retry or replay work.",
            "- Does not track real spend or mutate external systems.",
            "",
        ]
    )
    return "\n".join(lines)


def render_capability_expansion_ledger_line(
    ledger: CapabilityExpansionLedger,
) -> str:
    return (
        f"- {ledger.id}: status={ledger.status} capabilities={ledger.capability_count} "
        f"ready={ledger.ready_count} deferred={ledger.deferred_count} "
        f"approval_boundary={ledger.approval_boundary} report={ledger.report_path}"
    )


def render_capability_entry_line(entry: dict[str, str]) -> str:
    return (
        f"- {entry['capability']}: state={entry['state']} "
        f"next_proof={entry['next_proof']} "
        f"routing_effect={entry['routing_effect']} "
        f"approval_boundary={entry['approval_boundary']}"
    )


def _capability_entries() -> list[dict[str, str]]:
    return [
        {
            **spec,
            "approval_boundary": APPROVAL_BOUNDARY,
        }
        for spec in CAPABILITY_SPECS
    ]


def _count_state(capabilities: list[dict[str, str]], state: str) -> int:
    return sum(1 for capability in capabilities if capability["state"] == state)
