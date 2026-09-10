#!/usr/bin/env python3
"""Check command dependencies and replacement scope with real Python replays."""
from argparse import Namespace
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
import venv
from unittest.mock import patch

import computation_artifact as comp
import proof_doctor
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

    def test_standard_python_records_and_replays_without_a_wrapper(self):
        artifact = self.record(command=[sys.executable, "main.py", "premise.py"])
        self.assertEqual(self.replay(artifact)["status"], "passed")
        self.assertTrue(comp.audit_artifact(self.project, artifact["artifact_id"])["valid"])
        for options in (["-c", "print(2)"], ["-cprint(2)"], ["-Bcprint(2)"], ["-m", "timeit"]):
            with self.subTest(options=options), self.assertRaisesRegex(ValueError, "inline code"):
                self.record(command=[sys.executable, *options, "main.py"])
        (self.project / "unrecorded.py").write_text("print(2)\n")
        with self.assertRaisesRegex(ValueError, "entrypoint"):
            self.record(command=[sys.executable, "unrecorded.py", "main.py"])

    def test_python_virtual_environment_entrypoint_is_preserved(self):
        environment = self.root / "environment"
        venv.EnvBuilder(with_pip=False, symlinks=True).create(environment)
        interpreter = environment / "bin/python3"
        (self.project / "environment.py").write_text("from pathlib import Path\nimport sys\nprint(Path(sys.prefix).resolve())\n")
        (self.project / "expected.txt").write_text(str(environment.resolve()) + "\n")
        artifact = self.record(command=[str(interpreter), "environment.py"], inputs=["environment.py"])
        self.assertEqual(self.replay(artifact)["status"], "passed")
        self.assertTrue(comp.audit_artifact(self.project, artifact["artifact_id"])["valid"])

    def test_input_mutation_during_replay_is_not_a_pass(self):
        (self.project / "premise.py").write_text(
            "from pathlib import Path\nprint(2)\nPath(__file__).write_text('print(3)\\n')\n")
        artifact = self.record()
        replay = self.replay(artifact)
        self.assertEqual(replay["status"], "input-changed")
        self.assertTrue(any("premise.py" in error for error in replay["input_errors"]))
        self.assertFalse(comp.audit_artifact(self.project, artifact["artifact_id"])["valid"])

    def test_changed_expected_answer_cannot_validate_an_incorrect_output(self):
        for action in ("Path('expected.txt').write_text('3\\n')", "Path('expected.txt').unlink()"):
            with self.subTest(action=action):
                (self.project / "expected.txt").write_text("2\n")
                (self.project / "premise.py").write_text(f"from pathlib import Path\n{action}\nprint(3)\n")
                artifact = self.record()
                replay = self.replay(artifact)
                self.assertEqual(replay["status"], "input-changed")
                self.assertIn("expected output file changed or is missing", replay["input_errors"])

    def test_revised_claim_does_not_receive_the_old_replay_event(self):
        (self.project / "premise.py").write_text(
            "from pathlib import Path\nimport json, sys\n"
            f"sys.path.insert(0, {str(Path(runtime.__file__).parent)!r})\n"
            "import proof_runtime\n"
            "Path('routing.json').write_text(json.dumps({'claim': 'The revised arithmetic assertion holds.'}))\n"
            "proof_runtime.revise_claim(Path.cwd(), 'Fixture theorem revision during computation.')\nprint(2)\n")
        artifact = self.record()
        replay = self.replay(artifact)
        self.assertEqual(replay["status"], "input-changed")
        self.assertEqual(replay["claim_revision"], 0)
        self.assertEqual(runtime.read_state(self.project)["claim_revision"], 1)
        self.assertEqual(list(runtime.iter_channel(self.project, "computations", current_claim_only=True)), [])

    def test_artifact_edits_during_replay_are_preserved_and_rejected(self):
        (self.project / "premise.py").write_text(
            "from pathlib import Path\nimport json\n"
            "path = next(Path('.proof_runtime/computation_artifacts').glob('*/artifact.json'))\n"
            "payload = json.loads(path.read_text())\npayload['local_claim'] = 'An independently edited claim.'\n"
            "path.write_text(json.dumps(payload))\nprint(2)\n")
        artifact = self.record()
        with self.assertRaisesRegex(ValueError, "artifact changed during replay"):
            self.replay(artifact)
        _, payload = comp.load_artifact(self.project, artifact["artifact_id"])
        self.assertEqual(payload["local_claim"], "An independently edited claim.")

    def test_repointed_interpreter_alias_is_detected(self):
        artifact = self.record()
        self.replay(artifact)
        alternate = self.root / "alternate.py"
        alternate.write_text("print(2)\n")
        self.runner.unlink()
        self.runner.symlink_to(alternate)
        self.assertFalse(comp.audit_artifact(self.project, artifact["artifact_id"])["valid"])

    def test_a_history_snapshot_cannot_hide_a_later_replay(self):
        artifact = self.record()
        self.replay(artifact)
        history = comp.ComputationHistory.read(self.project)
        self.assertTrue(comp.audit_artifact(self.project, artifact["artifact_id"], history=history)["valid"])
        original = (self.project / "premise.py").read_text()
        (self.project / "premise.py").write_text("print(3)\n")
        self.assertFalse(comp.audit_artifact(self.project, artifact["artifact_id"], history=history)["valid"])
        (self.project / "premise.py").write_text(original)
        self.replay(artifact)
        with self.assertRaisesRegex(ValueError, "history changed"):
            comp.audit_artifact(self.project, artifact["artifact_id"], history=history)
        self.assertTrue(comp.audit_artifact(self.project, artifact["artifact_id"])["valid"])

    def test_relative_project_path_can_reuse_one_validated_history(self):
        old = self.record()
        self.replay(old)
        (self.project / "premise.py").write_text("print(1 + 1)\n")
        new = self.record()
        self.replay(new)
        self.supersede(old, new)
        previous = Path.cwd()
        try:
            os.chdir(self.root)
            feedback = proof_doctor.runtime_referee_feedback(Path("project"))
        finally:
            os.chdir(previous)
        self.assertEqual(feedback["passed_claim_ids"], ["L1"])
        self.assertFalse(feedback["invalid_computation_artifacts"])
        self.assertTrue(feedback["runtime_integrity_ok"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
