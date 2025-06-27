-- Обновление таблицы time_events для добавления новых полей
-- Выполните этот скрипт, если таблица time_events уже существует

-- Добавить новые поля
ALTER TABLE time_events 
ADD COLUMN IF NOT EXISTS event_type TEXT NOT NULL DEFAULT 'arrival',
ADD COLUMN IF NOT EXISTS is_auto_closed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS work_hours DECIMAL(4,2),
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

-- Обновить существующие записи (если есть) - установить тип события как 'arrival'
UPDATE time_events 
SET event_type = 'arrival' 
WHERE event_type IS NULL OR event_type = '';

-- Убрать DEFAULT для event_type после обновления существующих записей
ALTER TABLE time_events 
ALTER COLUMN event_type DROP DEFAULT;
