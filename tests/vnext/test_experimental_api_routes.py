from fastapi.testclient import TestClient

from app.main import app
from app.vnext.experimental_api_provider import experimental_repository_provider
from app.vnext.experimental_repository import InMemoryExperimentalRecordRepository


client = TestClient(app)


def setup_function() -> None:
    experimental_repository_provider.replace_repository(
        InMemoryExperimentalRecordRepository()
    )


def test_create_get_list_delete_round_trip() -> None:
    create_response = client.post(
        "/vnext/experimental/records",
        json={
            "record_id": "record-001",
            "process_id": "process-001",
            "record_type": "TrajectoryGraph",
            "payload": {"nodes": ["node-001"]},
            "metadata": {"source": "api-test"},
        },
    )
    assert create_response.status_code == 201
    assert create_response.json()["record"]["record_id"] == "record-001"

    get_response = client.get("/vnext/experimental/records/record-001")
    assert get_response.status_code == 200
    assert get_response.json()["record"]["payload"] == {"nodes": ["node-001"]}

    list_response = client.get("/vnext/experimental/records")
    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["ordering"] == "UNSPECIFIED"

    delete_response = client.delete("/vnext/experimental/records/record-001")
    assert delete_response.status_code == 204

    missing_response = client.get("/vnext/experimental/records/record-001")
    assert missing_response.status_code == 404
    assert missing_response.json()["error_code"] == "GYRO_VNEXT_EXPERIMENTAL_RECORD_NOT_FOUND"


def test_list_filters_by_process_and_record_type() -> None:
    records = [
        ("record-001", "process-a", "TrajectoryGraph"),
        ("record-002", "process-a", "ReadabilityContext"),
        ("record-003", "process-b", "TrajectoryGraph"),
    ]
    for record_id, process_id, record_type in records:
        response = client.post(
            "/vnext/experimental/records",
            json={
                "record_id": record_id,
                "process_id": process_id,
                "record_type": record_type,
                "payload": {},
            },
        )
        assert response.status_code == 201

    response = client.get(
        "/vnext/experimental/records",
        params={"process_id": "process-a", "record_type": "TrajectoryGraph"},
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["records"][0]["record_id"] == "record-001"


def test_list_limit_is_bounded_by_experimental_settings() -> None:
    for index in range(105):
        response = client.post(
            "/vnext/experimental/records",
            json={
                "record_id": f"record-{index:03d}",
                "process_id": "process-001",
                "record_type": "OpaqueRecord",
                "payload": {},
            },
        )
        assert response.status_code == 201

    response = client.get("/vnext/experimental/records", params={"limit": 1000})

    assert response.status_code == 200
    assert response.json()["count"] == 100


def test_create_rejects_canonical_fields() -> None:
    response = client.post(
        "/vnext/experimental/records",
        json={
            "record_id": "record-001",
            "process_id": "process-001",
            "record_type": "TrajectoryGraph",
            "payload": {},
            "canonical": True,
        },
    )

    assert response.status_code == 422


def test_missing_delete_returns_explicit_error() -> None:
    response = client.delete("/vnext/experimental/records/missing")

    assert response.status_code == 404
    assert response.json()["phase"] == "EXPERIMENTAL_RECORD_DELETE"


def test_existing_loop_step_route_remains_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/loop/step" in paths
    assert "/vnext/experimental/records" in paths
