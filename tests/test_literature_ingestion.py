from pathlib import Path

import pytest

from ihc_lab.literature.ingestion import (
    LiteratureExcerpt,
    load_excerpt_txt,
    load_excerpts_json,
    save_excerpts_json,
)


def test_load_sample_excerpt_txt_succeeds() -> None:
    excerpt = load_excerpt_txt(
        "data/literature_queue/excerpts/sample_colliot_theleme_voisin_excerpt.txt",
        source_id="colliot_theleme_voisin_2012_unramified",
    )

    assert excerpt.source_id == "colliot_theleme_voisin_2012_unramified"
    assert excerpt.excerpt_id.endswith("sample_colliot_theleme_voisin_excerpt")
    assert "unramified" in excerpt.text


def test_empty_excerpt_file_raises(tmp_path: Path) -> None:
    path = tmp_path / "empty.txt"
    path.write_text("  \n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_excerpt_txt(path, source_id="source")


def test_excerpt_roundtrip_json(tmp_path: Path) -> None:
    excerpt = LiteratureExcerpt(
        excerpt_id="excerpt",
        source_id="source",
        text="Some local text.",
    )
    assert LiteratureExcerpt.from_dict(excerpt.to_dict()).to_dict() == excerpt.to_dict()

    path = tmp_path / "excerpts.json"
    save_excerpts_json([excerpt], path)
    assert load_excerpts_json(path)[0].to_dict() == excerpt.to_dict()
