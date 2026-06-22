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
GitHub handoff -> operator-supplied CI/deploy evidence -> local evidence record
task/category -> profile routing decision -> durable selection record
routing decision -> read-only subagent delegation contract -> evidence artifact
delegation contract -> structured result ingestion -> completed local evidence
completed delegation result -> proposed memory entry -> operator approval/archive
useful run evidence -> proposed SKILL.md -> operator approval/archive
run evidence -> human review -> evidence index -> conceptual replay summary
goal state -> deterministic steering review -> next action -> operator inbox
approved operator request decisions -> proposed effect records -> blocked activation
proposed operator effects -> local application record -> capability-specific guard
applied capability effects -> pending activation tasks -> explicit evidence gates
pending activation tasks -> capability activation contracts -> blocked evidence/approval packets
activation contracts -> operator evidence ingestion -> local more-evidence decisions
more-evidence decisions -> pending follow-up evidence tasks -> task graph
follow-up evidence tasks -> routing decisions -> read-only delegation packets
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
network action was taken. After a handoff exists, it can ingest
operator-supplied CI/deploy evidence as a local record without calling CI,
deploying, or mutating GitHub. It now also creates safe local profile defaults
for planner/coder/scout/tester/evaluator work and records routing decisions
for task or category selection. It can also create read-only subagent
delegation contracts from those routing decisions without starting a subagent
or calling a model provider, then ingest operator-supplied structured
delegation results as completed local evidence. Completed delegation results
can become proposed memory entries, but they do not become active memory until
approved. Useful run evidence can also become proposed project skills under
`.clanker/skills/`, but those skills remain proposed until an operator
approves them. Run evidence can now be summarized with human-first `review`,
`evidence`, and `replay-summary` commands that write local Markdown packets
without rerunning work or approving effects. Deterministic steering reviews
can now inspect local goals, tasks, approvals, and incidents to recommend a
next operator action and populate a local inbox without executing work. The
operator approval schema chain can now cross its first explicit approval
boundary by creating the local `operator_approval_requests` table only after
an operator supplies an approved selection. After that table exists, an
approved row-application command can create pending local
`operator_approval_requests` rows from expansion approval drafts. A decision
command can then record local approve/defer/more-evidence decisions for those
pending rows while still leaving legacy `approval_requests`, capability
activation, trust promotion, and external systems untouched. Approved local
operator request decisions can now be converted into `proposed` effect records
for external-decision and capability surfaces, preserving the approval link
and idempotency key while still taking zero activation actions. Those proposed
effects can then be applied as local records, advancing effect status to
`applied` while still recording `capability_enabled=false`,
`activation_actions_taken=0`, and no external mutation. Applied capability
effects can now be materialized into pending high-risk activation-gate tasks,
one per capability, so the next work happens in the task graph with evidence
requirements instead of becoming silent capability enablement. Pending
activation tasks can now be converted into capability-specific activation
contracts that record required artifacts, required commands,
`explicit_operator_approval_required`, and `blocked_until_evidence_verified`
while keeping `approval_requests_created=0`, `activation_actions_taken=0`,
and `activation_allowed=false`. Operators can now attach local evidence to
those contracts and record approve/defer/more-evidence decisions; the current
safe path records `request_more_evidence` for the blocked proof state while
still creating no approval rows and taking no activation actions. Those
more-evidence decisions can now become pending high-risk follow-up evidence
tasks in the task graph, so the next proof work is executable queue state
rather than a chat reminder. Those follow-up tasks can now be routed to the
read-only evaluator profile and materialized as pending delegation packets
with local JSON artifacts, without starting a subagent or calling a model
provider.
Deployments and other external side effects remain blocked unless an
implemented flow explicitly models evidence, authorization, rollback, and
verification.

## Repository Metadata

GitHub description:

```text
Local-first agent operating system harness for goal loops, task graphs, verification evidence, approvals, and operator-visible autonomy.
```

