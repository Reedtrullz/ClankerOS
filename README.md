# ClankerOS

ClankerOS is a local-first agent OS harness for durable AI coding work. It
turns goals into task graphs, records evidence, keeps approval boundaries
explicit, and shows operators what is actually proven before any autonomous
capability is allowed to act.

```text
project -> goal/task -> scout delegation -> context pack -> implementation handoff
-> coder prep -> coder worktree plan -> approval -> bounded execution
-> commit request -> local commit -> publication request -> publication handoff
```

The project is intentionally conservative. It prefers local state, reportable
evidence, idempotent effects, and human approval over chat-only claims or
hidden autonomy.

## What It Does

- Tracks goals, tasks, evidence, approvals, effects, incidents, playbooks, and
  iteration packets in SQLite plus human-readable Markdown.
- Registers local git repositories and exposes `projects`, `project-status`,
  and `project-context` commands so an operator can inspect target repos before
  starting work.
- Creates durable project-scoped `goal`, `plan`, `contract`, and `tasks`
  records before execution, with versioned plan artifacts and explicit
  non-claims.
- Dispatches planned goal tasks through local profiles with `run-task`,
  records routing decisions, runs safe verifier commands, and writes evidence
  packets under `.clanker/projects/<project>/goals/<goal_id>/runs/`.
- Records retry/replan recommendations for failed planned-task runs and
  blocked planned tasks without automatically retrying, resetting, or
  dispatching work.
- Generates an operator dashboard and next-iteration packet from current local
  state.
- Starts a local-only browser operator app with `python3 -m agent_os.cli app`
  at `http://127.0.0.1:8787`, wrapping existing local state, artifacts, health,
  workflow, project, delegation/run, artifact, and demo pages.
- Runs worktree-isolated coding goals, captures diffs and verification output,
  and gates local commits behind explicit approval.
- Produces GitHub handoff packets after committed local effects, including
  exact push and draft-PR commands without taking network action itself.
- Supports safe profile routing, read-only delegation contracts, deterministic
  context packs, executable local delegation through configured shell adapters,
  project-aware repo scouting, first-class implementation handoffs, safe
  coder-prep packets, approval-gated coder worktree plans, explicit coder
  worktree approvals, bounded worktree execution with evidence, structured
  delegation-result ingestion, proposed memory, and proposed skills.
- Keeps the old capability proof ladder as advanced blocked-proof/reference
  machinery instead of the default operator path.

## Start Here

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli app
python3 -m agent_os.cli demo-app-scenario
python3 -m agent_os.cli demo
python3 -m agent_os.cli projects
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
python3 -m compileall -q agent_os tests
python3 -m agent_os.cli app-smoke-test
python3 -m agent_os.cli app-demo-smoke-test
```

`app-smoke-test` renders the core local app routes without starting a browser
server and checks each route for its expected page marker, so GitHub Actions can
catch blank or wrong operator pages before the full pytest suite finishes.
`app-demo-smoke-test` creates fixture-backed demo state and checks the
stateful goal cockpit, goal detail, demo, scoped workflow, project,
delegation, run, approvals, inbox, actions, and health pages for their
expected operator markers.

Then read:

- [Getting Started](docs/getting-started.md)
- [Suggested Use](docs/suggested-use.md)
- [Operator Recipes](docs/operator-recipes.md)
- [Local Operator App](docs/local-app.md)
- [Concepts](docs/concepts.md)
- [Architecture](docs/architecture.md)
- [Command Reference](docs/reference-commands.md)
- [Documentation Index](docs/docs-index.md)
- [First Loop Tutorial](docs/tutorial-first-loop.md)
- [First Target Repository Tutorial](docs/tutorial-first-target-repo.md)
- [Project Registry Tutorial](docs/tutorial-project-registry.md)
- [Goal Planning Lifecycle Tutorial](docs/tutorial-goal-lifecycle.md)
- [Run A Planned Task Tutorial](docs/tutorial-run-task.md)
- [Operator Daily Loop Tutorial](docs/tutorial-operator-daily-loop.md)
- [Approval-Gated Coding Tutorial](docs/tutorial-approval-gated-coding.md)
- [Executable Delegation Tutorial](docs/tutorial-executable-delegation.md)
- [Public Snapshot Tutorial](docs/tutorial-public-snapshot.md)
- [GitHub Testing](docs/github-testing.md)

The primary operator surface is now the local app plus the CLI. Start the app
for a browser view of goals, resume state, search, workspace restore, memory,
skills, profiles, projects, workflow, delegations, delegation runs, coder
runs, safe action catalog, verification handoff, dogfooding checklist, health,
artifacts, the operator inbox, approvals, incidents, and demo state:

```bash
python3 -m agent_os.cli app
```

The root `/` page is the Goal-First Home board. It starts with active,
paused, and completed goal lanes, recent activity, the operator inbox,
recommendations, incidents, saved workspace resume links, saved-goal phase and
next-action readbacks, a read-only `Home Live State` panel with five-second
local page reload polling that pauses while a form is focused or the tab is
hidden, a `Start Here` cockpit for the next click, resume
posture, blockers, and CI handoff, a `Home Day Plan` that names the current goal, phase,
one next action, waiting counts, whether end-of-day resume is ready, and a
confirmed `save-workspace` Finish Today form for the lead goal, the
read-only `Home Attention Brief` for approvals, incidents, recommendations,
inbox load, and proof posture before deeper goal work, the
`Home Focus Queue` for next actions across active and paused goals, the
read-only `Home Activity Command Bar` for the latest human-readable event,
`Home Verification Handoff` for current branch/commit GitHub Actions proof
commands and the latest operator-supplied CI evidence, the
saved-goal browser-available action form, and first-run project/goal/delegation
guidance when the checkout has not completed
its first delegation. The First Run Guide is
state-aware, and Home's live state, Start Here, Day Plan, Attention Brief, and
Focus Queue point directly to the same-page `Create Project` or `Create First
Goal` forms when no Goal exists yet. It shows the current step across create project, create first
goal, create first delegation, prepare context, and the confirmed local
`run-delegation` action with a copyable CLI fallback. It now starts with a
read-only `First Run Command Bar` that names the next first-run action, target
surface, form surface, Goal/delegation context, and zero-effect counters; after
a Goal exists it can render the same confirmed local next-action form inline,
so scout delegation, context-pack generation, and first delegation execution
can continue from the guide. Confirmed browser
project registration and goal creation also update the saved workspace, so
`/resume` already knows the first project/goal after those actions. When a
lead goal exists, Home also shows an explicit
`save-workspace` form so the operator can remember the current goal/project
context for the next session. Use the
compact local app smoke commands before pushing, then let GitHub Actions run
the fast route smoke and full pytest suite for slower proof.
The default contributor loop is intentionally GitHub-first: make a small
change, run only the narrow local check that matches it, push the PR branch,
watch `Fast smoke verification`, and let `Full pytest suite` finish in Actions.
See [GitHub Testing](docs/github-testing.md) for the exact proof boundaries and
status-recording commands.

Use `/today` as the daily command center when you want one page for the
current day instead of the full dashboard inventory. It starts with a
`Today Command Center` that chooses the lead Goal or first-run step, shows the
current phase, one primary action, the exact target or same-page action form,
attention routing for approvals/incidents/recommendations/inbox, resume
readiness, CI proof posture, a confirmed `save-goal-note` capture form for
goal-scoped operator context, a confirmed `pause-goal` form for shelving the
lead goal into paused lanes, and a confirmed `Finish Today` workspace save
form for tomorrow's resume point. A read-only `Today Live State` panel follows
with five-second local page reload polling that pauses while the tab is hidden
or a form field is focused, so the all-day cockpit can reflect changing local
goal state without adding action authority. A read-only
`Today Session Summary` then gives a return-to-work brief with current goal or
first-run step, current gate, next surface, latest activity, latest artifact,
workspace resume posture, and recorded CI proof in one scan-friendly block.
A read-only `Today Operator Workbench` follows with four obvious moves for the
day: do the current action, check timeline/evidence, clear the first blocker,
and save the resume point. A read-only `Today Workflow Map` follows with the whole first-run
path when no Goal exists, or the lead Goal's lifecycle gates when one does,
including current gate, next action, same-page action target, and gate counts.
A read-only `Today CI Handoff` follows so the daily cockpit shows the latest
operator-recorded GitHub Actions proof, whether it matches the current checkout,
the exact `gh run list` / `gh run view` commands to inspect current CI, and
links to `/verification` and `/ci-evidence` for recording proof after Actions
completes; the app still does not poll GitHub or write on GET. It also includes
a `Today Goal Queue` that lists active, paused, and completed goals with phase,
next action, switch links, same-page action availability for the lead goal,
progress, and waiting counts so daily goal switching does not require opening
the full `/goals` inventory. In an empty checkout, `/today` now points the
command center, Today Goal Queue, Start Here, and reused Home Day Plan targets
directly to the same-page `Create Project` or `Create First Goal` form instead
of sending the operator to another inventory page. It reuses the existing Home,
Goal, inbox, activity, and first-run surfaces below the command center, writes
nothing on GET, and only exposes confirmed local forms already available
elsewhere in the app.

Use `/resume` when returning to ClankerOS after a break. It reads the saved
workspace state, shows the exact saved goal/project/artifact links, preserves
filters and expanded panel readbacks, and starts with a read-only
`Resume Command Bar` that summarizes readiness, phase, current gate, next
action, target surface, action-form availability, last artifact, and
zero-effect counters. Before a saved Goal exists, `/resume` follows first-run
progress instead of stopping at the project link: an empty checkout points to
the Home `Create Project` anchor, and a registered-project/no-goal state points
to the Home `Create First Goal` anchor while still showing the saved project.
A `Resume Operator Workbench` follows it with
do/check/unblock/finish cards for the saved Goal, the current action or
same-page action form, readiness repair, blockers, last artifact, and the
existing `/workspace#save-workspace` finish surface. It also adds a `Resume
Readiness` checklist for the saved project, goal, filters, expanded panels,
last artifact existence, and next local surface, and shows a `Resume Next
Action` section with the saved goal's current phase, one next action, operator
attention cue, target surface, and the same confirmed local action form that
the Goal page would show when that next action is browser-available. When
first-run is still incomplete, the same Readiness, Next Action, and Workflow
Map sections show the current first-run gate, next setup action, and
Home/Today/Goals setup targets. It also
includes a read-only `Resume Workflow Map` that mirrors the Goal page
lifecycle rail, showing the saved goal's current gate, gate progress, next
action, and no-write/no-network boundaries before the operator leaves
`/resume`. `/workspace` shows the same
saved-goal continuation next to the editable saved-state form, adds a
read-only `Workspace Daily Brief` for morning start, continue, and finish
cues, follows with a `Workspace Operator Workbench` that gives the saved
workspace its own do/check/unblock/finish cards, same-page action-form routing,
blocker routing, last-artifact readback, and save-form target, adds a read-only
`Workspace Workflow Map` with the saved goal's current gate and gate counts,
and anchors the save form as `#save-workspace`, so operators can inspect,
update, and act from tomorrow's resume point in one place when the next action
is browser-available. Before a saved Goal exists, `/workspace` now follows the
same first-run progress as Home, Today, Goals, and `/resume`: an empty checkout
points its daily brief, workbench, continuation readback, restore links, and
workflow map at Home's `Create Project` anchor, while a registered-project/
no-goal workspace points at `Create First Goal` and keeps the saved project
visible. Both routes report that they write nothing on GET.

