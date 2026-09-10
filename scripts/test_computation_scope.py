#!/usr/bin/env python3
"""Check command dependencies and replacement scope with real Python replays."""
from argparse import Namespace
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import computation_artifact as comp
import proof_runtime as runtime


class ComputationScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="math-computation-")
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()
        (self.project / "routing.json").write_text(json.dumps({"claim": "The fixed arithmetic identities hold."}))
        runtime.ensure_runtime(self.project)
        self.runner = self.root / "codex-math-python"
        self.runner.symlink_to(sys.executable)
        (self.project / "main.py").write_text("import runpy, sys\nrunpy.run_path(sys.argv[1])\n")
        (self.project / "premise.py").write_text("print(2)\n")
        (self.project / "expected.txt").write_text("2\n")

    def tearDown(self):
        self.temp.cleanup()

    def record(self, *, claim_id="L1", local_claim="1 + 1 = 2", assumptions=None,
               result_kind="symbolic-identity", inputs=None, command=None):
        return comp.record_artifact(Namespace(
            project=str(self.project), cwd=".", claim_id=claim_id, local_claim=local_claim,
            assumption=assumptions or [], backend="Python", backend_version=sys.version,
            result_kind=result_kind, command_json=json.dumps(command or [str(self.runner), "main.py", "premise.py"]),
            input=inputs if inputs is not None else ["main.py", "premise.py"],
            compare="stdout-exact", expected_output="expected.txt", expected_exit_code=0,
            proof_translation="Supports only the declared local arithmetic claim.", limitation=[]))

    def replay(self, artifact):
        return comp.replay_artifact(Namespace(project=str(self.project), artifact=artifact["artifact_id"], timeout=10))

    def supersede(self, old, new):
        return comp.supersede_artifact(Namespace(project=str(self.project), artifact=old["artifact_id"],
            replacement=new["artifact_id"], reason="Replay the same local claim after refreshing its inputs."))

    def test_omitted_secondary_command_script_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "command file dependencies"):
            self.record(inputs=["main.py"])

    def test_equals_option_file_dependency_is_recorded(self):
        with self.assertRaisesRegex(ValueError, "premise.py"):
            self.record(inputs=["main.py"], command=[str(self.runner), "main.py", "--source=premise.py"])

    def test_declared_secondary_input_change_invalidates_a_pass(self):
        artifact = self.record()
        self.assertEqual(self.replay(artifact)["status"], "passed")
        (self.project / "premise.py").write_text("print(3)\n")
        audit = comp.audit_artifact(self.project, artifact["artifact_id"])
        self.assertFalse(audit["valid"])
        self.assertTrue(audit["claim_scope_sha256"])
        self.assertTrue(any("premise.py" in issue for issue in audit["errors"]))

    def test_legacy_omitted_input_is_rejected_by_current_audit(self):
        # Emulate only the former admission rule when producing the old record.
        with patch.object(comp, "validate_command_inputs", return_value=None):
            artifact = self.record(inputs=["main.py"])
            self.assertEqual(self.replay(artifact)["status"], "passed")
        audit = comp.audit_artifact(self.project, artifact["artifact_id"])
        self.assertFalse(audit["valid"])
        self.assertTrue(any("command file dependencies" in issue for issue in audit["errors"]))

    def test_stale_artifact_can_be_replaced_with_the_same_scope(self):
        old = self.record()
        self.replay(old)
        (self.project / "premise.py").write_text("print(1 + 1)\n")
        self.assertFalse(comp.audit_artifact(self.project, old["artifact_id"])["valid"])
        new = self.record()
        self.assertEqual(self.replay(new)["status"], "passed")
        result = self.supersede(old, new)
        self.assertEqual(result["replacement_artifact_id"], new["artifact_id"])
        self.assertTrue(result["claim_scope_sha256"])

    def test_different_claim_assumption_or_evidence_cannot_cover_the_old_claim(self):
        old = self.record()
        self.replay(old)
        for change in ({"claim_id": "L2"}, {"local_claim": "2 * 1 = 2"},
                       {"assumptions": ["An additional restriction holds."]}, {"result_kind": "numerical-evidence"}):
            with self.subTest(change=change):
                new = self.record(**change)
                self.assertEqual(self.replay(new)["status"], "passed")
                with self.assertRaisesRegex(ValueError, "same recorded local claim"):
                    self.supersede(old, new)

    def test_damaged_spec_has_no_trusted_scope_for_replacement(self):
        old = self.record()
        self.replay(old)
        path, payload = comp.load_artifact(self.project, old["artifact_id"])
        payload["local_claim"] = "An unrelated assertion."
        runtime.atomic_write_json(path, payload)
        self.assertIsNone(comp.audit_artifact(self.project, old["artifact_id"])["claim_scope_sha256"])
        new = self.record()
        self.replay(new)
        with self.assertRaisesRegex(ValueError, "same recorded local claim"):
            self.supersede(old, new)


if __name__ == "__main__":
    unittest.main(verbosity=2)
