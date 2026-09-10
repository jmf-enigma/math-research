# Strategy Scheduler

Use this file only when genuinely competing routes or repeated failure require scheduling. The natural proof loop remains the default; the sections below are conditional alternatives.

## Map

- Normalize first: make objects, quantifiers, and the smallest nontrivial case explicit.
- Exact symmetry quotient: merge routes related by a proved statement-preserving transform before allocating search.
- Portfolio routes: choose genuinely different proof architectures before converging.
- Diversity control: seed routes independently, register mathematical families, and redirect saturated search.
- Stage-conditioned trial: compare guidance policies on one frozen proof state only when route control itself is uncertain.
- Progressive budget grants: reserve the verification tail and renew expensive routes only for checked progress.
- Information-ordered representation switch: interpret failures by evidential strength, then change the mathematical object rather than the prose.
- Search discipline: retrieve, guess, kernelize, verify, and repair locally.
- Decomposition admission: accept a lemma split only when it is sufficient, simpler, acyclic, faithful, locally repairable, and consumable by the parent.
- Frontier control: compare a few non-equivalent next moves by decision value, check cost, and assembly relevance.
- Historical revisit: retain a tiny bounded pool of under-ranked but still viable proof states when route scores are noisy.
- Marginal value routing: after repeated failure, choose exactly one next action.
- Novelty and decision value: continue only when a route changes evidence, object, or obstruction.
- Switch rules and scoring: select the route whose assumptions and certificates best match the theorem.

## Normalize First

- Convert maximization/minimization to a standard objective and feasible set.
- Separate objects: primitives, decision variables, random variables, policies, mechanisms, outcomes, payments.
- Mark quantifier type: pointwise, uniform, in expectation, high probability, almost surely, asymptotic.
- Identify whether the desired statement is existence, uniqueness, monotonicity, optimality, incentive compatibility, regret, or lower bound.
- Create the simplest nontrivial instance: scalar, two actions, two types, one period, finite state, deterministic noise, or symmetric case.

## Exact Symmetry Quotient

- List only transforms that preserve the full theorem fence, including domains, quantifiers, assumptions, and conclusion. Examples include relabeling, left-right duality, sign reversal, time reversal, or player permutation when explicitly valid.
- Choose one canonical representative for each exact orbit. A mirrored derivation is not an independent route and does not add diversity by itself.
- Transport a checked witness, lemma, or proof only with the inverse map and a replay on the original statement. A suggestive analogy or approximate symmetry schedules exploration only.
- When the transform exchanges assumptions or boundary cases, record the exchanged obligations instead of silently declaring equivalence.
- Use symmetry to reduce duplicate search and to generate one targeted shadow route, not to multiply cosmetically different attempts.

## Portfolio Routes

Keep one route on the first serious attempt. After two materially different failures, or a serious attempt with no central object, compare at most two motivated routes. A difficult theorem alone is not a requirement to open a portfolio.

- Direct theorem route: match assumptions to a named theorem and verify every condition.
- Contradiction route: assume failure and derive violation of optimality, IC, monotonicity, or concentration event.
- Dual route: rewrite as Lagrangian, LP dual, convex conjugate, envelope, or separating hyperplane.
- Local-to-global route: prove local monotonicity/FOC/single crossing then upgrade using convexity, lattice, or envelope conditions.
- Dynamic route: write one-step recursion, prove Bellman inequality, telescope.
- Potential route: define a potential/log-partition/Bregman term and telescope.
- Martingale route: define filtration, increments, variance proxy, then apply concentration.
- Information route: choose hard instances, compute KL/TV/mutual information, transfer to error/regret.

## Diversity Control

When the portfolio trigger above is met, separate independent route seeding from later synthesis.

