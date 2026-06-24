# ClankerOS Concepts

This glossary explains the words used throughout the CLI, generated reports,
and project notes.

## Core Objects

- Goal: a durable objective stored in SQLite and reflected in project notes.
- Task: a unit of work derived from a goal. Tasks carry type, status, risk,
  evidence requirements, and project context.
- Run: one execution attempt with command output, verification files, and a
  summary under `runs/<run_id>/`.
- Evidence: files or rows that prove what happened locally. Evidence can
  include diffs, test output, JSON artifacts, reports, and command readbacks.
- Approval: an explicit operator decision required before sensitive local
  effects, such as creating a local git commit.
- Effect: a proposed or applied local state change. Effects preserve source
  links and counters so later commands can prove what they did not do.
- Incident: a durable failure or stuck-work record that prevents quiet loss of
  context.

## Operator Boundaries

- Report-only proof: a command writes local findings and non-claims without
  taking external action.
- Non-claim: an explicit statement that a report does not prove or mutate
  something, such as deployment, trust promotion, or capability enablement.
- Approval boundary: the point where ClankerOS requires an operator decision
  before crossing from evidence into a sensitive local effect.
- Activation blocked: a capability has evidence or tasks, but still has
  `activation_allowed=false` and `capability_enabled=false`.

## Execution Surfaces

- Worktree: an isolated git checkout used for coding tasks so the source repo
  is not edited directly by a run.
- Delegation packet: a local read-only contract for specialist or subagent
  context. Creating a packet does not start a subagent or call a model.
- Context pack: a delegation-specific repo scout packet generated from the
  parent goal, task, and delegation prompt. It ranks files, explains scores,
  records capped grep hits and snippets, lists test/entrypoint/config hints,
  skips ignored and secret-like paths, and writes JSON/Markdown under
  `.clanker/delegations/<delegation_id>/context/`.
- Implementation handoff: a compact run-evidence artifact written after a
  successful executable delegation. It points at context-pack JSON/Markdown,
  returned-file validation, scout returned files, and test hints without
  embedding large snippets or approving implementation work. Use
  `implementation-handoff <delegation_id>` to inspect the artifact directly;
  review and dashboard outputs also summarize handoff readability and schema
  health.
- Coder prep packet: an artifact-only bridge from an implementation handoff to
  a future coding run. `coder-prep <delegation_id>` consumes
  `implementation_handoff.md`, records allowed files, test hints, acceptance
  criteria, risks, and an operator-review-required run plan, and reports zero
  task rows, runs, routing decisions, worktrees, approvals, source edits,
  command reruns, network actions, and external mutations.
- Coder worktree plan: an artifact-only bridge from coder prep to a possible
  isolated coding run. `coder-worktree-plan <delegation_id>` consumes
  `coder_prep.md`, records the source prep hash, allowed files, proposed
  branch/path, future explicit `run-goal --isolation worktree` shape, and an
  operator-approval-required gate while reporting zero worktrees, approvals,
  runs, source edits, command reruns, network actions, provider calls, and
  external mutations.
- Project context packet: a durable operator summary for a registered project.
  It is broader and less task-specific than a context pack.
- Profile: a local routing role such as planner, coder, scout, tester, or
  evaluator.
- Dashboard: a generated markdown status view at `docs/dashboard.md`.
- Iteration packet: the generated next-work file at `docs/next-iteration.md`.

## Memory And Skills

- Memory proposal: a proposed durable fact from verified context. It remains
  inactive until approved.
- Skill proposal: a proposed reusable procedure under `.clanker/skills/`.
  It remains inactive until approved.
- Project notes: markdown continuity files under `projects/<name>/`.

## Trust Rule

Do not treat an agent message as completion. Treat a verified file, database
row, command output, dashboard section, report, or test result as evidence.
