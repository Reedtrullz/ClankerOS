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

- `/` - Goal-First Home dashboard. It starts with active, paused, and
  completed goal lanes, recent activity, the operator inbox, open
  recommendations, open incidents, saved workspace resume links, an explicit
  `save-workspace` form for the current lead goal when one exists, and
  first-run project/goal forms when no goals exist.
- `/` includes a confirmed `refresh-dashboard-state` action that rewrites the
  local `.clanker/app/local_app_status.json` artifact from current repository
  and route state without providers, pushes, PRs, deploys, or external
  mutations.
- `/` also includes a read-only state-aware `Next Recommended Action` panel
  that points to the highest-priority local operator surface, such as
  incidents, approvals, a reviewed coder run needing a commit request, a
  publication handoff, project state, or the demo/onboarding page.
- `/` also includes a read-only `Verification Snapshot` that summarizes the
  checked-in workflow timeout, latest operator-supplied CI evidence when one
  exists, and links to `/verification` plus `/ci-evidence` without polling
  GitHub status.
- `/` also includes a read-only `Goal Snapshot` that links to `/goals`, counts
  active/paused/completed goals, and names the lead goal phase plus next
  action when goal state exists.
- `/goals` - daily goal cockpit. It separates active, paused, and completed
  goals, links to each goal detail page, and keeps phase, next action, task
  progress, and first-run browser actions visible. The page exposes confirmed
  local `register-project` and `create-goal` forms for a fresh checkout.
- `/goals/<goal_id>` - goal-centered workbench with current phase, next action,
  overview, goal risk, completion criteria, progress, chronological timeline,
  activity log, delegations, runs, approvals, evidence, artifacts, memory,
  skills used, git status, operator notes, a goal-scoped resume snapshot, and
  remaining work. It uses local polling refresh and does not contact GitHub or
  providers. The Current Phase banner is the primary operator state readback:
  it shows the large phase label, reason, operator attention cue, next surface,
  latest activity, and zero-effect boundary so the operator knows what is
  happening without opening the CLI. Skills Used links to `/skills`, shows
  task skill usage counts,
  projects using each tag, matching generated or available skill records when
  present, and profile usage while keeping skill execution out of the Goal
  page. Goal Resume Snapshot reads `.clanker/app/workspace.json`, shows
  whether the saved workspace already points at the current goal, suggests the
  latest goal artifact as the resume anchor, renders saved filters, expanded
  panels, and last-viewed artifact as `Goal Workspace Restore State`, and
  exposes a confirmed `save-workspace` form that returns to the same goal page
  after saving without writing on GET. Operator Notes includes a confirmed
  `save-goal-note` form that appends local resume context to
  `.clanker/projects/<project>/goals/<goal>/operator-notes.md`; it does not
  overwrite previous notes. When the goal has planned tasks but no
  delegation yet, the Next Action card exposes a confirmed `delegate` form
  that writes a read-only scout delegation contract without starting a
  subagent. After that, the same Next Action card exposes a confirmed
  `context-pack` form while the delegation has no context pack. Once the
  context pack exists, the card shows the exact `run-delegation` CLI handoff
  and makes clear that browser adapter execution is not exposed yet. After a
  delegation completes, the card exposes confirmed `coder-prep`,
  `coder-worktree-plan`, and `coder-worktree-approval` forms at the matching
  workflow phases. It also exposes confirmed `approve-coder-worktree` and
  then a copy-only `run-coder-worktree` handoff once the worktree request is
  approved. The handoff names the approved plan, allowed-file preview,
  verifier, expected evidence path, and return route while keeping browser-side
  worktree execution unexposed. The Goal card exposes `review-run` when the
  completed coder worktree run is blocked on the review gate, then
  `coder-commit-request` once the review exists and mentions the coder run.
  Once a commit request exists, the same Goal card can drive
  `approve-coder-commit`, `commit-coder-worktree`,
  `coder-publication-request`, `approve-coder-publication`, and
  `coder-publication-handoff` through confirmed local forms, then shows the
  manual publish boundary and copy-only publication handoff commands. These
  create local artifacts, approval rows, approval decisions, or one isolated
  local worktree commit only; they do not run delegations or worktrees from
  the browser, push, create PRs, deploy, call providers, or perform external
  mutations.
- Every app page includes a shared operator shell with breadcrumbs, recent
  local items, a command palette, a dark/light theme toggle, and keyboard
  shortcuts for home, goals, and palette search. These controls only navigate
  local routes or submit existing local forms.
- `/search` - bounded global search over indexed goals, projects, delegations,
  known artifacts, incidents, recommendations, memory, runs, approvals, and
  skill records. It does not expose arbitrary filesystem browsing.
- `/workspace` - persistent local workspace state for open project, open goal,
  filters, expanded panels, and last viewed artifact. Home reads the same
  saved state for daily resume links. The confirmed `save-workspace` form
  writes `.clanker/app/workspace.json`.
- `/memory` - project memories, global memories, generated memories, operator
  notes, future-work recommendations, and confirmed `pin-memory` actions.
