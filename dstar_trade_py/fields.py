"""Dstar C++ packed structures represented as pure Python dataclasses.

The classes preserve vendor structure and field names to make later pybind11 conversion
unambiguous. Fixed-size C char arrays use ``str``; enum-coded fields intentionally use
``int`` and can be interpreted with :mod:`dstar_trade_py.enums`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, ClassVar, Mapping, TypeVar


ModelT = TypeVar("ModelT", bound="DstarField")


class DstarField:
    """所有 Dstar 数据结构的转换基类。"""

    CPP_NAME: ClassVar[str]

    @classmethod
    def from_dict(cls: type[ModelT], data: Mapping[str, Any]) -> ModelT:
        """使用与 C++ 字段同名的字典创建数据模型。"""

        return cls(**dict(data))

    def to_dict(self) -> dict[str, Any]:
        """递归转换为仅包含 Python 基础值的字典。"""

        return asdict(self)


@dataclass(slots=True)
class DstarApiReqLoginField(DstarField):
    """对应 C++ `DstarApiReqLoginField`：登录请求。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqLoginField"
    AccountNo: str = ""  # 账号
    Password: str = ""  # 密码
    AppId: str = ""  # app id(中继模式填中继app id)
    LicenseNo: str = ""  # 软件授权号

@dataclass(slots=True)
class DstarApiRspLoginField(DstarField):
    """对应 C++ `DstarApiRspLoginField`：登录应答。"""

    CPP_NAME: ClassVar[str] = "DstarApiRspLoginField"
    AccountIndex: int = 0  # 账号索引
    AccountNo: str = ""  # 账号
    TradeDate: str = ""  # 当前交易日
    UdpAuthCode: int = 0  # UDP认证码
    ErrorCode: int = 0  # 错误码
    StartTime: int = 0  # 交易系统启动时间
    StartMode: int = 0  # 交易系统启动模式
    FloatFlag: int = 0  # 持仓盈利是否计入可用

@dataclass(slots=True)
class DstarApiSubmitInfoField(DstarField):
    """对应 C++ `DstarApiSubmitInfoField`：上报信息。"""

    CPP_NAME: ClassVar[str] = "DstarApiSubmitInfoField"
    AccountNo: str = ""  # 账号
    AuthType: int = 0  # 授权类型
    AuthKeyVersion: int = 0  # 密钥版本号
    SystemInfo: str = ""  # 系统采集信息
    ClientLoginIp: str = ""  # 客户登录ip,直连模式不需要填写,中继模式需要填写
    ClientLoginPort: int = 0  # 客户登录port,直连模式不需要填写,中继模式需要填写
    ClientLoginDateTime: str = ""  # 登录时间,直连模式不需要填写,中继模式需要填写
    ClientAppId: str = ""  # app id
    LicenseNo: str = ""  # 软件授权号

@dataclass(slots=True)
class DstarApiRspSubmitInfoField(DstarField):
    """对应 C++ `DstarApiRspSubmitInfoField`：上报信息应答。"""

    CPP_NAME: ClassVar[str] = "DstarApiRspSubmitInfoField"
    AccountNo: str = ""  # 账号
    ErrorCode: int = 0  # 错误码

@dataclass(slots=True)
class DstarApiInitQryInfoField(DstarField):
    """对应 C++ `DstarApiInitQryInfoField`：初始化数据查询。"""

    CPP_NAME: ClassVar[str] = "DstarApiInitQryInfoField"
    ContractInitQryFlag: int = 0  # 合约初始化查询标识
    CmbContractInitQryFlag: int = 0  # 组合合约初始化查询标识
    SeatInitQryFlag: int = 0  # 席位信息初始化查询标识
    TrdFeeInitQryFlag: int = 0  # 手续费参数初始化查询标识
    TrdMarInitQryFlag: int = 0  # 保证金参数初始化查询标识
    TrdRightInitQryFlag: int = 0  # 交易权限初始化查询标识
    AccountCommListInitQryFlag: int = 0  # 客户白名单初始化查询标识
    TrdExchangeStateInitQryFlag: int = 0  # 市场状态初始化查询标识
    PrePositionInitQryFlag: int = 0  # 昨持仓快照初始化查询标识
    OrderInitQryFlag: int = 0  # 委托信息初始化查询标识
    OfferInitQryFlag: int = 0  # 报价信息初始化查询标识
    MatchInitQryFlag: int = 0  # 成交信息初始化查询标识
    CashInOutInitQryFlag: int = 0  # 出入金初始化查询标识

