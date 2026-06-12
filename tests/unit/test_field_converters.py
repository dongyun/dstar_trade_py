"""Integration tests for C++ packed-structure to Python dictionary conversion."""

from __future__ import annotations

import re
from pathlib import Path

from dstar_trade_py import _dstar_trade_py as native
from dstar_trade_py.enums import Direction, OrderState
from dstar_trade_py.fields import (
    DstarApiFundField,
    DstarApiMatchField,
    DstarApiOrderField,
    DstarApiPositionField,
    DstarApiRspLoginField,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_every_vendor_struct_has_a_converter_declaration_and_definition() -> None:
    """All 36 named vendor structs must have an overloaded conversion function."""

    vendor_header = (
        PROJECT_ROOT / "third_party/dstar/include/DstarTradeApiStruct.h"
    ).read_text(encoding="utf-8")
    converter_header = (PROJECT_ROOT / "cpp/field_converters.h").read_text(
        encoding="utf-8"
    )
    converter_source = (PROJECT_ROOT / "cpp/field_converters.cpp").read_text(
        encoding="utf-8"
    )
    struct_names = re.findall(r"^typedef struct (\w+)", vendor_header, re.MULTILINE)

    assert len(struct_names) == 36
    for struct_name in struct_names:
        signature = f"py::dict to_py_dict(const {struct_name}* field)"
        assert signature + ";" in converter_header
        assert signature + " {" in converter_source


def _samples() -> dict[str, dict[str, object]]:
    """Request fresh native dictionaries so no C++ pointer can outlive a call."""

    return native._test_field_converter_samples()


def test_native_login_dict_converts_to_dataclass() -> None:
    """Login response arrays, integers, and enum bytes convert correctly."""

    payload = _samples()["login"]
    login = DstarApiRspLoginField.from_dict(payload)

    assert login.AccountNo == "demo-account"
    assert login.TradeDate == "20260612"
    assert login.AccountIndex == 7
    assert login.UdpAuthCode == 123456
    assert login.ErrorCode == 0
    assert login.to_dict() == payload


def test_native_fund_and_position_dicts_convert_to_dataclasses() -> None:
    """Account snapshots preserve floating-point and wide integer fields."""

    samples = _samples()
    fund = DstarApiFundField.from_dict(samples["fund"])
    position = DstarApiPositionField.from_dict(samples["position"])

    assert fund.Equity == 100250.75
    assert fund.Avail == 80000.25
    assert position.ContractNo == "GC2608"
    assert position.TodayBuyQty == 2
    assert position.SerialId == 987654321


def test_native_order_and_match_dicts_convert_to_dataclasses() -> None:
    """Order and match dictionaries preserve enum bytes, IDs, prices, and text."""

    samples = _samples()
    order = DstarApiOrderField.from_dict(samples["order"])
    match = DstarApiMatchField.from_dict(samples["match"])

    assert order.Direct == int(Direction.BUY)
    assert order.OrderState == int(OrderState.QUEUE)
    assert order.ContractNo1 == "GC2608"
    assert order.OrderPrice == 2412.5
    assert match.OrderId == 10001
    assert match.MatchId == 20002
    assert match.MatchPrice == 2411.25


def test_error_bool_null_and_invalid_utf8_conventions() -> None:
    """Scalar errors, bools, null pointers, and invalid UTF-8 are deterministic."""

    samples = _samples()

    assert samples["error"] == {"ErrorCode": 10001}
    assert samples["bool"] == {"Value": True}
    assert type(samples["bool"]["Value"]) is bool
    assert samples["null_login"] == {}
    assert samples["invalid_utf8"]["AccountNo"] == "A\ufffd"
    assert samples["unterminated"]["Password"] == "x" * 65
