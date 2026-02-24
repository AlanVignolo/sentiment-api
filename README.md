# Sentiment API

API REST para análisis de sentimientos usando Machine Learning.

![CI](https://github.com/TU_USUARIO/sentiment-api/workflows/CI/badge.svg)
[![codecov](https://codecov.io/gh/TU_USUARIO/sentiment-api/branch/main/graph/badge.svg)](https://codecov.io/gh/TU_USUARIO/sentiment-api)

---

## Descripción

Analiza el sentimiento de textos en inglés usando el modelo `distilbert-base-uncased-finetuned-sst-2-english` de HuggingFace. Devuelve si el texto es **positivo**, **negativo** o **neutral**, con un nivel de confianza.

---

## 🚀 Quick Start

### Con Docker (Recomendado)

```bash
# Clonar repositorio
git clone https://github.com/TU_USUARIO/sentiment-api.git
cd sentiment-api

# Construir y ejecutar
docker-compose up --build

# La API estará disponible en http://localhost:8000
```

### Sin Docker

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
# .\venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
uvicorn app.main:app --reload
```

---

## 📡 Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información general de la API |
| GET | `/api/v1/health` | Estado de la API |
| GET | `/api/v1/health/detailed` | Estado detallado con info del modelo |
| GET | `/api/v1/health/ready` | Verifica si el modelo está cargado |
| POST | `/api/v1/sentiment/analyze` | Analiza el sentimiento de un texto |
| POST | `/api/v1/sentiment/analyze/batch` | Analiza múltiples textos a la vez |

### Ejemplo de uso

```bash
curl -X POST "http://localhost:8000/api/v1/sentiment/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this product! It is amazing."}'
```

Respuesta:
```json
{
  "text": "I love this product! It is amazing.",
  "sentiment": "positive",
  "confidence": 0.9998,
  "scores": [
    {"label": "positive", "score": 0.9998},
    {"label": "negative", "score": 0.0002}
  ],
  "processing_time_ms": 45.2,
  "model_version": "distilbert-base-uncased-finetuned-sst-2-english"
}
```

La documentación interactiva está disponible en `http://localhost:8000/docs` (Swagger UI).

---

## 🧪 Tests

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Correr todos los tests
pytest

# Con reporte de cobertura
pytest --cov=app --cov-report=term-missing
```

Cobertura actual: **86%** — 26 tests.

---

## 📁 Estructura del proyecto

```
sentiment-api/
├── app/
│   ├── api/
│   │   ├── dependencies.py        # inyección de dependencias (Depends)
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py      # endpoints /health
│   │       │   └── sentiment.py   # endpoints /sentiment/analyze
│   │       └── router.py          # agrupa todos los routers de v1
│   ├── core/
│   │   ├── exceptions.py          # excepciones personalizadas
│   │   └── logging.py             # configuración de logs
│   ├── ml/
│   │   ├── model.py               # wrapper del modelo HuggingFace
│   │   ├── pipeline.py            # orquestador: preprocesar → predecir → respuesta
│   │   └── preprocessor.py        # limpieza de texto (URLs, emails, espacios)
│   ├── schemas/
│   │   ├── health.py              # schemas de request/response para health
│   │   └── sentiment.py           # schemas de request/response para sentiment
│   ├── config.py                  # configuración con variables de entorno
│   └── main.py                    # app FastAPI, middleware, exception handlers
├── docker/
│   └── Dockerfile                 # imagen Docker (multi-stage build)
├── tests/
│   ├── conftest.py                # fixtures compartidos (client, load_model)
│   ├── test_api/
│   │   ├── test_health.py         # tests de endpoints de salud
│   │   └── test_sentiment.py      # tests de endpoints de sentimiento
│   └── test_ml/
│       └── test_pipeline.py       # tests de preprocesador, modelo y pipeline
├── .github/
│   └── workflows/
│       └── ci.yml                 # CI: lint + tests + build Docker automático
├── docker-compose.yml
├── pyproject.toml                 # configuración de black, isort, pytest, coverage
├── .flake8                        # configuración del linter
├── requirements.txt               # dependencias de producción
└── requirements-dev.txt           # dependencias de desarrollo (tests, linters)
```

---

## 🛠️ Tech Stack

| Herramienta | Uso |
|---|---|
| **FastAPI** | Framework web para la API REST |
| **HuggingFace Transformers** | Modelo de ML para análisis de sentimientos |
| **Pydantic** | Validación de datos y schemas |
| **Docker** | Containerización |
| **pytest** | Tests automáticos |
| **GitHub Actions** | CI/CD automático |

---

## License

MIT
