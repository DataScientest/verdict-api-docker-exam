"""verdict-api : classification d'intention d'avis clients.

Points d'entree :
  GET  /health           liveness, sans authentification, sans dependance externe
  POST /classify         classe un texte : positif, negatif ou neutre
  POST /classify/batch   classe une liste de textes en une seule requete

Les endpoints de classification exigent l'en-tete X-API-Key.
"""

from __future__ import annotations

import hmac
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from app import classifier, config
from app.embeddings import Embedder
from app.store import Store

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger("verdict")


class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)


class BatchRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=32)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Chargement du modele d'embeddings '%s'...", config.EMBED_MODEL)
    app.state.embedder = Embedder()
    app.state.store = Store()
    if app.state.store.ping():
        classifier.seed_if_empty(app.state.store, app.state.embedder)
    else:
        logger.warning(
            "Qdrant n'est pas joignable au demarrage. Le service demarre quand meme ; "
            "la classification echouera tant que Qdrant est absent."
        )
    logger.info("verdict-api prete, en ecoute sur le port 8000.")
    yield


app = FastAPI(title="verdict-api", version="1.0.0", lifespan=lifespan)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if x_api_key is None or not hmac.compare_digest(x_api_key, config.API_KEY):
        raise HTTPException(401, "Cle d'API absente ou invalide (en-tete X-API-Key).")


def _classify(texts: list[str]) -> list[dict]:
    store, embedder = app.state.store, app.state.embedder
    try:
        classifier.seed_if_empty(store, embedder)
        return classifier.classify(store, embedder, texts)
    except Exception as exc:  # noqa: BLE001
        logger.error("Classification impossible : %s", exc)
        raise HTTPException(503, f"Base vectorielle indisponible : {exc}") from exc


@app.get("/health")
def health() -> dict:
    """Liveness. Ne depend d'aucun service externe, par conception."""
    return {"status": "ok"}


@app.post("/classify", dependencies=[Depends(require_api_key)])
def classify_one(req: ClassifyRequest) -> dict:
    return _classify([req.text])[0]


@app.post("/classify/batch", dependencies=[Depends(require_api_key)])
def classify_batch(req: BatchRequest) -> dict:
    for text in req.texts:
        if not text.strip() or len(text) > 1000:
            raise HTTPException(422, "Chaque texte doit faire entre 1 et 1000 caracteres.")
    return {"results": _classify(req.texts)}
