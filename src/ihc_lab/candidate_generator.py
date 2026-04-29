"""Formal candidate generators for obstruction-channel mechanisms."""

from __future__ import annotations

from copy import deepcopy

from ihc_lab.channels import ObstructionChannel
from ihc_lab.cup_products import CupProductCandidate
from ihc_lab.enums import (
    BottleneckLabel,
    ChannelLabel,
    ComputabilityLevel,
    ObstructionStatus,
    OperationLabel,
    SurvivalStatus,
    TrustLevel,
)
from ihc_lab.finite_coefficients import FiniteCoefficientInput
from ihc_lab.groups import FiniteAbelianGroup
from ihc_lab.shadows import ShadowSelector


def build_standard_finite_inputs() -> list[FiniteCoefficientInput]:
    return [
        FiniteCoefficientInput(
            class_name="alpha",
            variety_factor="S",
            cohomological_degree=1,
            twist=1,
            coefficient=2,
            source_type="enriques_double_cover_class",
            theorem_status="theorem_backed_source",
        ),
        FiniteCoefficientInput(
            class_name="beta",
            variety_factor="S_i",
            cohomological_degree=2,
            twist=1,
            coefficient=2,
            source_type="brauer_detecting_class",
            theorem_status="theorem_backed_source",
        ),
    ]


def _level_inputs(level: int) -> list[FiniteCoefficientInput]:
    alpha, beta_template = build_standard_finite_inputs()
    inputs = [deepcopy(alpha)]
    for index in range(2, level + 1):
        beta = deepcopy(beta_template)
        beta.class_name = "beta" if level == 2 else f"beta_{index}"
        beta.variety_factor = f"S_{index}"
        inputs.append(beta)
    return inputs


def generate_coble_diaz_level_candidates(max_level: int = 5) -> list[ObstructionChannel]:
    candidates: list[ObstructionChannel] = []
    for level in range(2, max_level + 1):
        theorem_backed = level == 2
        bottleneck = (
            BottleneckLabel.survival_proved_in_source
            if theorem_backed
            else BottleneckLabel.unramified_nonvanishing
        )
        obstruction_status = (
            ObstructionStatus.theorem_backed_obstruction
            if theorem_backed
            else ObstructionStatus.candidate_survival_needed
        )
        survival_status = (
            SurvivalStatus.survival_proved_in_source
            if theorem_backed
            else SurvivalStatus.unknown
        )
        trust_level = (
            TrustLevel.theorem_backed_literature
            if theorem_backed
            else TrustLevel.generated_candidate
        )
        channel_labels = [ChannelLabel.cup_product_bockstein]
        active_operations = [OperationLabel.cup_product, OperationLabel.bockstein]
        if theorem_backed:
            channel_labels.append(ChannelLabel.brauer_unramified)
            active_operations.append(OperationLabel.unramified_survival)

        cup_product = CupProductCandidate(
            inputs=_level_inputs(level),
            target_codimension=level,
            coefficient=2,
            survival_status=survival_status,
            obstruction_status=obstruction_status,
            bottleneck=bottleneck,
            comments=(
                "Theorem-backed level-two source."
                if theorem_backed
                else "Formal degree--twist valid; theorem-level survival/nonvanishing not proved."
            ),
        )
        record_id = (
            "diaz_level_2_generated_or_reference"
            if theorem_backed
            else f"coble_diaz_level_{level}_candidate"
        )
        candidates.append(
            ObstructionChannel(
                id=record_id,
                display_name=(
                    "Diaz level-2 generated reference"
                    if theorem_backed
                    else f"Coble-Diaz level-{level} formal candidate"
                ),
                source_corpus="generated_candidate_corpus",
                trust_level=trust_level,
                geometry_or_package=f"Coble-Diaz level-{level} cup-product package",
                channel_labels=channel_labels,
                source_packages=["finite_coefficient_cup_product", "bockstein"],
                active_operations=active_operations,
                survival_status=survival_status,
                obstruction_status=obstruction_status,
                computability_level=(
                    ComputabilityLevel.level_3_theorem_import
                    if theorem_backed
                    else ComputabilityLevel.level_4_candidate
                ),
                bottleneck=bottleneck,
                citation_keys=["Diaz2023", "RahmanDiazKummer2026"],
                comments=(
                    "Generated reference row for the theorem-backed Diaz level-2 mechanism."
                    if theorem_backed
                    else "Formal degree--twist valid; theorem-level survival/nonvanishing not proved."
                ),
                cup_product_candidate=cup_product,
            )
        )

    return candidates


def _has_even_shadow_source(group: FiniteAbelianGroup) -> bool:
    return any(factor % 2 == 0 for factor in group.cyclic_factors)


def _has_mod_five_source(group: FiniteAbelianGroup) -> bool:
    return any(factor % 5 == 0 for factor in group.cyclic_factors)


def generate_local_discriminant_shadow_candidates(
    records: list[ObstructionChannel],
) -> list[ObstructionChannel]:
    candidates: list[ObstructionChannel] = []
    for record in records:
        if record.local_package is None:
            continue
        if record.shadow_selector is not None or ChannelLabel.shadow_selection in record.channel_labels:
            continue

        group = record.local_package.local_group
        if group.is_trivial():
            continue

        selected_group: FiniteAbelianGroup | None = None
        coefficient: int | None = None
        selection_type: str | None = None
        suffix: str | None = None
        if _has_even_shadow_source(group):
            selected_group = FiniteAbelianGroup([2])
            coefficient = 2
            selection_type = "order_two_shadow_candidate"
            suffix = "z2_shadow_candidate"
        elif _has_mod_five_source(group):
            selected_group = FiniteAbelianGroup([5])
            coefficient = 5
            selection_type = "mod_five_shadow_candidate"
            suffix = "mod5_shadow_candidate"

        if selected_group is None or coefficient is None or selection_type is None or suffix is None:
            continue

        candidates.append(
            ObstructionChannel(
                id=f"{record.id}_{suffix}",
                display_name=f"{record.display_name} generated shadow candidate",
                source_corpus="generated_candidate_corpus",
                trust_level=TrustLevel.generated_candidate,
                geometry_or_package=record.geometry_or_package,
                channel_labels=[ChannelLabel.shadow_selection],
                source_packages=["local_discriminant_shadow_generator"],
                active_operations=[OperationLabel.shadow_selection],
                survival_status=SurvivalStatus.unknown,
                obstruction_status=ObstructionStatus.formal_candidate,
                computability_level=ComputabilityLevel.level_4_candidate,
                bottleneck=BottleneckLabel.global_transport_survival,
                citation_keys=list(record.citation_keys),
                comments=(
                    "Generated local-discriminant shadow candidate; global transport not proved."
                ),
                local_package=deepcopy(record.local_package),
                shadow_selector=ShadowSelector(
                    source_group=group,
                    selected_group=selected_group,
                    selection_type=selection_type,
                    coefficient=coefficient,
                    status="generated_candidate",
                    comments="Generated local-discriminant shadow selector.",
                ),
            )
        )

    return candidates


def generate_all_candidates(
    records: list[ObstructionChannel], max_level: int = 5
) -> list[ObstructionChannel]:
    return generate_coble_diaz_level_candidates(max_level=max_level) + (
        generate_local_discriminant_shadow_candidates(records)
    )
