# Status Entry Point

The canonical chronological implementation log is [`../status.md`](../status.md).

Latest status focus:

- The local app now has a first-class `/guide` route in the main navigation.
  `Suggested Use Guide` maps the daily browser loop
  `Today -> Goal -> Action -> Proof -> Finish -> Resume`, points empty
  checkouts to the first-run browser path, points active work to the current
  Goal action form, and shows evidence for route state, counts, workspace
  resume state, and zero-effect safety on GET.
- The First Run Guide now includes a visible `First Run Empty State Map`:
  a text-only `Project -> Goal -> Delegation -> Context -> Run` illustration
  plus step cards between Next Step and Checklist, keeping empty checkouts
  scan-friendly with no state write, provider call, network action,
  approval/execution/push/PR/deploy, or external effect on GET.
- The shared browser shell now has first-class shortcut discovery: a visible
  `Keys` header control and `?` shortcut open a browser-local Keyboard
  Shortcuts dialog with the same shortcut list, no state write, no provider
  call, no network action, no approval/execution/push/PR/deploy, and no
  external effect on GET.
- The shared command palette now supports active-result keyboard navigation:
  `Palette Results` render as a local listbox, ArrowDown/ArrowUp move through
  visible local commands, Enter opens the active local route/anchor, and the
  Search button remains the explicit full indexed `/search` fallback. This
  keeps palette navigation browser-local with no server write, provider call,
  network action, approval, execution, push, PR, deploy, or external effect on
  GET.
- The first-run guide now includes a browser-local `First Run Checklist`
  between `First Run Next Step` and `First Run Progress`. It lets operators
  mark setup checks and save a short return note in
  `localStorage:clankeros-first-run-checklist`, exposes that state in
  `/workspace#workspace-view-memory`, and keeps real progress derived from
  ClankerOS state with no server write, provider call, network action,
  approval, execution, push, PR, deploy, or external effect on GET.
- `/today#today-goal-queue` now has a browser-local Find box, All / Active /
  Paused / Completed lane buttons, live match count, first-match link,
  no-match state, visible View status, and reload persistence via
  `localStorage:clankeros-today-goal-queue-view`. The saved queue view is now
  first-class in `/workspace#workspace-view-memory`, can be inspected or reset
  from there, and keeps GET rendering read-only with no server write, provider
  call, network action, approval, execution, push, PR, deploy, or external
  effect.
- `/goals/<goal_id>#goal-section-index` now remembers the section-finder query
  per Goal in `localStorage:clankeros-goal-section-finder:<goal_id>`, shows
  visible default/restored/saved/reset View status, exposes Reset section
  search, and can be inspected or cleared from
  `/workspace#workspace-view-memory` without server writes, provider calls,
  network actions, approvals, execution, pushes, PRs, deploys, or external
  effects.
- The root `/` `Home Goal Board` now has a browser-local Find box, lane mode
  buttons for all/active/paused/completed goals, live match count, first-match
  jump, no-match empty state, visible View status, and reload persistence via
  `localStorage:clankeros-home-goal-board-view`. It is resettable from
  `/workspace#workspace-view-memory` and keeps GET rendering read-only with no
  approval, execution, push, PR, deploy, provider call, network action, server
  write, GitHub polling, or external mutation.
- The command palette now adds `/today` section jump commands when the current
  route is `/today`, so typing for current action, goal queue, live state,
  session summary, activity digest, operator workbench, decision queue,
  decision filter, workflow map, CI handoff, or Finish Today opens the daily
  cockpit anchors directly. These are route-local links only and keep GET
  rendering read-only with no provider call, network action, write, approval,
  execution, push, PR, deploy, or external mutation.
- `/today#today-decision-filter` now narrows already-rendered Today Decision
  Queue rows by all, first-run action, current action, approval type,
  incidents, recommendations, blocked work, or local text search. It remembers
  lane/query for the daily cockpit in
  `localStorage:clankeros-today-decision-filter`, can be reset from
  `/workspace#workspace-view-memory`, and keeps GET rendering read-only with no
  decision, approval, execution, provider call, network action, push, PR,
  deploy, or external effect.
- `/goals/<goal_id>#goal-decision-filter` now narrows already-rendered Goal
  Decision Queue rows by all, current action, approval type, incidents,
  recommendations, blocked work, or local text search. It remembers lane/query
  per Goal in `localStorage:clankeros-goal-decision-filter:<goal_id>`, is
  discoverable through the Goal section index and command palette, can be reset
  from `/workspace#workspace-view-memory`, and keeps GET rendering read-only
  with no decision, approval, execution, provider call, network action, push,
  PR, deploy, or external effect.
- `/resume` now starts with a read-only `Browser Resume` panel that uses this
  browser's `localStorage:clankeros-route-history` to reopen the most recent
  non-resume route, reports route-scoped scroll/open-panel memory when present,
  falls back to the Goal cockpit, and keeps canonical resume state behind the
  explicit `/workspace#save-workspace` Finish Today form.
- Goal workflow forms now share the browser-local
  `localStorage:clankeros-action-form-draft:<action>:<scope>` draft system:
  worktree approval/run, commit request/approval, local commit, publication
  request/approval, and manual `complete-goal` notes/messages/commands restore
  after reloads, can be cleared from `/workspace#workspace-view-memory`, and
  are cleared after the submitted confirmed local action succeeds.
- First-run setup and daily Goal creation forms now keep unsent
  `register-project` and `create-goal` edits in browser-local
  `localStorage:clankeros-action-form-draft:<action>:<scope>` entries. The
  form drafts restore after reloads, can be cleared from the form or
  `/workspace#workspace-view-memory`, and are cleared after the confirmed local
  action succeeds.
- Goal and Today operator note capture now uses a multiline confirmed
  `save-goal-note` form with browser-local draft memory in
  `localStorage:clankeros-goal-note-draft:<goal_id>`, so unsent notes survive
  local reloads until cleared or until a confirmed note write updates the
  operator-notes artifact. `/workspace#workspace-view-memory` can inspect and
  reset these draft entries with the other browser-local view state.
- The shared app shell now remembers route-scoped scroll position in
  browser-local `localStorage:clankeros-scroll-position:<route>` after operator
  scrolling, restores long pages near the same working position on return, and
  skips restoration when a hash anchor is present. `/workspace#workspace-view-memory`
  can inspect and reset these entries with the other browser-local view state.
- The shared app shell now remembers route-scoped open/closed `<details>`
  panels in browser-local `localStorage:clankeros-open-panels:<route>` entries
  after a page has saved panel state, so evidence/detail panels survive local
  reloads on long operator pages. `/workspace#workspace-view-memory` can
  inspect and reset these entries without writing `.clanker/app/workspace.json`
  or touching providers, network, or external systems.
