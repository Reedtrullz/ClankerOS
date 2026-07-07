# ClankerOS Proof Surface And Operator Usability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ClankerOS clearly distinguish live current-main proof, committed dashboard snapshots, and local generated readbacks, while reducing operator noise and preparing the next safe hosted/read-only dashboard capability.

**Architecture:** Add small report-only helpers instead of widening autonomy. Keep proof records, hashes, counters, non-claims, and CI semantics intact; change presentation and classification only. Split smoke/golden-path helpers mechanically before deeper UX changes.

**Tech Stack:** Python stdlib, existing `agent_os` CLI/local app, SQLite-backed `Storage`, Git subprocess readbacks, GitHub Actions pytest workflow.

## Global Constraints

- Do not delete artifacts, mutate external systems, deploy, call providers, push, or create PRs from product commands in this slice.
- Preserve current CI proof ingestion semantics: operator-supplied GitHub JSON remains the source of CI proof records.
- Keep `/today`, `/resume`, and Goal first viewport focused on current Goal, phase, one next action, proof status, finish, and resume.
- Treat committed docs as snapshots unless the generated proof surface explicitly matches the current commit.
- Do not broadly ignore `.clanker/delegations`, `.clanker/projects`, or `runs`; some evidence there is intentionally tracked.
- Before long local test loops, run `df -h /System/Volumes/Data`.

---

## Implementation Changes

### Task 1: Proof Surface Model

Add `agent_os/proof_surface.py`, wire `proof-surface` CLI, self-hosting JSON/Markdown, dashboard Operator Cockpit, tests, and `docs/github-testing.md`. The state must distinguish live same-SHA current-main proof from committed dashboard snapshots and local generated readbacks.

### Task 2: Mechanical Local App Smoke Split

Move local app smoke/golden-path helpers into `agent_os/local_app_smoke.py`, preserve function names and CLI output, split smoke tests into `tests/test_local_app_smoke.py`, and update GitHub fast-smoke selectors.

### Task 3: Collapse Secondary Operator Surfaces

Add collapsed grouped secondary details on `/today`, `/resume`, and Goal pages while preserving all proof/evidence fields and first viewport markers.

### Task 4: Report-Only Artifact Hygiene

Add `artifact-hygiene` report-only command with JSON/Markdown reports and categories for tracked evidence, ignored runtime state, unpromoted proof, generated local artifacts, visible evidence candidates, and unknown review-needed files. Delete nothing.

### Task 5: Hosted Read-Only Dashboard Export

Add `hosted-dashboard-export` command that writes a local static HTML/manifest export with dashboard snapshot, status, proof surface, artifact hygiene summary, and zero-effect non-claims.

## Test Plan

- `df -h /System/Volumes/Data`
- `python3 -m pytest tests/test_proof_surface.py -q`
- `python3 -m pytest tests/test_local_app_smoke.py -q`
- `python3 -m pytest tests/test_operator_surfaces.py -q`
- `python3 -m pytest tests/test_artifact_hygiene.py -q`
- `python3 -m pytest tests/test_hosted_dashboard_export.py -q`
- `python3 -m compileall -q agent_os tests`
- `python3 -m agent_os.cli --root "$(mktemp -d)" app-golden-path-smoke-test`
- `python3 -m agent_os.cli proof-surface`
- `python3 -m agent_os.cli artifact-hygiene`
- `python3 -m agent_os.cli hosted-dashboard-export`
- `git diff --check`

## Assumptions

- Work starts from clean `origin/main` on branch `codex/proof-surface-operator-cleanup`.
- Hosted/read-only dashboard export is the chosen capability expansion; remote-worker proof ingestion remains later.
- Artifact hygiene is classification-only; no cleanup, deletion, ignore-rule broadening, or evidence promotion happens in this slice.
