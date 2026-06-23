# Suggested Use

ClankerOS works best as a local operating loop for agentic work, not as a
black-box autonomous runner. Use it to make work visible, verifiable, and
harder to overclaim.

## I Want To

| If you want to... | Start with... |
| --- | --- |
| See current state | `python3 -m agent_os.cli dashboard` |
| Pick the next safe local task | `python3 -m agent_os.cli iterate` |
| Run the first loop | `docs/tutorial-first-loop.md` |
| Make a coded change safely | `docs/tutorial-approval-gated-coding.md` |
| Capture subagent-style context without execution | `docs/tutorial-subagent-delegation-results.md` |
| Review a run before acting | `python3 -m agent_os.cli review <run_id>` |
| Keep activation blocked while preserving proof state | start with the capability follow-up tutorials below |
| Publish a coherent snapshot | read `## When To Commit And Push` before pushing |

## Good Starting Prompts

Use prompts that name a concrete local outcome:

```text
Create a local proof packet for enabling a hosted dashboard, but do not deploy it.
```

```text
Review the current expansion evidence and add the next report-only approval boundary.
```

```text
Run the first local loop, regenerate the dashboard, and summarize what is proven and not proven.
```

```text
Register this git repo, run a worktree-isolated coding task, capture the diff and tests, then ask me before creating the local worktree commit.
```

```text
List the safe default profiles and record a scout routing decision for repo search without dispatching a model.
```

```text
Record a read-only scout delegation contract for this task and show me the delegation artifact, but do not start a subagent.
```

```text
Attach this read-only delegation output to the existing contract, validate the schema, and keep the no-provider/non-network claims explicit.
```

```text
Propose a project memory entry from that completed delegation result, but leave it inactive until I approve it.
```

```text
Propose a reusable project skill from that verified run, but leave it inactive until I approve it.
```

```text
Write a human-first review, evidence index, and replay summary for this run before deciding the next action.
```

```text
Write a steering review for this goal, show the next action, and list the inbox without executing or approving anything.
```

```text
Apply the operator approval request schema after I approve the generated selection template, and prove that no approval rows were created.
```

```text
Create pending operator approval request rows from the latest expansion approval draft after I approve the row-creation selection, and prove no legacy approval requests were created.
```

```text
Decide pending operator approval request rows after I approve the decision selection, and prove that no capabilities or legacy approval requests were activated.
```

```text
Review ingested capability follow-up results, accept keeping activation blocked, and prove that no approval rows or activation actions were created.
```

```text
Create proposed effects from accepted blocked follow-up result decisions, and prove that capability activation remains blocked.
```

```text
Review downstream proof-plan result records, accept keeping activation blocked, and prove that no approval rows, activation actions, or external mutations were created.
```

```text
Create proposed effects from accepted downstream proof-plan result decisions, and prove that activation remains blocked.
```

```text
Apply proposed downstream proof-plan result decision effects as local records only, and prove that activation remains blocked.
```

```text
Create downstream proof tasks from applied downstream result decision effects, and prove that activation remains blocked.
```

```text
Route downstream result effect tasks to read-only evaluator delegation packets, and prove that no subagent starts.
```

```text
Review downstream result-effect task result records, accept keeping activation blocked, and prove that no approval rows, activation actions, or external mutations were created.
```

```text
Apply proposed downstream result effect task result decision effects as local records only, and prove that capability activation remains blocked.
```

```text
Create downstream proof tasks from applied downstream result effect task result decision effects, and prove that capability activation remains blocked.
```

```text
Route downstream result effect task result effect tasks to read-only evaluator delegation packets, and prove that no subagent starts.
```

```text
Ingest completed downstream result effect task result effect delegation outputs, and prove that activation remains blocked.
```

```text
Review downstream result effect task result effect result records, accept keeping activation blocked, and prove that no approval rows, activation actions, or external mutations were created.
```

```text
Create proposed effects from accepted downstream result effect task result effect result decisions, and prove that capability activation remains blocked.
```

```text
Apply proposed downstream result effect task result effect task result effect task result decision effects as local records only, and prove that capability activation remains blocked.
```

