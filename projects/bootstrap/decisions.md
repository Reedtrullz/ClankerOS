# Bootstrap Decisions

## 2026-06-21: Local-First Python Harness

Use Python standard library plus SQLite for the first milestone because it keeps
the runtime portable, inspectable, and easy to verify without dependency setup.

## 2026-06-21: Non-Executing Iteration Packets

Use `python3 -m agent_os.cli iterate` to generate a scoped next-iteration
packet from live momentum queues. The loop plans and records the next pass but
does not execute it autonomously; implementation still requires a verified
agent turn with repo-state and Obsidian evidence.

## 2026-06-21: Report-Only Handoff Reviews

Use `python3 -m agent_os.cli handoff-review` to report blocked tasks and
handoffs that do not reference the current iteration packet. The review records
evidence and dashboard state only; it does not edit handoffs, resolve
incidents, or requeue tasks.

## 2026-06-21: Manual Eval-After-Change Evidence

Use `python3 -m agent_os.cli eval-after-change --change "<summary>" --file <path>`
to tie a harness behavior change to fresh local eval evidence. Keep this manual
and report-only until the system has real scheduling, file watching, CI, or
deploy policy rails.

## 2026-06-21: Report-Only Stable Learning Promotion

Use `python3 -m agent_os.cli distill-learnings --min-occurrences 3` to promote
repeated run learnings into root `knowledge.md` with SQLite and report
evidence. Keep promotion report-only: stable knowledge does not automatically
edit prompts, skills, playbooks, tasks, handoffs, approvals, schedulers, CI, or
deploy behavior.

## 2026-06-21: Report-Only Budget And Trust Posture

Use `python3 -m agent_os.cli budget-trust-posture` to record local dispatch
metadata posture before adding any budget enforcement or trust promotion. The
snapshot reports task count, risk counts, and explicit `not_tracked` states,
then mirrors the latest row in the dashboard without changing routing,
approval, claiming, retry, replay, scheduler, CI, deploy, or external behavior.

## 2026-06-21: Report-Only Dispatch Posture History

Use `python3 -m agent_os.cli dispatch-posture-history` to summarize recent
report-only budget/trust posture snapshots. The summary records snapshot count,
latest task count, task-count delta, latest risk counts, observed budget/trust
states, and report evidence without changing routing, approval, claiming,
budget enforcement, trust promotion, retry, replay, scheduler, CI, deploy, or
external behavior.

## 2026-06-21: Report-Only Dispatch Posture Snapshot Review

Use `python3 -m agent_os.cli dispatch-posture-staleness` to review recent
budget/trust posture snapshot freshness from SQLite timestamps. The review
records snapshot count, stale-snapshot count, latest snapshot age, threshold,
latest task count, latest risk counts, and report evidence without scheduling
refreshes, running posture reports automatically, changing routing, approval,
claiming, budget enforcement, trust promotion, retry, replay, scheduler, CI,
deploy, or external behavior.

## 2026-06-21: Report-Only Dispatch Posture Refresh Recommendation

Use `python3 -m agent_os.cli dispatch-posture-refresh` to convert the latest
persisted staleness review into manual refresh guidance. The recommendation
records source review id/status, snapshot counts, latest snapshot age,
threshold, manual commands, approval boundary, deferred-capability context, and
report evidence without running commands, creating input posture reports,
scheduling refreshes, changing routing, approval, claiming, budget
enforcement, trust promotion, retry, replay, scheduler, CI, deploy, hosted
dashboard, remote worker, browser/desktop adapter, cost tracking, or external
behavior.

## 2026-06-21: Report-Only Capability Expansion Ledger

Use `python3 -m agent_os.cli capability-expansion-ledger` to inventory deferred
autonomy surfaces before enabling them. The ledger records hosted dashboard,
remote workers, autonomous scheduling, browser/desktop adapters, CI/deploy
proof, budget enforcement, trust promotion, automatic retries, and real cost
tracking with required evidence, next proof, approval boundary, and
`routing_effect=none`, without activating those capabilities or changing
routing, approval, claiming, retry, replay, scheduler, CI, deploy, cost, or
external behavior.

## 2026-06-21: Report-Only Capability Readiness Review

Use `python3 -m agent_os.cli capability-readiness-review` to review the latest
persisted Capability Expansion Ledger for attached evidence before promoting
any deferred capability. The review records source ledger id/status, readiness
counts, missing evidence counts, recommended manual commands, approval
boundary, and per-capability evidence state without creating ledgers as a side
effect or changing routing, approval, claiming, retry, replay, scheduler, CI,
deploy, budget, trust, cost, or external behavior.

## 2026-06-21: Report-Only Capability Proof Gap Index

Use `python3 -m agent_os.cli capability-proof-gap-index` to index open proof
gaps from the latest persisted Capability Readiness Review. The index records
source review id/status, gap counts, missing evidence counts, blocked
capability counts, next proof counts, approval boundary, and per-capability
proof gaps without creating readiness reviews or ledgers as a side effect,
generating proof artifacts, or changing routing, approval, claiming, retry,
replay, scheduler, CI, deploy, budget, trust, cost, or external behavior.

## 2026-06-21: Report-Only Capability Approval Boundary Matrix

Use `python3 -m agent_os.cli capability-approval-boundary-matrix` to map open
proof gaps from the latest persisted Capability Proof Gap Index to explicit
operator approval boundaries. The matrix records source index id/status,
boundary counts, gap counts, blocked capability counts, approval-required
counts, boundary rows, and per-capability decision states without creating
proof-gap indexes, readiness reviews, or ledgers as a side effect, approving
capabilities, generating proof artifacts, or changing routing, approval,
claiming, retry, replay, scheduler, CI, deploy, budget, trust, cost, or
external behavior.

## 2026-06-21: Report-Only Capability Evidence Collection Plan

