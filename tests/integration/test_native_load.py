"""Integration tests for loading the vendor library without connecting to a server."""

from __future__ import annotations

import dstar_trade_py


def test_package_imports() -> None:
    """Importing the public package should load the Linux native extension."""

    assert dstar_trade_py.IS_LINUX_BUILD is True


def test_get_api_version_returns_non_empty_string() -> None:
    """The vendor factory should provide a non-empty API version string."""

    version = dstar_trade_py.get_api_version()

    assert isinstance(version, str)
    assert version.strip()


def test_create_and_free_api_succeeds() -> None:
    """A vendor API instance should be created and released without a connection."""

    assert dstar_trade_py.create_and_free_api() is True
