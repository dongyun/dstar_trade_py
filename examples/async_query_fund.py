"""使用 AsyncDstarTradeClient 异步查询资金的示例。

本示例会连接真实交易前置，请只在确认网络、账号、授权信息和交易环境后运行。
所有敏感参数都从环境变量读取，避免把真实账号或密码写入仓库。
"""

from __future__ import annotations

import asyncio

from dstar_trade_py import AsyncDstarTradeClient
from live_common import exit_with_error, load_config, print_config_summary


async def main() -> None:
    """连接、登录、等待 API 就绪，然后查询资金。"""

    config = load_config()
    print_config_summary(config)
    client = AsyncDstarTradeClient(
        front_ip=config.trade_ip,
        front_port=config.trade_port,
        account_no=config.user,
        password=config.password,
        app_id=config.app_id,
        license_no=config.auth_code,
        api_log_path=config.log_path,
    )

    try:
        await client.connect()
        await client.login()
        await client.wait_ready(timeout=30)
        fund = await client.query_fund(timeout=5)
        print(fund)
    except BaseException as exc:
        exit_with_error(exc)
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
