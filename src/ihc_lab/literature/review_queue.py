"""Human review queue helpers for literature extraction candidates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import (
    BottleneckLabel,
    ChannelLabel,
    ComputabilityLevel,
    ObstructionStatus,
    OperationLabel,
    SurvivalStatus,
    TrustLevel,
)
from ihc_lab.literature.extraction_schema import (
    ExtractionStatus,
    ExtractedChannelCandidate,
    load_extracted_candidates,
    save_extracted_candidates,
)
from ihc_lab.literature.sources import (
    LiteratureSource,
    load_literature_sources,
    save_literature_sources,
)


@dataclass
class ReviewQueue:
    sources: list[LiteratureSource]
    extracted: list[ExtractedChannelCandidate]


def load_review_queue(
    raw_sources_path: str | Path, extracted_rows_path: str | Path
) -> ReviewQueue:
    return ReviewQueue(
        sources=load_literature_sources(raw_sources_path),
        extracted=load_extracted_candidates(extracted_rows_path),
    )


def save_review_queue(
    queue: ReviewQueue, raw_sources_path: str | Path, extracted_rows_path: str | Path
) -> None:
    save_literature_sources(queue.sources, raw_sources_path)
    save_extracted_candidates(queue.extracted, extracted_rows_path)


def list_needs_review(queue: ReviewQueue) -> list[ExtractedChannelCandidate]:
    return [
        candidate
        for candidate in queue.extracted
        if candidate.review_status == ExtractionStatus.needs_human_review
    ]


def mark_reviewed_accept(
    candidate: ExtractedChannelCandidate, reviewer_notes: str
) -> ExtractedChannelCandidate:
    candidate.review_status = ExtractionStatus.reviewed_accept
    candidate.reviewer_notes = reviewer_notes
    return candidate


def mark_reviewed_reject(
    candidate: ExtractedChannelCandidate, reviewer_notes: str
) -> ExtractedChannelCandidate:
    candidate.review_status = ExtractionStatus.reviewed_reject
    candidate.reviewer_notes = reviewer_notes
    return candidate


def mark_needs_revision(
    candidate: ExtractedChannelCandidate, reviewer_notes: str
) -> ExtractedChannelCandidate:
    candidate.review_status = ExtractionStatus.reviewed_needs_revision
    candidate.reviewer_notes = reviewer_notes
    return candidate


def _parse_or_default(enum_cls, value: str, default):
    try:
        return enum_cls(value)
    except ValueError:
        return default


def promote_candidate_to_obstruction_channel(
    candidate: ExtractedChannelCandidate, trust_level_override: str | None = None
) -> ObstructionChannel:
    trust_level_value = trust_level_override or candidate.trust_level
    if trust_level_value == TrustLevel.theorem_backed_literature.value:
        if not candidate.reviewer_notes:
            raise ValueError("theorem_backed_literature promotion requires reviewer_notes")
        if not candidate.proposed_citation_keys:
            raise ValueError("theorem_backed_literature promotion requires citation keys")
        if not candidate.evidence_snippets:
            raise ValueError("theorem_backed_literature promotion requires evidence snippets")

    trust_level = _parse_or_default(
        TrustLevel, trust_level_value, TrustLevel.llm_extracted_unverified
    )
    channel_labels = [
        _parse_or_default(ChannelLabel, label, None)
        for label in candidate.proposed_channel_labels
    ]
    channel_labels = [label for label in channel_labels if label is not None]
    active_operations = [
        _parse_or_default(OperationLabel, operation, None)
        for operation in candidate.proposed_active_operations
    ]
    active_operations = [operation for operation in active_operations if operation is not None]

    return ObstructionChannel(
        id=candidate.proposed_record_id,
        display_name=candidate.proposed_display_name,
        source_corpus="literature_review_queue",
        trust_level=trust_level,
        geometry_or_package="unknown",
        channel_labels=channel_labels,
        source_packages=list(candidate.proposed_source_packages),
        active_operations=active_operations,
        survival_status=_parse_or_default(
            SurvivalStatus, candidate.proposed_survival_status, SurvivalStatus.unknown
        ),
        obstruction_status=_parse_or_default(
            ObstructionStatus, candidate.proposed_obstruction_status, ObstructionStatus.unknown
        ),
        computability_level=_parse_or_default(
            ComputabilityLevel,
            candidate.proposed_computability_level,
            ComputabilityLevel.level_0_metadata,
        ),
        bottleneck=_parse_or_default(
            BottleneckLabel, candidate.proposed_bottleneck, BottleneckLabel.unknown
        ),
        citation_keys=list(candidate.proposed_citation_keys),
        comments=(
            "Promoted from literature review queue; extraction remains unverified "
            "unless trust_level_override was explicitly reviewed."
        ),
    )
