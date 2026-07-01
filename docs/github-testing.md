# GitHub Testing

Use GitHub Actions for the slow, authoritative verification loop. The local
machine should stay focused on quick checks while the repository workflow runs
the full suite after a codex branch push, main push, pull request, or manual
dispatch.

## Default Operator Loop

For normal ClankerOS app slices, do not spend the session running the whole
suite locally. Use this loop instead:

1. Make a small, reviewable change.
2. Run the narrowest relevant local check for the touched files. For docs-only
   changes, `git diff --check` is usually enough. For app/code changes, prefer
   one focused pytest expression, `app-smoke-test`, or `compileall` over the
   full suite.
3. Commit and push the branch tied to the pull request.
4. Watch the GitHub `Fast smoke verification` job first. If it passes, keep
   building while `Full pytest suite` runs in GitHub.
5. Only inspect full-suite logs when GitHub reports a failure or timeout.

This keeps local iteration fast while still making the repository, not the
chat transcript, the place where slow proof accumulates.

## Automatic Workflow

The workflow lives at `.github/workflows/tests.yml` and runs on:

- pushes to `main`;
- pushes to `codex/**` branches;
- pull requests targeting `main`;
- manual `workflow_dispatch` runs from GitHub as a fallback.

The `Tests` workflow has two jobs:

- `smoke` checks out the repo, sets up Python 3.10, installs `pytest`,
  compiles `agent_os` and `tests`, runs local CLI smoke checks against a
  temporary ClankerOS root, runs the generic route smoke plus the
  fixture-backed `app-demo-smoke-test`, including `/goals`,
  `/goals/<goal_id>`, `/search`, `/workspace`, `/memory`, `/skills`, and
  `/profiles`, runs a focused pytest slice for the GitHub workflow, CI
  snapshot handoff, local app route, artifact viewer, demo scenario, and
  bind-safety tests, and checks whitespace with
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
python3 -m pytest tests/test_first_milestone.py -q -k "github_actions or ci_snapshot or local_app"
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

`ci-snapshot-handoff` prints a `gh run view ...` command for the operator, a
JSON-validated `ci-snapshot-evidence-from-gh-json` pipeline, a job-scoped
fast-smoke variant, and the older manual `ci-snapshot-evidence` command.
Prefer the JSON-validated path after GitHub reports `status=completed`,
`conclusion=success`, and the expected commit SHA. When the fast smoke job has
completed successfully but the full suite is still running, pass
`--job-name "Fast smoke verification"` to record early route/CLI proof without
pretending the full suite has passed. The ClankerOS recorder consumes status
JSON from stdin or a file; it does not fetch GitHub status, run tests, deploy,
push, create PRs, call providers, or mutate external systems.

The validated direct-push proof path looks like:

```bash
gh run view <run_id> --repo Reedtrullz/ClankerOS \
  --json status,conclusion,headSha,headBranch,databaseId,url,jobs \
| python3 -m agent_os.cli ci-snapshot-evidence-from-gh-json \
  --project clankeros \
  --branch main \
  --commit <commit_sha> \
  --status-json -
```

The recorder infers the run id and URL from `databaseId`/`url`, then refuses
pending runs, failed runs, malformed JSON, branch mismatches when `headBranch`
is present, and commit mismatches.

The scoped fast-smoke proof path looks like:

```bash
gh run view <run_id> --repo Reedtrullz/ClankerOS \
  --json status,conclusion,headSha,headBranch,databaseId,url,jobs \
| python3 -m agent_os.cli ci-snapshot-evidence-from-gh-json \
  --project clankeros \
  --branch main \
  --commit <commit_sha> \
  --status-json - \
  --job-name "Fast smoke verification"
```

This records `status_source=github_status_json_job` and an
`evidence_scope` for the named job.

The local app offers the same validation on `/ci-evidence`: paste the completed
`gh run view` JSON into `Record Direct Snapshot From GitHub JSON`, optionally
enter a completed `job_name`, confirm the local write, and it records direct
snapshot proof only after the JSON passes the same checks. The app still does
not contact GitHub.

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

Both record commands write operator-supplied proof only. The
`ci-snapshot-evidence-from-gh-json` command validates supplied GitHub status
JSON before writing. Neither recorder fetches GitHub status, runs CI, deploys,
pushes, opens PRs, calls providers, or mutates external systems.

## Proof Boundaries

A passing fast local loop is not full-suite proof. A committed workflow file is
not CI proof until GitHub has run it on the pushed commit. A passing GitHub
test workflow is CI proof for tests only; it is still not deployment proof,
runtime proof, provider proof, or approval to enable blocked capabilities.