```text
Ingest completed downstream result effect task result effect task result effect delegation outputs, and prove that activation remains blocked.
```

```text
Review downstream result effect task result effect task result effect task result records, accept keeping activation blocked, and prove that no approval rows, activation actions, or external mutations were created.
```

```text
Create proposed effects from accepted downstream result effect task result effect task result effect task result decisions, and prove that capability activation remains blocked.
```

```text
Create downstream proof tasks from applied downstream result effect task result effect task result effect task result decision effects, and prove that capability activation remains blocked.
```

```text
Route downstream result effect task result effect task result effect task result effect tasks to read-only evaluator delegation packets, and prove that no subagent starts.
```

```text
Ingest completed downstream result effect task result effect task result effect task result effect delegation outputs, and prove that activation remains blocked.
```

```text
Review downstream result effect task result effect task result effect task result effect task result records, accept keeping activation blocked, and prove that no approval rows, activation actions, or external mutations were created.
```

```text
Create proposed local effects from accepted downstream result effect task result effect task result effect task result effect task result decisions, and prove that no approval rows, activation actions, or external mutations were created.
```

```text
Apply proposed downstream result effect task result effect task result effect task result effect task result decision effects as local records only, and prove that capability activation remains blocked.
```

## Recommended Operating Loop

1. Pick one narrow capability or boundary.
2. Write or update a red-first regression when behavior changes.
3. Add the smallest implementation that creates durable local evidence.
4. Regenerate the relevant report and `docs/dashboard.md`.
5. Run `python3 -m pytest -q`.
6. Run `python3 -m agent_os.cli eval`.
7. Record specialist delegation results when read-only context is useful.
8. Propose memory from completed delegation results only when the fact is small and reusable.
9. Propose skills from verified run evidence only when the procedure is reusable.
10. Write `review`, `evidence`, and `replay-summary` packets before operator decisions on meaningful runs.
11. Run `steer`, `next-action`, and `inbox` when the next operator move is unclear.
12. Apply local schema changes only through explicit operator approval commands.
13. Create local operator approval rows only through explicit operator approval commands.
14. Decide local operator approval rows only through explicit operator approval commands.
15. Review ingested capability follow-up results before treating them as an
    activation decision.
16. Convert accepted blocked follow-up result decisions into proposed effects
    only after the review decision exists.
17. Review downstream proof-plan result records before treating the next
    evidence plan as operator-accepted.
18. Convert accepted downstream proof-plan result decisions into proposed
    effects only after the downstream review decision exists.
19. Apply downstream result decision effects as local records only after the
    proposal row exists.
20. Materialize applied downstream result decision effects into pending
    downstream proof tasks before routing or delegation.
21. Route downstream result effect tasks into read-only delegation packets
    before ingesting more proof-plan output.
22. Review downstream result effect task result records before treating the
    next evidence plan as operator-accepted.
23. Convert accepted downstream result effect task result decisions into
    proposed effects only after the downstream review decision exists.
24. Apply downstream result effect task result decision effects as local
    records only after the proposal row exists.
25. Materialize applied downstream result effect task result decision effects
    into pending downstream proof tasks before routing or delegation.
26. Route downstream result effect task result effect tasks into read-only
    delegation packets before ingesting the next proof-plan output.
27. Ingest completed downstream result effect task result effect delegation
    outputs as local result records before any operator review.
28. Review downstream result effect task result effect result records before
    treating the next evidence plan as operator-accepted.
29. Convert accepted downstream result effect task result effect result
    decisions into proposed effects only after the review decision exists.
30. Route downstream result effect task result effect task result effect tasks
    into read-only delegation packets before ingesting the next proof-plan
    output.
31. Ingest completed downstream result effect task result effect task result
    effect delegation outputs as local result records before any operator
    review.
32. Review downstream result effect task result effect task result effect task
    result records before treating the next evidence plan as operator-accepted.
33. Convert accepted downstream result effect task result effect task result
    effect task result decisions into proposed effects only after the review
    decision exists.
34. Apply downstream result effect task result effect task result effect task
    result decision effects as local records only after the proposal row exists.
