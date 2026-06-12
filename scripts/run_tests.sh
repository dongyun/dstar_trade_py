#!/usr/bin/env bash
# Run the dstar_trade_py test suite by category.

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${project_root}"

if [[ -x "${project_root}/.venv/bin/python" ]]; then
    python_bin="${project_root}/.venv/bin/python"
else
    python_bin="${PYTHON:-python3}"
fi

usage() {
    cat <<'USAGE'
Usage:
  ./scripts/run_tests.sh unit
  ./scripts/run_tests.sh integration
  ./scripts/run_tests.sh live
  ./scripts/run_tests.sh all

Notes:
  - unit and integration never connect to a real trading server.
  - live tests require DSTAR_RUN_LIVE_TESTS=1 and DSTAR_TRADE_* environment variables.
  - live order-safety tests do not submit real orders by default.
USAGE
}

if [[ $# -ne 1 ]]; then
    usage >&2
    exit 2
fi

case "$1" in
    unit)
        exec "${python_bin}" -m pytest -o addopts="-ra" -m unit tests
        ;;
    integration)
        exec "${python_bin}" -m pytest -o addopts="-ra" -m integration tests
        ;;
    live)
        exec "${python_bin}" -m pytest -o addopts="-ra" -m live tests/live
        ;;
    all)
        exec "${python_bin}" -m pytest -o addopts="-ra" -m "unit or integration or live" tests
        ;;
    *)
        usage >&2
        exit 2
        ;;
esac
