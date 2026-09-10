#!/usr/bin/env python3
"""Maintain compact, typed runtime state for a theory-proof project."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
import uuid
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
RUNTIME_DIRNAME = ".proof_runtime"
CHANNELS = (
    "attempts",
    "proof_nodes",
    "counterexamples",
    "computations",
    "verification_reports",
    "events",
)
PROOF_STATUSES = {
    "unresolved",
    "conjecture",
    "counterexample-tested",
    "refuted",
    "lemma-conditional",
    "human-proof",
    "referee-accepted",
    "tool-checked",
    "formalized-local",
    "formalized-complete",
}
PROJECT_MODES = {"project", "recovery", "discovery"}
REQUIRED_RECORD_FIELDS = {
    "attempts": ("event_type", "route_family", "target_lemma", "outcome"),
    "proof_nodes": ("event_type", "node_id", "status"),
    "counterexamples": ("event_type", "claim_id", "status"),
    "computations": ("event_type", "artifact_id"),
    "verification_reports": ("event_type", "run_id", "verdict"),
    "events": ("event_type",),
}
CHECKER_GUIDED_ATTEMPT_FIELDS = (
    "feedback_kind",
    "checker_backend",
    "diagnostic",
    "local_state",
    "diagnostic_site",
    "inferred_root_cause",
    "failure_class",
    "diagnosis",
    "repair",
    "replay_result",
)
BRIEF_FIELDS = {
    "attempts": (
        "event_type",
        "route_family",
        "target_lemma",
        "outcome",
        "failure_witness",
        "feedback_kind",
        "checker_backend",
        "diagnostic",
        "local_state",
        "diagnostic_site",
        "diagnostic_fingerprint",
        "inferred_root_cause",
        "failure_class",
        "diagnosis",
        "repair",
        "replay_result",
        "proof_state_delta",
    ),
    "proof_nodes": ("event_type", "node_id", "status", "statement"),
    "counterexamples": ("event_type", "claim_id", "status", "witness"),
    "computations": (
        "event_type",
        "artifact_id",
        "claim_id",
        "result_kind",
        "evidentiary_status",
        "status",
    ),
    "verification_reports": (
        "event_type",
        "run_id",
        "module_id",
        "candidate_proof_source",
        "verdict",
        "failure_kind",
        "claim_fidelity_status",
        "assumption_coverage_status",
        "first_error",
        "repair_hints",
    ),
    "events": (
        "event_type",
        "run_id",
        "artifact_id",
        "changes",
        "reason",
        "old_claim_sha256",
        "new_claim_sha256",
    ),
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_path(raw: str | Path) -> Path:
    project = Path(raw).expanduser().resolve()
    if not project.is_dir():
        raise ValueError(f"proof project directory not found: {project}")
    return project


def runtime_dir(project: str | Path) -> Path:
    return project_path(project) / RUNTIME_DIRNAME


def state_path(project: str | Path) -> Path:
    return runtime_dir(project) / "state.json"


def channel_path(project: str | Path, channel: str) -> Path:
    if channel not in CHANNELS:
        raise ValueError(f"unknown runtime channel {channel!r}; choose from {', '.join(CHANNELS)}")
    return runtime_dir(project) / "channels" / f"{channel}.jsonl"


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def read_state(project: str | Path) -> dict[str, Any]:
    path = state_path(project)
    if not path.is_file():
        raise ValueError(f"runtime is not initialized: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported runtime state: {path}")
    claim = payload.get("claim")
    if not isinstance(claim, str) or payload.get("claim_sha256") != sha256_text(claim):
        raise ValueError(f"runtime claim hash mismatch: {path}")
    if payload.get("mode") not in PROJECT_MODES or payload.get("proof_status") not in PROOF_STATUSES:
        raise ValueError(f"invalid runtime mode or proof status: {path}")
    if not isinstance(payload.get("claim_revision", 0), int):
        raise ValueError(f"invalid runtime claim revision: {path}")
    return payload


def read_project_identity(project: str | Path) -> tuple[str, str]:
    root = project_path(project)
    routing_claim: str | None = None
    claim_file_claim: str | None = None
    mode = "project"
    routing_path = root / "routing.json"
    if routing_path.is_file():
        payload = json.loads(routing_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            claim = payload.get("claim")
            if isinstance(claim, str) and claim.strip():
                routing_claim = claim.strip()
            candidate_mode = payload.get("mode", "project")
            mode = candidate_mode if candidate_mode in PROJECT_MODES else "project"

    claim_path = root / "claim.md"
    if claim_path.is_file():
        text = claim_path.read_text(encoding="utf-8")
        match = re.search(r"^# Claim\s*\n(?P<body>.*?)(?=^##\s|\Z)", text, flags=re.M | re.S)
        if match and match.group("body").strip():
            claim_file_claim = match.group("body").strip()
    if routing_claim and claim_file_claim and routing_claim != claim_file_claim:
        raise ValueError("routing.json and claim.md contain different theorem statements")
    claim = routing_claim or claim_file_claim
    if claim:
        return claim, mode
    raise ValueError("cannot infer the proof claim from routing.json or claim.md")


def read_project_status_hint(project: str | Path) -> str | None:
    routing_path = project_path(project) / "routing.json"
    if not routing_path.is_file():
        return None
    payload = json.loads(routing_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return None
    for field in ("status", "proof_status"):
        value = payload.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()[:240]
    return None


def _append_envelope(project: Path, channel: str, envelope: dict[str, Any]) -> None:
    path = channel_path(project, channel)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(envelope, ensure_ascii=False, sort_keys=True) + "\n")


def validate_record(channel: str, record: dict[str, Any]) -> None:
    missing = [
        field
        for field in REQUIRED_RECORD_FIELDS[channel]
        if field not in record or record[field] in (None, "")
    ]
    if missing:
        raise ValueError(f"{channel} record is missing required fields: {', '.join(missing)}")
    nonstrings = [
        field for field in REQUIRED_RECORD_FIELDS[channel] if not isinstance(record[field], str)
    ]
    if nonstrings:
        raise ValueError(f"{channel} record fields must be strings: {', '.join(nonstrings)}")
    if channel == "attempts":
        event_type = record.get("event_type", "")
        feedback_kind = record.get("feedback_kind")
        checker_guided = feedback_kind == "checker" or "checker" in event_type.lower()
        if checker_guided:
            checker_missing = [
                field
                for field in CHECKER_GUIDED_ATTEMPT_FIELDS
                if field not in record or record[field] in (None, "")
            ]
            if checker_missing:
                raise ValueError(
                    "checker-guided attempts record is missing required fields: "
                    + ", ".join(checker_missing)
                )
            checker_nonstrings = [
                field
                for field in CHECKER_GUIDED_ATTEMPT_FIELDS
                if not isinstance(record[field], str)
            ]
            if checker_nonstrings:
                raise ValueError(
                    "checker-guided attempts fields must be strings: "
                    + ", ".join(checker_nonstrings)
                )


def init_runtime(
    project: str | Path,
    claim: str,
    mode: str,
    *,
    project_status_hint: str | None = None,
) -> dict[str, Any]:
    root = project_path(project)
    claim = claim.strip()
    if not claim:
        raise ValueError("runtime claim must be nonempty")
    if mode not in PROJECT_MODES:
        raise ValueError(f"unknown project mode {mode!r}; choose from {', '.join(sorted(PROJECT_MODES))}")
    run_dir = root / RUNTIME_DIRNAME
    channels_dir = run_dir / "channels"
    channels_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "referee_runs").mkdir(exist_ok=True)
    (run_dir / "computation_artifacts").mkdir(exist_ok=True)
    for channel in CHANNELS:
        (channels_dir / f"{channel}.jsonl").touch(exist_ok=True)

    path = run_dir / "state.json"
    claim_hash = sha256_text(claim)
    if path.exists():
        state = read_state(root)
        if state.get("claim_sha256") != claim_hash:
            raise ValueError("runtime claim hash differs from the requested claim")
        return state

    now = utc_now()
    state = {
        "schema_version": SCHEMA_VERSION,
        "claim": claim,
        "claim_sha256": claim_hash,
        "claim_revision": 0,
        "mode": mode,
        "proof_status": "unresolved",
        "current_node": None,
        "last_decisive_artifact": None,
        "created_at_utc": now,
        "updated_at_utc": now,
    }
    if project_status_hint:
        state["project_status_hint"] = project_status_hint
        state["project_status_hint_evidence"] = "unverified-routing-metadata"
    atomic_write_json(path, state)
    init_record = {"event_type": "runtime_initialized", "mode": mode}
    if project_status_hint:
        init_record["project_status_hint"] = project_status_hint
    _append_envelope(
        root,
        "events",
        {
            "schema_version": SCHEMA_VERSION,
            "record_id": f"event-{uuid.uuid4().hex}",
            "timestamp_utc": now,
            "claim_sha256": claim_hash,
            "claim_revision": 0,
            "record_sha256": sha256_text(canonical_json(init_record)),
            "record": init_record,
        },
    )
    return state


def ensure_runtime(project: str | Path) -> dict[str, Any]:
    root = project_path(project)
    path = root / RUNTIME_DIRNAME / "state.json"
    project_claim, mode = read_project_identity(root)
    project_status_hint = read_project_status_hint(root)
    if not path.is_file():
        return init_runtime(
            root,
            project_claim,
            mode,
            project_status_hint=project_status_hint,
        )
    state = read_state(root)
    if state["claim_sha256"] != sha256_text(project_claim):
        raise ValueError(
            "project claim differs from runtime state; run `proof_runtime.py revise-claim PROJECT "
            "--reason REASON` after updating routing.json or claim.md"
        )
    if project_status_hint and "project_status_hint" not in state:
        state["project_status_hint"] = project_status_hint
        state["project_status_hint_evidence"] = "unverified-routing-metadata"
        state["updated_at_utc"] = utc_now()
        atomic_write_json(path, state)
        _append_record(
            root,
            "events",
            {
                "event_type": "project_status_hint_imported",
                "project_status_hint": project_status_hint,
            },
        )
        state = read_state(root)
    return state


def _append_record(
    root: Path, channel: str, record: dict[str, Any],
    *, expected_claim: tuple[str, int] | None = None,
) -> dict[str, Any]:
    state = read_state(root)
    if expected_claim is not None and expected_claim != (
        state["claim_sha256"], state.get("claim_revision", 0)
    ):
        raise ValueError("the theorem changed before the prepared record could be appended")
    if channel not in CHANNELS:
        raise ValueError(f"unknown runtime channel {channel!r}; choose from {', '.join(CHANNELS)}")
    if not isinstance(record, dict):
        raise ValueError("record must be a JSON object")
    validate_record(channel, record)

    now = utc_now()
    record_hash = sha256_text(canonical_json(record))
    envelope = {
        "schema_version": SCHEMA_VERSION,
        "record_id": f"{channel}-{uuid.uuid4().hex}",
        "timestamp_utc": now,
        "claim_sha256": state["claim_sha256"],
        "claim_revision": state.get("claim_revision", 0),
        "record_sha256": record_hash,
        "record": record,
    }
    _append_envelope(root, channel, envelope)

    state = read_state(root)
    state["updated_at_utc"] = now
    atomic_write_json(state_path(root), state)
    return envelope


def append_record(
    project: str | Path,
    channel: str,
    record: dict[str, Any],
    *,
    expected_claim: tuple[str, int] | None = None,
) -> dict[str, Any]:
    root = project_path(project)
    ensure_runtime(root)
    return _append_record(root, channel, record, expected_claim=expected_claim)


def update_state(
    project: str | Path,
    *,
    proof_status: str | None = None,
    current_node: str | None = None,
    last_decisive_artifact: str | None = None,
    evidence_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    root = project_path(project)
    state = ensure_runtime(root)
    changes: dict[str, Any] = {}
    if evidence_summary is not None and state.get("evidence_summary") != evidence_summary:
        if not isinstance(evidence_summary, dict):
            raise ValueError("evidence_summary must be an object")
        changes["evidence_summary"] = evidence_summary
        state["evidence_summary"] = evidence_summary
    if proof_status is not None:
        if proof_status not in PROOF_STATUSES:
            raise ValueError(
                f"unknown proof status {proof_status!r}; choose from {', '.join(sorted(PROOF_STATUSES))}"
            )
        if state.get("proof_status") != proof_status:
            changes["proof_status"] = proof_status
            state["proof_status"] = proof_status
    if current_node is not None:
        value = current_node or None
        if state.get("current_node") != value:
            changes["current_node"] = value
            state["current_node"] = value
    if last_decisive_artifact is not None:
        value = last_decisive_artifact or None
        if state.get("last_decisive_artifact") != value:
            changes["last_decisive_artifact"] = value
            state["last_decisive_artifact"] = value
    if not changes:
        raise ValueError("state update does not change any field")
    state["updated_at_utc"] = utc_now()
    atomic_write_json(state_path(root), state)
    _append_record(root, "events", {"event_type": "state_updated", "changes": changes})
    return read_state(root)


def invalidate_acceptance(
    project: str | Path, reason: str, *, previous_result: dict[str, Any] | None = None,
    accepted_statuses: set[str] | None = None,
) -> dict[str, Any]:
    """Clear stale active acceptance while retaining its historical evidence."""
    root = project_path(project)
    state = ensure_runtime(root)
    eligible = accepted_statuses if accepted_statuses is not None else {
        "referee-accepted", "human-proof", "tool-checked", "formalized-local", "formalized-complete",
    }
    if state["proof_status"] not in eligible:
        return state
    previous_evidence = state.get("evidence_summary")
    previous_artifact = state.get("last_decisive_artifact")
    append_record(root, "events", {
        "event_type": "acceptance_invalidated",
        "reason": reason,
        "previous_result": previous_result,
        "previous_evidence_summary": previous_evidence,
        "previous_artifact": previous_artifact,
    })
    return update_state(
        root, proof_status="unresolved", current_node="pending verification",
        last_decisive_artifact="", evidence_summary={
            "disposition": "pending", "basis": reason,
            "previous_result": (previous_result or {}).get("artifact_descriptor"),
            "previous_artifact": previous_artifact,
            "human_reviewed": False, "formal_verification": False,
        },
    )


def revise_claim(project: str | Path, reason: str) -> dict[str, Any]:
    root = project_path(project)
    path = root / RUNTIME_DIRNAME / "state.json"
    if not path.is_file():
        return ensure_runtime(root)
    if not reason.strip():
        raise ValueError("claim revision requires a nonempty --reason")
    state = read_state(root)
    project_claim, _ = read_project_identity(root)
    new_hash = sha256_text(project_claim)
    if state["claim_sha256"] == new_hash:
        raise ValueError("project claim is unchanged")
    old_hash = state["claim_sha256"]
    state["claim"] = project_claim
    state["claim_sha256"] = new_hash
    state["claim_revision"] = state.get("claim_revision", 0) + 1
    state["proof_status"] = "unresolved"
    state["current_node"] = None
    state["last_decisive_artifact"] = None
    state.pop("evidence_summary", None)
    state["updated_at_utc"] = utc_now()
    atomic_write_json(state_path(root), state)
    _append_record(
        root,
        "events",
        {
            "event_type": "claim_revised",
            "old_claim_sha256": old_hash,
            "new_claim_sha256": new_hash,
            "reason": reason.strip(),
        },
    )
    return read_state(root)


def iter_channel(
    project: str | Path, channel: str, *, current_claim_only: bool = False
) -> Iterable[dict[str, Any]]:
    path = channel_path(project, channel)
    state = read_state(project) if current_claim_only else None
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON in {path} at line {line_number}") from exc
            if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
                raise ValueError(f"invalid runtime envelope in {path} at line {line_number}")
            record = payload.get("record")
            if not isinstance(record, dict):
                raise ValueError(f"missing runtime record in {path} at line {line_number}")
            validate_record(channel, record)
            if payload.get("record_sha256") != sha256_text(canonical_json(record)):
                raise ValueError(f"runtime record hash mismatch in {path} at line {line_number}")
            if state is not None:
                # Unversioned legacy records are usable only before the first theorem repair.
                revision = state.get("claim_revision", 0)
                if payload.get("claim_sha256") is None:
                    if revision != 0:
                        continue
                elif (
                    payload.get("claim_sha256") != state["claim_sha256"]
                    or payload.get("claim_revision") != revision
                ):
                    continue
            yield payload


def compact_value(value: Any, *, max_chars: int = 240) -> Any:
    if isinstance(value, str):
        return value if len(value) <= max_chars else value[: max_chars - 3] + "..."
    if isinstance(value, list):
        return [compact_value(item, max_chars=max_chars) for item in value[:3]]
    if isinstance(value, dict):
        return {
            str(key): compact_value(item, max_chars=max_chars)
            for key, item in list(value.items())[:6]
        }
    return value


def compact_envelope(channel: str, envelope: dict[str, Any]) -> dict[str, Any]:
    record = envelope.get("record", {})
    compact_record = {
        field: compact_value(record[field])
        for field in BRIEF_FIELDS[channel]
        if field in record
    }
    return {
        "record_id": envelope.get("record_id"),
        "timestamp_utc": envelope.get("timestamp_utc"),
        "record": compact_record,
    }


def runtime_brief(project: str | Path, limit: int = 2) -> dict[str, Any]:
    root = project_path(project)
    ensure_runtime(root)
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    recent: dict[str, list[dict[str, Any]]] = {}
    counts: dict[str, int] = {}
    for channel in CHANNELS:
        tail: deque[dict[str, Any]] = deque(maxlen=limit or 1)
        count = 0
        for entry in iter_channel(root, channel, current_claim_only=True):
            count += 1
            if limit:
                tail.append(compact_envelope(channel, entry))
        counts[channel] = count
        if limit:
            recent[channel] = list(tail)
    return {
        "project": str(root),
        "state": read_state(root),
        "counts": counts,
        "recent": recent,
    }


def brief_markdown(brief: dict[str, Any]) -> str:
    state = brief["state"]
    lines = [
        "# Proof Runtime Brief",
        "",
        f"- proof status: {state.get('proof_status')}",
        f"- current node: {state.get('current_node') or 'not set'}",
        f"- last decisive artifact: {state.get('last_decisive_artifact') or 'none'}",
        f"- updated: {state.get('updated_at_utc')}",
    ]
    if state.get("project_status_hint"):
        lines.append(f"- project status hint (unverified): {state['project_status_hint']}")
    lines.extend(["", "## Channel Counts", ""])
    for channel, count in brief["counts"].items():
        lines.append(f"- {channel}: {count}")
    lines.extend(["", "## Recent Decision-Relevant Records", ""])
    any_records = False
    for channel in CHANNELS:
        entries = brief["recent"].get(channel, [])
        if not entries:
            continue
        any_records = True
        lines.append(f"### {channel}")
        lines.append("")
        for entry in entries:
            lines.append(f"- `{entry.get('record_id', '')}`: {canonical_json(entry.get('record', {}))}")
        lines.append("")
    if not any_records:
        lines.append("No runtime records yet.")
    return "\n".join(lines).rstrip() + "\n"


def _load_record(args: argparse.Namespace) -> dict[str, Any]:
    if bool(args.record) == bool(args.record_file):
        raise ValueError("provide exactly one of --record or --record-file")
    raw = args.record if args.record else Path(args.record_file).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("record must decode to a JSON object")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="initialize typed runtime state")
    init_parser.add_argument("project")
    init_parser.add_argument("--claim", required=True)
    init_parser.add_argument("--mode", choices=sorted(PROJECT_MODES), default="project")

    ensure_parser = subparsers.add_parser(
        "ensure", help="initialize runtime state from an existing proof project when needed"
    )
    ensure_parser.add_argument("project")

    append_parser = subparsers.add_parser("append", help="append one typed runtime record")
    append_parser.add_argument("project")
    append_parser.add_argument("channel", choices=CHANNELS)
    append_parser.add_argument("--record")
    append_parser.add_argument("--record-file")

    set_parser = subparsers.add_parser("set", help="update the compact active state")
    set_parser.add_argument("project")
    set_parser.add_argument("--proof-status", choices=sorted(PROOF_STATUSES))
    set_parser.add_argument("--current-node")
    set_parser.add_argument("--last-decisive-artifact")

    revise_parser = subparsers.add_parser(
        "revise-claim", help="adopt the claim currently stored in routing.json or claim.md"
    )
    revise_parser.add_argument("project")
    revise_parser.add_argument("--reason", required=True)

    brief_parser = subparsers.add_parser("brief", help="show compact state and recent records")
    brief_parser.add_argument("project")
    brief_parser.add_argument("--limit", type=int, default=2)
    brief_parser.add_argument("--markdown", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "init":
            result = init_runtime(args.project, args.claim, args.mode)
        elif args.command == "ensure":
            result = ensure_runtime(args.project)
        elif args.command == "append":
            result = append_record(args.project, args.channel, _load_record(args))
        elif args.command == "set":
            result = update_state(
                args.project,
                proof_status=args.proof_status,
                current_node=args.current_node,
                last_decisive_artifact=args.last_decisive_artifact,
            )
        elif args.command == "revise-claim":
            result = revise_claim(args.project, args.reason)
        else:
            result = runtime_brief(args.project, args.limit)
            if args.markdown:
                print(brief_markdown(result), end="")
                return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
