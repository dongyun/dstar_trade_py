# Python API Reference

本文档列出 `dstar_trade_py` 的主要公开 Python API。所有真实交易接口仅支持 Linux。

## 模块级函数和常量

### `get_api_version() -> str`

创建一个官方 API 实例，调用 `GetApiVersion()`，释放实例后返回版本字符串。

异常：

- `RuntimeError`：非 Linux 平台或官方 API 创建失败。
- `ImportError`：Linux 下 native 扩展或 vendor 动态库加载失败。

```python
import dstar_trade_py as dstar

print(dstar.get_api_version())
```

### `create_and_free_api() -> bool`

创建并立即释放官方 API 实例，用于验证动态库能否加载。

```python
import dstar_trade_py as dstar

assert dstar.create_and_free_api() is True
```

### `IS_LINUX_BUILD`

native 扩展构建平台标识。Linux native 构建为 `True`；非 Linux fallback 为 `False`。

### `SDK_PROTOCOL_VERSION`

官方头文件中的协议版本常量。

## `NativeTradeApi`

pybind11 暴露的底层桥接类，直接代理官方 `IDstarTradeApi`。生产业务优先使用 `DstarTradeClient`。

生命周期：

- 构造函数调用 `CreateDstarTradeApi()`。
- 析构函数调用 `FreeDstarTradeApi()`。
- 不暴露 `IDstarTradeApi*` 裸指针。

方法：

| 方法 | 参数 | 返回值 | 说明 |
| --- | --- | --- | --- |
| `register_callback(dispatcher)` | `dispatcher` 必须有 `on_event(event_name, payload)` | `None` | 注册 Python 回调 dispatcher。 |
| `register_front_address(ip, port)` | `ip: str`, `port: int` | `None` | 注册交易前置地址。 |
| `set_api_log_path(path)` | `path: str` | `None` | 设置官方 SDK 原生日志目录。 |
| `set_login_info(login_info)` | `DstarApiReqLoginField` dict | `None` | 设置登录信息。 |
| `set_cpu_id(recv_notice_cpu_id, log_cpu_id)` | `int, int` | `None` | 设置 CPU 绑定。 |
| `set_subscribe_start_id(start_id)` | `int` | `None` | 设置通知流订阅起点。 |
| `set_real_time_data_filter(filter)` | `int` | `None` | 设置实时数据过滤。 |
| `set_run_mode(mode)` | `int` | `None` | 设置运行模式。 |
| `get_system_info()` | 无 | `dict` | 返回 `return_code`、`length`、`auth_key_version`、`system_info`。 |
| `set_submit_info(submit_info)` | `DstarApiSubmitInfoField` dict | `None` | 设置看穿式上报信息。 |
| `set_init_qry_info(init_qry_info)` | `DstarApiInitQryInfoField` dict | `None` | 设置初始化查询范围。 |
| `init()` | 无 | `int` | 调用官方 `Init()`。 |
| `req_last_client_req_id()` | 无 | `int` | 请求最新客户请求号。 |
| `req_pwd_mod(data)` | `DstarApiReqPwdModField` dict | `int` | 修改密码请求。 |
| `req_order_insert(data)` | `DstarApiReqOrderInsertField` dict | `int` | 普通报单请求。 |
| `req_offer_insert(data)` | `DstarApiReqOfferInsertField` dict | `int` | 报价请求。 |
| `req_offer_insert_new(data)` | `DstarApiReqOfferInsertNewField` dict | `int` | 新版报价请求。 |
| `req_order_delete(data)` | `DstarApiReqOrderDeleteField` dict | `int` | 撤单请求。 |
| `req_cmb_order_insert(data)` | `DstarApiReqCmbOrderInsertField` dict | `int` | 组合报单请求。 |
| `req_qry_fund()` | 无 | `int` | 资金查询请求。 |
| `req_qry_position()` | 无 | `int` | 持仓查询请求。 |
| `get_api_version()` | 无 | `str` | 返回官方 API 版本。 |

异常：

- `ValueError`：dict 入参缺少官方结构体字段，或字符串超过固定 char 数组长度。
- `RuntimeError`：native API 创建失败。

示例：

```python
from dstar_trade_py import NativeTradeApi
from dstar_trade_py.fields import DstarApiInitQryInfoField

class Dispatcher:
    def on_event(self, event_name: str, payload: dict) -> None:
        print("[示例格式]", event_name, payload)

api = NativeTradeApi()
api.register_callback(Dispatcher())
api.register_front_address("61.163.243.173", 6668)
api.set_init_qry_info(DstarApiInitQryInfoField().to_dict())
```

## `DstarTradeClient`

