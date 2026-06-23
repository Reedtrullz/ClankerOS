# Local Operating Summary

## Default Architecture

Use a harness-wrapper architecture around the current Codex runtime. The system
state lives in explicit project files, a SQLite control-plane database, task
events, run artifacts, and memory files. The first executable implementation is
a single local worker with deterministic verification; later versions can add
browser, desktop, remote workers, dashboards, and specialized harnesses.

Core layers for the bootstrap:

- Control plane: SQLite in WAL mode plus CLI output, markdown mirrors, and a
  static dashboard.
- Task graph: goals decompose into typed tasks with status, ownership,
  verification plans, evidence, and artifacts.
- Execution fabric: a pull-based worker claims pending tasks, executes safe
  local task types, and records lifecycle events.
- Approval gate: runnable risky or unknown tasks move to `waiting_approval`
  with a persisted `approval_requests` record before any worker claim.
- Project registry: local git repositories can be registered with a resolved
  git root, default test command, and allowed write roots before coding-agent
  runs target them.
- Worktree coding loop: a high-risk coding goal can run a constrained command
  inside an isolated git worktree, capture command/test/diff evidence, and
  record a proposed `local_git_commit` effect that waits for operator approval.
- Worktree cleanup loop: terminal local coding worktrees can be previewed and
  removed only after an explicit `cleanup-worktrees --confirm` decision. The
  cleanup writes SQLite and JSON evidence, removes clean committed/blocked/
  superseded worktrees, and blocks dirty worktrees without force deletion.
- GitHub handoff loop: a committed `local_git_commit` effect can produce a
  local handoff packet with branch, commit, remote, push command, and draft PR
  command while recording `network_actions_taken=0`. The loop does not push or
  open a PR.
- CI/deploy evidence ingestion: an operator can attach CI or deploy proof to a
  GitHub handoff packet with `ci-deploy-evidence`. The record preserves
  provider, external run id, URL, commit, branch, handoff, and JSON evidence
  while recording `network_actions_taken=0`; it does not fetch CI, run CI, or
  deploy.
- Profile routing: safe default planner, coder, scout, tester, and evaluator
  profiles plus routing rules can be materialized into SQLite and
  `.clanker/profiles.yml`. `route` records task/category selection decisions,
  including operator overrides, without claiming tasks, dispatching subagents,
  calling model providers, or changing approval gates.
- Subagent delegation records: `delegate` consumes a task routing decision and
  stores a read-only delegation contract with scoped prompt, input context,
  allowed tools, forbidden actions, expected output schema, budget hints, and
  a JSON artifact. Delegation records do not start subagents, call model
  providers, approve work, commit, write files, or mutate external state.
- Delegation result ingestion: `record-delegation-result` attaches structured
  operator-supplied output to an existing delegation, validates the expected
  schema family, marks the delegation completed, and writes a local result
  artifact while preserving no-provider, no-network, and no-external-mutation
  non-claims.
- Memory proposal lifecycle: `memory propose` and
  `memory propose-from-delegation` create `memory_entries` rows with
  `status=proposed` plus local JSON evidence. `memory approve` promotes a
  proposed entry to `active`, and `memory archive` marks an entry archived.
  Delegation-sourced memory proposals require a completed delegation result and
  never silently write active memory.
- Skill proposal lifecycle: `skill propose` creates a proposed skill row,
  a first `skill_versions` row, and `.clanker/skills/<name>/SKILL.md` from
  verified run evidence. `skills` lists proposals, `skill show` reads back the
  markdown, `skill approve` promotes a proposed skill to `active`, and
  `skill archive` records a local archive decision. Proposed skills are not
  active until approved.
- Run evidence review: `review <run_id>` writes a human-first
  `runs/<run_id>/review.md`, `evidence <run_id>` writes
  `runs/<run_id>/evidence-index.md`, and `replay-summary <run_id>` writes
  `runs/<run_id>/replay-summary.md`. The reports summarize existing local run
  rows, task evidence, events, artifacts, approvals, incidents, effects,
  delegations, memory entries, skills, and eval candidates without rerunning
  commands, approving effects, committing, pushing, deploying, or mutating
  external systems.
- Steering review: `steer <goal_id>` writes a deterministic
  `docs/steering-review.md` plus a `steering_reviews` row from local goal,
  task, approval, and incident state. `next-action <goal_or_project>` refreshes
  the review and prints the recommended operator action. `inbox` lists
  operator-worthy steering reviews, pending approvals, and open incidents.
  These commands do not execute tasks, approve requests, retry, commit, push,
  deploy, or mutate external systems.
- Operator cockpit: the dashboard starts with active runs, registered projects,
  approval inbox, proposed effects, verification status, recent worktrees,
  GitHub handoffs, CI/deploy evidence, profile routing decisions, subagent
  delegations, steering reviews, memory proposals, skill proposals, and the
  next recommended operator action.
- Operator approval effect proposals: approved local
  `operator_approval_requests` rows can be converted into idempotent
  `proposed` effect records for external-decision and capability surfaces
  while taking zero activation actions and creating zero legacy
  `approval_requests` rows.
- Operator approval effect application: proposed operator approval effects can
  be applied as local records with per-effect `status=applied` and explicit
  `capability_enabled=false` result evidence while still taking zero
  activation actions and mutating no external systems.
- Capability activation tasks: applied capability proposal effects can be
  materialized into pending high-risk `capability_activation_task` rows, one
  per capability, with evidence and verification gates that keep
  `activation_actions_taken=0` and `capability_enabled=false` until a later
  explicit capability-specific approval path exists.
- Capability activation contracts: pending activation-gate tasks can be
  converted into durable per-capability evidence and approval contracts with
  required artifacts, required commands, `explicit_operator_approval_required`,
  and `blocked_until_evidence_verified` while keeping
  `approval_requests_created=0`, `activation_actions_taken=0`, and
  `activation_allowed=false`.
