# Workflow

## Goal Run Lifecycle

1. Intake a goal.
2. Persist the goal and create a run id.
3. Decompose the goal into typed tasks.
4. Persist tasks before dispatch.
5. Dispatch policy checks runnable pending tasks before claim.
6. Approval-required tasks move to `waiting_approval` with a persisted request.
7. Approved tasks return to `pending`.
8. Worker claims one safe or approved pending task at a time.
9. Worker executes the task and writes artifacts.
10. Verifier checks expected outputs and records evidence.
11. Failed verification opens an incident with JSON evidence.
12. Explicit stuck-task sweeps block stale active tasks and open incidents.
13. Open incidents can be resolved with operator notes and JSON resolution evidence.
14. Queue-health checks report repeated blocked or failed work without
    retrying it automatically.
15. Handoff reviews report blocked tasks and project handoffs that do not
    reference the current iteration packet.
16. Eval-after-change checks link named harness changes to local eval evidence.
17. Verifier or workflow gaps create proposed eval candidates.
18. Repeated run learnings can be distilled into stable root knowledge when
    they recur enough times.
19. Budget/trust posture reports expose local dispatch metadata without
    enforcing budgets, promoting trust, or changing routing.
20. Dispatch posture history summarizes recent report-only posture snapshots
    without changing dispatch behavior.
21. Dispatch posture snapshot reviews check recent posture report timestamps
    without scheduling refreshes or changing dispatch behavior.
22. Dispatch posture refresh recommendations convert staleness reviews into
    manual command recommendations without running or scheduling them.
23. Capability expansion ledgers enumerate deferred autonomy surfaces and
    required proof before enabling any of them.
24. Capability readiness reviews check latest ledger evidence before promoting
    any deferred capability.
25. Capability proof gap indexes turn readiness gaps into explicit proof work
    without generating proof or changing dispatch behavior.
26. Capability approval boundary matrices map proof gaps to explicit operator
    approval boundaries without approving capabilities.
27. Capability evidence collection plans turn approval boundaries into manual
    evidence items without collecting proof or changing dispatch behavior.
28. Capability promotion gate checklists turn evidence plans into blocked or
    ready promotion gates without approving or promoting capabilities.
29. Capability promotion decision ledgers record report-only defer/manual
    review decisions from promotion gates without changing routing or trust.
30. Capability trust promotion audits review promotion decisions before any
    trust promotion, routing change, or capability activation exists.
31. Capability automatic retry audits review trust-promotion audits before any
    retry, replay, routing change, or scheduler behavior exists.
32. Capability real cost tracking audits review automatic-retry audits before
    any spend tracking, budget enforcement, routing change, or scheduler
    behavior exists.
33. Hosted dashboard proof checklists review real-cost-tracking audits before
    any hosted dashboard, deployment, routing change, or scheduler behavior
    exists.
34. Remote worker proof checklists review hosted-dashboard proof checklists
    before any remote worker, remote claim, routing change, or scheduler
    behavior exists.
35. Expansion operator decision ledgers record pending/manual decision posture
    from review checklists without approving, promoting, routing, or taking
    any external action.
36. Expansion operator approval drafts prepare draft-only approval-request
    packets from usable pending decision ledgers without creating
    `approval_requests`, taking allowed actions, approving, promoting, routing,
    or mutating external systems.
37. Expansion operator approval request reviews check those drafts against the
    current `approval_requests` contract, record schema gaps, and keep
    `created_approval_requests: 0` until the
    `approval_request_subject_not_modeled` gap is resolved and the approval
    subject model is chosen.
38. Expansion operator approval schema decisions convert schema-gap reviews into
    a report-only recommendation, currently `operator_approval_requests_table`,
    without applying migrations, creating approvals, or taking operator actions.
39. Expansion operator approval schema migration plans convert the chosen
    schema option into proposed columns, indexes, and migration steps for a
    future `operator_approval_requests` table without applying the migration,
    creating the table, creating approval rows, or changing routing.
40. Expansion operator approval schema migration approval requests convert the
    migration plan into an explicit operator approval packet with allowed
    actions before any schema is applied, table is created, approval row is
    written, or routing changes.
41. Expansion operator approval schema migration decision ledgers convert that
    approval packet into a pending/manual operator-action ledger without
    applying the schema, creating the table, creating approval rows, or taking
    an operator action.
42. Expansion operator approval schema migration action checklists convert the
    pending/manual ledger into explicit operator choices while keeping
    `selected_action=none`, recording no action taken, and applying no schema
    or approval-row mutation.
43. Expansion operator approval schema migration selection packets convert that
    action checklist into an operator-input packet while keeping
    `selected_action=none`, `selections_recorded=0`, recording no action
    taken, and applying no schema or approval-row mutation.
44. Expansion operator approval schema migration selection input templates
    capture the explicit operator fields needed before applying the schema
    while recording no schema or approval-row mutation.
45. Expansion operator approval schema migration applications apply the local
    `operator_approval_requests` schema only after an approved selection while
    keeping `approval_requests_created=0`.
46. Operator approval request row applications create pending local
    `operator_approval_requests` rows from approved drafts after the schema
    exists while keeping legacy `approval_requests` untouched.
47. Operator approval request decisions record approve/defer/more-evidence
    decisions for local operator request rows without enabling capabilities.
48. Operator approval effect proposals convert approved local operator request
    decisions into `proposed` effect rows while taking zero activation actions.
49. Operator approval effect applications move proposed effects to local
    `applied` records while keeping `capability_enabled=false`.
50. Capability activation tasks materialize applied capability effects into
    pending high-risk activation-gate tasks.
51. Capability activation contracts convert pending activation-gate tasks into
    blocked evidence and approval contracts without creating approval rows or
    taking activation actions.
52. Capability activation evidence ingestion attaches local operator-supplied
    evidence rows and JSON artifacts to those contracts without satisfying
    proof or enabling capabilities.
53. Capability activation decisions record local approve/defer/more-evidence
    decisions for evidence-bearing contracts while keeping activation actions
    at zero.
54. Capability activation follow-up task creation turns more-evidence
    decisions into pending high-risk task graph work while keeping activation
    actions at zero.
55. Capability activation follow-up delegation packet creation routes pending
    follow-up evidence tasks to read-only evaluator delegation contracts while
    keeping subagent execution and activation actions at zero.
56. Capability activation follow-up result ingestion records completed
    read-only evaluator delegation results as local evidence artifacts while
    keeping proof satisfaction, approval rows, activation actions, and
    capability enablement blocked.
57. Capability activation follow-up result decisions record local operator
    accept-keep-blocked/request-more-evidence/defer decisions for ingested
    result records while keeping approval rows, contract mutation, activation
    actions, and capability enablement blocked.
58. Capability activation follow-up result effect proposals convert accepted
    keep-blocked follow-up result decisions into idempotent `proposed` effect
    rows while keeping approval rows, external mutations, activation actions,
    activation allowance, and capability enablement blocked.
59. Capability activation follow-up result effect application records accepted
    blocked follow-up decision effects as local `applied` ledger rows while
    keeping approval rows, external mutations, activation actions, activation
    allowance, and capability enablement blocked.
60. Capability activation follow-up result downstream tasks materialize applied
    accepted-blocked follow-up result effects into pending high-risk proof
    tasks while keeping approval rows, external mutations, activation actions,
    activation allowance, and capability enablement blocked.
61. Capability activation follow-up result task delegation packet creation
    routes pending downstream proof tasks to read-only evaluator delegation
    contracts while keeping subagent execution, provider calls, approval rows,
    external mutations, activation actions, activation allowance, and
    capability enablement blocked.
62. Capability activation follow-up result task result ingestion records
    completed downstream proof-plan delegation outputs as local result records
    while keeping approval rows, external mutations, activation actions,
    activation allowance, capability enablement, and proof satisfaction
    blocked.
63. Capability activation follow-up result task decisions record local
    accept-keep-blocked/request-more-evidence/defer decisions for downstream
    proof-plan result records while keeping approval rows, external mutations,
    activation actions, activation allowance, capability enablement, and proof
    satisfaction blocked.
64. Capability activation follow-up result task result effect proposals convert
    accepted keep-blocked downstream proof-plan result decisions into
    idempotent `proposed` effect rows while keeping approval rows, external
    mutations, activation actions, activation allowance, capability enablement,
    and proof satisfaction blocked.
65. Capability activation follow-up result task result effect application
    records accepted keep-blocked downstream proof-plan result decision effects
    as local `applied` ledger rows while keeping approval rows, external
    mutations, activation actions, activation allowance, capability enablement,
    and proof satisfaction blocked.
