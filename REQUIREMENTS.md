# Requirements

## Mission

Build a maximally capable, self-improving agentic operating system for
computer-based work. The first usable version must prove a reliable local loop
before expanding breadth.

## Functional Requirements

- Accept goals through a CLI.
- Persist goals, tasks, task attempts, evidence, events, and learnings.
- Decompose a goal into typed tasks with explicit verification plans.
- Let a local worker claim pending tasks through the persisted queue.
- Require explicit local approval before dispatching risky or unknown tasks.
- Persist approval requests and approval decisions with policy metadata.
- Execute safe local file/artifact tasks.
- Verify every task before marking it complete.
- Record incidents when deterministic verification fails.
- Detect stale active tasks and move them to blocked state with evidence.
- Resolve incidents with an operator note, resolver identity, timestamp, and
  durable resolution evidence.
- Report repeated blocked or failed task hotspots by project and task type.
- Review blocked tasks and stale project handoff files against the current
  iteration packet.
- Run the local eval suite after a named harness behavior change and persist
  the change summary, changed paths, eval result paths, and run ids.
- Distill repeated run learnings into stable root `knowledge.md` entries with
  SQLite and report evidence.
- Report local budget/trust posture metadata for task dispatch without
  enforcement, routing, or trust promotion.
- Summarize recent report-only dispatch posture snapshots without enforcement,
  routing, claiming, approval, budget, or trust-promotion effects.
- Review recent report-only dispatch posture snapshot freshness from SQLite
  timestamps without scheduling refreshes or changing dispatch behavior.
- Recommend manual dispatch posture refresh commands from the latest persisted
  staleness review without running refreshes, scheduling work, or changing
  dispatch behavior.
- Record a report-only Capability Expansion Ledger for deferred autonomy
  surfaces, their required evidence, next proof, approval boundary, and lack of
  routing effect.
- Review capability readiness from the latest Capability Expansion Ledger,
  recording missing evidence and recommended manual commands without creating
  ledgers as a side effect or enabling any capability.
- Index capability proof gaps from the latest Capability Readiness Review,
  retaining missing evidence, blocked capabilities, next proof labels, and
  approval boundaries without creating readiness reviews as a side effect or
  generating proof automatically.
- Map capability proof gaps to a report-only Capability Approval Boundary
  Matrix, retaining explicit approval boundaries, blocked capabilities, next
  proof labels, and approval-required counts without approving or promoting
  any capability.
- Plan manual evidence collection from the latest Capability Approval Boundary
  Matrix, retaining required evidence, next proof labels, manual collection
  mode, evidence state, approval boundary, decision state, and routing effect
  without collecting proof or approving any capability.
- Review promotion gates from the latest Capability Evidence Collection Plan,
  retaining evidence state, approval state, missing evidence counts,
  blocked-promotion counts, approval boundaries, and routing effect without
  collecting evidence, approving capabilities, promoting capabilities, or
  changing routing.
- Record report-only promotion decisions from the latest Capability Promotion
  Gate Checklist, retaining deferred-promotion counts, operator-review counts,
  evidence and approval state, and routing effect without approving
  capabilities, promoting trust, promoting capabilities, or changing routing.
- Audit trust-promotion readiness from the latest Capability Promotion
  Decision Ledger, retaining blocked-trust-promotion counts, operator-review
  counts, deferred-promotion counts, evidence and approval state, and routing
  effect without promoting trust, approving capabilities, promoting
  capabilities, or changing routing.
- Audit automatic-retry readiness from the latest Capability Trust Promotion
  Audit, retaining blocked-retry counts, operator-review counts, evidence and
  approval state, and routing effect without retrying, replaying, changing
  routing, or mutating external systems.
- Audit real-cost-tracking readiness from the latest Capability Automatic
  Retry Audit, retaining blocked-cost-tracking counts, operator-review counts,
  blocked-retry counts, trust-promotion counts, evidence and approval state,
  and routing effect without tracking spend, enforcing budgets, changing
  routing, or mutating external systems.
- Check hosted-dashboard proof readiness from the latest Real Cost Tracking
  Proof Checklist, falling back to the legacy Capability Real Cost Tracking
  Audit when no proof checklist exists, retaining source kind, source proof
  checklist/audit ids, dashboard-proof counts, cost/retry/trust blockers,
  Real-Cost-sourced Real Cost Tracking proof metadata when present, evidence
  and approval state, and routing effect without enabling or deploying a
  hosted dashboard.
