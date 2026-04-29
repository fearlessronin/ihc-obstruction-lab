from ihc_lab.literature.keyword_hints import infer_channel_hints


def test_unramified_brauer_hints() -> None:
    hints = infer_channel_hints("Brauer comparison with unramified residue tests.")

    assert "brauer_unramified" in hints["proposed_channel_hints"]
    assert "residue_test" in hints["operation_hints"]
    assert "unramified_survival" in hints["operation_hints"]
    assert "brauer_nonzero" in hints["bottleneck_hints"]


def test_lattice_hints() -> None:
    hints = infer_channel_hints(
        "Fermat varieties with elementary divisors for the Hodge cycle lattice."
    )

    assert "lattice_saturation" in hints["proposed_channel_hints"]
    assert "computed_lattice_benchmark" in hints["proposed_channel_hints"]
    assert "elementary_divisor_comparison" in hints["operation_hints"]
    assert "lattice_identification" in hints["bottleneck_hints"]


def test_bockstein_cup_product_hints() -> None:
    hints = infer_channel_hints("A Bockstein image is formed from a cup product.")

    assert "cup_product_bockstein" in hints["proposed_channel_hints"]
    assert "bockstein" in hints["operation_hints"]
    assert "cup_product" in hints["operation_hints"]


def test_hints_are_deduplicated() -> None:
    hints = infer_channel_hints("unramified unramified Brauer Brauer")

    assert hints["proposed_channel_hints"].count("brauer_unramified") == 1
    assert hints["matched_keywords"].count("unramified") == 1
