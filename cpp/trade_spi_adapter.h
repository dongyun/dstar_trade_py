#ifndef DSTAR_TRADE_PY_TRADE_SPI_ADAPTER_H
#define DSTAR_TRADE_PY_TRADE_SPI_ADAPTER_H

// Adapter from the vendor IDstarTradeSpi callback interface to a Python dispatcher.
#include <pybind11/pybind11.h>

#include "DstarTradeApi.h"

namespace dstar_trade_py {

namespace py = pybind11;

class PyTradeSpiAdapter final : public IDstarTradeSpi {
public:
    // The dispatcher must provide on_event(event_name: str, payload: dict).
    explicit PyTradeSpiAdapter(py::object dispatcher);
    ~PyTradeSpiAdapter() = default;

    PyTradeSpiAdapter(const PyTradeSpiAdapter&) = delete;
    PyTradeSpiAdapter& operator=(const PyTradeSpiAdapter&) = delete;
    PyTradeSpiAdapter(PyTradeSpiAdapter&&) = delete;
    PyTradeSpiAdapter& operator=(PyTradeSpiAdapter&&) = delete;

    void OnFrontDisconnected() override;
    void OnRspError(DstarApiErrorCodeType nErrorCode) override;
    void OnRspUserLogin(const DstarApiRspLoginField *pRspUserLogin) override;
    void OnRspPwdMod(const DstarApiRspPwdModField *pRspPwdModField) override;
    void OnRspSubmitInfo(const DstarApiRspSubmitInfoField *pRspSubmitInfo) override;
    void OnRspContract(const DstarApiContractField *pContract) override;
    void OnRspCmbContract(const DstarApiCmbContractField *pCmbContract) override;
    void OnRspSeat(const DstarApiSeatField* pSeat) override;
    void OnRspTrdFeeParam(const DstarApiTrdFeeParamField* pFeeParam) override;
    void OnRspTrdMarParam(const DstarApiTrdMarParamField* pMarParam) override;
    void OnRspTradeRight(const DstarApiTradeRightField* pTradeRight) override;
    void OnRspAccountCommList(const DstarApiAccountCommListField* pAccountCommList) override;
    void OnRspTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) override;
    void OnRspFund(const DstarApiFundField *pFund) override;
    void OnRspPrePosition(const DstarApiPrePositionField *pPrePosition) override;
    void OnRspPosition(const DstarApiPositionField *pPosition) override;
    void OnRspOrder(const DstarApiOrderField *pOrder) override;
    void OnRspOffer(const DstarApiOfferField *pOffer) override;
    void OnRspMatch(const DstarApiMatchField *pMatch) override;
    void OnRspCashInOut(const DstarApiCashInOutField *pCashInOut) override;
    void OnApiReady(const DstarApiSerialIdType nSerialId) override;
    void OnRspUdpAuth(const DstarApiRspUdpAuthField *pRspUdpAuth) override;
    void OnRspOrderInsert(const DstarApiRspOrderInsertField *pOrderInsert) override;
    void OnRspOfferInsert(const DstarApiRspOfferInsertField *pOfferInsert) override;
    void OnRspOrderDelete(const DstarApiRspOrderDeleteField *pOrderDelete) override;
    void OnRspLastReqId(const DstaApiRspLastReqIdField *pLastReqId) override;
    void OnRtnPwdMod(const DstarApiPwdModField *pPwdModField) override;
    void OnRtnOrder(const DstarApiOrderField *pOrder) override;
    void OnRtnMatch(const DstarApiMatchField *pMatch) override;
    void OnRtnCashInOut(const DstarApiCashInOutField *pCashInOut) override;
    void OnRtnOffer(const DstarApiOfferField *pOffer) override;
    void OnRtnEnquiry(const DstarApiEnquiryField *pEnquiry) override;
    void OnRtnTrdExchangeState(const DstarApiTrdExchangeStateField *pTrdExchangeState) override;
    void OnRtnPosiProfit(const DstarApiPosiProfitField *pPosiProfit) override;
    void OnRtnSeat(const DstarApiSeatField* pSeat) override;
    void OnRtnTradeRight(const DstarApiTradeRightField* pTradeRight) override;
    void OnRtnTradeRightDel(const DstarApiTradeRightDelField* pTradeRightDel) override;
    void OnRspQryPosition(const DstarApiPositionField *pPosition, bool bLast) override;
    void OnRspQryFund(const DstarApiFundField *pFund) override;

private:
    // Dispatch an already-copied payload dictionary to Python safely.
    void dispatch_event(const char* event_name, py::dict payload) noexcept;

    py::object dispatcher_;
};

}  // namespace dstar_trade_py

#endif  // DSTAR_TRADE_PY_TRADE_SPI_ADAPTER_H
