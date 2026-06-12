"""Tests for environment configuration and sensitive-data redaction."""

from __future__ import annotations

import io
import logging

import pytest

from dstar_trade_py.config import (
    DstarTradeConfig,
    SensitiveDataFilter,
    load_config_from_env,
    redact_sensitive,
    redact_text,
)


def test_config_loads_from_environment_mapping() -> None:
    """DSTAR_TRADE_* variables should map to client construction kwargs."""

    config = load_config_from_env(
        environ={
            "DSTAR_TRADE_IP": "127.0.0.1",
            "DSTAR_TRADE_PORT": "6668",
            "DSTAR_TRADE_USER": "demo-user",
            "DSTAR_TRADE_PASSWORD": "demo-password",
            "DSTAR_TRADE_AUTH_CODE": "demo-auth",
            "DSTAR_TRADE_APP_ID": "demo-app",
            "DSTAR_TRADE_LOG_PATH": "/tmp/dstar",
        },
        require_credentials=True,
    )

    assert config.trade_ip == "127.0.0.1"
    assert config.trade_port == 6668
    assert config.to_client_kwargs()["license_no"] == "demo-auth"
    assert config.to_client_kwargs()["api_log_path"] == "/tmp/dstar"


def test_config_reports_missing_required_environment() -> None:
    """Live configuration should fail clearly when required variables are absent."""

    with pytest.raises(RuntimeError, match="DSTAR_TRADE_PASSWORD"):
        load_config_from_env(
            environ={
                "DSTAR_TRADE_IP": "127.0.0.1",
                "DSTAR_TRADE_PORT": "6668",
                "DSTAR_TRADE_USER": "demo-user",
            },
            require_credentials=True,
        )


def test_redaction_covers_password_auth_code_and_app_id() -> None:
    """Sensitive config fields should not be returned in printable summaries."""

    redacted = redact_sensitive(
        {
            "password": "secret-password",
            "auth_code": "secret-auth",
            "app_id": "secret-app",
            "nested": {"UdpAuthCode": 123456},
        }
    )

    assert redacted["password"] == "<redacted>"
    assert redacted["auth_code"] == "<redacted>"
    assert redacted["app_id"] == "<redacted>"
    assert redacted["nested"]["UdpAuthCode"] == "<redacted>"


def test_redact_text_filters_log_messages() -> None:
    """Formatted log strings should not leak common secret key names."""

    message = redact_text(
        "password=secret auth_code='auth-secret' app_id=app-secret UdpAuthCode=123456"
    )

    assert "secret" not in message
    assert "123456" not in message
    assert message.count("<redacted>") == 4


def test_sensitive_data_filter_redacts_logging_records() -> None:
    """The logging filter should redact after %-style formatting."""

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(SensitiveDataFilter())
    logger = logging.getLogger("dstar_trade_py.test_config")
    logger.handlers[:] = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False

    logger.info("login password=%s app_id=%s", "secret-password", "secret-app")

    output = stream.getvalue()
    assert "secret-password" not in output
    assert "secret-app" not in output
    assert "<redacted>" in output


def test_config_summary_is_redacted() -> None:
    """DstarTradeConfig.to_redacted_dict should be safe for logs."""

    config = DstarTradeConfig(
        trade_ip="127.0.0.1",
        trade_port=6668,
        user="demo-user",
        password="secret-password",
        auth_code="secret-auth",
        app_id="secret-app",
    )

    redacted = config.to_redacted_dict()

    assert redacted["trade_ip"] == "127.0.0.1"
    assert redacted["password"] == "<redacted>"
    assert redacted["auth_code"] == "<redacted>"
    assert redacted["app_id"] == "<redacted>"
