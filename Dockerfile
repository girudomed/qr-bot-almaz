# syntax=docker/dockerfile:1
###############################################################################
# 1) База: Debian-Slim + Python 3.11
###############################################################################
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

###############################################################################
# 2) Системные зависимости
#    libzbar0   – pyzbar (распознавание QR)
#    curl       – health-check
#    procps/ping – pgrep + ping (диагностика в контейнере)
###############################################################################
RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        libzbar0 curl procps iputils-ping build-essential && \
    rm -rf /var/lib/apt/lists/*

###############################################################################
# 3) Python-зависимости
#    – основной requirements.txt (+ gunicorn)
#    – Supabase-py 1.0.3 и его подпакеты --no-deps
#      (чтобы не притянуть «старый» httpx<0.24)
###############################################################################
WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn && \
    # --- Supabase-py 1.x + подпакеты, но БЕЗ зависимостей ---
    pip install --no-cache-dir \
        supabase==1.0.3 \
        gotrue==1.3.1 \
        realtime==1.0.2 \
        storage3==0.7.0 \
        --no-deps && \
    # --- clean ---
    apt-get purge -y --auto-remove build-essential && \
    rm -rf /root/.cache

###############################################################################
# 4) Исходники и непривилегированный пользователь
###############################################################################
RUN useradd -m -U qrbot
COPY --chown=qrbot:qrbot . .
USER qrbot

###############################################################################
# 5) Порт, health-check и дефолтный CMD (Web)
###############################################################################
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -fs http://localhost:8080/health || exit 1

CMD ["gunicorn", "-w", "2", "-k", "gthread", "-t", "30", \
     "-b", "0.0.0.0:8080", "web.main:app"]