---
name: math-research
description: "Use for hard, blocked, suspect, previously failed, open, or unknown-answer theoretical problems in OR/MS, dynamic programming, mechanism design, economic theory, learning theory, bandits, online learning, optimization, games, lower bounds, and probabilistic constructions. Use to discover or debug mathematics, find a construction or proof kernel, replace a calculation-heavy complete proof with a structural argument, coordinate mathematical tools, or recover from failed routes. Do not use merely to polish an already complete proof."
---

# Math Research

Own the mathematics, not the ceremony. Start with one natural proof line, keep orchestration in the background, and escalate only at a named obstruction.

Use `math-proof-writing` when the mathematical route stays fixed and the user needs better exposition. Finding a new mechanism that simplifies an existing complete proof belongs here. Use `math-tools`, Lean, Peppy, or literature search only for a specific local question whose answer changes the proof state.

## Invariants

- Preserve the exact variables, domains, assumptions, quantifiers, and conclusion. Label any change as theorem repair.
- Distinguish proof, checked local evidence, plausible pattern, and open gap. A tool or verifier supports only what it actually checked.
- Prefer one motivated route over a portfolio. Branch only after the current route reaches an exact obstruction.
- Admit an auxiliary object or lemma only when its motivation is clear, it is consumed by the route, and it makes the target strictly simpler.
- Do not repeat the same goal, assumptions, central object, and failure witness under new notation.
- A model referee is independent criticism, not formal verification. Lean checks the encoded statement, so statement fidelity and final assembly remain separate gates.

## Natural Proof Loop

### 1. Read the theorem as mathematics

State the exact claim compactly. Check definitions, quantifiers, boundary cases, and whether the claim may be false or missing an assumption. Do not build a project or fill a long acceptance template for an ordinary proof.

For a problem extracted from a paper, read the surrounding definitions and check whether the same source later answers or qualifies it. Freeze the source version only when it affects the target or a cited premise.

### 2. Find the mechanism

When the user asks to replace a calculation-heavy or pieced-together proof, use [structural-proof-compression.md](references/structural-proof-compression.md). Start from one costly block of the old argument, infer the shared relation behind its estimates, and prove a replacement kernel. Keep the old proof until the replacement covers the same claim; shorter prose alone is not a structural improvement. This is an optional discovery task, not a required pass after every proof.

Before drafting, answer three questions:

1. Why might the statement be true?
2. What central object controls the conclusion or its failure?
3. What is the first genuinely nonroutine implication?

Use the negation, the smallest informative case, and the equality or tight case when they clarify these questions. Select one structural lens from [proof-idea-generator.md](references/proof-idea-generator.md) only when the central object is not already visible.

If that compact pass still produces only generic nouns, run one bounded discovery map:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/plan_idea.py" \
  "EXACT CLAIM" --discovery
