"""Connection lifecycle manager for the high-level Dstar trade client."""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable, Mapping
from typing import Any

from .client import DstarTradeClient
from .config import DstarTradeConfig, PACKAGE_LOGGER_NAME, load_config_from_env, redact_text
from .errors import DstarConnectionError, DstarError, DstarTimeoutError


DstarClientFactory = Callable[..., DstarTradeClient]
logger = logging.getLogger(f"{PACKAGE_LOGGER_NAME}.connection_manager")


class DstarConnectionManager:
    """Manage ``DstarTradeClient`` connection, login, readiness, and reconnects.

    ``is_connected()`` intentionally means trade-ready: the client has connected,
    logged in, received ``api_ready``, and has not reported a disconnect.
    """

    def __init__(
        self,
        *,
        config: DstarTradeConfig | None = None,
        environ: Mapping[str, str] | None = None,
        client_factory: DstarClientFactory = DstarTradeClient,
        connect_timeout: float = 10,
        login_timeout: float = 30,
        ready_timeout: float = 30,
        reconnect_attempts: int = 2,
        reconnect_delay: float = 1,
    ) -> None:
        self.config = config or load_config_from_env(environ=environ, require_credentials=True)
        self._client_factory = client_factory
        self.connect_timeout = _validate_timeout("connect_timeout", connect_timeout)
        self.login_timeout = _validate_timeout("login_timeout", login_timeout)
        self.ready_timeout = _validate_timeout("ready_timeout", ready_timeout)
        self.reconnect_attempts = _validate_attempts(reconnect_attempts)
        self.reconnect_delay = _validate_delay(reconnect_delay)

        self._lock = threading.RLock()
        self._client: DstarTradeClient | None = None
        self._state = "closed"

    @property
    def client(self) -> DstarTradeClient | None:
        """Return the managed client, if created."""

        with self._lock:
            return self._client

    def connect(self, timeout: float | None = None) -> None:
        """Create/configure the Dstar client without waiting for API readiness."""

        _validate_timeout("timeout", self.connect_timeout if timeout is None else timeout)
        with self._lock:
            client = self._ensure_client()
            self._state = "connecting"
            try:
                client.connect()
            except DstarError:
                self._state = "failed"
                raise
            except Exception as exc:
                self._state = "failed"
                raise _wrap_connection_error(exc, "connect") from exc
            self._state = "connected"
            logger.info("Dstar client configured for %s:%s", self.config.trade_ip, self.config.trade_port)

    def login(self, timeout: float | None = None) -> None:
        """Login and wait for the login response callback."""

        login_timeout = self.login_timeout if timeout is None else _validate_timeout("timeout", timeout)
        with self._lock:
            client = self._require_client()
            if not client.connected:
                self.connect(timeout=self.connect_timeout)
            self._state = "logging_in"
            try:
                client.login()
                client.wait_login(timeout=login_timeout)
            except DstarError:
                self._state = "failed"
                raise
            except Exception as exc:
                self._state = "failed"
                raise _wrap_connection_error(exc, "login") from exc
            self._state = "logged_in"

    def wait_ready(self, timeout: float | None = None) -> None:
        """Wait for ``api_ready``; trading must not start before this returns."""

        ready_timeout = self.ready_timeout if timeout is None else _validate_timeout("timeout", timeout)
        with self._lock:
            client = self._require_client()
            self._state = "waiting_ready"
            try:
                client.wait_ready(timeout=ready_timeout)
            except DstarTimeoutError:
                self._state = "failed"
                raise
            except DstarError:
                self._state = "failed"
                raise
            except Exception as exc:
                self._state = "failed"
                raise _wrap_connection_error(exc, "wait_ready") from exc
            self._state = "ready"

    def close(self) -> None:
        """Close and release the managed Dstar client."""

        with self._lock:
            client = self._client
            self._client = None
            self._state = "closed"
        if client is not None:
            client.close()

    def is_connected(self) -> bool:
        """Return whether the managed client is connected, logged in, and ready."""

        with self._lock:
            client = self._client
            if client is None:
                return False
            return bool(
                client.connected
                and client.logged_in
                and client.api_ready
                and not client.disconnected
            )

    def reconnect(
        self,
        *,
        attempts: int | None = None,
        connect_timeout: float | None = None,
        login_timeout: float | None = None,
        ready_timeout: float | None = None,
    ) -> None:
        """Close the current client and run connect/login/wait_ready again."""

        total_attempts = self.reconnect_attempts if attempts is None else _validate_attempts(attempts)
        last_error: BaseException | None = None

        for attempt in range(1, total_attempts + 1):
            self.close()
            try:
                self.connect(timeout=connect_timeout or self.connect_timeout)
                self.login(timeout=login_timeout or self.login_timeout)
                self.wait_ready(timeout=ready_timeout or self.ready_timeout)
                logger.info("Dstar reconnect succeeded on attempt %s", attempt)
                return
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Dstar reconnect attempt %s/%s failed: %s",
                    attempt,
                    total_attempts,
                    redact_text(str(exc)),
                )
                if attempt < total_attempts and self.reconnect_delay > 0:
                    time.sleep(self.reconnect_delay)

        if isinstance(last_error, DstarError):
            raise DstarConnectionError(
                last_error.code,
                f"Reconnect failed after {total_attempts} attempt(s): {redact_text(last_error.message)}",
                "reconnect",
            ) from last_error
        raise DstarConnectionError(
            -1,
            f"Reconnect failed after {total_attempts} attempt(s)",
            "reconnect",
        ) from last_error

    def _ensure_client(self) -> DstarTradeClient:
        if self._client is None:
            self._client = self._client_factory(**self.config.to_client_kwargs())
        return self._client

    def _require_client(self) -> DstarTradeClient:
        client = self._client
        if client is None:
            raise DstarConnectionError(-1, "Dstar client has not been created", "connection")
        return client


def _validate_timeout(name: str, value: float) -> float:
    try:
        timeout = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if timeout <= 0:
        raise ValueError(f"{name} must be > 0")
    return timeout


def _validate_attempts(value: int) -> int:
    attempts = int(value)
    if attempts < 1:
        raise ValueError("reconnect_attempts must be >= 1")
    return attempts


def _validate_delay(value: float) -> float:
    delay = float(value)
    if delay < 0:
        raise ValueError("reconnect_delay must be >= 0")
    return delay


def _wrap_connection_error(exc: Exception, action: str) -> DstarConnectionError:
    return DstarConnectionError(-1, redact_text(str(exc)), action)


__all__ = ["DstarClientFactory", "DstarConnectionManager"]