35. Materialize applied downstream result effect task result effect task result
    effect task result decision effects into pending downstream proof tasks
    before routing or delegation.
36. Record non-claims before treating the work as safe.

## Approval-Gated Coding Loop

Use this loop when the desired outcome is an actual local code change:

1. Register the target repository with its default test command:

```bash
python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "python3 -m pytest -q"
```

2. Run the change in an isolated worktree:

```bash
python3 -m agent_os.cli run-goal "Make the smallest verified change" --project <name> --isolation worktree --command "<safe local command>"
```

3. Inspect `docs/dashboard.md`, especially `## Operator Cockpit`.
4. Read `runs/<run_id>/evidence/diff.patch`, `tests.txt`,
   `verification.json`, `effect.json`, and `approval.md`.
5. Use `python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "..."`
   only after the diff, tests, and policy evidence are acceptable.
6. Use `python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator`
   to re-check evidence and create the local worktree commit exactly once.
7. Use `python3 -m agent_os.cli github-handoff <effect_id> --base main --title "..."`
   when you want a local push/draft-PR packet after commit evidence exists.
8. Use `python3 -m agent_os.cli ci-deploy-evidence <github_handoff_id> --provider github-actions --status success --external-run-id <run_id> --url <run_url>`
   after real CI/deploy evidence exists and should be preserved locally.
9. Use `python3 -m agent_os.cli profiles`, `profile-show <name>`, and
   `route ...` to record profile routing choices before specialist work.
10. Use `python3 -m agent_os.cli delegate <task_id> --profile scout --title "..."`
   to create a read-only delegation contract when specialist prep is useful.
11. Use `python3 -m agent_os.cli record-delegation-result <delegation_id> --summary "..." --output-json '{...}'`
   to attach structured read-only output to an existing delegation.
12. Use `python3 -m agent_os.cli memory propose-from-delegation <delegation_id> --key "..."`
   to create an inactive memory proposal from completed delegation evidence.
13. Use `python3 -m agent_os.cli memory approve <memory_id> --approved-by operator`
   only after reviewing the proposal.
14. Use `python3 -m agent_os.cli skill propose --project <name> --name "..." --description "..." --from-run <run_id>`
   to create an inactive reusable `SKILL.md` proposal from run evidence.
15. Use `python3 -m agent_os.cli skill approve <skill_id> --approved-by operator`
   only after reviewing the generated `SKILL.md`.
16. Use `python3 -m agent_os.cli review <run_id>`, `evidence <run_id>`, and
   `replay-summary <run_id>` to create operator-readable run packets before
   making follow-up decisions.
17. Use `python3 -m agent_os.cli cleanup-worktrees --confirm --reason "..."`
   after reviewing terminal effects and deciding the worktree can be removed.

`commit-approved` blocks without committing if the worktree base commit, patch,
changed files, or stored test command no longer match the approved evidence.
`github-handoff` requires committed local effect evidence, writes a local
handoff packet, and prints operator `git push` plus `gh pr create --draft`
commands while recording `network_actions_taken=0`.
`ci-deploy-evidence` requires a GitHub handoff packet and records
operator-supplied proof while also recording `network_actions_taken=0`.
`profiles` creates safe local planner/coder/scout/tester/evaluator defaults
and `.clanker/profiles.yml`. `route` records profile selection decisions for
task ids or category/project pairs without claiming tasks or calling model
providers.
`delegate` stores a scoped pending delegation contract and JSON artifact under
`.clanker/delegations/`; it does not start a subagent, call a model provider,
write files, approve work, commit, or mutate external state.
`record-delegation-result` marks a delegation completed only after structured
operator-supplied output matches the expected schema family. It writes a local
result artifact and preserves `network_actions_taken=0`.
`memory propose-from-delegation` creates a proposed memory entry from a
completed delegation result. It writes local JSON evidence and does not make
the memory active until `memory approve` is run.
`skill propose` creates a proposed skill record and writes
`.clanker/skills/<name>/SKILL.md` from run evidence. It records a skill version
and does not make the skill active until `skill approve` is run.
`review`, `evidence`, and `replay-summary` write local Markdown packets under
`runs/<run_id>/` and expose them in the dashboard. They do not rerun commands,
approve effects, commit, push, deploy, or mutate external systems.
`steer <goal_id>` writes a local steering review from existing goals, tasks,
approvals, and incidents. `next-action <goal_or_project>` refreshes that
review and prints the recommended operator move. `inbox` lists operator-worthy
steering reviews, pending approvals, and open incidents. They do not execute
tasks, approve work, retry, commit, push, deploy, or mutate external systems.
`cleanup-worktrees` removes only clean terminal worktrees; dirty blocked
worktrees are recorded as blocked and left in place.

