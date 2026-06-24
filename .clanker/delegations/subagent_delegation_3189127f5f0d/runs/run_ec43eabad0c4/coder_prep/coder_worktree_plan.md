# Coder Worktree Plan

- plan_id: coder_worktree_plan
- delegation_id: subagent_delegation_3189127f5f0d
- source_coder_prep_md: .clanker/delegations/subagent_delegation_3189127f5f0d/runs/run_ec43eabad0c4/coder_prep/coder_prep.md
- source_coder_prep_sha256: b4b1fd2c21343c5ac86d23d4a649170a90b709f0e2230637d8d4086094d3be42
- project_id: clankeros

## Bounded Coding Task

- title: Approval-gated worktree plan from coder prep subagent_delegation_3189127f5f0d
- objective: Context pack scout demo completed.

## Allowed Files

- agent_os/context_pack.py
- agent_os/profile_routing.py
- evals/results/first_milestone_closed_loop.json
- playbooks/first-milestone-closed-loop.md
- agent_os/capability_activation_followup_result_task_result_effect_task_result_effect_task_delegations.py

## Proposed Worktree

- status: not_created
- branch_name_suggestion: codex/coder-prep-3189127f5f0d
- path_suggestion: .agent/worktrees/clankeros/coder-prep-3189127f5f0d
- base_ref: operator_selected_current_head

## Approval Gate

- status: operator_approval_required
- approval_request_created: false
- required_before: create_worktree
- required_before: run_command
- required_before: edit_source
- required_before: commit
- required_before: push
- required_before: deploy

## Future Run Plan

- execution_mode: future_explicit_worktree_run
- commands_to_run_now: none
- suggested_future_command: python3 -m agent_os.cli run-goal "Context pack scout demo completed." --project clankeros --isolation worktree --command "<operator-approved bounded command>"
- next_recommended_action: operator_review
- dispatch_ready: false

## Safety Counters

- source_edits_taken: 0
- task_rows_created: 0
- runs_created: 0
- routing_decisions_created: 0
- worktrees_created: 0
- effects_created: 0
- approval_requests_created: 0
- commands_rerun: 0
- provider_calls_taken_by_clankeros: 0
- network_actions_taken: 0
- external_mutations_taken: 0

## Non-Claims

- Coder worktree planning does not create a git worktree.
- Coder worktree planning does not create task, run, routing, approval, or effect rows.
- Coder worktree planning does not edit source files, run commands, commit, push, deploy, or call providers.
