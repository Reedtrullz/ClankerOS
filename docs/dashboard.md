# Agent System Dashboard

## Operator Cockpit

### Active Goals/Runs

- none

### Registered Projects

- none

### Approval Inbox

- none

### Proposed Effects

- effect_0fa73f003874: capability_followup_blocked_result_proposal status=applied approval=capability_activation_followup_result_decision_146e16543cec project=bootstrap target=hosted_dashboard evidence=docs/capability-activation-followup-result-effect-application.md
- effect_1a41ff7c5cca: operator_capability_proposal status=applied approval=operator_approval_request_c59b82c4f7c3 project=bootstrap target=real_cost_tracking evidence=docs/expansion-operator-approval-effect-application.md
- effect_e5a56b95d9ce: operator_capability_proposal status=applied approval=operator_approval_request_239a407346df project=bootstrap target=automatic_retries evidence=docs/expansion-operator-approval-effect-application.md
- effect_549912b53e8e: operator_capability_proposal status=applied approval=operator_approval_request_582f7bfe609c project=bootstrap target=trust_promotion evidence=docs/expansion-operator-approval-effect-application.md
- effect_9ad8411cfe14: operator_capability_proposal status=applied approval=operator_approval_request_21a453d20186 project=bootstrap target=budget_enforcement evidence=docs/expansion-operator-approval-effect-application.md

### Recent Commits/Effects

- effect_0fa73f003874: capability_followup_blocked_result_proposal status=applied committed_at=not_committed commit=none
- effect_1a41ff7c5cca: operator_capability_proposal status=applied committed_at=not_committed commit=none
- effect_e5a56b95d9ce: operator_capability_proposal status=applied committed_at=not_committed commit=none
- effect_549912b53e8e: operator_capability_proposal status=applied committed_at=not_committed commit=none
- effect_9ad8411cfe14: operator_capability_proposal status=applied committed_at=not_committed commit=none

### Incidents

- none

### Verification Status

- effect_0fa73f003874: missing method=capability_activation_more_evidence_followup command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_1a41ff7c5cca: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_e5a56b95d9ce: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_549912b53e8e: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_9ad8411cfe14: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json

### Recent Worktrees

- none

### Worktree Cleanup

- none

### GitHub Handoffs

- none

### CI/Deploy Evidence

- none

### Profile Routing

- enabled_profiles: 5
- profile coder: Implementation Coder mode=primary cost=high model=configurable/coder-model use_for=implementation,refactor,bugfix
- profile evaluator: Alignment Evaluator mode=subagent cost=medium model=configurable/strong-reasoning-model use_for=sprint_contract_review,alignment_review,evidence_review,final_review
- profile planner: Strategic Planner mode=primary cost=high model=configurable/planner-model use_for=ambiguous_goal,architecture,plan_creation,replan
- profile scout: Repo Scout mode=subagent cost=low model=configurable/cheap-fast-model use_for=repo_search,file_mapping,dependency_mapping,summarization
- profile tester: Verification Tester mode=subagent cost=low model=configurable/cheap-coding-model use_for=test_triage,failure_summary,verification_review
- recent_decisions:
- routing_decision_17a5d6070d70: category=evidence_review selected=evaluator model=configurable/strong-reasoning-model cost=medium task=task_4e0c48c4ff48 project=bootstrap status=selected
- routing_decision_db409963a4e4: category=evidence_review selected=evaluator model=configurable/strong-reasoning-model cost=medium task=task_77ba0589314d project=bootstrap status=selected
- routing_decision_58d4f07eae31: category=evidence_review selected=evaluator model=configurable/strong-reasoning-model cost=medium task=task_6db6dcd9a6c4 project=bootstrap status=selected
- routing_decision_066a1e8b171a: category=evidence_review selected=evaluator model=configurable/strong-reasoning-model cost=medium task=task_734b7397c0b4 project=bootstrap status=selected
- routing_decision_9391118ee82b: category=evidence_review selected=evaluator model=configurable/strong-reasoning-model cost=medium task=task_22406ad4a2a6 project=bootstrap status=selected

### Subagent Delegations

- subagent_delegation_48d1cc9f63ae: status=completed profile=evaluator category=evidence_review task=task_4e0c48c4ff48 schema=evidence_review artifact=/Users/reidar/Documents/Agent System/.clanker/delegations/subagent_delegation_48d1cc9f63ae-result.json summary=Hosted dashboard follow-up review found no fresh hosted-dashboard proof attached; keep activation blocked.
- subagent_delegation_159495832f88: status=pending profile=evaluator category=evidence_review task=task_77ba0589314d schema=evidence_review artifact=/Users/reidar/Documents/Agent System/.clanker/delegations/task_77ba0589314d-review-remote-workers-follow-up-evidence-requirements.json
- subagent_delegation_13cc55468b0d: status=pending profile=evaluator category=evidence_review task=task_6db6dcd9a6c4 schema=evidence_review artifact=/Users/reidar/Documents/Agent System/.clanker/delegations/task_6db6dcd9a6c4-review-autonomous-scheduling-follow-up-evidence-requirements.json
- subagent_delegation_f77fd0595f14: status=pending profile=evaluator category=evidence_review task=task_734b7397c0b4 schema=evidence_review artifact=/Users/reidar/Documents/Agent System/.clanker/delegations/task_734b7397c0b4-review-browser-desktop-adapters-follow-up-evidence-requirements.json
- subagent_delegation_f04958d76697: status=pending profile=evaluator category=evidence_review task=task_22406ad4a2a6 schema=evidence_review artifact=/Users/reidar/Documents/Agent System/.clanker/delegations/task_22406ad4a2a6-review-ci-deploy-proof-follow-up-evidence-requirements.json

## Steering Reviews

- steer_4a39cbdcc894: status=clear goal=goal_3010379344ae run=run_d52df83d4bba drift=none action=continue requires_operator=false report=docs/steering-review.md

### Next Recommended Action

- Review recent proposed effects and regenerate the dashboard after decisions.

## Queue Health

- pending: 18
- waiting_approval: 0
- claimed: 0
- running: 0
- verifying: 0
- completed: 433
- blocked: 0
- failed: 0
- active: 0
- needs_attention: 0

## Iteration Loop

- status: planned
- focus: Add downstream task records from applied follow-up decision effect applications.
- source: tasks.md#next
- packet: docs/next-iteration.md
- created_at: 2026-06-22T18:45:21.079014+00:00

## Simplicity Guardrail

- policy: highest-score-then-lowest-complexity
- reason: selected only actionable item with score 9 and complexity 4
- selected_score: 9
- selected_complexity: 4
- selected_focus: Add downstream task records from applied follow-up decision effect applications.

## Expansion Operator Approval Schema Decision

- status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_56ad3802e63b
- source_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_6cd8abd426f6
- source_ledger: expansion_operator_decision_ledger_21c9b282c06a
- source_checklist: expansion_operator_review_checklist_7c4fcdf41f96
- source_index: expansion_decision_evidence_index_77621150a88e
- source_brief: expansion_decision_brief_26db1de5231d
- source_audit: goal_completion_audit_981a08705399
- affected_requests: 11
- schema_gaps: 11
- missing_fields: 7
- external_requests: 2
- capability_requests: 9
- decision_options: 3
- recommended_option: operator_approval_requests_table
- rejected_options: 2
- schema_objects: 1
- migration_applied: 0
- created_approval_requests: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_plan_required
- report: docs/expansion-operator-approval-schema-decision.md

