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

- `/` - Goal-First Home dashboard. It renders the Home operating surface
  before the shared route/focus diagnostics, keeps Home state and board
  evidence collapsed by default, and starts with a read-only
  `Home Operator Board` that turns the lead Goal or first-run step into
  visible Do Now, Attention, Resume, and Proof cards with scoped approval
  links, direct action-form targets, Finish Today resume routing, and local CI
  proof surfaces. It also includes active, paused, and completed goal lanes,
  recent activity, the operator inbox, open recommendations, open incidents,
  saved workspace resume links, saved-goal phase and next-action readbacks, a
  `Home Day Plan` readback for the current goal, phase, one next action,
  waiting counts, and end-of-day resume readiness plus a confirmed
  `save-workspace` Finish Today form for the lead goal, a read-only
  `Home Live State` panel with five-second local page reload polling that
  pauses while a form is focused or the tab is hidden and reports zero
  provider/network/external-effect counters, a read-only `Home Attention Brief` that prioritizes approvals,
  incidents, recommendations, inbox review, and CI proof posture before deeper
  goal work, a `Home Focus Queue` for next actions across active and paused
  goals, a read-only `Home Activity Command Bar` that names the latest
  human-readable event and target surface across current goals, the same
  confirmed local action form as the Goal page when the saved
  goal's next action is browser-available, an explicit `save-workspace` form
  for the current lead goal when one exists, and first-run project/goal forms
  when no goals exist. Home's live state, Start Here, Day Plan, Attention
  Brief, and Focus Queue point directly to the same-page `Create Project` or
  `Create First Goal` form in first-run states instead of detouring to
  `/goals`. The `First Run Guide` starts with a read-only
  `First Run Command Bar` that names the next first-run action, target
  surface, form surface, Goal/delegation context, and zero-effect counters; once
  a Goal exists, it can render the same confirmed local next-action form inline
  for the scout delegation, context-pack, and first delegation run gates.
  Confirmed
  `register-project` and `create-goal` browser actions also update
  `.clanker/app/workspace.json`, so `/resume` can restore the new project or
  goal without a separate manual save step. After `register-project`, the
  local `Action Result Details` page also reads first-run progress and renders
  an inline confirmed `create-goal` continuation, plus Home and Today fallback
  links, so the operator can continue before a saved Goal exists.
- `/today` - daily command center for the current operating day. It is
  content-first and command-center-first: shared route/focus diagnostics render
  after the daily cockpit, while Today state, command, and workbench evidence
  stay collapsed by default. It starts with a read-only six-card
  `Today Command Center` that selects the lead Goal or first-run step, shows
  the current phase, one primary action, target surface or same-page
  current-action form, attention routing for approvals, incidents,
  recommendations, and inbox items, resume readiness, and CI proof posture.
  Confirmed `save-goal-note`, `pause-goal`, and `Finish Today`
  `save-workspace` forms are also collapsed by default and open from their
  visible command cards or direct hash links. A
  read-only `Today Live State` panel follows with five-second local page reload
  polling that pauses when the tab is hidden or a form field is focused and
  reports zero provider/network/external-effect counters. A read-only
  `Today Session Summary` follows with the current goal or first-run step,
  current gate, next surface, latest activity, latest artifact, workspace
  resume posture, and recorded CI proof in a single return-to-work brief. A
  read-only `Today Operator Workbench` follows with do/check/unblock/finish
  cards for the current action, timeline/evidence review, first blocker, and
  finish-today resume save target. A read-only `Today Workflow Map` follows
  with the first-run gate rail when no Goal exists, or the lead Goal's local
  lifecycle gates, current gate, next action, same-page action target, and gate
  counts once a Goal exists. A read-only `Today CI Handoff` follows with the
  latest operator-recorded GitHub Actions proof, current-checkout match status,
  exact `gh run list` / `gh run view` commands for current CI, and links to
  `/verification` plus `/ci-evidence` for recording proof once Actions
  completes; it reports that the app does not poll GitHub or write on GET. A
  read-only `Today Goal Queue` follows with active/paused/completed counts,
  lead-goal phase and next action, switch links, lead same-page action-form
  availability, progress, and waiting counts across the day's goals. When no
  Goal exists yet, the command center, queue, Start Here panel, and reused
  Home Day Plan link directly to the same-page `Create Project` or
  `Create First Goal` form rendered by the first-run guide instead of
  requiring a detour to `/goals`. It then reuses the existing Start Here,
  Home Day Plan,
  Attention Brief, Focus Queue, recent activity, inbox, recommendations,
  incidents, and first-run panels without writing on GET or adding new action
  authority.
- `/resume` - read-only return-to-work surface for the saved
  `.clanker/app/workspace.json` state. It opens with a primary return link and
  `Resume Operator Workbench` before shared route/focus diagnostics or command
  readback, links the saved goal, project, and last artifact, preserves filters
  and expanded panel readbacks, and keeps saved-state, command, and workbench
  evidence collapsed by default. The workbench turns the saved context into
  do/check/unblock/finish cards, same-page action-form routing, blocker
  routing, last-artifact readback, and a `/workspace#save-workspace` finish
  surface. A read-only `Resume Command Bar` follows with readiness, current
  phase/gate, one next action, target surface, action-form availability, last
  artifact, and zero-effect counters inside collapsed evidence. It includes a
  `Resume Readiness` checklist for the saved project,
  goal, filters, expanded panels, last artifact existence, and next local
  surface, shows the saved goal's current phase and one next action in
  `Resume Next Action`, renders the same confirmed local action form as the
  Goal page when that action is browser-available, includes a read-only
  `Resume Workflow Map` with the saved goal's current gate, lifecycle
  progress, next surface, and zero-effect counters, points back to
  `/workspace` for edits, and writes nothing on GET. Before a saved Goal
  exists, `/resume` follows first-run progress instead: an empty checkout
  points at Home's `Create Project` anchor, a registered-project/no-goal
  workspace points at Home's `Create First Goal` anchor while still linking
  the saved project, and the command bar, workbench, readiness, next-action,
  and workflow-map sections all show the same first-run gate and setup target.
