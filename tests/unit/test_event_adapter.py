"""Tests for DstarEventAdapter callback conversion and deduplication."""

from __future__ import annotations

from types import SimpleNamespace

from dstar_trade_py import OrderJournal
from dstar_trade_py.enums import OrderState
from dstar_trade_py.event_adapter import DstarEventAdapter, DstarNautilusEventType
from dstar_trade_py.fields import (
    DstarApiFundField,
    DstarApiMatchField,
    DstarApiOrderField,
    DstarApiPositionField,
    DstarApiRspOrderInsertField,
)
from dstar_trade_py.order_mapper import DstarOrderLifecycleStatus, DstarOrderMapper


def make_stack(tmp_path):
    journal = OrderJournal(tmp_path / "order_journal.jsonl")
    mapper = DstarOrderMapper(journal=journal)
    adapter = DstarEventAdapter(order_mapper=mapper, journal=journal)
    return mapper, adapter, journal


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


def register_local_order(mapper: DstarOrderMapper) -> None:
    mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.mark_submitted(request_id=100, local_return_code=0)


def test_rsp_order_insert_converts_to_order_accepted(tmp_path) -> None:
    """OnRspOrderInsert ErrCode=0 should produce OrderAccepted."""

    mapper, adapter, _ = make_stack(tmp_path)
    register_local_order(mapper)

    adapter.on_event(
        "rsp_order_insert",
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0),
    )

    events = adapter.process_all()

    assert [event.event_type for event in events] == [DstarNautilusEventType.ORDER_ACCEPTED]
    assert events[0].client_order_id == "C-001"
    assert events[0].request_id == 100
    assert events[0].exchange_order_id == 9001


def test_rsp_order_insert_rejects_on_error(tmp_path) -> None:
    """OnRspOrderInsert ErrCode!=0 should produce OrderRejected."""

    mapper, adapter, _ = make_stack(tmp_path)
    register_local_order(mapper)

    events = adapter.process_event(
        "rsp_order_insert",
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=0, ErrCode=20039),
    )

    assert len(events) == 1
    assert events[0].event_type == DstarNautilusEventType.ORDER_REJECTED
    assert events[0].status == DstarOrderLifecycleStatus.REJECTED.value


def test_duplicate_callbacks_are_suppressed_by_journal(tmp_path) -> None:
    """A duplicate callback should not emit twice, including after adapter restart."""

    mapper, adapter, journal = make_stack(tmp_path)
    register_local_order(mapper)
    payload = DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0)

    first = adapter.process_event("rsp_order_insert", payload)
    second = adapter.process_event("rsp_order_insert", payload)
    restarted = DstarEventAdapter(order_mapper=DstarOrderMapper(journal=journal), journal=journal)
    third = restarted.process_event("rsp_order_insert", payload)

    assert len(first) == 1
    assert second == []
    assert third == []


def test_out_of_order_match_before_rsp_insert_is_recovered_and_merged(tmp_path) -> None:
    """OnRtnMatch can arrive before OnRspOrderInsert and later merge into local order."""

    mapper, adapter, _ = make_stack(tmp_path)
    register_local_order(mapper)

    fill_events = adapter.process_event(
        "rtn_match",
        DstarApiMatchField(OrderId=9001, SystemNo="SYS001", MatchId=1, MatchQty=1, MatchPrice=2400.0),
    )
    rsp_events = adapter.process_event(
        "rsp_order_insert",
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0),
    )
    state = mapper.get_by_client_order_id("C-001")

    assert len(fill_events) == 1
    assert fill_events[0].event_type == DstarNautilusEventType.ORDER_FILLED
    assert fill_events[0].client_order_id.startswith("unknown-order-")
    assert rsp_events == []
    assert state is not None
    assert state.exchange_order_id == 9001
    assert state.filled_qty == 1
    assert state.status == DstarOrderLifecycleStatus.PARTIALLY_FILLED
    assert mapper.get_by_client_order_id("unknown-order-9001") is None


