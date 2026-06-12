# Dstar 错误码与异常体系

## 使用方式

所有返回整数状态码的主动接口都应立即调用统一入口：

```python
from dstar_trade_py import raise_for_error

result = native_api.ReqOrderInsert(request)
raise_for_error(result, action="ReqOrderInsert")
```

`code == 0` 时函数直接返回。非零时异常对象保留 `code`、`message` 和 `action`。未知错误不会丢失原始整数，其消息固定为 `Unknown Dstar error`。

异常层次：

- `DstarError`：所有 SDK 异常的基类。
- `DstarNativeError`：本地 SDK、系统信息采集、解析或缓冲区错误。
- `DstarConnectionError`：前置、网关、socket 或收发连接错误。
- `DstarAuthError`：登录、账号、授权码、License 或 UDP 认证错误。
- `DstarRequestError`：请求状态、字段或交易业务规则拒绝。
- `DstarTimeoutError`：心跳超时；它同时继承 `DstarConnectionError`。

## 官方声明错误码

下表完整覆盖 `DstarTradeApiError.h` 正式声明的 78 个常量。头文件后半部分仅以注释列出的交易所返回码不属于稳定的 `const` 声明；收到此类或未来新增的未知码时，SDK 保留 code 并返回 `Unknown Dstar error`。

### 通用与连接错误

| Code | Python name | Message | Exception |
| ---: | --- | --- | --- |
| 0 | `SUCCESS` | Success | None |
| 10001 | `NOCONNECTION` | Not connected | `DstarConnectionError` |
| 10002 | `NOTLOGIN` | Not logged in | `DstarAuthError` |
| 10003 | `NOTREADY` | API is not ready | `DstarRequestError` |
| 10004 | `SUBSERIALID` | Invalid subscription serial ID | `DstarRequestError` |
| 10005 | `SEND` | Failed to send data | `DstarConnectionError` |
| 10006 | `RECV` | Failed to receive data | `DstarConnectionError` |
| 10007 | `DATA_PROCESS` | Failed to parse data | `DstarNativeError` |
| 10008 | `BUFF_OVERFLOW` | Buffer overflow | `DstarNativeError` |
| 10009 | `HB_TIMEOUT` | Heartbeat timeout | `DstarTimeoutError` |

官方符号 `10007-10009` 拼写为 `DSATR_*`；Python 名称修正拼写，但数值保持不变。

### 认证与业务错误

| Code | Python name | Message |
| ---: | --- | --- |
| 20001 | `AUTHSTRING` | Invalid authentication string |
| 20002 | `NOACCOUNTNO` | Account does not exist |
| 20003 | `PASSWORD` | Incorrect password |
| 20004 | `LOGINCOUNT` | Login count limit exceeded |
| 20005 | `GWNOTCONN` | Gateway is not connected |
| 20006 | `CONTRACTINDEX` | Invalid contract index |
| 20007 | `TCPLOGIN` | TCP authentication has not completed |
| 20008 | `ACCOUNTINDEX` | Invalid account index |
| 20009 | `UDPAUTHCODE` | Invalid UDP authentication code |
| 20010 | `NOAUTH` | UDP authentication has not completed |
| 20011 | `ACCINDEX` | Order account differs from authenticated account |
| 20012 | `CONTRACTNO` | Contract index and contract number do not match |
| 20013 | `REQDATA` | Invalid order request fields |
| 20014 | `CLIENTREQID` | Invalid client request ID |
| 20015 | `ADDRESS` | Invalid order or cancellation address |
| 20016 | `AUTHCODE` | Invalid order or cancellation authentication code |
| 20017 | `TRADERIGHT` | Trading permission denied |
| 20018 | `FUND` | Insufficient funds |
| 20019 | `PARENTFUND` | Parent account has insufficient funds |
| 20020 | `ORDERFREQUENCY` | Account order frequency limit exceeded |
| 20021 | `AUTHVERSION` | Invalid authentication key version |
| 20022 | `SUBMITEMPTY` | Submitted system information is empty |
| 20023 | `NOLICENSE` | Software license does not exist |
| 20024 | `NOORDER` | Original order was not found for cancellation |
| 20025 | `SEATINDEX` | Invalid seat index |
| 20026 | `MAXCNT` | Batch quantity exceeds the per-request maximum |
| 20027 | `LICENSENO` | Invalid software license number |
| 20028 | `VERSION` | Protocol version mismatch |
| 20029 | `STATE` | Order state does not allow cancellation |
| 20030 | `ENOUGH` | Order capacity is exhausted |
| 20031 | `POSITION` | Insufficient position to close |
| 20032 | `TRADENO` | Trading code does not exist |
| 20033 | `SEAT` | Seat is unavailable or invalid |
| 20034 | `UNSUPPORTED` | Unsupported order |
| 20035 | `SYSTEMNO` | Invalid system number |
| 20036 | `NOCOMMODITY` | Commodity does not exist |
| 20037 | `WHITELIST` | Commodity is not on the account whitelist |
| 20038 | `NOCONTRACT` | Contract does not exist |
| 20039 | `PRICE` | Invalid price |
| 20040 | `HWLOGIN` | Failed to set hardware login information |
| 20041 | `MESSAGEAMOUNT` | Message volume limit exceeded |
| 20042 | `OFFERQTY` | Bid and ask quantities are inconsistent |
| 20043 | `ORDERIDREPLACE` | Replacement order ID does not exist |
| 20044 | `SYSNOREPLACE` | Replacement system number does not exist |
| 20045 | `SYSTEMTYPE` | Backup trading system is not active |
| 20046 | `UDPADDR` | Invalid UDP packet address |
| 20047 | `SELFMATCH` | Order may self-match |
| 20048 | `CASHINOUTVALUE` | Invalid cash transfer amount |
| 20049 | `CASHOUTMORE` | Withdrawal amount exceeds available funds |
| 20050 | `APPLICATIONNO` | Invalid application number |
| 20051 | `ACCLICENSENO` | Account is not authorized for this software license |
| 20052 | `LICENSENODATE` | Software license has expired |
| 20053 | `LOGINRIGHT` | Login is prohibited |

