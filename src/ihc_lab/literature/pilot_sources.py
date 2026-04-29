"""Pilot literature source metadata for atlas expansion."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ALLOWED_PILOT_GROUPS = {
    "classical_obstruction",
    "unramified_brauer",
    "enriques_coble_bockstein",
    "computational_lattice",
    "abelian_matroidal",
    "categorical_motivic",
    "positive_boundary",
    "local_singularity_perverse",
    "stacky_finite_group",
    "unknown",
}


CSV_COLUMNS = [
    "source_id",
    "title",
    "authors",
    "year",
    "venue",
    "bibtex_key",
    "doi",
    "arxiv_id",
    "url",
    "source_type",
    "pilot_group",
    "intended_channel_hints",
    "intended_bottleneck_hints",
    "priority",
    "notes",
]


@dataclass
class PilotLiteratureSource:
    source_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    bibtex_key: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    abstract: str | None = None
    source_type: str = "paper"
    pilot_group: str = "unknown"
    intended_channel_hints: list[str] = field(default_factory=list)
    intended_bottleneck_hints: list[str] = field(default_factory=list)
    priority: int = 2
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.source_id.strip():
            raise ValueError("source_id is required")
        if not self.title or not self.title.strip():
            raise ValueError("title is required")
        self.authors = list(self.authors or [])
        self.intended_channel_hints = list(self.intended_channel_hints or [])
        self.intended_bottleneck_hints = list(self.intended_bottleneck_hints or [])
        if self.year in ("", None):
            self.year = None
        else:
            self.year = int(self.year)
        if not self.source_type:
            self.source_type = "paper"
        if not self.pilot_group:
            self.pilot_group = "unknown"
        if self.pilot_group not in ALLOWED_PILOT_GROUPS:
            raise ValueError(f"unknown pilot_group: {self.pilot_group}")
        self.priority = int(self.priority or 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "title": self.title,
            "authors": list(self.authors),
            "year": self.year,
            "venue": self.venue,
            "bibtex_key": self.bibtex_key,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "url": self.url,
            "abstract": self.abstract,
            "source_type": self.source_type,
            "pilot_group": self.pilot_group,
            "intended_channel_hints": list(self.intended_channel_hints),
            "intended_bottleneck_hints": list(self.intended_bottleneck_hints),
            "priority": self.priority,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "PilotLiteratureSource") -> "PilotLiteratureSource":
        if isinstance(data, cls):
            return data
        return cls(
            source_id=data["source_id"],
            title=data["title"],
            authors=list(data.get("authors", [])),
            year=data.get("year"),
            venue=data.get("venue"),
            bibtex_key=data.get("bibtex_key"),
            doi=data.get("doi"),
            arxiv_id=data.get("arxiv_id"),
            url=data.get("url"),
            abstract=data.get("abstract"),
            source_type=data.get("source_type", "paper"),
            pilot_group=data.get("pilot_group", "unknown"),
            intended_channel_hints=list(data.get("intended_channel_hints", [])),
            intended_bottleneck_hints=list(data.get("intended_bottleneck_hints", [])),
            priority=data.get("priority", 2),
            notes=data.get("notes"),
        )


def _split_semicolon(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(";") if item.strip()]


def _split_comma(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def load_pilot_sources_json(path: str | Path) -> list[PilotLiteratureSource]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [PilotLiteratureSource.from_dict(item) for item in payload]


def save_pilot_sources_json(sources: list[PilotLiteratureSource], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([source.to_dict() for source in sources], handle, indent=2)
        handle.write("\n")


def load_pilot_sources_csv(path: str | Path) -> list[PilotLiteratureSource]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            rows.append(
                PilotLiteratureSource(
                    source_id=row["source_id"],
                    title=row["title"],
                    authors=_split_semicolon(row.get("authors")),
                    year=row.get("year") or None,
                    venue=row.get("venue") or None,
                    bibtex_key=row.get("bibtex_key") or None,
                    doi=row.get("doi") or None,
                    arxiv_id=row.get("arxiv_id") or None,
                    url=row.get("url") or None,
                    source_type=row.get("source_type") or "paper",
                    pilot_group=row.get("pilot_group") or "unknown",
                    intended_channel_hints=_split_comma(row.get("intended_channel_hints")),
                    intended_bottleneck_hints=_split_comma(row.get("intended_bottleneck_hints")),
                    priority=int(row.get("priority") or 2),
                    notes=row.get("notes") or None,
                )
            )
    return rows


def save_pilot_sources_csv(sources: list[PilotLiteratureSource], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for source in sources:
            writer.writerow(
                {
                    "source_id": source.source_id,
                    "title": source.title,
                    "authors": "; ".join(source.authors),
                    "year": source.year or "",
                    "venue": source.venue or "",
                    "bibtex_key": source.bibtex_key or "",
                    "doi": source.doi or "",
                    "arxiv_id": source.arxiv_id or "",
                    "url": source.url or "",
                    "source_type": source.source_type,
                    "pilot_group": source.pilot_group,
                    "intended_channel_hints": ", ".join(source.intended_channel_hints),
                    "intended_bottleneck_hints": ", ".join(source.intended_bottleneck_hints),
                    "priority": source.priority,
                    "notes": source.notes or "",
                }
            )
