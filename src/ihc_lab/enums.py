"""Controlled vocabularies for obstruction-channel records."""

from __future__ import annotations

from enum import Enum
from typing import TypeVar


class ValueEnum(str, Enum):
    """String enum with compact JSON rendering."""

    def __str__(self) -> str:
        return self.value


EnumT = TypeVar("EnumT", bound=ValueEnum)


def parse_enum(enum_cls: type[EnumT], value: EnumT | str) -> EnumT:
    if isinstance(value, enum_cls):
        return value
    return enum_cls(str(value))


class TrustLevel(ValueEnum):
    gold_hand_verified = "gold_hand_verified"
    theorem_backed_literature = "theorem_backed_literature"
    computed_by_code = "computed_by_code"
    symbolically_validated = "symbolically_validated"
    llm_extracted_unverified = "llm_extracted_unverified"
    generated_candidate = "generated_candidate"
    speculative_template = "speculative_template"


class ComputabilityLevel(ValueEnum):
    level_0_metadata = "level_0_metadata"
    level_1_symbolic = "level_1_symbolic"
    level_2_computed_group = "level_2_computed_group"
    level_3_theorem_import = "level_3_theorem_import"
    level_4_candidate = "level_4_candidate"


class ChannelLabel(ValueEnum):
    local_discriminant = "local_discriminant"
    shadow_selection = "shadow_selection"
    torsion_trajectory = "torsion_trajectory"
    cup_product_bockstein = "cup_product_bockstein"
    brauer_unramified = "brauer_unramified"
    global_smooth_torsion = "global_smooth_torsion"
    enriques_product = "enriques_product"
    specialization_target = "specialization_target"
    lattice_saturation = "lattice_saturation"
    divisibility = "divisibility"
    nodal_free_relation = "nodal_free_relation"
    computed_lattice_benchmark = "computed_lattice_benchmark"
    matroidal_parity = "matroidal_parity"
    abelian_variety_channel = "abelian_variety_channel"
    degeneration_combinatorics = "degeneration_combinatorics"
    stacky_stabilizer = "stacky_stabilizer"
    unimodular_boundary = "unimodular_boundary"
    torsion_cohomology_operation = "torsion_cohomology_operation"
    channel_calibration = "channel_calibration"
    boundary_behavior = "boundary_behavior"
    categorical_ihc = "categorical_ihc"
    motivic_realization = "motivic_realization"


class OperationLabel(ValueEnum):
    support_transport = "support_transport"
    excision = "excision"
    local_to_global_transport = "local_to_global_transport"
    shadow_selection = "shadow_selection"
    pullback = "pullback"
    cup_product = "cup_product"
    bockstein = "bockstein"
    brauer_comparison = "brauer_comparison"
    unramified_survival = "unramified_survival"
    residue_test = "residue_test"
    smith_normal_form = "smith_normal_form"
    specialization = "specialization"
    stack_coarse_comparison = "stack_coarse_comparison"
    monodromy_comparison = "monodromy_comparison"
    global_relation = "global_relation"
    cohomology_operation = "cohomology_operation"
    divisibility_check = "divisibility_check"
    elementary_divisor_comparison = "elementary_divisor_comparison"
    fourier_transform = "fourier_transform"
    parity_check = "parity_check"


class SurvivalStatus(ValueEnum):
    theorem_backed = "theorem_backed"
    unknown = "unknown"
    candidate = "candidate"
    not_applicable = "not_applicable"
    survives = "survives"
    dies = "dies"
    residue_killed = "residue_killed"
    relation_killed = "relation_killed"
    survival_proved_in_source = "survival_proved_in_source"


class ObstructionStatus(ValueEnum):
    theorem_backed_obstruction = "theorem_backed_obstruction"
    computed_benchmark = "computed_benchmark"
    calibration_row = "calibration_row"
    candidate_survival_needed = "candidate_survival_needed"
    non_obstruction_boundary = "non_obstruction_boundary"
    formal_candidate = "formal_candidate"
    unknown = "unknown"


class BottleneckLabel(ValueEnum):
    none = "none"
    survival_proved_in_source = "survival_proved_in_source"
    unramified_nonvanishing = "unramified_nonvanishing"
    residue_vanishing = "residue_vanishing"
    global_transport_survival = "global_transport_survival"
    brauer_nonzero = "brauer_nonzero"
    stacky_realization = "stacky_realization"
    lattice_identification = "lattice_identification"
    specialization_bridge = "specialization_bridge"
    degree_twist_invalid = "degree_twist_invalid"
    global_relation_rank = "global_relation_rank"
    verify_theorem_statement = "verify_theorem_statement"
    unknown = "unknown"
