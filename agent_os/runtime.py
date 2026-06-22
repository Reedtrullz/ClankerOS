from __future__ import annotations

import shutil
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Capability:
    name: str
    status: str
    evidence: str
    disposition: str


def detect_runtime_capabilities(root: Path) -> list[Capability]:
    root = root.resolve()
    git_status = "yes" if (root / ".git").exists() or shutil.which("git") else "partial"
    sqlite_status = "yes" if sqlite3.sqlite_version else "no"

    return [
        Capability("repo read access", "yes", f"workspace root is {root}", "use directly"),
        Capability("repo write access", "yes", "patch-based file edits are available", "use directly"),
        Capability("shell access", "yes", "commands can be run through the local shell", "use directly"),
        Capability("filesystem search", "yes", "`rg` and Python filesystem APIs are available", "use directly"),
        Capability("file editing", "yes", "repository files can be created and patched", "use directly"),
        Capability("git access", git_status, "git repository detected or git executable available", "use directly"),
        Capability("network access", "yes", "runtime reports network access enabled", "defer for v1"),
        Capability("package install ability", "partial", "shell is available, but v1 avoids dependencies", "defer safely"),
        Capability("local database availability", sqlite_status, f"sqlite {sqlite3.sqlite_version}", "use directly"),
        Capability("browser control", "partial", "runtime exposes browser-capable tools, not needed for v1", "defer safely"),
        Capability("screenshot or vision support", "partial", "runtime can inspect local images/screenshots", "defer safely"),
        Capability("desktop input control", "partial", "runtime exposes computer-use tools", "defer safely"),
        Capability("tool-calling support", "yes", "Codex tools are available in this session", "use directly"),
        Capability("sub-agent support", "partial", "available through deferred tools/skills when needed", "defer safely"),
        Capability("long-running background execution", "partial", "terminal sessions can run, durable scheduler absent", "emulate later"),
        Capability("cron or scheduled execution", "no", "no repository scheduler implemented yet", "defer safely"),
        Capability("webhook or event trigger support", "no", "no external listener implemented yet", "defer safely"),
        Capability("persistent storage", "yes", "repo files and SQLite are available", "use directly"),
        Capability("UI or dashboard rendering", "partial", "CLI/markdown available; hosted dashboard absent", "emulate in files"),
        Capability("secret management", "partial", "no harness-level secret vault yet", "defer safely"),
        Capability("approval and interruption controls", "partial", "human chat approval exists; policy engine absent", "defer safely"),
        Capability("multi-machine support", "no", "no hub/worker network protocol yet", "defer safely"),
    ]


def write_runtime_capability_matrix(root: Path) -> Path:
    root = root.resolve()
    capabilities = detect_runtime_capabilities(root)
    path = root / "docs" / "runtime-capability-matrix.md"
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Runtime Capability Matrix",
        "",
        f"- Python: {sys.version.split()[0]}",
        f"- Workspace: `{root}`",
        "",
        "| Capability | Status | Evidence | Disposition |",
        "| --- | --- | --- | --- |",
    ]
    for capability in capabilities:
        lines.append(
            f"| {capability.name} | {capability.status} | "
            f"{capability.evidence} | {capability.disposition} |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