- Check remote-worker proof readiness from the latest Hosted Dashboard Proof
  Checklist, retaining worker-proof counts, dashboard/cost/retry/trust
  blockers, Real-Cost-sourced hosted-dashboard proof metadata when present,
  evidence and approval state, and routing effect without starting remote
  workers, claiming remote work, or changing routing.
- Check autonomous-scheduling proof readiness from the latest
  Real-Cost-sourced Remote Worker Proof Checklist when one exists, retaining
  scheduling-proof counts, worker/dashboard/cost/retry/trust blockers,
  remote-worker proof metadata, the remote-worker source proof's own source
  metadata when available, evidence and approval state, and routing effect
  without scheduling autonomous work, starting remote workers, or changing
  routing.
- Check browser/desktop adapter proof readiness from the latest Autonomous
  Scheduling Proof Checklist, retaining adapter-proof counts, scheduling/
  worker/dashboard/cost/retry/trust blockers, Real-Cost-sourced autonomous
  scheduling proof metadata when present, evidence and approval state, and
  routing effect without operating browser or desktop adapters, scheduling
  autonomous work, or changing routing.
- Check CI Deploy proof readiness from the latest Real-Cost-sourced Browser
  Desktop Adapter Proof Checklist when one exists, retaining
  CI-Deploy-proof counts, adapter/scheduling/worker/dashboard/cost/retry/trust
  blockers, browser desktop adapter proof metadata, the browser desktop
  adapter source proof's own source metadata when available, evidence and
  approval state, and routing effect without running CI, deploying, or
  changing routing.
- Check Budget Enforcement proof readiness from the latest Real-Cost-sourced
  CI Deploy Proof Checklist when one exists, retaining
  budget-enforcement-proof counts, CI/adapters/scheduling/worker/dashboard/
  cost/retry/trust blockers, CI Deploy proof metadata, the CI Deploy source
  proof's own source metadata when available, evidence and approval state, and
  routing effect without enforcing budgets, running CI/deploys, or changing
  routing.
- Check Trust Promotion proof readiness from the latest Real-Cost-sourced
  Budget Enforcement Proof Checklist when one exists, retaining
  trust-promotion-proof counts,
  budget-enforcement/CI/adapters/scheduling/worker/dashboard/cost/retry/trust
  blockers, Budget Enforcement proof metadata, the Budget Enforcement source
  proof's own source metadata when available, evidence and approval state, and
  routing effect without promoting trust, enforcing budgets, or changing
  routing.
- Check Automatic Retry proof readiness from the latest Trust Promotion Proof
  Checklist, retaining automatic-retry-proof counts,
  trust-promotion/budget-enforcement/CI/adapters/scheduling/worker/dashboard/
  cost/retry/trust blockers, Real-Cost-sourced Trust Promotion proof metadata
  when present, evidence and approval state, and routing effect without
  retrying or replaying work, promoting trust, or changing routing.
- Check Real Cost Tracking proof readiness from the latest Automatic Retry
  Proof Checklist, retaining real-cost-tracking-proof counts,
  automatic-retry/trust-promotion/budget-enforcement/CI/adapters/scheduling/
  worker/dashboard/cost/retry/trust blockers, Real-Cost-sourced Automatic
  Retry proof metadata when present, evidence and approval state, and routing
  effect without tracking spend, retrying, enforcing budgets, or changing
  routing.
- Record proposed eval candidates when verifier or workflow gaps are
  discovered.
- Promote repeated successful eval runs into reusable playbooks with file and
  SQLite evidence.
- Prefer the lower-complexity queue item when candidate scores tie.
- Write human-readable activity, status, and memory artifacts.
- Generate a next-iteration packet from the live momentum queues without
  executing the selected work.