- Give each initial seed only the theorem fence, allowed prior results, and output contract. Do not preload the current favorite, a persuasive failed sketch, or another seed's narrative.
- Require one compact route card from each seed: mathematical mechanism, central object, proof kernel, expected artifact, and cheapest falsifier or evaluator.
- Register an approach family by proof architecture, central object, certificate type, and failure world. Merge routes that differ only in terminology, notation, parameterization, or presentation.
- Mark a family saturated when independent seeds reach the same kernel or failure witness without a new artifact. Redirect the next search toward an underexplored family instead of adding attempts to the crowded one.
- End the independence phase once each live family has produced one concrete artifact or exact gap. Only then cross-pollinate useful lemmas, constructions, or counterexamples.
- A route ending at a lemma comparable in strength to the theorem is blocked, not nearly solved. Reopen it only when a new mechanism, invariant, construction, representation, premise bundle, or verification hook makes that lemma genuinely more tractable.
- Keep one incompatible shadow family alive through the next portfolio checkpoint while the leading kernel remains unresolved. The shadow gets one bounded decisive probe, not continuous equal funding.
- After each bounded round, the integrator updates live, saturated, blocked, and retired families; records returned artifacts; and allocates the next role or tool to the highest-value missing artifact. Roles are a menu, not fixed quotas.
- Parallelize across families while the route is unknown. Once a conditional assembly identifies one stable bottleneck, focus independent workers on alternative attacks to that child and stop their siblings after one checked proof; do not pre-prove later children that replanning may discard.
- Before `stop/report`, inspect the registry for an underexplored family with a cheap high-decision probe. Run at most one such probe; exhausting the favorite route is not portfolio exhaustion, but the registry is not a license for unbounded search.

Keep the live frontier small. Independent serial passes can supply diversity; agent count is not a progress metric.

## Stage-Conditioned Strategy Trial

Use this only after repeated project cycles make strategy selection, rather than one mathematical node, the bottleneck. It is not a default multi-agent mode.

1. Label the current stage as `explore` (find a route or object), `consolidate` (merge checked prefixes and eliminate dominated families), `certify-repair` (close the first failing node), or `assemble` (map every theorem obligation to evidence).
2. Freeze one matched baseline: theorem fence, proof-state fingerprint, verified prefix, live gaps, allowed references and tools, privacy boundary, and budget. Compare at most two guidance policies on that identical baseline.
3. Require each trial to return one candidate artifact, its proof-state delta, first failure if any, and a vector audit of obligation coverage, mathematical evidence, dependency fidelity, decision value, and cost.
4. Use relative scores or Elo only to schedule the next trial. They have `proof_effect=none`; only the returned derivation, witness, certificate, checked premise, or formal artifact can change proof status.
5. Keep proof-candidate lineage separate from guidance lineage. Credit a guidance change only for a matched-baseline improvement, then test it on a second proof state or held-out problem before making it reusable.
6. Retire or revise guidance when the stage changes, the same failure fingerprint returns, or its marginal gain disappears. Preserve the compact local log, not every transcript, and never let an active run rewrite the global skill directly.

This is a bounded adaptation of EvE's synchronous race and stage-dependent guidance. EvE's paper evaluates ICON code search, while its public math-proof configuration uses model-generated score dimensions. Neither source makes the scheduling score a proof verifier.

## Progressive Budget Grants

Use this only for expensive routes or project mode.

1. Set aside a verification-and-assembly tail before exploration. It must cover exact replay of the winning artifacts, obligation mapping, and one adversarial final check.
2. Give each expensive route the smallest initial grant that can reach its cheapest decisive evaluator. A grant should target an artifact, not merely more reasoning time.
3. Renew a route only after a checked proof-state delta, a new premise or certificate, a smaller gap, or a verified artifact that unlocks another required node.
4. Stop renewing when the same failure fingerprint returns, prerequisites are absent, or the route consumes budget without changing an obligation. Transfer unused budget to a different family or the verification tail.
5. Keep predictors, route scores, small-model absence, and prior success as scheduling inputs with `proof_effect=none`. Never spend the reserved tail to rescue a favored but unchanged route.

## Information-Ordered Representation Switch

