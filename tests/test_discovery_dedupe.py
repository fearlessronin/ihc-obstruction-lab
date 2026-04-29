from __future__ import annotations

from ihc_lab.literature.discovery_dedupe import (
    deduplicate_discovered_sources,
    normalize_title,
    source_fingerprint,
)
from ihc_lab.literature.discovery_import import DiscoveredSource


def _source(discovery_id: str, title: str, doi: str | None = None) -> DiscoveredSource:
    return DiscoveredSource(
        discovery_id=discovery_id,
        source_id=f"source_{discovery_id}",
        title=title,
        doi=doi,
    )


def test_normalize_title_and_fingerprint() -> None:
    assert normalize_title("A Title: With, Punctuation!") == "a title with punctuation"
    assert source_fingerprint("Ignored", doi="10.1/ABC") == "doi:10.1/abc"


def test_duplicate_titles_are_deduped() -> None:
    sources = [_source("a", "Same Title"), _source("b", "Same title!")]

    unique, duplicates = deduplicate_discovered_sources(sources, existing_sources=[])

    assert len(unique) == 1
    assert len(duplicates) == 1
    assert duplicates[0]["reason"] == "duplicate_discovery_match"


def test_duplicate_doi_is_deduped() -> None:
    sources = [_source("a", "First", "10.1/example"), _source("b", "Second", "10.1/EXAMPLE")]

    unique, duplicates = deduplicate_discovered_sources(sources, existing_sources=[])

    assert len(unique) == 1
    assert len(duplicates) == 1


def test_unique_sources_preserved() -> None:
    sources = [_source("a", "First"), _source("b", "Second")]

    unique, duplicates = deduplicate_discovered_sources(sources, existing_sources=[])

    assert len(unique) == 2
    assert duplicates == []