- The shared app shell now includes a browser-local `Viewed Pages` panel and
  palette integration backed by `localStorage:clankeros-route-history`, so
  operator route hops are searchable and reopenable without server writes,
  provider calls, network actions, or external effects.
- `/today` now includes a read-only `Today Decision Queue` after the Today
  Operator Workbench, showing exact daily rows for the current action plus
  pending approvals, incidents, recommendations, or blocked tasks while linking
  only to existing confirmed forms and scoped review surfaces.
- Goal pages now include a read-only `Goal Decision Queue` after Attention
  Digest, showing concrete Goal-scoped rows for the current action plus pending
  approvals, incidents, recommendations, or blocked tasks while linking only to
  existing confirmed forms and scoped review surfaces.
- Goal pages now include a read-only `Goal Activity Pulse` between Session
  Digest and Continuation Rail, showing Latest, Recent Three, Mix, Artifact,
  and Next cards from existing Goal timeline data before the full event list.
- Active first-run Goal pages now include a read-only `Goal First Run Rail`
  between Attention and the Goal Command Bar, keeping Project, Goal,
  Delegation, Context, and Run visible inside the Goal page and routing the
  current onboarding gate to the existing confirmed Goal action form.
- The command palette now adds focused Goal section jump commands to its local
  filtered results, so typing `timeline`, `approval`, `artifact`, `memory`,
  `git`, or `remaining` can navigate directly to the current Goal's core
  browser sections. These are local route/anchor links only and keep GET
  rendering read-only with no provider call, network action, or external
  mutation.
- Shared Recent Items now has a browser-local `Find Recent` filter that narrows
  already-rendered shortcut rows by local text search. It remembers query view
  state in `localStorage:clankeros-recent-items-filter`, exposes Reset filter,
  is included in `/workspace#workspace-view-memory`, and keeps GET rendering
  read-only with no server state write, provider call, network action, or
  external effect.
- `/profiles#profile-routing-filter` now narrows already-rendered profile
  routing rows/cards by all, Planning, Coding, Review, Docs, Cheap Model,
  Frontier Model, Storage, Configured, or local text search. It remembers
  lane/query view state in `localStorage:clankeros-profile-routing-filter`,
  exposes Reset filter, and keeps provider routing, model routing, writes,
  provider calls, network actions, push, PR, deploy, and external effects
  inactive.
- `/inbox#inbox-queue-filter` now narrows already-rendered inbox rows by all,
  attention, decisions, work, publication, scoped Goal, scoped run, or local
  text search. It remembers lane/query view state in
  `localStorage:clankeros-inbox-queue-filter`, exposes Reset filter, and keeps
  GET rendering read-only with no decision, approval, execution, provider
  calls, network actions, push, PR, deploy, or external effects.
- `/approvals#approval-queue-filter` now narrows already-rendered pending
  approval rows by all, worktree, commit, publication, scoped Goal, scoped run,
  or local text search. It remembers lane/query view state in
  `localStorage:clankeros-approval-queue-filter`, exposes Reset filter, and
  keeps GET rendering read-only with no approval, execution, provider calls,
  network actions, push, PR, deploy, or external effects.
- `/skills#skills-inventory-filter` now narrows already-rendered Skills
  Inventory rows by all, available, generated, active, proposed, used, or
  unused lanes plus local text search. It remembers lane/query view state in
  `localStorage:clankeros-skills-inventory-filter`, exposes Reset filter, and
  keeps GET rendering read-only with no skill install, execution, provider
  calls, network actions, raw filesystem browsing, or external effects.
- `/memory#memory-inventory-filter` now narrows already-rendered Memory Bank
  rows by all, proposed, active pins, project, global, generated, notes, or
  future-work lanes plus local text search. It remembers lane/query view state
  in `localStorage:clankeros-memory-inventory-filter`, exposes Reset filter,
  and keeps GET rendering read-only with no memory writes, provider calls,
  network actions, raw filesystem browsing, or external effects.
- `/workspace#workspace-view-memory` now exposes browser-local view memory
  for theme, focus mode, Goal board view, Home Goal Board view, open panels,
  scroll position, search lanes, timeline lanes, Goal section searches,
  decision filters, artifact filters, notes filters, note drafts, setup form
  drafts, Memory Bank filters, Skills Inventory filters, Approval Queue
  filters, Inbox Queue filters, and Profile Routing filters. It can refresh or clear those
  `localStorage` values after explicit clicks while preserving read-only GET
  behavior, `.clanker/app/workspace.json`, no raw filesystem browsing, and
  no-provider/no-network/no-external-effect boundaries.
- `/goals/<goal_id>#goal-operator-notes-browser` now renders existing
  `operator-notes.md` sections as scan-first note cards with local text search,
  visible View status, per-Goal browser-local query memory in
  `localStorage:clankeros-goal-notes-filter:<goal_id>`, and Reset notes while
  preserving confirmed-only appends, read-only GET behavior, no raw filesystem
  browsing, and no-provider/no-network/no-external-effect boundaries.
- `/goals/<goal_id>#goal-artifact-filter` now adds a browser-local Goal
  Artifact Filter at the top of the typed Goal Artifact Explorer. It narrows
  already-rendered artifacts by type, source, or text, remembers that view per
  Goal in `localStorage:clankeros-goal-artifact-filter:<goal_id>`, and
  provides Reset filter while preserving read-only GET behavior and
  no-provider/no-network/no-raw-filesystem/no-external-effect boundaries.
- `/search#search-result-filter` now adds a browser-local Search Result Filter
  after the Search Result Map. It narrows already-rendered results by all,
  goals, projects, work, decisions, knowledge, or artifacts, remembers the
  selected lane per query in
  `localStorage:clankeros-search-result-lane:<query-hash>`, and provides Reset
  lane while preserving read-only GET behavior and no-provider/no-network/
  no-raw-filesystem boundaries.
- `/goals/<goal_id>#goal-timeline-filter` now remembers the selected Timeline
  lane per Goal in `localStorage:clankeros-goal-timeline-lane:<goal_id>`, shows
  visible View status, and provides Reset lane while preserving read-only GET
  behavior and no-provider/no-network/no-external-effect boundaries.
- `/goals` active, paused, and completed lanes now render scan-first Goal cards
  instead of dense text rows. Each card links to the Goal, project, and current
  next-action surface while showing phase, progress, next action, waiting
  count, open work, and the legacy row text needed by filters and automation.
