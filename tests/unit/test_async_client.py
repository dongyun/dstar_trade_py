"""Tests for the asyncio high-level Dstar client."""

from __future__ import annotations

import asyncio
import threading

import pytest

from dstar_trade_py import AsyncDstarTradeClient
from dstar_trade_py.enums import Direction, Hedge, Offset, OrderType, ValidType
from dstar_trade_py.errors import DstarRequestError, DstarTimeoutError
from dstar_trade_py.fields import DstarApiFundField, DstarApiMatchField, DstarApiPositionField


def fund_payload() -> dict[str, object]:
    """Return a complete DstarApiFundField payload."""

    return {
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
    }


def order_payload() -> dict[str, object]:
    """Return a complete DstarApiOrderField payload."""

    return {
        "Direct": int(Direction.BUY),
        "Offset": int(Offset.OPEN),
        "Hedge": int(Hedge.SPECULATE),
        "ValidType": int(ValidType.GFD),
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
        "OrderType": int(OrderType.LIMIT),
        "OrderState": 50,
        "SeatIndex": 0,
        "UpSeatNo": "",
        "ContractNo2": "",
        "CmbId": 0,
        "OrderFee": 0.0,
    }


def trade_payload() -> dict[str, object]:
    """Return a complete DstarApiMatchField payload."""

    return {
        "ContractNo": "GC2608",
        "MatchQty": 1,
        "MatchPrice": 2400.5,
        "Offset": int(Offset.OPEN),
        "Direct": int(Direction.BUY),
        "Hedge": int(Hedge.SPECULATE),
        "OrderType": int(OrderType.LIMIT),
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
    }


class AsyncFakeNativeTradeApi:
    """Fake NativeTradeApi that emits callbacks from background threads."""

    def __init__(self) -> None:
        self.dispatcher = None
        self.emit_fund = True
        self.emit_position = True
        self.order_payload: dict[str, object] | None = None
        self.cancel_payload: dict[str, object] | None = None

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
            self.emit_from_thread("rsp_qry_fund", fund_payload())
        return 0

    def req_qry_position(self) -> int:
        if self.emit_position:
            assert self.dispatcher is not None

            def emit_position_batch() -> None:
                self.dispatcher.on_event(
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
                self.dispatcher.on_event("rsp_qry_position", {"data": {}, "last": True})

            thread = threading.Thread(target=emit_position_batch, daemon=True)
            thread.start()
            thread.join(timeout=1)
        return 0

    def req_order_insert(self, data: dict[str, object]) -> int:
        self.order_payload = data
        return 0

    def req_order_delete(self, data: dict[str, object]) -> int:
        self.cancel_payload = data
        return 0

    def emit_from_thread(self, event_name: str, payload: dict[str, object]) -> threading.Thread:
        """Emit through the registered dispatcher from a non-asyncio thread."""

        assert self.dispatcher is not None
        thread = threading.Thread(
            target=self.dispatcher.on_event,
            args=(event_name, payload),
            daemon=True,
        )
        thread.start()
        return thread


def make_client(tmp_path) -> tuple[AsyncDstarTradeClient, AsyncFakeNativeTradeApi]:
    """Create an async client backed by one fake native instance."""

    fake = AsyncFakeNativeTradeApi()
    client = AsyncDstarTradeClient(
        front_ip="127.0.0.1",
        front_port=12345,
        journal_path=tmp_path / "order_journal.jsonl",
        api_factory=lambda: fake,
    )
    return client, fake


def test_async_wait_ready_uses_threadsafe_callback_delivery(tmp_path) -> None:
    """wait_ready should be completed by a callback emitted from another thread."""

    async def scenario() -> None:
        client, fake = make_client(tmp_path)
        await client.connect()

        waiter = asyncio.create_task(client.wait_ready(timeout=1))
        fake.emit_from_thread("api_ready", {"serial_id": 1})
        await waiter

        event = await anext(client.iter_events())
        assert event.name == "api_ready"
        assert client.api_ready is True
        await client.close()

    asyncio.run(scenario())


def test_async_query_fund_and_position_wait_for_callbacks(tmp_path) -> None:
    """query methods should await callback data converted to dataclasses."""

    async def scenario() -> None:
        client, fake = make_client(tmp_path)
        await client.connect()
        fake.emit_from_thread("api_ready", {"serial_id": 1})
        await client.wait_ready(timeout=1)

        fund = await client.query_fund(timeout=1)
        positions = await client.query_position(timeout=1)

        assert isinstance(fund, DstarApiFundField)
        assert fund.Equity == 100250.5
        assert len(positions) == 1
        assert isinstance(positions[0], DstarApiPositionField)
        assert positions[0].ContractNo == "GC2608"
        await client.close()

    asyncio.run(scenario())


def test_async_query_fund_timeout(tmp_path) -> None:
    """A missing async response should raise DstarTimeoutError."""

    async def scenario() -> None:
        client, fake = make_client(tmp_path)
        fake.emit_fund = False
        await client.connect()
        fake.emit_from_thread("api_ready", {"serial_id": 1})
        await client.wait_ready(timeout=1)

        with pytest.raises(DstarTimeoutError, match="query_fund"):
            await client.query_fund(timeout=0.01)
        await client.close()

    asyncio.run(scenario())


def test_async_insert_and_cancel_require_ready(tmp_path) -> None:
    """Order methods should reject calls before api_ready and return local codes after it."""

    async def scenario() -> None:
        client, fake = make_client(tmp_path)
        await client.connect()

        with pytest.raises(DstarRequestError):
            await client.insert_order(
                direct=int(Direction.BUY),
                offset=int(Offset.OPEN),
                hedge=int(Hedge.SPECULATE),
                order_type=int(OrderType.LIMIT),
                valid_type=int(ValidType.GFD),
                account_index=1,
                contract_index=2,
                contract_no="GC2608",
                order_qty=1,
                order_price=2400.5,
                client_req_id=100,
            )

        fake.emit_from_thread("api_ready", {"serial_id": 1})
        await client.wait_ready(timeout=1)
        insert_ret = await client.insert_order(
            direct=int(Direction.BUY),
            offset=int(Offset.OPEN),
            hedge=int(Hedge.SPECULATE),
            order_type=int(OrderType.LIMIT),
            valid_type=int(ValidType.GFD),
            account_index=1,
            contract_index=2,
            contract_no="GC2608",
            order_qty=1,
            order_price=2400.5,
            client_req_id=100,
        )
        cancel_ret = await client.cancel_order(
            account_index=1,
            client_req_id=101,
            order_id=10001,
            system_no="",
        )

        assert insert_ret == 0
        assert cancel_ret == 0
        assert fake.order_payload is not None
        assert fake.cancel_payload is not None
        await client.close()

    asyncio.run(scenario())


def test_async_iter_orders_and_trades(tmp_path) -> None:
    """Async iterators should receive converted order and trade events."""

    async def scenario() -> None:
        client, fake = make_client(tmp_path)
        await client.connect()
        order_task = asyncio.create_task(anext(client.iter_orders()))
        trade_task = asyncio.create_task(anext(client.iter_trades()))

        fake.emit_from_thread("rtn_order", order_payload())
        fake.emit_from_thread("rtn_match", trade_payload())
        order = await asyncio.wait_for(order_task, timeout=1)
        trade = await asyncio.wait_for(trade_task, timeout=1)

        assert order.ContractNo1 == "GC2608"
        assert isinstance(trade, DstarApiMatchField)
        assert trade.MatchId == 20001
        await client.close()

    asyncio.run(scenario())
