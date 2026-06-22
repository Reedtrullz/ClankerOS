# Agent System Dashboard

## Operator Cockpit

### Active Goals/Runs

- none

### Registered Projects

- none

### Approval Inbox

- none

### Proposed Effects

- effect_1a41ff7c5cca: operator_capability_proposal status=applied approval=operator_approval_request_c59b82c4f7c3 project=bootstrap target=real_cost_tracking evidence=docs/expansion-operator-approval-effect-application.md
- effect_e5a56b95d9ce: operator_capability_proposal status=applied approval=operator_approval_request_239a407346df project=bootstrap target=automatic_retries evidence=docs/expansion-operator-approval-effect-application.md
- effect_549912b53e8e: operator_capability_proposal status=applied approval=operator_approval_request_582f7bfe609c project=bootstrap target=trust_promotion evidence=docs/expansion-operator-approval-effect-application.md
- effect_9ad8411cfe14: operator_capability_proposal status=applied approval=operator_approval_request_21a453d20186 project=bootstrap target=budget_enforcement evidence=docs/expansion-operator-approval-effect-application.md
- effect_1e2d271e79f3: operator_capability_proposal status=applied approval=operator_approval_request_6a498ab280e1 project=bootstrap target=ci_deploy_proof evidence=docs/expansion-operator-approval-effect-application.md

### Recent Commits/Effects

- effect_1a41ff7c5cca: operator_capability_proposal status=applied committed_at=not_committed commit=none
- effect_e5a56b95d9ce: operator_capability_proposal status=applied committed_at=not_committed commit=none
- effect_549912b53e8e: operator_capability_proposal status=applied committed_at=not_committed commit=none
- effect_9ad8411cfe14: operator_capability_proposal status=applied committed_at=not_committed commit=none
- effect_1e2d271e79f3: operator_capability_proposal status=applied committed_at=not_committed commit=none

### Incidents

- none

### Verification Status

- effect_1a41ff7c5cca: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_e5a56b95d9ce: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_549912b53e8e: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_9ad8411cfe14: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json
- effect_1e2d271e79f3: missing method=unknown command_exit=unknown tests_exit=unknown evidence=docs/verification.json

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
- routing_decision_913d11bcaef2: category=test_triage selected=tester model=configurable/cheap-coding-model cost=low task=task_37d1509ef90f project=bootstrap status=selected
- routing_decision_3d77ced38bf2: category=repo_search selected=scout model=configurable/cheap-fast-model cost=low task=none project=bootstrap status=selected

### Subagent Delegations

- subagent_delegation_7c3ac6139928: status=completed profile=tester category=test_triage task=task_37d1509ef90f schema=failing_test_summary artifact=/Users/reidar/Documents/Agent System/.clanker/delegations/subagent_delegation_7c3ac6139928-result.json summary=Smoke ingestion proved read-only result recording for the delegation loop.

## Steering Reviews

- steer_4a39cbdcc894: status=clear goal=goal_3010379344ae run=run_d52df83d4bba drift=none action=continue requires_operator=false report=docs/steering-review.md

### Next Recommended Action

- Review recent proposed effects and regenerate the dashboard after decisions.

## Queue Health

- pending: 0
- waiting_approval: 0
- claimed: 0
- running: 0
- verifying: 0
- completed: 401
- blocked: 0
- failed: 0
- active: 0
- needs_attention: 0

## Iteration Loop

- status: planned
- focus: Add capability-specific activation tasks from applied operator approval effects.
- source: tasks.md#next
- packet: docs/next-iteration.md
- created_at: 2026-06-22T15:49:04.263477+00:00

## Simplicity Guardrail

- policy: highest-score-then-lowest-complexity
- reason: selected only actionable item with score 9 and complexity 4
- selected_score: 9
- selected_complexity: 4
- selected_focus: Add capability-specific activation tasks from applied operator approval effects.

## Expansion Operator Approval Schema Decision

- status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
- source_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_912a128e4891
- source_ledger: expansion_operator_decision_ledger_69572a6acdfa
- source_checklist: expansion_operator_review_checklist_4c25f852c022
- source_index: expansion_decision_evidence_index_0dc19502eb59
- source_brief: expansion_decision_brief_9e899bc00c50
- source_audit: goal_completion_audit_52df6b8c2e20
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