- `/goals` Goal Board Filter now includes browser-local sort controls for the
  already-rendered Goal cards. Operators can reorder each lane by updated time,
  waiting items, open work, progress, or title while preserving read-only
  GET behavior and no-provider/no-network/no-external-effect boundaries.
- `/goals` also remembers the Goal Board query, active/paused/completed mode,
  and sort in `localStorage:clankeros-goal-board-view` across reloads, with a
  Reset view button for clearing that browser-local board state.
- `/goals` now includes a browser-local `Goal Board Filter` after the goal
  creation form and before the active/paused/completed lanes. It filters
  rendered Goal rows by title, project, phase, status, next action, progress,
  and remaining work, supports all/active/paused/completed modes, updates a
  visible match count and first-match jump, and keeps writes, providers,
  network actions, and external effects out of the helper.
- `/goals/<goal_id>#goal-section-index` now includes a browser-local section
  finder with match count, first-match jump, compact anchor chips, per-Goal
  query memory in `localStorage:clankeros-goal-section-finder:<goal_id>`, and
  no-write/no-network posture so long Goal pages can be navigated by typing
  section names such as approval, memory, or git and restored after reload.
- `/artifacts?path=...` now renders stored Goal context title-first across the
  Artifact Operator Workbench, Relationship Map, Command Bar, and Review Brief.
  Raw Goal ids and label-source fields remain in collapsed evidence, and
  synthetic/orphan artifact paths keep their ID fallback behavior.
- The shared browser shell now turns saved `expanded_panels` into a
  `Workspace Panel Restore` strip on `/resume`, `/workspace`, and the saved
  Goal page. It shows direct links for saved panels such as Timeline and
  Evidence, auto-opens matching details only on the saved Goal page, and keeps
  GET requests read-only with explicit no-provider/no-network/no-external
  counters.
- `/goals/<goal_id>` now promotes open task recommendation commands into
  copy-only `Goal Recovery Commands` cards inside `Next Recommendation`.
  Operators can copy the stored `recommended_commands`, open the evidence
  artifact, and see explicit no-execute/no-retry/no-replan/no-write counters
  without leaving the Goal page. The Goal page's Next Action, header `Next`
  shortcut, attention digest, ribbon, daily loop, workbench, session digest,
  overview, incident, and remaining-work surfaces now route that state to
  `/goals/<goal_id>#goal-recovery-commands`, while `/incidents` remains the
  secondary triage surface.
- Goal Timeline now includes a browser-local `Timeline Lane Filter` after the
  digest and before metadata/the full list. It filters already-rendered
  `data-timeline-kind` rows by all, artifact, approval, delegation, run, task,
  note, or generic event, updates a visible count, and keeps persistence,
  provider calls, network actions, writes, and external mutation out of the
  helper.
- `/ci-evidence` now includes a browser-local `CI JSON Assistant` between the
  proof workbench and evidence summary. It copies the current `gh run view`
  JSON command, optionally pastes clipboard JSON into the confirmed recorder
  textarea, fills fast-smoke/full-suite job names, and keeps GitHub polling,
  recording, push, PR, deploy, provider calls, and external mutation outside
  GET and outside the helper.
- `/goals/<goal_id>` Remaining Work now includes a `Goal Task Closeout` panel
  before the detailed checklist. When ready publication-handoff evidence (or a
  completed Goal with the same evidence) exists, the confirmed
  `complete-goal-task` browser action marks one selected open task completed,
  updates a linked plan step when present, refreshes `TASKS.md`/`PLAN.md`,
  saves the resume point, and records a timeline event without fresh
  verification, approval, push, PR, deploy, provider call, network action, or
  external mutation.
- `/search` now indexes first-class operator approvals, not only legacy
  approval rows. Worktree, commit, and publication approvals appear in the
  Decisions lane and route to scoped `/approvals?goal_id=...`,
  `/approvals?run_id=...`, workflow, or run surfaces with zero-effect search
  evidence.
- The First Run Guide now includes a read-only `First Run Next Step` panel
  between the launchpad and progress strip. It gives fresh operators one
  primary same-page action for the current first-run gate, plus setup,
  handoff, resume, safety, confirmation, and zero-effect evidence.
- The shared browser shell now makes Finish Today route-aware. The header
  `Finish` control, `f` shortcut, Operator Ribbon, and command-palette Quick
  Switch open `#today-finish` on `/today`, `#goal-finish-today` on
  `/goals/<goal_id>`, and `/workspace#save-workspace` elsewhere. All routes
  still require the existing confirmed local `save-workspace` form before any
  write.
- `/resume` and `/workspace` now render same-page first-run continuation forms
  when no saved Goal exists. Fresh checkouts can register the project directly
  from Resume/Workspace, and registered-project/no-goal states can create the
  first Goal there, while Home/Today/Goals fallback setup links remain in
  collapsed safety evidence and GET requests stay read-only.
- `/workflow` now includes a read-only `Workflow Scope Picker` immediately
  after the `Workflow Operator Workbench`, with direct cards for the primary
  pickup, recent delegations, recent coder runs, parent Goal, and safety
  evidence before the journey rail.
- Confirmed local action result pages now include an `Action Resume Receipt`
  immediately after `Action Complete`, so operators can see the saved
  `.clanker/app/workspace.json` resume route, project/Goal, artifact, last
  action/result, updater, readiness, and zero-effect boundary before dense
  payload details.
- Confirmation pages now open with a read-only `Action Preflight` before the
  existing confirmation review. It turns the final browser safety checkpoint
  into visible Confirm, Returns, Local Write, Context, and Boundary cards,
  preserves submitted return route/project/Goal/artifact/field-count evidence,
  and still writes only after the final `confirm=yes` submit.
- The shared command palette now has a visible browser-local `Palette Results`
  list. Typing in `command-palette-search` filters local routes and recent work
  in place, shows a no-match state when needed, and keeps the existing Search
  button for full indexed `/search`; no writes, provider calls, network
  actions, or external effects are introduced.
- The shared browser shell now has a local Focus mode: the header `Focus`
  control and `m` shortcut persist `data-focus-mode="true"` in
  `localStorage:clankeros-focus-mode`, collapse Recent Items, Route Context,
  Operator Focus, and Last Action strips, keep the Operator Ribbon plus page
  body visible, and expose no-write/no-provider/no-network/no-external-effect
  evidence in the DOM.
- Goal Timeline now has a visible read-only `Goal Timeline Digest` after the
  Timeline Command Bar and before metadata/the full event list, with Span,
  Latest, Artifact, Next, and Safety cards plus collapsed item/gate/artifact/
  next-surface evidence.
- Saved workspace and return-to-work surfaces are now Goal title-first: Home,
  `/resume`, `/workspace`, Workspace Restore Map, and the Goal resume snapshot
  show human Goal titles for visible saved Goal links while retaining raw Goal
  ids plus label-source fields in collapsed evidence.
