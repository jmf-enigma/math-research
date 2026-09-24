# Changing representation

Read when a reduction, lifting, quotient, encoding, or recursive construction has a nontrivial return to the original theorem. State source and target domains, the concrete map, and the implication actually needed. Do not require a bijection when a one-sided bound suffices.

## Prove the transport

| Move | Obligation |
| --- | --- |
| Equivalent optimization | Feasible objects map in both directions with the claimed objective relation; preserve emptiness, unboundedness, or attainment when relevant |
| Relaxation | Prove the inclusion and bound in the needed direction; recovery is required for an attainable policy or exactness claim |
| Quotient/symmetry | Prove the equivalence relation respects operations and the target property; preserve multiplicities for counting and lift solutions as needed |
| Change of variables | Characterize the image and recovery there; track excluded or singular boundary points |
| Algebraic/formal encoding | Give symbol meanings, domain/order conditions, and permitted denominators; show the encoded conclusion implies the source conclusion |
| Recursive construction | Prove the base, legal composition, preserved invariant, and resource recurrence; exclude the original forbidden configuration |

For example, represent `x in [-1,1]` by `u,v >= 0`, `u+v <= 1`, `x=u-v`. Every source point lifts via its positive/negative parts, and every target pair recovers an admissible `x`. Thus minimizing `cx` is equivalent to minimizing `c(u-v)` even though the lift is not unique. Dropping `u+v <= 1` changes the represented domain; agreement on sampled objectives does not repair that error.

## Use a failed transport to find the object

Retain a smallest admissible failure. Identify the operation that breaks the needed property: composition, conditioning, projection, maximization, or a limit. Derive the exact residual or missing closure condition.

Try an invariant, coordinate, potential term, or boundary condition that addresses that residual. Prove both preservation and its implication for the parent claim. A stronger induction invariant helps only if its base and step are provable; an added theorem-strength assumption is a repaired statement.

In DP, terminal-reward monotonicity does not establish that Bellman updates preserve action-difference order. In mechanism design, local incentive inequalities need a valid path to all deviations. Keep the closure obligation specific enough to prove or refute. Small symbolic examples can expose it; numerical tests are optional.

## Localize a counterexample

- **Original theorem:** verify every original assumption and failure of its conclusion.
- **Child lemma/invariant:** reject that implication; retain independent parent results.
- **Encoding:** identify the lost semantic condition and correct the translation.
- **Proxy evaluator:** limit the conclusion to what the proxy measures.

When resuming work requires a durable witness, save source/target statements, map, discharged obligations, remaining gap, and exact replay if applicable. Existing computation or formalization artifacts can hold it; no separate form is required.
