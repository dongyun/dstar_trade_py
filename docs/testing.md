# Testing

本文说明 Dstar Execution Adapter 的测试分层和运行方式。默认测试不能连接真实交易服务器，不能真实下单。

## Test Layers

| Layer | Marker | Directory | Purpose |
| --- | --- | --- | --- |
| Unit | `unit` | `tests/unit` | mapper、state machine、journal、config、event adapter、recovery engine |
| Mock SDK | `mock_sdk` | `tests/mock_sdk` | mock `DstarTradeClient`、mock SPI callback、mock order flow |
| Integration | `integration` | `tests/integration` | 加载 native library 或非 live 安全检查，不连接交易前置 |
| Live | `live` | `tests/live` | 真实测试环境登录、查询；必须手动开启 |

`pyproject.toml` 默认配置：

```text
addopts = -ra -m 'not live'
```

所以 CI 或本地直接运行 `pytest` 不会跑 live tests。

## Commands

```bash
.venv/bin/pytest -m unit -q
.venv/bin/pytest -m mock_sdk -q
.venv/bin/pytest -m integration -q
.venv/bin/pytest -q
```

live tests 必须显式运行：

```bash
DSTAR_RUN_LIVE_TESTS=1 \
DSTAR_TRADE_IP=... \
DSTAR_TRADE_PORT=... \
DSTAR_TRADE_USER=... \
DSTAR_TRADE_PASSWORD=... \
DSTAR_TRADE_AUTH_CODE=... \
DSTAR_TRADE_APP_ID=... \
DSTAR_TRADE_LOG_PATH=/tmp/dstar/native \
.venv/bin/pytest -m live -q
```

`DSTAR_RUN_LIVE_TESTS=0` 不会启用 live tests。

## Unit Tests

Unit tests 覆盖：

- `DstarOrderMapper`: order mapping, lifecycle, unknown order recovery
- `DstarEventAdapter`: callback queue, duplicate callback, journal dedupe
- `DstarRecoveryEngine`: query recovery, trade-id dedupe, skipped capabilities
- `DstarConnectionManager`: env config, login failure, wait_ready timeout
- `OrderJournal`, `RequestIdManager`, `OrderStateManager`
- config redaction and errors

Unit tests 不创建真实 native connection。

## Mock SDK Tests

Mock SDK tests 使用 fake client：

```text
Nautilus-like order
  -> DstarOrderMapper
  -> MockDstarTradeClient.insert_limit_order()
  -> ret=0 only means Submitted
  -> mock rsp_order_insert
  -> mock rtn_order
  -> mock rtn_match
```

这些测试验证 adapter 只信 SPI 回调，不信 `ReqOrderInsert` 返回值。

## Replay Test

Replay test 回放 SPI 事件列表：

```text
rtn_match(OrderId=9001, MatchId=7001)
rsp_order_insert(ClientReqId=100, OrderId=9001)
rtn_order(OrderId=9001, PARTIAL_FILL)
rtn_match(OrderId=9001, MatchId=7002)
rtn_match(OrderId=9001, MatchId=7002)
```

断言：

- 乱序成交先到不会崩溃
- unknown order 后续合并到本地 order
- `MatchId=7002` 只产生一次 fill
- 重启后同一 journal 不重复发 fill

## Integration Tests

Integration tests 可以加载 `libdstartradeapi.so`，但不能连接交易前置。允许的检查包括：

- package import
- `get_api_version()`
- `create_and_free_api()`
- 默认 pytest 配置不跑 live

Integration tests 不调用 `connect/login/wait_ready`。

## Live Tests

Live tests 使用 `tests/live/conftest.py` gate：

```text
if DSTAR_RUN_LIVE_TESTS != "1":
    skip
if required DSTAR_TRADE_* missing:
    skip
```

当前 live tests 覆盖登录、资金查询、持仓查询和 dry-run 下单安全检查。默认不真实下单。

## Safety Requirements

- CI 默认不能跑 live。
- 默认不能真实下单。
- 所有真实交易 demo 必须 dry-run。
- 真实下单需要单独的显式确认机制。
- 测试中不能打印 password/auth/app id。
