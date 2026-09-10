#!/usr/bin/env python3
"""Exercise routing, project creation, recovery control, and proof diagnosis."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def run(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [sys.executable, *args],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"command failed: {exc.cmd}\nstdout:\n{exc.stdout}\nstderr:\n{exc.stderr}"
        ) from exc


def main() -> int:
    checks: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="statement-retrieval-smoke-") as retrieval_temp:
        retrieval_root = Path(retrieval_temp)
        matlas_fixture = retrieval_root / "matlas-response.json"
        matlas_fixture.write_text(
            json.dumps(
                [
                    {
                        "type": "paper",
                        "entity_name": "Theorem 3",
                        "doi": "doi.org/10.1287/moor.2020.1086",
                        "title": "Stochastic comparative statics in Markov decision processes",
                        "authors": "Light, Bar",
                        "journal": "Math. Oper. Res.",
                        "year": "2021",
                        "statement": "Increasing differences and a monotone transition imply a monotone policy.",
                        "candidate_id": "paper:Theorem:3",
                    },
                    {
                        "type": "paper",
                        "entity_name": "Theorem 3",
                        "doi": "https://doi.org/10.1287/MOOR.2020.1086",
                        "title": "Stochastic comparative statics in Markov decision processes",
                        "authors": "Light, Bar",
                        "journal": "Math. Oper. Res.",
                        "year": "2021",
                        "statement": "Increasing differences and a monotone transition imply a monotone policy.",
                        "candidate_id": "paper:Duplicate:3",
                    },
                    {"type": "paper", "title": "Malformed result"},
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        matlas_run = run(
            str(SCRIPTS / "statement_search.py"),
            "Increasing differences and monotone transitions imply a monotone policy.",
            "--intent",
            "theorem",
            "--response-file",
            str(matlas_fixture),
            "--project",
            str(retrieval_root / "project"),
        )
        matlas_summary = json.loads(matlas_run.stdout)
        matlas_packet_path = Path(matlas_summary["output_path"])
        matlas_packet = json.loads(matlas_packet_path.read_text(encoding="utf-8"))
        remote_guard = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "statement_search.py"),
                "A public mathematical query.",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        checks.append(
            {
                "name": "matlas-candidate-packet-and-privacy-guard",
                "ok": matlas_summary["evidence_status"] == "retrieved-unverified"
                and matlas_summary["proof_effect"] == "none"
                and matlas_summary["result_count_raw"] == 3
                and matlas_summary["result_count_unique"] == 1
                and matlas_packet["duplicates_removed"] == 1
                and matlas_packet["invalid_results_skipped"] == 1
                and matlas_packet["candidates"][0]["identifiers"]["doi"]
                == "10.1287/moor.2020.1086"
                and matlas_packet["candidates"][0]["verification"]["proof_read"]
                == "pending"
                and remote_guard.returncode == 2
                and "pass --remote-ok" in remote_guard.stderr,
            }
        )

        theoremsearch_fixture = retrieval_root / "theoremsearch-response.json"
        theoremsearch_fixture.write_text(
            json.dumps(
                {
                    "theorems": [
                        {
                            "slogan_id": 41,
                            "theorem_id": 17,
                            "name": "Corollary 3.3",
                            "body": "A concave value function implies a monotone optimal policy.",
                            "slogan": "Concavity yields a monotone policy.",
                            "theorem_type": "Corollary",
                            "paper": {
                                "paper_id": "2511.08523v1",
                                "source": "arXiv",
                                "title": "Service Rate Control in Queues with Abandonments",
                                "authors": ["Runhua Wu", "Hayriye Ayhan"],
                                "link": "http://arxiv.org/abs/2511.08523v1",
                                "year": 2025,
                                "citations": 0,
                            },
                            "similarity": 0.64,
                            "score": 0.64,
                        },
                        {"name": "Malformed result"},
                    ]
                }
            )
            + "\n",
            encoding="utf-8",
        )
        theoremsearch_run = run(
            str(SCRIPTS / "statement_search.py"),
            "A concave value function implies a monotone optimal policy.",
            "--service",
            "theoremsearch",
            "--intent",
            "theorem",
            "--tag",
            "math.OC",
            "--response-file",
            str(theoremsearch_fixture),
            "--project",
            str(retrieval_root / "project"),
        )
        theoremsearch_summary = json.loads(theoremsearch_run.stdout)
        theoremsearch_packet = json.loads(
            Path(theoremsearch_summary["output_path"]).read_text(encoding="utf-8")
        )
        checks.append(
            {
                "name": "theoremsearch-candidate-packet-and-filter-record",
                "ok": theoremsearch_summary["service"] == "theoremsearch"
                and theoremsearch_summary["evidence_status"] == "retrieved-unverified"
                and theoremsearch_summary["proof_effect"] == "none"
                and theoremsearch_summary["result_count_raw"] == 2
                and theoremsearch_summary["result_count_unique"] == 1
                and theoremsearch_packet["invalid_results_skipped"] == 1
                and theoremsearch_packet["query"]["filters"]["tags"] == ["math.OC"]
                and theoremsearch_packet["candidates"][0]["identifiers"]["arxiv_id"]
                == "2511.08523v1"
                and theoremsearch_packet["candidates"][0]["source_url"]
                == "https://arxiv.org/abs/2511.08523v1"
                and theoremsearch_packet["candidates"][0]["verification"]["proof_read"]
                == "pending"
                and "logs query text" in theoremsearch_packet["warnings"][0],
            }
        )

    frontier_spec = importlib.util.spec_from_file_location(
        "frontier_evidence_smoke",
        SCRIPTS / "frontier_evidence.py",
    )
    if frontier_spec is None or frontier_spec.loader is None:
        raise RuntimeError("could not load frontier_evidence.py")
    frontier_module = importlib.util.module_from_spec(frontier_spec)
    frontier_spec.loader.exec_module(frontier_module)
    signed_fixture = (
        "https://download.ssrn.com/20/07/29/"
        "ssrn_id3663420_code2380208.pdf?"
        "X-Amz-Date=20260710T072615Z&X-Amz-Expires=300&abstractId=3395992"
    )
    signed_expired = False
    try:
        frontier_module.validate_ssrn_signed_url(signed_fixture, "3395992")
    except ValueError as exc:
        signed_expired = "expired" in str(exc)
    fallback_args = frontier_module.build_parser().parse_args(
        [
            "fetch",
            "/tmp/project",
            "--paper-id",
            "P1",
            "--doi",
            "10.1287/example",
            "--fallback-url",
            "https://example.edu/paper.pdf",
        ]
    )
    checks.append(
        {
            "name": "ssrn-version-and-expiry-guard",
            "ok": frontier_module.normalize_ssrn_id(signed_fixture) == "3395992"
            and frontier_module.normalize_ssrn_id("https://doi.org/10.2139/ssrn.3395992")
            == "3395992"
            and signed_expired
            and frontier_module.automatic_pdf_url(
                "https://www.econstor.eu/bitstream/10419/1/paper.pdf"
            )
            and not frontier_module.automatic_pdf_url(
                "https://download.ssrn.com/temporary.pdf"
            )
            and frontier_module.same_work(
                {"title": "Mechanism Design and Intentions", "authors": ["Bierbrauer, Felix"]},
                {"title": "Mechanism Design & Intentions", "authors": ["Felix Bierbrauer"]},
            )
            and fallback_args.fallback_url == "https://example.edu/paper.pdf",
        }
    )

    idea = run(
        str(SCRIPTS / "plan_idea.py"),
        "In a finite discounted MDP, the Bellman operator is a contraction.",
    )
    checks.append(
        {
            "name": "idea-routing",
            "ok": "dp-proof-playbook.md" in idea.stdout and "Proof Kernel" not in idea.stdout,
        }
    )
    idea_full = run(
        str(SCRIPTS / "plan_idea.py"),
        "In a finite discounted MDP, the Bellman operator is a contraction.",
        "--full",
    )
    checks.append(
        {
            "name": "evidence-layered-idea-search",
            "ok": all(
                phrase in idea_full.stdout
                for phrase in [
                    "Evidence-layered search packet",
                    "Optional matched strategy trial",
                    "same proof-state baseline",
                    "proof_effect=none",
                    "falsifiable local prediction",
                    "representation ladder",
                    "rigidity or invariant conjecture",
                    "theorem-preserving symmetries",
                    "verification-and-assembly tail budget",
                    "solver-owned digest",
                    "Near-miss frontier",
                    "independent route or held-out check",
                    "target-restating answers",
                    "surjectivity",
                ]
            ),
        }
    )
    idea_discovery = run(
        str(SCRIPTS / "plan_idea.py"),
        "In a finite discounted MDP, the Bellman operator is a contraction.",
        "--discovery",
    )
    checks.append(
        {
            "name": "discovery-map-stays-mathematical-and-light",
            "ok": all(
                phrase in idea_discovery.stdout
                for phrase in [
                    "Certificate-first",
                    "Local-to-global",
                    "Abstraction-refinement",
                    "Bottom-up synthesis",
                    "Equality-driven algebra",
                    "Trick replay",
                ]
            )
            and "Optional matched strategy trial" not in idea_discovery.stdout
            and "Evidence-layered search packet" not in idea_discovery.stdout
            and "Outside patterns and tools" not in idea_discovery.stdout
            and "Scholar" not in idea_discovery.stdout
            and "learning-theory-playbook.md" not in idea_discovery.stdout
            and "uniform good event" not in idea_discovery.stdout,
        }
    )

    mechanism = run(
        str(SCRIPTS / "select_playbook.py"),
        "Prove incentive compatibility from cyclic monotonicity in a finite-type mechanism.",
    )
    selected = json.loads(mechanism.stdout)
    checks.append(
        {
            "name": "mechanism-routing",
            "ok": "mechanism-design-playbook.md" in selected.get("selected", []),
        }
    )

    bandit = run(
        str(SCRIPTS / "select_playbook.py"),
        "Prove a logarithmic UCB regret bound from a uniform confidence event.",
    )
    bandit_selected = json.loads(bandit.stdout)
    checks.append(
        {
            "name": "bandit-routing",
            "ok": "bandits-oco-playbook.md" in bandit_selected.get("selected", []),
        }
    )

    peppy_route = run(
        str(SCRIPTS / "select_playbook.py"),
        "Prove the worst-case rate of proximal gradient with a Lyapunov function.",
    )
    peppy_selected = json.loads(peppy_route.stdout)
    peppy_idea = run(
        str(SCRIPTS / "plan_idea.py"),
        "Prove the worst-case rate of proximal gradient with a Lyapunov function.",
    )
    checks.append(
        {
            "name": "peppy-optimization-routing",
            "ok": "optimization-or-playbook.md" in peppy_selected.get("selected", [])
            and "PEP dual/Lyapunov certificate" in peppy_idea.stdout,
        }
    )

    with tempfile.TemporaryDirectory(prefix="proof-workbench-smoke-") as temp_dir:
        legacy_project = Path(temp_dir) / "legacy-project"
        legacy_project.mkdir()
        legacy_routing = legacy_project / "routing.json"
        legacy_routing.write_text(
            json.dumps(
                {
                    "title": "legacy-project",
                    "claim": "For every real x, x equals x.",
                    "mode": "recovery",
                    "status": "complete",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        legacy_brief = json.loads(
            run(str(SCRIPTS / "proof_runtime.py"), "brief", str(legacy_project)).stdout
        )
        legacy_routing.write_text(
            json.dumps(
                {
                    "title": "legacy-project",
                    "claim": "For every real x, x squared is nonnegative.",
                    "mode": "recovery",
                    "status": "complete",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        stale_claim = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "proof_runtime.py"),
                "brief",
                str(legacy_project),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        revised_claim = json.loads(
            run(
                str(SCRIPTS / "proof_runtime.py"),
                "revise-claim",
                str(legacy_project),
                "--reason",
                "The legacy theorem statement was intentionally replaced.",
            ).stdout
        )
        checks.append(
            {
                "name": "legacy-runtime-migration-and-claim-fence",
                "ok": legacy_brief["state"]["mode"] == "recovery"
                and legacy_brief["state"]["proof_status"] == "unresolved"
                and legacy_brief["state"]["project_status_hint"] == "complete"
                and legacy_brief["state"]["project_status_hint_evidence"]
                == "unverified-routing-metadata"
                and (legacy_project / ".proof_runtime" / "state.json").is_file()
                and stale_claim.returncode != 0
                and "project claim differs from runtime state" in stale_claim.stderr
                and revised_claim["claim_revision"] == 1
                and revised_claim["proof_status"] == "unresolved",
            }
        )

        created = run(
            str(SCRIPTS / "start_proof.py"),
            "--title",
            "smoke-mdp",
            "--claim",
            "In a finite discounted MDP, the Bellman operator is a contraction.",
            "--dir",
            temp_dir,
        )
        project = Path(created.stdout.strip())
        required = {
            "claim.md",
            "TRIAGE.md",
            "LEDGER.md",
            "IDEA_MAP.md",
            "LEMMA_QUEUE.md",
            "routing.json",
            ".proof_runtime/state.json",
            ".proof_runtime/channels/events.jsonl",
            ".proof_runtime/channels/attempts.jsonl",
            ".proof_runtime/channels/computations.jsonl",
            ".proof_runtime/channels/verification_reports.jsonl",
        }
        checks.append(
            {
                "name": "project-creation",
                "ok": project.is_dir()
                and all((project / name).is_file() for name in required)
                and (project / "lean" / "handoffs").is_dir(),
            }
        )
        claim_template = (project / "claim.md").read_text(encoding="utf-8")
        workstreams_template = (project / "WORKSTREAMS.md").read_text(encoding="utf-8")
        idea_template = (project / "IDEA_MAP.md").read_text(encoding="utf-8")
        counterexample_template = (project / "counterexamples.md").read_text(encoding="utf-8")
        pattern_template = (project / "PATTERN_SCAN.md").read_text(encoding="utf-8")
        checks.append(
            {
                "name": "acceptance-and-route-family-control",
                "ok": "## Acceptance Contract" in claim_template
                and "atomic semantic obligations" in claim_template
                and "answer or witness contract" in claim_template
                and "## Assumption And Definition Lineage" in claim_template
                and "source-explicit / source-implied / encoding adapter / theorem repair" in claim_template
                and "## Completion Coverage" in claim_template
                and "## Approach Family Registry" in workstreams_template
                and "## Portfolio Checkpoint" in workstreams_template
                and "not the current favorite" in workstreams_template
                and "menu, not a required roster" in workstreams_template
                and "new mechanism / invariant / construction" in workstreams_template
                and "answer-hole contract when applicable" in idea_template
                and "diagnostic-grounded repair tuple" in workstreams_template
                and "diagnostic site" in workstreams_template
                and "inferred root cause" in workstreams_template
                and "worst active gap weakens" in workstreams_template
                and "evaluator scope" in idea_template
                and "evaluator calibration" in idea_template
                and "hard-witness regression set" in idea_template
                and "## Hypothesis Ablation" in counterexample_template
                and "## Autonomous Capability Check" in pattern_template,
            }
        )

        find_all_idea = run(
            str(SCRIPTS / "plan_idea.py"),
            "--full",
            "Find all real triples (a,b,c) satisfying a+b+c=3 and a^2+b^2+c^2=3.",
        ).stdout
        checks.append(
            {
                "name": "answer-hole-forward-control",
                "ok": "For construct or find-all tasks, freeze the answer type" in find_all_idea
                and "forbid target-restating answers" in find_all_idea
                and "separate witness soundness from completeness" in find_all_idea
                and "candidate: Find all real triples" not in find_all_idea,
            }
        )

        decomposition_created = run(
            str(SCRIPTS / "start_proof.py"),
            "--title",
            "smoke-decomposition",
            "--claim",
            "A parent theorem follows from two required local lemmas.",
            "--dir",
            temp_dir,
        )
        decomposition_project = Path(decomposition_created.stdout.strip())
        decomposition_ledger = decomposition_project / "LEDGER.md"
        decomposition_ledger.write_text(
            decomposition_ledger.read_text(encoding="utf-8").replace(
                "S2-stress-test", "S4-lemma-graph", 1
            ),
            encoding="utf-8",
        )
        decomposition_queue = decomposition_project / "LEMMA_QUEUE.md"
        decomposition_queue.write_text(
            """# Lemma Queue: smoke-decomposition

