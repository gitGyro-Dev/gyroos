import pytest

from app.vnext.inspection_manifest_comparison import (
    ExperimentalManifestComparisonRequest,
    ExperimentalManifestComparisonSettings,
    ExperimentalManifestReference,
)
from app.vnext.inspection_manifest_comparison_service import (
    ExperimentalManifestComparisonDuplicateError,
    ExperimentalManifestComparisonIdentityError,
    ExperimentalManifestComparisonResourceLimitError,
    ExperimentalManifestComparisonService,
)


def reference(
    manifest_id: str,
    receipt_ids: tuple[str, ...],
    digest: str | None,
) -> ExperimentalManifestReference:
    return ExperimentalManifestReference(
        manifest_id=manifest_id,
        receipt_ids=receipt_ids,
        manifest_digest=digest,
    )


def request(**overrides) -> ExperimentalManifestComparisonRequest:
    values = {
        "comparison_id": "comparison-001",
        "left": reference(
            "manifest-left",
            ("receipt-001", "receipt-002", "receipt-003"),
            "a" * 64,
        ),
        "right": reference(
            "manifest-right",
            ("receipt-002", "receipt-003", "receipt-004"),
            "b" * 64,
        ),
        "warnings": ("caller_warning",),
        "metadata": {"purpose": "reference-comparison"},
    }
    values.update(overrides)
    return ExperimentalManifestComparisonRequest(**values)


def test_service_creates_reference_level_comparison_report() -> None:
    result = ExperimentalManifestComparisonService().compare(request())

    assert result.comparison_report_created is True
    assert result.report.added_receipt_ids == ("receipt-004",)
    assert result.report.removed_receipt_ids == ("receipt-001",)
    assert result.report.retained_receipt_ids == ("receipt-002", "receipt-003")
    assert result.report.digest_changed is True
    assert result.report.warnings == ("caller_warning",)


def test_service_preserves_left_and_right_ordering() -> None:
    result = ExperimentalManifestComparisonService().compare(
        request(
            left=reference("manifest-left", ("c", "a", "b"), "a" * 64),
            right=reference("manifest-right", ("b", "d", "a"), "b" * 64),
        )
    )

    assert result.report.added_receipt_ids == ("d",)
    assert result.report.removed_receipt_ids == ("c",)
    assert result.report.retained_receipt_ids == ("a", "b")


def test_service_sets_digest_changed_none_when_digest_is_missing() -> None:
    result = ExperimentalManifestComparisonService().compare(
        request(
            left=reference("manifest-left", ("receipt-001",), None),
            right=reference("manifest-right", ("receipt-001",), "b" * 64),
        )
    )

    assert result.report.digest_changed is None


def test_service_rejects_same_manifest_identity() -> None:
    with pytest.raises(ExperimentalManifestComparisonIdentityError):
        ExperimentalManifestComparisonService().compare(
            request(
                left=reference("manifest-same", ("receipt-001",), "a" * 64),
                right=reference("manifest-same", ("receipt-002",), "b" * 64),
            )
        )


def test_service_rejects_duplicate_receipt_ids_within_side() -> None:
    with pytest.raises(ExperimentalManifestComparisonDuplicateError):
        ExperimentalManifestComparisonService().compare(
            request(
                left=reference(
                    "manifest-left",
                    ("receipt-001", "receipt-001"),
                    "a" * 64,
                )
            )
        )


def test_service_enforces_receipt_count_limit() -> None:
    service = ExperimentalManifestComparisonService(
        settings=ExperimentalManifestComparisonSettings(
            max_receipt_count_per_manifest=1
        )
    )

    with pytest.raises(ExperimentalManifestComparisonResourceLimitError):
        service.compare(request())


def test_service_enforces_metadata_limit() -> None:
    service = ExperimentalManifestComparisonService(
        settings=ExperimentalManifestComparisonSettings(max_metadata_bytes=8)
    )

    with pytest.raises(ExperimentalManifestComparisonResourceLimitError):
        service.compare(request(metadata={"value": "too-large"}))


def test_report_does_not_define_runtime_or_authentication_outputs() -> None:
    report = ExperimentalManifestComparisonService().compare(request()).report
    fields = type(report).model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
    assert "security_risk" not in fields
