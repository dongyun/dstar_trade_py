# 开发指南

本文面向继续维护 `dstar_trade_py` 的开发者，说明如何扩展字段、调试 C++ binding、运行测试和排查动态库问题。

## 本地开发环境

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
export LD_LIBRARY_PATH="$PWD/third_party/dstar/lib/linux:${LD_LIBRARY_PATH:-}"
./scripts/check_env.sh
python -m pytest
```

默认测试不连接真实交易服务器。live tests 需要显式设置 `DSTAR_RUN_LIVE_TESTS=1`。

## 目录约定

| 路径 | 说明 |
| --- | --- |
| `third_party/dstar/include/` | 官方头文件，不修改。 |
| `third_party/dstar/lib/linux/libdstartradeapi.so` | 官方 Linux 动态库，不修改。 |
| `cpp/binding.cpp` | pybind11 模块和 `NativeTradeApi`。 |
| `cpp/field_converters.*` | C++ 结构体到 Python dict 的转换。 |
| `cpp/trade_spi_adapter.*` | `IDstarTradeSpi` 到 Python dispatcher 的适配。 |
| `dstar_trade_py/fields.py` | Python dataclass。 |
| `dstar_trade_py/enums.py` | 官方常量的可读枚举。 |
| `dstar_trade_py/client.py` | 同步高层 client。 |
| `dstar_trade_py/async_client.py` | asyncio client。 |
| `tests/unit/` | 不连接真实服务器的单元测试。 |
| `tests/integration/` | 加载真实 `.so`，不连接服务器。 |
| `tests/live/` | 需要真实测试账号，默认跳过。 |

## 如何添加新字段

如果官方 SDK 更新了 `DstarTradeApiStruct.h` 或 `DstarTradeApiDataType.h`：

1. 不修改官方头文件。
2. 对照头文件更新 `docs/field_mapping.md`。
3. 更新 `dstar_trade_py/fields.py` 中对应 dataclass。
4. 如果字段是官方常量语义，更新 `dstar_trade_py/enums.py`。
5. 更新 C++ 转换函数 `cpp/field_converters.h` 和 `cpp/field_converters.cpp`。
6. 如果字段用于主动请求，更新 `cpp/binding.cpp` 中 dict -> C++ 结构体转换。
7. 更新测试：
   - `tests/unit/test_fields.py`
   - `tests/unit/test_field_converters.py`
   - 相关 client/builder 测试。

示例：给某个回报结构体新增字段 `FooValue`：

```python
@dataclass(slots=True)
class DstarApiOrderField(DstarField):
    # 已有字段...
    FooValue: int = 0  # 官方新增字段含义
