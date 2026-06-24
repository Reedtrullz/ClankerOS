from __future__ import annotations

import fnmatch
import hashlib
import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent_os.storage import RegisteredProject, Storage, SubagentDelegation, Task, utc_now


class ContextPackError(ValueError):
    pass


@dataclass(frozen=True)
class ContextPackResult:
    context_pack_id: str
    delegation_id: str
    project_id: str
    json_path: Path | None
    markdown_path: Path | None
    payload: dict[str, Any]


DEFAULT_BUDGETS = {
    "max_files": 25,
    "max_snippets": 40,
    "max_snippet_chars": 400,
    "max_total_chars": 20000,
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "before",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
}

IMPLEMENTATION_EXTENSIONS = {
    ".py",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
}

ENTRYPOINT_PATHS = {
    "agent_os/cli.py": "CLI command entrypoint",
    "README.md": "repository overview",
    "pyproject.toml": "project config",
    "AGENTS.md": "agent operating instructions",
}

SKIP_DIRS = {
    ".git",
    ".agent",
    ".clanker",
    ".venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
}

SECRET_PATTERNS = {
    ".env",
    "id_rsa",
    "*.pem",
    "*.key",
    "credentials*",
    "secrets*",
}


def generate_context_pack(
    root: Path,
    storage: Storage,
    delegation_id: str,
    *,
    max_files: int = DEFAULT_BUDGETS["max_files"],
    max_snippets: int = DEFAULT_BUDGETS["max_snippets"],
    max_snippet_chars: int = DEFAULT_BUDGETS["max_snippet_chars"],
    max_total_chars: int = DEFAULT_BUDGETS["max_total_chars"],
    include_globs: list[str] | None = None,
    exclude_globs: list[str] | None = None,
    output_format: str = "both",
    output_dir: Path | None = None,
) -> ContextPackResult:
    if output_format not in {"json", "markdown", "both"}:
        raise ContextPackError(f"unsupported context pack format {output_format}")
    if min(max_files, max_snippets, max_snippet_chars, max_total_chars) <= 0:
        raise ContextPackError("context pack budgets must be positive")

    root = root.resolve()
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        raise ContextPackError(f"delegation {delegation_id} not found")
    task = storage.get_task(delegation.parent_task_id)
    if task is None:
        raise ContextPackError(f"task {delegation.parent_task_id} not found")
    project = storage.get_registered_project(task.project_id)
    if project is None:
        raise ContextPackError(f"registered project {task.project_id} not found")

    project_root = Path(project.root_path).resolve()
    if not project_root.exists() or not project_root.is_dir():
        raise ContextPackError(f"registered project root unavailable: {project_root}")

    goal = storage.get_goal(task.goal_id)
    source_text = _source_text(goal.description if goal else "", task, delegation)
    terms = extract_search_terms(source_text)
    budgets = {
        "max_files": max_files,
        "max_snippets": max_snippets,
        "max_snippet_chars": max_snippet_chars,
        "max_total_chars": max_total_chars,
    }
    inventory = _repo_inventory(
        project_root,
        include_globs=include_globs or [],
        exclude_globs=exclude_globs or [],
    )
    grep_hits, grep_method, grep_available, grep_error = _grep_hits(
        project_root,
        terms,
        set(inventory),
        max_hits=80,
        max_hits_per_file=5,
        max_snippet_chars=max_snippet_chars,
    )
    ranked_files = _rank_files(
        inventory,
        terms,
        source_text,
        grep_hits,
        max_files=max_files,
    )
    snippets = _snippets(
        project_root,
        ranked_files,
        grep_hits,
        max_snippets=max_snippets,
        max_snippet_chars=max_snippet_chars,
        max_total_chars=max_total_chars,
    )
    context_pack_id = _context_pack_id(
        delegation=delegation,
        task=task,
        project=project,
        terms=terms,
        budgets=budgets,
    )
    payload = {
        "context_pack_id": context_pack_id,
        "project_id": project.name,
        "goal_id": task.goal_id,
        "task_id": task.id,
        "delegation_id": delegation.id,
        "created_at": utc_now(),
        "query": {
            "source_text": source_text,
            "terms": terms,
            "normalized_terms": sorted({term.replace("-", "_") for term in terms}),
        },
        "budgets": budgets,
        "project": _project_payload(project),
        "repo_inventory": {
            "root_path": str(project_root),
            "files": inventory,
            "file_count": len(inventory),
        },
        "grep_available": grep_available,
        "grep_method": grep_method,
        "grep_error": grep_error,
        "ranked_files": ranked_files,
        "test_hints": _test_hints(inventory, ranked_files),
        "entrypoint_hints": _entrypoint_hints(inventory),
        "config_hints": _config_hints(inventory),
        "grep_hits": grep_hits[:40],
        "snippets": snippets,
        "non_claims": [
            "No file was modified.",
            "No command with side effects was run.",
            "No model provider was called by ClankerOS.",
            "No commit, push, deploy, or approval was performed.",
        ],
    }

    context_dir = output_dir or _context_dir(root, delegation.id)
    context_dir.mkdir(parents=True, exist_ok=True)
    json_path: Path | None = None
    markdown_path: Path | None = None
    if output_format in {"json", "both"}:
        json_path = context_dir / "context_pack.json"
        json_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    if output_format in {"markdown", "both"}:
        markdown_path = context_dir / "context_pack.md"
        markdown_path.write_text(render_context_pack_markdown(payload), encoding="utf-8")
    return ContextPackResult(
        context_pack_id=context_pack_id,
        delegation_id=delegation.id,
        project_id=project.name,
        json_path=json_path,
        markdown_path=markdown_path,
        payload=payload,
    )