Suggested GitHub topics:

```text
agent-operating-system, agentic-ai, ai-agents, agent-os, agent-orchestration, subagent-delegation, local-first, coding-agents, automation, sqlite, approval-workflow, human-in-the-loop, cli-tool, developer-tools, worktrees, verification, operator-dashboard, evals, markdown, python
```

## Quick Start

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli evidence <run_id>
python3 -m agent_os.cli replay-summary <run_id>
python3 -m agent_os.cli steer <goal_id>
python3 -m agent_os.cli next-action <goal_id>
python3 -m agent_os.cli inbox
python3 -m agent_os.cli profiles
python3 -m agent_os.cli route --category repo_search --project bootstrap
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
python3 -m agent_os.cli ci-deploy-evidence <github_handoff_id> --provider github-actions --status success --external-run-id 123 --url https://github.com/owner/repo/actions/runs/123
python3 -m agent_os.cli profiles
python3 -m agent_os.cli route <task_id>
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli record-delegation-result <delegation_id> --summary "Relevant files identified." --output-json '{"files":["agent_os/cli.py"]}'
python3 -m agent_os.cli memory propose-from-delegation <delegation_id> --key relevant_cli_files
python3 -m agent_os.cli memory list --project bootstrap
python3 -m agent_os.cli skill propose --project bootstrap --name adding-cli-commands --description "Procedure for adding tested CLI commands." --from-run <run_id>
python3 -m agent_os.cli skills --project bootstrap
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli evidence <run_id>
python3 -m agent_os.cli replay-summary <run_id>
python3 -m agent_os.cli cleanup-worktrees --confirm --reason "committed branch kept"
```

This creates a worktree and approval packet, then creates the local worktree
commit only after approval and a fresh evidence recheck. Cleanup removes clean
terminal worktrees only after an explicit confirmed cleanup decision. The
GitHub handoff step writes local evidence and command strings; it does not push
or open the PR for you. The CI/deploy evidence step records what the operator
supplies; it does not call GitHub Actions, run CI, or deploy. The profile
routing commands create `.clanker/profiles.yml`, store safe default profiles
and routing rules in SQLite, and record selection decisions. The delegation
command stores a scoped read-only contract and evidence artifact; it does not
start a subagent, call external models, approve work, commit, or mutate files.
`record-delegation-result` attaches structured operator-supplied output to an
existing delegation, validates the expected schema family, marks it completed,
and writes a local result artifact while still recording `network_actions_taken=0`.
`memory propose-from-delegation` turns a completed delegation result into a
proposed memory entry with local JSON evidence; it does not activate memory
until `memory approve <memory_id>` is run. `skill propose` turns useful run
evidence into a proposed `.clanker/skills/<name>/SKILL.md` plus SQLite skill
and version records; it does not make the skill active until `skill approve
<skill_id>` is run.
`review <run_id>` writes `runs/<run_id>/review.md` for operator decisions,
`evidence <run_id>` writes `runs/<run_id>/evidence-index.md`, and
`replay-summary <run_id>` writes `runs/<run_id>/replay-summary.md` as a
conceptual replay map. These commands do not rerun work, approve effects,
commit, push, deploy, or mutate external systems.
`steer <goal_id>` writes `docs/steering-review.md` and a `steering_reviews`
SQLite row. `next-action <goal_or_project>` refreshes a steering review and
prints the recommended operator move. `inbox` lists recent steering reviews
that require an operator plus pending approvals and open incidents. These
commands do not execute tasks, approve work, retry, commit, push, deploy, or
mutate external systems.

## Tutorials And Suggested Use

- [Run the first local loop](docs/tutorial-first-loop.md)
- [Run an approval-gated coding task](docs/tutorial-approval-gated-coding.md)
- [Record profile routing, delegation, and delegation results](docs/tutorial-subagent-delegation-results.md)
- [Propose and approve reusable skills](docs/tutorial-skill-proposals.md)
- [Review run evidence and replay summaries](docs/tutorial-run-review.md)
- [Use steering reviews, next actions, and the inbox](docs/tutorial-steering-inbox.md)
- [Apply the operator approval request schema](docs/tutorial-operator-approval-schema.md)
- [Create operator approval effects and activation tasks](docs/tutorial-operator-approval-effect-proposals.md)
- [Create capability activation contracts](docs/tutorial-capability-activation-contracts.md)
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
- ingest operator-supplied CI/deploy evidence for a GitHub handoff packet,
  store it in SQLite and JSON, and preserve `network_actions_taken=0`;
- create safe default planner/coder/scout/tester/evaluator profile records and
  routing rules with `.clanker/profiles.yml` as a human-readable local config;
- record profile routing decisions for task ids or category/project pairs,
  including operator profile overrides, without changing worker claiming or
  calling a model provider;
- record read-only subagent delegation contracts from routing decisions,
  including scoped prompts, input context, allowed tools, forbidden actions,
  expected output schema, local budget hints, and JSON artifacts, without
  starting subagents or mutating state;
- ingest structured read-only delegation results, validate them against the
  expected schema family, mark delegations completed, and write local result
  artifacts while preserving no-provider and no-network non-claims;
- propose durable memory entries manually or from completed delegation results,
  list them by project, approve them into active memory, or archive them,
  without silently promoting proposed facts;
- propose reusable project skills from run evidence, write
  `.clanker/skills/<name>/SKILL.md`, list/show proposed skills, approve them
  into active skills, or archive them with decision metadata;
- write human-first run review packets, evidence indexes, and conceptual
  replay summaries for existing runs while preserving `network_actions_taken=0`
  and `external_mutations_taken=0`;
- write deterministic steering reviews for goals, recommend the next local
  operator action for a goal or project, and list operator-worthy inbox items
  from steering reviews, approvals, and incidents;
- create the local `operator_approval_requests` table from the schema migration
  selection template after an explicit `approve` selection, recording applied
  columns/indexes and idempotent repeat attempts while creating no approval
  rows;
- create capability activation contracts from pending activation-gate tasks,
  one per capability, while keeping approval creation, activation actions, and
  capability enablement blocked;
- attach operator-supplied evidence to capability activation contracts and
  record local operator decisions without enabling capabilities;
- create pending follow-up evidence tasks from activation contracts that need
  more evidence, without enabling capabilities or creating approval rows;
- route capability follow-up evidence tasks to read-only evaluator delegation
  packets without starting subagents or calling model providers;
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
- create pending local `operator_approval_requests` rows from expansion
  approval drafts only after the schema exists and an operator supplies an
  approved row-creation selection, while creating no legacy
  `approval_requests` rows and deciding nothing;
- record local decisions on pending `operator_approval_requests` rows with
  explicit operator input while still creating no legacy `approval_requests`
  rows, enabling no capability, and taking no external action;
- create proposed effect records from approved `operator_approval_requests`
  rows, linking each effect to its source operator request and idempotency key
  while taking no activation, routing, scheduling, trust-promotion, retry,
  spend-tracking, CI, deploy, or external action;
- apply proposed operator approval effects as local records only, preserving
  per-effect `applied` status, result evidence, idempotency, and
  `capability_enabled=false` while still taking no activation or external
  action;
- create pending capability-specific activation-gate tasks from applied
  capability effects, linking each task to its source effect while keeping
  every capability disabled until explicit evidence and approval gates pass;
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
python3 -m agent_os.cli ci-deploy-evidence <github_handoff_id> --provider github-actions --status success --external-run-id <run_id> --url <run_url>
python3 -m agent_os.cli expansion-operator-approval-effect-proposals
python3 -m agent_os.cli expansion-operator-approval-effect-apply --operator-id operator --selection-note "Apply approved local operator approval effect proposals as local records only." --evidence-reference docs/expansion-operator-approval-effect-proposals.md
python3 -m agent_os.cli capability-activation-tasks
python3 -m agent_os.cli capability-activation-contracts
python3 -m agent_os.cli capability-activation-evidence --all --evidence-kind proof_checklist --evidence-reference docs/capability-activation-contracts.md --verification-command "python3 -m agent_os.cli capability-activation-contracts" --verification-status blocked --recorded-by operator --summary "Current activation contracts are present but still missing capability-specific proof."
python3 -m agent_os.cli capability-activation-decide --operator-id operator --selected-action request_more_evidence --selection-note "Requested capability-specific proof before any activation decision." --evidence-reference docs/capability-activation-evidence.md
python3 -m agent_os.cli capability-activation-followups
python3 -m agent_os.cli capability-activation-followup-delegations
python3 -m agent_os.cli profiles
python3 -m agent_os.cli route <task_id>
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli record-delegation-result <delegation_id> --summary "Relevant files identified." --output-json '{"files":["agent_os/cli.py"]}'
python3 -m agent_os.cli memory propose --project <name> --key test_command --value "python3 -m pytest -q"
python3 -m agent_os.cli memory propose-from-delegation <delegation_id> --key relevant_cli_files
python3 -m agent_os.cli memory approve <memory_id> --approved-by operator
python3 -m agent_os.cli skill propose --project <name> --name adding-cli-commands --description "Procedure for adding tested CLI commands." --from-run <run_id>
python3 -m agent_os.cli skills --project <name>
python3 -m agent_os.cli skill show <skill_id>
python3 -m agent_os.cli skill approve <skill_id> --approved-by operator
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
python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-input-template
python3 -m agent_os.cli expansion-operator-approval-schema-migration-apply --operator-id operator --selected-action approve --selection-note "Approved local operator approval request schema." --evidence-reference docs/expansion-operator-approval-schema-migration-selection-input-template.md
python3 -m agent_os.cli expansion-operator-approval-request-rows-apply --operator-id operator --selected-action approve --selection-note "Approved local operator approval request row creation after reviewing the draft packet." --evidence-reference docs/expansion-operator-approval-draft.md
python3 -m agent_os.cli expansion-operator-approval-request-decide --operator-id operator --selected-action approve --selection-note "Approved pending operator approval requests after reviewing evidence." --evidence-reference docs/expansion-operator-approval-request-rows-application.md
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
- `docs/tutorial-subagent-delegation-results.md`: profile routing,
  read-only delegation contracts, and structured result ingestion walkthrough.
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
- `docs/expansion-operator-approval-schema-migration-application.md`:
  generated application evidence for an explicit operator schema selection;
  an approved selection can create the local `operator_approval_requests`
  table while still creating zero approval rows.
- `docs/expansion-operator-approval-request-rows-application.md`:
  generated application evidence for an explicit operator row-creation
  selection; an approved selection can create pending local
  `operator_approval_requests` rows while still creating zero legacy
  `approval_requests` rows and deciding nothing.
- `docs/expansion-operator-approval-request-decisions.md`: generated decision
  evidence for explicit operator selections on pending
  `operator_approval_requests` rows; decisions update local row status while
  still creating zero legacy `approval_requests` rows and enabling nothing.
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
  migration selection input template, operator approval schema migration
  applications, operator approval request row applications, operator approval
  request decisions, playbooks, eval candidates, iteration loop state, GitHub
  handoff packets, stuck tasks, incidents, and recent activity.
- `knowledge.md`: stable human-readable knowledge promoted from repeated local
  evidence.
- `playbooks/`: generated reusable playbook files from repeated successful evals.
- `tasks.md`: live momentum queues.
- `agent_os/`: Python harness implementation.
- `tests/`: first-milestone regression coverage.
- `runs/`: human-readable run activity, event logs, and summaries.
- `evals/`: eval candidates and results.
- `projects/bootstrap/`: canonical file pack for the bootstrap project.
