"""Configuration de verdict-api.

Toute la configuration vient de l'environnement : l'image est un artefact
fige, c'est son environnement d'execution qui l'adapte. Deux elements sont
obligatoires, et leur absence arrete le service immediatement avec un message
clair, plutot que de le laisser demarrer dans un etat inutilisable :

  - QDRANT_URL : l'adresse de la base vectorielle ;
  - la cle d'API qui protege les endpoints de classification.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


# --------------------------------------------------------------------------
# Base vectorielle
# --------------------------------------------------------------------------
QDRANT_URL = os.environ.get("QDRANT_URL")
if not QDRANT_URL:
    _fail(
        "la variable d'environnement QDRANT_URL est obligatoire. "
        "Exemple : QDRANT_URL=http://qdrant:6333"
    )

COLLECTION = os.environ.get("VERDICT_COLLECTION", "references")

# --------------------------------------------------------------------------
# Cle d'API
#
# Elle est lue en priorite dans un fichier, celui qu'un secret Docker monte
# dans le conteneur (chemin par defaut : /run/secrets/verdict_api_key). A
# defaut, la variable d'environnement VERDICT_API_KEY est acceptee, mais une
# cle passee en variable d'environnement est visible dans `docker inspect` :
# c'est a eviter hors developpement.
# --------------------------------------------------------------------------
API_KEY_FILE = Path(
    os.environ.get("VERDICT_API_KEY_FILE", "/run/secrets/verdict_api_key")
)


def _read_api_key() -> str:
    if API_KEY_FILE.is_file():
        key = API_KEY_FILE.read_text(encoding="utf-8").strip()
        if key:
            return key
    key = os.environ.get("VERDICT_API_KEY", "").strip()
    if key:
        return key
    _fail(
        "aucune cle d'API configuree. Fournissez-la via un secret monte en "
        f"{API_KEY_FILE} (recommande) ou, a defaut, via la variable "
        "VERDICT_API_KEY."
    )
    return ""  # jamais atteint


API_KEY = _read_api_key()

# --------------------------------------------------------------------------
# Modele d'embeddings
#
# Modele multilingue (les avis sont en francais), dimension 384, environ
# 220 Mo, execute sur CPU au format ONNX. Il est telecharge au premier
# demarrage dans le cache Hugging Face (HF_HOME) : sans volume, ce
# telechargement est rejoue a chaque nouveau conteneur.
# --------------------------------------------------------------------------
EMBED_MODEL = os.environ.get(
    "VERDICT_EMBED_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
EMBED_DIM = 384

# Dossier du cache du modele. fastembed range par defaut ses modeles dans un
# dossier temporaire (/tmp/fastembed_cache), ce qui rendrait inutile tout
# volume monte sur le cache Hugging Face. On le place donc explicitement sous
# HF_HOME (par defaut ~/.cache/huggingface) : c'est ce dossier qu'il faut
# monter en volume pour ne telecharger le modele qu'une seule fois.
HF_HOME = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
MODEL_CACHE_DIR = HF_HOME / "fastembed"

# Exemples de reference annotes, indexes dans Qdrant au premier demarrage.
DATA_PATH = Path(os.environ.get("VERDICT_DATA", "data/references.json"))

# Nombre de voisins consultes pour decider d'une intention.
NEIGHBORS = int(os.environ.get("VERDICT_NEIGHBORS", "7"))

LABELS = ("positif", "negatif", "neutre")
