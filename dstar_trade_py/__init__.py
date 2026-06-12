"""Public package surface for the initial dstar_trade_py project skeleton."""

from ._dstar_trade_py import IS_LINUX_BUILD, SDK_PROTOCOL_VERSION

__all__ = ["IS_LINUX_BUILD", "SDK_PROTOCOL_VERSION", "__version__"]

# Keep the package version aligned with pyproject.toml during the skeleton phase.
__version__ = "0.1.0"