- Capability activation evidence and decisions: operators can attach local
  evidence rows and JSON artifacts to activation contracts, then record local
  approve/defer/more-evidence decisions. The safe current decision path records
  `request_more_evidence` for blocked proofs while keeping
  `approval_requests_created=0`, `activation_actions_taken=0`, and
  `activation_allowed=false`.
- Capability activation follow-ups: more-evidence activation decisions can be
  materialized into pending high-risk `capability_activation_followup_task`
  rows that point back to the source contract and decision. This turns blocked
  proof decisions into task graph work while still creating no approval rows
  and taking no activation actions.
- Capability activation follow-up delegations: pending follow-up evidence tasks
  can be routed to `evidence_review` and materialized as read-only evaluator
  delegation packets with local JSON artifacts. The packets preserve source
  task evidence and required proof commands while keeping subagent execution,
  model-provider calls, approval rows, and activation actions at zero.
- Capability activation follow-up results: completed read-only evaluator
  delegation results can be ingested into local result records and JSON
  artifacts. The records preserve evaluator findings for operator review while
  keeping proof satisfaction, approval rows, activation actions, and capability
  enablement blocked.
- Capability activation follow-up result decisions: operators can record local
  accept-keep-blocked, request-more-evidence, or defer decisions for ingested
  follow-up result records. The decisions preserve blocked proof state and keep
  approval row creation, activation actions, contract mutation, and capability
  enablement at zero.
- Capability activation follow-up result effect proposals: accepted
  keep-blocked follow-up result decisions can be converted into idempotent
  `proposed` effect rows in the generic effects ledger. Each row links the
  source decision, result, delegation, follow-up task, contract, and capability
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result effect application: proposed
  accepted-blocked follow-up decision effects can be applied as local ledger
  records only. Application rows and applied effects preserve source decision,
  result, delegation, follow-up task, contract, and capability links while
  keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result tasks: applied accepted-blocked
  follow-up result effects can be materialized into pending downstream
  `capability_activation_followup_result_task` rows. Each task preserves
  source effect, application, result, delegation, follow-up task, contract,
  and capability links while keeping approval rows, external mutations,
  activation actions, activation allowance, and capability enablement at zero.
- Capability activation follow-up result task delegations: pending downstream
  follow-up result tasks can be routed to read-only evaluator delegation
  packets. Each packet preserves the next evidence-plan context while keeping
  subagent execution, model-provider calls, approval rows, external mutations,
  activation actions, activation allowance, and capability enablement at zero.
- Capability activation follow-up result task results: completed downstream
  proof-plan delegation packets can be ingested as local result records and
  JSON artifacts. Each result preserves the source effect, result, delegation,
  downstream task, contract, and capability links while keeping approval rows,
  external mutations, activation actions, activation allowance, capability
  enablement, and proof satisfaction at zero.
- Capability activation follow-up result task result effect proposals:
  accepted blocked downstream result decisions can be converted into
  idempotent `proposed` effect rows in the generic effects ledger. Each row
  links the source downstream decision, downstream result record, upstream
  follow-up result, source effect, downstream task, contract, and capability
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect application:
  proposed accepted-blocked downstream result decision effects can be applied
  as local ledger records only. Application rows and applied effects preserve
  source downstream decision, downstream result, upstream follow-up result,
  source effect, downstream task, contract, project, and capability links
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect tasks: applied
  downstream result decision effects can be materialized into pending
  downstream proof tasks. Each task preserves the source application,
  downstream decision, downstream result, upstream follow-up result, source
  effect, downstream task, contract, project, and capability links while
  keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task delegations:
  pending downstream result effect tasks can be routed to read-only evaluator
  delegation packets with local JSON artifacts. Each packet preserves the next
  evidence-plan context while keeping subagent execution, model-provider
  calls, approval rows, external mutations, activation actions, activation
  allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task results:
  completed downstream result effect delegation packets can be ingested as
  local result records and JSON artifacts. Each result preserves the source
  application, downstream decision, downstream result, upstream follow-up
  result, source effect, downstream task, contract, project, and capability
  links while keeping approval rows, external mutations, activation actions,
  activation allowance, capability enablement, and proof satisfaction at zero.
- Capability activation follow-up result task result effect task result
  decisions: operators can record local accept-keep-blocked,
  request-more-evidence, or defer decisions for downstream result effect task
  result records. Each decision preserves the blocked proof state while
  keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  proposals: accepted blocked downstream result effect task result decisions
  can be converted into idempotent `proposed` effect rows in the generic
  effects ledger. Each row links the source decision, result record,
  application, effect, delegation, task, contract, project, and capability
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  application: proposed accepted-blocked downstream result effect task result
  decision effects can be applied as local ledger records only. Application
  rows and applied effects preserve source decision, result record,
  application, effect, delegation, task, contract, project, and capability
  links while keeping approval row creation, external mutations, activation
  actions, activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  tasks: applied accepted-blocked downstream result effect task result decision
  effects can be materialized into pending downstream proof tasks. Each task
  preserves source decision, result record, application, effect, delegation,
  task, contract, project, and capability links while keeping approval row
  creation, external mutations, activation actions, activation allowance, and
  capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task delegations: pending downstream result effect task result effect tasks
  can be routed to read-only evaluator delegation packets with local JSON
  artifacts. Each packet preserves the next evidence-plan context while
  keeping subagent execution, model-provider calls, approval rows, external
  mutations, activation actions, activation allowance, and capability
  enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task results: completed downstream result effect task result effect
  delegation packets can be ingested as local result records and JSON
  artifacts. Each result preserves source decision, result, application,
  effect, delegation, task, contract, project, and capability links while
  keeping approval rows, external mutations, activation actions, activation
  allowance, capability enablement, and proof satisfaction at zero.
