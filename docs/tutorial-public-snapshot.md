# Tutorial: Public Snapshot

Use this tutorial when you want to show ClankerOS to another operator or
publish a coherent GitHub snapshot. The goal is a readable, locally verified
state. It is not a deployment claim, a CI claim, or proof that blocked
capabilities are enabled.

## What ClankerOS Is For

ClankerOS is a local-first harness for agentic coding work. It keeps the work
loop inspectable:

```text
goal -> task graph -> execution -> verification -> memory -> visibility -> learning
```

Use it when you want goals, task state, approvals, evidence, generated
operator views, and learning records to survive outside a chat transcript.
Treat the SQLite database, `runs/` artifacts, and generated markdown reports as
local evidence. Treat the markdown project files as the human-readable
continuity layer.

## Suggested First Session

From a fresh checkout, start with local setup and read-only visibility:

```bash
python3 -m agent_os.cli init
python3 -m pytest -q
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Then read:

- `README.md` for the public overview and non-claims.
- `docs/dashboard.md` for current local state.
- `docs/next-iteration.md` for the next suggested work packet.
- `docs/concepts.md` for the vocabulary.
- `docs/reference-commands.md` for the command map.

At this point you should be able to answer three questions before making any
new change:

- What is locally verified?
- What is only reported or proposed?
- What remains blocked behind approval or missing evidence?

## Operator Loop For A Small Change

Keep each change narrow enough that its proof is easy to inspect.

```bash
git status --short --branch
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Use `docs/next-iteration.md` as the suggested next packet, or choose a smaller
manual slice. Before calling the work complete, define:

- the expected file, report, row, or behavior change;
- the verifier command;
- the evidence file or command output that proves the verifier ran;
- the non-claims that still apply.

## Verification Before A Snapshot

For a normal public snapshot, run the broad local check set:

```bash
python3 -m py_compile agent_os/*.py tests/test_first_milestone.py
python3 -m pytest -q
python3 -m agent_os.cli sweep-stuck --timeout-seconds 1800
python3 -m agent_os.cli queue-health
python3 -m agent_os.cli handoff-review
python3 -m agent_os.cli eval-candidates
python3 -m agent_os.cli approvals
python3 -m agent_os.cli eval
python3 -m agent_os.cli playbooks
git diff --check
```

For a documentation-only or otherwise narrow slice, focused checks are fine if
the final summary says exactly what was and was not verified.

When the snapshot is headed to GitHub, prefer this lightweight local gate and
let the checked-in workflow spend the slow time:

```bash
python3 -m compileall -q agent_os tests
python3 -m agent_os.cli app-smoke-test
python3 -m pytest tests/test_first_milestone.py -q -k "github_actions or local_app or inbox"
git diff --check
```

The GitHub `Tests` workflow runs a fast smoke job first and a dependent
full-suite job second. The smoke job gives early route/CLI signal; the commit
is not CI-proven until the full-suite job passes on GitHub.

## Refresh The Human Views

Regenerate the operator-facing views after verification:

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Commit generated reports only when they match the behavior and state you just
verified. If a report is stale, refresh it before using it as evidence.

## Commit A Coherent Snapshot

Before committing, inspect the final shape:

```bash
git status --short
git diff --stat
git diff --check
```

A good public snapshot contains one coherent increment: code if behavior
changed, tests for that behavior, generated evidence when appropriate, and
docs or status notes that explain the current state. Avoid mixing unrelated
experiments into the same snapshot.

```bash
git add <files>
git commit -m "Describe the verified operational increment"
```

## Push Only After The Target Is Clear

Check the remote and branch before pushing:

```bash
git remote -v
git status --short --branch
```

For the public repository, push the intended branch explicitly:

```bash
git push origin main
```

If publishing a feature branch instead of `main`, use that branch name in the
push command and create a draft pull request only after the base branch is
explicit.

## Say What Is Proven

A safe public summary separates:

- local tests and command output;
- generated local reports;
- pushed GitHub state;
- CI or deployment evidence, if checked separately;
- capabilities that remain blocked by design.

Avoid saying the snapshot is deployed, hosted, CI-proven, autonomous,
budget-enforcing, retrying, cost-tracking, or trust-promoting unless those
specific checks actually happened and their evidence is linked.
