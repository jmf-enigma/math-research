# Mechanism design

Use for implementability, IC/IR, payment formulas, revenue, and approximation mechanisms. Fix valuation form, type domain, available reports, randomization, transfers, and ex-post versus interim constraints. DSIC and BIC quantify over different information and deviations.

## Implementability kernels

- **Single-parameter DSIC.** With interval types and quasilinear utility `t*x-p`, prove allocation monotonicity for each fixed profile of other reports. Integrating allocation gives utility up to a boundary constant; recover payments and check IR and payment constraints. A payment formula alone does not repair a nonmonotone allocation.
- **Single-parameter BIC.** Under the appropriate interim model, derive monotonicity and the envelope formula for interim allocation/utility. Independence of types supports the usual fixed distribution over others; correlated types need an argument accounting for the type-dependent conditional law.
- **Multidimensional quasilinear types.** For utility `t·x-p`, implementability requires cyclic monotonicity, equivalently an appropriate convex potential with allocation as a subgradient. State the domain and extension used. Pairwise monotonicity is not generally sufficient; test cycles of length three or more.
- **Revenue equivalence.** Equal allocations yield equal envelope derivatives only under the relevant implementability hypotheses. Fix boundary utility to determine the payment level; equal allocation alone leaves an additive constant.

For finite types, write every deviation as a payment difference inequality and check the resulting graph for inconsistent cycles, with the edge/sign convention stated. This can falsify a proposed allocation before deriving a payment formula.

## Optimality and repair

A virtual-surplus argument needs the distributional/integration assumptions, boundary terms, feasible allocation set, and implementability conditions. Irregular virtual values require a justified ironing argument and compatible allocation/tie rules. An algorithmic approximation guarantee does not imply truthfulness.

Budget caps, payment signs, and ex-post IR add constraints beyond an envelope identity. Check boundary types and randomized outcomes at the level the theorem requires. If monotonicity fails, changing the allocation, introducing randomization, or weakening IC changes the proposed mechanism or theorem; carry that change explicitly.
