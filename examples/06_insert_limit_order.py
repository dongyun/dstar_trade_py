"""真实测试：限价下单 demo。

默认 dry-run，不发送真实下单。必须传入 --confirm-live-order 并手工输入 YES 才会下单。
"""

from __future__ import annotations

import argparse

from live_common import (
    DEFAULT_VALID_TYPE,
    confirm_live_order,
    connect_login_ready,
    exit_with_error,
    latest_login_response,
    next_client_req_id,
    order_direction,
    order_hedge,
    order_offset,
    positive_int,
)


def main() -> None:
    """打印订单参数，经过二次确认后提交限价单。"""

    parser = argparse.ArgumentParser(description="Dstar live insert limit order demo")
    parser.add_argument("--ready-timeout", type=float, default=30, help="等待 api_ready 的超时")
    parser.add_argument("--contract-no", required=True, help="合约编号，例如 rb2410")
    parser.add_argument("--contract-index", type=int, required=True, help="合约索引")
    parser.add_argument("--direction", type=order_direction, required=True, help="buy 或 sell")
    parser.add_argument("--offset", type=order_offset, required=True, help="open/close/close_today")
    parser.add_argument("--price", type=float, required=True, help="限价价格")
    parser.add_argument("--qty", type=positive_int, required=True, help="下单手数")
    parser.add_argument("--account-index", type=int, help="账号索引，默认使用登录应答返回值")
    parser.add_argument("--client-req-id", type=int, help="客户请求号，默认查询最新请求号后加一")
    parser.add_argument("--udp-auth-code", type=int, help="UDP 认证码，默认使用登录应答返回值")
    parser.add_argument("--seat-index", type=int, default=0, help="席位索引，0 表示轮询")
    parser.add_argument("--min-qty", type=positive_int, default=1, help="最小成交量")
    parser.add_argument("--reference", type=int, default=0, help="报单引用")
    parser.add_argument(
        "--hedge",
        type=order_hedge,
        default=order_hedge("speculate"),
        help="speculate 或 hedge",
    )
    parser.add_argument(
        "--confirm-live-order",
        action="store_true",
        help="显式允许发送真实下单请求；仍需输入 YES 二次确认",
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

        order_params = {
            "direct": args.direction,
            "offset": args.offset,
            "hedge": args.hedge,
            "valid_type": DEFAULT_VALID_TYPE,
            "account_index": account_index,
            "contract_index": args.contract_index,
            "contract_no": args.contract_no,
            "order_qty": args.qty,
            "order_price": args.price,
            "client_req_id": client_req_id,
            "seat_index": args.seat_index,
            "min_qty": args.min_qty,
            "reference": args.reference,
            "udp_auth_code": udp_auth_code,
        }
        if not confirm_live_order("Insert limit order", order_params, args.confirm_live_order):
            return

        ret = client.insert_limit_order(**order_params)
        print(f"ReqOrderInsert local return code: {ret}")
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
