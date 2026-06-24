# Context Pack

- context_pack_id: context_pack_c77525064b80
- project_id: clankeros
- delegation_id: subagent_delegation_c1f5246a0b7f
- task_id: task_858971dcc5d7

## Query Terms

- 1fa51c15f846
- 1fa51c15f846-parent_task_id
- 1fa51c15f846_parent_task_id
- 858971dcc5d7
- 858971dcc5d7-project_id
- 858971dcc5d7_project_id
- approve
- approve-call
- approve_call
- assigned
- assigned-profile
- assigned_profile
- assigned_profile-assigned
- assigned_profile_assigned
- boundaries
- boundaries-read-only
- boundaries_read-only
- call
- call-external
- call_external
- category
- category-summarization
- category_summarization
- clankeros
- clankeros-task_type
- clankeros_task_type
- command
- command-python3
- command_python3
- commit
- commit-approve
- commit_approve
- context
- context-gathering
- context-pack
- context-pack-context
- context-pack_context
- context-parent_goal_id
- context_gathering
- context_pack

## Ranked Files

- agent_os/context_pack.py score=53 tags=implementation,python
  - path match: context
  - filename match: context
  - path match: context_pack
- agent_os/profile_routing.py score=41 tags=implementation,python
  - path match: file
  - filename match: file
  - path match: profile
- evals/results/first_milestone_closed_loop.json score=41 tags=config
  - path match: first
  - filename match: first
  - path match: first_milestone
- playbooks/first-milestone-closed-loop.md score=41 tags=
  - path match: first
  - filename match: first
  - path match: first-milestone
- agent_os/capability_activation_followup_result_task_result_effect_task_result_effect_task_delegations.py score=31 tags=implementation,python
  - path match: delegation
  - filename match: delegation
  - path match: task
- agent_os/capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations.py score=31 tags=implementation,python
  - path match: delegation
  - filename match: delegation
  - path match: task
- agent_os/capability_activation_followup_result_task_delegations.py score=28 tags=implementation,python
  - path match: delegation
  - filename match: delegation
  - path match: task
- agent_os/capability_activation_followup_result_task_result_effect_task_delegations.py score=28 tags=implementation,python
  - path match: delegation
  - filename match: delegation
  - path match: task

## Test Hints

- none

## Grep Hits

- agent_os/capability_activation_followups.py:227 term=command `required_commands = contract.evidence_requirements.get("required_commands", [])`
- agent_os/capability_activation_followups.py:234 term=command `"required_commands": required_commands,`
- runs/run_60c9a37d66ed/evidence-index.md:26 term=command `- .clanker/projects/bootstrap/goals/goal_0a8ac2a4cae4/runs/run_60c9a37d66ed/evidence/commands.jsonl`
- runs/run_60c9a37d66ed/evidence-index.md:70 term=approve `- Does not approve, reject, commit, push, deploy, or mutate external systems.`
- agent_os/expansion_operator_approval_schema_migration_selection_input_template.py:84 term=approve `approve_selection_count = 0`
- agent_os/expansion_operator_approval_schema_migration_selection_input_template.py:122 term=approve `approve_selection_count = source_packet.approve_selection_count`
- agent_os/expansion_operator_approval_schema_migration_selection_input_template.py:158 term=approve `approve_selection_count = source_packet.approve_selection_count`
- agent_os/expansion_operator_approval_schema_migration_selection_input_template.py:198 term=approve `approve_selection_count=approve_selection_count,`
- agent_os/expansion_operator_approval_schema_migration_selection_input_template.py:262 term=approve `f"- approve_selections: {template.approve_selection_count}",`
- agent_os/capability_activation_followup_result_effect_proposals.py:76 term=commit `committed_at=None,`
- agent_os/capability_activation_followup_result_effect_proposals.py:278 term=assigned `"assigned_profile": result_record.assigned_profile,`
- agent_os/capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_delegations.py:186 term=call `"- Does not call model providers.",`
- agent_os/browser_desktop_adapter_proof.py:140 term=boundaries `f"- boundaries: {checklist.boundary_count}",`
- agent_os/browser_desktop_adapter_proof.py:141 term=command `f"- recommended_commands: {format_recommended_commands(checklist.recommended_commands)}",`
- agent_os/browser_desktop_adapter_proof.py:227 term=call `"- Does not collect evidence automatically.",`
- agent_os/browser_desktop_adapter_proof.py:228 term=approve `"- Does not approve capabilities automatically.",`
- agent_os/browser_desktop_adapter_proof.py:229 term=call `"- Does not promote capabilities automatically.",`
- agent_os/task_recommendations.py:34 term=command `"verification command failed"`
- agent_os/task_recommendations.py:36 term=command `else f"verification command failed with exit {task.evidence['returncode']}"`
- agent_os/task_recommendations.py:44 term=command `commands = [`

## Snippets

### agent_os/capability_activation_followups.py:226-228

```text
) -> dict[str, object]:
    required_commands = contract.evidence_requirements.get("required_commands", [])
    required_artifacts = contract.evidence_requirements.get("required_artifacts", [])
```

### agent_os/capability_activation_followups.py:233-235

```text
        "source_decision_id": source_decision.id if source_decision else "none",
        "required_commands": required_commands,
        "required_artifacts": required_artifacts,
```

### runs/run_60c9a37d66ed/evidence-index.md:25-27

```text
- .clanker/projects/bootstrap/goals/goal_0a8ac2a4cae4/runs/run_60c9a37d66ed/evidence/steering_reviews.jsonl
- .clanker/projects/bootstrap/goals/goal_0a8ac2a4cae4/runs/run_60c9a37d66ed/evidence/commands.jsonl
- .clanker/projects/bootstrap/goals/goal_0a8ac2a4cae4/runs/run_60c9a37d66ed/evidence/verification.json
```

### runs/run_60c9a37d66ed/evidence-index.md:69-71

```text
- Does not replay or rerun the work.
- Does not approve, reject, commit, push, deploy, or mutate external systems.
- network_actions_taken: 0
```

## Non-Claims

- No file was modified.
- No command with side effects was run.
- No model provider was called by ClankerOS.
- No commit, push, deploy, or approval was performed.
