"""Coverage checks for every active IDstarTradeApi interface."""

from __future__ import annotations

import re
from pathlib import Path

import dstar_trade_py
from dstar_trade_py import AsyncDstarTradeClient, DstarTradeClient, NativeTradeApi


PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_HEADER = PROJECT_ROOT / "third_party/dstar/include/DstarTradeApi.h"

REQUIRED_CPP_INTERFACES = {
    "RegisterSpi",
    "RegisterFrontAddress",
    "SetApiLogPath",
    "SetLoginInfo",
    "SetCpuId",
    "SetSubscribeStartId",
    "SetRealTimeDataFilter",
    "SetRunMode",
    "GetSystemInfo",
    "SetSubmitInfo",
    "SetInitQryInfo",
    "Init",
    "ReqLastClientReqId",
    "ReqPwdMod",
    "ReqOrderInsert",
    "ReqOfferInsert",
    "ReqOfferInsertNew",
    "ReqOrderDelete",
    "ReqCmbOrderInsert",
    "ReqQryFund",
    "ReqQryPosition",
    "GetApiVersion",
    "CreateDstarTradeApi",
    "FreeDstarTradeApi",
}

NATIVE_COVERAGE = {
    "RegisterSpi": (NativeTradeApi, "register_callback"),
    "RegisterFrontAddress": (NativeTradeApi, "register_front_address"),
    "SetApiLogPath": (NativeTradeApi, "set_api_log_path"),
    "SetLoginInfo": (NativeTradeApi, "set_login_info"),
    "SetCpuId": (NativeTradeApi, "set_cpu_id"),
    "SetSubscribeStartId": (NativeTradeApi, "set_subscribe_start_id"),
    "SetRealTimeDataFilter": (NativeTradeApi, "set_real_time_data_filter"),
    "SetRunMode": (NativeTradeApi, "set_run_mode"),
    "GetSystemInfo": (NativeTradeApi, "get_system_info"),
    "SetSubmitInfo": (NativeTradeApi, "set_submit_info"),
    "SetInitQryInfo": (NativeTradeApi, "set_init_qry_info"),
    "Init": (NativeTradeApi, "init"),
    "ReqLastClientReqId": (NativeTradeApi, "req_last_client_req_id"),
    "ReqPwdMod": (NativeTradeApi, "req_pwd_mod"),
    "ReqOrderInsert": (NativeTradeApi, "req_order_insert"),
    "ReqOfferInsert": (NativeTradeApi, "req_offer_insert"),
    "ReqOfferInsertNew": (NativeTradeApi, "req_offer_insert_new"),
    "ReqOrderDelete": (NativeTradeApi, "req_order_delete"),
    "ReqCmbOrderInsert": (NativeTradeApi, "req_cmb_order_insert"),
    "ReqQryFund": (NativeTradeApi, "req_qry_fund"),
    "ReqQryPosition": (NativeTradeApi, "req_qry_position"),
    "GetApiVersion": (NativeTradeApi, "get_api_version"),
    "CreateDstarTradeApi": (dstar_trade_py, "create_and_free_api"),
    "FreeDstarTradeApi": (dstar_trade_py, "create_and_free_api"),
}

CLIENT_COVERAGE = {
    "RegisterSpi": "connect",
    "RegisterFrontAddress": "connect",
    "SetApiLogPath": "connect",
    "SetLoginInfo": "login",
    "SetCpuId": "connect",
    "SetSubscribeStartId": "connect",
    "SetRealTimeDataFilter": "connect",
    "SetRunMode": "connect",
    "GetSystemInfo": "get_system_info",
    "SetSubmitInfo": "connect",
    "SetInitQryInfo": "connect",
    "Init": "login",
    "ReqLastClientReqId": "query_last_client_req_id",
    "ReqPwdMod": "modify_password",
    "ReqOrderInsert": "insert_order",
    "ReqOfferInsert": "insert_offer",
    "ReqOfferInsertNew": "insert_offer_new",
    "ReqOrderDelete": "cancel_order",
    "ReqCmbOrderInsert": "insert_cmb_order",
    "ReqQryFund": "query_fund",
    "ReqQryPosition": "query_position",
    "GetApiVersion": "get_api_version",
    "CreateDstarTradeApi": "__init__",
    "FreeDstarTradeApi": "close",
}


def test_required_cpp_interface_list_matches_vendor_header() -> None:
    """The coverage table must track every active C++ API method and factory."""

    source = API_HEADER.read_text(encoding="utf-8")
    api_body = source.split("class DSTARTRADEAPI_EXPORT IDstarTradeApi", 1)[1].split(
        "};",
        1,
    )[0]
    virtual_methods = set(re.findall(r"virtual\s+[^;=]+?\s+\*?(\w+)\(", api_body))
    factory_methods = set(
        re.findall(r"DSTARTRADEAPI_EXPORT\s+(?:IDstarTradeApi\s+\*|void)\s*(\w+)\(", source)
    )

    assert virtual_methods | factory_methods == REQUIRED_CPP_INTERFACES


def test_native_binding_exposes_every_active_interface() -> None:
    """Every C++ active interface must be reachable from the pybind11 layer."""

    assert set(NATIVE_COVERAGE) == REQUIRED_CPP_INTERFACES
    for owner, method_name in NATIVE_COVERAGE.values():
        assert hasattr(owner, method_name), method_name


def test_python_clients_expose_every_active_interface() -> None:
    """The synchronous and asyncio clients should proxy every suitable API action."""

    assert set(CLIENT_COVERAGE) == REQUIRED_CPP_INTERFACES
    for method_name in CLIENT_COVERAGE.values():
        assert hasattr(DstarTradeClient, method_name), method_name
        if not method_name.startswith("__"):
            assert hasattr(AsyncDstarTradeClient, method_name), method_name
