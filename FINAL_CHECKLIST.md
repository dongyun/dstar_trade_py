# dstar_trade_py 最终验收清单

验收日期：2026-06-12

## 结论

`dstar_trade_py` 当前满足 Linux-only Python SDK 的阶段性验收要求：native binding、主动接口覆盖、SPI 回调覆盖、字段映射、结构体转换、同步/异步 client、订单状态、幂等保护、live demo 安全保护、测试分层和文档体系均已落地。

真实交易 live tests 在当前环境未设置 `DSTAR_RUN_LIVE_TESTS=1` 和真实账号环境变量，因此按设计全部 skip，没有伪造通过结果。

## 验收项目

| # | 项目 | 状态 | 验收证据 |
| ---: | --- | --- | --- |
| 1 | 项目只支持 Linux | 通过 | `CMakeLists.txt` 非 Linux `FATAL_ERROR`；Python 非 Linux 仅允许 import，创建 native API 抛 Linux-only 错误；`check_env.sh` 检查 Linux。 |
| 2 | 完整代理 `IDstarTradeApi` 所有主动接口 | 通过 | `tests/unit/test_api_coverage.py` 解析官方头文件并检查 24 项接口/工厂函数；unit tests 通过。 |
| 3 | 完整代理 `IDstarTradeSpi` 所有回调接口 | 通过 | `tests/unit/test_callback_coverage.py` 解析官方头文件，确认 39 个回调均声明、定义并进入统一 dispatcher。 |
| 4 | 所有 C++ 结构体都有 Python 映射 | 通过 | `tests/unit/test_fields.py` 解析 `DstarTradeApiStruct.h`，确认 36 个 named struct 与字段顺序完全映射；响应 alias 映射为同一模型。 |
| 5 | 结构体转换安全，不暴露悬空指针 | 通过 | `cpp/field_converters.cpp` 对固定 char 数组做 bounded NUL scan + UTF-8 replace；回调栈内立即复制为 Python dict；`test_field_converters.py` 覆盖 null、invalid UTF-8、未 NUL 结尾。 |
| 6 | 回调正确获取 GIL | 通过 | `PyTradeSpiAdapter::dispatch_event` 使用 `py::gil_scoped_acquire gil`；静态测试验证。 |
| 7 | 回调异常被捕获 | 通过 | `dispatch_event` 捕获 `py::error_already_set`、`std::exception` 和 unknown exception，且 `noexcept`；`test_callback_dispatch.py` 覆盖 Python callback 抛异常。 |
| 8 | `NativeTradeApi` 生命周期安全 | 通过 | 构造调用 `CreateDstarTradeApi()`；析构调用 `FreeDstarTradeApi()`；禁用 copy/move；Python 不持有裸 `IDstarTradeApi*`。 |
| 9 | 内存泄露风险检查 | 通过，有残余外部风险 | C++ 使用 RAII 和 `std::unique_ptr` 管理 SPI；临时 API 使用 `unique_ptr` deleter。残余风险来自 vendor SDK 如果在 `FreeDstarTradeApi` 后仍异步回调，项目已避免在 SPI 回调中释放 API。 |
| 10 | 下单 demo 默认 dry-run | 通过 | `examples/06_insert_limit_order.py` 和 `examples/07_cancel_order.py` 必须传 `--confirm-live-order` 且输入 `YES`；`examples/08_modify_password_demo.py` 同样默认 dry-run。 |
| 11 | 未提交真实账号密码 | 通过 | 代码扫描只发现环境变量名、中文占位符、公开测试环境 `Demo_TestCollect`、测试假值 `demo-password/secret`；无真实账号密码。 |
| 12 | pytest unit | 通过 | `./scripts/run_tests.sh unit`：`96 passed, 7 deselected`。 |
| 12 | pytest integration | 通过 | `./scripts/run_tests.sh integration`：`3 passed, 100 deselected`。 |
| 12 | pytest live | 通过 skip 语义 | `./scripts/run_tests.sh live`：`4 skipped`，原因均为未设置 `DSTAR_RUN_LIVE_TESTS=1`。 |
| 12 | 默认 pytest | 通过 | `.venv/bin/python -m pytest -q`：`99 passed, 4 deselected`。 |
| 13 | 文档完整性 | 通过 | `README.md` 链接全部 docs；本地 Markdown 链接检查通过：`checked 16 markdown files; all local links exist`。 |
| 14 | 生成最终清单 | 通过 | 本文件。 |

## 实际运行结果

### Unit Tests