- expansion_operator_approval_schema_decision_20d31b1c6e4f: status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_9f730b6a62fb source_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_912a128e4891 source_ledger=expansion_operator_decision_ledger_69572a6acdfa source_checklist=expansion_operator_review_checklist_4c25f852c022 source_index=expansion_decision_evidence_index_0dc19502eb59 source_brief=expansion_decision_brief_9e899bc00c50 source_audit=goal_completion_audit_52df6b8c2e20 affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 decision_options=3 recommended_option=operator_approval_requests_table rejected_options=2 schema_objects=1 migration_applied=0 created_approval_requests=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_plan_required report=docs/expansion-operator-approval-schema-decision.md

## Expansion Operator Approval Schema Migration Plan

- status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_20d31b1c6e4f
- source_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
- source_review_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_912a128e4891
- source_ledger: expansion_operator_decision_ledger_69572a6acdfa
- source_checklist: expansion_operator_review_checklist_4c25f852c022
- source_index: expansion_decision_evidence_index_0dc19502eb59
- source_brief: expansion_decision_brief_9e899bc00c50
- source_audit: goal_completion_audit_52df6b8c2e20
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

- expansion_operator_approval_schema_migration_plan_230532bbadd3: status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_20d31b1c6e4f source_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_9f730b6a62fb source_review_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_912a128e4891 source_ledger=expansion_operator_decision_ledger_69572a6acdfa source_checklist=expansion_operator_review_checklist_4c25f852c022 source_index=expansion_decision_evidence_index_0dc19502eb59 source_brief=expansion_decision_brief_9e899bc00c50 source_audit=goal_completion_audit_52df6b8c2e20 recommended_option=operator_approval_requests_table target_table=operator_approval_requests affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 planned_columns=26 planned_indexes=4 migration_steps=4 migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_approval_required report=docs/expansion-operator-approval-schema-migration-plan.md

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

- operator_approval_effect_application_a007e2ecce01: status=operator_approval_effect_application_already_recorded operator_id=operator proposed_effects=0 effects_applied=0 existing_applied_effects=11 external_effects=0 capability_effects=0 activation_actions=0 legacy_approval_requests=0 report=docs/expansion-operator-approval-effect-application.md

## Expansion Operator Approval Schema Migration Approval Request

- status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_230532bbadd3
- source_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_20d31b1c6e4f
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
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

- expansion_operator_approval_schema_migration_approval_request_1bcc87e59059: status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_230532bbadd3 source_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_20d31b1c6e4f source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_9f730b6a62fb source_review_status=approval_request_schema_review_required target_table=operator_approval_requests planned_columns=26 planned_indexes=4 migration_steps=4 affected_requests=11 schema_gaps=11 request_count=1 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_decision_required report=docs/expansion-operator-approval-schema-migration-approval-request.md

## Expansion Operator Approval Schema Migration Decision Ledger

- status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_1bcc87e59059
- source_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_230532bbadd3
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_20d31b1c6e4f
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
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

- expansion_operator_approval_schema_migration_decision_ledger_aeb1a7b61e81: status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_1bcc87e59059 source_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_230532bbadd3 source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_20d31b1c6e4f source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_9f730b6a62fb source_review_status=approval_request_schema_review_required target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 approved_decisions=0 deferred_decisions=0 more_evidence_decisions=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_action_required report=docs/expansion-operator-approval-schema-migration-decision-ledger.md

## Expansion Operator Approval Schema Migration Action Checklist

- status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_aeb1a7b61e81
- source_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_1bcc87e59059
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_230532bbadd3
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_20d31b1c6e4f
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
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

- expansion_operator_approval_schema_migration_action_checklist_4e48e8b0319c: status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_aeb1a7b61e81 source_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_1bcc87e59059 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_230532bbadd3 source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_20d31b1c6e4f source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_required report=docs/expansion-operator-approval-schema-migration-action-checklist.md

## Expansion Operator Approval Schema Migration Selection Packet

- status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_4e48e8b0319c
- source_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_aeb1a7b61e81
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_1bcc87e59059
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_230532bbadd3
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_20d31b1c6e4f
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
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

- expansion_operator_approval_schema_migration_selection_packet_f3401939e50a: status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_4e48e8b0319c source_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_aeb1a7b61e81 source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_1bcc87e59059 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_230532bbadd3 source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_20d31b1c6e4f source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 approve_selections=0 defer_selections=0 more_evidence_selections=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_input_required report=docs/expansion-operator-approval-schema-migration-selection-packet.md

## Queue Health Checks

