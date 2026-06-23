# Bootstrap Knowledge

The first milestone should prove a complete loop rather than broad domain
coverage.


## Learning run_ef049fa8bc1b

- Learning: Run run_ef049fa8bc1b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_442800b11c88

- Learning: Run run_442800b11c88 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning: Static Dashboard

- Operational visibility can start as generated markdown backed by SQLite and
  run artifacts before a hosted dashboard exists.
- The dashboard should stay narrow until incidents, approvals, and stuck-task
  detection create real state worth displaying.

## Learning: Failed-Verification Incidents

- Failed verifier paths need a first-class incident row, not only a failed task
  status, so operators can inspect failure evidence without replaying a run.
- Incident visibility remains static/file-backed until a hosted dashboard is
  justified by more live control-plane state.

## Learning: Stuck-Task Sweeps

- Stale active tasks should be blocked with evidence rather than retried,
  requeued, or unlocked automatically.
- Task-level `run_id` makes stuck-task incidents easier to attribute than
  inferring run identity from a goal after the fact.

## Learning: Approval Gates

- Approval should be enforced at the dispatch boundary (`claim_next_task`) after
  skill and dependency checks, so every worker path shares the same policy rail.
- Static policy snapshots with `policy_name`, `policy_version`, risk level, and
  reason are enough for the local baseline; configurable policy and budgets can
  wait until more task types exist.
- Runs waiting on an operator should report `waiting_approval`, not `failed`.

## Learning: Iteration Packets

- Continuing the north-star goal needs a deterministic packet generator, not a
  background autonomous executor.
- `iterate` should select from live momentum queues, write a scoped
  `docs/next-iteration.md` packet, and persist the selection before the next
  implementation pass begins.
- The packet makes the next slice resumable by carrying objective, Definition
  of Done, verification commands, current posture, and explicit non-claims.

## Learning: Incident Resolution

- Incidents should close through an explicit operator action that records
  `resolved_by`, `resolved_at`, a resolution note, and a companion JSON
  evidence file.
- Resolution should add to the audit trail instead of modifying or replacing
  the original failed-verification or stuck-task evidence.

## Learning: Queue Health

- Repeated blocked or failed tasks should first become a visible hotspot report,
  not an automatic retry loop.
- Grouping by project, task type, and status gives the operator a useful next
  question: which kind of work is repeatedly failing or stuck?

## Learning: Playbook Promotion

- Repeated passing eval rows can be turned into reusable playbooks without
  making the system execute them automatically.
- The first promoted playbook is `playbooks/first-milestone-closed-loop.md`,
  sourced from `first_milestone_closed_loop` eval results and indexed in
  `docs/playbooks.md`.

## Learning: Eval Candidates

- Verifier and workflow gaps should leave proposed eval cases at discovery
  time instead of relying on a later human memory sweep.
- The first gap sources are failed verification incidents and stuck-task
  incidents; both write `evals/candidates/<source>-eval-candidate.json` and a
  SQLite `eval_candidates` row.

## Learning: Simplicity Guardrail

- Equal-score choices should resolve with the smallest local change before any
  new orchestration surface is introduced.
- `iterate` uses optional `<!-- score=N complexity=N -->` queue metadata and
  stores the selected score, complexity, and reason in the packet and SQLite.

## Learning: Handoff Reviews

- Blocked-task and stale-handoff review should begin as report-only
  continuity evidence, not an automatic repair loop.
- The current iteration packet focus is the anchor for detecting stale project
  handoff files.

## Learning: Eval After Change

- Running the eval suite after each harness behavior change should leave a
  dedicated check record tied to the change summary and touched files.
- The first implementation keeps this manual and report-only; no background
  watcher, scheduler, CI gate, or deploy gate is implied.

## Learning: Stable Learning Distillation

- Repeated run learnings are episodic evidence until a deterministic local
  threshold promotes them into root `knowledge.md`.
- The first distillation promoted one stable pattern from 24 source learning
  rows after normalizing volatile `run_<id>` values.
- Distillation should stay report-only until a later policy slice defines how
  stable knowledge may affect prompts, skills, playbooks, or task routing.

## Learning: Budget And Trust Posture

- Budget and trust labels should first be visible as a report-only posture
  snapshot over local task metadata, not as dispatch policy.
- The first posture report tracks task count, risk-level counts, and explicit
  `not_tracked` budget/trust states without adding budget or trust columns to
  task dispatch.
- Dashboard generation should read the latest posture row; it should not create
  a new posture report as a rendering side effect.

## Learning: Dispatch Posture History

- Dispatch posture history should read prior report-only posture snapshots
  rather than querying or mutating live dispatch state.
- The first useful history summary is compact: snapshot count, latest task
  count, task-count delta, latest risk counts, and observed budget/trust
  states.
- Dashboard generation should read the latest history summary row; it should
  not generate a new history summary as a rendering side effect.

## Learning: Dispatch Posture Staleness

- Dispatch posture staleness should read prior posture report timestamps from
  SQLite rather than markdown file mtimes or live dispatch state.
- The first review records snapshot count, stale-snapshot count, latest
  snapshot age, threshold, latest task count, and latest risk counts.
- Dashboard generation should read the latest staleness review row; it should
  not create a new review as a rendering side effect.

## Learning: Dispatch Posture Refresh Recommendation

- Dispatch posture refresh recommendations should read the latest staleness
  review row rather than recalculating staleness or generating posture reports.
- The first recommendation records source review id/status, snapshot counts,
  latest snapshot age, threshold, manual command recommendations, approval
  boundary, and deferred-capability context.
- Dashboard generation should read the latest refresh recommendation row; it
  should not run recommended commands or create recommendation inputs as a
  rendering side effect.

## Learning: Capability Expansion Ledger

- Capability expansion should begin as an explicit inventory of deferred
  surfaces, not as a hidden set of roadmap assumptions.
- The first ledger records capability state, required evidence, next proof,
  approval boundary, and routing effect for hosted dashboard, remote workers,
  autonomous scheduling, browser/desktop adapters, CI/deploy proof, budget
  enforcement, trust promotion, automatic retries, and real cost tracking.
- Dashboard generation should read the latest ledger row; it should not enable
  capabilities or create readiness evidence as a rendering side effect.

## Learning: Capability Readiness Review

- Capability readiness review should read the latest persisted expansion
  ledger and report missing evidence before any deferred surface can be treated
  as ready.
- The first review reports 9 autonomy surfaces as `not_ready` with missing
  evidence paths and preserves the explicit operator approval boundary.
- Dashboard generation should read the latest review row; it should not create
  ledgers, activate capabilities, route tasks differently, schedule refreshes,
  or generate proof automatically.

## Learning: Capability Proof Gap Index

- Capability proof gap indexing should read the latest persisted readiness
  review and preserve each missing evidence gap as explicit proof planning.
- The first index keeps proof generation manual by recording next proof labels,
  required evidence, approval boundary, and routing effect without creating
  evidence artifacts.
- Dashboard generation should read the latest index row; it should not create
  readiness reviews, create ledgers, activate capabilities, route tasks
  differently, schedule work, or generate proof automatically.

## Learning: Capability Approval Boundary Matrix

- Capability approval-boundary mapping should read the latest persisted proof
  gap index and preserve each blocked capability as explicit operator approval
  planning.
- The first matrix records one explicit operator approval boundary across 9
  blocked autonomy surfaces and keeps every decision state blocked until proof
  evidence and operator approval exist.
- Dashboard generation should read the latest matrix row; it should not create
  proof-gap indexes, readiness reviews, ledgers, approvals, proof artifacts,
  routing changes, or scheduled work.

## Learning: Capability Evidence Collection Plan

- Capability evidence collection planning should read the latest persisted
  approval-boundary matrix and preserve each blocked capability as a manual
  evidence item.
- The first evidence plan records 9 manual evidence items with collection mode
  `manual_operator_supplied`, evidence state `missing`, and the explicit
  operator approval boundary preserved from the matrix.
- Dashboard generation should read the latest plan row; it should not create
  approval-boundary matrices, proof-gap indexes, readiness reviews, ledgers,
  approvals, proof artifacts, evidence files, routing changes, or scheduled
  work.

## Learning: Capability Promotion Gate Checklist

- Capability promotion gate checklists should read the latest persisted
  evidence collection plan and preserve each missing-evidence item as a blocked
  promotion gate.
- The first promotion checklist records 9 gates, all blocked until manual
  evidence and explicit operator approval exist.
- Dashboard generation should read the latest checklist row; it should not
  create evidence plans, approval-boundary matrices, proof-gap indexes,
  readiness reviews, ledgers, approvals, proof artifacts, evidence files,
  routing changes, trust-promotion changes, or scheduled work.

## Learning: Capability Promotion Decision Ledger

- Capability promotion decision ledgers should read the latest persisted gate
  checklist and preserve blocked gates as `defer_promotion` decisions.
- The first promotion decision ledger records 9 decisions, all deferred until
  manual evidence and explicit operator approval exist.
- Dashboard generation should read the latest decision ledger row; it should
  not create gate checklists, evidence plans, approval-boundary matrices,
  proof-gap indexes, readiness reviews, ledgers, approvals, proof artifacts,
  evidence files, routing changes, trust-promotion changes, or scheduled work.

