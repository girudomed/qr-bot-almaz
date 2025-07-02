#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импортов в Docker контейнере
"""

import sys
import os

print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")
print(f"Current working directory: {os.getcwd()}")
print(f"PYTHONPATH environment: {os.environ.get('PYTHONPATH', 'Not set')}")

print("\n=== Тестирование импортов ===")

try:
    print("1. Импорт utils...")
    import utils
    print("   ✅ utils импортирован успешно")
except Exception as e:
    print(f"   ❌ Ошибка импорта utils: {e}")

try:
    print("2. Импорт utils.httpx_proxy_patch...")
    import utils.httpx_proxy_patch
    print("   ✅ utils.httpx_proxy_patch импортирован успешно")
except Exception as e:
    print(f"   ❌ Ошибка импорта utils.httpx_proxy_patch: {e}")

try:
    print("3. Импорт основных зависимостей...")
    from dotenv import load_dotenv
    from supabase import create_client
    from telegram import Bot
    import asyncio
    import schedule
    print("   ✅ Основные зависимости импортированы успешно")
except Exception as e:
    print(f"   ❌ Ошибка импорта основных зависимостей: {e}")

print("\n=== Тест завершен ===")
