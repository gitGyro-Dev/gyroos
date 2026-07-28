from datetime import UTC, datetime

from fastapi.responses import JSONResponse

from app.vnext.experimental_api_routes import (
    create_experimental_inspection_comparison_ledger_comparison,
)
from app.vnext.inspection_comparison_ledger_comparison import (
    ExperimentalComparisonLedgerComparisonRequest,
    ExperimentalComparisonLedgerReference,
)


def make_request(left_id: str = "ledger-left", right_id: str = "ledger-right"):
    return ExperimentalComparisonLedgerComparisonRequest(
        ledger_comparison_id="ledger-comparison-1",
        left=ExperimentalComparisonLedgerReference(
            comparison_ledger_id=left_id,
            register_comparison_ids=("register-1", "register-2"),
            ledger_digest="a" * 64,
        ),
        right=ExperimentalComparisonLedgerReference(
            comparison_ledger_id=right_id,
            register_comparison_ids=("register-2", "register-3"),
            ledger_digest="b" * 64,
        ),
        created_at=datetime.now(UTC),
    )


def test_endpoint_returns_request_local_comparison_result():
    result = create_experimental_inspection_comparison_ledger_comparison(make_request())

    assert result.result == "comparison_ledger_comparison_created"
    assert result.report.added_register_comparison_ids == ("register-3",)
    assert result.report.removed_register_comparison_ids == ("register-1",)
    assert result.report.retained_register_comparison_ids == ("register-2",)
    assert result.report.digest_changed is True


def test_endpoint_maps_validation_error_to_422():
    response = create_experimental_inspection_comparison_ledger_comparison(
        make_request(left_id="ledger-same", right_id="ledger-same")
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 422
    assert b"GYRO_VNEXT_EXPERIMENTAL_COMPARISON_LEDGER_COMPARISON_INVALID" in response.body


def test_router_exposes_creation_only_for_ledger_comparisons():
    from app.vnext.experimental_api_routes import router

    matching = [
        route
        for route in router.routes
        if route.path.startswith(
            "/vnext/experimental/inspection-comparison-ledger-comparisons"
        )
    ]

    assert len(matching) == 1
    assert matching[0].methods == {"POST"}


def test_endpoint_output_has_no_runtime_authentication_or_semantic_fields():
    result = create_experimental_inspection_comparison_ledger_comparison(make_request())
    report = result.report.model_dump()

    assert "operator_response" not in report
    assert "auth_state" not in report
    assert "risk" not in report
    assert "difference_object" not in report
    assert "boundary_evaluation" not in report
