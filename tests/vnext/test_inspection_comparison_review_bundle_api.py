from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def payload() -> dict:
    return {
        "review_bundle_id": "bundle-001",
        "comparison_references": [
            {
                "comparison_id": "comparison-a",
                "left_manifest_id": "manifest-left-a",
                "right_manifest_id": "manifest-right-a",
                "added_count": 1,
                "removed_count": 2,
                "retained_count": 3,
                "digest_changed": True,
            },
            {
                "comparison_id": "comparison-b",
                "left_manifest_id": "manifest-left-b",
                "right_manifest_id": "manifest-right-b",
                "added_count": 0,
                "removed_count": 1,
                "retained_count": 4,
                "digest_changed": False,
            },
        ],
        "warnings": ["caller_warning"],
        "source_refs": ["comparison-a"],
        "metadata": {"purpose": "inspection-review"},
    }


def test_create_review_bundle_returns_request_local_result() -> None:
    response = client.post(
        "/vnext/experimental/inspection-comparison-review-bundles",
        json=payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["review_bundle_created"] is True
    assert body["bundle"]["review_bundle_id"] == "bundle-001"
    assert len(body["bundle"]["ordered_reference_digest"]) == 64
    assert [
        item["comparison_id"] for item in body["bundle"]["comparison_references"]
    ] == ["comparison-a", "comparison-b"]


def test_create_review_bundle_rejects_duplicate_comparison_ids() -> None:
    body = payload()
    body["comparison_references"][1]["comparison_id"] = "comparison-a"

    response = client.post(
        "/vnext/experimental/inspection-comparison-review-bundles",
        json=body,
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REVIEW_BUNDLE_INVALID"
    )


def test_review_bundle_endpoint_does_not_expose_retrieval_routes() -> None:
    paths = set(app.openapi()["paths"])

    assert "/vnext/experimental/inspection-comparison-review-bundles" in paths
    assert (
        "/vnext/experimental/inspection-comparison-review-bundles/{review_bundle_id}"
        not in paths
    )


def test_existing_routes_remain_registered() -> None:
    paths = set(app.openapi()["paths"])

    assert "/loop/step" in paths
    assert "/vnext/experimental/records" in paths
    assert "/vnext/experimental/compatibility/check" in paths
    assert "/vnext/experimental/inspection-receipts" in paths
    assert "/vnext/experimental/inspection-batch-manifests" in paths
    assert "/vnext/experimental/inspection-manifest-comparisons" in paths


def test_review_bundle_response_does_not_define_runtime_authentication_or_semantic_outputs() -> None:
    body = client.post(
        "/vnext/experimental/inspection-comparison-review-bundles",
        json=payload(),
    ).json()["bundle"]

    assert "auth_state" not in body
    assert "risk_level" not in body
    assert "semantic_trend" not in body
    assert "operator_response" not in body
    assert "runtime_state" not in body
