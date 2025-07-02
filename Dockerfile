# syntax=docker/dockerfile:1
###############################################################################
# 1) Базовый слой: Debian-Slim + Python 3.11
###############################################################################
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

###############################################################################
# 2) Системные зависимости
#    libzbar0   – pyzbar для QR-кодов
#    curl       – health-check
#    procps     – pgrep (health-check бота)
#    iputils-ping – ping (диагностика сети)
###############################################################################
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        libzbar0 curl procps iputils-ping build-essential && \
    rm -rf /var/lib/apt/lists/*

###############################################################################
# 3) Кэшируем Python-зависимости
###############################################################################
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn && \
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /root/.cache

###############################################################################
# 4) Копируем исходники под непривилегированного пользователя
###############################################################################
RUN useradd -m -U qrbot
COPY --chown=qrbot:qrbot . .
USER qrbot

###############################################################################
# 5) Health-check и дефолтная команда (для web)
###############################################################################
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -fs http://localhost:8080/health || exit 1

CMD ["gunicorn", "-w", "2", "-k", "gthread", "-t", "30", \
     "-b", "0.0.0.0:8080", "web.main:app"]