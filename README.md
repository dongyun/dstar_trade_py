# dstar_trade_py


`dstar_trade_py` 是一个 Linux-only Python SDK 项目，用于代理易盛启明星 V10 内盘交易 API。

项目提供：

- pybind11 + CMake native binding；
- 官方结构体到 Python dataclass 的映射；
- 同步 `DstarTradeClient`；
- asyncio 风格 `AsyncDstarTradeClient`；
- SPI 回调统一 dispatcher；
- 请求号管理、订单状态机、幂等保护和本地 journal；
- 环境变量配置、日志脱敏和 guarded live demo。

## 平台支持

仅支持 Linux x86-64，Python 版本要求 `>=3.10`。Windows 和 macOS 不支持官方 Linux 动态库。

非 Linux 平台可以 import 纯 Python 辅助模块，但创建 `NativeTradeApi()`、调用
`get_api_version()` 或 `create_and_free_api()` 会抛出清晰的 Linux-only 错误。

官方 SDK 文件约定放在：

```text
third_party/dstar/include/
third_party/dstar/lib/linux/libdstartradeapi.so
```

不要修改官方 SDK 原始文件。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'

export LD_LIBRARY_PATH="$PWD/third_party/dstar/lib/linux:${LD_LIBRARY_PATH:-}"
./scripts/check_env.sh
python -m pytest
```

验证 native API 本地生命周期，不连接真实交易服务器：

```bash
python - <<'PY'
import dstar_trade_py as dstar

print(dstar.get_api_version())
print(dstar.create_and_free_api())
PY
```

## 配置示例

真实测试 demo 从环境变量读取配置，不要在代码中写死账号密码：

```bash
export DSTAR_TRADE_IP=61.163.243.173
export DSTAR_TRADE_PORT=6668
export DSTAR_TRADE_USER=你的模拟账号
export DSTAR_TRADE_PASSWORD=你的模拟密码
export DSTAR_TRADE_AUTH_CODE=Demo_TestCollect
export DSTAR_TRADE_APP_ID=Demo_TestCollect
export DSTAR_TRADE_LOG_PATH=/tmp/dstar_trade_py/native_logs
```

Python 加载配置：

```python
from dstar_trade_py import DstarTradeClient, DstarTradeConfig, configure_logging

configure_logging("INFO")
config = DstarTradeConfig.from_env(require_credentials=True)
config.ensure_native_log_path()
client = DstarTradeClient(**config.to_client_kwargs())
```

## 基础使用

查询资金示例：

```python
from dstar_trade_py import DstarTradeClient

client = DstarTradeClient(
    front_ip="61.163.243.173",
    front_port=6668,
    account_no="你的账号",
    password="你的密码",
    app_id="你的APPID",
    license_no="你的AuthCode",
    api_log_path="/tmp/dstar_trade_py/native_logs",
)

try:
    client.connect()
    client.login()
    client.wait_ready(timeout=30)
    fund = client.query_fund(timeout=5)
    print("[示例格式] fund:", fund)
finally:
    client.close()
```

示例输出中的字段和值必须以真实环境返回为准；不要把文档中的示例格式当作真实交易结果。

## 测试

```bash
python -m pytest
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration
./scripts/run_tests.sh live
./scripts/run_tests.sh all
```

测试分类：

- `unit`：不连接真实服务器，不依赖真实账号。
- `integration`：可加载真实 `libdstartradeapi.so`，但不连接服务器。
- `live`：需要真实测试账号和 `DSTAR_RUN_LIVE_TESTS=1`，默认跳过。

默认 `python -m pytest` 不运行 live tests。

## 文档导航

核心文档：

- [架构说明](docs/architecture.md)：整体架构、pybind11 关系、回调线程模型、生命周期。
- [Linux 环境配置](docs/linux_setup.md)：依赖安装、动态库配置、权限问题。
- [Python API Reference](docs/api_reference.md)：公开类、方法、参数、返回值和异常。
- [IDstarTradeApi 映射](docs/native_api_mapping.md)：C++ 主动接口到 Python 的映射。
- [IDstarTradeSpi 回调覆盖](docs/callback_coverage.md)：全部回调、event_name 和 payload。
- [字段映射](docs/field_mapping.md)：C++ typedef/结构体到 Python dataclass 的映射。
- [真实测试 Demo](docs/live_testing.md)：测试环境、环境变量、demo 运行方式和风险提示。
- [订单 API](docs/order_api.md)：下单、撤单、订单状态、成交回报、请求号管理。
- [订单状态机](docs/order_state_machine.md)：本地状态流转、journal 和幂等保护。
- [错误码与异常](docs/error_codes.md)：官方错误码和 Python 异常映射。
- [安全说明](docs/security.md)：凭据、下单确认、journal 脱敏和日志脱敏。
- [开发指南](docs/development_guide.md)：继续开发、字段扩展、C++ binding 调试、动态库排查。

背景分析和覆盖报告：

- [SDK 分析](docs/sdk_analysis.md)
- [主动接口覆盖矩阵](docs/api_coverage.md)

## 安全边界

- 不提交真实账号、密码、AuthCode、APPID。
- live 下单 demo 默认 dry-run，必须显式确认才会发送真实请求。
- `ReqOrderInsert` 返回 `0` 不代表交易所接收或成交成功。
- 最终订单状态以 `OnRspOrderInsert`、`OnRtnOrder`、`OnRtnMatch` 等回调为准。
- journal 和 Python logging 会做脱敏，但官方 SDK 原生日志内容由 vendor 动态库生成，应放在权限受控目录。

## 许可

本项目自身代码按仓库许可管理。官方 SDK 的使用和再分发受易盛官方授权条款约束。
