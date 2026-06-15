# Configuration

本文说明 Dstar Execution Adapter 的运行配置。配置入口是环境变量和 `DstarTradeConfig`。

## Required Environment Variables

| Variable | Required | Used by | Notes |
| --- | --- | --- | --- |
| `DSTAR_TRADE_IP` | yes | `DstarConnectionManager` | 交易前置 IP |
| `DSTAR_TRADE_PORT` | yes | `DstarConnectionManager` | 交易前置端口，必须是整数 |
| `DSTAR_TRADE_USER` | yes | `DstarTradeClient` | 账号 |
| `DSTAR_TRADE_PASSWORD` | yes | `DstarTradeClient` | 密码，禁止打印 |
| `DSTAR_TRADE_AUTH_CODE` | yes | `DstarTradeClient` | AuthCode / LicenseNo，禁止打印 |
| `DSTAR_TRADE_APP_ID` | yes | `DstarTradeClient` | AppId，禁止打印 |
| `DSTAR_TRADE_LOG_PATH` | no | native SDK | 官方 SDK 原生日志目录 |
| `DSTAR_TRADE_LOG_LEVEL` | no | Python logging | 默认 `INFO` |
| `DSTAR_RUN_LIVE_TESTS` | live tests only | pytest live layer | 必须等于 `1` 才运行 live tests |

## Loading Configuration

```python
from dstar_trade_py import DstarConnectionManager

manager = DstarConnectionManager()
manager.connect()
manager.login()
manager.wait_ready()
```

`DstarConnectionManager` 默认调用 `load_config_from_env(require_credentials=True)`。缺少必填变量时会失败，不会创建
native client。

## Redacted Logging

```python
from dstar_trade_py import configure_logging, load_config_from_env

configure_logging("INFO")
config = load_config_from_env(require_credentials=True)
print(config.to_redacted_dict())
```

`to_redacted_dict()` 会遮蔽：

- `password`
- `auth_code`
- `app_id`
- `LicenseNo`
- `UdpAuthCode`
- `token`, `secret`

不要把 `config.to_client_kwargs()` 直接写入日志。

## Native Log Path

`DSTAR_TRADE_LOG_PATH` 传给官方 SDK。Python 层无法保证 vendor 原生日志完全脱敏，因此生产环境应：

- 使用权限受控目录，例如 `/var/log/dstar-trade/native`
- 禁止普通用户读取
- 做轮转和清理
- 不把该目录提交到 Git

## Adapter Construction

```text
load env
  -> DstarTradeConfig
  -> DstarConnectionManager
  -> DstarTradeClient(front_ip, front_port, account_no, password, app_id, license_no)
  -> connect/login/wait_ready
```

## Timeout Settings

`DstarConnectionManager` 支持：

| Setting | Default purpose |
| --- | --- |
| `connect_timeout` | 连接配置阶段保护 |
| `login_timeout` | 等待 `rsp_user_login` |
| `ready_timeout` | 等待 `api_ready` |
| `reconnect_attempts` | 基础重连次数 |
| `reconnect_delay` | 重连间隔 |

`DstarTradeClient` 必须 `wait_ready(timeout)` 成功后才能进入交易状态。

## Configuration Limitations

- 当前配置不保存到磁盘；如需配置文件，应由上层应用加载后传入 config object。
- 环境变量适合部署和 CI；不要把真实 `.env` 提交到 Git。
- live test gate 是测试层保护，不等于生产风控。生产仍需要账号、合约、数量、金额和 kill switch 限制。
