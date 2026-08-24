CREATE DATABASE IF NOT EXISTS comandas_db;

USE comandas_db;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

INSERT IGNORE INTO categories (name)
VALUES
    ('Bebidas'),
    ('Frios'),
    ('Lanches'),
    ('Pizzas'),
    ('Sobremesas');

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    category_id INT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (price >= 0),
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
    INDEX idx_products_category_active (category_id, active)
);

INSERT INTO products (name, price, category_id)
SELECT 'Coca-Cola', 7.50, category_id
FROM categories
WHERE name = 'Bebidas'
AND NOT EXISTS (
    SELECT 1 FROM products WHERE name = 'Coca-Cola'
);

INSERT INTO products (name, price, category_id)
SELECT 'X-Salada', 22.90, category_id
FROM categories
WHERE name = 'Lanches'
AND NOT EXISTS (
    SELECT 1 FROM products WHERE name = 'X-Salada'
);

INSERT INTO products (name, price, category_id)
SELECT 'Pudim', 9.00, category_id
FROM categories
WHERE name = 'Sobremesas'
AND NOT EXISTS (
    SELECT 1 FROM products WHERE name = 'Pudim'
);

CREATE TABLE IF NOT EXISTS command_cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    card_number CHAR(4) NOT NULL UNIQUE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (card_number REGEXP '^[0-9]{4}$')
);

INSERT IGNORE INTO command_cards (card_number)
VALUES
    ('0001'),
    ('0002'),
    ('0003'),
    ('0004'),
    ('0005');

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT NOT NULL,
    status ENUM('open', 'closed') NOT NULL DEFAULT 'open',
    opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME NULL,
    open_card_id INT
        GENERATED ALWAYS AS (
            CASE
                WHEN status = 'open' THEN card_id
                ELSE NULL
            END
        ) STORED,
    UNIQUE (open_card_id),
    CHECK (
        (status = 'open' AND closed_at IS NULL)
        OR
        (status = 'closed' AND closed_at IS NOT NULL)
    ),
    FOREIGN KEY (card_id)
        REFERENCES command_cards(card_id),
    INDEX idx_orders_status (status)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    notes VARCHAR(255) NULL,
    CHECK (quantity > 0),
    CHECK (unit_price >= 0),
    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),
    FOREIGN KEY (product_id)
        REFERENCES products(product_id),
    INDEX idx_order_items_order (order_id),
    INDEX idx_order_items_product (product_id)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('cash', 'credit', 'debit', 'pix') NOT NULL,
    sold_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (total_amount >= 0),
    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),
    INDEX idx_sales_sold_at (sold_at),
    INDEX idx_sales_payment_method (payment_method)
);

CREATE OR REPLACE VIEW vw_products AS
SELECT
    p.product_id,
    p.name AS product_name,
    p.price,
    c.category_id,
    c.name AS category_name,
    p.active
FROM products p
JOIN categories c
    ON p.category_id = c.category_id;

CREATE OR REPLACE VIEW vw_open_orders AS
SELECT
    o.order_id,
    cc.card_number,
    o.status,
    DATE_FORMAT(o.opened_at, '%H:%i  %d/%m/%Y') AS opened_at,
    COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total_amount
FROM orders o
JOIN command_cards cc
    ON o.card_id = cc.card_id
LEFT JOIN order_items oi
    ON o.order_id = oi.order_id
WHERE o.status = 'open'
GROUP BY
    o.order_id,
    cc.card_number,
    o.status,
    o.opened_at;

CREATE OR REPLACE VIEW vw_order_summary AS
SELECT
    o.order_id,
    cc.card_number,
    o.status,
    DATE_FORMAT(o.opened_at, '%H:%i  %d/%m/%Y') AS opened_at,
    DATE_FORMAT(o.closed_at, '%H:%i  %d/%m/%Y') AS closed_at,
    p.product_id,
    p.name AS product_name,
    c.name AS category_name,
    oi.quantity,
    oi.unit_price,
    oi.quantity * oi.unit_price AS subtotal,
    oi.notes,
    SUM(oi.quantity * oi.unit_price)
        OVER (PARTITION BY o.order_id) AS order_total
FROM orders o
JOIN command_cards cc
    ON o.card_id = cc.card_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
JOIN categories c
    ON p.category_id = c.category_id;

CREATE OR REPLACE VIEW vw_sales_history AS
SELECT
    s.sale_id,
    s.order_id,
    cc.card_number,
    s.total_amount,
    s.payment_method,
    CASE s.payment_method
        WHEN 'cash' THEN 'Dinheiro'
        WHEN 'credit' THEN 'Crédito'
        WHEN 'debit' THEN 'Débito'
        WHEN 'pix' THEN 'PIX'
    END AS payment_method_label,
    DATE_FORMAT(s.sold_at, '%H:%i  %d/%m/%Y') AS sold_at,
    s.sold_at AS sold_at_raw
FROM sales s
JOIN orders o
    ON s.order_id = o.order_id
JOIN command_cards cc
    ON o.card_id = cc.card_id;

CREATE OR REPLACE VIEW vw_daily_summary AS
SELECT
    DATE(sold_at) AS summary_date,
    DATE_FORMAT(sold_at, '%d/%m/%Y') AS date_label,
    COUNT(*) AS total_sales,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_ticket
FROM sales
GROUP BY DATE(sold_at), DATE_FORMAT(sold_at, '%d/%m/%Y');

CREATE OR REPLACE VIEW vw_weekly_summary AS
SELECT
    YEARWEEK(sold_at, 1) AS year_week,
    COUNT(*) AS total_sales,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_ticket
FROM sales
GROUP BY YEARWEEK(sold_at, 1);

CREATE OR REPLACE VIEW vw_monthly_summary AS
SELECT
    YEAR(sold_at) AS year,
    MONTH(sold_at) AS month,
    DATE_FORMAT(sold_at, '%m/%Y') AS month_label,
    COUNT(*) AS total_sales,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_ticket
FROM sales
GROUP BY
    YEAR(sold_at),
    MONTH(sold_at),
    DATE_FORMAT(sold_at, '%m/%Y');