Use `python3 -m agent_os.cli capability-evidence-collection-plan` to plan
manual proof evidence from the latest persisted Capability Approval Boundary
Matrix. The plan records source matrix id/status, evidence item counts, manual
collection counts, approval-required counts, boundary counts, recommended
manual commands, and per-capability evidence items without collecting
evidence, creating upstream matrices/indexes/reviews/ledgers as a side effect,
approving capabilities, generating proof artifacts, or changing routing,
approval, claiming, retry, replay, scheduler, CI, deploy, budget, trust, cost,
or external behavior.

## 2026-06-21: Report-Only Capability Promotion Gate Checklist

Use `python3 -m agent_os.cli capability-promotion-gate-checklist` to review
promotion gates from the latest persisted Capability Evidence Collection Plan.
The checklist records source plan id/status, gate counts, blocked-promotion
counts, missing-evidence counts, approval-required counts, boundary counts,
recommended manual commands, and per-capability gate state without collecting
evidence, creating upstream plans/matrices/indexes/reviews/ledgers as a side
effect, approving capabilities, promoting capabilities, generating proof
artifacts, or changing routing, approval, claiming, retry, replay, scheduler,
CI, deploy, budget, trust, cost, or external behavior.

## 2026-06-21: Report-Only Capability Promotion Decision Ledger

Use `python3 -m agent_os.cli capability-promotion-decision-ledger` to record
report-only defer/manual-review decisions from the latest persisted Capability
Promotion Gate Checklist. The ledger records source checklist id/status,
decision counts, deferred-promotion counts, operator-decision-required counts,
blocked-promotion counts, missing-evidence counts, approval-required counts,
boundary counts, recommended manual commands, and per-capability decision state
without creating upstream checklists/plans/matrices/indexes/reviews/ledgers as
a side effect, collecting evidence, approving capabilities, promoting
capabilities, generating proof artifacts, or changing routing, approval,
claiming, retry, replay, scheduler, CI, deploy, budget, trust, cost, or
external behavior.

## 2026-06-21: Report-Only Capability Trust Promotion Audit

Use `python3 -m agent_os.cli capability-trust-promotion-audit` to audit
trust-promotion readiness from the latest persisted Capability Promotion
Decision Ledger. The audit records source ledger id/status, audit counts,
blocked-trust-promotion counts, operator-review-required counts,
deferred-promotion counts, missing-evidence counts, approval-required counts,
boundary counts, recommended manual commands, and per-capability trust action
without creating upstream ledgers/checklists/plans/matrices/indexes/reviews as a
side effect, collecting evidence, approving capabilities, promoting
capabilities, promoting trust, generating proof artifacts, or changing routing,
approval, claiming, retry, replay, scheduler, CI, deploy, budget, trust, cost,
or external behavior.

## 2026-06-21: Report-Only Capability Automatic Retry Audit

Use `python3 -m agent_os.cli capability-automatic-retry-audit` to audit
automatic-retry readiness from the latest persisted Capability Trust Promotion
Audit. The audit records source audit id/status, audit counts,
blocked-retry counts, operator-review-required counts,
blocked-trust-promotion counts, deferred-promotion counts, missing-evidence
counts, approval-required counts, boundary counts, recommended manual commands,
and per-capability retry action without creating upstream audits/ledgers/
checklists/plans/matrices/indexes/reviews as a side effect, collecting
evidence, approving capabilities, promoting capabilities, promoting trust,
retrying or replaying work, generating proof artifacts, or changing routing,
approval, claiming, scheduler, CI, deploy, budget, trust, cost, or external
behavior.

## 2026-06-21: Report-Only Capability Real Cost Tracking Audit

Use `python3 -m agent_os.cli capability-real-cost-tracking-audit` to audit
real-cost-tracking readiness from the latest persisted Capability Automatic
Retry Audit. The audit records source audit id/status, audit counts,
blocked-cost-tracking counts, operator-review-required counts,
blocked-retry counts, blocked-trust-promotion counts, deferred-promotion
counts, missing-evidence counts, approval-required counts, boundary counts,
recommended manual commands, and per-capability cost action without creating
upstream audits/ledgers/checklists/plans/matrices/indexes/reviews as a side
effect, collecting evidence, approving capabilities, promoting capabilities,
promoting trust, retrying or replaying work, tracking real spend, generating
proof artifacts, enforcing budgets, or changing routing, approval, claiming,
scheduler, CI, deploy, trust, cost, or external behavior.

## 2026-06-21: Report-Only Hosted Dashboard Proof Checklist

Use `python3 -m agent_os.cli hosted-dashboard-proof-checklist` to check
hosted-dashboard proof readiness from the latest persisted Real Cost Tracking
Proof Checklist, falling back to the legacy Capability Real Cost Tracking
Audit when no proof checklist exists. The checklist records source kind, source
proof checklist/audit id/status, checklist counts, blocked-dashboard-proof
counts, operator-review-required counts, blocked-cost-tracking counts,
blocked-retry counts,
blocked-trust-promotion counts, missing-evidence counts,
approval-required counts, boundary counts, recommended manual commands, and a
single hosted-dashboard checklist item without creating upstream audits/
ledgers/checklists/plans/matrices/indexes/reviews as a side effect, collecting
evidence, approving capabilities, promoting capabilities, promoting trust,
retrying or replaying work, tracking real spend, generating proof artifacts,
enabling or deploying hosted dashboards, enforcing budgets, or changing
routing, approval, claiming, scheduler, CI, deploy, trust, cost, or external
behavior.

## 2026-06-22: Report-Only Remote Worker Proof Checklist

