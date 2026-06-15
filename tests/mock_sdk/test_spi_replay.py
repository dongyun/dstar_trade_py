"""Replay tests for SPI event streams."""

from __future__ import annotations

from dstar_trade_py import OrderJournal
from dstar_trade_py.enums import OrderState
from dstar_trade_py.event_adapter import DstarEventAdapter, DstarNautilusEventType
from dstar_trade_py.fields import DstarApiMatchField, DstarApiOrderField, DstarApiRspOrderInsertField
from dstar_trade_py.order_mapper import DstarOrderLifecycleStatus, DstarOrderMapper


def test_replay_spi_events_rebuilds_state_and_deduplicates_trades(tmp_path) -> None:
    """A replayed SPI stream should rebuild state without duplicate fill events."""

    path = tmp_path / "order_journal.jsonl"
    journal = OrderJournal(path)
    mapper = DstarOrderMapper(journal=journal)
    adapter = DstarEventAdapter(order_mapper=mapper, journal=journal)

    mapped = mapper.map_order_to_insert_request(
        {
            "client_order_id": "REPLAY-001",
            "side": "BUY",
            "order_type": "LIMIT",
            "quantity": 3,
            "price": 2400.5,
        },
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.mark_submitted(request_id=mapped.request_id, local_return_code=0)

    spi_events = [
        (
            "rtn_match",
            DstarApiMatchField(
                OrderId=9001,
                SystemNo="SYS001",
                MatchId=7001,
                MatchQty=1,
                MatchPrice=2400.0,
            ),
        ),
        ("rsp_order_insert", DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0)),
        (
            "rtn_order",
            DstarApiOrderField(
                OrderId=9001,
                SystemNo="SYS001",
                OrderState=int(OrderState.PARTIAL_FILL),
                OrderQty=3,
                MatchQty=1,
            ),
        ),
        (
            "rtn_match",
            DstarApiMatchField(
                OrderId=9001,
                SystemNo="SYS001",
                MatchId=7002,
                MatchQty=2,
                MatchPrice=2403.0,
            ),
        ),
        (
            "rtn_match",
            DstarApiMatchField(
                OrderId=9001,
                SystemNo="SYS001",
                MatchId=7002,
                MatchQty=2,
                MatchPrice=2403.0,
            ),
        ),
    ]

    emitted = []
    for event_name, payload in spi_events:
        emitted.extend(adapter.process_event(event_name, payload))

    restarted_mapper = DstarOrderMapper(journal=OrderJournal(path))
    restarted_adapter = DstarEventAdapter(order_mapper=restarted_mapper, journal=OrderJournal(path))
    replayed_again = []
    for event_name, payload in spi_events:
        replayed_again.extend(restarted_adapter.process_event(event_name, payload))

    fill_events = [event for event in emitted if event.event_type == DstarNautilusEventType.ORDER_FILLED]
    state = restarted_mapper.get_by_client_order_id("REPLAY-001")

    assert len(fill_events) == 2
    assert replayed_again == []
    assert state is not None
    assert state.exchange_order_id == 9001
    assert state.filled_qty == 3
    assert state.status == DstarOrderLifecycleStatus.FILLED
    assert state.match_ids == {"match:7001", "match:7002"}
