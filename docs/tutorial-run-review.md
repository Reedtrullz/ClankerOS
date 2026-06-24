# Tutorial: Review Run Evidence

Use this loop when a run already exists and you want an operator-readable
packet before deciding whether to continue, approve, archive, or replan.

## 1. Create Or Pick A Run

For a fresh local example:

```bash
python3 -m agent_os.cli run-goal "Prove a reviewable evidence packet" --project bootstrap
```

Copy the printed `run_id`.

For an existing run, use the id shown in `docs/dashboard.md` under
`## Recent Runs`.

## 2. Write The Human Review

```bash
python3 -m agent_os.cli review <run_id>
```

This writes:

```text
runs/<run_id>/review.md
```

Read it first when you need a decision summary. It includes the original goal,
current task plan, verification counts, linked evidence files, operator
signals, and recommended next action.

## 3. Write The Evidence Index

```bash
python3 -m agent_os.cli evidence <run_id>
```

This writes:

```text
runs/<run_id>/evidence-index.md
.clanker/projects/<project>/goals/<goal_id>/runs/<run_id>/evidence/
```

Read it when you need to audit the files and database rows attached to the
run. It indexes run files, project artifacts, task rows, event rows,
incidents, approvals, effects, delegations, memory entries, skills, and eval
candidates when they exist.

The packet directory includes `git_status.txt`, `diff.patch`, and
`changed_files.json`. For registered-project runs, those files describe the
registered repo. For bootstrap or system-root runs, they describe the ClankerOS
root. Existing command-proof files from `run-task` stay in place; the review
command writes sidecars instead of replacing them.

## 4. Write The Conceptual Replay

```bash
python3 -m agent_os.cli replay-summary <run_id>
```

This writes:

```text
runs/<run_id>/replay-summary.md
```

Read it when you want the run as a step-by-step story from recorded events.
It is a replay map, not an automated replay engine.

## 5. Refresh The Dashboard

```bash
python3 -m agent_os.cli dashboard
```

The dashboard shows generated run packets under `## Recent Evidence Packets`.

## Non-Claims

These commands do not rerun commands, mutate files, approve effects, commit,
push, fetch, pull, deploy, start remote workers, schedule work, promote trust,
retry work, or track spend. They write local Markdown reports from existing
local state and preserve `network_actions_taken=0`.