Use `python3 -m agent_os.cli remote-worker-proof-checklist` to check
remote-worker proof readiness from the latest persisted Hosted Dashboard Proof
Checklist. The checklist records source checklist id/status, checklist counts,
blocked-worker-proof counts, operator-review-required counts,
blocked-dashboard-proof counts, blocked-cost-tracking counts, blocked-retry
counts, blocked-trust-promotion counts, Real-Cost-sourced hosted-dashboard
proof metadata when present, missing-evidence counts, approval-required
counts, boundary counts, recommended manual commands, and a single
remote-worker checklist item without creating upstream checklists/audits/
ledgers/plans/matrices/indexes/reviews as a side effect, collecting evidence,
approving capabilities, promoting capabilities, promoting trust, retrying or
replaying work, tracking real spend, generating proof artifacts, enabling or
deploying hosted dashboards, starting or claiming remote work, enforcing
budgets, or changing routing, approval, claiming, scheduler, CI, deploy,
trust, cost, or external behavior.

## 2026-06-22: Report-Only Autonomous Scheduling Proof Checklist

Use `python3 -m agent_os.cli autonomous-scheduling-proof-checklist` to check
autonomous-scheduling proof readiness from the latest persisted Remote Worker
Proof Checklist. The checklist records source checklist id/status, checklist
counts, blocked-scheduling-proof counts, operator-review-required counts,
blocked-worker-proof counts, blocked-dashboard-proof counts,
blocked-cost-tracking counts, blocked-retry counts,
blocked-trust-promotion counts, missing-evidence counts,
approval-required counts, boundary counts, recommended manual commands, and a
single autonomous-scheduling checklist item without creating upstream
checklists/audits/ledgers/plans/matrices/indexes/reviews as a side effect,
collecting evidence, approving capabilities, promoting capabilities,
promoting trust, retrying or replaying work, tracking real spend, generating
proof artifacts, enabling or deploying hosted dashboards, starting or claiming
remote work, scheduling autonomous work, operating browser or desktop
adapters, enforcing budgets, or changing routing, approval, claiming,
scheduler, CI, deploy, trust, cost, or external behavior.

## 2026-06-22: Real-Cost-Sourced Autonomous Scheduling Proof Checklist

When the latest Remote Worker Proof Checklist is sourced from a
Real-Cost-sourced Hosted Dashboard proof chain, the Autonomous Scheduling
Proof Checklist preserves that upstream proof metadata in its checklist item
and exposes the remote-worker checklist's own source checklist id/status in
the generated report. This keeps the downstream Browser/Desktop Adapter proof
rung from losing why scheduling remains disabled, without creating upstream
checklists, scheduling autonomous work, starting or claiming remote work,
operating adapters, running CI/deploys, enforcing budgets, tracking spend,
changing routing, approving capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Remote Worker Proof Checklist

When the latest Hosted Dashboard Proof Checklist is sourced from a
Real-Cost-sourced Real Cost Tracking proof chain, the Remote Worker Proof
Checklist should preserve that proof chain in the remote-worker checklist item
and expose both the hosted-dashboard source checklist id/status and that source
proof's own source checklist id/status in the generated report. This keeps the
next Autonomous Scheduling proof rung from losing why remote workers remain
disabled, without creating upstream checklists, starting or claiming remote
work, enabling hosted dashboards, scheduling autonomous work, operating
adapters, running CI/deploys, enforcing budgets, tracking spend, changing
routing, approving capabilities, or mutating external systems.

## 2026-06-22: Report-Only Browser Desktop Adapter Proof Checklist

Use `python3 -m agent_os.cli browser-desktop-adapter-proof-checklist` to check
browser/desktop adapter proof readiness from the latest persisted Autonomous
Scheduling Proof Checklist. The checklist records source checklist id/status,
checklist counts, blocked-adapter-proof counts, operator-review-required
counts, blocked-scheduling-proof counts, blocked-worker-proof counts,
blocked-dashboard-proof counts, blocked-cost-tracking counts,
blocked-retry counts, blocked-trust-promotion counts, missing-evidence counts,
approval-required counts, boundary counts, recommended manual commands, and a
single browser/desktop adapter checklist item without creating upstream
checklists/audits/ledgers/plans/matrices/indexes/reviews as a side effect,
collecting evidence, approving capabilities, promoting capabilities,
promoting trust, retrying or replaying work, tracking real spend, generating
proof artifacts, enabling or deploying hosted dashboards, starting or claiming
remote work, scheduling autonomous work, operating browser or desktop
adapters, enforcing budgets, or changing routing, approval, claiming,
scheduler, CI, deploy, trust, cost, or external behavior.

## 2026-06-22: Real-Cost-Sourced Browser Desktop Adapter Proof Checklist

When the latest Autonomous Scheduling Proof Checklist is sourced from a
Real-Cost-sourced Remote Worker proof chain, the Browser/Desktop Adapter Proof
Checklist preserves that upstream proof metadata in its checklist item and
exposes the autonomous-scheduling checklist's own source checklist id/status
in the generated report. This keeps the downstream CI Deploy proof rung from
losing why adapter operation remains disabled, without creating upstream
checklists, operating browser/desktop adapters, scheduling autonomous work,
starting or claiming remote work, running CI/deploys, enforcing budgets,
tracking spend, changing routing, approving capabilities, or mutating
external systems.

## 2026-06-22: Report-Only CI Deploy Proof Checklist

Use `python3 -m agent_os.cli ci-deploy-proof-checklist` to check CI Deploy
proof readiness from the latest persisted Browser Desktop Adapter Proof
Checklist. The checklist records source checklist id/status, checklist counts,
blocked-CI-Deploy-proof counts, operator-review-required counts,
blocked-adapter-proof counts, blocked-scheduling-proof counts,
blocked-worker-proof counts, blocked-dashboard-proof counts,
blocked-cost-tracking counts, blocked-retry counts,
blocked-trust-promotion counts, missing-evidence counts,
approval-required counts, boundary counts, recommended manual commands, and a
single CI Deploy proof checklist item without creating upstream
checklists/audits/ledgers/plans/matrices/indexes/reviews as a side effect,
collecting evidence, approving capabilities, promoting capabilities,
promoting trust, retrying or replaying work, tracking real spend, generating
proof artifacts, enabling or deploying hosted dashboards, starting or claiming
remote work, scheduling autonomous work, operating browser or desktop
adapters, running CI or deploys, enforcing budgets, or changing routing,
approval, claiming, scheduler, CI, deploy, trust, cost, or external behavior.