- `/` includes a confirmed `refresh-dashboard-state` action that rewrites the
  local `.clanker/app/local_app_status.json` artifact from current repository
  and route state without providers, pushes, PRs, deploys, or external
  mutations.
- `/` also includes a read-only state-aware `Next Recommended Action` panel
  that points to the highest-priority local operator surface, such as
  incidents, approvals, a reviewed coder run needing a commit request, a
  publication handoff, project state, or the demo/onboarding page.
- `/` also includes a read-only `Start Here` cockpit near the top of Home that
  condenses the lead goal or first-run step, one primary action, target
  surface, resume readiness, waiting counts, and CI handoff posture into a
  single scan-friendly panel without writing on GET; in first-run states the
  target is the same-page `Create Project` or `Create First Goal` form.
- `/` also includes a read-only `Home Live State` panel that keeps the root
  goal board current with five-second local page reload polling, pauses while
  editing or hidden, points at the same-page first-run form before a Goal
  exists or the same-page Home Resume Action Form when a saved goal has a
  browser-available next action, and reports zero-effect
  counters.
- `/` also includes a read-only `Home Verification Handoff` that brings the
  GitHub Actions handoff onto the daily Home board: current branch/commit,
  direct snapshot command templates, latest operator-supplied CI evidence
  when one exists, and zero app-side GitHub polling, provider, push, PR,
  deploy, or external-mutation effects.
- `/` also includes a read-only `Verification Snapshot` that summarizes the
  checked-in workflow timeout, latest operator-supplied CI evidence when one
  exists, and links to `/verification` plus `/ci-evidence` without polling
  GitHub status.
- `/` also includes a read-only `Goal Snapshot` that links to `/goals`, counts
  active/paused/completed goals, and names the lead goal phase plus next
  action when goal state exists. Home goal lanes use the shared goal row
  summary with task progress plus open task, incident, and recommendation
  counts.
- `/goals` - daily goal cockpit. It separates active, paused, and completed
  goals, links to each goal detail page, and keeps phase, next action, task
  progress, open task/incident/recommendation counts, and first-run browser
  actions visible. A read-only `Goal Board Command Bar` summarizes total goal
  counts, the prioritized saved or active Goal, its phase, one next action,
  target surface, waiting counts, resume route, action availability, and
  write/network/external-effect counters. A `Goal Board Workbench` follows
  with Do Now, Selected Goal, Attention, and Start/Resume cards, including
  direct links to the selected Goal's confirmed action form, scoped
  `/approvals?goal_id=<goal_id>` attention routing, lane anchors, and
  `/resume`. The page exposes a confirmed local `Start Another Goal` form for
  registered projects, plus
  confirmed local `register-project` and `create-goal` forms for a fresh
  checkout.
