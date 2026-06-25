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
- `/workflow` - modern handoff/worktree/commit/publication workflow stepper,
  including `coder-prep-from-handoff` as the artifact-first prep route.
- `/projects` - registered project list.
- `/projects/<project_id>` - project detail and linked artifacts.
- `/delegations/<delegation_id>` - delegation, handoff, prep, worktree, commit,
  and publication state.
- `/runs/<run_id>` - run or coder-worktree run detail.
- `/artifacts?path=<relative_path>` - safe read-only artifact viewer.
- `/health` - Python, git, storage, command, import, route, and counter health.
- `/demo` - demo scenario instructions.

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
- a pending coder worktree approval request

It is local-only. It does not call providers, push, create PRs, deploy, use the
network, or modify external projects outside the repo demo area.

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

Large artifacts are truncated with a visible message. Artifact content is never
executed.

## Safe Actions

The first app version exposes low-risk and local artifact-producing actions
through explicit forms, including context pack generation, coder prep,
coder prep from `implementation_handoff.md`, coder-worktree plan, worktree
approval request, and publication handoff when the required approval exists.
Delegation pages also expose implementation handoff readback and link the
handoff Markdown through the safe artifact viewer.

Execution and commit actions remain CLI-first in this version. Push and PR
creation are never executed by the app.

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
