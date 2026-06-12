"""使用 AsyncDstarTradeClient 异步查询资金的示例。

本示例会连接真实交易前置，请只在确认网络、账号、授权信息和交易环境后运行。
所有敏感参数都从环境变量读取，避免把真实账号或密码写入仓库。
"""

from __future__ import annotations

import asyncio
import os

from dstar_trade_py import AsyncDstarTradeClient


def require_env(name: str) -> str:
    """读取必填环境变量；缺失时给出明确错误。"""

    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def main() -> None:
    """连接、登录、等待 API 就绪，然后查询资金。"""

    client = AsyncDstarTradeClient(
        front_ip=require_env("DSTAR_TRADE_FRONT_IP"),
        front_port=int(require_env("DSTAR_TRADE_FRONT_PORT")),
        account_no=require_env("DSTAR_TRADE_ACCOUNT_NO"),
        password=require_env("DSTAR_TRADE_PASSWORD"),
        app_id=require_env("DSTAR_TRADE_APP_ID"),
        license_no=require_env("DSTAR_TRADE_LICENSE_NO"),
        api_log_path=os.environ.get("DSTAR_TRADE_API_LOG_PATH", "/tmp/dstar_trade_py"),
    )

    try:
        await client.connect()
        await client.login()
        await client.wait_ready(timeout=float(os.environ.get("DSTAR_TRADE_READY_TIMEOUT", "30")))
        fund = await client.query_fund(
            timeout=float(os.environ.get("DSTAR_TRADE_QUERY_TIMEOUT", "5"))
        )
        print(fund)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
