# Local Operator App

ClankerOS now includes a local-only browser app for dogfooding the modern
operator workflow without replacing the CLI.

## Launch

```bash
python3 -m agent_os.cli app
```

The default bind is:

```text
http://127.0.0.1:8787
```

Aliases:

```bash
python3 -m agent_os.cli local-app
python3 -m agent_os.cli serve
```

Useful options:

```bash
python3 -m agent_os.cli app --port 8788
python3 -m agent_os.cli app --host 127.0.0.1 --port 8787
```

Non-local binds are refused unless explicitly opted in:

```bash
python3 -m agent_os.cli app --host 0.0.0.0 --allow-nonlocal-bind
```

## Pages

- `/` - local operator dashboard.
- `/` includes a confirmed `refresh-dashboard-state` action that rewrites the
  local `.clanker/app/local_app_status.json` artifact from current repository
  and route state without providers, pushes, PRs, deploys, or external
  mutations.
- `/workflow` - modern handoff/worktree/commit/publication workflow stepper,
  including `coder-prep-from-handoff` as the artifact-first prep route. Add
  `?delegation_id=<id>` or `?run_id=<coder_worktree_run_id>` to show selected
  workflow state, artifact status, approval/run/commit/publication status, and
  the next recommended local operator action. When a delegation or run is
  selected, each related workflow step also shows a `selected_status` token so
  the stepper itself can be scanned as the operator state map.
- `/projects` - registered project list.
- `/projects/<project_id>` - project detail with first-class project goals,
  goal-linked tasks, linked artifacts, project-scoped incidents/
  recommendations, and next recommended operator action.
- `/delegations/<delegation_id>` - delegation, handoff, prep, worktree, commit,
  and publication state, including a compact workflow-readiness summary and
  next recommended operator action.
- `/runs/<run_id>` - run or coder-worktree run detail, including a
  `Run Workflow State` block for upstream context-pack, handoff, prep, plan,
  approval/run, bounded validation, commit, publication, and next-action
  status when the run is a coder worktree run.
- `/inbox` - read-only operator queue for steering reviews, approval requests,
  incidents, delegations, coder runs, commits, and publication handoffs.
- `/approvals` - pending worktree, commit, and publication approvals.
- `/incidents` - recent local incidents and evidence links.
- `/artifacts?path=<relative_path>` - safe read-only artifact viewer.
- `/health` - Python, git, storage, command, import, route, and counter health.
- `/demo` - demo scenario instructions plus state-aware dogfooding links after
  `demo-app-scenario` has created fixture state.

## Demo Scenario

```bash
python3 -m agent_os.cli demo-app-scenario
```

Alias:

```bash
python3 -m agent_os.cli app-demo
```

The demo creates fixture-backed local state under `.clanker/demo/`:

- a registered `local-app-demo` project
- a goal and task
- a completed fixture-backed scout delegation
- context-pack and implementation-handoff artifacts
- coder prep and coder worktree plan packets
- a pending coder worktree approval for inbox/approval dogfooding
- an approved fixture-backed coder worktree execution
- a completed bounded coder worktree run with changed-file, diff, git-status,
  bounded-validation, stdout/stderr, verification, and review artifacts

It is local-only. It does not call providers, push, create PRs, deploy, use the
network, or modify external projects outside the repo demo area.

After running the demo command, open `/demo` in the local app. It reads the
current fixture state and links directly to the demo project, selected
workflow, delegation, coder worktree run, review artifact, inbox, approvals,
and health page. The same page includes a manual browser script for the first
dogfooding pass through commit request, commit approval, typed local commit,
publication request, publication approval, and publication handoff.

## Artifact Viewer

The artifact viewer accepts only relative paths under the ClankerOS repo root.
It rejects absolute paths, `..`, and paths that resolve outside the root.
Supported inert render types are:

- `.md`
- `.json`
- `.txt`
- `.patch`
- `.diff`
- `.log`

Large artifacts are truncated with a visible message. The page shows the
inert render type (`markdown`, `json`, `text`, `patch`, `diff`, or `log`) plus
file size and truncation status. Artifact content is never executed.

## Safe Actions

The first app version exposes low-risk and local artifact-producing actions
through explicit forms, including context pack generation, coder prep,
coder prep from `implementation_handoff.md`, coder-worktree plan, worktree
approval request, commit request, publication request, approval decisions, and
publication handoff when the required approval exists. The dashboard also
exposes a confirmed `refresh-dashboard-state` form for rewriting only the
local app status artifact. Delegation pages also expose implementation handoff
readback and link the handoff Markdown through the safe artifact viewer.

Run pages for completed coder worktree runs link the local review, `run.json`,
`diff.patch`, `changed_files.json`, `bounded_file_validation.json`,
`git_status.txt`, stdout/stderr, and verification output before showing
state-aware forms. The initial reviewed run page exposes a commit-request form
only. `commit-coder-worktree` appears only after commit approval and is still
an explicit confirmed local action with a typed commit message that must match
the approved request. Publication request appears only after the isolated local
commit is recorded, and publication handoff appears only after publication
approval. The commit action creates a commit only inside the isolated coder
worktree after the existing commit gate re-checks review, source hashes,
branch/HEAD, changed files, bounded-file validation, and verifier state.

The `/inbox`, `/approvals`, and `/incidents` pages are local operator surfaces.
The inbox is read-only and mirrors the CLI's operator-worthy queue without
starting work, approving requests, retrying tasks, committing, pushing, creating
PRs, deploying, calling providers, or using external network actions.

Worktree execution remains CLI-first outside the fixture-backed demo setup.
Push and PR creation are never executed by the app.

## Health Artifact

Visiting `/health` or starting the app writes:

```text
.clanker/app/local_app_status.json
```

The status artifact records host, port, repo root, branch, commit,
dirty/untracked summaries, routes, supported workflow stages, non-claims, and
known gaps. It does not include secrets.

## Stop The App

Stop the foreground server with `Ctrl-C` in the terminal that launched it.

## Non-Claims

- The app does not replace the CLI.
- The app does not push.
- The app does not create PRs.
- The app does not deploy.
- The app does not call model providers.
- The app does not perform network actions beyond local browser/server
  loopback.
- The app does not execute arbitrary commands.
- The app does not expose remote workers, hosted dashboards, schedulers,
  browser/desktop adapters, CI/deploy automation, or provider integrations.
