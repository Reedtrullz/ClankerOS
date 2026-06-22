# Capability Activation Tasks

- id: capability_activation_task_batch_bf62744d45f5
- status: capability_activation_tasks_already_recorded
- source_application: operator_approval_effect_application_8e180df11ab3
- goal: goal_b25a107a53a9
- applied_capability_effects: 9
- tasks_created: 0
- existing_activation_tasks: 9
- activation_actions_taken: 0
- report_path: docs/capability-activation-tasks.md
- created_at: 2026-06-22T16:07:31.157958+00:00

## Created Activation Tasks

- none

## Existing Activation Tasks

- task=task_8bcbf504e7d4 status=pending capability=real_cost_tracking source_effect=effect_1a41ff7c5cca risk=high activation_allowed=false
- task=task_dc62ee6f543d status=pending capability=automatic_retries source_effect=effect_e5a56b95d9ce risk=high activation_allowed=false
- task=task_99c552985002 status=pending capability=trust_promotion source_effect=effect_549912b53e8e risk=high activation_allowed=false
- task=task_0ad009784133 status=pending capability=budget_enforcement source_effect=effect_9ad8411cfe14 risk=high activation_allowed=false
- task=task_e1da0f911e35 status=pending capability=ci_deploy_proof source_effect=effect_1e2d271e79f3 risk=high activation_allowed=false
- task=task_7c11407bcf4c status=pending capability=browser_desktop_adapters source_effect=effect_2fe6bd7d30f4 risk=high activation_allowed=false
- task=task_1aa4ed98b59e status=pending capability=autonomous_scheduling source_effect=effect_29e9791db746 risk=high activation_allowed=false
- task=task_a8743cef9b81 status=pending capability=remote_workers source_effect=effect_cc210d6119d5 risk=high activation_allowed=false
- task=task_f26a1635d5f1 status=pending capability=hosted_dashboard source_effect=effect_f150fdc78c97 risk=high activation_allowed=false

## Applied Capability Effects

- effect=effect_1a41ff7c5cca status=applied capability=real_cost_tracking target=real_cost_tracking source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_e5a56b95d9ce status=applied capability=automatic_retries target=automatic_retries source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_549912b53e8e status=applied capability=trust_promotion target=trust_promotion source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_9ad8411cfe14 status=applied capability=budget_enforcement target=budget_enforcement source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_1e2d271e79f3 status=applied capability=ci_deploy_proof target=ci_deploy_proof source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_2fe6bd7d30f4 status=applied capability=browser_desktop_adapters target=browser_desktop_adapters source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_29e9791db746 status=applied capability=autonomous_scheduling target=autonomous_scheduling source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_cc210d6119d5 status=applied capability=remote_workers target=remote_workers source_application=operator_approval_effect_application_4a855067a8db
- effect=effect_f150fdc78c97 status=applied capability=hosted_dashboard target=hosted_dashboard source_application=operator_approval_effect_application_4a855067a8db

## Non-Claims

- Does not enable capabilities.
- Does not create legacy approval_requests rows.
- Does not mutate external systems.
- Does not route, schedule, retry, dispatch, run CI, or deploy.
- Does not promote trust or mark the active goal complete.
