from __future__ import annotations

from ihc_lab.cli import discover_literature, import_discovered_sources
from ihc_lab.literature.discovery_import import DiscoveredSource
from ihc_lab.literature.reports import (
    discovered_source_channel_hints_markdown,
    literature_discovery_report_latex,
    literature_discovery_report_markdown,
)


def test_discovery_reports_contain_warnings() -> None:
    sources = [
        DiscoveredSource(
            discovery_id="d",
            source_id="s",
            title="A source",
            intended_channel_hints=["brauer_unramified"],
        )
    ]

    markdown = literature_discovery_report_markdown(sources)
    hints = discovered_source_channel_hints_markdown(sources)
    latex = literature_discovery_report_latex(sources)

    assert "metadata-only, unreviewed" in markdown
    assert "triage hints" in hints
    assert r"\begin{table}" in latex


def test_cli_discover_literature_mock_creates_outputs(tmp_path) -> None:
    seed_before = open("data/seed_rows.json", encoding="utf-8").read()
    output = tmp_path / "discovered.json"
    report = tmp_path / "literature_discovery_report.md"
    channel_report = tmp_path / "discovered_source_channel_hints.md"
    latex = tmp_path / "literature_discovery_report.tex"

    paths = discover_literature(
        "data/literature_queue/discovery/discovery_queries.sample.json",
        "mock",
        False,
        output,
        report,
        channel_report,
        latex,
        True,
        False,
        tmp_path / "raw_sources.discovered.json",
    )

    assert output in paths
    assert report.exists()
    assert channel_report.exists()
    assert latex.exists()
    assert "# Literature Discovery Report" in report.read_text(encoding="utf-8")
    assert open("data/seed_rows.json", encoding="utf-8").read() == seed_before


def test_cli_import_discovered_sources_creates_outputs(tmp_path) -> None:
    output = tmp_path / "manual.json"
    report = tmp_path / "manual_report.md"
    channel_report = tmp_path / "manual_hints.md"
    latex = tmp_path / "manual_report.tex"

    import_discovered_sources(
        "data/literature_queue/discovery/discovered_sources.manual.sample.json",
        output,
        report,
        channel_report,
        latex,
        False,
        tmp_path / "raw_sources.discovered.json",
    )

    assert output.exists()
    assert report.exists()
    assert "not theorem-backed" in report.read_text(encoding="utf-8")
