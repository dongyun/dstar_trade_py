# IDstarTradeSpi 回调覆盖矩阵

本文档对照 `third_party/dstar/include/DstarTradeApi.h` 中的 `IDstarTradeSpi`，记录
`dstar_trade_py` 对全部回调的代理情况。

结论：39 个回调均已在 `cpp/trade_spi_adapter.*` 中覆盖，且全部进入统一
`dispatch_event(event_name, payload)`。`dispatch_event` 在 SDK 回调线程中获取 Python GIL，
调用 Python `dispatcher.on_event(...)`，并捕获 `py::error_already_set`、`std::exception`
和未知异常，异常不会穿透回易盛 C++ SDK。所有官方结构体指针都会在回调栈内立即转换为
Python-owned `dict`，不会把裸指针交给 Python 保存。

## 使用示例

下面示例只演示回调事件格式，不连接真实交易服务器：

```python
from dstar_trade_py import DstarTradeClient

client = DstarTradeClient(
    front_ip="61.163.243.173",
    front_port=6668,
    account_no="你的账号",
    password="你的密码",
    app_id="你的APPID",
    license_no="你的AuthCode",
)

try:
    client.connect()
    client.login()
    client.wait_ready(timeout=30)

    # 示例格式：实际事件来自官方 SDK 回调，不要伪造为真实交易结果。
    event = client.raw_events.get(timeout=5)
    print("[示例格式] event:", event.name)
    print("[示例格式] payload:", event.payload)
finally:
    client.close()
```

如果只关心委托和成交：

```python
order_event = client.order_events.get(timeout=5)
trade_event = client.trade_events.get(timeout=5)
print("[示例格式] order:", order_event)
print("[示例格式] trade:", trade_event)
```

以上输出是格式示例，真实字段和值必须以后续 SDK 回调为准。

