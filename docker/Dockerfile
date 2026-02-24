# =============================================================
# Dockerfile con construccion en 2 etapas (multi-stage build).
#
# ETAPA 1 (builder): instala dependencias y compila lo necesario.
# ETAPA 2 (runtime): copia solo lo necesario del builder.
# Resultado: imagen final mucho mas chica (sin herramientas de compilacion).
# =============================================================


# ----- ETAPA 1: builder -----
# "python:3.11-slim" = imagen oficial de Python 3.11 recortada (sin extras del SO)
FROM python:3.11-slim as builder

# /app sera el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala build-essential: compiladores C/C++ necesarios para algunas libs de Python (ej: numpy)
# --no-install-recommends evita instalar paquetes extra no necesarios
# rm -rf /var/lib/apt/lists/* borra la cache de apt para achicar la imagen
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de dependencias al contenedor
COPY requirements.txt .

# Crea un virtualenv en /opt/venv para aislar las dependencias
RUN python -m venv /opt/venv

# Agrega el venv al PATH para que "pip" y "python" usen el venv
ENV PATH="/opt/venv/bin:$PATH"

# Instala las dependencias dentro del venv
# --no-cache-dir evita guardar cache de pip (ahorra espacio en la imagen)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ----- ETAPA 2: runtime -----
# Nueva imagen limpia: NO tiene build-essential ni cache de compilacion
FROM python:3.11-slim as runtime

WORKDIR /app

# Copia solo el virtualenv ya construido desde la etapa builder
# --from=builder indica que viene de la etapa anterior, no del sistema local
COPY --from=builder /opt/venv /opt/venv

# Activa el venv en la etapa runtime tambien
ENV PATH="/opt/venv/bin:$PATH"

# Copia el codigo fuente de la aplicacion al contenedor
COPY app/ ./app/

# Seguridad: crea un usuario sin privilegios de root (buena practica en produccion)
# FIX: "uppuser" → "appuser" (typo en el nombre del usuario)
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

# Cambia al usuario sin privilegios
USER appuser

# Variables de entorno importantes para Docker:
# PYTHONUNBUFFERED=1     → Python escribe los logs directo a stdout (sin buffer), se ven en tiempo real
# PYTHONDONTWRITEBYTECODE=1 → Python no crea archivos .pyc (ahorra espacio)
# ENV=production         → la app detecta que esta en produccion (ver config.py)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=production

# Declara que el contenedor usa el puerto 8000
# FIX: "EXPOSE 800" → "EXPOSE 8000" (faltaba un cero)
EXPOSE 8000

# Health check: Docker verifica cada 30s que la API este respondiendo
# --start-period=60s le da 60s al modelo para cargarse antes del primer chequeo
# Si falla 3 veces seguidas, Docker marca el contenedor como "unhealthy"
# FIX: httpx no esta en requirements.txt. Se usa urllib.request que viene con Python (siempre disponible).
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

# Comando que se ejecuta al iniciar el contenedor
# Equivale a: uvicorn app.main:app --host 0.0.0.0 --port 8000
# 0.0.0.0 = acepta conexiones desde cualquier IP (necesario dentro de Docker)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
