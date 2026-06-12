# IDstarTradeApi 到 Python 映射

本文对照 `third_party/dstar/include/DstarTradeApi.h`，说明官方 `IDstarTradeApi` 主动接口在 Python 中的映射。

结论：

- pybind11 native 层覆盖全部主动接口。
- 同步 `DstarTradeClient` 覆盖全部适合高层调用的接口。
- `AsyncDstarTradeClient` 提供对应 asyncio 方法。
- `CreateDstarTradeApi` / `FreeDstarTradeApi` 不暴露裸指针，统一由 RAII 和 client 生命周期管理。

## 映射表

| C++ 接口 | NativeTradeApi | DstarTradeClient | AsyncDstarTradeClient | 说明 |
| --- | --- | --- | --- | --- |
| `RegisterSpi` | `register_callback(dispatcher)` | `connect()` | `await connect()` | 高层自动注册 `on_event` dispatcher。 |
| `RegisterFrontAddress` | `register_front_address(ip, port)` | `connect(front_ip, front_port)` | `await connect(...)` | 注册交易前置地址。 |
| `SetApiLogPath` | `set_api_log_path(path)` | 构造参数 `api_log_path` + `connect()` | 同步配置 | 官方 SDK 原生日志路径。 |
| `SetLoginInfo` | `set_login_info(login_info)` | `login(...)` | `await login(...)` | 登录信息在 `Init()` 前设置。 |
| `SetCpuId` | `set_cpu_id(recv_notice_cpu_id, log_cpu_id)` | 构造参数 + `connect()` | 同步配置 | 默认 `-1` 不绑定。 |
| `SetSubscribeStartId` | `set_subscribe_start_id(start_id)` | 构造参数 + `connect()` | 同步配置 | 默认 `-1` 从最新通知开始。 |
| `SetRealTimeDataFilter` | `set_real_time_data_filter(filter)` | 构造参数 + `connect()` | 同步配置 | 使用 `RealTimeDataFilter` int。 |
| `SetRunMode` | `set_run_mode(mode)` | 构造参数 + `connect()` | 同步配置 | 使用 `RunMode` int。 |
| `GetSystemInfo` | `get_system_info()` | `get_system_info()` | `await get_system_info()` | 可能需要系统权限。 |
| `SetSubmitInfo` | `set_submit_info(submit_info)` | 构造参数 `submit_info` + `connect()` | 同步配置 | 看穿式信息。 |
| `SetInitQryInfo` | `set_init_qry_info(init_qry_info)` | 构造参数 `init_qry_info` + `connect()` | 同步配置 | 初始化查询范围。 |
| `Init` | `init()` | `login()` | `await login()` | `Init()` 返回 0 不代表已 ready。 |
| `ReqLastClientReqId` | `req_last_client_req_id()` | `query_last_client_req_id(timeout)` | `await query_last_client_req_id(timeout)` | 收到回调后更新本地请求号管理器。 |
| `ReqPwdMod` | `req_pwd_mod(data)` | `modify_password(new_password, old_password)` | `await modify_password(...)` | 改密 demo 默认 dry-run。 |
| `ReqOrderInsert` | `req_order_insert(data)` | `insert_order(...)` / `insert_limit_order(...)` | `await insert_order(...)` | 返回本地同步码，不代表成交。 |
| `ReqOfferInsert` | `req_offer_insert(data)` | `insert_offer(...)` | `await insert_offer(...)` | 报价请求。 |
| `ReqOfferInsertNew` | `req_offer_insert_new(data)` | `insert_offer_new(...)` | `await insert_offer_new(...)` | 新版报价请求。 |
| `ReqOrderDelete` | `req_order_delete(data)` | `cancel_order(...)` | `await cancel_order(...)` | 撤单请求。 |
| `ReqCmbOrderInsert` | `req_cmb_order_insert(data)` | `insert_cmb_order(...)` / `insert_combo_order(...)` | `await insert_cmb_order(...)` | 组合报单。 |
| `ReqQryFund` | `req_qry_fund()` | `query_fund(timeout)` | `await query_fund(timeout)` | 同步等待 `rsp_qry_fund`。 |
| `ReqQryPosition` | `req_qry_position()` | `query_position(timeout)` | `await query_position(timeout)` | 聚合到 `last=True`。 |
| `GetApiVersion` | `get_api_version()` | `get_api_version()` | `await get_api_version()` | 不连接服务器。 |
| `CreateDstarTradeApi` | `NativeTradeApi()` / `create_and_free_api()` | 构造 client 时调用 | 构造 async client 时调用 | 不暴露裸指针。 |
| `FreeDstarTradeApi` | `NativeTradeApi` 析构 | `close()` 释放引用 | `await close()` | 不在 SPI 回调中释放。 |

## Native 调用示例

只验证本地动态库和 API 对象生命周期，不连接真实服务器：

```python
from dstar_trade_py import NativeTradeApi, create_and_free_api

print(create_and_free_api())
api = NativeTradeApi()
print(api.get_api_version())
```

## 同步 Client 示例

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
    last_id = client.query_last_client_req_id(timeout=5)
    print("[示例格式] LastClientReqId:", last_id)
finally:
    client.close()
```

## asyncio Client 示例

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
        positions = await client.query_position()
        print("[示例格式] position count:", len(positions))
    finally:
        await client.close()

asyncio.run(main())
```

## 设计边界

`NativeTradeApi` 是底层桥，不负责业务状态管理。高层状态、请求号、幂等、journal 和同步等待在 `DstarTradeClient` 中实现。

官方接口返回整数码时，高层 client 会调用 `raise_for_error(ret, action)`。直接调用 native 方法时，调用方必须自己处理返回码：

```python
from dstar_trade_py import NativeTradeApi, raise_for_error

api = NativeTradeApi()
ret = api.req_qry_fund()
raise_for_error(ret, "ReqQryFund")
```
