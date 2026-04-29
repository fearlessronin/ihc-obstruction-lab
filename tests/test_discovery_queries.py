from __future__ import annotations

import pytest

from ihc_lab.literature.discovery_queries import (
    DiscoveryQuery,
    load_discovery_queries,
)


def test_load_sample_discovery_queries() -> None:
    queries = load_discovery_queries(
        "data/literature_queue/discovery/discovery_queries.sample.json"
    )

    assert len(queries) >= 8
    assert {query.provider for query in queries} == {"mock"}


def test_discovery_query_round_trip() -> None:
    query = DiscoveryQuery(
        query_id="q",
        query_text="integral Hodge conjecture Brauer",
        intended_channel_hints=["brauer_unramified"],
    )

    assert DiscoveryQuery.from_dict(query.to_dict()) == query


def test_discovery_query_max_results_validation() -> None:
    with pytest.raises(ValueError, match="max_results"):
        DiscoveryQuery(query_id="bad", query_text="bad", max_results=0)
