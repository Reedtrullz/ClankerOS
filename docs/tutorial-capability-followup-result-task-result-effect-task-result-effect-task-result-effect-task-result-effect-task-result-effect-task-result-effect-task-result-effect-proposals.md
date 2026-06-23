# Tutorial: Capability Follow-Up Result Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Proposals

Use this command after an operator has accepted blocked downstream result
effect task result effect task result effect task result effect task result
effect task result effect task result records. It creates local proposed
effects only; it does not enable a capability.

## Command

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals
```

## Expected Output

The command writes:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`
- proposed rows in the generic `effects` table;
- idempotency keys rooted in the accepted blocked decision and result record.

If no accepted blocked decisions exist, the report is still written with
`_no_accepted_decisions` status and no effects are created.

## Safety Contract

This step preserves:

- `approval_requests_created=0`;
- `activation_actions_taken=0`;
- `external_mutations_taken=0`;
- `activation_allowed=false`;
- `capability_enabled=false`.

Run it twice when checking idempotency. The second run should report
`_already_recorded`, with `effect_proposals_created: 0` and
`existing_effect_proposals: 1` for the same accepted result.

## Verify

```bash
python3 -m pytest tests/test_first_milestone.py::test_capability_activation_followup_result_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_task_result_effect_proposals_create_local_effects -q
python3 -m agent_os.cli dashboard
```

The dashboard should include the matching effect proposal section and the
created effect id.