- blocked_threshold: 2
- failed_threshold: 2
- hotspots: 0

- none

## Handoff Review

- status: clear
- current_focus: Add capability-specific activation tasks from applied operator approval effects.
- blocked_tasks: 0
- stale_handoffs: 0
- report: docs/handoff-review.md

- none

## Eval After Change

- failed: 0

- eval_after_change_458109310ed9: status=pass change=Add operator approval effect application files=agent_os/operator_approval_effect_application.py,agent_os/operator_approval_effect_proposals.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-effect-proposals.md,docs/suggested-use.md,README.md evals=first_milestone_closed_loop runs=run_f3f628326998 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_a12fba6f9fb8: status=pass change=Add operator approval effect proposals files=agent_os/operator_approval_effect_proposals.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-effect-proposals.md,docs/suggested-use.md,README.md evals=first_milestone_closed_loop runs=run_706a409ddded results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_9826c9e77cfc: status=pass change=Add operator approval request decisions files=agent_os/operator_approval_request_decisions.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-schema.md evals=first_milestone_closed_loop runs=run_0080e0fe7462 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_a58ebbfd08d2: status=pass change=Add operator approval request row application files=agent_os/operator_approval_request_rows.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-schema.md evals=first_milestone_closed_loop runs=run_69b9d4af9bf1 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_4b8b415ba010: status=pass change=Apply operator approval request schema files=agent_os/operator_approval_schema_migration.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-schema.md,README.md,docs/suggested-use.md,projects/bootstrap/handoff.md evals=first_milestone_closed_loop runs=run_3d755f0aab76 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md

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
- tasks: 399
- budget_state: not_tracked
- trust_state: not_tracked
- risk_counts: low=399
- report: docs/budget-trust-posture.md

- budget_trust_posture_64f1c621757a: status=report_only tasks=399 budget_state=not_tracked trust_state=not_tracked risk_counts=low=399 report=docs/budget-trust-posture.md

## Dispatch Posture History

- status: report_only
- snapshots: 25
- latest_tasks: 399
- task_delta: 149
- latest_risk_counts: low=399
- report: docs/dispatch-posture-history.md

- dispatch_posture_history_3194b33ec8da: status=report_only snapshots=25 latest_tasks=399 task_delta=149 latest_risk_counts=low=399 report=docs/dispatch-posture-history.md

## Dispatch Posture Snapshot Review

- status: fresh
- snapshots: 25
- stale_snapshots: 23
- latest_snapshot_age_seconds: 0
- stale_after_seconds: 3600
- report: docs/dispatch-posture-staleness.md

- dispatch_posture_staleness_a76cf33d0b66: status=fresh snapshots=25 stale_snapshots=23 latest_snapshot_age_seconds=0 stale_after_seconds=3600 latest_tasks=399 latest_risk_counts=low=399 report=docs/dispatch-posture-staleness.md

## Dispatch Posture Refresh Recommendation

- status: no_refresh_needed
- source_review: dispatch_posture_staleness_a76cf33d0b66
- source_status: fresh
- recommended_commands: none
- report: docs/dispatch-posture-refresh.md

- dispatch_posture_refresh_b7f1b7f3ead4: status=no_refresh_needed source_review=dispatch_posture_staleness_a76cf33d0b66 source_status=fresh recommended_commands=none report=docs/dispatch-posture-refresh.md

## Capability Expansion Ledger

- status: report_only
- capabilities: 9
- ready: 0
- deferred: 9
- approval_boundary: explicit_operator_approval_required
- report: docs/capability-expansion-ledger.md

- capability_expansion_ledger_5b0420fb7aa8: status=report_only capabilities=9 ready=0 deferred=9 approval_boundary=explicit_operator_approval_required report=docs/capability-expansion-ledger.md

## Capability Readiness Review

- status: blocked_by_missing_evidence
- source_ledger: capability_expansion_ledger_5b0420fb7aa8
- capabilities: 9
- ready: 0
- not_ready: 9
- missing_evidence: 9
- recommended_commands: none
- report: docs/capability-readiness-review.md

- capability_readiness_review_001532903395: status=blocked_by_missing_evidence source_ledger=capability_expansion_ledger_5b0420fb7aa8 capabilities=9 ready=0 not_ready=9 missing_evidence=9 recommended_commands=none report=docs/capability-readiness-review.md

## Capability Proof Gap Index

