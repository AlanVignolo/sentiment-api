"""
Router principal de la API v1.
Su trabajo es juntar todos los routers de los endpoints y asignarles prefijos/tags.
Es como una "tabla de contenidos" de todas las URLs disponibles en v1.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import health, sentiment

# Router contenedor que agrupa todos los endpoints de la version 1
api_router = APIRouter()

# Conecta el router de health (sin prefijo extra, sus URLs son /health y /ready)
api_router.include_router(
    health.router,  # typo
    tags=["Health"],  # tags = categoria para agrupar en la documentacion automatica
)

# Conecta el router de sentiment con el prefijo /sentiment
# Sus URLs quedan como /sentiment/analyze, /sentiment/batch, etc.
api_router.include_router(
    sentiment.router,
    prefix="/sentiment",  # todas las URLs de sentiment empiezan con /sentiment
    tags=["Sentiment Analysis"],
)
