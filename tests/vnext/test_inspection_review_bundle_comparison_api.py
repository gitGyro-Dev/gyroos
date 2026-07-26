from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def payload() -> dict:
    return {
        "bundle_comparison_id": "bundle-comparison-001",
        "left_bundle": {
            "review_bundle_id": "bundle-left",
            "comparison_ids": ["comparison-001", "comparison-002"],
            "bundle_digest": "a" * 64,
        },
        "right_bundle": {
            "review_bundle_id": "bundle-right",
            "comparison_ids": ["comparison-002", "comparison-003"],
            "bundle_digest": "b" * 64,
        },
        "warnings": [],
        "metadata": {"purpose": "inspection"},
    }


def test_create_review_bundle_comparison_returns_request_local_result() -> None:
    response = client.post(
        "/vnext/experimental/inspection-review-bundle-comparisons",
        json=payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["review_bundle_comparison_created"] is True
    assert body["report"]["added_comparison_ids"] == ["comparison-003"]
    assert body["report"]["removed_comparison_ids"] == ["comparison-001"]
    assert body["report"]["retained_comparison_ids"] == ["comparison-002"]
    assert body["report"]["digest_changed"] is True


def test_create_review_bundle_comparison_rejects_same_bundle() -> None:
    body = payload()
    body["right_bundle"]["review_bundle_id"] = "bundle-left"

    response = client.post(
        "/vnext/experimental/inspection-review-bundle-comparisons",
        json=body,
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_REVIEW_BUNDLE_COMPARISON_INVALID"
    )


def test_review_bundle_comparison_endpoint_does_not_expose_retrieval_routes() -> None:
    paths = set(app.openapi()["paths"])

    assert "/vnext/experimental/inspection-review-bundle-comparisons" in paths
    assert (
        "/vnext/experimental/inspection-review-bundle-comparisons/{bundle_comparison_id}"
        not in paths
    )


def test_existing_routes_remain_registered() -> None:
    paths = set(app.openapi()["paths"])

    assert "/loop/step" in paths
    assert "/vnext/experimental/records" in paths
    assert "/vnext/experimental/inspection-comparison-review-bundles" in paths


def test_comparison_response_does_not_define_runtime_authentication_semantic_or_risk_outputs() -> None:
    report = client.post(
        "/vnext/experimental/inspection-review-bundle-comparisons",
        json=payload(),
    ).json()["report"]

    assert "auth_state" not in report
    assert "auth_score" not in report
    assert "risk_level" not in report
    assert "semantic_trend" not in report
    assert "difference_object" not in report
    assert "next_action" not in report
    assert "operator_response" not in report
    assert "runtime_state" not in report
