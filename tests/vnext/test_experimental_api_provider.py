from app.vnext.experimental_api_provider import ExperimentalRepositoryProvider
from app.vnext.experimental_repository import (
    ExperimentalRecordRepository,
    InMemoryExperimentalRecordRepository,
)


def test_provider_returns_repository_contract() -> None:
    repository = InMemoryExperimentalRecordRepository()
    provider = ExperimentalRepositoryProvider(repository)

    resolved = provider.get_repository()

    assert resolved is repository
    assert isinstance(resolved, ExperimentalRecordRepository)


def test_provider_can_replace_backend_explicitly() -> None:
    first = InMemoryExperimentalRecordRepository()
    second = InMemoryExperimentalRecordRepository()
    provider = ExperimentalRepositoryProvider(first)

    provider.replace_repository(second)

    assert provider.get_repository() is second


def test_provider_has_no_runtime_or_canonical_selection_methods() -> None:
    provider = ExperimentalRepositoryProvider(InMemoryExperimentalRecordRepository())

    assert not hasattr(provider, "get_runtime_store")
    assert not hasattr(provider, "select_current")
    assert not hasattr(provider, "select_canonical")
