# Optimization and OR/MS

Use for optimality certificates, algorithm guarantees, and structural optimization claims. Bellman and control arguments belong in [dp-proof-playbook.md](dp-proof-playbook.md).

## Choose a certificate with the right scope

| Problem | Kernel | Missing premise to check |
| --- | --- | --- |
| Convex program | Feasible KKT point or matching primal/dual values | Convexity makes KKT sufficient; deriving multipliers or strong duality needs its own constraint-qualification or duality argument |
| Nonconvex program | Global bound, exact convexification, or exchange argument | Stationarity and local second-order conditions do not certify global optimality |
| LP/integer program | Dual bound, integrality, or rounding | Primal/dual feasibility and attainment as used; total unimodularity also needs integral data in the appropriate form |
| Greedy or structural policy | Exchange preserving feasibility and improving the objective | Every proposed exchange is legal, and repeated exchanges reach the claimed canonical form |
| Approximation algorithm | Compare to a specified feasible benchmark | Charging, potential, or dual bound accounts for every cost and resource |
| Value/comparative statics | Envelope or monotone-argmax theorem | Attainment, regularity, ordering, and feasible-set dependence match that theorem |
| Fixed first-order algorithm | Interpolation inequalities and dual/energy certificate | Method, function class, normalization, horizon, and performance metric match the encoded problem |

For the final row, [peppy-proof-bridge.md](peppy-proof-bridge.md) separates numerical performance estimates, checked certificates, and all-horizon Lyapunov proofs. A finite-horizon pattern is a conjecture about the general formula.

## Simplify the bottleneck

Replace boundary-heavy first-order calculations by a subgradient/KKT certificate when justified. Seek a dual bound before solving for every optimizer. Derive an exchange or potential from the exact residual, and verify it uniformly rather than fitting coefficients on sampled instances.

Stress candidate arguments at active constraints, ties, fractional relaxation optima, and nonconvex local optima. Solver outputs can suggest active sets and dual support; the mathematical certificate must establish feasibility, the bound, and equality or the claimed gap.