@dataclass(slots=True)
class DstarApiReqPwdModField(DstarField):
    """对应 C++ `DstarApiReqPwdModField`：密码修改请求。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqPwdModField"
    Passwd: str = ""  # 新密码
    OldPasswd: str = ""  # 旧密码

@dataclass(slots=True)
class DstarApiRspPwdModField(DstarField):
    """对应 C++ `DstarApiRspPwdModField`：密码修改应答。"""

    CPP_NAME: ClassVar[str] = "DstarApiRspPwdModField"
    AccountNo: str = ""  # 账号
    ErrorCode: int = 0  # 错误码

@dataclass(slots=True)
class DstarApiPwdModField(DstarField):
    """对应 C++ `DstarApiPwdModField`：密码修改通知。"""

    CPP_NAME: ClassVar[str] = "DstarApiPwdModField"
    AccountNo: str = ""  # 账号

@dataclass(slots=True)
class DstarApiRspUdpAuthField(DstarField):
    """对应 C++ `DstarApiRspUdpAuthField`：UDP认证应答。"""

    CPP_NAME: ClassVar[str] = "DstarApiRspUdpAuthField"
    AccountIndex: int = 0  # 账号索引
    UdpAuthCode: int = 0  # udp认证码
    ReqIdMode: int = 0  # 请求号模式,不强制模式:请求号不强制连续但要求增大;强制模式:请求号必须连续自增
    ErrorCode: int = 0  # 错误码

@dataclass(slots=True)
class DstarApiSeatField(DstarField):
    """对应 C++ `DstarApiSeatField`：席位。"""

    CPP_NAME: ClassVar[str] = "DstarApiSeatField"
    SeatIndex: int = 0  # 席位索引
    SeatNo: str = ""  # 席位号
    Exchange: int = 0  # 交易所编号
    SeatState: int = 0  # 席位状态
    Ip: str = ""  # 席位IP

@dataclass(slots=True)
class DstarApiContractField(DstarField):
    """对应 C++ `DstarApiContractField`：合约数据。"""

    CPP_NAME: ClassVar[str] = "DstarApiContractField"
    ExchangeId: int = 0  # 交易所
    CommodityType: int = 0  # 品种类型
    ContractIndex: int = 0  # 合约索引
    ContractSize: int = 0  # 每手乘数
    ContractNo: str = ""  # 合约编号
    ContractTickSize: float = 0.0  # 最小变动价位
    PreSettlePrice: float = 0.0  # 昨结算
    ExpDate: str = ""  # 合约到期日
    LimitUpPrice: float = 0.0  # 涨停价
    LimitDownPrice: float = 0.0  # 跌停价

@dataclass(slots=True)
class DstarApiCmbContractField(DstarField):
    """对应 C++ `DstarApiCmbContractField`：组合合约数据。"""

    CPP_NAME: ClassVar[str] = "DstarApiCmbContractField"
    ExchangeId: int = 0  # 交易所
    CommodityType: int = 0  # 品种类型
    ContractIndex1: int = 0  # 合约索引1
    ContractNo1: str = ""  # 合约编号1
    ContractIndex2: int = 0  # 合约索引2
    ContractNo2: str = ""  # 合约编号2

@dataclass(slots=True)
class DstarApiOrderField(DstarField):
    """对应 C++ `DstarApiOrderField`：委托数据。"""

    CPP_NAME: ClassVar[str] = "DstarApiOrderField"
    Direct: int = 0  # 买卖方向
    Offset: int = 0  # 开平标志
    Hedge: int = 0  # 投机套保
    ValidType: int = 0  # 有效类型
    OrderPrice: float = 0.0  # 委托价格
    OrderQty: int = 0  # 委托数量
    MinQty: int = 0  # 最小成交量
    MatchQty: int = 0  # 成交量
    ErrCode: int = 0  # 错误编号
    SerialId: int = 0  # 流号
    OrderId: int = 0  # 委托号
    FrozenMargin: float = 0.0  # 冻结保证金
    Margin: float = 0.0  # 保证金
    Fee: float = 0.0  # 手续费
    AccountNo: str = ""  # 账号
    OrderLocalNo: str = ""  # 本地号
    SystemNo: str = ""  # 系统号
    UpdateTime: str = ""  # 更新时间
    ExchInsertTime: str = ""  # 交易所下单时间
    Reference: int = 0  # 报单引用(无报单引用时返回-1)
    ContractNo1: str = ""  # 合约编号1
    OrderType: int = 0  # 委托类型
    OrderState: int = 0  # 委托状态
    SeatIndex: int = 0  # 接收席位索引
    UpSeatNo: str = ""  # 报单席位号
    ContractNo2: str = ""  # 合约编号2
    CmbId: int = 0  # 组合号
    OrderFee: float = 0.0  # 申报费

@dataclass(slots=True)
class DstarApiRspOrderInsertField(DstarField):
    """对应 C++ `DstarApiRspOrderInsertField`：报单应答。"""

    CPP_NAME: ClassVar[str] = "DstarApiRspOrderInsertField"
    SeatIndex: int = 0  # 席位索引
    AccountNo: str = ""  # 账号
    ClientReqId: int = 0  # 客户请求号
    Reference: int = 0  # 报单引用(无报单引用时返回-1)
    MaxClientReqId: int = 0  # 最大请求号
    OrderId: int = 0  # 委托号
    InsertTime: str = ""  # 下单时间
    ErrCode: int = 0  # 错误编号

@dataclass(slots=True)
class DstarApiOfferField(DstarField):
    """对应 C++ `DstarApiOfferField`：报价通知。"""

    CPP_NAME: ClassVar[str] = "DstarApiOfferField"
    BuyOffset: int = 0  # 买开平标志
    SellOffset: int = 0  # 卖开平标志
    OrderQty: int = 0  # 报价数量（郑商所、上期所）；C++ 匿名 union 成员
    BuyOrderQty: int = 0  # 买报价数量（中金所、大商所、广期所）；C++ 匿名 union 成员
    BuyPrice: float = 0.0  # 买价
    SellPrice: float = 0.0  # 卖价
    BuyMatchQty: int = 0  # 买成交量
    SellMatchQty: int = 0  # 卖成交量
    AccountNo: str = ""  # 账号
    OrderLocalNo: str = ""  # 本地号
    SystemNo: str = ""  # 系统号
    EnquiryNo: str = ""  # 询价号
    UpdateTime: str = ""  # 更新时间
    ExchInsertTime: str = ""  # 交易所下单时间
    FrozenMargin: float = 0.0  # 冻结保证金
    Margin: float = 0.0  # 保证金
    SerialId: int = 0  # 流号
    OrderId: int = 0  # 委托号
    ErrCode: int = 0  # 错误编号
    OrderState: int = 0  # 报价状态
    Reference: int = 0  # 报单引用(无报单引用时返回-1)
    ContractNo: str = ""  # 合约编号
    SeatIndex: int = 0  # 接收席位索引
    UpSeatNo: str = ""  # 报价席位号
    SellOrderQty: int = 0  # 卖报价数量（中金所、大商所、广期所）

@dataclass(slots=True)
class DstarApiEnquiryField(DstarField):
    """对应 C++ `DstarApiEnquiryField`：询价通知。"""

    CPP_NAME: ClassVar[str] = "DstarApiEnquiryField"
    ContractNo: str = ""  # 合约编号
    Direct: int = 0  # 买卖方向
    EnquiryNo: str = ""  # 询价号

@dataclass(slots=True)
class DstarApiMatchField(DstarField):
    """对应 C++ `DstarApiMatchField`：成交数据。"""

    CPP_NAME: ClassVar[str] = "DstarApiMatchField"
    ContractNo: str = ""  # 合约编号
    MatchQty: int = 0  # 成交数量
    MatchPrice: float = 0.0  # 成交价格
    Offset: int = 0  # 开平标志
    Direct: int = 0  # 买卖方向
    Hedge: int = 0  # 投机套保
    OrderType: int = 0  # 委托类型
    Reference: int = 0  # 报单引用(无报单引用时返回-1)
    SerialId: int = 0  # 流号
    OrderId: int = 0  # 委托号
    MatchId: int = 0  # 成交号
    MatchTime: str = ""  # 成交时间
    ExchMatchNo: str = ""  # 交易所成交号
    SystemNo: str = ""  # 系统号
    Fee: float = 0.0  # 手续费
    Margin: float = 0.0  # 保证金
    FrozenMargin: float = 0.0  # 冻结保证金
    Premium: float = 0.0  # 权利金；C++ 匿名 union 成员
    CloseProfit: float = 0.0  # 平仓盈亏；C++ 匿名 union 成员
    AccountNo: str = ""  # 账号
    UpdateTime: str = ""  # 更新时间
    CmbId: int = 0  # 组合号
    OrderFee: float = 0.0  # 申报费

@dataclass(slots=True)
class DstarApiPrePositionField(DstarField):
    """对应 C++ `DstarApiPrePositionField`：昨持仓数据。"""

    CPP_NAME: ClassVar[str] = "DstarApiPrePositionField"
    AccountNo: str = ""  # 账号
    ContractNo: str = ""  # 合约编号
    PreBuyQty: int = 0  # 昨买持仓量
    PreBuyAvgPrice: float = 0.0  # 昨买持仓均价
    PreSellQty: int = 0  # 昨卖持仓量
    PreSellAvgPrice: float = 0.0  # 昨卖持仓均价

@dataclass(slots=True)
class DstarApiPositionField(DstarField):
    """对应 C++ `DstarApiPositionField`：实时持仓。"""

    CPP_NAME: ClassVar[str] = "DstarApiPositionField"
    AccountNo: str = ""  # 账号
    ContractNo: str = ""  # 合约编号
    PreBuyQty: int = 0  # 昨买持仓量
    TodayBuyQty: int = 0  # 今买持仓量 (总买持仓量=昨买持仓量+今买持仓量)
    BuyAvgPrice: float = 0.0  # 买持仓均价
    PreSellQty: int = 0  # 昨卖持仓量
    TodaySellQty: int = 0  # 今卖持仓量 (总卖持仓量=昨卖持仓量+今卖持仓量)
    SellAvgPrice: float = 0.0  # 卖持仓均价
    SerialId: int = 0  # 持仓数据对应流号

@dataclass(slots=True)
class DstarApiFundField(DstarField):
    """对应 C++ `DstarApiFundField`：资金数据。"""

    CPP_NAME: ClassVar[str] = "DstarApiFundField"
    AccountNo: str = ""  # 账号
    PreEquity: float = 0.0  # 昨权益
    Equity: float = 0.0  # 权益
    Avail: float = 0.0  # 可用
    Fee: float = 0.0  # 手续费
    Margin: float = 0.0  # 保证金
    FrozenMargin: float = 0.0  # 冻结保证金
    Premium: float = 0.0  # 权利金
    CloseProfit: float = 0.0  # 平仓盈亏
    PositionProfit: float = 0.0  # 持仓盈亏
    CashIn: float = 0.0  # 入金
    CashOut: float = 0.0  # 出金
    OrderFee: float = 0.0  # 申报费
    Frozen: float = 0.0  # 冻结资金
    DeliveryFrozen: float = 0.0  # 交割冻结资金

@dataclass(slots=True)
class DstarApiCashInOutField(DstarField):
    """对应 C++ `DstarApiCashInOutField`：出入金通知。"""

    CPP_NAME: ClassVar[str] = "DstarApiCashInOutField"
    SerialId: int = 0  # 流号
    CashInOutType: int = 0  # 出入金类型
    CashInOutMode: int = 0  # 出入金方式
    CashInOutValue: float = 0.0  # 出入金金额
    AccountNo: str = ""  # 账号
    OperateTime: str = ""  # 操作时间

@dataclass(slots=True)
class DstaApiRspLastReqIdField(DstarField):
    """对应 C++ `DstaApiRspLastReqIdField`：最新请求号应答。"""

    CPP_NAME: ClassVar[str] = "DstaApiRspLastReqIdField"
    LastClientReqId: int = 0  # 最新请求号

@dataclass(slots=True)
class DstarApiTrdExchangeStateField(DstarField):
    """对应 C++ `DstarApiTrdExchangeStateField`：市场状态。"""

    CPP_NAME: ClassVar[str] = "DstarApiTrdExchangeStateField"
    ExchangeId: int = 0  # 交易所
    CommodityType: int = 0  # 品种类型
    CommodityNo: str = ""  # 品种号
    TradingState: int = 0  # 交易状态
    ExchangeTime: str = ""  # 交易所时间

@dataclass(slots=True)
class DstarApiTrdFeeParamField(DstarField):
    """对应 C++ `DstarApiTrdFeeParamField`：手续费参数。"""

    CPP_NAME: ClassVar[str] = "DstarApiTrdFeeParamField"
    AccountNo: str = ""  # 账号
    ContractNo: str = ""  # 合约编号
    OpenRatio: float = 0.0  # 开仓按比例
    OpenVolume: float = 0.0  # 开仓按手数
    CloseRatio: float = 0.0  # 平仓按比例
    CloseVolume: float = 0.0  # 平仓按手数
    CloseTRatio: float = 0.0  # 平今按比例
    CloseTVolume: float = 0.0  # 平今按手数

@dataclass(slots=True)
class DstarApiTrdMarParamField(DstarField):
    """对应 C++ `DstarApiTrdMarParamField`：保证金参数。"""

    CPP_NAME: ClassVar[str] = "DstarApiTrdMarParamField"
    AccountNo: str = ""  # 账号
    ContractNo: str = ""  # 合约编号
    BuySpeculateParam: float = 0.0  # 买投机参数
    BuyHedgeParam: float = 0.0  # 买套保参数
    SellSpeculateParam: float = 0.0  # 卖投机参数
    SellHedgeParam: float = 0.0  # 买套保参数

@dataclass(slots=True)
class DstarApiPosiProfitField(DstarField):
    """对应 C++ `DstarApiPosiProfitField`：浮盈通知。"""

    CPP_NAME: ClassVar[str] = "DstarApiPosiProfitField"
    AccountNo: str = ""  # 账号
    PosiProfit: float = 0.0  # 持仓盈亏
    SerialId: int = 0  # 流号

@dataclass(slots=True)
class DstarApiTradeRightField(DstarField):
    """对应 C++ `DstarApiTradeRightField`：交易权限。"""

    CPP_NAME: ClassVar[str] = "DstarApiTradeRightField"
    AccountNo: str = ""  # 账号
    ExchangeId: int = 0  # 交易所标识
    CommodityType: int = 0  # 品种类型
    CommodityNo: str = ""  # 品种
    BuyTradeRight: int = 0  # 买交易权限
    SellTradeRight: int = 0  # 卖交易权限

@dataclass(slots=True)
class DstarApiTradeRightDelField(DstarField):
    """对应 C++ `DstarApiTradeRightDelField`：交易权限删除。"""

    CPP_NAME: ClassVar[str] = "DstarApiTradeRightDelField"
    AccountNo: str = ""  # 账号
    ExchangeId: int = 0  # 交易所标识
    CommodityType: int = 0  # 品种类型
    CommodityNo: str = ""  # 品种

@dataclass(slots=True)
class DstarApiAccountCommListField(DstarField):
    """对应 C++ `DstarApiAccountCommListField`：客户品种白名单。"""

    CPP_NAME: ClassVar[str] = "DstarApiAccountCommListField"
    AccountNo: str = ""  # 账号
    ExchangeId: int = 0  # 交易所标识
    CommodityType: int = 0  # 品种类型
    CommodityNo: str = ""  # 品种

@dataclass(slots=True)
class DstarApiHead(DstarField):
    """对应 C++ `DstarApiHead`：UDP协议头。"""

    CPP_NAME: ClassVar[str] = "DstarApiHead"
    ProtocolCode: int = 0  # 协议号
    DataLen: int = 0  # 数据长度(不包含协议头)

@dataclass(slots=True)
class DstarApiReqUdpAuthField(DstarField):
    """对应 C++ `DstarApiReqUdpAuthField`：UDP认证请求。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqUdpAuthField"
    AccountIndex: int = 0  # 账号索引
    UdpAuthCode: int = 0  # udp认证码
    ReqIdMode: int = 0  # 请求号模式,不检查:不检查报单请求号;不强制模式:请求号不强制连续但要求增大;强制模式:请求号必须连续自增