## Reading The Reports

Prefer these files when orienting:

- `docs/next-iteration.md` for the next suggested local work packet.
- `docs/dashboard.md` for the current operational view.
- `docs/OPERATING_SUMMARY.md` for architecture and guardrails.
- `docs/tutorial-subagent-delegation-results.md` for the profile routing,
  delegation contract, and result-ingestion loop.
- `docs/tutorial-run-review.md` for human-first run review, evidence indexing,
  and conceptual replay.
- `docs/tutorial-steering-inbox.md` for deterministic steering reviews,
  next-action output, and local inbox triage.
- `docs/tutorial-capability-followup-result-decisions.md` for reviewing
  ingested follow-up evidence while keeping activation blocked.
- `docs/tutorial-capability-followup-result-effect-proposals.md` for creating
  proposed local effects from accepted blocked follow-up decisions.
- `docs/tutorial-capability-followup-result-task-results.md` for ingesting
  completed downstream proof-plan delegation outputs as local result records.
- `docs/tutorial-capability-followup-result-task-decisions.md` for reviewing
  downstream proof-plan result records while keeping activation blocked.
- `docs/tutorial-capability-followup-result-task-result-effect-proposals.md`
  for creating proposed local effects from accepted downstream result
  decisions.
- `docs/tutorial-capability-followup-result-task-result-effect-task-results.md`
  for ingesting completed downstream result effect task delegation outputs.
- `docs/tutorial-capability-followup-result-task-result-effect-task-decisions.md`
  for reviewing downstream result effect task result records while keeping
  activation blocked.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-proposals.md`
  for creating proposed effects from accepted downstream result effect task
  result decisions.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-application.md`
  for applying proposed downstream result effect task result decision effects
  as local records.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-tasks.md`
  for creating pending downstream proof tasks from applied downstream result
  effect task result decision effects.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-delegations.md`
  for routing downstream result effect task result effect tasks to read-only
  evaluator delegation packets.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-results.md`
  for ingesting completed downstream result effect task result effect
  delegation outputs as local result records.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-decisions.md`
  for reviewing downstream result effect task result effect result records
  while keeping activation blocked.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results.md`
  for ingesting completed downstream result effect task result effect task
  result effect delegation outputs as local result records.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`
  for reviewing downstream result effect task result effect task result effect
  task result records while keeping activation blocked.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md`
  for creating proposed effects from accepted downstream result effect task
  result effect result decisions.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-application.md`
  for applying proposed downstream result effect task result effect result
  decision effects as local records.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`
  for creating pending downstream proof tasks from applied downstream result
  effect task result effect task result effect task result decision effects.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`
  for applying proposed downstream result effect task result effect task result
  effect task result effect task result decision effects as local records.
- `docs/tutorial-capability-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`
  for creating pending downstream proof tasks from applied downstream result
  effect task result effect task result effect task result effect task result
  decision effects.
- `contracts.md` for safety boundaries and evidence expectations.
- `status.md` for chronological implementation evidence.
- `projects/bootstrap/handoff.md` for the current continuation edge.

## Approval Boundaries

Allowed actions are not actions taken. A report may list choices such as
`approve`, `defer`, and `request_more_evidence` while still preserving:

- `selected_action=none`;
- `actions_taken=0`;
- `selections_recorded=0`;
- zero migration/table/approval-row creation counters.

Treat those zeros as intentional safety evidence. Do not cross them without an
explicit operator-approved flow and fresh verification.

