"""
Pipeline completo de ML. Orquesta preprocesamiento + modelo + postprocesamiento.
Es el "director de orquesta" que coordina los pasos: limpiar texto → predecir → armar respuesta.
"""

import time
from typing import Optional

from app.core import get_logger
from app.ml.model import SentimentModel, sentiment_model
from app.ml.preprocessor import TextPreprocessor
from app.schemas import (
    BatchSentimentRequest,
    BatchSentimentResponse,
    SentimentRequest,
    SentimentResponse,
    SentimentScore,
)

logger = get_logger(__name__)


class SentimentPipeline:
    """
    Pipeline completo de analisis de sentimientos.
    Junta el preprocessor (limpieza) y el model (prediccion) en un solo flujo.
    """

    def __init__(
        self,
        model: Optional[SentimentModel] = None,
        preprocessor: Optional[TextPreprocessor] = None,
    ):
        """Inicializa el pipeline con modelo y preprocesador."""
        # "or" funciona asi: si model es None, usa sentiment_model (el global)
        # Esto permite inyectar un modelo diferente para tests
        self.model = model or sentiment_model
        self.preprocessor = preprocessor or TextPreprocessor()

        logger.info("SentimentPipeline inicializado")

    def analyze(self, request: SentimentRequest) -> SentimentResponse:
        """
        Analiza el sentimiento de UN texto.
        Recibe un SentimentRequest y devuelve un SentimentResponse.
        """
        start_time = time.time()

        # Paso 1: Preprocesar (limpiar URLs, emails, espacios, etc.)
        logger.debug(f"Preprocesando texto de {len(request.text)} caracteres")
        processed_text = self.preprocessor.preprocess(request.text)

        # Paso 2: Predecir (mandar el texto limpio al modelo de ML)
        logger.debug("Ejecutando prediccion")
        prediction = self.model.predict(processed_text)

        # Paso 3: Construir la respuesta con el formato que espera la API
        total_time = (time.time() - start_time) * 1000  # convierte a milisegundos

        # Convierte los scores crudos del modelo a objetos SentimentScore (schema de pydantic)
        scores = [SentimentScore(label=s["label"], score=s["score"]) for s in prediction["scores"]]

        # Arma el SentimentResponse completo con todos los campos
        response = SentimentResponse(
            text=request.text,  # texto original (no el limpio)
            sentiment=prediction["sentiment"],  # POSITIVE/NEGATIVE/NEUTRAL
            confidence=prediction["confidence"],  # que tan seguro esta (0-1)
            scores=scores,  # puntuacion de cada sentimiento
            processing_time_ms=total_time,  # cuanto tardo en ms
            model_version=self.model.model_name,  # nombre del modelo usado
        )

        logger.info(
            f"Analisis completado: sentiment={response.sentiment}, "
            f"confidence={response.confidence:.2f}, "
            f"time={total_time:.1f}ms"
        )

        return response

    def analyze_batch(self, request: BatchSentimentRequest) -> BatchSentimentResponse:
        """
        Analiza VARIOS textos de una sola vez.
        Internamente llama a analyze() para cada texto individual.
        """
        start_time = time.time()

        results = []
        for text in request.texts:
            # Crea un SentimentRequest individual por cada texto de la lista
            single_request = SentimentRequest(text=text, language=request.language)
            result = self.analyze(single_request)  # reutiliza el metodo de arriba
            results.append(result)

        total_time = (time.time() - start_time) * 1000

        return BatchSentimentResponse(
            results=results,  # lista de SentimentResponse
            total_processing_time_ms=total_time,  # tiempo total (todos los textos)
            texts_analyzed=len(request.texts),  # cuantos textos se analizaron
        )


# Instancia global del pipeline, lista para importar desde cualquier parte
# Se usa asi: from app.ml.pipeline import sentiment_pipeline
sentiment_pipeline = SentimentPipeline()