@dataclass(slots=True)
class DstarApiReqOrderInsertField(DstarField):
    """对应 C++ `DstarApiReqOrderInsertField`：报单请求。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqOrderInsertField"
    Direct: int = 0  # 买卖方向
    Offset: int = 0  # 开平标志
    Hedge: int = 0  # 投机套保
    OrderType: int = 0  # 委托类型
    ValidType: int = 0  # 有效类型
    SeatIndex: int = 0  # 席位索引,0轮询席位,非0指定席位
    AccountIndex: int = 0  # 客户索引
    ContractIndex: int = 0  # 合约索引
    ContractNo: str = ""  # 合约编号
    OrderQty: int = 0  # 委托数量
    MinQty: int = 0  # 最小成交量
    OrderPrice: float = 0.0  # 委托价格
    ClientReqId: int = 0  # 客户请求号
    Reference: int = 0  # 报单引用(>=0,负数无效)
    UdpAuthCode: int = 0  # udp认证码

@dataclass(slots=True)
class DstarApiReqOfferInsertField(DstarField):
    """对应 C++ `DstarApiReqOfferInsertField`：报价请求。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqOfferInsertField"
    BuyOffset: int = 0  # 买开平标志
    SellOffset: int = 0  # 卖开平标志
    AccountIndex: int = 0  # 客户索引
    ClientReqId: int = 0  # 客户请求号
    ContractIndex: int = 0  # 合约索引
    ContractNo: str = ""  # 合约编号
    OrderQty: int = 0  # 报价数量
    BuyPrice: float = 0.0  # 买价
    SellPrice: float = 0.0  # 卖价
    SeatIndex: int = 0  # 席位索引
    EnquiryNo: str = ""  # 询价号
    Reference: int = 0  # 报单引用
    UdpAuthCode: int = 0  # udp认证码

