"""Deterministic rule-based classification for obstruction-channel rows."""

from __future__ import annotations

from dataclasses import dataclass

from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import BottleneckLabel, ChannelLabel, ObstructionStatus, SurvivalStatus


@dataclass(frozen=True)
class ClassificationResult:
    record_id: str
    predicted_channels: list[str]
    generator_status: str
    bottleneck: str
    explanations: list[str]


def classify_record(record: ObstructionChannel) -> ClassificationResult:
    """Classify a seed-row record using deterministic channel rules."""

    labels = set(record.channel_labels)
    explanations: list[str] = []
    generator_status = record.obstruction_status.value

    if ChannelLabel.local_discriminant in labels:
        explanations.append("Uses a local package/discriminant channel.")
        if record.local_package is not None:
            local_group = record.local_package.local_group
            if local_group.is_trivial():
                explanations.append(
                    "Local group is trivial, so the row is boundary/unimodular-like."
                )
            else:
                explanations.append(f"Finite local group is active: {local_group}.")

    if ChannelLabel.unimodular_boundary in labels:
        generator_status = "calibration"
        explanations.append(
            "Nontrivial local geometry can have trivial discriminant group in a "
            "unimodular boundary row."
        )

    if ChannelLabel.nodal_free_relation in labels:
        generator_status = "calibration"
        explanations.append(
            "Belongs to the free vanishing-cycle/global-relation channel, not "
            "surface-type finite local torsion."
        )

    if ChannelLabel.shadow_selection in labels:
        explanations.append("Uses a selected subgroup/quotient/shadow channel.")
        if (
            record.shadow_selector is not None
            and record.shadow_selector.validate_z4_order_two_shadow()
        ):
            explanations.append("Validated Z/4 -> Z/2 order-two shadow selector.")

    if ChannelLabel.cup_product_bockstein in labels:
        candidate = record.cup_product_candidate
        if candidate is not None:
            if candidate.is_degree_twist_valid():
                explanations.append(
                    "Cup-product Bockstein candidate has valid degree/twist arithmetic."
                )
            else:
                explanations.append(
                    "Cup-product Bockstein candidate has invalid degree/twist arithmetic."
                )
            explanations.append(f"Bockstein target: {candidate.bockstein_target_string()}.")

        if record.survival_status in {
            SurvivalStatus.theorem_backed,
            SurvivalStatus.survival_proved_in_source,
        }:
            generator_status = "theorem_backed_obstruction"

        if (
            record.obstruction_status == ObstructionStatus.candidate_survival_needed
            or record.bottleneck == BottleneckLabel.unramified_nonvanishing
        ):
            generator_status = "formal_candidate_survival_needed"

    if ChannelLabel.brauer_unramified in labels:
        explanations.append("Includes a Brauer/unramified survival station.")

    if ChannelLabel.global_smooth_torsion in labels:
        explanations.append("Records a smooth global torsion benchmark.")

    if ChannelLabel.specialization_target in labels:
        explanations.append("Uses a specialization/comparison role.")

    if not explanations:
        explanations.append("No refining rule fired; using recorded obstruction status.")

    return ClassificationResult(
        record_id=record.id,
        predicted_channels=[label.value for label in record.channel_labels],
        generator_status=generator_status,
        bottleneck=record.bottleneck.value,
        explanations=explanations,
    )


def classify_records(records: list[ObstructionChannel]) -> list[ClassificationResult]:
    return [classify_record(record) for record in records]
