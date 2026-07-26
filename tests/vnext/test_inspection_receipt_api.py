from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def payload(compatible: bool = True) -> dict:
    disposition = "COMPATIBLE" if compatible else "INCOMPATIBLE"
    return {
        "receipt_id": "receipt-001",
        "source_record_id": "record-001",
        "source_process_id": "process-001",
        "source_record_type": "TrajectoryGraph",
        "source_contract": {
            "api_namespace": "/vnext/experimental",
            "contract_version": "1.0.0",
            "record_type": "TrajectoryGraph"
        },
        "consumer_contract": {
            "api_namespace": "/vnext/experimental",
            "contract_version": "1.0.0",
            "record_type": "TrajectoryGraph"
        },
        "compatibility_result": {
            "compatible_for_inspection": compatible,
            "disposition": disposition,
            "source_contract_version": "1.0.0",
            "consumer_contract_version": "1.0.0",
            "warnings": [],
            "rejection_reason": None if compatible else "unsupported_major_version"
        },
        "payload": {"nodes": []},
        "source_metadata": {"source": "api"},
        "source_refs": ["record-001"],
        "warnings": [],
        "receipt_metadata": {"purpose": "inspection"}
    }


def test_create_receipt_returns_request_local_result() -> None:
    response = client.post("/vnext/experimental/inspection-receipts", json=payload())

    assert response.status_code == 201
    body = response.json()
    assert body["receipt_created"] is True
    assert body["receipt"]["receipt_id"] == "receipt-001"
    assert len(body["receipt"]["payload_digest"]) == 64
    assert "payload" not in body["receipt"]
    assert "source_metadata" not in body["receipt"]


def test_create_receipt_can_record_incompatible_attempt() -> None:
    response = client.post(
        "/vnext/experimental/inspection-receipts",
        json=payload(compatible=False),
    )

    assert response.status_code == 201
    assert response.json()["receipt"]["compatibility_result"][
        "compatible_for_inspection"
    ] is False


def test_create_receipt_rejects_descriptor_mismatch() -> None:
    body = payload()
    body["source_contract"]["record_type"] = "StabilityScene"

    response = client.post("/vnext/experimental/inspection-receipts", json=body)

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_INSPECTION_RECEIPT_INVALID"
    )


def test_receipt_endpoint_does_not_expose_retrieval_routes() -> None:
    paths = set(app.openapi()["paths"])

    assert "/vnext/experimental/inspection-receipts" in paths
    assert "/vnext/experimental/inspection-receipts/{receipt_id}" not in paths


def test_existing_routes_remain_registered() -> None:
    paths = set(app.openapi()["paths"])

    assert "/loop/step" in paths
    assert "/vnext/experimental/records" in paths
    assert "/vnext/experimental/compatibility/check" in paths


def test_receipt_response_does_not_define_authentication_or_runtime_outputs() -> None:
    body = client.post(
        "/vnext/experimental/inspection-receipts",
        json=payload(),
    ).json()["receipt"]

    assert "auth_state" not in body
    assert "auth_score" not in body
    assert "next_action" not in body
    assert "operator_response" not in body
    assert "runtime_state" not in body
