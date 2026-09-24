# Novel Problem Discovery

Use when the task asks for an unknown answer, formula, extremal object, or construction. A fixed theorem missing a proof object belongs in [structural discovery](proof-idea-generator.md). If a candidate answer is supplied, prove or refute that fixed candidate through the ordinary loop.

## External Frontier Gate

Before expensive search, distinguish unknown-to-us from apparently open. Execute the source and status checks in [full-text-frontier-evidence.md](full-text-frontier-evidence.md): exact and neighboring results, lawful full text, statement/proof anchors, and the unresolved gap. In durable mode, store the evidence in `literature/frontier-evidence.json` and validate with `frontier_evidence.py`.

Extract something usable from the closest result: a solved restriction, construction, representation, obstruction, or evaluator. A bounded search cannot establish novelty, and recalled results remain unverified until checked. A finite or weakened version is a partial result until the original quantifiers are restored.

## Discovery Contract

Before automated candidate search, settle:

- **Answer-hole contract:** the answer type, admissible encoding, and prohibited self-reference or restatement of the target. Separate witness feasibility from optimality, completeness, uniqueness, or canonicity.
- **Candidate representation:** what search may change, such as a graph, recurrence, basis, potential, dual certificate, or lemma.
- **Evaluator:** what it checks, its finite or sampled scope, soundness/completeness direction, and what a pass or failure implies for the original problem. Calibrate on known-valid and known-invalid examples or solved restrictions.
- **Progress:** the objective or mathematical distinction used after validity passes, plus the criterion for freezing a candidate as a proof target.
- **Search limits:** a task-appropriate budget and a stopping condition tied to unchanged candidates or obstructions.

If no trustworthy evaluator exists, use a falsifier, symbolic residual, finite relaxation, or conditional assembly test with explicit limits. Otherwise stay with bounded conceptual exploration; an unexplained scalar score is not a basis for evolutionary search.

## Frontier Ladder

Choose an understood restriction and the first extension where its mechanism breaks. These may differ by dimension, boundary behavior, dependence, action set, or asymptotic scale. Record the solved case, its proof, and the first obstruction after restoring the omitted feature.

Search should explain or cross that transition. A better score on a distant finite instance matters only if it improves the requested bound, supplies a construction, or exposes a mechanism transferable to the original problem.

## Search Cycle

Seed from solved neighbors, tight cases, failed checked prefixes, and useful baselines. Keep candidates by distinct mechanism as well as score. Alternate structural proposals—new representation, decomposition, basis, or family—with local repairs that preserve validity.

Evaluate in the cheapest informative order: admissibility, known violations, fresh feasibility checks, quality, then held-out cases. The **hard-witness regression set** stores previously violated constraints; descendants must pass it before receiving expensive fresh evaluation. Early rejection saves effort but does not strengthen a passing candidate's evidence scope.

Hold out sizes, boundaries, or parameters capable of distinguishing competing explanations. For formula discovery, derive a law beyond interpolation. For constructions, separate feasibility from improvement and optimality. For finite potential search, passing all tested transitions is not a global drift proof.

Keep the best candidate per genuinely different family and informative failure witnesses. Transfer named compatible components across families only after local checks. If candidates repeatedly fail on the same feature, examine whether the representation excludes the required object before tuning more coefficients. If no candidate, evaluator, or frontier transition changes, reframe or stop.

## Concept And Lemma Invention

Introduce a definition when it performs a mathematical job: closing a recurrence, exposing an invariant, converting a global constraint into a local one, or explaining structure shared across cases. Count the cost of its side conditions. A name for a long expression is useful notation, but is not by itself a new method.

A failed search may yield a proved intermediate theorem. Preserve it when it supports a live route; consider durable reuse only if it is general, useful beyond that attempt, costly to rederive, and supplied with proof or checker. Deduplicate by implication and specialization before enlarging the library.

## Discover-To-Prove Handoff

Freeze one explicit candidate in the answer-hole representation after its validity and informative holdout checks. Convert the unknown-answer task into a fixed theorem about that candidate. Then prove the required properties, including optimality or completeness if requested. Later changes are visible repairs, not silent movement of the answer.

Keep candidate discovery, numerical support, checked finite scope, and full proof separate. Novelty is an additional literature judgment, not a reward for passing an evaluator. Stop discovery when a candidate is ready for proof; continued search at that point can evade the hard obligation.

If search ends earlier, return the strongest supported artifact: a construction with checker, improved bound, counterexample, solved restriction, intermediate theorem, or exact missing prerequisite.

## Paper-Grounded Lessons

These are bounded mechanisms and case studies, not a guarantee of solving open problems. The broader inventory is in the [research source map](research-backed-proof-loop.md).

- [Discover and Prove](https://arxiv.org/abs/2604.15839): separate answer discovery from proving a frozen candidate.
- [Beyond Theorem Proving](https://arxiv.org/abs/2505.04528) and [ComBench](https://arxiv.org/abs/2606.10479): validate the answer payload, not only a proof that can restate the target predicate; separate realization from completeness.
- [PatternBoost](https://arxiv.org/abs/2411.00566), [AlphaEvolve](https://arxiv.org/abs/2506.13131), and [Generative Modelling for Mathematical Discovery](https://arxiv.org/abs/2503.11061): combine diverse proposals with executable validity checks and problem-specific local improvement.
- [$k$-server-bench](https://arxiv.org/abs/2604.07240): calibrate finite evaluators, cache hard violations, and retain the distinction between a finite lookup certificate and a general potential proof.
- [Self-supervised theorem discovery](https://arxiv.org/abs/2606.28747): select reached theorems by useful generality and difficulty of reproof rather than appearance.
- [From Solvers to Research](https://arxiv.org/abs/2607.07779): evaluator-driven search does not remove the need for new representations, concepts, and mathematical judgment.
