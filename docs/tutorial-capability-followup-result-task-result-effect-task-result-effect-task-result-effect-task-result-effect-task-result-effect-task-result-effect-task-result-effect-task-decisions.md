# Tutorial: Review Downstream Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Result Effect Task Results

This tutorial records operator review decisions for downstream result effect
task result effect task result effect task result effect task result effect
task result effect task result effect task result records.

Use it after completed read-only evaluator delegation outputs have already
been ingested as local result records by:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
```

The review command is local and conservative. It can record
`accept_keep_blocked`, `request_more_evidence`, or `defer_review`. It must
keep activation blocked.

## 1. Record The Operator Decision

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
```

Expected output for a new ready result:

```text
decisions_recorded: 1
accepted_keep_blocked_decisions: 1
approval_requests_created: 0
activation_actions_taken: 0
external_mutations_taken: 0
```

## 2. Repeat For Idempotency

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
```

Expected repeat output:

```text
results_ready: 0
decisions_recorded: 0
existing_decisions: 1
external_mutations_taken: 0
```

## 3. Regenerate Visibility

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Read:

- `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
- `docs/dashboard.md`
- `docs/next-iteration.md`

## What This Does Not Do

- It does not create `approval_requests` rows.
- It does not enable capabilities.
- It does not satisfy capability proof.
- It does not allow activation.
- It does not mutate capability activation contracts.
- It does not mutate external systems.
- It does not route, schedule, retry, dispatch, run CI, or deploy.
- It does not promote trust or mark the active goal complete.
