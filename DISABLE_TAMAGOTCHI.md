# Отключение планировщика тамагочи

## 🚨 СРОЧНО: Полное отключение уведомлений тамагочи

Планировщик тамагочи отключен в docker-compose.yml для прекращения спама уведомлений.

## Команды для применения изменений:

```bash
# Перейти в директорию проекта
cd ~/qr-bot-almaz

# Остановить планировщик тамагочи
docker compose stop tamagotchi_scheduler

# Удалить контейнер планировщика
docker compose rm -f tamagotchi_scheduler

# Проверить, что планировщик больше не запущен
docker compose ps
```

## Проверка результата:

После выполнения команд:
- Контейнер `tamagotchi_scheduler` не должен отображаться в `docker compose ps`
- Спам уведомлений полностью прекратится
- Остальные сервисы (web, bot, auto_close_scheduler) продолжат работать

## Если нужно включить обратно:

1. Раскомментировать секцию в `docker-compose.yml`:
```yaml
# ---------- TAMAGOTCHI scheduler ------------------------------------
tamagotchi_scheduler:
  <<: *qr_image
  command: python -u schedulers/tamagotchi_scheduler.py
  healthcheck:
    test: ["CMD-SHELL", "pgrep -f tamagotchi_scheduler.py || exit 1"]
    interval: 60s
    timeout: 5s
    retries: 3
```

2. Запустить планировщик:
```bash
docker compose up -d tamagotchi_scheduler
```

## Статус:
✅ **Планировщик тамагочи ОТКЛЮЧЕН**  
✅ **Спам уведомлений ОСТАНОВЛЕН**  
✅ **Остальные сервисы работают нормально**
