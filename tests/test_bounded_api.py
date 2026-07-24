from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.repositories import store

client = TestClient(app)


def base_request(*, request_id: str = "request_001", loop_id: str = "loop_001") -> dict:
    return {
        "request_id": request_id,
        "loop_id": loop_id,
        "idempotency_key": f"{loop_id}:{request_id}",
        "structure": {
            "structure_id": f"structure_{request_id}",
            "current_mode": {
                "stability": 0.92,
                "relation_ref": "relation_001",
                "boundary_readability": 0.95,
                "target_relation_readability": 0.9,
                "boundary_state": "NORMAL",
                "boundary_state_confidence": 0.93,
                "deviation": {"value": 0.08},
            },
        },
        "slice_request": {
            "mode": "SLICE",
            "source_type": "RUNTIME_STRUCTURE",
            "source_ref": f"structure_{request_id}",
            "orientation": {"orientation_id": "orientation_001"},
            "slice_policy": {
                "policy_id": "policy_continue",
                "policy_type": "BOUNDED_DEMO",
                "parameters": {
                    "response_type": "CONTINUE",
                    "response_reason": "Direct connection selected by bounded test policy.",
                },
            },
        },
        "runtime_limits": {"max_slice_operations": 1},
    }


def setup_function() -> None:
    store.processes.clear()
    store.records.clear()
    store.idempotency.clear()
    store.current_scope.clear()
    store.process_history.clear()


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["runtime"] == "bounded"


def test_one_request_creates_one_complete_process() -> None:
    response = client.post("/loop/step", json=base_request())
    assert response.status_code == 200
    body = response.json()
    assert body["slice_done"]["process_id"] == body["process_id"]
    assert body["stability"]["process_id"] == body["process_id"]
    assert body["operator_response"]["process_id"] == body["process_id"]
    assert body["continuity"]["process_id"] == body["process_id"]
    assert body["operator_response"]["response_type"] == "CONTINUE"
    assert body["continuity"]["continuity_type"] == "DIRECT_CONNECTION"


