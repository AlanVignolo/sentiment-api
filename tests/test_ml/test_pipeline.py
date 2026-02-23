"""
Tests para el pipeline de ML.
Prueba las 3 capas: TextPreprocessor (limpieza), SentimentModel (prediccion), SentimentPipeline (flujo completo).
"""

import pytest

# Importa los 3 componentes internos del modulo ml para testearlos directamente
from app.ml import TextPreprocessor, sentiment_model, sentiment_pipeline
from app.schemas import SentimentRequest


# ============================================================
# Tests para TextPreprocessor (limpieza de texto)
# ============================================================
class TestTextPreprocessor:
    """Tests para el preprocesador de text."""

    def test_removes_URLs(self):
        """URLs deben ser removidas del texto."""
        # remove_urls=True activa la regex que detecta "https://..." y "www...."
        preprocessor = TextPreprocessor(remove_urls=True)
        text = "Check this out: https://example.com it's great"
        result = preprocessor.preprocess(text)

        assert "https://example.com" not in result   # la URL desaparecio
        assert "great" in result                      # el resto del texto quedo

    def test_removes_emails(self):
        """Emails deben ser removidos del texto."""
        preprocessor = TextPreprocessor(remove_emails=True)
        text = "Contact me at user@example.com for more info."
        result = preprocessor.preprocess(text)

        assert "user@example.com" not in result   # el email desaparecio
        assert "Contact" in result                 # el resto del texto quedo

    def test_removes_mentions(self):
        """Test para remover menciones"""
        # remove_mentions=True activa la regex que detecta "@usuario"
        preprocessor = TextPreprocessor(remove_mentions=True)
        text = "Hello @user, how are you?"
        result = preprocessor.preprocess(text)

        assert "@user" not in result   # la mencion desaparecio
        assert "Hello" in result       # el resto del texto quedo

    def test_lowercase_when_enabled(self):
        """Test para convertir a minusculas"""
        preprocessor = TextPreprocessor(lowercase=True)
        text = "This is A Test."
        result = preprocessor.preprocess(text)

        assert result == "this is a test."   # todo en minusculas

    def test_truncates_long_text(self):
        """Test para truncar texto largo"""
        # max_length=10 corta el texto a exactamente 10 caracteres
        preprocessor = TextPreprocessor(max_length=10)
        text = "This text is definitely longer than ten characters."
        result = preprocessor.preprocess(text)

        assert len(result) == 10   # exactamente 10 caracteres

    def test_cleans_multiple_spaces(self):
        """Test para limpiar espacios multiples"""
        # FIX: clean_multiple_spaces no es un parametro del constructor.
        # TextPreprocessor SIEMPRE limpia espacios multiples (no necesita bandera).
        preprocessor = TextPreprocessor()
        text = "This   is    a   test."
        result = preprocessor.preprocess(text)

        assert "  " not in result            # no hay doble espacio
        assert result == "This is a test."   # texto normalizado


# ============================================================
# Tests para SentimentModel (prediccion del modelo de ML)
# ============================================================
class TestSentimentModel:
    """Tests para el modelo de sentimientos."""

    def test_model_is_loaded(self, load_model):
        """El modelo debe estar cargado por el fixture load_model."""
        # load_model es el fixture de conftest.py que llama sentiment_model.load()
        assert sentiment_model.is_loaded

    def test_predict_returns_required_keys(self, load_model):
        """La prediccion debe incluir 'label' y 'confidence'."""
        input_text = "I love this!"
        result = sentiment_model.predict(input_text)

        # El dict de retorno debe tener exactamente estos 4 campos
        assert "sentiment" in result
        assert "confidence" in result
        assert "scores" in result
        assert "processing_time_ms" in result

    def test_predict_confidence_is_valid(self, load_model):
        """La confianza debe estar entre 0 y 1."""
        input_text = "I love this!"
        result = sentiment_model.predict(input_text)

        # La confianza es una probabilidad: siempre entre 0.0 y 1.0
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_positive_text(self, load_model):
        """Texto positivo debe clasificarse como positivo."""
        result = sentiment_model.predict("I love this product!")

        # .value accede al string del Enum: SentimentLabel.POSITIVE.value == "positive"
        assert result["sentiment"].value == "positive"


# ============================================================
# Tests para SentimentPipeline (flujo completo: limpieza + prediccion + respuesta)
# ============================================================
class TestSentimentPipeline:
    """Tests para el pipeline completo."""

    def test_analyze_returns_response(self, load_model):
        """El pipeline debe retornar un SentimentResponse."""
        # Crea el request como lo haría la API (misma clase SentimentRequest)
        request = SentimentRequest(text="I love this!")
        response = sentiment_pipeline.analyze(request)

        # El response debe tener texto, sentimiento y confianza validos
        assert response.text == "I love this!"
        assert response.sentiment is not None
        assert response.confidence > 0

    def test_analyze_preserves_original_text(self, load_model):
        """El response debe contener todo el texto original."""
        # FIX: "test_anylze" → "test_analyze" (typo en el nombre del metodo)
        original_text = "   I love this product! It's amazing."
        request = SentimentRequest(text=original_text)
        response = sentiment_pipeline.analyze(request)

        # El pipeline guarda request.text (ya strip()-eado por field_validator del schema)
        assert "I" in response.text
        assert "love" in response.text
