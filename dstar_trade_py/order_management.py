"""Request-id, order-state, and journal helpers for dstar_trade_py."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .config import is_sensitive_key
from .fields import DstarApiMatchField, DstarApiOrderField, DstarApiRspOrderInsertField


DEFAULT_ORDER_JOURNAL_PATH = Path("logs/order_journal.jsonl")


def _plain(value: Any) -> Any:
    """Convert dataclasses and containers into JSON-compatible values."""

    if is_dataclass(value):
        return _plain(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): _plain(item)
            for key, item in value.items()
            if not is_sensitive_key(key)
        }
    if isinstance(value, list | tuple):
        return [_plain(item) for item in value]
    return value


class OrderJournal:
    """Append-only local JSONL journal for order lifecycle data.

    The journal intentionally records only order/cancel request data and callback
    payloads. It does not record passwords, auth strings, or login configuration.
    """

    def __init__(self, path: str | Path = DEFAULT_ORDER_JOURNAL_PATH) -> None:
        self.path = Path(path)

    def append(self, event_type: str, **data: Any) -> None:
        """Append one JSONL record with a timestamp."""

        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {"ts": time.time(), "event_type": event_type, **_plain(data)}
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def read_records(self) -> list[dict[str, Any]]:
        """Read valid JSONL records; ignore blank lines."""

        if not self.path.exists():
            return []
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                stripped = line.strip()
                if stripped:
                    try:
                        records.append(json.loads(stripped))
                    except json.JSONDecodeError:
                        # A crash can leave the last JSONL line partially written.
                        # Keep recovery best-effort instead of blocking client startup.
                        continue
        return records


class RequestIdManager:
    """Manage local ClientReqId allocation and duplicate detection."""

    def __init__(
        self,
        *,
        start: int = 0,
        jump_threshold: int = 1000,
        used_ids: Iterable[int] | None = None,
    ) -> None:
        self.current = int(start)
        self.jump_threshold = int(jump_threshold)
        self.used_ids: set[int] = set(used_ids or ())
        self.detected_jumps: list[tuple[int, int]] = []

    @classmethod
    def from_journal(
        cls,
        journal: OrderJournal,
        *,
        remote_last_id: int | None = None,
        jump_threshold: int = 1000,
    ) -> "RequestIdManager":
        """Recover used request IDs from local journal records."""

        used_ids: set[int] = set()
        for record in journal.read_records():
            for key in ("client_req_id", "ClientReqId"):
                value = record.get(key)
                if isinstance(value, int):
                    used_ids.add(value)
            payload = record.get("payload")
            if isinstance(payload, dict):
                value = payload.get("ClientReqId")
                if isinstance(value, int):
                    used_ids.add(value)

        start = max(used_ids, default=0)
        manager = cls(start=start, jump_threshold=jump_threshold, used_ids=used_ids)
        if remote_last_id is not None:
            manager.update_from_remote(remote_last_id)
        return manager

    def update_from_remote(self, remote_last_id: int) -> None:
        """Update local cursor using ReqLastClientReqId result and detect large jumps."""

        remote = int(remote_last_id)
        if self.current and abs(remote - self.current) > self.jump_threshold:
            self.detected_jumps.append((self.current, remote))
        self.current = max(self.current, remote)

    def next_id(self) -> int:
        """Return the next unused local request ID."""

        candidate = self.current + 1
        while candidate in self.used_ids:
            candidate += 1
        self.current = candidate
        self.used_ids.add(candidate)
        return candidate

    def reserve(self, client_req_id: int) -> int:
        """Reserve an explicit request ID, rejecting duplicates."""

        value = int(client_req_id)
        if value in self.used_ids:
            raise ValueError(f"duplicate client_req_id: {value}")
        if self.current and value - self.current > self.jump_threshold:
            self.detected_jumps.append((self.current, value))
        self.used_ids.add(value)
        self.current = max(self.current, value)
        return value

    def has_used(self, client_req_id: int) -> bool:
        """Return whether an ID was already reserved or recovered."""

        return int(client_req_id) in self.used_ids


@dataclass(slots=True)
class ManagedOrderState:
    """Locally tracked order state assembled from request and callback events."""

    client_order_id: str
    client_req_id: int
    order_id: int = 0
    system_no: str = ""
    status: str = "submitted_local"
    rsp_error_code: int | None = None
    order_state: int | None = None
    total_match_qty: int = 0
    last_update_ts: float = field(default_factory=time.time)


class OrderStateManager:
    """Maintain order state from request, response, order, and match events."""

    def __init__(self, *, known_client_order_ids: Iterable[str] | None = None) -> None:
        self.orders_by_client_order_id: dict[str, ManagedOrderState] = {}
        self.client_order_id_by_req_id: dict[int, str] = {}
        self.client_order_id_by_order_id: dict[int, str] = {}
        self.known_client_order_ids: set[str] = set(known_client_order_ids or ())

    @classmethod
    def from_journal(cls, journal: OrderJournal) -> "OrderStateManager":
        """Recover recent client_order_id mappings and replay known order events."""

        manager = cls()
        records = journal.read_records()
        for record in records:
            event_type = record.get("event_type")
            if event_type not in {"order_submit", "order_cancel"}:
                continue
            client_order_id = record.get("client_order_id")
            client_req_id = record.get("client_req_id")
            if isinstance(client_order_id, str):
                manager.known_client_order_ids.add(client_order_id)
                if isinstance(client_req_id, int):
                    state = ManagedOrderState(
                        client_order_id=client_order_id,
                        client_req_id=client_req_id,
                        status=str(event_type),
                    )
                    manager.orders_by_client_order_id[client_order_id] = state
                    manager.client_order_id_by_req_id[client_req_id] = client_order_id

        for record in records:
            event_type = record.get("event_type")
            payload = record.get("payload")
            if not isinstance(payload, dict):
                continue
            if event_type in {"rsp_order_insert", "rsp_order_delete", "rsp_offer_insert"}:
                manager.on_rsp_order_insert(DstarApiRspOrderInsertField.from_dict(payload))
            elif event_type == "rtn_order":
                manager.on_rtn_order(DstarApiOrderField.from_dict(payload))
            elif event_type == "rtn_match":
                manager.on_rtn_match(DstarApiMatchField.from_dict(payload))
        return manager

    def register_submission(self, client_order_id: str, client_req_id: int) -> ManagedOrderState:
        """Register a new logical client order and enforce idempotency."""

        if not client_order_id:
            raise ValueError("client_order_id is required")
        if client_order_id in self.known_client_order_ids:
            raise ValueError(f"duplicate client_order_id: {client_order_id}")
        self.known_client_order_ids.add(client_order_id)
        state = ManagedOrderState(
            client_order_id=client_order_id,
            client_req_id=int(client_req_id),
        )
        self.orders_by_client_order_id[client_order_id] = state
        self.client_order_id_by_req_id[int(client_req_id)] = client_order_id
        return state

    def on_rsp_order_insert(self, response: DstarApiRspOrderInsertField) -> ManagedOrderState:
        """Update state from OnRspOrderInsert/OnRspOrderDelete compatible payload."""

        client_order_id = self.client_order_id_by_req_id.get(response.ClientReqId)
        if client_order_id is None:
            client_order_id = f"unknown-req-{response.ClientReqId}"
            self.known_client_order_ids.add(client_order_id)
            self.client_order_id_by_req_id[response.ClientReqId] = client_order_id

        state = self.orders_by_client_order_id.get(client_order_id)
        if state is None:
            state = ManagedOrderState(client_order_id=client_order_id, client_req_id=response.ClientReqId)
            self.orders_by_client_order_id[client_order_id] = state

        state.order_id = response.OrderId
        state.rsp_error_code = response.ErrCode
        state.status = "accepted_by_api" if response.ErrCode == 0 else "rejected_by_api"
        state.last_update_ts = time.time()
        if response.OrderId:
            self.client_order_id_by_order_id[response.OrderId] = client_order_id
        return state

    def on_rtn_order(self, order: DstarApiOrderField) -> ManagedOrderState:
        """Update state from OnRtnOrder."""

        client_order_id = self.client_order_id_by_order_id.get(order.OrderId)
        if client_order_id is None:
            client_order_id = f"order-{order.OrderId}"
            self.known_client_order_ids.add(client_order_id)
            self.client_order_id_by_order_id[order.OrderId] = client_order_id

        state = self.orders_by_client_order_id.get(client_order_id)
        if state is None:
            state = ManagedOrderState(client_order_id=client_order_id, client_req_id=0)
            self.orders_by_client_order_id[client_order_id] = state

        state.order_id = order.OrderId
        state.system_no = order.SystemNo
        state.order_state = order.OrderState
        state.total_match_qty = max(state.total_match_qty, order.MatchQty)
        state.status = "order_update"
        state.last_update_ts = time.time()
        return state

    def on_rtn_match(self, match: DstarApiMatchField) -> ManagedOrderState:
        """Update state from OnRtnMatch."""

        client_order_id = self.client_order_id_by_order_id.get(match.OrderId)
        if client_order_id is None:
            client_order_id = f"order-{match.OrderId}"
            self.known_client_order_ids.add(client_order_id)
            self.client_order_id_by_order_id[match.OrderId] = client_order_id

        state = self.orders_by_client_order_id.get(client_order_id)
        if state is None:
            state = ManagedOrderState(client_order_id=client_order_id, client_req_id=0)
            self.orders_by_client_order_id[client_order_id] = state

        state.order_id = match.OrderId
        state.system_no = match.SystemNo
        state.total_match_qty += match.MatchQty
        state.status = "matched"
        state.last_update_ts = time.time()
        return state

    def get(self, client_order_id: str) -> ManagedOrderState | None:
        """Return tracked state by logical client order id."""

        return self.orders_by_client_order_id.get(client_order_id)


__all__ = [
    "DEFAULT_ORDER_JOURNAL_PATH",
    "ManagedOrderState",
    "OrderJournal",
    "OrderStateManager",
    "RequestIdManager",
]
