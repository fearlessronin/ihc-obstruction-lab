from pathlib import Path

from ihc_lab.cli import generate_reports
from ihc_lab.datasets import load_seed_rows
from ihc_lab.reports import (
    bottleneck_summary_latex,
    bottleneck_table_markdown,
    channel_table_latex,
    channel_table_markdown,
    classifier_report_latex,
    classifier_report_markdown,
    cup_product_validation_latex,
    cup_product_validation_markdown,
    dataset_summary_markdown,
    seed_dataset_summary_latex,
)


def test_markdown_reports_include_expected_seed_content() -> None:
    records = load_seed_rows()

    assert "Total records: 12" in dataset_summary_markdown(records)
    assert "diaz_level_two" in channel_table_markdown(records)
    assert "unramified_nonvanishing" in bottleneck_table_markdown(records)

    cup_report = cup_product_validation_markdown(records)
    assert "H^4(-, Z(2))" in cup_report
    assert "H^6(-, Z(3))" in cup_report

    classifier_report = classifier_report_markdown(records)
    assert "formal_candidate_survival_needed" in classifier_report


def test_latex_reports_have_table_caption_and_label() -> None:
    records = load_seed_rows()
    latex_reports = [
        seed_dataset_summary_latex(records),
        channel_table_latex(records),
        bottleneck_summary_latex(records),
        cup_product_validation_latex(records),
        classifier_report_latex(records),
    ]

    for report in latex_reports:
        assert r"\begin{table}" in report
        assert r"\caption" in report
        assert r"\label" in report


def test_cli_generation_writes_expected_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"
    paths = generate_reports("data/seed_rows.json", output_dir)

    expected = {
        output_dir / "seed_dataset_summary.md",
        output_dir / "channel_table.md",
        output_dir / "bottleneck_summary.md",
        output_dir / "cup_product_validation.md",
        output_dir / "classifier_report.md",
        output_dir / "latex" / "seed_dataset_summary.tex",
        output_dir / "latex" / "channel_table.tex",
        output_dir / "latex" / "bottleneck_summary.tex",
        output_dir / "latex" / "cup_product_validation.tex",
        output_dir / "latex" / "classifier_report.tex",
    }

    assert set(paths) == expected
    for path in expected:
        assert path.exists()
