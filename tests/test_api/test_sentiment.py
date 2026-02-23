"""
Tests para los endpoints de analisis de sentimientos.
Prueba que /analyze y /analyze/batch respondan correctamente para distintos casos.
"""

import pytest
from fastapi.testclient import TestClient


# ============================================================
# Tests para POST /api/v1/sentiment/analyze (un solo texto)
# ============================================================
class TestSentimentAnalyzeEndpoint:
    """Tests para POST /api/v1/sentiment/analyze"""

    def test_analyze_positive_text(self, client: TestClient, sample_texts):
        """Textos positivos deben clasificarse como positivos."""
        # Itera sobre los 3 textos positivos del fixture sample_texts de conftest.py
        for text in sample_texts["positive"]:
            response = client.post(
                "/api/v1/sentiment/analyze",
                json={"text": text}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["sentiment"] == "positive"      # SentimentLabel.POSITIVE.value = "positive" (minuscula)
            assert data["confidence"] > 0.5             # debe estar seguro (mas del 50%)

    def test_analyze_negative_text(self, client: TestClient, sample_texts):
        """Textos negativos deben clasificarse como negativos."""
        for text in sample_texts["negative"]:
            response = client.post(
                "/api/v1/sentiment/analyze",
                json={"text": text}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["sentiment"] == "negative"      # SentimentLabel.NEGATIVE.value = "negative"
            assert data["confidence"] > 0.5

    def test_analyze_returns_required_fields(self, client: TestClient):
        """La respuesta debe incluir todos los campos definidos en SentimentResponse."""
        response = client.post(
            "/api/v1/sentiment/analyze",
            json={"text": "Test text."}
        )

        assert response.status_code == 200
        data = response.json()

        # Si falta algun campo, el mensaje de error dice exactamente cual ("Missing field: X")
        required_fields = {"sentiment", "confidence", "scores", "processing_time_ms", "model_version", "timestamp"}
        for field in required_fields:
            assert field in data, f"Missing field: {field}"

    def test_analyze_empty_text_returns_422(self, client: TestClient):
        """Texto vacio debe retornar 422: SentimentRequest tiene min_length=1."""
        response = client.post(
            "/api/v1/sentiment/analyze",
            json={"text": ""}
        )

        assert response.status_code == 422      # 422 = Unprocessable Entity (datos invalidos)

    def test_analyze_whitespace_only_returns_422(self, client: TestClient):
        """Texto con solo espacios debe retornar 422: el field_validator llama strip() y rechaza."""
        response = client.post(
            "/api/v1/sentiment/analyze",
            json={"text": "     "}
        )

        assert response.status_code == 422

    def test_analyze_missing_text_returns_422(self, client: TestClient):
        """Request sin el campo 'text' debe retornar 422: campo obligatorio (...) ausente."""
        response = client.post(
            "/api/v1/sentiment/analyze",
            json={}     # "text" es requerido, pydantic lo rechaza automaticamente
        )

        assert response.status_code == 422


# Test de funcion suelta (fuera de clase): tambien es valido en pytest
def test_analyze_with_language_parameter(client: TestClient):
    """El campo opcional 'language' debe aceptarse sin errores."""
    response = client.post(
        "/api/v1/sentiment/analyze",
        json={
            "text": "I love this product!",
            "language": "en"    # opcional, default="en" en SentimentRequest
        }
    )

    assert response.status_code == 200


# ============================================================
# Tests para POST /api/v1/sentiment/analyze/batch (varios textos)
# ============================================================
class TestSentimentBatchAnalyzeEndpoint:
    """Tests para POST /api/v1/sentiment/analyze/batch"""

    def test_batch_analyze_multiple_texts(self, client: TestClient, sample_texts):
        """Batch debe analizar todos los textos y el conteo en la respuesta debe ser correcto."""
        # [:2] = toma los primeros 2 de cada lista. Total: 2 positivos + 2 negativos = 4
        texts = sample_texts["positive"][:2] + sample_texts["negative"][:2]

        response = client.post(
            "/api/v1/sentiment/analyze/batch",
            json={"texts": texts}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["texts_analyzed"] == 4      # 2+2 = 4 textos enviados
        assert len(data["results"]) == 4         # un SentimentResponse por cada texto

    def test_batch_empty_list_returns_422(self, client: TestClient):
        """Lista vacia debe retornar 422: BatchSentimentRequest requiere al menos 1 texto."""
        response = client.post(
            "/api/v1/sentiment/analyze/batch",
            json={"texts": []}      # lista vacia, pydantic la rechaza
        )

        assert response.status_code == 422

    def test_batch_returns_processing_time(self, client: TestClient):
        """La respuesta batch debe incluir el tiempo total que tardaron todos los analisis."""
        response = client.post(
            "/api/v1/sentiment/analyze/batch",
            json={"texts": ["Text 1", "Text 2"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_processing_time_ms" in data       # el campo existe en BatchSentimentResponse
        assert data["total_processing_time_ms"] > 0     # y el tiempo siempre es mayor a 0
    