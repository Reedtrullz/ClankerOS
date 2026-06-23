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
- Registers local git repositories and exposes `projects`, `project-status`,
  and `project-context` commands so an operator can inspect target repos before
  starting work.
- Creates durable project-scoped `goal`, `plan`, `contract`, and `tasks`
  records before execution, with versioned plan artifacts and explicit
  non-claims.
- Dispatches planned goal tasks through local profiles with `run-task`,
  records routing decisions, runs safe verifier commands, and writes evidence
  packets under `.clanker/projects/<project>/goals/<goal_id>/runs/`.
- Records retry/replan recommendations for failed planned-task runs and
  blocked planned tasks without automatically retrying, resetting, or
  dispatching work.
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
python3 -m agent_os.cli projects
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
- [Project Registry Tutorial](docs/tutorial-project-registry.md)
- [Goal Planning Lifecycle Tutorial](docs/tutorial-goal-lifecycle.md)
- [Run A Planned Task Tutorial](docs/tutorial-run-task.md)
- [Operator Daily Loop Tutorial](docs/tutorial-operator-daily-loop.md)
- [Approval-Gated Coding Tutorial](docs/tutorial-approval-gated-coding.md)
- [Public Snapshot Tutorial](docs/tutorial-public-snapshot.md)
- [Latest Capability Decision Tutorial](docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md)
- [Latest Capability Proposal Tutorial](docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md)
- [Latest Capability Application Tutorial](docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md)
- [Latest Capability Task Tutorial](docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md)
- [Latest Capability Delegation Tutorial](docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md)
- [Latest Capability Result Tutorial](docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md)

Register and inspect a target repository before asking ClankerOS to touch it:

```bash
python3 -m agent_os.cli register-project my-repo --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli projects
python3 -m agent_os.cli project-status my-repo
python3 -m agent_os.cli project-context my-repo
```

Plan a registered project goal before executing work:

```bash
python3 -m agent_os.cli goal "Make the smallest verified improvement" --project my-repo
python3 -m agent_os.cli plan <goal_id>
python3 -m agent_os.cli contract <goal_id>
python3 -m agent_os.cli tasks <goal_id>
```

This writes versioned local artifacts under
`.clanker/projects/<project>/goals/<goal_id>/`. It does not execute tasks,
commit, push, deploy, or call model providers.

Execute one planned task only after the plan and sprint contract are clear:

```bash
python3 -m agent_os.cli run-task <task_id> --profile tester
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli task-recommendations --goal <goal_id>
python3 -m agent_os.cli dashboard
```

`run-task` is profile-gated. `tester` can only run the registered project
default test command; `coder` can run safe local verifier commands. The command
creates a local run and evidence packet, but it does not commit, push, deploy,
start a model provider, or start a subagent.

If a planned task verifier fails, ClankerOS opens a local incident and records
an open `failed_run_task_recovery` recommendation with review, replan, and
manual rerun guidance. If a planned task is blocked, `task-recommendations`
records `blocked_planned_task_replan` guidance. These records are local
operator guidance only; they do not retry or change task status by themselves.

## Current Shape

ClankerOS is a Python CLI with a local SQLite control plane, generated Markdown
reports, JSON artifacts, pytest coverage, eval/playbook checks, and bootstrap
project memory. The first milestone is the closed loop:

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
```

The current control plane includes executable local slices where the verifier
is explicit (`run-goal`, `run-task`) and report-only ladders where a capability
is still blocked. Accepted blocked decisions can create local proposed effects,
applied effects can create more proof tasks, and every activation step
preserves `activation_allowed=false`, `capability_enabled=false`,
`approval_requests_created=0`, `activation_actions_taken=0`, and
`external_mutations_taken=0` unless a future approved capability boundary
changes that contract.

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
