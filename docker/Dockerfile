FROM python:3.12.9-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar proyecto
COPY backend/ .

# Crear directorios necesarios
RUN mkdir -p /app/dataset/raw /app/dataset/processed /app/ml_models /app/logs

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput || true

# Puerto
EXPOSE 8000

# Script de entrada
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]