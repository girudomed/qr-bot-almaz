-- Отключить Row Level Security (RLS) для таблицы branches
ALTER TABLE branches DISABLE ROW LEVEL SECURITY;

-- Дать все права пользователю postgres
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT USAGE ON SCHEMA public TO postgres;
GRANT CREATE ON SCHEMA public TO postgres;