- `/skills` - available/generated skill records with usage count, last-used
  readback, and projects using them.
- `/profiles` - inactive future provider-routing surface. It reads
  `.clanker/profiles.yml` when present and keeps provider calls at zero.
- `/workflow` - modern handoff/worktree/commit/publication workflow stepper,
  including `coder-prep-from-handoff` as the artifact-first prep route. Add
  `?delegation_id=<id>` or `?run_id=<coder_worktree_run_id>` to show selected
  workflow state, artifact status, approval/run/commit/publication status, and
  the next recommended local operator action. When a delegation or run is
  selected, each related workflow step also shows a `selected_status` token so
  the stepper itself can be scanned as the operator state map. Scoped workflow
  pages also render `Selected Workflow Continuation`, a read-only set of
  continuation links to the run detail, approvals queue, inbox, and dogfooding
  checklist with `external_effects_created: false`.
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
  after a push without fetching GitHub status. It includes a copy-only
  `GitHub Actions Follow-up` section with direct snapshot
  `ci-snapshot-handoff`, `gh run view`, and `ci-snapshot-evidence`
  record-after-success templates for the current checkout.
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
  status. Once a publication handoff is ready, the page also shows display-only
  suggested push and draft-PR commands plus the PR body path; those commands
  remain manual actions outside ClankerOS.
- Coder worktree run rows in the app include `changed_files_count` and a
  compact `diff_summary` read from existing `diff.patch` evidence, so the
  operator can scan change size without opening the artifact first.
- `/goals/<goal_id>` also includes a typed `Goal Artifact Explorer`. It groups
  goal-linked Markdown, JSON, Patch/Diff, and Text/Log artifacts and links each
  item through `/artifacts?path=...`; it does not expose raw filesystem
  browsing.
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
  fixture state. The demo page also includes `Demo Gate Artifacts`, a
  read-only artifact map for the selected fixture run's commit request,
  commit decision, local commit, publication request, publication decision,
  publication handoff, and PR-body artifacts as they become available. `Demo
  Gate Actions` names the current local gate, the form action, required input,
  expected output artifact, and renders the safe confirmed local form for that
  gate when one exists. `Manual Browser Checkpoints` lists route markers for
  the first visual pass.

## Demo Scenario

```bash
python3 -m agent_os.cli demo-app-scenario
```

Alias:

