# Bandits and online learning

Use for regret proofs. Fix the comparator, expected versus high-probability guarantee, and pseudo-regret versus realized regret. State the filtration: which quantities are chosen before the action draw and which noise terms have conditional mean zero. If losses may depend on the current action draw, the usual importance-weighted unbiasedness argument can fail.

## Choose the controlling inequality

| Setting | Kernel to prove | What closes the bound |
| --- | --- | --- |
| Stochastic finite-arm UCB | On a simultaneous confidence event, a suboptimal pull forces its gap below its confidence width | Pull-count bound plus the failure-event contribution; handle zero gaps separately |
| Gap-free stochastic regret | Split pulls by whether their gaps exceed a threshold | Bound small-gap loss directly, large-gap loss by counts, then optimize the threshold |
| Thompson sampling | A justified posterior concentration or information-ratio inequality | Match the Bayesian or frequentist quantifiers of the requested regret |
| Linear/contextual bandit | Conditional noise concentration yields a valid ridge confidence ellipsoid; optimism bounds regret by a feature norm | Elliptical potential controls the sum of norms; retain regularization bias and feature/noise assumptions |
| Adversarial bandit | Importance-weighted estimates are conditionally unbiased and satisfy the chosen potential inequality | Control the variance term using actual sampling probabilities, including exploration |
| OGD/FTRL/OMD | One-step regret is bounded by potential decrease plus a stability/error term | Telescope with the stated regularizer, norm, feasible set, and learning-rate schedule |

A confidence statement must cover the random times and actions actually used. A fixed-time or fixed-action bound cannot be substituted without a uniformity argument. For realized regret, bound the additional noise term separately.

## Diagnose the loss

When a rate loses a logarithm or dimension factor, locate it in concentration, instantaneous regret, or summation before changing the algorithm. A varying learning rate adds terms when telescoping; a doubling argument must include restart costs. Tiny sampling probabilities require explicit second-moment control, not a simulation of benign trajectories.

Useful stress cases are two nearly tied arms, adaptive contexts, vanishing sampling probabilities, and a comparator at the feasible boundary. Exact summation and parameter optimization can check the rate; they do not establish concentration.
