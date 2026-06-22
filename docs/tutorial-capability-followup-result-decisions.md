# Tutorial: Review Capability Follow-Up Results

Use this after read-only evaluator delegation results have been ingested with
`capability-activation-followup-results` and you want to record the operator
review outcome without enabling the capability.

## Prerequisites

Create follow-up tasks, delegation packets, complete at least one evaluator
delegation, and ingest the completed result:

```bash
python3 -m agent_os.cli capability-activation-followups
python3 -m agent_os.cli capability-activation-followup-delegations
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Evaluator found missing proof and recommends keeping activation blocked." \
  --output-json '{"evidence":[{"status":"missing","summary":"Required proof is not attached."}],"findings":[{"summary":"Keep activation blocked."}]}'
python3 -m agent_os.cli capability-activation-followup-results
```

## Record The Review Decision

For the current blocked proof path, accept the evaluator result and keep the
capability blocked:

```bash
python3 -m agent_os.cli capability-activation-followup-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted evaluator result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-results.md
```

Expected output includes:

```text
capability_activation_followup_result_decide: capability_activation_followup_result_decisions_recorded
results_ready: 1
decisions_recorded: 1
accepted_keep_blocked_decisions: 1
approval_requests_created: 0
activation_actions_taken: 0
report: docs/capability-activation-followup-decisions.md
```

Rerunning the command should report
`capability_activation_followup_result_decisions_already_recorded` when all
ingested result records already have local decision rows.

## Inspect The Evidence

Read:

- `docs/capability-activation-followup-results.md`
- `docs/capability-activation-followup-decisions.md`
- `docs/dashboard.md`, section `## Capability Activation Follow-Up Decisions`

The decision row records operator review state for ingested result records. It
does not approve activation, satisfy proof, or create legacy approval rows.

## Create Proposed Effect Rows

After accepting blocked results, record local proposed effects:

```bash
python3 -m agent_os.cli capability-activation-followup-result-effect-proposals
```

This writes
`docs/capability-activation-followup-result-effect-proposals.md` and adds
`proposed` rows to the generic effects ledger. The rows preserve the accepted
decision and source result link while keeping activation blocked. See
`docs/tutorial-capability-followup-result-effect-proposals.md` for the full
walkthrough.

## Other Local Decisions

Use `request_more_evidence` when the evaluator result is useful but still needs
a more specific proof artifact:

```bash
python3 -m agent_os.cli capability-activation-followup-result-decide \
  --operator-id operator \
  --selected-action request_more_evidence \
  --selection-note "Requested one more concrete proof artifact before deciding." \
  --evidence-reference docs/capability-activation-followup-results.md
```

Use `defer_review` when the result should stay visible but no operator decision
is ready yet.

## Non-Claims

- This does not create `approval_requests` rows.
- This does not enable capabilities.
- This does not satisfy capability proof.
- This does not mutate activation contracts.
- This does not start subagents, schedule, retry, run CI, deploy, push, or
  mutate external systems.
