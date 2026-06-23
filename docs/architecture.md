# Architecture

ClankerOS is intentionally local-first. It is a harness around replaceable
agents and command runners, not a hosted agent platform.

## Control Plane

```text
CLI commands
  -> AgentSystem
  -> SQLite state in .agent/state.db
  -> markdown reports and JSON artifacts
  -> dashboard, next-iteration, evals, and project notes
```

The control plane stores state in SQLite and writes human-readable continuity
to markdown. Runtime artifacts live under `.agent/`, `.clanker/`, `runs/`,
`docs/`, and `projects/`.

## Local-First Safety

The first milestone keeps external side effects out of scope unless a command
models the evidence and approval boundary explicitly. Most proof-chain commands
write local rows and reports only.

Examples of blocked or report-only surfaces:

- hosted dashboard deployment;
- remote worker startup;
- autonomous scheduling;
- browser or desktop operation;
- CI/deploy execution;
- budget enforcement;
- trust promotion;
- automatic retries;
- real cost tracking.

## Coding Loop

For code changes, ClankerOS can:

1. register a local git repo;
2. create an isolated worktree;
3. run a constrained local command;
4. collect diff and test evidence;
5. create a pending approval;
6. create a local worktree commit after approval and freshness checks;
7. write a GitHub handoff packet with commands for the operator.

The GitHub handoff packet does not push or open a pull request by itself.

## Evidence Chain

The generated capability-chain reports may look repetitive. That is deliberate:
each rung proves a tiny local transition and preserves source links, counters,
and non-claims.

For example, a review command can record:

- `approval_requests_created=0`;
- `activation_actions_taken=0`;
- `external_mutations_taken=0`;
- `activation_allowed=false`;
- `capability_enabled=false`.

Those zeros are part of the proof.

## Extending The System

When adding a capability, prefer this order:

1. write a focused failing test;
2. add storage for durable state;
3. add the CLI command;
4. write a report with explicit non-claims;
5. expose status in the dashboard and iteration packet;
6. run focused, adjacent, full, and operational verification;
7. update project notes and tutorials.
