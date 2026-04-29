"""Deterministic keyword hints for local literature excerpts."""

from __future__ import annotations


def _append_unique(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


def _contains(text_lower: str, phrase: str) -> bool:
    return phrase.lower() in text_lower


def infer_channel_hints(text: str) -> dict[str, list[str]]:
    text_lower = text.lower()
    channel_hints: list[str] = []
    operation_hints: list[str] = []
    bottleneck_hints: list[str] = []
    matched_keywords: list[str] = []

    def match(keyword: str) -> bool:
        if _contains(text_lower, keyword):
            _append_unique(matched_keywords, keyword)
            return True
        return False

    has_unramified = match("unramified")
    has_residue = match("residue")
    if has_unramified or has_residue:
        _append_unique(channel_hints, "brauer_unramified")
        if has_residue:
            _append_unique(operation_hints, "residue_test")
        if has_unramified:
            _append_unique(operation_hints, "unramified_survival")
        _append_unique(bottleneck_hints, "verify_survival_statement")

    if match("Brauer"):
        _append_unique(channel_hints, "brauer_unramified")
        _append_unique(bottleneck_hints, "brauer_nonzero")

    if match("Bockstein"):
        _append_unique(channel_hints, "cup_product_bockstein")
        _append_unique(operation_hints, "bockstein")

    if match("cup product"):
        _append_unique(operation_hints, "cup_product")

    lattice_terms = [
        "Smith normal form",
        "elementary divisors",
        "lattice of Hodge cycles",
        "Hodge cycle lattice",
        "lattice",
    ]
    lattice_matches = [term for term in lattice_terms if match(term)]
    if lattice_matches:
        _append_unique(channel_hints, "lattice_saturation")
        if any(term in lattice_matches for term in ["Smith normal form", "lattice"]):
            _append_unique(operation_hints, "smith_normal_form")
        if "elementary divisors" in lattice_matches:
            _append_unique(operation_hints, "elementary_divisor_comparison")
        _append_unique(bottleneck_hints, "lattice_identification")

    if match("Enriques"):
        _append_unique(channel_hints, "enriques_product")

    if match("matroid"):
        _append_unique(channel_hints, "matroidal_parity")

    has_odp = match("ordinary double point")
    has_nodal = match("nodal")
    if has_odp or has_nodal:
        _append_unique(channel_hints, "nodal_free_relation")
        _append_unique(operation_hints, "global_relation")

    has_stack = match("quotient stack")
    has_stabilizer = match("stabilizer")
    has_bg = match("BG")
    if has_stack or has_stabilizer or has_bg:
        _append_unique(channel_hints, "stacky_stabilizer")
        _append_unique(bottleneck_hints, "stacky_realization")

    if match("Fermat"):
        _append_unique(channel_hints, "computed_lattice_benchmark")

    return {
        "proposed_channel_hints": channel_hints,
        "operation_hints": operation_hints,
        "bottleneck_hints": bottleneck_hints,
        "matched_keywords": matched_keywords,
    }