66. Capability activation follow-up result task result effect downstream tasks
    materialize applied downstream result decision effects into pending
    high-risk proof tasks while keeping approval rows, external mutations,
    activation actions, activation allowance, capability enablement, and proof
    satisfaction blocked.
67. Capability activation follow-up result task result effect task delegation
    packet creation routes pending downstream result effect proof tasks to
    read-only evaluator delegation contracts while keeping subagent execution,
    provider calls, approval rows, external mutations, activation actions,
    activation allowance, and capability enablement blocked.
68. Capability activation follow-up result task result effect task result
    ingestion records completed downstream result effect task delegation
    outputs as local result records while preserving the same blocked proof
    state and source application, decision, result, task, contract, project,
    and capability links.
69. Capability activation follow-up result task result effect task result
    decisions record local accept-keep-blocked/request-more-evidence/defer
    decisions for downstream result effect task result records while keeping
    approval rows, external mutations, activation actions, activation
    allowance, capability enablement, and proof satisfaction blocked.
70. Autonomous scheduling proof checklists review the latest
    Real-Cost-sourced remote-worker proof checklist when one exists before any
    scheduler, remote worker, routing change, or claim behavior exists,
    preserving remote-worker proof metadata and the remote-worker source
    proof's own source metadata when present.
71. Browser desktop adapter proof checklists review the latest
    Real-Cost-sourced autonomous-scheduling proof checklist when one exists
    before any browser/desktop adapter operation or routing change exists,
    preserving autonomous-scheduling proof metadata and the
    autonomous-scheduling source proof's own source metadata when present.
72. CI Deploy proof checklists review browser desktop adapter proof checklists
    before any CI run, deploy, or routing change exists, preserving
    Real-Cost-sourced browser/desktop adapter proof metadata when present.
73. Budget Enforcement proof checklists review the latest Real-Cost-sourced
    CI Deploy proof checklist when one exists before any budget enforcement,
    CI/deploy, or routing change exists, preserving CI Deploy proof metadata
    and the CI Deploy source proof's own source metadata when available.
74. Trust Promotion proof checklists review the latest Real-Cost-sourced
    Budget Enforcement proof checklist when one exists before any trust
    promotion, budget enforcement, or routing change exists, preserving
    Budget Enforcement proof metadata and the Budget Enforcement source
    proof's own source metadata when available.
75. Automatic Retry proof checklists review Trust Promotion proof checklists
    before any retry, replay, trust promotion, or routing change exists,
    preserving Real-Cost-sourced Trust Promotion proof metadata when present.
76. Real Cost Tracking proof checklists review Automatic Retry proof
    checklists before any spend tracking, retry, budget enforcement, or
    routing change exists.
77. Repeated successful eval runs can be promoted into reusable playbooks.
78. Equal-score queue choices prefer lower complexity before adding
    orchestration.
79. Completed tasks update project memory and activity.
80. Run summary mirrors status to project files.
81. Learning loop records one improvement candidate.
82. Static dashboard generation mirrors queue health, handoff reviews,
    eval-after-change checks, learning distillation, budget/trust posture,
    dispatch posture history, dispatch posture snapshot reviews, dispatch
    posture refresh recommendations, capability expansion ledgers, capability
    readiness reviews, capability proof gap indexes, capability approval
    boundary matrices, capability evidence collection plans, capability
    promotion gate checklists, capability promotion decision ledgers,
    capability trust promotion audits, capability automatic retry audits,
    capability real cost tracking audits, hosted dashboard proof checklists,
    remote worker proof checklists, autonomous scheduling proof checklists,
    browser desktop adapter proof checklists, CI Deploy proof checklists,
    budget enforcement proof checklists, trust promotion proof checklists,
    automatic retry proof checklists, real cost tracking proof checklists,
    goal completion audits, expansion decision briefs, expansion decision
    evidence indexes, expansion operator review checklists, expansion
    operator decision ledgers, expansion operator approval drafts, expansion
    operator approval request reviews, expansion operator approval schema
    decisions, expansion operator approval schema migration plans, expansion
    operator approval schema migration approval requests, expansion operator
    approval schema migration decision ledgers, expansion operator approval
    schema migration action checklists, expansion operator approval schema
    migration selection packets, capability activation tasks, capability
    activation contracts, capability activation evidence, capability
    activation decisions, capability activation follow-up tasks, capability
    activation follow-up delegations, capability activation follow-up results,
    capability activation follow-up result decisions, capability activation
    follow-up result effect proposals, capability activation follow-up result
    effect applications, capability activation follow-up result downstream
    tasks, capability activation follow-up result task delegations, capability
    activation follow-up result task results, capability activation follow-up
    result task decisions, capability activation follow-up result task result
    effect proposals, capability activation follow-up result task result
    effect applications, capability activation follow-up result task result
    effect tasks, capability activation follow-up result task result effect
    task delegations, capability activation follow-up result task result
    effect task results, capability activation follow-up result task result
    effect task result decisions, playbooks, eval candidates, approvals, stuck
    tasks, incidents, and recent evidence.

## Incident Resolution Lifecycle

1. Inspect the open incident and original evidence path from `docs/dashboard.md`
   or SQLite state.
2. Run
   `python3 -m agent_os.cli resolve-incident <incident_id> --resolved-by operator --note "..."`
   after the local operator decision is ready.
3. The runtime writes `runs/<run_id>/incidents/<incident_id>-resolution.json`.
4. SQLite updates the incident to `resolved` with `resolved_at`,
   `resolved_by`, `resolution_note`, and `resolution_evidence_path`.
5. The run event log receives `incident.resolved` for the closure.
6. The static dashboard shows resolved counts and the resolution evidence path.

## Queue Health Lifecycle

1. Run `python3 -m agent_os.cli queue-health`.
2. The command groups `blocked` and `failed` tasks by project and task type.
3. Groups at or above the configured threshold are written to
   `docs/queue-health.md`.
4. The static dashboard mirrors the same hotspots under
   `## Queue Health Checks`.
5. Queue-health checks are report-only until a later policy slice adds
   escalation, quarantine, or replay controls.

## Handoff Review Lifecycle

1. Run `python3 -m agent_os.cli handoff-review`.
2. The command reads blocked task state from SQLite and discovers project
   handoff files under `projects/*/handoff.md`.
3. The latest iteration packet focus is treated as the current handoff anchor.
4. Handoff files that do not reference that focus are reported as stale.
5. The command writes `docs/handoff-review.md` and stores a `handoff_reviews`
   row with counts, reviewed paths, blocked task summaries, and stale handoff
   findings.
6. The static dashboard mirrors the latest review under `## Handoff Review`.
7. Handoff reviews are report-only; they do not resolve incidents, requeue
   tasks, edit handoff files, or advance work automatically.

## Eval After Change Lifecycle

1. Run
   `python3 -m agent_os.cli eval-after-change --change "<summary>" --file <path>`.
2. The command runs the local eval suite, currently
   `first_milestone_closed_loop`.
3. The command records a SQLite `eval_after_change_checks` row with the change
   summary, changed paths, eval names, status, result paths, run ids, command,
   report path, and timestamps.
4. The command writes `docs/eval-after-change.md`.
5. The static dashboard mirrors recent checks under `## Eval After Change`.
6. This is manual report-only evidence. It is not a scheduler, file watcher,
   CI gate, deploy gate, or automatic rollback mechanism.

## Learning Distillation Lifecycle

1. Run `python3 -m agent_os.cli distill-learnings --min-occurrences 3`.
2. The command reads the SQLite `learnings` table and groups exact repeated
   summaries after normalizing volatile run ids from `run_<value>` to
   `run_<id>`.
3. Groups at or above the occurrence threshold are written to
   `docs/learning-distillation.md`.
4. SQLite records a `learning_distillations` row with status, threshold,
   source-learning count, stable-learning count, report path, and stable
   learning evidence.
5. Root `knowledge.md` receives one generated `## Stable Distilled Learnings`
   block that is replaced idempotently on rerun.
6. The static dashboard mirrors the latest distillation under
   `## Learning Distillation`.
7. Learning distillation is report-only local evidence. It does not edit
   prompts, skills, playbooks, handoffs, tasks, approvals, schedulers, CI
   gates, deploy gates, retries, replays, or external systems automatically.

## Budget And Trust Posture Lifecycle

1. Run `python3 -m agent_os.cli budget-trust-posture`.
2. The command reads local task metadata from SQLite, including task count and
   current `risk_level` values.
3. The command writes `docs/budget-trust-posture.md` and records a
   `budget_trust_posture_reports` row with task count, risk counts, budget
   state, trust state, report path, and report-only summaries.
4. The static dashboard mirrors the latest posture under
   `## Budget And Trust Posture`.
5. Budget posture currently means visible local metadata only. It is not budget
   consumption, quota tracking, cost accounting, or spend control.
