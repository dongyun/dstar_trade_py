// Safe, immediate conversion of packed Dstar structures to owned Python values.
#include "field_converters.h"

#include <cstddef>
#include <type_traits>

namespace dstar_trade_py {
namespace {

// Decode a fixed C char array using a bounded NUL scan and UTF-8 replacement.
template <std::size_t Size>
py::object to_python_value(const char (&value)[Size]) {
    std::size_t length = 0;
    while (length < Size && value[length] != '\0') {
        ++length;
    }

    PyObject* decoded = PyUnicode_DecodeUTF8(value, static_cast<Py_ssize_t>(length), "replace");
    if (decoded == nullptr) {
        throw py::error_already_set();
    }
    return py::reinterpret_steal<py::str>(decoded);
}

// Preserve single-byte enum/status fields as their unsigned integer byte value.
py::object to_python_value(char value) {
    return py::int_(static_cast<unsigned int>(static_cast<unsigned char>(value)));
}

// Preserve unsigned byte fields as Python integers rather than one-character strings.
py::object to_python_value(unsigned char value) {
    return py::int_(static_cast<unsigned int>(value));
}

// Preserve signed byte fields as Python integers.
py::object to_python_value(signed char value) {
    return py::int_(static_cast<int>(value));
}

// Convert native bool values to real Python bool objects.
py::object to_python_value(bool value) {
    return py::bool_(value);
}

// Convert all remaining integral SDK values without narrowing them.
template <typename Value, std::enable_if_t<
    std::is_integral_v<Value> && !std::is_same_v<Value, bool> &&
    !std::is_same_v<Value, char> && !std::is_same_v<Value, signed char> &&
    !std::is_same_v<Value, unsigned char>, int> = 0>
py::object to_python_value(Value value) {
    return py::cast(value);
}

// Convert float and double SDK values to Python float objects.
template <typename Value, std::enable_if_t<std::is_floating_point_v<Value>, int> = 0>
py::object to_python_value(Value value) {
    return py::float_(value);
}

}  // namespace

// Convert DstarApiReqLoginField (登录请求); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqLoginField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["Password"] = to_python_value(field->Password);
    result["AppId"] = to_python_value(field->AppId);
    result["LicenseNo"] = to_python_value(field->LicenseNo);
    return result;
}

// Convert DstarApiRspLoginField (登录应答); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiRspLoginField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["AccountNo"] = to_python_value(field->AccountNo);
    result["TradeDate"] = to_python_value(field->TradeDate);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    result["ErrorCode"] = to_python_value(field->ErrorCode);
    result["StartTime"] = to_python_value(field->StartTime);
    result["StartMode"] = to_python_value(field->StartMode);
    result["FloatFlag"] = to_python_value(field->FloatFlag);
    return result;
}

// Convert DstarApiSubmitInfoField (上报信息); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiSubmitInfoField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["AuthType"] = to_python_value(field->AuthType);
    result["AuthKeyVersion"] = to_python_value(field->AuthKeyVersion);
    result["SystemInfo"] = to_python_value(field->SystemInfo);
    result["ClientLoginIp"] = to_python_value(field->ClientLoginIp);
    result["ClientLoginPort"] = to_python_value(field->ClientLoginPort);
    result["ClientLoginDateTime"] = to_python_value(field->ClientLoginDateTime);
    result["ClientAppId"] = to_python_value(field->ClientAppId);
    result["LicenseNo"] = to_python_value(field->LicenseNo);
    return result;
}

// Convert DstarApiRspSubmitInfoField (上报信息应答); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiRspSubmitInfoField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ErrorCode"] = to_python_value(field->ErrorCode);
    return result;
}

