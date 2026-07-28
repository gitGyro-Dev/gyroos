from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-token"}


def payload() -> dict:
    return {
        "comparison_archive_id": "archive-1",
        "ledger_comparisons": [
            {
                "ledger_comparison_id": "ledger-cmp-1",
                "left_comparison_ledger_id": "ledger-left-1",
                "right_comparison_ledger_id": "ledger-right-1",
                "added_count": 1,
                "removed_count": 0,
                "retained_count": 2,
                "digest_changed": True,
            }
        ],
        "created_at": "2026-07-28T00:00:00Z",
        "warnings": [],
        "source_refs": ["test"],
        "metadata": {"scope": "request-local"},
    }


def test_create_comparison_archive_endpoint() -> None:
    response = client.post(
        "/vnext/experimental/inspection-comparison-ledger-comparison-archives",
        headers=HEADERS,
        json=payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["result"] == "comparison_archive_created"
    assert body["manifest"]["comparison_archive_id"] == "archive-1"
    assert body["manifest"]["reference_count"] == 1
    assert len(body["manifest"]["archive_digest"]) == 64


def test_create_comparison_archive_rejects_duplicate_references() -> None:
    body = payload()
    body["ledger_comparisons"].append(dict(body["ledger_comparisons"][0]))

    response = client.post(
        "/vnext/experimental/inspection-comparison-ledger-comparison-archives",
        headers=HEADERS,
        json=body,
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_LEDGER_COMPARISON_ARCHIVE_INVALID"
    )


def test_comparison_archive_retrieval_routes_are_absent() -> None:
    assert client.get(
        "/vnext/experimental/inspection-comparison-ledger-comparison-archives/archive-1",
        headers=HEADERS,
    ).status_code == 404

    assert client.get(
        "/vnext/experimental/inspection-comparison-ledger-comparison-archives",
        headers=HEADERS,
    ).status_code == 405


def test_comparison_archive_response_has_no_runtime_or_authentication_outputs() -> None:
    response = client.post(
        "/vnext/experimental/inspection-comparison-ledger-comparison-archives",
        headers=HEADERS,
        json=payload(),
    )
    text = response.text

    assert "operator_response" not in text
    assert "auth_state" not in text
    assert "risk" not in text
    assert "difference_object" not in text