def test_out_of_order_order_update_before_rsp_insert_is_recovered_and_merged(tmp_path) -> None:
    """OnRtnOrder before OnRspOrderInsert should not crash and should merge later."""

    mapper, adapter, _ = make_stack(tmp_path)
    register_local_order(mapper)

    unknown_events = adapter.process_event(
        "rtn_order",
        DstarApiOrderField(
            OrderId=9001,
            SystemNo="SYS001",
            OrderState=int(OrderState.QUEUE),
            OrderQty=3,
            MatchQty=0,
        ),
    )
    rsp_events = adapter.process_event(
        "rsp_order_insert",
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0),
    )
    state = mapper.get_by_client_order_id("C-001")

    assert len(unknown_events) == 1
    assert unknown_events[0].event_type == DstarNautilusEventType.ORDER_ACCEPTED
    assert unknown_events[0].client_order_id == "unknown-order-9001"
    assert len(rsp_events) == 1
    assert rsp_events[0].event_type == DstarNautilusEventType.ORDER_ACCEPTED
    assert rsp_events[0].client_order_id == "C-001"
    assert state is not None
    assert state.exchange_order_id == 9001
    assert state.status == DstarOrderLifecycleStatus.ACCEPTED


def test_match_duplicate_is_suppressed(tmp_path) -> None:
    """The same OnRtnMatch should produce a single OrderFilled event."""

    mapper, adapter, _ = make_stack(tmp_path)
    register_local_order(mapper)
    adapter.process_event(
        "rsp_order_insert",
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0),
    )
    payload = DstarApiMatchField(OrderId=9001, MatchId=7, MatchQty=1, MatchPrice=2401.0)

    first = adapter.process_event("rtn_match", payload)
    second = adapter.process_event("rtn_match", payload)

    assert len(first) == 1
    assert first[0].event_type == DstarNautilusEventType.ORDER_FILLED
    assert second == []
    assert mapper.get_by_client_order_id("C-001").filled_qty == 1


def test_query_aliases_convert_order_and_trade_callbacks(tmp_path) -> None:
    """Optional query aliases should map like snapshot order/trade callbacks."""

    mapper, adapter, _ = make_stack(tmp_path)

    order_events = adapter.process_event(
        "rsp_qry_order",
        DstarApiOrderField(
            OrderId=9001,
            SystemNo="SYS001",
            OrderState=int(OrderState.QUEUE),
            OrderQty=2,
        ),
    )
    trade_events = adapter.process_event(
        "rsp_qry_trade",
        DstarApiMatchField(OrderId=9001, SystemNo="SYS001", MatchId=9, MatchQty=2, MatchPrice=2402.0),
    )

    assert [event.event_type for event in order_events] == [DstarNautilusEventType.ORDER_ACCEPTED]
    assert [event.event_type for event in trade_events] == [DstarNautilusEventType.ORDER_FILLED]
    assert mapper.get_by_exchange_order_id(9001).status == DstarOrderLifecycleStatus.FILLED


def test_position_and_account_callbacks_convert_to_state_events(tmp_path) -> None:
    """Position/fund callbacks should produce Nautilus-style account events."""

    _, adapter, _ = make_stack(tmp_path)

    position_events = adapter.process_event(
        "rsp_qry_position",
        {
            "data": DstarApiPositionField(
                AccountNo="ACC001",
                ContractNo="GC2608",
                TodayBuyQty=2,
                TodaySellQty=0,
                SerialId=10,
            ).to_dict(),
            "last": False,
        },
    )
    account_events = adapter.process_event(
        "rsp_qry_fund",
        DstarApiFundField(AccountNo="ACC001", Equity=100000.0, Avail=90000.0, Margin=10000.0),
    )

    assert [event.event_type for event in position_events] == [DstarNautilusEventType.POSITION_UPDATED]
    assert position_events[0].payload["ContractNo"] == "GC2608"
    assert [event.event_type for event in account_events] == [DstarNautilusEventType.ACCOUNT_STATE]
    assert account_events[0].payload["Avail"] == 90000.0
