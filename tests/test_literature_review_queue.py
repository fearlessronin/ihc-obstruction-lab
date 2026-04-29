import pytest

from ihc_lab.enums import TrustLevel
from ihc_lab.literature.extraction_schema import ExtractionStatus, ExtractedChannelCandidate
from ihc_lab.literature.review_queue import (
    list_needs_review,
    load_review_queue,
    mark_needs_revision,
    mark_reviewed_accept,
    mark_reviewed_reject,
    promote_candidate_to_obstruction_channel,
)


def test_load_queue_and_list_needs_review() -> None:
    queue = load_review_queue(
        "data/literature_queue/raw_sources.sample.json",
        "data/literature_queue/extracted_rows.sample.json",
    )

    assert len(queue.sources) == 2
    assert len(list_needs_review(queue)) == 2


def test_mark_review_status_helpers() -> None:
    queue = load_review_queue(
        "data/literature_queue/raw_sources.sample.json",
        "data/literature_queue/extracted_rows.sample.json",
    )
    first, second = queue.extracted

    mark_reviewed_accept(first, "Accept after review.")
    assert first.review_status == ExtractionStatus.reviewed_accept
    assert first.reviewer_notes == "Accept after review."

    mark_reviewed_reject(second, "Reject after review.")
    assert second.review_status == ExtractionStatus.reviewed_reject

    mark_needs_revision(second, "Needs more precise theorem statement.")
    assert second.review_status == ExtractionStatus.reviewed_needs_revision


def test_promotion_does_not_set_theorem_backed_by_default() -> None:
    queue = load_review_queue(
        "data/literature_queue/raw_sources.sample.json",
        "data/literature_queue/extracted_rows.sample.json",
    )
    promoted = promote_candidate_to_obstruction_channel(queue.extracted[0])

    assert promoted.trust_level == TrustLevel.llm_extracted_unverified


def test_theorem_backed_override_requires_review_evidence_and_citation() -> None:
    extracted = ExtractedChannelCandidate(
        extraction_id="ext",
        source_id="src",
        proposed_record_id="record",
        proposed_display_name="Record",
        proposed_channel_labels=["brauer_unramified"],
        proposed_citation_keys=[],
        evidence_snippets=[],
    )

    with pytest.raises(ValueError):
        promote_candidate_to_obstruction_channel(
            extracted,
            trust_level_override="theorem_backed_literature",
        )
