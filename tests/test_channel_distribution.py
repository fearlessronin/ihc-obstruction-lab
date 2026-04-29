from ihc_lab.analytics.channel_distribution import (
    LegitimacyTier,
    channel_summary,
    channel_year_counts,
    collect_atlas_records,
    legitimacy_tier,
    legitimacy_tier_summary,
)
from ihc_lab.analytics.metadata import load_record_metadata


def test_collect_atlas_records_returns_seed_canonical_and_generated() -> None:
    records = collect_atlas_records()
    ids = {record.id for record in records}

    assert "diaz_level_two" in ids
    assert "atiyah_hirzebruch_torsion_operation_anchor" in ids
    assert "coble_diaz_level_4_candidate" in ids


def test_legitimacy_tier_identifies_diaz_theorem_backed() -> None:
    metadata = load_record_metadata()
    diaz = next(record for record in collect_atlas_records() if record.id == "diaz_level_two")

    assert legitimacy_tier(diaz, metadata[diaz.id]) == LegitimacyTier.theorem_backed_obstruction


def test_channel_year_counts_has_year_channel_and_count() -> None:
    metadata = load_record_metadata()
    counts = channel_year_counts(collect_atlas_records(), metadata)

    assert counts
    assert {"year", "channel", "tier", "count", "count_mode"} <= set(counts[0])


def test_strict_counts_include_only_theorem_backed_obstructions() -> None:
    metadata = load_record_metadata()
    counts = channel_year_counts(collect_atlas_records(), metadata, strict=True)

    assert counts
    assert {row["tier"] for row in counts} == {LegitimacyTier.theorem_backed_obstruction}


def test_family_count_deduplicates_generated_diaz_reference() -> None:
    records = [
        record
        for record in collect_atlas_records()
        if record.id in {"diaz_level_two", "diaz_level_2_generated_or_reference"}
    ]
    metadata = load_record_metadata()
    row_counts = channel_year_counts(records, metadata, count_mode="row")
    family_counts = channel_year_counts(records, metadata, count_mode="family")

    assert sum(row["count"] for row in row_counts) > sum(row["count"] for row in family_counts)


def test_channel_summary_contains_expected_channels() -> None:
    metadata = load_record_metadata()
    summary = channel_summary(collect_atlas_records(), metadata)
    channels = {row["channel"] for row in summary}

    assert "cup_product_bockstein" in channels
    assert "brauer_unramified" in channels


def test_tier_summary_contains_theorem_and_generated() -> None:
    metadata = load_record_metadata()
    summary = legitimacy_tier_summary(collect_atlas_records(), metadata)
    tiers = {row["tier"] for row in summary}

    assert LegitimacyTier.theorem_backed_obstruction in tiers
    assert LegitimacyTier.generated_candidate in tiers
