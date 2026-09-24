# Finding structure in an existing proof

Use when the user wants a conceptual replacement for a calculation-heavy, certificate-heavy, or pieced-together proof. Changing the mathematical route is a research task even if a valid proof already exists. For exposition along the same route, use `math-proof-writing`.

The aim is a small mechanism that generates the needed estimates and explains their form. Preserve the exact theorem and the old proof's actual evidence status. Do not assume every theorem admits a short proof, or treat a rigorous computational proof as defective merely because it uses computation.

## Read the old proof backward

Choose one block responsible for much of the complexity. Identify its inputs, exact output, and downstream uses, including constants, equality cases, boundary terms, and terminal values. If the old argument has a gap, label it; a proposed simplification cannot inherit its claimed validity.

Ask what the block's estimates accomplish together: pay for one loss, cancel intermediate terms, prevent an improving move, or preserve a relation under an operation. Derive the residual before bounding its pieces separately. Shared variables may prevent several losses from being small simultaneously; bounding each on its own can destroy the very structure being sought.

Treat old coefficients and partitions as evidence, not constraints on the replacement. Explain them through binding conditions, symmetry, cancellation, or a recurrence when possible. Do not build a grand abstraction around every accidental feature of the old calculation.

## Choose one explanation to test

| What the old proof shows | Candidate mechanism | Decisive obligation |
| --- | --- | --- |
| Many compensating losses and reserves | One joint quadratic budget, convexity inequality, or dual certificate | Derive their shared constraint and the exact residual; preserve correlations |
| Repeated sums with endpoint corrections | A potential or telescoping identity | Express it in a few current mathematical quantities and prove the step plus both endpoints |
| Repeated case splits with matching formulas | Symmetry, an order relation, or one admissible transformation | Prove domain coverage and transport; a genuine change of active constraint may require separate cases |
| Long histories but repeated dependence on few quantities | A sufficient state, invariant, or low-dimensional basis | Prove the update closes and recovers the original objective for every admissible history |
| Explicit constructions or large tables | A generating rule, orbit, exchange, or recursive composition | Prove legality, closure, and the claimed property for the whole family |

These are alternatives. State one exact kernel and which old obligations it would remove. Check the conditional assembly before spending effort on the kernel. Reuse the [discovery lenses](proof-idea-generator.md) only if the candidate mechanism is still missing.

Use computation to distinguish explanations. Inspect a residual, active constraints, partial sums, or equality configurations; vary the size, boundary, or grouping where competing explanations differ. Preserve a holdout. For a numerical matrix certificate, inspect its range and seek meaningful basis vectors rather than interpolating every matrix entry. Numerical rank, attribution scores, and fitted recurrences suggest objects; they do not establish them.

Then derive the object from its defining requirements. For example, determine weights by cancellation or complementary slackness, rather than choosing coefficients solely because a fit looks good. A useful candidate predicts something beyond its seed calculation: an equality family, a boundary correction, or an identity at arbitrary size.

## Prove the replacement, then subtract the old machinery

Write the new argument without using the block it is meant to replace. Prove the general kernel, its admissibility, and its implication for the original theorem. Keep all parameter ranges and exceptional cases. An exact finite certificate can remain a legitimate leaf; identify it if it has not been eliminated.

Finally remove the old block mentally and follow every dependent step. Has the replacement really reduced the work? Useful gains include one uniform identity replacing many cases, coefficients derived by a single recurrence, or fewer independent inequalities with the same sharp constant. A new name for the old sum, an equally hard unproved lemma, or moving calculations into an appendix does not alone establish structural simplification. Count the cost of new definitions and side conditions too.

Deliver the mechanism, a complete replacement proof, what old work it removes, and any surviving computation or inherited dependencies. For a local replacement, state the local scope. If the kernel fails, preserve the valid old argument and report the precise unproved relation; do not advertise a simplified full proof. Stop when a proposed abstraction merely restates the target or repeated attempts retain the same obstruction.

In the executable loop, put the mathematical theorem in `claim.md`, the simplification goal in the acceptance contract, and supply the old proof through `--reference`. A theorem can be correct while the requested simplification remains unmet; have the referee assess both separately. An unmet simplification calls for a new route, not external evidence unless an actual premise or artifact is missing. No extra project structure is needed for a short direct task.

## Worked example: a shared constraint explains the bound

Suppose a long case analysis proves, for real vectors a, c, x with a nonzero and b positive,

    a · (x − c) ≥ b  implies  ||x − c||² ≥ b² / ||a||².

When a has at least two nonzero coordinates, each coordinate loss can vanish in some feasible vector, although all cannot vanish together. Separate coordinate minima then miss the bound. For every nonzero a, write y = x − c and derive the cheapest feasible displacement: at equality it must point along a. This suggests the projection identity

    y = ((a · y) / ||a||²) a + z,   a · z = 0,
    ||y||² = (a · y)² / ||a||² + ||z||² ≥ b² / ||a||².

This proves the claim in every dimension. Equality requires z = 0 and a · y = b, hence x = c + (b / ||a||²)a. The same object explains the constant, equality case, and all coordinate cases. A weighted positive-definite quadratic loss has the analogous geometry after a valid change of coordinates; singular weights require separate treatment.

This elementary example illustrates how to read compensating terms jointly. It is not evidence of discovery on a new research problem, and it does not imply that every collection of losses has such a constraint.

## Research basis and scope

Source check: 2026-09-24. These papers motivate selective moves, not a universal conversion algorithm.

- [Yoon et al. (2026), v1, §§3.1–3.4 and §4.1.1](https://arxiv.org/html/2606.26077v1): convert PEP inequality certificates through partial sums, low-rank structure, meaningful local bases, and symbolic coefficients into Lyapunov proofs. Finite numerical patterns still need analytic formulas and general identities. Basis search is heuristic; applicability is restricted to the paper's settings. Use the [Peppy bridge](peppy-proof-bridge.md) for eligible algorithmic bounds; do not impose a potential on unrelated proofs.
- [Davies et al. (2021), topology and representation-theory sections](https://www.nature.com/articles/s41586-021-04086-x): learned feature relationships guide humans toward mathematical objects and decompositions, followed by separate mathematical work. Feature importance is a clue, not a proof; the paper distinguishes proved results from remaining conjectures.
- [Romera-Paredes et al. (2024; online 2023), cap sets and admissible sets](https://www.nature.com/articles/s41586-023-06924-6): inspect the programs generating constructions to uncover explicit rules and symmetries. This supports studying generators rather than only output tables. Construction validity, optimality, and a general conceptual proof remain distinct tasks.

The general retrospective workflow above is an adaptation of these mechanisms and ordinary proof analysis. No claim of improved research solve rate follows from adding it to the skill.
