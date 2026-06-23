# Getting Started With ClankerOS

ClankerOS is a local-first control plane for agentic coding work. Use it when
you want goals, tasks, evidence, approvals, and operator decisions to survive
outside a chat transcript.

The safest first use is not full autonomy. It is a visible loop:

```text
goal -> task graph -> local work -> verification -> evidence -> dashboard -> next action
```

## Install And Initialize

```bash
git clone https://github.com/Reedtrullz/ClankerOS.git
cd ClankerOS
python3 -m agent_os.cli init
python3 -m pytest -q
```

Expected local effects:

- `.agent/state.db` is created for runtime state.
- `docs/runtime-capability-matrix.md` is written.
- No hosted service, remote worker, model provider, CI job, or deploy is
  started by initialization.

## Run The First Loop

```bash
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Read these files after the commands finish:

- `docs/dashboard.md` for current visible state.
- `docs/next-iteration.md` for the next local work packet.
- `status.md` and `projects/bootstrap/status.md` for chronological evidence.

## Use It For A Coding Change

Register a local repository and run the work in an isolated worktree:

```bash
python3 -m agent_os.cli register-project my-repo \
  --path /path/to/repo \
  --test-command "python3 -m pytest -q"

python3 -m agent_os.cli run-goal \
  "Make the smallest verified change" \
  --project my-repo \
  --isolation worktree \
  --command "<safe local command>"
```

Then inspect the generated run evidence before approving anything:

```bash
python3 -m agent_os.cli approvals
python3 -m agent_os.cli dashboard
```

Only after reviewing the diff and tests:

```bash
python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "reviewed diff and tests"
python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator
```

`commit-approved` creates a local worktree commit only after a fresh evidence
recheck. It does not push or open a pull request.

## Best Operating Pattern

1. Keep each request narrow and evidence-shaped.
2. Ask for one local capability boundary at a time.
3. Prefer report-only proof before action-taking features.
4. Treat dashboard and generated reports as evidence, not as guarantees.
5. Commit only coherent, verified increments.
6. Push only after local tests and metadata readback are clean.

## Good First Prompts

```text
Run the first local loop, regenerate the dashboard, and summarize what is proven and not proven.
```

```text
Register this repo, run a worktree-isolated coding task, capture the diff and tests, then ask before committing.
```

```text
Review the current dashboard and next-iteration packet, then implement the next local proof step with tests.
```

## What To Read Next

- `docs/concepts.md` for vocabulary.
- `docs/architecture.md` for the local control-plane shape.
- `docs/suggested-use.md` for prompt patterns and operating rules.
- `docs/tutorial-approval-gated-coding.md` for the worktree approval loop.
