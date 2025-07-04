-- Создание таблицы для отслеживания уведомлений тамагочи
-- Эту таблицу нужно создать в Supabase

CREATE TABLE IF NOT EXISTS tamagotchi_notifications (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    notification_type VARCHAR(20) NOT NULL CHECK (notification_type IN ('critical', 'hungry', 'death')),
    sent_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Создание индексов для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_tamagotchi_notifications_telegram_id 
ON tamagotchi_notifications(telegram_id);

CREATE INDEX IF NOT EXISTS idx_tamagotchi_notifications_type_time 
ON tamagotchi_notifications(telegram_id, notification_type, sent_at DESC);

-- Добавление политики RLS (Row Level Security) если нужно
-- ALTER TABLE tamagotchi_notifications ENABLE ROW LEVEL SECURITY;

-- Комментарии к таблице
COMMENT ON TABLE tamagotchi_notifications IS 'Таблица для отслеживания отправленных уведомлений тамагочи';
COMMENT ON COLUMN tamagotchi_notifications.telegram_id IS 'ID пользователя в Telegram';
COMMENT ON COLUMN tamagotchi_notifications.notification_type IS 'Тип уведомления: critical, hungry, death';
COMMENT ON COLUMN tamagotchi_notifications.sent_at IS 'Время отправки уведомления';

-- Автоматическая очистка старых записей (опционально)
-- Удаляем записи старше 30 дней
-- CREATE OR REPLACE FUNCTION cleanup_old_notifications()
-- RETURNS void AS $$
-- BEGIN
--     DELETE FROM tamagotchi_notifications 
--     WHERE sent_at < NOW() - INTERVAL '30 days';
-- END;
-- $$ LANGUAGE plpgsql;

-- Создание задачи для автоматической очистки (если поддерживается)
-- SELECT cron.schedule('cleanup-notifications', '0 2 * * *', 'SELECT cleanup_old_notifications();');
