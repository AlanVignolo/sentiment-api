"""
Configuracion de logging estructurado
Critico para debugging en produccion
"""

import logging  # modulo de Python para registrar mensajes/eventos de la app
import sys

from app.config import settings  # importa la config, ahi esta LOG_LEVEL


def setup_logging() -> None:
    """
    Configura el logging de la aplicacion.
    En desarrollo: logs legibles para humanos
    En produccion: cambiar a JSON para mejor parsing
    """

    # Plantilla que define como se ve cada linea de log
    # asctime=fecha, levelname=tipo (INFO/ERROR), name=modulo, lineno=linea
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"

    # Convierte el string "INFO" a la constante logging.INFO (un numero que Python entiende)
    # Si el valor es invalido, usa INFO como fallback
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Handler = a donde van los logs. StreamHandler(sys.stdout) = imprimirlos en la consola
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(log_format))  # le aplica el formato de arriba

    # Root logger = el logger "padre" del que heredan todos los demas
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)  # solo muestra mensajes de este nivel o mas graves
    root_logger.addHandler(handler)

    # Silencia logs de librerias externas para que no llenen la consola
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado
    Uso:
        -  logger = get_logger(__name__)
        -  logger.info("Mensaje")
    """
    return logging.getLogger(name)
