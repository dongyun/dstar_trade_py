"""Tests for adapter-facing DstarOrderMapper and lifecycle state machine."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from dstar_trade_py import OrderJournal
from dstar_trade_py.enums import Direction, Hedge, Offset, OrderState, OrderType, ValidType
from dstar_trade_py.fields import DstarApiMatchField, DstarApiOrderField, DstarApiRspOrderInsertField
from dstar_trade_py.order_mapper import DstarOrderLifecycleStatus, DstarOrderMapper


def make_mapper(tmp_path) -> DstarOrderMapper:
    return DstarOrderMapper(journal=OrderJournal(tmp_path / "order_journal.jsonl"))


def make_order(**overrides):
    data = {
        "client_order_id": "C-001",
        "side": "BUY",
        "order_type": "LIMIT",
        "quantity": 3,
        "price": 2400.5,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_mapper_converts_nautilus_like_limit_order_to_req_order_insert(tmp_path) -> None:
    """A Nautilus-like order should map to the official Dstar request fields."""

    mapper = make_mapper(tmp_path)

    mapped = mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )

    assert mapped.client_order_id == "C-001"
    assert mapped.request_id == 100
    assert mapped.request.ClientReqId == 100
    assert mapped.request.Direct == int(Direction.BUY)
    assert mapped.request.Offset == int(Offset.OPEN)
    assert mapped.request.Hedge == int(Hedge.SPECULATE)
    assert mapped.request.OrderType == int(OrderType.LIMIT)
    assert mapped.request.ValidType == int(ValidType.GFD)
    assert mapped.request.ContractNo == "GC2608"
    assert mapped.request.OrderQty == 3
    assert mapped.request.OrderPrice == 2400.5

    state = mapper.get_by_client_order_id("C-001")
    assert state is not None
    assert state.status == DstarOrderLifecycleStatus.CREATED


def test_req_order_insert_return_zero_only_moves_to_submitted(tmp_path) -> None:
    """ReqOrderInsert ret=0 must not be treated as Accepted."""

    mapper = make_mapper(tmp_path)
    mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )

    state = mapper.mark_submitted(request_id=100, local_return_code=0)

    assert state.status == DstarOrderLifecycleStatus.SUBMITTED
    assert state.exchange_order_id == 0


def test_rsp_order_insert_accepts_and_maps_exchange_order_id(tmp_path) -> None:
    """OnRspOrderInsert ErrCode=0 should transition to Accepted."""

    mapper = make_mapper(tmp_path)
    mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.mark_submitted(request_id=100, local_return_code=0)

    state = mapper.on_rsp_order_insert(
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0)
    )

    assert state.status == DstarOrderLifecycleStatus.ACCEPTED
    assert state.exchange_order_id == 9001
    assert mapper.get_by_request_id(100) is state
    assert mapper.get_by_exchange_order_id(9001) is state


def test_rsp_order_insert_rejects_on_error(tmp_path) -> None:
    """OnRspOrderInsert ErrCode!=0 is a trusted rejection signal."""

    mapper = make_mapper(tmp_path)
    mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.mark_submitted(request_id=100, local_return_code=0)

    state = mapper.on_rsp_order_insert(
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=0, ErrCode=20039)
    )

    assert state.status == DstarOrderLifecycleStatus.REJECTED
    assert state.last_error_code == 20039


def test_rtn_order_drives_cancelled_state(tmp_path) -> None:
    """OnRtnOrder deleted states should transition to Cancelled."""

    mapper = make_mapper(tmp_path)
    mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.on_rsp_order_insert(DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0))

    state = mapper.on_rtn_order(
        DstarApiOrderField(
            OrderId=9001,
            SystemNo="SYS001",
            OrderState=int(OrderState.DELETED),
            MatchQty=0,
        )
    )

    assert state.status == DstarOrderLifecycleStatus.CANCELLED
    assert state.system_no == "SYS001"


def test_rtn_match_drives_partial_and_full_fill_with_deduplication(tmp_path) -> None:
    """OnRtnMatch should be idempotent by match id and drive fill states."""

    mapper = make_mapper(tmp_path)
    mapper.map_order_to_insert_request(
        make_order(quantity=3),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.on_rsp_order_insert(DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0))

    first = DstarApiMatchField(OrderId=9001, MatchId=1, MatchQty=1, MatchPrice=2400.0)
    state = mapper.on_rtn_match(first)
    assert state.status == DstarOrderLifecycleStatus.PARTIALLY_FILLED
    assert state.filled_qty == 1

    duplicate = mapper.on_rtn_match(first)
    assert duplicate.filled_qty == 1

    final = mapper.on_rtn_match(
        DstarApiMatchField(OrderId=9001, MatchId=2, MatchQty=2, MatchPrice=2403.0)
    )

    assert final.status == DstarOrderLifecycleStatus.FILLED
    assert final.filled_qty == 3
    assert final.avg_fill_price == pytest.approx(2402.0)


def test_mapper_rejects_duplicate_client_order_id_from_live_state(tmp_path) -> None:
    """The mapper should enforce client_order_id idempotency before native submission."""

    mapper = make_mapper(tmp_path)
    kwargs = {
        "account_index": 1,
        "contract_index": 2,
        "contract_no": "GC2608",
    }

    mapper.map_order_to_insert_request(make_order(), request_id=100, **kwargs)

    with pytest.raises(ValueError, match="duplicate client_order_id"):
        mapper.map_order_to_insert_request(make_order(), request_id=101, **kwargs)


def test_mapper_replays_journal_for_backtest_or_recovery(tmp_path) -> None:
    """A fresh mapper should recover lifecycle and idempotency state from journal."""

    path = tmp_path / "order_journal.jsonl"
    mapper = DstarOrderMapper(journal=OrderJournal(path))
    mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.mark_submitted(request_id=100, local_return_code=0)
    mapper.on_rsp_order_insert(DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0))
    mapper.on_rtn_match(DstarApiMatchField(OrderId=9001, MatchId=1, MatchQty=3, MatchPrice=2400.0))

    replayed = DstarOrderMapper(journal=OrderJournal(path))
    state = replayed.get_by_client_order_id("C-001")

    assert state is not None
    assert state.status == DstarOrderLifecycleStatus.FILLED
    assert state.request_id == 100
    assert state.exchange_order_id == 9001
    assert state.filled_qty == 3
    with pytest.raises(ValueError, match="duplicate client_order_id"):
        replayed.map_order_to_insert_request(
            make_order(),
            account_index=1,
            contract_index=2,
            contract_no="GC2608",
            request_id=101,
        )