- status: open_gaps
- source_review: capability_readiness_review_001532903395
- capabilities: 9
- gaps: 9
- missing_evidence: 9
- blocked_capabilities: 9
- next_proofs: 9
- recommended_commands: none
- report: docs/capability-proof-gap-index.md

- capability_proof_gap_index_2f8b9f2a0b19: status=open_gaps source_review=capability_readiness_review_001532903395 source_status=blocked_by_missing_evidence gaps=9 missing_evidence=9 blocked_capabilities=9 next_proofs=9 recommended_commands=none report=docs/capability-proof-gap-index.md

## Capability Approval Boundary Matrix

- status: approval_required
- source_index: capability_proof_gap_index_2f8b9f2a0b19
- capabilities: 9
- boundaries: 1
- gaps: 9
- blocked_capabilities: 9
- approvals_required: 9
- recommended_commands: none
- report: docs/capability-approval-boundary-matrix.md

- capability_approval_boundary_matrix_3b4c0a104669: status=approval_required source_index=capability_proof_gap_index_2f8b9f2a0b19 source_status=open_gaps boundaries=1 gaps=9 blocked_capabilities=9 approvals_required=9 recommended_commands=none report=docs/capability-approval-boundary-matrix.md

## Capability Evidence Collection Plan

- status: evidence_required
- source_matrix: capability_approval_boundary_matrix_3b4c0a104669
- capabilities: 9
- evidence_items: 9
- manual_collection: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-evidence-collection-plan.md

- capability_evidence_collection_plan_397193cdab97: status=evidence_required source_matrix=capability_approval_boundary_matrix_3b4c0a104669 source_status=approval_required evidence_items=9 manual_collection=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-evidence-collection-plan.md

## Capability Promotion Gate Checklist

- status: promotion_blocked
- source_plan: capability_evidence_collection_plan_397193cdab97
- capabilities: 9
- gates: 9
- blocked_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-promotion-gate-checklist.md

- capability_promotion_gate_checklist_3280f4160e77: status=promotion_blocked source_plan=capability_evidence_collection_plan_397193cdab97 source_status=evidence_required gates=9 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-gate-checklist.md

## Capability Promotion Decision Ledger

- status: promotion_decision_blocked
- source_checklist: capability_promotion_gate_checklist_3280f4160e77
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

- capability_promotion_decision_ledger_7454c334c39f: status=promotion_decision_blocked source_checklist=capability_promotion_gate_checklist_3280f4160e77 source_status=promotion_blocked decisions=9 deferred_promotions=9 operator_decisions_required=0 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-decision-ledger.md

## Capability Trust Promotion Audit

- status: trust_promotion_blocked
- source_ledger: capability_promotion_decision_ledger_7454c334c39f
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

- capability_trust_promotion_audit_2db07351b603: status=trust_promotion_blocked source_ledger=capability_promotion_decision_ledger_7454c334c39f source_status=promotion_decision_blocked audits=9 blocked_trust_promotions=9 operator_reviews_required=0 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-trust-promotion-audit.md

## Capability Automatic Retry Audit

- status: automatic_retry_blocked
- source_audit: capability_trust_promotion_audit_2db07351b603
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

- capability_automatic_retry_audit_6b1cbb426bce: status=automatic_retry_blocked source_audit=capability_trust_promotion_audit_2db07351b603 source_status=trust_promotion_blocked audits=9 blocked_retries=9 operator_reviews_required=0 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-automatic-retry-audit.md

## Capability Real Cost Tracking Audit

- status: real_cost_tracking_blocked
- source_audit: capability_automatic_retry_audit_6b1cbb426bce
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

- capability_real_cost_tracking_audit_19c4d6c3a07b: status=real_cost_tracking_blocked source_audit=capability_automatic_retry_audit_6b1cbb426bce source_status=automatic_retry_blocked audits=9 blocked_cost_tracking=9 operator_reviews_required=0 blocked_retries=9 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-real-cost-tracking-audit.md

## Hosted Dashboard Proof Checklist

- status: hosted_dashboard_proof_blocked
- source_kind: real_cost_tracking_proof_checklist
- source_checklist: real_cost_tracking_proof_checklist_adbaffc3a981
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

- hosted_dashboard_proof_checklist_eb52d24e3dd1: status=hosted_dashboard_proof_blocked source_kind=real_cost_tracking_proof_checklist source_checklist=real_cost_tracking_proof_checklist_adbaffc3a981 source_audit=none source_status=real_cost_tracking_proof_blocked checklist_items=1 blocked_dashboard_proofs=1 operator_reviews_required=0 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/hosted-dashboard-proof-checklist.md

