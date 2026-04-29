"""Analytics metadata overlay for atlas records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import ObstructionStatus, TrustLevel


@dataclass
class RecordAnalyticsMetadata:
    record_id: str
    publication_year: int | None
    primary_reference: str | None
    family_id: str
    is_primary_family_anchor: bool
    count_as_obstruction: bool
    count_as_candidate: bool
    count_as_boundary: bool
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_year": self.publication_year,
            "primary_reference": self.primary_reference,
            "family_id": self.family_id,
            "is_primary_family_anchor": self.is_primary_family_anchor,
            "count_as_obstruction": self.count_as_obstruction,
            "count_as_candidate": self.count_as_candidate,
            "count_as_boundary": self.count_as_boundary,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(
        cls, record_id: str, data: dict[str, Any] | "RecordAnalyticsMetadata"
    ) -> "RecordAnalyticsMetadata":
        if isinstance(data, cls):
            return data
        return cls(
            record_id=record_id,
            publication_year=data.get("publication_year"),
            primary_reference=data.get("primary_reference"),
            family_id=data.get("family_id") or record_id,
            is_primary_family_anchor=bool(data.get("is_primary_family_anchor", True)),
            count_as_obstruction=bool(data.get("count_as_obstruction", False)),
            count_as_candidate=bool(data.get("count_as_candidate", False)),
            count_as_boundary=bool(data.get("count_as_boundary", False)),
            notes=data.get("notes"),
        )


def load_record_metadata(
    path: str | Path = "data/analytics/record_metadata.json",
) -> dict[str, RecordAnalyticsMetadata]:
    with Path(path).open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return {
        record_id: RecordAnalyticsMetadata.from_dict(record_id, item)
        for record_id, item in payload.items()
    }


def save_record_metadata(
    metadata: dict[str, RecordAnalyticsMetadata], path: str | Path
) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {record_id: item.to_dict() for record_id, item in metadata.items()}
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def metadata_for_record(
    record: ObstructionChannel,
    metadata_map: dict[str, RecordAnalyticsMetadata],
) -> RecordAnalyticsMetadata | None:
    return metadata_map.get(record.id)


def infer_basic_metadata(record: ObstructionChannel) -> RecordAnalyticsMetadata:
    count_as_obstruction = (
        record.obstruction_status == ObstructionStatus.theorem_backed_obstruction
    )
    count_as_candidate = record.trust_level == TrustLevel.generated_candidate
    count_as_boundary = record.obstruction_status in {
        ObstructionStatus.calibration_row,
        ObstructionStatus.non_obstruction_boundary,
    }
    return RecordAnalyticsMetadata(
        record_id=record.id,
        publication_year=None,
        primary_reference=record.citation_keys[0] if record.citation_keys else None,
        family_id=record.id,
        is_primary_family_anchor=True,
        count_as_obstruction=count_as_obstruction,
        count_as_candidate=count_as_candidate,
        count_as_boundary=count_as_boundary,
        notes="Inferred fallback metadata.",
    )


def merge_record_with_metadata(
    record: ObstructionChannel,
    metadata_map: dict[str, RecordAnalyticsMetadata],
) -> dict[str, Any]:
    metadata = metadata_for_record(record, metadata_map) or infer_basic_metadata(record)
    return {
        "record": record,
        "record_id": record.id,
        "publication_year": metadata.publication_year,
        "primary_reference": metadata.primary_reference,
        "family_id": metadata.family_id,
        "is_primary_family_anchor": metadata.is_primary_family_anchor,
        "count_as_obstruction": metadata.count_as_obstruction,
        "count_as_candidate": metadata.count_as_candidate,
        "count_as_boundary": metadata.count_as_boundary,
        "notes": metadata.notes,
    }
