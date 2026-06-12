# 易盛启明星 V10 交易 API SDK 分析

## 1. 分析范围与结论

- 官方包目录：`易盛启明星V10交易API_V1.0.1.19-20240118/`
- SDK 版本目录名：`V1.0.1.19-20240118`
- 主头文件目录：`易盛启明星V10交易API_V1.0.1.19-20240118/include/`
- demo 头文件目录：`易盛启明星V10交易API_V1.0.1.19-20240118/esunnyV10-demo/include/`
- Linux 动态库：`易盛启明星V10交易API_V1.0.1.19-20240118/lib/linux/libdstartradeapi.so`
- 看穿式测试密钥库版本：`易盛启明星V10交易API_V1.0.1.19-20240118/lib-看穿式测试密钥库/linux/libdstartradeapi.so`
- 官方 demo：`易盛启明星V10交易API_V1.0.1.19-20240118/esunnyV10-demo/src/`

主 `include/` 与 demo `include/` 下的四个核心头文件 SHA-256 完全一致，可将主 `include/` 作为唯一编译输入。两个 `.so` 的内容和 Build ID 不同，不能混用；默认应链接标准 `lib/linux/libdstartradeapi.so`，仅在明确要求看穿式测试密钥时切换另一版本。

本项目应做成 Linux x86-64 only。不能用 `ctypes` 直接调用 C++ 虚类；应使用 pybind11 编译一个 C++ 扩展，由 C++ 负责实现 SPI、管理厂商对象生命周期、复制回调结构体并安全地转交 Python。

## 最小使用示例

本分析文档面向封装设计。实际 Python SDK 的最小本地加载示例如下，不连接真实交易服务器：

```python
import dstar_trade_py as dstar

print(dstar.get_api_version())
print(dstar.create_and_free_api())
```

同步 client 示例格式：

```python
from dstar_trade_py import DstarTradeClient

client = DstarTradeClient(
    front_ip="61.163.243.173",
    front_port=6668,
    account_no="你的账号",
    password="你的密码",
    app_id="你的APPID",
    license_no="你的AuthCode",
)

try:
    client.connect()
    client.login()
    client.wait_ready(timeout=30)
    print("[示例格式] api_ready:", client.api_ready)
finally:
    client.close()
```

示例中的账号和输出均为格式说明，不代表真实登录或交易结果。

## 2. 官方包结构

```text
易盛启明星V10交易API_V1.0.1.19-20240118/
├── include/
│   ├── DstarTradeApi.h
│   ├── DstarTradeApiDataType.h
│   ├── DstarTradeApiError.h
│   └── DstarTradeApiStruct.h
├── lib/
│   ├── linux/libdstartradeapi.so
│   └── win/...
├── lib-看穿式测试密钥库/
│   ├── linux/libdstartradeapi.so
│   └── win/...
├── esunnyV10-demo/
│   ├── include/                 # 与主 include 内容相同
│   └── src/
│       ├── ApiClient.cpp
│       ├── ApiClient.h
│       ├── UdpClient.cpp
│       ├── UdpClient.h
│       └── main.cpp
├── version.txt
├── V10测试环境.txt
└── 易盛启明星V10交易API使用说明.docx
```

后续构建系统应把整个官方包视为只读 vendor 输入，不格式化、不改名、不补丁修改其中任何文件。

## 3. C++ 类与对象生命周期

### 3.1 SDK 类

`DstarTradeApi.h` 提供两个抽象 C++ class：

| 类 | 作用 |
| --- | --- |
| `IDstarTradeApi` | 主动调用接口。配置连接、初始化、查询、下单和撤单。 |
| `IDstarTradeSpi` | 纯虚回调基类。业务方必须派生并实现全部回调。 |

另有两个 `extern "C"` 工厂函数：

```cpp
IDstarTradeApi *CreateDstarTradeApi();
void FreeDstarTradeApi(IDstarTradeApi *pApiObj);
```

`FreeDstarTradeApi` 明确禁止在任意 SPI 回调中调用。Python 封装必须保证：先停止 Python 事件投递并注销/失效回调目标，再从非回调线程释放 API；扩展对象析构时也要遵守这一规则。

