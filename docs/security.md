# 安全说明

本文档说明 `dstar_trade_py` 对账号、密码、授权码、APPID、下单确认和本地日志的处理边界。

## 不提交账号密码

不要把真实账号、密码、AuthCode、APPID 写入源码、测试、示例或文档。也不要把这些值写入
`.env` 后提交到 Git。

推荐做法：

```bash
export DSTAR_TRADE_IP=61.163.243.173
export DSTAR_TRADE_PORT=6668
export DSTAR_TRADE_USER=你的模拟账号
export DSTAR_TRADE_PASSWORD=你的模拟密码
export DSTAR_TRADE_AUTH_CODE=你的授权码
export DSTAR_TRADE_APP_ID=你的APPID
export DSTAR_TRADE_LOG_PATH=/tmp/dstar_trade_py/native_logs
```

## 环境变量配置

`dstar_trade_py.config.DstarTradeConfig` 支持从 `DSTAR_TRADE_*` 环境变量加载配置：

```python
from dstar_trade_py.config import load_config_from_env

config = load_config_from_env(require_credentials=True)
client_kwargs = config.to_client_kwargs()
```

打印或记录配置时使用：

```python
config.to_redacted_dict()
```

该方法会脱敏 `password`、`auth_code`、`app_id` 以及 `UdpAuthCode`、`LicenseNo` 等授权字段变体。

## 下单 Demo 确认机制

真实下单 demo 默认 dry-run，不会发送真实请求。必须显式传入 `--confirm-live-order`，并在二次
确认提示中手工输入 `YES`，才会调用真实下单或撤单接口。

这只是一层示例保护，不替代生产系统的风控。生产系统仍应实现：

- 交易账号白名单；
- 合约白名单；
- 最大手数和最大金额限制；
- 重复下单保护；
- 请求号和业务订单号管理；
- 人工或系统级 kill switch。

## Journal 脱敏

本地订单 journal 默认写入：

```text
logs/order_journal.jsonl
```

journal 用于恢复近期请求号、`client_order_id` 幂等键和订单状态。写入前会递归过滤敏感字段，
包括但不限于：

- `password`
- `passwd`
- `auth_code`
- `UdpAuthCode`
- `app_id`
- `AppId`
- `LicenseNo`
- `secret`
- `token`

journal 不是审计级交易流水。生产环境如果要长期保存，应放在权限受控目录，并按业务合规要求
做轮转、备份和清理。

## 日志脱敏

项目使用 Python `logging`，并提供 `SensitiveDataFilter`：

```python
from dstar_trade_py import configure_logging

configure_logging("INFO")
```

该 filter 会对日志文本中的密码、AuthCode、APPID、LicenseNo、token 等字段进行脱敏。不要绕过
SDK 的日志工具直接打印完整配置，也不要在业务日志里记录完整请求 payload。

官方 SDK 原生日志路径由 `api_log_path` / `DSTAR_TRADE_LOG_PATH` 控制。官方原生日志的内容由
vendor 动态库生成，Python 层无法保证其中所有字段都已脱敏，因此该目录必须设置严格文件权限。

## Linux 权限边界

`GetSystemInfo` 可能读取系统硬件信息，某些机器上需要 root 或 sudo 才能获取完整数据。不要为了
方便长期用 root 运行交易进程；如果授权采集需要提升权限，应把采集步骤和交易进程权限分离。
