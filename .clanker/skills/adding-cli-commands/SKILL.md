---
name: adding-cli-commands
description: "Procedure for adding tested CLI commands."
status: proposed
---

# adding-cli-commands

## Purpose

Procedure for adding tested CLI commands.

## When To Use

Use this skill when repeating the procedure captured from source run
`run_6fcdef549e8b` would help future ClankerOS work.

## When Not To Use

Do not use this skill for unrelated projects, destructive actions, external
side effects, or work that lacks fresh verification evidence.

## Procedure

1. Read the current project state and the relevant source files.
2. State the intended local change and its approval boundary.
3. Make the smallest scoped change that satisfies the task.
4. Run the verification commands named by the project.
5. Record evidence, non-claims, and any follow-up action.

## Required Inputs

- project id
- current objective or task
- source files or run evidence
- verification command

## Expected Outputs

- scoped local change or proposal
- verification evidence
- explicit non-claims
- next recommended action

## Verification Steps

- Run the focused regression for the changed behavior.
- Run the project default verification command.
- Confirm generated evidence files exist before approving the skill.

## Common Failure Modes

- Treating a proposed skill as active before operator approval.
- Reusing stale run evidence without a fresh check.
- Expanding scope beyond the current project task.

## Proposal Metadata

- source_run_id: run_6fcdef549e8b
- source_task_id: none
- created_by_profile: tester
- network_actions_taken: 0
- external_mutations_taken: 0
- activation_status: proposed_until_approved
