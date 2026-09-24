# Proof Escalation Protocol

Use when the current route fails. Choose the next action from the failed obligation, not from a fixed sequence of tools.

## Trigger

Escalate immediately after a counterexample, unsupported assumption, or statement mismatch. After two attempts leave the same obstruction unchanged, stop extending the prose. A retry needs a new premise, object, representation, certificate, or justified theorem repair; a new label, parameter fit, or solver tolerance is insufficient.

Compare the tuple `(goal, assumptions, central object, failure witness)`. Earlier unsuccessful work on the same theorem counts when that tuple still matches.

## Escalation Ladder

These are alternative actions. Take the smallest one that can change the proof state.

| First failed obligation | Next action | Required return |
| --- | --- | --- |
| No useful central object | Probe a smallest/tight case or use one [discovery lens](proof-idea-generator.md). | Candidate kernel and a decisive check. |
| Child is theorem-strength, circular, or unused | Write conditional parent assembly; replace or drop the child. | Strictly smaller children that suffice for the parent. |
| Missing known premise | Search exact statement and hypotheses; read the source. | Applicable theorem or explicit mismatch. |
| Algebra, sign, feasibility, or finite construction | State the negation and use a narrow [tool query](tool-assisted-proof-patterns.md). | Counterexample, exact identity, condition set, or certificate. |
| Stable fragile formal lemma | Use the [Lean bridge](lean-formalization-bridge.md). | Frozen-target result with its checked scope. |
| Nonroutine idea-level kernel survives local methods | Use [bounded consultation](expert-consultation.md). | One new mechanism or decisive refutation to reconstruct independently. |
| Local deduction or omitted boundary | Repair once without changing the central mechanism. | Corrected inference and rechecked dependent assembly. |
| Valid children do not imply the parent | Expose the missing bridge in conditional assembly. | Bridge proof, revised decomposition, or conditional result. |
| Missing/stale artifact or process failure | Restore the named replay or pending check. | Current evidence; no mathematical failure is invented. |
| Witness violates the original conclusion under every original assumption | Record the original theorem as refuted. | [Saved witness and checking basis](verification-gate.md#recording-a-refutation). |
| Witness refutes only a child or encoding | Drop/repair that child or correct the encoding. | Revised route preserving independent parent components. |

A needed extra premise is evidence that this route is conditional, not automatically that the original claim is false. Explore the weakest useful repair while preserving the original status. Ask for steering only when choosing a repair would change the user's intended model or research objective beyond the existing authorization.

Before stopping, inspect whether an underexplored family has one cheap decisive probe. Run it only when its expected result can alter the conclusion; unexplored possibilities do not require exhausting all families.

## Domain Escalations

Use the relevant [domain playbook](proof-router.md) for the failed mathematical condition. Typical first probes are a Q-value sign change for a DP threshold, a finite-type deviation for IC, a confidence-event/summation split for regret, a global-optimality certificate for KKT, or an explicit KL/TV calculation for a lower bound.

## Required Ledger Entry

In durable mode, keep one compact record: exact failed implication and witness; retained valid prefix; new ingredient; next bounded action; result and affected dependencies. Add the repaired statement and its reason if the claim changes. Reuse existing fields rather than creating a second status report. Ordinary one-turn proofs need no ledger.

## Final Answer Rule

If no proof or original-theorem refutation results, report unresolved in this attempt or `lemma-conditional`, with the exact remaining obligation and one justified next action. Mark every unproved key lemma; a polished skeleton does not close it.
