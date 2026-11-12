"""Encodage de texte en vecteurs, via fastembed (ONNX, CPU, sans torch)."""

from __future__ import annotations

from fastembed import TextEmbedding

from app import config


class Embedder:
    def __init__(self, model_name: str = config.EMBED_MODEL) -> None:
        # Declenche le telechargement du modele s'il n'est pas deja en cache.
        self._model = TextEmbedding(
            model_name=model_name, cache_dir=str(config.MODEL_CACHE_DIR)
        )

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [vector.tolist() for vector in self._model.embed(texts)]