For the first manual browser pass, run `python3 -m agent_os.cli demo`
or `python3 -m agent_os.cli demo-app-scenario`, open `/goals`, then `/demo`,
and follow the state-aware dogfooding links
into the demo project, selected workflow, delegation, coder worktree run,
review artifact, approvals, and inbox. The `/demo` page starts with a
read-only `Demo Command Bar` that shows whether fixture state exists, the
preferred `demo` command, compatibility command, selected project, Goal,
delegation, run, next local surface, and zero-effect counters before the
longer walkthrough. It also shows a read-only `Demo Next Action` panel and
`Demo Browser Progress` checklist for the selected fixture run, so you can see
whether the app path is waiting on commit request, commit approval, local
commit, publication request, publication approval, publication handoff, or
manual push/PR outside ClankerOS. It also shows `Demo Gate Artifacts`, linking
the commit request, commit decision, local commit artifact, publication
request, publication decision, publication handoff, and PR-body artifact as
those gates become available. The `Demo Gate Actions` panel names the current
gate, the local form action, required input, expected output artifact, and
renders the safe confirmed local form when the current step can be driven from
the app. Once the publication handoff is ready, the demo keeps push/PR work
outside ClankerOS and exposes the confirmed local `complete-goal` form so the
operator can record that manual publication finished and review completed Goal
evidence.
`Manual Browser Checkpoints` lists the exact route markers to confirm across
`/demo`, `/dogfooding`, workflow, project, delegation, run, approvals, inbox,
verification, and health surfaces, then lets you jump directly to the relevant
local surface.

