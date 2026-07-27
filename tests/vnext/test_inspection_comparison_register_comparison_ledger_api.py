import json

from fastapi.responses import JSONResponse

from app.vnext.experimental_api_routes import (
    create_experimental_inspection_comparison_register_comparison_ledger,
    router as experimental_router,
)
from app.vnext.inspection_comparison_register_comparison_ledger import (
    ExperimentalComparisonRegisterComparisonLedgerRequest,
)


PATH = "/vnext/experimental/inspection-comparison-register-comparison-ledgers"


def payload() -> dict:
    return {
        "comparison_ledger_id": "ledger-001",
        "comparison_references": [
            {
                "register_comparison_id": "register-comparison-001",
                "left_comparison_register_id": "register-left",
                "right_comparison_register_id": "register-right",
                "added_count": 1,
                "removed_count": 1,
                "retained_count": 2,
                "digest_changed": True,
            }
        ],
        "warnings": [],
        "source_refs": [],
        "ledger_metadata": {"purpose": "inspection"},
    }


def test_create_ledger_returns_request_local_manifest() -> None:
    request = ExperimentalComparisonRegisterComparisonLedgerRequest(**payload())

    result = create_experimental_inspection_comparison_register_comparison_ledger(
        request
    )

    assert result.comparison_ledger_created is True
    assert result.manifest.comparison_ledger_id == "ledger-001"
    assert result.manifest.comparison_count == 1
    assert len(result.manifest.ledger_digest) == 64


def test_create_ledger_rejects_duplicate_reference() -> None:
    request_body = payload()
    request_body["comparison_references"].append(
        dict(request_body["comparison_references"][0])
    )
    request = ExperimentalComparisonRegisterComparisonLedgerRequest(**request_body)

    response = create_experimental_inspection_comparison_register_comparison_ledger(
        request
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    body = json.loads(response.body)
    assert body["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_LEDGER_INVALID"
    )


def test_response_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonRegisterComparisonLedgerRequest(**payload())
    manifest = create_experimental_inspection_comparison_register_comparison_ledger(
        request
    ).manifest
    fields = manifest.__class__.model_fields

    assert "auth_state" not in fields
    assert "risk_level" not in fields
    assert "semantic_trend" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields


def test_ledger_retrieval_routes_are_absent() -> None:
    registered_methods_by_path = {
        route.path: set(route.methods or set())
        for route in experimental_router.routes
        if hasattr(route, "path")
    }

    assert registered_methods_by_path[PATH] == {"POST"}
    assert f"{PATH}/{{comparison_ledger_id}}" not in registered_methods_by_path
