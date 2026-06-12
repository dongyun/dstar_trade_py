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

void PyTradeSpiAdapter::dispatch_event(const char* event_name, py::dict payload) noexcept {
    try {
        // Vendor callbacks are invoked from SDK-owned C++ threads. Any interaction
        // with Python objects must hold the GIL; otherwise CPython object state can
        // be corrupted. The payload was already copied into owned Python values, so
        // the vendor field pointer never escapes this callback frame.
        py::gil_scoped_acquire gil;
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
    dispatch_event("front_disconnected", py::dict{});
}

void PyTradeSpiAdapter::OnRspError(DstarApiErrorCodeType nErrorCode) {
    dispatch_event("rsp_error", make_error_payload(nErrorCode));
}

void PyTradeSpiAdapter::OnRspUserLogin(const DstarApiRspLoginField *pRspUserLogin) {
    dispatch_event("rsp_user_login", to_py_dict(pRspUserLogin));
}

void PyTradeSpiAdapter::OnRspPwdMod(const DstarApiRspPwdModField *pRspPwdModField) {
    dispatch_event("rsp_pwd_mod", to_py_dict(pRspPwdModField));
}

void PyTradeSpiAdapter::OnRspSubmitInfo(const DstarApiRspSubmitInfoField *pRspSubmitInfo) {
    dispatch_event("rsp_submit_info", to_py_dict(pRspSubmitInfo));
}

void PyTradeSpiAdapter::OnRspContract(const DstarApiContractField *pContract) {
    dispatch_event("rsp_contract", to_py_dict(pContract));
}

void PyTradeSpiAdapter::OnRspCmbContract(const DstarApiCmbContractField *pCmbContract) {
    dispatch_event("rsp_cmb_contract", to_py_dict(pCmbContract));
}

void PyTradeSpiAdapter::OnRspSeat(const DstarApiSeatField* pSeat) {
    dispatch_event("rsp_seat", to_py_dict(pSeat));
}

void PyTradeSpiAdapter::OnRspTrdFeeParam(const DstarApiTrdFeeParamField* pFeeParam) {
    dispatch_event("rsp_trd_fee_param", to_py_dict(pFeeParam));
}

void PyTradeSpiAdapter::OnRspTrdMarParam(const DstarApiTrdMarParamField* pMarParam) {
    dispatch_event("rsp_trd_mar_param", to_py_dict(pMarParam));
}

void PyTradeSpiAdapter::OnRspTradeRight(const DstarApiTradeRightField* pTradeRight) {
    dispatch_event("rsp_trade_right", to_py_dict(pTradeRight));
}

void PyTradeSpiAdapter::OnRspAccountCommList(const DstarApiAccountCommListField* pAccountCommList) {
    dispatch_event("rsp_account_comm_list", to_py_dict(pAccountCommList));
}

void PyTradeSpiAdapter::OnRspTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) {
    dispatch_event("rsp_trd_exchange_state", to_py_dict(pTrdExchangeState));
}

void PyTradeSpiAdapter::OnRspFund(const DstarApiFundField *pFund) {
    dispatch_event("rsp_fund", to_py_dict(pFund));
}

void PyTradeSpiAdapter::OnRspPrePosition(const DstarApiPrePositionField *pPrePosition) {
    dispatch_event("rsp_pre_position", to_py_dict(pPrePosition));
}

void PyTradeSpiAdapter::OnRspPosition(const DstarApiPositionField *pPosition) {
    dispatch_event("rsp_position", to_py_dict(pPosition));
}

void PyTradeSpiAdapter::OnRspOrder(const DstarApiOrderField *pOrder) {
    dispatch_event("rsp_order", to_py_dict(pOrder));
}

void PyTradeSpiAdapter::OnRspOffer(const DstarApiOfferField *pOffer) {
    dispatch_event("rsp_offer", to_py_dict(pOffer));
}

void PyTradeSpiAdapter::OnRspMatch(const DstarApiMatchField *pMatch) {
    dispatch_event("rsp_match", to_py_dict(pMatch));
}

