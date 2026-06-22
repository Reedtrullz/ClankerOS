# Implementation Contract

## Mission

Create a local-first agent operating-system harness that proves the closed loop
from goal intake to learning with visible, verifiable artifacts.

## Runtime Profile

- Host: Codex desktop agent operating in a local git repository.
- Mode: harness-wrapper around a strong generalist execution runtime.
- Storage: SQLite for indexed coordination state, markdown/json/jsonl for
  durable project and run artifacts.
- First worker: one local pull-based worker.

## First Milestone

Implement and verify a CLI-driven local run that accepts a goal, decomposes it,
executes at least one task, verifies outputs, records evidence, updates memory,
shows activity, and creates one learning/eval artifact.

## Non-Goals For V1

- No remote execution.
- No browser or desktop action execution.
- No autonomous external side effects.
- No multi-agent editing of one checkout.
- No hosted dashboard.

## Constraints

- Keep state inspectable in the repository.
- Keep the single-agent baseline simple before adding parallelism.
- Use deterministic validation for the first milestone.
- Prefer standard library Python unless a dependency earns its place.

## Safety Posture

- Default autonomy: supervised for external effects, guided for local
  repository writes.
- Treat destructive operations, network mutations, credential access, and
  outbound communications as approval-required and out of scope for the first
  milestone.

## Proof-Of-Progress Metrics

- Number of goals accepted.
- Number of tasks created, claimed, verified, completed, blocked, or failed.
- Number of tasks waiting on approval and approval decisions recorded.
- Number of iteration packets generated from live momentum queues.
- Iteration packet selection reason, score, and complexity.
- Verification pass rate.
- Incidents opened from failed verification.
- Incidents resolved with operator note and resolution evidence.
- Stale active tasks blocked by sweeps.
- Queue-health hotspots for repeated blocked or failed task groups.
- Handoff reviews run, blocked tasks found, and stale handoffs found.
- Eval-after-change checks run, changed paths covered, and eval run ids linked.
- Learning distillations run, source learnings reviewed, stable learning
  groups promoted, and report paths retained.
- Budget/trust posture reports run, task metadata reviewed, missing or unknown
  posture surfaced, and report paths retained.
- Dispatch posture history summaries run, snapshot counts reviewed, latest task
  count and delta retained, latest risk counts surfaced, observed budget/trust
  states retained, and report paths retained.
- Dispatch posture snapshot reviews run, latest snapshot age retained,
  stale-snapshot counts surfaced, missing history named explicitly, and report
  paths retained.
- Dispatch posture refresh recommendations run, source staleness review
  retained, recommended manual commands surfaced, approval boundaries named,
  and report paths retained.
- Capability expansion ledgers run, deferred autonomy surfaces enumerated,
  required evidence and next proof named, approval boundaries retained, routing
  effect shown as none, and report paths retained.
- Capability readiness reviews run, source ledger id retained, missing
  evidence counted, per-capability readiness surfaced, recommended manual
  commands retained, and report paths retained.
- Capability proof gap indexes run, source readiness review id retained,
  missing evidence and blocked capability counts surfaced, next proof labels
  grouped, approval boundaries retained, and report paths retained.
- Capability approval boundary matrices run, source proof-gap index id
  retained, boundary counts surfaced, blocked capability counts retained,
  approval-required counts retained, and report paths retained.
- Capability evidence collection plans run, source approval-boundary matrix id
  retained, evidence-item counts surfaced, manual collection counts retained,
  approval-required counts retained, boundary counts retained, and report paths
  retained.
- Capability promotion gate checklists run, source evidence collection plan id
  retained, gate counts surfaced, blocked-promotion counts retained, missing
  evidence counts retained, approval-required counts retained, boundary counts
  retained, and report paths retained.
- Capability promotion decision ledgers run, source gate checklist id
  retained, decision counts surfaced, deferred-promotion counts retained,
  operator-decision-required counts retained, missing evidence and approval
  counts retained, boundary counts retained, and report paths retained.
- Capability trust promotion audits run, source promotion decision ledger id
  retained, audit counts surfaced, blocked-trust-promotion counts retained,
  operator-review-required counts retained, deferred-promotion counts retained,
  missing evidence and approval counts retained, boundary counts retained, and
  report paths retained.
- Capability automatic retry audits run, source trust promotion audit id
  retained, audit counts surfaced, blocked-retry counts retained,
  operator-review-required counts retained, blocked-trust-promotion counts
  retained, deferred-promotion counts retained, missing evidence and approval
  counts retained, boundary counts retained, and report paths retained.
