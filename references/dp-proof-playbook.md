# Dynamic programming proofs

Use for Bellman equations, value structure, policy verification, thresholds, indexability, and average-cost control. Fix state, admissible actions, transition law, reward/cost convention, horizon or discount, and the class of comparison policies. State terminal/boundary conditions and how ties affect the policy claim.

## Choose the object that implies the target

| Target | Kernel | Required closure |
| --- | --- | --- |
| Finite-horizon value or policy structure | Backward induction on a function class | Terminal value belongs to the class; the Bellman operator preserves it; action comparisons imply the policy claim |
| Discounted fixed point | Contraction on a specified complete function space | Bellman operator maps that space into itself; admissible maximizing selections exist when claiming a policy |
| Monotone/threshold policy | Order or single crossing of action-value differences | Prove the property after expectation and continuation; account for state-dependent feasible actions and ties |
| Convex/concave/submodular value | Bellman operator preserves the claimed property | Verify expectation, composition, and optimization each preserve it; maximization need not preserve concavity |
| Average-cost optimality | Gain/bias inequality and equality under the candidate | Integrability and a terminal-bias bound justify passage from finite horizons to the specified average-reward criterion |
| Indexability | Passive optimal-action sets ordered by subsidy | Prove nesting over the full subsidy range, with endpoint limits and a consistent tie convention |
| Constrained control | Lagrangian bound attained by a feasible policy | Complementary slackness and feasibility close the primal bound; randomization may be needed |
| Belief-state control | A sufficient posterior state and a valid filter | Histories induce the stated belief transitions and admissible policies transport between representations |

Do not solve the entire value function if the claim needs only an action comparison or Bellman bound. Order preservation in the function argument does not by itself prove monotonicity in the state. For Topkis, identify the lattice/order, increasing differences, and feasible-set conditions of the exact theorem used; monotone rewards alone are insufficient.

## Bounded discounted certificate

For reward maximization in a well-defined MDP, suppose `0 <= beta < 1`, rewards and `V` are bounded measurable, and `pi` is an admissible measurable stationary policy. Verify at every state:

```text
V(s) >= r(s,a) + beta E[V(S') | s,a]  for every a in A(s),
V(s)  = r(s,pi(s)) + beta E[V(S') | s,pi(s)].
```

Iterate along any admissible policy for a finite horizon. Boundedness gives `beta^T E[V(S_T)] -> 0`, proving an upper bound on every policy's discounted reward and equality for `pi`.

For unbounded rewards or `V`, prove integrability of the finite-horizon identities, justify convergence to the specified return, and control the terminal term for both candidate and comparison policies. Vanishing discounted terminal value for every compared policy is sufficient for this argument; a weaker one-sided condition needs a corresponding verification proof.

For average reward, replace `V` by bias `h` and discounting by
`g + h(s) >= r(s,a) + E[h(S') | s,a]`, with equality on-policy. The relevant terminal term is `E[h(S_T)]/T`. Recurrence alone does not establish its required bound.

## Structural proof failures

- A binary-action threshold needs single crossing of `Delta(s)=Q(s,1)-Q(s,0)` and boundary signs for any claimed interior crossing. With more actions, adjacent comparisons must assemble into the claimed ordering.
- A finite-horizon threshold may depend on time; it does not establish a stationary threshold or indexability.
- If contraction fails, first identify the lost hypothesis. Weighted norms, monotone convergence, and span seminorms each need their own assumptions.
- Test disputed closure on two states, two actions, and two periods; include boundaries, action ties, and nonmonotone transitions. Finite enumeration can refute a universal claim but cannot certify its continuous-state extension.

For finite MDPs, occupation-measure LPs can expose Bellman certificates; reachability and recurrent-class calculations can expose missing policy conditions.