- `/inbox` and `/approvals` queue Goal links are now title-first: Inbox Next
  Item Brief, Inbox Operator Workbench, and Approval Operator Workbench show
  the human Goal title in visible Goal cards and links while retaining raw Goal
  ids plus label-source fields in collapsed evidence.
- `/goals/<goal_id>` now opens with a title-first Goal summary: the H1 and
  browser title use the human Goal title/intent, while the Goal id remains
  visible as metadata with project, status, phase, and local refresh evidence.
- Shared Goal navigation is title-first too: breadcrumbs, Route Context, and
  command-palette route evidence now show the human Goal title for visible Goal
  links while retaining explicit Goal id evidence fields.
- `/goals/<goal_id>` is now content-first in the shared app shell: the Goal
  summary, Current Phase banner, jump bar, action dock, and progress meter
  render before Route Context and Operator Focus diagnostics, so a direct Goal
  link opens on the actual working cockpit.
- `/goals/<goal_id>` now places a read-only `Goal Progress Meter` immediately
  after the Goal Action Dock and before deeper command surfaces. It shows task
  completion and workflow-gate progress bars, waiting operator items, latest CI
  proof posture, and the next confirmed browser action while preserving
  no-write/no-provider/no-network/no-external-effect evidence.
- `/goals/<goal_id>` now follows the progress meter with a read-only `Goal
  Attention Digest` that exposes Now, Approvals, Incidents, Recommendations,
  Open Work, and Safety cards before the Goal Command Bar, including the first
  waiting queue and zero-effect evidence.
- `/actions` now follows the Action Operator Workbench with a visible
  read-only `Action Workflow Map` for Setup, Scout, Context, Prep, Approval,
  Execute, Commit, Publish, and Proof. The map marks the current stage from
  the same first-run or lead-Goal focus context, links each stage to existing
  safe browser surfaces, and keeps no-write/no-approve/no-execute/no-network
  proof in collapsed evidence before the flat catalog.
- `/inbox` now follows the lane-level Inbox Triage Board with a visible
  read-only `Inbox Next Item Brief` for Next, Inspect, Evidence, After, and
  Safety. The brief turns the first local queue item into a single immediate
  click, inspection route, bounded artifact target or queue fallback, follow-up
  surface, and no-write/no-approve/no-execute/no-network boundary before the
  command evidence and long queue lists.
- Approval Decision Brief now opens with visible Decision, Inspect, Evidence,
  After, and Safety cards before collapsed approval decision evidence. The
  cards keep worktree/commit/publication decisions focused on the correct
  queue anchor, workflow or run inspection surface, bounded artifact evidence,
  post-decision local follow-up, and no-write/no-execute/no-network boundary.
- Skills Inventory now follows the visible `Skills Operator Workbench` with a
  read-only `Skills Usage Map` for Now, Available, Generated, Usage, Projects,
  and Safety before the dense skill lists. The map surfaces usage counts,
  project attribution, last-used posture, and the first bounded `/artifacts`
  skill artifact while keeping install/execution/provider/network/external
  effects unavailable.
- Home Attention Brief now opens with visible Now, Inbox, Approvals,
  Incidents, Recommendations, and Proof cards before the evidence readback.
  The cards reuse existing local surfaces (`/inbox`, `/approvals`,
  `/incidents`, `/verification`, or the first-run/goal next action), keep the
  read-only/no-provider/no-network/no-external-effect GET boundary, and expose
  card availability/count/surface evidence in the DOM.
- Home Recent Activity now opens with visible Latest, Goals, Artifacts, and
  Notes cards before the chronological list. Empty checkouts use real local
  fallback surfaces (`/goals`, `/search?q=artifact`, `/memory`), while
  populated demo data links directly to the latest timeline/artifact/note
  surfaces and keeps read-only/zero-effect evidence in the DOM.
- The First Run Guide now includes a visible read-only `First Run Launchpad`
  between the command bar and progress strip. Fresh operators can choose guided
  setup, demo, workflow, verification, or health without reading docs first.
  The launchpad is sourced from existing first-run state, keeps detailed status
  evidence collapsed, and preserves the no-write/no-provider/no-network/
  no-external-effect GET boundary while the existing confirmed forms remain the
  only write path.
- `.clanker/app/workspace.json` now treats `resume_surface` as a first-class
  saved local route. Confirmed `save-workspace` accepts it directly or derives
  it from `return_to`; `/resume` opens it as the primary return target; Home,
  `/workspace`, Recent Items, and the command palette show or prefer the exact
  saved surface while retaining `/resume` as the hub. `/workspace` now also
  shows a read-only `Workspace Restore Map` for Restore, Goal, Artifact,
  Filters + Panels, and Tomorrow so operators can see what is saved versus
  merely suggested before leaving. GET routes remain read-only.
- The shared browser shell now has a global keyboard-first next-action control:
  `n` opens the current recommended next-action target from the same
  saved-workspace or lead-Goal focus context as the ribbon and palette. A
  matching header `Next` control exposes the same safe target. When a
  browser-confirmed action form is available, `n` opens the existing
  `Operator Focus` details panel instead of submitting it, preserving the
  no-write/no-provider/no-network/no-external-effect GET boundary.
- The shared browser shell now has keyboard-first Workspace and Finish Today
  navigation: `w` opens `/workspace`, and `f` opens the route-local Finish
  Today form on Today/Goal pages before falling back to
  `/workspace#save-workspace`. Both shortcuts are discoverable in the command
  palette help and remain navigation-only; the actual workspace save still
  requires the existing confirmed form.
- Completed-action notice pages now open with a `Next Step` card that is
  sourced from first-run progress or saved-Goal state. The notice points
  directly at the next confirmed browser form or workflow surface, reports
  recommendation status/source/action/gate/confirmation evidence, keeps the
  clean-surface and last-action links, and preserves no-write/no-provider/
  no-network/no-external-effect boundaries on GET.
- The command palette `Quick Switch` now includes a fifth `Finish` card that
  uses the same route-aware Finish Today target as the header and Operator
  Ribbon, reports finish source/target/confirmation evidence, and keeps the
  launcher read-only until the existing confirmed workspace save form is
  submitted.
- `/workspace#save-workspace` now exposes first-class `Workspace save defaults`
  evidence. Empty first-run checkouts stay blank and read-only, saved
  workspaces stay authoritative, and fixture/lead-goal states prefill the
  confirmed Finish Today form from the current project, Goal, goal-scoped
  filters, panels, and latest artifact without writing on GET.
