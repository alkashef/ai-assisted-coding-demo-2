"""The only module that talks to Chroma: an in-memory cosine index over our own vectors.

Stores vectors by ID and returns every stored item nearest to a query vector. It does not embed
text (`llm_client.py` does), rank missing items (`ranking.py` does) or write to disk. Implements
`VectorIndex` from `ports.py` (RNK-001, DEC-004).

Checked against chromadb 1.5.9: `create_collection` defaults `embedding_function` to a local ONNX
model, so it is set to `None`; telemetry is on unless `anonymized_telemetry` is `False`; the cosine
setting is `configuration={"hnsw": {"space": "cosine"}}`, and a query returns cosine distance,
which is `1 - similarity`.
"""

from collections.abc import Sequence

import chromadb
from chromadb.config import Settings


class ChromaVectorStore:
    """Holds one in-memory Chroma collection and answers nearest-neighbour queries.

    State: the collection, which lives for the life of the process. The collection name must be
    unique in the process, because in-memory Chroma clients share their collections.
    """

    def __init__(self, collection_name: str) -> None:
        """Creates an empty collection that uses cosine similarity and no embedding model.

        Args:
            collection_name: The name of the new collection, such as "cvs".
        """
        client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
        self._collection = client.create_collection(
            name=collection_name,
            configuration={"hnsw": {"space": "cosine"}},
            embedding_function=None,
        )

    def add(self, item_id: str, vector: list[float]) -> None:
        """Stores one vector.

        Args:
            item_id: The ID of the item, such as a file name.
            vector: The embedding vector.
        """
        embeddings: list[Sequence[float]] = [vector]
        self._collection.add(ids=[item_id], embeddings=embeddings)

    def nearest(self, vector: list[float]) -> list[tuple[str, float]]:
        """Finds every stored item, nearest first.

        Args:
            vector: The query vector.

        Returns:
            One (item ID, cosine similarity) pair per stored item, best first. Equal
            similarities are ordered by item ID.
        """
        count = self._collection.count()
        if count == 0:
            return []
        query: list[Sequence[float]] = [vector]
        result = self._collection.query(
            query_embeddings=query, n_results=count, include=["distances"]
        )
        ids = result["ids"][0]
        distances = (result["distances"] or [[]])[0]
        pairs = [
            (item_id, 1.0 - distance) for item_id, distance in zip(ids, distances, strict=True)
        ]
        return sorted(pairs, key=lambda pair: (-pair[1], pair[0]))
