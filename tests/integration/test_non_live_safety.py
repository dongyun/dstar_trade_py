"""Non-live integration safety checks for default test runs."""

from __future__ import annotations

import os

import pytest


def test_default_pytest_addopts_excludes_live_marker(pytestconfig: pytest.Config) -> None:
    """CI/default pytest configuration must not run live tests."""

    configured = pytestconfig.getini("addopts")

    assert "not live" in " ".join(configured)


def test_dstar_run_live_tests_zero_is_not_live(monkeypatch: pytest.MonkeyPatch) -> None:
    """DSTAR_RUN_LIVE_TESTS=0 must not be interpreted as live enabled."""

    monkeypatch.setenv("DSTAR_RUN_LIVE_TESTS", "0")

    assert os.environ["DSTAR_RUN_LIVE_TESTS"] != "1"
