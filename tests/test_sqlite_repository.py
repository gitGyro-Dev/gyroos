from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from app.models import LoopStepRequest
from app.repository_errors import IdempotencyConflict, RecordIdentityCollision
from app.runtime import ProcessExecutor, canonical_digest
from app.sqlite_repository import SQLiteStore


def base_request(
    *,
    request_id: str = "sqlite_request_001",
    loop_id: str = "sqlite_loop_001",
) -> dict:
    return {
        "request_id": request_id,
        "loop_id": loop_id,
        "idempotency_key": f"{loop_id}:{request_id}",
        "structure": {
            "structure_id": f"sqlite_structure_{request_id}",
            "current_mode": {
                "relation_ref": "sqlite_relation_001",
                "representation": {"state": "readable"},
                "stability": 0.92,
                "deviation": {"value": 0.08},
                "boundary_readability": 0.95,
                "target_relation_readability": 0.91,
                "boundary_state": "NORMAL",
                "boundary_state_confidence": 0.94,
            },
        },
        "slice_request": {
            "mode": "SLICE",
            "source_type": "RUNTIME_STRUCTURE",
            "source_ref": f"sqlite_structure_{request_id}",
            "orientation": {"orientation_id": "sqlite_orientation_001"},
            "slice_policy": {
                "policy_id": "sqlite_policy_continue",
                "policy_type": "BOUNDED_SQLITE_TEST",
                "parameters": {
                    "response_type": "CONTINUE",
                    "response_reason": "Preserve direct connection.",
                },
            },
        },
        "runtime_limits": {"max_slice_operations": 1},
    }


def test_sqlite_store_persists_and_reconstructs_complete_process(tmp_path: Path) -> None:
    database = tmp_path / "runtime.db"
    request = LoopStepRequest.model_validate(base_request())

    first_store = SQLiteStore(database)
    first_result = ProcessExecutor(first_store).execute(request)

    second_store = SQLiteStore(database)
    restored = second_store.get_process(first_result.process_id)

    assert restored is not None
    assert restored.process_id == first_result.process_id
    assert restored.stability.status == first_result.stability.status
    assert restored.operator_response.response_type == first_result.operator_response.response_type
    assert restored.continuity.continuity_type == first_result.continuity.continuity_type
    assert len(restored.trajectory_edges) == 1

    for record_id in first_result.created_record_refs:
        assert second_store.get_record(record_id) is not None


def test_sqlite_store_preserves_current_scope_and_idempotency_after_restart(
    tmp_path: Path,
) -> None:
    database = tmp_path / "runtime.db"
    request = LoopStepRequest.model_validate(base_request())

    first_store = SQLiteStore(database)
    first_result = ProcessExecutor(first_store).execute(request)

    second_store = SQLiteStore(database)
    assert second_store.get_current_scope(request.loop_id) == first_result.process_id

    replay = ProcessExecutor(second_store).execute(request)
    assert replay.process_id == first_result.process_id
    assert replay.replayed is True


def test_sqlite_store_process_history_survives_restart_and_paginates(
    tmp_path: Path,
) -> None:
    database = tmp_path / "runtime.db"
    first_store = SQLiteStore(database)
    executor = ProcessExecutor(first_store)

    for index in range(3):
        request = LoopStepRequest.model_validate(
            base_request(request_id=f"history_{index}", loop_id="sqlite_history_loop")
        )
        executor.execute(request)

    second_store = SQLiteStore(database)
    first_page = second_store.list_process_history(
        loop_id="sqlite_history_loop",
        limit=2,
    )
    assert [item.request_id for item in first_page.items] == ["history_0", "history_1"]
    assert first_page.next_cursor == "2"

    second_page = second_store.list_process_history(
        loop_id="sqlite_history_loop",
        limit=2,
        cursor=first_page.next_cursor,
    )
    assert [item.request_id for item in second_page.items] == ["history_2"]
    assert second_page.next_cursor is None


def test_sqlite_store_process_history_returns_empty_page_for_unknown_loop(
    tmp_path: Path,
) -> None:
    store = SQLiteStore(tmp_path / "runtime.db")
    page = store.list_process_history(loop_id="missing_loop", limit=20)
    assert page.items == []
    assert page.next_cursor is None


def test_sqlite_store_process_history_rejects_invalid_cursor(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "runtime.db")
    with pytest.raises(ValueError, match="history cursor"):
        store.list_process_history(loop_id="loop", cursor="invalid")


def test_sqlite_store_missing_record_remains_none(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "runtime.db")
    assert store.get_record("missing_record") is None
    assert store.get_process("missing_process") is None


def test_sqlite_store_rolls_back_complete_publication_on_injected_failure(
    tmp_path: Path,
) -> None:
    database = tmp_path / "runtime.db"
    request = LoopStepRequest.model_validate(base_request())

    def fail_before_current_scope(phase: str, position: int) -> None:
        if phase == "before_current_scope":
            raise sqlite3.OperationalError(f"injected failure at {position}")

    store = SQLiteStore(database, failure_injector=fail_before_current_scope)

    with pytest.raises(Exception):
        ProcessExecutor(store).execute(request)

    verification_store = SQLiteStore(database)
    assert verification_store.get_current_scope(request.loop_id) is None
    assert verification_store.get_idempotent(
        request.loop_id,
        request.idempotency_key or "",
    ) is None

    with sqlite3.connect(database) as connection:
        record_count = connection.execute(
            "SELECT COUNT(*) FROM runtime_records"
        ).fetchone()[0]
        scope_count = connection.execute(
            "SELECT COUNT(*) FROM current_scope"
        ).fetchone()[0]
        idempotency_count = connection.execute(
            "SELECT COUNT(*) FROM idempotency_entries"
        ).fetchone()[0]

    assert record_count == 0
    assert scope_count == 0
    assert idempotency_count == 0


def test_sqlite_store_rejects_idempotency_key_with_different_digest(
    tmp_path: Path,
) -> None:
    database = tmp_path / "runtime.db"
    request = LoopStepRequest.model_validate(base_request())
    store = SQLiteStore(database)
    first_result = ProcessExecutor(store).execute(request)

    changed_payload = base_request()
    changed_payload["structure"]["current_mode"]["stability"] = 0.61
    changed_request = LoopStepRequest.model_validate(changed_payload)

    with pytest.raises(RuntimeError, match="idempotency conflict"):
        ProcessExecutor(store).execute(changed_request)

    persisted = store.get_process(first_result.process_id)
    assert persisted is not None
    assert persisted.stability.value == 0.92
    assert store.get_current_scope(request.loop_id) == first_result.process_id


def test_sqlite_store_publish_rejects_conflicting_idempotency_digest_directly(
    tmp_path: Path,
) -> None:
    database = tmp_path / "runtime.db"
    request = LoopStepRequest.model_validate(base_request())
    store = SQLiteStore(database)
    result = ProcessExecutor(store).execute(request)

    with pytest.raises(IdempotencyConflict):
        store.publish(
            result=result,
            request_digest="different_digest",
            idempotency_key=request.idempotency_key,
        )


def test_sqlite_store_translates_record_identity_collision(
    tmp_path: Path,
) -> None:
    database = tmp_path / "runtime.db"
    request = LoopStepRequest.model_validate(base_request())
    store = SQLiteStore(database)
    result = ProcessExecutor(store).execute(request)

    with pytest.raises(RecordIdentityCollision):
        store.publish(
            result=result.model_copy(update={"replayed": False}),
            request_digest=canonical_digest(request),
            idempotency_key=None,
        )
