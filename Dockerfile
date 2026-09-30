# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Ortam değişkenleri
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATABASE_PATH=/app/data/servisflow.db

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları ve curl (sağlık kontrolü için)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Güvenlik: Non-root kullanıcı oluştur
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Uygulama kodunu kopyala
COPY --chown=appuser:appuser app/ ./app/

# Güvenlik için non-root kullanıcıya geç
USER appuser

# Uygulama portu
EXPOSE 8000

# Sağlık kontrolü
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Çalıştırma komutu
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
