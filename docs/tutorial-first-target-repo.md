# Tutorial: First Target Repository

Use this tutorial when you want ClankerOS to help with a real local git
repository while keeping the work visible and approval-bounded.

## 1. Initialize ClankerOS

```bash
python3 -m agent_os.cli init
```

This creates or migrates `.agent/state.db` for local control-plane state.

## 2. Register The Repository

```bash
python3 -m agent_os.cli register-project my-repo \
  --path /absolute/path/to/repo \
  --test-command "python3 -m pytest -q"
```

Pick a test command that is safe to run repeatedly and actually proves the
kind of change you expect to make.

## 3. Inspect What ClankerOS Knows

```bash
python3 -m agent_os.cli projects
python3 -m agent_os.cli project-status my-repo
python3 -m agent_os.cli project-context my-repo
```

Read `projects/my-repo/context.md`. It records the git root, branch, remote,
default verifier, allowed write roots, and non-claims.

## 4. Create A Planning Packet

```bash
python3 -m agent_os.cli goal "Make one small verified improvement" --project my-repo
python3 -m agent_os.cli plan goal_...
python3 -m agent_os.cli contract goal_...
python3 -m agent_os.cli tasks goal_...
```

Read the generated artifacts under
`.clanker/projects/my-repo/goals/goal_.../`. If the plan is wrong, replan
before running a task.

## 5. Optional: Scout Relevant Files

Before executing a planned task, use a read-only scout delegation when you want
an adapter to inspect the target repo and return relevant files:

```bash
python3 -m agent_os.cli delegate task_... --profile scout --title "Find relevant files"
python3 -m agent_os.cli profile-adapter scout \
  --command "python3 /absolute/path/to/project_scout.py" \
  --input-mode json_file \
  --output-mode json \
  --working-directory project_root \
  --timeout-seconds 120
python3 -m agent_os.cli run-delegation subagent_delegation_...
```

The scout receives registered project metadata and `repo_scouting.files` in
`input.json`. With `--working-directory project_root`, the adapter can read the
target repo using relative paths, while ClankerOS still records schema
validation, stdout/stderr, `project.json`, `repo_files.json`, and the usual
non-claims in the delegation evidence packet.

## 6. Run One Task

```bash
python3 -m agent_os.cli run-task task_... --profile tester
python3 -m agent_os.cli review run_...
python3 -m agent_os.cli task-recommendations --goal goal_...
python3 -m agent_os.cli dashboard
```

Run one task at a time. The useful habit is: choose a small task, run it,
inspect the evidence packet, then decide the next step from the dashboard.

## 7. Commit Only After Coherent Verification

```bash
git status --short --branch
git diff --check
python3 -m pytest -q
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Commit when the diff, reports, and tests all describe one coherent increment.
Push only after the target remote and branch are explicit.

## What This Tutorial Does Not Do

- It does not deploy anything.
- It does not open a pull request.
- It does not start remote workers or subagents.
- It does not call model providers.
- It does not approve risky work.
- It does not claim CI proof unless CI was actually checked.
