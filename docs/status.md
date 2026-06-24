# Status Entry Point

The canonical chronological implementation log is [`../status.md`](../status.md).

Latest status focus:

- Coder commit promotion is the primary post-review gate after bounded coder
  worktree execution.
- Modern operator flow:
  `coder-commit-request -> approve-coder-commit -> commit-coder-worktree ->
  github-handoff`.
- Commit request and approval do not stage files or create commits.
- `commit-coder-worktree` creates one local commit only inside the isolated
  `.agent/worktrees/...` worktree, stages only approved files, and does not
  push, create PRs, deploy, call providers, or intentionally use the network.
