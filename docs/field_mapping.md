# Dstar 数据类型与字段映射

本文基于 `DstarTradeApiDataType.h` 和 `DstarTradeApiStruct.h`。头文件没有使用 C++ `enum` 关键字，而是以 typedef 加常量表达枚举语义。Python 数据结构保持 C++ 类名和字段名；固定 `char[N]` 使用 `str`，所有单字符/整数枚举字段先使用 `int`，可通过 `dstar_trade_py.enums` 中的 `IntEnum` 解读。

C++ 结构体使用 `#pragma pack(push, 1)`；Python dataclass 是业务值对象，不复制 packed ABI。匿名 union 的成员在 Python 中各自保留为独立字段，转换到 C++ 时 binding 层必须按业务语义选择有效成员。

## Typedef 映射

共 73 个 typedef。

| C++ typedef | C++ 底层类型 | Python 类型 | 字段名/含义 | char 数组 | 数值类别 | 枚举语义 |
| --- | --- | --- | --- | --- | --- | --- |
| `STR10` | `char[11]` | `str` | 字符串类型；长度为10的字符串 | 是 | char array | 否 |
| `STR20` | `char[21]` | `str` | 长度为20的字符串 | 是 | char array | 否 |
| `STR30` | `char[31]` | `str` | 长度为30的字符串 | 是 | char array | 否 |
| `STR40` | `char[41]` | `str` | 长度为40的字符串 | 是 | char array | 否 |
| `STR50` | `char[51]` | `str` | 长度为50的字符串 | 是 | char array | 否 |
| `STR100` | `char[101]` | `str` | 长度为100的字符串 | 是 | char array | 否 |
| `STR200` | `char[201]` | `str` | 长度为200的字符串 | 是 | char array | 否 |
| `RESULT` | `int` | `int` | - | 否 | int | 否 |
| `DstarApiVersionType` | `unsigned char` | `int` | 协议版本号类型 | 否 | int | 是 |
| `DstarApiProtocolCodeType` | `unsigned short` | `int` | 协议类型 | 否 | int | 是 |
| `DstarApiDataLen` | `unsigned short` | `int` | 数据长度 | 否 | int | 否 |
| `DstarApiClientReqId` | `unsigned int` | `int` | 客户请求号 | 否 | int | 否 |
| `DstarApiReferenceType` | `long long` | `int` | 报单引用, -1:无报单引用 | 否 | int | 否 |
| `DstarApiFdType` | `int` | `int` | 描述符 | 否 | int | 否 |
| `DstarApiIpType` | `char[41]` | `str` | ip | 是 | char array | 否 |
| `DstarApiIPv4IpType` | `char[16]` | `str` | ipv4 | 是 | char array | 否 |
| `DstarApiPortType` | `unsigned short` | `int` | 端口 | 否 | int | 否 |
| `DstarApiPathType` | `char[256]` | `str` | 日志路径 | 是 | char array | 否 |
| `DstarApiCpuIdType` | `int` | `int` | Cpu Id | 否 | int | 否 |
| `DstarApiSerialIdType` | `unsigned long long` | `int` | 流号 | 否 | int | 否 |
| `DstarApiAccountNoType` | `char[21]` | `str` | 账号 | 是 | char array | 否 |
| `DstarApiContractIndexType` | `unsigned int` | `int` | 合约索引 | 否 | int | 否 |
| `DstarApiAccountIndexType` | `unsigned short` | `int` | 账号索引 | 否 | int | 否 |
| `DstarApiSeatIndexType` | `unsigned char` | `int` | 席位索引 | 否 | int | 否 |
| `DstarApiSeatNoType` | `char[21]` | `str` | 席位号 | 是 | char array | 否 |
| `DstarApiPasswdType` | `char[65]` | `str` | 密码 | 是 | char array | 否 |
| `DstarApiNoticeSubIdType` | `long long` | `int` | 通知流订阅类型 | 否 | int | 是 |
| `DstarApiRealTimeDataFilterType` | `int` | `int` | 实时数据过滤器 | 否 | int | 是 |
| `DstarApiRunModeType` | `int` | `int` | 运行模式 | 否 | int | 是 |
| `DstarApiInitType` | `char` | `int` | 初始化类型 | 否 | int | 是 |
| `DstarApiAuthCodeType` | `unsigned int` | `int` | UDP认证码 | 否 | int | 否 |
| `DstarApiReqIdModeType` | `unsigned char` | `int` | 请求类型 | 否 | int | 是 |
| `DstarApiTradeNoType` | `char[9]` | `str` | 交易编码 | 是 | char array | 否 |
| `DstarApiExchangeType` | `char` | `int` | 交易所 | 否 | int | 是 |
| `DstarApiCommodityNoType` | `char[11]` | `str` | 品种 | 是 | char array | 否 |
| `DstarApiCommodityType` | `char` | `int` | 品种类型 | 否 | int | 是 |
| `DstarApiContractNoType` | `char[16]` | `str` | 合约 | 是 | char array | 否 |
| `DstarApiContractSizeType` | `int` | `int` | 合约乘数类型 | 否 | int | 否 |
| `DstarApiContractTickSizeType` | `double` | `float` | 合约最小变动价位 | 否 | double | 否 |
| `DstarApiDirectType` | `char` | `int` | 买卖 | 否 | int | 是 |
| `DstarApiOffsetType` | `char` | `int` | 开平 | 否 | int | 是 |
| `DstarApiHedgeType` | `char` | `int` | 投机套保 | 否 | int | 是 |
| `DstarApiOrderTypeType` | `char` | `int` | 委托类型 | 否 | int | 是 |
| `DstarApiTradeRightType` | `char` | `int` | 交易权限 | 否 | int | 是 |
| `DstarApiSystemNoType` | `char[21]` | `str` | 系统号 | 是 | char array | 否 |
| `DstarApiExchMatchNo` | `char[71]` | `str` | 交易所成交号 | 是 | char array | 否 |
| `DstarApiDateType` | `char[9]` | `str` | 日期类型 yyyymmdd | 是 | char array | 否 |
| `DstarApiOrderIdType` | `unsigned long long` | `int` | 委托号 | 否 | int | 否 |
| `DstarApiReplaceIdType` | `unsigned long long` | `int` | 顶单号（中金所报价） | 否 | int | 是 |
| `DstarApiMatchIdType` | `unsigned long long` | `int` | 成交ID | 否 | int | 否 |
| `DstarApiOrderLocalNoType` | `char[21]` | `str` | 本地号 | 是 | char array | 否 |
| `DstarApiPriceType` | `double` | `float` | 价格类型 | 否 | double | 否 |
| `DstarApiFundType` | `double` | `float` | 资金类型 | 否 | double | 否 |
| `DstarApiParamType` | `double` | `float` | 费率类型 | 否 | double | 否 |
| `DstarApiU16QuantityType` | `unsigned short` | `int` | 数量类型 U16 | 否 | int | 否 |
| `DstarApiQuantityType` | `unsigned int` | `int` | 数量类型 | 否 | int | 否 |
| `DstarApiMatchTimeType` | `char[20]` | `str` | 成交时间 yyyymmddhhmmss | 是 | char array | 否 |
| `DstarApiDateTimeType` | `char[20]` | `str` | 日期时间 yyyy-mm-dd hh:mm:ss | 是 | char array | 否 |
| `DstarApiValidTypeType` | `char` | `int` | 有效类型 | 否 | int | 是 |
| `DstarApiValidDateType` | `unsigned int` | `int` | 有效日期类型(yyyymmdd) | 否 | int | 否 |
| `DstarApiOrderStateType` | `char` | `int` | 委托状态 | 否 | int | 是 |
| `DstarApiCashInOutType` | `char` | `int` | 出入金类型 | 否 | int | 是 |
| `DstarApiCashInOutModeType` | `char` | `int` | 出入金方式 | 否 | int | 是 |
| `DstarApiTradingStateType` | `char` | `int` | 交易状态 | 否 | int | 是 |
| `DstarApiAuthTypeType` | `char` | `int` | 软件授权类型 | 否 | int | 是 |
| `DstarApiAuthKeyVersion` | `unsigned int` | `int` | 采集信息密钥版本号 | 否 | int | 否 |
| `DstarApiSystemInfoType` | `char[501]` | `str` | 系统采集信息 | 是 | char array | 否 |
| `DstarApiAppIdType` | `char[31]` | `str` | AppId类型 | 是 | char array | 否 |
| `DstarApiLicenseNoType` | `char[51]` | `str` | 软件授权号类型 | 是 | char array | 否 |
| `DstarApiStartTimeType` | `unsigned int` | `int` | 启动时间 hhmmss | 否 | int | 否 |
| `DstarApiStartModeType` | `unsigned char` | `int` | 启动模式 | 否 | int | 是 |
| `DstarApiSeatStateType` | `char` | `int` | 席位状态 | 否 | int | 是 |
| `DstarApiYesNoType` | `unsigned char` | `int` | 是否 | 否 | int | 是 |

