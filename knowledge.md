# Knowledge

## Architecture Decisions

- Start with a single local worker plus explicit task graph and verifier.
- Use SQLite in WAL mode for operational indexing.
- Use markdown files as the continuation surface for humans and future agents.
- Defer multi-agent and external side effects until the local loop is reliable.

## Stable Concepts

- A goal is user intent persisted by the control plane.
- A task is a verifiable unit of work derived from a goal.
- Evidence is a concrete file, command output, or state record attached to a
  verifier result.
- Approval is a persisted local control-plane decision required before risky
  or unknown tasks can be claimed by a worker.
- Incident resolution is a persisted operator decision that keeps the original
  failure evidence and adds a separate resolution evidence artifact.
- Queue health is a report-only control-plane check for repeated blocked or
  failed task groups before automatic replay, quarantine, or escalation exists.
- An eval candidate is a proposed regression case created when a verifier or
  workflow gap is discovered; it is not yet an executable eval.
- A playbook is a reusable operating guide promoted from repeated successful
  eval runs; it is not an automatic executor.
- An iteration packet is a non-executing handoff artifact selected from live
  momentum queues and persisted before the next implementation pass.
- A simplicity guardrail is a tie-breaker, not an orchestrator: equal score
  chooses lower complexity, then queue order.
- A handoff review is a report-only continuity check: it compares blocked task
  state and project handoff files against the current iteration packet before
  any automatic repair or requeue exists.
- An eval-after-change check is manual report-only proof that a named harness
  behavior change has fresh local eval evidence.
- Learning distillation is a report-only promotion path from repeated episodic
  learnings into stable root knowledge; it is not prompt, skill, task, or
  approval mutation.
- Budget/trust posture is report-only visibility over local dispatch metadata;
  it is not budget enforcement, trust promotion, permission elevation, or
  routing authority.
- Dispatch posture history is report-only visibility over recent posture
  snapshots; it is not trend-based policy, routing authority, enforcement, or
  trust promotion.
- Dispatch posture snapshot review is report-only freshness visibility over
  local posture report timestamps; it is not a scheduler, auto-refresh loop,
  routing authority, enforcement, or trust promotion.
- Dispatch posture refresh recommendation is report-only operator guidance over
  the latest staleness review; it is not an automatic refresh, scheduler,
  routing authority, enforcement, retry loop, hosted dashboard, adapter, or
  cost tracker.
- Capability expansion ledger is report-only readiness inventory for deferred
  autonomy surfaces; it is not activation, routing authority, scheduling,
  hosted dashboard, remote execution, adapter operation, budget enforcement,
  trust promotion, retry/replay, CI/deploy proof, or cost tracking.
- Capability readiness review is report-only proof-gap visibility over the
  latest expansion ledger; it is not activation, ledger creation, routing
  authority, scheduling, hosted dashboard, remote execution, adapter operation,
  budget enforcement, trust promotion, retry/replay, CI/deploy proof, or cost
  tracking.
- Capability proof gap index is report-only proof planning over the latest
  readiness review; it is not proof generation, activation, readiness-review
  creation, ledger creation, routing authority, scheduling, hosted dashboard,
  remote execution, adapter operation, budget enforcement, trust promotion,
  retry/replay, CI/deploy proof, or cost tracking.
- Capability approval boundary matrix is report-only approval planning over
  the latest proof-gap index; it is not capability approval, proof generation,
  activation, upstream report creation, routing authority, scheduling, hosted
  dashboard, remote execution, adapter operation, budget enforcement, trust
  promotion, retry/replay, CI/deploy proof, or cost tracking.
- Capability evidence collection plan is report-only manual proof collection
  planning over the latest approval-boundary matrix; it is not evidence
  collection, capability approval, proof generation, activation, upstream
  report creation, routing authority, scheduling, hosted dashboard, remote
  execution, adapter operation, budget enforcement, trust promotion,
  retry/replay, CI/deploy proof, or cost tracking.
- Capability promotion gate checklist is report-only promotion-gate visibility
  over the latest evidence collection plan; it is not evidence collection,
  capability approval, trust promotion, proof generation, activation, upstream
  report creation, routing authority, scheduling, hosted dashboard, remote
  execution, adapter operation, budget enforcement, retry/replay, CI/deploy
  proof, or cost tracking.
- Capability promotion decision ledger is report-only promotion-decision
  visibility over the latest promotion gate checklist; it is not evidence
  collection, capability approval, trust promotion, proof generation,
  activation, upstream report creation, routing authority, scheduling, hosted
  dashboard, remote execution, adapter operation, budget enforcement,
  retry/replay, CI/deploy proof, or cost tracking.