## 2026-06-22: Real-Cost-Sourced CI Deploy Proof Checklist

When the latest Browser Desktop Adapter Proof Checklist is sourced from a
Real-Cost-sourced Autonomous Scheduling proof chain, the CI Deploy Proof
Checklist preserves that upstream proof metadata in its checklist item and
exposes the browser/desktop adapter checklist's own source checklist id/status
in the generated report. This keeps the downstream Budget Enforcement proof
rung from losing why CI/deploy remains disabled, without creating upstream
checklists, running CI/deploys, operating browser/desktop adapters, scheduling
autonomous work, starting or claiming remote work, enforcing budgets, tracking
spend, changing routing, approving capabilities, or mutating external systems.

## 2026-06-22: Report-Only Budget Enforcement Proof Checklist

Use `python3 -m agent_os.cli budget-enforcement-proof-checklist` to check
Budget Enforcement proof readiness from the latest persisted CI Deploy Proof
Checklist. The checklist records source checklist id/status, checklist counts,
blocked-budget-enforcement-proof counts, operator-review-required counts,
blocked-CI-Deploy-proof counts, blocked-adapter-proof counts,
blocked-scheduling-proof counts, blocked-worker-proof counts,
blocked-dashboard-proof counts, blocked-cost-tracking counts,
blocked-retry counts, blocked-trust-promotion counts, missing-evidence
counts, approval-required counts, boundary counts, recommended manual
commands, and a single Budget Enforcement proof checklist item without
creating upstream checklists/audits/ledgers/plans/matrices/indexes/reviews as
a side effect, collecting evidence, approving capabilities, promoting
capabilities, promoting trust, retrying or replaying work, tracking real
spend, generating proof artifacts, enabling or deploying hosted dashboards,
starting or claiming remote work, scheduling autonomous work, operating
browser or desktop adapters, running CI or deploys, enforcing budgets, or
changing routing, approval, claiming, scheduler, CI, deploy, trust, cost, or
external behavior.

## 2026-06-22: Real-Cost-Sourced Budget Enforcement Proof Checklist

When the latest CI Deploy Proof Checklist is sourced from a Real-Cost-sourced
Browser/Desktop Adapter proof chain, the Budget Enforcement Proof Checklist
preserves that upstream proof metadata in its checklist item and exposes the
CI Deploy checklist's own source checklist id/status in the generated report.
This keeps the downstream Trust Promotion proof rung from losing why budget
enforcement remains disabled, without creating upstream checklists, enforcing
budgets, running CI/deploys, operating adapters, scheduling autonomous work,
starting or claiming remote work, tracking spend, changing routing, approving
capabilities, or mutating external systems.

## 2026-06-22: Report-Only Trust Promotion Proof Checklist

Use `python3 -m agent_os.cli trust-promotion-proof-checklist` to check Trust
Promotion proof readiness from the latest persisted Budget Enforcement Proof
Checklist. The checklist records source checklist id/status, checklist counts,
blocked-trust-promotion-proof counts, operator-review-required counts,
blocked-budget-enforcement-proof counts, blocked-CI-Deploy-proof counts,
blocked-adapter-proof counts, blocked-scheduling-proof counts,
blocked-worker-proof counts, blocked-dashboard-proof counts,
blocked-cost-tracking counts, blocked-retry counts,
blocked-trust-promotion counts, missing-evidence counts,
approval-required counts, boundary counts, recommended manual commands, and a
single Trust Promotion proof checklist item without creating upstream
checklists/audits/ledgers/plans/matrices/indexes/reviews as a side effect,
collecting evidence, approving capabilities, promoting capabilities,
promoting trust, retrying or replaying work, tracking real spend, generating
proof artifacts, enabling or deploying hosted dashboards, starting or claiming
remote work, scheduling autonomous work, operating browser or desktop
adapters, running CI or deploys, enforcing budgets, or changing routing,
approval, claiming, scheduler, CI, deploy, trust, cost, or external behavior.

## 2026-06-22: Real-Cost-Sourced Trust Promotion Proof Checklist

When the latest Budget Enforcement Proof Checklist is sourced from a
Real-Cost-sourced CI Deploy proof chain, the Trust Promotion Proof Checklist
preserves that upstream proof metadata in its checklist item and exposes the
Budget Enforcement checklist's own source checklist id/status in the generated
report. This keeps the downstream Automatic Retry proof rung from losing why
trust promotion remains disabled, without creating upstream checklists,
promoting trust, enforcing budgets, running CI/deploys, operating adapters,
scheduling autonomous work, starting or claiming remote work, tracking spend,
changing routing, approving capabilities, or mutating external systems.

## 2026-06-22: Report-Only Automatic Retry Proof Checklist

Use `python3 -m agent_os.cli automatic-retry-proof-checklist` to check
Automatic Retry proof readiness from the latest persisted Trust Promotion
Proof Checklist. The checklist records source checklist id/status, checklist
counts, blocked-automatic-retry-proof counts, operator-review-required counts,
blocked-trust-promotion-proof counts, blocked-budget-enforcement-proof counts,
blocked-CI-Deploy-proof counts, blocked-adapter-proof counts,
blocked-scheduling-proof counts, blocked-worker-proof counts,
blocked-dashboard-proof counts, blocked-cost-tracking counts,
blocked-retry counts, blocked-trust-promotion counts, missing-evidence
counts, approval-required counts, boundary counts, recommended manual
commands, and a single Automatic Retry proof checklist item without creating
upstream checklists/audits/ledgers/plans/matrices/indexes/reviews as a side
effect, collecting evidence, approving capabilities, promoting capabilities,
promoting trust, retrying or replaying work, tracking real spend, generating
proof artifacts, enabling or deploying hosted dashboards, starting or claiming
remote work, scheduling autonomous work, operating browser or desktop
adapters, running CI or deploys, enforcing budgets, or changing routing,
approval, claiming, scheduler, CI, deploy, trust, cost, or external behavior.