6. Trust posture currently means visible local metadata only. It is not trust
   promotion, permission elevation, or routing authority.
7. Approval gates remain the only current dispatch control. This report does
   not change task routing, approval decisions, worker claiming, retries,
   replays, schedulers, CI gates, deploy gates, hosted dashboards, remote
   workers, or external systems.

## Dispatch Posture History Lifecycle

1. Run `python3 -m agent_os.cli dispatch-posture-history`.
2. The command reads recent `budget_trust_posture_reports` rows from SQLite.
3. The command writes `docs/dispatch-posture-history.md` and records a
   `dispatch_posture_history_summaries` row with snapshot count, latest task
   count, task-count delta, latest risk counts, budget states, trust states,
   report path, and timestamps.
4. The static dashboard mirrors the latest summary under
   `## Dispatch Posture History`.
5. Dispatch posture history currently means visibility over local metadata
   snapshots. It does not enforce budgets, promote trust, alter routing,
   change approval decisions, affect worker claiming, retry, replay, schedule,
  gate CI/deploy, run a hosted dashboard, control remote workers, or touch
  external systems.

## Dispatch Posture Snapshot Review Lifecycle

1. Run `python3 -m agent_os.cli dispatch-posture-staleness`.
2. The command reads recent `budget_trust_posture_reports` rows from SQLite and
   compares their `created_at` timestamps with the review clock.
3. The command writes `docs/dispatch-posture-staleness.md` and records a
   `dispatch_posture_staleness_reviews` row with snapshot count,
   stale-snapshot count, latest snapshot age, threshold, latest task count,
   latest risk counts, report path, and timestamps.
4. The static dashboard mirrors the latest review under
   `## Dispatch Posture Snapshot Review`.
5. Missing history is reported as `missing_history`; old non-latest snapshots
   can increment `stale_snapshots` while the overall status remains `fresh`
   when the latest snapshot is within threshold.
6. Snapshot review currently means report-only local timestamp visibility. It
   does not run posture reports automatically, schedule refreshes, enforce
   budgets, promote trust, alter routing, change approval decisions, affect
   worker claiming, retry, replay, schedule, gate CI/deploy, run a hosted
   dashboard, control remote workers, or touch external systems.

## Dispatch Posture Refresh Recommendation Lifecycle

1. Run `python3 -m agent_os.cli dispatch-posture-refresh`.
2. The command reads only the latest persisted
   `dispatch_posture_staleness_reviews` row from SQLite.
3. The command writes `docs/dispatch-posture-refresh.md` and records a
   `dispatch_posture_refresh_recommendations` row with source review id,
   source review status, snapshot counts, latest snapshot age, stale threshold,
   recommended commands, reason, approval boundary, deferred-capability
   context, report path, and timestamps.
4. The static dashboard mirrors the latest recommendation under
   `## Dispatch Posture Refresh Recommendation`.
5. Status values are `no_refresh_needed`, `manual_refresh_recommended`,
   `snapshot_seed_recommended`, and `staleness_review_missing`.
6. Refresh recommendation currently means report-only local operator guidance.
   It does not run recommended commands automatically, create staleness reviews
   as a side effect, schedule refreshes, enforce budgets, promote trust, alter
   routing, change approval decisions, affect worker claiming, retry, replay,
   schedule, gate CI/deploy, run a hosted dashboard, control remote workers,
   operate browser or desktop adapters, track real costs, or touch external
   systems.

## Capability Expansion Ledger Lifecycle

1. Run `python3 -m agent_os.cli capability-expansion-ledger`.
2. The command writes `docs/capability-expansion-ledger.md` and records a
   `capability_expansion_ledgers` row with capability count, ready count,
   deferred count, approval boundary, report path, and a JSON list of
   capability entries.
3. Each entry names the capability, current state, required evidence, next
   proof, approval boundary, and routing effect.
4. The static dashboard mirrors the latest ledger under
   `## Capability Expansion Ledger`.
5. The iteration packet includes the command in its verification list and
   reports the latest `capability expansion ledger` posture.
6. The ledger currently means report-only local readiness inventory. It does
   not enable hosted dashboards, start remote workers, schedule autonomous
   work, operate browser or desktop adapters, run CI or deploys, enforce
   budgets, promote trust, retry or replay work, track real spend, change
   routing, or touch external systems.

## Capability Readiness Review Lifecycle

1. Run `python3 -m agent_os.cli capability-readiness-review`.
2. The command reads only the latest persisted `capability_expansion_ledgers`
   row from SQLite.
3. If no ledger exists, the command writes a `ledger_missing` review and
   recommends `capability-expansion-ledger` without creating a ledger itself.
4. When a ledger exists, each capability entry is checked for attached evidence
   and summarized as `ready` or `not_ready`.
5. The command writes `docs/capability-readiness-review.md` and records a
   `capability_readiness_reviews` row with source ledger id/status, capability
   counts, readiness counts, missing evidence count, recommended manual
   commands, approval boundary, report path, and reviewed entries.
6. The static dashboard mirrors the latest review under
   `## Capability Readiness Review`.
7. The iteration packet includes the command in its verification list and
   reports the latest `capability readiness review` posture.
8. Status values are `ready`, `blocked_by_missing_evidence`, and
   `ledger_missing`.
9. The review currently means report-only local proof-gap visibility. It does
   not create ledgers as a side effect, enable hosted dashboards, start remote
   workers, schedule autonomous work, operate browser or desktop adapters, run
   CI or deploys, enforce budgets, promote trust, retry or replay work, track
   real spend, change routing, or touch external systems.

## Capability Proof Gap Index Lifecycle

1. Run `python3 -m agent_os.cli capability-proof-gap-index`.
2. The command reads only the latest persisted
   `capability_readiness_reviews` row from SQLite.
3. If no readiness review exists, the command writes a
   `readiness_review_missing` index and recommends
   `capability-readiness-review` without creating a review itself.
4. When a readiness review exists, each non-ready or missing-evidence
   capability becomes a proof-gap entry with capability, gap type, readiness,
   evidence state, required evidence, next proof, approval boundary, and
   routing effect.
5. The command writes `docs/capability-proof-gap-index.md` and records a
   `capability_proof_gap_indexes` row with source review id/status, capability
   count, gap counts, missing evidence count, blocked capability count,
   next-proof count, recommended manual commands, approval boundary, report
   path, and indexed gaps.
6. The static dashboard mirrors the latest index under
   `## Capability Proof Gap Index`.
7. The iteration packet includes the command in its verification list and
   reports the latest `capability proof gap index` posture.
8. Status values are `open_gaps`, `no_open_gaps`, and
   `readiness_review_missing`.
9. The index currently means report-only local proof planning. It does not
   create readiness reviews or ledgers as a side effect, generate proof
   artifacts automatically, enable hosted dashboards, start remote workers,
   schedule autonomous work, operate browser or desktop adapters, run CI or
   deploys, enforce budgets, promote trust, retry or replay work, track real
   spend, change routing, or touch external systems.

## Capability Approval Boundary Matrix Lifecycle

1. Run `python3 -m agent_os.cli capability-approval-boundary-matrix`.
2. The command reads only the latest persisted
   `capability_proof_gap_indexes` row from SQLite.
3. If no proof-gap index exists, the command writes a
   `proof_gap_index_missing` matrix and recommends
   `capability-proof-gap-index` without creating an index itself.
4. When a proof-gap index exists, each proof gap becomes a matrix entry with
   capability, approval boundary, decision state, gap type, required evidence,
   next proof, and routing effect.
5. The command writes `docs/capability-approval-boundary-matrix.md` and
   records a `capability_approval_boundary_matrices` row with source index
   id/status, capability count, boundary count, gap count, blocked capability
   count, approval-required count, recommended manual commands, report path,
   boundary rows, and matrix entries.
6. The static dashboard mirrors the latest matrix under
   `## Capability Approval Boundary Matrix`.
7. The iteration packet includes the command in its verification list and
   reports the latest `capability approval boundary matrix` posture.
8. Status values are `approval_required`, `no_approval_required`, and
   `proof_gap_index_missing`.
9. The matrix currently means report-only local approval-boundary visibility.
   It does not create proof-gap indexes, readiness reviews, or ledgers as a
   side effect, approve capabilities automatically, generate proof artifacts,
   enable hosted dashboards, start remote workers, schedule autonomous work,
   operate browser or desktop adapters, run CI or deploys, enforce budgets,
   promote trust, retry or replay work, track real spend, change routing,
   change claims, or touch external systems.

## Capability Evidence Collection Plan Lifecycle

1. Run `python3 -m agent_os.cli capability-evidence-collection-plan`.
2. The command reads only the latest persisted
   `capability_approval_boundary_matrices` row from SQLite.