## Learning run_85aba7975e44

- Learning: Run run_85aba7975e44 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e00b0c8f8421

- Learning: Run run_e00b0c8f8421 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e641748ed7b5

- Learning: Run run_e641748ed7b5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_19c337ce39cd

- Learning: Run run_19c337ce39cd showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e641748ed7b5

- Learning: Run run_e641748ed7b5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_29f35bcd3c4a

- Learning: Run run_29f35bcd3c4a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5850098a3daf

- Learning: Run run_5850098a3daf showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_bdee61e695bb

- Learning: Run run_bdee61e695bb showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5c2e1d7e727b

- Learning: Run run_5c2e1d7e727b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_395eef2e002e

- Learning: Run run_395eef2e002e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9a7518e69a09

- Learning: Run run_9a7518e69a09 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c43d94c11c75

- Learning: Run run_c43d94c11c75 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_24c24ce0765e

- Learning: Run run_24c24ce0765e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_42129a67e1fe

- Learning: Run run_42129a67e1fe showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5953ddebb94f

- Learning: Run run_5953ddebb94f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_3f0260c058b7

- Learning: Run run_3f0260c058b7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_4ca70d56e922

- Learning: Run run_4ca70d56e922 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_b3345106e3e7

- Learning: Run run_b3345106e3e7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e9eb60b88b08

- Learning: Run run_e9eb60b88b08 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_aff094d41613

- Learning: Run run_aff094d41613 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6bba00951a85

- Learning: Run run_6bba00951a85 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d1c5f8393518

- Learning: Run run_d1c5f8393518 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ff65446deb79

- Learning: Run run_ff65446deb79 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_83cd8fbd7ff1

- Learning: Run run_83cd8fbd7ff1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_eb8833b57c9f

- Learning: Run run_eb8833b57c9f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_54bba2d2ff45

- Learning: Run run_54bba2d2ff45 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e954c471a119

- Learning: Run run_e954c471a119 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_4ac46899f8fe

- Learning: Run run_4ac46899f8fe showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5302f455721e

- Learning: Run run_5302f455721e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_46fd5c740bda

- Learning: Run run_46fd5c740bda showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_939ff75bc75d

- Learning: Run run_939ff75bc75d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a6db2dd016ef

- Learning: Run run_a6db2dd016ef showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_af1eca4e0a7c

- Learning: Run run_af1eca4e0a7c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6ab6f6bfd1ce

- Learning: Run run_6ab6f6bfd1ce showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1a7fa83c51f6

- Learning: Run run_1a7fa83c51f6 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_b44c3f315df3

- Learning: Run run_b44c3f315df3 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_db22e31baead

- Learning: Run run_db22e31baead showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0271914a888e

- Learning: Run run_0271914a888e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_3e1257073292

- Learning: Run run_3e1257073292 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_85f5d2bd4875

- Learning: Run run_85f5d2bd4875 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_420e5ea05146

- Learning: Run run_420e5ea05146 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9b2947223b0b

- Learning: Run run_9b2947223b0b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ddda4cc4a791

- Learning: Run run_ddda4cc4a791 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_73c6e141c58c

- Learning: Run run_73c6e141c58c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c481a9e1a499

- Learning: Run run_c481a9e1a499 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2a6739fd5ea7

- Learning: Run run_2a6739fd5ea7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_8409c967c832

- Learning: Run run_8409c967c832 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_f269a5796ca5

- Learning: Run run_f269a5796ca5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d2d0e0960e61

- Learning: Run run_d2d0e0960e61 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning: Capability Trust Promotion Audit

- Capability trust-promotion readiness should be audited from persisted
  promotion decision ledgers, not inferred from roadmap text or generated
  markdown.
- The first trust-promotion audit records 9 audit items, all blocked because
  the latest promotion decision ledger still has 9 deferred promotion
  decisions, 9 missing evidence items, and 9 operator approvals required.
- Trust-promotion audit visibility must stay report-only and must not create
  promotion decision ledgers, gate checklists, evidence plans,
  approval-boundary matrices, proof-gap indexes, readiness reviews, ledgers,
  approvals, proof artifacts, alter routing, schedule work, retry/replay, run
  CI/deploys, enforce budgets, promote trust, or track real spend.

## Learning: Capability Automatic Retry Audit

- Automatic-retry readiness should be audited from persisted trust-promotion
  audits, not inferred from roadmap text or generated markdown.
- The first automatic-retry audit records 9 audit items, all blocked because
  the latest trust-promotion audit still has 9 blocked trust promotions, 9
  missing evidence items, and 9 operator approvals required.
- Automatic-retry audit visibility must stay report-only and must not create
  trust-promotion audits, promotion decision ledgers, gate checklists, evidence
  plans, approval-boundary matrices, proof-gap indexes, readiness reviews,
  ledgers, approvals, proof artifacts, alter routing, schedule work,
  retry/replay, run CI/deploys, enforce budgets, promote trust, or track real
  spend.

## Learning: Capability Real Cost Tracking Audit

- Real-cost-tracking readiness should be audited from persisted
  automatic-retry audits, not inferred from roadmap text or generated markdown.
- The first real-cost-tracking audit records 9 audit items, all blocked because
  the latest automatic-retry audit still has 9 blocked retries, 9 blocked trust
  promotions, 9 missing evidence items, and 9 operator approvals required.
- Real-cost-tracking audit visibility must stay report-only and must not create
  automatic-retry audits, trust-promotion audits, promotion decision ledgers,
  gate checklists, evidence plans, approval-boundary matrices, proof-gap
  indexes, readiness reviews, ledgers, approvals, proof artifacts, alter
  routing, schedule work, retry/replay, run CI/deploys, enforce budgets,
  promote trust, track real spend, or mutate external systems.

## Learning: Hosted Dashboard Proof Checklist

- Hosted-dashboard proof readiness should be checked from persisted
  real-cost-tracking audits, not inferred from roadmap text or generated
  markdown.
- The first hosted-dashboard proof checklist records 1 checklist item for
  `hosted_dashboard`, blocked by cost tracking, retry, trust promotion,
  missing-evidence, and operator-approval blockers.
- Hosted-dashboard proof checklist visibility must stay report-only and must
  not enable or deploy hosted dashboards, start remote workers, run CI/deploys,
  enforce budgets, change routing, track real spend, or mutate external
  systems.

## Learning: Remote Worker Proof Checklist

- Remote-worker proof readiness should be checked from persisted
  hosted-dashboard proof checklists, not inferred from roadmap text or
  generated markdown.
- The first remote-worker proof checklist records 1 checklist item for
  `remote_workers`, blocked by hosted-dashboard proof, cost tracking, retry,
  trust promotion, missing-evidence, and operator-approval blockers.
- Remote-worker proof checklist visibility must stay report-only and must not
  create hosted-dashboard proof checklists or upstream reports, enable or
  deploy hosted dashboards, start remote workers, claim remote work, run
  CI/deploys, enforce budgets, change routing, track real spend, or mutate
  external systems.

## Learning: Real-Cost-Sourced Remote Worker Proof Checklist

- Remote-worker proof checklist items should preserve Real-Cost-sourced
  hosted-dashboard proof metadata when the source hosted-dashboard proof
  checklist carries it; otherwise downstream proof rungs lose the proof-chain
  reason for keeping remote workers disabled.
- The Real-Cost-sourced remote-worker proof checklist records 1 checklist item
  for `remote_workers`, blocked by Hosted Dashboard proof, Real Cost Tracking
  proof, Automatic Retry proof, Trust Promotion proof, Budget Enforcement
  proof, CI Deploy proof, browser/desktop adapter proof, autonomous scheduling
  proof, remote-worker proof, cost tracking, retry, trust promotion,
  missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create hosted-dashboard
  proof checklists, start or claim remote work, enable hosted dashboards,
  schedule autonomous work, operate adapters, run CI/deploys, enforce budgets,
  retry/replay, promote trust, track spend, change routing, or mutate external
  systems.

## Learning: Latest Real-Cost-Sourced Remote Worker Proof Checklist

- When the latest Hosted Dashboard Proof Checklist is sourced from a
  Real-Cost-sourced Real Cost Tracking proof checklist, the Remote Worker Proof
  Checklist report should expose both the hosted-dashboard source checklist and
  that source proof's own source checklist id/status.
- The latest live Remote Worker proof checklist remains blocked/report-only and
  is the correct source for the next Autonomous Scheduling proof packet.

## Learning: Autonomous Scheduling Proof Checklist

- Autonomous-scheduling proof readiness should be checked from persisted
  remote-worker proof checklists, not inferred from roadmap text or generated
  markdown.
- The first autonomous-scheduling proof checklist records 1 checklist item for
  `autonomous_scheduling`, blocked by remote-worker proof,
  hosted-dashboard proof, cost tracking, retry, trust promotion,
  missing-evidence, and operator-approval blockers.
- Autonomous-scheduling proof checklist visibility must stay report-only and
  must not create remote-worker proof checklists or upstream reports, schedule
  autonomous work, start remote workers, claim remote work, run CI/deploys,
  enforce budgets, change routing, track real spend, operate browser or
  desktop adapters, or mutate external systems.

## Learning: Real-Cost-Sourced Autonomous Scheduling Proof Checklist

