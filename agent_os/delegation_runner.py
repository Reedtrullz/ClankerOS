from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from agent_os.ids import new_id
from agent_os.memory_entries import MemoryEntryError, propose_memory_from_delegation
from agent_os.storage import (
    AgentProfile,
    MemoryEntry,
    Storage,
    SubagentDelegation,
    Task,
    utc_now,
)
from agent_os.subagent_delegation import DelegationError, record_delegation_result


class DelegationRunError(ValueError):
    pass


@dataclass(frozen=True)
class DelegationRunResult:
    delegation_id: str
    run_id: str
    status: str
    adapter_type: str
    command: str
    exit_code: int | None
    stdout_path: Path
    stderr_path: Path
    parsed_output_path: Path
    evidence_dir: Path
    result_artifact_path: Path | None
    incident_id: str | None
    memory_proposal_id: str | None
    next_recommended_action: str
    message: str


UNSAFE_ADAPTER_TOKENS = [
    "rm -rf",
    "git push",
    "gh pr create",
    "curl",
    "wget",
    "ssh",
    "scp",
    "rsync",
    "sudo",
]


def configure_profile_adapter(
    storage: Storage,
    profile_name: str,
    *,
    adapter_type: str,
    command: str,
    input_mode: str,
    output_mode: str,
    timeout_seconds: int,
) -> AgentProfile:
    if adapter_type != "shell":
        raise DelegationRunError("only shell adapters are supported")
    if input_mode not in {"prompt_file", "stdin", "json_file"}:
        raise DelegationRunError(f"unsupported input_mode {input_mode}")
    if output_mode not in {"json", "text"}:
        raise DelegationRunError(f"unsupported output_mode {output_mode}")
    if timeout_seconds <= 0:
        raise DelegationRunError("timeout_seconds must be positive")
    _validate_safe_adapter_command(command)
    return storage.update_profile_adapter_config(
        profile_name,
        {
            "type": adapter_type,
            "command": command,
            "input_mode": input_mode,
            "output_mode": output_mode,
            "timeout_seconds": timeout_seconds,
        },
    )


