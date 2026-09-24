# Peppy Proof Bridge

Use this bridge only for a fixed-algorithm worst-case performance claim. It connects the general proof controller to the companion `peppy` skill without making all five Peppy blocks a default checklist.

## PEP Eligibility Gate

Enter Peppy only when all of the following are explicit.

1. The algorithm recurrence and every oracle call are fixed.
2. The function or operator class has valid PEPFlow primitives or finite interpolation inequalities.
3. The initial normalization and scalar performance metric match the theorem.
4. The target is a finite-horizon worst-case bound or an all-horizon Lyapunov/telescoping bound.

Do not run Peppy merely because a problem involves optimization, learning, DP, mechanism design, or a recurrence. A reduction to a PEP model is admissible only after the reduction itself is proved. If any gate item is missing, return to the ordinary theorem fence and isolate the missing modeling lemma.

## Entry And Stop Rule

Load the installed `peppy` skill and let it inspect `examples_peppy/<ALGO_NAME>/state/`. Use the next missing block only when its artifact can improve the current proof state. If `b1` through `b5` already exist, validate them instead of rerunning discovery.

| Block | Artifact brought back to the workbench | Highest justified use before further checks |
| --- | --- | --- |
| 1 `pep-implement` | Exact encoding, horizon sweep, candidate rate | Conjecture discovery and falsification |
| 2 `pep-full-proof` | Dual support, lambda/S structure, proof residual | Finite-instance tool evidence; exact finite certificate only if independently checked |
| 3 `lyap-define` | Grouped partial sums, rank profile, sign convention | Candidate Lyapunov object and decomposition |
| 4 `lyap-vectors` | Sparse basis and coefficient patterns across indices | Candidate construction or recurrence |
| 5 `lyap-closed-form` | Closed formulas, base/step/boundary identities, theorem form | Proof-ready kernel after exactness, sign, domain, and assembly gates |

Stop after the first block that answers the user's question. Run Blocks 3-5 only when a readable all-horizon certificate is needed. A numerical rate estimate does not justify continuing automatically, and completing Block 5 does not by itself prove a theorem whose assumptions or metric differ from the encoding.

## Handoff Contract

Record a compact handoff in `TOOL_PLAN.md` and `LEDGER.md`.

- theorem-side algorithm, class assumptions, normalization, metric, and horizon;
- Peppy algorithm name and relevant `bN.json` path;
- central object or certificate pattern extracted from the state file;
- exact local identity or inequality that the artifact is meant to prove;
- current proof status and the next unmet gate.

Link to state files instead of copying dense matrices into the ledger. Put a promoted closed form into the lemma graph as a named node with its own assumptions and verification hook.

## Promotion Gate

A Peppy artifact may enter a completed proof only after checking all applicable items.

1. **Fidelity**: the encoded recurrence, oracle model, class, normalization, metric, and horizon equal the theorem's objects.
2. **Interpolation**: every interpolation inequality is valid under the theorem's assumptions.
3. **Exactness**: proof-bearing coefficients and identities are exact, rationalized with a proved reconstruction, or enclosed by rigorous bounds. A small floating residual is not an exact certificate.
4. **Feasibility**: multipliers, Gram/PSD terms, and any nonnegative coefficients satisfy their sign and domain conditions.
5. **Direction**: the Lyapunov or telescoping identity has the required inequality direction under the declared sign convention.
6. **Coverage**: base, interior step, terminal/boundary, and exceptional parameter cases are all included.
7. **Quantifiers**: a certificate found at one `N_verify` is not promoted to arbitrary `N` without an indexed formula and proof.
8. **Assembly**: the exact certificate implies the original performance claim, not only the internal PEP objective.

Use Wolfram, SymPy, exact Python arithmetic, or Lean for the fragile closed-form identity when useful. Independent checking should consume the extracted formula, not merely rerun the same numerical solver.

## Failure Routing

Do not restart Block 1 after every failure. Preserve completed state and route the first failed gate.

| Failure | Diagnosis | Next move |
| --- | --- | --- |
| Sweep disagrees with the conjecture | Fidelity, parameter, or theorem issue | Audit recurrence, class, normalization, metric, and small cases |
| Dense dual exists but no stable sparse support | Certificate-representation obstruction | Change normalization/objective or inspect a structurally close completed example once |
| Sparse certificate fails the identity | Local certificate error | Isolate the first residual term; repair only lambda/S formulas |
| Rank profile or grouping is unstable | Decomposition or indexing obstruction | Recheck grouping and boundaries before seeking new vectors |
| Vector coefficients fit sampled indices only | Construction remains conjectural | Add holdout indices, mine a recurrence, then prove it |
| Closed form fails base, step, boundary, PSD, or sign | Local proof obstruction | Keep valid earlier blocks and repair the failed identity |
| Exact PEP proof does not imply the user theorem | Assembly or fidelity obstruction | Prove the reduction or report a conditional result |

For no-repeat memory, identify a Peppy attempt by the recurrence, class, metric, normalization, horizon family, and certificate support. Changing notation, solver tolerance, or `N_verify` without a new expected artifact is the same route.

## Structural Analogy

For an existing PEP certificate whose structure is hard to see, [Yoon et al. (2026), §§3.1–3.4](https://arxiv.org/html/2606.26077v1) give a conversion through partial sums, rank structure, and meaningful local bases before solving for analytic coefficients. Use those signals within this bridge's eligibility gate. A large raw certificate need not require a large state; conversely, renaming its entire history as a potential does not establish a simpler proof. See [structural proof compression](structural-proof-compression.md) for the replacement criterion.

Completed examples may suggest a nearby certificate shape. Compare recurrence type, oracle/class assumptions, objective, active interpolation constraints, rank profile, and boundary terms before borrowing a pattern. An analogous example is an idea source, never a premise. If the borrowed structure survives a holdout horizon and exact identity check, promote only that verified structure.

## Research Basis And Credit

- [Drori and Teboulle (2014)](https://doi.org/10.1007/s10107-013-0653-0) introduced performance estimation for worst-case analysis of first-order methods.
- [Taylor, Hendrickx, and Glineur (2017)](https://doi.org/10.1007/s10107-016-1009-3) supplied necessary and sufficient smooth strongly convex interpolation conditions and an exact finite-dimensional SDP representation; their [composite convex extension](https://doi.org/10.1137/16M108104X) covers a broader oracle model.
- [Taylor, Van Scoy, and Lessard (2018)](https://proceedings.mlr.press/v80/taylor18a.html) developed automated tight quadratic Lyapunov analyses for first-order methods.
- [Suh, Ying, Jiang, and Nguyen (2025)](https://openreview.net/forum?id=tJqsZZBmmB) describe PEPFlow's workflow from primal/dual PEP formulation through dual-pattern inspection and symbolic proof verification.
- [Suh, Yoon, Nguyen, Ying, and Ma (2026)](https://openreview.net/forum?id=q7TfzOgGnb) introduce Peppy as a five-stage AI-assisted workflow. Its official command files and examples are released with PEPFlow under the [`peppy-workshop-v1` tag](https://github.com/pepflow-lib/PEPFlow/tree/peppy-workshop-v1/examples_peppy).

The installed block skills originate from the official Peppy command files. The companion `peppy` shortcut only selects and resumes them against the separate [PEPFlow project](https://github.com/pepflow-lib/PEPFlow). In research output, cite Peppy and PEPFlow plus the methodology source matching the encoded class. Cite PEPit or another implementation only when it was actually used.
