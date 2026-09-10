#!/usr/bin/env python3
"""Create a routed workspace for a hard theory-proof project."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from frontier_evidence import write_frontier_template
from new_ledger import TEMPLATE as LEDGER_TEMPLATE
from proof_runtime import init_runtime
from select_playbook import PLAYBOOKS, score


def slugify(text: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", text.strip().lower()).strip("-")
    return slug or "proof"


CLAIM_TEMPLATE = """# Claim

{claim}

## Context

- Domain:
- Variables:
- Assumptions:
- Desired conclusion:

## Source

- User prompt:
- Related files:

## Acceptance Contract

- exact success criterion:
- admissible objects or operations:
- required edge and boundary cases:
- near-misses that do not count:
- atomic semantic obligations:
- preservation checks for reductions and constructions:
- answer or witness contract when applicable: type, encoding, forbidden self-reference, soundness, completeness or canonicity

## Assumption And Definition Lineage

Fill this only when a route adds or changes an assumption, binder, quantifier, semantic convention, or definition field. Compilation does not make an undocumented change legitimate.

| item | lineage | source or justification | effect on original claim |
| --- | --- | --- | --- |
| H1 | original / source-explicit / source-implied / encoding adapter / theorem repair |  | unchanged / repaired |

## Completion Coverage

Fill this only during assembly or final review. A required row without a proved or checked discharge prevents complete-proof status.

| acceptance obligation or edge case | proof node or certificate | status |
| --- | --- | --- |
| C1 |  | open / covered |
"""


WORKSTREAMS_TEMPLATE = """# Workstreams: {title}

This is a state board, not executable code. Use it only for hard, stuck, tool-assisted, or literature-dependent proof work.

Create a card only when a branch needs durable state. Before a repeated or expensive move, name the expected new artifact. Changing notation or restating the same missing lemma is not progress.

## Approved Research Question

- question:
- scope:
- approved by user:
- open definitions:
- stop condition:

## Goal Backlog

| goal id | goal | why it matters | status | active workstreams | user approved |
| --- | --- | --- | --- | --- | --- |
| G1 |  |  | planned |  |  |

## Active Workstream Cards

No active workstream is required until a branch needs durable state. For a small unclear proof, use a micro check and record the result in `IDEA_MAP.md`, `PATTERN_SCAN.md`, or `LEDGER.md`.

## Multi-Agent Dispatch Gate

Use actual parallel agents only after the user explicitly asks for or approves multi-agent work. The coordinator/integrator remains responsible for statement fidelity, route choice, and final proof status.

Good role split:

- Planner: route portfolio, lemma graph, proof-state equivalence, and bottleneck choice.
- Falsifier: negation, boundary cases, finite examples, and missing-assumption search.
- Retriever: one to three theorem patterns, paper tricks, or formal-library premises.
- Formalizer or Tool-Checker: one local lemma, exact artifact, and failure feedback.
- Reviewer: adversarial audit of assumptions, quantifiers, assembly, and repeated states.

Bad split: several agents independently writing the same full proof.

For open-ended route discovery, independent scouts may each return one compact route card rather than a full proof. Give them the theorem fence and allowed prior results, but not the current favorite or other scouts' narratives. Deduplicate their cards by mathematical approach family before allocating proof budget. The role table is a menu, not a required roster; allocate the next role dynamically from the missing artifact.

| role | assigned artifact | input files | exclusions / do not touch | stop rule | status |
| --- | --- | --- | --- | --- | --- |
| Planner | lemma graph / route decision | claim.md, LEDGER.md | no tool runs, no final proof | one route board or one bottleneck | planned |
| Falsifier | counterexample or missing-assumption report | claim.md, counterexamples.md | no proof polishing | one finite/boundary result | planned |
| Retriever | pattern card or theorem-premise list | PATTERN_SCAN.md | no unsupported theorem import | 1-3 strong sources | planned |
| Formalizer | checked local lemma or Lean/tool gap | TOOL_PLAN.md, lean/ | no global theorem claim unless fully closed | one local artifact | planned |
| Reviewer | gap report | LEDGER.md, writeup/ | no rewriting proof route | one adversarial pass | planned |

## Integration Rule

Integrate returned artifacts by decision value: counterexample, missing assumption, verified lemma, retrieved theorem pattern, exact tool certificate, or concrete gap report. Long prose without a new artifact does not outrank a smaller checked result.

## Approach Family Registry

Use this only when several routes are live. Classify by mathematical mechanism, not route names or prose. A family that reaches the same theorem-strength gap without new evidence is blocked until its reopen condition is met.

| family | proof architecture | central object / certificate | independent seed artifact | kernel or failure witness | status | reopen only with |
| --- | --- | --- | --- | --- | --- | --- |
| F1 |  |  |  |  | live / saturated / blocked / retired | new mechanism / invariant / construction / representation / premise / verifier |

## Portfolio Checkpoint

Use this only after a bounded round with several live families. Preserve one incompatible shadow while the leading kernel is unresolved; do not fund every family equally.

- leading family and decisive next artifact:
- incompatible shadow family and bounded probe:
- live / saturated / blocked / retired updates:
- artifacts returned this round:
- underexplored high-decision family, if any:
- next dynamic role or tool allocation:
- stop coverage: no cheap high-decision family remains / run one bounded probe

## Attempt Fingerprint Index

Use this table before any repeated proof route, construction, counterexample search, or tool-backed lemma attempt. The point is to identify the same failed idea under different notation.

| id | status | route family | central object | target lemma | parameterization | invariant/certificate | failure witness | missing assumption | new evidence expected | retry allowed only if |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1 |  |  |  |  |  |  |  |  |  |  |

For constructive attempts, put the construction family in `route family`. A policy, mechanism, coupling, hard instance, potential, certificate, payment, dual, or counterexample with the same central object, parameterization, invariant/certificate, and failure witness is the same attempt unless the retry condition is genuinely new.

## No-Repeat Decision

Treat attempts with the same goal, assumptions, central object, and failure witness as one state. Retry only with a new premise, representation, certificate, counterexample repair, theorem repair, or imported theorem pattern. Otherwise block it in `LEDGER.md`.

If there are several fingerprints or the match is ambiguous, run:

```bash
codex-math-python "${{CODEX_HOME:-$HOME/.codex}}/skills/math-research/scripts/check_attempt.py" . --route-family "ROUTE" --central-object "OBJECT" --target-lemma "LEMMA" --failure-witness "WITNESS"
```

## Route Candidate Board

Use this when several proof sketches are plausible. Keep it small, attach one cheap decisive evaluator to each candidate, and retire repeats quickly.

| route | central object | expected artifact | cheapest decisive evaluator | decision value | assembly relevance | novelty axis | status / retire if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 |  |  | toy / boundary / symbolic / solver / local formal | high / medium / low | high / medium / low |  | candidate /  |

## Step Challenge Board

Use this for multi-step proof plans. Each fragile step needs both gates before it can become part of the final proof.
Set a small cap before starting, such as 1-2 challenge rounds per step and 1 re-plan per route unless the user explicitly grants a larger budget.

| step | declared goal | verification tag | goal gate | logic gate | verdict | trace-back or re-plan note |
| --- | --- | --- | --- | --- | --- | --- |
| S1 |  | tool-verified / easy-to-check / hard-to-check | pass / fail | pass / fail | accept / challenge / trace-back / re-decompose / re-plan / stop |  |

## Prover-Verifier Move Contract

Use this for fragile local moves, especially after a failed attempt, tool feedback, Lean feedback, or a possible hidden assumption.