// Convert DstarApiInitQryInfoField (初始化数据查询); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiInitQryInfoField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["ContractInitQryFlag"] = to_python_value(field->ContractInitQryFlag);
    result["CmbContractInitQryFlag"] = to_python_value(field->CmbContractInitQryFlag);
    result["SeatInitQryFlag"] = to_python_value(field->SeatInitQryFlag);
    result["TrdFeeInitQryFlag"] = to_python_value(field->TrdFeeInitQryFlag);
    result["TrdMarInitQryFlag"] = to_python_value(field->TrdMarInitQryFlag);
    result["TrdRightInitQryFlag"] = to_python_value(field->TrdRightInitQryFlag);
    result["AccountCommListInitQryFlag"] = to_python_value(field->AccountCommListInitQryFlag);
    result["TrdExchangeStateInitQryFlag"] = to_python_value(field->TrdExchangeStateInitQryFlag);
    result["PrePositionInitQryFlag"] = to_python_value(field->PrePositionInitQryFlag);
    result["OrderInitQryFlag"] = to_python_value(field->OrderInitQryFlag);
    result["OfferInitQryFlag"] = to_python_value(field->OfferInitQryFlag);
    result["MatchInitQryFlag"] = to_python_value(field->MatchInitQryFlag);
    result["CashInOutInitQryFlag"] = to_python_value(field->CashInOutInitQryFlag);
    return result;
}

// Convert DstarApiReqPwdModField (密码修改请求); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqPwdModField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["Passwd"] = to_python_value(field->Passwd);
    result["OldPasswd"] = to_python_value(field->OldPasswd);
    return result;
}

// Convert DstarApiRspPwdModField (密码修改应答); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiRspPwdModField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ErrorCode"] = to_python_value(field->ErrorCode);
    return result;
}

// Convert DstarApiPwdModField (密码修改通知); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiPwdModField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    return result;
}

// Convert DstarApiRspUdpAuthField (UDP认证应答); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiRspUdpAuthField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    result["ReqIdMode"] = to_python_value(field->ReqIdMode);
    result["ErrorCode"] = to_python_value(field->ErrorCode);
    return result;
}

// Convert DstarApiSeatField (席位); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiSeatField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["SeatNo"] = to_python_value(field->SeatNo);
    result["Exchange"] = to_python_value(field->Exchange);
    result["SeatState"] = to_python_value(field->SeatState);
    result["Ip"] = to_python_value(field->Ip);
    return result;
}

// Convert DstarApiContractField (合约数据); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiContractField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["ExchangeId"] = to_python_value(field->ExchangeId);
    result["CommodityType"] = to_python_value(field->CommodityType);
    result["ContractIndex"] = to_python_value(field->ContractIndex);
    result["ContractSize"] = to_python_value(field->ContractSize);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["ContractTickSize"] = to_python_value(field->ContractTickSize);
    result["PreSettlePrice"] = to_python_value(field->PreSettlePrice);
    result["ExpDate"] = to_python_value(field->ExpDate);
    result["LimitUpPrice"] = to_python_value(field->LimitUpPrice);
    result["LimitDownPrice"] = to_python_value(field->LimitDownPrice);
    return result;
}

// Convert DstarApiCmbContractField (组合合约数据); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiCmbContractField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["ExchangeId"] = to_python_value(field->ExchangeId);
    result["CommodityType"] = to_python_value(field->CommodityType);
    result["ContractIndex1"] = to_python_value(field->ContractIndex1);
    result["ContractNo1"] = to_python_value(field->ContractNo1);
    result["ContractIndex2"] = to_python_value(field->ContractIndex2);
    result["ContractNo2"] = to_python_value(field->ContractNo2);
    return result;
}

