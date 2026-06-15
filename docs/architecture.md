# Dstar Execution Adapter Architecture

本文说明 `NautilusTrader -> Dstar Execution Adapter -> dstar_trade_py -> 易盛启明星 V10`
的执行适配器架构。这里的 adapter 是 `dstar_trade_py` 之上的业务层，不修改 vendor native SDK。

## System Boundary

```text
NautilusTrader ExecutionEngine
  |
  | SubmitOrder / CancelOrder / QueryAccount / Reconciliation
  v
DstarExecutionClient
  |
  +-- DstarConnectionManager
  +-- DstarOrderMapper
  +-- DstarEventAdapter
  +-- DstarRecoveryEngine
  +-- DstarJournal
  |
  v
dstar_trade_py.DstarTradeClient
  |
  v
pybind11 NativeTradeApi
  |
  v
libdstartradeapi.so
  |
  v
易盛启明星 V10 内盘交易系统
```

适配器只支持 Linux x86_64 + Python 3.10+。如果接入特定版本 NautilusTrader，需要再校验该版本的
Python 版本要求；较新的 NautilusTrader 版本可能要求 Python 3.12+。

## Module Responsibilities

| Module | Responsibility | Input | Output |
| --- | --- | --- | --- |
| `DstarExecutionClient` | Nautilus 执行入口，负责调用各子模块 | Nautilus commands | Nautilus execution events |
| `DstarConnectionManager` | 创建、登录、等待 ready、关闭和基础重连 | `DSTAR_TRADE_*` env/config | ready `DstarTradeClient` |
| `DstarOrderMapper` | 订单请求转换和本地状态机 | Nautilus-like order, Dstar callbacks | `ReqOrderInsert` field, lifecycle state |
| `DstarEventAdapter` | SPI callback 到 Nautilus-style event 的转换 | `rsp_order_insert`, `rtn_order`, `rtn_match` 等 | `DstarNautilusEvent` |
| `DstarRecoveryEngine` | 启动或重连后的状态恢复 | journal, query snapshots, pending callbacks | `DstarRecoveryResult` |
| `DstarJournal` | JSONL 幂等、去重和恢复索引 | intents, callbacks, emitted events | append-only records |

当前实现不直接 import NautilusTrader，而是输出 `DstarNautilusEvent` 这种轻量事件对象。真正接入
Nautilus 时，`DstarExecutionClient` 负责把它转换成 Nautilus 原生 `OrderAccepted`、
`OrderFilled`、`AccountState` 等事件。

## Startup Sequence

```text
process start
  -> load config from DSTAR_TRADE_* env
  -> create DstarConnectionManager
  -> create DstarOrderMapper(journal)
  -> create DstarEventAdapter(order_mapper, journal)
  -> create DstarRecoveryEngine(client, mapper, adapter)
  -> connection.connect()
  -> connection.login()
  -> client.wait_login(timeout)
  -> connection.wait_ready()
  -> recovery.recover()
  -> start event dispatcher loop
  -> allow Nautilus order commands
```

`wait_ready()` 是交易门槛。`login()` 或 native `Init()` 成功不能视为可交易。

## Order Submission Sequence

```text
Nautilus SubmitOrder
  -> DstarOrderMapper.map_order_to_insert_request()
       - allocate/reserve ClientReqId
       - register client_order_id
       - write dstar_order_created to journal
  -> DstarTradeClient.insert_limit_order(...)
       - local ReqOrderInsert call
       - local ret returned
  -> DstarOrderMapper.mark_submitted(ret)
       - ret=0 => Submitted only
       - ret!=0 => Rejected local failure
  -> wait for SPI callbacks
```

`ReqOrderInsert` 返回 `0` 只表示本地 API 接收了请求，不表示柜台接受、交易所排队或成交。

## Callback Sequence

```text
SDK callback thread
  -> pybind11 copies C++ struct to Python dict
  -> DstarTradeClient.on_event(...)
  -> adapter DstarEventAdapter.on_event(...)
       - Queue.put(envelope)
       - return immediately

event dispatcher thread
  -> adapter.process_next()
  -> journal callback dedupe
  -> order mapper updates lifecycle
  -> journal emitted-event dedupe
  -> DstarNautilusEvent
  -> DstarExecutionClient converts to Nautilus native event
```

callback thread 不做重连、不做阻塞查询、不直接调用 Nautilus msgbus。它只入队。

## dstar_trade_py Limitations

当前 `dstar_trade_py.DstarTradeClient` 已确认支持：

- `connect`, `login`, `wait_ready`, `close`
- `insert_order`, `insert_limit_order`, `cancel_order`
- `query_fund`, `query_position`, `query_last_client_req_id`
- SPI callback: `OnRspOrderInsert`, `OnRtnOrder`, `OnRtnMatch`, 初始化 `OnRspOrder`, `OnRspMatch`

当前未确认或未暴露：

- 主动 `query_order` / `ReqQryOrder`
- 主动 `query_trade` / `ReqQryTrade`
- 原生改单 `ReqOrderModify`
- 批量撤单

因此 recovery 对订单/成交查询是能力自适应的：如果 client 有 `query_order/query_trade` 就调用；
否则依赖 journal、初始化快照回调和实时回调恢复订单状态。
