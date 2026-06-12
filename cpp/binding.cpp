// Minimal pybind11 bindings for validating the vendor API lifecycle on Linux.
#include <memory>
#include <stdexcept>
#include <string>

#include <pybind11/pybind11.h>

#include "DstarTradeApi.h"

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
}

