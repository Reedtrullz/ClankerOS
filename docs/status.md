# Status Entry Point

The canonical chronological implementation log is [`../status.md`](../status.md).

Latest status focus:

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
- Current verification: `python3 -m pytest tests/test_first_milestone.py -q`,
  `python3 -m pytest -q`, and `git diff --check` pass for the publication
  boundary update.