Use `/goals` as the daily cockpit. It separates active, paused, and completed
goals, links each goal to its detail page, and shows phase, next action, and
task progress plus open task, incident, and recommendation counts from
existing local state. A read-only `Goal Board Command Bar` starts the page
with total goal counts, the prioritized saved or active Goal, its current
phase, one next action, the target surface, waiting counts, resume link, and
zero-effect counters. The cockpit also includes a confirmed local `Start
Another Goal` form backed by the existing `create-goal` action, so an
operator can add the next goal for a registered project without switching to
the CLI.
Use `/goals/<goal_id>` as the
goal-centered workbench: the page now opens with the large Current Phase
banner immediately after the Goal summary, then shows an in-flow read-only
Goal Jump Bar for phase, action, workflow, timeline, evidence, artifacts,
notes, git, and remaining work. Its visible `1`-`9` key badges and
`aria-keyshortcuts` jump to those local anchors without submitting forms,
then a compact fixed desktop `Goal Action Dock` keeps the current action, gate,
CI proof target, and resume route visible while linking back to the existing
confirmed Goal Next Action form. The dock becomes static on narrow screens and
precedes the Goal Command Bar, Goal
Operator Workbench, Goal Daily Loop, Goal Return Brief, Goal Continuation Rail,
next action, next recommendation, Goal Workflow Map, Goal CI Handoff, live
state, and section index before the detailed progress, timeline, activity log, goal risk, completion
criteria, completion readiness, evidence, delegations, runs, approvals,
artifacts, a typed Goal Artifact Explorer, memory, skills used, git status,
operator notes, a goal-scoped resume snapshot, and remaining work. The page
auto-refreshes by local polling, pauses while the operator is editing a form or
the tab is hidden, and stays local-only. The Goal Command Bar near the top condenses
current phase, one primary action, target local surface, progress, waiting
counts, resume route, latest project-scoped CI proof state, and zero-effect
boundary so the operator can choose the next click without scrolling. Goal
Operator Workbench follows it with a human-readable do/check/unblock/finish
strip: it points at the in-page Goal action form when one is available, links
the source surface and first unblock surface, names the current gate/progress,
and exposes confirmation/write/provider/network/external-effect counters
before the deeper diagnostic sections. The Goal Next Action section now starts
with a human-first focus strip for Now, Gate, Target, and Boundary, with one
primary link to the existing confirmed form or source surface before the
diagnostic rows. Goal Daily Loop includes a confirmed
local `pause-goal` form for any non-paused incomplete goal, moving it into
paused lanes without approving work, running providers, using the network, or
mutating external systems. The read-only `Goal Continuation Rail` follows the
return brief and turns the current gate plus the next few local gates into a
short path of operator actions and surfaces, while keeping the eventual manual
publish boundary explicit. Goal
Section Index now also links directly to the Timeline, Activity, and Git
command bars, so the long Goal page can jump to the scan-first operational
panels instead of only the longer detail sections. Goal
Overview now starts with a read-only `Goal Overview Command Bar` that makes the
goal identity, status, phase, risk, progress, task/delegation/run/approval
counts, next click, and no-effect boundary visible before the raw metadata. Goal
Risk now starts with a read-only `Goal Risk Command Bar` that summarizes
risk level, task risk counts, approval-boundary posture, first task risk/status,
one next local surface, and zero-effect counters before the detailed risk
list. Goal Completion Criteria now starts with a read-only `Goal Criteria
Command Bar` that summarizes criteria source, item count, progress,
plan/contract posture, first acceptance item, one next local review surface,
and zero-effect counters before the detailed criteria list. Goal Progress now
starts with a read-only `Goal Progress Command Bar` that summarizes task
completion, workflow gate progress, current gate, waiting approvals/incidents/
recommendations, one next local action, and zero-effect counters before the
browser progress bar. Goal
Completion Readiness turns the same local gate, approval, incident, and
publication-handoff state into one explicit finish posture. It names the
current blocker or next safe action, links the relevant local surface, and only
offers the confirmed `complete-goal` form after the manual publish handoff is
ready. The Goal
Git Status section now starts with a read-only `Goal Git Command Bar` that
summarizes the registered project root, branch, commit, clean/dirty posture,
tracked and untracked counts, latest goal-linked `git_status.txt` evidence
when available, and one next local surface without fetching GitHub status or
mutating the repo. The Goal
Daily Loop turns the same local state into start/continue/unblock/finish cues:
`/resume`, the current next action, the first approval/incident/recommendation
surface, and a confirmed `save-workspace` form that records this goal and its
latest artifact as tomorrow's resume point without writing on GET. Goal Return
Brief follows it with a read-only return-to-work snapshot: current gate, next
action, resume readiness, latest activity, latest artifact, CI proof posture,
blocker route, `/resume`, and finish surface. The Goal Workflow Map
turns the same gate state used by Remaining Work into a top-level lifecycle
rail from scout delegation through manual publish, highlighting the current
gate, the next local action, every gate's eventual operator surface, and the
manual publish boundary without writing on GET. Goal CI Handoff follows the
workflow map near the top of the Goal page with project-scoped proof status,
latest operator-recorded GitHub Actions evidence, exact `gh run list` /
`gh run view` command templates, and a same-page JSON paste target for
recording proof, while still doing no GitHub polling or external mutation on
GET. Goal Remaining Work starts with a read-only `Goal Remaining Work Command Bar`
that summarizes current gate, done/pending/waiting gate counts, open
task/incident/recommendation counts, pending approvals, one next local surface,
and zero-effect boundaries before the detailed checklist. The Next Recommendation
section names whether the recommendation
comes from an open task recommendation or from current phase plus local goal
records, then points at the local target surface without writing on GET.
The in-flow Goal Jump Bar keeps the most-used in-page anchors one click or
one keypress away without covering later controls. The Goal Action Dock keeps
the current action one click away from deep scroll positions without adding a
second action form. The Goal Next Action focus strip makes the selected action
readable at the point of decision, while the Goal Section Index near the top
links to the full stable anchor map for the major Goal surfaces.
Goal Delegations starts with a read-only `Goal Delegation Command Bar` that
summarizes scout delegation counts, context-pack readiness, implementation
handoff readiness, coder-prep packets, worktree plans, the latest delegation
workflow surface, and one next local continuation before the detailed
delegation rows.
Goal Runs starts with a read-only `Goal Run Command Bar` that summarizes task
and worktree run counts, review readiness, changed-file posture, the latest
run surface, and one next local run action before the detailed run list.
Goal Approvals starts with a read-only `Goal Approval Command Bar` that
summarizes pending and approved worktree, commit, and publication gates, points
at `/approvals` or the next local Goal surface, and keeps approval decisions on
confirmed local forms instead of writing on page load.
Goal Incidents starts with a read-only `Goal Incident Command Bar` that
summarizes open/resolved incidents, open recommendations, the first incident's
severity, run, task, evidence, one triage surface, and zero-effect boundaries
before the detailed incident list.
Goal Evidence starts with a read-only `Goal Evidence Command Bar` that
summarizes run, worktree, incident, recommendation, and typed artifact
evidence counts, points at the latest bounded artifact or highest-priority
local evidence surface, and keeps provider/network/external-effect counters at
zero before the detailed evidence list.
Goal Verification Evidence starts with a read-only `Goal Verification Command
Bar` that shows whether project-scoped proof is missing, stale, job-scoped
early proof, or current full workflow success. It links to `/verification` and
`/ci-evidence`, shows whether the latest operator-supplied CI proof matches
the current checkout, and includes a confirmed Goal-scoped form for pasted
GitHub Actions JSON. The form infers run identity from `databaseId`/`url`,
validates the supplied JSON, and records local CI proof without app-side
GitHub polling.
Goal Memory starts with a read-only `Goal Memory Command Bar` that summarizes
project/global memory artifacts, project/active/proposed/global/generated entry
counts, operator-note state, future-work count, pinning posture, one next local
memory action, and zero-effect boundaries before the detailed memory readback.
Skills Used starts with a read-only `Goal Skills Command Bar` that summarizes
task skill tags, matching generated or available skill records, usage and
project counts, delegation profile usage, one `/skills` or `/profiles` review
target, and no-execution/no-install/no-network boundaries before the detailed
skill readback.
Timeline entries link back to the relevant local artifact, delegation, run,
approval queue, or goal surface, and render as scan-first event rows with
time, event-kind badge, clickable message, and target badge. The timeline also
backfills generic `Artifact recorded` events from the same bounded artifact
registry used by the Goal Artifact Explorer. The timeline starts with a
read-only `Goal Timeline Command Bar` that summarizes event-family counts, the
latest event, its target surface, and zero-effect boundaries before the full
chronological list. The Activity Log now starts with a read-only Goal Activity Command Bar
that names the latest human-readable event and target local surface before the
longer chronological list. Progress starts with a read-only Goal Progress
Command Bar, then uses a real browser progress bar.
Operator Notes starts with a read-only `Goal Operator Notes Command Bar` that
shows whether the note artifact exists, timestamped entry count, artifact size,
workspace resume-anchor posture, one review or capture target, and zero-effect
boundaries before the confirmed `save-goal-note` form. The form appends local
resume context to the goal-scoped `operator-notes.md` artifact without
overwriting earlier notes.
The Goal Resume Snapshot reads `.clanker/app/workspace.json`, shows whether
the saved workspace already points at the current goal, suggests the latest
goal artifact as the resume anchor, renders saved filters, expanded panels,
and last-viewed artifact as `Goal Workspace Restore State`, and provides a
confirmed `save-workspace` form that returns to the same goal page after
saving. It does not write on page load, fetch GitHub status, call providers,
push, create PRs, deploy, or mutate external systems.
The Goal Artifact Explorer groups goal-linked artifacts as Markdown, JSON,
Patch, or Text and links them through the bounded `/artifacts` viewer instead
of exposing raw filesystem browsing. The Goal page now starts the artifact
area with a read-only `Goal Artifact Command Bar` that summarizes artifact
record counts, available/missing posture, render-family counts, source-family
counts, the latest artifact, and one next bounded artifact review click before
the detailed artifact list and typed explorer. Each artifact page starts with
a read-only `Artifact Command Bar` showing path, type, renderer, size, line
count, truncation state, inferred project/goal context, whether it is already
the saved resume anchor, and one next action: remember it or resume from it.
Each artifact page also includes an `Artifact Review Brief` that links
goal-scoped artifacts back to their Goal and Project, or points unclassified
artifacts toward the remember/resume workspace path before the inert content
view.

