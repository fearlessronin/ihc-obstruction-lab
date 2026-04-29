"""Discovered source schema and import helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ihc_lab.literature.sources import LiteratureSource


@dataclass
class DiscoveredSource:
    discovery_id: str
    source_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    abstract: str | None = None
    provider: str = "mock"
    query_id: str = "unknown"
    query_text: str = "unknown"
    score: float | None = None
    bibtex_key_candidate: str | None = None
    intended_channel_hints: list[str] = field(default_factory=list)
    intended_bottleneck_hints: list[str] = field(default_factory=list)
    discovery_status: str = "discovered_unreviewed"
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.discovery_id or not self.discovery_id.strip():
            raise ValueError("discovery_id is required")
        if not self.source_id or not self.source_id.strip():
            raise ValueError("source_id is required")
        if not self.title or not self.title.strip():
            raise ValueError("title is required")
        self.authors = list(self.authors or [])
        if self.year in ("", None):
            self.year = None
        else:
            self.year = int(self.year)
        self.intended_channel_hints = list(self.intended_channel_hints or [])
        self.intended_bottleneck_hints = list(self.intended_bottleneck_hints or [])
        if not self.discovery_status:
            self.discovery_status = "discovered_unreviewed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "discovery_id": self.discovery_id,
            "source_id": self.source_id,
            "title": self.title,
            "authors": list(self.authors),
            "year": self.year,
            "venue": self.venue,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "url": self.url,
            "abstract": self.abstract,
            "provider": self.provider,
            "query_id": self.query_id,
            "query_text": self.query_text,
            "score": self.score,
            "bibtex_key_candidate": self.bibtex_key_candidate,
            "intended_channel_hints": list(self.intended_channel_hints),
            "intended_bottleneck_hints": list(self.intended_bottleneck_hints),
            "discovery_status": self.discovery_status,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "DiscoveredSource") -> "DiscoveredSource":
        if isinstance(data, cls):
            return data
        return cls(
            discovery_id=data["discovery_id"],
            source_id=data["source_id"],
            title=data["title"],
            authors=list(data.get("authors", [])),
            year=data.get("year"),
            venue=data.get("venue"),
            doi=data.get("doi"),
            arxiv_id=data.get("arxiv_id"),
            url=data.get("url"),
            abstract=data.get("abstract"),
            provider=data.get("provider", "mock"),
            query_id=data.get("query_id", "unknown"),
            query_text=data.get("query_text", "unknown"),
            score=data.get("score"),
            bibtex_key_candidate=data.get("bibtex_key_candidate"),
            intended_channel_hints=list(data.get("intended_channel_hints", [])),
            intended_bottleneck_hints=list(data.get("intended_bottleneck_hints", [])),
            discovery_status=data.get("discovery_status", "discovered_unreviewed"),
            notes=data.get("notes"),
        )


def discovered_to_literature_source(discovered: DiscoveredSource) -> LiteratureSource:
    notes = [
        f"discovery_provider={discovered.provider}",
        f"query_id={discovered.query_id}",
    ]
    if discovered.intended_channel_hints:
        notes.append(f"intended_channel_hints={', '.join(discovered.intended_channel_hints)}")
    if discovered.notes:
        notes.append(discovered.notes)
    return LiteratureSource(
        source_id=discovered.source_id,
        title=discovered.title,
        authors=list(discovered.authors),
        year=discovered.year,
        venue=discovered.venue,
        abstract=discovered.abstract,
        url=discovered.url,
        arxiv_id=discovered.arxiv_id,
        doi=discovered.doi,
        bibtex_key=discovered.bibtex_key_candidate,
        source_type="paper",
        notes="; ".join(notes),
    )


def load_discovered_sources(path: str | Path) -> list[DiscoveredSource]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [DiscoveredSource.from_dict(item) for item in payload]


def save_discovered_sources(sources: list[DiscoveredSource], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([source.to_dict() for source in sources], handle, indent=2)
        handle.write("\n")
