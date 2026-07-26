from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}
PATH = "/vnext/experimental/inspection-comparison-set-comparison-series"


def payload() -> dict:
    return {
        "comparison_series_id": "series-001",
        "set_comparison_references": [
            {
                "set_comparison_id": "set-comparison-001",
                "left_comparison_set_id": "set-left-001",
                "right_comparison_set_id": "set-right-001",
                "added_count": 1,
                "removed_count": 0,
                "retained_count": 2,
                "digest_changed": True,
            },
            {
                "set_comparison_id": "set-comparison-002",
                "left_comparison_set_id": "set-left-002",
                "right_comparison_set_id": "set-right-002",
                "added_count": 0,
                "removed_count": 1,
                "retained_count": 3,
                "digest_changed": False,
            },
        ],
        "warnings": [],
        "source_refs": [],
        "series_metadata": {"purpose": "inspection"},
    }


def test_create_series_returns_request_local_manifest(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["comparison_series_created"] is True
    assert body["manifest"]["reference_count"] == 2
    assert [
        item["set_comparison_id"]
        for item in body["manifest"]["set_comparison_references"]
    ] == ["set-comparison-001", "set-comparison-002"]
    assert len(body["manifest"]["series_digest"]) == 64


def test_create_series_rejects_duplicate_reference(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    request_body = payload()
    request_body["set_comparison_references"][1]["set_comparison_id"] = (
        "set-comparison-001"
    )

    response = client.post(PATH, headers=HEADERS, json=request_body)

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_SET_COMPARISON_SERIES_INVALID"
    )


def test_series_response_has_no_runtime_authentication_or_semantic_outputs(
    monkeypatch,
) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())
    manifest = response.json()["manifest"]

    assert "auth_state" not in manifest
    assert "risk_level" not in manifest
    assert "semantic_trend" not in manifest
    assert "operator_response" not in manifest
    assert "runtime_state" not in manifest
    assert "difference_object" not in manifest


def test_series_retrieval_routes_are_absent(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")

    assert client.get(f"{PATH}/series-001", headers=HEADERS).status_code == 404
    assert client.get(PATH, headers=HEADERS).status_code == 405
    assert client.delete(f"{PATH}/series-001", headers=HEADERS).status_code == 404
