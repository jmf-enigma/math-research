# Verification Gate

Use before delivering a hard proof or refutation. Inspect the obligations the argument actually creates; do not turn this reference into a visible checklist.

## Outcome, evidence, and scope

Report these separately:

| Axis | Question |
| --- | --- |
| Outcome | Proof, refutation, conditional result, or unresolved? |
| Basis | Written derivation, model referee, human review, exact computation, or formal checking? |
| Scope | Instance, finite class, local lemma, restricted theorem, or original theorem? |
| Fidelity | Original statement, justified encoding, explicit repair, or unresolved translation? |

`referee-accepted` records a model verdict, not certification. Inspect its decisive reasoning. The executable loop's `evidence_summary` binds the disposition and scope to the claim and candidate and records human/formal-check flags separately.

Legacy labels are not evidence: `human-proof` means an asserted prose proof, not a recorded human review; `counterexample-tested` means no witness was found in a bounded search. `tool-checked` and `formalized-local` apply only to their checked target. `formalized-complete` requires the original parent statement, its dependencies, and the formal trust audit.

## Four core checks

1. **Statement fidelity.** Match variables, domains, quantifiers, definitions, assumptions, and conclusion. A changed premise or conclusion is theorem repair, even if the replacement is easier to prove.
2. **Decisive implication.** Inspect the first nonroutine step and the dependencies it consumes. Give the derivation or the exact applicable theorem; agreement, successful execution, and plausible notation cannot supply it.
3. **Completion-coverage gate.** Assemble the components into every part of the original claim. Check relevant boundaries, ties, existence, and limiting arguments. A sufficient local condition proves the theorem only after that condition is established.
4. **Adversarial check.** Attack the fragile step using its negation, a boundary case, an independent derivation, or a suitable checker. On failure, retain only results whose dependencies survive.

## Conditional checks

| Trigger | Required evidence |
| --- | --- |
| New representation or custom definition | **Semantic-obligation gate:** concrete maps, admissible domains, and the feasibility, closure, multiplicity, or recovery properties used by the proof. See [representation witnesses](representation-witness.md). |
| Formula or construction inferred from examples | A case not used to infer it, followed by a quantified derivation or independently checkable certificate. The extra case tests the guess; it does not prove generality. |
| Retrieved theorem | Exact source statement, surrounding definitions, version, and hypothesis match. Read the proof move if transferring the method. Frontier/novelty classification is a separate task. |
| CAS, solver, or computation | Inputs and assumptions, current replay, exact versus floating/sampled scope, and the step connecting the output to the theorem. See [computation replay](tool-assisted-proof-patterns.md#replayable-computation). |
| Formal proof | Frozen target, current file/environment replay, admissions and axiom audit, statement fidelity, and parent assembly. See [Lean bridge](lean-formalization-bridge.md). |
| Lemma decomposition | Acyclic dependencies, strictly smaller children, and a parent proof that actually consumes them. Revise only affected dependents. |
| Replacement for a long proof | Complete coverage after removing the replaced argument, with fewer independent obligations. See [structural proof compression](structural-proof-compression.md). |
| Interrupted or stale evidence | Restore the pending check before changing the mathematics. See [runtime recovery](runtime-recovery.md). |
| Reusable formal library requested | Natural definitions, useful generality, namespaces, and a usable API. This is a reuse criterion, not a truth criterion. |

## Final report

Give the exact result or obstruction, decisive mechanism, essential assumptions, and scope of external checks. Identify unproved dependencies and explicit repairs. Include a dependency graph or audit record only when it helps assess the mathematics.

## Recording a refutation

In durable mode, save the witness with its original-assumption and conclusion checks in a nonempty project-local file. Record the actual checking basis under the current theorem revision:

```json
{
  "event_type": "exact_counterexample",
  "claim_id": "main theorem",
  "status": "refuted",
  "witness": "writeup/counterexample.md",
  "evidence_basis": "Exact analytic derivation and a distinct adversarial self-review."
}
```

Use `proof_runtime.py append PROJECT counterexamples --record-file RECORD.json`; the runtime records the witness hash. The doctor requires an original-theorem record, checking basis, and unchanged nonempty witness before recommending delivery. Recheck and rerecord older entries lacking a hash. A child-lemma or encoding counterexample refutes only that target. Hashes preserve inspected text; they do not check mathematics or create an independent review.
