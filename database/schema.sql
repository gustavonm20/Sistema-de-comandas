CREATE DATABASE IF NOT EXISTS comandas_db;

USE comandas_db;

CREATE TABLE IF NOT EXISTS categorias (
    categoria_id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

INSERT IGNORE INTO categorias (nome)
VALUES
    ('Bebidas'),
    ('Frios'),
    ('Lanches'),
    ('Pizzas'),
    ('Sobremesas');

CREATE TABLE IF NOT EXISTS produtos (
    produto_id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    categoria_id INT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (preco >= 0),
    FOREIGN KEY (categoria_id)
        REFERENCES categorias(categoria_id),
    INDEX idx_produtos_categoria_ativo (categoria_id, ativo)
);

INSERT INTO produtos (nome, preco, categoria_id)
SELECT 'Coca-Cola', 7.50, categoria_id
FROM categorias
WHERE nome = 'Bebidas'
AND NOT EXISTS (
    SELECT 1 FROM produtos WHERE nome = 'Coca-Cola'
);

INSERT INTO produtos (nome, preco, categoria_id)
SELECT 'X-Salada', 22.90, categoria_id
FROM categorias
WHERE nome = 'Lanches'
AND NOT EXISTS (
    SELECT 1 FROM produtos WHERE nome = 'X-Salada'
);

INSERT INTO produtos (nome, preco, categoria_id)
SELECT 'Pudim', 9.00, categoria_id
FROM categorias
WHERE nome = 'Sobremesas'
AND NOT EXISTS (
    SELECT 1 FROM produtos WHERE nome = 'Pudim'
);

CREATE TABLE IF NOT EXISTS comandas (
    comanda_id INT AUTO_INCREMENT PRIMARY KEY,
    numero_comanda CHAR(4) NOT NULL UNIQUE,
    ativa BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (numero_comanda REGEXP '^[0-9]{4}$')
);

INSERT IGNORE INTO comandas (numero_comanda)
VALUES
    ('0001'),
    ('0002'),
    ('0003'),
    ('0004'),
    ('0005');

CREATE TABLE IF NOT EXISTS pedidos (
    pedido_id INT AUTO_INCREMENT PRIMARY KEY,
    comanda_id INT NOT NULL,
    status ENUM('aberto', 'fechado') NOT NULL DEFAULT 'aberto',
    aberto_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fechado_em DATETIME NULL,
    comanda_aberta_id INT
        GENERATED ALWAYS AS (
            CASE
                WHEN status = 'aberto' THEN comanda_id
                ELSE NULL
            END
        ) STORED,
    UNIQUE (comanda_aberta_id),
    CHECK (
        (status = 'aberto' AND fechado_em IS NULL)
        OR
        (status = 'fechado' AND fechado_em IS NOT NULL)
    ),
    FOREIGN KEY (comanda_id)
        REFERENCES comandas(comanda_id),
    INDEX idx_pedidos_status (status)
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    item_pedido_id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    produto_id INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    observacoes VARCHAR(255) NULL,
    CHECK (quantidade > 0),
    CHECK (preco_unitario >= 0),
    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(pedido_id),
    FOREIGN KEY (produto_id)
        REFERENCES produtos(produto_id),
    INDEX idx_itens_pedido_pedido (pedido_id),
    INDEX idx_itens_pedido_produto (produto_id)
);

CREATE TABLE IF NOT EXISTS vendas (
    venda_id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL UNIQUE,
    valor_total DECIMAL(10,2) NOT NULL,
    forma_pagamento ENUM('dinheiro', 'credito', 'debito', 'pix') NOT NULL,
    vendido_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (valor_total >= 0),
    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(pedido_id),
    INDEX idx_vendas_vendido_em (vendido_em),
    INDEX idx_vendas_forma_pagamento (forma_pagamento)
);

CREATE OR REPLACE VIEW vw_produtos AS
SELECT
    p.produto_id,
    p.nome AS nome_produto,
    p.preco,
    c.categoria_id,
    c.nome AS nome_categoria,
    p.ativo
FROM produtos p
JOIN categorias c
    ON p.categoria_id = c.categoria_id;

CREATE OR REPLACE VIEW vw_comandas_abertas AS
SELECT
    p.pedido_id,
    c.numero_comanda,
    p.status,
    DATE_FORMAT(p.aberto_em, '%H:%i  %d/%m/%Y') AS aberto_em,
    COALESCE(SUM(ip.quantidade * ip.preco_unitario), 0) AS valor_total
FROM pedidos p
JOIN comandas c
    ON p.comanda_id = c.comanda_id
LEFT JOIN itens_pedido ip
    ON p.pedido_id = ip.pedido_id
WHERE p.status = 'aberto'
GROUP BY
    p.pedido_id,
    c.numero_comanda,
    p.status,
    p.aberto_em;

CREATE OR REPLACE VIEW vw_resumo_pedido AS
SELECT
    pe.pedido_id,
    co.numero_comanda,
    pe.status,
    DATE_FORMAT(pe.aberto_em, '%H:%i  %d/%m/%Y') AS aberto_em,
    DATE_FORMAT(pe.fechado_em, '%H:%i  %d/%m/%Y') AS fechado_em,
    pr.produto_id,
    pr.nome AS nome_produto,
    ca.nome AS nome_categoria,
    ip.quantidade,
    ip.preco_unitario,
    ip.quantidade * ip.preco_unitario AS subtotal,
    ip.observacoes,
    SUM(ip.quantidade * ip.preco_unitario)
        OVER (PARTITION BY pe.pedido_id) AS total_pedido
FROM pedidos pe
JOIN comandas co
    ON pe.comanda_id = co.comanda_id
JOIN itens_pedido ip
    ON pe.pedido_id = ip.pedido_id
JOIN produtos pr
    ON ip.produto_id = pr.produto_id
JOIN categorias ca
    ON pr.categoria_id = ca.categoria_id;

CREATE OR REPLACE VIEW vw_historico_vendas AS
SELECT
    v.venda_id,
    v.pedido_id,
    c.numero_comanda,
    v.valor_total,
    v.forma_pagamento,
    CASE v.forma_pagamento
        WHEN 'dinheiro' THEN 'Dinheiro'
        WHEN 'credito' THEN 'Crédito'
        WHEN 'debito' THEN 'Débito'
        WHEN 'pix' THEN 'PIX'
    END AS forma_pagamento_descricao,
    DATE_FORMAT(v.vendido_em, '%H:%i  %d/%m/%Y') AS vendido_em,
    v.vendido_em AS vendido_em_original
FROM vendas v
JOIN pedidos p
    ON v.pedido_id = p.pedido_id
JOIN comandas c
    ON p.comanda_id = c.comanda_id;

CREATE OR REPLACE VIEW vw_resumo_diario AS
SELECT
    DATE(vendido_em) AS data_resumo,
    DATE_FORMAT(vendido_em, '%d/%m/%Y') AS data_formatada,
    COUNT(*) AS total_vendas,
    SUM(valor_total) AS faturamento_total,
    AVG(valor_total) AS ticket_medio
FROM vendas
GROUP BY DATE(vendido_em), DATE_FORMAT(vendido_em, '%d/%m/%Y');

CREATE OR REPLACE VIEW vw_resumo_semanal AS
SELECT
    YEARWEEK(vendido_em, 1) AS ano_semana,
    COUNT(*) AS total_vendas,
    SUM(valor_total) AS faturamento_total,
    AVG(valor_total) AS ticket_medio
FROM vendas
GROUP BY YEARWEEK(vendido_em, 1);

CREATE OR REPLACE VIEW vw_resumo_mensal AS
SELECT
    YEAR(vendido_em) AS ano,
    MONTH(vendido_em) AS mes,
    DATE_FORMAT(vendido_em, '%m/%Y') AS mes_formatado,
    COUNT(*) AS total_vendas,
    SUM(valor_total) AS faturamento_total,
    AVG(valor_total) AS ticket_medio
FROM vendas
GROUP BY
    YEAR(vendido_em),
    MONTH(vendido_em),
    DATE_FORMAT(vendido_em, '%m/%Y');
