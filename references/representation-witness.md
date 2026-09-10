# Changing representation with a checkable witness

Read only when a proof uses a reduction, lifting, quotient, encoding, certificate, or recursive construction whose return to the original theorem is nontrivial. This is one local mathematical obligation, not another project-wide form.

## State the implication that is needed

Write the old objects, new objects, admissible domains, concrete map, and recovery implication. Use only the obligations the theorem needs:

| Claimed move | Required justification |
| --- | --- |
| Equivalent optimization problem | Forward and backward feasibility and preservation of objective order; handle empty feasible sets, unboundedness, and attainment if relevant |
| Relaxation giving a bound | The needed inclusion and objective inequality; recovery is required only if claiming an attainable policy or exact optimum |
| Quotient or symmetry reduction | A proved invariant equivalence relation, well-defined operations, and transport back; preserve multiplicities for counting |
| Change of variables | Image and domain, inverse or recovery on that image, and excluded boundary points |
| Formal or algebraic encoding | Meaning of each symbol, nondegeneracy and order conditions, permitted denominators, and how a checked encoded statement implies the source statement |
| Recursive construction | Base case, legal composition, invariant preservation, resource recurrence, and the original forbidden configuration or target property |

The map need not be a bijection. For example, lift x in [-1,1] to u,v ≥ 0 with u+v ≤ 1 and x=u−v. A forward choice is u=max(x,0), v=max(−x,0); any feasible pair recovers an admissible x, since |u−v| ≤ u+v ≤ 1. Thus minimizing cx is equivalent to minimizing c(u−v). Multiple pairs may represent the same x; requiring uniqueness would add an unnecessary obligation.

Conversely, dropping u+v ≤ 1 changes the represented domain. Matching the optimum for one sampled value of c would not establish equivalence. Use such witnesses to test the exact missing condition, then prove the quantified mapping.

## Let failure identify a new object

If the construction fails, retain a smallest admissible failure and ask which operation breaks the needed property: composition, conditioning, projection, maximization, taking limits, or transport. Derive the residual or missing closure condition exactly when possible.

Try one additional invariant, coordinate, potential term, witness map, or boundary condition that addresses that failure. Explain why it is preserved and why it closes the parent. A stronger invariant can make induction easier; it is useful only if the base case and induction step can both be proved. Adding a theorem-strength hypothesis is theorem repair, not discovery of a proof.

For a dynamic program, the corresponding question may be whether the Bellman operator preserves the claimed order of action differences. Monotonicity of a terminal reward alone does not settle that closure property. For a mechanism, local incentive inequalities need a valid route to all deviations. Keep the mathematical kernel specific to the model.

Use examples to falsify or formulate a candidate. If the user requests symbolic reasoning, derive small cases and residuals symbolically; simulations are optional diagnostics. A surviving test creates an obligation, not a proof.

## Interpret counterexamples at the correct level

Record what was actually refuted:

- Original theorem: replay all original assumptions and the failure of its conclusion.
- Child lemma or proposed invariant: retire that implication; keep independent parent components.
- Encoding: expose the missing semantic condition, correct the translation, and compare it again to the frozen source.
- Sampled/proxy evaluator: record the evaluator's scope; do not infer a theorem-level verdict.

For a durable project, attach a short artifact containing the source/target statements, map, obligations discharged, remaining gap, and exact replay if applicable. Existing computation and Lean bridges can carry this artifact. No dedicated verification service is implied.