// Convert DstarApiOrderField (委托数据); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiOrderField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["Direct"] = to_python_value(field->Direct);
    result["Offset"] = to_python_value(field->Offset);
    result["Hedge"] = to_python_value(field->Hedge);
    result["ValidType"] = to_python_value(field->ValidType);
    result["OrderPrice"] = to_python_value(field->OrderPrice);
    result["OrderQty"] = to_python_value(field->OrderQty);
    result["MinQty"] = to_python_value(field->MinQty);
    result["MatchQty"] = to_python_value(field->MatchQty);
    result["ErrCode"] = to_python_value(field->ErrCode);
    result["SerialId"] = to_python_value(field->SerialId);
    result["OrderId"] = to_python_value(field->OrderId);
    result["FrozenMargin"] = to_python_value(field->FrozenMargin);
    result["Margin"] = to_python_value(field->Margin);
    result["Fee"] = to_python_value(field->Fee);
    result["AccountNo"] = to_python_value(field->AccountNo);
    result["OrderLocalNo"] = to_python_value(field->OrderLocalNo);
    result["SystemNo"] = to_python_value(field->SystemNo);
    result["UpdateTime"] = to_python_value(field->UpdateTime);
    result["ExchInsertTime"] = to_python_value(field->ExchInsertTime);
    result["Reference"] = to_python_value(field->Reference);
    result["ContractNo1"] = to_python_value(field->ContractNo1);
    result["OrderType"] = to_python_value(field->OrderType);
    result["OrderState"] = to_python_value(field->OrderState);
    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["UpSeatNo"] = to_python_value(field->UpSeatNo);
    result["ContractNo2"] = to_python_value(field->ContractNo2);
    result["CmbId"] = to_python_value(field->CmbId);
    result["OrderFee"] = to_python_value(field->OrderFee);
    return result;
}

// Convert DstarApiRspOrderInsertField (报单应答); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiRspOrderInsertField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ClientReqId"] = to_python_value(field->ClientReqId);
    result["Reference"] = to_python_value(field->Reference);
    result["MaxClientReqId"] = to_python_value(field->MaxClientReqId);
    result["OrderId"] = to_python_value(field->OrderId);
    result["InsertTime"] = to_python_value(field->InsertTime);
    result["ErrCode"] = to_python_value(field->ErrCode);
    return result;
}

// Convert DstarApiOfferField (报价通知); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiOfferField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["BuyOffset"] = to_python_value(field->BuyOffset);
    result["SellOffset"] = to_python_value(field->SellOffset);
    result["OrderQty"] = to_python_value(field->OrderQty);
    result["BuyOrderQty"] = to_python_value(field->BuyOrderQty);
    result["BuyPrice"] = to_python_value(field->BuyPrice);
    result["SellPrice"] = to_python_value(field->SellPrice);
    result["BuyMatchQty"] = to_python_value(field->BuyMatchQty);
    result["SellMatchQty"] = to_python_value(field->SellMatchQty);
    result["AccountNo"] = to_python_value(field->AccountNo);
    result["OrderLocalNo"] = to_python_value(field->OrderLocalNo);
    result["SystemNo"] = to_python_value(field->SystemNo);
    result["EnquiryNo"] = to_python_value(field->EnquiryNo);
    result["UpdateTime"] = to_python_value(field->UpdateTime);
    result["ExchInsertTime"] = to_python_value(field->ExchInsertTime);
    result["FrozenMargin"] = to_python_value(field->FrozenMargin);
    result["Margin"] = to_python_value(field->Margin);
    result["SerialId"] = to_python_value(field->SerialId);
    result["OrderId"] = to_python_value(field->OrderId);
    result["ErrCode"] = to_python_value(field->ErrCode);
    result["OrderState"] = to_python_value(field->OrderState);
    result["Reference"] = to_python_value(field->Reference);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["UpSeatNo"] = to_python_value(field->UpSeatNo);
    result["SellOrderQty"] = to_python_value(field->SellOrderQty);
    return result;
}

// Convert DstarApiEnquiryField (询价通知); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiEnquiryField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["ContractNo"] = to_python_value(field->ContractNo);
    result["Direct"] = to_python_value(field->Direct);
    result["EnquiryNo"] = to_python_value(field->EnquiryNo);
    return result;
}