- Autonomous-scheduling proof checklist items should preserve
  Real-Cost-sourced remote-worker proof metadata when the source remote-worker
  proof checklist carries it; otherwise downstream adapter proof rungs lose
  the proof-chain reason for keeping scheduling disabled.
- The Real-Cost-sourced autonomous-scheduling proof checklist records 1
  checklist item for `autonomous_scheduling`, blocked by Remote Worker proof,
  Hosted Dashboard proof, Real Cost Tracking proof, Automatic Retry proof,
  Trust Promotion proof, Budget Enforcement proof, CI Deploy proof,
  browser/desktop adapter proof, autonomous scheduling proof, cost tracking,
  retry, trust promotion, missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create remote-worker proof
  checklists, schedule autonomous work, start or claim remote work, enable
  hosted dashboards, operate adapters, run CI/deploys, enforce budgets,
  retry/replay, promote trust, track spend, change routing, or mutate external
  systems.

## Learning: Browser Desktop Adapter Proof Checklist

- Browser/desktop adapter proof readiness should be checked from persisted
  autonomous-scheduling proof checklists, not inferred from roadmap text or
  generated markdown.
- The first browser/desktop adapter proof checklist records 1 checklist item
  for `browser_desktop_adapters`, blocked by autonomous-scheduling proof,
  remote-worker proof, hosted-dashboard proof, cost tracking, retry, trust
  promotion, missing-evidence, and operator-approval blockers.
- Browser/desktop adapter proof checklist visibility must stay report-only and
  must not create autonomous-scheduling proof checklists or upstream reports,
  schedule autonomous work, operate browser or desktop adapters, start remote
  workers, claim remote work, run CI/deploys, enforce budgets, change routing,
  track real spend, or mutate external systems.

## Learning: Real-Cost-Sourced Browser Desktop Adapter Proof Checklist

- Browser/desktop adapter proof checklist items should preserve
  Real-Cost-sourced autonomous-scheduling proof metadata when the source
  autonomous-scheduling proof checklist carries it; otherwise downstream
  CI/deploy proof rungs lose the proof-chain reason for keeping adapters
  disabled.
- The Real-Cost-sourced browser/desktop adapter proof checklist records 1
  checklist item for `browser_desktop_adapters`, blocked by Autonomous
  Scheduling proof, Remote Worker proof, Hosted Dashboard proof, Real Cost
  Tracking proof, Automatic Retry proof, Trust Promotion proof, Budget
  Enforcement proof, CI Deploy proof, browser/desktop adapter proof, cost
  tracking, retry, trust promotion, missing-evidence, and operator-approval
  blockers.
- This visibility remains report-only: it must not create
  autonomous-scheduling proof checklists, operate browser/desktop adapters,
  schedule autonomous work, start or claim remote work, enable hosted
  dashboards, run CI/deploys, enforce budgets, retry/replay, promote trust,
  track spend, change routing, or mutate external systems.

## Learning: CI Deploy Proof Checklist

- CI Deploy proof readiness should be checked from persisted browser/desktop
  adapter proof checklists, not inferred from roadmap text or generated
  markdown.
- The first CI Deploy proof checklist records 1 checklist item for
  `ci_deploy_proof`, blocked by browser/desktop adapter proof,
  autonomous-scheduling proof, remote-worker proof, hosted-dashboard proof,
  cost tracking, retry, trust promotion, missing-evidence, and
  operator-approval blockers.
- CI Deploy proof checklist visibility must stay report-only and must not
  create browser/desktop adapter proof checklists or upstream reports, run CI
  or deploys, operate browser or desktop adapters, schedule autonomous work,
  start remote workers, claim remote work, enforce budgets, change routing,
  track real spend, or mutate external systems.

## Learning: Real-Cost-Sourced CI Deploy Proof Checklist

- CI Deploy proof checklist items should preserve Real-Cost-sourced
  browser/desktop adapter proof metadata when the source browser/desktop
  adapter proof checklist carries it; otherwise downstream Budget Enforcement
  proof rungs lose the proof-chain reason for keeping CI/deploy disabled.
- The Real-Cost-sourced CI Deploy proof checklist records 1 checklist item for
  `ci_deploy_proof`, blocked by Browser/Desktop Adapter proof, Autonomous
  Scheduling proof, Remote Worker proof, Hosted Dashboard proof, Real Cost
  Tracking proof, Automatic Retry proof, Trust Promotion proof, Budget
  Enforcement proof, CI Deploy proof, cost tracking, retry, trust promotion,
  missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create browser/desktop
  adapter proof checklists, run CI/deploys, operate adapters, schedule
  autonomous work, start or claim remote work, enable hosted dashboards,
  enforce budgets, retry/replay, promote trust, track spend, change routing,
  or mutate external systems.

## Learning: Budget Enforcement Proof Checklist

- Budget Enforcement proof readiness should be checked from persisted CI
  Deploy proof checklists, not inferred from roadmap text or generated
  markdown.
- The first Budget Enforcement proof checklist records 1 checklist item for
  `budget_enforcement`, blocked by CI Deploy proof, browser/desktop adapter
  proof, autonomous-scheduling proof, remote-worker proof, hosted-dashboard
  proof, cost tracking, retry, trust promotion, missing-evidence, and
  operator-approval blockers.
- Budget Enforcement proof checklist items should preserve
  Real-Cost-sourced CI Deploy proof metadata when the source CI Deploy proof
  checklist carries it; otherwise downstream Trust Promotion proof rungs lose
  the proof-chain reason for keeping budget enforcement disabled.
- Budget Enforcement proof checklist visibility must stay report-only and must
  not create CI Deploy proof checklists or upstream reports, enforce budgets,
  run CI/deploys, operate browser or desktop adapters, schedule autonomous
  work, start remote workers, claim remote work, change routing, track real
  spend, or mutate external systems.

## Learning: Real-Cost-Sourced Budget Enforcement Proof Checklist

- Budget Enforcement proof checklist items should preserve Real-Cost-sourced
  CI Deploy proof metadata when the source CI Deploy proof checklist carries
  it.
- The Real-Cost-sourced Budget Enforcement proof checklist records 1 checklist
  item for `budget_enforcement`, blocked by CI Deploy proof,
  Browser/Desktop Adapter proof, Autonomous Scheduling proof, Remote Worker
  proof, Hosted Dashboard proof, Real Cost Tracking proof, Automatic Retry
  proof, Trust Promotion proof, Budget Enforcement proof, cost tracking,
  retry, trust promotion, missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create CI Deploy proof
  checklists, enforce budgets, run CI/deploys, operate adapters, schedule
  autonomous work, start or claim remote work, enable hosted dashboards,
  retry/replay, promote trust, track spend, change routing, or mutate
  external systems.

## Learning: Trust Promotion Proof Checklist

- Trust Promotion proof readiness should be checked from persisted Budget
  Enforcement proof checklists, not inferred from roadmap text or generated
  markdown.
- The first Trust Promotion proof checklist records 1 checklist item for
  `trust_promotion`, blocked by Budget Enforcement proof, CI Deploy proof,
  browser/desktop adapter proof, autonomous-scheduling proof, remote-worker
  proof, hosted-dashboard proof, cost tracking, retry, trust promotion,
  missing-evidence, and operator-approval blockers.
- Trust Promotion proof checklist visibility must stay report-only and must
  not create Budget Enforcement proof checklists or upstream reports, promote
  trust, enforce budgets, run CI/deploys, operate browser or desktop adapters,
  schedule autonomous work, start remote workers, claim remote work, change
  routing, track real spend, or mutate external systems.

## Learning: Real-Cost-Sourced Trust Promotion Proof Checklist

- Trust Promotion proof checklist items should carry the Real-Cost-sourced
  Budget Enforcement proof chain forward so the next Automatic Retry rung can
  see why trust promotion remains disabled.
- The Real-Cost-sourced Trust Promotion proof checklist records 1 checklist
  item for `trust_promotion`, blocked by Budget Enforcement proof, CI Deploy
  proof, Browser/Desktop Adapter proof, Autonomous Scheduling proof, Remote
  Worker proof, Hosted Dashboard proof, Real Cost Tracking proof, Automatic
  Retry proof, Trust Promotion proof, cost tracking, retry, trust promotion,
  missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create Budget Enforcement
  proof checklists, promote trust, enforce budgets, run CI/deploys, operate
  adapters, schedule work, start or claim remote work, retry/replay, track
  spend, change routing, or mutate external systems.

## Learning: Automatic Retry Proof Checklist

- Automatic Retry proof readiness should be checked from persisted Trust
  Promotion proof checklists, not inferred from roadmap text or generated
  markdown.
- The first Automatic Retry proof checklist records 1 checklist item for
  `automatic_retry`, blocked by Trust Promotion proof, Budget Enforcement
  proof, CI Deploy proof, browser/desktop adapter proof, autonomous scheduling
  proof, remote-worker proof, hosted-dashboard proof, cost tracking, retry,
  trust promotion, missing-evidence, and operator-approval blockers.
- Automatic Retry proof checklist visibility must stay report-only and must
  not create Trust Promotion proof checklists or upstream reports, promote
  trust, retry/replay, track real spend, enforce budgets, run CI/deploys,
  operate browser or desktop adapters, schedule autonomous work, start remote
  workers, claim remote work, change routing, or mutate external systems.

