"""Tests for Pythonic order builders and high-level order methods."""

from __future__ import annotations

import pytest

from dstar_trade_py import CancelRequestBuilder, DstarTradeClient, OrderRequestBuilder
from dstar_trade_py.enums import Direction, Hedge, Offset, OrderType, ValidType
from dstar_trade_py.errors import DstarRequestError
from dstar_trade_py.fields import (
    DstarApiReqCmbOrderInsertField,
    DstarApiReqOfferInsertField,
    DstarApiReqOrderDeleteField,
    DstarApiReqOrderInsertField,
)


class RecordingNativeApi:
    """Fake native API that records request dictionaries and never connects."""

    def __init__(self) -> None:
        self.order: dict[str, object] | None = None
        self.cancel: dict[str, object] | None = None
        self.offer: dict[str, object] | None = None
        self.combo: dict[str, object] | None = None

    def req_order_insert(self, data: dict[str, object]) -> int:
        self.order = data
        return 0

    def req_order_delete(self, data: dict[str, object]) -> int:
        self.cancel = data
        return 0

    def req_offer_insert(self, data: dict[str, object]) -> int:
        self.offer = data
        return 0

    def req_cmb_order_insert(self, data: dict[str, object]) -> int:
        self.combo = data
        return 0


def make_ready_client(tmp_path) -> tuple[DstarTradeClient, RecordingNativeApi]:
    """Create a client with api_ready=True and a fake native API."""

    native = RecordingNativeApi()
    client = DstarTradeClient(
        api_factory=lambda: native,
        journal_path=tmp_path / "order_journal.jsonl",
    )
    client.api_ready = True
    return client, native


def test_limit_order_builder_matches_vendor_request_fields() -> None:
    """OrderRequestBuilder.limit_order should produce DstarApiReqOrderInsertField."""

    request = OrderRequestBuilder.limit_order(
        direct=int(Direction.BUY),
        offset=int(Offset.OPEN),
        hedge=int(Hedge.SPECULATE),
        valid_type=int(ValidType.GFD),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        order_qty=3,
        order_price=2400.5,
        client_req_id=100,
        reference=10,
        udp_auth_code=123,
    )

    assert isinstance(request, DstarApiReqOrderInsertField)
    assert request.OrderType == int(OrderType.LIMIT)
    assert request.ContractNo == "GC2608"
    assert request.OrderQty == 3
    assert request.OrderPrice == 2400.5


def test_market_order_builder_keeps_vendor_order_price_field() -> None:
    """Market requests still include OrderPrice because the vendor structure requires it."""

    request = OrderRequestBuilder.market_order_if_supported(
        direct=int(Direction.SELL),
        offset=int(Offset.CLOSE),
        hedge=int(Hedge.SPECULATE),
        valid_type=int(ValidType.IOC),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        order_qty=1,
        client_req_id=101,
    )

    assert request.OrderType == int(OrderType.MARKET)
    assert request.OrderPrice == 0.0


def test_combo_offer_and_cancel_builders() -> None:
    """Builders should cover combo order, offer, and cancellation structures."""

    combo = OrderRequestBuilder.combo_order(
        direct=int(Direction.BUY),
        offset=int(Offset.OPEN),
        hedge=int(Hedge.SPECULATE),
        order_type=int(OrderType.LIMIT),
        valid_type=int(ValidType.GFD),
        account_index=1,
        contract_index1=2,
        contract_no1="GC2608",
        contract_index2=3,
        contract_no2="GC2610",
        order_qty=1,
        order_price=10.5,
        client_req_id=102,
    )
    offer = OrderRequestBuilder.offer(
        buy_offset=int(Offset.OPEN),
        sell_offset=int(Offset.CLOSE),
        account_index=1,
        client_req_id=103,
        contract_index=2,
        contract_no="GC2608",
        order_qty=1,
        buy_price=2400.0,
        sell_price=2401.0,
    )
    cancel = CancelRequestBuilder.order_delete(
        account_index=1,
        client_req_id=104,
        order_id=10001,
        system_no="",
    )

    assert isinstance(combo, DstarApiReqCmbOrderInsertField)
    assert isinstance(offer, DstarApiReqOfferInsertField)
    assert isinstance(cancel, DstarApiReqOrderDeleteField)
    assert combo.ContractNo2 == "GC2610"
    assert offer.BuyPrice == 2400.0
    assert cancel.OrderId == 10001


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"contract_no": ""}, "contract_no is required"),
        ({"order_qty": 0}, "order_qty must be >= 1"),
        ({"order_price": 0}, "order_price must be > 0"),
        ({"direct": 999}, "direct must be one of"),
        ({"reference": -1}, "reference must be >= 0"),
    ],
)
def test_limit_order_builder_validates_inputs(kwargs: dict[str, object], message: str) -> None:
    """Invalid order parameters should fail before hitting the native API."""

    params = {
        "direct": int(Direction.BUY),
        "offset": int(Offset.OPEN),
        "hedge": int(Hedge.SPECULATE),
        "valid_type": int(ValidType.GFD),
        "account_index": 1,
        "contract_index": 2,
        "contract_no": "GC2608",
        "order_qty": 1,
        "order_price": 2400.5,
        "client_req_id": 100,
    }
    params.update(kwargs)

    with pytest.raises(ValueError, match=message):
        OrderRequestBuilder.limit_order(**params)


