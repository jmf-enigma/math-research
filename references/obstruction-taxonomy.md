# Obstruction Taxonomy

Name the exact failed implication, then choose one diagnosis. Labels route the next move; they are not extra reporting requirements.

## Common Obstructions

| Symptom | Diagnosis | Decisive next check |
| --- | --- | --- |
| An admissible example violates the conclusion | False target | Check every original assumption; distinguish original, child, and encoding scope. |
| A proof step needs unstated regularity | Missing premise | Is the premise derivable, obtainable from another route, or an explicit theorem repair? |
| Pointwise/expected/asymptotic evidence is used for uniform/high-probability/finite claims | Quantifier mismatch | Write both quantified statements and the missing upgrade. |
| Derivatives ignore corners, ties, zero denominators, or nonunique optima | Boundary failure | Check the neglected case with KKT, subgradients, or the original inequality. |
| Pointwise argmax is treated as a measurable policy | Selection gap | Verify a measurable-selection theorem's hypotheses or prove an admissible approximation. |
| Adaptive data is treated as independent | Dependence gap | Define the filtration and conditional statement before applying concentration. |
| Local optimality is used as global optimality | Nonconvexity gap | Establish a global certificate or find a competing feasible point. |
| Weak/set-valued behavior is promoted to strict/unique/exact | Overstrong conclusion | Test equality, ties, and perturbations. |
| Correct one-step bound does not sum | Accumulation gap | Identify the shared budget, telescope, or summation lemma actually needed. |
| Lower-bound instances are distinguishable or infeasible | Construction failure | Compute feasibility, separation, and KL/TV on the smallest instance pair. |
| Sampled coefficients, active sets, or potentials fail elsewhere | Overfit construction | Use a withheld case to expose the missing condition; change the normal form. |
| Algebra hides signs, cancellation, or equality | Representation obstruction | Try the gap, residual, dual, or invariant suggested by the failure. For a complete long proof, use [structural compression](structural-proof-compression.md). |
| New notation leaves the same missing implication | Unchanged proof state | Compare goal, assumptions, object, and failure witness; require a new ingredient before retrying. |
| A proposed action cannot change any claim or route | No decision value | Replace it with a falsifier, premise retrieval, certificate, or exact obstruction report. |

## Failure Stage Router

| Stage | What failed | Repair location |
| --- | --- | --- |
| `strategy-discovery` | No central object or viable route | One informative special/tight case or bottom-up lemma. |
| `decomposition` | Child is cyclic, equally hard, or insufficient | Conditional parent assembly and child statements. |
| `premise-retrieval` | Needed theorem bundle is unavailable | Exact hypothesis-matched subqueries. |
| `local-proof` | A deduction fails within a viable route | First invalid inference and its dependents. |
| `assembly` | Children do not establish the parent | Missing bridge or unhandled case. |
| `fidelity` | Checked statement differs from intended claim | Statement/definition mapping before further search. |
| `library-coverage` | Formal prerequisites are absent | Missing definitions/theory, or an explicitly informal proof; no placeholder axioms. |

## Stuck Protocol

Write the smallest instance or lemma where the obstruction persists. Try its negation when that can distinguish a false claim from a difficult proof. Preserve the witness and surviving dependencies, then follow [escalation routing](proof-escalation-protocol.md#escalation-ladder). A false child does not by itself refute its parent.

## Red Flags

Inspect the obligation behind phrases such as “standard arguments”: differentiating an argmax, exchanging limit and expectation, deriving monotone policies from monotone primitives, treating random stopping as deterministic, or extending finite-support proofs to continuous domains. The issue is the missing condition or bridge, not the phrase itself.
