"""Adapter-facing order mapping and lifecycle state machine.

This module intentionally does not import NautilusTrader.  It accepts
Nautilus-like order objects by reading stable business fields through
duck-typing, so the real ExecutionAdapter can provide a thin compatibility
layer for the exact NautilusTrader version in use.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from .client import OrderRequestBuilder
from .enums import Direction, Hedge, Offset, OrderState, OrderType, ValidType
from .fields import (
    DstarApiMatchField,
    DstarApiOrderField,
    DstarApiReqOrderInsertField,
    DstarApiRspOrderInsertField,
)
from .order_management import DEFAULT_ORDER_JOURNAL_PATH, OrderJournal, RequestIdManager


class DstarOrderLifecycleStatus(StrEnum):
    """Adapter-level order lifecycle states."""

    CREATED = "Created"
    SUBMITTED = "Submitted"
    ACCEPTED = "Accepted"
    PARTIALLY_FILLED = "PartiallyFilled"
    FILLED = "Filled"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


TERMINAL_ORDER_STATUSES = {
    DstarOrderLifecycleStatus.FILLED,
    DstarOrderLifecycleStatus.REJECTED,
    DstarOrderLifecycleStatus.CANCELLED,
}


@dataclass(slots=True)
class DstarOrderLifecycle:
    """State tracked for one logical Nautilus client order."""

    client_order_id: str
    request_id: int
    order_qty: int
    status: DstarOrderLifecycleStatus = DstarOrderLifecycleStatus.CREATED
    exchange_order_id: int = 0
    system_no: str = ""
    filled_qty: int = 0
    avg_fill_price: float = 0.0
    last_order_state: int | None = None
    last_error_code: int | None = None
    local_return_code: int | None = None
    match_ids: set[str] = field(default_factory=set)
    created_ts: float = field(default_factory=time.time)
    updated_ts: float = field(default_factory=time.time)

    @property
    def remaining_qty(self) -> int:
        """Return the remaining quantity using callback-derived fills only."""

        return max(self.order_qty - self.filled_qty, 0)

    def to_journal_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible snapshot."""

        return {
            "client_order_id": self.client_order_id,
            "request_id": self.request_id,
            "client_req_id": self.request_id,
            "order_qty": self.order_qty,
            "status": self.status.value,
            "exchange_order_id": self.exchange_order_id,
            "order_id": self.exchange_order_id,
            "system_no": self.system_no,
            "filled_qty": self.filled_qty,
            "avg_fill_price": self.avg_fill_price,
            "last_order_state": self.last_order_state,
            "last_error_code": self.last_error_code,
            "local_return_code": self.local_return_code,
            "match_ids": sorted(self.match_ids),
            "updated_ts": self.updated_ts,
        }


@dataclass(frozen=True, slots=True)
class DstarMappedOrder:
    """Result of mapping a Nautilus order into a Dstar ReqOrderInsert field."""

    client_order_id: str
    request_id: int
    request: DstarApiReqOrderInsertField


