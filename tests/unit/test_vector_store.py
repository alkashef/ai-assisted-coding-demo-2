"""Tests for `src/vector_store.py`. Chroma runs in memory; no model is downloaded."""

from uuid import uuid4

import chromadb
import pytest
from chromadb.api.collection_configuration import CreateCollectionConfiguration
from chromadb.api.models.Collection import Collection
from chromadb.config import Settings

from src.vector_store import ChromaVectorStore

_REAL_EPHEMERAL_CLIENT = chromadb.EphemeralClient


def _store() -> ChromaVectorStore:
    return ChromaVectorStore(f"test-{uuid4().hex}")


class _SpyClient:
    """Wraps the real in-memory client and records how the store uses it."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.embedding_function: object = "not called"
        self.configuration: object = None
        self._real = _REAL_EPHEMERAL_CLIENT(settings=settings)

    def create_collection(
        self,
        name: str,
        configuration: CreateCollectionConfiguration,
        embedding_function: None,
    ) -> Collection:
        self.embedding_function = embedding_function
        self.configuration = configuration
        return self._real.create_collection(
            name=name, configuration=configuration, embedding_function=embedding_function
        )


def _spy(monkeypatch: pytest.MonkeyPatch) -> list[_SpyClient]:
    clients: list[_SpyClient] = []

    def make(settings: Settings) -> _SpyClient:
        clients.append(_SpyClient(settings))
        return clients[-1]

    monkeypatch.setattr("src.vector_store.chromadb.EphemeralClient", make)
    return clients


def test_rnk_001_nearest_orders_items_by_cosine_similarity() -> None:
    store = _store()
    store.add("far.txt", [0.0, 1.0])
    store.add("near.txt", [1.0, 0.0])
    store.add("middle.txt", [1.0, 1.0])

    result = store.nearest([2.0, 0.0])

    assert [item_id for item_id, _ in result] == ["near.txt", "middle.txt", "far.txt"]
    assert [round(similarity, 4) for _, similarity in result] == [1.0, 0.7071, 0.0]


def test_rnk_001_nearest_returns_every_stored_item() -> None:
    store = _store()
    for number in range(25):
        store.add(f"item-{number:02}.txt", [1.0, float(number)])

    assert len(store.nearest([1.0, 0.0])) == 25


def test_rnk_001_nearest_of_an_empty_store_is_empty() -> None:
    assert _store().nearest([1.0, 0.0]) == []


def test_rnk_001_ties_are_ordered_by_item_id() -> None:
    store = _store()
    store.add("c.txt", [1.0, 0.0])
    store.add("a.txt", [1.0, 0.0])
    store.add("b.txt", [1.0, 0.0])

    result = store.nearest([1.0, 0.0])

    assert [item_id for item_id, _ in result] == ["a.txt", "b.txt", "c.txt"]


def test_dec_004_chroma_telemetry_is_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    clients = _spy(monkeypatch)

    ChromaVectorStore(f"test-{uuid4().hex}")

    assert clients[0].settings.anonymized_telemetry is False


def test_dec_004_vectors_are_supplied_so_no_embedding_model_is_used(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients = _spy(monkeypatch)

    ChromaVectorStore(f"test-{uuid4().hex}")

    assert clients[0].embedding_function is None
    assert clients[0].configuration == {"hnsw": {"space": "cosine"}}
