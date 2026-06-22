# Suggested Use

ClankerOS works best as a local operating loop for agentic work, not as a
black-box autonomous runner. Use it to make work visible, verifiable, and
harder to overclaim.

## Good Starting Prompts

Use prompts that name a concrete local outcome:

```text
Create a local proof packet for enabling a hosted dashboard, but do not deploy it.
```

```text
Review the current expansion evidence and add the next report-only approval boundary.
```

```text
Run the first local loop, regenerate the dashboard, and summarize what is proven and not proven.
```

```text
Register this git repo, run a worktree-isolated coding task, capture the diff and tests, then ask me before creating the local worktree commit.
```

```text
List the safe default profiles and record a scout routing decision for repo search without dispatching a model.
```

```text
Record a read-only scout delegation contract for this task and show me the delegation artifact, but do not start a subagent.
```

```text
Attach this read-only delegation output to the existing contract, validate the schema, and keep the no-provider/non-network claims explicit.
```

## Recommended Operating Loop

1. Pick one narrow capability or boundary.
2. Write or update a red-first regression when behavior changes.
3. Add the smallest implementation that creates durable local evidence.
4. Regenerate the relevant report and `docs/dashboard.md`.
5. Run `python3 -m pytest -q`.
6. Run `python3 -m agent_os.cli eval`.
7. Record specialist delegation results when read-only context is useful.
8. Record non-claims before treating the work as safe.

## Approval-Gated Coding Loop

Use this loop when the desired outcome is an actual local code change:

1. Register the target repository with its default test command:

```bash
python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "python3 -m pytest -q"
```

2. Run the change in an isolated worktree:

```bash
python3 -m agent_os.cli run-goal "Make the smallest verified change" --project <name> --isolation worktree --command "<safe local command>"
```

3. Inspect `docs/dashboard.md`, especially `## Operator Cockpit`.
4. Read `runs/<run_id>/evidence/diff.patch`, `tests.txt`,
   `verification.json`, `effect.json`, and `approval.md`.
5. Use `python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "..."`
   only after the diff, tests, and policy evidence are acceptable.
6. Use `python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator`
   to re-check evidence and create the local worktree commit exactly once.
7. Use `python3 -m agent_os.cli github-handoff <effect_id> --base main --title "..."`
   when you want a local push/draft-PR packet after commit evidence exists.
8. Use `python3 -m agent_os.cli ci-deploy-evidence <github_handoff_id> --provider github-actions --status success --external-run-id <run_id> --url <run_url>`
   after real CI/deploy evidence exists and should be preserved locally.
9. Use `python3 -m agent_os.cli profiles`, `profile-show <name>`, and
   `route ...` to record profile routing choices before specialist work.
10. Use `python3 -m agent_os.cli delegate <task_id> --profile scout --title "..."`
   to create a read-only delegation contract when specialist prep is useful.
11. Use `python3 -m agent_os.cli record-delegation-result <delegation_id> --summary "..." --output-json '{...}'`
   to attach structured read-only output to an existing delegation.
12. Use `python3 -m agent_os.cli cleanup-worktrees --confirm --reason "..."`
   after reviewing terminal effects and deciding the worktree can be removed.

`commit-approved` blocks without committing if the worktree base commit, patch,
changed files, or stored test command no longer match the approved evidence.
`github-handoff` requires committed local effect evidence, writes a local
handoff packet, and prints operator `git push` plus `gh pr create --draft`
commands while recording `network_actions_taken=0`.
`ci-deploy-evidence` requires a GitHub handoff packet and records
operator-supplied proof while also recording `network_actions_taken=0`.
`profiles` creates safe local planner/coder/scout/tester/evaluator defaults
and `.clanker/profiles.yml`. `route` records profile selection decisions for
task ids or category/project pairs without claiming tasks or calling model
providers.
`delegate` stores a scoped pending delegation contract and JSON artifact under
`.clanker/delegations/`; it does not start a subagent, call a model provider,
write files, approve work, commit, or mutate external state.
`record-delegation-result` marks a delegation completed only after structured
operator-supplied output matches the expected schema family. It writes a local
result artifact and preserves `network_actions_taken=0`.
`cleanup-worktrees` removes only clean terminal worktrees; dirty blocked
worktrees are recorded as blocked and left in place.

## Reading The Reports

Prefer these files when orienting:

- `docs/next-iteration.md` for the next suggested local work packet.
- `docs/dashboard.md` for the current operational view.
- `docs/OPERATING_SUMMARY.md` for architecture and guardrails.
- `docs/tutorial-subagent-delegation-results.md` for the profile routing,
  delegation contract, and result-ingestion loop.
- `contracts.md` for safety boundaries and evidence expectations.
- `status.md` for chronological implementation evidence.
- `projects/bootstrap/handoff.md` for the current continuation edge.

## Approval Boundaries

Allowed actions are not actions taken. A report may list choices such as
`approve`, `defer`, and `request_more_evidence` while still preserving:

- `selected_action=none`;
- `actions_taken=0`;
- `selections_recorded=0`;
- zero migration/table/approval-row creation counters.

Treat those zeros as intentional safety evidence. Do not cross them without an
explicit operator-approved flow and fresh verification.

## When To Commit And Push

Commit when:

- the scope is coherent;
- generated reports match the current state;
- `python3 -m pytest -q` passes;
- `git diff --check` is clean;
- the commit message describes the operational increment.

Push after the branch target and remote are explicit. For the public GitHub
repo, prefer `main` only for verified snapshots that are useful to share.

## Practical Next Slices

Good next slices now favor executable local approval flow, routing records, and
delegation evidence before broader autonomy:

- memory proposal records and approval flow that can safely summarize useful
  completed delegation output without silently promoting it into durable
  knowledge;
- hosted-dashboard proof only after local commit and CI/deploy evidence is
  modeled;
- remote-worker, scheduler, browser/desktop adapter, budget, trust, retry, and
  real-cost surfaces only after their evidence and approval contracts can be
  enforced.

Each slice should end with explicit non-claims. That discipline is the point:
the system should show what is safe to trust, what is only locally proven, and
what remains blocked.
