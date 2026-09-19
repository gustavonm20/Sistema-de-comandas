CREATE DATABASE IF NOT EXISTS comandas;

USE comandas;


CREATE TABLE IF NOT EXISTS categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
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
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    id_categoria INT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    CHECK (preco >= 0),

    FOREIGN KEY (id_categoria)
        REFERENCES categorias(id_categoria)
);


INSERT INTO produtos (nome, preco, id_categoria)
SELECT
    'Coca-Cola',
    7.50,
    id_categoria
FROM categorias
WHERE nome = 'Bebidas'
AND NOT EXISTS (
    SELECT 1
    FROM produtos
    WHERE nome = 'Coca-Cola'
);


INSERT INTO produtos (nome, preco, id_categoria)
SELECT
    'X-Salada',
    22.90,
    id_categoria
FROM categorias
WHERE nome = 'Lanches'
AND NOT EXISTS (
    SELECT 1
    FROM produtos
    WHERE nome = 'X-Salada'
);


INSERT INTO produtos (nome, preco, id_categoria)
SELECT
    'Pudim',
    9.00,
    id_categoria
FROM categorias
WHERE nome = 'Sobremesas'
AND NOT EXISTS (
    SELECT 1
    FROM produtos
    WHERE nome = 'Pudim'
);


CREATE TABLE IF NOT EXISTS cartoes_comanda (
    id_cartao INT AUTO_INCREMENT PRIMARY KEY,
    numero_cartao CHAR(4) NOT NULL UNIQUE,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    CHECK (
        numero_cartao REGEXP '^[0-9]{4}$'
    )
);


INSERT IGNORE INTO cartoes_comanda (numero_cartao)
VALUES
    ('0001'),
    ('0002'),
    ('0003'),
    ('0004'),
    ('0005');


CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_cartao INT NOT NULL,

    situacao ENUM(
        'aberto',
        'fechado'
    ) NOT NULL DEFAULT 'aberto',

    aberto_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fechado_em DATETIME NULL,

    id_cartao_aberto INT
        GENERATED ALWAYS AS (
            CASE
                WHEN situacao = 'aberto' THEN id_cartao
                ELSE NULL
            END
        ) STORED,

    UNIQUE (id_cartao_aberto),

    FOREIGN KEY (id_cartao)
        REFERENCES cartoes_comanda(id_cartao),

    CHECK (
        (situacao = 'aberto' AND fechado_em IS NULL)
        OR
        (situacao = 'fechado' AND fechado_em IS NOT NULL)
    )
);


CREATE TABLE IF NOT EXISTS itens_pedido (
    id_item_pedido INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario DECIMAL(10,2) NOT NULL,
    observacoes VARCHAR(255) NULL,

    CHECK (quantidade > 0),

    CHECK (preco_unitario >= 0),

    FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido),

    FOREIGN KEY (id_produto)
        REFERENCES produtos(id_produto)
);


CREATE TABLE IF NOT EXISTS vendas (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_pedido INT NOT NULL UNIQUE,
    valor_total DECIMAL(10,2) NOT NULL,

    forma_pagamento ENUM(
        'dinheiro',
        'credito',
        'debito',
        'pix'
    ) NOT NULL,

    vendido_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CHECK (valor_total >= 0),

    FOREIGN KEY (id_pedido)
        REFERENCES pedidos(id_pedido)
);


CREATE OR REPLACE VIEW visao_produtos AS
SELECT
    p.id_produto,
    p.nome AS nome_produto,
    p.preco,
    c.id_categoria,
    c.nome AS nome_categoria,
    p.ativo
FROM produtos p
JOIN categorias c
    ON p.id_categoria = c.id_categoria;


CREATE OR REPLACE VIEW visao_pedidos_abertos AS
SELECT
    o.id_pedido,
    cc.numero_cartao,
    o.situacao,

    DATE_FORMAT(
        o.aberto_em,
        '%H:%i  %d/%m/%Y'
    ) AS aberto_em,

    COALESCE(
        SUM(oi.quantidade * oi.preco_unitario),
        0
    ) AS valor_total

FROM pedidos o

JOIN cartoes_comanda cc
    ON o.id_cartao = cc.id_cartao

LEFT JOIN itens_pedido oi
    ON o.id_pedido = oi.id_pedido