```

Choose one high-leverage move that matches the obstruction: certificate-first backward design, local-to-global upgrade, abstraction-refinement, bottom-up synthesis, equality-driven construction or algebra, or source-checked proof migration. These are alternatives, not a checklist. Each move must end in an exact kernel and a cheap way to kill it.

### 3. Carry one plan end to end

Write a short blueprint, usually three to seven mathematical steps, then try the entire route. Use a nearby theorem by adapting its proof move and checking every assumption, not by citing a similar-looking statement as a black box.

When changing representation, specify the concrete map and the implication back to the original theorem. When a construction fails, isolate its residual or failed closure property and try one additional invariant or coordinate that repairs it. Use [representation-witness.md](references/representation-witness.md) only if that bridge is nontrivial. A counterexample to a child lemma or an encoding does not by itself refute the original claim.

Do not open alternative routes merely because they exist. Stop at the first exact obstruction and name the failed implication, missing premise, counterexample shape, or unavailable construction.

### 4. Escalate one obstruction

Choose one action from the table. Do not load several modules at once.

| Obstruction | Next action |
| --- | --- |
| Claim may be false | Construct and replay a smallest counterexample |
| Central object is missing | Use one structural-discovery lens or one close proof-pattern search |
| A known premise may exist | Query Matlas or TheoremSearch, then check the source and assumptions |
| A cited tool certificate is missing or stale | Replay that exact artifact and recheck its local claim |
| Local algebra or signs are unclear | Ask Wolfram or SymPy for an exact identity, condition set, or witness |
| A finite or combinatorial leaf is unclear | Use Python, Z3, Sage, NetworkX, or an optimization certificate |
| One stable lemma is fragile | Run a local Lean handoff or a focused independent check |
| A genuinely idea-level local kernel remains stuck | Make one bounded expert consultation if an approved provider is available |
| A complete proof exists | Send the whole candidate to a fresh-context referee |
| The same obstruction appears twice | Change representation or retire the route; do not patch it again |

The returned artifact must either close/refute a local claim, reveal a smaller subgoal, supply a source-checked premise, or justify changing route. Otherwise it is not progress.

Treat expert consultation as a search operator, never as a verifier. Use it only after naming the exact local kernel and showing why retrieval, CAS, finite search, or formalization does not directly decide it. Read [expert-consultation.md](references/expert-consultation.md), send one compact packet, and allow at most one follow-up when the first answer supplies a new checkable kernel. Do not resend an unchanged proof state. Any returned idea has `proof_effect=none` until independently reconstructed or checked.

### 5. Verify, repair once, then replan

Check the complete candidate for the earliest fatal error. For a hard or suspect argument, use a fresh-context referee when available and permitted; give it only the exact claim, candidate, selected premises, and necessary evidence. Otherwise perform a distinct adversarial pass and identify it as self-review. Unavailable delegation does not block a self-contained proof. See [prover-verifier-loop.md](references/prover-verifier-loop.md) for the referee contract.

- If the first error is local and the central mechanism survives, repair it once and recheck the complete proof.
- If it attacks the central object, a theorem assumption, or the main assembly, start a fresh plan without the failed derivation.
- If two materially different plans reach the same kernel, report that kernel as the obstruction and retrieve, tool-check, repair the theorem, or stop honestly.

### 6. Finish cleanly

Present a paper-style proof or a precise obstruction. Keep route boards, tool logs, verifier packets, and project state out of the visible proof unless the user needs them to assess correctness.

## Executable Proof Loop

For a hard but self-contained problem, use the bounded generator-referee runner instead of simulating both roles in one context:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/proof_loop.py" \
  path/to/proof_project --claim "EXACT CLAIM" --max-iterations 3 --reasoning-effort high
```

The runner creates a minimal project when needed, gives each generator a compact packet, sends complete candidates to a fresh-context referee, permits at most one local repair before replanning, fingerprints failed routes, and stops on acceptance, a requested external capability, or its wall-time/iteration budget. When the claim has one clear domain classification, the packet also carries one compact domain seed with candidate objects and kernels. It is a search hint with `proof_effect=none`; discard it when its assumptions do not fit.

Use `--prepare-only` to inspect the pending packet without invoking another model. Add `--allow-search` only for a public or safely abstracted statement; otherwise retrieval remains an explicit outer action. Model acceptance is `referee-accepted`, with explicit evidence basis and scope; it does not record human review or formal certification.

Use `--reasoning-effort max` only for a genuinely hard kernel after the high-effort route has been inspected; iteration and wall-time budgets still apply.

The checkpoint preserves the theorem and acceptance contract, selected plan, pending repair or verification, first error, artifact hashes, and cumulative call/time counts. A new invocation grants more computation to the same mathematical action. Use `--fresh-attempt` only to intentionally restart execution; history and cumulative counts remain. Reuse completion only when the claim, contract, candidate, referee packet/report, and references still match. Changed obligations require another review; duplicate scout routes do not constitute mathematical failures.

When the runner returns `needs-evidence`, satisfy only its named request with `math-tools`, retrieval, Lean, or a bounded expert consultation, save the artifact inside the project, and resume with `--reference path/to/artifact`. Repeating the command without new evidence preserves the waiting route and makes no new model call. A changed reference must be supplied explicitly and checked again. See [runtime recovery](references/runtime-recovery.md) when recovering an older project.

### Hard exploration

Do not use this on the first attempt. Activate it after two materially different routes fail, or when a serious attempt still cannot identify a central object or conditional assembly:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/proof_loop.py" \
  path/to/proof_project --hard-exploration --max-iterations 3 --reasoning-effort high