- Capability trust promotion audit is report-only trust-promotion readiness
  visibility over the latest promotion decision ledger; it is not evidence
  collection, capability approval, capability promotion, trust promotion, proof
  generation, activation, upstream report creation, routing authority,
  scheduling, hosted dashboard, remote execution, adapter operation, budget
  enforcement, retry/replay, CI/deploy proof, or cost tracking.
- Capability automatic retry audit is report-only retry-readiness visibility
  over the latest trust promotion audit; it is not evidence collection,
  capability approval, capability promotion, trust promotion, automatic retry
  or replay, proof generation, activation, upstream report creation, routing
  authority, scheduling, hosted dashboard, remote execution, adapter operation,
  budget enforcement, CI/deploy proof, or cost tracking.
- Capability real cost tracking audit is report-only cost-tracking-readiness
  visibility over the latest automatic retry audit; it is not evidence
  collection, capability approval, capability promotion, trust promotion,
  automatic retry or replay, real spend tracking, proof generation, activation,
  upstream report creation, routing authority, scheduling, hosted dashboard,
  remote execution, adapter operation, budget enforcement, CI/deploy proof, or
  external mutation.
- Hosted dashboard proof checklist is report-only hosted-dashboard
  proof-readiness visibility over the latest Real-Cost-sourced Real Cost
  Tracking proof checklist when one exists, with structurally backed proof
  fallback and legacy real cost tracking audit fallback. It avoids promoting
  dangling Real Cost Tracking proof rows without an upstream Automatic Retry
  proof source, preserves the Real Cost Tracking proof's own source metadata
  when present, and is not evidence collection, capability approval,
  capability promotion, trust promotion, automatic retry or replay, real spend
  tracking, proof generation, hosted dashboard activation or deployment,
  upstream report creation, routing authority, scheduling, remote execution,
  adapter operation, budget enforcement, CI/deploy proof, or external mutation.
- Remote worker proof checklist is report-only remote-worker proof-readiness
  visibility over the latest hosted dashboard proof checklist; it is not
  evidence collection, capability approval, capability promotion, trust
  promotion, automatic retry or replay, real spend tracking, proof generation,
  hosted dashboard activation or deployment, remote worker start or claim,
  upstream report creation, routing authority, scheduling, adapter operation,
  budget enforcement, CI/deploy proof, or external mutation. When the hosted
  dashboard source is Real-Cost-sourced, the report keeps both the hosted source
  checklist and that proof checklist's own source metadata.
- Autonomous scheduling proof checklist is report-only scheduler
  proof-readiness visibility over the latest Real-Cost-sourced remote worker
  proof checklist when one exists; it preserves remote-worker proof metadata
  and keeps the remote-worker source proof's own source metadata in the
  generated report when available. It is not evidence collection, capability
  approval, capability promotion, trust promotion, automatic retry or replay,
  real spend tracking, proof generation, hosted dashboard activation or
  deployment, remote worker start or claim, autonomous scheduling, upstream
  report creation, routing authority, adapter operation, budget enforcement,
  CI/deploy proof, or external mutation.
- Browser/desktop adapter proof checklist is report-only adapter
  proof-readiness visibility over the latest autonomous scheduling proof
  checklist; it preserves Real-Cost-sourced autonomous-scheduling proof
  metadata when present and is not evidence collection, capability approval,
  capability promotion, trust promotion, automatic retry or replay, real spend
  tracking, proof generation, hosted dashboard activation or deployment,
  remote worker start or claim, autonomous scheduling, upstream report
  creation, routing authority, adapter operation, budget enforcement,
  CI/deploy proof, or external mutation.
- CI Deploy proof checklist is report-only CI/deploy proof-readiness
  visibility over the latest Real-Cost-sourced browser/desktop adapter proof
  checklist when one exists; it preserves browser/desktop adapter proof
  metadata and the browser/desktop adapter source proof's own source metadata
  when available and is not evidence collection, capability approval, capability
  promotion, trust promotion, automatic retry or replay, real spend tracking,
  proof generation, hosted dashboard activation or deployment, remote worker
  start or claim, autonomous scheduling, adapter operation, CI/deploy
  execution, budget enforcement, routing authority, or external mutation.
- Budget Enforcement proof checklist is report-only budget-enforcement
  proof-readiness visibility over the latest Real-Cost-sourced CI Deploy proof
  checklist when one exists; it preserves CI Deploy proof metadata and the CI
  Deploy source proof's own source metadata when available and is not evidence
  collection, capability approval, capability promotion, trust
  promotion, automatic retry or replay, real spend tracking, proof generation,
  hosted dashboard activation or deployment, remote worker start or claim,
  autonomous scheduling, adapter operation, CI/deploy execution, budget
  enforcement, routing authority, or external mutation.
