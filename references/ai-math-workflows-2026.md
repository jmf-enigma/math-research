# AI mathematics: source-to-method update, 2026-09-10

Maintenance reference; do not load during an ordinary proof. This is a targeted update to the earlier [research map](research-backed-proof-loop.md), not a new systematic review or a re-audit of its 57-paper inventory. Search covered recent proof agents, formalization workflows, and author-reported mathematical discoveries. Primary texts were checked at the versions below. No citation-count ranking was used.

## What transfers

| Source and reading scope | What the work actually supports | Adaptation in this workbench |
| --- | --- | --- |
| Robbins, Lawless, Udell, Vitercik, [FLARE](https://arxiv.org/html/2608.25220v1), Aug 25; §§4–6 and limitations | MILP reformulation checking through explicit parameter, forward, recovery, and monotone objective maps. The reported result concerns a particular benchmark subset; formal guarantees depend on faithful encoding. | Require the maps needed by the claimed implication; sampled agreement is insufficient. See [representation witnesses](representation-witness.md) and the generator/referee instructions. |
| Shen et al., [MechGeo](https://arxiv.org/html/2608.02295v1), Aug 3; methods and experiments | A geometry intermediate representation, deterministic translation, selective algebraization, and Lean-checked certificates. Some generated statements were refuted and subsequently corrected by experts. | Separate a counterexample to the original theorem, to a child lemma, and to an encoding. Use CAS on a suitable leaf and check the return to the parent. No geometry backend is bundled. |
| Tsoukalas et al., [AlphaProof Nexus](https://arxiv.org/html/2605.22763v2), June 8 revision; §§2, 5–6, Appendix A.1/B.3 | Durable formal sketches and exact compiler feedback. A basic agent replicated nine successes in a post-hoc comparison on the nine problems the full system solved; this is a selected subset, with substantial cost variance. | Default to a compact loop, preserve the pending mathematical action across compute grants, retain checked work, and evaluate additional orchestration against a matched baseline. This does not reproduce AlphaProof or establish that simple loops always win. |
| [QED](https://arxiv.org/html/2604.24021v4), June 26 revision; failure modes and system design | Separates planning, proving, and verification; focuses effort on the key original step and diagnoses statement modification. Expert assessment is distinct from the model verifier. | Keep the selected plan while awaiting evidence. Replan immediately on claim/assumption/assembly or central-mechanism failure; allow one repair for a surviving local mechanism. |
| [Rethlas/Archon](https://arxiv.org/html/2604.03789v2), May 30 revision; §3.1 and §5.1 | Chooses examples, counterexamples, source search, decomposition, and proving according to the current obstruction; examines source proofs and hypothesis boundaries. | Keep one obstruction-triggered action. Literature retrieval, tool replay, formalization, and idea consultation have different return contracts. A new process or tool is not itself proof progress. |
| Antonio and Pablo Acuaviva, [Mathematical Discovery in the Wild](https://arxiv.org/html/2607.17388v1), July 19; Parts I/III and the statement/strategy of Problem 3 | Reports AI-generated Banach-space arguments with subsequent human checking. Distinguishes human-selected research problems from automatically mined targets, and unreviewed packets from reviewed results. | Verify a source question in context, including later answers in the same paper. Preserve proof, refutation, partial, conditional, known-answer, and failed-attempt records separately. A candidate accepted by a model remains `referee-accepted`. We did not independently certify the paper's five proofs. |
| Steiner, [Locally bipartite subgraphs via multicolor Ramsey numbers](https://arxiv.org/html/2608.02522v2), Sept 7 revision; AI disclosure and §3, especially Lemma 3.3 | Attributes the idea and initial proof of Theorem 1.7, and an earlier proof of Lemma 4.5, to AI; identifies the author's other contributions and subsequent checking/reworking. The odd-cycle construction augments an earlier triangle construction with a second coordinate. | When a construction fails under composition, identify the missing closure property and try a minimal additional invariant or coordinate. Transfer the mechanism and prove its new obligations; do not transfer authorship or novelty claims. |
| OpenAI, [mathematical papers](https://cdn.openai.com/pdf/ten-proofs-oai.pdf) and [discovery walkthroughs](https://cdn.openai.com/pdf/reasoning-walkthroughs.pdf), linked from the [Aug 1 release](https://openai.com/index/ten-advances-in-mathematics/); walkthrough abstract and Chapter 10 | The Ramsey account describes fixed-product barriers, a missing-color palette, and a proper-label invariant that prevents a two-block monochromatic triangle. The walkthrough explicitly reconstructs discovery retrospectively using AI; it is not a raw execution trace or a controlled ablation. | Use failed closure and exact residuals to propose a stronger invariant. Keep retrospective explanation distinct from observed runtime evidence. No claim of having reviewed all ten long proofs or reproduced their discoveries. |

## From discovery to an actual proof

The runtime synthesis is maintained in [SKILL.md](../SKILL.md); representation and failed-closure obligations live in [representation-witness.md](representation-witness.md). These are adaptations of the mechanisms above, not claims that each source implements the same workflow.

## Concrete implementation and verification

| Transfer or diagnosed failure | Implementation | Validation |
| --- | --- | --- |
| Keep the mathematical action across episodes | `loop_checkpoint.py`; solve/repair/replan/verify/awaiting-evidence phases | Split run versus uninterrupted run; pending repair and verification recovery |
| Keep uncertainty separate from rejection | `referee_action`; typed evidence request; explicit first error | Tool replay, crash, empty rejection, no-evidence idle cases |
| Preserve theorem and failure provenance | Revision-scoped runtime events; Unicode/operator-preserving fingerprints | Chinese routes, changed assumptions, theorem repair, historical retention |
| Distinguish criticism from certification | `referee-accepted` plus `evidence_summary` | No automatic human-review or formal-verification flag |
| Construct and transport mathematical witnesses | [representation-witness.md](representation-witness.md), proof-idea generator, both agent packets | Behavioral evaluation cases; semantic review still required |
| Add complexity only when it helps | Conditional strategy and verification references; [evaluation protocol](evaluation.md) | Infrastructure tests and mathematical forward tests are reported separately |

The controller hashes exact normalized route descriptors; it does not decide semantic equivalence of arbitrary mathematics. Referee error classes are advisory judgments. Checkpoints protect continuity and artifact identity, not theorem truth.

## Version and evidence notes

- Steiner's earlier [2608.02537](https://arxiv.org/abs/2608.02537) was withdrawn on Sept 7 because it was merged into 2608.02522v2. That is supersession, not evidence that its mathematical result was refuted. Cite the merged version and its specific attribution.
- ArXiv and author manuscripts are primary reports, not an automatic statement of peer-review status. Reported success counts do not transfer to this skill.
- No trained verifier, evolutionary population, paper-mining queue, specialist model, or new backend is claimed to have been implemented by adding these references.
- The retained source audit records exact downloaded versions and file hashes. Refresh a paper's version and status when making a new external novelty claim; do not re-run a literature survey for each proof.
