# Status Entry Point

The canonical chronological implementation log is [`../status.md`](../status.md).

Latest status focus:

- `/goals/<goal_id>` now keeps the top of the Goal detail page more
  action-first: the Goal Jump Bar still exposes the nine daily anchors, the
  Goal Command Bar opens with visible Now, Phase, Progress, Proof, and Resume
  cards, the Goal Operator Workbench keeps its do/check/unblock/finish cards
  visible, and the Goal Daily Loop now exposes Continue, Start, Unblock, Pause,
  and Finish Today cards with direct hash-opened pause/save details. Goal
  Return Brief now follows with visible Continue, Latest, Blocker, Finish, and
  Resume cards, and Goal Continuation Rail now exposes Now, Next Gate, Then,
  Publish Boundary, and Finish Today cards. Goal Workflow Map now exposes Now,
  Progress, Approvals, Publish Boundary, and Finish Today cards before its
  detailed lifecycle rail. Goal CI Handoff exposes Check GitHub, Record Proof,
  Current Proof, Full Suite, and Finish Today cards, and Goal Live State now
  exposes Now, Phase, Refresh, Pause Rules, and Safety cards before its
  detailed refresh evidence. Jump, command, workbench,
  daily-loop, return-brief, continuation, workflow-map, CI handoff, live-state,
  and full section-index evidence are
  collapsed by default while preserving phase, next action, current gate,
  project-scoped CI proof posture, full anchor map, daily resume-save state,
  latest activity/artifact, blocker routing, workflow gate surfaces, manual
  publish boundary, local reload posture, and zero-effect counters in the DOM.
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
  walkthrough. Demo workbench and command evidence stay collapsed by default
  while preserving fixture status, selected project/Goal/delegation/run, next
  local target, proof checkpoints, demo command templates, and zero-effect
  counters in the DOM.
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
  inert content. Artifact workbench, command, and review evidence stay
  collapsed by default while preserving bounded path, renderer, context,
  workspace anchor, and zero-effect readbacks in the DOM.
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
  diagnostics. Project-index evidence, project workbench evidence, command
  evidence, and project finish forms stay collapsed by default while
  preserving project counts, first project action, resume state, proof
  posture, and zero-effect readbacks in the DOM.
- `/verification` is now action-first: it opens with the `Verification
  Operator Workbench` before shared route/focus diagnostics or command
  evidence, shows visible Now, Check GitHub, Proof, and Finish Today cards,
  and keeps verification workbench evidence, command evidence, and the
  finish-today save form collapsed by default while preserving current proof
  posture, CI handoff commands, proof-recording target, and zero-effect
  readbacks in the DOM.
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
  visible Now, State, Queue, and Resume cards, and keeps workflow command and
  workbench evidence collapsed by default while preserving selected
  delegation/run, parent Goal, project, current stage, next local action,
  target surface, selected-step counts, and zero-effect proof in the DOM.
- `/profiles` is now action-first: it opens with the `Profiles Operator
  Workbench` before shared route/focus diagnostics or command readback, shows
  visible Now, Lanes, Storage, and Resume cards, and keeps profiles state,
  workbench evidence, and command evidence collapsed by default while
  preserving future-lane, storage-profile, provider-disabled, model-routing-
  disabled, and zero-effect proof in the DOM.
- `/skills` is now action-first: it opens with the `Skills Operator
  Workbench` before shared route/focus diagnostics or command readback, shows
  visible Now, Generated, Usage, and Resume cards, and keeps skills state,
  workbench evidence, and command evidence collapsed by default while
  preserving generated-skill, usage, artifact, and zero-effect proof in the
  DOM.
- `/memory` is now action-first: it opens with the `Memory Operator Workbench`
  before shared route/focus diagnostics and command readback, shows visible
  Now, Pin, Notes, and Resume cards, and keeps memory state, workbench
  evidence, and command evidence collapsed by default while preserving pin,
  resume, workspace, and zero-effect proof in the DOM.