When the generated schema migration selection template is ready, the narrow
approved crossing is:

```bash
python3 -m agent_os.cli expansion-operator-approval-schema-migration-apply \
  --operator-id operator \
  --selected-action approve \
  --selection-note "Approved local operator approval request schema." \
  --evidence-reference docs/expansion-operator-approval-schema-migration-selection-input-template.md
```

That command may create the local `operator_approval_requests` table. It must
still report `operator_approval_rows_created: 0` and
`approval_requests_created: 0`.

After the table exists, the narrow approved row-creation crossing is:

```bash
python3 -m agent_os.cli expansion-operator-approval-request-rows-apply \
  --operator-id operator \
  --selected-action approve \
  --selection-note "Approved local operator approval request row creation after reviewing the draft packet." \
  --evidence-reference docs/expansion-operator-approval-draft.md
```

That command may create pending local `operator_approval_requests` rows from
the latest expansion approval draft. It must still report
`approval_requests_created: 0`, and it does not decide, promote, route,
deploy, or mutate external systems.

After pending rows exist, the narrow local decision crossing is:

```bash
python3 -m agent_os.cli expansion-operator-approval-request-decide \
  --operator-id operator \
  --selected-action approve \
  --selection-note "Approved pending operator approval requests after reviewing evidence." \
  --evidence-reference docs/expansion-operator-approval-request-rows-application.md
```

That command may update pending local `operator_approval_requests` rows to
`approved`, `deferred`, or `more_evidence_requested` depending on the selected
action. It must still report `approval_requests_created: 0`, and it does not
enable capabilities, promote trust, route work, deploy, or mutate external
systems.

After approved rows exist, create proposal records without applying them:

```bash
python3 -m agent_os.cli expansion-operator-approval-effect-proposals
```

This command writes `proposed` effect rows for approved local operator approval
requests and links each row back to the original operator request. It must
still report `legacy_approval_requests_created: 0` and
`activation_actions_taken: 0`; it does not enable capabilities, promote trust,
route work, schedule workers, retry work, track spend, deploy, or mutate
external systems.

After proposed effects exist, apply them as local records:

```bash
python3 -m agent_os.cli expansion-operator-approval-effect-apply \
  --operator-id operator \
  --selection-note "Apply approved local operator approval effect proposals as local records only." \
  --evidence-reference docs/expansion-operator-approval-effect-proposals.md
```

This command may move operator approval effects from `proposed` to `applied`
and write local application evidence. It must still report
`legacy_approval_requests_created: 0`, `activation_actions_taken: 0`, and
`capability_enabled=false`; it does not enable hosted dashboard, remote
workers, schedulers, adapters, CI/deploy, budget enforcement, trust promotion,
automatic retry, real-cost tracking, or external systems.

After applied capability effects exist, create pending activation-gate tasks:

```bash
python3 -m agent_os.cli capability-activation-tasks
```

This command creates one pending high-risk task per applied capability effect
and links each task back to its source effect. It must still report
`activation_actions_taken: 0`; the tasks are guardrails for future evidence
and approval work, not capability enablement.

Turn those pending activation tasks into blocked evidence and approval
contracts:

```bash
python3 -m agent_os.cli capability-activation-contracts
python3 -m agent_os.cli dashboard
```

This creates one blocked activation contract per pending activation task. Each
contract records required artifacts, required commands,
`explicit_operator_approval_required`, and `blocked_until_evidence_verified`.
It must still report `approval_requests_created: 0` and
`activation_actions_taken: 0`; it does not create `approval_requests` rows or
enable capabilities.

Attach local evidence and record the current operator decision:

```bash
python3 -m agent_os.cli capability-activation-evidence \
  --all \
  --evidence-kind proof_checklist \
  --evidence-reference docs/capability-activation-contracts.md \
  --verification-command "python3 -m agent_os.cli capability-activation-contracts" \
  --verification-status blocked \
  --recorded-by operator \
  --summary "Current activation contracts are present but still missing capability-specific proof."
python3 -m agent_os.cli capability-activation-decide \
  --operator-id operator \
  --selected-action request_more_evidence \
  --selection-note "Requested capability-specific proof before any activation decision." \
  --evidence-reference docs/capability-activation-evidence.md
```

