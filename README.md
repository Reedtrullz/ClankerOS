# ClankerOS

ClankerOS is a local-first agent OS harness for durable AI coding work. It
turns goals into task graphs, records evidence, keeps approval boundaries
explicit, and shows operators what is actually proven before any autonomous
capability is allowed to act.

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
```

The project is intentionally conservative. It prefers local state, reportable
evidence, idempotent effects, and human approval over chat-only claims or
hidden autonomy.

## What It Does

- Tracks goals, tasks, evidence, approvals, effects, incidents, playbooks, and
  iteration packets in SQLite plus human-readable Markdown.
- Generates an operator dashboard and next-iteration packet from current local
  state.
- Runs worktree-isolated coding goals, captures diffs and verification output,
  and gates local commits behind explicit approval.
- Produces GitHub handoff packets after committed local effects, including
  exact push and draft-PR commands without taking network action itself.
- Supports safe profile routing, read-only delegation contracts, structured
  delegation-result ingestion, proposed memory, and proposed skills.
- Models capability activation as blocked proof work until evidence, approval,
  idempotency, and rollback boundaries exist.

## Start Here

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
python3 -m pytest -q
```

Then read:

- [Getting Started](docs/getting-started.md)
- [Suggested Use](docs/suggested-use.md)
- [Concepts](docs/concepts.md)
- [Architecture](docs/architecture.md)
- [Command Reference](docs/reference-commands.md)
- [Documentation Index](docs/docs-index.md)
- [First Loop Tutorial](docs/tutorial-first-loop.md)
- [Operator Daily Loop Tutorial](docs/tutorial-operator-daily-loop.md)
- [Approval-Gated Coding Tutorial](docs/tutorial-approval-gated-coding.md)
- [Public Snapshot Tutorial](docs/tutorial-public-snapshot.md)

## Current Shape

ClankerOS is a Python CLI with a local SQLite control plane, generated Markdown
reports, JSON artifacts, pytest coverage, eval/playbook checks, and bootstrap
project memory. The first milestone is the closed loop:

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
```

The current capability ladder is deliberately report-heavy: accepted blocked
decisions can create local proposed effects, applied effects can create more
proof tasks, and every step preserves `activation_allowed=false`,
`capability_enabled=false`, `approval_requests_created=0`,
`activation_actions_taken=0`, and `external_mutations_taken=0` unless a future
approved capability boundary changes that contract.

For the detailed state, use:

- [Operator Dashboard](docs/dashboard.md)
- [Next Iteration Packet](docs/next-iteration.md)
- [Operating Summary](docs/OPERATING_SUMMARY.md)
- [Generated Evidence Reports](docs/docs-index.md#generated-evidence-reports)
- [Status Log](status.md)
- [Bootstrap Handoff](projects/bootstrap/handoff.md)

## Public Snapshot Checklist

Before pushing a public snapshot:

```bash
git status --short --branch
git diff --check
python3 -m pytest -q
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Pushing is not deployment. Local tests are not CI proof. GitHub metadata
readback is not runtime proof. See
[Tutorial: Public Snapshot](docs/tutorial-public-snapshot.md) for the full
recommended flow.

## Non-Claims

This repository does not yet claim hosted dashboard availability, remote worker
execution, autonomous scheduling, browser/desktop adapter readiness, live
CI/deploy proof, budget enforcement, trust promotion, automatic retries, or
real cost tracking. Those surfaces remain blocked until their evidence and
approval contracts are satisfied.

## GitHub About

Suggested repository description:

```text
Local-first agent OS harness for durable AI coding work: task graphs, verification evidence, approvals, and operator-visible autonomy.
```

Suggested topics:

```text
agent-operating-system, agent-os, ai-agents, agentic-ai, agent-orchestration, coding-agents, local-first, human-in-the-loop, approval-workflow, verification, evidence, task-graph, operator-dashboard, worktrees, sqlite, python, cli-tool, developer-tools, evals, markdown
```