- expansion_operator_approval_schema_decision_0682a62c5642: status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_56ad3802e63b source_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_6cd8abd426f6 source_ledger=expansion_operator_decision_ledger_21c9b282c06a source_checklist=expansion_operator_review_checklist_7c4fcdf41f96 source_index=expansion_decision_evidence_index_77621150a88e source_brief=expansion_decision_brief_26db1de5231d source_audit=goal_completion_audit_981a08705399 affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 decision_options=3 recommended_option=operator_approval_requests_table rejected_options=2 schema_objects=1 migration_applied=0 created_approval_requests=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_plan_required report=docs/expansion-operator-approval-schema-decision.md

## Expansion Operator Approval Schema Migration Plan

- status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_0682a62c5642
- source_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_56ad3802e63b
- source_review_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_6cd8abd426f6
- source_ledger: expansion_operator_decision_ledger_21c9b282c06a
- source_checklist: expansion_operator_review_checklist_7c4fcdf41f96
- source_index: expansion_decision_evidence_index_77621150a88e
- source_brief: expansion_decision_brief_26db1de5231d
- source_audit: goal_completion_audit_981a08705399
- recommended_option: operator_approval_requests_table
- target_table: operator_approval_requests
- affected_requests: 11
- schema_gaps: 11
- missing_fields: 7
- external_requests: 2
- capability_requests: 9
- planned_columns: 26
- planned_indexes: 4
- migration_steps: 4
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_approval_required
- report: docs/expansion-operator-approval-schema-migration-plan.md

- expansion_operator_approval_schema_migration_plan_43782b35400e: status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_0682a62c5642 source_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_56ad3802e63b source_review_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_6cd8abd426f6 source_ledger=expansion_operator_decision_ledger_21c9b282c06a source_checklist=expansion_operator_review_checklist_7c4fcdf41f96 source_index=expansion_decision_evidence_index_77621150a88e source_brief=expansion_decision_brief_26db1de5231d source_audit=goal_completion_audit_981a08705399 recommended_option=operator_approval_requests_table target_table=operator_approval_requests affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 planned_columns=26 planned_indexes=4 migration_steps=4 migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_approval_required report=docs/expansion-operator-approval-schema-migration-plan.md

## Capability Activation Follow-Up Delegations

- status: capability_activation_followup_delegations_already_recorded
- followup_tasks: 9
- routing_decisions_created: 0
- delegations_created: 0
- existing_delegations: 9
- execution_started: 0
- network_actions_taken: 0
- external_mutations_taken: 0
- activation_actions_taken: 0
- report: docs/capability-activation-followup-delegations.md

- capability_activation_followup_delegation_batch_d94bb0e07be2: status=capability_activation_followup_delegations_already_recorded followup_tasks=9 routing_decisions_created=0 delegations_created=0 existing_delegations=9 execution_started=0 network_actions=0 activation_actions=0 report=docs/capability-activation-followup-delegations.md

## Expansion Operator Approval Request Decisions

- status: operator_approval_request_decisions_recorded
- source_row_application: operator_approval_request_row_application_9d1c3e1d4012
- source_status: operator_approval_request_rows_applied
- source_draft: expansion_operator_approval_draft_93697a4315da
- source_schema_application: operator_approval_schema_migration_application_58b1de2348a1
- source_ledger: expansion_operator_decision_ledger_51c1e0f289fa
- source_checklist: expansion_operator_review_checklist_f01aaf772dab
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
- operator_id: operator
- selected_action: approve
- pending_requests_before: 11
- decisions_recorded: 11
- approved_decisions: 11
- deferred_decisions: 0
- more_evidence_decisions: 0
- pending_requests_after: 0
- existing_decisions: 0
- approval_requests_created: 0
- external_requests: 2
- capability_requests: 9
- report: docs/expansion-operator-approval-request-decisions.md

- operator_approval_request_decision_560d5914977d: status=operator_approval_request_decisions_recorded source_row_application=operator_approval_request_row_application_9d1c3e1d4012 operator_id=operator selected_action=approve pending_requests_before=11 decisions_recorded=11 approved_decisions=11 deferred_decisions=0 more_evidence_decisions=0 pending_requests_after=0 existing_decisions=0 approval_requests_created=0 external_requests=2 capability_requests=9 report=docs/expansion-operator-approval-request-decisions.md

## Expansion Operator Approval Effect Proposals

- status: operator_approval_effect_proposals_recorded
- source_decision: operator_approval_request_decision_560d5914977d
- approved_operator_requests: 11
- effect_proposals_created: 11
- existing_effect_proposals: 11
- external_effect_proposals: 2
- capability_effect_proposals: 9
- legacy_approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/expansion-operator-approval-effect-application.md

- effect_1a41ff7c5cca: status=applied effect_type=operator_capability_proposal capability=real_cost_tracking target=real_cost_tracking required_approval=operator_approval_request_c59b82c4f7c3 idempotency_key=operator-approval-effect:operator_approval_request_c59b82c4f7c3 report=docs/expansion-operator-approval-effect-application.md
- effect_e5a56b95d9ce: status=applied effect_type=operator_capability_proposal capability=automatic_retries target=automatic_retries required_approval=operator_approval_request_239a407346df idempotency_key=operator-approval-effect:operator_approval_request_239a407346df report=docs/expansion-operator-approval-effect-application.md
- effect_549912b53e8e: status=applied effect_type=operator_capability_proposal capability=trust_promotion target=trust_promotion required_approval=operator_approval_request_582f7bfe609c idempotency_key=operator-approval-effect:operator_approval_request_582f7bfe609c report=docs/expansion-operator-approval-effect-application.md
- effect_9ad8411cfe14: status=applied effect_type=operator_capability_proposal capability=budget_enforcement target=budget_enforcement required_approval=operator_approval_request_21a453d20186 idempotency_key=operator-approval-effect:operator_approval_request_21a453d20186 report=docs/expansion-operator-approval-effect-application.md
- effect_1e2d271e79f3: status=applied effect_type=operator_capability_proposal capability=ci_deploy_proof target=ci_deploy_proof required_approval=operator_approval_request_6a498ab280e1 idempotency_key=operator-approval-effect:operator_approval_request_6a498ab280e1 report=docs/expansion-operator-approval-effect-application.md
- effect_2fe6bd7d30f4: status=applied effect_type=operator_capability_proposal capability=browser_desktop_adapters target=browser_desktop_adapters required_approval=operator_approval_request_5f1238b66961 idempotency_key=operator-approval-effect:operator_approval_request_5f1238b66961 report=docs/expansion-operator-approval-effect-application.md
- effect_29e9791db746: status=applied effect_type=operator_capability_proposal capability=autonomous_scheduling target=autonomous_scheduling required_approval=operator_approval_request_6ebeb2f32056 idempotency_key=operator-approval-effect:operator_approval_request_6ebeb2f32056 report=docs/expansion-operator-approval-effect-application.md
- effect_cc210d6119d5: status=applied effect_type=operator_capability_proposal capability=remote_workers target=remote_workers required_approval=operator_approval_request_e9b0f08564e1 idempotency_key=operator-approval-effect:operator_approval_request_e9b0f08564e1 report=docs/expansion-operator-approval-effect-application.md
- effect_f150fdc78c97: status=applied effect_type=operator_capability_proposal capability=hosted_dashboard target=hosted_dashboard required_approval=operator_approval_request_6f34e2f394cd idempotency_key=operator-approval-effect:operator_approval_request_6f34e2f394cd report=docs/expansion-operator-approval-effect-application.md
- effect_a4c16d8bee74: status=applied effect_type=operator_external_decision capability=external_decision target=Choose deployment target before hosted dashboard work. required_approval=operator_approval_request_f7ee8e548564 idempotency_key=operator-approval-effect:operator_approval_request_f7ee8e548564 report=docs/expansion-operator-approval-effect-application.md
- effect_119092eae663: status=applied effect_type=operator_external_decision capability=external_decision target=Choose external model providers and API policies before adding remote model routing. required_approval=operator_approval_request_96d25fbeb129 idempotency_key=operator-approval-effect:operator_approval_request_96d25fbeb129 report=docs/expansion-operator-approval-effect-application.md

