# ClankerOS

ClankerOS is a local-first harness for building a durable agentic operating
system with explicit state, verification evidence, and approval boundaries.
It starts with the closed loop and then adds a practical approval-gated coding
vertical:

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
registered repo -> isolated worktree -> verified diff -> proposed effect -> approval
approval -> freshness recheck -> local worktree commit -> committed effect evidence
committed effect -> GitHub handoff packet -> operator push/draft-PR commands
```

The project deliberately favors report-only proof, conservative local behavior,
and clear non-claims before any hosted dashboard, remote worker, scheduler,
browser/desktop adapter, CI/deploy, budget enforcement, trust promotion,
automatic retry, or real-cost tracking capability is allowed to act.

## About

ClankerOS is for operators who want agents to become more useful without
becoming vague or unsafe. It stores operational state in SQLite, writes
human-readable continuity in Markdown, and uses tests plus generated reports to
separate what is locally proven from what still needs approval.

The repository currently contains a working Python CLI, SQLite storage layer,
generated proof reports, dashboard output, evals, playbooks, and bootstrap
project memory. It can also register local git repositories, run a constrained
coding command inside an isolated git worktree, capture the resulting diff and
test evidence, and record a pending `local_git_commit` effect for operator
review. After explicit approval, it can re-check the captured evidence and
create the local git commit exactly once in the isolated worktree. It can also
prepare a GitHub handoff packet for a committed local effect, including exact
operator commands for `git push` and draft PR creation while recording that no
network action was taken. Deployments and other external side effects remain
blocked unless an implemented flow explicitly models evidence, authorization,
rollback, and verification.

## Repository Metadata

GitHub description:

```text
Local-first agent operating system harness with explicit state, evidence, and approval-gated coding workflows.
```

Suggested GitHub topics:

```text
agent-operating-system, agentic-ai, ai-agents, agent-os, local-first, coding-agents, automation, sqlite, approval-workflow, worktrees, verification, operator-dashboard, evals, markdown, python
```

## Quick Start

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
python3 -m agent_os.cli dashboard
python3 -m pytest -q
```

Then read:

- `docs/dashboard.md` for the current operational view.
- `docs/next-iteration.md` for the next local work packet.
- `projects/bootstrap/handoff.md` for the current continuation edge.

To try the approval-gated coding loop on a local git repo:

```bash
python3 -m agent_os.cli register-project my-repo --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli run-goal "Make a tiny verified change" --project my-repo --isolation worktree --command "python3 -c \"from pathlib import Path; Path('agent-output.txt').write_text('hello\\n')\""
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli approvals
python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "reviewed diff and tests"
python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator
python3 -m agent_os.cli github-handoff <effect_id> --base main --title "Make a tiny verified change"
python3 -m agent_os.cli cleanup-worktrees --confirm --reason "committed branch kept"
```

This creates a worktree and approval packet, then creates the local worktree
commit only after approval and a fresh evidence recheck. Cleanup removes clean
terminal worktrees only after an explicit confirmed cleanup decision. The
GitHub handoff step writes local evidence and command strings; it does not push
or open the PR for you.

## Tutorials And Suggested Use

- [Run the first local loop](docs/tutorial-first-loop.md)
- [Run an approval-gated coding task](docs/tutorial-approval-gated-coding.md)
- [Suggested use patterns](docs/suggested-use.md)
- [Operating summary](docs/OPERATING_SUMMARY.md)
- [Safety contract](contracts.md)

## Current Capability

The repository can now:

- initialize a SQLite-backed local control plane;
- write a runtime capability matrix;
- register local git repositories with default test commands and allowed write
  roots;
- create isolated git worktrees for constrained local coding runs;
- capture command output, git status, patch diffs, test output, verification
  JSON, and approval packets for proposed code changes;
- record proposed `local_git_commit` effects without creating the commit;
- create an approved local worktree commit exactly once after re-checking the
  captured base commit, diff, changed files, and test command;