- Trust Promotion proof checklist is report-only trust-promotion
  proof-readiness visibility over the latest Real-Cost-sourced Budget
  Enforcement proof checklist when one exists; it preserves Budget
  Enforcement proof metadata and the Budget Enforcement source proof's own
  source metadata when available and is not evidence collection, capability
  approval, capability promotion, trust promotion, automatic retry or replay,
  real spend tracking, proof generation, hosted dashboard activation or
  deployment, remote worker start or claim, autonomous scheduling, adapter
  operation, CI/deploy execution, budget enforcement, routing authority, or
  external mutation.
- Automatic Retry proof checklist is report-only retry proof-readiness
  visibility over the latest Real-Cost-sourced Trust Promotion proof checklist
  when one exists; newer legacy or dangling Trust Promotion rows are skipped
  unless the Budget Enforcement -> CI Deploy -> Browser/Desktop Adapter ->
  Autonomous Scheduling -> Remote Worker -> Hosted Dashboard -> Real Cost
  Tracking -> Automatic Retry source chain is retrievable. It is not evidence
  collection, capability approval, capability promotion, trust promotion,
  automatic retry or replay, real spend tracking, proof generation, upstream
  report creation, routing authority, scheduling, remote execution, adapter
  operation, budget enforcement, CI/deploy proof, or external mutation. The
  Trust Promotion upstream proof metadata is preserved into the Automatic Retry
  proof item and source report.
- Real Cost Tracking proof checklist is report-only cost-tracking
  proof-readiness visibility over the latest Real-Cost-sourced Automatic Retry
  proof checklist when one exists; it is not evidence collection, capability
  approval, capability promotion, trust promotion, automatic retry or replay,
  real spend tracking, proof generation, upstream report creation, routing
  authority, scheduling, remote execution, adapter operation, budget
  enforcement, CI/deploy proof, or external mutation. The Automatic Retry
  upstream proof metadata is preserved into the Real Cost Tracking proof item
  and source report.
- Goal Completion Audit is report-only goal-state visibility over the latest
  expansion proof checklist rows. It can report missing proof rows, report-only
  blockers, approvals, and external decisions, but it is not a completion
  marker, approval mechanism, evidence collector, deployment action, scheduler,
  adapter operator, budget enforcer, trust promoter, retry loop, cost tracker,
  routing authority, or external mutation.
- A learning is a durable observation that can improve future runs.

## Evidence-Backed Learning

- `run_ef049fa8bc1b` and the first milestone eval show that the closed-loop
  boundary is now executable enough to serve as a regression test before
  adding dashboards, incidents, approvals, or adapters.
- `run_bdee61e695bb` shows the closed-loop eval remains green after adding the
  static approval gate and dashboard approval visibility.
- `run_395eef2e002e` shows the closed-loop eval remains green after adding
  next-iteration packet generation and dashboard visibility.
- `run_5953ddebb94f` shows the closed-loop eval remains green after adding
  playbook promotion, and the active playbook now summarizes 15 successful
  `first_milestone_closed_loop` runs.
- `run_3f0260c058b7` shows the closed-loop eval remains green after adding
  verifier/workflow gap eval candidates, and the active playbook now summarizes
  16 successful `first_milestone_closed_loop` runs.
- `run_4ca70d56e922` shows the closed-loop eval remains green after adding the
  simplicity guardrail, and the active playbook now summarizes 17 successful
  `first_milestone_closed_loop` runs.
- `run_b3345106e3e7` shows the closed-loop eval remains green after adding
  handoff reviews, and the active playbook now summarizes 18 successful
  `first_milestone_closed_loop` runs.
- `run_e9eb60b88b08` and `run_6bba00951a85` show the closed-loop eval remains
  green after adding eval-after-change checks, and the active playbook now
  summarizes 21 successful `first_milestone_closed_loop` runs.
- `docs/learning-distillation.md` shows one stable learning promoted from 24
  source learning rows after normalizing volatile run ids.
- `docs/budget-trust-posture.md` shows current local task dispatch posture:
  68 tasks, `low=68`, budget state `not_tracked`, and trust state
  `not_tracked`.
- `docs/dispatch-posture-history.md` shows recent report-only posture history:
  12 snapshots, latest 68 tasks, task-count delta 20, `low=68`, budget state
  `not_tracked`, and trust state `not_tracked`.
