# Cold Prover-Verifier Loop

Use this after a complete candidate proof exists, or earlier only when the whole route depends on one unusually fragile kernel. Verification should test mathematics, not co-author the initial idea.

## Separation Contract

The prover receives the problem, selected premises, compact failure memory, and any checked artifacts needed to construct a proof.

The verifier receives only:

- the exact claim and essential acceptance conditions;
- the candidate proof or explicit counterexample;
- source excerpts or tool artifacts actually cited by the candidate;
- no route scores, generator confidence, hidden plan, or desired verdict.

Use a fresh context when possible. A same-model fresh context reduces anchoring but remains advisory rather than formal proof.

## Prover Contract

The prover should:

1. choose one motivated route;
2. state its central object and first nonroutine implication;
3. for a selected hard plan, expose and fully develop its key original step and conditional assembly;
4. carry the route to a complete paper-order candidate;
5. stop at the first exact obstruction if completion is impossible;
6. avoid placeholder lemmas, theorem-strength assumptions, and citations that merely resemble the target.

The visible candidate should contain mathematics only. Search logs and route management belong in project memory.

## Verifier Contract

Read the proof sequentially and locate the earliest fatal error. Check:

- fidelity to the exact statement;
- every quantified domain and boundary case;
- assumption availability at the point of use;
- definitions and theorem applicability;
- existence and properties of constructed objects;
- local deductions and global assembly;
- citations or computational evidence supplied in the packet.

Return one of:

- `correct`: exact claim established with no critical error or gap;
- `wrong`: a visible invalid deduction, contradiction, counterexample, or claim mismatch;
- `uncertain`: a nontrivial premise or artifact needed for checking is absent.

Always return the first error, its location, the violated obligation, and the smallest useful repair hint. Do not replace the proof with a new proof.

## Repair Decision

After rejection, classify the first error before acting.

| Error | Action |
| --- | --- |
| Local algebra, omitted case, or missing cited premise | Repair once, then recheck the whole proof |
| Claim mismatch or silent assumption | Restore the original statement and replan |
| Central lemma false or unsupported | Retire or replace the central mechanism |
| Assembly gap | Preserve independent lemmas, rebuild only the dependency path |
| Missing source premise | Retrieve the exact source and check its assumptions |
| Missing or stale tool evidence | Replay the named certificate; preserve the candidate and resume verification |
| Referee process failure | Restore verification of the same candidate; no mathematical failure is recorded |

One local repair is allowed while the same central mechanism survives. A second rejection at the same proof state requires a fresh representation or route.

## Local Kernel Exception

Before a full proof exists, use a verifier only if all of the following hold:

- the route is coherent except for one named kernel;
- the kernel is strictly smaller than the theorem;
- the verifier has the exact local assumptions and dependencies;
- either verdict changes the route.

Otherwise continue mathematical discovery. Repeatedly verifying speculative fragments creates local polish without global progress.

## Promotion Boundary

A model-accepted candidate is `referee-accepted`; its recorded disposition may be proof or refutation, while human review and formal verification remain false. An exact replayed CAS or solver artifact is `tool-checked` only for its encoded claim. A Lean lemma is `formalized-local` until the exact parent theorem is assembled and replayed. Outcome, evidence basis, and scope are separate; never promote by wording alone.

Use `scripts/run_referee.py` for the fresh-context packet and `scripts/proof_loop.py` for bounded generation, first-error repair, and replanning.
