# Proof State Machine

Use to resume or coordinate a durable project. States name the current mathematical action; they are not stages every proof must visit.

## States

| State | Work | Exit artifact |
| --- | --- | --- |
| `S0-parse` | Fix the exact claim, definitions, domains, and quantifiers. | Statement fence and essential acceptance obligations. |
| `S1-classify` | Check a direct proof or applicable theorem. | Motivated route, direct proof, or named missing object. |
| `S2-stress-test` | Test a negation, edge, or informative small case. | Admissible witness or scoped observation. |
| `S2b-idea-map` | Infer an object or kernel when the route is missing. | Candidate mechanism and decisive check. |
| `S3-route-choice` | Choose one route; compare alternatives only when justified. | Central object and conditional parent argument. |
| `S4-lemma-graph` | Decompose only the nonroutine obligations. | Acyclic, sufficient children with downstream uses. |
| `S5-local-certification` | Prove or check the fragile child. | Derivation/artifact with exact scope, or first error. |
| `S6-assembly` | Discharge the original claim from the children. | Complete candidate or explicit missing bridge. |
| `S7-adversarial-review` | Attack the candidate's fragile inference. | First-error verdict and evidence. |
| `S8-finalize` | Deliver the result. | Proof/refutation/conditional result with checked scope. |
| `S9-stuck` | Diagnose the blocking obligation. | Exact obstruction and justified next action. |

## Transitions

Move directly to the needed state. In particular:

- A direct argument can go from `S1` to `S8` after [verification](verification-gate.md); no stress test or graph is required.
- A counterexample closes the original theorem only if it satisfies all original assumptions and violates its conclusion. A child or encoding witness returns to `S4` or `S0`.
- A guessed object moves from `S2b` to `S3` as a candidate after a meaningful check, never as an already proved lemma.
- Before proving children, write the parent argument conditional on them. Reject circular, unused, or theorem-equivalent children.
- A failed child returns to its earliest affected layer. Preserve independent lemmas; invalidate dependent claims even if they look plausible.
- `S6` closes only when each required child has a valid derivation or appropriately translated certificate. Unproved children yield a conditional result.
- Every proof/refutation delivered from `S8` must pass the verification gate at its stated scope. `S9` can return to any earlier state with a new ingredient.

## Anti-Loop Rule

Use the [escalation trigger](proof-escalation-protocol.md#trigger) and its compact durable record. Equivalent states share the goal, assumptions, central object, and failure witness up to notation. An unchanged state is not a new attempt.

Node labels such as `candidate`, `proved`, `tool-checked`, `partial-verified`, `formalized-local`, `false`, and `missing` preserve local status. `partial-verified` records a surviving checked prefix/helper; it does not close the parent. See [evidence meanings](verification-gate.md#outcome-evidence-and-scope).

## Discovery Overlay

If a fixed claim lacks an object, use one [discovery lens](proof-idea-generator.md); no literature-frontier audit is required. If the answer itself is unknown, use [novel-problem discovery](novel-problem-discovery.md) to define a valid candidate and evaluator, then freeze a surviving answer as a theorem before proving it. A known/open/new classification separately requires [frontier evidence](full-text-frontier-evidence.md).

## Research-Level Overlay

For a long proof, keep a compact dependency graph: statement, assumptions/dependencies, downstream use, current evidence, and first error for failed nodes. Alternative routes are OR branches; the children required by a route are AND branches. Work on ready children that determine whether the route survives.

Draft the parent argument, expose the nonroutine child, prove or refute it, and rebuild only affected dependents. A checkable child must be strictly simpler than its parent. Compact repair uses its local statement, assumptions, previous attempt, and exact feedback rather than the entire transcript. Unused lemmas are worthwhile only if they diagnose or repair the route.

When the proof is already complete but opaque, use [structural compression](structural-proof-compression.md) instead of building a larger graph.
