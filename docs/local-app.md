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
- `/` also includes a read-only state-aware `Next Recommended Action` panel
  that points to the highest-priority local operator surface, such as
  incidents, approvals, a reviewed coder run needing a commit request, a
  publication handoff, project state, or the demo/onboarding page.
- `/workflow` - modern handoff/worktree/commit/publication workflow stepper,
  including `coder-prep-from-handoff` as the artifact-first prep route. Add
  `?delegation_id=<id>` or `?run_id=<coder_worktree_run_id>` to show selected
  workflow state, artifact status, approval/run/commit/publication status, and
  the next recommended local operator action. When a delegation or run is
  selected, each related workflow step also shows a `selected_status` token so
  the stepper itself can be scanned as the operator state map.
- `/actions` - read-only safe action catalog showing local app actions, where
  their forms appear, required previous artifacts, output artifacts,
  confirmation requirements, local mutation posture, and external-effect
  boundary. It also includes the confirmed dashboard status refresh form.
- `/verification` - read-only verification handoff showing the checked-in
  GitHub Actions workflow posture, compact local checks, remote full-suite
  boundary, and explicit CI non-claims without contacting GitHub.
- `/ci-evidence` - read-only CI/deploy evidence records that were already
  supplied by the operator with `ci-deploy-evidence`, including provider,
  status, external run id, URL, commit, and safe artifact links without
  fetching GitHub status.
- `/dogfooding` - read-only manual browser checklist for refreshing the demo
  fixture, walking demo/workflow/project/delegation/run routes, using local
  commit and publication gates, and handing full-suite proof to GitHub Actions
  after a push without fetching GitHub status.
- `/projects` - read-only project workflow index with root path, default test
  command, current branch/commit, goal/task/delegation counts, next
  recommended local operator action, project detail links, and selected
  delegation/run workflow shortcuts.
- `/projects/<project_id>` - project detail with first-class project goals,
  goal-linked tasks, linked artifacts, project-scoped incidents/
  recommendations, next recommended operator action, and a project workflow
  launchpad that links the project to selected delegation/run workflow views,
  the safe action catalog, dogfooding checklist, and verification handoff.
- `/delegation-runs` - read-only delegation execution run index with evidence
  directories, result artifacts, context-pack and implementation-handoff links,
  zero-effect counters, retry signals, and next recommended local operator
  actions.
- `/delegations/<delegation_id>` - delegation, handoff, prep, worktree, commit,
  and publication state, including a compact workflow-readiness summary and
  next recommended operator action.
- `/runs/<run_id>` - run detail. For delegation execution run ids, the page
  shows scout evidence, result artifacts, context-pack and
  implementation-handoff links, zero-effect counters, retry signals, and next
  local operator action. For coder worktree run ids, it includes a
  `Run Workflow State` block for upstream context-pack, handoff, prep, plan,
  approval/run, bounded validation, commit, publication, and next-action
  status.
- Coder worktree run rows in the app include `changed_files_count` and a
  compact `diff_summary` read from existing `diff.patch` evidence, so the
  operator can scan change size without opening the artifact first.
- `/inbox` - read-only operator queue for steering reviews, approval requests,
  incidents, delegations, coder runs, commits, and publication handoffs.
  Pending commit and publication rows include run links, approval-queue links,
  and next-action cues without exposing decision forms on the inbox page.
- `/approvals` - pending worktree, commit, and publication approvals. Commit
  and publication rows link back to the relevant run and show the next
  local-only follow-up action after approval.
- `/incidents` - recent local incidents and evidence links.
- `/artifacts?path=<relative_path>` - safe read-only artifact viewer.
- `/health` - Python, git, storage, command, import, route, and counter health.
- `/demo` - demo scenario instructions plus state-aware dogfooding links and a
  read-only browser-progress checklist after `demo-app-scenario` has created
  fixture state.

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
publication request, publication approval, and publication handoff. The
`Demo Browser Progress` section reads existing local commit/publication
records for the selected fixture run and shows the current status for commit
request, commit approval, local commit, publication request, publication
approval, publication handoff, and the final manual push/PR boundary outside
ClankerOS.

## Verification Handoff

`/verification` is a local read-only testing map. It reads
`.github/workflows/tests.yml`, shows whether push-to-main, pull-request, and
manual workflow triggers are configured, lists the GitHub Actions steps, and
keeps the compact local checks visible. It also shows the workflow job timeout
and labels an in-progress GitHub run as pending proof rather than CI proof:

