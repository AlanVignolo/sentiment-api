"""
Endpoints de analisis de sentimientos.
Define las URLs POST /analyze y /analyze/batch para analizar texto.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_sentiment_pipeline
from app.core import SentimentAPIException, get_logger
from app.ml import SentimentPipeline
from app.schemas import (
    BatchSentimentRequest,
    BatchSentimentResponse,
    ErrorResponse,
    SentimentRequest,
    SentimentResponse,
)

logger = get_logger(__name__)
router = APIRouter()


# -------- POST /analyze - Analiza UN texto --------
@router.post(
    "/analyze",
    response_model=SentimentResponse,
    status_code=status.HTTP_200_OK,  # FIX: era HHTP_200_OK (typo)
    summary="Analizar sentimiento de un texto",
    description="Analiza el sentimiento de un texto y devuelve la clasificacion con confianza",
    responses={
        200: {"description": "Analisis exitoso", "model": SentimentResponse},
        400: {"description": "Request invalido", "model": ErrorResponse},
        503: {"description": "Servicio no disponible (modelo no cargado)", "model": ErrorResponse},
    },
)
async def analyze_sentiment(
    request: SentimentRequest,
    pipeline: SentimentPipeline = Depends(get_sentiment_pipeline),  # FastAPI inyecta el pipeline
) -> SentimentResponse:
    """Analiza el sentimiento de un texto unico."""
    logger.info(f"Recibido request de analisis: {len(request.text)} caracteres")

    try:
        response = pipeline.analyze(request)  # delega todo al pipeline de ML
        return response

    except SentimentAPIException as e:
        # Errores conocidos: modelo no cargado, texto muy largo, etc.
        logger.error(f"Error de aplicacion: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": e.error_code, "message": e.message, "details": e.details},
        )

    except Exception as e:
        # Errores inesperados: cualquier otra cosa que falle
        logger.exception(f"Error inesperado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Error interno del servidor"},
        )


# -------- POST /analyze/batch - Analiza VARIOS textos de una vez --------
@router.post(
    "/analyze/batch",
    response_model=BatchSentimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Analizar multiples textos",
    description="Analiza el sentimiento de multiples textos en una sola llamada",
)
async def analyze_sentiment_batch(
    request: BatchSentimentRequest, pipeline: SentimentPipeline = Depends(get_sentiment_pipeline)
) -> BatchSentimentResponse:
    """Analiza multiples textos en batch."""
    logger.info(f"Recibido request batch: {len(request.texts)} textos")

    try:
        response = pipeline.analyze_batch(request)
        return response

    except SentimentAPIException as e:
        logger.error(f"Error de aplicacion: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": e.error_code, "message": e.message},
        )

    except Exception as e:
        logger.exception(f"Error inesperado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "INTERNAL_ERROR", "message": "Error interno del servidor"},
        )