- `/goals/<goal_id>` - goal-centered workbench that opens with the large
  Current Phase banner immediately after the Goal summary, then shows an in-flow
  read-only `Goal Jump Bar` for phase, action, workflow, timeline, evidence,
  artifacts, notes, git, and remaining work. Its visible `1`-`9` key badges
  and `aria-keyshortcuts` jump to those local anchors without submitting
  forms, then a compact fixed desktop `Goal Action Dock` keeps the current action,
  gate, CI proof target, and resume route visible while jumping directly to the
  existing confirmed Goal action form when one is available and becomes static on
  narrow
  screens. The dock appears before the Goal
  Command Bar, Goal Operator Workbench, Goal Daily Loop, Goal Return Brief,
  Goal Continuation Rail, next action, next recommendation, Goal Workflow Map,
  Goal CI Handoff, live state, and section index before the detailed overview, goal risk, completion criteria,
  progress, chronological timeline, activity log, delegations, runs, approvals,
  evidence, artifacts, memory, skills used, git status, operator notes, a
  goal-scoped resume snapshot, and remaining work. The timeline starts with a
  read-only `Goal Timeline Command Bar` that shows total events, the latest
  event, event-family counts, target surface, and zero-effect counters before
  the full chronological list. Each timeline and Activity Log event renders
  with a time, event-kind badge, clickable local message, and target badge so
  artifacts, delegations, runs, approvals, and goal events are easier to scan
  without reading raw logs. It uses local polling
  refresh, pauses refresh while the
  operator is editing a form or the tab is hidden, and does not contact GitHub
  or providers. The Current Phase banner is the primary operator state readback:
  it shows the large phase label, reason, operator attention cue, next surface,
  latest activity, and zero-effect boundary so the operator knows what is
  happening without opening the CLI. A read-only `Goal Command Bar` appears
  above the detailed cards with the current phase, one primary action, target
  local surface, progress, open/waiting counts, resume route, project-scoped CI
  proof state, and write-on-GET/network/external-effect boundaries. A
  `Goal Operator Workbench` follows with a human-readable do/check/unblock/
  finish strip, with its primary action jumping directly to the in-page
  action-form target when available, the
  source surface, current gate/progress, first unblock surface, and confirmed
  local-action counters before the longer diagnostic sections. The Goal Next
  Action section starts with a human-first focus strip for Now, Gate, Target,
  and Boundary, with one primary link to the existing confirmed form or source
  surface, then renders the confirmed form before collapsed action evidence.
  The in-flow Goal Jump Bar keeps the main
  daily anchors one click or keypress away without covering later controls, and
  the Goal Action Dock keeps the current action reachable from deep scroll
  positions by jumping directly to the confirmed form without adding a second
  action form. The Goal Section Index links
  directly to the Timeline, Activity, and Git command bars as well as the
  detailed sections, so long Goal pages remain navigable from their scan-first
  operator surfaces. Goal
  Overview starts with a read-only `Goal Overview Command Bar` that condenses
  identity, status, phase, risk, progress, task/delegation/run/approval counts,
  the next click, and zero-effect boundaries before the raw goal metadata. Goal Risk
  starts with a read-only `Goal Risk Command Bar` that summarizes risk
  level, task risk counts, approval-boundary posture, first task risk/status,
  one next local surface, and zero-effect counters before the detailed risk list.
  Goal Completion Criteria starts with a read-only `Goal Criteria Command Bar`
  that summarizes criteria source, item count, progress, plan/contract
  posture, first acceptance item, one next local review surface, and
  zero-effect counters before the detailed criteria list. Goal Progress starts
  with a read-only `Goal Progress Command Bar` that summarizes task completion,
  workflow gate progress, current gate, waiting approvals/incidents/
  recommendations, one next local action, and zero-effect counters before the
  browser progress bar and detailed counts.
  `Goal Completion Readiness` follows the local gate, approval, incident, and
  publication-handoff state to say whether the goal is completed, blocked,
  waiting for operator approval, still missing evidence, or safe to complete
  after manual publication. It links the next local surface and only renders
  the confirmed `complete-goal` form when the manual publish handoff is ready.
  A
  read-only `Goal Git Command Bar` inside Git Status summarizes the registered
  project root, branch, commit, clean/dirty posture, tracked and untracked
  counts, latest goal-linked `git_status.txt` artifact, and one next local
  surface without fetching GitHub status or mutating the repo. A
  `Goal Daily Loop` follows it with start, continue, unblock, and finish cues
  sourced from the Goal, workspace, approval, incident, and recommendation
  state, including whether tomorrow's resume anchor still needs saving, plus a
  confirmed local `pause-goal` form for non-paused incomplete goals and a
  confirmed local `save-workspace` form that writes only
  `.clanker/app/workspace.json` after confirmation. The pause action only
  changes local goal status to `paused`; it does not approve work, run work,
  call providers, use the network, push, create PRs, deploy, or mutate external
  systems. A read-only `Goal Return Brief` follows the daily loop and gathers
  the current gate, next local action, resume readiness, latest activity,
  latest artifact, CI proof posture, blocker route, `/resume`, and finish
  surface into one return-to-work snapshot without writing on GET. A read-only
  `Goal Continuation Rail` follows it with the current gate, the next few
  local gate actions, their operator surfaces, and the final manual publish
  boundary, so the Goal page can be followed as a short continuation path
  before the deeper diagnostics. The next
  detailed surface is a read-only `Goal Workflow Map` that turns the same
  Remaining Work gate state into a lifecycle rail from scout delegation through
  manual publish, with the current gate, next action, gate counts, every
  gate's eventual local operator surface, and zero-effect boundary visible
  before scrolling. A read-only `Goal CI Handoff` follows it with
  project-scoped proof status, latest operator-recorded GitHub Actions
  evidence, exact `gh run list` / `gh run view` command templates, and a
  same-page JSON paste target for recording proof without app-side GitHub
  polling. Remaining Work also starts with a read-only
  `Goal Remaining Work Command Bar` that summarizes the
  current gate, done/pending/waiting gate counts, open task/incident/
  recommendation counts, pending approvals, one next local surface, and
  zero-effect boundaries before the detailed checklist. The Next
  Recommendation section explains
  whether the Goal is following an open task recommendation or deriving the
  action from current phase and local goal records, then names the target
  local surface and zero-effect boundary without writing on GET. Skills Used
  starts with a read-only `Goal Skills Command Bar` that summarizes task skill
  tags, matching generated or available skill records, usage and project
  counts, delegation profile usage, one `/skills` or `/profiles` review
  target, and no-execution/no-install/no-network boundaries before the
  detailed skill readback. Goal Resume Snapshot reads `.clanker/app/workspace.json`, shows
  whether the saved workspace already points at the current goal, suggests the
  latest goal artifact as the resume anchor, renders saved filters, expanded
  panels, and last-viewed artifact as `Goal Workspace Restore State`, and
  exposes a confirmed `save-workspace` form that returns to the same goal page
  after saving without writing on GET. Operator Notes starts with a read-only
  `Goal Operator Notes Command Bar` that reports whether the note artifact
  exists, timestamped entry count, size, workspace resume-anchor posture, one
  review or capture target, and zero-effect boundaries before the confirmed
  `save-goal-note` form. The form appends local resume context to
  `.clanker/projects/<project>/goals/<goal>/operator-notes.md`; it does not
  overwrite previous notes. Saved operator notes also appear as linked
  `Operator note saved` entries in the Goal timeline and recent Activity Log,
  with a read-only `Goal Activity Command Bar` summarizing the latest event,
  target surface, operator-note count, artifact count, and zero-effect
  boundary so daily resume context is chronological instead of side-channel only. The
  Goal Delegations section starts with a read-only
  `Goal Delegation Command Bar` that summarizes scout delegation counts,
  context-pack readiness, implementation handoff readiness, coder-prep packets,
  worktree plans, the latest delegation workflow surface, and one next local
  continuation before the detailed delegation rows. The
  Goal Memory section links to `/memory`, shows
  project/global memory artifacts, goal-scoped memory entry counts, generated
  memory count, operator-note status, future-work count, and the current pin
  posture; it starts with a read-only `Goal Memory Command Bar` that chooses
  one next local memory action and reports zero-effect boundaries before the
  detailed readback. Pinning stays on the confirmed `/memory` action surface.
  Goal
  Runs starts with a read-only `Goal Run Command Bar` that summarizes task and
  worktree run counts, reviewed/blocked run gates, changed-file posture, the
  latest run surface, one next local run action, and zero-effect boundaries
  before the detailed run rows. Goal
  Approvals starts with a read-only `Goal Approval Command Bar` that summarizes
  pending and approved worktree, commit, and publication gates, links the next
  approval posture to `/approvals` or the relevant local Goal surface, and
  records zero write/provider/network/external-effect counters before the
  detailed approval rows. Goal Incidents starts with a read-only
  `Goal Incident Command Bar` that summarizes open/resolved incidents, open
  recommendations, the first incident's severity, run, task, evidence, one
  triage surface, and zero-effect counters before the detailed incident rows.
  Goal
  Evidence starts with a read-only `Goal Evidence Command Bar` that summarizes
  run evidence, worktree evidence, incident evidence, recommendation evidence,
  typed artifact counts, latest artifact, one local review target, and
  zero-effect boundaries before the detailed evidence list. Goal
  Verification Evidence starts with a read-only `Goal Verification Command
  Bar`, links to `/verification` and `/ci-evidence`, filters
  operator-supplied CI records to the current goal project, compares the
  recorded branch/commit to the current project checkout, distinguishes
  missing, stale, job-scoped early proof, and current full workflow proof, and
  reports `github_status_fetch: none` so missing or stale project proof stays
  visible.
  If a goal is explicitly paused, the Current Phase banner shows `Paused` and
  the Next Action card exposes a confirmed `resume-goal` form. That action
  only changes local goal status from `paused` to `active`; it does not resume
  blocked tasks, approve gates, run work, push, create PRs, deploy, call
  providers, use the network, or perform external mutations.
  When the
  goal has planned tasks but no
  delegation yet, the Next Action card exposes a confirmed `delegate` form
  that writes a read-only scout delegation contract without starting a
  subagent. After that, the same Next Action card exposes a confirmed
  `context-pack` form while the delegation has no context pack. Once the
  context pack exists, the card shows a confirmed `run-delegation` browser
  action plus the exact CLI fallback command. After a delegation completes,
  the card exposes confirmed `coder-prep`,
  `coder-worktree-plan`, and `coder-worktree-approval` forms at the matching
  workflow phases. It also exposes confirmed `approve-coder-worktree` and
  then a confirmed `run-coder-worktree` action once the worktree request is
  approved. The action names the approved plan, allowed-file preview,
  verifier, expected evidence path, return route, and safe-command validator
  before running one operator-provided local command after confirmation. The
  Goal card exposes `review-run` when the
  completed coder worktree run is blocked on the review gate, then
  `coder-commit-request` once the review exists and mentions the coder run.
  Once a commit request exists, the same Goal card can drive
  `approve-coder-commit`, `commit-coder-worktree`,
  `coder-publication-request`, `approve-coder-publication`, and
  `coder-publication-handoff` through confirmed local forms, then shows the
  manual publish boundary and copy-only publication handoff commands. After
  the operator finishes that manual push/PR work outside ClankerOS, the same
  boundary exposes a confirmed local `complete-goal` action that marks the
  Goal completed and moves it into completed-goal lanes. These create local
  artifacts, approval rows, approval decisions, one isolated local worktree
  commit, or local goal status only; they do not run delegations or worktrees
  from the browser, push, create PRs, deploy, call providers, or perform external
  mutations. Remaining Work starts with a read-only `Goal Remaining Work
  Command Bar` and then a gate-aware checklist sourced from local goal state:
  it shows the current recommended action, current gate, open task/incident/
  recommendation counts, pending approvals, and done/pending/waiting status
  for scout, context-pack, handoff, coder prep, worktree, review, commit,
  publication, and manual publish gates without taking any action.