- Generate a static dashboard from persisted runs, tasks, approvals,
  iteration packets, queue-health checks, handoff reviews, eval-after-change
  checks, learning distillations, budget/trust posture reports, dispatch
  posture history summaries, dispatch posture snapshot reviews, dispatch
  posture refresh recommendations, capability expansion ledgers, capability
  readiness reviews, capability proof gap indexes, capability approval
  boundary matrices, capability evidence collection plans, capability
  promotion gate checklists, capability promotion decision ledgers, capability
  trust promotion audits, capability automatic retry audits, capability real
  cost tracking audits, hosted dashboard proof checklists, remote worker proof
  checklists, autonomous scheduling proof checklists, browser desktop adapter
  proof checklists, CI Deploy proof checklists, budget enforcement proof
  checklists, trust promotion proof checklists, automatic retry proof
  checklists, playbooks, eval candidates, stuck-task incidents, learnings, and
  evals.
- Provide a basic eval command for the first closed-loop behavior.

## Non-Functional Requirements

- Local-first and portable.
- SQLite WAL mode for operational state.
- Markdown files for human-readable project state.
- No external side effects in the first milestone.
- No secrets in logs, memory, or artifacts.
- Stable learning promotion is report-only and must not edit prompts, skills,
  tasks, approvals, or handoffs automatically.
- Budget/trust posture is report-only and must not consume budget, promote
  trust, alter routing, change approval decisions, or affect worker claiming.
- Dispatch posture history is report-only and must not change dispatch,
  claiming, approvals, retries, replay, scheduling, CI, deploy, or external
  systems.
- Dispatch posture snapshot review is report-only and must not schedule
  refreshes, run posture reports automatically, change dispatch, claiming,
  approvals, retries, replay, scheduling, CI, deploy, or external systems.
- Dispatch posture refresh recommendation is report-only and must not run
  recommended commands automatically, create posture reports as a side effect,
  schedule refreshes, change dispatch, claiming, approvals, retries, replay,
  scheduling, CI, deploy, hosted dashboards, remote workers, browser or desktop
  adapters, cost tracking, or external systems.
- Capability Expansion Ledger is report-only and must not enable hosted
  dashboards, start remote workers, schedule autonomous work, operate browser
  or desktop adapters, run CI or deploys, enforce budgets, promote trust, retry
  or replay work, track real spend, change routing, or mutate external systems.
- Capability Readiness Review is report-only and must not create Capability
  Expansion Ledgers as a side effect, enable hosted dashboards, start remote
  workers, schedule autonomous work, operate browser or desktop adapters, run
  CI or deploys, enforce budgets, promote trust, retry or replay work, track
  real spend, change routing, or mutate external systems.
- Capability Proof Gap Index is report-only and must not create Capability
  Readiness Reviews or Capability Expansion Ledgers as a side effect, generate
  proof artifacts automatically, enable hosted dashboards, start remote
  workers, schedule autonomous work, operate browser or desktop adapters, run
  CI or deploys, enforce budgets, promote trust, retry or replay work, track
  real spend, change routing, or mutate external systems.
- Capability Approval Boundary Matrix is report-only and must not create
  Capability Proof Gap Indexes, Readiness Reviews, or Expansion Ledgers as a
  side effect, approve capabilities automatically, generate proof artifacts,
  enable hosted dashboards, start remote workers, schedule autonomous work,
  operate browser or desktop adapters, run CI or deploys, enforce budgets,
  promote trust, retry or replay work, track real spend, change routing, change
  claims, or mutate external systems.
- Capability Evidence Collection Plan is report-only and must not create
  Capability Approval Boundary Matrices, Proof Gap Indexes, Readiness Reviews,
  or Expansion Ledgers as a side effect, collect evidence automatically,
  approve capabilities automatically, generate proof artifacts, enable hosted
  dashboards, start remote workers, schedule autonomous work, operate browser
  or desktop adapters, run CI or deploys, enforce budgets, promote trust, retry
  or replay work, track real spend, change routing, change claims, or mutate
  external systems.
- Capability Promotion Gate Checklist is report-only and must not create
  Capability Evidence Collection Plans, Approval Boundary Matrices, Proof Gap
  Indexes, Readiness Reviews, or Expansion Ledgers as a side effect, collect
  evidence automatically, approve capabilities automatically, promote
  capabilities automatically, generate proof artifacts, enable hosted
  dashboards, start remote workers, schedule autonomous work, operate browser
  or desktop adapters, run CI or deploys, enforce budgets, promote trust, retry
  or replay work, track real spend, change routing, change claims, or mutate
  external systems.
