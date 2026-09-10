# Proof State Machine

Use this for a durable project. States are available actions, not a mandatory sequence; direct proving may bypass stress tests, portfolios, or decomposition when they do not help.

## States

- `S0-parse`: exact claim, notation, quantifiers, domains, statement fence, acceptance contract, and atomic semantic obligations.
- `S1-classify`: target type, direct-solve check, and candidate theorem families.
- `S2-stress-test`: negation, edge cases, finite/numeric examples, relaxed assumptions.
- `S2b-idea-map`: optional state for unclear or repeatedly failed proofs; propose failure world, small-case pattern guess, central object, proof kernel, central lemma, and verification hook.
- `S3-route-choice`: one motivated route by default; a bounded portfolio only after the hard-exploration trigger in SKILL.md.
- `S4-lemma-graph`: theorem reduced to a blueprint-style dependency graph of definitions, lemmas, and theorem assembly nodes with statement dependencies, proof dependencies, downstream use, and statuses.
- `S5-local-certification`: check fragile lemmas with tools, known theorems, one-step proof-state feedback, or the prover-verifier move contract; retain any independently verified prefix or helper artifact.
- `S6-assembly`: combine lemmas into the exact target statement.
- `S7-adversarial-review`: try to break assumptions, quantifiers, boundary cases, and conclusion.
- `S8-finalize`: final proof with verification status.
- `S9-stuck`: exact obstruction named, next experiment chosen.

## Transitions

- `S0 -> S1`: all variables, domains, quantifiers, assumptions, acceptance items, semantic obligations, and the no-silent-statement-change rule are explicit.
- `S1 -> S2`: at least one theorem family or proof route is plausible.
- `S1 -> S8`: direct theorem, certificate, contradiction, or known decomposition proves the claim and verification gates pass.
- `S2 -> refuted`: an explicit witness is checked against the original assumptions and conclusion; an encoding or child-lemma counterexample has only that local scope.
- `S2 -> S3`: select one route; no counterexample found is a search signal, not proof evidence.
- `S2 -> S2b`: no obvious central route or the same obstruction has appeared before.
- `S2b -> S3`: one proof kernel or candidate central lemma has a verification hook; if an unknown construction or answer is required, it has passed a holdout/self-check.
- `S3 -> S4`: route has a proof skeleton whose proposed children pass parent sufficiency, strict simplification, acyclicity, fidelity, repair-radius, and premise-feasibility checks.
- `S4 -> S5`: all nontrivial steps are lemma candidates with statement dependencies, proof dependencies, downstream use, statuses, expected evidence artifacts, gap grades, and compact repair states for failed nodes. Fragile or repeated local moves have a named prover move and verifier target.
- `S4 -> S4`: merge equivalent proof states or actions before retrying. Equivalent means same goal, same local assumptions, same central object, and same failure witness up to notation.
- `S5 -> S4`: when a check fails, return to the earliest failing node, keep the verified prefix, and invalidate only affected dependents.
- `S5 -> S6`: each essential lemma is proved, tool-checked, or explicitly marked conditional.
- `S6 -> S7`: assembled proof matches the exact claim and every required acceptance item, edge case, and semantic obligation maps to a proved or checked node.
- `S7 -> S8`: review finds no unhandled gaps.
- any state -> `S9`: a named obstruction blocks progress.
- `S9 -> S1/S2/S3/S4/S5/S6`: classify the failure stage, then return to strategy discovery, stress testing, route choice, decomposition, local proof, or assembly at the earliest affected layer.

## Anti-Loop Rule

After two failed attempts, do not continue prose proof. Update the ledger with:

- current state,
- named obstruction,
- failed routes,
- failed proof state if the last move left the same subgoal unchanged,
- failure stage: strategy-discovery, decomposition, premise-retrieval, local-proof, assembly, fidelity, or library-coverage,
- route decision: continue, repair, re-decompose, retrieve, tool/falsify, or stop/report,
- smallest toy version,
- next experiment.

Then apply `proof-escalation-protocol.md`: tool falsification, retrieval, local formalization, theorem repair, or stop/report.

Node evidence may be `candidate`, `counterexample-tested`, `proved`, `tool-checked`, `partial-verified`, `formalized-local`, `false`, or `missing`. `partial-verified` means a checked prefix or helper artifact survived an incomplete global proof; it cannot close the parent theorem by itself.

## Discovery Overlay

Discovery is a mode overlay, not a mandatory state for ordinary proofs. When a fixed claim lacks a central object or invariant, use one bounded structural-discovery move and a decisive local check; the original theorem remains fixed. Retrieve a close premise only when it could resolve the named obstruction. A missing proof object does not require a literature-frontier audit.

When classifying a result as known, open, or new, or claiming a research contribution, use a bounded external frontier scan with queries, cutoff date, verified source anchors, closest results, and the exact unresolved gap; model memory alone is not status evidence. If the answer itself is unknown and broad candidate search is justified, first define its representation, validity gate, evaluator, simplification ladder, holdouts, promotion criterion, and budget. After one candidate passes those gates, freeze the answer as a fixed theorem statement and resume at `S1` or `S2`. If no defensible evaluator exists, use bounded conceptual exploration or ask for steering instead of running an open-ended candidate loop.

## Research-Level Overlay

For proofs that have already failed or look paper-level, run `S3 -> S6` as a Draft-Sketch-Prove cycle:

- Draft: write the informal proof idea in 5-10 steps, including the theorem family each step is supposed to use.
- Sketch: convert the draft into named subgoals/lemmas, each with inputs, output, and likely prior result.
- Decomposition admission: write a conditional parent assembly, reject equivalent ancestors, and prefer children whose failure has a small repair radius.
- Prove: fill or refute the subgoals one by one; for fragile kernels, try one move at a time and record whether the subgoal became smaller.
- Verify: for challenged local moves, separate proposer, checker, and coordinator roles; record verifier verdict, soundness probe, proof-state delta, and decision before retrying.
- First-error localization: on rejection, identify the earliest invalid step and its witness. Freeze the valid prefix and discard downstream claims that depend on the bad step.
- Repair: classify the failure stage first. Change only strategy, decomposition, retrieval, local proof, assembly, statement fidelity, or prerequisite coverage at the failed layer.
- Blueprint refinement: preserve solved nodes, diagnose failed nodes as false statement or too-hard proof, then rewrite only the failed node and its dependents.
- AND/OR proof graph: treat alternative routes as OR nodes and required child lemmas as AND nodes. A parent proof route is not solved until all required children are solved. Work the lowest-confidence required child first.
- Action/state equivalence: if a new tactic, derivation, or construction produces the same remaining subgoal as a previous failed move, record it as the same proof state instead of counting it as a new attempt.
- Lemma revision loop: after failure, keep proved nodes and verified helper lemmas, add or repair only unproved lemmas, and rerun assembly only after the changed dependencies are ready.
- Salvage rule: promote an intermediate result only when its own dependencies are valid; a result derived after the first failing step is not rescued merely because it looks plausible.
- Dynamic leaves: work on ready leaves whose dependencies are settled and whose downstream use feeds the current theorem. Do not prove orphan lemmas unless they falsify or repair the route.
- Good-gap review: do not accept a missing lemma unless it is smaller than its parent, non-circular, assumption-explicit, and checkable.
- Compact repair: the next repair should use the node statement, dependencies, previous attempt signature, previous feedback, and suggested fix, not the full failed transcript.

Do not polish final prose until every sketch subgoal is `proved`, `tool-checked`, `known`, or explicitly `missing`.
