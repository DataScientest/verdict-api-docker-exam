"""Tests d'intégration de verdict-api, exécutés à travers le réseau.

Ils supposent que l'API et sa base vectorielle tournent et que l'API est
joignable à l'adresse API_URL. On teste l'artefact réel, tel qu'il tournera
en production, et non le code sur la machine qui lance les tests.
"""

from __future__ import annotations

import requests

LABELS = {"positif", "negatif", "neutre"}
TIMEOUT = 60


def test_health(api_url: str) -> None:
    """Le service répond, sans authentification."""
    resp = requests.get(f"{api_url}/health", timeout=TIMEOUT)
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_classify_requires_api_key(api_url: str) -> None:
    """Sans clé, ou avec une mauvaise clé, la classification est refusée."""
    body = {"text": "Très bon séjour."}
    assert requests.post(f"{api_url}/classify", json=body, timeout=TIMEOUT).status_code == 401
    wrong = {"X-API-Key": "ceci-n-est-pas-la-bonne-cle"}
    assert (
        requests.post(f"{api_url}/classify", json=body, headers=wrong, timeout=TIMEOUT).status_code
        == 401
    )


def test_classify_positive(api_url: str, headers: dict) -> None:
    resp = requests.post(
        f"{api_url}/classify",
        json={"text": "Séjour fantastique, personnel aux petits soins, je recommande vivement !"},
        headers=headers,
        timeout=TIMEOUT,
    )
    assert resp.status_code == 200
    assert resp.json()["label"] == "positif"


def test_classify_negative(api_url: str, headers: dict) -> None:
    resp = requests.post(
        f"{api_url}/classify",
        json={"text": "Commande arrivée cassée et service client injoignable, je suis furieux."},
        headers=headers,
        timeout=TIMEOUT,
    )
    assert resp.status_code == 200
    assert resp.json()["label"] == "negatif"


def test_classify_response_shape(api_url: str, headers: dict) -> None:
    """La réponse contient le texte, une intention valide et une confiance entre 0 et 1."""
    text = "Le magasin ouvre à 9 heures du lundi au samedi."
    resp = requests.post(
        f"{api_url}/classify", json={"text": text}, headers=headers, timeout=TIMEOUT
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["text"] == text
    assert data["label"] in LABELS
    assert 0.0 <= data["confidence"] <= 1.0


def test_batch_preserves_order(api_url: str, headers: dict) -> None:
    texts = [
        "Un dîner exceptionnel, tout était parfait du début à la fin.",
        "Chambre bruyante et sale, le pire hôtel que j'ai connu.",
    ]
    resp = requests.post(
        f"{api_url}/classify/batch", json={"texts": texts}, headers=headers, timeout=TIMEOUT
    )
    assert resp.status_code == 200
    results = resp.json()["results"]
    assert [r["text"] for r in results] == texts
    assert [r["label"] for r in results] == ["positif", "negatif"]


def test_input_validation(api_url: str, headers: dict) -> None:
    """Les entrées invalides sont rejetées proprement, en 422."""
    empty = requests.post(
        f"{api_url}/classify", json={"text": ""}, headers=headers, timeout=TIMEOUT
    )
    assert empty.status_code == 422
    too_many = requests.post(
        f"{api_url}/classify/batch",
        json={"texts": ["ok"] * 33},
        headers=headers,
        timeout=TIMEOUT,
    )
    assert too_many.status_code == 422