WHERE o.situacao = 'aberto'

GROUP BY
    o.id_pedido,
    cc.numero_cartao,
    o.situacao,
    o.aberto_em;


CREATE OR REPLACE VIEW visao_resumo_pedidos AS
SELECT
    o.id_pedido,
    cc.numero_cartao,
    o.situacao,

    DATE_FORMAT(
        o.aberto_em,
        '%H:%i  %d/%m/%Y'
    ) AS aberto_em,

    DATE_FORMAT(
        o.fechado_em,
        '%H:%i  %d/%m/%Y'
    ) AS fechado_em,

    p.id_produto,
    p.nome AS nome_produto,
    c.nome AS nome_categoria,

    oi.quantidade,
    oi.preco_unitario,

    oi.quantidade * oi.preco_unitario AS subtotal,

    oi.observacoes,

    SUM(
        oi.quantidade * oi.preco_unitario
    ) OVER (
        PARTITION BY o.id_pedido
    ) AS total_pedido

FROM pedidos o

JOIN cartoes_comanda cc
    ON o.id_cartao = cc.id_cartao

JOIN itens_pedido oi
    ON o.id_pedido = oi.id_pedido

JOIN produtos p
    ON oi.id_produto = p.id_produto

JOIN categorias c
    ON p.id_categoria = c.id_categoria;


CREATE OR REPLACE VIEW visao_historico_vendas AS
SELECT
    s.id_venda,
    s.id_pedido,
    cc.numero_cartao,
    s.valor_total,
    s.forma_pagamento,

    CASE s.forma_pagamento
        WHEN 'dinheiro' THEN 'Dinheiro'
        WHEN 'credito' THEN 'Crédito'
        WHEN 'debito' THEN 'Débito'
        WHEN 'pix' THEN 'PIX'
    END AS rotulo_forma_pagamento,

    DATE_FORMAT(
        s.vendido_em,
        '%H:%i  %d/%m/%Y'
    ) AS vendido_em,

    s.vendido_em AS data_venda_original

FROM vendas s

JOIN pedidos o
    ON s.id_pedido = o.id_pedido

JOIN cartoes_comanda cc
    ON o.id_cartao = cc.id_cartao;


CREATE OR REPLACE VIEW visao_resumo_diario AS
SELECT
    DATE(vendido_em) AS data_resumo,

    DATE_FORMAT(
        vendido_em,
        '%d/%m/%Y'
    ) AS rotulo_data,

    COUNT(*) AS total_vendas,

    SUM(valor_total) AS faturamento_total,

    AVG(valor_total) AS valor_medio_venda

FROM vendas

GROUP BY DATE(vendido_em);


CREATE OR REPLACE VIEW visao_resumo_semanal AS
SELECT
    YEARWEEK(vendido_em, 1) AS ano_semana,

    MIN(DATE(vendido_em)) AS data_primeira_venda,

    MAX(DATE(vendido_em)) AS data_ultima_venda,

    COUNT(*) AS total_vendas,

    SUM(valor_total) AS faturamento_total,

    AVG(valor_total) AS valor_medio_venda

FROM vendas

GROUP BY YEARWEEK(vendido_em, 1);


CREATE OR REPLACE VIEW visao_resumo_mensal AS
SELECT
    YEAR(vendido_em) AS ano,
    MONTH(vendido_em) AS mes,

    DATE_FORMAT(
        vendido_em,
        '%m/%Y'
    ) AS rotulo_mes,

    COUNT(*) AS total_vendas,

    SUM(valor_total) AS faturamento_total,

    AVG(valor_total) AS valor_medio_venda

FROM vendas

GROUP BY
    YEAR(vendido_em),
    MONTH(vendido_em),
    DATE_FORMAT(vendido_em, '%m/%Y');


SELECT * FROM categorias;

SELECT * FROM visao_produtos;

SELECT * FROM cartoes_comanda;

SELECT * FROM visao_pedidos_abertos;

SELECT * FROM visao_resumo_pedidos;

SELECT * FROM visao_historico_vendas;

SELECT * FROM visao_resumo_diario;

SELECT * FROM visao_resumo_semanal;

SELECT * FROM visao_resumo_mensal;

Select * from produtos;

Select * from cartao_comanda;

Select * from categorias;


SHOW TABLES;
