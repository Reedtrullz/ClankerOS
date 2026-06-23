# Tutorial: Public Snapshot

Use this when you want to publish a coherent ClankerOS snapshot to GitHub.
The goal is a shareable state, not a deployment claim.

## 1. Check The Local State

```bash
git status --short --branch
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Read `docs/dashboard.md` and `docs/next-iteration.md`. The dashboard should
show the current local proof state, pending approvals, stuck work, eval posture,
and generated evidence reports. The iteration packet should point to the next
task rather than hiding unfinished work.

## 2. Run Verification

For a normal public snapshot:

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

For a narrower slice, run the focused tests first, then decide whether the
full suite is needed before publishing.

## 3. Regenerate Operator Views

```bash
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

Commit generated reports only when they match the behavior you verified. If a
report is stale, refresh it before treating it as evidence.

## 4. Commit A Coherent Snapshot

```bash
git status --short
git diff --stat
git add <files>
git commit -m "Describe the verified operational increment"
```

A good snapshot commit includes the code change, tests, generated evidence,
status updates, and docs needed to understand the new behavior.

## 5. Push Only After The Target Is Clear

For the public repository:

```bash
git remote -v
git push origin main
```

If publishing a branch instead of `main`, use the branch name in the push and
create a draft PR only after the branch target is explicit.

## 6. Keep The Non-Claims Explicit

After pushing, do not describe the snapshot as deployed, hosted, CI-proven, or
autonomous unless those checks actually happened. A safe summary separates:

- local tests and command output;
- generated local reports;
- pushed GitHub state;
- CI or deployment evidence, if checked separately;
- capabilities that remain blocked by design.
