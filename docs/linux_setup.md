# Linux 运行环境配置

`dstar_trade_py` 只支持 Linux。Windows 和 macOS 不支持加载易盛启明星 V10 交易 API 的
Linux 动态库。非 Linux 平台可以 import 纯 Python 辅助模块，但创建 `NativeTradeApi`
会抛出明确的 Linux-only 运行时错误。

## Ubuntu 依赖

推荐 Ubuntu 22.04 或更新版本。最小依赖：

```bash
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  g++ \
  cmake \
  python3 \
  python3-dev \
  python3-venv \
  python3-pip
```

可选系统信息工具：

```bash
sudo apt-get install -y dmidecode lshw
```

## 官方 SDK 放置位置

项目约定官方 SDK 文件放在：

```text
third_party/dstar/include/
third_party/dstar/lib/linux/libdstartradeapi.so
```

不要修改官方头文件和动态库。构建时 CMake 会检查这些路径是否存在，并把
`libdstartradeapi.so` 安装到 Python 包的私有 `.libs` 目录。

## LD_LIBRARY_PATH

开发态运行环境建议设置：

```bash
export LD_LIBRARY_PATH="$PWD/third_party/dstar/lib/linux:${LD_LIBRARY_PATH:-}"
```

安装后的扩展带有 `$ORIGIN/.libs` 运行时搜索路径，正常 editable install 后 import 不应依赖
全局系统目录。但 `LD_LIBRARY_PATH` 对本地调试、直接运行构建目录中的扩展仍然有帮助。

## 构建与检查

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[test]'
./scripts/check_env.sh
python -m pytest
```

`scripts/check_env.sh` 会检查：

- 当前系统是否为 Linux；
- Python 版本是否满足 `>=3.10`；
- `python3-dev` / `Python.h` 是否存在；
- `g++` 是否存在；
- `cmake` 是否存在；
- `libdstartradeapi.so` 是否存在；
- `ldd` 是否能解析 vendor 动态库依赖；
- `LD_LIBRARY_PATH` 是否包含 vendor 动态库目录；
- `dmidecode` / `lshw` 是否存在以及当前用户是否可读。

## SDK 原生日志路径

Python 高层客户端通过 `api_log_path` 配置官方 SDK 原生日志路径：

```python
from dstar_trade_py import DstarTradeClient

client = DstarTradeClient(api_log_path="/tmp/dstar_trade_py/native_logs")
```

也可以使用环境变量：

```bash
export DSTAR_TRADE_LOG_PATH=/tmp/dstar_trade_py/native_logs
```

`DstarTradeConfig.ensure_native_log_path()` 会创建该目录。目录权限应限制为当前用户可读写，
不要放在会被提交到 Git 的路径下。

Python 示例：

```python
from dstar_trade_py import DstarTradeConfig

config = DstarTradeConfig.from_env(require_credentials=True)
native_log_path = config.ensure_native_log_path()
print("[示例格式] native log path:", native_log_path)
```

## 系统信息采集权限

官方 `GetSystemInfo` 通常会采集机器授权相关信息，可能依赖硬件序列号、DMI、网卡或其他
系统标识。不同发行版的权限策略不同，普通用户可能遇到采集失败。

常见情况：

- `dmidecode` 读取 DMI 信息通常需要 root 或 sudo；
- `lshw` 普通用户可运行，但完整信息可能需要 sudo；
- 容器内可能缺少 DMI、网卡或硬件标识，导致采集结果不完整；
- 云主机镜像可能限制部分 `/sys` 或 `/dev/mem` 访问。

如果 `get_system_info()` 返回错误码，先在目标机器上运行：

```bash
dmidecode -s system-uuid
lshw -quiet -class system
```

如果普通用户失败，再用 sudo 验证权限问题。生产部署时应按最小权限原则配置，而不是长期
用 root 运行交易进程；只有确实需要采集授权信息时才临时提升权限。