| move id | current subgoal | prover move | expected artifact | verifier verdict | soundness probe | proof-state delta | coordinator decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PV1 |  |  | proof / counterexample / condition / certificate / repaired statement | accept / challenge / trace-back / re-decompose / retrieve / tool-check / statement-repair / stop-report |  | smaller / unchanged / larger / refuted |  |

The verifier is read-only unless explicitly assigned a proof role. If the same move is challenged twice without a new artifact, route to `Route Decision Check`.

When feedback comes from Lean, a solver, CAS, or another exact checker, mark the runtime attempt with `feedback_kind: checker` and preserve a diagnostic-grounded repair tuple: checker backend, failed artifact, exact diagnostic and local state, diagnostic site, inferred root cause, failure class, compact diagnosis, minimal repair, and replay result. Copy checker output without paraphrasing it away. The reported site may be downstream of the cause; only replay through the same pinned checker can accept the repair.

## Failure Localization And Salvage

Fill this only after a verifier, tool, reviewer, or counterexample rejects a multi-step attempt. Later deductions are not evidence once an earlier dependency fails.

- verified prefix:
- first failing step:
- failure witness or verifier error:
- independently rescued artifacts:
- affected dependents:
- failure stage: strategy-discovery / decomposition / premise-retrieval / local-proof / assembly / fidelity / library-coverage
- next scope: local trace-back / re-decompose / route replan / statement repair / stop-report

Preserve only artifacts whose own dependencies were checked. Repair the first failing node and affected dependents; do not regenerate the verified prefix.

## Proof-State Equivalence

Use this before retrying a route. Merge states or actions that differ only by notation.

| id | equivalent prior state/action | shared goal | shared local assumptions | shared central object | shared failure witness | decision |
| --- | --- | --- | --- | --- | --- | --- |
| E1 |  |  |  |  |  | merge / allow-new |

## AND/OR Bottleneck Board

Alternative routes or constructions are OR nodes. Required child lemmas are AND nodes. Attack the weakest required child before expanding a new route.

| node | kind | parent | required children or alternatives | bottleneck child | next action |
| --- | --- | --- | --- | --- | --- |
| G1 | AND / OR |  |  |  | prove / refute / split / retrieve / repair |

## Failed-State Notebook

Keep entries short. Use this when a proof move leaves the same subgoal unchanged.

| id | subgoal | attempted move | why it failed | needed new ingredient | next allowed action |
| --- | --- | --- | --- | --- | --- |
| F1 |  |  |  |  |  |

## Route Decision Check

Use this after two local attempts on a node, one repeated failure signature, or any expensive proof move. The decision should be short and evidence-based.

| target node | attempts | proof-state delta | failure diversity | proof similarity / repeat risk | expected next artifact | decision | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N1 |  | smaller / unchanged / larger | new / same / mixed | low / medium / high | proof / counterexample / certificate / theorem pattern / repair / none | continue / repair / re-decompose / retrieve / tool-falsify / stop-report |  |

Use the table to avoid repeated small edits to the same failed idea. Continue only when the next attempt has a new premise, central object, representation, certificate, counterexample, theorem repair, or a smaller proof state.
Count `smaller` only when a required obligation disappears, the worst active gap weakens, or an opaque gap becomes a checkable leaf. More goals or harder goals are not progress.

## Workstream Card Template

Copy this block only when a branch is hard, repeated, multi-lemma, tool-assisted, literature-dependent, or expensive enough to track.

### Workstream W1

- parent goal:
- objective:
- current status: planned / active / blocked / failed / complete
- input context:
- output artifact: pattern card / tool certificate / proof attempt / reviewer report / steering answer
- report path:
- route novelty: new central object / theorem family / certificate / failure world / evidence source / theorem repair
- expected new evidence:

#### Look At How Others Do It Gate

Fill this before heavy execution unless it is intentionally skipped.

- related local drafts, papers, appendices, or prior ledgers:
- theorem or proof names to search:
- analogous models, simpler cases, or benchmark examples:
- source budget: one to three strong sources or patterns before first execution
- extracted proof architecture:
- transferable trick:
- hidden assumptions or conditions:
- what not to copy:
- skip reason, if skipped:
- output to `PATTERN_SCAN.md` or `trick_cards/`:

#### Execution Plan

- branch type: retrieval / computation / proof search / review / steering / mixed
- subagents or tools, if any:
- expected artifact:
- stop rule:
- budget:
- user steering trigger:

#### Progress And Review

- result:
- failure warning:
- reviewer status:
- next escalation:
- user steering question:

## Parallelization Rule

- Treat these as roles first, not automatic agents.
- Use actual parallel agents only when the user explicitly asks for delegation or parallel agent work, and after the dispatch gate above has non-overlapping assignments.
- Each branch must have a bounded output and a stop rule before execution.
- Do not let two agents own the same file or the same proof route unless one is reviewer-only.
- When agents return, update `LEDGER.md`, `WORKSTREAMS.md`, or `PATTERN_SCAN.md` with the artifact, not the full transcript.
- Do not create a workstream card for routine direct proofs; use a micro check instead.
- Failed branches remain in this file and are summarized in `LEDGER.md`.
"""


COUNTEREXAMPLE_TEMPLATE = """# Counterexample Search

## Negation

What would falsify the claim?

## Toy Cases

## Numerical / Finite Searches

## Relaxed Assumptions

## Hypothesis Ablation

Remove or weaken only one high-leverage suspect assumption at a time.

| assumption | ablated claim | explicit witness or failed search | where the original assumption blocks the witness | decision |
| --- | --- | --- | --- | --- |
|  |  |  |  | keep / repair / counterexample route |
"""


IDEA_MAP_TEMPLATE = """# Proof Idea Map: {title}

This page is optional. Fill it only when the proof route is unclear, the theorem has failed before, or the user asks for proof strategy.

## Direct Solve Check

- direct theorem/certificate available:
- if yes, route:
- if no, why not:
- statement fence: exact theorem that cannot be changed without theorem repair:
- papers or prior ledgers to mine for ideas:

## Failure World

- negation:
- smallest bad example:
- boundary or degenerate case:

## Divergence Before Convergence

For hard or previously failed proofs, fill three short candidates before choosing a long route. They must differ by central object, certificate, failure world, or evidence source.
Develop the candidates independently before comparing them; do not let the current favorite become the premise of every lane.

| lane | candidate route | central object | evidence or check | why not a repeat |
| --- | --- | --- | --- | --- |
| proof |  |  |  |  |
| falsification |  |  |  |  |
| orthogonal evidence | small cases / tool / paper pattern / local formalization |  |  |  |

## Central Object Candidates

| object | failure it controls | assumptions that support it | verification hook |
| --- | --- | --- | --- |
{idea_table}

- chosen central object:

## Idea Engines Tried

- [ ] failure-world engine
- [ ] assumption-to-machine engine
- [ ] central-object engine
- [ ] certificate or dual engine
- [ ] invariant, potential, or telescope engine
- [ ] local-to-global engine
- [ ] abstraction-refinement engine
- [ ] retrieval-and-analogy engine
- [ ] pattern-guessing engine
- [ ] construction engine
- [ ] algebra-normal-form engine
- [ ] theorem-repair engine

## Novel Problem Discovery

Fill this only when the answer, object, formula, construction, or decisive concept is genuinely unknown. Otherwise leave the template choices unchanged and continue with the ordinary proof loop.

