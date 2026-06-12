"""Public package surface for the minimal native Dstar API load checks."""

try:
    from ._dstar_trade_py import (
        IS_LINUX_BUILD,
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

__all__ = [
    "IS_LINUX_BUILD",
    "SDK_PROTOCOL_VERSION",
    "create_and_free_api",
    "get_api_version",
    "__version__",
]

# Keep the package version aligned with pyproject.toml during the skeleton phase.
__version__ = "0.1.0"