```text
./scripts/run_tests.sh unit
96 passed, 7 deselected in 0.61s
```

### Integration Tests

```text
./scripts/run_tests.sh integration
3 passed, 100 deselected in 0.11s
```

### Live Tests

```text
./scripts/run_tests.sh live
4 skipped in 0.02s
```

skip 原因：

```text
live tests require DSTAR_RUN_LIVE_TESTS=1
```

### 默认 Pytest

```text
.venv/bin/python -m pytest -q
99 passed, 4 deselected in 0.60s
```

### Linux 环境检查

```text
LD_LIBRARY_PATH=/home/ubuntu/dongyun/dstar_trade_py/third_party/dstar/lib/linux:${LD_LIBRARY_PATH:-} ./scripts/check_env.sh
Environment check passed.
```

环境检查输出中存在一个非失败 warning：

```text
[WARN] dmidecode exists but may require root/sudo for system-info collection
```

该 warning 与 `GetSystemInfo` 的系统权限采集相关，已在 `docs/linux_setup.md` 和 `docs/security.md` 中说明。

## 文档清单

| 文档 | 状态 |
| --- | --- |
| `README.md` | 通过：中文入口文档，链接全部 docs。 |
| `docs/architecture.md` | 通过：整体架构、binding 关系、回调线程模型、生命周期。 |
| `docs/linux_setup.md` | 通过：Linux 依赖、动态库、权限问题。 |
| `docs/api_reference.md` | 通过：公开类、方法、参数、返回值、异常。 |
| `docs/native_api_mapping.md` | 通过：`IDstarTradeApi` 到 Python 映射。 |
| `docs/callback_coverage.md` | 通过：`IDstarTradeSpi` 全回调覆盖表。 |
| `docs/field_mapping.md` | 通过：C++ typedef/结构体到 Python dataclass 映射。 |
| `docs/live_testing.md` | 通过：测试环境、环境变量、demo 运行方式、风险提示。 |
| `docs/order_api.md` | 通过：下单、撤单、状态、成交回报、请求号。 |
| `docs/order_state_machine.md` | 通过：状态机、journal、幂等保护。 |
| `docs/error_codes.md` | 通过：错误码和 Python 异常映射。 |
| `docs/development_guide.md` | 通过：继续开发、字段扩展、binding 调试、动态库排查。 |
| `docs/security.md` | 通过：凭据、日志、journal、live demo 安全边界。 |
| `docs/sdk_analysis.md` | 通过：官方 SDK 分析。 |
| `docs/api_coverage.md` | 通过：主动接口覆盖矩阵。 |

## 已完成项

- Linux-only 构建和运行边界。
- pybind11 native binding。
- `NativeTradeApi` RAII 生命周期。
- 全部 `IDstarTradeApi` 主动接口代理。
- 全部 `IDstarTradeSpi` 回调代理。
- 全部官方结构体 Python dataclass 映射。
- C++ 结构体到 Python dict 的安全转换。
- 回调 GIL 获取与异常捕获。
- 同步与 asyncio 高层 client。
- 请求号管理、订单状态机、幂等保护。
- 本地 order journal，敏感字段脱敏。
- 配置环境变量加载和 Python logging 脱敏。
- live demo 默认 dry-run 和二次确认。
- unit/integration/live 测试分层。
- 完整中文技术文档。

## 未完成项

无阻塞性未完成项。

## 风险项

- `GetSystemInfo` 可能受 Linux 权限、容器环境、DMI/硬件信息可见性影响；当前环境 `dmidecode` 对普通用户存在权限 warning。
- `FreeDstarTradeApi` 的内部线程停止行为由官方 vendor SDK 保证；项目侧已避免在 SPI 回调中释放 API，但无法证明 vendor 内部没有延迟回调。
- live tests 未在当前环境真实连接易盛测试环境，因为缺少真实账号和 `DSTAR_RUN_LIVE_TESTS=1`。当前只验证了 skip 逻辑。
- 官方 SDK 原始解压目录仍作为未跟踪目录存在，未纳入 git；项目使用的是 `third_party/dstar/`。

## 后续建议

- 在具备真实模拟账号的 Linux 主机上执行 live tests，并保存脱敏后的测试记录。
- 对生产部署补充进程级风控：账号白名单、合约白名单、最大手数、最大金额、kill switch。
- 若官方 SDK 升级，先运行字段/API/SPI 覆盖测试，再更新 `docs/field_mapping.md` 和 binding 转换。
- 生产环境将 `logs/order_journal.jsonl` 和官方 native log path 放在权限受控目录，并配置日志轮转。
