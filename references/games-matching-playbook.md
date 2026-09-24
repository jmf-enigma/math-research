# Games and matching

Use for equilibrium existence or order, price of anarchy, no-regret equilibrium links, and matching stability or incentives. Fix pure versus mixed strategies, the equilibrium concept, and admissible deviations before selecting a kernel.

## Equilibrium kernels

- **Pure Nash by best responses.** For finitely many players, nonempty finite-dimensional compact convex strategy sets, continuous payoffs, and quasi-concavity in own action give nonempty convex best responses and the continuity properties needed for Kakutani. Verify those properties; a set-valued response is not a continuous function. Mixed-strategy existence uses a different strategy space and theorem.
- **Supermodular games.** Specify complete strategy lattices and conditions ensuring extremal best responses exist and are monotone. Tarski applies to the resulting monotone map. Parameter comparative statics needs the additional parameter-order conditions; it does not follow from equilibrium existence.
- **Potential games.** Show each allowed unilateral improvement changes the potential in the required direction. Finite action spaces then rule out improvement cycles; infinite spaces also need an attained extremum or a separate convergence argument.
- **Price of anarchy.** Prove a smoothness or deviation inequality against the stated social benchmark, then sum equilibrium inequalities. Keep cost versus welfare signs and correlated/randomized deviations consistent.
- **No-regret limits.** External regret controls empirical coarse correlated equilibrium violations; internal/swap regret supports correlated equilibrium. Specify empirical distribution, vanishing error, and whether the guarantee is expected or pathwise.

## Matching kernels

For deferred acceptance, track what each rejection implies about the rejecting side's current and future assignments. Use that invariant to exclude a blocking pair in the final matching. State capacities, acceptability, strict preferences or tie rules, and the precise stability notion.

Strategy-proofness is a separate deviation claim. A proposer-side theorem does not imply incentives for the receiving side. Many-to-one, ties, couples, or general choice functions require their own hypotheses; do not import one-to-one strict-preference lattice or rural-hospitals facts unchanged.

Small finite games expose nonconvex best responses and discontinuities. Enumerated matching profiles expose blocking pairs and profitable misreports. These are useful falsifiers before attempting a general fixed-point or rejection-chain argument.
