from app.vnext.experimental_repository import (
    ExperimentalRecordRepository,
    InMemoryExperimentalRecordRepository,
)
from app.vnext.models import ExperimentalRecordEnvelope


def envelope(
    record_id: str,
    *,
    process_id: str = "process-1",
    record_type: str = "StabilityScene",
) -> ExperimentalRecordEnvelope:
    return ExperimentalRecordEnvelope(
        record_id=record_id,
        process_id=process_id,
        record_type=record_type,
        payload={"nested": {"value": 1}},
        source_ref="source-1",
        metadata={"labels": ["experimental"]},
    )


def test_in_memory_repository_implements_contract() -> None:
    repository = InMemoryExperimentalRecordRepository()
    assert isinstance(repository, ExperimentalRecordRepository)


def test_save_and_get_use_deep_copy_boundaries() -> None:
    repository = InMemoryExperimentalRecordRepository()
    original = envelope("record-1")

    saved = repository.save(original)
    original.payload["nested"]["value"] = 99
    original.metadata["labels"].append("changed")
    saved.payload["nested"]["value"] = 88

    loaded = repository.get("record-1")
    assert loaded is not None
    assert loaded.payload == {"nested": {"value": 1}}
    assert loaded.metadata == {"labels": ["experimental"]}


def test_save_replaces_same_record_id_without_version_inference() -> None:
    repository = InMemoryExperimentalRecordRepository()
    repository.save(envelope("record-1"))
    replacement = envelope("record-1", record_type="TrajectoryGraph")
    replacement.payload = {"revision": 2}

    repository.save(replacement)

    loaded = repository.get("record-1")
    assert loaded is not None
    assert loaded.record_type == "TrajectoryGraph"
    assert loaded.payload == {"revision": 2}
    assert len(repository.list()) == 1


def test_list_filters_by_process_and_record_type() -> None:
    repository = InMemoryExperimentalRecordRepository()
    repository.save(envelope("record-1", process_id="process-1", record_type="StabilityScene"))
    repository.save(envelope("record-2", process_id="process-1", record_type="TrajectoryGraph"))
    repository.save(envelope("record-3", process_id="process-2", record_type="TrajectoryGraph"))

    assert {item.record_id for item in repository.list(process_id="process-1")} == {
        "record-1",
        "record-2",
    }
    assert {item.record_id for item in repository.list(record_type="TrajectoryGraph")} == {
        "record-2",
        "record-3",
    }
    assert [
        item.record_id
        for item in repository.list(
            process_id="process-1",
            record_type="TrajectoryGraph",
        )
    ] == ["record-2"]


def test_list_returns_independent_copies() -> None:
    repository = InMemoryExperimentalRecordRepository()
    repository.save(envelope("record-1"))

    listed = repository.list()
    listed[0].payload["nested"]["value"] = 999

    loaded = repository.get("record-1")
    assert loaded is not None
    assert loaded.payload["nested"]["value"] == 1


def test_delete_reports_whether_record_existed() -> None:
    repository = InMemoryExperimentalRecordRepository()
    repository.save(envelope("record-1"))

    assert repository.delete("record-1") is True
    assert repository.get("record-1") is None
    assert repository.delete("record-1") is False


def test_repository_does_not_add_canonical_or_ordering_fields() -> None:
    repository = InMemoryExperimentalRecordRepository()
    stored = repository.save(envelope("record-1"))

    fields = type(stored).model_fields
    assert "canonical" not in fields
    assert "authoritative" not in fields
    assert "current" not in fields
    assert "version" not in fields
    assert "sequence" not in fields
    assert "trajectory_order" not in fields
