///@system  Dstar V10
///@file    DstarTradeApiDataType.h
///@author  Hao Lin 2020-08-20


#ifndef DSTARTRADEAPIDATATYPE_H
#define DSTARTRADEAPIDATATYPE_H


//字符串类型
// 长度为10的字符串
typedef char                STR10[11];
// 长度为20的字符串
typedef char                STR20[21];
// 长度为30的字符串
typedef char                STR30[31];
// 长度为40的字符串
typedef char                STR40[41];
// 长度为50的字符串
typedef char                STR50[51];
// 长度为100的字符串
typedef char                STR100[101];
// 长度为200的字符串
typedef char                STR200[201];

typedef int                 RESULT;


// 协议版本号类型
typedef unsigned char       DstarApiVersionType;
const DstarApiVersionType   DSTAR_API_PROTOCOL_VERSION      = 3;

// 协议类型
typedef unsigned short      DstarApiProtocolCodeType;

// 数据长度
typedef unsigned short      DstarApiDataLen;

// 客户请求号
typedef unsigned int        DstarApiClientReqId;

// 报单引用, -1:无报单引用
typedef long long           DstarApiReferenceType;

// 描述符
typedef int                 DstarApiFdType;

// ip
typedef char                DstarApiIpType[41];

// ipv4
typedef char                DstarApiIPv4IpType[16];

// 端口
typedef unsigned short      DstarApiPortType;

// 日志路径
typedef char                DstarApiPathType[256];

// Cpu Id
typedef int                 DstarApiCpuIdType;

// 流号
typedef unsigned long long  DstarApiSerialIdType;

// 账号
typedef char                DstarApiAccountNoType[21];

// 合约索引
typedef unsigned int        DstarApiContractIndexType;

// 账号索引
typedef unsigned short      DstarApiAccountIndexType;

// 席位索引
typedef unsigned char       DstarApiSeatIndexType;

// 席位号
typedef char                DstarApiSeatNoType[21];

// 密码
typedef char                DstarApiPasswdType[65];

// 通知流订阅类型
typedef long long           DstarApiNoticeSubIdType;
// 从头订阅
const DstarApiNoticeSubIdType DSTAR_API_SUB_HEAD            = 0;
// 从最新订阅
const DstarApiNoticeSubIdType DSTAR_API_SUB_LAST            = -1;

// 实时数据过滤器
typedef int                 DstarApiRealTimeDataFilterType;
// 不过滤任何数据
const DstarApiRealTimeDataFilterType DSTAR_API_REAL_TIME_DATA_FILTER_NONE = 0;
// 过滤所有数据
const DstarApiRealTimeDataFilterType DSTAR_API_REAL_TIME_DATA_FILTER_IGNORE_ALL = -1;

// 运行模式
typedef int                 DstarApiRunModeType;
// 运行模式满载
const DstarApiRunModeType   DSTAR_API_RUN_MODE_TYPE_FULL_LOAD = 0;
// 运行模式非满载
const DstarApiRunModeType   DSTAR_API_RUN_MODE_TYPE_NON_FULL_LOAD = -1;

// 初始化类型
typedef char                DstarApiInitType;
// 初始化过程中查询基础数据
const DstarApiInitType      DSTAR_API_INIT_QUERY            = 0;
// 初始化过程中不查询基础数据
const DstarApiInitType      DSTAR_API_INIT_NOQUERY          = -1;

// UDP认证码
typedef unsigned int        DstarApiAuthCodeType;

// 请求类型
typedef unsigned char       DstarApiReqIdModeType;
// 不检测 对请求号不做检测
const DstarApiReqIdModeType DSTAR_API_REQIDMODE_NOCHECK     = 0;
// 增大 请求号要比上一笔请求大,否则报撤单无效
const DstarApiReqIdModeType DSTAR_API_REQIDMODE_INCREASE    = 1;
// 强制自增 要求请求号连续自增,否则报撤单无效
const DstarApiReqIdModeType DSTAR_API_REQIDMODE_FORCE       = 2;


// 交易编码
typedef char                DstarApiTradeNoType[9];

// 交易所
typedef char                DstarApiExchangeType;
const DstarApiExchangeType  DSTAR_API_EXCHANGE_ZCE          = 'Z';          // 郑商所
const DstarApiExchangeType  DSTAR_API_EXCHANGE_SHFE         = 'S';          // 上期所
const DstarApiExchangeType  DSTAR_API_EXCHANGE_INE          = 'I';          // 能源所
const DstarApiExchangeType  DSTAR_API_EXCHANGE_CFFEX        = 'C';          // 中金所
const DstarApiExchangeType  DSTAR_API_EXCHANGE_DCE          = 'D';          // 大商所
const DstarApiExchangeType  DSTAR_API_EXCHANGE_GFEX         = 'F';          // 广期所
const DstarApiExchangeType  DSTAR_API_EXCHANGE_SGE          = 'G';          // 金交所

