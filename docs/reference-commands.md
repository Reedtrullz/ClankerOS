# Command Reference

This is a compact map for common ClankerOS commands. Generated reports contain
the detailed proof for each capability.

## Setup And Status

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli projects
python3 -m agent_os.cli project-status <project>
python3 -m agent_os.cli project-context <project>
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
python3 -m agent_os.cli approvals
python3 -m agent_os.cli queue-health
python3 -m agent_os.cli handoff-review
```

## First Loop

```bash
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli evidence <run_id>
python3 -m agent_os.cli replay-summary <run_id>
python3 -m agent_os.cli steer <goal_id>
python3 -m agent_os.cli next-action <goal_or_project>
python3 -m agent_os.cli inbox
```

`evidence <run_id>` now prints `packet_dir` and writes goal-scoped packet
files under `.clanker/projects/<project>/goals/<goal_id>/runs/<run_id>/evidence/`.
For `run-task` runs it preserves executable proof files and writes aggregate
operator snapshots as sidecars.

## Goal Planning Lifecycle

```bash
python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli goal "Make the smallest verified improvement" --project <name>
python3 -m agent_os.cli plan <goal_id>
python3 -m agent_os.cli contract <goal_id>
python3 -m agent_os.cli tasks <goal_id>
python3 -m agent_os.cli run-task <task_id> --profile tester
python3 -m agent_os.cli task-recommendations --goal <goal_id>
python3 -m agent_os.cli update-task <task_id> --status blocked --blocked-reason "waiting on operator scope"
python3 -m agent_os.cli replan <goal_id> --reason "scope changed after operator review"
python3 -m agent_os.cli dashboard
```

`goal` requires a registered project. It creates a durable goal row, plan v1,
three `planned_step` task rows, and artifacts under
`.clanker/projects/<project>/goals/<goal_id>/`. `plan` and `replan` keep
versioned `PLAN-vN.md` files plus the latest `PLAN.md`. `contract` creates a
draft sprint contract for the latest plan. `run-task` dispatches one
`status=planned` task through a profile-gated local verifier, records a
routing decision, creates a run, writes an evidence packet under the goal, and
updates the linked plan step. It does not commit, push, deploy, call model
providers, start subagents, or mutate external systems.
`evidence <run_id>` preserves existing command-proof files from `run-task` and
adds review-side packet files, including `git_status.txt`, `diff.patch`, and
`changed_files.json`. The git target is the registered project repo when one is
known for the run, otherwise the ClankerOS root. This is a local snapshot; it
does not fetch, pull, commit, push, rerun commands, or approve effects.
`task-recommendations` records idempotent local `task_recommendations` rows and
writes `docs/task-recommendations.md` for failed planned-task runs and blocked
planned tasks. It recommends review/replan/manual reset commands but does not
retry, reset, replan, dispatch, approve, or mutate external systems.

## Approval-Gated Coding

```bash
python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli project-context <name>
python3 -m agent_os.cli run-goal "Make a tiny verified change" --project <name> --isolation worktree --command "<safe local command>"
python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "reviewed diff and tests"
python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator
python3 -m agent_os.cli github-handoff <effect_id> --base main --title "Change title"
python3 -m agent_os.cli cleanup-worktrees --confirm --reason "committed branch kept"
```

## Profiles And Delegation Packets

```bash
python3 -m agent_os.cli profiles
python3 -m agent_os.cli profile-show scout
python3 -m agent_os.cli route --category repo_search --project bootstrap
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli delegations <goal_id>
python3 -m agent_os.cli profile-adapter scout --command "python3 .clanker/adapters/fake_scout.py" --input-mode json_file --output-mode json --timeout-seconds 120
python3 -m agent_os.cli run-delegation <delegation_id>
python3 -m agent_os.cli delegation-result <delegation_id>
python3 -m agent_os.cli record-delegation-result <delegation_id> --summary "Relevant files identified." --output-json '{"files":["agent_os/cli.py"],"findings":["CLI parser lives in agent_os/cli.py."],"relevant_files":["agent_os/cli.py"]}'
```

`run-delegation` executes a pending read-only delegation through the configured
local shell adapter, writes `.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/`,
validates JSON output, and opens local incidents for adapter or validation
failures. `record-delegation-result` remains the manual ingestion path for
operator-supplied output.

## Memory And Skills

```bash
python3 -m agent_os.cli memory propose --project bootstrap --key <key> --value <value> --source <source>
python3 -m agent_os.cli memory propose-from-delegation <delegation_id> --key <key>
python3 -m agent_os.cli memory list --project bootstrap
python3 -m agent_os.cli memory approve <memory_id> --approved-by operator
python3 -m agent_os.cli skill propose --project bootstrap --name <name> --description <description> --from-run <run_id>
python3 -m agent_os.cli skills --project bootstrap
python3 -m agent_os.cli skill approve <skill_id> --approved-by operator
```

## Verification

```bash
python3 -m py_compile agent_os/storage.py agent_os/planning.py agent_os/cli.py agent_os/dashboard.py agent_os/iteration.py
python3 -m pytest -q
python3 -m agent_os.cli eval-candidates
python3 -m agent_os.cli eval-after-change --change "<change name>" --file <path>
python3 -m agent_os.cli eval
python3 -m agent_os.cli playbooks
git diff --check
```

## Capability Activation Proof Tasks

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide --operator-id operator --selected-action accept_keep_blocked --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task proof-plan result and kept capability activation blocked." --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply --operator-id operator --selection-note "Apply accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task result effect proposals as local records only." --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide --operator-id operator --selected-action accept_keep_blocked --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task proof-plan result and kept capability activation blocked." --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply --operator-id operator --selection-note "Apply accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task result effect proposals as local records only." --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide --operator-id operator --selected-action accept_keep_blocked --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task proof-plan result and kept capability activation blocked." --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
```

This creates pending downstream proof tasks from applied local effects and
then routes those tasks into read-only evaluator delegation packets. Completed
local evaluator outputs can be ingested as result records, and those records
remain blocked for operator decisions. Accepted blocked decisions can
then create local proposed effect rows, apply those proposed rows as local
application records only, and materialize the applied local effects as the next
pending proof tasks. The latest task rung can also be routed into read-only
evaluator delegation packets and ingested after an operator records structured
delegation output. The latest result records can now receive a local
accept-keep-blocked, request-more-evidence, or defer-review decision, and
accepted blocked decisions can create idempotent proposed effect rows.
Those proposed effect rows can now be applied as local application records
only, keeping the generic `effects` row applied while preserving zero approval,
activation, and external mutation counters. The latest applied rows can now
materialize pending downstream proof tasks without routing or executing them.
The latest downstream result-effect task result-effect task result-effect task
result-effect task result-effect task result-effect task result-effect task
result-effect task result records can now also receive local
accept-keep-blocked, request-more-evidence, or defer-review decisions.
Approval, activation, execution,
network, and external
mutation counters stay at zero.

## Publishing

```bash
git status --short --branch
git diff --check
python3 -m pytest -q
gh repo view Reedtrullz/ClankerOS --json description,repositoryTopics,homepageUrl
git push origin main
```

Pushing is not deployment. GitHub metadata readback is not CI proof.
