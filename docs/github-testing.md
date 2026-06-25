# GitHub Testing

Use GitHub Actions for the slow, authoritative verification loop. The local
machine should stay focused on quick checks while the repository workflow runs
the full suite after a push, pull request, or manual dispatch.

## Automatic Workflow

The workflow lives at `.github/workflows/tests.yml` and runs on:

- pushes to `main`;
- pull requests targeting `main`;
- manual `workflow_dispatch` runs from GitHub.

The `Tests` workflow checks out the repo, sets up Python 3.10, installs
`pytest`, compiles `agent_os` and `tests`, runs local CLI smoke checks against
a temporary ClankerOS root, checks whitespace with `git diff --check`, and then
runs the full suite with:

```bash
python -m pytest -q
```

The temporary root keeps CI smoke commands such as `dashboard` and `iterate`
from rewriting repository docs with runner-specific paths.

## Fast Local Loop

Before pushing, use focused checks that match the files you touched:

```bash
python3 -m compileall -q agent_os tests
python3 -m agent_os.cli app-smoke-test
python3 -m pytest tests/test_first_milestone.py -q -k "github_actions or local_app or inbox"
git diff --check
```

For non-app work, replace the `-k` expression with the narrow test area you
changed. Run the full suite locally only when you need local proof before a
push; otherwise let the GitHub workflow spend the 15-20 minute full-suite time.

## Proof Boundaries

A passing fast local loop is not full-suite proof. A committed workflow file is
not CI proof until GitHub has run it on the pushed commit. A passing GitHub
test workflow is CI proof for tests only; it is still not deployment proof,
runtime proof, provider proof, or approval to enable blocked capabilities.
