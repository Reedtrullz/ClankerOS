# Status Entry Point

The canonical chronological implementation log is [`../status.md`](../status.md).

Latest status focus:

- Saved-Goal action result pages now include a visible `Continue Goal` panel
  inside `Action Result Next Step`, before the inline confirmed next-action
  form. After first Goal creation, the success page names `Create scout
  delegation`, points directly at the existing confirmation-gated form, and
  records `action_result_goal_continuation_*` evidence plus zero-effect
  counters. Local proof includes the red/green focused first-run/resume test,
  compile, the three-route first-run/resume/Today selection, and the
  fixture-backed demo scenario result-page regression.
- First-run action result receipts are now Resume-aware before a Goal exists:
  after confirmed project registration, `Resume Tomorrow` points at
  `/resume#resume-first-run-action-form` for `Create First Goal`, while the
  older receipt evidence still records the raw saved project surface. Local
  proof includes a red/green focused first-run route test plus the broader
  route and Today finish receipt checks (`3 passed` together).
- Confirmed local action result pages now lead the saved workspace receipt with
  a visible `Resume Tomorrow` section and primary return link. The older
  `Action Resume Receipt` evidence remains in place, now with
  `action_resume_tomorrow_*` rows for readiness, surface, artifact, and
  zero-effect counters. Local proof includes a red/green focused route smoke
  test plus the Today Finish path (`2 passed` together).
- Shared `save-workspace` / Finish Today forms now bridge browser-local Last
  Artifact memory into the durable workspace save path. If this browser has
  `localStorage:clankeros-last-artifact`, the `last_viewed_artifact` field is
  hydrated before confirmation/submission unless the operator manually edits
  it; `.clanker/app/workspace.json` still changes only after the confirmed
  save. Local proof includes a red/green focused route smoke test (`1
  passed`).
- The command palette now exposes a browser-local Last Artifact result backed
  by `localStorage:clankeros-last-artifact`. Typing in the palette can find the
  fallback `/artifacts` result immediately, then hydrate to `Open last artifact`
  after page load when a recent artifact exists. Canonical workspace state
  still changes only through confirmed `save-workspace`; local proof includes
  a red/green focused route smoke test (`1 passed`), compile, and diff check.
- Shared Recent Items now makes the browser-local Last Artifact breadcrumb
  global: its Artifact card reads `localStorage:clankeros-last-artifact` after
  page load and switches to `Open last artifact` when available, while the
  durable workspace artifact anchor still changes only through confirmed
  `save-workspace`. Local proof includes a red/green focused route smoke test
  (`1 passed`), compile, and diff check.
- `/resume` now surfaces the same browser-local last-artifact breadcrumb that
  `/artifacts?path=...` writes to `localStorage:clankeros-last-artifact`. The
  `Browser Resume` panel has a `Last Artifact` card that links back to the most
  recently opened artifact after page load, while canonical resume state still
  changes only through confirmed `save-workspace`. Local proof includes a
  red/green focused route smoke test (`1 passed`), compile, and diff check.
- `/artifacts?path=...` now includes an `Artifact Continuity` panel that writes
  the opened artifact to browser-local `localStorage:clankeros-last-artifact`.
  `/workspace#workspace-view-memory` includes a matching `Last Artifact` card,
  so operators can inspect or reset the latest artifact breadcrumb while the
  durable `.clanker/app/workspace.json` resume anchor still changes only after
  confirmed `save-workspace`. Local proof includes a red/green focused route
  and artifact viewer pytest selection (`2 passed`), compile, and diff check.
- GitHub Actions now runs the `Tests` workflow automatically for pushes to
  `codex/**` branches as well as `main`, so normal ClankerOS branch slices no
  longer need manual `workflow_dispatch` just to start remote verification.
  `/verification` reads this back as `push_to_codex_branches: configured`
  beside the existing push-to-main, pull-request, and manual trigger posture.
  Local proof includes a red/green workflow/route test, compile, and diff
  check.
- The shared browser shell now exposes a global `p` shortcut and header
  `Proof` button that jumps directly to
  `/ci-evidence#record-ci-snapshot-json`. It makes the evidence-recording step
  reachable from every route alongside Next Action, Recent Items, and Finish
  Today, while preserving no-write/no-provider/no-network/no-external-effect
  boundaries until the operator explicitly submits an existing form. Local
  proof includes a red/green focused route test, compile, and diff check.
- The shared browser shell now exposes a global `v` shortcut and header
  `Recent` button for the existing Recent Items / Viewed Pages rail. The rail
  has a stable `#recent-items` anchor; activating the shortcut/button scrolls
  to it and focuses the primary recent link using browser-local state only,
  preserving the no-write/no-provider/no-network/no-external-effect boundary.
- The shared browser shell now treats the global Artifact Index as a first-class
  daily destination. `/artifacts` exposes `Artifacts (a)` shortcut metadata,
  `Keyboard Shortcuts` lists `a` as `Open artifacts`, and the shared keydown
  handler routes `a` to `/artifacts` without server writes, provider calls,
  network actions, or external effects. Local proof includes compile, diff
  check, and the broad local-app route smoke pytest (`1 passed`).
- Workspace View Memory now includes the global Artifact Index filter key
  `localStorage:clankeros-artifact-index-filter`, with a separate
  `Artifact Index Filter` card alongside per-Goal `Goal Artifact Filters`.
  `/workspace` can inspect and reset that browser-local `/artifacts` view
  state without touching `.clanker/app/workspace.json`, calling providers,
  using the network, or creating external effects. Local proof includes
  compile, diff check, and the broad local-app route smoke pytest (`1 passed`).
- Bare `/artifacts` now opens a read-only global Artifact Index instead of a
  missing-path error, while `/artifacts?path=...` remains the bounded inert
  single-artifact viewer. The index exposes Open, Latest, Inventory, Types,
  and Safety cards plus a browser-local type/source/text filter using
  `localStorage:clankeros-artifact-index-filter`. Search suggestions and shell
  navigation now route directly to `/artifacts` as `Browse artifacts`, and
  known artifact paths include coder worktree reviews/evidence plus app
  status/workspace artifacts when present. Local proof includes compile, diff
  check, the broad local-app route smoke pytest (`1 passed`), and the
  fixture-backed demo scenario pytest (`1 passed`). Previous GitHub Actions
  run `28499347667` for commit `c22fe3a53f537edde7368f9a5c38cb44c8023934` is
  fully green across fast smoke and full pytest.
