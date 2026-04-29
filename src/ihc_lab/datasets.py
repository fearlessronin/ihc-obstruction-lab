"""JSON dataset import/export helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from ihc_lab.channels import ObstructionChannel
from ihc_lab.validation import validate_seed_rows


def load_seed_rows(path: str | Path = "data/seed_rows.json") -> list[ObstructionChannel]:
    dataset_path = Path(path)
    with dataset_path.open("r", encoding="utf-8") as handle:
        raw_records = json.load(handle)
    return [ObstructionChannel.from_dict(item) for item in raw_records]


def save_seed_rows(records: Iterable[ObstructionChannel], path: str | Path) -> None:
    dataset_path = Path(path)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [record.to_dict() for record in records]
    with dataset_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def dataset_summary(records: list[ObstructionChannel]) -> dict:
    return validate_seed_rows(records)
