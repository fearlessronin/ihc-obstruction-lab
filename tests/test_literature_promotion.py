import json
from pathlib import Path

import pytest

from ihc_lab.channels import ObstructionChannel
from ihc_lab.cli import apply_literature_review, export_reviewed_literature, main
from ihc_lab.literature.extraction_schema import ExtractedChannelCandidate
from ihc_lab.literature.promotion import (
    export_promoted_candidates,
    promote_reviewed_candidate,
    promote_reviewed_candidates,
    safe_bottleneck,
)


def _candidate(
    review_status: str = "reviewed_accept",
    reviewer_notes: str | None = "reviewed",
    citation_keys: list[str] | None = None,
    evidence: list[str] | None = None,
) -> ExtractedChannelCandidate:
    candidate = ExtractedChannelCandidate(
        extraction_id="extract",
        source_id="source",
        proposed_record_id="record",
        proposed_display_name="Record",
        proposed_channel_labels=["brauer_unramified"],
        proposed_source_packages=["unramified_cohomology_class"],
        proposed_active_operations=["residue_test", "unramified_survival"],
        proposed_survival_status="unknown",
        proposed_obstruction_status="unknown",
        proposed_computability_level="level_3_theorem_import",
        proposed_bottleneck="verify_theorem_statement",
        proposed_citation_keys=["CitationKey"] if citation_keys is None else citation_keys,
        evidence_snippets=["sample evidence"] if evidence is None else evidence,
    )
    candidate.review_status = review_status
    candidate.reviewer_notes = reviewer_notes
    return candidate


def test_promotion_fails_if_not_reviewed_accept() -> None:
    with pytest.raises(ValueError):
        promote_reviewed_candidate(_candidate(review_status="needs_human_review"))


def test_promotion_fails_without_reviewer_notes() -> None:
    with pytest.raises(ValueError):
        promote_reviewed_candidate(_candidate(reviewer_notes=None))


def test_default_promotion_does_not_set_theorem_backed() -> None:
    promoted = promote_reviewed_candidate(_candidate())

    assert promoted.trust_level.value == "llm_extracted_unverified"


def test_promotion_preserves_verify_theorem_statement_bottleneck() -> None:
    promoted = promote_reviewed_candidate(_candidate())

    assert promoted.bottleneck.value == "verify_theorem_statement"
    assert "Unmapped bottleneck" not in (promoted.comments or "")


def test_existing_bottleneck_mapping_still_works() -> None:
    assert safe_bottleneck("lattice_identification").value == "lattice_identification"
    assert safe_bottleneck("not_a_bottleneck").value == "unknown"


def test_theorem_backed_override_fails_without_citation_keys() -> None:
    candidate = _candidate(citation_keys=[], evidence=["sample evidence"])

    with pytest.raises(ValueError):
        promote_reviewed_candidate(candidate, "theorem_backed_literature")


def test_theorem_backed_override_fails_without_evidence() -> None:
    candidate = _candidate(citation_keys=["CitationKey"], evidence=[])
    candidate.evidence_snippets = []

    with pytest.raises(ValueError):
        promote_reviewed_candidate(candidate, "theorem_backed_literature")


def test_theorem_backed_override_succeeds_with_review_citation_and_evidence() -> None:
    promoted = promote_reviewed_candidate(_candidate(), "theorem_backed_literature")

    assert isinstance(promoted, ObstructionChannel)
    assert promoted.trust_level.value == "theorem_backed_literature"


def test_promote_reviewed_candidates_skips_rejected() -> None:
    records = promote_reviewed_candidates(
        [_candidate(), _candidate(review_status="reviewed_reject")]
    )

    assert len(records) == 1


def test_export_promoted_candidates_writes_json(tmp_path: Path) -> None:
    output = tmp_path / "canonical.json"
    export_promoted_candidates([promote_reviewed_candidate(_candidate())], output)

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload[0]["id"] == "record"


def test_review_and_export_cli_helpers_leave_seed_rows_unchanged(tmp_path: Path) -> None:
    before = Path("data/seed_rows.json").read_bytes()
    reviewed = tmp_path / "reviewed.json"
    review_report = tmp_path / "literature_review_status.md"
    promoted = tmp_path / "canonical_literature.candidates.json"
    promoted_report = tmp_path / "promoted_literature_candidates.md"

    review_paths = apply_literature_review(
        "data/literature_queue/extracted_rows.manual.json",
        "data/literature_queue/review_manifest.sample.json",
        reviewed,
        review_report,
    )
    export_paths = export_reviewed_literature(reviewed, promoted, promoted_report)

    assert set(review_paths) == {reviewed, review_report}
    assert set(export_paths) == {promoted, promoted_report}
    assert "# Literature Review Status" in review_report.read_text(encoding="utf-8")
    assert "# Promoted Literature Candidates" in promoted_report.read_text(encoding="utf-8")
    assert Path("data/seed_rows.json").read_bytes() == before


def test_review_and_export_cli_commands(tmp_path: Path) -> None:
    reviewed = tmp_path / "reviewed.json"
    review_report = tmp_path / "literature_review_status.md"
    promoted = tmp_path / "canonical_literature.candidates.json"
    promoted_report = tmp_path / "promoted_literature_candidates.md"

    assert (
        main(
            [
                "apply-literature-review",
                "--extracted",
                "data/literature_queue/extracted_rows.manual.json",
                "--review",
                "data/literature_queue/review_manifest.sample.json",
                "--output",
                str(reviewed),
                "--report",
                str(review_report),
            ]
        )
        == 0
    )
    assert (
        main(
            [
                "export-reviewed-literature",
                "--reviewed",
                str(reviewed),
                "--output",
                str(promoted),
                "--report",
                str(promoted_report),
            ]
        )
        == 0
    )
    assert reviewed.exists()
    assert promoted.exists()