- Capability Promotion Decision Ledger is report-only and must not create
  Promotion Gate Checklists, Evidence Collection Plans, Approval Boundary
  Matrices, Proof Gap Indexes, Readiness Reviews, or Expansion Ledgers as a
  side effect, collect evidence automatically, approve capabilities
  automatically, promote capabilities automatically, generate proof artifacts,
  enable hosted dashboards, start remote workers, schedule autonomous work,
  operate browser or desktop adapters, run CI or deploys, enforce budgets,
  promote trust, retry or replay work, track real spend, change routing, change
  claims, or mutate external systems.
- Capability Trust Promotion Audit is report-only and must not create
  Promotion Decision Ledgers, Promotion Gate Checklists, Evidence Collection
  Plans, Approval Boundary Matrices, Proof Gap Indexes, Readiness Reviews, or
  Expansion Ledgers as a side effect, collect evidence automatically, approve
  capabilities automatically, promote capabilities automatically, promote trust
  automatically, generate proof artifacts, enable hosted dashboards, start
  remote workers, schedule autonomous work, operate browser or desktop
  adapters, run CI or deploys, enforce budgets, retry or replay work, track
  real spend, change routing, change claims, or mutate external systems.
- Capability Automatic Retry Audit is report-only and must not create Trust
  Promotion Audits, Promotion Decision Ledgers, Promotion Gate Checklists,
  Evidence Collection Plans, Approval Boundary Matrices, Proof Gap Indexes,
  Readiness Reviews, or Expansion Ledgers as a side effect, collect evidence
  automatically, approve capabilities automatically, promote capabilities
  automatically, promote trust automatically, retry or replay work
  automatically, generate proof artifacts, enable hosted dashboards, start
  remote workers, schedule autonomous work, operate browser or desktop
  adapters, run CI or deploys, enforce budgets, track real spend, change
  routing, change claims, or mutate external systems.
- Capability Real Cost Tracking Audit is report-only and must not create
  Automatic Retry Audits, Trust Promotion Audits, Promotion Decision Ledgers,
  Promotion Gate Checklists, Evidence Collection Plans, Approval Boundary
  Matrices, Proof Gap Indexes, Readiness Reviews, or Expansion Ledgers as a
  side effect, collect evidence automatically, approve capabilities
  automatically, promote capabilities automatically, promote trust
  automatically, retry or replay work automatically, track real spend
  automatically, generate proof artifacts, enable hosted dashboards, start
  remote workers, schedule autonomous work, operate browser or desktop
  adapters, run CI or deploys, enforce budgets, change routing, change claims,
  or mutate external systems.
- Hosted Dashboard Proof Checklist is report-only and must not create Real
  Cost Tracking Audits, Automatic Retry Audits, Trust Promotion Audits,
  Promotion Decision Ledgers, Promotion Gate Checklists, Evidence Collection
  Plans, Approval Boundary Matrices, Proof Gap Indexes, Readiness Reviews, or
  Expansion Ledgers as a side effect, while preserving Real-Cost-sourced Real
  Cost Tracking proof metadata when present; it must not collect evidence
  automatically, approve capabilities automatically, promote capabilities
  automatically, promote trust automatically, retry or replay work
  automatically, track real spend automatically, generate proof artifacts,
  enable or deploy hosted dashboards, start remote workers, schedule
  autonomous work, operate browser or desktop adapters, run CI or deploys,
  enforce budgets, change routing, change claims, or mutate external systems.
- Remote Worker Proof Checklist is report-only and must not create Hosted
  Dashboard Proof Checklists, Real Cost Tracking Audits, Automatic Retry
  Audits, Trust Promotion Audits, Promotion Decision Ledgers, Promotion Gate
  Checklists, Evidence Collection Plans, Approval Boundary Matrices, Proof Gap
  Indexes, Readiness Reviews, or Expansion Ledgers as a side effect, while
  preserving Real-Cost-sourced hosted-dashboard proof metadata and the hosted
  dashboard source proof's own source metadata when present; it must not collect
  evidence automatically, approve capabilities automatically, promote
  capabilities automatically, promote trust automatically, retry or replay work
  automatically, track real spend automatically, generate proof artifacts,
  enable or deploy hosted dashboards, start remote workers, claim remote work,
  schedule autonomous work, operate browser or desktop adapters, run CI or
  deploys, enforce budgets, change routing, change claims, or mutate external
  systems.
