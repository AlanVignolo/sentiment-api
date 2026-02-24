"""
Schemas para analisis de sentimientos.
Definen el CONTRATO de la API: que datos acepta y que devuelve.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

# field_validator = decorador para crear validaciones personalizadas sobre un campo
from pydantic import BaseModel, Field, field_validator


# Enum = lista cerrada de opciones validas. El sentimiento SOLO puede ser uno de estos 3
class SentimentLabel(str, Enum):
    """Etiquetas posibles."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# -------- REQUEST: lo que el cliente ENVIA a la API --------


class SentimentRequest(BaseModel):
    """Request para analizar sentimiento. El cliente envia esto a POST /api/v1/analyze."""

    text: str = Field(
        ...,
        min_length=1,  # minimo 1 caracter
        max_length=5000,  # maximo 5000 caracteres (pydantic valida esto automaticamente)
        description="Texto a analizar",
        examples=["I love this product! It's amazing."],
    )

    language: str = Field(
        default="en",  # si no mandan idioma, asume ingles
        description="Codigo de idioma (ISO 639-1)",
        examples=["en", "es"],
    )

    # Validador personalizado: se ejecuta ANTES de aceptar el valor de "text"
    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validar que el texto no sea solo espacios."""
        if not v.strip():  # strip() quita espacios de los extremos
            raise ValueError("El texto no puede estar vacio o contener solo espacios")
        return v.strip()  # devuelve el texto limpio (sin espacios extra)

    # Ejemplo completo que aparece en la documentacion automatica de FastAPI
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This movie was absolutely fantastic! I loved every minute of it.",
                "language": "en",
            }
        }


# -------- SCORES: puntuacion detallada de cada sentimiento --------


class SentimentScore(BaseModel):
    """Puntuacion detallada por cada sentimiento."""

    label: SentimentLabel = Field(..., description="Etiqueta del sentimiento")
    score: float = Field(
        ...,
        ge=0.0,  # ge = greater or equal (mayor o igual a 0)
        le=1.0,  # le = less or equal (menor o igual a 1)
        description="Puntuacion de confianza (0-1)",
    )


# -------- RESPONSE: lo que la API DEVUELVE al cliente --------


class SentimentResponse(BaseModel):
    """Response del analisis de sentimiento.
    Esto es lo que el cliente recibe despues del analisis."""

    text: str = Field(..., description="Texto analizado")
    sentiment: SentimentLabel = Field(..., description="Sentimiento predominante")

    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza en la prediccion (0-1)")

    scores: List[SentimentScore] = Field(  # lista con la puntuacion de cada sentimiento
        ..., description="Puntuaciones para cada sentimiento"
    )

    processing_time_ms: float = Field(..., description="Tiempo de procesamiento en milisegundos")

    model_version: str = Field(..., description="Version del modelo usado")

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ),  # lambda = funcion anonima que se ejecuta cada vez
        description="Timestamp del analisis",
    )

    class Config:
        protected_namespaces = ()  # permite usar campos que empiezan con "model_" sin warning
        json_schema_extra = {
            "example": {
                "text": "This movie was absolutely fantastic!",
                "sentiment": "positive",
                "confidence": 0.95,
                "scores": [
                    {"label": "positive", "score": 0.95},
                    {"label": "negative", "score": 0.03},
                    {"label": "neutral", "score": 0.02},
                ],
                "processing_time_ms": 45.2,
                "model_version": "distilbert-base-uncased-finetuned-sst-2-english",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        }


# -------- BATCH: para analizar VARIOS textos de una sola vez --------


class BatchSentimentRequest(BaseModel):
    """Request para analisis de multiples textos."""

    texts: List[str] = Field(
        ...,
        min_length=1,  # al menos 1 texto en la lista
        max_length=100,  # maximo 100 textos por request
        description="Lista de textos a analizar (maximo 100)",
    )

    language: str = Field(default="en")

    # Validador que recorre CADA texto de la lista y lo valida individualmente
    @field_validator("texts")
    @classmethod
    def validate_texts(cls, v: List[str]) -> List[str]:
        """Validar cada texto en la lista."""
        validated = []
        for i, text in enumerate(v):  # enumerate da el indice (i) y el valor (text)
            if not text.strip():
                raise ValueError(f"El texto en posicion {i} esta vacio")
            if len(text) > 5000:
                raise ValueError(f"El texto en posicion {i} excede 5000 caracteres")
            validated.append(text.strip())
        return validated


class BatchSentimentResponse(BaseModel):
    """Response del analisis batch."""

    results: List[SentimentResponse] = Field(  # una lista de SentimentResponse, uno por cada texto
        ..., description="Resultados para cada texto"
    )

    total_processing_time_ms: float = Field(..., description="Tiempo total de procesamiento")

    texts_analyzed: int = Field(..., description="Cantidad de textos analizados")


# -------- ERROR: formato estandar para cuando algo falla --------


class ErrorResponse(BaseModel):
    """Respuesta de error estandar."""

    error: str = Field(..., description="Codigo de error")
    message: str = Field(..., description="Mensaje descriptivo")
    details: Optional[dict] = Field(None, description="Detalles adicionales del error")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