Use `/goals` on a fresh checkout for first-run browser actions. The page now
renders a state-aware First Run Guide plus confirmed local forms for
`register-project` and `create-goal`, so a new operator can create a project
and first goal without switching to CLI commands. The guide tracks whether
the project, goal, first delegation, and context pack exist, then points to
the current surface, the confirmed local `run-delegation` action, or its exact
CLI fallback command. After a confirmed `register-project` action, the
`Action Result Details` page also renders a first-run continuation with an
inline confirmed `create-goal` form plus Home and Today fallback links, so the
operator can keep moving before a saved Goal exists. From the created goal
page, the Next Action card can create the first read-only scout delegation
with a confirmed `delegate` form, writing a local contract artifact without
starting a subagent or calling a provider. After the delegation exists, the
same card can generate the local context pack with a confirmed `context-pack`
form. When the context pack is ready, the card shows the exact
confirmed local `run-delegation` action while keeping the CLI command as a
fallback/readback. After a delegation has completed, the Goal Next Action
card can also create the local coder prep packet, create the approval-gated
worktree plan, and request the pending worktree approval with confirmed
browser forms. It can then approve the pending worktree request. After
approval, the Goal card exposes a confirmed `run-coder-worktree` form for one
operator-provided safe local command in the isolated worktree. The existing
approval, safe-command, verifier, and bounded-file checks still apply, and
the exact CLI fallback remains visible. Once the bounded run completes, the
Goal card can create the local review artifact for the completed coder
worktree run. Once that review gate passes, it can create the review-gated
commit request.
After that, the same Goal card can approve the commit request, create the
isolated local worktree commit, request and approve publication handoff
preparation, and write the local publication handoff/PR-body artifacts. Push
and draft PR creation remain copy-only/manual outside ClankerOS. After the
operator finishes that manual publication work, the Goal page exposes a
confirmed local `complete-goal` action that marks the Goal completed and moves
it into the completed-goals lane without pushing, creating a PR, deploying,
calling providers, or using the network.
Those steps write local artifacts, local approval rows, local approval
decisions, bounded worktree run evidence, or one isolated local worktree
commit only; they do not expose arbitrary commands, push, create PRs, deploy,
call providers, or use the network. Use Home, `/resume`, or `/workspace` to
save and restore open project, open goal, filters, expanded panels, and last
viewed artifact in `.clanker/app/workspace.json`, with saved-goal phase and
next-action readbacks on each return-to-work surface. `/workspace` now also
has a `Workspace Operator Workbench` beside the editable state form, and
`/resume` and `/workspace` both expose the saved goal's workflow gate map, so changing saved
context does not hide the current gate.
Use the goal page note form for day-to-day operator breadcrumbs, then find the
same note artifact again from `/memory`.
Use `/search` for bounded global search across indexed goals, projects,
delegations, known artifacts, incidents, recommendations, memory, runs, and
approvals. Goal search results include live local phase, one next action, and
remaining-work counts, so action or phase searches can return the Goal to
continue. The read-only `Search Command Bar` starts each search with result
counts by category, the first result to open, its target link, and the
no-write/no-network/no-raw-filesystem boundary. Use `/memory`, `/skills`, and
`/profiles` for local readbacks of memory entries, generated skills/usage,
and inactive future provider-routing lanes. The read-only `Memory Command Bar`
starts `/memory` with entry counts, proposed-memory pin posture, first target,
one next local action, saved workspace context, and no-write/provider/network/
external-effect boundaries before the longer memory lists. The read-only
`Skills Command Bar` starts `/skills` with skill record counts, generated-skill
posture, usage/project counts, the first generated or available skill artifact,
one local review target, and no execution/install/provider/network effects.
The read-only `Profiles Command Bar` starts `/profiles` with configured and
storage profile counts, future-lane readiness, adapter/write/use-for posture,
one local review target, and provider/model routing explicitly disabled.
`/profiles` also shows both `.clanker/profiles.yml` names and SQLite profile
storage rows, including labels, modes, cost tiers, write posture, adapter
status, and `use_for` labels without enabling providers.
Use `/incidents` as a read-only triage board for open incidents, resolved
incident history, and task recovery recommendations. The `Incident Triage
Command Bar` starts the page with one local review target, incident and
recommendation counts, evidence links, and no-resolution/no-retry/no-network
boundaries.

The app shell also includes a global `Operator Focus` strip, a read-only
`Route Context` breadcrumb strip, recent local items, a command palette,
keyboard shortcuts, and a dark/light theme toggle on every page. After a
confirmed local action, the shell also shows a read-only `Last Action` strip
from `.clanker/app/workspace.json`, with the action result, target notice
surface, saved Goal/project context, and zero-effect counters so the operator
can recover the last handoff after navigating away. The route
context strip shows the current route family/path, parent surface, current
Goal/Project/run context when it can be resolved, saved workspace anchors,
resume link, current focus target, and expandable zero-effect counters before
the page content. The recent-items sidebar now starts with a read-only `Recent Items
Command Bar` that names the first reopen target, counts workspace/goal/
delegation/run shortcuts, shows saved workspace context and last action,
links `/resume`, and
keeps zero-effect counters visible. The focus strip keeps the saved or lead
goal's phase, one primary action, target surface, progress, waiting counts,
and resume link visible outside the Goal page, and can expand the same
confirmed local action form when the current next action is browser-available.
Before any Goal exists, the same shared shell follows first-run progress
instead: Home, Today, and Goals point the route context, command palette, and
Operator Focus at their same-page `Create Project` or `Create First Goal`
forms, while other pages link back to those Home/Today/Goals first-run
anchors.
The command palette also opens with a route-aware `Current Page` block that
names the current path, parent surface, resolved Goal/Project/run context,
focus target, and `/resume` link before the same goal-aware
`Continue Current Goal` block, a compact Goal continuation readback for the
current gate plus the next few local gates, and the confirmed local action
form. Those controls stay inside the local browser app and do not perform
external effects.

Use `/workflow?delegation_id=<id>` or `/workflow?run_id=<coder_run_id>` when
you want the scoped operator map. The selected workflow page now includes a
read-only `Workflow Command Bar` that summarizes the selected delegation or
run, parent Goal, project, current stage, next local action, target surface,
reason, and zero-effect counters before the detailed stepper. It also includes a
read-only `Selected Workflow Continuation` block with the exact next local
action, run detail surface, approvals queue, inbox, dogfooding checklist, and
the explicit `external_effects_created: false` boundary.