class DstarOrderMapper:
    """Map Nautilus orders to Dstar requests and maintain callback-driven state."""

    def __init__(
        self,
        *,
        journal: OrderJournal | None = None,
        journal_path: str | None = None,
        request_id_manager: RequestIdManager | None = None,
    ) -> None:
        self.journal = journal or OrderJournal(journal_path or DEFAULT_ORDER_JOURNAL_PATH)
        self.request_id_manager = request_id_manager or RequestIdManager.from_journal(self.journal)
        self._lock = threading.RLock()
        self._orders_by_client_id: dict[str, DstarOrderLifecycle] = {}
        self._client_id_by_request_id: dict[int, str] = {}
        self._client_id_by_exchange_order_id: dict[int, str] = {}
        self._recover_from_journal()

    def map_order_to_insert_request(
        self,
        order: Any,
        *,
        account_index: int,
        contract_index: int | None = None,
        contract_no: str | None = None,
        client_order_id: str | None = None,
        request_id: int | None = None,
        offset: int | str | None = None,
        hedge: int | str | None = None,
        valid_type: int | str | None = None,
        seat_index: int = 0,
        min_qty: int = 1,
        reference: int = 0,
        udp_auth_code: int = 0,
    ) -> DstarMappedOrder:
        """Convert a Nautilus-like order into ``DstarApiReqOrderInsertField``.

        The method registers the order as ``Created`` before native submission.
        Calling it twice with the same ``client_order_id`` raises ``ValueError``.
        """

        logical_id = client_order_id or _string_value(_read(order, "client_order_id", "client_order_id"))
        if not logical_id:
            raise ValueError("client_order_id is required")

        resolved_contract_no = contract_no or _string_value(_read(order, "contract_no", "symbol"))
        if not resolved_contract_no:
            raise ValueError("contract_no is required")
        resolved_contract_index = _int_value(
            contract_index if contract_index is not None else _read(order, "contract_index"),
            "contract_index",
        )

        side = _direction_value(_read(order, "side", "order_side", "direction"))
        resolved_offset = _offset_value(offset if offset is not None else _read(order, "offset"), default=Offset.OPEN)
        resolved_hedge = _hedge_value(hedge if hedge is not None else _read(order, "hedge"), default=Hedge.SPECULATE)
        resolved_valid_type = _valid_type_value(
            valid_type if valid_type is not None else _read(order, "time_in_force", "valid_type"),
            default=ValidType.GFD,
        )
        order_type = _order_type_value(_read(order, "order_type", "type"), default=OrderType.LIMIT)
        qty = _quantity_value(_read(order, "quantity", "qty", "order_qty"), "quantity")
        price = _price_value(_read(order, "price", "limit_price"), order_type)

        with self._lock:
            if logical_id in self._orders_by_client_id:
                raise ValueError(f"duplicate client_order_id: {logical_id}")
            resolved_request_id = (
                self.request_id_manager.next_id()
                if request_id is None
                else self.request_id_manager.reserve(request_id)
            )
            request = DstarApiReqOrderInsertField(
                Direct=side,
                Offset=resolved_offset,
                Hedge=resolved_hedge,
                OrderType=order_type,
                ValidType=resolved_valid_type,
                SeatIndex=seat_index,
                AccountIndex=account_index,
                ContractIndex=resolved_contract_index,
                ContractNo=resolved_contract_no,
                OrderQty=qty,
                MinQty=min_qty,
                OrderPrice=price,
                ClientReqId=resolved_request_id,
                Reference=reference,
                UdpAuthCode=udp_auth_code,
            )
            state = DstarOrderLifecycle(
                client_order_id=logical_id,
                request_id=resolved_request_id,
                order_qty=qty,
            )
            self._store_state(state)
            self.journal.append(
                "dstar_order_created",
                client_order_id=logical_id,
                client_req_id=resolved_request_id,
                request_id=resolved_request_id,
                payload=request,
                state=state.to_journal_dict(),
            )
            return DstarMappedOrder(logical_id, resolved_request_id, request)

    def mark_submitted(
        self,
        *,
        client_order_id: str | None = None,
        request_id: int | None = None,
        local_return_code: int,
    ) -> DstarOrderLifecycle:
        """Record the local ``ReqOrderInsert`` return code.

        A zero return code only moves the order to ``Submitted``. It is not
        treated as acceptance; acceptance must arrive through SPI callbacks.
        """

        with self._lock:
            state = self._find_state(client_order_id=client_order_id, request_id=request_id)
            state.local_return_code = int(local_return_code)
            if local_return_code == 0:
                self._transition(state, DstarOrderLifecycleStatus.SUBMITTED)
            else:
                state.last_error_code = int(local_return_code)
                self._transition(state, DstarOrderLifecycleStatus.REJECTED)
            self._append_state("dstar_order_submitted", state, local_return_code=local_return_code)
            return state

    def on_rsp_order_insert(self, response: DstarApiRspOrderInsertField | Mapping[str, Any]) -> DstarOrderLifecycle:
        """Apply ``OnRspOrderInsert``. This is the first trusted accept/reject signal."""

        rsp = _coerce_rsp_order_insert(response)
        with self._lock:
            state = self._find_state(request_id=rsp.ClientReqId)
            if rsp.OrderId:
                state = self._merge_exchange_order_state(state, rsp.OrderId)
            state.last_error_code = rsp.ErrCode
            if rsp.OrderId:
                state.exchange_order_id = rsp.OrderId
                self._client_id_by_exchange_order_id[rsp.OrderId] = state.client_order_id
            if rsp.ErrCode == 0:
                if state.status in {
                    DstarOrderLifecycleStatus.CREATED,
                    DstarOrderLifecycleStatus.SUBMITTED,
                    DstarOrderLifecycleStatus.ACCEPTED,
                }:
                    self._transition(state, DstarOrderLifecycleStatus.ACCEPTED)
            else:
                self._transition(state, DstarOrderLifecycleStatus.REJECTED)
            self._append_state("dstar_order_rsp_insert", state, payload=rsp)
            return state

    def on_rtn_order(self, order: DstarApiOrderField | Mapping[str, Any]) -> DstarOrderLifecycle:
        """Apply ``OnRtnOrder`` and update status from official order state."""

        rtn = _coerce_order(order)
        with self._lock:
            state = self._find_state_or_recover_from_order(rtn)
            if rtn.OrderId:
                state.exchange_order_id = rtn.OrderId
                self._client_id_by_exchange_order_id[rtn.OrderId] = state.client_order_id
            if rtn.SystemNo:
                state.system_no = rtn.SystemNo
            state.last_order_state = rtn.OrderState
            state.last_error_code = rtn.ErrCode
            if rtn.MatchQty > state.filled_qty:
                state.filled_qty = min(rtn.MatchQty, state.order_qty)
            self._transition(state, _status_from_order_state(rtn.OrderState, state))
            self._append_state("dstar_order_rtn_order", state, payload=rtn)
            return state

    def on_rtn_match(self, match: DstarApiMatchField | Mapping[str, Any]) -> DstarOrderLifecycle:
        """Apply ``OnRtnMatch`` and return the deduplicated lifecycle state."""

        rtn = _coerce_match(match)
        match_key = _match_key(rtn)
        with self._lock:
            state = self._find_state_or_recover_from_match(rtn)
            if rtn.OrderId:
                state.exchange_order_id = rtn.OrderId
                self._client_id_by_exchange_order_id[rtn.OrderId] = state.client_order_id
            if rtn.SystemNo:
                state.system_no = rtn.SystemNo
            if match_key not in state.match_ids:
                previous_qty = state.filled_qty
                new_qty = min(previous_qty + rtn.MatchQty, state.order_qty)
                if new_qty > previous_qty:
                    state.avg_fill_price = _weighted_avg(
                        state.avg_fill_price,
                        previous_qty,
                        rtn.MatchPrice,
                        new_qty - previous_qty,
                    )
                    state.filled_qty = new_qty
                state.match_ids.add(match_key)
            self._transition(
                state,
                DstarOrderLifecycleStatus.FILLED
                if state.filled_qty >= state.order_qty
                else DstarOrderLifecycleStatus.PARTIALLY_FILLED,
            )
            self._append_state("dstar_order_rtn_match", state, payload=rtn, match_key=match_key)
            return state

    def get_by_client_order_id(self, client_order_id: str) -> DstarOrderLifecycle | None:
        """Return lifecycle state by Nautilus client order id."""

        with self._lock:
            return self._orders_by_client_id.get(client_order_id)

    def get_by_request_id(self, request_id: int) -> DstarOrderLifecycle | None:
        """Return lifecycle state by Dstar ``ClientReqId``."""

        with self._lock:
            client_order_id = self._client_id_by_request_id.get(int(request_id))
            return self._orders_by_client_id.get(client_order_id) if client_order_id else None

    def get_by_exchange_order_id(self, exchange_order_id: int) -> DstarOrderLifecycle | None:
        """Return lifecycle state by Dstar ``OrderId``."""

        with self._lock:
            client_order_id = self._client_id_by_exchange_order_id.get(int(exchange_order_id))
            return self._orders_by_client_id.get(client_order_id) if client_order_id else None

    def recover_unknown_order(
        self,
        *,
        exchange_order_id: int,
        order_qty: int,
        system_no: str = "",
    ) -> DstarOrderLifecycle:
        """Create or return a lifecycle state for an order not submitted locally."""

        with self._lock:
            existing = self.get_by_exchange_order_id(exchange_order_id)
            if existing is not None:
                return existing
            synthetic_request_id = -int(exchange_order_id) if exchange_order_id else self._next_unknown_request_id()
            state = DstarOrderLifecycle(
                client_order_id=f"unknown-order-{exchange_order_id or abs(synthetic_request_id)}",
                request_id=synthetic_request_id,
                order_qty=max(int(order_qty), 1),
                status=DstarOrderLifecycleStatus.ACCEPTED,
                exchange_order_id=int(exchange_order_id),
                system_no=system_no,
            )
            self._store_state(state)
            self._append_state("dstar_order_unknown_recovered", state)
            return state

    def replay(self) -> list[DstarOrderLifecycle]:
        """Return recovered states in journal order for backtest/recovery checks."""

        with self._lock:
            return list(self._orders_by_client_id.values())

    def _store_state(self, state: DstarOrderLifecycle) -> None:
        self._orders_by_client_id[state.client_order_id] = state
        self._client_id_by_request_id[state.request_id] = state.client_order_id
        if state.exchange_order_id:
            self._client_id_by_exchange_order_id[state.exchange_order_id] = state.client_order_id

    def _find_state(
        self,
        *,
        client_order_id: str | None = None,
        request_id: int | None = None,
        exchange_order_id: int | None = None,
    ) -> DstarOrderLifecycle:
        if client_order_id is not None:
            state = self._orders_by_client_id.get(client_order_id)
            if state is not None:
                return state
        if request_id is not None:
            mapped_id = self._client_id_by_request_id.get(int(request_id))
            if mapped_id is not None:
                return self._orders_by_client_id[mapped_id]
        if exchange_order_id is not None:
            mapped_id = self._client_id_by_exchange_order_id.get(int(exchange_order_id))
            if mapped_id is not None:
                return self._orders_by_client_id[mapped_id]
        raise KeyError("unknown order identity")

    def _find_state_or_recover_from_order(self, order: DstarApiOrderField) -> DstarOrderLifecycle:
        try:
            return self._find_state(exchange_order_id=order.OrderId)
        except KeyError:
            return self.recover_unknown_order(
                exchange_order_id=order.OrderId,
                order_qty=order.OrderQty or order.MatchQty or 1,
                system_no=order.SystemNo,
            )

    def _find_state_or_recover_from_match(self, match: DstarApiMatchField) -> DstarOrderLifecycle:
        try:
            return self._find_state(exchange_order_id=match.OrderId)
        except KeyError:
            return self.recover_unknown_order(
                exchange_order_id=match.OrderId,
                order_qty=match.MatchQty or 1,
                system_no=match.SystemNo,
            )

    def _next_unknown_request_id(self) -> int:
        candidate = -1
        while candidate in self._client_id_by_request_id:
            candidate -= 1
        return candidate

    def _merge_exchange_order_state(
        self,
        preferred: DstarOrderLifecycle,
        exchange_order_id: int,
    ) -> DstarOrderLifecycle:
        existing_client_order_id = self._client_id_by_exchange_order_id.get(int(exchange_order_id))
        if not existing_client_order_id or existing_client_order_id == preferred.client_order_id:
            return preferred
        existing = self._orders_by_client_id.get(existing_client_order_id)
        if existing is None:
            return preferred

        preferred.exchange_order_id = int(exchange_order_id)
        preferred.system_no = preferred.system_no or existing.system_no
        preferred.filled_qty = max(preferred.filled_qty, existing.filled_qty)
        preferred.avg_fill_price = existing.avg_fill_price or preferred.avg_fill_price
        preferred.last_order_state = preferred.last_order_state or existing.last_order_state
        preferred.last_error_code = preferred.last_error_code or existing.last_error_code
        preferred.match_ids.update(existing.match_ids)
        if existing.status == DstarOrderLifecycleStatus.FILLED:
            preferred.status = (
                DstarOrderLifecycleStatus.FILLED
                if preferred.filled_qty >= preferred.order_qty
                else DstarOrderLifecycleStatus.PARTIALLY_FILLED
            )
        elif existing.status in {
            DstarOrderLifecycleStatus.REJECTED,
            DstarOrderLifecycleStatus.CANCELLED,
            DstarOrderLifecycleStatus.PARTIALLY_FILLED,
        }:
            preferred.status = existing.status
        self._orders_by_client_id.pop(existing_client_order_id, None)
        self._client_id_by_request_id.pop(existing.request_id, None)
        self._client_id_by_exchange_order_id[int(exchange_order_id)] = preferred.client_order_id
        self._store_state(preferred)
        self._append_state("dstar_order_unknown_merged", preferred)
        return preferred

    def _transition(self, state: DstarOrderLifecycle, next_status: DstarOrderLifecycleStatus) -> None:
        if state.status in TERMINAL_ORDER_STATUSES and next_status != state.status:
            return
        state.status = next_status
        state.updated_ts = time.time()
        self._store_state(state)

    def _append_state(self, event_type: str, state: DstarOrderLifecycle, **data: Any) -> None:
        self.journal.append(
            event_type,
            client_order_id=state.client_order_id,
            client_req_id=state.request_id,
            request_id=state.request_id,
            order_id=state.exchange_order_id,
            exchange_order_id=state.exchange_order_id,
            state=state.to_journal_dict(),
            **data,
        )

    def _recover_from_journal(self) -> None:
        for record in self.journal.read_records():
            state_data = record.get("state")
            if not isinstance(state_data, Mapping):
                continue
            state = _state_from_journal(state_data)
            self._store_state(state)


