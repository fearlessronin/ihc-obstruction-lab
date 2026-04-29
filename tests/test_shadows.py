from ihc_lab.groups import FiniteAbelianGroup
from ihc_lab.shadows import ShadowSelector


def test_z4_order_two_shadow_validates() -> None:
    selector = ShadowSelector(
        source_group=FiniteAbelianGroup([4]),
        selected_group=FiniteAbelianGroup([2]),
        selection_type="order_two_shadow",
        coefficient=2,
    )

    assert selector.validate_z4_order_two_shadow()


def test_z4_shadow_rejects_wrong_coefficient() -> None:
    selector = ShadowSelector(
        source_group=FiniteAbelianGroup([4]),
        selected_group=FiniteAbelianGroup([2]),
        selection_type="order_two_shadow",
        coefficient=3,
    )

    assert not selector.validate_z4_order_two_shadow()
