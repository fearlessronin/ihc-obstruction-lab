from ihc_lab.candidate_generator import (
    generate_all_candidates,
    generate_coble_diaz_level_candidates,
    generate_local_discriminant_shadow_candidates,
)
from ihc_lab.channels import ObstructionChannel
from ihc_lab.datasets import load_seed_rows
from ihc_lab.enums import BottleneckLabel, ObstructionStatus


def test_generate_coble_diaz_level_candidates() -> None:
    candidates = generate_coble_diaz_level_candidates(max_level=5)

    assert len(candidates) == 4
    assert all(candidate.cup_product_candidate is not None for candidate in candidates)
    assert all(
        candidate.cup_product_candidate.is_degree_twist_valid()
        for candidate in candidates
        if candidate.cup_product_candidate is not None
    )
    assert candidates[0].obstruction_status == ObstructionStatus.theorem_backed_obstruction
    assert all(
        candidate.obstruction_status == ObstructionStatus.candidate_survival_needed
        for candidate in candidates[1:]
    )

    targets = {
        candidate.cup_product_candidate.target_codimension: (
            candidate.cup_product_candidate.bockstein_target_string()
        )
        for candidate in candidates
        if candidate.cup_product_candidate is not None
    }
    assert targets[3] == "H^6(-, Z(3))"
    assert targets[4] == "H^8(-, Z(4))"
    assert targets[5] == "H^10(-, Z(5))"


def test_generate_local_discriminant_shadow_candidates() -> None:
    candidates = generate_local_discriminant_shadow_candidates(load_seed_rows())

    assert candidates
    assert all(
        candidate.bottleneck == BottleneckLabel.global_transport_survival
        for candidate in candidates
    )
    assert all(candidate.id != "coble_one_four_shadow" for candidate in candidates)


def test_generate_all_candidates_roundtrip_dicts() -> None:
    candidates = generate_all_candidates(load_seed_rows(), max_level=5)

    roundtripped = [ObstructionChannel.from_dict(candidate.to_dict()) for candidate in candidates]
    assert [candidate.id for candidate in roundtripped] == [candidate.id for candidate in candidates]