This records local evidence rows and a local decision state for each contract.
It does not approve capability activation. In the current blocked proof state,
the safe decision is `request_more_evidence`.

Turn the `request_more_evidence` decisions into pending queue work:

```bash
python3 -m agent_os.cli capability-activation-followups
python3 -m agent_os.cli dashboard
```

This creates one pending high-risk `capability_activation_followup_task` per
contract that needs more evidence. It is task graph state for future evidence
collection; it does not create approval rows, satisfy proof, or enable
capabilities.

Turn the pending follow-up evidence tasks into read-only delegation packets:

```bash
python3 -m agent_os.cli capability-activation-followup-delegations
python3 -m agent_os.cli dashboard
```

This records routing decisions to the `evidence_review` category and creates
pending evaluator delegation packets with local JSON artifacts. It does not
start subagents, call model providers, create approval rows, satisfy proof, or
enable capabilities.

After an operator records a completed evaluator result with
`record-delegation-result`, ingest those completed follow-up results into the
capability evidence trail:

```bash
python3 -m agent_os.cli capability-activation-followup-results
python3 -m agent_os.cli dashboard
```

This writes local result records and JSON artifacts for completed read-only
evaluator delegation results. It keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`; the record is evidence for operator review, not
proof satisfaction or capability enablement.

Record the local operator review decision over ingested results:

```bash
python3 -m agent_os.cli capability-activation-followup-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted evaluator result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-results.md
python3 -m agent_os.cli dashboard
```

This writes `docs/capability-activation-followup-decisions.md` and a local
decision row for result records that have not already been reviewed. It keeps
`approval_requests_created=0` and `activation_actions_taken=0`; the
`accept_keep_blocked` action is an operator review state, not capability
enablement.

After accepted blocked follow-up result decisions exist, create proposed effect
rows:

```bash
python3 -m agent_os.cli capability-activation-followup-result-effect-proposals
python3 -m agent_os.cli dashboard
```

This writes
`docs/capability-activation-followup-result-effect-proposals.md` and local
`proposed` effect rows in the generic effects ledger. It keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`; the effect row is a traceable local proposal, not
capability enablement.

After proposed follow-up result effects exist, apply the accepted blocked
effects locally and materialize the next downstream proof task:

```bash
python3 -m agent_os.cli capability-activation-followup-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted blocked follow-up result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-effect-proposals.md
python3 -m agent_os.cli capability-activation-followup-result-tasks
python3 -m agent_os.cli capability-activation-followup-result-task-delegations
python3 -m agent_os.cli dashboard
```

The task command writes
`docs/capability-activation-followup-result-tasks.md` and creates one pending
`capability_activation_followup_result_task` per applied follow-up result
effect that has not already been materialized. It preserves source decision,
result, delegation, follow-up task, contract, and capability links while
keeping `approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

The delegation command writes
`docs/capability-activation-followup-result-task-delegations.md` and creates
read-only evaluator delegation packets for pending
`capability_activation_followup_result_task` rows that do not already have a
packet. It keeps `execution_started=0`, `network_actions_taken=0`,
`external_mutations_taken=0`, and `activation_actions_taken=0`; the packets
are local proof-planning contracts, not worker execution.

After a downstream proof-plan delegation has been completed by recording an
operator-supplied structured result, ingest it as a local downstream result
record:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Evaluator drafted the next evidence plan while keeping activation blocked." \
  --output-json '{"evidence":[{"status":"planned","summary":"Collect hosted dashboard proof."}],"findings":[{"summary":"Keep activation blocked."}]}'
python3 -m agent_os.cli capability-activation-followup-result-task-results
python3 -m agent_os.cli dashboard
```

The result command writes
`docs/capability-activation-followup-result-task-results.md`, stores one local
result row per completed downstream delegation, and writes JSON artifacts under
`docs/capability-activation-followup-result-task-results/`. It keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`; the result is a preserved evidence plan, not
capability activation or proof satisfaction.

Review those downstream result records explicitly before using them as accepted
operator posture:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-results.md
python3 -m agent_os.cli dashboard
```

