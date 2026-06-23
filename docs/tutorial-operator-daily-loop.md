# Tutorial: Operator Daily Loop

Use this when you return to a ClankerOS workspace and want to know what to do
next without relying on chat memory.

## 1. Rebuild The Visible State

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Read:

- `docs/dashboard.md`
- `docs/next-iteration.md`
- `status.md`
- `projects/bootstrap/handoff.md`

The dashboard is the current local view. The iteration packet is the suggested
next local work item. Neither file is proof of hosted service availability,
remote worker execution, CI success, deployment, trust promotion, or automatic
retry readiness.

## 2. Choose One Narrow Move

Good next moves are shaped like this:

```text
Implement the next item in docs/next-iteration.md with red-first tests,
durable SQLite evidence, dashboard visibility, and explicit non-claims.
```

```text
Review the current dashboard and explain what is locally proven, what is only
a generated report, and what still needs operator approval.
```

```text
Create the next pending downstream proof tasks from applied local effects and
prove the command is idempotent.
```

Avoid broad prompts that ask for multiple autonomy surfaces at once. If a task
touches hosted dashboards, remote workers, scheduling, browser/desktop
automation, CI/deploy, budget enforcement, trust promotion, automatic retries,
or real cost tracking, keep it in proof mode until its local evidence and
operator approval boundary are explicit.

## 3. Verify Before Claiming Progress

For a normal implementation slice:

```bash
python3 -m py_compile agent_os/*.py tests/test_first_milestone.py
python3 -m pytest -q
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
git diff --check
```

For a docs-only slice, at least run:

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
git diff --check
```

## 4. Commit Only Coherent Evidence

A good commit contains:

- the behavior change
- regression tests
- generated report or dashboard updates
- status or handoff notes that name the next move
- docs that explain how an operator should use the new behavior

Do not describe a pushed commit as deployed, CI-proven, hosted, or autonomous
unless that proof was actually checked and recorded.
