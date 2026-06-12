# 真实测试 Demo 说明

本文档说明如何运行 `examples/` 下的真实测试 demo。所有 demo 都只从环境变量读取账号、
密码和授权信息；仓库中不得写入真实账号密码。

## 申请模拟账号

请向易盛或对应期货公司申请启明星 V10 内盘交易 API 模拟测试账号，并确认账号允许使用
看穿式采集授权。官方测试环境信息：

- `AuthCode`: `Demo_TestCollect`
- `APPID`: `Demo_TestCollect`
- 交易 IP: `61.163.243.173` 或 `123.161.206.213`
- UDP 下单端口: `6666`
- TCP 查询通知端口: `6668`

当前 SDK 的 `RegisterFrontAddress` 使用 TCP 查询通知端口，因此通常应把
`DSTAR_TRADE_PORT` 设置为 `6668`。报单请求中的 UDP 认证码由登录应答返回，demo 会优先
使用登录应答中的 `UdpAuthCode`。

## 环境变量

运行 demo 前设置以下变量：

```bash
export DSTAR_TRADE_IP=61.163.243.173
export DSTAR_TRADE_PORT=6668
export DSTAR_TRADE_USER=你的模拟账号
export DSTAR_TRADE_PASSWORD=你的模拟密码
export DSTAR_TRADE_AUTH_CODE=Demo_TestCollect
export DSTAR_TRADE_APP_ID=Demo_TestCollect
export DSTAR_TRADE_LOG_PATH=/tmp/dstar_trade_py
```

不要把上述真实账号和密码提交到 git。建议使用本机 shell profile、direnv 的私有文件、
CI secret 或临时 shell export。

## 运行顺序

建议按以下顺序逐步验证：

```bash
.venv/bin/python examples/01_login.py
.venv/bin/python examples/02_wait_ready.py
.venv/bin/python examples/03_query_fund.py
.venv/bin/python examples/04_query_position.py
.venv/bin/python examples/05_subscribe_order_trade_events.py --duration 120
```

如果登录失败，先检查账号、密码、`APPID`、`AuthCode`、IP、端口和本机网络连通性。
账号、密码、AuthCode、APPID、journal 和日志脱敏要求见 [`security.md`](security.md)。
如果 `wait_ready` 超时，不要继续运行下单或撤单 demo。

## 下单 Dry Run

下单 demo 默认不会发送真实请求，只打印订单参数：

```bash
.venv/bin/python examples/06_insert_limit_order.py \
  --contract-no rb2410 \
  --contract-index 12345 \
  --direction buy \
  --offset open \
  --price 3000 \
  --qty 1
```

只有同时满足以下条件才会真实下单：

- 显式传入 `--confirm-live-order`
- demo 打印订单参数后，手工输入 `YES`

示例：

```bash
.venv/bin/python examples/06_insert_limit_order.py \
  --contract-no rb2410 \
  --contract-index 12345 \
  --direction buy \
  --offset open \
  --price 3000 \
  --qty 1 \
  --confirm-live-order
```

## 撤单 Dry Run

撤单 demo 同样默认 dry-run：

```bash
.venv/bin/python examples/07_cancel_order.py --order-id 10001
```

真实撤单必须传入 `--confirm-live-order` 并输入 `YES`：

```bash
.venv/bin/python examples/07_cancel_order.py \
  --order-id 10001 \
  --system-no 交易系统号 \
  --confirm-live-order
```

## 修改密码 Demo

修改密码是高风险操作，默认不会发送请求：

```bash
.venv/bin/python examples/08_modify_password_demo.py
```

真实修改密码必须传入 `--confirm-live-password-change` 并输入 `YES`。新密码可以通过
`--new-password` 传入，也可以由 demo 交互输入。不要在 shell history 中长期保留真实密码。

## 风险提示

- demo 面向模拟测试环境，但仍会连接真实网络服务。
- 下单、撤单、改密属于有副作用操作。未确认合约、价格、数量、账号索引、请求号前不要
  传入确认参数。
- `insert_order` 返回的是本地请求返回码，不代表交易所已接收、已成交或最终成功。后续状态
  需要通过 `05_subscribe_order_trade_events.py` 或客户端事件队列观察。
- 不要在单元测试中连接真实交易服务器；真实环境验证只放在 `examples/` 下手动运行。