同步高层客户端。构造参数：

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `front_ip` | `str | None` | `None` | 交易前置 IP。 |
| `front_port` | `int | None` | `None` | 交易前置端口，测试环境通常为 `6668`。 |
| `account_no` | `str` | `""` | 账号。 |
| `password` | `str` | `""` | 密码，不应写入日志。 |
| `app_id` | `str` | `""` | APPID。 |
| `license_no` | `str` | `""` | AuthCode/LicenseNo。 |
| `api_log_path` | `str` | `""` | 官方 SDK 原生日志路径。 |
| `recv_notice_cpu_id` | `int` | `-1` | 通知接收线程 CPU 绑定。 |
| `log_cpu_id` | `int` | `-1` | 日志线程 CPU 绑定。 |
| `subscribe_start_id` | `int` | `-1` | 通知流订阅起点。 |
| `real_time_data_filter` | `int` | `RealTimeDataFilter.NONE` | 实时数据过滤。 |
| `run_mode` | `int` | `RunMode.FULL_LOAD` | 运行模式。 |
| `submit_info` | dataclass/dict/None | `None` | 看穿式上报信息。 |
| `init_qry_info` | dataclass/dict/None | `None` | 初始化查询配置。 |
| `journal_path` | `str | Path` | `logs/order_journal.jsonl` | 本地订单 journal。 |
| `api_factory` | callable | `NativeTradeApi` | 测试注入 fake native。 |

状态属性：

`created`、`initialized`、`connected`、`logged_in`、`api_ready`、`disconnected`。

事件队列：

`raw_events`、`order_events`、`trade_events`、`fund_events`、`position_events`。

### 生命周期方法

| 方法 | 返回值 | 异常 | 说明 |
| --- | --- | --- | --- |
| `connect(front_ip=None, front_port=None)` | `None` | `ValueError`, `DstarRequestError` | 注册回调、前置地址和本地配置。 |
| `login(account_no=None, password=None, app_id=None, license_no=None)` | `None` | `DstarError` | 设置登录信息并调用 `Init()`。 |
| `wait_ready(timeout=30)` | `None` | `DstarTimeoutError` | 等待 `api_ready`。 |
| `close()` | `None` | 无 | 释放 native API 引用。 |
| `get_system_info()` | `dict` | `DstarNativeError` 等 | 采集系统授权信息。 |
| `get_api_version()` | `str` | `RuntimeError` | 获取 API 版本。 |

### 查询方法

| 方法 | 返回值 | 说明 |
| --- | --- | --- |
| `query_fund(timeout=5)` | `DstarApiFundField` | 请求资金并等待 `rsp_qry_fund`。 |
| `query_position(timeout=5)` | `list[DstarApiPositionField]` | 请求持仓并等待 `rsp_qry_position last=True`。 |
| `query_last_client_req_id(timeout=5)` | `int` | 查询柜台最新客户请求号，并更新本地 `RequestIdManager`。 |

异常：

- `DstarRequestError`：API 未 ready、上次查询未完成、请求被拒绝。
- `DstarTimeoutError`：等待回调超时。

### 下单和撤单方法

| 方法 | 返回值 | 说明 |
| --- | --- | --- |
| `insert_order(...)` | `int` | 普通报单，直接基于 `DstarApiReqOrderInsertField` 字段。 |
| `insert_limit_order(**kwargs)` | `int` | 限价单 helper。 |
| `insert_market_order_if_supported(**kwargs)` | `int` | 市价单 helper，是否支持以后续回报为准。 |
| `insert_combo_order(**kwargs)` | `int` | 组合报单别名。 |
| `insert_cmb_order(...)` | `int` | 组合报单。 |
| `insert_offer(...)` | `int` | 报价请求。 |
| `insert_offer_new(...)` | `int` | 新版报价请求。 |
| `cancel_order(...)` | `int` | 撤单。 |
| `cancel_offer_if_supported(**kwargs)` | `int` | 报价撤销，底层复用 `ReqOrderDelete`。 |
| `modify_password(new_password, old_password)` | `int` | 修改密码。 |

重要：返回值 `0` 只表示本地请求同步返回成功，不代表最终委托成功、撤单成功或成交成功。

示例：

```python
from dstar_trade_py import DstarTradeClient
from dstar_trade_py.enums import Direction, Hedge, Offset, ValidType

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
    client.wait_ready()
    ret = client.insert_limit_order(
        direct=int(Direction.BUY),
        offset=int(Offset.OPEN),
        hedge=int(Hedge.SPECULATE),
        valid_type=int(ValidType.GFD),
        account_index=1,
        contract_index=12345,
        contract_no="rb2410",
        order_qty=1,
        order_price=3000.0,
        client_order_id="my-biz-order-001",
    )
    print("[示例格式] ReqOrderInsert local return code:", ret)
finally:
    client.close()
```

## `AsyncDstarTradeClient`

asyncio 风格客户端，复用同步客户端逻辑，但回调线程通过 `loop.call_soon_threadsafe` 投递事件。

异步方法：