def run_delegation(
    root: Path,
    storage: Storage,
    delegation_id: str,
    *,
    profile_override: str | None = None,
    adapter_command: str | None = None,
    record_memory: bool = False,
    memory_key: str | None = None,
    operator_id: str = "operator",
) -> DelegationRunResult:
    root = root.resolve()
    delegation = storage.get_subagent_delegation(delegation_id)
    if delegation is None:
        raise DelegationRunError(f"delegation {delegation_id} not found")
    if delegation.status == "completed":
        raise DelegationRunError(f"delegation {delegation_id} is already completed")
    if delegation.status != "pending":
        raise DelegationRunError(
            f"delegation {delegation_id} is not pending: {delegation.status}"
        )

    task = storage.get_task(delegation.parent_task_id)
    assigned_profile = storage.get_profile(delegation.assigned_profile)
    if assigned_profile is None:
        raise DelegationRunError(f"profile {delegation.assigned_profile} not found")
    _validate_read_only_subagent(assigned_profile)
    profile_name = profile_override or delegation.assigned_profile
    profile = assigned_profile
    if profile_override:
        profile = storage.get_profile(profile_name)
        if profile is None:
            raise DelegationRunError(f"profile {profile_name} not found")
        _validate_read_only_subagent(profile)
    adapter = _adapter_config(profile, adapter_command)

    run_id = storage.create_run(delegation.parent_goal_id, task.project_id, root / "runs")
    evidence_dir = (
        root
        / ".clanker"
        / "delegations"
        / delegation.id
        / "runs"
        / run_id
        / "evidence"
    )
    evidence_dir.mkdir(parents=True, exist_ok=True)
    _write_run_files(root, run_id, delegation, task)
    started = storage.mark_subagent_delegation_started(delegation.id)
    delegation = started

    try:
        _validate_adapter_config(adapter, profile)
    except DelegationRunError as error:
        return _fail_run(
            root,
            storage,
            delegation=delegation,
            task=task,
            profile=profile,
            adapter=adapter,
            run_id=run_id,
            evidence_dir=evidence_dir,
            failure_class=_failure_class(str(error)),
            message=str(error),
            exit_code=None,
            stdout="",
            stderr="",
            parsed_output=None,
        )

    input_bundle = _write_input_bundle(evidence_dir, delegation, task, profile, adapter)
    prompt_path = evidence_dir / "prompt.md"
    stdout_path = evidence_dir / "stdout.txt"
    stderr_path = evidence_dir / "stderr.txt"
    raw_output_path = evidence_dir / "raw_output.txt"
    parsed_output_path = evidence_dir / "parsed_output.json"
    validation_path = evidence_dir / "validation.json"
    command = _adapter_command(
        adapter["command"],
        input_mode=adapter["input_mode"],
        input_path=evidence_dir / "input.json",
        prompt_path=prompt_path,
        evidence_dir=evidence_dir,
    )
    completed = _run_shell_adapter(
        command,
        cwd=root,
        timeout_seconds=int(adapter["timeout_seconds"]),
        stdin_text=delegation.prompt if adapter["input_mode"] == "stdin" else None,
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    raw_output_path.write_text(completed.stdout, encoding="utf-8")

    if completed.returncode == 124:
        return _fail_run(
            root,
            storage,
            delegation=delegation,
            task=task,
            profile=profile,
            adapter={**adapter, "command": command},
            run_id=run_id,
            evidence_dir=evidence_dir,
            failure_class="adapter timeout",
            message=f"adapter command timed out after {adapter['timeout_seconds']} seconds",
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            parsed_output=None,
        )
    if completed.returncode != 0:
        return _fail_run(
            root,
            storage,
            delegation=delegation,
            task=task,
            profile=profile,
            adapter={**adapter, "command": command},
            run_id=run_id,
            evidence_dir=evidence_dir,
            failure_class="adapter non-zero exit",
            message=f"adapter command exited with {completed.returncode}",
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            parsed_output=None,
        )

    try:
        parsed = _parse_adapter_output(completed.stdout, adapter["output_mode"])
        result_summary = _result_summary(parsed)
        structured_output = _structured_output(parsed)
        _validate_forbidden_actions(delegation, parsed)
        validation_path.write_text(
            json.dumps(
                {
                    "valid": True,
                    "expected_output_schema": delegation.expected_output_schema,
                    "result_summary_present": True,
                    "structured_output_present": True,
                    "forbidden_actions_detected": [],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        parsed_output_path.write_text(
            json.dumps(parsed, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        completed_delegation, _already_recorded = record_delegation_result(
            root,
            storage,
            delegation_id=delegation.id,
            result_summary=result_summary,
            structured_output=structured_output,
            recorded_by=f"adapter:{profile.name}",
            execution_metadata={
                "execution_run_id": run_id,
                "execution_adapter_type": adapter["type"],
                "adapter_type": adapter["type"],
                "execution_evidence_dir": str(evidence_dir.relative_to(root)),
                "network_actions_taken": "unknown",
                "provider_calls_taken_by_clankeros": 0,
                "external_mutations_taken": 0,
                "non_claims": [
                    "No commit was created by ClankerOS.",
                    "No push was created by ClankerOS.",
                    "No deploy was created by ClankerOS.",
                    "No approval was granted by ClankerOS.",
                    "No capability was activated by ClankerOS.",
                    "ClankerOS did not directly call a model provider.",
                    "Adapter network/provider behavior is unknown unless adapter evidence proves otherwise.",
                ],
            },
        )
    except json.JSONDecodeError as error:
        return _fail_run(
            root,
            storage,
            delegation=delegation,
            task=task,
            profile=profile,
            adapter={**adapter, "command": command},
            run_id=run_id,
            evidence_dir=evidence_dir,
            failure_class="malformed json",
            message="malformed adapter json output",
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            parsed_output={"error": str(error)},
        )
    except DelegationRunError as error:
        return _fail_run(
            root,
            storage,
            delegation=delegation,
            task=task,
            profile=profile,
            adapter={**adapter, "command": command},
            run_id=run_id,
            evidence_dir=evidence_dir,
            failure_class=_failure_class(str(error)),
            message=str(error),
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            parsed_output=None,
        )
    except (DelegationError, OSError, ValueError) as error:
        message = str(error)
        failure_class = (
            "schema validation failed"
            if "expected schema" in message
            else "result artifact write failure"
            if isinstance(error, OSError)
            else "delegation result failed"
        )
        return _fail_run(
            root,
            storage,
            delegation=delegation,
            task=task,
            profile=profile,
            adapter={**adapter, "command": command},
            run_id=run_id,
            evidence_dir=evidence_dir,
            failure_class=failure_class,
            message=message,
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            parsed_output=None,
        )

    result_artifact = Path(completed_delegation.result_artifact_path)
    result_payload = json.loads(result_artifact.read_text(encoding="utf-8"))
    (evidence_dir / "result.json").write_text(
        json.dumps(result_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    memory_entry: MemoryEntry | None = None
    if record_memory:
        key = memory_key or f"delegation.{delegation.category}.{delegation.id}"
        memory_entry, memory_artifact, _already = propose_memory_from_delegation(
            root,
            storage,
            delegation_id=delegation.id,
            key=key,
            created_by_profile=profile.name,
        )
        (evidence_dir / "memory_proposal.json").write_text(
            Path(memory_artifact).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    storage.complete_run(run_id, "completed")
    _write_success_summary(
        evidence_dir,
        delegation=completed_delegation,
        profile=profile,
        adapter={**adapter, "command": command},
        run_id=run_id,
        result_summary=result_summary,
        memory_entry=memory_entry,
    )
    _write_profile_and_adapter(evidence_dir, profile, {**adapter, "command": command})
    _write_delegation_json(evidence_dir, completed_delegation)
    return DelegationRunResult(
        delegation_id=delegation.id,
        run_id=run_id,
        status="completed",
        adapter_type=adapter["type"],
        command=command,
        exit_code=completed.returncode,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        parsed_output_path=parsed_output_path,
        evidence_dir=evidence_dir,
        result_artifact_path=result_artifact,
        incident_id=None,
        memory_proposal_id=memory_entry.id if memory_entry else None,
        next_recommended_action="review_delegation_result",
        message="completed",
    )


def _adapter_config(
    profile: AgentProfile,
    adapter_command: str | None,
) -> dict[str, Any]:
    adapter = dict(profile.adapter_config_json or {})
    if adapter_command:
        adapter.update(
            {
                "type": "shell",
                "command": adapter_command,
                "input_mode": adapter.get("input_mode", "json_file"),
                "output_mode": adapter.get("output_mode", "json"),
                "timeout_seconds": adapter.get("timeout_seconds", 300),
            }
        )
    return adapter


def _validate_adapter_config(adapter: dict[str, Any], profile: AgentProfile) -> None:
    if not adapter:
        raise DelegationRunError(
            f"no executor adapter configured for profile {profile.name}"
        )
    if adapter.get("type") != "shell":
        raise DelegationRunError(f"unsupported adapter type {adapter.get('type')}")
    command = str(adapter.get("command") or "").strip()
    if not command:
        raise DelegationRunError(
            f"no executor adapter configured for profile {profile.name}"
        )
    _validate_safe_adapter_command(command)
    input_mode = adapter.get("input_mode", "json_file")
    output_mode = adapter.get("output_mode", "json")
    if input_mode not in {"prompt_file", "stdin", "json_file"}:
        raise DelegationRunError(f"unsupported input_mode {input_mode}")
    if output_mode not in {"json", "text"}:
        raise DelegationRunError(f"unsupported output_mode {output_mode}")
    adapter["command"] = command
    adapter["input_mode"] = input_mode
    adapter["output_mode"] = output_mode
    adapter["timeout_seconds"] = int(adapter.get("timeout_seconds", 300))


def _validate_safe_adapter_command(command: str) -> None:
    lowered = command.lower()
    for token in UNSAFE_ADAPTER_TOKENS:
        if token in lowered:
            raise DelegationRunError(f"unsafe adapter command contains {token}")


def _validate_read_only_subagent(profile: AgentProfile) -> None:
    permissions = profile.permissions_json
    if (
        profile.mode != "subagent"
        or permissions.get("write") != "deny"
        or permissions.get("commit") != "deny"
    ):
        raise DelegationRunError(f"profile {profile.name} is not a read-only subagent")


def _write_input_bundle(
    evidence_dir: Path,
    delegation: SubagentDelegation,
    task: Task,
    profile: AgentProfile,
    adapter: dict[str, Any],
) -> dict[str, Any]:
    prompt_path = evidence_dir / "prompt.md"
    prompt_path.write_text(delegation.prompt, encoding="utf-8")
    bundle = {
        "delegation": _delegation_payload(delegation),
        "task": {
            "id": task.id,
            "goal_id": task.goal_id,
            "project_id": task.project_id,
            "task_type": task.task_type,
            "description": task.description,
            "verification_plan": task.verification_plan,
        },
        "profile": _profile_payload(profile),
        "adapter": _redacted_adapter(adapter),
        "prompt_path": str(prompt_path),
        "evidence_dir": str(evidence_dir),
        "network_actions_taken_by_clankeros": 0,
        "provider_calls_taken_by_clankeros": 0,
        "external_mutations_taken_by_clankeros": 0,
    }
    (evidence_dir / "input.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_profile_and_adapter(evidence_dir, profile, adapter)
    _write_delegation_json(evidence_dir, delegation)
    return bundle


def _adapter_command(
    command: str,
    *,
    input_mode: str,
    input_path: Path,
    prompt_path: Path,
    evidence_dir: Path,
) -> str:
    replacements = {
        "{input_path}": shlex.quote(str(input_path)),
        "{prompt_path}": shlex.quote(str(prompt_path)),
        "{evidence_dir}": shlex.quote(str(evidence_dir)),
    }
    formatted = command
    for placeholder, value in replacements.items():
        formatted = formatted.replace(placeholder, value)
    if input_mode == "json_file" and "{input_path}" not in command:
        formatted += " " + shlex.quote(str(input_path))
    if input_mode == "prompt_file" and "{prompt_path}" not in command:
        formatted += " " + shlex.quote(str(prompt_path))
    return formatted


def _run_shell_adapter(
    command: str,
    *,
    cwd: Path,
    timeout_seconds: int,
    stdin_text: str | None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            text=True,
            input=stdin_text,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        stderr = _timeout_output(error.stderr)
        if stderr:
            stderr += "\n"
        stderr += f"Adapter timed out after {timeout_seconds} seconds."
        return subprocess.CompletedProcess(
            args=command,
            returncode=124,
            stdout=_timeout_output(error.stdout),
            stderr=stderr,
        )


def _parse_adapter_output(stdout: str, output_mode: str) -> dict[str, Any]:
    if output_mode == "json":
        return json.loads(stdout)
    return {
        "result_summary": stdout.strip(),
        "structured_output": {},
    }


def _result_summary(parsed: dict[str, Any]) -> str:
    summary = parsed.get("result_summary")
    if not isinstance(summary, str) or not summary.strip():
        raise DelegationRunError("adapter output missing non-empty result_summary")
    return summary.strip()


def _structured_output(parsed: dict[str, Any]) -> dict[str, Any]:
    structured_output = parsed.get("structured_output")
    if not isinstance(structured_output, dict):
        raise DelegationRunError("adapter output missing structured_output")
    return structured_output


def _validate_forbidden_actions(
    delegation: SubagentDelegation,
    parsed: dict[str, Any],
) -> None:
    claimed = parsed.get("forbidden_actions_taken", [])
    if not isinstance(claimed, list):
        claimed = [claimed]
    actions_taken = parsed.get("actions_taken", [])
    if not isinstance(actions_taken, list):
        actions_taken = [actions_taken]
    forbidden = set(delegation.forbidden_actions_json)
    detected = [str(action) for action in claimed if str(action)]
    detected.extend(str(action) for action in actions_taken if str(action) in forbidden)
    if detected:
        raise DelegationRunError(
            "adapter output claims forbidden actions: " + ",".join(sorted(set(detected)))
        )


def _fail_run(
    root: Path,
    storage: Storage,
    *,
    delegation: SubagentDelegation,
    task: Task,
    profile: AgentProfile,
    adapter: dict[str, Any],
    run_id: str,
    evidence_dir: Path,
    failure_class: str,
    message: str,
    exit_code: int | None,
    stdout: str,
    stderr: str,
    parsed_output: dict[str, Any] | None,
) -> DelegationRunResult:
    stdout_path = evidence_dir / "stdout.txt"
    stderr_path = evidence_dir / "stderr.txt"
    raw_output_path = evidence_dir / "raw_output.txt"
    parsed_output_path = evidence_dir / "parsed_output.json"
    validation_path = evidence_dir / "validation.json"
    result_path = evidence_dir / "result.json"
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    raw_output_path.write_text(stdout, encoding="utf-8")
    parsed_output_path.write_text(
        json.dumps(parsed_output or {}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    validation_payload = {
        "valid": False,
        "failure_class": failure_class,
        "message": message,
        "expected_output_schema": delegation.expected_output_schema,
    }
    validation_path.write_text(
        json.dumps(validation_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    result_payload = {
        "delegation_id": delegation.id,
        "run_id": run_id,
        "status": "failed",
        "adapter_type": str(adapter.get("type", "none")),
        "evidence_dir": str(evidence_dir.relative_to(root)),
        "failure_class": failure_class,
        "message": message,
        "exit_code": exit_code,
        "network_actions_taken": "unknown",
        "provider_calls_taken_by_clankeros": 0,
        "external_mutations_taken": 0,
    }
    result_path.write_text(
        json.dumps(result_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    failed = storage.fail_subagent_delegation(
        delegation.id,
        result_summary=message,
        result_artifact_path=str(result_path),
    )
    incident_id = _record_incident(
        storage,
        evidence_dir,
        delegation=failed,
        task=task,
        profile=profile,
        adapter=adapter,
        run_id=run_id,
        failure_class=failure_class,
        message=message,
        exit_code=exit_code,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        validation_path=validation_path,
    )
    result_payload["incident_id"] = incident_id
    result_path.write_text(
        json.dumps(result_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    storage.complete_run(run_id, "failed")
    _write_failure_summary(
        evidence_dir,
        delegation=failed,
        profile=profile,
        adapter=adapter,
        run_id=run_id,
        failure_class=failure_class,
        message=message,
        incident_id=incident_id,
    )
    _write_profile_and_adapter(evidence_dir, profile, adapter)
    _write_delegation_json(evidence_dir, failed)
    return DelegationRunResult(
        delegation_id=delegation.id,
        run_id=run_id,
        status="failed",
        adapter_type=str(adapter.get("type", "none")),
        command=str(adapter.get("command", "")),
        exit_code=exit_code,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        parsed_output_path=parsed_output_path,
        evidence_dir=evidence_dir,
        result_artifact_path=result_path,
        incident_id=incident_id,
        memory_proposal_id=None,
        next_recommended_action="review_open_incident",
        message=message,
    )


def _record_incident(
    storage: Storage,
    evidence_dir: Path,
    *,
    delegation: SubagentDelegation,
    task: Task,
    profile: AgentProfile,
    adapter: dict[str, Any],
    run_id: str,
    failure_class: str,
    message: str,
    exit_code: int | None,
    stdout_path: Path,
    stderr_path: Path,
    validation_path: Path,
) -> str:
    incident_id = new_id("incident")
    incident_path = evidence_dir / "incident.json"
    evidence = {
        "incident_id": incident_id,
        "delegation_id": delegation.id,
        "profile": profile.name,
        "adapter": _redacted_adapter(adapter),
        "exit_code": exit_code,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "validation_path": str(validation_path),
        "failure_class": failure_class,
        "message": message,
        "next_recommended_operator_action": "review_open_incident",
        "network_actions_taken": "unknown",
        "provider_calls_taken_by_clankeros": 0,
        "external_mutations_taken": 0,
    }
    incident_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return storage.record_incident(
        incident_id=incident_id,
        project_id=task.project_id,
        run_id=run_id,
        goal_id=delegation.parent_goal_id,
        task_id=task.id,
        task_type="subagent_delegation",
        incident_type="delegation_execution_failed",
        severity="high",
        status="open",
        summary=message,
        failure_class=failure_class,
        verification_method="run-delegation",
        verification_path=str(validation_path),
        failed_checks=[failure_class],
        evidence=evidence,
        artifacts=[str(stdout_path), str(stderr_path), str(validation_path)],
        evidence_path=str(incident_path),
    )


def _write_run_files(
    root: Path,
    run_id: str,
    delegation: SubagentDelegation,
    task: Task,
) -> None:
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "activity.md").write_text(
        "\n".join(
            [
                f"# Activity For {run_id}",
                "",
                f"- run-delegation started for {delegation.id}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "events.jsonl").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "goal_id": delegation.parent_goal_id,
                "task_id": task.id,
                "event_type": "delegation.execution_started",
                "message": f"started delegation {delegation.id}",
                "created_at": utc_now(),
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "summary.md").write_text(
        "\n".join(
            [
                f"# Delegation Run {run_id}",
                "",
                f"- delegation_id: {delegation.id}",
                f"- parent_goal_id: {delegation.parent_goal_id}",
                f"- parent_task_id: {task.id}",
                f"- project_id: {task.project_id}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def _write_success_summary(
    evidence_dir: Path,
    *,
    delegation: SubagentDelegation,
    profile: AgentProfile,
    adapter: dict[str, Any],
    run_id: str,
    result_summary: str,
    memory_entry: MemoryEntry | None,
) -> None:
    _write_summary(
        evidence_dir,
        lines=[
            f"# Delegation Evidence {delegation.id}",
            "",
            f"- run_id: {run_id}",
            f"- delegation_id: {delegation.id}",
            f"- parent_goal_id: {delegation.parent_goal_id}",
            f"- parent_task_id: {delegation.parent_task_id}",
            f"- assigned_profile: {profile.name}",
            f"- adapter_type: {adapter.get('type', 'unknown')}",
            f"- expected_output_schema: {delegation.expected_output_schema}",
            "- execution_status: completed",
            "- output_validated: true",
            f"- result_summary: {result_summary}",
            f"- memory_proposal: {memory_entry.id if memory_entry else 'none'}",
            "",
            "## Evidence Paths",
            "",
            "- delegation.json",
            "- profile.json",
            "- adapter.json",
            "- input.json",
            "- prompt.md",
            "- stdout.txt",
            "- stderr.txt",
            "- raw_output.txt",
            "- parsed_output.json",
            "- validation.json",
            "- result.json",
            "",
            "## Non-Claims",
            "",
            "- no commit",
            "- no push",
            "- no deploy",
            "- no approval was granted",
            "- no capability was activated",
            "- provider_calls_taken_by_clankeros: 0",
            "- external_mutations_taken: 0",
            "- network_actions_taken: unknown unless adapter evidence proves otherwise",
        ],
    )


def _write_failure_summary(
    evidence_dir: Path,
    *,
    delegation: SubagentDelegation,
    profile: AgentProfile,
    adapter: dict[str, Any],
    run_id: str,
    failure_class: str,
    message: str,
    incident_id: str,
) -> None:
    _write_summary(
        evidence_dir,
        lines=[
            f"# Delegation Evidence {delegation.id}",
            "",
            f"- run_id: {run_id}",
            f"- delegation_id: {delegation.id}",
            f"- parent_goal_id: {delegation.parent_goal_id}",
            f"- parent_task_id: {delegation.parent_task_id}",
            f"- assigned_profile: {profile.name}",
            f"- adapter_type: {adapter.get('type', 'none')}",
            f"- expected_output_schema: {delegation.expected_output_schema}",
            "- execution_status: failed",
            "- output_validated: false",
            f"- failure_class: {failure_class}",
            f"- message: {message}",
            f"- incident_id: {incident_id}",
            "",
            "## Non-Claims",
            "",
            "- no commit",
            "- no push",
            "- no deploy",
            "- no approval was granted",
            "- no capability was activated",
            "- provider_calls_taken_by_clankeros: 0",
            "- external_mutations_taken: 0",
            "- network_actions_taken: unknown unless adapter evidence proves otherwise",
        ],
    )


def _write_summary(evidence_dir: Path, *, lines: list[str]) -> None:
    (evidence_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_profile_and_adapter(
    evidence_dir: Path,
    profile: AgentProfile,
    adapter: dict[str, Any],
) -> None:
    (evidence_dir / "profile.json").write_text(
        json.dumps(_profile_payload(profile), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (evidence_dir / "adapter.json").write_text(
        json.dumps(_redacted_adapter(adapter), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_delegation_json(
    evidence_dir: Path,
    delegation: SubagentDelegation,
) -> None:
    (evidence_dir / "delegation.json").write_text(
        json.dumps(_delegation_payload(delegation), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _delegation_payload(delegation: SubagentDelegation) -> dict[str, Any]:
    return asdict(delegation)


def _profile_payload(profile: AgentProfile) -> dict[str, Any]:
    payload = asdict(profile)
    payload["adapter_config_json"] = _redacted_adapter(profile.adapter_config_json)
    return payload


def _redacted_adapter(adapter: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in adapter.items()
        if key not in {"env", "token", "api_key", "secret", "password"}
    }


def _failure_class(message: str) -> str:
    if "no executor adapter configured" in message:
        return "missing adapter config"
    if "unsafe adapter command" in message:
        return "unsafe adapter command"
    if "expected schema" in message:
        return "schema validation failed"
    if "forbidden actions" in message:
        return "forbidden action claimed"
    if "missing structured_output" in message:
        return "malformed output envelope"
    if "result_summary" in message:
        return "malformed output envelope"
    return "delegation execution failed"


def _timeout_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value