- Goal timeline latest ordering is now deterministic across local runs and
  GitHub Actions when lifecycle events and artifacts share the same timestamp.
  Today Session Summary / Activity Digest keep the workflow lifecycle latest
  event stable while latest artifact labels still render as readable coder-run
  review copy. This fixes GitHub Actions fast-smoke run `28498425453`; local
  proof includes the exact fast-smoke pytest selection (`15 passed, 502
  deselected`) plus compile and whitespace checks. Follow-up run `28499106431`
  exposed the sibling latest-artifact selector issue; latest artifact records
  now use deterministic ranking and Today Activity Digest prefers the ranked
  artifact registry label before timeline fallbacks. The focused demo scenario
  pytest passes after that selector fix.
- `/artifacts?path=...` relationship-map source links now show operator-facing
  labels for run-backed artifacts, for example `Open run run_demo`, instead
  of raw `/runs/run_demo` route text. Exact local routes remain preserved in
  `artifact_relationship_source_href`, while
  `artifact_relationship_source_label` records the visible label. Local proof
  includes the focused artifact viewer pytest (`1 passed`) plus compile and
  whitespace checks.
- Goal workflow/continuation guidance now routes waiting local action gates to
  the `Goal Action Dock` instead of the older generic `#goal-next-action`
  anchor, and approval gates render as `Review approvals` while preserving the
  raw `/approvals` href. This applies to the Goal Continuation Rail, Goal
  Workflow Map, command palette continuation readback, action-result workflow
  map, first-run handoff fallback, and failed-action recovery. Local proof
  includes the fixture-backed demo Goal route pytest (`1 passed`) plus compile
  and whitespace checks.
- Goal Return Brief now names the working Goal, next action, and blocker in
  the visible context line, and its evidence is title/action-first while
  preserving raw route fields. In the fixture demo it reads back
  `Demo the ClankerOS local operator app with fixture-backed state`,
  `Create commit request`, and `Review approvals`, while
  `goal_return_blocker_href` / `goal_return_resume_href` retain `/approvals`
  and `/resume`. Local proof includes the fixture-backed demo Goal route
  pytest (`1 passed`) plus compile and whitespace checks.
- Goal Daily Loop now names the working Goal and saved return action in the
  visible context line, and its Finish Today evidence is title/action-first
  while preserving the raw Goal id and exact resume href fields. In the fixture
  demo this reads back
  `Demo the ClankerOS local operator app with fixture-backed state` and
  `Create commit request` instead of raw `/goals/<goal_id>` copy. Local proof
  includes the fixture-backed demo Goal route pytest (`1 passed`) plus compile
  and whitespace checks.
- Return-path workflow maps now show the saved/lead Goal title across Home Day
  Plan, Today, Workspace, and Resume instead of raw `/goals/<goal_id>` copy,
  while preserving `*_goal_id`, `*_goal_label`, and `*_goal_label_source`
  evidence rows. In the fixture demo those surfaces point back to
  `Demo the ClankerOS local operator app with fixture-backed state`. Local
  proof includes the fixture-backed demo Home/Today/Workspace/Resume route
  pytest (`1 passed`) plus compile and whitespace checks.
- Workflow page parent Goal links now show the Goal title across the Operator
  Workbench, Scope Picker, Journey, Live State, Finish Today, and Command Bar,
  while preserving `*_goal_id`, `*_goal_label`, and `*_goal_label_source`
  evidence rows. The first-run completion target used by workflow scope
  selection now also points back to
  `Demo the ClankerOS local operator app with fixture-backed state` instead of
  raw `/goals/<goal_id>` copy. Local proof includes the fixture-backed demo
  workflow route pytest (`1 passed`) plus compile and whitespace checks.
- Coder-run `Run Readiness Strip` now includes a visible parent Goal card and
  title-first Goal evidence. In the fixture demo, the strip links back to
  `Demo the ClankerOS local operator app with fixture-backed state` instead of
  labeling the parent Goal link as raw `/goals/<goal_id>` route text. Local
  proof includes the fixture-backed demo run route pytest (`1 passed`) plus
  compile.
- Delegation-run continuation parent Goal links now show the Goal title
  instead of raw `/goals/<goal_id>` route text. In the fixture demo, the
  Delegation Run Continuation Goal card links back to
  `Demo the ClankerOS local operator app with fixture-backed state` while
  preserving the raw Goal id/source in evidence. Local proof includes the
  fixture-backed demo delegation/run route pytest (`1 passed`) plus compile.
- Run-level parent Goal links now show the Goal title instead of raw
  `/goals/<goal_id>` route text. In the fixture demo, the Run Operator
  Workbench and Run Continuation Strip use
  `Demo the ClankerOS local operator app with fixture-backed state` while
  preserving the raw Goal id/source in evidence. Local proof includes the
  fixture-backed demo run/Goal route pytest (`1 passed`) plus compile and
  whitespace checks.
- Project-level Goal entry cards now route to the concrete current Goal action
  when available. In the fixture demo, the Project Operator Workbench and
  Project Goal Map lead cards open
  `/goals/<goal_id>#goal-action-dock-form` as `Create commit request` instead
  of broad `Open lead goal` / `Open Goal` copy. Local proof includes the
  fixture-backed demo project/Goal route pytest (`1 passed`) plus compile and
  whitespace checks.
- Recent Items Command Bar Goal shortcuts now name the concrete Goal in the
  visible primary/card actions and collapsed evidence instead of generic
  `Open Goal` copy. The fixture demo now renders copy such as
  `Open Demo the ClankerOS local operator app with fixture-backed state` for
  the recent Goal return path. Local proof includes the fixture-backed demo
  Goal route pytest (`1 passed`) plus compile and whitespace checks.
- Command-palette Goal section shortcuts now include live Goal context instead
  of only repeating the Goal title. Key entries label the current action,
  waiting decision count, pending approvals, available artifacts, latest
  readable artifact, and remaining-work gate, for example
  `Goal Next action: Create commit request` and
  `Goal Artifact reader: Read coder run <run_id> review`. Local proof includes
  the fixture-backed demo Goal route pytest (`1 passed`) plus compile and
  whitespace checks.