官方 demo 自己定义了 `ApiClient : public IDstarTradeSpi`，它不是 SDK 公共类，只是回调实现示例。

## 4. `IDstarTradeApi` 主动接口

共 22 个虚函数，可按阶段分组如下。

### 4.1 创建后、`Init()` 前配置

| 接口 | 说明 |
| --- | --- |
| `RegisterSpi(IDstarTradeSpi*)` | 注册回调对象。 |
| `RegisterFrontAddress(ip, port)` | 注册 TCP 前置地址。 |
| `SetApiLogPath(path)` | 设置交易数据及工作日志目录；目录必须可用。 |
| `SetLoginInfo(DstarApiReqLoginField*)` | 设置账号、密码、App ID、授权号。 |
| `SetCpuId(recv_cpu, log_cpu)` | 绑定接收线程和日志线程 CPU；`-1` 表示不绑定，日志 CPU 为 `-1` 时不记录交易数据日志。 |
| `SetSubscribeStartId(start_id)` | 通知流起点：`-1` 最新、`0` 从头、正数为指定流号。 |
| `SetRealTimeDataFilter(filter)` | `0` 不过滤；`-1` 过滤 `OnApiReady` 后全部实时数据。 |
| `SetRunMode(mode)` | `0` 满载，`-1` 非满载。 |
| `GetSystemInfo(buf, len, key_version)` | 采集看穿式系统信息。需要调用方提供缓冲区。 |
| `SetSubmitInfo(DstarApiSubmitInfoField*)` | 设置系统采集及软件授权上报信息。 |
| `SetInitQryInfo(DstarApiInitQryInfoField*)` | 控制初始化阶段需要加载的快照种类。demo 未调用，因此使用库默认值。 |
| `Init()` | 启动连接和工作线程。 |

### 4.2 就绪后的业务请求

只有收到 `OnApiReady` 后才能进行后续业务操作。

| 接口 | 请求结构/返回 | 同步返回码 |
| --- | --- | --- |
| `ReqLastClientReqId()` | 无参数，结果由 `OnRspLastReqId` 返回 | `0` 成功；`-1` 未就绪；`-2` 频率超限；`-3` 断线。间隔不小于 5 秒。 |
| `ReqPwdMod(...)` | `DstarApiReqPwdModField` | `0`；`-1` 未就绪；`-2` 断线。 |
| `ReqOrderInsert(...)` | `DstarApiReqOrderInsertField` | `0`；`-1` 未就绪；`-2` 断线。 |
| `ReqOfferInsert(...)` | `DstarApiReqOfferInsertField` | 同上。 |
| `ReqOfferInsertNew(...)` | `DstarApiReqOfferInsertNewField` | 同上。 |
| `ReqOrderDelete(...)` | `DstarApiReqOrderDeleteField` | 同上。 |
| `ReqCmbOrderInsert(...)` | `DstarApiReqCmbOrderInsertField` | 同上。 |
| `ReqQryFund()` | 结果由 `OnRspQryFund` 返回 | `0`；`-1` 未就绪；`-2` 断线；`-3` 小于 1 秒频限；`-4` 上次查询未结束。 |
| `ReqQryPosition()` | 多条 `OnRspQryPosition(..., bLast)` | 与资金查询相同。 |
| `GetApiVersion()` | 返回库版本字符串 | 不适用。 |

同步返回 `0` 仅代表请求被本地 API 接受，不代表交易成功。最终结果必须依据对应应答、委托通知、成交通知中的错误码和状态判断。

## 5. `IDstarTradeSpi` 回调接口

共 39 个纯虚回调。

### 5.1 连接、登录和初始化

| 回调 | 说明 |
| --- | --- |
| `OnFrontDisconnected()` | TCP 连接断开。 |
| `OnRspError(error_code)` | 通用错误应答。 |
| `OnRspUserLogin(login)` | 登录应答；`ErrorCode == 0` 才是成功。 |
| `OnRspPwdMod(result)` | 密码修改应答。 |
| `OnRspSubmitInfo(result)` | 系统信息/授权上报应答。 |
| `OnApiReady(serial_id)` | API 初始化快照完成并可交易；给出后续增量流起点。 |
| `OnRspUdpAuth(result)` | UDP 认证应答。仅 UDP 直发流程需要。 |

