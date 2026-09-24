# Structural Proof Discovery

Use when the central object, construction, or first nonroutine implication is missing. For a complete argument that needs a different mathematical route, use [structural proof compression](structural-proof-compression.md).

An idea is an executable hypothesis: an exact local statement, a reason the target suggests it, and a check that can change the route. Naming a potential, duality, or invariant without specifying its required property is not yet an idea.

## The Compact Pass

Locate the smallest possible failure and the expected tight case. Ask what mathematical object controls both. State the resulting **kernel**, its cheapest decisive check, and the conditional argument from that kernel to the full target. Skip prompts whose answer is already clear.

If the conditional argument still contains the main unknown construction, the kernel has not isolated the difficulty. Choose a lens below according to what is missing; do not expand a generic sketch.

## Structural Lenses

| Obstruction | Move | Required mathematical output |
| --- | --- | --- |
| The claim is intuitive but its failure is vague | Write its negation with minimal objects: reversed pair, profitable deviation, improving move, bad history, distinguishable hard instances | A relation that excludes this failure under the stated assumptions |
| Coefficients or a construction look arbitrary | Start from equality, symmetry, support, boundary, and cancellation conditions | An object derived from these conditions, with a residual that can be signed or eliminated |
| An assumption has no visible job | Translate it into a legal operation: convexity into global sufficiency, Markov structure into recursion, adaptive sampling into a filtration | The precise inference bought by that assumption; a missing condition if the inference fails |
| Algebra obscures the obstruction | Move to a gap, difference, slack, dual, coupling, envelope, or potential | A simpler obligation and a valid implication back to the target; use [representation-witness.md](representation-witness.md) for nontrivial maps |
| The object is hidden | Solve informative small, tight, or degenerate cases | An exact conjecture that predicts a held-out case and suggests a general proof kernel |
| The bridge may already be known | Search the nearest theorem family | A source-checked assumption map and the first step still needing proof; see [external proof pattern scan](external-proof-pattern-scan.md) |

No-small-counterexample results are search signals. Surviving a holdout creates a new proof obligation; it does not discharge one.

## High-Leverage Moves

Use these when a lens identifies the difficulty but leaves the mechanism missing.

### Certificate-first backward design

Write what would certify the conclusion: Bellman inequalities, feasible dual variables, a coupling, flow, deviation potential, or hard-instance separation. Solve backward for a simple object satisfying those conditions. Before investing, verify that certificate validity implies the full target, including endpoints and quantifiers. A certificate condition that restates the original theorem supplies no simplification.

### Local-to-global upgrade

Pair a local fact with its actual globalizer: exchanges that improve every nonglobal solution plus termination, a derivative sign with convexity or single crossing, a one-step inequality with induction, or local incentives with the applicable envelope or no-positive-cycle result. Prove the globalizer's hypotheses. Local optimality alone cannot certify global optimality.

### Abstraction-refinement and bottom-up synthesis

Choose a tractable restriction preserving the feature responsible for the obstruction. Prove or refute it, then restore the omitted feature and identify the first broken implication. Add only the state, invariant, or hypothesis that repairs that implication. Special cases are useful when they suggest this bridge; accumulating solved toy cases without one is not progress on the general claim.

### Equality-driven construction and algebra

Derive an ansatz from binding, symmetry, dimensional, support, and boundary conditions. Determine its unknowns from those requirements. Test a case outside the derivation, then compute the exact residual. Factor, telescope, dualize, or sign-decompose it: the resulting identity should state the real lemma. Reject an interpolating formula with no reason to persist at general size.

### Proof-move migration and trick replay

Extract a source move as required assumptions → transformation → guaranteed output. Re-derive it in the present notation and check where the parent consumes its output. Audit semantic range before substitution: a compound term need not cover its ambient domain. Keep an unverified move local and labeled `candidate`; source checking and a current replay precede proof use. Independent or held-out replay is needed before treating it as a reusable trick.

### Theorem repair

At the first missing implication, identify the extra assumption it needs or the weaker conclusion it supports. Examples include existence instead of uniqueness or monotone selection instead of strict monotonicity. State what remains false, conditional, or unresolved about the original before proving the repaired claim.

## Lemma Admission

Invest only if the lemma has a use site in a conditional proof and makes the parent easier by removing a quantifier, case family, unknown object, or difficult inference. Its motivation must come from the target, assumptions, failure, or tight case. Reject circular, equivalent, unconsumed, or silently stronger children. Durable graph checks are in [strategy scheduler](strategy-scheduler.md#decomposition-admission).

## Stop Rule

Leave discovery as soon as one route has a motivated object, exact kernel, and decisive check. Try that route through to assembly. If attempts preserve the same obstruction, change the representation, retrieve a missing premise, test a falsifiable kernel, repair the statement, or report the gap. More names for the same missing lemma do not create alternatives.