- frontier scan status: not run / completed
- search cutoff date:
- Scholar queries:
- verified source anchors:
- closest known result:
- active-work signals:
- current frontier gap:
- known-solution status: not assessed / known / likely known / apparently open / genuinely new
- status evidence:
- discovery target: answer / threshold / formula / construction / policy / invariant / counterexample / intermediate theorem / new representation
- answer-hole contract when applicable: admissible representation, forbidden target restatement, and separate soundness / completeness / optimality obligations
- candidate representation:
- validity gate:
- score or evaluator:
- evaluator scope: original theorem / exhaustive restricted instance / sampled / proxy
- rejection implication and acceptance implication:
- evaluator calibration: at least one known-valid and one known-invalid candidate, preferably from a solved frontier rung
- hard-witness regression set:
- simplification ladder:
- holdout cases:
- promotion criterion:
- discovery budget:
- discovered candidate:
- fixed proof handoff:

## Candidate Central Lemma

Start from one of these candidates, then sharpen it.

{central_lemma}

- chosen statement:
- why it would imply the theorem:
- likely proof route:
- how to test or certify it:

## Proof Kernel

Pick one kernel before writing a long proof. A kernel is the smallest lemma, certificate, or counterexample barrier that would decide the current route.

- kernel statement:
- theorem implication: how the kernel plus routine steps gives the claim:
- evidence type: direct proof / known theorem / tool certificate / finite falsification / local formalization:
- failure shape: what counterexample or missing assumption would make the kernel false:
- expected new evidence:
- next action: prove / refute / retrieve / tool-check / repair:

## Bottleneck Surgery

Use this if the kernel stays unresolved after one serious move.

- smallest local lemma:
- negation or tight/equality case:
- alternate representation: dual / slack / Bellman gap / envelope / deviation graph / coupling / KL bridge / potential / telescope:
- decision-value ranking: kernel proof/refutation / counterexample / missing assumption / certificate / retrieval / theorem repair:
- expected artifact:
- result:

## One-Step Proof Move Queue

Use this when the kernel is fragile. Each move should shrink the proof state or reveal a repair.

| subgoal | proposed move | intended theorem/algebra/tool/premise | expected new subgoal | result | proof-state delta |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  | kept / repaired / discarded | smaller / unchanged / larger |

## Construction And Algebra Search

Use this only when the kernel needs a clever object or non-obvious manipulation.

- small cases computed:
- observed pattern: formula / threshold / invariant / tight instance / active set / potential / coefficient sequence:
- guessed object or identity:
- holdout checks that were not used to guess it:
- pattern miner output, if a sequence is available:
- tight or equality case:
- construction seed: dual/slack variable, Bellman gap, envelope term, coupling, hard instance, potential, benchmark, change of measure:
- algebra normal form: add-subtract benchmark, gap form, ratio-to-difference, log/KL/determinant expansion, completing square, conjugate/dual, telescope:
- toy instance or symbolic pattern that suggests it:
- why this move controls the failure world:
- quick check: finite example / Wolfram or SymPy simplification / LP or SMT certificate / known identity:
- discard condition:

## Good Gap / Bad Gap Review

- current missing lemma:
- gap grade: good / bad / unknown:
- reason:
- if bad, split/retrieve/repair action:

## Route Candidate Board

Keep 2-4 routes when the proof needs invention.

| route | central object | why plausible | verification hook | novelty axis | gap grade | status | retire if |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 |  |  |  |  | good / bad / unknown | candidate |  |

## Paper Trick Cards

Record only tricks that change the next proof move.

| source | trick | problem shape | obstruction solved | hidden assumptions | transplant step | verification hook | failure mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

## Route Decision

- selected idea:
- rejected ideas and why:
- route novelty:
- expected new evidence:
- next proof route:
"""


LEAN_TEMPLATE = """import Mathlib