### 5.2 初始化快照响应

`OnRspContract`、`OnRspCmbContract`、`OnRspSeat`、`OnRspTrdFeeParam`、`OnRspTrdMarParam`、`OnRspTradeRight`、`OnRspAccountCommList`、`OnRspTrdExchangeState`、`OnRspFund`、`OnRspPrePosition`、`OnRspPosition`、`OnRspOrder`、`OnRspOffer`、`OnRspMatch`、`OnRspCashInOut`。

这些回调在初始化期间建立本地基础数据和账户快照。头文件没有给每条快照回调提供 `bLast`，初始化完成边界由 `OnApiReady` 统一表示。

### 5.3 请求应答

| 回调 | 说明 |
| --- | --- |
| `OnRspOrderInsert` | 报单受理/拒绝应答。 |
| `OnRspOfferInsert` | 报价受理/拒绝应答。 |
| `OnRspOrderDelete` | 撤单受理/拒绝应答。 |
| `OnRspLastReqId` | 返回服务端已见的最新客户请求号。 |
| `OnRspQryPosition(position, bLast)` | 实时持仓查询，多条返回；`bLast=true` 时 `position` 可能为空。 |
| `OnRspQryFund(fund)` | 资金查询响应。该接口没有 `bLast` 参数。 |

### 5.4 实时通知

`OnRtnPwdMod`、`OnRtnOrder`、`OnRtnMatch`、`OnRtnCashInOut`、`OnRtnOffer`、`OnRtnEnquiry`、`OnRtnTrdExchangeState`、`OnRtnPosiProfit`、`OnRtnSeat`、`OnRtnTradeRight`、`OnRtnTradeRightDel`。

撤单失败时，SDK 可能返回状态未变但带失败错误码的 `OnRtnOrder` 或 `OnRtnOffer`，不能只等待 `OnRspOrderDelete`。

## 6. Python 需要映射的结构体

头文件使用 `#pragma pack(push, 1)`，所有结构体均为 1 字节对齐。binding 必须直接包含官方头文件编译，不应在 Python 或另一个头文件中手工复制 ABI 布局。回调指针只保证在回调期间有效，进入队列前必须在 C++ 中按值复制。

### 6.1 配置、登录与认证

- `DstarApiReqLoginField`
- `DstarApiRspLoginField`
- `DstarApiSubmitInfoField`
- `DstarApiRspSubmitInfoField`
- `DstarApiInitQryInfoField`
- `DstarApiReqPwdModField`
- `DstarApiRspPwdModField`
- `DstarApiPwdModField`
- `DstarApiReqUdpAuthField`
- `DstarApiRspUdpAuthField`

### 6.2 基础数据与风控参数

- `DstarApiSeatField`
- `DstarApiContractField`
- `DstarApiCmbContractField`
- `DstarApiTrdExchangeStateField`
- `DstarApiTrdFeeParamField`
- `DstarApiTrdMarParamField`
- `DstarApiTradeRightField`
- `DstarApiTradeRightDelField`
- `DstarApiAccountCommListField`

### 6.3 账户、委托、成交和通知

- `DstarApiOrderField`
- `DstarApiOfferField`
- `DstarApiEnquiryField`
- `DstarApiMatchField`
- `DstarApiPrePositionField`
- `DstarApiPositionField`
- `DstarApiFundField`
- `DstarApiCashInOutField`
- `DstarApiPosiProfitField`
- `DstaApiRspLastReqIdField`：官方名称中是 `Dsta`，封装时应保留 C++ 名字，但 Python 可暴露为正确拼写的 `LastReqIdResponse`。

### 6.4 交易请求和应答

- `DstarApiReqOrderInsertField`
- `DstarApiReqOfferInsertField`
- `DstarApiReqOfferInsertNewField`
- `DstarApiReqOrderDeleteField`
- `DstarApiReqCmbOrderInsertField`
- `DstarApiRspOrderInsertField`
- `DstarApiRspOrderDeleteField`：`DstarApiRspOrderInsertField` 的 typedef 别名。
- `DstarApiRspOfferInsertField`：`DstarApiRspOrderInsertField` 的 typedef 别名。
- `DstarApiHead`：只用于 demo 自行构造 UDP 协议帧；高层 TCP Python API 不必公开，若以后支持低延迟 UDP 可放入独立的 advanced 模块。

