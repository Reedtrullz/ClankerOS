# Tutorial: Run An Approval-Gated Coding Task

This tutorial walks through the first executable local coding-agent vertical:

1. register a local git repository;
2. run a constrained coding command in an isolated git worktree;
3. capture diff, command, and test evidence;
4. inspect the proposed `local_git_commit` effect;
5. make an operator approval decision;
6. create the approved local worktree commit exactly once;
7. prepare a GitHub handoff packet from committed local evidence;
8. record operator-supplied CI/deploy evidence for the handoff;
9. record profile routing decisions for future specialist work;
10. record read-only subagent delegation contracts;
11. ingest structured read-only delegation results;
12. clean up terminal worktrees after an explicit cleanup decision.

The flow is intentionally conservative. It creates evidence and an approval
packet first. It creates a local git commit only after explicit approval and a
fresh evidence recheck. It can prepare operator commands for push and draft PR
handoff after the commit exists and later record operator-supplied CI/deploy
evidence. It does not push, open a PR, run CI, deploy, or mutate external
systems.

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

## 8. Record CI/Deploy Evidence

After an operator has real CI or deploy evidence for the handoff, record it
locally:

```bash
python3 -m agent_os.cli ci-deploy-evidence <github_handoff_id> \
  --provider github-actions \
  --status success \
  --external-run-id 123 \
  --url https://github.com/owner/repo/actions/runs/123 \
  --recorded-by operator \
  --note "GitHub Actions run was green."
```

ClankerOS will:

- require a GitHub handoff packet;
- copy branch, commit, effect, run, task, and project metadata from the handoff;
- write `ci-deploy-evidence-<handoff_id>-<provider>-<run_id>.json`;
- store a `ci_deploy_evidence_records` row;
- record `network_actions_taken=0`.

This step does not fetch the URL, call GitHub Actions, run CI, deploy, or
mutate an external system. It records operator-supplied proof so the local
control plane can preserve the evidence trail.

## 9. Record Profile Routing Decisions

Create the default local profile config and record a routing decision:

```bash
python3 -m agent_os.cli profiles
python3 -m agent_os.cli profile-show scout
python3 -m agent_os.cli route <task_id>
python3 -m agent_os.cli route --category repo_search --project my-repo
python3 -m agent_os.cli route <task_id> --profile evaluator
```

ClankerOS stores planner, coder, scout, tester, and evaluator profiles in
SQLite and writes `.clanker/profiles.yml` if no local config exists. Route
decisions preserve the selected profile, model label, category, cost tier,
task/goal/project context, and operator override reason when present.

This is a control-plane record only. It does not claim tasks, start subagents,
call model providers, or change approval gates.

## 10. Record Delegation Contracts

After routing a task, record a read-only specialist delegation contract:

```bash
python3 -m agent_os.cli delegate <task_id> \
  --profile scout \
  --title "Find relevant CLI files and tests"

python3 -m agent_os.cli delegations <goal_id>
python3 -m agent_os.cli delegation-result <delegation_id>
```

ClankerOS will:

- record or consume a routing decision for the task;
- require the selected profile to be a read-only subagent profile;
- store scoped prompt/context/tool/budget fields in SQLite;
- write a JSON artifact under `.clanker/delegations/`;
- keep the delegation `pending`.

This step does not start a subagent, call a model provider, write files,
approve work, commit, or mutate external state.

## 11. Record Delegation Results

When read-only specialist output exists, attach it to the delegation:

```bash
python3 -m agent_os.cli record-delegation-result <delegation_id> \
  --summary "Relevant files identified." \
  --output-json '{"files":["agent_os/cli.py","tests/test_first_milestone.py"]}' \
  --recorded-by operator
```

ClankerOS will:

- validate the payload against the delegation's expected schema family;
- mark the delegation `completed`;
- write `.clanker/delegations/<delegation_id>-result.json`;
- keep `network_actions_taken=0` and external mutation non-claims explicit.

Repeating the same result is idempotent. A different result for a completed
delegation is rejected.

This step does not start a subagent, call a model provider, approve work,
commit, push, run CI, deploy, or mutate external state.

## 12. Clean Up Terminal Worktrees

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
- It does not run GitHub Actions, even when it records a GitHub Actions URL.
- It does not deploy anything, even when it records deploy evidence.
- It does not dispatch subagents or call model providers when it records
  profile routing decisions.
- It does not start subagents or call model providers when it records
  delegation contracts.
- It does not enable hosted dashboards, remote workers, scheduling, browser or
  desktop adapters, budget enforcement, trust promotion, retries, or real cost
  tracking.

Those steps need their own approval-gated implementation and verification.
