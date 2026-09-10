#!/usr/bin/env python3
"""Exercise manual route-history decisions through the public CLI."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("check_attempt.py")
FIELDS = ["route_family", "central_object", "target_lemma", "parameterization",
          "invariant_certificate", "failure_witness", "missing_assumption"]
BASE = dict(zip(FIELDS, ["duality", "potential", "x < y", "n >= 0", "A + b", "x = 0", "convexity"]))


class AttemptMatchingTests(unittest.TestCase):
    def run_case(self, entry=BASE, proposed=None, status="failed", delta=""):
        with tempfile.TemporaryDirectory(prefix="math-attempt-") as raw:
            project = Path(raw)
            row = "| A1 | " + status + " | " + " | ".join(entry.values()) + " | evidence | repair |\n"
            (project / "WORKSTREAMS.md").write_text("## Attempt Fingerprint Index\n\n" + row + "\n## No-Repeat Decision\n")
            command = [sys.executable, str(SCRIPT), str(project), "--json", "--new-delta", delta]
            for field, value in (entry if proposed is None else proposed).items():
                command.extend(["--" + field.replace("_", "-"), value])
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

    def test_exact_chinese_failure_is_recognized(self):
        entry = dict(zip(FIELDS, ["归纳法", "势函数", "单调性", "整数域", "边界恒等式", "负值反例", "非负性"]))
        self.assertEqual(self.run_case(entry)["decision"], "block-repeat")

    def test_operator_case_and_assumption_changes_are_not_exact_repeats(self):
        for field, value in [("target_lemma", "x > y"), ("parameterization", "n > 0"),
                             ("invariant_certificate", "a + b")]:
            with self.subTest(field=field):
                result = self.run_case(proposed={**BASE, field: value})
                self.assertEqual(result["decision"], "review-similar")
                self.assertFalse(any(item["exact_failed_repeat"] for item in result["matches"]))

    def test_untried_active_and_unknown_statuses_are_not_failures(self):
        for status in ("untried", "active", "blocked", ""):
            with self.subTest(status=status):
                self.assertNotEqual(self.run_case(status=status)["decision"], "block-repeat")

    def test_shared_route_names_do_not_block_a_different_kernel(self):
        proposed = dict(route_family="duality", central_object="potential", target_lemma="compactness")
        self.assertEqual(self.run_case(proposed=proposed)["decision"], "review-similar")

    def test_missing_fingerprint_fields_require_review(self):
        proposed = {k: v for k, v in BASE.items() if k != "parameterization"}
        self.assertEqual(self.run_case(proposed=proposed)["decision"], "review-similar")

    def test_exact_failure_requires_a_nonempty_explicit_change(self):
        self.assertEqual(self.run_case(delta="  ")["decision"], "block-repeat")
        result = self.run_case(delta="A new independently checked certificate replaces the failed step.")
        self.assertEqual(result["decision"], "allow-with-delta")
        self.assertEqual(result["proof_effect"], "none")


if __name__ == "__main__":
    unittest.main(verbosity=2)