- `docs/dispatch-posture-staleness.md` shows current report-only posture
  snapshot freshness: status `fresh`, 12 snapshots, 10 stale snapshots, latest
  snapshot age 8 seconds, stale threshold 3600 seconds, and `low=68`.
- `docs/dispatch-posture-refresh.md` shows current report-only refresh
  recommendation: status `no_refresh_needed`, source staleness status `fresh`,
  12 snapshots, 10 stale snapshots, and no recommended commands.
- `docs/capability-expansion-ledger.md` shows current report-only expansion
  posture: status `report_only`, 9 deferred autonomy surfaces, 0 ready
  surfaces, approval boundary `explicit_operator_approval_required`, and
  routing effect `none` for every surface.
- `docs/capability-readiness-review.md` shows current report-only readiness
  posture: status `blocked_by_missing_evidence`, 9 reviewed autonomy surfaces,
  0 ready surfaces, 9 not ready surfaces, and 9 missing evidence paths.
- `docs/capability-proof-gap-index.md` shows current report-only proof-gap
  posture: status `open_gaps`, 9 gaps, 9 missing evidence paths, 9 blocked
  capabilities, 9 next proof labels, and no recommended commands.
- `docs/capability-approval-boundary-matrix.md` shows current report-only
  approval-boundary posture: status `approval_required`, 1 approval boundary,
  9 gaps, 9 blocked capabilities, 9 approvals required, and no recommended
  commands.
- `docs/capability-evidence-collection-plan.md` shows current report-only
  evidence collection posture: status `evidence_required`, 9 manual evidence
  items, 9 approvals required, 1 approval boundary, and no recommended
  commands.
- `docs/capability-promotion-gate-checklist.md` shows current report-only
  promotion posture: status `promotion_blocked`, 9 gates, 9 blocked
  promotions, 9 missing evidence paths, 9 approvals required, 1 approval
  boundary, and no recommended commands.
- `docs/capability-promotion-decision-ledger.md` shows current report-only
  promotion-decision posture: status `promotion_decision_blocked`, 9
  decisions, 9 deferred promotions, 0 operator-ready promotion decisions, 9
  missing evidence paths, 9 approvals required, 1 approval boundary, and no
  recommended commands.
- `docs/capability-trust-promotion-audit.md` shows current report-only
  trust-promotion audit posture: status `trust_promotion_blocked`, 9 audit
  items, 9 blocked trust promotions, 0 operator-ready trust reviews, 9 deferred
  promotions, 9 missing evidence paths, 9 approvals required, 1 approval
  boundary, and no recommended commands.
- `docs/capability-automatic-retry-audit.md` shows current report-only
  automatic-retry audit posture: status `automatic_retry_blocked`, 9 audit
  items, 9 blocked retries, 0 operator-ready retry reviews, 9 blocked trust
  promotions, 9 deferred promotions, 9 missing evidence paths, 9 approvals
  required, 1 approval boundary, and no recommended commands.
- `docs/capability-real-cost-tracking-audit.md` shows current report-only
  real-cost-tracking audit posture: status `real_cost_tracking_blocked`, 9
  audit items, 9 blocked cost-tracking rows, 0 operator-ready cost reviews, 9
  blocked retries, 9 blocked trust promotions, 9 deferred promotions, 9
  missing evidence paths, 9 approvals required, 1 approval boundary, and no
  recommended commands.
- `docs/hosted-dashboard-proof-checklist.md` shows current report-only hosted
  dashboard proof posture: status `hosted_dashboard_proof_blocked`, 1
  checklist item sourced from the latest Real Cost Tracking proof checklist,
  1 blocked dashboard proof, 0 operator-ready dashboard reviews, 1 blocked
  cost-tracking row, 1 blocked retry, 1 blocked trust promotion, 1 missing
  evidence path, 1 approval required, 1 approval boundary, and no recommended
  commands.
- `docs/remote-worker-proof-checklist.md` shows current report-only remote
  worker proof posture: status `remote_worker_proof_blocked`, 1 checklist
  item sourced from a Real-Cost-sourced Hosted Dashboard proof checklist, 1
  blocked worker proof, 0 operator-ready worker reviews, 1 blocked
  hosted-dashboard proof row, 1 blocked cost-tracking row, 1 blocked retry, 1
  blocked trust promotion, 1 missing evidence path, 1 approval required, 1
  approval boundary, and no recommended commands.
