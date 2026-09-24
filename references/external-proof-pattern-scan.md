# External Proof Pattern Scan

Use when a route lacks a likely known theorem, construction, assumption, or proof move. Name that missing ingredient before searching. Start with local papers, appendices, prior ledgers, and nearby theorem names; stop when a source changes the next mathematical action or shows a decisive mismatch.

For a claim of novelty or openness, use [full-text frontier evidence](full-text-frontier-evidence.md). For workbench maintenance, the [research source map](research-backed-proof-loop.md) contains the method inventory. Loading a catalog of prover papers is not part of an ordinary proof attempt.

## Statement Retrieval

Search individual statements when titles and abstracts do not identify the needed result.

| Service | Useful coverage | Limit |
| --- | --- | --- |
| Matlas | Published papers and textbooks | Does not establish recency or completeness |
| TheoremSearch | arXiv and open-source statements, with type/source/year filters | Coverage is incomplete; query text and filters are logged |
| LeanSearch/Loogle/LeanFinder | Formal declarations and current Lean goals | Does not establish an informal paper's claim |

```bash
python3 scripts/statement_search.py \
  "A COMPLETE, ABSTRACTED MATHEMATICAL STATEMENT" \
  --service matlas --intent theorem --remote-ok --project path/to/project
```

Use `--service theoremsearch` for its corpus; filters include `--tag math.OC`, `--source arXiv`, `--result-type Lemma`, and `--year-range MIN MAX`. Both services are remote. No Matlas query-retention policy was verified. Use public abstracted queries within existing authorization; do not send private source material, model details, or identifying constants without permission. If abstraction removes the relevant mathematics, search locally or obtain authorization for the actual content.

1. Phrase the desired theorem, construction, or obstruction as a complete mathematical statement. For a construction, specify properties that must hold jointly.
2. Choose the corpus matching the need. Switch services for a coverage mismatch, not merely to seek a more agreeable top hit.
3. If retrieval fails, reformulate through the actual proof gap: a bridge lemma, existence claim, dual statement, or obstruction. Repeated paraphrases with unchanged mathematics do not justify more queries.
4. Verify the strongest plausible candidate in its full text before widening the search. Expand definitions, map assumptions, and read the proof passage that supplies the move.
5. Return to mathematics: derive the missing bridge, test a boundary, or reject the source by an assumption mismatch. Search again only if this produces a different target.

Retrieval packets remain `retrieved-unverified` with `proof_effect=none`. Scores and absence of hits establish neither applicability nor novelty. A service failure means `retrieval-unavailable`; an unhelpful search means `no-useful-candidate`. Neither blocks a local proof attempt.

Service sources: [Matlas](https://arxiv.org/abs/2604.17484), [TheoremSearch](https://arxiv.org/abs/2602.05216). [Rethlas](https://arxiv.org/abs/2604.03789) illustrates broad search → reformulated target → focused retrieval → independent bridge proof. Its preliminary arXiv endpoint was marked for deprecation; use the maintained adapter rather than copying that endpoint.

## Extraction Card

Record only what makes the source usable:

- **Anchor:** verified source/version and the exact definition, theorem, or proof passage.
- **Applicability:** required assumptions, their map to the current problem, and what each unmatched assumption does in the source proof.
- **Move:** the construction, transformation, or invariant and its guaranteed output.
- **Bridge:** the remaining current-problem lemma and where the imported output is consumed.
- **Check:** a derivation, boundary test, certificate, or replay deciding whether the transfer works; state its scope.

If several retrieved results are needed, test their joint sufficiency in a conditional assembly. Individually relevant theorems can still leave a gap between incompatible definitions or hypotheses. If an extra source assumption is essential, report the mismatch or repair the target explicitly.

A source can provide intuition without supplying a proof step. Promote a reusable trick only after source verification and replay; see [proof-move migration](proof-idea-generator.md#proof-move-migration-and-trick-replay).

## Autonomous Capability Radar

Search for a new tool or method only when the route needs an unavailable artifact or independent evidence channel. Derive the query from that output: exact certificate, construction, premise bundle, formal declaration, or strict checker.

Check existing tools first. For a new candidate, inspect its primary paper and implementation, identify the additional capability and trust boundary, and try a bounded live probe within existing authorization. A documented endpoint alone does not establish that a service works. Reject a wrapper duplicating the current evidence channel; a second model's confidence is not independent mathematical verification.

Stop when the needed artifact can be produced or when candidates share the same mismatch. Installation and capability browsing must earn their cost by changing the proof route. Source uploads and public writes remain separate authorized actions.

## Use In A Proof Project

Record a useful source in `PATTERN_SCAN.md` with its extraction card. Put a checked premise in `LEDGER.md`, a changed route in `ATTACK_MATRIX.md`, or an expected tool artifact in `TOOL_PLAN.md` only when that file is already needed. Preserve retrieval packets as provenance. Do not create project paperwork for a short theorem lookup.

## Stop Rule

Return to proving when a source supplies a checkable route, identifies a missing assumption, or fails for a mathematically informative reason. Continue searching only for a named unresolved ingredient. Agreement among papers or proof agents is not an acceptance test for the current theorem.