The decision command writes
`docs/capability-activation-followup-result-task-decisions.md` and records the
selected operator action for downstream result records that have not already
been decided. It keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`.

Convert accepted blocked downstream result decisions into local proposed
effects:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-proposals
python3 -m agent_os.cli dashboard
```

The proposal command writes
`docs/capability-activation-followup-result-task-result-effect-proposals.md`
and creates `proposed` rows in the generic `effects` ledger for accepted
downstream result decisions. It keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`; it does not apply
the proposed effects.

Apply accepted blocked downstream result decision effects as local records:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream proof-plan result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-proposals.md
python3 -m agent_os.cli dashboard
```

The application command writes
`docs/capability-activation-followup-result-task-result-effect-application.md`,
records a local application row, and marks applicable proposed effects as
`applied`. It keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`.

Create downstream proof tasks from applied downstream result decision effects:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-tasks
python3 -m agent_os.cli dashboard
```

The task command writes
`docs/capability-activation-followup-result-task-result-effect-tasks.md`,
records a local batch row, and creates pending high-risk task graph records
for applied downstream result decision effects that do not already have a
downstream task. It keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`.

Route downstream result effect tasks into read-only evaluator delegation
packets:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-delegations
python3 -m agent_os.cli dashboard
```

The delegation command writes
`docs/capability-activation-followup-result-task-result-effect-task-delegations.md`,
records local routing and delegation batch rows, and writes pending delegation
JSON artifacts under `.clanker/delegations/`. It keeps
`execution_started=0`, `network_actions_taken=0`,
`external_mutations_taken=0`, `approval_requests_created=0`,
`activation_actions_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

After a downstream result effect task delegation has been completed by
recording an operator-supplied structured result, ingest it as a local result
record:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Evaluator drafted downstream result-effect proof evidence while keeping activation blocked." \
  --output-json '{"evidence":[{"status":"planned","summary":"Collect downstream result-effect proof evidence."}],"findings":[{"summary":"Keep activation blocked."}]}'
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-results
python3 -m agent_os.cli dashboard
```

The result command writes
`docs/capability-activation-followup-result-task-result-effect-task-results.md`,
stores one local result row per completed downstream result effect task
delegation, and writes JSON artifacts under
`docs/capability-activation-followup-result-task-result-effect-task-results/`.
It keeps `approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`; the result is a preserved evidence plan, not
capability activation or proof satisfaction.

Review downstream result effect task result records with an operator decision:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-results.md
python3 -m agent_os.cli dashboard
```

The decision command writes
`docs/capability-activation-followup-result-task-result-effect-task-decisions.md`,
records the operator action in SQLite, and keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

Create proposed effects from accepted downstream result effect task result
decisions:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-proposals
python3 -m agent_os.cli dashboard
```

The proposal command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-proposals.md`,
creates generic local `effects` rows with idempotency keys, and keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`. It does not apply the proposed effects; that is
the next local application-record slice.

Apply accepted downstream result effect task result decision effects as local
records:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-proposals.md
python3 -m agent_os.cli dashboard
```

The application command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-application.md`,
records a local application row, and marks applicable proposed effects as
`applied`. It keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`.

Create downstream proof tasks from those applied effects:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli dashboard
```

The task command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-tasks.md`,
records a local batch row, and creates pending high-risk task graph records
for applied downstream result effect task result decision effects that do not
already have a downstream task. It keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`.

Route those downstream result effect task result effect tasks into read-only
evaluator delegation packets:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli dashboard
```

The delegation command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations.md`,
records local routing and delegation batch rows, and writes pending delegation
JSON artifacts under `.clanker/delegations/`. It keeps
`execution_started=0`, `network_actions_taken=0`,
`external_mutations_taken=0`, `approval_requests_created=0`,
`activation_actions_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

After a downstream result effect task result effect delegation has been
completed by recording an operator-supplied structured result, ingest it as a
local result record:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Evaluator drafted downstream result-effect task result-effect proof evidence while keeping activation blocked." \
  --output-json '{"evidence":[{"status":"planned","summary":"Collect downstream result-effect task result-effect proof evidence."}],"findings":[{"summary":"Keep activation blocked."}]}'
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli dashboard
```

