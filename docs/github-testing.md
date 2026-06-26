# GitHub Testing

Use GitHub Actions for the slow, authoritative verification loop. The local
machine should stay focused on quick checks while the repository workflow runs
the full suite after a push, pull request, or manual dispatch.

## Automatic Workflow

The workflow lives at `.github/workflows/tests.yml` and runs on:

- pushes to `main`;
- pull requests targeting `main`;
- manual `workflow_dispatch` runs from GitHub.

The `Tests` workflow has two jobs:

- `smoke` checks out the repo, sets up Python 3.10, installs `pytest`,
  compiles `agent_os` and `tests`, runs local CLI smoke checks against a
  temporary ClankerOS root, runs the generic route smoke plus the
  fixture-backed `app-demo-smoke-test`, runs a focused pytest slice for the
  GitHub workflow, CI snapshot handoff, local app route, artifact viewer,
  demo scenario, and bind-safety tests, and checks whitespace with
  `git diff --check`.
- `full-suite` depends on `smoke` and then runs the slow full suite with:

```bash
python -m pytest -q
```

The temporary root keeps CI smoke commands such as `dashboard` and `iterate`
from rewriting repository docs with runner-specific paths.

The focused pytest smoke is intentionally narrower than the full suite. It
exists to catch high-signal local-app and CI-handoff regressions early, before
the slower `full-suite` job spends time on every test.

The smoke job has a 10-minute timeout, and the full-suite job has a 45-minute
timeout. A passed smoke job is early route/CLI proof only. While a run is still
in progress, treat it as pending proof and keep waiting on GitHub instead of
rerunning the full suite locally. If the run fails or reaches the timeout,
inspect the failed job log and fix that specific CI failure before pushing
another app slice.

## Fast Local Loop

Before pushing, use focused checks that match the files you touched:

```bash
python3 -m compileall -q agent_os tests
python3 -m agent_os.cli app-smoke-test
python3 -m agent_os.cli app-demo-smoke-test
python3 -m pytest tests/test_first_milestone.py -q -k "github_actions or ci_snapshot_handoff or local_app"
git diff --check
```

For non-app work, replace the `-k` expression with the narrow test area you
changed. Run the full suite locally only when you need local proof before a
push; otherwise let the GitHub workflow spend the 15-20 minute full-suite time.

## Recording Proof

While a direct-push run is pending, generate the exact status-check and
record-after-success commands with:

```bash
python3 -m agent_os.cli ci-snapshot-handoff \
  --project clankeros \
  --branch main \
  --commit <commit_sha> \
  --external-run-id <run_id> \
  --repo Reedtrullz/ClankerOS
```

`ci-snapshot-handoff` prints a `gh run view ...` command for the operator and
the matching `ci-snapshot-evidence` command to run after GitHub reports
`status=completed`, `conclusion=success`, and the expected commit SHA. It does
not fetch GitHub status, write evidence, run tests, deploy, push, create PRs,
call providers, or mutate external systems.

For publication handoffs, record a completed GitHub Actions run with:

```bash
python3 -m agent_os.cli ci-deploy-evidence <github_handoff_id> \
  --provider github-actions \
  --status success \
  --external-run-id <run_id> \
  --url <run_url>
```

For direct operator-authorized pushes to `main`, record the completed run with:

```bash
python3 -m agent_os.cli ci-snapshot-evidence \
  --project clankeros \
  --branch main \
  --commit <commit_sha> \
  --provider github-actions \
  --status success \
  --external-run-id <run_id> \
  --url <run_url>
```

Both commands record operator-supplied proof only. They do not fetch GitHub
status, run CI, deploy, push, open PRs, call providers, or mutate external
systems.

## Proof Boundaries

A passing fast local loop is not full-suite proof. A committed workflow file is
not CI proof until GitHub has run it on the pushed commit. A passing GitHub
test workflow is CI proof for tests only; it is still not deployment proof,
runtime proof, provider proof, or approval to enable blocked capabilities.
