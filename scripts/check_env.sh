#!/usr/bin/env bash
# Validate the local Linux build environment before compiling the extension.

set -u

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
vendor_lib_dir="${project_root}/third_party/dstar/lib/linux"
vendor_lib="${vendor_lib_dir}/libdstartradeapi.so"
minimum_python="3.10"
failures=0
python_bin="python3"
cmake_bin="cmake"

pass() {
    printf '[OK] %s\n' "$1"
}

fail() {
    printf '[FAIL] %s\n' "$1" >&2
    failures=$((failures + 1))
}

warn() {
    printf '[WARN] %s\n' "$1" >&2
}

if [[ "$(uname -s)" == "Linux" ]]; then
    pass "Operating system is Linux"
else
    fail "dstar_trade_py supports Linux only"
fi

if [[ -x "${project_root}/.venv/bin/python" ]]; then
    python_bin="${project_root}/.venv/bin/python"
fi

if command -v "${python_bin}" >/dev/null 2>&1; then
    if "${python_bin}" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
        pass "Python $("${python_bin}" -c 'import platform; print(platform.python_version())') satisfies >= ${minimum_python}: ${python_bin}"
    else
        fail "Python >= ${minimum_python} is required"
    fi

    python_header="$("${python_bin}" -c 'import pathlib, sysconfig; print(pathlib.Path(sysconfig.get_paths()["include"]) / "Python.h")')"
    if [[ -f "${python_header}" ]]; then
        pass "Python development headers are available: ${python_header}"
    else
        fail "Python development headers are missing; install python3-dev"
    fi
else
    fail "${python_bin} was not found"
fi

if command -v g++ >/dev/null 2>&1; then
    pass "g++ is available: $(g++ --version | head -n 1)"
else
    fail "g++ was not found"
fi

if ! command -v "${cmake_bin}" >/dev/null 2>&1 && [[ -x "${project_root}/.venv/bin/cmake" ]]; then
    cmake_bin="${project_root}/.venv/bin/cmake"
fi

if command -v "${cmake_bin}" >/dev/null 2>&1; then
    pass "cmake is available: $("${cmake_bin}" --version | head -n 1)"
else
    fail "cmake was not found"
fi

if [[ -f "${vendor_lib}" ]]; then
    pass "Vendor library exists: ${vendor_lib}"
    if command -v ldd >/dev/null 2>&1; then
        if ldd "${vendor_lib}" | grep -q "not found"; then
            fail "Vendor library has unresolved shared-library dependencies"
            ldd "${vendor_lib}" >&2
        else
            pass "Vendor library dependencies are resolvable by ldd"
        fi
    else
        warn "ldd was not found; cannot inspect vendor library dependencies"
    fi
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

if command -v dmidecode >/dev/null 2>&1; then
    if dmidecode -s system-uuid >/dev/null 2>&1; then
        pass "dmidecode is available and readable for current user"
    else
        warn "dmidecode exists but may require root/sudo for system-info collection"
    fi
else
    warn "dmidecode was not found; GetSystemInfo may rely on other host identifiers"
fi

if command -v lshw >/dev/null 2>&1; then
    if lshw -quiet -class system >/dev/null 2>&1; then
        pass "lshw is available and readable for current user"
    else
        warn "lshw exists but may require root/sudo for complete hardware details"
    fi
else
    warn "lshw was not found; install it if vendor system-info collection needs it"
fi

if ((failures > 0)); then
    printf '\nEnvironment check failed with %d issue(s).\n' "${failures}" >&2
    exit 1
fi

printf '\nEnvironment check passed.\n'