- `docs/autonomous-scheduling-proof-checklist.md` shows current report-only
  autonomous scheduling proof posture: status
  `autonomous_scheduling_proof_blocked`, 1 checklist item sourced from a
  Real-Cost-sourced Remote Worker proof checklist, 1 blocked scheduling proof,
  0 operator-ready scheduling reviews, 1 blocked remote worker proof row, 1
  blocked hosted-dashboard proof row, 1 blocked cost-tracking row, 1 blocked
  retry, 1 blocked trust promotion, 1 missing evidence path, 1 approval
  required, 1 approval boundary, and no recommended commands.
- `docs/browser-desktop-adapter-proof-checklist.md` shows current report-only
  browser/desktop adapter proof posture: status
  `browser_desktop_adapter_proof_blocked`, live id
  `browser_desktop_adapter_proof_checklist_814054442404`, 1 checklist item
  sourced from the latest Real-Cost-sourced Autonomous Scheduling proof
  checklist, 1 blocked adapter proof, 0 operator-ready adapter reviews, 1
  blocked autonomous scheduling proof row, 1 blocked remote-worker proof row,
  1 blocked hosted-dashboard proof row, 1 blocked cost-tracking row, 1 blocked
  retry, 1 blocked trust promotion, 1 missing evidence path, 1 approval
  required, 1 approval boundary, and no recommended commands. Its report
  retains the Autonomous Scheduling -> Remote Worker -> Hosted Dashboard ->
  Real Cost Tracking -> Automatic Retry source id/status chain when available.
- `docs/ci-deploy-proof-checklist.md` shows current report-only CI Deploy
  proof posture: status `ci_deploy_proof_blocked`, live id
  `ci_deploy_proof_checklist_f1f00e75b9f2`, 1 checklist item sourced from the
  latest Real-Cost-sourced Browser/Desktop Adapter proof checklist
  `browser_desktop_adapter_proof_checklist_8389f5785db0`, 1 blocked CI Deploy
  proof, 0 operator-ready CI Deploy reviews, 1 blocked browser/desktop adapter
  proof row, 1 blocked autonomous-scheduling proof row, 1 blocked
  remote-worker proof row, 1 blocked hosted-dashboard proof row, 1 blocked
  cost-tracking row, 1 blocked retry, 1 blocked trust promotion, 1 missing
  evidence path, 1 approval required, 1 approval boundary, and no recommended
  commands. The selector scans all local Browser/Desktop Adapter proof rows,
  skips newer legacy rows, skips dangling rows without retrievable Autonomous
  Scheduling, Remote Worker, Hosted Dashboard, Real Cost Tracking, and
  Automatic Retry proof sources, and retains the Browser/Desktop Adapter ->
  Autonomous Scheduling -> Remote Worker -> Hosted Dashboard -> Real Cost
  Tracking -> Automatic Retry source id/status chain when available.
- `docs/budget-enforcement-proof-checklist.md` shows current report-only
  Budget Enforcement proof posture: status
  `budget_enforcement_proof_blocked`, live id
  `budget_enforcement_proof_checklist_5a8fb9bd4410`, 1 checklist item sourced
  from the latest Real-Cost-sourced CI Deploy proof checklist
  `ci_deploy_proof_checklist_1cac90c8a6a4`, 1 blocked budget enforcement
  proof, 0 operator-ready budget reviews, 1 blocked CI Deploy proof row, 1
  blocked browser/desktop adapter proof row, 1 blocked autonomous-scheduling
  proof row, 1 blocked remote-worker proof row, 1 blocked hosted-dashboard
  proof row, 1 blocked cost-tracking row, 1 blocked retry, 1 blocked trust
  promotion, 1 missing evidence path, 1 approval required, 1 approval
  boundary, and no recommended commands. The selector scans all local CI Deploy
  proof rows, skips newer legacy rows, skips dangling rows without retrievable
  Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources, and retains
  the CI Deploy -> Browser/Desktop Adapter -> Autonomous Scheduling -> Remote
  Worker -> Hosted Dashboard -> Real Cost Tracking -> Automatic Retry source
  id/status chain when available.
