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

## Recommended Operating Loop

1. Pick one narrow capability or boundary.
2. Write or update a red-first regression when behavior changes.
3. Add the smallest implementation that creates durable local evidence.
4. Regenerate the relevant report and `docs/dashboard.md`.
5. Run `python3 -m pytest -q`.
6. Run `python3 -m agent_os.cli eval`.
7. Record non-claims before treating the work as safe.

## Reading The Reports

Prefer these files when orienting:

- `docs/next-iteration.md` for the next suggested local work packet.
- `docs/dashboard.md` for the current operational view.
- `docs/OPERATING_SUMMARY.md` for architecture and guardrails.
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

Good next slices are still report-only until approved:

- a hosted-dashboard proof evidence importer;
- a remote-worker approval packet that models credentials and rollback;
- an autonomous-scheduling dry-run calendar;
- browser/desktop adapter evidence capture without action execution;
- CI/deploy proof ingestion from GitHub Actions;
- budget-limit simulation before enforcement;
- trust-promotion criteria with explicit demotion paths;
- retry policy dry-run reports;
- real-cost ledger imports from local usage records.

Each slice should end with explicit non-claims. That discipline is the point:
the system should show what is safe to trust, what is only locally proven, and
what remains blocked.
