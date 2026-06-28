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
  demo pages. The `/projects` index now acts as a project workflow index with
  a confirmed local `Register Local Project` form, local repo posture, default
  test command, goal/task/delegation counts, next recommended operator action,
  and selected delegation/run workflow links. Project detail pages separate
  project goals from goal-linked project tasks, include a read-only
  `Project Command Bar` that summarizes branch/commit, goal and queue counts,
  next project action, target local surface, and no-write/no-network/
  no-external-effect boundaries before the longer inventory, and now include a
  `Project Operator Workbench` with Do Now, Goal, Unblock, and Finish Today
  cards plus a confirmed `save-workspace` form for project-level resume. They
  include a confirmed local `Start Goal For This Project` form and a project
  workflow launchpad with scoped delegation/run workflow links, safe actions,
  dogfooding, and verification links so the operator can start from the
  product path rather than infer goals from task rows. Project goal rows link
  directly to
  `/goals/<goal_id>` and show phase, next action, and task progress so the
  project page can launch the same goal-centered workbench as `/goals`. The
  local app now also exposes `/today` as a daily command center for the
  current operating day, starting with a read-only `Today Command Center`
  that selects the lead Goal or first-run step, names current phase, one
  primary action, target surface or same-page action form, attention routing
  for approvals/incidents/recommendations/inbox, resume readiness, CI proof
  posture, a confirmed `save-goal-note` capture form for goal-scoped operator
  context, a confirmed `pause-goal` form for shelving the lead Goal locally,
  and a confirmed `Finish Today` workspace save form for tomorrow's resume
  point. A read-only `Today Live State` panel follows with five-second local
  page reload polling that pauses when the tab is hidden or a form field is
  focused and reports zero provider/network/external-effect counters. A
  read-only `Today Session Summary` follows with current goal or first-run
  step, current gate, next surface, latest activity, latest artifact,
  workspace resume posture, and recorded CI proof in one browser return brief.
  A read-only `Today Operator Workbench` follows with do/check/unblock/finish
  cards for the current action, timeline/evidence review, first blocker, and
  finish-today resume save target. A read-only `Today Workflow Map` follows
  with the first-run gate rail when no Goal exists, or the lead Goal's local
  lifecycle gates, current gate, next action, same-page action target, and gate
  counts once a Goal exists. A read-only `Today CI Handoff` follows with the
  latest operator-recorded GitHub Actions proof, current-checkout match status,
  exact `gh run list` / `gh run view` commands for current CI, and links to
  `/verification` plus `/ci-evidence` for recording proof after Actions
  completes without app-side GitHub polling or GET writes. A
  read-only `Today Goal Queue` follows with active/paused/completed
  goal counts, lead-goal phase and next action, goal switch links,
  same-page action-form availability for the lead Goal, progress, and waiting
  counts so the daily cockpit can switch goals without falling back to the
  full inventory. When no Goal exists yet, `/today` points the command center,
  Today Goal Queue, Start Here, and reused Home Day Plan targets directly to
  the same-page `Create Project` or `Create First Goal` form rendered by the
  first-run guide instead of requiring a detour to `/goals`. It then reuses
  the Start Here, Home Day Plan, Attention Brief,
  Focus Queue, recent activity, inbox, recommendations, incidents, and
  first-run panels without writing on GET or adding action authority. The
  local app also exposes `/resume` as a
  read-only return-to-work surface over saved `.clanker/app/workspace.json`
  state, showing saved goal, project, artifact, filters, expanded panels,
  zero-effect counters, a direct next resume link, a read-only
  `Resume Command Bar` for readiness, current phase/gate, one next action,
  target surface, action-form availability, last artifact, and zero-effect
  counters, followed by a `Resume Operator Workbench` that turns the saved
  context into do/check/unblock/finish cards with same-page action-form
  routing when available, readiness repair, blocker routing, last-artifact
  readback, and the existing `/workspace#save-workspace` finish surface. It
  also includes a `Resume Readiness` checklist for the saved project, goal,
  filters, expanded panels, last artifact existence, and next local surface,
  and the saved goal's current phase plus one recommended next action and the
  same confirmed local action form as the Goal page when that action is
  browser-available, plus a read-only `Resume Workflow Map` sourced from the
  same Goal remaining-work gates so the saved goal's current gate, lifecycle
  progress, next surface, and zero-effect boundaries are visible before
  leaving `/resume`; before a saved Goal exists, `/resume` follows first-run
  progress instead, so an empty checkout points to Home's `Create Project`
  anchor and a registered-project/no-goal workspace points to Home's
  `Create First Goal` anchor while still showing the saved project, without
  writing on GET;
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
  `/verification` includes a read-only `Verification Command Bar` that
  summarizes workflow configuration, current checkout commit when available,
  latest local CI proof source/status/scope, current-proof posture, one next
  proof action, target surface, and no-write/no-GitHub-polling/no-external-
  effect boundaries before the longer testing map; `/ci-evidence` includes a
  read-only `CI Evidence Command Bar` that summarizes handoff/snapshot record
  counts, latest proof, current-proof posture, and same-page recording or
  review targets before the JSON paste form and evidence lists;
  `/search` for bounded global search across indexed goals, projects,
  delegations, known artifacts, incidents, recommendations, memory, runs,
  approvals, and skills, with goal results including live local phase, one
  recommended next action, and remaining-work counts, plus a read-only
  `Search Command Bar` that summarizes result counts by category, first
  result, target link, summary, and no-write/no-network/no-raw-filesystem
  boundaries;
  `/incidents` includes a read-only `Incident Triage Command Bar` that
  summarizes open/resolved incident counts, open task-recommendation counts,
  the first local incident or recovery recommendation to review, evidence
  links, stable open/resolved/recommendation anchors, and no-write/
  no-resolution-on-GET/no-network/no-external-effect boundaries;
  `/delegation-runs` includes a read-only `Delegation Run Command Bar` that
  summarizes completed/pending delegation runs, incidents, retry candidates,
  context-pack and implementation-handoff readiness, the first local
  delegation/run/workflow surface to inspect, stable attention/coder-prep/
  recent-run anchors, and no-write/no-provider/no-network/no-external-effect
  boundaries before the longer execution evidence index;
  `/workflow` includes a read-only `Workflow Command Bar` that summarizes the
  selected delegation or coder run, parent Goal, project, current workflow
  stage, next local action, target surface, reason, and zero-effect counters
  before the detailed selected-state map and continuation links;
  `/artifacts?path=...` includes a read-only `Artifact Command Bar` that
  summarizes bounded artifact path, render type/family/renderer, size,
  rendered bytes, line count, truncation state, inferred project/goal context,
  workspace anchor status, one next action, and no-write/no-raw-filesystem/
  no-content-execution/no-network/no-external-effect boundaries before the
  inert content renderer and remember-artifact form. It also includes a
  read-only `Artifact Review Brief` that links goal-scoped artifacts back to
  their Goal and Project, identifies saved resume anchors, and points
  unclassified artifacts toward the remember/resume workspace path;
  `/workspace` for persistent open project/goal/filter/panel/last-artifact
  state in `.clanker/app/workspace.json` plus the saved goal's current phase,
  one next action, operator attention cue, target surface, and the same
  confirmed local action form as the Goal page when that action is
  browser-available beside the editable saved-state form, plus a read-only
  `Workspace Daily Brief` that summarizes the saved project, goal, artifact,
  next local action, current gate, resume readiness, and finish-today save
  status before any editable fields. It also includes a `Workspace Operator
  Workbench` that turns the saved state into do/check/unblock/finish cards
  with same-page action-form routing when available, readiness and blocker
  routing, last-artifact readback, and the confirmed save form as the finish
  target, followed by a read-only `Workspace Workflow Map` sourced from the
  same Goal remaining-work gates so the current saved gate stays visible while
  editing resume context. Before a saved Goal exists, `/workspace` follows
  first-run progress instead: empty checkouts point those sections at Home's
  `Create Project` anchor and registered-project/no-goal workspaces point at
  `Create First Goal` while preserving the saved project link; `/memory` for project/global/
  generated memories, proposed memories, operator notes, future work, and pin
  actions, with a read-only `Memory Command Bar` that summarizes entry counts,
  first proposed pin or fallback resume target, one next local action, saved
  workspace context, and no-write/provider/network/external-effect boundaries
  before the longer lists; `/skills`
  for available/generated skill records with usage counts and a read-only
  `Skills Command Bar` that summarizes record, generated, usage, and
  project-usage counts, points at the first generated or available skill
  artifact, names one local review target, and keeps execution/install/
  provider/network effects disabled; `/approvals` as a
  local decision queue with a read-only `Approval Queue Command Bar` that
  summarizes pending worktree/commit/publication counts, first recommended
  decision, target section, after-decision guidance, and zero-effect boundary,
  followed by an `Approval Operator Workbench` with do/inspect/Goal/finish
  cards, parent Goal routing, request/evidence artifacts, confirmation
  posture, and a confirmed `save-workspace` form that stores the queue as a
  future resume point without writing on GET;
  and `/profiles`
  for inactive future provider-routing readback from `.clanker/profiles.yml`
  and SQLite profile storage rows, including profile labels, modes, cost
  tiers, model placeholders, write posture, adapter status, and `use_for`
  labels plus a read-only `Profiles Command Bar` that summarizes configured,
  storage, enabled, disabled, future-lane, adapter, write-posture, and
  use-for counts, names one local review target, and keeps provider/model
  routing disabled.
  The `/goals` and Home first-run panel now exposes a state-aware
  Create project -> Create first goal -> Create first delegation -> Generate
  context pack -> Run first delegation checklist plus confirmed local
  `register-project` and `create-goal` forms, explicitly defaults the first
  dogfood project to `clankeros` at the current repository path, persists
  resume workspace state after confirmed browser project registration and
  first goal creation, and now refreshes the same saved workspace anchor after
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
  cockpit starts with a read-only `Goal Board Command Bar` that prioritizes
  the saved or active Goal, phase, one next action, target local surface,
  waiting counts, resume route, action availability, and zero-effect counters
  before the active/paused/completed lanes. It also exposes a confirmed
  local `Start Another Goal` form for registered projects, so daily goal
  creation does not require the CLI. The checklist reports the current step,
  one `first_run_next_action` with a reason, project/goal/delegation/
  context-pack state, next local surface, a confirmed local `run-delegation`
  action once context is ready, and a copyable CLI fallback while keeping
  provider calls, network actions, push, PR creation, deploy, and external
  mutation unexposed. Shared goal rows in Home, `/goals`, and project detail
  pages now show phase, next action, progress, and compact remaining-work
  counts for open tasks, incidents, and recommendations. Goal detail pages now
  expose first-class Goal Risk and Goal Completion Criteria sections sourced
  from task risk metadata, sprint contracts, plan steps, or task verification
  plans. Goal Risk starts with a read-only `Goal Risk Command Bar` that
  summarizes risk level, task risk counts, approval-boundary posture, first
  task risk/status, one next local surface, and no-write/no-provider/no-network/
  no-external-effect boundaries before the detailed risk list. Goal Completion
  Criteria starts with a read-only `Goal Criteria Command Bar` that summarizes
  criteria source, item count, progress, plan/contract posture, first
  acceptance item, one next local review surface, and no-write/no-provider/
  no-network/no-external-effect boundaries before the detailed criteria list.
  Goal detail pages now place the large Current Phase banner immediately after
  the Goal summary and before an in-flow read-only `Goal Jump Bar` for phase,
  action, workflow, timeline, evidence, artifacts, notes, git, and remaining
  work. Visible `1`-`9` key badges and `aria-keyshortcuts` jump to those local
  anchors without submitting forms. A compact fixed desktop `Goal Action Dock`
  follows the jump bar and keeps the current action, workflow gate, CI proof
  target, and `/resume` route visible while jumping directly to the existing
  confirmed Goal action form when one is available instead of duplicating
  action authority. It becomes static on narrow screens and precedes the Goal
  Command Bar, Goal Operator Workbench, Daily Loop, Goal Return Brief, Goal
  Continuation Rail, Next Action, Workflow Map, Goal CI Handoff, live refresh
  panel, and long section index, so the first
  viewport names the current phase before
  navigation and diagnostics. Goal Progress starts with a read-only `Goal Progress Command Bar` that
  summarizes task completion, workflow gate progress, current gate, waiting
  approvals/incidents/recommendations, one next local action, and no-write/
  no-provider/no-network/no-external-effect boundaries before the browser
  progress bar and detailed counts.
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
  `Goal Timeline Command Bar` that summarizes total events, the latest linked
  event, event-family counts for artifacts, approvals, delegations, runs,
  tasks, and operator notes, and zero-effect boundaries before the full
  chronological list. Goal pages include a browser-native progress
  bar and a large Current Phase banner that explains the phase reason,
  operator attention cue, next action surface, latest activity, and zero-effect
  boundary without requiring the CLI. Home and Goal activity sections now also
  include read-only activity command bars that summarize the latest
  human-readable event, target surface, operator-note/artifact counts, and
  zero-effect boundaries before the longer activity lists. Goal detail pages also include a
  read-only `Goal Command Bar` near the top that condenses phase, one primary
  action, target local surface, progress, waiting counts, `/resume`, latest
  project-scoped CI proof status, and write-on-GET/network/external-effect
  boundaries into one operator scan. A `Goal Operator Workbench` follows it
  with a human-readable do/check/unblock/finish strip, pointing its primary
  action directly at the in-page Goal action form when available, the source
  surface, current gate/progress, first unblock surface, and confirmed
  local-action counters before the longer diagnostic sections. The in-flow Goal Jump Bar keeps the main daily anchors
  one click or keypress away without covering later controls, the Goal Action
  Dock keeps the current action one click away from deep scroll positions by
  jumping directly to the confirmed form without adding a second action form,
  and the Goal Next Action section starts
  with a human-first focus strip for Now, Gate, Target, and Boundary, then
  renders the confirmed form before collapsed action evidence. The Goal Section Index now links
  directly to the Timeline, Activity, and Git command bars in addition to the
  longer detail sections, making the page navigable through scan-first
  operator surfaces.
  Goal Overview starts with a read-only
  `Goal Overview Command Bar` so the operator sees goal identity, status,
  phase, risk, progress, local counts, next click, and no-effect boundaries
  before the raw overview metadata. Goal detail pages also include a
  `Goal Daily Loop` near the top that condenses start, continue,
  unblock, and finish cues from the same local Goal/workspace/approval/
  incident/recommendation state, including whether the saved workspace points
  at the current goal and latest artifact before the operator ends the day,
  and exposes confirmed local `pause-goal` and `save-workspace` forms. The
  pause action is local status movement only: it accepts non-paused incomplete
  goals, sets status to `paused`, refreshes saved workspace context to the Goal
  artifact, and does not approve work, run work, call providers, use the
  network, push, create PRs, deploy, or mutate external systems.
  A read-only `Goal Return Brief` follows the daily loop near the top of the
  Goal page and condenses current gate, next action, resume readiness, latest
  activity, latest artifact, CI proof posture, blocker routing, `/resume`, and
  finish surface into one return-to-work snapshot without writing on GET.
  A read-only `Goal Continuation Rail` follows it with the current gate, the
  next few local workflow gates, their operator surfaces, and the final manual
  publish boundary preserved as outside ClankerOS, so the Goal page can be
  followed without jumping straight to longer diagnostics.
  Goal detail pages also include a
  read-only `Goal Workflow Map` near the top that renders the same
  Remaining Work gate state as a lifecycle rail, highlighting the current
  gate, next action, done/pending/waiting counts, each gate's eventual local
  operator surface, and zero-effect boundary. A read-only `Goal CI Handoff`
  follows it with project-scoped proof status, latest operator-recorded
  GitHub Actions evidence, exact `gh run list` / `gh run view` command
  templates, and a same-page proof-recording target before the operator
  reaches the long timeline and artifact sections, without app-side GitHub
  polling or external mutations. Goal
  Remaining Work itself starts with a read-only `Goal Remaining Work Command
  Bar` that summarizes current gate, done/pending/waiting gate counts, open
  task/incident/recommendation counts, pending approvals, one next local
  surface, and no-write/no-provider/no-network/no-external-effect boundaries
  before the detailed checklist. Goal
  detail pages also include a
  first-class `Next Recommendation` section that identifies whether the current
  recommendation came from an open task recommendation or was derived from
  current phase and local goal records, points at the target local surface, and
  records write-on-GET and external-effect boundaries. They also include a
  first-class `Goal Live State` readback and local page reload polling that
  pauses while the operator is editing a form or the tab is hidden; it does not
  fetch GitHub status, call providers, push, create PRs, deploy, or mutate
  external systems. They also include a read-only `Goal Section Index` with
  stable in-page anchors including the command bar, workflow map, and the
  major Goal surfaces,
  so operators can jump
  through a long Goal workbench without leaving the page or triggering writes.
  Every app page also includes a shared read-only `Operator Focus` strip that
  derives from the saved workspace goal or current lead goal and now opens with
  compact action cards for the primary action, phase, progress, waiting counts,
  and `/resume`, followed by the expandable confirmed local action form when
  the current next action is browser-available and collapsed `Focus evidence`
  for the full readback and no-write/no-provider/no-network/no-external-effect
  boundaries outside the Goal page. When
  no Goal exists yet, the shared shell now treats that as first-run progress:
  Home, Today, and Goals point `Route Context`, `Operator Focus`, and the
  command palette at their same-page `Create Project` or `Create First Goal`
  anchors, while other pages link back to Home/Today/Goals first-run anchors.
  The command palette now opens with a compact `Palette Focus` launcher for
  continuing the current Goal action, searching local state, resuming the saved
  workspace, or staying on the current page. Its detailed route readback,
  keyboard shortcuts, long open list, and zero-effect counters are still
  available inside collapsed `Palette evidence and shortcuts`, while the
  goal-aware `Continue Current Goal` form remains directly below search.
  They also include a read-only `Goal Operator Notes Command Bar` before the
  confirmed `save-goal-note` form. The command bar reports whether the
  goal-scoped `operator-notes.md` artifact exists, timestamped entry count,
  artifact size, workspace resume-anchor posture, one review or capture target,
  and no-write/no-provider/no-network/no-external-effect boundaries. The
  confirmed note form appends local operator resume context to the artifact;
  saved operator notes also become linked `Operator note saved` entries in the
  Goal timeline and recent Activity Log with zero external effects, and the
  confirmed note action now refreshes saved workspace state to the
  operator-notes artifact so `/resume`, Home, and `/workspace` return to the
  note context without a separate manual
  save. They also include a confirmed `delegate`
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
  include a `Goal Resume Snapshot` that reads saved workspace state, links the
  current goal/project, suggests the newest goal artifact as a resume anchor,
  renders saved filters, expanded panels, and last-viewed artifact as
  `Goal Workspace Restore State`, and exposes a confirmed `save-workspace`
  form that returns to the same goal page after saving without writing on GET.
  Goal `Completion Readiness` summarizes the same workflow gates, local
  blockers, approvals, and publication handoff state used elsewhere on the Goal
  page into one finish posture. It identifies the current blocker or next safe
  action, links the relevant local surface, reports no-write, no-network, and
  no-external-effect boundaries, and only exposes the confirmed `complete-goal`
  form after the manual publish handoff is ready.
  Goal `Incidents` now starts with a read-only `Goal Incident Command Bar`
  that summarizes open/resolved incidents, open recommendations, the first
  incident's severity, run, task, evidence, one triage surface, and no-write/
  no-provider/no-network/no-external-effect boundaries, then links to
  `/incidents`, shows open/resolved/total incident counts, and lists goal-owned
  incident status, severity, run, task, summary, and evidence artifact links
  without taking action.
  Goal `Remaining Work` now starts with a read-only `Goal Remaining Work
  Command Bar` and then renders a gate-aware checklist from local state,
  showing the next action, current gate, open task/incident/recommendation
  counts, pending approvals, and done/pending/waiting status for scout,
  context-pack, implementation handoff, coder prep, worktree, review, commit,
  publication, and manual publish gates without taking action.
  Goal `Memory` now links to `/memory`, shows project/global memory artifacts,
  goal-scoped memory entry counts, generated memory count, operator-note
  status, future-work count, latest memory summaries, and the fact that
  pinning remains available on the confirmed `/memory` surface rather than on
  the read-only Goal page. It starts with a read-only `Goal Memory Command Bar`
  that summarizes memory entry counts, memory artifact posture, operator-note
  state, future-work count, one next local memory action, and zero-effect
  counters before the detailed memory readback. The `/memory` surface now starts with a read-only
  `Memory Command Bar` so proposed-memory pins, operator-note review, future
  work, saved workspace resume, and empty-bank starts have one visible next
  click before the inventory. Confirmed `/memory` pinning promotes only entries
  with existing evidence artifacts and refreshes saved workspace state to that
  artifact with zero provider, network, or external mutation effects.
  The shared browser shell now exposes accessible shortcut metadata for Home,
  Resume, Goals, Search, palette, and theme controls, and the palette can be
  closed with Escape even while the search input is focused; the shortcut layer
  remains local-only and creates no server writes. The command palette also
  starts with a route-aware `Current Page` block that mirrors the current
  path, parent surface, resolved Goal/Project/run context, focus target,
  `/resume`, and zero-effect readbacks before the visible keyboard-shortcut
  help block generated from the same shortcut map, so operators can discover
  both where they are and the local navigation shortcuts from inside the app
  instead of reading external docs. When a saved or lead Goal exists, the
  command palette also includes a compact Goal continuation readback for the
  current workflow gate, the next few local gates, their target surfaces, and
  the manual publish boundary without writing on GET.
  The Goal `Skills Used` section starts with a read-only `Goal Skills Command
  Bar` that summarizes task skill tags, matching generated or available local
  skill records, usage and project counts, delegation profile usage, one
  `/skills` or `/profiles` review target, and no-execution/no-install/
  no-network boundaries before the detailed skill readback.
  Goal `Git Status` starts with a read-only `Goal Git Command Bar` that
  summarizes the registered project root, branch, commit, clean/dirty posture,
  tracked and untracked counts, latest goal-linked `git_status.txt` artifact,
  one next local surface, and no-fetch/no-write/no-network/no-external-effect
  boundaries before the repository snapshot.
  Goal `Delegations` starts with a read-only `Goal Delegation Command Bar`
  that summarizes scout delegation counts, context-pack readiness,
  implementation handoff readiness, coder-prep packets, worktree plans, the
  latest delegation workflow surface, one next local continuation, and
  zero-effect counters before the detailed delegation rows.
  Goal `Runs` starts with a read-only `Goal Run Command Bar` that summarizes
  task and worktree run counts, reviewed and blocked run gates, changed-file
  posture, latest run evidence, one next local run action, and zero-effect
  counters before the detailed run rows.
  Goal `Approvals` starts with a read-only `Goal Approval Command Bar` that
  summarizes pending and approved worktree, commit, and publication approval
  gates, selects one local approval or continuation surface, and reports
  write-on-GET/provider/network/external-effect counters before the detailed
  approval rows.
  Goal `Evidence` starts with a read-only `Goal Evidence Command Bar` that
  summarizes run evidence, worktree evidence, incident evidence,
  recommendation evidence, typed artifact counts, latest artifact, one local
  review target, and zero-effect boundaries before the detailed evidence list
  and typed artifact explorer.
  Goal `Verification Evidence` starts with a read-only
  `Goal Verification Command Bar` that summarizes project-scoped proof status,
  latest source/status/scope, branch and commit freshness, one proof action,
  target surface, and zero-fetch/zero-effect boundaries before the detailed
  proof lines. It links to `/verification` and `/ci-evidence`, filters local
  operator-supplied CI proof records to the current goal project, compares the
  recorded branch/commit to the current project checkout, distinguishes
  missing, stale, job-scoped early proof, and current full workflow proof, and
  reports missing or stale proof without fetching GitHub status. It also
  exposes a confirmed Goal-scoped `ci-snapshot-evidence-from-gh-json` form
  that accepts pasted GitHub Actions JSON, infers run identity from
  `databaseId`/`url`, validates status, branch, commit, and optional job
  status, then records local project CI proof and returns to the same Goal
  page without app-side GitHub polling.
  They also include a typed
  `Goal Artifact Explorer` that groups goal-linked Markdown,
  JSON, Patch/Diff, and Text/Log artifacts and links them through the bounded
  inert `/artifacts` viewer without raw filesystem browsing. Goal `Artifacts`
  starts with a read-only `Goal Artifact Command Bar` that summarizes artifact
  record counts, available/missing posture, render-family counts,
  source-family counts, the latest artifact, one bounded review click, and
  zero-effect counters before the detailed artifact list and typed explorer.
  The artifact
  viewer now reports render family/renderer posture and renders Markdown as
  escaped headings/lists/paragraphs, JSON as pretty-printed text, patch/diff
  artifacts with scan-friendly line classes, and text/log artifacts as inert
  text while keeping content execution disabled. It also exposes a confirmed
  local `save-workspace` form so the operator can remember the current artifact
  as the next-session resume anchor without writing on GET. Every page shares
  a browser operator shell with a read-only `Route Context` breadcrumb strip,
  recent local items, a read-only `Last Action` strip after confirmed local
  actions, a command palette, keyboard shortcuts, and a theme toggle. The last
  action strip reads `.clanker/app/workspace.json` and exposes the latest
  completed local action, result, notice target, saved project/goal context,
  timestamp, and zero-effect counters without writing on GET. The route
  context strip now starts with a compact action-first focus grid for the
  current page, next local action, back target, Goal, Project, and `/resume`,
  while route family/path, saved workspace anchors, focus target, and
  zero-effect boundaries stay available inside collapsed `Route evidence`
  before the page body. The
  recent-items sidebar now starts with a read-only `Recent Items Command Bar`
  that shows one compact reopen action plus `/resume`, then keeps
  workspace/goal/delegation/run counts, saved workspace project/goal/artifact
  context, last-action context, and zero-effect boundaries inside collapsed
  evidence, with the longer recent-link list in a second collapsed disclosure.
  The command palette now also
  starts with the same current-page route context, parent link, resolved
  Goal/Project/run context, focus target, `/resume`, and zero-effect readbacks
  inside the keyboard-driven surface. The shared focus strip and command
  palette include the same goal-aware current-action readback from the saved
  workspace goal or current lead goal, showing phase, one recommended action,
  target surface, a compact current-gate continuation readback, zero-effect
  readbacks, and the same confirmed local action form as the Goal page when
  the current next action is browser-available. In
  first-run states, those shared surfaces point at the concrete setup form for
  the current route when possible, or at the Home/Today/Goals first-run anchors
  when the current page does not render the guide.
  They still write nothing on GET and only submit existing local forms after
  explicit confirmation. The workflow page
  can be
  scoped with a
  delegation or coder run id, then annotates related stepper rows with
  selected local artifact, approval, run, commit, publication, and next-action
  status, plus a read-only `Selected Workflow Continuation` block linking the
  exact run, approvals, inbox, and dogfooding surfaces without creating
  external effects. Coder worktree
  run detail pages include a read-only `Run Command Bar` that summarizes run
  status, review gate, commit/publication state, changed-file count, diff
  summary, next local action, target surface, and no-write/no-network/
  no-external-effect boundaries. A `Run Operator Workbench` follows it with
  do/check/unblock/finish cards, same-page action anchors, review/evidence
  links, approvals, parent Goal, and a confirmed `save-workspace` form that
  stores the run plus review/evidence artifact as a future resume point
  without writing on GET, followed by the same upstream and downstream workflow
  posture as a `Run Workflow State` readback, plus a `Run Review Gate`
  readback that mirrors the backend requirement that
  `runs/<source_run_id>/review.md` exists and mentions the coder worktree run
  id before `coder-commit-request` is offered; once publication handoff is
  ready they show copy-only suggested push and draft-PR commands plus the PR
  body path with zero-effect counters.
  The root `/` app page is now a Goal-First Home board with active, paused,
  and completed goal lanes, recent activity, inbox counts, recommendations,
  incidents, saved workspace resume links, saved-goal phase and next-action
  readbacks, a read-only `Start Here` cockpit that condenses the lead goal or
  first-run step, one primary action, target surface, resume readiness,
  waiting counts, and CI handoff posture into a single scan-friendly panel, a
  form-backed `Home Day Plan` that names the current goal, current phase, one
  next action, waiting counts, end-of-day resume readiness from saved
  workspace state, and a confirmed local `save-workspace` Finish Today form
  that records the lead goal and latest artifact as tomorrow's resume point
  after confirmation, a read-only `Home Attention Brief` that prioritizes
  existing approvals, incidents, recommendations, inbox load, and local CI
  proof posture before deeper goal work without fetching GitHub status, a
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
  posture, and zero-effect counters; after a Goal exists, it can render the
  same confirmed local next-action form inline for scout delegation,
  context-pack generation, and first delegation execution. After a confirmed
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
  delegation execution run ids and renders scout evidence, result artifacts,
  context-pack and handoff status, zero-effect counters, and next-action
  readback; a read-only `/actions` catalog with an `Action Catalog Command
  Bar` for safe local action counts, first action, target anchors, local
  execution/git/approval/artifact posture, confirmation posture, form
  locations, output artifacts, and external-effect boundaries, plus an
  `Action Operator Workbench` that reads first-run or lead-Goal focus, names
  the current local action, links the owning surface for the confirmed form,
  routes blockers, and provides a confirmed project/Goal resume save point
  without adding action authority to the catalog page; a read-only
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
  fallback, with copy-only `gh run view` / validated recorder templates and
  explicit fast-smoke-versus-full-suite proof boundaries, while still
  performing no GitHub polling; a
  read-only root dashboard `Verification Snapshot` for checked-in workflow
  timeout, latest operator-supplied CI evidence, `/verification`,
  `/ci-evidence`, and current direct-snapshot handoff templates without
  contacting GitHub; a read-only root dashboard
  `Dashboard Dogfooding Snapshot` for fixture availability, next dogfooding
  action, selected workflow/run links, and the `/demo` manual browser script
  surface; a read-only `/dogfooding` command bar for fixture status, selected
  project/Goal/delegation/run, the next local target surface, route/CI/action/
  health links, and zero-effect counters; a read-only `/dogfooding` GitHub
  Actions follow-up section with direct pushed-snapshot `ci-snapshot-handoff`,
  `gh run view`, JSON-validated record, and manual record-after-success
  templates for the current checkout; a
  read-only `/actions` current-demo action surface map that links fixture state
  to the selected project, delegation, workflow, run, approvals, and inbox
  surfaces; a read-only `/dogfooding` checklist and next-action panel for the
  first browser route walk, fixture refresh, scoped workflow/run links, local
  commit/publication gate sequence, and GitHub Actions handoff boundary
  without fetching GitHub status; `/health` includes a `Health Command Bar`
  that summarizes warning count, bind scope, branch/commit, storage/import
  readiness, the refreshed local status artifact, explicit
  `status_artifact_write_on_get=true`, one next local surface, and zero
  provider/network/external-effect counters before the detailed diagnostics; a read-only
  operator inbox plus local approval and
  incident pages for pending worktree, commit, and publication decisions,
  with the inbox starting from a read-only `Inbox Command Bar` that summarizes
  total local queue size, queue-type counts, the first attention item, target
  section, reason, and zero-effect boundary, followed by an
  `Inbox Operator Workbench` with do/inspect/Goal/finish cards, Goal/
  delegation/run/evidence routing, a continuation surface, and a confirmed
  `save-workspace` form that stores the queue as a future resume point
  without writing on GET while preserving read-only run links and next-action
  cues for pending commit/publication rows,
  with `/approvals` starting from both a queue summary and a read-only
  `Approval Decision Brief` that links the first local decision to its
  delegation, workflow, run when available, request artifact, evidence
  artifact, exact form anchor, post-decision surface, and zero-effect counters,
  with commit/publication approval rows linking back to the relevant run and
  naming the next local-only follow-up action after approval,
  operator-worthy queue items, incident evidence readback, a confirmed
  dashboard refresh action for rewriting the local app status artifact from
  current repo and route state, a read-only state-aware root dashboard
  recommendation that points to the next operator surface, and a state-aware
  `/demo` launchpad that starts with a read-only `Demo Command Bar` for
  fixture availability, preferred demo command, compatibility command,
  selected project/Goal/delegation/run, next local surface, and zero-effect
  counters, then links the fixture project, selected workflow, delegation,
  coder worktree run, review artifact, inbox, approvals, first manual browser
  dogfooding script, a read-only next-action panel, and a browser-progress
  checklist for commit/publication handoff status, plus a
  read-only `Demo Gate Artifacts` map for commit request, commit decision,
  local commit, publication request, publication decision, publication
  handoff, and PR-body artifacts as those gates become available, plus a
  state-aware `Demo Gate Actions` panel that names the current gate, local
  form action, required input, expected output artifact, and renders the safe
  confirmed local form for the active gate when one exists. At the manual
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
  a read-only `Action Confirmation Command Bar`, submitted action payload, and
  safety boundary before a confirmed local write, local approval decision, or
  bounded local execution; confirmed action result pages render the submitted
  payload, local
  result fields, artifact links, next-page link, safety boundary, and an
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
  GET pages render an escaped
  `Action Notice` banner when reached through a notice link;
  action error pages render the attempted action, submitted payload, error
  details, and a no-action-completed non-claim. It does not push, create PRs,
  deploy, call providers, execute arbitrary commands, or use the network
  beyond local browser/server loopback.
- Local app smoke testing: `app-smoke-test` renders the core local app routes
  without starting a server, requires route-specific page markers such as
  `ClankerOS Local Operator`, `Modern Operator Workflow`, `Safe Action
  Catalog`, `Verification Handoff`, and `CI Evidence Records`, and reports
  `marker=matched` or `marker=missing` per route while preserving
  provider/network/external-mutation counters at zero. `app-demo-smoke-test`
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