3. If no approval-boundary matrix exists, the command writes an
   `approval_boundary_matrix_missing` plan and recommends
   `capability-approval-boundary-matrix` without creating a matrix itself.
4. When a matrix exists, each matrix entry becomes a manual evidence item with
   capability, required evidence, next proof label, collection mode, evidence
   state, approval boundary, decision state, and routing effect.
5. The command writes `docs/capability-evidence-collection-plan.md` and
   records a `capability_evidence_collection_plans` row with source matrix
   id/status, capability count, evidence-item count, manual collection count,
   approval-required count, boundary count, recommended manual commands,
   report path, and evidence items.
6. The static dashboard mirrors the latest plan under
   `## Capability Evidence Collection Plan`.
7. The iteration packet includes the command in its verification list and
   reports the latest `capability evidence collection plan` posture.
8. Status values are `evidence_required`, `no_evidence_required`, and
   `approval_boundary_matrix_missing`.
9. The plan currently means report-only manual evidence planning. It does not
   create approval-boundary matrices, proof-gap indexes, readiness reviews, or
   ledgers as a side effect, collect evidence automatically, approve
   capabilities automatically, generate proof artifacts, enable hosted
   dashboards, start remote workers, schedule autonomous work, operate browser
   or desktop adapters, run CI or deploys, enforce budgets, promote trust,
   retry or replay work, track real spend, change routing, change claims, or
   touch external systems.

## Capability Promotion Gate Checklist Lifecycle

1. Run `python3 -m agent_os.cli capability-promotion-gate-checklist`.
2. The command reads only the latest persisted
   `capability_evidence_collection_plans` row from SQLite.
3. If no evidence collection plan exists, the command writes an
   `evidence_collection_plan_missing` checklist and recommends
   `capability-evidence-collection-plan` without creating a plan itself.
4. When an evidence collection plan exists but is incomplete, the checklist
   preserves the source plan's recommended manual commands instead of
   reporting promotion readiness.
5. When a complete plan exists, each evidence item becomes a promotion gate
   with capability, promotion gate state, evidence item, required evidence,
   evidence state, approval state, approval boundary, and routing effect.
6. The command writes `docs/capability-promotion-gate-checklist.md` and
   records a `capability_promotion_gate_checklists` row with source plan
   id/status, capability count, gate count, blocked-promotion count, missing
   evidence count, approval-required count, boundary count, recommended manual
   commands, report path, and checklist items.
7. The static dashboard mirrors the latest checklist under
   `## Capability Promotion Gate Checklist`.
8. The iteration packet includes the command in its verification list and
   reports the latest `capability promotion gate checklist` posture.
9. Status values are `promotion_blocked`, `promotion_ready`, and
   `evidence_collection_plan_missing`.
10. The checklist currently means report-only promotion-gate visibility. It
    does not create evidence collection plans, approval-boundary matrices,
    proof-gap indexes, readiness reviews, or ledgers as a side effect, collect
    evidence automatically, approve capabilities automatically, promote
    capabilities automatically, generate proof artifacts, enable hosted
    dashboards, start remote workers, schedule autonomous work, operate browser
    or desktop adapters, run CI or deploys, enforce budgets, promote trust,
    retry or replay work, track real spend, change routing, change claims, or
    touch external systems.

## Capability Promotion Decision Ledger Lifecycle

1. Run `python3 -m agent_os.cli capability-promotion-decision-ledger`.
2. The command reads only the latest persisted
   `capability_promotion_gate_checklists` row from SQLite.
3. If no promotion gate checklist exists, the command writes a
   `promotion_gate_checklist_missing` ledger and recommends
   `capability-promotion-gate-checklist` without creating a checklist itself.
4. When a promotion gate checklist exists but is incomplete, the ledger
   preserves the checklist's recommended manual commands instead of recording
   promotion decisions.
5. When a complete checklist exists, each gate becomes a report-only promotion
   decision with capability, recommended decision, decision state, promotion
   gate state, evidence state, approval state, approval boundary, decision
   effect, and routing effect.
6. Blocked gates become `defer_promotion` decisions. Ready gates become
   `manual_operator_review_required` decisions.
7. The command writes `docs/capability-promotion-decision-ledger.md` and
   records a `capability_promotion_decision_ledgers` row with source checklist
   id/status, capability count, decision count, deferred-promotion count,
   operator-decision-required count, blocked-promotion count, missing-evidence
   count, approval-required count, boundary count, recommended manual
   commands, report path, and decision items.
8. The static dashboard mirrors the latest ledger under
   `## Capability Promotion Decision Ledger`.
9. The iteration packet includes the command in its verification list and
   reports the latest `capability promotion decision ledger` posture.
10. Status values are `promotion_decision_blocked`,
    `operator_decision_required`, `no_promotion_decisions_needed`, and
    `promotion_gate_checklist_missing`.
11. The ledger currently means report-only promotion-decision visibility. It
    does not create promotion gate checklists, evidence collection plans,
    approval-boundary matrices, proof-gap indexes, readiness reviews, or
    ledgers as a side effect, collect evidence automatically, approve
    capabilities automatically, promote capabilities automatically, generate
    proof artifacts, enable hosted dashboards, start remote workers, schedule
    autonomous work, operate browser or desktop adapters, run CI or deploys,
    enforce budgets, promote trust, retry or replay work, track real spend,
    change routing, change claims, or touch external systems.

## Capability Trust Promotion Audit Lifecycle

1. Run `python3 -m agent_os.cli capability-trust-promotion-audit`.
2. The command reads only the latest persisted
   `capability_promotion_decision_ledgers` row from SQLite.
3. If no promotion decision ledger exists, the command writes a
   `promotion_decision_ledger_missing` audit and recommends
   `capability-promotion-decision-ledger` without creating a ledger itself.
4. When a promotion decision ledger exists but is incomplete, the audit
   preserves the ledger's recommended manual commands instead of reporting
   trust-promotion readiness.
5. When a complete ledger exists, each promotion decision becomes a report-only
   trust-promotion audit item with capability, recommended trust action, trust
   promotion state, source decision, source decision state, evidence state,
   approval state, approval boundary, trust effect, and routing effect.
6. Deferred promotion decisions become `keep_trust_unpromoted` audit items.
   Operator-review promotion decisions become `manual_trust_review_required`
   audit items.
7. The command writes `docs/capability-trust-promotion-audit.md` and records a
   `capability_trust_promotion_audits` row with source ledger id/status,
   capability count, audit count, blocked-trust-promotion count,
   operator-review-required count, deferred-promotion count, missing-evidence
   count, approval-required count, boundary count, recommended manual
   commands, report path, and audit items.
8. The static dashboard mirrors the latest audit under
   `## Capability Trust Promotion Audit`.
9. The iteration packet includes the command in its verification list and
   reports the latest `capability trust promotion audit` posture.
10. Status values are `trust_promotion_blocked`,
    `operator_trust_review_required`, `no_trust_promotion_candidates`, and
    `promotion_decision_ledger_missing`.
11. The audit currently means report-only trust-promotion visibility. It does
    not create promotion decision ledgers, promotion gate checklists, evidence
    collection plans, approval-boundary matrices, proof-gap indexes, readiness
    reviews, or ledgers as a side effect, collect evidence automatically,
    approve capabilities automatically, promote capabilities automatically,
    promote trust automatically, generate proof artifacts, enable hosted
    dashboards, start remote workers, schedule autonomous work, operate browser
    or desktop adapters, run CI or deploys, enforce budgets, retry or replay
    work, track real spend, change routing, change claims, or touch external
    systems.

## Capability Automatic Retry Audit Lifecycle

1. Run `python3 -m agent_os.cli capability-automatic-retry-audit`.
2. The command reads only the latest persisted
   `capability_trust_promotion_audits` row from SQLite.
3. If no trust promotion audit exists, the command writes a
   `trust_promotion_audit_missing` audit and recommends
   `capability-trust-promotion-audit` without creating a trust audit itself.
4. When a trust promotion audit exists but is incomplete, the automatic-retry
   audit preserves the trust audit's recommended manual commands instead of
   reporting retry readiness.
5. When a complete trust promotion audit exists, each trust-promotion audit item
   becomes a report-only automatic-retry audit item with capability,
   recommended retry action, retry state, source trust action, source trust
   state, evidence state, approval state, approval boundary, retry effect, and
   routing effect.
6. Blocked trust-promotion audit items become `keep_retry_disabled` retry audit
   items. Operator-review trust items become `manual_retry_review_required`
   retry audit items.
7. The command writes `docs/capability-automatic-retry-audit.md` and records a
   `capability_automatic_retry_audits` row with source audit id/status,
   capability count, audit count, blocked-retry count,
   operator-review-required count, blocked-trust-promotion count,
   deferred-promotion count, missing-evidence count, approval-required count,
   boundary count, recommended manual commands, report path, and audit items.
