"""Build local extraction packets from source metadata and excerpts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ihc_lab.literature.ingestion import LiteratureExcerpt
from ihc_lab.literature.keyword_hints import infer_channel_hints
from ihc_lab.literature.prompts import LITERATURE_EXTRACTION_USER_TEMPLATE
from ihc_lab.literature.sources import LiteratureSource


@dataclass
class ExtractionPacket:
    packet_id: str
    source_id: str
    excerpt_id: str
    title: str
    authors: list[str] = field(default_factory=list)
    bibtex_key: str | None = None
    excerpt_text: str = ""
    channel_hints: list[str] = field(default_factory=list)
    operation_hints: list[str] = field(default_factory=list)
    bottleneck_hints: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    prompt: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_id": self.packet_id,
            "source_id": self.source_id,
            "excerpt_id": self.excerpt_id,
            "title": self.title,
            "authors": list(self.authors),
            "bibtex_key": self.bibtex_key,
            "excerpt_text": self.excerpt_text,
            "channel_hints": list(self.channel_hints),
            "operation_hints": list(self.operation_hints),
            "bottleneck_hints": list(self.bottleneck_hints),
            "matched_keywords": list(self.matched_keywords),
            "prompt": self.prompt,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "ExtractionPacket") -> "ExtractionPacket":
        if isinstance(data, cls):
            return data
        return cls(
            packet_id=data["packet_id"],
            source_id=data["source_id"],
            excerpt_id=data["excerpt_id"],
            title=data["title"],
            authors=list(data.get("authors", [])),
            bibtex_key=data.get("bibtex_key"),
            excerpt_text=data.get("excerpt_text", ""),
            channel_hints=list(data.get("channel_hints", [])),
            operation_hints=list(data.get("operation_hints", [])),
            bottleneck_hints=list(data.get("bottleneck_hints", [])),
            matched_keywords=list(data.get("matched_keywords", [])),
            prompt=data.get("prompt", ""),
        )


def build_extraction_packet(
    source: LiteratureSource, excerpt: LiteratureExcerpt
) -> ExtractionPacket:
    hints = infer_channel_hints(excerpt.text)
    prompt = LITERATURE_EXTRACTION_USER_TEMPLATE.format(
        title=source.title,
        authors=", ".join(source.authors),
        abstract=source.abstract or "unknown",
        excerpt=excerpt.text,
        citation_key=source.bibtex_key or "unknown",
    )
    prompt = (
        f"{prompt}\n\n"
        "The channel hints are non-binding hints. Do not treat them as verified labels.\n"
        f"Channel hints: {', '.join(hints['proposed_channel_hints']) or 'none'}\n"
        f"Operation hints: {', '.join(hints['operation_hints']) or 'none'}\n"
        f"Bottleneck hints: {', '.join(hints['bottleneck_hints']) or 'none'}"
    )
    return ExtractionPacket(
        packet_id=f"{source.source_id}__{excerpt.excerpt_id}",
        source_id=source.source_id,
        excerpt_id=excerpt.excerpt_id,
        title=source.title,
        authors=list(source.authors),
        bibtex_key=source.bibtex_key,
        excerpt_text=excerpt.text,
        channel_hints=hints["proposed_channel_hints"],
        operation_hints=hints["operation_hints"],
        bottleneck_hints=hints["bottleneck_hints"],
        matched_keywords=hints["matched_keywords"],
        prompt=prompt,
    )


def build_packets(
    sources: list[LiteratureSource], excerpts: list[LiteratureExcerpt]
) -> list[ExtractionPacket]:
    source_by_id = {source.source_id: source for source in sources}
    packets: list[ExtractionPacket] = []
    for excerpt in excerpts:
        source = source_by_id.get(excerpt.source_id)
        if source is None:
            raise ValueError(f"no source found for excerpt source_id: {excerpt.source_id}")
        packets.append(build_extraction_packet(source, excerpt))
    return packets


def save_packets_json(packets: list[ExtractionPacket], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([packet.to_dict() for packet in packets], handle, indent=2)
        handle.write("\n")


def load_packets_json(path: str | Path) -> list[ExtractionPacket]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [ExtractionPacket.from_dict(item) for item in payload]
