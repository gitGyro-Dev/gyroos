from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}
PATH = "/vnext/experimental/inspection-review-bundle-comparison-set-comparisons"


def payload() -> dict:
    return {
        "set_comparison_id": "set-comparison-001",
        "left_set": {
            "comparison_set_id": "set-left",
            "bundle_comparison_ids": [
                "bundle-comparison-001",
                "bundle-comparison-002",
            ],
            "set_digest": "a" * 64,
        },
        "right_set": {
            "comparison_set_id": "set-right",
            "bundle_comparison_ids": [
                "bundle-comparison-002",
                "bundle-comparison-003",
            ],
            "set_digest": "b" * 64,
        },
        "warnings": [],
        "comparison_metadata": {"purpose": "inspection"},
    }


def test_create_comparison_returns_request_local_report(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["comparison_report_created"] is True
    assert body["report"]["added_bundle_comparison_ids"] == ["bundle-comparison-003"]
    assert body["report"]["removed_bundle_comparison_ids"] == ["bundle-comparison-001"]
    assert body["report"]["retained_bundle_comparison_ids"] == ["bundle-comparison-002"]
    assert body["report"]["digest_changed"] is True


def test_create_comparison_rejects_same_set(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    request_body = payload()
    request_body["right_set"]["comparison_set_id"] = "set-left"

    response = client.post(PATH, headers=HEADERS, json=request_body)

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_COMPARISON_INVALID"
    )


def test_comparison_response_has_no_runtime_authentication_or_semantic_outputs(
    monkeypatch,
) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")
    response = client.post(PATH, headers=HEADERS, json=payload())
    report = response.json()["report"]

    assert "auth_state" not in report
    assert "risk_level" not in report
    assert "semantic_trend" not in report
    assert "operator_response" not in report
    assert "runtime_state" not in report
    assert "difference_object" not in report


def test_comparison_retrieval_routes_are_absent(monkeypatch) -> None:
    monkeypatch.setenv("GYRO_RUNTIME_TOKEN", "test-token")

    assert client.get(f"{PATH}/set-comparison-001", headers=HEADERS).status_code == 404
    assert client.get(PATH, headers=HEADERS).status_code == 405
    assert client.delete(f"{PATH}/set-comparison-001", headers=HEADERS).status_code == 404