- Saved exact Goal action routes now carry their concrete action label into
  the command palette Quick Switch workspace card, for example
  `Create commit request`, while project-only saved routes still say
  `Open saved project`. This fixes the GitHub fast-smoke demo regression from
  run `28493458234`; local proof includes the first-run/browser and
  fixture-backed demo route pytests (`1 passed` each).
- Confirmed `create-goal` now saves the first Goal's exact action-dock route
  as `resume_surface`, for example `/goals/<goal_id>#goal-action-dock-form`,
  instead of the broad Goal page. `/resume` uses that route as the primary
  hero, command, and workbench target with labels such as
  `Create scout delegation`, while saved-state evidence preserves the raw
  route. Local proof includes the first-run/browser route pytest (`1 passed`).
- Confirmed `save-goal-note` now saves the exact Goal operator-notes section
  as `resume_surface`, for example `/goals/<goal_id>#goal-operator-notes`,
  while keeping `operator-notes.md` as the last viewed artifact. `/resume`
  reads back that notes-section route after the local note append. Local proof
  includes the first-run/browser route pytest (`1 passed`).
- Confirmed `save-workspace` POST now promotes an omitted or broad saved Goal
  `resume_surface` to the exact current action route, for example
  `/goals/<goal_id>#goal-action-dock-form`, before writing
  `.clanker/app/workspace.json`. Home, `/workspace`, and `/resume` read back
  the same actionable route after operator save. Local proof includes the
  fixture-backed demo route pytest (`1 passed`).
- `/workspace` save defaults and restore guidance now use the Goal's exact
  current action route as `resume_surface`, for example
  `/goals/<goal_id>#goal-action-dock-form`, when suggesting a lead Goal or
  repairing an old broad `/goals/<goal_id>` saved route. The Restore Map labels
  that route with the current action, such as `Create commit request`. Local
  proof includes the fixture-backed demo Workspace route pytest (`1 passed`).
- Root `/` Home Resume Workspace `Remember Current Goal` now saves the lead
  Goal's exact current action route as `resume_surface`, for example
  `/goals/<goal_id>#goal-action-dock-form`, instead of the broad Goal page.
  Readback exposes `home_resume_remember_resume_surface` with labels such as
  `Create commit request`. Local proof includes the fixture-backed demo Home
  route pytest (`1 passed`).
- Root `/` Home Day Plan Finish Today now saves the current concrete Goal
  action route as `resume_surface`, for example
  `/goals/<goal_id>#goal-action-dock-form`, alongside the lead Goal, filters,
  panels, and latest artifact. Day Plan evidence exposes
  `home_day_plan_finish_resume_surface` and `day_plan_finish_resume` with
  labels such as `Create commit request`. Local proof includes the
  fixture-backed demo Home route pytest (`1 passed`).
- Root `/` Home Recent Activity now carries the latest Goal artifact into the
  Artifacts card even when newer run/approval events fill the recent timeline
  window. The card and `home_activity_artifact_surface` evidence route to the
  exact bounded `/artifacts?path=...` target with labels such as
  `Open coder run <run_id> review`, instead of falling back to `Search artifacts`
  or generic `Open artifact` copy. Local proof includes the fixture-backed demo
  Home route pytest (`1 passed`).
- `/goals/<goal_id>` scan-first history surfaces now name latest artifact
  actions in `Goal Activity Pulse` and `Goal Timeline Digest`, such as
  `Open coder run <run_id> review`, instead of `Open artifact` or
  `Latest artifact`. Collapsed evidence records the new artifact action label
  fields while preserving exact bounded artifact routes. Local proof includes
  the fixture-backed demo Goal route pytest (`1 passed`).
- `/goals/<goal_id>` command-palette Quick Switch and Goal Review Strip now
  name the exact artifact action, such as `Open coder run <run_id> review` and
  `Read coder run <run_id> review`, instead of generic artifact copy. A shared
  helper also falls back to a concrete filename for saved workspace artifact
  paths. Local proof includes the fixture-backed demo Goal route pytest
  (`1 passed`) plus compile and whitespace checks.
- `/skills` Skills Usage Map now names the selected skill in the `Now` card's
  primary action, such as `Open local-files skill`, instead of the generic
  `Open artifact` copy. Collapsed evidence records
  `skills_usage_map_primary_label` while preserving the exact artifact route.
  Local proof includes the fixture-backed demo skills route pytest
  (`1 passed`).
- Confirmed action-result command cards now name the concrete next workflow
  action instead of showing generic `Continue workflow` copy. First-run setup
  results link the Workflow card to `Create first goal`; saved-Goal
  commit-request results link it to `Approve commit`. Local proof includes
  the focused first-run, demo-scenario, and reviewed-commit pytest paths
  (`1 passed` each).
- `/goals/<goal_id>` Goal Task Closeout now routes blocked closeout states
  back to the concrete current Goal action. At the publication-request gate it
  links to `#goal-action-dock-form` as `Create publication request` instead of
  generic `Continue workflow` copy. Local proof includes the focused
  publication-gate pytest (`1 passed`).
- `/goals` lane cards now label their primary action with the concrete current
  Goal action, such as `Create commit request`, instead of generic
  `Use action form` copy. The href and confirmation-gated action form remain
  unchanged. Local proof includes the fixture-backed demo Goal route pytest
  (`1 passed`).
- `/ci-evidence` now has a visible `CI Evidence Readiness Strip` between the
  `CI Proof Workbench` and `CI JSON Assistant`. It summarizes current proof
  posture, latest local CI record, operator-supplied GitHub JSON, the
  confirmed local recorder, and the no-fetch/no-effect safety boundary before
  the denser proof and command evidence. Local proof includes focused route
  pytest (`1 passed`).
- `/health` now has a visible `Health Readiness Strip` between the
  `Health Operator Workbench` and `Health Command Bar`. It summarizes local
  bind scope, initialized storage, workflow import readiness, next local
  action, and the status-artifact-only safety boundary, with ready and
  nonlocal-warning states covered in focused route pytest. Local proof includes
  focused health route pytest (`1 passed`) and `compileall`.
- `/runs/<coder_run_id>` now places a visible `Run Readiness Strip` between
  the `Run Command Bar` and `Run Operator Workbench`. It summarizes run status,
  review gate, bounded evidence, next local action, current gate progress, and
  no-effect safety posture before the denser workbench and evidence sections.
  Local proof includes focused demo pytest (`1 passed`), compileall, and
  `git diff --check`.
