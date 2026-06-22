# Agent System Dashboard

## Operator Cockpit

### Active Goals/Runs

- none

### Registered Projects

- none

### Approval Inbox

- none

### Proposed Effects

- none

### Recent Commits/Effects

- none

### Incidents

- none

### Verification Status

- none

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

- Run `python3 -m agent_os.cli iterate` for the next local work packet.

## Queue Health

- pending: 0
- waiting_approval: 0
- claimed: 0
- running: 0
- verifying: 0
- completed: 389
- blocked: 0
- failed: 0
- active: 0
- needs_attention: 0

## Iteration Loop

- status: planned
- focus: Add effect proposal records from approved operator approval request decisions.
- source: tasks.md#next
- packet: docs/next-iteration.md
- created_at: 2026-06-22T15:17:47.396671+00:00

## Simplicity Guardrail

- policy: highest-score-then-lowest-complexity
- reason: selected only actionable item with score 9 and complexity 4
- selected_score: 9
- selected_complexity: 4
- selected_focus: Add effect proposal records from approved operator approval request decisions.

## Expansion Operator Approval Schema Decision

- status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_b5c60c8ccc43
- source_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_93697a4315da
- source_ledger: expansion_operator_decision_ledger_51c1e0f289fa
- source_checklist: expansion_operator_review_checklist_f01aaf772dab
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
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

- expansion_operator_approval_schema_decision_23d2990e8da1: status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_b5c60c8ccc43 source_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_93697a4315da source_ledger=expansion_operator_decision_ledger_51c1e0f289fa source_checklist=expansion_operator_review_checklist_f01aaf772dab source_index=expansion_decision_evidence_index_d63c685e43c6 source_brief=expansion_decision_brief_9bfc1f0a12d2 source_audit=goal_completion_audit_9053feef303e affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 decision_options=3 recommended_option=operator_approval_requests_table rejected_options=2 schema_objects=1 migration_applied=0 created_approval_requests=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_plan_required report=docs/expansion-operator-approval-schema-decision.md

## Expansion Operator Approval Schema Migration Plan

- status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_23d2990e8da1
- source_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_b5c60c8ccc43
- source_review_status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_93697a4315da
- source_ledger: expansion_operator_decision_ledger_51c1e0f289fa
- source_checklist: expansion_operator_review_checklist_f01aaf772dab
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
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

- expansion_operator_approval_schema_migration_plan_71f2d6d61eab: status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_23d2990e8da1 source_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_b5c60c8ccc43 source_review_status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_93697a4315da source_ledger=expansion_operator_decision_ledger_51c1e0f289fa source_checklist=expansion_operator_review_checklist_f01aaf772dab source_index=expansion_decision_evidence_index_d63c685e43c6 source_brief=expansion_decision_brief_9bfc1f0a12d2 source_audit=goal_completion_audit_9053feef303e recommended_option=operator_approval_requests_table target_table=operator_approval_requests affected_requests=11 schema_gaps=11 missing_fields=7 external_requests=2 capability_requests=9 planned_columns=26 planned_indexes=4 migration_steps=4 migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_approval_required report=docs/expansion-operator-approval-schema-migration-plan.md

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

## Expansion Operator Approval Schema Migration Approval Request

- status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_71f2d6d61eab
- source_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_23d2990e8da1
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_b5c60c8ccc43
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

- expansion_operator_approval_schema_migration_approval_request_c092fc60ba80: status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_71f2d6d61eab source_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_23d2990e8da1 source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_b5c60c8ccc43 source_review_status=approval_request_schema_review_required target_table=operator_approval_requests planned_columns=26 planned_indexes=4 migration_steps=4 affected_requests=11 schema_gaps=11 request_count=1 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_decision_required report=docs/expansion-operator-approval-schema-migration-approval-request.md

## Expansion Operator Approval Schema Migration Decision Ledger

- status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_c092fc60ba80
- source_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_71f2d6d61eab
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_23d2990e8da1
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_b5c60c8ccc43
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

- expansion_operator_approval_schema_migration_decision_ledger_7e5b081c0280: status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_c092fc60ba80 source_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_71f2d6d61eab source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_23d2990e8da1 source_decision_status=approval_schema_decision_ready source_review=expansion_operator_approval_request_review_b5c60c8ccc43 source_review_status=approval_request_schema_review_required target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 approved_decisions=0 deferred_decisions=0 more_evidence_decisions=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_action_required report=docs/expansion-operator-approval-schema-migration-decision-ledger.md

