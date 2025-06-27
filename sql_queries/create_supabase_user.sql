-- Создать пользователя с логином gayazking1@gmail.com и паролем master940nw
-- (логин в PostgreSQL не может содержать @, поэтому используем подчеркивание или только имя)

CREATE USER gayazking1 WITH PASSWORD 'master940nw';

-- Дать все права на базу postgres (или нужную базу)
GRANT ALL PRIVILEGES ON DATABASE postgres TO gayazking1;

-- Дать все права на все таблицы и последовательности в public
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gayazking1;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO gayazking1;
GRANT USAGE ON SCHEMA public TO gayazking1;
GRANT CREATE ON SCHEMA public TO gayazking1;

-- Отключить RLS для таблицы branches (если ещё не отключено)
ALTER TABLE branches DISABLE ROW LEVEL SECURITY;

-- Если нужно, дать права на подключение к базе
ALTER USER gayazking1 WITH LOGIN;