- record worktree cleanup decisions and remove clean terminal worktrees for
  committed, blocked, or superseded effects without forcing dirty deletions;
- prepare a GitHub handoff packet for a committed local effect with exact
  operator `git push` and draft PR commands while recording
  `network_actions_taken=0`;
- accept a goal through the CLI;
- decompose the goal into typed tasks;
- let a local worker claim and execute tasks;
- gate approval-required tasks before worker claim or execution;
- verify task outputs with deterministic evidence;
- open incident records with JSON evidence when verification fails;
- sweep for stale active tasks and block them with `task_stuck` incidents;
- resolve incidents with operator notes and JSON resolution evidence;
- report repeated blocked or failed task hotspots with a queue-health report;
- review blocked tasks and stale project handoffs with a handoff report;
- run the local eval suite after a harness behavior change and record the
  change-specific evidence;
- distill repeated run learnings into root `knowledge.md` with a local report;
- report local budget/trust posture metadata without changing dispatch behavior;
- summarize dispatch posture history from recent report-only posture snapshots;
- review dispatch posture snapshot freshness from local report timestamps;
- recommend manual dispatch posture refresh commands from persisted staleness
  reviews without running them;
- record a report-only Capability Expansion Ledger for deferred autonomy
  surfaces before any hosted dashboard, remote worker, scheduler, adapter,
  CI/deploy, budget, trust, retry, or cost-tracking behavior exists;
- review capability readiness from the latest expansion ledger and report
  missing evidence without enabling any capability or creating ledgers as a
  side effect;
- index capability proof gaps from readiness reviews without generating proof
  artifacts or promoting any deferred capability;
- plan manual evidence collection from approval-boundary matrices without
  collecting proof, approving capabilities, or creating upstream reports as a
  side effect;
- review promotion gates from evidence collection plans without collecting
  evidence, approving capabilities, promoting capabilities, or changing
  routing;
- record report-only promotion decisions from gate checklists without
  approving capabilities, promoting trust, or changing routing;
- audit trust-promotion readiness from promotion decision ledgers without
  promoting trust, approving capabilities, or changing routing;
- audit automatic-retry readiness from trust-promotion audits without retrying
  or replaying work;
- audit real-cost-tracking readiness from automatic-retry audits without
  tracking spend, enforcing budgets, or mutating external systems;
- check hosted-dashboard proof readiness from Real Cost Tracking proof
  checklists, preserving Real-Cost-sourced Real Cost Tracking proof metadata
  when present, with legacy real-cost-tracking audit fallback, without
  enabling or deploying a hosted dashboard;
- check remote-worker proof readiness from hosted-dashboard proof checklists,
  preserving Real-Cost-sourced hosted-dashboard proof metadata when present,
  without starting remote workers or changing routing;
- check autonomous-scheduling proof readiness from the latest
  Real-Cost-sourced remote-worker proof checklist when one exists, preserving
  remote-worker proof metadata and the remote-worker source proof's own source
  metadata when available, without scheduling autonomous work or changing
  routing;
- check browser/desktop adapter proof readiness from the latest
  Real-Cost-sourced autonomous-scheduling proof checklist when one exists,
  preserving autonomous-scheduling proof metadata and the autonomous-scheduling
  source proof's own source metadata when available, without operating browser
  or desktop adapters;
- check CI Deploy proof readiness from the latest Real-Cost-sourced
  browser/desktop adapter proof checklist when one exists, preserving
  browser/desktop adapter proof metadata and the browser/desktop adapter
  source proof's own source metadata when available, without running CI or
  deploys;
- check budget-enforcement proof readiness from the latest
  Real-Cost-sourced CI Deploy proof checklist when one exists, preserving CI
  Deploy proof metadata and the CI Deploy source proof's own source metadata
  when available, without enforcing budgets, running CI/deploys, or changing
  routing;
