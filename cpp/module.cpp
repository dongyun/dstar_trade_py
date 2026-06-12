// Minimal pybind11 module used to validate the Linux C++ build toolchain.
#include <pybind11/pybind11.h>

#include "DstarTradeApi.h"

namespace py = pybind11;

PYBIND11_MODULE(_dstar_trade_py, module) {
    module.doc() = "Minimal native module for dstar_trade_py";
    module.attr("IS_LINUX_BUILD") = true;
    module.attr("SDK_PROTOCOL_VERSION") = DSTAR_API_PROTOCOL_VERSION;
}