- Capability activation follow-up result task result effect task result effect
  task result decisions: operators can record accept-keep-blocked,
  request-more-evidence, or defer decisions for downstream result effect task
  result effect result records while keeping approval rows, external
  mutations, activation actions, activation allowance, capability enablement,
  and proof satisfaction at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect proposals: accepted blocked downstream result effect task
  result effect result decisions can be converted into idempotent `proposed`
  effect rows in the generic effects ledger. Each row links the source
  decision, result, application, effect, delegation, task, contract, project,
  and capability while keeping approval row creation, external mutations,
  activation actions, activation allowance, and capability enablement at zero.
- Verifier: each completed task is checked by a separate deterministic verifier.
- Incidents: failed verification opens a first-class incident record with JSON
  evidence under the run directory; operator resolution writes a companion JSON
  evidence file and records who resolved it, when, and why.
- Stuck detection: explicit local sweeps block stale active tasks and open
  `task_stuck` incidents without killing, retrying, or requeueing work.
- Queue health: repeated blocked or failed task groups are reported by project
  and task type without automatic retry or replay.
- Handoff review: blocked tasks and stale project handoffs are reported against
  the latest iteration packet before any automatic repair exists.
- Eval after change: named harness behavior changes can be linked to a local
  eval-suite run with explicit changed paths and run/result evidence.
- Eval candidates: verifier or workflow gaps write proposed eval cases with
  JSON and SQLite evidence before executable evals exist.
- Playbooks: repeated successful eval runs can be promoted into reusable
  markdown playbooks with an indexed SQLite row.
- Learning distillation: repeated run learnings can be grouped after volatile
  run-id normalization and promoted into root `knowledge.md` with report and
  SQLite evidence.
- Budget/trust posture: local task risk metadata can be reported with
  budget/trust state labels before any enforcement, trust promotion, or routing
  change exists.
- Dispatch posture history: recent report-only posture snapshots can be
  summarized for local metadata trends before any policy or routing behavior
  exists.
- Dispatch posture snapshot review: recent posture snapshot timestamps can be
  checked for freshness before any scheduled refresh, policy, or routing
  behavior exists.
- Dispatch posture refresh recommendation: persisted staleness reviews can be
  translated into manual operator command recommendations before any scheduler
  or automatic refresh behavior exists.
- Capability expansion ledger: deferred autonomy surfaces can be recorded with
  required evidence, next proof, approval boundary, and no routing effect before
  any surface is enabled.
- Capability readiness review: the latest expansion ledger can be checked for
  attached evidence and readiness gaps before any activation, routing, or
  follow-up automation exists.
- Capability proof gap index: the latest readiness review can be converted into
  an explicit proof-gap list before any proof generation, promotion, routing,
  or scheduler behavior exists.
- Capability approval boundary matrix: the latest proof-gap index can be
  converted into explicit operator approval-boundary rows before any approval,
  proof generation, promotion, routing, or scheduler behavior exists.
- Capability evidence collection plan: the latest approval-boundary matrix can
  be converted into manual proof-evidence collection items before any evidence
  capture, approval, promotion, routing, or scheduler behavior exists.
- Capability promotion gate checklist: the latest evidence collection plan can
  be converted into blocked or ready promotion gates before any evidence
  capture, approval, trust promotion, routing, or scheduler behavior exists.
- Capability promotion decision ledger: the latest promotion gate checklist can
  be converted into defer/manual-review decision rows before any approval,
  trust promotion, routing, or scheduler behavior exists.
- Capability trust promotion audit: the latest promotion decision ledger can be
  audited for trust-promotion readiness before any trust promotion, routing, or
  scheduler behavior exists.
- Capability automatic retry audit: the latest trust promotion audit can be
  audited for automatic-retry readiness before any retry, replay, routing, or
  scheduler behavior exists.
- Capability real cost tracking audit: the latest automatic retry audit can be
  audited for real-cost-tracking readiness before any spend tracking, budget
  enforcement, routing, or scheduler behavior exists.
- Hosted dashboard proof checklist: the latest Real-Cost-sourced Real Cost
  Tracking proof checklist can be checked for hosted-dashboard proof readiness
  before any hosted dashboard, deployment, routing, or scheduler behavior
  exists when one exists, with legacy real-cost-tracking audit fallback when no
  proof checklist exists. The upstream proof chain is preserved in the Hosted
  Dashboard proof item and the generated report retains the Real Cost Tracking
  source proof's own source metadata when available.
- Remote worker proof checklist: the latest Real-Cost-sourced hosted dashboard
  proof checklist can be checked for remote-worker proof readiness before any
  remote worker, remote claim, routing, or scheduler behavior exists when one
  exists. Newer legacy hosted-dashboard rows and dangling hosted-dashboard rows
  without retrievable Real Cost Tracking and Automatic Retry proof sources do
  not hide the stronger proof chain. The upstream proof chain is preserved in
  the remote-worker proof item and the generated report retains the
  hosted-dashboard source proof's own source metadata when available.
- Autonomous scheduling proof checklist: the latest Real-Cost-sourced remote
  worker proof checklist can be checked for autonomous-scheduling proof
  readiness before any scheduler, remote worker, routing, or claim behavior
  exists. Newer legacy remote-worker rows and dangling remote-worker rows
  without retrievable Hosted Dashboard, Real Cost Tracking, and Automatic
  Retry proof sources do not hide the stronger proof chain. The upstream proof
  chain is preserved in the autonomous-scheduling proof item and the generated
  report retains the remote-worker source proof's own source metadata when
  available.
