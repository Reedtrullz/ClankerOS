# Local Operating Summary

## Default Architecture

Use a harness-wrapper architecture around the current Codex runtime. The system
state lives in explicit project files, a SQLite control-plane database, task
events, run artifacts, and memory files. The first executable implementation is
a single local worker with deterministic verification; later versions can add
browser, desktop, remote workers, dashboards, and specialized harnesses.

Core layers for the bootstrap:

- Control plane: SQLite in WAL mode plus CLI output, markdown mirrors, and a
  static dashboard.
- Task graph: goals decompose into typed tasks with status, ownership,
  verification plans, evidence, and artifacts.
- Execution fabric: a pull-based worker claims pending tasks, executes safe
  local task types, and records lifecycle events.
- Approval gate: runnable risky or unknown tasks move to `waiting_approval`
  with a persisted `approval_requests` record before any worker claim.
- Project registry: local git repositories can be registered with a resolved
  git root, default test command, and allowed write roots before coding-agent
  runs target them. Operators can list registered projects, inspect local
  branch/remote/readiness fields, and write durable
  `projects/<name>/context.md` packets with `projects`, `project-status`, and
  `project-context` before starting work.
- Goal planning lifecycle: registered projects can receive durable `goal`,
  `plan`, `contract`, `tasks`, `update-task`, and `replan` records before
  execution. The lifecycle writes SQLite rows plus versioned artifacts under
  `.clanker/projects/<project>/goals/<goal_id>/`, keeps planned tasks at
  `status=planned`, and preserves explicit non-claims around task execution,
  approval, commits, pushes, deployments, provider calls, and external
  mutations.
- Planned task dispatch: `run-task <task_id> --profile <profile>` dispatches
  one `status=planned` goal task only after the linked plan has a sprint
  contract. It records a `status=dispatched` routing decision, creates a run,
  executes the task verification command through the local shell adapter under
  profile permissions, writes an evidence packet under
  `.clanker/projects/<project>/goals/<goal_id>/runs/<run_id>/evidence/`,
  updates the task and linked plan step, and opens a local incident if
  verification fails. It does not commit, push, deploy, call model providers,
  start subagents, or mutate external systems.
- Run evidence packets: `evidence <run_id>` writes replayable review files for
  the run, including `git_status.txt`, `diff.patch`, and `changed_files.json`.
  The git snapshot target is the registered project repo for registered
  project runs, otherwise the ClankerOS root. Existing `run-task` command proof
  files are preserved and aggregate review sidecars are written separately.
  The export does not rerun commands, fetch, pull, commit, push, approve
  effects, or mutate external systems.
- Task recovery recommendations: failed planned-task runs and blocked planned
  tasks can create idempotent `task_recommendations` rows plus local JSON
  evidence. Failed `run-task` evidence packets include
  `recommendations.jsonl`; `task-recommendations --goal <goal_id>` refreshes
  `docs/task-recommendations.md` and dashboard visibility. Recommendations
  guide review/replan/manual reset decisions only; they do not retry, reset,
  replan, dispatch, approve, commit, push, deploy, schedule work, call
  providers, or mutate external systems.
- Worktree coding loop: a high-risk coding goal can run a constrained command
  inside an isolated git worktree, capture command/test/diff evidence, and
  record a proposed `local_git_commit` effect that waits for operator approval.
- Worktree cleanup loop: terminal local coding worktrees can be previewed and
  removed only after an explicit `cleanup-worktrees --confirm` decision. The
  cleanup writes SQLite and JSON evidence, removes clean committed/blocked/
  superseded worktrees, and blocks dirty worktrees without force deletion.
- GitHub handoff loop: a committed `local_git_commit` effect can produce a
  local handoff packet with branch, commit, remote, push command, and draft PR
  command while recording `network_actions_taken=0`. The loop does not push or
  open a PR.
- Local operator app: `app` / `local-app` / `serve` starts a standard-library
  browser UI on `127.0.0.1:8787` by default. It surfaces the modern
  project -> goal/task -> scout -> context-pack -> implementation-handoff ->
  coder-prep -> worktree-plan -> approval -> bounded execution -> commit ->
  publication handoff path, plus project, delegation/run, artifact, health, and
  demo pages. The `/projects` index now acts as a content-first project
  workflow index with a visible `Project Index Workbench` before shared
  diagnostics, cards for opening the first registered project, registering a
  local repo, jumping to goals, or resuming saved work, plus collapsed
  project-index evidence. It still includes a confirmed local
  `Register Local Project` form, local repo posture, default test command,
  goal/task/delegation counts, next recommended operator action, and selected
  delegation/run workflow links. Project detail pages separate project goals
  from goal-linked project tasks, and now open with a `Project Operator
  Workbench` before shared diagnostics or command evidence. The visible cards
  cover Do Now, Goal, Unblock, and Finish Today; workbench evidence, command
  evidence, and the confirmed `save-workspace` form stay collapsed by default
  while preserving branch/commit, goal and queue counts, next project action,
  target local surface, and no-write/no-network/no-external-effect boundaries.
  They include a confirmed local `Start Goal For This Project` form, followed
  by a visible read-only `Project Goal Map` with Lead Goal, Phase, Work,
  Waiting, and Finish cards so the project page exposes the Goal to resume
  before the dense inventory. The map's Work card now names the selected run
  in its workflow action while collapsed evidence preserves the exact workflow
  label and raw href. They also include a project
  workflow launchpad with scoped delegation/run workflow links, safe actions,
  dogfooding, and verification links so the operator can start from the
  product path rather than infer goals from task rows. Project goal rows link
  directly to
  `/goals/<goal_id>` and show phase, next action, and task progress so the
  project page can launch the same goal-centered workbench as `/goals`. The
  local app now also exposes `/today` as a daily command center for the
  current operating day. It is content-first and command-center-first: shared
  route/focus diagnostics render after the daily cockpit, while Today state,
  command, and workbench evidence stay collapsed by default. It starts with a
  read-only six-card `Today Command Center` that selects the lead Goal or
  first-run step, names current phase, one primary action, target surface or
  same-page action form, attention routing for
  approvals/incidents/recommendations/inbox, resume readiness, and CI proof
  posture. When the lead Goal's current action has a confirmed browser form,
  the command center renders it visibly as `#today-current-action` before
  command evidence, so the daily cockpit can be used without opening a
  collapsed details panel. Confirmed `save-goal-note`, `pause-goal`, and `Finish Today`
  workspace save forms are also collapsed by default and open from their
  visible command cards or direct hash links. A read-only
  `Today Live State` panel follows with five-second local
  page reload polling that pauses when the tab is hidden or a form field is
  focused and reports zero provider/network/external-effect counters. A
  read-only `Today Session Summary` follows with visible Continue, Latest,
  Proof, and Resume cards before the detailed readback. Those cards point at
  the current goal or first-run step, latest activity, recorded CI proof, and
  workspace resume posture so the operator can act from the browser return
  brief without reading the whole evidence table.
  A read-only `Today Activity Digest` follows with Now, Window, Artifacts,
  Notes, and Safety cards plus a compact recent timeline list for the lead Goal
  or current first-run step, preserving source, item-count, latest-event,
  artifact, operator-note, and zero-effect evidence in a collapsed details
  block before the denser reused activity inventory. Its Artifacts card now
  uses the latest artifact event label while preserving the exact raw artifact
  href in evidence.
  A read-only `Today Operator Workbench` follows with do/check/unblock/finish
  cards for the current action, timeline/evidence review, first blocker, and
  finish-today resume save target. A read-only `Today Decision Queue` follows
  with exact daily decision rows for the current action plus waiting approvals,
  incidents, recommendations, or blocked work, linking only to existing
  confirmed forms and scoped review surfaces while preserving zero-effect
  evidence. A browser-local `Today Decision Filter` narrows those
  already-rendered rows by lane or text, restores lane/query from
  `localStorage:clankeros-today-decision-filter`, and is included in
  `/workspace#workspace-view-memory` reset coverage. A read-only `Today
  Workflow Map` follows with the first-run gate rail when no Goal exists, or
  the lead Goal's local lifecycle gates, current gate, next action, same-page
  action target, and gate counts once a Goal exists. A read-only `Today CI
  Handoff` follows with the
  latest operator-recorded GitHub Actions proof, current-checkout match status,
  exact `gh run list` / `gh run view` commands for current CI, and links to
  `/verification` plus `/ci-evidence` for recording proof after Actions
  completes without app-side GitHub polling or GET writes. A
  read-only `Today Goal Queue` follows with active/paused/completed
  goal counts, lead-goal phase and next action, goal switch links,
  same-page action-form availability for the lead Goal, progress, and waiting
  counts so the daily cockpit can switch goals without falling back to the
  full inventory. The queue now has a browser-local Find box, All / Active /
  Paused / Completed lane buttons, live count, first-match link, no-match
  state, visible View status, and reload persistence in
  `localStorage:clankeros-today-goal-queue-view`, with reset coverage in
  `/workspace#workspace-view-memory`. When no Goal exists yet, `/today` points
  the command center, Today Goal Queue, Start Here, and reused Home Day Plan
  targets directly to the same-page `Create Project` or `Create First Goal`
  form rendered by the first-run guide instead of requiring a detour to
  `/goals`. It then reuses
  the Start Here, Home Day Plan, Attention Brief,
  Focus Queue, recent activity, inbox, recommendations, incidents, and
  first-run panels without writing on GET or adding action authority. The
  local app also exposes `/guide` as an in-app `Suggested Use Guide` that maps
  `Today -> Goal -> Action -> Proof -> Finish -> Resume`, links first-run
  operators to Home/Today/Goals project/goal setup forms, links current-goal
  operators to `/today`, `/goals/<goal_id>`, existing confirmed action forms,
  `/verification`, `/ci-evidence`, Finish Today,
  `/workspace#save-workspace`, and `/resume`. A visible `Guide Command Panel`
  embeds the existing confirmed first-run or current Goal action form when
  available, letting operators register the project, create the first Goal, or
  continue the current Goal from the guide. A read-only `Operator Recipes`
  panel follows the command panel with Start The Day, Set Up Or Select Goal,
  Do The Next Thing, Unblock Work, Check Proof, Finish Today, and Resume
  Tomorrow intent cards. These cards route to existing local browser surfaces,
  reflect the current action/proof/resume posture, and add no new write
  authority. It remains read-only on GET with no
  provider calls, network actions, push, PR, deploy, or external mutation.
  The local app also exposes `/resume` as a
  read-only return-to-work surface over saved `.clanker/app/workspace.json`
  state and browser-local route memory. It opens with a primary return link, a
  `Browser Resume` panel, and `Resume Operator Workbench` before shared
  route/focus diagnostics or command readback. `Browser Resume` reads
  `localStorage:clankeros-route-history`, ignores `/resume` itself, and offers
  the most recent non-resume route plus route-scoped scroll/open-panel memory
  when available. It also reads `localStorage:clankeros-last-artifact` and
  shows a `Last Artifact` card for the most recently opened artifact in this
  browser while leaving canonical resume state to the explicit
  `/workspace#save-workspace` form. The shared `save-workspace` / Finish Today
  form can hydrate its `last_viewed_artifact` field from that browser-local
  breadcrumb before confirmation/submission unless the operator manually edits
  the field. It shows saved `resume_surface`, goal,
  project, artifact, filters, expanded panels, and zero-effect counters inside
  collapsed saved-state/browser-resume/command/workbench evidence. The shared
  `Workspace Panel Restore` strip now treats saved
  `expanded_panels` as actionable return context on `/resume`, `/workspace`,
  and the saved Goal page; it links to saved Goal panels and browser-locally
  reopens matching details on the saved Goal page without writing state,
  calling providers, or using the network. The visible workbench turns the saved context into
  do/check/unblock/finish cards with same-page action-form routing when
  available, readiness repair, blocker routing, last-artifact readback, and the
  existing `/workspace#save-workspace` finish surface. When the saved Goal or
  current first-run gate has a confirmed browser form, the workbench renders
  that same form as a top `#resume-workbench-action-form` before workbench
  evidence while preserving the deeper Resume Next Action or First-Run Action
  section as the detailed source/fallback. When `resume_surface`
  exists, `/resume` opens that exact local route as the primary return target
  before falling back to the saved Goal or project. Saved Goal links on Home,
  `/resume`, `/workspace`, and the Goal resume snapshot are title-first when a
  title exists, while exact Goal ids and label-source fields remain in
  collapsed evidence for review and automation. A read-only
  `Resume Command Bar` follows with readiness,
  current phase/gate, one next action, target surface, action-form
  availability, last artifact, and zero-effect counters inside collapsed
  evidence. It also includes a `Resume Readiness` checklist for the saved project, goal,
  filters, expanded panels, last artifact existence, and next local surface,
  and the saved goal's current phase plus one recommended next action and the
  same confirmed local action form as the Goal page when that action is
  browser-available, plus a read-only `Resume Workflow Map` sourced from the
  same Goal remaining-work gates so the saved goal's current gate, lifecycle
  progress, next surface, and zero-effect boundaries are visible before
  leaving `/resume`; before a saved Goal exists, `/resume` follows first-run
  progress instead by rendering the same-page `Resume First-Run Action`
  `register-project` or `create-goal` form for the current gate while retaining
  Home/Today/Goals fallback setup links in collapsed evidence, without writing
  on GET;
  `/` also includes a read-only `Home Live State` panel with five-second local
  page reload polling that pauses while a form is focused or the tab is hidden,
  points at the same-page first-run form before a Goal exists or the
  same-page Home Resume Action Form when the saved goal has a
  browser-available next action, and reports zero provider/network/external
  effect counters;
  `/` also includes a read-only `Home Verification Handoff` that shows the
  current branch/commit GitHub Actions direct snapshot command templates,
  latest operator-supplied CI evidence when one exists, and zero app-side
  GitHub polling, provider, push, PR, deploy, or external-mutation effects;
  `/verification` includes a read-only `Verification Operator Workbench` that
  opens the page with Now, Check GitHub, Proof, and Finish Today cards before
  shared diagnostics or command readbacks. It routes missing or stale proof to
  `/ci-evidence#record-ci-snapshot-json`, follows with a visible
  `Verification Proof Map` for Current, Fast Smoke, Full Suite, Record, and
  Boundary, keeps workbench evidence, proof-map evidence, command evidence,
  and the finish form collapsed by default, and preserves no-write,
  no-GitHub-polling, and no-external-effect boundaries in the DOM;
  `/ci-evidence` is now content-first and opens with a read-only
  `CI Proof Workbench` before shared diagnostics or command evidence. It shows
  Check, Record Smoke, Record Full Suite, and Manual Record cards for the
  copy-only GitHub Actions proof loop, then a visible
  `CI Evidence Readiness Strip` for current proof posture, latest local record,
  operator-supplied GitHub JSON, confirmed local recording, and the no-fetch
  safety boundary before the browser-local `CI JSON Assistant` for copying
  the current `gh run view` JSON command,
  optionally pasting clipboard JSON into the recorder textarea, and filling
  fast-smoke or full-suite job names. Summary rows, proof workbench evidence,
  assistant evidence, and command evidence stay collapsed by default before
  the JSON paste form and evidence lists;
  the shared browser shell exposes `Proof (p)` globally beside Next Action,
  Recent Items, and Finish Today, routing explicit clicks/keypresses to
  `/ci-evidence#record-ci-snapshot-json` with no app-side writes, provider
  calls, network actions, or external effects on page render;
  `/search` for bounded global search across indexed goals, projects,
  delegations, known artifacts, incidents, recommendations, memory, runs,
  approvals, and skills, with goal results including live local phase, one
  recommended next action, and remaining-work counts. Search now indexes the