## Learning: Real-Cost-Sourced Automatic Retry Proof Checklist

- Automatic Retry proof checklist items should carry the Real-Cost-sourced
  Trust Promotion proof chain forward so the next Real Cost Tracking rung can
  see why retries remain disabled.
- The Real-Cost-sourced Automatic Retry proof checklist records 1 checklist
  item for `automatic_retry`, blocked by Trust Promotion proof, Budget
  Enforcement proof, CI Deploy proof, Browser/Desktop Adapter proof,
  Autonomous Scheduling proof, Remote Worker proof, Hosted Dashboard proof,
  Real Cost Tracking proof, Automatic Retry proof, cost tracking, retry, trust
  promotion, missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create Trust Promotion
  proof checklists, retry/replay work, promote trust, enforce budgets, run
  CI/deploys, operate adapters, schedule work, start or claim remote work,
  track spend, change routing, or mutate external systems.

## Learning: Real-Cost-Sourced Real Cost Tracking Proof Checklist

- Real Cost Tracking proof checklist items should carry the Real-Cost-sourced
  Automatic Retry proof chain forward so the next Hosted Dashboard proof rung
  can see why spend tracking remains disabled.
- The Real-Cost-sourced Real Cost Tracking proof checklist records 1 checklist
  item for `real_cost_tracking`, blocked by Automatic Retry proof, Trust
  Promotion proof, Budget Enforcement proof, CI Deploy proof, Browser/Desktop
  Adapter proof, Autonomous Scheduling proof, Remote Worker proof, Hosted
  Dashboard proof, Real Cost Tracking proof, cost tracking, retry, trust
  promotion, missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create Automatic Retry
  proof checklists, track spend, retry/replay work, promote trust, enforce
  budgets, run CI/deploys, operate adapters, schedule work, start or claim
  remote work, change routing, or mutate external systems.

## Learning: Real-Cost-Sourced Hosted Dashboard Proof Checklist

- Hosted Dashboard proof checklist items should carry the Real-Cost-sourced
  Real Cost Tracking proof chain forward so the next Remote Worker proof rung
  can see why hosted dashboard deployment remains disabled.
- The Real-Cost-sourced Hosted Dashboard proof checklist records 1 checklist
  item for `hosted_dashboard`, blocked by Real Cost Tracking proof, Automatic
  Retry proof, Trust Promotion proof, Budget Enforcement proof, CI Deploy
  proof, Browser/Desktop Adapter proof, Autonomous Scheduling proof, Remote
  Worker proof, Hosted Dashboard proof, cost tracking, retry, trust promotion,
  missing-evidence, and operator-approval blockers.
- This visibility remains report-only: it must not create Real Cost Tracking
  proof checklists, enable or deploy hosted dashboards, track spend,
  retry/replay work, promote trust, enforce budgets, run CI/deploys, operate
  adapters, schedule work, start or claim remote work, change routing, or
  mutate external systems.

## Learning: Real Cost Tracking Proof Checklist

- Real Cost Tracking proof readiness should be checked from persisted
  Automatic Retry proof checklists, not inferred from roadmap text or
  generated markdown.
- The first Real Cost Tracking proof checklist records 1 checklist item for
  `real_cost_tracking`, blocked by Automatic Retry proof, Trust Promotion
  proof, Budget Enforcement proof, CI Deploy proof, browser/desktop adapter
  proof, autonomous scheduling proof, remote-worker proof, hosted-dashboard
  proof, cost tracking, retry, trust promotion, missing-evidence, and
  operator-approval blockers.
- Real Cost Tracking proof checklist visibility must stay report-only and must
  not create Automatic Retry proof checklists or upstream reports, promote
  trust, retry/replay, track real spend, enforce budgets, run CI/deploys,
  operate browser or desktop adapters, schedule autonomous work, start remote
  workers, claim remote work, change routing, or mutate external systems.

## Learning run_9b6d1517ca29

- Learning: Run run_9b6d1517ca29 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d02a11802c94

- Learning: Run run_d02a11802c94 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_29fb010c87d6

- Learning: Run run_29fb010c87d6 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_45e3ac2c77b5

- Learning: Run run_45e3ac2c77b5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1c95f26d1706

- Learning: Run run_1c95f26d1706 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_cab32f09381f

- Learning: Run run_cab32f09381f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2bac9f89ec8e

- Learning: Run run_2bac9f89ec8e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_db1019999649

- Learning: Run run_db1019999649 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1b3df5c2c342

- Learning: Run run_1b3df5c2c342 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_67ecad07a6ef

- Learning: Run run_67ecad07a6ef showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_faf93cdf8375

- Learning: Run run_faf93cdf8375 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0f377d53ed76

- Learning: Run run_0f377d53ed76 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2f004a4f812e

- Learning: Run run_2f004a4f812e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_54d9e3803278

- Learning: Run run_54d9e3803278 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_df5a25b1c66f

- Learning: Run run_df5a25b1c66f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_940710bd40ed

- Learning: Run run_940710bd40ed showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a2128bc31519

- Learning: Run run_a2128bc31519 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2602a8ce2576

- Learning: Run run_2602a8ce2576 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7da1a4063146

- Learning: Run run_7da1a4063146 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_13cb14b466b4

- Learning: Run run_13cb14b466b4 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e12088846f48

- Learning: Run run_e12088846f48 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_dafb055ee333

- Learning: Run run_dafb055ee333 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_90e9d4a9a1a4

- Learning: Run run_90e9d4a9a1a4 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1b764e2e7835

- Learning: Run run_1b764e2e7835 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9dbad6cf3fb2

- Learning: Run run_9dbad6cf3fb2 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d41bccfe8d92

- Learning: Run run_d41bccfe8d92 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_dd63f3590e77

- Learning: Run run_dd63f3590e77 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ef95760d00e6

- Learning: Run run_ef95760d00e6 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_be3756e3aebf

- Learning: Run run_be3756e3aebf showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1accc98b90e4

- Learning: Run run_1accc98b90e4 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_8e31de564282

- Learning: Run run_8e31de564282 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a36ddde8a20f

- Learning: Run run_a36ddde8a20f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9590a28ef746

- Learning: Run run_9590a28ef746 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_db246504c841

- Learning: Run run_db246504c841 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_52d024aaad91

- Learning: Run run_52d024aaad91 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1592df60c1fb

- Learning: Run run_1592df60c1fb showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ee31e7ccd86f

- Learning: Run run_ee31e7ccd86f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0b437b93dbcb

- Learning: Run run_0b437b93dbcb showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7766f9f14493

- Learning: Run run_7766f9f14493 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0668ce06db2d

- Learning: Run run_0668ce06db2d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_3eaaa82d8bf8

- Learning: Run run_3eaaa82d8bf8 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5a2104fb0811

- Learning: Run run_5a2104fb0811 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6d5b24d09d9f

- Learning: Run run_6d5b24d09d9f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5d89d7158895

- Learning: Run run_5d89d7158895 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning: Latest Real-Cost-Sourced Autonomous Scheduling Proof Checklist

- Autonomous Scheduling proof should select the latest Real-Cost-sourced
  Remote Worker proof checklist when one exists, not merely the newest Remote
  Worker row.
- The Autonomous Scheduling report should retain the Remote Worker source
  Hosted Dashboard proof id/status, the Hosted Dashboard source Real Cost
  Tracking proof id/status, and the Real Cost Tracking source Automatic Retry
  proof id/status when available.
- The current live Autonomous Scheduling proof remains blocked/report-only and
  is the correct source for the next Browser/Desktop Adapter proof packet.

## Learning: Latest Real-Cost-Sourced Browser Desktop Adapter Proof Checklist

- Browser/Desktop Adapter proof should select the latest Real-Cost-sourced
  Autonomous Scheduling proof checklist when one exists, not merely the newest
  Autonomous Scheduling row.
- Newer legacy Autonomous Scheduling rows and dangling Autonomous Scheduling
  rows without retrievable Remote Worker, Hosted Dashboard, Real Cost
  Tracking, and Automatic Retry proof sources should not become valid adapter
  blockers when a stronger proof chain exists.
- Partial optional proof metadata in a Browser/Desktop Adapter checklist item
  should be omitted unless the full optional proof group is present.
- The Browser/Desktop Adapter report should retain the Autonomous Scheduling
  source Remote Worker proof id/status, the Remote Worker source Hosted
  Dashboard proof id/status, the Hosted Dashboard source Real Cost Tracking
  proof id/status, and the Real Cost Tracking source Automatic Retry proof
  id/status when available.
- The current live Browser/Desktop Adapter proof remains blocked/report-only
  and is the correct source for the next CI Deploy proof packet.

## Learning: Latest Real-Cost-Sourced CI Deploy Proof Checklist

- CI Deploy proof should select the latest Real-Cost-sourced Browser/Desktop
  Adapter proof checklist when one exists, not merely the newest
  Browser/Desktop Adapter row.
- The selector should scan all local Browser/Desktop Adapter proof rows, skip
  newer legacy rows, and skip dangling Browser/Desktop Adapter rows without
  retrievable Autonomous Scheduling, Remote Worker, Hosted Dashboard, Real
  Cost Tracking, and Automatic Retry proof sources.
