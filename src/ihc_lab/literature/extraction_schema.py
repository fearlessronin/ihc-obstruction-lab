"""Schema for unverified literature extraction candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ExtractionStatus:
    llm_extracted_unverified = "llm_extracted_unverified"
    needs_human_review = "needs_human_review"
    reviewed_accept = "reviewed_accept"
    reviewed_reject = "reviewed_reject"
    reviewed_needs_revision = "reviewed_needs_revision"
    promoted_to_literature = "promoted_to_literature"
    speculative_template = "speculative_template"


@dataclass
class ExtractedChannelCandidate:
    extraction_id: str
    source_id: str
    proposed_record_id: str
    proposed_display_name: str
    proposed_channel_labels: list[str] = field(default_factory=list)
    proposed_source_packages: list[str] = field(default_factory=list)
    proposed_active_operations: list[str] = field(default_factory=list)
    proposed_survival_status: str = "unknown"
    proposed_obstruction_status: str = "unknown"
    proposed_computability_level: str = "level_0_metadata"
    proposed_bottleneck: str = "unknown"
    proposed_citation_keys: list[str] = field(default_factory=list)
    evidence_snippets: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    extraction_notes: str | None = None
    trust_level: str = ExtractionStatus.llm_extracted_unverified
    review_status: str = ExtractionStatus.needs_human_review
    reviewer_notes: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "extraction_id",
            "source_id",
            "proposed_record_id",
            "proposed_display_name",
        ):
            value = getattr(self, field_name)
            if not value or not str(value).strip():
                raise ValueError(f"{field_name} is required")
        if self.trust_level == "theorem_backed_literature":
            raise ValueError("LLM extraction rows cannot default to theorem_backed_literature")
        if (
            self.review_status == ExtractionStatus.promoted_to_literature
            and not self.reviewer_notes
        ):
            raise ValueError("promoted_to_literature requires reviewer_notes")

        self.proposed_channel_labels = list(self.proposed_channel_labels)
        self.proposed_source_packages = list(self.proposed_source_packages)
        self.proposed_active_operations = list(self.proposed_active_operations)
        self.proposed_citation_keys = list(self.proposed_citation_keys)
        self.evidence_snippets = list(self.evidence_snippets)
        self.missing_fields = list(self.missing_fields)
        if not self.evidence_snippets and "evidence_snippets" not in self.missing_fields:
            self.missing_fields.append("evidence_snippets")

    def has_required_minimum_fields(self) -> bool:
        return all(
            [
                self.extraction_id,
                self.source_id,
                self.proposed_record_id,
                self.proposed_display_name,
                self.proposed_channel_labels,
            ]
        )

    def can_be_promoted(self) -> bool:
        return (
            self.review_status == ExtractionStatus.reviewed_accept
            and bool(self.reviewer_notes)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "extraction_id": self.extraction_id,
            "source_id": self.source_id,
            "proposed_record_id": self.proposed_record_id,
            "proposed_display_name": self.proposed_display_name,
            "proposed_channel_labels": list(self.proposed_channel_labels),
            "proposed_source_packages": list(self.proposed_source_packages),
            "proposed_active_operations": list(self.proposed_active_operations),
            "proposed_survival_status": self.proposed_survival_status,
            "proposed_obstruction_status": self.proposed_obstruction_status,
            "proposed_computability_level": self.proposed_computability_level,
            "proposed_bottleneck": self.proposed_bottleneck,
            "proposed_citation_keys": list(self.proposed_citation_keys),
            "evidence_snippets": list(self.evidence_snippets),
            "missing_fields": list(self.missing_fields),
            "extraction_notes": self.extraction_notes,
            "trust_level": self.trust_level,
            "review_status": self.review_status,
            "reviewer_notes": self.reviewer_notes,
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, Any] | "ExtractedChannelCandidate"
    ) -> "ExtractedChannelCandidate":
        if isinstance(data, cls):
            return data
        return cls(
            extraction_id=data["extraction_id"],
            source_id=data["source_id"],
            proposed_record_id=data["proposed_record_id"],
            proposed_display_name=data["proposed_display_name"],
            proposed_channel_labels=list(data.get("proposed_channel_labels", [])),
            proposed_source_packages=list(data.get("proposed_source_packages", [])),
            proposed_active_operations=list(data.get("proposed_active_operations", [])),
            proposed_survival_status=data.get("proposed_survival_status", "unknown"),
            proposed_obstruction_status=data.get("proposed_obstruction_status", "unknown"),
            proposed_computability_level=data.get(
                "proposed_computability_level", "level_0_metadata"
            ),
            proposed_bottleneck=data.get("proposed_bottleneck", "unknown"),
            proposed_citation_keys=list(data.get("proposed_citation_keys", [])),
            evidence_snippets=list(data.get("evidence_snippets", [])),
            missing_fields=list(data.get("missing_fields", [])),
            extraction_notes=data.get("extraction_notes"),
            trust_level=data.get("trust_level", ExtractionStatus.llm_extracted_unverified),
            review_status=data.get("review_status", ExtractionStatus.needs_human_review),
            reviewer_notes=data.get("reviewer_notes"),
        )


def load_extracted_candidates(path: str | Path) -> list[ExtractedChannelCandidate]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [ExtractedChannelCandidate.from_dict(item) for item in payload]


def save_extracted_candidates(
    candidates: list[ExtractedChannelCandidate], path: str | Path
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([candidate.to_dict() for candidate in candidates], handle, indent=2)
        handle.write("\n")