## Expansion Operator Approval Schema Migration Action Checklist

- status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_7e5b081c0280
- source_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_c092fc60ba80
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_71f2d6d61eab
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_23d2990e8da1
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_b5c60c8ccc43
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

- expansion_operator_approval_schema_migration_action_checklist_2297f678eee7: status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_7e5b081c0280 source_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_c092fc60ba80 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_71f2d6d61eab source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_23d2990e8da1 source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_required report=docs/expansion-operator-approval-schema-migration-action-checklist.md

## Expansion Operator Approval Schema Migration Selection Packet

- status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_2297f678eee7
- source_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_7e5b081c0280
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_c092fc60ba80
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_71f2d6d61eab
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_23d2990e8da1
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_b5c60c8ccc43
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

- expansion_operator_approval_schema_migration_selection_packet_dc7e54cc874c: status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_2297f678eee7 source_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_7e5b081c0280 source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_c092fc60ba80 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_71f2d6d61eab source_plan_status=operator_approval_schema_migration_plan_ready source_decision=expansion_operator_approval_schema_decision_23d2990e8da1 source_decision_status=approval_schema_decision_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 approve_selections=0 defer_selections=0 more_evidence_selections=0 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_selection_input_required report=docs/expansion-operator-approval-schema-migration-selection-packet.md

## Queue Health Checks

- blocked_threshold: 2
- failed_threshold: 2
- hotspots: 0

- none

## Handoff Review

- status: clear
- current_focus: Add approval-gated decision command for pending operator approval request rows.
- blocked_tasks: 0
- stale_handoffs: 0
- report: docs/handoff-review.md

- none

## Eval After Change

- failed: 0

- eval_after_change_a58ebbfd08d2: status=pass change=Add operator approval request row application files=agent_os/operator_approval_request_rows.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-schema.md evals=first_milestone_closed_loop runs=run_69b9d4af9bf1 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_4b8b415ba010: status=pass change=Apply operator approval request schema files=agent_os/operator_approval_schema_migration.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-schema.md,README.md,docs/suggested-use.md,projects/bootstrap/handoff.md evals=first_milestone_closed_loop runs=run_3d755f0aab76 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_fd7a7396ce90: status=pass change=Apply operator approval request schema files=agent_os/operator_approval_schema_migration.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,agent_os/iteration.py,tests/test_first_milestone.py,docs/tutorial-operator-approval-schema.md evals=first_milestone_closed_loop runs=run_052990c19430 results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_e7222ef41ef8: status=pass change=Add steering reviews and inbox files=agent_os/steering.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,tests/test_first_milestone.py,docs/tutorial-steering-inbox.md evals=first_milestone_closed_loop runs=run_10ab8e90564a results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md
- eval_after_change_f9315f2416fb: status=pass change=Add run evidence review packets files=agent_os/run_review.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,tests/test_first_milestone.py,docs/tutorial-run-review.md evals=first_milestone_closed_loop runs=run_d52df83d4bba results=evals/results/first_milestone_closed_loop.json report=docs/eval-after-change.md

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
- tasks: 381
- budget_state: not_tracked
- trust_state: not_tracked
- risk_counts: low=381
- report: docs/budget-trust-posture.md

- budget_trust_posture_ba2ae8e9854a: status=report_only tasks=381 budget_state=not_tracked trust_state=not_tracked risk_counts=low=381 report=docs/budget-trust-posture.md

## Dispatch Posture History

- status: report_only
- snapshots: 25
- latest_tasks: 381
- task_delta: 139
- latest_risk_counts: low=381
- report: docs/dispatch-posture-history.md

- dispatch_posture_history_46d9599ab0e2: status=report_only snapshots=25 latest_tasks=381 task_delta=139 latest_risk_counts=low=381 report=docs/dispatch-posture-history.md

## Dispatch Posture Snapshot Review

- status: fresh
- snapshots: 25
- stale_snapshots: 21
- latest_snapshot_age_seconds: 0
- stale_after_seconds: 3600
- report: docs/dispatch-posture-staleness.md

- dispatch_posture_staleness_f4f5d9cd3b69: status=fresh snapshots=25 stale_snapshots=21 latest_snapshot_age_seconds=0 stale_after_seconds=3600 latest_tasks=381 latest_risk_counts=low=381 report=docs/dispatch-posture-staleness.md