- `docs/trust-promotion-proof-checklist.md` shows current report-only Trust
  Promotion proof posture: status `trust_promotion_proof_blocked`, 1 checklist
  item sourced from the latest Real-Cost-sourced Budget Enforcement proof
  checklist `budget_enforcement_proof_checklist_69bfa57e4ebe` when one
  exists, live id `trust_promotion_proof_checklist_2505a9003449`, 1 blocked
  Trust Promotion proof, 0 operator-ready
  trust reviews, 1 blocked Budget Enforcement proof row, 1 blocked CI Deploy
  proof row, 1 blocked browser/desktop adapter proof row, 1 blocked
  autonomous-scheduling proof row, 1 blocked remote-worker proof row, 1
  blocked hosted-dashboard proof row, 1 blocked cost-tracking row, 1 blocked
  retry, 1 blocked trust promotion, 1 missing evidence path, 1 approval
  required, 1 approval boundary, and no recommended commands. The generated
  report keeps the Budget Enforcement -> CI Deploy -> Browser/Desktop Adapter
  -> Autonomous Scheduling -> Remote Worker -> Hosted Dashboard -> Real Cost
  Tracking -> Automatic Retry source id/status chain when available, skips
  newer legacy Budget Enforcement rows, and treats dangling Budget Enforcement
  rows without retrievable upstream proof sources as missing proof.
- `docs/automatic-retry-proof-checklist.md` shows current report-only
  Automatic Retry proof posture: status `automatic_retry_proof_blocked`, 1
  checklist item sourced from a Real-Cost-sourced Trust Promotion proof
  checklist, 1 blocked Automatic Retry proof, 0 operator-ready retry reviews,
  1 blocked Trust Promotion proof row, 1 blocked Budget Enforcement proof row,
  1 blocked CI Deploy proof row, 1 blocked browser/desktop adapter proof row,
  1 blocked autonomous-scheduling proof row, 1 blocked remote-worker proof
  row, 1 blocked hosted-dashboard proof row, 1 blocked cost-tracking row, 1
  blocked retry, 1 blocked trust promotion, 1 missing evidence path, 1
  approval required, 1 approval boundary, and no recommended commands. The
  generated report keeps the Trust Promotion -> Budget Enforcement -> CI Deploy
  -> Browser/Desktop Adapter -> Autonomous Scheduling -> Remote Worker ->
  Hosted Dashboard -> Real Cost Tracking -> Automatic Retry source id/status
  chain when available, skips newer legacy Trust Promotion rows, and treats
  dangling Trust Promotion rows without retrievable upstream proof sources as
  missing proof.
- `docs/real-cost-tracking-proof-checklist.md` shows current report-only Real
  Cost Tracking proof posture: status `real_cost_tracking_proof_blocked`, 1
  checklist item sourced from a Real-Cost-sourced Automatic Retry proof
  checklist, 1 blocked Real Cost Tracking proof, 0 operator-ready cost reviews,
  1 blocked Automatic Retry proof row, 1 blocked Trust Promotion proof row, 1
  blocked Budget Enforcement proof row, 1 blocked CI Deploy proof row, 1
  blocked browser/desktop adapter proof row, 1 blocked autonomous-scheduling
  proof row, 1 blocked remote-worker proof row, 1 blocked hosted-dashboard
  proof row, 1 blocked cost-tracking row, 1 blocked retry, 1 blocked trust
  promotion, 1 missing evidence path, 1 approval required, 1 approval
  boundary, and no recommended commands.
- `docs/goal-completion-audit.md` shows current expansion-goal posture: status
  `blocked_by_report_only_proofs`, live id
  `goal_completion_audit_1618bab2ea69`, 9 requirements audited, 0 satisfied,
  9 blocked by report-only proof rows, 9 missing evidence items, 9 approvals
  required, 2 external decisions required, and no recommended commands.
- `docs/expansion-decision-brief.md` is the current operator-facing decision
  packet for expansion promotion. Live id
  `expansion_decision_brief_9b29e3c3ae29`, status
  `operator_decisions_required`, source audit
  `goal_completion_audit_1618bab2ea69`, 11 decision items: 2 external
  decisions plus 9 capability approvals. It is report-only and does not
  approve capabilities, mutate external systems, mark the goal complete, or
  enable hosted dashboard, remote worker, scheduling, adapter, CI/deploy,
  budget, trust, retry, or real-cost behavior.
- `docs/expansion-decision-evidence-index.md` links the current expansion
  decision brief to concrete evidence paths. Live id
  `expansion_decision_evidence_index_923da20181ca`, status
  `evidence_indexed`, source brief `expansion_decision_brief_9b29e3c3ae29`,
  source audit `goal_completion_audit_1618bab2ea69`, 11 evidence items, 2
  external decisions linked to `tasks.md`, 9 capability decisions linked to
  their proof-checklist reports, and 0 missing evidence links. It is
  report-only and does not approve decisions, collect evidence automatically,
  mutate external systems, mark the goal complete, or enable any deferred
  expansion capability.
