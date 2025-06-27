CREATE TABLE IF NOT EXISTS branches (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT
);

-- Пример наполнения:
INSERT INTO branches (name, address) VALUES
('Проспект Победы', 'пр. Победы'),
('Гвардейская', 'ул. Гвардейская'),
('Чистопольская', 'ул. Чистопольская')
ON CONFLICT DO NOTHING;