first-class coder worktree, coder commit, and publication approval records,
so approval queries can route directly to scoped approval, workflow, or run
surfaces instead of relying only on legacy approval rows. It is content-first
and
opens with a visible `Search Operator Workbench` before shared route/focus
  diagnostics, with cards for query, first useful hit, result list, and
  `/resume`. A visible read-only `Search Suggestions` panel now appears
  before the workbench, deriving quick links from the live Current Action,
  current Goal, next action, registered projects, approvals, decisions, memory,
  skills, and known artifacts when local state exists, or routing first-run users to `/goals`
  and `/demo` when search has nothing indexed yet. When a Goal action is
  available, the first suggestion links directly to the Goal action dock
  instead of asking the operator to search for the active Goal again. A visible read-only
  `Search Result Map` follows with Goals,
  Projects, Work, Decisions, Knowledge, and Artifacts lane cards before the
  flat result list. A browser-local `Search Result Filter` follows the map,
  narrowing already-rendered results to all, goals, projects, work, decisions,
  knowledge, or artifacts. It remembers the selected lane per query in
  `localStorage:clankeros-search-result-lane:<query-hash>` and exposes Reset
  lane to clear that browser-local view while keeping GET rendering free of
  search-state writes, network access, external effects, and raw filesystem
  browsing. Search state, result-map, result-filter, workbench, and command
  evidence stay collapsed by default while preserving result counts by
  category, first result, target link, summary, lane counts, and
  no-write/no-network/no-raw-filesystem boundaries in the DOM;
  `/incidents` is action-first and includes a visible read-only
  `Incident Operator Workbench` before shared route/focus diagnostics or
  command readback, with cards for the next triage action, evidence artifact,
  recovery surface, and Finish Today handoff. Incident workbench
  evidence, incident command evidence, and the Finish Today save form stay
  collapsed by default while preserving open/resolved incident counts, open
  task-recommendation counts, the first local incident or recovery
  recommendation to review, evidence links, stable open/resolved/
  recommendation anchors, and no-write/no-resolution-on-GET/no-retry-on-GET/
  no-network/no-external-effect boundaries;
  `/delegation-runs` is action-first and includes a visible `Delegation Run
  Operator Workbench` before shared route/focus diagnostics or command
  readback, with cards for the next delegation/run action, scoped workflow,
  handoffs ready for coder prep, and `/resume`. Workbench and command evidence
  stay collapsed by default while preserving completed/pending delegation run
  counts, incidents, retry candidates, context-pack and
  implementation-handoff readiness, the first local delegation/run/workflow
  surface to inspect, stable attention/coder-prep/recent-run anchors, and
  no-write/no-provider/no-network/no-external-effect boundaries before the
  longer execution evidence index;
  `/workflow` renders the current reviewed-run `coder-commit-request` form
  inline in the `Workflow Operator Workbench` when the selected workflow is at
  that gate, preserving the source `/runs/<id>` surface in evidence and still
  requiring the normal `/actions/coder-commit-request` confirmation before
  writing local artifacts. It also includes a visible read-only `Workflow
  Journey` between the `Workflow Operator Workbench` and `Workflow Command Bar`,
  with nine stage cards for Select, Goal + Scout, Context, Handoff, Coder Prep,
  Approval, Execution, Commit, and Publish. A visible `Workflow Live State` panel follows
  with local page reload polling every five seconds, pause-while-editing and
  pause-while-hidden rules, and zero provider/network/external-effect
  counters. A visible `Workflow Finish Today` handoff follows with a confirmed
  `save-workspace` form that stores the exact scoped workflow route as
  `resume_surface`; the shared shell's `Finish` button, `f` shortcut,
  Operator Ribbon Finish card, and command palette Finish card now target that
  same `#workflow-finish-today` form on `/workflow` instead of the generic
  Workspace fallback. These summarize the selected delegation or coder run,
  parent Goal, project, current workflow stage, journey position, exact resume
  surface, next local action, target surface, reason, and zero-effect counters
  before the detailed selected-state map and continuation links;
  `/artifacts?path=...` is content-first and opens with a visible read-only
  `Artifact Operator Workbench` before shared diagnostics or dense readbacks.
  It shows cards to open the inert content, return to the owning Goal or
  delegation context, remember or resume from the artifact, and inspect safety
  proof. A visible `Artifact Format Lens` follows with renderer-specific
  cards for Markdown, JSON, patch/diff, text, and log artifacts, including the
  primary read/review action, structure summary, review target, and safety
  boundary. A visible `Artifact Relationship Map` then connects the artifact
  back to inferred Goal, project, delegation, run, saved workspace, and safety
  return paths before dense evidence. Detailed `Artifact Command Bar`,
  `Artifact Review Brief`, format evidence, and relationship evidence stay
  collapsed by default while preserving bounded artifact
  path, render type/family/renderer, size, rendered bytes, line count,
  truncation state, inferred project/goal/delegation/run context, workspace
  anchor status, one next action, and no-write/no-raw-filesystem/
  no-content-execution/no-network/no-external-effect boundaries before the
  inert content renderer and remember-artifact form;
  `/workspace` for persistent open project/goal/filter/panel/last-artifact/
  `resume_surface` state in `.clanker/app/workspace.json`. It now opens with the
  `Workspace Operator Workbench` before shared route/focus diagnostics or
  saved-state evidence, so the saved workspace first shows do/check/unblock/
  finish cards, same-page action-form routing when available, readiness and
  blocker routing, last-artifact readback, and a Finish Today link that opens
  the collapsed confirmed save form. The save form keeps saved workspace state
  authoritative, but when no workspace Goal is saved and a lead Goal exists it
  pre-fills suggested project, Goal, goal-scoped filters, panels, latest
  artifact values, and exact current-action `resume_surface` while reporting
  `workspace_save_defaults_write_on_get=false`.
  When a saved workspace only has the broad `/goals/<goal_id>` route, the save
  defaults now repair the next saved `resume_surface` to the exact Goal action
  route while labeling it with the current action.
  Confirmed `save-workspace` POST applies the same repair before writing
  `.clanker/app/workspace.json` when a saved Goal workspace omits
  `resume_surface` or only supplies the broad Goal route.
  The same Goal-page action form appears immediately below the workbench when
  browser-available, followed by a read-only `Workspace Restore Map` with
  Restore, Goal, Artifact, Filters + Panels, and Tomorrow cards that make saved
  versus suggested return state explicit before the
  read-only `Workspace View Memory` panel. That panel inventories browser
  `localStorage` view state for theme, focus mode, Goal board, Home Goal
  Board, Recent Items filters, route history, the last opened artifact
  breadcrumb, open panels, scroll position, search lanes, timeline lanes, Goal
  section searches, Today Goal Queue view, artifact filters, the global
  Artifact Index filter, Today and Goal decision filters, notes filters, note
  drafts, setup and workflow form drafts, Memory Bank filters, Skills Inventory
  filters, First Run Checklist checks/notes,
  Approval Queue filters, Inbox Queue filters, and Profile Routing filters, and
  can clear those browser-local
  values after explicit operator clicks without writing
  `.clanker/app/workspace.json`, calling providers, using the network, or
  mutating external systems. It sits before the
  read-only `Workspace Daily Brief` and `Workspace Workflow Map` for the saved
  goal's phase, current gate, resume readiness, finish posture, and zero-effect
  counters. Saved-state and restore-link readbacks stay inside collapsed
  evidence. Before a saved Goal exists, `/workspace` follows first-run
  progress instead: empty checkouts point those sections at the same-page
  `Workspace First-Run Action` `register-project` form and
  registered-project/no-goal workspaces point at the same-page `create-goal`
  form while preserving the saved project link. Goal workflow forms use the
  same scoped browser-local draft memory for worktree approval notes, safe
  local run commands, commit/publication messages, approval notes, and manual
  `complete-goal` notes, with cleanup after confirmed local success. Home,
  Recent Items, and the command palette also prefer the exact saved `resume_surface`
  when one exists, while retaining `/resume` as the hub; `/memory` for project/global/
  generated memories, proposed memories, operator notes, future work, and pin
  actions. It is action-first and opens with a visible
  `Memory Operator Workbench` before shared route/focus diagnostics and
  command readback, with cards for the next memory action, proposed pins,
  operator notes, and `/resume` or goal context. When proposed memories exist,
  the workbench also opens a same-page `pin-memory` form for the first
  proposed memory before collapsed evidence; the write still happens only
  through the confirmed POST action. A visible read-only `Memory Pinboard`
  follows with Active Pins, Proposed Pins, Project, Global,
  Generated, Operator Notes, and Future Work lanes. A browser-local
  `Memory Inventory Filter` then narrows already-rendered memory rows by lane
  or text and restores lane/query from
  `localStorage:clankeros-memory-inventory-filter` before the longer memory
  inventory. Memory state, pinboard, filter, workbench evidence, and command
  evidence stay collapsed by default while preserving entry counts, first proposed pin
  or fallback resume target, saved workspace context, and
  no-write/provider/network/external-effect boundaries in the DOM; `/skills`
  for available/generated skill records with usage counts. It is action-first
  and opens with a visible `Skills Operator Workbench` before shared
  route/focus diagnostics or command readback, with cards for the next skill
  review, generated skills, usage, and `/resume` or Goal context. A visible
  `Skills Usage Map` follows with Now, Available, Generated, Usage, Projects,
  and Safety cards; the Now card's primary action names the selected skill
  when opening a skill artifact, such as `Open local-files skill`, instead of
  generic artifact copy. A browser-local `Skills Inventory Filter` then narrows
  already-rendered skill rows by lane or text and restores lane/query from
  `localStorage:clankeros-skills-inventory-filter` before the dense inventory.
  Skills state, usage-map, filter, workbench evidence, and command evidence
  stay collapsed by default while preserving record, generated, usage,
  project-usage, last-used, first-artifact, no-execution/no-install/provider/
  network, and zero-effect readbacks in the DOM; `/approvals` as an action-first
  local decision queue with a visible `Approval Operator Workbench` before
  shared route/focus diagnostics or command readback. It shows
  do/inspect/Goal/finish cards, parent Goal routing, request/evidence
  artifacts, confirmation posture, and a collapsed confirmed
  `save-workspace` form that stores the queue as a future resume point without
  writing on GET. A visible read-only `Approval Readiness Strip` follows the
  workbench with Queue, Decision, Scope, Evidence, and Safety cards for the
  focused approval item, exposing pending counts, scoped Goal/run/delegation
  context, the existing confirmed approval form anchor, evidence artifact,
  after-decision route, and no-write/no-approval/no-execution/no-network/
  no-external-effect boundaries before the older queue readbacks. The read-only `Approval Queue Command Bar` follows with
  pending worktree/commit/publication counts, first recommended decision,
  target section, after-decision guidance, and zero-effect boundary inside
  collapsed evidence. The `Approval Decision Brief` then shows Decision,
  Inspect, Evidence, After, and Safety cards before collapsed decision evidence
  so the operator can inspect the right workflow/run/artifact and understand
  the next local-only follow-up before using a confirmed approval form. A
  browser-local `Approval Queue Filter` narrows already-rendered approval rows
  by worktree, commit, publication, scoped Goal, scoped run, or text and
  restores lane/query from `localStorage:clankeros-approval-queue-filter`
  without deciding, approving, executing, pushing, creating PRs, deploying, or
  calling providers;
  and `/profiles`
  for inactive future provider-routing readback from `.clanker/profiles.yml`
  and SQLite profile storage rows, including profile labels, modes, cost
  tiers, model placeholders, write posture, adapter status, and `use_for`
  labels. It is action-first and opens with a visible
  `Profiles Operator Workbench` before shared route/focus diagnostics or
  command readback, with cards for the next profile review, future lanes,
  storage, and `/resume` or Goal context. The read-only `Profile Routing
  Matrix` maps Planning, Coding, Review, Docs, Cheap Model, and Frontier Model
  lanes to stored local profiles, cost posture, `use_for` labels, and inactive
  provider/model routing status. A browser-local `Profile Routing Filter`
  narrows already-rendered matrix cards and profile rows by routing lane,
  storage/configured posture, or text, remembers lane/query in
  `localStorage:clankeros-profile-routing-filter`, and resets without enabling
  providers or model routing. Profiles state, matrix evidence, filter evidence,
  workbench evidence, and command evidence stay collapsed by default while preserving
  configured, storage, enabled, disabled, future-lane, adapter, write-posture,
  use-for, provider, model-routing, and zero-effect readbacks in the DOM.
  The `/goals` and Home first-run panel now exposes a state-aware
  Create project -> Create first goal -> Create first delegation -> Generate
  context pack -> Run first delegation checklist, visible five-card progress
  strip, and confirmed local
  `register-project` and `create-goal` forms, explicitly defaults the first
  dogfood project to `clankeros` at the current repository path, persists
  resume workspace state plus exact `resume_surface` routes after confirmed
  browser project registration and first goal creation, now writes first Goal
  creation resume state to the exact
  `/goals/<goal_id>#goal-action-dock-form` route so `/resume` opens with the
  next Goal action, such as `Create scout delegation`, instead of a broad Goal
  overview, keeps unsent setup and
  Goal creation edits in browser-local
  `localStorage:clankeros-action-form-draft:<action>:<scope>` until cleared or
  confirmed-success cleanup, gives those setup forms action briefs, human
  labels, field help, confirmation/external-effect notes, and outcome-named
  buttons like `Create project` / `Create Goal`, carries the same human labels
  through the confirmation/result pages while retaining raw action ids in
  evidence, and now refreshes the
  same saved workspace anchor after
  confirmed first-run scout delegation, context-pack generation, and delegation
  run actions so `/resume`, Home, and `/workspace` return to the newest local
  workflow artifact without a separate manual save. Confirmed coder-prep,
  coder-worktree-plan, coder-worktree-approval, and
  approve-coder-worktree browser actions also refresh that saved workspace
  anchor to their newest human-readable local packet or decision artifact, so
  post-delegation resume continues through the bounded coding gates without
  creating worktrees or external effects. It moves initial project/goal setup
  into the browser without adding provider calls or external effects. After an
  approved execution gate, confirmed `run-coder-worktree`, `review-run`, and
  `coder-commit-request` browser actions refresh the saved workspace anchor to
  the coder run summary, local review report, and commit approval request
  Markdown respectively, so browser resume continues through execution,
  review, and commit-request gates without a separate workspace save and
  without pushing, creating PRs, deploying, calling providers, or fetching
  GitHub status. Confirmed `approve-coder-commit`,
  `commit-coder-worktree`, `coder-publication-request`,
  `approve-coder-publication`, `coder-publication-handoff`, and
  `complete-goal` browser actions now do the same for the commit decision,
  local worktree commit summary, publication request, publication decision,
  publication handoff, and final completion anchor, keeping resume state
  current through the manual publish boundary without app-side push, PR,
  deploy, provider, network, or GitHub polling effects. Confirmed `pin-memory`
  promotion also refreshes the saved workspace anchor to the pinned evidence
  artifact while preserving the current goal when it belongs to the same
  project, so memory decisions can become tomorrow's resume surface without a
  separate manual workspace save. The
  populated `/goals`
  cockpit now starts with a `Goal Board Workbench` with Do Now, Selected Goal,
  Attention, and Start/Resume cards, including selected-Goal action-form links,
  scoped approval attention via `/approvals?goal_id=<goal_id>`, lane anchors,
  and `/resume`, before shared route/focus diagnostics, the command readback,
  or active/paused/completed lanes.
  The read-only `Goal Board Command Bar` follows as collapsed command evidence
  that preserves the saved or active Goal, phase, one next action, target local
  surface, waiting counts, resume route, action availability, and zero-effect
  counters. It also exposes a confirmed local `Start Another Goal` form for
  registered projects, so daily goal creation does not require the CLI. A
  browser-local `Goal Board Filter` follows that form, filtering active,
  paused, and completed lanes by title, project, phase, status, next action,
  progress, or remaining work with a live count, mode buttons, first-match
  jump, and explicit no-write/no-provider/no-network/no-external-effect
  evidence before the longer lane lists. The same browser-local helper sorts
  already-rendered Goal cards within each lane by updated time, waiting items,
  open work, progress, or title without changing state or running commands, and
  restores query, lane mode, and sort from
  `localStorage:clankeros-goal-board-view` across reloads until Reset view
  clears the browser-local board state.
  Goal rows in those lanes render as
  scan-first cards with direct Goal, project, and concrete next-action links
  such as `Create commit request` plus phase, progress, waiting, and open-work
  readbacks while preserving the legacy
  project/status/phase/next-action/progress/remaining-work text for automation
  and tests. The
  checklist reports the current step,
  one `first_run_next_action` with a reason, project/goal/delegation/
  context-pack state, next local surface, a confirmed local `run-delegation`
  action once context is ready, and a copyable CLI fallback while keeping
  provider calls, network actions, push, PR creation, deploy, and external
  mutation unexposed. Shared goal rows in Home, `/goals`, and project detail
  pages now show phase, next action, progress, and compact remaining-work
  counts for open tasks, incidents, and recommendations. Goal detail pages now
  expose first-class Goal Risk and Goal Completion Criteria sections sourced
  from task risk metadata, sprint contracts, plan steps, or task verification
  plans. Goal Overview, Goal Risk, Goal Completion Criteria, and Goal Progress
  now start with visible action cards instead of raw readbacks: Overview shows
  Now, Scope, Progress, Waiting, and Safety; Risk shows Now, Counts, Boundary,
  First Task, and Safety; Criteria shows Now, Source, Progress, First, and
  Safety; Progress shows Now, Tasks, Gates, Waiting, and Safety. Their command
  evidence and detailed overview/risk/criteria/progress rows stay collapsed by
  default while preserving no-write/no-provider/no-network/no-external-effect
  boundaries in the DOM.
  Goal detail pages are now content-first: the Goal summary, large Current
  Phase banner, jump bar, action dock, and progress meter render before shared
  route/focus diagnostics. The summary is title-first and uses the human Goal
  title/intent as both the page heading and browser title, while retaining the
  Goal id as metadata with project, status, phase, and local refresh posture.
  The shared breadcrumb/Route Context/command-palette route evidence layer now
  uses the same human Goal title for visible Goal links, while preserving
  explicit Goal id evidence fields so review and automation do not lose the
  stable identifier.
  The in-flow read-only `Goal Jump Bar` covers phase, action, workflow,
  timeline, evidence, artifacts, notes, git, and remaining work. Visible `1`-`9`
  key badges and `aria-keyshortcuts` jump to those local anchors without
  submitting forms while jump evidence stays collapsed by default. An in-flow `Goal Action Dock`
  follows the jump bar and keeps the current action, workflow gate, CI proof
  target, and `/resume` route visible near the top of the workbench while
  rendering a top-of-page `Current Action Form` when the existing confirmed
  Goal action form is available. This duplicates the rendered form for
  usability, not the backend action authority; the same confirmation route
  still owns writes and local execution. A read-only `Goal Progress
  Meter` follows with task and workflow progress bars, waiting operator work,
  latest proof posture, and the next confirmed browser action. The dock and
  meter precede the Goal
  Command Bar, Goal Operator Workbench, Daily Loop, Goal Return Brief, Goal
  Continuation Rail, Next Action, Workflow Map, Goal CI Handoff, live refresh
  panel, and collapsed full section index, so the first
  viewport names the current phase before
  navigation and diagnostics. Goal Progress keeps the browser progress bar
  visible after its card-first command bar, while detailed task/gate/waiting
  counts stay collapsed until the operator asks for evidence.
  Goal pages also
  include clickable timeline entries with operator-facing lifecycle language
  for approval requested/granted, execution completed, review passed, commit
  approved, and publication approved states. The timeline also
  backfills generic artifact events from the same bounded Goal Artifact
  Explorer registry, deduping workflow-specific artifact links so produced
  context packs, handoffs, diffs, changed-file lists, and text logs stay
  chronological. Timeline and Activity Log rows render as scan-first events
  with time, event-kind badge, clickable local message, and target badge, so
  artifacts, delegations, runs, approvals, tasks, and goal events are easier
  to distinguish at a glance. The Goal timeline starts with a read-only
  `Goal Timeline Command Bar` that exposes visible Now, Latest, Families,
  Flow, and Safety cards before collapsed total-event, latest-linked-event,
  event-family, run/task/note, and zero-effect evidence. A read-only
  `Goal Timeline Digest` follows with Span, Latest, Artifact, Next, and Safety
  cards, plus collapsed evidence for item counts, current gate, latest
  artifact, next surface, and zero-effect counters. Its Artifact card uses
  the concrete bounded artifact action label, such as
  `Open coder run <run_id> review`, instead of generic latest-artifact copy.
  A browser-local
  `Timeline Lane Filter` follows the digest, using existing
  `data-timeline-kind` markers to hide or show rendered artifact, approval,
  delegation, run, task, note, and generic event rows. It remembers the
  selected lane per Goal in
  `localStorage:clankeros-goal-timeline-lane:<goal_id>` and exposes Reset lane
  to clear that browser-local view, while keeping GET rendering free of Goal
  writes, network access, and external effects before timeline metadata and the
  full chronological list. The Activity Log likewise opens with visible Now, Latest, Signals,
  Window, and Safety cards before collapsed recent-event evidence and
  metadata. Goal pages include a browser-native progress
  bar and a large Current Phase banner that explains the phase reason,
  operator attention cue, next action surface, latest activity, and zero-effect
  boundary without requiring the CLI. Home activity now includes a read-only
  activity command bar with visible Latest, Goals, Artifacts, and Notes cards
  before the longer activity list, while preserving target surface,
  operator-note/artifact counts, and zero-effect boundaries in the DOM. Goal
  activity sections keep the matching command-bar pattern for latest
  human-readable event, target surface, counts, and safety evidence. Goal detail pages also include a
  read-only `Goal Attention Digest` after the progress meter with visible Now,
  Approvals, Incidents, Recommendations, Open Work, and Safety cards before the
  deeper command surfaces. A read-only `Goal Decision Queue` follows with
  exact Goal-scoped rows for the current next action plus pending approvals,
  incidents, recommendations, and blocked tasks; those rows link only to the
  existing confirmed Goal action form, scoped approvals, incidents,
  recommendations, or risk surfaces and preserve zero write/provider/network/
  external-effect counters. A browser-local `Goal Decision Filter` then
  narrows those rendered rows by lane or text, restores lane/query per Goal
  from `localStorage:clankeros-goal-decision-filter:<goal_id>`, and is
  included in `/workspace#workspace-view-memory` reset coverage. The page also includes a
  read-only `Goal Command Bar` near the top that opens with visible Now,
  Phase, Progress, Proof, and Resume cards while keeping phase, one primary
  action, target local surface, progress, waiting counts, `/resume`, latest
  project-scoped CI proof status, and write-on-GET/network/external-effect
  boundaries in collapsed command evidence. A `Goal Operator Workbench` follows it
  with a human-readable do/check/unblock/finish strip, pointing its primary
  action directly at the in-page Goal action form when available, the source
  surface, current gate/progress, first unblock surface, and confirmed
  local-action counters in collapsed workbench evidence before the longer
  diagnostic sections. The in-flow Goal Jump Bar keeps the main daily anchors
  one click or keypress away without covering later controls, the in-flow Goal
  Action Dock keeps the current action, gate, proof, and resume route visible
  near the top without covering later controls, and renders the current
  confirmed action form before the deeper detailed copy. The Goal Next Action
  section starts with a human-first focus strip for Now, Gate, Action source,
  and Boundary, labels source links in operator language such as
  `Review run <run_id>`, then renders the confirmed form before collapsed
  action evidence with the exact raw source route retained. The Goal
  Section Index now opens with visible Operate, Proof, Work, Knowledge, and
  Finish switchboard cards before the collapsed full anchor map, making the
  page navigable through scan-first operator surfaces without dumping every
  anchor by default.
  Goal Overview starts with a read-only
  `Goal Overview Command Bar` so the operator sees goal identity, status,
  phase, risk, progress, local counts, next click, and no-effect boundaries
  before the raw overview metadata. Goal detail pages also include a
  `Goal Daily Loop` near the top that condenses start, continue,
  unblock, pause, and finish cues from the same local Goal/workspace/approval/
  incident/recommendation state into visible cards. Detailed daily-loop proof
  stays collapsed by default, while the confirmed local `pause-goal` and
  `save-workspace` forms open from hash-linked Pause and Finish Today details
  so the operator can shelve or save the goal without scanning state rows. The
  pause action is local status movement only: it accepts non-paused incomplete
  goals, sets status to `paused`, refreshes saved workspace context to the Goal
  artifact, and does not approve work, run work, call providers, use the
  network, push, create PRs, deploy, or mutate external systems.
  A read-only `Goal Return Brief` follows the daily loop near the top of the
  Goal page as visible Continue, Latest, Blocker, Finish, and Resume cards,
  then keeps current gate, next action, resume readiness, latest activity,
  latest activity label, latest raw surface, latest artifact, CI proof
  posture, blocker routing, `/resume`, finish surface, and zero-effect
  counters in collapsed return evidence without writing on GET.
  A read-only `Goal Session Digest` follows it as visible Continue, Since
  Save, Latest Artifact, Waiting, and Finish Today cards. The digest is sourced
  from existing Goal state, saved workspace timestamp, latest local timeline
  item, latest activity label and raw surface, latest artifact, and waiting
  queue counts, with source and zero-effect counters kept in collapsed digest
  evidence. Its Latest Artifact card now names the concrete latest artifact
  record, such as `Open coder run <run_id> review`, while preserving the exact
  raw artifact href in evidence.
  The `Goal Coder Handoff Digest` Execute and Ship cards also name the
  concrete selected run when they open a run surface, rather than using
  generic latest-run copy.
  A read-only `Goal Activity Pulse` follows the digest as visible Latest,
  Recent Three, Mix, Artifact, and Next cards, reusing the Goal timeline so a
  returning operator can see the newest linked movement before opening the
  full event list. Its Artifact card uses the same concrete artifact action
  label and preserves the exact artifact route in collapsed evidence.
  A read-only `Goal Continuation Rail` follows the pulse as visible Now, Next Gate,
  Then, Publish Boundary, and Finish Today cards, with detailed gate rows,
  exact surfaces, the manual publish boundary, and zero-effect counters kept
  in collapsed continuation evidence so the Goal page can be followed without
  jumping straight to longer diagnostics.
  Goal detail pages also include a
  read-only `Goal Workflow Map` near the top that opens with Now, Progress,
  Approvals, Publish Boundary, and Finish Today cards sourced from the same
  Remaining Work gate state. It points at the existing Goal action form,
  Remaining Work, goal-scoped approvals, CI handoff, and Finish Today save
  form, while the detailed lifecycle rail, each gate's eventual local operator
  surface, manual publish boundary, and zero-effect counters stay in collapsed
  workflow evidence. A read-only `Goal Coder Handoff Digest` follows it with
  visible Now, Handoff, Prep, Execute, Ship, and Safety cards over the selected
  delegation, context-pack, implementation-handoff, coder-prep/worktree,
  commit, and publication posture. A read-only `Goal CI Handoff`
  follows that with visible Check GitHub, Record Proof, Current Proof, Full
  Suite, and Finish Today cards, project-scoped proof status, latest
  operator-recorded GitHub Actions evidence, exact `gh run list` /
  `gh run view` command templates, and a same-page proof-recording target
  before the operator reaches the long timeline and artifact sections. The
  detailed ledger remains collapsed, and the app still does no GitHub polling
  or external mutations on GET. Goal
  Remaining Work itself opens with visible Now, Gate Progress, Waiting, Open
  Work, and Finish cards, while the command proof and full remaining-work
  checklist stay collapsed by default. It preserves current gate,
  done/pending/waiting gate counts, open task/incident/recommendation counts,
  pending approvals, one next local surface, and no-write/no-provider/
  no-network/no-external-effect boundaries in the DOM. Goal
  detail pages also include a
  first-class `Next Recommendation` section that identifies whether the current
  recommendation came from an open task recommendation or was derived from
  current phase and local goal records, points at the target local surface, and
  records write-on-GET and external-effect boundaries. Open task
  recommendations with stored `recommended_commands` now render copy-only
  `Goal Recovery Commands` cards with clipboard buttons, evidence links, and
  explicit no-execute/no-retry/no-replan/no-write counters. When those cards
  exist, Goal-local Next Action, header shortcut, attention digest, ribbon,
  daily loop, workbench, session digest, overview, incident, and
  remaining-work surfaces route to the recovery-command anchor first while
  keeping incident recommendations available as secondary triage. They also include a
  first-class `Goal Live State` surface that opens with visible Now, Phase,
  Refresh, Pause Rules, and Safety cards, including a local `Refresh now`
  control and collapsed detailed refresh evidence. Its five-second local page
  reload polling pauses while the operator is editing a form or the tab is
  hidden; it does not fetch GitHub status, call providers, push, create PRs,
  deploy, or mutate external systems. They also include a read-only
  `Goal Section Index` with visible Operate, Proof, Work, Knowledge, and
  Finish switchboard cards plus a browser-local section finder over stable
  in-page anchors including the command bar, workflow map, and major Goal
  surfaces. The finder keeps only its per-Goal query in
  `localStorage:clankeros-goal-section-finder:<goal_id>` and can be reset from
  the Goal page or Workspace View Memory, so operators can filter/jump through
  a long Goal workbench without leaving the page or triggering writes.
  Every app page also includes a shared read-only `Operator Ribbon` above the
  sidebar/page shell. It derives from the saved workspace goal, current lead
  goal, or first-run state and opens with compact Now, Goal, Attention,
  Finish, Resume, and Search cards plus collapsed ribbon evidence for the
  current route, phase, primary action, waiting counts, saved workspace
  context, Finish Today confirmation surface, command palette availability,
  and no-write/no-provider/no-network/no-external-effect boundaries. The
  shared read-only `Operator Focus` strip still derives from
  the same saved workspace goal or current lead goal and opens with compact
  action cards for the primary action, phase, progress, waiting counts, and
  `/resume`, followed by the expandable confirmed local action form when the
  current next action is browser-available and collapsed `Focus evidence` for
  the full readback and no-write/no-provider/no-network/no-external-effect
  boundaries outside the Goal page. The header `Focus` control and `m`
  shortcut now provide a browser-local Focus mode that stores
  `data-focus-mode="true"` in `localStorage:clankeros-focus-mode`, hides Recent
  Items, Route Context, and Last Action strips while keeping Operator Focus and
  the current-action launcher visible, and keeps the Operator Ribbon plus page
  body visible without writing server state. When
  no Goal exists yet, the shared shell now treats that as first-run progress:
  Home, Today, and Goals point `Route Context`, `Operator Focus`, and the
  command palette at their same-page `Create Project` or `Create First Goal`
  anchors, while other pages link back to Home/Today/Goals first-run anchors.
  Goal `Finish Today` and `Remember This Goal` saves preserve a precise
  `resume_surface` at the current action form when available, or the Goal Next
  Action card otherwise, so `/resume` returns to an actionable Goal anchor
  instead of only the broad Goal page.
  The command palette now opens with a compact `Palette Focus` launcher for
  continuing the current Goal action, searching local state, resuming the saved
  workspace, or staying on the current page. Its search box narrows a visible
  `Palette Results` list of local routes, recent work, the focused Goal's
  exact Current Action when available, core section anchors, and route-local
  `/today` section anchors in place, with a no-match state and zero-effect
  evidence. The Current Action result uses `kind=current-action` and the Goal
  action dock href, so action text such as `commit` opens the live Goal action
  before static route matches. ArrowDown/ArrowUp move the
  active visible command and Enter opens that local route or anchor, while the
  Search button still opens full indexed `/search`. This makes palette queries such as
  `timeline`, `approval`, `artifact`, `memory`, `git`, `remaining`,
  `decision`, `workflow`, `CI`, or `finish` jump directly to the relevant
  Goal or Today page sections. Its detailed
  route readback, keyboard shortcuts, long
  open list, and zero-effect counters are still available inside collapsed
  `Palette evidence and shortcuts`, while the goal-aware `Continue Current
  Goal` form remains directly below search.
  They also include a read-only `Goal Operator Notes Command Bar` before the
  confirmed `save-goal-note` form. It opens with visible Now, Artifact,
  Resume, Capture, and Safety cards, then a visible `Goal Notes Browser`
  renders the existing `operator-notes.md` sections as scan-first cards with
  text search, per-Goal browser-local query memory in
  `localStorage:clankeros-goal-notes-filter:<goal_id>`, Reset notes, and
  no-write/no-provider/no-network/no-raw-filesystem/no-external-effect
  boundaries. Command evidence and note details stay collapsed and preserve
  the goal-scoped path, timestamped entry count, artifact size, workspace
  resume-anchor posture, one review or capture target, and safety counters.
  The confirmed note form is multiline and keeps unsent text in browser-local
  `localStorage:clankeros-goal-note-draft:<goal_id>` until the operator clears
  it or a confirmed note write updates the artifact. The confirmed note action
  appends local operator resume context to the artifact; saved operator notes
  also become linked `Operator note saved` entries in the Goal timeline and
  recent Activity Log with zero external effects, and the confirmed note action
  now refreshes saved workspace state to the exact
  `/goals/<goal_id>#goal-operator-notes` surface plus the operator-notes
  artifact so `/resume`, Home, and `/workspace` return to the note context
  without a separate manual save. They also include a confirmed `delegate`
  next-action form when a goal has planned tasks but no delegation yet. If a
  goal needs to be shelved, the Goal Daily Loop and `/today` expose confirmed
  `pause-goal`; if a goal is explicitly paused, the Goal page shows a `Paused`
  phase and a confirmed `resume-goal` next-action form that only changes local
  goal status from `paused` to `active`; neither action resumes blocked tasks,
  approves gates, runs work, pushes, creates PRs, deploys, calls providers, uses
  the network, or mutates external systems, and confirmed pause/resume refreshes
  saved workspace state to the relevant Goal artifact. The
  delegation form writes a read-only scout delegation contract only and does
  not start a subagent. Once a delegation exists without a context pack, the
  same Goal Next Action card exposes a confirmed `context-pack` form; after
  the context pack exists, it shows a confirmed `run-delegation` form that
  reuses the existing read-only adapter checks and incident-on-failure path,
  plus the exact CLI fallback command. After a delegation
  completes, the Goal Next Action card exposes confirmed `coder-prep`,
  `coder-worktree-plan`, and `coder-worktree-approval` forms at the matching
  workflow phases, then exposes confirmed `approve-coder-worktree`. Once the
  worktree request is approved, the Goal card exposes a confirmed
  `run-coder-worktree` form for one operator-provided safe local command in
  the isolated worktree, while showing the approved plan, allowed-file
  preview, verifier, expected evidence path, return route, and exact CLI
  fallback. It then exposes confirmed
  `review-run` when a completed coder worktree run is waiting on the review
  gate, then `coder-commit-request` once the local review exists and mentions
  the coder run. After a commit request exists, the Goal Next Action card also
  exposes confirmed
  `approve-coder-commit`, `commit-coder-worktree`,
  `coder-publication-request`, `approve-coder-publication`, and
  `coder-publication-handoff` forms at the matching phases, then shows the
  manual publish boundary and copy-only publication handoff commands once the
  handoff is ready. After the operator manually finishes the push/PR work
  outside ClankerOS, the same manual boundary offers a confirmed
  `complete-goal` action that marks the local Goal completed and moves it into
  completed-goal lanes. These write local artifacts, approval rows, approval
  decisions, read-only delegation run evidence, bounded worktree run evidence,
  one isolated local worktree commit, or a local goal-status update without
  exposing arbitrary commands, pushing, creating PRs, deploying,
  calling providers, or mutating external systems. Goal pages also
  include a `Goal Resume Snapshot` that reads saved workspace state and opens
  with visible Now, Current, Saved, Artifact, and Safety cards before collapsed
  resume evidence, collapsed `Goal Workspace Restore State`, and a collapsed
  confirmed `save-workspace` form that returns to the same goal page after
  saving without writing on GET. Goal `Completion Readiness` summarizes the
  same workflow gates, local blockers, approvals, and publication handoff state
  used elsewhere on the Goal page into one finish posture. It opens with
  visible Now, Gates, Waiting, Publish, and Safety cards before collapsed
  readiness evidence, identifies the current blocker or next safe action,
  links the relevant local surface, reports no-write, no-network, and
  no-external-effect boundaries, and only exposes the confirmed `complete-goal`
  form after the manual publish handoff is ready.
  Goal `Incidents` now starts with a read-only `Goal Incident Command Bar`
  that summarizes open/resolved incidents, open recommendations, the first
  incident's severity, run, task, evidence, one triage surface, and no-write/
  no-provider/no-network/no-external-effect boundaries, then links to
  `/incidents`, shows open/resolved/total incident counts, and lists goal-owned
  incident status, severity, run, task, summary, and evidence artifact links
  without taking action.
  Goal `Remaining Work` now opens with visible Now, Gate Progress, Waiting,
  Open Work, and Finish cards, then keeps command proof and the gate-aware
  checklist collapsed by default. The hidden checklist remains sourced from
  local state and preserves the next action, current gate, open
  task/incident/recommendation counts, pending approvals, and
  done/pending/waiting status for scout, context-pack, implementation handoff,
  coder prep, worktree, review, commit, publication, and manual publish gates
  without taking action. A `Goal Task Closeout` panel follows the command cards
  and exposes a confirmed `complete-goal-task` action only when ready local
  publication-handoff evidence or a completed Goal can back the bookkeeping.
  While closeout is blocked, it routes back to the concrete current Goal action
  and visible action dock when available instead of generic continuation copy.
  The action marks one selected open task completed, updates the linked plan
  step when present, refreshes `TASKS.md` and plan artifacts, saves the
  workspace resume point, and records a timeline event. It does not run fresh
  verification, approve anything, push, create PRs, deploy, call providers, or
  mutate external systems.
  Goal `Memory` now links to `/memory`, shows project/global memory artifacts,
  goal-scoped memory entry counts, generated memory count, operator-note
  status, future-work count, latest memory summaries, and the fact that
  pinning remains available on the confirmed `/memory` surface rather than on
  the read-only Goal page. It starts with a read-only `Goal Memory Command Bar`
  that summarizes memory entry counts, memory artifact posture, operator-note
  state, future-work count, one next local memory action, and zero-effect
  counters as visible Now, Notes, Memory Bank, Pin, and Safety cards before
  collapsed command evidence and the detailed memory readback. The `/memory` surface now starts with a read-only
  `Memory Operator Workbench` so proposed-memory pins, operator-note review,
  future work, saved workspace resume, and empty-bank starts have one visible
  next click before shared diagnostics or inventory. Proposed memories also
  expose the first confirmed pin form directly in that top workbench so the
  operator does not have to scroll to the dense memory list. Confirmed
  `/memory` pinning promotes only entries
  with existing evidence artifacts and refreshes saved workspace state to that
  artifact with zero provider, network, or external mutation effects.
  The shared browser shell now exposes accessible shortcut metadata for Home,
  Today, Resume, Goals, Search, Workspace, Artifacts, Recent Items,
  Finish Today, palette, and theme controls, plus a compact primary/More route split. Dashboard, Today, Guide,
  Resume, Goals, Search, and Workspace stay visible for daily operation, while
  advanced routes stay available under `More` and in the command palette.
  `More` opens automatically when the current route is secondary. The shell
  also exposes a global next-action shortcut. `n` opens the current
  recommended next-action target and displays the resolved action label in the
  shared header instead of a generic `Next` label. When the current Goal action
  has a confirmed browser form, `n` opens the Goal Action Dock, using
  `#goal-action-dock-form` on that Goal page or
  `/goals/<goal_id>#goal-action-dock-form` from other routes. `w` opens
  `/workspace`, `a` opens `/artifacts`, `v` opens the browser-local
  Recent Items rail, and `f` opens the
  route-local Finish Today form on `/today` (`#today-finish`) or
  `/goals/<goal_id>` (`#goal-finish-today`), plus the route-local forms on
  `/workflow`, `/actions`, `/verification`, project detail pages, run detail
  pages, `/inbox`, `/approvals`, and `/incidents`, before falling back to
  `/workspace#save-workspace` elsewhere. The palette can be closed with Escape
  even while the search input is focused; the shortcut layer remains
  local-only and creates no server writes.
  The command palette also
  starts with a route-aware `Current Page` block that mirrors the current
  path, parent surface, resolved Goal/Project/run context, focus target,
  `/resume`, and zero-effect readbacks before the visible keyboard-shortcut
  help block generated from the same shortcut map, so operators can discover
  both where they are and the local navigation shortcuts from inside the app
  instead of reading external docs. When a saved or lead Goal exists, the
  command palette also includes a compact Goal continuation readback for the
  current workflow gate, the next few local gates, their target surfaces, and
  the manual publish boundary without writing on GET. Its Focus and Quick
  Switch action cards use the exact current action label, such as `Create
  commit request`, instead of generic current-action copy.
  The Goal `Skills Used` section starts with a read-only `Goal Skills Command
  Bar` that summarizes task skill tags, matching generated or available local
  skill records, usage and project counts, delegation profile usage, one
  `/skills` or `/profiles` review target, and no-execution/no-install/
  no-network boundaries as visible Now, Record, Usage, Profile, and Safety
  cards before collapsed command evidence and the detailed skill readback.
  Goal `Git Status` starts with a read-only `Goal Git Command Bar` that
  summarizes the registered project root, branch, commit, clean/dirty posture,
  tracked and untracked counts, latest goal-linked `git_status.txt` artifact,
  one next local surface, and no-fetch/no-write/no-network/no-external-effect
  boundaries as visible Now, Branch, Changes, Proof, and Safety cards before
  collapsed command evidence and the repository snapshot.
  Goal `Delegations` starts with a read-only `Goal Delegation Command Bar`
  that opens with visible Now, Latest, Workflow, Handoff, and Safety cards,
  while command evidence keeps scout delegation counts, context-pack readiness,
  implementation handoff readiness, coder-prep packets, worktree plans, the
  latest delegation workflow surface, one next local continuation, and
  zero-effect counters collapsed before the detailed delegation rows.
  Goal `Runs` starts with a read-only `Goal Run Command Bar` that summarizes
  task and worktree run counts, reviewed and blocked run gates, changed-file
  posture, latest run evidence, one next local run action, and zero-effect
  counters as visible Now, Latest Run, Review, Changes, and Safety cards
  before collapsed command evidence and the detailed run rows.
  Goal `Approvals` starts with a read-only `Goal Approval Command Bar` that
  summarizes pending and approved worktree, commit, and publication approval
  gates, selects one local approval or continuation surface as visible Now,
  Pending, Approved, Downstream, and Safety cards, and reports write-on-GET/
  provider/network/external-effect counters inside collapsed command evidence
  before the detailed approval rows.
  Goal `Incidents` starts with a read-only `Goal Incident Command Bar` that
  opens with visible Now, Open, First, Recovery, and Safety cards while keeping
  incident/recommendation counts, first incident evidence, one triage surface,
  and zero-effect counters in collapsed command evidence before the detailed
  incident rows.
  Goal `Evidence` starts with a read-only `Goal Evidence Command Bar` that
  summarizes run evidence, worktree evidence, incident evidence,
  recommendation evidence, typed artifact counts, latest artifact label, raw
  latest-artifact href, one local review target, and zero-effect boundaries
  through visible Now, Latest, Inventory, Attention, and Safety cards before
  collapsed command evidence, the read-only `Goal Evidence Digest`, the
  collapsed detailed evidence list, and the typed artifact explorer. The digest
  adds Proof, Latest, Run Proof, Artifact Mix, CI Proof, and Safety cards
  sourced from existing local evidence/artifact records and operator-supplied
  CI proof.
  Goal `Verification Evidence` starts with a read-only
  `Goal Verification Command Bar` that exposes visible Now, Current, Latest,
  Record, and Safety cards for project-scoped proof status, checkout freshness,
  one proof action, recording posture, and zero-fetch/zero-effect boundaries
  before collapsed command evidence and collapsed proof lines. It links to
  `/verification` and `/ci-evidence`, filters local operator-supplied CI proof
  records to the current goal project, compares the recorded branch/commit to
  the current project checkout, distinguishes missing, stale, job-scoped early
  proof, and current full workflow proof, and reports missing or stale proof
  without fetching GitHub status. It also exposes a confirmed Goal-scoped
  `ci-snapshot-evidence-from-gh-json` form that accepts pasted GitHub Actions
  JSON, infers run identity from `databaseId`/`url`, validates status, branch,
  commit, and optional job status, then records local project CI proof and
  returns to the same Goal page without app-side GitHub polling.
  They also include a typed
  `Goal Artifact Explorer` that groups goal-linked Markdown,
  JSON, Patch/Diff, and Text/Log artifacts and links them through the bounded
  inert `/artifacts` viewer without raw filesystem browsing. Goal `Artifacts`
  starts with a read-only `Goal Artifact Command Bar` that summarizes artifact
  record counts, available/missing posture, render-family counts,
  source-family counts, the latest artifact label, raw latest-artifact href,
  one bounded review click, and zero-effect counters through visible Open,
  Latest, Types, Inventory, and Safety cards before collapsed command evidence
  and the collapsed detailed artifact list. The typed explorer now starts with
  a browser-local
  `Goal Artifact Filter` that narrows already-rendered artifact rows by
  Markdown/JSON/Patch/Text type, source, or text query, restores that view per
  Goal from `localStorage:clankeros-goal-artifact-filter:<goal_id>`, and
  exposes Reset filter while preserving read-only GET, no-provider,
  no-network, no-raw-filesystem, and no-external-effect boundaries.
  A browser-local `Goal Artifact Reader` follows the filter, renders one
  already-registered artifact inline through the same bounded inert Markdown,
  JSON, patch/diff, text, and log renderers used by `/artifacts`, opens with a
  visible Selected/Type/Source/Open/Safety focus strip, labels the full-artifact
  link in operator language such as `Open coder run <run_id> review`, remembers the
  selected preview per Goal in
  `localStorage:clankeros-goal-artifact-reader:<goal_id>`, and exposes Reset
  reader while preserving the same zero-effect boundaries.
  The artifact
  viewer now opens with an `Artifact Operator Workbench`, reports render
  family/renderer posture, and renders Markdown as escaped headings/lists/
  paragraphs, JSON as pretty-printed text, then shows an
  `Artifact Relationship Map` for Goal/project/delegation/run/workspace
  return paths before dense command evidence. Stored Goal artifact links render
  title-first while keeping raw Goal ids and label-source evidence in collapsed
  proof. Patch/diff artifacts render with
  scan-friendly line classes, and text/log artifacts as inert text while
  keeping content execution disabled. It also exposes a confirmed local
  `save-workspace` form so the operator can remember the current artifact as
  the next-session resume anchor without writing on GET. Every page shares
  a browser operator shell with a read-only `Operator Ribbon`, `Route Context`
  breadcrumb strip, recent local items, a read-only `Last Action` strip after
  confirmed local actions, a command palette, keyboard shortcuts, local Focus
  mode, and a theme toggle. The shared header includes a visible `Keys`
  control plus `?` shortcut that opens a browser-local keyboard-help dialog
  with the same shortcut list and zero-effect evidence outside the palette.
  Focus mode is toggled by the header `Focus` control
  or `m`, persists only in browser `localStorage`, and collapses the side rails
  while keeping the ribbon and page content available. The ribbon sits above the
  shell and keeps the current page's primary
  action, Goal/project, attention count, `/resume`, `/search`, and collapsed
  zero-effect readback visible before the page-specific workbench. The last
  action strip reads `.clanker/app/workspace.json` and exposes the latest
  completed local action, result, notice target, saved project/goal context,
  timestamp, and zero-effect counters without writing on GET. Action notice
  pages now open with a Next Step card sourced from first-run or saved-Goal
  state, so completed-action notices route directly to the next confirmed form
  or workflow surface while keeping notice evidence read-only. The route
  context strip now starts with a compact action-first focus grid for the
  current page, next local action, back target, Goal, Project, and `/resume`,
  while route family/path, saved workspace anchors, focus target, and
  zero-effect boundaries stay available inside collapsed `Route evidence`
  before the page body. The
  recent-items sidebar now starts with a read-only `Recent Items Command Bar`
  and a visible return dock for Recent, Workspace, Action, and Artifact. It
  links the primary recent surface, saved project/Goal when present, the live
  Goal action when a Goal exists, last action notice when no Goal action is
  available, saved artifact when present, and safe fallback surfaces otherwise.
  The Action card uses the same Goal action dock target as the command palette
  instead of detouring through the generic `/actions` catalog, and the longer
  Recent shortcuts list prepends the same live Goal action as
  `current-action` so filter/search behavior matches the visible Action card.
  The Artifact card also hydrates after load from
  browser-local `localStorage:clankeros-last-artifact`, so the last opened
  artifact can be reopened globally before the operator explicitly saves it to
  workspace state. Workspace/goal/delegation/run counts, saved
  workspace project/goal/artifact context, last-action context, and zero-effect
  boundaries stay inside collapsed evidence with the longer recent-link list
  in a second collapsed disclosure. A browser-local `Viewed Pages` panel
  records local app routes in `localStorage:clankeros-route-history`, dedupes
  by href, keeps the 12 most recent entries, exposes a clear button, and adds
  those viewed routes to the command palette after localStorage readback
  without writing server state. The shared shell also remembers route-scoped
  open/closed `<details>` panels in `localStorage:clankeros-open-panels:<route>`
  after the browser has saved state for that route, so expanded evidence panels
  survive reloads on long operator pages; `/workspace#workspace-view-memory`
  inventories and clears those browser-local entries without changing
  `.clanker/app/workspace.json`. The same shell remembers route-scoped scroll
  position in `localStorage:clankeros-scroll-position:<route>` after operator
  scrolling, restores long pages near the prior working spot, and skips that
  restoration when the URL contains a hash anchor.
  The command palette now also includes a visible `Quick Switch` dock for
  Continue, Workspace, Action, Artifact, and Finish, so the keyboard launcher
  can reopen the current Goal, saved workspace, latest local action target,
  latest artifact, or the route-aware Finish Today handoff without expanding
  the sidebar. Saved exact Goal action routes in that dock use the same
  operator-facing current-action label as `/resume`, such as
  `Create commit request`, while project-only saved routes keep their project
  label. When no saved workspace surface is stronger, the current Goal fallback
  also resolves to the action dock and uses the concrete action label. The
  visible `Palette Results` list filters local routes and
  recent work on input, prepends the live Goal action as `current-action` when
  available, supports ArrowDown/ArrowUp plus Enter for active local result
  navigation, and keeps full `/search` as the explicit fallback. It also
  includes a browser-local Last Artifact result backed by
  `localStorage:clankeros-last-artifact`, so keyboard-first resume can reopen
  the last viewed artifact before canonical workspace save. It starts with the same
  current-page route context, parent link, resolved Goal/Project/run context,
  focus target, `/resume`, and zero-effect readbacks inside the
  keyboard-driven surface. The shared focus strip and command palette include
  the same goal-aware current-action readback from the saved workspace goal or
  current lead goal, showing phase, one recommended action, target surface, a
  compact current-gate continuation readback, zero-effect readbacks, and the
  same confirmed local action form as the Goal page when the current next
  action is browser-available. In
  first-run states, those shared surfaces point at the concrete setup form for
  the current route when possible, or at the Home/Today/Goals first-run anchors
  when the current page does not render the guide.
  The shared shell also exposes `n` as a global next-action shortcut and a
  matching header control labeled with the concrete operator move, such as
  `Create Project` or `Create commit request`. It resolves from the same
  saved-workspace or lead-Goal focus context as the ribbon and palette; when a
  confirmed browser action form is available, `n` opens the existing
  `Operator Focus` details panel instead of submitting it. The shortcut
  remains local navigation only
  and records no provider, network, write, approval, execution, push, PR, or
  deploy effects on GET.
  They still write nothing on GET and only submit existing local forms after
  explicit confirmation. The workflow page
  can be
  scoped with a
  delegation or coder run id. It is action-first and opens with a visible
  `Workflow Operator Workbench` before shared route/focus diagnostics or
  command readback, with cards for the current workflow action, selected
  state, queue attention, and `/resume`. A visible read-only
  `Workflow Scope Picker` follows with the primary pickup, recent delegation
  and coder-run choices, parent Goal link, and zero-effect safety evidence so
  direct `/workflow` visits can select a concrete scope before the stage map.
  A visible read-only
  `Workflow Journey` follows with nine stage cards that mark the current stage
  and route each stage to the next safe local surface. A visible
  `Workflow Live State` panel follows with local page reload polling every five
  seconds, pause rules for focused form fields and hidden tabs, a manual
  refresh button, current stage/position/target/resume readbacks, and
  zero-effect evidence. A visible
  `Workflow Finish Today` handoff follows with a confirmed local workspace
  save form that persists the exact scoped workflow route for `/resume`.
  The shared shell's route-aware Finish shortcut now opens that same
  `#workflow-finish-today` form from `/workflow`, and uses the matching
  same-page Finish forms on `/actions`, `/verification`, project detail pages,
  run detail pages, `/inbox`, `/approvals`, and `/incidents` instead of
  sending those operator routes to the generic Workspace save form.
  Journey, live-state, finish, and command evidence stay collapsed by default
  while preserving selected delegation/run, parent Goal, project, current
  stage, journey position, exact resume surface, next local action, target
  surface, reason, selected-step count, and zero-effect readbacks in the DOM.
  The page then annotates related
  stepper rows with selected local artifact, approval, run, commit,
  publication, and next-action status, plus a read-only `Selected Workflow
  Continuation` block linking the exact run, approvals, inbox, and dogfooding
  surfaces without creating external effects. Coder worktree
  run detail pages include a read-only `Run Command Bar` that summarizes run
  status, review gate, commit/publication state, changed-file count, diff
  summary, next local action, target surface, and no-write/no-network/
  no-external-effect boundaries. A read-only `Run Readiness Strip` follows with
  five scan-first cards for run status, review gate, bounded evidence, next
  local action, and safety posture, plus evidence fields for current gate,
  gate progress, action-form availability, target surface, and zero-effect
  counters. A `Run Operator Workbench` follows it with do/check/unblock/finish
  cards, same-page action anchors, review/evidence links, approvals, parent
  Goal, and a confirmed `save-workspace` form that stores the run plus
  review/evidence artifact as a future resume point without writing on GET.
  Delegation execution run detail pages now render the
  current form-backed continuation action inline at
  `#delegation-run-continuation-action-form`; `prepare_coder_from_handoff`
  keeps the implementation handoff, run, project, Goal, return, and resume
  fields on the run page while preserving `/delegations/<id>#safe-local-actions`
  as source/fallback evidence and still using the existing `/actions/<action>`
  confirmation route. When the current coder run gate has a safe confirmed local
  action, the workbench renders it inline at `#run-workbench-action-form`,
  promotes that form as the primary Do Now target, and preserves the original
  gate surface as source evidence. Commit request, local commit, publication
  request, and publication handoff still use the existing `/actions/<action>`
  confirmation routes. A read-only `Run Gate Map` then marks the current
  eight-step run path from review through local commit, publication handoff,
  and manual publish outside ClankerOS. The map links only to existing local
  anchors or `/approvals`, counts done/waiting/blocked gates, and adds no
  action authority. A read-only `Run Continuation Strip`
  follows the map and gives the operator five visible cards for the current
  gate, scoped approvals, evidence, parent Goal, and manual publication
  boundary before the dense workflow state. The page then shows the same
  upstream and downstream workflow posture as a `Run Workflow State` readback,
  plus a `Run Review Gate` readback that mirrors the backend requirement that
  `runs/<source_run_id>/review.md` exists and mentions the coder worktree run
  id before `coder-commit-request` is offered. A read-only `Run Evidence Map`
  then turns review, diff, changed files, bounded validation, logs, and
  verification output into visible cards backed only by bounded artifact
  viewer links before the full evidence list. Once publication handoff is
  ready they show copy-only suggested push and draft-PR commands plus the PR
  body path with zero-effect counters. Run-scoped approval links use
  `/approvals?run_id=<coder_run_id>` so the approval page foregrounds the
  matching commit or publication decision ahead of unrelated queue items, and
  commit/publication approval decisions return to the owning run page after
  confirmation.
  The root `/` app page is now an action-first Goal-First Home board: the
  Home operating surface renders before the shared route/focus diagnostics,
  while Home state and board evidence remain available in collapsed details.
  It starts with a read-only `Home Operator Board` that condenses the lead
  goal or first-run step into visible Do Now, Attention, Resume, and Proof
  cards with action-form routing, scoped approval links, resume readiness,
  waiting counts, and CI proof posture. Home also includes active, paused, and
  completed goal lanes through a scan-first `Home Goal Board` with a
  browser-local Find box, lane mode buttons, live match count, first-match
  jump, no-match empty state, visible View status, reload persistence in
  `localStorage:clankeros-home-goal-board-view`, and reset coverage in
  `/workspace#workspace-view-memory`. It continues with recent activity whose
  Artifacts card carries the latest Goal artifact from the bounded artifact
  registry into a concrete `/artifacts?path=...` action such as
  `Open coder run <run_id> review`, even when newer run/approval events fill
  the recent timeline window, inbox counts, recommendations,
  incidents, saved workspace resume links, saved-goal phase and next-action
  readbacks, a read-only `Start Here` cockpit that condenses the
  lead goal or first-run step, one primary action, target surface, resume
  readiness, waiting counts, and CI handoff posture into a single scan-friendly panel, a
  form-backed `Home Day Plan` that names the current goal, current phase, one
  next action, waiting counts, end-of-day resume readiness from saved
  workspace state, and a confirmed local `save-workspace` Finish Today form
  that records the lead goal, latest artifact, and exact current action
  `resume_surface` as tomorrow's resume point after confirmation, a
  `Home Resume Workspace` whose `Remember Current Goal` form now also stores
  the lead Goal's exact current action `resume_surface` and exposes
  `home_resume_remember_resume_surface` with the same action label,
  the shared shell's `Finish` button, `f` shortcut, Operator Ribbon Finish
  card, and command palette Finish card now route populated Home sessions to
  that same-page `#home-finish-today` form instead of detouring to Workspace,
  while empty first-run Home keeps the `/workspace#save-workspace` fallback,
  a read-only
  `Home Attention Brief` with visible Now,
  Inbox, Approvals, Incidents, Recommendations, and Proof cards for existing
  approvals, incidents, recommendations, inbox load, and local CI proof posture
  before deeper goal work without fetching GitHub status, a
  read-only `Home Focus Queue` that lists next actions,
  phase, target surface, progress, and waiting counts across active and paused
  goals, the same confirmed local action form as the Goal page when the saved
  goal's next action is browser-available, a `/resume` landing link, an
  explicit `save-workspace` form for the current lead goal when one exists,
  and a state-aware first-run project/goal/delegation guide until the first
  delegation is completed. In first-run states, Home Live State, Start Here,
  Home Day Plan, Home Attention Brief, and Home Focus Queue target the
  same-page `Create Project` or `Create First Goal` form instead of requiring
  a `/goals` detour. The first-run guide starts with a read-only
  `First Run Command Bar` that names the current first-run step, one next
  action, target surface, form surface, Goal/delegation context, confirmation
  posture, and zero-effect counters. It then shows a read-only
  `First Run Launchpad` with guided setup, demo, workflow, verification, and
  health cards before the progress strip, so fresh operators can choose the
  right browser path without reading docs first. It then shows a read-only
  `First Run Next Step` panel with one primary same-page action plus setup,
  handoff, resume, and safety cards, so the current click is obvious before the
  operator reads the full checklist. It then shows a visible read-only
  `First Run Action Ladder` with five Project, Goal, Delegation, Context, and
  Run cards, highlighting the current action and recording the exact browser
  target, action name, confirmation posture, and zero-effect counters before
  the checklist. It then shows a visible read-only
  `First Run Empty State Map` with a text-only
  `Project -> Goal -> Delegation -> Context -> Run` illustration and step
  cards, so a blank checkout still has a concrete path. It then shows a browser-local
  `First Run Checklist` that lets operators mark setup checks and keep a short
  return note in `localStorage:clankeros-first-run-checklist`, while the real
  Project, Goal, Delegation, Context, and Run statuses still come from
  ClankerOS state and the page keeps GET rendering read-only. It then shows a
  read-only
  `First Run Progress` strip with a progress bar and five step cards for
  Project, Goal, Delegation, Context, and Run, keeping detailed status evidence
  collapsed and preserving no-write/provider/network/external-effect
  counters; after a Goal exists, it can render the same confirmed local
  next-action form inline for scout delegation, context-pack generation, and
  first delegation execution. Those three forms, confirmation pages, and
  result pages use operator language (`Create scout delegation`,
  `Generate context pack`, `Run scout delegation`) while preserving raw
  `delegate`, `context-pack`, and `run-delegation` action ids in evidence.
  The later day-to-day workflow forms now do the same for coder prep,
  worktree planning and approval, commit request/approval/local commit, and
  publication request/approval/handoff, so visible controls use verbs such as
  `Prepare coder packet`, `Approve commit`, and `Prepare publication handoff`
  while raw action ids remain in URLs, DOM metadata, and evidence.
  Form-backed current-action CTAs on Goal, Home, Action Notice, and delegation
  run continuation surfaces now use those same verbs directly, so the primary
  click names the work it will prepare while the underlying confirmation route
  and raw action evidence remain unchanged.
  Active first-run Goal pages also show a
  read-only `Goal First Run Rail` between Attention and the Goal Command Bar,
  preserving the Project -> Goal -> Delegation -> Context -> Run path on the
  Goal page and pointing the current gate at the existing confirmed Goal action
  form. After a confirmed
  `register-project` action, `Action Result Details` can also continue the
  first-run browser path before a saved Goal exists by rendering the
  confirmation-required `create-goal` form inline plus Home and Today fallback
  targets, without writing on GET.
  Coder worktree run rows in review,
  dashboard, and the local app include changed-file counts and compact diff
  summaries read from existing evidence. The app also includes a read-only
  `/delegation-runs` index for scout/delegation execution evidence, context
  pack and implementation handoff links, zero-effect counters, retry signals,
  and next local operator actions; `/runs/<run_id>` now also recognizes
  delegation execution run ids and renders a read-only `Delegation Run
  Continuation` strip before the detailed scout evidence, with visible Now,
  Workflow, Handoff, Artifacts, and Goal cards plus an inline
  `#delegation-run-continuation-action-form` when the next action is
  form-backed, preserving the original Safe Local Actions surface as source
  evidence while the form posts through the existing confirmation flow; the
  strip also keeps context-pack/handoff status, retry/incident state,
  zero-effect counters, and next-action readback; a read-only content-first
  `/actions` catalog that opens with the
  safe action header and `Action Operator Workbench` before shared route/focus
  diagnostics, reading first-run or lead-Goal focus, naming the current local
  action, linking the owning surface for the confirmed form, routing blockers,
  and providing a confirmed project/Goal resume save point without adding
  action authority to the catalog page. A visible read-only
  `Action Workflow Map` then arranges browser actions into Setup, Scout,
  Context, Prep, Approval, Execute, Commit, Publish, and Proof stages, marks
  the current stage from the same first-run or lead-Goal focus, and links each
  stage to its existing safe local surface, followed by an
  `Action Catalog Command Bar` with visible Catalog, Forms, Approvals, and
  Boundary cards while safe local action counts, target anchors, local
  execution/git/approval/artifact posture, confirmation posture, form
  locations, output artifacts, and external-effect boundaries stay available
  in collapsed evidence; a read-only
  `/verification` handoff for the checked-in GitHub
  Actions workflow, separate fast-smoke and full-suite job readbacks,
  configured job timeout, latest operator-supplied CI evidence summary,
  compact local checks, in-progress run non-proof guidance, and CI proof
  boundary without contacting GitHub; the page also shows a display-only
  direct `ci-snapshot-handoff`, `gh run view`, JSON-validated
  `ci-snapshot-evidence-from-gh-json`, and manual record-after-success
  templates from current branch/commit state; a
  read-only `/ci-evidence` page for operator-supplied CI/deploy proof records
  already stored in local ClankerOS state, plus a `CI Evidence Recording Guide`
  with the latest local GitHub handoff id, branch, commit, handoff evidence,
  a handoff-specific `ci-deploy-evidence` command template when available, and
  direct pushed-snapshot `ci-snapshot-handoff` and
  `ci-snapshot-evidence-from-gh-json` templates, without fetching GitHub
  status; `/ci-evidence` also exposes a confirmed local
  `ci-snapshot-evidence-from-gh-json` form that records proof from pasted
  GitHub status JSON after validating completed/success status, commit SHA,
  and branch, inferring the run id and URL from `databaseId`/`url` when the
  operator leaves those form fields blank; `/ci-evidence` now includes a
  `CI Proof Workbench` with four
  browser-first cards for checking a pushed run, recording fast-smoke proof,
  recording full-suite proof, or using the manual record-after-success
  fallback, with copy-only `gh run view` / validated recorder templates behind
  compact per-card command disclosures, a browser-local `CI JSON Assistant`
  for copy/paste and job-name fill, and explicit fast-smoke-versus-full-suite
  proof boundaries, while still performing no GitHub polling; a
  read-only root dashboard `Verification Snapshot` for checked-in workflow
  timeout, latest operator-supplied CI evidence, `/verification`,
  `/ci-evidence`, and current direct-snapshot handoff templates without
  contacting GitHub; a read-only root dashboard
  `Dashboard Dogfooding Snapshot` for fixture availability, next dogfooding
  action, selected workflow/run links, and the `/demo` manual browser script
  surface; a read-only `/dogfooding` operator workbench that now opens the
  page before shared diagnostics with Do Now, ClankerOS, Workflow, and Proof
  cards before the longer checklist, while keeping dogfooding workbench and
  fixture/command evidence collapsed by default; a read-only `/dogfooding` GitHub
  Actions follow-up section with direct pushed-snapshot `ci-snapshot-handoff`,
  `gh run view`, JSON-validated record, and manual record-after-success
  templates for the current checkout; a
  read-only `/actions` current-demo action surface map that links fixture state
  to the selected project, delegation, workflow, run, approvals, and inbox
  surfaces; a read-only `/dogfooding` checklist and next-action panel for the
  first browser route walk, fixture refresh, scoped workflow/run links, local
  commit/publication gate sequence, and GitHub Actions handoff boundary
  without fetching GitHub status; `/health` opens with a `Health Operator
  Workbench` that turns warning count, bind scope, branch/commit,
  storage/import readiness, the refreshed local status artifact, explicit
  `status_artifact_write_on_get=true`, one next local surface, and zero
  provider/network/external-effect counters into visible cards, followed by a
  `Health Readiness Strip` for local bind scope, storage, workflow imports,
  next local action, and the status-artifact-only safety boundary before the
  collapsed command/diagnostic evidence; a read-only
  operator inbox plus local approval and
  incident pages for pending worktree, commit, and publication decisions,
  with the inbox opening from an `Inbox Operator Workbench` before shared
  route/focus diagnostics or command readback. The workbench shows
  do/inspect/Goal/finish cards, Goal/delegation/run/evidence routing, a
  continuation surface, and a confirmed `save-workspace` form in a collapsed
  Finish Today section that stores the queue as a future resume point without
  writing on GET. Approval-backed worktree, commit, and publication Inbox
  items can render their existing confirmation-gated local decision form
  directly in the workbench; `/inbox?run_id=<coder_run_id>` scopes that top
  workbench queue to the run so commit/publication approvals are not masked by
  unrelated global items. Inbox and approval queue Goal cards now use the human Goal
  title when available, while raw Goal ids and label-source fields stay in
  collapsed evidence for durable review. A visible read-only `Inbox Triage Board` follows with
  Attention, Decisions, Work, Publication, and Finish Today lane cards so the
  operator can see queue counts and first targets before the long category
  lists. A read-only `Inbox Next Item Brief` then promotes the first queue
  item into Next, Inspect, Evidence, After, and Safety cards, preserving the
  queue anchor, inspection route, bounded artifact target or queue fallback,
  follow-up surface, and zero-effect proof before the dense lists. A
  read-only
  `Inbox Command Bar` follows with total local queue size, queue-type counts,
  the first attention item, target section, reason, and zero-effect boundary
  inside collapsed evidence. A browser-local `Inbox Queue Filter` then narrows
  already-rendered rows by attention, decisions, work, publication, current
  route scope, or text, remembers lane/query in
  `localStorage:clankeros-inbox-queue-filter`, and resets without deciding,
  approving, executing, calling providers, or mutating external systems while
  preserving read-only run links and
  next-action cues for pending commit/publication rows,
  with `/approvals` starting from a visible readiness strip, queue summary, and a read-only
  `Approval Decision Brief` that links the first local decision to its
  delegation, workflow, run when available, request artifact, evidence
  artifact, exact form anchor, post-decision surface, and zero-effect counters,
  with commit/publication approval rows linking back to the relevant run and
  naming the next local-only follow-up action after approval,
  operator-worthy queue items, incident evidence readback, a confirmed
  dashboard refresh action for rewriting the local app status artifact from
  current repo and route state, a read-only state-aware root dashboard
  recommendation that points to the next operator surface, and a state-aware
  `/demo` launchpad that opens with a read-only `Demo Operator Workbench` for
  Now, Project, Workflow, and Proof before shared diagnostics or command
  readback. A read-only `Demo Walkthrough Map` follows with Fixture,
  Project + Goal, Workflow, Run, Approval, Publish Boundary, and Resume + Proof
  cards before the command readback, making the full product tour visible
  without reading the manual browser script first. Demo workbench,
  walkthrough, and command evidence stay collapsed by default while preserving
  fixture availability, preferred demo command, compatibility command,
  selected project/Goal/delegation/run, next local surface, and zero-effect
  counters; it then links the fixture project, selected workflow,
  delegation, coder worktree run, review artifact, inbox, approvals, first
  manual browser dogfooding script, a read-only next-action panel, and a
  browser-progress checklist for commit/publication handoff status, plus a
  read-only `Demo Gate Artifacts` map for commit request, commit decision,
  local commit, publication request, publication decision, publication
  handoff, and PR-body artifacts as those gates become available, plus a
  state-aware `Demo Gate Actions` panel that names the current gate, local
  form action, required input, expected output artifact, and renders the safe
  confirmed local form for the active gate when one exists. Supported active
  gate text fields preserve unsent drafts in browser-local storage across
  reloads until cleared or confirmed. At the manual
  push/PR boundary it keeps publication outside ClankerOS, exposes only the
  confirmed local `complete-goal` form, and advances completed fixture Goals
  to `review_completed_goal_evidence`, plus `Manual
  Browser Checkpoints` route-marker expectations for the first visual
  dogfooding pass. The demo also seeds a generated local `local-files` skill
  record and `SKILL.md`, so `/skills` and Goal `Skills Used` show a concrete
  available/generated skill with usage, last-used, project, and artifact link
  readbacks instead of an empty placeholder.
  The app reads existing SQLite state and repo artifacts, writes a local
  health/status artifact with current warning readbacks, and exposes only
  explicit local forms for safe
  artifact-producing and approval-producing actions. Confirmation pages render
  a read-only `Action Preflight` first, with visible Confirm, Returns, Local
  Write, Context, and Boundary cards plus collapsed preflight evidence for the
  submitted return route, project/Goal context, artifact, field count, and
  zero-effect counters. The existing read-only `Action Confirmation Review`,
  `Action Confirmation Command Bar`, submitted action payload, and safety
  boundary remain available before a confirmed local write, local approval
  decision, or bounded local execution; confirmed action result pages
  now open with an action-first `Action Complete` surface containing Continue,
  Completed, Artifact, Workflow, and Boundary cards plus collapsed
  result-command evidence. The Workflow card uses the concrete refreshed next
  operator action, such as `Create first goal` or `Approve commit`, instead of
  generic continuation copy. An `Action Result Next Step` panel follows the
  command bar and turns the refreshed first-run or saved-Goal state into the
  next visible operator move, rendering the same confirmed browser form inline
  when one exists while preserving the confirmation boundary before local
  writes or local execution. For saved-Goal continuations, that panel also
  renders a visible `Continue Goal` block before the form with Goal, phase,
  next action, form availability, confirmation posture, and zero-effect
  evidence. A `Resume Tomorrow` receipt follows and reads
  `.clanker/app/workspace.json` back as the operator's return path, with
  visible Resume Tomorrow, Context, Artifact, Last Action, and Boundary cards.
  When first-run setup is incomplete and no Goal is saved yet, the primary
  Resume Tomorrow link routes through `/resume#resume-first-run-action-form`
  so the operator lands on the next setup form while the receipt evidence keeps
  the raw saved project surface. Its `Action Resume Receipt` evidence
  preserves the saved project, Goal, exact resume surface, latest artifact,
  updater, last action/result,
  readiness, and zero-effect counters, before preserving the submitted payload,
  local result fields, artifact links, next-page link, safety boundary, and an
  `Action Continuation` block from the refreshed saved goal state with phase,
  one next action, target surface, and the same confirmed local action form
  when available; when no saved Goal exists, the continuation falls back to
  first-run progress and can render the next confirmation-required first-run
  form inline. Confirmed result pages also render an `Action Result Workflow
  Map` from refreshed first-run or saved-Goal state with the current gate,
  next action, next local surface, progress counts, and manual-publish
  boundary while preserving the no-write-on-GET and no-provider/no-network/
  no-push/no-PR/no-deploy boundary. Successful action results are recorded as
  last-action workspace fields so the global shell and `/resume` can reopen
  the target notice after navigation without granting new action authority.
  GET pages reached through a notice link now render an escaped action-first
  `Action Notice` surface with Continue Here, Last Action, Resume, Details,
  and Boundary cards plus collapsed notice/workspace evidence before the
  target page content. When saved Goal state exposes a confirmed next action
  form, the notice renders an inline `Action Notice Next Step` form and points
  the primary notice action at the same-page form while preserving the
  original Goal/workflow source surface in evidence, without writing on GET or
  adding action authority;
  action error pages now open with an action-first `Action Needs Attention`
  recovery surface containing Fix Input, Retry Surface, Error, Catalog, and
  Boundary cards before preserving the attempted action, submitted payload,
  error details, and a no-action-completed non-claim in collapsed/anchored
  evidence. It does not push, create PRs,
  deploy, call providers, execute arbitrary commands, or use the network
  beyond local browser/server loopback.
