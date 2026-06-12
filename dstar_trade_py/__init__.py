"""Public package surface for the minimal native Dstar API load checks."""

try:
    from ._dstar_trade_py import (
        IS_LINUX_BUILD,
        NativeTradeApi,
        SDK_PROTOCOL_VERSION,
        create_and_free_api,
        get_api_version,
    )
except ImportError as exc:
    # Add package-specific context to loader errors such as a missing vendor .so.
    raise ImportError(
        "Failed to load the dstar_trade_py Linux extension. Ensure the package was "
        "built on Linux and libdstartradeapi.so is installed in "
        "dstar_trade_py/.libs (or available through LD_LIBRARY_PATH)."
    ) from exc

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
from .async_client import AsyncDstarTradeClient

__all__ = [
    "IS_LINUX_BUILD",
    "AsyncDstarTradeClient",
    "CancelRequestBuilder",
    "DstarClientEvent",
    "DstarTradeClient",
    "NativeTradeApi",
    "OrderRequestBuilder",
    "SDK_PROTOCOL_VERSION",
    "DstarAuthError",
    "DstarConnectionError",
    "DstarError",
    "DstarErrorCode",
    "DstarNativeError",
    "DstarRequestError",
    "DstarTimeoutError",
    "DstarField",
    "ENUM_BY_CPP_TYPE",
    "STRUCT_MODELS",
    "create_and_free_api",
    "get_api_version",
    "get_error_message",
    "raise_for_error",
    "__version__",
]

# Keep the package version aligned with pyproject.toml during the skeleton phase.
__version__ = "0.1.0"
