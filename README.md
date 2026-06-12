# dstar_trade_py

`dstar_trade_py` is a Python SDK project for wrapping the Esunny Dstar V10 domestic trade API. The project provides Linux native bindings, generated Python field models, synchronous and asyncio client layers, and guarded live-test examples for the vendor test environment.

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

For a fuller Linux setup checklist, including `python3-dev`, `dmidecode`, `lshw`, and
system-info collection permissions, see [`docs/linux_setup.md`](docs/linux_setup.md).

## Editable Build

Create a virtual environment and install the project with its test dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
```

The build uses scikit-build-core, CMake, and pybind11. The installed extension carries a relative runtime search path to its private copy of `libdstartradeapi.so`, so importing the installed package does not depend on a globally installed vendor library.

Verify the native API lifecycle directly:

```bash
python -c 'import dstar_trade_py as d; print(d.get_api_version()); print(d.create_and_free_api())'
```

`get_api_version()` creates an API instance, reads `GetApiVersion()`, and releases the instance. `create_and_free_api()` only validates the factory and release functions. Neither function initializes a connection or contacts a real trading server.

## Tests

```bash
python -m pytest
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration
python examples/check_install.py
```

The pytest suite is split into three marker categories:

- `unit`: no real server and no real account; covers error codes, dataclasses, field conversion, event dispatch, state machines, and request validation.
- `integration`: may load `libdstartradeapi.so`, create/free API objects, and read the vendor API version; never connects to a trading server.
- `live`: connects to the Dstar test environment and requires real test credentials. These tests are skipped unless `DSTAR_RUN_LIVE_TESTS=1` is set.

Pytest defaults to `not live`, so this is safe for CI and local development:

```bash
python -m pytest
```

Run live tests only after configuring the environment described in [`docs/live_testing.md`](docs/live_testing.md):

```bash
export DSTAR_RUN_LIVE_TESTS=1
./scripts/run_tests.sh live
```

`./scripts/run_tests.sh all` includes live tests in the selection, but the live fixtures still skip unless `DSTAR_RUN_LIVE_TESTS=1` and all required `DSTAR_TRADE_*` variables are present. Live order-safety tests do not submit real orders by default.

If the dynamic loader cannot find the vendor library, package import raises an error explaining that `libdstartradeapi.so` must be installed under `dstar_trade_py/.libs` or made available through `LD_LIBRARY_PATH`.

## Documentation

The initial vendor SDK analysis is available in [`docs/sdk_analysis.md`](docs/sdk_analysis.md).
Security guidance for credentials, live-order confirmation, journal redaction, and
log redaction is available in [`docs/security.md`](docs/security.md).
