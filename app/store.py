"""Acces a la base vectorielle Qdrant.

La connexion n'est jamais bloquante au demarrage : si Qdrant est injoignable,
le service demarre quand meme et /health reste vert ; les endpoints qui ont
besoin de la base echouent proprement, en 503, tant qu'elle est absente.
"""

from __future__ import annotations

import logging

from qdrant_client import QdrantClient, models

from app import config

logger = logging.getLogger("verdict.store")


class Store:
    def __init__(self, url: str = config.QDRANT_URL) -> None:
        self._client = QdrantClient(url=url, timeout=5.0)

    def ping(self) -> bool:
        try:
            self._client.get_collections()
            return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Qdrant injoignable : %s", exc)
            return False

    def ensure_collection(self) -> None:
        if not self._client.collection_exists(config.COLLECTION):
            self._client.create_collection(
                collection_name=config.COLLECTION,
                vectors_config=models.VectorParams(
                    size=config.EMBED_DIM, distance=models.Distance.COSINE
                ),
            )
            logger.info("Collection '%s' creee.", config.COLLECTION)

    def count(self) -> int:
        return self._client.count(collection_name=config.COLLECTION).count

    def upsert(self, points: list[models.PointStruct]) -> None:
        self._client.upsert(collection_name=config.COLLECTION, points=points)

    def neighbors(self, vector: list[float], limit: int):
        return self._client.query_points(
            collection_name=config.COLLECTION,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points
