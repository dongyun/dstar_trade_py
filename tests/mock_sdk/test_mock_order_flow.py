"""Mock-SDK order flow tests for the Dstar execution adapter layer."""

from __future__ import annotations

from types import SimpleNamespace

from dstar_trade_py import OrderJournal
from dstar_trade_py.enums import OrderState
from dstar_trade_py.event_adapter import DstarEventAdapter, DstarNautilusEventType
from dstar_trade_py.fields import DstarApiMatchField, DstarApiOrderField, DstarApiRspOrderInsertField
from dstar_trade_py.order_mapper import DstarOrderLifecycleStatus, DstarOrderMapper


class MockDstarTradeClient:
    """Mock DstarTradeClient that records order requests and never sends them."""

    def __init__(self) -> None:
        self.inserted_orders: list[dict[str, object]] = []

    def insert_limit_order(self, **kwargs) -> int:
        self.inserted_orders.append(dict(kwargs))
        return 0


def make_order() -> SimpleNamespace:
    return SimpleNamespace(
        client_order_id="MOCK-001",
        side="BUY",
        order_type="LIMIT",
        quantity=2,
        price=2400.5,
    )


def test_mock_dstar_order_flow_uses_callbacks_as_source_of_truth(tmp_path) -> None:
    """ReqOrderInsert ret=0 should not accept/fill until mock SPI callbacks arrive."""

    journal = OrderJournal(tmp_path / "order_journal.jsonl")
    mapper = DstarOrderMapper(journal=journal)
    adapter = DstarEventAdapter(order_mapper=mapper, journal=journal)
    client = MockDstarTradeClient()

    mapped = mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    ret = client.insert_limit_order(**mapped.request.to_dict(), client_order_id=mapped.client_order_id)
    state = mapper.mark_submitted(request_id=mapped.request_id, local_return_code=ret)

    assert ret == 0
    assert state.status == DstarOrderLifecycleStatus.SUBMITTED
    assert client.inserted_orders[0]["ClientReqId"] == 100

    accepted = adapter.process_event(
        "rsp_order_insert",
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=9001, ErrCode=0),
    )
    queued = adapter.process_event(
        "rtn_order",
        DstarApiOrderField(
            OrderId=9001,
            SystemNo="SYS001",
            OrderState=int(OrderState.QUEUE),
            OrderQty=2,
            MatchQty=0,
        ),
    )
    filled = adapter.process_event(
        "rtn_match",
        DstarApiMatchField(
            OrderId=9001,
            SystemNo="SYS001",
            MatchId=7001,
            MatchQty=2,
            MatchPrice=2401.0,
        ),
    )

    assert [event.event_type for event in accepted] == [DstarNautilusEventType.ORDER_ACCEPTED]
    assert [event.event_type for event in queued] == [DstarNautilusEventType.ORDER_UPDATED]
    assert [event.event_type for event in filled] == [DstarNautilusEventType.ORDER_FILLED]
    assert mapper.get_by_client_order_id("MOCK-001").status == DstarOrderLifecycleStatus.FILLED


def test_mock_spi_callback_reject_flow(tmp_path) -> None:
    """Mock SPI rejection should produce OrderRejected without any live request."""

    journal = OrderJournal(tmp_path / "order_journal.jsonl")
    mapper = DstarOrderMapper(journal=journal)
    adapter = DstarEventAdapter(order_mapper=mapper, journal=journal)

    mapped = mapper.map_order_to_insert_request(
        make_order(),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        request_id=100,
    )
    mapper.mark_submitted(request_id=mapped.request_id, local_return_code=0)

    rejected = adapter.process_event(
        "rsp_order_insert",
        DstarApiRspOrderInsertField(ClientReqId=100, OrderId=0, ErrCode=20039),
    )

    assert [event.event_type for event in rejected] == [DstarNautilusEventType.ORDER_REJECTED]
    assert mapper.get_by_client_order_id("MOCK-001").status == DstarOrderLifecycleStatus.REJECTED
