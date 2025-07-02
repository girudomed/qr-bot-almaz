# syntax=docker/dockerfile:1
###############################################################################
# 1) База: Debian-Slim + Python 3.11
###############################################################################
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

###############################################################################
# 2) Системные пакеты
###############################################################################
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        libzbar0 curl procps iputils-ping build-essential && \
    rm -rf /var/lib/apt/lists/*

###############################################################################
# 3) Python-зависимости
#    3.1 base requirements + gunicorn
#    3.2 вся экосистема Supabase 2.x с зависимостями
#    3.3 обновляем httpx до 0.25.2 (нужен PTB и FastAPI)
###############################################################################
WORKDIR /app
COPY requirements.txt .

# 3.1 base
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# 3.2 Supabase-py 2.x (+ postgrest, storage3, supafunc … подтянутся сами)
RUN pip install --no-cache-dir supabase==2.16.0

# 3.3 httpx 0.25.2 поверх (pip лишь выдаст предупреждение — это нормально)
RUN pip install --no-cache-dir --upgrade httpx==0.25.2

# Чистим build-tools
RUN apt-get purge -y --auto-remove build-essential && \
    rm -rf /root/.cache

###############################################################################
# 4) Исходники под непривилегированного пользователя
###############################################################################
RUN useradd -m -U qrbot
COPY --chown=qrbot:qrbot . .
USER qrbot

###############################################################################
# 5) Порт, health-check, CMD
###############################################################################
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -fs http://localhost:8080/health || exit 1

CMD ["gunicorn", "-w", "2", "-k", "gthread", "-t", "30", \
     "-b", "0.0.0.0:8080", "web.main:app"]
