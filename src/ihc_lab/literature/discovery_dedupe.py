"""Deduplication helpers for discovered literature metadata."""

from __future__ import annotations

import json
import re
import string
from pathlib import Path

from ihc_lab.channels import ObstructionChannel
from ihc_lab.literature.discovery_import import DiscoveredSource
from ihc_lab.literature.sources import LiteratureSource, load_literature_sources


def normalize_title(title: str) -> str:
    table = str.maketrans("", "", string.punctuation)
    return re.sub(r"\s+", " ", title.lower().translate(table)).strip()


def source_fingerprint(title: str, doi: str | None = None, arxiv_id: str | None = None) -> str:
    if doi:
        return f"doi:{doi.lower().strip()}"
    if arxiv_id:
        return f"arxiv:{arxiv_id.lower().strip()}"
    return f"title:{normalize_title(title)}"


def _load_json_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_existing_source_fingerprints() -> dict[str, str]:
    fingerprints: dict[str, str] = {}
    source_paths = [
        Path("data/literature_queue/raw_sources.sample.json"),
        Path("data/literature_queue/raw_sources.pilot.json"),
    ]
    for path in source_paths:
        if not path.exists():
            continue
        for source in load_literature_sources(path):
            fingerprints[source_fingerprint(source.title, source.doi, source.arxiv_id)] = (
                source.source_id
            )
            if source.bibtex_key:
                fingerprints[f"bibtex:{source.bibtex_key.lower()}"] = source.source_id

    for path in [
        Path("data/canonical_literature_rows.json"),
        Path("data/seed_rows.json"),
        Path("data/literature_queue/canonical_literature.candidates.json"),
    ]:
        for row in _load_json_rows(path):
            record = ObstructionChannel.from_dict(row)
            fingerprints[source_fingerprint(record.display_name)] = record.id
            for citation in record.citation_keys:
                fingerprints[f"bibtex:{citation.lower()}"] = record.id
    return fingerprints


def _fingerprints_for_source(source: DiscoveredSource | LiteratureSource) -> list[str]:
    keys = [source_fingerprint(source.title, source.doi, source.arxiv_id)]
    bibtex = getattr(source, "bibtex_key_candidate", None) or getattr(source, "bibtex_key", None)
    if bibtex:
        keys.append(f"bibtex:{bibtex.lower()}")
    return keys


def deduplicate_discovered_sources(
    discovered: list[DiscoveredSource],
    existing_sources: list[LiteratureSource] | None = None,
) -> tuple[list[DiscoveredSource], list[dict]]:
    existing = collect_existing_source_fingerprints()
    if existing_sources is not None:
        existing = {}
        for source in existing_sources:
            for key in _fingerprints_for_source(source):
                existing[key] = source.source_id

    seen: dict[str, str] = {}
    unique: list[DiscoveredSource] = []
    duplicates: list[dict] = []
    for source in discovered:
        keys = _fingerprints_for_source(source)
        matched_existing = next((existing[key] for key in keys if key in existing), None)
        matched_seen = next((seen[key] for key in keys if key in seen), None)
        if matched_existing:
            duplicates.append(
                {
                    "discovery_id": source.discovery_id,
                    "source_id": source.source_id,
                    "matched_existing": matched_existing,
                    "reason": "existing_source_match",
                }
            )
            continue
        if matched_seen:
            duplicates.append(
                {
                    "discovery_id": source.discovery_id,
                    "source_id": source.source_id,
                    "matched_existing": matched_seen,
                    "reason": "duplicate_discovery_match",
                }
            )
            continue
        unique.append(source)
        for key in keys:
            seen[key] = source.source_id
    return unique, duplicates