- `await connect(...)`
- `await login(...)`
- `await wait_ready(timeout=30)`
- `await query_fund(timeout=5)`
- `await query_position(timeout=5)`
- `await query_last_client_req_id(timeout=5)`
- `await insert_order(...)`
- `await insert_limit_order(...)`
- `await insert_market_order_if_supported(...)`
- `await insert_offer(...)`
- `await insert_offer_new(...)`
- `await insert_cmb_order(...)`
- `await insert_combo_order(...)`
- `await cancel_order(...)`
- `await cancel_offer_if_supported(...)`
- `await modify_password(...)`
- `await close()`

异步迭代器：

- `iter_events()`：全部事件。
- `iter_orders()`：委托相关事件。
- `iter_trades()`：成交事件。

示例：

```python
import asyncio
from dstar_trade_py import AsyncDstarTradeClient

async def main() -> None:
    client = AsyncDstarTradeClient(
        front_ip="61.163.243.173",
        front_port=6668,
        account_no="你的账号",
        password="你的密码",
        app_id="你的APPID",
        license_no="你的AuthCode",
    )
    try:
        await client.connect()
        await client.login()
        await client.wait_ready()
        fund = await client.query_fund()
        print("[示例格式] fund:", fund)
    finally:
        await client.close()

asyncio.run(main())
```

## Builder 类

### `OrderRequestBuilder`

只构造官方请求结构体对应 dataclass，不凭空增加官方没有的字段。

| 方法 | 返回值 | 说明 |
| --- | --- | --- |
| `limit_order(...)` | `DstarApiReqOrderInsertField` | 限价普通报单。 |
| `market_order_if_supported(...)` | `DstarApiReqOrderInsertField` | 市价普通报单。 |
| `combo_order(...)` | `DstarApiReqCmbOrderInsertField` | 组合报单。 |
| `offer(...)` | `DstarApiReqOfferInsertField` | 报价。 |

### `CancelRequestBuilder`

| 方法 | 返回值 | 说明 |
| --- | --- | --- |
| `order_delete(...)` | `DstarApiReqOrderDeleteField` | 撤单。 |
| `offer_delete_if_supported(...)` | `DstarApiReqOrderDeleteField` | 报价撤销尝试。 |

## 配置与安全

### `DstarTradeConfig`

从环境变量加载连接和登录配置。

```python
from dstar_trade_py import DstarTradeClient, DstarTradeConfig

config = DstarTradeConfig.from_env(require_credentials=True)
config.ensure_native_log_path()
client = DstarTradeClient(**config.to_client_kwargs())
print(config.to_redacted_dict())
```

### `configure_logging(level=None)`

配置 `dstar_trade_py` package logger，并安装脱敏 filter。

```python
from dstar_trade_py import configure_logging

configure_logging("INFO")
```

### `redact_sensitive(value)` / `redact_text(message)`

递归脱敏 dict/dataclass 或日志文本中的 `password`、`auth_code`、`app_id`、`LicenseNo`、`UdpAuthCode` 等字段。

## 请求号、状态机和 Journal

### `OrderJournal`

- `append(event_type, **data) -> None`
- `read_records() -> list[dict]`

默认路径：`logs/order_journal.jsonl`。写入前会过滤敏感字段。

### `RequestIdManager`

- `from_journal(journal, remote_last_id=None, jump_threshold=1000)`
- `update_from_remote(remote_last_id) -> None`
- `next_id() -> int`
- `reserve(client_req_id) -> int`
- `has_used(client_req_id) -> bool`

### `OrderStateManager`

- `from_journal(journal)`
- `register_submission(client_order_id, client_req_id)`
- `on_rsp_order_insert(response)`
- `on_rtn_order(order)`
- `on_rtn_match(match)`
- `get(client_order_id)`

示例：

```python
from dstar_trade_py import OrderJournal, RequestIdManager

journal = OrderJournal("logs/order_journal.jsonl")
manager = RequestIdManager.from_journal(journal)
client_req_id = manager.next_id()
print("[示例格式] next ClientReqId:", client_req_id)
```

## 数据模型

所有结构体 dataclass 继承 `DstarField`：

- `from_dict(data) -> dataclass`
- `to_dict() -> dict`

示例：

```python
from dstar_trade_py.fields import DstarApiFundField

fund = DstarApiFundField.from_dict({"AccountNo": "demo", "Equity": 100000.0})
assert fund.Equity == 100000.0
assert fund.to_dict()["AccountNo"] == "demo"
```

完整结构体列表见 [`field_mapping.md`](field_mapping.md)。

## 错误和异常

异常基类：`DstarError`。

子类：

- `DstarNativeError`
- `DstarConnectionError`
- `DstarAuthError`
- `DstarRequestError`
- `DstarTimeoutError`

统一处理：

```python
from dstar_trade_py import NativeTradeApi, raise_for_error

native_api = NativeTradeApi()
ret = native_api.req_qry_fund()
raise_for_error(ret, "ReqQryFund")
```

业务代码通常不需要直接调用 native 方法，高层 client 已经内置 `raise_for_error`。
