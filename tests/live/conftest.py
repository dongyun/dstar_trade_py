"""Fixtures for live Dstar tests.

Live tests are intentionally opt-in. They connect to the Dstar test environment
only when ``DSTAR_RUN_LIVE_TESTS=1`` and every required credential environment
variable is present.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from dstar_trade_py import DstarTradeClient


REQUIRED_LIVE_ENV = (
    "DSTAR_TRADE_IP",
    "DSTAR_TRADE_PORT",
    "DSTAR_TRADE_USER",
    "DSTAR_TRADE_PASSWORD",
    "DSTAR_TRADE_AUTH_CODE",
    "DSTAR_TRADE_APP_ID",
    "DSTAR_TRADE_LOG_PATH",
)


@pytest.fixture(scope="session")
def live_config() -> dict[str, str | int]:
    """Return live configuration or skip with a clear reason."""

    if os.environ.get("DSTAR_RUN_LIVE_TESTS") != "1":
        pytest.skip("live tests require DSTAR_RUN_LIVE_TESTS=1")

    missing = [name for name in REQUIRED_LIVE_ENV if not os.environ.get(name)]
    if missing:
        pytest.skip("missing live test environment variables: " + ", ".join(missing))

    try:
        port = int(os.environ["DSTAR_TRADE_PORT"])
    except ValueError:
        pytest.skip("DSTAR_TRADE_PORT must be an integer")

    return {
        "ip": os.environ["DSTAR_TRADE_IP"],
        "port": port,
        "user": os.environ["DSTAR_TRADE_USER"],
        "password": os.environ["DSTAR_TRADE_PASSWORD"],
        "auth_code": os.environ["DSTAR_TRADE_AUTH_CODE"],
        "app_id": os.environ["DSTAR_TRADE_APP_ID"],
        "log_path": os.environ["DSTAR_TRADE_LOG_PATH"],
    }


@pytest.fixture()
def live_client(live_config: dict[str, str | int]) -> Iterator[DstarTradeClient]:
    """Create a configured live client and release it after each test."""

    client = DstarTradeClient(
        front_ip=str(live_config["ip"]),
        front_port=int(live_config["port"]),
        account_no=str(live_config["user"]),
        password=str(live_config["password"]),
        app_id=str(live_config["app_id"]),
        license_no=str(live_config["auth_code"]),
        api_log_path=str(live_config["log_path"]),
    )
    try:
        yield client
    finally:
        client.close()


@pytest.fixture()
def ready_live_client(live_client: DstarTradeClient) -> DstarTradeClient:
    """Connect, login, and wait for api_ready before returning the client."""

    live_client.connect()
    live_client.login()
    live_client.wait_ready(timeout=30)
    return live_client
