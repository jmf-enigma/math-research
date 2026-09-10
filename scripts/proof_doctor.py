#!/usr/bin/env python3
"""Diagnose one primary next move for a theory-proof project."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from audit_ledger import audit_ledger_text, section_body
from computation_artifact import audit_artifact
from frontier_evidence import FRONTIER_STATUSES, validate_frontier_bundle
from lean_bridge import audit_formal_result
from proof_runtime import CHANNELS, ensure_runtime, iter_channel
from select_playbook import PLAYBOOKS, score


PATTERN_QUERIES = {
    "dp-proof-playbook.md": [
        "Bellman inequality certificate proof",
        "monotone optimal policy proof submodular dynamic programming",
        "threshold policy single crossing MDP proof",
    ],
    "optimization-or-playbook.md": [
        "KKT sufficiency proof constraint qualification",
        "primal dual certificate operations research proof",
        "exchange argument proof optimization matching scheduling",
        "performance estimation problem exact Lyapunov certificate first order method",
    ],
    "mechanism-design-playbook.md": [
        "cyclic monotonicity proof mechanism design",
        "payment identity IC IR envelope theorem proof",
        "finite type payment feasibility LP incentive compatibility",
    ],
    "games-matching-playbook.md": [
        "fixed point theorem game equilibrium proof assumptions",
        "supermodular games increasing differences proof",
        "stable matching blocking pair invariant proof",
    ],
    "learning-theory-playbook.md": [
        "uniform convergence proof covering Rademacher concentration",
        "stability generalization proof learning theory",
        "PAC Bayes proof KL change of measure",
    ],
    "bandits-oco-playbook.md": [
        "uniform confidence event regret proof bandits",
        "elliptical potential lemma linear bandit proof",
        "online convex optimization potential proof regret",
    ],
    "lower-bounds-playbook.md": [
        "two point testing lower bound proof",
        "Fano Assouad minimax lower bound proof",
        "change of measure bandit lower bound KL proof",
    ],
    "probabilistic-method-playbook.md": [
        "Lovasz Local Lemma bad events dependency graph proof",
        "Moser Tardos resampling algorithmic Lovasz Local Lemma proof",
        "lopsided Lovasz Local Lemma dependency graph proof",
    ],
}


CAPABILITY_QUERIES = {
    "strategy-discovery": "recent mathematical proof discovery construction counterexample system",
    "decomposition": "Lean proof decomposition standalone lemma extraction dependency merge",
    "premise-retrieval": "global premise retrieval semantic theorem search formal mathematics",
    "local-proof": "Lean compiler feedback proof repair isolated sublemma",
    "assembly": "strict Lean proof verification signature axiom assembly",
    "fidelity": "autoformalization statement fidelity hypothesis audit",
    "library-coverage": "Lean research mathematics custom definition auxiliary lemma package coverage",
}


STATE_ACTIONS = {
    "S0-parse": [
        "Make variables, domains, quantifiers, assumptions, and desired conclusion explicit in claim.md.",
        "Record the statement fence: proof mode must not silently change assumptions, quantifiers, domains, or conclusion.",
        "Audit statement fidelity for model-heavy or literature-derived claims: definitions, zero/boundary behavior, implicit conventions, and quantifier scope.",
        "Run the direct-solve check: named theorem, certificate, contradiction, or known decomposition.",
        "Classify the theorem family with select_playbook.py.",
    ],
    "S1-classify": [
        "Before route search, check whether the selected playbook gives a direct theorem or certificate.",
        "If the statement came from a paper or informal model, confirm that the formal claim matches the intended theorem before route search.",
        "If no direct route is visible but the proof is still small, do a micro pattern check: one theorem family, prior ledger, or close paper pattern.",
        "Choose at least two proof routes and one falsification route in ATTACK_MATRIX.md or strategy.md.",
        "Move to stress testing before drafting the final proof.",
    ],
    "S2-stress-test": [
        "If direct solve failed, record the mismatch in LEDGER.md.",
        "Write the negation and smallest toy model in counterexamples.md.",
        "Try one boundary case, then ablate at most one high-leverage suspect hypothesis; seek an explicit witness and record where the original assumption blocks it.",
        "If no route has a pattern guess, chosen central object, or proof kernel, fill IDEA_MAP.md before drafting another proof.",
        "If the route is still unclear, first do a micro pattern check; create a workstream card only if the branch is hard, repeated, tool-assisted, or literature-dependent.",
    ],
    "S2b-idea-map": [
        "Fill failure world, central object candidates, one proof kernel, candidate central lemma, and verification hook in IDEA_MAP.md.",
        "If candidate rules are noisy, add one compact evidence-layered packet: sound shortcuts, executable falsifiers, scheduler-only priors, and checked near-misses; only replayable artifacts can change status.",
        "If the kernel needs invention, guess from small cases: formula, threshold, invariant, active set, tight instance, or potential; use pattern_miner.py for exact sequences and keep one holdout check.",
        "If an answer, construction, threshold, potential, hard instance, or coefficient is unknown, treat discovery as a separate step before proof.",
        "Review the current missing lemma as a good gap or bad gap before promoting it.",
        "Use nearby papers, appendices, prior ledgers, theorem families, or analogous models to extract a candidate proof architecture.",
        "Move to route portfolio only after one kernel can be proved, refuted, retrieved, tool-checked, or locally formalized.",
    ],
    "S3-route-portfolio": [
        "Confirm that candidate routes differ by central object, theorem family, certificate, failure world, or evidence source.",
        "Keep a small route candidate board: 2-4 routes scored by central object, verification hook, novelty, and gap quality.",
        "Update WORKSTREAMS.md only for branches that need durable state; each active card should include a look-at-how-others-do-it pass or a skip reason.",
        "If the user approved multi-agent work, fill the Multi-Agent Dispatch Gate with disjoint artifacts before delegation.",
        "Fill Route A, Route B, and Route C statuses in LEDGER.md.",
        "Pick the route whose theorem assumptions most closely match the claim.",
    ],
    "S4-lemma-graph": [
        "Select the least-certain ready leaf that feeds the current theorem assembly.",
        "Turn every nontrivial step into a blueprint node with statement deps, proof deps, downstream use, status, expected artifact, gap grade, failure diagnosis, and compact repair state.",
        "Mark OR alternatives and AND required child lemmas; attack the lowest-confidence required child before expanding another route.",
        "Merge equivalent proof states/actions before retrying: same goal, assumptions, central object, and failure witness means same state unless a new artifact exists.",
        "Prove ready leaves that feed the current assembly path first; postpone orphan lemmas unless they falsify, repair, or unlock the route.",
        "After two local attempts on a node, fill the Route Decision Check before retrying.",
        "Preserve solved nodes; if a failed node is STATEMENT_WRONG, repair/drop it and rewire dependents; if PROOF_TOO_HARD, split it into helper nodes.",
        "After failure, keep proved helper lemmas and revise only unproved or false nodes plus dependents.",
        "If a skeleton is right but a block fails, preserve the skeleton and isolate the bad block as a named lemma.",
        "For the hardest unresolved lemma, run bottleneck surgery: shrink, flip, change representation, then certify/falsify/retrieve/repair.",
        "For the hardest fragile lemma, use one-step moves: current subgoal, proposed move, expected new subgoal, check result, proof-state delta.",
        "If the local move is fragile or repeated, fill the Prover-Verifier Move Contract: prover move, verifier verdict, soundness probe, proof-state delta, and coordinator decision.",
        "For multi-step plans, tag fragile steps as tool-verified/easy-to-check/hard-to-check and run goal and logic gates before accepting them.",
        "Promote the single hardest missing step to its own lemma card.",
    ],
    "S5-local-certification": [
        "Check fragile algebra, finite cases, optimization certificates, or formalizable inequalities with tools.",
        "For Lean/API artifacts, audit `sorry`, admitted axioms, unresolved obligations, and whether verified helper lemmas assemble into the original theorem.",
        "Record the exact command/result in LEDGER.md.",
    ],
    "S6-assembly": [
        "Assemble only proved or explicitly conditional lemmas into the exact claim.",
        "Check quantifiers and boundary cases before final review.",
    ],
    "S7-adversarial-review": [
        "Attack the proof for hidden assumptions, quantifier mismatch, boundary failure, and theorem-family mismatch.",
        "Run audit_ledger.py before finalizing.",
    ],
    "S8-finalize": [
        "Write the final proof with claim status, verification status, assumptions, lemma graph, and proof pattern.",
    ],
    "S9-stuck": [
        "Name the exact obstruction in LEDGER.md.",
        "Recycle only the verified prefix, checked helper lemmas, and useful intermediate objects from failed routes; heuristics and near-misses remain proof_effect=none until independently replayed.",
        "Check the Attempt Fingerprint Index in WORKSTREAMS.md; run check_attempt.py only if several fingerprints or an ambiguous match make this hard.",
        "Fill Proof-State Equivalence if the new idea has the same goal, assumptions, central object, and failure witness as a prior route.",
        "Shrink the obstruction to one proof kernel before trying another long proof route.",
        "If the proof graph has an AND bottleneck, work that required child before opening another OR route.",
        "Fill Route Decision Check in WORKSTREAMS.md: continue, repair, re-decompose, retrieve, tool-falsify, or stop-report.",
        "Rank next moves by decision value: kernel proof/refutation, counterexample, missing assumption, certificate, retrieval, representation change, or theorem repair.",
        "If a proposed move leaves the proof state unchanged, add a Failed-State Notebook entry in WORKSTREAMS.md before retrying.",
        "If a local move has been challenged or repeated, run the Prover-Verifier Move Contract before another proof paragraph.",
        "If a step-level challenge stalls, check challenge/replan budget and choose one verdict before more prose: challenge, trace-back, re-decompose, re-plan, switch to pure reasoning on tool artifacts, or stop/report.",
        "If no construction is visible, mine small cases for a pattern; use pattern_miner.py for exact sequences and test one holdout case before promoting the guess.",
        "Classify the current gap as good or bad; bad gaps require splitting, retrieval, falsification, or theorem repair.",
        "Use compact repair state for the bottleneck: statement, dependencies, previous attempt signature, previous feedback, and suggested fix.",
        "Before repeating proof search, inspect one to three nearby papers, appendices, prior ledgers, theorem families, or analogous models for this obstruction.",
        "If the user approved multi-agent work, split roles by artifact: planner, falsifier, retriever, formalizer/tool-checker, reviewer; do not ask several agents to write the same full proof.",
        "Create a bounded workstream card only if the next branch needs durable state.",
        "Choose one escalation method: tool falsification, retrieval, local formalization, theorem repair, or stop/report.",
        "If the block depends on modeling taste or domain intuition, ask the user for a steering hint before another heavy cycle.",
    ],
}


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def runtime_referee_feedback(project: Path) -> dict:
    try:
        runtime_state = ensure_runtime(project)
        channels = {
            name: list(iter_channel(project, name, current_claim_only=True))
            for name in CHANNELS
        }
        verification_entries = channels["verification_reports"]
        computation_entries = channels["computations"]
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return {
            "available": False,
            "verdict": None,
            "raw_verdict": None,
            "run_id": None,
            "review_scope": None,
            "candidate_proof_sha256": None,
            "failure_kind": None,
            "first_error": {},
            "repair_hints": [],
            "passed_claim_ids": [],
            "passed_artifact_ids": [],
            "invalid_computation_artifacts": [],
            "superseded_computation_artifacts": [],
            "computation_warnings": [],
            "runtime_errors": [str(exc)],
            "runtime_integrity_ok": False,
            "invalid_formal_artifacts": [],
            "passed_formal_node_ids": [],
            "needs_packet_repair": False,
        }

    runtime_errors: list[str] = []
    evidence_summary = runtime_state.get("evidence_summary")
    if isinstance(evidence_summary, dict) and evidence_summary.get("disposition") == "pending":
        runtime_errors.append(
            "previous proof acceptance is invalidated: " + str(evidence_summary.get("basis") or "reverification is required")
        )
    latest_formal: dict[str, dict] = {}
    previously_passed_formal: set[str] = set()
    for envelope in channels["proof_nodes"]:
        record = envelope["record"]
        if record.get("event_type") == "lean_node_checked":
            latest_formal[record["node_id"]] = record
            if record.get("status") == "formalized-local":
                previously_passed_formal.add(record["node_id"])
    formal_audits = [audit_formal_result(project, latest_formal[node]) for node in sorted(previously_passed_formal)]
    if runtime_state.get("proof_status") == "formalized-complete":
        active_result = (
            evidence_summary.get("formal_result_path")
            if isinstance(evidence_summary, dict)
            else None
        ) or runtime_state.get("last_decisive_artifact")
        active_audits = [audit for audit in formal_audits if (
            audit["valid"] and audit["promoted_full_theorem"] and audit["result_path"] == active_result
        )]
        if active_audits:
            # A current checked full target plus its bound assembly/axiom audit
            # establishes its own scope; failed unrelated exploratory nodes do
            # not refute that independent complete proof.
            formal_audits = active_audits
        else:
            runtime_errors.append("formalized-complete has no current, valid full-theorem promotion evidence")
    invalid_formal = [audit for audit in formal_audits if not audit["valid"]]
    passed_formal = [audit["node_id"] for audit in formal_audits if audit["valid"]]

    recorded_claims: dict[str, str] = {}
    passed_artifacts: set[str] = set()
    superseded_by: dict[str, dict] = {}
    for envelope in computation_entries:
        record = envelope.get("record", {})
        artifact_id = record.get("artifact_id")
        if not isinstance(artifact_id, str):
            continue
        claim_id = record.get("claim_id")
        if isinstance(claim_id, str) and claim_id:
            recorded_claims[artifact_id] = claim_id
        if record.get("event_type") == "computation_replayed" and record.get("status") == "passed":
            passed_artifacts.add(artifact_id)
        if record.get("event_type") == "computation_superseded":
            replacement_id = record.get("replacement_artifact_id")
            if isinstance(replacement_id, str) and replacement_id:
                superseded_by[artifact_id] = record

    valid_artifacts: set[str] = set()
    invalid_artifacts: list[dict] = []
    superseded_artifacts: list[dict] = []
    computation_warnings: list[dict] = []
    artifact_audits: dict[str, dict] = {}

    def cached_audit(artifact_id: str) -> dict:
        if artifact_id not in artifact_audits:
            artifact_audits[artifact_id] = audit_artifact(project, artifact_id)
        return artifact_audits[artifact_id]

    for artifact_id in sorted(passed_artifacts):
        if artifact_id in superseded_by:
            chain = [artifact_id]
            cursor = artifact_id
            seen = {artifact_id}
            while cursor in superseded_by:
                replacement_id = superseded_by[cursor]["replacement_artifact_id"]
                if replacement_id in seen:
                    invalid_artifacts.append(
                        {
                            "artifact_id": artifact_id,
                            "claim_id": recorded_claims.get(artifact_id),
                            "errors": ["computation supersession cycle detected"],
                        }
                    )
                    cursor = ""
                    break
                source_scope = cached_audit(cursor).get("claim_scope_sha256")
                replacement_scope = cached_audit(replacement_id).get("claim_scope_sha256")
                if not source_scope or source_scope != replacement_scope:
                    invalid_artifacts.append({
                        "artifact_id": artifact_id,
                        "claim_id": recorded_claims.get(artifact_id),
                        "errors": [f"computation supersession changes or lacks immutable claim scope: {cursor} -> {replacement_id}"],
                    })
                    cursor = ""
                    break
                seen.add(replacement_id)
                chain.append(replacement_id)
                cursor = replacement_id
            if not cursor:
                continue
            replacement_audit = cached_audit(cursor)
            if not replacement_audit["valid"]:
                invalid_artifacts.append(
                    {
                        "artifact_id": artifact_id,
                        "claim_id": recorded_claims.get(artifact_id),
                        "replacement_artifact_id": cursor,
                        "errors": [
                            f"superseding artifact {cursor} is not currently valid",
                            *replacement_audit["errors"],
                        ],
                    }
                )
                continue
            valid_artifacts.add(cursor)
            superseded_artifacts.append(
                {
                    "artifact_id": artifact_id,
                    "claim_id": recorded_claims.get(artifact_id),
                    "replacement_artifact_id": cursor,
                    "chain": chain,
                    "reason": superseded_by[artifact_id].get("reason"),
                }
            )
            continue

        artifact_audit = cached_audit(artifact_id)
        if artifact_audit["valid"]:
            valid_artifacts.add(artifact_id)
            if artifact_audit["warnings"]:
                computation_warnings.append(
                    {
                        "artifact_id": artifact_id,
                        "claim_id": artifact_audit.get("claim_id") or recorded_claims.get(artifact_id),
                        "warnings": artifact_audit["warnings"],
                    }
                )
        else:
            invalid_artifacts.append(
                {
                    "artifact_id": artifact_id,
                    "claim_id": artifact_audit.get("claim_id") or recorded_claims.get(artifact_id),
                    "errors": artifact_audit["errors"],
                }
            )
    covered_claim_ids = {
        recorded_claims[artifact_id]
        for artifact_id in valid_artifacts
        if artifact_id in recorded_claims
    }
    covered_claim_ids.update(
        item["claim_id"] for item in superseded_artifacts if item.get("claim_id")
    )
    passed_claim_ids = sorted(covered_claim_ids)

    if not verification_entries:
        return {
            "available": False,
            "verdict": None,
            "raw_verdict": None,
            "run_id": None,
            "review_scope": None,
            "candidate_proof_sha256": None,
            "failure_kind": None,
            "first_error": {},
            "repair_hints": [],
            "passed_claim_ids": passed_claim_ids,
            "passed_artifact_ids": sorted(valid_artifacts),
            "invalid_computation_artifacts": invalid_artifacts,
            "superseded_computation_artifacts": superseded_artifacts,
            "computation_warnings": computation_warnings,
            "runtime_errors": runtime_errors,
            "runtime_integrity_ok": True,
            "invalid_formal_artifacts": invalid_formal,
            "passed_formal_node_ids": passed_formal,
            "needs_packet_repair": False,
        }
    record = verification_entries[-1].get("record", {})
    first_error = record.get("first_error") if isinstance(record.get("first_error"), dict) else {}
    failure_kind = record.get("failure_kind")
    if not isinstance(failure_kind, str) or not failure_kind:
        issue = str(first_error.get("issue", "")).lower()
        missing_markers = (
            "absent from the packet",
            "not supplied",
            "not contained",
            "unavailable",
            "missing evidence",
            "cannot be verified",
        )
        if any(marker in issue for marker in missing_markers):
            failure_kind = "missing-packet-evidence"
    repair_hints = record.get("repair_hints")
    if not isinstance(repair_hints, list):
        repair_hints = []
    raw_verdict = record.get("verdict")
    effective_verdict = (
        "uncertain"
        if raw_verdict == "wrong"
        and failure_kind in {"missing-packet-evidence", "tool-evidence-gap"}
        else raw_verdict
    )
    return {
        "available": True,
        "verdict": effective_verdict,
        "raw_verdict": raw_verdict,
        "run_id": record.get("run_id"),
        "review_scope": record.get("module_id") or record.get("candidate_proof_source"),
        "candidate_proof_sha256": record.get("candidate_proof_sha256"),
        "failure_kind": failure_kind,
        "first_error": first_error,
        "repair_hints": [hint for hint in repair_hints if isinstance(hint, str)][:3],
        "passed_claim_ids": passed_claim_ids,
        "passed_artifact_ids": sorted(valid_artifacts),
        "invalid_computation_artifacts": invalid_artifacts,
        "superseded_computation_artifacts": superseded_artifacts,
        "computation_warnings": computation_warnings,
        "runtime_errors": runtime_errors,
        "runtime_integrity_ok": True,
        "invalid_formal_artifacts": invalid_formal,
        "passed_formal_node_ids": passed_formal,
        "needs_packet_repair": failure_kind in {"missing-packet-evidence", "tool-evidence-gap"},
        "verification_path": record.get("verification_path"),
    }


def audit_text(text: str, ledger: Path) -> dict:
    return audit_ledger_text(text, ledger)


def route_from_claim(claim: str) -> list[tuple[str, int]]:
    ranked = sorted(
        [(name, score(claim.lower(), keywords)) for name, keywords in PLAYBOOKS.items()],
        key=lambda item: item[1],
        reverse=True,
    )
    selected = [(name, value) for name, value in ranked if value > 0][:3]
    return selected or [
        ("proof-router.md", 0),
        ("strategy-scheduler.md", 0),
        ("obstruction-taxonomy.md", 0),
    ]


def is_blank_pattern_scan(project: Path) -> bool:
    path = project / "PATTERN_SCAN.md"
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8")
    filled_source = re.search(r"^- source:\s*\S+", text, flags=re.M)
    imported_move = re.search(r"^- route to add .*:\s*\S+", text, flags=re.M)
    return not (filled_source or imported_move)


def is_blank_idea_map(project: Path) -> bool:
    path = project / "IDEA_MAP.md"
    if not path.exists():
        return True
    text = path.read_text(encoding="utf-8")
    central_object = re.search(r"^- chosen central object:\s*\S+", text, flags=re.M)
    central_lemma = re.search(r"^- chosen statement:\s*\S+", text, flags=re.M)
    proof_kernel = re.search(r"^- kernel statement:\s*\S+", text, flags=re.M)
    pattern_guess = re.search(r"^- guessed object or identity:\s*\S+", text, flags=re.M)
    selected_idea = re.search(r"^- selected idea:\s*\S+", text, flags=re.M)
    return not (central_object or central_lemma or proof_kernel or pattern_guess or selected_idea)


def idea_map_need(project: Path, state: str, selected: list[tuple[str, int]], text: str) -> dict:
    reasons = []
    idea_states = {"S1-classify", "S2-stress-test", "S2b-idea-map", "S3-route-portfolio", "S9-stuck"}
    if state not in idea_states:
        return {"needed": False, "reasons": reasons}
    if not (project / "IDEA_MAP.md").exists():
        reasons.append("IDEA_MAP.md is missing")
    elif is_blank_idea_map(project):
        if state in {"S2b-idea-map", "S9-stuck"}:
            reasons.append("IDEA_MAP.md has no pattern guess, central object, proof kernel, or central lemma")
    if state == "S2b-idea-map":
        reasons.append("proof state is idea-map")
    if state == "S9-stuck":
        reasons.append("proof state is stuck")
    if selected and max(value for _, value in selected) == 0 and state in {"S1-classify", "S2-stress-test", "S3-route-portfolio"}:
        reasons.append("playbook routing is low-confidence")
    if re.search(r"central lemma:\s*$", text, flags=re.M | re.I):
        reasons.append("ledger has no central lemma recorded")
    return {"needed": bool(reasons), "reasons": reasons}


def pattern_scan_need(project: Path, state: str, selected: list[tuple[str, int]], text: str) -> dict:
    reasons = []
    low_confidence = not selected or max(value for _, value in selected) == 0
    repeated_obstruction = filled_field_count(text, "obstruction type") >= 2
    triggered = (
        state == "S9-stuck"
        or repeated_obstruction
        or (state in {"S1-classify", "S3-route-portfolio"} and low_confidence)
    )
    if not triggered:
        return {"needed": False, "reasons": reasons}
    if not (project / "PATTERN_SCAN.md").exists():
        reasons.append("PATTERN_SCAN.md is missing")
    elif is_blank_pattern_scan(project):
        reasons.append("PATTERN_SCAN.md has no imported source or route yet")
    if state == "S9-stuck":
        reasons.append("proof state is stuck")
    if low_confidence:
        reasons.append("playbook routing is low-confidence")
    if repeated_obstruction:
        reasons.append("two or more obstruction slots are present")
    return {"needed": bool(reasons), "reasons": reasons}


def attempt_fingerprint_summary(project: Path) -> dict:
    path = project / "WORKSTREAMS.md"
    if not path.exists():
        return {"exists": False, "count": 0, "blocked_retry_count": 0, "has_real_entries": False}
    text = path.read_text(encoding="utf-8")
    index_match = re.search(
        r"## Attempt Fingerprint Index(?P<body>.*?)(?:\n## No-Repeat Decision|\Z)",
        text,
        flags=re.S,
    )
    index_text = index_match.group("body") if index_match else ""
    table_entries = 0
    for line in index_text.splitlines():
        if not line.startswith("|"):
            continue
        if "---" in line or "route family" in line.lower():
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0] == "A1" and sum(bool(cell) for cell in cells[1:]) <= 1:
            continue
        if sum(bool(cell) for cell in cells) >= 4:
            table_entries += 1
    blocked = len(re.findall(r"forbidden retry:[^\S\r\n]*\S+", text, flags=re.I))
    fingerprints = len(re.findall(r"obstruction fingerprint:[^\S\r\n]*\S+", text, flags=re.I))
    count = max(table_entries, fingerprints)
    return {
        "exists": True,
        "count": count,
        "blocked_retry_count": blocked,
        "has_real_entries": count > 0,
    }


def filled_field_count(text: str, field: str) -> int:
    return len(
        re.findall(
            rf"^[ \t]*(?:[-*][^\S\r\n]*)?{re.escape(field)}:[^\S\r\n]*\S+",
            text,
            flags=re.I | re.M,
        )
    )


def filled_field_values(text: str, field: str) -> list[str]:
    pattern = rf"^[ \t]*(?:[-*][^\S\r\n]*)?{re.escape(field)}:[^\S\r\n]*(?P<value>\S.*)$"
    return [match.group("value").strip() for match in re.finditer(pattern, text, flags=re.I | re.M)]


def looks_like_template_choice(value: str) -> bool:
    lower = value.strip().lower()
    if not lower:
        return True
    if " / " in lower:
        return True
    if lower in {"pending", "planned", "missing", "candidate", "yes", "no", "unknown"}:
        return True
    return False


def blueprint_rows(text: str) -> list[dict[str, str]]:
    match = re.search(
        r"## Blueprint Dependency Graph(?P<body>.*?)(?:\n## Blueprint Metadata Audit|\Z)",
        text,
        flags=re.S,
    )
    body = match.group("body") if match else ""
    rows = []
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 7:
            continue
        node_id, node_type, status, statement = cells[:4]
        if (
            not node_id
            or node_id.lower() == "node id"
            or set(node_id) <= {"-", ":"}
            or not statement
        ):
            continue
        rows.append(
            {
                "node_id": node_id,
                "type": node_type,
                "status": status.lower(),
                "statement": statement,
                "used_by_assembly": cells[6],
            }
        )
    return rows


def decomposition_admission_summary(project: Path, state: str) -> dict:
    path = project / "LEMMA_QUEUE.md"
    if not path.exists():
        return {
            "active": False,
            "admitted": False,
            "blocks_progress": False,
            "missing_fields": [],
            "required_child_ids": [],
            "unmapped_child_ids": [],
            "proved_required_child_ids": [],
            "proved_unused_nodes": [],
            "parent_replay_status": "not-applicable",
            "recommended_action": "create LEMMA_QUEUE.md before decomposing the theorem",
        }

    text = path.read_text(encoding="utf-8")
    rows = blueprint_rows(text)

    def concrete(field: str) -> str:
        for value in filled_field_values(text, field):
            if not looks_like_template_choice(value):
                return value
        return ""

    parent = concrete("parent node")
    assembly = concrete("conditional parent assembly")
    exact_use = concrete("exact use site for each required child")
    legacy_consumption = concrete("exact use site for each child and post-proof parent replay")
    if not exact_use:
        exact_use = legacy_consumption
    replay = concrete("post-proof parent replay")
    if not replay and legacy_consumption and re.search(
        r"\b(replay|recheck|re-check|verified|passed|failed)\b",
        legacy_consumption,
        flags=re.I,
    ):
        replay = legacy_consumption

    fields = {
        "parent node": parent,
        "conditional parent assembly": assembly,
        "exact use site for each required child": exact_use,
        "why each required child is strictly simpler": concrete(
            "why each required child is strictly simpler"
        ),
        "ancestor-equivalence and cycle check": concrete(
            "ancestor-equivalence and cycle check"
        ),
        "source or statement-fence anchor": concrete("source or statement-fence anchor"),
        "expected repair radius if one child fails": concrete(
            "expected repair radius if one child fails"
        ),
        "jointly sufficient premise bundle or retrieval plan": concrete(
            "jointly sufficient premise bundle or retrieval plan"
        ),
        "reviewer verdict": concrete("reviewer verdict"),
    }
    active_states = {
        "S4-lemma-graph",
        "S5-local-certification",
        "S6-assembly",
        "S7-adversarial-review",
        "S8-finalize",
        "S9-stuck",
    }
    active = any(fields.values()) or (state in active_states and len(rows) >= 2)
    missing = [name for name, value in fields.items() if active and not value]

    def feeds_assembly(value: str) -> bool:
        lower = value.strip().lower()
        return bool(lower) and lower not in {
            "no",
            "false",
            "unknown",
            "n/a",
            "none",
            "yes / no / unknown",
        }

    required_children = [
        row
        for row in rows
        if row["node_id"] != parent and feeds_assembly(row["used_by_assembly"])
    ]
    unmapped = []
    for row in required_children:
        node_id = row["node_id"]
        if exact_use and not re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(node_id)}(?![A-Za-z0-9_])",
            exact_use,
            flags=re.I,
        ):
            unmapped.append(node_id)

    proved_statuses = {"checked", "proved", "tool-checked", "formalized"}
    proved_required = [
        row["node_id"] for row in required_children if row["status"] in proved_statuses
    ]
    proved_unused = [
        row["node_id"]
        for row in rows
        if row["node_id"] != parent
        and row["status"] in proved_statuses
        and not feeds_assembly(row["used_by_assembly"])
    ]

    replay_lower = replay.lower()
    if not replay:
        replay_status = "missing" if proved_required else "not-yet-required"
    elif re.search(r"\b(fail|failed|broken|counterexample)\b", replay_lower):
        replay_status = "failed"
    elif re.search(r"\b(pending|not[- ]?run|todo|unknown|missing)\b", replay_lower):
        replay_status = "pending"
    elif re.search(r"\b(pass|passed|verified|checked|closed|holds|success)\b", replay_lower):
        replay_status = "passed"
    else:
        replay_status = "unclear"

    verdict = fields["reviewer verdict"].lower()
    verdict_admits = bool(re.search(r"\badmit(?:ted)?\b", verdict))
    admitted = active and not missing and not unmapped and verdict_admits
    replay_complete = not proved_required or replay_status == "passed"
    blocks_progress = active and (not admitted or not replay_complete)

    if missing:
        action = "Complete decomposition admission before proving another child: fill " + ", ".join(
            missing
        ) + "."
    elif unmapped:
        action = (
            "Map every required child to an exact parent-proof use site before funding it: "
            + ", ".join(unmapped)
            + "."
        )
    elif not verdict_admits:
        action = "Revise or reject the decomposition; the reviewer verdict does not admit it."
    elif proved_required and replay_status != "passed":
        action = (
            "Replay the conditional parent assembly with the proved child lemmas and record a passed "
            "or failed parent replay before counting them as progress."
        )
    elif proved_unused:
        action = (
            "Retire or rewire proved-but-unused node(s) before funding more side lemmas: "
            + ", ".join(proved_unused)
            + "."
        )
    elif active:
        action = "Proceed with the least-certain required child on the admitted parent assembly path."
    else:
        action = "not activated"

    return {
        "active": active,
        "admitted": admitted,
        "blocks_progress": blocks_progress,
        "missing_fields": missing,
        "required_child_ids": [row["node_id"] for row in required_children],
        "unmapped_child_ids": unmapped,
        "proved_required_child_ids": proved_required,
        "proved_unused_nodes": proved_unused,
        "parent_replay_status": replay_status,
        "recommended_action": action,
    }


def novel_problem_summary(project: Path, mode: str) -> dict:
    path = project / "IDEA_MAP.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""

    def concrete(field: str) -> str:
        for value in filled_field_values(text, field):
            if not looks_like_template_choice(value):
                return value
        return ""

    def normalize_status(raw: str) -> str | None:
        lower = raw.strip().lower()
        if lower in FRONTIER_STATUSES:
            return lower
        if "genuinely new" in lower or lower in {"new", "novel", "new problem"}:
            return "genuinely-new"
        if "apparently open" in lower or lower == "open":
            return "apparently-open"
        if "unknown answer" in lower or "unknown-answer" in lower:
            return "unknown-answer"
        if "likely known" in lower or lower == "likely-known":
            return "likely-known"
        if lower == "known":
            return "known"
        return None

    idea_status = normalize_status(concrete("known-solution status"))
    evidence_path = project / "literature" / "frontier-evidence.json"
    evidence_exists = evidence_path.exists()
    try:
        evidence_data = read_json(evidence_path)
    except (OSError, ValueError):
        evidence_data = {}
    if not isinstance(evidence_data, dict):
        evidence_data = {}
    frontier_data = evidence_data.get("frontier")
    frontier_data = frontier_data if isinstance(frontier_data, dict) else {}
    manifest_status = normalize_status(
        str(frontier_data.get("status") or "")
    )
    status = manifest_status or idea_status

    fields = {
        "frontier scan status": concrete("frontier scan status"),
        "search cutoff date": concrete("search cutoff date"),
        "Scholar queries": concrete("Scholar queries"),
        "verified source anchors": concrete("verified source anchors"),
        "closest known result": concrete("closest known result"),
        "active-work signals": concrete("active-work signals"),
        "current frontier gap": concrete("current frontier gap"),
        "status evidence": concrete("status evidence"),
        "discovery target": concrete("discovery target"),
        "candidate representation": concrete("candidate representation"),
        "validity gate": concrete("validity gate"),
        "score or evaluator": concrete("score or evaluator"),
        "simplification ladder": concrete("simplification ladder"),
        "holdout cases": concrete("holdout cases"),
        "promotion criterion": concrete("promotion criterion"),
        "discovery budget": concrete("discovery budget"),
        "discovered candidate": concrete("discovered candidate"),
        "fixed proof handoff": concrete("fixed proof handoff"),
    }

    frontier_required = mode == "discovery" or idea_status is not None or evidence_exists
    if frontier_required:
        evidence = validate_frontier_bundle(project)
        evidence_errors = list(evidence["errors"])
        if idea_status and manifest_status and idea_status != manifest_status:
            evidence_errors.append("IDEA_MAP.md status conflicts with frontier-evidence.json")
        evidence["errors"] = evidence_errors
        evidence["ok"] = bool(evidence["ok"] and not evidence_errors)
    else:
        evidence = {
            "ok": False,
            "path": str(evidence_path),
            "errors": [],
            "warnings": [],
            "frontier_status": None,
            "counts": {"queries": 0, "papers": 0, "proof_read": 0, "solution_cards": 0},
        }
    frontier_missing = evidence["errors"] if frontier_required else []
    frontier_verified = bool(frontier_required and evidence["ok"] and status)
    frontier_scan_needed = bool(frontier_required and not frontier_verified)
    activated = status in {"apparently-open", "genuinely-new", "unknown-answer"} or (
        mode == "discovery" and status not in {"known", "likely-known"}
    )

    if not activated:
        if frontier_scan_needed:
            action = (
                "Run an external frontier scan before accepting a known/open classification: use Scholar-backed "
                "queries, retrieve and proof-read a lawful full text, save exact anchors and hashes in "
                "literature/frontier-evidence.json, inspect recent public work, and state the exact gap."
            )
        elif status in {"known", "likely-known"}:
            action = "Use the verified closest result for bounded premise retrieval, then continue with the ordinary proof loop."
        else:
            action = "not activated"
        return {
            "activated": False,
            "status": status,
            "frontier_scan_needed": frontier_scan_needed,
            "frontier_verified": frontier_verified,
            "frontier_missing": frontier_missing,
            "frontier_evidence": evidence,
            "missing_setup": [],
            "ready_for_search": False,
            "candidate_found": bool(fields["discovered candidate"]),
            "handoff_ready": bool(fields["fixed proof handoff"]),
            "recommended_action": action,
        }

    missing = []
    for field in [
        "discovery target",
        "candidate representation",
        "validity gate",
        "score or evaluator",
        "simplification ladder",
        "discovery budget",
    ]:
        if not fields[field]:
            missing.append(field)

    candidate_found = bool(fields["discovered candidate"])
    handoff_ready = bool(
        fields["fixed proof handoff"]
        and candidate_found
        and fields["holdout cases"]
        and fields["promotion criterion"]
        and frontier_verified
        and not missing
    )
    if frontier_scan_needed:
        action = (
            "Run an external frontier scan before accepting a known/open classification: use Scholar-backed "
            "queries, retrieve and proof-read a lawful full text, save exact anchors and hashes in "
            "literature/frontier-evidence.json, inspect recent public work, and state the exact gap."
        )
    elif missing:
        action = (
            "Define the novel-problem discovery contract before broad search: target, "
            "candidate representation, validity gate, evaluator, simplification ladder, and budget."
        )
    elif not candidate_found:
        action = (
            "Run one bounded discovery cycle: generate structurally diverse candidates, repair locally, "
            "evaluate exactly, and preserve elite plus informative failed families."
        )
    elif not fields["holdout cases"] or not fields["promotion criterion"]:
        action = (
            "Challenge the discovered candidate on holdout and boundary cases, then state the promotion "
            "criterion before treating it as a theorem target."
        )
    elif not handoff_ready:
        action = (
            "Freeze the promoted candidate and rewrite the unknown-answer problem as one fixed theorem "
            "before starting proof search."
        )
    else:
        action = "Switch to the ordinary proof loop on the fixed handoff statement."

    return {
        "activated": True,
        "status": status,
        "frontier_scan_needed": frontier_scan_needed,
        "frontier_verified": frontier_verified,
        "frontier_missing": frontier_missing,
        "frontier_evidence": evidence,
        "missing_setup": missing,
        "ready_for_search": frontier_verified and not missing,
        "candidate_found": candidate_found,
        "handoff_ready": handoff_ready,
        "recommended_action": action,
    }


def progress_evidence_summary(project: Path) -> dict:
    chunks = []
    for name in ["LEDGER.md", "IDEA_MAP.md", "WORKSTREAMS.md", "ATTACK_MATRIX.md"]:
        path = project / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    unchanged = len(re.findall(r"proof-state delta:[^\S\r\n]*(unchanged|larger)", text, flags=re.I))
    unchanged += len(re.findall(r"\|[^|\n]*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|\s*(unchanged|larger)\s*\|", text, flags=re.I))
    smaller = len(re.findall(r"proof-state delta:[^\S\r\n]*smaller", text, flags=re.I))
    smaller += len(re.findall(r"\|[^|\n]*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|[^|\n]*\|\s*smaller\s*\|", text, flags=re.I))
    blocked = len(
        re.findall(
            r"^(?:[-*]\s*)?(blocked retry|forbidden retry|block-repeat):\s*\S+",
            text,
            flags=re.I | re.M,
        )
    )
    evidence = 0
    for field in [
        "result",
        "external method used",
        "theorem repair, if any",
        "new evidence expected",
        "expected artifact",
        "retrieved theorem",
        "tool certificate",
        "counterexample",
        "missing assumption",
        "verified trick",
        "formalization",
        "verifier verdict",
        "coordinator decision",
        "soundness probe",
        "prover move if using PV",
        "verifier verdict if using PV",
        "soundness probe if using PV",
        "coordinator decision if using PV",
    ]:
        evidence += sum(1 for value in filled_field_values(text, field) if not looks_like_template_choice(value))
    return {
        "unchanged_or_larger_moves": unchanged,
        "smaller_moves": smaller,
        "blocked_retries": blocked,
        "evidence_markers": evidence,
        "no_progress_threshold_met": unchanged >= 2 or blocked >= 1,
    }


def prover_verifier_summary(project: Path) -> dict:
    chunks = []
    has_contract = False
    for name in ["WORKSTREAMS.md", "LEDGER.md"]:
        path = project / name
        if path.exists():
            text = path.read_text(encoding="utf-8")
            has_contract = has_contract or "Prover-Verifier Move Contract" in text or "prover move if using PV" in text
            chunks.append(text)
    text = "\n".join(chunks)
    verdicts = [
        value
        for field in ["verifier verdict", "verifier verdict if using PV"]
        for value in filled_field_values(text, field)
        if not looks_like_template_choice(value)
    ]
    soundness = [
        value
        for field in ["soundness probe", "soundness probe if using PV"]
        for value in filled_field_values(text, field)
        if not looks_like_template_choice(value)
    ]
    decisions = [
        value
        for field in ["coordinator decision", "coordinator decision if using PV"]
        for value in filled_field_values(text, field)
        if not looks_like_template_choice(value)
    ]
    table_entries = 0
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line or "move id" in line.lower():
            continue
        if "PV1" in line and re.search(r"\|\s*PV1\s*\|\s*\|\s*\|", line):
            continue
        if "soundness" in line.lower() or "coordinator" in line.lower():
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0].upper().startswith("PV") and sum(bool(cell) for cell in cells[1:]) >= 3:
            table_entries += 1
    count = max(table_entries, len(verdicts), len(soundness), len(decisions))
    return {
        "has_contract": has_contract,
        "count": count,
        "has_real_entries": count > 0,
    }


def prover_verifier_need(project: Path, progress: dict, summary: dict) -> dict:
    if summary["has_real_entries"]:
        return {"needed": False, "reasons": []}
    chunks = []
    for name in ["WORKSTREAMS.md", "LEDGER.md"]:
        path = project / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    reasons = []
    if progress["no_progress_threshold_met"]:
        reasons.append("the same local proof state has not shrunk")
    challenged = any(
        not looks_like_template_choice(value)
        for field in ["verdict", "verifier verdict", "verifier verdict if using PV"]
        for value in filled_field_values(text, field)
        if value.lower().startswith(("challenge", "trace-back", "re-decompose", "re-plan"))
    ) or bool(re.search(r"\|\s*(challenge|trace-back|re-decompose|re-plan)\s*\|", text, flags=re.I))
    if challenged:
        reasons.append("a local move has already been challenged or sent back")
    hard_to_check = any(
        value.strip().lower() == "hard-to-check"
        for value in filled_field_values(text, "verification tag")
    ) or bool(re.search(r"\|\s*hard-to-check\s*\|", text, flags=re.I))
    if hard_to_check:
        reasons.append("the active step is marked hard-to-check")
    return {"needed": bool(reasons), "reasons": reasons}


def failure_localization_summary(project: Path, progress: dict, pv_need: dict) -> dict:
    chunks = []
    has_board = False
    for name in ["WORKSTREAMS.md", "LEDGER.md"]:
        path = project / name
        if path.exists():
            text = path.read_text(encoding="utf-8")
            has_board = has_board or "Failure Localization And Salvage" in text
            chunks.append(text)
    text = "\n".join(chunks)

    def real_values(field: str) -> list[str]:
        return [
            value
            for value in filled_field_values(text, field)
            if not looks_like_template_choice(value)
        ]

    first_failure = real_values("first failing step")
    verified_prefix = real_values("verified prefix")
    failure_witness = real_values("failure witness or verifier error")
    rescued = real_values("independently rescued artifacts")
    affected = real_values("affected dependents")
    scope = real_values("next scope")
    triggered = progress["no_progress_threshold_met"] or pv_need["needed"]
    needed = triggered and not first_failure

    if needed:
        action = "localize the earliest failing step before route selection"
    elif first_failure and scope:
        action = f"execute {scope[0]} while preserving the verified prefix"
    elif first_failure:
        action = "preserve the verified prefix and repair only the first failing node plus affected dependents"
    else:
        action = "not activated"

    return {
        "has_board": has_board,
        "needed": needed,
        "first_failing_step": first_failure[:1],
        "verified_prefix": verified_prefix[:1],
        "failure_witness": failure_witness[:1],
        "rescued_artifacts": rescued[:1],
        "affected_dependents": affected[:1],
        "next_scope": scope[:1],
        "recommended_action": action,
    }


def failure_stage_summary(project: Path, progress: dict, localization: dict) -> dict:
    chunks = []
    for name in ["WORKSTREAMS.md", "LEDGER.md"]:
        path = project / name
        if path.exists():
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    values = [
        value.strip().lower()
        for value in filled_field_values(text, "failure stage")
        if not looks_like_template_choice(value)
    ]
    stage = values[0] if values else ""
    aliases = {
        "strategy": "strategy-discovery",
        "idea": "strategy-discovery",
        "blueprint": "decomposition",
        "retrieval": "premise-retrieval",
        "premise": "premise-retrieval",
        "local": "local-proof",
        "proof": "local-proof",
        "source": "fidelity",
        "statement": "fidelity",
        "formalization": "library-coverage",
        "library": "library-coverage",
    }
    stage = aliases.get(stage, stage)
    activated = bool(localization["first_failing_step"]) or progress["no_progress_threshold_met"]
    actions = {
        "strategy-discovery": (
            "Run one bounded bottom-up lemma probe: prove or refute one to two special cases or "
            "auxiliary facts, then infer a central object from their shared structure."
        ),
        "decomposition": (
            "Review the decomposition before proving children: require conditional parent assembly, "
            "strict simplification, acyclicity, source fidelity, low repair radius, and premise feasibility."
        ),
        "premise-retrieval": (
            "Run sketch-retrieve-reflect for a jointly sufficient premise bundle; revise the route if "
            "retrieval is empty, individually relevant, or insufficient for assembly."
        ),
        "local-proof": (
            "Repair the first failing local inference with a distinct verifier or tool artifact while "
            "preserving the verified prefix."
        ),
        "assembly": (
            "Write the parent proof conditionally from the available children and isolate the exact "
            "missing bridge before proving another side lemma."
        ),
        "fidelity": (
            "Freeze proof search and repair the statement fence against the original source, definitions, "
            "assumptions, domains, and quantifiers."
        ),
        "library-coverage": (
            "Inventory missing prerequisite definitions and theory. For each project-specific type, "
            "check a positive witness, an exclusion or characterization lemma, and the downstream "
            "properties before building it explicitly; otherwise continue informally without dummy "
            "objects, fake instances, or unproved axioms."
        ),
    }
    needed = activated and stage not in actions and not localization["needed"]
    return {
        "needed": needed,
        "stage": stage or None,
        "recommended_action": actions.get(stage, "classify the failure stage before another attempt"),
        "recognized": stage in actions if stage else False,
        "allowed_stages": list(actions),
    }


def route_decision_summary(state: str, progress: dict, fingerprints: dict, idea_map: dict, pattern_scan: dict) -> dict:
    reasons = []
    decision = "continue"
    next_artifact = "smaller proof state or proved local lemma"

    if progress["no_progress_threshold_met"] or fingerprints["blocked_retry_count"] > 0:
        decision = "re-decompose / retrieve / tool-falsify before another prose attempt"
        next_artifact = "new helper DAG, retrieved theorem pattern, counterexample, certificate, or theorem repair"
        reasons.append("no-progress threshold or blocked retry is present")
    elif progress["smaller_moves"] > 0 and progress["unchanged_or_larger_moves"] == 0:
        decision = "continue current node with local repair"
        next_artifact = "proved local lemma or one smaller subgoal"
        reasons.append("recent proof-state evidence is shrinking")
    elif state in {"S1-classify", "S2-stress-test"} and idea_map["needed"]:
        decision = "run direct-solve or micro pattern check before proving"
        next_artifact = "named theorem/certificate, clear mismatch, or one central object"
        reasons.append("route is low-confidence but not yet in idea-map mode")
    elif state in {"S2b-idea-map", "S3-route-portfolio"} and idea_map["needed"]:
        decision = "run idea pass before proving"
        next_artifact = "central object, proof kernel, central lemma, or verification hook"
        reasons.append("proof route is not yet grounded in a kernel")
    elif pattern_scan["needed"]:
        decision = "retrieve / pattern scan before another same-style route"
        next_artifact = "theorem pattern, hidden assumption, or route repair"
        reasons.append("external pattern scan is needed for this state")
    elif state in {"S4-lemma-graph", "S5-local-certification"}:
        decision = "prove a ready leaf on the assembly path"
        next_artifact = "proved/tool-checked leaf lemma or failed-node diagnosis"
        reasons.append("proof is in local lemma/certification mode")
    elif state == "S9-stuck":
        decision = "escalate before proving"
        next_artifact = "counterexample, certificate, retrieval result, local formalization, or theorem repair"
        reasons.append("proof state is stuck")
    else:
        reasons.append("no repeated-failure signal found")

    return {
        "decision": decision,
        "next_artifact": next_artifact,
        "reasons": reasons,
    }


def external_pattern_queries(
    claim: str,
    selected: list[tuple[str, int]],
    failure_stage: str | None = None,
) -> list[str]:
    queries = []
    if failure_stage in CAPABILITY_QUERIES:
        queries.append(f"{CAPABILITY_QUERIES[failure_stage]} {date.today().year}")
    for name, _ in selected[:2]:
        queries.extend(PATTERN_QUERIES.get(name, []))
    if claim:
        cleaned = " ".join(re.findall(r"[A-Za-z][A-Za-z0-9_-]+", claim)[:18])
        if cleaned:
            queries.append(f"{cleaned} proof theorem assumptions")
            queries.append(f"{cleaned} counterexample missing assumption")
    out = []
    seen = set()
    for query in queries:
        if query not in seen:
            seen.add(query)
            out.append(query)
    return out[:8]


def recommended_files(project: Path, routing: dict, state: str) -> list[str]:
    # Keep recommendations state-local. Older projects may contain a broad
    # routing.json next_files list; loading it here defeats progressive disclosure.
    _ = routing
    state_files = {
        "S0-parse": ["claim.md", "TRIAGE.md"],
        "S1-classify": ["TRIAGE.md", "ATTACK_MATRIX.md", "strategy.md"],
        "S2-stress-test": ["counterexamples.md", "ATTACK_MATRIX.md", "LEDGER.md"],
        "S2b-idea-map": ["IDEA_MAP.md", "counterexamples.md", "ATTACK_MATRIX.md", "LEDGER.md"],
        "S3-route-portfolio": ["WORKSTREAMS.md", "strategy.md", "ATTACK_MATRIX.md", "LEDGER.md"],
        "S4-lemma-graph": ["LEMMA_QUEUE.md", "LEDGER.md"],
        "S5-local-certification": ["TOOL_PLAN.md", "tool_checks/README.md", "LEDGER.md"],
        "S6-assembly": ["LEDGER.md", "writeup"],
        "S7-adversarial-review": ["LEDGER.md", "counterexamples.md"],
        "S8-finalize": ["LEDGER.md", "writeup"],
        "S9-stuck": ["LEDGER.md", "ESCALATION.md"],
    }
    files = state_files.get(state, ["TRIAGE.md", "LEDGER.md"])
    existing = []
    for name in files:
        if name not in existing and (project / name).exists():
            existing.append(name)
    return existing


def primary_action_for(
    mode: str,
    state: str,
    route_decision: dict,
    progress: dict,
    fingerprints: dict,
    novel_problem: dict,
    idea_map: dict,
    pattern_scan: dict,
    pv_need: dict,
    failure_localization: dict,
    failure_stage: dict,
    decomposition: dict,
    audit: dict,
    runtime_feedback: dict,
) -> str:
    finalizing = state in {"S7-adversarial-review", "S8-finalize"}
    if not runtime_feedback["runtime_integrity_ok"]:
        return "Repair the invalid runtime record before continuing: " + runtime_feedback["runtime_errors"][0]
    if finalizing and runtime_feedback["runtime_errors"]:
        return "Repair the invalid or stale runtime evidence before finalizing: " + runtime_feedback["runtime_errors"][0]
    if finalizing and runtime_feedback["invalid_formal_artifacts"]:
        return "Recheck the stale or failed formal evidence before finalizing the proof."
    invalid_artifacts = runtime_feedback["invalid_computation_artifacts"]
    if invalid_artifacts:
        artifact_ids = ", ".join(item["artifact_id"] for item in invalid_artifacts[:3])
        return (
            f"Restore, re-record, or replay invalid computation artifact(s) {artifact_ids}; "
            "their claims cannot count as checked until the local artifact audit passes."
        )
    if runtime_feedback["needs_packet_repair"]:
        first_error = runtime_feedback["first_error"]
        location = first_error.get("location") or "the referee's first unsupported dependency"
        passed = runtime_feedback["passed_claim_ids"]
        suffix = f" Do not rerun already passed artifacts: {', '.join(passed)}." if passed else ""
        return (
            f"Repair the referee packet at {location}: supply the exact missing premise, proof, or "
            f"replayable certificate before resubmitting; do not restart proof search.{suffix}"
        )
    if (
        mode == "recovery"
        and not fingerprints["has_real_entries"]
        and progress["unchanged_or_larger_moves"] == 0
        and progress["blocked_retries"] == 0
    ):
        return "Import the prior failed routes, failure witnesses, and reusable lemmas before proposing a new proof route."
    if decomposition["blocks_progress"]:
        return decomposition["recommended_action"]
    if novel_problem["frontier_scan_needed"]:
        return novel_problem["recommended_action"]
    if state == "S8-finalize" and audit["ready_for_final_proof"]:
        return "Present the proof with its verified status and essential assumptions."
    if state in {"S7-adversarial-review", "S8-finalize"} and not audit["ready_for_final_proof"]:
        return "Close the blocking ledger and verification-gate gaps before presenting the proof."
    if novel_problem["activated"] and not novel_problem["handoff_ready"]:
        return novel_problem["recommended_action"]
    if failure_localization["needed"]:
        return "Localize the earliest failing step, freeze the verified prefix, and salvage independent artifacts before choosing another route."
    if failure_stage["needed"]:
        return "Classify the first failure as strategy, decomposition, premise retrieval, local proof, assembly, fidelity, or library coverage before choosing a repair."
    if failure_stage["stage"] and failure_stage["stage"] != "local-proof":
        return failure_stage["recommended_action"]
    if failure_localization["first_failing_step"] and failure_localization["next_scope"]:
        return (
            f"Execute the localized scope: {failure_localization['next_scope'][0]}; "
            "preserve the verified prefix and repair only affected dependents."
        )
    # A failed formal node can require a new premise or mathematical repair;
    # repeating its checker is not a substitute for that named nonfinal work.
    # Its evidence remains invalid, so none of these routes can finalize it.
    if runtime_feedback["runtime_errors"]:
        return "Resolve the stale proof acceptance before reusing its checked status: " + runtime_feedback["runtime_errors"][0]
    if runtime_feedback["invalid_formal_artifacts"]:
        return "Inspect the stale or failed formal node and identify its repair before reusing its checked status."
    if progress["no_progress_threshold_met"] or state == "S9-stuck":
        return f"Execute the route decision: {route_decision['decision']}; produce {route_decision['next_artifact']}."
    if pv_need["needed"]:
        return "Run one Prover-Verifier Move Contract on the active fragile step before another prose attempt."
    if idea_map["needed"]:
        return "Identify one central object and proof kernel with a concrete verification hook."
    if pattern_scan["needed"]:
        return "Run one bounded pattern scan and import only a theorem pattern or hidden assumption that changes the next move."
    if state in {"S4-lemma-graph", "S5-local-certification"}:
        return f"Execute the route decision: {route_decision['decision']}; produce {route_decision['next_artifact']}."
    return STATE_ACTIONS.get(state, STATE_ACTIONS["S9-stuck"])[0]


def diagnose(project: Path) -> dict:
    ledger = project / "LEDGER.md"
    if not ledger.exists():
        raise SystemExit(f"LEDGER.md not found in {project}")
    text = ledger.read_text(encoding="utf-8")
    routing = read_json(project / "routing.json")
    claim = section_body(text, "Claim") or routing.get("claim", "")
    state = (section_body(text, "Proof State") or "S0-parse").splitlines()[0].strip()
    verification = (section_body(text, "Verification Status") or "conjecture").splitlines()[0].strip()
    status = (section_body(text, "Status") or "open").splitlines()[0].strip()
    mode_body = section_body(text, "Mode Decision") or ""
    mode_match = re.search(r"^[ \t]*-[ \t]*mode:[ \t]*(\S+)", mode_body, flags=re.I | re.M)
    mode = mode_match.group(1) if mode_match else routing.get("mode", "project")
    stored_selected = routing.get("selected_playbooks") or []
    rerouted = route_from_claim(claim)
    if rerouted and max(value for _, value in rerouted) > 0:
        selected = rerouted
    elif stored_selected and any(value > 0 for _, value in stored_selected):
        selected = stored_selected
    else:
        selected = rerouted
    audit = audit_text(text, ledger)
    novel_problem = novel_problem_summary(project, mode)
    idea_map = idea_map_need(project, state, selected, text)
    pattern_scan = pattern_scan_need(project, state, selected, text)
    fingerprints = attempt_fingerprint_summary(project)
    progress = progress_evidence_summary(project)
    prover_verifier = prover_verifier_summary(project)
    pv_need = prover_verifier_need(project, progress, prover_verifier)
    failure_localization = failure_localization_summary(project, progress, pv_need)
    failure_stage = failure_stage_summary(project, progress, failure_localization)
    decomposition = decomposition_admission_summary(project, state)
    route_decision = route_decision_summary(state, progress, fingerprints, idea_map, pattern_scan)
    runtime_feedback = runtime_referee_feedback(project)
    audit["runtime_evidence_ready"] = not (
        runtime_feedback["invalid_computation_artifacts"]
        or runtime_feedback["invalid_formal_artifacts"]
        or runtime_feedback["runtime_errors"]
    )
    audit["frontier_evidence_ready"] = not novel_problem["frontier_scan_needed"]
    audit["decomposition_ready"] = not decomposition["blocks_progress"]
    if not audit["runtime_evidence_ready"]:
        audit["ready_for_final_proof"] = False
    if not audit["decomposition_ready"]:
        audit["ready_for_final_proof"] = False
    if not audit["frontier_evidence_ready"]:
        audit["ready_for_final_proof"] = False

    actions = []
    actions.extend(runtime_feedback["runtime_errors"])
    for artifact in runtime_feedback["invalid_formal_artifacts"]:
        actions.append(
            f"Formal evidence repair for {artifact['node_id']}: " + "; ".join(artifact["errors"])
        )
    if runtime_feedback["invalid_computation_artifacts"]:
        invalid_ids = ", ".join(
            item["artifact_id"] for item in runtime_feedback["invalid_computation_artifacts"][:3]
        )
        actions.append(
            "Computation evidence repair: restore the original project-local artifact or record and "
            f"replay a replacement for {invalid_ids}."
        )
    if runtime_feedback["needs_packet_repair"]:
        first_error = runtime_feedback["first_error"]
        actions.append(
            "Referee evidence repair: attach or prove the first unsupported dependency at "
            f"{first_error.get('location') or 'the recorded first-error location'}."
        )
        if runtime_feedback["passed_claim_ids"]:
            actions.append(
                "Preserve and do not rerun passed computation claims: "
                + ", ".join(runtime_feedback["passed_claim_ids"])
                + "."
            )
    if not (project / "ATTACK_MATRIX.md").exists():
        actions.append("Create ATTACK_MATRIX.md with one proof route and one falsification route.")
    if not (project / "LEMMA_QUEUE.md").exists():
        actions.append("Create LEMMA_QUEUE.md as a blueprint DAG with nodes, statement deps, proof deps, downstream use, statuses, and failure diagnoses.")
    elif decomposition["active"]:
        actions.append(f"Decomposition admission: {decomposition['recommended_action']}")
    if novel_problem["frontier_scan_needed"] or novel_problem["activated"]:
        actions.append(f"Novel-problem discovery: {novel_problem['recommended_action']}")
    if not (project / "WORKSTREAMS.md").exists() and state in {"S3-route-portfolio", "S5-local-certification", "S7-adversarial-review", "S9-stuck"}:
        actions.append("Create WORKSTREAMS.md with approved goals, bounded workstream cards, and a look-at-how-others-do-it gate.")
    fingerprint_recovery_needed = (
        mode == "recovery"
        or state == "S9-stuck"
        or progress["no_progress_threshold_met"]
        or filled_field_count(text, "obstruction type") > 0
    )
    if (
        state in {"S3-route-portfolio", "S4-lemma-graph", "S9-stuck"}
        and fingerprints["exists"]
        and not fingerprints["has_real_entries"]
        and fingerprint_recovery_needed
    ):
        actions.append("Fill the Attempt Fingerprint Index in WORKSTREAMS.md before trying another similar route or construction.")
    elif state in {"S3-route-portfolio", "S4-lemma-graph", "S9-stuck"} and fingerprints["has_real_entries"]:
        actions.append(f"Compare the next attempt against {fingerprints['count']} recorded attempt fingerprint(s) before proceeding.")
    if progress["no_progress_threshold_met"]:
        actions.append("No-progress threshold met: do not retry prose. Switch to counterexample search, tools, retrieval, local formalization, theorem repair, or user steering.")
    if state in {"S4-lemma-graph", "S5-local-certification", "S9-stuck"}:
        actions.append(f"Route decision: {route_decision['decision']}; expected artifact: {route_decision['next_artifact']}.")
    if decomposition["proved_unused_nodes"]:
        actions.append(
            "Do not count proved-but-unused nodes as parent progress; retire or rewire: "
            + ", ".join(decomposition["proved_unused_nodes"])
            + "."
        )
    if pv_need["needed"]:
        actions.append("Fill the Prover-Verifier Move Contract for the fragile move before another prose retry.")
    if failure_localization["needed"]:
        actions.append("Fill Failure Localization And Salvage: first failing step, failure witness, verified prefix, rescued artifacts, and affected dependents.")
    elif failure_localization["first_failing_step"]:
        actions.append("Preserve the verified prefix and independently rescued artifacts; repair only the first failing node and affected dependents.")
    if failure_stage["needed"]:
        actions.append("Classify the failure stage before allocating another proof, retrieval, tool, or formalization attempt.")
    elif failure_stage["stage"]:
        actions.append(f"Failure-stage action ({failure_stage['stage']}): {failure_stage['recommended_action']}")
    actions.extend(STATE_ACTIONS.get(state, STATE_ACTIONS["S9-stuck"]))
    if idea_map["needed"] and state in {"S1-classify", "S2-stress-test", "S2b-idea-map", "S3-route-portfolio", "S9-stuck"}:
        actions.append("Use IDEA_MAP.md as an optional idea pass: failure world, pattern guess, central object, proof kernel, central lemma, verification hook.")
    if idea_map["needed"] or pattern_scan["needed"]:
        actions.append("If direct solve is unavailable, mine prior papers, local drafts, appendices, or ledgers for a transferable proof architecture.")
        actions.append("Save only useful paper tricks as short local trick cards; do not promote them globally until validated or reused.")
    if pattern_scan["needed"]:
        actions.append("Derive one capability query from the missing artifact and failure stage; do not wait for the user to name a tool, database, or paper.")
    if (project / "ESCALATION.md").exists() and filled_field_count(text, "obstruction type") >= 2:
        actions.append("Two or more failed-route slots are present; run the escalation ladder before trying another route.")
    if audit["placeholder_count"]:
        actions.append("Fill ledger placeholders before presenting a final proof.")
    if not (project / "TOOL_PLAN.md").exists():
        actions.append("Create TOOL_PLAN.md before relying on CAS/SMT/optimization/Lean output in the proof.")
    if pattern_scan["needed"] and state in {"S1-classify", "S3-route-portfolio", "S9-stuck"}:
        actions.append("Fill PATTERN_SCAN.md with one extraction card and route scorecard before another same-style proof route.")
    if any("gate" in pat.lower() for pat in audit["placeholders"]):
        actions.append("Complete all verification gates: pre-solve, statement, assumption, negation, toy-model, pattern, lemma, proof-state, step-verdict when relevant, quantifier, boundary, assembly, review, progress.")
    if "S9-stuck" in state:
        actions.append("Use ESCALATION.md before another prose proof attempt; record the external method and result in LEDGER.md.")
        actions.append("Name the smallest missing lemma or false condition, then switch route or repair the theorem.")

    files = recommended_files(project, routing, state)
    if novel_problem["activated"] and (project / "IDEA_MAP.md").exists() and "IDEA_MAP.md" not in files:
        files.insert(0, "IDEA_MAP.md")
    if idea_map["needed"] and (project / "IDEA_MAP.md").exists() and "IDEA_MAP.md" not in files:
        files.insert(0, "IDEA_MAP.md")
    if pattern_scan["needed"] and (project / "PATTERN_SCAN.md").exists() and "PATTERN_SCAN.md" not in files:
        files.insert(0, "PATTERN_SCAN.md")
    if (
        pv_need["needed"]
        or fingerprint_recovery_needed
        or fingerprints["has_real_entries"]
    ) and (project / "WORKSTREAMS.md").exists() and "WORKSTREAMS.md" not in files:
        files.insert(0, "WORKSTREAMS.md")
    if decomposition["active"] and (project / "LEMMA_QUEUE.md").exists() and "LEMMA_QUEUE.md" not in files:
        files.insert(0, "LEMMA_QUEUE.md")
    verification_path = runtime_feedback.get("verification_path")
    if isinstance(verification_path, str) and verification_path and verification_path not in files:
        files.insert(0, verification_path)

    primary_action = primary_action_for(
        mode,
        state,
        route_decision,
        progress,
        fingerprints,
        novel_problem,
        idea_map,
        pattern_scan,
        pv_need,
        failure_localization,
        failure_stage,
        decomposition,
        audit,
        runtime_feedback,
    )
    ordered_actions = [primary_action]
    for action in actions:
        if action not in ordered_actions:
            ordered_actions.append(action)

    return {
        "project": str(project),
        "claim": claim,
        "mode": mode,
        "status": status,
        "verification_status": verification,
        "proof_state": state,
        "selected_playbooks": selected,
        "recommended_files": files,
        "primary_action": primary_action,
        "next_actions": ordered_actions[:6],
        "novel_problem": novel_problem,
        "idea_map": idea_map,
        "external_pattern_scan": {
            **pattern_scan,
            "queries": external_pattern_queries(
                claim,
                selected,
                failure_stage.get("stage"),
            ) if pattern_scan["needed"] else [],
            "capability_admission": [
                "adds a missing artifact or independent evidence channel",
                "has a primary source and an inspectable active implementation",
                "fits the project's privacy and trust boundary",
                "passes one bounded live probe before adoption",
            ],
            "scorecard_fields": [
                "route",
                "retrieved premise or theorem",
                "evidence type",
                "dependency value",
                "certificate availability",
                "failure risk",
                "next experiment",
            ],
        },
        "attempt_fingerprints": fingerprints,
        "progress_evidence": progress,
        "prover_verifier": {**prover_verifier, **pv_need},
        "failure_localization": failure_localization,
        "failure_stage": failure_stage,
        "decomposition_admission": decomposition,
        "route_decision": route_decision,
        "latest_referee": runtime_feedback,
        "audit": audit,
    }


def print_human(result: dict) -> None:
    print(f"project: {result['project']}")
    print(f"state: {result['proof_state']}")
    print(f"mode: {result['mode']}")
    print(f"status: {result['status']} / {result['verification_status']}")
    print("selected playbooks:")
    for name, value in result["selected_playbooks"]:
        print(f"- {name} (score {value})")
    print("recommended files:")
    for name in result["recommended_files"]:
        print(f"- {name}")
    print("primary action:")
    print(f"- {result['primary_action']}")
    print("supporting actions:")
    for action in result["next_actions"][1:]:
        print(f"- {action}")
    referee = result["latest_referee"]
    print("latest referee:")
    print(f"- available: {referee['available']}")
    print(f"- verdict: {referee['verdict']}")
    print(f"- run_id: {referee['run_id']}")
    print(f"- review_scope: {referee['review_scope']}")
    print(f"- candidate_proof_sha256: {referee['candidate_proof_sha256']}")
    if referee["raw_verdict"] != referee["verdict"]:
        print(f"- raw_verdict: {referee['raw_verdict']}")
    print(f"- failure_kind: {referee['failure_kind']}")
    print(f"- first_error: {referee['first_error']}")
    print(f"- passed_claim_ids: {referee['passed_claim_ids']}")
    print(f"- passed_artifact_ids: {referee['passed_artifact_ids']}")
    print(f"- invalid_computation_artifacts: {referee['invalid_computation_artifacts']}")
    print(f"- superseded_computation_artifacts: {referee['superseded_computation_artifacts']}")
    print(f"- computation_warnings: {referee['computation_warnings']}")
    print(f"- runtime_errors: {referee['runtime_errors']}")
    print(f"- invalid_formal_artifacts: {referee['invalid_formal_artifacts']}")
    novel = result["novel_problem"]
    print("novel problem discovery:")
    print(f"- activated: {novel['activated']}")
    print(f"- status: {novel['status']}")
    print(f"- frontier_scan_needed: {novel['frontier_scan_needed']}")
    print(f"- frontier_verified: {novel['frontier_verified']}")
    for field in novel["frontier_missing"]:
        print(f"- frontier_missing: {field}")
    print(f"- ready_for_search: {novel['ready_for_search']}")
    print(f"- candidate_found: {novel['candidate_found']}")
    print(f"- handoff_ready: {novel['handoff_ready']}")
    for field in novel["missing_setup"]:
        print(f"- missing: {field}")
    print(f"- recommended_action: {novel['recommended_action']}")
    idea = result["idea_map"]
    if idea["needed"]:
        print("idea map:")
        for reason in idea["reasons"]:
            print(f"- reason: {reason}")
    scan = result["external_pattern_scan"]
    if scan["needed"]:
        print("external pattern scan:")
        for reason in scan["reasons"]:
            print(f"- reason: {reason}")
        for query in scan["queries"][:5]:
            print(f"- query: {query}")
    fingerprints = result["attempt_fingerprints"]
    if fingerprints["exists"]:
        print("attempt fingerprints:")
        print(f"- count: {fingerprints['count']}")
        print(f"- blocked retries: {fingerprints['blocked_retry_count']}")
    progress = result["progress_evidence"]
    print("progress evidence:")
    print(f"- unchanged_or_larger_moves: {progress['unchanged_or_larger_moves']}")
    print(f"- smaller_moves: {progress['smaller_moves']}")
    print(f"- blocked_retries: {progress['blocked_retries']}")
    print(f"- evidence_markers: {progress['evidence_markers']}")
    pv = result["prover_verifier"]
    print("prover-verifier:")
    print(f"- contract_available: {pv['has_contract']}")
    print(f"- recorded_moves: {pv['count']}")
    print(f"- needed_now: {pv['needed']}")
    for reason in pv["reasons"]:
        print(f"- reason: {reason}")
    localization = result["failure_localization"]
    print("failure localization:")
    print(f"- needed_now: {localization['needed']}")
    print(f"- first_failing_step: {localization['first_failing_step']}")
    print(f"- verified_prefix: {localization['verified_prefix']}")
    print(f"- rescued_artifacts: {localization['rescued_artifacts']}")
    print(f"- recommended_action: {localization['recommended_action']}")
    failure_stage = result["failure_stage"]
    print("failure stage:")
    print(f"- needed_now: {failure_stage['needed']}")
    print(f"- stage: {failure_stage['stage']}")
    print(f"- recognized: {failure_stage['recognized']}")
    print(f"- recommended_action: {failure_stage['recommended_action']}")
    decomposition = result["decomposition_admission"]
    print("decomposition admission:")
    print(f"- active: {decomposition['active']}")
    print(f"- admitted: {decomposition['admitted']}")
    print(f"- blocks_progress: {decomposition['blocks_progress']}")
    print(f"- missing_fields: {decomposition['missing_fields']}")
    print(f"- unmapped_child_ids: {decomposition['unmapped_child_ids']}")
    print(f"- proved_unused_nodes: {decomposition['proved_unused_nodes']}")
    print(f"- parent_replay_status: {decomposition['parent_replay_status']}")
    print(f"- recommended_action: {decomposition['recommended_action']}")
    route = result["route_decision"]
    print("route decision:")
    print(f"- decision: {route['decision']}")
    print(f"- next_artifact: {route['next_artifact']}")
    for reason in route["reasons"]:
        print(f"- reason: {reason}")
    print(f"ready_for_final_proof: {result['audit']['ready_for_final_proof']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose the next move for a theory proof project.")
    parser.add_argument("project", help="Proof project directory containing LEDGER.md")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    result = diagnose(Path(args.project))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