- `/goals/<goal_id>` includes `Goal Section Index`, a read-only in-page map
  of stable anchors for summary, live state, command bar, workflow map,
  current phase, next action, next
  recommendation, timeline, artifacts, memory, skills, verification evidence,
  notes, and remaining work. The index writes nothing on GET and only helps
  the operator jump around the long Goal workbench.
- Every app page includes a shared operator shell with a global
  `Operator Focus` strip, a read-only `Route Context` breadcrumb strip, recent
  local items, a command palette, a dark/light theme toggle, and keyboard
  shortcuts for home, goals, and palette search. After a confirmed local
  action, the shell renders a read-only `Last Action` strip from
  `.clanker/app/workspace.json` with the action kind, result, target notice
  surface, saved project/goal context, timestamp, and no-write/provider/
  network/external-effect counters. The route context strip now opens with a
  compact action-first focus grid for the current page, next local action, back
  target, Goal, Project, and `/resume`; route family/path, saved workspace
  anchors, focus target, and zero-effect counters stay available inside
  collapsed `Route evidence` before the page body. The recent-items sidebar
  starts with a read-only `Recent Items Command Bar` that shows one compact
  reopen action plus `/resume`, then keeps workspace/goal/delegation/run
  counts, saved project/goal/artifact context, the last confirmed action, and
  write/provider/network/external-effect counters inside collapsed evidence,
  with the remaining recent shortcuts in a second collapsed disclosure. The focus strip is derived from the saved
  workspace goal or current lead goal and now opens with compact action cards
  for primary action, phase, progress, waiting counts, and `/resume`, followed
  by the expandable confirmed local action form when the current next action is
  browser-available and collapsed `Focus evidence` for the full readback and
  zero-effect counters. When no Goal exists yet, the shared
  shell treats that as first-run progress, so Home, Today, and Goals point the
  route context, command palette, and Operator Focus at their same-page
  `Create Project` or `Create First Goal` forms, and other pages link back to
  the Home/Today/Goals first-run anchors. The command palette starts with a
  `Palette Focus` launcher for continuing the current Goal action, jumping to
  search, resuming the saved workspace, or staying on the current page. The
  route-aware `Current Page` readback, keyboard shortcuts, and long open list
  stay available inside collapsed `Palette evidence and shortcuts`; the
  goal-aware `Continue Current Goal` block, compact Goal continuation readback,
  and confirmed local action form remain directly below search. These controls
  only navigate local routes or submit existing local forms after confirmation.
- `/profiles` reads both `.clanker/profiles.yml` and SQLite profile rows. It
  shows configured profile names, storage-backed profile labels, modes, cost
  tiers, model placeholders, write posture, adapter status, and `use_for`
  labels while keeping `provider_routing_active=false` and
  `provider_calls_taken=0`. A read-only `Profiles Command Bar` summarizes
  configured, storage, enabled, disabled, future-lane, adapter, write-posture,
  and `use_for` counts, points at the first storage/configured/future profile
  review target, and keeps provider/model routing disabled.