- `docs/expansion-operator-review-checklist.md` is the current manual
  operator-review checklist. Live id
  `expansion_operator_review_checklist_429aaac491b7`, status
  `operator_review_required`, source index
  `expansion_decision_evidence_index_923da20181ca`, 11 review items,
  11 decisions required, 2 external reviews, 9 capability reviews, 0 missing
  evidence links, and allowed actions `approve,defer,request_more_evidence`.
  It is report-only and does not approve decisions, collect evidence
  automatically, mutate external systems, mark the goal complete, or enable
  any deferred expansion capability.
- `docs/expansion-operator-decision-ledger.md` is the current pending/manual
  decision ledger. Live id `expansion_operator_decision_ledger_9822c2c343b0`,
  status `pending_operator_decisions`, source checklist
  `expansion_operator_review_checklist_429aaac491b7`, 11 decision rows,
  11 pending decisions, 0 approved, 0 deferred, 0 more-evidence-requested,
  2 external decisions, and 9 capability decisions. Allowed actions are not
  actions taken; the ledger is report-only and does not approve decisions,
  collect evidence automatically, mutate external systems, mark the goal
  complete, or enable any deferred expansion capability.
- `docs/expansion-operator-approval-draft.md` is the current draft-only
  approval packet surface after the pending/manual decision ledger. It must
  keep draft rows `draft_only`, approval request status `not_created`, and
  `created_approval_requests: 0`; unusable source ledgers are reported as
  `operator_decision_ledger_not_ready` instead of approval-ready.
- `docs/expansion-operator-approval-request-review.md` is the current schema
  review surface after the draft packet. It keeps all current requests blocked
  with `approval_request_subject_not_modeled`, reports `creation_status=not_created`,
  and preserves `created_approval_requests: 0` until the approval subject model
  is explicitly designed. It should list the missing approval-table fields
  `task_id,goal_id,project_id,task_type,risk_level,policy_name,policy_version`
  as the next schema-design input.
- `docs/expansion-operator-approval-schema-decision.md` is the current schema
  design packet after the request review. It recommends
  `operator_approval_requests_table` and a future `operator_approval_requests`
  schema object while preserving the current task approval gate and applying no
  migration.
- `docs/expansion-operator-approval-schema-migration-plan.md` is the current
  migration-plan packet after the schema decision. It proposes the future
  `operator_approval_requests` table columns, indexes, and migration steps,
  while applying no migration, creating no table, and creating no rows.
- `docs/expansion-operator-approval-schema-migration-approval-request.md` is
  the current approval-boundary packet after the migration plan. It requests
  `apply_operator_approval_requests_schema`, names the `schema_migration`
  boundary, and keeps all migration/table/row creation counts at zero.
- `docs/expansion-operator-approval-schema-migration-decision-ledger.md` is
  the current pending/manual operator-action ledger after the schema migration
  approval request. It records `pending_operator_action` for
  `apply_operator_approval_requests_schema`, keeps approved/deferred/more
  evidence counts at zero, and preserves zero migration/table/approval-row
  creation counters until a separate explicit operator action exists.
- `docs/expansion-operator-approval-schema-migration-action-checklist.md` is
  the current manual action-selection checklist after the decision ledger. It
  keeps `selected_action=none`, `actions_taken: 0`, and all
  migration/table/approval-row creation counters at zero until a distinct
  operator selection flow exists.
- `docs/expansion-operator-approval-schema-migration-selection-packet.md` is
  the current operator-input packet after the manual action checklist. It
  keeps `selected_action=none`, `selections_recorded: 0`,
  `actions_taken: 0`, and all migration/table/approval-row creation counters
  at zero until a distinct operator selection flow is designed and verified.
- Accepted blocked downstream result decisions can be bridged into the next
  operator-visible stage as generic `effects` rows with a stage-specific
  idempotency prefix. This proposal stage should not add a new table, create
  approval rows, apply effects, satisfy proof, allow activation, or enable
  capabilities; the separate application-record slice owns durable application
  rows.
- Accepted blocked downstream result effect task result decision effects can
  be bridged through local application records that mark applicable effects
  `applied` and write application evidence while still preserving zero
  approval rows, zero activation actions, zero external mutations,
  `activation_allowed=false`, and `capability_enabled=false`.
- Applied downstream result effect task result decision effects should become
  pending task graph rows before routing or delegation. The task-materializing
  stage must preserve source decision, result, application, effect,
  delegation, task, contract, project, and capability links while keeping
  approval rows, activation actions, external mutations, activation allowance,
  and capability enablement at zero.
- Pending downstream result effect task result effect tasks should route into
  read-only evaluator delegation packets before result ingestion. The routing
  stage must create durable routing decisions, pending subagent delegation
  rows, and local JSON artifacts while preserving source links and keeping
  execution, provider calls, approval rows, activation actions, external
  mutations, activation allowance, and capability enablement at zero.