// 品种
typedef char                DstarApiCommodityNoType[11];

// 品种类型
typedef char                DstarApiCommodityType;
const DstarApiCommodityType DSTAR_API_COMMTYPE_FUTURES      = 'F';          // 期货
const DstarApiCommodityType DSTAR_API_COMMTYPE_OPTION       = 'O';          // 期权
const DstarApiCommodityType DSTAR_API_COMMTYPE_SPD          = 'S';          // 跨期套利
const DstarApiCommodityType	DSTAR_API_COMMTYPE_IPS          = 'M';          // 跨品种套利
const DstarApiCommodityType	DSTAR_API_COMMTYPE_STD		    = 'D';          // 跨式套利
const DstarApiCommodityType	DSTAR_API_COMMTYPE_STG		    = 'G';          // 宽跨式套利
const DstarApiCommodityType	DSTAR_API_COMMTYPE_PRT			= 'R';          // 备兑
const DstarApiCommodityType DSTAR_API_COMMTYPE_NONE         = 'N';          // 无

// 合约
typedef char                DstarApiContractNoType[16];

// 合约乘数类型
typedef int                 DstarApiContractSizeType;

// 合约最小变动价位
typedef double              DstarApiContractTickSizeType;

// 买卖
typedef char                DstarApiDirectType;
const DstarApiDirectType    DSTAR_API_DIRECT_BUY            = 'B';          // 买方向
const DstarApiDirectType    DSTAR_API_DIRECT_SELL           = 'S';          // 卖方向
const DstarApiDirectType    DSTAR_API_DIRECT_ALL            = 'N';          // 所有

// 开平
typedef char                DstarApiOffsetType;
const DstarApiOffsetType    DSTAR_API_OFFSET_OPEN           = 'O';          // 开仓
const DstarApiOffsetType    DSTAR_API_OFFSET_CLOSE          = 'C';          // 平仓
const DstarApiOffsetType    DSTAR_API_OFFSET_CLOSETODAY     = 'T';          // 平今

// 投机套保
typedef char                DstarApiHedgeType;
const DstarApiHedgeType     DSTAR_API_HEDGE_SPECULATE       = 'T';          // 投机
const DstarApiHedgeType     DSTAR_API_HEDGE_HEDGE           = 'B';          // 套保

// 委托类型
typedef char                DstarApiOrderTypeType;
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_NONE        = '0';          // 空
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_MARKET      = '1';          // 市价单
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_LIMIT       = '2';          // 限价单
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_EXECUTE     = '3';          // 行权
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_ABANDON     = '4';          // 弃权
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_ENQUIRY     = '5';          // 询价
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_OFFER       = '6';          // 报价
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_SWAP        = '7';          // 互换
const DstarApiOrderTypeType DSTAR_API_ORDERTYPE_EFP         = '8';          // 期转现

// 交易权限
typedef char                 DstarApiTradeRightType;
const DstarApiTradeRightType DSTAR_API_TRADERIGHT_NORMAL    = '0';          // 正常交易
const DstarApiTradeRightType DSTAR_API_TRADERIGHT_NOTRADE   = '1';          // 禁止交易
const DstarApiTradeRightType DSTAR_API_TRADERIGHT_CLOSE     = '2';          // 只可平仓

// 系统号
typedef char                DstarApiSystemNoType[21];

// 交易所成交号
typedef char                DstarApiExchMatchNo[71];

// 日期类型 yyyymmdd
typedef char                DstarApiDateType[9];

// 委托号
typedef unsigned long long  DstarApiOrderIdType;

// 顶单号（中金所报价）
typedef unsigned long long  DstarApiReplaceIdType;
// 正常报价
const DstarApiReplaceIdType DSTAR_API_REPLACE_NORMAL        = 0;
// 顶最近一笔报价
const DstarApiReplaceIdType DSTAR_API_REPLACE_LAST          = 1;

// 成交ID
typedef unsigned long long  DstarApiMatchIdType;

// 本地号
typedef char                DstarApiOrderLocalNoType[21];

//价格类型
typedef double              DstarApiPriceType;

// 资金类型
typedef double              DstarApiFundType;

// 费率类型
typedef double              DstarApiParamType;

// 数量类型 U16
typedef unsigned short      DstarApiU16QuantityType;

// 数量类型
typedef unsigned int        DstarApiQuantityType;

// 成交时间 yyyymmddhhmmss
typedef char                DstarApiMatchTimeType[20];

// 日期时间 yyyy-mm-dd hh:mm:ss
typedef char                DstarApiDateTimeType[20];

// 有效类型
typedef char                DstarApiValidTypeType;
const DstarApiValidTypeType DSTAR_API_VALID_FOK             = '1';          //即时全部
const DstarApiValidTypeType DSTAR_API_VALID_IOC             = '2';          //即时部分
const DstarApiValidTypeType DSTAR_API_VALID_GFD             = '3';          //当日有效
const DstarApiValidTypeType DSTAR_API_VALID_GIS             = '4';          //小节有效