- `/search` - bounded global search over indexed goals, projects, delegations,
  known artifacts, incidents, recommendations, memory, runs, approvals, and
  skill records. Goal results include live local phase, one next action, and
  remaining-work counts, so searches like `Ready to commit` or
  `Create commit request` return the relevant Goal. It is content-first and
  opens with a visible `Search Operator Workbench` before shared route/focus
  diagnostics, with cards for the current query, first useful hit, result
  list, and `/resume`. Search state, workbench evidence, and command evidence
  stay collapsed by default while preserving result counts by category, first
  result target, summary, and write-on-GET/network/external-effect/raw
  filesystem boundaries in the DOM. It does not expose arbitrary filesystem
  browsing.
- `/incidents` - read-only incident and recommendation triage. It starts with
  an `Incident Triage Command Bar` that summarizes open/resolved incident
  counts, open recommendation counts, the first local review target, evidence
  link, and write-on-GET/resolution/network/external-effect boundaries before
  anchored open incident, resolved incident, and task recommendation sections.
- `/workspace` - persistent local workspace state for open project, open goal,
  filters, expanded panels, and last viewed artifact. It now opens with the
  `Workspace Operator Workbench` before shared route/focus diagnostics or
  saved-state evidence, so saved workspace pages lead with do/check/unblock/
  finish cards, same-page action-form routing, blocker routing, last-artifact
  readback, and a Finish Today link that opens the collapsed `save-workspace`
  form. The read-only `Workspace Daily Brief` and `Workspace Workflow Map`
  follow with the saved goal's current gate, lifecycle progress, next surface,
  and zero-effect counters, while saved-state and restore-link readbacks stay
  inside collapsed evidence. Before a saved Goal exists, the same daily brief,
  workbench, continuation readback, restore links, and workflow map follow
  first-run progress: empty checkouts point to Home's `Create Project` anchor
  and registered-project/no-goal workspaces point to `Create First Goal` while
  preserving the saved project link. Home and `/resume` read the same saved
  state for daily resume links and continuation readbacks. The confirmed
  `save-workspace` form writes `.clanker/app/workspace.json`; GET requests
  write nothing.
- `/memory` - project memories, global memories, generated memories, proposed
  memories, operator notes, future-work recommendations, and confirmed
  `pin-memory` actions. It opens with a visible `Memory Operator Workbench`
  before shared route/focus diagnostics and command readback, with cards for
  the next memory action, proposed pins, operator notes, and `/resume` or goal
  context. Memory state, workbench evidence, and command evidence stay
  collapsed by default while preserving memory counts, the first proposed
  memory or fallback resume target, saved workspace context, and
  write-on-GET/provider/network/external-effect boundaries in the DOM.
- `/skills` - available/generated skill records with usage count, last-used
  readback, and projects using them. It now opens with a visible
  `Skills Operator Workbench` before shared route/focus diagnostics or
  command readback, with cards for the next skill review, generated skills,
  usage, and `/resume` or Goal context. Skills state, workbench evidence, and
  command evidence stay collapsed by default while preserving total, active,
  proposed, archived, generated, used-skill, project-usage, first-artifact,
  and zero-effect readbacks in the DOM.
- `/profiles` - inactive future provider-routing surface. It reads
  `.clanker/profiles.yml` when present, starts with a read-only
  `Profiles Command Bar`, and keeps provider calls and model routing at zero.
- `/workflow` - modern handoff/worktree/commit/publication workflow stepper,
  including `coder-prep-from-handoff` as the artifact-first prep route. Add
  `?delegation_id=<id>` or `?run_id=<coder_worktree_run_id>` to show selected
  workflow state, artifact status, approval/run/commit/publication status, and
  the next recommended local operator action. A read-only
  `Workflow Command Bar` starts the page with the selected delegation/run,
  parent Goal, project, current stage, next local action, target surface,
  reason, and zero-effect counters before the detailed evidence map. When a
  delegation or run is
  selected, each related workflow step also shows a `selected_status` token so
  the stepper itself can be scanned as the operator state map. Scoped workflow
  pages also render `Selected Workflow Continuation`, a read-only set of
  continuation links to the run detail, approvals queue, inbox, and dogfooding
  checklist with `external_effects_created: false`.
- `/actions` - read-only safe action catalog showing local app actions, where
  their forms appear, required previous artifacts, output artifacts,
  confirmation requirements, local mutation posture, and external-effect
  boundary. It opens with the safe action header and an `Action Operator
  Workbench` before shared route/focus diagnostics, deriving the current action
  from first-run or lead-Goal focus, linking the owning surface where the
  confirmed form lives, routing blockers to inbox/approvals/incidents, and
  providing a confirmed `save-workspace` finish form. A read-only
  `Action Catalog Command Bar` follows with visible Catalog, Forms, Approvals,
  and Boundary cards, while action counts, posture readbacks, and zero
  provider/network/external-effect counters remain in collapsed evidence. It
  also includes the confirmed
  dashboard status refresh form.
- `/verification` - read-only verification handoff showing the checked-in
  GitHub Actions workflow posture, compact local checks, remote full-suite
  boundary, and explicit CI non-claims without contacting GitHub.
- `/ci-evidence` - read-only CI/deploy evidence records that were already
  supplied by the operator with `ci-deploy-evidence`, including provider,
  status, external run id, URL, commit, and safe artifact links without
  fetching GitHub status.
- `/goals/<goal_id>#goal-verification-evidence` - shows the current goal
  project's latest local CI proof and provides a confirmed Goal-scoped
  `ci-snapshot-evidence-from-gh-json` form. The form accepts pasted GitHub
  Actions JSON, infers run id and URL from `databaseId`/`url`, validates the
  proof locally, records project-scoped CI evidence, and returns to the Goal
  page without app-side GitHub polling.