/- Put local formalizable lemmas here. -/
"""


PLAYBOOK_GUIDES = {
    "dp-proof-playbook.md": {
        "attacks": [
            (
                "Bellman verification route",
                "write Bellman equality for the candidate policy and Bellman inequality for all deviations",
                "boundary states, tie-breaking, infeasible actions, missing transversality",
                "Python for finite-state checks; Wolfram for Q-value differences",
            ),
            (
                "threshold or monotone policy route",
                "define Q-value difference and prove single crossing or increasing differences",
                "two-state/two-action examples, nonmonotone transitions, multiple crossings",
                "Z3/Python for finite counterexamples; Wolfram for sign simplification",
            ),
            (
                "convergence or average-cost route",
                "prove contraction/monotone convergence or ACOE with recurrence and bias conditions",
                "beta near 1, transient classes, unbounded value/bias, unstable policy",
                "CVXPy/LP for finite MDP certificates; NetworkX for recurrent classes",
            ),
        ],
        "lemmas": [
            "The Bellman operator is well-defined on the stated value-function class.",
            "The candidate policy satisfies Bellman equality and all off-policy Bellman inequalities.",
            "The Q-value difference has the monotonicity or single-crossing property needed for the claimed structure.",
            "Boundary states, tie-breaking, and finite/infinite horizon distinctions preserve the claimed policy.",
        ],
        "ideas": [
            (
                "Q-value difference",
                "nonthreshold or nonmonotone action choices",
                "increasing differences, monotone transitions, value induction",
                "finite grids plus Wolfram/SymPy sign checks",
            ),
            (
                "Bellman inequality certificate",
                "a feasible action beating the candidate policy",
                "discounting, well-defined value function, feasible action correspondence",
                "finite MDP LP/CVXPy certificate or direct Bellman inequalities",
            ),
            (
                "Bellman operator on a function class",
                "loss of monotonicity, convexity, or threshold structure after one step",
                "operator monotonicity, lattice order, contraction or finite-horizon induction",
                "prove preservation on a two-state/two-action toy model first",
            ),
        ],
    },
    "optimization-or-playbook.md": {
        "attacks": [
            (
                "KKT or dual certificate",
                "prove convexity/concavity, constraint qualification, and complementary slackness",
                "active constraints, nonconvex local optima, nonunique optima, zero denominators",
                "Wolfram/SymPy for algebra; CVXPy for primal-dual sanity checks",
            ),
            (
                "dynamic program or structural policy",
                "write Bellman recursion, then prove monotonicity/threshold/index structure",
                "two-period examples, boundary states, tie-breaking, nonstationarity",
                "Python/Z3 for finite policy counterexamples; Wolfram for value differences",
            ),
            (
                "exchange or primal-dual algorithm proof",
                "define invariant, benchmark, and certificate that telescopes or exchanges locally",
                "small integer instances, relaxation gaps, fractional solutions",
                "OR-Tools/CVXPy for small instances and dual certificates",
            ),
            (
                "PEP certificate and Lyapunov route",
                "encode the recurrence, class, normalization, and metric; conjecture the rate; then extract and prove a sparse certificate",
                "encoding mismatch, finite-N overgeneralization, floating residuals, sign errors, boundary terms",
                "Peppy/PEPFlow for discovery, followed by an independent exact identity check",
            ),
        ],
        "lemmas": [
            "Feasible set and objective satisfy the theorem's compactness/convexity/continuity conditions.",
            "First-order or KKT conditions are sufficient, not merely necessary.",
            "A dual certificate, Bellman inequality, or exchange invariant implies global optimality.",
            "Any all-horizon PEP certificate has exact indexed coefficients, feasible PSD/sign terms, and checked base, step, and boundary identities.",
            "Boundary and tie cases preserve the claimed structure.",
        ],
        "ideas": [
            (
                "KKT or subgradient system",
                "local optimum mistaken for global optimum or ignored boundary",
                "convexity/concavity, constraint qualification, feasible set regularity",
                "Wolfram/SymPy algebra plus active-set checks",
            ),
            (
                "dual certificate",
                "candidate objective value is not globally optimal",
                "strong duality, weak duality, complementary slackness",
                "CVXPy primal-dual sanity check then exact certificate",
            ),
            (
                "exchange invariant",
                "a local swap or deviation improves the solution",
                "matroid, submodularity, convexity, or monotone marginal structure",
                "small integer instances and local exchange checks",
            ),
            (
                "PEP dual/Lyapunov certificate",
                "a candidate algorithm rate lacks an exact all-horizon proof",
                "an exact PEP encoding and valid interpolation class",
                "Peppy eligibility gate, then independent exact checks of the certificate identities",
            ),
        ],
    },
    "mechanism-design-playbook.md": {
        "attacks": [
            (
                "single-parameter IC route",
                "prove allocation monotonicity and derive payments from envelope/payment identity",
                "two-type deviations, lowest-type IR, boundary payments, nonmonotone allocation",
                "Z3/linear inequalities for finite IC/IR; Wolfram for envelope derivatives",
            ),
            (
                "multidimensional cyclic monotonicity",
                "convert IC to no-positive-cycle or convex indirect utility/subgradient allocation",
                "3-cycle type graph, allocation discontinuity, missing quasilinearity",
                "NetworkX/Z3 graph cycle checks; CVXPy for payment feasibility",
            ),
            (
                "revenue or virtual surplus route",
                "identify virtual values, regularity/ironing, benchmark, and payment normalization",
                "nonregular distribution, ironing interval, reserve boundary, approximation benchmark mismatch",
                "Wolfram for virtual values; finite LP for revenue/payment checks",
            ),
        ],
        "lemmas": [
            "Allocation rule is monotone or cyclically monotone under the stated type space.",
            "Payment formula satisfies all IC and IR constraints including boundary types.",
            "Virtual surplus or benchmark comparison implies the stated revenue/optimality claim.",
            "Any randomization, tie-breaking, and support endpoints preserve implementability.",
        ],
        "ideas": [
            (
                "indirect utility and envelope formula",
                "a type gains by a one-dimensional misreport",
                "single-parameter types, quasilinear utility, monotone allocation, boundary IR",
                "finite type IC/IR LP plus envelope derivative check",
            ),
            (
                "deviation graph",
                "a positive cycle of misreports",
                "quasilinearity, finite or discretized type set, cyclic monotonicity",
                "NetworkX/Z3 cycle search or payment feasibility LP",
            ),
            (
                "virtual surplus benchmark",
                "claimed revenue rule loses to another feasible mechanism",
                "regularity, ironing conditions, payment normalization",
                "Wolfram virtual values and finite LP revenue checks",
            ),
        ],
    },
    "games-matching-playbook.md": {
        "attacks": [
            (
                "fixed-point existence route",
                "verify compact convex strategy sets, continuity, and convex-valued upper hemicontinuous best responses",
                "noncompact action set, discontinuous payoff, nonconvex best response",
                "Z3/Python for finite games; Wolfram for payoff inequalities",
            ),
            (
                "supermodular or potential route",
                "prove increasing differences/lattice conditions or construct a potential",
                "two-player two-action counterexample, nonmonotone best response, missing lattice",
                "Sage/Python for lattice examples; Wolfram for increasing differences",
            ),
            (
                "matching invariant route",
                "track proposal/rejection or blocking-pair invariant through the algorithm",
                "ties, capacity edge cases, many-to-one constraints, preference cycles",
                "NetworkX/Python for blocking-pair searches",
            ),
        ],
        "lemmas": [
            "Best response or matching correspondence satisfies the exact fixed-point/stability theorem assumptions.",
            "The proposed invariant is preserved at every step and implies the final property.",
            "Tie-breaking, capacities, and set-valued outcomes do not invalidate the conclusion.",
        ],
        "ideas": [
            (
                "best-response correspondence",
                "no equilibrium or unstable fixed point",
                "compact convex strategy sets, continuity, convex values, upper hemicontinuity",
                "finite game examples plus fixed-point assumption audit",
            ),
            (
                "potential function",
                "improvement cycles prevent convergence or equilibrium selection",
                "exact/ordinal potential or increasing differences",
                "two-player two-action search and Wolfram payoff differences",
            ),
            (
                "blocking-pair invariant",
                "a final matching admits a blocking pair",
                "preference order, capacity, tie-breaking, proposal/rejection invariant",
                "NetworkX blocking-pair search on small instances",
            ),
        ],
    },
    "learning-theory-playbook.md": {
        "attacks": [
            (
                "uniform convergence route",
                "prove pointwise concentration plus union/covering/VC/Rademacher uniformization",
                "data-dependent class, infinite class without capacity, unbounded losses",
                "Python simulations for toy distributions; Wolfram for rate optimization",
            ),
            (
                "stability or PAC-Bayes route",
                "bound neighboring-sample sensitivity or KL/change-of-measure term",
                "adaptive hypothesis choice, missing independence, expectation vs high-probability mismatch",
                "SymPy/Wolfram for constants; Python for small empirical checks",
            ),
            (
                "optimization-to-generalization route",
                "split excess risk into estimation, approximation, and optimization error",
                "nonconvex loss, stochastic gradient noise, missing smoothness/boundedness",
                "Python for SGD toy cases; Lean for local inequalities if useful",
            ),
        ],
        "lemmas": [
            "The target is pointwise, uniform, in expectation, or high probability, and the proof matches that quantifier.",
            "The hypothesis class/loss has the required boundedness, capacity, or stability control.",
            "All failure probabilities are unioned over the right events and indices.",
            "Excess-risk decomposition exactly matches the final theorem statement.",
        ],
        "ideas": [
            (
                "uniform good event",
                "a data-dependent hypothesis violates the bound",
                "bounded loss, capacity control, independence or martingale structure",
                "toy distributions plus concentration theorem retrieval",
            ),
            (
                "excess-risk decomposition",
                "estimation, approximation, or optimization error is mixed incorrectly",
                "ERM/stability/smoothness assumptions and matching quantifier type",
                "symbolic rate algebra and failure-probability audit",
            ),
            (
                "stability or KL bridge",
                "adaptive hypothesis choice or neighboring sample change breaks generalization",
                "algorithmic stability, PAC-Bayes prior/posterior, bounded loss",
                "small-sample perturbation checks and KL algebra",
            ),
        ],
    },
    "bandits-oco-playbook.md": {
        "attacks": [
            (
                "confidence plus optimism route",
                "define a uniform confidence event and prove instantaneous regret under that event",
                "time-uniform failure, adaptive data treated as iid, missing bounded noise",
                "Python simulations; Wolfram/SymPy for rate and threshold algebra",
            ),
            (
                "linear bandit route",
                "prove ridge self-normalized concentration, optimism, and elliptical potential summation",
                "singular design matrix, wrong norm, determinant/log factor mistake, adaptive contexts",
                "SymPy for determinant algebra; Python for summation checks; Lean for local inequalities",
            ),
            (
                "adversarial/OCO potential route",
                "build one-step potential/Bregman inequality and telescope",
                "importance weights with tiny probabilities, comparator outside feasible set, wrong learning rate",
                "Python for variance/summation; Wolfram for learning-rate optimization",
            ),
        ],
        "lemmas": [
            "The confidence event is valid uniformly over time, actions, contexts, and adaptive histories.",
            "Optimism converts the confidence event into an instantaneous regret bound.",
            "The summation lemma is explicit: pull-count, harmonic sum, elliptical potential, or Bregman telescope.",
            "The failure-event contribution is included with the right probability and horizon dependence.",
        ],
        "ideas": [
            (
                "time-uniform confidence event",
                "the chosen action has an underestimated uncertainty or invalid adaptive concentration",
                "bounded/sub-Gaussian noise, filtration, self-normalized martingale conditions",
                "known concentration theorem plus toy adaptive simulations",
            ),
            (
                "instantaneous regret decomposition",
                "optimism does not imply the claimed one-step regret bound",
                "confidence set contains truth, action is optimistic, comparator is feasible",
                "finite horizon stress test and algebraic bound check",
            ),
            (
                "summation potential",
                "one-step bounds do not sum to the claimed rate",
                "elliptical potential, harmonic pulls, Bregman telescope, learning-rate choice",
                "SymPy/Wolfram rate optimization and determinant algebra",
            ),
        ],
    },
    "lower-bounds-playbook.md": {
        "attacks": [
            (
                "two-point testing route",
                "construct two feasible instances that are statistically close but require different decisions",
                "instances too far apart, gap too small, alternative violates assumptions",
                "SymPy/Python for KL/TV and parameter optimization",
            ),
            (
                "Fano or Assouad route",
                "build packing/cube, bound mutual information or pairwise KL, convert testing to risk/regret",
                "packing not feasible, loss separation not uniform, Bayesian/minimax mismatch",
                "Python for packing and KL checks; Wolfram for asymptotic rates",
            ),
            (
                "bandit or mechanism impossibility route",
                "use change of measure or finite type profiles that force contradictory constraints",
                "algorithm can distinguish cheaply, IC constraints not contradictory, wrong benchmark",
                "Z3/LP for finite profiles; Python for change-of-measure algebra",
            ),
        ],
        "lemmas": [
            "Hard instances are all feasible under the model assumptions.",
            "Observation distributions are close enough in KL/TV/mutual information.",
            "Any decision that is good on one instance is bad on another by the claimed amount.",
            "The testing lower bound transfers to the stated minimax/regret/impossibility conclusion.",
        ],
        "ideas": [
            (
                "two hard instances",
                "an algorithm distinguishes or performs well on both instances",
                "feasible parameter perturbation, small KL, separated optimal decisions",
                "Python/SymPy KL and separation optimization",
            ),
            (
                "packing or hypercube",
                "multi-instance lower bound has no uniform separation",
                "packing feasibility, bounded pairwise KL, loss separation",
                "finite packing construction and Fano/Assouad audit",
            ),
            (
                "testing-to-risk bridge",
                "statistical testing lower bound does not imply target regret or risk",
                "minimax/Bayes reduction, feasible estimator/algorithm class, loss transfer",
                "write the binary testing reduction explicitly",
            ),
        ],
    },
    "probabilistic-method-playbook.md": {
        "attacks": [
            (
                "Lovasz Local Lemma route",
                "define bad events, build a valid dependency graph, and check the symmetric or asymmetric LLL condition",
                "bad events too likely, hidden shared randomness, invalid dependency graph, constants fail",
                "Python/NetworkX for dependency degree; SymPy/Wolfram for LLL inequalities",
            ),
            (
                "alteration route",
                "sample a random object, bound the number of violations, then repair or delete them",
                "repair creates new violations, deletes too much, or breaks model constraints",
                "Python for small random instances; algebra tools for expectation and tail bounds",
            ),
            (
                "algorithmic LLL route",
                "identify variables, bad events, and a Moser-Tardos resampling step that terminates under LLL hypotheses",
                "events not variable-determined, resampling changes unrelated constraints, nonconstructive proof claimed as algorithmic",
                "small resampling simulations for sanity only; proof needs LLL hypotheses",
            ),
        ],
        "lemmas": [
            "The random object distribution satisfies all hard constraints before bad-event avoidance.",
            "The bad events exactly cover failure of the desired property.",
            "Each bad-event probability and dependency degree/asymmetric witness bound is correct.",
            "Avoiding all bad events implies exactly the theorem statement, including constants and boundary cases.",
        ],
        "ideas": [
            (
                "bad-event family",
                "some forbidden local configuration survives",
                "random object, local obstruction definition, finite dependency neighborhood",
                "dependency graph count plus LLL inequality check",
            ),
            (
                "dependency graph",
                "union bound is too loose because there are too many events",
                "limited overlap of random variables or justified lopsided dependence",
                "NetworkX overlap enumeration and symbolic `e p (d+1)` check",
            ),
            (
                "alteration repair",
                "random sample has a small number of violations rather than none",
                "expected violation bound, repair does not destroy target size/value",
                "finite simulations plus expectation/tail algebra",
            ),
        ],
    },
}

GENERIC_ATTACKS = [
    (
        "direct theorem route",
        "match the claim to a named theorem and verify every assumption",
        "missing compactness, convexity, continuity, independence, boundedness, or measurability",
        "Wolfram/SymPy/Python/Lean depending on the fragile step",
    ),
    (
        "counterexample route",
        "write the negation and search smallest finite or boundary instance",
        "two-point, two-action, scalar, one-period, or degenerate cases",
        "Python/Z3/CVXPy/Sage for finite searches",
    ),
    (
        "lemma isolation route",
        "split the theorem into the one missing lemma and prove/refute it separately",
        "quantifier mismatch, boundary failure, false strengthening",
        "audit_ledger.py and proof_doctor.py",
    ),
]

GENERIC_LEMMAS = [
    "All variables, domains, quantifiers, and assumptions are explicit.",
    "The negation and smallest nontrivial example have been tested.",
    "Every nontrivial proof step is named as a lemma with status known/proved/tool-checked/missing/false.",
    "The final assembly proves exactly the claim, not a nearby easier theorem.",
]

GENERIC_IDEAS = [
    (
        "negation witness",
        "the smallest object that would falsify the claim",
        "explicit domains, boundary cases, and quantifier type",
        "finite, scalar, two-action, two-type, or one-period search",
    ),
    (
        "named theorem certificate",
        "a hidden assumption gap in a direct theorem application",
        "compactness, continuity, convexity, measurability, independence, or boundedness",
        "assumption-by-assumption theorem audit",
    ),
    (
        "smallest missing lemma",
        "the first unproved step in the attempted proof",
        "only the assumptions used by that step",
        "prove, refute, retrieve, or tool-check this lemma alone",
    ),
]


def dedupe(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def select_playbooks(text: str) -> list[tuple[str, int]]:
    ranked = sorted(
        [(name, score(text.lower(), keywords)) for name, keywords in PLAYBOOKS.items()],
        key=lambda item: item[1],
        reverse=True,
    )
    selected = [(name, value) for name, value in ranked if value > 0][:3]
    if selected:
        return selected
    return [
        ("proof-router.md", 0),
        ("strategy-scheduler.md", 0),
        ("obstruction-taxonomy.md", 0),
    ]


def md_cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ")


def format_attack_table(rows: list[tuple[str, str, str, str]]) -> str:
    lines = [
        "| route | prove by | try to break with | certify/check with |",
        "| --- | --- | --- | --- |",
    ]
    for route, prove_by, break_by, certify in rows:
        lines.append(f"| {md_cell(route)} | {md_cell(prove_by)} | {md_cell(break_by)} | {md_cell(certify)} |")
    return "\n".join(lines)


def format_idea_table(rows: list[tuple[str, str, str, str]]) -> str:
    lines = []
    for obj, failure, assumptions, hook in rows:
        lines.append(f"| {md_cell(obj)} | {md_cell(failure)} | {md_cell(assumptions)} | {md_cell(hook)} |")
    return "\n".join(lines)


def attack_rows(selected: list[tuple[str, int]]) -> list[tuple[str, str, str, str]]:
    rows = []
    for name, _ in selected:
        rows.extend(PLAYBOOK_GUIDES.get(name, {}).get("attacks", []))
    return rows or GENERIC_ATTACKS


def lemma_items(selected: list[tuple[str, int]]) -> list[str]:
    items = []
    for name, _ in selected:
        items.extend(PLAYBOOK_GUIDES.get(name, {}).get("lemmas", []))
    return dedupe(items or GENERIC_LEMMAS)


def idea_rows(selected: list[tuple[str, int]]) -> list[tuple[str, str, str, str]]:
    rows = []
    for name, _ in selected:
        rows.extend(PLAYBOOK_GUIDES.get(name, {}).get("ideas", []))
    return rows or GENERIC_IDEAS


def central_lemma_suggestions(selected: list[tuple[str, int]]) -> str:
    return "\n".join(f"- candidate: {item}" for item in lemma_items(selected)[:4])


def attack_matrix_text(title: str, claim: str, selected: list[tuple[str, int]]) -> str:
    return f"""# Attack Matrix: {title}

