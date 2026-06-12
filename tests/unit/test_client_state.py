"""State-management tests for the high-level DstarTradeClient."""

from __future__ import annotations

import pytest

from dstar_trade_py import DstarTradeClient
from dstar_trade_py.enums import Direction, Hedge, Offset, OrderType, ValidType
from dstar_trade_py.errors import DstarRequestError


class FakeNativeTradeApi:
    """Small fake matching the NativeTradeApi surface used by DstarTradeClient."""

    def __init__(self) -> None:
        self.dispatcher = None
        self.calls: list[tuple[str, object]] = []
        self.order_payload: dict[str, object] | None = None

    def register_callback(self, dispatcher) -> None:
        self.dispatcher = dispatcher
        self.calls.append(("register_callback", dispatcher))

    def register_front_address(self, ip: str, port: int) -> None:
        self.calls.append(("register_front_address", (ip, port)))

    def set_api_log_path(self, path: str) -> None:
        self.calls.append(("set_api_log_path", path))

    def set_login_info(self, login_info: dict[str, object]) -> None:
        self.calls.append(("set_login_info", login_info))

    def set_cpu_id(self, recv_notice_cpu_id: int, log_cpu_id: int) -> None:
        self.calls.append(("set_cpu_id", (recv_notice_cpu_id, log_cpu_id)))

    def set_subscribe_start_id(self, start_id: int) -> None:
        self.calls.append(("set_subscribe_start_id", start_id))

    def set_real_time_data_filter(self, filter: int) -> None:
        self.calls.append(("set_real_time_data_filter", filter))

    def set_run_mode(self, mode: int) -> None:
        self.calls.append(("set_run_mode", mode))

    def set_submit_info(self, submit_info: dict[str, object]) -> None:
        self.calls.append(("set_submit_info", submit_info))

    def set_init_qry_info(self, init_qry_info: dict[str, object]) -> None:
        self.calls.append(("set_init_qry_info", init_qry_info))

    def init(self) -> int:
        self.calls.append(("init", None))
        return 0

    def req_order_insert(self, data: dict[str, object]) -> int:
        self.order_payload = data
        self.calls.append(("req_order_insert", data))
        return 0

    def emit(self, event_name: str, payload: dict[str, object]) -> None:
        assert self.dispatcher is not None
        self.dispatcher.on_event(event_name, payload)


def make_client() -> tuple[DstarTradeClient, FakeNativeTradeApi]:
    """Create a client backed by a single fake native instance."""

    fake = FakeNativeTradeApi()
    client = DstarTradeClient(
        front_ip="127.0.0.1",
        front_port=12345,
        account_no="demo-account",
        password="demo-password",
        app_id="demo-app",
        license_no="demo-license",
        api_factory=lambda: fake,
    )
    return client, fake


def test_client_connect_and_login_update_basic_state() -> None:
    """connect configures native API; login calls Init but waits for callbacks for state."""

    client, fake = make_client()

    assert client.created is True
    assert client.connected is False
    assert client.initialized is False

    client.connect()

    assert client.connected is True
    assert fake.dispatcher is client
    assert ("register_front_address", ("127.0.0.1", 12345)) in fake.calls

    client.login()

    assert client.initialized is True
    assert client.logged_in is False
    fake.emit(
        "rsp_user_login",
        {
            "AccountIndex": 1,
            "AccountNo": "demo-account",
            "TradeDate": "20260612",
            "UdpAuthCode": 123,
            "ErrorCode": 0,
            "StartTime": 90000,
            "StartMode": 1,
            "FloatFlag": 1,
        },
    )

    assert client.logged_in is True


def test_wait_ready_and_disconnected_state() -> None:
    """api_ready and front_disconnected callbacks should drive lifecycle flags."""

    client, fake = make_client()

    client.connect()
    fake.emit("api_ready", {"serial_id": 99})
    client.wait_ready(timeout=0.01)

    assert client.api_ready is True
    assert client.connected is True

    fake.emit("front_disconnected", {})

    assert client.disconnected is True
    assert client.connected is False
    assert client.api_ready is False


def test_insert_order_requires_api_ready() -> None:
    """下单前必须收到 api_ready，防止在未就绪状态提交真实交易请求。"""

    client, _ = make_client()

    with pytest.raises(DstarRequestError, match="insert_order failed"):
        client.insert_order(
            direct=int(Direction.BUY),
            offset=int(Offset.OPEN),
            hedge=int(Hedge.SPECULATE),
            order_type=int(OrderType.LIMIT),
            valid_type=int(ValidType.GFD),
            account_index=1,
            contract_index=2,
            contract_no="GC2608",
            order_qty=1,
            order_price=2400.5,
            client_req_id=100,
        )


def test_insert_order_returns_local_request_code_after_ready() -> None:
    """insert_order returns the native request code and stores no fake trade result."""

    client, fake = make_client()

    client.connect()
    fake.emit("api_ready", {"serial_id": 99})
    ret = client.insert_order(
        direct=int(Direction.BUY),
        offset=int(Offset.OPEN),
        hedge=int(Hedge.SPECULATE),
        order_type=int(OrderType.LIMIT),
        valid_type=int(ValidType.GFD),
        account_index=1,
        contract_index=2,
        contract_no="GC2608",
        order_qty=1,
        order_price=2400.5,
        client_req_id=100,
    )

    assert ret == 0
    assert fake.order_payload is not None
    assert fake.order_payload["ContractNo"] == "GC2608"
    assert client.trade_events.empty()


def test_close_releases_client_state() -> None:
    """close drops the native reference and marks the client disconnected."""

    client, _ = make_client()

    client.connect()
    client.close()

    assert client.created is False
    assert client.connected is False
    assert client.disconnected is True
