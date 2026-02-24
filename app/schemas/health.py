"""
Schemas para endpoints de health check.
Definen la FORMA que tienen las respuestas JSON del endpoint /health.
"""

from datetime import datetime
from typing import List, Optional

# BaseModel = clase base de pydantic para definir "la forma" de un dato
# Field = permite agregar validaciones y descripciones a cada campo
from pydantic import BaseModel, Field


# Schema para la respuesta SIMPLE de "esta vivo el servidor?"
class HealthResponse(BaseModel):
    """Respuesta del health check basico."""

    status: str = Field(
        ...,  # ... = obligatorio, no puede faltar
        description="Estado del servicio",
        examples=["healthy", "unhealthy"],
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,  # se genera solo con la fecha/hora actual
        description="Timestamp del check",
    )
    version: str = Field(..., description="Version de la API")


# Schema para el estado de UN componente (ej: el modelo de ML, la base de datos, etc)
class ComponentHealth(BaseModel):
    """Estado de un componente individual."""

    name: str = Field(..., description="Nombre del componente")
    status: str = Field(..., description="Estado: healthy/unhealthy/degraded")
    latency_ms: Optional[float] = Field(  # Optional = puede venir o no (puede ser None)
        None, description="Latencia en milisegundos"
    )
    message: Optional[str] = Field(
        None, description="Mensaje adicional"  # None = si no se pasa, queda vacio
    )


# Schema para la respuesta DETALLADA que incluye el estado de cada componente
class DetailedHealthResponse(BaseModel):
    """Respuesta detallada del health check."""

    status: str = Field(..., description="Estado general del servicio")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(..., description="Version de la API")
    components: List[ComponentHealth] = Field(  # lista de ComponentHealth (uno por cada componente)
        default_factory=list,  # si no se pasa, arranca como lista vacia []
        description="Estado de cada componente",
    )