## 2026-06-22: Real-Cost-Sourced Automatic Retry Proof Checklist

When the latest Trust Promotion Proof Checklist is sourced from a
Real-Cost-sourced Budget Enforcement proof chain, the Automatic Retry Proof
Checklist preserves that upstream proof metadata in its checklist item and
exposes the Trust Promotion checklist's own source checklist id/status in the
generated report. This keeps the downstream Real Cost Tracking proof rung from
losing why automatic retries remain disabled, without creating upstream
checklists, retrying/replaying work, promoting trust, enforcing budgets,
running CI/deploys, operating adapters, scheduling autonomous work, starting
or claiming remote work, tracking spend, changing routing, approving
capabilities, or mutating external systems.

## 2026-06-22: Report-Only Real Cost Tracking Proof Checklist

Use `python3 -m agent_os.cli real-cost-tracking-proof-checklist` to check Real
Cost Tracking proof readiness from the latest persisted Automatic Retry Proof
Checklist. The checklist records source checklist id/status, checklist counts,
blocked-real-cost-tracking-proof counts, operator-review-required counts,
blocked-automatic-retry-proof counts, blocked-trust-promotion-proof counts,
blocked-budget-enforcement-proof counts, blocked-CI-Deploy-proof counts,
blocked-adapter-proof counts, blocked-scheduling-proof counts,
blocked-worker-proof counts, blocked-dashboard-proof counts,
blocked-cost-tracking counts, blocked-retry counts,
blocked-trust-promotion counts, missing-evidence counts, approval-required
counts, boundary counts, recommended manual commands, and a single Real Cost
Tracking proof checklist item without creating upstream checklists/audits/
ledgers/plans/matrices/indexes/reviews as a side effect, collecting evidence,
approving capabilities, promoting capabilities, promoting trust, retrying or
replaying work, tracking real spend, generating proof artifacts, enabling or
deploying hosted dashboards, starting or claiming remote work, scheduling
autonomous work, operating browser or desktop adapters, running CI/deploys,
enforcing budgets, or changing routing, approval, claiming, scheduler, CI,
deploy, trust, cost, or external behavior.

## 2026-06-22: Real-Cost-Sourced Real Cost Tracking Proof Checklist

When the latest Automatic Retry Proof Checklist is sourced from a
Real-Cost-sourced Trust Promotion proof chain, the Real Cost Tracking Proof
Checklist preserves that upstream proof metadata in its checklist item and
exposes the Automatic Retry checklist's own source checklist id/status in the
generated report. This keeps the downstream Hosted Dashboard proof rung from
losing why spend tracking remains disabled, without creating upstream
checklists, tracking spend, retrying/replaying work, promoting trust,
enforcing budgets, running CI/deploys, operating adapters, scheduling
autonomous work, starting or claiming remote work, changing routing, approving
capabilities, or mutating external systems.

## 2026-06-22: Real-Cost-Sourced Hosted Dashboard Proof Checklist

When the latest Real Cost Tracking Proof Checklist is sourced from a
Real-Cost-sourced Automatic Retry proof chain, the Hosted Dashboard Proof
Checklist preserves that upstream proof metadata in its checklist item and
exposes the Real Cost Tracking checklist's own source checklist id/status in
the generated report. This keeps the downstream Remote Worker proof rung from
losing why hosted dashboard deployment remains disabled, without creating
upstream checklists, enabling or deploying hosted dashboards, tracking spend,
retrying/replaying work, promoting trust, enforcing budgets, running
CI/deploys, operating adapters, scheduling autonomous work, starting or
claiming remote work, changing routing, approving capabilities, or mutating
external systems.

## 2026-06-22: Latest Real-Cost-Sourced Autonomous Scheduling Proof Checklist

When checking Autonomous Scheduling proof readiness, prefer the latest
Real-Cost-sourced Remote Worker proof checklist when one exists instead of
blindly selecting the newest Remote Worker row. The generated report should
retain the Remote Worker source Hosted Dashboard proof id/status, the Hosted
Dashboard source Real Cost Tracking proof id/status, and the Real Cost
Tracking source Automatic Retry proof id/status when available. This keeps the
downstream Browser/Desktop Adapter proof rung from losing the cost/retry proof
chain, without scheduling autonomous work, starting or claiming remote work,
operating browser or desktop adapters, changing routing, approving
capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Browser Desktop Adapter Proof Checklist

When checking Browser/Desktop Adapter proof readiness, prefer the latest
Real-Cost-sourced Autonomous Scheduling proof checklist when one exists
instead of blindly selecting the newest Autonomous Scheduling row. Newer
legacy Autonomous Scheduling rows and dangling Autonomous Scheduling rows
without retrievable Remote Worker, Hosted Dashboard, Real Cost Tracking, and
Automatic Retry proof sources should not hide the stronger proof chain. The
generated report should retain the Autonomous Scheduling source Remote Worker
proof id/status, the Remote Worker source Hosted Dashboard proof id/status,
the Hosted Dashboard source Real Cost Tracking proof id/status, and the Real
Cost Tracking source Automatic Retry proof id/status when available. This
keeps the downstream CI Deploy proof rung from losing the cost/retry proof
chain, without operating browser or desktop adapters, scheduling autonomous
work, running CI/deploys, changing routing, approving capabilities, or
mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced CI Deploy Proof Checklist