- Partial optional proof metadata should be omitted unless the full optional
  proof group is present.
- The CI Deploy report should retain the Browser/Desktop Adapter source
  Autonomous Scheduling proof id/status, the Autonomous Scheduling source
  Remote Worker proof id/status, the Remote Worker source Hosted Dashboard
  proof id/status, the Hosted Dashboard source Real Cost Tracking proof
  id/status, and the Real Cost Tracking source Automatic Retry proof id/status
  when available.
- The current live CI Deploy proof remains blocked/report-only and is the
  correct source for the next Budget Enforcement proof packet.

## Learning: Latest Real-Cost-Sourced Budget Enforcement Proof Checklist

- Budget Enforcement proof should select the latest Real-Cost-sourced CI
  Deploy proof checklist when one exists, not merely the newest CI Deploy row.
- The selector should scan all local CI Deploy proof rows, skip newer legacy
  rows, and skip dangling CI Deploy rows without retrievable Browser/Desktop
  Adapter, Autonomous Scheduling, Remote Worker, Hosted Dashboard, Real Cost
  Tracking, and Automatic Retry proof sources.
- Partial optional proof metadata should be omitted unless the full optional
  proof group is present.
- The Budget Enforcement report should retain the CI Deploy source
  Browser/Desktop Adapter proof id/status, the Browser/Desktop Adapter source
  Autonomous Scheduling proof id/status, the Autonomous Scheduling source
  Remote Worker proof id/status, the Remote Worker source Hosted Dashboard
  proof id/status, the Hosted Dashboard source Real Cost Tracking proof
  id/status, and the Real Cost Tracking source Automatic Retry proof
  id/status when available.
- The current live Budget Enforcement proof remains blocked/report-only and
  is the correct source for the next Trust Promotion proof packet.

## Learning: Latest Real-Cost-Sourced Trust Promotion Proof Checklist

- Trust Promotion proof should select the latest Real-Cost-sourced Budget
  Enforcement proof checklist when one exists, not merely the newest Budget
  Enforcement row.
- Newer legacy Budget Enforcement rows and dangling Budget Enforcement rows
  without retrievable CI Deploy, Browser/Desktop Adapter, Autonomous
  Scheduling, Remote Worker, Hosted Dashboard, Real Cost Tracking, and
  Automatic Retry proof sources should not become valid Trust Promotion
  blockers when a stronger proof chain exists.
- The Trust Promotion report should retain the Budget Enforcement source CI
  Deploy proof id/status, the CI Deploy source Browser/Desktop Adapter proof
  id/status, the Browser/Desktop Adapter source Autonomous Scheduling proof
  id/status, the Autonomous Scheduling source Remote Worker proof id/status,
  the Remote Worker source Hosted Dashboard proof id/status, the Hosted
  Dashboard source Real Cost Tracking proof id/status, and the Real Cost
  Tracking source Automatic Retry proof id/status when available.
- The current live Trust Promotion proof
  `trust_promotion_proof_checklist_2505a9003449` remains blocked/report-only
  and is the correct source for the next Automatic Retry proof packet.

## Learning: Latest Real-Cost-Sourced Automatic Retry Proof Checklist

- Automatic Retry proof should select the latest Real-Cost-sourced Trust
  Promotion proof checklist when one exists, not merely the newest Trust
  Promotion row.
- Automatic Retry proof should skip newer legacy Trust Promotion rows and
  dangling Trust Promotion rows unless the Budget Enforcement -> CI Deploy ->
  Browser/Desktop Adapter -> Autonomous Scheduling -> Remote Worker -> Hosted
  Dashboard -> Real Cost Tracking -> Automatic Retry source chain is
  retrievable.
- The Automatic Retry report should retain the Trust Promotion source Budget
  Enforcement proof id/status, the Budget Enforcement source CI Deploy proof
  id/status, the CI Deploy source Browser/Desktop Adapter proof id/status, the
  Browser/Desktop Adapter source Autonomous Scheduling proof id/status, the
  Autonomous Scheduling source Remote Worker proof id/status, the Remote Worker
  source Hosted Dashboard proof id/status, the Hosted Dashboard source Real Cost
  Tracking proof id/status, and the Real Cost Tracking source Automatic Retry
  proof id/status when available.
- The current live Automatic Retry proof remains blocked/report-only and is the
  correct source for the next Real Cost Tracking proof packet.

## Learning: Latest Real-Cost-Sourced Real Cost Tracking Proof Checklist

- Real Cost Tracking proof should select the latest Real-Cost-sourced Automatic
  Retry proof checklist when one exists, not merely the newest Automatic Retry
  row.
- The Real Cost Tracking report should retain the Automatic Retry source Trust
  Promotion proof id/status, the Trust Promotion source Budget Enforcement
  proof id/status, the Budget Enforcement source CI Deploy proof id/status,
  the CI Deploy source Browser/Desktop Adapter proof id/status, the
  Browser/Desktop Adapter source Autonomous Scheduling proof id/status, the
  Autonomous Scheduling source Remote Worker proof id/status, the Remote Worker
  source Hosted Dashboard proof id/status, the Hosted Dashboard source Real
  Cost Tracking proof id/status, and the source Real Cost Tracking proof's
  Automatic Retry source id/status when available.
- The current live Real Cost Tracking proof remains blocked/report-only and is
  the correct source for the next Hosted Dashboard proof packet.

## Learning: Latest Real-Cost-Sourced Hosted Dashboard Proof Checklist

- Hosted Dashboard proof should select the latest Real-Cost-sourced Real Cost
  Tracking proof checklist when one exists, not merely the newest Real Cost
  Tracking row.
- The Hosted Dashboard report should retain the Real Cost Tracking source
  Automatic Retry proof id/status, Automatic Retry source Trust Promotion proof
  id/status, Trust Promotion source Budget Enforcement proof id/status, Budget
  Enforcement source CI Deploy proof id/status, CI Deploy source
  Browser/Desktop Adapter proof id/status, Browser/Desktop Adapter source
  Autonomous Scheduling proof id/status, Autonomous Scheduling source Remote
  Worker proof id/status, Remote Worker source Hosted Dashboard proof
  id/status, Hosted Dashboard source Real Cost Tracking proof id/status, and
  that source Real Cost Tracking proof's Automatic Retry source id/status when
  available.
- Dangling Real Cost Tracking proof rows without a retrievable upstream
  Automatic Retry proof source should report a missing proof instead of
  becoming a Hosted Dashboard blocker.
- The current live Hosted Dashboard proof remains blocked/report-only and is
  the correct source for the next Remote Worker proof packet.

## Learning: Latest Real-Cost-Sourced Remote Worker Proof Checklist, Second Pass

- Remote Worker proof should select the latest Real-Cost-sourced Hosted
  Dashboard proof checklist when one exists, not merely the newest Hosted
  Dashboard row.
- Newer legacy Hosted Dashboard proof rows and dangling Hosted Dashboard rows
  without retrievable Real Cost Tracking and Automatic Retry proof sources
  should not become valid Remote Worker blockers when a stronger proof chain
  exists.
- Partial optional proof metadata in a Remote Worker checklist item should be
  omitted from rendering unless the full optional proof group is present.
- The current live Remote Worker proof remains blocked/report-only and is the
  correct source for the next Autonomous Scheduling proof packet.

## Learning: Latest Real-Cost-Sourced Autonomous Scheduling Proof Checklist, Second Pass

- Autonomous Scheduling proof should select the latest Real-Cost-sourced
  Remote Worker proof checklist when one exists, not merely the newest Remote
  Worker row.
- Newer legacy Remote Worker proof rows and dangling Remote Worker rows
  without retrievable Hosted Dashboard, Real Cost Tracking, and Automatic
  Retry proof sources should not become valid Autonomous Scheduling blockers
  when a stronger proof chain exists.
- Partial optional proof metadata in an Autonomous Scheduling checklist item
  should be omitted from rendering unless the full optional proof group is
  present.
- The current live Autonomous Scheduling proof remains blocked/report-only and
  is the correct source for the next Browser/Desktop Adapter proof packet.

## Learning run_e44a1d0e0bed

- Learning: Run run_e44a1d0e0bed showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_64cadedfe744

- Learning: Run run_64cadedfe744 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_295b60ac0286

- Learning: Run run_295b60ac0286 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e1a5fe40a92d

- Learning: Run run_e1a5fe40a92d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_03e06859bd9e

- Learning: Run run_03e06859bd9e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_77e1fb3ccb3a

- Learning: Run run_77e1fb3ccb3a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_534758ebb666

- Learning: Run run_534758ebb666 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_705be5e6788d

- Learning: Run run_705be5e6788d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_abbcc132d45f

- Learning: Run run_abbcc132d45f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9edb9779bfb7

- Learning: Run run_9edb9779bfb7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_cad12de7bd0b

- Learning: Run run_cad12de7bd0b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ac6219925a6d

- Learning: Run run_ac6219925a6d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d195146c147d

- Learning: Run run_d195146c147d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_4f374811257a

- Learning: Run run_4f374811257a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6a77df0663e3

- Learning: Run run_6a77df0663e3 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_8f38a552b447

- Learning: Run run_8f38a552b447 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_3efe3cfa1a4f