- Every route now gets a global read-only `Operator Ribbon` above the
  sidebar/page shell, with visible Now, Goal, Attention, Finish, Resume, and
  Search cards before any route-specific workbench. The ribbon is sourced from
  the saved workspace goal, current lead goal, or first-run state; it preserves
  the current route, phase, primary action, waiting counts, saved workspace
  context, the Finish Today confirmation surface, command-palette availability,
  and no-write/no-provider/no-network/no-external-effect counters inside
  collapsed evidence.
- `/goals/<goal_id>` now keeps the top of the Goal detail page more
  action-first: the Goal Jump Bar still exposes the nine daily anchors, the
  Goal Command Bar opens with visible Now, Phase, Progress, Proof, and Resume
  cards, the Goal Operator Workbench keeps its do/check/unblock/finish cards
  visible, and the Goal Daily Loop now exposes Continue, Start, Unblock, Pause,
  and Finish Today cards with direct hash-opened pause/save details. Goal
  Return Brief now follows with visible Continue, Latest, Blocker, Finish, and
  Resume cards, Goal Session Digest now follows with Continue, Since Save,
  Latest Artifact, Waiting, and Finish Today cards sourced from workspace,
  timeline, artifact, and waiting-queue state, and Goal Continuation Rail now
  exposes Now, Next Gate, Then, Publish Boundary, and Finish Today cards. Goal
  Workflow Map now exposes Now,
  Progress, Approvals, Publish Boundary, and Finish Today cards before its
  detailed lifecycle rail. Goal Coder Handoff Digest now exposes Now, Handoff,
  Prep, Execute, Ship, and Safety cards over context-pack,
  implementation-handoff, coder-prep, worktree, commit, and publication
  posture before CI. Goal CI Handoff exposes Check GitHub, Record Proof,
  Current Proof, Full Suite, and Finish Today cards, and Goal Live State now
  exposes Now, Phase, Refresh, Pause Rules, and Safety cards before its
  detailed refresh evidence. Goal Remaining Work now exposes Now, Gate
  Progress, Waiting, Open Work, and Finish cards before collapsed command
  evidence and the collapsed gate checklist. Goal Delegations now exposes Now,
  Latest, Workflow, Handoff, and Safety cards; Goal Runs now exposes Now,
  Latest Run, Review, Changes, and Safety cards; Goal Approvals now exposes
  Now, Pending, Approved, Downstream, and Safety cards; Goal Incidents now
  exposes Now, Open, First, Recovery, and Safety cards, all before collapsed
  command evidence and collapsed detailed rows. Goal Evidence now exposes Now,
  Latest, Inventory, Attention, and Safety cards before collapsed command
  evidence, then a read-only Proof/Latest/Run Proof/Artifact Mix/CI Proof/
  Safety digest before the collapsed detailed evidence list; Goal Artifacts now exposes
  Open, Latest, Types, Inventory, and Safety cards before collapsed command
  evidence, the collapsed detailed artifact list, and collapsed typed explorer
  groups. Goal Memory now exposes Now, Notes, Memory Bank, Pin, and Safety
  cards before collapsed command evidence and detailed memory readback; Goal
  Skills Used now exposes Now, Record, Usage, Profile, and Safety cards before
  collapsed command evidence and detailed skill readback; Goal Git Status now
  exposes Now, Branch, Changes, Proof, and Safety cards before collapsed
  command evidence and repository snapshot; Goal Verification Evidence now
  exposes Now, Current, Latest, Record, and Safety cards before collapsed
  command evidence and collapsed proof lines. The earlier Goal Overview, Risk,
  Completion Criteria, and Progress sections now match the same pattern with
  visible Overview cards for Now/Scope/Progress/Waiting/Safety, Risk cards for
  Now/Counts/Boundary/First Task/Safety, Criteria cards for
  Now/Source/Progress/First/Safety, and Progress cards for
  Now/Tasks/Gates/Waiting/Safety before collapsed evidence and detailed rows.
  Goal Timeline now exposes Now, Latest, Families, Flow, and Safety cards
  before collapsed command evidence and metadata while keeping the
  chronological event rows visible; Goal Activity now exposes Now, Latest,
  Signals, Window, and Safety cards before collapsed activity evidence and
  metadata while keeping the recent human-readable event rows visible.
  Goal Completion Readiness now exposes Now, Gates, Waiting, Publish, and
  Safety cards before collapsed readiness evidence; Goal Resume Snapshot now
  exposes Now, Current, Saved, Artifact, and Safety cards before collapsed
  resume evidence, restore state, and save form; Goal Operator Notes now
  exposes Now, Artifact, Resume, Capture, and Safety cards before collapsed
  notes evidence and note details. Goal Section Index now exposes Operate,
  Proof, Work, Knowledge, and Finish switchboard cards before the collapsed
  full anchor map.
  Jump, command, workbench,
  daily-loop, return-brief, continuation, workflow-map, CI handoff, live-state,
  timeline, activity, delegations, runs, approvals, incidents, evidence,
  artifacts, memory, skills, git, verification, overview, risk, criteria, progress,
  completion-readiness, resume-snapshot, operator-notes, section-index, remaining-work, and full
  section-index evidence are
  collapsed by default while preserving phase, next action, current gate,
  project-scoped CI proof posture, full anchor map, daily resume-save state,
  latest activity/artifact, blocker routing, workflow gate surfaces, manual
  publish boundary, local reload posture, delegation/run/approval/incident/
  evidence/artifact/memory/skills/git/verification posture, overview/risk/criteria/progress
  posture, timeline/activity posture, completion/resume/notes posture,
  remaining gate posture, and zero-effect counters in the DOM.
- `/runs/<coder_run_id>` now adds a read-only `Run Evidence Map` after the
  review gate, with Review, Diff, Changed Files, Validation, Logs, and
  Verification cards backed by bounded artifact links before the dense
  evidence inventory.
- `/goals` is now content-first and board-first instead of shared-diagnostic or
  command-readback-first: the `Goal Board Workbench` opens the page before
  Route Context, Operator Focus, and the `Goal Board Command Bar`, with visible
  Do Now, Selected Goal, Attention, and Start/Resume cards plus stable
  visible-card handles. Goal cockpit counts, goal board workbench evidence, and
  command evidence stay collapsed by default while preserving selected Goal,
  phase, next action, waiting counts, lane routing, resume route, first-run
  state, and zero-effect counters in the DOM.
