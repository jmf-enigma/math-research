# Verification Gate

Use before presenting a hard proof as complete. Check the mathematics that bears on this claim; do not produce a long checklist or require every available tool.

## Outcome, evidence, and scope

These are separate axes, not a confidence ladder.

| Axis | Examples |
| --- | --- |
| Mathematical outcome | Proof, refutation, partial result, conditional result, known literature answer, unresolved |
| Evidence basis | Written derivation, model referee, human review, exact computation, formal proof |
| Scope | One instance, finite class, local lemma, restricted theorem, full original theorem |
| Fidelity | Exact original statement, faithful encoding, explicitly repaired theorem, unresolved translation |

The executable loop uses `referee-accepted` and an `evidence_summary` with the disposition, scope, candidate and claim identity, and explicit human/formal-check flags. The model referee can reject a candidate or identify a gap; its agreement does not certify the theorem. Independently inspect its decisive reasoning before reporting a proved or refuted original claim.

Legacy labels remain readable: `human-proof` denotes an asserted prose proof, not an automatically recorded human review; `counterexample-tested` means a bounded search found no witness; `tool-checked` and `formalized-local` require a stated scope. `formalized-complete` requires the exact parent statement and all dependencies to pass the formal trust audit. Historical labels alone are insufficient evidence.

## Four core checks

1. **Statement and assumptions.** Match the original variables, domains, quantifiers, definitions, hypotheses, and conclusion. Check the boundaries and ties actually relevant to the proof. Any change is explicit theorem repair.
2. **Decisive reasoning.** Inspect the first nonroutine implication and every dependency it consumes. Cite exact applicable premises or give derivations. Plausibility, a tool's success code, and a referee's confidence do not fill gaps.
3. **Completion-coverage gate.** Assemble the proved components into every required part of the original claim. A correct local lemma, a restricted case, or a merely sufficient condition does not establish a broader theorem.
4. **Adversarial review.** Attempt to break the fragile step using its negation, a boundary case, an independent derivation, or an appropriate checker. If it fails, preserve independently valid work and return the exact obstruction.

## Conditional checks

Load or apply only the row triggered by the proof.

| Trigger | Check |
| --- | --- |
| Changed representation or custom definitions | **Semantic-obligation gate:** verify the concrete maps, domains, feasibility, closure, multiplicity, and recovery direction actually needed. Test basic definition consequences. See [representation witnesses](representation-witness.md). |
| A construction or formula guessed from examples | Reserve a case not used to guess it, then derive a quantified proof or independently checkable certificate. No finite search silently becomes a general theorem. |
| Retrieved theorem | Read the exact source and surrounding definitions; check version, hypotheses, and applicability. Inspect the proof move when transferring it. Novelty checking is separate and only needed when novelty is claimed. |
| CAS, solver, or computation | Replay inputs, assumptions, executable/version, output, and certificate. Identify exact versus floating or sampled scope, and translate back to the theorem. |
| Lean or another formal checker | Freeze the target; audit `sorry`, admissions, unexpected axioms, dependencies, and the intended environment. Check statement fidelity and full parent assembly separately from kernel acceptance. |
| A decomposition spans several lemmas | Require sufficiency, acyclicity, strict simplification, and actual downstream consumption. Repair only affected dependents. |
| Repeated failure or budget interruption | Restore the pending action and first error; distinguish missing evidence, a failed mechanism, and a process error. Re-open mathematical work only with a changed artifact or a justified new route. |
| Reusable library code requested | Review natural definitions, useful generality, namespaces, and a small API. This is a reuse check, not a truth criterion. |

Examples of targeted attacks include necessary versus sufficient KKT conditions, adaptive versus independent data, missing limit-exchange conditions, nonattainment, nonunique optimizers, and unproved preservation under maximization. Select the attack relevant to the argument; do not enumerate them all in every proof.

## Final report

Give the exact result or obstruction, the decisive mechanism, essential assumptions, and the scope of any external check. Name unresolved dependencies and explicit theorem repairs. Show a lemma graph or audit details only when they help the reader assess the result. Do not replace a mathematical proof with workflow records.

## Recording a refutation

For a durable project marked `refuted`, save the counterexample and its assumption/conclusion checks in a project-local file. Record its actual checking or review basis in the current theorem revision, for example:

```json
{
  "event_type": "exact_counterexample",
  "claim_id": "main theorem",
  "status": "refuted",
  "witness": "writeup/counterexample.md",
  "evidence_basis": "Exact analytic derivation and a distinct adversarial self-review."
}
```

Append the saved JSON with `proof_runtime.py append PROJECT counterexamples --record-file RECORD.json`. The runtime records the current witness file hash automatically. The doctor requires an original-theorem record, its checking basis, and an unchanged nonempty witness file before recommending delivery of a refutation. A local-lemma counterexample does not close the original theorem; a `refuted` ledger label alone is insufficient. An older record without a file hash needs checking and recording again. The hash preserves the inspected text; it does not verify the mathematics or create an independent review.
