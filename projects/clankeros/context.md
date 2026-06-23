# Project Context: clankeros

## Registry

- project_id: clankeros
- status: registered
- root_path: /Users/reidar/Documents/Agent System
- repo_url: https://github.com/Reedtrullz/ClankerOS.git
- default_branch: main
- current_branch: main
- default_test_command: python3 -m pytest -q
- allowed_write_roots: /Users/reidar/Documents/Agent System
- project_note: projects/clankeros/project.md
- memory_path: projects/clankeros/knowledge.md
- skills_path: .clanker/skills
- evidence_root: projects/clankeros/artifacts
- last_activity_at: 2026-06-23T13:41:01.603769+00:00

## Operator Commands

```bash
python3 -m agent_os.cli project-status clankeros
python3 -m agent_os.cli run-goal "..." --project clankeros
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
```

## Non-Claims

- Project context generation does not run tests, commit, push, deploy, or mutate external systems.
- Project context generation does not create worktrees, approve effects, or call model providers.
- Branch and remote fields are local git readbacks when available, not live GitHub or CI proof.
