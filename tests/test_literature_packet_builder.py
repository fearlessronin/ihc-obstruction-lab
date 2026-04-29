from pathlib import Path

import pytest

from ihc_lab.cli import build_literature_packets, main
from ihc_lab.literature.ingestion import LiteratureExcerpt, load_excerpt_txt
from ihc_lab.literature.packet_builder import (
    build_extraction_packet,
    build_packets,
    load_packets_json,
    save_packets_json,
)
from ihc_lab.literature.sources import LiteratureSource, load_literature_sources


def test_build_packet_from_sample_source_and_excerpt() -> None:
    source = load_literature_sources("data/literature_queue/raw_sources.sample.json")[0]
    excerpt = load_excerpt_txt(
        "data/literature_queue/excerpts/sample_colliot_theleme_voisin_excerpt.txt",
        source_id=source.source_id,
    )
    packet = build_extraction_packet(source, excerpt)

    assert packet.prompt
    assert "non-binding hints" in packet.prompt
    assert "brauer_unramified" in packet.channel_hints


def test_build_packets_unknown_source_raises() -> None:
    excerpt = LiteratureExcerpt(
        excerpt_id="excerpt",
        source_id="missing",
        text="unramified text",
    )

    with pytest.raises(ValueError):
        build_packets([], [excerpt])


def test_save_load_packets_roundtrip(tmp_path: Path) -> None:
    source = LiteratureSource(source_id="source", title="Title")
    excerpt = LiteratureExcerpt(
        excerpt_id="excerpt",
        source_id="source",
        text="Bockstein cup product text.",
    )
    packets = build_packets([source], [excerpt])
    path = tmp_path / "packets.json"
    save_packets_json(packets, path)

    assert load_packets_json(path)[0].to_dict() == packets[0].to_dict()


def test_build_literature_packets_cli_helper(tmp_path: Path) -> None:
    output = tmp_path / "packets.json"
    report = tmp_path / "literature_packets.md"
    paths = build_literature_packets(
        "data/literature_queue/raw_sources.sample.json",
        "data/literature_queue/excerpts",
        output,
        report,
    )

    assert set(paths) == {output, report}
    assert output.exists()
    assert "# Literature Extraction Packets" in report.read_text(encoding="utf-8")


def test_build_literature_packets_cli_command(tmp_path: Path) -> None:
    output = tmp_path / "packets.json"
    report = tmp_path / "literature_packets.md"
    result = main(
        [
            "build-literature-packets",
            "--sources",
            "data/literature_queue/raw_sources.sample.json",
            "--excerpts-dir",
            "data/literature_queue/excerpts",
            "--output",
            str(output),
            "--report",
            str(report),
        ]
    )

    assert result == 0
    assert output.exists()
    assert report.exists()
