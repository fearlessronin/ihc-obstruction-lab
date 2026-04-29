from __future__ import annotations

from ihc_lab.literature.discovery_import import (
    DiscoveredSource,
    discovered_to_literature_source,
    load_discovered_sources,
    save_discovered_sources,
)


def test_discovered_source_round_trip() -> None:
    source = DiscoveredSource(
        discovery_id="d",
        source_id="s",
        title="A source",
        intended_channel_hints=["brauer_unramified"],
    )

    assert DiscoveredSource.from_dict(source.to_dict()) == source


def test_discovered_to_literature_source_maps_fields() -> None:
    discovered = DiscoveredSource(
        discovery_id="d",
        source_id="s",
        title="A source",
        authors=["A"],
        year=2026,
        bibtex_key_candidate="Key2026",
        intended_channel_hints=["brauer_unramified"],
    )

    source = discovered_to_literature_source(discovered)

    assert source.source_id == "s"
    assert source.bibtex_key == "Key2026"
    assert "intended_channel_hints=brauer_unramified" in (source.notes or "")


def test_load_save_discovered_sources(tmp_path) -> None:
    output = tmp_path / "discovered.json"
    sources = [DiscoveredSource(discovery_id="d", source_id="s", title="A source")]

    save_discovered_sources(sources, output)

    assert load_discovered_sources(output) == sources


def test_manual_discovered_sample_loads() -> None:
    sources = load_discovered_sources(
        "data/literature_queue/discovery/discovered_sources.manual.sample.json"
    )

    assert len(sources) >= 2
    assert all(source.discovery_status == "discovered_unreviewed" for source in sources)
