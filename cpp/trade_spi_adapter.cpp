// IDstarTradeSpi implementation that copies vendor callbacks into Python dictionaries.
#include "trade_spi_adapter.h"

#include <iostream>
#include <string>
#include <utility>

#include "field_converters.h"

namespace dstar_trade_py {
namespace {

py::dict make_api_ready_payload(DstarApiSerialIdType serial_id) {
    py::dict payload;
    payload["serial_id"] = py::cast(serial_id);
    return payload;
}

py::dict make_error_payload(DstarApiErrorCodeType error_code) {
    py::dict payload;
    payload["error_code"] = py::cast(error_code);
    payload["ErrorCode"] = py::cast(error_code);
    payload["error_message"] = py::module_::import("dstar_trade_py.errors")
        .attr("get_error_message")(error_code);
    return payload;
}

py::dict make_query_position_payload(const DstarApiPositionField* position, bool last) {
    py::dict payload;
    payload["data"] = to_py_dict(position);
    payload["last"] = py::bool_(last);
    return payload;
}

}  // namespace

PyTradeSpiAdapter::PyTradeSpiAdapter(py::object dispatcher)
    : dispatcher_(std::move(dispatcher)) {}

void PyTradeSpiAdapter::dispatch_event(const char* event_name, const PayloadFactory& payload_factory) noexcept {
    try {
        // Vendor callbacks are invoked from SDK-owned C++ threads. Any interaction
        // with Python objects must hold the GIL; otherwise CPython object state can
        // be corrupted. Build the payload only after acquiring the GIL, so field
        // conversion and py::dict construction are both protected.
        py::gil_scoped_acquire gil;
        py::dict payload = payload_factory();
        dispatcher_.attr("on_event")(event_name, payload);
    } catch (const py::error_already_set& error) {
        PyErr_Clear();
        std::cerr << "dstar_trade_py callback error in " << event_name << ": "
                  << error.what() << std::endl;
    } catch (const std::exception& error) {
        std::cerr << "dstar_trade_py callback error in " << event_name << ": "
                  << error.what() << std::endl;
    } catch (...) {
        std::cerr << "dstar_trade_py callback error in " << event_name
                  << ": unknown exception" << std::endl;
    }
}

void PyTradeSpiAdapter::OnFrontDisconnected() {
    dispatch_event("front_disconnected", []() {
        return py::dict{};
    });
}

void PyTradeSpiAdapter::OnRspError(DstarApiErrorCodeType nErrorCode) {
    dispatch_event("rsp_error", [nErrorCode]() {
        return make_error_payload(nErrorCode);
    });
}

void PyTradeSpiAdapter::OnRspUserLogin(const DstarApiRspLoginField *pRspUserLogin) {
    dispatch_event("rsp_user_login", [pRspUserLogin]() {
        return to_py_dict(pRspUserLogin);
    });
}

void PyTradeSpiAdapter::OnRspPwdMod(const DstarApiRspPwdModField *pRspPwdModField) {
    dispatch_event("rsp_pwd_mod", [pRspPwdModField]() {
        return to_py_dict(pRspPwdModField);
    });
}

void PyTradeSpiAdapter::OnRspSubmitInfo(const DstarApiRspSubmitInfoField *pRspSubmitInfo) {
    dispatch_event("rsp_submit_info", [pRspSubmitInfo]() {
        return to_py_dict(pRspSubmitInfo);
    });
}

void PyTradeSpiAdapter::OnRspContract(const DstarApiContractField *pContract) {
    dispatch_event("rsp_contract", [pContract]() {
        return to_py_dict(pContract);
    });
}

void PyTradeSpiAdapter::OnRspCmbContract(const DstarApiCmbContractField *pCmbContract) {
    dispatch_event("rsp_cmb_contract", [pCmbContract]() {
        return to_py_dict(pCmbContract);
    });
}

void PyTradeSpiAdapter::OnRspSeat(const DstarApiSeatField* pSeat) {
    dispatch_event("rsp_seat", [pSeat]() {
        return to_py_dict(pSeat);
    });
}

void PyTradeSpiAdapter::OnRspTrdFeeParam(const DstarApiTrdFeeParamField* pFeeParam) {
    dispatch_event("rsp_trd_fee_param", [pFeeParam]() {
        return to_py_dict(pFeeParam);
    });
}

void PyTradeSpiAdapter::OnRspTrdMarParam(const DstarApiTrdMarParamField* pMarParam) {
    dispatch_event("rsp_trd_mar_param", [pMarParam]() {
        return to_py_dict(pMarParam);
    });
}

void PyTradeSpiAdapter::OnRspTradeRight(const DstarApiTradeRightField* pTradeRight) {
    dispatch_event("rsp_trade_right", [pTradeRight]() {
        return to_py_dict(pTradeRight);
    });
}

void PyTradeSpiAdapter::OnRspAccountCommList(const DstarApiAccountCommListField* pAccountCommList) {
    dispatch_event("rsp_account_comm_list", [pAccountCommList]() {
        return to_py_dict(pAccountCommList);
    });
}

void PyTradeSpiAdapter::OnRspTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) {
    dispatch_event("rsp_trd_exchange_state", [pTrdExchangeState]() {
        return to_py_dict(pTrdExchangeState);
    });
}

void PyTradeSpiAdapter::OnRspFund(const DstarApiFundField *pFund) {
    dispatch_event("rsp_fund", [pFund]() {
        return to_py_dict(pFund);
    });
}

void PyTradeSpiAdapter::OnRspPrePosition(const DstarApiPrePositionField *pPrePosition) {
    dispatch_event("rsp_pre_position", [pPrePosition]() {
        return to_py_dict(pPrePosition);
    });
}