## Remote Worker Proof Checklist

- status: remote_worker_proof_blocked
- source_checklist: hosted_dashboard_proof_checklist_eb52d24e3dd1
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

- remote_worker_proof_checklist_9e7dd04092a1: status=remote_worker_proof_blocked source_checklist=hosted_dashboard_proof_checklist_eb52d24e3dd1 source_status=hosted_dashboard_proof_blocked checklist_items=1 blocked_worker_proofs=1 operator_reviews_required=0 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/remote-worker-proof-checklist.md

## Autonomous Scheduling Proof Checklist

- status: autonomous_scheduling_proof_blocked
- source_checklist: remote_worker_proof_checklist_9e7dd04092a1
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

- autonomous_scheduling_proof_checklist_e8a19fb6af8a: status=autonomous_scheduling_proof_blocked source_checklist=remote_worker_proof_checklist_9e7dd04092a1 source_status=remote_worker_proof_blocked checklist_items=1 blocked_scheduling_proofs=1 operator_reviews_required=0 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/autonomous-scheduling-proof-checklist.md

## Browser Desktop Adapter Proof Checklist

- status: browser_desktop_adapter_proof_blocked
- source_checklist: autonomous_scheduling_proof_checklist_e8a19fb6af8a
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

- browser_desktop_adapter_proof_checklist_a7498dbb4827: status=browser_desktop_adapter_proof_blocked source_checklist=autonomous_scheduling_proof_checklist_e8a19fb6af8a source_status=autonomous_scheduling_proof_blocked checklist_items=1 blocked_adapter_proofs=1 operator_reviews_required=0 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/browser-desktop-adapter-proof-checklist.md

## CI Deploy Proof Checklist

- status: ci_deploy_proof_blocked
- source_checklist: browser_desktop_adapter_proof_checklist_a7498dbb4827
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

- ci_deploy_proof_checklist_1571d0b45a33: status=ci_deploy_proof_blocked source_checklist=browser_desktop_adapter_proof_checklist_a7498dbb4827 source_status=browser_desktop_adapter_proof_blocked checklist_items=1 blocked_ci_deploy_proofs=1 operator_reviews_required=0 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/ci-deploy-proof-checklist.md

## Budget Enforcement Proof Checklist

- status: budget_enforcement_proof_blocked
- source_checklist: ci_deploy_proof_checklist_1571d0b45a33
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

- budget_enforcement_proof_checklist_964447bda567: status=budget_enforcement_proof_blocked source_checklist=ci_deploy_proof_checklist_1571d0b45a33 source_status=ci_deploy_proof_blocked checklist_items=1 blocked_budget_enforcement_proofs=1 operator_reviews_required=0 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/budget-enforcement-proof-checklist.md

## Trust Promotion Proof Checklist

- status: trust_promotion_proof_blocked
- source_checklist: budget_enforcement_proof_checklist_964447bda567
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

- trust_promotion_proof_checklist_55058f49e569: status=trust_promotion_proof_blocked source_checklist=budget_enforcement_proof_checklist_964447bda567 source_status=budget_enforcement_proof_blocked checklist_items=1 blocked_trust_promotion_proofs=1 operator_reviews_required=0 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/trust-promotion-proof-checklist.md

## Automatic Retry Proof Checklist

- status: automatic_retry_proof_blocked
- source_checklist: trust_promotion_proof_checklist_55058f49e569
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

- automatic_retry_proof_checklist_63533758ec7a: status=automatic_retry_proof_blocked source_checklist=trust_promotion_proof_checklist_55058f49e569 source_status=trust_promotion_proof_blocked checklist_items=1 blocked_automatic_retry_proofs=1 operator_reviews_required=0 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/automatic-retry-proof-checklist.md

## Real Cost Tracking Proof Checklist

- status: real_cost_tracking_proof_blocked
- source_checklist: automatic_retry_proof_checklist_63533758ec7a
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

- real_cost_tracking_proof_checklist_9a086155d146: status=real_cost_tracking_proof_blocked source_checklist=automatic_retry_proof_checklist_63533758ec7a source_status=automatic_retry_proof_blocked checklist_items=1 blocked_real_cost_tracking_proofs=1 operator_reviews_required=0 blocked_automatic_retry_proofs=1 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/real-cost-tracking-proof-checklist.md

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