## 常量与可读枚举

共 96 个常量：数据类型头文件 90 个，结构体头文件 UDP 协议常量 6 个。字符常量在 Python `IntEnum` 中使用 `ord(char)`。

| C++ 类型 | 官方常量 | 原始值 | Python 枚举 | 含义 |
| --- | --- | ---: | --- | --- |
| `DstarApiVersionType` | `DSTAR_API_PROTOCOL_VERSION` | `3` | `ProtocolVersion.CURRENT` | - |
| `DstarApiNoticeSubIdType` | `DSTAR_API_SUB_HEAD` | `0` | `NoticeSubscription.HEAD` | 从头订阅 |
| `DstarApiNoticeSubIdType` | `DSTAR_API_SUB_LAST` | `-1` | `NoticeSubscription.LAST` | 从最新订阅 |
| `DstarApiRealTimeDataFilterType` | `DSTAR_API_REAL_TIME_DATA_FILTER_NONE` | `0` | `RealTimeDataFilter.NONE` | 不过滤任何数据 |
| `DstarApiRealTimeDataFilterType` | `DSTAR_API_REAL_TIME_DATA_FILTER_IGNORE_ALL` | `-1` | `RealTimeDataFilter.IGNORE_ALL` | 过滤所有数据 |
| `DstarApiRunModeType` | `DSTAR_API_RUN_MODE_TYPE_FULL_LOAD` | `0` | `RunMode.FULL_LOAD` | 运行模式满载 |
| `DstarApiRunModeType` | `DSTAR_API_RUN_MODE_TYPE_NON_FULL_LOAD` | `-1` | `RunMode.NON_FULL_LOAD` | 运行模式非满载 |
| `DstarApiInitType` | `DSTAR_API_INIT_QUERY` | `0` | `InitMode.QUERY` | 初始化过程中查询基础数据 |
| `DstarApiInitType` | `DSTAR_API_INIT_NOQUERY` | `-1` | `InitMode.NO_QUERY` | 初始化过程中不查询基础数据 |
| `DstarApiReqIdModeType` | `DSTAR_API_REQIDMODE_NOCHECK` | `0` | `RequestIdMode.NO_CHECK` | 不检测 对请求号不做检测 |
| `DstarApiReqIdModeType` | `DSTAR_API_REQIDMODE_INCREASE` | `1` | `RequestIdMode.INCREASE` | 增大 请求号要比上一笔请求大,否则报撤单无效 |
| `DstarApiReqIdModeType` | `DSTAR_API_REQIDMODE_FORCE` | `2` | `RequestIdMode.FORCE` | 强制自增 要求请求号连续自增,否则报撤单无效 |
| `DstarApiExchangeType` | `DSTAR_API_EXCHANGE_ZCE` | `'Z'` | `Exchange.ZCE` | 郑商所 |
| `DstarApiExchangeType` | `DSTAR_API_EXCHANGE_SHFE` | `'S'` | `Exchange.SHFE` | 上期所 |
| `DstarApiExchangeType` | `DSTAR_API_EXCHANGE_INE` | `'I'` | `Exchange.INE` | 能源所 |
| `DstarApiExchangeType` | `DSTAR_API_EXCHANGE_CFFEX` | `'C'` | `Exchange.CFFEX` | 中金所 |
| `DstarApiExchangeType` | `DSTAR_API_EXCHANGE_DCE` | `'D'` | `Exchange.DCE` | 大商所 |
| `DstarApiExchangeType` | `DSTAR_API_EXCHANGE_GFEX` | `'F'` | `Exchange.GFEX` | 广期所 |
| `DstarApiExchangeType` | `DSTAR_API_EXCHANGE_SGE` | `'G'` | `Exchange.SGE` | 金交所 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_FUTURES` | `'F'` | `CommodityType.FUTURES` | 期货 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_OPTION` | `'O'` | `CommodityType.OPTION` | 期权 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_SPD` | `'S'` | `CommodityType.SPD` | 跨期套利 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_IPS` | `'M'` | `CommodityType.IPS` | 跨品种套利 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_STD` | `'D'` | `CommodityType.STD` | 跨式套利 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_STG` | `'G'` | `CommodityType.STG` | 宽跨式套利 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_PRT` | `'R'` | `CommodityType.PRT` | 备兑 |
| `DstarApiCommodityType` | `DSTAR_API_COMMTYPE_NONE` | `'N'` | `CommodityType.NONE` | 无 |
| `DstarApiDirectType` | `DSTAR_API_DIRECT_BUY` | `'B'` | `Direction.BUY` | 买方向 |
| `DstarApiDirectType` | `DSTAR_API_DIRECT_SELL` | `'S'` | `Direction.SELL` | 卖方向 |
| `DstarApiDirectType` | `DSTAR_API_DIRECT_ALL` | `'N'` | `Direction.ALL` | 所有 |
| `DstarApiOffsetType` | `DSTAR_API_OFFSET_OPEN` | `'O'` | `Offset.OPEN` | 开仓 |
| `DstarApiOffsetType` | `DSTAR_API_OFFSET_CLOSE` | `'C'` | `Offset.CLOSE` | 平仓 |
| `DstarApiOffsetType` | `DSTAR_API_OFFSET_CLOSETODAY` | `'T'` | `Offset.CLOSE_TODAY` | 平今 |
| `DstarApiHedgeType` | `DSTAR_API_HEDGE_SPECULATE` | `'T'` | `Hedge.SPECULATE` | 投机 |
| `DstarApiHedgeType` | `DSTAR_API_HEDGE_HEDGE` | `'B'` | `Hedge.HEDGE` | 套保 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_NONE` | `'0'` | `OrderType.NONE` | 空 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_MARKET` | `'1'` | `OrderType.MARKET` | 市价单 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_LIMIT` | `'2'` | `OrderType.LIMIT` | 限价单 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_EXECUTE` | `'3'` | `OrderType.EXECUTE` | 行权 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_ABANDON` | `'4'` | `OrderType.ABANDON` | 弃权 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_ENQUIRY` | `'5'` | `OrderType.ENQUIRY` | 询价 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_OFFER` | `'6'` | `OrderType.OFFER` | 报价 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_SWAP` | `'7'` | `OrderType.SWAP` | 互换 |
| `DstarApiOrderTypeType` | `DSTAR_API_ORDERTYPE_EFP` | `'8'` | `OrderType.EFP` | 期转现 |
| `DstarApiTradeRightType` | `DSTAR_API_TRADERIGHT_NORMAL` | `'0'` | `TradeRight.NORMAL` | 正常交易 |
| `DstarApiTradeRightType` | `DSTAR_API_TRADERIGHT_NOTRADE` | `'1'` | `TradeRight.NO_TRADE` | 禁止交易 |
| `DstarApiTradeRightType` | `DSTAR_API_TRADERIGHT_CLOSE` | `'2'` | `TradeRight.CLOSE_ONLY` | 只可平仓 |
| `DstarApiReplaceIdType` | `DSTAR_API_REPLACE_NORMAL` | `0` | `ReplaceMode.NORMAL` | 正常报价 |
| `DstarApiReplaceIdType` | `DSTAR_API_REPLACE_LAST` | `1` | `ReplaceMode.LAST` | 顶最近一笔报价 |
| `DstarApiValidTypeType` | `DSTAR_API_VALID_FOK` | `'1'` | `ValidType.FOK` | 即时全部 |
| `DstarApiValidTypeType` | `DSTAR_API_VALID_IOC` | `'2'` | `ValidType.IOC` | 即时部分 |
| `DstarApiValidTypeType` | `DSTAR_API_VALID_GFD` | `'3'` | `ValidType.GFD` | 当日有效 |
| `DstarApiValidTypeType` | `DSTAR_API_VALID_GIS` | `'4'` | `ValidType.GIS` | 小节有效 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_ACCEPT` | `'1'` | `OrderState.ACCEPT` | 已受理 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_QUEUE` | `'2'` | `OrderState.QUEUE` | 已排队 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_APPLY` | `'3'` | `OrderState.APPLY` | 已申请(行权、弃权、套利等申请成功) |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_SUSPENDED` | `'4'` | `OrderState.SUSPENDED` | 已挂起 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_TRIGGERED` | `'5'` | `OrderState.TRIGGERED` | 已触发 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_PARTFILL` | `'6'` | `OrderState.PARTIAL_FILL` | 部分成交 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_FILL` | `'7'` | `OrderState.FILLED` | 完全成交 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_FAIL` | `'8'` | `OrderState.FAILED` | 指令失败 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_DELETE` | `'B'` | `OrderState.DELETED` | 已撤单 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_LEFTDELETE` | `'C'` | `OrderState.REMAINDER_DELETED` | 已撤余单 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_SYSDELETE` | `'D'` | `OrderState.SYSTEM_DELETED` | 已删除 |
| `DstarApiOrderStateType` | `DSTAR_API_STATUS_TRIGGERING` | `'E'` | `OrderState.WAITING_TRIGGER` | 策略待触发 |
| `DstarApiCashInOutType` | `DSTAR_API_CASH_IN` | `'I'` | `CashInOutType.IN` | 入金 |
| `DstarApiCashInOutType` | `DSTAR_API_CASH_OUT` | `'O'` | `CashInOutType.OUT` | 出金 |
| `DstarApiCashInOutModeType` | `DSTAR_API_CASHMODE_TRANSFER` | `'1'` | `CashInOutMode.TRANSFER` | 转账 |
| `DstarApiCashInOutModeType` | `DSTAR_API_CASHMODE_CHEQUE` | `'2'` | `CashInOutMode.CHEQUE` | 支票 |
| `DstarApiCashInOutModeType` | `DSTAR_API_CASHMODE_CASH` | `'3'` | `CashInOutMode.CASH` | 现金 |
| `DstarApiCashInOutModeType` | `DSTAR_API_CASHMODE_SWAP` | `'4'` | `CashInOutMode.SWAP` | 换汇 |
| `DstarApiCashInOutModeType` | `DSTAR_API_CASHMODE_BFTRNSFER` | `'5'` | `CashInOutMode.BANK_FUTURES_TRANSFER` | 银期转账 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_UNKNOWN` | `'0'` | `TradingState.UNKNOWN` | 未知状态 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_BID` | `'1'` | `TradingState.BID` | 集合竞价 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_MATCH` | `'2'` | `TradingState.MATCH` | 集合竞价撮合 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_CONTINUOUS` | `'3'` | `TradingState.CONTINUOUS` | 连续交易 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_PAUSED` | `'4'` | `TradingState.PAUSED` | 交易暂停 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_CLOSE` | `'5'` | `TradingState.CLOSED` | 闭市 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_DEALLAST` | `'6'` | `TradingState.POST_CLOSE` | 闭市处理时间 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_INITIALIZE` | `'7'` | `TradingState.INITIALIZING` | 正初始化 |
| `DstarApiTradingStateType` | `DSTAR_API_TRADE_STATE_READY` | `'8'` | `TradingState.READY` | 准备就绪 |
| `DstarApiAuthTypeType` | `DSTAR_API_AUTHTYPE_NOGATHER` | `'0'` | `AuthType.NO_GATHER` | 不采集模式软件授权 |
| `DstarApiAuthTypeType` | `DSTAR_API_AUTHTYPE_DIRECT` | `'1'` | `AuthType.DIRECT` | 直连模式软件授权 |
| `DstarApiAuthTypeType` | `DSTAR_API_AUTHTYPE_RELAY` | `'2'` | `AuthType.RELAY` | 中继模式软件授权 |
| `DstarApiStartModeType` | `DSTAR_API_STARTMODE_CHECK` | `0` | `StartMode.CHECK` | 对账 |
| `DstarApiStartModeType` | `DSTAR_API_STARTMODE_TRADE` | `1` | `StartMode.TRADE` | 交易 |
| `DstarApiSeatStateType` | `DSTAR_API_SEATSTATE_DISCONNECT` | `'D'` | `SeatState.DISCONNECTED` | 断开 |
| `DstarApiSeatStateType` | `DSTAR_API_SEATSTATE_NORMAL` | `'N'` | `SeatState.NORMAL` | 正常 |
| `DstarApiYesNoType` | `DSTAR_API_YES` | `1` | `YesNo.YES` | 是 |
| `DstarApiYesNoType` | `DSTAR_API_NO` | `0` | `YesNo.NO` | 否 |
| `DstarApiProtocolCodeType` | `CMD_API_Req_UdpAuth` | `0xEC00` | `ProtocolCommand.REQ_UDP_AUTH` | Udp认证请求 |
| `DstarApiProtocolCodeType` | `CMD_API_Req_OrderInsert` | `0xEC01` | `ProtocolCommand.REQ_ORDER_INSERT` | 报单请求 |
| `DstarApiProtocolCodeType` | `CMD_API_Req_OfferInsert` | `0xEC02` | `ProtocolCommand.REQ_OFFER_INSERT` | 报价请求 |
| `DstarApiProtocolCodeType` | `CMD_API_Req_OfferInsertNew` | `0xEC09` | `ProtocolCommand.REQ_OFFER_INSERT_NEW` | 新报价请求 |
| `DstarApiProtocolCodeType` | `CMD_API_Req_OrderDelete` | `0xEC03` | `ProtocolCommand.REQ_ORDER_DELETE` | 撤单请求 |
| `DstarApiProtocolCodeType` | `CMD_API_Req_CmbOrderInsert` | `0xEC04` | `ProtocolCommand.REQ_CMB_ORDER_INSERT` | 组合报单请求 |