- Capability real cost tracking audits run, source automatic retry audit id
  retained, audit counts surfaced, blocked-cost-tracking counts retained,
  operator-review-required counts retained, blocked-retry counts retained,
  blocked-trust-promotion counts retained, deferred-promotion counts retained,
  missing evidence and approval counts retained, boundary counts retained, and
  report paths retained.
- Hosted dashboard proof checklists run, source kind retained, latest
  Real-Cost-sourced Real Cost Tracking proof checklist id/status retained when
  present, dangling Real Cost Tracking proof rows without an upstream
  Automatic Retry proof source reported as missing, legacy source real cost
  tracking audit id/status retained when used as fallback, checklist counts
  surfaced, blocked-dashboard-proof counts retained,
  operator-review-required counts retained, blocked-cost-tracking counts
  retained, blocked-retry counts retained, blocked-trust-promotion counts
  retained, Real Cost Tracking source proof's own source metadata retained
  when available, missing evidence and approval counts retained, boundary
  counts retained, and report paths retained.
- Remote worker proof checklists run, latest Real-Cost-sourced source hosted
  dashboard proof checklist id retained when one exists, newer legacy hosted
  rows skipped when a stronger chain exists, dangling hosted rows without
  retrievable Real Cost Tracking and Automatic Retry proof sources reported as
  missing instead of valid remote-worker blockers, checklist counts surfaced,
  blocked-worker-proof counts retained, operator-review-required counts
  retained, blocked-dashboard-proof counts retained, blocked-cost-tracking
  counts retained, blocked-retry counts retained, blocked-trust-promotion
  counts retained, Real-Cost-sourced hosted dashboard proof metadata retained
  when present, hosted dashboard source proof's own source metadata retained
  when available, missing evidence and approval counts retained, boundary
  counts retained, and report paths retained.
- Autonomous scheduling proof checklists run, latest Real-Cost-sourced remote
  worker proof checklist id retained when one exists, newer legacy remote rows
  skipped when a stronger chain exists, dangling remote rows without
  retrievable Hosted Dashboard, Real Cost Tracking, and Automatic Retry proof
  sources reported as missing instead of valid autonomous-scheduling blockers,
  checklist counts surfaced, blocked-scheduling-proof counts retained,
  operator-review-required counts retained, blocked-worker-proof counts
  retained, blocked-dashboard-proof counts retained, blocked-cost-tracking
  counts retained, blocked-retry counts retained, blocked-trust-promotion
  counts retained, Real-Cost-sourced remote worker proof metadata retained
  when present, remote worker source proof's own source metadata retained when
  available, missing evidence and approval counts retained, boundary counts
  retained, and report paths retained.
- Browser desktop adapter proof checklists run, latest Real-Cost-sourced
  autonomous scheduling proof checklist id retained when one exists, newer
  legacy autonomous-scheduling rows skipped when a stronger chain exists,
  dangling autonomous-scheduling rows without retrievable Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources reported as
  missing instead of valid adapter blockers, checklist counts surfaced,
  blocked-adapter-proof counts retained, operator-review-required counts retained,
  blocked-scheduling-proof counts retained, blocked-worker-proof counts
  retained, blocked-dashboard-proof counts retained, blocked-cost-tracking
  counts retained, blocked-retry counts retained, blocked-trust-promotion
  counts retained, Real-Cost-sourced autonomous scheduling proof metadata
  retained when present, autonomous scheduling source proof's own source
  metadata retained when available, missing evidence and approval counts
  retained, boundary counts retained, and report paths retained.
- CI Deploy proof checklists run, latest Real-Cost-sourced browser desktop
  adapter proof checklist id retained when one exists, newer legacy browser
  desktop adapter rows skipped when a stronger chain exists, dangling browser
  desktop adapter rows without retrievable Autonomous Scheduling, Remote
  Worker, Hosted Dashboard, Real Cost Tracking, and Automatic Retry proof
  sources reported as missing instead of valid CI Deploy blockers, checklist
  counts surfaced, blocked-CI-Deploy-proof counts retained,
  operator-review-required counts retained, blocked-adapter-proof counts retained,
  blocked-scheduling-proof counts retained, blocked-worker-proof counts
  retained, blocked-dashboard-proof counts retained, blocked-cost-tracking
  counts retained, blocked-retry counts retained, blocked-trust-promotion
  counts retained, browser desktop adapter proof metadata retained, browser
  desktop adapter source proof's own source metadata retained when available,
  missing evidence and approval counts retained, boundary counts retained, and
  report paths retained.
