from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.storage import utc_now


ARTIFACT_HYGIENE_DIR = Path(".clanker/artifact-hygiene")
ARTIFACT_HYGIENE_JSON = ARTIFACT_HYGIENE_DIR / "latest.json"
ARTIFACT_HYGIENE_MARKDOWN = ARTIFACT_HYGIENE_DIR / "latest.md"

ARTIFACT_HYGIENE_CATEGORIES = [
    "tracked_intentional",
    "ignored_runtime_state",
    "unpromoted_proof",
    "generated_local_artifact",
    "visible_evidence_candidate",
    "unknown_needs_operator_review",
]

TRACKED_INTENTIONAL_PREFIXES = (
    ".clanker/delegations/",
    ".clanker/projects/",
    ".clanker/memory/",
)
TRACKED_INTENTIONAL_PATHS = {
    "status.md",
    "tasks.md",
    "plan.md",
    "docs/status.md",
    "docs/dashboard.md",
    "docs/self-hosting-check.md",
    "docs/next-iteration.md",
    "docs/OPERATING_SUMMARY.md",
}
UNPROMOTED_PROOF_PREFIXES = (
    ".clanker/ci-snapshots/",
    ".clanker/self-hosting-checks/",
)
GENERATED_PROOF_DOCS = {
    "docs/dashboard.md",
    "docs/status.md",
    "docs/self-hosting-check.md",
    "docs/next-iteration.md",
    "status.md",
}
GENERATED_LOCAL_PREFIXES = (
    ".clanker/app/",
    ".clanker/demo/",
    ".clanker/artifact-hygiene/",
    ".clanker/hosted-dashboard-export/",
    ".clanker/local-app/",
    ".clanker/smoke/",
    "runs/run_",
)
VISIBLE_EVIDENCE_PREFIXES = (
    ".clanker/delegations/",
    ".clanker/projects/",
)


@dataclass(frozen=True)
class ArtifactHygieneReport:
    root: Path
    payload: dict[str, Any]
    json_path: Path
    markdown_path: Path

    @property
    def counts(self) -> dict[str, int]:
        return dict(self.payload["counts"])


def write_artifact_hygiene_report(root: Path) -> ArtifactHygieneReport:
    root = root.resolve()
    categories = {category: [] for category in ARTIFACT_HYGIENE_CATEGORIES}
    tracked_paths = _git_lines(root, "ls-files")
    for path in tracked_paths:
        if _is_tracked_intentional(path):
            categories["tracked_intentional"].append(path)

    for status, path in _git_status_entries(root):
        if status == "!!":
            categories["ignored_runtime_state"].append(path)
            continue
        if _is_unpromoted_proof(path, status=status):
            categories["unpromoted_proof"].append(path)
        elif _is_generated_local_artifact(path):
            categories["generated_local_artifact"].append(path)
        elif status == "??" and _has_prefix(path, VISIBLE_EVIDENCE_PREFIXES):
            categories["visible_evidence_candidate"].append(path)
        elif status == "??":
            categories["unknown_needs_operator_review"].append(path)

    for key in categories:
        categories[key] = sorted(dict.fromkeys(categories[key]))

    counts = {key: len(categories[key]) for key in ARTIFACT_HYGIENE_CATEGORIES}
    payload = {
        "kind": "artifact_hygiene_report",
        "schema_version": 1,
        "generated_at": utc_now(),
        "categories": categories,
        "counts": counts,
        "deleted": 0,
        "gitignore_changes": 0,
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "non_claims": [
            "Report-only artifact classification.",
            "Does not delete files.",
            "Does not edit .gitignore.",
            "Does not promote evidence.",
            "Does not hide tracked .clanker evidence.",
        ],
    }

    report_dir = root / ARTIFACT_HYGIENE_DIR
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = root / ARTIFACT_HYGIENE_JSON
    markdown_path = root / ARTIFACT_HYGIENE_MARKDOWN
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    markdown_path.write_text(_render_markdown(payload), encoding="utf-8")
    return ArtifactHygieneReport(
        root=root,
        payload=payload,
        json_path=json_path,
        markdown_path=markdown_path,
    )


