# Инструкция по развертыванию исправлений спама тамагочи

## 🚨 СРОЧНО: Остановка спама уведомлений

### Шаг 1: Создание таблицы в Supabase

1. Откройте Supabase Dashboard
2. Перейдите в SQL Editor
3. Выполните скрипт из файла `create_notifications_table.sql`:

```sql
CREATE TABLE IF NOT EXISTS tamagotchi_notifications (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    notification_type VARCHAR(20) NOT NULL CHECK (notification_type IN ('critical', 'hungry', 'death')),
    sent_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tamagotchi_notifications_telegram_id 
ON tamagotchi_notifications(telegram_id);

CREATE INDEX IF NOT EXISTS idx_tamagotchi_notifications_type_time 
ON tamagotchi_notifications(telegram_id, notification_type, sent_at DESC);
```

### Шаг 2: Перезапуск планировщика

```bash
# Перейти в директорию проекта
cd ~/qr-bot-almaz

# Перезапустить только планировщик тамагочи
docker compose restart tamagotchi_scheduler

# Проверить статус
docker compose ps tamagotchi_scheduler
```

### Шаг 3: Проверка работы

```bash
# Просмотр логов в реальном времени
docker compose logs -f tamagotchi_scheduler

# Проверка последних 50 записей
docker compose logs --tail=50 tamagotchi_scheduler
```

### Шаг 4: Мониторинг

После развертывания следите за логами. Вы должны увидеть:

✅ **Правильное поведение:**
- Уведомления отправляются только в рабочие часы (9:00-18:00 МСК)
- Сообщения типа "Проверка рабочего времени" в логах
- Меньше уведомлений в целом

❌ **Если проблемы продолжаются:**
- Проверьте, создалась ли таблица `tamagotchi_notifications`
- Убедитесь, что планировщик перезапустился с новым кодом

### Экстренная остановка (если нужно)

```bash
# Полная остановка планировщика
docker compose stop tamagotchi_scheduler

# Запуск обратно
docker compose start tamagotchi_scheduler
```

---

## 📊 Проверка результатов

### В Supabase (SQL Editor):

```sql
-- Проверить созданную таблицу
SELECT * FROM tamagotchi_notifications ORDER BY sent_at DESC LIMIT 10;

-- Статистика за сегодня
SELECT 
    notification_type,
    COUNT(*) as count,
    MIN(sent_at) as first_sent,
    MAX(sent_at) as last_sent
FROM tamagotchi_notifications 
WHERE DATE(sent_at) = CURRENT_DATE
GROUP BY notification_type;
```

### В логах Docker:

Ищите строки:
- `"Проверка голодных тамагочи..."`
- `"Проверка тамагочи завершена"`
- `"Отправлено ... уведомление пользователю"`

---

## 🎯 Ожидаемый результат

После развертывания:
- **Ночной спам прекратится** (уведомления только 9:00-18:00 МСК)
- **Критические уведомления** - максимум раз в 4 часа
- **Обычные уведомления** - максимум раз в 6 часов
- **Уведомления о смерти** - максимум раз в день

---

## 🆘 Если что-то пошло не так

1. **Откатить изменения:**
   ```bash
   git checkout HEAD~1 schedulers/tamagotchi_scheduler.py
   docker compose restart tamagotchi_scheduler
   ```

2. **Связаться с разработчиком**

3. **Временно отключить планировщик:**
   ```bash
   docker compose stop tamagotchi_scheduler
   ```

---

**Время развертывания:** ~5 минут  
**Простой системы:** Минимальный (только перезапуск планировщика)  
**Риски:** Низкие (изменения только в логике уведомлений)
