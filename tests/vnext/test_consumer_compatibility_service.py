import pytest

from app.vnext.consumer_compatibility import (
    CompatibilityDisposition,
    ExperimentalCompatibilitySettings,
    ExperimentalConsumerCompatibilityRequest,
    ExperimentalContractDescriptor,
)
from app.vnext.consumer_compatibility_service import (
    ExperimentalCompatibilityError,
    ExperimentalCompatibilityPolicy,
    ExperimentalConsumerCompatibilityService,
)


def make_request(
    *,
    source_version: str = "1.2.3",
    consumer_version: str = "1.2.3",
    namespace: str = "/vnext/experimental",
    record_type: str = "TrajectoryGraph",
    expected_record_type: str | None = "TrajectoryGraph",
) -> ExperimentalConsumerCompatibilityRequest:
    return ExperimentalConsumerCompatibilityRequest(
        descriptor=ExperimentalContractDescriptor(
            source_api_namespace=namespace,
            source_contract_version=source_version,
            consumer_contract_version=consumer_version,
            record_type=record_type,
        ),
        expected_record_type=expected_record_type,
    )


def test_exact_versions_are_compatible_for_inspection() -> None:
    result = ExperimentalConsumerCompatibilityService().check(make_request())

    assert result.compatible_for_inspection is True
    assert result.disposition == CompatibilityDisposition.COMPATIBLE
    assert result.warnings == []
    assert result.rejection_reason is None


def test_minor_and_patch_mismatch_are_warnings_only() -> None:
    result = ExperimentalConsumerCompatibilityService().check(
        make_request(source_version="1.3.4", consumer_version="1.2.3")
    )

    assert result.compatible_for_inspection is True
    assert result.disposition == CompatibilityDisposition.COMPATIBLE_WITH_WARNING
    assert result.warnings == ["minor_version_mismatch", "patch_version_mismatch"]


def test_namespace_mismatch_is_incompatible() -> None:
    result = ExperimentalConsumerCompatibilityService().check(
        make_request(namespace="/other")
    )

    assert result.compatible_for_inspection is False
    assert result.rejection_reason == "source_api_namespace_mismatch"


def test_unsupported_source_or_consumer_major_is_incompatible() -> None:
    source_result = ExperimentalConsumerCompatibilityService().check(
        make_request(source_version="2.0.0", consumer_version="1.0.0")
    )
    consumer_result = ExperimentalConsumerCompatibilityService().check(
        make_request(source_version="1.0.0", consumer_version="2.0.0")
    )

    assert source_result.rejection_reason == "unsupported_source_major_version"
    assert consumer_result.rejection_reason == "unsupported_consumer_major_version"


def test_record_type_mismatch_is_incompatible_without_reconstruction() -> None:
    result = ExperimentalConsumerCompatibilityService().check(
        make_request(record_type="TrajectoryGraph", expected_record_type="StabilityScene")
    )

    assert result.compatible_for_inspection is False
    assert result.rejection_reason == "record_type_mismatch"


def test_invalid_version_is_explicit_policy_error() -> None:
    request = make_request(source_version="v1")

    with pytest.raises(ExperimentalCompatibilityError):
        ExperimentalConsumerCompatibilityService().check(request)


def test_policy_respects_configured_major_versions() -> None:
    policy = ExperimentalCompatibilityPolicy(
        ExperimentalCompatibilitySettings(
            supported_source_major=2,
            supported_consumer_major=2,
        )
    )
    result = policy.evaluate(
        make_request(source_version="2.0.0", consumer_version="2.0.0")
    )

    assert result.compatible_for_inspection is True


def test_result_does_not_define_authentication_or_semantic_outcomes() -> None:
    result = ExperimentalConsumerCompatibilityService().check(make_request())
    fields = result.__class__.model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "semantic_equivalence" not in fields
    assert "migration_action" not in fields