## Expansion Operator Approval Effect Application

- status: operator_approval_effect_application_already_recorded
- operator_id: operator
- proposed_effects: 0
- effects_applied: 0
- existing_applied_effects: 11
- external_effects_applied: 0
- capability_effects_applied: 0
- legacy_approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/expansion-operator-approval-effect-application.md

- operator_approval_effect_application_e0c5bd92fde7: status=operator_approval_effect_application_already_recorded operator_id=operator proposed_effects=0 effects_applied=0 existing_applied_effects=11 external_effects=0 capability_effects=0 activation_actions=0 legacy_approval_requests=0 report=docs/expansion-operator-approval-effect-application.md

## Capability Activation Tasks

- status: capability_activation_tasks_already_recorded
- source_application: operator_approval_effect_application_e0c5bd92fde7
- goal: goal_b25a107a53a9
- applied_capability_effects: 9
- tasks_created: 0
- existing_activation_tasks: 9
- activation_actions_taken: 0
- report: docs/capability-activation-tasks.md

- capability_activation_task_batch_e7876bf8ae6a: status=capability_activation_tasks_already_recorded source_application=operator_approval_effect_application_e0c5bd92fde7 goal=goal_b25a107a53a9 applied_capability_effects=9 tasks_created=0 existing_activation_tasks=9 activation_actions=0 report=docs/capability-activation-tasks.md

## Capability Activation Contracts

- status: capability_activation_contracts_already_recorded
- source_task_batch: capability_activation_task_batch_e7876bf8ae6a
- activation_tasks: 9
- contracts_created: 0
- existing_contracts: 9
- approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/capability-activation-contracts.md

- capability_activation_contract_batch_c39486464038: status=capability_activation_contracts_already_recorded source_task_batch=capability_activation_task_batch_e7876bf8ae6a activation_tasks=9 contracts_created=0 existing_contracts=9 approval_requests_created=0 activation_actions=0 report=docs/capability-activation-contracts.md

## Capability Activation Evidence

- status: capability_activation_evidence_already_recorded
- contracts_selected: 9
- evidence_records_created: 0
- existing_evidence_records: 9
- approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/capability-activation-evidence.md

- capability_activation_evidence_batch_eb4026020292: status=capability_activation_evidence_already_recorded contracts_selected=9 evidence_records_created=0 existing_evidence_records=9 approval_requests_created=0 activation_actions=0 report=docs/capability-activation-evidence.md

## Capability Activation Decisions

- status: capability_activation_decisions_already_recorded
- operator_id: operator
- selected_action: request_more_evidence
- contracts_ready: 0
- decisions_recorded: 0
- approved_decisions: 0
- deferred_decisions: 0
- more_evidence_decisions: 0
- existing_decisions: 9
- approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/capability-activation-decisions.md

- capability_activation_decision_3097690da5f9: status=capability_activation_decisions_already_recorded operator_id=operator selected_action=request_more_evidence contracts_ready=0 decisions_recorded=0 approved_decisions=0 deferred_decisions=0 more_evidence_decisions=0 existing_decisions=9 approval_requests_created=0 activation_actions=0 report=docs/capability-activation-decisions.md

## Capability Activation Follow-Up Tasks

- status: capability_activation_followups_already_recorded
- source_decision: capability_activation_decision_f601a69d076e
- contracts_selected: 9
- followup_tasks_created: 0
- existing_followup_tasks: 9
- approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/capability-activation-followups.md

- capability_activation_followup_batch_c288c45b9623: status=capability_activation_followups_already_recorded source_decision=capability_activation_decision_f601a69d076e contracts_selected=9 followup_tasks_created=0 existing_followup_tasks=9 approval_requests_created=0 activation_actions=0 report=docs/capability-activation-followups.md

## Capability Activation Follow-Up Results

- status: capability_activation_followup_results_already_recorded
- completed_delegations: 1
- result_records_created: 0
- existing_result_records: 1
- approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/capability-activation-followup-results.md

- capability_activation_followup_result_batch_bb94fe9345a6: status=capability_activation_followup_results_already_recorded completed_delegations=1 result_records_created=0 existing_result_records=1 approval_requests_created=0 activation_actions=0 report=docs/capability-activation-followup-results.md

## Capability Activation Follow-Up Decisions

- status: capability_activation_followup_result_decisions_already_recorded
- selected_action: accept_keep_blocked
- results_ready: 0
- decisions_recorded: 0
- accepted_keep_blocked_decisions: 0
- more_evidence_decisions: 0
- deferred_decisions: 0
- existing_decisions: 1
- approval_requests_created: 0
- activation_actions_taken: 0
- report: docs/capability-activation-followup-decisions.md

- capability_activation_followup_result_decision_bf51ed57df70: status=capability_activation_followup_result_decisions_already_recorded operator_id=operator selected_action=accept_keep_blocked results_ready=0 decisions_recorded=0 accepted_keep_blocked_decisions=0 more_evidence_decisions=0 deferred_decisions=0 existing_decisions=1 approval_requests_created=0 activation_actions=0 report=docs/capability-activation-followup-decisions.md

## Capability Activation Follow-Up Result Effect Proposals

- status: capability_activation_followup_result_effect_proposals_recorded
- source_decision: capability_activation_followup_result_decision_146e16543cec
- accepted_decisions: 1
- accepted_results: 1
- effect_proposals_created: 1
- existing_effect_proposals: 1
- capability_effect_proposals: 1
- approval_requests_created: 0
- activation_actions_taken: 0
- external_mutations_taken: 0
- report: docs/capability-activation-followup-result-effect-application.md