The result command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md`,
stores one local result row per completed downstream result effect task result
effect task delegation, and writes JSON artifacts under
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results/`.
It keeps `approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`; the record is the next preserved evidence plan,
not capability activation or proof satisfaction.

Review those downstream result effect task result effect result records before
they drive the next local effect proposal:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md
python3 -m agent_os.cli dashboard
```

The decision command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-decisions.md`,
records the operator action, and keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`.

Create proposed local effects from accepted downstream result effect task
result effect result decisions:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals
python3 -m agent_os.cli dashboard
```

The proposal command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
creates generic local `effects` rows for accepted blocked decisions, and keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

Apply those proposed effects as local application records:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-apply \
  --operator-id operator \
  --selection-note "Apply accepted downstream result-effect task result-effect task result effect proposals as local records only." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md
python3 -m agent_os.cli dashboard
```

The application command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-application.md`,
records a local application row, marks applicable generic `effects` rows as
`applied`, and keeps `approval_requests_created=0`,
`activation_actions_taken=0`, `external_mutations_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`.

Materialize those applied effects into pending downstream proof tasks:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli dashboard
```

The task command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-tasks.md`,
creates pending high-risk local proof tasks, and keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

Route those pending tasks to read-only evaluator delegation packets:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli dashboard
```

The delegation command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`,
records local `evidence_review` routing decisions and pending evaluator
delegation packets, and keeps `execution_started=0`,
`network_actions_taken=0`, `external_mutations_taken=0`,
`activation_actions_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`. The packet is a local proof-planning contract, not
subagent execution.

Route the next pending downstream proof tasks to read-only evaluator delegation
packets:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli dashboard
```

The delegation command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`,
records local `evidence_review` routing decisions and pending evaluator
delegation packets, and keeps `execution_started=0`,
`network_actions_taken=0`, `external_mutations_taken=0`,
`approval_requests_created=0`, `activation_actions_taken=0`,
`activation_allowed=false`, and `capability_enabled=false`. The packet is still
a local proof-planning contract, not subagent execution.

After an operator records a completed evaluator output, ingest that local result
artifact:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli dashboard
```

The result command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`,
creates local result records and per-result JSON artifacts, and keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`,
`capability_enabled=false`, and proof satisfaction blocked. Missing result
artifacts are reported without creating result rows.

After the result record exists, record the operator review decision:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
python3 -m agent_os.cli dashboard
```

The decision command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`,
records the operator action against local result ids, and still keeps
`approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

After an accepted blocked decision exists, create the local proposed effect:

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals
python3 -m agent_os.cli dashboard
```

The proposal command writes
`docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
creates idempotent generic `effects` rows for accepted blocked decisions, and
still keeps `approval_requests_created=0`, `activation_actions_taken=0`,
`external_mutations_taken=0`, `activation_allowed=false`, and
`capability_enabled=false`.

## When To Commit And Push

Commit when:

- the scope is coherent;
- generated reports match the current state;
- `python3 -m pytest -q` passes;
- `git diff --check` is clean;
- the commit message describes the operational increment.

Push after the branch target and remote are explicit. For the public GitHub
repo, prefer `main` only for verified snapshots that are useful to share.

## Practical Next Slices

Good next slices now favor result ingestion and capability-specific guards after
local delegation packets exist:

- result ingestion for downstream result effect task result effect task result
  effect task result effect delegation packets;
- per-request operator decision targeting and inbox refinement;
- hosted-dashboard proof only after local commit and CI/deploy evidence is
  modeled;
- remote-worker, scheduler, browser/desktop adapter, budget, trust, retry, and
  real-cost surfaces only after their evidence and approval contracts can be
  enforced.

Each slice should end with explicit non-claims. That discipline is the point:
the system should show what is safe to trust, what is only locally proven, and
what remains blocked.
