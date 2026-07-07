# Hosted Read-Only Dashboard Export

`hosted-dashboard-export` creates a static local dashboard bundle that can be
reviewed like a hosted-dashboard candidate without creating a server, deploy,
remote worker, provider call, scheduler, or external mutation.

```bash
python3 -m agent_os.cli hosted-dashboard-export
```

Default output:

- `.clanker/hosted-dashboard-export/index.html`
- `.clanker/hosted-dashboard-export/manifest.json`

The export includes:

- the committed or local `docs/dashboard.md` snapshot when present,
- `status.md` and `docs/status.md` summaries when present,
- the current proof surface state,
- the latest artifact-hygiene summary when present,
- explicit non-claims and zero-effect counters.

Expected CLI safety lines:

```text
hosted_dashboard_export: written
network_actions_taken: 0
external_mutations_taken: 0
deploy_created: false
```

This command does not prove a live hosted dashboard. It creates a local static
readback that can later inform a real hosted dashboard design or deployment
review.
