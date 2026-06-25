# Command Reference

This is a compact map for common ClankerOS commands. Generated reports contain
the detailed proof for each capability.

Default `python3 -m agent_os.cli --help` now favors the implementation-handoff
operator workflow and hides legacy proof-ladder commands from the first-view
command list. The hidden commands remain callable by exact name and are kept in
this reference for advanced blocked-proof work.

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
python3 -m agent_os.cli profile-adapter scout --command "python3 /absolute/path/to/project_scout.py" --input-mode json_file --output-mode json --working-directory project_root --timeout-seconds 120
python3 -m agent_os.cli context-pack <delegation_id> --max-files 12 --max-snippets 8 --max-total-chars 12000
python3 -m agent_os.cli run-delegation <delegation_id>
python3 -m agent_os.cli delegation-result <delegation_id>
python3 -m agent_os.cli implementation-handoff <delegation_id>
python3 -m agent_os.cli coder-prep <delegation_id>
python3 -m agent_os.cli coder-worktree-plan <delegation_id>
python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "Approve bounded worktree execution"
python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "Approved bounded execution"
python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify
python3 -m agent_os.cli record-delegation-result <delegation_id> --summary "Relevant files identified." --output-json '{"files":["agent_os/cli.py"],"findings":["CLI parser lives in agent_os/cli.py."],"relevant_files":["agent_os/cli.py"]}'
```

`run-delegation` executes a pending read-only delegation through the configured
local shell adapter, writes `.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/`,
validates JSON output, and opens local incidents for adapter or validation
failures. Adapter configs default to `--working-directory system_root`; use
`--working-directory project_root` for registered-project repo scouts that need
relative reads from the target repository. Registered-project delegations add
`project.json`, `repo_files.json`, `project`, and `repo_scouting` context to
the evidence packet/input bundle.

`context-pack <delegation_id>` writes deterministic scout context before
execution:

```text
.clanker/delegations/<delegation_id>/context/context_pack.json
.clanker/delegations/<delegation_id>/context/context_pack.md
```

Useful flags:

- `--max-files`
- `--max-snippets`
- `--max-snippet-chars`
- `--max-total-chars`
- `--include-glob`
- `--exclude-glob`
- `--format json|markdown|both`

`run-delegation` auto-generates the pack when it is missing, copies it into the
run evidence packet, and puts compact `context_pack` metadata in `input.json`.
Successful executable delegations also write first-class implementation
handoff artifacts:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.json
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.md
```

The handoff JSON includes `schema_version: 1`, kind
`implementation_context_handoff`, context-pack paths/counts, returned-file
inventory validation, scout returned files, and non-claims. It intentionally
points at `context_pack.json` and `context_pack.md` instead of embedding large
snippets. `implementation-handoff <delegation_id>` parses the artifact and
prints readability, schema/kind, context-pack validation, top ranked files,
test hints, scout relevant files, and `snippets_embedded`. Missing or
unreadable handoffs return non-zero with explicit status. `delegation-result`,
`review`, `inbox`, and `dashboard` also surface handoff health and validation
summary.

`coder-prep <delegation_id>` consumes the readable `implementation_handoff.md`
and writes a bounded future coding packet under:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_prep.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_prep.md
```

The prep packet records the source handoff hash, allowed files, candidate test
files, acceptance criteria, risks, and a run plan with
`status=operator_review_required` and `dispatch_ready=false`. It is
idempotent for the same handoff hash and reports
`task_rows_created=0`, `runs_created=0`, `routing_decisions_created=0`,
`worktrees_created=0`, `approval_requests_created=0`, `source_edits=0`,
`commands_rerun=0`, `network_actions_taken=0`, and
`external_mutations_taken=0`. `review` and `dashboard` surface existing coder
prep packets, but the command does not dispatch work or edit files.

`coder-worktree-plan <delegation_id>` consumes the readable `coder_prep.md`
and writes an approval-gated future worktree/run packet beside the prep files:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_plan.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_plan.md
```

The worktree plan records the source prep Markdown hash, bounded allowed files,
candidate tests, proposed branch/path, future explicit
`run-goal --isolation worktree` shape, and an approval gate with
`status=operator_approval_required` and `dispatch_ready=false`. It is
idempotent for the same `coder_prep.md` hash and reports
`task_rows_created=0`, `runs_created=0`, `routing_decisions_created=0`,
`worktrees_created=0`, `approval_requests_created=0`, `source_edits=0`,
`commands_rerun=0`, `provider_calls_taken_by_clankeros=0`,
`network_actions_taken=0`, and `external_mutations_taken=0`. It does not
create a worktree, run commands, request approval, dispatch work, edit files,
commit, push, deploy, call providers, or mutate external systems.

`coder-worktree-approval <delegation_id>` loads the latest
`coder_worktree_plan.json`, validates the kind, `dispatch_ready=false`,
approval gate, source hash, registered project, and non-empty allowed files,
then writes:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_approval_request.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_approval_request.md
```

It creates a dedicated local approval record tied to the current plan hash and
is idempotent for that hash unless `--force-new` is used. It does not create a
worktree, run commands, edit source, commit, push, deploy, call providers, or
use the network.

`approve-coder-worktree <approval_id>` marks a pending coder worktree request
approved and writes:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_approval_decision.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/coder_worktree_approval_decision.md
```

