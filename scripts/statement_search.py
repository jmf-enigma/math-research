#!/usr/bin/env python3
"""Query a mathematical statement index and emit a candidate-only packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SERVICE_CONFIG = {
    "matlas": {
        "name": "Matlas",
        "endpoint": "https://matlas.ai/api/search",
        "paper": "https://arxiv.org/abs/2604.17484",
        "privacy": None,
        "corpus_role": "curated published papers and textbooks",
    },
    "theoremsearch": {
        "name": "TheoremSearch",
        "endpoint": "https://api.theoremsearch.com/search",
        "paper": "https://arxiv.org/abs/2602.05216",
        "privacy": "https://www.theoremsearch.com/privacy",
        "corpus_role": "arXiv and open mathematical sources",
    },
}
SCHEMA_VERSION = "statement-retrieval/v1"
USER_AGENT = "MathResearch/1.0 (mathematical retrieval)"
MAX_QUERY_CHARS = 6000
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
VALID_INTENTS = (
    "theorem",
    "construction",
    "example",
    "counterexample",
    "background",
    "proof-trick",
    "obstruction",
)


class RetrievalError(RuntimeError):
    """A bounded, user-facing statement-retrieval failure."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_doi(raw: str) -> str:
    value = urllib.parse.unquote(raw.strip()).lower()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    value = re.sub(r"^(?:dx\.)?doi\.org/", "", value)
    value = re.sub(r"^doi:\s*", "", value)
    return value.strip().rstrip(".,;)")


def normalize_source_url(raw: str) -> str:
    value = raw.strip()
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme == "http" and parsed.netloc.casefold() in {"arxiv.org", "www.arxiv.org"}:
        return urllib.parse.urlunsplit(("https", parsed.netloc, parsed.path, parsed.query, parsed.fragment))
    return value


def validate_query(raw: str) -> str:
    query = compact_whitespace(raw)
    if not query:
        raise RetrievalError("query must be non-empty")
    if len(query) > MAX_QUERY_CHARS:
        raise RetrievalError(
            f"query exceeds {MAX_QUERY_CHARS} characters; send an abstracted local subgoal, "
            "not a full paper or confidential note"
        )
    return query


