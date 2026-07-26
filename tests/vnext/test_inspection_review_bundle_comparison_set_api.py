from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-runtime-token"}


def payload():
    return {
        "comparison_set_id": "set-001",
        "comparison_references": [
            {
                "bundle_comparison_id": "comparison-001",
                "left_review_bundle_id": "bundle-left-001",
                "right_review_bundle_id": "bundle-right-001",
                "added_count": 1,
                "removed_count": 2,
                "retained_count": 3,
                "digest_changed": True,
            },
            {
                "bundle_comparison_id": "comparison-002",
                "left_review_bundle_id": "bundle-left-002",
                "right_review_bundle_id": "bundle-right-002",
                "added_count": 0,
                "removed_count": 1,
                "retained_count": 4,
                "digest_changed": False,
            },
        ],
        "warnings": ["caller_warning"],
        "source_refs": ["source-001"],
        "metadata": {"purpose": "inspection"},
    }


def test_create_set_returns_request_local_result() -> None:
    response = client.post(
        "/vnext/experimental/inspection-review-bundle-comparison-sets",
        json=payload(),
        headers=HEADERS,
    )

    assert response.status_code == 201
    body = response.json()
    assert body["comparison_set_created"] is True
    assert body["comparison_set"]["comparison_count"] == 2
    assert len(body["comparison_set"]["comparison_references_digest"]) == 64


def test_create_set_rejects_duplicate_comparison_ids() -> None:
    body = payload()
    body["comparison_references"][1]["bundle_comparison_id"] = "comparison-001"

    response = client.post(
        "/vnext/experimental/inspection-review-bundle-comparison-sets",
        json=body,
        headers=HEADERS,
    )

    assert response.status_code == 422
    assert (
        response.json()["error_code"]
        == "GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_SET_INVALID"
    )


def test_set_response_does_not_define_runtime_authentication_or_risk_outputs() -> None:
    response = client.post(
        "/vnext/experimental/inspection-review-bundle-comparison-sets",
        json=payload(),
        headers=HEADERS,
    )

    manifest = response.json()["comparison_set"]
    for field in (
        "auth_state",
        "auth_score",
        "operator_response",
        "next_action",
        "runtime_state",
        "semantic_trend",
        "risk_level",
    ):
        assert field not in manifest


def test_set_retrieval_routes_are_not_defined() -> None:
    assert (
        client.get(
            "/vnext/experimental/inspection-review-bundle-comparison-sets/set-001",
            headers=HEADERS,
        ).status_code
        == 404
    )
    assert (
        client.get(
            "/vnext/experimental/inspection-review-bundle-comparison-sets",
            headers=HEADERS,
        ).status_code
        == 405
    )


def test_existing_routes_remain_available() -> None:
    assert (
        client.post(
            "/vnext/experimental/inspection-review-bundle-comparisons",
            json={},
            headers=HEADERS,
        ).status_code
        == 422
    )
    assert client.get("/openapi.json").status_code == 200
