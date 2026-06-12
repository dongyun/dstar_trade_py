# 订单 API 使用说明

`dstar_trade_py` 的订单接口严格基于官方请求结构体：

- `DstarApiReqOrderInsertField`：普通报单
- `DstarApiReqOrderDeleteField`：撤单
- `DstarApiReqCmbOrderInsertField`：组合报单
- `DstarApiReqOfferInsertField`：报价

高层方法不会把官方结构体中不存在的字段塞进请求。例如普通报单结构体没有交易所字段，
所以交易所、品种等信息需要调用方通过合约基础资料确认后，落实到 `ContractIndex` 和
`ContractNo`。

## 构造限价单

可以直接使用 `OrderRequestBuilder` 构造官方 dataclass：

```python
from dstar_trade_py import OrderRequestBuilder
from dstar_trade_py.enums import Direction, Hedge, Offset, ValidType

request = OrderRequestBuilder.limit_order(
    direct=int(Direction.BUY),
    offset=int(Offset.OPEN),
    hedge=int(Hedge.SPECULATE),
    valid_type=int(ValidType.GFD),
    account_index=1,
    contract_index=12345,
    contract_no="rb2410",
    order_qty=1,
    order_price=3000.0,
    client_req_id=1001,
    reference=0,
    udp_auth_code=123456,
)
```

也可以通过 client 直接发送：

```python
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
    client_req_id=1001,
    udp_auth_code=123456,
)
```

`ret == 0` 只表示 `ReqOrderInsert` 本地请求被 API 接收，不代表交易所接收、排队、成交或
最终成功。

## 市价单

使用 `insert_market_order_if_supported(...)` 或
`OrderRequestBuilder.market_order_if_supported(...)`。方法名中的 `if_supported` 是刻意的：
官方结构体有 `OrderType`，但具体合约、交易所、柜台是否支持市价单，需要以后续返回码和
回报为准。

## 组合报单

组合报单使用 `insert_combo_order(...)`，底层对应官方 `DstarApiReqCmbOrderInsertField`：

```python
ret = client.insert_combo_order(
    direct=int(Direction.BUY),
    offset=int(Offset.OPEN),
    hedge=int(Hedge.SPECULATE),
    order_type=int(OrderType.LIMIT),
    valid_type=int(ValidType.GFD),
    account_index=1,
    contract_index1=12345,
    contract_no1="rb2410",
    contract_index2=12346,
    contract_no2="rb2411",
    order_qty=1,
    order_price=10.0,
    client_req_id=1002,
)
```

## 报价

报价使用 `insert_offer(...)`，底层对应 `DstarApiReqOfferInsertField`：

```python
ret = client.insert_offer(
    buy_offset=int(Offset.OPEN),
    sell_offset=int(Offset.CLOSE),
    account_index=1,
    client_req_id=1003,
    contract_index=12345,
    contract_no="rb2410",
    order_qty=1,
    buy_price=2999.0,
    sell_price=3001.0,
)
```

## 撤单

撤单请求使用 `CancelRequestBuilder` 或 `client.cancel_order(...)`：

```python
from dstar_trade_py import CancelRequestBuilder

request = CancelRequestBuilder.order_delete(
    account_index=1,
    client_req_id=1004,
    order_id=987654,
    system_no="",
)

ret = client.cancel_order(
    account_index=1,
    client_req_id=1004,
    order_id=987654,
    system_no="",
)
```

官方主动接口没有单独的 `ReqOfferDelete`。`cancel_offer_if_supported(...)` 复用
`DstarApiReqOrderDeleteField` / `ReqOrderDelete`，是否支持撤销报价由柜台返回码和后续报价
回报决定。

## 回报处理

不要把不同阶段混为一谈：

- `ReqOrderInsert` 返回值：本地同步返回码。只说明请求是否被 API 本地接受。
- `OnRspOrderInsert` / `rsp_order_insert`：报单请求应答，包含 `ErrCode`、`OrderId` 等。
- `OnRtnOrder` / `rtn_order`：委托状态通知，反映排队、撤单、失败等状态变化。
- `OnRtnMatch` / `rtn_match`：成交通知，才是成交层面的事件。

高层 client 会把 `rtn_order` 推入 `client.order_events`，把 `rtn_match` 推入
`client.trade_events`。如果需要完整事件流，可以读取 `client.raw_events`。

## 避免重复下单

建议调用方在业务层维护以下幂等信息：

- `client_req_id`
- 合约编号和合约索引
- 买卖方向、开平、投保
- 价格和数量
- 本地业务流水号

下单前先检查同一个业务流水号是否已经提交过。`ReqOrderInsert` 返回网络错误或超时时，不要
盲目重发；应优先查询最新请求号、监听委托回报，确认上一笔请求是否已被柜台处理。

## 请求号管理

可以使用：

```python
last_id = client.query_last_client_req_id(timeout=5)
next_id = last_id + 1
```

官方文档说明查询最新请求号可用于检测报撤单丢包情况，但有频率限制。不要每次循环高频调用；
通常应在本地维护递增请求号，并在登录后或异常恢复时查询一次进行校准。

## Demo 安全

`examples/06_insert_limit_order.py` 和 `examples/07_cancel_order.py` 默认 dry-run，不发送真实请求。
必须传入 `--confirm-live-order` 并手工输入 `YES`，才会调用真实下单或撤单方法。
