"""真实测试：连接并等待登录应答。

运行前请先按 docs/live_testing.md 设置环境变量。本 demo 不会下单，只验证登录流程。
"""

from __future__ import annotations

import argparse

from live_common import (
    exit_with_error,
    load_config,
    make_client,
    print_config_summary,
    print_event,
    raise_login_error,
    wait_for_event,
)


def main() -> None:
    """连接交易前置，调用 Init，并等待 rsp_user_login。"""

    parser = argparse.ArgumentParser(description="Dstar live login demo")
    parser.add_argument("--timeout", type=float, default=30, help="等待登录应答的超时时间")
    args = parser.parse_args()

    client = None
    try:
        config = load_config()
        print_config_summary(config)
        client = make_client(config)
        client.connect()
        client.login()
        event = wait_for_event(client, {"rsp_user_login", "rsp_error"}, args.timeout)
        print_event(event)
        if event.name == "rsp_user_login":
            raise_login_error(event.data)
            print("Login succeeded.")
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