Use `/runs/<coder_run_id>` to review the worktree evidence and gate state. The
read-only `Run Command Bar` starts the page with the run status, review gate,
commit/publication state, changed-file count, diff summary, next local action,
target surface, and no-write/no-network/no-push boundary. A `Run Operator
Workbench` follows it with do/check/unblock/finish cards for the same run gate,
including same-page action anchors, review/evidence links, approvals, parent
Goal, and a confirmed `save-workspace` form that stores the run and review or
evidence artifact as tomorrow's resume point without writing on GET. The `Run Review
Gate` panel shows whether `runs/<source_run_id>/review.md` exists and mentions
the coder worktree run id. The app only exposes the `coder-commit-request`
form when that gate passes. The Goal Next Action card can now create that
local review artifact with a confirmed `review-run` form when the goal is
waiting on review.

Use `/runs/<coder_run_id>` after publication handoff preparation when you want
the display-only manual publication commands. The app shows
`suggested_push_command`, `suggested_draft_pr_command`, and `pr_body_path`, but
it does not run them.

Use `/dogfooding` when you want one checklist for the first browser route walk:
refresh the fixture, inspect demo/workflow/project/delegation/run surfaces,
walk the local commit and publication gates, then hand verification to GitHub
Actions after a push. The page starts with a read-only `Dogfooding Command
Bar` that shows fixture status, selected project/Goal/delegation/run, the one
recommended next surface, route-walk/CI/action/health links, and zero-effect
counters before the longer checklist. The existing `Dogfooding Next Action`
panel then expands the fixture-backed next action and links the project,
delegation, workflow, run, approval queue, inbox, action catalog, and
verification surfaces. It also shows a copy-only `GitHub Actions Follow-up`
section with the direct snapshot handoff, `gh run view`, and
record-after-success command templates for the current checkout. The page is
read-only and does not fetch GitHub status.

Use `/delegation-runs` when you want a compact read-only index of scout
execution evidence, context packs, implementation handoffs, zero-effect
counters, retry signals, and next local operator actions before handing work to
coder prep. The page starts with a `Delegation Run Command Bar` that counts
completed/pending runs, incidents, retry candidates, context packs, and
implementation handoffs, then points at the first local delegation, run, or
workflow surface to inspect next.

Use `/projects` as the project workflow index. It shows each registered
project's root, default test command, current branch/commit, goal/task/
delegation counts, next recommended local operator action, and direct project
or selected workflow links. It also includes a confirmed local
`Register Local Project` form backed by the existing `register-project`
action, so daily project onboarding does not require switching back to the
CLI.

Use `/projects/<project_id>` as the project-level launchpad. It shows goals,
tasks, delegations, artifacts, project guidance, and a read-only
`Project Command Bar` that summarizes branch/commit, goal and queue counts,
the next project action, the target local surface, and no-write/no-network
boundaries before the longer inventory. The page also starts with a
`Project Operator Workbench` with Do Now, Goal, Unblock, and Finish Today
cards, including a confirmed `save-workspace` form so a project can become the
next resume point without leaving the browser. It also includes a confirmed
local project-scoped `create-goal` form, goal rows that link directly to
`/goals/<goal_id>` with phase, next action, and task progress, scoped workflow
links for delegations and coder runs, and links back to safe actions,
dogfooding, and verification without executing external effects.

Use `/actions` when you want a read-only catalog of available local app
actions, where their forms appear, what previous artifact they require, what
local artifact or approval they write, and the no-external-effects boundary.
The page starts with an `Action Catalog Command Bar` that summarizes total
actions, navigation actions, mutating actions, confirmation-required actions,
local execution/git/approval/artifact posture, first safe action, target
anchors, and zero provider/network/external-effect counters before the longer
catalog. It also includes an `Action Operator Workbench` that reads the same
first-run or lead-Goal focus as the rest of the app, names the current safe
local action, links the owning surface where the confirmed form already lives,
routes blockers to inbox/approvals/incidents, and exposes a confirmed
`save-workspace` finish form for returning to action context later.
When the fixture exists, `/actions` also shows `Current Demo Action Surfaces`
with links to the selected project, delegation, workflow, run, approvals, and
inbox surfaces.

Use `/approvals` when you want to keep driving the gate sequence from one
queue. The read-only `Approval Queue Command Bar` starts the page with total
pending worktree, commit, and publication decisions, the first recommended
decision, the same-page form target, the follow-up after approval, and the
zero-effect boundary. The `Approval Operator Workbench` follows it with
do/inspect/Goal/finish cards, the first pending decision, the parent Goal when
known, request and evidence artifacts, confirmation posture, and a confirmed
`save-workspace` form so an approval queue can become tomorrow's resume point
without writing on GET. The read-only `Approval Decision Brief` then expands
the first recommended decision into direct inspection links for the relevant
delegation, workflow, run when one exists, request artifact, evidence artifact,
form anchor, post-decision surface, and no-write/no-network/no-external-effect
boundary. Pending commit and publication approvals link back to the relevant
run and name the next local-only follow-up action after approval, including
the typed commit-message requirement and the manual push/PR boundary.

Use `/inbox` when you want the read-only operator queue. Pending commit and
publication items include the same run links and next-action cues, but the
actual decision forms stay on `/approvals` and the state-aware run detail
pages. The read-only `Inbox Command Bar` starts the page with the total local
queue size, counts by queue type, the first attention item, its target section,
and the no-write/no-network boundary. The `Inbox Operator Workbench` follows
it with do/inspect/Goal/finish cards for the first attention item, resolving
Goal, delegation, run, evidence, and continuation surfaces when available, and
includes a confirmed `save-workspace` form so the queue can become tomorrow's
resume point without writing on GET.

Use `/verification` when you want the local-vs-GitHub testing split in one
place. It reads the checked-in GitHub Actions workflow, lists the compact local
checks to run before a push, and states that CI proof requires a completed
passing GitHub Actions run. It also shows the configured job timeout, the
latest operator-supplied CI evidence record when one exists, and makes clear
that an in-progress GitHub run is pending proof, not CI proof, so you can wait
on GitHub instead of rerunning the full suite locally. It also shows a
copyable `ci-snapshot-handoff` template for the current checkout so you can
watch a direct pushed-snapshot run and then record it after success. The page
itself does not contact GitHub. A read-only `Verification Command Bar` now
starts the page with workflow status, latest local CI proof, whether that proof
matches the current checkout, and one target action, usually
`/ci-evidence#record-ci-snapshot-json` when proof is missing, stale, or only
job-scoped.

The root dashboard includes the same proof boundary as a compact
`Verification Snapshot`, with links to `/verification` and `/ci-evidence`, so
you can see from the first screen whether local CI proof has been recorded and
whether it came from a publication handoff or a direct pushed snapshot.
It also shows the current direct-snapshot handoff, status-check, and
record-after-success command templates without executing them.
It also includes a `Dashboard Dogfooding Snapshot` that shows whether the
fixture-backed demo state exists, the next dogfooding action, the selected
workflow/run surface when available, and the `/demo` manual browser script
link.

Use `/ci-evidence` after recording CI proof with `ci-deploy-evidence` for a
publication handoff or `ci-snapshot-evidence` for a direct operator-authorized
push. It shows operator-supplied GitHub Actions/deploy evidence already stored
in local ClankerOS state and links the inert evidence artifact. It also shows
the latest local GitHub handoff id, branch, commit, handoff evidence, and a
handoff-specific `ci-deploy-evidence` command template when a recordable
handoff exists. When no handoff exists, it shows a direct snapshot evidence
template instead. A read-only `CI Evidence Command Bar` now starts the page
with handoff/snapshot record counts, latest proof source/status/scope, current
proof posture, one next action, and same-page targets for the paste form or
recent evidence lists. In both states it also shows the direct `ci-snapshot-handoff`
template for the current checkout. A `CI Proof Workbench` follows with four
scannable cards: check the pushed run, record fast-smoke proof, record
full-suite proof, or fall back to manual record-after-success. The cards and
rows show the exact `gh run view` / validated recorder commands, link back to
the paste form, and keep fast-smoke proof labeled as early route/CLI proof
only. It does not fetch GitHub status.

