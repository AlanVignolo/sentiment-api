"""Schemas (Pydantic models) para la API."""
from app.schemas.health import (
    HealthResponse,
    ComponentHealth,
    DetailedHealthResponse,
)

from app.schemas.sentiment import (
    SentimentLabel,
    SentimentRequest,
    SentimentResponse,
    SentimentScore,
    BatchSentimentRequest,
    BatchSentimentResponse,
    ErrorResponse,
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