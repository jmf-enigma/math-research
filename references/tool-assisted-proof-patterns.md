# Tool-Assisted Proof Patterns

Use this for hard proofs where computation, CAS, SMT, optimization solvers, or Lean may help. The goal is not to "ask tools for a proof"; it is to turn tool output into a smaller human-checkable lemma, certificate, counterexample, or theorem repair.

## Map

- Imported patterns and tool roles: choose the backend by expected artifact.
- Tool plan and default loop: refute, shrink, run the narrowest query, translate.
- Artifact translation and replay: convert output into a proof step or repair, then preserve proof-critical runs.
- Stop rules: avoid trusting numerical evidence or repeated timeouts.

## Imported Patterns

- **Lean/Goedel blueprint pattern**: maintain a human-readable proof map and a machine-checkable or reviewer-checkable dependency graph. Each node has a statement, statement dependencies, proof dependencies, downstream use, status, and failure diagnosis. Prove or check ready leaves on the current theorem path before side lemmas unless explicitly rewiring the graph.
- **Cost-aware tool routing**: after repeated failed tool or Lean attempts, decide whether the next run has positive value. Continue only if the expected artifact is new: counterexample, exact condition, certificate, smaller subgoal, retrieved premise, or theorem repair.
- **Flyspeck pattern**: combine a human proof with formal verification and external computations only when every computational step has a checked certificate or proof object.
- **CAS refutation pattern**: under the claim's explicit assumptions and domains, ask for a satisfying instance of its negation. Identify whether the claim is the original theorem, a child lemma, or an encoding.
- **Certificate pattern**: prefer certificates that can be independently checked: dual variables, KKT conditions, exact rational identities, interval bounds, SMT models/unsat cores, or Lean proof terms.
- **Rethlas-style replay pattern**: keep computation outside the prose transcript. Save the exact local claim, assumptions, backend and version, script hashes, executable fingerprint, output comparator, evidence level, and replay result so a verifier can inspect the same artifact.
- **Premise-retrieval pattern**: when a lemma feels standard, search for the nearest theorem pattern or library lemma before inventing a new proof.
- **Global-premise pattern**: for a multi-step route, retrieve premises by proof-sketch subqueries and judge the set jointly. A topically similar theorem that cannot enter the assembly is not useful retrieval.
- **Repair-loop pattern**: when a tool rejects a step, preserve the failed subgoal, extract the smallest missing lemma, then retry only that lemma.
- **Sorrify/localize pattern**: when a skeleton is promising, replace the failed block with a named lemma, keep the good dependencies, and repair only that lemma.
- **Compact-feedback pattern**: after a tool or Lean failure, keep the next repair input small: node statement, assumptions, dependencies, previous attempt, feedback, and proposed fix.
- **Aristotle formal-feedback pattern**: use Lean feedback as a hard proof-state signal. Search or repair one state at a time, keep an action history, merge equivalent states, preserve verified helper lemmas, and prioritize the hardest required subgoal in an AND branch.
- **Formal artifact audit pattern**: a Lean/API result is not a completed proof if the main theorem still contains `sorry`, admits extra axioms, or relies on an unencoded global assembly step. Treat such output as verified local components plus explicit missing obligations.
- **Library-coverage boundary**: before heavy formal search, inventory whether the required definitions and prerequisite theory exist. Never replace missing mathematics with dummy structures, fake instances, or unproved axioms merely to make a file type-check.

## Tool Roles

- **Wolfram**: symbolic simplification, quantifier elimination, condition discovery, inequality checks, FOCs/KKT algebra, counterexample search with `FindInstance`.
- **Python/SymPy/flint/gmpy2**: exact rational algebra, polynomial coefficient checks, finite stress tests, high-precision sanity checks.
- **Z3/cvc5/PySAT**: finite/integer/Boolean counterexamples, IC/IR feasibility, small-model search, discrete impossibility.
- **CVXPy/OR-Tools**: primal/dual optimization sanity checks, finite LP/MIP certificates, policy/capacity/matching counterexamples.
- **Peppy/PEPFlow**: worst-case rates, PEP dual certificates, and Lyapunov discovery for exactly encoded fixed first-order or operator algorithms; use [peppy-proof-bridge.md](peppy-proof-bridge.md) before invoking it.
- **Sage**: exact combinatorics, graph/algebra/finite-field/group computations.
- **Lean/mathlib**: use the live goal/search/multi-attempt lane for bounded local repair, then replay the winning script in the intended file and return a typed bridge result. It formalizes stable nodes; it does not own theorem discovery or global assembly.
- **Empirical/simulation tools**: falsification and sanity checks only; they do not prove universal claims.

## Tool Plan Template

For each proof-critical step, write:

- lemma or claim fragment:
- assumptions/domains:
- negation to test:
- backend:
- query or script:
- expected artifact: counterexample, `True`, conditions, dual certificate, unsat result, exact identity, Lean proof.
- how the artifact becomes a proof step:
- failure interpretation:
- compact repair state if the step fails:

If the expected artifact is only "numerical evidence," the step is not proof-ready.

## Default Tool Loop

1. **Normalize** the claim: remove ambiguous notation, name domains, list boundary cases.
2. **Refute first**: test the negation in the smallest admissible scalar, finite, or boundary model. A relaxed-assumption test diagnoses that assumption; its witness refutes the original claim only if all original assumptions still hold.
3. **Guess a pattern if needed**: use exact small cases, active sets, coefficient sequences, symbolic simplification, or optimized witnesses to infer a construction, invariant, or algebra normal form. If the evidence is a sequence, run `scripts/pattern_miner.py` before treating the guess as a candidate lemma.
4. **Hold out a case**: test at least one small case that was not used to guess the pattern.
5. **Shrink** the theorem into one or more tool-checkable lemmas.
6. **Pick artifact type** before running the tool.
7. **Run the narrowest query**: avoid global simplification on a full theorem. For multiple candidate lemmas, try the hardest boundary case or the most certificate-friendly subgoal first.
8. **Translate** tool output into a lemma, missing assumption, counterexample, or certificate.
9. **Independently check** proof-critical artifacts when feasible: symbolic plus numeric, CAS plus exact arithmetic, LP solution plus dual certificate, informal proof plus Lean.
10. **Record** command, assumptions, result, and translation in `TOOL_PLAN.md` and `LEDGER.md`. For a proof-critical run, also create and replay a machine-readable artifact before upgrading proof status.
11. **Local repair** if the check fails: preserve any proved parent nodes, isolate the first false or too-hard block, and retry only after adding a new parent, repaired statement, counterexample, theorem pattern, or certificate.

## Replayable Computation

Keep the computation in a project-local `.py`, `.wl`, `.wls`, `.sage`, or `.lean` file. Inline expressions are suitable for exploration but are deliberately rejected by the replay recorder. A minimal Wolfram-backed record is:

Before the first proof-critical call in a run, execute a minimal backend probe and record its version. An activation error, nonzero exit, timeout, or printed result followed by a nonzero exit is a backend failure, not mathematical evidence. Repair or reroute the backend before recording the claim artifact.

```bash
python3 scripts/computation_artifact.py record path/to/project \
  --claim-id L3 --local-claim "EXACT LOCAL CLAIM" \
  --assumption "x is real and x > 0" \
  --backend Wolfram --backend-version "ENGINE VERSION" \
  --result-kind symbolic-identity \
  --command-json '["codex-wmath","-file","tool_checks/L3.wl"]' \
  --input tool_checks/L3.wl \
  --compare stdout-exact \
  --expected-output tool_checks/L3.expected.txt \
  --proof-translation "HOW THIS OUTPUT ENTERS THE PROOF"
```

Replay the returned artifact id with:

```bash
python3 scripts/computation_artifact.py replay path/to/project ARTIFACT_ID
python3 scripts/computation_artifact.py audit path/to/project ARTIFACT_ID
```

The runner uses no shell, allows only named math backends, requires an installed executable outside the project, verifies input and executable fingerprints, applies a timeout with process-group cleanup, and records stdout and stderr. `audit` additionally checks that the artifact still lives in the current project, its hashes and latest replay files agree, and its latest passed replay has a matching runtime event. A copied JSON summary or stale ledger event is not a live artifact. It executes trusted proof-project scripts; it is an audit and replay boundary, not a sandbox for hostile code. Exact counterexamples, symbolic identities, condition sets, and solver certificates must match a canonical expected stdout; `exit-only` is retained only for numerical exploration, unclassified runs, or formal-tool process checks and never establishes a mathematical output by itself. `numerical-evidence` remains conjectural, and every symbolic, solver, or formal result remains a candidate artifact until translated and independently checked.

Record every command-named file dependency with `--input`, including secondary scripts, data files, and paths supplied as `--option=path`. Imported modules, files opened inside scripts, and backend environment dependencies still need an explicit input or environment record; the runner does not discover those automatically. Keep generated outputs distinct from command arguments treated as input files.

When a new artifact covers the same local claim, record and replay it first, then preserve the append-only history with `computation_artifact.py supersede PROJECT OLD_ID --replacement NEW_ID --reason "COVERAGE ARGUMENT"`. The replacement must be currently valid and match the recorded project claim, local claim ID/text, assumptions, result kind, and comparison mode. Stale inputs or replays may be replaced; the old immutable specification must remain verifiable. A result for a different lemma needs a separate explicit derivation of the old claim before it can count as coverage. The reason still requires mathematical inspection.