### 席位、本地与策略错误

| Code | Python name | Message |
| ---: | --- | --- |
| 30001 | `SEATFREQUENCY` | Seat order frequency limit exceeded |
| 30002 | `SENDFAILED` | Send operation failed |
| 30003 | `LOCAL_ENOUGH` | Local order number capacity is exhausted |
| 30004 | `LOCALNO` | Invalid local order number |
| 30005 | `EXEC` | Exercise orders are not supported |
| 30006 | `CANCEL_EXEC` | Cancelling exercise orders is not supported |
| 30007 | `ABANDON` | Abandonment orders are not supported |
| 30008 | `CANCEL_ABANDON` | Cancelling abandonment orders is not supported |
| 30009 | `CMB` | Combination orders are not supported |
| 30010 | `INITING` | Trading system is initializing |
| 30011 | `NOTHREAD` | Data was received on an unexpected thread |
| 30012 | `CANCEL_ENQUIRY` | Cancelling enquiry orders is not supported |
| 60001 | `SLG_ORDERUNUSUAL` | Strategy order submission failed |
| 60002 | `SLG_INVALIDSORDER` | Invalid strategy order |
| 60003 | `SLG_NOQUOTE` | Market quote is unavailable |

## 主动接口负返回值

负返回值不是 `DstarApiErrorCodeType`，且相同数字在不同方法中含义不同。因此 client 层必须传入官方方法名作为 `action`：

| Action | Codes |
| --- | --- |
| `GetSystemInfo` | `-1..-9`：IP、MAC、设备名、操作系统、硬盘、CPU、BIOS、分区或设备序列号采集失败。 |
| `Init` | `-3` 已创建连接；`-4` socket 创建失败；`-5` 连接失败；`-11..-19` 系统信息采集失败。 |
| `ReqLastClientReqId` | `-1` 未就绪；`-2` 频率超限；`-3` 网络断开。 |
| `ReqPwdMod`, `ReqOrderInsert`, `ReqOfferInsert`, `ReqOfferInsertNew`, `ReqOrderDelete`, `ReqCmbOrderInsert` | `-1` 未就绪；`-2` 网络断开。 |
| `ReqQryFund`, `ReqQryPosition` | `-1` 未就绪；`-2` 网络断开；`-3` 查询频率超限；`-4` 上次查询未结束。 |

action 匹配忽略大小写和下划线，因此 `ReqQryPosition` 与 `req_qry_position` 等价。未来 client 层每次调用上述方法后都应统一执行 `raise_for_error(result, action="官方方法名")`。