// Convert DstarApiMatchField (成交数据); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiMatchField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["ContractNo"] = to_python_value(field->ContractNo);
    result["MatchQty"] = to_python_value(field->MatchQty);
    result["MatchPrice"] = to_python_value(field->MatchPrice);
    result["Offset"] = to_python_value(field->Offset);
    result["Direct"] = to_python_value(field->Direct);
    result["Hedge"] = to_python_value(field->Hedge);
    result["OrderType"] = to_python_value(field->OrderType);
    result["Reference"] = to_python_value(field->Reference);
    result["SerialId"] = to_python_value(field->SerialId);
    result["OrderId"] = to_python_value(field->OrderId);
    result["MatchId"] = to_python_value(field->MatchId);
    result["MatchTime"] = to_python_value(field->MatchTime);
    result["ExchMatchNo"] = to_python_value(field->ExchMatchNo);
    result["SystemNo"] = to_python_value(field->SystemNo);
    result["Fee"] = to_python_value(field->Fee);
    result["Margin"] = to_python_value(field->Margin);
    result["FrozenMargin"] = to_python_value(field->FrozenMargin);
    result["Premium"] = to_python_value(field->Premium);
    result["CloseProfit"] = to_python_value(field->CloseProfit);
    result["AccountNo"] = to_python_value(field->AccountNo);
    result["UpdateTime"] = to_python_value(field->UpdateTime);
    result["CmbId"] = to_python_value(field->CmbId);
    result["OrderFee"] = to_python_value(field->OrderFee);
    return result;
}

// Convert DstarApiPrePositionField (昨持仓数据); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiPrePositionField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["PreBuyQty"] = to_python_value(field->PreBuyQty);
    result["PreBuyAvgPrice"] = to_python_value(field->PreBuyAvgPrice);
    result["PreSellQty"] = to_python_value(field->PreSellQty);
    result["PreSellAvgPrice"] = to_python_value(field->PreSellAvgPrice);
    return result;
}

// Convert DstarApiPositionField (实时持仓); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiPositionField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["PreBuyQty"] = to_python_value(field->PreBuyQty);
    result["TodayBuyQty"] = to_python_value(field->TodayBuyQty);
    result["BuyAvgPrice"] = to_python_value(field->BuyAvgPrice);
    result["PreSellQty"] = to_python_value(field->PreSellQty);
    result["TodaySellQty"] = to_python_value(field->TodaySellQty);
    result["SellAvgPrice"] = to_python_value(field->SellAvgPrice);
    result["SerialId"] = to_python_value(field->SerialId);
    return result;
}

// Convert DstarApiFundField (资金数据); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiFundField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["PreEquity"] = to_python_value(field->PreEquity);
    result["Equity"] = to_python_value(field->Equity);
    result["Avail"] = to_python_value(field->Avail);
    result["Fee"] = to_python_value(field->Fee);
    result["Margin"] = to_python_value(field->Margin);
    result["FrozenMargin"] = to_python_value(field->FrozenMargin);
    result["Premium"] = to_python_value(field->Premium);
    result["CloseProfit"] = to_python_value(field->CloseProfit);
    result["PositionProfit"] = to_python_value(field->PositionProfit);
    result["CashIn"] = to_python_value(field->CashIn);
    result["CashOut"] = to_python_value(field->CashOut);
    result["OrderFee"] = to_python_value(field->OrderFee);
    result["Frozen"] = to_python_value(field->Frozen);
    result["DeliveryFrozen"] = to_python_value(field->DeliveryFrozen);
    return result;
}

// Convert DstarApiCashInOutField (出入金通知); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiCashInOutField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["SerialId"] = to_python_value(field->SerialId);
    result["CashInOutType"] = to_python_value(field->CashInOutType);
    result["CashInOutMode"] = to_python_value(field->CashInOutMode);
    result["CashInOutValue"] = to_python_value(field->CashInOutValue);
    result["AccountNo"] = to_python_value(field->AccountNo);
    result["OperateTime"] = to_python_value(field->OperateTime);
    return result;
}

// Convert DstaApiRspLastReqIdField (最新请求号应答); no vendor pointer escapes this call.
py::dict to_py_dict(const DstaApiRspLastReqIdField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["LastClientReqId"] = to_python_value(field->LastClientReqId);
    return result;
}

