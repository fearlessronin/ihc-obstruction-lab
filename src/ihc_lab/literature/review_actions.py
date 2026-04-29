"""Human review decisions for literature-extracted candidates."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ihc_lab.literature.extraction_schema import (
    ExtractionStatus,
    ExtractedChannelCandidate,
)


ALLOWED_REVIEW_DECISIONS = {"accept", "reject", "needs_revision"}


@dataclass
class ReviewDecision:
    extraction_id: str
    decision: str
    reviewer: str
    reviewer_notes: str
    corrected_channel_labels: list[str] | None = None
    corrected_bottleneck: str | None = None
    corrected_citation_keys: list[str] | None = None
    corrected_evidence_snippets: list[str] | None = None
    corrected_obstruction_status: str | None = None
    corrected_survival_status: str | None = None
    corrected_computability_level: str | None = None
    trust_level_override: str | None = None
    _candidate_citation_keys: list[str] = field(default_factory=list, repr=False)
    _candidate_evidence_snippets: list[str] = field(default_factory=list, repr=False)

    def __post_init__(self) -> None:
        if not self.extraction_id or not self.extraction_id.strip():
            raise ValueError("extraction_id is required")
        if self.decision not in ALLOWED_REVIEW_DECISIONS:
            raise ValueError(f"unknown review decision: {self.decision}")
        if not self.reviewer or not self.reviewer.strip():
            raise ValueError("reviewer is required")
        if not self.reviewer_notes or not self.reviewer_notes.strip():
            raise ValueError("reviewer_notes is required")
        if self.trust_level_override == "theorem_backed_literature":
            if self.decision != "accept":
                raise ValueError("theorem_backed_literature override requires accept decision")
            if self._candidate_citation_keys and not (
                self.corrected_citation_keys or self._candidate_citation_keys
            ):
                raise ValueError("theorem_backed_literature override requires citation keys")
            if self._candidate_evidence_snippets and not (
                self.corrected_evidence_snippets or self._candidate_evidence_snippets
            ):
                raise ValueError("theorem_backed_literature override requires evidence snippets")

    def to_dict(self) -> dict[str, Any]:
        return {
            "extraction_id": self.extraction_id,
            "decision": self.decision,
            "reviewer": self.reviewer,
            "reviewer_notes": self.reviewer_notes,
            "corrected_channel_labels": self.corrected_channel_labels,
            "corrected_bottleneck": self.corrected_bottleneck,
            "corrected_citation_keys": self.corrected_citation_keys,
            "corrected_evidence_snippets": self.corrected_evidence_snippets,
            "corrected_obstruction_status": self.corrected_obstruction_status,
            "corrected_survival_status": self.corrected_survival_status,
            "corrected_computability_level": self.corrected_computability_level,
            "trust_level_override": self.trust_level_override,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any] | "ReviewDecision") -> "ReviewDecision":
        if isinstance(data, cls):
            return data
        return cls(
            extraction_id=data["extraction_id"],
            decision=data["decision"],
            reviewer=data["reviewer"],
            reviewer_notes=data["reviewer_notes"],
            corrected_channel_labels=(
                list(data["corrected_channel_labels"])
                if data.get("corrected_channel_labels") is not None
                else None
            ),
            corrected_bottleneck=data.get("corrected_bottleneck"),
            corrected_citation_keys=(
                list(data["corrected_citation_keys"])
                if data.get("corrected_citation_keys") is not None
                else None
            ),
            corrected_evidence_snippets=(
                list(data["corrected_evidence_snippets"])
                if data.get("corrected_evidence_snippets") is not None
                else None
            ),
            corrected_obstruction_status=data.get("corrected_obstruction_status"),
            corrected_survival_status=data.get("corrected_survival_status"),
            corrected_computability_level=data.get("corrected_computability_level"),
            trust_level_override=data.get("trust_level_override"),
        )


def load_review_decisions(path: str | Path) -> list[ReviewDecision]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [ReviewDecision.from_dict(item) for item in payload]


def save_review_decisions(decisions: list[ReviewDecision], path: str | Path) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([decision.to_dict() for decision in decisions], handle, indent=2)
        handle.write("\n")


def _validate_override_for_candidate(
    candidate: ExtractedChannelCandidate, decision: ReviewDecision
) -> None:
    if decision.trust_level_override != "theorem_backed_literature":
        return
    if decision.decision != "accept":
        raise ValueError("theorem_backed_literature override requires accept decision")
    if not (decision.corrected_citation_keys or candidate.proposed_citation_keys):
        raise ValueError("theorem_backed_literature override requires citation keys")
    if not (decision.corrected_evidence_snippets or candidate.evidence_snippets):
        raise ValueError("theorem_backed_literature override requires evidence snippets")


def apply_review_decision(
    candidate: ExtractedChannelCandidate, decision: ReviewDecision
) -> ExtractedChannelCandidate:
    if candidate.extraction_id != decision.extraction_id:
        raise ValueError(
            f"decision {decision.extraction_id} does not match candidate {candidate.extraction_id}"
        )
    _validate_override_for_candidate(candidate, decision)
    status_by_decision = {
        "accept": ExtractionStatus.reviewed_accept,
        "reject": ExtractionStatus.reviewed_reject,
        "needs_revision": ExtractionStatus.reviewed_needs_revision,
    }
    candidate.review_status = status_by_decision[decision.decision]
    candidate.reviewer_notes = decision.reviewer_notes
    if decision.corrected_channel_labels is not None:
        candidate.proposed_channel_labels = list(decision.corrected_channel_labels)
    if decision.corrected_bottleneck is not None:
        candidate.proposed_bottleneck = decision.corrected_bottleneck
    if decision.corrected_citation_keys is not None:
        candidate.proposed_citation_keys = list(decision.corrected_citation_keys)
    if decision.corrected_evidence_snippets is not None:
        candidate.evidence_snippets = list(decision.corrected_evidence_snippets)
    if decision.corrected_obstruction_status is not None:
        candidate.proposed_obstruction_status = decision.corrected_obstruction_status
    if decision.corrected_survival_status is not None:
        candidate.proposed_survival_status = decision.corrected_survival_status
    if decision.corrected_computability_level is not None:
        candidate.proposed_computability_level = decision.corrected_computability_level
    if decision.trust_level_override:
        note = f"Requested trust_level_override: {decision.trust_level_override}."
        candidate.extraction_notes = (
            f"{candidate.extraction_notes} {note}".strip()
            if candidate.extraction_notes
            else note
        )
    return candidate


def apply_review_decisions(
    candidates: list[ExtractedChannelCandidate], decisions: list[ReviewDecision]
) -> list[ExtractedChannelCandidate]:
    candidates_by_id = {candidate.extraction_id: candidate for candidate in candidates}
    for decision in decisions:
        candidate = candidates_by_id.get(decision.extraction_id)
        if candidate is None:
            raise ValueError(f"review decision refers to unknown extraction_id: {decision.extraction_id}")
        apply_review_decision(candidate, decision)
    return candidates
