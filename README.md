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
python3 -m agent_os.cli demo
python3 -m agent_os.cli demo-app-scenario
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
for a browser view of goals, suggested-use guidance, resume state, search,
workspace restore, memory, skills, profiles, projects, workflow, delegations,
delegation runs, coder runs, safe action catalog, verification handoff,
dogfooding checklist, health, artifacts, the operator inbox, approvals,
incidents, and demo state:

```bash
python3 -m agent_os.cli app
```

Saved workspace panels are also treated as return-to-work context. When
`.clanker/app/workspace.json` contains `expanded_panels`, `/resume`,
`/workspace`, and the saved Goal page show a `Workspace Panel Restore` strip
with direct panel links; the saved Goal page browser-locally reopens matching
details panels without writing state, calling providers, or using the network.

The root `/` page is the Goal-First Home board. It now leads with the actual
Home operating surface before the shared route/focus diagnostics, and keeps
Home state plus board evidence collapsed by default. The `Home Operator Board`
shows visible Do Now, Attention, Resume, and Proof cards for the lead Goal or
first-run step, routing browser-available work to existing confirmed forms,
lead-goal approval attention to `/approvals?goal_id=<goal_id>`, unfinished
resume state to the Home Finish Today anchor, and proof review to the local CI
evidence surfaces. Home also includes a scan-first `Home Goal Board` with
active, paused, and completed lanes, a browser-local Find box, lane buttons,
live match count, first-match jump, no-match empty state, visible View status,
reload persistence in `localStorage:clankeros-home-goal-board-view`, and reset
coverage in `/workspace#workspace-view-memory`. It also includes
recent activity, the operator inbox, recommendations, incidents, saved
workspace resume links, saved-goal phase and next-action readbacks, a read-only
`Home Live State` panel with five-second local page reload polling that pauses
while a form is focused or the tab is hidden, a `Start Here` cockpit for the
next click, resume posture, blockers, and CI handoff, a `Home Day Plan` that names the current goal, phase,
one next action, waiting counts, whether end-of-day resume is ready, and a
confirmed `save-workspace` Finish Today form for the lead goal, the
read-only `Home Attention Brief` with visible Now, Inbox, Approvals,
Incidents, Recommendations, and Proof cards before deeper goal work, the
`Home Focus Queue` for next actions across active and paused goals, the
read-only `Home Activity Command Bar` with visible Latest, Goals, Artifacts,
and Notes cards for recent human-readable activity,
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
can continue from the guide. The command bar is followed by a visible
`First Run Launchpad` with five browser choices: continue guided setup, open a
populated demo, inspect workflow, review verification proof, or check health
and safety. A visible `First Run Next Step` panel follows with one primary
same-page action, setup/handoff/resume/safety cards, confirmation posture, and
zero-effect counters, making the current click obvious before the checklist.
A visible `First Run Action Ladder` then turns Project, Goal, Delegation,
Context, and Run into five action cards with the current action highlighted,
the exact browser target, the CLI/action name evidence, and the same
zero-effect safety counters. A visible `First Run Empty State Map` now renders a text-only
`Project -> Goal -> Delegation -> Context -> Run` illustration with step cards,
so a blank checkout shows a path instead of just empty inventories. A
browser-local `First Run Checklist` then lets the operator mark setup checks
and keep a short return note in `localStorage:clankeros-first-run-checklist`;
the real step state still comes from ClankerOS progress and GET rendering
stays read-only. A visible `First Run Progress` strip follows with a progress
bar and five step
cards for Project, Goal, Delegation, Context, and Run, while detailed status
evidence stays collapsed and read-only. Active first-run Goal pages also show
a read-only `Goal First Run Rail` between Attention and the Goal Command Bar,
so the same Project -> Goal -> Delegation -> Context -> Run path stays visible
and routes the current step to the existing confirmed Goal action form.
Confirmed browser
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
current day instead of the full dashboard inventory. It is content-first and
command-center-first: the shared route/focus diagnostics are pushed below the
daily cockpit, the visible opening is a six-card `Today Command Center`, and
state/command/workbench evidence stays collapsed until explicitly opened. The
command center chooses the lead Goal or first-run step, shows the current
phase, one primary action, the exact target or same-page action form,
attention routing for approvals/incidents/recommendations/inbox, resume
readiness, and CI proof posture. Note capture, pause, and `Finish Today`
workspace save forms are also collapsed by default and open from the visible
cards or direct hash links, preserving confirmed local writes without making
the first screen feel like a report. A read-only `Today Live State` panel follows
with five-second local page reload polling that pauses while the tab is hidden
or a form field is focused, so the all-day cockpit can reflect changing local
goal state without adding action authority. A read-only
`Today Session Summary` then gives a return-to-work brief with visible
Continue, Latest, Proof, and Resume cards before the detailed readback. The
cards point at the current goal or first-run step, latest activity, recorded
CI proof, and workspace resume posture so the operator can act from the brief
without reading the whole evidence table. A read-only `Today Activity Digest`
follows with Now, Window, Artifacts, Notes, and Safety cards plus a compact
recent timeline list for the lead Goal or current first-run step, so the daily
cockpit carries enough context to regain the thread without opening the full
Goal timeline.
A read-only `Today Operator Workbench` follows with four obvious moves for the
day: do the current action, check timeline/evidence, clear the first blocker,
and save the resume point. A read-only `Today Decision Queue` then turns the
lead Goal or first-run state into exact daily rows: current action first, then
pending approvals, incidents, recommendations, or blocked work, all linked to
existing confirmed action forms or scoped review surfaces. A browser-local
`Today Decision Filter` narrows those already-rendered rows by lane or text,
restores lane/query from `localStorage:clankeros-today-decision-filter`, and
can be reset from `/workspace#workspace-view-memory`. A read-only `Today
Workflow Map` follows with the whole first-run path when no Goal exists, or the
lead Goal's lifecycle gates when one does, including current gate, next action,
same-page action target, and gate counts.
A read-only `Today CI Handoff` follows so the daily cockpit shows the latest
operator-recorded GitHub Actions proof, whether it matches the current checkout,
the exact `gh run list` / `gh run view` commands to inspect current CI, and
links to `/verification` and `/ci-evidence` for recording proof after Actions
completes; the app still does not poll GitHub or write on GET. It also includes
a `Today Goal Queue` that lists active, paused, and completed goals with phase,
next action, switch links, same-page action availability for the lead goal,
progress, and waiting counts so daily goal switching does not require opening
the full `/goals` inventory. The queue has a browser-local Find box, All /
Active / Paused / Completed lane buttons, live match count, first-match link,
no-match state, visible View status, and reload persistence via
`localStorage:clankeros-today-goal-queue-view`; it can be reset from
`/workspace#workspace-view-memory` without server writes. In an empty
checkout, `/today` now points the command center, Today Goal Queue, Start
Here, and reused Home Day Plan targets directly to the same-page
`Create Project` or `Create First Goal` form instead of sending the operator
to another inventory page. It reuses the existing Home,
Goal, inbox, activity, and first-run surfaces below the command center, writes
nothing on GET, and only exposes confirmed local forms already available
elsewhere in the app.

