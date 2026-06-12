"""Live position-query test.

This test connects to the Dstar test environment and performs only a read-only
position query. It never submits orders.
"""

from __future__ import annotations

from dstar_trade_py import DstarTradeClient
from dstar_trade_py.fields import DstarApiPositionField


def test_live_query_position(ready_live_client: DstarTradeClient) -> None:
    """A live read-only position query should return a list of position dataclasses."""

    positions = ready_live_client.query_position(timeout=10)

    assert isinstance(positions, list)
    for position in positions:
        assert isinstance(position, DstarApiPositionField)
        assert isinstance(position.ContractNo, str)
