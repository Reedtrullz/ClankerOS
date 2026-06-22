# Plan

## Milestones

### Milestone 1: Local Closed Loop

Implement the smallest reliable harness that accepts a goal, creates tasks,
executes and verifies a local task, records memory, displays activity, and
creates one learning/eval artifact.

### Milestone 2: Operational Visibility

Add richer task/session views, incident reporting, queue health checks, and a
static dashboard generated from SQLite and run artifacts.

### Milestone 3: Policy, Budgets, And Approvals

Add risk levels, approval gates, budget tracking, trust levels by domain, and
safe blocked/wait states.

### Milestone 4: Adapter Expansion

Add browser and desktop workflow adapters with evidence capture, then add
research and external-intelligence loops behind explicit policies.

## Current Focus

Milestone 3 approval-gated capability activation flow: keep deferred autonomy
surfaces in local task, delegation, result, decision, effect, and dashboard
state while preserving explicit approval boundaries. Current work favors
operator review decisions, idempotent local effect proposals, evidence plans,
and dashboard visibility before any hosted dashboard, remote worker,
scheduler, browser/desktop adapter, CI/deploy automation, budget enforcement,
trust promotion, automatic retry, or real cost tracking behavior is enabled.