## Blueprint Dependency Graph

| node id | type | status | statement / role | statement deps | proof deps | used by assembly | expected artifact | gap grade | failure diagnosis | compact repair state | suggested fix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P | theorem | missing | parent theorem |  | L1, L2 | yes | human proof | good |  |  |  |
| L1 | lemma | proved | first required bridge |  |  | yes | human proof | good |  |  |  |
| L2 | lemma | missing | second required bridge |  |  | yes | human proof | good |  |  |  |
| A1 | lemma | checked | auxiliary identity |  |  | no | tool check | good |  |  |  |

## Blueprint Metadata Audit

- statement status: intended

## Decomposition Admission Gate

- parent node: P
- conditional parent assembly: assume L1 and L2, then execute parent steps 1 and 2
- exact use site for each required child:
- post-proof parent replay: not-run / passed / failed
- why each required child is strictly simpler: each is one local implication
- ancestor-equivalence and cycle check: no child restates P and the graph is acyclic
- source or statement-fence anchor: claim.md acceptance contract
- expected repair radius if one child fails: only that child and its use site
- jointly sufficient premise bundle or retrieval plan: L1 and L2 jointly close P
- reviewer verdict: admit
""",
            encoding="utf-8",
        )
        blocked_decomposition = json.loads(
            run(
                str(SCRIPTS / "proof_doctor.py"),
                str(decomposition_project),
                "--json",
            ).stdout
        )
        checks.append(
            {
                "name": "decomposition-consumption-gate-blocks-unmapped-child",
                "ok": blocked_decomposition["decomposition_admission"]["active"]
                and blocked_decomposition["decomposition_admission"]["blocks_progress"]
                and "exact use site for each required child"
                in blocked_decomposition["decomposition_admission"]["missing_fields"]
                and blocked_decomposition["primary_action"].startswith(
                    "Complete decomposition admission"
                ),
            }
        )
        admitted_queue = decomposition_queue.read_text(encoding="utf-8").replace(
            "- exact use site for each required child:\n",
            "- exact use site for each required child: L1 at parent step 1; L2 at parent step 2\n",
        ).replace(
            "- post-proof parent replay: not-run / passed / failed\n",
            "- post-proof parent replay: passed conditionally with L2 still assumed\n",
        )
        decomposition_queue.write_text(admitted_queue, encoding="utf-8")
        admitted_decomposition = json.loads(
            run(
                str(SCRIPTS / "proof_doctor.py"),
                str(decomposition_project),
                "--json",
            ).stdout
        )
        checks.append(
            {
                "name": "decomposition-consumption-gate-replays-parent",
                "ok": admitted_decomposition["decomposition_admission"]["admitted"]
                and not admitted_decomposition["decomposition_admission"]["blocks_progress"]
                and admitted_decomposition["decomposition_admission"][
                    "parent_replay_status"
                ]
                == "passed"
                and admitted_decomposition["decomposition_admission"][
                    "required_child_ids"
                ]
                == ["L1", "L2"]
                and admitted_decomposition["decomposition_admission"][
                    "proved_unused_nodes"
                ]
                == ["A1"]
                and any(
                    "Do not count proved-but-unused nodes" in action
                    for action in admitted_decomposition["next_actions"]
                ),
            }
        )

        trick_path = Path(
            run(
                str(SCRIPTS / "new_trick_card.py"),
                "bounded-ablation",
                "--project",
                str(project),
            ).stdout.strip()
        )
        trick_text = trick_path.read_text(encoding="utf-8")
        checks.append(
            {
                "name": "trick-applicability-and-replay-contract",
                "ok": "## Applicability Contract" in trick_text
                and "## Independent Replay" in trick_text,
            }
        )

        attempt_record = {
            "event_type": "checker_guided_attempt_completed",
            "route_family": "Bellman contraction",
            "target_lemma": "sup-norm contraction",
            "outcome": "blocked",
            "failure_witness": "discount factor domain not yet stated",
            "feedback_kind": "checker",
            "checker_backend": "synthetic Lean fixture",
            "diagnostic": "missing hypothesis: 0 <= discount and discount < 1",
            "local_state": "prove sup-norm contraction under the current MDP assumptions",
            "diagnostic_site": "synthetic fixture:1:1",
            "inferred_root_cause": "the contraction factor has no declared domain",
            "failure_class": "MISSING_ASSUMPTION",
            "diagnosis": "the contraction factor has no declared domain",
            "repair": "add the discount-factor domain to the theorem fence",
            "replay_result": "not-run",
            "proof_state_delta": "one missing assumption isolated",
        }
        run(
            str(SCRIPTS / "proof_runtime.py"),
            "append",
            str(project),
            "attempts",
            "--record",
            json.dumps(attempt_record),
        )
        incomplete_checker_record = dict(attempt_record)
        incomplete_checker_record.pop("diagnosis")
        rejected_checker_record = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "proof_runtime.py"),
                "append",
                str(project),
                "attempts",
                "--record",
                json.dumps(incomplete_checker_record),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        run(
            str(SCRIPTS / "proof_runtime.py"),
            "set",
            str(project),
            "--proof-status",
            "lemma-conditional",
            "--current-node",
            "sup-norm contraction",
        )
        runtime_brief = json.loads(
            run(str(SCRIPTS / "proof_runtime.py"), "brief", str(project)).stdout
        )
        runtime_markdown = run(
            str(SCRIPTS / "proof_runtime.py"),
            "brief",
            str(project),
            "--markdown",
        ).stdout
        checks.append(
            {
                "name": "compact-typed-runtime",
                "ok": runtime_brief["state"]["proof_status"] == "lemma-conditional"
                and runtime_brief["counts"]["attempts"] == 1
                and runtime_brief["counts"]["events"] == 2
                and rejected_checker_record.returncode != 0
                and "checker-guided attempts record is missing" in rejected_checker_record.stderr
                and "discount factor domain" in runtime_markdown
                and "missing hypothesis" in runtime_markdown
                and "diagnostic_site" in runtime_markdown
                and "inferred_root_cause" in runtime_markdown
                and "failure_class" in runtime_markdown
                and "replay_result" in runtime_markdown
                and "sup-norm contraction" in runtime_markdown,
            }
        )

        lean_file = project / "lean" / "LocalLemmas.lean"
        lean_file.write_text(
            "namespace Smoke\n\ntheorem bellman_local : True := by trivial\n\nend Smoke\n",
            encoding="utf-8",
        )
        lemma_statement_file = project / "lemmas" / "L-bellman-local.md"
        lemma_statement_file.write_text("True\n", encoding="utf-8")
        mock_lean_success = Path(temp_dir) / "mock_lean_status_success.py"
        mock_lean_success.write_text(
            """#!/usr/bin/env python3