def ensure_context_pack_for_run(
    root: Path,
    storage: Storage,
    delegation: SubagentDelegation,
    evidence_dir: Path,
) -> dict[str, Any]:
    task = storage.get_task(delegation.parent_task_id)
    if task is None or storage.get_registered_project(task.project_id) is None:
        return {"available": False, "reason": "parent project is not registered"}

    context_dir = _context_dir(root, delegation.id)
    json_path = context_dir / "context_pack.json"
    markdown_path = context_dir / "context_pack.md"
    if not json_path.exists() or not markdown_path.exists():
        generate_context_pack(root, storage, delegation.id)
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    evidence_json = evidence_dir / "context_pack.json"
    evidence_md = evidence_dir / "context_pack.md"
    shutil.copyfile(json_path, evidence_json)
    shutil.copyfile(markdown_path, evidence_md)
    top_ranked_files = [item["path"] for item in payload.get("ranked_files", [])[:5]]
    return {
        "available": True,
        "context_pack_id": payload["context_pack_id"],
        "project_id": payload["project_id"],
        "json_path": str(evidence_json),
        "markdown_path": str(evidence_md),
        "json_path_relative": str(evidence_json.relative_to(root)),
        "markdown_path_relative": str(evidence_md.relative_to(root)),
        "ranked_file_count": len(payload.get("ranked_files", [])),
        "grep_hit_count": len(payload.get("grep_hits", [])),
        "top_ranked_files": top_ranked_files,
        "test_hints": payload.get("test_hints", [])[:5],
    }


