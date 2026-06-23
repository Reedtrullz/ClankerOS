# Tutorial: Capability Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Application

Use this command after accepted blocked downstream result effect task result
effect task result effect task result effect task result effect task result
decisions have created local proposed effects. It applies those proposals as
local ledger records only; it does not enable a capability.

## Command

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md
```

## Expected Output

The command writes:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`;
- one row in `capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_applications`;
- `status=applied` on each applicable local proposed effect.

If no proposed effects exist, the report is still written with
`_application_no_proposals` and no effects are applied.

## Safety Contract

The application keeps these counters at zero:

- `approval_requests_created=0`;
- `activation_actions_taken=0`;
- `external_mutations_taken=0`.

The applied effect result keeps:

- `activation_allowed=false`;
- `capability_enabled=false`;
- `application_status=recorded_local_only`.

Run the command twice when checking idempotency. The second run should report
`_already_recorded`, with `effects_applied: 0` and
`existing_applied_effects: 1` for the same accepted result.

## Verify

```bash
python3 -m pytest tests/test_first_milestone.py -q -k "application_requires_proposals or application_records_local_applications or application_is_idempotent"
python3 -m pytest tests/test_first_milestone.py -q -k "task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result"
python3 -m agent_os.cli dashboard
```

The dashboard should include the matching application section and the report
should include explicit non-claims for approvals, activation, routing,
scheduling, CI, deployment, trust promotion, and external mutation.
