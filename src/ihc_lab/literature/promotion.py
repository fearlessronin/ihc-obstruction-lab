"""Controlled promotion from reviewed literature candidates to channel records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

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
)

EnumValue = TypeVar("EnumValue")


def _safe_enum(enum_cls: type[EnumValue], value: str, default: EnumValue) -> tuple[EnumValue, str | None]:
    try:
        return enum_cls(value), None
    except ValueError:
        return default, value


def _safe_enum_list(enum_cls: type[EnumValue], labels: list[str]) -> tuple[list[EnumValue], list[str]]:
    mapped: list[EnumValue] = []
    unmapped: list[str] = []
    for label in labels:
        try:
            mapped.append(enum_cls(label))
        except ValueError:
            unmapped.append(label)
    return mapped, unmapped


def safe_channel_labels(labels: list[str]) -> list[ChannelLabel]:
    mapped, _ = _safe_enum_list(ChannelLabel, labels)
    return mapped


def safe_operation_labels(labels: list[str]) -> list[OperationLabel]:
    mapped, _ = _safe_enum_list(OperationLabel, labels)
    return mapped


def safe_survival_status(value: str) -> SurvivalStatus:
    mapped, _ = _safe_enum(SurvivalStatus, value, SurvivalStatus.unknown)
    return mapped


def safe_obstruction_status(value: str) -> ObstructionStatus:
    mapped, _ = _safe_enum(ObstructionStatus, value, ObstructionStatus.unknown)
    return mapped


def safe_computability_level(value: str) -> ComputabilityLevel:
    mapped, _ = _safe_enum(
        ComputabilityLevel, value, ComputabilityLevel.level_0_metadata
    )
    return mapped


def safe_bottleneck(value: str) -> BottleneckLabel:
    mapped, _ = _safe_enum(BottleneckLabel, value, BottleneckLabel.unknown)
    return mapped


def _default_trust_level(candidate: ExtractedChannelCandidate) -> TrustLevel:
    text = " ".join(
        [
            candidate.proposed_obstruction_status,
            candidate.extraction_notes or "",
        ]
    ).lower()
    if "speculative" in text:
        return TrustLevel.speculative_template
    return TrustLevel.llm_extracted_unverified


def promote_reviewed_candidate(
    candidate: ExtractedChannelCandidate,
    trust_level_override: str | None = None,
) -> ObstructionChannel:
    if candidate.review_status != ExtractionStatus.reviewed_accept:
        raise ValueError("candidate must be reviewed_accept before promotion")
    if not candidate.reviewer_notes:
        raise ValueError("promotion requires reviewer_notes")

    if trust_level_override == TrustLevel.theorem_backed_literature.value:
        if not candidate.proposed_citation_keys:
            raise ValueError("theorem_backed_literature promotion requires citation keys")
        if not candidate.evidence_snippets:
            raise ValueError("theorem_backed_literature promotion requires evidence snippets")
        trust_level = TrustLevel.theorem_backed_literature
    elif trust_level_override is None:
        trust_level = _default_trust_level(candidate)
    else:
        trust_level = TrustLevel(trust_level_override)
        if trust_level == TrustLevel.theorem_backed_literature:
            raise ValueError("theorem_backed_literature override requires explicit validation")

    channel_labels, unmapped_channels = _safe_enum_list(
        ChannelLabel, candidate.proposed_channel_labels
    )
    active_operations, unmapped_operations = _safe_enum_list(
        OperationLabel, candidate.proposed_active_operations
    )
    _, unmapped_bottleneck = _safe_enum(
        BottleneckLabel, candidate.proposed_bottleneck, BottleneckLabel.unknown
    )
    comments = [
        "Promoted from literature review queue.",
        f"Original extraction_id: {candidate.extraction_id}.",
        f"Reviewer notes: {candidate.reviewer_notes}",
    ]
    if unmapped_channels:
        comments.append(f"Unmapped channel labels: {', '.join(unmapped_channels)}.")
    if unmapped_operations:
        comments.append(f"Unmapped operation labels: {', '.join(unmapped_operations)}.")
    if unmapped_bottleneck:
        comments.append(f"Unmapped bottleneck label: {unmapped_bottleneck}.")

    return ObstructionChannel(
        id=candidate.proposed_record_id,
        display_name=candidate.proposed_display_name,
        source_corpus="literature_review_queue",
        trust_level=trust_level,
        geometry_or_package=candidate.source_id or "unknown",
        channel_labels=channel_labels,
        source_packages=list(candidate.proposed_source_packages),
        active_operations=active_operations,
        survival_status=safe_survival_status(candidate.proposed_survival_status),
        obstruction_status=safe_obstruction_status(candidate.proposed_obstruction_status),
        computability_level=safe_computability_level(
            candidate.proposed_computability_level
        ),
        bottleneck=safe_bottleneck(candidate.proposed_bottleneck),
        citation_keys=list(candidate.proposed_citation_keys),
        comments=" ".join(comments),
    )


def promote_reviewed_candidates(
    candidates: list[ExtractedChannelCandidate],
    trust_level_overrides: dict[str, str] | None = None,
) -> list[ObstructionChannel]:
    overrides = trust_level_overrides or {}
    records: list[ObstructionChannel] = []
    for candidate in candidates:
        if candidate.review_status != ExtractionStatus.reviewed_accept:
            continue
        records.append(
            promote_reviewed_candidate(
                candidate,
                trust_level_override=overrides.get(candidate.extraction_id),
            )
        )
    return records


def export_promoted_candidates(
    records: list[ObstructionChannel],
    output_path: str | Path = "data/literature_queue/canonical_literature.candidates.json",
) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump([record.to_dict() for record in records], handle, indent=2)
        handle.write("\n")