Use `/guide` as the in-app `Suggested Use Guide` when you want the operator
loop in browser form. It maps `Today -> Goal -> Action -> Proof -> Finish ->
Resume`: start in `/today`, choose or create the Goal through the Home
first-run forms or `/goals`, follow the current action to the existing
confirmed action form or Goal page, check proof in `/verification` or
`/ci-evidence`, save the day with the route-local Finish Today form or
`/workspace#save-workspace`, and return through `/resume`. A visible
`Guide Command Panel` now embeds the existing confirmed first-run or current
Goal action form when available, so an empty checkout can register a project
and then create the first Goal from the guide without hunting through docs. A
read-only `Operator Recipes` panel follows it with seven intent cards for
Start The Day, Set Up Or Select Goal, Do The Next Thing, Unblock Work, Check
Proof, Finish Today, and Resume Tomorrow, routing each intent to existing
browser surfaces and confirmed forms while naming the current proof and
workspace posture. It
is read-only on GET and only reuses existing local surfaces and confirmed
forms; it does not call providers, perform network actions, push, create PRs,
deploy, or mutate external systems.

Use `/resume` when returning to ClankerOS after a break. It now opens with a
primary return link, a browser-local `Browser Resume` panel, and a
`Resume Operator Workbench` before shared route/focus diagnostics or the
command readback, so the first screen is the current return path instead of a
report. `Browser Resume` reads this browser's
`localStorage:clankeros-route-history`, ignores `/resume` itself, and offers
the most recent non-resume route with route-scoped scroll/open-panel memory
when available. It does not write server state; the canonical saved workspace
still comes from the explicit `/workspace#save-workspace` Finish Today form.
The rest of `/resume` reads the saved workspace state, prefers the exact saved
`resume_surface` local route when one exists, shows the saved
goal/project/artifact links, preserves filters and expanded panel readbacks,
and keeps saved-state, command, workbench, and browser-local resume evidence
collapsed by default.
Saved Goal links on Home, `/resume`, `/workspace`, and the Goal resume snapshot
are now title-first when a title exists, while raw Goal ids and label-source
readbacks remain in collapsed evidence for review and automation.
Before a saved Goal exists, `/resume` follows first-run progress instead of
stopping at the project link: an empty checkout renders the same-page
`Resume First-Run Action` `register-project` form, and a
registered-project/no-goal state renders the same-page `create-goal` form while
still showing the saved project. The
workbench shows
do/check/unblock/finish cards for the saved Goal, the current action or
same-page action form, readiness repair, blockers, last artifact, and the
existing `/workspace#save-workspace` finish surface. The `Resume Command Bar`
follows with readiness, phase, current gate, next action, target surface,
action-form availability, last artifact, and zero-effect counters inside
collapsed evidence. It also adds a `Resume
Readiness` checklist for the saved project, goal, filters, expanded panels,
last artifact existence, and next local surface, and shows a `Resume Next
Action` section with the saved goal's current phase, one next action, operator
attention cue, target surface, and the same confirmed local action form that
the Goal page would show when that next action is browser-available. When
first-run is still incomplete, the same Readiness, Next Action, and Workflow
Map sections show the current first-run gate, next setup action, and
same-page setup target, with Home/Today/Goals setup links retained as fallback
evidence. It also
includes a read-only `Resume Workflow Map` that mirrors the Goal page
lifecycle rail, showing the saved goal's current gate, gate progress, next
action, and no-write/no-network boundaries before the operator leaves
`/resume`. `/workspace` now opens with the
`Workspace Operator Workbench` before shared route/focus diagnostics or
saved-state evidence. The workbench gives the saved workspace do/check/unblock/
finish cards, same-page action-form routing, blocker routing, last-artifact
readback, and a Finish Today link that opens the collapsed `#save-workspace`
form. When no workspace has been explicitly saved yet but a lead Goal exists,
that form is prefilled from the current project, Goal, goal-scoped filters,
latest artifact, and exact `resume_surface` route, with a
`Workspace save defaults` evidence block showing that the values are
suggestions only and nothing was written on GET. The
read-only `Workspace Restore Map` follows with Restore, Goal, Artifact,
Filters + Panels, and Tomorrow cards that distinguish saved workspace state
from suggested defaults before the longer checklist. The Goal card is
title-first when possible, while still retaining exact saved Goal id and route
evidence for restoration. A read-only `Workspace View Memory` panel follows to
inspect and clear browser-local view state such as theme, focus mode, Goal
board filters, open panels, scroll position, search lanes, timeline lanes,
Goal section searches, Today Goal Queue view, Today and Goal decision filters,
artifact filters, notes filters, note drafts, setup and workflow form drafts,
Memory Bank filters, Skills Inventory filters, and the First Run Checklist
from `localStorage` without
changing `.clanker/app/workspace.json`.
The read-only
`Workspace Daily Brief` and `Workspace Workflow Map` then follow with the
saved goal's current gate, gate counts, and finish posture, while saved-state
and restore-link readbacks stay inside collapsed evidence.
Before a saved Goal exists, `/workspace` now follows the
same first-run progress as Home, Today, Goals, and `/resume`: an empty checkout
points its daily brief, workbench, continuation readback, restore links, and
workflow map at the same-page `Workspace First-Run Action` `register-project`
form, while a registered-project/no-goal workspace points at the same-page
`create-goal` form and keeps the saved project visible. Home/Today/Goals setup
links remain in collapsed evidence as fallback routes. Both routes report that
they write nothing on GET.

For the first manual browser pass, open `/demo#demo-fixture-action` and confirm
the browser-local demo action. CLI fallback:
`python3 -m agent_os.cli demo` or
`python3 -m agent_os.cli demo-app-scenario`. After the action result offers
`/demo` as the next surface, open `/goals` and follow the state-aware dogfooding links
into the demo project, selected workflow, delegation, coder worktree run,
review artifact, approvals, and inbox. The `/demo` page starts with a
read-only `Demo Operator Workbench` for Now, Project, Workflow, and Proof,
then shows a read-only `Demo Walkthrough Map` with Fixture, Project + Goal,
Workflow, Run, Approval, Publish Boundary, and Resume + Proof cards before the
fixture command/readback details. It
still shows whether fixture state exists, the preferred `demo` command,
compatibility command, selected project, Goal, delegation, run, next local
surface, and zero-effect counters before the longer walkthrough. It also shows
a read-only `Demo Next Action` panel and `Demo Browser Progress` checklist for
the selected fixture run, so you can see
whether the app path is waiting on commit request, commit approval, local
commit, publication request, publication approval, publication handoff, or
manual push/PR outside ClankerOS. It also shows `Demo Gate Artifacts`, linking
the commit request, commit decision, local commit artifact, publication
request, publication decision, publication handoff, and PR-body artifact as
those gates become available. The `Demo Gate Actions` panel names the current
gate, the local form action, required input, expected output artifact, and
renders the safe confirmed local form when the current step can be driven from
the app. Draft-backed workflow fields preserve unsent operator notes,
messages, and safe local command text across reloads until the operator clears
them or the confirmed local action succeeds. Once the publication handoff is
ready, the demo keeps push/PR work
outside ClankerOS and exposes the confirmed local `complete-goal` form so the
operator can record that manual publication finished and review completed Goal
evidence.
`Manual Browser Checkpoints` lists the exact route markers to confirm across
`/demo`, `/dogfooding`, workflow, project, delegation, run, approvals, inbox,
verification, and health surfaces, then lets you jump directly to the relevant
local surface.

