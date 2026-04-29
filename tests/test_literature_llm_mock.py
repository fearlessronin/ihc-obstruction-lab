from pathlib import Path

from ihc_lab.cli import main
from ihc_lab.literature.extract_with_llm import extract_candidate_from_packet
from ihc_lab.literature.llm_client import MockLLMClient
from ihc_lab.literature.packet_builder import load_packets_json
from ihc_lab.literature.parsing import parse_extracted_candidate_json


def test_mock_llm_fermat_output_parses() -> None:
    client = MockLLMClient()
    text = client.generate("Fermat varieties and elementary divisors")
    candidate = parse_extracted_candidate_json(text)

    assert "lattice_saturation" in candidate.proposed_channel_labels
    assert candidate.trust_level == "llm_extracted_unverified"
    assert candidate.review_status == "needs_human_review"


def test_extract_candidate_from_sample_packet() -> None:
    packet = load_packets_json("data/literature_queue/packets.sample.json")[0]
    candidate = extract_candidate_from_packet(packet, MockLLMClient())

    assert candidate.source_id
    assert candidate.trust_level == "llm_extracted_unverified"
    assert candidate.review_status == "needs_human_review"


def test_cli_run_llm_extraction_mock(tmp_path: Path) -> None:
    output = tmp_path / "extracted_rows.mock.json"
    report = tmp_path / "literature_llm_extraction.md"
    result = main(
        [
            "run-llm-extraction",
            "--provider",
            "mock",
            "--packets",
            "data/literature_queue/packets.sample.json",
            "--output",
            str(output),
            "--report",
            str(report),
        ]
    )

    assert result == 0
    assert output.exists()
    assert "# LLM Extraction Report" in report.read_text(encoding="utf-8")
