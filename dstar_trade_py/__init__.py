"""Public package surface for dstar_trade_py."""

from __future__ import annotations

import platform

try:
    from ._dstar_trade_py import (
        IS_LINUX_BUILD,
        NativeTradeApi,
        SDK_PROTOCOL_VERSION,
        create_and_free_api,
        get_api_version,
    )
except ImportError as exc:
    if platform.system() == "Linux":
        # Add package-specific context to loader errors such as a missing vendor .so.
        raise ImportError(
            "Failed to load the dstar_trade_py Linux extension. Ensure the package was "
            "built on Linux and libdstartradeapi.so is installed in "
            "dstar_trade_py/.libs (or available through LD_LIBRARY_PATH)."
        ) from exc

    _native_import_error = exc
    IS_LINUX_BUILD = False
    SDK_PROTOCOL_VERSION = 0

    def _raise_non_linux_runtime_error(*args, **kwargs):
        raise RuntimeError(
            "dstar_trade_py native trading APIs are only available on Linux. "
            "Importing the package is allowed on this platform for pure-Python helpers, "
            "but creating or loading the vendor NativeTradeApi is unsupported."
        ) from _native_import_error

    class NativeTradeApi:  # type: ignore[no-redef]
        """Non-Linux placeholder that fails clearly when instantiated."""

        def __init__(self) -> None:
            _raise_non_linux_runtime_error()

    create_and_free_api = _raise_non_linux_runtime_error
    get_api_version = _raise_non_linux_runtime_error

from .config import (
    DstarTradeConfig,
    SensitiveDataFilter,
    configure_logging,
    load_config_from_env,
    redact_sensitive,
    redact_text,
)

from .errors import (
    DstarAuthError,
    DstarConnectionError,
    DstarError,
    DstarErrorCode,
    DstarNativeError,
    DstarRequestError,
    DstarTimeoutError,
    get_error_message,
    raise_for_error,
)
from .enums import ENUM_BY_CPP_TYPE
from .fields import STRUCT_MODELS, DstarField
from .client import CancelRequestBuilder, DstarClientEvent, DstarTradeClient, OrderRequestBuilder
from .connection_manager import DstarConnectionManager
from .async_client import AsyncDstarTradeClient
from .order_management import (
    ManagedOrderState,
    OrderJournal,
    OrderStateManager,
    RequestIdManager,
)
from .order_mapper import (
    DstarMappedOrder,
    DstarOrderLifecycle,
    DstarOrderLifecycleStatus,
    DstarOrderMapper,
)
from .event_adapter import (
    DstarCallbackEnvelope,
    DstarEventAdapter,
    DstarNautilusEvent,
    DstarNautilusEventType,
)
from .recovery_engine import DstarRecoveryEngine, DstarRecoveryResult

__all__ = [
    "IS_LINUX_BUILD",
    "AsyncDstarTradeClient",
    "CancelRequestBuilder",
    "DstarClientEvent",
    "DstarTradeConfig",
    "DstarTradeClient",
    "NativeTradeApi",
    "OrderRequestBuilder",
    "SDK_PROTOCOL_VERSION",
    "SensitiveDataFilter",
    "DstarAuthError",
    "DstarConnectionError",
    "DstarConnectionManager",
    "DstarError",
    "DstarErrorCode",
    "DstarCallbackEnvelope",
    "DstarEventAdapter",
    "DstarNativeError",
    "DstarNautilusEvent",
    "DstarNautilusEventType",
    "DstarRequestError",
    "DstarTimeoutError",
    "DstarField",
    "DstarMappedOrder",
    "DstarOrderLifecycle",
    "DstarOrderLifecycleStatus",
    "DstarOrderMapper",
    "DstarRecoveryEngine",
    "DstarRecoveryResult",
    "ENUM_BY_CPP_TYPE",
    "ManagedOrderState",
    "OrderJournal",
    "OrderStateManager",
    "RequestIdManager",
    "STRUCT_MODELS",
    "create_and_free_api",
    "configure_logging",
    "get_api_version",
    "get_error_message",
    "load_config_from_env",
    "redact_sensitive",
    "redact_text",
    "raise_for_error",
    "__version__",
]

# Keep the package version aligned with pyproject.toml during the skeleton phase.
__version__ = "0.1.0"