import json
import sys

required = "Smoke.bellman_local:theorem"
ok = "--require-decl-kind" in sys.argv and required in sys.argv
print(json.dumps({
    "results": [{
        "path": sys.argv[1],
        "blockers": {"sorry": 0, "axiom": 0, "unsafe": 0},
        "total_blockers": 0,
        "declarations": [{"name": "Smoke.bellman_local", "kind": "theorem"}],
        "missing_required_declaration_kinds": [] if ok else [required],
        "check": {"returncode": 0 if ok else 1, "stdout": "", "stderr": ""},
    }],
    "exit_code": 0 if ok else 1,
}))
raise SystemExit(0 if ok else 1)
""",
            encoding="utf-8",
        )
        missing_downstream = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "prepare",
                str(project),
                "--node-id",
                "L-unowned",
                "--statement-file",
                "lemmas/L-bellman-local.md",
                "--target-name",
                "Smoke.unowned",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        prepared = json.loads(
            run(
                str(SCRIPTS / "lean_bridge.py"),
                "prepare",
                str(project),
                "--node-id",
                "L-bellman-local",
                "--role",
                "local-lemma",
                "--statement-file",
                "lemmas/L-bellman-local.md",
                "--lean-file",
                "lean/LocalLemmas.lean",
                "--target-name",
                "Smoke.bellman_local",
                "--target-kind",
                "theorem",
                "--dependency",
                "True.intro",
                "--downstream-use",
                "synthetic smoke-test parent",
            ).stdout
        )
        request_path = Path(prepared["request_path"])
        request_packet = prepared["packet"]
        lean_success = json.loads(
            run(
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(request_path),
                "--lean-status-script",
                str(mock_lean_success),
            ).stdout
        )
        mock_lean_outer_failure = Path(temp_dir) / "mock_lean_status_outer_failure.py"
        mock_lean_outer_failure.write_text(
            mock_lean_success.read_text(encoding="utf-8").replace(
                "raise SystemExit(0 if ok else 1)",
                "raise SystemExit(1)",
            ),
            encoding="utf-8",
        )
        outer_failure = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(request_path),
                "--lean-status-script",
                str(mock_lean_outer_failure),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        outer_failure_result = json.loads(outer_failure.stdout)
        changed_target = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(request_path),
                "--lean-file",
                "claim.md",
                "--lean-status-script",
                str(mock_lean_success),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        original_lean_text = lean_file.read_text(encoding="utf-8")
        mock_lean_mutating = Path(temp_dir) / "mock_lean_status_mutating.py"
        mock_lean_mutating.write_text(
            """#!/usr/bin/env python3
import json
import sys
from pathlib import Path

target = Path(sys.argv[1])
target.write_text(target.read_text(encoding="utf-8") + "\\n-- concurrent edit\\n", encoding="utf-8")
print(json.dumps({
    "results": [{
        "path": str(target),
        "blockers": {"sorry": 0, "axiom": 0, "unsafe": 0},
        "total_blockers": 0,
        "missing_required_declaration_kinds": [],
        "check": {"returncode": 0, "stdout": "", "stderr": ""},
    }],
    "exit_code": 0,
}))
""",
            encoding="utf-8",
        )
        changed_during_check = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(request_path),
                "--lean-status-script",
                str(mock_lean_mutating),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        changed_during_check_result = json.loads(changed_during_check.stdout)
        lean_file.write_text(original_lean_text, encoding="utf-8")
        local_promotion = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(request_path),
                "--lean-status-script",
                str(mock_lean_success),
                "--promote-final",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        tampered_path = project / "lean" / "handoffs" / "tampered.request.json"
        tampered_packet = dict(request_packet)
        tampered_packet["node"] = dict(tampered_packet["node"])
        tampered_packet["node"]["statement"] = "True or False"
        tampered_path.write_text(json.dumps(tampered_packet), encoding="utf-8")
        tampered_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(tampered_path),
                "--lean-status-script",
                str(mock_lean_success),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        stale_path = project / "lean" / "handoffs" / "stale.request.json"
        stale_packet = dict(request_packet)
        stale_packet["claim_sha256"] = "0" * 64
        stale_packet.pop("packet_sha256")
        stale_packet["packet_sha256"] = hashlib.sha256(
            json.dumps(
                stale_packet,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        stale_path.write_text(json.dumps(stale_packet), encoding="utf-8")
        stale_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(stale_path),
                "--lean-status-script",
                str(mock_lean_success),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        mock_lean_failure = Path(temp_dir) / "mock_lean_status_failure.py"
        mock_lean_failure.write_text(
            """#!/usr/bin/env python3
