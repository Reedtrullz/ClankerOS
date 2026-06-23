# Sprint Contract contract_5c2df3a91f86

- project_id: clankeros
- goal_id: goal_9b9a52c29e43
- plan_id: plan_7b0d95b67749
- plan_version: 1
- status: draft

## Scope

Execute plan v1 for goal: Add a small tested improvement to the CLI help output

## Non-Goals

No external side effects, no CI/deploy claim, no autonomous scheduling, and no model-provider dispatch from this contract.

## Acceptance Criteria

- Scope, non-goals, and verifier are explicit.
- Changed files are limited to the agreed scope and have local evidence.
- Tests, dashboard, handoff, and next-action evidence are current.

## Verification Plan

- python3 -m agent_os.cli project-context clankeros
- python3 -m pytest -q
- python3 -m pytest -q

## Risk Notes

Planned tasks remain status=planned until an operator or later runner explicitly moves them into an executable state.

## Evaluator Notes

Review plan alignment, task evidence, and non-claims before execution.

## Plan Steps

- 1. Clarify scope and acceptance criteria: planned
- 2. Implement the smallest safe change: planned
- 3. Verify evidence and decide next action: planned

## Non-Claims

- Contract creation does not approve work.
- Contract creation does not run tests, commit, push, deploy, or call model providers.
