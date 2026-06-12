# dstar_trade_py 架构说明

本文说明 `dstar_trade_py` 如何把易盛启明星 V10 内盘交易 C++ SDK 封装为 Linux-only Python SDK。

## 整体架构

```text
Python 应用
  |
  | 调用同步/异步高层客户端
  v
dstar_trade_py.client / dstar_trade_py.async_client
  |
  | 传入 dict / dataclass，接收 dataclass / 事件队列
  v
pybind11 扩展 dstar_trade_py._dstar_trade_py
  |
  | 持有 IDstarTradeApi*，注册 IDstarTradeSpi adapter
  v
官方 C++ SDK: libdstartradeapi.so
  |
  | TCP/UDP 与交易前置、柜台通信
  v
易盛测试或生产交易环境
```

项目分层：

| 层级 | 目录/模块 | 职责 |
| --- | --- | --- |
| 官方 SDK | `third_party/dstar/` | 官方头文件和 `libdstartradeapi.so`，不修改。 |
| C++ binding | `cpp/` | pybind11 扩展、结构体转换、SPI 回调适配、RAII 生命周期。 |
| Python 数据层 | `fields.py`、`enums.py`、`errors.py` | dataclass、枚举、错误码和异常体系。 |
| Python client | `client.py` | 同步高层 API、状态机、事件队列、请求号和 journal。 |
| asyncio client | `async_client.py` | asyncio 包装，线程安全投递回调到事件循环。 |
| 配置与安全 | `config.py`、`order_management.py` | 环境变量、日志脱敏、请求号、订单状态、幂等保护。 |
| 示例和测试 | `examples/`、`tests/` | dry-run demo、unit/integration/live tests。 |

## C++ SDK、pybind11、Python Client 的关系

官方接口核心是两个 C++ virtual class：

- `IDstarTradeApi`：主动接口，例如 `Init`、`ReqOrderInsert`、`ReqQryFund`。
- `IDstarTradeSpi`：回调接口，例如 `OnRspUserLogin`、`OnRtnOrder`、`OnRtnMatch`。

Python 不能用 `ctypes` 安全调用 C++ virtual class，因此本项目使用 pybind11：

- `NativeTradeApi` 在 C++ 中持有 `IDstarTradeApi*`。
- 构造函数调用 `CreateDstarTradeApi()`。
- 析构函数调用 `FreeDstarTradeApi()`。
- Python 只看到 `NativeTradeApi` 方法，不接触裸指针。
- C++ 回调把官方结构体立即复制为 Python-owned `dict`，再交给 Python dispatcher。

示例：

```python
from dstar_trade_py import NativeTradeApi

api = NativeTradeApi()
print(api.get_api_version())
api.set_api_log_path("/tmp/dstar/native")
```

这段代码只演示本地 API 对象生命周期，不连接真实交易服务器。

## 回调线程模型

官方 SDK 的 SPI 回调可能运行在 SDK 自己的工作线程，而不是 Python 主线程。

C++ adapter 的处理原则：

1. 回调进入 `PyTradeSpiAdapter::OnXXX`。
2. 立即把官方结构体指针复制为 `py::dict`，不把指针交给 Python 保存。
3. 获取 Python GIL。
4. 调用 Python dispatcher：`dispatcher.on_event(event_name, payload)`。
5. 捕获所有 Python/C++ 异常，不能让异常穿透回官方 SDK。

同步客户端的事件流：

```text
SDK 回调线程
  -> C++ adapter 获取 GIL
  -> DstarTradeClient.on_event(...)
  -> 转 dataclass
  -> 更新状态
  -> 写 raw_events / order_events / trade_events
  -> notify Condition
```

asyncio 客户端的事件流：

```text
SDK 回调线程
  -> AsyncDstarTradeClient.on_event(...)
  -> loop.call_soon_threadsafe(...)
  -> 事件循环线程中转换 dataclass、更新状态、唤醒 Future
```

不能在 SDK 回调线程直接操作 `asyncio.Future`，否则会破坏 asyncio 对象的线程亲和性。

## 生命周期

同步客户端推荐流程：

```python
from dstar_trade_py import DstarTradeClient

client = DstarTradeClient(
    front_ip="61.163.243.173",
    front_port=6668,
    account_no="你的账号",
    password="你的密码",
    app_id="你的APPID",
    license_no="你的AuthCode",
    api_log_path="/tmp/dstar/native",
)

try:
    client.connect()
    client.login()
    client.wait_ready(timeout=30)
    fund = client.query_fund(timeout=5)
    print(fund)
finally:
    client.close()
```

生命周期状态：

| 状态 | 含义 |
| --- | --- |
| `created` | Python client 已创建 native API 对象。 |
| `connected` | 已注册 callback、前置地址和本地参数；真实连接由 `Init` 触发。 |
| `initialized` | `Init()` 本地同步返回成功。 |
| `logged_in` | 收到 `rsp_user_login` 且错误码为 0。 |
| `api_ready` | 收到 `api_ready`，允许查询和下单。 |
| `disconnected` | 收到断线或关闭状态。 |

注意：`Init()` 返回 0 不代表登录完成，`ReqOrderInsert()` 返回 0 不代表委托最终成功。最终状态必须以后续回报为准。

## 请求、回报和状态

下单路径：

```text
insert_limit_order(...)
  -> 分配/预留 ClientReqId
  -> 检查 client_order_id 幂等
  -> 转 DstarApiReqOrderInsertField dict
  -> NativeTradeApi.req_order_insert(...)
  -> 写 order_journal.jsonl
  -> 返回本地同步 ret
```

回报路径：

```text
OnRspOrderInsert -> rsp_order_insert -> OrderStateManager.on_rsp_order_insert
OnRtnOrder       -> rtn_order        -> OrderStateManager.on_rtn_order
OnRtnMatch       -> rtn_match        -> OrderStateManager.on_rtn_match
```

示例格式，非真实交易结果：

```text
[示例格式] ReqOrderInsert local return code: 0
[示例格式] rsp_order_insert: ErrCode=0, OrderId=10001
[示例格式] rtn_order: OrderState=50, MatchQty=0
[示例格式] rtn_match: MatchQty=1, MatchPrice=3000.0
```

上述数字只是格式示例，不代表真实柜台或交易所返回。

## Linux-only 边界

- CMake 在非 Linux 平台拒绝构建。
- Python 包在非 Linux 平台可以 import 纯 Python 辅助模块。
- 非 Linux 平台创建 `NativeTradeApi()`、调用 `get_api_version()` 或 `create_and_free_api()` 会抛出清晰错误。
- 真实交易功能只支持 Linux + 官方 `libdstartradeapi.so`。