import json
import sys

print(json.dumps({
    "results": [{
        "path": sys.argv[1],
        "blockers": {"sorry": 0, "axiom": 0, "unsafe": 0},
        "total_blockers": 0,
        "declarations": [{"name": "Smoke.bellman_local", "kind": "theorem"}],
        "missing_required_declaration_kinds": [],
        "check": {
            "returncode": 1,
            "stdout": "",
            "stderr": "lean/LocalLemmas.lean:4:2: error: type mismatch",
        },
    }],
    "exit_code": 1,
}))
raise SystemExit(1)
""",
            encoding="utf-8",
        )
        failed_runs = []
        for _ in range(2):
            failed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "lean_bridge.py"),
                    "verify",
                    str(project),
                    str(request_path),
                    "--lean-status-script",
                    str(mock_lean_failure),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            failed_runs.append((failed.returncode, json.loads(failed.stdout)))

        mock_lean_local_failure = Path(temp_dir) / "mock_lean_status_local_failure.py"
        mock_lean_local_failure.write_text(
            mock_lean_failure.read_text(encoding="utf-8").replace(
                "error: type mismatch",
                "error: tactic 'linarith' failed",
            ),
            encoding="utf-8",
        )
        local_failure = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(request_path),
                "--lean-status-script",
                str(mock_lean_local_failure),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        local_failure_result = json.loads(local_failure.stdout)
        mathematical_failure = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                str(request_path),
                "--lean-status-script",
                str(mock_lean_local_failure),
                "--failure-stage",
                "mathematical",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        mathematical_failure_result = json.loads(mathematical_failure.stdout)

        full_prepared = json.loads(
            run(
                str(SCRIPTS / "lean_bridge.py"),
                "prepare",
                str(project),
                "--node-id",
                "T-smoke",
                "--role",
                "full-theorem",
                "--statement",
                "True",
                "--lean-file",
                "lean/LocalLemmas.lean",
                "--target-name",
                "Smoke.bellman_local",
                "--target-kind",
                "theorem",
            ).stdout
        )
        acceptance_path = project / full_prepared["packet"]["acceptance_report"]
        acceptance = json.loads(acceptance_path.read_text(encoding="utf-8"))
        for name, item in acceptance["checks"].items():
            item["status"] = "pass"
            item["evidence"] = f"synthetic smoke evidence for {name}"
        acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")
        final_result = json.loads(
            run(
                str(SCRIPTS / "lean_bridge.py"),
                "verify",
                str(project),
                full_prepared["request_path"],
                "--lean-status-script",
                str(mock_lean_success),
                "--promote-final",
            ).stdout
        )
        final_state = json.loads(
            (project / ".proof_runtime" / "state.json").read_text(encoding="utf-8")
        )
        checks.append(
            {
                "name": "lean-bidirectional-handoff",
                "ok": request_path.is_file()
                and bool(request_packet.get("packet_sha256"))
                and request_packet["node"]["statement_source"]["path"]
                == "lemmas/L-bellman-local.md"
                and request_packet["node"]["statement_source"]["sha256"]
                == hashlib.sha256(lemma_statement_file.read_bytes()).hexdigest()
                and missing_downstream.returncode == 2
                and "require --downstream-use" in missing_downstream.stderr
                and lean_success["exact_target_gate"] == "pass"
                and lean_success["node_status"] == "formalized-local"
                and lean_success["recommended_owner"] == "theory-integrator"
                and Path(project / lean_success["lean_file"]).is_file()
                and outer_failure.returncode == 1
                and outer_failure_result["exact_target_gate"] == "fail"
                and outer_failure_result["checker_process_exit_code"] == 1
                and changed_target.returncode == 2
                and "differs from the frozen handoff" in changed_target.stderr
                and changed_during_check.returncode == 1
                and changed_during_check_result["failure_class"]
                == "TARGET_CHANGED_DURING_CHECK"
                and not changed_during_check_result["lean_file_stable_during_check"]
                and local_promotion.returncode == 2
                and "final promotion requires" in local_promotion.stdout
                and tampered_result.returncode == 2
                and "tampered Lean handoff" in tampered_result.stderr
                and stale_result.returncode == 2
                and "stale Lean handoff" in stale_result.stderr
                and failed_runs[0][0] == 1
                and failed_runs[0][1]["recommended_owner"] == "lean-theorem-formalizer"
                and failed_runs[0][1]["failure_class"] == "TYPE_COERCION"
                and bool(failed_runs[0][1]["diagnostic_fingerprint"])
                and failed_runs[1][0] == 1
                and failed_runs[1][1]["prior_same_failure_count"] == 1
                and failed_runs[1][1]["recommended_owner"] == "math-research"
                and "same Lean failure signature" in failed_runs[1][1]["repair"]
                and local_failure.returncode == 1
                and local_failure_result["failure_class"] == "LOCAL_PROOF"
                and local_failure_result["formal_failure_surgery"]["activation"]
                == "candidate"
                and "innermost failing structured proof block"
                in local_failure_result["formal_failure_surgery"]["repair_scope"]
                and len(
                    local_failure_result["formal_failure_surgery"]["required_subgoal_gates"]
                )
                == 4
                and mathematical_failure.returncode == 1
                and mathematical_failure_result["recommended_owner"]
                == "math-research"
                and mathematical_failure_result["formal_failure_surgery"]["activation"]
                == "not-applicable"
                and "declared failure stage is mathematical"
                in mathematical_failure_result["formal_failure_surgery"]["reason"]
                and final_result["eligible_for_formalized_complete"]
                and final_state["proof_status"] == "formalized-complete",
            }
        )

        mock_bin = Path(temp_dir) / "mock-bin"
        mock_bin.mkdir()
        mock_codex = mock_bin / "codex"
        mock_codex.write_text(
            """#!/usr/bin/env python3
import json
import os
import sys

output = sys.argv[sys.argv.index("--output-last-message") + 1]
payload = {
    "summary": "All declared obligations were checked.",
    "claim_fidelity": {"status": "pass", "issue": ""},
    "assumption_coverage": {"status": "pass", "issue": ""},
    "failure_kind": "none",
    "first_error": {"location": "", "issue": ""},
    "critical_errors": [],
    "gaps": [],
    "verdict": "correct",
    "repair_hints": [],
}
if os.environ.get("MOCK_REFEREE_CONTRADICTORY"):
    payload["gaps"] = [{"location": "step 2", "issue": "unsupported implication"}]
if os.environ.get("MOCK_REFEREE_MISSING_EVIDENCE"):
    payload.update({
        "summary": "A cited premise is absent from the packet.",
        "assumption_coverage": {"status": "fail", "issue": "premise L2 is absent"},
        "failure_kind": "missing-packet-evidence",
        "first_error": {"location": "step 3", "issue": "premise L2 is absent from the packet"},
        "critical_errors": [{"location": "step 3", "issue": "premise L2 is unavailable"}],
        "gaps": [],
        "verdict": "wrong",
        "repair_hints": ["Supply premise L2."],
    })
with open(output, "w", encoding="utf-8") as handle:
    json.dump(payload, handle)