- `/approvals` now opens from the operator workbench into a visible
  `Approval Readiness Strip` before the older command/filter inventory. The
  strip summarizes queue counts, the focused approval decision, scoped
  Goal/run/delegation context, evidence artifact routing, after-decision
  guidance, and explicit safety boundaries while linking only to existing
  confirmed approval forms. Local proof includes focused route/demo pytest
  (`2 passed, 515 deselected`), compileall, and `git diff --check`.
- `/search` now opens with visible `Search Suggestions` before the
  `Search Operator Workbench`. Populated local state produces quick searches
  for the current Goal, next action, projects, approvals, decisions, memory,
  skills, and artifacts; empty first-run state falls back to `/goals` and
  `/demo`. Local proof includes py-compile, focused route/demo pytest (`2
  passed, 515 deselected`), and the disposable-root app demo smoke test with
  all route markers matched and provider/network/external-mutation counters
  at `0`.
- `/memory` now lets the operator pin the next proposed memory directly from
  the top `Memory Operator Workbench`. When a proposed memory exists, the
  workbench renders a same-page `pin-memory` form before collapsed evidence;
  the write still goes through the existing confirmed POST action. Empty
  memory states render no top pin form. Local proof includes py-compile,
  focused route/demo pytest (`2 passed, 515 deselected`), and the
  disposable-root app demo smoke test with all route markers matched and
  provider/network/external-mutation counters at `0`.
- Goal Artifact Reader now opens with a visible selected-artifact focus strip
  for Selected, Type, Source, Open, and Safety. Its toolbar/focus/full-preview
  links now say concrete actions such as `Open coder run <run_id> review`
  instead of generic `Open full artifact`, while exact `/artifacts?path=...`
  surfaces remain in reader evidence. Local proof includes py-compile,
  diff-check, focused route/demo pytest (`2 passed, 515 deselected`), and the
  disposable-root app demo smoke test.
- Goal Next Action focus strips now label the source card as `Action source`
  and show a human link such as `Review run <run_id>` instead of a generic
  `Target` card with a raw route. Collapsed evidence preserves
  `next_action_focus_source_surface` for the exact route and adds
  `next_action_focus_source_label` /
  `next_action_focus_source_label_surface` for the operator-facing label.
  Local proof includes py-compile, diff-check, focused route/demo pytest
  (`2 passed, 515 deselected`), and the disposable-root app demo smoke test.
  Remote GitHub Actions proof for this slice should be read back after push.
- Today Activity Digest and Goal Session Digest latest-artifact cards now name
  the concrete artifact/event they open instead of generic latest-artifact
  copy, and the Coder Handoff Execute/Ship cards name the concrete selected
  run instead of generic latest-run copy. The demo Today surface now labels the
  latest artifact with concrete coder-run copy, such as `Artifact recorded:
  coder run <run_id> verification stderr.` or `Open coder run <run_id>
  review`, and the Goal Session Digest labels its latest artifact action as
  `Open coder run <run_id> review`, while preserving exact raw href evidence
  through `today_activity_digest_latest_artifact_raw_surface` and
  `goal_session_digest_latest_artifact_raw_surface`. Local proof includes
  py-compile, focused route/demo pytest (`2 passed, 515 deselected`), and
  temp-root `app-demo-smoke-test` with all demo route markers matched and
  provider/network/external-mutation counters at `0`. Remote GitHub Actions
  proof for this slice should be read back after push.
- Project Goal Map Work cards now label the exact workflow target when a coder
  run exists: `Open run <run_id> workflow` replaces generic `Open latest run
  workflow` copy on `/projects/<project_id>`. Collapsed evidence now records
  both `project_goal_map_workflow_label` and
  `project_goal_map_workflow_raw_surface`, preserving the exact
  `/workflow?run_id=<run_id>` href for review. Local proof includes
  py-compile, focused route/demo pytest (`2 passed, 515 deselected`), and
  temp-root `app-demo-smoke-test` with all demo route markers matched and
  provider/network/external-mutation counters at `0`. Remote GitHub Actions
  proof for this slice should be read back after push.
- Goal Evidence Command Bar and Goal Artifact Command Bar latest links now name
  the concrete artifact they open instead of generic `Open latest Goal
  artifact` / `Open latest artifact` copy. The demo Goal shows labels such as
  `Open coder run <run_id> verification stderr` and `Open coder run <run_id>
  review`, while preserving exact href evidence through
  `goal_evidence_command_latest_raw_surface`,
  `goal_evidence_command_latest_artifact_surface`,
  `goal_artifact_command_latest_raw_surface`, and
  `goal_artifact_command_latest_artifact_surface`. Local proof includes a
  `73Gi` free-space check, py-compile, diff check, focused route/demo pytest
  (`2 passed, 515 deselected`), and temp-root `app-demo-smoke-test` with all
  demo route markers matched and zero provider, network, or external mutation
  counters. The previous commit's GitHub Actions fast smoke is green; its full
  suite remains in progress, and remote proof for this slice should be read
  back after push.
- Goal Return Brief and Goal Session Digest latest links now use concrete
  event labels instead of generic `Open latest activity` copy or raw href text.
  The ready-to-commit demo Goal shows `Execution completed: <run_id>.` while
  preserving exact `/runs/<run_id>` evidence through
  `goal_return_latest_activity_raw_surface` and
  `goal_session_digest_latest_raw_surface`. Local proof includes a `72Gi`
  free-space check, py-compile, diff check, focused route/demo pytest (`2
  passed, 515 deselected`), and temp-root `app-demo-smoke-test` with all demo
  route markers matched and zero provider, network, or external mutation
  counters. The previous commit's GitHub Actions fast smoke is green; its full
  suite remains in progress, and remote proof for this slice should be read
  back after push.
- Home, Today, and Goal detail latest-action cards now use concrete labels
  instead of generic `Open latest` copy. Today Session Summary, Today Activity
  Digest, Home Activity Command Bar, Goal Review Strip, Goal Activity Pulse,
  and Goal Evidence Digest label links with the event or artifact they open
  while preserving exact raw href evidence rows. Local proof includes a `73Gi`
  free-space precheck, py-compile, diff check, focused route/demo pytest (`2
  passed, 515 deselected`), and temp-root `app-demo-smoke-test` with all demo
  route markers matched and zero provider, network, or external mutation
  counters. The previous commit's GitHub Actions fast smoke is green; its full
  suite remains in progress, and pushed Actions proof for this new slice is
  pending until commit/push.
