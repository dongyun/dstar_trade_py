"""Smoke tests for the package and its native extension."""

import dstar_trade_py


def test_native_extension_imports() -> None:
    """The extension should report a Linux build and the vendor protocol version."""
    assert dstar_trade_py.IS_LINUX_BUILD is True
    assert dstar_trade_py.SDK_PROTOCOL_VERSION == 3