- check trust-promotion proof readiness from the latest Real-Cost-sourced
  Budget Enforcement proof checklist when one exists, preserving Budget
  Enforcement proof metadata and the Budget Enforcement source proof's own
  source metadata when available, without promoting trust, enforcing budgets,
  or changing routing;
- check automatic-retry proof readiness from Trust Promotion proof checklists
  preserving Real-Cost-sourced Trust Promotion proof metadata when present,
  without retrying or replaying work, promoting trust, or changing routing;
- check real-cost-tracking proof readiness from Automatic Retry proof
  checklists, preserving Real-Cost-sourced Automatic Retry proof metadata when
  present, without tracking spend, retrying, or changing routing;
- audit expansion-goal completion posture, build an operator decision brief,
  index evidence, prepare manual review choices, and record pending operator
  decision posture without approving, promoting, enabling, routing, or
  mutating external systems;
- prepare a report-only Expansion Operator Approval Draft from usable pending
  decision ledgers while keeping draft rows `draft_only`, approval request
  status `not_created`, and `created_approval_requests: 0`;
- review draft approval-request packets against the current `approval_requests`
  contract while keeping `created_approval_requests: 0` and blocking current
  requests on `approval_request_subject_not_modeled`;
- prepare a report-only approval schema decision that recommends an
  `operator_approval_requests` table for external and capability approvals
  without applying a migration or creating approval rows;
- prepare a report-only schema migration plan, approval request, and pending
  decision ledger for the future `operator_approval_requests` table while
  applying no migration, creating no table, creating no approval rows, and
  taking no operator action;
- prepare a report-only schema migration action checklist that leaves
  `selected_action=none` and records no operator action while preserving the
  allowed manual choices;
- prepare a report-only schema migration selection packet that still leaves
  `selected_action=none`, records no operator selection, and requires explicit
  operator input before any action can be taken;
- record proposed eval candidates when verifier or workflow gaps are discovered;
- promote repeated successful eval runs into reusable playbook files;
- prefer lower-complexity queue items when candidate scores tie;
- write activity, run, memory, learning, and eval artifacts;
- generate the next iteration packet from live momentum queues;
- generate a static dashboard with queue health, handoff reviews,
  eval-after-change checks, learning distillation, budget/trust posture,
  dispatch posture history, playbooks, eval candidates, approvals, stuck tasks,
  incidents, an operator cockpit for active approvals/effects/worktrees,
  recent runs, learnings, and evals;
- run a first-milestone regression eval.