- Goal timeline and Activity Log controls now label latest-event links with the
  actual event instead of generic `Open latest` / `Target` copy. The demo
  ready-to-commit Goal now surfaces `Execution completed: <run_id>.` in the
  Timeline Command Bar, Goal Timeline Digest, and Goal Activity Command Bar
  while preserving raw `/runs/<run_id>` evidence rows. Local proof includes a
  `74Gi` free-space precheck, py-compile, diff check, focused demo pytest,
  focused route/demo pytest, and temp-root app-smoke-test with all route
  markers matched and zero provider, network, or external mutation counters;
  pushed GitHub Actions and full-suite proof are still pending.
- Global Search now acts as a command surface for matched Goals. When a Goal
  result has a browser-confirmed current action form, the Search Operator
  Workbench, Search Result Map, Search Command Bar, and flat result row expose
  `/goals/<goal_id>#goal-action-dock-form` with the concrete action label such
  as `Create commit request`, while preserving the raw `/goals/<goal_id>` title
  link and source evidence. Local proof includes a `74Gi` free-space precheck,
  py-compile, diff check, focused demo pytest, focused route/demo pytest, and a
  temp-root app-smoke-test with all route markers matched and zero provider,
  network, or external mutation counters; pushed GitHub Actions and full-suite
  proof are still pending.
- Goal Continuation Rail and the full Goal Workflow Map now route the current
  actionable gate to the visible confirmed Goal Action Dock form when one
  exists. For the ready-to-commit demo Goal, the current `commit_request` gate
  links to `#goal-action-dock-form` as `Create commit request` instead of the
  older detailed `#goal-next-action` surface. Local proof includes
  py-compile, focused route/demo pytest, temp-root app-smoke-test, and in-app
  Browser desktop QA with clean logs, no horizontal overflow, continuation
  click-through to the `/actions/coder-commit-request` POST form, and DOM
  confirmation that both current lifecycle surfaces use the dock anchor.
  Mobile Browser proof and pushed GitHub Actions proof for this new slice are
  still pending.
- Goal Jump Bar shortcut `2` now names and opens the real current Goal action.
  For the ready-to-commit demo Goal it displays `Create commit request` and
  links to the existing confirmed `#goal-action-dock-form` instead of the
  generic `Action -> #goal-next-action` jump. Local proof includes
  py-compile, focused route/demo pytest, temp-root app-smoke-test, and in-app
  Browser desktop QA with clean logs, no horizontal overflow, and click plus
  keyboard shortcut navigation to the commit-request form. Mobile Browser
  proof is not claimed for this slice because the viewport check timed out
  twice and the reset attempt timed out; pushed GitHub Actions and full-suite
  proof are still pending.
- Goal Section Index now uses the actual current Goal action as its primary
  `Operate` card. For the ready-to-commit demo Goal it shows
  `Create commit request` and links to the existing confirmed
  `#goal-action-dock-form` instead of the generic deep `#goal-next-action`
  section, while preserving read-only/no-provider/no-network/no-external-
  effect evidence. Local proof includes py-compile, focused route/demo pytest,
  temp-root app-smoke-test, and in-app Browser QA on desktop 1280x720 plus
  mobile 390x844 with clean logs, no page overflow, primary-action evidence,
  single-column mobile switchboard cards, and click-through to the
  commit-request form; pushed GitHub Actions and full-suite proof are still
  pending for this slice.
- Goal detail pages now include a first-screen `Goal Control Strip` after the
  title and before the Path Rail/Review Strip. It gathers the current action,
  state, waiting attention, proof, notes, and finish-today return point into
  one operator band, while linking only to existing confirmation-gated browser
  surfaces such as `#goal-action-dock-form`, `/approvals?goal_id=...`,
  `#goal-ci-handoff`, `#goal-operator-note-form`, and `#goal-finish-today`.
  Local proof includes py-compile, diff check, focused route/demo pytest,
  temp-root app-smoke-test, and in-app Browser QA on desktop 1280x720 plus
  mobile 390x844 with first-viewport strip visibility, clean logs, no page
  overflow, single-column mobile cards, and click-through to commit-request,
  note, and finish forms; pushed GitHub Actions and full-suite proof are still
  pending for this slice.
- Goal detail pages now include a first-screen `Goal Path Rail` after the
  title and before the review strip. It reuses the existing workflow-gate
  summary to show the full local lifecycle as a compact horizontal rail,
  highlights the current `commit_request` gate, and links the current rail
  action to the existing confirmation-gated Goal action surface
  (`#goal-action-dock-form`) while non-current gates point to the lower
  Workflow Map. Local proof includes py-compile, diff check, focused
  route/demo pytest, temp-root app-smoke-test, and in-app Browser QA on
  desktop 1280x720 plus mobile 390x844 with first-viewport rail visibility,
  contained rail scrolling, clean logs, no page overflow, and current-action
  click-through; pushed GitHub Actions and full-suite proof are still pending
  for this slice.
- Goal detail pages now put a first-class `Goal Review Strip` directly in the
  Goal header path, immediately after the title and before summary cards,
  phase, Action Dock, and lower surfaces. It summarizes latest activity, local
  proof, latest artifact, risk/remaining work, and safety posture with links
  into existing timeline/evidence/artifact/approval surfaces and collapsed
  evidence rows preserving counts plus no-write/no-provider/no-network/
  no-external-effect counters. Local proof includes py-compile, diff check,
  focused route/demo pytest, temp-root app-smoke-test, and in-app Browser QA
  on desktop 1280x720 plus mobile 390x844 with clean logs, no overflow, first-
  viewport visibility, and artifact-reader click-through; pushed GitHub
  Actions and full-suite proof are still pending for this slice.
- Goal summary is now action-first on Goal detail pages. A first `Next` card
  appears before Project/Status/Phase/Live and links to the existing
  confirmation-gated Goal Action Dock surface, such as
  `#goal-action-dock-form` labeled `Create commit request`, while evidence
  preserves the next action, chosen summary surface, source surface, form
  availability, confirmation requirement, and no-effect counters. Local proof
  includes py-compile, diff check, focused route/demo pytest, temp-root
  app-smoke-test, and in-app Browser QA on desktop 1280x720 plus mobile
  390x844 with clean logs, no overflow, and click-through to the visible
  confirmation form; pushed GitHub Actions and full-suite proof are still
  pending for this slice.