It tolerates already-approved requests and prints `already_approved`. It does
not create a worktree, run commands, edit source, commit, push, deploy, call
providers, or use the network.

`run-coder-worktree <delegation_id> --command "<safe local command>" --verify`
requires readable plan/prep/handoff artifacts, a registered project root, a
non-empty allowed-file list, an approved matching plan hash, and a command
that passes conservative local-command validation. It creates a local git
worktree under `.agent/worktrees/<project>/<run_id>/`, runs the command inside
that worktree, optionally runs the registered default verifier or
`--verify-command`, and writes:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/run.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/command.txt
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/stdout.txt
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/stderr.txt
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/verification_command.txt
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/verification_stdout.txt
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/verification_stderr.txt
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/git_status.txt
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/diff.patch
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/changed_files.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/bounded_file_validation.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/approval.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/source_plan.json
.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/summary.md
```

Changed files must be a subset of `allowed_files`; outside files mark the run
`blocked` with `failure_class=bounded_file_violation`. Command or verification
failures mark the run `failed`. Completed approval/plan pairs are not rerun
unless `--rerun` is provided. The command does not commit, push, deploy, call
providers, or intentionally use the network.

`coder-commit-request <coder_worktree_run_id> --requested-by <id> --message
<commit_message> --note <note>` is the next gate after a successful coder
worktree run has been included in `review <coder_worktree_run_id>` or the
source delegation run review. It refuses unreviewed, failed, blocked,
outside-file, no-change, missing-worktree, unsafe-git-state, stale-source, or
failed-verification runs unless the operator explicitly used
`--allow-unverified` at request time. For eligible reviewed runs it records the
current worktree HEAD, source `run.json` hash, `diff.patch` hash, changed-file
list, review path, branch, and commit message, then writes both compatibility
and modern request artifacts. The modern operator artifacts are:

```text
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/coder_commit_request.json
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/coder_commit_request.md
```

The request is idempotent for the same run evidence, diff hash, and commit
message unless `--force-new` is used. A different commit message creates a
separate request. It does not stage files, create a commit, push, create a PR,
deploy, call providers, or use the network.

`approve-coder-commit <commit_request_id> --decided-by <id> --note <note>`
marks that dedicated request approved and writes:

```text
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/coder_commit_decision.json
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/coder_commit_decision.md
```

The approval decision does not stage files, create a commit, push, create a
PR, deploy, call providers, or use the network.

`commit-coder-worktree <coder_worktree_run_id> --message <commit_message>` is
the only command in the coder worktree path that stages files and creates a
local git commit. It requires an approved matching commit request, blocks if the
source run hash changed, the worktree path is outside `.agent/worktrees`, the
branch or HEAD moved, outside files appeared, files outside `allowed_files` are
already staged, the changed file list differs, the commit message differs, or
the verifier no longer passes. Use `--use-approved-message` only when the
operator wants the message stored on the approved request. The command stages
only reviewed allowed files, re-inspects the staged set before commit, and
creates one commit in the isolated coder worktree branch. It writes:

```text
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/commit.json
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/commit.md
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/pre_commit_status.txt
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/post_commit_status.txt
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/committed_diff.patch
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_commit/committed_files.json
```

The local commit records a committed `local_git_commit` effect. Pass the
printed `effect_id` to `github-handoff <effect_id>` to write local push and
draft-PR instructions. The handoff still takes `network_actions_taken=0` and
does not push, create a PR, deploy, call providers, or mutate external
systems. Compatibility commands remain available as
`coder-worktree-commit-approval`, `approve-coder-worktree-commit`, and
`promote-coder-worktree-commit`, but the shorter `coder-commit-request`,
`approve-coder-commit`, and `commit-coder-worktree` names are the primary
operator flow.

`coder-publication-request <coder_worktree_run_id> --requested-by <id>
--remote origin --target-branch main --note <note>` is the next boundary after
the isolated local coder worktree commit. It requires a valid
`coder_commit/commit.json`, verifies the commit SHA exists in the isolated
worktree, checks committed files remain inside `allowed_files`, validates safe
remote and target branch names, and writes:

```text
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_publication/publication_request.json
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_publication/publication_request.md
```

The request is idempotent for the same commit artifact hash, remote, and target
branch unless `--force-new` is used. It does not push, create a PR, deploy,
call providers, use the network, run `git fetch`, or contact GitHub.

`approve-coder-publication <publication_request_id> --decided-by <id> --note
<note>` marks that request approved and writes:

```text
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_publication/publication_decision.json
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_publication/publication_decision.md
```

The approval decision does not push, create a PR, deploy, call providers, or
use the network.

`coder-publication-handoff <coder_worktree_run_id>` requires an approved
publication request, revalidates the commit artifact hash and commit SHA, then
writes local suggested commands only:

```text
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_publication/publication_handoff.json
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_publication/publication_handoff.md
.clanker/delegations/<delegation_id>/runs/<coder_worktree_run_id>/coder_publication/publication_handoff_body.md
```

The handoff includes `git push <remote> <branch>` and a draft `gh pr create`
command with a body-file path. It does not execute either command. Manual
operator execution remains required for push or PR creation, and deploy remains
out of scope.
`record-delegation-result` remains the manual ingestion path for
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
