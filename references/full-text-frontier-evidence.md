# Full-Text Frontier Evidence

Use the full evidence bundle when classifying a claim as known, open, or new. For a nearby paper needed only as a premise or proof method, retrieve its exact statement/proof and create a solution card; no frontier classification or Scholar-query quota is required.

Matlas/TheoremSearch can suggest candidates. Their packets do not establish current coverage, verified metadata, or source-text anchors.

## Evidence Ladder

For a frontier classification: execute Scholar searches, verify official metadata, obtain and inspect the full text, anchor the relevant statement/proof, compare the closest result, check recent activity, and record the remaining gap with a cutoff and limitations. Validate the saved bundle before using its status. The validator checks recorded evidence, not novelty itself.

## Scholar Evidence

With SerpAPI configured:

```bash
codex-cite scholar "EXACT QUERY" --num 10 --json > /tmp/scholar-q1.json
codex-cite scholar-url "EXACT QUERY"
python3 scripts/frontier_evidence.py add-query PROJECT \
  --query "EXACT QUERY" \
  --scholar-url "PRINTED_SCHOLAR_URL" \
  --evidence /tmp/scholar-q1.json \
  --method google-scholar-serpapi
```

Without SerpAPI, inspect the generated Scholar URL in a browser and save an export, screenshot, or concise result record. Do not scrape or bypass CAPTCHA. The runtime requires two distinct executed queries for frontier validation; this is a recording minimum, not exhaustive coverage.

Use exact-claim/equivalent terminology, central-object/theorem, stronger/weaker-result, and recent/cited-by variants as needed. Stop broadening when new queries no longer change the closest result or gap. Model memory is a query seed, not search evidence.

## Lawful Full Text

`frontier_evidence.py fetch` supports:

```bash
# arXiv; include source only when it helps inspect the mathematics
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P1 --arxiv 1706.03762 --include-source

# DOI metadata and open-copy resolution
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P2 --doi 10.xxxx/xxxxx --mailto you@example.edu

# SSRN abstract identity and alternate open copies
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P3 --ssrn 3395992

# Known lawful PDF with official metadata
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P4 --url "OPEN_PDF_URL" \
  --title "TITLE" --authors "AUTHOR" --year 2025 \
  --identifier "official:ID" --verification-url "OFFICIAL_RECORD_URL"
```

Set `UNPAYWALL_EMAIL` instead of repeating `--mailto`. Optional OpenAlex/Semantic Scholar API keys improve access limits; do not commit them. Before reading, check source/version, local artifact, PDF signature where applicable, byte count, access status, and SHA-256. HTML challenges and metadata are not full text.

## SSRN And INFORMS

Use the SSRN abstract ID and DOI `10.2139/ssrn.ID` as stable identity. Do not construct `download.ssrn.com` URLs from the DOI: signed download URLs expire and may use a different document-version ID.

Run `fetch --ssrn` first. It checks Unpaywall, OpenAlex, and Semantic Scholar, excludes links back to SSRN, and matches alternate records by exact title plus author. If unresolved, make a bounded exact-title/author search for institutional or author manuscripts and lawful repositories before asking for user access. Verify the PDF title/authors and retain the SSRN DOI as metadata anchor.

For a published DOI with a verified open manuscript:

```bash
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P3 --doi 10.xxxx/published-doi \
  --fallback-url "VERIFIED_AUTHOR_OR_REPOSITORY_PDF" \
  --version "accepted or submitted manuscript"
```

A fresh signed URL from an already authorized browser session can be consumed immediately:

```bash
python3 scripts/frontier_evidence.py fetch PROJECT \
  --paper-id P3 --ssrn 3395992 --ssrn-signed-url "FRESH_DOWNLOAD_URL"
```

The helper checks host, abstract ID, and AWS expiry; it retains the stable landing page and artifact hash, discarding the temporary credential. Prefer browser-native download and `register-local` when the browser controller cannot safely expose the URL. Reuse existing authorized access; stop at a new authentication, paywall, or protective challenge.

For INFORMS, resolve the published DOI first, then search title/authors for an accepted manuscript or SSRN version. Before using an alternate version as a premise, compare statement, assumptions, appendices/supplements, and revision dates: theorem numbers and proofs may differ.

Register user-provided or institution-authorized copies:

```bash
python3 scripts/frontier_evidence.py register-local PROJECT \
  --paper-id P1 --path /path/to/paper.pdf --source-url "AUTHORIZED_SOURCE_URL" \
  --title "TITLE" --authors "AUTHOR" --year 2025 \
  --identifier "doi:10.xxxx/xxxxx" --verification-url "https://doi.org/10.xxxx/xxxxx" \
  --version "version of record" --access "institution-authorized" --license "all rights reserved"
```

Use authorized browser/downloader access without bypassing passwords, CAPTCHA, OTP, DRM, or bot challenges. `no_authorized_pdf_found` records retrieval failure, not absence of a result or permission to bypass controls.

## Source Anchors And Solution Card

Use a precise theorem/proof/page anchor, stable HTML section, or source file/line span. A title or abstract cannot support a proof claim.

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

A solution card distinguishes source and target, identifies the transferable move, and exposes the new bridge. If nothing transfers, record the failed assumption match. A paper summary alone does not change the proof state.

## Frontier Decision

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

Use `apparently-open` unless coverage supports a stronger label. Validation confirms hashes and required fields. `proof-read`, anchors, and solution cards are inspectable declarations of reading, not independently established reading or mathematical truth. A valid bundle does not establish exhaustive coverage.

## Design Source

The artifact checks and explicit access/failure states adapt the downloader and stable source-map patterns from [nature-skills](https://github.com/Yuan1z0825/nature-skills). Institution-specific browser, translation, and preview machinery is outside this proof workflow.