When checking CI Deploy proof readiness, prefer the latest Real-Cost-sourced
Browser/Desktop Adapter proof checklist when one exists instead of blindly
selecting the newest Browser/Desktop Adapter row. Scan all local
Browser/Desktop Adapter proof rows; skip newer legacy rows; and report
dangling Browser/Desktop Adapter rows without retrievable Autonomous
Scheduling, Remote Worker, Hosted Dashboard, Real Cost Tracking, and Automatic
Retry proof sources as missing proof instead of valid CI Deploy blockers. The
generated report should retain the Browser/Desktop Adapter source Autonomous
Scheduling proof id/status, the Autonomous Scheduling source Remote Worker
proof id/status, the Remote Worker source Hosted Dashboard proof id/status,
the Hosted Dashboard source Real Cost Tracking proof id/status, and the Real
Cost Tracking source Automatic Retry proof id/status when available. This
keeps the downstream Budget Enforcement proof rung from losing the cost/retry
proof chain, without running CI/deploys, operating browser or desktop
adapters, scheduling autonomous work, changing routing, approving
capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Budget Enforcement Proof Checklist

When checking Budget Enforcement proof readiness, prefer the latest
Real-Cost-sourced CI Deploy proof checklist when one exists instead of blindly
selecting the newest CI Deploy row. Scan all local CI Deploy proof rows; skip
newer legacy rows; and report dangling CI Deploy rows without retrievable
Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
Dashboard, Real Cost Tracking, and Automatic Retry proof sources as missing
proof instead of valid Budget Enforcement blockers. The generated report
should retain the CI Deploy source Browser/Desktop Adapter proof id/status,
the Browser/Desktop Adapter source Autonomous Scheduling proof id/status, the
Autonomous Scheduling source Remote Worker proof id/status, the Remote Worker
source Hosted Dashboard proof id/status, the Hosted Dashboard source Real Cost
Tracking proof id/status, and the Real Cost Tracking source Automatic Retry
proof id/status when available. This keeps the downstream Trust Promotion
proof rung from losing the cost/retry proof chain, without enforcing budgets,
running CI/deploys, operating adapters, scheduling autonomous work, changing
routing, approving capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Trust Promotion Proof Checklist

When checking Trust Promotion proof readiness, prefer the latest
Real-Cost-sourced Budget Enforcement proof checklist when one exists instead
of blindly selecting the newest Budget Enforcement row. Scan all local Budget
Enforcement proof rows; skip newer legacy rows; and report dangling Budget
Enforcement rows without retrievable CI Deploy, Browser/Desktop Adapter,
Autonomous Scheduling, Remote Worker, Hosted Dashboard, Real Cost Tracking,
and Automatic Retry proof sources as missing proof instead of valid Trust
Promotion blockers. The generated report should retain the Budget Enforcement
source CI Deploy proof id/status, the CI Deploy source Browser/Desktop Adapter
proof id/status, the Browser/Desktop Adapter source Autonomous Scheduling
proof id/status, the Autonomous Scheduling source Remote Worker proof
id/status, the Remote Worker source Hosted Dashboard proof id/status, the
Hosted Dashboard source Real Cost Tracking proof id/status, and the Real Cost
Tracking source Automatic Retry proof id/status when available. This keeps the
downstream Automatic Retry proof rung from losing the cost/retry proof chain,
without promoting trust, enforcing budgets, running CI/deploys, operating
adapters, scheduling autonomous work, retrying/replaying work, tracking spend,
changing routing, approving capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Automatic Retry Proof Checklist

When checking Automatic Retry proof readiness, prefer the latest
Real-Cost-sourced Trust Promotion proof checklist when one exists instead of
blindly selecting the newest Trust Promotion row. Newer legacy Trust Promotion
rows and dangling Trust Promotion rows without retrievable Budget Enforcement,
CI Deploy, Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker,
Hosted Dashboard, Real Cost Tracking, and Automatic Retry proof sources should
be skipped or reported as missing upstream proof rather than accepted as valid
Automatic Retry blockers. The generated report should
retain the Trust Promotion source Budget Enforcement proof id/status, the
Budget Enforcement source CI Deploy proof id/status, the CI Deploy source
Browser/Desktop Adapter proof id/status, the Browser/Desktop Adapter source
Autonomous Scheduling proof id/status, the Autonomous Scheduling source Remote
Worker proof id/status, the Remote Worker source Hosted Dashboard proof
id/status, the Hosted Dashboard source Real Cost Tracking proof id/status, and
the Real Cost Tracking source Automatic Retry proof id/status when available.
This keeps the downstream Real Cost Tracking proof rung from losing the
cost/retry proof chain, without retrying/replaying work, promoting trust,
enforcing budgets, running CI/deploys, operating adapters, scheduling
autonomous work, tracking spend, changing routing, approving capabilities, or
mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Real Cost Tracking Proof Checklist

When checking Real Cost Tracking proof readiness, prefer the latest
Real-Cost-sourced Automatic Retry proof checklist when one exists instead of
blindly selecting the newest Automatic Retry row. The generated report should
retain the Automatic Retry source Trust Promotion proof id/status, the Trust
Promotion source Budget Enforcement proof id/status, the Budget Enforcement
source CI Deploy proof id/status, the CI Deploy source Browser/Desktop Adapter
proof id/status, the Browser/Desktop Adapter source Autonomous Scheduling proof
id/status, the Autonomous Scheduling source Remote Worker proof id/status, the
Remote Worker source Hosted Dashboard proof id/status, the Hosted Dashboard
source Real Cost Tracking proof id/status, and the source Real Cost Tracking
proof's Automatic Retry source id/status when available. This keeps the
downstream Hosted Dashboard proof rung from losing the cost/retry proof chain,
without tracking spend, retrying/replaying work, promoting trust, enforcing
budgets, running CI/deploys, operating adapters, scheduling autonomous work,
changing routing, approving capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Hosted Dashboard Proof Checklist