## Claim

{claim}

## Selected Playbooks

{chr(10).join(f"- {name} (score {value})" for name, value in selected)}

## Route Matrix

{format_attack_table(attack_rows(selected))}

## Branch Discipline

- Run one proof route and one falsification route before drafting a final proof.
- If a route fails, record the named obstruction in `LEDGER.md`; then switch routes instead of retrying the same prose argument.
- If two routes fail or the same obstruction repeats, open `ESCALATION.md` and run the next external method before another prose proof.
- If the claim changes, rerun `start_proof.py` or update `routing.json` and this matrix.
"""


def lemma_queue_text(title: str, claim: str, selected: list[tuple[str, int]]) -> str:
    lemma_lines = "\n".join(f"- [ ] {item}" for item in lemma_items(selected))
    return f"""# Lemma Queue: {title}

## Claim

{claim}

## Blueprint Dependency Graph

Use this as a proof blueprint, not a flat checklist. Keep the final theorem as the unique sink when possible. Independent proof branches should stay independent until assembly.

Separate statement dependencies from proof dependencies. Statement dependencies define the node's mathematical meaning; proof dependencies are facts, tools, or helper lemmas used to prove it. A node should normally feed the current assembly path before receiving heavy proof effort.

Use AND nodes for required sublemmas and OR nodes for alternative routes, constructions, or representations. A route is complete only when every required AND child is solved. Before expanding another OR branch, work the lowest-confidence required child or record why it is being postponed.