- Browser desktop adapter proof checklist: the latest Real-Cost-sourced
  autonomous scheduling proof checklist can be checked for browser/desktop
  adapter proof readiness before any adapter operation, scheduler, routing, or
  claim behavior exists. Newer legacy autonomous-scheduling rows and dangling
  autonomous-scheduling rows without retrievable Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources do not hide
  the stronger proof chain. The upstream proof chain is preserved in the
  browser/desktop adapter proof item and the generated report retains the
  autonomous-scheduling source proof's own source metadata when available.
- CI Deploy proof checklist: the latest Real-Cost-sourced browser desktop
  adapter proof checklist can be checked for CI/deploy proof readiness before
  any CI run, deployment, adapter operation, routing, or claim behavior exists
  when one exists. Newer legacy browser/desktop adapter rows and dangling
  browser/desktop adapter rows without retrievable Autonomous Scheduling,
  Remote Worker, Hosted Dashboard, Real Cost Tracking, and Automatic Retry
  proof sources do not hide the stronger proof chain. The upstream proof chain
  is preserved in the CI Deploy proof item and the generated report retains
  the browser/desktop adapter source proof's own source metadata when
  available.
- Budget Enforcement proof checklist: the latest Real-Cost-sourced CI Deploy
  proof checklist can be checked for budget-enforcement proof readiness before
  any budget enforcement, CI/deploy run, routing, or claim behavior exists
  when one exists. Newer legacy CI Deploy rows and dangling CI Deploy rows
  without retrievable Browser/Desktop Adapter, Autonomous Scheduling, Remote
  Worker, Hosted Dashboard, Real Cost Tracking, and Automatic Retry proof
  sources do not hide the stronger proof chain. The upstream proof chain is
  preserved in the Budget Enforcement proof item and the generated report
  retains the CI Deploy source proof's own source metadata when available.
- Trust Promotion proof checklist: the latest Real-Cost-sourced Budget
  Enforcement proof checklist can be checked for trust-promotion proof
  readiness before any trust promotion, budget enforcement, routing, or claim
  behavior exists when one exists. Newer legacy Budget Enforcement rows and
  dangling Budget Enforcement rows without retrievable CI Deploy,
  Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources do not hide
  the stronger proof chain. The upstream proof chain is preserved in the Trust
  Promotion proof item and the generated report retains the Budget Enforcement
  source proof's own source metadata when available.
- Automatic Retry proof checklist: the latest Real-Cost-sourced Trust Promotion
  proof checklist can be checked for automatic-retry proof readiness before any
  retry, replay, trust promotion, budget enforcement, routing, or claim
  behavior exists when one exists. Newer legacy Trust Promotion rows and
  dangling Trust Promotion rows without retrievable Budget Enforcement, CI
  Deploy, Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources do not hide
  the stronger proof chain. The upstream proof chain is preserved in the
  Automatic Retry proof item and the generated report retains the Trust
  Promotion source proof's own source metadata when available.
- Real Cost Tracking proof checklist: the latest Real-Cost-sourced Automatic
  Retry proof checklist can be checked for real-cost-tracking proof readiness
  before any spend tracking, retry, budget enforcement, routing, or claim
  behavior exists when one exists. The upstream proof chain is preserved in the
  Real Cost Tracking proof item and the generated report retains the Automatic
  Retry source proof's own source metadata when available.
- Goal completion audit: the latest expansion proof checklists can be audited
  against the active expansion goal before any goal-complete claim exists. The
  audit reports satisfied, blocked, and missing requirements plus external
  decisions and explicit non-claims, and it does not mark the active goal
  complete or approve any capability.
- Expansion decision brief: the latest goal completion audit can be converted
  into a report-only operator decision packet before any capability approval,
  promotion, routing, or external side effect exists.
- Expansion decision evidence index: the latest expansion decision brief can
  be cross-referenced to blocked queue entries and proof report paths before
  any decision is approved or evidence is collected automatically.
- Expansion operator review checklist: the latest decision evidence index can
  be converted into manual operator choices with allowed actions before any
  approval, promotion, routing, or external side effect exists.
- Expansion operator decision ledger: the latest operator review checklist can
  be converted into pending/manual decision rows before any approval action,
  promotion, routing, or external side effect exists.
- Expansion operator approval draft: the latest operator decision ledger can
  be converted into draft-only approval-request packet rows before any
  `approval_requests` rows are created, allowed action is taken, promotion,
  routing, or external side effect exists.
- Expansion operator approval request review: the latest approval draft can be
  reviewed against the existing `approval_requests` contract before any real
  approval row is created; current capability decisions are blocked by
  `approval_request_subject_not_modeled` until the approval schema is extended
  or a separate subject table is chosen.
- Expansion operator approval schema decision: the latest approval request
  review can be converted into a report-only schema decision packet that
  recommends `operator_approval_requests_table` while preserving the existing
  task approval gate, applying no migration, creating no approval rows, and
  taking no operator action.
- Expansion operator approval schema migration plan: the latest schema
  decision can be converted into a report-only migration plan for a future
  `operator_approval_requests` table. The plan records proposed columns,
  indexes, and migration steps while applying no migration, creating no table,
  creating no operator approval rows, and creating no approval requests.
- Expansion operator approval schema migration approval request: the latest
  migration plan can be converted into a report-only approval request packet
  for applying the future `operator_approval_requests` table. The packet
  records the requested action and allowed operator actions while applying no
  migration, creating no table, creating no operator approval rows, and
  creating no approval requests.
- Expansion operator approval schema migration decision ledger: the latest
  schema migration approval request can be converted into a report-only
  pending/manual decision ledger. The ledger records the source request,
  requested action, allowed operator actions, pending decision count, and
  zero mutation counters while applying no migration, creating no table,
  creating no operator approval rows, creating no approval requests, and
  taking no operator action.