@dataclass(slots=True)
class DstarApiReqOfferInsertNewField(DstarField):
    """对应 C++ `DstarApiReqOfferInsertNewField`：新报价请求。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqOfferInsertNewField"
    BuyOffset: int = 0  # 买开平标志
    SellOffset: int = 0  # 卖开平标志
    AccountIndex: int = 0  # 客户索引
    ClientReqId: int = 0  # 客户请求号
    ContractIndex: int = 0  # 合约索引
    ContractNo: str = ""  # 合约编号
    BuyOrderQty: int = 0  # 买报价量
    SellOrderQty: int = 0  # 卖报价量
    BuyPrice: float = 0.0  # 买价
    SellPrice: float = 0.0  # 卖价
    SeatIndex: int = 0  # 席位索引
    EnquiryNo: str = ""  # 询价号
    Reference: int = 0  # 报单引用
    UdpAuthCode: int = 0  # udp认证码
    ReplaceId: int = 0  # 定单委托号(中金所使用)

@dataclass(slots=True)
class DstarApiReqOrderDeleteField(DstarField):
    """对应 C++ `DstarApiReqOrderDeleteField`：撤单请求 (撤单失败时返回委托通知或报价通知,订单状态不变,包含撤单失败的错误码)。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqOrderDeleteField"
    AccountIndex: int = 0  # 客户索引
    ClientReqId: int = 0  # 客户请求号
    UdpAuthCode: int = 0  # udp认证码
    Reference: int = 0  # 报单引用(>=0,负数无效)
    SeatIndex: int = 0  # 席位索引,0从报单席位撤单,非0从指定席位撤单
    OrderId: int = 0  # 委托号
    SystemNo: str = ""  # 系统号

