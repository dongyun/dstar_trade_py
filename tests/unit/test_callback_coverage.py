"""Static coverage checks for every IDstarTradeSpi callback."""

from __future__ import annotations

import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_HEADER = PROJECT_ROOT / "third_party/dstar/include/DstarTradeApi.h"
ADAPTER_HEADER = PROJECT_ROOT / "cpp/trade_spi_adapter.h"
ADAPTER_SOURCE = PROJECT_ROOT / "cpp/trade_spi_adapter.cpp"
CLIENT_SOURCE = PROJECT_ROOT / "dstar_trade_py/client.py"


def _callback_names() -> list[str]:
    """Parse all pure virtual callback names from IDstarTradeSpi."""

    source = API_HEADER.read_text(encoding="utf-8")
    spi_body = source.split("class IDstarTradeSpi", 1)[1].split("};", 1)[0]
    return re.findall(r"virtual\s+void\s+(\w+)\(", spi_body)


def _expected_event_name(callback_name: str) -> str:
    """Convert vendor callback names to the SDK's snake_case event names."""

    if callback_name == "OnFrontDisconnected":
        return "front_disconnected"
    if callback_name == "OnApiReady":
        return "api_ready"
    stem = callback_name[2:]
    return re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()


def _callback_body(source: str, callback_name: str) -> str:
    """Return one callback definition body from the adapter source."""

    pattern = re.compile(
        rf"void PyTradeSpiAdapter::{callback_name}\([^)]*\)(?:\s+noexcept)?\s*\{{(?P<body>.*?)\n\}}",
        re.DOTALL,
    )
    match = pattern.search(source)
    assert match is not None, callback_name
    return match.group("body")


def test_all_spi_callbacks_have_adapter_declarations_and_definitions() -> None:
    """Every callback declared by the vendor header must be implemented."""

    callback_names = _callback_names()
    adapter_header = ADAPTER_HEADER.read_text(encoding="utf-8")
    adapter_source = ADAPTER_SOURCE.read_text(encoding="utf-8")

    assert len(callback_names) == 39
    for callback_name in callback_names:
        assert f"void {callback_name}(" in adapter_header
        assert f"void PyTradeSpiAdapter::{callback_name}(" in adapter_source


def test_all_spi_callbacks_dispatch_to_unified_dispatcher() -> None:
    """Every callback body must call dispatch_event with the expected event name."""

    adapter_source = ADAPTER_SOURCE.read_text(encoding="utf-8")
    for callback_name in _callback_names():
        body = _callback_body(adapter_source, callback_name)
        event_name = _expected_event_name(callback_name)

        assert f'dispatch_event("{event_name}"' in body
        assert "dispatcher_.attr" not in body


def test_dispatcher_catches_python_and_cpp_exceptions() -> None:
    """Callback exceptions must be caught before they can reach the vendor SDK."""

    adapter_source = ADAPTER_SOURCE.read_text(encoding="utf-8")
    dispatch_body = _callback_body(adapter_source, "dispatch_event")

    assert "noexcept" in adapter_source
    assert "py::gil_scoped_acquire gil" in dispatch_body
    assert "dispatcher_.attr(\"on_event\")" in dispatch_body
    assert "catch (const py::error_already_set&" in adapter_source
    assert "catch (const std::exception&" in adapter_source
    assert "catch (...)" in adapter_source


def test_python_client_knows_every_event_name() -> None:
    """The high-level client should recognize every event name emitted by C++."""

    client_source = CLIENT_SOURCE.read_text(encoding="utf-8")
    expected_events = {_expected_event_name(callback_name) for callback_name in _callback_names()}

    for event_name in expected_events:
        assert f'"{event_name}"' in client_source, event_name
