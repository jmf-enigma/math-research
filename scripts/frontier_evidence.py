#!/usr/bin/env python3
"""Build and validate auditable literature evidence for proof discovery."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from proof_runtime import read_project_identity


SCHEMA_VERSION = 1
MANIFEST = Path("literature/frontier-evidence.json")
READ_STATUSES = {"statement-checked", "proof-read"}
FULLTEXT_STATUSES = {
    "metadata-only",
    "downloaded",
    "parsed",
    "statement-checked",
    "proof-read",
    "not-retrieved",
}
FRONTIER_STATUSES = {"known", "likely-known", "apparently-open", "genuinely-new"}
ACCESS_STATUSES = {"open-access", "user-provided", "institution-authorized"}
MAX_BYTES = 200 * 1024 * 1024
USER_AGENT = "MathResearch/1.0 (lawful academic full-text retrieval)"


def today() -> str:
    return date.today().isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def blank_bundle(claim: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "claim": claim,
        "discovery": {"method": "", "queries": []},
        "papers": [],
        "activity": {"queries": [], "signals": [], "none_found_note": ""},
        "frontier": {
            "status": "",
            "closest_paper_ids": [],
            "exact_gap": "",
            "assessment": "",
        },
        "limitations": [],
    }


def project_path(project: Path, relative: str) -> Path:
    root = project.resolve()
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes project: {relative}") from exc
    return candidate


def relative_to_project(project: Path, path: Path) -> str:
    return str(path.resolve().relative_to(project.resolve()))


def manifest_path(project: Path) -> Path:
    return project.resolve() / MANIFEST


def write_frontier_template(project: Path, claim: str, *, overwrite: bool = False) -> Path:
    project = project.resolve()
    path = manifest_path(project)
    if path.exists() and not overwrite:
        return path
    (project / "literature" / "evidence").mkdir(parents=True, exist_ok=True)
    (project / "literature" / "papers").mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blank_bundle(claim), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def load_bundle(project: Path) -> dict[str, Any]:
    path = manifest_path(project)
    if not path.exists():
        raise FileNotFoundError(f"missing {MANIFEST}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("frontier evidence root must be a JSON object")
    return data


def save_bundle(project: Path, bundle: dict[str, Any]) -> None:
    path = manifest_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def filled(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value)
    return value is not None


def valid_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def valid_url(value: Any, *, scholar: bool = False) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    if scholar and not (parsed.hostname or "").endswith("scholar.google.com"):
        return False
    return True


def validate_hashed_file(
    project: Path,
    relative: Any,
    expected_hash: Any,
    label: str,
    errors: list[str],
    *,
    require_pdf: bool = False,
) -> Path | None:
    if not filled(relative):
        errors.append(f"{label}: missing path")
        return None
    try:
        path = project_path(project, str(relative))
    except ValueError as exc:
        errors.append(f"{label}: {exc}")
        return None
    if not path.is_file():
        errors.append(f"{label}: file not found: {relative}")
        return None
    if not re.fullmatch(r"[0-9a-f]{64}", str(expected_hash or "")):
        errors.append(f"{label}: missing or invalid sha256")
    else:
        actual = sha256_file(path)
        if actual != expected_hash:
            errors.append(f"{label}: sha256 mismatch")
    if require_pdf:
        with path.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                errors.append(f"{label}: file is not a PDF")
    return path


def validate_frontier_bundle(project: Path) -> dict[str, Any]:
    project = project.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        bundle = load_bundle(project)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "path": str(manifest_path(project)),
            "errors": [str(exc)],
            "warnings": [],
            "frontier_status": None,
            "counts": {"queries": 0, "papers": 0, "proof_read": 0, "solution_cards": 0},
        }

    if bundle.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not isinstance(bundle.get("claim"), str) or not bundle["claim"].strip():
        errors.append("claim is blank")
    if (project / "routing.json").is_file() or (project / "claim.md").is_file():
        try:
            project_claim, _ = read_project_identity(project)
        except (OSError, ValueError) as exc:
            errors.append(f"project claim identity is invalid: {exc}")
        else:
            if not isinstance(bundle.get("claim"), str) or bundle["claim"].strip() != project_claim:
                errors.append("frontier evidence claim does not match the project claim")

    discovery = bundle.get("discovery") if isinstance(bundle.get("discovery"), dict) else {}
    method = discovery.get("method")
    if method not in {"google-scholar-serpapi", "google-scholar-browser"}:
        errors.append("discovery.method must record a Google Scholar execution path")
    queries = discovery.get("queries") if isinstance(discovery.get("queries"), list) else []
    unique_queries: set[str] = set()
    query_hashes: set[str] = set()
    for index, query in enumerate(queries, start=1):
        label = f"query Q{index}"
        if not isinstance(query, dict):
            errors.append(f"{label}: entry must be an object")
            continue
        text = str(query.get("query") or "").strip()
        if not text:
            errors.append(f"{label}: query is blank")
        else:
            unique_queries.add(text.casefold())
        if not valid_url(query.get("url"), scholar=True):
            errors.append(f"{label}: url must be a Google Scholar URL")
        if not valid_date(query.get("retrieved_at")):
            errors.append(f"{label}: retrieved_at must be YYYY-MM-DD")
        validate_hashed_file(
            project,
            query.get("evidence_path"),
            query.get("evidence_sha256"),
            label,
            errors,
        )
        evidence_hash = str(query.get("evidence_sha256") or "")
        if evidence_hash in query_hashes:
            errors.append(f"{label}: evidence file duplicates another query")
        elif evidence_hash:
            query_hashes.add(evidence_hash)
    if len(unique_queries) < 2:
        errors.append("at least two distinct executed Scholar queries are required")

    papers = bundle.get("papers") if isinstance(bundle.get("papers"), list) else []
    paper_ids: set[str] = set()
    paper_statuses: dict[str, str] = {}
    solution_card_ids: set[str] = set()
    proof_read = 0
    solution_cards = 0
    for index, paper in enumerate(papers, start=1):
        label = f"paper P{index}"
        if not isinstance(paper, dict):
            errors.append(f"{label}: entry must be an object")
            continue
        paper_id = str(paper.get("id") or "").strip()
        label = f"paper {paper_id or f'P{index}'}"
        if not paper_id:
            errors.append(f"{label}: missing id")
        elif paper_id in paper_ids:
            errors.append(f"{label}: duplicate id")
        else:
            paper_ids.add(paper_id)
        for field in ["title", "authors", "year", "identifier", "verification_url"]:
            if not filled(paper.get(field)):
                errors.append(f"{label}: missing {field}")
        if not isinstance(paper.get("authors"), list) or not all(filled(author) for author in paper.get("authors", [])):
            errors.append(f"{label}: authors must be a nonempty list")
        if not isinstance(paper.get("year"), int) or not 1000 <= paper.get("year", 0) <= date.today().year + 1:
            errors.append(f"{label}: year must be a plausible integer")
        if not valid_url(paper.get("verification_url")):
            errors.append(f"{label}: verification_url must be an official HTTP(S) anchor")
        identifier = str(paper.get("identifier") or "").strip()
        verification_host = urllib.parse.urlparse(str(paper.get("verification_url") or "")).hostname or ""
        if identifier.lower().startswith("doi:") and verification_host != "doi.org":
            errors.append(f"{label}: DOI metadata must be anchored at doi.org")
        elif identifier.lower().startswith("arxiv:") and not verification_host.endswith("arxiv.org"):
            errors.append(f"{label}: arXiv metadata must be anchored at arxiv.org")
        elif not re.match(r"^(doi:10\.|arxiv:|official:)", identifier, flags=re.I):
            errors.append(f"{label}: identifier must be a DOI, arXiv ID, or official identifier")

        fulltext = paper.get("fulltext") if isinstance(paper.get("fulltext"), dict) else {}
        status = fulltext.get("status")
        if status not in FULLTEXT_STATUSES:
            errors.append(f"{label}: invalid fulltext.status")
            continue
        if paper_id:
            paper_statuses[paper_id] = status
        if status not in {"metadata-only", "not-retrieved"}:
            if not valid_url(fulltext.get("source_url")):
                errors.append(f"{label}: fulltext.source_url is missing or invalid")
            if not valid_date(fulltext.get("retrieved_at")):
                errors.append(f"{label}: fulltext.retrieved_at must be YYYY-MM-DD")
            for field in ["version", "access"]:
                if not filled(fulltext.get(field)):
                    errors.append(f"{label}: fulltext.{field} is missing")
            if fulltext.get("access") not in ACCESS_STATUSES:
                errors.append(f"{label}: fulltext.access is invalid")
            path = validate_hashed_file(
                project,
                fulltext.get("path"),
                fulltext.get("sha256"),
                f"{label} full text",
                errors,
                require_pdf=str(fulltext.get("path") or "").lower().endswith(".pdf"),
            )
            if path is not None and fulltext.get("bytes") not in {None, path.stat().st_size}:
                errors.append(f"{label}: fulltext.bytes does not match the file")
            source_archive = fulltext.get("source_archive")
            if isinstance(source_archive, dict):
                validate_hashed_file(
                    project,
                    source_archive.get("path"),
                    source_archive.get("sha256"),
                    f"{label} source archive",
                    errors,
                )

        if status in READ_STATUSES:
            for field in ["statement_anchor", "result", "assumptions", "gap_to_claim"]:
                if not filled(paper.get(field)):
                    errors.append(f"{label}: {field} is required after statement checking")
        if status == "proof-read":
            proof_read += 1
            if not filled(paper.get("proof_anchor")):
                errors.append(f"{label}: proof_anchor is required after proof reading")
            card = paper.get("solution_card") if isinstance(paper.get("solution_card"), dict) else {}
            card_fields = [
                "central_object",
                "proof_decomposition",
                "key_nonroutine_step",
                "transplantable_move",
                "new_bridge_lemma",
                "falsifier_or_evaluator",
            ]
            missing_card = [field for field in card_fields if not filled(card.get(field))]
            if missing_card:
                errors.append(f"{label}: incomplete solution_card ({', '.join(missing_card)})")
            else:
                solution_cards += 1
                solution_card_ids.add(paper_id)

    if not papers:
        errors.append("at least one closest paper must be verified")
    if proof_read < 1 or solution_cards < 1:
        errors.append("at least one closest paper must be proof-read with a complete solution_card")

    activity = bundle.get("activity") if isinstance(bundle.get("activity"), dict) else {}
    activity_queries = activity.get("queries") if isinstance(activity.get("queries"), list) else []
    signals = activity.get("signals") if isinstance(activity.get("signals"), list) else []
    if not any(filled(query) for query in activity_queries):
        errors.append("activity.queries must record a recent-work or cited-by check")
    for index, signal in enumerate(signals, start=1):
        if not isinstance(signal, dict):
            errors.append(f"activity signal {index}: entry must be an object")
            continue
        for field in ["title", "url", "date", "relationship"]:
            if not filled(signal.get(field)):
                errors.append(f"activity signal {index}: missing {field}")
        if filled(signal.get("url")) and not valid_url(signal.get("url")):
            errors.append(f"activity signal {index}: invalid URL")
    if not signals and not filled(activity.get("none_found_note")):
        errors.append("record active-work signals or an explicit bounded no-result note")

    frontier = bundle.get("frontier") if isinstance(bundle.get("frontier"), dict) else {}
    frontier_status = frontier.get("status")
    if frontier_status not in FRONTIER_STATUSES:
        errors.append("frontier.status is missing or invalid")
        frontier_status = None
    closest = frontier.get("closest_paper_ids") if isinstance(frontier.get("closest_paper_ids"), list) else []
    if not closest:
        errors.append("frontier.closest_paper_ids is empty")
    for paper_id in closest:
        if paper_id not in paper_ids:
            errors.append(f"frontier.closest_paper_ids contains unknown id: {paper_id}")
        elif paper_statuses.get(paper_id) not in READ_STATUSES:
            errors.append(f"closest paper {paper_id} has not been statement-checked")
    if closest and not any(paper_id in solution_card_ids for paper_id in closest):
        errors.append("at least one closest paper must be proof-read with a complete solution_card")
    for field in ["exact_gap", "assessment"]:
        if not filled(frontier.get(field)):
            errors.append(f"frontier.{field} is blank")
    if frontier_status == "genuinely-new":
        warnings.append("a bounded scan cannot prove novelty; use genuinely-new only with unusually strong coverage")

    return {
        "ok": not errors,
        "path": str(manifest_path(project)),
        "errors": errors,
        "warnings": warnings,
        "frontier_status": frontier_status,
        "counts": {
            "queries": len(unique_queries),
            "papers": len(papers),
            "proof_read": proof_read,
            "solution_cards": solution_cards,
        },
    }


def safe_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-.")
    return cleaned[:80] or "paper"


def request_json(
    url: str,
    *,
    timeout: int = 45,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str, destination: Path, *, require_pdf: bool = True) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.8"})
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temp:
        temp_path = Path(temp.name)
        total = 0
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                final_url = response.geturl()
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_BYTES:
                        raise ValueError("download exceeds 200 MB guard")
                    temp.write(chunk)
            if total == 0:
                raise ValueError("empty download")
            with temp_path.open("rb") as handle:
                if require_pdf and handle.read(5) != b"%PDF-":
                    raise ValueError("downloaded response is not a PDF")
            temp_path.replace(destination)
            return {
                "path": destination,
                "bytes": total,
                "sha256": sha256_file(destination),
                "final_url": final_url,
            }
        except Exception:
            temp_path.unlink(missing_ok=True)
            raise


def normalize_arxiv_id(value: str) -> str:
    match = re.search(r"(?:arxiv\.org/(?:abs|pdf)/)?([A-Za-z-]+/\d{7}|\d{4}\.\d{4,5})(v\d+)?", value)
    if not match:
        raise ValueError(f"invalid arXiv id: {value}")
    return f"{match.group(1)}{match.group(2) or ''}"


def normalize_ssrn_id(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    for key, values in urllib.parse.parse_qs(parsed.query).items():
        if key.casefold().replace("_", "") == "abstractid" and values:
            if re.fullmatch(r"\d{4,10}", values[0]):
                return values[0]
    explicit = re.search(r"abstract(?:[_-]?id)?=(\d{4,10})", value, flags=re.I)
    if explicit:
        return explicit.group(1)
    doi_match = re.search(r"10\.2139/ssrn\.(\d{4,10})", value, flags=re.I)
    if doi_match:
        return doi_match.group(1)
    label_match = re.search(r"ssrn(?:_id|[.:/_-])(\d{4,10})(?:\D|$)", value, flags=re.I)
    if label_match:
        return label_match.group(1)
    if re.fullmatch(r"\d{4,10}", value.strip()):
        return value.strip()
    raise ValueError(f"invalid SSRN abstract id: {value}")


def validate_ssrn_signed_url(url: str, ssrn_id: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if (parsed.hostname or "").casefold() != "download.ssrn.com":
        raise ValueError("--ssrn-signed-url must use download.ssrn.com")
    query = {key.casefold(): values for key, values in urllib.parse.parse_qs(parsed.query).items()}
    abstract_ids = query.get("abstractid") or []
    if not abstract_ids:
        raise ValueError("signed URL is missing abstractId")
    if abstract_ids[0] != ssrn_id:
        raise ValueError("signed URL abstractId does not match --ssrn")
    dates = query.get("x-amz-date") or []
    expiries = query.get("x-amz-expires") or []
    if not dates or not expiries:
        raise ValueError("signed URL is missing AWS expiry fields")
    issued = datetime.strptime(dates[0], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    expires_at = issued.timestamp() + int(expiries[0])
    if datetime.now(timezone.utc).timestamp() >= expires_at:
        raise ValueError("SSRN signed URL has expired; request a fresh browser download link")


def normalized_words(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value.replace("&", " and ")).encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", ascii_value.casefold()))


def author_surnames(authors: list[str]) -> set[str]:
    surnames: set[str] = set()
    for author in authors:
        if "," in author:
            words = normalized_words(author.split(",", 1)[0]).split()
        else:
            words = normalized_words(author).split()
        if words:
            surnames.add(words[-1])
    return surnames


def same_work(candidate: dict[str, Any], metadata: dict[str, Any]) -> bool:
    if normalized_words(str(candidate.get("title") or "")) != normalized_words(str(metadata.get("title") or "")):
        return False
    expected_authors = author_surnames(list(metadata.get("authors") or []))
    candidate_authors = author_surnames(list(candidate.get("authors") or []))
    return not expected_authors or not candidate_authors or bool(expected_authors & candidate_authors)


def automatic_pdf_url(value: Any) -> str:
    if not valid_url(value):
        return ""
    url = str(value)
    host = (urllib.parse.urlparse(url).hostname or "").casefold()
    if (
        host == "ssrn.com"
        or host.endswith(".ssrn.com")
        or host in {"doi.org", "dx.doi.org", "hdl.handle.net"}
    ):
        return ""
    return url


def probe_pdf_url(url: str) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.8"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.read(5) != b"%PDF-":
            raise ValueError("candidate response is not a PDF")


def arxiv_metadata(arxiv_id: str) -> dict[str, Any]:
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": arxiv_id, "max_results": 1})
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=45) as response:
        root = ET.fromstring(response.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = root.find("a:entry", ns)
    if entry is None:
        raise ValueError(f"arXiv did not return metadata for {arxiv_id}")
    title = " ".join((entry.findtext("a:title", default="", namespaces=ns)).split())
    authors = [
        " ".join((node.findtext("a:name", default="", namespaces=ns)).split())
        for node in entry.findall("a:author", ns)
    ]
    published = entry.findtext("a:published", default="", namespaces=ns)
    return {"title": title, "authors": authors, "year": int(published[:4])}


def crossref_item_metadata(message: dict[str, Any]) -> dict[str, Any]:
    titles = message.get("title") or []
    authors = []
    for author in message.get("author") or []:
        name = " ".join(part for part in [author.get("given", ""), author.get("family", "")] if part).strip()
        if name:
            authors.append(name)
    year = 0
    for field in ["posted", "published-print", "published-online", "published", "issued", "created"]:
        date_value = message.get(field) or {}
        parts = (date_value.get("date-parts") or [[]])[0]
        if parts:
            year = int(parts[0])
            break
        date_time = str(date_value.get("date-time") or "")
        if re.match(r"^\d{4}", date_time):
            year = int(date_time[:4])
            break
    return {
        "doi": str(message.get("DOI") or ""),
        "title": titles[0] if titles else "",
        "authors": authors,
        "year": year,
    }


def crossref_metadata(doi: str) -> dict[str, Any]:
    encoded = urllib.parse.quote(doi, safe="")
    message = request_json(f"https://api.crossref.org/works/{encoded}").get("message", {})
    metadata = crossref_item_metadata(message)
    metadata["doi"] = metadata["doi"] or doi
    return metadata


def crossref_related_works(metadata: dict[str, Any], exclude_doi: str) -> list[dict[str, Any]]:
    query: dict[str, Any] = {
        "query.title": metadata.get("title") or "",
        "rows": 10,
    }
    authors = list(metadata.get("authors") or [])
    if authors:
        query["query.author"] = authors[0]
    data = request_json(f"https://api.crossref.org/works?{urllib.parse.urlencode(query)}")
    related: list[dict[str, Any]] = []
    seen: set[str] = {exclude_doi.casefold()}
    for item in (data.get("message") or {}).get("items") or []:
        candidate = crossref_item_metadata(item)
        doi = str(candidate.get("doi") or "")
        if not doi or doi.casefold() in seen or doi.casefold().startswith("10.2139/ssrn."):
            continue
        if same_work(candidate, metadata):
            seen.add(doi.casefold())
            related.append(candidate)
    return related


def unpaywall_open_access(doi: str, mailto: str) -> dict[str, Any]:
    if not mailto:
        raise ValueError("UNPAYWALL_EMAIL is not configured")
    encoded = urllib.parse.quote(doi, safe="")
    query = urllib.parse.urlencode({"email": mailto})
    data = request_json(f"https://api.unpaywall.org/v2/{encoded}?{query}")
    location = data.get("best_oa_location") or {}
    pdf_url = automatic_pdf_url(location.get("url_for_pdf"))
    if not pdf_url:
        raise ValueError("no non-SSRN open PDF")
    return {
        "url": pdf_url,
        "version": location.get("version") or "unknown",
        "access": "open-access",
        "license": location.get("license") or "unknown",
        "resolver": "unpaywall",
    }


def openalex_location(data: dict[str, Any]) -> dict[str, Any]:
    locations = [data.get("best_oa_location") or {}, *(data.get("locations") or [])]
    for location in locations:
        pdf_url = automatic_pdf_url(location.get("pdf_url"))
        if location.get("is_oa") and pdf_url:
            source = location.get("source") or {}
            return {
                "url": pdf_url,
                "version": location.get("version") or "open-access copy",
                "access": "open-access",
                "license": location.get("license") or "unknown",
                "resolver": f"openalex:{source.get('display_name') or 'location'}",
            }
    raise ValueError("no non-SSRN open PDF")


def openalex_open_access(doi: str, metadata: dict[str, Any], api_key: str = "") -> dict[str, Any]:
    query = {"select": "title,authorships,publication_year,best_oa_location,locations"}
    if api_key:
        query["api_key"] = api_key
    encoded = urllib.parse.quote(f"doi:{doi}", safe="")
    try:
        data = request_json(f"https://api.openalex.org/works/{encoded}?{urllib.parse.urlencode(query)}")
        return openalex_location(data)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        pass

    search_query = {
        "search": metadata.get("title") or "",
        "per-page": 10,
        "select": "title,authorships,publication_year,best_oa_location,locations",
    }
    if api_key:
        search_query["api_key"] = api_key
    data = request_json(f"https://api.openalex.org/works?{urllib.parse.urlencode(search_query)}")
    for item in data.get("results") or []:
        candidate = {
            "title": item.get("title") or "",
            "authors": [
                ((authorship.get("author") or {}).get("display_name") or "")
                for authorship in item.get("authorships") or []
            ],
        }
        if same_work(candidate, metadata):
            try:
                return openalex_location(item)
            except ValueError:
                continue
    raise ValueError("no exact-title non-SSRN open PDF")


def semantic_scholar_pdf(data: dict[str, Any]) -> dict[str, Any]:
    pdf = data.get("openAccessPdf") or {}
    pdf_url = automatic_pdf_url(pdf.get("url"))
    if not pdf_url:
        raise ValueError("no non-SSRN open PDF")
    return {
        "url": pdf_url,
        "version": "open-access copy",
        "access": "open-access",
        "license": pdf.get("license") or pdf.get("status") or "unknown",
        "resolver": "semantic-scholar-openAccessPdf",
    }


def semantic_scholar_open_access(
    doi: str,
    metadata: dict[str, Any],
    api_key: str = "",
) -> dict[str, Any]:
    fields = "title,authors,year,externalIds,openAccessPdf,url"
    headers = {"x-api-key": api_key} if api_key else {}
    encoded = urllib.parse.quote(f"DOI:{doi}", safe="")
    try:
        data = request_json(
            f"https://api.semanticscholar.org/graph/v1/paper/{encoded}?fields={fields}",
            headers=headers,
        )
        return semantic_scholar_pdf(data)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError):
        pass

    query = urllib.parse.urlencode(
        {"query": metadata.get("title") or "", "limit": 10, "fields": fields}
    )
    data = request_json(
        f"https://api.semanticscholar.org/graph/v1/paper/search?{query}",
        headers=headers,
    )
    for item in data.get("data") or []:
        candidate = {
            "title": item.get("title") or "",
            "authors": [author.get("name") or "" for author in item.get("authors") or []],
        }
        if same_work(candidate, metadata):
            try:
                return semantic_scholar_pdf(item)
            except ValueError:
                continue
    raise ValueError("no exact-title non-SSRN open PDF")


def doi_open_access(
    doi: str,
    mailto: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = metadata or crossref_metadata(doi)
    resolvers = [
        (
            "unpaywall",
            lambda: unpaywall_open_access(doi, mailto or os.environ.get("UNPAYWALL_EMAIL", "")),
        ),
        (
            "openalex",
            lambda: openalex_open_access(doi, metadata, os.environ.get("OPENALEX_API_KEY", "")),
        ),
        (
            "semantic-scholar",
            lambda: semantic_scholar_open_access(
                doi,
                metadata,
                os.environ.get("SEMANTIC_SCHOLAR_API_KEY", ""),
            ),
        ),
    ]
    failures: list[str] = []
    for name, resolver in resolvers:
        try:
            candidate = resolver()
            probe_pdf_url(candidate["url"])
            return candidate
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            failures.append(f"{name}={exc}")
    raise ValueError("no_authorized_pdf_found: " + "; ".join(failures))


def ssrn_open_access(
    doi: str,
    mailto: str,
    metadata: dict[str, Any],
) -> dict[str, Any]:
    failures: list[str] = []
    try:
        resolved = doi_open_access(doi, mailto, metadata)
        resolved.update({"identity_doi": doi, "identity_metadata": metadata})
        return resolved
    except ValueError as exc:
        failures.append(f"preprint={exc}")

    try:
        related = crossref_related_works(metadata, doi)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise ValueError("no_authorized_pdf_found: " + "; ".join([*failures, f"related-doi={exc}"])) from exc
    for item in related:
        related_doi = str(item["doi"])
        try:
            resolved = doi_open_access(related_doi, mailto, item)
            resolved.update({"identity_doi": related_doi, "identity_metadata": item})
            return resolved
        except ValueError as exc:
            failures.append(f"doi:{related_doi}={exc}")
    raise ValueError("no_authorized_pdf_found: " + "; ".join(failures))


def upsert_paper(bundle: dict[str, Any], paper: dict[str, Any]) -> None:
    papers = bundle.setdefault("papers", [])
    for index, existing in enumerate(papers):
        if existing.get("id") == paper["id"]:
            papers[index] = paper
            return
    papers.append(paper)


def base_paper(
    paper_id: str,
    title: str,
    authors: list[str],
    year: int,
    identifier: str,
    verification_url: str,
    fulltext: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": paper_id,
        "title": title,
        "authors": authors,
        "year": year,
        "identifier": identifier,
        "verification_url": verification_url,
        "fulltext": fulltext,
        "statement_anchor": "",
        "proof_anchor": "",
        "result": "",
        "assumptions": "",
        "gap_to_claim": "",
        "solution_card": {
            "central_object": "",
            "proof_decomposition": "",
            "key_nonroutine_step": "",
            "transplantable_move": "",
            "new_bridge_lemma": "",
            "falsifier_or_evaluator": "",
        },
    }


def cmd_init(args: argparse.Namespace) -> None:
    path = write_frontier_template(Path(args.project), args.claim, overwrite=args.overwrite)
    print(path)


def cmd_add_query(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    if not valid_url(args.scholar_url, scholar=True):
        raise ValueError("--scholar-url must point to scholar.google.com")
    evidence = Path(args.evidence).resolve()
    if not evidence.is_file():
        raise FileNotFoundError(evidence)
    bundle = load_bundle(project)
    queries = bundle.setdefault("discovery", {}).setdefault("queries", [])
    suffix = evidence.suffix or ".txt"
    destination = project / "literature" / "evidence" / f"q{len(queries) + 1:02d}{suffix}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if evidence != destination.resolve():
        shutil.copy2(evidence, destination)
    queries.append(
        {
            "query": args.query,
            "url": args.scholar_url,
            "retrieved_at": args.date or today(),
            "evidence_path": relative_to_project(project, destination),
            "evidence_sha256": sha256_file(destination),
        }
    )
    bundle["discovery"]["method"] = args.method
    save_bundle(project, bundle)
    print(destination)


def cmd_register_local(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    source = Path(args.path).resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() == ".pdf":
        with source.open("rb") as handle:
            if handle.read(5) != b"%PDF-":
                raise ValueError("local file does not have a PDF signature")
    destination = project / "literature" / "papers" / f"{safe_name(args.paper_id)}{source.suffix or '.bin'}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source != destination.resolve():
        shutil.copy2(source, destination)
    fulltext = {
        "status": "downloaded",
        "path": relative_to_project(project, destination),
        "source_url": args.source_url,
        "retrieved_at": args.date or today(),
        "sha256": sha256_file(destination),
        "bytes": destination.stat().st_size,
        "version": args.version,
        "access": args.access,
        "license": args.license,
    }
    paper = base_paper(
        args.paper_id,
        args.title,
        args.authors,
        args.year,
        args.identifier,
        args.verification_url,
        fulltext,
    )
    bundle = load_bundle(project)
    upsert_paper(bundle, paper)
    save_bundle(project, bundle)
    print(destination)


def cmd_fetch(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    if sum(bool(value) for value in [args.arxiv, args.doi, args.ssrn, args.url]) != 1:
        raise ValueError("choose exactly one of --arxiv, --doi, --ssrn, or --url")
    if args.ssrn_signed_url and not args.ssrn:
        raise ValueError("--ssrn-signed-url requires --ssrn")
    if args.fallback_url and not (args.doi or args.ssrn):
        raise ValueError("--fallback-url requires --doi or --ssrn")
    if args.fallback_url and args.ssrn_signed_url:
        raise ValueError("choose --fallback-url or --ssrn-signed-url, not both")
    if args.fallback_url and not automatic_pdf_url(args.fallback_url):
        raise ValueError("--fallback-url must be a non-SSRN direct HTTP(S) candidate")

    license_value = args.license
    resolver_name = ""
    related_identifiers: list[str] = []
    if args.arxiv:
        arxiv_id = normalize_arxiv_id(args.arxiv)
        metadata = arxiv_metadata(arxiv_id)
        title = args.title or metadata["title"]
        authors = args.authors or metadata["authors"]
        year = args.year or metadata["year"]
        identifier = f"arXiv:{arxiv_id}"
        verification_url = f"https://arxiv.org/abs/{arxiv_id}"
        source_url = f"https://arxiv.org/pdf/{arxiv_id}"
        download_url = source_url
        resolver_name = "arxiv"
        version = args.version or "preprint"
        access = "open-access"
        license_value = license_value or "see arXiv record"
    elif args.doi:
        doi = args.doi.strip().removeprefix("https://doi.org/").removeprefix("doi:")
        metadata = crossref_metadata(doi)
        title = args.title or metadata["title"]
        authors = args.authors or metadata["authors"]
        year = args.year or metadata["year"]
        identifier = f"doi:{doi}"
        verification_url = f"https://doi.org/{doi}"
        if args.fallback_url:
            source_url = args.fallback_url
            download_url = source_url
            resolver_name = "verified-web-candidate"
            version = args.version or "open copy"
            access = "open-access"
            license_value = license_value or "verify at source"
        else:
            resolved = doi_open_access(doi, args.mailto or "", metadata)
            source_url = resolved["url"]
            download_url = source_url
            resolver_name = resolved["resolver"]
            version = args.version or resolved["version"]
            access = resolved["access"]
            license_value = license_value or resolved["license"]
    elif args.ssrn:
        ssrn_id = normalize_ssrn_id(args.ssrn)
        if args.ssrn_signed_url:
            validate_ssrn_signed_url(args.ssrn_signed_url, ssrn_id)
        doi = f"10.2139/ssrn.{ssrn_id}"
        metadata = crossref_metadata(doi)
        if args.ssrn_signed_url:
            title = args.title or metadata["title"]
            authors = args.authors or metadata["authors"]
            year = args.year or metadata["year"]
            identifier = f"doi:{doi}"
            verification_url = f"https://doi.org/{doi}"
            source_url = f"https://papers.ssrn.com/sol3/papers.cfm?abstract_id={ssrn_id}"
            download_url = args.ssrn_signed_url
            resolver_name = "ssrn-browser-presigned"
            version = args.version or "SSRN preprint"
            access = "open-access"
            license_value = license_value or "see SSRN record"
        elif args.fallback_url:
            title = args.title or metadata["title"]
            authors = args.authors or metadata["authors"]
            year = args.year or metadata["year"]
            identifier = f"doi:{doi}"
            verification_url = f"https://doi.org/{doi}"
            source_url = args.fallback_url
            download_url = source_url
            resolver_name = "verified-web-candidate"
            version = args.version or "open copy"
            access = "open-access"
            license_value = license_value or "verify at source"
        else:
            resolved = ssrn_open_access(doi, args.mailto or "", metadata)
            identity_doi = str(resolved["identity_doi"])
            identity_metadata = resolved["identity_metadata"]
            title = args.title or identity_metadata["title"]
            authors = args.authors or identity_metadata["authors"]
            year = args.year or identity_metadata["year"]
            identifier = f"doi:{identity_doi}"
            verification_url = f"https://doi.org/{identity_doi}"
            if identity_doi.casefold() != doi.casefold():
                related_identifiers.append(f"doi:{doi}")
            source_url = resolved["url"]
            download_url = source_url
            resolver_name = resolved["resolver"]
            version = args.version or resolved["version"]
            access = resolved["access"]
            license_value = license_value or resolved["license"]
    else:
        if not all([args.title, args.authors, args.year, args.identifier, args.verification_url]):
            raise ValueError("--url requires --title, --authors, --year, --identifier, and --verification-url")
        title = args.title
        authors = args.authors
        year = args.year
        identifier = args.identifier
        verification_url = args.verification_url
        source_url = args.url
        download_url = source_url
        resolver_name = "direct-open-url"
        version = args.version or "open copy"
        access = args.access
        license_value = license_value or "unknown"

    destination = project / "literature" / "papers" / f"{safe_name(args.paper_id)}.pdf"
    try:
        result = download_file(download_url, destination, require_pdf=True)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
        host = urllib.parse.urlparse(download_url).hostname or "unknown host"
        raise ValueError(f"{resolver_name} failed at {host}: {exc}") from exc
    fulltext = {
        "status": "downloaded",
        "path": relative_to_project(project, destination),
        "source_url": source_url,
        "retrieved_at": args.date or today(),
        "sha256": result["sha256"],
        "bytes": result["bytes"],
        "version": version,
        "access": access,
        "license": license_value,
        "resolver": resolver_name,
    }
    if args.include_source and args.arxiv:
        source_destination = project / "literature" / "papers" / f"{safe_name(args.paper_id)}-source.tar"
        source_result = download_file(
            f"https://export.arxiv.org/e-print/{normalize_arxiv_id(args.arxiv)}",
            source_destination,
            require_pdf=False,
        )
        fulltext["source_archive"] = {
            "path": relative_to_project(project, source_destination),
            "source_url": f"https://export.arxiv.org/e-print/{normalize_arxiv_id(args.arxiv)}",
            "sha256": source_result["sha256"],
            "bytes": source_result["bytes"],
        }
    paper = base_paper(paper_id=args.paper_id, title=title, authors=authors, year=year, identifier=identifier, verification_url=verification_url, fulltext=fulltext)
    if related_identifiers:
        paper["related_identifiers"] = related_identifiers
    bundle = load_bundle(project)
    upsert_paper(bundle, paper)
    save_bundle(project, bundle)
    print(json.dumps({"paper_id": args.paper_id, "file": str(destination), "sha256": result["sha256"]}, indent=2))


def find_paper(bundle: dict[str, Any], paper_id: str) -> dict[str, Any]:
    for paper in bundle.get("papers", []):
        if paper.get("id") == paper_id:
            return paper
    raise ValueError(f"paper not found: {paper_id}")


def cmd_mark_read(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    bundle = load_bundle(project)
    paper = find_paper(bundle, args.paper_id)
    paper.setdefault("fulltext", {})["status"] = args.status
    paper.update(
        {
            "statement_anchor": args.statement_anchor,
            "proof_anchor": args.proof_anchor or "",
            "result": args.result,
            "assumptions": args.assumptions,
            "gap_to_claim": args.gap,
        }
    )
    if args.status == "proof-read":
        paper["solution_card"] = {
            "central_object": args.central_object,
            "proof_decomposition": args.proof_decomposition,
            "key_nonroutine_step": args.key_step,
            "transplantable_move": args.transplantable_move,
            "new_bridge_lemma": args.bridge_lemma,
            "falsifier_or_evaluator": args.evaluator,
        }
    save_bundle(project, bundle)


def cmd_set_activity(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    bundle = load_bundle(project)
    signals = []
    for raw in args.signal:
        parts = raw.split("||")
        if len(parts) != 4:
            raise ValueError("--signal must be TITLE||URL||DATE||RELATIONSHIP")
        signals.append(dict(zip(["title", "url", "date", "relationship"], parts)))
    bundle["activity"] = {
        "queries": args.query,
        "signals": signals,
        "none_found_note": args.none_found_note or "",
    }
    save_bundle(project, bundle)


def cmd_set_frontier(args: argparse.Namespace) -> None:
    project = Path(args.project).resolve()
    bundle = load_bundle(project)
    bundle["frontier"] = {
        "status": args.status,
        "closest_paper_ids": args.closest,
        "exact_gap": args.gap,
        "assessment": args.assessment,
    }
    bundle["limitations"] = args.limitation
    save_bundle(project, bundle)


def cmd_validate(args: argparse.Namespace) -> None:
    result = validate_frontier_bundle(Path(args.project))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if not result["ok"]:
        raise SystemExit(1)


def add_paper_metadata(parser: argparse.ArgumentParser, *, required: bool = False) -> None:
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--title", required=required)
    parser.add_argument("--authors", action="append", default=[], required=required)
    parser.add_argument("--year", type=int, required=required)
    parser.add_argument("--identifier", required=required)
    parser.add_argument("--verification-url", required=required)
    parser.add_argument("--version", default="")
    parser.add_argument("--access", choices=sorted(ACCESS_STATUSES), default="open-access")
    parser.add_argument("--license", default="")
    parser.add_argument("--date")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="create an empty frontier evidence bundle")
    init.add_argument("project")
    init.add_argument("--claim", required=True)
    init.add_argument("--overwrite", action="store_true")
    init.set_defaults(func=cmd_init)

    query = subparsers.add_parser("add-query", help="register one executed Scholar query and its raw evidence")
    query.add_argument("project")
    query.add_argument("--query", required=True)
    query.add_argument("--scholar-url", required=True)
    query.add_argument("--evidence", required=True)
    query.add_argument("--method", choices=["google-scholar-serpapi", "google-scholar-browser"], required=True)
    query.add_argument("--date")
    query.set_defaults(func=cmd_add_query)

    local = subparsers.add_parser("register-local", help="copy a lawful local full text into the evidence bundle")
    local.add_argument("project")
    local.add_argument("--path", required=True)
    local.add_argument("--source-url", required=True)
    add_paper_metadata(local, required=True)
    local.set_defaults(func=cmd_register_local)

    fetch = subparsers.add_parser("fetch", help="download one lawful open PDF and register it")
    fetch.add_argument("project")
    fetch.add_argument("--arxiv")
    fetch.add_argument("--doi")
    fetch.add_argument("--ssrn", help="SSRN abstract id or URL; resolves a non-SSRN lawful copy")
    fetch.add_argument(
        "--ssrn-signed-url",
        help="fresh browser-issued download.ssrn.com URL; valid only with --ssrn and never persisted",
    )
    fetch.add_argument(
        "--fallback-url",
        help="verified non-SSRN PDF candidate found by a bounded exact-title web search",
    )
    fetch.add_argument("--url")
    fetch.add_argument("--mailto", help="Unpaywall email; defaults to UNPAYWALL_EMAIL")
    fetch.add_argument("--include-source", action="store_true", help="also download the arXiv source archive")
    add_paper_metadata(fetch)
    fetch.set_defaults(func=cmd_fetch)

    read = subparsers.add_parser("mark-read", help="add exact theorem/proof anchors and a solution card")
    read.add_argument("project")
    read.add_argument("--paper-id", required=True)
    read.add_argument("--status", choices=["statement-checked", "proof-read"], required=True)
    read.add_argument("--statement-anchor", required=True)
    read.add_argument("--proof-anchor")
    read.add_argument("--result", required=True)
    read.add_argument("--assumptions", required=True)
    read.add_argument("--gap", required=True)
    read.add_argument("--central-object", default="")
    read.add_argument("--proof-decomposition", default="")
    read.add_argument("--key-step", default="")
    read.add_argument("--transplantable-move", default="")
    read.add_argument("--bridge-lemma", default="")
    read.add_argument("--evaluator", default="")
    read.set_defaults(func=cmd_mark_read)

    activity = subparsers.add_parser("set-activity", help="record recent cited-by or active-project checks")
    activity.add_argument("project")
    activity.add_argument("--query", action="append", required=True)
    activity.add_argument("--signal", action="append", default=[], help="TITLE||URL||DATE||RELATIONSHIP")
    activity.add_argument("--none-found-note")
    activity.set_defaults(func=cmd_set_activity)

    frontier = subparsers.add_parser("set-frontier", help="record the bounded frontier classification")
    frontier.add_argument("project")
    frontier.add_argument("--status", choices=sorted(FRONTIER_STATUSES), required=True)
    frontier.add_argument("--closest", action="append", required=True)
    frontier.add_argument("--gap", required=True)
    frontier.add_argument("--assessment", required=True)
    frontier.add_argument("--limitation", action="append", default=[])
    frontier.set_defaults(func=cmd_set_frontier)

    validate = subparsers.add_parser("validate", help="validate hashes, anchors, and frontier evidence")
    validate.add_argument("project")
    validate.set_defaults(func=cmd_validate)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
        return 0
    except (FileNotFoundError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