- `/search` is now content-first and search-action-first: it opens with the
  `Search Operator Workbench` before shared route/focus diagnostics, shows
  visible Query, Open, Results, and Resume cards, and keeps search state,
  workbench evidence, and command evidence collapsed by default while
  preserving bounded indexed-search proof and zero-effect counters in the DOM.
- `/today` is now content-first and command-center-first: it opens with the
  `Today Command Center` before shared route/focus diagnostics, keeps Today
  state, command, and workbench evidence collapsed by default, and opens the
  note, pause, and Finish Today forms only when the operator clicks their
  visible cards or navigates to the matching hash. The page still preserves
  goal/readiness/CI/zero-effect proof in the DOM.
- `/workspace` is now content-first and finish/resume-action-first: it opens
  with the `Workspace Operator Workbench` before shared route/focus diagnostics,
  saved-state evidence, or restore-link readbacks. Browser-available saved
  actions render immediately below the workbench, the daily brief and workflow
  map follow, and saved-state/restore/save-form details stay collapsed until
  the operator opens them. Direct `/workspace#save-workspace` navigation now
  opens the collapsed save form client-side.
- `/inbox` is now content-first and queue-action-first: it opens with the
  `Inbox Operator Workbench` before shared route/focus diagnostics or command
  readback, while inbox command and workbench evidence stay collapsed by
  default. The page still preserves queue counts, first attention item,
  Goal/delegation/run/evidence routing, a collapsed finish-today workspace
  save form, and zero-effect counters in the DOM.
- `/resume` is now content-first and return-to-work-first: it opens with a
  primary saved-context link and `Resume Operator Workbench` before shared
  route/focus diagnostics or command readback, while saved workspace state,
  command evidence, and workbench evidence stay collapsed by default. The page
  still preserves saved project/Goal/artifact/filter/panel readbacks,
  first-run continuation, readiness checks, same-page action-form routing, and
  zero-effect counters in the DOM.
- `/actions` is now content-first and action-first: the page opens on the safe
  action header and `Action Operator Workbench` before shared route/focus
  diagnostics or catalog readback, while action safety, workbench evidence, and
  catalog evidence stay collapsed by default. The catalog still exposes visible
  Catalog, Forms, Approvals, and Boundary cards plus all prior zero-effect
  counters in the DOM.
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
  sections.
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
- The shared Operator Focus strip is now compact and action-first: it shows
  the primary action, phase, progress, waiting counts, and `/resume` as visible
  cards, keeps the confirmed local action form available when relevant, and
  moves the full focus readback plus zero-effect counters into collapsed
  `Focus evidence`.
- The shared Route Context strip is now compact and action-first: it shows the
  current page, one primary next local action, back target, Goal, Project, and
  `/resume` before any diagnostic route rows, while the full route evidence and
  zero-effect counters remain available inside collapsed `Route evidence`.
- The shared Recent Items sidebar is now compact and action-first: it shows one
  primary reopen link plus `/resume`, while counts, saved context, last action,
  zero-effect counters, and the longer shortcut list stay available inside
  collapsed evidence/details.
- Goal Action Dock and Goal Operator Workbench primary links now jump directly
  to `#goal-next-action-form` when the confirmed browser action form exists,
  so persistent/top-of-page action controls land on the actionable form instead
  of the broader Next Action readback.
- Goal Next Action sections now open with a human-first focus strip for Now,
  Gate, Target, and Boundary, giving the operator one readable primary link to
  the existing confirmed form or source surface, then placing the confirmed
  form before collapsed action evidence.
- Goal pages include a compact fixed desktop `Goal Action Dock` after the
  Current Phase banner and Goal Jump Bar, keeping the current action, workflow
  gate, CI proof target, and `/resume` route visible during long scroll
  sessions while jumping directly to the existing confirmed action form when
  one is available without adding action authority; it becomes static on
  narrow screens.
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