- Budget Enforcement proof checklists run, latest Real-Cost-sourced source CI
  Deploy proof checklist id retained when one exists, newer legacy CI Deploy
  rows skipped when a stronger chain exists, dangling CI Deploy rows without
  retrievable Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker,
  Hosted Dashboard, Real Cost Tracking, and Automatic Retry proof sources
  reported as missing instead of valid Budget Enforcement blockers, checklist
  counts surfaced, blocked-budget-enforcement-proof counts retained,
  operator-review-required counts retained, blocked-CI-Deploy-proof
  counts retained, blocked-adapter-proof counts retained,
  blocked-scheduling-proof counts retained, blocked-worker-proof counts
  retained, blocked-dashboard-proof counts retained, blocked-cost-tracking
  counts retained, blocked-retry counts retained, blocked-trust-promotion
  counts retained, CI Deploy proof metadata retained, CI Deploy source
  proof's own source metadata retained when available, missing evidence and
  approval counts retained, boundary counts retained, and report paths
  retained.
- Trust Promotion proof checklists run, latest Real-Cost-sourced source
  Budget Enforcement proof checklist id retained when one exists, newer legacy
  Budget Enforcement rows skipped when a stronger chain exists, dangling
  Budget Enforcement rows without retrievable CI Deploy, Browser/Desktop
  Adapter, Autonomous Scheduling, Remote Worker, Hosted Dashboard, Real Cost
  Tracking, and Automatic Retry proof sources reported as missing instead of
  valid Trust Promotion blockers, checklist counts surfaced,
  blocked-trust-promotion-proof counts retained,
  operator-review-required counts retained, blocked-budget-enforcement-proof
  counts retained, blocked-CI-Deploy-proof counts retained,
  blocked-adapter-proof counts retained, blocked-scheduling-proof counts
  retained, blocked-worker-proof counts retained, blocked-dashboard-proof
  counts retained, blocked-cost-tracking counts retained, blocked-retry counts
  retained, blocked-trust-promotion counts retained, Budget Enforcement proof
  metadata retained, Budget Enforcement source proof's own source metadata
  retained when available, missing evidence and approval counts retained,
  boundary counts retained, and report paths retained.
- Automatic Retry proof checklists run, latest Real-Cost-sourced source Trust
  Promotion proof checklist id retained when one exists, checklist counts
  surfaced, blocked-automatic-retry-proof counts retained,
  operator-review-required counts retained,
  blocked-trust-promotion-proof counts retained,
  blocked-budget-enforcement-proof counts retained,
  blocked-CI-Deploy-proof counts retained, blocked-adapter-proof counts
  retained, blocked-scheduling-proof counts retained, blocked-worker-proof
  counts retained, blocked-dashboard-proof counts retained,
  blocked-cost-tracking counts retained, blocked-retry counts retained,
  blocked-trust-promotion counts retained, missing evidence and approval
  counts retained, newer legacy Trust Promotion rows skipped when a stronger
  Real-Cost-sourced chain exists, dangling Trust Promotion rows without
  retrievable Budget Enforcement, CI Deploy, Browser/Desktop Adapter,
  Autonomous Scheduling, Remote Worker, Hosted Dashboard, Real Cost Tracking,
  and Automatic Retry proof sources reported as missing upstream proof instead
  of valid Automatic Retry blockers, Real-Cost-sourced Trust Promotion proof
  metadata retained when present, Trust Promotion source proof's own source
  metadata retained when available, boundary counts retained, and report paths
  retained.
- Real Cost Tracking proof checklists run, latest Real-Cost-sourced source
  Automatic Retry proof checklist id retained when one exists, checklist
  counts surfaced,
  blocked-real-cost-tracking-proof counts retained,
  operator-review-required counts retained,
  blocked-automatic-retry-proof counts retained,
  blocked-trust-promotion-proof counts retained,
  blocked-budget-enforcement-proof counts retained,
  blocked-CI-Deploy-proof counts retained, blocked-adapter-proof counts
  retained, blocked-scheduling-proof counts retained, blocked-worker-proof
  counts retained, blocked-dashboard-proof counts retained,
  blocked-cost-tracking counts retained, blocked-retry counts retained,
  blocked-trust-promotion counts retained, Real-Cost-sourced Automatic Retry
  proof metadata retained when present, Automatic Retry source proof's own
  source metadata retained when available, missing evidence and approval
  counts retained, boundary counts retained, and report paths retained.
- Goal completion audits run, audited expansion requirements counted,
  satisfied requirements counted, blocked requirements counted, missing
  evidence and approval counts retained, external decisions surfaced,
  recommended commands retained for missing proof rows, report-only
  non-claims retained, and report paths retained.
- Expansion decision briefs run, source goal completion audit id/status
  retained, external decisions counted, blocked capability approvals counted,
  recommended next step retained, report-only non-claims retained, and report
  paths retained.
- Expansion decision evidence indexes run, source decision brief and source
  audit ids retained, decision and evidence counts surfaced, external and
  capability decision counts retained, missing evidence-link counts retained,
  blocked queue/proof report paths retained, recommended next step retained,
  report-only non-claims retained, and report paths retained.
