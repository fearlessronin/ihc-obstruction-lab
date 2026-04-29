from ihc_lab.datasets import load_seed_rows
from ihc_lab.rule_classifier import classify_record


def record_by_id(record_id: str):
    return next(record for record in load_seed_rows() if record.id == record_id)


def test_diaz_classified_as_theorem_backed_obstruction() -> None:
    result = classify_record(record_by_id("diaz_level_two"))

    assert result.generator_status == "theorem_backed_obstruction"
    assert any("degree/twist" in explanation for explanation in result.explanations)


def test_level_three_candidate_needs_survival() -> None:
    result = classify_record(record_by_id("level_three_coble_diaz_candidate"))

    assert result.generator_status == "formal_candidate_survival_needed"
    assert any("Bockstein target" in explanation for explanation in result.explanations)


def test_odp_explanation_mentions_free_relation_or_vanishing_cycle() -> None:
    result = classify_record(record_by_id("threefold_ordinary_double_point_free_relation"))
    explanation = " ".join(result.explanations).lower()

    assert "free" in explanation
    assert "vanishing-cycle" in explanation


def test_e8_explanation_mentions_unimodular_or_trivial_discriminant() -> None:
    result = classify_record(record_by_id("e8_surface_unimodular_boundary"))
    explanation = " ".join(result.explanations).lower()

    assert "unimodular" in explanation or "trivial discriminant" in explanation


def test_coble_shadow_explanation_mentions_z4_to_z2_validation() -> None:
    result = classify_record(record_by_id("coble_one_four_shadow"))
    explanation = " ".join(result.explanations)

    assert "shadow" in explanation.lower()
    assert "Z/4 -> Z/2" in explanation