Use `/goals` as the daily cockpit. It separates active, paused, and completed
goals into scan-first Goal cards that link each goal to its detail page,
project page, and next action surface while showing phase, next action, task
progress, waiting count, and open work from existing local state. A
`Goal Board Workbench` starts the page before shared
route/focus diagnostics, with visible Do Now, Selected Goal, Attention, and
Start/Resume cards; it links the selected Goal straight to its confirmed
action form when one exists, routes pending approval attention through
`/approvals?goal_id=<goal_id>`, and anchors active, paused, and completed
lanes for fast switching. The read-only
`Goal Board Command Bar` follows as collapsed command evidence with total goal
counts, the prioritized saved or active Goal, its current phase, one next
action, the target surface, waiting counts, resume link, and zero-effect
counters. Populated cockpit counts are also collapsed as evidence so the board
arrives quickly on mobile. A browser-local `Goal Board Filter` follows the
goal creation form and filters active, paused, and completed lanes by title,
project, phase, status, next action, progress, or remaining work, with a live
count, mode buttons, first-match jump, and no-write/no-network evidence. It
also sorts the already-rendered Goal cards locally by updated time, waiting
items, open work, progress, or title, so a busy day can be re-prioritized
without running commands or changing state. The board view remembers its
query, lane mode, and sort in browser-local storage across reloads, with a
Reset view control for returning to the default board. The
cockpit also includes a confirmed local
`Start Another Goal` form backed by the existing `create-goal` action,
so an operator can add the next goal for a registered project without
switching to the CLI. Setup and Goal creation forms keep unsent edits in
browser-local `localStorage:clankeros-action-form-draft:<action>:<scope>`
until the operator clears them or the confirmed local action succeeds. The
same browser-local draft behavior is used for goal workflow forms that collect
worktree approval notes, safe run commands, commit/publication messages,
publication approval notes, and manual `complete-goal` notes.
Use `/goals/<goal_id>` as the
goal-centered workbench: the page is now content-first, so the Goal summary,
large Current Phase banner, jump bar, action dock, progress meter, and
attention digest appear before shared route/focus diagnostics. The summary itself is title-first: it
uses the human Goal title/intent as the page heading, keeps the Goal id as
metadata instead of the headline, and preserves the project, status, phase,
and local refresh posture in the readback. Shared Goal navigation now follows
the same rule: breadcrumbs, Route Context, and command-palette route evidence
show the human Goal title while retaining explicit Goal id evidence fields for
review and automation. The Goal Jump Bar covers phase, action,
workflow, timeline, evidence, artifacts, notes, git, and remaining work. Its visible `1`-`9` key badges and
`aria-keyshortcuts` jump to those local anchors without submitting forms,
while jump-state evidence stays collapsed by default,
then an in-flow `Goal Action Dock` keeps the current action, gate, CI proof
target, and resume route near the top of the workbench while jumping directly
to the existing confirmed Goal action form when one is available. A read-only
`Goal Progress Meter` follows with task and workflow progress bars, waiting
operator work, latest proof state, and the next confirmed browser action before
deeper command evidence. A read-only `Goal Attention Digest` follows the meter
with Now, Approvals, Incidents, Recommendations, Open Work, and Safety cards so
the first waiting queue and safe next click are visible before deeper command
evidence. A read-only `Goal Decision Queue` follows with exact Goal-scoped
operator rows for the current action plus pending approvals, incidents,
recommendations, or blocked tasks, linking to the existing confirmed action
form or scoped approval surfaces without deciding anything on GET. It includes
a browser-local `Goal Decision Filter` for narrowing those already-rendered
rows by current action, approval type, incidents, recommendations, blocked
work, or text while restoring lane/query per Goal from
`localStorage:clankeros-goal-decision-filter:<goal_id>`. The dock, meter,
digest, and decision queue precede the Goal Command Bar, Goal Operator
Workbench, Goal Daily Loop, Goal Return Brief, Goal Session Digest, Goal
Activity Pulse, Goal Continuation Rail,
next action, next recommendation, Goal Workflow Map, Goal Coder Handoff
Digest, Goal CI Handoff, live state, and collapsed section index before the detailed progress, timeline, activity log, goal risk, completion
criteria, completion readiness, evidence, delegations, runs, approvals,
artifacts, a typed Goal Artifact Explorer, memory, skills used, git status,
operator notes, a goal-scoped resume snapshot, and remaining work. The page
auto-refreshes by local polling, pauses while the operator is editing a form or
the tab is hidden, and stays local-only. The Goal Command Bar near the top now
opens with visible Now, Phase, Progress, Proof, and Resume cards, while its
full current phase, primary action, target local surface, progress, waiting
counts, resume route, latest project-scoped CI proof state, and zero-effect
boundary stay available in collapsed command evidence. Goal
Operator Workbench follows it with a human-readable do/check/unblock/finish
strip: its primary action points directly at the in-page Goal action form when
one is available, links
the source surface and first unblock surface, names the current gate/progress,
and keeps confirmation/write/provider/network/external-effect counters
available in collapsed workbench evidence before the deeper diagnostic
sections. The Goal Next Action section now starts
with a human-first focus strip for Now, Gate, Target, and Boundary, with one
primary link to the existing confirmed form or source surface, then renders the
confirmed form before collapsed action evidence. Goal Daily Loop now opens as a
five-card Continue, Start, Unblock, Pause, and Finish Today strip. Detailed
local state stays in collapsed daily-loop evidence, while the confirmed
`pause-goal` and `save-workspace` forms live in hash-openable Pause and Finish
Today details so ending or shelving a goal is a direct click, not a hunt
through proof rows. `pause-goal` moves any non-paused incomplete goal into
paused lanes without approving work, running providers, using the network, or
mutating external systems. Goal Return Brief now follows as its own five-card
return board for Continue, Latest, Blocker, Finish, and Resume, with the
same gate, activity, artifact, CI, resume-readiness, blocker, and zero-effect
state preserved in collapsed return evidence instead of leading the operator
through proof rows.
The read-only `Goal Session Digest` follows the return brief and condenses the
current continuation into Continue, Since Save, Latest Artifact, Waiting, and
Finish Today cards. It uses existing Goal state, saved workspace timestamp,
latest local timeline item, latest artifact, and waiting queue counts, then
keeps the exact sources and zero-effect boundary in collapsed digest evidence.
The read-only `Goal Activity Pulse` follows the digest with Latest, Recent
Three, Mix, Artifact, and Next cards, reusing the Goal timeline so returning
operators can see the newest linked movement before opening the full timeline.
The read-only `Goal Continuation Rail` follows the pulse as visible
Now, Next Gate, Then, Publish Boundary, and Finish Today cards, while detailed
gate rows, exact surfaces, manual publish boundary, and zero-effect counters
stay in collapsed continuation evidence. Goal
Section Index now includes a browser-local section finder with a type-to-filter
input, match count, first-match jump, compact anchor chips, visible View
status, and per-Goal query memory in
`localStorage:clankeros-goal-section-finder:<goal_id>` before the collapsed
evidence ledger, so the long Goal page can jump back to operational panels
such as approvals, memory, or git without memorizing the page structure.
Workspace View Memory can inspect or clear those section searches alongside
the rest of the browser-local view state. Goal
Overview now starts with a read-only `Goal Overview Command Bar` with visible
Now, Scope, Progress, Waiting, and Safety cards before collapsed command
evidence and collapsed raw metadata. Goal Risk now starts with visible Now,
Counts, Boundary, First Task, and Safety cards before collapsed command
evidence and collapsed detailed risk rows. Goal Completion Criteria now starts
with visible Now, Source, Progress, First, and Safety cards before collapsed
command evidence and collapsed criteria rows. Goal Progress now starts with
visible Now, Tasks, Gates, Waiting, and Safety cards before collapsed command
evidence, the browser progress bar, and collapsed detailed progress counts. Goal
Completion Readiness turns the same local gate, approval, incident, and
publication-handoff state into one explicit finish posture. It names the
current blocker or next safe action, links the relevant local surface, and only
offers the confirmed `complete-goal` form after the manual publish handoff is
ready. The Goal
Git Status section now starts with a read-only `Goal Git Command Bar` that
opens with visible Now, Branch, Changes, Proof, and Safety cards. It still
summarizes the registered project root, branch, commit, clean/dirty posture,
tracked and untracked counts, latest goal-linked `git_status.txt` evidence
when available, and one next local surface, but the detailed command evidence
and repository snapshot stay collapsed without fetching GitHub status or
mutating the repo. The Goal
Daily Loop turns the same local state into start/continue/unblock/finish cues:
`/resume`, the current next action, the first approval/incident/recommendation
surface, and a confirmed `save-workspace` form that records this goal and its
latest artifact as tomorrow's resume point without writing on GET. Goal Return
Brief follows it with a read-only return-to-work snapshot: current gate, next
action, resume readiness, latest activity, latest artifact, CI proof posture,
blocker route, `/resume`, and finish surface. The Goal Workflow Map now opens
with visible Now, Progress, Approvals, Publish Boundary, and Finish Today cards
that point at the existing Goal action form, Remaining Work, goal-scoped
approvals, CI handoff, and Finish Today save form. The detailed lifecycle rail
from scout delegation through manual publish, every gate's eventual operator
surface, the manual publish boundary, and zero-effect counters remain in
collapsed workflow evidence without writing on GET. Goal Coder Handoff Digest
follows the workflow map and turns delegation, context-pack,
implementation-handoff, coder-prep, worktree, commit, and publication state
into scan-first Now, Handoff, Prep, Execute, Ship, and Safety cards. Goal CI
Handoff follows near the top of the Goal page with visible Check GitHub, Record
Proof, Current Proof, Full Suite, and Finish Today cards. The cards expose the
project-scoped proof status, latest operator-recorded GitHub Actions evidence,
exact `gh run list` / `gh run view` command templates, and a same-page JSON
paste target for recording proof, while the detailed ledger remains collapsed
and still does no GitHub polling or external mutation on GET. Goal Live State
now opens with visible Now, Phase, Refresh, Pause Rules, and Safety cards,
including a local `Refresh now` control, while detailed refresh posture stays
collapsed and the five-second loop still pauses during edits or hidden tabs.
Goal Remaining Work now opens with visible Now, Gate Progress, Waiting, Open
Work, and Finish cards; detailed command proof and the full remaining-work
checklist stay collapsed while preserving current gate, done/pending/waiting
gate counts, open task/incident/recommendation counts, pending approvals, one
next local surface, and zero-effect boundaries. It now also includes a
confirmed `complete-goal-task` closeout for ready publication-handoff evidence,
so a reviewed local workflow can update the task row, linked plan step when
present, refreshed `TASKS.md`/`PLAN.md`, workspace resume point, and timeline
event without running fresh verification or taking external action. The Next Recommendation
section names whether the recommendation
comes from an open task recommendation or from current phase plus local goal
records, then points at the local target surface without writing on GET. When
an open task recommendation includes `recommended_commands`, the Goal page
also shows copy-only `Goal Recovery Commands` cards with clipboard buttons,
evidence links, and explicit no-execute/no-retry/no-replan/no-write counters.
Those cards are now the primary Goal-local target for recommendation recovery:
the Goal Next Action, header `Next` shortcut, attention digest, ribbon, daily
loop, workbench, session digest, overview, incident, and remaining-work cards
route to `/goals/<goal_id>#goal-recovery-commands` when stored commands exist,
with incident triage preserved as a secondary surface.
The in-flow Goal Jump Bar keeps the most-used in-page anchors one click or
one keypress away without covering later controls. The in-flow Goal Action
Dock keeps the current action, gate, proof, and resume route visible near the
top of the Goal without covering later controls, and jumps directly to the
confirmed form without adding a second action form. The Goal
Next Action focus strip makes the selected action
readable at the point of decision and keeps the confirmed form ahead of
diagnostic evidence, while the Goal Section Index near the top links to the
main day-loop areas through visible Operate, Proof, Work, Knowledge, and
Finish cards, with the full stable anchor map still collapsed underneath for
deep review.
Goal Delegations starts with a read-only `Goal Delegation Command Bar` that
opens with visible Now, Latest, Workflow, Handoff, and Safety cards. It still
summarizes scout delegation counts, context-pack readiness, implementation
handoff readiness, coder-prep packets, worktree plans, the latest delegation
workflow surface, and one next local continuation, while command evidence and
detailed delegation rows stay collapsed.
Goal Runs starts with a read-only `Goal Run Command Bar` that summarizes task
and worktree run counts, review readiness, changed-file posture, the latest
run surface, and one next local run action as visible Now, Latest Run, Review,
Changes, and Safety cards before collapsed command evidence and detailed run
rows.
Goal Approvals starts with a read-only `Goal Approval Command Bar` that
summarizes pending and approved worktree, commit, and publication gates, points
at `/approvals` or the next local Goal surface as visible Now, Pending,
Approved, Downstream, and Safety cards, and keeps approval decisions on
confirmed local forms instead of writing on page load.
Goal Incidents starts with a read-only `Goal Incident Command Bar` that
opens with visible Now, Open, First, Recovery, and Safety cards while
preserving open/resolved incidents, recommendations, first incident evidence,
one triage surface, and zero-effect boundaries inside collapsed command
evidence before the detailed incident rows.
Goal Evidence starts with a read-only `Goal Evidence Command Bar` that
opens with visible Now, Latest, Inventory, Attention, and Safety cards. It
summarizes run, worktree, incident, recommendation, and typed artifact evidence
counts, points at the latest bounded artifact or highest-priority local evidence
surface, and keeps provider/network/external-effect counters at zero inside
collapsed command evidence. A read-only `Goal Evidence Digest` follows with
Proof, Latest, Run Proof, Artifact Mix, CI Proof, and Safety cards before the
collapsed detailed evidence list, so the operator can distinguish local proof,
artifact coverage, and recorded CI posture without opening the full inventory.
Goal Verification Evidence starts with a read-only `Goal Verification Command
Bar` that opens with visible Now, Current, Latest, Record, and Safety cards
before collapsed command evidence and collapsed proof lines. It shows whether
project-scoped proof is missing, stale, job-scoped early proof, or current
full workflow success, links to `/verification` and `/ci-evidence`, shows
whether the latest operator-supplied CI proof matches the current checkout,
and includes a confirmed Goal-scoped form for pasted GitHub Actions JSON. The
form infers run identity from `databaseId`/`url`, validates the supplied JSON,
and records local CI proof without app-side GitHub polling.
Goal Memory starts with a read-only `Goal Memory Command Bar` that summarizes
project/global memory artifacts, project/active/proposed/global/generated entry
counts, operator-note state, future-work count, pinning posture, one next local
memory action, and zero-effect boundaries as visible Now, Notes, Memory Bank,
Pin, and Safety cards before collapsed command evidence and detailed memory
readback.
Skills Used starts with a read-only `Goal Skills Command Bar` that summarizes
task skill tags, matching generated or available skill records, usage and
project counts, delegation profile usage, one `/skills` or `/profiles` review
target, and no-execution/no-install/no-network boundaries as visible Now,
Record, Usage, Profile, and Safety cards before collapsed command evidence and
detailed skill readback.
Timeline entries link back to the relevant local artifact, delegation, run,
approval queue, or goal surface, and render as scan-first event rows with
time, event-kind badge, clickable message, and target badge. The timeline also
backfills generic `Artifact recorded` events from the same bounded artifact
registry used by the Goal Artifact Explorer. The timeline starts with a
read-only `Goal Timeline Command Bar` that exposes visible Now, Latest,
Families, Flow, and Safety cards before collapsed timeline command evidence
and metadata. A read-only `Goal Timeline Digest` follows with Span, Latest,
Artifact, Next, and Safety cards so the chronological list can be scanned from
the current useful event, newest artifact, and next action before reading every
row. A browser-local `Timeline Lane Filter` follows the digest so the operator
can switch the rendered chronology between all events, artifacts, approvals,
delegations, runs, tasks, notes, and generic events without changing Goal
state or leaving the page. The selected lane is remembered per Goal in
`localStorage:clankeros-goal-timeline-lane:<goal_id>` across reloads, with a
Reset lane control for returning to the full chronology. The Activity Log now starts
with a read-only `Goal Activity Command Bar` that exposes visible Now, Latest,
Signals, Window, and Safety cards before collapsed activity evidence and
metadata, then the recent human-readable event list. Progress starts with a read-only Goal Progress
Command Bar, then uses a real browser progress bar.
Operator Notes starts with a read-only `Goal Operator Notes Command Bar` that
opens with visible Now, Artifact, Resume, Capture, and Safety cards before
collapsed command evidence and collapsed note details. A `Goal Notes Browser`
follows it with already-rendered note cards, text search, per-Goal browser-local
view memory in `localStorage:clankeros-goal-notes-filter:<goal_id>`, and Reset
notes; it reads only the goal-scoped `operator-notes.md` artifact and does not
open arbitrary filesystem paths. The confirmed `save-goal-note` form remains
the local write path, now uses a multiline capture box, and keeps unsent draft
text in browser-local `localStorage:clankeros-goal-note-draft:<goal_id>` until
the operator clears it or a confirmed note write updates the artifact. It
appends resume context to the artifact without overwriting earlier notes.
The Goal Resume Snapshot reads `.clanker/app/workspace.json` and opens with
visible Now, Current, Saved, Artifact, and Safety cards before collapsed
resume evidence, collapsed `Goal Workspace Restore State`, and a collapsed
confirmed `save-workspace` form that returns to the same goal page after
saving. It does not write on page load, fetch GitHub status, call providers,
push, create PRs, deploy, or mutate external systems.
The Goal Artifact Explorer groups goal-linked artifacts as Markdown, JSON,
Patch, or Text and links them through the bounded `/artifacts` viewer instead
of exposing raw filesystem browsing. The Goal page now starts the artifact
area with a read-only `Goal Artifact Command Bar` that opens with visible Open,
Latest, Types, Inventory, and Safety cards. It summarizes artifact record
counts, available/missing posture, render-family counts, source-family counts,
the latest artifact, and one next bounded artifact review click while keeping
command evidence and the detailed artifact list collapsed by default. The
typed explorer now starts with a browser-local `Goal Artifact Filter` for
type, source, and text narrowing over the already-rendered artifact rows; the
selected filter is remembered per Goal in
`localStorage:clankeros-goal-artifact-filter:<goal_id>` and Reset filter clears
that browser-local view without reading arbitrary filesystem paths. A
browser-local `Goal Artifact Reader` follows the filter so the operator can
preview one already-registered artifact inline, switch between bounded
Markdown/JSON/Patch/Text renderers, keep the selected artifact per Goal in
`localStorage:clankeros-goal-artifact-reader:<goal_id>`, and reset that reader
view without executing content, writing state, or browsing raw paths. Each
artifact page starts with
a visible `Artifact Operator Workbench` for opening the inert content,
returning to the owning Goal/delegation context, remembering or resuming from
the artifact, and checking the safety proof. It now follows with a visible
`Artifact Format Lens` that names the active Markdown, JSON, patch/diff, text,
or log renderer, gives the format-specific read/review action, and keeps
structure, byte counts, and inert-renderer boundaries visible before the
content body. A visible `Artifact Relationship Map` follows it with Workflow,
Goal, Source, Resume, and Boundary cards so Goal/project/delegation/run return
paths are visible before dense evidence. When the artifact path resolves to a
stored Goal, those artifact context links are title-first while preserving raw
Goal ids and label-source evidence for automation. The detailed `Artifact
Command Bar`, `Artifact Review Brief`, format evidence, and relationship
evidence stay collapsed by default while preserving path, type, renderer,
size, line count, truncation state, inferred project/goal/delegation/run context,
saved-resume-anchor posture, and zero-effect boundaries. The content view
remains inert and bounded.