总计 36 个具名 `struct`，另有 2 个应答 typedef 别名。第一版 Python SDK 至少应完整映射所有 TCP 公共接口直接涉及的请求、应答和回调结构；UDP 帧头可延后。

### 6.5 字段映射规则

- 固定 `char[N]`：C++ 边界上做长度检查、NUL 终止和编码转换；Python 暴露 `str`，原始字节可按需另暴露 `bytes`。
- 单字符代码：Python 使用 `str` 枚举，而不是裸整数。
- `unsigned long long`/`long long`：映射 Python `int`。
- `double`：映射 Python `float`；金额和价格保持厂商原始 double 语义，不在 binding 层擅自改成 Decimal。
- 匿名 union：提供语义化属性。`DstarApiOfferField` 的 `OrderQty/BuyOrderQty` 和 `DstarApiMatchField` 的 `Premium/CloseProfit` 共用内存，不能当作两个独立值。
- 结构体输入：优先提供 Python dataclass/普通类，再由 C++ 显式填充官方结构体并做边界校验；不要让用户操作原始 packed memory。

## 7. 数据类型与枚举

`DstarTradeApiDataType.h` 定义了 90 个命名常量。建议按语义映射为 Python `Enum`/`IntEnum`，至少包括：

- `Exchange`：ZCE、SHFE、INE、CFFEX、DCE、GFEX、SGE。
- `CommodityType`：期货、期权、跨期、跨品种、跨式、宽跨式、备兑、无。
- `Direction`：买、卖、所有。
- `Offset`：开、平、平今。
- `Hedge`：投机、套保。
- `OrderType`：市价、限价、行权、弃权、询价、报价、互换、期转现等。
- `ValidType`：FOK、IOC、GFD、GIS。
- `OrderState`：受理、排队、申请、挂起、触发、部分成交、完全成交、失败、撤单、撤余、系统删除、策略待触发。
- `TradeRight`、`TradingState`、`CashInOutType`、`CashInOutMode`、`AuthType`、`StartMode`、`SeatState`、`YesNo`。
- 配置常量：订阅位置、实时过滤器、运行模式、初始化模式、请求号模式、报价顶单模式。

保留原始代码值非常重要，因为日志、错误排查和交易所文档都使用这些字符或整数代码。

## 8. 错误码封装

### 8.1 头文件正式声明的错误码

`DstarTradeApiError.h` 正式声明 78 个 `DstarApiErrorCodeType` 常量：

- `0`：`DSTAR_API_ERR_SUCCESS`。
- `10001-10009`：连接、登录前状态、订阅、收发、解析、缓冲区和心跳错误。
- `20001-20053`：认证、账户、请求字段、权限、资金、频率、授权、撤单、合约、价格、容量、自成交、出入金和登录权限等业务错误。
- `30001-30012`：席位频率、发送、本地号、行权/弃权/组合支持、初始化状态、线程和询价撤销错误。
- `60001-60003`：策略单异常、无效策略单、无行情。

需要注意头文件中的两个拼写错误也属于 ABI/API 名称：

- `DSATR_API_ERR_DATA_PROCESS = 10007`
- `DSATR_API_ERR_BUFF_OVERFLOW = 10008`
- `DSATR_API_ERR_HB_TIMEOUT = 10009`

Python 层建议提供纠正拼写的枚举成员，同时保留原始名称别名以便排查。例如 `DATA_PROCESS = 10007` 和 `DSATR_API_ERR_DATA_PROCESS = 10007`。

错误枚举应覆盖全部 78 个常量，而不是只覆盖 demo 会遇到的错误。按头文件顺序生成常量表比手工维护更可靠。

### 8.2 同步调用错误

`Init()`、`GetSystemInfo()` 和各 `Req*()` 返回的负整数不是 `DstarApiErrorCodeType`，必须单独封装为 `ApiCallError`/`InitError`，不能与 10001 以上的异步业务错误混在一个枚举中。

特别是：

