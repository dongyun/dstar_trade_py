"""真实测试：订阅并打印委托/成交事件。

本 demo 不主动下单，只监听当前账号在指定时间内收到的订单和成交回调。
"""

from __future__ import annotations

import argparse
import queue
import time

from live_common import connect_login_ready, exit_with_error, print_event


def main() -> None:
    """登录并持续打印 order/trade 相关事件。"""

    parser = argparse.ArgumentParser(description="Dstar live order/trade event demo")
    parser.add_argument("--ready-timeout", type=float, default=30, help="等待 api_ready 的超时")
    parser.add_argument("--duration", type=float, default=60, help="监听秒数")
    args = parser.parse_args()

    client = None
    try:
        client = connect_login_ready(timeout=args.ready_timeout)
        print(f"Listening order/trade events for {args.duration} seconds...")
        deadline = time.monotonic() + args.duration
        interesting = {
            "rsp_order",
            "rsp_order_insert",
            "rsp_order_delete",
            "rtn_order",
            "rsp_match",
            "rtn_match",
        }
        while time.monotonic() < deadline:
            remaining = max(0.1, min(1.0, deadline - time.monotonic()))
            try:
                event = client.raw_events.get(timeout=remaining)
            except queue.Empty:
                continue
            if event.name in interesting:
                print_event(event)
        print("Listening finished.")
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
