"""
Dependencias compartidas para los endpoints.
En FastAPI, una "dependencia" es una funcion que le entrega algo a un endpoint.
En vez de que cada endpoint busque el pipeline por su cuenta, esta funcion se lo da.
"""

from typing import Generator

from app.core import get_logger
from app.ml import SentimentPipeline, sentiment_pipeline

logger = get_logger(__name__)


def get_sentiment_pipeline() -> Generator[SentimentPipeline, None, None]:
    """
    Dependency que provee el pipeline de sentimientos.
    FastAPI llama a esta funcion ANTES de ejecutar el endpoint,
    y le pasa el resultado (sentiment_pipeline) como parametro.

    Uso en endpoints:
        @app.post("/analyze")
        def analyze(
            request: SentimentRequest,
            pipeline: SentimentPipeline = Depends(get_sentiment_pipeline)
        ):
            return pipeline.analyze(request)
    """
    logger.debug("Obteniendo pipeline de sentimientos")
    # yield = "prestame esto mientras dure el request"
    # Cuando el request termina, FastAPI vuelve aca (por si hubiera que limpiar algo)
    yield sentiment_pipeline