For an aggregate checker, do not trust a final summary token alone. The driver must reject every child timeout, nonzero exit, exact-output mismatch, and unexpected child stderr, then exit nonzero itself. Record the manifest, all child scripts, canonical expected output, and the driver as inputs. This makes a batch pass an auditable conjunction of local checks rather than a wrapper that can hide a failed child.

## Artifact Translation

- `FindInstance` returns an admissible witness to the negation: the exact encoded claim is false. A witness against a child lemma or encoding refutes only that target; an original-theorem refutation must satisfy every original assumption and violate its conclusion.
- `FindInstance` returns `{}`: no counterexample found in that theory/search scope; not a proof unless the backend solved the quantified formula completely.
- `Reduce`/`Resolve` gives conditions: these are candidate assumptions or case splits, not prose by themselves.
- `FullSimplify[..., assumptions] == True`: a proof-critical algebraic step is strongly checked under those assumptions; still state the algebraic lemma.
- Numerical optimizer returns a solution: use it to guess active constraints, then prove KKT/duality/convexity or construct an exact certificate.
- LP/MIP/SMT feasible model: use it as a counterexample or witness.
- LP dual variables or Bellman inequalities: convert to a certificate that a human can verify line by line.
- Peppy Block 1 returns a rate pattern: keep it as a conjecture. Later blocks may supply a finite-horizon dual certificate or an all-horizon Lyapunov identity, but only the exact artifact and its theorem mapping enter the proof.
- Lean accepts a lemma through final file replay: status becomes `formalized-local`; still explain how the lemma fits the paper proof. A live MCP or REPL pass alone does not promote status.
- Lean/API returns several verified helper lemmas but leaves the theorem open: keep the helpers, mark the theorem `lemma-conditional` or `still open`, and encode the missing global assembly lemma before claiming success.
- Lean fails: inspect the failed subgoal; often it reveals a missing assumption, coercion/domain issue, or too-strong statement.
- Tool returns a counterexample to a sublemma: mark the node `false-negated`; repair/drop it and rewire dependents instead of regenerating the whole proof.
- Tool times out or gives no useful artifact: classify the gap. If the missing lemma is a bad gap, switch to discovery/retrieval before more tool calls.

## Domain Recipes

### Optimization / OR/MS

- Use tools to guess active sets, simplify KKT conditions, and search boundary failures.
- For fixed-algorithm worst-case rates, apply the Peppy eligibility gate; do not force a general optimization theorem into a PEP encoding.
- Final proof needs convexity/concavity, constraint qualification, feasibility, and a primal-dual/KKT certificate.
- For nonconvex problems, numerical optima are only conjecture generators unless paired with a global argument.

### Dynamic Programming / MDP

- Use finite-state Python/LP to test Bellman inequalities and policy structure.
- Use Wolfram for Q-value difference signs and threshold boundaries.
- Final proof needs Bellman equality for the candidate policy and Bellman inequality for deviations, with boundary/tie cases.

### Mechanism Design / Econ

- Use finite type grids and LP/Z3 for IC/IR feasibility and deviation search.
- Use Wolfram for envelope derivatives, virtual values, and payoff differences.
- Final proof needs monotonicity/cyclic monotonicity, payment construction, and boundary IR.

### Learning Theory / Bandits

- Use Python to stress-test finite horizons and constants; use Wolfram/SymPy for summation and tuning.
- Use Lean only for stable local inequalities or algebraic lemmas.
- Final proof needs a named good event, failure probability, instantaneous bound, summation/telescope, and exact quantifier type.

### Lower Bounds

- Use tools to tune hard instances and KL/TV expressions.
- Final proof needs feasible instances, closeness bound, separation bound, and testing-to-risk transfer.

## Stop Rules

- If a tool query times out twice, shrink the lemma or change artifact type.
- If two tools disagree, inspect domains, numeric precision, branch cuts, and boundary assumptions before trusting either.
- If the same missing assumption appears in two tool outputs, repair the theorem statement before drafting prose.
- If no artifact can be translated into a proof step, report `still open` with the smallest remaining lemma.
- If Lean compiles only because of `sorry`, an admitted axiom, or an unproved theorem dependency, do not upgrade status beyond `lemma-conditional` or `formalized-local`.

## Source Patterns

- Lean/mathlib projects: blueprint, premise retrieval, local formalization, proof-state repair.
- Liquid Tensor Experiment: human-readable blueprint linked to Lean formalization.
- Flyspeck/Kepler: formal proof plus checked external computation and nonlinear inequality certification.
- Wolfram theorem proving: `FindInstance`, `Reduce`, `Resolve`, and simplification under explicit assumptions.