def test_explicit_representation_preserves_stability_for_evaluation() -> None:
    payload = base_request(request_id="representation_stability")
    payload["structure"]["current_mode"]["representation"] = {
        "state": "readable",
        "path": "direct",
    }
    response = client.post("/loop/step", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["slice_done"]["representation"]["state"] == "readable"
    assert body["slice_done"]["representation"]["stability"] == 0.92
    assert body["stability"]["status"] == "STABLE"
    assert body["stability"]["value"] == 0.92


def test_idempotent_replay_does_not_create_second_process() -> None:
    payload = base_request()
    first = client.post("/loop/step", json=payload)
    second = client.post("/loop/step", json=payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["process_id"] == second.json()["process_id"]
    assert second.json()["replayed"] is True
    assert len(store.processes) == 1
    assert len(store.process_history["loop_001"]) == 1


def test_void_is_runtime_result_and_defer_is_separate() -> None:
    payload = base_request(request_id="void_001", loop_id="loop_void")
    payload["structure"]["current_mode"].update(
        {
            "boundary_state": "VOID",
            "target_relation_readability": 0.1,
            "connectability": 0.0,
        }
    )
    payload["slice_request"]["slice_policy"]["parameters"]["response_type"] = "DEFER"
    response = client.post("/loop/step", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["slice_done"]["boundary_state_records"][0]["state_type"] == "VOID"
    assert body["slice_done"]["void_evidence"]
    assert body["operator_response"]["response_type"] == "DEFER"
    assert body["continuity"]["continuity_type"] == "DEFERRED_PENDING_RELATION"
    assert body["continuity"]["pending"] is True


def test_reslice_prepares_next_request_without_recursive_execution() -> None:
    seed = base_request(request_id="seed", loop_id="loop_reslice")
    seed["structure"]["current_mode"]["context"] = {"candidate": "alternate path"}
    seed_response = client.post("/loop/step", json=seed)
    context_ref = seed_response.json()["slice_done"]["context_evidence"][0]["context_evidence_id"]

    payload = base_request(request_id="prepare", loop_id="loop_prepare")
    payload["slice_request"]["slice_policy"]["parameters"].update(
        {
            "response_type": "RESLICE",
            "reslice_source_type": "CONTEXT_EVIDENCE",
            "reslice_source_ref": context_ref,
        }
    )
    response = client.post("/loop/step", json=payload)
    assert response.status_code == 200
    body = response.json()
    next_request = body["operator_response"]["next_request"]
    assert next_request["mode"] == "RESLICE"
    assert next_request["source_ref"] == context_ref
    assert len(store.processes) == 2


def test_invalid_initial_source_is_422() -> None:
    payload = base_request()
    payload["slice_request"]["source_type"] = "CONTEXT_EVIDENCE"
    response = client.post("/loop/step", json=payload)
    assert response.status_code == 422


def test_current_scope_conflict_is_409_not_stop() -> None:
    first = client.post("/loop/step", json=base_request(request_id="one", loop_id="scope_loop"))
    assert first.status_code == 200
    payload = base_request(request_id="two", loop_id="scope_loop")
    payload["expected_current_scope_ref"] = "wrong_process"
    response = client.post("/loop/step", json=payload)
    assert response.status_code == 409
    assert response.json()["category"] == "IDENTITY_CONFLICT"


def test_current_scope_endpoint_returns_explicit_current_process() -> None:
    created = client.post(
        "/loop/step",
        json=base_request(request_id="scope_state", loop_id="scope_state_loop"),
    )
    assert created.status_code == 200
    process_id = created.json()["process_id"]

    response = client.get("/loop/state/scope_state_loop")
    assert response.status_code == 200
    body = response.json()
    assert body["loop_id"] == "scope_state_loop"
    assert body["current_process_id"] == process_id
    assert body["process"]["process_id"] == process_id


def test_current_scope_endpoint_returns_404_when_scope_is_absent() -> None:
    response = client.get("/loop/state/missing_loop")
    assert response.status_code == 404
    body = response.json()
    assert body["error_code"] == "GYRO_API_NOT_FOUND_CURRENT_SCOPE"
    assert body["category"] == "NOT_FOUND"


def test_current_scope_endpoint_reports_broken_pointer_as_repository_error() -> None:
    store.current_scope["broken_loop"] = "missing_process"
    response = client.get("/loop/state/broken_loop")
    assert response.status_code == 500
    body = response.json()
    assert body["error_code"] == "GYRO_API_REPOSITORY_INTEGRITY"
    assert body["category"] == "REPOSITORY"


def test_process_history_returns_publication_order_and_summary() -> None:
    first = client.post(
        "/loop/step",
        json=base_request(request_id="history_one", loop_id="history_loop"),
    )
    second = client.post(
        "/loop/step",
        json=base_request(request_id="history_two", loop_id="history_loop"),
    )
    assert first.status_code == 200
    assert second.status_code == 200

    response = client.get("/loop/history/history_loop")
    assert response.status_code == 200
    body = response.json()
    assert body["loop_id"] == "history_loop"
    assert [item["request_id"] for item in body["items"]] == [
        "history_one",
        "history_two",
    ]
    assert body["items"][0]["operator_response"] == "CONTINUE"
    assert body["items"][0]["continuity_type"] == "DIRECT_CONNECTION"
    assert body["next_cursor"] is None


def test_process_history_supports_bounded_cursor_pagination() -> None:
    for index in range(3):
        response = client.post(
            "/loop/step",
            json=base_request(request_id=f"page_{index}", loop_id="page_loop"),
        )
        assert response.status_code == 200

    first_page = client.get("/loop/history/page_loop?limit=2")
    assert first_page.status_code == 200
    first_body = first_page.json()
    assert [item["request_id"] for item in first_body["items"]] == ["page_0", "page_1"]
    assert first_body["next_cursor"] == "2"

    second_page = client.get(
        f"/loop/history/page_loop?limit=2&cursor={first_body['next_cursor']}"
    )
    assert second_page.status_code == 200
    second_body = second_page.json()
    assert [item["request_id"] for item in second_body["items"]] == ["page_2"]
    assert second_body["next_cursor"] is None


def test_process_history_empty_loop_returns_empty_page() -> None:
    response = client.get("/loop/history/missing_history")
    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["next_cursor"] is None


def test_process_history_rejects_invalid_cursor() -> None:
    response = client.get("/loop/history/history_loop?cursor=invalid")
    assert response.status_code == 422
    body = response.json()
    assert body["error_code"] == "GYRO_API_VALIDATION_HISTORY_CURSOR"
    assert body["phase"] == "PROCESS_HISTORY_QUERY"


def test_published_process_and_record_can_be_retrieved() -> None:
    created = client.post("/loop/step", json=base_request())
    body = created.json()
    process = client.get(f"/process/{body['process_id']}")
    record = client.get(f"/memory/record/{body['stability']['stability_result_id']}")
    assert process.status_code == 200
    assert record.status_code == 200
    assert record.json()["status"] == "STABLE"