8. The static dashboard mirrors the latest audit under
   `## Capability Automatic Retry Audit`.
9. The iteration packet includes the command in its verification list and
   reports the latest `capability automatic retry audit` posture.
10. Status values are `automatic_retry_blocked`,
    `operator_retry_review_required`, `no_automatic_retry_candidates`, and
    `trust_promotion_audit_missing`.
11. The audit currently means report-only retry-readiness visibility. It does
    not create trust promotion audits, promotion decision ledgers, promotion
    gate checklists, evidence collection plans, approval-boundary matrices,
    proof-gap indexes, readiness reviews, or ledgers as a side effect, collect
    evidence automatically, approve capabilities automatically, promote
    capabilities automatically, promote trust automatically, retry or replay
    work automatically, generate proof artifacts, enable hosted dashboards,
    start remote workers, schedule autonomous work, operate browser or desktop
    adapters, run CI or deploys, enforce budgets, track real spend, change
    routing, change claims, or touch external systems.

## Capability Real Cost Tracking Audit Lifecycle

1. Run `python3 -m agent_os.cli capability-real-cost-tracking-audit`.
2. The command reads only the latest persisted
   `capability_automatic_retry_audits` row from SQLite.
3. If no automatic retry audit exists, the command writes an
   `automatic_retry_audit_missing` audit and recommends
   `capability-automatic-retry-audit` without creating an automatic retry audit
   itself.
4. When an automatic retry audit exists but is incomplete, the real-cost audit
   preserves the retry audit's recommended manual commands instead of reporting
   cost-tracking readiness.
5. When a complete automatic retry audit exists, each retry audit item becomes
   a report-only real-cost-tracking audit item with capability, recommended
   cost action, cost tracking state, source retry action, source retry state,
   source trust action, source trust state, evidence state, approval state,
   approval boundary, cost effect, and routing effect.
6. Blocked retry audit items become `keep_cost_tracking_disabled` cost audit
   items. Operator-review retry items become `manual_cost_review_required`
   cost audit items.
7. The command writes `docs/capability-real-cost-tracking-audit.md` and records
   a `capability_real_cost_tracking_audits` row with source audit id/status,
   capability count, audit count, blocked-cost-tracking count,
   operator-review-required count, blocked-retry count,
   blocked-trust-promotion count, deferred-promotion count,
   missing-evidence count, approval-required count, boundary count,
   recommended manual commands, report path, and audit items.
8. The static dashboard mirrors the latest audit under
   `## Capability Real Cost Tracking Audit`.
9. The iteration packet includes the command in its verification list and
   reports the latest `capability real cost tracking audit` posture.
10. Status values are `real_cost_tracking_blocked`,
    `operator_cost_review_required`, `no_real_cost_tracking_candidates`, and
    `automatic_retry_audit_missing`.
11. The audit currently means report-only cost-tracking-readiness visibility.
    It does not create automatic retry audits, trust promotion audits,
    promotion decision ledgers, promotion gate checklists, evidence collection
    plans, approval-boundary matrices, proof-gap indexes, readiness reviews, or
    ledgers as a side effect, collect evidence automatically, approve
    capabilities automatically, promote capabilities automatically, promote
    trust automatically, retry or replay work automatically, track real spend
    automatically, generate proof artifacts, enable hosted dashboards, start
    remote workers, schedule autonomous work, operate browser or desktop
    adapters, run CI or deploys, enforce budgets, change routing, change
    claims, or touch external systems.

## Hosted Dashboard Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli hosted-dashboard-proof-checklist`.
2. The command prefers the latest persisted
   `real_cost_tracking_proof_checklists` row from SQLite. If no proof
   checklist exists, it falls back to the latest legacy
   `capability_real_cost_tracking_audits` row.
3. If neither source exists, the command writes a
   `real_cost_tracking_proof_checklist_missing` checklist and recommends
   `real-cost-tracking-proof-checklist` without creating upstream proof
   checklists or audits itself.
4. When a Real Cost Tracking proof checklist exists but is incomplete, the
   hosted dashboard checklist preserves the proof checklist's recommended
   manual commands instead of reporting dashboard proof readiness.
5. When a complete Real Cost Tracking proof checklist exists, only the
   `real_cost_tracking` proof item becomes a report-only hosted-dashboard
   proof checklist item with proof item, recommended dashboard action,
   dashboard state, Real Cost Tracking proof source action/state, upstream
   proof/action chain fields, Real-Cost-sourced source checklist metadata in
   the report when present, evidence state, approval state, approval boundary,
   dashboard effect, and routing effect.
6. When only a legacy real cost tracking audit exists, the command keeps the
   previous audit-backed fallback and maps only the `hosted_dashboard` audit
   item into the same report-only hosted-dashboard proof surface.
7. Blocked hosted-dashboard source rows become
   `keep_hosted_dashboard_disabled` checklist items. Operator-review rows become
   `manual_hosted_dashboard_review_required` checklist items.
8. The command writes `docs/hosted-dashboard-proof-checklist.md` and records a
   `hosted_dashboard_proof_checklists` row with source kind, source proof
   checklist/audit id/status, capability count, checklist count,
   blocked-dashboard-proof count, operator-review-required count,
   blocked-cost-tracking count, blocked-retry count, blocked-trust-promotion
   count, missing-evidence count, approval-required count, boundary count,
   recommended manual commands, report path, and checklist items.
9. The static dashboard mirrors the latest checklist under
   `## Hosted Dashboard Proof Checklist`.
10. The iteration packet includes the command in its verification list and
   reports the latest `hosted dashboard proof checklist` posture.
11. Status values are `hosted_dashboard_proof_blocked`,
    `operator_hosted_dashboard_review_required`,
    `no_hosted_dashboard_proof_candidate`, and
    `real_cost_tracking_proof_checklist_missing`; legacy fallback may still
    emit `real_cost_tracking_audit_missing`.
12. The checklist currently means report-only hosted-dashboard proof-readiness
    visibility. It does not create real cost tracking audits, automatic retry
    audits, trust promotion audits, promotion decision ledgers, promotion gate
    checklists, evidence collection plans, approval-boundary matrices,
    proof-gap indexes, readiness reviews, or ledgers as a side effect, collect
    evidence automatically, approve capabilities automatically, promote
    capabilities automatically, promote trust automatically, retry or replay
    work automatically, track real spend automatically, generate proof
    artifacts, enable or deploy hosted dashboards, start remote workers,
    schedule autonomous work, operate browser or desktop adapters, run CI or
    deploys, enforce budgets, change routing, change claims, or touch external
    systems.

## Remote Worker Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli remote-worker-proof-checklist`.
2. The command reads only the latest persisted
   `hosted_dashboard_proof_checklists` row from SQLite.
3. If no hosted dashboard proof checklist exists, the command writes a
   `hosted_dashboard_proof_checklist_missing` checklist and recommends
   `hosted-dashboard-proof-checklist` without creating a hosted-dashboard
   checklist itself.
4. When a hosted dashboard proof checklist exists but is incomplete, the remote
   worker checklist preserves the hosted-dashboard checklist's recommended
   manual commands instead of reporting remote-worker proof readiness.
5. When a complete hosted dashboard proof checklist exists, the
   `hosted_dashboard` proof item becomes a report-only `remote_workers`
   proof checklist item with proof item, recommended worker action, worker
   state, source dashboard action/state, Real-Cost-sourced hosted-dashboard
   proof metadata when present, source cost action/state, source retry
   action/state, source trust action/state, evidence state, approval state,
   approval boundary, worker effect, and routing effect.
6. Blocked hosted-dashboard proof rows become `keep_remote_workers_disabled`
   checklist items. Operator-review rows become
   `manual_remote_worker_review_required` checklist items.
7. The command writes `docs/remote-worker-proof-checklist.md` and records a
   `remote_worker_proof_checklists` row with source checklist id/status,
   capability count, checklist count, blocked-worker-proof count,
   operator-review-required count, blocked-dashboard-proof count,
   blocked-cost-tracking count, blocked-retry count,
   blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, and checklist items. The generated report also shows the
   source hosted-dashboard proof checklist's own source kind and source
   checklist/audit ids, plus that source proof checklist's own source metadata
   when available.
8. The static dashboard mirrors the latest checklist under
   `## Remote Worker Proof Checklist`.
9. The iteration packet includes the command in its verification list and
   reports the latest `remote worker proof checklist` posture.
10. Status values are `remote_worker_proof_blocked`,
    `operator_remote_worker_review_required`,
    `no_remote_worker_proof_candidate`, and
    `hosted_dashboard_proof_checklist_missing`.
