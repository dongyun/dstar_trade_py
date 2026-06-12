"""真实测试：登录后等待 API 就绪。

收到 api_ready 后，才允许进行查询、下单、撤单等业务请求。
"""

from __future__ import annotations

import argparse

from live_common import connect_login_ready, exit_with_error


def main() -> None:
    """连接、登录并等待 api_ready。"""

    parser = argparse.ArgumentParser(description="Dstar live wait-ready demo")
    parser.add_argument("--timeout", type=float, default=30, help="等待 api_ready 的超时时间")
    args = parser.parse_args()

    client = None
    try:
        client = connect_login_ready(timeout=args.timeout)
        print(
            "State: "
            f"connected={client.connected}, logged_in={client.logged_in}, "
            f"api_ready={client.api_ready}, disconnected={client.disconnected}"
        )
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
