"""Dstar error codes, readable messages, and typed Python exceptions.

The positive error codes in this module are a complete transcription of the
78 ``DstarApiErrorCodeType`` constants declared by the vendored
``DstarTradeApiError.h`` header. Negative return values are synchronous native
call results documented on ``GetSystemInfo``, ``Init``, and the ``Req*``
methods in ``DstarTradeApi.h``; their meaning depends on the action being
performed, so :func:`raise_for_error` uses its ``action`` argument to resolve
them.
"""

from __future__ import annotations

from enum import IntEnum
from types import MappingProxyType
from typing import Final, Mapping, TypeAlias


class DstarErrorCode(IntEnum):
    """All error-code constants formally declared by the vendor header."""

    SUCCESS = 0

    NOCONNECTION = 10001
    NOTLOGIN = 10002
    NOTREADY = 10003
    SUBSERIALID = 10004
    SEND = 10005
    RECV = 10006
    DATA_PROCESS = 10007
    BUFF_OVERFLOW = 10008
    HB_TIMEOUT = 10009

    AUTHSTRING = 20001
    NOACCOUNTNO = 20002
    PASSWORD = 20003
    LOGINCOUNT = 20004
    GWNOTCONN = 20005
    CONTRACTINDEX = 20006
    TCPLOGIN = 20007
    ACCOUNTINDEX = 20008
    UDPAUTHCODE = 20009
    NOAUTH = 20010
    ACCINDEX = 20011
    CONTRACTNO = 20012
    REQDATA = 20013
    CLIENTREQID = 20014
    ADDRESS = 20015
    AUTHCODE = 20016
    TRADERIGHT = 20017
    FUND = 20018
    PARENTFUND = 20019
    ORDERFREQUENCY = 20020
    AUTHVERSION = 20021
    SUBMITEMPTY = 20022
    NOLICENSE = 20023
    NOORDER = 20024
    SEATINDEX = 20025
    MAXCNT = 20026
    LICENSENO = 20027
    VERSION = 20028
    STATE = 20029
    ENOUGH = 20030
    POSITION = 20031
    TRADENO = 20032
    SEAT = 20033
    UNSUPPORTED = 20034
    SYSTEMNO = 20035
    NOCOMMODITY = 20036
    WHITELIST = 20037
    NOCONTRACT = 20038
    PRICE = 20039
    HWLOGIN = 20040
    MESSAGEAMOUNT = 20041
    OFFERQTY = 20042
    ORDERIDREPLACE = 20043
    SYSNOREPLACE = 20044
    SYSTEMTYPE = 20045
    UDPADDR = 20046
    SELFMATCH = 20047
    CASHINOUTVALUE = 20048
    CASHOUTMORE = 20049
    APPLICATIONNO = 20050
    ACCLICENSENO = 20051
    LICENSENODATE = 20052
    LOGINRIGHT = 20053

    SEATFREQUENCY = 30001
    SENDFAILED = 30002
    LOCAL_ENOUGH = 30003
    LOCALNO = 30004
    EXEC = 30005
    CANCEL_EXEC = 30006
    ABANDON = 30007
    CANCEL_ABANDON = 30008
    CMB = 30009
    INITING = 30010
    NOTHREAD = 30011
    CANCEL_ENQUIRY = 30012

    SLG_ORDERUNUSUAL = 60001
    SLG_INVALIDSORDER = 60002
    SLG_NOQUOTE = 60003


class DstarError(Exception):
    """Base exception carrying the original integer code and failed action."""

    def __init__(self, code: int, message: str, action: str = "") -> None:
        self.code = int(code)
        self.message = message
        self.action = action

        prefix = f"{action} failed" if action else "Dstar operation failed"
        super().__init__(f"{prefix} with error {self.code}: {self.message}")


class DstarNativeError(DstarError):
    """A local SDK, system-information, parsing, or buffer operation failed."""


class DstarConnectionError(DstarError):
    """The API cannot communicate with the front end or gateway."""


