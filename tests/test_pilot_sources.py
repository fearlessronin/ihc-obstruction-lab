from pathlib import Path

from ihc_lab.literature.pilot_sources import (
    PilotLiteratureSource,
    load_pilot_sources_csv,
    load_pilot_sources_json,
    save_pilot_sources_csv,
    save_pilot_sources_json,
)
from ihc_lab.literature.reports import (
    pilot_source_channel_intents_markdown,
    pilot_sources_summary_latex,
    pilot_sources_summary_markdown,
)


PILOT_JSON = "data/literature_queue/pilot_sources/pilot_sources.sample.json"
PILOT_CSV = "data/literature_queue/pilot_sources/pilot_sources.sample.csv"


def test_load_pilot_sources_json_succeeds() -> None:
    sources = load_pilot_sources_json(PILOT_JSON)

    assert len(sources) >= 28


def test_source_ids_are_unique() -> None:
    sources = load_pilot_sources_json(PILOT_JSON)
    source_ids = [source.source_id for source in sources]

    assert len(source_ids) == len(set(source_ids))


def test_expected_channel_hints_present() -> None:
    sources = load_pilot_sources_json(PILOT_JSON)
    hints = {hint for source in sources for hint in source.intended_channel_hints}

    assert "brauer_unramified" in hints
    assert "lattice_saturation" in hints
    assert "stacky_stabilizer" in hints


def test_stacky_finite_group_coverage_present() -> None:
    sources = load_pilot_sources_json(PILOT_JSON)

    assert any(source.pilot_group == "stacky_finite_group" for source in sources)
    assert any(
        "stacky_realization" in source.intended_bottleneck_hints
        for source in sources
    )


def test_pilot_source_round_trip_json_and_csv(tmp_path: Path) -> None:
    source = PilotLiteratureSource(
        source_id="source",
        title="Title",
        authors=["A", "B"],
        intended_channel_hints=["brauer_unramified"],
        intended_bottleneck_hints=["verify_theorem_statement"],
    )
    json_path = tmp_path / "sources.json"
    csv_path = tmp_path / "sources.csv"
    save_pilot_sources_json([source], json_path)
    save_pilot_sources_csv([source], csv_path)

    assert load_pilot_sources_json(json_path)[0].to_dict() == source.to_dict()
    assert load_pilot_sources_csv(csv_path)[0].to_dict() == source.to_dict()


def test_csv_load_works() -> None:
    sources = load_pilot_sources_csv(PILOT_CSV)

    assert len(sources) >= 28


def test_pilot_source_reports() -> None:
    sources = load_pilot_sources_json(PILOT_JSON)

    assert "not a complete bibliography" in pilot_sources_summary_markdown(sources)
    assert "triage hints" in pilot_source_channel_intents_markdown(sources)
    assert r"\begin{table}" in pilot_sources_summary_latex(sources)