@dataclass(slots=True)
class DstarApiReqCmbOrderInsertField(DstarField):
    """对应 C++ `DstarApiReqCmbOrderInsertField`：组合报单请求。"""

    CPP_NAME: ClassVar[str] = "DstarApiReqCmbOrderInsertField"
    Direct: int = 0  # 买卖方向
    Offset: int = 0  # 开平标志
    Hedge: int = 0  # 投机套保
    OrderType: int = 0  # 委托类型
    ValidType: int = 0  # 有效类型
    SeatIndex: int = 0  # 席位索引
    AccountIndex: int = 0  # 客户索引
    ContractIndex1: int = 0  # 合约索引
    ContractNo1: str = ""  # 合约号
    ContractIndex2: int = 0  # 合约索引
    ContractNo2: str = ""  # 合约号
    OrderQty: int = 0  # 委托数量
    MinQty: int = 0  # 最小成交量
    OrderPrice: float = 0.0  # 委托价格
    ClientReqId: int = 0  # 客户请求号
    Reference: int = 0  # 报单引用
    UdpAuthCode: int = 0  # udp认证码

# C++ typedef aliases share the same layout and therefore the same Python model.
DstarApiRspOrderDeleteField = DstarApiRspOrderInsertField
DstarApiRspOfferInsertField = DstarApiRspOrderInsertField

