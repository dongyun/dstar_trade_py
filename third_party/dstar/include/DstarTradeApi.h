///@system  Dstar V10
///@file    DstarTradeApi.h
///@author  Hao Lin 2020-08-20


#ifndef DSTARTRADEAPI_H
#define DSTARTRADEAPI_H

#include "DstarTradeApiError.h"
#include "DstarTradeApiDataType.h"
#include "DstarTradeApiStruct.h"

#if defined WIN32 || defined _WIN32
#ifdef LIBDSTARTRADEAPI_EXPORTS
#define DSTARTRADEAPI_EXPORT __declspec(dllexport)
#else
#define DSTARTRADEAPI_EXPORT __declspec(dllimport)
#endif
#else
#define DSTARTRADEAPI_EXPORT
#endif

///@brief DstarTradeApi的回调基类
class IDstarTradeSpi
{
public:
    ///客户端与接口通信连接断开
    virtual void OnFrontDisconnected() = 0;

    ///错误应答
    virtual void OnRspError(DstarApiErrorCodeType nErrorCode) = 0;

    ///登录请求响应,错误码为0说明用户登录成功。
    virtual void OnRspUserLogin(const DstarApiRspLoginField *pRspUserLogin) = 0;
    
    // 密码修改应答
    virtual void OnRspPwdMod(const DstarApiRspPwdModField *pRspPwdModField) = 0;
    
    ///提交信息响应
    virtual void OnRspSubmitInfo(const DstarApiRspSubmitInfoField *pRspSubmitInfo) = 0;

    ///合约信息响应
    virtual void OnRspContract(const DstarApiContractField *pContract) = 0;

    ///组合合约信息响应
    virtual void OnRspCmbContract(const DstarApiCmbContractField *pCmbContract) = 0;

    ///席位信息响应
    virtual void OnRspSeat(const DstarApiSeatField* pSeat) = 0;

    ///手续费参数响应
    virtual void OnRspTrdFeeParam(const DstarApiTrdFeeParamField* pFeeParam) = 0;

    ///保证金参数响应
    virtual void OnRspTrdMarParam(const DstarApiTrdMarParamField* pMarParam) = 0;

    ///交易权限响应
    virtual void OnRspTradeRight(const DstarApiTradeRightField* pTradeRight) = 0;

    ///客户品种白名单响应
    virtual void OnRspAccountCommList(const DstarApiAccountCommListField* pAccountCommList) = 0;

    ///市场状态信息响应
    virtual void OnRspTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) = 0;
    
    ///资金快照响应
    virtual void OnRspFund(const DstarApiFundField *pFund) = 0;

    ///昨持仓快照响应
    virtual void OnRspPrePosition(const DstarApiPrePositionField *pPrePosition) = 0;
    
    ///实时持仓快照响应
    virtual void OnRspPosition(const DstarApiPositionField *pPosition) = 0;

    ///委托响应
    virtual void OnRspOrder(const DstarApiOrderField *pOrder) = 0;
    
    ///报价响应
    virtual void OnRspOffer(const DstarApiOfferField *pOffer) = 0;
    
    ///成交响应
    virtual void OnRspMatch(const DstarApiMatchField *pMatch) = 0;

    ///出入金响应
    virtual void OnRspCashInOut(const DstarApiCashInOutField *pCashInOut) = 0;
    
    ///API准备就绪,用户只有收到此就绪通知时才能进行后续的操作
    ///@param nSerialId 数据快照对应的流号,如果依据快照数据计算,使用该流号之后的数据
    virtual void OnApiReady(const DstarApiSerialIdType nSerialId) = 0;
    
    ///UDP认证请求响应,错误码为0说明认证成功。
    virtual void OnRspUdpAuth(const DstarApiRspUdpAuthField *pRspUdpAuth) = 0;
    
    ///报单应答
    virtual void OnRspOrderInsert(const DstarApiRspOrderInsertField *pOrderInsert) = 0;
    
    ///报价应答
    virtual void OnRspOfferInsert(const DstarApiRspOfferInsertField *pOfferInsert) = 0;
    
    ///撤单应答
    virtual void OnRspOrderDelete(const DstarApiRspOrderDeleteField *pOrderDelete) = 0;
    
    ///最新请求号应答
    virtual void OnRspLastReqId(const DstaApiRspLastReqIdField *pLastReqId) = 0;
    
    // 密码修改通知（收到此通知后API会主动断开连接）
    virtual void OnRtnPwdMod(const DstarApiPwdModField *pPwdModField) = 0;
    
    ///委托通知 (撤单失败时返回委托通知,委托状态不变,包含撤单失败的错误码)
    virtual void OnRtnOrder(const DstarApiOrderField *pOrder) = 0;

    ///成交通知
    virtual void OnRtnMatch(const DstarApiMatchField *pMatch) = 0;
    
    ///出入金通知
    virtual void OnRtnCashInOut(const DstarApiCashInOutField *pCashInOut) = 0;
    
    ///报价通知 (撤单失败时返回报价通知,报价状态不变,包含撤单失败的错误码)
    virtual void OnRtnOffer(const DstarApiOfferField *pOffer) = 0;
    
    ///询价通知
    virtual void OnRtnEnquiry(const DstarApiEnquiryField *pEnquiry) = 0;

    ///市场状态通知
    virtual void OnRtnTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) = 0;
    
    ///浮盈通知
    virtual void OnRtnPosiProfit(const DstarApiPosiProfitField *pPosiProfit) = 0;
    
    ///席位信息通知
    virtual void OnRtnSeat(const DstarApiSeatField* pSeat) = 0;

    ///交易权限通知 (当添加或者修改某个品种交易权限时，会推送此通知)
    virtual void OnRtnTradeRight(const DstarApiTradeRightField* pTradeRight) = 0;

    ///交易权限删除通知 (当删除某个品种交易权限时，会推送此通知)
    virtual void OnRtnTradeRightDel(const DstarApiTradeRightDelField* pTradeRightDel) = 0;

    ///实时持仓查询响应(当bLast为true时, pPosition有可能为NULL)
    virtual void OnRspQryPosition(const DstarApiPositionField *pPosition, bool bLast) = 0;

    ///资金查询响应
    virtual void OnRspQryFund(const DstarApiFundField *pFund) = 0;
    
};

