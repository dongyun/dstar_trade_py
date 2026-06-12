"""Tests for the IDstarTradeSpi to Python dispatcher adapter."""

from __future__ import annotations

import re
from pathlib import Path

from dstar_trade_py import _dstar_trade_py as native
from dstar_trade_py.enums import Direction, OrderState
from dstar_trade_py.fields import DstarApiPositionField, DstarApiRspLoginField


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class RecordingDispatcher:
    """Simple dispatcher implementing on_event(event_name, payload)."""

    def __init__(self, fail_after: int | None = None) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []
        self.fail_after = fail_after

    def on_event(self, event_name: str, payload: dict[str, object]) -> None:
        """Record callback events and optionally raise for exception-safety tests."""

        self.events.append((event_name, payload))
        if self.fail_after is not None and len(self.events) >= self.fail_after:
            raise RuntimeError("dispatcher failure")


def test_spi_adapter_dispatches_representative_events() -> None:
    """The native adapter should dispatch snake_case names with copied payloads."""

    dispatcher = RecordingDispatcher()

    native._test_spi_dispatch(dispatcher)

    names = [name for name, _ in dispatcher.events]
    assert names == [
        "front_disconnected",
        "rsp_error",
        "rsp_user_login",
        "api_ready",
        "rsp_qry_position",
        "rtn_order",
        "rsp_qry_fund",
    ]
    assert dispatcher.events[0][1] == {}
    assert dispatcher.events[1][1]["error_code"] == 10001
    assert dispatcher.events[1][1]["error_message"] == "Not connected"
    assert dispatcher.events[3][1] == {"serial_id": 998877}


def test_spi_adapter_payloads_convert_to_dataclasses() -> None:
    """Callback dictionaries should be compatible with generated dataclasses."""

    dispatcher = RecordingDispatcher()

    native._test_spi_dispatch(dispatcher)
    payload_by_name = dict(dispatcher.events)
    login = DstarApiRspLoginField.from_dict(payload_by_name["rsp_user_login"])
    position_payload = payload_by_name["rsp_qry_position"]
    position = DstarApiPositionField.from_dict(position_payload["data"])

    assert login.AccountNo == "demo-account"
    assert login.AccountIndex == 7
    assert position_payload["last"] is True
    assert position.ContractNo == "GC2608"
    assert position.SerialId == 987654321


def test_spi_adapter_dispatches_order_payload_as_plain_dict() -> None:
    """Return notifications should contain copied scalar and text values."""

    dispatcher = RecordingDispatcher()

    native._test_spi_dispatch(dispatcher)
    payload_by_name = dict(dispatcher.events)
    order = payload_by_name["rtn_order"]

    assert order["Direct"] == int(Direction.BUY)
    assert order["OrderState"] == int(OrderState.QUEUE)
    assert order["AccountNo"] == "demo-account"
    assert order["OrderId"] == 10001


def test_spi_adapter_catches_python_callback_exceptions(capfd) -> None:
    """Python exceptions must be logged and must not escape C++ callbacks."""

    dispatcher = RecordingDispatcher(fail_after=1)

    native._test_spi_dispatch(dispatcher, raise_on_callback=True)
    captured = capfd.readouterr()

    assert dispatcher.events
    assert "dstar_trade_py callback error in front_disconnected" in captured.err


def test_all_spi_callbacks_are_declared_and_defined() -> None:
    """Every pure virtual IDstarTradeSpi callback must be implemented."""

    api_header = (PROJECT_ROOT / "third_party/dstar/include/DstarTradeApi.h").read_text(
        encoding="utf-8"
    )
    adapter_header = (PROJECT_ROOT / "cpp/trade_spi_adapter.h").read_text(encoding="utf-8")
    adapter_source = (PROJECT_ROOT / "cpp/trade_spi_adapter.cpp").read_text(encoding="utf-8")
    spi_body = api_header.split("class IDstarTradeSpi", 1)[1].split("};", 1)[0]
    callback_names = re.findall(r"virtual\s+void\s+(\w+)\(", spi_body)

    assert len(callback_names) == 39
    for callback_name in callback_names:
        assert f"void {callback_name}(" in adapter_header
        assert f"void PyTradeSpiAdapter::{callback_name}(" in adapter_source