def validate_endpoint(raw: str) -> str:
    endpoint = raw.strip()
    parsed = urllib.parse.urlsplit(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RetrievalError("statement-search endpoint must be an absolute HTTPS URL")
    return endpoint


def parse_response_bytes(payload: bytes, service: str) -> list[Any]:
    if len(payload) > MAX_RESPONSE_BYTES:
        raise RetrievalError("statement-search response exceeded the bounded response size")
    try:
        data = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetrievalError("statement-search service returned invalid JSON") from exc

    if service == "matlas":
        if not isinstance(data, list):
            raise RetrievalError("Matlas response must be a JSON list")
        return data

    if not isinstance(data, dict) or not isinstance(data.get("theorems"), list):
        raise RetrievalError("TheoremSearch response must contain a JSON theorem list")
    return data["theorems"]


def request_payload(
    service: str,
    query: str,
    num_results: int,
    filters: dict[str, Any],
) -> dict[str, Any]:
    if service == "matlas":
        return {"query": query, "num_results": num_results}
    return {"query": query, "n_results": num_results, **filters}


def fetch_results(
    query: str,
    *,
    service: str,
    endpoint: str,
    num_results: int,
    filters: dict[str, Any],
    timeout_seconds: float,
) -> list[Any]:
    body = json.dumps(
        request_payload(service, query, num_results, filters),
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        detail = exc.read(2048).decode("utf-8", errors="replace").strip()
        suffix = f": {detail}" if detail else ""
        raise RetrievalError(
            f"{SERVICE_CONFIG[service]['name']} HTTP {exc.code}{suffix}"
        ) from exc
    except urllib.error.URLError as exc:
        raise RetrievalError(
            f"{SERVICE_CONFIG[service]['name']} request failed: {exc.reason}"
        ) from exc
    except TimeoutError as exc:
        raise RetrievalError(f"{SERVICE_CONFIG[service]['name']} request timed out") from exc
    return parse_response_bytes(payload, service)


def load_results(path: Path, service: str) -> list[Any]:
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise RetrievalError(f"could not read response fixture: {path}") from exc
    return parse_response_bytes(payload, service)


def clean_field(item: dict[str, Any], name: str) -> str:
    value = item.get(name, "")
    return compact_whitespace(str(value)) if value is not None else ""


def clean_authors(value: Any) -> list[str]:
    if isinstance(value, list):
        return [compact_whitespace(str(author)) for author in value if str(author).strip()]
    text = compact_whitespace(str(value)) if value is not None else ""
    return [text] if text else []


def clean_number(value: Any) -> int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None


def verification_template() -> dict[str, str]:
    return {
        "metadata": "pending",
        "source_context": "pending",
        "definitions": "pending",
        "assumption_mapping": "pending",
        "proof_read": "pending",
        "applicability": "unverified",
    }


def normalize_matlas_candidate(item: dict[str, Any], raw_rank: int) -> dict[str, Any] | None:
    statement = clean_field(item, "statement")
    if not statement:
        return None
    doi = normalize_doi(clean_field(item, "doi"))
    return {
        "service": "matlas",
        "raw_rank": raw_rank,
        "theorem_type": clean_field(item, "type"),
        "theorem_name": clean_field(item, "entity_name"),
        "title": clean_field(item, "title"),
        "authors": clean_authors(item.get("authors")),
        "source_name": clean_field(item, "journal"),
        "year": clean_field(item, "year"),
        "identifiers": {"doi": doi, "arxiv_id": ""},
        "source_url": f"https://doi.org/{doi}" if doi else "",
        "candidate_id": clean_field(item, "candidate_id"),
        "slogan": "",
        "statement": statement,
        "statement_sha256": sha256_text(compact_whitespace(statement).casefold()),
        "similarity": None,
        "score": None,
        "citations": None,
        "evidence_status": "retrieved-unverified",
        "verification": verification_template(),
    }


def normalize_theoremsearch_candidate(
    item: dict[str, Any], raw_rank: int
) -> dict[str, Any] | None:
    statement = clean_field(item, "body")
    if not statement:
        return None
    paper = item.get("paper") if isinstance(item.get("paper"), dict) else {}
    source_name = clean_field(paper, "source")
    paper_id = clean_field(paper, "paper_id")
    arxiv_id = paper_id if source_name.casefold() == "arxiv" else ""
    source_url = normalize_source_url(clean_field(item, "link") or clean_field(paper, "link"))
    if not source_url and arxiv_id:
        source_url = f"https://arxiv.org/abs/{arxiv_id}"
    theorem_id = clean_number(item.get("theorem_id"))
    slogan_id = clean_number(item.get("slogan_id"))
    candidate_id = ":".join(
        str(part) for part in ("theoremsearch", theorem_id, slogan_id) if part is not None
    )
    return {
        "service": "theoremsearch",
        "raw_rank": raw_rank,
        "theorem_type": clean_field(item, "theorem_type"),
        "theorem_name": clean_field(item, "name"),
        "title": clean_field(paper, "title"),
        "authors": clean_authors(paper.get("authors")),
        "source_name": source_name,
        "year": clean_field(paper, "year"),
        "identifiers": {"doi": "", "arxiv_id": arxiv_id},
        "source_url": source_url,
        "candidate_id": candidate_id,
        "slogan": clean_field(item, "slogan"),
        "statement": statement,
        "statement_sha256": sha256_text(compact_whitespace(statement).casefold()),
        "similarity": clean_number(item.get("similarity")),
        "score": clean_number(item.get("score")),
        "citations": clean_number(paper.get("citations")),
        "evidence_status": "retrieved-unverified",
        "verification": verification_template(),
    }


def normalize_candidate(
    service: str,
    item: dict[str, Any],
    raw_rank: int,
) -> dict[str, Any] | None:
    if service == "matlas":
        return normalize_matlas_candidate(item, raw_rank)
    return normalize_theoremsearch_candidate(item, raw_rank)


def candidate_key(candidate: dict[str, Any]) -> tuple[str, str, str, str, str]:
    identifiers = candidate["identifiers"]
    return (
        candidate["service"],
        str(identifiers.get("doi") or identifiers.get("arxiv_id") or candidate["source_url"]),
        candidate["theorem_name"].casefold(),
        candidate["title"].casefold(),
        candidate["statement_sha256"],
    )


def privacy_warning(service: str) -> str:
    if service == "theoremsearch":
        return (
            "TheoremSearch states that it logs query text and filters; abstract unpublished or "
            "sensitive mathematics before retrieval."
        )
    return (
        "No public Matlas query-retention policy was verified; treat the query as disclosed to a "
        "third-party service."
    )


def build_packet(
    *,
    query: str,
    intent: str,
    service: str,
    endpoint: str,
    filters: dict[str, Any],
    raw_results: list[Any],
    retrieved_at: str | None = None,
    source_mode: str = "remote",
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str]] = set()
    invalid_count = 0
    duplicate_count = 0
    for raw_rank, item in enumerate(raw_results, start=1):
        if not isinstance(item, dict):
            invalid_count += 1
            continue
        candidate = normalize_candidate(service, item, raw_rank)
        if candidate is None:
            invalid_count += 1
            continue
        key = candidate_key(candidate)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        candidate["rank"] = len(candidates) + 1
        candidates.append(candidate)

    warnings = [
        privacy_warning(service),
        "Retrieval rank is not relevance, applicability, or correctness evidence.",
        "Verify source metadata, local definitions, exact assumptions, and the source proof before use.",
        "This packet cannot upgrade proof status or establish that a result is known, open, or new.",
    ]
    if invalid_count:
        warnings.append(f"Skipped {invalid_count} malformed or statement-free result(s).")
    if duplicate_count:
        warnings.append(f"Removed {duplicate_count} exact duplicate result(s).")

    config = SERVICE_CONFIG[service]
    return {
        "schema_version": SCHEMA_VERSION,
        "retrieved_at_utc": retrieved_at or utc_now(),
        "service": {
            "id": service,
            "name": config["name"],
            "endpoint": endpoint,
            "paper": config["paper"],
            "privacy": config["privacy"],
            "corpus_role": config["corpus_role"],
            "source_mode": source_mode,
        },
        "query": {
            "text": query,
            "sha256": sha256_text(query),
            "intent": intent,
            "filters": filters,
        },
        "evidence_status": "retrieved-unverified",
        "proof_effect": "none",
        "result_count_raw": len(raw_results),
        "result_count_unique": len(candidates),
        "duplicates_removed": duplicate_count,
        "invalid_results_skipped": invalid_count,
        "warnings": warnings,
        "candidates": candidates,
    }


def generated_project_path(project: Path, packet: dict[str, Any]) -> Path:
    stamp = str(packet["retrieved_at_utc"]).replace("-", "").replace(":", "")
    intent = str(packet["query"]["intent"])
    query_hash = str(packet["query"]["sha256"])[:12]
    service = str(packet["service"]["id"])
    directory = project.resolve() / "literature" / "statement-search" / service
    directory.mkdir(parents=True, exist_ok=True)
    base = directory / f"{stamp}-{intent}-{query_hash}.json"
    if not base.exists():
        return base
    for index in range(2, 1000):
        candidate = base.with_name(f"{base.stem}-{index}{base.suffix}")
        if not candidate.exists():
            return candidate
    raise RetrievalError("could not allocate a unique statement-search packet path")


def write_packet(path: Path, packet: dict[str, Any]) -> None:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RetrievalError(f"refusing to overwrite existing packet: {path}")
    payload = json.dumps(packet, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(payload)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    except OSError as exc:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        raise RetrievalError(f"could not write statement-search packet: {path}") from exc


def compact_summary(packet: dict[str, Any], output_path: Path | None) -> dict[str, Any]:
    top = []
    for candidate in packet["candidates"][:3]:
        top.append(
            {
                "rank": candidate["rank"],
                "theorem_name": candidate["theorem_name"],
                "title": candidate["title"],
                "identifiers": candidate["identifiers"],
                "source_url": candidate["source_url"],
            }
        )
    return {
        "ok": True,
        "service": packet["service"]["id"],
        "evidence_status": packet["evidence_status"],
        "proof_effect": packet["proof_effect"],
        "result_count_raw": packet["result_count_raw"],
        "result_count_unique": packet["result_count_unique"],
        "output_path": str(output_path) if output_path else None,
        "top_candidates": top,
    }


def theoremsearch_filters(args: argparse.Namespace) -> dict[str, Any]:
    filters: dict[str, Any] = {}
    if args.source:
        filters["sources"] = args.source
    if args.result_type:
        filters["types"] = args.result_type
    if args.tag:
        filters["tags"] = args.tag
    if args.year_range:
        filters["year_range"] = args.year_range
    if args.citation_range:
        filters["citation_range"] = args.citation_range
    if args.citation_weight:
        filters["citation_weight"] = args.citation_weight
    return filters


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve Matlas or TheoremSearch statement candidates without treating them as proof evidence."
        )
    )
    parser.add_argument("query", help="A complete, abstracted mathematical statement or subgoal")
    parser.add_argument("--service", choices=sorted(SERVICE_CONFIG), default="matlas")
    parser.add_argument("--intent", choices=VALID_INTENTS, default="theorem")
    parser.add_argument("--num-results", type=int, default=10)
    parser.add_argument("--endpoint", help="Override the selected service's HTTPS endpoint")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--remote-ok",
        action="store_true",
        help="Confirm that the abstracted query may be sent to the selected public service",
    )
    parser.add_argument(
        "--response-file",
        type=Path,
        help="Build a packet from a saved service response without network access",
    )
    parser.add_argument("--source", action="append", help="TheoremSearch source filter")
    parser.add_argument(
        "--result-type",
        action="append",
        help="TheoremSearch result type filter, such as Theorem or Lemma",
    )
    parser.add_argument("--tag", action="append", help="TheoremSearch arXiv tag filter")
    parser.add_argument("--year-range", type=int, nargs=2, metavar=("MIN", "MAX"))
    parser.add_argument("--citation-range", type=int, nargs=2, metavar=("MIN", "MAX"))
    parser.add_argument("--citation-weight", type=float, default=0.0)
    destination = parser.add_mutually_exclusive_group()
    destination.add_argument(
        "--project",
        type=Path,
        help="Write under PROJECT/literature/statement-search/SERVICE",
    )
    destination.add_argument("--output", type=Path, help="Write to an explicit new JSON path")
    parser.add_argument(
        "--print-full",
        action="store_true",
        help="Print the full packet even when it is also written to disk",
    )
    return parser


