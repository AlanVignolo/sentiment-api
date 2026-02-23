"""
Configuracion de pytest.
Los fixtures definidos aqui estan disponibles para TODOS los tests automaticamente,
sin necesidad de importarlos en cada archivo de test.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml import sentiment_model
from app.core import setup_logging


# scope="session" = corre UNA SOLA VEZ para toda la sesion de tests (no una vez por test)
# autouse=True = corre automaticamente sin que ningun test lo pida explicitamente
@pytest.fixture(scope="session", autouse=True)
def setup():
    """Setup que corre una vez antes de todos los tests."""
    setup_logging()     # configura logging para que los tests muestren logs ordenados


@pytest.fixture(scope="session")
def load_model():
    """Carga el modelo ML una vez para toda la sesion. Evita recargar en cada test."""
    sentiment_model.load()
    return sentiment_model


@pytest.fixture
def client(load_model) -> TestClient:
    """
    Cliente HTTP de test para hacer requests a la API sin levantar un servidor real.
    Depende de load_model: garantiza que el modelo este cargado antes de crear el cliente.
    """
    # TestClient simula un cliente HTTP que habla directamente con la app FastAPI
    return TestClient(app)


@pytest.fixture
def sample_texts():
    """
    Textos de ejemplo clasificados por sentimiento esperado.
    Reutilizables en cualquier test que necesite textos de prueba.
    """
    return {
        "positive": [
            "I love this product! It's amazing!",
            "This is the best movie I've ever seen.",
            "Excellent service, highly recommended!",
        ],
        "negative": [
            "This is terrible. I hate it.",
            "Worst experience ever. Very disappointed.",
            "Complete waste of money. Awful quality.",
        ],
        "neutral": [
            "The product arrived on time.",
            "It works as described.",
            "Standard packaging, nothing special.",
        ]
    }
    