## 结构体字段

共 36 个具名结构体、298 个字段，另有 2 个 typedef 布局别名。每一行均给出后续 C++/Python 转换所需的字段元数据。

### `DstarApiReqLoginField`

登录请求。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiPasswdType` | `str` | `Password` | 密码 | 是 | char array | 否 |
| `DstarApiAppIdType` | `str` | `AppId` | app id(中继模式填中继app id) | 是 | char array | 否 |
| `DstarApiLicenseNoType` | `str` | `LicenseNo` | 软件授权号 | 是 | char array | 否 |

### `DstarApiRspLoginField`

登录应答。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 账号索引 | 否 | int | 否 |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiDateType` | `str` | `TradeDate` | 当前交易日 | 是 | char array | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | UDP认证码 | 否 | int | 否 |
| `DstarApiErrorCodeType` | `int` | `ErrorCode` | 错误码 | 否 | int | 是 |
| `DstarApiStartTimeType` | `int` | `StartTime` | 交易系统启动时间 | 否 | int | 否 |
| `DstarApiStartModeType` | `int` | `StartMode` | 交易系统启动模式 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `FloatFlag` | 持仓盈利是否计入可用 | 否 | int | 是 |

### `DstarApiSubmitInfoField`

上报信息。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiAuthTypeType` | `int` | `AuthType` | 授权类型 | 否 | int | 是 |
| `DstarApiAuthKeyVersion` | `int` | `AuthKeyVersion` | 密钥版本号 | 否 | int | 否 |
| `DstarApiSystemInfoType` | `str` | `SystemInfo` | 系统采集信息 | 是 | char array | 否 |
| `DstarApiIpType` | `str` | `ClientLoginIp` | 客户登录ip,直连模式不需要填写,中继模式需要填写 | 是 | char array | 否 |
| `DstarApiPortType` | `int` | `ClientLoginPort` | 客户登录port,直连模式不需要填写,中继模式需要填写 | 否 | int | 否 |
| `DstarApiDateTimeType` | `str` | `ClientLoginDateTime` | 登录时间,直连模式不需要填写,中继模式需要填写 | 是 | char array | 否 |
| `DstarApiAppIdType` | `str` | `ClientAppId` | app id | 是 | char array | 否 |
| `DstarApiLicenseNoType` | `str` | `LicenseNo` | 软件授权号 | 是 | char array | 否 |

### `DstarApiRspSubmitInfoField`

上报信息应答。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiErrorCodeType` | `int` | `ErrorCode` | 错误码 | 否 | int | 是 |