// 有效日期类型(yyyymmdd)
typedef unsigned int        DstarApiValidDateType;

// 委托状态
typedef char                DstarApiOrderStateType;

const DstarApiOrderStateType DSTAR_API_STATUS_ACCEPT        = '1';          // 已受理
const DstarApiOrderStateType DSTAR_API_STATUS_QUEUE         = '2';          // 已排队
const DstarApiOrderStateType DSTAR_API_STATUS_APPLY         = '3';          // 已申请(行权、弃权、套利等申请成功)
const DstarApiOrderStateType DSTAR_API_STATUS_SUSPENDED     = '4';          // 已挂起
const DstarApiOrderStateType DSTAR_API_STATUS_TRIGGERED     = '5';          // 已触发
const DstarApiOrderStateType DSTAR_API_STATUS_PARTFILL      = '6';          // 部分成交
const DstarApiOrderStateType DSTAR_API_STATUS_FILL          = '7';          // 完全成交
const DstarApiOrderStateType DSTAR_API_STATUS_FAIL          = '8';          // 指令失败
const DstarApiOrderStateType DSTAR_API_STATUS_DELETE        = 'B';          // 已撤单
const DstarApiOrderStateType DSTAR_API_STATUS_LEFTDELETE    = 'C';          // 已撤余单
const DstarApiOrderStateType DSTAR_API_STATUS_SYSDELETE     = 'D';          // 已删除
const DstarApiOrderStateType DSTAR_API_STATUS_TRIGGERING    = 'E';          // 策略待触发

// 出入金类型
typedef char                DstarApiCashInOutType;
// 入金
const DstarApiCashInOutType DSTAR_API_CASH_IN               = 'I';
// 出金
const DstarApiCashInOutType DSTAR_API_CASH_OUT              = 'O';

// 出入金方式
typedef char                DstarApiCashInOutModeType;
// 转账
const DstarApiCashInOutModeType DSTAR_API_CASHMODE_TRANSFER  = '1';
// 支票
const DstarApiCashInOutModeType DSTAR_API_CASHMODE_CHEQUE    = '2';
// 现金
const DstarApiCashInOutModeType DSTAR_API_CASHMODE_CASH      = '3';
// 换汇
const DstarApiCashInOutModeType DSTAR_API_CASHMODE_SWAP      = '4';
// 银期转账
const DstarApiCashInOutModeType DSTAR_API_CASHMODE_BFTRNSFER = '5';

// 交易状态
typedef char                DstarApiTradingStateType;
// 未知状态
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_UNKNOWN    = '0';
// 集合竞价
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_BID        = '1';
// 集合竞价撮合
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_MATCH      = '2';
// 连续交易
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_CONTINUOUS = '3';
// 交易暂停
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_PAUSED     = '4';
// 闭市
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_CLOSE      = '5';
// 闭市处理时间
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_DEALLAST   = '6';
// 正初始化
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_INITIALIZE = '7';
// 准备就绪
const DstarApiTradingStateType DSTAR_API_TRADE_STATE_READY      = '8';

// 软件授权类型
typedef char                DstarApiAuthTypeType;
// 不采集模式软件授权
const DstarApiAuthTypeType  DSTAR_API_AUTHTYPE_NOGATHER     = '0';
// 直连模式软件授权
const DstarApiAuthTypeType  DSTAR_API_AUTHTYPE_DIRECT       = '1';
// 中继模式软件授权
const DstarApiAuthTypeType  DSTAR_API_AUTHTYPE_RELAY        = '2';

// 采集信息密钥版本号
typedef unsigned int        DstarApiAuthKeyVersion;

// 系统采集信息
typedef char                DstarApiSystemInfoType[501];

// AppId类型
typedef char                DstarApiAppIdType[31];

// 软件授权号类型
typedef char                DstarApiLicenseNoType[51];

// 启动时间 hhmmss
typedef unsigned int        DstarApiStartTimeType;

// 启动模式
typedef unsigned char       DstarApiStartModeType;

// 对账
const DstarApiStartModeType    DSTAR_API_STARTMODE_CHECK    = 0;
// 交易
const DstarApiStartModeType    DSTAR_API_STARTMODE_TRADE    = 1;

// 席位状态
typedef char                   DstarApiSeatStateType;
// 断开
const DstarApiSeatStateType    DSTAR_API_SEATSTATE_DISCONNECT = 'D';
// 正常
const DstarApiSeatStateType    DSTAR_API_SEATSTATE_NORMAL     = 'N';

// 是否
typedef unsigned char          DstarApiYesNoType;
// 是
const DstarApiYesNoType        DSTAR_API_YES                  = 1;
// 否
const DstarApiYesNoType        DSTAR_API_NO                   = 0;


#endif // DSTARTRADEAPIDATATYPE_H
