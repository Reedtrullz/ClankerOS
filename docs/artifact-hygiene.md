# Artifact Hygiene

`artifact-hygiene` is a report-only local command for separating intentional
evidence from local runtime clutter without deleting anything.

```bash
python3 -m agent_os.cli artifact-hygiene
```

It writes:

- `.clanker/artifact-hygiene/latest.json`
- `.clanker/artifact-hygiene/latest.md`

The command prints counts for:

- `tracked_intentional` - tracked evidence such as selected `.clanker`
  delegation/project/memory files and repo-visible status docs.
- `ignored_runtime_state` - files matched by `.gitignore`, including `.agent/`
  and local app state.
- `unpromoted_proof` - untracked CI/self-hosting proof readbacks and modified
  generated proof docs that are not new merge claims.
- `generated_local_artifact` - local run, smoke, demo, app scratch, and hygiene
  report outputs.
- `visible_evidence_candidate` - untracked `.clanker/delegations/**` or
  `.clanker/projects/**` evidence that may deserve operator promotion.
- `unknown_needs_operator_review` - other untracked files.

Safety counters are part of the contract:

```text
deleted: 0
gitignore_changes: 0
network_actions_taken: 0
external_mutations_taken: 0
```

The command does not edit `.gitignore`, promote evidence, hide intentional
`.clanker` paths, delete files, call providers, deploy, or contact GitHub.