### `DstarApiInitQryInfoField`

初始化数据查询。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiYesNoType` | `int` | `ContractInitQryFlag` | 合约初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `CmbContractInitQryFlag` | 组合合约初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `SeatInitQryFlag` | 席位信息初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `TrdFeeInitQryFlag` | 手续费参数初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `TrdMarInitQryFlag` | 保证金参数初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `TrdRightInitQryFlag` | 交易权限初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `AccountCommListInitQryFlag` | 客户白名单初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `TrdExchangeStateInitQryFlag` | 市场状态初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `PrePositionInitQryFlag` | 昨持仓快照初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `OrderInitQryFlag` | 委托信息初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `OfferInitQryFlag` | 报价信息初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `MatchInitQryFlag` | 成交信息初始化查询标识 | 否 | int | 是 |
| `DstarApiYesNoType` | `int` | `CashInOutInitQryFlag` | 出入金初始化查询标识 | 否 | int | 是 |

### `DstarApiReqPwdModField`

密码修改请求。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiPasswdType` | `str` | `Passwd` | 新密码 | 是 | char array | 否 |
| `DstarApiPasswdType` | `str` | `OldPasswd` | 旧密码 | 是 | char array | 否 |

### `DstarApiRspPwdModField`

密码修改应答。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiErrorCodeType` | `int` | `ErrorCode` | 错误码 | 否 | int | 是 |

### `DstarApiPwdModField`

密码修改通知。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |

### `DstarApiRspUdpAuthField`

UDP认证应答。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 账号索引 | 否 | int | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | udp认证码 | 否 | int | 否 |
| `DstarApiReqIdModeType` | `int` | `ReqIdMode` | 请求号模式,不强制模式:请求号不强制连续但要求增大;强制模式:请求号必须连续自增 | 否 | int | 是 |
| `DstarApiErrorCodeType` | `int` | `ErrorCode` | 错误码 | 否 | int | 是 |

### `DstarApiSeatField`

席位。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 席位索引 | 否 | int | 否 |
| `DstarApiSeatNoType` | `str` | `SeatNo` | 席位号 | 是 | char array | 否 |
| `DstarApiExchangeType` | `int` | `Exchange` | 交易所编号 | 否 | int | 是 |
| `DstarApiSeatStateType` | `int` | `SeatState` | 席位状态 | 否 | int | 是 |
| `DstarApiIPv4IpType` | `str` | `Ip` | 席位IP | 是 | char array | 否 |

### `DstarApiContractField`

合约数据。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiExchangeType` | `int` | `ExchangeId` | 交易所 | 否 | int | 是 |
| `DstarApiCommodityType` | `int` | `CommodityType` | 品种类型 | 否 | int | 是 |
| `DstarApiContractIndexType` | `int` | `ContractIndex` | 合约索引 | 否 | int | 否 |
| `DstarApiContractSizeType` | `int` | `ContractSize` | 每手乘数 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiContractTickSizeType` | `float` | `ContractTickSize` | 最小变动价位 | 否 | double | 否 |
| `DstarApiPriceType` | `float` | `PreSettlePrice` | 昨结算 | 否 | double | 否 |
| `DstarApiDateType` | `str` | `ExpDate` | 合约到期日 | 是 | char array | 否 |
| `DstarApiPriceType` | `float` | `LimitUpPrice` | 涨停价 | 否 | double | 否 |
| `DstarApiPriceType` | `float` | `LimitDownPrice` | 跌停价 | 否 | double | 否 |

### `DstarApiCmbContractField`

组合合约数据。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiExchangeType` | `int` | `ExchangeId` | 交易所 | 否 | int | 是 |
| `DstarApiCommodityType` | `int` | `CommodityType` | 品种类型 | 否 | int | 是 |
| `DstarApiContractIndexType` | `int` | `ContractIndex1` | 合约索引1 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo1` | 合约编号1 | 是 | char array | 否 |
| `DstarApiContractIndexType` | `int` | `ContractIndex2` | 合约索引2 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo2` | 合约编号2 | 是 | char array | 否 |