- Local app smoke testing: `app-smoke-test` renders the core local app routes
  without starting a server, requires route-specific page markers such as
  `ClankerOS Local Operator`, `Modern Operator Workflow`, `Safe Action
  Catalog`, `Verification Handoff`, and `CI Evidence Records`, and reports
  `marker=matched` or `marker=missing` per route while preserving
  provider/network/external-mutation counters at zero. The browser demo path
  now starts at `/demo#demo-fixture-action`, where an explicit confirmation
  creates or refreshes the same deterministic fixture while preserving the CLI
  commands as fallbacks. `app-demo-smoke-test`
  creates the fixture-backed demo state and renders the stateful demo,
  dogfooding, goal, search, workspace, memory, skills, profiles, project,
  delegation, scoped workflow, run, approvals, inbox,
  actions, and health routes with expected snippet checks while preserving the
  same zero provider/network/external-mutation counters. The checked-in GitHub
  Actions workflow now runs a separate 10-minute `smoke` job for compile,
  local CLI smoke, route-marker app smoke, fixture-backed app-demo smoke,
  demo, dashboard, iterate, focused local-app/CI-handoff pytest, and
  whitespace checks before a dependent 45-minute `full-suite` job spends time
  on `python -m pytest -q`.
- CI/deploy evidence ingestion: an operator can attach CI or deploy proof to a
  GitHub handoff packet with `ci-deploy-evidence`. The record preserves
  provider, external run id, URL, commit, branch, handoff, and JSON evidence
  while recording `network_actions_taken=0`; it does not fetch CI, run CI, or
  deploy. Direct operator-authorized pushed snapshots can use
  `ci-snapshot-evidence` to record the completed GitHub Actions run id and URL
  against project, branch, and commit without fabricating a publication
  handoff. While a direct pushed-snapshot run is still pending,
  `ci-snapshot-handoff` prints the exact `gh run view` check command and
  matching `ci-snapshot-evidence-from-gh-json` pipeline plus the manual
  record-after-success command without fetching GitHub status or writing
  proof. `ci-snapshot-evidence-from-gh-json` consumes supplied `gh run view`
  JSON from stdin or a file, infers the run id and URL from `databaseId`/`url`,
  requires a completed successful run with the expected commit SHA and
  matching branch when present, then records local proof. It can also take
  `--job-name "Fast smoke verification"` to validate one completed successful
  GitHub Actions job from an in-progress workflow run and record scoped early
  route/CLI proof with
  `status_source=github_status_json_job`; that record is not full-suite proof.
  The local app mirrors those commands as display-only templates on
  `/`, `/verification`, `/ci-evidence`, and `/dogfooding`, and `/ci-evidence`
  can record the same proof from pasted status JSON plus an optional job name
  through a confirmed local form. Snapshot records are
  surfaced separately in `/verification`, `/ci-evidence`, and the static
  dashboard, record `network_actions_taken=0` and `external_mutations_taken=0`,
  and do not fetch GitHub status, run CI, deploy, push, create PRs, call
  providers, or mutate external systems.
