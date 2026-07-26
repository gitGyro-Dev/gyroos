from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def payload() -> dict:
    return {
        "comparison_id": "comparison-001",
        "left": {
            "manifest_id": "manifest-left",
            "receipt_ids": ["receipt-001", "receipt-002"],
            "manifest_digest": "a" * 64,
        },
        "right": {
            "manifest_id": "manifest-right",
            "receipt_ids": ["receipt-002", "receipt-003"],
            "manifest_digest": "b" * 64,
        },
        "warnings": ["caller_warning"],
        "metadata": {"purpose": "reference-comparison"},
    }


def test_create_comparison_returns_request_local_result() -> None:
    response = client.post(
        "/vnext/experimental/inspection-manifest-comparisons",
        json=payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["comparison_report_created"] is True
    assert body["report"]["added_receipt_ids"] == ["receipt-003"]
    assert body["report"]["removed_receipt_ids"] == ["receipt-001"]
    assert body["report"]["retained_receipt_ids"] == ["receipt-002"]
    assert body["report"]["digest_changed"] is True


def test_create_comparison_rejects_same_manifest() -> None:
    body = payload()
    body["right"]["manifest_id"] = "manifest-left"

    response = client.post(
        "/vnext/experimental/inspection-manifest-comparisons",
        json=body,
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_MANIFEST_COMPARISON_INVALID"
    )


def test_comparison_endpoint_does_not_expose_retrieval_routes() -> None:
    paths = set(app.openapi()["paths"])

    assert "/vnext/experimental/inspection-manifest-comparisons" in paths
    assert (
        "/vnext/experimental/inspection-manifest-comparisons/{comparison_id}"
        not in paths
    )


def test_existing_routes_remain_registered() -> None:
    paths = set(app.openapi()["paths"])

    assert "/loop/step" in paths
    assert "/vnext/experimental/records" in paths
    assert "/vnext/experimental/compatibility/check" in paths
    assert "/vnext/experimental/inspection-receipts" in paths
    assert "/vnext/experimental/inspection-batch-manifests" in paths


def test_comparison_response_does_not_define_runtime_or_authentication_outputs() -> None:
    body = client.post(
        "/vnext/experimental/inspection-manifest-comparisons",
        json=payload(),
    ).json()["report"]

    assert "auth_state" not in body
    assert "auth_score" not in body
    assert "next_action" not in body
    assert "operator_response" not in body
    assert "runtime_state" not in body
    assert "difference_object" not in body
    assert "security_risk" not in body