- `GetSystemInfo()`：`-1` 至 `-9` 为不同系统信息采集失败。
- `Init()`：`-3` 已创建连接、`-4` socket 创建失败、`-5` 连接失败；`-11` 至 `-19` 为系统信息采集失败。
- 查询接口还有频率超限和上次查询未结束等本地返回码。

### 8.3 交易所透传错误

错误头文件后半部分还列出大量郑商所、上期所、能源中心、中金所、大商所等交易所错误码说明。这些不是 `const` 声明，编码空间也可能随交易所升级变化。封装策略应为：

1. 对官方声明的 78 个 API 错误提供稳定 `IntEnum` 和文字说明。
2. 对交易所错误建立可更新的 `dict[int, str]` 查询表。
3. 未知错误码必须保留原始整数并显示 `Unknown exchange/API error`，不能抛弃或强制转换失败。
4. 应答和通知对象同时暴露 `error_code` 与 `error_message`。

## 9. Linux 动态库与 ABI

### 9.1 文件属性

- 格式：ELF 64-bit LSB shared object。
- 架构：x86-64。
- 动态链接，未 strip。
- 标准库 Build ID：`8fa838e0e3b108879592edfdd600fbed53919fd4`。
- 标准库 SHA-256：`f51029afb4b1b44694fa7bd0cba997cc8db06b204c6b2652c6ab3f4fbc496ad5`。
- 看穿式测试密钥库 SHA-256：`11584813f695a6db6d4952396fc3f1574725fd4dd256030f645171e8804dd175`。
- 无 `SONAME`、`RPATH` 或 `RUNPATH` 条目。

### 9.2 `DT_NEEDED` 依赖

```text
libpthread.so.0
librt.so.1
libstdc++.so.6
libm.so.6
libgcc_s.so.1
libc.so.6
```

当前 Ubuntu x86-64 环境中 `ldd` 可解析全部依赖。版本符号显示最低/最高可见要求包括 `GLIBC_2.14`、`GLIBCXX_3.4`、`CXXABI_1.3` 和 `GCC_3.0`，说明该库使用较老的 libstdc++ ABI，兼容面相对宽，但发布 wheel 前仍需在目标 manylinux 基线上实际加载验证。

### 9.3 构建和分发建议

- pybind11 扩展直接链接标准 `.so`。
- wheel 内可放在 `dstar_trade_py/.libs/libdstartradeapi.so`，扩展设置相对 `RPATH=$ORIGIN/.libs` 或使用 wheel 修复工具校正加载路径。
- 不把两个同名厂商库同时打进同一个 wheel。测试密钥版本应使用单独构建产物或显式构建选项。
- 构建时校验厂商库 SHA-256，避免误链接。
- 运行时检查 `platform.system() == "Linux"`、机器架构为 `x86_64/AMD64`，并在导入错误中给出明确诊断。
- `GetSystemInfo`/`Init` 可能需要读取 DMI 信息或执行 `dmidecode`、`lshw`；非 root 部署要预先配置对应权限，不能在 Python SDK 中自动提权。

## 10. 官方 demo 流程

### 10.1 初始化与登录

`ApiClient` 的流程为：

1. `CreateDstarTradeApi()` 创建 API，并调用 `GetApiVersion()` 打印版本。
2. `SetAddress()` 保存前置 IP/端口。
3. `SetUser()` 填充 `DstarApiReqLoginField` 的账号、密码、App ID、授权号。
4. `RegisterSpi(this)` 注册回调。
5. `RegisterFrontAddress()` 设置 TCP 地址。
6. `SetApiLogPath()` 设置日志目录；Linux demo 硬编码为 `/home/esunny/apidemo/`，Python SDK 必须改为用户可配置目录。
7. `SetLoginInfo()` 设置登录信息。
8. `SetCpuId(0, 1)` 绑定接收和日志线程。
9. `SetSubscribeStartId(-1)` 从最新通知开始订阅。
10. `GetSystemInfo()` 获取系统信息和密钥版本。
11. 构造 `DstarApiSubmitInfoField`：账号、直连授权类型、密钥版本、系统信息、License No、Client App ID，然后调用 `SetSubmitInfo()`。
12. 调用 `Init()`。
13. SDK 异步触发 `OnRspSubmitInfo`、`OnRspUserLogin`、初始化快照回调，最终触发 `OnApiReady`。
14. demo 轮询 `IsReady()`；只有 `OnApiReady` 将其置为 `true`。

