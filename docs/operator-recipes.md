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
  --output-json '{"files":["agent_os/cli.py"]}'
```

Use this when you want structured specialist-style context in the control
plane without starting an external worker.

Boundary: delegation records and results are local artifacts. They do not
start subagents, call model providers, approve work, or write target files.

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