- Profile routing: safe default planner, coder, scout, tester, and evaluator
  profiles plus routing rules can be materialized into SQLite and
  `.clanker/profiles.yml`. `route` records task/category selection decisions,
  including operator overrides, without claiming tasks, dispatching subagents,
  calling model providers, or changing approval gates.
- Subagent delegation records: `delegate` consumes a task routing decision and
  stores a read-only delegation contract with scoped prompt, input context,
  allowed tools, forbidden actions, expected output schema, budget hints, and
  a JSON artifact. Delegation records do not start subagents, call model
  providers, approve work, commit, write files, or mutate external state.
- Executable delegation runner: `profile-adapter` stores local shell adapter
  metadata on a profile, and `run-delegation <delegation_id>` executes a
  pending read-only delegation through that configured adapter. The runner
  writes a prompt/context bundle, generates or reuses a deterministic
  context pack for registered-project parents, invokes the shell command,
  captures stdout/stderr/exit code, parses JSON output, validates the
  delegation schema, records the result, writes
  `.clanker/delegations/<delegation_id>/runs/<run_id>/evidence/`, optionally
  proposes memory, and opens incidents for adapter or output failures. For
  registered-project tasks, the input bundle includes project metadata and a
  capped git file inventory plus compact `context_pack` metadata, and the
  evidence packet includes `project.json`, `repo_files.json`,
  `context_pack.json`, `context_pack.md`, and `context_pack_metadata.json`.
  Context packs rank files with explainable scores, record capped grep hits
  and snippets, list test/entrypoint/config hints, skip ignored and
  secret-like paths, and add validation metadata showing whether returned files
  were in the inventory. Successful delegation runs also write
  `implementation_handoff.json` and `implementation_handoff.md` with compact
  context-pack paths, ranked/test hint summaries, scout returned files,
  validation health, and non-claims without embedding large snippets. The
  `implementation-handoff <delegation_id>` command reads the artifact back with
  readability, schema/kind, validation, scout file, and snippet-embedding
  status; run review and dashboard output include first-class implementation
  handoff sections. The `coder-prep <delegation_id>` command consumes the
  readable `implementation_handoff.md` and writes
  `.clanker/delegations/<delegation_id>/runs/<run_id>/coder_prep/` JSON and
  Markdown packets with allowed files, candidate tests, acceptance criteria,
  risks, and an operator-review-required future run plan. It is idempotent for
  the same handoff hash and creates no task rows, runs, routing decisions,
  worktrees, effects, approvals, source edits, command reruns, network actions,
  provider calls, or external mutations. `coder-prep-from-handoff
  <path/to/implementation_handoff.md>` is the artifact-first equivalent: it
  rejects absolute paths and parent traversal, reads the sibling
  `implementation_handoff.json`, verifies the current delegation handoff, and
  writes the same bounded prep packet with the same zero-effect counters. The
  `coder-worktree-plan <delegation_id>` command consumes the readable
  `coder_prep.md` and writes sibling `coder_worktree_plan.json` and Markdown
  packets with the source prep hash, bounded files, proposed branch/path,
  future explicit worktree-run shape, and an operator-approval-required gate.
  It is idempotent for the same prep Markdown hash and creates no task rows,
  runs, routing decisions, worktrees, effects, approvals, source edits,
  command reruns, network actions, provider calls, or external mutations. Run
  review and dashboard output also surface existing coder prep packets and
  coder worktree plans. `coder-worktree-approval <delegation_id>` creates a
  dedicated local approval request for the current plan hash and writes
  `coder_worktree_approval_request.json/.md` beside the plan without creating
  a worktree, editing source, running commands, committing, pushing,
  deploying, calling providers, or using the network.
  `approve-coder-worktree <approval_id>` marks that request approved and
  writes `coder_worktree_approval_decision.json/.md` without running the work.
  `run-coder-worktree <delegation_id> --command "<safe local command>" --verify`
  requires the approved matching plan hash, creates an isolated local git
  worktree under `.agent/worktrees/<project>/<run_id>/`, runs the explicit
  safe command inside it, optionally runs the default or operator-supplied
  verifier, captures stdout/stderr/status/diff/changed files, validates that
  changed files are a subset of `allowed_files`, and writes evidence under
  `.clanker/delegations/<delegation_id>/runs/<run_id>/coder_worktree/`.
  The run blocks on bounded-file violations, fails on command or verification
  failure, does not auto-revert, and never commits, pushes, deploys, calls
  providers, or intentionally uses the network. A reviewed completed run can
  then enter `coder-commit-request <coder_worktree_run_id>`, which refuses
  unreviewed, failed, stale, unsafe, or outside-file evidence and writes a
  dedicated `coder_commit/coder_commit_request.json/.md` request without
  staging or committing. `approve-coder-commit` records the operator decision
  in `coder_commit/coder_commit_decision.json/.md` without staging or
  committing. `commit-coder-worktree` re-checks source hashes, branch/HEAD,
  changed files, outside files, commit message, and verifier state before
  staging only reviewed allowed files and creating one local git commit in the
  isolated worktree branch. It records `coder_commit/commit.json`,
  `pre_commit_status.txt`, `post_commit_status.txt`, `committed_diff.patch`,
  `committed_files.json`, and a committed local effect that can feed
  `github-handoff <effect_id>`. It never pushes, creates a PR, deploys, calls
  providers, or mutates external systems. A committed coder worktree run can
  then enter `coder-publication-request <coder_worktree_run_id>`, which
  validates the local commit artifact, commit SHA, safe worktree, safe remote
  and target branch names, committed-file bounds, zero push/PR/deploy
  counters, and a non-empty operator note before writing
  `coder_publication/publication_request.json/.md`.
  `approve-coder-publication` writes the local decision without pushing or
  creating a PR. `coder-publication-handoff` requires the approved request,
  revalidates the request artifact hash and commit artifact hash, and writes
  `publication_handoff.json`, `publication_handoff.md`, and `pr_body.md` with
  suggested push and draft-PR commands only. It does not execute those commands,
  run `git fetch`, contact GitHub, deploy, call providers, use the network, or
  mutate external systems. Run review, delegation-result, inbox, dashboard, and
  local app run-detail output surface coder commit requests, approvals, local
  commits, publication requests, publication handoffs, and copy-only manual
  publication commands.
  Adapters run from the system root by default and can opt into
  `--working-directory project_root` for repo scouting. It supports shell
  adapters only. ClankerOS records
  `provider_calls_taken_by_clankeros=0`, `external_mutations_taken=0`, and
  `network_actions_taken=unknown` unless adapter evidence proves otherwise.