STRUCT_MODELS: dict[str, type[DstarField]] = {
    "DstarApiReqLoginField": DstarApiReqLoginField,
    "DstarApiRspLoginField": DstarApiRspLoginField,
    "DstarApiSubmitInfoField": DstarApiSubmitInfoField,
    "DstarApiRspSubmitInfoField": DstarApiRspSubmitInfoField,
    "DstarApiInitQryInfoField": DstarApiInitQryInfoField,
    "DstarApiReqPwdModField": DstarApiReqPwdModField,
    "DstarApiRspPwdModField": DstarApiRspPwdModField,
    "DstarApiPwdModField": DstarApiPwdModField,
    "DstarApiRspUdpAuthField": DstarApiRspUdpAuthField,
    "DstarApiSeatField": DstarApiSeatField,
    "DstarApiContractField": DstarApiContractField,
    "DstarApiCmbContractField": DstarApiCmbContractField,
    "DstarApiOrderField": DstarApiOrderField,
    "DstarApiRspOrderInsertField": DstarApiRspOrderInsertField,
    "DstarApiOfferField": DstarApiOfferField,
    "DstarApiEnquiryField": DstarApiEnquiryField,
    "DstarApiMatchField": DstarApiMatchField,
    "DstarApiPrePositionField": DstarApiPrePositionField,
    "DstarApiPositionField": DstarApiPositionField,
    "DstarApiFundField": DstarApiFundField,
    "DstarApiCashInOutField": DstarApiCashInOutField,
    "DstaApiRspLastReqIdField": DstaApiRspLastReqIdField,
    "DstarApiTrdExchangeStateField": DstarApiTrdExchangeStateField,
    "DstarApiTrdFeeParamField": DstarApiTrdFeeParamField,
    "DstarApiTrdMarParamField": DstarApiTrdMarParamField,
    "DstarApiPosiProfitField": DstarApiPosiProfitField,
    "DstarApiTradeRightField": DstarApiTradeRightField,
    "DstarApiTradeRightDelField": DstarApiTradeRightDelField,
    "DstarApiAccountCommListField": DstarApiAccountCommListField,
    "DstarApiHead": DstarApiHead,
    "DstarApiReqUdpAuthField": DstarApiReqUdpAuthField,
    "DstarApiReqOrderInsertField": DstarApiReqOrderInsertField,
    "DstarApiReqOfferInsertField": DstarApiReqOfferInsertField,
    "DstarApiReqOfferInsertNewField": DstarApiReqOfferInsertNewField,
    "DstarApiReqOrderDeleteField": DstarApiReqOrderDeleteField,
    "DstarApiReqCmbOrderInsertField": DstarApiReqCmbOrderInsertField,
    "DstarApiRspOrderDeleteField": DstarApiRspOrderDeleteField,
    "DstarApiRspOfferInsertField": DstarApiRspOfferInsertField,
}