## Dispatch Posture Refresh Recommendation

- status: no_refresh_needed
- source_review: dispatch_posture_staleness_f4f5d9cd3b69
- source_status: fresh
- recommended_commands: none
- report: docs/dispatch-posture-refresh.md

- dispatch_posture_refresh_4b50f768a49d: status=no_refresh_needed source_review=dispatch_posture_staleness_f4f5d9cd3b69 source_status=fresh recommended_commands=none report=docs/dispatch-posture-refresh.md

## Capability Expansion Ledger

- status: report_only
- capabilities: 9
- ready: 0
- deferred: 9
- approval_boundary: explicit_operator_approval_required
- report: docs/capability-expansion-ledger.md

- capability_expansion_ledger_adfe6bd5d2d2: status=report_only capabilities=9 ready=0 deferred=9 approval_boundary=explicit_operator_approval_required report=docs/capability-expansion-ledger.md

## Capability Readiness Review

- status: blocked_by_missing_evidence
- source_ledger: capability_expansion_ledger_adfe6bd5d2d2
- capabilities: 9
- ready: 0
- not_ready: 9
- missing_evidence: 9
- recommended_commands: none
- report: docs/capability-readiness-review.md

- capability_readiness_review_1b8d847e8426: status=blocked_by_missing_evidence source_ledger=capability_expansion_ledger_adfe6bd5d2d2 capabilities=9 ready=0 not_ready=9 missing_evidence=9 recommended_commands=none report=docs/capability-readiness-review.md

## Capability Proof Gap Index

- status: open_gaps
- source_review: capability_readiness_review_1b8d847e8426
- capabilities: 9
- gaps: 9
- missing_evidence: 9
- blocked_capabilities: 9
- next_proofs: 9
- recommended_commands: none
- report: docs/capability-proof-gap-index.md

- capability_proof_gap_index_2e86cc7a2331: status=open_gaps source_review=capability_readiness_review_1b8d847e8426 source_status=blocked_by_missing_evidence gaps=9 missing_evidence=9 blocked_capabilities=9 next_proofs=9 recommended_commands=none report=docs/capability-proof-gap-index.md

## Capability Approval Boundary Matrix

- status: approval_required
- source_index: capability_proof_gap_index_2e86cc7a2331
- capabilities: 9
- boundaries: 1
- gaps: 9
- blocked_capabilities: 9
- approvals_required: 9
- recommended_commands: none
- report: docs/capability-approval-boundary-matrix.md

- capability_approval_boundary_matrix_edc3e766edba: status=approval_required source_index=capability_proof_gap_index_2e86cc7a2331 source_status=open_gaps boundaries=1 gaps=9 blocked_capabilities=9 approvals_required=9 recommended_commands=none report=docs/capability-approval-boundary-matrix.md

## Capability Evidence Collection Plan

- status: evidence_required
- source_matrix: capability_approval_boundary_matrix_edc3e766edba
- capabilities: 9
- evidence_items: 9
- manual_collection: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-evidence-collection-plan.md

- capability_evidence_collection_plan_09c5d3a55d40: status=evidence_required source_matrix=capability_approval_boundary_matrix_edc3e766edba source_status=approval_required evidence_items=9 manual_collection=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-evidence-collection-plan.md

## Capability Promotion Gate Checklist

- status: promotion_blocked
- source_plan: capability_evidence_collection_plan_09c5d3a55d40
- capabilities: 9
- gates: 9
- blocked_promotions: 9
- missing_evidence: 9
- approvals_required: 9
- boundaries: 1
- recommended_commands: none
- report: docs/capability-promotion-gate-checklist.md

- capability_promotion_gate_checklist_6bdd087bb63c: status=promotion_blocked source_plan=capability_evidence_collection_plan_09c5d3a55d40 source_status=evidence_required gates=9 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-gate-checklist.md

## Capability Promotion Decision Ledger

- status: promotion_decision_blocked
- source_checklist: capability_promotion_gate_checklist_6bdd087bb63c
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

- capability_promotion_decision_ledger_4e027252f779: status=promotion_decision_blocked source_checklist=capability_promotion_gate_checklist_6bdd087bb63c source_status=promotion_blocked decisions=9 deferred_promotions=9 operator_decisions_required=0 blocked_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-promotion-decision-ledger.md

## Capability Trust Promotion Audit

