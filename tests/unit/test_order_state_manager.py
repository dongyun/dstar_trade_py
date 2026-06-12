"""Tests for OrderStateManager and order journal behavior."""

from __future__ import annotations

import json

import pytest

from dstar_trade_py import OrderJournal, OrderStateManager
from dstar_trade_py.enums import Direction, Hedge, Offset, OrderType, OrderState, ValidType
from dstar_trade_py.fields import DstarApiMatchField, DstarApiOrderField, DstarApiRspOrderInsertField
from dstar_trade_py.fields import DstarApiReqOrderInsertField


def test_order_state_manager_tracks_rsp_order_and_match() -> None:
    """Order state should move from local submission to response, order update, and match."""

    manager = OrderStateManager()
    state = manager.register_submission("biz-1", 100)

    assert state.status == "submitted_local"

    rsp = DstarApiRspOrderInsertField(
        ClientReqId=100,
        OrderId=200,
        ErrCode=0,
    )
    order = DstarApiOrderField(
        OrderId=200,
        SystemNo="SYS001",
        OrderState=int(OrderState.QUEUE),
        MatchQty=1,
    )
    match = DstarApiMatchField(
        OrderId=200,
        SystemNo="SYS001",
        MatchQty=2,
        MatchId=300,
        Direct=int(Direction.BUY),
        Offset=int(Offset.OPEN),
        Hedge=int(Hedge.SPECULATE),
        OrderType=int(OrderType.LIMIT),
    )

    manager.on_rsp_order_insert(rsp)
    manager.on_rtn_order(order)
    manager.on_rtn_match(match)
    tracked = manager.get("biz-1")

    assert tracked is not None
    assert tracked.order_id == 200
    assert tracked.system_no == "SYS001"
    assert tracked.order_state == int(OrderState.QUEUE)
    assert tracked.total_match_qty == 3
    assert tracked.status == "matched"


def test_order_state_manager_rejects_duplicate_client_order_id() -> None:
    """The same logical client_order_id must not be submitted twice."""

    manager = OrderStateManager()

    manager.register_submission("biz-1", 100)
    with pytest.raises(ValueError, match="duplicate client_order_id"):
        manager.register_submission("biz-1", 101)


def test_order_state_manager_recovers_client_order_ids_from_journal(tmp_path) -> None:
    """A restarted process should recover recent client_order_id values."""

    journal = OrderJournal(tmp_path / "order_journal.jsonl")
    journal.append("order_submit", client_order_id="biz-1", client_req_id=100)

    manager = OrderStateManager.from_journal(journal)

    assert "biz-1" in manager.known_client_order_ids
    with pytest.raises(ValueError, match="duplicate client_order_id"):
        manager.register_submission("biz-1", 101)


def test_order_journal_writes_json_without_sensitive_fields(tmp_path) -> None:
    """Journal records should be JSONL and should not include credentials."""

    path = tmp_path / "order_journal.jsonl"
    journal = OrderJournal(path)

    journal.append(
        "order_submit",
        client_order_id="biz-1",
        client_req_id=100,
        payload={
            "Direct": int(Direction.BUY),
            "Offset": int(Offset.OPEN),
            "Hedge": int(Hedge.SPECULATE),
            "OrderType": int(OrderType.LIMIT),
            "ValidType": int(ValidType.GFD),
            "UdpAuthCode": 123456,
        },
    )
    record = json.loads(path.read_text(encoding="utf-8").strip())

    assert record["event_type"] == "order_submit"
    assert record["client_order_id"] == "biz-1"
    assert "password" not in json.dumps(record).casefold()
    assert "UdpAuthCode" not in record["payload"]


def test_order_journal_redacts_sensitive_dataclass_fields(tmp_path) -> None:
    """Dataclass payloads should be recursively filtered before JSONL writes."""

    path = tmp_path / "order_journal.jsonl"
    journal = OrderJournal(path)
    request = DstarApiReqOrderInsertField(
        Direct=int(Direction.BUY),
        Offset=int(Offset.OPEN),
        Hedge=int(Hedge.SPECULATE),
        OrderType=int(OrderType.LIMIT),
        ValidType=int(ValidType.GFD),
        ContractNo="GC2608",
        OrderQty=1,
        ClientReqId=100,
        UdpAuthCode=123456,
    )

    journal.append("order_submit", client_order_id="biz-1", client_req_id=100, payload=request)
    record = json.loads(path.read_text(encoding="utf-8").strip())

    assert "UdpAuthCode" not in record["payload"]
