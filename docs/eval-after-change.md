# Eval After Change

- id: eval_after_change_55b5d28285b1
- status: pass
- change: Add approval-gated worktree coding cockpit and tutorial docs
- changed_paths: agent_os/coding_workflow.py,agent_os/project_registry.py,agent_os/storage.py,agent_os/cli.py,agent_os/dashboard.py,tests/test_first_milestone.py,README.md,docs/tutorial-approval-gated-coding.md,docs/suggested-use.md,docs/OPERATING_SUMMARY.md,plan.md,tasks.md
- evals: first_milestone_closed_loop
- result_paths: evals/results/first_milestone_closed_loop.json
- run_ids: run_f53498dc62ff
- command: python3 -m agent_os.cli eval-after-change --change "Add approval-gated worktree coding cockpit and tutorial docs" --file "agent_os/coding_workflow.py" --file "agent_os/project_registry.py" --file "agent_os/storage.py" --file "agent_os/cli.py" --file "agent_os/dashboard.py" --file "tests/test_first_milestone.py" --file "README.md" --file "docs/tutorial-approval-gated-coding.md" --file "docs/suggested-use.md" --file "docs/OPERATING_SUMMARY.md" --file "plan.md" --file "tasks.md"
- completed_at: 2026-06-22T11:35:09.014759+00:00
