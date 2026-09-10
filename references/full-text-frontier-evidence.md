# Full-Text Frontier Evidence

Use this only when a claim is being classified as known, open, or new, or when a nearby paper may supply a proof route. It turns literature work into a small auditable bundle rather than a prose claim that papers were checked.

A Matlas or TheoremSearch packet may seed candidate papers and exact statement searches, but it is not Scholar evidence, current-coverage evidence, verified metadata, or a source-text anchor. Start the ladder below from the candidates it suggests.

## Evidence Ladder

1. Discover candidates through Google Scholar. Model memory may suggest search terms but is not a search result.
2. Verify metadata through DOI, arXiv, proceedings, or another official record.
3. Retrieve a lawful full text. Prefer arXiv, publisher open access, Unpaywall, OpenAlex, Semantic Scholar `openAccessPdf`, an author copy, or the user's authorized local copy.
4. Verify the artifact before reading: local path, `%PDF` signature when applicable, byte count, source URL, version, access status, and SHA-256.
5. Read the exact theorem statement and proof. Record stable statement and proof anchors rather than citing the paper generally.
6. Extract a solution card that says what mathematical move transfers and what new bridge remains.
7. Record recent cited-by or active-project checks, the closest result, exact gap, limitations, and cutoff.
8. Run the validator. Do not classify the frontier from hand-written `IDEA_MAP.md` fields alone.

## Scholar Evidence

With SerpAPI configured, preserve normalized or raw JSON from an executed Scholar query:

```bash
codex-cite scholar "EXACT QUERY" --num 10 --json > /tmp/scholar-q1.json
codex-cite scholar-url "EXACT QUERY"
python3 scripts/frontier_evidence.py add-query PROJECT \
  --query "EXACT QUERY" \
  --scholar-url "PRINTED_SCHOLAR_URL" \
  --evidence /tmp/scholar-q1.json \
  --method google-scholar-serpapi
```

Without SerpAPI, use `codex-cite scholar-url`, inspect Scholar in a browser, and save a visible export, screenshot, or concise result record as the evidence file. Do not scrape Scholar or bypass CAPTCHA. Two distinct executed queries are the minimum gate, not a claim of exhaustive coverage.

Useful query families are the exact claim, equivalent terminology, central object plus theorem, closest stronger/weaker result, and cited-by or recent-year variants. Stop broadening when new queries no longer change the closest result or exact gap.

## Lawful Full Text

`frontier_evidence.py fetch` supports four compact routes:

```bash
# arXiv PDF; add --include-source when LaTeX source helps locate exact mathematics
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P1 --arxiv 1706.03762 --include-source

# DOI: Crossref metadata, then Unpaywall when --mailto is supplied,
# with Semantic Scholar openAccessPdf as a lawful fallback
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P2 --doi 10.xxxx/xxxxx --mailto you@example.edu

# SSRN abstract ID or URL: derive doi:10.2139/ssrn.ID, verify metadata,
# and resolve a non-SSRN open copy through the DOI resolver chain
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P3 --ssrn 3395992

# Known lawful PDF URL with explicit official metadata
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P4 --url "OPEN_PDF_URL" \
  --title "TITLE" --authors "AUTHOR" --year 2025 \
  --identifier "official:ID" --verification-url "OFFICIAL_RECORD_URL"
```

Set `UNPAYWALL_EMAIL` once instead of passing `--mailto` repeatedly. Optional `OPENALEX_API_KEY` and `SEMANTIC_SCHOLAR_API_KEY` values improve rate limits; never commit them to the skill or a proof project.

## SSRN And INFORMS

For an SSRN record, use the abstract ID as the stable identity and derive `10.2139/ssrn.ID`. Do not try to construct a `download.ssrn.com` URL from the DOI. Those URLs contain AWS session credentials and signatures issued by SSRN, typically expire within minutes, and may use a document-version ID different from the abstract ID.

Run `fetch --ssrn` first. It queries Unpaywall, OpenAlex, and Semantic Scholar, rejects candidates that merely point back to SSRN, and uses exact-title plus author matching for alternate records. If that chain has no PDF, automatically search the exact title and one author for an institutional repository, author manuscript, RePEc-linked copy, EconStor, NBER, HAL, arXiv, Optimization Online, or another lawful repository. Do this bounded mirror scan before asking the user to handle SSRN. Verify the PDF first page against title and authors, then anchor metadata at the SSRN DOI.

If Crossref reveals a published DOI and the bounded web search supplies an author-hosted PDF, keep metadata automatic:

```bash
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P3 --doi 10.xxxx/published-doi \
  --fallback-url "VERIFIED_AUTHOR_OR_REPOSITORY_PDF" \
  --version "accepted or submitted manuscript"
```