// Convert DstarApiTrdExchangeStateField (市场状态); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiTrdExchangeStateField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["ExchangeId"] = to_python_value(field->ExchangeId);
    result["CommodityType"] = to_python_value(field->CommodityType);
    result["CommodityNo"] = to_python_value(field->CommodityNo);
    result["TradingState"] = to_python_value(field->TradingState);
    result["ExchangeTime"] = to_python_value(field->ExchangeTime);
    return result;
}

// Convert DstarApiTrdFeeParamField (手续费参数); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiTrdFeeParamField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["OpenRatio"] = to_python_value(field->OpenRatio);
    result["OpenVolume"] = to_python_value(field->OpenVolume);
    result["CloseRatio"] = to_python_value(field->CloseRatio);
    result["CloseVolume"] = to_python_value(field->CloseVolume);
    result["CloseTRatio"] = to_python_value(field->CloseTRatio);
    result["CloseTVolume"] = to_python_value(field->CloseTVolume);
    return result;
}

// Convert DstarApiTrdMarParamField (保证金参数); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiTrdMarParamField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["BuySpeculateParam"] = to_python_value(field->BuySpeculateParam);
    result["BuyHedgeParam"] = to_python_value(field->BuyHedgeParam);
    result["SellSpeculateParam"] = to_python_value(field->SellSpeculateParam);
    result["SellHedgeParam"] = to_python_value(field->SellHedgeParam);
    return result;
}

// Convert DstarApiPosiProfitField (浮盈通知); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiPosiProfitField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["PosiProfit"] = to_python_value(field->PosiProfit);
    result["SerialId"] = to_python_value(field->SerialId);
    return result;
}

// Convert DstarApiTradeRightField (交易权限); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiTradeRightField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ExchangeId"] = to_python_value(field->ExchangeId);
    result["CommodityType"] = to_python_value(field->CommodityType);
    result["CommodityNo"] = to_python_value(field->CommodityNo);
    result["BuyTradeRight"] = to_python_value(field->BuyTradeRight);
    result["SellTradeRight"] = to_python_value(field->SellTradeRight);
    return result;
}

// Convert DstarApiTradeRightDelField (交易权限删除); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiTradeRightDelField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ExchangeId"] = to_python_value(field->ExchangeId);
    result["CommodityType"] = to_python_value(field->CommodityType);
    result["CommodityNo"] = to_python_value(field->CommodityNo);
    return result;
}

// Convert DstarApiAccountCommListField (客户品种白名单); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiAccountCommListField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountNo"] = to_python_value(field->AccountNo);
    result["ExchangeId"] = to_python_value(field->ExchangeId);
    result["CommodityType"] = to_python_value(field->CommodityType);
    result["CommodityNo"] = to_python_value(field->CommodityNo);
    return result;
}

// Convert DstarApiHead (UDP协议头); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiHead* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["ProtocolCode"] = to_python_value(field->ProtocolCode);
    result["DataLen"] = to_python_value(field->DataLen);
    return result;
}

// Convert DstarApiReqUdpAuthField (UDP认证请求); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqUdpAuthField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    result["ReqIdMode"] = to_python_value(field->ReqIdMode);
    return result;
}

// Convert DstarApiReqOrderInsertField (报单请求); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqOrderInsertField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["Direct"] = to_python_value(field->Direct);
    result["Offset"] = to_python_value(field->Offset);
    result["Hedge"] = to_python_value(field->Hedge);
    result["OrderType"] = to_python_value(field->OrderType);
    result["ValidType"] = to_python_value(field->ValidType);
    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["ContractIndex"] = to_python_value(field->ContractIndex);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["OrderQty"] = to_python_value(field->OrderQty);
    result["MinQty"] = to_python_value(field->MinQty);
    result["OrderPrice"] = to_python_value(field->OrderPrice);
    result["ClientReqId"] = to_python_value(field->ClientReqId);
    result["Reference"] = to_python_value(field->Reference);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    return result;
}

