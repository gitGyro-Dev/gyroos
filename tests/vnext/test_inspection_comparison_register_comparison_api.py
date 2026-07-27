import json

from fastapi.responses import JSONResponse

from app.vnext.experimental_api_routes import (
    create_experimental_inspection_comparison_register_comparison,
    router as experimental_router,
)
from app.vnext.inspection_comparison_register_comparison import (
    ExperimentalComparisonRegisterComparisonRequest,
)
from app.vnext.inspection_comparison_register_comparison_service import (
    ExperimentalComparisonRegisterComparisonService,
)


PATH = "/vnext/experimental/inspection-comparison-register-comparisons"


def payload() -> dict:
    return {
        "register_comparison_id": "register-comparison-001",
        "left_register": {
            "comparison_register_id": "register-left",
            "sequence_comparison_ids": ["sequence-cmp-001", "sequence-cmp-002"],
            "register_digest": "a" * 64,
        },
        "right_register": {
            "comparison_register_id": "register-right",
            "sequence_comparison_ids": ["sequence-cmp-002", "sequence-cmp-003"],
            "register_digest": "b" * 64,
        },
        "warnings": [],
        "comparison_metadata": {"purpose": "inspection"},
    }


def test_create_comparison_returns_request_local_report() -> None:
    request = ExperimentalComparisonRegisterComparisonRequest(**payload())
    result = create_experimental_inspection_comparison_register_comparison(request)

    assert result.comparison_register_comparison_created is True
    assert result.report.added_sequence_comparison_ids == ("sequence-cmp-003",)
    assert result.report.removed_sequence_comparison_ids == ("sequence-cmp-001",)
    assert result.report.retained_sequence_comparison_ids == ("sequence-cmp-002",)
    assert result.report.digest_changed is True


def test_create_comparison_rejects_same_register() -> None:
    request_body = payload()
    request_body["right_register"]["comparison_register_id"] = "register-left"
    request = ExperimentalComparisonRegisterComparisonRequest(**request_body)

    response = create_experimental_inspection_comparison_register_comparison(request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    body = json.loads(response.body)
    assert body["error_code"] == (
        "GYRO_VNEXT_EXPERIMENTAL_COMPARISON_REGISTER_COMPARISON_INVALID"
    )


def test_response_has_no_runtime_authentication_or_semantic_outputs() -> None:
    request = ExperimentalComparisonRegisterComparisonRequest(**payload())
    report = ExperimentalComparisonRegisterComparisonService().compare(request).report
    fields = report.__class__.model_fields

    forbidden = {
        "auth_state",
        "risk_level",
        "semantic_trend",
        "operator_response",
        "runtime_state",
        "difference_object",
        "boundary_evaluation",
        "next_action",
    }
    assert forbidden.isdisjoint(fields)


def test_comparison_retrieval_routes_are_absent() -> None:
    registered_methods_by_path = {
        route.path: set(route.methods or set())
        for route in experimental_router.routes
        if hasattr(route, "path")
    }

    assert registered_methods_by_path[PATH] == {"POST"}
    assert f"{PATH}/{{register_comparison_id}}" not in registered_methods_by_path