///@brief DstarTradeApi开放函数接口
class DSTARTRADEAPI_EXPORT IDstarTradeApi {
public:
    ///注册回调接口
    ///@param pSpi 派生自回调接口类的实例
    virtual void RegisterSpi(IDstarTradeSpi *pSpi) = 0;

    ///注册接口地址
    ///@param pIp IP地址
    ///@param nPort 端口号
    virtual void RegisterFrontAddress(DstarApiIpType pIp, DstarApiPortType nPort) = 0;

    ///设置API保存交易数据目录和工作日志目录
    ///@param  pPath 目录。目录必须可用
    virtual void SetApiLogPath(DstarApiPathType pPath) = 0;

    ///设置用户信息
    ///@param pLoginInfo 用户信息
    virtual void SetLoginInfo(DstarApiReqLoginField *pLoginInfo) = 0;
    
    ///绑定CPU信息
    ///@param nRecvNoticeDataCpuId 绑定接收数据线程Cpu Id,可选。-1:不绑定
    ///@param nLogCpuId  绑定日志线程Cpu Id,可选。-1:不绑定,不记录交易数据日志,也不会开启日志线程
    virtual void SetCpuId(DstarApiCpuIdType nRecvNoticeDataCpuId, DstarApiCpuIdType nLogCpuId) = 0;
    
    ///设置通知流订阅位置
    ///@param nStartId 通知流订阅位置 -1:从最新开始订阅 0:从头订阅 >0:从指定位置订阅
    virtual void SetSubscribeStartId(DstarApiNoticeSubIdType nStartId) = 0;

    ///设置实时数据过滤器
    ///@param nFilter 过滤器标识 -1:过滤掉OnApiReady之后所有的实时数据(此时API工作线程将非满载运行, SetRunMode接口不生效) 0:不过滤任何实时数据(默认值)
    virtual void SetRealTimeDataFilter(DstarApiRealTimeDataFilterType nFilter) = 0;

    ///设置运行模式 默认满载模式
    ///@param nMode 运行模式 0:满载模式(默认值) -1:非满载模式(网卡加速启动此模式失效,将会满载运行)
    virtual void SetRunMode(DstarApiRunModeType nMode) = 0;
    
    ///采集系统信息
    ///@remark 该函数需要系统权限。
    ///Linux用户: 如果不使用root运行,需要单独设置权限(dmidecode/lshw; /sys/class/dmi/id/product_serial; /sys/devices/virtual/dmi/id/product_serial)
    ///@param pSystemInfo 接收系统信息,内存由客户申请
    ///@param nLen pSystemInfo的长度
    ///@param nAuthKeyVersion 返回密钥版本
    ///@return 错误码 0:成功,-1:获取Ip失败,-2:获取Mac失败,-3:获取设备名称失败,-4:获取操作系统版本失败,-5:获取硬盘序列号失败,
    ///                    -6:获取Cpu序列号失败,-7:获取Bios序列号失败,-8:获取系统分盘信息失败,-9:获取MacOS设备序列号失败
    virtual int GetSystemInfo(char* pSystemInfo, int *nLen, unsigned int *nAuthKeyVersion) = 0;
    
