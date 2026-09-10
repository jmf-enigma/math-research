# Obstruction Taxonomy

Use this when a proof is stuck. Name the obstruction before trying another route.

## Common Obstructions

- False claim: small counterexample exists or theorem contradicts known boundary case. Next move: refute or add assumptions.
- Missing assumption: proof needs compactness, convexity, continuity, boundedness, independence, monotonicity, single crossing, or regularity not stated. Next move: state conditional theorem.
- Wrong theorem family: route proves a related conclusion but not the target. Next move: reclassify with `proof-router.md`.
- Quantifier mismatch: pointwise proof used for uniform claim, expectation proof used for high-probability claim, asymptotic proof used for finite-sample claim. Next move: restate target and choose matching concentration/compactness argument.
- Boundary failure: FOC or derivative argument ignores corner, tie, zero denominator, support endpoint, inactive/active constraint, nonunique optimizer. Next move: KKT/subgradient/case split.
- Measurability/selection gap: existence of pointwise argmax does not give measurable policy/selector. Next move: measurable maximum theorem or finite approximation.
- Dependence gap: adaptive data treated as iid, or filtration not defined. Next move: martingale/self-normalized route.
- Nonconvexity gap: KKT or local optimum used as global optimum. Next move: find convexity/concavity, use global certificate, or search counterexample.
- Too-strong conclusion: uniqueness, strict monotonicity, gap-free bound, or exact optimality claimed where only weak/set-valued/approximate result holds. Next move: weaken conclusion or strengthen assumptions.
- Missing summation lemma: regret proof has correct instantaneous bound but cannot sum. Next move: apply peeling, elliptical potential, harmonic/log sum, or Cauchy-Schwarz.
- Lower-bound construction too easy: instances are too separated or not both feasible. Next move: make instances closer and compute KL explicitly.
- Overfit pattern guess: formula, potential, active set, or construction fits the first toy cases but fails a holdout case or lacks a certificate. Next move: keep the failed guess as evidence, change the normal form, or search for the missing condition.
- Opaque algebra: the route depends on a manipulation with no visible sign, telescope, dual, or equality case. Next move: change representation before continuing: gap form, add-subtract benchmark, conjugate/dual, Bellman residual, envelope term, KL/TV bridge, or potential.
- Low decision value: the next proposed move would not prove/refute a kernel, expose an assumption, retrieve a theorem, or produce a certificate. Next move: choose a higher-value move or stop for theorem repair/user steering.
- Unchanged proof state: a proof move only renames the same subgoal, missing lemma, or algebraic obstacle. Next move: record the failed state, retrieve a premise/paper pattern, tool-check the local claim, or try theorem repair.
- Repeated construction: the same central object, parameterization, invariant, or failure witness has appeared under new notation. Next move: update the attempt fingerprint in `WORKSTREAMS.md`; retry only with a new assumption, invariant, certificate, verified trick, or theorem repair.
- Repeated route without delta: the same theorem family attacks the same missing lemma with no new proof ingredient. Next move: block the retry in `LEDGER.md`, then switch route, retrieve a pattern, tool-check the obstruction, or repair the theorem.

## Failure Stage Router

Classify where the proof failed before choosing a repair:

- `strategy-discovery`: no useful central object or route. Probe one or two special cases or auxiliary lemmas bottom-up, then ask what common invariant they reveal.
- `decomposition`: the sketch exists, but a child is not simpler, is cyclic, or leaves a large repair radius. Review parent sufficiency, strict simplification, acyclicity, and source fidelity before proving children.
- `premise-retrieval`: the route is plausible but the needed theorem set is missing. Decompose the route into subqueries and retrieve a jointly sufficient premise bundle, not isolated similar lemmas.
- `local-proof`: the route and decomposition are sound but one inference fails. Use first-error localization, a verifier/tool artifact, and local repair.
- `assembly`: child lemmas are available but do not imply the exact parent. Write the parent proof conditionally from the children and expose the missing bridge.
- `fidelity`: a proved statement does not match the intended claim or source. Freeze proof search and repair the statement fence.
- `library-coverage`: formalization lacks prerequisite definitions or theory. Inventory the missing foundation; build it explicitly or continue informally without fake axioms or placeholder objects.

## Stuck Protocol

1. Name the obstruction in the ledger.
2. Write the smallest version where the obstruction appears.
3. Check whether this is a repeated route or construction by comparing against `WORKSTREAMS.md`.
4. Classify the failure stage and use its legal repair class.
5. Rank the next move by decision value: kernel proof/refutation, counterexample, certificate, retrieval, representation change, or theorem repair.
6. Try to refute that small version.
7. If true, promote it to a named lemma and prove it separately.
8. If false, identify whether the witness refutes the original theorem, a child lemma, or an encoding. Repair/drop the refuted child or correct the encoding; repair the original theorem only when its own assumptions and conclusion are the issue.

## Red Flags

- "Clearly", "obvious", "by standard arguments" without a named theorem.
- Differentiating an argmax without envelope/regularity conditions.
- Swapping limit and expectation without domination/uniform integrability/concentration.
- Claiming monotone policy from monotone primitives without Topkis/single-crossing conditions.
- Treating a random stopping/adaptive sample size as deterministic.
- Proving only for finite support but stating a continuous-type theorem.
- Renaming the same construction without changing the invariant, certificate, missing assumption, or failure witness.
- Saying "now prove the remaining lemma" when the remaining lemma is identical to the previous failed subgoal.
