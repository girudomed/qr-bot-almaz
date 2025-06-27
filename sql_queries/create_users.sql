CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    phone TEXT,
    chat_id BIGINT,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, approved, declined
    role TEXT NOT NULL DEFAULT 'user',      -- user, admin, superuser
    is_superuser BOOLEAN DEFAULT FALSE,
    can_approve_registrations BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Добавить главного администратора (username = gayazking)
INSERT INTO users (telegram_id, first_name, last_name, username, chat_id, status, role)
VALUES (0, '', '', 'gayazking', 0, 'approved', 'admin')
ON CONFLICT (telegram_id) DO NOTHING;
