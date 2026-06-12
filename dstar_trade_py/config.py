"""Configuration, logging, and redaction helpers for dstar_trade_py."""

from __future__ import annotations

import logging
import os
import re
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Mapping


PACKAGE_LOGGER_NAME = "dstar_trade_py"
DEFAULT_NATIVE_LOG_PATH = "logs/native"

ENV_TRADE_IP = "DSTAR_TRADE_IP"
ENV_TRADE_PORT = "DSTAR_TRADE_PORT"
ENV_TRADE_USER = "DSTAR_TRADE_USER"
ENV_TRADE_PASSWORD = "DSTAR_TRADE_PASSWORD"
ENV_TRADE_AUTH_CODE = "DSTAR_TRADE_AUTH_CODE"
ENV_TRADE_APP_ID = "DSTAR_TRADE_APP_ID"
ENV_TRADE_LOG_PATH = "DSTAR_TRADE_LOG_PATH"
ENV_LOG_LEVEL = "DSTAR_TRADE_LOG_LEVEL"

REQUIRED_TRADE_ENV_VARS = (
    ENV_TRADE_IP,
    ENV_TRADE_PORT,
    ENV_TRADE_USER,
    ENV_TRADE_PASSWORD,
    ENV_TRADE_AUTH_CODE,
    ENV_TRADE_APP_ID,
)

_SENSITIVE_KEY_PARTS = {
    "password",
    "passwd",
    "auth_code",
    "authcode",
    "auth",
    "app_id",
    "appid",
    "license",
    "secret",
    "token",
}
_SENSITIVE_TEXT_RE = re.compile(
    r"(?P<key>[A-Za-z_]*(?:password|passwd|auth|app_id|appid|license|secret|token)[A-Za-z_]*)"
    r"(?P<sep>\s*[:=]\s*)"
    r"(?P<quote>['\"]?)"
    r"(?P<value>[^,'\"\s}\]]+)"
    r"(?P=quote)",
    re.IGNORECASE,
)


def is_sensitive_key(key: object) -> bool:
    """Return whether a config/log field name should be redacted."""

    text = str(key).casefold()
    return any(part in text for part in _SENSITIVE_KEY_PARTS)


def redact_secret(value: Any) -> str:
    """Return a fixed replacement for sensitive values.

    使用固定字符串而不是保留长度，避免日志通过长度泄露账号侧配置细节。
    """

    if value in (None, ""):
        return ""
    return "<redacted>"


def redact_sensitive(value: Any) -> Any:
    """Recursively redact sensitive fields from dataclasses and mappings."""

    if is_dataclass(value):
        return redact_sensitive(asdict(value))
    if isinstance(value, Mapping):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            redacted[text_key] = redact_secret(item) if is_sensitive_key(text_key) else redact_sensitive(item)
        return redacted
    if isinstance(value, list | tuple):
        return [redact_sensitive(item) for item in value]
    return value


def redact_text(message: str) -> str:
    """Redact sensitive key-value pairs from a formatted log message."""

    def replace(match: re.Match[str]) -> str:
        quote = match.group("quote")
        return f"{match.group('key')}{match.group('sep')}{quote}<redacted>{quote}"

    return _SENSITIVE_TEXT_RE.sub(replace, message)