- Delegation result ingestion: `record-delegation-result` attaches structured
  operator-supplied output to an existing delegation, validates the expected
  schema family, marks the delegation completed, and writes a local result
  artifact while preserving no-provider, no-network, and no-external-mutation
  non-claims.
- Memory proposal lifecycle: `memory propose` and
  `memory propose-from-delegation` create `memory_entries` rows with
  `status=proposed` plus local JSON evidence. `memory approve` promotes a
  proposed entry to `active`, and `memory archive` marks an entry archived.
  Delegation-sourced memory proposals require a completed delegation result and
  never silently write active memory.
- Skill proposal lifecycle: `skill propose` creates a proposed skill row,
  a first `skill_versions` row, and `.clanker/skills/<name>/SKILL.md` from
  verified run evidence. `skills` lists proposals, `skill show` reads back the
  markdown, `skill approve` promotes a proposed skill to `active`, and
  `skill archive` records a local archive decision. Proposed skills are not
  active until approved.
- Run evidence review: `review <run_id>` writes a human-first
  `runs/<run_id>/review.md`, `evidence <run_id>` writes
  `runs/<run_id>/evidence-index.md` and a replayable packet under
  `.clanker/projects/<project>/goals/<goal_id>/runs/<run_id>/evidence/`, and
  `replay-summary <run_id>` writes `runs/<run_id>/replay-summary.md`. The
  packet includes goal, plan, contract, tasks, routing decisions, delegations,
  steering reviews, commands, approvals, effects, memory/skill proposals,
  incidents, eval candidates, and verification summary files. If `run-task`
  already wrote executable command proof such as `verification.json`,
  `commands.jsonl`, `tasks.json`, or `summary.md`, `evidence` preserves those
  files and writes aggregate operator sidecars instead. The reports summarize
  existing local run rows without rerunning commands, approving effects,
  committing, pushing, deploying, or mutating external systems.