- goal_completion_audit_52df6b8c2e20: status=blocked_by_report_only_proofs requirements=9 satisfied_requirements=0 blocked_requirements=9 missing_evidence=9 approvals_required=9 external_decisions_required=2 recommended_commands=none report=docs/goal-completion-audit.md

## Expansion Decision Brief

- status: operator_decisions_required
- source_audit: goal_completion_audit_52df6b8c2e20
- source_status: blocked_by_report_only_proofs
- requirements: 9
- blocked_requirements: 9
- external_decisions_required: 2
- approvals_required: 9
- decision_items: 11
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-brief.md

- expansion_decision_brief_9e899bc00c50: status=operator_decisions_required source_audit=goal_completion_audit_52df6b8c2e20 source_status=blocked_by_report_only_proofs requirements=9 blocked_requirements=9 external_decisions_required=2 approvals_required=9 decision_items=11 recommended_next_step=operator_review_required report=docs/expansion-decision-brief.md

## Expansion Decision Evidence Index

- status: evidence_indexed
- source_brief: expansion_decision_brief_9e899bc00c50
- source_status: operator_decisions_required
- source_audit: goal_completion_audit_52df6b8c2e20
- decision_items: 11
- evidence_items: 11
- external_decisions: 2
- capability_decisions: 9
- missing_evidence_links: 0
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-evidence-index.md

- expansion_decision_evidence_index_0dc19502eb59: status=evidence_indexed source_brief=expansion_decision_brief_9e899bc00c50 source_status=operator_decisions_required source_audit=goal_completion_audit_52df6b8c2e20 decision_items=11 evidence_items=11 external_decisions=2 capability_decisions=9 missing_evidence_links=0 recommended_next_step=operator_review_required report=docs/expansion-decision-evidence-index.md

## Expansion Operator Review Checklist

- status: operator_review_required
- source_index: expansion_decision_evidence_index_0dc19502eb59
- source_status: evidence_indexed
- source_brief: expansion_decision_brief_9e899bc00c50
- source_audit: goal_completion_audit_52df6b8c2e20
- review_items: 11
- decision_required: 11
- external_reviews: 2
- capability_reviews: 9
- missing_evidence_links: 0
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_decision_required
- report: docs/expansion-operator-review-checklist.md

- expansion_operator_review_checklist_4c25f852c022: status=operator_review_required source_index=expansion_decision_evidence_index_0dc19502eb59 source_status=evidence_indexed source_brief=expansion_decision_brief_9e899bc00c50 source_audit=goal_completion_audit_52df6b8c2e20 review_items=11 decision_required=11 external_reviews=2 capability_reviews=9 missing_evidence_links=0 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-review-checklist.md

## Expansion Operator Decision Ledger

- status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_4c25f852c022
- source_status: operator_review_required
- source_index: expansion_decision_evidence_index_0dc19502eb59
- source_brief: expansion_decision_brief_9e899bc00c50
- source_audit: goal_completion_audit_52df6b8c2e20
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

- expansion_operator_decision_ledger_69572a6acdfa: status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_4c25f852c022 source_status=operator_review_required source_index=expansion_decision_evidence_index_0dc19502eb59 source_brief=expansion_decision_brief_9e899bc00c50 source_audit=goal_completion_audit_52df6b8c2e20 decision_items=11 pending_decisions=11 approved_decisions=0 deferred_decisions=0 more_evidence_requested=0 external_decisions=2 capability_decisions=9 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-decision-ledger.md

## Expansion Operator Approval Draft

- status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_69572a6acdfa
- source_status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_4c25f852c022
- source_index: expansion_decision_evidence_index_0dc19502eb59
- source_brief: expansion_decision_brief_9e899bc00c50
- source_audit: goal_completion_audit_52df6b8c2e20
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

- expansion_operator_approval_draft_912a128e4891: status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_69572a6acdfa source_status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_4c25f852c022 source_index=expansion_decision_evidence_index_0dc19502eb59 source_brief=expansion_decision_brief_9e899bc00c50 source_audit=goal_completion_audit_52df6b8c2e20 draft_items=11 draft_requests=11 created_approval_requests=0 external_drafts=2 capability_drafts=9 approval_boundaries=2 pending_decisions=11 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_approval_flow_required report=docs/expansion-operator-approval-draft.md

## Expansion Operator Approval Request Review

