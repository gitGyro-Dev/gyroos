from pathlib import Path

import pytest

from app.vnext.json_artifact_repository import (
    InvalidArtifactRecordIdError,
    JsonArtifactPathPolicy,
    JsonArtifactRepositorySettings,
)


def make_policy(tmp_path: Path) -> JsonArtifactPathPolicy:
    return JsonArtifactPathPolicy(JsonArtifactRepositorySettings(root=tmp_path))


def test_artifact_path_is_contained_in_repository_root(tmp_path: Path) -> None:
    policy = make_policy(tmp_path)

    path = policy.artifact_path("record-001")

    assert path == tmp_path.resolve() / "record-001.json"
    assert path.parent == policy.root


def test_temporary_path_is_same_directory_and_unique(tmp_path: Path) -> None:
    policy = make_policy(tmp_path)

    first = policy.temporary_path("record-001")
    second = policy.temporary_path("record-001")

    assert first.parent == policy.root
    assert second.parent == policy.root
    assert first != second
    assert first.name.startswith(".record-001.json.")
    assert first.name.endswith(".tmp")


@pytest.mark.parametrize(
    "record_id",
    [
        "",
        ".",
        "..",
        "../escape",
        "folder/record",
        "folder\\record",
        "/absolute",
        "record\x00id",
    ],
)
def test_unsafe_record_ids_are_rejected(tmp_path: Path, record_id: str) -> None:
    policy = make_policy(tmp_path)

    with pytest.raises(InvalidArtifactRecordIdError):
        policy.artifact_path(record_id)


def test_custom_suffix_is_applied_without_changing_record_identity(tmp_path: Path) -> None:
    settings = JsonArtifactRepositorySettings(root=tmp_path, suffix=".artifact.json")
    policy = JsonArtifactPathPolicy(settings)

    assert policy.artifact_path("record-001").name == "record-001.artifact.json"


def test_policy_does_not_create_directories_or_files(tmp_path: Path) -> None:
    root = tmp_path / "not-created"
    policy = JsonArtifactPathPolicy(JsonArtifactRepositorySettings(root=root))

    path = policy.artifact_path("record-001")

    assert path.parent == root.resolve()
    assert not root.exists()
    assert not path.exists()