- Read feedback in descending evidential strength: an exact checker result or replayable witness, an exhaustive result within a declared finite scope, sampled or randomized absence, then a model score or critique. A weaker signal may schedule work but cannot inherit the proof effect of a stronger one.
- One valid witness can refute. Failure to find a witness can only suggest a candidate obstruction, rigidity law, or invariant; that candidate becomes a separate lemma to prove.
- After the same failure fingerprint appears twice, move one rung away from the current representation: direct formula to a difference, gap, slack, or equality case; then to a structural lemma; then to a dual, countermodel, certificate, or formal leaf.
- Choose the switch from the obstruction. Boundary failures suggest case separation or KKT conditions; global algebra failures suggest a telescope, potential, conjugate, or invariant; quantifier failures suggest a witness, minimax swap audit, or uniformization lemma.
- A new prompt, agent, temperature, or larger sample is not a representation switch unless it creates a stronger evaluator or a genuinely different artifact.

## Search Discipline

- Retrieval before invention: list the closest known theorem patterns, paper lemmas, textbook facts, or prior ledger lemmas before proposing a new lemma.
- Premise-bundle retrieval: when a route needs several known results, sketch the whole route, turn its steps into subqueries, retrieve candidate premises, and judge whether the set jointly supports the route. Revise the sketch when the bundle is empty or insufficient.
- Guess before proving when the object is hidden: compute tiny cases, infer a formula, threshold, active set, invariant, tight instance, or potential, then reserve one holdout case before promoting the guess.
- Bottom-up lemma probes: when no global strategy is visible, generate at most two special cases or auxiliary facts from the assumptions, prove/refute them cheaply, and use their shared structure to propose the next central object. They need not appear in the final proof.
- Kernel before long proof: state the one lemma, certificate, or counterexample barrier that would decide the route, then prove, refute, retrieve, or tool-check that kernel first.
- Draft-Sketch-Prove: turn the intuitive proof into named subgoals before filling details; subgoals should be small enough for algebra, finite checks, Lean, or direct theorem matching.
- Direct-first then blueprint: try a short direct route once. If it fails, build a lemma graph rather than extending the same prose proof.
- One-step verifier loop: for a fragile subgoal, try one move, predict the new subgoal, check it, and record whether the proof state became smaller.
- Repair by isolation: when a route fails, find the earliest false or unproved step, preserve the verified prefix, and rewrite only the affected subgraph.
- First-error rule: downstream steps after the first invalid inference are not evidence. Earlier checked steps and independent helper lemmas remain reusable artifacts.
- Compact feedback repair: when retrying a failed node, use the node statement, retrieved pattern, previous attempt signature, and a solver-owned attempt digest built from exact checker output. Do not rely on provider-rendered history, and do not reload the whole failed transcript.
- Guarded proof-template reuse: store an accepted schema as its preconditions, substitution map, dependency interface, certificate type, and replay check, not as a raw proof body. Match those preconditions to the current node and replay the instantiated artifact; structural similarity alone is insufficient.
- Progress estimate: after each route, mark whether the remaining obstacle is smaller, unchanged, or bigger; stop or switch after two unchanged/bigger cycles.
- Recombine only after local checks: a final proof is allowed only when each sketch lemma has a status and the assembly matches the original quantifiers.
- Gap reviewer: before accepting a missing lemma, classify it as a good gap or bad gap. A bad gap is equivalent to the theorem, hides the core construction, is circular, or lacks a verification hook.
- Used-node filter: before proving side lemmas, check whether they feed the current theorem assembly. If not, postpone them unless they are being used to falsify, retrieve, or repair the theorem.
- Dependency split: distinguish statement dependencies from proof dependencies. A theorem can structurally depend on one lemma while its proof temporarily needs a different theorem, tool certificate, or local helper.

## Decomposition Admission

Before committing new child lemmas to the graph, require:

