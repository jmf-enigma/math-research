#!/usr/bin/env python3
"""Exchange stable proof nodes with Lean and record checker results."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from proof_runtime import (
    append_record,
    ensure_runtime,
    invalidate_acceptance,
    iter_channel,
    project_path,
    read_state,
    update_state,
)


SCHEMA_VERSION = 1
ROLES = ("local-lemma", "interface-theorem", "full-theorem")
TARGET_KINDS = ("theorem", "lemma")
FAILURE_STAGES = (
    "auto",
    "local-proof",
    "statement-fidelity",
    "mathematical",
    "assembly",
    "library-coverage",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_json(payload: dict[str, Any]) -> str:
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def bounded(text: str, limit: int = 12000) -> str:
    value = text.strip()
    if not value:
        return "not-reported"
    return value if len(value) <= limit else value[:limit] + "\n[truncated]"


def diagnostic_fingerprint(diagnostic: str) -> str:
    normalized = re.sub(r"\s+", " ", diagnostic.strip())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def slug(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return result or "node"


def inside_project(project: Path, raw: str | Path) -> tuple[Path, str]:
    candidate = Path(raw).expanduser()
    resolved = (project / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    try:
        relative = resolved.relative_to(project)
    except ValueError as exc:
        raise ValueError(f"path must stay inside the proof project: {raw}") from exc
    return resolved, relative.as_posix()


def statement_from_args(args: argparse.Namespace, project: Path) -> tuple[str, dict[str, str]]:
    if bool(args.statement) == bool(args.statement_file):
        raise ValueError("provide exactly one of --statement or --statement-file")
    statement = args.statement
    source = {"kind": "inline"}
    if args.statement_file:
        source_path, source_rel = inside_project(project, args.statement_file)
        if not source_path.is_file():
            raise ValueError(f"statement file not found: {source_path}")
        statement = source_path.read_text(encoding="utf-8")
        source = {
            "kind": "project-file",
            "path": source_rel,
            "sha256": sha256_file(source_path),
        }
    value = str(statement).strip()
    if not value:
        raise ValueError("Lean handoff statement must be nonempty")
    return value, source


def validate_statement_source(project: Path, node: dict[str, Any]) -> None:
    source = node.get("statement_source")
    if not isinstance(source, dict) or source.get("kind") not in {"inline", "project-file"}:
        raise ValueError("Lean handoff has no valid frozen statement source")
    if source["kind"] == "project-file":
        path, _ = inside_project(project, str(source.get("path", "")))
        if (
            not path.is_file()
            or sha256_file(path) != source.get("sha256")
            or path.read_text(encoding="utf-8").strip() != node.get("statement")
        ):
            raise ValueError("stale Lean handoff: the frozen statement source changed or is missing")


def target_binding(project: Path, packet: dict[str, Any]) -> dict[str, Any]:
    """Bind human fidelity/assembly gates to the actual project formal sources."""
    target = packet["lean_target"]
    lean_path, lean_rel = inside_project(project, str(target["file"]))
    files: dict[str, str] = {}
    # Local imports and project configuration can change a target's meaning even
    # when the final file does not. Package caches are audited as environment
    # dependencies; avoid walking their large generated trees on each local check.
    configuration = {"lean-toolchain", "lakefile.lean", "lakefile.toml", "lake-manifest.json"}
    for directory, dirs, names in os.walk(project):
        dirs[:] = [name for name in dirs if name not in {".git", ".proof_runtime", ".lake", "__pycache__"}]
        for name in names:
            if not name.endswith(".lean") and name not in configuration:
                continue
            path, relative = inside_project(project, Path(directory) / name)
            files[relative] = sha256_file(path)
    return {
        "lean_file": lean_rel,
        "lean_file_sha256": sha256_file(lean_path),
        "target_name": target["name"],
        "target_kind": target["kind"],
        "local_formal_files": files,
    }


def invalidate_completed_request(project: Path, request_relative: str, reason: str) -> None:
    """Revoke only completion supplied by the request being rechecked."""
    state = read_state(project)
    if state.get("proof_status") != "formalized-complete":
        return
    summary = state.get("evidence_summary")
    summary = summary if isinstance(summary, dict) else {}
    result_relative = summary.get("formal_result_path") or state.get("last_decisive_artifact")
    if not isinstance(result_relative, str):
        return
    result_path, _ = inside_project(project, result_relative)
    try:
        result = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        result = {}
    if not isinstance(result, dict) or result.get("request_path") != request_relative:
        return
    invalidate_acceptance(
        project,
        reason,
        previous_result=result,
        accepted_statuses={"formalized-complete"},
    )


def prepare(args: argparse.Namespace) -> int:
    project = project_path(args.project)
    ensure_runtime(project)
    state = read_state(project)
    statement, statement_source = statement_from_args(args, project)
    if args.role != "full-theorem" and not args.downstream_use.strip():
        raise ValueError("local and interface handoffs require --downstream-use")
    _, lean_file = inside_project(project, args.lean_file)
    handoff_id = f"lean-{slug(args.node_id)}-{uuid.uuid4().hex[:10]}"
    default_output = Path("lean") / "handoffs" / f"{handoff_id}.request.json"
    output_path, output_rel = inside_project(project, args.output or default_output)
    if output_path.exists():
        raise ValueError(f"handoff request already exists: {output_path}")

    packet: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "theory-to-lean",
        "handoff_id": handoff_id,
        "created_at_utc": utc_now(),
        "claim": state["claim"],
        "claim_sha256": state["claim_sha256"],
        "claim_revision": state.get("claim_revision", 0),
        "node": {
            "id": args.node_id,
            "role": args.role,
            "statement": statement,
            "statement_source": statement_source,
            "dependencies": args.dependency,
            "downstream_use": args.downstream_use,
            "expected_proof_method": args.expected_proof_method,
        },
        "lean_target": {
            "file": lean_file,
            "name": args.target_name,
            "kind": args.target_kind,
        },
        "fidelity": {
            "source_fragments": args.source_fragment,
            "allowed_axioms": args.allowed_axiom,
        },
        "request_status": "prepared",
    }

    acceptance_path: Path | None = None
    if args.role == "full-theorem":
        acceptance_path = output_path.with_name(output_path.name.replace(".request.json", ".acceptance.json"))
        _, acceptance_rel = inside_project(project, acceptance_path)
        packet["acceptance_report"] = acceptance_rel

    packet["packet_sha256"] = sha256_json(packet)
    if acceptance_path is not None:
        acceptance = {
            "schema_version": SCHEMA_VERSION,
            "packet_type": "lean-final-acceptance",
            "handoff_id": handoff_id,
            "claim_sha256": state["claim_sha256"],
            "request_packet_sha256": packet["packet_sha256"],
            "target_binding": (
                target_binding(project, packet)
                if (project / lean_file).is_file()
                else None
            ),
            "checks": {
                name: {"status": "not-audited", "evidence": ""}
                for name in (
                    "claim_fidelity",
                    "assumption_lineage",
                    "assembly_coverage",
                    "axiom_audit",
                )
            },
        }
        atomic_write_json(acceptance_path, acceptance)

    atomic_write_json(output_path, packet)
    append_record(
        project,
        "proof_nodes",
        {
            "event_type": "lean_handoff_prepared",
            "node_id": args.node_id,
            "status": "awaiting-formalization",
            "statement": statement,
            "handoff_id": handoff_id,
            "request_path": output_rel,
            "lean_target": f"{lean_file}::{args.target_name}:{args.target_kind}",
        },
    )
    append_record(
        project,
        "events",
        {
            "event_type": "lean_handoff_prepared",
            "handoff_id": handoff_id,
            "node_id": args.node_id,
            "request_path": output_rel,
        },
    )
    print(
        json.dumps(
            {"request_path": str(output_path), "packet": packet},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


def locate_lean_status(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
    else:
        codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
        path = codex_home / "skills" / "lean-theorem-formalizer" / "scripts" / "lean_status.py"
    if not path.is_file():
        raise ValueError(
            "lean_status.py not found; install lean-theorem-formalizer or pass --lean-status-script"
        )
    return path


def first_result(payload: dict[str, Any]) -> dict[str, Any]:
    results = payload.get("results")
    if not isinstance(results, list) or not results or not isinstance(results[0], dict):
        raise ValueError("lean_status.py returned no structured file result")
    return results[0]


def validate_checker_result(
    payload: dict[str, Any], lean_path: Path, target_name: str, target_kind: str
) -> dict[str, Any]:
    """Require affirmative, typed evidence instead of defaulting absent gates to success."""
    scan = first_result(payload)
    if len(payload["results"]) != 1 or type(payload.get("exit_code")) is not int:
        raise ValueError("malformed Lean checker result: expected one result and an integer exit_code")
    if not isinstance(scan.get("path"), str) or Path(scan["path"]).resolve() != lean_path:
        raise ValueError("malformed Lean checker result: checked path does not match the requested file")
    check = scan.get("check")
    if not isinstance(check, dict) or type(check.get("returncode")) is not int:
        raise ValueError("malformed Lean checker result: missing compile returncode")
    if check.get("timed_out") is not None and type(check["timed_out"]) is not bool:
        raise ValueError("malformed Lean checker result: invalid timeout flag")
    blockers = scan.get("blockers")
    if (
        not isinstance(blockers, dict)
        or not {"sorry", "admit", "axiom", "constant", "unsafe"}.issubset(blockers)
        or any(type(value) is not int or value < 0 for value in blockers.values())
        or type(scan.get("total_blockers")) is not int
        or scan["total_blockers"] != sum(blockers.values())
    ):
        raise ValueError("malformed Lean checker result: missing or inconsistent blocker audit")
    missing = scan.get("missing_required_declaration_kinds")
    declarations = scan.get("declaration_list", scan.get("declarations"))
    if not isinstance(missing, list) or not isinstance(declarations, list):
        raise ValueError("malformed Lean checker result: missing declaration audit")
    if any(
        not isinstance(item, dict)
        or not isinstance(item.get("kind"), str)
        or not any(field in item for field in ("name", "full_name"))
        or any(field in item and not isinstance(item[field], str) for field in ("name", "full_name"))
        for item in declarations
    ):
        raise ValueError("malformed Lean checker result: declaration names and kinds must be strings")
    if not missing and not any(
        target_name in (item.get("name"), item.get("full_name"))
        and item.get("kind") == target_kind
        for item in declarations
    ):
        raise ValueError("malformed Lean checker result: claimed target is absent from declarations")
    return scan


def diagnostic_site(diagnostic: str) -> str:
    match = re.search(r"(?:^|\n)([^\n:]+):(\d+):(\d+)", diagnostic)
    if not match:
        return "not-reported"
    return f"{match.group(1).strip()}:{match.group(2)}:{match.group(3)}"


def classify_failure(
    diagnostic: str,
    blockers: dict[str, Any],
    target_missing: bool,
) -> tuple[str, str, str]:
    lower = diagnostic.lower()
    if any(int(value or 0) for value in blockers.values()):
        return (
            "FORMAL_BLOCKER",
            "the checked file still contains a placeholder, target-encoding declaration, or unsafe declaration",
            "remove the blocker and replay the same exact target gate",
        )
    if target_missing:
        return (
            "TARGET_MISMATCH",
            "the required namespace-qualified target is absent or has the wrong declaration kind",
            "repair the declaration name or kind before changing the mathematical proof",
        )
    if any(token in lower for token in ("unknown module", "invalid import", "no such file", "unexpected token")):
        return (
            "PARSE_IMPORT",
            "the Lean environment, import graph, or syntax does not match the target file",
            "repair the project root, import, namespace, or syntax and rerun the exact gate",
        )
    if any(token in lower for token in ("type mismatch", "has type", "expected", "failed to synthesize")):
        return (
            "TYPE_COERCION",
            "the encoded types, coercions, or inferred instances do not match the intended statement",
            "audit the source-to-Lean mapping and retrieve the needed coercion or instance lemma",
        )
    if any(token in lower for token in ("unknown identifier", "unknown constant", "declaration uses 'sorry'")):
        return (
            "PREMISE_RETRIEVAL",
            "an accessible local or mathlib premise is missing or has not been named correctly",
            "build a focused premise packet before inventing another helper theorem",
        )
    return (
        "LOCAL_PROOF",
        "Lean rejected the current local proof term or tactic sequence",
        "repair the first reported error once; return to Math Research if the same state persists",
    )


def owner_for(stage: str, eligible: bool) -> str:
    if eligible:
        return "theory-integrator"
    if stage in {"statement-fidelity", "mathematical", "assembly"}:
        return "math-research"
    return "lean-theorem-formalizer"


def formal_failure_surgery_contract(
    *,
    eligible: bool,
    failure_class: str,
    failure_stage: str,
    site: str,
    fingerprint: str,
    previous_same_failures: int,
) -> dict[str, Any]:
    """Return a bounded repair contract for a rejected local Lean proof."""
    if eligible:
        return {
            "activation": "not-needed",
            "reason": "the exact target gate passed",
        }
    if failure_stage not in {"auto", "local-proof"}:
        return {
            "activation": "not-applicable",
            "reason": f"the declared failure stage is {failure_stage}; repair that layer before local proof surgery",
        }
    if failure_class != "LOCAL_PROOF":
        return {
            "activation": "not-applicable",
            "reason": "repair the classified parse, import, type, premise, fidelity, or assembly layer first",
        }
    if previous_same_failures >= 1:
        return {
            "activation": "return-to-theory",
            "reason": "the same local proof state already failed after one bounded repair",
            "stop_rule": "do not sorrify or regenerate the same parent state again without a new premise, decomposition, or statement repair",
        }
    return {
        "activation": "candidate",
        "reported_site": site,
        "diagnostic_fingerprint": fingerprint,
        "repair_scope": "replace only the innermost failing structured proof block, then recompile immediately before interpreting later diagnostics",
        "skeleton_status": "compiling only when sorry is allowed preserves a candidate skeleton; it proves neither the extracted child nor the parent theorem",
        "required_subgoal_gates": [
            "well-formed Lean statement with the exact local context",
            "semantic entailment from the frozen parent context without dropped hypotheses",
            "counterexample or missing-premise attack",
            "exact reassembly interface into the frozen parent target",
        ],
        "recursion_stop": "stop when the extracted child is equivalent to its parent or a bounded retry creates no proof-state delta",
        "promotion_gate": "reassemble the verified child, replay the frozen target, scan sorry and axioms, and rerun fidelity and assembly checks",
    }


def read_acceptance(project: Path, packet: dict[str, Any]) -> dict[str, Any] | None:
    raw = packet.get("acceptance_report")
    if not isinstance(raw, str) or not raw:
        return None
    path, relative = inside_project(project, raw)
    if not path.is_file():
        return {"path": relative, "error": "missing"}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"path": relative, "error": "not-an-object"}
    payload = dict(payload)
    payload["path"] = relative
    payload["sha256"] = sha256_file(path)
    if payload.get("handoff_id") != packet.get("handoff_id"):
        payload["error"] = "handoff-id-mismatch"
    elif payload.get("claim_sha256") != packet.get("claim_sha256"):
        payload["error"] = "claim-hash-mismatch"
    elif payload.get("request_packet_sha256") != packet.get("packet_sha256"):
        payload["error"] = "request-hash-mismatch"
    return payload


def acceptance_passes(report: dict[str, Any] | None) -> tuple[bool, list[str]]:
    required = ("claim_fidelity", "assumption_lineage", "assembly_coverage", "axiom_audit")
    if not report or report.get("error"):
        return False, ["acceptance report is missing or invalid"]
    checks = report.get("checks")
    if not isinstance(checks, dict):
        return False, ["acceptance report has no checks object"]
    missing = []
    for name in required:
        item = checks.get(name)
        if (
            not isinstance(item, dict)
            or item.get("status") != "pass"
            or not isinstance(item.get("evidence"), str)
            or not item["evidence"].strip()
        ):
            missing.append(name)
    return not missing, missing


def refresh_acceptance_binding(
    project: Path, packet: dict[str, Any], binding: dict[str, Any]
) -> tuple[dict[str, Any] | None, bool]:
    report = read_acceptance(project, packet)
    if not report or report.get("error") or report.get("target_binding") == binding:
        return report, False
    path, _ = inside_project(project, report["path"])
    payload = {key: value for key, value in report.items() if key not in {"path", "sha256"}}
    payload["previous_audit_sha256"] = report["sha256"]
    payload["target_binding"] = binding
    payload["binding_updated_at_utc"] = utc_now()
    payload["checks"] = {
        name: {"status": "not-audited", "evidence": ""}
        for name in ("claim_fidelity", "assumption_lineage", "assembly_coverage", "axiom_audit")
    }
    atomic_write_json(path, payload)
    return read_acceptance(project, packet), True


def audit_formal_result(project: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Read-only freshness audit of one recorded local/full formal result."""
    errors: list[str] = []
    promoted_full_theorem = False
    result_relative = record.get("result_path")
    try:
        state = ensure_runtime(project)
        if not isinstance(result_relative, str):
            raise ValueError("formal record has no result path")
        path, _ = inside_project(project, result_relative)
        result = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(result, dict) or result.get("packet_type") != "lean-to-theory":
            raise ValueError("invalid formal result packet")
        promoted_full_theorem = (
            result.get("node_role") == "full-theorem"
            and result.get("eligible_for_formalized_complete") is True
            and result.get("promotion_requested") is True
        )
        if sha256_file(path) != record.get("result_file_sha256"):
            errors.append("formal result is changed or lacks a recorded file hash; recheck it")
        if result.get("result_sha256") != sha256_json({
            key: value for key, value in result.items() if key != "result_sha256"
        }):
            errors.append("formal result packet hash mismatch")
        if (
            result.get("claim_sha256") != state["claim_sha256"]
            or result.get("claim_revision") != state.get("claim_revision", 0)
        ):
            errors.append("formal result belongs to a different claim revision")
        if record.get("status") != "formalized-local" or result.get("exact_target_gate") != "pass":
            errors.append("latest formal verification failed")
        request_path, _ = inside_project(project, result["request_path"])
        if sha256_file(request_path) != result.get("request_sha256"):
            errors.append("frozen formal request changed or is missing")
        packet = json.loads(request_path.read_text(encoding="utf-8"))
        if not isinstance(packet, dict) or packet.get("packet_sha256") != sha256_json({
            key: value for key, value in packet.items() if key != "packet_sha256"
        }):
            raise ValueError("invalid frozen formal request")
        if not isinstance(packet.get("node"), dict) or not isinstance(packet.get("lean_target"), dict):
            raise ValueError("invalid frozen formal node or target")
        validate_statement_source(project, packet["node"])
        binding = target_binding(project, packet)
        if binding != result.get("target_binding"):
            errors.append("formal source or project dependency changed after checking")
        lean_path, _ = inside_project(project, binding["lean_file"])
        scan = validate_checker_result(result["lean_status"], lean_path, binding["target_name"], binding["target_kind"])
        if (
            scan["check"]["returncode"] != 0
            or scan["check"].get("timed_out", False)
            or scan["total_blockers"] != 0
            or scan["missing_required_declaration_kinds"]
            or result.get("checker_exit_code") != 0
            or result.get("checker_process_exit_code") != 0
        ):
            errors.append("recorded formal checker gates did not pass")
        checker_path = Path(result["checker_command"][1])
        if not checker_path.is_file() or sha256_file(checker_path) != result.get("checker_script_sha256"):
            errors.append("formal checker changed or is missing")
        if result.get("eligible_for_formalized_complete"):
            acceptance = read_acceptance(project, packet)
            accepted, _ = acceptance_passes(acceptance)
            if (
                not accepted
                or acceptance.get("target_binding") != binding
                or acceptance.get("sha256") != (result.get("acceptance_report") or {}).get("sha256")
            ):
                errors.append("full-theorem acceptance gates changed or are stale")
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        errors.append(str(exc))
    return {
        "node_id": record.get("node_id"),
        "result_path": result_relative,
        "valid": not errors,
        "promoted_full_theorem": promoted_full_theorem,
        "errors": list(dict.fromkeys(errors)),
    }


