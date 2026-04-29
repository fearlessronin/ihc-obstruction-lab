"""Local text ingestion for literature extraction packets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LiteratureExcerpt:
    excerpt_id: str
    source_id: str
    text: str
    section_label: str | None = None
    page_range: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.excerpt_id or not self.excerpt_id.strip():
            raise ValueError("excerpt_id is required")
        if not self.source_id or not self.source_id.strip():
            raise ValueError("source_id is required")
        if not self.text or not self.text.strip():
            raise ValueError("text is required")
        self.text = self.text.strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "excerpt_id": self.excerpt_id,
            "source_id": self.source_id,
            "text": self.text,
            "section_label": self.section_label,
            "page_range": self.page_range,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "LiteratureExcerpt") -> "LiteratureExcerpt":
        if isinstance(data, cls):
            return data
        return cls(
            excerpt_id=data["excerpt_id"],
            source_id=data["source_id"],
            text=data["text"],
            section_label=data.get("section_label"),
            page_range=data.get("page_range"),
            notes=data.get("notes"),
        )


def load_excerpt_txt(
    path: str | Path,
    source_id: str,
    excerpt_id: str | None = None,
    section_label: str | None = None,
    page_range: str | None = None,
    notes: str | None = None,
) -> LiteratureExcerpt:
    excerpt_path = Path(path)
    text = excerpt_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"excerpt file is empty: {excerpt_path}")
    return LiteratureExcerpt(
        excerpt_id=excerpt_id or f"{source_id}__{excerpt_path.stem}",
        source_id=source_id,
        text=text,
        section_label=section_label,
        page_range=page_range,
        notes=notes,
    )


def save_excerpts_json(excerpts: list[LiteratureExcerpt], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([excerpt.to_dict() for excerpt in excerpts], handle, indent=2)
        handle.write("\n")


def load_excerpts_json(path: str | Path) -> list[LiteratureExcerpt]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [LiteratureExcerpt.from_dict(item) for item in payload]
