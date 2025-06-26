-- Initial schema for family budget app

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(14,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    description TEXT,
    spent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed default categories
INSERT INTO categories(name) VALUES ('Продукты') ON CONFLICT DO NOTHING;
INSERT INTO categories(name) VALUES ('Транспорт') ON CONFLICT DO NOTHING;
INSERT INTO categories(name) VALUES ('Развлечения') ON CONFLICT DO NOTHING;

-- =============================================================
-- Дополнительные таблицы для расширенного учёта семейного бюджета
-- =============================================================

-- Счета (кошельки, карты и т.д.)
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    balance NUMERIC(14,2) NOT NULL DEFAULT 0
);

-- Доходы
CREATE TABLE IF NOT EXISTS incomes (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(14,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    description TEXT,
    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Переводы между счетами
CREATE TABLE IF NOT EXISTS transfers (
    id SERIAL PRIMARY KEY,
    from_account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    to_account_id INTEGER REFERENCES accounts(id) ON DELETE SET NULL,
    amount NUMERIC(14,2) NOT NULL,
    description TEXT,
    transferred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (from_account_id <> to_account_id)
);

-- Месячные бюджеты по категориям
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    month DATE NOT NULL,
    planned NUMERIC(14,2) NOT NULL,
    UNIQUE(category_id, month)
);

-- Seed default accounts
INSERT INTO accounts(name) VALUES ('Наличные') ON CONFLICT DO NOTHING;
INSERT INTO accounts(name) VALUES ('Банковская карта') ON CONFLICT DO NOTHING;