| node id | type | status | statement / role | statement deps | proof deps | used by assembly | expected artifact | gap grade | failure diagnosis | compact repair state | suggested fix |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N1 | lemma | missing |  |  |  | yes / no / unknown | human proof / tool check / counterexample / theorem pattern | good / bad / unknown |  | statement + deps + previous attempt + feedback |  |

Status values:

- missing: needed but not proved.
- checked: verified by symbolic, numeric, finite, or formal tool.
- proved: human proof written and reviewed.
- false-negated: counterexample or proof of negation found.
- conditional: true only under named extra assumptions or weaker conclusion.

Failure diagnoses:

- `STATEMENT_WRONG`: the node is false, too strong, missing an assumption, or uses the wrong representation. Repair or drop it and rewire dependents.
- `PROOF_TOO_HARD`: the node is plausible but too large. Split it into helper lemmas and record those helpers as proof dependencies.

Gap grades:

- good: smaller than the parent, non-circular, assumption-explicit, and checkable.
- bad: hides the core insight, restates the theorem, is circular, or has no verification hook.

Blueprint refinement rule:

- Preserve solved nodes whose statements and dependencies are unchanged.
- If a statement dependency changes, mark dependents as missing until rechecked.
- If a proof dependency changes, recheck the proof route without changing the node statement unless needed.
- Merge equivalent states/actions: same goal, local assumptions, central object, and failure witness means same proof state unless a new premise or certificate is present.
- Prove ready leaves whose dependencies are settled and that feed the final assembly path first.
- Postpone orphan lemmas unless they are used for falsification, theorem repair, or a clearly named route experiment.
- When a node fails, record a short forfeit: diagnosis, forensic analysis, and suggested fix.
- Do not retry a failed node unless the graph changed: new parent, new helper lemma, repaired statement, counterexample, theorem pattern, or certificate.

## Blueprint Metadata Audit

- statement status: intended / suspect / repaired:
- proof status: missing / checked / proved / conditional / false-negated:
- not-ready reason or discussion:
- downstream theorem path:
- orphan or unused nodes to postpone:

## Decomposition Admission Gate

Fill this only before committing a new multi-lemma decomposition, especially after failure.

- parent node:
- conditional parent assembly:
- exact use site for each required child:
- post-proof parent replay: not-run / passed / failed
- why each required child is strictly simpler:
- ancestor-equivalence and cycle check:
- source or statement-fence anchor:
- expected repair radius if one child fails:
- jointly sufficient premise bundle or retrieval plan:
- reviewer verdict: admit / revise / reject

Do not admit the split when the parent assembly or a required child's exact use site is missing, a child merely restates an ancestor, or one failure would force a wholesale rewrite. After a required child is proved, replay the conditional parent assembly and record whether it passed or failed.

## Candidate Lemmas To Prove Or Refute

{lemma_lines}

## Promotion Rule

When a lemma becomes reusable, create a lemma card:

```bash
codex-math-python "${{CODEX_HOME:-$HOME/.codex}}/skills/math-research/scripts/new_lemma_card.py" "LEMMA NAME" --statement "STATEMENT"
```
"""


def tool_check_readme_text(selected: list[tuple[str, int]]) -> str:
    names = ", ".join(name for name, _ in selected)
    return f"""# Tool Checks

Selected playbooks: {names}

Use this directory for small reproducible checks only:

- algebra/rates: `codex-wmath` or `codex-math-python` with SymPy;
- finite counterexamples: Python, Z3, CVXPy, OR-Tools, Sage;
- empirical sanity checks for learning/bandits: `empirical-tools` scripts;
- local formal lemmas: `codex-mathlib-lean lean/LocalLemmas.lean`.

Record every check in `LEDGER.md` before using it in the proof.
"""


def trick_cards_readme_text() -> str:
    return """# Trick Cards

Use this directory for reusable local proof moves extracted from papers, appendices, prior ledgers, or failed attempts.

Create a card only when the trick changes the next proof move:

```bash
codex-math-python "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/new_trick_card.py" "TRICK NAME" --project . --source "SOURCE" --shape "PROBLEM SHAPE" --obstruction "OBSTRUCTION"
```

Status values:

- candidate: promising but not checked in this proof.
- validated-local: proved, refuted, or repaired a concrete lemma.
- rejected: hidden assumptions do not hold.
- promoted: useful enough to copy into a global skill reference.

Keep cards short. Record the local move, hidden assumptions, transplant step, verification hook, and failure mode.
"""


def pattern_scan_text(title: str, claim: str, selected: list[tuple[str, int]]) -> str:
    return f"""# Pattern Scan: {title}