- Goal detail pages now have a mobile compact chrome mode. At 640px and
  below, Goal detail pages keep the header/nav/action rows to one scrollable
  line and compact the operator ribbon to the first-screen `Now` and `Finish`
  cards while preserving full desktop ribbon behavior, evidence rows, and the
  existing confirmation-gated action form. In-app Browser QA verified desktop
  all-card behavior plus mobile 390x844 no-overflow behavior and click-through
  from the compact `Create commit request` card to
  `#goal-action-dock-form`; pushed GitHub Actions and full-suite proof are
  still pending for this slice.
- Goal detail pages now use Goal-first shell ordering: the main Goal cockpit
  renders before Recent Items, the Workspace Panel Restore strip moves after
  Goal content, and the Goal Action Dock sits before the jump bar. Summary and
  Current Phase surfaces are compact scan-first cards with collapsed exact
  evidence blocks that preserve no-write/no-external-effect rows. Local proof
  includes py-compile, diff check, focused route/demo pytest, and in-app
  Browser QA on desktop 1280x720 plus mobile 390x844; pushed GitHub Actions
  and full-suite proof are still pending for this slice.
- The first-screen `/today` Resume affordance now uses the exact saved
  `resume_surface` when one exists. A saved `/today#today-current-action`
  route appears in both the shared operator ribbon and Today Command Center as
  `Open Today current action`, while `/resume` remains available as the
  broader hub through explicit `*_resume_hub_surface` evidence rows and
  `*_resume_surface_source` records whether the visible card came from
  `saved_resume_surface` or the `resume_page` fallback.
- The `/today` Session Summary Resume card now honors an explicit saved
  `resume_surface` before falling back to the workspace readiness target. A
  saved `/today#today-current-action` route displays as
  `Open Today current action` inside the daily return-to-work summary, with
  `today_session_resume_surface_source` naming whether the card came from
  `saved_resume_surface` or the readiness fallback and
  `today_session_resume_surface` preserving the exact raw href.
- Saved Today section anchors now get human return labels across the resume
  surfaces. A saved `/today#today-current-action` route displays as
  `Open Today current action` in `/resume`, `/workspace`, Recent Items, Quick
  Switch, and the action resume receipt while preserving the exact href in
  evidence and keeping all writes behind the existing confirmed
  `save-workspace` boundary.
- Today `Finish Today` now saves the exact daily action resume surface,
  `/today#today-current-action`, when the current Today action form exists.
  The form and command evidence expose the chosen `resume_surface` and reason,
  the confirmed `save-workspace` action writes that exact surface to
  `.clanker/app/workspace.json`, and `/resume` reads it back while preserving
  the confirmation-gated local-write boundary and zero provider/network/
  external-effect posture.
- `/today` now opens the daily cockpit with a first-screen `Today Session Rail`
  inside the Today Command Center. It shows the current action, attention
  count, CI proof state, and Finish Today target in one compact strip before
  the larger command grid. The rail reuses the existing confirmed local action
  form, approval/inbox routes, verification/CI evidence routes, and
  `#today-finish` save form, while first-run state routes the finish slot back
  to the current setup action instead of a disabled save target. GET remains
  read-only with no provider calls, non-loopback network actions, or external
  mutations.
- The shared header `n` / next-action shortcut now opens the Goal Action Dock
  when the current Goal action has a confirmed browser form. On the Goal page
  it uses `#goal-action-dock-form`; from other routes it opens
  `/goals/<goal_id>#goal-action-dock-form`, while preserving the same
  confirmation-gated form, no-write GET posture, and zero provider/network/
  external-effect boundaries.
- Browser-local Focus mode now keeps the shared `Operator Focus` strip visible
  while hiding surrounding chrome. The shell records
  `data-focus-mode-keeps-current-action="true"` so the `n` shortcut and
  `#operator-focus-current-action` remain reachable in Focus mode, while the
  same localStorage-only, no-write GET, confirmation-gated action posture is
  preserved.
- Goal `Finish Today` saves now preserve an exact next-morning surface:
  `/goals/<goal_id>#goal-action-dock-form` when the current action form exists,
  otherwise `/goals/<goal_id>#goal-next-action`. The Goal Daily Loop and Goal
  Resume Snapshot expose the target in evidence/hidden save fields while
  keeping action-result `return_to` on the broad Goal page.
- The in-app Suggested Use Guide now names the current first-run action in its
  primary browser path. The Guide Command Panel, Operator Recipes primary card,
  recipe evidence, and form-surface evidence say `Register ClankerOS project`
  instead of `Use command form` or `Guide command form`, while preserving the
  same `#guide-command-panel` anchor, confirmed `register-project` form, and
  zero-effect GET posture.
- Workflow, Approval, Inbox, Delegation Run Continuation, and Run workbench
  surfaces now label the primary same-page action form with the actual next
  operator move. Links and evidence rows say `Request commit for reviewed run`,
  `Approve worktree`, `Approve commit`, `Approve publication`,
  `Prepare coder packet`, or `Create commit request` instead of generic
  `* Workbench Action Form` copy, while preserving the same local anchors,
  confirmation-gated forms, and zero-effect GET posture.
- Saved workspace return labels now name the actual destination instead of
  saying `Open saved surface`. Resume and Workspace saved Goal return points
  say `Open saved Goal: <Goal title>`, saved projects say
  `Open saved project: <project>`, and Workflow finish points say
  `Open workflow`, while preserving the same saved `resume_surface` hrefs,
  confirmation-gated `save-workspace` flow, collapsed exact-route evidence,
  and zero-effect GET posture.
- Shared Recent Items and Quick Switch launchers now name the destination or
  action directly. Primary recent shortcuts say `Open Goal`, `Open run`,
  `Open delegation`, or `Open Goal cockpit` instead of `Open recent item`;
  saved workspace links say `Open saved project`, `Open saved Goal`, or
  `Open saved run` instead of `Open saved surface`; and saved last-action
  links reuse product action titles such as `First project setup`, while
  preserving the same local hrefs, browser-local filtering, command-palette
  surfaces, and zero-effect GET posture.
- Resume, Workspace, and Home saved-action surfaces now name the concrete
  operator move instead of exposing form mechanics. Primary workbench links,
  top action headings, deep evidence links, and Home live-state resume targets
  say actions such as `Create commit request` or `Create scout delegation`
  rather than `Use resume action form`, `Use workspace action form`,
  `Resume Action Form`, `Workspace Action Form`, or
  `Home Resume Action Form`, while preserving the same local anchors,
  confirmation-gated action routes, and zero-effect GET posture.