```bash
python3 -m agent_os.cli app-demo
python3 -m agent_os.cli demo
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

After running the demo command, open `/goals`, then `/demo` in the local app.
`/goals` shows the fixture goal phase and next action, while `/demo` reads the
current fixture state and links directly to the demo project, selected
workflow, delegation, coder worktree run, review artifact, inbox, approvals,
and health page. The same page includes a manual browser script for the first
dogfooding pass through commit request, commit approval, typed local commit,
publication request, publication approval, and publication handoff. The
`Demo Next Action` panel and `Demo Browser Progress` section read existing
local commit/publication records for the selected fixture run. Together they
show the current status for commit request, commit approval, local commit,
publication request, publication approval, publication handoff, and the final
manual push/PR boundary outside ClankerOS, while linking back to the relevant
local workflow, run, approvals, and inbox surfaces. `Demo Gate Actions`
renders the active local gate form, such as `coder-commit-request`,
`approve-coder-commit`, `commit-coder-worktree`,
`coder-publication-request`, `approve-coder-publication`, or
`coder-publication-handoff`; every write still goes through the normal
confirmation page and existing local safety checks. `Manual Browser
Checkpoints` lists the route markers to confirm during the first visual pass,
including demo, dogfooding, project, delegation, scoped workflow, run,
approvals, inbox, verification, and health pages.

After publication handoff preparation, return to `/runs/<coder_run_id>` to see
`Publication Handoff Commands`: the suggested push command, draft PR command,
PR body path, and zero-effect counters. This is a copy-only operator readback;
the app does not run the commands.

## Verification Handoff

`/verification` is a local read-only testing map. It reads
`.github/workflows/tests.yml`, shows whether push-to-main, pull-request, and
manual workflow triggers are configured, lists the separate fast smoke and
full-suite GitHub Actions jobs, and keeps the compact local checks visible. It
also shows the workflow job timeout, summarizes the latest operator-supplied
CI evidence record when one exists, and labels an in-progress GitHub run as
pending proof rather than CI proof:

- `python3 -m py_compile agent_os/local_app.py tests/test_first_milestone.py`
- focused local app pytest slices
- `python3 -m agent_os.cli app-smoke-test`
- `python3 -m agent_os.cli app-demo-smoke-test`
- `git diff --check`

`app-smoke-test` is route-marker aware: it renders the core local app routes
without starting a server, checks each route for its expected page marker, and
prints `marker=matched` or `marker=missing` beside the route status. The
checked-in GitHub Actions workflow runs the same smoke command before the full
pytest suite.

`app-demo-smoke-test` is the fixture-backed companion. It creates or refreshes
the local demo scenario, renders the goal cockpit, goal detail, global search,
workspace, memory, skills, profiles, selected project, delegation, scoped
workflow, coder run, approvals, inbox, actions, and health pages, and checks
state-specific snippets without starting a server or taking network/external
actions. The GitHub fast smoke job runs it before the full suite.

The page does not fetch GitHub status. The fast smoke job can prove route and
CLI wiring before the full suite finishes, but a pushed commit is not CI proof
until the GitHub Actions run completes successfully. If a GitHub run is still
in progress, keep waiting on GitHub instead of rerunning the full suite
locally; if it fails or reaches the timeout, inspect the failed job log and
fix that specific CI issue. If no CI evidence has been recorded locally, the
page shows `ci-deploy-evidence` and `ci-snapshot-evidence` command templates
instead of pretending CI proof exists. Use `ci-snapshot-handoff` from the CLI
while a direct pushed-snapshot run is pending to print the exact `gh run view`
plus `ci-snapshot-evidence-from-gh-json` commands without fetching GitHub
status or writing local proof. The validated recorder consumes operator-supplied
GitHub status JSON from stdin or a file, refuses pending/failed or wrong-commit
runs, and then writes the same local direct-snapshot proof record. The root
dashboard, `/verification`, and `/ci-evidence` also show the direct snapshot
handoff, status-check, JSON-validated record, and manual record-after-success
command templates from current local branch/commit state when available; those
lines are display-only and are never executed by the app.
The root dashboard mirrors this boundary as a compact `Verification Snapshot`
with `/verification` and `/ci-evidence` links, and it labels the latest
operator-supplied source as either `publication_handoff` or
`direct_public_snapshot` while still avoiding GitHub status polling. The same
first screen now includes a `Dashboard Dogfooding
Snapshot` with fixture availability, the next dogfooding action, selected
workflow/run links when available, and the `/demo` manual browser script
surface.

`/ci-evidence` is the read-only companion for proof that has already been
recorded locally with `ci-deploy-evidence` or `ci-snapshot-evidence`. It shows
the provider, status, external run id, external URL, commit, recorded-by field,
and evidence artifact link for recent CI/deploy evidence records. Handoff
records keep the GitHub handoff id; direct snapshot records are labeled
`direct_public_snapshot` so they do not pretend to come from a publication
handoff. The `CI Evidence Recording Guide` shows a handoff-specific
`ci-deploy-evidence` command when a local GitHub handoff exists, and a direct
`ci-snapshot-handoff`, `ci-snapshot-evidence-from-gh-json`, and manual
`ci-snapshot-evidence` command template when the operator is recording a
direct pushed snapshot. The page also has a confirmed
`ci-snapshot-evidence-from-gh-json` form where the operator can paste
`gh run view` JSON and optionally enter a completed job name such as
`Fast smoke verification`. The app records local proof only after it validates
the supplied status, conclusion, commit SHA, branch, and, when scoped, the
named job status. Job-scoped fast-smoke evidence is early route/CLI proof, not
full-suite proof. The page does not poll GitHub, refresh statuses, push,
create PRs, deploy, call providers, or mutate external systems.

## Manual Dogfooding Checklist

`/dogfooding` is the first-stop browser checklist for a compact local pass
before pushing. It shows whether the fixture-backed `local-app-demo` state is
available, points to `/demo`, `/workflow`, `/projects`, `/delegation-runs`,
`/inbox`, `/approvals`, `/actions`, and `/verification`, and names the local
commit/publication gate sequence to walk from the selected `/runs/<run_id>`
page.

The page also includes `Dogfooding Next Action`, a read-only state panel that
names the current fixture-backed next action and links the selected project,
delegation, scoped workflow, coder run, approval queue, inbox, action catalog,
and verification surfaces. The page reports zero app network actions, zero
external mutations, zero provider calls, no GitHub status fetch, and the
manual push/PR boundary outside ClankerOS.

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
rewriting only the local app status artifact. Goal pages expose
`save-goal-note` for appending goal-scoped operator notes, and the Memory page
indexes those note artifacts for later resume. Delegation pages also expose
implementation handoff readback and link the handoff Markdown through the safe
artifact viewer. When fixture state exists, `/actions` includes
`Current Demo Action Surfaces`, a read-only map from the selected demo project
and run to the current workflow, action form, approvals, and inbox surfaces.
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
state-aware forms. `Run Review Gate` mirrors the backend commit-request rule:
`runs/<source_run_id>/review.md` must exist and mention the coder worktree run
id before the app exposes `coder-commit-request`. If the review artifact is
missing or stale, the run page shows the blocked reason and hides the commit
request form. The Goal Next Action card exposes a confirmed `review-run` form
for that missing/stale review gate and writes the same local review artifact
without approving, committing, pushing, creating PRs, deploying, calling
providers, or using the network. `commit-coder-worktree` appears only after
commit approval and
is still an explicit confirmed local action with a typed commit message that
must match the approved request. Publication request appears only after the
isolated local commit is recorded, and publication handoff appears only after
publication approval. The commit action creates a commit only inside the
isolated coder worktree after the existing commit gate re-checks review,
source hashes, branch/HEAD, changed files, bounded-file validation, and
verifier state.

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
