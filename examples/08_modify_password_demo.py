"""真实测试：修改密码 demo。

修改密码属于高风险操作。默认 dry-run；必须传入 --confirm-live-password-change 并输入 YES。
"""

from __future__ import annotations

import argparse
import getpass

from live_common import connect_login_ready, exit_with_error


def main() -> None:
    """经过二次确认后提交密码修改请求。"""

    parser = argparse.ArgumentParser(description="Dstar live modify-password demo")
    parser.add_argument("--ready-timeout", type=float, default=30, help="等待 api_ready 的超时")
    parser.add_argument("--new-password", help="新密码；不传则交互输入")
    parser.add_argument(
        "--confirm-live-password-change",
        action="store_true",
        help="显式允许发送真实改密请求；仍需输入 YES 二次确认",
    )
    args = parser.parse_args()

    client = None
    try:
        if not args.confirm_live_password_change:
            print("dry_run=True. No live password-change request was sent.")
            print("Pass --confirm-live-password-change and type YES to send this request.")
            return
        new_password = args.new_password or getpass.getpass("New password: ")
        print("WARNING: this will send a real password-change request.")
        answer = input("Type YES to confirm: ")
        if answer != "YES":
            print("Confirmation failed. No live password-change request was sent.")
            return

        client = connect_login_ready(timeout=args.ready_timeout)
        ret = client.modify_password(new_password=new_password, old_password=client.password)
        print(f"ReqPwdMod local return code: {ret}")
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        if client is not None:
            client.close()


if __name__ == "__main__":
    main()