- status: trust_promotion_blocked
- source_ledger: capability_promotion_decision_ledger_4e027252f779
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

- capability_trust_promotion_audit_aabf9e25e3cc: status=trust_promotion_blocked source_ledger=capability_promotion_decision_ledger_4e027252f779 source_status=promotion_decision_blocked audits=9 blocked_trust_promotions=9 operator_reviews_required=0 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-trust-promotion-audit.md

## Capability Automatic Retry Audit

- status: automatic_retry_blocked
- source_audit: capability_trust_promotion_audit_aabf9e25e3cc
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

- capability_automatic_retry_audit_f5b409de134d: status=automatic_retry_blocked source_audit=capability_trust_promotion_audit_aabf9e25e3cc source_status=trust_promotion_blocked audits=9 blocked_retries=9 operator_reviews_required=0 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-automatic-retry-audit.md

## Capability Real Cost Tracking Audit

- status: real_cost_tracking_blocked
- source_audit: capability_automatic_retry_audit_f5b409de134d
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

- capability_real_cost_tracking_audit_c9fb1e4e6687: status=real_cost_tracking_blocked source_audit=capability_automatic_retry_audit_f5b409de134d source_status=automatic_retry_blocked audits=9 blocked_cost_tracking=9 operator_reviews_required=0 blocked_retries=9 blocked_trust_promotions=9 deferred_promotions=9 missing_evidence=9 approvals_required=9 boundaries=1 recommended_commands=none report=docs/capability-real-cost-tracking-audit.md

## Hosted Dashboard Proof Checklist

- status: hosted_dashboard_proof_blocked
- source_kind: real_cost_tracking_proof_checklist
- source_checklist: real_cost_tracking_proof_checklist_b41df5abca67
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

- hosted_dashboard_proof_checklist_b2585ef086ae: status=hosted_dashboard_proof_blocked source_kind=real_cost_tracking_proof_checklist source_checklist=real_cost_tracking_proof_checklist_b41df5abca67 source_audit=none source_status=real_cost_tracking_proof_blocked checklist_items=1 blocked_dashboard_proofs=1 operator_reviews_required=0 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/hosted-dashboard-proof-checklist.md

## Remote Worker Proof Checklist

- status: remote_worker_proof_blocked
- source_checklist: hosted_dashboard_proof_checklist_b2585ef086ae
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

- remote_worker_proof_checklist_e55511045c7f: status=remote_worker_proof_blocked source_checklist=hosted_dashboard_proof_checklist_b2585ef086ae source_status=hosted_dashboard_proof_blocked checklist_items=1 blocked_worker_proofs=1 operator_reviews_required=0 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/remote-worker-proof-checklist.md

## Autonomous Scheduling Proof Checklist

- status: autonomous_scheduling_proof_blocked
- source_checklist: remote_worker_proof_checklist_e55511045c7f
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

- autonomous_scheduling_proof_checklist_5b742c8b72e6: status=autonomous_scheduling_proof_blocked source_checklist=remote_worker_proof_checklist_e55511045c7f source_status=remote_worker_proof_blocked checklist_items=1 blocked_scheduling_proofs=1 operator_reviews_required=0 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/autonomous-scheduling-proof-checklist.md

## Browser Desktop Adapter Proof Checklist

- status: browser_desktop_adapter_proof_blocked
- source_checklist: autonomous_scheduling_proof_checklist_5b742c8b72e6
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

- browser_desktop_adapter_proof_checklist_9bed536369e7: status=browser_desktop_adapter_proof_blocked source_checklist=autonomous_scheduling_proof_checklist_5b742c8b72e6 source_status=autonomous_scheduling_proof_blocked checklist_items=1 blocked_adapter_proofs=1 operator_reviews_required=0 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/browser-desktop-adapter-proof-checklist.md

## CI Deploy Proof Checklist

- status: ci_deploy_proof_blocked
- source_checklist: browser_desktop_adapter_proof_checklist_9bed536369e7
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

- ci_deploy_proof_checklist_bf7f02f1b3ae: status=ci_deploy_proof_blocked source_checklist=browser_desktop_adapter_proof_checklist_9bed536369e7 source_status=browser_desktop_adapter_proof_blocked checklist_items=1 blocked_ci_deploy_proofs=1 operator_reviews_required=0 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/ci-deploy-proof-checklist.md

## Budget Enforcement Proof Checklist

- status: budget_enforcement_proof_blocked
- source_checklist: ci_deploy_proof_checklist_bf7f02f1b3ae
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