- status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_912a128e4891
- source_status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_69572a6acdfa
- source_checklist: expansion_operator_review_checklist_4c25f852c022
- source_index: expansion_decision_evidence_index_0dc19502eb59
- source_brief: expansion_decision_brief_9e899bc00c50
- source_audit: goal_completion_audit_52df6b8c2e20
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

- expansion_operator_approval_request_review_9f730b6a62fb: status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_912a128e4891 source_status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_69572a6acdfa source_checklist=expansion_operator_review_checklist_4c25f852c022 source_index=expansion_decision_evidence_index_0dc19502eb59 source_brief=expansion_decision_brief_9e899bc00c50 source_audit=goal_completion_audit_52df6b8c2e20 draft_requests=11 review_items=11 ready_requests=0 blocked_requests=11 schema_gaps=11 created_approval_requests=0 existing_approval_requests=0 external_requests=2 capability_requests=9 approval_boundaries=2 recommended_next_step=approval_request_schema_decision_required report=docs/expansion-operator-approval-request-review.md

## Expansion Operator Approval Schema Migration Selection Input Template

- status: operator_approval_schema_migration_selection_input_required
- source_packet: expansion_operator_approval_schema_migration_selection_packet_f3401939e50a
- source_status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_4e48e8b0319c
- source_checklist_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_aeb1a7b61e81
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_1bcc87e59059
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_230532bbadd3
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_20d31b1c6e4f
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_9f730b6a62fb
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

- expansion_operator_approval_schema_migration_selection_input_template_ef6b84ceae2e: status=operator_approval_schema_migration_selection_input_required source_packet=expansion_operator_approval_schema_migration_selection_packet_f3401939e50a source_status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_4e48e8b0319c source_checklist_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_aeb1a7b61e81 source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_1bcc87e59059 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_230532bbadd3 source_plan_status=operator_approval_schema_migration_plan_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 template_count=1 pending_inputs=1 inputs_recorded=0 required_fields_count=4 missing_required_inputs=4 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_input_required report=docs/expansion-operator-approval-schema-migration-selection-input-template.md

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

- first-milestone-closed-loop: active source=first_milestone_closed_loop successful_runs=199 path=playbooks/first-milestone-closed-loop.md

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

- run_2bd28a33546a: completed project=bootstrap goal=goal_89f10f6757c8 completed=2026-06-22T15:51:24.681697+00:00 summary=runs/run_2bd28a33546a/summary.md
- run_f3f628326998: completed project=bootstrap goal=goal_4cbd583ba48e completed=2026-06-22T15:49:18.431038+00:00 summary=runs/run_f3f628326998/summary.md
- run_533ba4c469c4: completed project=bootstrap goal=goal_fd234e068201 completed=2026-06-22T15:36:49.743533+00:00 summary=runs/run_533ba4c469c4/summary.md
- run_706a409ddded: completed project=bootstrap goal=goal_7337fda44178 completed=2026-06-22T15:34:30.171988+00:00 summary=runs/run_706a409ddded/summary.md
- run_7964f9ddd944: completed project=bootstrap goal=goal_ba717f829701 completed=2026-06-22T15:17:55.383003+00:00 summary=runs/run_7964f9ddd944/summary.md

## Recent Evidence Packets

- none

## Recent Learnings

- run_2bd28a33546a: Run run_2bd28a33546a showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_2bd28a33546a/learning.md)
- run_f3f628326998: Run run_f3f628326998 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_f3f628326998/learning.md)
- run_533ba4c469c4: Run run_533ba4c469c4 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_533ba4c469c4/learning.md)
- run_706a409ddded: Run run_706a409ddded showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_706a409ddded/learning.md)
- run_7964f9ddd944: Run run_7964f9ddd944 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_7964f9ddd944/learning.md)

## Recent Eval Results

- first_milestone_closed_loop: pass run=run_2bd28a33546a created_at=2026-06-22T15:51:24.689433+00:00
- first_milestone_closed_loop: pass run=run_f3f628326998 created_at=2026-06-22T15:49:18.439791+00:00
- first_milestone_closed_loop: pass run=run_533ba4c469c4 created_at=2026-06-22T15:36:49.751338+00:00
- first_milestone_closed_loop: pass run=run_706a409ddded created_at=2026-06-22T15:34:30.181636+00:00
- first_milestone_closed_loop: pass run=run_7964f9ddd944 created_at=2026-06-22T15:17:55.392506+00:00
