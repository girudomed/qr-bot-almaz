-- Сменить пароль существующего пользователя
ALTER USER gayazking1 WITH PASSWORD 'master940nw';

-- Дать все права на базу postgres (или нужную базу)
GRANT ALL PRIVILEGES ON DATABASE postgres TO gayazking1;

-- Дать все права на все таблицы и последовательности в public
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gayazking1;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gayazking1;
GRANT USAGE ON SCHEMA public TO gayazking1;
GRANT CREATE ON SCHEMA public TO gayazking1;

-- Отключить RLS для таблицы branches (если ещё не отключено)
ALTER TABLE branches DISABLE ROW LEVEL SECURITY;
