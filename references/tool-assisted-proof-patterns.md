# Tool-Assisted Proof Patterns

Use a tool when its output can settle a named local obligation: an exact identity, admissible counterexample, condition set, or checkable certificate. A computation that only makes the claim look plausible remains discovery evidence.

## Map

Choose by artifact, translate the result, and preserve a replay when the proof depends on it. Specialized formal and PEP mechanics live in their bridges.

## Imported Patterns

The useful common pattern is **small claim → typed artifact → independent check → theorem implication**. A blueprint identifies the current dependency; a certificate makes the output inspectable; a replay preserves the checked computation. These roles do not require importing a paper's entire search system. See [research sources](research-backed-proof-loop.md) for provenance and limits.

## Tool Roles

| Needed artifact | Suitable backend | What still needs proof |
| --- | --- | --- |
| Algebraic identity, quantified conditions, symbolic witness | Wolfram; SymPy or exact Python for supported algebra | Domains, branch/boundary conditions, and theorem implication. |
| Finite/integer/Boolean witness or infeasibility result | Z3, cvc5, PySAT | Encoding fidelity and the solver's actual theory/certificate scope. |
| Optimization witness or primal/dual certificate | CVXPy, OR-Tools | Exact feasibility, signs, global validity, and certificate verification. |
| Exact combinatorial/algebraic calculation | Sage, flint, gmpy2, exact Python | What the enumerated class covers. |
| Fixed-algorithm worst-case or Lyapunov certificate | [Peppy/PEPFlow bridge](peppy-proof-bridge.md) | Eligibility, interpolation, exactness, all-horizon identity, and assembly. |
| Stable formal lemma | [Lean bridge](lean-formalization-bridge.md) | Frozen target, environment/axiom audit, and parent assembly. |
| Numerical behavior or rate pattern | Simulation or numerical solver | General statement; floating agreement alone does not prove it. |

## Tool Plan Template

Before a proof-critical call, identify the local claim and assumptions, requested artifact, expected theorem implication, and failure interpretation. In durable mode save the command/script and evidence reference in the existing tool plan; no second report is needed.

## Default Tool Loop

1. Make the local claim exact. Use its negation or smallest informative boundary when falsification would distinguish routes.
2. Choose the artifact before the backend. Query the narrowest obligation whose outcome changes the proof.
3. If discovering a formula, infer it from informative cases and challenge it on a withheld case. For sequence inference, `scripts/pattern_miner.py` is available. Generality still needs an indexed proof.
4. Translate the output using the table below. Check a proof-bearing certificate independently, preferably with simpler arithmetic or a different derivation rather than the same search.
5. Preserve the replay if the argument depends on the computation. On failure, isolate the first invalid step and return to [escalation routing](proof-escalation-protocol.md).

## Replayable Computation

Keep proof-critical code in a project-local `.py`, `.wl`, `.wls`, `.sage`, or `.lean` file. The recorder rejects inline expressions. Probe the backend and record its version before the first proof-critical call in a run: activation failure, timeout, or a nonzero exit—even after printed output—is a process failure.

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

python3 scripts/computation_artifact.py replay path/to/project ARTIFACT_ID
python3 scripts/computation_artifact.py audit path/to/project ARTIFACT_ID
```

For Python use its actual version, `--backend Python`, a direct script command such as `["python3","tool_checks/L3.py"]`, and the script as `--input`. Standard/versioned Python executables and `codex-math-python` are accepted; `-c` and `-m` are not recorded script entrypoints. Virtual environments preserve the invoked path while fingerprinting the resolved binary.

The replay boundary is specific:

- No shell; only named math backends with an installed executable outside the proof project. A timeout cleans up the process group. The runner executes trusted project scripts; it is not a hostile-code sandbox.
- Input and executable fingerprints are checked before and after replay. Changed inputs, expected output, artifact specification, or theorem revision cannot pass. A mid-run edited artifact is preserved and rejected, and a revised theorem cannot receive the old replay.
- `audit` checks project locality, hashes, latest replay files, and the matching runtime event. A copied JSON summary or stale event is not live evidence.
- Exact counterexamples, identities, condition sets, and solver certificates require canonical expected stdout. `exit-only` is limited to exploration, unclassified runs, or formal-tool process checks; it establishes no mathematical output.
- Numerical evidence stays conjectural. Symbolic, solver, and formal outputs still need their mathematical translation and the relevant independent check.

Record every command-named file with `--input`, including secondary scripts/data and `--option=path`. Also record imported modules, files opened inside code, and environment dependencies explicitly; the runner does not discover them. Keep generated outputs separate from command arguments interpreted as inputs.

To replace a stale artifact, record and replay the replacement first, then use:

```bash
python3 scripts/computation_artifact.py supersede PROJECT OLD_ID \
  --replacement NEW_ID --reason "COVERAGE ARGUMENT"
```

The replacement must currently pass and match project claim, local claim ID/text, assumptions, result kind, and comparison mode. The old immutable specification must remain verifiable. A different lemma needs an explicit derivation of the old claim; the coverage reason itself still needs mathematical inspection.

An aggregate checker must fail on every child timeout, nonzero exit, expected-output mismatch, or unexpected stderr, and propagate nonzero status. Record its manifest, children, expected output, and driver. A summary token alone cannot certify the conjunction.

Within a diagnosis, the runtime indexes computation history once; it discards the index between diagnoses or if history changes. Current input, output, and executable checks still apply per artifact.

## Artifact Translation

| Returned output | Legitimate conclusion |
| --- | --- |
| Admissible model of the negation | The encoded target is false. Original-theorem refutation additionally checks every original assumption and the conclusion. |
| Empty witness search | No witness in the completed search scope. Claim a quantified result only when the backend establishes that scope completely. |
| `Reduce`/`Resolve` conditions | Candidate assumptions or case split to interpret and prove applicable. |
| Exact simplification under assumptions | The stated algebraic identity/inequality is checked under those assumptions; expose it as a lemma. |
| Numerical optimum | Candidate active constraints or witness; reconstruct and verify exact feasibility/duality or a global argument. |
| Feasible LP/MIP/SMT model | Candidate witness; verify constraints and intended interpretation. |
| Dual variables or Bellman inequalities | Local certificate after checking feasibility, sign, direction, and theorem mapping. |
| Peppy rate pattern | Conjecture until an exact finite certificate or general Lyapunov identity is established. |
| Lean target passes intended-file replay | Checked encoded target at the bridge's scope; helpers alone leave parent assembly open. |
| Failure or timeout | Diagnostic information, not mathematical refutation. Inspect the first failed obligation. |

## Domain Recipes

Use the relevant [domain playbook](proof-router.md). The tool should resolve its missing obligation: Bellman inequalities for a candidate policy, deviations/payment feasibility for IC, event and summation bounds for regret, or feasible indistinguishable instances for a lower bound. Do not force every optimization proof through KKT or every recurrence through PEP.

## Stop Rules

After two timeouts, shrink the target or change artifact type. If tools disagree, inspect domains, precision, branch cuts, and boundary assumptions. If no output can enter a derivation, report the remaining lemma or return to discovery; do not accumulate successful runs as proof evidence.

## Source Patterns

The blueprint and scoped formalization pattern appears in Lean/mathlib and the Liquid Tensor Experiment; checked external computation is central to Flyspeck. Wolfram's `FindInstance`, `Reduce`, `Resolve`, and assumption-aware simplification provide distinct artifact types. These precedents motivate the division of work; their success does not certify a new encoding.