- effect=effect_0fa73f003874 decision=capability_activation_followup_result_decision_146e16543cec result=capability_activation_followup_result_4c9b8b0d1c43 status=applied effect_type=capability_followup_blocked_result_proposal capability=hosted_dashboard target=hosted_dashboard required_approval=capability_activation_followup_result_decision_146e16543cec idempotency_key=capability-followup-decision-effect:capability_activation_followup_result_decision_146e16543cec:capability_activation_followup_result_4c9b8b0d1c43 report=docs/capability-activation-followup-result-effect-application.md

## Capability Activation Follow-Up Result Effect Application

- status: capability_activation_followup_result_effect_application_already_recorded
- operator_id: operator
- proposed_effects: 0
- effects_applied: 0
- existing_applied_effects: 1
- capability_effects_applied: 0
- approval_requests_created: 0
- activation_actions_taken: 0
- external_mutations_taken: 0
- report: docs/capability-activation-followup-result-effect-application.md

- capability_activation_followup_result_effect_application_8b15a1b9d3e8: status=capability_activation_followup_result_effect_application_already_recorded operator_id=operator proposed_effects=0 effects_applied=0 existing_applied_effects=1 capability_effects=0 approval_requests=0 activation_actions=0 external_mutations=0 report=docs/capability-activation-followup-result-effect-application.md

## Expansion Operator Approval Schema Migration Approval Request

- status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43782b35400e
- source_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_0682a62c5642
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_56ad3802e63b
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- planned_columns: 26
- planned_indexes: 4
- migration_steps: 4
- affected_requests: 11
- schema_gaps: 11
- request_count: 1
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_decision_required
- report: docs/expansion-operator-approval-schema-migration-approval-request.md

- expansion_operator_approval_schema_migration_approval_request_5823fec40069: status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43782b35400e source_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_0682a62c5642 source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_56ad3802e63b source_review_status=approval_request_schema_review_required target_table=operator_approval_requests planned_columns=26 planned_indexes=4 migration_steps=4 affected_requests=11 schema_gaps=11 request_count=1 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_decision_required report=docs/expansion-operator-approval-schema-migration-approval-request.md

## Expansion Operator Approval Schema Migration Decision Ledger

- status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_5823fec40069
- source_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43782b35400e
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_0682a62c5642
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_56ad3802e63b
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- planned_columns: 26
- planned_indexes: 4
- migration_steps: 4
- affected_requests: 11
- schema_gaps: 11
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- approved_decisions: 0
- deferred_decisions: 0
- more_evidence_decisions: 0
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_action_required
- report: docs/expansion-operator-approval-schema-migration-decision-ledger.md

- expansion_operator_approval_schema_migration_decision_ledger_272ffdcbec3b: status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_5823fec40069 source_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43782b35400e source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_0682a62c5642 source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_56ad3802e63b source_review_status=approval_request_schema_review_required target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 approved_decisions=0 deferred_decisions=0 more_evidence_decisions=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_action_required report=docs/expansion-operator-approval-schema-migration-decision-ledger.md

## Expansion Operator Approval Schema Migration Action Checklist

- status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_272ffdcbec3b
- source_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_5823fec40069
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43782b35400e
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_0682a62c5642
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_56ad3802e63b
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- action_count: 1
- pending_actions: 1
- actions_taken: 0
- selected_action: none
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_selection_required
- report: docs/expansion-operator-approval-schema-migration-action-checklist.md

- expansion_operator_approval_schema_migration_action_checklist_07a5199a1907: status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_272ffdcbec3b source_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_5823fec40069 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43782b35400e source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_0682a62c5642 source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_required report=docs/expansion-operator-approval-schema-migration-action-checklist.md

## Expansion Operator Approval Schema Migration Selection Packet

- status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_07a5199a1907
- source_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_272ffdcbec3b
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_5823fec40069
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43782b35400e
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_0682a62c5642
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_56ad3802e63b
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- action_count: 1
- pending_actions: 1
- actions_taken: 0
- selected_action: none
- selection_count: 1
- pending_selections: 1
- selections_recorded: 0
- approve_selections: 0
- defer_selections: 0
- more_evidence_selections: 0
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_selection_input_required
- report: docs/expansion-operator-approval-schema-migration-selection-packet.md

- expansion_operator_approval_schema_migration_selection_packet_a3c1283899d1: status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_07a5199a1907 source_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_272ffdcbec3b source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_5823fec40069 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43782b35400e source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_0682a62c5642 source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 approve_selections=0 defer_selections=0 more_evidence_selections=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_input_required report=docs/expansion-operator-approval-schema-migration-selection-packet.md

## Queue Health Checks

- blocked_threshold: 2
- failed_threshold: 2
- hotspots: 0

- none

## Handoff Review

- status: clear
- current_focus: Add downstream task records from applied follow-up decision effect applications.
- blocked_tasks: 0
- stale_handoffs: 0
- report: docs/handoff-review.md

- none

## Eval After Change

- failed: 0

- eval_after_change_d5de7ef57f9f: status=pass change=Add capability followup result effect application records files=agent_os/capability_activation_followup_result_effect_application.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_357ca9a6d7fa results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_9a8a88b1f97b: status=pass change=Add capability followup result effect proposals files=agent_os/capability_activation_followup_result_effect_proposals.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_6aaaf091a7a0 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_b789b57e03a8: status=pass change=Add capability followup result decision ledger files=agent_os/capability_activation_followup_result_decisions.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_168daa0b1ab7 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_4a9cf0a65710: status=pass change=Add capability activation followup result ingestion files=agent_os/capability_activation_followup_results.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py evals=first_milestone_closed_loop runs=run_a3d4b9fcbe41 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_bff47ca6bd0f: status=pass change=Add capability followup delegation packets files=agent_os/capability_activation_followup_delegations.py,agent_os/profile_routing.py,agent_os/subagent_delegation.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,tests/test_first_milestone.py evals=first_milestone_closed_loop runs=run_b96ce8f34c7b results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md

## Learning Distillation

- status: stable
- stable_learnings: 1
- source_learnings: 24
- min_occurrences: 3
- report: docs/learning-distillation.md

- learning_distillation_255ae71ad9db: status=stable stable_learnings=1 source_learnings=24 min_occurrences=3 report=docs/learning-distillation.md
- Run run_<id> showed that the first closed loop can be verified through file evidence before expanding to broader domains. occurrences=24 runs=run_ef049fa8bc1b,run_442800b11c88,run_85aba7975e44,run_e00b0c8f8421,run_19c337ce39cd,run_e641748ed7b5,run_29f35bcd3c4a,run_5850098a3daf,run_bdee61e695bb,run_5c2e1d7e727b,run_395eef2e002e,run_9a7518e69a09,run_c43d94c11c75,run_24c24ce0765e,run_42129a67e1fe,run_5953ddebb94f,run_3f0260c058b7,run_4ca70d56e922,run_b3345106e3e7,run_e9eb60b88b08,run_aff094d41613,run_6bba00951a85,run_d1c5f8393518,run_ff65446deb79

## Memory Proposals

- memory_4bc20665a3ec: status=proposed project=bootstrap scope=project key=delegation_result_ingestion_smoke source=subagent_delegation:subagent_delegation_7c3ac6139928 confidence=0.7 artifact=/Users/reidar/Documents/Agent System/.clanker/memory/memory_4bc20665a3ec.json value=Smoke ingestion proved read-only result recording for the delegation loop.

