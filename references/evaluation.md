# Evaluating changes to the workbench

Use when maintaining the skill or claiming a capability improvement. Ordinary proof tasks do not require an evaluation campaign.

## Three different kinds of evidence

1. **Controller regressions:** deterministic fixtures check continuation, rejection routing, artifact identity, theorem revisions, and budget accounting. They establish software behavior, not mathematical ability.
2. **Mathematical forward tests:** solve realistic fixed tasks without supplying the intended answer to the solving agent; separately inspect its mathematics, scope, and routing. Examples used to revise instructions become calibration cases, not held-out tests.
3. **Capability comparisons:** freeze a separate problem set and compare the old/simple baseline with the new skill under matched model, reasoning effort, tools, references, and resource grants. Blind review must assess the original theorem rather than the model's own success label.

## Regression commands

Use the maintained command list in [README: Development](../README.md#development), including the focused evidence and recovery regressions as well as the integrated smoke checks.

Include accepted and refuted candidates, wrong/uncertain/empty verdicts, central versus local errors, repeated repair, tool crashes, missing evidence, changed artifacts, Chinese mathematical descriptions, and theorem repair. A split run should preserve the same next mathematical action as a continuous run. Changes to documentation wording are not mathematical tests.

## Forward-test design

Include an ordinary provable claim, a false claim with an admissible counterexample, a missing-assumption problem, a representation/recovery problem, and an actually unresolved or resource-limited kernel. Cover native OR/MS objects such as Bellman inequalities, deviation cycles, primal/dual witnesses, and boundary/tie cases.

Give the solver the exact user request, the skill, and minimal raw inputs. Withhold the answer, rubric, suspected failure, and revision rationale. A separate reviewer sees the original request and final artifact. Score:

- Correctness and fidelity to the original quantified claim.
- Completion of the main argument, or an exact and honest unresolved kernel.
- Witness validity and faithful return from a reformulation or encoding.
- Unsupported promotion, missing assumptions, fabricated premises, and local/global confusion.
- Unnecessary orchestration, duplicated work on resume, and actual resource use.

Record model identifier as reported, requested reasoning effort, CLI/tool versions, skill commit or file hashes, task and reference hashes, prompts, outcomes, first fatal error, and per-run costs. Keep unavailable usage fields null. Count retries, failed runs, scouts, verifiers, and external tool calls. Equal iteration counts alone do not imply equal compute; if token/cost telemetry is unavailable, describe only the equal wall-time/call grants actually enforced.

Report denominators, failure cases, and variance over repeats before claiming gains. A selected set of previously solved tasks cannot estimate general solve rate. A few forward tests can detect regressions but cannot establish improved discovery on unseen research mathematics. Novelty is a separate literature question, not a correctness score.
