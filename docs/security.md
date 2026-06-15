# Security

本文说明 Dstar Execution Adapter 的安全边界。目标是防止误连、误下单、凭证泄露和重复成交事件。

## Non-Negotiable Rules

- 默认测试和 demo 不能真实下单。
- CI 默认不能运行 live tests。
- `DSTAR_RUN_LIVE_TESTS` 必须等于 `1` 才允许 live tests。
- `ReqOrderInsert ret=0` 不能视为成功下单。
- 订单最终状态必须来自 SPI 回调。
- 不修改 `third_party/dstar` 或官方 SDK 解压目录下的 native 文件。
- 不打印 password、AuthCode、AppId、LicenseNo。

## Credential Handling

使用环境变量传递凭证：

```bash
export DSTAR_TRADE_IP=...
export DSTAR_TRADE_PORT=...
export DSTAR_TRADE_USER=...
export DSTAR_TRADE_PASSWORD=...
export DSTAR_TRADE_AUTH_CODE=...
export DSTAR_TRADE_APP_ID=...
```

禁止：

- 把真实凭证写入源码、测试、文档示例或 Git
- 记录 `config.to_client_kwargs()`
- 把 `.env` 提交到仓库
- 在异常信息中拼接 password/auth

允许记录：

```python
config.to_redacted_dict()
```

## Live Test Gate

```text
pytest default
  -> addopts -m "not live"
  -> live tests deselected

pytest -m live
  -> tests/live/conftest.py
  -> require DSTAR_RUN_LIVE_TESTS=1
  -> require DSTAR_TRADE_* credentials
```

`DSTAR_RUN_LIVE_TESTS=0`、空值或未设置都不是 live enabled。

## Dry-Run Order Safety

下单 demo 必须默认 dry-run：

```text
run order demo
  -> print order summary
  -> confirm_flag?
       no  -> do not call insert_order/cancel_order
       yes -> require manual YES
  -> only then call real SDK method
```

测试只能验证 dry-run 阻断路径，不能在默认 CI 中发送真实 order insert 或 cancel。

## Journal Security

Journal 用于幂等和恢复，不是审计级交易流水。

Journal 会记录：

- `client_order_id`
- `ClientReqId`
- `OrderId`
- `SystemNo`
- state snapshot
- callback/event dedupe key
- non-sensitive payload fields

Journal 会过滤：

- `password`
- `passwd`
- `auth`
- `auth_code`
- `UdpAuthCode`
- `app_id`
- `LicenseNo`
- `secret`
- `token`

生产环境应把 journal 放在权限受控目录，做轮转和备份。不要把 journal 提交到 Git。

## Native SDK Logs

官方 SDK 原生日志由 vendor library 写入，Python 层不能保证完全脱敏。

要求：

- `DSTAR_TRADE_LOG_PATH` 指向权限受控目录
- 目录不进入 Git
- 生产环境做 logrotate
- 线上排障时先脱敏再共享

## Idempotency Security

重复下单和重复成交都属于安全问题。

| Risk | Protection |
| --- | --- |
| 重复 `client_order_id` | `DstarOrderMapper` 启动时从 journal 恢复并拒绝重复 |
| 重复 `ClientReqId` | `RequestIdManager` 恢复 used ids |
| 重复 callback | `dstar_callback_seen` journal key |
| 重复 emitted event | `dstar_event_emitted` journal key |
| 重复 fill | `MatchId` / fallback match key |

## Recovery Safety

Recovery 只查询，不下单：

```text
recover
  -> query_order if available
  -> query_trade if available
  -> query_position
  -> query_fund
  -> drain pending callbacks
```

当前 `dstar_trade_py` 没有主动 `query_order/query_trade`，engine 会跳过这些 capability，不会假装已经恢复服务端全部历史订单。

## Operational Controls

生产系统还需要上层风控：

- 账号白名单
- 合约白名单
- 最大手数
- 最大名义金额
- 交易时段限制
- kill switch
- 单策略限频
- 人工确认或审批机制

这些不属于 `dstar_trade_py` native binding 能力，必须在 Execution Adapter 或更上层系统实现。