def prior_failure_count(
    project: Path,
    handoff_id: str,
    failure_class: str,
    site: str,
    fingerprint: str,
) -> int:
    count = 0
    for envelope in iter_channel(project, "attempts"):
        record = envelope.get("record")
        if not isinstance(record, dict):
            continue
        if (
            record.get("handoff_id") == handoff_id
            and record.get("failure_class") == failure_class
            and record.get("diagnostic_site") == site
            and record.get("diagnostic_fingerprint") == fingerprint
            and record.get("outcome") == "blocked"
        ):
            count += 1
    return count


def verify(args: argparse.Namespace) -> int:
    project = project_path(args.project)
    ensure_runtime(project)
    state = read_state(project)
    request_path, request_rel = inside_project(project, args.request)
    request_sha256_before = sha256_file(request_path)
    packet = json.loads(request_path.read_text(encoding="utf-8"))
    if not isinstance(packet, dict) or packet.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported Lean handoff request")
    if packet.get("packet_type") != "theory-to-lean":
        raise ValueError("not a theory-to-Lean handoff request")
    packet_hash = packet.get("packet_sha256")
    unhashed_packet = {key: value for key, value in packet.items() if key != "packet_sha256"}
    if not isinstance(packet_hash, str) or packet_hash != sha256_json(unhashed_packet):
        raise ValueError("tampered Lean handoff: request packet hash mismatch")
    if packet.get("claim_sha256") != state["claim_sha256"] or packet.get("claim_revision") != state.get(
        "claim_revision", 0
    ):
        raise ValueError("stale Lean handoff: the Math Research claim has changed")

    node = packet.get("node")
    target = packet.get("lean_target")
    if not isinstance(node, dict) or not isinstance(target, dict):
        raise ValueError("Lean handoff request lacks node or target data")
    validate_statement_source(project, node)
    lean_path, lean_rel = inside_project(project, str(target.get("file", "")))
    if args.lean_file:
        override_path, override_rel = inside_project(project, args.lean_file)
        if override_path != lean_path or override_rel != lean_rel:
            raise ValueError("Lean target file differs from the frozen handoff; prepare a new request")
    if not lean_path.is_file():
        raise ValueError(f"Lean target file not found: {lean_path}")
    lean_sha256_before = sha256_file(lean_path)
    binding_before = target_binding(project, packet)
    target_name = str(target.get("name", ""))
    target_kind = str(target.get("kind", ""))
    if not target_name or target_kind not in TARGET_KINDS:
        raise ValueError("Lean handoff target name or kind is invalid")

    lean_status = locate_lean_status(args.lean_status_script)
    checker_sha256_before = sha256_file(lean_status)
    command = [
        sys.executable,
        str(lean_status),
        str(lean_path),
        "--check",
        "--runner",
        args.runner,
        "--fail-on-blockers",
        "--fail-on-empty",
        "--require-decl-kind",
        f"{target_name}:{target_kind}",
        "--json",
    ]
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=args.timeout,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        status_payload = {
            "results": [
                {
                    "path": str(lean_path),
                    "blockers": {"sorry": 0, "admit": 0, "axiom": 0, "constant": 0, "unsafe": 0},
                    "total_blockers": 0,
                    "declaration_list": [],
                    "missing_required_declaration_kinds": [{"name": target_name, "required_kind": target_kind}],
                    "check": {
                        "returncode": 124,
                        "stdout": stdout,
                        "stderr": stderr or f"Lean check timed out after {args.timeout} seconds",
                    },
                }
            ],
            "exit_code": 124,
        }
        proc_returncode = 124
    else:
        proc_returncode = proc.returncode
        try:
            status_payload = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"lean_status.py did not emit valid JSON: {bounded(proc.stderr or proc.stdout)}"
            ) from exc
    if not isinstance(status_payload, dict):
        raise ValueError("lean_status.py output must be a JSON object")
    if sha256_file(request_path) != request_sha256_before:
        raise ValueError("Lean handoff request changed during verification; rerun from a stable request")
    current_state = ensure_runtime(project)
    if (current_state["claim_sha256"], current_state.get("claim_revision", 0)) != (
        state["claim_sha256"], state.get("claim_revision", 0)
    ):
        raise ValueError("project claim revision changed during Lean verification")
    validate_statement_source(project, node)
    if sha256_file(lean_status) != checker_sha256_before:
        raise ValueError("Lean checker script changed during verification")
    lean_sha256_after = sha256_file(lean_path)
    binding_after = target_binding(project, packet)
    lean_file_stable = lean_sha256_before == lean_sha256_after and binding_before == binding_after
    scan = validate_checker_result(status_payload, lean_path, target_name, target_kind)
    check = scan.get("check") if isinstance(scan.get("check"), dict) else {}
    blockers = scan.get("blockers") if isinstance(scan.get("blockers"), dict) else {}
    target_missing = bool(scan.get("missing_required_declaration_kinds"))
    raw_check_returncode = check.get("returncode", proc_returncode)
    check_returncode = (
        int(raw_check_returncode)
        if isinstance(raw_check_returncode, (int, str)) and str(raw_check_returncode).lstrip("-").isdigit()
        else proc_returncode
    )
    raw_status_exit_code = status_payload.get("exit_code", proc_returncode)
    status_exit_code = (
        int(raw_status_exit_code)
        if isinstance(raw_status_exit_code, (int, str)) and str(raw_status_exit_code).lstrip("-").isdigit()
        else proc_returncode
    )
    compile_ok = check_returncode == 0
    checker_ok = proc_returncode == 0 and status_exit_code == 0
    blocker_free = int(scan.get("total_blockers", 0) or 0) == 0
    eligible = (
        compile_ok
        and checker_ok
        and blocker_free
        and not target_missing
        and not scan.get("error")
        and not check.get("timed_out", False)
        and lean_file_stable
    )

    raw_diagnostic = str(check.get("stderr", "") or "")
    if not lean_file_stable:
        raw_diagnostic = "Lean target file changed during verification; the checker result is not bound to one file version"
    if not raw_diagnostic and not eligible:
        raw_diagnostic = json.dumps(
            {
                "blockers": blockers,
                "missing_target": scan.get("missing_required_declaration_kinds", []),
                "scan_error": scan.get("error", ""),
                "checker_process_exit": proc_returncode,
                "checker_status_exit": status_exit_code,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    diagnostic = bounded(raw_diagnostic if raw_diagnostic else "Lean exact target gate passed")
    if not lean_file_stable:
        failure_class = "TARGET_CHANGED_DURING_CHECK"
        inferred_root = "the checked Lean source changed while the exact target gate was running"
        repair = "stop concurrent edits and rerun the same request against one stable file version"
    elif eligible:
        failure_class = "NONE"
        inferred_root = "the exact target compiled with no scanned blockers"
        repair = "assemble this verified node into its declared parent"
    else:
        failure_class, inferred_root, repair = classify_failure(diagnostic, blockers, target_missing)
    if args.diagnosis:
        inferred_root = args.diagnosis.strip()
    if args.repair:
        repair = args.repair.strip()

    site = diagnostic_site(diagnostic)
    fingerprint = diagnostic_fingerprint(diagnostic)
    previous_same_failures = (
        0
        if eligible
        else prior_failure_count(
            project,
            str(packet["handoff_id"]),
            failure_class,
            site,
            fingerprint,
        )
    )
    stage = args.failure_stage
    owner = owner_for(stage, eligible)
    if not eligible and stage in {"auto", "local-proof"} and previous_same_failures >= 1:
        owner = "math-research"
        repair = (
            "the same Lean failure signature has repeated; return the node to Math Research "
            "for premise retrieval, decomposition, or statement audit"
        )
    repeated_local_failure = (
        not eligible
        and stage in {"auto", "local-proof"}
        and previous_same_failures >= 1
    )
    surgery_contract = formal_failure_surgery_contract(
        eligible=eligible,
        failure_class=failure_class,
        failure_stage=stage,
        site=site,
        fingerprint=fingerprint,
        previous_same_failures=previous_same_failures,
    )
    if owner == "math-research" and not repeated_local_failure:
        repair = args.repair.strip() if args.repair else (
            "return the exact Lean diagnostic to Math Research for statement, mathematical, or assembly repair"
        )
    proof_state_delta = (
        "target formalized locally and ready for parent assembly"
        if eligible
        else "exact Lean obstruction recorded; target remains blocked"
    )
    acceptance, acceptance_refreshed = refresh_acceptance_binding(project, packet, binding_after)
    acceptance_ok, acceptance_missing = acceptance_passes(acceptance)
    final_ready = eligible and node.get("role") == "full-theorem" and acceptance_ok
    promotion_error = ""
    if args.promote_final and not final_ready:
        promotion_error = (
            "final promotion requires a full-theorem request, a passing exact target gate, and evidence for "
            + ", ".join(acceptance_missing or ["all acceptance checks"])
        )

    run_id = f"lean-check-{uuid.uuid4().hex[:12]}"
    result_rel_path = Path("lean") / "handoffs" / f"{packet['handoff_id']}.{run_id}.result.json"
    result_path, result_rel = inside_project(project, result_rel_path)
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "packet_type": "lean-to-theory",
        "run_id": run_id,
        "handoff_id": packet["handoff_id"],
        "checked_at_utc": utc_now(),
        "request_path": request_rel,
        "request_sha256": request_sha256_before,
        "claim_sha256": state["claim_sha256"],
        "claim_revision": state.get("claim_revision", 0),
        "node_id": node.get("id"),
        "node_role": node.get("role"),
        "statement": node.get("statement"),
        "lean_file": lean_rel,
        "lean_file_sha256_before": lean_sha256_before,
        "lean_file_sha256": lean_sha256_after,
        "lean_file_stable_during_check": lean_file_stable,
        "target_binding": binding_after,
        "target_name": target_name,
        "target_kind": target_kind,
        "checker_command": command,
        "checker_script_sha256": checker_sha256_before,
        "checker_exit_code": status_exit_code,
        "checker_process_exit_code": proc_returncode,
        "exact_target_gate": "pass" if eligible else "fail",
        "node_status": "formalized-local" if eligible else "blocked",
        "diagnostic": diagnostic,
        "diagnostic_site": site,
        "diagnostic_fingerprint": fingerprint,
        "failure_class": failure_class,
        "inferred_root_cause": inferred_root,
        "repair": repair,
        "proof_state_delta": proof_state_delta,
        "failure_stage": stage,
        "prior_same_failure_count": previous_same_failures,
        "recommended_owner": owner,
        "formal_failure_surgery": surgery_contract,
        "acceptance_report": acceptance,
        "acceptance_binding_refreshed": acceptance_refreshed,
        "eligible_for_formalized_complete": final_ready,
        "promotion_requested": bool(args.promote_final),
        "promotion_error": promotion_error,
        "lean_status": status_payload,
    }
    result["result_sha256"] = sha256_json(result)
    atomic_write_json(result_path, result)
    if not final_ready:
        invalidate_completed_request(
            project, request_rel,
            "the completed formal target failed rechecking or its final acceptance audit is stale",
        )

    attempt = {
        "event_type": "lean_handoff_checked",
        "route_family": "Lean formalization",
        "target_lemma": str(node.get("id", target_name)),
        "outcome": "formalized-local" if eligible else "blocked",
        "failure_witness": "none" if eligible else diagnostic,
        "feedback_kind": "checker",
        "checker_backend": " ".join(command),
        "diagnostic": diagnostic,
        "local_state": str(node.get("statement", "")),
        "diagnostic_site": result["diagnostic_site"],
        "diagnostic_fingerprint": fingerprint,
        "inferred_root_cause": inferred_root,
        "failure_class": failure_class,
        "diagnosis": inferred_root,
        "repair": repair,
        "replay_result": "passed" if eligible else f"failed with code {result['checker_exit_code']}",
        "proof_state_delta": proof_state_delta,
        "handoff_id": packet["handoff_id"],
        "result_path": result_rel,
        "lean_file_sha256": result["lean_file_sha256"],
        "recommended_owner": owner,
    }
    append_record(project, "attempts", attempt)
    append_record(
        project,
        "proof_nodes",
        {
            "event_type": "lean_node_checked",
            "node_id": str(node.get("id", target_name)),
            "status": result["node_status"],
            "statement": str(node.get("statement", "")),
            "handoff_id": packet["handoff_id"],
            "result_path": result_rel,
            "result_file_sha256": sha256_file(result_path),
            "recommended_owner": owner,
        },
    )
    update_state(
        project,
        proof_status="formalized-complete" if args.promote_final and final_ready else None,
        current_node=str(node.get("id", target_name)),
        last_decisive_artifact=result_rel,
        evidence_summary={
            "disposition": "proved",
            "basis": "formal-proof",
            "scope": "full-original-theorem",
            "claim_sha256": state["claim_sha256"],
            "claim_revision": state.get("claim_revision", 0),
            "human_reviewed": False,
            "formal_verification": True,
            "formal_result_path": result_rel,
            "formal_result_sha256": sha256_file(result_path),
        } if args.promote_final and final_ready else None,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if promotion_error:
        return 2
    return 0 if eligible else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare_parser = subparsers.add_parser("prepare", help="prepare a Theory-to-Lean request")
    prepare_parser.add_argument("project")
    prepare_parser.add_argument("--node-id", required=True)
    prepare_parser.add_argument("--role", choices=ROLES, default="local-lemma")
    prepare_parser.add_argument("--statement")
    prepare_parser.add_argument(
        "--statement-file",
        help="statement source inside PROJECT; relative paths resolve from the project root",
    )
    prepare_parser.add_argument("--lean-file", default="lean/LocalLemmas.lean")
    prepare_parser.add_argument("--target-name", required=True)
    prepare_parser.add_argument("--target-kind", choices=TARGET_KINDS, default="theorem")
    prepare_parser.add_argument("--dependency", action="append", default=[])
    prepare_parser.add_argument("--source-fragment", action="append", default=[])
    prepare_parser.add_argument(
        "--allowed-axiom",
        action="append",
        default=[],
        help="record an expected dependency for later audit; does not bypass blocker scans",
    )
    prepare_parser.add_argument(
        "--downstream-use",
        default="",
        help="named parent use; required for local-lemma and interface-theorem requests",
    )
    prepare_parser.add_argument("--expected-proof-method", default="")
    prepare_parser.add_argument("--output")

    verify_parser = subparsers.add_parser("verify", help="run Lean and return evidence to Theory")
    verify_parser.add_argument("project")
    verify_parser.add_argument("request")
    verify_parser.add_argument(
        "--lean-file",
        help="optional path assertion; must equal the target frozen in the request",
    )
    verify_parser.add_argument("--lean-status-script")
    verify_parser.add_argument(
        "--runner",
        choices=("auto", "lean", "lake", "codex-mathlib-lean"),
        default="auto",
    )
    verify_parser.add_argument("--timeout", type=int, default=180)
    verify_parser.add_argument("--failure-stage", choices=FAILURE_STAGES, default="auto")
    verify_parser.add_argument("--diagnosis")
    verify_parser.add_argument("--repair")
    verify_parser.add_argument("--promote-final", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return prepare(args) if args.command == "prepare" else verify(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        if args.command == "verify":
            try:
                project = project_path(args.project)
                _, request_relative = inside_project(project, args.request)
                invalidate_completed_request(project, request_relative, str(exc))
            except (OSError, ValueError, TypeError, KeyError):
                pass
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