class SensitiveDataFilter(logging.Filter):
    """Logging filter that removes passwords, auth codes, and app IDs."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rendered = record.getMessage()
        except Exception:
            rendered = str(record.msg)
        record.msg = redact_text(rendered)
        record.args = ()
        return True


def configure_logging(level: int | str | None = None) -> logging.Logger:
    """Configure the package logger with a stream handler and redaction filter."""

    configured_level = level if level is not None else os.environ.get(ENV_LOG_LEVEL, "INFO")
    logger = logging.getLogger(PACKAGE_LOGGER_NAME)
    logger.setLevel(configured_level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)

    for handler in logger.handlers:
        if not any(isinstance(item, SensitiveDataFilter) for item in handler.filters):
            handler.addFilter(SensitiveDataFilter())
    return logger


@dataclass(slots=True)
class DstarTradeConfig:
    """Runtime configuration loaded from environment variables."""

    trade_ip: str = ""
    trade_port: int = 0
    user: str = ""
    password: str = ""
    auth_code: str = ""
    app_id: str = ""
    log_path: str = DEFAULT_NATIVE_LOG_PATH

    @classmethod
    def from_env(
        cls,
        *,
        environ: Mapping[str, str] | None = None,
        require_credentials: bool = False,
    ) -> "DstarTradeConfig":
        """Load configuration from ``DSTAR_TRADE_*`` environment variables."""

        source = os.environ if environ is None else environ
        missing = [name for name in REQUIRED_TRADE_ENV_VARS if not source.get(name)]
        if require_credentials and missing:
            joined = ", ".join(missing)
            raise RuntimeError(
                "Missing required Dstar trade environment variables: "
                f"{joined}. Configure them before connecting to a live trade front."
            )

        port_value = source.get(ENV_TRADE_PORT, "0") or "0"
        try:
            trade_port = int(port_value)
        except ValueError as exc:
            raise RuntimeError(f"{ENV_TRADE_PORT} must be an integer") from exc

        return cls(
            trade_ip=source.get(ENV_TRADE_IP, ""),
            trade_port=trade_port,
            user=source.get(ENV_TRADE_USER, ""),
            password=source.get(ENV_TRADE_PASSWORD, ""),
            auth_code=source.get(ENV_TRADE_AUTH_CODE, ""),
            app_id=source.get(ENV_TRADE_APP_ID, ""),
            log_path=source.get(ENV_TRADE_LOG_PATH, DEFAULT_NATIVE_LOG_PATH)
            or DEFAULT_NATIVE_LOG_PATH,
        )

    def ensure_native_log_path(self) -> Path:
        """Create and return the vendor SDK native log directory."""

        path = Path(self.log_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def to_client_kwargs(self) -> dict[str, Any]:
        """Return keyword arguments accepted by ``DstarTradeClient``."""

        return {
            "front_ip": self.trade_ip,
            "front_port": self.trade_port,
            "account_no": self.user,
            "password": self.password,
            "app_id": self.app_id,
            "license_no": self.auth_code,
            "api_log_path": self.log_path,
        }

    def to_redacted_dict(self) -> dict[str, Any]:
        """Return a dict safe to write to logs or demo console output."""

        return redact_sensitive(self)


def load_config_from_env(
    *,
    environ: Mapping[str, str] | None = None,
    require_credentials: bool = False,
) -> DstarTradeConfig:
    """Convenience wrapper around ``DstarTradeConfig.from_env``."""

    return DstarTradeConfig.from_env(environ=environ, require_credentials=require_credentials)


def log_config_summary(
    logger: logging.Logger,
    config: DstarTradeConfig,
    *,
    level: int = logging.INFO,
) -> None:
    """Log a redacted config summary."""

    logger.log(level, "Dstar trade config: %s", config.to_redacted_dict())


__all__ = [
    "DEFAULT_NATIVE_LOG_PATH",
    "DstarTradeConfig",
    "ENV_LOG_LEVEL",
    "ENV_TRADE_APP_ID",
    "ENV_TRADE_AUTH_CODE",
    "ENV_TRADE_IP",
    "ENV_TRADE_LOG_PATH",
    "ENV_TRADE_PASSWORD",
    "ENV_TRADE_PORT",
    "ENV_TRADE_USER",
    "PACKAGE_LOGGER_NAME",
    "REQUIRED_TRADE_ENV_VARS",
    "SensitiveDataFilter",
    "configure_logging",
    "is_sensitive_key",
    "load_config_from_env",
    "log_config_summary",
    "redact_secret",
    "redact_sensitive",
    "redact_text",
]
