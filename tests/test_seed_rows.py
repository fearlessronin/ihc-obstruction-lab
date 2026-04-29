from ihc_lab.datasets import dataset_summary, load_seed_rows
from ihc_lab.enums import ChannelLabel
from ihc_lab.reports import cup_product_validation_report


def test_loading_seed_rows_succeeds() -> None:
    records = load_seed_rows()
    assert len(records) >= 10


def test_dataset_summary_has_expected_count() -> None:
    records = load_seed_rows()
    summary = dataset_summary(records)

    assert summary["total"] >= 10
    assert summary["by_channel"]["local_discriminant"] >= 4


def test_odp_row_is_nodal_free_relation_not_local_discriminant() -> None:
    records = load_seed_rows()
    odp = next(row for row in records if row.id == "threefold_ordinary_double_point_free_relation")

    assert ChannelLabel.nodal_free_relation in odp.channel_labels
    assert ChannelLabel.local_discriminant not in odp.channel_labels


def test_seed_rows_have_no_validation_warnings() -> None:
    records = load_seed_rows()
    summary = dataset_summary(records)

    assert summary["warnings"] == []


def test_coble_seed_shadow_is_order_two_z4_shadow() -> None:
    records = load_seed_rows()
    coble = next(row for row in records if row.id == "coble_one_four_shadow")

    assert coble.shadow_selector is not None
    assert coble.shadow_selector.validate_z4_order_two_shadow()


def test_cup_product_validation_report_mentions_seed_candidates() -> None:
    records = load_seed_rows()
    report = cup_product_validation_report(records)

    assert "diaz_level_two" in report
    assert "level_three_coble_diaz_candidate" in report
    assert "Candidate rows checked: 2" in report
