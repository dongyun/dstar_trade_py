# IDstarTradeApi 主动接口覆盖矩阵

本文档对照 `third_party/dstar/include/DstarTradeApi.h`，记录
`dstar_trade_py` 对 `IDstarTradeApi` 主动接口以及 `CreateDstarTradeApi` /
`FreeDstarTradeApi` 工厂函数的代理情况。

结论：native pybind11 层已经覆盖全部 24 项；同步 `DstarTradeClient` 和
`AsyncDstarTradeClient` 也为所有适合高层调用的能力提供了代理。`CreateDstarTradeApi` 和
`FreeDstarTradeApi` 不直接暴露裸指针给 Python，高层通过构造、`close()` 和 RAII 间接覆盖。

| C++ 接口名 | native binding 是否覆盖 | Python client 是否覆盖 | 测试是否覆盖 | demo 是否覆盖 | 备注 |
|---|---|---|---|---|---|
| `RegisterSpi` | 是：`NativeTradeApi.register_callback()` | 是：`connect()` 自动注册 client dispatcher | 是：`test_native_api_methods.py`、`test_callback_dispatch.py`、`test_api_coverage.py` | 是：所有 live demo 通过 `connect_login_ready()` 或 `connect()` 间接使用 | 高层不暴露 SPI 指针，只注册 Python `on_event` dispatcher。 |
| `RegisterFrontAddress` | 是：`NativeTradeApi.register_front_address()` | 是：`connect(front_ip, front_port)` | 是：`test_native_api_methods.py`、`test_client_state.py`、`test_api_coverage.py` | 是：所有 live 连接类 demo | 前置地址来自环境变量或构造参数。 |
| `SetApiLogPath` | 是：`NativeTradeApi.set_api_log_path()` | 是：构造参数 `api_log_path` + `connect()` | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 是：live demo 使用 `DSTAR_TRADE_LOG_PATH` | 仅在提供路径时调用。 |
| `SetLoginInfo` | 是：`NativeTradeApi.set_login_info()` | 是：`login()` | 是：`test_native_api_methods.py`、`test_client_state.py`、`test_api_coverage.py` | 是：`01_login.py` 等登录 demo | 官方无独立登录请求，登录信息在 `Init()` 前设置。 |
| `SetCpuId` | 是：`NativeTradeApi.set_cpu_id()` | 是：构造参数 + `connect()` | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 间接覆盖：live demo 使用默认 `-1/-1` | 高层默认不绑定 CPU。 |
| `SetSubscribeStartId` | 是：`NativeTradeApi.set_subscribe_start_id()` | 是：构造参数 + `connect()` | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 间接覆盖：live demo 使用默认 `-1` | 默认从最新通知流开始。 |
| `SetRealTimeDataFilter` | 是：`NativeTradeApi.set_real_time_data_filter()` | 是：构造参数 + `connect()` | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 间接覆盖：live demo 使用默认不过滤 | 高层使用 enum int。 |
| `SetRunMode` | 是：`NativeTradeApi.set_run_mode()` | 是：构造参数 + `connect()` | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 间接覆盖：live demo 使用默认满载模式 | 高层使用 enum int。 |
| `GetSystemInfo` | 是：`NativeTradeApi.get_system_info()` | 是：`get_system_info()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 暂无专用 demo | 该接口可能需要 Linux 系统权限；高层统一处理返回码。 |
| `SetSubmitInfo` | 是：`NativeTradeApi.set_submit_info()` | 是：构造参数 `submit_info` + `connect()` | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 暂无专用 demo | 上报信息通常由调用方按看穿式要求提供；不强制 demo 默认填写。 |
| `SetInitQryInfo` | 是：`NativeTradeApi.set_init_qry_info()` | 是：构造参数 `init_qry_info` + `connect()` | 是：`test_native_api_methods.py`、`test_client_state.py`、`test_api_coverage.py` | 是：所有 live 连接类 demo 间接使用默认初始化查询配置 | 默认使用空 `DstarApiInitQryInfoField()`。 |
| `Init` | 是：`NativeTradeApi.init()` | 是：`login()` 调用 | 是：`test_api_coverage.py`、client fake state tests；live tests opt-in 覆盖真实调用 | 是：`01_login.py`、`02_wait_ready.py` 等 | 不在普通 unit/integration 中连接真实服务器。 |
| `ReqLastClientReqId` | 是：`NativeTradeApi.req_last_client_req_id()` | 是：`query_last_client_req_id()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_client_events.py`、`test_api_coverage.py` | 是：下单/撤单 demo 默认用它生成下一请求号 | 查询间隔限制由官方 API 返回码处理。 |
| `ReqPwdMod` | 是：`NativeTradeApi.req_pwd_mod()` | 是：`modify_password()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 是：`08_modify_password_demo.py`，默认 dry-run 且需二次确认 | 改密是高风险操作，demo 默认不发送。 |
| `ReqOrderInsert` | 是：`NativeTradeApi.req_order_insert()` | 是：`insert_order()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_client_state.py`、`test_api_coverage.py` | 是：`06_insert_limit_order.py`，默认 dry-run 且需二次确认 | 返回本地请求码，不伪造成交结果。 |
| `ReqOfferInsert` | 是：`NativeTradeApi.req_offer_insert()` | 是：`insert_offer()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 暂无专用 demo | 报价请求参数较依赖业务场景，当前先提供 SDK 代理能力。 |
| `ReqOfferInsertNew` | 是：`NativeTradeApi.req_offer_insert_new()` | 是：`insert_offer_new()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 暂无专用 demo | 新报价接口已完整代理，demo 暂未提供以降低误操作面。 |
| `ReqOrderDelete` | 是：`NativeTradeApi.req_order_delete()` | 是：`cancel_order()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 是：`07_cancel_order.py`，默认 dry-run 且需二次确认 | 撤单失败后结果通过委托/报价通知观察。 |
| `ReqCmbOrderInsert` | 是：`NativeTradeApi.req_cmb_order_insert()` | 是：`insert_cmb_order()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_api_coverage.py` | 暂无专用 demo | 组合报单已代理；真实 demo 暂不默认提供，以避免用户误提交复杂订单。 |
| `ReqQryFund` | 是：`NativeTradeApi.req_qry_fund()` | 是：`query_fund()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_client_events.py`、`test_async_client.py`、live opt-in tests | 是：`03_query_fund.py`、`async_query_fund.py` | 请求-响应等待已在 client 层实现。 |
| `ReqQryPosition` | 是：`NativeTradeApi.req_qry_position()` | 是：`query_position()` / async 同名方法 | 是：`test_native_api_methods.py`、`test_client_events.py`、`test_async_client.py`、live opt-in tests | 是：`04_query_position.py` | 按 `last=True` 聚合持仓批次。 |
| `GetApiVersion` | 是：模块函数 `get_api_version()` 与 `NativeTradeApi.get_api_version()` | 是：`get_api_version()` / async 同名方法 | 是：`tests/integration/test_native_load.py`、`test_native_api_methods.py`、`test_api_coverage.py` | 是：`examples/check_install.py` | 不连接服务器。 |
| `CreateDstarTradeApi` | 是：`NativeTradeApi` 构造、模块函数 `create_and_free_api()` / `get_api_version()` | 是：client 构造时通过 `api_factory` 创建 native API | 是：`tests/integration/test_native_load.py`、`test_api_coverage.py` | 是：所有使用 client/native 的 demo 间接覆盖 | 高层不暴露裸 `IDstarTradeApi*`，避免 Python 管理 C++ 指针生命周期。 |
| `FreeDstarTradeApi` | 是：`NativeTradeApi` 析构、模块函数 `create_and_free_api()` | 是：`close()` 释放 native 引用并触发 RAII 析构 | 是：`tests/integration/test_native_load.py`、`test_api_coverage.py` | 是：所有 demo 的 `finally: close()` 间接覆盖 | 官方要求不要在 SPI 回调中调用释放函数；当前释放只发生在生命周期结束。 |

## 当前没有单独 high-level 方法的情况

没有。所有 22 个 `IDstarTradeApi` 主动接口都有 native binding，且同步/异步 client 均提供了
对应的直接方法或明确生命周期方法。`CreateDstarTradeApi` / `FreeDstarTradeApi` 属于 C 工厂
函数，不适合把裸指针直接暴露给 Python，因此由 `NativeTradeApi` RAII、模块生命周期检查函数
和高层 client 构造/`close()` 间接代理。
