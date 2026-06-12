"""Event routing and synchronous query tests for DstarTradeClient."""

from __future__ import annotations

import pytest

from dstar_trade_py import DstarTradeClient
from dstar_trade_py.errors import DstarTimeoutError
from dstar_trade_py.fields import DstarApiFundField, DstarApiMatchField, DstarApiOrderField


class QueryFakeNativeTradeApi:
    """Fake native API that can synchronously emit requested responses."""

    def __init__(self) -> None:
        self.dispatcher = None
        self.emit_fund = True
        self.emit_position = True
        self.emit_last_req_id = True

    def register_callback(self, dispatcher) -> None:
        self.dispatcher = dispatcher

    def register_front_address(self, ip: str, port: int) -> None:
        pass

    def set_cpu_id(self, recv_notice_cpu_id: int, log_cpu_id: int) -> None:
        pass

    def set_subscribe_start_id(self, start_id: int) -> None:
        pass

    def set_real_time_data_filter(self, filter: int) -> None:
        pass

    def set_run_mode(self, mode: int) -> None:
        pass

    def set_init_qry_info(self, init_qry_info: dict[str, object]) -> None:
        pass

    def req_qry_fund(self) -> int:
        if self.emit_fund:
            self.emit(
                "rsp_qry_fund",
                {
                    "AccountNo": "demo-account",
                    "PreEquity": 100000.0,
                    "Equity": 100250.5,
                    "Avail": 80000.0,
                    "Fee": 1.0,
                    "Margin": 20000.0,
                    "FrozenMargin": 0.0,
                    "Premium": 0.0,
                    "CloseProfit": 0.0,
                    "PositionProfit": 250.5,
                    "CashIn": 0.0,
                    "CashOut": 0.0,
                    "OrderFee": 0.0,
                    "Frozen": 0.0,
                    "DeliveryFrozen": 0.0,
                },
            )
        return 0

    def req_qry_position(self) -> int:
        if self.emit_position:
            self.emit(
                "rsp_qry_position",
                {
                    "data": {
                        "AccountNo": "demo-account",
                        "ContractNo": "GC2608",
                        "PreBuyQty": 1,
                        "TodayBuyQty": 2,
                        "BuyAvgPrice": 2400.5,
                        "PreSellQty": 0,
                        "TodaySellQty": 0,
                        "SellAvgPrice": 0.0,
                        "SerialId": 10,
                    },
                    "last": False,
                },
            )
            self.emit("rsp_qry_position", {"data": {}, "last": True})
        return 0

    def req_last_client_req_id(self) -> int:
        if self.emit_last_req_id:
            self.emit("rsp_last_req_id", {"LastClientReqId": 1234})
        return 0

    def emit(self, event_name: str, payload: dict[str, object]) -> None:
        assert self.dispatcher is not None
        self.dispatcher.on_event(event_name, payload)


def make_ready_client(tmp_path) -> tuple[DstarTradeClient, QueryFakeNativeTradeApi]:
    """Create a connected and ready client backed by the query fake."""

    fake = QueryFakeNativeTradeApi()
    client = DstarTradeClient(
        front_ip="127.0.0.1",
        front_port=12345,
        journal_path=tmp_path / "order_journal.jsonl",
        api_factory=lambda: fake,
    )
    client.connect()
    fake.emit("api_ready", {"serial_id": 1})
    return client, fake


def test_query_fund_waits_for_response_and_routes_event(tmp_path) -> None:
    """query_fund should return a dataclass and push the same type to fund_events."""

    client, _ = make_ready_client(tmp_path)

    fund = client.query_fund(timeout=0.01)
    queued_fund = client.fund_events.get_nowait()

    assert isinstance(fund, DstarApiFundField)
    assert fund.AccountNo == "demo-account"
    assert fund.Equity == 100250.5
    assert queued_fund == fund


def test_query_position_collects_until_last_response(tmp_path) -> None:
    """query_position should collect positions until the last flag is received."""

    client, _ = make_ready_client(tmp_path)

    positions = client.query_position(timeout=0.01)
    queued_position = client.position_events.get_nowait()

    assert len(positions) == 1
    assert positions[0].ContractNo == "GC2608"
    assert queued_position == positions[0]


def test_query_position_timeout(tmp_path) -> None:
    """Missing last response should surface as DstarTimeoutError."""

    client, fake = make_ready_client(tmp_path)
    fake.emit_position = False

    with pytest.raises(DstarTimeoutError, match="query_position"):
        client.query_position(timeout=0.01)


def test_query_last_client_req_id_waits_for_callback(tmp_path) -> None:
    """query_last_client_req_id should return the callback's LastClientReqId."""

    client, _ = make_ready_client(tmp_path)

    assert client.query_last_client_req_id(timeout=0.01) == 1234
    assert client.request_id_manager.current == 1234


def test_raw_order_and_trade_events_are_converted_and_queued(tmp_path) -> None:
    """Dispatcher should convert raw dict payloads into generated dataclasses."""

    client, fake = make_ready_client(tmp_path)

    fake.emit(
        "rtn_order",
        {
            "Direct": 66,
            "Offset": 79,
            "Hedge": 84,
            "ValidType": 51,
            "OrderPrice": 2400.5,
            "OrderQty": 1,
            "MinQty": 1,
            "MatchQty": 0,
            "ErrCode": 0,
            "SerialId": 10,
            "OrderId": 10001,
            "FrozenMargin": 0.0,
            "Margin": 0.0,
            "Fee": 0.0,
            "AccountNo": "demo-account",
            "OrderLocalNo": "",
            "SystemNo": "",
            "UpdateTime": "",
            "ExchInsertTime": "",
            "Reference": 1,
            "ContractNo1": "GC2608",
            "OrderType": 50,
            "OrderState": 50,
            "SeatIndex": 0,
            "UpSeatNo": "",
            "ContractNo2": "",
            "CmbId": 0,
            "OrderFee": 0.0,
        },
    )
    fake.emit(
        "rtn_match",
        {
            "ContractNo": "GC2608",
            "MatchQty": 1,
            "MatchPrice": 2400.5,
            "Offset": 79,
            "Direct": 66,
            "Hedge": 84,
            "OrderType": 50,
            "Reference": 1,
            "SerialId": 11,
            "OrderId": 10001,
            "MatchId": 20001,
            "MatchTime": "",
            "ExchMatchNo": "",
            "SystemNo": "",
            "Fee": 0.0,
            "Margin": 0.0,
            "FrozenMargin": 0.0,
            "Premium": 0.0,
            "CloseProfit": 0.0,
            "AccountNo": "demo-account",
            "UpdateTime": "",
            "CmbId": 0,
            "OrderFee": 0.0,
        },
    )

    raw_order = client.raw_events.get_nowait()
    raw_match = client.raw_events.get_nowait()
    order = client.order_events.get_nowait()
    trade = client.trade_events.get_nowait()

    assert raw_order.name == "api_ready"
    assert raw_match.name == "rtn_order"
    assert isinstance(order, DstarApiOrderField)
    assert isinstance(trade, DstarApiMatchField)
    assert order.ContractNo1 == "GC2608"
    assert trade.MatchId == 20001
