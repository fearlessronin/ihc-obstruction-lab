from pathlib import Path

import pytest

from ihc_lab.literature.sources import (
    LiteratureSource,
    load_literature_sources,
    save_literature_sources,
)


def test_literature_source_required_fields() -> None:
    with pytest.raises(ValueError):
        LiteratureSource(source_id="", title="A title")
    with pytest.raises(ValueError):
        LiteratureSource(source_id="source", title="")


def test_literature_source_roundtrip() -> None:
    source = LiteratureSource(
        source_id="src",
        title="Title",
        authors=["A"],
        year=2020,
        source_type="paper",
    )

    assert LiteratureSource.from_dict(source.to_dict()).to_dict() == source.to_dict()


def test_load_save_sample_sources(tmp_path: Path) -> None:
    sources = load_literature_sources("data/literature_queue/raw_sources.sample.json")
    out = tmp_path / "sources.json"
    save_literature_sources(sources, out)

    assert len(load_literature_sources(out)) == 2