- `/dogfooding` - read-only manual browser checklist for refreshing the demo
  fixture, walking demo/workflow/project/delegation/run routes, using local
  commit and publication gates, and handing full-suite proof to GitHub Actions
  after a push without fetching GitHub status. It includes a copy-only
  `Dogfooding Command Bar` for fixture status, selected local demo objects,
  the one next surface, route/CI/action/health links, and zero-effect
  counters, plus a `GitHub Actions Follow-up` section with direct snapshot
  `ci-snapshot-handoff`, `gh run view`, and `ci-snapshot-evidence`
  record-after-success templates for the current checkout.
- `/projects` - project workflow index with a confirmed local
  `Register Local Project` form plus root path, default test command, current
  branch/commit, goal/task/delegation counts, next recommended local operator
  action, project detail links, and selected delegation/run workflow
  shortcuts.
- `/projects/<project_id>` - project detail with first-class project goals and
  a read-only `Project Command Bar` that summarizes branch/commit, active/
  paused/completed goal counts, task/delegation/run counts, pending queue
  counts, the next project action, the target local surface, and no-write/
  no-network/no-external-effect boundaries before the longer inventory. It
  also includes a `Project Operator Workbench` with Do Now, Goal, Unblock, and
  Finish Today cards, plus a confirmed `save-workspace` form that can make the
  project detail page the next resume point. The rest of the page includes a
  confirmed local `Start Goal For This Project` form, goal rows that link
  directly to `/goals/<goal_id>` with phase, next action, and task progress,
  goal-linked tasks, linked artifacts, project-scoped incidents/
  recommendations, next recommended operator action, and a project workflow
  launchpad that links the project to selected delegation/run workflow views,
  the safe action catalog, dogfooding checklist, and verification handoff.
- `/delegation-runs` - read-only delegation execution run index with a
  `Delegation Run Command Bar`, evidence directories, result artifacts,
  context-pack and implementation-handoff links, zero-effect counters, retry
  signals, and next recommended local operator actions. The command bar counts
  completed/pending runs, incidents, retry candidates, context packs, and
  implementation handoffs, then links the first local attention target to the
  run, delegation, and scoped workflow surfaces.
- `/delegations/<delegation_id>` - delegation, handoff, prep, worktree, commit,
  and publication state, including a compact workflow-readiness summary and
  next recommended operator action.
- `/runs/<run_id>` - run detail. For delegation execution run ids, the page
  shows scout evidence, result artifacts, context-pack and
  implementation-handoff links, zero-effect counters, retry signals, and next
  local operator action. For coder worktree run ids, it includes a
  read-only `Run Command Bar` that summarizes run status, review gate,
  commit/publication state, changed-file count, diff summary, next local
  action, target surface, and no-write/no-network/no-external-effect
  boundaries before the detailed evidence and forms. A `Run Operator
  Workbench` follows it with do/check/unblock/finish cards, same-page action
  anchors, review/evidence links, approvals, parent Goal, and a confirmed
  `save-workspace` form that stores the run plus review/evidence artifact as a
  future resume point without writing on GET. It also includes a read-only
  `Run Gate Map` with eight scan-first gates: review, commit request, commit
  approval, local commit, publication request, publication approval,
  publication handoff, and manual publish outside ClankerOS. The map marks the
  current gate, counts done/waiting/blocked gates, links only to existing app
  anchors or `/approvals`, and keeps all write authority in the existing
  confirmed forms. It also includes a `Run Workflow State` block for upstream
  context-pack, handoff, prep, plan, approval/run, bounded validation, commit,
  publication, and next-action status. Once a publication handoff is ready, the
  page also shows display-only suggested push and draft-PR commands plus the PR
  body path; those commands remain manual actions outside ClankerOS.
- Coder worktree run rows in the app include `changed_files_count` and a
  compact `diff_summary` read from existing `diff.patch` evidence, so the
  operator can scan change size without opening the artifact first.
- `/goals/<goal_id>` also includes a typed `Goal Artifact Explorer`. It groups
  goal-linked Markdown, JSON, Patch/Diff, and Text/Log artifacts and links each
  item through `/artifacts?path=...`; it does not expose raw filesystem
  browsing. The artifact area starts with a read-only
  `Goal Artifact Command Bar` that summarizes artifact record counts,
  available/missing posture, render-family counts, source-family counts, the
  latest artifact, one bounded review click, and zero-effect counters before
  the detailed artifact list and typed explorer. The Goal timeline backfills
  generic `Artifact recorded` entries
  from the same bounded artifact registry after workflow-specific timeline
  events are added, so artifacts such as context-pack JSON, handoff JSON,
  diffs, changed-file lists, and git-status logs appear chronologically. The
  `Goal Timeline Command Bar` keeps the latest linked event and event-family
  counts visible before that longer list.
- `/inbox` - read-only operator queue for steering reviews, approval requests,
  incidents, delegations, coder runs, commits, and publication handoffs.
  It opens with the `Inbox Operator Workbench` before shared route/focus
  diagnostics or command readback, with do/inspect/Goal/finish cards for the
  first attention item, Goal/delegation/run/evidence routing when available, a
  continuation surface, and a confirmed `save-workspace` form in a collapsed
  Finish Today section that can store the queue as a resume point without
  writing on GET. The read-only
  `Inbox Command Bar` follows with total local queue size, counts by queue
  type, the first attention item, target section, reason, and
  write-on-GET/network/external-effect boundaries inside collapsed evidence.
  Pending commit and publication rows include run links, approval-queue links,
  and next-action cues without exposing decision forms on the inbox page.