Use `/goals` on a fresh checkout for first-run browser actions. The page now
renders a state-aware First Run Guide plus confirmed local forms for
`register-project` and `create-goal`, with browser-local draft memory for
those setup fields, so a new operator can create a project and first goal
without switching to CLI commands. The guide tracks whether
the project, goal, first delegation, and context pack exist, then points to
the current surface, the confirmed local `run-delegation` action, or its exact
CLI fallback command. It also renders `First Run Next Step` plus the
browser-local `First Run Checklist` plus the `First Run Progress` strip so the
operator sees the immediate browser action, resumable setup checks, five-step
path, and current gate before the forms.
After a confirmed `register-project` action, the
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
save and restore open project, open goal, filters, expanded panels, last
viewed artifact, and exact `resume_surface` route in
`.clanker/app/workspace.json`, with saved-goal phase and next-action
readbacks on each return-to-work surface. `/workspace` now also
has a `Workspace Operator Workbench` beside the editable state form, and
`/resume` and `/workspace` both expose the saved goal's workflow gate map, so changing saved
context does not hide the current gate.
Use the goal page note form for day-to-day operator breadcrumbs, then find the
same note artifact again from `/memory`. The Memory Bank opens with a
workbench, pinboard, and browser-local `Memory Inventory Filter`, so you can
narrow already-rendered proposed, active, project, global, generated, note, or
future-work rows by lane/text and restore that view from
`localStorage:clankeros-memory-inventory-filter` without writing memory state.
Use `/search` for bounded global search across indexed goals, projects,
delegations, known artifacts, incidents, recommendations, memory, runs, and
approvals. Goal search results include live local phase, one next action, and
remaining-work counts, so action or phase searches can return the Goal to
continue. Approval search now includes the first-class coder worktree, commit,
and publication approval queues, with scoped links back to the matching
`/approvals?goal_id=...`, `/approvals?run_id=...`, workflow, or run surface
instead of only the older generic approval rows. `/search` is now
content-first and opens with a visible
`Search Operator Workbench` before shared route/focus diagnostics, turning the
query, first useful hit, result list, and `/resume` into four browser cards.
It now follows with a visible read-only `Search Result Map` for Goals,
Projects, Work, Decisions, Knowledge, and Artifacts, so category counts and
first targets are visible before the flat result list. A browser-local
`Search Result Filter` follows the map so broad queries can be narrowed to one
lane without another request; the selected lane is remembered per query in
`localStorage:clankeros-search-result-lane:<query-hash>` and Reset lane clears
that browser-local view. Search state, result map, result filter, workbench
evidence, and command evidence stay collapsed by default while preserving
result counts, first-result target links, lane counts, and the
no-write/no-network/no-raw-filesystem boundary in the DOM. Use `/memory`, `/skills`, and
`/profiles` for local readbacks of memory entries, generated skills/usage,
and inactive future provider-routing lanes. `/memory` is now action-first and
opens with a visible `Memory Operator Workbench` before shared route/focus
diagnostics and command readback, turning the next memory action, proposed
pins, operator notes, and resume target into four browser cards. It now follows
with a visible read-only `Memory Pinboard` for Active Pins, Proposed Pins,
Project, Global, Generated, Operator Notes, and Future Work before the dense
memory inventory. Memory state, pinboard, workbench evidence, and command
evidence stay collapsed by default while preserving entry counts,
proposed-memory pin posture, saved workspace context, and
no-write/provider/network/external-effect boundaries in the DOM. `/skills`
is now action-first and opens with a visible `Skills Operator Workbench` before
shared route/focus diagnostics or command readback, turning generated-skill
review, usage review, and resume context into browser cards. It now follows
the usage map with a browser-local `Skills Inventory Filter`, so you can narrow
already-rendered available, generated, active, proposed, used, or unused skill
rows by lane/text and restore that view from
`localStorage:clankeros-skills-inventory-filter` without installing or
executing skills. Skills state, usage-map, filter, workbench evidence, and
command evidence stay collapsed by default while preserving skill counts,
generated-skill posture, usage/project counts, last-used posture, the first
bounded skill artifact, and no execution/install/provider/network effects in
the DOM.
`/profiles` is also action-first: it opens with a visible
`Profiles Operator Workbench` before shared route/focus diagnostics or command
readback, turning storage-profile review, future-lane review, and resume
context into browser cards while provider/model routing remains inactive.
It now follows with a read-only `Profile Routing Matrix` that maps Planning,
Coding, Review, Docs, Cheap Model, and Frontier Model lanes to stored local
profile rows, cost posture, `use_for` labels, and inactive provider/model
routing status. A browser-local `Profile Routing Filter` then narrows the
already-rendered matrix cards and profile rows by lane, storage/configured
posture, or text, remembers lane/query in
`localStorage:clankeros-profile-routing-filter`, and resets without enabling
providers or model routing. Profiles state, matrix evidence, filter evidence,
workbench evidence, and command evidence stay collapsed by default while preserving
configured/storage profile counts, future-lane readiness, adapter/write
posture, `use_for` posture, and provider/model routing disabled proof in the
DOM.
`/profiles` also shows both `.clanker/profiles.yml` names and SQLite profile
storage rows, including labels, modes, cost tiers, write posture, adapter
status, and `use_for` labels without enabling providers.
Use `/incidents` as a read-only triage board for open incidents, resolved
incident history, and task recovery recommendations. The page now opens with
an `Incident Operator Workbench` before shared route/focus diagnostics or
command readback, showing Now, Evidence, Recover, and Finish Today cards while
incident workbench evidence, command evidence, and the Finish Today save form
stay collapsed by default. The older `Incident Triage Command Bar` remains as
read-only evidence with one local review target, incident and recommendation
counts, evidence links, and no-resolution/no-retry/no-network boundaries.

