from pathlib import Path

from ihc_lab.analytics.metadata import (
    infer_basic_metadata,
    load_record_metadata,
    metadata_for_record,
)
from ihc_lab.channels import ObstructionChannel
from ihc_lab.datasets import load_seed_rows
from ihc_lab.enums import (
    BottleneckLabel,
    ComputabilityLevel,
    ObstructionStatus,
    SurvivalStatus,
    TrustLevel,
)


def test_load_record_metadata_succeeds() -> None:
    metadata = load_record_metadata()

    assert "diaz_level_two" in metadata
    assert metadata["diaz_level_two"].publication_year == 2023


def test_metadata_for_known_seed_row() -> None:
    records = load_seed_rows()
    diaz = next(record for record in records if record.id == "diaz_level_two")
    metadata = metadata_for_record(diaz, load_record_metadata())

    assert metadata is not None
    assert metadata.family_id == "diaz_level_two_bockstein"


def test_infer_basic_metadata_for_row_without_overlay() -> None:
    record = ObstructionChannel(
        id="unlisted",
        display_name="Unlisted",
        source_corpus="test",
        trust_level=TrustLevel.generated_candidate,
        geometry_or_package="test",
        channel_labels=[],
        source_packages=[],
        active_operations=[],
        survival_status=SurvivalStatus.unknown,
        obstruction_status=ObstructionStatus.formal_candidate,
        computability_level=ComputabilityLevel.level_4_candidate,
        bottleneck=BottleneckLabel.unknown,
        citation_keys=[],
    )
    metadata = infer_basic_metadata(record)

    assert metadata.publication_year is None
    assert metadata.family_id == "unlisted"
    assert metadata.count_as_candidate is True


def test_metadata_functions_do_not_mutate_seed_rows() -> None:
    before = Path("data/seed_rows.json").read_bytes()

    load_record_metadata()
    infer_basic_metadata(load_seed_rows()[0])

    assert Path("data/seed_rows.json").read_bytes() == before
