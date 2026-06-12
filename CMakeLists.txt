# Minimal CMake build for the pybind11 extension and vendor runtime library.
cmake_minimum_required(VERSION 3.18)
project(dstar_trade_py LANGUAGES CXX)

if(NOT CMAKE_SYSTEM_NAME STREQUAL "Linux")
    message(FATAL_ERROR "dstar_trade_py supports Linux only")
endif()

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

set(DSTAR_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/third_party/dstar")
set(DSTAR_INCLUDE_DIR "${DSTAR_ROOT}/include")
set(DSTAR_LIBRARY "${DSTAR_ROOT}/lib/linux/libdstartradeapi.so")

foreach(required_header
        DstarTradeApi.h
        DstarTradeApiDataType.h
        DstarTradeApiError.h
        DstarTradeApiStruct.h)
    if(NOT EXISTS "${DSTAR_INCLUDE_DIR}/${required_header}")
        message(FATAL_ERROR "Missing vendor header: ${DSTAR_INCLUDE_DIR}/${required_header}")
    endif()
endforeach()

if(NOT EXISTS "${DSTAR_LIBRARY}")
    message(FATAL_ERROR "Missing vendor library: ${DSTAR_LIBRARY}")
endif()

add_library(DstarTradeApi SHARED IMPORTED GLOBAL)
set_target_properties(DstarTradeApi PROPERTIES
    IMPORTED_LOCATION "${DSTAR_LIBRARY}"
    # The vendor library has no SONAME; avoid embedding its source path in DT_NEEDED.
    IMPORTED_NO_SONAME TRUE
)

pybind11_add_module(
    _dstar_trade_py
    MODULE
    cpp/binding.cpp
    cpp/field_converters.cpp
)
target_compile_features(_dstar_trade_py PRIVATE cxx_std_17)
target_include_directories(_dstar_trade_py PRIVATE "${DSTAR_INCLUDE_DIR}")
# Keep the linker configuration explicit for this Linux-only vendor library.
target_link_options(_dstar_trade_py PRIVATE "LINKER:--no-as-needed")
target_link_libraries(_dstar_trade_py PRIVATE DstarTradeApi)

# Keep the vendor library next to the installed extension in a private directory.
set_target_properties(_dstar_trade_py PROPERTIES
    INSTALL_RPATH "$ORIGIN/.libs"
    BUILD_WITH_INSTALL_RPATH TRUE
)

install(TARGETS _dstar_trade_py LIBRARY DESTINATION dstar_trade_py)
install(FILES "${DSTAR_LIBRARY}" DESTINATION dstar_trade_py/.libs)
