# 订单状态机、请求号与幂等保护

本文档说明 `dstar_trade_py` 高层客户端如何管理 `ClientReqId`、订单状态和本地
journal。这里的状态只用于 Python SDK 本地保护和事件整理，订单最终结果必须以后续柜台
或交易所回报为准。

## 最小示例

下面示例演示本地请求号和订单状态管理，不连接真实交易服务器：

```python
from dstar_trade_py import OrderJournal, OrderStateManager, RequestIdManager
from dstar_trade_py.fields import DstarApiRspOrderInsertField

journal = OrderJournal("logs/order_journal.jsonl")
request_ids = RequestIdManager.from_journal(journal)
states = OrderStateManager.from_journal(journal)

client_req_id = request_ids.next_id()
states.register_submission("strategy-a-000001", client_req_id)

# 示例格式：真实 response 来自 OnRspOrderInsert 回调。
state = states.on_rsp_order_insert(
    DstarApiRspOrderInsertField(ClientReqId=client_req_id, OrderId=10001, ErrCode=0)
)
print("[示例格式]", state.status, state.order_id)
```

示例输出格式：

```text
[示例格式] accepted_by_api 10001
```

这只是本地状态机演示，不代表真实委托已成交或最终成功。

## 请求号管理

`RequestIdManager` 负责分配和保护 `ClientReqId`。

| 能力 | 说明 |
| --- | --- |
| 本地递增 | 不传 `client_req_id` 时，客户端从当前游标加 1 分配。 |
| 显式预留 | 传入 `client_req_id` 时会先预留，已使用的请求号会抛出 `ValueError`。 |
| 最新请求号同步 | `query_last_client_req_id()` 调用底层 `ReqLastClientReqId`，收到 `rsp_last_req_id` 后更新本地游标。 |
| 跳跃检测 | 远端最新请求号或显式请求号与本地游标差距超过阈值时，记录到 `detected_jumps`。 |
| 重启恢复 | 启动时从 journal 中恢复 `client_req_id` / `ClientReqId`，避免复用近期请求号。 |

## 幂等保护

`OrderStateManager` 使用 `client_order_id` 做业务幂等键。同一个 `client_order_id` 在
同一个客户端生命周期或从 journal 恢复后的近期窗口内只能提交一次。

如果调用方不传 `client_order_id`，客户端会生成形如
`auto-{client_req_id}-{random}` 的本地业务 ID。生产系统建议传入由上层订单系统生成的
稳定业务 ID，这样进程重启后仍能阻止重复提交。

## 本地 Journal

默认 journal 路径为：

```text
logs/order_journal.jsonl
```

每行是一条 JSON 记录，当前会记录：

| event_type | 触发时机 |
| --- | --- |
| `order_submit` | 普通报单、限价单、市价单、组合单、报价请求提交后 |
| `order_cancel` | 撤单或报价撤销请求提交后 |
| `rsp_order_insert` | 收到 `OnRspOrderInsert` |
| `rsp_order_delete` | 收到 `OnRspOrderDelete` |
| `rsp_offer_insert` | 收到 `OnRspOfferInsert` |
| `rtn_order` | 收到 `OnRtnOrder` |
| `rtn_match` | 收到 `OnRtnMatch` |
| `rtn_offer` | 收到 `OnRtnOffer` |

journal 会过滤包含 `password`、`passwd`、`auth`、`license`、`secret`、`token` 的字段，
避免持久化密码、授权码和令牌类敏感信息。journal 的主要用途是恢复请求号和幂等键，不是
审计级交易流水。

## 订单状态流转

本地状态由 `ManagedOrderState.status` 表示：

| 本地状态 | 来源 | 含义 |
| --- | --- | --- |
| `submitted_local` | 下单/撤单前本地注册 | SDK 准备向 native API 提交请求。 |
| `accepted_by_api` | `OnRspOrderInsert` / `OnRspOrderDelete` 且 `ErrCode == 0` | 柜台应答本次请求未返回错误，但这不是最终成交或最终委托成功。 |
| `rejected_by_api` | `OnRspOrderInsert` / `OnRspOrderDelete` 且 `ErrCode != 0` | 柜台应答本次请求失败。 |
| `order_update` | `OnRtnOrder` | 收到委托回报，`OrderState` 和 `MatchQty` 以回报字段为准。 |
| `matched` | `OnRtnMatch` | 收到成交回报，累计 `MatchQty`。 |

`OnRtnOrder.OrderState` 是官方状态枚举，SDK 只保存原始整数值，不自行推断交易所最终语义。
调用方应结合 `OrderState`、`ErrCode`、`MatchQty`、`OrderId`、`SystemNo` 和业务风控规则
判断订单是否完成、撤销或失败。

## 关键边界

`ReqOrderInsert`、`ReqOrderDelete`、`ReqOfferInsert` 等主动接口返回 `0`，只表示请求被本地
API 接收或同步调用没有立即失败，不代表：

- 交易所已经接受委托；
- 委托已经排队；
- 委托已经成交；
- 撤单已经成功；
- 报价已经生效。

最终状态必须以后续 `OnRspOrderInsert`、`OnRtnOrder`、`OnRtnMatch` 等回调为准。