| C++ 回调名 | Python event_name | payload 类型 | 是否转换结构体 | 是否有单元测试 | 是否有 demo 使用 |
|---|---|---|---|---|---|
| `OnFrontDisconnected` | `front_disconnected` | `{}` | 否 | 是：`test_callback_dispatch.py`、`test_callback_coverage.py` | 无专用 demo；所有 client 都会处理断线状态 |
| `OnRspError` | `rsp_error` | `dict(error_code, ErrorCode, error_message)` | 否 | 是：`test_callback_dispatch.py`、`test_callback_coverage.py` | 无专用 demo；所有 client 都会处理连接类错误 |
| `OnRspUserLogin` | `rsp_user_login` | `DstarApiRspLoginField` dict / client dataclass | 是 | 是：`test_callback_dispatch.py`、`test_callback_coverage.py` | 是：`01_login.py` |
| `OnRspPwdMod` | `rsp_pwd_mod` | `DstarApiRspPwdModField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：`08_modify_password_demo.py` 间接观察 |
| `OnRspSubmitInfo` | `rsp_submit_info` | `DstarApiRspSubmitInfoField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRspContract` | `rsp_contract` | `DstarApiContractField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspCmbContract` | `rsp_cmb_contract` | `DstarApiCmbContractField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspSeat` | `rsp_seat` | `DstarApiSeatField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspTrdFeeParam` | `rsp_trd_fee_param` | `DstarApiTrdFeeParamField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspTrdMarParam` | `rsp_trd_mar_param` | `DstarApiTrdMarParamField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspTradeRight` | `rsp_trade_right` | `DstarApiTradeRightField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspAccountCommList` | `rsp_account_comm_list` | `DstarApiAccountCommListField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspTrdExchangeState` | `rsp_trd_exchange_state` | `DstarApiTrdExchangeStateField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspFund` | `rsp_fund` | `DstarApiFundField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；资金查询 demo 使用 `rsp_qry_fund` |
| `OnRspPrePosition` | `rsp_pre_position` | `DstarApiPrePositionField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；无专用打印 demo |
| `OnRspPosition` | `rsp_position` | `DstarApiPositionField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 初始化查询可能收到；持仓查询 demo 使用 `rsp_qry_position` |
| `OnRspOrder` | `rsp_order` | `DstarApiOrderField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：`05_subscribe_order_trade_events.py` |
| `OnRspOffer` | `rsp_offer` | `DstarApiOfferField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 可由订阅 demo 通过 raw events 观察；无专用报价 demo |
| `OnRspMatch` | `rsp_match` | `DstarApiMatchField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：`05_subscribe_order_trade_events.py` |
| `OnRspCashInOut` | `rsp_cash_in_out` | `DstarApiCashInOutField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnApiReady` | `api_ready` | `dict(serial_id)` | 否 | 是：`test_callback_dispatch.py`、`test_callback_coverage.py` | 是：`02_wait_ready.py` 及所有查询/下单 demo |
| `OnRspUdpAuth` | `rsp_udp_auth` | `DstarApiRspUdpAuthField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 登录流程可能收到；无专用 demo |
| `OnRspOrderInsert` | `rsp_order_insert` | `DstarApiRspOrderInsertField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：`06_insert_limit_order.py` 间接观察 |
| `OnRspOfferInsert` | `rsp_offer_insert` | `DstarApiRspOfferInsertField` alias dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用报价 demo |
| `OnRspOrderDelete` | `rsp_order_delete` | `DstarApiRspOrderDeleteField` alias dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：`07_cancel_order.py` 间接观察 |
| `OnRspLastReqId` | `rsp_last_req_id` | `DstaApiRspLastReqIdField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：下单/撤单 demo 默认用于生成下一请求号 |
| `OnRtnPwdMod` | `rtn_pwd_mod` | `DstarApiPwdModField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：`08_modify_password_demo.py` 间接观察 |
| `OnRtnOrder` | `rtn_order` | `DstarApiOrderField` dict / client dataclass | 是 | 是：`test_callback_dispatch.py`、`test_callback_coverage.py` | 是：`05_subscribe_order_trade_events.py` |
| `OnRtnMatch` | `rtn_match` | `DstarApiMatchField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 是：`05_subscribe_order_trade_events.py` |
| `OnRtnCashInOut` | `rtn_cash_in_out` | `DstarApiCashInOutField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRtnOffer` | `rtn_offer` | `DstarApiOfferField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 可由订阅 demo 通过 raw events 观察；无专用报价 demo |
| `OnRtnEnquiry` | `rtn_enquiry` | `DstarApiEnquiryField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRtnTrdExchangeState` | `rtn_trd_exchange_state` | `DstarApiTrdExchangeStateField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRtnPosiProfit` | `rtn_posi_profit` | `DstarApiPosiProfitField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRtnSeat` | `rtn_seat` | `DstarApiSeatField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRtnTradeRight` | `rtn_trade_right` | `DstarApiTradeRightField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRtnTradeRightDel` | `rtn_trade_right_del` | `DstarApiTradeRightDelField` dict / client dataclass | 是 | 是：`test_callback_coverage.py` | 无专用 demo |
| `OnRspQryPosition` | `rsp_qry_position` | `dict(data: DstarApiPositionField dict, last: bool)` / client nested dataclass | 是 | 是：`test_callback_dispatch.py`、`test_callback_coverage.py` | 是：`04_query_position.py` |
| `OnRspQryFund` | `rsp_qry_fund` | `DstarApiFundField` dict / client dataclass | 是 | 是：`test_callback_dispatch.py`、`test_callback_coverage.py` | 是：`03_query_fund.py`、`async_query_fund.py` |

## 自动覆盖检查

`tests/unit/test_callback_coverage.py` 会自动解析官方头文件并验证：

- `IDstarTradeSpi` 中 39 个回调都有 C++ adapter 声明和定义。
- 每个回调体都调用统一 `dispatch_event(...)`。
- 每个回调的 `event_name` 符合 snake_case 约定。
- 回调体不直接调用 Python dispatcher。
- `dispatch_event` 获取 GIL，并捕获 Python/C++/未知异常。
- 高层 Python client 认识每个 C++ adapter 可能发出的 `event_name`。
