# Proof-loop recovery

Use for the executable runner, durable projects, missing evidence, interrupted execution, or migration. Commands assume the skill directory is the working directory and Python 3.10+ is available. Run only one controller per project.

## Start and resume

```bash
python3 scripts/proof_loop.py path/to/project --claim "EXACT CLAIM" --max-iterations 3 --reasoning-effort high
python3 scripts/proof_loop.py path/to/project --reference tool_checks/evidence.md
python3 scripts/proof_loop.py path/to/project --prepare-only
```

The runner creates a minimal project, generates one candidate, and sends it to a separate ephemeral referee. A surviving route gets one local repair; a failed repair or broken mechanism triggers replanning. It stops on acceptance, a named evidence request, or its budget. `--prepare-only` prepares the next packet without invoking a model.

Use `--allow-search` only for public or safely abstracted mathematics. It permits one retrieval turn after the generator identifies retrieval as the obstruction; otherwise retrieval remains an outer action. Provide project-local evidence with `--reference`. For a simplification request, retain the exact theorem in `claim.md`, put the simplification requirement under `## Acceptance Contract`, and supply the old proof as a reference.

For a larger project:

```bash
python3 scripts/start_proof.py --title "SHORT NAME" --claim "EXACT CLAIM"
python3 scripts/proof_doctor.py path/to/project
```

Use `start_proof.py --mode recovery` for prior failures, `--mode discovery` for unknown-answer exploration. A fixed claim missing a proof object stays in ordinary proof discovery. Resume from the compact runtime brief: current claim, revision, revision reason, and unresolved action. Read older ledgers only for the missing context.

## Hard exploration

Add `--hard-exploration` after materially different routes have failed, or a serious attempt still lacks a central object or conditional assembly. It adds at most two independent scouts and one selector. The selector chooses a supplied route, identifies its `key_original_step`, and defers plausible alternatives; it neither proves the route nor blends new plans. The historical pool keeps at most three untried routes. The selected plan survives later invocations.

This mode and `--reasoning-effort max` are options for a diagnosed hard kernel, not prerequisites for ordinary proving. Model and reasoning settings inherit from the checkpoint unless overridden.

## Saved action and budget

`.proof_runtime/proof_loop_checkpoint.json` binds the claim and acceptance contract to the plan, first error, repair budget, pending candidate, evidence request, references, and hashes.

| Saved action | Next invocation |
| --- | --- |
| `solve` | Continue the selected plan, if present |
| `repair` | Supply the rejected candidate and first error for the remaining repair |
| `replan` | Use the target and failure record without the failed derivation |
| `verify` | Review the same unchanged candidate |
| `awaiting-evidence` | Return the same request without a model call until a new or explicitly updated reference arrives |
| `complete` | Recheck claim, contract, candidate, result, referee packet/report, and references; changed obligations or new evidence requires review |
| `exact-obstruction` | Return the gap until new evidence or an intentional restart |

Each invocation grants its own `--max-iterations` and `--max-wall-seconds`. Cumulative counts cover generator iterations, all agent calls, and observed controller wall time for the theorem revision; they are not token or cost totals. A prepared packet is not a model call. Ctrl-C terminates the active generator/referee process group and preserves the next action. Interrupted review resumes the same candidate. Forced host termination may bypass cleanup or the final time update.

## Revisions and evidence

`needs-evidence` names the local claim, assumptions, missing artifact, capability, acceptance test, and resume action. Supply that artifact rather than restarting discovery. Tool replay, retrieval, and uncertain mathematical review are different requests. A correct proof with `simplification-gap` replans; it does not wait for external evidence or make the theorem false. Malformed referee output is a retryable execution failure.

A changed reference must be supplied again explicitly. Changes during review cannot accept or retire a route: the verdict and accepted Markdown are bound to the checked packet. Changing only the acceptance contract returns the existing candidate to review. Legacy completion without contract or referee-packet identity also needs review.

A theorem repair requires consistent edits to the claim, routing, and ledger, followed by:

```bash
python3 scripts/proof_runtime.py revise-claim path/to/project --reason "Exact change and why it is needed"
```

History remains append-only. Hard exclusions apply only to the same claim hash, revision, and acceptance contract. Older failures are hints to recheck; duplicate scout proposals are not mathematical failures. For a legacy project without a checkpoint, inspect its last packet and supply useful artifacts explicitly—the controller cannot recover a reliable next action from prose alone.

## Restart and damaged checkpoints

`--fresh-attempt` resets execution, clears active acceptance, and retains history and the valid checkpoint's cumulative counts. It does not create a new theorem. A changed accepted artifact or damaged checkpoint raises an error and clears active acceptance; preserve the files and inspect the mismatch. `--prepare-only` does not change active acceptance.

For a damaged checkpoint, explicit `--fresh-attempt` archives its exact bytes as `.proof_runtime/proof_loop_checkpoint.damaged-*.json` and verifies the backup before saving a clean checkpoint. Damaged settings, counters, and references are not reused; supply them again. New counters carry `scope=since-checkpoint-recovery` and `prior_totals_known=false`, including on later resumes. Earlier histories remain inspectable. Without an explicit restart—or with `--prepare-only`—the damaged file is neither archived nor replaced.

`referee-accepted` records model review of the stated proof/refutation. Its evidence summary does not assert human review or formal verification.

## Skill rename

The repository is `jmf-enigma/math-research`; the installed skill and invocation are `math-research` and `$math-research`. The old repository was `codex-theory-proof-workbench`, with skill directory `theory-proof-workbench`.

Back up the old installation, install under `math-research`, and update its remote and saved commands. Existing proof-project directories and checkpoints need no renaming. Remove the old `SKILL.md` from discovery. If saved commands require the old scripts path, retain a compatibility directory with a `scripts` symlink, without registering a duplicate skill.
