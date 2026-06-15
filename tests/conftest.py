"""Shared pytest configuration for dstar_trade_py.

Markers are assigned from file location so new tests automatically land in the
correct class:

- ``tests/live`` -> live
- ``tests/integration`` -> integration
- ``tests/mock_sdk`` -> mock_sdk
- all other tests -> unit
"""

from __future__ import annotations

from pathlib import Path

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Apply test-category markers consistently across the suite."""

    for item in items:
        path = Path(str(item.fspath))
        parts = set(path.parts)
        if "live" in parts:
            item.add_marker(pytest.mark.live)
        elif "integration" in parts:
            item.add_marker(pytest.mark.integration)
        elif "mock_sdk" in parts:
            item.add_marker(pytest.mark.mock_sdk)
        else:
            item.add_marker(pytest.mark.unit)
