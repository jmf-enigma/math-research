# Dynamic Programming Proof Playbook

Use for Bellman equations, MDPs, finite/infinite horizon DP, average-cost DP, threshold policies, monotone policies, indexability, inventory/queueing/control models, and dynamic mechanism/control problems. The goal is to turn a hard DP into a small set of Bellman, structural, and verification lemmas.

## Map

- Intake and branch split: identify the DP object and horizon/criterion.
- Smart routes and common lemmas: choose Bellman, monotonicity, threshold, or certificate proof.
- Counterexample tests and tool hooks: stress boundary/tie cases before final proof.
- Templates and failure diagnosis: use the smallest certificate that proves the policy/value claim.

## Intake

Write these before proving:

- State `s`, action `a`, shock `w`, transition `s' = f(s,a,w)`, reward/cost `r(s,a)`, discount or horizon.
- Feasible action set `A(s)` and how it changes with `s`.
- Value object: `V_t`, discounted `V`, average-cost bias `h`, Q-function `Q`, or post-decision value.
- Target: existence, Bellman equation, convergence, threshold/index/monotone policy, convexity/concavity, comparative statics, or optimality of a candidate policy.
- Boundary and tie rules: terminal state, absorbing state, capacity, zero inventory/queue, action ties, finite horizon endpoints.

## Branch Split

- Finite horizon: backward induction; prove the structural property is preserved from `V_{t+1}` to `V_t`.
- Discounted infinite horizon: define Bellman operator `T`; prove contraction or monotone bounded iteration; then prove fixed point and policy verification.
- Average cost: use ACOE/optimality inequality with gain `g` and bias `h`; for finite states use relative value/LP; for unbounded states use drift or Lyapunov bounds.
- Threshold or monotone policy: compare action differences `Delta(s)=Q(s,a_high)-Q(s,a_low)` and prove single crossing.
- Convex/concave value: prove `T` preserves convexity/concavity; use Jensen, monotone transitions, or post-decision state.
- Index policy: introduce subsidy/passive reward; prove passive set expands monotonically in subsidy.
- Constrained DP: use Lagrangian relaxation, prove policy optimality for multiplier, then recover feasibility/complementary slackness.
- Partially observed or belief-state DP: move to belief state, prove value structure on simplex, then verify filter update assumptions.

## Smart Routes

- Do not solve for `V` unless needed. Prove Bellman inequalities or compare Q-values.
- For a candidate policy `pi`, verify `Q(s,pi(s)) >= Q(s,a)` for all `a`; this is often easier than deriving `V`.
- For thresholds, prove `Delta(s)` is monotone and check one crossing plus boundary signs.
- For monotone optimal policies, use Topkis: lattice state/action spaces, increasing differences, and monotone feasible sets.
- For value monotonicity, prove the Bellman operator is order preserving and start value iteration from an ordered function.
- For convexity/submodularity, prove the operator preserves the property; avoid differentiating an unknown value function unless justified.
- For hard global optimality, build a Bellman certificate: `V(s) >= r(s,a)+beta E[V(s')]` for all `a`, with equality for the proposed policy.
- For average-cost proofs, separate recurrence/stability from optimality; ACOE alone may not imply optimality without transversality or boundedness.

## Common Lemmas

- Bellman operator maps the chosen function class into itself.
- Discounted Bellman operator is a contraction in sup norm.
- Finite-horizon induction preserves monotonicity/convexity/submodularity.
- Q-value difference has single crossing.
- Topkis monotonicity gives monotone argmax correspondence.
- Candidate value/policy satisfies Bellman equality on-policy and inequality off-policy.
- Boundary states and action ties preserve the claimed structure.
- Average-cost gain/bias pair satisfies the ACOE and required transversality/stability condition.

## Counterexample Tests

- Two states, two actions, two periods.
- Boundary state: empty/full inventory, zero queue, capacity limit, absorbing state.
- Discount extremes: `beta = 0`, `beta` near 1.
- Tie-breaking and nonunique argmax.
- Nonmonotone transition kernel or action-dependent feasible set.
- Finite horizon versus stationary infinite-horizon policy.
- Average-cost chain with transient or unstable policy.

## Tool Hooks

- Python: enumerate finite-state DP, value iteration, policy iteration, random parameter search, boundary grids.
- Z3/OR-Tools: finite-state counterexamples to threshold/monotone policies.
- CVXPy: finite MDP LP, occupation measures, dual Bellman certificates.
- Wolfram/SymPy: simplify Q-value differences, derivatives, boundary signs, contraction constants, and threshold inequalities. For concrete templates, use `math-tools` reference `dp-wolfram-patterns.md`.
- NetworkX: recurrent classes and reachability in finite Markov chains.
- Lean: small order/inequality lemmas after the DP statement is stable.

## Templates

Bellman certificate for bounded discounted maximization:

Assume a well-defined MDP with bounded measurable reward `r` and discount `0 <= beta < 1`. Let `V` be bounded and measurable, and let `pi` be an admissible measurable stationary policy, with `pi(s) in A(s)` for every state.

```text
Verify for every state s:
V(s) = r(s,pi(s)) + beta E[V(s' | s,pi(s))]
V(s) >= r(s,a) + beta E[V(s' | s,a)] for all a in A(s).
Then pi is optimal for expected total discounted reward among admissible policies.
```

The proof iterates these relations over a finite horizon and then uses `beta^T E[V(S_T)] -> 0`, which boundedness guarantees for every admissible policy. For unbounded rewards or `V`, separately establish integrability of the conditional expectations and finite-horizon identities, justify passage to the infinite return under the stated reward criterion, and prove the needed tail/transversality conditions for the candidate and comparison policies. Vanishing `beta^T E_s^sigma[V(S_T)]` for every compared policy `sigma` is a sufficient tail condition for this argument; any weaker one-sided condition needs its own verification argument. The displayed Bellman relations alone do not justify the unbounded extension.

Threshold proof:

```text
Define Delta(s) = Q(s,1)-Q(s,0).
Prove Delta is increasing or decreasing in s.
Check boundary signs.
Conclude the argmax switches at most once.
Handle ties by the stated tie-breaking rule.
```

Finite-horizon structural induction:

```text
Base: terminal value V_T has property P.
Step: assume V_{t+1} has P.
Show T_t preserves P, so V_t = T_t V_{t+1} has P.
Then derive policy structure from Q_t differences.
```

Average-cost verification:

```text
Find gain g, bias h, and policy pi.
Show g + h(s) >= r(s,a) + E[h(s') | s,a] for all a.
Show equality for a = pi(s).
Check recurrence/stability/transversality.
Then pi is average-cost optimal.
```

Indexability route:

```text
Add subsidy lambda for passive action.
For each lambda, characterize passive set P(lambda).
Prove P(lambda) expands monotonically in lambda.
Solve indifference equation for the index.
Verify boundary states and unreachable/tie states.
```

## Failure Diagnosis

- If monotonicity fails, check transition stochastic monotonicity and increasing differences.
- If threshold proof fails, inspect whether Q-difference is nonmonotone or has multiple crossings.
- If contraction fails, check discounting, weighted norms, or monotone bounded convergence.
- If FOC proof ignores corners, switch to Bellman inequalities or KKT-style active-action cases.
- If average-cost proof is stuck, first prove stability/recurrence under the candidate policy.
- If continuous state proof is messy, discretize for counterexamples before proving the continuous theorem.
