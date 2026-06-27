# Status Entry Point

The canonical chronological implementation log is [`../status.md`](../status.md).

Latest status focus:

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
  showing project-scoped GitHub Actions proof posture, exact `gh run list` /
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
