"""asyncio 风格的 Dstar 高层交易客户端。"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any, Mapping

from .client import DstarClientEvent, DstarTradeClient, NativeApiFactory
from .enums import RealTimeDataFilter, RunMode
from .errors import DstarRequestError, DstarTimeoutError, raise_for_error
from .fields import (
    DstarApiFundField,
    DstarApiInitQryInfoField,
    DstarApiMatchField,
    DstarApiPositionField,
    DstarApiReqLoginField,
    DstarApiSubmitInfoField,
)


_QUEUE_SENTINEL = object()


class AsyncDstarTradeClient(DstarTradeClient):
    """基于 ``asyncio`` 的交易客户端。

    易盛 SDK 的 SPI 回调可能来自官方 API 的工作线程，而 ``asyncio.Future`` 和
    ``asyncio.Queue`` 只能在所属事件循环线程中安全操作。因此本类重写 ``on_event``：
    回调线程只复制 payload 并调用 ``loop.call_soon_threadsafe``，真正的状态更新、
    Future 唤醒和异步队列写入全部在事件循环线程执行。
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
        api_factory: NativeApiFactory | None = None,
    ) -> None:
        """创建 async 客户端。

        ``api_factory`` 仅用于测试或高级注入；生产环境默认沿用同步客户端的
        ``NativeTradeApi`` 创建逻辑。
        """

        kwargs: dict[str, Any] = {
            "front_ip": front_ip,
            "front_port": front_port,
            "account_no": account_no,
            "password": password,
            "app_id": app_id,
            "license_no": license_no,
            "api_log_path": api_log_path,
            "recv_notice_cpu_id": recv_notice_cpu_id,
            "log_cpu_id": log_cpu_id,
            "subscribe_start_id": subscribe_start_id,
            "real_time_data_filter": real_time_data_filter,
            "run_mode": run_mode,
            "submit_info": submit_info,
            "init_qry_info": init_qry_info,
        }
        if api_factory is not None:
            kwargs["api_factory"] = api_factory
        super().__init__(**kwargs)

        self._loop: asyncio.AbstractEventLoop | None = None
        self._async_events: asyncio.Queue[DstarClientEvent | object] | None = None
        self._async_orders: asyncio.Queue[Any] | None = None
        self._async_trades: asyncio.Queue[DstarApiMatchField | object] | None = None

        self._ready_waiters: list[asyncio.Future[None]] = []
        self._fund_future: asyncio.Future[DstarApiFundField] | None = None
        self._position_future: asyncio.Future[list[DstarApiPositionField]] | None = None
        self._closed_async = False

    async def connect(
        self,
        *,
        front_ip: str | None = None,
        front_port: int | None = None,
    ) -> None:
        """异步注册回调、前置地址和本地运行参数。"""

        self._bind_loop()
        super().connect(front_ip=front_ip, front_port=front_port)

    async def login(
        self,
        *,
        account_no: str | None = None,
        password: str | None = None,
        app_id: str | None = None,
        license_no: str | None = None,
    ) -> None:
        """异步执行同步客户端的登录/Init 流程。

        ``Init`` 可能创建连接并阻塞一小段时间，因此通过 ``asyncio.to_thread`` 放到工作
        线程执行，避免卡住事件循环。
        """

        self._bind_loop()
        if not self.connected:
            await self.connect()
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
        api = self._require_api()
        api.set_login_info(login_info.to_dict())
        ret = await asyncio.to_thread(api.init)
        raise_for_error(ret, "Init")
        with self._condition:
            self.initialized = True
            self._condition.notify_all()

    async def wait_ready(self, timeout: float = 30) -> None:
        """等待 ``api_ready`` 回调。"""

        self._bind_loop()
        if self.api_ready:
            return
        future: asyncio.Future[None] = self._loop.create_future()
        self._ready_waiters.append(future)
        try:
            await asyncio.wait_for(future, timeout)
        except TimeoutError as exc:
            raise DstarTimeoutError(-1, "Timed out waiting for API ready", "wait_ready") from exc
        finally:
            if future in self._ready_waiters:
                self._ready_waiters.remove(future)

    async def query_fund(self, timeout: float = 5) -> DstarApiFundField:
        """异步请求资金并等待 ``rsp_qry_fund`` 响应。"""

        self._bind_loop()
        self._ensure_ready("query_fund")
        if self._fund_future is not None and not self._fund_future.done():
            raise DstarRequestError(-4, "Previous fund query has not completed", "query_fund")

        future: asyncio.Future[DstarApiFundField] = self._loop.create_future()
        self._fund_future = future
        try:
            ret = self._require_api().req_qry_fund()
            raise_for_error(ret, "ReqQryFund")
            return await asyncio.wait_for(future, timeout)
        except TimeoutError as exc:
            raise DstarTimeoutError(-1, "Timed out waiting for fund response", "query_fund") from exc
        finally:
            if self._fund_future is future:
                self._fund_future = None

    async def query_position(self, timeout: float = 5) -> list[DstarApiPositionField]:
        """异步请求持仓并等待 ``rsp_qry_position`` 的 ``last=True`` 响应。"""

        self._bind_loop()
        self._ensure_ready("query_position")
        if self._position_future is not None and not self._position_future.done():
            raise DstarRequestError(
                -4,
                "Previous position query has not completed",
                "query_position",
            )

        future: asyncio.Future[list[DstarApiPositionField]] = self._loop.create_future()
        self._position_future = future
        try:
            ret = self._require_api().req_qry_position()
            raise_for_error(ret, "ReqQryPosition")
            return await asyncio.wait_for(future, timeout)
        except TimeoutError as exc:
            raise DstarTimeoutError(
                -1,
                "Timed out waiting for position response",
                "query_position",
            ) from exc
        finally:
            if self._position_future is future:
                self._position_future = None

    async def get_system_info(self) -> dict[str, Any]:
        """异步采集系统授权信息。"""

        self._bind_loop()
        return await asyncio.to_thread(super().get_system_info)

    async def get_api_version(self) -> str:
        """异步返回官方交易 API 版本号。"""

        self._bind_loop()
        return super().get_api_version()

    async def insert_order(self, **kwargs: Any) -> int:
        """异步提交普通报单，返回官方本地请求返回码。"""

        self._bind_loop()
        return super().insert_order(**kwargs)

    async def insert_limit_order(self, **kwargs: Any) -> int:
        """异步提交限价报单，返回官方本地请求返回码。"""

        self._bind_loop()
        return super().insert_limit_order(**kwargs)

    async def insert_market_order_if_supported(self, **kwargs: Any) -> int:
        """异步提交市价报单请求；是否支持由官方返回码和后续回报决定。"""

        self._bind_loop()
        return super().insert_market_order_if_supported(**kwargs)

    async def cancel_order(self, **kwargs: Any) -> int:
        """异步提交撤单请求，返回官方本地请求返回码。"""

        self._bind_loop()
        return super().cancel_order(**kwargs)

    async def cancel_offer_if_supported(self, **kwargs: Any) -> int:
        """异步撤销报价请求；底层复用 ReqOrderDelete。"""

        self._bind_loop()
        return super().cancel_offer_if_supported(**kwargs)

    async def query_last_client_req_id(self, timeout: float = 5) -> int:
        """异步查询最新客户请求号。"""

        self._bind_loop()
        return await asyncio.to_thread(super().query_last_client_req_id, timeout)

    async def modify_password(self, *, new_password: str, old_password: str) -> int:
        """异步提交密码修改请求，返回官方本地请求返回码。"""

        self._bind_loop()
        return super().modify_password(new_password=new_password, old_password=old_password)

    async def insert_offer(self, **kwargs: Any) -> int:
        """异步提交报价请求，返回官方本地请求返回码。"""

        self._bind_loop()
        return super().insert_offer(**kwargs)

    async def insert_offer_new(self, **kwargs: Any) -> int:
        """异步提交新版报价请求，返回官方本地请求返回码。"""

        self._bind_loop()
        return super().insert_offer_new(**kwargs)

    async def insert_cmb_order(self, **kwargs: Any) -> int:
        """异步提交组合报单请求，返回官方本地请求返回码。"""

        self._bind_loop()
        return super().insert_cmb_order(**kwargs)

    async def insert_combo_order(self, **kwargs: Any) -> int:
        """异步提交组合报单请求的 Pythonic 别名。"""

        self._bind_loop()
        return super().insert_combo_order(**kwargs)

    async def close(self) -> None:
        """关闭客户端并唤醒异步迭代器。"""

        self._bind_loop()
        super().close()
        self._closed_async = True
        self._fail_pending_waiters(DstarRequestError(-1, "AsyncDstarTradeClient is closed", "close"))
        self._async_events_queue().put_nowait(_QUEUE_SENTINEL)
        self._async_orders_queue().put_nowait(_QUEUE_SENTINEL)
        self._async_trades_queue().put_nowait(_QUEUE_SENTINEL)

    def on_event(self, event_name: str, payload: dict[str, Any]) -> None:
        """SDK 回调入口，只做线程安全投递。

        这里可能运行在易盛 SDK 的工作线程。不能在这个线程中直接 ``Future.set_result``
        或 ``asyncio.Queue.put_nowait``，否则会破坏 asyncio 对象的线程亲和性。
        """

        loop = self._loop
        payload_copy = dict(payload)
        if loop is None or loop.is_closed():
            return
        loop.call_soon_threadsafe(self._handle_event_on_loop, event_name, payload_copy)

    async def iter_events(self) -> AsyncIterator[DstarClientEvent]:
        """异步迭代所有回调事件。"""

        self._bind_loop()
        queue = self._async_events_queue()
        while True:
            item = await queue.get()
            if item is _QUEUE_SENTINEL:
                break
            yield item

    async def iter_orders(self) -> AsyncIterator[Any]:
        """异步迭代委托相关事件。"""

        self._bind_loop()
        queue = self._async_orders_queue()
        while True:
            item = await queue.get()
            if item is _QUEUE_SENTINEL:
                break
            yield item

    async def iter_trades(self) -> AsyncIterator[DstarApiMatchField]:
        """异步迭代成交事件。"""

        self._bind_loop()
        queue = self._async_trades_queue()
        while True:
            item = await queue.get()
            if item is _QUEUE_SENTINEL:
                break
            yield item

    def _bind_loop(self) -> None:
        """绑定当前运行中的 asyncio loop，并确保所有 asyncio 队列在该 loop 中使用。"""

        loop = asyncio.get_running_loop()
        if self._loop is not None and self._loop is not loop:
            raise RuntimeError("AsyncDstarTradeClient cannot be used from multiple event loops")
        self._loop = loop
        self._async_events_queue()
        self._async_orders_queue()
        self._async_trades_queue()

    def _handle_event_on_loop(self, event_name: str, payload: dict[str, Any]) -> None:
        """在事件循环线程中完成事件转换、同步状态更新和异步唤醒。"""

        data = self._convert_event_payload(event_name, payload)
        event = DstarClientEvent(event_name, payload, data)

        with self._condition:
            self.raw_events.put(event)
            self._update_state_from_event(event_name, data, payload)
            self._route_event_to_queue(event_name, data)
            self._condition.notify_all()

        self._async_events_queue().put_nowait(event)
        self._route_async_event(event_name, data)

    def _route_async_event(self, event_name: str, data: Any) -> None:
        """把事件投递到 asyncio 队列，并完成对应的请求 Future。"""

        if event_name in {"rsp_order", "rtn_order", "rsp_order_insert", "rsp_order_delete"}:
            self._async_orders_queue().put_nowait(data)
        elif event_name in {"rsp_match", "rtn_match"} and isinstance(data, DstarApiMatchField):
            self._async_trades_queue().put_nowait(data)

        if event_name == "api_ready":
            for future in list(self._ready_waiters):
                if not future.done():
                    future.set_result(None)
            self._ready_waiters.clear()
        elif event_name == "front_disconnected":
            self._fail_pending_waiters(
                DstarTimeoutError(-1, "Disconnected while waiting for response", event_name)
            )
        elif event_name == "rsp_qry_fund" and isinstance(data, DstarApiFundField):
            if self._fund_future is not None and not self._fund_future.done():
                self._fund_future.set_result(data)
        elif event_name == "rsp_qry_position" and isinstance(data, dict) and data["last"]:
            if self._position_future is not None and not self._position_future.done():
                self._position_future.set_result(list(self._latest_position_batch))

    def _fail_pending_waiters(self, error: Exception) -> None:
        """关闭或断线时统一失败所有未完成的异步等待。"""

        for future in list(self._ready_waiters):
            if not future.done():
                future.set_exception(error)
        self._ready_waiters.clear()
        if self._fund_future is not None and not self._fund_future.done():
            self._fund_future.set_exception(error)
        if self._position_future is not None and not self._position_future.done():
            self._position_future.set_exception(error)

    def _async_events_queue(self) -> asyncio.Queue[DstarClientEvent | object]:
        """延迟创建原始事件异步队列。"""

        if self._async_events is None:
            self._async_events = asyncio.Queue()
        return self._async_events

    def _async_orders_queue(self) -> asyncio.Queue[Any]:
        """延迟创建委托事件异步队列。"""

        if self._async_orders is None:
            self._async_orders = asyncio.Queue()
        return self._async_orders

    def _async_trades_queue(self) -> asyncio.Queue[DstarApiMatchField | object]:
        """延迟创建成交事件异步队列。"""

        if self._async_trades is None:
            self._async_trades = asyncio.Queue()
        return self._async_trades


__all__ = ["AsyncDstarTradeClient"]
