"""Small example that confirms the package and native module are importable."""

import dstar_trade_py


def main() -> None:
    """Create a temporary API instance and print non-sensitive build metadata."""
    print(f"dstar_trade_py version: {dstar_trade_py.__version__}")
    print(f"SDK protocol version: {dstar_trade_py.SDK_PROTOCOL_VERSION}")
    print(f"Vendor API version: {dstar_trade_py.get_api_version()}")
    print(f"Create/free check: {dstar_trade_py.create_and_free_api()}")


if __name__ == "__main__":
    main()
