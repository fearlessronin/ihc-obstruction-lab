"""Temporal channel-distribution analytics for atlas records."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Literal

from ihc_lab.channels import ObstructionChannel
from ihc_lab.datasets import load_canonical_literature_rows, load_seed_rows
from ihc_lab.enums import ObstructionStatus, TrustLevel
from ihc_lab.analytics.metadata import (
    RecordAnalyticsMetadata,
    infer_basic_metadata,
    metadata_for_record,
)

CountMode = Literal["row", "family"]
"""Count modes for channel-level analytics.

``row`` counts every record-channel pair. ``family`` counts every distinct
family-channel-tier combination. The latter is still a channel-distribution
mode: one multi-channel family appears once in each channel it occupies.
Unique-family analytics below count each family independently of channels.
"""


class LegitimacyTier:
    theorem_backed_obstruction = "theorem_backed_obstruction"
    computed_benchmark = "computed_benchmark"
    boundary_or_calibration = "boundary_or_calibration"
    reviewed_candidate = "reviewed_candidate"
    generated_candidate = "generated_candidate"
    unverified_extracted = "unverified_extracted"
    unknown = "unknown"


def _load_channel_rows(path: str | Path) -> list[ObstructionChannel]:
    dataset_path = Path(path)
    if not dataset_path.exists():
        return []
    with dataset_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return [ObstructionChannel.from_dict(item) for item in payload]


def legitimacy_tier(
    record: ObstructionChannel,
    metadata: RecordAnalyticsMetadata | None = None,
) -> str:
    if (
        record.trust_level == TrustLevel.theorem_backed_literature
        and record.obstruction_status == ObstructionStatus.theorem_backed_obstruction
    ):
        return LegitimacyTier.theorem_backed_obstruction
    if record.obstruction_status == ObstructionStatus.computed_benchmark:
        return LegitimacyTier.computed_benchmark
    if record.trust_level == TrustLevel.llm_extracted_unverified:
        return LegitimacyTier.unverified_extracted
    if record.obstruction_status in {
        ObstructionStatus.calibration_row,
        ObstructionStatus.non_obstruction_boundary,
    } or (metadata is not None and metadata.count_as_boundary):
        return LegitimacyTier.boundary_or_calibration
    if record.trust_level == TrustLevel.generated_candidate or (
        metadata is not None and metadata.count_as_candidate
    ):
        return LegitimacyTier.generated_candidate
    return LegitimacyTier.unknown


def collect_atlas_records(
    include_seed: bool = True,
    include_canonical: bool = True,
    include_generated: bool = True,
    include_promoted: bool = False,
) -> list[ObstructionChannel]:
    records: list[ObstructionChannel] = []
    if include_seed:
        records.extend(load_seed_rows())
    if include_canonical:
        canonical_path = Path("data/canonical_literature_rows.json")
        if canonical_path.exists():
            records.extend(load_canonical_literature_rows(canonical_path))
    if include_generated:
        records.extend(_load_channel_rows("data/generated_candidates.json"))
    if include_promoted:
        records.extend(_load_channel_rows("data/literature_queue/canonical_literature.candidates.json"))
    return records


def _metadata(record: ObstructionChannel, metadata_map: dict[str, RecordAnalyticsMetadata]):
    return metadata_for_record(record, metadata_map) or infer_basic_metadata(record)


def channel_year_counts(
    records: list[ObstructionChannel],
    metadata_map: dict[str, RecordAnalyticsMetadata],
    count_mode: CountMode = "row",
    strict: bool = False,
) -> list[dict]:
    if count_mode not in {"row", "family"}:
        raise ValueError(f"unknown count mode: {count_mode}")
    counter: Counter[tuple[int | None, str, str]] = Counter()
    seen_families: set[tuple[str, str, str]] = set()
    for record in records:
        metadata = _metadata(record, metadata_map)
        tier = legitimacy_tier(record, metadata)
        if strict and tier != LegitimacyTier.theorem_backed_obstruction:
            continue
        year = metadata.publication_year
        for label in record.channel_labels:
            channel = label.value
            if count_mode == "family":
                family_key = (metadata.family_id, channel, tier)
                if family_key in seen_families:
                    continue
                seen_families.add(family_key)
            counter[(year, channel, tier)] += 1
    return [
        {
            "year": year,
            "channel": channel,
            "tier": tier,
            "count": count,
            "count_mode": count_mode,
        }
        for (year, channel, tier), count in sorted(
            counter.items(),
            key=lambda item: (
                item[0][0] is None,
                item[0][0] or 0,
                item[0][1],
                item[0][2],
            ),
        )
    ]


def channel_summary(
    records: list[ObstructionChannel],
    metadata_map: dict[str, RecordAnalyticsMetadata],
    count_mode: CountMode = "family",
) -> list[dict]:
    counts = channel_year_counts(records, metadata_map, count_mode=count_mode)
    by_channel: dict[str, dict] = {}
    for row in counts:
        channel = row["channel"]
        summary = by_channel.setdefault(
            channel,
            {
                "channel": channel,
                "first_year": None,
                "last_year": None,
                "theorem_backed_obstruction_count": 0,
                "computed_benchmark_count": 0,
                "boundary_or_calibration_count": 0,
                "generated_candidate_count": 0,
                "unverified_extracted_count": 0,
                "total_count": 0,
            },
        )
        year = row["year"]
        if isinstance(year, int):
            summary["first_year"] = (
                year if summary["first_year"] is None else min(summary["first_year"], year)
            )
            summary["last_year"] = (
                year if summary["last_year"] is None else max(summary["last_year"], year)
            )
        tier_key = f"{row['tier']}_count"
        if tier_key in summary:
            summary[tier_key] += row["count"]
        summary["total_count"] += row["count"]
    return sorted(by_channel.values(), key=lambda row: row["channel"])


def legitimacy_tier_summary(
    records: list[ObstructionChannel],
    metadata_map: dict[str, RecordAnalyticsMetadata],
    count_mode: CountMode = "family",
) -> list[dict]:
    counts = channel_year_counts(records, metadata_map, count_mode=count_mode)
    by_tier: defaultdict[str, int] = defaultdict(int)
    for row in counts:
        by_tier[row["tier"]] += row["count"]
    return [
        {"tier": tier, "count": count}
        for tier, count in sorted(by_tier.items())
    ]


def unique_family_tier_summary(
    records: list[ObstructionChannel],
    metadata_map: dict[str, RecordAnalyticsMetadata],
    strict: bool = False,
) -> list[dict]:
    families: set[tuple[str, str]] = set()
    for record in records:
        metadata = _metadata(record, metadata_map)
        tier = legitimacy_tier(record, metadata)
        if strict and tier != LegitimacyTier.theorem_backed_obstruction:
            continue
        families.add((metadata.family_id, tier))
    counts: defaultdict[str, int] = defaultdict(int)
    for _, tier in families:
        counts[tier] += 1
    return [
        {"tier": tier, "family_count": count}
        for tier, count in sorted(counts.items())
    ]


def unique_family_year_summary(
    records: list[ObstructionChannel],
    metadata_map: dict[str, RecordAnalyticsMetadata],
    strict: bool = False,
) -> list[dict]:
    families: set[tuple[str, int | None, str]] = set()
    for record in records:
        metadata = _metadata(record, metadata_map)
        tier = legitimacy_tier(record, metadata)
        if strict and tier != LegitimacyTier.theorem_backed_obstruction:
            continue
        families.add((metadata.family_id, metadata.publication_year, tier))
    counts: defaultdict[tuple[int | None, str], int] = defaultdict(int)
    for _, year, tier in families:
        counts[(year, tier)] += 1
    return [
        {"year": year, "tier": tier, "family_count": count}
        for (year, tier), count in sorted(
            counts.items(),
            key=lambda item: (
                item[0][0] is None,
                item[0][0] or 0,
                item[0][1],
            ),
        )
    ]


def unique_family_channel_summary(
    records: list[ObstructionChannel],
    metadata_map: dict[str, RecordAnalyticsMetadata],
    strict: bool = False,
) -> list[dict]:
    families: dict[str, dict] = {}
    for record in records:
        metadata = _metadata(record, metadata_map)
        tier = legitimacy_tier(record, metadata)
        if strict and tier != LegitimacyTier.theorem_backed_obstruction:
            continue
        current = families.setdefault(
            metadata.family_id,
            {
                "family_id": metadata.family_id,
                "primary_reference": metadata.primary_reference,
                "publication_year": metadata.publication_year,
                "tier": tier,
                "channels": set(),
                "representative_record_id": record.id,
                "_has_primary_anchor": False,
            },
        )
        current["channels"].update(label.value for label in record.channel_labels)
        if metadata.primary_reference and not current["primary_reference"]:
            current["primary_reference"] = metadata.primary_reference
        if metadata.publication_year is not None and current["publication_year"] is None:
            current["publication_year"] = metadata.publication_year
        if metadata.is_primary_family_anchor and not current["_has_primary_anchor"]:
            current["representative_record_id"] = record.id
            current["_has_primary_anchor"] = True
            current["tier"] = tier
    return [
        {
            "family_id": item["family_id"],
            "primary_reference": item["primary_reference"],
            "publication_year": item["publication_year"],
            "tier": item["tier"],
            "channels": sorted(item["channels"]),
            "representative_record_id": item["representative_record_id"],
        }
        for item in sorted(families.values(), key=lambda row: row["family_id"])
    ]
