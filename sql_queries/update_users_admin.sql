-- Обновление таблицы users для добавления админских полей
-- Выполните этот скрипт, если таблица users уже существует

-- Добавить новые поля
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_superuser BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS can_approve_registrations BOOLEAN DEFAULT FALSE;

-- Обновить gayazking как суперпользователя
UPDATE users 
SET is_superuser = TRUE, 
    role = 'superuser', 
    can_approve_registrations = TRUE 
WHERE username = 'gayazking';

-- Если gayazking еще не существует, создать его
INSERT INTO users (telegram_id, first_name, last_name, username, chat_id, status, role, is_superuser, can_approve_registrations)
VALUES (0, '', '', 'gayazking', 0, 'approved', 'superuser', TRUE, TRUE)
ON CONFLICT (telegram_id) DO UPDATE SET
    is_superuser = TRUE,
    role = 'superuser',
    can_approve_registrations = TRUE;