class DstarAuthError(DstarError):
    """Login, account, software-license, or UDP authentication failed."""


class DstarRequestError(DstarError):
    """A request was rejected because of its state, fields, or business rules."""


class DstarTimeoutError(DstarConnectionError):
    """A heartbeat or other documented Dstar timeout occurred."""


ExceptionType: TypeAlias = type[DstarError]
ErrorSpec: TypeAlias = tuple[str, ExceptionType]


# Messages deliberately preserve the meaning of every declared header comment.
# Corrected Python names are used for the three misspelled ``DSATR_*`` symbols,
# while their numeric values remain unchanged and therefore ABI-compatible.
_ERROR_SPECS: Final[dict[int, ErrorSpec]] = {
    0: ("Success", DstarError),
    10001: ("Not connected", DstarConnectionError),
    10002: ("Not logged in", DstarAuthError),
    10003: ("API is not ready", DstarRequestError),
    10004: ("Invalid subscription serial ID", DstarRequestError),
    10005: ("Failed to send data", DstarConnectionError),
    10006: ("Failed to receive data", DstarConnectionError),
    10007: ("Failed to parse data", DstarNativeError),
    10008: ("Buffer overflow", DstarNativeError),
    10009: ("Heartbeat timeout", DstarTimeoutError),
    20001: ("Invalid authentication string", DstarAuthError),
    20002: ("Account does not exist", DstarAuthError),
    20003: ("Incorrect password", DstarAuthError),
    20004: ("Login count limit exceeded", DstarAuthError),
    20005: ("Gateway is not connected", DstarConnectionError),
    20006: ("Invalid contract index", DstarRequestError),
    20007: ("TCP authentication has not completed", DstarAuthError),
    20008: ("Invalid account index", DstarAuthError),
    20009: ("Invalid UDP authentication code", DstarAuthError),
    20010: ("UDP authentication has not completed", DstarAuthError),
    20011: ("Order account differs from authenticated account", DstarAuthError),
    20012: ("Contract index and contract number do not match", DstarRequestError),
    20013: ("Invalid order request fields", DstarRequestError),
    20014: ("Invalid client request ID", DstarRequestError),
    20015: ("Invalid order or cancellation address", DstarRequestError),
    20016: ("Invalid order or cancellation authentication code", DstarAuthError),
    20017: ("Trading permission denied", DstarRequestError),
    20018: ("Insufficient funds", DstarRequestError),
    20019: ("Parent account has insufficient funds", DstarRequestError),
    20020: ("Account order frequency limit exceeded", DstarRequestError),
    20021: ("Invalid authentication key version", DstarAuthError),
    20022: ("Submitted system information is empty", DstarAuthError),
    20023: ("Software license does not exist", DstarAuthError),
    20024: ("Original order was not found for cancellation", DstarRequestError),
    20025: ("Invalid seat index", DstarRequestError),
    20026: ("Batch quantity exceeds the per-request maximum", DstarRequestError),
    20027: ("Invalid software license number", DstarAuthError),
    20028: ("Protocol version mismatch", DstarNativeError),
    20029: ("Order state does not allow cancellation", DstarRequestError),
    20030: ("Order capacity is exhausted", DstarRequestError),
    20031: ("Insufficient position to close", DstarRequestError),
    20032: ("Trading code does not exist", DstarRequestError),
    20033: ("Seat is unavailable or invalid", DstarRequestError),
    20034: ("Unsupported order", DstarRequestError),
    20035: ("Invalid system number", DstarRequestError),
    20036: ("Commodity does not exist", DstarRequestError),
    20037: ("Commodity is not on the account whitelist", DstarRequestError),
    20038: ("Contract does not exist", DstarRequestError),
    20039: ("Invalid price", DstarRequestError),
    20040: ("Failed to set hardware login information", DstarAuthError),
    20041: ("Message volume limit exceeded", DstarRequestError),
    20042: ("Bid and ask quantities are inconsistent", DstarRequestError),
    20043: ("Replacement order ID does not exist", DstarRequestError),
    20044: ("Replacement system number does not exist", DstarRequestError),
    20045: ("Backup trading system is not active", DstarConnectionError),
    20046: ("Invalid UDP packet address", DstarConnectionError),
    20047: ("Order may self-match", DstarRequestError),
    20048: ("Invalid cash transfer amount", DstarRequestError),
    20049: ("Withdrawal amount exceeds available funds", DstarRequestError),
    20050: ("Invalid application number", DstarAuthError),
    20051: ("Account is not authorized for this software license", DstarAuthError),
    20052: ("Software license has expired", DstarAuthError),
    20053: ("Login is prohibited", DstarAuthError),
    30001: ("Seat order frequency limit exceeded", DstarRequestError),
    30002: ("Send operation failed", DstarConnectionError),
    30003: ("Local order number capacity is exhausted", DstarRequestError),
    30004: ("Invalid local order number", DstarRequestError),
    30005: ("Exercise orders are not supported", DstarRequestError),
    30006: ("Cancelling exercise orders is not supported", DstarRequestError),
    30007: ("Abandonment orders are not supported", DstarRequestError),
    30008: ("Cancelling abandonment orders is not supported", DstarRequestError),
    30009: ("Combination orders are not supported", DstarRequestError),
    30010: ("Trading system is initializing", DstarRequestError),
    30011: ("Data was received on an unexpected thread", DstarNativeError),
    30012: ("Cancelling enquiry orders is not supported", DstarRequestError),
    60001: ("Strategy order submission failed", DstarRequestError),
    60002: ("Invalid strategy order", DstarRequestError),
    60003: ("Market quote is unavailable", DstarRequestError),
}


