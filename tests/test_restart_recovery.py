from __future__ import annotations

from pathlib import Path

from app.models import LoopStepRequest, StabilityResult, TrajectoryEdge
from app.runtime import ProcessExecutor
from app.sqlite_repository import SQLiteStore


def base_request(
    *,
    request_id: str,
    loop_id: str = "recovery_loop",
    response_type: str = "CONTINUE",
) -> dict:
    return {
        "request_id": request_id,
        "loop_id": loop_id,
        "idempotency_key": f"{loop_id}:{request_id}",
        "structure": {
            "structure_id": f"structure_{request_id}",
            "current_mode": {
                "relation_ref": "recovery_relation",
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
            "source_ref": f"structure_{request_id}",
            "orientation": {"orientation_id": "recovery_orientation"},
            "slice_policy": {
                "policy_id": "recovery_policy",
                "policy_type": "RESTART_RECOVERY_TEST",
                "parameters": {
                    "response_type": response_type,
                    "response_reason": "Recovery scenario response.",
                },
            },
        },
        "runtime_limits": {"max_slice_operations": 1},
    }


def test_restart_recovers_complete_runtime_state(tmp_path: Path) -> None:
    database = tmp_path / "recovery.db"
    first_store = SQLiteStore(database)
    executor = ProcessExecutor(first_store)

    first_request = LoopStepRequest.model_validate(
        base_request(request_id="recovery_one")
    )
    second_request = LoopStepRequest.model_validate(
        base_request(request_id="recovery_two", response_type="ADJUST")
    )

    first_result = executor.execute(first_request)
    second_result = executor.execute(second_request)

    restarted_store = SQLiteStore(database)

    assert restarted_store.get_current_scope("recovery_loop") == second_result.process_id

    history = restarted_store.list_process_history(loop_id="recovery_loop", limit=10)
    assert [item.process_id for item in history.items] == [
        first_result.process_id,
        second_result.process_id,
    ]
    assert history.next_cursor is None

    trajectory = restarted_store.list_trajectory_edges(
        trajectory_ref="recovery_relation",
        limit=10,
    )
    assert [edge.process_id for edge in trajectory.items] == [
        first_result.process_id,
        second_result.process_id,
    ]
    assert all(isinstance(edge, TrajectoryEdge) for edge in trajectory.items)

    restored_stability = restarted_store.get_record(
        second_result.stability.stability_result_id
    )
    assert isinstance(restored_stability, StabilityResult)
    assert restored_stability.status == second_result.stability.status

    restored_process = restarted_store.get_process(second_result.process_id)
    assert restored_process is not None
    assert restored_process.operator_response.response_type.value == "ADJUST"
    assert restored_process.continuity.continuity_type.value == "ADJUSTED_CONNECTION"


def test_restart_idempotent_replay_does_not_publish_new_state(tmp_path: Path) -> None:
    database = tmp_path / "replay.db"
    request = LoopStepRequest.model_validate(
        base_request(request_id="recovery_replay")
    )

    first_store = SQLiteStore(database)
    first_result = ProcessExecutor(first_store).execute(request)

    restarted_store = SQLiteStore(database)
    replayed = ProcessExecutor(restarted_store).execute(request)

    assert replayed.process_id == first_result.process_id
    assert replayed.replayed is True

    history = restarted_store.list_process_history(loop_id=request.loop_id, limit=10)
    assert [item.process_id for item in history.items] == [first_result.process_id]

    trajectory = restarted_store.list_trajectory_edges(
        trajectory_ref="recovery_relation",
        limit=10,
    )
    assert [edge.process_id for edge in trajectory.items] == [first_result.process_id]
    assert restarted_store.get_current_scope(request.loop_id) == first_result.process_id


def test_restart_preserves_empty_and_missing_queries(tmp_path: Path) -> None:
    database = tmp_path / "empty.db"
    SQLiteStore(database)

    restarted_store = SQLiteStore(database)
    assert restarted_store.get_current_scope("missing_loop") is None
    assert restarted_store.get_process("missing_process") is None
    assert restarted_store.get_record("missing_record") is None
    assert restarted_store.list_process_history(
        loop_id="missing_loop",
        limit=10,
    ).items == []
    assert restarted_store.list_trajectory_edges(
        trajectory_ref="missing_relation",
        limit=10,
    ).items == []
