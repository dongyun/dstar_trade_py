"""Pythonic high-level client built on top of the native Dstar trade API bridge."""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from ._dstar_trade_py import NativeTradeApi
from .enums import RealTimeDataFilter, RunMode
from .errors import (
    DstarErrorCode,
    DstarRequestError,
    DstarTimeoutError,
    get_error_message,
    raise_for_error,
)
from .fields import (
    DstaApiRspLastReqIdField,
    DstarApiFundField,
    DstarApiInitQryInfoField,
    DstarApiMatchField,
    DstarApiOrderField,
    DstarApiReqLoginField,
    DstarApiReqOrderDeleteField,
    DstarApiReqOrderInsertField,
    DstarApiReqPwdModField,
    DstarApiRspLoginField,
    DstarApiRspOrderInsertField,
    DstarApiRspPwdModField,
    DstarApiSubmitInfoField,
    DstarApiPositionField,
)


NativeApiFactory = Callable[[], NativeTradeApi]


@dataclass(slots=True)
class DstarClientEvent:
    """高层客户端保存的事件对象，保留原始事件名、payload 和转换后的数据。"""

    name: str
    payload: dict[str, Any]
    data: Any = None


class DstarTradeClient:
    """面向 Python 用户的交易客户端。

    该类只负责 SDK 本地生命周期、同步等待和事件整理，不隐藏交易所/柜台返回的真实结果。
    例如 ``insert_order`` 只返回本地请求是否成功送入 API，不会伪造成交或委托成功。
    """

    def __init__(
        self,
        *,
        front_ip: str | None = None,
        front_port: int | None = None,
        account_no: str = "",
        password: str = "",
        app_id: str = "",
        license_no: str = "",
        api_log_path: str = "",
        recv_notice_cpu_id: int = -1,
        log_cpu_id: int = -1,
        subscribe_start_id: int = -1,
        real_time_data_filter: int = int(RealTimeDataFilter.NONE),
        run_mode: int = int(RunMode.FULL_LOAD),
        submit_info: DstarApiSubmitInfoField | Mapping[str, Any] | None = None,
        init_qry_info: DstarApiInitQryInfoField | Mapping[str, Any] | None = None,
        api_factory: NativeApiFactory = NativeTradeApi,
    ) -> None:
        """创建客户端并立即创建 native API 实例。

        ``api_factory`` 主要用于单元测试注入 fake native；生产环境默认创建 pybind11
        暴露的 ``NativeTradeApi``，Python 侧永远不直接接触官方 ``IDstarTradeApi*``。
        """

        self._api_factory = api_factory
        self._api: NativeTradeApi | None = api_factory()
        self._condition = threading.Condition()

        self.front_ip = front_ip
        self.front_port = front_port
        self.account_no = account_no
        self.password = password
        self.app_id = app_id
        self.license_no = license_no
        self.api_log_path = api_log_path
        self.recv_notice_cpu_id = recv_notice_cpu_id
        self.log_cpu_id = log_cpu_id
        self.subscribe_start_id = subscribe_start_id
        self.real_time_data_filter = real_time_data_filter
        self.run_mode = run_mode
        self.submit_info = submit_info
        self.init_qry_info = init_qry_info

        # 生命周期状态由同步方法和回调共同维护。只有收到 api_ready 后才允许下单。
        self.created = True
        self.initialized = False
        self.connected = False
        self.logged_in = False
        self.api_ready = False
        self.disconnected = False

        # 对外暴露的事件队列。raw_events 保存全部事件，其余队列保存已转换的数据模型。
        self.raw_events: queue.Queue[DstarClientEvent] = queue.Queue()
        self.order_events: queue.Queue[Any] = queue.Queue()
        self.trade_events: queue.Queue[DstarApiMatchField] = queue.Queue()
        self.fund_events: queue.Queue[DstarApiFundField] = queue.Queue()
        self.position_events: queue.Queue[DstarApiPositionField] = queue.Queue()

        # 请求-响应等待使用 generation 计数，避免回调先于 req_* 返回时丢失唤醒。
        self._fund_generation = 0
        self._latest_fund: DstarApiFundField | None = None
        self._fund_query_inflight = False

        self._position_generation = 0
        self._position_buffer: list[DstarApiPositionField] = []
        self._latest_position_batch: list[DstarApiPositionField] = []
        self._position_query_inflight = False

        self._last_req_id_generation = 0
        self._latest_last_req_id: DstaApiRspLastReqIdField | None = None
        self._last_req_id_inflight = False

    def connect(self, *, front_ip: str | None = None, front_port: int | None = None) -> None:
        """注册回调、前置地址和本地运行参数。

        官方 API 的真实 TCP 连接由 ``Init`` 触发，因此本方法表示“客户端配置完成”，
        不会向交易前置发起登录。调用 ``login`` 后才会进入初始化/登录流程。
        """

        api = self._require_api()
        if front_ip is not None:
            self.front_ip = front_ip
        if front_port is not None:
            self.front_port = front_port
        if not self.front_ip or self.front_port is None:
            raise ValueError("front_ip and front_port are required before connect()")

        api.register_callback(self)
        api.register_front_address(self.front_ip, self.front_port)
        if self.api_log_path:
            api.set_api_log_path(self.api_log_path)
        api.set_cpu_id(self.recv_notice_cpu_id, self.log_cpu_id)
        api.set_subscribe_start_id(self.subscribe_start_id)
        api.set_real_time_data_filter(self.real_time_data_filter)
        api.set_run_mode(self.run_mode)
        if self.submit_info is not None:
            api.set_submit_info(self._field_to_dict(self.submit_info))
        api.set_init_qry_info(self._field_to_dict(self.init_qry_info or DstarApiInitQryInfoField()))

        with self._condition:
            self.connected = True
            self.disconnected = False
            self._condition.notify_all()

    def close(self) -> None:
        """释放 native API 引用并标记客户端关闭。

        官方头文件没有提供 Close/Release 之外的主动断开接口；pybind11 对象引用归零后，
        其 RAII 析构会调用 ``FreeDstarTradeApi``。
        """

        with self._condition:
            self._api = None
            self.created = False
            self.initialized = False
            self.connected = False
            self.logged_in = False
            self.api_ready = False
            self.disconnected = True
            self._condition.notify_all()

    def login(
        self,
        *,
        account_no: str | None = None,
        password: str | None = None,
        app_id: str | None = None,
        license_no: str | None = None,
    ) -> None:
        """设置登录信息并调用官方 ``Init``。

        登录是否真正成功由后续 ``rsp_user_login`` 回调确认；本方法只校验本地 ``Init``
        同步返回码。调用者可继续使用 ``wait_ready`` 等待 API 就绪。
        """

        api = self._require_api()
        if not self.connected:
            self.connect()
        if account_no is not None:
            self.account_no = account_no
        if password is not None:
            self.password = password
        if app_id is not None:
            self.app_id = app_id
        if license_no is not None:
            self.license_no = license_no
        login_info = DstarApiReqLoginField(
            AccountNo=self.account_no,
            Password=self.password,
            AppId=self.app_id,
            LicenseNo=self.license_no,
        )

        api.set_login_info(login_info.to_dict())
        ret = api.init()
        raise_for_error(ret, "Init")
        with self._condition:
            self.initialized = True
            self._condition.notify_all()

    def wait_ready(self, timeout: float = 30) -> None:
        """等待 ``api_ready`` 回调。

        未在超时时间内收到就绪事件时抛出 ``DstarTimeoutError``；收到断开事件也会被视为
        等待失败，避免调用方在不可交易状态继续下单。
        """

        self._wait_for(
            lambda: self.api_ready or self.disconnected or not self.created,
            timeout,
            "wait_ready",
        )
        if not self.api_ready:
            raise DstarTimeoutError(-1, "Timed out waiting for API ready", "wait_ready")

    def query_fund(self, timeout: float = 5) -> DstarApiFundField:
        """请求资金并等待 ``rsp_qry_fund`` 响应。"""

        api = self._require_api()
        self._ensure_ready("query_fund")
        with self._condition:
            if self._fund_query_inflight:
                raise DstarRequestError(-4, "Previous fund query has not completed", "query_fund")
            self._fund_query_inflight = True
            start_generation = self._fund_generation

        try:
            ret = api.req_qry_fund()
            raise_for_error(ret, "ReqQryFund")
            self._wait_for(lambda: self._fund_generation > start_generation, timeout, "query_fund")
            if self._latest_fund is None:
                raise DstarTimeoutError(-1, "Timed out waiting for fund response", "query_fund")
            return self._latest_fund
        finally:
            with self._condition:
                self._fund_query_inflight = False
                self._condition.notify_all()

    def query_position(self, timeout: float = 5) -> list[DstarApiPositionField]:
        """请求持仓并等待 ``rsp_qry_position`` 的 ``last=True`` 响应。"""

        api = self._require_api()
        self._ensure_ready("query_position")
        with self._condition:
            if self._position_query_inflight:
                raise DstarRequestError(
                    -4, "Previous position query has not completed", "query_position"
                )
            self._position_query_inflight = True
            self._position_buffer = []
            start_generation = self._position_generation

        try:
            ret = api.req_qry_position()
            raise_for_error(ret, "ReqQryPosition")
            self._wait_for(
                lambda: self._position_generation > start_generation,
                timeout,
                "query_position",
            )
            return list(self._latest_position_batch)
        finally:
            with self._condition:
                self._position_query_inflight = False
                self._condition.notify_all()

    def insert_order(
        self,
        *,
        direct: int,
        offset: int,
        hedge: int,
        order_type: int,
        valid_type: int,
        account_index: int,
        contract_index: int,
        contract_no: str,
        order_qty: int,
        order_price: float,
        client_req_id: int,
        seat_index: int = 0,
        min_qty: int = 1,
        reference: int = 0,
        udp_auth_code: int = 0,
    ) -> int:
        """提交普通报单，返回官方本地请求返回码。

        该方法只表示请求是否成功送入 API。本地返回 0 不代表交易所接收、成交或最终成功；
        后续委托/成交变化必须从 ``order_events`` 和 ``trade_events`` 读取。
        """

        self._ensure_ready("insert_order")
        request = DstarApiReqOrderInsertField(
            Direct=direct,
            Offset=offset,
            Hedge=hedge,
            OrderType=order_type,
            ValidType=valid_type,
            SeatIndex=seat_index,
            AccountIndex=account_index,
            ContractIndex=contract_index,
            ContractNo=contract_no,
            OrderQty=order_qty,
            MinQty=min_qty,
            OrderPrice=order_price,
            ClientReqId=client_req_id,
            Reference=reference,
            UdpAuthCode=udp_auth_code,
        )
        ret = self._require_api().req_order_insert(request.to_dict())
        raise_for_error(ret, "ReqOrderInsert")
        return ret

    def cancel_order(
        self,
        *,
        account_index: int,
        client_req_id: int,
        order_id: int,
        system_no: str = "",
        udp_auth_code: int = 0,
        reference: int = 0,
        seat_index: int = 0,
    ) -> int:
        """提交撤单请求，返回官方本地请求返回码。"""

        self._ensure_ready("cancel_order")
        request = DstarApiReqOrderDeleteField(
            AccountIndex=account_index,
            ClientReqId=client_req_id,
            UdpAuthCode=udp_auth_code,
            Reference=reference,
            SeatIndex=seat_index,
            OrderId=order_id,
            SystemNo=system_no,
        )
        ret = self._require_api().req_order_delete(request.to_dict())
        raise_for_error(ret, "ReqOrderDelete")
        return ret

    def query_last_client_req_id(self, timeout: float = 5) -> int:
        """查询最新客户请求号并等待 ``rsp_last_req_id`` 响应。"""

        api = self._require_api()
        self._ensure_ready("query_last_client_req_id")
        with self._condition:
            if self._last_req_id_inflight:
                raise DstarRequestError(
                    -4,
                    "Previous last-client-request-id query has not completed",
                    "query_last_client_req_id",
                )
            self._last_req_id_inflight = True
            start_generation = self._last_req_id_generation

        try:
            ret = api.req_last_client_req_id()
            raise_for_error(ret, "ReqLastClientReqId")
            self._wait_for(
                lambda: self._last_req_id_generation > start_generation,
                timeout,
                "query_last_client_req_id",
            )
            if self._latest_last_req_id is None:
                raise DstarTimeoutError(
                    -1,
                    "Timed out waiting for last client request id",
                    "query_last_client_req_id",
                )
            return self._latest_last_req_id.LastClientReqId
        finally:
            with self._condition:
                self._last_req_id_inflight = False
                self._condition.notify_all()

    def modify_password(self, *, new_password: str, old_password: str) -> int:
        """提交密码修改请求，返回官方本地请求返回码。"""

        self._ensure_ready("modify_password")
        request = DstarApiReqPwdModField(Passwd=new_password, OldPasswd=old_password)
        ret = self._require_api().req_pwd_mod(request.to_dict())
        raise_for_error(ret, "ReqPwdMod")
        return ret

    def on_event(self, event_name: str, payload: dict[str, Any]) -> None:
        """Native SPI dispatcher 入口。

        C++ 层已经在回调中立即复制了官方结构体指针；Python 层只接收普通 dict。本方法
        负责把 dict 转为 dataclass、更新状态、推入队列，并唤醒正在等待响应的同步方法。
        """

        payload_copy = dict(payload)
        data = self._convert_event_payload(event_name, payload_copy)
        event = DstarClientEvent(event_name, payload_copy, data)

        with self._condition:
            self.raw_events.put(event)
            self._update_state_from_event(event_name, data, payload_copy)
            self._route_event_to_queue(event_name, data)
            self._condition.notify_all()

    def _convert_event_payload(self, event_name: str, payload: dict[str, Any]) -> Any:
        """按事件名把 native dict 转成对应 dataclass。"""

        if event_name == "rsp_user_login":
            return DstarApiRspLoginField.from_dict(payload)
        if event_name == "rsp_pwd_mod":
            return DstarApiRspPwdModField.from_dict(payload)
        if event_name == "rsp_order_insert":
            return DstarApiRspOrderInsertField.from_dict(payload)
        if event_name == "rsp_order_delete":
            return DstarApiRspOrderInsertField.from_dict(payload)
        if event_name == "rsp_last_req_id":
            return DstaApiRspLastReqIdField.from_dict(payload)
        if event_name in {"rsp_order", "rtn_order"}:
            return DstarApiOrderField.from_dict(payload)
        if event_name in {"rsp_match", "rtn_match"}:
            return DstarApiMatchField.from_dict(payload)
        if event_name in {"rsp_fund", "rsp_qry_fund"}:
            return DstarApiFundField.from_dict(payload)
        if event_name == "rsp_position":
            return DstarApiPositionField.from_dict(payload)
        if event_name == "rsp_qry_position":
            raw_data = payload.get("data")
            position = None
            if isinstance(raw_data, Mapping) and raw_data:
                position = DstarApiPositionField.from_dict(raw_data)
            return {"data": position, "last": bool(payload.get("last", False))}
        return payload

    def _update_state_from_event(
        self,
        event_name: str,
        data: Any,
        payload: dict[str, Any],
    ) -> None:
        """根据关键回调维护生命周期状态。"""

        if event_name == "front_disconnected":
            self.connected = False
            self.disconnected = True
            self.api_ready = False
            return
        if event_name == "rsp_error":
            error_code = int(payload.get("error_code", payload.get("ErrorCode", 0)))
            if error_code in {
                int(DstarErrorCode.NOCONNECTION),
                int(DstarErrorCode.NOTLOGIN),
                int(DstarErrorCode.HB_TIMEOUT),
            }:
                self.connected = False
                self.disconnected = True
                self.api_ready = False
            return
        if event_name == "rsp_user_login" and isinstance(data, DstarApiRspLoginField):
            self.logged_in = data.ErrorCode == int(DstarErrorCode.SUCCESS)
            return
        if event_name == "api_ready":
            self.api_ready = True
            self.connected = True
            self.disconnected = False

    def _route_event_to_queue(self, event_name: str, data: Any) -> None:
        """把转换后的事件推入分类队列，并更新同步等待缓存。"""

        if event_name in {"rsp_order", "rtn_order", "rsp_order_insert", "rsp_order_delete"}:
            self.order_events.put(data)
        elif event_name in {"rsp_match", "rtn_match"} and isinstance(data, DstarApiMatchField):
            self.trade_events.put(data)
        elif event_name in {"rsp_fund", "rsp_qry_fund"} and isinstance(data, DstarApiFundField):
            self.fund_events.put(data)
            if event_name == "rsp_qry_fund":
                self._latest_fund = data
                self._fund_generation += 1
        elif event_name == "rsp_qry_position" and isinstance(data, dict):
            position = data["data"]
            if isinstance(position, DstarApiPositionField):
                self.position_events.put(position)
                self._position_buffer.append(position)
            if data["last"]:
                self._latest_position_batch = list(self._position_buffer)
                self._position_buffer = []
                self._position_generation += 1
        elif event_name == "rsp_position" and isinstance(data, DstarApiPositionField):
            self.position_events.put(data)
        elif event_name == "rsp_last_req_id" and isinstance(data, DstaApiRspLastReqIdField):
            self._latest_last_req_id = data
            self._last_req_id_generation += 1

    def _ensure_ready(self, action: str) -> None:
        """所有真实请求前统一检查 API 就绪状态。"""

        if not self.api_ready:
            raise DstarRequestError(
                int(DstarErrorCode.NOTREADY),
                get_error_message(int(DstarErrorCode.NOTREADY)),
                action,
            )

    def _require_api(self) -> NativeTradeApi:
        """返回 native API；客户端关闭后继续调用会得到明确异常。"""

        if self._api is None:
            raise DstarRequestError(-1, "DstarTradeClient is closed", "client")
        return self._api

    def _wait_for(self, predicate: Callable[[], bool], timeout: float, action: str) -> None:
        """基于 Condition 的超时等待，避免忙等。"""

        deadline = time.monotonic() + timeout
        with self._condition:
            while not predicate():
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise DstarTimeoutError(-1, f"Timed out during {action}", action)
                self._condition.wait(remaining)

    @staticmethod
    def _field_to_dict(value: Any) -> dict[str, Any]:
        """兼容 dataclass 字段对象和普通 mapping。"""

        if hasattr(value, "to_dict"):
            return value.to_dict()
        return dict(value)


__all__ = ["DstarClientEvent", "DstarTradeClient"]