print("mock referee completed")
""",
            encoding="utf-8",
        )
        mock_codex.chmod(0o755)
        tool_env = dict(os.environ)
        tool_env["PATH"] = str(mock_bin) + os.pathsep + tool_env.get("PATH", "")

        candidate_proof = project / "writeup" / "candidate.md"
        candidate_proof.write_text(
            "# Candidate Proof\n\nFor any value functions V and W, take the sup norm after "
            "applying the discounted Bellman inequality.\n",
            encoding="utf-8",
        )
        prepared = json.loads(
            run(
                str(SCRIPTS / "run_referee.py"),
                str(project),
                "--proof",
                "writeup/candidate.md",
                "--prepare-only",
                env=tool_env,
            ).stdout
        )
        prepared_dir = Path(prepared["run_dir"])
        prepared_packet = json.loads((prepared_dir / "packet.json").read_text(encoding="utf-8"))
        command = prepared["command"]
        checks.append(
            {
                "name": "context-isolated-referee-packet",
                "ok": prepared_packet["claim"]
                == "In a finite discounted MDP, the Bellman operator is a contraction."
                and prepared_packet["candidate_proof_sha256"]
                == hashlib.sha256(candidate_proof.read_bytes()).hexdigest()
                and "--ephemeral" in command
                and "--ignore-user-config" in command
                and "--ignore-rules" in command
                and "read-only" in command
                and not any("dangerously-bypass" in item for item in command),
            }
        )
        referee_result = json.loads(
            run(
                str(SCRIPTS / "run_referee.py"),
                str(project),
                "--proof",
                "writeup/candidate.md",
                "--timeout",
                "30",
                env=tool_env,
            ).stdout
        )
        checks.append(
            {
                "name": "mock-referee-controller",
                "ok": referee_result["verdict"] == "correct"
                and referee_result["controller"]["fresh_context"]
                and referee_result["controller"]["sandbox"] == "read-only"
                and referee_result["controller"]["filesystem_isolation_not_claimed"],
            }
        )
        contradictory_env = dict(tool_env)
        contradictory_env["MOCK_REFEREE_CONTRADICTORY"] = "1"
        contradictory = json.loads(
            run(
                str(SCRIPTS / "run_referee.py"),
                str(project),
                "--proof",
                "writeup/candidate.md",
                "--timeout",
                "30",
                env=contradictory_env,
            ).stdout
        )
        checks.append(
            {
                "name": "contradictory-referee-downgrade",
                "ok": contradictory["verdict"] == "uncertain"
                and any(
                    "correct verdict conflicts" in problem
                    for problem in contradictory["controller"]["validation_errors"]
                ),
            }
        )
        missing_evidence_env = dict(tool_env)
        missing_evidence_env["MOCK_REFEREE_MISSING_EVIDENCE"] = "1"
        gap_created = run(
            str(SCRIPTS / "start_proof.py"),
            "--title",
            "smoke-referee-gap",
            "--claim",
            "In a finite discounted MDP, the Bellman operator is a contraction.",
            "--dir",
            temp_dir,
        )
        referee_gap_project = Path(gap_created.stdout.strip())
        referee_gap_candidate = referee_gap_project / "writeup" / "candidate.md"
        referee_gap_candidate.write_text(candidate_proof.read_text(encoding="utf-8"), encoding="utf-8")
        missing_evidence = json.loads(
            run(
                str(SCRIPTS / "run_referee.py"),
                str(referee_gap_project),
                "--proof",
                "writeup/candidate.md",
                "--timeout",
                "30",
                env=missing_evidence_env,
            ).stdout
        )
        missing_evidence_doctor = run(
            str(SCRIPTS / "proof_doctor.py"), str(referee_gap_project)
        ).stdout
        checks.append(
            {
                "name": "missing-evidence-referee-routing",
                "ok": missing_evidence["verdict"] == "uncertain"
                and missing_evidence["failure_kind"] == "missing-packet-evidence"
                and any(
                    "unavailable packet or tool evidence" in problem
                    for problem in missing_evidence["controller"]["validation_errors"]
                )
                and "Repair the referee packet at step 3" in missing_evidence_doctor
                and "do not restart proof search" in missing_evidence_doctor,
            }
        )

        replay_input = project / "tool_checks" / "replay.wl"
        replay_input.write_text("Print[2 + 2];\n", encoding="utf-8")
        expected_output = project / "tool_checks" / "expected.txt"
        expected_output.write_text("4\n", encoding="utf-8")
        mock_wmath = mock_bin / "codex-wmath"
        mock_wmath.write_text("#!/bin/sh\nprintf '4\\n'\n", encoding="utf-8")
        mock_wmath.chmod(0o755)
        recorded = json.loads(
            run(
                str(SCRIPTS / "computation_artifact.py"),
                "record",
                str(project),
                "--claim-id",
                "L1",
                "--local-claim",
                "The exact test expression equals four.",
                "--backend",
                "mock-wolfram",
                "--backend-version",
                "mock-1",
                "--result-kind",
                "symbolic-identity",
                "--command-json",
                json.dumps(["codex-wmath", "-file", "tool_checks/replay.wl"]),
                "--input",
                "tool_checks/replay.wl",
                "--compare",
                "stdout-exact",
                "--expected-output",
                "tool_checks/expected.txt",
                "--proof-translation",
                "A replayed exact identity supports only local lemma L1.",
                env=tool_env,
            ).stdout
        )
        replayed = json.loads(
            run(
                str(SCRIPTS / "computation_artifact.py"),
                "replay",
                str(project),
                recorded["artifact_id"],
                "--timeout",
                "30",
                env=tool_env,
            ).stdout
        )
        checks.append(
            {
                "name": "replayable-computation-artifact",
                "ok": recorded["backend_version"] == "mock-1"
                and bool(recorded["executable"]["sha256"])
                and recorded["evidentiary_status"] == "lemma-candidate"
                and replayed["status"] == "passed",
            }
        )
        audited_artifact = json.loads(
            run(
                str(SCRIPTS / "computation_artifact.py"),
                "audit",
                str(project),
                recorded["artifact_id"],
                env=tool_env,
            ).stdout
        )
        doctor_with_valid_artifact = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json", env=tool_env).stdout
        )
        checks.append(
            {
                "name": "doctor-counts-only-live-valid-artifacts",
                "ok": audited_artifact["valid"]
                and recorded["artifact_id"]
                in doctor_with_valid_artifact["latest_referee"]["passed_artifact_ids"]
                and "L1" in doctor_with_valid_artifact["latest_referee"]["passed_claim_ids"]
                and not doctor_with_valid_artifact["latest_referee"][
                    "invalid_computation_artifacts"
                ],
            }
        )
        artifact_file = (
            project
            / ".proof_runtime"
            / "computation_artifacts"
            / recorded["artifact_id"]
            / "artifact.json"
        )
        tampered_artifact = json.loads(artifact_file.read_text(encoding="utf-8"))
        tampered_artifact["backend_version"] = "mock-2"
        artifact_file.write_text(
            json.dumps(tampered_artifact, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tampered_replay = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "computation_artifact.py"),
                "replay",
                str(project),
                recorded["artifact_id"],
                "--timeout",
                "30",
            ],
            capture_output=True,
            text=True,
            env=tool_env,
            check=False,
        )
        tampered_result = json.loads(tampered_replay.stdout)
        checks.append(
            {
                "name": "computation-spec-tamper-guard",
                "ok": tampered_replay.returncode != 0
                and tampered_result["status"] == "input-changed"
                and "computation artifact specification hash mismatch"
                in tampered_result["input_errors"],
            }
        )
        doctor_with_tampered_artifact = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json", env=tool_env).stdout
        )
        checks.append(
            {
                "name": "doctor-rejects-tampered-passed-artifact",
                "ok": "L1"
                not in doctor_with_tampered_artifact["latest_referee"]["passed_claim_ids"]
                and any(
                    item["artifact_id"] == recorded["artifact_id"]
                    for item in doctor_with_tampered_artifact["latest_referee"][
                        "invalid_computation_artifacts"
                    ]
                ),
            }
        )
        orphaned_directory = project / "tool_checks" / "orphaned-computation-artifact"
        artifact_file.parent.rename(orphaned_directory)
        doctor_with_orphaned_artifact = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json", env=tool_env).stdout
        )
        checks.append(
            {
                "name": "doctor-rejects-orphaned-computation-record",
                "ok": "L1"
                not in doctor_with_orphaned_artifact["latest_referee"]["passed_claim_ids"]
                and any(
                    "not found" in error
                    for item in doctor_with_orphaned_artifact["latest_referee"][
                        "invalid_computation_artifacts"
                    ]
                    for error in item["errors"]
                ),
            }
        )
        replacement = json.loads(
            run(
                str(SCRIPTS / "computation_artifact.py"),
                "record",
                str(project),
                "--claim-id",
                "L1-replacement",
                "--local-claim",
                "The replacement exact test expression equals four.",
                "--backend",
                "mock-wolfram",
                "--backend-version",
                "mock-1",
                "--result-kind",
                "symbolic-identity",
                "--command-json",
                json.dumps(["codex-wmath", "-file", "tool_checks/replay.wl"]),
                "--input",
                "tool_checks/replay.wl",
                "--compare",
                "stdout-exact",
                "--expected-output",
                "tool_checks/expected.txt",
                "--proof-translation",
                "This stricter replacement covers local lemma L1.",
                env=tool_env,
            ).stdout
        )
        replacement_replay = json.loads(
            run(
                str(SCRIPTS / "computation_artifact.py"),
                "replay",
                str(project),
                replacement["artifact_id"],
                "--timeout",
                "30",
                env=tool_env,
            ).stdout
        )
        superseded = json.loads(
            run(
                str(SCRIPTS / "computation_artifact.py"),
                "supersede",
                str(project),
                recorded["artifact_id"],
                "--replacement",
                replacement["artifact_id"],
                "--reason",
                "The replacement reruns the same local identity under the current inputs.",
                env=tool_env,
            ).stdout
        )
        doctor_after_supersession = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json", env=tool_env).stdout
        )
        checks.append(
            {
                "name": "append-only-computation-supersession",
                "ok": replacement_replay["status"] == "passed"
                and superseded["replacement_artifact_id"] == replacement["artifact_id"]
                and "L1" in doctor_after_supersession["latest_referee"]["passed_claim_ids"]
                and not doctor_after_supersession["latest_referee"][
                    "invalid_computation_artifacts"
                ]
                and any(
                    item["artifact_id"] == recorded["artifact_id"]
                    for item in doctor_after_supersession["latest_referee"][
                        "superseded_computation_artifacts"
                    ]
                ),
            }
        )
        unsafe = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "computation_artifact.py"),
                "record",
                str(project),
                "--claim-id",
                "L2",
                "--local-claim",
                "Unrecorded inline expression.",
                "--backend",
                "mock-wolfram",
                "--backend-version",
                "mock-1",
                "--result-kind",
                "other",
                "--command-json",
                json.dumps(["codex-wmath", "2+2"]),
                "--input",
                "tool_checks/replay.wl",
                "--proof-translation",
                "This unsafe fixture must be rejected before execution.",
            ],
            capture_output=True,
            text=True,
            env=tool_env,
            check=False,
        )
        checks.append(
            {
                "name": "reject-inline-computation",
                "ok": unsafe.returncode != 0
                and "must name at least one recorded project-local script" in unsafe.stderr,
            }
        )
        weak_math_result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "computation_artifact.py"),
                "record",
                str(project),
                "--claim-id",
                "L3",
                "--local-claim",
                "A symbolic identity must match a canonical result.",
                "--backend",
                "mock-wolfram",
                "--backend-version",
                "mock-1",
                "--result-kind",
                "symbolic-identity",
                "--command-json",
                json.dumps(["codex-wmath", "-file", "tool_checks/replay.wl"]),
                "--input",
                "tool_checks/replay.wl",
                "--proof-translation",
                "The identity would support local lemma L3.",
            ],
            capture_output=True,
            text=True,
            env=tool_env,
            check=False,
        )
        checks.append(
            {
                "name": "reject-exit-only-mathematical-result",
                "ok": weak_math_result.returncode != 0
                and "exit-only shows process success" in weak_math_result.stderr,
            }
        )

        diagnosis = run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json")
        diagnosed = json.loads(diagnosis.stdout)
        checks.append(
            {
                "name": "proof-diagnosis",
                "ok": bool(diagnosed.get("primary_action"))
                and diagnosed.get("project") == str(project)
                and not diagnosed["novel_problem"]["activated"]
                and diagnosed["latest_referee"]["review_scope"]
                == "writeup/candidate.md",
            }
        )

        ledger = project / "LEDGER.md"
        ledger.write_text(
            ledger.read_text(encoding="utf-8").replace("S2-stress-test", "S9-stuck"),
            encoding="utf-8",
        )
        workstreams = project / "WORKSTREAMS.md"
        stalled = workstreams.read_text(encoding="utf-8") + (
            "\n- proof-state delta: unchanged\n"
            "- proof-state delta: unchanged\n"
        )
        workstreams.write_text(stalled, encoding="utf-8")
        stalled_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json").stdout
        )
        checks.append(
            {
                "name": "first-error-gate",
                "ok": stalled_diagnosis["failure_localization"]["needed"]
                and stalled_diagnosis["primary_action"].startswith("Localize the earliest failing step"),
            }
        )

        localized = stalled.replace(
            "- verified prefix:\n",
            "- verified prefix: steps 1-2 and helper lemma H1\n",
        ).replace(
            "- first failing step:\n",
            "- first failing step: step 3, Bellman difference sign\n",
        ).replace(
            "- failure witness or verifier error:\n",
            "- failure witness or verifier error: boundary state x=0 reverses the inequality\n",
        ).replace(
            "- independently rescued artifacts:\n",
            "- independently rescued artifacts: helper lemma H1\n",
        ).replace(
            "- failure stage: strategy-discovery / decomposition / premise-retrieval / local-proof / assembly / fidelity / library-coverage\n",
            "- failure stage: local-proof\n",
        ).replace(
            "- next scope: local trace-back / re-decompose / route replan / statement repair / stop-report\n",
            "- next scope: local trace-back\n",
        )
        workstreams.write_text(localized, encoding="utf-8")
        localized_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json").stdout
        )
        checks.append(
            {
                "name": "verified-prefix-salvage",
                "ok": not localized_diagnosis["failure_localization"]["needed"]
                and bool(localized_diagnosis["failure_localization"]["first_failing_step"])
                and bool(localized_diagnosis["failure_localization"]["rescued_artifacts"])
                and localized_diagnosis["primary_action"].startswith(
                    "Execute the localized scope: local trace-back"
                ),
            }
        )

        retrieval_failure = localized.replace(
            "- failure stage: local-proof\n",
            "- failure stage: retrieval\n",
        )
        workstreams.write_text(retrieval_failure, encoding="utf-8")
        retrieval_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json").stdout
        )
        checks.append(
            {
                "name": "failure-stage-routing",
                "ok": retrieval_diagnosis["failure_stage"]["stage"] == "premise-retrieval"
                and retrieval_diagnosis["primary_action"].startswith(
                    "Run sketch-retrieve-reflect"
                )
                and any(
                    "global premise retrieval" in query
                    for query in retrieval_diagnosis["external_pattern_scan"]["queries"]
                )
                and len(
                    retrieval_diagnosis["external_pattern_scan"]["capability_admission"]
                ) == 4,
            }
        )

        library_failure = retrieval_failure.replace(
            "- failure stage: retrieval\n",
            "- failure stage: library\n",
        )
        workstreams.write_text(library_failure, encoding="utf-8")
        library_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(project), "--json").stdout
        )
        checks.append(
            {
                "name": "formal-vocabulary-gate-routing",
                "ok": library_diagnosis["failure_stage"]["stage"] == "library-coverage"
                and "positive witness" in library_diagnosis["primary_action"]
                and any(
                    "custom definition auxiliary lemma" in query
                    for query in library_diagnosis["external_pattern_scan"]["queries"]
                ),
            }
        )

        discovery_created = run(
            str(SCRIPTS / "start_proof.py"),
            "--title",
            "smoke-discovery",
            "--claim",
            "Find the exact optimal threshold policy in a finite discounted MDP.",
            "--mode",
            "discovery",
            "--dir",
            temp_dir,
        )
        discovery_project = Path(discovery_created.stdout.strip())
        checks.append(
            {
                "name": "frontier-evidence-template",
                "ok": (discovery_project / "literature" / "frontier-evidence.json").is_file(),
            }
        )
        discovery_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(discovery_project), "--json").stdout
        )
        checks.append(
            {
                "name": "novel-frontier-scan-gate",
                "ok": discovery_diagnosis["novel_problem"]["activated"]
                and not discovery_diagnosis["novel_problem"]["ready_for_search"]
                and discovery_diagnosis["primary_action"].startswith(
                    "Run an external frontier scan"
                ),
            }
        )

        idea_map = discovery_project / "IDEA_MAP.md"
        discovery_text = idea_map.read_text(encoding="utf-8")
        memory_only = discovery_text.replace(
            "- known-solution status: not assessed / known / likely known / apparently open / genuinely new",
            "- known-solution status: known",
        )
        idea_map.write_text(memory_only, encoding="utf-8")
        memory_only_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(discovery_project), "--json").stdout
        )
        checks.append(
            {
                "name": "memory-is-not-known-evidence",
                "ok": memory_only_diagnosis["novel_problem"]["frontier_scan_needed"]
                and memory_only_diagnosis["primary_action"].startswith(
                    "Run an external frontier scan"
                ),
            }
        )
        idea_map.write_text(discovery_text, encoding="utf-8")

        evidence_dir = discovery_project / "literature" / "evidence"
        papers_dir = discovery_project / "literature" / "papers"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        papers_dir.mkdir(parents=True, exist_ok=True)
        query_one = evidence_dir / "q01.json"
        query_two = evidence_dir / "q02.json"
        query_one.write_text('{"query":"exact threshold policy theorem","results":["P1"]}\n', encoding="utf-8")
        query_two.write_text('{"query":"finite MDP monotone threshold cited by","results":["P1"]}\n', encoding="utf-8")
        paper_pdf = papers_dir / "P1.pdf"
        paper_bytes = b"%PDF-1.4\n% synthetic smoke fixture\n%%EOF\n"
        paper_pdf.write_bytes(paper_bytes)

        def digest(path: Path) -> str:
            return hashlib.sha256(path.read_bytes()).hexdigest()

        evidence_bundle = {
            "schema_version": 1,
            "claim": "Find the exact optimal threshold policy in a finite discounted MDP.",
            "discovery": {
                "method": "google-scholar-serpapi",
                "queries": [
                    {
                        "query": "exact threshold policy theorem",
                        "url": "https://scholar.google.com/scholar?q=exact+threshold+policy+theorem",
                        "retrieved_at": "2026-07-13",
                        "evidence_path": "literature/evidence/q01.json",
                        "evidence_sha256": digest(query_one),
                    },
                    {
                        "query": "finite MDP monotone threshold cited by",
                        "url": "https://scholar.google.com/scholar?q=finite+MDP+monotone+threshold+cited+by",
                        "retrieved_at": "2026-07-13",
                        "evidence_path": "literature/evidence/q02.json",
                        "evidence_sha256": digest(query_two),
                    },
                ],
            },
            "papers": [
                {
                    "id": "P1",
                    "title": "A closest finite-horizon threshold theorem",
                    "authors": ["Ada Researcher"],
                    "year": 2026,
                    "identifier": "arXiv:2604.15839",
                    "verification_url": "https://arxiv.org/abs/2604.15839",
                    "fulltext": {
                        "status": "proof-read",
                        "path": "literature/papers/P1.pdf",
                        "source_url": "https://arxiv.org/pdf/2604.15839",
                        "retrieved_at": "2026-07-13",
                        "sha256": digest(paper_pdf),
                        "bytes": len(paper_bytes),
                        "version": "preprint",
                        "access": "open-access",
                        "license": "test fixture",
                    },
                    "statement_anchor": "Theorem 2, p. 7, source block S042",
                    "proof_anchor": "Proof of Theorem 2, pp. 18-20, source blocks S131-S149",
                    "result": "A threshold policy is optimal under finite horizon and stronger monotonicity.",
                    "assumptions": "Finite horizon, ordered states, submodular one-step costs.",
                    "gap_to_claim": "The user's infinite-horizon formula is not established.",
                    "solution_card": {
                        "central_object": "Bellman action-difference function",
                        "proof_decomposition": "preserve increasing differences, then invoke single crossing",
                        "key_nonroutine_step": "couple continuation values to keep the action difference monotone",
                        "transplantable_move": "reuse the action-difference representation",
                        "new_bridge_lemma": "prove discounted Bellman iteration preserves the required single crossing",
                        "falsifier_or_evaluator": "exact Bellman inequalities on every state and action",
                    },
                }
            ],
            "activity": {
                "queries": ["2025..2026 cited-by and author-project search for P1"],
                "signals": [],
                "none_found_note": "No exact public project was visible under the recorded query by 2026-07-13.",
            },
            "frontier": {
                "status": "apparently-open",
                "closest_paper_ids": ["P1"],
                "exact_gap": "infinite-horizon threshold formula without the stronger monotonicity assumption",
                "assessment": "Two bounded Scholar queries and a proof-read closest source found only the stronger finite-horizon result.",
            },
            "limitations": ["Bounded search does not prove novelty."],
        }
        (discovery_project / "literature" / "frontier-evidence.json").write_text(
            json.dumps(evidence_bundle, indent=2) + "\n",
            encoding="utf-8",
        )
        evidence_validation = json.loads(
            run(str(SCRIPTS / "frontier_evidence.py"), "validate", str(discovery_project)).stdout
        )
        checks.append(
            {
                "name": "frontier-evidence-validation",
                "ok": evidence_validation["ok"]
                and evidence_validation["counts"]["proof_read"] == 1
                and evidence_validation["counts"]["queries"] == 2,
            }
        )

        setup_replacements = {
            "- frontier scan status: not run / completed": "- frontier scan status: completed",
            "- search cutoff date:": "- search cutoff date: 2026-07-13",
            "- Scholar queries:": "- Scholar queries: exact threshold-policy claim; cited-by search on closest Bellman theorem",
            "- verified source anchors:": "- verified source anchors: Closest Bellman theorem, https://arxiv.org/abs/2604.15839",
            "- closest known result:": "- closest known result: finite-horizon threshold theorem under stronger monotonicity",
            "- active-work signals:": "- active-work signals: two 2026 preprints study related finite-state models; no exact general theorem found",
            "- current frontier gap:": "- current frontier gap: infinite-horizon threshold formula without the stronger monotonicity assumption",
            "- known-solution status: not assessed / known / likely known / apparently open / genuinely new": "- known-solution status: apparently open",
            "- status evidence:": "- status evidence: bounded scan found solved finite neighbors but no general threshold theorem",
            "- discovery target: answer / threshold / formula / construction / policy / invariant / counterexample / intermediate theorem / new representation": "- discovery target: threshold formula",
            "- candidate representation:": "- candidate representation: integer threshold as a function of model parameters",
            "- validity gate:": "- validity gate: exact Bellman inequalities for every state and action",
            "- score or evaluator:": "- score or evaluator: feasibility first, then Bellman slack and formula complexity",
            "- simplification ladder:": "- simplification ladder: two states, finite horizon, then general finite discounted model",
            "- discovery budget:": "- discovery budget: 40 candidates or two plateau cycles",
        }
        for old, new in setup_replacements.items():
            discovery_text = discovery_text.replace(old, new)
        idea_map.write_text(discovery_text, encoding="utf-8")
        search_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(discovery_project), "--json").stdout
        )
        checks.append(
            {
                "name": "novel-discovery-search-routing",
                "ok": search_diagnosis["novel_problem"]["ready_for_search"]
                and search_diagnosis["primary_action"].startswith(
                    "Run one bounded discovery cycle"
                ),
            }
        )

        paper_pdf.write_bytes(paper_bytes + b"tampered")
        tampered_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(discovery_project), "--json").stdout
        )
        checks.append(
            {
                "name": "frontier-hash-tamper-gate",
                "ok": tampered_diagnosis["novel_problem"]["frontier_scan_needed"]
                and any(
                    "sha256 mismatch" in item
                    for item in tampered_diagnosis["novel_problem"]["frontier_missing"]
                ),
            }
        )
        paper_pdf.write_bytes(paper_bytes)

        promoted = idea_map.read_text(encoding="utf-8").replace(
            "- holdout cases:",
            "- holdout cases: larger state spaces and boundary discount factors",
        ).replace(
            "- promotion criterion:",
            "- promotion criterion: exact Bellman feasibility on seeds and holdouts",
        ).replace(
            "- discovered candidate:",
            "- discovered candidate: threshold tau(theta) from the fitted recurrence",
        ).replace(
            "- fixed proof handoff:",
            "- fixed proof handoff: prove policy tau(theta) satisfies every Bellman inequality",
        )
        idea_map.write_text(promoted, encoding="utf-8")
        handoff_diagnosis = json.loads(
            run(str(SCRIPTS / "proof_doctor.py"), str(discovery_project), "--json").stdout
        )
        checks.append(
            {
                "name": "novel-discovery-proof-handoff",
                "ok": handoff_diagnosis["novel_problem"]["handoff_ready"]
                and handoff_diagnosis["novel_problem"]["recommended_action"].startswith(
                    "Switch to the ordinary proof loop"
                )
                and not handoff_diagnosis["primary_action"].startswith(
                    "Run one bounded discovery cycle"
                ),
            }
        )

    portable_text = "".join(
        path.read_text(encoding="utf-8")
        for path in [
            ROOT / "SKILL.md",
            SCRIPTS / "start_proof.py",
            SCRIPTS / "proof_runtime.py",
            SCRIPTS / "lean_bridge.py",
            SCRIPTS / "computation_artifact.py",
            SCRIPTS / "run_referee.py",
            SCRIPTS / "proof_loop.py",
        ]
    )
    checks.append(
        {
            "name": "portable-paths",
            "ok": "/Users/" not in portable_text,
        }
    )

    research_text = (ROOT / "references" / "research-backed-proof-loop.md").read_text(
        encoding="utf-8"
    )
    proof_idea_text = (ROOT / "references" / "proof-idea-generator.md").read_text(
        encoding="utf-8"
    )
    strategy_text = (ROOT / "references" / "strategy-scheduler.md").read_text(
        encoding="utf-8"
    )
    verification_text = (ROOT / "references" / "verification-gate.md").read_text(
        encoding="utf-8"
    )
    escalation_text = (ROOT / "references" / "proof-escalation-protocol.md").read_text(
        encoding="utf-8"
    )
    discovery_text = (ROOT / "references" / "novel-problem-discovery.md").read_text(
        encoding="utf-8"
    )
    frontier_text = (ROOT / "references" / "full-text-frontier-evidence.md").read_text(
        encoding="utf-8"
    )
    peppy_text = (ROOT / "references" / "peppy-proof-bridge.md").read_text(
        encoding="utf-8"
    )
    lean_bridge_text = (ROOT / "references" / "lean-formalization-bridge.md").read_text(
        encoding="utf-8"
    )
    expert_consultation_text = (
        ROOT / "references" / "expert-consultation.md"
    ).read_text(encoding="utf-8")
    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    agent_text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    proof_loop_text = (SCRIPTS / "proof_loop.py").read_text(encoding="utf-8")
    idea_planner_text = (SCRIPTS / "plan_idea.py").read_text(encoding="utf-8")
    template_text = (SCRIPTS / "start_proof.py").read_text(encoding="utf-8")
    trick_template_text = (SCRIPTS / "new_trick_card.py").read_text(encoding="utf-8")
    audited_arxiv_ids = {
        "2411.00566",
        "2502.00212",
        "2502.17925",
        "2503.24036",
        "2504.21801",
        "2505.04528",
        "2506.11085",
        "2506.13131",
        "2506.19923",
        "2507.06804",
        "2507.15225",
        "2508.03613",
        "2509.06493",
        "2509.22819",
        "2510.01346",
        "2510.15940",
        "2511.13027",
        "2602.02285",
        "2602.02990",
        "2602.05216",
        "2602.10177",
        "2602.20629",
        "2603.02668",
        "2603.04735",
        "2603.19514",
        "2603.24465",
        "2604.07240",
        "2604.15839",
        "2604.17484",
        "2604.18897",
        "2604.24021",
        "2605.06651",
        "2605.09018",
        "2605.13137",
        "2605.13171",
        "2605.17283",
        "2605.19338",
        "2605.22763",
        "2605.26959",
        "2606.03303",
        "2606.05400",
        "2606.06473",
        "2606.09450",
        "2606.10479",
        "2606.13925",
        "2606.20068",
        "2606.20642",
        "2606.26442",
        "2606.28747",
        "2606.28841",
        "2606.29493",
        "2606.31134",
        "2607.04394",
        "2607.07779",
        "2607.09217",
        "2607.17352",
        "2607.27259",
    }
    checks.append(
        {
            "name": "research-control-map-and-source-coverage",
            "ok": all(
                phrase in research_text
                for phrase in [
                    "Decision Lanes",
                    "Paper Admission Gate",
                    "Stage attribution",
                    "A paper name in a prompt is never a capability",
                    "The controller, not the model's renamed route label",
                    "Training algorithms and benchmark designs are not additional runtime lanes",
                    "search a diverse frontier",
                    "artifact roles, not votes",
                    "The 57-paper audit",
                ]
            )
            and all(
                f"arxiv.org/abs/{paper_id}" in research_text
                for paper_id in audited_arxiv_ids
            )
            and all(
                f"arxiv.org/abs/{paper_id}" in research_text
                for paper_id in [
                    "2210.12283",
                    "2505.05758",
                    "2601.22554",
                    "2604.03789",
                    "2605.25143",
                    "2606.06468",
                    "2607.20525",
                ]
            )
            and "Decomposition Admission Gate" in template_text
            and "jointly sufficient premise bundle" in template_text
            and "post-proof parent replay" in template_text
            and "incompatible shadow family" in strategy_text
            and "Roles are a menu, not fixed quotas" in strategy_text
            and "Stage-Conditioned Strategy Trial" in strategy_text
            and "matched-baseline improvement" in strategy_text
            and "Exact Symmetry Quotient" in strategy_text
            and "Progressive Budget Grants" in strategy_text
            and "Information-Ordered Representation Switch" in strategy_text
            and "exact checker result or replayable witness" in strategy_text
            and "solver-owned attempt digest" in strategy_text
            and "Guarded proof-template reuse" in strategy_text
            and "Consumption gate" in strategy_text
            and "Semantic-obligation gate" in verification_text
            and "Completion-coverage gate" in verification_text
            and "underexplored family" in escalation_text
            and "Discover-To-Prove Handoff" in discovery_text
            and "Answer-hole contract" in discovery_text
            and "Google Scholar-backed discovery" in discovery_text
            and "SHA-256" in frontier_text
            and "solution card" in frontier_text
            and "no_authorized_pdf_found" in frontier_text
            and "PatternBoost" in discovery_text
            and "Self-supervised theorem discovery" in discovery_text
            and "Hard-witness regression set" in discovery_text,
        }
    )
    checks.append(
        {
            "name": "peppy-conditional-proof-bridge",
            "ok": "peppy-proof-bridge.md" in skill_text
            and "PEP Eligibility Gate" in peppy_text
            and "Stop after the first block" in peppy_text
            and "A small floating residual is not an exact certificate" in peppy_text
            and all(
                source in peppy_text
                for source in [
                    "10.1007/s10107-013-0653-0",
                    "10.1007/s10107-016-1009-3",
                    "10.1137/16M108104X",
                    "proceedings.mlr.press/v80/taylor18a.html",
                    "openreview.net/forum?id=tJqsZZBmmB",
                    "openreview.net/forum?id=q7TfzOgGnb",
                    "PEPFlow/tree/peppy-workshop-v1/examples_peppy",
                    "github.com/pepflow-lib/PEPFlow",
                ]
            )
            and all(
                block in peppy_text
                for block in [
                    "pep-implement",
                    "pep-full-proof",
                    "lyap-define",
                    "lyap-vectors",
                    "lyap-closed-form",
                ]
            ),
        }
    )
    checks.append(
        {
            "name": "evidence-layer-and-cache-poisoning-guards",
            "ok": all(
                phrase in proof_idea_text
                for phrase in [
                    "sound shortcuts",
                    "executable falsifiers",
                    "scheduler priors",
                    "near-miss frontier",
                    "No-small-counterexample results",
                    "poisoning later searches",
                    "Audit semantic range",
                ]
            )
            and "EvE's reported paper ablation concerns ICON code search" in research_text
            and "SAIR strategies are competition artifacts" in research_text
            and "Deterministic reductions, replayable witnesses" in research_text
            and "A notation change is not a new route" in research_text
            and "Do not load it during an ordinary first proof attempt" in research_text
            and "An idea is an executable hypothesis" in proof_idea_text
            and "creates a new proof obligation" in proof_idea_text
            and "Promotion And Reuse Gate" in trick_template_text
            and "allowed to seed future search" in trick_template_text,
        }
    )
    checks.append(
        {
            "name": "high-leverage-discovery-is-reachable",
            "ok": all(
                phrase in skill_text
                for phrase in [
                    "plan_idea.py",
                    "--discovery",
                    "certificate-first backward design",
                    "local-to-global upgrade",
                    "abstraction-refinement",
                    "bottom-up synthesis",
                    "equality-driven construction",
                    "source-checked proof migration",
                ]
            )
            and all(
                phrase in proof_idea_text
                for phrase in [
                    "Certificate-first backward design",
                    "Local-to-global upgrade",
                    "Abstraction-refinement and bottom-up synthesis",
                    "Equality-driven construction and algebra",
                    "Proof-move migration and trick replay",
                    "Theorem repair",
                ]
            )
            and all(
                phrase in proof_loop_text
                for phrase in [
                    "certificate-first backward design",
                    "local-to-global upgrade",
                    "equality-driven",
                    "abstraction-refinement",
                    "bottom-up special-case synthesis",
                    "source-checked proof migration",
                ]
            )
            and all(
                phrase in idea_planner_text
                for phrase in [
                    "Certificate-first",
                    "Local-to-global",
                    "Abstraction-refinement",
                    "Bottom-up synthesis",
                    "Equality-driven algebra",
                    "Trick replay",
                ]
            )
            and "choose one high-leverage discovery move" in agent_text,
        }
    )
    checks.append(
        {
            "name": "specialist-return-and-lean-fast-lane",
            "ok": all(
                phrase in skill_text
                for phrase in [
                    "Specialist Returns",
                    "lean-theorem-formalizer",
                    "status-preserving return",
                    "proof_loop.py",
                    "Hard exploration",
                    "key_original_step",
                ]
            )
            and "Interactive Fast Lane" in lean_bridge_text
            and "Formal Failure Surgery" in lean_bridge_text
            and "Valid allowing `sorry`" in lean_bridge_text
            and "equivalent to its parent" in lean_bridge_text
            and "scratch and repair, not promotion" in lean_bridge_text
            and "exact bridge verifier" in lean_bridge_text
            and "isolate it with exact context" in research_text
            and "One integrator owns theorem fidelity" in research_text,
        }
    )
    checks.append(
        {
            "name": "expert-consultation-is-bounded-and-non-evidentiary",
            "ok": "expert-consultation.md" in skill_text
            and '"expert-consultation"' in proof_loop_text
            and all(
                phrase in expert_consultation_text
                for phrase in [
                    "one call per unchanged proof-state tuple",
                    "The hard cap is two calls",
                    "fresh: true",
                    "no `recall`",
                    "proof_effect=none",
                    "explicitly opts in for the current task",
                    "stop immediately and do not retry",
                    "Run the proposed falsifier first",
                    "Never cite the consultation itself as proof authority",
                ]
            ),
        }
    )

    loop_smoke = json.loads(run(str(SCRIPTS / "smoke_proof_loop.py")).stdout)
    checks.append(
        {
            "name": "bounded-natural-proof-loop",
            "ok": bool(loop_smoke.get("ok"))
            and len(loop_smoke.get("checks", [])) == 15,
        }
    )

    result = {"ok": all(bool(check["ok"]) for check in checks), "checks": checks}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
