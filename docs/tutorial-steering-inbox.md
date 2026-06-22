# Tutorial: Steering Reviews And Inbox

This tutorial walks through the local operator-steering loop:

```text
goal state -> deterministic review -> next action -> inbox triage
```

The loop is intentionally read-mostly. It records local evidence and
recommendations, but it does not execute tasks, approve requests, retry work,
commit, push, deploy, or mutate external systems.

## 1. Start From A Goal

Run a normal local goal or use an existing goal id from `docs/dashboard.md`:

```bash
python3 -m agent_os.cli run-goal "Prove the first milestone closed loop" --project bootstrap
```

If the run produces a `goal_id`, keep it for the next commands.

## 2. Write A Steering Review

```bash
python3 -m agent_os.cli steer <goal_id>
```

The command writes:

- a `steering_reviews` SQLite row;
- `docs/steering-review.md`;
- a CLI summary with `status`, `drift_score`, `recommended_next_action`, and
  `requires_operator`;
- explicit `network_actions_taken: 0` and `external_mutations_taken: 0`.

Deterministic rules currently check for pending approvals, blocked tasks,
failed or repeated attempts, open incidents, completed tasks without evidence,
completed task graphs with an open goal, and missing task plans.

## 3. Ask For The Next Action

```bash
python3 -m agent_os.cli next-action <goal_id>
```

You can also pass a project id:

```bash
python3 -m agent_os.cli next-action bootstrap
```

The command refreshes a steering review and prints the recommended local
operator move. Typical actions include:

- `operator_approval`;
- `review_or_replan`;
- `review_open_incident`;
- `add_evidence_or_replan`;
- `final_review`;
- `continue_current_task`;
- `continue`.

## 4. Triage The Inbox

```bash
python3 -m agent_os.cli inbox
```

The inbox lists:

- recent steering reviews that require an operator;
- pending approval requests;
- open incidents.

Use it before deciding whether to approve, replan, resolve an incident, or ask
for more evidence.

## 5. Regenerate The Dashboard

```bash
python3 -m agent_os.cli dashboard
```

Read `docs/dashboard.md`, especially:

- `## Steering Reviews`;
- `### Approval Inbox`;
- `### Incidents`;
- `### Next Recommended Action`.

## Non-Claims

The steering loop is not a scheduler, worker, model router, retry engine, CI
gate, deploy system, hosted dashboard, remote worker, or approval authority.
It is a local evidence and recommendation layer for the operator.
