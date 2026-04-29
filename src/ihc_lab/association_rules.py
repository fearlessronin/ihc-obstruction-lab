"""Pure-Python association-rule mining for binary obstruction features."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

from ihc_lab.features import FeatureValue


@dataclass(frozen=True)
class AssociationRule:
    antecedent: tuple[str, ...]
    consequent: str
    support_count: int
    support: float
    confidence: float
    lift: float


def transactions_from_feature_matrix(
    feature_matrix: Iterable[dict[str, FeatureValue]],
) -> list[set[str]]:
    transactions: list[set[str]] = []
    for row in feature_matrix:
        transactions.append({name for name, value in row.items() if value is True})
    return transactions


def mine_association_rules(
    transactions: list[set[str]],
    max_antecedent_size: int = 2,
    min_support_count: int = 1,
    min_confidence: float = 0.8,
    consequent_prefixes: tuple[str, ...] = ("channel_", "status_", "bottleneck_"),
) -> list[AssociationRule]:
    if not transactions:
        return []

    item_universe = sorted(set().union(*transactions))
    consequent_items = [
        item for item in item_universe if item.startswith(consequent_prefixes)
    ]
    transaction_count = len(transactions)
    rules: list[AssociationRule] = []

    for consequent in consequent_items:
        consequent_count = sum(1 for transaction in transactions if consequent in transaction)
        if consequent_count == 0:
            continue
        consequent_probability = consequent_count / transaction_count

        antecedent_universe = [item for item in item_universe if item != consequent]
        for size in range(1, max_antecedent_size + 1):
            for antecedent in combinations(antecedent_universe, size):
                antecedent_set = set(antecedent)
                antecedent_count = sum(
                    1 for transaction in transactions if antecedent_set <= transaction
                )
                if antecedent_count == 0:
                    continue

                combined_count = sum(
                    1
                    for transaction in transactions
                    if antecedent_set <= transaction and consequent in transaction
                )
                if combined_count < min_support_count:
                    continue

                confidence = combined_count / antecedent_count
                if confidence < min_confidence:
                    continue

                support = combined_count / transaction_count
                lift = confidence / consequent_probability if consequent_probability else 0.0
                rules.append(
                    AssociationRule(
                        antecedent=tuple(sorted(antecedent)),
                        consequent=consequent,
                        support_count=combined_count,
                        support=support,
                        confidence=confidence,
                        lift=lift,
                    )
                )

    return sorted(
        rules,
        key=lambda rule: (
            -rule.confidence,
            -rule.support_count,
            -rule.lift,
            rule.antecedent,
            rule.consequent,
        ),
    )


def rule_to_text(rule: AssociationRule) -> str:
    antecedent = " and ".join(rule.antecedent)
    return (
        f"{antecedent} -> {rule.consequent} "
        f"(support={rule.support_count}, confidence={rule.confidence:.2f}, "
        f"lift={rule.lift:.2f})"
    )


def filter_interesting_rules(rules: list[AssociationRule]) -> list[AssociationRule]:
    preferred_prefixes = (
        "has_",
        "local_",
        "cup_product_",
        "valid_",
        "op_",
        "trust_",
        "computability_",
    )
    interesting: list[AssociationRule] = []

    for rule in rules:
        if rule.consequent in rule.antecedent:
            continue
        if any(
            item.startswith(("channel_", "status_", "bottleneck_"))
            for item in rule.antecedent
        ):
            continue
        if not any(item.startswith(preferred_prefixes) for item in rule.antecedent):
            continue
        interesting.append(rule)

    interesting = sorted(
        interesting,
        key=lambda rule: (
            -rule.confidence,
            -rule.support_count,
            -rule.lift,
            rule.antecedent,
            rule.consequent,
        ),
    )
    return interesting[:20]