- Autonomous Scheduling Proof Checklist is report-only and must not create
  Remote Worker Proof Checklists, Hosted Dashboard Proof Checklists, Real Cost
  Tracking Audits, Automatic Retry Audits, Trust Promotion Audits, Promotion
  Decision Ledgers, Promotion Gate Checklists, Evidence Collection Plans,
  Approval Boundary Matrices, Proof Gap Indexes, Readiness Reviews, or
  Expansion Ledgers as a side effect, collect evidence automatically, approve
  capabilities automatically, promote capabilities automatically, promote
  trust automatically, retry or replay work automatically, track real spend
  automatically, generate proof artifacts, enable or deploy hosted dashboards,
  start remote workers, claim remote work, schedule autonomous work, operate
  browser or desktop adapters, run CI or deploys, enforce budgets, change
  routing, change claims, or mutate external systems.
- Browser Desktop Adapter Proof Checklist is report-only and must not create
  Autonomous Scheduling Proof Checklists, Remote Worker Proof Checklists,
  Hosted Dashboard Proof Checklists, Real Cost Tracking Audits, Automatic
  Retry Audits, Trust Promotion Audits, Promotion Decision Ledgers, Promotion
  Gate Checklists, Evidence Collection Plans, Approval Boundary Matrices,
  Proof Gap Indexes, Readiness Reviews, or Expansion Ledgers as a side effect,
  while preserving Real-Cost-sourced autonomous-scheduling proof metadata and
  the autonomous-scheduling source proof's own source metadata when present;
  it must not collect evidence automatically, approve capabilities
  automatically, promote capabilities automatically, promote trust
  automatically, retry or replay work automatically, track real spend
  automatically, generate proof artifacts, enable or deploy hosted dashboards,
  start remote workers, claim remote work, schedule autonomous work, operate
  browser or desktop adapters, run CI or deploys, enforce budgets, change
  routing, change claims, or mutate external systems.
- CI Deploy Proof Checklist is report-only and must not create Browser Desktop
  Adapter Proof Checklists, Autonomous Scheduling Proof Checklists, Remote
  Worker Proof Checklists, Hosted Dashboard Proof Checklists, Real Cost
  Tracking Audits, Automatic Retry Audits, Trust Promotion Audits, Promotion
  Decision Ledgers, Promotion Gate Checklists, Evidence Collection Plans,
  Approval Boundary Matrices, Proof Gap Indexes, Readiness Reviews, or
  Expansion Ledgers as a side effect, while preserving Real-Cost-sourced
  browser desktop adapter proof metadata when present; it must not collect
  evidence automatically, approve capabilities automatically, promote
  capabilities automatically, promote trust automatically, retry or replay work
  automatically, track real spend automatically, generate proof artifacts,
  enable or deploy hosted dashboards, start remote workers, claim remote work,
  schedule autonomous work, operate browser or desktop adapters, run CI or
  deploys, enforce budgets, change routing, change claims, or mutate external
  systems.
- Budget Enforcement Proof Checklist is report-only and must not create CI
  Deploy Proof Checklists, Browser Desktop Adapter Proof Checklists,
  Autonomous Scheduling Proof Checklists, Remote Worker Proof Checklists,
  Hosted Dashboard Proof Checklists, Real Cost Tracking Audits, Automatic
  Retry Audits, Trust Promotion Audits, Promotion Decision Ledgers, Promotion
  Gate Checklists, Evidence Collection Plans, Approval Boundary Matrices,
  Proof Gap Indexes, Readiness Reviews, or Expansion Ledgers as a side effect,
  while preferring the latest Real-Cost-sourced CI Deploy proof checklist when
  one exists and preserving CI Deploy proof metadata plus the CI Deploy source
  proof's own source metadata when available; it
  must not collect evidence automatically, approve capabilities automatically,
  promote capabilities automatically, promote trust automatically, retry or
  replay work automatically, track real spend automatically, generate proof
  artifacts, enable or deploy hosted dashboards, start remote workers, claim
  remote work, schedule autonomous work, operate browser or desktop adapters,
  run CI or deploys, enforce budgets, change routing, change claims, or mutate
  external systems.
