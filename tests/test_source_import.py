from pathlib import Path

from ihc_lab.cli import main
from ihc_lab.literature.pilot_sources import PilotLiteratureSource
from ihc_lab.literature.source_import import (
    merge_sources,
    pilot_source_to_literature_source,
)
from ihc_lab.literature.sources import LiteratureSource, load_literature_sources


def test_pilot_source_to_literature_source_maps_fields() -> None:
    pilot = PilotLiteratureSource(
        source_id="source",
        title="Title",
        authors=["Author"],
        year=2026,
        bibtex_key="Key",
        pilot_group="unramified_brauer",
        intended_channel_hints=["brauer_unramified"],
    )
    source = pilot_source_to_literature_source(pilot)

    assert source.source_id == "source"
    assert source.title == "Title"
    assert source.year == 2026
    assert "pilot_group=unramified_brauer" in (source.notes or "")
    assert "brauer_unramified" in (source.notes or "")


def test_merge_sources_deduplicates_by_source_id() -> None:
    existing = [LiteratureSource(source_id="source", title="Existing")]
    new = [LiteratureSource(source_id="source", title="New", year=2026)]
    merged = merge_sources(existing, new)

    assert len(merged) == 1
    assert merged[0].title == "Existing"
    assert merged[0].year == 2026


def test_merge_sources_does_not_overwrite_nonempty_existing_values() -> None:
    existing = [
        LiteratureSource(
            source_id="source",
            title="Existing",
            authors=["Existing Author"],
            year=2020,
        )
    ]
    new = [LiteratureSource(source_id="source", title="New", authors=[], year=None)]
    merged = merge_sources(existing, new)

    assert merged[0].authors == ["Existing Author"]
    assert merged[0].year == 2020


def test_cli_pilot_sources_report_creates_outputs(tmp_path: Path) -> None:
    report = tmp_path / "pilot_sources_summary.md"
    channel_report = tmp_path / "pilot_source_channel_intents.md"
    latex = tmp_path / "pilot_sources_summary.tex"
    result = main(
        [
            "pilot-sources-report",
            "--input",
            "data/literature_queue/pilot_sources/pilot_sources.sample.json",
            "--report",
            str(report),
            "--channel-report",
            str(channel_report),
            "--latex",
            str(latex),
        ]
    )

    assert result == 0
    assert report.exists()
    assert channel_report.exists()
    assert latex.exists()


def test_cli_pilot_sources_report_csv_and_merge_leave_seed_rows_unchanged(tmp_path: Path) -> None:
    before = Path("data/seed_rows.json").read_bytes()
    queue_output = tmp_path / "raw_sources.pilot.json"
    result = main(
        [
            "pilot-sources-report",
            "--csv",
            "data/literature_queue/pilot_sources/pilot_sources.sample.csv",
            "--merge-into-queue",
            "--queue-output",
            str(queue_output),
            "--report",
            str(tmp_path / "summary.md"),
            "--channel-report",
            str(tmp_path / "channels.md"),
            "--latex",
            str(tmp_path / "summary.tex"),
        ]
    )

    assert result == 0
    assert queue_output.exists()
    assert len(load_literature_sources(queue_output)) >= 20
    assert Path("data/seed_rows.json").read_bytes() == before
