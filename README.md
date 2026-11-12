# verdict-api - Docker Module Exam / Examen du module Docker

<!-- Language selection / Onglets de langue -->
<details open>
<summary><b>🇫🇷 Français</b> (cliquer pour replier / déplier)</summary>

---

Ce dépôt est le point de départ de l'examen du module Docker. L'énoncé complet, avec les livrables attendus et la grille d'évaluation, se trouve dans le dernier chapitre du cours : lisez-le avant de commencer.

## Le service

Une équipe a développé `verdict-api`, une petite API qui attribue à un court avis client une intention parmi trois : `positif`, `negatif` ou `neutre`.

| Point d'entrée | Authentification | Rôle |
|---|---|---|
| `GET /health` | aucune | Indique si le service est opérationnel |
| `POST /classify` | `X-API-Key` | Classe un texte |
| `POST /classify/batch` | `X-API-Key` | Classe une liste de textes (32 au plus) |

Exemple de requête et de réponse :

```shell
curl -s -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <votre-cle>" \
  -d '{"text": "Livraison rapide et produit conforme, parfait."}'
```

```json
{"text": "Livraison rapide et produit conforme, parfait.", "label": "positif", "confidence": 0.86}
```

Le classement fonctionne par plus proches voisins : le texte est encodé en vecteur par un petit modèle d'embeddings multilingue, exécuté sur CPU et téléchargé au premier démarrage, puis comparé à 180 avis de référence annotés, stockés dans une base vectorielle Qdrant. Au premier démarrage, l'API indexe ces exemples si la collection est vide.

> Le métier n'est pas le sujet de l'examen. Vous n'avez pas à modifier le code de l'application : toute la difficulté porte sur Docker et l'architecture.

## Ce que le service attend de son environnement

Lisez attentivement cette section : elle décrit le contrat entre l'application et l'infrastructure que vous allez construire.

| Élément | Obligatoire | Description |
|---|---|---|
| `QDRANT_URL` | oui | Adresse de Qdrant, par exemple `http://qdrant:6333` |
| Clé d'API | oui | Lue dans le fichier `/run/secrets/verdict_api_key` ; à défaut, dans la variable `VERDICT_API_KEY` |
| `HF_HOME` | non | Dossier du cache du modèle d'embeddings |
| `VERDICT_API_KEY_FILE` | non | Autre chemin pour le fichier de la clé |

Sans `QDRANT_URL` ou sans clé d'API, le service s'arrête immédiatement avec un message explicite (code de sortie 1). Si Qdrant est injoignable au démarrage, le service démarre quand même et `/health` répond, mais la classification renvoie 503 tant que la base est absente.

Le service écoute sur le port **8000**, sur toutes les interfaces. Il se lance avec :

```shell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Les tests

Les tests fournis dans `tests/` sont des tests d'intégration : ils interrogent l'API **par le réseau**, à l'adresse donnée par `API_URL` (par défaut `http://localhost:8000`), avec la même clé d'API que le service (fichier `/run/secrets/verdict_api_key`, ou variable `VERDICT_API_KEY`).

Si la variable `REPORT_FILE` est définie, chaque test y écrit son résultat et un résumé est ajouté en fin de session. C'est ce fichier que l'énoncé vous demande de récupérer hors du conteneur de tests.

Les dépendances nécessaires aux tests (`pytest`, `requests`) sont déclarées dans le groupe `dev` du `pyproject.toml`.

## Structure du dépôt

```text
.
├── app/                    code de l'API (à ne pas modifier)
│   ├── config.py           configuration par l'environnement
│   ├── embeddings.py       encodage de texte en vecteurs (fastembed, CPU)
│   ├── store.py            accès à Qdrant
│   ├── classifier.py       indexation des références et classement
│   └── main.py             application FastAPI et endpoints
├── data/
│   └── references.json     180 avis de référence annotés
├── tests/                  tests d'intégration, exécutés par le réseau
├── scripts/
│   └── gen_references.py   régénère data/references.json
├── pyproject.toml          dépendances
└── uv.lock                 versions figées, pour des builds reproductibles
```

Aucun fichier Docker n'est fourni : les produire est l'objet de l'examen.

</details>

<details open>
<summary><b>🇬🇧 English</b> (click to expand / collapse)</summary>

---

This repository is the starting point for the Docker module exam. The full assignment, expected deliverables, and grading rubric are in the last chapter of the course: make sure to read them before starting.

## The Service

A team developed `verdict-api`, a lightweight API that categorizes short customer reviews into one of three sentiments: `positif`, `negatif`, or `neutre`.

| Endpoint | Authentication | Purpose |
|---|---|---|
| `GET /health` | None | Reports service health status |
| `POST /classify` | `X-API-Key` | Classifies a single review |
| `POST /classify/batch` | `X-API-Key` | Classifies a list of reviews (up to 32) |

Example request and response:

```shell
curl -s -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-key>" \
  -d '{"text": "Livraison rapide et produit conforme, parfait."}'
```

```json
{"text": "Livraison rapide et produit conforme, parfait.", "label": "positif", "confidence": 0.86}
```

Classification relies on nearest neighbors: text is converted into vectors by a lightweight multilingual embedding model (running on CPU and downloaded on first boot), then compared against 180 annotated reference reviews stored in a Qdrant vector database. On first boot, the API indexes these reference examples if the collection is empty.

> The business logic is not the exam's focus. You do not need to modify application code: all challenges revolve around Docker and architecture.

## Environment Requirements & Expectations

Read this section carefully: it defines the contract between the application and the infrastructure you will build.

| Item | Required | Description |
|---|---|---|
| `QDRANT_URL` | Yes | Address of Qdrant instance, e.g. `http://qdrant:6333` |
| API Key | Yes | Read from file `/run/secrets/verdict_api_key`; falls back to env var `VERDICT_API_KEY` |
| `HF_HOME` | No | Cache directory for the embeddings model |
| `VERDICT_API_KEY_FILE` | No | Custom path to the API key secret file |

Without `QDRANT_URL` or an API key, the service terminates immediately with an explicit error message (exit code 1). If Qdrant is unreachable at startup, the service still boots and `/health` responds, but classification requests return 503 while the database is unavailable.

The service listens on port **8000**, across all network interfaces (`0.0.0.0`). It is started with:

```shell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Running Tests

The tests provided in `tests/` are integration tests: they query the API **over the network** at the address specified by `API_URL` (defaults to `http://localhost:8000`), using the same API key as the service (via `/run/secrets/verdict_api_key` or `VERDICT_API_KEY`).

If the `REPORT_FILE` environment variable is defined, each test writes its results to that file and appends a summary at session completion. This is the exact file the exam asks you to retrieve outside of the test container.

Dependencies required for tests (`pytest`, `requests`) are defined under the `dev` dependency group in `pyproject.toml`.

## Repository Layout

```text
.
├── app/                    API source code (do not modify)
│   ├── config.py           configuration via environment
│   ├── embeddings.py       text vector embeddings (fastembed, CPU)
│   ├── store.py            Qdrant access layer
│   ├── classifier.py       reference indexing and classification
│   └── main.py             FastAPI application and endpoints
├── data/
│   └── references.json     180 annotated reference reviews
├── tests/                  integration tests executed over the network
├── scripts/
│   └── gen_references.py   regenerates data/references.json
├── pyproject.toml          package dependencies
└── uv.lock                 pinned dependency versions for reproducible builds
```

No Docker files are provided: building them is the core objective of the exam.

</details>