def render_artifact_hygiene_cli_lines(report: ArtifactHygieneReport) -> list[str]:
    lines = ["artifact_hygiene: written"]
    for category in ARTIFACT_HYGIENE_CATEGORIES:
        lines.append(f"{category}: {report.counts[category]}")
    lines.extend(
        [
            f"deleted: {report.payload['deleted']}",
            f"gitignore_changes: {report.payload['gitignore_changes']}",
            f"report_json: {_display_path(report.root, report.json_path)}",
            f"report_markdown: {_display_path(report.root, report.markdown_path)}",
            f"network_actions_taken: {report.payload['network_actions_taken']}",
            f"external_mutations_taken: {report.payload['external_mutations_taken']}",
        ]
    )
    return lines


def load_latest_artifact_hygiene_summary(root: Path) -> dict[str, Any] | None:
    path = root.resolve() / ARTIFACT_HYGIENE_JSON
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "status": "unreadable",
            "path": str(ARTIFACT_HYGIENE_JSON),
        }
    if not isinstance(payload, dict):
        return {
            "status": "unreadable",
            "path": str(ARTIFACT_HYGIENE_JSON),
        }
    return {
        "status": "available",
        "path": str(ARTIFACT_HYGIENE_JSON),
        "generated_at": payload.get("generated_at", "unknown"),
        "counts": payload.get("counts", {}),
        "deleted": payload.get("deleted", "unknown"),
        "gitignore_changes": payload.get("gitignore_changes", "unknown"),
        "non_claims": payload.get("non_claims", []),
    }


def render_artifact_hygiene_dashboard_lines(root: Path) -> list[str]:
    summary = load_latest_artifact_hygiene_summary(root)
    lines = ["### Artifact Hygiene", ""]
    if summary is None:
        lines.extend(
            [
                "- Report status: `missing`",
                "- Next action: run `python3 -m agent_os.cli artifact-hygiene`.",
                "- Deleted files: `0`",
                "- Gitignore changes: `0`",
                "",
            ]
        )
        return lines
    lines.extend(
        [
            f"- Report status: `{summary['status']}`",
            f"- Report path: `{summary['path']}`",
            f"- Generated at: `{summary.get('generated_at', 'unknown')}`",
        ]
    )
    counts = summary.get("counts", {})
    if isinstance(counts, dict):
        for category in ARTIFACT_HYGIENE_CATEGORIES:
            lines.append(f"- {category}: `{counts.get(category, 0)}`")
    lines.extend(
        [
            f"- Deleted files: `{summary.get('deleted', 0)}`",
            f"- Gitignore changes: `{summary.get('gitignore_changes', 0)}`",
            "",
        ]
    )
    return lines


def _render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Artifact Hygiene Report",
        "",
        f"- Generated at: `{payload['generated_at']}`",
        "- Deleted files: `0`",
        "- Gitignore changes: `0`",
        "- Network actions taken: `0`",
        "- External mutations taken: `0`",
        "",
    ]
    categories = payload["categories"]
    for category in ARTIFACT_HYGIENE_CATEGORIES:
        paths = categories[category]
        lines.extend([f"## {category}", "", f"- Count: `{len(paths)}`"])
        if paths:
            lines.extend(f"- `{path}`" for path in paths)
        else:
            lines.append("- none")
        lines.append("")
    lines.extend(["## Non-Claims", ""])
    lines.extend(f"- {claim}" for claim in payload["non_claims"])
    lines.append("")
    return "\n".join(lines)


def _git_lines(root: Path, *args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _git_status_entries(root: Path) -> list[tuple[str, str]]:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--ignored", "-uall"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    entries: list[tuple[str, str]] = []
    for raw_line in result.stdout.splitlines():
        if not raw_line:
            continue
        status = raw_line[:2]
        path = raw_line[3:].strip()
        if " -> " in path:
            path = path.rsplit(" -> ", 1)[1]
        if path:
            entries.append((status, path))
    return entries


def _is_tracked_intentional(path: str) -> bool:
    return path in TRACKED_INTENTIONAL_PATHS or _has_prefix(
        path,
        TRACKED_INTENTIONAL_PREFIXES,
    )


def _is_unpromoted_proof(path: str, *, status: str) -> bool:
    if _has_prefix(path, UNPROMOTED_PROOF_PREFIXES):
        return True
    return path in GENERATED_PROOF_DOCS and status != "!!"


def _is_generated_local_artifact(path: str) -> bool:
    if _has_prefix(path, GENERATED_LOCAL_PREFIXES):
        return True
    return "smoke-artifacts/" in path or "demo-artifacts/" in path


def _has_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