11. The checklist currently means report-only remote-worker proof-readiness
    visibility. It does not create hosted dashboard proof checklists, real cost
    tracking audits, automatic retry audits, trust promotion audits, promotion
    decision ledgers, promotion gate checklists, evidence collection plans,
    approval-boundary matrices, proof-gap indexes, readiness reviews, or
    ledgers as a side effect, collect evidence automatically, approve
    capabilities automatically, promote capabilities automatically, promote
    trust automatically, retry or replay work automatically, track real spend
    automatically, generate proof artifacts, enable or deploy hosted
    dashboards, start remote workers, claim remote work, schedule autonomous
    work, operate browser or desktop adapters, run CI or deploys, enforce
    budgets, change routing, change claims, or touch external systems.

## Autonomous Scheduling Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli autonomous-scheduling-proof-checklist`.
2. The command reads only the latest persisted
   `remote_worker_proof_checklists` row from SQLite.
3. If no remote worker proof checklist exists, the command writes a
   `remote_worker_proof_checklist_missing` checklist and recommends
   `remote-worker-proof-checklist` without creating a remote-worker checklist
   itself.
4. When a remote worker proof checklist exists but is incomplete, the
   autonomous scheduling checklist preserves the remote-worker checklist's
   recommended manual commands instead of reporting scheduling proof
   readiness.
5. When a complete remote worker proof checklist exists, the `remote_workers`
   proof item becomes a report-only `autonomous_scheduling` proof checklist
   item with proof item, recommended scheduling action, scheduling state,
   source worker action/state, source dashboard action/state,
   Real-Cost-sourced remote-worker proof metadata when present, source cost
   action/state, source retry action/state, source trust action/state,
   evidence state, approval state, approval boundary, scheduling effect, and
   routing effect.
6. Blocked remote-worker proof rows become
   `keep_autonomous_scheduling_disabled` checklist items. Operator-review rows
   become `manual_autonomous_scheduling_review_required` checklist items.
7. The command writes `docs/autonomous-scheduling-proof-checklist.md` and
   records an `autonomous_scheduling_proof_checklists` row with source
   checklist id/status, capability count, checklist count,
   blocked-scheduling-proof count, operator-review-required count,
   blocked-worker-proof count, blocked-dashboard-proof count,
   blocked-cost-tracking count, blocked-retry count,
   blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, and checklist items. The generated report also shows the
   source remote-worker proof checklist's own source checklist id/status.
8. The static dashboard mirrors the latest checklist under
   `## Autonomous Scheduling Proof Checklist`.
9. The iteration packet includes the command in its verification list and
   reports the latest `autonomous scheduling proof checklist` posture.
10. Status values are `autonomous_scheduling_proof_blocked`,
    `operator_autonomous_scheduling_review_required`,
    `no_autonomous_scheduling_proof_candidate`, and
    `remote_worker_proof_checklist_missing`.
11. The checklist currently means report-only autonomous-scheduling
    proof-readiness visibility. It does not create remote worker proof
    checklists, hosted dashboard proof checklists, real cost tracking audits,
    automatic retry audits, trust promotion audits, promotion decision ledgers,
    promotion gate checklists, evidence collection plans, approval-boundary
    matrices, proof-gap indexes, readiness reviews, or ledgers as a side
    effect, collect evidence automatically, approve capabilities
    automatically, promote capabilities automatically, promote trust
    automatically, retry or replay work automatically, track real spend
    automatically, generate proof artifacts, enable or deploy hosted
    dashboards, start remote workers, claim remote work, schedule autonomous
    work, operate browser or desktop adapters, run CI or deploys, enforce
    budgets, change routing, change claims, or touch external systems.

## Browser Desktop Adapter Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli browser-desktop-adapter-proof-checklist`.
2. The command reads only the latest persisted
   `autonomous_scheduling_proof_checklists` row from SQLite.
3. If no autonomous scheduling proof checklist exists, the command writes an
   `autonomous_scheduling_proof_checklist_missing` checklist and recommends
   `autonomous-scheduling-proof-checklist` without creating an
   autonomous-scheduling checklist itself.
4. When an autonomous scheduling proof checklist exists but is incomplete, the
   browser/desktop adapter checklist preserves the autonomous-scheduling
   checklist's recommended manual commands instead of reporting adapter proof
   readiness.
5. When a complete autonomous scheduling proof checklist exists, the
   `autonomous_scheduling` proof item becomes a report-only
   `browser_desktop_adapters` proof checklist item with proof item,
   recommended adapter action, adapter state, source scheduling action/state,
   source worker action/state, source dashboard action/state,
   Real-Cost-sourced autonomous-scheduling proof metadata when present, source
   cost action/state, source retry action/state, source trust action/state,
   evidence state, approval state, approval boundary, adapter effect, and
   routing effect.
6. Blocked autonomous-scheduling proof rows become
   `keep_browser_desktop_adapters_disabled` checklist items. Operator-review
   rows become `manual_browser_desktop_adapter_review_required` checklist
   items.
7. The command writes `docs/browser-desktop-adapter-proof-checklist.md` and
   records a `browser_desktop_adapter_proof_checklists` row with source
   checklist id/status, capability count, checklist count,
   blocked-adapter-proof count, operator-review-required count,
   blocked-scheduling-proof count, blocked-worker-proof count,
   blocked-dashboard-proof count, blocked-cost-tracking count,
   blocked-retry count, blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, and checklist items. The generated report also shows the
   source autonomous-scheduling proof checklist's own source checklist
   id/status.
8. The static dashboard mirrors the latest checklist under
   `## Browser Desktop Adapter Proof Checklist`.
9. The iteration packet includes the command in its verification list and
   reports the latest `browser desktop adapter proof checklist` posture.
10. Status values are `browser_desktop_adapter_proof_blocked`,
    `operator_browser_desktop_adapter_review_required`,
    `no_browser_desktop_adapter_proof_candidate`, and
    `autonomous_scheduling_proof_checklist_missing`.
11. The checklist currently means report-only browser/desktop adapter
    proof-readiness visibility. It does not create autonomous scheduling proof
    checklists, remote worker proof checklists, hosted dashboard proof
    checklists, real cost tracking audits, automatic retry audits, trust
    promotion audits, promotion decision ledgers, promotion gate checklists,
    evidence collection plans, approval-boundary matrices, proof-gap indexes,
    readiness reviews, or ledgers as a side effect, collect evidence
    automatically, approve capabilities automatically, promote capabilities
    automatically, promote trust automatically, retry or replay work
    automatically, track real spend automatically, generate proof artifacts,
    enable or deploy hosted dashboards, start remote workers, claim remote
    work, schedule autonomous work, operate browser or desktop adapters, run
    CI or deploys, enforce budgets, change routing, change claims, or touch
    external systems.

## CI Deploy Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli ci-deploy-proof-checklist`.
2. The command reads recent persisted
   `browser_desktop_adapter_proof_checklists` rows from SQLite and prefers the
   latest Real-Cost-sourced Browser Desktop Adapter proof checklist when one
   exists.
3. If no browser/desktop adapter proof checklist exists, the command writes a
   `browser_desktop_adapter_proof_checklist_missing` checklist and recommends
   `browser-desktop-adapter-proof-checklist` without creating an adapter
   checklist itself.
4. When a browser/desktop adapter proof checklist exists but is incomplete, the
   CI Deploy checklist preserves the adapter checklist's recommended manual
   commands instead of reporting CI Deploy proof readiness.
5. When a complete browser/desktop adapter proof checklist exists, the
   `browser_desktop_adapters` proof item becomes a report-only
   `ci_deploy_proof` checklist item with proof item, recommended CI Deploy
   action, CI Deploy state, source adapter action/state, source scheduling
   action/state, source worker action/state, source dashboard action/state,
   upstream Real-Cost-sourced proof/action chain fields when present, the
   browser/desktop adapter source proof's own source metadata in the generated
   report when available, source cost action/state, source retry action/state,
   source trust action/state, evidence state, approval state, approval
   boundary, CI Deploy effect, and routing effect.
6. Blocked browser/desktop adapter proof rows become
   `keep_ci_deploy_disabled` checklist items. Operator-review rows become
   `manual_ci_deploy_review_required` checklist items.
7. The command writes `docs/ci-deploy-proof-checklist.md` and records a
   `ci_deploy_proof_checklists` row with source checklist id/status,
   capability count, checklist count, blocked-CI-Deploy-proof count,
   operator-review-required count, blocked-adapter-proof count,
   blocked-scheduling-proof count, blocked-worker-proof count,
   blocked-dashboard-proof count, blocked-cost-tracking count,
   blocked-retry count, blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, checklist items, and the source browser/desktop adapter
   checklist's own source checklist id/status.
