#!/usr/bin/env python3
"""Behavioral regressions for durable execution; fixtures do not measure proof ability."""

from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import proof_loop as loop
import proof_runtime as runtime
from loop_checkpoint import load_checkpoint
from run_referee import validate_verdict
from smoke_proof_loop import MOCK_CODEX

CLAIM = "For every integer n, n(n+1) is even."
ROOT = Path(__file__).resolve().parents[1]
INJECTION = '''
forced = os.environ.get("TEST_REFEREE_FAILURE", "")
if output.name == "scout.json" and forced == "crash-second-scout" and packet["scout_role"]["name"] != "structural":
    sys.exit(23)
if output.name == "generation.json" and forced == "follow-plan" and packet.get("stable_plan"):
    plan = packet["stable_plan"]
    payload.update(route_family=plan["route_family"], central_object=plan["central_object"],
                   proof_kernel=plan["key_original_step"], assumptions_used=plan["assumptions_used"])
if output.name == "verification.json":
    project = Path.cwd().parents[2]
    if forced == "mutate-candidate":
        (project / packet["candidate_proof_source"]).write_text("An unreviewed argument.\\n")
    elif forced == "mutate-packet":
        Path("packet.json").write_text("{}")
    elif forced == "mutate-reference":
        (project / packet["references"][0]["source_path"]).write_text("Different premises.\\n")
    elif forced == "mutate-copy":
        Path(packet["references"][0]["path"]).write_text("Different copied premises.\\n")
    elif forced == "mutate-contract":
        path = project / "claim.md"
        path.write_text(path.read_text() + "- Additional checked certificate required.\\n")
    if forced == "crash":
        sys.exit(3)
    if forced == "tool-evidence-gap":
        payload.update(verdict="uncertain", failure_kind=forced,
            first_error={"location": "certificate", "issue": "Replay the exact sign certificate."},
            gaps=[{"location": "certificate", "issue": "Missing replay."}], critical_errors=[])
    elif forced and payload["verdict"] == "wrong":
        payload["failure_kind"] = forced
        payload["first_error"] = {"location": "target", "issue": "The central implication proves a different quantified statement."}
output.write_text(json.dumps(payload), encoding="utf-8")
'''


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="proof-recovery-")
        self.root = Path(self.temp.name)
        self.codex = self.root / "bin" / "codex"
        self.codex.parent.mkdir()
        marker = 'output.write_text(json.dumps(payload), encoding="utf-8")'
        self.assertEqual(MOCK_CODEX.count(marker), 1)
        self.codex.write_text(MOCK_CODEX.replace(marker, INJECTION), encoding="utf-8")
        self.codex.chmod(0o755)

    def tearDown(self):
        self.temp.cleanup()

    def run_case(self, name, scenario="accept", iterations=1, *, failure="", extra=(), error=False):
        env = dict(os.environ, MOCK_PROOF_SCENARIO=scenario,
                   TEST_REFEREE_FAILURE=failure, PYTHONDONTWRITEBYTECODE="1")
        command = [sys.executable, str(ROOT / "scripts" / "proof_loop.py"),
                   str(self.root / name), "--max-iterations", str(iterations),
                   "--codex-bin", str(self.codex), *extra]
        if not (self.root / name).exists():
            command.extend(["--claim", CLAIM])
        result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=30)
        if error:
            self.assertNotEqual(result.returncode, 0)
            return result.stderr
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        return json.loads(result.stdout)

    def packet(self, name, result, iteration=1):
        path = self.root / name / ".proof_runtime" / "proof_loop_runs" / result["run_id"]
        return json.loads((path / f"iteration-{iteration:02d}" / "packet.json").read_text())

    def checkpoint(self, name):
        return load_checkpoint(self.root / name)

    def evidence(self, name, text="Exact local evidence with explicit assumptions."):
        path = self.root / name / "evidence.txt"
        path.write_text(text, encoding="utf-8")
        return ("--reference", "evidence.txt")

    def test_unicode_operators_and_assumptions_have_distinct_identities(self):
        a = dict(route_family="归纳法", central_object="不变量", proof_kernel="x < y", assumptions_used=["n≥0"])
        b = dict(route_family="对偶法", central_object="证书", proof_kernel="x > y", assumptions_used=["n≥0"])
        self.assertNotEqual(loop.route_signature(a), loop.route_signature(b))
        for field, value in [("proof_kernel", "x > y"), ("assumptions_used", ["n>0"])]:
            self.assertNotEqual(loop.route_signature(a), loop.route_signature({**a, field: value}))
        self.assertEqual(loop.normalize_signature(" e\u0301  ∀x "), "é ∀x")

    def test_claim_mismatch_and_central_failure_replan_without_derivation(self):
        for failure in ("claim-mismatch", "central-mechanism-failure", "assembly-gap"):
            result = self.run_case(failure, "repair", 2, failure=failure)
            packet = self.packet(failure, result, 2)
            self.assertEqual(packet["mode"], "replan")
            self.assertIsNone(packet["previous_candidate"])
            self.assertIsNone(packet["stable_plan"])

    def test_repair_survives_budget_boundary(self):
        first = self.run_case("split", "repair")
        self.assertEqual(first["status"], "budget-exhausted")
        self.assertEqual(self.checkpoint("split")["phase"], "repair")
        self.assertEqual(loop.prior_retired_routes(self.root / "split"), {})
        second = self.run_case("split")
        packet = self.packet("split", second)
        self.assertEqual(packet["mode"], "repair")
        self.assertIsNotNone(packet["previous_candidate"])
        self.assertTrue(packet["referee_feedback"]["first_error"]["issue"])
        uninterrupted = self.run_case("whole", "repair", 2)
        self.assertEqual(second["status"], uninterrupted["status"])
        for field in ("iterations", "agent_calls"):
            self.assertEqual(second["cumulative_usage"][field], uninterrupted["cumulative_usage"][field])

    def test_awaiting_plan_is_stable_and_idle_until_evidence(self):
        first = self.run_case("plan", "blocked", extra=("--hard-exploration",))
        saved = self.checkpoint("plan")
        self.assertEqual(saved["phase"], "awaiting-evidence")
        self.assertIsNotNone(saved["stable_plan"])
        idle = self.run_case("plan", extra=("--hard-exploration",))
        self.assertEqual(idle["evidence_request"]["request_id"], first["evidence_request"]["request_id"])
        self.assertEqual(idle["cumulative_usage"]["agent_calls"], first["cumulative_usage"]["agent_calls"])
        resumed = self.run_case("plan", extra=self.evidence("plan") + ("--hard-exploration",))
        self.assertEqual(self.packet("plan", resumed)["stable_plan"], saved["stable_plan"])
        self.assertEqual(loop.prior_retired_routes(self.root / "plan"), {})

    def test_tool_evidence_replays_existing_candidate(self):
        first = self.run_case("tool", failure="tool-evidence-gap")
        self.assertEqual(first["requested_capability"], "tool-replay")
        candidate = self.checkpoint("tool")["pending_candidate"]["artifact"]
        resumed = self.run_case("tool", extra=self.evidence("tool"))
        self.assertEqual(resumed["status"], "referee-accepted")
        self.assertEqual(self.checkpoint("tool")["pending_candidate"]["artifact"], candidate)
        self.assertEqual(resumed["cumulative_usage"]["iterations"], 1)

    def test_referee_crash_resumes_verification_without_regeneration(self):
        first = self.run_case("crash", failure="crash")
        self.assertEqual(first["status"], "runtime-error")
        self.assertEqual(self.checkpoint("crash")["phase"], "verify")
        resumed = self.run_case("crash")
        self.assertEqual(resumed["status"], "referee-accepted")
        self.assertEqual(resumed["cumulative_usage"]["iterations"], 1)
        self.assertEqual(loop.prior_retired_routes(self.root / "crash"), {})

    def test_scout_evidence_wait_does_not_repeat_scouts(self):
        first = self.run_case("scouts", "hard_blocked", extra=("--hard-exploration",))
        idle = self.run_case("scouts", "hard_blocked", extra=("--hard-exploration",))
        self.assertEqual(idle["status"], "needs-evidence")
        self.assertEqual(first["cumulative_usage"]["agent_calls"], 2)
        self.assertEqual(idle["cumulative_usage"]["agent_calls"], 2)

    def test_changed_evidence_requires_explicit_reference_and_reverification(self):
        self.run_case("refs", "blocked")
        self.run_case("refs", extra=self.evidence("refs"))
        args = self.evidence("refs", "Revised exact evidence.")
        self.assertIn("artifact changed", self.run_case("refs", error=True))
        resumed = self.run_case("refs", extra=args)
        self.assertEqual(resumed["status"], "referee-accepted")
        self.assertNotIn("reused_completed_result", resumed)

    def test_changed_candidate_is_never_reused(self):
        self.run_case("tamper", failure="crash")
        descriptor = self.checkpoint("tamper")["pending_candidate"]["artifact"]
        (self.root / "tamper" / descriptor["path"]).write_text("A different argument.")
        result = self.run_case("tamper")
        self.assertEqual(result["status"], "runtime-error")
        self.assertIn("artifact changed", result["obstruction"])

    def test_updated_evidence_does_not_leave_a_stale_accepted_state(self):
        self.run_case("recheck", "blocked")
        self.run_case("recheck", extra=self.evidence("recheck"))
        result = self.run_case("recheck", failure="crash", extra=self.evidence("recheck", "Changed premises."))
        self.assertEqual(result["status"], "runtime-error")
        state = runtime.read_state(self.root / "recheck")
        self.assertEqual(state["proof_status"], "unresolved")
        self.assertEqual(state["evidence_summary"]["disposition"], "pending")

    def test_accepted_referee_report_hash_is_checked_on_reuse(self):
        result = self.run_case("report")
        Path(result["referee_report"]).write_text("{}")
        self.assertIn("artifact changed", self.run_case("report", error=True))

    def test_contract_change_rechecks_existing_candidate_and_downgrades_status(self):
        first = self.run_case("contract")
        project = self.root / "contract"
        path = project / "claim.md"
        path.write_text(path.read_text() + "- Require a checked Lean file without sorry or extra axioms.\n")
        waiting = self.run_case("contract", failure="tool-evidence-gap")
        self.assertEqual(waiting["status"], "needs-evidence")
        self.assertNotIn("reused_completed_result", waiting)
        self.assertEqual(waiting["cumulative_usage"]["iterations"], 1)
        self.assertEqual(waiting["cumulative_usage"]["agent_calls"], first["cumulative_usage"]["agent_calls"] + 1)
        self.assertEqual(runtime.read_state(project)["proof_status"], "unresolved")

    def test_legacy_completion_requires_a_new_review(self):
        for missing in ("contract", "packet"):
            with self.subTest(missing=missing):
                name = "legacy-" + missing
                self.run_case(name)
                project = self.root / name
                path = project / ".proof_runtime" / "proof_loop_checkpoint.json"
                saved = json.loads(path.read_text())
                saved.pop("checkpoint_sha256")
                if missing == "contract":
                    saved.pop("acceptance_contract_sha256")
                else:
                    saved["result"].pop("referee_packet_descriptor")
                saved["checkpoint_sha256"] = runtime.sha256_text(runtime.canonical_json(saved))
                runtime.atomic_write_json(path, saved)
                resumed = self.run_case(name)
                self.assertEqual(resumed["status"], "referee-accepted")
                self.assertNotIn("reused_completed_result", resumed)
                self.assertEqual(resumed["cumulative_usage"]["agent_calls"], 3)
                self.assertEqual(resumed["cumulative_usage"]["iterations"], 1)

    def test_changes_during_review_cannot_be_accepted_or_retire_a_route(self):
        for target in ("candidate", "packet", "reference", "copy"):
            with self.subTest(target=target):
                name = "race-" + target
                self.run_case(name, "blocked")
                result = self.run_case(name, failure="mutate-" + target, extra=self.evidence(name))
                self.assertEqual(result["status"], "runtime-error")
                self.assertEqual(self.checkpoint(name)["phase"], "verify")
                self.assertEqual(loop.prior_retired_routes(self.root / name), {})
                self.assertNotEqual(runtime.read_state(self.root / name)["proof_status"], "referee-accepted")
                self.assertFalse((self.root / name / "writeup" / "referee_accepted_proof.md").exists())

    def test_contract_change_during_review_fences_acceptance_and_can_resume(self):
        self.assertIn("acceptance contract changed", self.run_case("contract-race", failure="mutate-contract", error=True))
        self.assertEqual(self.checkpoint("contract-race")["phase"], "verify")
        self.assertNotEqual(runtime.read_state(self.root / "contract-race")["proof_status"], "referee-accepted")
        resumed = self.run_case("contract-race")
        self.assertEqual(resumed["status"], "referee-accepted")
        self.assertEqual(resumed["cumulative_usage"]["iterations"], 1)

    def test_accepted_packet_hash_is_checked_and_published_proof_matches_snapshot(self):
        result = self.run_case("packet")
        project = self.root / "packet"
        packet_path = project / result["referee_packet_descriptor"]["path"]
        packet = json.loads(packet_path.read_text())
        self.assertEqual(runtime.sha256_file(Path(result["artifact"])), packet["candidate_proof_sha256"])
        packet_path.write_text("{}")
        self.assertIn("artifact changed", self.run_case("packet", error=True))

    def test_duplicate_scout_after_interruption_can_resume_selected_route(self):
        first = self.run_case("duplicate", failure="crash-second-scout", extra=("--hard-exploration",))
        self.assertEqual(first["status"], "runtime-error")
        self.run_case("duplicate", "blocked", failure="follow-plan", extra=("--hard-exploration",))
        project = self.root / "duplicate"
        self.assertIsNotNone(self.checkpoint("duplicate")["stable_plan"])
        self.assertEqual(loop.prior_retired_routes(project), {})
        resumed = self.run_case("duplicate", failure="follow-plan", extra=("--hard-exploration",) + self.evidence("duplicate"))
        self.assertEqual(resumed["status"], "referee-accepted")

    def test_legacy_duplicate_only_retirements_are_ignored_but_real_failures_remain(self):
        self.run_case("legacy-route", "blocked", extra=("--hard-exploration",))
        project = self.root / "legacy-route"
        plan = self.checkpoint("legacy-route")["stable_plan"]
        candidate = {**plan, "candidate_id": "historical-duplicate"}
        for reason in (loop.DUPLICATE_ROUTE_REASON, loop.EXCLUDED_ROUTE_REASON):
            loop.record_plan_disposition(project, "legacy", candidate, "retire", reason)
        self.assertEqual(loop.prior_retired_routes(project), {})
        loop.record_retirement(project, {**plan, "proof_kernel": plan["key_original_step"]},
                               plan["route_signature"], "A concrete counterexample defeats this route.")
        self.assertIn(plan["route_signature"], loop.prior_retired_routes(project))

    def test_deferred_route_can_be_selected_after_explicit_retirement(self):
        self.run_case("history", extra=("--hard-exploration",))
        project = self.root / "history"
        plan = self.checkpoint("history")["stable_plan"]
        loop.record_retirement(project, {**plan, "proof_kernel": plan["key_original_step"]},
                               plan["route_signature"], "Explicit fixture retirement after inspection.")
        result = self.run_case("history", extra=("--fresh-attempt", "--hard-exploration"))
        run_dir = project / ".proof_runtime" / "proof_loop_runs" / result["run_id"] / "hard-exploration"
        selected = json.loads((run_dir / "selected_plan.json").read_text())
        self.assertEqual(selected["source"], "historical-untried-route")
        self.assertEqual(len(list(run_dir.glob("scout-*/scout.json"))), 1)

    def test_claim_revision_invalidates_checkpoint_and_exclusions_but_keeps_history(self):
        self.run_case("revision", "replan", 2)
        project = self.root / "revision"
        self.assertTrue(loop.prior_retired_routes(project))
        routing_path = project / "routing.json"
        routing = json.loads(routing_path.read_text())
        routing["claim"] = "For every nonnegative integer n, n(n+1) is even."
        routing_path.write_text(json.dumps(routing))
        (project / "claim.md").write_text("# Claim\n\n" + routing["claim"] + "\n")
        runtime.revise_claim(project, "Explicit domain restriction for the regression fixture.")
        self.assertEqual(loop.prior_retired_routes(project), {})
        self.assertEqual(self.checkpoint("revision")["phase"], "solve")
        self.assertIsNone(self.checkpoint("revision")["previous_candidate"])
        self.assertGreater(len(list(runtime.iter_channel(project, "attempts"))), 0)

    def test_completed_result_is_cached_and_fresh_attempt_preserves_compute(self):
        accepted = self.run_case("cache")
        cached = self.run_case("cache")
        preview = self.run_case("cache", extra=("--prepare-only",))
        self.assertTrue(cached["reused_completed_result"])
        self.assertTrue(preview["reused_completed_result"])
        self.assertEqual(cached["cumulative_usage"]["agent_calls"], 2)
        fresh = self.run_case("cache", extra=("--fresh-attempt",))
        self.assertEqual(fresh["cumulative_usage"]["agent_calls"], 4)
        self.assertEqual(accepted["proof_status"], "referee-accepted")
        self.assertFalse(accepted["evidence_summary"]["formal_verification"])
        self.assertFalse(accepted["evidence_summary"]["human_reviewed"])

    def test_empty_rejection_cannot_retire_a_route(self):
        verdict = dict(summary="No evidence.", verdict="wrong", failure_kind="none",
                       claim_fidelity={"status": "pass", "issue": ""},
                       assumption_coverage={"status": "pass", "issue": ""},
                       first_error={"location": "", "issue": ""},
                       critical_errors=[], gaps=[], repair_hints=[])
        checked, errors = validate_verdict(copy.deepcopy(verdict))
        self.assertEqual(checked["verdict"], "uncertain")
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
