"""
Configuración centralizada de la aplicación.
Usa pydantic-settings para cargar configuración desde variables de entorno.
"""

from functools import lru_cache # lru_cache guarda en memoria el resultado de una funcion para no recalcularlo


from pydantic_settings import BaseSettings, SettingsConfigDict # BaseSettings lee variables de entorno automaticamente; SettingsConfigDict configura como leerlas

# Clase que centraliza TODA la configuracion de la app en un solo lugar
class Settings(BaseSettings):
    """
    Configuracion de la aplicacion.
    Los valores se cargan desde variables de entorno.
    Si no existen, usa los valores por defecto.
    """

    #Informacion del proyecto
    PROJECT_NAME : str = "Sentiment API"
    PROJECT_DESCRIPTION : str = "API para analisis de sentimientos con ML"
    VERSION : str = "1.0.0"

    #Ambiente
    ENV: str = "development"
    DEBUG : bool = True  # en produccion se pone False para no mostrar errores internos

    #API
    API_V1_PREFIX : str ="/api/v1"  # prefijo comun para todas las rutas de la API

    #ML Model
    MODEL_NAME : str = "distilbert-base-uncased-finetuned-sst-2-english"  # modelo preentrenado de HuggingFace
    MODEL_CACHE_DIR : str = "./model_cache"  # carpeta donde se guarda el modelo descargado

    #Logging
    LOG_LEVEL : str = "INFO"  # nivel de detalle de los logs (DEBUG, INFO, WARNING, ERROR)

    # Le dice a pydantic de donde leer las variables de entorno
    model_config = SettingsConfigDict(
        env_file = ".env.example",   # busca un archivo .env en la raiz del proyecto
        env_file_encoding = "utf-8",
        case_sensitive = True        # diferencia mayusculas de minusculas en los nombres
    )

# lru_cache hace que esta funcion se ejecute UNA sola vez y despues devuelva el mismo resultado
@lru_cache()
def get_settings() -> Settings:
    """
    Obtiene la configuracion (cacheada)
    Usamos lru_cache para no leer el .env en cada request
    """
    return Settings()

# Variable lista para importar desde cualquier parte: from app.config import settings
settings = get_settings()