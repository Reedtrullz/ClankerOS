# Agent System Operator Guide

This repository is a local-first harness for a durable agentic operating system.
It should favor working loops, explicit state, and verification evidence over
chat-only claims.

## Operating Rules

- Read `docs/OPERATING_SUMMARY.md`, `contracts.md`, `plan.md`, `tasks.md`,
  `status.md`, and the active project file pack before changing behavior.
- Treat the SQLite database and `.agent/` runtime files as operational indexes.
  Treat markdown files under the repository as the human-readable source of
  project continuity.
- Every meaningful task needs a Definition of Done, a verifier, evidence, and a
  memory or learning update.
- Do not mark work complete because an agent said it completed. Verify the
  expected file, output, behavior, or state change.
- Keep the first milestone focused on the closed loop:
  goal -> task graph -> execution -> verification -> memory -> visibility -> learning.
- Add multi-agent parallelism only after the single-worker baseline is reliable.

## Safety Defaults

- Local filesystem actions are allowed inside the repository.
- External side effects are out of scope for the first milestone.
- Destructive actions require explicit approval and a checkpoint.
- Secrets must not be written to project memory, logs, or artifacts.