def validate_args(args: argparse.Namespace, filters: dict[str, Any]) -> None:
    lower, upper = (10, 200) if args.service == "matlas" else (1, 50)
    if not lower <= args.num_results <= upper:
        raise RetrievalError(
            f"--num-results for {args.service} must be between {lower} and {upper}"
        )
    if not 1.0 <= args.timeout <= 120.0:
        raise RetrievalError("--timeout must be between 1 and 120 seconds")
    if not 0.0 <= args.citation_weight <= 1.0:
        raise RetrievalError("--citation-weight must be between 0 and 1")
    for name in ("year_range", "citation_range"):
        value = getattr(args, name)
        if value is not None and (value[0] < 0 or value[0] > value[1]):
            raise RetrievalError(f"--{name.replace('_', '-')} must be an increasing nonnegative pair")
    if args.service == "matlas" and filters:
        raise RetrievalError("source, type, year, citation, and tag filters require TheoremSearch")
    if args.response_file is None and not args.remote_ok:
        raise RetrievalError(
            "remote search sends query text to a third-party service; abstract sensitive work "
            "and pass --remote-ok"
        )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        query = validate_query(args.query)
        filters = theoremsearch_filters(args)
        validate_args(args, filters)
        default_endpoint = str(SERVICE_CONFIG[args.service]["endpoint"])
        endpoint = validate_endpoint(args.endpoint or default_endpoint)

        if args.response_file is not None:
            raw_results = load_results(args.response_file.expanduser().resolve(), args.service)
            source_mode = "saved-response"
        else:
            raw_results = fetch_results(
                query,
                service=args.service,
                endpoint=endpoint,
                num_results=args.num_results,
                filters=filters,
                timeout_seconds=args.timeout,
            )
            source_mode = "remote"

        packet = build_packet(
            query=query,
            intent=args.intent,
            service=args.service,
            endpoint=endpoint,
            filters=filters,
            raw_results=raw_results,
            source_mode=source_mode,
        )
        output_path: Path | None = None
        if args.project is not None:
            output_path = generated_project_path(args.project.expanduser(), packet)
            write_packet(output_path, packet)
        elif args.output is not None:
            output_path = args.output.expanduser().resolve()
            write_packet(output_path, packet)

        rendered = packet if output_path is None or args.print_full else compact_summary(packet, output_path)
        print(json.dumps(rendered, indent=2, ensure_ascii=False, sort_keys=True))
        return 0
    except RetrievalError as exc:
        print(f"statement_search: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
