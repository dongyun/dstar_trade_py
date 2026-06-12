# dstar_trade_py

`dstar_trade_py` is a Python SDK project for wrapping the Esunny Dstar V10 domestic trade API. The project currently contains only the package, build, test, and vendor-library skeleton; it does not yet implement trading operations.

## Platform Support

This project supports Linux x86-64 only and requires Python 3.10 or newer. Windows and macOS builds are intentionally rejected by CMake.

The official SDK headers and Linux shared library are stored without modification under:

```text
third_party/dstar/include/
third_party/dstar/lib/linux/libdstartradeapi.so
```

Use and redistribution of the vendor SDK remain subject to the vendor's license terms.

## Prerequisites

- Python 3.10 or newer
- A C++17 compiler such as `g++`
- CMake 3.18 or newer
- The vendor `libdstartradeapi.so`

Run the environment check before building:

```bash
export LD_LIBRARY_PATH="$PWD/third_party/dstar/lib/linux:${LD_LIBRARY_PATH:-}"
./scripts/check_env.sh
```

## Editable Build

Create a virtual environment and install the project with its test dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
```

The build uses scikit-build-core, CMake, and pybind11. The installed extension carries a relative runtime search path to its private copy of `libdstartradeapi.so`, so importing the installed package does not depend on a globally installed vendor library.

## Tests

```bash
python -m pytest
python examples/check_install.py
```

The current test is an import smoke test for the minimal native extension. No real account connection or trade request is performed.

## Documentation

The initial vendor SDK analysis is available in [`docs/sdk_analysis.md`](docs/sdk_analysis.md).