# Expose a read-only mapping for diagnostics and coverage checks without
# allowing callers to mutate the SDK's canonical messages.
ERROR_MESSAGES: Final[Mapping[int, str]] = MappingProxyType(
    {code: message for code, (message, _) in _ERROR_SPECS.items()}
)

_UNKNOWN_MESSAGE: Final = "Unknown Dstar error"


# Synchronous return codes overlap numerically, so each native method has an
# explicit action table. Future client methods should pass the vendor method
# name to ``raise_for_error`` immediately after every integer-returning call.
_GET_SYSTEM_INFO_ERRORS: Final[dict[int, ErrorSpec]] = {
    -1: ("Failed to obtain an IP address", DstarNativeError),
    -2: ("Failed to obtain a MAC address", DstarNativeError),
    -3: ("Failed to obtain the device name", DstarNativeError),
    -4: ("Failed to obtain the operating system version", DstarNativeError),
    -5: ("Failed to obtain the disk serial number", DstarNativeError),
    -6: ("Failed to obtain the CPU serial number", DstarNativeError),
    -7: ("Failed to obtain the BIOS serial number", DstarNativeError),
    -8: ("Failed to obtain disk partition information", DstarNativeError),
    -9: ("Failed to obtain the device serial number", DstarNativeError),
}

_INIT_ERRORS: Final[dict[int, ErrorSpec]] = {
    -3: ("Connection has already been created", DstarConnectionError),
    -4: ("Failed to create the socket", DstarConnectionError),
    -5: ("Failed to connect to the front end", DstarConnectionError),
    -11: ("Failed to obtain an IP address", DstarNativeError),
    -12: ("Failed to obtain a MAC address", DstarNativeError),
    -13: ("Failed to obtain the device name", DstarNativeError),
    -14: ("Failed to obtain the operating system version", DstarNativeError),
    -15: ("Failed to obtain the disk serial number", DstarNativeError),
    -16: ("Failed to obtain the CPU serial number", DstarNativeError),
    -17: ("Failed to obtain the BIOS serial number", DstarNativeError),
    -18: ("Failed to obtain disk partition information", DstarNativeError),
    -19: ("Failed to obtain the device serial number", DstarNativeError),
}