- budget_enforcement_proof_checklist_88637d37a3c7: status=budget_enforcement_proof_blocked source_checklist=ci_deploy_proof_checklist_bf7f02f1b3ae source_status=ci_deploy_proof_blocked checklist_items=1 blocked_budget_enforcement_proofs=1 operator_reviews_required=0 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/budget-enforcement-proof-checklist.md

## Trust Promotion Proof Checklist

- status: trust_promotion_proof_blocked
- source_checklist: budget_enforcement_proof_checklist_88637d37a3c7
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

- trust_promotion_proof_checklist_4ac7bd15c0be: status=trust_promotion_proof_blocked source_checklist=budget_enforcement_proof_checklist_88637d37a3c7 source_status=budget_enforcement_proof_blocked checklist_items=1 blocked_trust_promotion_proofs=1 operator_reviews_required=0 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/trust-promotion-proof-checklist.md

## Automatic Retry Proof Checklist

- status: automatic_retry_proof_blocked
- source_checklist: trust_promotion_proof_checklist_4ac7bd15c0be
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

- automatic_retry_proof_checklist_7c54a05319a3: status=automatic_retry_proof_blocked source_checklist=trust_promotion_proof_checklist_4ac7bd15c0be source_status=trust_promotion_proof_blocked checklist_items=1 blocked_automatic_retry_proofs=1 operator_reviews_required=0 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/automatic-retry-proof-checklist.md

## Real Cost Tracking Proof Checklist

- status: real_cost_tracking_proof_blocked
- source_checklist: automatic_retry_proof_checklist_7c54a05319a3
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

- real_cost_tracking_proof_checklist_5b564749f49f: status=real_cost_tracking_proof_blocked source_checklist=automatic_retry_proof_checklist_7c54a05319a3 source_status=automatic_retry_proof_blocked checklist_items=1 blocked_real_cost_tracking_proofs=1 operator_reviews_required=0 blocked_automatic_retry_proofs=1 blocked_trust_promotion_proofs=1 blocked_budget_enforcement_proofs=1 blocked_ci_deploy_proofs=1 blocked_adapter_proofs=1 blocked_scheduling_proofs=1 blocked_worker_proofs=1 blocked_dashboard_proofs=1 blocked_cost_tracking=1 blocked_retries=1 blocked_trust_promotions=1 missing_evidence=1 approvals_required=1 boundaries=1 recommended_commands=none report=docs/real-cost-tracking-proof-checklist.md

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

- goal_completion_audit_9053feef303e: status=blocked_by_report_only_proofs requirements=9 satisfied_requirements=0 blocked_requirements=9 missing_evidence=9 approvals_required=9 external_decisions_required=2 recommended_commands=none report=docs/goal-completion-audit.md

## Expansion Decision Brief

- status: operator_decisions_required
- source_audit: goal_completion_audit_9053feef303e
- source_status: blocked_by_report_only_proofs
- requirements: 9
- blocked_requirements: 9
- external_decisions_required: 2
- approvals_required: 9
- decision_items: 11
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-brief.md

- expansion_decision_brief_9bfc1f0a12d2: status=operator_decisions_required source_audit=goal_completion_audit_9053feef303e source_status=blocked_by_report_only_proofs requirements=9 blocked_requirements=9 external_decisions_required=2 approvals_required=9 decision_items=11 recommended_next_step=operator_review_required report=docs/expansion-decision-brief.md

## Expansion Decision Evidence Index

- status: evidence_indexed
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_status: operator_decisions_required
- source_audit: goal_completion_audit_9053feef303e
- decision_items: 11
- evidence_items: 11
- external_decisions: 2
- capability_decisions: 9
- missing_evidence_links: 0
- recommended_next_step: operator_review_required
- report: docs/expansion-decision-evidence-index.md

- expansion_decision_evidence_index_d63c685e43c6: status=evidence_indexed source_brief=expansion_decision_brief_9bfc1f0a12d2 source_status=operator_decisions_required source_audit=goal_completion_audit_9053feef303e decision_items=11 evidence_items=11 external_decisions=2 capability_decisions=9 missing_evidence_links=0 recommended_next_step=operator_review_required report=docs/expansion-decision-evidence-index.md

## Expansion Operator Review Checklist