## Skill Proposals

- skill_073a6967c3df: status=proposed project=bootstrap name=adding-cli-commands source_run=run_6fcdef549e8b verification=pending_operator_approval path=/Users/reidar/Documents/Agent System/.clanker/skills/adding-cli-commands/SKILL.md description=Procedure for adding tested CLI commands.

## Budget And Trust Posture

- status: report_only
- tasks: 435
- budget_state: not_tracked
- trust_state: not_tracked
- risk_counts: high=18,low=417
- report: docs/budget-trust-posture.md

- budget_trust_posture_2a45c238b87f: status=report_only tasks=435 budget_state=not_tracked trust_state=not_tracked risk_counts=high=18,low=417 report=docs/budget-trust-posture.md

## Dispatch Posture History

- status: report_only
- snapshots: 25
- latest_tasks: 435
- task_delta: 161
- latest_risk_counts: high=18,low=417
- report: docs/dispatch-posture-history.md

- dispatch_posture_history_01e722e5f040: status=report_only snapshots=25 latest_tasks=435 task_delta=161 latest_risk_counts=high=18,low=417 report=docs/dispatch-posture-history.md

## Dispatch Posture Snapshot Review

- status: fresh
- snapshots: 25
- stale_snapshots: 23
- latest_snapshot_age_seconds: 0
- stale_after_seconds: 3600
- report: docs/dispatch-posture-staleness.md

- dispatch_posture_staleness_5f543da96d3f: status=fresh snapshots=25 stale_snapshots=23 latest_snapshot_age_seconds=0 stale_after_seconds=3600 latest_tasks=435 latest_risk_counts=high=18,low=417 report=docs/dispatch-posture-staleness.md

## Dispatch Posture Refresh Recommendation

- status: no_refresh_needed
- source_review: dispatch_posture_staleness_5f543da96d3f
- source_status: fresh
- recommended_commands: none
- report: docs/dispatch-posture-refresh.md

- dispatch_posture_refresh_5b5ec5b44794: status=no_refresh_needed source_review=dispatch_posture_staleness_5f543da96d3f source_status=fresh recommended_commands=none report=docs/dispatch-posture-refresh.md

## Capability Expansion Ledger

- status: report_only
- capabilities: 9
- ready: 0
- deferred: 9
- approval_boundary: explicit_operator_approval_required
- report: docs/capability-expansion-ledger.md

- capability_expansion_ledger_ba3cef4c99b9: status=report_only capabilities=9 ready=0 deferred=9 approval_boundary=explicit_operator_approval_required report=docs/capability-expansion-ledger.md

## Capability Readiness Review

- status: blocked_by_missing_evidence
- source_ledger: capability_expansion_ledger_ba3cef4c99b9
- capabilities: 9
- ready: 0
- not_ready: 9
- missing_evidence: 9
- recommended_commands: none
- report: docs/capability-readiness-review.md

- capability_readiness_review_0128e9b65694: status=blocked_by_missing_evidence source_ledger=capability_expansion_ledger_ba3cef4c99b9 capabilities=9 ready=0 not_ready=9 missing_evidence=9 recommended_commands=none report=docs/capability-readiness-review.md

## Capability Proof Gap Index

- status: open_gaps
- source_review: capability_readiness_review_0128e9b65694
- capabilities: 9
- gaps: 9
- missing_evidence: 9
- blocked_capabilities: 9
- next_proofs: 9
- recommended_commands: none
- report: docs/capability-proof-gap-index.md

- capability_proof_gap_index_f6206bbf81b9: status=open_gaps source_review=capability_readiness_review_0128e9b65694 source_status=blocked_by_missing_evidence gaps=9 missing_evidence=9 blocked_capabilities=9 next_proofs=9 recommended_commands=none report=docs/capability-proof-gap-index.md

## Capability Approval Boundary Matrix

- status: approval_required
- source_index: capability_proof_gap_index_f6206bbf81b9
- capabilities: 9
- boundaries: 1
- gaps: 9
- blocked_capabilities: 9
- approvals_required: 9
- recommended_commands: none
- report: docs/capability-approval-boundary-matrix.md

- capability_approval_boundary_matrix_f44fd56de564: status=approval_required source_index=capability_proof_gap_index_f6206bbf81b9 source_status=open_gaps boundaries=1 gaps=9 blocked_capabilities=9 approvals_required=9 recommended_commands=none report=docs/capability-approval-boundary-matrix.md

## Capability Evidence Collection Plan

- status: evidence_required
- source_matrix: capability_approval_boundary_matrix_f44fd56de564
- capabilities: 9
- evidence_items: 9
- manual_collection: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-evidence-collection-plan.md

- capability_evidence_collection_plan_263fdaf29539: status=evidence_required source_matrix=capability_approval_boundary_matrix_f44fd56de564 source_status=approval_required evidence_items=9 manual_collection=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-evidence-collection-plan.md

## Capability Promotion Gate Checklist

- status: promotion_blocked
- source_plan: capability_evidence_collection_plan_263fdaf29539
- capabilities: 9
- gates: 9
- blocked_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-promotion-gate-checklist.md

- capability_promotion_gate_checklist_8d0a4df791a2: status=promotion_blocked source_plan=capability_evidence_collection_plan_263fdaf29539 source_status=evidence_required gates=9 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-gate-checklist.md

## Capability Promotion Decision Ledger

- status: promotion_decision_blocked
- source_checklist: capability_promotion_gate_checklist_8d0a4df791a2
- capabilities: 9
- decisions: 9
- deferred_promotions: 9
- operator_decisions_required: 0
- blocked_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-promotion-decision-ledger.md

- capability_promotion_decision_ledger_6a7434e0e6dc: status=promotion_decision_blocked source_checklist=capability_promotion_gate_checklist_8d0a4df791a2 source_status=promotion_blocked decisions=9 deferred_promotions=9 operator_decisions_required=0 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-decision-ledger.md

## Capability Trust Promotion Audit

- status: trust_promotion_blocked
- source_ledger: capability_promotion_decision_ledger_6a7434e0e6dc
- capabilities: 9
- audits: 9
- blocked_trust_promotions: 9
- operator_reviews_required: 0
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-trust-promotion-audit.md

- capability_trust_promotion_audit_4c345d316140: status=trust_promotion_blocked source_ledger=capability_promotion_decision_ledger_6a7434e0e6dc source_status=promotion_decision_blocked audits=9 blocked_trust_promotions=9 operator_reviews_required=0 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-trust-promotion-audit.md

## Capability Automatic Retry Audit

- status: automatic_retry_blocked
- source_audit: capability_trust_promotion_audit_4c345d316140
- capabilities: 9
- audits: 9
- blocked_retries: 9
- operator_reviews_required: 0
- blocked_trust_promotions: 9
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-automatic-retry-audit.md

- capability_automatic_retry_audit_6a7f2f760634: status=automatic_retry_blocked source_audit=capability_trust_promotion_audit_4c345d316140 source_status=trust_promotion_blocked audits=9 blocked_retries=9 operator_reviews_required=0 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-automatic-retry-audit.md

## Capability Real Cost Tracking Audit

