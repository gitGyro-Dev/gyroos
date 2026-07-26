from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def receipt_reference(receipt_id: str, record_id: str) -> dict:
    return {
        "receipt_id": receipt_id,
        "source_record_id": record_id,
        "source_process_id": "process-001",
        "source_record_type": "TrajectoryGraph",
        "source_contract_version": "1.0.0",
        "consumer_contract_version": "1.0.0",
        "compatible_for_inspection": True,
        "payload_digest": "a" * 64,
        "metadata_digest": "b" * 64,
    }


def payload() -> dict:
    return {
        "manifest_id": "manifest-001",
        "receipt_references": [
            receipt_reference("receipt-001", "record-001"),
            receipt_reference("receipt-002", "record-002"),
        ],
        "warnings": ["caller_warning"],
        "source_refs": ["batch-source"],
        "manifest_metadata": {"purpose": "review"},
    }


def test_create_manifest_returns_request_local_result() -> None:
    response = client.post(
        "/vnext/experimental/inspection-batch-manifests",
        json=payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["batch_manifest_created"] is True
    assert body["manifest"]["manifest_id"] == "manifest-001"
    assert len(body["manifest"]["receipt_reference_digest"]) == 64
    assert len(body["manifest"]["receipt_references"]) == 2


def test_create_manifest_rejects_duplicate_receipt_ids() -> None:
    body = payload()
    body["receipt_references"][1]["receipt_id"] = "receipt-001"

    response = client.post(
        "/vnext/experimental/inspection-batch-manifests",
        json=body,
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_INSPECTION_BATCH_INVALID"
    )


def test_manifest_endpoint_does_not_expose_retrieval_routes() -> None:
    paths = set(app.openapi()["paths"])

    assert "/vnext/experimental/inspection-batch-manifests" in paths
    assert (
        "/vnext/experimental/inspection-batch-manifests/{manifest_id}" not in paths
    )


def test_existing_routes_remain_registered() -> None:
    paths = set(app.openapi()["paths"])

    assert "/loop/step" in paths
    assert "/vnext/experimental/records" in paths
    assert "/vnext/experimental/compatibility/check" in paths
    assert "/vnext/experimental/inspection-receipts" in paths


def test_manifest_response_does_not_define_authentication_or_runtime_outputs() -> None:
    manifest = client.post(
        "/vnext/experimental/inspection-batch-manifests",
        json=payload(),
    ).json()["manifest"]

    assert "auth_state" not in manifest
    assert "auth_score" not in manifest
    assert "next_action" not in manifest
    assert "operator_response" not in manifest
    assert "runtime_state" not in manifest