- Expansion operator approval schema migration action checklist: the latest
  schema migration decision ledger can be converted into a report-only manual
  action checklist. The checklist records allowed operator actions,
  `selected_action=none`, pending action counts, and zero mutation counters
  while applying no migration, creating no table, creating no operator
  approval rows, creating no approval requests, and taking no operator action.
- Expansion operator approval schema migration selection packet: the latest
  schema migration action checklist can be converted into a report-only
  operator selection input packet. The packet records
  `selected_action=none`, `selections_recorded: 0`, pending selection counts,
  allowed operator actions, and zero mutation counters while applying no
  migration, creating no table, creating no approval rows, and recording no
  operator selection.
- Expansion operator approval schema migration selection input template: the
  latest selection packet can be converted into a report-only operator input
  template. The template records required input fields and
  `inputs_recorded: 0` while keeping `selected_action=none`,
  `selections_recorded: 0`, `actions_taken: 0`, and zero mutation counters.
- Operator approval request row application: after the schema migration
  application has created the local `operator_approval_requests` table, an
  explicit approved row-creation selection can create pending local operator
  approval request rows from the latest expansion approval draft. It creates
  no legacy `approval_requests` rows, decides no requests, promotes nothing,
  and takes no external action.
- Operator approval request decisions: after pending local
  `operator_approval_requests` rows exist, an explicit operator decision
  selection can mark those rows `approved`, `deferred`, or
  `more_evidence_requested`. The command records durable decision evidence
  while creating no legacy `approval_requests` rows, enabling no capability,
  promoting no trust, and taking no external action.
- Iteration loop: `iterate` selects the next actionable queue item and writes a
  non-executing `docs/next-iteration.md` packet with verification commands.
- Simplicity guardrail: when queue items have equal score metadata, `iterate`
  selects the lower-complexity item before queue order.
- Memory: project files preserve hot/warm memory and run files preserve episodic
  evidence.
- Learning: each run records an episodic learning; repeated stable patterns can
  be promoted into root knowledge through `distill-learnings`.
- Visibility: `docs/dashboard.md` summarizes queue health, handoff reviews,
  eval-after-change checks, learning distillation, budget/trust posture,
  dispatch posture history, dispatch posture snapshot reviews, dispatch
  posture refresh recommendations, capability expansion ledgers, capability
  readiness reviews, capability proof gap indexes, capability approval-boundary
  matrices, capability evidence collection plans, capability promotion gate
  checklists, capability promotion decision ledgers, capability trust
  promotion audits, capability automatic retry audits, capability real cost
  tracking audits, hosted dashboard proof checklists, remote worker proof
  checklists, autonomous scheduling proof checklists, browser desktop adapter
  proof checklists, CI Deploy proof checklists, budget enforcement proof
  checklists, trust promotion proof checklists, automatic retry proof
  checklists, real cost tracking proof checklists, goal completion audits,
  expansion decision briefs, expansion decision evidence indexes, expansion
  operator review checklists, expansion operator decision ledgers, expansion
  operator approval drafts, expansion operator approval request reviews,
  expansion operator approval schema decisions, expansion operator approval
  schema migration plans, expansion operator approval schema migration
  approval requests, expansion operator approval schema migration decision
  ledgers, expansion operator approval schema migration action checklists,
  expansion operator approval schema migration selection packets, expansion
  operator approval schema migration selection input templates, operator
  approval schema migration applications, operator approval request row
  applications, operator approval request decisions, capability activation
  follow-up result batches, follow-up result decisions, follow-up result
  downstream task batches, playbooks, eval candidates, iteration packets,
  simplicity guardrails, approvals, proposed
  effects, worktrees, verification status, stuck tasks, incidents, recent
  runs, learnings, and eval results.

## First Milestone

Prove one full local loop:

1. Accept a goal.
2. Decompose it into an explicit task graph.
3. Route a task to a worker.
4. Execute work in the repository.
5. Verify the result with saved evidence.
6. Record memory and activity visible to a human.
7. Learn one thing from the run.

Status: implemented and locally verified by automated tests and CLI smoke runs.

## Key Guardrails

- Start with one strong local worker and explicit workflows.
- Prefer file-first state, typed schemas, and deterministic verification.
- Keep research mode and action mode distinct.
- Do not use hidden memory as the source of truth.
- Do not promote autonomy without outcome evidence.
- Keep external side effects out of scope until approvals, idempotency, and
  rollback are implemented.

## Current Runtime Constraints

- Runtime: Codex desktop coding agent in a local git repository.
- Shell and filesystem: available.
- File editing: available through patch-based edits.
- Git: available. ClankerOS itself is connected to a GitHub remote, and
  registered target repositories can be isolated with git worktrees.
- Network: available, but not required for the first milestone.
- Browser and desktop control: available to the agent runtime, deferred from the
  first executable milestone.
- Persistent local storage: SQLite and repo files are available.
- Static dashboard: available through `python3 -m agent_os.cli dashboard`.
- Next iteration packet: available through `python3 -m agent_os.cli iterate`.
  Queue items may include `<!-- score=N complexity=N -->`; equal scores prefer
  lower complexity.
- Local approval review: available through `python3 -m agent_os.cli approvals`
  and `python3 -m agent_os.cli approve <approval_id>`.
- Local project registration: available through
  `python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "<command>"`.
- Worktree-isolated coding run: available through
  `python3 -m agent_os.cli run-goal "<goal>" --project <name> --isolation worktree --command "<safe local command>"`.
  The current flow records a proposed `local_git_commit` effect and approval
  packet, but it does not create the commit yet.
- Incident resolution: available through
  `python3 -m agent_os.cli resolve-incident <incident_id> --resolved-by operator --note "..."`.