- `/demo` is now content-first and launchpad-first: it opens with the
  `Demo Operator Workbench` cards for Now, Project, Workflow, and Proof before
  shared route/focus diagnostics, command evidence, or the longer fixture
  walkthrough. A visible read-only `Demo Walkthrough Map` now follows with
  Fixture, Project + Goal, Workflow, Run, Approval, Publish Boundary, and
  Resume + Proof cards. Demo workbench, walkthrough, and command evidence stay
  collapsed by default while preserving fixture status, selected
  project/Goal/delegation/run, next local target, proof checkpoints, demo
  command templates, and zero-effect counters in the DOM.
- `/health` is now content-first and action-first: it opens with the
  `Health Operator Workbench` cards for Status, Artifact, Diagnostics, and
  Safety before shared route/focus diagnostics, command evidence, or dense
  health readbacks. Health workbench, command, diagnostics, counts, key-command,
  and workflow-import evidence stay collapsed by default while preserving the
  refreshed local status artifact, explicit status-artifact write-on-GET
  boundary, warning routing, and zero-effect counters in the DOM.
- `/artifacts?path=...` is now content-first and artifact-action-first: it
  opens with `Artifact Operator Workbench` cards for Read, Context, Resume,
  and Safety before shared diagnostics, command evidence, review evidence, or
  inert content. It now follows with an `Artifact Format Lens` for
  renderer-specific Markdown, JSON, patch/diff, text, and log review actions,
  then an `Artifact Relationship Map` for Workflow, Goal, Source, Resume, and
  Boundary return paths. Artifact workbench, format, relationship, command,
  and review evidence stay collapsed by default while preserving bounded path,
  renderer, context, inferred Goal/project/delegation/run, workspace anchor,
  no-content-execution, and zero-effect readbacks in the DOM.
- `/ci-evidence` is now content-first and proof-action-first: it opens with
  the `CI Proof Workbench` cards for Check, Record Smoke, Record Full Suite,
  and Manual Record before shared diagnostics, summary rows, or command
  evidence. CI evidence summary, proof workbench evidence, and command evidence
  stay collapsed by default while preserving GitHub Actions copy-only command
  templates in per-card disclosures, validated recorder targets, proof posture,
  and zero-effect readbacks in the DOM.
- `/dogfooding` is now content-first and action-first: it opens with
  `Dogfooding Operator Workbench` cards for Do Now, ClankerOS, Workflow, and
  Proof before shared diagnostics, command/evidence readback, or the longer
  checklist. Dogfooding workbench, fixture, and command evidence stay collapsed
  by default while preserving fixture status, selected
  project/Goal/delegation/run, next local target, route/CI/action/health links,
  and zero-effect proof in the DOM.
- `/projects` and `/projects/<project_id>` are now action-first: the project
  index opens with `Project Index Workbench` cards for Open, Register, Goals,
  and Resume before shared diagnostics, while project detail pages open with
  the `Project Operator Workbench` before command evidence or shared
  diagnostics. Project detail pages now also show a visible read-only
  `Project Goal Map` for Lead Goal, Phase, Work, Waiting, and Finish before
  the dense Goal list. Project-index evidence, project workbench evidence,
  goal-map evidence, command evidence, and project finish forms stay collapsed
  by default while preserving project counts, first project action, lead Goal
  phase, resume state, proof posture, and zero-effect readbacks in the DOM.
- `/verification` is now action-first: it opens with the `Verification
  Operator Workbench` before shared route/focus diagnostics or command
  evidence, shows visible Now, Check GitHub, Proof, and Finish Today cards,
  then follows with a visible read-only `Verification Proof Map` for Current,
  Fast Smoke, Full Suite, Record, and Boundary. Verification workbench
  evidence, proof-map evidence, command evidence, and the finish-today save
  form stay collapsed by default while preserving current proof posture, CI
  handoff commands, proof-recording target, fast-smoke/full-suite boundaries,
  and zero-effect readbacks in the DOM.
- `/incidents` is now action-first: it opens with the `Incident Operator
  Workbench` before shared route/focus diagnostics or command readback, shows
  visible Now, Evidence, Recover, and Finish Today cards, and keeps incident
  workbench evidence, command evidence, and the finish-today save form
  collapsed by default while preserving incident/recommendation counts, first
  local review target, evidence artifact, and no-resolution/no-retry/
  zero-effect proof in the DOM.
- `/approvals` is now action-first: it opens with the `Approval Operator
  Workbench` before shared route/focus diagnostics or command readback, shows
  visible Do Now, Inspect, Goal, and Finish Today cards, and keeps approval
  workbench, command evidence, and the finish-today save form collapsed by
  default while preserving scoped run/Goal matching, approval type counts,
  request/evidence artifacts, confirmation posture, and zero-effect proof in
  the DOM.
- `/delegation-runs` is now action-first: it opens with the `Delegation Run
  Operator Workbench` before shared route/focus diagnostics or command
  readback, shows visible Now, Workflow, Coder Prep, and Resume cards, and
  keeps delegation-run workbench and command evidence collapsed by default
  while preserving selected delegation/run, project, status, profile/category,
  context-pack/handoff counts, retry/incidents, result artifact, and
  zero-effect proof in the DOM.
- `/workflow` is now action-first: it opens with the `Workflow Operator
  Workbench` before shared route/focus diagnostics or command readback, shows
  visible Now, State, Queue, and Resume cards, then follows with a visible
  read-only `Workflow Scope Picker` for choosing the primary delegation/run
  scope, recent delegations, recent coder runs, parent Goal, and safety
  evidence before the `Workflow Journey` rail for Select, Goal + Scout, Context,
  Handoff, Coder Prep, Approval, Execution, Commit, and Publish. It then adds
  `Workflow Live State` with five-second local page reload polling, pause rules
  for focused form fields and hidden tabs, and a manual Refresh button. It now
  also includes a `Workflow Finish Today` handoff with a confirmed
  `save-workspace` form that stores the exact scoped workflow route as
  `resume_surface`. Workflow journey, live-state, finish, command, and
  workbench evidence stay collapsed by default while preserving selected
  delegation/run, parent Goal, project, current stage, current journey
  position, exact resume surface, next local action, target surface,
  selected-step counts, and zero-effect proof in the DOM.
- `/profiles` is now action-first: it opens with the `Profiles Operator
  Workbench` before shared route/focus diagnostics or command readback, shows
  visible Now, Lanes, Storage, and Resume cards, then follows with a read-only
  `Profile Routing Matrix` for Planning, Coding, Review, Docs, Cheap Model,
  and Frontier Model lanes. Profiles state, matrix evidence, workbench
  evidence, and command evidence stay collapsed by default while preserving
  future-lane, storage-profile, cost-posture, provider-disabled,
  model-routing-disabled, and zero-effect proof in the DOM.