## Claim

{claim}

## Selected Playbooks

{chr(10).join(f"- {name} (score {value})" for name, value in selected)}

## When To Use

Fill this only when the proof is unfamiliar, has failed twice, or needs outside theorem/proof-agent patterns.
Read `external-proof-pattern-scan.md` before broad literature or skill browsing.

## Autonomous Capability Check

- missing artifact or evidence channel:
- failure stage:
- derived current-method query:
- candidate system and primary source:
- non-duplicated capability:
- privacy/trust boundary:
- bounded live probe:
- admit / defer / reject and why:

## Extraction Cards

### Source 1

- source:
- source type: paper / appendix / formalization project / proof-agent skill / prior ledger:
- trick name:
- theorem family:
- proof decomposition:
- statement-fidelity lesson:
- discovery or construction step:
- retrieval target:
- tool/certificate pattern:
- failure or repair rule:
- route-control lesson:
- dependency lesson:
- premise bundle:
- repair-radius lesson:
- source anchor:
- failure stage addressed:
- good-gap / bad-gap lesson:
- transplantable idea:
- hidden assumptions:
- verification hook:
- limits:

## Route Scorecard

### Route 1

- route:
- retrieved premise or theorem:
- evidence type:
- dependency value: high / medium / low
- certificate availability: direct / local / indirect / none
- failure risk:
- next experiment:

## Imported Moves

- route to add to `ATTACK_MATRIX.md`:
- lemma or theorem name to add to `LEDGER.md`:
- expected tool artifact to add to `TOOL_PLAN.md`:
- theorem repair or missing assumption:
"""


def idea_map_text(title: str, claim: str, selected: list[tuple[str, int]]) -> str:
    playbooks = "\n".join(f"- {name} (score {value})" for name, value in selected)
    return IDEA_MAP_TEMPLATE.format(
        title=title,
        idea_table=format_idea_table(idea_rows(selected)),
        central_lemma=central_lemma_suggestions(selected),
    ) + f"""

## Claim

{claim}

## Selected Playbooks

{playbooks}

## Use Rule

If a direct theorem route already works, skip this file. If no central object appears after two idea engines, switch to counterexample search, retrieval, or theorem repair.
"""


def tool_plan_text(title: str, claim: str, selected: list[tuple[str, int]]) -> str:
    return f"""# Tool Plan: {title}

## Claim

{claim}

## Selected Playbooks

{chr(10).join(f"- {name} (score {value})" for name, value in selected)}

## Protocol

Read `tool-assisted-proof-patterns.md` before running broad symbolic, numeric, SMT, optimization, or Lean checks.

For each tool-assisted step, fill one block:

### Check 1

- lemma or claim fragment:
- assumptions/domains:
- negation to test:
- backend:
- query/script path:
- expected artifact: counterexample / exact identity / conditions / KKT-dual certificate / SMT model-or-unsat / Lean lemma / other
- result:
- translation into proof:
- failure interpretation:
- compact repair state if failed:
- next legal repair:

## Artifact Rules

- Counterexample: refutes or repairs the theorem.
- Conditions: become assumptions or case splits.
- Exact identity or `True`: becomes a named algebraic lemma under copied assumptions.
- Optimizer output: must be converted into KKT/dual/certificate logic before use.
- Lean accepted lemma: local formalization only; explain how it connects to the full proof.
- Lean/API formal artifact: audit for `sorry`, admitted axioms, incomplete declarations, unproved dependencies, and missing global assembly.
- Simulation: sanity/falsification only, not a proof.
"""


def strategy_text(selected: list[tuple[str, int]]) -> str:
    first = selected[0][0]
    second = selected[1][0] if len(selected) > 1 else "strategy-scheduler.md"
    return f"""# Strategy Portfolio

## Selected Playbooks

{chr(10).join(f"- {name} (score {value})" for name, value in selected)}

## Research-Backed Loop

- prior-result audit: pending
- draft proof: pending
- sketch subgoals: pending
- premise retrieval targets: selected playbooks, prior ledgers, paper lemmas, formalization projects, proof-agent workflows, mathlib/search if relevant
- external pattern scan: fill `PATTERN_SCAN.md` if routes are unfamiliar or repeated attempts failed
- tool-guided repair targets: first false or unproved sublemma
- compact repair rule: retry a failed node using only statement, dependencies, previous attempt signature, previous feedback, and suggested fix
- graph-search rule: mark OR alternatives and AND required subgoals; work the bottleneck required child before expanding another route
- decomposition-admission rule: require parent sufficiency, strict simplification, acyclicity, source fidelity, low repair radius, and premise feasibility
- failure-stage rule: distinguish strategy-discovery / decomposition / premise-retrieval / local-proof / assembly / fidelity / library-coverage before spending another attempt
- discovery handoff rule: treat model memory as unverified; first record Scholar-backed queries, verified source anchors, closest results, active-work signals, and the exact frontier gap; then define the candidate search and freeze one promoted candidate before proof
- premise-bundle rule: for multi-step routes, retrieve a jointly sufficient theorem set through sketch-retrieve-reflect rather than independent similarity search
- state/action dedupe rule: same goal, assumptions, central object, and failure witness means the same proof state unless there is a real new artifact
- step-challenge rule: tag fragile steps by verification level, run goal and logic gates, then accept/challenge/trace-back/re-decompose/re-plan/stop
- prover-verifier rule: for fragile local moves, keep proposer/checker/coordinator roles separate and record soundness probes plus proof-state delta
- meta-strategy rule: if a route or tool loop repeats, let the coordinator choose a directive before another attempt
- route decision rule: after two local failures, choose continue / repair / re-decompose / retrieve / tool-falsify / stop-report before another attempt
- used-node rule: prove ready leaves on the current assembly path before side lemmas
- lemma revision rule: preserve proved helper lemmas and revise only unproved or false nodes plus dependents
- gap review: good gaps may be deferred as lemmas; bad gaps must be split, retrieved, falsified, or repaired
- formal artifact rule: Lean/API output is not final if the theorem still has `sorry`, admitted axioms, or an unencoded assembly obligation
- progress budget: stop or switch after two unchanged obstruction cycles

## Route A

- theorem family: {first}
- why plausible: selected by keyword/playbook routing from the claim
- current status: pending stress test

## Route B

- theorem family: {second}
- why plausible: backup route if Route A hits an obstruction
- current status: pending stress test

## Route C

- theorem family: counterexample or theorem-repair route
- why plausible: hard proofs often fail because of one missing assumption or quantifier mismatch
- current status: pending negation and toy examples

## Switch Rule

If Route A hits a named obstruction in `obstruction-taxonomy.md`, update `LEDGER.md`, then switch to Route B or re-run playbook selection with the obstruction text.
If two routes fail or the obstruction does not shrink, follow `ESCALATION.md`: tool falsification, retrieval, local formalization, theorem repair, or stop/report.
"""


def triage_text(title: str, claim: str, selected: list[tuple[str, int]], mode: str) -> str:
    return f"""# Proof Triage: {title}

## Claim

{claim}

## Selected Playbooks

{chr(10).join(f"- {name} (score {value})" for name, value in selected)}

## Mode Decision

- mode: {mode}
- why this mode is enough:
- next artifact expected:
- stop or escalation trigger:

## Immediate Tasks

