"""真实测试 demo 共用工具。

本文件只从环境变量读取连接和登录配置，不保存任何真实账号、密码或授权信息。
下单类 demo 必须调用这里的确认函数，避免误触发真实交易请求。
"""

from __future__ import annotations

import argparse
import os
import queue
import sys
import time
from dataclasses import asdict, is_dataclass
from pprint import pprint
from typing import Any, Iterable

from dstar_trade_py import DstarClientEvent, DstarTradeClient
from dstar_trade_py.config import DstarTradeConfig, REQUIRED_TRADE_ENV_VARS, load_config_from_env
from dstar_trade_py.enums import Direction, Hedge, Offset, OrderType, ValidType
from dstar_trade_py.errors import raise_for_error
from dstar_trade_py.fields import DstarApiRspLoginField


REQUIRED_ENV_VARS = (*REQUIRED_TRADE_ENV_VARS, "DSTAR_TRADE_LOG_PATH")
LiveTradeConfig = DstarTradeConfig


def load_config() -> LiveTradeConfig:
    """读取并校验真实测试环境变量。"""

    if not os.environ.get("DSTAR_TRADE_LOG_PATH"):
        raise RuntimeError(
            "Missing required Dstar live-test environment variable: "
            "DSTAR_TRADE_LOG_PATH. See docs/live_testing.md for setup instructions."
        )
    config = load_config_from_env(require_credentials=True)
    return config


def print_config_summary(config: LiveTradeConfig) -> None:
    """打印非敏感配置摘要，敏感字段统一脱敏。"""

    redacted = config.to_redacted_dict()
    print("Dstar live-test configuration:")
    print(f"  trade_ip: {redacted['trade_ip']}")
    print(f"  trade_port: {redacted['trade_port']}")
    print(f"  user: {redacted['user']}")
    print(f"  password: {redacted['password']}")
    print(f"  auth_code: {redacted['auth_code']}")
    print(f"  app_id: {redacted['app_id']}")
    print(f"  log_path: {redacted['log_path']}")


def make_client(config: LiveTradeConfig) -> DstarTradeClient:
    """用真实测试配置创建同步高层客户端。"""

    config.ensure_native_log_path()
    return DstarTradeClient(**config.to_client_kwargs())


def connect_login_ready(timeout: float = 30) -> DstarTradeClient:
    """创建客户端、连接、登录并等待 api_ready。"""

    config = load_config()
    print_config_summary(config)
    client = make_client(config)
    client.connect()
    client.login()
    client.wait_ready(timeout=timeout)
    print("API ready.")
    return client


def wait_for_event(
    client: DstarTradeClient,
    event_names: Iterable[str],
    timeout: float,
) -> DstarClientEvent:
    """从 raw_events 队列等待指定事件。"""

    expected = set(event_names)
    deadline = time.monotonic() + timeout
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            names = ", ".join(sorted(expected))
            raise TimeoutError(f"Timed out waiting for event: {names}")
        try:
            event = client.raw_events.get(timeout=remaining)
        except queue.Empty as exc:
            names = ", ".join(sorted(expected))
            raise TimeoutError(f"Timed out waiting for event: {names}") from exc
        if event.name in expected:
            return event
        print_event(event)


def latest_login_response(client: DstarTradeClient) -> DstarApiRspLoginField | None:
    """从现有 raw_events 中提取最近一次登录应答，用于默认账号索引和 UDP 认证码。"""

    latest: DstarApiRspLoginField | None = None
    buffered: list[DstarClientEvent] = []
    while True:
        try:
            event = client.raw_events.get_nowait()
        except queue.Empty:
            break
        buffered.append(event)
        if event.name == "rsp_user_login" and isinstance(event.data, DstarApiRspLoginField):
            latest = event.data

    # 把非登录事件放回队列，避免订阅 demo 丢失业务事件。
    for event in buffered:
        if event.name != "rsp_user_login":
            client.raw_events.put(event)
    return latest


def print_event(event: DstarClientEvent) -> None:
    """用可读方式打印事件名和数据。"""

    print(f"[event] {event.name}")
    print_value(event.data)


def print_value(value: Any) -> None:
    """打印 dataclass 或普通 Python 值。"""

    if is_dataclass(value):
        pprint(asdict(value))
    else:
        pprint(value)


def next_client_req_id(client: DstarTradeClient, timeout: float = 5) -> int:
    """查询最新请求号并返回下一笔请求号。"""

    return client.query_last_client_req_id(timeout=timeout) + 1


def order_direction(value: str) -> int:
    """解析买卖方向。"""

    mapping = {"buy": int(Direction.BUY), "sell": int(Direction.SELL)}
    try:
        return mapping[value.casefold()]
    except KeyError as exc:
        raise argparse.ArgumentTypeError("direction must be buy or sell") from exc


def order_offset(value: str) -> int:
    """解析开平标志。"""

    mapping = {
        "open": int(Offset.OPEN),
        "close": int(Offset.CLOSE),
        "close_today": int(Offset.CLOSE_TODAY),
    }
    try:
        return mapping[value.casefold()]
    except KeyError as exc:
        raise argparse.ArgumentTypeError("offset must be open, close, or close_today") from exc


def order_hedge(value: str) -> int:
    """解析投机套保标志。"""

    mapping = {"speculate": int(Hedge.SPECULATE), "hedge": int(Hedge.HEDGE)}
    try:
        return mapping[value.casefold()]
    except KeyError as exc:
        raise argparse.ArgumentTypeError("hedge must be speculate or hedge") from exc


def positive_int(value: str) -> int:
    """解析正整数命令行参数。"""

    numeric = int(value)
    if numeric <= 0:
        raise argparse.ArgumentTypeError("value must be a positive integer")
    return numeric


def confirm_live_order(action: str, params: dict[str, Any], confirm_flag: bool) -> bool:
    """真实下单/撤单前的强制安全确认。

    默认 dry-run，只有传入 ``--confirm-live-order`` 后才进入二次确认。二次确认必须
    手工输入 ``YES``，否则仍然不会发送真实请求。
    """

    print(f"{action} parameters:")
    pprint(params)
    if not confirm_flag:
        print("dry_run=True. No live request was sent.")
        print("Pass --confirm-live-order and type YES to send this request.")
        return False

    print("WARNING: this will send a real request to the configured Dstar test environment.")
    answer = input("Type YES to confirm: ")
    if answer != "YES":
        print("Confirmation failed. No live request was sent.")
        return False
    return True


def exit_with_error(exc: BaseException) -> None:
    """demo 统一错误出口。"""

    print(f"ERROR: {exc}", file=sys.stderr)
    raise SystemExit(1) from exc


def raise_login_error(login: DstarApiRspLoginField) -> None:
    """登录应答错误码统一处理。"""

    raise_for_error(login.ErrorCode, "OnRspUserLogin")


DEFAULT_ORDER_TYPE = int(OrderType.LIMIT)
DEFAULT_VALID_TYPE = int(ValidType.GFD)