### `DstarApiOrderField`

委托数据。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiDirectType` | `int` | `Direct` | 买卖方向 | 否 | int | 是 |
| `DstarApiOffsetType` | `int` | `Offset` | 开平标志 | 否 | int | 是 |
| `DstarApiHedgeType` | `int` | `Hedge` | 投机套保 | 否 | int | 是 |
| `DstarApiValidTypeType` | `int` | `ValidType` | 有效类型 | 否 | int | 是 |
| `DstarApiPriceType` | `float` | `OrderPrice` | 委托价格 | 否 | double | 否 |
| `DstarApiQuantityType` | `int` | `OrderQty` | 委托数量 | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `MinQty` | 最小成交量 | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `MatchQty` | 成交量 | 否 | int | 否 |
| `DstarApiErrorCodeType` | `int` | `ErrCode` | 错误编号 | 否 | int | 是 |
| `DstarApiSerialIdType` | `int` | `SerialId` | 流号 | 否 | int | 否 |
| `DstarApiOrderIdType` | `int` | `OrderId` | 委托号 | 否 | int | 否 |
| `DstarApiFundType` | `float` | `FrozenMargin` | 冻结保证金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Margin` | 保证金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Fee` | 手续费 | 否 | double | 否 |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiOrderLocalNoType` | `str` | `OrderLocalNo` | 本地号 | 是 | char array | 否 |
| `DstarApiSystemNoType` | `str` | `SystemNo` | 系统号 | 是 | char array | 否 |
| `DstarApiDateTimeType` | `str` | `UpdateTime` | 更新时间 | 是 | char array | 否 |
| `DstarApiDateTimeType` | `str` | `ExchInsertTime` | 交易所下单时间 | 是 | char array | 否 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用(无报单引用时返回-1) | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo1` | 合约编号1 | 是 | char array | 否 |
| `DstarApiOrderTypeType` | `int` | `OrderType` | 委托类型 | 否 | int | 是 |
| `DstarApiOrderStateType` | `int` | `OrderState` | 委托状态 | 否 | int | 是 |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 接收席位索引 | 否 | int | 否 |
| `DstarApiSeatNoType` | `str` | `UpSeatNo` | 报单席位号 | 是 | char array | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo2` | 合约编号2 | 是 | char array | 否 |
| `DstarApiOrderIdType` | `int` | `CmbId` | 组合号 | 否 | int | 否 |
| `DstarApiFundType` | `float` | `OrderFee` | 申报费 | 否 | double | 否 |

### `DstarApiRspOrderInsertField`

