"""Research-priority ranking for generated obstruction-channel candidates."""

from __future__ import annotations

from dataclasses import dataclass

from ihc_lab.channels import ObstructionChannel
from ihc_lab.enums import BottleneckLabel, ChannelLabel, ComputabilityLevel, ObstructionStatus


@dataclass(frozen=True)
class CandidateScore:
    record_id: str
    score: float
    formal_validity: float
    theorem_analogy: float
    survival_plausibility: float
    computability: float
    motivic_lift_compatibility: float
    bottleneck: str
    explanation: str


def _formal_validity(record: ObstructionChannel) -> float:
    if (
        record.cup_product_candidate is not None
        and record.cup_product_candidate.is_degree_twist_valid()
    ):
        return 1.0
    if (
        ChannelLabel.shadow_selection in record.channel_labels
        and record.shadow_selector is not None
        and not record.shadow_selector.source_group.is_trivial()
    ):
        return 0.8
    return 0.0


def _theorem_analogy(record: ObstructionChannel) -> float:
    if record.id == "diaz_level_2_generated_or_reference":
        return 1.0
    if record.id.startswith("coble_diaz_level_"):
        return 0.8
    if ChannelLabel.shadow_selection in record.channel_labels:
        return 0.6
    return 0.4


def _survival_plausibility(record: ObstructionChannel) -> float:
    if record.bottleneck in {BottleneckLabel.survival_proved_in_source, BottleneckLabel.none}:
        return 1.0
    if record.bottleneck == BottleneckLabel.unramified_nonvanishing:
        return 0.5
    if record.bottleneck == BottleneckLabel.global_transport_survival:
        return 0.4
    if record.bottleneck == BottleneckLabel.specialization_bridge:
        return 0.3
    return 0.2


def _computability(record: ObstructionChannel) -> float:
    if record.computability_level in {
        ComputabilityLevel.level_2_computed_group,
        ComputabilityLevel.level_1_symbolic,
    }:
        return 1.0
    if (
        record.cup_product_candidate is not None
        and record.cup_product_candidate.is_degree_twist_valid()
    ):
        return 0.8
    if record.computability_level == ComputabilityLevel.level_3_theorem_import:
        return 0.6
    if record.computability_level == ComputabilityLevel.level_4_candidate:
        return 0.5
    return 0.5


def _motivic_lift_compatibility(record: ObstructionChannel) -> float:
    if ChannelLabel.cup_product_bockstein in record.channel_labels:
        return 0.8
    if ChannelLabel.shadow_selection in record.channel_labels:
        return 0.7
    if ChannelLabel.local_discriminant in record.channel_labels:
        return 0.6
    return 0.5


def score_candidate(record: ObstructionChannel) -> CandidateScore:
    formal_validity = _formal_validity(record)
    theorem_analogy = _theorem_analogy(record)
    survival_plausibility = _survival_plausibility(record)
    computability = _computability(record)
    motivic_lift_compatibility = _motivic_lift_compatibility(record)
    score = (
        0.30 * formal_validity
        + 0.25 * theorem_analogy
        + 0.20 * survival_plausibility
        + 0.15 * computability
        + 0.10 * motivic_lift_compatibility
    )
    explanation = (
        "Research-priority score, not a truth probability. "
        f"Formal validity={formal_validity:.2f}; "
        f"survival bottleneck={record.bottleneck.value}; "
        f"theorem analogy={theorem_analogy:.2f}."
    )
    return CandidateScore(
        record_id=record.id,
        score=round(score, 4),
        formal_validity=formal_validity,
        theorem_analogy=theorem_analogy,
        survival_plausibility=survival_plausibility,
        computability=computability,
        motivic_lift_compatibility=motivic_lift_compatibility,
        bottleneck=record.bottleneck.value,
        explanation=explanation,
    )


def rank_candidates(records: list[ObstructionChannel]) -> list[CandidateScore]:
    scores = [score_candidate(record) for record in records]
    return sorted(scores, key=lambda item: (-item.score, item.record_id))