- `/approvals` - pending worktree, commit, and publication approvals. A
  read-only `Approval Queue Command Bar` summarizes total pending decisions,
  pending counts by approval type, the first recommended decision, the
  same-page form target, the follow-up after approval, and the zero-effect
  boundary. An `Approval Operator Workbench` follows it with
  do/inspect/Goal/finish cards, the first pending decision, parent Goal,
  request/evidence artifacts, confirmation posture, and a confirmed
  `save-workspace` form that can store the queue as a resume point without
  writing on GET. A read-only `Approval Decision Brief` expands the first
  decision into direct delegation/workflow/run links, request and evidence
  artifacts, the exact form anchor, the post-decision surface, and explicit
  write/network/external-effect counters. Commit and publication rows link
  back to the relevant run and show the next local-only follow-up action after
  approval.
- `/incidents` - recent local incidents and evidence links.
- `/artifacts?path=<relative_path>` - safe read-only artifact viewer.
- `/health` - Python, git, storage, command, import, route, and counter health.
  A read-only `Health Command Bar` starts the page with local readiness,
  warning count, bind scope, storage/import posture, the refreshed status
  artifact link, explicit `status_artifact_write_on_get=true`, one next local
  surface, and zero provider/network/external-effect counters.
- `/demo` - demo scenario instructions plus a read-only `Demo Command Bar`
  that exposes fixture status, the preferred `python3 -m agent_os.cli demo`
  command, compatibility command, selected project/Goal/delegation/run, next
  local surface, and zero-effect counters before the state-aware dogfooding
  links and browser-progress checklist. The demo page also includes
  `Demo Gate Artifacts`, a read-only artifact map for the selected fixture
  run's commit request,
  commit decision, local commit, publication request, publication decision,
  publication handoff, and PR-body artifacts as they become available. `Demo
  Gate Actions` names the current local gate, the form action, required input,
  expected output artifact, and renders the safe confirmed local form for that
  gate when one exists. `Manual Browser Checkpoints` lists route markers for
  the first visual pass.

## Demo Scenario

```bash
python3 -m agent_os.cli demo
```

Compatibility aliases:

```bash
python3 -m agent_os.cli app-demo
python3 -m agent_os.cli demo-app-scenario
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
confirmation page and existing local safety checks. Once the publication
handoff is ready, the demo gate keeps push/PR work as a manual action outside
ClankerOS, then renders the confirmed local `complete-goal` form and advances
the demo to `review_completed_goal_evidence` after the Goal is completed.
`Manual Browser
Checkpoints` lists the route markers to confirm during the first visual pass,
including demo, dogfooding, project, delegation, scoped workflow, run,
approvals, inbox, verification, and health pages.

After publication handoff preparation, return to `/runs/<coder_run_id>` to see
`Publication Handoff Commands`: the suggested push command, draft PR command,
PR body path, and zero-effect counters. This is a copy-only operator readback;
the app does not run the commands. After those commands are handled outside
ClankerOS, return to the Goal page or `/demo` and use `complete-goal` to mark
the local Goal complete.

## Verification Handoff

`/verification` is a local read-only testing map. It reads
`.github/workflows/tests.yml`, shows whether push-to-main, pull-request, and
manual workflow triggers are configured, lists the separate fast smoke and
full-suite GitHub Actions jobs, and keeps the compact local checks visible. It
also shows the workflow job timeout, summarizes the latest operator-supplied
CI evidence record when one exists, and labels an in-progress GitHub run as
pending proof rather than CI proof:

A read-only `Verification Command Bar` appears before the workflow inventory.
It summarizes whether the workflow is configured, the current local checkout
commit when available, the latest recorded CI source/status/scope, whether
that evidence proves the current commit, the next proof action, and the target
surface. When proof is missing, stale, job-scoped, or the checkout commit is
unknown, the bar points to `/ci-evidence#record-ci-snapshot-json` instead of
asking the operator to rerun the full suite locally.

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
GitHub status JSON from stdin or a file, infers the run id and URL from
`databaseId`/`url`, refuses pending/failed or wrong-commit runs, and then
writes the same local direct-snapshot proof record. The root
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
handoff. A read-only `CI Evidence Command Bar` starts the page with handoff and
snapshot record counts, the latest local proof source/status/scope, whether it
matches the current checkout, and the one next recording or review action. The
bar links to stable same-page targets such as `#record-ci-snapshot-json`,
`#recent-ci-evidence`, and `#recent-direct-snapshot-ci-evidence`. The `CI
Proof Workbench` then presents the operator path as four scan-first cards:
check the pushed GitHub run outside ClankerOS, record job-scoped fast-smoke
proof, record full-suite proof, or use the manual record-after-success
fallback. It repeats the exact copy-only `gh run view` and validated recorder
templates, links back to the paste form, and labels fast-smoke proof as early
route/CLI proof only. The `CI Evidence Recording Guide` shows a handoff-specific
`ci-deploy-evidence` command when a local GitHub handoff exists, and a direct
`ci-snapshot-handoff`, `ci-snapshot-evidence-from-gh-json`, and manual
`ci-snapshot-evidence` command template when the operator is recording a
direct pushed snapshot. The page also has a confirmed
`ci-snapshot-evidence-from-gh-json` form where the operator can paste
`gh run view` JSON and optionally enter a completed job name such as
`Fast smoke verification`. If the JSON includes `databaseId` and `url`, the
run id and URL fields can stay blank. The app records local proof only after
it validates the supplied status, conclusion, commit SHA, branch, and, when
scoped, the named job status. Job-scoped fast-smoke evidence is early route/CLI proof, not
full-suite proof. The page does not poll GitHub, refresh statuses, push,
create PRs, deploy, call providers, or mutate external systems.

## Manual Dogfooding Checklist

`/dogfooding` is the first-stop browser checklist for a compact local pass
before pushing. It shows whether the fixture-backed `local-app-demo` state is
available, points to `/demo`, `/workflow`, `/projects`, `/delegation-runs`,
`/inbox`, `/approvals`, `/actions`, and `/verification`, and names the local
commit/publication gate sequence to walk from the selected `/runs/<run_id>`
page.