void PyTradeSpiAdapter::OnRspPosition(const DstarApiPositionField *pPosition) {
    dispatch_event("rsp_position", [pPosition]() {
        return to_py_dict(pPosition);
    });
}

void PyTradeSpiAdapter::OnRspOrder(const DstarApiOrderField *pOrder) {
    dispatch_event("rsp_order", [pOrder]() {
        return to_py_dict(pOrder);
    });
}

void PyTradeSpiAdapter::OnRspOffer(const DstarApiOfferField *pOffer) {
    dispatch_event("rsp_offer", [pOffer]() {
        return to_py_dict(pOffer);
    });
}

void PyTradeSpiAdapter::OnRspMatch(const DstarApiMatchField *pMatch) {
    dispatch_event("rsp_match", [pMatch]() {
        return to_py_dict(pMatch);
    });
}

void PyTradeSpiAdapter::OnRspCashInOut(const DstarApiCashInOutField *pCashInOut) {
    dispatch_event("rsp_cash_in_out", [pCashInOut]() {
        return to_py_dict(pCashInOut);
    });
}

void PyTradeSpiAdapter::OnApiReady(const DstarApiSerialIdType nSerialId) {
    dispatch_event("api_ready", [nSerialId]() {
        return make_api_ready_payload(nSerialId);
    });
}

void PyTradeSpiAdapter::OnRspUdpAuth(const DstarApiRspUdpAuthField *pRspUdpAuth) {
    dispatch_event("rsp_udp_auth", [pRspUdpAuth]() {
        return to_py_dict(pRspUdpAuth);
    });
}

void PyTradeSpiAdapter::OnRspOrderInsert(const DstarApiRspOrderInsertField *pOrderInsert) {
    dispatch_event("rsp_order_insert", [pOrderInsert]() {
        return to_py_dict(pOrderInsert);
    });
}

void PyTradeSpiAdapter::OnRspOfferInsert(const DstarApiRspOfferInsertField *pOfferInsert) {
    dispatch_event("rsp_offer_insert", [pOfferInsert]() {
        return to_py_dict(pOfferInsert);
    });
}

void PyTradeSpiAdapter::OnRspOrderDelete(const DstarApiRspOrderDeleteField *pOrderDelete) {
    dispatch_event("rsp_order_delete", [pOrderDelete]() {
        return to_py_dict(pOrderDelete);
    });
}

void PyTradeSpiAdapter::OnRspLastReqId(const DstaApiRspLastReqIdField *pLastReqId) {
    dispatch_event("rsp_last_req_id", [pLastReqId]() {
        return to_py_dict(pLastReqId);
    });
}

void PyTradeSpiAdapter::OnRtnPwdMod(const DstarApiPwdModField *pPwdModField) {
    dispatch_event("rtn_pwd_mod", [pPwdModField]() {
        return to_py_dict(pPwdModField);
    });
}

void PyTradeSpiAdapter::OnRtnOrder(const DstarApiOrderField *pOrder) {
    dispatch_event("rtn_order", [pOrder]() {
        return to_py_dict(pOrder);
    });
}

void PyTradeSpiAdapter::OnRtnMatch(const DstarApiMatchField *pMatch) {
    dispatch_event("rtn_match", [pMatch]() {
        return to_py_dict(pMatch);
    });
}

void PyTradeSpiAdapter::OnRtnCashInOut(const DstarApiCashInOutField *pCashInOut) {
    dispatch_event("rtn_cash_in_out", [pCashInOut]() {
        return to_py_dict(pCashInOut);
    });
}

void PyTradeSpiAdapter::OnRtnOffer(const DstarApiOfferField *pOffer) {
    dispatch_event("rtn_offer", [pOffer]() {
        return to_py_dict(pOffer);
    });
}

void PyTradeSpiAdapter::OnRtnEnquiry(const DstarApiEnquiryField *pEnquiry) {
    dispatch_event("rtn_enquiry", [pEnquiry]() {
        return to_py_dict(pEnquiry);
    });
}

void PyTradeSpiAdapter::OnRtnTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) {
    dispatch_event("rtn_trd_exchange_state", [pTrdExchangeState]() {
        return to_py_dict(pTrdExchangeState);
    });
}

void PyTradeSpiAdapter::OnRtnPosiProfit(const DstarApiPosiProfitField *pPosiProfit) {
    dispatch_event("rtn_posi_profit", [pPosiProfit]() {
        return to_py_dict(pPosiProfit);
    });
}

void PyTradeSpiAdapter::OnRtnSeat(const DstarApiSeatField* pSeat) {
    dispatch_event("rtn_seat", [pSeat]() {
        return to_py_dict(pSeat);
    });
}

void PyTradeSpiAdapter::OnRtnTradeRight(const DstarApiTradeRightField* pTradeRight) {
    dispatch_event("rtn_trade_right", [pTradeRight]() {
        return to_py_dict(pTradeRight);
    });
}

void PyTradeSpiAdapter::OnRtnTradeRightDel(const DstarApiTradeRightDelField* pTradeRightDel) {
    dispatch_event("rtn_trade_right_del", [pTradeRightDel]() {
        return to_py_dict(pTradeRightDel);
    });
}

void PyTradeSpiAdapter::OnRspQryPosition(const DstarApiPositionField *pPosition, bool bLast) {
    dispatch_event("rsp_qry_position", [pPosition, bLast]() {
        return make_query_position_payload(pPosition, bLast);
    });
}

void PyTradeSpiAdapter::OnRspQryFund(const DstarApiFundField *pFund) {
    dispatch_event("rsp_qry_fund", [pFund]() {
        return to_py_dict(pFund);
    });
}

}  // namespace dstar_trade_py
