from pathlib import Path

from ihc_lab.cli import generate_reports, main
from ihc_lab.datasets import load_canonical_literature_rows
from ihc_lab.enums import TrustLevel
from ihc_lab.reports import (
    canonical_literature_table_latex,
    canonical_literature_table_markdown,
)


def test_load_canonical_literature_rows_succeeds() -> None:
    rows = load_canonical_literature_rows()

    assert len(rows) >= 9


def test_theorem_backed_rows_have_citations() -> None:
    rows = load_canonical_literature_rows()

    assert all(
        row.citation_keys
        for row in rows
        if row.trust_level == TrustLevel.theorem_backed_literature
    )


def test_canonical_rows_are_not_llm_extracted() -> None:
    rows = load_canonical_literature_rows()

    assert all(row.trust_level != TrustLevel.llm_extracted_unverified for row in rows)


def test_canonical_rows_do_not_alter_seed_rows() -> None:
    before = Path("data/seed_rows.json").read_bytes()

    load_canonical_literature_rows()

    assert Path("data/seed_rows.json").read_bytes() == before


def test_canonical_literature_markdown_report() -> None:
    report = canonical_literature_table_markdown(load_canonical_literature_rows())

    assert "Canonical Literature Mechanism Rows" in report
    assert "atiyah_hirzebruch_torsion_operation_anchor" in report
    assert "aljovin_movasati_villaflor_fermat_lattice_anchor" in report


def test_canonical_literature_latex_report() -> None:
    report = canonical_literature_table_latex(load_canonical_literature_rows())

    assert r"\begin{table}" in report
    assert "Canonical literature mechanism anchors" in report


def test_canonical_literature_report_cli_command(tmp_path: Path) -> None:
    result = main(
        [
            "canonical-literature-report",
            "--data-path",
            "data/canonical_literature_rows.json",
            "--output-dir",
            str(tmp_path),
        ]
    )

    assert result == 0
    assert (tmp_path / "canonical_literature_table.md").exists()
    assert (tmp_path / "latex" / "canonical_literature_table.tex").exists()


def test_generate_reports_writes_canonical_literature_reports(tmp_path: Path) -> None:
    outputs = generate_reports("data/seed_rows.json", tmp_path)

    assert tmp_path / "canonical_literature_table.md" in outputs
    assert tmp_path / "latex" / "canonical_literature_table.tex" in outputs
    assert (tmp_path / "canonical_literature_table.md").exists()