1. Fill exact variables, domains, quantifiers, and assumptions in `claim.md`.
2. Run the direct-solve and statement-fidelity checks. Mark any changed assumption, quantifier, domain, or conclusion as theorem repair.
3. Write the negation and smallest toy, boundary, and relaxed-assumption cases in `counterexamples.md`.
4. Use `ATTACK_MATRIX.md` to compare one proof route, one falsification route, and one orthogonal evidence route.
5. Open `IDEA_MAP.md` only if the central object, construction, proof kernel, or unknown answer is missing. In discovery mode, complete its external frontier scan and Novel Problem Discovery contract before broad search.
6. Build the active AND/OR lemma graph in `LEMMA_QUEUE.md`; work the least-certain required child on the assembly path.
7. Use `WORKSTREAMS.md`, `PATTERN_SCAN.md`, `TOOL_PLAN.md`, or the prover-verifier contract only when repetition, retrieval, tools, or fragile local checking activates them.
8. Run `proof_doctor.py .` after a failure or state change, and `audit_ledger.py LEDGER.md` before claiming a final proof.

## Do Not

- Do not present a polished proof before the verification gates are filled.
- Do not restart from scratch after a failed route; name the obstruction and update `LEDGER.md`.
"""


def counterexample_text(claim: str) -> str:
    return COUNTEREXAMPLE_TEMPLATE + f"""

## Claim Under Test

{claim}

## First Stress Tests To Fill

- Smallest finite instance:
- Boundary/degenerate case:
- Missing-assumption variant:
- Numerical or symbolic counterexample search:
"""


def escalation_text(title: str, claim: str, selected: list[tuple[str, int]]) -> str:
    return f"""# Escalation Plan: {title}

## Claim

{claim}

## Selected Playbooks

{chr(10).join(f"- {name} (score {value})" for name, value in selected)}

## Trigger

Use this file after two failed routes, one repeated obstruction, or a failed tool/toy-model check.

## Ladder

1. Local reroute: name obstruction, shrink to the missing lemma, make a route decision, then switch theorem family if needed.
2. Tool falsification: write negation; search finite/boundary examples; use Wolfram, Python, Z3, CVXPy, Sage, or OR-Tools.
3. Retrieval: search playbooks, prior ledgers, local paper text, theorem names, and formal libraries; use web literature only when needed or requested.
4. Local formalization: formalize the fragile local lemma in Lean/mathlib or write a pseudo-formal lemma card.
5. Theorem repair: mark the original claim refuted/conditional, then add the weakest assumption or weaken the conclusion.
6. Stop/report: return still-open status with exact obstruction and next bounded move.

## Domain Hints

- DP/MDP/Bellman: Q-value single crossing, boundary states, tie-breaking, beta -> 1, Bellman inequality certificate.
- Mechanism/econ: finite type IC/IR deviations, envelope/cyclic monotonicity, payment feasibility LP.
- Learning/bandits: confidence event, instantaneous regret, summation lemma, failure-event contribution.
- OR/optimization: convexity/concavity, constraint qualification, dual certificate, subgradient/case split.

## Ledger Entry To Fill

- trigger:
- failed route:
- obstruction:
- smaller lemma or negation:
- route decision:
- proof-state delta and failure diversity:
- external method used:
- result:
- theorem repair, if any:
- next bounded move:
"""


def ledger_text(title: str, claim: str, selected: list[tuple[str, int]], mode: str) -> str:
    ledger = LEDGER_TEMPLATE.format(title=title, claim=claim, mode=mode)
    entries = "\n".join(f"- {name} (score {value})" for name, value in selected)
    ledger = ledger.replace(
        "Candidate patterns:\n\nSelected playbooks:",
        "Candidate patterns:\n"
        + entries
        + "\n\nSelected playbooks:\n"
        + entries,
    )
    ledger = ledger.replace("S0-parse", "S2-stress-test")
    return ledger


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a theory proof project with automatic routing.")
    parser.add_argument("--title", required=True, help="Short proof project name")
    parser.add_argument("--claim", required=True, help="Exact or provisional theorem statement")
    parser.add_argument(
        "--mode",
        choices=["project", "recovery", "discovery"],
        default="project",
        help="Use recovery after prior failures; use discovery when the answer or object is unknown",
    )
    parser.add_argument("--dir", default="proof_projects", help="Output base directory")
    args = parser.parse_args()

    selected = select_playbooks(args.claim)
    project = Path(args.dir) / slugify(args.title)
    if project.exists():
        raise SystemExit(f"proof project already exists: {project}")

    for subdir in [
        "scratch",
        "lean",
        "lean/handoffs",
        "lemmas",
        "tool_checks",
        "trick_cards",
        "literature",
        "writeup",
    ]:
        (project / subdir).mkdir(parents=True, exist_ok=True)

    (project / "claim.md").write_text(CLAIM_TEMPLATE.format(claim=args.claim), encoding="utf-8")
    (project / "TRIAGE.md").write_text(triage_text(args.title, args.claim, selected, args.mode), encoding="utf-8")
    (project / "LEDGER.md").write_text(ledger_text(args.title, args.claim, selected, args.mode), encoding="utf-8")
    (project / "WORKSTREAMS.md").write_text(WORKSTREAMS_TEMPLATE.format(title=args.title), encoding="utf-8")
    (project / "ATTACK_MATRIX.md").write_text(attack_matrix_text(args.title, args.claim, selected), encoding="utf-8")
    (project / "LEMMA_QUEUE.md").write_text(lemma_queue_text(args.title, args.claim, selected), encoding="utf-8")
    (project / "IDEA_MAP.md").write_text(idea_map_text(args.title, args.claim, selected), encoding="utf-8")
    (project / "ESCALATION.md").write_text(escalation_text(args.title, args.claim, selected), encoding="utf-8")
    (project / "PATTERN_SCAN.md").write_text(pattern_scan_text(args.title, args.claim, selected), encoding="utf-8")
    (project / "TOOL_PLAN.md").write_text(tool_plan_text(args.title, args.claim, selected), encoding="utf-8")
    (project / "strategy.md").write_text(strategy_text(selected), encoding="utf-8")
    (project / "counterexamples.md").write_text(counterexample_text(args.claim), encoding="utf-8")
    (project / "lean" / "LocalLemmas.lean").write_text(LEAN_TEMPLATE, encoding="utf-8")
    (project / "tool_checks" / "README.md").write_text(tool_check_readme_text(selected), encoding="utf-8")
    (project / "trick_cards" / "README.md").write_text(trick_cards_readme_text(), encoding="utf-8")
    (project / "lemmas" / ".gitkeep").write_text("", encoding="utf-8")
    (project / "tool_checks" / ".gitkeep").write_text("", encoding="utf-8")
    (project / "trick_cards" / ".gitkeep").write_text("", encoding="utf-8")
    (project / "literature" / ".gitkeep").write_text("", encoding="utf-8")
    (project / "writeup" / ".gitkeep").write_text("", encoding="utf-8")
    if args.mode == "discovery":
        write_frontier_template(project, args.claim)
    (project / "routing.json").write_text(
        json.dumps(
            {
                "title": args.title,
                "claim": args.claim,
                "mode": args.mode,
                "selected_playbooks": selected,
                "runtime_state": ".proof_runtime/state.json",
                "runtime_brief_command": "proof_runtime.py brief . --markdown",
                "lean_bridge_command": "lean_bridge.py prepare|verify",
                "entry_files": [
                    "TRIAGE.md",
                    "ATTACK_MATRIX.md",
                    "LEDGER.md",
                    "counterexamples.md",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    init_runtime(project, args.claim, args.mode)

    print(project)


if __name__ == "__main__":
    main()
