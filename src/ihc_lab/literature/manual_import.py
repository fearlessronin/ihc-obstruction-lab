"""Manual JSON import for locally supplied extraction outputs."""

from __future__ import annotations

import json
from pathlib import Path

from ihc_lab.literature.extraction_schema import (
    ExtractedChannelCandidate,
    save_extracted_candidates,
)
from ihc_lab.literature.parsing import parse_many_extracted_candidates_json


def load_manual_extraction(path: str | Path) -> list[ExtractedChannelCandidate]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return parse_many_extracted_candidates_json(json.dumps(payload))


def save_manual_extraction(
    candidates: list[ExtractedChannelCandidate], output_path: str | Path
) -> None:
    save_extracted_candidates(candidates, output_path)


def import_manual_extraction(
    input_path: str | Path, output_path: str | Path
) -> list[ExtractedChannelCandidate]:
    candidates = load_manual_extraction(input_path)
    save_manual_extraction(candidates, output_path)
    return candidates