__all__ = [
    "DstarField",
    "STRUCT_MODELS",
    "DstarApiReqLoginField",
    "DstarApiRspLoginField",
    "DstarApiSubmitInfoField",
    "DstarApiRspSubmitInfoField",
    "DstarApiInitQryInfoField",
    "DstarApiReqPwdModField",
    "DstarApiRspPwdModField",
    "DstarApiPwdModField",
    "DstarApiRspUdpAuthField",
    "DstarApiSeatField",
    "DstarApiContractField",
    "DstarApiCmbContractField",
    "DstarApiOrderField",
    "DstarApiRspOrderInsertField",
    "DstarApiOfferField",
    "DstarApiEnquiryField",
    "DstarApiMatchField",
    "DstarApiPrePositionField",
    "DstarApiPositionField",
    "DstarApiFundField",
    "DstarApiCashInOutField",
    "DstaApiRspLastReqIdField",
    "DstarApiTrdExchangeStateField",
    "DstarApiTrdFeeParamField",
    "DstarApiTrdMarParamField",
    "DstarApiPosiProfitField",
    "DstarApiTradeRightField",
    "DstarApiTradeRightDelField",
    "DstarApiAccountCommListField",
    "DstarApiHead",
    "DstarApiReqUdpAuthField",
    "DstarApiReqOrderInsertField",
    "DstarApiReqOfferInsertField",
    "DstarApiReqOfferInsertNewField",
    "DstarApiReqOrderDeleteField",
    "DstarApiReqCmbOrderInsertField",
    "DstarApiRspOrderDeleteField",
    "DstarApiRspOfferInsertField",
]
