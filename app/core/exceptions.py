"""
Excepciones personalizadas para la aplicacion.
Cada tipo de error tiene su propia clase, asi el codigo que las atrapa
sabe exactamente que paso y puede responder de forma adecuada.
"""

from typing import Any, Dict, Optional

# Clase "madre" de la que heredan TODAS las excepciones de esta app
# Esto permite atrapar cualquier error de la app con: except SentimentAPIException
class SentimentAPIException(Exception):
    """
    Exception base de la aplicacion
    """

    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict[str,Any]] = None):
        self.message = message          # texto descriptivo del error
        self.error_code = error_code    # codigo corto para identificar el tipo de error
        self.details = details or {}    # info extra (si no viene nada, queda como dict vacio)
        super().__init__(self.message)  # llama al __init__ de Exception (la clase padre)

# Se lanza cuando el modelo de ML no se pudo cargar o no esta disponible
class ModelNotLoadedError(SentimentAPIException):
    """
    El modelo de ML no esta cargado
    """

    def __init__(self, message: str = "El modelo no esta disponible"):
        super().__init__(message=message, error_code="MODEL_NOT_LOADED")

# Se lanza cuando el usuario manda un texto demasiado largo
class TextTooLongError(SentimentAPIException):
    """
    El texto excede el limite permitido
    """

    def __init__(self, max_length: int, actual_length: int):
        super().__init__(
            message=f"El texto excede el limite de {max_length} caracteres",
            error_code="TXT_TOO_LONG",
            details={"max_length": max_length, "actual_length": actual_length}  # guarda los numeros para que el cliente sepa cuanto se paso
        )

# Se lanza cuando el usuario manda un texto vacio
class EmptyTextError(SentimentAPIException):
    """
    El texto esta vacio
    """

    def __init__(self):
        super().__init__(message="El texto no puede estar vacio", error_code="EMPTY_TEXT")

# Se lanza cuando algo falla durante el analisis de sentimiento
class PredictionError(SentimentAPIException):
    """
    Error durante la prediccion
    """

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            error_code="PREDICTION_ERROR",
            details={"original_error": str(original_error)} if original_error else {}  # guarda el error original para debugging
        )

