#!/usr/bin/env bash
# Validate the local Linux build environment before compiling the extension.

set -u

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
vendor_lib_dir="${project_root}/third_party/dstar/lib/linux"
vendor_lib="${vendor_lib_dir}/libdstartradeapi.so"
minimum_python="3.10"
failures=0

pass() {
    printf '[OK] %s\n' "$1"
}

fail() {
    printf '[FAIL] %s\n' "$1" >&2
    failures=$((failures + 1))
}

if [[ "$(uname -s)" == "Linux" ]]; then
    pass "Operating system is Linux"
else
    fail "dstar_trade_py supports Linux only"
fi

if command -v python3 >/dev/null 2>&1; then
    if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
        pass "Python $(python3 -c 'import platform; print(platform.python_version())') satisfies >= ${minimum_python}"
    else
        fail "Python >= ${minimum_python} is required"
    fi
else
    fail "python3 was not found"
fi

if command -v g++ >/dev/null 2>&1; then
    pass "g++ is available: $(g++ --version | head -n 1)"
else
    fail "g++ was not found"
fi

if command -v cmake >/dev/null 2>&1; then
    pass "cmake is available: $(cmake --version | head -n 1)"
else
    fail "cmake was not found"
fi

if [[ -f "${vendor_lib}" ]]; then
    pass "Vendor library exists: ${vendor_lib}"
else
    fail "Vendor library is missing: ${vendor_lib}"
fi

ld_library_path="${LD_LIBRARY_PATH:-}"
case ":${ld_library_path}:" in
    *":${vendor_lib_dir}:"*)
        pass "LD_LIBRARY_PATH contains ${vendor_lib_dir}"
        ;;
    *)
        fail "LD_LIBRARY_PATH does not contain ${vendor_lib_dir}"
        ;;
esac

if ((failures > 0)); then
    printf '\nEnvironment check failed with %d issue(s).\n' "${failures}" >&2
    exit 1
fi

printf '\nEnvironment check passed.\n'