void PyTradeSpiAdapter::OnRspCashInOut(const DstarApiCashInOutField *pCashInOut) {
    dispatch_event("rsp_cash_in_out", to_py_dict(pCashInOut));
}

void PyTradeSpiAdapter::OnApiReady(const DstarApiSerialIdType nSerialId) {
    dispatch_event("api_ready", make_api_ready_payload(nSerialId));
}

void PyTradeSpiAdapter::OnRspUdpAuth(const DstarApiRspUdpAuthField *pRspUdpAuth) {
    dispatch_event("rsp_udp_auth", to_py_dict(pRspUdpAuth));
}

void PyTradeSpiAdapter::OnRspOrderInsert(const DstarApiRspOrderInsertField *pOrderInsert) {
    dispatch_event("rsp_order_insert", to_py_dict(pOrderInsert));
}

void PyTradeSpiAdapter::OnRspOfferInsert(const DstarApiRspOfferInsertField *pOfferInsert) {
    dispatch_event("rsp_offer_insert", to_py_dict(pOfferInsert));
}

void PyTradeSpiAdapter::OnRspOrderDelete(const DstarApiRspOrderDeleteField *pOrderDelete) {
    dispatch_event("rsp_order_delete", to_py_dict(pOrderDelete));
}

void PyTradeSpiAdapter::OnRspLastReqId(const DstaApiRspLastReqIdField *pLastReqId) {
    dispatch_event("rsp_last_req_id", to_py_dict(pLastReqId));
}

void PyTradeSpiAdapter::OnRtnPwdMod(const DstarApiPwdModField *pPwdModField) {
    dispatch_event("rtn_pwd_mod", to_py_dict(pPwdModField));
}

void PyTradeSpiAdapter::OnRtnOrder(const DstarApiOrderField *pOrder) {
    dispatch_event("rtn_order", to_py_dict(pOrder));
}

void PyTradeSpiAdapter::OnRtnMatch(const DstarApiMatchField *pMatch) {
    dispatch_event("rtn_match", to_py_dict(pMatch));
}

void PyTradeSpiAdapter::OnRtnCashInOut(const DstarApiCashInOutField *pCashInOut) {
    dispatch_event("rtn_cash_in_out", to_py_dict(pCashInOut));
}

void PyTradeSpiAdapter::OnRtnOffer(const DstarApiOfferField *pOffer) {
    dispatch_event("rtn_offer", to_py_dict(pOffer));
}

void PyTradeSpiAdapter::OnRtnEnquiry(const DstarApiEnquiryField *pEnquiry) {
    dispatch_event("rtn_enquiry", to_py_dict(pEnquiry));
}

void PyTradeSpiAdapter::OnRtnTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) {
    dispatch_event("rtn_trd_exchange_state", to_py_dict(pTrdExchangeState));
}

void PyTradeSpiAdapter::OnRtnPosiProfit(const DstarApiPosiProfitField *pPosiProfit) {
    dispatch_event("rtn_posi_profit", to_py_dict(pPosiProfit));
}

void PyTradeSpiAdapter::OnRtnSeat(const DstarApiSeatField* pSeat) {
    dispatch_event("rtn_seat", to_py_dict(pSeat));
}

void PyTradeSpiAdapter::OnRtnTradeRight(const DstarApiTradeRightField* pTradeRight) {
    dispatch_event("rtn_trade_right", to_py_dict(pTradeRight));
}

void PyTradeSpiAdapter::OnRtnTradeRightDel(const DstarApiTradeRightDelField* pTradeRightDel) {
    dispatch_event("rtn_trade_right_del", to_py_dict(pTradeRightDel));
}

void PyTradeSpiAdapter::OnRspQryPosition(const DstarApiPositionField *pPosition, bool bLast) {
    dispatch_event("rsp_qry_position", make_query_position_payload(pPosition, bLast));
}

void PyTradeSpiAdapter::OnRspQryFund(const DstarApiFundField *pFund) {
    dispatch_event("rsp_qry_fund", to_py_dict(pFund));
}

}  // namespace dstar_trade_py
