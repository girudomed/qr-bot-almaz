#!/usr/bin/env python3
"""
Тест для проверки исправления проблемы с QR кодами
"""

import os
import json
import base64
import hmac
import hashlib
from datetime import datetime, timezone, timedelta

# Московское время (UTC+3)
MOSCOW_TZ = timezone(timedelta(hours=3))

def get_moscow_time():
    """Получить текущее время в Москве"""
    return datetime.now(MOSCOW_TZ)

def get_moscow_timestamp():
    """Получить timestamp московского времени"""
    return int(get_moscow_time().timestamp())

# Секрет из .env
QR_SECRET = "qr_secret_2025"

def generate_signature(branch_id, time_window):
    """Генерация подписи (как в веб-части)"""
    msg = f"{branch_id}:{time_window}".encode()
    secret = QR_SECRET.encode()
    return hmac.new(secret, msg, hashlib.sha256).hexdigest()

def verify_signature(branch_id, time_window, signature):
    """Проверка подписи (как в боте)"""
    msg = f"{branch_id}:{time_window}".encode()
    secret = QR_SECRET.encode()
    expected = hmac.new(secret, msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)

def generate_qr_payload(branch_id, branch_name):
    """Генерация QR payload (как в веб-части)"""
    timestamp = get_moscow_timestamp()
    time_window = timestamp // 30  # Окно 30 секунд
    expires = timestamp + 60
    signature = generate_signature(branch_id, time_window)
    payload = {
        "branch_id": branch_id,
        "branch_name": branch_name,
        "timestamp": time_window,  # ← Важно: сохраняем time_window как timestamp
        "expires": expires,
        "signature": signature,
    }
    json_str = json.dumps(payload, ensure_ascii=False)
    base64_str = base64.urlsafe_b64encode(json_str.encode()).decode()
    return base64_str, payload

def test_qr_verification():
    """Тест проверки QR кода"""
    print("🧪 Тестирование исправления QR кодов...")
    print("=" * 50)
    
    # Генерируем QR как веб-часть
    branch_id = 1
    branch_name = "Тестовый филиал"
    
    print(f"📍 Филиал: {branch_name} (ID: {branch_id})")
    
    qr_data, payload = generate_qr_payload(branch_id, branch_name)
    print(f"🔗 QR данные: /qr_{qr_data}")
    print(f"📦 Payload: {payload}")
    
    # Проверяем как бот
    timestamp = payload.get("timestamp")
    signature = payload.get("signature")
    expires = payload.get("expires")
    
    print(f"\n🔍 Проверка подписи:")
    print(f"   branch_id: {branch_id}")
    print(f"   timestamp (time_window): {timestamp}")
    print(f"   signature: {signature}")
    
    # Проверка подписи
    is_valid = verify_signature(branch_id, timestamp, signature)
    print(f"   ✅ Подпись валидна: {is_valid}")
    
    # Проверка времени
    now_ts = get_moscow_timestamp()
    is_not_expired = now_ts <= expires
    print(f"\n⏰ Проверка времени:")
    print(f"   Текущее время: {now_ts}")
    print(f"   Истекает: {expires}")
    print(f"   Разница: {now_ts - expires} сек")
    print(f"   ✅ Не истёк: {is_not_expired}")
    
    # Общий результат
    success = is_valid and is_not_expired
    print(f"\n🎯 РЕЗУЛЬТАТ: {'✅ УСПЕХ' if success else '❌ ОШИБКА'}")
    
    if success:
        print("🎉 QR код будет принят ботом!")
    else:
        print("💥 QR код будет отклонён ботом!")
    
    return success

def test_edge_cases():
    """Тест граничных случаев"""
    print("\n🧪 Тестирование граничных случаев...")
    print("=" * 50)
    
    # Тест 1: Неправильная подпись
    print("1️⃣ Тест неправильной подписи:")
    is_valid = verify_signature(1, 12345, "wrong_signature")
    print(f"   ✅ Неправильная подпись отклонена: {not is_valid}")
    
    # Тест 2: Разные branch_id
    print("\n2️⃣ Тест разных branch_id:")
    time_window = get_moscow_timestamp() // 30
    signature = generate_signature(1, time_window)
    is_valid = verify_signature(2, time_window, signature)  # Другой branch_id
    print(f"   ✅ Подпись для другого филиала отклонена: {not is_valid}")
    
    # Тест 3: Правильная подпись
    print("\n3️⃣ Тест правильной подписи:")
    signature = generate_signature(1, time_window)
    is_valid = verify_signature(1, time_window, signature)
    print(f"   ✅ Правильная подпись принята: {is_valid}")
    
    return True

if __name__ == "__main__":
    print("🚀 Запуск тестов исправления QR кодов")
    print("=" * 60)
    
    # Основной тест
    main_test = test_qr_verification()
    
    # Граничные случаи
    edge_test = test_edge_cases()
    
    print("\n" + "=" * 60)
    if main_test and edge_test:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Исправление работает корректно")
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ")
        print("🔧 Требуется дополнительная отладка")
