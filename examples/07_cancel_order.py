"""真实测试：撤单 demo。

默认 dry-run，不发送真实撤单。必须传入 --confirm-live-order 并手工输入 YES 才会撤单。
"""

from __future__ import annotations

import argparse

from live_common import (
    confirm_live_order,
    connect_login_ready,
    exit_with_error,
    latest_login_response,
    next_client_req_id,
)


def main() -> None:
    """打印撤单参数，经过二次确认后提交撤单请求。"""

    parser = argparse.ArgumentParser(description="Dstar live cancel order demo")
    parser.add_argument("--ready-timeout", type=float, default=30, help="等待 api_ready 的超时")
    parser.add_argument("--order-id", type=int, required=True, help="要撤销的委托号")
    parser.add_argument("--system-no", default="", help="系统号，按柜台要求填写")
    parser.add_argument("--account-index", type=int, help="账号索引，默认使用登录应答返回值")
    parser.add_argument("--client-req-id", type=int, help="客户请求号，默认查询最新请求号后加一")
    parser.add_argument("--udp-auth-code", type=int, help="UDP 认证码，默认使用登录应答返回值")
    parser.add_argument("--reference", type=int, default=0, help="报单引用")
    parser.add_argument("--seat-index", type=int, default=0, help="席位索引")
    parser.add_argument(
        "--confirm-live-order",
        action="store_true",
        help="显式允许发送真实撤单请求；仍需输入 YES 二次确认",
    )
    args = parser.parse_args()

    client = None
    try:
        client = connect_login_ready(timeout=args.ready_timeout)
        login = latest_login_response(client)
        account_index = args.account_index
        udp_auth_code = args.udp_auth_code
        if login is not None:
            account_index = login.AccountIndex if account_index is None else account_index
            udp_auth_code = login.UdpAuthCode if udp_auth_code is None else udp_auth_code
        if account_index is None:
            raise RuntimeError("Missing --account-index and no login AccountIndex is available")
        if udp_auth_code is None:
            raise RuntimeError("Missing --udp-auth-code and no login UdpAuthCode is available")

        client_req_id = args.client_req_id
        if client_req_id is None:
            client_req_id = next_client_req_id(client)

        cancel_params = {
            "account_index": account_index,
            "client_req_id": client_req_id,
            "order_id": args.order_id,
            "system_no": args.system_no,
            "udp_auth_code": udp_auth_code,
            "reference": args.reference,
            "seat_index": args.seat_index,
        }
        if not confirm_live_order("Cancel order", cancel_params, args.confirm_live_order):
            return

        ret = client.cancel_order(**cancel_params)
        print(f"ReqOrderDelete local return code: {ret}")
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