def test_client_order_methods_use_builders_and_return_local_codes(tmp_path) -> None:
    """High-level order methods should submit validated dicts and return only local codes."""

    client, native = make_ready_client(tmp_path)

    order_ret = client.insert_limit_order(
        direct=int(Direction.BUY),
        offset=int(Offset.OPEN),
        hedge=int(Hedge.SPECULATE),
        valid_type=int(ValidType.GFD),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        order_qty=1,
        order_price=2400.5,
        client_req_id=100,
    )
    cancel_ret = client.cancel_order(account_index=1, client_req_id=101, order_id=10001)
    offer_ret = client.insert_offer(
        buy_offset=int(Offset.OPEN),
        sell_offset=int(Offset.CLOSE),
        account_index=1,
        client_req_id=102,
        contract_index=2,
        contract_no="GC2608",
        order_qty=1,
        buy_price=2400.0,
        sell_price=2401.0,
    )
    combo_ret = client.insert_combo_order(
        direct=int(Direction.BUY),
        offset=int(Offset.OPEN),
        hedge=int(Hedge.SPECULATE),
        order_type=int(OrderType.LIMIT),
        valid_type=int(ValidType.GFD),
        account_index=1,
        contract_index1=2,
        contract_no1="GC2608",
        contract_index2=3,
        contract_no2="GC2610",
        order_qty=1,
        order_price=10.5,
        client_req_id=103,
    )

    assert order_ret == 0
    assert cancel_ret == 0
    assert offer_ret == 0
    assert combo_ret == 0
    assert native.order is not None
    assert native.order["OrderType"] == int(OrderType.LIMIT)
    assert native.cancel is not None
    assert native.offer is not None
    assert native.combo is not None
    assert client.trade_events.empty()


def test_client_rejects_duplicate_client_order_id(tmp_path) -> None:
    """A logical client_order_id may only be submitted once for idempotency."""

    client, _ = make_ready_client(tmp_path)
    params = {
        "direct": int(Direction.BUY),
        "offset": int(Offset.OPEN),
        "hedge": int(Hedge.SPECULATE),
        "valid_type": int(ValidType.GFD),
        "account_index": 1,
        "contract_index": 2,
        "contract_no": "GC2608",
        "order_qty": 1,
        "order_price": 2400.5,
        "client_order_id": "biz-duplicate",
    }

    assert client.insert_limit_order(client_req_id=100, **params) == 0
    with pytest.raises(ValueError, match="duplicate client_order_id"):
        client.insert_limit_order(client_req_id=101, **params)


def test_client_rejects_order_methods_before_api_ready(tmp_path) -> None:
    """Order methods must not submit before api_ready."""

    client = DstarTradeClient(
        api_factory=RecordingNativeApi,
        journal_path=tmp_path / "order_journal.jsonl",
    )

    with pytest.raises(DstarRequestError, match="insert_limit_order failed"):
        client.insert_limit_order(
            direct=int(Direction.BUY),
            offset=int(Offset.OPEN),
            hedge=int(Hedge.SPECULATE),
            valid_type=int(ValidType.GFD),
            account_index=1,
            contract_index=2,
            contract_no="GC2608",
            order_qty=1,
            order_price=2400.5,
            client_req_id=100,
        )