- Steering review: `steer <goal_id>` writes a deterministic
  `docs/steering-review.md` plus a `steering_reviews` row from local goal,
  task, approval, and incident state. `next-action <goal_or_project>` refreshes
  the review and prints the recommended operator action. `inbox` lists
  operator-worthy steering reviews, pending approvals, open incidents, recent
  delegation states, pending coder worktree approvals, and recent coder
  worktree runs.
  These commands do not execute tasks, approve requests, retry, commit, push,
  deploy, or mutate external systems.
- Operator cockpit: the dashboard starts by making the implementation-handoff
  workflow explicit: `delegate -> context-pack -> run-delegation ->
  implementation-handoff -> coder-prep -> coder-worktree-plan ->
  coder-worktree-approval -> approve-coder-worktree -> run-coder-worktree ->
  review -> coder-commit-request -> approve-coder-commit ->
  commit-coder-worktree -> coder-publication-request ->
  approve-coder-publication -> coder-publication-handoff -> review ->
  dashboard -> inbox`, then surfaces current
  handoffs, coder-prep packets, coder worktree plans, coder worktree approvals,
  approved coder worktree runs, coder commit requests, local coder commits,
  coder publication requests, and coder publication handoffs before the broader
  goal, task, approval, effect,
  verification, routing, steering, memory, and skill sections. Legacy
  capability proof-ladder records remain available in lower advanced sections,
  but they are not the default operator path.
- Operator approval effect proposals: approved local
  `operator_approval_requests` rows can be converted into idempotent
  `proposed` effect records for external-decision and capability surfaces
  while taking zero activation actions and creating zero legacy
  `approval_requests` rows.
- Operator approval effect application: proposed operator approval effects can
  be applied as local records with per-effect `status=applied` and explicit
  `capability_enabled=false` result evidence while still taking zero
  activation actions and mutating no external systems.
- Capability activation tasks: applied capability proposal effects can be
  materialized into pending high-risk `capability_activation_task` rows, one
  per capability, with evidence and verification gates that keep
  `activation_actions_taken=0` and `capability_enabled=false` until a later
  explicit capability-specific approval path exists.
- Capability activation contracts: pending activation-gate tasks can be
  converted into durable per-capability evidence and approval contracts with
  required artifacts, required commands, `explicit_operator_approval_required`,
  and `blocked_until_evidence_verified` while keeping
  `approval_requests_created=0`, `activation_actions_taken=0`, and
  `activation_allowed=false`.
- Capability activation evidence and decisions: operators can attach local
  evidence rows and JSON artifacts to activation contracts, then record local
  approve/defer/more-evidence decisions. The safe current decision path records
  `request_more_evidence` for blocked proofs while keeping
  `approval_requests_created=0`, `activation_actions_taken=0`, and
  `activation_allowed=false`.
- Capability activation follow-ups: more-evidence activation decisions can be
  materialized into pending high-risk `capability_activation_followup_task`
  rows that point back to the source contract and decision. This turns blocked
  proof decisions into task graph work while still creating no approval rows
  and taking no activation actions.
- Capability activation follow-up delegations: pending follow-up evidence tasks
  can be routed to `evidence_review` and materialized as read-only evaluator
  delegation packets with local JSON artifacts. The packets preserve source
  task evidence and required proof commands while keeping subagent execution,
  model-provider calls, approval rows, and activation actions at zero.
- Capability activation follow-up results: completed read-only evaluator
  delegation results can be ingested into local result records and JSON
  artifacts. The records preserve evaluator findings for operator review while
  keeping proof satisfaction, approval rows, activation actions, and capability
  enablement blocked.
- Capability activation follow-up result decisions: operators can record local
  accept-keep-blocked, request-more-evidence, or defer decisions for ingested
  follow-up result records. The decisions preserve blocked proof state and keep
  approval row creation, activation actions, contract mutation, and capability
  enablement at zero.
- Capability activation follow-up result effect proposals: accepted
  keep-blocked follow-up result decisions can be converted into idempotent
  `proposed` effect rows in the generic effects ledger. Each row links the
  source decision, result, delegation, follow-up task, contract, and capability
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result effect application: proposed
  accepted-blocked follow-up decision effects can be applied as local ledger
  records only. Application rows and applied effects preserve source decision,
  result, delegation, follow-up task, contract, and capability links while
  keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result tasks: applied accepted-blocked
  follow-up result effects can be materialized into pending downstream
  `capability_activation_followup_result_task` rows. Each task preserves
  source effect, application, result, delegation, follow-up task, contract,
  and capability links while keeping approval rows, external mutations,
  activation actions, activation allowance, and capability enablement at zero.
- Capability activation follow-up result task delegations: pending downstream
  follow-up result tasks can be routed to read-only evaluator delegation
  packets. Each packet preserves the next evidence-plan context while keeping
  subagent execution, model-provider calls, approval rows, external mutations,
  activation actions, activation allowance, and capability enablement at zero.
- Capability activation follow-up result task results: completed downstream
  proof-plan delegation packets can be ingested as local result records and
  JSON artifacts. Each result preserves the source effect, result, delegation,
  downstream task, contract, and capability links while keeping approval rows,
  external mutations, activation actions, activation allowance, capability
  enablement, and proof satisfaction at zero.
- Capability activation follow-up result task result effect proposals:
  accepted blocked downstream result decisions can be converted into
  idempotent `proposed` effect rows in the generic effects ledger. Each row
  links the source downstream decision, downstream result record, upstream
  follow-up result, source effect, downstream task, contract, and capability
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect application:
  proposed accepted-blocked downstream result decision effects can be applied
  as local ledger records only. Application rows and applied effects preserve
  source downstream decision, downstream result, upstream follow-up result,
  source effect, downstream task, contract, project, and capability links
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect tasks: applied
  downstream result decision effects can be materialized into pending
  downstream proof tasks. Each task preserves the source application,
  downstream decision, downstream result, upstream follow-up result, source
  effect, downstream task, contract, project, and capability links while
  keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task delegations:
  pending downstream result effect tasks can be routed to read-only evaluator
  delegation packets with local JSON artifacts. Each packet preserves the next
  evidence-plan context while keeping subagent execution, model-provider
  calls, approval rows, external mutations, activation actions, activation
  allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task results:
  completed downstream result effect delegation packets can be ingested as
  local result records and JSON artifacts. Each result preserves the source
  application, downstream decision, downstream result, upstream follow-up
  result, source effect, downstream task, contract, project, and capability
  links while keeping approval rows, external mutations, activation actions,
  activation allowance, capability enablement, and proof satisfaction at zero.
- Capability activation follow-up result task result effect task result
  decisions: operators can record local accept-keep-blocked,
  request-more-evidence, or defer decisions for downstream result effect task
  result records. Each decision preserves the blocked proof state while
  keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  proposals: accepted blocked downstream result effect task result decisions
  can be converted into idempotent `proposed` effect rows in the generic
  effects ledger. Each row links the source decision, result record,
  application, effect, delegation, task, contract, project, and capability
  while keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  application: proposed accepted-blocked downstream result effect task result
  decision effects can be applied as local ledger records only. Application
  rows and applied effects preserve source decision, result record,
  application, effect, delegation, task, contract, project, and capability
  links while keeping approval row creation, external mutations, activation
  actions, activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  tasks: applied accepted-blocked downstream result effect task result decision
  effects can be materialized into pending downstream proof tasks. Each task
  preserves source decision, result record, application, effect, delegation,
  task, contract, project, and capability links while keeping approval row
  creation, external mutations, activation actions, activation allowance, and
  capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task delegations: pending downstream result effect task result effect tasks
  can be routed to read-only evaluator delegation packets with local JSON
  artifacts. Each packet preserves the next evidence-plan context while
  keeping subagent execution, model-provider calls, approval rows, external
  mutations, activation actions, activation allowance, and capability
  enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task results: completed downstream result effect task result effect
  delegation packets can be ingested as local result records and JSON
  artifacts. Each result preserves source decision, result, application,
  effect, delegation, task, contract, project, and capability links while
  keeping approval rows, external mutations, activation actions, activation
  allowance, capability enablement, and proof satisfaction at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect task results: completed downstream result effect task
  result effect task result effect delegation packets can be ingested as local
  result records and JSON artifacts. Each result preserves source decision,
  result, application, effect, delegation, task, contract, project, and
  capability links while keeping approval rows, external mutations, activation
  actions, activation allowance, capability enablement, and proof satisfaction
  at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect task result decisions: operators can record
  accept-keep-blocked, request-more-evidence, or defer decisions for
  downstream result effect task result effect task result effect task result
  records while keeping approval rows, external mutations, activation actions,
  activation allowance, capability enablement, and proof satisfaction at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect proposals:
  accepted blocked downstream result effect task result effect task result
  effect task result effect task result decisions can be converted into
  idempotent `proposed` effect rows in the generic effects ledger. Each row
  links the source decision, result, application, effect, delegation, task,
  contract, project, and capability while keeping approval row creation,
  external mutations, activation actions, activation allowance, and capability
  enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect proposals: accepted blocked downstream
  result effect task result effect task result effect task result decisions
  can be converted into idempotent `proposed` effect rows in the generic
  effects ledger. Each row links the source decision, result, application,
  effect, delegation, task, contract, project, and capability while keeping
  approval row creation, external mutations, activation actions, activation
  allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect application: proposed accepted-blocked
  downstream result effect task result effect task result effect task result
  decision effects can be applied as local ledger records only. Application
  rows and applied effects preserve source decision, result, application,
  effect, delegation, task, contract, project, and capability links while
  keeping approval row creation, external mutations, activation actions,
  activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect tasks: applied downstream result
  effect task result effect task result effect task result decision effects
  can be materialized into pending downstream proof tasks. Each task preserves
  source decision, result, application, effect, delegation, task, contract,
  project, and capability links while keeping approval row creation, external
  mutations, activation actions, activation allowance, and capability
  enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task delegations: pending downstream
  proof tasks can be routed to read-only `evidence_review` evaluator delegation
  packets. The batch preserves routing and packet ids while keeping subagent
  execution, model-provider calls, approval rows, external mutations,
  activation actions, activation allowance, and capability enablement at zero.
- Capability activation follow-up result task result effect task result effect
  task result decisions: operators can record accept-keep-blocked,
  request-more-evidence, or defer decisions for downstream result effect task
  result effect result records while keeping approval rows, external
  mutations, activation actions, activation allowance, capability enablement,
  and proof satisfaction at zero.
- Capability activation follow-up result task result effect task result effect
  task result effect proposals: accepted blocked downstream result effect task
  result effect result decisions can be converted into idempotent `proposed`
  effect rows in the generic effects ledger. Each row links the source
  decision, result, application, effect, delegation, task, contract, project,
  and capability while keeping approval row creation, external mutations,
  activation actions, activation allowance, and capability enablement at zero.
- Verifier: each completed task is checked by a separate deterministic verifier.
- Incidents: failed verification opens a first-class incident record with JSON
  evidence under the run directory; operator resolution writes a companion JSON
  evidence file and records who resolved it, when, and why.
- Stuck detection: explicit local sweeps block stale active tasks and open
  `task_stuck` incidents without killing, retrying, or requeueing work.
- Queue health: repeated blocked or failed task groups are reported by project
  and task type without automatic retry or replay.
- Handoff review: blocked tasks and stale project handoffs are reported against
  the latest iteration packet before any automatic repair exists.
- Eval after change: named harness behavior changes can be linked to a local
  eval-suite run with explicit changed paths and run/result evidence.
- Eval candidates: verifier or workflow gaps write proposed eval cases with
  JSON and SQLite evidence before executable evals exist.
- Playbooks: repeated successful eval runs can be promoted into reusable
  markdown playbooks with an indexed SQLite row.
- Learning distillation: repeated run learnings can be grouped after volatile
  run-id normalization and promoted into root `knowledge.md` with report and
  SQLite evidence.
- Budget/trust posture: local task risk metadata can be reported with
  budget/trust state labels before any enforcement, trust promotion, or routing
  change exists.