- status: operator_review_required
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_status: evidence_indexed
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
- review_items: 11
- decision_required: 11
- external_reviews: 2
- capability_reviews: 9
- missing_evidence_links: 0
- allowed_actions: approve,defer,request_more_evidence
- recommended_next_step: operator_decision_required
- report: docs/expansion-operator-review-checklist.md

- expansion_operator_review_checklist_f01aaf772dab: status=operator_review_required source_index=expansion_decision_evidence_index_d63c685e43c6 source_status=evidence_indexed source_brief=expansion_decision_brief_9bfc1f0a12d2 source_audit=goal_completion_audit_9053feef303e review_items=11 decision_required=11 external_reviews=2 capability_reviews=9 missing_evidence_links=0 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-review-checklist.md

## Expansion Operator Decision Ledger

- status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_f01aaf772dab
- source_status: operator_review_required
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
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

- expansion_operator_decision_ledger_51c1e0f289fa: status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_f01aaf772dab source_status=operator_review_required source_index=expansion_decision_evidence_index_d63c685e43c6 source_brief=expansion_decision_brief_9bfc1f0a12d2 source_audit=goal_completion_audit_9053feef303e decision_items=11 pending_decisions=11 approved_decisions=0 deferred_decisions=0 more_evidence_requested=0 external_decisions=2 capability_decisions=9 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_decision_required report=docs/expansion-operator-decision-ledger.md

## Expansion Operator Approval Draft

- status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_51c1e0f289fa
- source_status: pending_operator_decisions
- source_checklist: expansion_operator_review_checklist_f01aaf772dab
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
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

- expansion_operator_approval_draft_93697a4315da: status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_51c1e0f289fa source_status=pending_operator_decisions source_checklist=expansion_operator_review_checklist_f01aaf772dab source_index=expansion_decision_evidence_index_d63c685e43c6 source_brief=expansion_decision_brief_9bfc1f0a12d2 source_audit=goal_completion_audit_9053feef303e draft_items=11 draft_requests=11 created_approval_requests=0 external_drafts=2 capability_drafts=9 approval_boundaries=2 pending_decisions=11 allowed_actions=approve,defer,request_more_evidence recommended_next_step=operator_approval_flow_required report=docs/expansion-operator-approval-draft.md

## Expansion Operator Approval Request Review

- status: approval_request_schema_review_required
- source_draft: expansion_operator_approval_draft_93697a4315da
- source_status: approval_draft_ready
- source_ledger: expansion_operator_decision_ledger_51c1e0f289fa
- source_checklist: expansion_operator_review_checklist_f01aaf772dab
- source_index: expansion_decision_evidence_index_d63c685e43c6
- source_brief: expansion_decision_brief_9bfc1f0a12d2
- source_audit: goal_completion_audit_9053feef303e
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

- expansion_operator_approval_request_review_b5c60c8ccc43: status=approval_request_schema_review_required source_draft=expansion_operator_approval_draft_93697a4315da source_status=approval_draft_ready source_ledger=expansion_operator_decision_ledger_51c1e0f289fa source_checklist=expansion_operator_review_checklist_f01aaf772dab source_index=expansion_decision_evidence_index_d63c685e43c6 source_brief=expansion_decision_brief_9bfc1f0a12d2 source_audit=goal_completion_audit_9053feef303e draft_requests=11 review_items=11 ready_requests=0 blocked_requests=11 schema_gaps=11 created_approval_requests=0 existing_approval_requests=0 external_requests=2 capability_requests=9 approval_boundaries=2 recommended_next_step=approval_request_schema_decision_required report=docs/expansion-operator-approval-request-review.md

## Expansion Operator Approval Schema Migration Selection Input Template

- status: operator_approval_schema_migration_selection_input_required
- source_packet: expansion_operator_approval_schema_migration_selection_packet_dc7e54cc874c
- source_status: operator_approval_schema_migration_selection_required
- source_checklist: expansion_operator_approval_schema_migration_action_checklist_2297f678eee7
- source_checklist_status: operator_approval_schema_migration_manual_action_required
- source_ledger: expansion_operator_approval_schema_migration_decision_ledger_7e5b081c0280
- source_ledger_status: operator_approval_schema_migration_decision_pending
- source_request: expansion_operator_approval_schema_migration_approval_request_c092fc60ba80
- source_request_status: operator_approval_schema_migration_approval_required
- source_plan: expansion_operator_approval_schema_migration_plan_71f2d6d61eab
- source_plan_status: operator_approval_schema_migration_plan_ready
- source_decision: expansion_operator_approval_schema_decision_23d2990e8da1
- source_decision_status: approval_schema_decision_ready
- source_review: expansion_operator_approval_request_review_b5c60c8ccc43
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