- Stuck-task sweep: available through
  `python3 -m agent_os.cli sweep-stuck --timeout-seconds 1800`.
- Queue-health report: available through `python3 -m agent_os.cli queue-health`
  and mirrored into `docs/dashboard.md`.
- Handoff review: available through
  `python3 -m agent_os.cli handoff-review` and mirrored into
  `docs/handoff-review.md` plus `docs/dashboard.md`.
- Eval-after-change check: available through
  `python3 -m agent_os.cli eval-after-change --change "<summary>" --file <path>`
  and mirrored into `docs/eval-after-change.md` plus `docs/dashboard.md`.
- Learning distillation: available through
  `python3 -m agent_os.cli distill-learnings --min-occurrences 3` and mirrored
  into `docs/learning-distillation.md`, root `knowledge.md`, SQLite state, and
  `docs/dashboard.md`.
- Budget/trust posture: available through
  `python3 -m agent_os.cli budget-trust-posture` and mirrored into
  `docs/budget-trust-posture.md`, SQLite state, and `docs/dashboard.md`.
- Dispatch posture history: available through
  `python3 -m agent_os.cli dispatch-posture-history` and mirrored into
  `docs/dispatch-posture-history.md`, SQLite state, and `docs/dashboard.md`.
- Dispatch posture snapshot review: available through
  `python3 -m agent_os.cli dispatch-posture-staleness` and mirrored into
  `docs/dispatch-posture-staleness.md`, SQLite state, and
  `docs/dashboard.md`.
- Dispatch posture refresh recommendation: available through
  `python3 -m agent_os.cli dispatch-posture-refresh` and mirrored into
  `docs/dispatch-posture-refresh.md`, SQLite state, and `docs/dashboard.md`.
- Capability expansion ledger: available through
  `python3 -m agent_os.cli capability-expansion-ledger` and mirrored into
  `docs/capability-expansion-ledger.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability readiness review: available through
  `python3 -m agent_os.cli capability-readiness-review` and mirrored into
  `docs/capability-readiness-review.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability proof gap index: available through
  `python3 -m agent_os.cli capability-proof-gap-index` and mirrored into
  `docs/capability-proof-gap-index.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability approval boundary matrix: available through
  `python3 -m agent_os.cli capability-approval-boundary-matrix` and mirrored
  into `docs/capability-approval-boundary-matrix.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability evidence collection plan: available through
  `python3 -m agent_os.cli capability-evidence-collection-plan` and mirrored
  into `docs/capability-evidence-collection-plan.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability promotion gate checklist: available through
  `python3 -m agent_os.cli capability-promotion-gate-checklist` and mirrored
  into `docs/capability-promotion-gate-checklist.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability promotion decision ledger: available through
  `python3 -m agent_os.cli capability-promotion-decision-ledger` and mirrored
  into `docs/capability-promotion-decision-ledger.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability trust promotion audit: available through
  `python3 -m agent_os.cli capability-trust-promotion-audit` and mirrored into
  `docs/capability-trust-promotion-audit.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability automatic retry audit: available through
  `python3 -m agent_os.cli capability-automatic-retry-audit` and mirrored into
  `docs/capability-automatic-retry-audit.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability real cost tracking audit: available through
  `python3 -m agent_os.cli capability-real-cost-tracking-audit` and mirrored
  into `docs/capability-real-cost-tracking-audit.md`, SQLite state, and
  `docs/dashboard.md`.
- Hosted dashboard proof checklist: available through
  `python3 -m agent_os.cli hosted-dashboard-proof-checklist` and mirrored into
  `docs/hosted-dashboard-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced Real Cost Tracking
  proof checklists when one exists, avoids dangling Real Cost Tracking proof
  rows without an upstream Automatic Retry proof source, falls back to the
  latest structurally backed Real Cost Tracking proof checklist otherwise, and
  falls back to real-cost-tracking audits only when no proof checklist exists;
  it preserves source proof metadata when present.
- Remote worker proof checklist: available through
  `python3 -m agent_os.cli remote-worker-proof-checklist` and mirrored into
  `docs/remote-worker-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced hosted-dashboard
  proof checklists, avoids dangling hosted-dashboard rows without retrievable
  Real Cost Tracking and Automatic Retry proof sources, and preserves source
  proof metadata when present.
- Autonomous scheduling proof checklist: available through
  `python3 -m agent_os.cli autonomous-scheduling-proof-checklist` and mirrored
  into `docs/autonomous-scheduling-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced remote-worker proof
  checklists, avoids dangling remote-worker rows without retrievable Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources, and
  preserves source proof metadata when present.
- Browser desktop adapter proof checklist: available through
  `python3 -m agent_os.cli browser-desktop-adapter-proof-checklist` and
  mirrored into `docs/browser-desktop-adapter-proof-checklist.md`, SQLite
  state, and `docs/dashboard.md`; it prefers latest Real-Cost-sourced
  autonomous scheduling proof checklists and preserves source proof metadata
  when present.
- CI Deploy proof checklist: available through
  `python3 -m agent_os.cli ci-deploy-proof-checklist` and mirrored into
  `docs/ci-deploy-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced browser/desktop
  adapter proof checklists, avoids dangling browser/desktop adapter rows
  without retrievable Autonomous Scheduling, Remote Worker, Hosted Dashboard,
  Real Cost Tracking, and Automatic Retry proof sources, and preserves source
  proof metadata when present.
- Budget Enforcement proof checklist: available through
  `python3 -m agent_os.cli budget-enforcement-proof-checklist` and mirrored
  into `docs/budget-enforcement-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced CI Deploy proof
  checklists, avoids dangling CI Deploy rows without retrievable
  Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources, and
  preserves source proof metadata when present.
