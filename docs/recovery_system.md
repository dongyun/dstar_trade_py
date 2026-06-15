# Recovery System

本文说明 `DstarRecoveryEngine` 如何在系统启动或重连后恢复订单、成交、持仓和资金状态。

## Recovery Goals

恢复目标不是重新下单，而是重建 NautilusTrader 对执行状态的视图：

- 避免重复成交事件
- 根据 `OrderId` 恢复委托状态
- 根据 `MatchId` 恢复成交状态
- 处理未知订单
- 恢复资金和持仓快照

## Recovery Sequence

```text
startup / reconnect
  -> load journal
       - DstarOrderMapper rebuilds lifecycle state
       - DstarEventAdapter rebuilds callback/event dedupe sets
  -> query_order(timeout)
       - if client supports it
       - else mark skipped_capabilities += query_order
  -> query_trade(timeout)
       - if client supports it
       - else mark skipped_capabilities += query_trade
  -> query_position(timeout)
  -> query_fund(timeout)
  -> drain pending callback queue
  -> return DstarRecoveryResult
```

`DstarRecoveryResult` includes:

| Field | Meaning |
| --- | --- |
| `events` | Nautilus-style events generated during recovery |
| `orders` | recovered lifecycle states |
| `positions` | queried position fields |
| `fund` | queried fund field |
| `skipped_capabilities` | query capabilities not present on current client |

## Query Capability Detection

Current `dstar_trade_py.DstarTradeClient` supports:

- `query_position`
- `query_fund`
- `query_last_client_req_id`

It does not expose active `query_order` or `query_trade`. `DstarRecoveryEngine` therefore checks methods dynamically:

```text
if hasattr(client, "query_order"):
    call query_order
else:
    skipped_capabilities.append("query_order")
```

The same applies to `query_trade`. This avoids documenting or calling APIs that do not exist.

## Order Recovery

If `query_order` is available:

```text
query_order()
  -> DstarApiOrderField list
  -> event_adapter.process_event("rsp_qry_order", order)
  -> order_mapper.on_rtn_order(order)
  -> lifecycle by OrderId
```

If `OrderId` is unknown, mapper creates:

```text
client_order_id = unknown-order-{OrderId}
request_id = -OrderId
status = Accepted / PartiallyFilled / Filled / Cancelled / Rejected based on OrderState
```

If a later `OnRspOrderInsert(ClientReqId, OrderId)` connects that `OrderId` to a local request, the unknown lifecycle is
merged into the local `client_order_id`.

## Trade Recovery

If `query_trade` is available:

```text
query_trade()
  -> DstarApiMatchField list
  -> event_adapter.process_event("rsp_qry_trade", trade)
  -> match_key from MatchId
  -> drop if match_key seen in lifecycle/journal
  -> emit OrderFilled if new
```

`MatchId` is the primary idempotency key. If missing, fallback key is:

```text
OrderId + SystemNo + MatchTime + MatchQty
```

## Position and Fund Recovery

```text
query_position()
  -> list[DstarApiPositionField]
  -> PositionUpdated events

query_fund()
  -> DstarApiFundField
  -> AccountStateEvent
```

These queries are safe by default because they do not submit orders. They still require `api_ready`.

## Replay Recovery

Replay test coverage uses recorded SPI event tuples:

```text
rtn_match(OrderId=9001, MatchId=7001)
rsp_order_insert(ClientReqId=100, OrderId=9001)
rtn_order(OrderId=9001, PARTIAL_FILL)
rtn_match(OrderId=9001, MatchId=7002)
rtn_match(OrderId=9001, MatchId=7002)  # duplicate
```

Expected result:

- two unique fills
- no repeated fill for duplicate `MatchId=7002`
- unknown order merged into local `client_order_id`
- recovered lifecycle is `Filled`

## Recovery Limitations

- Without active `query_order/query_trade`, recovery cannot ask the server for all historical orders/trades.
- Journal is not an audit database; it is an idempotency and recovery index.
- If an event never reached the process and no server-side query is available, adapter cannot reconstruct it.
- Recovery must run after `wait_ready()`, otherwise query methods may fail with not-ready errors.
