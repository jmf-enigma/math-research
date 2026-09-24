# Cold Prover-Verifier Loop

Use after a complete candidate exists. Earlier review is useful only when one strictly smaller, fragile kernel determines whether a coherent route survives.

## Separation Contract

The prover receives the claim, selected premises, compact failure memory, and checked artifacts. The verifier receives the exact claim, candidate proof or counterexample, essential acceptance conditions, and cited source/tool evidence. Exclude route scores, generator confidence, hidden plans, and the desired verdict.

Prefer a fresh context. It reduces anchoring; it does not make model review formal proof. If delegation is unavailable, perform a distinct adversarial self-review and label it accordingly.

## Prover Contract

Develop one motivated route through its central object, first nonroutine implication, and full assembly. Expose the key original step rather than hiding it in a theorem-strength lemma. Return a paper-order candidate or the first exact obstruction. Keep search history outside the candidate.

## Verifier Contract

Read sequentially. Apply the [verification gate](verification-gate.md) to the candidate and return:

| Verdict | Meaning |
| --- | --- |
| `correct` | The exact claim and applicable acceptance requirements are met, with no detected critical error or gap. |
| `wrong` | A visible invalid deduction, contradiction, counterexample, or claim mismatch. |
| `uncertain` | A necessary premise or artifact is absent, or a valid proof has not met an explicit simplification requirement. |

For `wrong` or `uncertain`, give the earliest blocking location, violated obligation, witness or missing evidence, and smallest useful repair hint. For `correct`, identify the decisive checked implication and scope. Do not replace the candidate with a new proof.

## Repair Decision

Classify the first error using [escalation routing](proof-escalation-protocol.md#escalation-ladder). One local repair may preserve the mechanism; a second rejection at the same goal, assumptions, object, and failure witness requires a changed route or representation.

Missing or stale evidence calls for the named replay, then review of the same candidate. A referee process failure calls for restoring verification, not a new mathematical attempt. Dependency repair preserves independently valid lemmas and rechecks affected assembly.

## Local Kernel Exception

Before a full proof exists, review a kernel only if its exact assumptions and dependencies are available, it is strictly smaller than the theorem, and either verdict changes the route. Otherwise continue discovery; reviewing speculative fragments does not advance global assembly.

## Promotion Boundary

Use [outcome, evidence, and scope](verification-gate.md#outcome-evidence-and-scope) to report the result. The controller records model acceptance as `referee-accepted`, with proof/refutation disposition and separate human/formal-check flags. No status is promoted by wording alone.

`scripts/run_referee.py` prepares the fresh-context check. `scripts/proof_loop.py` manages bounded generation, first-error repair, and replanning.
