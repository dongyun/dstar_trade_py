"""Tests for DstarRecoveryEngine startup/reconnect recovery."""

from __future__ import annotations

from dstar_trade_py import OrderJournal
from dstar_trade_py.enums import OrderState
from dstar_trade_py.event_adapter import DstarEventAdapter, DstarNautilusEventType
from dstar_trade_py.fields import DstarApiFundField, DstarApiMatchField, DstarApiOrderField, DstarApiPositionField
from dstar_trade_py.order_mapper import DstarOrderLifecycleStatus, DstarOrderMapper
from dstar_trade_py.recovery_engine import DstarRecoveryEngine


class FullQueryClient:
    """Fake client with order, trade, position, and fund query methods."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def query_order(self, timeout: float = 5):
        self.calls.append(f"query_order:{timeout}")
        return [
            DstarApiOrderField(
                OrderId=9001,
                SystemNo="SYS001",
                OrderState=int(OrderState.QUEUE),
                OrderQty=3,
                MatchQty=0,
            )
        ]

    def query_trade(self, timeout: float = 5):
        self.calls.append(f"query_trade:{timeout}")
        return [
            DstarApiMatchField(
                OrderId=9001,
                SystemNo="SYS001",
                MatchId=7001,
                MatchQty=1,
                MatchPrice=2400.0,
            )
        ]

    def query_position(self, timeout: float = 5):
        self.calls.append(f"query_position:{timeout}")
        return [
            DstarApiPositionField(
                AccountNo="ACC001",
                ContractNo="GC2608",
                TodayBuyQty=1,
                SerialId=10,
            )
        ]

    def query_fund(self, timeout: float = 5):
        self.calls.append(f"query_fund:{timeout}")
        return DstarApiFundField(AccountNo="ACC001", Equity=100000.0, Avail=90000.0)


class FundPositionOnlyClient:
    """Current dstar_trade_py-like client surface without query_order/query_trade."""

    def query_position(self, timeout: float = 5):
        return [DstarApiPositionField(AccountNo="ACC001", ContractNo="GC2608", TodayBuyQty=1)]

    def query_fund(self, timeout: float = 5):
        return DstarApiFundField(AccountNo="ACC001", Equity=100000.0, Avail=90000.0)


def make_engine(tmp_path, client):
    journal = OrderJournal(tmp_path / "order_journal.jsonl")
    mapper = DstarOrderMapper(journal=journal)
    adapter = DstarEventAdapter(order_mapper=mapper, journal=journal)
    engine = DstarRecoveryEngine(client=client, order_mapper=mapper, event_adapter=adapter, query_timeout=7)
    return engine, mapper, adapter, journal


def test_recovery_queries_order_trade_position_fund_and_rebuilds_state(tmp_path) -> None:
    """Recovery should run all queries and rebuild order, position, and account events."""

    client = FullQueryClient()
    engine, mapper, _, _ = make_engine(tmp_path, client)

    result = engine.recover()

    assert client.calls == [
        "query_order:7.0",
        "query_trade:7.0",
        "query_position:7.0",
        "query_fund:7.0",
    ]
    assert [event.event_type for event in result.events] == [
        DstarNautilusEventType.ORDER_ACCEPTED,
        DstarNautilusEventType.ORDER_FILLED,
        DstarNautilusEventType.POSITION_UPDATED,
        DstarNautilusEventType.ACCOUNT_STATE,
    ]
    state = mapper.get_by_exchange_order_id(9001)
    assert state is not None
    assert state.client_order_id == "unknown-order-9001"
    assert state.filled_qty == 1
    assert state.status == DstarOrderLifecycleStatus.PARTIALLY_FILLED
    assert result.positions[0].ContractNo == "GC2608"
    assert result.fund is not None
    assert result.fund.Avail == 90000.0


def test_recovery_deduplicates_trade_id_from_journal_on_restart(tmp_path) -> None:
    """A trade already emitted before restart must not produce another fill event."""

    client = FullQueryClient()
    engine, _, _, journal = make_engine(tmp_path, client)
    first = engine.recover()

    restarted_mapper = DstarOrderMapper(journal=journal)
    restarted_adapter = DstarEventAdapter(order_mapper=restarted_mapper, journal=journal)
    restarted = DstarRecoveryEngine(
        client=FullQueryClient(),
        order_mapper=restarted_mapper,
        event_adapter=restarted_adapter,
        query_timeout=7,
    )
    second = restarted.recover()

    assert [event.event_type for event in first.events].count(DstarNautilusEventType.ORDER_FILLED) == 1
    assert DstarNautilusEventType.ORDER_FILLED not in [event.event_type for event in second.events]
    assert restarted_mapper.get_by_exchange_order_id(9001).filled_qty == 1


def test_recovery_marks_missing_order_trade_queries_as_skipped(tmp_path) -> None:
    """Current SDK clients without query_order/query_trade should still recover fund/position."""

    engine, _, _, _ = make_engine(tmp_path, FundPositionOnlyClient())

    result = engine.recover()

    assert result.skipped_capabilities == ["query_order", "query_trade"]
    assert [event.event_type for event in result.events] == [
        DstarNautilusEventType.POSITION_UPDATED,
        DstarNautilusEventType.ACCOUNT_STATE,
    ]


def test_recovery_processes_pending_callback_queue_after_queries(tmp_path) -> None:
    """Queued callback events should be drained after query recovery."""

    engine, mapper, adapter, _ = make_engine(tmp_path, FundPositionOnlyClient())
    adapter.on_event(
        "rsp_qry_order",
        DstarApiOrderField(
            OrderId=9002,
            SystemNo="SYS002",
            OrderState=int(OrderState.FILLED),
            OrderQty=2,
            MatchQty=2,
        ),
    )

    result = engine.recover()

    assert DstarNautilusEventType.ORDER_UPDATED in [event.event_type for event in result.events]
    state = mapper.get_by_exchange_order_id(9002)
    assert state is not None
    assert state.status == DstarOrderLifecycleStatus.FILLED
