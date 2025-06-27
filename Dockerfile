# syntax=docker/dockerfile:1

#############################
# 1) Базовый минимальный образ
#############################
FROM python:3.11-slim

#############################
# 2) Устанавливаем системные зависимости
#############################
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libpq-dev \
 && rm -rf /var/lib/apt/lists/*

#############################
# 3) Работаем в директории /app
#############################
WORKDIR /app

#############################
# 4) Кэшируем зависимые слои
#############################
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

#############################
# 5) Копируем остальной код
#############################
COPY . .

#############################
# 6) Константы окружения + порт
#############################
ENV PYTHONUNBUFFERED=1
EXPOSE 5000

#############################
# 7) Точка входа
#############################
CMD ["python", "main.py"]