- Learning: Run run_3efe3cfa1a4f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_efef50f9f345

- Learning: Run run_efef50f9f345 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0015af31d594

- Learning: Run run_0015af31d594 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_784e464afd63

- Learning: Run run_784e464afd63 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_4a2b8d37a912

- Learning: Run run_4a2b8d37a912 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d2db34386fd4

- Learning: Run run_d2db34386fd4 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c7b653e389a5

- Learning: Run run_c7b653e389a5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_39647f055e8c

- Learning: Run run_39647f055e8c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e152d3eccdfb

- Learning: Run run_e152d3eccdfb showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_bfa5f9998f2f

- Learning: Run run_bfa5f9998f2f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0755d4107bdd

- Learning: Run run_0755d4107bdd showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5cd688e012ff

- Learning: Run run_5cd688e012ff showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_96a3ee5ae36d

- Learning: Run run_96a3ee5ae36d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_054750939faf

- Learning: Run run_054750939faf showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_da02810ad015

- Learning: Run run_da02810ad015 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6aad25670310

- Learning: Run run_6aad25670310 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5a231a4affb6

- Learning: Run run_5a231a4affb6 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning: Goal Completion Audit

- Expansion-goal completion needs a separate audit over the proof-checklist
  ladder; individual report-only proof rows are necessary visibility, not
  sufficient completion evidence.
- The current audit keeps hosted dashboard, remote workers, autonomous
  scheduling, browser/desktop adapters, CI/deploy proof, budget enforcement,
  trust promotion, automatic retries, and real cost tracking blocked until
  real evidence, approvals, and external decisions exist.

## Learning: Expansion Operator Decision Ledger

- `expansion-operator-decision-ledger` records pending/manual posture from the
  latest operator review checklist; it is not the approval mechanism.
- The first ledger records 11 decision rows: 11 pending, 0 approved, 0
  deferred, 0 more-evidence-requested, 2 external decisions, and 9 capability
  decisions.
- Allowed actions such as `approve`, `defer`, and `request_more_evidence` are
  not actions taken until a separate approved flow records the operator
  choice.

## Learning: Expansion Operator Approval Draft

- `expansion-operator-approval-draft` prepares draft-only approval-request
  packet rows from a usable pending decision ledger; it is not the approval
  mechanism.
- Draft rows remain `draft_only` with `approval_request_status=not_created`,
  and live verification must keep `created_approval_requests: 0`.
- Missing, placeholder, or empty decision ledgers are not approval-ready input;
  the draft reports `operator_decision_ledger_not_ready` instead of creating
  draft items from an unusable source.

## Learning: Expansion Operator Approval Request Review

- `expansion-operator-approval-request-review` reviews draft approval packets
  against the existing `approval_requests` contract; it is still not the
  approval mechanism.
- Current external and capability requests remain blocked by
  `approval_request_subject_not_modeled` with `creation_status=not_created`.
- Live verification must keep `created_approval_requests: 0` and
  `existing_approval_requests: 0` until an explicit approval subject model is
  implemented.
- The schema gap should retain missing approval-table fields:
  `task_id,goal_id,project_id,task_type,risk_level,policy_name,policy_version`.

## Learning: Expansion Operator Approval Schema Decision

- `expansion-operator-approval-schema-decision` turns the request-review schema
  gap into a report-only schema decision packet.
- The current recommendation is `operator_approval_requests_table`, with future
  schema object `operator_approval_requests`, because it preserves the existing
  task approval gate and avoids synthetic queue tasks for operator decisions.
- Live verification must keep `migration_applied: 0`,
  `created_approval_requests: 0`, and no operator approval rows until an
  explicit migration plan is approved.

## Learning: Expansion Operator Approval Schema Migration Plan

- `expansion-operator-approval-schema-migration-plan` turns the approved schema
  option into a proposed table plan without applying the schema.
- The current plan targets `operator_approval_requests`, with 26 planned
  columns, 4 planned indexes, and 4 migration steps.
- Live verification must keep `migration_applied: 0`, `table_created: 0`,
  `operator_approval_rows_created: 0`, and `approval_requests_created: 0`
  until an explicit operator approval authorizes applying the migration.

## Learning: Expansion Operator Approval Schema Migration Approval Request

- `expansion-operator-approval-schema-migration-approval-request` turns the
  migration plan into a report-only approval packet without taking an action.
- The current packet requests `apply_operator_approval_requests_schema`, uses
  approval boundary `schema_migration`, and exposes allowed actions
  `approve,defer,request_more_evidence`.
- Live verification must keep `migration_applied: 0`, `table_created: 0`,
  `operator_approval_rows_created: 0`, and `approval_requests_created: 0`
  until an explicit operator decision is recorded.

## Learning run_0197ce1f9863

- Learning: Run run_0197ce1f9863 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d2534b6572d4

- Learning: Run run_d2534b6572d4 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e23054c31931

- Learning: Run run_e23054c31931 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_4953c335d98b

- Learning: Run run_4953c335d98b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_29913449aabc

- Learning: Run run_29913449aabc showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ce78a3447127

- Learning: Run run_ce78a3447127 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2140d8b2e109

- Learning: Run run_2140d8b2e109 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_219a8d652890

- Learning: Run run_219a8d652890 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a87d1a94b79c

- Learning: Run run_a87d1a94b79c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2735c5f0c227

- Learning: Run run_2735c5f0c227 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_71be44a8366f

- Learning: Run run_71be44a8366f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2b5dfa544325

- Learning: Run run_2b5dfa544325 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_f03cacb50c00

- Learning: Run run_f03cacb50c00 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_41ad6e7b6baa

- Learning: Run run_41ad6e7b6baa showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c2a020af0ea2

- Learning: Run run_c2a020af0ea2 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5700c564cd17

- Learning: Run run_5700c564cd17 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ce99839a37b6

- Learning: Run run_ce99839a37b6 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a9dfa401c26b

- Learning: Run run_a9dfa401c26b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a4aa083f1f23

- Learning: Run run_a4aa083f1f23 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_24dec73feae5

- Learning: Run run_24dec73feae5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_705e9f53edc1

- Learning: Run run_705e9f53edc1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5e54e5ca400f

- Learning: Run run_5e54e5ca400f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6eae8c1a5d9c

- Learning: Run run_6eae8c1a5d9c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_604a33781c2f

- Learning: Run run_604a33781c2f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c1fa8e225bf7

- Learning: Run run_c1fa8e225bf7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_84fd053bbdf7

- Learning: Run run_84fd053bbdf7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_54025ba42771

- Learning: Run run_54025ba42771 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_fa04499de687

- Learning: Run run_fa04499de687 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_66c5a0ad5210

- Learning: Run run_66c5a0ad5210 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning: Expansion Operator Approval Schema Migration Decision Ledger

- The schema migration approval chain now has a separate pending/manual
  decision-ledger rung after the approval request packet.
- The latest ledger,
  `expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081`,
  preserves source request
  `expansion_operator_approval_schema_migration_approval_request_88a59ed82a34`
  and records one `pending_operator_action` for
  `apply_operator_approval_requests_schema`.
- Keep schema application, table creation, approval-row creation, and
  `approval_requests` creation at zero until a distinct approved operator
  action flow is designed and verified.

## Learning: Expansion Operator Approval Schema Migration Action Checklist

- The schema migration approval chain now has an explicit manual action
  checklist after the pending decision ledger.
- The latest checklist,
  `expansion_operator_approval_schema_migration_action_checklist_c8d344afd257`,
  preserves source ledger
  `expansion_operator_approval_schema_migration_decision_ledger_8354ba63b081`
  and keeps `selected_action: none`, `actions_taken: 0`, and all
  schema/table/approval-row mutation counters at zero.
- Treat `operator_approval_schema_migration_operator_selection_required` as
  the next boundary; do not apply migrations or create approval rows until an
  explicit operator selection flow is designed and verified.

## Learning: Expansion Operator Approval Schema Migration Selection Packet

- The schema migration approval chain now has an explicit operator-input packet
  after the manual action checklist.
- The latest packet preserves source checklist
  `expansion_operator_approval_schema_migration_action_checklist_c8d344afd257`
  and keeps `selected_action: none`, `selections_recorded: 0`,
  `actions_taken: 0`, and all schema/table/approval-row mutation counters at
  zero.
- Treat
  `operator_approval_schema_migration_operator_selection_input_required` as
  the next boundary; do not record a selection, apply migrations, or create
  approval rows until an explicit operator selection flow is designed and
  verified.

## Learning: Expansion Operator Approval Schema Migration Selection Input Template

- The schema migration approval chain now has an explicit operator input
  template after the selection packet.
- The latest template preserves source packet
  `expansion_operator_approval_schema_migration_selection_packet_05fdef0caa17`
  and keeps `inputs_recorded: 0`, `selections_recorded: 0`,
  `selected_action: none`, `actions_taken: 0`, and all schema/table/approval-row
  mutation counters at zero.
- Treat `operator_approval_schema_migration_operator_input_required` as the
  next boundary; do not record input, record a selection, apply migrations, or
  create approval rows until explicit operator input is provided and verified.

## Learning run_b4567c7f4709

- Learning: Run run_b4567c7f4709 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1f5819f6547c

- Learning: Run run_1f5819f6547c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_53c46f6d9926

