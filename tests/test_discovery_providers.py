from __future__ import annotations

import pytest

from ihc_lab.literature.discovery_providers import (
    MockDiscoveryProvider,
    create_discovery_provider,
)
from ihc_lab.literature.discovery_queries import DiscoveryQuery


def _search_text(text: str):
    query = DiscoveryQuery(query_id="q", query_text=text)
    return MockDiscoveryProvider().search(query)


def test_mock_provider_returns_thematic_sources() -> None:
    assert "brauer_unramified" in _search_text("unramified Brauer")[0].intended_channel_hints
    assert "lattice_saturation" in _search_text("Fermat")[0].intended_channel_hints
    assert "matroidal_parity" in _search_text("matroid")[0].intended_channel_hints
    assert "stacky_stabilizer" in _search_text("stack stabilizer")[0].intended_channel_hints


@pytest.mark.parametrize("provider", ["openalex", "crossref", "arxiv"])
def test_network_providers_require_explicit_allow_network(provider: str) -> None:
    with pytest.raises(RuntimeError, match="Network discovery is disabled"):
        create_discovery_provider(provider, allow_network=False)


def test_create_mock_discovery_provider() -> None:
    assert isinstance(create_discovery_provider("mock"), MockDiscoveryProvider)
