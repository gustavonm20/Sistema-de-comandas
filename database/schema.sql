-- Inicialização de banco NOVO. Não é uma migration. Consulte docs/DATABASE.md.
CREATE DATABASE IF NOT EXISTS comandas_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE comandas_db;

CREATE TABLE IF NOT EXISTS establishments (
    establishment_id INT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL,
    business_type VARCHAR(100) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    normalized_name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category_id INT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_products_category_active (category_id, active),
    UNIQUE (normalized_name),
    CHECK (price >= 0),
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS command_cards (
    card_id INT AUTO_INCREMENT PRIMARY KEY,
    card_number CHAR(4) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE (card_number),
    CHECK (card_number REGEXP '^[0-9]{4}$')
);

CREATE TABLE IF NOT EXISTS daily_operations (
    operation_id INT AUTO_INCREMENT PRIMARY KEY,
    status ENUM('open', 'closed') NOT NULL DEFAULT 'open',
    opening_cash DECIMAL(10, 2) NOT NULL,
    expected_cash DECIMAL(10, 2) NULL,
    counted_cash DECIMAL(10, 2) NULL,
    difference_amount DECIMAL(10, 2) NULL,
    discrepancy_note VARCHAR(255) NULL,
    opened_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    closed_at DATETIME NULL,

    open_operation_marker TINYINT
        GENERATED ALWAYS AS (
            CASE
                WHEN status = 'open' THEN 1
                ELSE NULL
            END
        ) STORED,

    UNIQUE (open_operation_marker),
    CHECK (opening_cash >= 0),
    CHECK (
        (status = 'open' AND closed_at IS NULL)
        OR
        (status = 'closed' AND closed_at IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    card_id INT NOT NULL,
    operation_id INT NOT NULL,
    service_type ENUM('table', 'counter', 'pickup') NOT NULL DEFAULT 'counter',
    service_label VARCHAR(100) NULL,
    note VARCHAR(255) NULL,
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

    INDEX idx_orders_status_opened (status, opened_at),
    UNIQUE (open_card_id),
    FOREIGN KEY (card_id)
        REFERENCES command_cards(card_id),
    FOREIGN KEY (operation_id)
        REFERENCES daily_operations(operation_id),
    CHECK (
        (status = 'open' AND closed_at IS NULL)
        OR
        (status = 'closed' AND closed_at IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    notes VARCHAR(255) NULL,
    product_name_snapshot VARCHAR(100) NOT NULL,
    category_name_snapshot VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    quantity INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE (order_id, product_id),
    CHECK (unit_price >= 0),
    CHECK (quantity > 0),
    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    card_number_snapshot CHAR(4) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('cash', 'pix', 'debit', 'credit') NOT NULL,
    cash_received DECIMAL(10, 2) NULL,
    change_amount DECIMAL(10, 2) NULL,
    sold_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_sales_sold_at (sold_at),
    INDEX idx_sales_payment_sold (payment_method, sold_at),
    UNIQUE (order_id),
    CHECK (total_amount >= 0),
    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    actor VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT NULL,
    detail VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO establishments (establishment_id, name, email, business_type)
SELECT 1, 'Meu Estabelecimento', 'contato@estabelecimento.com', 'Padaria e cafeteria'
WHERE NOT EXISTS (
    SELECT 1
    FROM establishments
    WHERE establishment_id = 1
);

INSERT INTO categories (name)
SELECT 'Bebidas'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Bebidas');

INSERT INTO categories (name)
SELECT 'Frios'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Frios');

INSERT INTO categories (name)
SELECT 'Lanches'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Lanches');

INSERT INTO categories (name)
SELECT 'Pizzas'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Pizzas');

INSERT INTO categories (name)
SELECT 'Sobremesas'
WHERE NOT EXISTS (SELECT 1 FROM categories WHERE name = 'Sobremesas');

INSERT IGNORE INTO command_cards (card_number) VALUES
    ('0001'), ('0002'), ('0003'), ('0004'), ('0005'),
    ('0006'), ('0007'), ('0008'), ('0009'), ('0010'),
    ('0011'), ('0012'), ('0013'), ('0014'), ('0015'),
    ('0016'), ('0017'), ('0018'), ('0019'), ('0020');

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

    DATE_FORMAT(
        o.opened_at,
        '%H:%i  %d/%m/%Y'
    ) AS opened_at,

    COALESCE(
        SUM(oi.quantity * oi.unit_price),
        0
    ) AS total_amount

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

    DATE_FORMAT(
        o.opened_at,
        '%H:%i  %d/%m/%Y'
    ) AS opened_at,

    DATE_FORMAT(
        o.closed_at,
        '%H:%i  %d/%m/%Y'
    ) AS closed_at,

    p.product_id,
    oi.product_name_snapshot AS product_name,
    oi.category_name_snapshot AS category_name,

    oi.quantity,
    oi.unit_price,

    oi.quantity * oi.unit_price AS subtotal,

    oi.notes,

    SUM(
        oi.quantity * oi.unit_price
    ) OVER (
        PARTITION BY o.order_id
    ) AS order_total

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
    s.card_number_snapshot AS card_number,
    s.total_amount,
    s.payment_method,

    CASE s.payment_method
        WHEN 'cash' THEN 'Dinheiro'
        WHEN 'credit' THEN 'Crédito'
        WHEN 'debit' THEN 'Débito'
        WHEN 'pix' THEN 'PIX'
    END AS payment_method_label,

    DATE_FORMAT(
        s.sold_at,
        '%H:%i  %d/%m/%Y'
    ) AS sold_at,

    s.sold_at AS sold_at_raw

FROM sales s

JOIN orders o
    ON s.order_id = o.order_id

JOIN command_cards cc
    ON o.card_id = cc.card_id;


CREATE OR REPLACE VIEW vw_daily_summary AS
SELECT
    summary_date,
    DATE_FORMAT(summary_date, '%d/%m/%Y') AS date_label,
    total_sales,
    total_revenue,
    average_ticket
FROM (
    SELECT DATE(sold_at) AS summary_date,
           COUNT(*) AS total_sales,
           SUM(total_amount) AS total_revenue,
           AVG(total_amount) AS average_ticket
    FROM sales
    GROUP BY DATE(sold_at)
) AS daily_sales;


CREATE OR REPLACE VIEW vw_weekly_summary AS
SELECT
    YEARWEEK(sold_at, 1) AS year_week,

    MIN(DATE(sold_at)) AS first_sale_date,

    MAX(DATE(sold_at)) AS last_sale_date,

    COUNT(*) AS total_sales,

    SUM(total_amount) AS total_revenue,

    AVG(total_amount) AS average_ticket

FROM sales

GROUP BY YEARWEEK(sold_at, 1);


CREATE OR REPLACE VIEW vw_monthly_summary AS
SELECT
    YEAR(sold_at) AS year,
    MONTH(sold_at) AS month,

    DATE_FORMAT(
        sold_at,
        '%m/%Y'
    ) AS month_label,

    COUNT(*) AS total_sales,

    SUM(total_amount) AS total_revenue,

    AVG(total_amount) AS average_ticket

FROM sales

GROUP BY
    YEAR(sold_at),
    MONTH(sold_at),
    DATE_FORMAT(sold_at, '%m/%Y');