- Learning: Run run_53c46f6d9926 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a08cb9a26ca1

- Learning: Run run_a08cb9a26ca1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_64d3fd52b283

- Learning: Run run_64d3fd52b283 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_21b6a386585b

- Learning: Run run_21b6a386585b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_60c83a6cdc32

- Learning: Run run_60c83a6cdc32 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_547845d76cbe

- Learning: Run run_547845d76cbe showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_f53498dc62ff

- Learning: Run run_f53498dc62ff showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c97fc54ea589

- Learning: Run run_c97fc54ea589 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a0c003d91c49

- Learning: Run run_a0c003d91c49 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e7a7e3131ca9

- Learning: Run run_e7a7e3131ca9 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ec08ac8afc78

- Learning: Run run_ec08ac8afc78 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_e5fb00a2281a

- Learning: Run run_e5fb00a2281a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0083145f0860

- Learning: Run run_0083145f0860 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_dd35af759bf1

- Learning: Run run_dd35af759bf1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_8446c13ffdf5

- Learning: Run run_8446c13ffdf5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c9f27563004a

- Learning: Run run_c9f27563004a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_89e2b27803c1

- Learning: Run run_89e2b27803c1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2b6b0b2f72a8

- Learning: Run run_2b6b0b2f72a8 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_48c25da1dc60

- Learning: Run run_48c25da1dc60 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a013a9d6f48f

- Learning: Run run_a013a9d6f48f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_06e1465cad6d

- Learning: Run run_06e1465cad6d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7a9b1e946e32

- Learning: Run run_7a9b1e946e32 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_dd1c529d99f5

- Learning: Run run_dd1c529d99f5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6fcdef549e8b

- Learning: Run run_6fcdef549e8b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_14bdf1a0b1cb

- Learning: Run run_14bdf1a0b1cb showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ce1a7fc25cd8

- Learning: Run run_ce1a7fc25cd8 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_03eaeada2d97

- Learning: Run run_03eaeada2d97 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d52df83d4bba

- Learning: Run run_d52df83d4bba showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_700e3874f0cd

- Learning: Run run_700e3874f0cd showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_10ab8e90564a

- Learning: Run run_10ab8e90564a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_052990c19430

- Learning: Run run_052990c19430 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_fd407239da0f

- Learning: Run run_fd407239da0f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_da9053c101aa

- Learning: Run run_da9053c101aa showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_3d755f0aab76

- Learning: Run run_3d755f0aab76 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_69b9d4af9bf1

- Learning: Run run_69b9d4af9bf1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2cffa41b4f05

- Learning: Run run_2cffa41b4f05 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0080e0fe7462

- Learning: Run run_0080e0fe7462 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7964f9ddd944

- Learning: Run run_7964f9ddd944 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_706a409ddded

- Learning: Run run_706a409ddded showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_533ba4c469c4

- Learning: Run run_533ba4c469c4 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_f3f628326998

- Learning: Run run_f3f628326998 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2bd28a33546a

- Learning: Run run_2bd28a33546a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_40790f144c91

- Learning: Run run_40790f144c91 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_fbfd3145e789

- Learning: Run run_fbfd3145e789 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_49a0a5c2b535

- Learning: Run run_49a0a5c2b535 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7a6b67313ad9

- Learning: Run run_7a6b67313ad9 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7a274a64c63c

- Learning: Run run_7a274a64c63c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_866139841586

- Learning: Run run_866139841586 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ea9f8f455264

- Learning: Run run_ea9f8f455264 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_b96ce8f34c7b

- Learning: Run run_b96ce8f34c7b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a3d4b9fcbe41

- Learning: Run run_a3d4b9fcbe41 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7b7c73848df1

- Learning: Run run_7b7c73848df1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_168daa0b1ab7

- Learning: Run run_168daa0b1ab7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_f95f1af299b5

- Learning: Run run_f95f1af299b5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6aaaf091a7a0

- Learning: Run run_6aaaf091a7a0 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_de3c184afb5d

- Learning: Run run_de3c184afb5d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_357ca9a6d7fa

- Learning: Run run_357ca9a6d7fa showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9a36a417e092

- Learning: Run run_9a36a417e092 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_5abaa9a0176d

- Learning: Run run_5abaa9a0176d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c0a2f690460d

- Learning: Run run_c0a2f690460d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_30b88ff510c7

- Learning: Run run_30b88ff510c7 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1da58c9a62d1

- Learning: Run run_1da58c9a62d1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_51df62621e6b

- Learning: Run run_51df62621e6b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_917b14566d23

- Learning: Run run_917b14566d23 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_38a7d9c5354c

- Learning: Run run_38a7d9c5354c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ea63edf343f5

- Learning: Run run_ea63edf343f5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6688c4a689d3

- Learning: Run run_6688c4a689d3 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_fb277f1d82df

- Learning: Run run_fb277f1d82df showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_660cb0357548

- Learning: Run run_660cb0357548 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_af75fe75ca2b

- Learning: Run run_af75fe75ca2b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_be7bcaef132d

- Learning: Run run_be7bcaef132d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_1c4ddeb9652f

- Learning: Run run_1c4ddeb9652f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_82796f63f258

- Learning: Run run_82796f63f258 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_79feca04b697

- Learning: Run run_79feca04b697 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_2441e028f6c2

- Learning: Run run_2441e028f6c2 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7a03009ac0e9

- Learning: Run run_7a03009ac0e9 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_3259313197c0

- Learning: Run run_3259313197c0 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_56e58e2665fa

- Learning: Run run_56e58e2665fa showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_7018e86ea326

- Learning: Run run_7018e86ea326 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d1ee1ffa9162

- Learning: Run run_d1ee1ffa9162 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c4553a4de66d

- Learning: Run run_c4553a4de66d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6623795ccd5a

- Learning: Run run_6623795ccd5a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_6bf53ce1f7b2

- Learning: Run run_6bf53ce1f7b2 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_20e17f766d13

- Learning: Run run_20e17f766d13 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_b6f39da18d37

- Learning: Run run_b6f39da18d37 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning effect proposal bridge

- Accepted blocked downstream result decisions should become generic
  proposal-only `effects` rows with a stage-specific idempotency prefix before
  any application-record slice. Do not add approval rows, apply effects,
  satisfy proof, allow activation, or enable capabilities in the proposal
  stage.

## Learning effect application bridge

- Accepted blocked downstream result effect task result decision effects should
  be applied through a local application-record slice that marks applicable
  effects `applied` and writes application evidence, while still preserving
  zero approval rows, zero activation actions, zero external mutations,
  `activation_allowed=false`, and `capability_enabled=false`.

## Learning effect task bridge

- Applied downstream result effect task result decision effects should become
  pending task graph rows before routing or delegation. The task-materializing
  stage should preserve source decision, result, application, effect,
  delegation, task, contract, project, and capability links while keeping
  approval rows, activation actions, external mutations, activation allowance,
  and capability enablement at zero.

## Learning effect task delegation bridge

- Pending downstream result effect task result effect tasks should route into
  read-only evaluator delegation packets before result ingestion. The routing
  stage should create durable routing decisions, pending subagent delegation
  rows, and local JSON artifacts while preserving source links and keeping
  execution, provider calls, approval rows, activation actions, external
  mutations, activation allowance, and capability enablement at zero.

## Learning effect task result ingestion bridge

- Completed downstream result effect task result effect delegation packets
  should become local result records and JSON artifacts before operator
  review. The ingestion stage should preserve source decision, result,
  application, effect, delegation, task, contract, project, and capability
  links while keeping approval rows, activation actions, external mutations,
  activation allowance, capability enablement, and proof satisfaction at zero.

## Learning effect task result decision bridge

- Downstream result effect task result effect result decisions should allow
  preliminary `request_more_evidence` or `defer_review` rows to be superseded
  by a later `accept_keep_blocked` decision for the same result. Accepted
  keep-blocked decisions are the terminal source for the next proposed-effect
  slice while preserving zero approval rows, zero activation actions, zero
  external mutations, `activation_allowed=false`, and
  `capability_enabled=false`.

## Learning effect task result proposal bridge

- Accepted blocked downstream result effect task result effect result
  decisions should become generic proposal-only `effects` rows with a
  stage-specific idempotency prefix before any application-record slice. The
  proposal stage should preserve source decision, result, application, effect,
  delegation, task, contract, project, and capability links while keeping
  approval rows, activation actions, external mutations, activation allowance,
  and capability enablement at zero.

## Learning eval serialization

- Run `eval` and `eval-after-change` serially. They share the
  `first_milestone_closed_loop` result output; running them concurrently can
  create a failed run artifact even when a serial eval rerun passes.

## Learning run_26885a0289b5

- Learning: Run run_26885a0289b5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_4927d5cebf25

- Learning: Run run_4927d5cebf25 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_bd4187ca97c0

- Learning: Run run_bd4187ca97c0 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_8b1f3acec286

- Learning: Run run_8b1f3acec286 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d2beb553f71a

- Learning: Run run_d2beb553f71a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_42a378a20457

- Learning: Run run_42a378a20457 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_67e2aa5509d1

- Learning: Run run_67e2aa5509d1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_726f7a1ffd32

- Learning: Run run_726f7a1ffd32 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ac030ed77372