The page starts with `Dogfooding Command Bar`, a read-only scan surface for
fixture status, selected project/Goal/delegation/run, one recommended target
surface, demo command, route-walk/CI/action/health links, and zero-effect
counters. It also includes `Dogfooding Next Action`, a read-only state panel
that names the current fixture-backed next action and links the selected
project, delegation, scoped workflow, coder run, approval queue, inbox, action
catalog, and verification surfaces. The page reports zero app network actions,
zero external mutations, zero provider calls, no GitHub status fetch, and the
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
file size and truncation status. It also reports the render family, renderer,
raw-filesystem-browsing posture, and execution posture. Markdown artifacts are
rendered through a small escaped heading/list/paragraph view, JSON artifacts
are pretty-printed, patch/diff artifacts get line classes for meta/add/delete/
hunk scanning, and text/log artifacts render as inert text. Artifact content
is never executed. A read-only `Artifact Command Bar` now appears before the
content with the artifact path, type, renderer, size, rendered byte count, line
count, truncation state, inferred project/goal links when the path lives under
`.clanker/projects/<project>/goals/<goal>/`, workspace anchor status, one next
action, and write-on-GET/raw-filesystem/content-execution/network/external-
effect boundaries. The command bar links to `#remember-artifact` when the
artifact is not yet the saved resume anchor and to `/resume` once it is.
An `Artifact Review Brief` follows the command bar and summarizes whether the
artifact is goal-scoped, delegation-scoped, saved as the resume anchor, or
unclassified. It links goal-scoped artifacts back to the Goal and Project and
points unclassified artifacts toward the remember/resume workspace path before
the inert content renderer.

## Safe Actions

The `/actions` page is the first-stop safe action catalog. It maps low-risk and
local artifact-producing actions to the page where each form appears, the
required previous artifact, the output artifact, whether confirmation is
required, and the no-external-effects boundary. The page starts with the safe
action header and `Action Operator Workbench` before shared route/focus
diagnostics, turning current first-run or lead-Goal state into one local
action, the owning Goal/run/approval surface, blocker routing, and a confirmed
`save-workspace` finish point without submitting actions from the catalog page
itself. The `Action Catalog Command Bar` follows with compact
Catalog, Forms, Approvals, and Boundary cards; detailed action counts,
section anchors, local execution/git/approval/artifact posture, and zero
provider/network/external-effect counters stay in collapsed evidence. The app exposes these actions through explicit forms,
including context pack generation, coder prep, coder
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
The `/approvals` page is the gate queue for pending local decisions. Use
`/approvals?run_id=<coder_run_id>` from a run gate to foreground that run's
pending commit or publication approval before unrelated global queue items;
`/approvals?goal_id=<goal_id>` similarly scopes the first decision to a saved
Goal when possible. Pending commit approvals show the relevant run link, the
`commit-coder-worktree` follow-up, and the typed commit-message requirement.
Pending publication approvals show the relevant run link and the
`coder-publication-handoff` follow-up while preserving the explicit
`push_created=false`, `pr_created=false`, and `deploy_created=false` boundary.
The page starts with `Approval Queue Command Bar`, a read-only summary of total
pending decisions,
the first queue action, target section, after-decision guidance, and the
write-on-GET/network/external-effect boundary.
The `/inbox` page keeps the same commit/publication continuation cues in a
read-only queue form: it links to the run and approval queue and names the next
action after approval, but it does not render the approval decision forms.
Confirmation pages show the submitted action payload as visible read-only
fields plus the safety boundary before resubmitting with `confirm=yes`, so the
operator can review exactly what will be written before a local artifact,
approval, or bounded execution action runs. They start with a read-only
`Action Confirmation Command Bar` that summarizes the action category, source
surface, required input, output artifact, whether confirmation will mutate
local state or execute a safe local command, and the no-provider/no-network/
no-push/no-PR/no-deploy boundary. Confirmed actions render
`Action Result Details` with the
attempted action, submitted payload, result fields, artifact links when paths
are returned, a next-page link, and the safety boundary. They also render an
`Action Continuation` block from the refreshed saved goal state, including the
current phase, one next action, target surface, and the same confirmed local
action form when available, so the operator can keep moving without guessing
which page to open next. If there is no saved Goal yet, the continuation uses
first-run progress instead and can render the next confirmed first-run form
inline, such as `create-goal` after `register-project`, without writing on
GET. The result page also renders an `Action Result Workflow Map` from the
same refreshed state: it shows the first-run or saved-Goal gate rail, current
gate, next action, next surface, progress counts, and explicit
`manual_publish` boundary without creating actions, calling providers, using
non-loopback network, pushing, creating PRs, or deploying. Successful action
results are also remembered in `.clanker/app/workspace.json` and shown by the
global `Last Action` strip on later pages, so the operator can reopen the
target notice or `/resume` after navigating away. Following the
next-page link renders an `Action Notice` banner on the target GET page,
preserving the action result context while the operator reviews the dashboard,
run, delegation, or approval surface.
Failed actions render `Action Error Details` with the
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
local operator surfaces. The delegation run index now starts with a read-only
command bar and anchored attention, coder-prep-ready, and recent-run sections
so the operator can choose the next delegation/run surface without scanning the
full history. The delegation run index and inbox are read-only and mirror
operator-worthy queue and execution evidence without starting work, approving
requests, retrying tasks, committing, pushing, creating PRs, deploying,
calling providers, or using external network actions.

Worktree execution is exposed only as the confirmed `run-coder-worktree`
Goal action after an approved plan and safe-command validation. Push and PR
creation are never executed by the app.

## Health Artifact

Visiting `/health` or starting the app writes:

```text
.clanker/app/local_app_status.json
```

The status artifact records host, port, repo root, branch, commit,
dirty/untracked summaries, warning readbacks, routes, supported workflow
stages, non-claims, and known gaps. `/health` renders the same warnings for
non-local binds, dirty tracked files, ahead-of-origin state, and known
duplicate untracked files. The page now starts with a `Health Command Bar`
that makes the local status-artifact write explicit, links the artifact through
the bounded artifact viewer, and points either to warnings or `/resume` as the
next operator surface. The artifact does not include secrets.

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