报单应答。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 席位索引 | 否 | int | 否 |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiClientReqId` | `int` | `ClientReqId` | 客户请求号 | 否 | int | 否 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用(无报单引用时返回-1) | 否 | int | 否 |
| `DstarApiClientReqId` | `int` | `MaxClientReqId` | 最大请求号 | 否 | int | 否 |
| `DstarApiOrderIdType` | `int` | `OrderId` | 委托号 | 否 | int | 否 |
| `DstarApiDateTimeType` | `str` | `InsertTime` | 下单时间 | 是 | char array | 否 |
| `DstarApiErrorCodeType` | `int` | `ErrCode` | 错误编号 | 否 | int | 是 |

### `DstarApiOfferField`

报价通知。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiOffsetType` | `int` | `BuyOffset` | 买开平标志 | 否 | int | 是 |
| `DstarApiOffsetType` | `int` | `SellOffset` | 卖开平标志 | 否 | int | 是 |
| `DstarApiQuantityType` | `int` | `OrderQty` | 报价数量（郑商所、上期所）（C++ 匿名 union 成员） | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `BuyOrderQty` | 买报价数量（中金所、大商所、广期所）（C++ 匿名 union 成员） | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `BuyPrice` | 买价 | 否 | double | 否 |
| `DstarApiPriceType` | `float` | `SellPrice` | 卖价 | 否 | double | 否 |
| `DstarApiQuantityType` | `int` | `BuyMatchQty` | 买成交量 | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `SellMatchQty` | 卖成交量 | 否 | int | 否 |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiOrderLocalNoType` | `str` | `OrderLocalNo` | 本地号 | 是 | char array | 否 |
| `DstarApiSystemNoType` | `str` | `SystemNo` | 系统号 | 是 | char array | 否 |
| `DstarApiSystemNoType` | `str` | `EnquiryNo` | 询价号 | 是 | char array | 否 |
| `DstarApiDateTimeType` | `str` | `UpdateTime` | 更新时间 | 是 | char array | 否 |
| `DstarApiDateTimeType` | `str` | `ExchInsertTime` | 交易所下单时间 | 是 | char array | 否 |
| `DstarApiFundType` | `float` | `FrozenMargin` | 冻结保证金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Margin` | 保证金 | 否 | double | 否 |
| `DstarApiSerialIdType` | `int` | `SerialId` | 流号 | 否 | int | 否 |
| `DstarApiOrderIdType` | `int` | `OrderId` | 委托号 | 否 | int | 否 |
| `DstarApiErrorCodeType` | `int` | `ErrCode` | 错误编号 | 否 | int | 是 |
| `DstarApiOrderStateType` | `int` | `OrderState` | 报价状态 | 否 | int | 是 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用(无报单引用时返回-1) | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 接收席位索引 | 否 | int | 否 |
| `DstarApiSeatNoType` | `str` | `UpSeatNo` | 报价席位号 | 是 | char array | 否 |
| `DstarApiQuantityType` | `int` | `SellOrderQty` | 卖报价数量（中金所、大商所、广期所） | 否 | int | 否 |

### `DstarApiEnquiryField`

询价通知。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiDirectType` | `int` | `Direct` | 买卖方向 | 否 | int | 是 |
| `DstarApiSystemNoType` | `str` | `EnquiryNo` | 询价号 | 是 | char array | 否 |

### `DstarApiMatchField`

成交数据。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiQuantityType` | `int` | `MatchQty` | 成交数量 | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `MatchPrice` | 成交价格 | 否 | double | 否 |
| `DstarApiOffsetType` | `int` | `Offset` | 开平标志 | 否 | int | 是 |
| `DstarApiDirectType` | `int` | `Direct` | 买卖方向 | 否 | int | 是 |
| `DstarApiHedgeType` | `int` | `Hedge` | 投机套保 | 否 | int | 是 |
| `DstarApiOrderTypeType` | `int` | `OrderType` | 委托类型 | 否 | int | 是 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用(无报单引用时返回-1) | 否 | int | 否 |
| `DstarApiSerialIdType` | `int` | `SerialId` | 流号 | 否 | int | 否 |
| `DstarApiOrderIdType` | `int` | `OrderId` | 委托号 | 否 | int | 否 |
| `DstarApiMatchIdType` | `int` | `MatchId` | 成交号 | 否 | int | 否 |
| `DstarApiMatchTimeType` | `str` | `MatchTime` | 成交时间 | 是 | char array | 否 |
| `DstarApiExchMatchNo` | `str` | `ExchMatchNo` | 交易所成交号 | 是 | char array | 否 |
| `DstarApiSystemNoType` | `str` | `SystemNo` | 系统号 | 是 | char array | 否 |
| `DstarApiFundType` | `float` | `Fee` | 手续费 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Margin` | 保证金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `FrozenMargin` | 冻结保证金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Premium` | 权利金（C++ 匿名 union 成员） | 否 | double | 否 |
| `DstarApiFundType` | `float` | `CloseProfit` | 平仓盈亏（C++ 匿名 union 成员） | 否 | double | 否 |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiDateTimeType` | `str` | `UpdateTime` | 更新时间 | 是 | char array | 否 |
| `DstarApiOrderIdType` | `int` | `CmbId` | 组合号 | 否 | int | 否 |
| `DstarApiFundType` | `float` | `OrderFee` | 申报费 | 否 | double | 否 |

### `DstarApiPrePositionField`

昨持仓数据。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiQuantityType` | `int` | `PreBuyQty` | 昨买持仓量 | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `PreBuyAvgPrice` | 昨买持仓均价 | 否 | double | 否 |
| `DstarApiQuantityType` | `int` | `PreSellQty` | 昨卖持仓量 | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `PreSellAvgPrice` | 昨卖持仓均价 | 否 | double | 否 |

### `DstarApiPositionField`

