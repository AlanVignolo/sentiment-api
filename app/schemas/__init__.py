"""Schemas (Pydantic models) para la API."""

from app.schemas.health import ComponentHealth, DetailedHealthResponse, HealthResponse
from app.schemas.sentiment import (
    BatchSentimentRequest,
    BatchSentimentResponse,
    ErrorResponse,
    SentimentLabel,
    SentimentRequest,
    SentimentResponse,
    SentimentScore,
)

__all__ = [
    # Health
    "HealthResponse",
    "ComponentHealth",
    "DetailedHealthResponse",
    # Sentiment
    "SentimentLabel",
    "SentimentRequest",
    "SentimentResponse",
    "SentimentScore",
    "BatchSentimentRequest",
    "BatchSentimentResponse",
    "ErrorResponse",
]
