"""可读的 Dstar 数据类型枚举。

C++ 头文件使用 char 或整数常量而不是真正的 ``enum``。为满足数据模型字段先保留
``int`` 的约束，本模块使用 ``IntEnum``，字符常量以其单字节 ``ord`` 值表示。
"""

from enum import IntEnum

from .errors import DstarErrorCode

class ProtocolVersion(IntEnum):
    """对应 C++ `DstarApiVersionType` 的可读常量。"""

    CURRENT = 3  # -

class NoticeSubscription(IntEnum):
    """对应 C++ `DstarApiNoticeSubIdType` 的可读常量。"""

    HEAD = 0  # 从头订阅
    LAST = -1  # 从最新订阅

class RealTimeDataFilter(IntEnum):
    """对应 C++ `DstarApiRealTimeDataFilterType` 的可读常量。"""

    NONE = 0  # 不过滤任何数据
    IGNORE_ALL = -1  # 过滤所有数据

class RunMode(IntEnum):
    """对应 C++ `DstarApiRunModeType` 的可读常量。"""

    FULL_LOAD = 0  # 运行模式满载
    NON_FULL_LOAD = -1  # 运行模式非满载

class InitMode(IntEnum):
    """对应 C++ `DstarApiInitType` 的可读常量。"""

    QUERY = 0  # 初始化过程中查询基础数据
    NO_QUERY = -1  # 初始化过程中不查询基础数据

class RequestIdMode(IntEnum):
    """对应 C++ `DstarApiReqIdModeType` 的可读常量。"""

    NO_CHECK = 0  # 不检测 对请求号不做检测
    INCREASE = 1  # 增大 请求号要比上一笔请求大,否则报撤单无效
    FORCE = 2  # 强制自增 要求请求号连续自增,否则报撤单无效

class Exchange(IntEnum):
    """对应 C++ `DstarApiExchangeType` 的可读常量。"""

    ZCE = ord('Z')  # 郑商所
    SHFE = ord('S')  # 上期所
    INE = ord('I')  # 能源所
    CFFEX = ord('C')  # 中金所
    DCE = ord('D')  # 大商所
    GFEX = ord('F')  # 广期所
    SGE = ord('G')  # 金交所

class CommodityType(IntEnum):
    """对应 C++ `DstarApiCommodityType` 的可读常量。"""

    FUTURES = ord('F')  # 期货
    OPTION = ord('O')  # 期权
    SPD = ord('S')  # 跨期套利
    IPS = ord('M')  # 跨品种套利
    STD = ord('D')  # 跨式套利
    STG = ord('G')  # 宽跨式套利
    PRT = ord('R')  # 备兑
    NONE = ord('N')  # 无

class Direction(IntEnum):
    """对应 C++ `DstarApiDirectType` 的可读常量。"""

    BUY = ord('B')  # 买方向
    SELL = ord('S')  # 卖方向
    ALL = ord('N')  # 所有

class Offset(IntEnum):
    """对应 C++ `DstarApiOffsetType` 的可读常量。"""

    OPEN = ord('O')  # 开仓
    CLOSE = ord('C')  # 平仓
    CLOSE_TODAY = ord('T')  # 平今

class Hedge(IntEnum):
    """对应 C++ `DstarApiHedgeType` 的可读常量。"""

    SPECULATE = ord('T')  # 投机
    HEDGE = ord('B')  # 套保

class OrderType(IntEnum):
    """对应 C++ `DstarApiOrderTypeType` 的可读常量。"""

    NONE = ord('0')  # 空
    MARKET = ord('1')  # 市价单
    LIMIT = ord('2')  # 限价单
    EXECUTE = ord('3')  # 行权
    ABANDON = ord('4')  # 弃权
    ENQUIRY = ord('5')  # 询价
    OFFER = ord('6')  # 报价
    SWAP = ord('7')  # 互换
    EFP = ord('8')  # 期转现

class TradeRight(IntEnum):
    """对应 C++ `DstarApiTradeRightType` 的可读常量。"""

    NORMAL = ord('0')  # 正常交易
    NO_TRADE = ord('1')  # 禁止交易
    CLOSE_ONLY = ord('2')  # 只可平仓

class ReplaceMode(IntEnum):
    """对应 C++ `DstarApiReplaceIdType` 的可读常量。"""

    NORMAL = 0  # 正常报价
    LAST = 1  # 顶最近一笔报价

class ValidType(IntEnum):
    """对应 C++ `DstarApiValidTypeType` 的可读常量。"""

    FOK = ord('1')  # 即时全部
    IOC = ord('2')  # 即时部分
    GFD = ord('3')  # 当日有效
    GIS = ord('4')  # 小节有效

