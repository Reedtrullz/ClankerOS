# Tutorial: Run An Approval-Gated Coding Task

This tutorial walks through the first executable local coding-agent vertical:

1. register a local git repository;
2. run a constrained coding command in an isolated git worktree;
3. capture diff, command, and test evidence;
4. inspect the proposed `local_git_commit` effect;
5. make an operator approval decision;
6. create the approved local worktree commit exactly once;
7. prepare a GitHub handoff packet from committed local evidence;
8. clean up terminal worktrees after an explicit cleanup decision.

The flow is intentionally conservative. It creates evidence and an approval
packet first. It creates a local git commit only after explicit approval and a
fresh evidence recheck. It can prepare operator commands for push and draft PR
handoff after the commit exists. It does not push, open a PR, deploy, or mutate
external systems.

## Prerequisites

- Python 3.10 or newer.
- `git`.
- A local git repository with at least one commit.
- A deterministic test command for that repository.

## 1. Initialize ClankerOS State

Run this from the ClankerOS repository root:

```bash
python3 -m agent_os.cli init
```

This prepares `.agent/state.db` and the local runtime files.

## 2. Register A Target Repository

Replace `/path/to/repo` and the test command with values for your project:

```bash
python3 -m agent_os.cli register-project my-repo \
  --path /path/to/repo \
  --test-command "python3 -m pytest -q"
```

Registration records:

- the resolved git root;
- the default verification command;
- allowed write roots, defaulting to the repository root;
- a project note under `projects/my-repo/project.md`.

Registration does not create a worktree, run commands, or change the target
repository.

## 3. Run A Worktree-Isolated Coding Goal

Use `run-goal` with `--isolation worktree` and a narrow local command:

```bash
python3 -m agent_os.cli run-goal \
  "Make a tiny verified local change" \
  --project my-repo \
  --isolation worktree \
  --command "python3 -c \"from pathlib import Path; Path('agent-output.txt').write_text('hello\\n')\""
```

ClankerOS will:

- create a new git worktree under `.agent/worktrees/my-repo/<run_id>`;
- run the command in that worktree;
- collect stdout, stderr, git status, patch diff, and changed files;
- run the registered test command in the worktree;
- write `verification.json`, `effect.json`, `approval.md`, and `summary.md`;
- create a pending approval request;
- record a proposed `local_git_commit` effect.

The original repository checkout is not edited by this command.

## 4. Inspect Evidence

Regenerate the dashboard:

```bash
python3 -m agent_os.cli dashboard
```

Open `docs/dashboard.md` and start with `## Operator Cockpit`.

For a proposed coding effect, inspect the run evidence under:

```text
runs/<run_id>/evidence/
```

Important files:

- `summary.md`: compact operator summary and non-claims.
- `worktree.json`: worktree id, branch, path, and base commit.
- `commands.jsonl`: command and test execution metadata.
- `command-stdout.txt` and `command-stderr.txt`: coding command output.
- `git_status.txt`: short git status from the worktree.
- `diff.patch`: exact proposed diff.
- `diff_summary.md`: changed-file summary.
- `tests.txt`: test command, exit code, stdout, and stderr.
- `verification.json`: policy, command, test, and diff verification status.
- `effect.json`: proposed effect payload.
- `approval.md`: approval packet for the operator.

## 5. Review And Decide

List pending approvals:

```bash
python3 -m agent_os.cli approvals
```

If the evidence is acceptable, record the approval:

```bash
python3 -m agent_os.cli approve <approval_id> \
  --decided-by operator \
  --note "reviewed diff and tests"
```

Approval records the operator decision. It does not create the commit by
itself.

## 6. Commit The Approved Effect

After approval, create the local worktree commit:

```bash
python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator
```

Before committing, ClankerOS re-checks:

- the approval exists and is approved;
- the effect is a `local_git_commit` still awaiting application;
- the worktree `HEAD` still matches the captured base commit;
- the current changed files and patch still match `diff.patch`;
- the stored test command still passes.

If any freshness check fails, the effect is blocked and no commit is created.
If the command is repeated after a successful commit, ClankerOS returns the
stored commit SHA instead of creating another commit.

The command writes `commit-approved.json` beside the original run evidence and
updates the effect with `status=committed`, `committed_at`, `result_json`, and
a local `git revert <commit_sha>` compensation note.

## 7. Prepare A GitHub Handoff

After a committed effect exists, create a local handoff packet:

```bash
python3 -m agent_os.cli github-handoff <effect_id> \
  --remote origin \
  --base main \
  --title "Make a tiny verified local change"
```

ClankerOS will:

- require a committed `local_git_commit` effect;
- confirm the recorded commit object exists in the registered project;
- read the configured remote URL;
- write `github-handoff-<effect_id>.json`;
- write a draft PR body beside the run evidence;
- print exact operator commands for `git push` and `gh pr create --draft`;
- record `network_actions_taken=0`.

This step does not push the branch or open a pull request. The operator can run
the printed commands later after reviewing the local evidence.

## 8. Clean Up Terminal Worktrees

Preview cleanup candidates:

```bash
python3 -m agent_os.cli cleanup-worktrees
```

After reviewing the terminal effects and evidence, confirm cleanup:

```bash
python3 -m agent_os.cli cleanup-worktrees \
  --confirm \
  --decided-by operator \
  --reason "committed branch kept, worktree no longer needed"
```

Cleanup writes a `worktree-cleanup-<effect_id>.json` evidence file and a
SQLite `worktree_cleanup_records` row. It removes clean worktrees for terminal
`local_git_commit` effects such as `committed`, `blocked`, or `superseded`.
Dirty worktrees are blocked and left in place; ClankerOS does not force-delete
uncommitted changes.

## What This Tutorial Does Not Do

- It does not commit before explicit approval.
- It does not commit if the worktree no longer matches the captured evidence.
- It does not force-delete dirty worktrees during cleanup.
- It does not push a branch, even when it prints a push command.
- It does not open a pull request, even when it prints a draft PR command.
- It does not run GitHub Actions.
- It does not deploy anything.
- It does not enable hosted dashboards, remote workers, scheduling, browser or
  desktop adapters, budget enforcement, trust promotion, retries, or real cost
  tracking.

Those steps need their own approval-gated implementation and verification.