The app shell also includes a global `Operator Ribbon`, `Operator Focus`
strip, a read-only `Route Context` breadcrumb strip, recent local items, a
command palette, keyboard shortcuts, local Focus mode, and a dark/light theme
toggle on every page. The header now exposes a visible `Keys` control and the
`?` shortcut to open the same local keyboard-help dialog without opening
palette evidence first. Focus mode uses the header `Focus` button or `m`
shortcut to hide Recent Items, Route Context, Operator Focus, and Last Action
strips while keeping the Operator Ribbon and page body visible. It is stored in
`localStorage:clankeros-focus-mode` only and does not write server state. The
shared shortcut layer now includes `w` for `/workspace` and a route-aware `f`
for Finish Today: Today opens `#today-finish`, Goal pages open
`#goal-finish-today`, and other routes fall back to
`/workspace#save-workspace`. `n` still opens the current recommended next
action, so return-to-work, Finish Today, and the main next click are available
without opening the palette. If a browser-confirmed action form is available,
`n` opens that existing form details panel; it never submits the form or writes
state on its own. The header also exposes a visible `Finish` control backed by
the same route-aware target. The ribbon sits above the sidebar and page body
with visible Now, Goal,
Attention, Finish, Resume, and Search cards, so every route immediately shows
the current or lead Goal, one recommended click, waiting-review posture,
end-of-day save routing, resume state, and collapsed no-write/no-provider/
no-network evidence before the operator starts decoding the page. After a
confirmed local action, the shell also shows a read-only `Last Action` strip
from `.clanker/app/workspace.json`, with the action result, target notice
surface, saved Goal/project context, and zero-effect counters so the operator
can recover the last handoff after navigating away. Action notice pages now
start with a Next Step card sourced from first-run or saved-Goal state, so
following a completed-action notice points straight at the next confirmed form
or workflow surface instead of only echoing the previous result. The route
context strip now starts with a compact action-first focus grid: current page,
next local action, back target, Goal, Project, and `/resume`. The full route
family/path, saved workspace anchors, focus target, and zero-effect counters
remain available inside collapsed `Route evidence` before the page content.
The recent-items sidebar now starts with a read-only `Recent Items
Command Bar` plus a visible return dock for Recent, Workspace, Action, and
Artifact, so the operator can reopen the latest surface, saved project/Goal,
last action notice, or saved artifact without expanding the longer shortcut
list. It also includes a browser-local `Viewed Pages` panel backed by
`localStorage:clankeros-route-history`, which records the local app pages
visited in this browser, dedupes them by route, caps the list at 12 entries,
and can be cleared with an explicit click without touching server state. The
shared shell also remembers open/closed route panels in route-scoped
`localStorage:clankeros-open-panels:<route>` entries, so expanded evidence and
details survive reloads on the same page while `/workspace#workspace-view-memory`
can inspect or reset them with the other browser-local view state. It also
remembers route-scoped scroll position in
`localStorage:clankeros-scroll-position:<route>` after the operator scrolls, so
long Goal pages reopen near the same working position while hash anchors still
take precedence. A
browser-local `Find Recent` filter narrows the already-rendered
shortcut rows by text, remembers the query in
`localStorage:clankeros-recent-items-filter`, and resets without writing server
state. When an exact saved `resume_surface` exists, the Workspace card opens
that route directly. Workspace/goal/delegation/run counts, saved workspace
context, last action, artifact targets, filter evidence, and zero-effect
counters stay inside collapsed evidence and the remaining recent shortcuts stay
in a second collapsed disclosure. The focus strip keeps the saved or lead
goal's primary action, phase, progress, waiting counts, and resume link visible
as compact action cards outside the Goal page. It can expand the same confirmed
local action form when the current next action is browser-available, while the
full focus readback and zero-effect counters stay inside collapsed
`Focus evidence`.
Before any Goal exists, the same shared shell follows first-run progress
instead: Home, Today, and Goals point the route context, command palette, and
Operator Focus at their same-page `Create Project` or `Create First Goal`
forms, while other pages link back to those Home/Today/Goals first-run
anchors.
The command palette now opens with a `Palette Focus` launcher: continue the
current Goal action, jump to search, resume the saved workspace, or stay on the
current page. The search box also narrows a visible `Palette Results` list of
local routes, recent work, and the focused Goal's core section anchors as you
type, so `timeline`, `approval`, `artifact`, `memory`, `git`, or `remaining`
can jump straight into the Goal page without scanning. ArrowDown/ArrowUp move
through visible local commands and Enter opens the active local result, while
the Search button remains the full indexed `/search` fallback. Browser-local viewed
pages are appended to the same palette results after localStorage readback, so
recent route hops are searchable from `/` without a server write. A no-match state leaves
the existing Search button available for full indexed search. It also includes a
visible `Quick Switch` dock for Continue, Workspace, Action, Artifact, and
Finish so the palette can recover the current Goal, exact saved workspace
surface, last action target, latest artifact, or `/workspace#save-workspace`
handoff without opening the sidebar. The
route-aware `Current Page` readback, keyboard shortcuts, and long open list
live in collapsed `Palette evidence and shortcuts`, while the
goal-aware `Continue Current Goal` block and its confirmed local action form
remain one keyboard open away. Those controls stay inside the local browser app
and do not perform external effects.

