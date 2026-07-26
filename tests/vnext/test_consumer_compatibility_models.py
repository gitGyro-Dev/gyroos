import pytest
from pydantic import ValidationError

from app.vnext.consumer_compatibility import (
    ExperimentalCompatibilitySettings,
    ExperimentalContractDescriptor,
    SemanticVersion,
)


def test_settings_reject_non_positive_limits() -> None:
    with pytest.raises(ValueError):
        ExperimentalCompatibilitySettings(max_warning_count=0)


def test_semantic_version_parse_and_label() -> None:
    version = SemanticVersion.parse("1.2.3")

    assert version.major == 1
    assert version.minor == 2
    assert version.patch == 3
    assert version.label() == "1.2.3"


def test_semantic_version_rejects_non_numeric_or_partial_label() -> None:
    for raw in ("1", "1.2", "1.2.x", "v1.2.3"):
        with pytest.raises(ValueError):
            SemanticVersion.parse(raw)


def test_descriptor_normalizes_labels_and_exposes_versions() -> None:
    descriptor = ExperimentalContractDescriptor(
        source_api_namespace=" /vnext/experimental ",
        source_contract_version="1.2.0",
        consumer_contract_version="1.1.0",
        record_type=" TrajectoryGraph ",
    )

    assert descriptor.source_api_namespace == "/vnext/experimental"
    assert descriptor.record_type == "TrajectoryGraph"
    assert descriptor.source_version().major == 1
    assert descriptor.consumer_version().minor == 1


def test_descriptor_is_closed_and_rejects_blank_labels() -> None:
    with pytest.raises(ValidationError):
        ExperimentalContractDescriptor(
            source_api_namespace="",
            source_contract_version="1.0.0",
            consumer_contract_version="1.0.0",
            record_type="TrajectoryGraph",
        )

    with pytest.raises(ValidationError):
        ExperimentalContractDescriptor(
            source_api_namespace="/vnext/experimental",
            source_contract_version="1.0.0",
            consumer_contract_version="1.0.0",
            record_type="TrajectoryGraph",
            authentication_compatible=True,
        )


def test_descriptor_does_not_define_semantic_or_authentication_fields() -> None:
    fields = ExperimentalContractDescriptor.model_fields

    assert "auth_state" not in fields
    assert "auth_score" not in fields
    assert "semantic_equivalence" not in fields
    assert "canonical" not in fields
