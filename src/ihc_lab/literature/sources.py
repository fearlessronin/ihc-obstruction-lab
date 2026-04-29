"""Literature source metadata for local review queues."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class LiteratureSource:
    source_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    url: str | None = None
    arxiv_id: str | None = None
    doi: str | None = None
    bibtex_key: str | None = None
    source_type: str = "unknown"
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.source_id.strip():
            raise ValueError("source_id is required")
        if not self.title or not self.title.strip():
            raise ValueError("title is required")
        self.authors = list(self.authors or [])
        if self.year is not None:
            self.year = int(self.year)
        if not self.source_type:
            self.source_type = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "authors": list(self.authors),
            "year": self.year,
            "venue": self.venue,
            "abstract": self.abstract,
            "url": self.url,
            "arxiv_id": self.arxiv_id,
            "doi": self.doi,
            "bibtex_key": self.bibtex_key,
            "source_type": self.source_type,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "LiteratureSource") -> "LiteratureSource":
        if isinstance(data, cls):
            return data
        return cls(
            source_id=data["source_id"],
            title=data["title"],
            authors=list(data.get("authors", [])),
            year=data.get("year"),
            venue=data.get("venue"),
            abstract=data.get("abstract"),
            url=data.get("url"),
            arxiv_id=data.get("arxiv_id"),
            doi=data.get("doi"),
            bibtex_key=data.get("bibtex_key"),
            source_type=data.get("source_type", "unknown"),
            notes=data.get("notes"),
        )


def load_literature_sources(path: str | Path) -> list[LiteratureSource]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [LiteratureSource.from_dict(item) for item in payload]


def save_literature_sources(sources: list[LiteratureSource], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([source.to_dict() for source in sources], handle, indent=2)
        handle.write("\n")
