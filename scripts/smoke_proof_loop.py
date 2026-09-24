#!/usr/bin/env python3
"""Smoke-test the bounded proof loop with an isolated mock Codex executable."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from proof_loop import (
    generation_domain_seed_packet,
    packet_retired_routes,
    remember_retired_route,
    scout_domain_seed_packet,
    prior_untried_routes,
)


ROOT = Path(__file__).resolve().parents[1]
PROOF_LOOP = ROOT / "scripts" / "proof_loop.py"

MOCK_CODEX = r'''#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
output = Path(args[args.index("--output-last-message") + 1])
packet = json.loads((Path.cwd() / "packet.json").read_text(encoding="utf-8"))
scenario = os.environ.get("MOCK_PROOF_SCENARIO", "accept")

if output.name == "scout.json":
    role = packet["scout_role"]["name"]
    if scenario == "hard_blocked":
        payload = {
            "status": "blocked",
            "summary": "The decisive sign cannot be derived from the packet.",
            "route_family": "",
            "central_object": "the parity remainder",
            "key_original_step": "",
            "plan_steps": [],
            "conditional_assembly": [],
            "decisive_check": "",
            "assumptions_used": ["n is an integer"],
            "novelty_against_failures": "No attemptable route was found.",
            "obstruction": "An exact sign certificate for the parity remainder is missing.",
            "requested_capability": "symbolic",
        }
    elif role == "structural":
        payload = {
            "status": "route",
            "summary": "Factor the product through the even member of a consecutive pair.",
            "route_family": "consecutive-factor parity",
            "central_object": "the even member of n and n+1",
            "key_original_step": "write the even member as twice an integer",
            "plan_steps": [
                "Split according to the parity of n.",
                "Write the even member of the consecutive pair as twice an integer.",
                "Substitute into n(n+1) and conclude divisibility by two.",
            ],
            "conditional_assembly": [
                "The factor two in either case proves the original universal divisibility claim."
            ],
            "decisive_check": "Verify both residue classes modulo two without changing the domain.",
            "assumptions_used": ["n is an integer"],
            "novelty_against_failures": "It exposes the controlling member instead of assuming the product is even.",
            "obstruction": "",
            "requested_capability": "none",
        }
    else:
        payload = {
            "status": "route",
            "summary": "Use the product modulo two as a direct falsification-resistant route.",
            "route_family": "residue-class product",
            "central_object": "the pair of residues n mod 2 and n+1 mod 2",
            "key_original_step": "show one of the two residues is zero",
            "plan_steps": [
                "Enumerate the two residue classes of n modulo two.",
                "Show the adjacent residue is zero in the nonzero case.",
                "Multiply the residues and lift divisibility back to the integers.",
            ],
            "conditional_assembly": [
                "A zero product residue is equivalent to divisibility of n(n+1) by two."
            ],
            "decisive_check": "Evaluate the two possible residues of n modulo two.",
            "assumptions_used": ["n is an integer"],
            "novelty_against_failures": "It uses a residue representation rather than factor naming.",
            "obstruction": "",
            "requested_capability": "none",
        }
elif output.name == "selection.json":
    candidates = packet["candidates"]
    selected = candidates[0]["candidate_id"]
    payload = {
        "decision": "selected",
        "selected_candidate_id": selected,
        "selection_reason": "The route exposes the factor two and closes the exact claim.",
        "execution_focus": "Prove the parity split completely and keep both integer cases explicit.",
        "rejected_candidates": [
            {
                "candidate_id": candidate["candidate_id"],
                "disposition": "defer",
                "reason": "Plausible but not needed for this attempt.",
            }
            for candidate in candidates[1:]
        ],
        "obstruction": "",
        "requested_capability": "none",
    }
elif output.name == "generation.json":
    iteration = int(packet["iteration"])
    if scenario in {"blocked", "hard_revisit"}:
        payload = {
            "status": "blocked",
            "candidate_kind": "none",
            "summary": "The sign of the kernel is unresolved.",
            "route_family": "direct inequality",
            "central_object": "the derivative gap",
            "proof_kernel": "the derivative gap is nonnegative",
            "assumptions_used": ["x is real"],
            "candidate_markdown": "",
            "obstruction": "The derivative gap has no established sign.",
            "requested_capability": "symbolic",
        }
    elif scenario == "refutation":
        payload = {
            "status": "candidate",
            "candidate_kind": "refutation",
            "summary": "The universal claim fails at one.",
            "route_family": "explicit counterexample",
            "central_object": "the integer one",
            "proof_kernel": "one is not divisible by two",
            "assumptions_used": ["n is an integer"],
            "candidate_markdown": "# Counterexample\n\nTake n=1. It is an integer but is not even.\n",
            "obstruction": "",
            "requested_capability": "none",
        }
    elif scenario in {"retrieval", "retrieval_twice"} and (
        iteration == 1 or scenario == "retrieval_twice"
    ):
        payload = {
            "status": "blocked",
            "candidate_kind": "none",
            "summary": "A named parity premise is missing.",
            "route_family": "parity",
            "central_object": "two consecutive residues",
            "proof_kernel": "one of two consecutive integers is even",
            "assumptions_used": ["n is an integer"],
            "candidate_markdown": "",
            "obstruction": "Retrieve and check the standard consecutive-parity lemma.",
            "requested_capability": "retrieval",
        }
    elif scenario == "new_representation" and iteration == 1:
        payload = {
            "status": "blocked",
            "candidate_kind": "none",
            "summary": "The factorization representation is not shrinking the goal.",
            "route_family": "factorization",
            "central_object": "an integer factorization",
            "proof_kernel": "extract a factor two directly",
            "assumptions_used": ["n is an integer"],
            "candidate_markdown": "",
            "obstruction": "The same divisibility obligation survives unchanged.",
            "requested_capability": "new-representation",
        }
    elif scenario == "expert_consultation":
        payload = {
            "status": "blocked",
            "candidate_kind": "none",
            "summary": "The equality cases determine constraints but not the missing construction.",
            "route_family": "equality-driven construction",
            "central_object": "a feasible extremal certificate",
            "proof_kernel": "construct a certificate satisfying all boundary and coupling constraints",
            "assumptions_used": ["the feasible region is nonempty"],
            "candidate_markdown": "",
            "obstruction": "Local tools can check a proposed certificate but do not suggest the missing ansatz.",
            "requested_capability": "expert-consultation",
        }
    else:
        bad = (scenario == "repair" and iteration == 1) or (
            scenario == "replan" and iteration <= 2
        ) or (scenario == "repair_rename" and iteration <= 2)
        replanned = scenario == "replan" and iteration >= 3
        renamed = scenario == "repair_rename" and iteration == 2
        renamed_replan = scenario == "repair_rename" and iteration >= 3
        payload = {
            "status": "candidate",
            "candidate_kind": "proof",
            "summary": "A direct parity proof.",
            "route_family": (
                "consecutive residues"
                if replanned or renamed_replan
                else "renamed divisibility route"
                if renamed
                else "parity"
            ),
            "central_object": (
                "residues modulo two"
                if replanned or renamed_replan
                else "a relabeled factor pair"
                if renamed
                else "an integer factorization"
            ),
            "proof_kernel": (
                "one residue vanishes modulo two"
                if renamed
                else "the product contains a factor two"
            ),
            "assumptions_used": ["n is an integer"],
            "candidate_markdown": "# Proof\n\n" + ("Bad proof.\n" if bad else "Write n(n+1)=2k for an integer k. Hence the product is even.\n"),
            "obstruction": "",
            "requested_capability": "none",
        }
else:
    proof = packet["candidate_proof"]
    bad = "Bad proof" in proof
    payload = {
        "summary": "The candidate has a gap." if bad else "The proof is complete.",
        "claim_fidelity": {"status": "pass", "issue": ""},
        "assumption_coverage": {"status": "pass", "issue": ""},
        "failure_kind": "mathematical-error" if bad else "none",
        "first_error": {"location": "proof", "issue": "No argument is given."} if bad else {"location": "", "issue": ""},
        "critical_errors": [{"location": "proof", "issue": "No argument is given."}] if bad else [],
        "gaps": [],
        "verdict": "wrong" if bad else "correct",
        "repair_hints": ["Supply the parity factorization."] if bad else [],
    }

output.write_text(json.dumps(payload), encoding="utf-8")
'''


def run_scenario(
    root: Path,
    codex: Path,
    scenario: str,
    max_iterations: int,
    *,
    allow_search: bool = False,
    hard_exploration: bool = False,
    project_name: str | None = None,
) -> dict:
    project = root / (project_name or scenario)
    env = os.environ.copy()
    env["MOCK_PROOF_SCENARIO"] = scenario
    claim = (
        "For every integer n, n is even."
        if scenario == "refutation"
        else "For every integer n, n(n+1) is even."
    )
    command = [
            sys.executable,
            str(PROOF_LOOP),
            str(project),
            "--claim",
            claim,
            "--max-iterations",
            str(max_iterations),
            "--codex-bin",
            str(codex),
        ]
    if allow_search:
        command.append("--allow-search")
    if hard_exploration:
        command.append("--hard-exploration")
    completed = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"scenario {scenario} failed: {completed.stderr.strip() or completed.stdout.strip()}"
        )
    result = json.loads(completed.stdout)
    result["project"] = str(project)
    return result


def prepare_packet(root: Path, name: str, claim: str) -> tuple[dict, dict, str]:
    project = root / name
    completed = subprocess.run(
        [
            sys.executable,
            str(PROOF_LOOP),
            str(project),
            "--claim",
            claim,
            "--prepare-only",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    result = (
        json.loads(completed.stdout)
        if completed.returncode == 0 and completed.stdout.strip()
        else {}
    )
    run_dir = Path(result.get("run_dir", root / "missing-run"))
    packet = (
        json.loads((run_dir / "packet.json").read_text(encoding="utf-8"))
        if (run_dir / "packet.json").is_file()
        else {}
    )
    instructions = (
        (run_dir / "AGENTS.md").read_text(encoding="utf-8")
        if (run_dir / "AGENTS.md").is_file()
        else ""
    )
    return result, packet, instructions


def main() -> int:
    checks: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="proof-loop-smoke-") as raw:
        root = Path(raw)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        codex = bin_dir / "codex"
        codex.write_text(MOCK_CODEX, encoding="utf-8")
        codex.chmod(0o755)

        prepared, prepared_packet, prepared_agents = prepare_packet(
            root,
            "domain-seed",
            "In a discounted dynamic program, an optimal policy has a threshold structure.",
        )
        _, ambiguous_packet, _ = prepare_packet(
            root,
            "ambiguous-domain",
            "A theorem combining a dynamic program and mechanism design.",
        )
        checks.append(
            {
                "name": "high-leverage-domain-seeds-reach-agent-packet",
                "ok": prepared.get("status") == "prepared"
                and prepared_packet.get("domain_seed", {}).get("playbook")
                == "dp-proof-playbook.md"
                and prepared_packet.get("domain_seed", {}).get("proof_effect") == "none"
                and bool(
                    prepared_packet.get("domain_seed", {}).get("central_object_hints")
                )
                and ambiguous_packet.get("domain_seed") == {}
                and generation_domain_seed_packet(
                    "In a discounted dynamic program, an optimal policy is threshold.",
                    "repair",
                    None,
                )
                == {}
                and generation_domain_seed_packet(
                    "In a discounted dynamic program, an optimal policy is threshold.",
                    "solve",
                    {"route_family": "fixed plan"},
                )
                == {}
                and generation_domain_seed_packet(
                    "In a discounted dynamic program, an optimal policy is threshold.",
                    "replan",
                    None,
                ).get("playbook")
                == "dp-proof-playbook.md"
                and scout_domain_seed_packet(
                    "In a discounted dynamic program, an optimal policy is threshold.",
                    "structural",
                ).get("playbook")
                == "dp-proof-playbook.md"
                and scout_domain_seed_packet(
                    "In a discounted dynamic program, an optimal policy is threshold.",
                    "adversarial",
                )
                == {}
                and bool(prepared_agents.strip()),
            }
        )

        retired_fixture = {
            f"{index:064x}": {
                "route_signature": f"{index:064x}",
                "route_family": f"route-{index}",
                "central_object": f"object-{index}",
                "proof_kernel": f"kernel-{index}",
                "failure": f"failure-{index}",
            }
            for index in range(20)
        }
        bounded_retired = packet_retired_routes(retired_fixture)
        remember_retired_route(
            retired_fixture,
            f"{8:064x}",
            {
                "route_signature": f"{8:064x}",
                "route_family": "route-8-refreshed",
                "central_object": "object-8",
                "proof_kernel": "kernel-8",
                "failure": "failure-8-refreshed",
            },
        )
        refreshed_retired = packet_retired_routes(retired_fixture)
        checks.append(
            {
                "name": "retired-route-packet-context-is-bounded",
                "ok": len(bounded_retired) == 12
                and bounded_retired[0].get("route_family") == "route-8"
                and bounded_retired[-1].get("route_family") == "route-19"
                and len(refreshed_retired) == 12
                and refreshed_retired[0].get("route_family") == "route-9"
                and refreshed_retired[-1].get("route_family")
                == "route-8-refreshed",
            }
        )

        accepted = run_scenario(root, codex, "accept", 2)
        checks.append(
            {
                "name": "one-route-cold-referee-acceptance",
                "ok": accepted.get("status") == "referee-accepted"
                and accepted.get("iterations_completed") == 1
                and accepted.get("proof_status") == "referee-accepted"
                and accepted.get("evidence_summary", {}).get("human_reviewed") is False,
            }
        )

        refuted = run_scenario(root, codex, "refutation", 2)
        referee_packet = json.loads(
            next(
                (
                    Path(refuted["project"])
                    / ".proof_runtime"
                    / "referee_runs"
                ).glob("*/packet.json")
            ).read_text(encoding="utf-8")
        )
        checks.append(
            {
                "name": "explicit-refutation-disposition",
                "ok": refuted.get("status") == "referee-accepted"
                and refuted.get("candidate_kind") == "refutation"
                and refuted.get("proof_status") == "referee-accepted"
                and refuted.get("evidence_summary", {}).get("disposition") == "refutation"
                and referee_packet.get("candidate_kind") == "refutation"
                and any(
                    json.loads(line).get("record", {}).get("status") == "referee-accepted"
                    for line in (
                        Path(refuted["project"])
                        / ".proof_runtime"
                        / "channels"
                        / "counterexamples.jsonl"
                    ).read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ),
            }
        )

        replanned = run_scenario(root, codex, "replan", 4)
        replan_packet = json.loads(
            (
                Path(replanned["project"])
                / ".proof_runtime"
                / "proof_loop_runs"
                / replanned["run_id"]
                / "iteration-03"
                / "packet.json"
            ).read_text(encoding="utf-8")
        )
        checks.append(
            {
                "name": "repeated-route-retirement-and-replan",
                "ok": replanned.get("status") == "referee-accepted"
                and replanned.get("iterations_completed") == 3
                and replan_packet.get("mode") == "replan"
                and replan_packet.get("previous_candidate") is None
                and replan_packet.get("retired_routes", [{}])[0].get("route_family") == "parity",
            }
        )

        renamed = run_scenario(root, codex, "repair_rename", 3)
        renamed_packet = json.loads(
            (
                Path(renamed["project"])
                / ".proof_runtime"
                / "proof_loop_runs"
                / renamed["run_id"]
                / "iteration-03"
                / "packet.json"
            ).read_text(encoding="utf-8")
        )
        checks.append(
            {
                "name": "repair-route-rename-cannot-reset-budget",
                "ok": renamed.get("status") == "referee-accepted"
                and renamed.get("iterations_completed") == 3
                and renamed_packet.get("mode") == "replan"
                and renamed_packet.get("previous_candidate") is None
                and renamed_packet.get("retired_routes", [{}])[0].get("route_family")
                == "parity",
            }
        )

        retrieval = run_scenario(
            root, codex, "retrieval", 3, allow_search=True
        )
        retrieval_root = (
            Path(retrieval["project"])
            / ".proof_runtime"
            / "proof_loop_runs"
            / retrieval["run_id"]
        )
        retrieval_first = json.loads(
            (retrieval_root / "iteration-01" / "packet.json").read_text(encoding="utf-8")
        )
        retrieval_second = json.loads(
            (retrieval_root / "iteration-02" / "packet.json").read_text(encoding="utf-8")
        )
        checks.append(
            {
                "name": "retrieval-search-is-obstruction-triggered",
                "ok": retrieval.get("status") == "referee-accepted"
                and retrieval.get("iterations_completed") == 2
                and not retrieval_first.get("search_enabled")
                and retrieval_second.get("search_enabled")
                and retrieval_second.get("mode") == "solve",
            }
        )

        retrieval_twice = run_scenario(
            root, codex, "retrieval_twice", 3, allow_search=True
        )
        retrieval_twice_root = (
            Path(retrieval_twice["project"])
            / ".proof_runtime"
            / "proof_loop_runs"
            / retrieval_twice["run_id"]
        )
        checks.append(
            {
                "name": "retrieval-search-is-used-at-most-once",
                "ok": retrieval_twice.get("status") == "needs-evidence"
                and retrieval_twice.get("iterations_completed") == 2
                and retrieval_twice.get("requested_capability") == "retrieval"
                and not (retrieval_twice_root / "iteration-03").exists(),
            }
        )

        switched = run_scenario(root, codex, "new_representation", 3)
        switched_root = (
            Path(switched["project"])
            / ".proof_runtime"
            / "proof_loop_runs"
            / switched["run_id"]
        )
        switched_packet = json.loads(
            (switched_root / "iteration-02" / "packet.json").read_text(encoding="utf-8")
        )
        retired_records = [
            json.loads(line).get("record", {})
            for line in (
                Path(switched["project"])
                / ".proof_runtime"
                / "channels"
                / "attempts.jsonl"
            ).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        checks.append(
            {
                "name": "representation-switch-retirement-is-persistent",
                "ok": switched.get("status") == "referee-accepted"
                and switched.get("iterations_completed") == 2
                and switched_packet.get("mode") == "replan"
                and switched_packet.get("retired_routes", [{}])[0].get("route_family")
                == "factorization"
                and any(record.get("outcome") == "retired" for record in retired_records),
            }
        )

        repaired = run_scenario(root, codex, "repair", 3)
        repair_packet = json.loads(
            (
                Path(repaired["project"])
                / ".proof_runtime"
                / "proof_loop_runs"
                / repaired["run_id"]
                / "iteration-02"
                / "packet.json"
            ).read_text(encoding="utf-8")
        )
        checks.append(
            {
                "name": "first-error-single-repair",
                "ok": repaired.get("status") == "referee-accepted"
                and repaired.get("iterations_completed") == 2
                and repair_packet.get("mode") == "repair"
                and repair_packet.get("previous_candidate", {}).get("candidate_markdown", "").startswith("# Proof"),
            }
        )

        blocked = run_scenario(root, codex, "blocked", 2)
        checks.append(
            {
                "name": "named-capability-stop",
                "ok": blocked.get("status") == "needs-evidence"
                and blocked.get("requested_capability") == "symbolic"
                and blocked.get("iterations_completed") == 1,
            }
        )

        consulted = run_scenario(root, codex, "expert_consultation", 2)
        checks.append(
            {
                "name": "expert-consultation-is-an-outer-evidence-request",
                "ok": consulted.get("status") == "needs-evidence"
                and consulted.get("requested_capability") == "expert-consultation"
                and consulted.get("iterations_completed") == 1,
            }
        )

        hard = run_scenario(
            root, codex, "hard_exploration", 2, hard_exploration=True
        )
        hard_root = (
            Path(hard["project"])
            / ".proof_runtime"
            / "proof_loop_runs"
            / hard["run_id"]
        )
        scout_packets = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((hard_root / "hard-exploration").glob("scout-*/packet.json"))
        ]
        scout_instructions = [
            path.read_text(encoding="utf-8")
            for path in sorted((hard_root / "hard-exploration").glob("scout-*/AGENTS.md"))
        ]
        hard_generation = json.loads(
            (hard_root / "iteration-01" / "packet.json").read_text(encoding="utf-8")
        )
        hard_attempts = [
            json.loads(line).get("record", {})
            for line in (
                Path(hard["project"])
                / ".proof_runtime"
                / "channels"
                / "attempts.jsonl"
            ).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        checks.append(
            {
                "name": "hard-exploration-selects-and-stabilizes-one-route",
                "ok": hard.get("status") == "referee-accepted"
                and len(scout_packets) == 2
                and all(packet.get("independent_context") for packet in scout_packets)
                and all("candidates" not in packet for packet in scout_packets)
                and any(
                    packet.get("scout_role", {}).get("name") == "adversarial"
                    and packet.get("domain_seed") == {}
                    for packet in scout_packets
                )
                and all("exact residual" in text for text in scout_instructions)
                and all("domain_seed" in text for text in scout_instructions)
                and hard_generation.get("stable_plan", {}).get("key_original_step")
                == "write the even member as twice an integer"
                and (
                    hard_root / "hard-exploration" / "selected_plan.md"
                ).is_file()
                and any(
                    record.get("event_type") == "hard_exploration_selected"
                    for record in hard_attempts
                ),
            }
        )

        revisited = run_scenario(
            root,
            codex,
            "hard_revisit",
            2,
            hard_exploration=True,
            project_name="hard_exploration",
        )
        revisit_root = (
            Path(revisited["project"])
            / ".proof_runtime"
            / "proof_loop_runs"
            / revisited["run_id"]
        )
        checks.append(
            {
                "name": "completed-proof-is-reused-with-untried-history-preserved",
                "ok": revisited.get("status") == "referee-accepted"
                and revisited.get("reused_completed_result") is True
                and not (revisit_root / "hard-exploration").exists()
                and revisited["cumulative_usage"]["agent_calls"] == hard["cumulative_usage"]["agent_calls"]
                and len(prior_untried_routes(Path(revisited["project"]))) == 1,
            }
        )

        hard_blocked = run_scenario(
            root, codex, "hard_blocked", 2, hard_exploration=True
        )
        hard_blocked_root = (
            Path(hard_blocked["project"])
            / ".proof_runtime"
            / "proof_loop_runs"
            / hard_blocked["run_id"]
        )
        checks.append(
            {
                "name": "hard-exploration-stops-with-named-capability",
                "ok": hard_blocked.get("status") == "needs-evidence"
                and hard_blocked.get("requested_capability") == "symbolic"
                and hard_blocked.get("iterations_completed") == 0
                and len(
                    list(
                        (hard_blocked_root / "hard-exploration").glob(
                            "scout-*/scout.json"
                        )
                    )
                )
                == 2
                and not (hard_blocked_root / "hard-exploration" / "selector").exists()
                and not (hard_blocked_root / "iteration-01").exists(),
            }
        )

    result = {"ok": all(bool(item["ok"]) for item in checks), "checks": checks}
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
