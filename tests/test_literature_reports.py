from pathlib import Path

from ihc_lab.cli import generate_literature_report
from ihc_lab.literature.reports import literature_queue_latex, literature_queue_markdown
from ihc_lab.literature.review_queue import load_review_queue


def test_literature_queue_reports_render() -> None:
    queue = load_review_queue(
        "data/literature_queue/raw_sources.sample.json",
        "data/literature_queue/extracted_rows.sample.json",
    )

    markdown = literature_queue_markdown(queue)
    assert "# Literature Queue" in markdown
    assert "needs_human_review" in markdown
    assert r"\begin{table}" in literature_queue_latex(queue)


def test_cli_literature_report_writes_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "reports"
    paths = generate_literature_report(
        "data/literature_queue/raw_sources.sample.json",
        "data/literature_queue/extracted_rows.sample.json",
        output_dir,
    )

    expected = {
        output_dir / "literature_queue.md",
        output_dir / "latex" / "literature_queue.tex",
    }
    assert set(paths) == expected
    for path in expected:
        assert path.exists()
