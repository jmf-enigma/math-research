# Lower bounds

Use for minimax risk, sample complexity, regret, oracle complexity, and impossibility. Fix the algorithm class, information available to it, loss, and quantifier order. An instance chosen with access to an algorithm's private randomness may violate the adversary model.

## Construct the decision conflict

A useful hard family forces different good decisions while keeping observation laws close. Prove both facts; parameter separation alone need not imply loss separation.

| Obstruction | Kernel | Required check |
| --- | --- | --- |
| Binary decision conflict | Le Cam/testing bound | Admissible alternatives, decision-loss gap, and total variation or KL control |
| Many distinguishable decisions | Fano packing | Packing separation, entropy/cardinality, and mutual-information bound |
| Many local binary choices | Assouad cube | Loss decomposes across coordinates; adjacent hypotheses remain hard to distinguish |
| Adaptive sampling | Change of measure | KL chain rule under the actual history; divergence weighted by expected sample counts |
| Restricted optimization oracle | Hard family or resisting oracle | Oracle replies remain consistent with an admissible instance; dimension and query limits match |
| Mechanism impossibility | Finite type/deviation constraints | Every forced inequality follows from the exact IC, IR, feasibility, and randomization requirements |
| Communication constraint | Information bound and data processing | Transcript includes all permitted messages, public randomness, and side information |

Try two instances when the conflict is binary. Start with a packing or cube when the claimed dimension dependence needs many alternatives. Compute or upper-bound divergence under the actual observation model before optimizing the gap.

A Bayes risk lower bound under a prior supported on the admissible class also bounds worst-case risk for each allowed algorithm; retain the infimum over algorithms to obtain a minimax bound. A lower bound for one fixed algorithm does not establish that infimum.

Stress the construction by checking support mismatch, informative side observations, inadmissible alternatives, and a decision gap too small to imply the target rate. Exact KL and finite feasibility calculations can expose these failures early.
