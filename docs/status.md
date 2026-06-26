# Status Entry Point

The canonical chronological implementation log is [`../status.md`](../status.md).

Latest status focus:

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
  commit. Prefer `ci-snapshot-evidence-from-gh-json` after GitHub completes so
  ClankerOS validates the supplied run JSON before recording direct snapshot
  CI proof.