def _state_from_journal(data: Mapping[str, Any]) -> DstarOrderLifecycle:
    status_text = str(data.get("status", DstarOrderLifecycleStatus.CREATED.value))
    try:
        status = DstarOrderLifecycleStatus(status_text)
    except ValueError:
        status = DstarOrderLifecycleStatus.CREATED
    return DstarOrderLifecycle(
        client_order_id=str(data["client_order_id"]),
        request_id=int(data["request_id"]),
        order_qty=int(data["order_qty"]),
        status=status,
        exchange_order_id=int(data.get("exchange_order_id") or data.get("order_id") or 0),
        system_no=str(data.get("system_no", "")),
        filled_qty=int(data.get("filled_qty", 0)),
        avg_fill_price=float(data.get("avg_fill_price", 0.0)),
        last_order_state=(
            int(data["last_order_state"]) if data.get("last_order_state") is not None else None
        ),
        last_error_code=(
            int(data["last_error_code"]) if data.get("last_error_code") is not None else None
        ),
        local_return_code=(
            int(data["local_return_code"]) if data.get("local_return_code") is not None else None
        ),
        match_ids={str(item) for item in data.get("match_ids", [])},
        updated_ts=float(data.get("updated_ts", time.time())),
    )


def _read(source: Any, *names: str) -> Any:
    for name in names:
        if isinstance(source, Mapping) and name in source:
            return source[name]
        if hasattr(source, name):
            return getattr(source, name)
    return None


