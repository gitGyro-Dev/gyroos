from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def make_payload(
    *,
    source_version: str = "1.2.3",
    consumer_version: str = "1.2.3",
    namespace: str = "/vnext/experimental",
    record_type: str = "TrajectoryGraph",
    expected_record_type: str | None = "TrajectoryGraph",
) -> dict:
    return {
        "descriptor": {
            "source_api_namespace": namespace,
            "source_contract_version": source_version,
            "consumer_contract_version": consumer_version,
            "record_type": record_type,
        },
        "expected_record_type": expected_record_type,
    }


def test_compatibility_endpoint_returns_exact_match() -> None:
    response = client.post(
        "/vnext/experimental/compatibility/check",
        json=make_payload(),
    )

    assert response.status_code == 200
    assert response.json()["compatible_for_inspection"] is True
    assert response.json()["disposition"] == "COMPATIBLE"


def test_compatibility_endpoint_returns_warning_for_minor_patch_mismatch() -> None:
    response = client.post(
        "/vnext/experimental/compatibility/check",
        json=make_payload(source_version="1.3.4", consumer_version="1.2.3"),
    )

    assert response.status_code == 200
    assert response.json()["disposition"] == "COMPATIBLE_WITH_WARNING"
    assert response.json()["warnings"] == [
        "minor_version_mismatch",
        "patch_version_mismatch",
    ]


def test_compatibility_endpoint_returns_incompatible_result() -> None:
    response = client.post(
        "/vnext/experimental/compatibility/check",
        json=make_payload(source_version="2.0.0", consumer_version="1.0.0"),
    )

    assert response.status_code == 200
    assert response.json()["compatible_for_inspection"] is False
    assert response.json()["rejection_reason"] == "unsupported_source_major_version"


def test_compatibility_endpoint_returns_explicit_invalid_version_error() -> None:
    response = client.post(
        "/vnext/experimental/compatibility/check",
        json=make_payload(source_version="v1"),
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPATIBILITY_INVALID_VERSION"
    )
    assert response.json()["phase"] == "EXPERIMENTAL_COMPATIBILITY_CHECK"


def test_compatibility_endpoint_rejects_unknown_fields() -> None:
    payload = make_payload()
    payload["auth_state"] = "AUTH_STABLE"

    response = client.post(
        "/vnext/experimental/compatibility/check",
        json=payload,
    )

    assert response.status_code == 422


def test_compatibility_endpoint_is_registered_without_removing_existing_routes() -> None:
    paths = set(app.openapi()["paths"])

    assert "/vnext/experimental/compatibility/check" in paths
    assert "/vnext/experimental/records" in paths
    assert "/loop/step" in paths
