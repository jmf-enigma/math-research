# Finding structure in an existing proof

Use when the user wants a conceptual replacement for a calculation-heavy, certificate-heavy, or pieced-together proof. For clearer exposition along the same route, use `math-proof-writing`.

A structural improvement replaces work with a mechanism that explains and generates the needed estimates. Preserve the exact theorem and the old proof's evidence status. A rigorous computational proof is valid evidence; the task is to find a simpler route, not to presume one exists.

## Read the old proof backward

Choose a block responsible for much of the complexity. Identify exactly what its consumers need, including constants, equality cases, boundary terms, and terminal values. A proof may construct a whole inverse or bound every term when the theorem needs only one relation. Remove those excess objectives before inventing a new method. Mark gaps in the old proof rather than inheriting its claimed validity.

Determine what the surviving estimates do jointly: pay for one loss, cancel intermediate terms, exclude an improving move, or preserve a relation. Form the residual before bounding its pieces. Separate estimates can discard a shared constraint—for example, several losses may each vanish in some feasible state but never vanish together.

Treat coefficients and partitions as clues. Ask which binding conditions, symmetries, cancellations, or recurrence determine them. The replacement need not explain accidental detail that downstream steps never use.

## Choose one explanation to test

| Observed complexity | Candidate mechanism | Obligation that decides it |
| --- | --- | --- |
| Compensating losses and reserves | Joint quadratic budget, convexity inequality, or dual certificate | Derive the shared constraint and exact residual |
| Repeated sums and endpoint corrections | Potential or telescoping identity | Prove the step and endpoints using a small set of current quantities |
| Case splits with matching formulas | Symmetry, order, or admissible transformation | Prove coverage and transport; retain genuine changes of active constraint |
| Long histories with repeated dependence on few quantities | Sufficient state, invariant, or local basis | Prove update closure and objective recovery for every admissible history |
| Large tables or explicit constructions | Generating rule, orbit, exchange, or recursion | Prove legality, closure, and the property for the whole family |

State the replacement kernel and the old obligations it removes. Check that assuming this kernel actually closes its consumers. If the mechanism is still missing, use [structural discovery](proof-idea-generator.md).

Use computation where rival explanations predict different outcomes: residuals, active constraints, partial sums, equality configurations, or changed boundaries. For a numerical matrix certificate, inspect its range and meaningful basis vectors before fitting every entry. Numerical rank and fitted recurrences suggest an object; they do not prove it.

Derive the object from its requirements. Cancellation or complementary slackness should determine weights; a seed fit alone should not. Test a held-out case and seek a new prediction: an equality family, boundary correction, or identity at arbitrary size.

## Prove the replacement, then subtract the old machinery

Prove the general kernel and its implication for the original theorem without invoking the block being replaced. Preserve parameter ranges and exceptional cases. Then remove the old block and trace every dependency: does the proof still close, and has the total work decreased after counting new definitions and side conditions?

A uniform identity replacing many cases or a recurrence determining all coefficients is a concrete gain. Renaming the old sum, hiding the computation in an appendix, or assuming an equally hard lemma is not. An exact finite certificate may remain a valid leaf; identify it rather than claiming its elimination.

Deliver the mechanism, replacement proof, removed obligations, and surviving dependencies or computation. State local scope for a local replacement. If the kernel remains unproved, preserve the valid old argument and report that exact gap.

In the executable loop, put the theorem in `claim.md`, the simplification goal in the acceptance contract, and the old proof in `--reference`. Referee theorem correctness and the requested simplification separately. An unmet simplification calls for a new route; request external evidence only for an actually missing premise or artifact. Short direct tasks need no extra project structure.

## Worked example: a shared constraint explains the bound

Suppose a case analysis proves, for real vectors a, c, x with a nonzero and b positive,

    a · (x − c) ≥ b  implies  ||x − c||² ≥ b² / ||a||².

When a has at least two nonzero coordinates, every coordinate loss can vanish in some feasible vector, but all cannot vanish together. Coordinatewise minima miss the bound. Write y = x − c. The constraint controls only the component along a; the orthogonal component adds cost without helping feasibility. Thus decompose

    y = ((a · y) / ||a||²) a + z,   a · z = 0,
    ||y||² = (a · y)² / ||a||² + ||z||² ≥ b² / ||a||².

Equality requires z = 0 and a · y = b, giving x = c + (b / ||a||²)a. The projection explains the constant, equality case, and dimension-free proof. Positive-definite weighted loss admits the analogous change of coordinates; singular weights require separate treatment.

This illustrates a joint constraint, not a discovery result or a universal recipe for combining losses.

## Research basis and scope

Source check: 2026-09-24. The retrospective workflow adapts these mechanisms and ordinary proof analysis; adding it does not establish improved research solve rates.

- [Yoon et al. (2026), v1, §§3.1–3.4 and §4.1.1](https://arxiv.org/html/2606.26077v1): convert eligible PEP certificates through partial sums, low-rank structure, local bases, and symbolic coefficients into Lyapunov proofs. Basis search is heuristic; numerical patterns still require general analytic identities. Use the [Peppy bridge](peppy-proof-bridge.md) for applicability.
- [Davies et al. (2021), topology and representation-theory sections](https://www.nature.com/articles/s41586-021-04086-x): learned relationships guide humans toward objects and decompositions, followed by separate mathematical work. Feature importance is a clue; the paper distinguishes proved results from conjectures.
- [Romera-Paredes et al. (2024; online 2023), cap sets and admissible sets](https://www.nature.com/articles/s41586-023-06924-6): inspecting generators exposes rules and symmetries beyond output tables. Construction validity, optimality, and general proof remain separate tasks.