def _string_value(value: Any) -> str:
    if value is None:
        return ""
    for attr in ("value", "id", "raw"):
        if hasattr(value, attr):
            nested = getattr(value, attr)
            if nested is not value:
                return _string_value(nested)
    return str(value)


def _int_value(value: Any, name: str) -> int:
    if value is None:
        raise ValueError(f"{name} is required")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an int") from exc


def _quantity_value(value: Any, name: str) -> int:
    if value is None:
        raise ValueError(f"{name} is required")
    numeric = _numeric_value(value)
    if numeric <= 0:
        raise ValueError(f"{name} must be > 0")
    if int(numeric) != numeric:
        raise ValueError(f"{name} must be a whole number")
    return int(numeric)


def _price_value(value: Any, order_type: int) -> float:
    if order_type == int(OrderType.MARKET) and value is None:
        return 0.0
    if value is None:
        raise ValueError("price is required")
    price = _numeric_value(value)
    if order_type == int(OrderType.LIMIT) and price <= 0:
        raise ValueError("price must be > 0")
    return float(price)


def _numeric_value(value: Any) -> float:
    for method_name in ("as_double", "as_decimal"):
        method = getattr(value, method_name, None)
        if callable(method):
            return float(method())
    if hasattr(value, "value"):
        nested = getattr(value, "value")
        if nested is not value:
            return _numeric_value(nested)
    return float(value)