- `/skills` is now action-first: it opens with the `Skills Operator
  Workbench` before shared route/focus diagnostics or command readback, shows
  visible Now, Generated, Usage, and Resume cards, then follows with the
  `Skills Usage Map` and browser-local `Skills Inventory Filter`. Skills
  state, usage-map, filter, workbench evidence, and command evidence stay
  collapsed by default while preserving generated-skill, usage, artifact,
  view-memory, and zero-effect proof in the DOM.
- `/memory` is now action-first: it opens with the `Memory Operator Workbench`
  before shared route/focus diagnostics and command readback, shows visible
  Now, Pin, Notes, and Resume cards, then follows with a `Memory Pinboard` for
  Active Pins, Proposed Pins, Project, Global, Generated, Operator Notes, and
  Future Work plus a browser-local `Memory Inventory Filter` before the dense
  inventory. Memory state, pinboard, filter, workbench evidence, and command
  evidence stay collapsed by default while preserving pin, resume, workspace,
  view-memory, and zero-effect proof in the DOM.
- `/search` is now content-first and search-action-first: it opens with the
  `Search Operator Workbench` before shared route/focus diagnostics, shows
  visible Query, Open, Results, and Resume cards, then follows with a
  `Search Result Map` for Goals, Projects, Work, Decisions, Knowledge, and
  Artifacts lane cards before command evidence or the flat result list. Search
  now indexes coder worktree approvals, coder commit approvals, and publication
  approvals as first-class decision results with scoped approval/workflow/run
  links instead of relying only on legacy approval rows. Search
  state, result-map, workbench, and command evidence stay collapsed by default
  while preserving bounded indexed-search proof and zero-effect counters in
  the DOM.
- `/today` is now content-first and command-center-first: it opens with the
  `Today Command Center` before shared route/focus diagnostics, keeps Today
  state, command, and workbench evidence collapsed by default, and follows
  live refresh with a `Today Session Summary` that now exposes Continue,
  Latest, Proof, and Resume cards before the detailed readback. It then renders
  a read-only `Today Activity Digest` with Now, Window, Artifacts, Notes, and
  Safety cards plus a compact recent timeline list for the lead Goal or
  first-run step before the operator workbench. The note, pause, and Finish
  Today forms still open only when the operator clicks their visible cards or
  navigates to the matching hash, while goal/readiness/activity/CI and
  zero-effect proof stay preserved in the DOM.
- `/workspace` is now content-first and finish/resume-action-first: it opens
  with the `Workspace Operator Workbench` before shared route/focus diagnostics,
  saved-state evidence, or restore-link readbacks. Browser-available saved
  actions render immediately below the workbench, the daily brief and workflow
  map follow, and saved-state/restore/save-form details stay collapsed until
  the operator opens them. Direct `/workspace#save-workspace` navigation now
  opens the collapsed save form client-side.
- `/inbox` is now content-first and queue-action-first: it opens with the
  `Inbox Operator Workbench` before shared route/focus diagnostics or command
  readback, then follows with an `Inbox Triage Board` for Attention,
  Decisions, Work, Publication, and Finish Today lane cards. A read-only
  `Inbox Next Item Brief` then turns the first queue item into Next, Inspect,
  Evidence, After, and Safety cards before command evidence or long queue
  lists. Inbox command, triage, next-item, and workbench evidence stay
  collapsed by default while preserving queue counts, first attention item,
  Goal/delegation/run/evidence routing, a collapsed finish-today workspace save
  form, and zero-effect counters in the DOM.
- `/resume` is now content-first and return-to-work-first: it opens with a
  primary saved-context link and `Resume Operator Workbench` before shared
  route/focus diagnostics or command readback, while saved workspace state,
  command evidence, and workbench evidence stay collapsed by default. The page
  still preserves saved project/Goal/artifact/filter/panel readbacks,
  first-run continuation, readiness checks, same-page action-form routing, and
  zero-effect counters in the DOM.
- `/actions` is now content-first and action-first: the page opens on the safe
  action header and `Action Operator Workbench` before shared route/focus
  diagnostics or catalog readback, then follows with a read-only
  `Action Workflow Map` for Setup, Scout, Context, Prep, Approval, Execute,
  Commit, Publish, and Proof. Action safety, workbench, workflow-map, and
  catalog evidence stay collapsed by default. The catalog still exposes
  visible Catalog, Forms, Approvals, and Boundary cards plus all prior
  zero-effect counters in the DOM.
- `/` now leads with the Home operating surface before shared route/focus
  diagnostics. Its `Home Operator Board` is visible in the first desktop and
  mobile viewports, shows Do Now, Attention, Resume, and Proof cards for the
  lead Goal or first-run step, keeps Home state and board evidence collapsed by
  default, routes browser-available actions to existing confirmed forms, sends
  lead-goal approval attention to `/approvals?goal_id=<goal_id>`, and points
  unfinished resume state at the Home Finish Today anchor.
- `/goals` now includes a `Goal Board Workbench` after the command bar, with
  visible Do Now, Selected Goal, Attention, and Start/Resume cards. It routes
  selected goals directly to their confirmed action form, sends approval
  attention to `/approvals?goal_id=<goal_id>`, and anchors active, paused, and
  completed lanes for faster board navigation.
- Run detail pages now include a read-only `Run Gate Map` after the operator
  workbench, showing the eight local/manual gates from review through manual
  publish, the current gate, done/waiting/blocked counts, direct existing
  surfaces, and zero-effect counters before the dense workflow/evidence
  sections. They now also include a read-only `Run Continuation Strip` after
  the gate map with visible Next Gate, Approval, Evidence, Goal, and Boundary
  cards, so the selected run can be continued from the browser before the
  dense workflow/evidence stack.
- Delegation execution run detail pages now include a read-only
  `Delegation Run Continuation` strip with visible Now, Workflow, Handoff,
  Artifacts, and Goal cards before the detailed scout evidence. It links to
  the owning delegation's `Safe Local Actions`, workflow map, artifact anchor,
  and parent Goal while keeping continuation evidence collapsed by default.
- Run-specific approval gates now link to `/approvals?run_id=<coder_run_id>`,
  where the approval command bar, workbench, and decision brief foreground the
  matching commit or publication approval ahead of unrelated global queue
  items. Commit and publication approval decisions return to the owning run
  page after confirmation.
- The command palette now opens with a compact `Palette Focus` launcher for
  continuing the current Goal action, searching local state, resuming the saved
  workspace, or staying on the current page; detailed route context, keyboard
  shortcuts, and the long open list are preserved inside collapsed palette
  evidence.
- The command palette now also includes a visible `Quick Switch` dock for
  Continue, Workspace, Action, Artifact, and Finish, using saved workspace
  state when present and the current lead Goal/latest artifact as fallback,
  while keeping the `/workspace#save-workspace` handoff, quick-switch
  evidence, confirmation boundary, and zero-effect counters collapsed.
