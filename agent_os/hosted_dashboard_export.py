from __future__ import annotations

import hashlib
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.artifact_hygiene import load_latest_artifact_hygiene_summary
from agent_os.proof_surface import build_proof_surface_state
from agent_os.storage import utc_now


HOSTED_DASHBOARD_EXPORT_DIR = Path(".clanker/hosted-dashboard-export")
HOSTED_DASHBOARD_INDEX = HOSTED_DASHBOARD_EXPORT_DIR / "index.html"
HOSTED_DASHBOARD_MANIFEST = HOSTED_DASHBOARD_EXPORT_DIR / "manifest.json"

HOSTED_DASHBOARD_NON_CLAIMS = [
    "Static local read-only export only.",
    "Does not start a server.",
    "Does not deploy.",
    "Does not call GitHub.",
    "Does not call providers.",
    "Does not create remote workers.",
    "Does not schedule work.",
    "Does not perform browser or desktop automation.",
    "Does not mutate external systems.",
]


@dataclass(frozen=True)
class HostedDashboardExportResult:
    root: Path
    output_dir: Path
    index_path: Path
    manifest_path: Path
    manifest: dict[str, Any]


def write_hosted_dashboard_export(
    root: Path,
    *,
    output_dir: Path | None = None,
) -> HostedDashboardExportResult:
    root = root.resolve()
    export_dir = (root / HOSTED_DASHBOARD_EXPORT_DIR) if output_dir is None else output_dir
    export_dir.mkdir(parents=True, exist_ok=True)
    index_path = export_dir / "index.html"
    manifest_path = export_dir / "manifest.json"

    dashboard = _snapshot(root, Path("docs/dashboard.md"))
    status = {
        "status_md": _snapshot(root, Path("status.md")),
        "docs_status_md": _snapshot(root, Path("docs/status.md")),
    }
    proof_surface = build_proof_surface_state(root).to_dict()
    artifact_hygiene = load_latest_artifact_hygiene_summary(root) or {
        "status": "missing",
        "path": str(Path(".clanker/artifact-hygiene/latest.json")),
        "counts": {},
        "deleted": 0,
        "gitignore_changes": 0,
    }
    generated_at = utc_now()
    manifest = {
        "kind": "hosted_dashboard_export",
        "schema_version": 1,
        "generated_at": generated_at,
        "dashboard_snapshot": dashboard,
        "status_summary": status,
        "proof_surface": proof_surface,
        "artifact_hygiene": artifact_hygiene,
        "output": {
            "index_html": _display_path(root, index_path),
            "manifest_json": _display_path(root, manifest_path),
        },
        "network_actions_taken": 0,
        "external_mutations_taken": 0,
        "deploy_created": False,
        "non_claims": HOSTED_DASHBOARD_NON_CLAIMS,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    index_path.write_text(_render_html(manifest), encoding="utf-8")
    return HostedDashboardExportResult(
        root=root,
        output_dir=export_dir,
        index_path=index_path,
        manifest_path=manifest_path,
        manifest=manifest,
    )


def render_hosted_dashboard_export_cli_lines(
    result: HostedDashboardExportResult,
) -> list[str]:
    return [
        "hosted_dashboard_export: written",
        f"output: {_display_path(result.root, result.index_path)}",
        f"manifest: {_display_path(result.root, result.manifest_path)}",
        "network_actions_taken: 0",
        "external_mutations_taken: 0",
        "deploy_created: false",
    ]


def load_latest_hosted_dashboard_export_summary(root: Path) -> dict[str, Any] | None:
    path = root.resolve() / HOSTED_DASHBOARD_MANIFEST
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {
            "status": "unreadable",
            "path": str(HOSTED_DASHBOARD_MANIFEST),
        }
    if not isinstance(payload, dict):
        return {
            "status": "unreadable",
            "path": str(HOSTED_DASHBOARD_MANIFEST),
        }
    return {
        "status": "available",
        "path": str(HOSTED_DASHBOARD_MANIFEST),
        "index_html": str(HOSTED_DASHBOARD_INDEX),
        "generated_at": payload.get("generated_at", "unknown"),
        "proof_surface": payload.get("proof_surface", {}),
        "artifact_hygiene": payload.get("artifact_hygiene", {}),
        "network_actions_taken": payload.get("network_actions_taken", "unknown"),
        "external_mutations_taken": payload.get("external_mutations_taken", "unknown"),
        "deploy_created": payload.get("deploy_created", "unknown"),
    }


def render_hosted_dashboard_export_dashboard_lines(root: Path) -> list[str]:
    summary = load_latest_hosted_dashboard_export_summary(root)
    lines = ["### Hosted Read-Only Dashboard Export", ""]
    if summary is None:
        lines.extend(
            [
                "- Export status: `missing`",
                "- Command: `python3 -m agent_os.cli hosted-dashboard-export`",
                "- Scope: `static_local_read_only_export`",
                "- Network actions taken: `0`",
                "- External mutations taken: `0`",
                "- Deploy created: `false`",
                "",
            ]
        )
        return lines
    lines.extend(
        [
            f"- Export status: `{summary['status']}`",
            f"- Index: `{summary['index_html']}`",
            f"- Manifest: `{summary['path']}`",
            f"- Generated at: `{summary.get('generated_at', 'unknown')}`",
            f"- Network actions taken: `{summary.get('network_actions_taken', 0)}`",
            f"- External mutations taken: `{summary.get('external_mutations_taken', 0)}`",
            f"- Deploy created: `{str(summary.get('deploy_created', False)).lower()}`",
            "",
        ]
    )
    return lines


def _snapshot(root: Path, relative_path: Path) -> dict[str, Any]:
    path = root / relative_path
    if not path.exists():
        return {
            "state": "missing",
            "path": str(relative_path),
            "sha256": "none",
            "text": "",
        }
    text = path.read_text(encoding="utf-8", errors="replace")
    return {
        "state": "available",
        "path": str(relative_path),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "text": text,
    }


def _render_html(manifest: dict[str, Any]) -> str:
    dashboard = manifest["dashboard_snapshot"]
    status = manifest["status_summary"]
    proof_surface = manifest["proof_surface"]
    artifact_hygiene = manifest["artifact_hygiene"]
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1">',
            "  <title>ClankerOS Read-Only Dashboard Export</title>",
            "  <style>",
            "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 32px; line-height: 1.5; color: #1f2937; background: #f8fafc; }",
            "    main { max-width: 1080px; margin: 0 auto; }",
            "    section { margin: 18px 0; padding: 18px; border: 1px solid #d1d5db; background: #fff; }",
            "    h1, h2 { margin-top: 0; }",
            "    dl { display: grid; grid-template-columns: minmax(180px, 260px) 1fr; gap: 8px 14px; }",
            "    dt { font-weight: 700; }",
            "    dd { margin: 0; overflow-wrap: anywhere; }",
            "    pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f3f4f6; padding: 12px; border: 1px solid #e5e7eb; }",
            "  </style>",
            "</head>",
            "<body>",
            "<main>",
            "<h1>ClankerOS Read-Only Dashboard Export</h1>",
            f"<p>Generated at {html.escape(str(manifest['generated_at']))}. This is a local static snapshot, not a live hosted proof.</p>",
            _definition_list(
                [
                    ("network_actions_taken", str(manifest["network_actions_taken"])),
                    ("external_mutations_taken", str(manifest["external_mutations_taken"])),
                    ("deploy_created", str(manifest["deploy_created"]).lower()),
                ]
            ),
            "<section>",
            "<h2>Dashboard Snapshot</h2>",
            _definition_list(
                [
                    ("state", dashboard["state"]),
                    ("path", dashboard["path"]),
                    ("sha256", dashboard["sha256"]),
                ]
            ),
            f"<pre>{html.escape(dashboard['text'])}</pre>",
            "</section>",
            "<section>",
            "<h2>Status Summary</h2>",
            "<h3>status.md</h3>",
            _snapshot_html(status["status_md"]),
            "<h3>docs/status.md</h3>",
            _snapshot_html(status["docs_status_md"]),
            "</section>",
            "<section>",
            "<h2>Proof Surface State</h2>",
            _definition_list((key, value) for key, value in proof_surface.items()),
            "</section>",
            "<section>",
            "<h2>Artifact Hygiene Summary</h2>",
            _definition_list(
                [
                    ("status", artifact_hygiene.get("status", "missing")),
                    ("path", artifact_hygiene.get("path", "unknown")),
                    ("deleted", artifact_hygiene.get("deleted", 0)),
                    ("gitignore_changes", artifact_hygiene.get("gitignore_changes", 0)),
                ]
            ),
            "<pre>"
            + html.escape(
                json.dumps(
                    artifact_hygiene.get("counts", {}),
                    indent=2,
                    sort_keys=True,
                )
            )
            + "</pre>",
            "</section>",
            "<section>",
            "<h2>Non-Claims</h2>",
            "<ul>",
            "".join(f"<li>{html.escape(claim)}</li>" for claim in manifest["non_claims"]),
            "</ul>",
            "</section>",
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def _snapshot_html(snapshot: dict[str, Any]) -> str:
    return "".join(
        [
            _definition_list(
                [
                    ("state", snapshot["state"]),
                    ("path", snapshot["path"]),
                    ("sha256", snapshot["sha256"]),
                ]
            ),
            f"<pre>{html.escape(snapshot['text'])}</pre>",
        ]
    )


def _definition_list(rows: Any) -> str:
    items = []
    for key, value in rows:
        if isinstance(value, (dict, list)):
            rendered = json.dumps(value, sort_keys=True)
        else:
            rendered = str(value)
        items.append(f"<dt>{html.escape(str(key))}</dt><dd>{html.escape(rendered)}</dd>")
    return "<dl>" + "".join(items) + "</dl>"


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