_STANDARD_REQUEST_ERRORS: Final[dict[int, ErrorSpec]] = {
    -1: ("API is not ready", DstarRequestError),
    -2: ("Network connection is disconnected", DstarConnectionError),
}

_LAST_REQUEST_ID_ERRORS: Final[dict[int, ErrorSpec]] = {
    -1: ("API is not ready", DstarRequestError),
    -2: ("Request frequency limit exceeded", DstarRequestError),
    -3: ("Network connection is disconnected", DstarConnectionError),
}

_QUERY_ERRORS: Final[dict[int, ErrorSpec]] = {
    -1: ("API is not ready", DstarRequestError),
    -2: ("Network connection is disconnected", DstarConnectionError),
    -3: ("Query frequency limit exceeded", DstarRequestError),
    -4: ("Previous query has not completed", DstarRequestError),
}


def _normalize_action(action: str) -> str:
    """Normalize C++ and Python method spellings for action-specific lookup."""

    return "".join(character for character in action.casefold() if character.isalnum())


_ACTION_ERRORS: Final[dict[str, Mapping[int, ErrorSpec]]] = {
    "getsysteminfo": _GET_SYSTEM_INFO_ERRORS,
    "init": _INIT_ERRORS,
    "reqlastclientreqid": _LAST_REQUEST_ID_ERRORS,
    "reqpwdmod": _STANDARD_REQUEST_ERRORS,
    "reqorderinsert": _STANDARD_REQUEST_ERRORS,
    "reqofferinsert": _STANDARD_REQUEST_ERRORS,
    "reqofferinsertnew": _STANDARD_REQUEST_ERRORS,
    "reqorderdelete": _STANDARD_REQUEST_ERRORS,
    "reqcmborderinsert": _STANDARD_REQUEST_ERRORS,
    "reqqryfund": _QUERY_ERRORS,
    "reqqryposition": _QUERY_ERRORS,
}


def get_error_message(code: int) -> str:
    """Return the declared message for *code* or a stable unknown marker.

    Negative synchronous return values require an action to disambiguate and
    are therefore resolved by :func:`raise_for_error`. Calling this function
    directly for a negative or undeclared exchange code returns the required
    ``Unknown Dstar error`` marker while preserving the integer at the caller.
    """

    spec = _ERROR_SPECS.get(int(code))
    return spec[0] if spec is not None else _UNKNOWN_MESSAGE


def raise_for_error(code: int, action: str = "") -> None:
    """Raise the typed exception corresponding to a Dstar return code.

    ``0`` always succeeds. Positive values use the complete mapping from
    ``DstarTradeApiError.h``. Negative values use the action-specific return
    documentation from ``DstarTradeApi.h``; unknown values become
    :class:`DstarNativeError` and retain their original code.
    """

    numeric_code = int(code)
    if numeric_code == DstarErrorCode.SUCCESS:
        return

    spec: ErrorSpec | None = None
    if numeric_code < 0:
        action_errors = _ACTION_ERRORS.get(_normalize_action(action))
        if action_errors is not None:
            spec = action_errors.get(numeric_code)
        if spec is None:
            spec = (_UNKNOWN_MESSAGE, DstarNativeError)
    else:
        spec = _ERROR_SPECS.get(numeric_code)
        if spec is None:
            # Undeclared positive values may be exchange pass-through errors.
            # Keep the exact code while avoiding an unsupported classification.
            spec = (_UNKNOWN_MESSAGE, DstarRequestError)

    message, exception_type = spec
    raise exception_type(numeric_code, message, action)


__all__ = [
    "DstarAuthError",
    "DstarConnectionError",
    "DstarError",
    "DstarErrorCode",
    "DstarNativeError",
    "DstarRequestError",
    "DstarTimeoutError",
    "ERROR_MESSAGES",
    "get_error_message",
    "raise_for_error",
]