```

This adds at most two independent route scouts and one fresh plan selector before the ordinary loop. Scouts do not see one another. The selector may choose only a supplied route, marks one `key_original_step`, and cannot certify it. A selected route is not rediscovered on the next run; plausible untried routes remain in a three-item historical pool. Stop if no route passes the assembly gate or one named external capability is required. Do not combine this mode with broad speculative search.

## Durable Project Mode

Use the heavier project system only when the proof spans sessions, depends on several lemmas or tools, has already failed twice, or needs an auditable research record:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/start_proof.py" \
  --title "SHORT NAME" --claim "EXACT CLAIM"
python3 "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/proof_doctor.py" \
  path/to/project
```

Use `--mode recovery` after prior failures and `--mode discovery` only when the answer or central object is genuinely unknown. On resume, read the compact `.proof_runtime` brief before older ledger material.

In project mode, the detailed state machine, route scheduler, decomposition admission, evidence replay, and frontier controls remain available. They are safeguards for durable work, not the default way to think about a theorem.

## Specialist Returns

Keep one proof owner. Delegate one named artifact and require a status-preserving return:

| Specialist | Return |
| --- | --- |
| `math-tools` | Local claim, assumptions, command, exact artifact, and scope |
| `lean-theorem-formalizer` | Frozen target, replay result, axioms, and local/global status |
| `peppy` | Exact encoding, certificate scope, and missing theorem mapping |
| Expert consultant | One candidate kernel or refutation, assumption map, decisive check, and unresolved gap; `proof_effect=none` |
| `math-proof-writing` | Polished exposition with inherited gaps unchanged |

## Reference Router

Read at most one process reference and one domain playbook for the current decision.

- Missing central object or clever construction: [proof-idea-generator.md](references/proof-idea-generator.md); if its compact pass stays generic, run `plan_idea.py "EXACT CLAIM" --discovery` once before hard exploration
- Structural simplification of an existing proof: [structural-proof-compression.md](references/structural-proof-compression.md)
- Repeated route or long project: [proof-state-machine.md](references/proof-state-machine.md), then [strategy-scheduler.md](references/strategy-scheduler.md) only if routes truly compete
- Literature premise or proof migration: [external-proof-pattern-scan.md](references/external-proof-pattern-scan.md)
- Natural-language verification: [prover-verifier-loop.md](references/prover-verifier-loop.md)
- CAS, SMT, optimization, or exact computation: [tool-assisted-proof-patterns.md](references/tool-assisted-proof-patterns.md)
- Nontrivial reduction, encoding, or failed construction: [representation-witness.md](references/representation-witness.md)
- Stuck idea-level kernel after local methods are exhausted: [expert-consultation.md](references/expert-consultation.md)
- Lean handoff: [lean-formalization-bridge.md](references/lean-formalization-bridge.md)
- Fixed-algorithm PEP or Lyapunov certificate: [peppy-proof-bridge.md](references/peppy-proof-bridge.md)
- Unknown/open-answer frontier: [novel-problem-discovery.md](references/novel-problem-discovery.md)
- Research provenance and method maintenance only: [ai-math-workflows-2026.md](references/ai-math-workflows-2026.md), with the earlier [research map](references/research-backed-proof-loop.md); do not load these during ordinary proving

Choose at most one domain playbook: optimization/OR, DP, mechanism design, games/matching, learning theory, bandits/OCO, lower bounds, or probabilistic method.

## Evidence Boundary

- Matlas and TheoremSearch return candidates, not proof authority. Verify metadata, definitions, assumptions, and the source argument.
- Simulations and bounded searches can refute or guide; failure to find a witness is not a proof.
- CAS and solver output becomes proof evidence only after its exact inputs, assumptions, and result are replayable.
- A locally checked lemma does not prove its parent until the dependency path is assembled.
- Preserve solved lemmas and checked artifacts. Repair only the first failed node and affected dependents.

## Output Contract

Report the mathematical outcome, evidence basis, and scope separately: for example, a full candidate accepted by a model referee, an exact counterexample to one lemma, a formally checked original theorem, or a conditional result with a named gap. Include the decisive mechanism and essential assumptions. If unresolved, name the first exact obstruction and one bounded next action. Use [verification-gate.md](references/verification-gate.md) for four core checks plus only the relevant conditional checks.