If a real authorized browser session produces a fresh signed SSRN URL, consume it immediately without storing the token:

```bash
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P3 --ssrn 3395992 --ssrn-signed-url "FRESH_DOWNLOAD_URL"
```

The helper checks `download.ssrn.com`, the abstract ID, and the AWS expiry, stores only the stable SSRN landing page plus the downloaded artifact hash, and discards the temporary credential. Prefer a browser-native download followed by `register-local` when the browser controller cannot safely expose the URL. Reuse the authorized browser profile; stop only when SSRN presents a new CAPTCHA, OTP, paywall, or account challenge.

For an INFORMS paper, start from its published DOI and run the ordinary DOI route. If the version of record is unavailable, search the exact title and authors for an SSRN working paper or accepted manuscript. Treat it as a proof source only after comparing theorem statements, assumptions, appendix/supplement structure, and revision dates against the published record; theorem numbering and proofs can differ across versions.

For a user-provided or institution-authorized local copy:

```bash
python3 scripts/frontier_evidence.py register-local PROJECT \
  --paper-id P1 --path /path/to/paper.pdf --source-url "AUTHORIZED_SOURCE_URL" \
  --title "TITLE" --authors "AUTHOR" --year 2025 \
  --identifier "doi:10.xxxx/xxxxx" --verification-url "https://doi.org/10.xxxx/xxxxx" \
  --version "version of record" --access "institution-authorized" --license "all rights reserved"
```

If browser-based institutional access is needed, use an installed lawful downloader or browser-control skill only with the user's active authorized session. Stop at passwords, CAPTCHA, QR login, OTP, DRM, or bot challenges. Register the resulting local file afterward. `no_authorized_pdf_found` is evidence of retrieval failure, not permission to bypass access controls.

## Source Anchors And Solution Card

Prefer anchors such as `Theorem 3, p. 11`, `Proof of Lemma 5, pp. 19-21`, a stable HTML section, or arXiv source file and line span. A title, abstract, or general page number is not a proof anchor.

After reading, record:

```bash
python3 scripts/frontier_evidence.py mark-read PROJECT \
  --paper-id P1 --status proof-read \
  --statement-anchor "Theorem 3, p. 11" \
  --proof-anchor "Proof of Theorem 3, pp. 19-21" \
  --result "EXACT RESULT" --assumptions "EXACT ASSUMPTIONS" \
  --gap "MISMATCH WITH THE USER CLAIM" \
  --central-object "OBJECT THAT ORGANIZES THE PROOF" \
  --proof-decomposition "HOW THE PROOF BREAKS INTO LEMMAS" \
  --key-step "NONROUTINE MOVE" \
  --transplantable-move "MOVE TO TRY IN THE CURRENT PROBLEM" \
  --bridge-lemma "NEW LEMMA NEEDED FOR TRANSFER" \
  --evaluator "CHEAPEST FALSIFIER OR CHECKER"
```

The solution card is not a paper summary. It must distinguish the source theorem from the user's theorem and produce one bounded next move. If nothing transfers, say so explicitly and identify the failed assumption match.

## Frontier Decision

Record active-work checks and the bounded classification:

```bash
python3 scripts/frontier_evidence.py set-activity PROJECT \
  --query "RECENT CITED-BY OR PUBLIC-PROJECT QUERY" \
  --none-found-note "No exact public route was visible under this query by YYYY-MM-DD."

python3 scripts/frontier_evidence.py set-frontier PROJECT \
  --status apparently-open --closest P1 \
  --gap "EXACT UNSOLVED DIFFERENCE" \
  --assessment "WHY THE RECORDED EVIDENCE SUPPORTS THIS BOUNDED LABEL" \
  --limitation "Absence from a bounded search does not prove novelty."

python3 scripts/frontier_evidence.py validate PROJECT
python3 scripts/proof_doctor.py PROJECT
```

Use `apparently-open` unless coverage is unusually strong. A valid bundle confirms that the recorded files match their hashes and required search/reading fields are present. The `proof-read` status, anchors, and solution card are declared reading evidence for inspection; the validator does not independently establish that a human or agent read the proof. It does not prove exhaustive literature coverage or the truth of the paper.

## Design Source

This layer adapts two useful patterns from [nature-skills](https://github.com/Yuan1z0825/nature-skills): the downloader's explicit access and failure states plus PDF-signature checks, and the reader's stable full-document source map. It deliberately omits the project's institution-specific CDP, CARSI, CNKI, translation, figure, and browser-preview machinery. The proof workbench needs a compact evidence chain and transferable mathematical structure, not a second literature-management system.
