from ihc_lab.datasets import load_seed_rows
from ihc_lab.features import extract_features


def row(record_id: str):
    return next(record for record in load_seed_rows() if record.id == record_id)


def test_diaz_features() -> None:
    features = extract_features(row("diaz_level_two"))

    assert features["has_cup_product_candidate"] is True
    assert features["cup_product_degree_twist_valid"] is True
    assert features["channel_cup_product_bockstein"] is True
    assert features["channel_brauer_unramified"] is True
    assert features["bottleneck_survival_proved_in_source"] is True


def test_level_three_candidate_features() -> None:
    features = extract_features(row("level_three_coble_diaz_candidate"))

    assert features["has_cup_product_candidate"] is True
    assert features["cup_product_degree_twist_valid"] is True
    assert features["trust_generated_candidate"] is True
    assert features["status_candidate_survival_needed"] is True
    assert features["bottleneck_unramified_nonvanishing"] is True


def test_coble_shadow_features() -> None:
    features = extract_features(row("coble_one_four_shadow"))

    assert features["has_local_package"] is True
    assert features["local_group_nontrivial"] is True
    assert features["has_shadow_selector"] is True
    assert features["valid_z4_to_z2_shadow"] is True
    assert features["channel_shadow_selection"] is True


def test_e8_boundary_features() -> None:
    features = extract_features(row("e8_surface_unimodular_boundary"))

    assert features["channel_unimodular_boundary"] is True
    assert features["local_group_trivial"] is True
    assert features["bottleneck_none"] is True
