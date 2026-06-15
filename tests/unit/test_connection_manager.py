"""Unit tests for DstarConnectionManager using mock clients only."""

from __future__ import annotations

import logging

import pytest

from dstar_trade_py.connection_manager import DstarConnectionManager
from dstar_trade_py.errors import DstarAuthError, DstarTimeoutError


ENV = {
    "DSTAR_TRADE_IP": "127.0.0.1",
    "DSTAR_TRADE_PORT": "6668",
    "DSTAR_TRADE_USER": "demo-user",
    "DSTAR_TRADE_PASSWORD": "secret-password",
    "DSTAR_TRADE_AUTH_CODE": "secret-auth",
    "DSTAR_TRADE_APP_ID": "secret-app",
}


class FakeDstarTradeClient:
    """Small mock matching the DstarTradeClient lifecycle surface."""

    def __init__(
        self,
        *,
        front_ip: str,
        front_port: int,
        account_no: str,
        password: str,
        app_id: str,
        license_no: str,
        api_log_path: str = "",
        fail_login: bool = False,
        fail_ready: bool = False,
        leak_secret_error: bool = False,
    ) -> None:
        self.kwargs = {
            "front_ip": front_ip,
            "front_port": front_port,
            "account_no": account_no,
            "password": password,
            "app_id": app_id,
            "license_no": license_no,
            "api_log_path": api_log_path,
        }
        self.fail_login = fail_login
        self.fail_ready = fail_ready
        self.leak_secret_error = leak_secret_error
        self.calls: list[tuple[str, float | None]] = []
        self.connected = False
        self.logged_in = False
        self.api_ready = False
        self.disconnected = False
        self.closed = False

    def connect(self) -> None:
        self.calls.append(("connect", None))
        if self.leak_secret_error:
            raise RuntimeError("password=secret-password auth_code=secret-auth")
        self.connected = True
        self.disconnected = False

    def login(self) -> None:
        self.calls.append(("login", None))

    def wait_login(self, timeout: float = 30) -> None:
        self.calls.append(("wait_login", timeout))
        if self.fail_login:
            raise DstarAuthError(20003, "Incorrect password", "login")
        self.logged_in = True

    def wait_ready(self, timeout: float = 30) -> None:
        self.calls.append(("wait_ready", timeout))
        if self.fail_ready:
            raise DstarTimeoutError(-1, "Timed out waiting for API ready", "wait_ready")
        self.api_ready = True

    def close(self) -> None:
        self.calls.append(("close", None))
        self.connected = False
        self.logged_in = False
        self.api_ready = False
        self.disconnected = True
        self.closed = True


def test_manager_loads_environment_and_reaches_ready_state() -> None:
    """connect/login/wait_ready should create a ready client from env config."""

    created: list[FakeDstarTradeClient] = []

    def factory(**kwargs) -> FakeDstarTradeClient:
        client = FakeDstarTradeClient(**kwargs)
        created.append(client)
        return client

    manager = DstarConnectionManager(
        environ=ENV,
        client_factory=factory,
        login_timeout=3,
        ready_timeout=4,
    )

    manager.connect()
    manager.login()
    manager.wait_ready()

    assert manager.is_connected() is True
    assert created[0].kwargs["front_ip"] == "127.0.0.1"
    assert created[0].kwargs["front_port"] == 6668
    assert created[0].kwargs["account_no"] == "demo-user"
    assert created[0].kwargs["password"] == "secret-password"
    assert created[0].kwargs["license_no"] == "secret-auth"
    assert ("wait_login", 3.0) in created[0].calls
    assert ("wait_ready", 4.0) in created[0].calls


def test_manager_reports_login_failure_without_ready_state() -> None:
    """A login callback failure should stop before trading readiness."""

    manager = DstarConnectionManager(
        environ=ENV,
        client_factory=lambda **kwargs: FakeDstarTradeClient(**kwargs, fail_login=True),
    )

    manager.connect()

    with pytest.raises(DstarAuthError, match="login failed"):
        manager.login(timeout=0.1)

    assert manager.is_connected() is False


def test_manager_reports_wait_ready_timeout() -> None:
    """API ready timeout must keep the manager out of trade-ready state."""

    manager = DstarConnectionManager(
        environ=ENV,
        client_factory=lambda **kwargs: FakeDstarTradeClient(**kwargs, fail_ready=True),
    )

    manager.connect()
    manager.login()

    with pytest.raises(DstarTimeoutError, match="wait_ready failed"):
        manager.wait_ready(timeout=0.1)

    assert manager.is_connected() is False


def test_reconnect_recreates_client_after_failed_attempt() -> None:
    """Basic reconnect should close a failed client and create a fresh one."""

    created: list[FakeDstarTradeClient] = []

    def factory(**kwargs) -> FakeDstarTradeClient:
        client = FakeDstarTradeClient(**kwargs, fail_ready=len(created) == 0)
        created.append(client)
        return client

    manager = DstarConnectionManager(
        environ=ENV,
        client_factory=factory,
        reconnect_attempts=2,
        reconnect_delay=0,
    )

    manager.reconnect()

    assert len(created) == 2
    assert created[0].closed is True
    assert created[1].api_ready is True
    assert manager.is_connected() is True


def test_manager_redacts_secret_values_from_wrapped_errors(caplog: pytest.LogCaptureFixture) -> None:
    """Wrapped errors and reconnect logs must not leak password or auth values."""

    manager = DstarConnectionManager(
        environ=ENV,
        client_factory=lambda **kwargs: FakeDstarTradeClient(**kwargs, leak_secret_error=True),
        reconnect_attempts=1,
        reconnect_delay=0,
    )

    with caplog.at_level(logging.WARNING, logger="dstar_trade_py.connection_manager"):
        with pytest.raises(Exception) as exc_info:
            manager.reconnect()

    rendered_logs = "\n".join(record.getMessage() for record in caplog.records)
    combined = rendered_logs + "\n" + str(exc_info.value)
    assert "secret-password" not in combined
    assert "secret-auth" not in combined
    assert "<redacted>" in combined


def test_close_releases_managed_client() -> None:
    """close should delegate to the client and make is_connected false."""

    created: list[FakeDstarTradeClient] = []

    def factory(**kwargs) -> FakeDstarTradeClient:
        client = FakeDstarTradeClient(**kwargs)
        created.append(client)
        return client

    manager = DstarConnectionManager(environ=ENV, client_factory=factory)
    manager.connect()
    manager.login()
    manager.wait_ready()

    manager.close()

    assert created[0].closed is True
    assert manager.client is None
    assert manager.is_connected() is False