- Trust Promotion proof checklist: available through
  `python3 -m agent_os.cli trust-promotion-proof-checklist` and mirrored into
  `docs/trust-promotion-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced Budget Enforcement
  proof checklists, avoids dangling Budget Enforcement rows without
  retrievable CI Deploy, Browser/Desktop Adapter, Autonomous Scheduling,
  Remote Worker, Hosted Dashboard, Real Cost Tracking, and Automatic Retry
  proof sources, and preserves source proof metadata when present.
- Automatic Retry proof checklist: available through
  `python3 -m agent_os.cli automatic-retry-proof-checklist` and mirrored into
  `docs/automatic-retry-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced Trust Promotion
  proof checklists, avoids dangling Trust Promotion rows without retrievable
  Budget Enforcement, CI Deploy, Browser/Desktop Adapter, Autonomous
  Scheduling, Remote Worker, Hosted Dashboard, Real Cost Tracking, and
  Automatic Retry proof sources, and preserves source proof metadata when
  present.
- Real Cost Tracking proof checklist: available through
  `python3 -m agent_os.cli real-cost-tracking-proof-checklist` and mirrored
  into `docs/real-cost-tracking-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it preserves Real-Cost-sourced Automatic Retry proof
  metadata when present.
- Goal completion audit: available through
  `python3 -m agent_os.cli goal-completion-audit` and mirrored into
  `docs/goal-completion-audit.md`, SQLite state, and `docs/dashboard.md`; it
  reports whether the expansion goal is still blocked by report-only proofs,
  missing proof rows, external decisions, or approvals before any completion
  claim is made.
- Expansion decision brief: available through
  `python3 -m agent_os.cli expansion-decision-brief` and mirrored into
  `docs/expansion-decision-brief.md`, SQLite state, and `docs/dashboard.md`;
  it turns the latest goal completion audit into explicit operator decisions
  without approving, routing, promoting, or mutating external systems.
- Expansion decision evidence index: available through
  `python3 -m agent_os.cli expansion-decision-evidence-index` and mirrored
  into `docs/expansion-decision-evidence-index.md`, SQLite state, and
  `docs/dashboard.md`; it links decision items to blocked queue evidence and
  proof reports without granting approval or collecting evidence
  automatically.
- Expansion operator review checklist: available through
  `python3 -m agent_os.cli expansion-operator-review-checklist` and mirrored
  into `docs/expansion-operator-review-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it lists manual operator choices and allowed actions
  without granting approval, promotion, routing, or external side effects.
- Expansion operator decision ledger: available through
  `python3 -m agent_os.cli expansion-operator-decision-ledger` and mirrored
  into `docs/expansion-operator-decision-ledger.md`, SQLite state, and
  `docs/dashboard.md`; it records pending/manual operator decision posture
  without taking allowed actions, granting approval, promotion, routing, or
  external side effects.
- Expansion operator approval draft: available through
  `python3 -m agent_os.cli expansion-operator-approval-draft` and mirrored
  into `docs/expansion-operator-approval-draft.md`, SQLite state, and
  `docs/dashboard.md`; it prepares draft-only approval-request packet rows
  from the latest decision ledger while keeping `created_approval_requests: 0`
  and without taking allowed actions, granting approval, routing, or mutating
  external systems.
- Expansion operator approval request review: available through
  `python3 -m agent_os.cli expansion-operator-approval-request-review` and
  mirrored into `docs/expansion-operator-approval-request-review.md`, SQLite
  state, and `docs/dashboard.md`; it reviews draft requests against the
  existing `approval_requests` contract, records schema gaps, keeps
  `created_approval_requests: 0`, and does not create approvals, take allowed
  actions, route work, or mutate external systems.
- Expansion operator approval schema decision: available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-decision` and
  mirrored into `docs/expansion-operator-approval-schema-decision.md`, SQLite
  state, and `docs/dashboard.md`; it recommends the report-only
  `operator_approval_requests_table` schema option from the current schema gap
  while applying no migration and creating no approval rows.
- Expansion operator approval schema migration plan: available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-plan`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-plan.md`, SQLite state,
  and `docs/dashboard.md`; it turns the chosen schema option into a concrete
  report-only migration plan while applying no migration and creating no table
  or rows.
- Expansion operator approval schema migration approval request: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-approval-request`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-approval-request.md`,
  SQLite state, and `docs/dashboard.md`; it records that applying the planned
  schema requires an operator decision, while taking no action and creating no
  approval rows.
- Expansion operator approval schema migration decision ledger: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-decision-ledger`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-decision-ledger.md`,
  SQLite state, and `docs/dashboard.md`; it records the schema migration
  request as a pending/manual operator action while applying no migration and
  creating no table or approval rows.
- Expansion operator approval schema migration action checklist: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-action-checklist`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-action-checklist.md`,
  SQLite state, and `docs/dashboard.md`; it lists the allowed manual choices
  while keeping `selected_action=none` and recording no action taken.
- Expansion operator approval schema migration selection packet: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-packet`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-selection-packet.md`,
  SQLite state, and `docs/dashboard.md`; it requires explicit operator input
  while keeping `selected_action=none`, `selections_recorded: 0`, and all
  migration, table, and approval-row counters at zero.
- Expansion operator approval schema migration selection input template:
  available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-input-template`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-selection-input-template.md`,
  SQLite state, and `docs/dashboard.md`; it lists required operator fields
  while keeping `inputs_recorded: 0`, `selections_recorded: 0`, and all
  migration, table, and approval-row counters at zero.
- Operator approval schema migration application: available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-apply`
  after the selection input template exists. Non-approve selections record a
  local application row without creating the table. An approved selection
  creates the local `operator_approval_requests` table exactly once, records
  applied columns/indexes in
  `docs/expansion-operator-approval-schema-migration-application.md`, and
  keeps `operator_approval_rows_created: 0` and
  `approval_requests_created: 0`.
