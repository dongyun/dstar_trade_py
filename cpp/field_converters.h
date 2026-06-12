#ifndef DSTAR_TRADE_PY_FIELD_CONVERTERS_H
#define DSTAR_TRADE_PY_FIELD_CONVERTERS_H

// pybind11 dictionary conversion declarations for all vendor field structures.
#include <pybind11/pybind11.h>

#include "DstarTradeApiError.h"
#include "DstarTradeApiStruct.h"

namespace dstar_trade_py {

namespace py = pybind11;

// Null field pointers consistently convert to an empty Python dictionary.
// Convert DstarApiReqLoginField (登录请求) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqLoginField* field);

// Convert DstarApiRspLoginField (登录应答) by immediately copying every field.
py::dict to_py_dict(const DstarApiRspLoginField* field);

// Convert DstarApiSubmitInfoField (上报信息) by immediately copying every field.
py::dict to_py_dict(const DstarApiSubmitInfoField* field);

// Convert DstarApiRspSubmitInfoField (上报信息应答) by immediately copying every field.
py::dict to_py_dict(const DstarApiRspSubmitInfoField* field);

// Convert DstarApiInitQryInfoField (初始化数据查询) by immediately copying every field.
py::dict to_py_dict(const DstarApiInitQryInfoField* field);

// Convert DstarApiReqPwdModField (密码修改请求) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqPwdModField* field);

// Convert DstarApiRspPwdModField (密码修改应答) by immediately copying every field.
py::dict to_py_dict(const DstarApiRspPwdModField* field);

// Convert DstarApiPwdModField (密码修改通知) by immediately copying every field.
py::dict to_py_dict(const DstarApiPwdModField* field);

// Convert DstarApiRspUdpAuthField (UDP认证应答) by immediately copying every field.
py::dict to_py_dict(const DstarApiRspUdpAuthField* field);

// Convert DstarApiSeatField (席位) by immediately copying every field.
py::dict to_py_dict(const DstarApiSeatField* field);

// Convert DstarApiContractField (合约数据) by immediately copying every field.
py::dict to_py_dict(const DstarApiContractField* field);

// Convert DstarApiCmbContractField (组合合约数据) by immediately copying every field.
py::dict to_py_dict(const DstarApiCmbContractField* field);

// Convert DstarApiOrderField (委托数据) by immediately copying every field.
py::dict to_py_dict(const DstarApiOrderField* field);

// Convert DstarApiRspOrderInsertField (报单应答) by immediately copying every field.
// DstarApiRspOrderDeleteField and DstarApiRspOfferInsertField are typedef aliases
// of this exact C++ type and therefore use the same overload.
py::dict to_py_dict(const DstarApiRspOrderInsertField* field);

// Convert DstarApiOfferField (报价通知) by immediately copying every field.
py::dict to_py_dict(const DstarApiOfferField* field);

// Convert DstarApiEnquiryField (询价通知) by immediately copying every field.
py::dict to_py_dict(const DstarApiEnquiryField* field);

// Convert DstarApiMatchField (成交数据) by immediately copying every field.
py::dict to_py_dict(const DstarApiMatchField* field);

// Convert DstarApiPrePositionField (昨持仓数据) by immediately copying every field.
py::dict to_py_dict(const DstarApiPrePositionField* field);

// Convert DstarApiPositionField (实时持仓) by immediately copying every field.
py::dict to_py_dict(const DstarApiPositionField* field);

// Convert DstarApiFundField (资金数据) by immediately copying every field.
py::dict to_py_dict(const DstarApiFundField* field);

// Convert DstarApiCashInOutField (出入金通知) by immediately copying every field.
py::dict to_py_dict(const DstarApiCashInOutField* field);

// Convert DstaApiRspLastReqIdField (最新请求号应答) by immediately copying every field.
py::dict to_py_dict(const DstaApiRspLastReqIdField* field);

// Convert DstarApiTrdExchangeStateField (市场状态) by immediately copying every field.
py::dict to_py_dict(const DstarApiTrdExchangeStateField* field);

// Convert DstarApiTrdFeeParamField (手续费参数) by immediately copying every field.
py::dict to_py_dict(const DstarApiTrdFeeParamField* field);

// Convert DstarApiTrdMarParamField (保证金参数) by immediately copying every field.
py::dict to_py_dict(const DstarApiTrdMarParamField* field);

// Convert DstarApiPosiProfitField (浮盈通知) by immediately copying every field.
py::dict to_py_dict(const DstarApiPosiProfitField* field);

// Convert DstarApiTradeRightField (交易权限) by immediately copying every field.
py::dict to_py_dict(const DstarApiTradeRightField* field);

// Convert DstarApiTradeRightDelField (交易权限删除) by immediately copying every field.
py::dict to_py_dict(const DstarApiTradeRightDelField* field);

// Convert DstarApiAccountCommListField (客户品种白名单) by immediately copying every field.
py::dict to_py_dict(const DstarApiAccountCommListField* field);

// Convert DstarApiHead (UDP协议头) by immediately copying every field.
py::dict to_py_dict(const DstarApiHead* field);

// Convert DstarApiReqUdpAuthField (UDP认证请求) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqUdpAuthField* field);

// Convert DstarApiReqOrderInsertField (报单请求) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqOrderInsertField* field);

// Convert DstarApiReqOfferInsertField (报价请求) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqOfferInsertField* field);

// Convert DstarApiReqOfferInsertNewField (新报价请求) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqOfferInsertNewField* field);

// Convert DstarApiReqOrderDeleteField (撤单请求 (撤单失败时返回委托通知或报价通知,订单状态不变,包含撤单失败的错误码)) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqOrderDeleteField* field);

// Convert DstarApiReqCmbOrderInsertField (组合报单请求) by immediately copying every field.
py::dict to_py_dict(const DstarApiReqCmbOrderInsertField* field);

// Convert a callback error code without exposing a pointer or borrowed storage.
py::dict to_py_error_dict(DstarApiErrorCodeType error_code);

// Convert callback boolean metadata, such as a future query bLast flag.
py::dict to_py_bool_dict(bool value);

}  // namespace dstar_trade_py

#endif  // DSTAR_TRADE_PY_FIELD_CONVERTERS_H
