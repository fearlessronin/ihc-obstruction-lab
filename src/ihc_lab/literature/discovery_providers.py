"""Discovery provider adapters for source metadata polling."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any, Protocol

from ihc_lab.literature.discovery_import import DiscoveredSource
from ihc_lab.literature.discovery_queries import DiscoveryQuery


class DiscoveryProvider(Protocol):
    def search(self, query: DiscoveryQuery) -> list[DiscoveredSource]:
        """Search for source metadata."""


def _source_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:80] or "source"


def _mock_source(
    query: DiscoveryQuery,
    source_id: str,
    title: str,
    authors: list[str],
    year: int | None,
    bibtex_key: str | None,
    extra_hints: list[str] | None = None,
) -> DiscoveredSource:
    hints = list(dict.fromkeys([*query.intended_channel_hints, *(extra_hints or [])]))
    return DiscoveredSource(
        discovery_id=f"mock_{query.query_id}_{source_id}",
        source_id=source_id,
        title=title,
        authors=authors,
        year=year,
        provider="mock",
        query_id=query.query_id,
        query_text=query.query_text,
        score=1.0,
        bibtex_key_candidate=bibtex_key,
        intended_channel_hints=hints,
        intended_bottleneck_hints=list(query.intended_bottleneck_hints),
        notes="Mock/offline discovery result for tests and CI.",
    )


class MockDiscoveryProvider:
    def search(self, query: DiscoveryQuery) -> list[DiscoveredSource]:
        text = query.query_text.lower()
        if "unramified" in text or "brauer" in text:
            source = _mock_source(
                query,
                "mock_colliot_theleme_voisin_unramified",
                "Mock unramified cohomology and integral Hodge source",
                ["Jean-Louis Colliot-Thélène", "Claire Voisin"],
                2012,
                "ColliotTheleneVoisin2012",
                ["brauer_unramified"],
            )
        elif "fermat" in text:
            source = _mock_source(
                query,
                "mock_fermat_lattice_source",
                "Mock Fermat lattice-saturation source",
                ["Enzo Aljovin", "Hossein Movasati", "Roberto Villaflor Loyola"],
                2019,
                "AljovinMovasatiVillaflor2019",
                ["lattice_saturation", "computed_lattice_benchmark"],
            )
        elif "matroid" in text:
            source = _mock_source(
                query,
                "mock_matroidal_abelian_source",
                "Mock matroidal parity and abelian-variety source",
                ["Engel", "Anton de Gaay Fortman", "Schreieder"],
                2025,
                "EngelDeGaayFortmanSchreieder2025",
                ["matroidal_parity", "abelian_variety_channel"],
            )
        elif "stack" in text or "stabilizer" in text:
            source = _mock_source(
                query,
                "mock_stacky_stabilizer_source",
                "Mock stack quotient stabilizer source",
                ["Burt Totaro"],
                1999,
                "Totaro1999ChowRingClassifyingSpace",
                ["stacky_stabilizer"],
            )
        else:
            source = _mock_source(
                query,
                f"mock_{_source_slug(query.query_text)}",
                f"Mock source for {query.query_text}",
                ["Unknown"],
                None,
                None,
                [],
            )
        return [source]


def _read_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _abstract_from_inverted_index(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    words: list[tuple[int, str]] = []
    for word, positions in index.items():
        for position in positions:
            words.append((position, word))
    return " ".join(word for _, word in sorted(words))


class OpenAlexDiscoveryProvider:
    def search(self, query: DiscoveryQuery) -> list[DiscoveredSource]:
        params = {"search": query.query_text, "per-page": str(query.max_results)}
        filters = []
        if query.year_from:
            filters.append(f"from_publication_date:{query.year_from}-01-01")
        if query.year_to:
            filters.append(f"to_publication_date:{query.year_to}-12-31")
        if filters:
            params["filter"] = ",".join(filters)
        url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
        payload = _read_json(url)
        results = []
        for item in payload.get("results", []):
            title = item.get("display_name") or "Untitled"
            source_id = f"openalex_{_source_slug(title)}"
            authors = [
                authorship.get("author", {}).get("display_name", "")
                for authorship in item.get("authorships", [])
            ]
            results.append(
                DiscoveredSource(
                    discovery_id=f"{query.query_id}_{source_id}",
                    source_id=source_id,
                    title=title,
                    authors=[author for author in authors if author],
                    year=item.get("publication_year"),
                    doi=item.get("doi"),
                    url=item.get("id"),
                    abstract=_abstract_from_inverted_index(item.get("abstract_inverted_index")),
                    provider="openalex",
                    query_id=query.query_id,
                    query_text=query.query_text,
                    score=item.get("relevance_score"),
                    intended_channel_hints=list(query.intended_channel_hints),
                    intended_bottleneck_hints=list(query.intended_bottleneck_hints),
                )
            )
        return results


class CrossrefDiscoveryProvider:
    def search(self, query: DiscoveryQuery) -> list[DiscoveredSource]:
        params = {"query": query.query_text, "rows": str(query.max_results)}
        url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
        payload = _read_json(url)
        results = []
        for item in payload.get("message", {}).get("items", []):
            title = (item.get("title") or ["Untitled"])[0]
            date_parts = (
                item.get("published-print", {}).get("date-parts")
                or item.get("published-online", {}).get("date-parts")
                or [[]]
            )
            year = date_parts[0][0] if date_parts and date_parts[0] else None
            authors = [
                " ".join(part for part in [author.get("given"), author.get("family")] if part)
                for author in item.get("author", [])
            ]
            source_id = f"crossref_{_source_slug(title)}"
            results.append(
                DiscoveredSource(
                    discovery_id=f"{query.query_id}_{source_id}",
                    source_id=source_id,
                    title=title,
                    authors=authors,
                    year=year,
                    venue=(item.get("container-title") or [None])[0],
                    doi=item.get("DOI"),
                    url=item.get("URL"),
                    abstract=item.get("abstract"),
                    provider="crossref",
                    query_id=query.query_id,
                    query_text=query.query_text,
                    intended_channel_hints=list(query.intended_channel_hints),
                    intended_bottleneck_hints=list(query.intended_bottleneck_hints),
                )
            )
        return results


class ArxivDiscoveryProvider:
    def search(self, query: DiscoveryQuery) -> list[DiscoveredSource]:
        params = {
            "search_query": f"all:{query.query_text}",
            "start": "0",
            "max_results": str(query.max_results),
        }
        url = "http://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=30) as response:
            root = ET.fromstring(response.read())
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        results = []
        for entry in root.findall("atom:entry", ns):
            title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
            url_id = entry.findtext("atom:id", default="", namespaces=ns)
            published = entry.findtext("atom:published", default="", namespaces=ns)
            year = int(published[:4]) if published[:4].isdigit() else None
            authors = [
                author.findtext("atom:name", default="", namespaces=ns)
                for author in entry.findall("atom:author", ns)
            ]
            arxiv_id = url_id.rsplit("/", 1)[-1] if url_id else None
            source_id = f"arxiv_{_source_slug(arxiv_id or title)}"
            results.append(
                DiscoveredSource(
                    discovery_id=f"{query.query_id}_{source_id}",
                    source_id=source_id,
                    title=title or "Untitled",
                    authors=[author for author in authors if author],
                    year=year,
                    arxiv_id=arxiv_id,
                    url=url_id,
                    abstract=(
                        entry.findtext("atom:summary", default="", namespaces=ns) or ""
                    ).strip(),
                    provider="arxiv",
                    query_id=query.query_id,
                    query_text=query.query_text,
                    intended_channel_hints=list(query.intended_channel_hints),
                    intended_bottleneck_hints=list(query.intended_bottleneck_hints),
                )
            )
        return results


def create_discovery_provider(provider_name: str, allow_network: bool = False) -> DiscoveryProvider:
    if provider_name == "mock":
        return MockDiscoveryProvider()
    if provider_name == "manual":
        raise RuntimeError("Manual discovery import does not use a provider.")
    if provider_name in {"openalex", "crossref", "arxiv"} and not allow_network:
        raise RuntimeError(
            "Network discovery is disabled by default. Pass --allow-network to query external providers."
        )
    if provider_name == "openalex":
        return OpenAlexDiscoveryProvider()
    if provider_name == "crossref":
        return CrossrefDiscoveryProvider()
    if provider_name == "arxiv":
        return ArxivDiscoveryProvider()
    raise ValueError(f"unknown discovery provider: {provider_name}")
