-- Initial schema for family budget app

CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(14,2) NOT NULL,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    description TEXT,
    spent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Seed default categories
INSERT INTO categories(name) VALUES ('Продукты') ON CONFLICT DO NOTHING;
INSERT INTO categories(name) VALUES ('Транспорт') ON CONFLICT DO NOTHING;
INSERT INTO categories(name) VALUES ('Развлечения') ON CONFLICT DO NOTHING;
