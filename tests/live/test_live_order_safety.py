"""Live-order safety tests.

These tests are live-marked because they belong to the live-test workflow, but
they intentionally never submit a real order in the default path.
"""

from __future__ import annotations

from examples.live_common import confirm_live_order


def test_live_order_dry_run_does_not_confirm(live_config, capsys) -> None:
    """Without the explicit live-order flag, safety confirmation must block sending."""

    assert live_config
    allowed = confirm_live_order(
        "Insert limit order",
        {
            "contract_no": "SAFETY_ONLY",
            "order_qty": 1,
            "order_price": 1.0,
        },
        confirm_flag=False,
    )
    captured = capsys.readouterr()

    assert allowed is False
    assert "dry_run=True" in captured.out
    assert "No live request was sent" in captured.out
