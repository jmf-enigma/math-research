# Lean Formalization Bridge

Use when a node's mathematics is stable enough to formalize. The bridge freezes a request and returns a replayable result for that encoded target.

## Escalation Gate

Require an exact statement, domains/assumptions, dependencies, downstream use, namespace-qualified Lean target, and role: `local-lemma`, `interface-theorem`, or `full-theorem`. Resolve semantic ambiguity before encoding. Keep changing objects and proof discovery in Math Research.

## Vocabulary Gate

For a project-specific definition, state its intended meaning and check a positive witness/constructor, an exclusion or boundary, and the properties consumed downstream. Inspect these independently of the main proof. Empty, vacuous, over-strong, or shifted definitions fail fidelity even if compilation succeeds.

Replay repairs against the frozen original declaration. A changed definition, type, or statement needs recorded lineage and a new request.

## Prepare A Request

```bash
codex-math-python "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/lean_bridge.py" prepare PROJECT \
  --node-id L3 \
  --role local-lemma \
  --statement-file lemmas/L3.md \
  --lean-file lean/LocalLemmas.lean \
  --target-name Project.L3 \
  --target-kind lemma \
  --dependency L1 \
  --dependency L2 \
  --downstream-use "closes the monotonicity step"
```

The immutable request in `lean/handoffs/` binds the claim hash/revision, node statement, file-backed statement path/hash, dependencies, target, and fidelity notes. Relative statement paths resolve inside the project; `packet_sha256` detects edits. Prepare a new request when the claim or node changes.

A `full-theorem` request also creates an acceptance report:

| Gate | Required evidence |
| --- | --- |
| `claim_fidelity` | The checked target has the same force as the original claim. |
| `assumption_lineage` | Every added assumption is sourced, derived, an explicit interface, or declared theorem repair. |
| `assembly_coverage` | Required children and edge cases reach the final target. |
| `axiom_audit` | Dependencies use only accepted foundational/project axioms. |

All begin `not-audited`. Compilation cannot fill them. The report's `target_binding` hashes the target, project-local Lean sources, and Lean/Lake configuration; a change resets every gate. For a legacy report without a binding, verify to initialize it, inspect the current target/dependencies, fill the gates with evidence, then verify with `--promote-final`. Historical result packets retain the old audit.

The binding excludes generated `.lake` caches. Pin external dependencies in configuration and inspect their actual environment during the axiom audit; local hashes do not certify a modified package cache.

## Interactive Fast Lane

When Lean MCP tools are available, iterate only on the target file while keeping the request immutable. Use `lean_goal`, `lean_local_search`, a bounded set of materially different `lean_multi_attempt` snippets, `lean_code_actions`, and diagnostics as needed. Reserve `lean_run_code` for self-contained elaboration experiments and `lean_verify` for axiom/source inspection.

This is scratch and repair, not promotion. Experimental REPL rejection is provisional; success covers only the tested state. Write the surviving script into the intended file and run the exact bridge verifier. Repeated states or fidelity/mathematical/assembly failures return to Math Research.

## Formal Failure Surgery

Use only for a frozen target with a coherent skeleton and a remaining local proof-block failure. Parse, import, type, premise, fidelity, mathematical, and assembly failures return to their own layer.

1. Locate the first primary diagnostic and smallest enclosing structured block. Replace only a failed `have`/`replace` body; treat a failing `calc`/`choose` as one block. If parsing failed, cut only at the diagnostic. Recompile after each edit; later errors may be cascades.
2. Temporary `sorry` placeholders may isolate failures within the repair budget. “Valid allowing `sorry`” salvages a skeleton; it proves no child or parent.
3. Extract each isolated goal with all variables, hypotheses, typeclasses, imports, and parent use. Removing a hypothesis requires both the child and reassembly to remain faithful.
4. Check well-formedness, then semantic entailment from the frozen context and the reassembly interface. Extraction can faithfully isolate a false step.
5. Recurse only on a strictly simpler validated child. Stop on a child equivalent to its parent, a repeated failure fingerprint, or no smaller remaining obligation.
6. Reinsert a verified child and replay the frozen parent; audit admissions, axioms, fidelity, lineage, and coverage again.

On the first classified local-proof failure, `lean_bridge.py verify` records this policy in `formal_failure_surgery`; a repeated identical failure returns ownership to Math Research.

Remote extraction/checking is optional for a suitable single-file target. Use it only when existing user authorization covers sharing that source. A remote result does not replace the bridge's four gates; record service limitations or differences from the intended verifier.

## Verify And Return

```bash
codex-math-python "${CODEX_HOME:-$HOME/.codex}/skills/math-research/scripts/lean_bridge.py" verify PROJECT \
  lean/handoffs/REQUEST.request.json \
  --runner auto
```

The companion `lean-theorem-formalizer` checker must affirm compilation, absence of blockers, and the exact declaration. The bridge compares source/configuration hashes before and after checking, revalidates the file-backed statement and claim revision, writes a unique result, and appends it to `.proof_runtime`. Missing checker fields or changed inputs cannot pass.

Use `--failure-stage statement-fidelity`, `mathematical`, or `assembly` for nonlocal failures. `--diagnosis` records a root cause grounded in the preserved diagnostic; `--repair` names one bounded next edit.

## Ownership Rule

| Result | Next action |
| --- | --- |
| Exact node passes | Assemble its downstream use at the checked scope. |
| First parse/import/type/premise/local-proof failure | Lean formalizer repairs once. |
| Same failure class, site, and diagnostic repeat | Math Research retrieves, re-decomposes, or audits the statement. |
| Fidelity/mathematical/assembly failure | Math Research immediately. |
| Full theorem compiles but an acceptance gate is missing | Complete the audit; status stays below complete. |

`formalized-local` applies only to the checked node. `--promote-final` requires a `full-theorem` request and all four gates. Tampering, stale claim revision, missing target, placeholders, target-encoding axioms, or incomplete acceptance blocks promotion.

A failed recheck of the request supplying completion, or stale acceptance gates, revokes that active completion. The doctor checks current sources, checker, request, acceptance report, and runtime provenance. Recheck legacy records without provenance; corrupt records remain blockers.

During nonfinal work a named mathematical repair or premise search may precede replay of a failed node. Its evidence remains invalid until checked again.

## Return Packet

Preserve the checker command/exit, request/source hashes, target status, raw diagnostic/site, failure class/fingerprint, root-cause judgment, proposed repair, change in remaining obligations, prior identical failures, repair contract if applicable, next owner, and promotion eligibility.

The result certifies only its encoded target and stated trust basis. The parent remains conditional until its required dependency path and acceptance obligations are discharged.