- status: real_cost_tracking_blocked
- source_audit: capability_automatic_retry_audit_6a7f2f760634
- capabilities: 9
- audits: 9
- blocked_cost_tracking: 9
- operator_reviews_required: 0
- blocked_retries: 9
- blocked_trust_promotions: 9
- deferred_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-real-cost-tracking-audit.md

- capability_real_cost_tracking_audit_b8451bdaf165: status=real_cost_tracking_blocked source_audit=capability_automatic_retry_audit_6a7f2f760634 source_status=automatic_retry_blocked audits=9 blocked_cost_tracking=9 operator_reviews_required=0 blocked_retries=9 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-real-cost-tracking-audit.md

## Hosted Dashboard Proof Checklist

- status: hosted_dashboard_proof_blocked
- source_kind: real_cost_tracking_proof_checklist
- source_checklist: real_cost_tracking_proof_checklist_88b013aea03b
- source_audit: none
- source_status: real_cost_tracking_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_dashboard_proofs: 1
- operator_reviews_required: 0
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/hosted-dashboard-proof-checklist.md

- hosted_dashboard_proof_checklist_b2bcb40524e1: status=hosted_dashboard_proof_blocked source_kind=real_cost_tracking_proof_checklist source_checklist=real_cost_tracking_proof_checklist_88b013aea03b source_audit=none source_status=real_cost_tracking_proof_blocked checklist_items=1 blocked_dashboard_proofs=1 operator_reviews_required=0 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/hosted-dashboard-proof-checklist.md

## Remote Worker Proof Checklist

- status: remote_worker_proof_blocked
- source_checklist: hosted_dashboard_proof_checklist_b2bcb40524e1
- source_status: hosted_dashboard_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_worker_proofs: 1
- operator_reviews_required: 0
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/remote-worker-proof-checklist.md

- remote_worker_proof_checklist_7f7cd3aa32ea: status=remote_worker_proof_blocked source_checklist=hosted_dashboard_proof_checklist_b2bcb40524e1 source_status=hosted_dashboard_proof_blocked checklist_items=1 blocked_worker_proofs=1 operator_reviews_required=0 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/remote-worker-proof-checklist.md

## Autonomous Scheduling Proof Checklist

- status: autonomous_scheduling_proof_blocked
- source_checklist: remote_worker_proof_checklist_7f7cd3aa32ea
- source_status: remote_worker_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_scheduling_proofs: 1
- operator_reviews_required: 0
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/autonomous-scheduling-proof-checklist.md

- autonomous_scheduling_proof_checklist_c71c9bac6ad8: status=autonomous_scheduling_proof_blocked source_checklist=remote_worker_proof_checklist_7f7cd3aa32ea source_status=remote_worker_proof_blocked checklist_items=1 blocked_scheduling_proofs=1 operator_reviews_required=0 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/autonomous-scheduling-proof-checklist.md

## Browser Desktop Adapter Proof Checklist

- status: browser_desktop_adapter_proof_blocked
- source_checklist: autonomous_scheduling_proof_checklist_c71c9bac6ad8
- source_status: autonomous_scheduling_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_adapter_proofs: 1
- operator_reviews_required: 0
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/browser-desktop-adapter-proof-checklist.md

- browser_desktop_adapter_proof_checklist_f39a085d4b18: status=browser_desktop_adapter_proof_blocked source_checklist=autonomous_scheduling_proof_checklist_c71c9bac6ad8 source_status=autonomous_scheduling_proof_blocked checklist_items=1 blocked_adapter_proofs=1 operator_reviews_required=0 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/browser-desktop-adapter-proof-checklist.md

## CI Deploy Proof Checklist

- status: ci_deploy_proof_blocked
- source_checklist: browser_desktop_adapter_proof_checklist_f39a085d4b18
- source_status: browser_desktop_adapter_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_ci_deploy_proofs: 1
- operator_reviews_required: 0
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/ci-deploy-proof-checklist.md

- ci_deploy_proof_checklist_d1c6d0e922d5: status=ci_deploy_proof_blocked source_checklist=browser_desktop_adapter_proof_checklist_f39a085d4b18 source_status=browser_desktop_adapter_proof_blocked checklist_items=1 blocked_ci_deploy_proofs=1 operator_reviews_required=0 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/ci-deploy-proof-checklist.md

## Budget Enforcement Proof Checklist

- status: budget_enforcement_proof_blocked
- source_checklist: ci_deploy_proof_checklist_d1c6d0e922d5
- source_status: ci_deploy_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_budget_enforcement_proofs: 1
- operator_reviews_required: 0
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/budget-enforcement-proof-checklist.md

- budget_enforcement_proof_checklist_5438ba49e94f: status=budget_enforcement_proof_blocked source_checklist=ci_deploy_proof_checklist_d1c6d0e922d5 source_status=ci_deploy_proof_blocked checklist_items=1 blocked_budget_enforcement_proofs=1 operator_reviews_required=0 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/budget-enforcement-proof-checklist.md

## Trust Promotion Proof Checklist

- status: trust_promotion_proof_blocked
- source_checklist: budget_enforcement_proof_checklist_5438ba49e94f
- source_status: budget_enforcement_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_trust_promotion_proofs: 1
- operator_reviews_required: 0
- blocked_budget_enforcement_proofs: 1
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/trust-promotion-proof-checklist.md

- trust_promotion_proof_checklist_0f90a8c53b24: status=trust_promotion_proof_blocked source_checklist=budget_enforcement_proof_checklist_5438ba49e94f source_status=budget_enforcement_proof_blocked checklist_items=1 blocked_trust_promotion_proofs=1 operator_reviews_required=0 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/trust-promotion-proof-checklist.md

## Automatic Retry Proof Checklist

- status: automatic_retry_proof_blocked
- source_checklist: trust_promotion_proof_checklist_0f90a8c53b24
- source_status: trust_promotion_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_automatic_retry_proofs: 1
- operator_reviews_required: 0
- blocked_trust_promotion_proofs: 1
- blocked_budget_enforcement_proofs: 1
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/automatic-retry-proof-checklist.md

- automatic_retry_proof_checklist_e6b8dc080daf: status=automatic_retry_proof_blocked source_checklist=trust_promotion_proof_checklist_0f90a8c53b24 source_status=trust_promotion_proof_blocked checklist_items=1 blocked_automatic_retry_proofs=1 operator_reviews_required=0 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/automatic-retry-proof-checklist.md

## Real Cost Tracking Proof Checklist

- status: real_cost_tracking_proof_blocked
- source_checklist: automatic_retry_proof_checklist_e6b8dc080daf
- source_status: automatic_retry_proof_blocked
- capabilities: 1
- checklist_items: 1
- blocked_real_cost_tracking_proofs: 1
- operator_reviews_required: 0
- blocked_automatic_retry_proofs: 1
- blocked_trust_promotion_proofs: 1
- blocked_budget_enforcement_proofs: 1
- blocked_ci_deploy_proofs: 1
- blocked_adapter_proofs: 1
- blocked_scheduling_proofs: 1
- blocked_worker_proofs: 1
- blocked_dashboard_proofs: 1
- blocked_cost_tracking: 1
- blocked_retries: 1
- blocked_trust_promotions: 1
- missing_evidence: 1
- approvals_required: 1
- boundaries: 1
- recommended_commands: none
- report: docs/real-cost-tracking-proof-checklist.md

