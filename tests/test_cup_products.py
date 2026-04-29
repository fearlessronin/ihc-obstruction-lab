from ihc_lab.cup_products import CupProductCandidate
from ihc_lab.finite_coefficients import FiniteCoefficientInput


def finite_input(name: str, degree: int, twist: int) -> FiniteCoefficientInput:
    return FiniteCoefficientInput(
        class_name=name,
        variety_factor="S",
        cohomological_degree=degree,
        twist=twist,
        coefficient=2,
        source_type="test_source",
        theorem_status="test",
    )


def test_diaz_level_two_degree_twist_validity() -> None:
    candidate = CupProductCandidate(
        inputs=[finite_input("alpha", 1, 1), finite_input("beta", 2, 1)],
        target_codimension=2,
        coefficient=2,
    )

    assert candidate.total_degree() == 3
    assert candidate.total_twist() == 2
    assert candidate.is_degree_twist_valid()
    assert candidate.bockstein_target_string() == "H^4(-, Z(2))"
    assert candidate.finite_coefficient_source_string() == "H^3(-, Z/2(2))"


def test_level_three_degree_twist_validity() -> None:
    candidate = CupProductCandidate(
        inputs=[
            finite_input("alpha_1", 1, 1),
            finite_input("beta_2", 2, 1),
            finite_input("beta_3", 2, 1),
        ],
        target_codimension=3,
        coefficient=2,
    )

    assert candidate.total_degree() == 5
    assert candidate.total_twist() == 3
    assert candidate.is_degree_twist_valid()
    assert candidate.bockstein_target_string() == "H^6(-, Z(3))"


def test_invalid_degree_twist_candidate_fails() -> None:
    candidate = CupProductCandidate(
        inputs=[finite_input("alpha", 1, 1), finite_input("beta", 1, 1)],
        target_codimension=2,
        coefficient=2,
    )

    assert not candidate.is_degree_twist_valid()