- The shared Operator Focus strip is now compact and action-first: it shows
  the primary action, phase, progress, waiting counts, and `/resume` as visible
  cards, keeps the confirmed local action form available when relevant, and
  moves the full focus readback plus zero-effect counters into collapsed
  `Focus evidence`.
- The shared Route Context strip is now compact and action-first: it shows the
  current page, one primary next local action, back target, Goal, Project, and
  `/resume` before any diagnostic route rows, while the full route evidence and
  zero-effect counters remain available inside collapsed `Route evidence`.
- The shared Recent Items sidebar is now compact and action-first: it shows a
  visible Recent/Workspace/Action/Artifact return dock, while counts, saved
  context, last action, artifact targets, zero-effect counters, and the longer
  shortcut list stay available inside collapsed evidence/details.
- Goal Action Dock and Goal Operator Workbench primary links now jump directly
  to `#goal-next-action-form` when the confirmed browser action form exists,
  so top-of-page action controls land on the actionable form instead of the
  broader Next Action readback.
- Goal Next Action sections now open with a human-first focus strip for Now,
  Gate, Target, and Boundary, giving the operator one readable primary link to
  the existing confirmed form or source surface, then placing the confirmed
  form before collapsed action evidence.
- Goal pages include an in-flow `Goal Action Dock` after the Current Phase
  banner and Goal Jump Bar, keeping the current action, workflow gate, CI proof
  target, and `/resume` route visible near the top of the workbench while
  jumping directly to the existing confirmed action form when one is available
  without adding action authority or covering later Goal sections.
- Goal pages include an in-flow, read-only `Goal Jump Bar` immediately after
  the Current Phase banner, keeping phase, action, workflow, timeline,
  evidence, artifacts, notes, git, and remaining work anchors one click or
  `1`-`9` keypress away without covering later controls or adding writes or
  action authority.
- Goal Timeline and Activity Log rows now render as scan-first event rows with
  time, event-kind badge, clickable local message, target badge, and stable
  `data-timeline-*` markers, making artifacts, delegations, runs, approvals,
  tasks, and goal events easier to distinguish without opening the CLI.
- `/ci-evidence` now has a first-class `CI Proof Workbench` with four browser
  cards for checking a pushed GitHub Actions run, recording job-scoped
  fast-smoke proof, recording full-suite proof, or using the manual
  record-after-success fallback, while keeping all GitHub commands copy-only
  and all local proof writes confirmation-bound.
- Confirmation pages now open with a read-only `Action Preflight` and then the
  existing `Action Confirmation Review` before payload details, with visible
  return route, local write, submitted context, field-count, confirmation
  target, and zero-effect evidence before `confirm=yes`.
- Confirmed local action result pages now open with an action-first
  `Action Complete` surface before payload details, with visible Continue,
  Completed, Artifact, Workflow, and Boundary cards plus collapsed result
  command evidence preserving the target notice surface, result, primary
  artifact, confirmation source, and zero-effect counters.
- Action notice target pages now open with an action-first `Action Notice`
  surface before target content, with visible Continue Here, Last Action,
  Resume, Details, and Boundary cards plus collapsed notice/workspace evidence
  preserving the notice query, saved last action, resume context, and
  no-write/no-external-effect counters.
- Failed local action pages now open with an action-first
  `Action Needs Attention` recovery surface before error details, with visible
  Fix Input, Retry Surface, Error, Catalog, and Boundary cards plus collapsed
  error evidence preserving no-result/no-write/no-external-effect counters.
- The shared operator shell now persists the latest confirmed local action in
  `.clanker/app/workspace.json` and renders a read-only `Last Action` strip on
  later pages, with the result, target notice surface, saved context, and
  zero-effect counters.
- Confirmed local action result pages now include an `Action Result Workflow
  Map` after the continuation block, showing first-run or saved-Goal gate
  progress, current gate, next action, next local surface, and manual publish
  boundary without granting new action authority.
- Goal pages now expose a top-of-page `Goal CI Handoff` after the Workflow Map,
  opening with visible Check GitHub, Record Proof, Current Proof, Full Suite,
  and Finish Today cards before collapsed proof evidence. It still shows
  project-scoped GitHub Actions proof posture, exact `gh run list` /
  `gh run view` command templates, and same-page proof recording targets
  without app-side GitHub polling.
- The Goal page `Goal Workflow Map` now includes action/surface guidance for
  every gate from scout delegation through manual publish, making the full
  workflow easier to follow from the browser without reading docs.
- The global command palette now includes a compact Goal continuation readback
  inside `Continue Current Goal`, so Home and Goal pages can show the current
  workflow gate, next few local gates, target surfaces, and manual publish
  boundary without leaving the palette.
- Goal pages now expose a read-only `Goal Continuation Rail` between the
  Return Brief and Next Action card, showing the current gate, the next few
  local gate actions, their operator surfaces, and the manual publish boundary
  without creating actions or external effects.
- The local app demo now exercises a reviewed, bounded coder worktree run and
  app-confirmed local commit/publication request path. The app can create the
  local isolated commit only after an approved commit request and typed
  matching message; it still never pushes, creates PRs, deploys, calls
  providers, or uses non-loopback network actions.
- GitHub Actions testing is now the intended full-suite verification path after
  push, PR, or manual dispatch. Fast local checks should cover compile,
  app-smoke, focused pytest slices, and whitespace before push.
- Coder publication preparation is the primary post-commit gate after a bounded
  coder worktree commit exists.
- Modern operator flow:
  `coder-commit-request -> approve-coder-commit -> commit-coder-worktree ->
  coder-publication-request -> approve-coder-publication ->
  coder-publication-handoff`.
- Commit request and approval do not stage files or create commits.
- `commit-coder-worktree` creates one local commit only inside the isolated
  `.agent/worktrees/...` worktree, stages only approved files, and does not
  push, create PRs, deploy, call providers, or intentionally use the network.
- Publication request and approval do not push or create PRs.
  `coder-publication-handoff` writes suggested commands only; manual operator
  execution is still required for push/PR.
- Current local verification guidance: run focused checks locally and let
  `.github/workflows/tests.yml` run `python -m pytest -q` on GitHub. A local
  workflow file is not CI proof until GitHub Actions passes on the pushed
  commit. Prefer `ci-snapshot-evidence-from-gh-json` after GitHub completes,
  or with `--job-name "Fast smoke verification"` for scoped early smoke proof,
  so ClankerOS validates the supplied run JSON before recording direct
  snapshot CI proof.
