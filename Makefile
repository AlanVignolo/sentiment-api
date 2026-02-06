.PHONY: install test lint format run docker-build docker-run clean
# Instalar dependencias
install:
pip install -r requirements-dev.txt
# Correr tests
test:
pytest tests/ -v --cov=app --cov-report=term-missing
# Correr linter
lint:
flake8 app/ tests/
mypy app/
# Formatear código
format:
black app/ tests/
isort app/ tests/
# Correr servidor de desarrollo
run:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Construir imagen Docker
docker-build:
docker build -f docker/Dockerfile -t sentiment-api .
# Correr con Docker
docker-run:
docker-compose up
# Limpiar archivos temporales
clean:
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type d -name .pytest_cache -exec rm -rf {} +
find . -type d -name .mypy_cache -exec rm -rf {} +
find . -type f -name .coverage -delete