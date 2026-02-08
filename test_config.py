from app.config import settings
from app.core import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

print(f"Project: {settings.PROJECT_NAME}")
print(f"Environment: {settings.ENV}")
print(f"Model: {settings.MODEL_NAME}")
# Verificar logging
logger.debug("Este es un mensaje DEBUG")
logger.info("Este es un mensaje INFO")
logger.warning("Este es un mensaje WARNING")
logger.error("Este es un mensaje ERROR")
print("\n✅ Configuración funcionando correctamente!")