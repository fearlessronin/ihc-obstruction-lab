from pathlib import Path

from ihc_lab.cli import main
from ihc_lab.literature.manual_import import import_manual_extraction, load_manual_extraction


def test_manual_sample_import_forces_status(tmp_path: Path) -> None:
    output = tmp_path / "manual.json"
    candidates = import_manual_extraction(
        "data/literature_queue/manual_extraction.sample.json",
        output,
    )

    assert output.exists()
    assert candidates[0].trust_level == "llm_extracted_unverified"
    assert candidates[0].review_status == "needs_human_review"


def test_load_manual_extraction() -> None:
    candidates = load_manual_extraction("data/literature_queue/manual_extraction.sample.json")

    assert candidates[0].extraction_id == "manual_sample_unramified"
    assert candidates[0].trust_level == "llm_extracted_unverified"


def test_cli_import_manual_extraction(tmp_path: Path) -> None:
    output = tmp_path / "manual.json"
    report = tmp_path / "literature_manual_extraction.md"
    result = main(
        [
            "import-manual-extraction",
            "--input",
            "data/literature_queue/manual_extraction.sample.json",
            "--output",
            str(output),
            "--report",
            str(report),
        ]
    )

    assert result == 0
    assert output.exists()
    assert "# LLM Extraction Report" in report.read_text(encoding="utf-8")
