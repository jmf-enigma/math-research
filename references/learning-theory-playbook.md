# Learning theory

Use for generalization, empirical processes, statistical rates, stability, PAC-Bayes, and online-to-batch conversion.

## Fix the probability statement

State expected, high-probability, almost-sure, or other convergence mode; pointwise versus uniform scope; iid versus adapted observations; and loss/noise tail assumptions. A data-dependent class needs a valid conditioning or complexity argument. Check measurability/separability of suprema and every interchange of supremum, expectation, or limit.

## Select the bound that matches the dependence

| Setting | Kernel | Main obligation |
| --- | --- | --- |
| Fixed finite class | Concentration plus union bound | Simultaneous coverage of the whole class under the stated sampling law |
| Fixed infinite class | Symmetrization and capacity control | Integrable envelope, measurable supremum, and a valid complexity/covering metric |
| Local excess risk | Basic inequality and localized fluctuations | Curvature/Bernstein condition and a self-consistent radius bound |
| Algorithmic stability | Compare neighboring samples | The stability notion implies the requested expected or tail guarantee |
| PAC-Bayes | Change of measure from a prior to a posterior | Prior independence or an explicit data-dependent-prior theorem; KL and confidence terms retained |
| Online-to-batch | Convert regret into population risk | Sampling/filtration, averaging rule, and convexity or randomized-output argument |
| Optimization plus estimation | Decompose error | Each optimization, approximation, and estimation term uses the same objective and domain |

## Localized empirical processes

Derive the estimator's basic inequality before choosing a complexity measure. Localize in the risk or metric that inequality controls, bound stochastic fluctuations on that class, and solve the critical-radius inequality. Then prove the estimator lies in the claimed region, using peeling, star-shaped scaling, or another justified closure argument. Assuming localization to prove localization is circular.

If the radius does not close, inspect curvature, the localization metric, and whether a global capacity bound was substituted for a local one. Optimizing an algebraic rate cannot repair a missing statistical premise.

## Chaining

Choose multiscale nets in the process's increment metric. Bound the telescoping increments with a valid allocation of failure probabilities or expected suprema, and justify convergence of the entropy sum/integral. Separability, path continuity, or an explicit approximation bound must control the terminal remainder. A sequence of finite-net bounds is not yet a uniform bound on the full class.

## Failure probes

Use a heavy-tailed loss to test hidden boundedness, an adaptively selected hypothesis to test conditioning, and a large or nonmeasurable class to test uniformity. Keep pointwise versus uniform and expectation versus tail conclusions separate. In SGD arguments, isolate deterministic descent, bias, and martingale noise before invoking concentration.

The semantic checks are informed by the [AI4SLT case study](https://arxiv.org/abs/2602.02285); its project-specific results do not establish a general theorem-proving success rate.