// Convert DstarApiReqOfferInsertField (报价请求); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqOfferInsertField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["BuyOffset"] = to_python_value(field->BuyOffset);
    result["SellOffset"] = to_python_value(field->SellOffset);
    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["ClientReqId"] = to_python_value(field->ClientReqId);
    result["ContractIndex"] = to_python_value(field->ContractIndex);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["OrderQty"] = to_python_value(field->OrderQty);
    result["BuyPrice"] = to_python_value(field->BuyPrice);
    result["SellPrice"] = to_python_value(field->SellPrice);
    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["EnquiryNo"] = to_python_value(field->EnquiryNo);
    result["Reference"] = to_python_value(field->Reference);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    return result;
}

// Convert DstarApiReqOfferInsertNewField (新报价请求); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqOfferInsertNewField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["BuyOffset"] = to_python_value(field->BuyOffset);
    result["SellOffset"] = to_python_value(field->SellOffset);
    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["ClientReqId"] = to_python_value(field->ClientReqId);
    result["ContractIndex"] = to_python_value(field->ContractIndex);
    result["ContractNo"] = to_python_value(field->ContractNo);
    result["BuyOrderQty"] = to_python_value(field->BuyOrderQty);
    result["SellOrderQty"] = to_python_value(field->SellOrderQty);
    result["BuyPrice"] = to_python_value(field->BuyPrice);
    result["SellPrice"] = to_python_value(field->SellPrice);
    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["EnquiryNo"] = to_python_value(field->EnquiryNo);
    result["Reference"] = to_python_value(field->Reference);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    result["ReplaceId"] = to_python_value(field->ReplaceId);
    return result;
}

// Convert DstarApiReqOrderDeleteField (撤单请求 (撤单失败时返回委托通知或报价通知,订单状态不变,包含撤单失败的错误码)); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqOrderDeleteField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["ClientReqId"] = to_python_value(field->ClientReqId);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    result["Reference"] = to_python_value(field->Reference);
    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["OrderId"] = to_python_value(field->OrderId);
    result["SystemNo"] = to_python_value(field->SystemNo);
    return result;
}

// Convert DstarApiReqCmbOrderInsertField (组合报单请求); no vendor pointer escapes this call.
py::dict to_py_dict(const DstarApiReqCmbOrderInsertField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }

    result["Direct"] = to_python_value(field->Direct);
    result["Offset"] = to_python_value(field->Offset);
    result["Hedge"] = to_python_value(field->Hedge);
    result["OrderType"] = to_python_value(field->OrderType);
    result["ValidType"] = to_python_value(field->ValidType);
    result["SeatIndex"] = to_python_value(field->SeatIndex);
    result["AccountIndex"] = to_python_value(field->AccountIndex);
    result["ContractIndex1"] = to_python_value(field->ContractIndex1);
    result["ContractNo1"] = to_python_value(field->ContractNo1);
    result["ContractIndex2"] = to_python_value(field->ContractIndex2);
    result["ContractNo2"] = to_python_value(field->ContractNo2);
    result["OrderQty"] = to_python_value(field->OrderQty);
    result["MinQty"] = to_python_value(field->MinQty);
    result["OrderPrice"] = to_python_value(field->OrderPrice);
    result["ClientReqId"] = to_python_value(field->ClientReqId);
    result["Reference"] = to_python_value(field->Reference);
    result["UdpAuthCode"] = to_python_value(field->UdpAuthCode);
    return result;
}

// Convert the scalar OnRspError payload to the same owned-dictionary convention.
py::dict to_py_error_dict(DstarApiErrorCodeType error_code) {
    py::dict result;
    result["ErrorCode"] = to_python_value(error_code);
    return result;
}

// Convert bool callback metadata and preserve the Python bool type.
py::dict to_py_bool_dict(bool value) {
    py::dict result;
    result["Value"] = to_python_value(value);
    return result;
}

}  // namespace dstar_trade_py