- Dispatch posture history: recent report-only posture snapshots can be
  summarized for local metadata trends before any policy or routing behavior
  exists.
- Dispatch posture snapshot review: recent posture snapshot timestamps can be
  checked for freshness before any scheduled refresh, policy, or routing
  behavior exists.
- Dispatch posture refresh recommendation: persisted staleness reviews can be
  translated into manual operator command recommendations before any scheduler
  or automatic refresh behavior exists.
- Capability expansion ledger: deferred autonomy surfaces can be recorded with
  required evidence, next proof, approval boundary, and no routing effect before
  any surface is enabled.
- Capability readiness review: the latest expansion ledger can be checked for
  attached evidence and readiness gaps before any activation, routing, or
  follow-up automation exists.
- Capability proof gap index: the latest readiness review can be converted into
  an explicit proof-gap list before any proof generation, promotion, routing,
  or scheduler behavior exists.
- Capability approval boundary matrix: the latest proof-gap index can be
  converted into explicit operator approval-boundary rows before any approval,
  proof generation, promotion, routing, or scheduler behavior exists.
- Capability evidence collection plan: the latest approval-boundary matrix can
  be converted into manual proof-evidence collection items before any evidence
  capture, approval, promotion, routing, or scheduler behavior exists.
- Capability promotion gate checklist: the latest evidence collection plan can
  be converted into blocked or ready promotion gates before any evidence
  capture, approval, trust promotion, routing, or scheduler behavior exists.
- Capability promotion decision ledger: the latest promotion gate checklist can
  be converted into defer/manual-review decision rows before any approval,
  trust promotion, routing, or scheduler behavior exists.
- Capability trust promotion audit: the latest promotion decision ledger can be
  audited for trust-promotion readiness before any trust promotion, routing, or
  scheduler behavior exists.
- Capability automatic retry audit: the latest trust promotion audit can be
  audited for automatic-retry readiness before any retry, replay, routing, or
  scheduler behavior exists.
- Capability real cost tracking audit: the latest automatic retry audit can be
  audited for real-cost-tracking readiness before any spend tracking, budget
  enforcement, routing, or scheduler behavior exists.
- Hosted dashboard proof checklist: the latest Real-Cost-sourced Real Cost
  Tracking proof checklist can be checked for hosted-dashboard proof readiness
  before any hosted dashboard, deployment, routing, or scheduler behavior
  exists when one exists, with legacy real-cost-tracking audit fallback when no
  proof checklist exists. The upstream proof chain is preserved in the Hosted
  Dashboard proof item and the generated report retains the Real Cost Tracking
  source proof's own source metadata when available.
- Remote worker proof checklist: the latest Real-Cost-sourced hosted dashboard
  proof checklist can be checked for remote-worker proof readiness before any
  remote worker, remote claim, routing, or scheduler behavior exists when one
  exists. Newer legacy hosted-dashboard rows and dangling hosted-dashboard rows
  without retrievable Real Cost Tracking and Automatic Retry proof sources do
  not hide the stronger proof chain. The upstream proof chain is preserved in
  the remote-worker proof item and the generated report retains the
  hosted-dashboard source proof's own source metadata when available.
- Autonomous scheduling proof checklist: the latest Real-Cost-sourced remote
  worker proof checklist can be checked for autonomous-scheduling proof
  readiness before any scheduler, remote worker, routing, or claim behavior
  exists. Newer legacy remote-worker rows and dangling remote-worker rows
  without retrievable Hosted Dashboard, Real Cost Tracking, and Automatic
  Retry proof sources do not hide the stronger proof chain. The upstream proof
  chain is preserved in the autonomous-scheduling proof item and the generated
  report retains the remote-worker source proof's own source metadata when
  available.
- Browser desktop adapter proof checklist: the latest Real-Cost-sourced
  autonomous scheduling proof checklist can be checked for browser/desktop
  adapter proof readiness before any adapter operation, scheduler, routing, or
  claim behavior exists. Newer legacy autonomous-scheduling rows and dangling
  autonomous-scheduling rows without retrievable Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources do not hide
  the stronger proof chain. The upstream proof chain is preserved in the
  browser/desktop adapter proof item and the generated report retains the
  autonomous-scheduling source proof's own source metadata when available.
- CI Deploy proof checklist: the latest Real-Cost-sourced browser desktop
  adapter proof checklist can be checked for CI/deploy proof readiness before
  any CI run, deployment, adapter operation, routing, or claim behavior exists
  when one exists. Newer legacy browser/desktop adapter rows and dangling
  browser/desktop adapter rows without retrievable Autonomous Scheduling,
  Remote Worker, Hosted Dashboard, Real Cost Tracking, and Automatic Retry
  proof sources do not hide the stronger proof chain. The upstream proof chain
  is preserved in the CI Deploy proof item and the generated report retains
  the browser/desktop adapter source proof's own source metadata when
  available.
- Budget Enforcement proof checklist: the latest Real-Cost-sourced CI Deploy
  proof checklist can be checked for budget-enforcement proof readiness before
  any budget enforcement, CI/deploy run, routing, or claim behavior exists
  when one exists. Newer legacy CI Deploy rows and dangling CI Deploy rows
  without retrievable Browser/Desktop Adapter, Autonomous Scheduling, Remote
  Worker, Hosted Dashboard, Real Cost Tracking, and Automatic Retry proof
  sources do not hide the stronger proof chain. The upstream proof chain is
  preserved in the Budget Enforcement proof item and the generated report
  retains the CI Deploy source proof's own source metadata when available.
- Trust Promotion proof checklist: the latest Real-Cost-sourced Budget
  Enforcement proof checklist can be checked for trust-promotion proof
  readiness before any trust promotion, budget enforcement, routing, or claim
  behavior exists when one exists. Newer legacy Budget Enforcement rows and
  dangling Budget Enforcement rows without retrievable CI Deploy,
  Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources do not hide
  the stronger proof chain. The upstream proof chain is preserved in the Trust
  Promotion proof item and the generated report retains the Budget Enforcement
  source proof's own source metadata when available.
- Automatic Retry proof checklist: the latest Real-Cost-sourced Trust Promotion
  proof checklist can be checked for automatic-retry proof readiness before any
  retry, replay, trust promotion, budget enforcement, routing, or claim
  behavior exists when one exists. Newer legacy Trust Promotion rows and
  dangling Trust Promotion rows without retrievable Budget Enforcement, CI
  Deploy, Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources do not hide
  the stronger proof chain. The upstream proof chain is preserved in the
  Automatic Retry proof item and the generated report retains the Trust
  Promotion source proof's own source metadata when available.
- Real Cost Tracking proof checklist: the latest Real-Cost-sourced Automatic
  Retry proof checklist can be checked for real-cost-tracking proof readiness
  before any spend tracking, retry, budget enforcement, routing, or claim
  behavior exists when one exists. The upstream proof chain is preserved in the
  Real Cost Tracking proof item and the generated report retains the Automatic
  Retry source proof's own source metadata when available.
- Goal completion audit: the latest expansion proof checklists can be audited
  against the active expansion goal before any goal-complete claim exists. The
  audit reports satisfied, blocked, and missing requirements plus external
  decisions and explicit non-claims, and it does not mark the active goal
  complete or approve any capability.
- Expansion decision brief: the latest goal completion audit can be converted
  into a report-only operator decision packet before any capability approval,
  promotion, routing, or external side effect exists.
- Expansion decision evidence index: the latest expansion decision brief can
  be cross-referenced to blocked queue entries and proof report paths before
  any decision is approved or evidence is collected automatically.
- Expansion operator review checklist: the latest decision evidence index can
  be converted into manual operator choices with allowed actions before any
  approval, promotion, routing, or external side effect exists.
- Expansion operator decision ledger: the latest operator review checklist can
  be converted into pending/manual decision rows before any approval action,
  promotion, routing, or external side effect exists.
- Expansion operator approval draft: the latest operator decision ledger can
  be converted into draft-only approval-request packet rows before any
  `approval_requests` rows are created, allowed action is taken, promotion,
  routing, or external side effect exists.
- Expansion operator approval request review: the latest approval draft can be
  reviewed against the existing `approval_requests` contract before any real
  approval row is created; current capability decisions are blocked by
  `approval_request_subject_not_modeled` until the approval schema is extended
  or a separate subject table is chosen.
- Expansion operator approval schema decision: the latest approval request
  review can be converted into a report-only schema decision packet that
  recommends `operator_approval_requests_table` while preserving the existing
  task approval gate, applying no migration, creating no approval rows, and
  taking no operator action.
- Expansion operator approval schema migration plan: the latest schema
  decision can be converted into a report-only migration plan for a future
  `operator_approval_requests` table. The plan records proposed columns,
  indexes, and migration steps while applying no migration, creating no table,
  creating no operator approval rows, and creating no approval requests.
- Expansion operator approval schema migration approval request: the latest
  migration plan can be converted into a report-only approval request packet
  for applying the future `operator_approval_requests` table. The packet
  records the requested action and allowed operator actions while applying no
  migration, creating no table, creating no operator approval rows, and
  creating no approval requests.
- Expansion operator approval schema migration decision ledger: the latest
  schema migration approval request can be converted into a report-only
  pending/manual decision ledger. The ledger records the source request,
  requested action, allowed operator actions, pending decision count, and
  zero mutation counters while applying no migration, creating no table,
  creating no operator approval rows, creating no approval requests, and
  taking no operator action.
- Expansion operator approval schema migration action checklist: the latest
  schema migration decision ledger can be converted into a report-only manual
  action checklist. The checklist records allowed operator actions,
  `selected_action=none`, pending action counts, and zero mutation counters
  while applying no migration, creating no table, creating no operator
  approval rows, creating no approval requests, and taking no operator action.
- Expansion operator approval schema migration selection packet: the latest
  schema migration action checklist can be converted into a report-only
  operator selection input packet. The packet records
  `selected_action=none`, `selections_recorded: 0`, pending selection counts,
  allowed operator actions, and zero mutation counters while applying no
  migration, creating no table, creating no approval rows, and recording no
  operator selection.
- Expansion operator approval schema migration selection input template: the
  latest selection packet can be converted into a report-only operator input
  template. The template records required input fields and
  `inputs_recorded: 0` while keeping `selected_action=none`,
  `selections_recorded: 0`, `actions_taken: 0`, and zero mutation counters.
- Operator approval request row application: after the schema migration
  application has created the local `operator_approval_requests` table, an
  explicit approved row-creation selection can create pending local operator
  approval request rows from the latest expansion approval draft. It creates
  no legacy `approval_requests` rows, decides no requests, promotes nothing,
  and takes no external action.
- Operator approval request decisions: after pending local
  `operator_approval_requests` rows exist, an explicit operator decision
  selection can mark those rows `approved`, `deferred`, or
  `more_evidence_requested`. The command records durable decision evidence
  while creating no legacy `approval_requests` rows, enabling no capability,
  promoting no trust, and taking no external action.
- Iteration loop: `iterate` selects the next actionable queue item and writes a
  non-executing `docs/next-iteration.md` packet with verification commands.
- Simplicity guardrail: when queue items have equal score metadata, `iterate`
  selects the lower-complexity item before queue order.
- Memory: project files preserve hot/warm memory and run files preserve episodic
  evidence.
- Learning: each run records an episodic learning; repeated stable patterns can
  be promoted into root knowledge through `distill-learnings`.
- Visibility: `docs/dashboard.md` summarizes queue health, handoff reviews,
  eval-after-change checks, learning distillation, budget/trust posture,
  dispatch posture history, dispatch posture snapshot reviews, dispatch
  posture refresh recommendations, capability expansion ledgers, capability
  readiness reviews, capability proof gap indexes, capability approval-boundary
  matrices, capability evidence collection plans, capability promotion gate
  checklists, capability promotion decision ledgers, capability trust
  promotion audits, capability automatic retry audits, capability real cost
  tracking audits, hosted dashboard proof checklists, remote worker proof
  checklists, autonomous scheduling proof checklists, browser desktop adapter
  proof checklists, CI Deploy proof checklists, budget enforcement proof
  checklists, trust promotion proof checklists, automatic retry proof
  checklists, real cost tracking proof checklists, goal completion audits,
  expansion decision briefs, expansion decision evidence indexes, expansion
  operator review checklists, expansion operator decision ledgers, expansion
  operator approval drafts, expansion operator approval request reviews,
  expansion operator approval schema decisions, expansion operator approval
  schema migration plans, expansion operator approval schema migration
  approval requests, expansion operator approval schema migration decision
  ledgers, expansion operator approval schema migration action checklists,
  expansion operator approval schema migration selection packets, expansion
  operator approval schema migration selection input templates, operator
  approval schema migration applications, operator approval request row
  applications, operator approval request decisions, capability activation
  follow-up result batches, follow-up result decisions, follow-up result
  downstream task batches, playbooks, eval candidates, iteration packets,
  simplicity guardrails, approvals, proposed
  effects, worktrees, verification status, stuck tasks, incidents, recent
  runs, learnings, and eval results.

## First Milestone

Prove one full local loop:

1. Accept a goal.
2. Decompose it into an explicit task graph.
3. Route a task to a worker.
4. Execute work in the repository.
5. Verify the result with saved evidence.
6. Record memory and activity visible to a human.
7. Learn one thing from the run.

Status: implemented and locally verified by automated tests and CLI smoke runs.

## Key Guardrails

- Start with one strong local worker and explicit workflows.
- Prefer file-first state, typed schemas, and deterministic verification.
- Keep research mode and action mode distinct.
- Do not use hidden memory as the source of truth.
- Do not promote autonomy without outcome evidence.
- Keep external side effects out of scope until approvals, idempotency, and
  rollback are implemented.

## Current Runtime Constraints

- Runtime: Codex desktop coding agent in a local git repository.
- Shell and filesystem: available.
- File editing: available through patch-based edits.
- Git: available. ClankerOS itself is connected to a GitHub remote, and
  registered target repositories can be isolated with git worktrees.
- Network: available, but not required for the first milestone.
- Browser and desktop control: available to the agent runtime, deferred from the
  first executable milestone.
- Persistent local storage: SQLite and repo files are available.
- Static dashboard: available through `python3 -m agent_os.cli dashboard`.
- Next iteration packet: available through `python3 -m agent_os.cli iterate`.
  Queue items may include `<!-- score=N complexity=N -->`; equal scores prefer
  lower complexity.
- Local approval review: available through `python3 -m agent_os.cli approvals`
  and `python3 -m agent_os.cli approve <approval_id>`.
- Local project registration: available through
  `python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "<command>"`.
- Worktree-isolated coding run: available through
  `python3 -m agent_os.cli run-goal "<goal>" --project <name> --isolation worktree --command "<safe local command>"`.
  The current flow records a proposed `local_git_commit` effect and approval
  packet. After explicit approval, `commit-approved` re-checks the captured
  evidence and creates the local worktree commit exactly once.
- Incident resolution: available through
  `python3 -m agent_os.cli resolve-incident <incident_id> --resolved-by operator --note "..."`.
- Stuck-task sweep: available through
  `python3 -m agent_os.cli sweep-stuck --timeout-seconds 1800`.
- Queue-health report: available through `python3 -m agent_os.cli queue-health`
  and mirrored into `docs/dashboard.md`.
- Handoff review: available through
  `python3 -m agent_os.cli handoff-review` and mirrored into
  `docs/handoff-review.md` plus `docs/dashboard.md`.
- Eval-after-change check: available through
  `python3 -m agent_os.cli eval-after-change --change "<summary>" --file <path>`
  and mirrored into `docs/eval-after-change.md` plus `docs/dashboard.md`.
- Learning distillation: available through
  `python3 -m agent_os.cli distill-learnings --min-occurrences 3` and mirrored
  into `docs/learning-distillation.md`, root `knowledge.md`, SQLite state, and
  `docs/dashboard.md`.
- Budget/trust posture: available through
  `python3 -m agent_os.cli budget-trust-posture` and mirrored into
  `docs/budget-trust-posture.md`, SQLite state, and `docs/dashboard.md`.
- Dispatch posture history: available through
  `python3 -m agent_os.cli dispatch-posture-history` and mirrored into
  `docs/dispatch-posture-history.md`, SQLite state, and `docs/dashboard.md`.
- Dispatch posture snapshot review: available through
  `python3 -m agent_os.cli dispatch-posture-staleness` and mirrored into
  `docs/dispatch-posture-staleness.md`, SQLite state, and
  `docs/dashboard.md`.
- Dispatch posture refresh recommendation: available through
  `python3 -m agent_os.cli dispatch-posture-refresh` and mirrored into
  `docs/dispatch-posture-refresh.md`, SQLite state, and `docs/dashboard.md`.
- Capability expansion ledger: available through
  `python3 -m agent_os.cli capability-expansion-ledger` and mirrored into
  `docs/capability-expansion-ledger.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability readiness review: available through
  `python3 -m agent_os.cli capability-readiness-review` and mirrored into
  `docs/capability-readiness-review.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability proof gap index: available through
  `python3 -m agent_os.cli capability-proof-gap-index` and mirrored into
  `docs/capability-proof-gap-index.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability approval boundary matrix: available through
  `python3 -m agent_os.cli capability-approval-boundary-matrix` and mirrored
  into `docs/capability-approval-boundary-matrix.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability evidence collection plan: available through
  `python3 -m agent_os.cli capability-evidence-collection-plan` and mirrored
  into `docs/capability-evidence-collection-plan.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability promotion gate checklist: available through
  `python3 -m agent_os.cli capability-promotion-gate-checklist` and mirrored
  into `docs/capability-promotion-gate-checklist.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability promotion decision ledger: available through
  `python3 -m agent_os.cli capability-promotion-decision-ledger` and mirrored
  into `docs/capability-promotion-decision-ledger.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability trust promotion audit: available through
  `python3 -m agent_os.cli capability-trust-promotion-audit` and mirrored into
  `docs/capability-trust-promotion-audit.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability automatic retry audit: available through
  `python3 -m agent_os.cli capability-automatic-retry-audit` and mirrored into
  `docs/capability-automatic-retry-audit.md`, SQLite state, and
  `docs/dashboard.md`.
- Capability real cost tracking audit: available through
  `python3 -m agent_os.cli capability-real-cost-tracking-audit` and mirrored
  into `docs/capability-real-cost-tracking-audit.md`, SQLite state, and
  `docs/dashboard.md`.
- Hosted dashboard proof checklist: available through
  `python3 -m agent_os.cli hosted-dashboard-proof-checklist` and mirrored into
  `docs/hosted-dashboard-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced Real Cost Tracking
  proof checklists when one exists, avoids dangling Real Cost Tracking proof
  rows without an upstream Automatic Retry proof source, falls back to the
  latest structurally backed Real Cost Tracking proof checklist otherwise, and
  falls back to real-cost-tracking audits only when no proof checklist exists;
  it preserves source proof metadata when present.
- Remote worker proof checklist: available through
  `python3 -m agent_os.cli remote-worker-proof-checklist` and mirrored into
  `docs/remote-worker-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced hosted-dashboard
  proof checklists, avoids dangling hosted-dashboard rows without retrievable
  Real Cost Tracking and Automatic Retry proof sources, and preserves source
  proof metadata when present.
