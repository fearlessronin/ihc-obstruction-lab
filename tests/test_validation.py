import pytest

from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import (
    BottleneckLabel,
    ChannelLabel,
    ComputabilityLevel,
    ObstructionStatus,
    SurvivalStatus,
    TrustLevel,
)
from ihc_lab.validation import validate_channel_record


def base_channel(**overrides) -> ObstructionChannel:
    data = {
        "id": "test_row",
        "display_name": "Test row",
        "source_corpus": "tests",
        "trust_level": TrustLevel.gold_hand_verified,
        "geometry_or_package": "test package",
        "channel_labels": [ChannelLabel.cup_product_bockstein],
        "source_packages": [],
        "active_operations": [],
        "survival_status": SurvivalStatus.unknown,
        "obstruction_status": ObstructionStatus.unknown,
        "computability_level": ComputabilityLevel.level_0_metadata,
        "bottleneck": BottleneckLabel.unknown,
        "citation_keys": [],
    }
    data.update(overrides)
    return ObstructionChannel(**data)


def test_generated_candidate_must_have_bottleneck_warning() -> None:
    record = base_channel(
        trust_level=TrustLevel.generated_candidate,
        bottleneck=BottleneckLabel.none,
    )

    warnings = validate_channel_record(record)
    assert any("generated candidate must include a bottleneck" in item for item in warnings)


def test_theorem_backed_literature_requires_citation_keys_warning() -> None:
    record = base_channel(trust_level=TrustLevel.theorem_backed_literature)

    warnings = validate_channel_record(record)
    assert any("lacks citation_keys" in item for item in warnings)


def test_nodal_free_relation_cannot_mix_with_local_discriminant() -> None:
    with pytest.raises(ValueError):
        base_channel(
            channel_labels=[
                ChannelLabel.nodal_free_relation,
                ChannelLabel.local_discriminant,
            ]
        )
