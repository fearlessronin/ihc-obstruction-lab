import pytest

from ihc_lab.literature.extraction_schema import (
    ExtractionStatus,
    ExtractedChannelCandidate,
)


def candidate(**overrides) -> ExtractedChannelCandidate:
    data = {
        "extraction_id": "ext",
        "source_id": "src",
        "proposed_record_id": "record",
        "proposed_display_name": "Record",
        "proposed_channel_labels": ["brauer_unramified"],
    }
    data.update(overrides)
    return ExtractedChannelCandidate(**data)


def test_extracted_candidate_defaults_to_unverified_review() -> None:
    extracted = candidate()

    assert extracted.trust_level == ExtractionStatus.llm_extracted_unverified
    assert extracted.review_status == ExtractionStatus.needs_human_review
    assert "evidence_snippets" in extracted.missing_fields


def test_required_minimum_fields_and_promotion_gate() -> None:
    extracted = candidate(evidence_snippets=["sample evidence"])

    assert extracted.has_required_minimum_fields()
    assert not extracted.can_be_promoted()

    extracted.review_status = ExtractionStatus.reviewed_accept
    extracted.reviewer_notes = "Checked by reviewer."
    assert extracted.can_be_promoted()


def test_cannot_construct_theorem_backed_by_default() -> None:
    with pytest.raises(ValueError):
        candidate(trust_level="theorem_backed_literature")


def test_promoted_status_requires_notes() -> None:
    with pytest.raises(ValueError):
        candidate(review_status=ExtractionStatus.promoted_to_literature)