Use `/workflow?delegation_id=<id>` or `/workflow?run_id=<coder_run_id>` when
you want the scoped operator map. The workflow page is action-first: it opens
with a visible `Workflow Operator Workbench` before shared route/focus
diagnostics and command readback, with cards for the current workflow action,
selected state, queue attention, and `/resume`. It then shows a read-only
`Workflow Scope Picker` with direct cards for the primary pickup, recent
delegations, recent coder runs, the parent Goal, and safety evidence, so a
plain `/workflow` visit can choose the right delegation or run without
detouring through another page. A visible read-only
`Workflow Journey` follows with nine stage cards for Select, Goal + Scout,
Context, Handoff, Coder Prep, Approval, Execution, Commit, and Publish, marking
the current stage and linking to the next safe local surface. A visible
`Workflow Live State` panel follows so a selected delegation or coder-run
workflow can be left open during the day; it reloads the local page every five
seconds, pauses while form fields are focused or the tab is hidden, and keeps
refresh evidence collapsed with zero provider/network/external-effect
counters. A
`Workflow Finish Today` section then exposes a confirmed `save-workspace` form
that stores the exact scoped workflow route as `resume_surface`, so `/resume`
can reopen `/workflow?delegation_id=<id>` or `/workflow?run_id=<coder_run_id>`
tomorrow. The selected workflow page still includes a read-only
`Workflow Command Bar`, but its detailed
delegation/run, parent Goal, project, current stage, next local action, target
surface, reason, and zero-effect counters stay collapsed by default before the
detailed stepper. It also includes a read-only `Selected Workflow
Continuation` block with the exact next local action, run detail surface,
approvals queue, inbox, dogfooding checklist, and the explicit
`external_effects_created: false` boundary.

