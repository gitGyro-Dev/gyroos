import pytest
from pydantic import ValidationError

from app.vnext.inspection_manifest_comparison import (
    ExperimentalManifestComparisonRequest,
    ExperimentalManifestComparisonSettings,
    ExperimentalManifestReference,
)


def reference(manifest_id: str = "manifest-left") -> ExperimentalManifestReference:
    return ExperimentalManifestReference(
        manifest_id=manifest_id,
        receipt_ids=("receipt-001", "receipt-002"),
        manifest_digest="a" * 64,
    )


def test_settings_reject_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        ExperimentalManifestComparisonSettings(max_receipt_count_per_manifest=0)


def test_manifest_reference_normalizes_digest_and_is_frozen() -> None:
    item = ExperimentalManifestReference(
        manifest_id=" manifest-left ",
        receipt_ids=(" receipt-001 ",),
        manifest_digest="A" * 64,
    )

    assert item.manifest_id == "manifest-left"
    assert item.receipt_ids == ("receipt-001",)
    assert item.manifest_digest == "a" * 64

    with pytest.raises(ValidationError):
        item.manifest_id = "changed"


def test_manifest_reference_rejects_invalid_digest_label() -> None:
    with pytest.raises(ValidationError):
        ExperimentalManifestReference(
            manifest_id="manifest-left",
            receipt_ids=("receipt-001",),
            manifest_digest="not-hex",
        )


def test_comparison_request_is_closed() -> None:
    with pytest.raises(ValidationError):
        ExperimentalManifestComparisonRequest(
            comparison_id="comparison-001",
            left=reference(),
            right=reference("manifest-right"),
            auth_state="AUTH_STABLE",
        )


def test_comparison_models_do_not_define_runtime_or_authentication_fields() -> None:
    fields = ExperimentalManifestComparisonRequest.model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "next_action" not in fields
    assert "operator_response" not in fields
    assert "runtime_state" not in fields
    assert "difference_object" not in fields
