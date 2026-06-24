# Operator Recipes

Use these recipes when you know the kind of work you want ClankerOS to make
visible. Each recipe ends with evidence and an explicit boundary.

## Return To A Workspace

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli inbox
python3 -m agent_os.cli next-action bootstrap
python3 -m agent_os.cli iterate
```

Use this when you are resuming after time away. Read `docs/dashboard.md` and
`docs/next-iteration.md` before asking for another implementation pass.

Boundary: these commands inspect and generate local state. They do not execute
tasks, approve work, commit, push, deploy, or call providers.

## Start Work On A Target Repo

```bash
python3 -m agent_os.cli register-project my-repo \
  --path /absolute/path/to/repo \
  --test-command "python3 -m pytest -q"
python3 -m agent_os.cli project-status my-repo
python3 -m agent_os.cli project-context my-repo
```

Use this before coding. The project context packet is the source of truth for
what ClankerOS currently knows about the repository.

Boundary: registration and context are local evidence. They do not mutate the
target repository beyond the project notes ClankerOS writes in this checkout.

## Plan Before Executing

```bash
python3 -m agent_os.cli goal "Make one small verified improvement" --project my-repo
python3 -m agent_os.cli plan goal_...
python3 -m agent_os.cli contract goal_...
python3 -m agent_os.cli tasks goal_...
```

Use this when scope matters. Read the generated `GOAL.md`, `PLAN.md`,
`CONTRACT.md`, and `TASKS.md` under `.clanker/projects/my-repo/goals/`.

Boundary: planned tasks are not proof that work happened. They remain local
planning state until a runner or operator advances one task.

## Run One Planned Task

```bash
python3 -m agent_os.cli run-task task_... --profile tester
python3 -m agent_os.cli review run_...
python3 -m agent_os.cli evidence run_...
python3 -m agent_os.cli dashboard
```

Use this for narrow verification work. Prefer `tester` when the task verifier
is exactly the registered project test command. Prefer `coder` only for safe
local verifier commands already captured in the task contract.

Boundary: `run-task` records local verifier evidence. It does not commit,
push, deploy, open PRs, start subagents, or call model providers.

## Capture Specialist Input Without Execution

```bash
python3 -m agent_os.cli route --category repo_search --project my-repo
python3 -m agent_os.cli delegate task_... --profile scout --title "Find relevant files"
python3 -m agent_os.cli record-delegation-result subagent_delegation_... \
  --summary "Relevant files identified." \
  --output-json '{"files":["agent_os/cli.py"],"findings":["CLI parser lives in agent_os/cli.py."],"relevant_files":["agent_os/cli.py"]}'
```

Use this when you want structured specialist-style context in the control
plane without starting an external worker.

Boundary: delegation records and results are local artifacts. They do not
start subagents, call model providers, approve work, or write target files.

## Run A Local Delegation Adapter

```bash
python3 -m agent_os.cli delegate task_... --profile scout --title "Find relevant files"
python3 -m agent_os.cli profile-adapter scout \
  --command "python3 .clanker/adapters/fake_scout.py" \
  --input-mode json_file \
  --output-mode json \
  --timeout-seconds 120
python3 -m agent_os.cli run-delegation subagent_delegation_...
python3 -m agent_os.cli delegation-result subagent_delegation_...
python3 -m agent_os.cli inbox
python3 -m agent_os.cli dashboard
```

Use this when a read-only specialist should be executed by a locally configured
shell adapter. The adapter must return a JSON envelope with `result_summary`
and `structured_output`.

Boundary: ClankerOS records durable state, evidence, validation, and incidents.
It does not provide built-in model-provider integrations, and adapter network
behavior is unknown unless the adapter writes evidence proving otherwise.

## Prepare A Worktree Plan From Scout Evidence

```bash
python3 -m agent_os.cli implementation-handoff subagent_delegation_...
python3 -m agent_os.cli coder-prep subagent_delegation_...
python3 -m agent_os.cli coder-worktree-plan subagent_delegation_...
python3 -m agent_os.cli review run_...
python3 -m agent_os.cli dashboard
```

Use this after a read-only scout delegation has produced a readable
implementation handoff and you want a bounded coding plan before any
implementation run. The sequence consumes `implementation_handoff.md`, then
`coder_prep.md`, and leaves JSON/Markdown packets under the delegation run.

Boundary: this recipe prepares operator-review artifacts only. It does not
create a worktree, dispatch a task, request approval, run commands, edit
source, commit, push, deploy, call providers, or mutate external systems.

## Approve And Run A Bounded Coder Worktree

```bash
python3 -m agent_os.cli coder-worktree-approval subagent_delegation_... \
  --requested-by operator \
  --note "Approve bounded worktree execution"
python3 -m agent_os.cli approve-coder-worktree coder_worktree_approval_... \
  --decided-by operator \
  --note "Approved bounded execution"
python3 -m agent_os.cli run-coder-worktree subagent_delegation_... \
  --command "python3 scripts/local_change.py" \
  --verify
python3 -m agent_os.cli review run_...
python3 -m agent_os.cli dashboard
```

Use this only after `coder-worktree-plan` has produced a bounded plan with
allowed files you are willing to authorize. The approval request is tied to
the current plan hash, and `run-coder-worktree` refuses to run if the plan
changes after approval.

Boundary: approval request and approval decision still do not create a
worktree or run commands. `run-coder-worktree` creates a local isolated
worktree and runs the explicitly provided safe local command, then writes
stdout, stderr, verification output, git status, diff, changed files, and
bounded-file validation. It does not commit, push, deploy, call providers, or
intentionally use the network. Any changed file outside `allowed_files` blocks
the run for operator review.

## Promote A Reviewed Coder Worktree Commit

```bash
python3 -m agent_os.cli review run_...
python3 -m agent_os.cli coder-worktree-commit-approval run_... \
  --requested-by operator \
  --note "Promote reviewed coder worktree run"
python3 -m agent_os.cli approve-coder-worktree-commit coder_worktree_commit_approval_... \
  --decided-by operator \
  --note "Approved local commit promotion"
python3 -m agent_os.cli promote-coder-worktree-commit coder_worktree_commit_approval_... \
  --committed-by operator
python3 -m agent_os.cli dashboard
```

Use this only after the completed coder worktree run has been reviewed and the
diff is acceptable. The approval request is tied to the reviewed run evidence
and current diff hash. Promotion re-checks HEAD, diff, changed files, and the
recorded verifier before creating one local commit in the isolated worktree
branch.

Boundary: request and approval do not commit. Promotion creates no push, PR,
deploy, provider call, network action, merge into the original checkout, or
external mutation.

## Review Latest Capability Result Without Activation

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide \
  --operator-id operator \
  --selected-action accept_keep_blocked \
  --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task result-effect task proof-plan result and kept capability activation blocked." \
  --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
python3 -m agent_os.cli dashboard
```

Use this after the latest downstream result-effect task result-effect task
result-effect task result-effect task result-effect task result-effect task
result-effect task result-effect task result records exist and the operator
wants to preserve the proof-plan output without unblocking activation.

Boundary: this records a local operator decision only. It does not create
approval rows, enable capabilities, satisfy proof, start subagents, call model
providers, run CI, deploy, or mutate external systems.

## Publish A Coherent Snapshot

```bash
git status --short --branch
git diff --check
python3 -m pytest -q
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
gh repo view Reedtrullz/ClankerOS --json description,repositoryTopics,homepageUrl
```

Commit only a coherent verified increment. Push only after you know the target
remote and branch.

Boundary: local verification is not CI proof. Pushing to GitHub is not
deployment. GitHub metadata readback is not runtime proof.