- **Parent sufficiency**: a conditional assembly explicitly derives the parent from the proposed children.
- **Consumption gate**: every required child has an exact use site in that assembly. Before expensive proof, confirm the parent would close if the child were assumed; after proof, record a passed or failed replay of the parent with the actual child and retire any proved-but-unused node. `proof_doctor.py` blocks further child work when the active gate is incomplete or a proved required child lacks a passed replay.
- **Strict simplification**: each required child removes a quantifier, dimension, case family, unknown object, or proof technique; it is not the parent under new notation.
- **Acyclicity**: no child depends on its parent or an equivalent ancestor state.
- **Fidelity**: child statements preserve the source definitions, intended role, and legal assumptions.
- **Repair radius**: if one child is false, only a small connected subgraph should need revision.
- **Premise feasibility**: known results, tools, or a bounded retrieval query can plausibly discharge each child.

Reject the decomposition when the conditional assembly or use site is missing, a child is not easier, or the expected repair radius is broad. A formally admissible sketch can still be mathematically useless.

## Marginal Value Routing

Use this after two failed local attempts, one repeated failure signature, or any expensive proof move.

Choose exactly one next action:

- continue current node: only if the proof state got smaller, failures are genuinely diverse, or a new certificate/premise is now available;
- local repair: if the statement seems right but the proof block fails for one identifiable reason;
- re-decompose: if the current missing lemma is a bad gap, too broad, circular, or hides the core construction;
- retrieve/pattern scan: if the route needs a theorem name, standard trick, or assumption list not yet identified;
- tool/falsification check: if a finite example, algebra identity, LP/SMT witness, or local formalization can decide the kernel;
- stop/report: if failure signatures repeat, the proof state is unchanged, and no next move has a checkable artifact.

Route by signals, not vibes:

- proof-state delta: smaller / unchanged / larger;
- failure diversity: new obstruction or same obstruction;
- proof similarity: same central object, same algebra, same parameterization, or same construction;
- attempt count on the node;
- expected artifact from the next attempt.

If the next attempt cannot name an expected artifact, do not continue the same proof route.

## Novelty And Evidence

For a hard or previously failed proof, a new route must change at least one real axis:

- theorem family or proof architecture;
- central object such as a dual, Bellman gap, envelope, potential, coupling, hard instance, certificate, or good event;
- failure world or boundary case being controlled;
- evidence source, such as a tool certificate, finite counterexample search, retrieved theorem, or local formalization;
- statement repair or newly identified missing assumption.

Do not treat these as new routes: same missing lemma with stronger wording, same construction under different notation, same algebra after adding a cosmetic case split, or a proof sketch whose only new ingredient is hope.

A route has made progress only if it proves/refutes a kernel, shrinks the missing lemma, exposes a missing assumption, imports a checked theorem pattern, or produces a checkable artifact. If none of those happen, record the failed state and switch route.

For difficult proofs, use a three-lane first pass unless direct mode succeeds: proof route, falsification route, and orthogonal evidence route. The third lane can be small-case pattern mining, symbolic simplification, LP/SMT/CVX certificate search, Lean for a local lemma, or a one-to-three-source pattern scan.

## Frontier Controller

For a research-level stuck proof, keep a small candidate frontier after the first pass:

- 2-4 routes only;
- each route must differ by central object, certificate type, theorem family, or failure world;
- attach one cheap evaluator to each route: toy counterexample, symbolic identity, premise match, local certificate, or formalizable leaf;
- rank routes qualitatively by decision value, evaluator cost, assembly relevance, novelty, and circularity risk;
- retire any route whose compact failure state matches an earlier fingerprint.

