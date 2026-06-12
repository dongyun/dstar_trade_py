"""Tests for the pybind11 NativeTradeApi bridge.

These tests intentionally avoid calling ``init()`` so they do not connect to a real
trading server. Request methods are invoked only against an uninitialized API instance;
the assertions check that conversion and native dispatch return an integer error code.
"""

from __future__ import annotations

import pytest

from dstar_trade_py import NativeTradeApi
from dstar_trade_py.enums import (
    AuthType,
    Direction,
    Hedge,
    Offset,
    OrderType,
    RealTimeDataFilter,
    RunMode,
    ValidType,
)
from dstar_trade_py.fields import (
    DstarApiInitQryInfoField,
    DstarApiReqCmbOrderInsertField,
    DstarApiReqLoginField,
    DstarApiReqOfferInsertField,
    DstarApiReqOfferInsertNewField,
    DstarApiReqOrderDeleteField,
    DstarApiReqOrderInsertField,
    DstarApiReqPwdModField,
    DstarApiSubmitInfoField,
)


class RecordingDispatcher:
    """Minimal Python callback dispatcher accepted by NativeTradeApi."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def on_event(self, event_name: str, payload: dict[str, object]) -> None:
        """Record events if the native SPI receives callbacks during tests."""

        self.events.append((event_name, payload))


def order_insert_dict() -> dict[str, object]:
    """Build a complete DstarApiReqOrderInsertField payload."""

    return DstarApiReqOrderInsertField(
        Direct=int(Direction.BUY),
        Offset=int(Offset.OPEN),
        Hedge=int(Hedge.SPECULATE),
        OrderType=int(OrderType.LIMIT),
        ValidType=int(ValidType.GFD),
        SeatIndex=0,
        AccountIndex=1,
        ContractIndex=2,
        ContractNo="GC2608",
        OrderQty=1,
        MinQty=1,
        OrderPrice=2400.5,
        ClientReqId=100,
        Reference=10,
        UdpAuthCode=123456,
    ).to_dict()


def test_native_trade_api_constructs_and_reports_version() -> None:
    """NativeTradeApi should own a vendor API instance and expose its version."""

    api = NativeTradeApi()

    assert isinstance(api.get_api_version(), str)
    assert api.get_api_version()


def test_native_trade_api_accepts_basic_configuration(tmp_path) -> None:
    """Configuration methods should accept Python primitives and field dicts."""

    api = NativeTradeApi()
    dispatcher = RecordingDispatcher()

    api.register_callback(dispatcher)
    api.register_front_address("127.0.0.1", 12345)
    api.set_api_log_path(str(tmp_path))
    api.set_cpu_id(-1, -1)
    api.set_subscribe_start_id(-1)
    api.set_real_time_data_filter(int(RealTimeDataFilter.NONE))
    api.set_run_mode(int(RunMode.FULL_LOAD))
    api.set_login_info(
        DstarApiReqLoginField(
            AccountNo="demo-account",
            Password="demo-password",
            AppId="demo-app",
            LicenseNo="demo-license",
        ).to_dict()
    )
    api.set_submit_info(
        DstarApiSubmitInfoField(
            AccountNo="demo-account",
            AuthType=int(AuthType.DIRECT),
            AuthKeyVersion=1,
            SystemInfo="system-info",
            ClientLoginIp="127.0.0.1",
            ClientLoginPort=12345,
            ClientLoginDateTime="20260612120000",
            ClientAppId="demo-app",
            LicenseNo="demo-license",
        ).to_dict()
    )
    api.set_init_qry_info(DstarApiInitQryInfoField().to_dict())


def test_register_callback_requires_on_event() -> None:
    """The bridge should fail early for an invalid callback dispatcher."""

    api = NativeTradeApi()

    with pytest.raises(ValueError, match="on_event"):
        api.register_callback(object())


def test_get_system_info_returns_stable_shape() -> None:
    """System info collection may fail without privileges, but shape is stable."""

    api = NativeTradeApi()

    result = api.get_system_info()

    assert set(result) == {"return_code", "length", "auth_key_version", "system_info"}
    assert isinstance(result["return_code"], int)
    assert isinstance(result["length"], int)
    assert isinstance(result["auth_key_version"], int)
    assert isinstance(result["system_info"], str)


def test_request_methods_convert_dicts_and_return_error_codes() -> None:
    """Request methods should convert dict payloads and return native int codes."""

    api = NativeTradeApi()

    offer_insert = DstarApiReqOfferInsertField(
        BuyOffset=int(Offset.OPEN),
        SellOffset=int(Offset.CLOSE),
        AccountIndex=1,
        ClientReqId=101,
        ContractIndex=2,
        ContractNo="GC2608",
        OrderQty=1,
        BuyPrice=2400.0,
        SellPrice=2401.0,
        SeatIndex=0,
        EnquiryNo="",
        Reference=11,
        UdpAuthCode=123456,
    ).to_dict()
    offer_insert_new = DstarApiReqOfferInsertNewField(
        BuyOffset=int(Offset.OPEN),
        SellOffset=int(Offset.CLOSE),
        AccountIndex=1,
        ClientReqId=102,
        ContractIndex=2,
        ContractNo="GC2608",
        BuyOrderQty=1,
        SellOrderQty=1,
        BuyPrice=2400.0,
        SellPrice=2401.0,
        SeatIndex=0,
        EnquiryNo="",
        Reference=12,
        UdpAuthCode=123456,
        ReplaceId=0,
    ).to_dict()
    order_delete = DstarApiReqOrderDeleteField(
        AccountIndex=1,
        ClientReqId=103,
        UdpAuthCode=123456,
        Reference=13,
        SeatIndex=0,
        OrderId=999,
        SystemNo="",
    ).to_dict()
    cmb_order_insert = DstarApiReqCmbOrderInsertField(
        Direct=int(Direction.BUY),
        Offset=int(Offset.OPEN),
        Hedge=int(Hedge.SPECULATE),
        OrderType=int(OrderType.LIMIT),
        ValidType=int(ValidType.GFD),
        SeatIndex=0,
        AccountIndex=1,
        ContractIndex1=2,
        ContractNo1="GC2608",
        ContractIndex2=3,
        ContractNo2="GC2610",
        OrderQty=1,
        MinQty=1,
        OrderPrice=10.5,
        ClientReqId=104,
        Reference=14,
        UdpAuthCode=123456,
    ).to_dict()

    assert isinstance(api.req_last_client_req_id(), int)
    assert isinstance(api.req_pwd_mod(DstarApiReqPwdModField("new", "old").to_dict()), int)
    assert isinstance(api.req_order_insert(order_insert_dict()), int)
    assert isinstance(api.req_offer_insert(offer_insert), int)
    assert isinstance(api.req_offer_insert_new(offer_insert_new), int)
    assert isinstance(api.req_order_delete(order_delete), int)
    assert isinstance(api.req_cmb_order_insert(cmb_order_insert), int)
    assert isinstance(api.req_qry_fund(), int)
    assert isinstance(api.req_qry_position(), int)


def test_dict_conversion_reports_missing_required_fields() -> None:
    """Missing C++ fields should produce a clear validation error."""

    api = NativeTradeApi()

    with pytest.raises(
        ValueError,
        match=r"Missing required field for DstarApiReqLoginField: AccountNo",
    ):
        api.set_login_info({"Password": "demo-password", "AppId": "app", "LicenseNo": "lic"})


def test_dict_conversion_rejects_oversized_char_arrays() -> None:
    """Strings must fit the vendor fixed-size char arrays including NUL."""

    api = NativeTradeApi()
    payload = DstarApiReqLoginField(
        AccountNo="x" * 256,
        Password="demo-password",
        AppId="demo-app",
        LicenseNo="demo-license",
    ).to_dict()

    with pytest.raises(ValueError, match="exceeds fixed char array capacity"):
        api.set_login_info(payload)