- Post-Goal first-run state now names the actual operator move,
  `Create scout delegation`, instead of the route-oriented
  `Open goal to create scout delegation`. The guide, command bar, next-step
  card, action ladder, header next-action, and Goal first-run rail now agree
  while preserving the same `#first-run-command-action` anchor,
  `/actions/delegate` confirmation route, and zero-effect GET posture.
- First-run action surfaces now label the current browser move directly instead
  of saying `Run First-Run Action`. After first Goal creation, the guide,
  next-step card, action ladder, header next-action, and inline expander say
  `Create scout delegation`; the following gates say `Generate context pack`
  and `Run delegation` while preserving the same local anchors,
  confirmation-gated forms, and zero-effect GET posture.
- Goal continuation rails and workflow maps now label same-page Goal action
  surfaces with the concrete gate action instead of `Goal action form`.
  Current and follow-on map links still use the same local
  `#goal-next-action` anchors and confirmation-gated forms, but visible labels
  now say moves such as `Create commit request`, `Commit approved worktree`,
  and `Create publication request`.
- Action-result workflow maps now label the current continuation surface with
  the concrete operator move instead of `Action continuation form`. First-run
  maps say `Create first goal`, saved Goal maps say the refreshed next action
  such as `Approve commit`, and the same local anchors, confirmation-gated
  forms, raw evidence, and zero-effect GET posture are preserved.
- Remaining continuation/action-source labels on Goal and action-result
  surfaces now use concrete operator language. Goal Next Action primary links
  say the actual move, such as `Create commit request`, action result
  continuation pages promote `Create first goal` or `Approve commit`, and the
  Goal Operator Workbench now says `Review action source` / `Save return
  point` instead of exposing form/source mechanics. The same local anchors,
  confirmation-gated action routes, and zero-effect GET posture are preserved.
- Inline current-action form surfaces on Today, Goal, and Operator Focus now
  use the exact operator move, such as `Create commit request`, instead of
  generic form labels like `Run Current Action`, `Today Current Action`, or
  `Current Action Form`. The links still point at the same local inline forms
  and confirmation-gated action routes, but the visible UI now tells the
  operator what they are about to do. The Today workbench grid also collapses
  to one column on 390px mobile viewports, removing the horizontal overflow
  caused by the desktop four-column workbench layout.
- The shared app header now keeps daily navigation compact by showing
  Dashboard, Today, Guide, Resume, Goals, Search, and Workspace as primary
  links, while advanced routes live under a `More` disclosure and remain
  available through the command palette. `More` opens automatically for
  secondary routes so advanced pages keep active nav context, while Goal and
  Today pages keep the first viewport focused on the cockpit. The closed
  `More` menu takes zero layout height on mobile, avoiding a blank spacer
  before the operator ribbon.
- The shared header `n` / next-action control now displays the concrete
  operator move, such as `Create Project` or `Create commit request`, rather
  than the generic `Next` label. Command palette Focus and Quick Switch action
  cards also use the exact current action text instead of generic `Run current
  action` / `Open action source` copy, while preserving the same local anchors,
  raw action metadata, confirmation-gated form routes, and zero-effect GET
  posture.
- Current-action CTAs now use the exact operator verb on Goal, Home, Action
  Notice, and delegation-run continuation surfaces instead of generic labels
  such as "Use current action" or "Continue Here." Primary links now say
  `Create commit request`, `Approve commit`, or `Prepare coder packet` while
  retaining the same raw action ids, evidence rows, DOM metadata, and
  confirmation-gated form routes underneath.
- Daily workflow browser forms now use operator-language copy instead of raw
  action ids for coder prep, worktree planning/approval, commit
  request/approval/local commit, and publication request/approval/handoff.
  Buttons and confirmation/result pages say things like `Prepare coder
  packet`, `Confirm commit request`, `Create local commit`, and `Prepare
  publication handoff`, while raw ids such as `coder-prep-from-handoff` and
  `approve-coder-commit` remain available in action URLs, DOM metadata,
  workspace state, and evidence fields.
- `/runs/<delegation_execution_run_id>` now promotes the current form-backed
  delegation continuation action into an inline
  `#delegation-run-continuation-action-form` inside the `Delegation Run
  Continuation` strip. `prepare_coder_from_handoff` preserves the
  implementation handoff path, delegation id, run id, project, Goal,
  `return_to`, and `resume_surface` fields on the run page, posts through the
  existing `/actions/coder-prep-from-handoff` confirmation route, and keeps
  `/delegations/<id>#safe-local-actions` as source/fallback evidence. GET
  remains read-only with no provider, non-loopback network, push, PR, deploy,
  or external mutation.
- `/runs/<coder_run_id>` now promotes the current safe local run action into
  an inline `#run-workbench-action-form` inside the `Run Operator Workbench`.
  Commit request, local commit, publication request, and publication handoff
  gates reuse the existing `/actions/<action>` confirmation routes; the
  workbench primary target points at the inline form while preserving the
  original gate surface in evidence. GET remains read-only with no provider,
  non-loopback network, push, PR, deploy, or external mutation.
- `/inbox` now promotes the first approval-backed coder worktree, commit, or
  publication decision into an inline `#inbox-workbench-action-form` inside the
  `Inbox Operator Workbench`. `/inbox` keeps global queue priority, while
  `/inbox?run_id=<coder_run_id>` scopes the top workbench queue to a run so
  commit and publication approvals can be handled without unrelated global
  approvals masking them. The forms still post through the existing
  `/actions/<action>` confirmation screen and keep GET read-only with no
  provider, non-loopback network, push, PR, deploy, or external mutation.
- `/today` now makes the daily cockpit directly actionable when the lead Goal's
  next action has a confirmed browser form. The command center renders the
  form visibly as `#today-current-action` before command evidence, while note,
  pause, and Finish Today forms remain collapsed and all writes still require
  the existing confirmation route.
- `/resume` now turns the `Resume Operator Workbench` into the actionable
  return surface. Saved Goal current-action forms and first-run setup forms
  render as a top `#resume-workbench-action-form` before workbench evidence,
  while the deeper Resume Next Action or First-Run Action section remains as
  detailed source/fallback readback and all writes stay behind confirmation.