```

C++ 转换示例格式：

```cpp
py::dict to_py_dict(const DstarApiOrderField* field) {
    py::dict result;
    if (field == nullptr) {
        return result;
    }
    result["FooValue"] = field->FooValue;
    return result;
}
```

## 如何添加新的主动接口

当前 `IDstarTradeApi` 已全部覆盖。如果未来官方新增主动接口：

1. 在 `cpp/binding.cpp` 的 `NativeTradeApi` 类中新增方法。
2. 如果有结构体入参，先实现严格 dict -> C++ 结构体转换。
3. 在 `PYBIND11_MODULE` 中 `.def(...)` 暴露方法。
4. 在 `DstarTradeClient` 中新增高层方法，并统一调用 `raise_for_error(ret, "官方方法名")`。
5. 在 `AsyncDstarTradeClient` 中新增 async 包装。
6. 更新 `docs/native_api_mapping.md` 和 `docs/api_reference.md`。
7. 更新 `tests/unit/test_api_coverage.py`。

不要把 `IDstarTradeApi*` 裸指针暴露给 Python。

## 如何添加新的 SPI 回调

当前 `IDstarTradeSpi` 已全部覆盖。如果官方新增回调：

1. 在 `cpp/trade_spi_adapter.h` 声明 override。
2. 在 `cpp/trade_spi_adapter.cpp` 实现：
   - 立即复制结构体到 `py::dict`；
   - 获取 GIL；
   - 调用统一 dispatcher；
   - 捕获所有异常。
3. 在 `cpp/field_converters.*` 添加结构体转换函数。
4. 在 `DstarTradeClient._convert_event_payload` 增加 event -> dataclass 映射。
5. 如需状态更新，在 `_update_state_from_event` 或 `_route_event_to_queue` 中处理。
6. 更新 `docs/callback_coverage.md` 和 `tests/unit/test_callback_coverage.py`。

回调命名规则：`OnRspUserLogin -> rsp_user_login`，`OnRtnOrder -> rtn_order`，`OnApiReady -> api_ready`。

## 调试 C++ Binding

重新构建 editable install：

```bash
source .venv/bin/activate
python -m pip install -e '.[test]' --no-build-isolation
```

查看扩展位置：

```bash
python - <<'PY'
import dstar_trade_py._dstar_trade_py as native
print(native.__file__)
PY
```

查看动态依赖：

```bash
ldd "$(python - <<'PY'
import dstar_trade_py._dstar_trade_py as native
print(native.__file__)
PY
)"
```

运行 native 相关测试：

```bash
python -m pytest tests/integration/test_native_load.py -q
python -m pytest tests/unit/test_native_api_methods.py -q
python -m pytest tests/unit/test_field_converters.py -q
python -m pytest tests/unit/test_callback_dispatch.py -q
```

## 排查动态库加载失败

典型错误：

```text
ImportError: Failed to load the dstar_trade_py Linux extension...
```

排查顺序：

1. 确认系统是 Linux：

   ```bash
   uname -a
   ```

2. 确认 vendor so 存在：

   ```bash
   ls -l third_party/dstar/lib/linux/libdstartradeapi.so
   ```

3. 检查依赖：

   ```bash
   ldd third_party/dstar/lib/linux/libdstartradeapi.so
   ```

4. 检查运行时搜索路径：

   ```bash
   export LD_LIBRARY_PATH="$PWD/third_party/dstar/lib/linux:${LD_LIBRARY_PATH:-}"
   ./scripts/check_env.sh
   ```

5. 重新安装：

   ```bash
   python -m pip install -e '.[test]' --force-reinstall
   ```

安装后的扩展会携带 `$ORIGIN/.libs` RPATH，并把 vendor so 安装到 `dstar_trade_py/.libs`。

## 排查系统信息采集失败

`get_system_info()` 可能依赖 DMI、硬件序列号、网卡和系统信息。普通用户可能没有权限。

```bash
dmidecode -s system-uuid
lshw -quiet -class system
```

如果普通用户失败，用 sudo 验证是否是权限问题：

```bash
sudo dmidecode -s system-uuid
sudo lshw -quiet -class system
```

不要为了方便长期用 root 运行交易进程。更合理的做法是单独处理授权采集步骤，并限制交易进程权限。

## 测试策略

```bash
./scripts/run_tests.sh unit
./scripts/run_tests.sh integration
./scripts/run_tests.sh live
./scripts/run_tests.sh all
```

测试分层：

- unit：不依赖真实账号，不连接服务器。
- integration：可加载真实 `.so`，不连接服务器。
- live：需要 `DSTAR_RUN_LIVE_TESTS=1` 和 `DSTAR_TRADE_*` 环境变量。

live order 测试默认不真实下单。真实有副作用操作只放在 `examples/`，并要求命令行确认。

## 文档更新规则

新增或修改公开 API 时同步更新：

- `docs/api_reference.md`
- `docs/native_api_mapping.md`
- `docs/callback_coverage.md`
- `docs/field_mapping.md`
- `README.md`

新增下单行为时同步更新：

- `docs/order_api.md`
- `docs/order_state_machine.md`
- `docs/security.md`

## 常见开发错误

| 问题 | 原因 | 处理 |
| --- | --- | --- |
| 回调崩溃 | Python 异常穿透 C++ 回调 | 必须在 adapter 中捕获异常。 |
| 字符串乱码 | char 数组不是 UTF-8 或未 NUL 结尾 | C++ 转换使用 bounded length + UTF-8 replace。 |
| 悬空指针 | Python 保存官方结构体指针 | 回调中必须立即复制为 dict。 |
| 重复下单 | 复用 `client_order_id` 或 `ClientReqId` | 使用 `RequestIdManager` 和 `OrderStateManager`。 |
| 测试污染仓库 | 默认 journal 写到 `logs/` | 单元测试传 `tmp_path / "order_journal.jsonl"`。 |
