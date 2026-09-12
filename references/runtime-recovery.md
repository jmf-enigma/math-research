# Proof-loop recovery

Use for a multi-session run, missing evidence, an interrupted process, or migration of an older project. Commands below assume the skill directory is the working directory and Python 3.10+ is available.

```bash
python3 scripts/proof_loop.py path/to/project --max-iterations 3
python3 scripts/proof_loop.py path/to/project --reference tool_checks/evidence.md
python3 scripts/proof_loop.py path/to/project --prepare-only
```

The checkpoint at `.proof_runtime/proof_loop_checkpoint.json` stores the theorem and acceptance-contract identity, selected plan, first error, repair budget, pending candidate, evidence request, references and hashes, and next action. Model and reasoning settings inherit from the checkpoint unless explicitly overridden. Only run one controller against a given project at a time.

The compact runtime brief shows the current claim, its revision, and the reason for that revision. Its channel counts cover the current theorem revision; older records remain in the append-only history.

| Saved action | What the next invocation does |
| --- | --- |
| `solve` | Continue the selected plan if there is one |
| `repair` | Supply the rejected candidate and exact first error for the remaining local repair |
| `replan` | Start from the target and current failure record, without the failed derivation |
| `verify` | Recheck the same unchanged candidate; do not generate another proof |
| `awaiting-evidence` | Return the same request without a model call until a new or explicitly updated reference arrives |
| `complete` | Check the claim, contract, candidate, result, referee packet/report, and references; new evidence or changed obligations triggers rechecking |
| `exact-obstruction` | Return the obstruction until new evidence arrives or execution is explicitly restarted |

`--max-iterations` and `--max-wall-seconds` grant resources to this invocation. The checkpoint also reports cumulative generator iterations, agent calls (including scouts/referees/failures), and observed controller wall time for the current theorem revision. These are not token counts or monetary costs. Abrupt host termination can prevent a final wall-time update. A prepared packet is not a model call. Ctrl-C stops the controller's current generator or referee process group and preserves the saved next action; an interrupted referee resumes with the same candidate. Forced host or process termination may bypass that cleanup.

Use `--fresh-attempt` to intentionally reset execution while keeping failure history and the cumulative counts from a valid checkpoint. It is not a new theorem. To repair a theorem, edit the claim and routing files consistently, update the ledger's Claim and proof status to match the revised statement, then run:

```bash
python3 scripts/proof_runtime.py revise-claim path/to/project --reason "Exact change and why it is needed"
```

Old attempts remain in append-only history. Hard route exclusions require the current claim hash, revision, and acceptance-contract hash. Failures from older or unknown contracts remain available as historical search hints; inspect whether their failure conditions still apply. Unversioned historical route fingerprints are not trusted as new hard exclusions. With an older project that has no checkpoint, inspect its last packet before choosing a fresh action and supply useful artifacts as references. The controller does not infer a reliable pending action from old prose logs.

A stale reference cannot silently change a pending proof: provide its path again explicitly, then let the pending action recheck it. A changed accepted artifact or a damaged checkpoint clears active referee acceptance and produces a runtime error. Starting a fresh attempt also clears that active acceptance while retaining its historical evidence. Preserve the historical files, inspect the mismatch, and use an intentional fresh attempt or theorem repair as appropriate. `--prepare-only` does not change the active acceptance status.

For a damaged checkpoint, an explicit `--fresh-attempt` first copies its exact bytes to a uniquely named `.proof_runtime/proof_loop_checkpoint.damaged-*.json` archive and verifies that copy. The original path is replaced only when the clean checkpoint can be saved. The damaged file's proof state, settings, references, and counters are not reused; provide the needed references and settings again. New counters carry `scope=since-checkpoint-recovery` and `prior_totals_known=false`, and the summary names the archive and explains that earlier totals are unknown. Those labels survive later resumptions and fresh attempts for this theorem revision. Existing run histories and proof artifacts remain available for inspection. Without `--fresh-attempt`, or with `--prepare-only`, a damaged checkpoint still produces an error and is not archived or replaced.

Changing only `## Acceptance Contract` in `claim.md` also invalidates completion. The existing candidate returns to verification, and the runtime status becomes unresolved while that review is pending. Legacy completed checkpoints without a recorded contract identity or referee-packet hash must be reviewed again. A verdict binds to the frozen packet's claim, contract, proof, and references; changes during review cannot accept or retire a route. The accepted Markdown is written from that checked snapshot.

Duplicate scout routes are bookkeeping events, not failed mechanisms. The reader ignores legacy duplicate-only retirements and exclusions propagated from them, while preserving explicit retirements and recorded mathematical failures.

`needs-evidence` is a request to the proof owner, not an automatic external invocation. Its packet contains a local claim, assumptions, requested capability, missing artifact, acceptance test, candidate identity when available, and resume phase. A `tool-replay` request differs from literature retrieval; an uncertain model verdict is not a route refutation. Malformed referee output is a retryable runtime failure, not a request to wait indefinitely for unspecified mathematical evidence.

The runtime's `referee-accepted` label means a model accepted a candidate. `evidence_summary` records proof/refutation disposition and keeps `human_reviewed` and `formal_verification` false. Independent mathematical review and formal replay remain separate actions.

## Skill rename

The repository is now `jmf-enigma/math-research`; the installed skill and explicit invocation are `math-research` and `$math-research`. The previous repository was `codex-theory-proof-workbench`, with skill directory `theory-proof-workbench`.

Back up the old installation, install the new version under `math-research`, update its Git remote if it is a clone, and update saved commands and neighboring skill references. Existing proof-project directories, claims, ledgers, and checkpoints do not need renaming. Remove the old `SKILL.md` from skill discovery after migration. If saved project commands still use the old scripts path, a compatibility directory containing a `scripts` symlink to the new installation can preserve those commands without registering a duplicate skill.
