import pytest

from ihc_lab.groups import FiniteAbelianGroup


def test_trivial_group_renders_as_zero() -> None:
    assert str(FiniteAbelianGroup([])) == "0"
    assert str(FiniteAbelianGroup([1])) == "0"


def test_single_factor_rendering() -> None:
    assert str(FiniteAbelianGroup([2])) == "Z/2Z"


def test_group_normalization_and_rendering() -> None:
    group = FiniteAbelianGroup([1, 4, 2])
    assert group.cyclic_factors == [2, 4]
    assert str(group) == "Z/2Z ⊕ Z/4Z"


def test_invalid_factors_raise() -> None:
    with pytest.raises(ValueError):
        FiniteAbelianGroup([0])
    with pytest.raises(ValueError):
        FiniteAbelianGroup([-2])


def test_group_order() -> None:
    assert FiniteAbelianGroup([2, 4]).order() == 8


def test_group_dict_roundtrip() -> None:
    group = FiniteAbelianGroup([1, 4, 2])
    assert FiniteAbelianGroup.from_dict(group.to_dict()) == group