Use `/runs/<delegation_execution_run_id>` after scout/delegation execution to
continue from the returned evidence. The read-only `Delegation Run
Continuation` strip shows Now, Workflow, Handoff, Artifacts, and Goal cards
before the detailed evidence, linking only to existing local surfaces such as
the delegation page's `Safe Local Actions`, workflow map, artifact anchors,
and parent Goal.

Use `/runs/<coder_run_id>` to review the worktree evidence and gate state. The
read-only `Run Command Bar` starts the page with the run status, review gate,
commit/publication state, changed-file count, diff summary, next local action,
target surface, and no-write/no-network/no-push boundary. A `Run Operator
Workbench` follows it with do/check/unblock/finish cards for the same run gate,
including same-page action anchors, review/evidence links, approvals, parent
Goal, and a confirmed `save-workspace` form that stores the run and review or
evidence artifact as tomorrow's resume point without writing on GET. A
read-only `Run Gate Map` then lays out the run-scoped path from review through
commit request, commit approval, local commit, publication request,
publication approval, publication handoff, and the manual publish boundary,
marking the current gate and linking only to existing local surfaces. A
read-only `Run Continuation Strip` then condenses the current gate, scoped
approval queue, evidence, parent Goal, and manual publication boundary into
five visible cards before the dense workflow/evidence sections. The `Run
Review Gate` panel shows whether `runs/<source_run_id>/review.md` exists and
mentions the coder worktree run id. A read-only `Run Evidence Map` follows it
with Review, Diff, Changed Files, Validation, Logs, and Verification cards
that link to the bounded artifact viewer before the full evidence inventory.
The app only exposes the
`coder-commit-request` form when that gate passes. The Goal Next Action card
can now create that local review artifact with a confirmed `review-run` form
when the goal is waiting on review.

Use `/runs/<coder_run_id>` after publication handoff preparation when you want
the display-only manual publication commands. The app shows
`suggested_push_command`, `suggested_draft_pr_command`, and `pr_body_path`, but
it does not run them.

Use `/dogfooding` when you want one checklist for the first browser route walk:
refresh the fixture, inspect demo/workflow/project/delegation/run surfaces,
walk the local commit and publication gates, then hand verification to GitHub
Actions after a push. The page starts with a read-only `Dogfooding Operator
Workbench` before shared diagnostics, with Do Now, ClankerOS, Workflow, and
Proof cards, then keeps dogfooding workbench evidence, fixture evidence, and
the lower `Dogfooding Command Bar` evidence collapsed by default. The existing
`Dogfooding Next Action` panel still expands the fixture-backed next action and
links the project, delegation, workflow, run, approval queue, inbox, action
catalog, and verification surfaces. It also shows a copy-only `GitHub Actions
Follow-up` section with the direct snapshot handoff, `gh run view`, and
record-after-success command templates for the current checkout. The page is
read-only and does not fetch GitHub status.

Use `/delegation-runs` when you want a compact read-only index of scout
execution evidence, context packs, implementation handoffs, zero-effect
counters, retry signals, and next local operator actions before handing work to
coder prep. The page is action-first: it opens with a visible `Delegation Run
Operator Workbench` before shared route/focus diagnostics and command
readback, with cards for the next delegation/run action, scoped workflow,
handoffs ready for coder prep, and `/resume`. The `Delegation Run Command Bar`
still counts completed/pending runs, incidents, retry candidates, context
packs, and implementation handoffs, then points at the first local delegation,
run, or workflow surface to inspect next, but detailed evidence stays
collapsed by default.

Use `/projects` as the project workflow index. It shows each registered
project's root, default test command, current branch/commit, goal/task/
delegation counts, next recommended local operator action, and direct project
or selected workflow links. It also includes a confirmed local
`Register Local Project` form backed by the existing `register-project`
action, so daily project onboarding does not require switching back to the
CLI. The page now opens with a `Project Index Workbench` before shared
diagnostics, with Open, Register, Goals, and Resume cards plus collapsed
project-index evidence, so first-run project onboarding and daily project
selection have one visible next click.

Use `/projects/<project_id>` as the project-level launchpad. It shows goals,
tasks, delegations, artifacts, project guidance, and a read-only
`Project Command Bar` that summarizes branch/commit, goal and queue counts,
the next project action, the target local surface, and no-write/no-network
boundaries before the longer inventory. The page now starts with a
`Project Operator Workbench` before command evidence or shared diagnostics,
with Do Now, Goal, Unblock, and Finish Today cards. Workbench evidence,
command evidence, and the confirmed `save-workspace` form stay collapsed by
default while still preserving project state and zero-effect readbacks in the
DOM. A visible read-only `Project Goal Map` now follows the project-scoped
Goal form with Lead Goal, Phase, Work, Waiting, and Finish cards, so the
project page shows the Goal to resume before the dense inventory. It also
includes a confirmed
local project-scoped `create-goal` form, goal rows that link directly to
`/goals/<goal_id>` with phase, next action, and task progress, scoped workflow
links for delegations and coder runs, and links back to safe actions,
dogfooding, and verification without executing external effects.

Use `/actions` when you want a read-only catalog of available local app
actions, where their forms appear, what previous artifact they require, what
local artifact or approval they write, and the no-external-effects boundary.
The page now opens with the safe action header and an `Action Operator
Workbench` before shared route/focus diagnostics, so the first viewport is the
current usable action rather than readback. The workbench reads the same
first-run or lead-Goal focus as the rest of the app, names the current safe
local action, links the owning surface where the confirmed form already lives,
routes blockers to inbox/approvals/incidents, and exposes a confirmed
`save-workspace` finish form for returning to action context later. The
read-only `Action Workflow Map` follows with Setup, Scout, Context, Prep,
Approval, Execute, Commit, Publish, and Proof cards, marking the current stage
from the same operator focus context and linking to the existing local browser
surfaces. The `Action Catalog Command Bar` follows with visible Catalog,
Forms, Approvals, and Boundary cards, while detailed posture counters and
zero-effect readbacks stay available inside collapsed evidence.
When the fixture exists, `/actions` also shows `Current Demo Action Surfaces`
with links to the selected project, delegation, workflow, run, approvals, and
inbox surfaces.