- `python3 -m py_compile agent_os/local_app.py tests/test_first_milestone.py`
- focused local app pytest slices
- `python3 -m agent_os.cli app-smoke-test`
- `git diff --check`

The page does not fetch GitHub status. A pushed commit is not CI proof until
the GitHub Actions run completes successfully. If a GitHub run is still in
progress, keep waiting on GitHub instead of rerunning the full suite locally;
if it fails or reaches the timeout, inspect the failed job log and fix that
specific CI issue.

`/ci-evidence` is the read-only companion for proof that has already been
recorded locally with `ci-deploy-evidence`. It shows the provider, status,
external run id, external URL, handoff id, commit, recorded-by field, and
evidence artifact link for recent CI/deploy evidence records. The page does
not poll GitHub, refresh statuses, push, create PRs, deploy, call providers, or
mutate external systems.

## Manual Dogfooding Checklist

`/dogfooding` is the first-stop browser checklist for a compact local pass
before pushing. It shows whether the fixture-backed `local-app-demo` state is
available, points to `/demo`, `/workflow`, `/projects`, `/delegation-runs`,
`/inbox`, `/approvals`, `/actions`, and `/verification`, and names the local
commit/publication gate sequence to walk from the selected `/runs/<run_id>`
page.

The page is read-only. It reports zero app network actions, zero external
mutations, zero provider calls, no GitHub status fetch, and the manual
push/PR boundary outside ClankerOS.

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

The `/actions` page is the first-stop safe action catalog. It maps low-risk and
local artifact-producing actions to the page where each form appears, the
required previous artifact, the output artifact, whether confirmation is
required, and the no-external-effects boundary. The app exposes these actions
through explicit forms, including context pack generation, coder prep, coder
prep from `implementation_handoff.md`, coder-worktree plan, worktree approval
request, commit request, publication request, approval decisions, and
publication handoff when the required approval exists. The dashboard and
`/actions` page also expose a confirmed `refresh-dashboard-state` form for
rewriting only the local app status artifact. Delegation pages also expose
implementation handoff readback and link the handoff Markdown through the safe
artifact viewer.
The `/approvals` page is the gate queue for pending local decisions. Pending
commit approvals now show the relevant run link, the `commit-coder-worktree`
follow-up, and the typed commit-message requirement. Pending publication
approvals show the relevant run link and the `coder-publication-handoff`
follow-up while preserving the explicit `push_created=false`,
`pr_created=false`, and `deploy_created=false` boundary.
The `/inbox` page keeps the same commit/publication continuation cues in a
read-only queue form: it links to the run and approval queue and names the next
action after approval, but it does not render the approval decision forms.
Confirmation pages show the submitted action payload as visible read-only
fields plus the safety boundary before resubmitting with `confirm=yes`, so the
operator can review exactly what will be written before a local artifact or
approval action runs. Confirmed actions render `Action Result Details` with the
attempted action, submitted payload, result fields, artifact links when paths
are returned, a next-page link, and the safety boundary, so the operator can
review what was written before continuing. Following that next-page link
renders an `Action Notice` banner on the target GET page, preserving the action
result context while the operator reviews the dashboard, run, delegation, or
approval surface. Failed actions render `Action Error Details` with the
attempted action, error, submitted payload, and a clear no-action-completed
message so operators can fix inputs without guessing what happened.

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

The `/delegation-runs`, `/inbox`, `/approvals`, and `/incidents` pages are
local operator surfaces. The delegation run index and inbox are read-only and
mirror operator-worthy queue and execution evidence without starting work,
approving requests, retrying tasks, committing, pushing, creating PRs,
deploying, calling providers, or using external network actions.

Worktree execution remains CLI-first outside the fixture-backed demo setup.
Push and PR creation are never executed by the app.

## Health Artifact

Visiting `/health` or starting the app writes:

```text
.clanker/app/local_app_status.json
```

The status artifact records host, port, repo root, branch, commit,
dirty/untracked summaries, warning readbacks, routes, supported workflow
stages, non-claims, and known gaps. `/health` renders the same warnings for
non-local binds, dirty tracked files, ahead-of-origin state, and known
duplicate untracked files. The artifact does not include secrets.

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
