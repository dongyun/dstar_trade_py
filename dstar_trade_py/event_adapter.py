"""Convert Dstar SPI callback events into Nautilus-style execution events."""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .fields import DstarApiFundField, DstarApiMatchField, DstarApiOrderField, DstarApiPositionField
from .fields import DstarApiRspOrderInsertField
from .order_management import DEFAULT_ORDER_JOURNAL_PATH, OrderJournal
from .order_mapper import DstarOrderLifecycle, DstarOrderLifecycleStatus, DstarOrderMapper


class DstarNautilusEventType(StrEnum):
    """Nautilus event names produced by the adapter layer."""

    ORDER_ACCEPTED = "OrderAccepted"
    ORDER_REJECTED = "OrderRejected"
    ORDER_UPDATED = "OrderUpdated"
    ORDER_FILLED = "OrderFilled"
    POSITION_UPDATED = "PositionUpdated"
    ACCOUNT_STATE = "AccountStateEvent"


@dataclass(frozen=True, slots=True)
class DstarCallbackEnvelope:
    """Thread-safe queue item for one Dstar callback."""

    event_name: str
    payload: Any
    received_ts: float = field(default_factory=time.time)


@dataclass(frozen=True, slots=True)
class DstarNautilusEvent:
    """Nautilus-style event payload produced without importing NautilusTrader."""

    event_type: DstarNautilusEventType
    event_key: str
    client_order_id: str = ""
    request_id: int = 0
    exchange_order_id: int = 0
    status: str = ""
    quantity: int = 0
    filled_qty: int = 0
    last_qty: int = 0
    last_px: float = 0.0
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class _StateSnapshot:
    status: DstarOrderLifecycleStatus | None
    filled_qty: int


