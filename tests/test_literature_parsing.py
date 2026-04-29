import json

import pytest

from ihc_lab.literature.parsing import parse_extracted_candidate_json


def _payload() -> dict[str, object]:
    return {
        "extraction_id": "extract",
        "source_id": "source",
        "proposed_record_id": "record",
        "proposed_display_name": "Record",
        "proposed_channel_labels": ["brauer_unramified"],
        "proposed_source_packages": ["unramified_cohomology_class"],
        "proposed_active_operations": ["residue_test"],
        "proposed_survival_status": "unknown",
        "proposed_obstruction_status": "unknown",
        "proposed_computability_level": "level_0_metadata",
        "proposed_bottleneck": "verify_theorem_statement",
        "proposed_citation_keys": ["CitationKey"],
        "evidence_snippets": ["sample evidence"],
        "missing_fields": [],
    }


def test_parse_json_object() -> None:
    candidate = parse_extracted_candidate_json(json.dumps(_payload()))

    assert candidate.extraction_id == "extract"
    assert candidate.review_status == "needs_human_review"


def test_parse_fenced_json_block() -> None:
    text = "```json\n" + json.dumps(_payload()) + "\n```"
    candidate = parse_extracted_candidate_json(text)

    assert candidate.proposed_record_id == "record"


def test_parser_overrides_theorem_backed_and_reviewed_accept() -> None:
    payload = _payload()
    payload["trust_level"] = "theorem_backed_literature"
    payload["review_status"] = "reviewed_accept"
    candidate = parse_extracted_candidate_json(json.dumps(payload))

    assert candidate.trust_level == "llm_extracted_unverified"
    assert candidate.review_status == "needs_human_review"
    assert "reset" in (candidate.extraction_notes or "")


def test_parser_adds_missing_evidence_field() -> None:
    payload = _payload()
    payload["evidence_snippets"] = []
    candidate = parse_extracted_candidate_json(json.dumps(payload))

    assert "evidence_snippets" in candidate.missing_fields


def test_invalid_json_raises() -> None:
    with pytest.raises(ValueError):
        parse_extracted_candidate_json("not json")
