from __future__ import annotations

from pathlib import Path

from app.models import LoopStepRequest
from app.runtime import ProcessExecutor
from app.sqlite_repository import SQLiteStore


def base_request() -> dict:
    return {
        "request_id": "sqlite_request_001",
        "loop_id": "sqlite_loop_001",
        "idempotency_key": "sqlite_loop_001:step_001",
        "structure": {
            "structure_id": "sqlite_structure_001",
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
            "source_ref": "sqlite_structure_001",
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


def test_sqlite_store_missing_record_remains_none(tmp_path: Path) -> None:
    store = SQLiteStore(tmp_path / "runtime.db")
    assert store.get_record("missing_record") is None
    assert store.get_process("missing_process") is None