- Operator approval request row application: available through
  `python3 -m agent_os.cli expansion-operator-approval-request-rows-apply`
  after the approval draft and schema application exist. Non-approve
  selections record local evidence without creating rows. An approved
  selection creates pending local `operator_approval_requests` rows exactly
  once for the latest draft, records evidence in
  `docs/expansion-operator-approval-request-rows-application.md`, and keeps
  `approval_requests_created: 0`.
- Operator approval request decisions: available through
  `python3 -m agent_os.cli expansion-operator-approval-request-decide`
  after pending operator approval request rows exist. The command records
  approve/defer/more-evidence decisions on local rows, writes evidence to
  `docs/expansion-operator-approval-request-decisions.md`, and keeps
  `approval_requests_created: 0` without enabling capabilities.
- Capability activation contracts: available through
  `python3 -m agent_os.cli capability-activation-contracts` after
  `capability-activation-tasks` has created pending activation tasks. The
  command writes `docs/capability-activation-contracts.md`, records one
  blocked contract per task, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, and `activation_allowed=false`.
- Capability activation evidence: available through
  `python3 -m agent_os.cli capability-activation-evidence` after contracts
  exist. The command writes `docs/capability-activation-evidence.md`, one JSON
  artifact per selected contract, and keeps `approval_requests_created: 0` and
  `activation_actions_taken: 0`.
- Capability activation decisions: available through
  `python3 -m agent_os.cli capability-activation-decide` after evidence exists.
  The command writes `docs/capability-activation-decisions.md`, updates
  contract decision state, and keeps capability activation blocked.
- Capability activation follow-ups: available through
  `python3 -m agent_os.cli capability-activation-followups` after contracts
  have `request_more_evidence` decisions. The command writes
  `docs/capability-activation-followups.md` and creates pending high-risk
  follow-up evidence tasks while keeping `approval_requests_created: 0` and
  `activation_actions_taken: 0`.
- Capability activation follow-up delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-delegations` after
  follow-up evidence tasks exist. The command writes
  `docs/capability-activation-followup-delegations.md`, records
  `evidence_review` routing decisions, and creates pending read-only evaluator
  delegation packets while keeping execution and activation actions at zero.
- Capability activation follow-up results: available through
  `python3 -m agent_os.cli capability-activation-followup-results` after
  read-only evaluator delegation results are completed. The command writes
  `docs/capability-activation-followup-results.md`, records local result rows
  and JSON artifacts, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-decide` after
  result records exist. The command writes
  `docs/capability-activation-followup-decisions.md`, records local operator
  review decisions, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-tasks` after
  accepted blocked follow-up result effects have been applied locally. The
  command writes `docs/capability-activation-followup-result-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-delegations`
  after downstream follow-up result tasks exist. The command writes
  `docs/capability-activation-followup-result-task-delegations.md`, creates
  read-only evaluator delegation packets and local JSON artifacts, and keeps
  `execution_started: 0`, `network_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_actions_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-results`
  after downstream proof-plan delegation packets have completed results. The
  command writes
  `docs/capability-activation-followup-result-task-results.md`, stores local
  result records and JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-decide`
  after downstream proof-plan result records exist. The command writes
  `docs/capability-activation-followup-result-task-decisions.md`, records
  accept-keep-blocked, more-evidence, or defer operator decisions for
  downstream result records, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect proposals:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-proposals`
  after accepted blocked downstream result decisions exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-proposals.md`,
  creates local `proposed` effects, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect application:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-apply`
  after downstream result decision effect proposals exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-application.md`,
  records local application rows, marks applicable effects `applied`, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect tasks: available
  through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-tasks`
  after downstream result decision effects have been applied locally. The
  command writes
  `docs/capability-activation-followup-result-task-result-effect-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task delegations:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-delegations`
  after downstream result effect tasks exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-delegations.md`,
  records read-only evaluator routing and delegation packet evidence, and
  keeps `execution_started: 0`, `network_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_actions_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect task results:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-results`
  after downstream result effect task delegations have completed. The command
  writes
  `docs/capability-activation-followup-result-task-result-effect-task-results.md`,
  stores local result records and JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result
  decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-decide`
  after downstream result effect task results exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-decisions.md`,
  stores local operator decision rows, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  proposals: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-proposals`
  after accepted downstream result effect task result decisions exist. The
  command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-proposals.md`,
  stores generic local proposed `effects` rows with idempotency keys, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  application: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-apply`
  after downstream result effect task result decision effect proposals exist.
  The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-application.md`,
  records local application rows, marks applicable effects `applied`, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-tasks`
  after downstream result effect task result decision effects have been applied
  locally. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations`
  after downstream result effect task result effect tasks exist. The command
  writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations.md`,
  records read-only routing decisions and pending delegation packets, and
  keeps `execution_started: 0`, `network_actions_taken: 0`,
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-results`
  after completed downstream result effect task result effect delegation
  outputs exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md`,
  stores local result rows and JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-decide`
  after downstream result effect task result effect task result records exist.
  The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-decisions.md`,
  stores local operator decision rows, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect proposals: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals`
  after accepted downstream result effect task result effect result decisions
  exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
  stores generic local proposed `effects` rows with idempotency keys, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Eval candidate listing: available through
  `python3 -m agent_os.cli eval-candidates` and mirrored into
  `docs/dashboard.md`.
- Playbook promotion: available through `python3 -m agent_os.cli playbooks`
  and mirrored into `docs/playbooks.md` plus `docs/dashboard.md`.
- Background scheduling, webhooks, multi-machine dispatch, and hosted dashboard:
  deferred until the local closed loop is stable.