- Trust Promotion Proof Checklist is report-only and must prefer the latest
  Real-Cost-sourced Budget Enforcement Proof Checklist when one exists; it
  must not create Budget
  Enforcement Proof Checklists, CI Deploy Proof Checklists, Browser Desktop
  Adapter Proof Checklists, Autonomous Scheduling Proof Checklists, Remote
  Worker Proof Checklists, Hosted Dashboard Proof Checklists, Real Cost
  Tracking Audits, Automatic Retry Audits, Trust Promotion Audits, Promotion
  Decision Ledgers, Promotion Gate Checklists, Evidence Collection Plans,
  Approval Boundary Matrices, Proof Gap Indexes, Readiness Reviews, or
  Expansion Ledgers as a side effect, while preserving Budget Enforcement
  proof metadata and the Budget Enforcement source proof's own source metadata
  when available; it must not collect evidence automatically, approve
  capabilities automatically, promote capabilities
  automatically, promote trust automatically, retry or replay work
  automatically, track real spend automatically, generate proof artifacts,
  enable or deploy hosted dashboards,
  start remote workers, claim remote work, schedule autonomous work, operate
  browser or desktop adapters, run CI or deploys, enforce budgets, change
  routing, change claims, or mutate external systems.
- Automatic Retry Proof Checklist is report-only and must preserve
  Real-Cost-sourced Trust Promotion proof metadata when present; it must not
  create Trust Promotion Proof Checklists, Budget Enforcement Proof
  Checklists, CI Deploy Proof Checklists, Browser Desktop Adapter Proof
  Checklists, Autonomous Scheduling Proof Checklists, Remote Worker Proof
  Checklists, Hosted Dashboard Proof Checklists, Real Cost Tracking Audits,
  Automatic Retry Audits, Trust Promotion Audits, Promotion Decision Ledgers,
  Promotion Gate Checklists, Evidence Collection Plans, Approval Boundary
  Matrices, Proof Gap Indexes, Readiness Reviews, or Expansion Ledgers as a
  side effect, collect evidence automatically, approve capabilities
  automatically, promote capabilities automatically, promote trust
  automatically, retry or replay work automatically, track real spend
  automatically, generate proof artifacts, enable or deploy hosted dashboards,
  start remote workers, claim remote work, schedule autonomous work, operate
  browser or desktop adapters, run CI or deploys, enforce budgets, change
  routing, change claims, or mutate external systems.
- Real Cost Tracking Proof Checklist is report-only and must not create
  Automatic Retry Proof Checklists, Trust Promotion Proof Checklists, Budget
  Enforcement Proof Checklists, CI Deploy Proof Checklists, Browser Desktop
  Adapter Proof Checklists, Autonomous Scheduling Proof Checklists, Remote
  Worker Proof Checklists, Hosted Dashboard Proof Checklists, Real Cost
  Tracking Audits, Automatic Retry Audits, Trust Promotion Audits, Promotion
  Decision Ledgers, Promotion Gate Checklists, Evidence Collection Plans,
  Approval Boundary Matrices, Proof Gap Indexes, Readiness Reviews, or
  Expansion Ledgers as a side effect, while preserving Real-Cost-sourced
  Automatic Retry proof metadata when present; it must not collect evidence
  automatically, approve capabilities automatically, promote capabilities
  automatically, promote trust automatically, retry or replay work
  automatically, track real spend automatically, generate proof artifacts,
  enable or deploy hosted dashboards, start remote workers, claim remote work,
  schedule autonomous work, operate browser or desktop adapters, run CI or
  deploys, enforce budgets, change routing, change claims, or mutate external
  systems.
- Graceful failure with recorded incidents or blocked state.

## Deferred Requirements

- Multi-worker and multi-machine orchestration.
- Browser and desktop workflow execution.
- Hosted dashboard and real-time streaming UI beyond the static markdown view.
- External service adapters for email, calendar, CRM, finance, and cloud.
- Trust promotion, budgets, configurable policy rules, and external approvals
  beyond static local defaults.
- Automatic prompt, skill, or playbook mutation from distilled learnings.
- Budget enforcement, spend accounting, trust-level promotion, and policy
  simulation.
