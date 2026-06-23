# Command Reference

This is a compact map for common ClankerOS commands. Generated reports contain
the detailed proof for each capability.

## Setup And Status

```bash
python3 -m agent_os.cli init
python3 -m agent_os.cli projects
python3 -m agent_os.cli project-status <project>
python3 -m agent_os.cli project-context <project>
python3 -m agent_os.cli dashboard
python3 -m agent_os.cli iterate
python3 -m agent_os.cli approvals
python3 -m agent_os.cli queue-health
python3 -m agent_os.cli handoff-review
```

## First Loop

```bash
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
python3 -m agent_os.cli review <run_id>
python3 -m agent_os.cli evidence <run_id>
python3 -m agent_os.cli replay-summary <run_id>
python3 -m agent_os.cli steer <goal_id>
python3 -m agent_os.cli next-action <goal_or_project>
python3 -m agent_os.cli inbox
```

## Goal Planning Lifecycle

```bash
python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli goal "Make the smallest verified improvement" --project <name>
python3 -m agent_os.cli plan <goal_id>
python3 -m agent_os.cli contract <goal_id>
python3 -m agent_os.cli tasks <goal_id>
python3 -m agent_os.cli update-task <task_id> --status blocked --blocked-reason "waiting on operator scope"
python3 -m agent_os.cli replan <goal_id> --reason "scope changed after operator review"
python3 -m agent_os.cli dashboard
```

`goal` requires a registered project. It creates a durable goal row, plan v1,
three `planned_step` task rows, and artifacts under
`.clanker/projects/<project>/goals/<goal_id>/`. `plan` and `replan` keep
versioned `PLAN-vN.md` files plus the latest `PLAN.md`. `contract` creates a
draft sprint contract for the latest plan. These commands do not execute
tasks, approve work, commit, push, deploy, or call model providers.

## Approval-Gated Coding

```bash
python3 -m agent_os.cli register-project <name> --path /path/to/repo --test-command "python3 -m pytest -q"
python3 -m agent_os.cli project-context <name>
python3 -m agent_os.cli run-goal "Make a tiny verified change" --project <name> --isolation worktree --command "<safe local command>"
python3 -m agent_os.cli approve <approval_id> --decided-by operator --note "reviewed diff and tests"
python3 -m agent_os.cli commit-approved <approval_id> --committed-by operator
python3 -m agent_os.cli github-handoff <effect_id> --base main --title "Change title"
python3 -m agent_os.cli cleanup-worktrees --confirm --reason "committed branch kept"
```

## Profiles And Delegation Packets

```bash
python3 -m agent_os.cli profiles
python3 -m agent_os.cli profile-show scout
python3 -m agent_os.cli route --category repo_search --project bootstrap
python3 -m agent_os.cli delegate <task_id> --profile scout --title "Find relevant files"
python3 -m agent_os.cli delegations <goal_id>
python3 -m agent_os.cli record-delegation-result <delegation_id> --summary "Relevant files identified." --output-json '{"files":["agent_os/cli.py"]}'
```

## Memory And Skills

```bash
python3 -m agent_os.cli memory propose --project bootstrap --key <key> --value <value> --source <source>
python3 -m agent_os.cli memory propose-from-delegation <delegation_id> --key <key>
python3 -m agent_os.cli memory list --project bootstrap
python3 -m agent_os.cli memory approve <memory_id> --approved-by operator
python3 -m agent_os.cli skill propose --project bootstrap --name <name> --description <description> --from-run <run_id>
python3 -m agent_os.cli skills --project bootstrap
python3 -m agent_os.cli skill approve <skill_id> --approved-by operator
```

## Verification

```bash
python3 -m py_compile agent_os/storage.py agent_os/planning.py agent_os/cli.py agent_os/dashboard.py agent_os/iteration.py
python3 -m pytest -q
python3 -m agent_os.cli eval-candidates
python3 -m agent_os.cli eval-after-change --change "<change name>" --file <path>
python3 -m agent_os.cli eval
python3 -m agent_os.cli playbooks
git diff --check
```

## Capability Activation Proof Tasks

```bash
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-tasks
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-delegations
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results
python3 -m agent_os.cli capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-decide --operator-id operator --selected-action accept_keep_blocked --selection-note "Accepted downstream result-effect task result-effect task result-effect task result-effect task result-effect task proof-plan result and kept capability activation blocked." --evidence-reference docs/capability-activation-followup-result-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-result-effect-task-results.md
```

This creates pending downstream proof tasks from applied local effects and
then routes those tasks into read-only evaluator delegation packets. Completed
local evaluator outputs can be ingested as result records and reviewed by an
operator decision. Approval, activation, execution, network, and external
mutation counters stay at zero.

## Publishing

```bash
git status --short --branch
git diff --check
python3 -m pytest -q
gh repo view Reedtrullz/ClankerOS --json description,repositoryTopics,homepageUrl
git push origin main
```

Pushing is not deployment. GitHub metadata readback is not CI proof.
