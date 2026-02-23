"""
Punto de entrada principal de la aplicacion FastAPI.

Este archivo:
- Crea la instancia de FastAPI
- Configura middleware
- Registra routers
- Define eventos de startup/shutdown
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status      
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core import setup_logging, get_logger, SentimentAPIException
from app.api.v1.router import api_router
from app.ml import sentiment_model

# Configura el logging antes que todo lo demas
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la app. El codigo ANTES del yield corre al arrancar,
    el codigo DESPUES del yield corre al apagar.
    """
    # ---- STARTUP ----
    logger.info(f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENV}")

    # Carga el modelo de ML al arrancar (una sola vez)
    logger.info("Cargando modelo de ML...")
    try:
        sentiment_model.load()
        logger.info("Modelo de ML cargado exitosamente")
    except Exception as e:
        logger.error(f"Error al cargar el modelo de ML: {e}")
        if settings.ENV == "production":
            raise   # en produccion, si falla el modelo no arranca la app

    logger.info("Aplicacion lista para recibir requests")

    yield  # la app esta corriendo, esperando requests

    # ---- SHUTDOWN ----
    logger.info("Apagando aplicacion...")
    # Aqui va cualquier limpieza: cerrar conexiones a BD, liberar memoria, etc.
    logger.info("Aplicacion apagada")


# Crea la instancia principal de FastAPI con su configuracion
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,    
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",   # URL del esquema OpenAPI
    docs_url=f"{settings.API_V1_PREFIX}/docs",              # URL de la documentacion Swagger
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",            # URL de la documentacion Redoc
    lifespan=lifespan
)

# ---- MIDDLEWARE ----

# CORS: permite que navegadores de otros dominios puedan llamar a la API
# (sin esto, una pagina web en otro dominio no puede hacer requests a la API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # en produccion, poner dominios especificos
    allow_credentials=True,
    allow_methods=["*"],        
    allow_headers=["*"],
)

# ---- EXCEPTION HANDLERS ----
# Interceptan errores especificos y los convierten en respuestas JSON limpias

@app.exception_handler(SentimentAPIException)
async def sentiment_api_exception_handler(       
    request: Request,
    exc: SentimentAPIException
):
    """Captura errores propios de la app (modelo no cargado, texto muy largo, etc.)"""
    logger.error(f"SentimentAPIException: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    """Captura errores de validacion de Pydantic (campos faltantes, tipos incorrectos, etc.)"""
    logger.warning(f"Validation error: {exc.errors()}")

    # FIX: Pydantic V2 incluye el objeto ValueError original dentro de 'ctx'.
    # JSONResponse no puede serializar excepciones a JSON, hay que convertirlas a string.
    errors = []
    for e in exc.errors():
        error = dict(e)
        if "ctx" in error:
            error["ctx"] = {k: str(v) for k, v in error["ctx"].items()}
        errors.append(error)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,   # 422 = datos invalidos
        content={
            "error": "VALIDATION_ERROR",
            "message": "Error de validacion de los datos enviados",
            "details": errors
        }
    )


# ---- ROUTERS ----
# Conecta todos los endpoints de v1 bajo el prefijo /api/v1
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX    # /api/v1
)


# ---- ROOT ----
@app.get("/", tags=["Root"])
async def root():
    """Endpoint raiz. Confirma que la API esta viva y dice donde esta la documentacion."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }
    