Heuristic route scores can discard a viable prefix too early. Keep at most two historical revisit states outside the live frontier. Admit one only when it preserves a checked prefix, belongs to a distinct approach family, has a named reason the earlier score may be misleading, and either was pruned before a decisive probe or now gains a genuinely new premise, representation, certificate, evaluator, or witness. At a portfolio checkpoint, revisit at most one such state; retire it after an unchanged probe. This is a bounded analogy to [persistent-pool stochastic backtracking](https://arxiv.org/abs/2605.25143), not evidence that random backtracking solves research proofs, and it never overrides the no-repeat rule.

If the answer or construction may be unknown, schedule an external frontier scan before discovery: exact and neighboring results, recent cited-by work, public active projects, verified source anchors, and the unresolved gap. Then require a candidate representation, validity gate, evaluator, simplification ladder, holdout set, promotion rule, and budget. Keep best-per-family candidates rather than a single scalar winner. After local stagnation, inspect another branch; after global stagnation, change representation, audit the evaluator, revise the frontier ladder, or stop. Once a candidate passes promotion, freeze it and return to the ordinary proof scheduler.

When several initial sketches exist, refine the one with the smallest substantive error surface and strongest conditional assembly, not the most polished prose. Raw compiler-error count can be a useful proxy, but one deep mathematical gap can dominate many syntax errors.

Expand one route at a time. Prefer the route whose next artifact can prove, refute, or sharply re-decompose the kernel. Keep a lower-ranked route alive only when it explores a genuinely different proof state. Do not average several weak sketches into one proof.

After an evaluator returns:

- `accept`: add the artifact to the lemma graph;
- `local repair`: preserve the verified prefix and repair the first failing node;
- `trace-back`: reopen the earliest accepted ancestor contradicted by the new evidence;
- `route replan`: retire the proof family only when its central object, decomposition, or required assumptions fail;
- `stop/report`: use when every live candidate is equivalent, low-value, or lacks a checkable artifact.

## Decision Value Ranking

When several next moves are possible, choose the one with the highest decision value. A high-value move can end or sharply reroute the search:

- prove or refute the current kernel;
- produce a counterexample, boundary case, or missing assumption;
- produce a checkable certificate, exact identity, LP/SMT/CVX witness, or local formalization;
- retrieve a theorem pattern whose assumptions can be matched immediately;
- replace an opaque algebra step with a dual, envelope, Bellman, KL, coupling, potential, or telescope representation.

Use a verification cascade and stop at the first decisive level: dimensional/domain checks, smallest counterexample or boundary case, exact symbolic/numeric certificate, local formalization, then adversarial assembly review. Expensive formal search is justified only when the local statement is stable and the cheaper checks cannot decide it.

Low-value moves include polishing exposition, adding an unmotivated case split, strengthening the same missing lemma, or trying another route whose failure witness is unchanged.

If all candidate moves have low decision value, stop and ask whether the theorem statement, modeling assumptions, or intended conclusion should change.

When the theorem needs a construction, threshold, potential, hard instance, coefficient, or exact answer, the highest decision-value move is often discovery, not proof: compute or derive the object, self-check it on a holdout case, then convert it into a lemma.

## Switch Rules

- FOC fails or boundary matters: switch to KKT/subgradient/complementary slackness.
- Many IC constraints: switch to envelope theorem for one-dimensional types or cyclic monotonicity/no-positive-cycle for multidimensional types.
- Monotonicity is intuitive but unproved: switch to increasing differences, single crossing, supermodularity, or lattice fixed point.
- Existence proof handwaves best response: switch to compactness/continuity/upper hemicontinuity audit and a fixed-point theorem.
- Regret proof loses a factor: split into confidence event, instantaneous regret bound, summation lemma, and failure-event term.
- Linear bandit proof stalls: isolate ridge confidence, optimism, and elliptical potential as separate lemmas.
- Lower bound has no bite: reduce to two instances, compute KL, then generalize with Fano/Assouad only if needed.
- Optimization proof proves necessary conditions only: add sufficiency via convexity/concavity or construct a dual certificate.

## Route Scoring

Prefer a route when:

- its theorem assumptions are close to the problem assumptions,
- the target conclusion exactly matches the theorem conclusion,
- key lemmas can be checked by local tools,
- it produces reusable lemma cards for future problems,
- it avoids hidden regularity assumptions.

Avoid a route when it requires stronger smoothness, compactness, independence, or convexity than the user stated, unless presenting a conditional theorem.
