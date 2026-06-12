"""Tests for complete Dstar error-code coverage and exception selection."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dstar_trade_py.errors import (
    ERROR_MESSAGES,
    DstarAuthError,
    DstarConnectionError,
    DstarError,
    DstarErrorCode,
    DstarNativeError,
    DstarRequestError,
    DstarTimeoutError,
    get_error_message,
    raise_for_error,
)


def _declared_header_codes() -> set[int]:
    """Read every formally declared constant from the vendored source header."""

    project_root = Path(__file__).resolve().parents[2]
    header = project_root / "third_party/dstar/include/DstarTradeApiError.h"
    pattern = re.compile(
        r"^const DstarApiErrorCodeType\s+\w+\s*=\s*(\d+)\s*;",
        re.MULTILINE,
    )
    return {int(value) for value in pattern.findall(header.read_text(encoding="utf-8"))}


def test_all_declared_header_codes_are_mapped() -> None:
    """The Python map must neither omit nor invent declared vendor codes."""

    header_codes = _declared_header_codes()

    assert len(header_codes) == 78
    assert set(ERROR_MESSAGES) == header_codes
    assert {member.value for member in DstarErrorCode} == header_codes


@pytest.mark.parametrize(
    ("code", "message"),
    [
        (0, "Success"),
        (10001, "Not connected"),
        (20018, "Insufficient funds"),
        (30012, "Cancelling enquiry orders is not supported"),
        (60003, "Market quote is unavailable"),
    ],
)
def test_get_error_message_returns_readable_text(code: int, message: str) -> None:
    """Representative groups should expose stable English messages."""

    assert get_error_message(code) == message


def test_get_error_message_marks_unknown_code() -> None:
    """Undeclared and incomplete pass-through codes use the documented marker."""

    assert get_error_message(999999) == "Unknown Dstar error"
    assert get_error_message(-1) == "Unknown Dstar error"


def test_success_does_not_raise() -> None:
    """A zero result is accepted for any client action."""

    assert raise_for_error(0, action="ReqOrderInsert") is None


@pytest.mark.parametrize(
    ("code", "exception_type"),
    [
        (10001, DstarConnectionError),
        (10009, DstarTimeoutError),
        (20003, DstarAuthError),
        (20018, DstarRequestError),
        (10007, DstarNativeError),
    ],
)
def test_declared_errors_raise_typed_exceptions(
    code: int, exception_type: type[DstarError]
) -> None:
    """Declared code families should map to their public exception classes."""

    with pytest.raises(exception_type) as captured:
        raise_for_error(code, action="test action")

    assert captured.value.code == code
    assert captured.value.action == "test action"
    assert captured.value.message == get_error_message(code)


@pytest.mark.parametrize(
    ("code", "action", "exception_type", "message_fragment"),
    [
        (-1, "GetSystemInfo", DstarNativeError, "IP address"),
        (-5, "Init", DstarConnectionError, "connect"),
        (-3, "ReqLastClientReqId", DstarConnectionError, "disconnected"),
        (-2, "ReqOrderInsert", DstarConnectionError, "disconnected"),
        (-3, "ReqQryFund", DstarRequestError, "frequency"),
        (-4, "req_qry_position", DstarRequestError, "not completed"),
    ],
)
def test_active_request_return_codes_use_action_context(
    code: int,
    action: str,
    exception_type: type[DstarError],
    message_fragment: str,
) -> None:
    """Overlapping negative results are interpreted by native method name."""

    with pytest.raises(exception_type) as captured:
        raise_for_error(code, action=action)

    assert captured.value.code == code
    assert message_fragment.casefold() in captured.value.message.casefold()


def test_unknown_codes_preserve_original_integer() -> None:
    """Unknown exchange/native codes remain available for logs and diagnostics."""

    with pytest.raises(DstarRequestError) as positive:
        raise_for_error(987654, action="OnRspOrderInsert")
    with pytest.raises(DstarNativeError) as negative:
        raise_for_error(-99, action="FutureNativeCall")

    assert positive.value.code == 987654
    assert positive.value.message == "Unknown Dstar error"
    assert negative.value.code == -99
    assert negative.value.message == "Unknown Dstar error"

