"""Feature extraction for obstruction-channel records."""

from __future__ import annotations

from typing import TypeAlias

from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import (
    BottleneckLabel,
    ChannelLabel,
    ComputabilityLevel,
    ObstructionStatus,
    OperationLabel,
    TrustLevel,
)

FeatureValue: TypeAlias = bool | str | int


CHANNEL_FEATURES: dict[ChannelLabel, str] = {
    ChannelLabel.local_discriminant: "channel_local_discriminant",
    ChannelLabel.shadow_selection: "channel_shadow_selection",
    ChannelLabel.cup_product_bockstein: "channel_cup_product_bockstein",
    ChannelLabel.brauer_unramified: "channel_brauer_unramified",
    ChannelLabel.global_smooth_torsion: "channel_global_smooth_torsion",
    ChannelLabel.enriques_product: "channel_enriques_product",
    ChannelLabel.specialization_target: "channel_specialization_target",
    ChannelLabel.nodal_free_relation: "channel_nodal_free_relation",
    ChannelLabel.unimodular_boundary: "channel_unimodular_boundary",
    ChannelLabel.lattice_saturation: "channel_lattice_saturation",
    ChannelLabel.divisibility: "channel_divisibility",
    ChannelLabel.matroidal_parity: "channel_matroidal_parity",
    ChannelLabel.stacky_stabilizer: "channel_stacky_stabilizer",
}

TRUST_FEATURES: dict[TrustLevel, str] = {
    TrustLevel.gold_hand_verified: "trust_gold_hand_verified",
    TrustLevel.theorem_backed_literature: "trust_theorem_backed_literature",
    TrustLevel.generated_candidate: "trust_generated_candidate",
}

STATUS_FEATURES: dict[ObstructionStatus, str] = {
    ObstructionStatus.theorem_backed_obstruction: "status_theorem_backed_obstruction",
    ObstructionStatus.calibration_row: "status_calibration_row",
    ObstructionStatus.candidate_survival_needed: "status_candidate_survival_needed",
}

COMPUTABILITY_FEATURES: dict[ComputabilityLevel, str] = {
    ComputabilityLevel.level_0_metadata: "computability_level_0_metadata",
    ComputabilityLevel.level_1_symbolic: "computability_level_1_symbolic",
    ComputabilityLevel.level_2_computed_group: "computability_level_2_computed_group",
    ComputabilityLevel.level_3_theorem_import: "computability_level_3_theorem_import",
    ComputabilityLevel.level_4_candidate: "computability_level_4_candidate",
}

OPERATION_FEATURES: dict[OperationLabel, str] = {
    OperationLabel.pullback: "op_pullback",
    OperationLabel.cup_product: "op_cup_product",
    OperationLabel.bockstein: "op_bockstein",
    OperationLabel.unramified_survival: "op_unramified_survival",
    OperationLabel.brauer_comparison: "op_brauer_comparison",
    OperationLabel.smith_normal_form: "op_smith_normal_form",
    OperationLabel.shadow_selection: "op_shadow_selection",
    OperationLabel.global_relation: "op_global_relation",
    OperationLabel.support_transport: "op_support_transport",
    OperationLabel.specialization: "op_specialization",
}

BOTTLENECK_FEATURES: dict[BottleneckLabel, str] = {
    BottleneckLabel.global_transport_survival: "bottleneck_global_transport_survival",
    BottleneckLabel.global_relation_rank: "bottleneck_global_relation_rank",
    BottleneckLabel.none: "bottleneck_none",
    BottleneckLabel.specialization_bridge: "bottleneck_specialization_bridge",
    BottleneckLabel.survival_proved_in_source: "bottleneck_survival_proved_in_source",
    BottleneckLabel.unramified_nonvanishing: "bottleneck_unramified_nonvanishing",
}


def _false_feature_block(names: list[str]) -> dict[str, bool]:
    return {name: False for name in names}


def extract_features(record: ObstructionChannel) -> dict[str, FeatureValue]:
    """Return a flat, deterministic feature dictionary for one channel row."""

    features: dict[str, FeatureValue] = {
        "record_id": record.id,
        "channel_count": len(record.channel_labels),
        "primary_channel_count": len(record.channel_labels),
        "is_multichannel": len(record.channel_labels) > 1,
    }

    features.update(_false_feature_block(list(CHANNEL_FEATURES.values())))
    features.update(_false_feature_block(list(TRUST_FEATURES.values())))
    features.update(_false_feature_block(list(STATUS_FEATURES.values())))
    features.update(_false_feature_block(list(COMPUTABILITY_FEATURES.values())))
    features.update(_false_feature_block(list(OPERATION_FEATURES.values())))
    features.update(_false_feature_block(list(BOTTLENECK_FEATURES.values())))

    for label in record.channel_labels:
        feature_name = CHANNEL_FEATURES.get(label)
        if feature_name is not None:
            features[feature_name] = True

    if record.trust_level in TRUST_FEATURES:
        features[TRUST_FEATURES[record.trust_level]] = True
    if record.obstruction_status in STATUS_FEATURES:
        features[STATUS_FEATURES[record.obstruction_status]] = True
    if record.computability_level in COMPUTABILITY_FEATURES:
        features[COMPUTABILITY_FEATURES[record.computability_level]] = True
    if record.bottleneck in BOTTLENECK_FEATURES:
        features[BOTTLENECK_FEATURES[record.bottleneck]] = True

    for operation in record.active_operations:
        feature_name = OPERATION_FEATURES.get(operation)
        if feature_name is not None:
            features[feature_name] = True

    has_local_package = record.local_package is not None
    local_group_trivial = bool(
        record.local_package is not None and record.local_package.local_group.is_trivial()
    )
    local_group_nontrivial = bool(
        record.local_package is not None and not record.local_package.local_group.is_trivial()
    )
    has_shadow_selector = record.shadow_selector is not None
    has_cup_product_candidate = record.cup_product_candidate is not None

    features.update(
        {
            "has_local_package": has_local_package,
            "local_group_nontrivial": local_group_nontrivial,
            "local_group_trivial": local_group_trivial,
            "has_shadow_selector": has_shadow_selector,
            "valid_z4_to_z2_shadow": bool(
                record.shadow_selector is not None
                and record.shadow_selector.validate_z4_order_two_shadow()
            ),
            "has_cup_product_candidate": has_cup_product_candidate,
            "cup_product_degree_twist_valid": bool(
                record.cup_product_candidate is not None
                and record.cup_product_candidate.is_degree_twist_valid()
            ),
            "has_torsion_trajectory": record.torsion_trajectory is not None,
        }
    )

    return features


def extract_feature_matrix(
    records: list[ObstructionChannel],
) -> list[dict[str, FeatureValue]]:
    return [extract_features(record) for record in records]
