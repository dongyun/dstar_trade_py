# Order Lifecycle

本文描述 Dstar Execution Adapter 的订单状态机。订单状态只由 adapter 本地状态机维护，最终交易事实
仍以易盛 SPI 回调为准。

## State Machine

```text
Created
  |
  | ReqOrderInsert local call returned
  v
Submitted
  |
  | OnRspOrderInsert ErrCode == 0
  v
Accepted
  |
  | OnRtnMatch partial fill or OnRtnOrder PARTIAL_FILL
  v
PartiallyFilled
  |
  | cumulative fill qty >= order qty or OnRtnOrder FILLED
  v
Filled

Submitted/Accepted/PartiallyFilled
  | OnRspOrderInsert ErrCode != 0 or OnRtnOrder FAILED
  v
Rejected

Accepted/PartiallyFilled
  | OnRtnOrder DELETED / REMAINDER_DELETED / SYSTEM_DELETED
  v
Cancelled
```

## Local Submission Timeline

```text
Nautilus order
  -> DstarOrderMapper.map_order_to_insert_request()
       status = Created
       journal: dstar_order_created
  -> DstarTradeClient.insert_limit_order(...)
       calls ReqOrderInsert
  -> DstarOrderMapper.mark_submitted(local_return_code)
       ret=0  => Submitted
       ret!=0 => Rejected
       journal: dstar_order_submitted
  -> wait for SPI callbacks
```

`Submitted` 不是交易所状态，只说明 adapter 已调用 native API。不能从 `Submitted` 生成最终成交判断。

## ID Mapping

| ID | Source | Purpose |
| --- | --- | --- |
| `client_order_id` | Nautilus / strategy | 业务幂等主键 |
| `request_id` / `ClientReqId` | Adapter `RequestIdManager` | Dstar 请求号，连接 `OnRspOrderInsert` |
| `exchange_order_id` / `OrderId` | `OnRspOrderInsert` or `OnRtnOrder` | 柜台委托号，连接 `OnRtnOrder` / `OnRtnMatch` |
| `SystemNo` | `OnRtnOrder` / `OnRtnMatch` | 撤单和恢复辅助键 |
| `MatchId` | `OnRtnMatch` | 成交去重主键 |

## Callback Rules

| Callback | Adapter action | Nautilus-style event |
| --- | --- | --- |
| `OnRspOrderInsert ErrCode == 0` | map `ClientReqId -> OrderId`; state `Accepted` if not already filled/cancelled | `OrderAccepted` |
| `OnRspOrderInsert ErrCode != 0` | state `Rejected` | `OrderRejected` |
| `OnRtnOrder QUEUE/ACCEPT/APPLY` | state `Accepted` unless already partially filled | `OrderUpdated` or `OrderAccepted` for unknown order |
| `OnRtnOrder PARTIAL_FILL` | state `PartiallyFilled` | `OrderUpdated` |
| `OnRtnOrder FILLED` | state `Filled`; fill event still comes from `OnRtnMatch` | `OrderUpdated` |
| `OnRtnOrder DELETED/LEFTDELETE/SYSDELETE` | state `Cancelled` | `OrderUpdated` then Nautilus bridge may map to `OrderCanceled` |
| `OnRtnMatch` | update cumulative fill by `MatchId` | `OrderFilled` |

## Out-of-Order Handling

易盛回调可能乱序。adapter 必须接受以下顺序：

```text
OnRtnMatch(OrderId=9001, MatchId=1)
  -> no local OrderId mapping
  -> create unknown-order-9001
  -> emit OrderFilled for unknown order

OnRspOrderInsert(ClientReqId=100, OrderId=9001)
  -> find local client_order_id by ClientReqId
  -> merge unknown-order-9001 into local order
  -> do not regress PartiallyFilled to Accepted
```

`OnRtnOrder` 先到也同理。unknown state 会在 `ClientReqId + OrderId` 同时可见时合并。

## Idempotency

`DstarOrderMapper` 写入以下 journal 事件：

| event_type | Meaning |
| --- | --- |
| `dstar_order_created` | 请求映射完成，尚未调用 native |
| `dstar_order_submitted` | native 本地返回码已记录 |
| `dstar_order_rsp_insert` | 收到 `OnRspOrderInsert` |
| `dstar_order_rtn_order` | 收到 `OnRtnOrder` |
| `dstar_order_rtn_match` | 收到 `OnRtnMatch` |
| `dstar_order_unknown_recovered` | 发现未知 `OrderId` |
| `dstar_order_unknown_merged` | unknown 状态合并到本地订单 |

重启时从 journal 恢复 `client_order_id`、`ClientReqId`、`OrderId`、`MatchId`，防止重复提交和重复成交。

## Current Limitations

- 不支持 native 原生改单；如果 Nautilus 发 `ModifyOrder`，MVP 应拒绝或由上层实现 cancel-replace。
- 没有主动 `query_order/query_trade` 时，订单恢复依赖 journal、初始化快照和实时回调。
- `OrderState` 的交易所细节由易盛柜台定义，adapter 只做保守映射，不推断不存在的成交。