def context_pack_validation_metadata(
    context_pack: dict[str, Any],
    structured_output: dict[str, Any],
) -> dict[str, Any]:
    if not context_pack.get("available"):
        return {
            "context_pack_used": False,
            "returned_files_in_inventory": None,
            "returned_files_missing": [],
            "top_ranked_files_referenced": [],
        }
    try:
        payload = json.loads(Path(context_pack["json_path"]).read_text(encoding="utf-8"))
    except (KeyError, OSError, json.JSONDecodeError):
        return {
            "context_pack_used": False,
            "returned_files_in_inventory": None,
            "returned_files_missing": [],
            "top_ranked_files_referenced": [],
        }
    inventory = set(payload.get("repo_inventory", {}).get("files", []))
    returned_files = _returned_files(structured_output)
    missing = sorted(path for path in returned_files if path not in inventory)
    top_ranked = [item["path"] for item in payload.get("ranked_files", [])[:5]]
    referenced = [path for path in top_ranked if path in returned_files]
    return {
        "context_pack_used": True,
        "returned_files_in_inventory": len(missing) == 0,
        "returned_files_missing": missing,
        "top_ranked_files_referenced": referenced,
    }


def render_context_pack_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Context Pack",
        "",
        f"- context_pack_id: {payload['context_pack_id']}",
        f"- project_id: {payload['project_id']}",
        f"- delegation_id: {payload['delegation_id']}",
        f"- task_id: {payload['task_id']}",
        "",
        "## Query Terms",
        "",
    ]
    lines.extend(f"- {term}" for term in payload["query"]["terms"][:40])
    lines.extend(["", "## Ranked Files", ""])
    for item in payload["ranked_files"]:
        lines.append(f"- {item['path']} score={item['score']} tags={','.join(item['tags'])}")
        for reason in item["reasons"][:3]:
            lines.append(f"  - {reason}")
    lines.extend(["", "## Test Hints", ""])
    if payload["test_hints"]:
        lines.extend(f"- {hint['path']}: {hint['reason']}" for hint in payload["test_hints"])
    else:
        lines.append("- none")
    lines.extend(["", "## Grep Hits", ""])
    for hit in payload["grep_hits"][:20]:
        lines.append(f"- {hit['path']}:{hit['line']} term={hit['term']} `{hit['snippet']}`")
    if not payload["grep_hits"]:
        lines.append("- none")
    lines.extend(["", "## Snippets", ""])
    for snippet in payload["snippets"]:
        lines.append(f"### {snippet['path']}:{snippet['start_line']}-{snippet['end_line']}")
        lines.append("")
        lines.append("```text")
        lines.append(snippet["text"])
        lines.append("```")
        lines.append("")
    lines.extend(["## Non-Claims", ""])
    lines.extend(f"- {claim}" for claim in payload["non_claims"])
    return "\n".join(lines) + "\n"