- Autonomous scheduling proof checklist: available through
  `python3 -m agent_os.cli autonomous-scheduling-proof-checklist` and mirrored
  into `docs/autonomous-scheduling-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced remote-worker proof
  checklists, avoids dangling remote-worker rows without retrievable Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources, and
  preserves source proof metadata when present.
- Browser desktop adapter proof checklist: available through
  `python3 -m agent_os.cli browser-desktop-adapter-proof-checklist` and
  mirrored into `docs/browser-desktop-adapter-proof-checklist.md`, SQLite
  state, and `docs/dashboard.md`; it prefers latest Real-Cost-sourced
  autonomous scheduling proof checklists and preserves source proof metadata
  when present.
- CI Deploy proof checklist: available through
  `python3 -m agent_os.cli ci-deploy-proof-checklist` and mirrored into
  `docs/ci-deploy-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced browser/desktop
  adapter proof checklists, avoids dangling browser/desktop adapter rows
  without retrievable Autonomous Scheduling, Remote Worker, Hosted Dashboard,
  Real Cost Tracking, and Automatic Retry proof sources, and preserves source
  proof metadata when present.
- Budget Enforcement proof checklist: available through
  `python3 -m agent_os.cli budget-enforcement-proof-checklist` and mirrored
  into `docs/budget-enforcement-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced CI Deploy proof
  checklists, avoids dangling CI Deploy rows without retrievable
  Browser/Desktop Adapter, Autonomous Scheduling, Remote Worker, Hosted
  Dashboard, Real Cost Tracking, and Automatic Retry proof sources, and
  preserves source proof metadata when present.
- Trust Promotion proof checklist: available through
  `python3 -m agent_os.cli trust-promotion-proof-checklist` and mirrored into
  `docs/trust-promotion-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced Budget Enforcement
  proof checklists, avoids dangling Budget Enforcement rows without
  retrievable CI Deploy, Browser/Desktop Adapter, Autonomous Scheduling,
  Remote Worker, Hosted Dashboard, Real Cost Tracking, and Automatic Retry
  proof sources, and preserves source proof metadata when present.
- Automatic Retry proof checklist: available through
  `python3 -m agent_os.cli automatic-retry-proof-checklist` and mirrored into
  `docs/automatic-retry-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it prefers latest Real-Cost-sourced Trust Promotion
  proof checklists, avoids dangling Trust Promotion rows without retrievable
  Budget Enforcement, CI Deploy, Browser/Desktop Adapter, Autonomous
  Scheduling, Remote Worker, Hosted Dashboard, Real Cost Tracking, and
  Automatic Retry proof sources, and preserves source proof metadata when
  present.
- Real Cost Tracking proof checklist: available through
  `python3 -m agent_os.cli real-cost-tracking-proof-checklist` and mirrored
  into `docs/real-cost-tracking-proof-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it preserves Real-Cost-sourced Automatic Retry proof
  metadata when present.
- Goal completion audit: available through
  `python3 -m agent_os.cli goal-completion-audit` and mirrored into
  `docs/goal-completion-audit.md`, SQLite state, and `docs/dashboard.md`; it
  reports whether the expansion goal is still blocked by report-only proofs,
  missing proof rows, external decisions, or approvals before any completion
  claim is made.
- Expansion decision brief: available through
  `python3 -m agent_os.cli expansion-decision-brief` and mirrored into
  `docs/expansion-decision-brief.md`, SQLite state, and `docs/dashboard.md`;
  it turns the latest goal completion audit into explicit operator decisions
  without approving, routing, promoting, or mutating external systems.
- Expansion decision evidence index: available through
  `python3 -m agent_os.cli expansion-decision-evidence-index` and mirrored
  into `docs/expansion-decision-evidence-index.md`, SQLite state, and
  `docs/dashboard.md`; it links decision items to blocked queue evidence and
  proof reports without granting approval or collecting evidence
  automatically.
- Expansion operator review checklist: available through
  `python3 -m agent_os.cli expansion-operator-review-checklist` and mirrored
  into `docs/expansion-operator-review-checklist.md`, SQLite state, and
  `docs/dashboard.md`; it lists manual operator choices and allowed actions
  without granting approval, promotion, routing, or external side effects.
- Expansion operator decision ledger: available through
  `python3 -m agent_os.cli expansion-operator-decision-ledger` and mirrored
  into `docs/expansion-operator-decision-ledger.md`, SQLite state, and
  `docs/dashboard.md`; it records pending/manual operator decision posture
  without taking allowed actions, granting approval, promotion, routing, or
  external side effects.
- Expansion operator approval draft: available through
  `python3 -m agent_os.cli expansion-operator-approval-draft` and mirrored
  into `docs/expansion-operator-approval-draft.md`, SQLite state, and
  `docs/dashboard.md`; it prepares draft-only approval-request packet rows
  from the latest decision ledger while keeping `created_approval_requests: 0`
  and without taking allowed actions, granting approval, routing, or mutating
  external systems.
- Expansion operator approval request review: available through
  `python3 -m agent_os.cli expansion-operator-approval-request-review` and
  mirrored into `docs/expansion-operator-approval-request-review.md`, SQLite
  state, and `docs/dashboard.md`; it reviews draft requests against the
  existing `approval_requests` contract, records schema gaps, keeps
  `created_approval_requests: 0`, and does not create approvals, take allowed
  actions, route work, or mutate external systems.
- Expansion operator approval schema decision: available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-decision` and
  mirrored into `docs/expansion-operator-approval-schema-decision.md`, SQLite
  state, and `docs/dashboard.md`; it recommends the report-only
  `operator_approval_requests_table` schema option from the current schema gap
  while applying no migration and creating no approval rows.
- Expansion operator approval schema migration plan: available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-plan`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-plan.md`, SQLite state,
  and `docs/dashboard.md`; it turns the chosen schema option into a concrete
  report-only migration plan while applying no migration and creating no table
  or rows.
- Expansion operator approval schema migration approval request: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-approval-request`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-approval-request.md`,
  SQLite state, and `docs/dashboard.md`; it records that applying the planned
  schema requires an operator decision, while taking no action and creating no
  approval rows.
- Expansion operator approval schema migration decision ledger: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-decision-ledger`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-decision-ledger.md`,
  SQLite state, and `docs/dashboard.md`; it records the schema migration
  request as a pending/manual operator action while applying no migration and
  creating no table or approval rows.
- Expansion operator approval schema migration action checklist: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-action-checklist`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-action-checklist.md`,
  SQLite state, and `docs/dashboard.md`; it lists the allowed manual choices
  while keeping `selected_action=none` and recording no action taken.
- Expansion operator approval schema migration selection packet: available
  through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-packet`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-selection-packet.md`,
  SQLite state, and `docs/dashboard.md`; it requires explicit operator input
  while keeping `selected_action=none`, `selections_recorded: 0`, and all
  migration, table, and approval-row counters at zero.
- Expansion operator approval schema migration selection input template:
  available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-selection-input-template`
  and mirrored into
  `docs/expansion-operator-approval-schema-migration-selection-input-template.md`,
  SQLite state, and `docs/dashboard.md`; it lists required operator fields
  while keeping `inputs_recorded: 0`, `selections_recorded: 0`, and all
  migration, table, and approval-row counters at zero.
- Operator approval schema migration application: available through
  `python3 -m agent_os.cli expansion-operator-approval-schema-migration-apply`
  after the selection input template exists. Non-approve selections record a
  local application row without creating the table. An approved selection
  creates the local `operator_approval_requests` table exactly once, records
  applied columns/indexes in
  `docs/expansion-operator-approval-schema-migration-application.md`, and
  keeps `operator_approval_rows_created: 0` and
  `approval_requests_created: 0`.
- Operator approval request row application: available through
  `python3 -m agent_os.cli expansion-operator-approval-request-rows-apply`
  after the approval draft and schema application exist. Non-approve
  selections record local evidence without creating rows. An approved
  selection creates pending local `operator_approval_requests` rows exactly
  once for the latest draft, records evidence in
  `docs/expansion-operator-approval-request-rows-application.md`, and keeps
  `approval_requests_created: 0`.
- Operator approval request decisions: available through
  `python3 -m agent_os.cli expansion-operator-approval-request-decide`
  after pending operator approval request rows exist. The command records
  approve/defer/more-evidence decisions on local rows, writes evidence to
  `docs/expansion-operator-approval-request-decisions.md`, and keeps
  `approval_requests_created: 0` without enabling capabilities.
- Capability activation contracts: available through
  `python3 -m agent_os.cli capability-activation-contracts` after
  `capability-activation-tasks` has created pending activation tasks. The
  command writes `docs/capability-activation-contracts.md`, records one
  blocked contract per task, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, and `activation_allowed=false`.
- Capability activation evidence: available through
  `python3 -m agent_os.cli capability-activation-evidence` after contracts
  exist. The command writes `docs/capability-activation-evidence.md`, one JSON
  artifact per selected contract, and keeps `approval_requests_created: 0` and
  `activation_actions_taken: 0`.
- Capability activation decisions: available through
  `python3 -m agent_os.cli capability-activation-decide` after evidence exists.
  The command writes `docs/capability-activation-decisions.md`, updates
  contract decision state, and keeps capability activation blocked.
- Capability activation follow-ups: available through
  `python3 -m agent_os.cli capability-activation-followups` after contracts
  have `request_more_evidence` decisions. The command writes
  `docs/capability-activation-followups.md` and creates pending high-risk
  follow-up evidence tasks while keeping `approval_requests_created: 0` and
  `activation_actions_taken: 0`.
- Capability activation follow-up delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-delegations` after
  follow-up evidence tasks exist. The command writes
  `docs/capability-activation-followup-delegations.md`, records
  `evidence_review` routing decisions, and creates pending read-only evaluator
  delegation packets while keeping execution and activation actions at zero.
- Capability activation follow-up results: available through
  `python3 -m agent_os.cli capability-activation-followup-results` after
  read-only evaluator delegation results are completed. The command writes
  `docs/capability-activation-followup-results.md`, records local result rows
  and JSON artifacts, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-decide` after
  result records exist. The command writes
  `docs/capability-activation-followup-decisions.md`, records local operator
  review decisions, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-tasks` after
  accepted blocked follow-up result effects have been applied locally. The
  command writes `docs/capability-activation-followup-result-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-delegations`
  after downstream follow-up result tasks exist. The command writes
  `docs/capability-activation-followup-result-task-delegations.md`, creates
  read-only evaluator delegation packets and local JSON artifacts, and keeps
  `execution_started: 0`, `network_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_actions_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-results`
  after downstream proof-plan delegation packets have completed results. The
  command writes
  `docs/capability-activation-followup-result-task-results.md`, stores local
  result records and JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-decide`
  after downstream proof-plan result records exist. The command writes
  `docs/capability-activation-followup-result-task-decisions.md`, records
  accept-keep-blocked, more-evidence, or defer operator decisions for
  downstream result records, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect proposals:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-proposals`
  after accepted blocked downstream result decisions exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-proposals.md`,
  creates local `proposed` effects, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect application:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-apply`
  after downstream result decision effect proposals exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-application.md`,
  records local application rows, marks applicable effects `applied`, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect tasks: available
  through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-tasks`
  after downstream result decision effects have been applied locally. The
  command writes
  `docs/capability-activation-followup-result-task-result-effect-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task delegations:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-delegations`
  after downstream result effect tasks exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-delegations.md`,
  records read-only evaluator routing and delegation packet evidence, and
  keeps `execution_started: 0`, `network_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_actions_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect task results:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-results`
  after downstream result effect task delegations have completed. The command
  writes
  `docs/capability-activation-followup-result-task-result-effect-task-results.md`,
  stores local result records and JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result
  decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-decide`
  after downstream result effect task results exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-decisions.md`,
  stores local operator decision rows, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  proposals: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-proposals`
  after accepted downstream result effect task result decisions exist. The
  command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-proposals.md`,
  stores generic local proposed `effects` rows with idempotency keys, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  application: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-apply`
  after downstream result effect task result decision effect proposals exist.
  The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-application.md`,
  records local application rows, marks applicable effects `applied`, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-tasks`
  after downstream result effect task result decision effects have been applied
  locally. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations`
  after downstream result effect task result effect tasks exist. The command
  writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-delegations.md`,
  records read-only routing decisions and pending delegation packets, and
  keeps `execution_started: 0`, `network_actions_taken: 0`,
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-results`
  after completed downstream result effect task result effect delegation
  outputs exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-results.md`,
  stores local result rows and JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-decide`
  after downstream result effect task result effect task result records exist.
  The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-decisions.md`,
  stores local operator decision rows, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect proposals: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals`
  after accepted downstream result effect task result effect result decisions
  exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
  stores generic local proposed `effects` rows with idempotency keys, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect application: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-apply`
  after proposed downstream result effect task result effect result decision
  effects exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-application.md`,
  records local application rows, marks applicable generic `effects` rows as
  `applied`, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-tasks`
  after downstream result effect task result effect task result decision effects
  have been applied locally. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-delegations`
  after downstream result effect task result effect task result effect tasks
  exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`,
  records read-only `evidence_review` routing decisions and pending evaluator
  delegation packets, and keeps `execution_started: 0`,
  `network_actions_taken: 0`, `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results`
  after the read-only evaluator delegation packet has a completed local result.
  The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-results.md`,
  stores one JSON artifact per ingested delegation under the matching docs
  directory, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task result decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-decide`
  after downstream result effect task result effect task result effect task
  result records exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`,
  stores local operator decision rows, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect proposals: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals`
  after accepted downstream result effect task result effect task result effect
  task result decisions exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
  stores generic local proposed `effects` rows with idempotency keys, and
  keeps `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect application: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply`
  after proposed downstream result effect task result effect task result
  effect task result decision effects exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`,
  records local application rows, marks applicable generic `effects` rows as
  `applied`, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks`
  after downstream result effect task result effect task result effect task
  result decision effects have been applied locally. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`,
  creates pending downstream proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`, and
  `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations`
  after pending downstream proof tasks exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`,
  records local `evidence_review` routing decisions and pending evaluator
  delegation packets, and keeps `execution_started: 0`,
  `network_actions_taken: 0`, `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, and `capability_enabled: false`.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results`
  after completed downstream evaluator delegation outputs exist. The command
  writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`,
  records local result rows and JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, and proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result decisions: available
  through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide`
  after downstream result effect task result effect task result effect task
  result effect task result records exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`,
  records review-only operator decisions, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, and proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect proposals:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals`
  after accepted blocked downstream result effect task result effect task
  result effect task result effect task result decisions exist. The command
  writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
  creates idempotent generic `effects` rows, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, and proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect application:
  available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply`
  after proposed downstream result effect task result effect task result
  effect task result effect task result effect task result decision effects
  exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`,
  records local application rows, marks applicable generic `effects` rows as
  `applied`, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, `capability_enabled: false`, and proof
  satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect proposals: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals`
  after accepted blocked downstream result effect task result effect task
  result effect task result effect task result effect task result effect task
  result decisions exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
  creates idempotent generic `effects` rows, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, and proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect application: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply`
  after proposed downstream result effect task result effect task result
  effect task result effect task result effect task result effect task result
  effect task result decision effects exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`,
  records local application rows, marks applicable generic `effects` rows as
  `applied`, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, `capability_enabled: false`, and proof
  satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks`
  after accepted blocked downstream result effect task result effect task
  result effect task result effect task result effect task result effect task
  result effect task result decision effects have been applied locally. The
  command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`,
  creates pending high-risk proof tasks, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, routing, dispatch, and proof satisfaction
  blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations`
  after those pending proof tasks exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`,
  records local `evidence_review` routing decisions and pending evaluator
  delegation packets, and keeps `execution_started: 0`,
  `network_actions_taken: 0`, `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, `capability_enabled: false`, dispatch, and
  proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results`
  after an operator records structured output for the pending evaluator
  delegation packets. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`,
  creates local result records and per-result JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, dispatch, provider calls, subagent starts, and
  proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task result decisions: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide`
  after downstream result effect task result effect task result effect task
  result effect task result effect task result effect task result records
  exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`,
  records review-only operator decisions, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, and proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task result effect proposals: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals`
  after an accepted blocked operator decision exists for the latest downstream
  result records. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-proposals.md`,
  creates idempotent proposed rows in the generic `effects` table, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, and proof satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task result effect application: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-apply`
  after proposed rows exist for the latest accepted blocked downstream result
  decisions. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-application.md`,
  records local-only application rows, marks applicable generic `effects` rows
  as applied, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, `capability_enabled: false`, and proof
  satisfaction blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task result effect tasks: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks`
  after latest accepted blocked downstream decision-effect applications exist.
  The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks.md`,
  records pending high-risk downstream proof tasks, preserves source effect,
  application, result, delegation, downstream task, contract, project, and
  capability links, and keeps `approval_requests_created: 0`,
  `activation_actions_taken: 0`, `external_mutations_taken: 0`,
  `activation_allowed: false`, `capability_enabled: false`, routing,
  execution, proof satisfaction, and external mutation blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task result effect task delegations: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations`
  after those latest pending proof tasks exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations.md`,
  records local `evidence_review` routing decisions and pending evaluator
  delegation packets, stores packet JSON under `.clanker/delegations/`, and
  keeps `execution_started: 0`, `network_actions_taken: 0`,
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, dispatch, proof satisfaction, and external
  mutation blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task result effect task results: available through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results`
  after those evaluator delegation packets are completed with structured
  `record-delegation-result` output. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md`,
  creates local result rows plus per-result JSON artifacts, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, subagent start, provider calls, proof
  satisfaction, and external mutation blocked.
- Capability activation follow-up result task result effect task result effect
  task result effect task result effect task result effect task result effect
  task result effect task result effect task result decisions: available
  through
  `python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide`
  after the latest downstream result effect task result effect task result
  effect task result effect task result effect task result effect task result
  effect task result effect task result records exist. The command writes
  `docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-decisions.md`,
  records review-only operator decisions, and keeps
  `approval_requests_created: 0`, `activation_actions_taken: 0`,
  `external_mutations_taken: 0`, `activation_allowed: false`,
  `capability_enabled: false`, proof satisfaction, provider calls, subagent
  starts, and external mutation blocked.
- Eval candidate listing: available through
  `python3 -m agent_os.cli eval-candidates` and mirrored into
  `docs/dashboard.md`.
- Playbook promotion: available through `python3 -m agent_os.cli playbooks`
  and mirrored into `docs/playbooks.md` plus `docs/dashboard.md`.
- Background scheduling, webhooks, multi-machine dispatch, and hosted dashboard:
  deferred until the local closed loop is stable.
