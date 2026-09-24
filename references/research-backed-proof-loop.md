# Research-Backed Proof Controls

Use this file only to maintain the skill, diagnose a repeatedly failed proof, or choose a project-mode escalation. Do not load it during an ordinary first proof attempt.

The [2026-09-10 source update](ai-math-workflows-2026.md) adds recent proof workflows and mathematical-discovery case studies, with exact versions, reading scope, limits, and implementation links. It supplements the earlier inventory below.

The papers below contribute decision rules, evidence boundaries, and conditional modules. They do not form one mandatory workflow. The main imported capability is choosing the right stage transition: continue the mathematics, retrieve one missing premise, run one decisive computation, repair one local block, build a durable blueprint, or stop.

## Contents

- [Decision Lanes](#decision-lanes)
- [Paper Admission Gate](#paper-admission-gate)
- [Runtime Controls](#runtime-controls)
- [Conditional Modules](#conditional-modules)
- [Source-To-Control Map](#source-to-control-map)
- [Evidence Boundaries](#evidence-boundaries)
- [Audited Source Inventory](#audited-source-inventory)

## Decision Lanes

| Lane | Activate when | Core action | Do not import |
| --- | --- | --- | --- |
| Natural proof | The statement is stable and one plausible mechanism is visible | Carry one motivated route to a complete candidate, then use a cold referee | A DAG, agent team, route portfolio, or broad search by default |
| Local obstruction | One exact implication, premise, computation, or construction is missing | Choose one retrieval, tool, falsification, Lean, or representation action | Several tools or paper families at once |
| Hard exploration | Two materially different routes failed, or a serious attempt still has no central object or conditional assembly | Run at most two independent route scouts, select one supplied plan, and develop its key original step in depth | Agent voting, blended plans, broad search, or repeated rediscovery of a selected route |
| Durable blueprint | The proof is nonlocal, spans sessions, has several dependent lemmas, or needs formal project tracking | Build a typed dependency graph, preserve solved nodes, and revise only the failed subgraph | Blueprint overhead for a short natural proof |
| Evaluator-backed discovery | The answer or construction is unknown and a replayable evaluator can reject candidates | Freeze the object type, search a diverse frontier, challenge on holdouts, then prove the winner | Evolutionary search scored only by model preference |
| Formal verification | A stable theorem or local lemma is worth encoding | Translate, compile, repair the first failing block, audit axioms and statement fidelity, and replay final assembly | Treating compilation, helper lemmas, or `sorry`-valid sketches as the original theorem |

Start in the natural lane. Move lanes only when a named obstruction makes the next artifact predictable. Run one lane at a time. A module has made progress only if it returns a checked witness, source-verified premise, exact certificate, verified local lemma, strictly smaller obligation, or concrete reason to repair or retire the route.

Training algorithms and benchmark designs are not additional runtime lanes. They may justify a guardrail or an evaluation, but the workbench must not pretend to possess their learned policy, search model, private data, or compute.

## Paper Admission Gate

Judge every new proof paper before changing the runtime. Record six items:

1. **Stage attribution:** does it improve idea discovery, plan stability, proof execution, verification, formalization, training, or only evaluation?
2. **Mechanism:** what concrete intervention could cause the gain, as distinct from a stronger model or larger budget?
3. **Evidence:** is support a controlled ablation, matched-budget benchmark, expert-reviewed case study, model-judged result, or architectural claim only?
4. **Unavailable dependencies:** learned weights, PRMs, private retrieval, token-level sampling, formal libraries, GPUs, or human intervention that this skill does not possess.
5. **Transferable control:** the smallest observable trigger, action, artifact, and stop rule that can run in the present environment.
6. **Regression test:** what routing, budget, memory, or evidence behavior can be tested without pretending that a smoke test proves mathematical ability?

Use one verdict: `import` when the mechanism is directly available and well supported; `adapt` when only a conservative control transfers; `monitor` when evidence is promising but not actionable; `reject` when the gain is inseparable from unavailable training, private implementation, weak evaluation, or unbounded compute. A paper name in a prompt is never a capability.

## Runtime Controls

Runtime instructions have one home: [SKILL.md](../SKILL.md) owns the proof loop; [proof-idea-generator.md](proof-idea-generator.md) owns object discovery; [prover-verifier-loop.md](prover-verifier-loop.md) owns review; [runtime-recovery.md](runtime-recovery.md) owns execution and resume behavior. The source map below explains why those controls were retained.

## Conditional Modules

Activate a module for its mathematical return, not because a cited system uses it. Use [retrieval](external-proof-pattern-scan.md) for an applicable premise, [construction search](novel-problem-discovery.md) for an evaluable unknown object, [Peppy](peppy-proof-bridge.md) for an eligible performance certificate, and [Lean](lean-formalization-bridge.md) for a stable formal target. A long project may need [state and dependencies](proof-state-machine.md); repeated failure may justify the bounded hard-exploration mode documented in [runtime recovery](runtime-recovery.md).

The implementation imports available controls only. It does not reproduce private models, learned policies, PRMs, training, or token-prefix search. QED's two-case diagnostic ablations, the sum-product study's repeated trials on one target, and Beyond the Frontier's PRM-guided benchmark results remain differently scoped evidence, as recorded below.

## Source-To-Control Map

| Source family | Retained control | Activate when | Boundary |
| --- | --- | --- | --- |
| [Rethlas](https://arxiv.org/abs/2604.03789) and [code](https://github.com/frenzymath/Rethlas) | Adaptive choice among examples, counterexamples, retrieval, direct proof, decomposition, and recursion; compact working memory | The natural route lacks one premise or construction | Its natural-language verifier left details that later formalization had to close |
| [Goedel-Architect](https://arxiv.org/abs/2606.06468), [Draft-Sketch-Prove](https://arxiv.org/abs/2210.12283), and [LeanArchitect](https://arxiv.org/abs/2601.22554) | Typed dependency planning, conditional assembly, solved-node preservation, synchronized informal/formal state | Long, nonlocal, or formal projects | Infrastructure and decomposition do not generate the mathematical kernel by themselves |
| [APOLLO](https://arxiv.org/abs/2505.05758), OProver, AXLE, Mechanic, and Goedel-Prover-V2 | First-error localization, coherent-skeleton preservation, compact repair state, exact recompilation | One local block fails and the main strategy survives | APOLLO reports weak repair when the central skeleton is wrong |
| [Aletheia](https://arxiv.org/abs/2602.10177) and [scaling generative verifiers](https://arxiv.org/abs/2511.13027) | Separate bounded verification, abstention, concrete first error, evidence diversity | A complete natural-language candidate exists | Prompt sensitivity and same-family agreement prevent model judges from certifying correctness |
| [AI co-mathematician](https://arxiv.org/abs/2605.06651), [STAR-PolyaMath](https://arxiv.org/abs/2605.19338), and MechMath Agent Team | Durable failed artifacts, trace-back, bounded replan, user steering, single integration point | Repeated or project-scale work | False consensus, nontermination, and orchestration cost argue against default multi-agent use |
| [QED](https://arxiv.org/abs/2604.24021) and [code](https://github.com/proofQED/QED) | Stable plan before execution, explicit key original step, theorem-fidelity and citation gates, proof/plan/strategy retry distinction | The natural lane repeatedly changes plans or hides the hard step | Diagnostic two-case ablations, expert-reviewed case studies, high cost, and model verification do not establish a general success rate |
| [Autonomous sum-product disproofs](https://arxiv.org/abs/2607.20525) and [code](https://github.com/yichenhuang/sum-product) | Deep plan with precise gaps before construction; light review after a viable proof emerges | One high-leverage route deserves sustained work | Seven of eight trials on one known-true target, about 132.4k reasoning tokens per trial, and no matched-budget ablation |
| [Beyond the Frontier](https://arxiv.org/abs/2605.25143) | Preserve plausible untried historical routes instead of irreversible frontier pruning | A prior route was deferred rather than refuted | Benchmark evidence uses learned PRM scores and token-prefix sampling; route-level memory is only an analogy, not PB-SMC reproduction |
| [Matlas](https://arxiv.org/abs/2604.17484), [TheoremSearch](https://arxiv.org/abs/2602.05216), LeanSearch v2, Lean Finder, and LAMP | Intent-aware candidate retrieval and jointly sufficient premise bundles | A named premise or declaration is missing | Search ranking and extracted text are not source verification or proof |
| [PatternBoost](https://arxiv.org/abs/2411.00566), [AlphaEvolve](https://arxiv.org/abs/2506.13131), MLEvolve, and self-supervised theorem discovery | Diverse candidate generation, local improvement, holdouts, verified intermediate theorem extraction | An executable evaluator exists | Model scores or finite non-failure cannot promote a claim |
| [Peppy](https://openreview.net/forum?id=q7TfzOgGnb) and [PEPFlow](https://github.com/pepflow-lib/PEPFlow) | Numerical-to-symbolic certificate discovery for fixed-algorithm worst-case bounds | The theorem passes the PEP eligibility gate | Fixed-horizon numerics and floating residuals do not prove an all-horizon bound |
| Formal Conjectures, Faults in Formal Benchmarking, hypothesis-lineage work, and Sorries Are Not the Hard Part | Statement fidelity, axiom footprint, semantic obligations, and assembly audit | Any formal artifact is used | Kernel validity is narrower than intended-theorem validity |
| STP, DeepSeek-Prover-V2, process-verified RL, and Goedel-Prover-V2 training results | Evidence that decomposition, verifier feedback, and curated trajectories can improve trained provers | Skill evaluation and future model training | Their learned policies, data, and training gains are not available at inference time here |
| QEDBench, TheoremBench, ComBench, SorryDB, and real-project harnesses | Held-out evaluation, failure taxonomy, project realism, and workflow regression design | Evaluating the skill itself | A benchmark is not a proof tactic and smoke tests do not establish capability gains |

## Evidence Boundaries

- The 57-paper audit rechecked each official arXiv PDF for identity, task, central mechanism, and evaluation boundary. Core architecture papers were additionally checked in their method, experiment or ablation, and limitation sections. This is not a claim that every line of every paper was imported.
- Newer focused reviews use the same gate. QED's front-half controls, the sum-product agent, and Beyond the Frontier were attributed separately to planning, case-study inference, and PRM-guided search rather than blended into one success claim.
- A paper remains in the inventory even when its correct role is negative: training-only evidence, evaluator-only discovery, benchmark design, or a warning against verifier overconfidence.
- AlephProver is an optional external Lean service, not an imported theorem or a local capability. Its output needs the same statement, axiom, dependency, and final-assembly audit.
- SAIR strategies are competition artifacts. Deterministic reductions, replayable witnesses, first-error repair, and verification reserves transfer; leaderboard rank, learned shortcuts, self-reported coverage, and default labels do not.
- EvE's reported paper ablation concerns ICON code search. Its later math-proof configuration and model-generated ratings may schedule experiments but cannot verify mathematics.
- Smoke tests establish schema, budget, state, and routing behavior only. A capability claim needs held-out problems, the same model and budget, blinded evaluation, exact final-assembly scoring, and error analysis.

## Audited Source Inventory

Every arXiv item from the prior source log remains below. The grouping states how it may influence the skill; it is not a quality ranking.

### Direct Runtime And Retrieval Controls

[LeanProgress](https://arxiv.org/abs/2502.17925), [TacMiner](https://arxiv.org/abs/2503.24036), [LeanExplore](https://arxiv.org/abs/2506.11085), [Prover Agent](https://arxiv.org/abs/2506.19923), [Lean Finder](https://arxiv.org/abs/2510.15940), [TheoremSearch](https://arxiv.org/abs/2602.05216), [APRIL](https://arxiv.org/abs/2602.02990), [Learning to Disprove](https://arxiv.org/abs/2603.19514), [Mechanic](https://arxiv.org/abs/2603.24465), [Matlas](https://arxiv.org/abs/2604.17484), [Less Is More](https://arxiv.org/abs/2604.18897), [LeanSearch v2](https://arxiv.org/abs/2605.13137), [OProver](https://arxiv.org/abs/2605.17283), [AXLE](https://arxiv.org/abs/2606.26442), [LAMP](https://arxiv.org/abs/2606.28841), and [OpenProver](https://arxiv.org/abs/2607.09217).

LeanProgress supplies a scheduler signal only. Retrieval systems supply candidates only. Repair systems apply only after the central route survives diagnosis.

### Blueprint, Formal Search, And Project Controls

[DRP-IMO](https://arxiv.org/abs/2507.06804), [Delta Prover](https://arxiv.org/abs/2507.15225), [BFS-Prover-V2](https://arxiv.org/abs/2509.06493), [Hilbert](https://arxiv.org/abs/2509.22819), [Aristotle](https://arxiv.org/abs/2510.01346), [MerLean-Prover](https://arxiv.org/abs/2605.26959), [LEAP](https://arxiv.org/abs/2606.03303), [LeanMarathon](https://arxiv.org/abs/2606.05400), [Beyond the Library](https://arxiv.org/abs/2606.31134), [MechMath Agent Team](https://arxiv.org/abs/2607.04394), [self-modifying Lean agents](https://arxiv.org/abs/2607.17352), and [CircuitProver](https://arxiv.org/abs/2607.27259).

These sources motivate project-mode decomposition, proof-state search, repair radius, typed artifacts, and formal context management. They do not justify putting every natural proof into tree search.

### Evaluator-Backed Discovery And Construction

[PatternBoost](https://arxiv.org/abs/2411.00566), [Beyond Theorem Proving](https://arxiv.org/abs/2505.04528), [AlphaEvolve](https://arxiv.org/abs/2506.13131), [AI-assisted open-problem discovery](https://arxiv.org/abs/2603.04735), [$k$-server-bench](https://arxiv.org/abs/2604.07240), [Discover and Prove](https://arxiv.org/abs/2604.15839), [QED](https://arxiv.org/abs/2604.24021), [Evolutionary Ensemble of Agents](https://arxiv.org/abs/2605.09018), [AlphaProof Nexus](https://arxiv.org/abs/2605.22763), [MLEvolve](https://arxiv.org/abs/2606.06473), [self-supervised theorem discovery](https://arxiv.org/abs/2606.28747), and [From Solvers to Research](https://arxiv.org/abs/2607.07779).

Their general lesson is discover, challenge, then prove. Search is justified only by a frozen representation and a replayable evaluator.

### Verification, Fidelity, And Status Calibration

[Scaling Generative Verifiers](https://arxiv.org/abs/2511.13027), [AI4SLT](https://arxiv.org/abs/2602.02285), [Aletheia](https://arxiv.org/abs/2602.10177), [QEDBench](https://arxiv.org/abs/2602.20629), [SorryDB](https://arxiv.org/abs/2603.02668), [Formal Conjectures](https://arxiv.org/abs/2605.13171), [TheoremBench](https://arxiv.org/abs/2606.09450), [ComBench](https://arxiv.org/abs/2606.10479), [Sorries Are Not the Hard Part](https://arxiv.org/abs/2606.13925), [hypothesis-disciplined formalization](https://arxiv.org/abs/2606.20642), and [Faults in Formal Benchmarking](https://arxiv.org/abs/2606.29493).

These papers calibrate acceptance, statement fidelity, hypothesis lineage, benchmark contamination, and formal trust. They mostly constrain claims about success rather than propose a natural-proof move.

### Training And Data Lessons Only

[Self-play theorem proving](https://arxiv.org/abs/2502.00212), [DeepSeek-Prover-V2](https://arxiv.org/abs/2504.21801), [Goedel-Prover-V2](https://arxiv.org/abs/2508.03613), and [process-verified theorem proving](https://arxiv.org/abs/2606.20068).

Their decomposition, data generation, and process-feedback results matter for future training or evaluation. They are not callable inference-time capabilities of this skill.

### Control And Collaboration Sources

[AI co-mathematician](https://arxiv.org/abs/2605.06651), [STAR-PolyaMath](https://arxiv.org/abs/2605.19338), [QED](https://arxiv.org/abs/2604.24021), the [sum-product agent](https://arxiv.org/abs/2607.20525), and [Beyond the Frontier](https://arxiv.org/abs/2605.25143) supply differently scoped control evidence. Supporting public artifacts include the [EvE repository](https://github.com/scaling-group/eve), [MechMath](https://github.com/MechMath/MechMath-v1), [MechMath Agent Team](https://github.com/MechMath/MechMath-agent-team), the [SAIR Stage 1 leaderboard](https://competition.sair.foundation/competitions/mathematics-distillation-challenge-equational-theories-stage1/leaderboard), the [SAIR Stage 2 network](https://competition.sair.foundation/contributor-network?competition=mathematics-distillation-challenge-equational-theories-stage2), and the [official Stage 2 repository](https://github.com/SAIRcompetition/equational-theories-lean-stage2).

Additional primary sources retained outside the 57-paper arXiv set are [Rethlas](https://arxiv.org/abs/2604.03789), [Goedel-Architect](https://arxiv.org/abs/2606.06468), [APOLLO](https://arxiv.org/abs/2505.05758), [Draft-Sketch-Prove](https://arxiv.org/abs/2210.12283), [LeanArchitect](https://arxiv.org/abs/2601.22554), the [axiom-audited Lean study](https://openreview.net/forum?id=adCv2IV5V3), and [Peppy](https://openreview.net/forum?id=q7TfzOgGnb).
