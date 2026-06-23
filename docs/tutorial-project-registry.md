# Tutorial: Register And Inspect Projects

Use this tutorial when you want ClankerOS to know about a local git repository
before running agentic work against it. The goal is a durable project record
plus a read-only context packet that an operator can inspect later.

## 1. Initialize Local State

```bash
python3 -m agent_os.cli init
```

This creates or migrates `.agent/state.db`. It does not start a service, call a
model provider, create a worktree, push, deploy, or schedule background work.

## 2. Register A Git Repository

```bash
python3 -m agent_os.cli register-project my-repo \
  --path /path/to/repo \
  --test-command "python3 -m pytest -q"
```

Registration validates that the path exists and resolves to a git repository.
Allowed write roots default to the git root and must stay inside that root.

The command writes:

- a `registered_projects` row in SQLite;
- `projects/my-repo/project.md` for human continuity.

## 3. List Registered Projects

```bash
python3 -m agent_os.cli projects
```

Expected shape:

```text
projects: 1
my-repo status=registered root_path=/path/to/repo test="python3 -m pytest -q" ...
```

This is the quickest check before choosing a target project for work.

## 4. Inspect Project Status

```bash
python3 -m agent_os.cli project-status my-repo
```

This prints the registered root, local branch readbacks, remote URL if locally
configured, default test command, allowed write roots, memory path, skills
path, evidence root, and non-claim counters.

`project-status` does not run tests, create a worktree, approve effects,
commit, push, deploy, or call model providers.

## 5. Write A Context Packet

```bash
python3 -m agent_os.cli project-context my-repo
```

This writes:

```text
projects/my-repo/context.md
```

Use that file as the project handoff before starting a goal. It names the
target repository, the default verifier, the safe write boundary, and the next
operator commands to consider.

## 6. Continue Into A Goal

After the context looks right, choose a narrow goal:

```bash
python3 -m agent_os.cli run-goal \
  "Make the smallest verified change" \
  --project my-repo \
  --isolation worktree \
  --command "<safe local command>"
```

Then inspect evidence and approvals before any commit:

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli approvals
```

## Non-Claims

- Project registration does not prove the default test command passes.
- Project status does not contact GitHub, CI, or deployment systems.
- Project context generation does not run tests or execute agent work.
- These commands do not enable hosted dashboards, remote workers,
  autonomous scheduling, browser/desktop adapters, budget enforcement, trust
  promotion, automatic retries, or real cost tracking.
