"""Small example that confirms the package and native module are importable."""

import dstar_trade_py


def main() -> None:
    """Print non-sensitive build metadata from the minimal extension."""
    print(f"dstar_trade_py version: {dstar_trade_py.__version__}")
    print(f"SDK protocol version: {dstar_trade_py.SDK_PROTOCOL_VERSION}")


if __name__ == "__main__":
    main()

