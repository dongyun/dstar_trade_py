"""Recovery engine for rebuilding adapter state after startup or reconnect."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from .event_adapter import DstarEventAdapter, DstarNautilusEvent
from .fields import DstarApiFundField, DstarApiMatchField, DstarApiOrderField, DstarApiPositionField
from .order_mapper import DstarOrderLifecycle, DstarOrderMapper


@dataclass(slots=True)
class DstarRecoveryResult:
    """Summary of a recovery pass."""

    events: list[DstarNautilusEvent] = field(default_factory=list)
    orders: list[DstarOrderLifecycle] = field(default_factory=list)
    positions: list[DstarApiPositionField] = field(default_factory=list)
    fund: DstarApiFundField | None = None
    skipped_capabilities: list[str] = field(default_factory=list)


class DstarRecoveryEngine:
    """Run query-based and journal-based recovery after startup/reconnect."""

    def __init__(
        self,
        *,
        client: Any,
        order_mapper: DstarOrderMapper,
        event_adapter: DstarEventAdapter,
        query_timeout: float = 5,
    ) -> None:
        self.client = client
        self.order_mapper = order_mapper
        self.event_adapter = event_adapter
        self.query_timeout = float(query_timeout)

    def recover(self) -> DstarRecoveryResult:
        """Run recovery in the required order: order, trade, position, fund."""

        result = DstarRecoveryResult()

        result.events.extend(self._recover_orders(result))
        result.events.extend(self._recover_trades(result))
        result.events.extend(self._recover_positions(result))
        result.events.extend(self._recover_fund(result))
        result.events.extend(self.event_adapter.process_all())
        result.orders = self.order_mapper.replay()
        return result

    def _recover_orders(self, result: DstarRecoveryResult) -> list[DstarNautilusEvent]:
        query_order = getattr(self.client, "query_order", None)
        if query_order is None:
            result.skipped_capabilities.append("query_order")
            return []
        events: list[DstarNautilusEvent] = []
        for order in _as_list(_call_query(query_order, self.query_timeout)):
            events.extend(self.event_adapter.process_event("rsp_qry_order", _coerce_order(order)))
        return events

    def _recover_trades(self, result: DstarRecoveryResult) -> list[DstarNautilusEvent]:
        query_trade = getattr(self.client, "query_trade", None)
        if query_trade is None:
            result.skipped_capabilities.append("query_trade")
            return []
        events: list[DstarNautilusEvent] = []
        for trade in _as_list(_call_query(query_trade, self.query_timeout)):
            events.extend(self.event_adapter.process_event("rsp_qry_trade", _coerce_match(trade)))
        return events

    def _recover_positions(self, result: DstarRecoveryResult) -> list[DstarNautilusEvent]:
        query_position = getattr(self.client, "query_position", None)
        if query_position is None:
            result.skipped_capabilities.append("query_position")
            return []
        events: list[DstarNautilusEvent] = []
        positions = [_coerce_position(item) for item in _as_list(_call_query(query_position, self.query_timeout))]
        result.positions.extend(positions)
        for position in positions:
            events.extend(self.event_adapter.process_event("rsp_qry_position", {"data": position, "last": False}))
        return events

    def _recover_fund(self, result: DstarRecoveryResult) -> list[DstarNautilusEvent]:
        query_fund = getattr(self.client, "query_fund", None)
        if query_fund is None:
            result.skipped_capabilities.append("query_fund")
            return []
        fund = _coerce_fund(_call_query(query_fund, self.query_timeout))
        result.fund = fund
        return self.event_adapter.process_event("rsp_qry_fund", fund)


def _call_query(method: Any, timeout: float) -> Any:
    try:
        return method(timeout=timeout)
    except TypeError:
        return method()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
        return list(value)
    return [value]


def _coerce_order(value: Any) -> DstarApiOrderField:
    return value if isinstance(value, DstarApiOrderField) else DstarApiOrderField.from_dict(dict(value))


def _coerce_match(value: Any) -> DstarApiMatchField:
    return value if isinstance(value, DstarApiMatchField) else DstarApiMatchField.from_dict(dict(value))


def _coerce_position(value: Any) -> DstarApiPositionField:
    return value if isinstance(value, DstarApiPositionField) else DstarApiPositionField.from_dict(dict(value))


def _coerce_fund(value: Any) -> DstarApiFundField:
    return value if isinstance(value, DstarApiFundField) else DstarApiFundField.from_dict(dict(value))


__all__ = ["DstarRecoveryEngine", "DstarRecoveryResult"]
