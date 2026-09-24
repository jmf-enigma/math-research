#!/usr/bin/env python3
"""Persist the next mathematical action, separately from a run's compute grant."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from proof_runtime import (
    atomic_write_json, canonical_json, ensure_runtime, runtime_dir, sha256_file, sha256_text,
)
from run_referee import read_acceptance_contract


PHASES = {"solve", "repair", "replan", "verify", "awaiting-evidence", "complete", "exact-obstruction"}


class CheckpointIntegrityError(ValueError):
    """The checkpoint file is damaged; the surrounding project may still be valid."""


def empty_checkpoint(project: Path) -> dict[str, Any]:
    state = ensure_runtime(project)
    return {
        "schema_version": 1,
        "claim_sha256": state["claim_sha256"],
        "claim_revision": state.get("claim_revision", 0),
        "acceptance_contract_sha256": sha256_text(read_acceptance_contract(project)),
        "phase": "solve",
        "stable_plan": None,
        "repaired_routes": [],
        "repair_origin_signature": None,
        "previous_candidate": None,
        "referee_feedback": None,
        "pending_candidate": None,
        "evidence_request": None,
        "resume_phase": "solve",
        "search_used": False,
        "references": [],
        "result": None,
        "usage": {"iterations": 0, "agent_calls": 0, "wall_seconds": 0.0},
        "model": None,
        "reasoning_effort": "high",
    }


def load_checkpoint(project: Path) -> dict[str, Any]:
    empty = empty_checkpoint(project)
    path = runtime_dir(project) / "proof_loop_checkpoint.json"
    if not path.exists():
        return empty
    if path.stat().st_size > 2 * 1024 * 1024:
        raise CheckpointIntegrityError("proof checkpoint exceeds the 2 MiB limit")
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CheckpointIntegrityError(f"proof checkpoint cannot be decoded: {exc}") from exc
    if not isinstance(saved, dict) or saved.get("schema_version") != 1:
        raise CheckpointIntegrityError("unsupported proof checkpoint")
    digest = saved.pop("checkpoint_sha256", None)
    if digest != sha256_text(canonical_json(saved)):
        raise CheckpointIntegrityError("proof checkpoint hash mismatch")
    if (saved.get("claim_sha256"), saved.get("claim_revision")) != (
        empty["claim_sha256"], empty["claim_revision"]
    ):
        # The historical checkpoint remains on disk until a new action is saved.
        return empty
    if saved.get("phase") not in PHASES or saved.get("resume_phase") not in PHASES:
        raise CheckpointIntegrityError("invalid checkpoint phase")
    if not isinstance(saved.get("references"), list) or not isinstance(saved.get("repaired_routes"), list):
        raise CheckpointIntegrityError("invalid checkpoint references or repair history")
    # Missing identity in a legacy checkpoint is unknown, not today's contract.
    return {**empty, **saved,
            "acceptance_contract_sha256": saved.get("acceptance_contract_sha256")}


def save_checkpoint(project: Path, checkpoint: dict[str, Any]) -> None:
    state = ensure_runtime(project)
    if (checkpoint["claim_sha256"], checkpoint["claim_revision"]) != (
        state["claim_sha256"], state.get("claim_revision", 0)
    ):
        raise ValueError("the theorem changed while the proof loop was running")
    if checkpoint["acceptance_contract_sha256"] != sha256_text(read_acceptance_contract(project)):
        raise ValueError("the acceptance contract changed while the proof loop was running")
    payload = dict(checkpoint)
    payload.pop("checkpoint_sha256", None)
    payload["checkpoint_sha256"] = sha256_text(canonical_json(payload))
    atomic_write_json(runtime_dir(project) / "proof_loop_checkpoint.json", payload)


def local_descriptor(project: Path, raw: str | Path) -> dict[str, str]:
    path = Path(raw).expanduser()
    path = (project / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(project.resolve()) or not path.is_file():
        raise ValueError(f"checkpoint artifact must be a file inside the project: {raw}")
    return {"path": path.relative_to(project.resolve()).as_posix(), "sha256": sha256_file(path)}


def checked_path(project: Path, descriptor: dict[str, str]) -> Path:
    current = local_descriptor(project, descriptor["path"])
    if current != descriptor:
        raise ValueError(f"checkpoint artifact changed: {descriptor['path']}")
    return project / current["path"]


def merge_references(
    project: Path, checkpoint: dict[str, Any], supplied: list[str]
) -> tuple[list[str], bool]:
    old = {item["path"]: item for item in checkpoint["references"]}
    new = {item["path"]: item for item in (local_descriptor(project, p) for p in supplied)}
    for name, descriptor in old.items():
        if name not in new:
            checked_path(project, descriptor)
    merged = {**old, **new}
    changed = merged != old
    checkpoint["references"] = list(merged.values())
    return list(merged), changed


def make_evidence_request(
    capability: str, local_claim: str, assumptions: list[str], issue: Any,
    *, resume_phase: str, candidate: dict[str, str] | None = None,
) -> dict[str, Any]:
    request = {
        "capability": capability,
        "local_claim": local_claim,
        "assumptions": assumptions,
        "missing_artifact": issue,
        "acceptance_test": (
            "Check the supplied artifact against this exact local claim and assumptions; "
            "record its scope and recheck the pending candidate or dependency before promotion."
        ),
        "resume_phase": resume_phase,
        "candidate": candidate,
        "proof_effect": "none",
    }
    request["request_id"] = sha256_text(canonical_json(request))[:16]
    return request


def referee_action(verdict: dict[str, Any]) -> tuple[str, str | None]:
    """Classify control flow without claiming the classifier checks mathematics."""
    kind = verdict.get("failure_kind")
    if verdict.get("verdict") == "correct":
        return "accept", None
    if kind == "referee-runtime":
        return "runtime-error", None
    if kind == "tool-evidence-gap":
        return "awaiting-evidence", "tool-replay"
    if kind == "missing-packet-evidence":
        return "awaiting-evidence", "retrieval"
    if kind == "simplification-gap" and verdict.get("verdict") == "uncertain":
        return "replan", None
    if verdict.get("verdict") != "wrong":
        return "awaiting-evidence", "independent-review"
    if kind in {"claim-mismatch", "assumption-gap", "assembly-gap", "central-mechanism-failure"}:
        return "replan", None
    return "repair", None
