// Minimal pybind11 bindings for validating the vendor API lifecycle on Linux.
#include <memory>
#include <cstring>
#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>

#include "DstarTradeApi.h"
#include "field_converters.h"

namespace py = pybind11;

namespace {

// Use the vendor release function for every successfully created API instance.
struct DstarApiDeleter {
    void operator()(IDstarTradeApi* api) const noexcept {
        if (api != nullptr) {
            FreeDstarTradeApi(api);
        }
    }
};

// The unique pointer guarantees release if version conversion raises an exception.
using DstarApiHandle = std::unique_ptr<IDstarTradeApi, DstarApiDeleter>;

// Create a temporary API instance, read its version, and release it before returning.
std::string get_api_version() {
    DstarApiHandle api(CreateDstarTradeApi());
    if (!api) {
        throw std::runtime_error(
            "CreateDstarTradeApi() returned null; verify the Linux vendor library and runtime environment"
        );
    }

    const char* version = api->GetApiVersion();
    if (version == nullptr || version[0] == '\0') {
        throw std::runtime_error("Dstar Trade API returned an empty version string");
    }

    return std::string(version);
}

// Exercise only the vendor factory and release functions without connecting to a server.
bool create_and_free_api() {
    DstarApiHandle api(CreateDstarTradeApi());
    return static_cast<bool>(api);
}

// Copy test text into a fixed vendor char array with guaranteed termination.
template <std::size_t Size>
void copy_test_text(char (&destination)[Size], const char* source) {
    static_assert(Size > 0, "Dstar character arrays must have positive capacity");
    std::strncpy(destination, source, Size - 1);
    destination[Size - 1] = '\0';
}

// Build representative packed structures on the stack and immediately copy them.
py::dict test_field_converter_samples() {
    DstarApiRspLoginField login{};
    login.AccountIndex = 7;
    copy_test_text(login.AccountNo, "demo-account");
    copy_test_text(login.TradeDate, "20260612");
    login.UdpAuthCode = 123456;
    login.ErrorCode = DSTAR_API_ERR_SUCCESS;
    login.StartTime = 90000;
    login.StartMode = DSTAR_API_STARTMODE_TRADE;
    login.FloatFlag = DSTAR_API_YES;

    DstarApiFundField fund{};
    copy_test_text(fund.AccountNo, "demo-account");
    fund.PreEquity = 100000.5;
    fund.Equity = 100250.75;
    fund.Avail = 80000.25;
    fund.Margin = 20000.5;
    fund.PositionProfit = 250.25;

    DstarApiPositionField position{};
    copy_test_text(position.AccountNo, "demo-account");
    copy_test_text(position.ContractNo, "GC2608");
    position.PreBuyQty = 1;
    position.TodayBuyQty = 2;
    position.BuyAvgPrice = 2410.5;
    position.SerialId = 987654321ULL;

    DstarApiOrderField order{};
    order.Direct = DSTAR_API_DIRECT_BUY;
    order.Offset = DSTAR_API_OFFSET_OPEN;
    order.Hedge = DSTAR_API_HEDGE_SPECULATE;
    order.ValidType = DSTAR_API_VALID_GFD;
    order.OrderPrice = 2412.5;
    order.OrderQty = 3;
    order.OrderId = 10001;
    copy_test_text(order.AccountNo, "demo-account");
    copy_test_text(order.ContractNo1, "GC2608");
    order.OrderType = DSTAR_API_ORDERTYPE_LIMIT;
    order.OrderState = DSTAR_API_STATUS_QUEUE;

    DstarApiMatchField match{};
    copy_test_text(match.ContractNo, "GC2608");
    match.MatchQty = 2;
    match.MatchPrice = 2411.25;
    match.Offset = DSTAR_API_OFFSET_OPEN;
    match.Direct = DSTAR_API_DIRECT_BUY;
    match.Hedge = DSTAR_API_HEDGE_SPECULATE;
    match.OrderType = DSTAR_API_ORDERTYPE_LIMIT;
    match.OrderId = 10001;
    match.MatchId = 20002;
    copy_test_text(match.AccountNo, "demo-account");

    // Invalid UTF-8 is intentional and verifies the replacement decoding policy.
    DstarApiReqLoginField invalid_utf8{};
    invalid_utf8.AccountNo[0] = 'A';
    invalid_utf8.AccountNo[1] = static_cast<char>(0xFF);
    invalid_utf8.AccountNo[2] = '\0';

    // A full array without NUL verifies that conversion never reads past capacity.
    DstarApiReqLoginField unterminated{};
    std::memset(unterminated.Password, 'x', sizeof(unterminated.Password));

    py::dict samples;
    samples["login"] = dstar_trade_py::to_py_dict(&login);
    samples["fund"] = dstar_trade_py::to_py_dict(&fund);
    samples["position"] = dstar_trade_py::to_py_dict(&position);
    samples["order"] = dstar_trade_py::to_py_dict(&order);
    samples["match"] = dstar_trade_py::to_py_dict(&match);
    samples["error"] = dstar_trade_py::to_py_error_dict(DSTAR_API_ERR_NOCONNECTION);
    samples["bool"] = dstar_trade_py::to_py_bool_dict(true);
    samples["null_login"] = dstar_trade_py::to_py_dict(
        static_cast<const DstarApiRspLoginField*>(nullptr)
    );
    samples["invalid_utf8"] = dstar_trade_py::to_py_dict(&invalid_utf8);
    samples["unterminated"] = dstar_trade_py::to_py_dict(&unterminated);
    return samples;
}

}  // namespace

// Register the minimal native surface used by the Linux load tests.
PYBIND11_MODULE(_dstar_trade_py, module) {
    module.doc() = "Minimal Linux bindings for validating the Dstar Trade API library";
    module.attr("IS_LINUX_BUILD") = true;
    module.attr("SDK_PROTOCOL_VERSION") = DSTAR_API_PROTOCOL_VERSION;

    module.def(
        "get_api_version",
        &get_api_version,
        "Create the vendor API, return its version string, and release the instance."
    );
    module.def(
        "create_and_free_api",
        &create_and_free_api,
        "Create and immediately release a vendor API instance."
    );
    module.def(
        "_test_field_converter_samples",
        &test_field_converter_samples,
        "Return owned dictionaries produced from representative stack fields."
    );
}