def _direction_value(value: Any) -> int:
    text = _string_value(value).upper()
    if not text:
        raise ValueError("side is required")
    if text in {str(int(Direction.BUY)), "BUY", "BID", "LONG", "B"}:
        return int(Direction.BUY)
    if text in {str(int(Direction.SELL)), "SELL", "ASK", "SHORT", "S"}:
        return int(Direction.SELL)
    raise ValueError(f"unsupported side: {text}")


def _offset_value(value: Any, *, default: Offset) -> int:
    text = _string_value(value).upper()
    if not text:
        return int(default)
    if text in {str(int(Offset.OPEN)), "OPEN", "O"}:
        return int(Offset.OPEN)
    if text in {str(int(Offset.CLOSE)), "CLOSE", "C"}:
        return int(Offset.CLOSE)
    if text in {str(int(Offset.CLOSE_TODAY)), "CLOSE_TODAY", "CLOSETODAY", "T"}:
        return int(Offset.CLOSE_TODAY)
    raise ValueError(f"unsupported offset: {text}")


def _hedge_value(value: Any, *, default: Hedge) -> int:
    text = _string_value(value).upper()
    if not text:
        return int(default)
    if text in {str(int(Hedge.SPECULATE)), "SPECULATE", "SPECULATION", "T"}:
        return int(Hedge.SPECULATE)
    if text in {str(int(Hedge.HEDGE)), "HEDGE", "B"}:
        return int(Hedge.HEDGE)
    raise ValueError(f"unsupported hedge: {text}")