The app is local-only by default, binds to `127.0.0.1`, and refuses non-local
binds unless `--allow-nonlocal-bind` is explicitly supplied. It does not push,
create PRs, deploy, call providers, or perform network actions beyond local
browser/server loopback. Confirmation pages show submitted payloads before
local writes. They now start with a read-only
`Action Confirmation Command Bar` that names the action kind, required input,
output artifact, local mutation/execution posture, and no-provider/no-network/
no-push boundaries before the final `confirm=yes` submit. Confirmed actions
return an `Action Result Details` page with the payload, result fields,
artifact links, next-page link, and safety boundary. Successful results also
show an `Action Continuation` block from the
refreshed saved goal, including current phase, one next action, target page,
and the same confirmed local action form when available. Before a saved Goal
exists, that block follows first-run progress instead and can render the
confirmed next first-run form inline, such as `create-goal` after
`register-project`. The same result page now includes an
`Action Result Workflow Map` that shows the first-run or saved-Goal gate rail,
current gate, next action, next local surface, progress counts, and explicit
manual-publish boundary after the confirmed action, without writing on GET or
adding provider, network, push, PR, or deploy authority. The workspace also
remembers that completed local action as the shell's `Last Action` strip, so
the next page and `/resume` can reopen the result notice without reading the
original action result page. Following the
next-page link renders an `Action Notice` banner on the target page so the
operator keeps context. The dashboard and `/health`
surface the same warning posture for non-local binds, dirty tracked files,
ahead-of-origin state, and known duplicate untracked files. `/health` starts
with a `Health Command Bar` that summarizes warning count, bind scope,
branch/commit, storage and workflow-import readiness, the refreshed local
status artifact, the fact that the artifact is written on GET, one next local
surface, and zero provider/network/external-effect counters. Stop it with
`Ctrl-C`.

The underlying CLI workflow remains the source of truth: scout a repo, inspect
the generated handoff, prepare a bounded coder plan from either the delegation
or the `implementation_handoff.md` artifact, propose an approval-gated
worktree plan, request explicit approval, run a bounded local command in an
isolated worktree, review evidence, request and approve a separate local
commit, create that commit only inside the isolated worktree, then request and
approve a local-only publication handoff packet with suggested push and
draft-PR commands. Once the handoff is ready, the run detail page shows the
suggested push command, draft PR command, and PR body path as copy-only
operator guidance while keeping manual push/PR outside ClankerOS.

```bash
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli context-pack <delegation_id>
python3 -m agent_os.cli run-delegation <delegation_id>
python3 -m agent_os.cli implementation-handoff <delegation_id>
python3 -m agent_os.cli coder-prep <delegation_id>
python3 -m agent_os.cli coder-prep-from-handoff <path/to/implementation_handoff.md>
python3 -m agent_os.cli coder-worktree-plan <delegation_id>
python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "Approve bounded worktree execution"
python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "Approved bounded execution"
python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify
python3 -m agent_os.cli review <coder_worktree_run_id>
python3 -m agent_os.cli coder-commit-request <coder_worktree_run_id> --requested-by operator --message "Implement bounded change from approved worktree run" --note "Request local commit after review"
python3 -m agent_os.cli approve-coder-commit <commit_request_id> --decided-by operator --note "Approved local commit"
python3 -m agent_os.cli commit-coder-worktree <coder_worktree_run_id> --message "Implement bounded change from approved worktree run"
python3 -m agent_os.cli coder-publication-request <coder_worktree_run_id> --requested-by operator --remote origin --target-branch main --note "Request publication handoff"
python3 -m agent_os.cli approve-coder-publication <publication_request_id> --decided-by operator --note "Approved publication handoff preparation"
python3 -m agent_os.cli coder-publication-handoff <coder_worktree_run_id>
python3 -m agent_os.cli review <coder_worktree_run_id>
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli inbox
```

