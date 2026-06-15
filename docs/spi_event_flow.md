# SPI Event Flow

本文说明易盛 SPI 回调如何进入 adapter，并转换为 Nautilus-style event。

## Thread Model

```text
SDK callback thread
  -> C++ PyTradeSpiAdapter::OnXXX
  -> copy native struct to Python dict
  -> DstarTradeClient.on_event(event_name, payload)
  -> DstarEventAdapter.on_event(event_name, payload)
       Queue.put(DstarCallbackEnvelope)
       return

dispatcher thread
  -> DstarEventAdapter.process_next()
  -> callback dedupe by journal
  -> update DstarOrderMapper
  -> emitted-event dedupe by journal
  -> DstarNautilusEvent

Nautilus event loop
  -> DstarExecutionClient converts lightweight event to native Nautilus event
```

SDK callback thread 只能做入队操作。不能在回调线程中：

- 调用 `query_fund/query_position`
- 重连或 close native API
- 直接调用 Nautilus msgbus
- 等待另一个需要 SPI 回调完成的锁或条件变量

## Event Names

`dstar_trade_py` 把 C++ 回调转换为 snake_case event name。

| C++ SPI | Python event | Adapter handling |
| --- | --- | --- |
| `OnRspOrderInsert` | `rsp_order_insert` | `OrderAccepted` / `OrderRejected` |
| `OnRtnOrder` | `rtn_order` | `OrderAccepted` / `OrderUpdated` / rejection update |
| `OnRtnMatch` | `rtn_match` | `OrderFilled` |
| `OnRspOrder` | `rsp_order` | snapshot/recovery order update |
| `OnRspMatch` | `rsp_match` | snapshot/recovery fill |
| `OnRspQryPosition` | `rsp_qry_position` | `PositionUpdated` |
| `OnRspQryFund` | `rsp_qry_fund` | `AccountStateEvent` |

`rsp_qry_order` and `rsp_qry_trade` are optional adapter aliases for future client implementations.
The current SDK binding does not expose active `ReqQryOrder` or `ReqQryTrade`.

## Order Insert Response

```text
rsp_order_insert(ClientReqId=100, OrderId=9001, ErrCode=0)
  -> callback_key = rsp_order_insert:100:9001:0
  -> find lifecycle by ClientReqId
  -> store OrderId
  -> state Accepted
  -> event_key = OrderAccepted:client_order_id:100:9001:Accepted::0
  -> emit OrderAccepted
```

If `ErrCode != 0`, state becomes `Rejected` and adapter emits `OrderRejected`.

## Order Update

```text
rtn_order(OrderId=9001, OrderState=QUEUE, MatchQty=0)
  -> callback_key contains OrderId/SystemNo/OrderState/MatchQty/ErrCode/UpdateTime
  -> find lifecycle by OrderId
  -> update SystemNo, OrderState, MatchQty
  -> emit OrderUpdated unless no effective state change
```

For unknown `OrderId`, adapter creates `unknown-order-{OrderId}` and later merges it if
`rsp_order_insert` connects the same `OrderId` to a local `ClientReqId`.

## Match Event

```text
rtn_match(OrderId=9001, MatchId=7001, MatchQty=1, MatchPrice=2400.0)
  -> match_key = match:7001
  -> if match_key already in journal/state, drop
  -> update cumulative filled qty
  -> emit OrderFilled
```

If `MatchId` is `0`, fallback key uses `OrderId`, `SystemNo`, `MatchTime`, and `MatchQty`.

## Position and Fund

```text
rsp_qry_position(data=Position, last=False)
  -> PositionUpdated

rsp_qry_fund(Fund)
  -> AccountStateEvent
```

`rsp_qry_position(last=True)` with empty data is a batch terminator and does not produce a position event.

## Dedupe Layers

| Layer | Key source | Journal event |
| --- | --- | --- |
| callback dedupe | event name + stable payload fields | `dstar_callback_seen` |
| emitted-event dedupe | Nautilus-style event key | `dstar_event_emitted` |
| fill dedupe | `MatchId` or fallback match tuple | lifecycle `match_ids` |

These layers are intentionally redundant. A duplicate callback should be ignored before state mutation; if state was
mutated before a crash, emitted-event dedupe prevents repeating the external event after restart.