8. The static dashboard mirrors the latest checklist under
   `## CI Deploy Proof Checklist`.
9. The iteration packet includes the command in its verification list and
   reports the latest `ci deploy proof checklist` posture.
10. Status values are `ci_deploy_proof_blocked`,
    `operator_ci_deploy_review_required`, `no_ci_deploy_proof_candidate`, and
    `browser_desktop_adapter_proof_checklist_missing`.
11. The checklist currently means report-only CI Deploy proof-readiness
    visibility. It does not create browser/desktop adapter proof checklists,
    autonomous scheduling proof checklists, remote worker proof checklists,
    hosted dashboard proof checklists, real cost tracking audits, automatic
    retry audits, trust promotion audits, promotion decision ledgers,
    promotion gate checklists, evidence collection plans, approval-boundary
    matrices, proof-gap indexes, readiness reviews, or ledgers as a side
    effect, collect evidence automatically, approve capabilities
    automatically, promote capabilities automatically, promote trust
    automatically, retry or replay work automatically, track real spend
    automatically, generate proof artifacts, enable or deploy hosted
    dashboards, start remote workers, claim remote work, schedule autonomous
    work, operate browser or desktop adapters, run CI or deploys, enforce
    budgets, change routing, change claims, or touch external systems.

## Budget Enforcement Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli budget-enforcement-proof-checklist`.
2. The command reads recent persisted `ci_deploy_proof_checklists` rows from
   SQLite and prefers the latest Real-Cost-sourced CI Deploy proof checklist
   when one exists.
3. If no CI Deploy proof checklist exists, the command writes a
   `ci_deploy_proof_checklist_missing` checklist and recommends
   `ci-deploy-proof-checklist` without creating a CI Deploy checklist itself.
4. When a CI Deploy proof checklist exists but is incomplete, the Budget
   Enforcement checklist preserves the CI Deploy checklist's recommended
   manual commands instead of reporting budget-enforcement proof readiness.
5. When a complete CI Deploy proof checklist exists, the `ci_deploy_proof`
   item becomes a report-only `budget_enforcement` checklist item with proof
   item, recommended budget action, budget enforcement state, source CI Deploy
   action/state, source adapter action/state, source scheduling action/state,
   source worker action/state, source dashboard action/state, upstream
   Real-Cost-sourced proof/action chain fields when present, source cost
   action/state, source retry action/state, source trust action/state,
   evidence state, approval state, approval boundary, budget enforcement
   effect, and routing effect.
6. Blocked CI Deploy proof rows become `keep_budget_enforcement_disabled`
   checklist items. Operator-review rows become
   `manual_budget_enforcement_review_required` checklist items.
7. The command writes `docs/budget-enforcement-proof-checklist.md` and records
   a `budget_enforcement_proof_checklists` row with source checklist id/status,
   capability count, checklist count, blocked-budget-enforcement-proof count,
   operator-review-required count, blocked-CI-Deploy-proof count,
   blocked-adapter-proof count, blocked-scheduling-proof count,
   blocked-worker-proof count, blocked-dashboard-proof count,
   blocked-cost-tracking count, blocked-retry count,
   blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, checklist items, the source CI Deploy checklist's own source
   checklist id/status, and the CI Deploy source proof's own source metadata
   when available.
8. The static dashboard mirrors the latest checklist under
   `## Budget Enforcement Proof Checklist`.
9. The iteration packet includes the command in its verification list and
   reports the latest `budget enforcement proof checklist` posture.
10. Status values are `budget_enforcement_proof_blocked`,
    `operator_budget_enforcement_review_required`,
    `no_budget_enforcement_proof_candidate`, and
    `ci_deploy_proof_checklist_missing`.
11. The checklist currently means report-only budget-enforcement
    proof-readiness visibility. It does not create CI Deploy proof checklists,
    browser/desktop adapter proof checklists, autonomous scheduling proof
    checklists, remote worker proof checklists, hosted dashboard proof
    checklists, real cost tracking audits, automatic retry audits, trust
    promotion audits, promotion decision ledgers, promotion gate checklists,
    evidence collection plans, approval-boundary matrices, proof-gap indexes,
    readiness reviews, or ledgers as a side effect, collect evidence
    automatically, approve capabilities automatically, promote capabilities
    automatically, promote trust automatically, retry or replay work
    automatically, track real spend automatically, generate proof artifacts,
    enable or deploy hosted dashboards, start remote workers, claim remote
    work, schedule autonomous work, operate browser or desktop adapters, run
    CI or deploys, enforce budgets, change routing, change claims, or touch
    external systems.

## Trust Promotion Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli trust-promotion-proof-checklist`.
2. The command reads recent persisted `budget_enforcement_proof_checklists`
   rows from SQLite and prefers the latest row backed by a Real-Cost-sourced
   CI Deploy -> Browser/Desktop Adapter -> Autonomous Scheduling -> Remote
   Worker -> Hosted Dashboard -> Real Cost Tracking source chain when one
   exists.
3. If no Budget Enforcement proof checklist exists, the command writes a
   `budget_enforcement_proof_checklist_missing` checklist and recommends
   `budget-enforcement-proof-checklist` without creating a Budget Enforcement
   checklist itself.
4. When a Budget Enforcement proof checklist exists but is incomplete, the
   Trust Promotion checklist preserves the Budget Enforcement checklist's
   recommended manual commands instead of reporting trust-promotion proof
   readiness.
5. When a complete Budget Enforcement proof checklist exists, the
   `budget_enforcement` item becomes a report-only `trust_promotion` checklist
   item with proof item, recommended trust action, trust promotion state,
   source budget action/state, source CI Deploy action/state, source adapter
   action/state, source scheduling action/state, source worker action/state,
   source dashboard action/state, optional upstream Real Cost Tracking proof,
   Automatic Retry proof, and Trust proof action/state fields when present,
   source cost action/state, source retry action/state, source trust
   action/state, evidence state, approval state, approval boundary, trust
   promotion effect, and routing effect.
6. Blocked Budget Enforcement proof rows become `keep_trust_unpromoted`
   checklist items. Operator-review rows become
   `manual_trust_promotion_review_required` checklist items.
7. The command writes `docs/trust-promotion-proof-checklist.md` and records a
   `trust_promotion_proof_checklists` row with source checklist id/status,
   capability count, checklist count, blocked-trust-promotion-proof count,
   operator-review-required count, blocked-budget-enforcement-proof count,
   blocked-CI-Deploy-proof count, blocked-adapter-proof count,
   blocked-scheduling-proof count, blocked-worker-proof count,
   blocked-dashboard-proof count, blocked-cost-tracking count,
   blocked-retry count, blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, checklist items, and the selected Budget Enforcement proof
   checklist's nested source proof id/status chain when available.
8. The static dashboard mirrors the latest checklist under
   `## Trust Promotion Proof Checklist`, including first-hop source status.
9. The iteration packet includes the command in its verification list and
   reports the latest `trust promotion proof checklist` posture.
10. Status values are `trust_promotion_proof_blocked`,
    `operator_trust_promotion_review_required`,
    `no_trust_promotion_proof_candidate`, and
    `budget_enforcement_proof_checklist_missing`.
11. The checklist currently means report-only trust-promotion proof-readiness
    visibility from the latest Real-Cost-sourced Budget Enforcement proof
    checklist when one exists. It does not create Budget Enforcement proof
    checklists, CI
    Deploy proof checklists, browser/desktop adapter proof checklists,
    autonomous scheduling proof checklists, remote worker proof checklists,
    hosted dashboard proof checklists, real cost tracking audits, automatic
    retry audits, trust promotion audits, promotion decision ledgers,
    promotion gate checklists, evidence collection plans, approval-boundary
    matrices, proof-gap indexes, readiness reviews, or ledgers as a side
    effect, collect evidence automatically, approve capabilities
    automatically, promote capabilities automatically, promote trust
    automatically, retry or replay work automatically, track real spend
    automatically, generate proof artifacts, enable or deploy hosted
    dashboards, start remote workers, claim remote work, schedule autonomous
    work, operate browser or desktop adapters, run CI or deploys, enforce
    budgets, change routing, change claims, or touch external systems.

## Automatic Retry Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli automatic-retry-proof-checklist`.
2. The command reads only the latest persisted
   `trust_promotion_proof_checklists` row from SQLite.
3. If no Trust Promotion proof checklist exists, the command writes a
   `trust_promotion_proof_checklist_missing` checklist and recommends
   `trust-promotion-proof-checklist` without creating a Trust Promotion
   checklist itself.
4. When a Trust Promotion proof checklist exists but is incomplete, the
   Automatic Retry checklist preserves the Trust Promotion checklist's
   recommended manual commands instead of reporting automatic-retry proof
   readiness.
