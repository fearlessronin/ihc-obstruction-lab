from pathlib import Path

import pytest

from ihc_lab.literature.extraction_schema import ExtractedChannelCandidate
from ihc_lab.literature.review_actions import (
    ReviewDecision,
    apply_review_decision,
    apply_review_decisions,
    load_review_decisions,
    save_review_decisions,
)


def _candidate(extraction_id: str = "extract") -> ExtractedChannelCandidate:
    return ExtractedChannelCandidate(
        extraction_id=extraction_id,
        source_id="source",
        proposed_record_id="record",
        proposed_display_name="Record",
        proposed_channel_labels=["brauer_unramified"],
        proposed_source_packages=["unramified_cohomology_class"],
        proposed_active_operations=["residue_test"],
        proposed_bottleneck="unknown",
        proposed_citation_keys=["CitationKey"],
        evidence_snippets=["sample evidence"],
    )


def test_review_decision_requires_reviewer_and_notes() -> None:
    with pytest.raises(ValueError):
        ReviewDecision(
            extraction_id="extract",
            decision="accept",
            reviewer="",
            reviewer_notes="notes",
        )
    with pytest.raises(ValueError):
        ReviewDecision(
            extraction_id="extract",
            decision="accept",
            reviewer="reviewer",
            reviewer_notes="",
        )


def test_accept_reject_needs_revision_statuses_apply() -> None:
    accepted = apply_review_decision(
        _candidate("accepted"),
        ReviewDecision("accepted", "accept", "reviewer", "accepted"),
    )
    rejected = apply_review_decision(
        _candidate("rejected"),
        ReviewDecision("rejected", "reject", "reviewer", "rejected"),
    )
    revision = apply_review_decision(
        _candidate("revision"),
        ReviewDecision("revision", "needs_revision", "reviewer", "revise"),
    )

    assert accepted.review_status == "reviewed_accept"
    assert rejected.review_status == "reviewed_reject"
    assert revision.review_status == "reviewed_needs_revision"


def test_corrected_fields_update_candidate() -> None:
    candidate = _candidate()
    reviewed = apply_review_decision(
        candidate,
        ReviewDecision(
            extraction_id="extract",
            decision="accept",
            reviewer="reviewer",
            reviewer_notes="corrected",
            corrected_channel_labels=["lattice_saturation"],
            corrected_bottleneck="lattice_identification",
            corrected_citation_keys=["CorrectedKey"],
            corrected_evidence_snippets=["corrected evidence"],
            corrected_obstruction_status="computed_benchmark",
            corrected_survival_status="unknown",
            corrected_computability_level="level_2_computed_group",
        ),
    )

    assert reviewed.proposed_channel_labels == ["lattice_saturation"]
    assert reviewed.proposed_bottleneck == "lattice_identification"
    assert reviewed.proposed_citation_keys == ["CorrectedKey"]
    assert reviewed.evidence_snippets == ["corrected evidence"]
    assert reviewed.proposed_obstruction_status == "computed_benchmark"
    assert reviewed.proposed_computability_level == "level_2_computed_group"


def test_unknown_decision_extraction_id_raises() -> None:
    with pytest.raises(ValueError):
        apply_review_decisions(
            [_candidate("known")],
            [ReviewDecision("missing", "accept", "reviewer", "notes")],
        )


def test_review_decisions_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "review.json"
    decisions = [ReviewDecision("extract", "accept", "reviewer", "notes")]
    save_review_decisions(decisions, path)

    assert load_review_decisions(path)[0].to_dict() == decisions[0].to_dict()