- Expansion operator review checklists run, source evidence index, brief, and
  audit ids retained, review-item counts surfaced, decision-required counts
  retained, external and capability review counts retained, missing
  evidence-link counts retained, allowed manual actions retained, recommended
  next step retained, report-only non-claims retained, and report paths
  retained.
- Expansion operator decision ledgers run, source checklist, evidence index,
  brief, and audit ids retained, decision-row counts surfaced,
  pending/manual counts retained, approved/deferred/more-evidence counts
  retained, external and capability decision counts retained, allowed manual
  actions separated from actions taken, recommended next step retained,
  report-only non-claims retained, and report paths retained.
- Expansion operator approval drafts run, source ledger, checklist, evidence
  index, brief, and audit ids retained, draft-item and draft-request counts
  surfaced, created approval request count retained as zero, external and
  capability draft counts retained, approval-boundary count retained, pending
  decision count retained, allowed manual actions retained, recommended next
  step retained, report-only non-claims retained, and report paths retained.
- Expansion operator approval request reviews run, source draft, ledger,
  checklist, evidence index, brief, and audit ids retained, draft request and
  review-item counts surfaced, `approval_request_schema_review_required` status
  retained when draft rows cannot map to the current approval table, ready and
  blocked request counts retained, `approval_request_subject_not_modeled`
  schema-gap counts retained, missing `approval_requests` fields retained,
  created and existing approval request counts retained, external and
  capability request counts retained, approval-boundary count retained,
  recommended next step retained, report-only non-claims retained, and report
  paths retained.
- Expansion operator approval schema decisions run, source review, draft,
  ledger, checklist, evidence index, brief, and audit ids retained, affected
  request counts surfaced, schema-gap and missing-field counts retained,
  external and capability request counts retained, decision option counts
  surfaced, recommended option retained, rejected option count retained,
  schema-object count retained, migration-applied count retained as zero,
  created and existing approval request counts retained, recommended next step
  retained, report-only non-claims retained, and report paths retained.
- Expansion operator approval schema migration plans run, source schema
  decision, review, draft, ledger, checklist, evidence index, brief, and audit
  ids retained, target table retained, proposed column and index counts
  surfaced, migration-step counts retained, migration-applied and table-created
  counts retained as zero, operator approval row and approval request creation
  counts retained as zero, recommended next step retained, report-only
  non-claims retained, and report paths retained.
- Expansion operator approval schema migration approval requests run, source
  migration plan, schema decision, and review ids retained, target table
  retained, requested action and approval boundary surfaced, allowed operator
  actions retained, request counts surfaced, migration-applied and
  table-created counts retained as zero, operator approval row and approval
  request creation counts retained as zero, recommended next step retained,
  report-only non-claims retained, and report paths retained.
- Expansion operator approval schema migration decision ledgers run, source
  approval request, migration plan, schema decision, and review ids retained,
  target table retained, requested action and approval boundary surfaced,
  allowed operator actions retained, request and decision counts surfaced,
  pending action count retained, approved/deferred/more-evidence counts
  retained as zero, migration-applied and table-created counts retained as
  zero, operator approval row and approval request creation counts retained as
  zero, recommended next step retained, report-only non-claims retained, and
  report paths retained.
- Expansion operator approval schema migration action checklists run, source
  decision ledger, approval request, migration plan, schema decision, and
  review ids retained, target table retained, requested action and approval
  boundary surfaced, allowed operator actions retained, pending action counts
  surfaced, selected action retained as `none`, actions-taken count retained
  as zero, migration-applied and table-created counts retained as zero,
  operator approval row and approval request creation counts retained as zero,
  recommended next step retained, report-only non-claims retained, and report
  paths retained.
- Expansion operator approval schema migration selection packets run, source
  action checklist, decision ledger, approval request, migration plan, schema
  decision, and review ids retained, target table retained, requested action
  and approval boundary surfaced, allowed operator actions retained, pending
  selection counts surfaced, selected action retained as `none`,
  selections-recorded and actions-taken counts retained as zero,
  migration-applied and table-created counts retained as zero, operator
  approval row and approval request creation counts retained as zero,
  recommended next step retained, report-only non-claims retained, and report
  paths retained.
- Eval candidates proposed from verifier or workflow gaps.
- Playbooks promoted from repeated successful eval runs.
- Equal-score queue choices that selected the lower-complexity item.
- Run duration.
- Evidence artifacts produced.
- Learnings recorded.

## Verification Strategy

- Unit tests for storage and task claiming.
- End-to-end test for the first milestone loop in a temporary repository.
- CLI smoke test.
- Eval command that runs the first milestone scenario and reports pass/fail.
