"""Tests for RequestIdManager and request-id recovery."""

from __future__ import annotations

import pytest

from dstar_trade_py import OrderJournal, RequestIdManager


def test_request_id_manager_allocates_monotonic_ids() -> None:
    """Local request IDs should increase and skip already used values."""

    manager = RequestIdManager(start=10, used_ids={11})

    assert manager.next_id() == 12
    assert manager.next_id() == 13
    assert manager.has_used(12) is True


def test_request_id_manager_rejects_duplicate_explicit_ids() -> None:
    """Explicit duplicate ClientReqId values should fail before native submit."""

    manager = RequestIdManager()

    assert manager.reserve(100) == 100
    with pytest.raises(ValueError, match="duplicate client_req_id"):
        manager.reserve(100)


def test_request_id_manager_updates_from_remote_and_detects_jumps() -> None:
    """Large gaps between local and remote request IDs should be recorded."""

    manager = RequestIdManager(start=10, jump_threshold=5)

    manager.update_from_remote(30)

    assert manager.current == 30
    assert manager.detected_jumps == [(10, 30)]


def test_request_id_manager_recovers_used_ids_from_journal(tmp_path) -> None:
    """Journal recovery should preserve used ClientReqId values."""

    journal = OrderJournal(tmp_path / "order_journal.jsonl")
    journal.append("order_submit", client_req_id=7, payload={"ClientReqId": 7})
    journal.append("order_cancel", client_req_id=9, payload={"ClientReqId": 9})

    manager = RequestIdManager.from_journal(journal)

    assert manager.has_used(7)
    assert manager.has_used(9)
    assert manager.next_id() == 10


def test_request_id_manager_ignores_corrupt_journal_lines(tmp_path) -> None:
    """Recovery should skip a partially written JSONL line after a crash."""

    path = tmp_path / "order_journal.jsonl"
    path.write_text(
        '{"client_req_id": 10, "event_type": "order_submit"}\n'
        '{"client_req_id": ',
        encoding="utf-8",
    )

    manager = RequestIdManager.from_journal(OrderJournal(path))

    assert manager.has_used(10)
    assert manager.next_id() == 11