- Completed downstream result effect task result effect delegation packets
  should become local result records and JSON artifacts before operator
  review. The ingestion stage must preserve source decision, result,
  application, effect, delegation, task, contract, project, and capability
  links while keeping approval rows, activation actions, external mutations,
  activation allowance, capability enablement, and proof satisfaction at zero.
- `eval` and `eval-after-change` both write the
  `first_milestone_closed_loop` result path and should be run serially, not in
  parallel. A parallel invocation can leave a failed run artifact even when the
  serial baseline eval passes immediately afterward.
- Downstream result effect task result effect result decisions should allow
  preliminary `request_more_evidence` or `defer_review` rows to be superseded
  by a later `accept_keep_blocked` decision for the same result. Accepted
  keep-blocked decisions are the terminal source for the next proposed-effect
  slice while preserving zero approval rows, zero activation actions, zero
  external mutations, `activation_allowed=false`, and
  `capability_enabled=false`.
- Accepted blocked downstream result effect task result effect result
  decisions should become generic proposal-only `effects` rows with a
  stage-specific idempotency prefix before any application-record slice. The
  proposal stage should preserve source decision, result, application, effect,
  delegation, task, contract, project, and capability links while keeping
  approval rows, activation actions, external mutations, activation allowance,
  and capability enablement at zero.
- Downstream result effect task result effect result decision effect
  applications should remain ledger-only: they record an application row, mark
  applicable generic `effects` rows as `applied`, preserve source decision,
  result, application, effect, delegation, task, contract, project, and
  capability links, and still keep approval rows, activation actions,
  external mutations, activation allowance, and capability enablement at zero.
- Applied downstream result effect task result effect result decision effect
  applications should become pending downstream proof tasks, not activation:
  preserve source decision, result, application, effect, delegation, task,
  contract, project, and capability links in task evidence while keeping
  approval rows, activation actions, external mutations, activation allowance,
  capability enablement, and proof satisfaction at zero.
- Pending downstream result effect task result effect task result effect tasks
  should route into read-only evaluator delegation packets before result
  ingestion. The routing stage must create durable routing decisions, pending
  subagent delegation rows, and local JSON artifacts while preserving source
  links and keeping execution, provider calls, approval rows, activation
  actions, external mutations, activation allowance, and capability enablement
  at zero.
- Completed downstream result effect task result effect task result effect
  delegation outputs should ingest into local result records only. The
  ingestion stage must preserve source decision, result, application, effect,
  delegation, task, contract, project, and capability links while keeping
  proof satisfaction, approval rows, activation actions, external mutations,
  activation allowance, and capability enablement at zero.
- Downstream result effect task result effect task result effect task result
  decisions should allow preliminary `request_more_evidence` or
  `defer_review` rows to be superseded by a later `accept_keep_blocked`
  decision for the same result. Accepted keep-blocked decisions are the
  terminal source for the next proposed-effect slice while preserving zero
  approval rows, zero activation actions, zero external mutations,
  `activation_allowed=false`, and `capability_enabled=false`.
- Accepted blocked downstream result effect task result effect task result
  effect task result decisions should become generic proposal-only `effects`
  rows with a stage-specific idempotency prefix before any application-record
  slice. The proposal stage should preserve source decision, result,
  application, effect, delegation, task, contract, project, and capability
  links while keeping approval rows, activation actions, external mutations,
  activation allowance, and capability enablement at zero.
- Downstream result effect task result effect task result effect task result
  decision effect applications should remain ledger-only: they record an
  application row, mark applicable generic `effects` rows as `applied`,
  preserve source decision, result, application, effect, delegation, task,
  contract, project, and capability links, and still keep approval rows,
  activation actions, external mutations, activation allowance, and
  capability enablement at zero.
- Applied downstream result effect task result effect task result effect task
  result decision effect applications should become pending downstream proof
  tasks before routing or delegation. The task materialization stage must
  preserve source decision, result, application, effect, delegation, task,
  contract, project, and capability links while keeping approval rows,
  activation actions, external mutations, activation allowance, capability
  enablement, and proof satisfaction at zero.

## Stable Distilled Learnings

<!-- learning-distillation:start -->
- source: docs/learning-distillation.md
- status: stable
- min_occurrences: 3
- source_learnings: 24
- stable_learnings: 1

- Run run_<id> showed that the first closed loop can be verified through file evidence before expanding to broader domains. (occurrences=24, evidence=docs/learning-distillation.md)
<!-- learning-distillation:end -->