class DstarEventAdapter:
    """Queue, deduplicate, and convert Dstar SPI events into Nautilus-style events."""

    ORDER_EVENT_NAMES = {
        "rsp_order_insert",
        "rtn_order",
        "rsp_order",
        "rsp_qry_order",
        "rtn_match",
        "rsp_match",
        "rsp_qry_trade",
    }

    def __init__(
        self,
        *,
        order_mapper: DstarOrderMapper,
        journal: OrderJournal | None = None,
        journal_path: str | None = None,
        event_queue: queue.Queue[DstarCallbackEnvelope] | None = None,
    ) -> None:
        self.order_mapper = order_mapper
        self.journal = journal or order_mapper.journal or OrderJournal(journal_path or DEFAULT_ORDER_JOURNAL_PATH)
        self._queue: queue.Queue[DstarCallbackEnvelope] = event_queue or queue.Queue()
        self._lock = threading.RLock()
        self._seen_callback_keys: set[str] = set()
        self._emitted_event_keys: set[str] = set()
        self._load_dedupe_keys()

    def on_event(self, event_name: str, payload: Any) -> None:
        """Callback-thread-safe enqueue entrypoint."""

        self._queue.put(DstarCallbackEnvelope(event_name=event_name, payload=payload))

    def process_next(self, timeout: float | None = None) -> list[DstarNautilusEvent]:
        """Process one queued callback and return zero or more Nautilus-style events."""

        envelope = self._queue.get(timeout=timeout) if timeout is not None else self._queue.get_nowait()
        return self.process_event(envelope.event_name, envelope.payload)

    def process_all(self, *, max_events: int | None = None) -> list[DstarNautilusEvent]:
        """Drain currently queued callbacks."""

        events: list[DstarNautilusEvent] = []
        processed = 0
        while max_events is None or processed < max_events:
            try:
                events.extend(self.process_next())
            except queue.Empty:
                break
            processed += 1
        return events

    def process_event(self, event_name: str, payload: Any) -> list[DstarNautilusEvent]:
        """Convert a single callback payload."""

        callback_key = _callback_key(event_name, payload)
        with self._lock:
            if callback_key in self._seen_callback_keys:
                return []
            self._seen_callback_keys.add(callback_key)
            self.journal.append("dstar_callback_seen", event_key=callback_key, callback_name=event_name)

        if event_name == "rsp_order_insert":
            return self._handle_rsp_order_insert(payload)
        if event_name in {"rtn_order", "rsp_order", "rsp_qry_order"}:
            return self._handle_order_update(payload)
        if event_name in {"rtn_match", "rsp_match", "rsp_qry_trade"}:
            return self._handle_match(payload)
        if event_name in {"rsp_position", "rsp_qry_position"}:
            return self._handle_position(payload)
        if event_name in {"rsp_fund", "rsp_qry_fund"}:
            return self._handle_fund(payload)
        return []

    def _handle_rsp_order_insert(self, payload: Any) -> list[DstarNautilusEvent]:
        response = _coerce_rsp_order_insert(payload)
        before = _snapshot(self.order_mapper.get_by_request_id(response.ClientReqId))
        state = self.order_mapper.on_rsp_order_insert(response)
        if response.ErrCode == 0:
            if state.status != DstarOrderLifecycleStatus.ACCEPTED or before.status == DstarOrderLifecycleStatus.ACCEPTED:
                return []
            return self._emit_order_event(DstarNautilusEventType.ORDER_ACCEPTED, state, payload=response)
        return self._emit_order_event(DstarNautilusEventType.ORDER_REJECTED, state, payload=response)

    def _handle_order_update(self, payload: Any) -> list[DstarNautilusEvent]:
        order = _coerce_order(payload)
        before = _snapshot(self.order_mapper.get_by_exchange_order_id(order.OrderId))
        state = self.order_mapper.on_rtn_order(order)
        if state.status == DstarOrderLifecycleStatus.REJECTED:
            return self._emit_order_event(DstarNautilusEventType.ORDER_REJECTED, state, payload=order)
        if (
            before.status == state.status
            and before.filled_qty == state.filled_qty
            and state.status != DstarOrderLifecycleStatus.ACCEPTED
        ):
            return []
        event_type = (
            DstarNautilusEventType.ORDER_ACCEPTED
            if state.status == DstarOrderLifecycleStatus.ACCEPTED and before.status != state.status
            else DstarNautilusEventType.ORDER_UPDATED
        )
        return self._emit_order_event(event_type, state, payload=order)

    def _handle_match(self, payload: Any) -> list[DstarNautilusEvent]:
        match = _coerce_match(payload)
        state_before = self.order_mapper.get_by_exchange_order_id(match.OrderId)
        before_fills = set(state_before.match_ids) if state_before is not None else set()
        state = self.order_mapper.on_rtn_match(match)
        match_key = _match_key(match)
        if match_key in before_fills:
            return []
        return self._emit_order_event(DstarNautilusEventType.ORDER_FILLED, state, payload=match, match=match)

    def _handle_position(self, payload: Any) -> list[DstarNautilusEvent]:
        position = _extract_query_data(payload)
        if position is None:
            return []
        field = position if isinstance(position, DstarApiPositionField) else DstarApiPositionField.from_dict(position)
        event_key = f"position:{field.AccountNo}:{field.ContractNo}:{field.SerialId}:{field.TodayBuyQty}:{field.TodaySellQty}"
        return self._emit_generic_event(DstarNautilusEventType.POSITION_UPDATED, event_key, field.to_dict())

    def _handle_fund(self, payload: Any) -> list[DstarNautilusEvent]:
        fund = payload if isinstance(payload, DstarApiFundField) else DstarApiFundField.from_dict(payload)
        event_key = f"account:{fund.AccountNo}:{fund.Equity}:{fund.Avail}:{fund.Margin}:{fund.Frozen}"
        return self._emit_generic_event(DstarNautilusEventType.ACCOUNT_STATE, event_key, fund.to_dict())

    def _emit_order_event(
        self,
        event_type: DstarNautilusEventType,
        state: DstarOrderLifecycle,
        *,
        payload: Any,
        match: DstarApiMatchField | None = None,
    ) -> list[DstarNautilusEvent]:
        raw_payload = _plain_payload(payload)
        event_key = _event_key(event_type, state, raw_payload, match=match)
        event = DstarNautilusEvent(
            event_type=event_type,
            event_key=event_key,
            client_order_id=state.client_order_id,
            request_id=state.request_id,
            exchange_order_id=state.exchange_order_id,
            status=state.status.value,
            quantity=state.order_qty,
            filled_qty=state.filled_qty,
            last_qty=match.MatchQty if match is not None else 0,
            last_px=match.MatchPrice if match is not None else 0.0,
            payload=raw_payload,
        )
        return self._record_emitted_event(event)

    def _emit_generic_event(
        self,
        event_type: DstarNautilusEventType,
        event_key: str,
        payload: dict[str, Any],
    ) -> list[DstarNautilusEvent]:
        event = DstarNautilusEvent(event_type=event_type, event_key=f"{event_type.value}:{event_key}", payload=payload)
        return self._record_emitted_event(event)

    def _record_emitted_event(self, event: DstarNautilusEvent) -> list[DstarNautilusEvent]:
        with self._lock:
            if event.event_key in self._emitted_event_keys:
                return []
            self._emitted_event_keys.add(event.event_key)
            self.journal.append(
                "dstar_event_emitted",
                event_key=event.event_key,
                nautilus_event_type=event.event_type.value,
                client_order_id=event.client_order_id,
                request_id=event.request_id,
                exchange_order_id=event.exchange_order_id,
                payload=event.payload,
            )
            return [event]

    def _load_dedupe_keys(self) -> None:
        for record in self.journal.read_records():
            event_key = record.get("event_key")
            if not isinstance(event_key, str):
                continue
            if record.get("event_type") == "dstar_callback_seen":
                self._seen_callback_keys.add(event_key)
            elif record.get("event_type") == "dstar_event_emitted":
                self._emitted_event_keys.add(event_key)


