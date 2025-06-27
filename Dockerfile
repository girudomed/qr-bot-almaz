# syntax=docker/dockerfile:1

###########################################################
# 1) Базовый образ
###########################################################
FROM python:3.11-slim

###########################################################
# 2) Системные зависимости    (только то, что реально нужно)
#    - libzbar0  : pyzbar ищет shared-lib ZBar в рантайме
#    - curl      : для HEALTHCHECK
###########################################################
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libzbar0 \
        curl \
 && rm -rf /var/lib/apt/lists/*

###########################################################
# 3) Создаём пользователя и рабочий каталог
###########################################################
RUN useradd -m qrbot
WORKDIR /app
USER qrbot

###########################################################
# 4) Python-зависимости (кэшируем слоем)
###########################################################
COPY --chown=qrbot:qrbot requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 # прод-сервер
 && pip install --no-cache-dir gunicorn

###########################################################
# 5) Копируем код (уже под владельца qrbot)
###########################################################
COPY --chown=qrbot:qrbot . .

###########################################################
# 6) Константы окружения + порт + health-check
###########################################################
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

###########################################################
# 7) Точка входа: Gunicorn
#    main:app →  файл main.py, переменная app = Flask(__name__)
###########################################################
CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]