实时持仓。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiQuantityType` | `int` | `PreBuyQty` | 昨买持仓量 | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `TodayBuyQty` | 今买持仓量 (总买持仓量=昨买持仓量+今买持仓量) | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `BuyAvgPrice` | 买持仓均价 | 否 | double | 否 |
| `DstarApiQuantityType` | `int` | `PreSellQty` | 昨卖持仓量 | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `TodaySellQty` | 今卖持仓量 (总卖持仓量=昨卖持仓量+今卖持仓量) | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `SellAvgPrice` | 卖持仓均价 | 否 | double | 否 |
| `DstarApiSerialIdType` | `int` | `SerialId` | 持仓数据对应流号 | 否 | int | 否 |

### `DstarApiFundField`

资金数据。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiFundType` | `float` | `PreEquity` | 昨权益 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Equity` | 权益 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Avail` | 可用 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Fee` | 手续费 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Margin` | 保证金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `FrozenMargin` | 冻结保证金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Premium` | 权利金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `CloseProfit` | 平仓盈亏 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `PositionProfit` | 持仓盈亏 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `CashIn` | 入金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `CashOut` | 出金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `OrderFee` | 申报费 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `Frozen` | 冻结资金 | 否 | double | 否 |
| `DstarApiFundType` | `float` | `DeliveryFrozen` | 交割冻结资金 | 否 | double | 否 |

### `DstarApiCashInOutField`

出入金通知。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiSerialIdType` | `int` | `SerialId` | 流号 | 否 | int | 否 |
| `DstarApiCashInOutType` | `int` | `CashInOutType` | 出入金类型 | 否 | int | 是 |
| `DstarApiCashInOutModeType` | `int` | `CashInOutMode` | 出入金方式 | 否 | int | 是 |
| `DstarApiFundType` | `float` | `CashInOutValue` | 出入金金额 | 否 | double | 否 |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiDateTimeType` | `str` | `OperateTime` | 操作时间 | 是 | char array | 否 |

### `DstaApiRspLastReqIdField`

最新请求号应答。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiClientReqId` | `int` | `LastClientReqId` | 最新请求号 | 否 | int | 否 |

### `DstarApiTrdExchangeStateField`

市场状态。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiExchangeType` | `int` | `ExchangeId` | 交易所 | 否 | int | 是 |
| `DstarApiCommodityType` | `int` | `CommodityType` | 品种类型 | 否 | int | 是 |
| `DstarApiCommodityNoType` | `str` | `CommodityNo` | 品种号 | 是 | char array | 否 |
| `DstarApiTradingStateType` | `int` | `TradingState` | 交易状态 | 否 | int | 是 |
| `DstarApiDateTimeType` | `str` | `ExchangeTime` | 交易所时间 | 是 | char array | 否 |

### `DstarApiTrdFeeParamField`

手续费参数。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiParamType` | `float` | `OpenRatio` | 开仓按比例 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `OpenVolume` | 开仓按手数 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `CloseRatio` | 平仓按比例 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `CloseVolume` | 平仓按手数 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `CloseTRatio` | 平今按比例 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `CloseTVolume` | 平今按手数 | 否 | double | 否 |

### `DstarApiTrdMarParamField`

保证金参数。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiParamType` | `float` | `BuySpeculateParam` | 买投机参数 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `BuyHedgeParam` | 买套保参数 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `SellSpeculateParam` | 卖投机参数 | 否 | double | 否 |
| `DstarApiParamType` | `float` | `SellHedgeParam` | 买套保参数 | 否 | double | 否 |

### `DstarApiPosiProfitField`

浮盈通知。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiFundType` | `float` | `PosiProfit` | 持仓盈亏 | 否 | double | 否 |
| `DstarApiSerialIdType` | `int` | `SerialId` | 流号 | 否 | int | 否 |

### `DstarApiTradeRightField`

交易权限。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiExchangeType` | `int` | `ExchangeId` | 交易所标识 | 否 | int | 是 |
| `DstarApiCommodityType` | `int` | `CommodityType` | 品种类型 | 否 | int | 是 |
| `DstarApiCommodityNoType` | `str` | `CommodityNo` | 品种 | 是 | char array | 否 |
| `DstarApiTradeRightType` | `int` | `BuyTradeRight` | 买交易权限 | 否 | int | 是 |
| `DstarApiTradeRightType` | `int` | `SellTradeRight` | 卖交易权限 | 否 | int | 是 |

### `DstarApiTradeRightDelField`

交易权限删除。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiExchangeType` | `int` | `ExchangeId` | 交易所标识 | 否 | int | 是 |
| `DstarApiCommodityType` | `int` | `CommodityType` | 品种类型 | 否 | int | 是 |
| `DstarApiCommodityNoType` | `str` | `CommodityNo` | 品种 | 是 | char array | 否 |

### `DstarApiAccountCommListField`

客户品种白名单。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountNoType` | `str` | `AccountNo` | 账号 | 是 | char array | 否 |
| `DstarApiExchangeType` | `int` | `ExchangeId` | 交易所标识 | 否 | int | 是 |
| `DstarApiCommodityType` | `int` | `CommodityType` | 品种类型 | 否 | int | 是 |
| `DstarApiCommodityNoType` | `str` | `CommodityNo` | 品种 | 是 | char array | 否 |

### `DstarApiHead`

UDP协议头。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiProtocolCodeType` | `int` | `ProtocolCode` | 协议号 | 否 | int | 是 |
| `DstarApiDataLen` | `int` | `DataLen` | 数据长度(不包含协议头) | 否 | int | 否 |

### `DstarApiReqUdpAuthField`

UDP认证请求。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 账号索引 | 否 | int | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | udp认证码 | 否 | int | 否 |
| `DstarApiReqIdModeType` | `int` | `ReqIdMode` | 请求号模式,不检查:不检查报单请求号;不强制模式:请求号不强制连续但要求增大;强制模式:请求号必须连续自增 | 否 | int | 是 |

### `DstarApiReqOrderInsertField`

报单请求。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiDirectType` | `int` | `Direct` | 买卖方向 | 否 | int | 是 |
| `DstarApiOffsetType` | `int` | `Offset` | 开平标志 | 否 | int | 是 |
| `DstarApiHedgeType` | `int` | `Hedge` | 投机套保 | 否 | int | 是 |
| `DstarApiOrderTypeType` | `int` | `OrderType` | 委托类型 | 否 | int | 是 |
| `DstarApiValidTypeType` | `int` | `ValidType` | 有效类型 | 否 | int | 是 |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 席位索引,0轮询席位,非0指定席位 | 否 | int | 否 |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 客户索引 | 否 | int | 否 |
| `DstarApiContractIndexType` | `int` | `ContractIndex` | 合约索引 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiQuantityType` | `int` | `OrderQty` | 委托数量 | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `MinQty` | 最小成交量 | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `OrderPrice` | 委托价格 | 否 | double | 否 |
| `DstarApiClientReqId` | `int` | `ClientReqId` | 客户请求号 | 否 | int | 否 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用(>=0,负数无效) | 否 | int | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | udp认证码 | 否 | int | 否 |

