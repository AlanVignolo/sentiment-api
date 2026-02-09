"""
Wrapper del modelo de ML.
Carga el modelo de HuggingFace una sola vez y lo reutiliza para todas las predicciones.
"""

import time
from typing import List, Optional

from transformers import pipeline, Pipeline  # pipeline = funcion de HuggingFace que simplifica usar modelos

from app.config import settings
from app.core import get_logger, ModelNotLoadedError, PredictionError
from app.schemas import SentimentLabel

logger = get_logger(__name__)


class SentimentModel:
    """
    Wrapper del modelo de analisis de sentimientos.
    Implementa el patron Singleton: sin importar cuantas veces hagas SentimentModel(), siempre te devuelve la MISMA instancia.
    Esto evita cargar el modelo (que pesa cientos de MB) mas de una vez.
    """

    # Variables de clase (compartidas por todas las instancias, que en este caso es una sola)
    _instance: Optional['SentimentModel'] = None   # la unica instancia
    _pipeline: Optional[Pipeline] = None           # el modelo cargado
    _is_loaded: bool = False                       # flag de "ya cargo?"

    def __new__(cls):
        """Singleton: si ya existe una instancia, devuelve esa. Si no, crea una nueva."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # @property convierte un metodo en un atributo de solo lectura
    # En vez de model.is_loaded() se usa model.is_loaded (sin parentesis)
    @property
    def is_loaded(self) -> bool:
        """Verifica si el modelo esta cargado."""
        return self._is_loaded and self._pipeline is not None

    @property
    def model_name(self) -> str:
        """Nombre del modelo."""
        return settings.MODEL_NAME

    def load(self) -> None:
        """
        Carga el modelo en memoria. Se llama una vez cuando arranca la app.
        La primera vez descarga el modelo de internet (puede tardar).
        """
        if self._is_loaded:
            logger.info("Modelo ya esta cargado")
            return

        logger.info(f"Cargando modelo: {settings.MODEL_NAME}")
        start_time = time.time()        # marca el inicio para medir cuanto tarda

        try:
            # pipeline() de HuggingFace: carga modelo + tokenizer y los deja listos para usar
            # task="sentiment-analysis" le dice que tipo de tarea va a hacer
            self._pipeline = pipeline(
                task="sentiment-analysis",
                model=settings.MODEL_NAME,
                tokenizer=settings.MODEL_NAME,
                device=-1               # -1 = usa CPU, 0 = usaria la primera GPU
            )

            self._is_loaded = True
            load_time = time.time() - start_time    # calcula cuanto tardo

            logger.info(f"Modelo cargado en {load_time:.2f} segundos")

        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            raise ModelNotLoadedError(f"No se pudo cargar el modelo: {e}")

    def predict(self, text: str) -> dict:
        """
        Analiza el sentimiento de un texto.
        Devuelve un dict con: sentiment, confidence, scores, processing_time_ms.
        """

        if not self.is_loaded:
            raise ModelNotLoadedError()

        try:
            start_time = time.time()

            # Le pasa el texto al modelo. top_k=None devuelve scores para TODAS las clases
            result = self._pipeline(text, top_k=None)

            processing_time = (time.time() - start_time) * 1000    # convierte a milisegundos

            # Con top_k=None el modelo devuelve [{"label": "POSITIVE", "score": 0.95}, {"label": "NEGATIVE", "score": 0.05}]
            # Ya es una lista directa, no hace falta result[0]
            scores = result

            # Busca cual tiene el score mas alto
            best = max(scores, key=lambda x: x["score"])

            # El modelo usa nombres como "POSITIVE"/"LABEL_0", los mapeamos a nuestro Enum
            label_mapping = {
                "POSITIVE": SentimentLabel.POSITIVE,
                "NEGATIVE": SentimentLabel.NEGATIVE,
                "NEUTRAL": SentimentLabel.NEUTRAL,
                "LABEL_0": SentimentLabel.NEGATIVE,    # algunos modelos usan LABEL_0/LABEL_1
                "LABEL_1": SentimentLabel.POSITIVE,
            }

            # .get() busca en el diccionario. Si no encuentra, usa NEUTRAL como fallback
            sentiment = label_mapping.get(
                best["label"].upper(),
                SentimentLabel.NEUTRAL
            )

            # Construye la lista de scores con nuestros labels
            normalized_scores = []
            for s in scores:
                mapped_label = label_mapping.get(
                    s["label"].upper(),
                    SentimentLabel.NEUTRAL
                )
                normalized_scores.append({
                    "label": mapped_label,
                    "score": s["score"]
                })

            return {
                "sentiment": sentiment,
                "confidence": best["score"],
                "scores": normalized_scores,
                "processing_time_ms": processing_time
            }

        except Exception as e:
            logger.error(f"Error en prediccion: {e}")
            raise PredictionError(f"Error durante la prediccion: {e}", e)

    def predict_batch(self, texts: List[str]) -> List[dict]:
        """Analiza multiples textos de una vez."""
        return [self.predict(text) for text in texts]


# Instancia global (por el Singleton, siempre es la misma)
# Se importa asi: from app.ml.model import sentiment_model
sentiment_model = SentimentModel()
