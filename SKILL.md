---
name: math-research
description: "Discover, repair, refute, or structurally simplify mathematical proofs, especially hard or unknown-answer problems in OR/MS, optimization, probability, learning, games, and economic theory. Use when the missing work is a proof mechanism, construction, valid reduction, or global argument. Use math-proof-writing for exposition along an unchanged mathematical route."
---

# Math Research

Deliver a proof of the exact claim, a valid counterexample, or the first precise unresolved implication. Find the mathematical mechanism and carry it through. Keep project administration out of the argument.

## Fix the target

Read the definitions, domains, assumptions, quantifiers, and conclusion. For a claim from a paper, inspect its surrounding context and any later qualification or solution. Identify what must be proved before choosing a method.

A changed assumption or weaker conclusion is theorem repair. State the original claim's status and the exact change. A counterexample to a proposed lemma or faulty encoding does not refute the original theorem.

Use `math-proof-writing` when the route stays fixed. When the user wants a new structural proof of an already established result, stay here.

## Find a mechanism that closes the argument

Ask: what prevents a counterexample, what happens at equality, and what object makes that relation visible? Use a small case only when it distinguishes plausible explanations.

State the **kernel**: the exact nonroutine implication on which the proof turns. Before pursuing it, check the chain from that implication to every part of the target. An auxiliary lemma must have a reason to exist, a downstream use, and less unresolved work than the theorem it replaces.

Choose the next resource by the missing mathematics:

| Need | Action |
| --- | --- |
| No useful central object | Choose a lens in [proof-idea-generator.md](references/proof-idea-generator.md); formulate one kernel and a decisive falsifier |
| A complete proof is obscured by calculations or cases | Use [structural-proof-compression.md](references/structural-proof-compression.md); derive a replacement mechanism and identify which old obligations disappear |
| A reduction, lifting, or new state representation | Prove the map, its admissible image, and the implication back; use [representation-witness.md](references/representation-witness.md) for nontrivial bridges |
| A likely known premise or transferable proof move | Use [external-proof-pattern-scan.md](references/external-proof-pattern-scan.md); verify the source and assumption match |
| The requested answer is an unknown construction, optimum, or solution set | Use [novel-problem-discovery.md](references/novel-problem-discovery.md); separate validity, completeness, optimality, and novelty |
| Domain-specific guidance | Select the relevant [playbook](references/proof-router.md), not the whole catalog |

If the discovery pass remains generic, `scripts/plan_idea.py "EXACT CLAIM" --discovery` offers a compact set of candidate moves. It generates hints, not new mathematical evidence.

For structural simplification, preserve the old proof until the replacement establishes the same target. Count new definitions, side conditions, and surviving computational leaves. Shorter notation or an equally difficult hidden lemma does not establish simplification.

## Execute, then resolve the first obstruction

Develop one coherent route through the whole claim. On a failed step, identify the exact implication and the missing ingredient. Change representation, retrieve a premise, or compute only when the result would settle that obstruction or reduce it to a smaller one.

| Local question | Useful return |
| --- | --- |
| Is this algebraic, sign, or finite claim correct? | `math-tools` or an available exact tool: inputs, assumptions, replayable result, and implication for the proof. See [tool-assisted checks](references/tool-assisted-proof-patterns.md) |
| Can this stable lemma be formally checked? | `lean-theorem-formalizer`: checked target, axioms, replay, and the remaining parent implication. See [Lean bridge](references/lean-formalization-bridge.md) |
| Does this fixed algorithm admit a performance certificate? | `peppy`, only after the [PEP eligibility gate](references/peppy-proof-bridge.md) |
| Is a genuinely idea-level kernel still missing after local methods? | A bounded [expert consultation](references/expert-consultation.md), if available and authorized; independently check its suggestion |

A useful return proves or refutes a local claim, supplies an applicable premise, exposes a smaller obligation, or rules out a mechanism. More examples, longer prose, renamed objects, and model agreement alone do not count.

Preserve valid work when a route fails. Retry only with an ingredient that addresses the failure. For repeated or nonlocal work, use [proof-state-machine.md](references/proof-state-machine.md); use its scheduler only when route choice itself is the obstacle.

## Verify and deliver

Review the entire candidate against the original target, including boundaries, exceptional parameters, cited premises, and final assembly. Use a fresh-context referee for a hard or suspect argument when available; otherwise identify the check as self-review. The [referee contract](references/prover-verifier-loop.md) separates criticism from coauthoring.

Repair a local error once while the mechanism survives. A failed repair or broken mechanism calls for a new route; repeated failure at the same kernel calls for a new ingredient or an explicit unresolved result. For a correct but unsimplified proof, preserve correctness and report that the simplification goal is still unmet.

Use the [verification gate](references/verification-gate.md) to determine what the evidence supports. In particular:

- A surviving numerical pattern remains a conjecture; a counterexample must satisfy the original assumptions.
- A tool check supports its encoded claim. A local lemma supports the parent only after assembly.
- A model referee is advisory. Formal checking also requires fidelity to the intended statement.

Lead the answer with the mathematical result and its mechanism. Give a complete proof, a replayable counterexample, or the exact gap with one useful next action. State the evidence basis and scope without substituting a status label for the mathematics.

## Execution and durable state

Solve short problems directly. For a hard self-contained task that benefits from separate generation and review, the optional bounded runner is:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/proof_loop.py" \
  path/to/project --claim "EXACT CLAIM" --max-iterations 3 --reasoning-effort high
```

It enforces one repair per route and explicit iteration/time budgets. `--prepare-only` inspects the packet without a model call. Follow [runtime recovery](references/runtime-recovery.md) for references, search, hard exploration, theorem revisions, and interrupted runs. Use `start_proof.py` for a project spanning sessions or dependent lemmas; on resume read the compact runtime brief before old logs.

Load references to answer the current mathematical question. The [research map](references/research-backed-proof-loop.md), [source update](references/ai-math-workflows-2026.md), and [evaluation protocol](references/evaluation.md) are for skill maintenance, not ordinary proof context.
