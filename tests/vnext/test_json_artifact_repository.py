import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.vnext.experimental_repository import ExperimentalRecordRepository
from app.vnext.json_artifact_repository import (
    ArtifactDeserializationError,
    ArtifactValidationError,
    InvalidArtifactRecordIdError,
    JsonArtifactExperimentalRecordRepository,
    JsonArtifactRepositorySettings,
)
from app.vnext.models import ExperimentalRecordEnvelope


def envelope(
    record_id: str = "record-001",
    *,
    process_id: str = "process-001",
    record_type: str = "TrajectoryGraph",
    payload: dict[str, object] | None = None,
) -> ExperimentalRecordEnvelope:
    return ExperimentalRecordEnvelope(
        record_id=record_id,
        process_id=process_id,
        record_type=record_type,
        payload=payload or {"nested": {"value": 1}},
        source_ref="source-001",
        provisional=True,
        stored_at=datetime(2026, 7, 26, tzinfo=timezone.utc),
        metadata={"labels": ["experimental"]},
    )


def repository(tmp_path: Path) -> JsonArtifactExperimentalRecordRepository:
    return JsonArtifactExperimentalRecordRepository(
        JsonArtifactRepositorySettings(root=tmp_path)
    )


def test_repository_implements_experimental_contract(tmp_path: Path) -> None:
    assert isinstance(repository(tmp_path), ExperimentalRecordRepository)


def test_save_and_get_round_trip_one_record_per_file(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    original = envelope()

    saved = repo.save(original)
    loaded = repo.get(original.record_id)

    assert saved == original
    assert loaded == original
    artifact = tmp_path / "record-001.json"
    assert artifact.exists()
    assert json.loads(artifact.read_text(encoding="utf-8"))["record_id"] == "record-001"
    assert list(tmp_path.glob("*.json")) == [artifact]


def test_save_and_get_are_deep_copy_boundaries(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    original = envelope()

    repo.save(original)
    original.payload["nested"]["value"] = 99  # type: ignore[index]
    loaded = repo.get("record-001")
    assert loaded is not None
    assert loaded.payload["nested"]["value"] == 1  # type: ignore[index]

    loaded.payload["nested"]["value"] = 77  # type: ignore[index]
    reloaded = repo.get("record-001")
    assert reloaded is not None
    assert reloaded.payload["nested"]["value"] == 1  # type: ignore[index]


def test_same_id_save_replaces_file_without_version_semantics(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.save(envelope(payload={"value": 1}))
    repo.save(envelope(payload={"value": 2}))

    loaded = repo.get("record-001")
    assert loaded is not None
    assert loaded.payload == {"value": 2}
    assert len(list(tmp_path.glob("*.json"))) == 1
    assert not list(tmp_path.glob("*.tmp"))


def test_list_filters_without_order_guarantee(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.save(envelope("record-a", process_id="process-a", record_type="TrajectoryGraph"))
    repo.save(envelope("record-b", process_id="process-a", record_type="RuntimeSnapshot"))
    repo.save(envelope("record-c", process_id="process-b", record_type="TrajectoryGraph"))

    all_ids = {item.record_id for item in repo.list()}
    process_ids = {item.record_id for item in repo.list(process_id="process-a")}
    type_ids = {item.record_id for item in repo.list(record_type="TrajectoryGraph")}
    combined_ids = {
        item.record_id
        for item in repo.list(process_id="process-a", record_type="TrajectoryGraph")
    }

    assert all_ids == {"record-a", "record-b", "record-c"}
    assert process_ids == {"record-a", "record-b"}
    assert type_ids == {"record-a", "record-c"}
    assert combined_ids == {"record-a"}


def test_delete_returns_boolean(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.save(envelope())

    assert repo.delete("record-001") is True
    assert repo.delete("record-001") is False
    assert repo.get("record-001") is None


def test_invalid_record_id_is_rejected_before_storage(tmp_path: Path) -> None:
    repo = repository(tmp_path)

    with pytest.raises(InvalidArtifactRecordIdError):
        repo.save(envelope("../escape"))

    assert not list(tmp_path.rglob("*"))


def test_corrupt_json_is_not_silently_ignored(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "record-001.json").write_text("{not-json", encoding="utf-8")
    repo = repository(tmp_path)

    with pytest.raises(ArtifactDeserializationError):
        repo.get("record-001")


def test_invalid_envelope_is_not_silently_ignored(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "record-001.json").write_text(
        json.dumps({"record_id": "record-001"}), encoding="utf-8"
    )
    repo = repository(tmp_path)

    with pytest.raises(ArtifactValidationError):
        repo.get("record-001")


def test_filename_must_match_envelope_record_id(tmp_path: Path) -> None:
    tmp_path.mkdir(parents=True, exist_ok=True)
    data = envelope("other-record").model_dump(mode="json")
    (tmp_path / "record-001.json").write_text(json.dumps(data), encoding="utf-8")
    repo = repository(tmp_path)

    with pytest.raises(ArtifactValidationError):
        repo.get("record-001")


def test_repository_does_not_add_canonical_or_typed_fields(tmp_path: Path) -> None:
    repo = repository(tmp_path)
    repo.save(envelope())
    loaded = repo.get("record-001")
    assert loaded is not None

    dumped = loaded.model_dump()
    for forbidden in (
        "canonical",
        "current",
        "latest",
        "version",
        "supersedes_ref",
        "trajectory_position",
        "typed_model",
    ):
        assert forbidden not in dumped