登录成功本身不等于 API ready。Python SDK 应分别建模 `connected`、`logged_in`、`ready`、`disconnected/closed` 状态。

### 10.2 查询

头文件提供 `ReqQryFund()` 和 `ReqQryPosition()`，但 `main.cpp` 没有实际调用查询接口。对应实现只在 `ApiClient` 中打印：

- 资金查询：一次 `OnRspQryFund`。
- 持仓查询：零到多次 `OnRspQryPosition`，以 `bLast=true` 结束，且最后一条的结构体指针可能为空。

此外，初始化阶段默认会收到资金、昨持仓、实时持仓、委托、报价、成交等快照；它们与显式查询回调不同。

### 10.3 TCP 下单

`TcpInsertOrder()` 清零 `DstarApiReqOrderInsertField` 后填充：方向、开平、投保、委托类型、有效类型、引用号、席位索引、账户索引、客户请求号、合约索引与合约号、数量、价格和最小成交量，最后调用 `ReqOrderInsert()`。

TCP 请求无需填写 `UdpAuthCode`。结果链路通常为：

1. `ReqOrderInsert()` 同步返回本地接收结果。
2. `OnRspOrderInsert()` 返回请求号、委托号、最大请求号及错误码。
3. `OnRtnOrder()` 推送委托状态变化。
4. 成交时 `OnRtnMatch()` 推送成交，并伴随后续委托状态更新。

### 10.4 TCP 撤单

`TcpDeleteOrder()` 填充账户索引、递增的客户请求号和引用号、席位索引、原委托 `OrderId`，可选填写 `SystemNo`，然后调用 `ReqOrderDelete()`。TCP 同样不填 `UdpAuthCode`。

撤单结果需要同时观察 `OnRspOrderDelete()` 与 `OnRtnOrder()`/`OnRtnOffer()`。demo 中实际撤单调用被注释，只展示了构造方式。

### 10.5 其他 TCP 请求

demo 还展示：

- 询价：复用 `DstarApiReqOrderInsertField`，`OrderType=ENQUIRY`、`Direct=ALL`。
- 旧报价：`ReqOfferInsert()`。
- 新报价：`ReqOfferInsertNew()`，支持买卖不同数量及 `ReplaceId` 顶单语义。
- 行权/弃权：复用报单结构并设置对应 `OrderType`。
- 组合报单：`ReqCmbOrderInsert()`，填写两腿合约索引和合约号。

### 10.6 UDP 流程

demo 默认 `udp_or_tcp = 0`，会额外创建 `TUdpClient`，在 API ready 后使用登录返回的 `AccountIndex` 和 `UdpAuthCode` 发送 `DstarApiReqUdpAuthField`，等待 `OnRspUdpAuth` 成功，再自行拼装 packed 协议帧发送报单。

UDP 路径绕过 `IDstarTradeApi::Req*` 的 TCP 发送函数，复杂度和风险明显更高。第一版 Python SDK 建议只封装厂商 `IDstarTradeApi` 提供的 TCP API；UDP 作为后续独立、显式 opt-in 的低延迟模块，不与普通客户端混合。

## 11. 建议的 Python SDK 架构

```text
dstar_trade_py/
├── pyproject.toml
├── CMakeLists.txt
├── cmake/
├── src/
│   ├── binding/
│   │   ├── module.cpp              # pybind11 模块入口
│   │   ├── trade_api.cpp           # IDstarTradeApi RAII 包装
│   │   ├── trade_spi.cpp           # IDstarTradeSpi 完整实现
│   │   ├── converters.cpp          # packed struct <-> Python 值对象
│   │   └── callback_queue.cpp      # C++ 回调复制和有界队列
│   └── dstar_trade_py/
│       ├── __init__.py
│       ├── client.py               # 高层同步客户端/状态机
│       ├── async_client.py         # asyncio 适配，不直接跑厂商线程
│       ├── models.py               # dataclass 响应和请求模型
│       ├── enums.py                # 业务字符枚举
│       ├── errors.py               # API、同步调用、交易所错误
│       └── events.py               # 回调事件类型与订阅接口
├── vendor/                         # 可用路径配置或受控打包，不改官方内容
├── tests/
│   ├── unit/
│   ├── abi/
│   └── integration/
└── docs/
```

