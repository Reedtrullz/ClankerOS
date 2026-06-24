# Context Pack

- context_pack_id: context_pack_2bf26861809c
- project_id: clankeros
- delegation_id: subagent_delegation_035c3e0876c7
- task_id: task_de0322669e63

## Query Terms

- 1fa51c15f846
- 1fa51c15f846-parent_task_id
- 1fa51c15f846_parent_task_id
- acceptance
- acceptance-criteria
- acceptance_criteria
- acceptance_criteria-acceptance
- acceptance_criteria_acceptance
- agent
- agent-cli
- agent-os
- agent_cli
- agent_os
- agent_os-agent
- agent_os_agent
- approve
- approve-call
- approve_call
- assigned
- assigned-profile
- assigned_profile
- assigned_profile-assigned
- assigned_profile_assigned
- behavior
- behavior-proof
- behavior_proof
- boundaries
- boundaries-read-only
- boundaries_read-only
- boundary
- boundary-demo
- boundary_demo
- call
- call-external
- call_external
- category
- category-implementation
- category_implementation
- clankeros
- clankeros-source

## Ranked Files

- agent_os/context_pack.py score=51 tags=implementation,python
  - path match: agent
  - path match: agent_os
  - path match: context
- agent_os/profile_routing.py score=38 tags=implementation,python
  - path match: agent
  - path match: agent_os
  - path match: profile
- agent_os/browser_desktop_adapter_proof.py score=37 tags=implementation,python
  - path match: agent
  - path match: agent_os
  - path match: proof
- agent_os/capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations.py score=37 tags=implementation,python
  - path match: agent
  - path match: agent_os
  - path match: task
- AGENTS.md score=30 tags=entrypoint
  - path match: agent
  - filename match: agent
  - implementation extension: .md
- docs/tutorial-first-target-repo.md score=28 tags=docs
  - path match: repo
  - filename match: repo
  - path match: target
- README (1).md score=27 tags=
  - path match: read
  - filename match: read
  - implementation extension: .md
- agent_os/automatic_retry_proof.py score=25 tags=implementation,python
  - path match: agent
  - path match: agent_os
  - path match: proof

## Test Hints

- none

## Grep Hits

- runs/run_60c9a37d66ed/evidence-index.md:70 term=approve `- Does not approve, reject, commit, push, deploy, or mutate external systems.`
- runs/run_2ea420719720/evidence-index.md:67 term=approve `- Does not approve, reject, commit, push, deploy, or mutate external systems.`
- runs/run_ce1a7fc25cd8/review.md:51 term=approve `- This report does not approve effects, commit changes, push code, or rerun work.`
- runs/run_ce1a7fc25cd8/replay-summary.md:30 term=approve `- This report does not rerun commands, mutate files, or approve effects.`
- AGENTS.md:3 term=agent `This repository is a local-first harness for a durable agentic operating system.`
- AGENTS.md:10 term=behavior ``status.md`, and the active project file pack before changing behavior.`
- AGENTS.md:11 term=agent `- Treat the SQLite database and `.agent/` runtime files as operational indexes.`
- AGENTS.md:16 term=agent `- Do not mark work complete because an agent said it completed. Verify the`
- AGENTS.md:17 term=behavior `expected file, output, behavior, or state change.`
- runs/run_ce1a7fc25cd8/evidence-index.md:39 term=approve `- Does not approve, reject, commit, push, deploy, or mutate external systems.`
- README (1).md:3 term=agent `ClankerOS is a local-first harness for building a durable agentic operating`
- README (1).md:4 term=boundaries `system with explicit state, verification evidence, and approval boundaries.`
- README (1).md:5 term=agent `It sits above replaceable coding agents and keeps durable project truth in`
- README (1).md:12 term=agent `-> replaceable agent/runtime execution`
- README (1).md:29 term=behavior `The project deliberately favors report-only proof, conservative local behavior,`
- contracts.md:5 term=agent `Create a local-first agent operating-system harness that proves the closed loop`
- contracts.md:10 term=agent `- Host: Codex desktop agent operating in a local git repository.`
- contracts.md:27 term=agent `- No multi-agent editing of one checkout.`
- contracts.md:33 term=agent `- Keep the single-agent baseline simple before adding parallelism.`
- contracts.md:70 term=boundaries `retained, recommended manual commands surfaced, approval boundaries named,`

## Snippets

### runs/run_60c9a37d66ed/evidence-index.md:69-71

```text
- Does not replay or rerun the work.
- Does not approve, reject, commit, push, deploy, or mutate external systems.
- network_actions_taken: 0
```

### runs/run_2ea420719720/evidence-index.md:66-68

```text
- Does not replay or rerun the work.
- Does not approve, reject, commit, push, deploy, or mutate external systems.
- network_actions_taken: 0
```

### runs/run_ce1a7fc25cd8/review.md:50-51

```text
- external_mutations_taken: 0
- This report does not approve effects, commit changes, push code, or rerun work.
```

### runs/run_ce1a7fc25cd8/replay-summary.md:29-31

```text

- This report does not rerun commands, mutate files, or approve effects.
- It is a conceptual replay map for operator review and future automation.
```

## Non-Claims

- No file was modified.
- No command with side effects was run.
- No model provider was called by ClankerOS.
- No commit, push, deploy, or approval was performed.
