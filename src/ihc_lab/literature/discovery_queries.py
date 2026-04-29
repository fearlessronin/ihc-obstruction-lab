"""Discovery query definitions for literature source polling."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ALLOWED_DISCOVERY_PROVIDERS = {"mock", "manual", "openalex", "crossref", "arxiv"}


@dataclass
class DiscoveryQuery:
    query_id: str
    query_text: str
    provider: str = "mock"
    year_from: int | None = None
    year_to: int | None = None
    max_results: int = 25
    pilot_group: str = "unknown"
    intended_channel_hints: list[str] = field(default_factory=list)
    intended_bottleneck_hints: list[str] = field(default_factory=list)
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.query_id or not self.query_id.strip():
            raise ValueError("query_id is required")
        if not self.query_text or not self.query_text.strip():
            raise ValueError("query_text is required")
        if not self.provider:
            self.provider = "mock"
        if self.provider not in ALLOWED_DISCOVERY_PROVIDERS:
            raise ValueError(f"unknown discovery provider: {self.provider}")
        if self.year_from in ("", None):
            self.year_from = None
        else:
            self.year_from = int(self.year_from)
        if self.year_to in ("", None):
            self.year_to = None
        else:
            self.year_to = int(self.year_to)
        if self.max_results in ("", None):
            self.max_results = 25
        else:
            self.max_results = int(self.max_results)
        if self.max_results <= 0:
            raise ValueError("max_results must be positive")
        self.intended_channel_hints = list(self.intended_channel_hints or [])
        self.intended_bottleneck_hints = list(self.intended_bottleneck_hints or [])
        if not self.pilot_group:
            self.pilot_group = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_id": self.query_id,
            "query_text": self.query_text,
            "provider": self.provider,
            "year_from": self.year_from,
            "year_to": self.year_to,
            "max_results": self.max_results,
            "pilot_group": self.pilot_group,
            "intended_channel_hints": list(self.intended_channel_hints),
            "intended_bottleneck_hints": list(self.intended_bottleneck_hints),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "DiscoveryQuery") -> "DiscoveryQuery":
        if isinstance(data, cls):
            return data
        return cls(
            query_id=data["query_id"],
            query_text=data["query_text"],
            provider=data.get("provider", "mock"),
            year_from=data.get("year_from"),
            year_to=data.get("year_to"),
            max_results=data.get("max_results", 25),
            pilot_group=data.get("pilot_group", "unknown"),
            intended_channel_hints=list(data.get("intended_channel_hints", [])),
            intended_bottleneck_hints=list(data.get("intended_bottleneck_hints", [])),
            notes=data.get("notes"),
        )


def load_discovery_queries(path: str | Path) -> list[DiscoveryQuery]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [DiscoveryQuery.from_dict(item) for item in payload]


def save_discovery_queries(queries: list[DiscoveryQuery], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([query.to_dict() for query in queries], handle, indent=2)
        handle.write("\n")
