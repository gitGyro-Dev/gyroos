from pathlib import Path

import pytest

from app.vnext.json_artifact_repository import (
    ArtifactDeserializationError,
    ArtifactSerializationError,
    ArtifactStorageError,
    ArtifactValidationError,
    ExperimentalRepositoryError,
    InvalidArtifactRecordIdError,
    JsonArtifactRepositorySettings,
)


def test_error_hierarchy_is_repository_local() -> None:
    for error_type in (
        InvalidArtifactRecordIdError,
        ArtifactSerializationError,
        ArtifactDeserializationError,
        ArtifactValidationError,
        ArtifactStorageError,
    ):
        assert issubclass(error_type, ExperimentalRepositoryError)


def test_settings_copy_explicit_defaults() -> None:
    settings = JsonArtifactRepositorySettings(root=Path("artifacts/vnext"))

    assert settings.root == Path("artifacts/vnext")
    assert settings.encoding == "utf-8"
    assert settings.indent == 2
    assert settings.suffix == ".json"
    assert settings.fsync_on_save is True


def test_settings_are_immutable() -> None:
    settings = JsonArtifactRepositorySettings(root=Path("artifacts/vnext"))

    with pytest.raises(Exception):
        settings.encoding = "ascii"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"encoding": ""}, "encoding must not be empty"),
        ({"indent": -1}, "indent must be zero or greater"),
        ({"suffix": "json"}, "suffix must be"),
        ({"suffix": "."}, "suffix must be"),
    ],
)
def test_invalid_settings_are_rejected(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        JsonArtifactRepositorySettings(root=Path("artifacts/vnext"), **kwargs)


def test_settings_do_not_define_canonical_or_runtime_semantics() -> None:
    fields = JsonArtifactRepositorySettings.__dataclass_fields__

    for forbidden in (
        "canonical",
        "current",
        "latest",
        "runtime",
        "operator_response",
        "typed_reconstruction",
    ):
        assert forbidden not in fields