def extract_search_terms(source_text: str) -> list[str]:
    raw_tokens = re.findall(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", source_text.lower())
    terms: set[str] = set()
    meaningful_sequence: list[str] = []
    for token in raw_tokens:
        if _is_meaningful_term(token):
            terms.add(token)
            meaningful_sequence.append(token)
        for part in re.split(r"[-_]+", token):
            if _is_meaningful_term(part):
                terms.add(part)
                meaningful_sequence.append(part)
        if "-" in token or "_" in token:
            terms.add(token.replace("-", "_"))
            terms.add(token.replace("_", "-"))
    for left, right in zip(meaningful_sequence, meaningful_sequence[1:]):
        if left != right:
            terms.add(f"{left}-{right}")
            terms.add(f"{left}_{right}")
    return sorted(terms)


def _source_text(goal_text: str, task: Task, delegation: SubagentDelegation) -> str:
    return "\n".join(
        [
            goal_text,
            task.description,
            task.task_type,
            json.dumps(task.verification_plan, sort_keys=True),
            delegation.title,
            delegation.prompt,
            delegation.expected_output_schema,
        ]
    )


def _context_pack_id(
    *,
    delegation: SubagentDelegation,
    task: Task,
    project: RegisteredProject,
    terms: list[str],
    budgets: dict[str, int],
) -> str:
    seed = json.dumps(
        {
            "delegation_id": delegation.id,
            "task_id": task.id,
            "project_id": project.name,
            "terms": terms,
            "budgets": budgets,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    return f"context_pack_{digest}"


def _project_payload(project: RegisteredProject) -> dict[str, Any]:
    return {
        "id": project.name,
        "name": project.name,
        "root_path": project.root_path,
        "default_test_command": project.default_test_command,
        "allowed_write_roots": project.allowed_write_roots,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    }


def _context_dir(root: Path, delegation_id: str) -> Path:
    return root / ".clanker" / "delegations" / delegation_id / "context"


def _is_meaningful_term(token: str) -> bool:
    return (
        bool(token)
        and token not in STOPWORDS
        and (len(token) >= 3 or "-" in token or "_" in token)
    )


def _repo_inventory(
    project_root: Path,
    *,
    include_globs: list[str],
    exclude_globs: list[str],
) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        candidates = [line for line in result.stdout.splitlines() if line]
    else:
        candidates = [
            path.relative_to(project_root).as_posix()
            for path in project_root.rglob("*")
            if path.is_file()
        ]
    return sorted(
        path
        for path in candidates
        if _is_allowed_path(path, include_globs=include_globs, exclude_globs=exclude_globs)
        and _safe_file(project_root / path)
    )


def _is_allowed_path(
    path: str,
    *,
    include_globs: list[str],
    exclude_globs: list[str],
) -> bool:
    parts = Path(path).parts
    if any(part in SKIP_DIRS for part in parts):
        return False
    if _is_secret_like(path):
        return False
    if include_globs and not any(fnmatch.fnmatch(path, glob) for glob in include_globs):
        return False
    if exclude_globs and any(fnmatch.fnmatch(path, glob) for glob in exclude_globs):
        return False
    return True


def _is_secret_like(path: str) -> bool:
    name = Path(path).name
    return any(fnmatch.fnmatch(name, pattern) for pattern in SECRET_PATTERNS)


def _safe_file(path: Path, max_bytes: int = 200_000) -> bool:
    try:
        if path.stat().st_size > max_bytes:
            return False
        with path.open("rb") as handle:
            sample = handle.read(1024)
        return b"\x00" not in sample
    except OSError:
        return False


def _grep_hits(
    project_root: Path,
    terms: list[str],
    inventory: set[str],
    *,
    max_hits: int,
    max_hits_per_file: int,
    max_snippet_chars: int,
) -> tuple[list[dict[str, Any]], str, bool, str | None]:
    if shutil.which("rg"):
        hits = _rg_hits(
            project_root,
            terms,
            inventory,
            max_hits=max_hits,
            max_hits_per_file=max_hits_per_file,
            max_snippet_chars=max_snippet_chars,
        )
        if hits is not None:
            return hits, "rg", True, None
    hits = _python_hits(
        project_root,
        terms,
        inventory,
        max_hits=max_hits,
        max_hits_per_file=max_hits_per_file,
        max_snippet_chars=max_snippet_chars,
    )
    return hits, "python fallback", True, None


def _rg_hits(
    project_root: Path,
    terms: list[str],
    inventory: set[str],
    *,
    max_hits: int,
    max_hits_per_file: int,
    max_snippet_chars: int,
) -> list[dict[str, Any]] | None:
    if not terms:
        return []
    command = [
        "rg",
        "--line-number",
        "--no-heading",
        "--color",
        "never",
        "--fixed-strings",
        "--max-filesize",
        "200K",
    ]
    for directory in sorted(SKIP_DIRS):
        command.extend(["--glob", f"!{directory}/**"])
    for pattern in sorted(SECRET_PATTERNS):
        command.extend(["--glob", f"!{pattern}"])
    for term in terms[:40]:
        command.extend(["-e", term])
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode not in {0, 1}:
        return None
    hits: list[dict[str, Any]] = []
    per_file: dict[str, int] = {}
    for line in result.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) != 3:
            continue
        path, line_number_text, text = parts
        if path not in inventory:
            continue
        if per_file.get(path, 0) >= max_hits_per_file:
            continue
        term = _first_matching_term(text, terms)
        if term is None:
            continue
        hits.append(
            {
                "path": path,
                "line": int(line_number_text),
                "term": term,
                "snippet": text.strip()[:max_snippet_chars],
            }
        )
        per_file[path] = per_file.get(path, 0) + 1
        if len(hits) >= max_hits:
            break
    return hits


def _python_hits(
    project_root: Path,
    terms: list[str],
    inventory: set[str],
    *,
    max_hits: int,
    max_hits_per_file: int,
    max_snippet_chars: int,
) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    lowered_terms = [(term, term.lower()) for term in terms[:40]]
    for path in sorted(inventory):
        per_file = 0
        try:
            lines = (project_root / path).read_text(
                encoding="utf-8",
                errors="replace",
            ).splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            term = next((original for original, value in lowered_terms if value in lowered), None)
            if term is None:
                continue
            hits.append(
                {
                    "path": path,
                    "line": line_number,
                    "term": term,
                    "snippet": line.strip()[:max_snippet_chars],
                }
            )
            per_file += 1
            if per_file >= max_hits_per_file or len(hits) >= max_hits:
                break
        if len(hits) >= max_hits:
            break
    return hits


def _first_matching_term(text: str, terms: list[str]) -> str | None:
    lowered = text.lower()
    for term in terms:
        if term.lower() in lowered:
            return term
    return None


def _rank_files(
    inventory: list[str],
    terms: list[str],
    source_text: str,
    grep_hits: list[dict[str, Any]],
    *,
    max_files: int,
) -> list[dict[str, Any]]:
    source_lower = source_text.lower()
    hits_by_file: dict[str, list[dict[str, Any]]] = {}
    for hit in grep_hits:
        hits_by_file.setdefault(hit["path"], []).append(hit)
    ranked: list[dict[str, Any]] = []
    for path in inventory:
        score = 0
        reasons: list[str] = []
        tags = _tags_for_path(path)
        path_lower = path.lower()
        basename = Path(path).name.lower()
        for term in terms:
            term_lower = term.lower()
            if term_lower in path_lower:
                score += 5
                reasons.append(f"path match: {term}")
            if term_lower in basename:
                score += 8
                reasons.append(f"filename match: {term}")
        suffix = Path(path).suffix.lower()
        if suffix in IMPLEMENTATION_EXTENSIONS:
            score += 2
            reasons.append(f"implementation extension: {suffix or 'none'}")
        if path.startswith("tests/") and any(term in source_lower for term in ["test", "tests", "verification", "pytest"]):
            score += 5
            reasons.append("test path matches task verification language")
        if path.startswith("docs/") and any(term in source_lower for term in ["docs", "tutorial", "readme"]):
            score += 4
            reasons.append("docs path matches task documentation language")
        if path in ENTRYPOINT_PATHS:
            score += 3
            reasons.append(ENTRYPOINT_PATHS[path])
        file_hits = hits_by_file.get(path, [])
        if file_hits:
            hit_score = min(len(file_hits), 4) * 3
            score += hit_score
            reasons.append(f"grep hits: {len(file_hits)}")
        if _is_generated_ladder_path(path) and not any(term in path_lower for term in terms):
            score -= 8
            reasons.append("generated proof-ladder path deprioritized")
        if score > 0:
            ranked.append(
                {
                    "path": path,
                    "score": score,
                    "reasons": _dedupe(reasons),
                    "tags": tags,
                    "exists": True,
                }
            )
    ranked.sort(key=lambda item: (-item["score"], item["path"]))
    return ranked[:max_files]


def _tags_for_path(path: str) -> list[str]:
    tags: list[str] = []
    suffix = Path(path).suffix.lower()
    if path.startswith("tests/"):
        tags.append("test")
    if path.startswith("docs/") or path == "README.md":
        tags.append("docs")
    if suffix == ".py":
        tags.append("python")
        if not path.startswith("tests/"):
            tags.append("implementation")
    if path in ENTRYPOINT_PATHS:
        tags.append("entrypoint")
    if suffix in {".toml", ".yaml", ".yml", ".json"}:
        tags.append("config")
    return sorted(set(tags))


def _is_generated_ladder_path(path: str) -> bool:
    lowered = path.lower()
    return "capability_activation_followup" in lowered or "expansion_operator" in lowered or "proof-checklist" in lowered


def _test_hints(inventory: list[str], ranked_files: list[dict[str, Any]]) -> list[dict[str, str]]:
    ranked_paths = {file["path"] for file in ranked_files}
    hints = [
        {
            "path": path,
            "reason": "test file candidate for ranked implementation context",
        }
        for path in inventory
        if path.startswith("tests/") and (path in ranked_paths or "test" in Path(path).name)
    ]
    return hints[:10]


def _entrypoint_hints(inventory: list[str]) -> list[dict[str, str]]:
    return [
        {"path": path, "reason": reason}
        for path, reason in ENTRYPOINT_PATHS.items()
        if path in inventory
    ]


def _config_hints(inventory: list[str]) -> list[dict[str, str]]:
    return [
        {"path": path, "reason": "project config"}
        for path in inventory
        if Path(path).name in {"pyproject.toml", "package.json", "tsconfig.json", "vite.config.ts"}
        or Path(path).suffix.lower() in {".toml", ".yaml", ".yml"}
    ][:10]


def _snippets(
    project_root: Path,
    ranked_files: list[dict[str, Any]],
    grep_hits: list[dict[str, Any]],
    *,
    max_snippets: int,
    max_snippet_chars: int,
    max_total_chars: int,
) -> list[dict[str, Any]]:
    snippets: list[dict[str, Any]] = []
    seen_regions: set[tuple[str, int, int]] = set()
    total_chars = 0
    for hit in grep_hits:
        if len(snippets) >= max_snippets or total_chars >= max_total_chars:
            break
        snippet = _snippet_for_line(project_root, hit["path"], hit["line"], max_snippet_chars)
        if snippet is None:
            continue
        key = (snippet["path"], snippet["start_line"], snippet["end_line"])
        if key in seen_regions:
            continue
        remaining = max_total_chars - total_chars
        if remaining <= 0:
            break
        if len(snippet["text"]) > remaining:
            snippet["text"] = snippet["text"][:remaining]
        snippets.append(snippet)
        seen_regions.add(key)
        total_chars += len(snippet["text"])
    for ranked in ranked_files:
        if len(snippets) >= max_snippets or total_chars >= max_total_chars:
            break
        if any(snippet["path"] == ranked["path"] for snippet in snippets):
            continue
        snippet = _snippet_for_line(project_root, ranked["path"], 1, max_snippet_chars)
        if snippet is None:
            continue
        remaining = max_total_chars - total_chars
        if len(snippet["text"]) > remaining:
            snippet["text"] = snippet["text"][:remaining]
        snippets.append(snippet)
        total_chars += len(snippet["text"])
    return snippets


def _snippet_for_line(
    project_root: Path,
    relative_path: str,
    line_number: int,
    max_snippet_chars: int,
) -> dict[str, Any] | None:
    path = project_root / relative_path
    if not _safe_file(path):
        return None
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None
    if not lines:
        return None
    start = max(1, line_number - 1)
    end = min(len(lines), line_number + 1)
    text = "\n".join(lines[start - 1 : end])[:max_snippet_chars]
    return {
        "path": relative_path,
        "start_line": start,
        "end_line": end,
        "text": text,
    }


def _returned_files(structured_output: dict[str, Any]) -> set[str]:
    returned: set[str] = set()
    for key in ["files", "relevant_files"]:
        values = structured_output.get(key, [])
        if isinstance(values, list):
            returned.update(str(value) for value in values if str(value))
    return returned


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            result.append(value)
            seen.add(value)
    return result