The historical capability proof ladder remains callable and documented for
advanced blocked-proof work, but it is not the default README or CLI-help path.
Use the [Command Reference](docs/reference-commands.md#capability-activation-proof-tasks)
or [Documentation Index](docs/docs-index.md#capability-follow-up-tutorials)
when you need a specific blocked-activation rung.

Register and inspect a target repository before asking ClankerOS to touch it:

```bash
python3 -m agent_os.cli register-project my-repo --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli projects
python3 -m agent_os.cli project-status my-repo
python3 -m agent_os.cli project-context my-repo
```

Plan a registered project goal before executing work:

```bash
python3 -m agent_os.cli goal "Make the smallest verified improvement" --project my-repo
python3 -m agent_os.cli plan <goal_id>
python3 -m agent_os.cli contract <goal_id>
python3 -m agent_os.cli tasks <goal_id>
```

This writes versioned local artifacts under
`.clanker/projects/<project>/goals/<goal_id>/`. It does not execute tasks,
commit, push, deploy, or call model providers.

Execute one planned task only after the plan and sprint contract are clear:

```bash
python3 -m agent_os.cli run-task <task_id> --profile tester
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli evidence <run_id>
python3 -m agent_os.cli task-recommendations --goal <goal_id>
python3 -m agent_os.cli dashboard
```

`run-task` is profile-gated. `tester` can only run the registered project
default test command; `coder` can run safe local verifier commands. The command
creates a local run and evidence packet, but it does not commit, push, deploy,
start a model provider, or start a subagent.

`evidence <run_id>` adds the replayable operator packet under
`.clanker/projects/<project>/goals/<goal_id>/runs/<run_id>/evidence/` and
prints the `packet_dir`. If the run already has command-proof files from
`run-task`, ClankerOS preserves them and writes aggregate review sidecars.
The packet also includes `git_status.txt`, `diff.patch`, and
`changed_files.json` for the selected evidence target: the registered project
repo when the run belongs to one, otherwise the ClankerOS system root. These
files are local snapshots only; export does not fetch, pull, commit, push, or
mutate the repo.

If a planned task verifier fails, ClankerOS opens a local incident and records
an open `failed_run_task_recovery` recommendation with review, replan, and
manual rerun guidance. If a planned task is blocked, `task-recommendations`
records `blocked_planned_task_replan` guidance. These records are local
operator guidance only; `/incidents` does not retry, resolve, or change task
status by itself.

Run a read-only delegation through a configured local shell adapter when you
want a replaceable specialist executor:

```bash
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli context-pack <delegation_id> --max-files 12 --max-snippets 8
python3 -m agent_os.cli profile-adapter scout --command "python3 .clanker/adapters/fake_scout.py" --input-mode json_file --output-mode json --timeout-seconds 120
python3 -m agent_os.cli run-delegation <delegation_id>
python3 -m agent_os.cli delegation-result <delegation_id>
python3 -m agent_os.cli implementation-handoff <delegation_id>
python3 -m agent_os.cli coder-prep <delegation_id>
python3 -m agent_os.cli coder-worktree-plan <delegation_id>
python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "Approve bounded worktree execution"
python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "Approved bounded execution"
python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli dashboard
```

`run-delegation` is provider-agnostic. ClankerOS owns the durable state,
prompt/context bundle, evidence packet, schema validation, and incident
handling; the configured adapter is only a local executor. There are no
built-in OpenAI, Anthropic, Codex, OpenCode, Hermes, Aider, or MCP provider
integrations yet. Subagent profiles remain read-only by default and cannot be
used by ClankerOS to commit, push, approve, deploy, or mutate external systems.
When the parent task belongs to a registered project, `context-pack` writes
ranked files, grep hits, snippets, test hints, entrypoint hints, config hints,
and non-claims under `.clanker/delegations/<delegation_id>/context/`.
`run-delegation` auto-generates that pack if it is missing, copies it into the
run evidence packet, and passes compact `context_pack` metadata to the adapter.
Successful executable delegations also write compact implementation handoff
artifacts in the run evidence packet. These handoffs point at the context pack,
returned files, validation status, and relevant test hints without embedding
the large snippets:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.json
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.md
```

Use `implementation-handoff <delegation_id>` to parse that handoff directly.
It prints readability, schema/kind, context-pack validation, scout returned
files, top ranked files, test hints, and whether snippets were embedded.
Use `coder-prep <delegation_id>` when an operator wants to turn the handoff
into a bounded future coding plan before editing anything. It consumes
`implementation_handoff.md`, writes `coder_prep.json` and `coder_prep.md`
under the delegation run, and prints zero-effect counters for task rows, runs,
routing decisions, worktrees, approvals, source edits, command reruns, network
actions, and external mutations.
Use `coder-worktree-plan <delegation_id>` after reviewing the prep packet. It
consumes `coder_prep.md`, writes `coder_worktree_plan.json` and
`coder_worktree_plan.md` beside it, proposes a bounded future worktree/run
shape, and keeps `dispatch_ready=false` with no worktree, approval request, run,
task, effect, command rerun, source edit, network action, provider call, commit,
push, deploy, or external mutation.
Use `coder-worktree-approval <delegation_id>` to request the explicit operator
gate for that exact plan hash. It writes `coder_worktree_approval_request.json`
and `.md` beside the plan and still creates no worktree, runs no command, and
edits no source.
Use `approve-coder-worktree <approval_id>` to mark that local approval request
approved. It writes `coder_worktree_approval_decision.json` and `.md`, but it
still does not create a worktree or run commands.
Only `run-coder-worktree <delegation_id> --command "<safe local cmd>" --verify`
can create the isolated worktree. It requires an approved matching plan hash,
runs the operator-provided safe local command in that worktree, captures stdout,
stderr, verification output, git status, diff, changed files, and bounded-file
validation under `.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/`.
It blocks if changed files are outside `allowed_files`. It does not commit,
push, deploy, call providers, or intentionally use the network.
After a successful run, use `review <coder_worktree_run_id>` before requesting
local commit promotion. `coder-commit-request <coder_worktree_run_id>` requires
completed bounded worktree evidence, a clean verification result, current
changes still inside `allowed_files`, a readable worktree, and an explicit
commit message. It writes `coder_commit/coder_commit_request.json` and `.md`
without staging or committing. `approve-coder-commit <commit_request_id>`
records the operator decision in `coder_commit/coder_commit_decision.json` and
`.md` without staging or committing. Only
`commit-coder-worktree <coder_worktree_run_id>` may stage the reviewed allowed
files and create one local commit in the isolated worktree branch. It re-checks
the source run hash, branch/HEAD, current changed files, outside files,
message, and verifier state, then writes `coder_commit/commit.json`,
`pre_commit_status.txt`, `post_commit_status.txt`, `committed_diff.patch`, and
`committed_files.json`. After the local commit exists, use
`coder-publication-request <coder_worktree_run_id>` to request the next
boundary. `approve-coder-publication <publication_request_id>` records the
operator decision without pushing or creating a PR.
`coder-publication-handoff <coder_worktree_run_id>` writes
`coder_publication/publication_handoff.json`, a Markdown handoff, and a PR body
draft at `coder_publication/pr_body.md` with suggested `git push` and draft
`gh pr create` commands. It does not execute those commands, contact GitHub,
push, create a PR, deploy, call providers, or mutate external systems.
Add `--working-directory project_root` when configuring the adapter if the
local executor should run from the target repository instead of the ClankerOS
system root.
For the full walkthrough, see
[Executable Delegation](docs/tutorial-executable-delegation.md).

## Primary Operator Surface

| Need | Command |
| --- | --- |
| Initialize local state | `python3 -m agent_os.cli init` |
| See current operator state | `python3 -m agent_os.cli dashboard` |
| Select the next narrow slice | `python3 -m agent_os.cli iterate` |
| Register a local git repo | `python3 -m agent_os.cli register-project <name> --path <path>` |
| Create planning state | `goal`, `plan`, `contract`, `tasks` |
| Run one planned task | `python3 -m agent_os.cli run-task <task_id> --profile tester` |
| Configure delegation adapter | `python3 -m agent_os.cli profile-adapter scout --command "python3 .clanker/adapters/fake_scout.py"` |
| Configure project-root scout adapter | `python3 -m agent_os.cli profile-adapter scout --command "python3 /path/to/scout.py" --working-directory project_root` |
| Generate scout context | `python3 -m agent_os.cli context-pack <delegation_id>` |
| Run read-only delegation | `python3 -m agent_os.cli run-delegation <delegation_id>` |
| Inspect implementation handoff | `python3 -m agent_os.cli implementation-handoff <delegation_id>` |
| Prepare bounded coder plan | `python3 -m agent_os.cli coder-prep <delegation_id>` |
| Prepare approval-gated worktree plan | `python3 -m agent_os.cli coder-worktree-plan <delegation_id>` |
| Request coder worktree approval | `python3 -m agent_os.cli coder-worktree-approval <delegation_id> --requested-by operator --note "..."` |
| Approve coder worktree execution | `python3 -m agent_os.cli approve-coder-worktree <approval_id> --decided-by operator --note "..."` |
| Run approved bounded worktree command | `python3 -m agent_os.cli run-coder-worktree <delegation_id> --command "python3 scripts/local_change.py" --verify` |
| Request local commit from reviewed worktree | `python3 -m agent_os.cli coder-commit-request <coder_worktree_run_id> --requested-by operator --message "..." --note "..."` |
| Approve local commit request | `python3 -m agent_os.cli approve-coder-commit <commit_request_id> --decided-by operator --note "..."` |
| Create local worktree commit | `python3 -m agent_os.cli commit-coder-worktree <coder_worktree_run_id> --message "..."` |
| Request publication handoff | `python3 -m agent_os.cli coder-publication-request <coder_worktree_run_id> --requested-by operator --remote origin --target-branch main --note "..."` |
| Approve publication handoff | `python3 -m agent_os.cli approve-coder-publication <publication_request_id> --decided-by operator --note "..."` |
| Write publication handoff | `python3 -m agent_os.cli coder-publication-handoff <coder_worktree_run_id>` |
| Review evidence | `review`, `evidence`, `replay-summary` |
| Inspect approvals | `python3 -m agent_os.cli approvals` |
| Inspect operator queue | `python3 -m agent_os.cli inbox` |

For common workflows, use [Operator Recipes](docs/operator-recipes.md). For
legacy proof-ladder and advanced report-only commands, use
[Command Reference](docs/reference-commands.md).

## Executable Delegation

The current delegation loop can execute a pending read-only delegation through
a locally configured shell adapter. The adapter receives a scoped
prompt/context bundle, returns a JSON result envelope, and ClankerOS validates
the output against the delegation schema before marking the delegation
completed.

For registered-project tasks, `input.json` includes a `project` object with
the registered root path, default test command, and allowed write roots; a
`repo_scouting` object with a capped git file inventory; and a `context_pack`
object pointing at the evidence-local `context_pack.json` and
`context_pack.md`.

`context-pack` is the deterministic scout preflight. It extracts technical
terms from the goal, task, delegation prompt, and schema; ranks repository
files with explainable scores; records capped grep hits and snippets; skips
ignored and secret-like paths; and writes:

```text
.clanker/delegations/<delegation_id>/context/context_pack.json
.clanker/delegations/<delegation_id>/context/context_pack.md
```

During `run-delegation`, those files are copied into:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/context_pack.json
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/context_pack.md
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.json
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/implementation_handoff.md
```

`delegation-result`, `implementation-handoff <delegation_id>`,
`coder-prep <delegation_id>`, `coder-worktree-plan <delegation_id>`,
`coder-worktree-approval <delegation_id>`, `approve-coder-worktree <approval_id>`,
`run-coder-worktree <delegation_id>`, `review <run_id>`, `inbox`, and `dashboard`
surface the context-pack path, returned-file inventory validation, missing
returned files, and implementation handoff health so a later implementation
pass can start from paths and metadata instead of pasted snippets. `review`
writes `## Implementation Handoff`, `## Coder Prep`, and
`## Coder Worktree Plan`, `## Coder Worktree Approval`, and
`## Coder Worktree Run` sections, and the dashboard writes
`### Implementation Handoffs`, `### Coder Prep Packets`, and
`### Coder Worktree Plans`, `### Coder Worktree Approvals`, and
`### Approved Coder Worktree Runs`.

`coder-prep` is artifact-only and idempotent for the same handoff hash. It
does not create task rows, dispatch runs, rerun commands, edit source files,
create worktrees, request approvals, commit, push, deploy, call providers, or
mutate external systems.
`coder-worktree-plan` is also artifact-only and idempotent for the same
`coder_prep.md` hash. It proposes a branch/path and future explicit
`run-goal --isolation worktree` command, but it does not create the worktree,
run the command, request approval, edit files, commit, push, deploy, call
providers, or mutate external systems.
`coder-worktree-approval` is idempotent for the same plan hash unless
`--force-new` is used. `approve-coder-worktree` tolerates already-approved
requests and prints `already_approved`. `run-coder-worktree` refuses to run
without an approved matching plan hash and does not rerun a completed
approval/plan pair unless `--rerun` is provided.

Adapters run from the ClankerOS root by default; configure
`--working-directory project_root` to let a scout read repo files with relative
paths.

Malformed JSON, schema-invalid output, non-zero exits, timeouts, and unsafe
adapter commands fail safely with local incidents and evidence packets under:

```text
.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/
```

This is the first executable delegation primitive, not a general provider
integration layer. Adapter commands are configured locally per profile, and
ClankerOS records that network/provider actions taken by the adapter are
unknown unless the adapter itself proves otherwise.

## Current Shape

ClankerOS is a Python CLI with a local SQLite control plane, generated Markdown
reports, JSON artifacts, pytest coverage, eval/playbook checks, and bootstrap
project memory. The first milestone is the closed loop:

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
```

The current control plane's primary operator path is implementation handoff:
`run-delegation` writes context and handoff evidence, `implementation-handoff`
reads it back, `coder-prep` writes a bounded future coding plan, and
`coder-worktree-plan` writes an approval-gated future worktree plan.
`coder-worktree-approval`, `approve-coder-worktree`, and `run-coder-worktree`
then provide the first explicit bounded worktree execution gate with local
evidence but no automatic commit, push, deploy, provider call, or network
action. A reviewed successful coder worktree run can then move through the
separate local-only gate `coder-commit-request -> approve-coder-commit ->
commit-coder-worktree -> coder-publication-request ->
approve-coder-publication -> coder-publication-handoff`; commit approval
remains separate from execution approval, publication approval remains separate
from commit approval, and the publication handoff remains separate from manual
push/PR execution.
Executable local slices still exist where the verifier is explicit (`run-goal`,
`run-task`, `run-delegation`, `run-coder-worktree`). The older report-only
proof ladders remain available as
advanced blocked-proof machinery, and every activation step still preserves
`activation_allowed=false`, `capability_enabled=false`,
`approval_requests_created=0`, `activation_actions_taken=0`, and
`external_mutations_taken=0` unless a future approved capability boundary
changes that contract.

For the detailed state, use:

- [Operator Dashboard](docs/dashboard.md)
- [Next Iteration Packet](docs/next-iteration.md)
- [Operating Summary](docs/OPERATING_SUMMARY.md)
- [Generated Evidence Reports](docs/docs-index.md#generated-evidence-reports)
- [Status Log](status.md)
- [Bootstrap Handoff](projects/bootstrap/handoff.md)

## Key Files

- `agent_os/cli.py` - command entrypoint.
- `agent_os/storage.py` - SQLite schema and persistence layer.
- `agent_os/dashboard.py` - generated operator dashboard.
- `agent_os/iteration.py` - next-iteration packet generator.
- `docs/OPERATING_SUMMARY.md` - current architecture and proof state.
- `docs/dashboard.md` - generated operator cockpit.
- `docs/next-iteration.md` - generated next work packet.
- `tasks.md` - human-readable momentum queue.
- `status.md` - chronological implementation evidence.
- `projects/bootstrap/` - bootstrap project continuity notes.

## Public Snapshot Checklist

Before pushing a public snapshot, run a fast local slice:

```bash
git status --short --branch
git diff --check
python3 -m compileall -q agent_os tests
python3 -m agent_os.cli app-smoke-test
python3 -m agent_os.cli app-demo-smoke-test
python3 -m pytest tests/test_first_milestone.py -q -k "github_actions or ci_snapshot or local_app or inbox"
```

After pushing or opening a PR, wait for the GitHub `Tests` workflow to run the
fast smoke job first, then the dependent full-suite job with
`python -m pytest -q`. The smoke job is early route/CLI proof only; a committed
workflow file is not CI proof until GitHub Actions passes on that commit.
While the run is pending, generate a pasteable watch/record handoff without
contacting GitHub from ClankerOS:

```bash
python3 -m agent_os.cli ci-snapshot-handoff --project clankeros --branch main --commit <commit_sha> --external-run-id <run_id> --repo Reedtrullz/ClankerOS
```

The local app mirrors this on `/`, `/verification`, and `/ci-evidence` as a
template-only operator surface. The app never runs the `gh run view` command;
it only shows what the operator can run outside ClankerOS after a push. On
`/ci-evidence`, the `CI Proof Workbench` turns the same flow into four browser
cards for checking status, recording fast-smoke proof, recording full-suite
proof, or manually recording an already-known successful run.

Prefer the validated record path after GitHub completes:

```bash
gh run view <run_id> --repo Reedtrullz/ClankerOS --json status,conclusion,headSha,headBranch,databaseId,url,jobs \
| python3 -m agent_os.cli ci-snapshot-evidence-from-gh-json --project clankeros --branch main --commit <commit_sha> --status-json -
```

If the fast smoke job is green but the full suite is still running, record
scoped smoke proof from the same JSON instead:

```bash
gh run view <run_id> --repo Reedtrullz/ClankerOS --json status,conclusion,headSha,headBranch,databaseId,url,jobs \
| python3 -m agent_os.cli ci-snapshot-evidence-from-gh-json --project clankeros --branch main --commit <commit_sha> --status-json - --job-name "Fast smoke verification"
```

That smoke record is early route/CLI proof, not full-suite proof.

That command consumes GitHub status JSON from stdin, infers the run id and URL
from `databaseId`/`url`, refuses pending/failed or
wrong-commit runs, and records local proof only after the status JSON matches.
The `/ci-evidence` page offers the same validated recorder as a confirmed
local form for pasted `gh run view` JSON; the app still never contacts GitHub
and still requires operator confirmation before writing local proof.

For direct pushes, record the completed run locally with
`python3 -m agent_os.cli ci-snapshot-evidence --project clankeros --branch main --commit <commit_sha> --provider github-actions --status success --external-run-id <run_id> --url <run_url>`.
Pushing is not deployment. GitHub metadata readback is not runtime proof. See
[GitHub Testing](docs/github-testing.md) and
[Tutorial: Public Snapshot](docs/tutorial-public-snapshot.md) for the full
recommended flow.

## Non-Claims

This repository does not yet claim hosted dashboard availability, remote worker
execution, autonomous scheduling, browser/desktop adapter readiness, live
CI/deploy proof, built-in model provider integrations, budget enforcement,
trust promotion, automatic retries, automatic memory activation, automatic
skill activation, or real cost tracking. Shell adapters are local configured
executors; ClankerOS records `provider_calls_taken_by_clankeros=0` and
`external_mutations_taken=0`, but adapter network/provider behavior is unknown
unless the adapter writes evidence proving otherwise. Those surfaces remain
blocked until their evidence and approval contracts are satisfied.

## GitHub About

Suggested repository description:

```text
Local-first agent OS harness for durable AI coding: task graphs, executable delegation, verification evidence, and approval gates.
```

Suggested topics:

```text
agent-operating-system, agent-os, ai-agents, agentic-ai, coding-agents, agent-orchestration, subagent-delegation, executable-delegation, local-first, human-in-the-loop, approval-workflow, verification, evidence, task-graph, operator-dashboard, worktrees, sqlite, python, cli-tool, developer-tools
```
