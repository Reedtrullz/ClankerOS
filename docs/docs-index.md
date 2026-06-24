# ClankerOS Documentation Index

Use this as the human map. Generated reports are evidence packets; start with
the tutorials and operating docs when you are trying to understand or use the
system.

## Start Here

- `README.md` - public overview, quick start, non-claims, and repository
  metadata suggestions.
- `docs/getting-started.md` - first local loop, expected outputs, and starter
  prompts.
- `docs/suggested-use.md` - operator prompts, loops, approval boundaries, and
  publishing guidance.
- `docs/operator-recipes.md` - short recipes for returning to a workspace,
  registering a target repo, planning, running one task, capturing specialist
  input, and publishing a snapshot.
- `docs/concepts.md` - glossary for goals, tasks, evidence, approvals,
  effects, worktrees, delegations, memory, skills, and non-claims.
- `docs/architecture.md` - local control plane, runtime artifacts, safety
  boundaries, and extension order.
- `docs/reference-commands.md` - compact command map.
- `docs/tutorial-operator-daily-loop.md` - daily operator loop for returning
  to a workspace, choosing one narrow move, and verifying before claims.
- `docs/tutorial-first-target-repo.md` - register a real local git repository,
  create a planning packet, run one task, and inspect the evidence.
- `docs/tutorial-project-registry.md` - register local git repositories,
  inspect registry status, and write durable project context packets before
  running work.
- `docs/tutorial-goal-lifecycle.md` - create a registered-project goal, inspect
  its plan, write a draft sprint contract, update planned tasks, and replan
  without executing work.
- `docs/tutorial-run-task.md` - dispatch one planned task through a local
  profile-backed verifier, record routing, and inspect the evidence packet.
- `docs/tutorial-executable-delegation.md` - configure a fake local shell
  adapter, run a read-only delegation, inspect evidence, and propose memory.
- `docs/tutorial-public-snapshot.md` - verify, commit, and push a coherent
  public GitHub snapshot without overclaiming.
- `contracts.md` - safety contract and evidence expectations.
- `WORKFLOW.md` - lifecycle ordering from goal intake through verification,
  approvals, delegation packets, and dashboard visibility.

## Core Tutorials

- `docs/tutorial-first-loop.md`
- `docs/tutorial-first-target-repo.md`
- `docs/tutorial-project-registry.md`
- `docs/tutorial-goal-lifecycle.md`
- `docs/tutorial-run-task.md`
- `docs/tutorial-executable-delegation.md`
- `docs/tutorial-operator-daily-loop.md`
- `docs/tutorial-approval-gated-coding.md`
- `docs/tutorial-public-snapshot.md`
- `docs/tutorial-subagent-delegation-results.md`
- `docs/tutorial-skill-proposals.md`
- `docs/tutorial-run-review.md`
- `docs/tutorial-steering-inbox.md`
- `docs/tutorial-operator-approval-schema.md`
- `docs/tutorial-operator-approval-effect-proposals.md`
- `docs/tutorial-capability-activation-contracts.md`

## Capability Follow-Up Tutorials

These tutorials explain the blocked activation ladder. They are intentionally
verbose because each rung preserves source links and explicit non-claims.

- `docs/tutorial-capability-followup-result-decisions.md`
- `docs/tutorial-capability-followup-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-effect-application.md`
- `docs/tutorial-capability-followup-result-tasks.md`
- `docs/tutorial-capability-followup-result-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-results.md`
- `docs/tutorial-capability-followup-result-task-decisions.md`
- `docs/tutorial-capability-followup-result-task-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-task-result-effect-application.md`
- `docs/tutorial-capability-followup-result-task-result-effect-tasks.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-results.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-decisions.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-application.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-tasks.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-results.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-decisions.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-application.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-tasks.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`

## Current State

- `docs/dashboard.md` - generated operator dashboard.
- `docs/next-iteration.md` - generated next work packet from `tasks.md`.
- `docs/task-recommendations.md` - generated local retry/replan guidance for
  failed or blocked planned tasks.
- `docs/OPERATING_SUMMARY.md` - architecture, runtime capability, guardrails,
  and current local proof state.
- `status.md` - chronological implementation evidence.
- `plan.md` - milestone plan.
- `tasks.md` - momentum queue.
- `projects/bootstrap/status.md` - bootstrap project implementation log.
- `projects/bootstrap/handoff.md` - current continuation edge.
- `projects/bootstrap/knowledge.md` - project-local lessons.

## Generated Evidence Reports

Generated reports under `docs/` are proof packets, not marketing docs. The
largest family is the capability activation follow-up ladder:

```text
docs/capability-activation-*.md
docs/capability-activation-followup-*.md
docs/capability-activation-followup-result-*.md
```

Read them when you need exact counters, ids, source links, and non-claims for a
specific command. Use `docs/dashboard.md` for the current operator view.

## Publishing

For public snapshots, use `docs/tutorial-public-snapshot.md` and
`docs/suggested-use.md#when-to-commit-and-push`. Commit only coherent,
verified increments; push only after the branch target and remote are
explicit. Pushing is not deployment, and local tests are not CI proof unless CI
was actually checked.