- Learning: Run run_ac030ed77372 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_365c9386fb0c

- Learning: Run run_365c9386fb0c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_684366c03ec9

- Learning: Run run_684366c03ec9 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_47b112a4c033

- Learning: Run run_47b112a4c033 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Downstream Result Effect Task Result Effect Application

- Applied downstream result effect task result effect result decision effects
  should remain local ledger applications only: record an application row,
  mark applicable generic `effects` rows as `applied`, preserve source links,
  and keep approval rows, activation actions, external mutations, activation
  allowance, and capability enablement at zero.

## Downstream Result Effect Task Result Effect Tasks

- Applied downstream result effect task result effect result decision effect
  applications should materialize pending downstream proof tasks only:
  preserve source links in task evidence and keep approval rows, activation
  actions, external mutations, activation allowance, capability enablement,
  and proof satisfaction at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Delegations

- Pending downstream result effect task result effect task result effect tasks
  should materialize read-only evaluator delegation packets only: preserve
  source links in routing and packet artifacts and keep execution, provider
  calls, approval rows, activation actions, external mutations, activation
  allowance, and capability enablement at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Results

- Completed downstream result effect task result effect task result effect
  delegation outputs should materialize local result records and JSON
  artifacts only: preserve source links and structured evaluator output while
  keeping approval rows, activation actions, external mutations, activation
  allowance, capability enablement, and proof satisfaction at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Decisions

- Operator decisions for downstream result effect task result effect task
  result effect task result records should stay review-only: allow
  `accept_keep_blocked`, `request_more_evidence`, and `defer_review`, keep
  accepted blocked decisions as the source for the next proposed-effect slice,
  and preserve zero approval rows, activation actions, external mutations,
  activation allowance, capability enablement, and proof satisfaction.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals

- Accepted blocked downstream result effect task result effect task result
  effect task result decisions should become proposal-only generic `effects`
  rows before application. Preserve source decision, result, application,
  effect, delegation, task, contract, project, and capability links while
  keeping approval rows, activation actions, external mutations, activation
  allowance, and capability enablement at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Application

- Proposed downstream result effect task result effect task result effect task
  result decision effects should be applied as local ledger records only:
  record an application row, mark applicable generic `effects` rows as
  `applied`, preserve source decision, result, application, effect,
  delegation, task, contract, project, and capability links, and still keep
  approval rows, activation actions, external mutations, activation allowance,
  and capability enablement at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Tasks

- Applied downstream result effect task result effect task result effect task
  result decision effect applications should materialize pending downstream
  proof tasks only: preserve source links in task evidence and keep approval
  rows, activation actions, external mutations, activation allowance,
  capability enablement, and proof satisfaction at zero.

## Learning run_6aac17428229

- Learning: Run run_6aac17428229 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_a59934b85647

- Learning: Run run_a59934b85647 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c5205e42e98c

- Learning: Run run_c5205e42e98c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_756c74ab5874

- Learning: Run run_756c74ab5874 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_b39c91a3d55e

- Learning: Run run_b39c91a3d55e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_79c09f5f3356

- Learning: Run run_79c09f5f3356 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c43a1ca4746c

- Learning: Run run_c43a1ca4746c showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_b0914e88c600

- Learning: Run run_b0914e88c600 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c146d1d3470f

- Learning: Run run_c146d1d3470f showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d4e7029a8b97

- Learning: Run run_d4e7029a8b97 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_f50924edf3b5

- Learning: Run run_f50924edf3b5 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_ebdd7e7884a4

- Learning: Run run_ebdd7e7884a4 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_d9353699167b

- Learning: Run run_d9353699167b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_043ed13bc23a

- Learning: Run run_043ed13bc23a showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_69f486df6818

- Learning: Run run_69f486df6818 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_67f2e1009254

- Learning: Run run_67f2e1009254 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Delegations

- Pending downstream result effect task result effect task result effect task
  result effect tasks should route into read-only evaluator delegation packets
  before result ingestion. Preserve source links in the routing decision and
  packet artifact, and keep execution, provider calls, approval rows,
  activation actions, external mutations, activation allowance, capability
  enablement, and proof satisfaction at zero.

## Learning run_467a31dc8e9b

- Learning: Run run_467a31dc8e9b showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_347d9c5476f0

- Learning: Run run_347d9c5476f0 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_79c55faad757

- Learning: Run run_79c55faad757 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_cb1e42d04bd1

- Learning: Run run_cb1e42d04bd1 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9840a0f8c284

- Learning: Run run_9840a0f8c284 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_987c0d25c356

- Learning: Run run_987c0d25c356 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Decisions

- Operator decisions for downstream result effect task result effect task
  result effect task result effect result records should be durable local rows:
  `accept_keep_blocked` is terminal for idempotency, while
  `request_more_evidence` and `defer_review` can precede a later accepted
  blocked decision. Keep approval rows, activation actions, external mutations,
  activation allowance, capability enablement, and proof satisfaction at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals

- Accepted blocked downstream result effect task result effect task result
  effect task result effect task result decisions should produce local
  proposed generic `effects` rows only. The proposal stage is the handoff into
  the next local application slice and must keep approval rows, activation
  actions, external mutations, activation allowance, capability enablement,
  and proof satisfaction at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Application

- Proposed downstream result effect task result effect task result effect task
  result effect task result decision effects can be applied as local records
  only after the proposal rows exist. The application stage marks eligible
  effects `applied`, records an application row, and must keep approval rows,
  activation actions, external mutations, activation allowance, capability
  enablement, and proof satisfaction at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Tasks

- Applied downstream result effect task result effect task result effect task
  result effect task result decision effects can be converted into pending
  high-risk downstream proof tasks. This materialization preserves source
  effect, application, decision, result, delegation, task, contract, project,
  and capability links, and it must keep approval rows, routing/delegation
  side effects, activation actions, external mutations, activation allowance,
  capability enablement, and proof satisfaction at zero.

## Learning run_2f3e9e364ab3

- Learning: Run run_2f3e9e364ab3 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_88c5a2e43a85

- Learning: Run run_88c5a2e43a85 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_bb953d9452f2

- Learning: Run run_bb953d9452f2 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_87857b9c6080

- Learning: Run run_87857b9c6080 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0d34a37b268d

- Learning: Run run_0d34a37b268d showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c86e2ef3dc65

- Learning: Run run_c86e2ef3dc65 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Delegations

- Pending downstream result effect task result effect task result effect task
  result effect task result effect tasks must map to `evidence_review` and
  create read-only evaluator delegation packets before any result ingestion.
  The packet stage preserves task, effect, application, result, contract,
  project, and capability links while keeping execution, provider calls,
  approval rows, activation actions, external mutations, activation allowance,
  capability enablement, and proof satisfaction at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Results

- Completed downstream result effect task result effect task result effect task
  result effect task result effect delegation outputs can be ingested only
  after `record-delegation-result` supplies structured evaluator output. The
  ingestion writes local result records and JSON artifacts, preserves source
  decision, result, application, effect, delegation, task, contract, project,
  and capability links, and keeps approval rows, activation actions, external
  mutations, activation allowance, capability enablement, and proof
  satisfaction at zero.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Decisions

- Operator decisions for downstream result effect task result effect task
  result effect task result effect task result effect task result records are
  terminal for idempotency only when `accept_keep_blocked` is recorded. A
  `request_more_evidence` or `defer_review` row can be followed later by an
  accepted blocked decision. The decision stage must keep approval rows,
  activation actions, external mutations, activation allowance, capability
  enablement, and proof satisfaction at zero.

## Learning run_91127e0fee7e

- Learning: Run run_91127e0fee7e showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_42f4470845e8

- Learning: Run run_42f4470845e8 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_c31c6dfc8305

- Learning: Run run_c31c6dfc8305 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_9fe48487b396

- Learning: Run run_9fe48487b396 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_78eae4fa0664

- Learning: Run run_78eae4fa0664 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_0dc0258afe93

- Learning: Run run_0dc0258afe93 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals

- Accepted blocked downstream result effect task result effect task result
  effect task result effect task result effect task result decisions can create
  local proposed generic `effects` rows keyed by decision id and result id.
  The proposal stage must preserve source links and keep approval rows,
  activation actions, external mutations, activation allowance, capability
  enablement, and proof satisfaction at zero. Idempotency is checked by
  rerunning the proposal command and expecting existing proposals with no new
  effects.

## Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Application

- Accepted blocked downstream result effect task result effect task result
  effect task result effect task result effect task result decision effect
  proposals can be applied only as local ledger/application records. The
  application stage marks applicable generic `effects` rows as `applied`,
  preserves source decision/result/application/effect/delegation links, and
  keeps approval rows, activation actions, external mutations, activation
  allowance, capability enablement, and proof satisfaction at zero.

## Learning run_349c6a785d89

- Learning: Run run_349c6a785d89 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_8d22761742cc

- Learning: Run run_8d22761742cc showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_4fbedd855cb2

- Learning: Run run_4fbedd855cb2 showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_feddcf5836ed

- Learning: Run run_feddcf5836ed showed that the first closed loop can be verified through file evidence before expanding to broader domains.

## Learning run_f364483e641a

- Learning: Run run_f364483e641a showed that the first closed loop can be verified through file evidence before expanding to broader domains.