When checking Hosted Dashboard proof readiness, prefer the latest
Real-Cost-sourced Real Cost Tracking proof checklist when one exists instead of
blindly selecting the newest Real Cost Tracking row. The generated report
should retain the Real Cost Tracking source Automatic Retry proof id/status,
Automatic Retry source Trust Promotion proof id/status, Trust Promotion source
Budget Enforcement proof id/status, Budget Enforcement source CI Deploy proof
id/status, CI Deploy source Browser/Desktop Adapter proof id/status,
Browser/Desktop Adapter source Autonomous Scheduling proof id/status,
Autonomous Scheduling source Remote Worker proof id/status, Remote Worker
source Hosted Dashboard proof id/status, Hosted Dashboard source Real Cost
Tracking proof id/status, and that source Real Cost Tracking proof's Automatic
Retry source id/status when available. Dangling Real Cost Tracking proof rows
without an upstream Automatic Retry proof source should be treated as missing
upstream proof, not as a valid Hosted Dashboard blocker. This keeps the
downstream Remote Worker proof rung from losing the cost/retry proof chain,
without enabling or deploying hosted dashboards, tracking spend,
retrying/replaying work, promoting trust, enforcing budgets, running
CI/deploys, operating adapters, scheduling autonomous work, changing routing,
approving capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Remote Worker Proof Checklist, Second Pass

When checking Remote Worker proof readiness, prefer the latest
Real-Cost-sourced Hosted Dashboard proof checklist when one exists instead of
blindly selecting the newest Hosted Dashboard row. Newer legacy Hosted
Dashboard rows and dangling Hosted Dashboard rows without retrievable Real
Cost Tracking and Automatic Retry proof sources should not hide the stronger
proof chain. This keeps the downstream Autonomous Scheduling proof rung from
losing the hosted-dashboard, cost, and retry proof chain, without starting
remote workers, claiming remote work, scheduling autonomous work, changing
routing, approving capabilities, or mutating external systems.

## 2026-06-22: Latest Real-Cost-Sourced Autonomous Scheduling Proof Checklist, Second Pass

When checking Autonomous Scheduling proof readiness, prefer the latest
Real-Cost-sourced Remote Worker proof checklist when one exists instead of
blindly selecting the newest Remote Worker row. Newer legacy Remote Worker
rows and dangling Remote Worker rows without retrievable Hosted Dashboard,
Real Cost Tracking, and Automatic Retry proof sources should not hide the
stronger proof chain. This keeps the downstream Browser/Desktop Adapter proof
rung from losing the remote-worker, hosted-dashboard, cost, and retry proof
chain, without scheduling autonomous work, starting remote workers, claiming
remote work, operating adapters, changing routing, approving capabilities, or
mutating external systems.

## 2026-06-22: Report-Only Goal Completion Audit

Use `python3 -m agent_os.cli goal-completion-audit` to audit the expansion
goal against the latest local proof-checklist rows before making any completion
claim. The audit records requirement counts, blocked report-only requirements,
missing evidence, approvals, external decisions, recommended commands, and
explicit non-claims. It does not mark goals complete, approve capabilities,
collect evidence, deploy hosted dashboards, start remote workers, schedule
autonomous work, operate adapters, run CI/deploys, enforce budgets, promote
trust, retry or replay work, track real spend, change routing, or mutate
external systems.

## 2026-06-22: Report-Only Expansion Decision Evidence Index

Use `python3 -m agent_os.cli expansion-decision-evidence-index` after
`expansion-decision-brief` to link each operator decision item to its local
evidence path. External decisions should point to blocked queue evidence in
`tasks.md`; capability approval decisions should point to the proof-checklist
report path named by the source goal completion audit. The index is an
operator-review aid only: it does not approve decisions, collect evidence,
complete the active goal, enable hosted dashboards, start remote workers,
schedule autonomous work, operate adapters, run CI/deploys, enforce budgets,
promote trust, retry/replay work, track real spend, change routing, or mutate
external systems.

## 2026-06-22: Report-Only Expansion Operator Review Checklist

Use `python3 -m agent_os.cli expansion-operator-review-checklist` after
`expansion-decision-evidence-index` to prepare the manual operator choices for
each decision item. The checklist should retain source index, source brief,
source audit, evidence path, and approval boundary; expose allowed manual
actions `approve`, `defer`, and `request_more_evidence`; and keep all items in
`operator_review_required` posture until an operator acts through a separate
approved flow. The checklist is not itself an approval ledger: it does not
approve decisions, collect evidence, complete the active goal, enable hosted
dashboards, start remote workers, schedule autonomous work, operate adapters,
run CI/deploys, enforce budgets, promote trust, retry/replay work, track real
spend, change routing, or mutate external systems.

## 2026-06-22: Report-Only Expansion Operator Decision Ledger

Use `python3 -m agent_os.cli expansion-operator-decision-ledger` after
`expansion-operator-review-checklist` to persist pending/manual operator
decision rows from the latest review checklist. The ledger should retain the
source checklist, evidence index, decision brief, goal audit, evidence paths,
allowed actions, and external/capability decision counts. Allowed actions are
not actions taken: all rows remain `pending_operator_decision` with
`selected_action=pending` until a separate approved flow records an operator
choice. The ledger does not approve decisions, collect evidence, complete the
active goal, enable hosted dashboards, start remote workers, schedule
autonomous work, operate adapters, run CI/deploys, enforce budgets, promote
trust, retry/replay work, track real spend, change routing, or mutate external
systems.

## 2026-06-22: Report-Only Expansion Operator Approval Draft

