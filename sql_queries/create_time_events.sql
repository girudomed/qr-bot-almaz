CREATE TABLE IF NOT EXISTS time_events (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    username TEXT,
    chat_id BIGINT,
    branch_id INTEGER NOT NULL,
    branch_name TEXT,
    event_time TIMESTAMP NOT NULL,
    event_type TEXT NOT NULL, -- 'arrival' или 'departure'
    is_auto_closed BOOLEAN DEFAULT FALSE, -- автоматическое закрытие
    work_hours DECIMAL(4,2), -- количество отработанных часов
    qr_timestamp INTEGER,
    signature TEXT,
    raw_json TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
