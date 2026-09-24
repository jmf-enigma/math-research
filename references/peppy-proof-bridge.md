# Peppy Proof Bridge

Use for a fixed-algorithm worst-case performance claim whose encoding is justified. Resume the companion `peppy` workflow only far enough to obtain the missing proof artifact.

## PEP Eligibility Gate

Require the exact algorithm recurrence/oracle calls, a function/operator class supported by valid PEPFlow primitives or finite interpolation inequalities, the theorem's normalization and scalar metric, and a finite-horizon bound or all-horizon Lyapunov/telescoping target.

Optimization, learning, DP, or a recurrence alone does not establish eligibility. Prove a proposed reduction before relying on its PEP result; isolate missing modeling lemmas first.

## Entry And Stop Rule

Load the installed `peppy` skill and inspect `examples_peppy/<ALGO_NAME>/state/`. Use the next missing block only when its return changes the current proof. Validate existing `b1`–`b5` artifacts before rerunning discovery.

| Block | Return | Scope before further proof |
| --- | --- | --- |
| 1 `pep-implement` | Encoding, horizon sweep, rate pattern | Conjecture/falsification. |
| 2 `pep-full-proof` | Dual support, lambda/S structure, residual | Finite-instance evidence; exact certificate only after independent checking. |
| 3 `lyap-define` | Grouped partial sums, rank profile, sign convention | Candidate potential/decomposition. |
| 4 `lyap-vectors` | Sparse basis and coefficient patterns | Candidate construction/recurrence. |
| 5 `lyap-closed-form` | Formulas, base/step/boundary identities | Proof kernel subject to the gates below. |

Stop after the first block that answers the question. Blocks 3–5 are for a needed all-horizon or readable certificate; finishing them does not repair a mismatch with the user's theorem.

## Handoff Contract

In durable mode record the theorem-side recurrence, class, normalization, metric, and horizon; algorithm name and `bN.json` path; extracted object; exact obligation it addresses; and next unmet gate. Link state files instead of copying matrices. A promoted formula becomes a named lemma with its assumptions and downstream use.

## Promotion Gate

| Gate | Required check |
| --- | --- |
| Fidelity | Recurrence, oracle/class, normalization, metric, and horizon match the theorem. |
| Interpolation | Each inequality is valid under those assumptions. |
| Exactness | Coefficients/identities are exact, reconstructed with proof, or rigorously enclosed. A small floating residual is not an exact certificate. |
| Feasibility | Multipliers and Gram/PSD terms satisfy signs and domains. |
| Direction | The identity has the needed inequality direction under its sign convention. |
| Coverage | Base, interior, terminal, and exceptional parameter cases hold. |
| Quantifiers | An indexed formula and proof establish arbitrary horizon; one `N_verify` cannot. |
| Assembly | The certificate implies the original performance claim. |

Check extracted formulas with exact arithmetic, CAS, or Lean where useful. Repeating the numerical solver is not an independent certificate check.

## Failure Routing

| First failure | Next move |
| --- | --- |
| Sweep contradicts conjecture | Audit encoding, parameters, and theorem on small cases. |
| Dense dual has no stable sparse support | Revisit certificate representation or inspect one structurally close example. A changed normalization/objective still needs a theorem mapping. |
| Sparse certificate leaves a residual | Isolate the first residual term; repair lambda/S locally. |
| Rank/grouping is unstable | Check indices and boundaries before finding new vectors. |
| Coefficients fit only sampled indices | Challenge on holdouts, derive a recurrence, then prove it. |
| Base/step/boundary/PSD/sign fails | Keep valid blocks and repair the failed obligation. |
| Exact PEP result does not imply theorem | Prove the reduction or report a conditional result. |

An attempt is identified by recurrence, class, metric, normalization, horizon family, and certificate support. New notation, tolerance, or verification horizon without a new expected artifact is the same route.

## Structural Analogy

[Yoon et al. (2026), §§3.1–3.4](https://arxiv.org/html/2606.26077v1) convert PEP certificates through partial sums, rank structure, and local bases before deriving analytic coefficients. Use those signals within the eligibility gate. A large certificate can have a smaller structural explanation; renaming its full history as a potential does not supply one. Apply the [replacement criterion](structural-proof-compression.md).

Before borrowing a completed example, compare recurrence, oracle/class, objective, active interpolation constraints, rank, and boundaries. An analogy suggests a candidate; a holdout horizon challenges it, and an exact general identity establishes its scope.

## Research Basis And Credit

- [Drori and Teboulle (2014)](https://doi.org/10.1007/s10107-013-0653-0): performance estimation for worst-case first-order analysis.
- [Taylor, Hendrickx, and Glineur (2017)](https://doi.org/10.1007/s10107-016-1009-3): smooth strongly convex interpolation and exact finite-dimensional SDP representation; [composite extension](https://doi.org/10.1137/16M108104X).
- [Taylor, Van Scoy, and Lessard (2018)](https://proceedings.mlr.press/v80/taylor18a.html): automated tight quadratic Lyapunov analyses.
- [Suh, Ying, Jiang, and Nguyen (2025)](https://openreview.net/forum?id=tJqsZZBmmB): PEPFlow, from primal/dual formulation through pattern inspection and symbolic verification.
- [Suh, Yoon, Nguyen, Ying, and Ma (2026)](https://openreview.net/forum?id=q7TfzOgGnb): Peppy's five-stage workflow, with official commands/examples in PEPFlow's [`peppy-workshop-v1` release](https://github.com/pepflow-lib/PEPFlow/tree/peppy-workshop-v1/examples_peppy).

The installed block skills derive from the official commands; the `peppy` shortcut selects/resumes them in the separate [PEPFlow project](https://github.com/pepflow-lib/PEPFlow). Cite Peppy, PEPFlow, and methodology matching the encoded class. Cite other implementations only when used.
