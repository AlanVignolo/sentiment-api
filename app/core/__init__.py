"""
Core utilities - Re-exporta las piezas principales del paquete core para que se puedan importar de forma mas corta.
"""

# Trae todas las excepciones desde exceptions.py
from app.core.exceptions import (
    SentimentAPIException,
    ModelNotLoadedError,
    TextTooLongError,
    EmptyTextError,
    PredictionError,
)
# Trae las funciones de logging desde logging.py
from app.core.logging import setup_logging, get_logger

# __all__ define que se exporta cuando alguien hace: from app.core import *
# Es como una "lista publica" de lo que ofrece este paquete
__all__ = [
    "SentimentAPIException",
    "ModelNotLoadedError",
    "TextTooLongError",
    "EmptyTextError",
    "PredictionError",
    "setup_logging",
    "get_logger",
]