### 11.1 C++ binding 层职责

- `TradeApiHandle` 用 RAII 管理 `CreateDstarTradeApi`/`FreeDstarTradeApi`。
- `TradeSpiAdapter` 实现全部 39 个纯虚函数，不能遗漏空实现，否则无法实例化。
- 每个回调立即检查空指针、按值复制 packed struct，生成内部事件后快速返回。
- 厂商线程不直接执行耗时 Python 用户代码。使用有界 C++ 队列和单独 dispatcher 线程；进入 Python 前获取 GIL。
- 所有主动调用在进入可能阻塞的厂商函数时考虑释放 GIL，但对象生命周期和关闭互斥必须先锁定。
- Python 异常不能穿过 C++/厂商回调边界；应捕获、记录并转为客户端错误事件。
- `close()` 幂等，且禁止从 dispatcher 正在执行的厂商回调栈内释放 API。

### 11.2 Python 高层 API

建议公开一个主要入口 `TradeClient`：

```python
client = TradeClient(config)
client.start()
client.wait_ready(timeout=30)
order_ref = client.insert_order(order)
fund = client.query_fund(timeout=3)
positions = client.query_positions(timeout=3)
client.cancel_order(order_id=..., system_no=...)
client.close()
```

高层层负责：

- 显式状态机和超时。
- 自动生成线程安全、单调递增的 `ClientReqId` 与 `Reference`，同时允许高级用户覆盖。
- 将同步负返回码立即抛为调用异常。
- 用 `ClientReqId`、`Reference`、`OrderId` 关联应答与实时通知。
- 将持仓多条回调聚合到 `bLast`。
- 提供原始事件订阅，避免高层抽象丢失厂商字段。
- 对密码等敏感字段做 `repr=False`，日志中禁止输出明文。

### 11.3 线程、背压和可靠性

- 交易通知不能使用无界队列，避免 Python 消费变慢导致内存无限增长。
- 订单、成交、断线等关键事件不能静默丢弃；队列满时应记录致命状态并要求上层重建快照。
- 市场状态、浮盈等可合并事件可采用最新值覆盖策略，但策略必须可配置并有指标。
- `OnApiReady(serial_id)` 的流号应暴露并持久化，供断线重连和增量一致性检查使用。
- 可周期调用 `ReqLastClientReqId()` 检测报撤单丢包，但必须遵守至少 5 秒频率限制。

### 11.4 第一阶段建议范围

第一阶段只实现 Linux x86-64、TCP 模式和官方标准库：

1. API 生命周期、登录、系统信息上报、ready 状态。
2. 初始化快照和全部实时回调的无损映射。
3. 资金/持仓查询。
4. 普通报单、撤单、委托与成交通知。
5. 错误码、枚举、长度校验、线程安全和关闭流程。

报价、新报价、组合单、密码修改可在同一 ABI 基础上随后补齐；原始 UDP 组帧不进入第一阶段核心接口。

## 12. 关键风险

- 厂商接口是 C++ virtual ABI，必须用同 ABI 的 C++ 编译器链链接，不能用 ctypes 模拟 vtable。
- 所有 struct 都是 packed(1)，匿名 union 和固定字符数组容易产生错误映射。
- 回调来自厂商线程，指针生命周期短；跨线程前必须复制。
- 登录成功和 API ready 是两个不同阶段。
- 同步 `Req*` 返回成功不等于业务成功。
- 撤单失败可能通过委托/报价通知体现。
- 厂商库无 SONAME/RPATH，wheel 必须主动管理动态库定位。
- 两个同名 `.so` 不同，必须固定选择并校验哈希。
- 系统信息采集涉及 Linux 主机权限，容器环境尤其需要部署前验证。
- 官方 demo 含硬编码测试账号、地址和日志目录，只能作为流程参考，不能直接进入 Python SDK 默认配置。
