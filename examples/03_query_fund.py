"""真实测试：查询资金。"""

from __future__ import annotations

import argparse

from live_common import connect_login_ready, exit_with_error, print_value


def main() -> None:
    """登录并等待就绪后，请求资金快照。"""

    parser = argparse.ArgumentParser(description="Dstar live query-fund demo")
    parser.add_argument("--ready-timeout", type=float, default=30, help="等待 api_ready 的超时")
    parser.add_argument("--query-timeout", type=float, default=5, help="等待资金响应的超时")
    args = parser.parse_args()

    client = None
    try:
        client = connect_login_ready(timeout=args.ready_timeout)
        fund = client.query_fund(timeout=args.query_timeout)
        print("Fund:")
        print_value(fund)
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
