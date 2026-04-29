"""Conversion helpers for pilot source imports."""

from __future__ import annotations

from dataclasses import replace

from ihc_lab.literature.pilot_sources import PilotLiteratureSource
from ihc_lab.literature.sources import LiteratureSource


def pilot_source_to_literature_source(pilot: PilotLiteratureSource) -> LiteratureSource:
    notes_parts = []
    if pilot.notes:
        notes_parts.append(pilot.notes)
    notes_parts.append(f"pilot_group={pilot.pilot_group}")
    if pilot.intended_channel_hints:
        notes_parts.append(f"intended_channel_hints={', '.join(pilot.intended_channel_hints)}")
    if pilot.intended_bottleneck_hints:
        notes_parts.append(
            f"intended_bottleneck_hints={', '.join(pilot.intended_bottleneck_hints)}"
        )
    return LiteratureSource(
        source_id=pilot.source_id,
        title=pilot.title,
        authors=list(pilot.authors),
        year=pilot.year,
        venue=pilot.venue,
        abstract=pilot.abstract,
        url=pilot.url,
        arxiv_id=pilot.arxiv_id,
        doi=pilot.doi,
        bibtex_key=pilot.bibtex_key,
        source_type=pilot.source_type,
        notes="; ".join(notes_parts),
    )


def convert_pilot_sources_to_literature_sources(
    pilot_sources: list[PilotLiteratureSource],
) -> list[LiteratureSource]:
    return [pilot_source_to_literature_source(source) for source in pilot_sources]


def _merge_source(existing: LiteratureSource, new: LiteratureSource) -> LiteratureSource:
    data = existing.to_dict()
    for key, value in new.to_dict().items():
        if key in {"source_id", "title"}:
            continue
        if data.get(key) in (None, "", []):
            data[key] = value
    return replace(existing, **data)


def merge_sources(
    existing: list[LiteratureSource], new: list[LiteratureSource]
) -> list[LiteratureSource]:
    by_id = {source.source_id: source for source in existing}
    order = [source.source_id for source in existing]
    for source in new:
        if source.source_id in by_id:
            by_id[source.source_id] = _merge_source(by_id[source.source_id], source)
        else:
            by_id[source.source_id] = source
            order.append(source.source_id)
    return [by_id[source_id] for source_id in order]