    ///设置上报信息
    ///@param pSubmitInfo 上报信息,包含系统信息和用户登录信息
    virtual void SetSubmitInfo(DstarApiSubmitInfoField *pSubmitInfo) = 0;

    ///设置初始化查询信息
    ///@param pInitQryInfo 初始化查询信息
    virtual void SetInitQryInfo(DstarApiInitQryInfoField *pInitQryInfo) = 0;
    
    ///初始化
    ///@remark 初始化运行环境,只有调用后,API才开始工作
    ///Linux用户: 如果不使用root运行,需要单独设置权限(dmidecode/lshw; /sys/class/dmi/id/product_serial; /sys/devices/virtual/dmi/id/product_serial)
    ///@return 错误码 0:成功,-3:连接已创建,-4:socket创建失败,-5:连接失败,
    /// 系统采集信息错误码 -11:获取Ip失败,-12:获取Mac失败,-13:获取设备名称失败,-14:获取操作系统版本失败,-15:获取硬盘序列号失败,
    ///                 -16:获取Cpu序列号失败,-17:获取Bios序列号失败,-18:获取系统分盘信息失败,-19:获取MacOS设备序列号失败
    virtual int Init() = 0;
    
    ///查询最新客户请求号
    ///@remark 可以用来检测报撤单丢包情况,查询间隔不小于5s
    ///@return 错误码 0:成功,-1:Api未就绪,-2:频率超限, -3:网络连接已断开
    virtual int ReqLastClientReqId() = 0;
    
    /// 密码修改请求
    /// \param pPwdModField 请求域
    /// \return  错误码 0:成功, -1:Api未就绪,-2:网络连接已断开
    virtual int ReqPwdMod(const DstarApiReqPwdModField *pReqPwdModField) = 0;
    
    ///报单请求
    ///@param pOrder 输入报单
    ///@return 错误码 0:成功,-1:Api未就绪,-2:网络连接已断开
    virtual int ReqOrderInsert(const DstarApiReqOrderInsertField *pOrder) = 0;
    
    ///报价请求
    ///@param pOffer 输入报价
    ///@return 错误码 0:成功,-1:Api未就绪,-2:网络连接已断开
    virtual int ReqOfferInsert(const DstarApiReqOfferInsertField *pOffer) = 0;

    ///新报价请求
    ///@param pOffer 输入报价
    ///@return 错误码 0:成功,-1:Api未就绪,-2:网络连接已断开
    virtual int ReqOfferInsertNew(const DstarApiReqOfferInsertNewField *pOffer) = 0;
    
    ///撤单请求
    ///@param pOrder 输入报单
    ///@return 错误码 0:成功,-1:Api未就绪,-2:网络连接已断开
    virtual int ReqOrderDelete(const DstarApiReqOrderDeleteField *pOrder) = 0;
    
    ///组合报单请求
    ///@param pCmbOrder 输入组合报单
    ///@return 错误码 0:成功,-1:Api未就绪,-2:网络连接已断开
    virtual int ReqCmbOrderInsert(const DstarApiReqCmbOrderInsertField *pCmbOrder) = 0;

    ///资金查询请求
    ///@return 错误码 0:成功,-1:Api未就绪,-2:网络连接已断开,-3:频率超限(最小间隔1s),-4:上次查询未结束
    virtual int ReqQryFund() = 0;

    ///持仓查询请求
    ///@return 错误码 0:成功,-1:Api未就绪,-2:网络连接已断开,-3:频率超限(最小间隔1s),-4:上次查询未结束
    virtual int ReqQryPosition() = 0;

    ///获取API的版本信息
    ///@retrun 获取到的版本号
    virtual const char *GetApiVersion() = 0;

};


extern "C" {

///创建Api实例 
///@return Api实例
DSTARTRADEAPI_EXPORT IDstarTradeApi *CreateDstarTradeApi();

///释放Api实例 
///@remark !!!不要在任何SPI回调中调用此函数
///@param pApiObj 需要释放的Api实例
DSTARTRADEAPI_EXPORT void FreeDstarTradeApi(IDstarTradeApi *pApiObj);

}


#endif // DSTARTRADEAPI_H
