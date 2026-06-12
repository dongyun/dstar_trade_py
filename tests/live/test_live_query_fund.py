"""Live fund-query test.

This test connects to the Dstar test environment and performs only a read-only
fund query. It never submits orders.
"""

from __future__ import annotations

from dstar_trade_py import DstarTradeClient
from dstar_trade_py.fields import DstarApiFundField


def test_live_query_fund(ready_live_client: DstarTradeClient) -> None:
    """A live read-only fund query should return a fund dataclass."""

    fund = ready_live_client.query_fund(timeout=10)

    assert isinstance(fund, DstarApiFundField)
    assert isinstance(fund.AccountNo, str)