def _snapshot(state: DstarOrderLifecycle | None) -> _StateSnapshot:
    if state is None:
        return _StateSnapshot(status=None, filled_qty=0)
    return _StateSnapshot(status=state.status, filled_qty=state.filled_qty)


def _coerce_rsp_order_insert(value: Any) -> DstarApiRspOrderInsertField:
    return value if isinstance(value, DstarApiRspOrderInsertField) else DstarApiRspOrderInsertField.from_dict(value)


def _coerce_order(value: Any) -> DstarApiOrderField:
    return value if isinstance(value, DstarApiOrderField) else DstarApiOrderField.from_dict(value)


def _coerce_match(value: Any) -> DstarApiMatchField:
    return value if isinstance(value, DstarApiMatchField) else DstarApiMatchField.from_dict(value)


def _plain_payload(payload: Any) -> dict[str, Any]:
    if hasattr(payload, "to_dict"):
        return payload.to_dict()
    if isinstance(payload, Mapping):
        return dict(payload)
    return {"value": payload}


def _extract_query_data(payload: Any) -> Any:
    if isinstance(payload, Mapping) and "data" in payload:
        return payload.get("data")
    return payload


def _callback_key(event_name: str, payload: Any) -> str:
    raw = _plain_payload(_extract_query_data(payload) if event_name == "rsp_qry_position" else payload)
    if event_name == "rsp_order_insert":
        return f"{event_name}:{raw.get('ClientReqId', 0)}:{raw.get('OrderId', 0)}:{raw.get('ErrCode', 0)}"
    if event_name in {"rtn_order", "rsp_order", "rsp_qry_order"}:
        return (
            f"{event_name}:{raw.get('OrderId', 0)}:{raw.get('SystemNo', '')}:"
            f"{raw.get('OrderState', 0)}:{raw.get('MatchQty', 0)}:{raw.get('ErrCode', 0)}:"
            f"{raw.get('UpdateTime', '')}"
        )
    if event_name in {"rtn_match", "rsp_match", "rsp_qry_trade"}:
        return f"{event_name}:{_match_key(_coerce_match(raw))}"
    if event_name in {"rsp_position", "rsp_qry_position"}:
        return (
            f"{event_name}:{raw.get('AccountNo', '')}:{raw.get('ContractNo', '')}:"
            f"{raw.get('SerialId', 0)}:{raw.get('TodayBuyQty', 0)}:{raw.get('TodaySellQty', 0)}"
        )
    if event_name in {"rsp_fund", "rsp_qry_fund"}:
        return f"{event_name}:{raw.get('AccountNo', '')}:{raw.get('Equity', 0)}:{raw.get('Avail', 0)}"
    return f"{event_name}:{repr(sorted(raw.items()))}"


def _event_key(
    event_type: DstarNautilusEventType,
    state: DstarOrderLifecycle,
    payload: Mapping[str, Any],
    *,
    match: DstarApiMatchField | None,
) -> str:
    if match is not None:
        return f"{event_type.value}:{state.exchange_order_id}:{_match_key(match)}"
    return (
        f"{event_type.value}:{state.client_order_id}:{state.request_id}:"
        f"{state.exchange_order_id}:{state.status.value}:{payload.get('OrderState', '')}:"
        f"{payload.get('ErrCode', '')}:{state.filled_qty}"
    )


def _match_key(match: DstarApiMatchField) -> str:
    if match.MatchId:
        return f"match:{match.MatchId}"
    return f"order:{match.OrderId}:system:{match.SystemNo}:time:{match.MatchTime}:qty:{match.MatchQty}"


__all__ = [
    "DstarCallbackEnvelope",
    "DstarEventAdapter",
    "DstarNautilusEvent",
    "DstarNautilusEventType",
]