5. When a complete Trust Promotion proof checklist exists, the
   `trust_promotion` item becomes a report-only `automatic_retry` checklist
   item with proof item, recommended retry action, automatic retry state,
   source trust proof action/state, source budget action/state, source CI
   Deploy action/state, source adapter action/state, source scheduling
   action/state, source worker action/state, source dashboard action/state,
   optional source Real Cost Tracking proof action/state and Automatic Retry
   proof action/state when present,
   source cost action/state, source retry action/state, source trust
   action/state, evidence state, approval state, approval boundary, automatic
   retry effect, and routing effect.
6. Blocked Trust Promotion proof rows become `keep_retry_disabled` checklist
   items. Operator-review rows become `manual_retry_review_required` checklist
   items.
7. The command writes `docs/automatic-retry-proof-checklist.md` and records an
   `automatic_retry_proof_checklists` row with source checklist id/status,
   capability count, checklist count, blocked-automatic-retry-proof count,
   operator-review-required count, blocked-trust-promotion-proof count,
   blocked-budget-enforcement-proof count, blocked-CI-Deploy-proof count,
   blocked-adapter-proof count, blocked-scheduling-proof count,
   blocked-worker-proof count, blocked-dashboard-proof count,
   blocked-cost-tracking count, blocked-retry count,
   blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, and checklist items.
8. The generated report includes the source Trust Promotion checklist's own
   source checklist id/status when present.
9. The static dashboard mirrors the latest checklist under
   `## Automatic Retry Proof Checklist`.
10. The iteration packet includes the command in its verification list and
   reports the latest `automatic retry proof checklist` posture.
11. Status values are `automatic_retry_proof_blocked`,
    `operator_automatic_retry_review_required`,
    `no_automatic_retry_proof_candidate`, and
    `trust_promotion_proof_checklist_missing`.
12. The checklist currently means report-only automatic-retry proof-readiness
    visibility. It does not create Trust Promotion proof checklists, Budget
    Enforcement proof checklists, CI Deploy proof checklists, browser/desktop
    adapter proof checklists, autonomous scheduling proof checklists, remote
    worker proof checklists, hosted dashboard proof checklists, real cost
    tracking audits, automatic retry audits, trust promotion audits, promotion
    decision ledgers, promotion gate checklists, evidence collection plans,
    approval-boundary matrices, proof-gap indexes, readiness reviews, or
    ledgers as a side effect, collect evidence automatically, approve
    capabilities automatically, promote capabilities automatically, promote
    trust automatically, retry or replay work automatically, track real spend
    automatically, generate proof artifacts, enable or deploy hosted
    dashboards, start remote workers, claim remote work, schedule autonomous
    work, operate browser or desktop adapters, run CI or deploys, enforce
    budgets, change routing, change claims, or touch external systems.

## Real Cost Tracking Proof Checklist Lifecycle

1. Run `python3 -m agent_os.cli real-cost-tracking-proof-checklist`.
2. The command reads only the latest persisted
   `automatic_retry_proof_checklists` row from SQLite.
3. If no Automatic Retry proof checklist exists, the command writes an
   `automatic_retry_proof_checklist_missing` checklist and recommends
   `automatic-retry-proof-checklist` without creating an Automatic Retry
   checklist itself.
4. When an Automatic Retry proof checklist exists but is incomplete, the Real
   Cost Tracking checklist preserves the Automatic Retry checklist's
   recommended manual commands instead of reporting real-cost-tracking proof
   readiness.
5. When a complete Automatic Retry proof checklist exists, the
   `automatic_retry` item becomes a report-only `real_cost_tracking`
   checklist item with proof item, recommended cost action, real cost tracking
   state, source automatic retry proof action/state, source trust proof
   action/state, source budget action/state, source CI Deploy action/state,
   source adapter action/state, source scheduling action/state, source worker
   action/state, source dashboard action/state, upstream Real-Cost-sourced
   proof/action chain fields when present, source cost action/state, source
   retry action/state, source trust action/state, evidence state, approval
   state, approval boundary, real cost tracking effect, and routing effect.
6. Blocked Automatic Retry proof rows become `keep_cost_tracking_disabled`
   checklist items. Operator-review rows become
   `manual_real_cost_tracking_review_required` checklist items.
7. The command writes `docs/real-cost-tracking-proof-checklist.md` and records
   a `real_cost_tracking_proof_checklists` row with source checklist id/status,
   capability count, checklist count, blocked-real-cost-tracking-proof count,
   operator-review-required count, blocked-automatic-retry-proof count,
   blocked-trust-promotion-proof count, blocked-budget-enforcement-proof
   count, blocked-CI-Deploy-proof count, blocked-adapter-proof count,
   blocked-scheduling-proof count, blocked-worker-proof count,
   blocked-dashboard-proof count, blocked-cost-tracking count,
   blocked-retry count, blocked-trust-promotion count, missing-evidence count,
   approval-required count, boundary count, recommended manual commands,
   report path, and checklist items.
8. The static dashboard mirrors the latest checklist and source status under
   `## Real Cost Tracking Proof Checklist`.
9. The iteration packet includes the command in its verification list and
   reports the latest `real cost tracking proof checklist` posture.
10. Status values are `real_cost_tracking_proof_blocked`,
    `operator_real_cost_tracking_review_required`,
    `no_real_cost_tracking_proof_candidate`, and
    `automatic_retry_proof_checklist_missing`.
11. The checklist currently means report-only real-cost-tracking
    proof-readiness visibility. It does not create Automatic Retry proof
    checklists, Trust Promotion proof checklists, Budget Enforcement proof
    checklists, CI Deploy proof checklists, browser/desktop adapter proof
    checklists, autonomous scheduling proof checklists, remote worker proof
    checklists, hosted dashboard proof checklists, real cost tracking audits,
    automatic retry audits, trust promotion audits, promotion decision ledgers,
    promotion gate checklists, evidence collection plans, approval-boundary
    matrices, proof-gap indexes, readiness reviews, or ledgers as a side
    effect, collect evidence automatically, approve capabilities
    automatically, promote capabilities automatically, promote trust
    automatically, retry or replay work automatically, track real spend
    automatically, generate proof artifacts, enable or deploy hosted
    dashboards, start remote workers, claim remote work, schedule autonomous
    work, operate browser or desktop adapters, run CI or deploys, enforce
    budgets, change routing, change claims, or touch external systems.

## Eval Candidate Lifecycle

1. A verifier or workflow gap is discovered, such as failed deterministic
   verification or a stuck active task.
2. The runtime writes `evals/candidates/<source>-eval-candidate.json` with the
   source incident, gap type, failed checks, reason, and suggested eval name.
3. SQLite records the candidate in `eval_candidates` with status `proposed`.
4. `python3 -m agent_os.cli eval-candidates` lists current proposed candidates.
5. The static dashboard mirrors candidates under `## Eval Candidates`.
6. Candidates are report-only until a later slice turns proposals into concrete
   executable eval implementations.

## Playbook Promotion Lifecycle

1. Run `python3 -m agent_os.cli playbooks`.
2. The command reads successful `eval_results` rows from SQLite.
3. Eval names with at least two passing runs become active playbook candidates.
4. The command writes `playbooks/<slug>.md` and updates the SQLite `playbooks`
   table idempotently.
5. The command writes `docs/playbooks.md` as a compact playbook index.
6. The static dashboard mirrors active playbooks under `## Playbooks`.
7. Playbooks are operating guidance only; they are not automatic executors.

## Iteration Packet Lifecycle

1. Run `python3 -m agent_os.cli iterate`.
2. Read unchecked items from `tasks.md`.
3. Skip checked items and blocked/deferred queues.
4. Select the first actionable item by section order: `now`, `next`,
   `improve`, then `recurring`.
5. Within the selected section, prefer highest `score`; when scores tie,
   prefer lower `complexity`; when both tie, preserve queue order.
6. Queue item metadata uses an HTML comment suffix:
   `<!-- score=10 complexity=2 -->`.
7. Write `docs/next-iteration.md` with objective, Definition of Done,
   verification commands, guardrails, current posture, and a resume prompt.
8. Persist the packet in SQLite `iteration_packets` with status `planned` plus
   selection policy, reason, selected score, and selected complexity.
9. Regenerate the dashboard so `## Iteration Loop` and
   `## Simplicity Guardrail` point at the packet.
10. A future implementation pass uses the packet as its scoped work brief.

## Task Statuses

- `pending`
- `waiting_approval`
- `claimed`
- `running`
- `verifying`
- `completed`
- `blocked`
- `failed`

## First Supported Task Types

- `write_goal_artifact`: write a human-readable artifact for the accepted goal.
- `record_learning`: distill one learning from the run into memory.
