"""Tests para endpoints de health check."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests para los 3 endpoints de health: /health, /health/detailed, /ready."""

    def test_health_check_returns_200(self, client: TestClient):
        """GET /api/v1/health debe retornar 200 con status=healthy."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data      # HealthResponse siempre incluye timestamp

    def test_detailed_health_check_returns_200(self, client: TestClient):
        """GET /api/v1/health/detailed debe retornar 200 con lista de componentes."""
        response = client.get("/api/v1/health/detailed")    # FIX: era /api/v1/health/ready (URL incorrecta)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "components" in data
        assert len(data["components"]) > 0      # al menos el componente ml_model

    def test_readiness_check_returns_200_when_model_loaded(self, client: TestClient):
        """GET /api/v1/ready debe retornar 200 cuando el modelo esta cargado."""
        response = client.get("/api/v1/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"

    def test_root_endpoint_returns_api_info(self, client: TestClient):
        """GET / debe retornar informacion basica de la API (nombre, version, docs)."""
        response = client.get("/")      # FIX: era /api/v1/ (el root esta en /, no en /api/v1/)

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data