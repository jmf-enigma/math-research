#!/usr/bin/env python3
"""Record and boundedly replay proof-relevant computational artifacts."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import uuid
from pathlib import Path
from typing import Any

from proof_runtime import (
    append_record,
    atomic_write_json,
    canonical_json,
    ensure_runtime,
    iter_channel,
    project_path,
    runtime_dir,
    sha256_file,
    sha256_text,
    utc_now,
)


RESULT_KINDS = {
    "numerical-evidence": "conjecture-only",
    "exact-counterexample": "refutation-candidate",
    "symbolic-identity": "lemma-candidate",
    "condition-set": "theorem-repair-candidate",
    "solver-certificate": "certificate-candidate",
    "formal-certificate": "formal-local-candidate",
    "other": "unclassified-evidence",
}
RESULT_KINDS_REQUIRING_EXACT_STDOUT = {
    "exact-counterexample",
    "symbolic-identity",
    "condition-set",
    "solver-certificate",
}
COMPARE_MODES = {"exit-only", "stdout-exact"}
ALLOWED_EXECUTABLES = {
    "codex-wmath",
    "wolframscript",
    "codex-math-python",
    "codex-sage",
    "codex-mathlib-lean",
}
INLINE_CODE_FLAGS = {"-c", "-code", "--code", "--eval", "-e"}
SCRIPT_SUFFIXES = {".lean", ".py", ".sage", ".wl", ".wls"}
MAX_EXECUTABLE_HASH_BYTES = 32 * 1024 * 1024
MAX_INPUT_BYTES = 8 * 1024 * 1024
MAX_EXPECTED_OUTPUT_BYTES = 4 * 1024 * 1024
MAX_CAPTURE_BYTES = 4 * 1024 * 1024


def project_local_path(project: Path, raw: str | Path) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = project / candidate
    candidate = candidate.resolve()
    if not candidate.is_relative_to(project):
        raise ValueError(f"path must remain inside the proof project: {candidate}")
    return candidate


def relative_to_project(project: Path, path: Path) -> str:
    return path.resolve().relative_to(project).as_posix()


def parse_command(raw: str) -> list[str]:
    payload = json.loads(raw)
    if not isinstance(payload, list) or not payload or not all(isinstance(item, str) for item in payload):
        raise ValueError("--command-json must be a nonempty JSON array of strings")
    executable = Path(payload[0]).name
    if executable not in ALLOWED_EXECUTABLES:
        raise ValueError(
            f"replay executable {executable!r} is not allowed; choose from "
            + ", ".join(sorted(ALLOWED_EXECUTABLES))
        )
    forbidden = sorted(flag for flag in payload[1:] if flag in INLINE_CODE_FLAGS)
    if forbidden:
        raise ValueError(
            "inline code is not replayable; put the computation in a recorded project-local "
            f"script instead (forbidden flags: {', '.join(forbidden)})"
        )
    return payload


def executable_descriptor(project: Path, command: list[str]) -> dict[str, Any]:
    raw = command[0]
    resolved_raw = raw if Path(raw).is_absolute() else shutil.which(raw)
    if not resolved_raw:
        raise ValueError(f"replay executable not found on PATH: {raw}")
    resolved = Path(resolved_raw).expanduser().resolve()
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError(f"replay executable is not an executable file: {resolved}")
    if resolved.is_relative_to(project):
        raise ValueError("replay executable must be installed outside the proof project")
    stat = resolved.stat()
    return {
        "name": resolved.name,
        "path": str(resolved),
        "bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256_file(resolved) if stat.st_size <= MAX_EXECUTABLE_HASH_BYTES else None,
    }


def validate_command_inputs(
    project: Path,
    cwd: Path,
    command: list[str],
    input_files: list[dict[str, Any]],
) -> None:
    if not isinstance(input_files, list) or not all(
        isinstance(descriptor, dict)
        and isinstance(descriptor.get("path"), str)
        and isinstance(descriptor.get("sha256"), str)
        and isinstance(descriptor.get("bytes"), int)
        for descriptor in input_files
    ):
        raise ValueError("artifact input descriptors are invalid")
    if not input_files:
        raise ValueError("record at least one project-local input script with --input")
    recorded_paths = {project_local_path(project, item["path"]) for item in input_files}
    script_paths = {path for path in recorded_paths if path.suffix.lower() in SCRIPT_SUFFIXES}
    if not script_paths:
        raise ValueError(
            "at least one recorded input must be a .py, .wl, .wls, .sage, or .lean script"
        )
    command_paths: set[Path] = set()
    command_files: set[Path] = set()
    for item in command[1:]:
        if item.startswith("--") and "=" in item:
            item = item.split("=", 1)[1]
        elif item.startswith("-"):
            continue
        candidate = Path(item).expanduser()
        if not candidate.is_absolute():
            candidate = cwd / candidate
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.is_relative_to(project):
            command_paths.add(resolved)
        if resolved.is_file() or resolved.suffix.lower() in SCRIPT_SUFFIXES:
            if not resolved.is_relative_to(project):
                raise ValueError(f"command file dependency must remain inside the proof project: {item}")
            command_files.add(resolved)
    if script_paths.isdisjoint(command_paths):
        raise ValueError(
            "the command must name at least one recorded project-local script; inline expressions "
            "and unrecorded scripts are rejected"
        )
    unrecorded = command_files - recorded_paths
    if unrecorded:
        paths = ", ".join(sorted(relative_to_project(project, path) for path in unrecorded))
        raise ValueError(f"command file dependencies must be recorded with --input: {paths}")


def normalize_stdout(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def artifact_root(project: Path) -> Path:
    return runtime_dir(project) / "computation_artifacts"


def artifact_path(project: Path, artifact_id_or_path: str) -> Path:
    direct = Path(artifact_id_or_path).expanduser()
    if direct.is_absolute() or "/" in artifact_id_or_path:
        candidate = project_local_path(project, direct)
        if candidate.is_dir():
            candidate = candidate / "artifact.json"
    else:
        if not re.fullmatch(r"comp-[0-9a-f]{10}-[0-9a-f]{8}", artifact_id_or_path):
            raise ValueError(f"invalid computation artifact id: {artifact_id_or_path}")
        candidate = artifact_root(project) / artifact_id_or_path / "artifact.json"
    if not candidate.is_file():
        raise ValueError(f"computation artifact not found: {candidate}")
    return candidate


def load_artifact(project: Path, artifact_id_or_path: str) -> tuple[Path, dict[str, Any]]:
    path = artifact_path(project, artifact_id_or_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError(f"unsupported computation artifact: {path}")
    required_strings = [
        "artifact_id",
        "claim_id",
        "local_claim",
        "project_claim_sha256",
        "backend",
        "backend_version",
        "result_kind",
        "evidentiary_status",
        "comparison",
        "proof_translation",
        "spec_sha256",
    ]
    if any(not isinstance(payload.get(field), str) for field in required_strings):
        raise ValueError(f"computation artifact has invalid required fields: {path}")
    if payload["result_kind"] not in RESULT_KINDS or payload["comparison"] not in COMPARE_MODES:
        raise ValueError(f"computation artifact has invalid result or comparison type: {path}")
    if not isinstance(payload.get("replays"), list):
        raise ValueError(f"computation artifact has invalid replay history: {path}")
    return path, payload


def file_descriptor(project: Path, raw: str) -> dict[str, Any]:
    path = project_local_path(project, raw)
    if not path.is_file():
        raise ValueError(f"artifact file not found: {path}")
    return {
        "path": relative_to_project(project, path),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def record_artifact(args: argparse.Namespace) -> dict[str, Any]:
    project = project_path(args.project)
    state = ensure_runtime(project)
    cwd = project_local_path(project, args.cwd)
    if not cwd.is_dir():
        raise ValueError(f"replay working directory not found: {cwd}")
    input_files = [file_descriptor(project, raw) for raw in args.input]
    if sum(descriptor["bytes"] for descriptor in input_files) > MAX_INPUT_BYTES:
        raise ValueError("recorded computation inputs exceed the 8 MiB limit")
    command = parse_command(args.command_json)
    validate_command_inputs(project, cwd, command, input_files)
    executable = executable_descriptor(project, command)
    if not args.backend_version.strip():
        raise ValueError("--backend-version must be nonempty")
    for name, value in [
        ("--claim-id", args.claim_id),
        ("--local-claim", args.local_claim),
        ("--backend", args.backend),
        ("--proof-translation", args.proof_translation),
    ]:
        if not value.strip():
            raise ValueError(f"{name} must be nonempty")
    expected_output = file_descriptor(project, args.expected_output) if args.expected_output else None
    if args.compare == "stdout-exact" and expected_output is None:
        raise ValueError("--compare stdout-exact requires --expected-output")
    if args.result_kind in RESULT_KINDS_REQUIRING_EXACT_STDOUT and args.compare != "stdout-exact":
        raise ValueError(
            f"{args.result_kind} requires --compare stdout-exact and a canonical expected output; "
            "exit-only shows process success, not mathematical agreement"
        )
    if expected_output and expected_output["bytes"] > MAX_EXPECTED_OUTPUT_BYTES:
        raise ValueError("expected output exceeds the 4 MiB comparison limit")

    now = utc_now()
    identity = {
        "claim_id": args.claim_id,
        "local_claim": args.local_claim,
        "project_claim_sha256": state["claim_sha256"],
        "backend": args.backend,
        "backend_version": args.backend_version,
        "result_kind": args.result_kind,
        "command": command,
        "executable": executable,
        "inputs": input_files,
    }
    artifact_id = f"comp-{sha256_text(canonical_json(identity))[:10]}-{uuid.uuid4().hex[:8]}"
    directory = artifact_root(project) / artifact_id
    directory.mkdir(parents=True, exist_ok=False)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "artifact_id": artifact_id,
        "claim_id": args.claim_id,
        "local_claim": args.local_claim,
        "project_claim_sha256": state["claim_sha256"],
        "assumptions": args.assumption,
        "backend": args.backend,
        "backend_version": args.backend_version,
        "result_kind": args.result_kind,
        "evidentiary_status": RESULT_KINDS[args.result_kind],
        "command": command,
        "executable": executable,
        "cwd": relative_to_project(project, cwd),
        "input_files": input_files,
        "expected_exit_code": args.expected_exit_code,
        "comparison": args.compare,
        "comparison_strength": (
            "mathematical-output" if args.compare == "stdout-exact" else "process-exit-only"
        ),
        "expected_output": expected_output,
        "proof_translation": args.proof_translation,
        "limitations": args.limitation,
        "created_at_utc": now,
        "replay_status": "not-run",
        "replays": [],
    }
    immutable_spec = {
        key: value for key, value in payload.items() if key not in {"replay_status", "replays"}
    }
    payload["spec_sha256"] = sha256_text(canonical_json(immutable_spec))
    path = directory / "artifact.json"
    atomic_write_json(path, payload)
    append_record(
        project,
        "computations",
        {
            "event_type": "computation_recorded",
            "artifact_id": artifact_id,
            "artifact_path": relative_to_project(project, path),
            "claim_id": args.claim_id,
            "backend": args.backend,
            "result_kind": args.result_kind,
            "evidentiary_status": payload["evidentiary_status"],
            "comparison_strength": payload["comparison_strength"],
            "spec_sha256": payload["spec_sha256"],
        },
    )
    return payload


def terminate_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except (ProcessLookupError, PermissionError, AttributeError):
        process.terminate()
    try:
        process.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, AttributeError):
        process.kill()
    try:
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        pass


def verify_inputs(project: Path, artifact: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    descriptors = artifact.get("input_files", [])
    if not isinstance(descriptors, list):
        return ["artifact input descriptors are invalid"]
    for descriptor in descriptors:
        if not isinstance(descriptor, dict) or not isinstance(descriptor.get("path"), str):
            errors.append("artifact input descriptor is invalid")
            continue
        try:
            path = project_local_path(project, descriptor["path"])
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not path.is_file():
            errors.append(f"missing input: {descriptor['path']}")
        elif sha256_file(path) != descriptor.get("sha256"):
            errors.append(f"input sha256 changed: {descriptor['path']}")
    expected = artifact.get("expected_output")
    if expected is not None:
        if not isinstance(expected, dict) or not isinstance(expected.get("path"), str):
            errors.append("expected output descriptor is invalid")
        else:
            try:
                expected_path = project_local_path(project, expected["path"])
            except ValueError as exc:
                errors.append(str(exc))
            else:
                if not expected_path.is_file() or sha256_file(expected_path) != expected.get("sha256"):
                    errors.append("expected output file changed or is missing")
    return errors


def verify_artifact_spec(project: Path, artifact: dict[str, Any]) -> list[str]:
    artifact_id = artifact.get("artifact_id")
    expected = artifact.get("spec_sha256")
    immutable_spec = {
        key: value
        for key, value in artifact.items()
        if key not in {"spec_sha256", "replay_status", "replays"}
    }
    actual = sha256_text(canonical_json(immutable_spec))
    errors: list[str] = []
    if not isinstance(expected, str) or expected != actual:
        errors.append("computation artifact specification hash mismatch")
    recorded_hashes = {
        entry.get("record", {}).get("spec_sha256")
        for entry in iter_channel(project, "computations")
        if entry.get("record", {}).get("event_type") == "computation_recorded"
        and entry.get("record", {}).get("artifact_id") == artifact_id
    }
    if recorded_hashes != {expected}:
        errors.append("computation artifact specification does not match its recorded event")
    return errors


def verify_executable(project: Path, artifact: dict[str, Any]) -> tuple[Path | None, list[str]]:
    descriptor = artifact.get("executable")
    if not isinstance(descriptor, dict) or not isinstance(descriptor.get("path"), str):
        return None, ["missing executable descriptor"]
    path = Path(descriptor["path"]).expanduser().resolve()
    errors: list[str] = []
    if not path.is_file() or not os.access(path, os.X_OK):
        return None, [f"recorded executable is unavailable: {path}"]
    if path.is_relative_to(project):
        errors.append("recorded executable is inside the proof project")
    stat = path.stat()
    if stat.st_size != descriptor.get("bytes") or stat.st_mtime_ns != descriptor.get("mtime_ns"):
        errors.append("recorded executable metadata changed")
    expected_hash = descriptor.get("sha256")
    if expected_hash and sha256_file(path) != expected_hash:
        errors.append("recorded executable sha256 changed")
    return path, errors


def audit_artifact(project_raw: str | Path, artifact_id_or_path: str) -> dict[str, Any]:
    """Check that a recorded pass is still present, internally consistent, and replayable."""
    project = project_path(project_raw)
    state = ensure_runtime(project)
    try:
        path, artifact = load_artifact(project, artifact_id_or_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "artifact_id": artifact_id_or_path,
            "claim_id": None,
            "valid": False,
            "status": "invalid",
            "latest_replay_id": None,
            "errors": [str(exc)],
            "warnings": [],
            "claim_scope_sha256": None,
        }

    errors = verify_inputs(project, artifact)
    spec_errors = verify_artifact_spec(project, artifact)
    errors.extend(spec_errors)
    scope = {key: artifact.get(key) for key in (
        "project_claim_sha256", "claim_id", "local_claim", "assumptions", "result_kind", "comparison",
    )}
    claim_scope_sha256 = sha256_text(canonical_json(scope)) if not spec_errors else None
    try:
        command = parse_command(json.dumps(artifact.get("command")))
        cwd = project_local_path(project, artifact.get("cwd", "."))
        validate_command_inputs(project, cwd, command, artifact.get("input_files", []))
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    if artifact.get("project_claim_sha256") != state["claim_sha256"]:
        errors.append("project claim changed after the computation was recorded")
    try:
        _, executable_errors = verify_executable(project, artifact)
    except OSError as exc:
        executable_errors = [f"could not inspect the recorded executable: {exc}"]
    errors.extend(executable_errors)

    artifact_id = artifact["artifact_id"]
    replay_events = [
        entry.get("record", {})
        for entry in iter_channel(project, "computations")
        if entry.get("record", {}).get("event_type") == "computation_replayed"
        and entry.get("record", {}).get("artifact_id") == artifact_id
    ]
    latest_replay_event = replay_events[-1] if replay_events else None
    replays = artifact.get("replays", [])
    latest = replays[-1] if replays and isinstance(replays[-1], dict) else None
    latest_replay_id = latest.get("replay_id") if latest else None
    warnings: list[str] = []
    stdout_path: Path | None = None

    if artifact.get("replay_status") != "passed":
        errors.append("latest computation replay is not passed")
    if latest is None:
        errors.append("computation artifact has no replay details")
    else:
        if latest.get("status") != "passed":
            errors.append("latest replay detail is not passed")
        if latest_replay_event is None:
            errors.append("latest replay has no matching runtime event")
        elif (
            latest_replay_event.get("replay_id") != latest_replay_id
            or latest_replay_event.get("status") != "passed"
        ):
            errors.append("latest replay detail does not match the latest runtime event")
        if latest.get("timed_out"):
            errors.append("latest replay timed out")
        if latest.get("return_code") != artifact.get("expected_exit_code", 0):
            errors.append("latest replay return code does not match the recorded expectation")
        if latest.get("input_errors"):
            errors.append("latest replay recorded input errors")
        if latest.get("output_errors"):
            errors.append("latest replay recorded output errors")

        expected_replay_dir = path.parent / "replays" / str(latest_replay_id)
        for stream in ("stdout", "stderr"):
            raw_path = latest.get(f"{stream}_path")
            expected_hash = latest.get(f"{stream}_sha256")
            if not isinstance(raw_path, str) or not isinstance(expected_hash, str):
                errors.append(f"latest replay has an invalid {stream} descriptor")
                continue
            try:
                stream_path = project_local_path(project, raw_path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if stream_path.parent != expected_replay_dir or stream_path.name != f"{stream}.txt":
                errors.append(f"latest replay {stream} path is outside its replay directory")
                continue
            if not stream_path.is_file():
                errors.append(f"latest replay {stream} file is missing")
                continue
            if sha256_file(stream_path) != expected_hash:
                errors.append(f"latest replay {stream} hash changed")
                continue
            if stream == "stdout":
                stdout_path = stream_path
            elif stream_path.stat().st_size:
                warnings.append("latest replay stderr is nonempty; confirm it is expected")

    if artifact.get("comparison") == "stdout-exact" and stdout_path is not None:
        expected = artifact.get("expected_output") or {}
        try:
            expected_path = project_local_path(project, expected.get("path", ""))
            actual_text = stdout_path.read_text(encoding="utf-8")
            expected_text = expected_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"could not recheck exact stdout: {exc}")
        else:
            if normalize_stdout(actual_text) != normalize_stdout(expected_text):
                errors.append("latest replay stdout no longer matches the canonical expected output")

    errors = list(dict.fromkeys(errors))
    warnings = list(dict.fromkeys(warnings))
    return {
        "artifact_id": artifact_id,
        "claim_id": artifact["claim_id"],
        "valid": not errors,
        "status": "valid" if not errors else "invalid",
        "latest_replay_id": latest_replay_id,
        "errors": errors,
        "warnings": warnings,
        "claim_scope_sha256": claim_scope_sha256,
    }


def supersede_artifact(args: argparse.Namespace) -> dict[str, Any]:
    project = project_path(args.project)
    ensure_runtime(project)
    if args.artifact == args.replacement:
        raise ValueError("an artifact cannot supersede itself")
    reason = args.reason.strip()
    if not reason:
        raise ValueError("--reason must be nonempty")

    recorded_ids = {
        entry.get("record", {}).get("artifact_id")
        for entry in iter_channel(project, "computations")
        if entry.get("record", {}).get("event_type") == "computation_recorded"
    }
    if args.artifact not in recorded_ids:
        raise ValueError(f"cannot supersede an unrecorded artifact: {args.artifact}")
    replacement_audit = audit_artifact(project, args.replacement)
    if not replacement_audit["valid"]:
        details = "; ".join(replacement_audit["errors"])
        raise ValueError(f"replacement artifact is not currently valid: {details}")
    if args.artifact == replacement_audit["artifact_id"]:
        raise ValueError("an artifact cannot supersede itself")
    source_audit = audit_artifact(project, args.artifact)
    if (not source_audit.get("claim_scope_sha256")
        or source_audit["claim_scope_sha256"] != replacement_audit.get("claim_scope_sha256")):
        raise ValueError("replacement must have the same recorded local claim, assumptions, and evidence scope")

    record = {
        "event_type": "computation_superseded",
        "artifact_id": args.artifact,
        "replacement_artifact_id": replacement_audit["artifact_id"],
        "replacement_claim_id": replacement_audit["claim_id"],
        "claim_scope_sha256": source_audit["claim_scope_sha256"],
        "reason": reason,
    }
    append_record(project, "computations", record)
    return record


def replay_artifact(args: argparse.Namespace) -> dict[str, Any]:
    project = project_path(args.project)
    state = ensure_runtime(project)
    path, artifact = load_artifact(project, args.artifact)
    command = artifact.get("command")
    if not isinstance(command, list):
        raise ValueError("artifact command is missing or invalid")
    parse_command(json.dumps(command))
    cwd = project_local_path(project, artifact.get("cwd", "."))
    validate_command_inputs(project, cwd, command, artifact.get("input_files", []))

    replay_id = f"replay-{uuid.uuid4().hex}"
    replay_dir = path.parent / "replays" / replay_id
    replay_dir.mkdir(parents=True, exist_ok=False)
    started = utc_now()
    input_errors = verify_inputs(project, artifact)
    if artifact["project_claim_sha256"] != state["claim_sha256"]:
        input_errors.append("project claim changed after the computation was recorded")
    input_errors.extend(verify_artifact_spec(project, artifact))
    executable, executable_errors = verify_executable(project, artifact)
    input_errors.extend(executable_errors)
    timed_out = False
    return_code: int | None = None
    output_errors: list[str] = []
    stdout_path = replay_dir / "stdout.txt"
    stderr_path = replay_dir / "stderr.txt"
    stdout_path.write_bytes(b"")
    stderr_path.write_bytes(b"")

    if input_errors:
        status = "input-changed"
    else:
        execution_command = [str(executable), *command[1:]]
        with stdout_path.open("wb") as stdout_handle, stderr_path.open("wb") as stderr_handle:
            process = subprocess.Popen(
                execution_command,
                cwd=cwd,
                stdout=stdout_handle,
                stderr=stderr_handle,
                start_new_session=True,
            )
            try:
                process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                terminate_process_group(process)
        return_code = process.returncode
        if stdout_path.stat().st_size > MAX_CAPTURE_BYTES:
            output_errors.append("stdout exceeds the 4 MiB capture limit")
        if stderr_path.stat().st_size > MAX_CAPTURE_BYTES:
            output_errors.append("stderr exceeds the 4 MiB capture limit")
        if timed_out:
            status = "timeout"
        elif output_errors:
            status = "output-too-large"
        elif return_code != artifact.get("expected_exit_code", 0):
            status = "failed"
        elif artifact.get("comparison") == "stdout-exact":
            expected = artifact.get("expected_output") or {}
            expected_path = project_local_path(project, expected.get("path", ""))
            try:
                actual_text = stdout_path.read_text(encoding="utf-8")
                expected_text = expected_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                output_errors.append("stdout or expected output is not UTF-8 text")
                status = "failed"
            else:
                status = (
                    "passed"
                    if normalize_stdout(actual_text) == normalize_stdout(expected_text)
                    else "failed"
                )
        else:
            status = "passed"

    replay = {
        "replay_id": replay_id,
        "started_at_utc": started,
        "finished_at_utc": utc_now(),
        "status": status,
        "timeout_seconds": args.timeout,
        "timed_out": timed_out,
        "return_code": return_code,
        "input_errors": input_errors,
        "output_errors": output_errors,
        "stdout_path": relative_to_project(project, stdout_path),
        "stdout_sha256": sha256_file(stdout_path),
        "stderr_path": relative_to_project(project, stderr_path),
        "stderr_sha256": sha256_file(stderr_path),
    }
    artifact.setdefault("replays", []).append(replay)
    artifact["replay_status"] = status
    atomic_write_json(path, artifact)
    append_record(
        project,
        "computations",
        {
            "event_type": "computation_replayed",
            "artifact_id": artifact["artifact_id"],
            "replay_id": replay_id,
            "status": status,
            "result_kind": artifact["result_kind"],
            "return_code": return_code,
            "input_errors": input_errors,
            "output_errors": output_errors,
        },
    )
    return replay


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    record_parser = subparsers.add_parser("record", help="record a replayable computation")
    record_parser.add_argument("project")
    record_parser.add_argument("--claim-id", required=True)
    record_parser.add_argument("--local-claim", required=True)
    record_parser.add_argument("--assumption", action="append", default=[])
    record_parser.add_argument("--backend", required=True)
    record_parser.add_argument("--backend-version", required=True)
    record_parser.add_argument("--result-kind", choices=sorted(RESULT_KINDS), required=True)
    record_parser.add_argument("--command-json", required=True)
    record_parser.add_argument("--cwd", default=".")
    record_parser.add_argument("--input", action="append", default=[])
    record_parser.add_argument("--expected-exit-code", type=int, default=0)
    record_parser.add_argument("--compare", choices=sorted(COMPARE_MODES), default="exit-only")
    record_parser.add_argument("--expected-output")
    record_parser.add_argument("--proof-translation", required=True)
    record_parser.add_argument("--limitation", action="append", default=[])

    replay_parser = subparsers.add_parser("replay", help="replay a recorded computation")
    replay_parser.add_argument("project")
    replay_parser.add_argument("artifact", help="artifact id or project-local artifact.json path")
    replay_parser.add_argument("--timeout", type=int, default=120)

    show_parser = subparsers.add_parser("show", help="show a computation artifact")
    show_parser.add_argument("project")
    show_parser.add_argument("artifact")

    audit_parser = subparsers.add_parser(
        "audit", help="audit whether a recorded passed artifact is still valid"
    )
    audit_parser.add_argument("project")
    audit_parser.add_argument("artifact")

    supersede_parser = subparsers.add_parser(
        "supersede", help="replace a stale artifact with an explicitly audited successor"
    )
    supersede_parser.add_argument("project")
    supersede_parser.add_argument("artifact", help="stale artifact id")
    supersede_parser.add_argument("--replacement", required=True, help="valid replacement artifact id")
    supersede_parser.add_argument("--reason", required=True)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "record":
            result = record_artifact(args)
        elif args.command == "replay":
            if args.timeout <= 0:
                raise ValueError("--timeout must be positive")
            result = replay_artifact(args)
        elif args.command == "audit":
            result = audit_artifact(args.project, args.artifact)
        elif args.command == "supersede":
            result = supersede_artifact(args)
        else:
            project = project_path(args.project)
            ensure_runtime(project)
            _, result = load_artifact(project, args.artifact)
    except (OSError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.command == "replay" and result.get("status") != "passed":
        return 1
    if args.command == "audit" and not result.get("valid"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