- real_cost_tracking_proof_checklist_12830b0001e4: status=real_cost_tracking_proof_blocked source_checklist=automatic_retry_proof_checklist_e6b8dc080daf source_status=automatic_retry_proof_blocked checklist_items=1 blocked_real_cost_tracking_proofs=1 operator_reviews_required=0 blocked_automatic_retry_proofs=1 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/real-cost-tracking-proof-checklist.md

## Goal Completion Audit

- status: blocked_by_report_only_proofs
- requirements: 9
- satisfied_requirements: 0
- blocked_requirements: 9
- missing_evidence: 9
- approvals_required: 9
- external_decisions_required: 2
- recommended_commands: none
- report: docs/goal-completion-audit.md

- goal_completion_audit_981a08705399: status=blocked_by_report_only_proofs requirements=9 satisfied_requirements=0 blocked_requirements=9 missing_evidence=9 approvals_required=9 external_decisions_required=2 recommended_commands=none report=docs/goal-completion-audit.md

## Expansion Decision Brief

- status: operator_decisions_required
- source_audit: goal_completion_audit_981a08705399
- source_status: blocked_by_report_only_proofs
- requirements: 9
- blocked_requirements: 9
- external_decisions_required: 2
- approvals_required: 9
- decision_items: 11
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-brief.md

- expansion_decision_brief_26db1de5231d: status=operator_decisions_required source_audit=goal_completion_audit_981a08705399 source_status=blocked_by_report_only_proofs requirements=9 blocked_requirements=9 external_decisions_required=2 approvals_required=9 decision_items=11 recommended_next_step=operator_review_required report=docs/expansion-decision-brief.md

## Expansion Decision Evidence Index

- status: evidence_indexed
- source_brief: expansion_decision_brief_26db1de5231d
- source_status: operator_decisions_required
- source_audit: goal_completion_audit_981a08705399
- decision_items: 11
- evidence_items: 11
- external_decisions: 2
- capability_decisions: 9
- missing_evidence_links: 0
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-evidence-index.md

- expansion_decision_evidence_index_77621150a88e: status=evidence_indexed source_brief=expansion_decision_brief_26db1de5231d source_status=operator_decisions_required source_audit=goal_completion_audit_981a08705399 decision_items=11 evidence_items=11 external_decisions=2 capability_decisions=9 missing_evidence_links=0 recommended_next_step=operator_review_required report=docs/expansion-decision-evidence-index.md

## Expansion Operator Review Checklist

- status: operator_review_required
- source_index: expansion_decision_evidence_index_77621150a88e
- source_status: evidence_indexed
- source_brief: expansion_decision_brief_26db1de5231d
- source_audit: goal_completion_audit_981a08705399
- review_items: 11
- decision_required: 11
- external_reviews: 2
- capability_reviews: 9
- missing_evidence_links: 0
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_decision_required
- report: docs/expansion-operator-review-checklist.md

- expansion_operator_review_checklist_7c4fcdf41f96: status=operator_review_required source_index=expansion_decision_evidence_index_77621150a88e source_status=evidence_indexed source_brief=expansion_decision_brief_26db1de5231d source_audit=goal_completion_audit_981a08705399 review_items=11 decision_required=11 external_reviews=2 capability_reviews=9 missing_evidence_links=0 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-review-checklist.md

## Expansion Operator Decision Ledger

- status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_7c4fcdf41f96
- source_status: operator_review_required
- source_index: expansion_decision_evidence_index_77621150a88e
- source_brief: expansion_decision_brief_26db1de5231d
- source_audit: goal_completion_audit_981a08705399
- decision_items: 11
- pending_decisions: 11
- approved_decisions: 0
- deferred_decisions: 0
- more_evidence_requested: 0
- external_decisions: 2
- capability_decisions: 9
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_decision_required
- report: docs/expansion-operator-decision-ledger.md

- expansion_operator_decision_ledger_21c9b282c06a: status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_7c4fcdf41f96 source_status=operator_review_required source_index=expansion_decision_evidence_index_77621150a88e source_brief=expansion_decision_brief_26db1de5231d source_audit=goal_completion_audit_981a08705399 decision_items=11 pending_decisions=11 approved_decisions=0 deferred_decisions=0 more_evidence_requested=0 external_decisions=2 capability_decisions=9 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-decision-ledger.md

## Expansion Operator Approval Draft

- status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_21c9b282c06a
- source_status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_7c4fcdf41f96
- source_index: expansion_decision_evidence_index_77621150a88e
- source_brief: expansion_decision_brief_26db1de5231d
- source_audit: goal_completion_audit_981a08705399
- draft_items: 11
- draft_requests: 11
- created_approval_requests: 0
- external_drafts: 2
- capability_drafts: 9
- approval_boundaries: 2
- pending_decisions: 11
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_approval_flow_required
- report: docs/expansion-operator-approval-draft.md

- expansion_operator_approval_draft_6cd8abd426f6: status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_21c9b282c06a source_status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_7c4fcdf41f96 source_index=expansion_decision_evidence_index_77621150a88e source_brief=expansion_decision_brief_26db1de5231d source_audit=goal_completion_audit_981a08705399 draft_items=11 draft_requests=11 created_approval_requests=0 external_drafts=2 capability_drafts=9 approval_boundaries=2 pending_decisions=11 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_approval_flow_required report=docs/expansion-operator-approval-draft.md

## Expansion Operator Approval Request Review

- status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_6cd8abd426f6
- source_status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_21c9b282c06a
- source_checklist: expansion_operator_review_checklist_7c4fcdf41f96
- source_index: expansion_decision_evidence_index_77621150a88e
- source_brief: expansion_decision_brief_26db1de5231d
- source_audit: goal_completion_audit_981a08705399
- draft_requests: 11
- review_items: 11
- ready_requests: 0
- blocked_requests: 11
- schema_gaps: 11
- created_approval_requests: 0
- existing_approval_requests: 0
- external_requests: 2
- capability_requests: 9
- approval_boundaries: 2
- recommended_next_step: approval_request_schema_decision_required
- report: docs/expansion-operator-approval-request-review.md

- expansion_operator_approval_request_review_56ad3802e63b: status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_6cd8abd426f6 source_status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_21c9b282c06a source_checklist=expansion_operator_review_checklist_7c4fcdf41f96 source_index=expansion_decision_evidence_index_77621150a88e source_brief=expansion_decision_brief_26db1de5231d source_audit=goal_completion_audit_981a08705399 draft_requests=11 review_items=11 ready_requests=0 blocked_requests=11 schema_gaps=11 created_approval_requests=0 existing_approval_requests=0 external_requests=2 capability_requests=9 approval_boundaries=2 recommended_next_step=approval_request_schema_decision_required report=docs/expansion-operator-approval-request-review.md

## Expansion Operator Approval Schema Migration Selection Input Template

