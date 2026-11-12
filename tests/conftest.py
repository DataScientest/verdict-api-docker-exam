"""Configuration des tests de verdict-api.

Les tests interrogent l'API par le réseau, à l'adresse API_URL :
  - depuis votre machine        : http://localhost:8000 (valeur par défaut)
  - depuis un conteneur de test : http://<nom-du-service>:8000

La clé d'API est lue comme le fait l'application : d'abord dans le fichier
/run/secrets/verdict_api_key (secret monté), sinon dans la variable
VERDICT_API_KEY.

Compte rendu : si la variable REPORT_FILE est définie, chaque test y écrit
son résultat, et un résumé est ajouté en fin de session. Pointez REPORT_FILE
vers un dossier monté en volume pour récupérer le rapport hors du conteneur.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytest

LABELS = {"positif", "negatif", "neutre"}

_report_path = os.environ.get("REPORT_FILE")
_counts = {"passed": 0, "failed": 0, "skipped": 0}


@pytest.fixture(scope="session")
def api_url() -> str:
    return os.environ.get("API_URL", "http://localhost:8000").rstrip("/")


@pytest.fixture(scope="session")
def api_key() -> str:
    secret = Path(os.environ.get("VERDICT_API_KEY_FILE", "/run/secrets/verdict_api_key"))
    if secret.is_file() and secret.read_text(encoding="utf-8").strip():
        return secret.read_text(encoding="utf-8").strip()
    key = os.environ.get("VERDICT_API_KEY", "").strip()
    if not key:
        pytest.fail(
            "Clé d'API introuvable pour les tests : montez le secret "
            "verdict_api_key ou définissez VERDICT_API_KEY."
        )
    return key


@pytest.fixture(scope="session")
def headers(api_key: str) -> dict:
    return {"X-API-Key": api_key}


# --------------------------------------------------------------------------
# Compte rendu dans REPORT_FILE
# --------------------------------------------------------------------------
def _write(line: str) -> None:
    if not _report_path:
        return
    path = Path(_report_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        # Un dossier de rapport non accessible en écriture ne doit pas masquer
        # le résultat des tests : on prévient, et on continue.
        print(f"AVERTISSEMENT : impossible d'écrire le rapport {path} ({exc})")


def pytest_sessionstart(session: pytest.Session) -> None:
    api = os.environ.get("API_URL", "http://localhost:8000")
    _write("=" * 60)
    _write(f"verdict-api : rapport de tests du {datetime.now():%Y-%m-%d %H:%M:%S}")
    _write(f"API testée : {api}")
    _write("=" * 60)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when == "call" or (report.when == "setup" and report.outcome != "passed"):
        _counts[report.outcome] = _counts.get(report.outcome, 0) + 1
        status = {"passed": "SUCCESS", "failed": "FAILURE", "skipped": "SKIPPED"}[report.outcome]
        _write(f"[{status:7}] {report.nodeid}")
        if report.outcome == "failed":
            _write(f"          {report.longreprtext.strip().splitlines()[-1]}")


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    _write("-" * 60)
    _write(
        f"Résumé : {_counts['passed']} réussi(s), {_counts['failed']} échoué(s), "
        f"{_counts['skipped']} ignoré(s)"
    )
    _write("")