## Commands

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
python3 -m agent_os.cli register-project <name> --path /path/to/git/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli run-goal "Make a verified local change" --project <name> --isolation worktree --command "<safe local command>"
python3 -m agent_os.cli approvals
python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "local approval"
python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator
python3 -m agent_os.cli github-handoff <effect_id> --remote origin --base main --title "Draft PR title"
python3 -m agent_os.cli cleanup-worktrees --confirm --decided-by operator --reason "terminal worktree reviewed"
python3 -m agent_os.cli resolve-incident <incident_id> --resolved-by operator --note "local resolution note"
python3 -m agent_os.cli queue-health
python3 -m agent_os.cli handoff-review
python3 -m agent_os.cli eval-after-change --change "Describe the harness change" --file agent_os/cli.py
python3 -m agent_os.cli distill-learnings --min-occurrences 3
python3 -m agent_os.cli budget-trust-posture
python3 -m agent_os.cli dispatch-posture-history
python3 -m agent_os.cli dispatch-posture-staleness
python3 -m agent_os.cli dispatch-posture-refresh
python3 -m agent_os.cli capability-expansion-ledger
python3 -m agent_os.cli capability-readiness-review
python3 -m agent_os.cli capability-proof-gap-index
python3 -m agent_os.cli capability-approval-boundary-matrix
python3 -m agent_os.cli capability-evidence-collection-plan
python3 -m agent_os.cli capability-promotion-gate-checklist
python3 -m agent_os.cli capability-promotion-decision-ledger
python3 -m agent_os.cli capability-trust-promotion-audit
python3 -m agent_os.cli capability-automatic-retry-audit
python3 -m agent_os.cli capability-real-cost-tracking-audit
python3 -m agent_os.cli hosted-dashboard-proof-checklist
python3 -m agent_os.cli remote-worker-proof-checklist
python3 -m agent_os.cli autonomous-scheduling-proof-checklist
python3 -m agent_os.cli browser-desktop-adapter-proof-checklist
python3 -m agent_os.cli ci-deploy-proof-checklist
python3 -m agent_os.cli budget-enforcement-proof-checklist
python3 -m agent_os.cli trust-promotion-proof-checklist
python3 -m agent_os.cli automatic-retry-proof-checklist
python3 -m agent_os.cli real-cost-tracking-proof-checklist
python3 -m agent_os.cli goal-completion-audit
python3 -m agent_os.cli expansion-decision-brief
python3 -m agent_os.cli expansion-decision-evidence-index
python3 -m agent_os.cli expansion-operator-review-checklist
python3 -m agent_os.cli expansion-operator-decision-ledger
python3 -m agent_os.cli expansion-operator-approval-draft
python3 -m agent_os.cli expansion-operator-approval-request-review
python3 -m agent_os.cli expansion-operator-approval-schema-decision
python3 -m agent_os.cli expansion-operator-approval-schema-migration-plan
python3 -m agent_os.cli expansion-operator-approval-schema-migration-approval-request
python3 -m agent_os.cli expansion-operator-approval-schema-migration-decision-ledger
python3 -m agent_os.cli expansion-operator-approval-schema-migration-action-checklist
python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-packet
python3 -m agent_os.cli eval-candidates
python3 -m agent_os.cli playbooks
python3 -m agent_os.cli iterate
python3 -m agent_os.cli sweep-stuck --timeout-seconds 1800
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli eval
python3 -m pytest tests/test_first_milestone.py -q
```

## Key Files

- `contracts.md`: implementation contract and v1 safety boundary.
- `docs/OPERATING_SUMMARY.md`: compact architecture and first milestone summary.
- `docs/runtime-capability-matrix.md`: detected runtime capabilities and dispositions.
- `docs/tutorial-first-loop.md`: step-by-step local loop walkthrough.
- `docs/tutorial-approval-gated-coding.md`: worktree-isolated coding run
  walkthrough with evidence, approval review, GitHub handoff, and cleanup.
- `docs/suggested-use.md`: operator guidance, prompts, and practical next slices.
- `docs/next-iteration.md`: generated packet for the next implementation pass.
  Queue items may include `<!-- score=N complexity=N -->`; equal scores choose
  the lower complexity item before queue order.
- `docs/playbooks.md`: generated index of reusable local playbooks.
- `docs/handoff-review.md`: generated report for blocked tasks and handoffs
  that do not reference the current iteration packet.
- `docs/eval-after-change.md`: generated report linking a named harness
  behavior change to the eval suite run that covered it.
- `docs/learning-distillation.md`: generated report for repeated learning
  patterns promoted into root `knowledge.md`.
- `docs/budget-trust-posture.md`: generated report for local budget/trust
  posture metadata. Report-only; no enforcement or trust promotion.
- `docs/dispatch-posture-history.md`: generated history summary over recent
  report-only dispatch posture snapshots.
- `docs/dispatch-posture-staleness.md`: generated freshness review over recent
  report-only posture snapshot timestamps.
- `docs/dispatch-posture-refresh.md`: generated report-only recommendation for
  manual posture refresh commands from the latest staleness review.
- `docs/capability-expansion-ledger.md`: generated report-only ledger for
  deferred autonomy surfaces and the proof each still needs.
- `docs/capability-readiness-review.md`: generated report-only review of the
  latest expansion ledger, including missing evidence for each deferred
  capability.
- `docs/capability-proof-gap-index.md`: generated report-only index of proof
  gaps from the latest readiness review.
- `docs/capability-approval-boundary-matrix.md`: generated report-only matrix
  mapping proof gaps to explicit approval boundaries.
- `docs/capability-evidence-collection-plan.md`: generated report-only plan
  for manually supplying proof evidence required by the latest approval
  boundaries.
- `docs/capability-promotion-gate-checklist.md`: generated report-only
  checklist of blocked promotion gates from the latest evidence collection
  plan.
- `docs/capability-promotion-decision-ledger.md`: generated report-only
  ledger of deferred/manual promotion decisions from the latest gate checklist.
- `docs/capability-trust-promotion-audit.md`: generated report-only audit of
  trust-promotion readiness from the latest promotion decision ledger.
- `docs/capability-automatic-retry-audit.md`: generated report-only audit of
  automatic-retry readiness from the latest trust-promotion audit.
- `docs/capability-real-cost-tracking-audit.md`: generated report-only audit
  of real-cost-tracking readiness from the latest automatic-retry audit.
- `docs/hosted-dashboard-proof-checklist.md`: generated report-only checklist
  of hosted-dashboard proof readiness from the latest Real Cost Tracking proof
  checklist, including Real-Cost-sourced Real Cost Tracking proof metadata when
  present, with legacy real-cost-tracking audit fallback.
- `docs/remote-worker-proof-checklist.md`: generated report-only checklist of
  remote-worker proof readiness from the latest hosted-dashboard proof
  checklist, including Real-Cost-sourced hosted-dashboard proof metadata when
  present and the hosted dashboard source proof's own source metadata when
  available.
- `docs/autonomous-scheduling-proof-checklist.md`: generated report-only
  checklist of autonomous-scheduling proof readiness from the latest
  Real-Cost-sourced remote-worker proof checklist when one exists, including
  remote-worker proof metadata and the remote-worker source proof's own source
  metadata when available.
- `docs/browser-desktop-adapter-proof-checklist.md`: generated report-only
  checklist of browser/desktop adapter proof readiness from the latest
  Real-Cost-sourced autonomous-scheduling proof checklist when one exists,
  including autonomous-scheduling proof metadata and the
  autonomous-scheduling source proof's own source metadata when available.
- `docs/ci-deploy-proof-checklist.md`: generated report-only checklist of
  CI Deploy proof readiness from the latest Real-Cost-sourced browser/desktop
  adapter proof checklist when one exists, including browser/desktop adapter
  proof metadata and the browser/desktop adapter source proof's own source
  metadata when available.
- `docs/budget-enforcement-proof-checklist.md`: generated report-only
  checklist of budget-enforcement proof readiness from the latest
  Real-Cost-sourced CI Deploy proof checklist when one exists, including CI
  Deploy proof metadata and the CI Deploy source proof's own source metadata
  when available.
- `docs/trust-promotion-proof-checklist.md`: generated report-only checklist
  of trust-promotion proof readiness from the latest Real-Cost-sourced Budget
  Enforcement proof checklist when one exists, including Budget Enforcement
  proof metadata and the Budget Enforcement source proof's own source
  metadata when available.
- `docs/automatic-retry-proof-checklist.md`: generated report-only checklist
  of automatic-retry proof readiness from the latest Trust Promotion proof
  checklist, including Real-Cost-sourced Trust Promotion proof metadata when
  present.
- `docs/real-cost-tracking-proof-checklist.md`: generated report-only
  checklist of real-cost-tracking proof readiness from the latest Automatic
  Retry proof checklist, including Real-Cost-sourced Automatic Retry proof
  metadata when present.
- `docs/goal-completion-audit.md`: generated report-only expansion goal
  completion posture.
- `docs/expansion-decision-brief.md`: generated operator decision packet for
  external decisions and capability approvals.
- `docs/expansion-decision-evidence-index.md`: generated evidence map for
  the operator decision packet.
- `docs/expansion-operator-review-checklist.md`: generated manual operator
  review choices and allowed actions.
- `docs/expansion-operator-decision-ledger.md`: generated pending/manual
  operator decision posture; allowed actions are not actions taken.
- `docs/expansion-operator-approval-draft.md`: generated draft-only
  approval-request packet from the latest usable decision ledger; it does not
  create `approval_requests` rows.
- `docs/expansion-operator-approval-request-review.md`: generated report-only
  review of draft approval requests against the current `approval_requests`
  contract; capability requests stay blocked by
  `approval_request_subject_not_modeled` and no approval rows are created.
- `docs/expansion-operator-approval-schema-decision.md`: generated report-only
  schema decision packet that recommends `operator_approval_requests` for
  non-task approvals without applying migrations.
- `docs/expansion-operator-approval-schema-migration-plan.md`: generated
  report-only migration plan for a future `operator_approval_requests` table;
  it records proposed columns, indexes, and steps without creating the table.
- `docs/expansion-operator-approval-schema-migration-approval-request.md`:
  generated report-only approval request packet for applying the planned
  schema; it records allowed operator actions without taking one.
- `docs/expansion-operator-approval-schema-migration-decision-ledger.md`:
  generated report-only pending/manual decision ledger for the schema
  migration approval request; it records one pending operator action without
  applying the migration or creating approval rows.
- `docs/expansion-operator-approval-schema-migration-action-checklist.md`:
  generated report-only manual action checklist for the schema migration
  decision ledger; it keeps `selected_action=none` and records no action
  taken.
- `docs/expansion-operator-approval-schema-migration-selection-packet.md`:
  generated report-only operator selection input packet for the schema
  migration action checklist; it keeps `selected_action=none` and records no
  operator selection.
- `docs/expansion-operator-approval-schema-migration-selection-input-template.md`:
  generated report-only operator input template for the schema migration
  selection packet; it lists required fields while recording no operator input
  or selection.
- `docs/dashboard.md`: generated operational view with an operator cockpit for
  active runs, registered projects, approval inbox, proposed effects,
  verification status, recent worktrees, queue health, approvals, handoff
  reviews, eval-after-change checks, learning distillation,
  budget/trust posture, dispatch posture history, dispatch posture snapshot
  review, dispatch posture refresh recommendation, capability expansion
  ledger, capability readiness review, capability proof gap index, capability
  approval boundary matrix, capability evidence collection plan, capability
  promotion gate checklist, capability promotion decision ledger, capability
  trust promotion audit, capability automatic retry audit, capability real cost
  tracking audit, hosted dashboard proof checklist, remote worker proof
  checklist, autonomous scheduling proof checklist, browser desktop adapter
  proof checklist, CI Deploy proof checklist, budget enforcement proof
  checklist, trust promotion proof checklist, automatic retry proof checklist,
  real cost tracking proof checklist, goal completion audit, expansion
  decision brief, expansion decision evidence index, expansion operator review
  checklist, expansion operator decision ledger, expansion operator approval
  draft, expansion operator approval request review, expansion operator
  approval schema decision, expansion operator approval schema migration plan,
  expansion operator approval schema migration approval request, expansion
  operator approval schema migration decision ledger, expansion operator
  approval schema migration action checklist, expansion operator approval
  schema migration selection packet, expansion operator approval schema
  migration selection input template, playbooks, eval candidates, iteration
  loop state, GitHub handoff packets, stuck tasks, incidents, and recent
  activity.
- `knowledge.md`: stable human-readable knowledge promoted from repeated local
  evidence.
- `playbooks/`: generated reusable playbook files from repeated successful evals.
- `tasks.md`: live momentum queues.
- `agent_os/`: Python harness implementation.
- `tests/`: first-milestone regression coverage.
- `runs/`: human-readable run activity, event logs, and summaries.
- `evals/`: eval candidates and results.
- `projects/bootstrap/`: canonical file pack for the bootstrap project.