### `DstarApiReqOfferInsertField`

报价请求。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiOffsetType` | `int` | `BuyOffset` | 买开平标志 | 否 | int | 是 |
| `DstarApiOffsetType` | `int` | `SellOffset` | 卖开平标志 | 否 | int | 是 |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 客户索引 | 否 | int | 否 |
| `DstarApiClientReqId` | `int` | `ClientReqId` | 客户请求号 | 否 | int | 否 |
| `DstarApiContractIndexType` | `int` | `ContractIndex` | 合约索引 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiQuantityType` | `int` | `OrderQty` | 报价数量 | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `BuyPrice` | 买价 | 否 | double | 否 |
| `DstarApiPriceType` | `float` | `SellPrice` | 卖价 | 否 | double | 否 |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 席位索引 | 否 | int | 否 |
| `DstarApiSystemNoType` | `str` | `EnquiryNo` | 询价号 | 是 | char array | 否 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用 | 否 | int | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | udp认证码 | 否 | int | 否 |

### `DstarApiReqOfferInsertNewField`

新报价请求。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiOffsetType` | `int` | `BuyOffset` | 买开平标志 | 否 | int | 是 |
| `DstarApiOffsetType` | `int` | `SellOffset` | 卖开平标志 | 否 | int | 是 |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 客户索引 | 否 | int | 否 |
| `DstarApiClientReqId` | `int` | `ClientReqId` | 客户请求号 | 否 | int | 否 |
| `DstarApiContractIndexType` | `int` | `ContractIndex` | 合约索引 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo` | 合约编号 | 是 | char array | 否 |
| `DstarApiU16QuantityType` | `int` | `BuyOrderQty` | 买报价量 | 否 | int | 否 |
| `DstarApiU16QuantityType` | `int` | `SellOrderQty` | 卖报价量 | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `BuyPrice` | 买价 | 否 | double | 否 |
| `DstarApiPriceType` | `float` | `SellPrice` | 卖价 | 否 | double | 否 |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 席位索引 | 否 | int | 否 |
| `DstarApiSystemNoType` | `str` | `EnquiryNo` | 询价号 | 是 | char array | 否 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用 | 否 | int | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | udp认证码 | 否 | int | 否 |
| `DstarApiReplaceIdType` | `int` | `ReplaceId` | 定单委托号(中金所使用) | 否 | int | 是 |

### `DstarApiReqOrderDeleteField`

撤单请求 (撤单失败时返回委托通知或报价通知,订单状态不变,包含撤单失败的错误码)。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 客户索引 | 否 | int | 否 |
| `DstarApiClientReqId` | `int` | `ClientReqId` | 客户请求号 | 否 | int | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | udp认证码 | 否 | int | 否 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用(>=0,负数无效) | 否 | int | 否 |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 席位索引,0从报单席位撤单,非0从指定席位撤单 | 否 | int | 否 |
| `DstarApiOrderIdType` | `int` | `OrderId` | 委托号 | 否 | int | 否 |
| `DstarApiSystemNoType` | `str` | `SystemNo` | 系统号 | 是 | char array | 否 |

### `DstarApiReqCmbOrderInsertField`

组合报单请求。

| C++ 类型 | Python 类型 | 字段名 | 字段含义 | char 数组 | int/float/double | 枚举 |
| --- | --- | --- | --- | --- | --- | --- |
| `DstarApiDirectType` | `int` | `Direct` | 买卖方向 | 否 | int | 是 |
| `DstarApiOffsetType` | `int` | `Offset` | 开平标志 | 否 | int | 是 |
| `DstarApiHedgeType` | `int` | `Hedge` | 投机套保 | 否 | int | 是 |
| `DstarApiOrderTypeType` | `int` | `OrderType` | 委托类型 | 否 | int | 是 |
| `DstarApiValidTypeType` | `int` | `ValidType` | 有效类型 | 否 | int | 是 |
| `DstarApiSeatIndexType` | `int` | `SeatIndex` | 席位索引 | 否 | int | 否 |
| `DstarApiAccountIndexType` | `int` | `AccountIndex` | 客户索引 | 否 | int | 否 |
| `DstarApiContractIndexType` | `int` | `ContractIndex1` | 合约索引 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo1` | 合约号 | 是 | char array | 否 |
| `DstarApiContractIndexType` | `int` | `ContractIndex2` | 合约索引 | 否 | int | 否 |
| `DstarApiContractNoType` | `str` | `ContractNo2` | 合约号 | 是 | char array | 否 |
| `DstarApiQuantityType` | `int` | `OrderQty` | 委托数量 | 否 | int | 否 |
| `DstarApiQuantityType` | `int` | `MinQty` | 最小成交量 | 否 | int | 否 |
| `DstarApiPriceType` | `float` | `OrderPrice` | 委托价格 | 否 | double | 否 |
| `DstarApiClientReqId` | `int` | `ClientReqId` | 客户请求号 | 否 | int | 否 |
| `DstarApiReferenceType` | `int` | `Reference` | 报单引用 | 否 | int | 否 |
| `DstarApiAuthCodeType` | `int` | `UdpAuthCode` | udp认证码 | 否 | int | 否 |

## Typedef 结构别名

| C++ 别名 | 原结构体 | Python 映射 |
| --- | --- | --- |
| `DstarApiRspOrderDeleteField` | `DstarApiRspOrderInsertField` | `DstarApiRspOrderDeleteField = DstarApiRspOrderInsertField` |
| `DstarApiRspOfferInsertField` | `DstarApiRspOrderInsertField` | `DstarApiRspOfferInsertField = DstarApiRspOrderInsertField` |

## 转换约定

- `DstarField.from_dict()` 接受与 C++ 字段同名的 mapping；未知字段由 dataclass 构造器抛出 `TypeError`。
- `DstarField.to_dict()` 使用 `dataclasses.asdict()` 返回基础 Python 字典。
- 所有字段均有零值默认值：字符串为 `""`，整数/枚举为 `0`，浮点数为 `0.0`。
- 枚举字段不强制转换成枚举实例，避免未知或交易所扩展值在解析时失败；调用方可按需使用 `EnumType(value)`。
- `DstaApiRspLastReqIdField` 保留官方头文件中的 `Dsta` 拼写。