- status: operator_approval_schema_migration_selection_input_required
- source_packet: expansion_operator_approval_schema_migration_selection_packet_a3c1283899d1
- source_status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_07a5199a1907
- source_checklist_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_272ffdcbec3b
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_5823fec40069
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_43782b35400e
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_0682a62c5642
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_56ad3802e63b
- source_review_status: approval_request_schema_review_required
- target_table: operator_approval_requests
- request_count: 1
- decision_count: 1
- pending_decisions: 1
- action_count: 1
- pending_actions: 1
- actions_taken: 0
- selected_action: none
- selection_count: 1
- pending_selections: 1
- selections_recorded: 0
- approve_selections: 0
- defer_selections: 0
- more_evidence_selections: 0
- template_count: 1
- pending_inputs: 1
- inputs_recorded: 0
- required_fields_count: 4
- missing_required_inputs: 4
- approval_boundary: schema_migration
- requested_action: apply_operator_approval_requests_schema
- allowed_actions: approve,defer,request_more_evidence
- migration_applied: 0
- table_created: 0
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- recommended_next_step: operator_approval_schema_migration_operator_input_required
- report: docs/expansion-operator-approval-schema-migration-selection-input-template.md

- expansion_operator_approval_schema_migration_selection_input_template_b8c40b3db9f1: status=operator_approval_schema_migration_selection_input_required source_packet=expansion_operator_approval_schema_migration_selection_packet_a3c1283899d1 source_status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_07a5199a1907 source_checklist_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_272ffdcbec3b source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_5823fec40069 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_43782b35400e source_plan_status=operator_approval_schema_migration_plan_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 template_count=1 pending_inputs=1 inputs_recorded=0 required_fields_count=4 missing_required_inputs=4 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_input_required report=docs/expansion-operator-approval-schema-migration-selection-input-template.md

## Expansion Operator Approval Schema Migration Application

- status: operator_approval_schema_migration_applied
- source_template: expansion_operator_approval_schema_migration_selection_input_template_f996d5f4b462
- source_status: operator_approval_schema_migration_selection_input_required
- source_packet: expansion_operator_approval_schema_migration_selection_packet_5b00d71060c7
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_d2536bf7efc4
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_05d8ff4beb6a
- source_request: expansion_operator_approval_schema_migration_approval_request_cd8b40d8168e
- source_plan: expansion_operator_approval_schema_migration_plan_14f74e1e91ad
- source_decision: expansion_operator_approval_schema_decision_2c10728733d4
- source_review: expansion_operator_approval_request_review_718ad693cf0f
- target_table: operator_approval_requests
- operator_id: operator
- selected_action: approve
- inputs_recorded: 1
- missing_required_inputs: 0
- actions_taken: 1
- migration_applied: 1
- table_created: 1
- operator_approval_rows_created: 0
- approval_requests_created: 0
- existing_approval_requests: 0
- report: docs/expansion-operator-approval-schema-migration-application.md

- operator_approval_schema_migration_application_58b1de2348a1: status=operator_approval_schema_migration_applied source_template=expansion_operator_approval_schema_migration_selection_input_template_f996d5f4b462 target_table=operator_approval_requests operator_id=operator selected_action=approve inputs_recorded=1 actions_taken=1 migration_applied=1 table_created=1 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 report=docs/expansion-operator-approval-schema-migration-application.md

## Expansion Operator Approval Request Rows Application

- status: operator_approval_request_rows_applied
- source_draft: expansion_operator_approval_draft_93697a4315da
- source_status: approval_draft_ready
- source_schema_application: operator_approval_schema_migration_application_58b1de2348a1
- source_schema_status: operator_approval_schema_migration_applied
- source_ledger: expansion_operator_decision_ledger_51c1e0f289fa
- source_checklist: expansion_operator_review_checklist_f01aaf772dab
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
- operator_id: operator
- selected_action: approve
- draft_requests: 11
- operator_approval_rows_created: 11
- approval_requests_created: 0
- existing_operator_approval_requests: 0
- external_requests: 2
- capability_requests: 9
- report: docs/expansion-operator-approval-request-rows-application.md

- operator_approval_request_row_application_9d1c3e1d4012: status=operator_approval_request_rows_applied source_draft=expansion_operator_approval_draft_93697a4315da source_schema_application=operator_approval_schema_migration_application_58b1de2348a1 operator_id=operator selected_action=approve draft_requests=11 operator_approval_rows_created=11 approval_requests_created=0 existing_operator_approval_requests=0 external_requests=2 capability_requests=9 report=docs/expansion-operator-approval-request-rows-application.md

## Playbooks

- active: 1

- first-milestone-closed-loop: active source=first_milestone_closed_loop successful_runs=214 path=playbooks/first-milestone-closed-loop.md

## Eval Candidates

- proposed: 0

- none

## Approvals

- pending: 0
- approved: 0
- rejected: 0

- none

## Stuck Tasks

- open: 0

- none

## Incidents

- open: 0
- resolved: 0

- none

## Recent Runs

- run_9a36a417e092: completed project=bootstrap goal=goal_1c1fe1c4765c completed=2026-06-22T18:45:21.577172+00:00 summary=runs/run_9a36a417e092/summary.md
- run_357ca9a6d7fa: completed project=bootstrap goal=goal_2d9940130246 completed=2026-06-22T18:45:13.024906+00:00 summary=runs/run_357ca9a6d7fa/summary.md
- run_de3c184afb5d: completed project=bootstrap goal=goal_ed5ccdae8879 completed=2026-06-22T18:27:31.238039+00:00 summary=runs/run_de3c184afb5d/summary.md
- run_6aaaf091a7a0: completed project=bootstrap goal=goal_8d3dcd80bf65 completed=2026-06-22T18:26:48.124142+00:00 summary=runs/run_6aaaf091a7a0/summary.md
- run_f95f1af299b5: completed project=bootstrap goal=goal_16cd2dfb922c completed=2026-06-22T18:07:57.628382+00:00 summary=runs/run_f95f1af299b5/summary.md

## Recent Evidence Packets

- none

## Recent Learnings

- run_9a36a417e092: Run run_9a36a417e092 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_9a36a417e092/learning.md)
- run_357ca9a6d7fa: Run run_357ca9a6d7fa showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_357ca9a6d7fa/learning.md)
- run_de3c184afb5d: Run run_de3c184afb5d showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_de3c184afb5d/learning.md)
- run_6aaaf091a7a0: Run run_6aaaf091a7a0 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_6aaaf091a7a0/learning.md)
- run_f95f1af299b5: Run run_f95f1af299b5 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_f95f1af299b5/learning.md)

## Recent Eval Results

- first_milestone_closed_loop: pass run=run_9a36a417e092 created_at=2026-06-22T18:45:21.585582+00:00
- first_milestone_closed_loop: pass run=run_357ca9a6d7fa created_at=2026-06-22T18:45:13.034610+00:00
- first_milestone_closed_loop: pass run=run_de3c184afb5d created_at=2026-06-22T18:27:31.247400+00:00
- first_milestone_closed_loop: pass run=run_6aaaf091a7a0 created_at=2026-06-22T18:26:48.134564+00:00
- first_milestone_closed_loop: pass run=run_f95f1af299b5 created_at=2026-06-22T18:07:57.641026+00:00
