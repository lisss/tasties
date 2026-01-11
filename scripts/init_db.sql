CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    order_type TEXT NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    remaining INTEGER NOT NULL
);
