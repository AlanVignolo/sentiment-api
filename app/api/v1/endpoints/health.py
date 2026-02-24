"""
Endpoints de health check.
Son las URLs que responden "estoy vivo" o "estoy listo".
Los usan herramientas de monitoreo, Kubernetes, balanceadores de carga, etc.
"""

import time

from fastapi import APIRouter, status

from app.config import settings
from app.core import get_logger
from app.ml import sentiment_model
from app.schemas import ComponentHealth, DetailedHealthResponse, HealthResponse

logger = get_logger(__name__)

# APIRouter agrupa endpoints relacionados. Despues se conecta a la app principal con app.include_router()
router = APIRouter()


# -------- /health - "Estas vivo?" --------
@router.get(
    "/health",
    response_model=HealthResponse,  # le dice a FastAPI que la respuesta tiene esta forma
    status_code=status.HTTP_200_OK,  # 200 = todo bien
    summary="Health check basico",
    description="Verifica que el servicio esta corriendo",
)
async def health_check() -> HealthResponse:
    """Health check simple: si responde, esta vivo."""
    return HealthResponse(
        status="healthy", version=settings.VERSION  # la version que definimos en config.py
    )


# -------- /health/detailed - "Estas vivo Y como estan tus componentes?" --------
@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check detallado",
    description="Verifica el estado de cada componente",
)
async def detailed_health_check() -> DetailedHealthResponse:
    """Health check que verifica cada componente (modelo, DB, etc)."""
    components = []
    overall_status = "healthy"  # arranca asumiendo que todo esta bien

    # Verificar modelo de ML
    model_start = time.time()
    if sentiment_model.is_loaded:
        model_status = "healthy"
        model_message = f"Model loaded: {sentiment_model.model_name}"
    else:
        model_status = "unhealthy"
        model_message = "Model not loaded"
        overall_status = "unhealthy"  # si el modelo falla, el servicio no esta sano

    model_latency = (time.time() - model_start) * 1000  # cuanto tardo la verificacion en ms

    # Agrega el resultado del modelo a la lista de componentes
    components.append(
        ComponentHealth(
            name="ml_model", status=model_status, latency_ms=model_latency, message=model_message
        )
    )

    # Aca van otros componentes: base de datos, cache, servicios externos

    return DetailedHealthResponse(
        status=overall_status, version=settings.VERSION, components=components
    )


# -------- /ready - "Estas listo para recibir requests?" --------
@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Verifica que el servicio esta listo para recibir trafico",
)
async def readiness_check():
    """
    Readiness probe para Kubernetes.
    Si el modelo no esta cargado, devuelve 503 (no disponible).
    Kubernetes no le manda trafico hasta que responda 200.
    """
    if not sentiment_model.is_loaded:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,  # 503 = servicio no disponible
            detail="Model not loaded yet",
        )

    return {"status": "ready"}