class OrderState(IntEnum):
    """对应 C++ `DstarApiOrderStateType` 的可读常量。"""

    ACCEPT = ord('1')  # 已受理
    QUEUE = ord('2')  # 已排队
    APPLY = ord('3')  # 已申请(行权、弃权、套利等申请成功)
    SUSPENDED = ord('4')  # 已挂起
    TRIGGERED = ord('5')  # 已触发
    PARTIAL_FILL = ord('6')  # 部分成交
    FILLED = ord('7')  # 完全成交
    FAILED = ord('8')  # 指令失败
    DELETED = ord('B')  # 已撤单
    REMAINDER_DELETED = ord('C')  # 已撤余单
    SYSTEM_DELETED = ord('D')  # 已删除
    WAITING_TRIGGER = ord('E')  # 策略待触发

class CashInOutType(IntEnum):
    """对应 C++ `DstarApiCashInOutType` 的可读常量。"""

    IN = ord('I')  # 入金
    OUT = ord('O')  # 出金

class CashInOutMode(IntEnum):
    """对应 C++ `DstarApiCashInOutModeType` 的可读常量。"""

    TRANSFER = ord('1')  # 转账
    CHEQUE = ord('2')  # 支票
    CASH = ord('3')  # 现金
    SWAP = ord('4')  # 换汇
    BANK_FUTURES_TRANSFER = ord('5')  # 银期转账

class TradingState(IntEnum):
    """对应 C++ `DstarApiTradingStateType` 的可读常量。"""

    UNKNOWN = ord('0')  # 未知状态
    BID = ord('1')  # 集合竞价
    MATCH = ord('2')  # 集合竞价撮合
    CONTINUOUS = ord('3')  # 连续交易
    PAUSED = ord('4')  # 交易暂停
    CLOSED = ord('5')  # 闭市
    POST_CLOSE = ord('6')  # 闭市处理时间
    INITIALIZING = ord('7')  # 正初始化
    READY = ord('8')  # 准备就绪

class AuthType(IntEnum):
    """对应 C++ `DstarApiAuthTypeType` 的可读常量。"""

    NO_GATHER = ord('0')  # 不采集模式软件授权
    DIRECT = ord('1')  # 直连模式软件授权
    RELAY = ord('2')  # 中继模式软件授权

class StartMode(IntEnum):
    """对应 C++ `DstarApiStartModeType` 的可读常量。"""

    CHECK = 0  # 对账
    TRADE = 1  # 交易

class SeatState(IntEnum):
    """对应 C++ `DstarApiSeatStateType` 的可读常量。"""

    DISCONNECTED = ord('D')  # 断开
    NORMAL = ord('N')  # 正常

class YesNo(IntEnum):
    """对应 C++ `DstarApiYesNoType` 的可读常量。"""

    YES = 1  # 是
    NO = 0  # 否

class ProtocolCommand(IntEnum):
    """对应 C++ `DstarApiProtocolCodeType` 的可读常量。"""

    REQ_UDP_AUTH = 0xEC00  # Udp认证请求
    REQ_ORDER_INSERT = 0xEC01  # 报单请求
    REQ_OFFER_INSERT = 0xEC02  # 报价请求
    REQ_OFFER_INSERT_NEW = 0xEC09  # 新报价请求
    REQ_ORDER_DELETE = 0xEC03  # 撤单请求
    REQ_CMB_ORDER_INSERT = 0xEC04  # 组合报单请求

ENUM_BY_CPP_TYPE = {
    "DstarApiVersionType": ProtocolVersion,
    "DstarApiNoticeSubIdType": NoticeSubscription,
    "DstarApiRealTimeDataFilterType": RealTimeDataFilter,
    "DstarApiRunModeType": RunMode,
    "DstarApiInitType": InitMode,
    "DstarApiReqIdModeType": RequestIdMode,
    "DstarApiExchangeType": Exchange,
    "DstarApiCommodityType": CommodityType,
    "DstarApiDirectType": Direction,
    "DstarApiOffsetType": Offset,
    "DstarApiHedgeType": Hedge,
    "DstarApiOrderTypeType": OrderType,
    "DstarApiTradeRightType": TradeRight,
    "DstarApiReplaceIdType": ReplaceMode,
    "DstarApiValidTypeType": ValidType,
    "DstarApiOrderStateType": OrderState,
    "DstarApiCashInOutType": CashInOutType,
    "DstarApiCashInOutModeType": CashInOutMode,
    "DstarApiTradingStateType": TradingState,
    "DstarApiAuthTypeType": AuthType,
    "DstarApiStartModeType": StartMode,
    "DstarApiSeatStateType": SeatState,
    "DstarApiYesNoType": YesNo,
    "DstarApiProtocolCodeType": ProtocolCommand,
    "DstarApiErrorCodeType": DstarErrorCode,
}

__all__ = [
    "ProtocolVersion",
    "NoticeSubscription",
    "RealTimeDataFilter",
    "RunMode",
    "InitMode",
    "RequestIdMode",
    "Exchange",
    "CommodityType",
    "Direction",
    "Offset",
    "Hedge",
    "OrderType",
    "TradeRight",
    "ReplaceMode",
    "ValidType",
    "OrderState",
    "CashInOutType",
    "CashInOutMode",
    "TradingState",
    "AuthType",
    "StartMode",
    "SeatState",
    "YesNo",
    "ProtocolCommand",
    "DstarErrorCode",
    "ENUM_BY_CPP_TYPE",
]