- Completed-action notice pages now become direct continuation surfaces for
  saved Goal work. When the refreshed saved or lead Goal has a confirmed next
  action form, `Action Notice` renders an inline `Action Notice Next Step`
  section and points the primary Next Step card at
  `#action-notice-next-step-form`, while preserving the original Goal/workflow
  source surface in evidence and keeping all writes behind confirmation.
- Confirmed local action result pages now include a top `Action Result Next
  Step` panel between the action command bar and the resume/details readback.
  It uses refreshed first-run or saved-Goal state to promote the next operator
  move, renders the next confirmed browser form inline when available, and
  keeps writes/local execution behind the existing confirmation screen.
- Goal Action Dock now renders a top-of-page `Current Action Form` whenever
  the current Goal next action already has a confirmed browser form. The lower
  Next Action section remains as detailed readback/fallback, but operators can
  use the current action without scrolling through the long Goal page; writes
  and local execution still go through the same confirmation route.
- First-run scout workflow actions now use product copy instead of raw action
  ids after Goal creation: `delegate` renders `Create scout delegation` /
  `Confirm scout delegation` / `Scout delegation created`, `context-pack`
  renders `Generate context pack` / `Confirm context pack` /
  `Context pack ready`, and `run-delegation` renders `Run scout delegation` /
  `Confirm scout run` / `Scout run finished`, while raw action ids remain in
  evidence fields.
- First-run confirmation and result pages now continue the human setup
  language after form submission: `register-project` renders `Confirm project
  setup` / `Project setup complete`, `create-goal` renders `Confirm Goal
  setup` / `Goal setup complete`, and both keep raw action ids in evidence
  fields for auditability. Focused pytest routes, `app-smoke-test`, and
  browser QA on desktop plus 390x844 mobile passed locally; the full suite is
  left to GitHub Actions.
- First-run action forms now read like product surfaces instead of raw action
  payloads: `register-project` and `create-goal` forms include a short action
  brief, human field labels, field help, confirmation/external-effect notes,
  and outcome-named buttons such as `Create project` and `Create Goal`, while
  preserving the existing confirmed-local-action flow, browser-local drafts,
  and zero provider/network/external-effect posture.
- `/demo#demo-fixture-action` now lets the operator create or refresh the
  deterministic local demo fixture from the browser through the existing
  confirmation flow. It records the action in the safe action catalog, sets
  `/demo` as the next surface, points dogfooding at the exact fixture form,
  keeps CLI commands as fallbacks, and preserves no provider call, no
  non-loopback network action, no push, no PR, no deploy, and no external
  mutation.
- The local app now has a first-class `/guide` route in the main navigation.
  `Suggested Use Guide` maps the daily browser loop
  `Today -> Goal -> Action -> Proof -> Finish -> Resume`, points empty
  checkouts to the first-run browser path, points active work to the current
  Goal action form, and now opens with a `Guide Command Panel` that embeds the
  existing confirmed first-run or current Goal action form when available. It
  now follows with a read-only `Operator Recipes` panel for Start The Day, Set
  Up Or Select Goal, Do The Next Thing, Unblock Work, Check Proof, Finish
  Today, and Resume Tomorrow, each routed to existing browser surfaces. It
  shows evidence for route state, counts, workspace resume state, confirmation
  requirements, recipe routing, and zero-effect safety on GET.
- The First Run Guide now includes a visible `First Run Empty State Map`:
  a text-only `Project -> Goal -> Delegation -> Context -> Run` illustration
  plus step cards between Next Step and Checklist, keeping empty checkouts
  scan-friendly with no state write, provider call, network action,
  approval/execution/push/PR/deploy, or external effect on GET.
- The First Run Guide now includes a visible `First Run Action Ladder` between
  Next Step and the empty-state map. It highlights the current Project, Goal,
  Delegation, Context, or Run card, exposes the exact browser target and action
  name, and preserves no-write/provider/network/external-effect counters on
  GET while reusing existing confirmed forms.
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
- `/goals/<goal_id>#goal-artifact-reader` now adds a browser-local Goal
  Artifact Reader after the Goal Artifact Filter. It previews one
  already-registered artifact inline with the bounded inert Markdown, JSON,
  Patch/Diff, Text, and Log renderers, remembers the selected artifact per Goal
  in `localStorage:clankeros-goal-artifact-reader:<goal_id>`, and provides
  Reset reader while preserving read-only GET behavior and
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
- Confirmed local action result pages now include a `Resume Tomorrow` receipt
  immediately after `Action Complete`, so operators can see the saved
  `.clanker/app/workspace.json` resume route, project/Goal, artifact, last
  action/result, updater, readiness, and zero-effect boundary before dense
  payload details. The older `Action Resume Receipt` label remains as the
  evidence contract for review and automation.
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
  and Last Action strips while keeping Operator Focus/current action visible,
  keep the Operator Ribbon plus page body visible, and expose
  no-write/no-provider/no-network/no-external-effect evidence in the DOM.
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
  evidence inventory. Its top `Run Operator Workbench` also renders the
  current confirmed run action inline at `#run-workbench-action-form` when the
  gate is ready, while retaining the original gate surface as source evidence.
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
  Safety, then a visible `Health Readiness Strip` for Local Bind, Storage,
  Workflow, Next Action, and Safety before command evidence or dense health
  readbacks. Health workbench, readiness, command, diagnostics, counts,
  key-command, and workflow-import evidence stay collapsed by default while
  preserving the refreshed local status artifact, explicit status-artifact
  write-on-GET boundary, warning routing, and zero-effect counters in the DOM.
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
  and Manual Record, followed by a visible `CI Evidence Readiness Strip` for
  current proof posture, latest record, GitHub JSON, recorder, and safety
  before shared diagnostics, summary rows, or command evidence. CI evidence
  summary, proof workbench evidence, readiness evidence, and command evidence
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
  visible Now, State, Queue, and Resume cards, renders
  `#workflow-workbench-action-form` with the confirmed
  `coder-commit-request` form when the selected reviewed run is ready for a
  local commit request, keeps the source `/runs/<id>` surface in evidence, then
  follows with a visible
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
- Goal Action Dock now renders a top-of-page `Current Action Form` when the
  confirmed browser action form exists, and the shared operator ribbon routes
  form-backed Goal actions to that dock form instead of the deeper
  `#goal-next-action-form` fallback.
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