def _valid_type_value(value: Any, *, default: ValidType) -> int:
    text = _string_value(value).upper()
    if not text or text in {"DAY", "GTC"}:
        return int(default)
    if text in {str(int(ValidType.GFD)), "GFD"}:
        return int(ValidType.GFD)
    if text in {str(int(ValidType.FOK)), "FOK"}:
        return int(ValidType.FOK)
    if text in {str(int(ValidType.IOC)), "IOC"}:
        return int(ValidType.IOC)
    if text in {str(int(ValidType.GIS)), "GIS"}:
        return int(ValidType.GIS)
    raise ValueError(f"unsupported valid_type: {text}")


def _order_type_value(value: Any, *, default: OrderType) -> int:
    text = _string_value(value).upper()
    if not text:
        return int(default)
    if text in {str(int(OrderType.LIMIT)), "LIMIT"}:
        return int(OrderType.LIMIT)
    if text in {str(int(OrderType.MARKET)), "MARKET"}:
        return int(OrderType.MARKET)
    raise ValueError(f"unsupported order_type: {text}")


def _coerce_rsp_order_insert(value: DstarApiRspOrderInsertField | Mapping[str, Any]) -> DstarApiRspOrderInsertField:
    return value if isinstance(value, DstarApiRspOrderInsertField) else DstarApiRspOrderInsertField.from_dict(value)


def _coerce_order(value: DstarApiOrderField | Mapping[str, Any]) -> DstarApiOrderField:
    return value if isinstance(value, DstarApiOrderField) else DstarApiOrderField.from_dict(value)


def _coerce_match(value: DstarApiMatchField | Mapping[str, Any]) -> DstarApiMatchField:
    return value if isinstance(value, DstarApiMatchField) else DstarApiMatchField.from_dict(value)


def _status_from_order_state(
    order_state: int,
    state: DstarOrderLifecycle,
) -> DstarOrderLifecycleStatus:
    if order_state in {
        int(OrderState.ACCEPT),
        int(OrderState.QUEUE),
        int(OrderState.APPLY),
        int(OrderState.SUSPENDED),
        int(OrderState.TRIGGERED),
        int(OrderState.WAITING_TRIGGER),
    }:
        return (
            DstarOrderLifecycleStatus.PARTIALLY_FILLED
            if state.filled_qty > 0
            else DstarOrderLifecycleStatus.ACCEPTED
        )
    if order_state == int(OrderState.PARTIAL_FILL):
        return DstarOrderLifecycleStatus.PARTIALLY_FILLED
    if order_state == int(OrderState.FILLED):
        return DstarOrderLifecycleStatus.FILLED
    if order_state == int(OrderState.FAILED):
        return DstarOrderLifecycleStatus.REJECTED
    if order_state in {
        int(OrderState.DELETED),
        int(OrderState.REMAINDER_DELETED),
        int(OrderState.SYSTEM_DELETED),
    }:
        return DstarOrderLifecycleStatus.CANCELLED
    return state.status


def _match_key(match: DstarApiMatchField) -> str:
    if match.MatchId:
        return f"match:{match.MatchId}"
    return f"order:{match.OrderId}:system:{match.SystemNo}:time:{match.MatchTime}:qty:{match.MatchQty}"


def _weighted_avg(existing_price: float, existing_qty: int, fill_price: float, fill_qty: int) -> float:
    total_qty = existing_qty + fill_qty
    if total_qty <= 0:
        return 0.0
    return ((existing_price * existing_qty) + (fill_price * fill_qty)) / total_qty


__all__ = [
    "DstarMappedOrder",
    "DstarOrderLifecycle",
    "DstarOrderLifecycleStatus",
    "DstarOrderMapper",
]
