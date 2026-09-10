#!/usr/bin/env python3
"""Regression tests for evidence scope, freshness, and project completion.

Lean responses here are explicit checker-contract fixtures. Real local Lean
reproductions are recorded separately by the audit; no model or network is used.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
import audit_ledger
import computation_artifact
import frontier_evidence
import lean_bridge
import proof_doctor
import proof_runtime


class EvidenceLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=os.environ.get("MATH_RESEARCH_TEST_TMPDIR"))
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / "project"
        self.root.mkdir()
        self.claim = "For every natural number n, n + 0 = n."
        self.write_json(self.root / "routing.json", {"claim": self.claim, "mode": "project"})
        (self.root / "claim.md").write_text(f"# Claim\n\n{self.claim}\n")
        bodies = {name: "The fixed arithmetic proof has no additional obligations." for name in audit_ledger.REQUIRED_HEADINGS}
        bodies.update({"Claim": self.claim, "Status": "complete", "Verification Status": "tool-checked",
                       "Proof State": "S8-finalize", "Mode Decision": "- mode: project"})
        (self.root / "LEDGER.md").write_text("# Ledger\n\n" + "\n\n".join(
            f"## {name}\n\n{bodies[name]}" for name in audit_ledger.REQUIRED_HEADINGS))
        (self.root / "lean").mkdir()
        self.target = self.root / "lean/Target.lean"
        self.target.write_text("theorem audit_target (n : Nat) : n + 0 = n := by simp\n")
        (self.root / "statement.md").write_text(self.claim + "\n")
        self.checker = Path(self.temporary.name) / "checker_fixture.py"
        self.checker.write_text("# Typed checker response is supplied by this test.\n")
        self.python_runner = Path(self.temporary.name) / "codex-math-python"
        self.python_runner.symlink_to(Path(sys.executable).resolve())

    @staticmethod
    def write_json(path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n")

    def checker_response(self, command, **_):
        path = Path(command[2])
        blocked = "sorry" in path.read_text()
        target_name, target_kind = command[command.index("--require-decl-kind") + 1].split(":")
        payload = {"exit_code": int(blocked), "results": [{
            "path": str(path),
            "blockers": {"sorry": int(blocked), "admit": 0, "axiom": 0, "constant": 0, "unsafe": 0},
            "total_blockers": int(blocked),
            "declaration_list": [{"name": target_name, "full_name": target_name, "kind": target_kind}],
            "missing_required_declaration_kinds": [],
            "check": {"returncode": 0, "stdout": "", "stderr": "", "timed_out": False},
        }]}
        return subprocess.CompletedProcess(command, int(blocked), json.dumps(payload), "")

    def lean(self, *args, response=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(sys, "argv", ["lean_bridge.py", *map(str, args)]), \
             patch.object(lean_bridge.subprocess, "run", side_effect=response or self.checker_response), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = lean_bridge.main()
        payload = json.loads(stdout.getvalue()) if stdout.getvalue() else {}
        return code, payload, stderr.getvalue()

    def prepare(self, *, full=True):
        code, result, error = self.lean("prepare", self.root, "--node-id", "N1",
            "--role", "full-theorem" if full else "local-lemma", "--statement-file", "statement.md",
            "--lean-file", "lean/Target.lean", "--target-name", "audit_target",
            "--downstream-use", "Establish the frozen original theorem.")
        self.assertEqual(code, 0, error)
        self.request = Path(result["request_path"])
        self.packet = result["packet"]
        return result

    def fill_acceptance(self):
        path = self.root / self.packet["acceptance_report"]
        payload = json.loads(path.read_text())
        for name in payload["checks"]:
            payload["checks"][name] = {"status": "pass", "evidence": f"Fixture audit of the current target: {name}."}
        self.write_json(path, payload)

    def verify(self, *, promote=True, response=None):
        return self.lean("verify", self.root, self.request, "--lean-status-script", self.checker,
                         *(["--promote-final"] if promote else []), response=response)

    def promote(self):
        self.prepare()
        self.fill_acceptance()
        code, result, error = self.verify()
        self.assertEqual(code, 0, error or result)
        self.assertTrue(result["eligible_for_formalized_complete"])
        return result

    def test_faithful_full_target_passes_and_missing_gates_do_not(self):
        self.prepare()
        code, result, _ = self.verify()
        self.assertEqual(code, 2)
        self.assertEqual(result["node_status"], "formalized-local")
        self.assertFalse(result["eligible_for_formalized_complete"])
        self.fill_acceptance()
        self.assertEqual(self.verify()[0], 0)
        diagnosis = proof_doctor.diagnose(self.root)
        self.assertTrue(diagnosis["audit"]["ready_for_final_proof"], diagnosis["latest_referee"])

    def test_changed_target_resets_audit_and_revokes_completion(self):
        self.promote()
        self.target.write_text("theorem audit_target : True := by trivial\n")
        code, result, _ = self.verify()
        self.assertEqual(code, 2)
        self.assertTrue(result["acceptance_binding_refreshed"])
        self.assertFalse(result["eligible_for_formalized_complete"])
        self.assertTrue(all(item["status"] == "not-audited" for item in result["acceptance_report"]["checks"].values()))
        self.assertEqual(proof_runtime.read_state(self.root)["proof_status"], "unresolved")
        self.assertFalse(proof_doctor.diagnose(self.root)["audit"]["ready_for_final_proof"])

    def test_failed_recheck_revokes_completion_and_blocks_doctor(self):
        self.promote()
        self.target.write_text("theorem audit_target (n : Nat) : n + 0 = n := by sorry\n")
        code, result, _ = self.verify()
        self.assertEqual(code, 2)
        self.assertEqual(result["node_status"], "blocked")
        self.assertEqual(proof_runtime.read_state(self.root)["proof_status"], "unresolved")
        diagnosis = proof_doctor.diagnose(self.root)
        self.assertTrue(diagnosis["latest_referee"]["invalid_formal_artifacts"])
        self.assertFalse(diagnosis["audit"]["ready_for_final_proof"])

    def test_failed_formal_evidence_allows_named_nonfinal_repair_only(self):
        self.promote()
        self.target.write_text("theorem audit_target (n : Nat) : n + 0 = n := by sorry\n")
        self.assertEqual(self.verify()[0], 2)
        ledger = self.root / "LEDGER.md"
        ledger.write_text(ledger.read_text().replace("S8-finalize", "S9-stuck"))
        workstreams = self.root / "WORKSTREAMS.md"
        stalled = "# Failure Localization And Salvage\n\n" + "- proof-state delta: unchanged\n" * 2
        workstreams.write_text(stalled)
        diagnosis = proof_doctor.diagnose(self.root)
        self.assertTrue(diagnosis["failure_localization"]["needed"])
        self.assertTrue(diagnosis["primary_action"].startswith("Localize the earliest failing step"))
        self.assertFalse(diagnosis["audit"]["ready_for_final_proof"])
        localized = stalled + (
            "- verified prefix: the natural-number domain is fixed\n"
            "- first failing step: step 2, the final simplification is unavailable\n"
            "- failure witness or verifier error: the selected source still has an admission\n"
            "- independently rescued artifacts: the domain fidelity check\n"
            "- next scope: local trace-back\n"
        )
        for stage, expected in (
            ("local-proof", "Execute the localized scope: local trace-back"),
            ("retrieval", "Run sketch-retrieve-reflect"),
            ("library", "positive witness"),
        ):
            with self.subTest(stage=stage):
                workstreams.write_text(localized + f"- failure stage: {stage}\n")
                diagnosis = proof_doctor.diagnose(self.root)
                self.assertIn(expected, diagnosis["primary_action"])
                self.assertTrue(diagnosis["latest_referee"]["invalid_formal_artifacts"])
                self.assertFalse(diagnosis["audit"]["ready_for_final_proof"])
        channel = proof_runtime.channel_path(self.root, "computations")
        original = channel.read_text()
        channel.write_text(original + '{"schema_version": 1, "record":\n')
        corrupt = proof_doctor.diagnose(self.root)
        self.assertFalse(corrupt["latest_referee"]["runtime_integrity_ok"])
        self.assertTrue(corrupt["primary_action"].startswith("Repair the invalid runtime record"))
        channel.write_text(original)
        ledger.write_text(ledger.read_text().replace("S9-stuck", "S8-finalize"))
        finalizing = proof_doctor.diagnose(self.root)
        self.assertFalse(finalizing["audit"]["ready_for_final_proof"])
        self.assertTrue(finalizing["primary_action"].startswith("Repair the invalid or stale runtime evidence"))

    def test_stale_statement_source_is_rejected_before_checker(self):
        self.promote()
        (self.root / "statement.md").write_text("For every natural number n, n + 1 = n.\n")
        def unexpected(*_, **__):
            self.fail("The checker must not run for a stale frozen statement source.")
        code, _, error = self.verify(response=unexpected)
        self.assertEqual(code, 2)
        self.assertIn("statement source changed", error)
        self.assertEqual(proof_runtime.read_state(self.root)["proof_status"], "unresolved")

    def test_changed_local_dependency_requires_new_final_audit(self):
        (self.root / "lean/Premise.lean").write_text("theorem premise : True := by trivial\n")
        self.promote()
        (self.root / "lean/Premise.lean").write_text("theorem premise (h : False) : True := by trivial\n")
        code, result, _ = self.verify()
        self.assertEqual(code, 2)
        self.assertTrue(result["acceptance_binding_refreshed"])

    def test_malformed_success_is_rejected_and_revokes_active_acceptance(self):
        for variant in ("empty_scan", "name", "full_name", "kind"):
            with self.subTest(variant=variant):
                self.promote()
                def malformed(command, **kwargs):
                    payload = json.loads(self.checker_response(command, **kwargs).stdout)
                    if variant == "empty_scan":
                        payload["results"] = [{}]
                    else:
                        payload["results"][0]["declaration_list"][0][variant] = []
                    return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")
                code, _, error = self.verify(response=malformed)
                self.assertEqual(code, 2)
                self.assertIn("malformed Lean checker result", error)
                self.assertEqual(proof_runtime.read_state(self.root)["proof_status"], "unresolved")
                self.assertFalse(proof_doctor.diagnose(self.root)["audit"]["ready_for_final_proof"])

    def test_inconsistent_checker_gates_are_rejected(self):
        self.prepare(full=False)
        for mutation in ("compile", "counts", "target", "path"):
            with self.subTest(mutation=mutation):
                def malformed(command, **kwargs):
                    proc = self.checker_response(command, **kwargs)
                    payload = json.loads(proc.stdout)
                    scan = payload["results"][0]
                    if mutation == "compile":
                        scan.pop("check")
                    elif mutation == "counts":
                        scan["blockers"]["sorry"] = 1
                    elif mutation == "target":
                        scan["declaration_list"] = []
                    else:
                        scan["path"] = str(self.root / "another.lean")
                    return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")
                self.assertEqual(self.verify(promote=False, response=malformed)[0], 2)

    def test_altered_formal_result_is_not_usable_evidence(self):
        self.promote()
        state = proof_runtime.read_state(self.root)
        path = self.root / state["last_decisive_artifact"]
        result = json.loads(path.read_text())
        result["statement"] = "An altered statement."
        self.write_json(path, result)
        diagnosis = proof_doctor.diagnose(self.root)
        self.assertFalse(diagnosis["audit"]["ready_for_final_proof"])
        self.assertTrue(diagnosis["latest_referee"]["invalid_formal_artifacts"])

    def test_corrupt_runtime_channels_fail_closed(self):
        proof_runtime.ensure_runtime(self.root)
        for channel in proof_runtime.CHANNELS:
            with self.subTest(channel=channel):
                path = proof_runtime.channel_path(self.root, channel)
                original = path.read_text()
                path.write_text(original + '{"schema_version": 1, "record":\n')
                diagnosis = proof_doctor.diagnose(self.root)
                self.assertFalse(diagnosis["audit"]["runtime_evidence_ready"])
                self.assertFalse(diagnosis["audit"]["ready_for_final_proof"])
                self.assertTrue(diagnosis["latest_referee"]["runtime_errors"])
                path.write_text(original)

    def test_legacy_cross_scope_supersession_is_rejected_by_doctor(self):
        ids = []
        (self.root / "expected.txt").write_text("4\n")
        for index, expression in enumerate(("2 + 2", "2 * 2"), start=1):
            script = f"exact{index}.py"
            (self.root / script).write_text(f"print({expression})\n")
            args = computation_artifact.build_parser().parse_args([
                "record", str(self.root), "--claim-id", f"L{index}", "--local-claim", f"{expression} = 4.",
                "--backend", "Python", "--backend-version", "installed", "--result-kind", "symbolic-identity",
                "--command-json", json.dumps([str(self.python_runner), script]), "--input", script,
                "--compare", "stdout-exact", "--expected-output", "expected.txt", "--proof-translation", "Fixed exact arithmetic.",
            ])
            artifact = computation_artifact.record_artifact(args)
            ids.append(artifact["artifact_id"])
            replay_args = computation_artifact.build_parser().parse_args(["replay", str(self.root), ids[-1], "--timeout", "10"])
            self.assertEqual(computation_artifact.replay_artifact(replay_args)["status"], "passed")
        # Simulate a record made by the old supported supersession command.
        proof_runtime.append_record(self.root, "computations", {"event_type": "computation_superseded",
            "artifact_id": ids[0], "replacement_artifact_id": ids[1], "replacement_claim_id": "L2", "reason": "Legacy replacement."})
        feedback = proof_doctor.runtime_referee_feedback(self.root)
        self.assertTrue(feedback["invalid_computation_artifacts"])
        self.assertNotIn("L1", feedback["passed_claim_ids"])

    def frontier(self):
        bundle = frontier_evidence.blank_bundle(self.claim)
        bundle["discovery"]["method"] = "google-scholar-browser"
        for index in (1, 2):
            path = self.root / f"literature/evidence/q{index}.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"Synthetic contract fixture {index}; no search was executed.\n")
            bundle["discovery"]["queries"].append({"query": f"synthetic query {index}",
                "url": f"https://scholar.google.com/scholar?q=fixture{index}", "retrieved_at": frontier_evidence.today(),
                "evidence_path": str(path.relative_to(self.root)), "evidence_sha256": frontier_evidence.sha256_file(path)})
        path = self.root / "literature/source.txt"
        path.write_text("Synthetic source. Theorem 1: n + 0 = n. Proof: natural-number recursion.\n")
        paper = frontier_evidence.base_paper("P1", "Synthetic contract source", ["Fixture Author"], 2026,
            "official:fixture", "https://example.edu/fixture", {"status": "proof-read", "path": "literature/source.txt",
            "source_url": "https://example.edu/fixture.txt", "retrieved_at": frontier_evidence.today(),
            "version": "synthetic-v1", "access": "user-provided", "sha256": frontier_evidence.sha256_file(path), "bytes": path.stat().st_size})
        paper.update({"statement_anchor": "Theorem 1", "proof_anchor": "Proof of Theorem 1", "result": self.claim,
                      "assumptions": "Natural numbers.", "gap_to_claim": "Identical claim."})
        paper["solution_card"] = {key: "Synthetic arithmetic proof decomposition." for key in paper["solution_card"]}
        bundle["papers"] = [paper]
        bundle["activity"] = {"queries": ["synthetic recent-work check"], "signals": [], "none_found_note": "Synthetic fixture only."}
        bundle["frontier"] = {"status": "known", "closest_paper_ids": ["P1"], "exact_gap": "No gap.", "assessment": "Synthetic fixture only."}
        self.write_json(self.root / "literature/frontier-evidence.json", bundle)
        return bundle

    def test_all_canonical_frontier_statuses_round_trip(self):
        bundle = self.frontier()
        for status in frontier_evidence.FRONTIER_STATUSES:
            with self.subTest(status=status):
                bundle["frontier"]["status"] = status
                self.write_json(self.root / "literature/frontier-evidence.json", bundle)
                self.assertTrue(frontier_evidence.validate_frontier_bundle(self.root)["ok"])
                result = proof_doctor.novel_problem_summary(self.root, "project")
                self.assertEqual(result["status"], status)
                self.assertTrue(result["frontier_verified"])

    def test_frontier_binds_claim_md_fallback(self):
        bundle = self.frontier()
        (self.root / "routing.json").unlink()
        bundle["claim"] = "2 + 2 = 4."
        self.write_json(self.root / "literature/frontier-evidence.json", bundle)
        self.assertFalse(frontier_evidence.validate_frontier_bundle(self.root)["ok"])
        self.assertFalse(proof_doctor.novel_problem_summary(self.root, "project")["frontier_verified"])

    def test_stale_required_frontier_source_blocks_finalization(self):
        self.frontier()
        self.assertTrue(proof_doctor.diagnose(self.root)["audit"]["ready_for_final_proof"])
        (self.root / "literature/source.txt").write_text("Changed source.\n")
        diagnosis = proof_doctor.diagnose(self.root)
        self.assertFalse(diagnosis["audit"]["frontier_evidence_ready"])
        self.assertFalse(diagnosis["audit"]["ready_for_final_proof"])
        self.assertIn("frontier scan", diagnosis["primary_action"])

    def test_malformed_frontier_manifest_is_a_blocker(self):
        self.frontier()
        (self.root / "literature/frontier-evidence.json").write_text('{"claim":')
        diagnosis = proof_doctor.diagnose(self.root)
        self.assertFalse(diagnosis["audit"]["ready_for_final_proof"])
        self.assertTrue(diagnosis["novel_problem"]["frontier_missing"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