Use `/approvals` when you want to keep driving the gate sequence from one
queue, and use `/approvals?run_id=<coder_run_id>` when you arrived from a run
gate and want that run's pending commit or publication decision foregrounded
even if unrelated approvals also exist. The page now opens with the
`Approval Operator Workbench` before shared route/focus diagnostics or command
readback, showing do/inspect/Goal/finish cards, the first pending decision, the
parent Goal when known, request and evidence artifact links, confirmation
posture, and a collapsed confirmed `save-workspace` form so an approval queue
can become tomorrow's resume point without writing on GET. The Goal card and
goal links are title-first when the parent Goal has a title, while raw Goal ids
remain in the collapsed evidence fields for durable review. The read-only
`Approval Queue Command Bar` follows with total pending worktree, commit, and
publication decisions, the scoped or global first recommended decision, the
same-page form target, the follow-up after approval, and the zero-effect
boundary inside collapsed evidence. The read-only `Approval Decision Brief`
then turns the first recommended decision into visible Decision, Inspect,
Evidence, After, and Safety cards before collapsed evidence for the relevant
delegation, workflow, run when one exists, request artifact, evidence artifact,
form anchor, post-decision surface, and no-write/no-network/no-external-effect
boundary. A browser-local `Approval Queue Filter` follows, narrowing
already-rendered approval rows by worktree, commit, publication, scoped Goal,
scoped run, or text and restoring lane/query from
`localStorage:clankeros-approval-queue-filter` without deciding or approving
anything. Pending commit and publication approvals link back to the relevant
run and name the next local-only follow-up action after
approval, including the typed commit-message requirement and the manual
push/PR boundary.

Use `/inbox` when you want the read-only operator queue. Pending commit and
publication items include the same run links and next-action cues, but the
actual decision forms stay on `/approvals` and the state-aware run detail
pages. The page now opens with the `Inbox Operator Workbench` before shared
route/focus diagnostics or command readback, so the first screen is the next
queue action. Its do/inspect/Goal/finish cards resolve Goal, delegation, run,
evidence, and continuation surfaces when available, and include a confirmed
`save-workspace` form in a collapsed Finish Today section so the queue can
become tomorrow's resume point without writing on GET. Goal cards and queue
goal links are title-first when possible, while raw Goal ids and label-source
evidence stay available in the collapsed readback. A visible read-only
`Inbox Triage Board` follows with Attention, Decisions, Work, Publication,
and Finish Today lane cards, turning the long queue lists into count-backed
first targets before dense evidence. A read-only `Inbox Next Item Brief`
then turns the first queue item into Next, Inspect, Evidence, After, and
Safety cards, so an operator can see the immediate click, inspection surface,
bounded artifact target or queue fallback, and follow-up without opening the
long lists. The read-only
`Inbox Command Bar` follows with total local queue size, counts by queue type,
the first attention item, its target section, and the no-write/no-network
boundary inside collapsed evidence. A browser-local `Inbox Queue Filter` then
narrows already-rendered inbox rows by lane, current route scope, or text,
remembers lane/query in `localStorage:clankeros-inbox-queue-filter`, and resets
without deciding, approving, executing, or calling providers.

Use `/verification` when you want the local-vs-GitHub testing split in one
place. It reads the checked-in GitHub Actions workflow, lists the compact local
checks to run before a push, and states that CI proof requires a completed
passing GitHub Actions run. It also shows the configured job timeout, the
latest operator-supplied CI evidence record when one exists, and makes clear
that an in-progress GitHub run is pending proof, not CI proof, so you can wait
on GitHub instead of rerunning the full suite locally. It also shows a
copyable `ci-snapshot-handoff` template for the current checkout so you can
watch a direct pushed-snapshot run and then record it after success. The page
itself does not contact GitHub. A `Verification Operator Workbench` now leads
the page with Now, Check GitHub, Proof, and Finish Today cards so the next
operator action is visible before the workflow inventory. Detailed workbench
evidence and the save form stay collapsed by default while still preserving
the current proof posture, target action, and zero-effect readbacks in the
DOM. A visible read-only `Verification Proof Map` follows with Current, Fast
Smoke, Full Suite, Record, and Boundary cards, making the early-smoke versus
full-workflow proof split explicit before the command details. The read-only
`Verification Command Bar` follows as evidence and usually points to
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
template instead. The page now starts with a read-only `CI Proof Workbench`
before shared diagnostics, with four scannable cards: check the pushed run,
record fast-smoke proof, record full-suite proof, or fall back to manual
record-after-success. Each long GitHub command is available through a compact
per-card command disclosure. Summary rows, proof workbench evidence, and the
`CI Evidence Command Bar` evidence stay collapsed by default while preserving
handoff/snapshot counts, proof source/status/scope, current proof posture, one
next action, same-page targets, the direct `ci-snapshot-handoff` template, and
the exact `gh run view` / validated recorder commands in the DOM. A
browser-local `CI JSON Assistant` follows with copy buttons for the current
`gh run view` JSON command, optional clipboard paste into the recorder
textarea, and quick job-name fill buttons for fast-smoke or full-suite proof.
Fast-smoke proof remains labeled as early route/CLI proof only. It does not
fetch GitHub status.

The app is local-only by default, binds to `127.0.0.1`, and refuses non-local
binds unless `--allow-nonlocal-bind` is explicitly supplied. It does not push,
create PRs, deploy, call providers, or perform network actions beyond local
browser/server loopback. Confirmation pages show submitted payloads before
local writes. They now start with a read-only `Action Preflight` that shows the
local action, return route, expected local write, submitted project/Goal
context, field count, and safety boundary before the existing read-only
`Action Confirmation Review` cards and payload. The existing `Action
Confirmation Command Bar` remains as collapsed evidence, preserving the action
kind, required input, output artifact, local mutation/execution posture, and
no-provider/no-network/no-push boundaries before the final `confirm=yes`
submit. Confirmed actions now return an
action-first `Action Complete` surface before the raw details, with visible
Continue, Completed, Artifact, Workflow, and Boundary cards plus collapsed
result-command evidence preserving the target notice surface, result, primary
artifact, confirmation source, and zero-effect counters. An `Action Resume
Receipt` follows immediately, reading `.clanker/app/workspace.json` back as
visible Resume, Context, Artifact, Last Action, and Boundary cards with
collapsed evidence for the saved project, Goal, exact `resume_surface`, latest
artifact, updater, last action/result, readiness, and zero-effect counters. The existing
`Action Result Details` section remains below it with the payload, result
fields, artifact links, next-page link, and safety boundary. Successful
results also show an
`Action Continuation` block from the
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
next-page link now opens an action-first `Action Notice` surface on the
target page, with visible Continue Here, Last Action, Resume, Details, and
Boundary cards plus collapsed notice/workspace evidence so the operator can
continue without reconstructing context from a plain banner. Action errors now
open with an action-first
`Action Needs Attention` recovery surface before the raw error details, with
Fix Input, Retry Surface, Error, Catalog, and Boundary cards plus collapsed
error evidence proving no result was recorded and no external effect was
created. The dashboard and `/health`
surface the same warning posture for non-local binds, dirty tracked files,
ahead-of-origin state, and known duplicate untracked files. `/health` starts
with a `Health Operator Workbench` that turns warning count, bind scope,
branch/commit, storage and workflow-import readiness, the refreshed local
status artifact, the fact that the artifact is written on GET, one next local
surface, and zero provider/network/external-effect counters into visible
operator cards before the collapsed command and diagnostic evidence. Stop it with
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
