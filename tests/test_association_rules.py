from ihc_lab.association_rules import (
    filter_interesting_rules,
    mine_association_rules,
    transactions_from_feature_matrix,
)
from ihc_lab.datasets import load_seed_rows
from ihc_lab.features import extract_feature_matrix
from ihc_lab.reports import (
    association_rules_latex,
    association_rules_markdown,
    feature_matrix_markdown,
)


def test_association_rule_mining_returns_interpretable_rules() -> None:
    matrix = extract_feature_matrix(load_seed_rows())
    transactions = transactions_from_feature_matrix(matrix)
    rules = mine_association_rules(transactions)
    filtered = filter_interesting_rules(rules)

    assert rules
    assert isinstance(filtered, list)
    assert any(
        rule.consequent
        in {
            "channel_cup_product_bockstein",
            "bottleneck_unramified_nonvanishing",
            "channel_nodal_free_relation",
        }
        for rule in filtered
    )
    assert all(0 <= rule.confidence <= 1 for rule in rules)
    assert all(rule.lift >= 0 for rule in rules)


def test_feature_and_association_reports_render() -> None:
    records = load_seed_rows()

    assert "# Association Rules" in association_rules_markdown(records)
    assert "# Feature Matrix Summary" in feature_matrix_markdown(records)
    assert r"\begin{table}" in association_rules_latex(records)