Use `python3 -m agent_os.cli expansion-operator-approval-draft` after
`expansion-operator-decision-ledger` to prepare draft-only approval-request
packet rows from a usable pending decision ledger. Draft items remain
`draft_only`, approval request status remains `not_created`, and
`created_approval_requests` must stay `0`; if the latest ledger is missing,
not `pending_operator_decisions`, or has no pending decisions, the draft must
report `operator_decision_ledger_not_ready` instead of pretending an approval
packet is ready. The real approval flow remains separate. This draft does not
create `approval_requests`, take allowed actions, approve decisions, collect
evidence, complete the active goal, enable hosted dashboards, start remote
workers, schedule autonomous work, operate adapters, run CI/deploys, enforce
budgets, promote trust, retry/replay work, track real spend, change routing,
or mutate external systems.

## 2026-06-22: Report-Only Expansion Operator Approval Request Review

Use `python3 -m agent_os.cli expansion-operator-approval-request-review` after
`expansion-operator-approval-draft` to review draft requests against the
existing `approval_requests` table before any real approval row exists. The
review should retain the source draft, ledger, checklist, evidence index,
decision brief, goal audit, evidence paths, request kinds, allowed actions, and
approval boundaries. Until the approval subject model is extended or split into
a separate table, capability/external approval requests remain blocked with
`approval_request_subject_not_modeled`, `creation_status=not_created`, and
`created_approval_requests=0`. The review does not create approval requests,
take allowed actions, approve decisions, collect evidence, complete the active
goal, enable hosted dashboards, start remote workers, schedule autonomous work,
operate adapters, run CI/deploys, enforce budgets, promote trust, retry/replay
work, track real spend, change routing, or mutate external systems.

## 2026-06-22: Report-Only Expansion Operator Approval Schema Decision

Use `python3 -m agent_os.cli expansion-operator-approval-schema-decision` after
`expansion-operator-approval-request-review` to turn the current
`approval_request_subject_not_modeled` gap into an explicit local schema
decision packet. The current recommendation is
`operator_approval_requests_table`, backed by a new `operator_approval_requests`
schema object in a future migration, because it preserves the existing
task-focused `approval_requests` gate while modeling external decisions and
capability approvals as non-task subjects. Reject making current task fields
nullable because it weakens the existing dispatch approval contract; reject
synthesizing placeholder tasks because it mixes non-executable operator
decisions into the executable queue. This decision packet applies no migration,
creates no approval requests or operator approval rows, approves no decisions,
takes no allowed actions, collects no evidence, completes no goal, enables no
capability, changes no routing, and mutates no external systems.

## 2026-06-22: Report-Only Expansion Operator Approval Schema Migration Plan

Use `python3 -m agent_os.cli expansion-operator-approval-schema-migration-plan`
after `expansion-operator-approval-schema-decision` to convert the chosen
`operator_approval_requests_table` option into a concrete migration plan for a
future `operator_approval_requests` table. The plan should retain the source
schema decision and upstream review chain, propose subject-oriented columns,
indexes, and migration steps, and require explicit operator approval before
any schema application. This plan applies no migration, creates no table,
creates no `operator_approval_requests` rows, creates no `approval_requests`
rows, approves no decisions, takes no allowed actions, completes no goal,
changes no routing, and mutates no external systems.

## 2026-06-22: Report-Only Expansion Operator Approval Schema Migration Approval Request

Use
`python3 -m agent_os.cli expansion-operator-approval-schema-migration-approval-request`
after `expansion-operator-approval-schema-migration-plan` to convert the plan
into a report-only operator approval packet. The packet should retain the
source migration plan and schema decision, target table, requested action
`apply_operator_approval_requests_schema`, approval boundary
`schema_migration`, and allowed actions `approve`, `defer`, and
`request_more_evidence`. This packet creates no approval rows, applies no
migration, creates no table, takes no allowed action, approves no decisions,
changes no routing, and mutates no external systems.

## 2026-06-22: Report-Only Expansion Operator Approval Schema Migration Decision Ledger

Use
`python3 -m agent_os.cli expansion-operator-approval-schema-migration-decision-ledger`
after `expansion-operator-approval-schema-migration-approval-request` to
convert the schema migration approval packet into a pending/manual operator
action ledger. The ledger should retain the source approval request, migration
plan, schema decision, target table, requested action
`apply_operator_approval_requests_schema`, boundary `schema_migration`, and
allowed actions `approve`, `defer`, and `request_more_evidence`. It may record
`pending_operator_action`, but it must not record an action as taken. This
ledger creates no approval rows, applies no migration, creates no table,
takes no allowed action, approves no decisions, changes no routing, and
mutates no external systems.

## 2026-06-22: Report-Only Expansion Operator Approval Schema Migration Action Checklist

Use
`python3 -m agent_os.cli expansion-operator-approval-schema-migration-action-checklist`
after `expansion-operator-approval-schema-migration-decision-ledger` to
surface the manual operator choices before any schema migration is selected.
The checklist should retain the source decision ledger, approval request,
target table, requested action `apply_operator_approval_requests_schema`,
boundary `schema_migration`, and allowed actions `approve`, `defer`, and
`request_more_evidence`. It must keep `selected_action=none` and
`actions_taken=0` until a separate explicit selection flow exists. This
checklist creates no approval rows, applies no migration, creates no table,
takes no allowed action, approves no decisions, changes no routing, and
mutates no external systems.

## 2026-06-22: Report-Only Expansion Operator Approval Schema Migration Selection Packet

Use
`python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-packet`
after `expansion-operator-approval-schema-migration-action-checklist` to make
the remaining operator input requirement explicit before any schema migration
action can be selected. The packet should retain the source action checklist,
decision ledger, approval request, target table, requested action
`apply_operator_approval_requests_schema`, boundary `schema_migration`, and
allowed actions `approve`, `defer`, and `request_more_evidence`. It must keep
`selected_action=none`, `selections_recorded=0`, and `actions_taken=0`; the
selection packet is not itself a selection. This packet creates no approval
rows, applies no migration, creates no table, takes no allowed action,
approves no decisions, changes no routing, and mutates no external systems.
