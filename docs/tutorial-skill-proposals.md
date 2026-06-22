# Propose And Approve Reusable Skills

Use this loop when a verified run produced a reusable procedure that should
become local project knowledge, but should not become active without operator
review.

## 1. Start From Verified Run Evidence

Pick a run id that already exists in ClankerOS:

```bash
python3 -m agent_os.cli eval-after-change --change "Describe the harness change" --file agent_os/cli.py
```

The command prints one or more `run_ids`. Use the relevant run id in the next
step.

## 2. Propose The Skill

```bash
python3 -m agent_os.cli skill propose \
  --project bootstrap \
  --name adding-cli-commands \
  --description "Procedure for adding tested CLI commands." \
  --from-run <run_id>
```

This writes:

```text
.clanker/skills/adding-cli-commands/SKILL.md
```

It also records a `skills` row with `status=proposed` and a first
`skill_versions` row with the content hash.

## 3. Review The Proposal

```bash
python3 -m agent_os.cli skills --project bootstrap
python3 -m agent_os.cli skill show <skill_id>
python3 -m agent_os.cli dashboard
```

The dashboard shows proposed skills under `## Skill Proposals`. A proposed
skill is reviewable local evidence, not an active operating instruction.

## 4. Approve Or Archive

Approve only after reviewing the generated `SKILL.md`:

```bash
python3 -m agent_os.cli skill approve <skill_id> --approved-by operator
```

Archive proposals that are stale, duplicate, or too weak:

```bash
python3 -m agent_os.cli skill archive <skill_id> --archived-by operator --reason "superseded"
```

## Non-Claims

- `skill propose` does not call a model provider.
- `skill propose` does not mutate external systems.
- Proposed skills are not active until `skill approve` runs.
- This is local ClankerOS skill state, not a Codex global skill install.
