"""Classification d'intention par plus proches voisins.

Le principe est volontairement simple : on encode le texte, on cherche dans
Qdrant les exemples de reference les plus proches par le sens, et l'intention
qui pese le plus parmi ces voisins (somme des similarites) l'emporte. La
confiance est la part de cette intention dans le poids total.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict

from qdrant_client import models

from app import config
from app.embeddings import Embedder
from app.store import Store

logger = logging.getLogger("verdict.classifier")


def seed_if_empty(store: Store, embedder: Embedder) -> int:
    """Indexe les exemples de reference si la collection est vide.

    Renvoie le nombre d'exemples presents apres l'operation. Si un volume
    conserve l'etat de Qdrant, la collection est deja peuplee au redemarrage
    et rien n'est recalcule.
    """
    store.ensure_collection()
    existing = store.count()
    if existing > 0:
        logger.info(
            "Collection deja peuplee (%d exemples) : pas de reindexation.", existing
        )
        return existing

    references = json.loads(config.DATA_PATH.read_text(encoding="utf-8"))
    vectors = embedder.encode([r["text"] for r in references])
    store.upsert(
        [
            models.PointStruct(id=r["id"], vector=v, payload=r)
            for r, v in zip(references, vectors)
        ]
    )
    logger.info("%d exemples de reference indexes.", len(references))
    return len(references)


def classify(store: Store, embedder: Embedder, texts: list[str]) -> list[dict]:
    vectors = embedder.encode(texts)
    results = []
    for text, vector in zip(texts, vectors):
        hits = store.neighbors(vector, config.NEIGHBORS)
        weights: dict[str, float] = defaultdict(float)
        for hit in hits:
            weights[hit.payload["label"]] += max(hit.score, 0.0)
        total = sum(weights.values())
        if total == 0:
            raise RuntimeError("aucun exemple de reference disponible")
        label = max(weights, key=weights.get)
        results.append(
            {"text": text, "label": label, "confidence": round(weights[label] / total, 3)}
        )
    return results
