"""Live login test for the Dstar test environment."""

from __future__ import annotations

from dstar_trade_py import DstarTradeClient


def test_live_login_and_wait_ready(ready_live_client: DstarTradeClient) -> None:
    """Login should complete and api_ready must be observed before trading calls."""

    assert ready_live_client.initialized is True
    assert ready_live_client.connected is True
    assert ready_live_client.api_ready is True
    assert ready_live_client.disconnected is False
