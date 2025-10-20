# 🚀 ИНСТРУКЦИЯ ПО РАЗВЕРТЫВАНИЮ ИСПРАВЛЕНИЙ

## ⚡ Быстрое развертывание

### 1. Остановить текущие контейнеры
```bash
docker-compose down
```

### 2. Пересобрать образ с исправлениями
```bash
docker-compose build --no-cache
```

### 3. Запустить обновленные контейнеры.
```bash
docker-compose up -d
```

### 4. Проверить статус
```bash
docker-compose ps
```

### 5. Проверить логи бота
```bash
docker-compose logs -f bot
```

## 🔍 Проверка работоспособности

### Тест обработки фото QR-кодов:
1. Отправьте фото QR-кода в бота
2. Убедитесь, что нет ошибок `Permission denied`
3. Проверьте, что QR-код успешно распознается

### Ожидаемые логи:
```
bot-1  | INFO Фото скачано: /app/temp/temp_qr_abc123.jpg, размер: 45678 байт
bot-1  | INFO Изображение открыто: (800, 600), режим: RGB
bot-1  | INFO QR-код успешно декодирован: /qr_...
bot-1  | INFO Временный файл удален: /app/temp/temp_qr_abc123.jpg
```

### Тест прав доступа:
```bash
# Проверить права в контейнере
docker-compose exec bot ls -la /app/temp/
docker-compose exec bot touch /app/temp/test.txt
```

## ❌ Устранение проблем

### Если контейнеры не запускаются:
```bash
# Проверить логи
docker-compose logs

# Очистить все и пересобрать
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

### Если остались ошибки Permission denied:
```bash
# Проверить права в контейнере
docker-compose exec bot ls -la /tmp/
docker-compose exec bot whoami
```

## ✅ Критерии успешного развертывания

- [ ] Все 4 контейнера запущены и имеют статус "healthy"
- [ ] Бот отвечает на команды
- [ ] Фото QR-кодов обрабатываются без ошибок
- [ ] В логах нет ошибок Permission denied
- [ ] Временные файлы создаются и удаляются корректно

---

**Время развертывания:** ~3-5 минут
**Требуется перезапуск:** Да (с пересборкой образа)