- expansion_operator_approval_schema_migration_selection_input_template_63f5e50b13ff: status=operator_approval_schema_migration_selection_input_required source_packet=expansion_operator_approval_schema_migration_selection_packet_dc7e54cc874c source_status=operator_approval_schema_migration_selection_required source_checklist=expansion_operator_approval_schema_migration_action_checklist_2297f678eee7 source_checklist_status=operator_approval_schema_migration_manual_action_required source_ledger=expansion_operator_approval_schema_migration_decision_ledger_7e5b081c0280 source_ledger_status=operator_approval_schema_migration_decision_pending source_request=expansion_operator_approval_schema_migration_approval_request_c092fc60ba80 source_request_status=operator_approval_schema_migration_approval_required source_plan=expansion_operator_approval_schema_migration_plan_71f2d6d61eab source_plan_status=operator_approval_schema_migration_plan_ready target_table=operator_approval_requests request_count=1 decision_count=1 pending_decisions=1 action_count=1 pending_actions=1 actions_taken=0 selected_action=none selection_count=1 pending_selections=1 selections_recorded=0 template_count=1 pending_inputs=1 inputs_recorded=0 required_fields_count=4 missing_required_inputs=4 approval_boundary=schema_migration requested_action=apply_operator_approval_requests_schema allowed_actions=approve,defer,request_more_evidence migration_applied=0 table_created=0 operator_approval_rows_created=0 approval_requests_created=0 existing_approval_requests=0 recommended_next_step=operator_approval_schema_migration_operator_input_required report=docs/expansion-operator-approval-schema-migration-selection-input-template.md

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

- first-milestone-closed-loop: active source=first_milestone_closed_loop successful_runs=192 path=playbooks/first-milestone-closed-loop.md

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

- run_2cffa41b4f05: completed project=bootstrap goal=goal_38e36136446c completed=2026-06-22T15:06:22.932826+00:00 summary=runs/run_2cffa41b4f05/summary.md
- run_69b9d4af9bf1: completed project=bootstrap goal=goal_1a59ec28c2e2 completed=2026-06-22T15:06:15.196270+00:00 summary=runs/run_69b9d4af9bf1/summary.md
- run_3d755f0aab76: completed project=bootstrap goal=goal_714c0ce097c6 completed=2026-06-22T14:49:19.559351+00:00 summary=runs/run_3d755f0aab76/summary.md
- run_da9053c101aa: completed project=bootstrap goal=goal_bc6b5a1e184e completed=2026-06-22T14:48:49.932932+00:00 summary=runs/run_da9053c101aa/summary.md
- run_fd407239da0f: completed project=bootstrap goal=goal_2df3a832406e completed=2026-06-22T14:48:25.087576+00:00 summary=runs/run_fd407239da0f/summary.md

## Recent Evidence Packets

- none

## Recent Learnings

- run_2cffa41b4f05: Run run_2cffa41b4f05 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_2cffa41b4f05/learning.md)
- run_69b9d4af9bf1: Run run_69b9d4af9bf1 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_69b9d4af9bf1/learning.md)
- run_3d755f0aab76: Run run_3d755f0aab76 showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_3d755f0aab76/learning.md)
- run_da9053c101aa: Run run_da9053c101aa showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_da9053c101aa/learning.md)
- run_fd407239da0f: Run run_fd407239da0f showed that the first closed loop can be verified through file evidence before expanding to broader domains. (project=bootstrap, source=projects/bootstrap/artifacts/run_fd407239da0f/learning.md)

## Recent Eval Results

- first_milestone_closed_loop: pass run=run_2cffa41b4f05 created_at=2026-06-22T15:06:22.939572+00:00
- first_milestone_closed_loop: pass run=run_69b9d4af9bf1 created_at=2026-06-22T15:06:15.207118+00:00
- first_milestone_closed_loop: pass run=run_3d755f0aab76 created_at=2026-06-22T14:49:19.568205+00:00
- first_milestone_closed_loop: pass run=run_da9053c101aa created_at=2026-06-22T14:48:49.940961+00:00
- first_milestone_closed_loop: pass run=run_fd407239da0f created_at=2026-06-22T14:48:25.094454+00:00
